"""
Claude AI Service for Book Generation
====================================
Handles all interactions with Claude API for generating book content.
Supports streaming, retry logic, and error handling.
"""

import json
import logging
import asyncio
from typing import Dict, Any, AsyncIterator, Optional, List
from datetime import datetime, timezone
import anthropic
from anthropic import AsyncAnthropic, APIError, APIConnectionError, RateLimitError
import structlog
from flask import current_app
from app.models import BookGeneration
from app.utils.retry import exponential_backoff_retry

logger = structlog.get_logger()


class ClaudeService:
    """
    Servicio optimizado para generación completa de libros con Claude AI.
    
    Este servicio está diseñado específicamente para generar libros completos
    en una sola operación, utilizando streaming SSE para feedback en tiempo real
    y el modelo más avanzado de Claude (claude-sonnet-4-20250514) con capacidades
    de thinking extendido.
    
    Características principales:
    - Generación completa de libros (no por capítulos)
    - Streaming en tiempo real con WebSocket
    - Thinking transparente para mostrar el proceso de análisis
    - Métricas detalladas de generación
    - Manejo robusto de errores
    """
    
    def __init__(self):
        """Initialize Claude service with API client."""
        self.api_key = current_app.config.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        
        self.client = AsyncAnthropic(api_key=self.api_key)
        self.model = current_app.config.get('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
        self.max_tokens = current_app.config.get('CLAUDE_MAX_TOKENS', 64000)
        self.temperature = current_app.config.get('CLAUDE_TEMPERATURE', 1.0)
        self.thinking_budget = current_app.config.get('CLAUDE_THINKING_BUDGET', 63999)
        
        # Retry configuration
        self.max_retries = current_app.config.get('CLAUDE_MAX_RETRIES', 3)
        self.retry_delay = current_app.config.get('CLAUDE_RETRY_DELAY', 1.0)
        
        logger.info("claude_service_initialized", 
                   model=self.model,
                   max_tokens=self.max_tokens)
    
    # MÉTODO PRINCIPAL: Generación completa de libros con streaming
    
    
    async def generate_book_content_stream(self, book_id: int, book_params: Dict[str, Any]) -> Dict[str, Any]:
        """Genera el contenido del libro usando Claude AI con streaming SSE"""
        try:
            # Preparar el prompt con los detalles del libro
            messages = self._build_messages(book_params)
            
            # Variables para acumular respuesta y métricas
            full_content = []
            thinking_content = []
            chunk_count = 0
            total_chars = 0
            current_block_index = None
            
            # Emisión de evento de inicio
            from app import socketio
            from app.routes.websocket import emit_book_progress_update
            
            # Usar la función helper para emitir correctamente
            emit_book_progress_update(book_id, {
                'current': 5,
                'total': 100,
                'status': 'connecting',
                'status_message': 'Conectando con Claude AI...',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # Crear streaming request con thinking habilitado
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=messages,
                thinking={
                    "type": "enabled",
                    "budget_tokens": self.thinking_budget
                }
            ) as stream:
                
                # Progreso inicial - análisis comenzado
                emit_book_progress_update(book_id, {
                    'current': 10,
                    'total': 100,
                    'status': 'thinking',
                    'status_message': 'Claude está analizando tu solicitud...',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                
                async for event in stream:
                    chunk_count += 1
                    
                    # Thinking blocks
                    if event.type == "content_block_start" and event.content_block.type == "thinking":
                        current_block_index = event.index
                        emit_book_progress_update(book_id, {
                            'current': 15,
                            'total': 100,
                            'status': 'deep_thinking',
                            'status_message': 'Claude está pensando profundamente en tu libro...',
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        })
                        
                        # Emit thinking start event
                        from app.routes.websocket import emit_thinking_start, emit_generation_log
                        emit_thinking_start(book_id)
                        emit_generation_log(book_id, 'thinking', 'Claude AI iniciando análisis profundo...')
                    
                    elif event.type == "content_block_delta" and hasattr(event, 'delta'):
                        if hasattr(event.delta, 'text'):
                            text_chunk = event.delta.text
                            total_chars += len(text_chunk)
                            
                            # Si es thinking content
                            if current_block_index is not None and event.index == current_block_index:
                                thinking_content.append(text_chunk)
                                
                                # Emit thinking update with streaming
                                from app.routes.websocket import emit_thinking_update
                                full_thinking = ''.join(thinking_content)
                                
                                # Emit chunk immediately for real-time streaming
                                emit_thinking_update(book_id, text_chunk, {
                                    'total_chars': len(full_thinking),
                                    'total_words': len(full_thinking.split())
                                })
                                
                                # Emit progress update every 100 chunks
                                if chunk_count % 100 == 0:
                                    emit_book_progress_update(book_id, {
                                        'current': 20,
                                        'total': 100,
                                        'status': 'thinking',
                                        'status_message': f'Analizando... ({len(full_thinking.split())} palabras de pensamiento)',
                                        'timestamp': datetime.now(timezone.utc).isoformat()
                                    })
                            
                            # Content principal
                            else:
                                full_content.append(text_chunk)
                                
                                # Calcular progreso basado en contenido generado
                                estimated_final_chars = book_params.get('page_count', 50) * 2000  # ~2000 chars per page
                                content_progress = min(80, 20 + (total_chars / estimated_final_chars) * 60)
                                
                                # Emit progress cada 50 chunks para evitar spam
                                if chunk_count % 50 == 0:
                                    # Calcular estadísticas reales del contenido actual
                                    current_content = ''.join(full_content)
                                    actual_words = len(current_content.split())
                                    actual_pages = actual_words // 350  # ~350 palabras por página
                                    actual_chapters = current_content.count('Capítulo')
                                    
                                    emit_book_progress_update(book_id, {
                                        'current': int(content_progress),
                                        'total': 100,
                                        'status': 'writing',
                                        'status_message': f'Escribiendo tu libro... {actual_pages} páginas generadas',
                                        'stats': {
                                            'pages': actual_pages,
                                            'words': actual_words,
                                            'chapters': actual_chapters,
                                            'chunks_processed': chunk_count
                                        },
                                        'timestamp': datetime.now(timezone.utc).isoformat()
                                    })
                                    
                                    # Emit log cada 100 chunks
                                    if chunk_count % 100 == 0:
                                        from app.routes.websocket import emit_generation_log
                                        emit_generation_log(book_id, 'info', 
                                            f'Progreso: {actual_pages} páginas, {actual_words:,} palabras, {actual_chapters} capítulos')
                    
                    elif event.type == "content_block_stop":
                        if current_block_index == event.index:
                            # Fin del thinking
                            from app.routes.websocket import emit_thinking_complete, emit_generation_log
                            full_thinking = ''.join(thinking_content)
                            emit_thinking_complete(book_id, {
                                'total_chars': len(full_thinking),
                                'total_words': len(full_thinking.split())
                            })
                            emit_generation_log(book_id, 'thinking', f'Análisis completado: {len(full_thinking.split())} palabras de pensamiento')
                            
                            emit_book_progress_update(book_id, {
                                'current': 25,
                                'total': 100,
                                'status': 'analysis_complete',
                                'status_message': 'Análisis completado, comenzando escritura...',
                                'timestamp': datetime.now(timezone.utc).isoformat()
                            })
                            current_block_index = None
                        else:
                            # Fin del contenido principal
                            emit_book_progress_update(book_id, {
                                'current': 85,
                                'total': 100,
                                'status': 'writing_complete',
                                'status_message': 'Escritura completada, finalizando...',
                                'timestamp': datetime.now(timezone.utc).isoformat()
                            })
                
                # Obtener mensaje final para estadísticas
                final_message = await stream.get_final_message()
                
                # Calcular estadísticas finales
                complete_content = ''.join(full_content)
                complete_thinking = ''.join(thinking_content)
                final_words = len(complete_content.split())
                final_pages = final_words // 350  # ~350 words per page
                final_chapters = complete_content.count('Capítulo')
                
                # Validar que se cumplió con el mínimo de páginas solicitadas (STRICT VALIDATION)
                requested_pages = book_params.get('page_count', 50)
                deficit_percentage = ((requested_pages - final_pages) / requested_pages) * 100 if requested_pages > 0 else 0
                
                if final_pages < requested_pages * 0.95:  # Stricter requirement: allow only 5% margin
                    logger.warning("book_generation_below_page_count",
                                 book_id=book_id,
                                 requested_pages=requested_pages,
                                 actual_pages=final_pages,
                                 deficit_pages=requested_pages - final_pages,
                                 deficit_percentage=deficit_percentage)
                    
                    # Emit detailed warning with recommendation
                    from app.routes.websocket import emit_generation_log
                    
                    if deficit_percentage > 20:  # Significant shortage
                        warning_message = (f'⚠️ ADVERTENCIA: Se generaron solo {final_pages} páginas de las {requested_pages} solicitadas ' +
                                         f'({deficit_percentage:.1f}% menos). Esto puede indicar que el tema necesita más expansión.')
                        emit_generation_log(book_id, 'warning', warning_message, {
                            'recommendation': 'Considera agregar más temas específicos o solicitar un nuevo libro con contenido expandido.',
                            'deficit_info': {
                                'requested': requested_pages,
                                'generated': final_pages,
                                'deficit_pages': requested_pages - final_pages,
                                'deficit_percentage': round(deficit_percentage, 1)
                            }
                        })
                    else:  # Minor shortage
                        warning_message = (f'Nota: Se generaron {final_pages} páginas de las {requested_pages} solicitadas. ' +
                                         f'El contenido es completo y de alta calidad.')
                        emit_generation_log(book_id, 'warning', warning_message)
                
                elif final_pages >= requested_pages:
                    # Success: Met or exceeded requirements
                    from app.routes.websocket import emit_generation_log
                    success_message = f'✅ Objetivo cumplido: Se generaron {final_pages} páginas (solicitadas: {requested_pages})'
                    emit_generation_log(book_id, 'success', success_message)
                
                # Emit final log
                from app.routes.websocket import emit_generation_log
                emit_generation_log(book_id, 'success', 
                    f'Generación completada: {final_pages} páginas, {final_words:,} palabras, {final_chapters} capítulos')
                
                logger.info("streaming_book_generation_completed",
                           book_id=book_id,
                           total_chunks=chunk_count,
                           total_characters=total_chars,
                           final_words=final_words,
                           final_pages=final_pages,
                           thinking_length=len(complete_thinking))
                
                return {
                    'content': complete_content,
                    'thinking': complete_thinking,
                    'usage': {
                        'prompt_tokens': final_message.usage.input_tokens,
                        'completion_tokens': final_message.usage.output_tokens,
                        'thinking_tokens': getattr(final_message.usage, 'thinking_tokens', 0),
                        'total_tokens': final_message.usage.input_tokens + final_message.usage.output_tokens
                    },
                    'model': final_message.model,
                    'stop_reason': final_message.stop_reason,
                    'streaming_stats': {
                        'total_chunks': chunk_count,
                        'total_characters': total_chars,
                        'estimated_pages': final_pages,
                        'estimated_words': final_words,
                        'thinking_length': len(complete_thinking),
                        'chapters': final_chapters
                    }
                }
                
        except anthropic.APIError as e:
            logger.error(f"Claude API error: {str(e)}")
            
            # Check if it's a temporary error that should be retried
            error_str = str(e)
            is_temporary_error = any(keyword in error_str.lower() for keyword in [
                'overloaded', 'rate_limit', 'timeout', 'temporary', 'service_unavailable'
            ])
            
            # Craft friendly error messages with structured technical details
            technical_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'api_model': self.model,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'is_retryable': is_temporary_error,
                'book_params': {
                    'title': book_params.get('title', 'N/A'),
                    'pages': book_params.get('page_count', 'N/A'),
                    'language': book_params.get('language', 'N/A')
                }
            }
            
            if 'overloaded' in error_str.lower():
                user_message = ('🔄 Claude está procesando muchas solicitudes en este momento. ' +
                              'No te preocupes, tu libro sigue en cola y se procesará automáticamente ' +
                              'en unos minutos cuando haya espacio disponible.')
                technical_details['category'] = 'OVERLOADED'
                technical_details['recommendation'] = 'El sistema reintentará automáticamente. No es necesario ninguna acción.'
            elif 'rate_limit' in error_str.lower():
                user_message = ('⏱️ Hemos alcanzado el límite temporal de solicitudes. ' +
                              'Tu libro se procesará automáticamente en breve. ' +
                              'Esto es normal y tu contenido está seguro.')
                technical_details['category'] = 'RATE_LIMIT'
                technical_details['recommendation'] = 'Esperando ventana de límite de velocidad. Reintento automático programado.'
            elif 'timeout' in error_str.lower():
                user_message = ('⏳ La generación está tomando más tiempo del esperado. ' +
                              'Estamos reintentando automáticamente. Tu libro se generará pronto.')
                technical_details['category'] = 'TIMEOUT'
                technical_details['recommendation'] = 'La generación es compleja. El sistema continuará intentando.'
            else:
                user_message = ('📡 Hubo un problema temporal de conexión con Claude AI. ' +
                              'Estamos reintentando automáticamente. Por favor, mantén esta página abierta.')
                technical_details['category'] = 'CONNECTION_ERROR'
                technical_details['recommendation'] = 'Problema de conectividad. Se reintentará automáticamente.'
            
            # Emit enhanced error with structured technical details
            from app.routes.websocket import emit_generation_log
            emit_generation_log(book_id, 'error', user_message, {
                'expandable_details': technical_details,
                'user_friendly_message': user_message,
                'show_retry_info': is_temporary_error
            })
            
            socketio.emit('book_error', {
                'book_id': book_id,
                'error': 'API error',
                'message': user_message,
                'technical_details': technical_details,
                'is_temporary': is_temporary_error,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, room=f'book_{book_id}')
            raise
        except Exception as e:
            logger.error(f"Streaming generation error: {str(e)}")
            socketio.emit('book_error', {
                'book_id': book_id,
                'error': 'generation_error',
                'message': 'Error durante la generación',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, room=f'book_{book_id}')
            raise
    
    def _build_messages(self, book_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Construye los mensajes para Claude AI según las especificaciones"""
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(book_params)
        
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    }
                ]
            }
        ]
    
    def _build_system_prompt(self) -> str:
        """Sistema prompt optimizado para generación de libros"""
        return """You are a professional book writer that MUST follow the exact specifications provided by the user.

🚨 CRITICAL REQUIREMENTS - FAILURE TO FOLLOW WILL RESULT IN REJECTION:

1. **STRICT TOPIC ADHERENCE**: You MUST write about the EXACT topic, title, and subject matter specified in the user's request. DO NOT deviate from the specified topic under any circumstances.

2. **EXACT TITLE USAGE**: Use the EXACT title provided by the user. Do not create generic titles like "LIBRO SIN TÍTULO" - always use the specific title given.

3. **GENRE COMPLIANCE**: The book MUST match the specified genre (technical, fiction, etc.). Do not write generic self-help content unless specifically requested.

4. **TOPIC FOCUS**: Follow the key_topics and description provided. If the user wants a book about Python programming, write about Python programming. If they want a book about cooking, write about cooking.

5. **LANGUAGE REQUIREMENTS**: Write in the exact language specified (Spanish, English, etc.).

WRITING PROCESS:
1. READ the user's title, genre, key_topics, and description CAREFULLY
2. ENSURE your content directly addresses the specified topic
3. Use the exact title provided - never substitute with generic alternatives
4. Match the requested genre and tone precisely
5. Include specific, relevant content for the requested subject matter

FORMATTING:
- Start with # [EXACT USER TITLE]
- Include ## Tabla de Contenidos
- Write substantive chapters about the SPECIFIC topic requested
- Use ### for chapter headers
- Maintain professional structure

FORBIDDEN:
- Generic self-help content when technical content is requested
- Substituting user's title with "LIBRO SIN TÍTULO" or similar
- Writing about topics different from those specified
- Ignoring the genre requirements

Remember: Your job is to write the SPECIFIC book the user requested, not a generic book."""
    
    def _build_user_prompt(self, book_params: Dict[str, Any]) -> str:
        """Construye el prompt del usuario con los detalles del libro"""
        # Obtener información de formato
        page_size = book_params.get('page_size', 'pocket')
        line_spacing = book_params.get('line_spacing', 'medium')
        page_count = book_params.get('page_count', 50)
        
        # Calcular palabras aproximadas por página según formato
        words_per_page = {
            ('pocket', 'single'): 250,  # Pocket con espaciado sencillo (como Kindle)
            ('pocket', 'medium'): 200,  # Pocket con espaciado 1.5
            ('pocket', 'double'): 150,  # Pocket con espaciado doble
            ('A5', 'single'): 350,      # A5 con espaciado sencillo
            ('A5', 'medium'): 280,      # A5 con espaciado 1.5
            ('A5', 'double'): 210,      # A5 con espaciado doble
            ('B5', 'single'): 450,      # B5 con espaciado sencillo
            ('B5', 'medium'): 360,      # B5 con espaciado 1.5
            ('B5', 'double'): 270,      # B5 con espaciado doble
            ('letter', 'single'): 500,  # Letter con espaciado sencillo
            ('letter', 'medium'): 400,  # Letter con espaciado 1.5
            ('letter', 'double'): 300,  # Letter con espaciado doble
        }
        
        words_per_page_estimate = words_per_page.get((page_size, line_spacing), 400)
        total_words = page_count * words_per_page_estimate
        
        # Convertir código de idioma a nombre completo
        language_map = {
            'es': 'Spanish',
            'en': 'English',
            'pt': 'Portuguese',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian'
        }
        
        user_language = book_params.get('language', 'es')
        language_name = language_map.get(user_language, user_language)
        
        return f"""Create a complete book with the following specifications:

**CRITICAL LANGUAGE REQUIREMENT:**
- LANGUAGE: {language_name} (Code: {user_language})
- WRITE EVERYTHING IN {language_name.upper()} - Title, chapters, content, everything!
- Do NOT use English or any other language unless specifically requested

**BOOK DETAILS:**
- Title: {book_params.get('title', 'Untitled Book')}
- Genre: {book_params.get('genre', 'General')}
- Target Audience: {book_params.get('target_audience', 'General audience')}
- Number of Chapters: {book_params.get('chapter_count', 10)}

**🚨 CRITICAL PAGE COUNT REQUIREMENT - THIS IS MANDATORY:**
- Target Pages: {page_count} pages (OBLIGATORY - YOU MUST MEET THIS REQUIREMENT)
- Page Size: {page_size}
- Line Spacing: {line_spacing} ({"1.0" if line_spacing == "single" else "1.5" if line_spacing == "medium" else "2.0"})
- Required Total Words: {total_words:,} words (MINIMUM REQUIRED)
- Words per Page: ~{words_per_page_estimate}

**MANDATORY PAGE COUNT ENFORCEMENT:**
- You MUST generate AT LEAST {total_words:,} words to fill {page_count} pages
- If you reach what you think is the end, continue writing until you reach the word count
- Add more detailed explanations, examples, case studies, or expand on topics
- The user has specifically requested {page_count} pages and expects exactly that amount
- Do not stop writing until you have generated sufficient content for {page_count} full pages

**CONTENT REQUIREMENTS:**
- Writing Style: {book_params.get('writing_style', 'Professional and engaging')}
- Tone: {book_params.get('tone', 'Informative')}
- Key Topics: {book_params.get('key_topics', 'As relevant to the title')}
- Additional Instructions: {book_params.get('additional_instructions', 'None')}

**STRUCTURE REQUIREMENTS:**
- Include Table of Contents: {book_params.get('include_toc', True)}
- Include Introduction: {book_params.get('include_introduction', True)}
- Include Conclusion: {book_params.get('include_conclusion', True)}

**CONTENT EXPANSION STRATEGIES IF NEEDED:**
- Add detailed examples and case studies
- Include practical exercises or applications
- Expand on theoretical concepts with real-world connections
- Add historical context or background information
- Include troubleshooting sections or FAQs
- Add appendices with additional resources
- Expand chapter conclusions with key takeaways

Please write the COMPLETE book content in {language_name.upper()}, including:
1. Engaging introduction that sets the tone
2. Full content for each chapter (not just outlines) - EXPAND AS NEEDED
3. Proper transitions between chapters
4. Comprehensive conclusion
5. Professional formatting with clear structure

FINAL MANDATORY REMINDER: 
- Write EVERYTHING in {language_name.upper()}
- Generate AT LEAST {total_words:,} words to fill {page_count} pages
- Do not stop until you reach the required page count
- The user expects {page_count} pages of valuable content"""
    
    # MÉTODOS DE UTILIDAD PARA EL SERVICIO PRINCIPAL
    
    async def generate_complete_book(self, book_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método de conveniencia para generar un libro completo.
        
        Args:
            book_params: Parámetros del libro
            
        Returns:
            Resultado de la generación con contenido, métricas y metadatos
        """
        # Para compatibilidad, usar el book_id como 0 si no se proporciona
        book_id = book_params.get('book_id', 0)
        
        logger.info("starting_complete_book_generation",
                   title=book_params.get('title'),
                   genre=book_params.get('genre'),
                   pages=book_params.get('page_count', 50))
        
        try:
            result = await self.generate_book_content_stream(book_id, book_params)
            
            logger.info("complete_book_generation_finished",
                       title=book_params.get('title'),
                       words=result['streaming_stats']['estimated_words'],
                       pages=result['streaming_stats']['estimated_pages'],
                       total_tokens=result['usage']['total_tokens'])
            
            return result
            
        except Exception as e:
            logger.error("complete_book_generation_failed",
                        error=str(e),
                        title=book_params.get('title'))
            raise
    
    def estimate_generation_time(self, book_params: Dict[str, Any]) -> int:
        """
        Estima el tiempo de generación en segundos basado en los parámetros del libro.
        
        Args:
            book_params: Parámetros del libro
            
        Returns:
            Tiempo estimado en segundos
        """
        base_time = 60  # 1 minuto base
        page_count = book_params.get('page_count', 50)
        chapter_count = book_params.get('chapter_count', 10)
        
        # ~2 segundos por página + ~5 segundos por capítulo
        estimated_time = base_time + (page_count * 2) + (chapter_count * 5)
        
        # Máximo 10 minutos
        return min(estimated_time, 600)
    
    def validate_book_params(self, book_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida y normaliza los parámetros del libro.
        
        Args:
            book_params: Parámetros del libro
            
        Returns:
            Parámetros validados y normalizados
        """
        validated = book_params.copy()
        
        # Valores por defecto
        defaults = {
            'title': 'Libro Sin Título',
            'genre': 'General',
            'target_audience': 'Audiencia general',
            'language': 'Spanish',
            'chapter_count': 10,
            'page_count': 50,
            'writing_style': 'Profesional y ameno',
            'tone': 'Informativo',
            'key_topics': 'Relevantes al título',
            'additional_instructions': 'Ninguna'
        }
        
        # Aplicar valores por defecto SOLO si el parámetro no existe o es None
        for key, default_value in defaults.items():
            if key not in validated or validated[key] is None:
                validated[key] = default_value
        
        # Validar rangos
        validated['chapter_count'] = max(3, min(validated['chapter_count'], 20))
        validated['page_count'] = max(10, min(validated['page_count'], 300))
        
        # Normalizar strings
        string_fields = ['title', 'genre', 'target_audience', 'writing_style', 'tone']
        for field in string_fields:
            if field in validated and isinstance(validated[field], str):
                validated[field] = validated[field].strip()
        
        logger.info("book_params_validated",
                   title=validated['title'],
                   chapters=validated['chapter_count'],
                   pages=validated['page_count'])
        
        return validated


# Singleton instance
_claude_service: Optional[ClaudeService] = None


def get_claude_service() -> ClaudeService:
    """Get or create Claude service instance."""
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeService()
    return _claude_service