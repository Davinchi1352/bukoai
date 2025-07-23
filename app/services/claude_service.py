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
    
    # MÉTODO PARA GENERACIÓN DE ARQUITECTURA (PRIMERA ETAPA)
    
    async def generate_book_architecture(self, book_id: int, book_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera únicamente la arquitectura del libro (estructura, capítulos, personajes, etc.)
        para que el usuario pueda revisar y aprobar antes de la generación completa.
        
        Args:
            book_id: ID del libro
            book_params: Parámetros del libro
            
        Returns:
            Resultado con la arquitectura generada
        """
        try:
            # Preparar el prompt específico para arquitectura
            messages = self._build_architecture_messages(book_params)
            
            # Variables para acumular respuesta
            full_content = []
            thinking_content = []
            chunk_count = 0
            
            # Emisión de evento de inicio
            from app.routes.websocket import emit_book_progress_update, emit_generation_log
            
            emit_book_progress_update(book_id, {
                'current': 5,
                'total': 100,
                'status': 'connecting',
                'status_message': 'Conectando con Claude AI para generar arquitectura...',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # Crear streaming request con thinking habilitado
            # Para arquitectura usamos tokens optimizados (menos que para generación completa)
            arch_max_tokens = min(16000, self.max_tokens)  # Suficiente para arquitectura
            arch_budget_tokens = min(15000, self.thinking_budget)  # Mantener relación correcta
            
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=arch_max_tokens,
                temperature=self.temperature,
                messages=messages,
                thinking={
                    "type": "enabled",
                    "budget_tokens": arch_budget_tokens
                }
            ) as stream:
                
                emit_book_progress_update(book_id, {
                    'current': 15,
                    'total': 100,
                    'status': 'thinking',
                    'status_message': 'Claude está diseñando la arquitectura de tu libro...',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                
                current_block_index = None
                
                async for event in stream:
                    chunk_count += 1
                    
                    # Thinking blocks
                    if event.type == "content_block_start" and event.content_block.type == "thinking":
                        current_block_index = event.index
                        emit_generation_log(book_id, 'thinking', 'Analizando requerimientos y diseñando estructura...')
                        
                    elif event.type == "content_block_delta" and hasattr(event, 'delta'):
                        if hasattr(event.delta, 'text'):
                            text_chunk = event.delta.text
                            
                            # Si es thinking content
                            if current_block_index is not None and event.index == current_block_index:
                                thinking_content.append(text_chunk)
                                
                                if chunk_count % 50 == 0:
                                    emit_book_progress_update(book_id, {
                                        'current': 25,
                                        'total': 100,
                                        'status': 'thinking',
                                        'status_message': 'Estructurando capítulos y desarrollo narrativo...',
                                        'timestamp': datetime.now(timezone.utc).isoformat()
                                    })
                            
                            # Content principal
                            else:
                                full_content.append(text_chunk)
                                
                                if chunk_count % 30 == 0:
                                    emit_book_progress_update(book_id, {
                                        'current': 50 + (chunk_count % 200) // 10,  # 50-70%
                                        'total': 100,
                                        'status': 'writing',
                                        'status_message': 'Generando estructura detallada del libro...',
                                        'timestamp': datetime.now(timezone.utc).isoformat()
                                    })
                    
                    elif event.type == "content_block_stop":
                        if current_block_index == event.index:
                            emit_generation_log(book_id, 'thinking', 'Análisis completado')
                            current_block_index = None
                        else:
                            emit_book_progress_update(book_id, {
                                'current': 90,
                                'total': 100,
                                'status': 'finalizing',
                                'status_message': 'Finalizando arquitectura del libro...',
                                'timestamp': datetime.now(timezone.utc).isoformat()
                            })
                
                # Obtener mensaje final
                final_message = await stream.get_final_message()
                
                # Parsear la arquitectura generada
                complete_content = ''.join(full_content)
                complete_thinking = ''.join(thinking_content)
                
                # Intentar parsear como JSON, si falla mantener como texto
                try:
                    import json
                    architecture = json.loads(complete_content)
                except json.JSONDecodeError:
                    # Si no es JSON válido, estructurarlo manualmente
                    architecture = {
                        "raw_content": complete_content,
                        "summary": "Arquitectura generada - requiere formato manual",
                        "type": "text"
                    }
                
                emit_generation_log(book_id, 'success', 
                    f'Arquitectura del libro generada exitosamente')
                
                logger.info("architecture_generation_completed",
                           book_id=book_id,
                           architecture_length=len(complete_content),
                           thinking_length=len(complete_thinking))
                
                return {
                    'architecture': architecture,
                    'thinking': complete_thinking,
                    'usage': {
                        'prompt_tokens': final_message.usage.input_tokens,
                        'completion_tokens': final_message.usage.output_tokens,
                        'thinking_tokens': getattr(final_message.usage, 'thinking_tokens', 0),
                        'total_tokens': final_message.usage.input_tokens + final_message.usage.output_tokens
                    },
                    'model': final_message.model,
                    'stop_reason': final_message.stop_reason
                }
                
        except Exception as e:
            logger.error(f"Architecture generation error: {str(e)}")
            
            from app.routes.websocket import emit_generation_log
            emit_generation_log(book_id, 'error', f'Error generando arquitectura: {str(e)}')
            
            raise
    
    def _build_architecture_messages(self, book_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Construye los mensajes para generar únicamente la arquitectura del libro"""
        system_prompt = self._build_architecture_system_prompt()
        user_prompt = self._build_architecture_user_prompt(book_params)
        
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
    
    def _build_architecture_system_prompt(self) -> str:
        """Sistema prompt optimizado para generación de arquitectura únicamente"""
        return """You are a professional book architect. Your job is to create a detailed book structure and architecture that the user can review and approve before full content generation.

🚨 CRITICAL: Generate ONLY the book architecture, NOT the full content.

Your output must be a well-structured JSON with the following format:

```json
{
  "title": "Book Title",
  "summary": "Brief book description (2-3 sentences)",
  "target_pages": 150,
  "estimated_words": 45000,
  "genre": "specified_genre",
  "tone": "specified_tone",
  "structure": {
    "introduction": {
      "title": "Introduction Title",
      "summary": "What this introduction will cover",
      "estimated_pages": 5
    },
    "chapters": [
      {
        "number": 1,
        "title": "Chapter Title",
        "summary": "Detailed summary of what this chapter will cover",
        "key_points": ["Point 1", "Point 2", "Point 3"],
        "estimated_pages": 12,
        "learning_objectives": ["What reader will learn"]
      }
    ],
    "conclusion": {
      "title": "Conclusion Title", 
      "summary": "What the conclusion will cover",
      "estimated_pages": 3
    }
  },
  "characters": [
    {
      "name": "Character Name",
      "role": "Character role/importance",
      "description": "Brief character description"
    }
  ],
  "key_themes": ["Theme 1", "Theme 2"],
  "writing_approach": "How the book will be written",
  "special_sections": [
    {
      "type": "exercises/examples/case_studies",
      "frequency": "per chapter/throughout book",
      "purpose": "Why included"
    }
  ]
}
```

REQUIREMENTS:
- Generate a detailed chapter-by-chapter breakdown
- Each chapter should have clear learning objectives and key points
- Estimate realistic page counts for each section
- Include characters if it's a fiction book
- Suggest special sections (exercises, examples, etc.) if relevant
- Make sure total estimated pages match the target
- Provide enough detail for user to understand the full book structure

DO NOT write any actual book content - only the detailed architecture and structure."""

    def _build_architecture_user_prompt(self, book_params: Dict[str, Any]) -> str:
        """Construye el prompt del usuario para arquitectura únicamente"""
        language_map = {
            'es': 'Spanish',
            'en': 'English', 
            'pt': 'Portuguese',
            'fr': 'French'
        }
        
        user_language = book_params.get('language', 'es')
        language_name = language_map.get(user_language, user_language)
        
        return f"""Create a detailed book architecture for the following specifications:

**BOOK SPECIFICATIONS:**
- Title: {book_params.get('title', 'Untitled Book')}
- Genre: {book_params.get('genre', 'General')}
- Target Audience: {book_params.get('target_audience', 'General audience')}
- Writing Style: {book_params.get('writing_style', 'Professional and engaging')}
- Tone: {book_params.get('tone', 'Informative')}
- Language: {language_name.upper()}
- Target Pages: {book_params.get('page_count', 50)}
- Number of Chapters: {book_params.get('chapter_count', 10)}

**CONTENT FOCUS:**
- Key Topics: {book_params.get('key_topics', 'As relevant to the title')}
- Additional Instructions: {book_params.get('additional_instructions', 'None')}

**STRUCTURE REQUIREMENTS:**
- Include Table of Contents: {book_params.get('include_toc', True)}
- Include Introduction: {book_params.get('include_introduction', True)} 
- Include Conclusion: {book_params.get('include_conclusion', True)}

**IMPORTANT:**
- Create the architecture in {language_name.upper()}
- Ensure all chapter summaries and content descriptions are in {language_name.upper()}
- Structure should be appropriate for {book_params.get('genre', 'General')} genre
- Target a total of {book_params.get('page_count', 50)} pages
- Include {book_params.get('chapter_count', 10)} main chapters

Generate a comprehensive book architecture that the user can review, modify if needed, and approve before full content generation begins."""

    # MÉTODO PARA GENERACIÓN COMPLETA BASADA EN ARQUITECTURA APROBADA
    
    async def generate_book_from_architecture(self, book_id: int, book_params: Dict[str, Any], approved_architecture: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera el contenido completo del libro basado en una arquitectura previamente aprobada.
        
        Args:
            book_id: ID del libro
            book_params: Parámetros originales del libro
            approved_architecture: Arquitectura aprobada por el usuario
            
        Returns:
            Resultado de la generación con contenido completo
        """
        try:
            # Log crítico: verificar que se recibió toda la arquitectura
            logger.info("generating_from_approved_architecture",
                       book_id=book_id,
                       architecture_has_structure=bool(approved_architecture.get('structure')),
                       chapters_count=len(approved_architecture.get('structure', {}).get('chapters', [])),
                       characters_count=len(approved_architecture.get('characters', [])),
                       special_sections_count=len(approved_architecture.get('special_sections', [])),
                       has_introduction=bool(approved_architecture.get('structure', {}).get('introduction')),
                       has_conclusion=bool(approved_architecture.get('structure', {}).get('conclusion')),
                       target_pages=approved_architecture.get('target_pages'),
                       estimated_words=approved_architecture.get('estimated_words'),
                       using_max_tokens=self.max_tokens)
            
            # Preparar el prompt específico para generación basada en arquitectura
            messages = self._build_architecture_based_messages(book_params, approved_architecture)
            
            # Variables para acumular respuesta y métricas
            full_content = []
            thinking_content = []
            chunk_count = 0
            total_chars = 0
            current_block_index = None
            
            # Emisión de evento de inicio
            from app.routes.websocket import emit_book_progress_update, emit_generation_log
            
            emit_book_progress_update(book_id, {
                'current': 5,
                'total': 100,
                'status': 'connecting',
                'status_message': 'Conectando con Claude AI para generar libro completo...',
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
                    'status_message': 'Claude está revisando la arquitectura aprobada...',
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
                            'status_message': 'Claude está planificando la escritura basada en tu arquitectura...',
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        })
                        
                        # Emit thinking start event
                        from app.routes.websocket import emit_thinking_start
                        emit_thinking_start(book_id)
                        emit_generation_log(book_id, 'thinking', 'Iniciando escritura basada en arquitectura aprobada...')
                    
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
                                        'status_message': f'Desarrollando contenido basado en arquitectura... ({len(full_thinking.split())} palabras de pensamiento)',
                                        'timestamp': datetime.now(timezone.utc).isoformat()
                                    })
                            
                            # Content principal
                            else:
                                full_content.append(text_chunk)
                                
                                # Calcular progreso basado en contenido generado
                                estimated_final_chars = approved_architecture.get('estimated_words', book_params.get('page_count', 50) * 350) * 5  # ~5 chars per word
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
                                        'status_message': f'Escribiendo tu libro según arquitectura... {actual_pages} páginas generadas',
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
                                        emit_generation_log(book_id, 'info', 
                                            f'Progreso: {actual_pages} páginas, {actual_words:,} palabras, {actual_chapters} capítulos')
                    
                    elif event.type == "content_block_stop":
                        if current_block_index == event.index:
                            # Fin del thinking
                            from app.routes.websocket import emit_thinking_complete
                            full_thinking = ''.join(thinking_content)
                            emit_thinking_complete(book_id, {
                                'total_chars': len(full_thinking),
                                'total_words': len(full_thinking.split())
                            })
                            emit_generation_log(book_id, 'thinking', f'Planificación completada: {len(full_thinking.split())} palabras de pensamiento')
                            
                            emit_book_progress_update(book_id, {
                                'current': 25,
                                'total': 100,
                                'status': 'analysis_complete',
                                'status_message': 'Planificación completada, escribiendo contenido...',
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
                
                # Validar que se cumplió con el objetivo de páginas
                requested_pages = approved_architecture.get('target_pages', book_params.get('page_count', 50))
                deficit_percentage = ((requested_pages - final_pages) / requested_pages) * 100 if requested_pages > 0 else 0
                
                if final_pages < requested_pages * 0.95:  # Allow 5% margin
                    logger.warning("architecture_based_book_below_page_count",
                                 book_id=book_id,
                                 requested_pages=requested_pages,
                                 actual_pages=final_pages,
                                 deficit_percentage=deficit_percentage)
                    
                    emit_generation_log(book_id, 'warning', 
                        f'⚠️ Se generaron {final_pages} páginas de las {requested_pages} estimadas en la arquitectura ({deficit_percentage:.1f}% menos)')
                else:
                    emit_generation_log(book_id, 'success', 
                        f'✅ Objetivo cumplido: Se generaron {final_pages} páginas (arquitectura estimaba: {requested_pages})')
                
                # Emit final log
                emit_generation_log(book_id, 'success', 
                    f'Generación basada en arquitectura completada: {final_pages} páginas, {final_words:,} palabras, {final_chapters} capítulos')
                
                logger.info("architecture_based_book_generation_completed",
                           book_id=book_id,
                           total_chunks=chunk_count,
                           total_characters=total_chars,
                           final_words=final_words,
                           final_pages=final_pages,
                           thinking_length=len(complete_thinking),
                           architecture_pages_estimate=requested_pages)
                
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
                        'chapters': final_chapters,
                        'architecture_based': True,
                        'architecture_pages_estimate': requested_pages
                    }
                }
                
        except Exception as e:
            logger.error(f"Architecture-based generation error: {str(e)}")
            
            emit_generation_log(book_id, 'error', f'Error generando libro basado en arquitectura: {str(e)}')
            
            raise

    def _build_architecture_based_messages(self, book_params: Dict[str, Any], approved_architecture: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Construye los mensajes para generar el libro basado en arquitectura aprobada"""
        system_prompt = self._build_architecture_based_system_prompt()
        user_prompt = self._build_architecture_based_user_prompt(book_params, approved_architecture)
        
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

    def _build_architecture_based_system_prompt(self) -> str:
        """Sistema prompt para generación basada en arquitectura aprobada"""
        return """You are a professional book writer who must generate complete book content based on a pre-approved architecture.

🚨 CRITICAL REQUIREMENTS:

1. **STRICT ARCHITECTURE ADHERENCE**: You MUST follow the provided architecture exactly as specified. Do not deviate from the approved structure, chapter titles, or content outlines.

2. **COMPLETE CONTENT GENERATION**: Write the full content for each section, not just outlines or summaries. Every chapter must be fully written with detailed explanations, examples, and comprehensive coverage.

3. **EXACT CHAPTER STRUCTURE**: Follow the exact chapter sequence, titles, and content summaries provided in the architecture.

4. **PAGE COUNT COMPLIANCE**: The architecture specifies target pages for each section. You must generate enough content to meet these page targets.

5. **CONSISTENCY**: Maintain consistent tone, writing style, and approach as specified in the original book parameters and architecture.

WRITING APPROACH:
- Start with the exact title from the architecture
- Include table of contents if specified
- Write introduction exactly as outlined in architecture
- Generate each chapter with full content following the provided summaries and key points
- Include conclusion as specified
- Maintain professional formatting and structure
- Ensure content depth matches the estimated page counts

FORMATTING:
- Use # for main title
- Use ## for major sections (Introduction, Table of Contents, Conclusion)
- Use ### for chapter headers (exactly as specified in architecture)
- Use #### for subsections within chapters
- Maintain clear paragraph structure
- Include examples, explanations, and detailed content as appropriate

FORBIDDEN:
- Do not change chapter titles from the approved architecture
- Do not skip or combine chapters
- Do not write summaries instead of full content
- Do not add chapters not specified in the architecture
- Do not change the overall structure or flow

Remember: The user has already approved this specific architecture. Your job is to bring it to life with complete, high-quality content."""

    def _build_architecture_based_user_prompt(self, book_params: Dict[str, Any], approved_architecture: Dict[str, Any]) -> str:
        """Construye el prompt del usuario para generación basada en arquitectura"""
        language_map = {
            'es': 'Spanish',
            'en': 'English', 
            'pt': 'Portuguese',
            'fr': 'French'
        }
        
        user_language = book_params.get('language', 'es')
        language_name = language_map.get(user_language, user_language)
        
        # CRÍTICO: Usar siempre los valores correctos de la base de datos para páginas y palabras
        # No confiar en los valores de la arquitectura que pueden estar desactualizados
        db_pages = book_params.get('page_count', approved_architecture.get('target_pages', 150))
        db_format = book_params.get('page_size', approved_architecture.get('format_size', 'pocket'))
        
        # Calcular palabras con multiplicadores correctos
        format_multipliers = {
            'pocket': 220,
            'A5': 250,
            'B5': 280,
            'letter': 350
        }
        calculated_words = db_pages * format_multipliers.get(db_format, 220)
        
        # Forzar valores correctos en la arquitectura antes de serializar
        approved_architecture['target_pages'] = db_pages
        approved_architecture['estimated_words'] = calculated_words
        approved_architecture['format_size'] = db_format
        
        # Serializar la arquitectura para el prompt con valores corregidos
        import json
        architecture_json = json.dumps(approved_architecture, indent=2, ensure_ascii=False)
        
        # Log para verificar datos enviados a Claude
        logger.info("architecture_prompt_data", 
                   db_pages=db_pages,
                   calculated_words=calculated_words,
                   format_size=db_format,
                   architecture_chapters=len(approved_architecture.get('structure', {}).get('chapters', [])),
                   architecture_characters=len(approved_architecture.get('characters', [])),
                   architecture_special_sections=len(approved_architecture.get('special_sections', [])))
        
        return f"""Generate the complete book content based on this approved architecture:

**ORIGINAL BOOK PARAMETERS:**
- Language: {language_name.upper()}
- Genre: {book_params.get('genre', 'General')}
- Target Audience: {book_params.get('target_audience', 'General audience')}
- Writing Style: {book_params.get('writing_style', 'Professional and engaging')}
- Tone: {book_params.get('tone', 'Informative')}
- Format Size: {db_format.upper()}
- Line Spacing: {book_params.get('line_spacing', 'medium')}

**APPROVED ARCHITECTURE (USER-EDITED):**
```json
{architecture_json}
```

**MANDATORY REQUIREMENTS - NO EXCEPTIONS:**
- Write EVERYTHING in {language_name.upper()}
- Follow the architecture structure EXACTLY as approved by the user
- Generate COMPLETE content for each chapter (not summaries or outlines)
- Meet the estimated page counts specified in the architecture
- Use the exact chapter titles and sequence from the architecture
- Include ALL key points and learning objectives specified for each chapter
- Include ALL characters and their roles as specified in the architecture
- Implement ALL special sections as defined in the architecture
- Write in the specified tone and style consistently
- Generate approximately {calculated_words:,} words total (EXACT TARGET)
- Target {db_pages} pages total (EXACT TARGET for {db_format} format)

**ARCHITECTURE COMPLIANCE:**
- Every chapter MUST include all key points listed in the architecture
- Every chapter MUST address all learning objectives specified
- All characters mentioned in the architecture MUST appear in relevant contexts
- All special sections (exercises, case studies, etc.) MUST be integrated appropriately
- The writing approach and themes MUST match the approved architecture

**CONTENT DEPTH REQUIREMENTS:**
- Each chapter must be fully developed with detailed explanations (minimum 80% of estimated pages per chapter)
- Include practical examples, case studies, and real-world applications where specified
- Provide comprehensive coverage of each topic outlined in the user-edited architecture
- Ensure content quality matches what readers would expect from a professionally published book
- Maintain consistent depth and detail throughout all chapters
- Each key point must be thoroughly explained with supporting details
- Each learning objective must be clearly addressed with actionable content

**CRITICAL SUCCESS FACTORS:**
- The user has spent time editing and perfecting this architecture - honor their decisions exactly
- This is the final content generation - it must be complete and publication-ready
- Use the full {self.max_tokens:,} token capacity to ensure maximum quality and completeness
- Every element in the approved architecture is important and must be included

Please generate the complete book content following this user-approved architecture exactly."""

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

    # MÉTODO PARA REGENERACIÓN DE ARQUITECTURA CON FEEDBACK

    async def regenerate_book_architecture(self, book_id: int, book_params: Dict[str, Any], current_architecture: Dict[str, Any], feedback_what: str, feedback_how: str) -> Dict[str, Any]:
        """
        Regenera la arquitectura del libro basada en feedback específico del usuario.
        
        Args:
            book_id: ID del libro
            book_params: Parámetros originales del libro
            current_architecture: Arquitectura actual que se va a mejorar
            feedback_what: Qué no le gustó al usuario de la arquitectura actual
            feedback_how: Qué cambios específicos quiere el usuario
            
        Returns:
            Resultado con la arquitectura regenerada mejorada
        """
        try:
            # Log del inicio de regeneración
            logger.info("starting_architecture_regeneration",
                       book_id=book_id,
                       has_current_architecture=bool(current_architecture),
                       feedback_what_length=len(feedback_what),
                       feedback_how_length=len(feedback_how))
                       
            # Preparar el prompt específico para regeneración con feedback
            messages = self._build_regeneration_messages(book_params, current_architecture, feedback_what, feedback_how)
            
            # Variables para acumular respuesta
            full_content = []
            thinking_content = []
            chunk_count = 0
            
            # Emisión de evento de inicio
            from app.routes.websocket import emit_book_progress_update, emit_generation_log
            
            emit_book_progress_update(book_id, {
                'current': 5,
                'total': 100,
                'status': 'connecting',
                'status_message': 'Conectando con Claude AI para regenerar arquitectura...',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # Crear streaming request con thinking habilitado
            # Para regeneración usamos tokens optimizados similar a arquitectura inicial
            regen_max_tokens = min(16000, self.max_tokens)  # Suficiente para arquitectura mejorada
            regen_budget_tokens = min(15000, self.thinking_budget)
            
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=regen_max_tokens,
                temperature=self.temperature,
                messages=messages,
                thinking={
                    "type": "enabled",
                    "budget_tokens": regen_budget_tokens
                }
            ) as stream:
                
                emit_book_progress_update(book_id, {
                    'current': 15,
                    'total': 100,
                    'status': 'thinking',
                    'status_message': 'Claude está analizando tu feedback y mejorando la arquitectura...',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                
                current_block_index = None
                
                async for event in stream:
                    chunk_count += 1
                    
                    # Thinking blocks
                    if event.type == "content_block_start" and event.content_block.type == "thinking":
                        current_block_index = event.index
                        emit_generation_log(book_id, 'thinking', 'Analizando feedback y replanteando arquitectura...')
                        
                    elif event.type == "content_block_delta" and hasattr(event, 'delta'):
                        if hasattr(event.delta, 'text'):
                            text_chunk = event.delta.text
                            
                            # Si es thinking content
                            if current_block_index is not None and event.index == current_block_index:
                                thinking_content.append(text_chunk)
                                
                                if chunk_count % 50 == 0:
                                    emit_book_progress_update(book_id, {
                                        'current': 30,
                                        'total': 100,
                                        'status': 'thinking',
                                        'status_message': 'Incorporando tus sugerencias y refinando estructura...',
                                        'timestamp': datetime.now(timezone.utc).isoformat()
                                    })
                            
                            # Content principal
                            else:
                                full_content.append(text_chunk)
                                
                                if chunk_count % 30 == 0:
                                    emit_book_progress_update(book_id, {
                                        'current': 50 + (chunk_count % 200) // 10,  # 50-70%
                                        'total': 100,
                                        'status': 'writing',
                                        'status_message': 'Generando arquitectura mejorada basada en tu feedback...',
                                        'timestamp': datetime.now(timezone.utc).isoformat()
                                    })
                    
                    elif event.type == "content_block_stop":
                        if current_block_index == event.index:
                            emit_generation_log(book_id, 'thinking', 'Análisis de feedback completado')
                            current_block_index = None
                        else:
                            emit_book_progress_update(book_id, {
                                'current': 90,
                                'total': 100,
                                'status': 'finalizing',
                                'status_message': 'Finalizando arquitectura regenerada...',
                                'timestamp': datetime.now(timezone.utc).isoformat()
                            })
                
                # Obtener mensaje final
                final_message = await stream.get_final_message()
                
                # Parsear la arquitectura regenerada
                complete_content = ''.join(full_content)
                complete_thinking = ''.join(thinking_content)
                
                # Intentar parsear como JSON, si falla mantener como texto
                try:
                    import json
                    architecture = json.loads(complete_content)
                    
                    # Validar que la arquitectura regenerada tenga la estructura mínima requerida
                    if not architecture.get('structure') or not architecture.get('structure', {}).get('chapters'):
                        logger.warning("regenerated_architecture_incomplete", book_id=book_id)
                        # Intentar usar la arquitectura actual con mejoras textuales
                        architecture = current_architecture.copy()
                        architecture['regeneration_notes'] = complete_content
                        architecture['feedback_incorporated'] = True
                        
                except json.JSONDecodeError:
                    logger.warning("regenerated_architecture_json_error", book_id=book_id)
                    # Si no es JSON válido, usar la arquitectura actual como base
                    architecture = current_architecture.copy()
                    architecture['regeneration_content'] = complete_content
                    architecture['feedback_incorporated'] = True
                    architecture['regeneration_method'] = 'text_based'
                
                # Marcar que es una regeneración
                architecture['regenerated'] = True
                architecture['regeneration_timestamp'] = datetime.now(timezone.utc).isoformat()
                architecture['user_feedback'] = {
                    'what_disliked': feedback_what,
                    'requested_changes': feedback_how
                }
                
                emit_generation_log(book_id, 'success', 
                    f'Arquitectura regenerada exitosamente basada en tu feedback')
                
                logger.info("architecture_regeneration_completed",
                           book_id=book_id,
                           architecture_length=len(complete_content),
                           thinking_length=len(complete_thinking),
                           feedback_incorporated=True)
                
                return {
                    'architecture': architecture,
                    'thinking': complete_thinking,
                    'usage': {
                        'prompt_tokens': final_message.usage.input_tokens,
                        'completion_tokens': final_message.usage.output_tokens,
                        'thinking_tokens': getattr(final_message.usage, 'thinking_tokens', 0),
                        'total_tokens': final_message.usage.input_tokens + final_message.usage.output_tokens
                    },
                    'model': final_message.model,
                    'stop_reason': final_message.stop_reason,
                    'regenerated': True
                }
                
        except Exception as e:
            logger.error(f"Architecture regeneration error: {str(e)}")
            
            from app.routes.websocket import emit_generation_log
            emit_generation_log(book_id, 'error', f'Error regenerando arquitectura: {str(e)}')
            
            raise

    def _build_regeneration_messages(self, book_params: Dict[str, Any], current_architecture: Dict[str, Any], feedback_what: str, feedback_how: str) -> List[Dict[str, Any]]:
        """Construye los mensajes para regenerar arquitectura con feedback del usuario"""
        system_prompt = self._build_regeneration_system_prompt()
        user_prompt = self._build_regeneration_user_prompt(book_params, current_architecture, feedback_what, feedback_how)
        
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

    def _build_regeneration_system_prompt(self) -> str:
        """Sistema prompt para regeneración de arquitectura con feedback"""
        return """You are a professional book architect specialized in improving book structures based on user feedback.

🚨 CRITICAL: You must regenerate the book architecture incorporating the user's specific feedback while maintaining professional quality.

Your output must be a well-structured JSON with the same format as before, but improved based on the feedback:

```json
{
  "title": "Book Title (use original or improve if feedback suggests)",
  "summary": "Improved book description based on feedback",
  "target_pages": 150,
  "estimated_words": 45000,
  "genre": "specified_genre",
  "tone": "specified_tone (adjust if feedback suggests)",
  "writing_approach": "Improved approach based on feedback",
  "structure": {
    "introduction": {
      "title": "Introduction Title (improve if needed)",
      "summary": "Improved introduction outline",
      "estimated_pages": 5
    },
    "chapters": [
      {
        "number": 1,
        "title": "Improved Chapter Title",
        "summary": "Enhanced chapter summary based on feedback",
        "key_points": ["Improved or new points based on feedback"],
        "estimated_pages": 12,
        "learning_objectives": ["Enhanced learning objectives"]
      }
    ],
    "conclusion": {
      "title": "Conclusion Title", 
      "summary": "Improved conclusion outline",
      "estimated_pages": 3
    }
  },
  "characters": [
    {
      "name": "Character Name (enhance or add based on feedback)",
      "role": "Enhanced character role",
      "description": "Improved character description"
    }
  ],
  "key_themes": ["Enhanced themes based on feedback"],
  "special_sections": [
    {
      "type": "Enhanced or new section types",
      "frequency": "Adjusted frequency",
      "purpose": "Improved purpose based on feedback"
    }
  ],
  "improvements_made": ["List of specific improvements based on user feedback"],
  "feedback_addressed": true
}
```

FEEDBACK INCORPORATION REQUIREMENTS:
- Carefully analyze what the user didn't like and address those specific issues
- Implement the exact changes the user requested
- Improve weak areas identified in the feedback
- Enhance sections the user wants expanded
- Adjust tone, structure, or content focus as requested
- Add missing elements the user identified
- Remove or modify elements the user found unnecessary
- Maintain overall coherence while making requested changes

QUALITY REQUIREMENTS:
- Ensure the regenerated architecture is better than the original
- Address all feedback points systematically
- Maintain professional structure and completeness
- Keep the same JSON format for consistency
- Ensure chapter count and page estimates remain realistic
- Preserve good elements from the original while improving problematic areas

DO NOT simply make minor cosmetic changes - make substantial improvements based on the specific feedback provided."""

    def _build_regeneration_user_prompt(self, book_params: Dict[str, Any], current_architecture: Dict[str, Any], feedback_what: str, feedback_how: str) -> str:
        """Construye el prompt para regeneración con feedback específico"""
        language_map = {
            'es': 'Spanish',
            'en': 'English', 
            'pt': 'Portuguese',
            'fr': 'French'
        }
        
        user_language = book_params.get('language', 'es')
        language_name = language_map.get(user_language, user_language)
        
        # Serializar la arquitectura actual
        import json
        current_architecture_json = json.dumps(current_architecture, indent=2, ensure_ascii=False)
        
        return f"""Please regenerate the book architecture based on the user's specific feedback.

**ORIGINAL BOOK SPECIFICATIONS:**
- Title: {book_params.get('title', 'Untitled Book')}
- Genre: {book_params.get('genre', 'General')}
- Target Audience: {book_params.get('target_audience', 'General audience')}
- Writing Style: {book_params.get('writing_style', 'Professional and engaging')}
- Tone: {book_params.get('tone', 'Informative')}
- Language: {language_name.upper()}
- Target Pages: {book_params.get('page_count', 50)}
- Number of Chapters: {book_params.get('chapter_count', 10)}

**CURRENT ARCHITECTURE (TO BE IMPROVED):**
```json
{current_architecture_json}
```

**USER FEEDBACK - CRITICAL REQUIREMENTS:**

**What the user DIDN'T LIKE about the current architecture:**
{feedback_what}

**What the user WANTS CHANGED or IMPROVED:**
{feedback_how}

**REGENERATION REQUIREMENTS:**
- Address EVERY point mentioned in the user's feedback
- Make substantial improvements, not just minor tweaks
- If user wants more chapters, add them with detailed content
- If user wants different themes, incorporate them thoroughly
- If user wants character changes, implement them completely
- If user wants tone adjustments, reflect them throughout
- If user wants structural changes, rebuild the structure accordingly
- Maintain {language_name.upper()} language throughout
- Keep the target of {book_params.get('page_count', 50)} pages total
- Ensure the regenerated architecture is significantly better than the original

**FEEDBACK INCORPORATION CHECKLIST:**
- ✅ Analyze each feedback point systematically
- ✅ Address what the user didn't like by changing or removing those elements
- ✅ Implement the specific improvements the user requested
- ✅ Enhance weak areas identified in the feedback
- ✅ Add missing elements the user identified
- ✅ Adjust chapter structure if requested
- ✅ Modify character development if mentioned
- ✅ Update special sections based on feedback
- ✅ Improve writing approach or tone as suggested

**QUALITY ASSURANCE:**
- The new architecture must be noticeably better than the original
- Every aspect mentioned in the feedback must be addressed
- The result should align perfectly with the user's vision
- Maintain professional quality and structure throughout

Generate the improved architecture in {language_name.upper()} that fully incorporates the user's feedback and creates a superior book structure."""


# Singleton instance
_claude_service: Optional[ClaudeService] = None


def get_claude_service() -> ClaudeService:
    """Get or create Claude service instance."""
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeService()
    return _claude_service