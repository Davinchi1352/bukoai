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
from app.utils.retry import exponential_backoff_retry
from app.services.claude_service_coherence import BookCoherenceManager
from app.utils.structured_logging import track_book_generation_start, track_claude_api_call, track_generation_complete
import httpx
import time

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
        
        # Configurar timeouts generosos pero efectivos para libros de calidad
        http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=30.0,      # 30 segundos para conectar
                read=1800.0,       # 30 minutos para leer (libros extensos)
                write=60.0,        # 1 minuto para escribir
                pool=300.0         # 5 minutos para pool
            ),
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10,
                keepalive_expiry=300
            )
        )
        
        self.client = AsyncAnthropic(
            api_key=self.api_key,
            http_client=http_client
        )
        
        self.model = current_app.config.get('CLAUDE_MODEL', 'claude-sonnet-4-20250514')
        # 🚀 MAX_TOKENS OPTIMIZADOS: Específicos por tipo de contenido para mayor velocidad
        self.max_tokens_config = {
            'architecture': 16000,      # Reducido de 32000 - Suficiente para arquitectura
            'chunk_main': 28000,        # Reducido de 64000 - Optimizado para chunks principales
            'introduction': 8000,       # Reducido de 16000 - Introducciones compactas
            'conclusion': 8000,         # Reducido de 16000 - Conclusiones concisas
            'continuation': 16000,      # Nuevo - Para chunks de continuación
            'expansion': 12000          # Nuevo - Para expansiones orgánicas (deshabilitadas)
        }
        self.max_tokens = current_app.config.get('CLAUDE_MAX_TOKENS', 28000)  # Default optimizado
        self.temperature = current_app.config.get('CLAUDE_TEMPERATURE', 1.0)
        self.thinking_budget = current_app.config.get('CLAUDE_THINKING_BUDGET', 25000)  # Optimizado para velocidad
        
        # Multi-chunk configuration
        self.chunk_overlap = 500  # Tokens de overlap entre chunks para continuidad
        self.max_chunks = 5       # Máximo de chunks por libro
        
        # Timeouts generosos para contenidos extensos de alta calidad
        self.architecture_timeout = 2400  # 40 minutos para arquitectura (contenidos extensos)
        self.chunk_timeout = 3600         # 60 minutos por chunk (sin cortes prematuros)
        self.thinking_timeout = 1200      # 20 minutos adicionales para thinking complejo
        
        # Circuit breaker para 10K usuarios - balance entre estabilidad y disponibilidad
        self.error_count = 0
        self.max_errors = 5               # Más tolerancia con alta carga
        self.circuit_open_time = None
        self.circuit_timeout = 300        # 5 minutos de espera (recuperación rápida)
        
        # Monitoreo de progreso optimizado para alta concurrencia
        self.last_progress_time = None
        self.progress_timeout = 1200      # 20 minutos sin progreso = posible cuelgue
        self.progress_check_interval = 50 # Verificar progreso cada 50 chunks (menos overhead)
        
        # Coherence manager
        self.coherence_manager = BookCoherenceManager()
        
        # Retry configuration
        self.max_retries = current_app.config.get('CLAUDE_MAX_RETRIES', 3)
        self.retry_delay = current_app.config.get('CLAUDE_RETRY_DELAY', 1.0)
        
        logger.info("claude_service_initialized", 
                   model=self.model,
                   max_tokens_optimized=self.max_tokens_config,
                   architecture_timeout=self.architecture_timeout,
                   chunk_timeout=self.chunk_timeout,
                   target_users=10000,
                   progress_check_interval=self.progress_check_interval)
    
    def _get_optimized_tokens(self, content_type: str) -> int:
        """🚀 Obtiene tokens optimizados según tipo de contenido"""
        return self.max_tokens_config.get(content_type, self.max_tokens)
    
    def _get_optimized_thinking_budget(self, content_type: str) -> int:
        """🚀 Obtiene thinking budget optimizado según tipo de contenido"""
        max_tokens = self._get_optimized_tokens(content_type)
        return min(max_tokens - 1000, self.thinking_budget)  # Dejar margen de 1000 tokens
    
    # =====================================
    # CIRCUIT BREAKER Y MONITOREO
    # =====================================
    
    def _check_circuit_breaker(self):
        """Verifica si el circuit breaker está abierto"""
        if self.circuit_open_time:
            if datetime.now(timezone.utc).timestamp() - self.circuit_open_time < self.circuit_timeout:
                raise Exception(f"Circuit breaker abierto. Esperando {self.circuit_timeout}s")
            else:
                # Reset circuit breaker
                self.circuit_open_time = None
                self.error_count = 0
                logger.info("circuit_breaker_reset", 
                           after_timeout=self.circuit_timeout)
    
    def _handle_api_error(self, error: Exception):
        """Maneja errores de API y actualiza circuit breaker"""
        self.error_count += 1
        logger.error("claude_api_error", 
                    error=str(error),
                    error_count=self.error_count,
                    max_errors=self.max_errors)
        
        if self.error_count >= self.max_errors:
            self.circuit_open_time = datetime.now(timezone.utc).timestamp()
            logger.error("circuit_breaker_opened", 
                        error_count=self.error_count,
                        timeout=self.circuit_timeout)
    
    def _handle_api_success(self):
        """Maneja éxito de API y resetea contadores"""
        if self.error_count > 0:
            logger.info("claude_api_recovered", 
                       previous_errors=self.error_count)
            self.error_count = 0
    
    def _update_progress(self, book_id: int, operation: str, details: str = None):
        """Actualiza el timestamp de progreso para monitoreo inteligente"""
        self.last_progress_time = datetime.now(timezone.utc).timestamp()
        logger.info("claude_progress_update",
                   book_id=book_id,
                   operation=operation,
                   details=details,
                   timestamp=self.last_progress_time)
    
    def _check_progress_timeout(self, book_id: int, operation: str) -> bool:
        """Verifica si ha pasado demasiado tiempo sin progreso (posible cuelgue)"""
        if not self.last_progress_time:
            return False
            
        time_since_progress = datetime.now(timezone.utc).timestamp() - self.last_progress_time
        
        if time_since_progress > self.progress_timeout:
            logger.warning("possible_hang_detected",
                          book_id=book_id,
                          operation=operation,
                          time_since_progress=time_since_progress,
                          progress_timeout=self.progress_timeout)
            return True
            
        return False
    
    # =====================================
    # MÉTODOS PRINCIPALES DE GENERACIÓN
    # =====================================
    
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
            # Verificar circuit breaker
            self._check_circuit_breaker()
            
            # Iniciar tracking de generación
            track_book_generation_start(book_id, book_params.get('user_id', 0), 
                                       'architecture', book_params)
            
            # Preparar el prompt específico para arquitectura
            messages = self._build_architecture_messages(book_params)
            
            # Track inicio de llamada a Claude API
            api_start_time = time.time()
            
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
            
            # 🚀 OPTIMIZACIÓN: Tokens específicos optimizados para arquitectura
            arch_max_tokens = self._get_optimized_tokens('architecture')  # 16000 optimizado
            arch_budget_tokens = self._get_optimized_thinking_budget('architecture')  # Optimizado
            
            logger.info("starting_architecture_stream",
                       book_id=book_id,
                       max_tokens=arch_max_tokens,
                       thinking_budget=arch_budget_tokens,
                       timeout=self.architecture_timeout)
            
            # Usar timeout generoso pero efectivo para arquitectura de calidad
            async with asyncio.timeout(self.architecture_timeout):
                async with self.client.messages.stream(
                    model=self.model,
                    max_tokens=arch_max_tokens,
                    temperature=self.temperature,
                    messages=messages,
                    thinking={
                        "type": "enabled",
                        "budget_tokens": arch_budget_tokens
                    },
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
                        
                        # Actualizar progreso optimizado para 10K usuarios (menos overhead)
                        if chunk_count % self.progress_check_interval == 0:
                            self._update_progress(book_id, "architecture_generation", 
                                                f"Procesando chunk {chunk_count}")
                        
                        # Thinking blocks
                        if event.type == "content_block_start" and event.content_block.type == "thinking":
                            current_block_index = event.index
                            self._update_progress(book_id, "architecture_thinking", "Iniciando análisis")
                            emit_generation_log(book_id, 'thinking', 'Analizando requerimientos y diseñando estructura...')
                            
                        elif event.type == "content_block_delta" and hasattr(event, 'delta'):
                            if hasattr(event.delta, 'text'):
                                text_chunk = event.delta.text
                                
                                # Si es thinking content
                                if current_block_index is not None and event.index == current_block_index:
                                    thinking_content.append(text_chunk)
                                    
                                    if chunk_count % (self.progress_check_interval * 2) == 0:  # Menos updates de UI
                                        emit_book_progress_update(book_id, {
                                            'current': 25,
                                            'total': 100,
                                            'status': 'thinking',
                                            'status_message': f'Estructurando capítulos... ({chunk_count} chunks)',
                                            'timestamp': datetime.now(timezone.utc).isoformat()
                                        })
                                
                                # Content principal
                                else:
                                    full_content.append(text_chunk)
                                    
                                    if chunk_count % self.progress_check_interval == 0:
                                        progress_pct = min(85, 50 + (chunk_count // 20))  # Más granular
                                        emit_book_progress_update(book_id, {
                                            'current': progress_pct,
                                            'total': 100,
                                            'status': 'writing',
                                            'status_message': f'Generando arquitectura... ({chunk_count} chunks procesados)',
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
                    
                    # Track finalización de Claude API call
                    api_duration = time.time() - api_start_time
                    total_tokens = (final_message.usage.input_tokens + 
                                  final_message.usage.output_tokens + 
                                  getattr(final_message.usage, 'thinking_tokens', 0))
                    
                    track_claude_api_call(book_id, 'architecture_generation', api_duration,
                                        total_tokens, 'success', self.model)
                    
                    # Marcar éxito en circuit breaker
                    self._handle_api_success()
                    
                    # Parsear la arquitectura generada
                    complete_content = ''.join(full_content)
                    complete_thinking = ''.join(thinking_content)
                    
                    # Intentar parsear como JSON con parser robusto
                    import json
                    import re
                    
                    def extract_json_from_response(content: str) -> dict:
                        """
                        Extrae JSON de respuesta de Claude de manera robusta
                        """
                        # 1. Intentar parsear directamente
                        try:
                            return json.loads(content.strip())
                        except json.JSONDecodeError:
                            pass
                        
                        # 2. Buscar bloques de código JSON (```json ... ```)
                        json_pattern = r'```json\s*([\s\S]*?)\s*```'
                        json_match = re.search(json_pattern, content, re.IGNORECASE)
                        if json_match:
                            try:
                                extracted_json = json_match.group(1).strip()
                                parsed = json.loads(extracted_json)
                                # Si el JSON tiene un wrapper como "book_architecture", extraerlo
                                if isinstance(parsed, dict) and len(parsed) == 1:
                                    wrapper_key = list(parsed.keys())[0]
                                    if 'architecture' in wrapper_key.lower() or 'book' in wrapper_key.lower():
                                        return parsed[wrapper_key]
                                return parsed
                            except json.JSONDecodeError:
                                pass
                        
                        # 3. Buscar cualquier objeto JSON válido (empiece con { y termine con })
                        brace_pattern = r'\{.*\}'
                        brace_match = re.search(brace_pattern, content, re.DOTALL)
                        if brace_match:
                            try:
                                json_text = brace_match.group(0)
                                return json.loads(json_text)
                            except json.JSONDecodeError:
                                pass
                        
                        # 4. Si todo falla, retornar None para manejar el error
                        return None
                    
                    architecture = extract_json_from_response(complete_content)
                    
                    if architecture is None:
                        # Si no se pudo extraer JSON válido, crear estructura mínima
                        logger.error("failed_to_parse_architecture_json",
                                   book_id=book_id,
                                   content_preview=complete_content[:500],
                                   content_length=len(complete_content))
                        
                        # Intentar extraer información básica del texto
                        lines = complete_content.split('\n')
                        title_line = next((line for line in lines if 'title' in line.lower()), "")
                        
                        architecture = {
                            "title": book_params.get('title', 'Untitled Book'),
                            "summary": "Error parsing JSON response from Claude",
                            "target_pages": book_params.get('page_count', 50),
                            "estimated_words": book_params.get('page_count', 50) * 300,
                            "genre": book_params.get('genre', 'General'),
                            "tone": book_params.get('tone', 'Informative'),
                            "target_audience": book_params.get('target_audience', 'General'),
                            "language": book_params.get('language', 'es'),
                            "page_size": book_params.get('format_size', 'pocket'),
                            "line_spacing": book_params.get('line_spacing', 'medium'),
                            "chapter_count": book_params.get('chapter_count', 8),
                            "writing_style": book_params.get('writing_style', 'Professional'),
                            "include_toc": book_params.get('include_toc', True),
                            "include_introduction": book_params.get('include_introduction', True),
                            "include_conclusion": book_params.get('include_conclusion', True),
                            "structure": {
                                "introduction": {
                                    "title": "Introducción",
                                    "summary": "Introducción al tema del libro",
                                    "estimated_pages": 3
                                },
                                "chapters": [
                                    {
                                        "number": i,
                                        "title": f"Capítulo {i}: Contenido Principal {i}",
                                        "summary": f"Desarrollo del tema principal - parte {i}",
                                        "key_points": ["Punto clave 1", "Punto clave 2", "Punto clave 3"],
                                        "estimated_pages": max(4, (book_params.get('page_count', 50) - 6) // book_params.get('chapter_count', 8)),
                                        "learning_objectives": [f"Objetivo de aprendizaje {i}"]
                                    }
                                    for i in range(1, book_params.get('chapter_count', 8) + 1)
                                ],
                                "conclusion": {
                                    "title": "Conclusión",
                                    "summary": "Resumen y reflexiones finales",
                                    "estimated_pages": 3
                                }
                            },
                            "characters": [],
                            "key_themes": ["Tema principal"],
                            "writing_approach": "Enfoque directo y práctico",
                            "special_sections": [],
                            "additional_instructions": book_params.get('additional_instructions', ''),
                            "raw_content": complete_content,
                            "parsing_error": True
                        }
                    
                    emit_generation_log(book_id, 'success', 
                        f'Arquitectura del libro generada exitosamente')
                    
                    logger.info("architecture_generation_completed",
                               book_id=book_id,
                               architecture_length=len(complete_content),
                               thinking_length=len(complete_thinking),
                               tokens_used=final_message.usage.input_tokens + final_message.usage.output_tokens)
                    
                    return {
                        'architecture': architecture,
                        'thinking': complete_thinking,
                        'usage': {
                            'prompt_tokens': final_message.usage.input_tokens,
                            'completion_tokens': final_message.usage.output_tokens,
                            'thinking_tokens': getattr(final_message.usage, 'thinking_tokens', 0),
                            'total_tokens': final_message.usage.input_tokens + final_message.usage.output_tokens + getattr(final_message.usage, 'thinking_tokens', 0)
                        },
                        'model': final_message.model,
                        'stop_reason': final_message.stop_reason
                    }
                
        except asyncio.TimeoutError:
            error_msg = f"Timeout generando arquitectura después de {self.architecture_timeout}s"
            logger.error("architecture_generation_timeout",
                        book_id=book_id,
                        timeout=self.architecture_timeout,
                        error=error_msg)
            
            # Track API call failure
            api_duration = time.time() - api_start_time if 'api_start_time' in locals() else 0
            track_claude_api_call(book_id, 'architecture_generation', api_duration,
                                0, 'timeout', self.model)
            
            # Track generation completion with error
            track_generation_complete(book_id, book_params.get('user_id', 0), 'timeout',
                                    0, 0, 0, error_msg)
            
            self._handle_api_error(Exception(error_msg))
            
            from app.routes.websocket import emit_generation_log
            emit_generation_log(book_id, 'error', error_msg)
            
            raise Exception(error_msg)
            
        except (APIError, APIConnectionError, RateLimitError) as e:
            error_msg = f"Error de Claude API: {str(e)}"
            logger.error("claude_api_error",
                        book_id=book_id,
                        error_type=type(e).__name__,
                        error=str(e))
            
            # Track API call failure
            api_duration = time.time() - api_start_time if 'api_start_time' in locals() else 0
            track_claude_api_call(book_id, 'architecture_generation', api_duration,
                                0, f'api_error_{type(e).__name__}', self.model)
            
            # Track generation completion with error
            track_generation_complete(book_id, book_params.get('user_id', 0), 'api_error',
                                    0, 0, 0, error_msg)
            
            self._handle_api_error(e)
            
            from app.routes.websocket import emit_generation_log
            emit_generation_log(book_id, 'error', error_msg)
            
            raise Exception(error_msg)
            
        except Exception as e:
            error_msg = f"Error inesperado generando arquitectura: {str(e)}"
            logger.error("architecture_generation_error",
                        book_id=book_id,
                        error=str(e),
                        error_type=type(e).__name__)
            
            # Track API call failure
            api_duration = time.time() - api_start_time if 'api_start_time' in locals() else 0
            track_claude_api_call(book_id, 'architecture_generation', api_duration,
                                0, f'unexpected_error', self.model)
            
            # Track generation completion with error
            track_generation_complete(book_id, book_params.get('user_id', 0), 'error',
                                    0, 0, 0, error_msg)
            
            self._handle_api_error(e)
            
            from app.routes.websocket import emit_generation_log
            emit_generation_log(book_id, 'error', error_msg)
            
            raise Exception(error_msg)
    
    # =====================================
    # MÉTODOS DE GENERACIÓN DE ARQUITECTURA
    # =====================================
    
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

Your output must be a well-structured JSON with the following format (this is just an EXAMPLE - use the actual user configuration values):

```json
{
  "title": "[USE EXACT USER TITLE]",
  "summary": "Brief book description (2-3 sentences)",
  "target_pages": "[USE USER'S TARGET PAGES]",
  "estimated_words": "[CALCULATE BASED ON USER'S PAGE COUNT]",
  "genre": "[USE USER'S SELECTED GENRE]",
  "tone": "[USE USER'S SELECTED TONE]",
  "target_audience": "[USE USER'S SELECTED AUDIENCE]",
  "language": "[USE USER'S SELECTED LANGUAGE]",
  "page_size": "[USE USER'S SELECTED PAGE SIZE]",
  "line_spacing": "[USE USER'S SELECTED LINE SPACING]",
  "chapter_count": "[USE USER'S REQUESTED CHAPTER COUNT]",
  "writing_style": "[USE USER'S SELECTED WRITING STYLE]",
  "include_toc": "[USE USER'S TOC PREFERENCE]",
  "include_introduction": "[USE USER'S INTRODUCTION PREFERENCE]",
  "include_conclusion": "[USE USER'S CONCLUSION PREFERENCE]",
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
  ],
  "additional_instructions": "[INCLUDE USER'S ADDITIONAL INSTRUCTIONS IF PROVIDED]"
}
```

🚨 CRITICAL REQUIREMENTS:
- Use ALL the exact configuration values provided by the user (title, pages, genre, tone, audience, language, page size, line spacing, chapter count, writing style, etc.)
- DO NOT use the example values shown above - they are just placeholders
- ⚠️ **CRITICAL: Use EXACT field names as shown in the JSON schema above**:
  - For chapters: Use "number" (NOT "chapter_number") and "estimated_pages" (NOT "pages")
  - For introduction/conclusion: Use "estimated_pages" (NOT "pages")
  - These field names are MANDATORY for frontend compatibility
- Generate a detailed chapter-by-chapter breakdown
- Each chapter should have clear learning objectives and key points
- Estimate realistic page counts for each section that add up to the user's target
- Include characters (regardless of genre - they can be real people, case study subjects, examples, etc.)
- Suggest special sections (exercises, examples, etc.) if relevant to the genre and topic
- Make sure total estimated pages match the user's target
- Provide enough detail for user to understand the full book structure
- Respect all user preferences (TOC, introduction, conclusion, etc.)

DO NOT write any actual book content - only the detailed architecture and structure using the user's exact specifications."""

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
        
        # Obtener información de formato - IMPORTANTE: page_count ya viene calculado con el algoritmo de páginas efectivas
        page_size = book_params.get('page_size', book_params.get('format_size', 'pocket'))
        line_spacing = book_params.get('line_spacing', 'medium')
        page_count = book_params.get('page_count', 50)  # Este valor YA está calculado según el algoritmo (base × factores)
        
        # Calcular palabras aproximadas por página según formato (aumentado 1.5x para mayor contenido)
        words_per_page = {
            ('pocket', 'single'): 375,  ('pocket', 'medium'): 300,  ('pocket', 'double'): 225,
            ('A5', 'single'): 525,      ('A5', 'medium'): 420,      ('A5', 'double'): 315,
            ('B5', 'single'): 675,      ('B5', 'medium'): 540,      ('B5', 'double'): 405,
            ('letter', 'single'): 750,  ('letter', 'medium'): 600,  ('letter', 'double'): 450,
        }
        
        words_per_page_estimate = words_per_page.get((page_size, line_spacing), 400)
        total_words = page_count * words_per_page_estimate
        
        # Obtener parámetros adicionales del libro
        parameters = book_params.get('parameters', {})
        length_option = parameters.get('length', 'medium')  # short/medium/long
        
        return f"""🚨 CRITICAL: Create ONLY a detailed book ARCHITECTURE (structure/outline), NOT the actual book content!

**COMPLETE USER CONFIGURATION (use ALL these values in your JSON):**

📚 **BASIC INFORMATION:**
- Title: {book_params.get('title', 'Untitled Book')}
- Genre: {book_params.get('genre', 'General')}
- Target Audience: {book_params.get('target_audience', 'General audience')}
- Tone: {book_params.get('tone', 'Informative')}
- Writing Style: {book_params.get('writing_style', 'Professional and engaging')}
- Language: {language_name.upper()} (Code: {user_language})

📖 **BOOK STRUCTURE:**
- Length Option Selected: {length_option.upper()} (user selected this range)
- Target Pages (calculated): {page_count} pages
- Estimated Total Words: {total_words:,} words
- Number of Chapters: {book_params.get('chapter_count', 10)} chapters
- Page Size Format: {page_size}
- Line Spacing: {line_spacing}
- Include Table of Contents: {book_params.get('include_toc', True)}
- Include Introduction: {book_params.get('include_introduction', True)} 
- Include Conclusion: {book_params.get('include_conclusion', True)}

💡 **CONTENT SPECIFICATIONS:**
- Key Topics/Description: {book_params.get('key_topics', 'As relevant to the title')}
- Additional Instructions: {book_params.get('additional_instructions', 'None')}

⚠️ **CRITICAL ARCHITECTURE REQUIREMENTS:**
1. Generate ONLY the book architecture/structure - NO actual book content
2. Create a JSON with chapter titles, summaries, and structure - NOT the chapters themselves
3. Use ALL the configuration values exactly as provided above
4. The JSON must include: title, summary, target_pages ({page_count}), estimated_words ({total_words:,}), genre, tone, target_audience, language, page_size ({page_size}), line_spacing ({line_spacing}), chapter_count ({book_params.get('chapter_count', 10)}), writing_style, include_toc, include_introduction, include_conclusion
5. Create exactly {book_params.get('chapter_count', 10)} chapters in the structure
6. 🎯 **CRITICAL PAGE DISTRIBUTION**: The sum of ALL chapter pages + introduction pages + conclusion pages must EXACTLY equal {page_count} pages
7. All text in the architecture (titles, summaries, descriptions) must be in {language_name.upper()}

📊 **PAGE DISTRIBUTION GUIDANCE:**
- Total target: {page_count} pages (THIS IS MANDATORY)
- Introduction: 3-5% of total pages ({"2-3" if page_count < 100 else "3-5"} pages)
- Conclusion: 3-5% of total pages ({"2-3" if page_count < 100 else "3-5"} pages)  
- Chapters: Remaining pages distributed logically ({page_count - (3 if page_count < 100 else 5) - (3 if page_count < 100 else 5)} pages total for chapters)
- Average per chapter: ~{(page_count - (6 if page_count < 100 else 10)) // book_params.get('chapter_count', 10)} pages, but vary based on content complexity

🛑 **WHAT NOT TO DO:**
- Do NOT write actual chapter content
- Do NOT write paragraphs of book text
- Do NOT create the book itself
- ONLY create the structural outline/architecture in JSON format

Remember: You are creating a BLUEPRINT of the book, not writing the book itself.
- Structure should be appropriate for {book_params.get('genre', 'General')} genre
- Target a total of {book_params.get('page_count', 50)} pages
- Include {book_params.get('chapter_count', 10)} main chapters

Generate a comprehensive book architecture that the user can review, modify if needed, and approve before full content generation begins."""

    # =====================================
    # MÉTODOS UTILITARIOS Y VALIDACIÓN
    # =====================================
    
    
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

    # =====================================
    # MÉTODOS DE REGENERACIÓN DE ARQUITECTURA
    # =====================================
    
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
            regen_max_tokens = min(32000, self.max_tokens)  # Aumentado para arquitectura mejorada
            regen_budget_tokens = min(30000, self.thinking_budget)
            
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=regen_max_tokens,
                temperature=self.temperature,
                messages=messages,
                thinking={
                    "type": "enabled",
                    "budget_tokens": regen_budget_tokens
                },
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
                        'total_tokens': final_message.usage.input_tokens + final_message.usage.output_tokens + getattr(final_message.usage, 'thinking_tokens', 0)
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

    # =====================================
    # MÉTODOS DE SOPORTE PARA REGENERACIÓN DE ARQUITECTURA
    # =====================================
    
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

Your output must be a well-structured JSON with the same format as before, but improved based on the feedback.

⚠️ IMPORTANT: The following JSON is just an EXAMPLE TEMPLATE - DO NOT use these example values:

```json
{
  "title": "[KEEP ORIGINAL TITLE OR IMPROVE BASED ON FEEDBACK]",
  "summary": "[IMPROVED BOOK DESCRIPTION BASED ON FEEDBACK]",
  "target_pages": "[USE ACTUAL TARGET PAGES FROM USER CONFIG]",
  "estimated_words": "[CALCULATE BASED ON ACTUAL USER SPECIFICATIONS]",
  "genre": "[USE ACTUAL GENRE FROM USER CONFIG]",
  "tone": "[USE ORIGINAL TONE OR ADJUST IF FEEDBACK SUGGESTS]",
  "target_audience": "[USE ACTUAL AUDIENCE FROM USER CONFIG]",
  "language": "[USE ACTUAL LANGUAGE FROM USER CONFIG]",
  "page_size": "[USE ACTUAL PAGE SIZE FROM USER CONFIG]",
  "line_spacing": "[USE ACTUAL LINE SPACING FROM USER CONFIG]",
  "chapter_count": "[USE ACTUAL CHAPTER COUNT FROM USER CONFIG]",
  "writing_style": "[USE ACTUAL WRITING STYLE OR IMPROVE BASED ON FEEDBACK]",
  "include_toc": "[USE ACTUAL TOC PREFERENCE]",
  "include_introduction": "[USE ACTUAL INTRODUCTION PREFERENCE]",
  "include_conclusion": "[USE ACTUAL CONCLUSION PREFERENCE]",
  "writing_approach": "[DESCRIBE IMPROVED APPROACH BASED ON FEEDBACK]",
  "structure": {
    "introduction": {
      "title": "[ACTUAL INTRODUCTION TITLE - IMPROVE IF NEEDED]",
      "summary": "[IMPROVED INTRODUCTION OUTLINE BASED ON FEEDBACK]",
      "estimated_pages": "[REALISTIC PAGE ESTIMATE]"
    },
    "chapters": [
      {
        "number": 1,
        "title": "[IMPROVED CHAPTER TITLE BASED ON FEEDBACK]",
        "summary": "[ENHANCED CHAPTER SUMMARY ADDRESSING FEEDBACK]",
        "key_points": ["[ACTUAL IMPROVED POINTS BASED ON FEEDBACK]"],
        "estimated_pages": "[REALISTIC PAGE ESTIMATE]",
        "learning_objectives": ["[ENHANCED OBJECTIVES BASED ON FEEDBACK]"]
      }
    ],
    "conclusion": {
      "title": "[ACTUAL CONCLUSION TITLE]", 
      "summary": "[IMPROVED CONCLUSION OUTLINE]",
      "estimated_pages": "[REALISTIC PAGE ESTIMATE]"
    }
  },
  "characters": [
    {
      "name": "[ACTUAL CHARACTER NAME OR NEW BASED ON FEEDBACK]",
      "role": "[ENHANCED CHARACTER ROLE BASED ON FEEDBACK]",
      "description": "[IMPROVED CHARACTER DESCRIPTION]"
    }
  ],
  "key_themes": ["[ACTUAL ENHANCED THEMES BASED ON FEEDBACK]"],
  "special_sections": [
    {
      "type": "[ACTUAL SECTION TYPE BASED ON FEEDBACK]",
      "frequency": "[ACTUAL FREQUENCY]",
      "purpose": "[ACTUAL PURPOSE BASED ON FEEDBACK]"
    }
  ],
  "improvements_made": ["[LIST SPECIFIC IMPROVEMENTS YOU MADE BASED ON USER FEEDBACK]"],
  "feedback_addressed": true
}
```

🚨 CRITICAL REQUIREMENTS:
- The above JSON is ONLY an example template showing the structure
- DO NOT use any of the example values (150 pages, 45000 words, etc.)
- Use the ACTUAL configuration values from the user's book
- Use the ACTUAL current architecture as your starting point
- Incorporate ALL the user's specific feedback
- Make substantial improvements based on what the user requested
- ⚠️ **CRITICAL: Use EXACT field names as shown in the JSON schema above**:
  - For chapters: Use "number" (NOT "chapter_number") and "estimated_pages" (NOT "pages")
  - For introduction/conclusion: Use "estimated_pages" (NOT "pages")
  - These field names are MANDATORY for frontend compatibility

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
        
        # Obtener información de formato completa
        page_size = book_params.get('page_size', book_params.get('format_size', 'pocket'))
        line_spacing = book_params.get('line_spacing', 'medium')
        page_count = book_params.get('page_count', 50)
        
        # Calcular palabras aproximadas
        words_per_page = {
            ('pocket', 'single'): 375,  ('pocket', 'medium'): 300,  ('pocket', 'double'): 225,
            ('A5', 'single'): 525,      ('A5', 'medium'): 420,      ('A5', 'double'): 315,
            ('B5', 'single'): 675,      ('B5', 'medium'): 540,      ('B5', 'double'): 405,
            ('letter', 'single'): 750,  ('letter', 'medium'): 600,  ('letter', 'double'): 450,
        }
        words_per_page_estimate = words_per_page.get((page_size, line_spacing), 400)
        total_words = page_count * words_per_page_estimate
        
        return f"""Please regenerate the book architecture based on the user's specific feedback.

**📚 COMPLETE ORIGINAL BOOK SPECIFICATIONS:**
- Title: {book_params.get('title', 'Untitled Book')}
- Genre: {book_params.get('genre', 'General')}
- Target Audience: {book_params.get('target_audience', 'General audience')}
- Writing Style: {book_params.get('writing_style', 'Professional and engaging')}
- Tone: {book_params.get('tone', 'Informative')}
- Language: {language_name.upper()} (Code: {user_language})

**📖 FORMAT SPECIFICATIONS:**
- Page Size: {page_size.upper()} format
- Line Spacing: {line_spacing}
- Target Pages: {page_count} pages
- Estimated Words: {total_words:,} words
- Number of Chapters: {book_params.get('chapter_count', 10)}

**📋 STRUCTURE PREFERENCES:**
- Include Table of Contents: {book_params.get('include_toc', True)}
- Include Introduction: {book_params.get('include_introduction', True)}
- Include Conclusion: {book_params.get('include_conclusion', True)}

**💡 CONTENT FOCUS:**
- Key Topics: {book_params.get('key_topics', 'As relevant to the title')}
- Additional Instructions: {book_params.get('additional_instructions', 'None')}

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


    # =====================================
    # MÉTODOS DE REGENERACIÓN DE CAPÍTULOS
    # =====================================
    
    async def regenerate_chapter_content(self, chapter_content: str, feedback: Dict[str, str], book=None) -> Dict[str, Any]:
        """
        Regenera un capítulo específico basado en el feedback del usuario.
        
        Args:
            chapter_content: Contenido actual del capítulo
            feedback: Diccionario con whatDislike, whatChange, howWant
            book: Objeto del libro (opcional) para calcular palabras basado en arquitectura
            
        Returns:
            Dict con el nuevo contenido y métricas de uso
        """
        try:
            # Preparar el prompt para regeneración de capítulo
            messages = self._build_chapter_regeneration_messages(chapter_content, feedback, book)
            
            logger.info("starting_chapter_regeneration", 
                       content_length=len(chapter_content),
                       feedback_keys=list(feedback.keys()))
            
            # Llamar a Claude con configuración específica para regeneración
            system_prompt = self._build_chapter_regeneration_system_prompt()
            user_prompt = self._build_chapter_regeneration_user_prompt(chapter_content, feedback, book)
            
            # Para regeneración de capítulos, necesitamos más tokens para capítulos más extensos
            chapter_max_tokens = 32000  # Aumentado para capítulos muy extensos
            chapter_budget_tokens = min(30000, self.thinking_budget)  # Mantener relación correcta
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=chapter_max_tokens,  # Aumentado para contenido extenso
                temperature=0.7,  # Creatividad controlada
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }],
                thinking={
                    "type": "enabled",
                    "budget_tokens": chapter_budget_tokens  # Ahora < max_tokens
                },
            )
            
            # Extraer contenido y thinking
            content = ""
            thinking_content = ""
            
            for block in response.content:
                if hasattr(block, 'text'):
                    content += block.text
                elif hasattr(block, 'type') and block.type == 'thinking':
                    thinking_content += getattr(block, 'text', '')
            
            # Métricas de uso
            thinking_tokens = getattr(response.usage, 'thinking_tokens', 0) if hasattr(response, 'usage') else 0
            usage_info = {
                'prompt_tokens': response.usage.input_tokens if hasattr(response, 'usage') else 0,
                'completion_tokens': response.usage.output_tokens if hasattr(response, 'usage') else 0,
                'thinking_tokens': thinking_tokens,
                'total_tokens': (response.usage.input_tokens + response.usage.output_tokens + thinking_tokens) if hasattr(response, 'usage') else 0
            }
            
            logger.info("chapter_regeneration_completed",
                       new_content_length=len(content),
                       **usage_info)
            
            return {
                'content': content.strip(),
                'thinking': thinking_content,
                'usage': usage_info,
                'success': True
            }
            
        except Exception as e:
            logger.error("chapter_regeneration_failed", error=str(e))
            return {
                'content': '',
                'usage': {},
                'success': False,
                'error': str(e)
            }
    
    # =====================================
    # NUEVO: GENERACIÓN MULTI-CHUNKED CON CLAUDE SONNET 4
    # =====================================
    
    async def generate_book_from_architecture_multichunk(self, book_id: int, book_params: Dict[str, Any], approved_architecture: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera el contenido completo del libro usando generación multi-chunked con Claude Sonnet 4.
        Garantiza que se cumplan las páginas prometidas al usuario.
        
        Args:
            book_id: ID del libro
            book_params: Parámetros originales del libro
            approved_architecture: Arquitectura aprobada por el usuario
            
        Returns:
            Resultado de la generación con contenido completo
        """
        try:
            # Log crítico del inicio con Claude Sonnet 4
            logger.info("starting_multichunk_generation",
                       book_id=book_id,
                       model=self.model,
                       chapters_count=len(approved_architecture.get('structure', {}).get('chapters', [])),
                       target_pages=approved_architecture.get('target_pages'),
                       estimated_words=approved_architecture.get('estimated_words'),
                       max_tokens_per_chunk=self.max_tokens,
                       max_chunks=self.max_chunks)
            
            # Emisión de evento de inicio
            from app.routes.websocket import emit_book_progress_update, emit_generation_log
            
            emit_book_progress_update(book_id, {
                'current': 5,
                'total': 100,
                'status': 'initializing',
                'status_message': 'Iniciando generación multi-chunked con Claude Sonnet 4...',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # Dividir capítulos en chunks
            chapters = approved_architecture.get('structure', {}).get('chapters', [])
            total_chapters = len(chapters)
            
            if total_chapters == 0:
                raise Exception("No se encontraron capítulos en la arquitectura")
            
            # 🚀 OPTIMIZACIÓN: Chunks más grandes para reducir necesidad de continuación
            # Calcular chunks necesarios (máximo 15 capítulos por chunk, antes era 12)
            chapters_per_chunk = max(2, min(15, total_chapters // max(2, self.max_chunks - 1) + 1))
            chunks = []
            
            for i in range(0, total_chapters, chapters_per_chunk):
                chunk_chapters = chapters[i:i + chapters_per_chunk]
                chunks.append({
                    'index': len(chunks) + 1,
                    'chapters': chunk_chapters,
                    'start_chapter': i + 1,
                    'end_chapter': min(i + chapters_per_chunk, total_chapters)
                })
            
            logger.info("chunk_planning",
                       book_id=book_id,
                       total_chunks=len(chunks),
                       chapters_per_chunk=chapters_per_chunk,
                       total_chapters=total_chapters)
            
            # Variables de acumulación
            complete_book_content = []
            complete_thinking_content = []
            total_tokens_used = 0
            total_thinking_tokens = 0
            chunk_summaries = []
            
            # 🚨 SISTEMA DE COHERENCIA: Basado en arquitectura aprobada
            
            # 1. Extraer target real de la arquitectura
            target_pages = self.coherence_manager.extract_target_pages_from_architecture(
                approved_architecture, book_params
            )
            
            # 2. Validar y estructurar capítulos con páginas target
            structured_chapters = self.coherence_manager.validate_and_structure_chapters(
                approved_architecture, target_pages
            )
            
            # 3. Calcular distribución coherente por chunks
            chunk_distributions = self.coherence_manager.calculate_chunk_page_distribution(
                structured_chapters, target_pages
            )
            
            # 🚨 VALIDACIÓN CRÍTICA: Verificar que se generaron distribuciones de chunks
            if not chunk_distributions:
                raise Exception(f"No se pudieron generar distribuciones de chunks. Structured chapters: {len(structured_chapters)}, Target pages: {target_pages}")
            
            logger.info("coherence_system_initialized",
                       book_id=book_id,
                       target_pages=target_pages,
                       structured_chapters=len(structured_chapters),
                       planned_chunks=len(chunk_distributions))
            
            chunk_num = 0
            max_total_chunks = 4  # 🚀 OPTIMIZACIÓN: Reducido de 8 → 4 para evitar bucles largos
            generated_chapters = []  # Track capítulos generados
            
            # 📖 GENERAR INTRODUCCIÓN (si está configurada)
            emit_book_progress_update(book_id, {
                'current': 8,
                'total': 100,
                'status': 'generating_introduction',
                'status_message': 'Generando introducción personalizada del libro...',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            introduction_result = await self._generate_introduction(book_id, book_params, approved_architecture)
            if introduction_result['content']:
                complete_book_content.append(introduction_result['content'])
                complete_thinking_content.append(introduction_result['thinking'])
                total_tokens_used += introduction_result['usage']['total_tokens']
                total_thinking_tokens += introduction_result['usage']['thinking_tokens']
                
                emit_generation_log(book_id, 'success', 
                    f'✅ Introducción generada: {len(introduction_result["content"].split())} palabras')
            
            # 🚀 PARALELIZACIÓN DE CHUNKS - OPTIMIZACIÓN MÁXIMO IMPACTO
            # Reducir de 45-60 min (secuencial) → 15-20 min (paralelo)
            
            emit_book_progress_update(book_id, {
                'current': 15,
                'total': 100,
                'status': 'preparing_parallel_generation',
                'status_message': f'🚀 Preparando generación paralela de {len(chunk_distributions)} chunks principales...',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # Preparar tareas paralelas para chunks principales
            chunk_tasks = []
            for chunk_idx, chunk_distribution in enumerate(chunk_distributions):
                chunk_num = chunk_idx + 1
                
                # Preparar chunk info con distribución coherente
                coherent_chunk_info = {
                    'index': chunk_num,
                    'chapters': chunk_distribution['chapters'],
                    'target_pages': chunk_distribution['target_pages'],
                    'target_words': chunk_distribution['target_words'],
                    'start_chapter': chunk_distribution['start_chapter'],
                    'end_chapter': chunk_distribution['end_chapter']
                }
                
                # Crear tarea para generación paralela
                task = self._generate_chunk_parallel(
                    book_id=book_id,
                    chunk_info=coherent_chunk_info,
                    book_params=book_params,
                    approved_architecture=approved_architecture,
                    introduction_content=complete_book_content[0] if complete_book_content else "",
                    chunk_idx=chunk_idx
                )
                chunk_tasks.append(task)
            
            # 🚀 EJECUTAR CHUNKS EN PARALELO - MÁXIMA OPTIMIZACIÓN
            emit_book_progress_update(book_id, {
                'current': 20,
                'total': 100,
                'status': 'generating_parallel_chunks',
                'status_message': f'🚀 Generando {len(chunk_distributions)} chunks principales EN PARALELO...',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            emit_generation_log(book_id, 'info', 
                f'🚀 PARALELIZACIÓN ACTIVA: Generando {len(chunk_distributions)} chunks simultáneamente')
            
            # Esperar todos los chunks en paralelo
            chunk_results = await asyncio.gather(*chunk_tasks, return_exceptions=True)
            
            # 🚀 PROCESAMIENTO OPTIMIZADO: Sin validaciones costosas intermedias
            emit_generation_log(book_id, 'success', 
                f'✅ Paralelización completada: {len(chunk_results)} chunks generados simultáneamente')
            
            # Procesar resultados paralelos manteniendo orden correcto
            for idx, chunk_result in enumerate(chunk_results):
                if isinstance(chunk_result, Exception):
                    emit_generation_log(book_id, 'error', 
                        f'❌ Error en chunk paralelo {idx + 1}: {str(chunk_result)}')
                    raise chunk_result
                
                # Acumular resultados directamente (sin validaciones costosas)
                complete_book_content.append(chunk_result['content'])
                complete_thinking_content.append(chunk_result['thinking'])
                total_tokens_used += chunk_result['usage']['total_tokens']
                total_thinking_tokens += chunk_result['usage']['thinking_tokens']
                
                emit_generation_log(book_id, 'success', 
                    f'✅ Chunk {idx + 1} integrado: {len(chunk_result["content"].split())} palabras')
            
            # 🚀 OPTIMIZACIÓN: Progreso consolidado tras paralelización
            emit_book_progress_update(book_id, {
                'current': 70,
                'total': 100,
                'status': 'parallel_chunks_completed',
                'status_message': f'Chunks principales completados en paralelo - Evaluando contenido...',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # 🚀 ELIMINACIÓN TOTAL DEL BUCLE WHILE - ESTRATEGIA PREDETERMINISTA
            # Calcular si necesitamos chunks adicionales basado en déficit actual
            current_content = '\n\n'.join(complete_book_content)
            current_words = len(current_content.split())
            current_pages = current_words // 350
            pages_ratio = current_pages / target_pages if target_pages > 0 else 1
            
            emit_generation_log(book_id, 'info', 
                f'📊 Evaluación inicial: {current_pages}/{target_pages} páginas ({pages_ratio:.1%})')
            
            # 🎯 ESTRATEGIA DETERMINÍSTICA: Máximo 1 chunk adicional si es absolutamente necesario
            additional_chunks_needed = 0
            if pages_ratio < 0.70:  # Solo si tenemos menos del 70%
                pages_deficit = target_pages - current_pages
                additional_chunks_needed = 1 if pages_deficit > 15 else 0  # Solo 1 chunk extra máximo
                
                emit_generation_log(book_id, 'info', 
                    f'📈 Déficit detectado: {pages_deficit} páginas faltantes - Generando 1 chunk adicional')
            else:
                emit_generation_log(book_id, 'success', 
                    f'✅ Target suficiente alcanzado: {current_pages} páginas ({pages_ratio:.1%}) - Sin chunks adicionales')
            
            # Generar chunk adicional SOLO si es absolutamente necesario
            if additional_chunks_needed > 0 and chunk_num < max_total_chunks:
                
                # Generar estrategia de continuación inteligente
                continuation_strategy = self.coherence_manager.generate_continuation_strategy(
                    current_pages, target_pages, generated_chapters
                )
                
                # Generar chunk de continuación
                chunk_num += 1
                progress_base = 70 + ((chunk_num - len(chunk_distributions)) * 20 // (max_total_chunks - len(chunk_distributions)))
                
                emit_book_progress_update(book_id, {
                    'current': progress_base,
                    'total': 100,
                    'status': 'extending_content',
                    'status_message': f'Estrategia: {continuation_strategy["type"]} - Chunk {chunk_num} ({continuation_strategy["pages_deficit"]} páginas faltantes)...',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                
                # Crear chunk de continuación inteligente
                continuation_chunk = {
                    'index': chunk_num,
                    'chapters': [],
                    'start_chapter': 'continuación',
                    'end_chapter': 'continuación',
                    'is_continuation': True,
                    'continuation_strategy': continuation_strategy,
                    'target_pages_remaining': continuation_strategy['pages_deficit'],
                    'target_words_remaining': continuation_strategy['target_words'],
                    'generated_chapters': generated_chapters.copy()
                }
                
                emit_generation_log(book_id, 'info', 
                    f'🔄 Continuación {chunk_num}: {continuation_strategy["strategy"]}')
                
                # Generar contenido de continuación
                chunk_result = await self._generate_single_chunk(
                    book_id=book_id,
                    chunk_info=continuation_chunk,
                    book_params=book_params,
                    approved_architecture=approved_architecture,
                    previous_content=current_content,
                    chunk_summaries=chunk_summaries,
                    progress_base=progress_base
                )
                
                # Acumular resultados
                complete_book_content.append(chunk_result['content'])
                complete_thinking_content.append(chunk_result['thinking'])
                total_tokens_used += chunk_result['usage']['total_tokens']
                total_thinking_tokens += chunk_result['usage']['thinking_tokens']
                
                # Guardar resumen para contexto
                chunk_summaries.append({
                    'chunk_number': chunk_num,
                    'chapters': 'continuación',
                    'word_count': len(chunk_result['content'].split()),
                    'summary': chunk_result['content'][:500] + "..." if len(chunk_result['content']) > 500 else chunk_result['content']
                })
                
                # Verificar progreso
                new_content = '\n\n'.join(complete_book_content)
                new_words = len(new_content.split())
                new_pages = new_words // 350
                words_added = new_words - current_words
                
                emit_generation_log(book_id, 'success', 
                    f'✅ Chunk adicional único completado - +{words_added} palabras | Total: {new_pages}/{target_pages} páginas')
            else:
                emit_generation_log(book_id, 'info', 
                    f'🚀 OPTIMIZACIÓN: Bucle while eliminado - Sin chunks adicionales necesarios')
            
            # Combinar todo el contenido
            final_content = '\n\n'.join(complete_book_content)
            final_thinking = '\n\n---CHUNK SEPARATOR---\n\n'.join(complete_thinking_content)
            
            # Calcular métricas finales
            final_words = len(final_content.split())
            final_pages = final_words // 350  # ~350 words per page
            final_chapters = final_content.count('##')  # Contar headers de capítulos
            
            # Validar cumplimiento de páginas prometidas
            requested_pages = approved_architecture.get('target_pages', book_params.get('page_count', 50))
            pages_ratio = final_pages / requested_pages if requested_pages > 0 else 1
            
            if pages_ratio < 0.95:  # Si faltan más del 5%
                deficit_percentage = ((requested_pages - final_pages) / requested_pages) * 100
                logger.warning("multichunk_book_below_target",
                             book_id=book_id,
                             requested_pages=requested_pages,
                             actual_pages=final_pages,
                             deficit_percentage=deficit_percentage,
                             chunks_generated=chunk_num)
                
                emit_generation_log(book_id, 'warning', 
                    f'⚠️ Se generaron {final_pages} páginas de las {requested_pages} solicitadas ({deficit_percentage:.1f}% menos)')
            else:
                emit_generation_log(book_id, 'success', 
                    f'✅ Objetivo cumplido: {final_pages} páginas generadas (solicitadas: {requested_pages})')
            
            # 📖 GENERAR CONCLUSIÓN (si está configurada)
            emit_book_progress_update(book_id, {
                'current': 92,
                'total': 100,
                'status': 'generating_conclusion',
                'status_message': 'Generando conclusión personalizada del libro...',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            conclusion_result = await self._generate_conclusion(book_id, book_params, approved_architecture, final_content)
            if conclusion_result['content']:
                complete_book_content.append(conclusion_result['content'])
                complete_thinking_content.append(conclusion_result['thinking'])
                total_tokens_used += conclusion_result['usage']['total_tokens']
                total_thinking_tokens += conclusion_result['usage']['thinking_tokens']
                
                # Recalcular contenido final con conclusión
                final_content = '\n\n'.join(complete_book_content)
                final_thinking = '\n\n---CHUNK SEPARATOR---\n\n'.join(complete_thinking_content)
                final_words = len(final_content.split())
                final_pages = final_words // 350
            
            # Progreso final
            emit_book_progress_update(book_id, {
                'current': 98,
                'total': 100,
                'status': 'finalizing',
                'status_message': f'Libro completado: {final_pages} páginas, {final_words:,} palabras',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # Resultado final
            return {
                'content': final_content,
                'thinking': final_thinking,
                'usage': {
                    'prompt_tokens': total_tokens_used - total_thinking_tokens,  # Aproximado
                    'completion_tokens': total_tokens_used - total_thinking_tokens,  # Tokens de contenido
                    'thinking_tokens': total_thinking_tokens,
                    'total_tokens': total_tokens_used
                },
                'model': self.model,
                'chunks_generated': chunk_num,  # Usar chunk_num real, no len(chunks) planeado
                'chunk_summaries': chunk_summaries,
                'final_stats': {
                    'pages': final_pages,
                    'words': final_words,
                    'chapters': final_chapters,
                    'pages_ratio': pages_ratio,
                    'target_pages': requested_pages
                }
            }
            
        except Exception as e:
            logger.error("multichunk_generation_error", 
                        book_id=book_id, 
                        error=str(e),
                        model=self.model)
            raise
    
    async def _generate_single_chunk(self, book_id: int, chunk_info: Dict, book_params: Dict[str, Any], 
                                   approved_architecture: Dict[str, Any], previous_content: str, 
                                   chunk_summaries: List[Dict], progress_base: int) -> Dict[str, Any]:
        """
        Genera un único chunk del libro con continuidad del anterior.
        """
        try:
            # Preparar prompt específico para este chunk
            messages = self._build_chunk_messages(
                chunk_info, book_params, approved_architecture, 
                previous_content, chunk_summaries
            )
            
            # Variables de acumulación para este chunk
            chunk_content = []
            chunk_thinking = []
            chunk_tokens = 0
            thinking_tokens = 0
            current_block_index = None
            
            from app.routes.websocket import emit_book_progress_update, emit_generation_log
            
            emit_book_progress_update(book_id, {
                'current': progress_base + 5,
                'total': 100,
                'status': 'thinking',
                'status_message': f'Claude Sonnet 4 analizando chunk {chunk_info["index"]}...',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # 🚀 OPTIMIZACIÓN: Generar con tokens optimizados para chunks principales
            chunk_max_tokens = self._get_optimized_tokens('chunk_main')  # 28000 optimizado
            chunk_thinking_budget = self._get_optimized_thinking_budget('chunk_main')  # Optimizado
            
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=chunk_max_tokens,
                temperature=self.temperature,
                messages=messages,
                thinking={
                    "type": "enabled",
                    "budget_tokens": chunk_thinking_budget
                }
            ) as stream:
                
                async for event in stream:
                    # Thinking blocks
                    if event.type == "content_block_start" and event.content_block.type == "thinking":
                        current_block_index = event.index
                        emit_book_progress_update(book_id, {
                            'current': progress_base + 10,
                            'total': 100,
                            'status': 'deep_thinking',
                            'status_message': f'Análisis profundo chunk {chunk_info["index"]} - Pensamiento extendido activo...',
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        })
                    
                    elif event.type == "content_block_delta" and hasattr(event, 'delta'):
                        if hasattr(event.delta, 'text'):
                            text_chunk = event.delta.text
                            
                            # Si es thinking content
                            if current_block_index is not None and event.index == current_block_index:
                                chunk_thinking.append(text_chunk)
                                thinking_tokens += len(text_chunk.split())
                            else:
                                # Content principal
                                chunk_content.append(text_chunk)
                                chunk_tokens += len(text_chunk.split())
                                
                                # Update progress
                                if len(chunk_content) % 50 == 0:
                                    current_words = len(''.join(chunk_content).split())
                                    emit_book_progress_update(book_id, {
                                        'current': progress_base + 15 + min(50, (len(chunk_content) // 10)),
                                        'total': 100,
                                        'status': 'writing',
                                        'status_message': f'Escribiendo chunk {chunk_info["index"]} - {current_words} palabras...',
                                        'timestamp': datetime.now(timezone.utc).isoformat()
                                    })
                    
                    elif event.type == "content_block_stop":
                        if current_block_index == event.index:
                            # Fin del thinking
                            current_block_index = None
                            full_thinking = ''.join(chunk_thinking)
                            emit_generation_log(book_id, 'thinking', 
                                f'Chunk {chunk_info["index"]} - Planificación: {len(full_thinking.split())} palabras de pensamiento')
                
                # Obtener métricas finales del stream
                final_message = await stream.get_final_message()
                if hasattr(final_message, 'usage'):
                    chunk_tokens = final_message.usage.input_tokens + final_message.usage.output_tokens
                    thinking_tokens = getattr(final_message.usage, 'thinking_tokens', 0)
            
            final_chunk_content = ''.join(chunk_content)
            final_chunk_thinking = ''.join(chunk_thinking)
            
            emit_generation_log(book_id, 'success', 
                f'Chunk {chunk_info["index"]} generado: {len(final_chunk_content.split())} palabras, {thinking_tokens} thinking tokens')
            
            return {
                'content': final_chunk_content,
                'thinking': final_chunk_thinking,
                'usage': {
                    'total_tokens': chunk_tokens,
                    'thinking_tokens': thinking_tokens,
                    'output_tokens': len(final_chunk_content.split()),
                    'chunk_info': chunk_info
                }
            }
            
        except Exception as e:
            logger.error("chunk_generation_error", 
                        book_id=book_id, 
                        chunk_index=chunk_info.get('index', 'unknown'),
                        error=str(e))
            raise
    
    async def _generate_introduction(self, book_id: int, book_params: Dict[str, Any], 
                                   approved_architecture: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera la introducción específica del libro basada en la arquitectura aprobada.
        """
        try:
            introduction_info = approved_architecture.get('structure', {}).get('introduction', {})
            
            if not introduction_info or not book_params.get('include_introduction', True):
                return {'content': '', 'thinking': '', 'usage': {'total_tokens': 0}}
            
            language_map = {'es': 'Spanish', 'en': 'English', 'pt': 'Portuguese', 'fr': 'French'}
            language_name = language_map.get(book_params.get('language', 'es'), 'Spanish')
            
            # Calcular palabras precisas para introducción
            page_size = book_params.get('page_size', approved_architecture.get('page_size', 'pocket'))
            line_spacing = book_params.get('line_spacing', approved_architecture.get('line_spacing', 'medium'))
            words_per_page_matrix = {
                ('pocket', 'single'): 300, ('pocket', 'medium'): 240, ('pocket', 'double'): 180,
                ('A5', 'single'): 400, ('A5', 'medium'): 320, ('A5', 'double'): 240,
                ('B5', 'single'): 500, ('B5', 'medium'): 400, ('B5', 'double'): 300,
                ('letter', 'single'): 600, ('letter', 'medium'): 480, ('letter', 'double'): 360,
            }
            words_per_page = words_per_page_matrix.get((page_size, line_spacing), 240)
            intro_pages = introduction_info.get('pages', introduction_info.get('estimated_pages', 3))
            intro_words = intro_pages * words_per_page
            
            prompt = f"""
**GENERACIÓN DE INTRODUCCIÓN PROFESIONAL**

Escribe la introducción completa para este libro siguiendo exactamente la arquitectura aprobada.

**📚 INFORMACIÓN DEL LIBRO:**
- Título: {book_params.get('title', approved_architecture.get('title', 'Sin título'))}
- Descripción: {approved_architecture.get('summary', 'Descripción del libro')}
- Género: {book_params.get('genre', approved_architecture.get('genre', 'General'))}
- Audiencia: {book_params.get('target_audience', approved_architecture.get('target_audience', 'General'))}
- Tono: {book_params.get('tone', approved_architecture.get('tone', 'Profesional'))}
- Estilo: {book_params.get('writing_style', approved_architecture.get('writing_style', 'Professional and engaging'))}

**📝 INTRODUCCIÓN A GENERAR:**
- Título: {introduction_info.get('title', 'Introducción')}
- Resumen: {introduction_info.get('summary', 'Introducción al tema del libro')}
- Páginas target: {intro_pages}
- Palabras target: {intro_words:,} (formato {page_size}/{line_spacing})

**🎯 INSTRUCCIONES ESPECÍFICAS:**
1. Escribe en {language_name.upper()} exclusivamente
2. Mantén el tono {book_params.get('tone', 'profesional').upper()} y estilo "{book_params.get('writing_style', 'Professional and engaging')}"
3. Adapta para audiencia {book_params.get('target_audience', 'general')}
4. Genera exactamente {intro_words:,} palabras de contenido valioso
5. Incluye: presentación del tema, importancia, qué aprenderá el lector, estructura del libro
6. Conecta directamente con el primer capítulo

Genera la introducción completa ahora:
"""

            messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
            
            intro_content = []
            intro_thinking = []
            current_block_index = None
            
            from app.routes.websocket import emit_generation_log
            emit_generation_log(book_id, 'info', 'Generando introducción personalizada...')
            
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=self._get_optimized_tokens('introduction'),  # 🚀 8000 optimizado para introducción
                temperature=self.temperature,
                messages=messages,
                thinking={"type": "enabled", "budget_tokens": self.thinking_budget // 4}
            ) as stream:
                
                async for event in stream:
                    if event.type == "content_block_start" and event.content_block.type == "thinking":
                        current_block_index = event.index
                    elif event.type == "content_block_delta" and hasattr(event, 'delta'):
                        if hasattr(event.delta, 'text'):
                            text_chunk = event.delta.text
                            if current_block_index is not None and event.index == current_block_index:
                                intro_thinking.append(text_chunk)
                            else:
                                intro_content.append(text_chunk)
                    elif event.type == "content_block_stop":
                        if current_block_index == event.index:
                            current_block_index = None
                
                final_message = await stream.get_final_message()
            
            final_intro_content = ''.join(intro_content)
            final_intro_thinking = ''.join(intro_thinking)
            
            emit_generation_log(book_id, 'success', f'Introducción generada: {len(final_intro_content.split())} palabras')
            
            return {
                'content': final_intro_content,
                'thinking': final_intro_thinking,
                'usage': {
                    'total_tokens': final_message.usage.input_tokens + final_message.usage.output_tokens if hasattr(final_message, 'usage') else 0,
                    'thinking_tokens': getattr(final_message.usage, 'thinking_tokens', 0) if hasattr(final_message, 'usage') else 0
                }
            }
            
        except Exception as e:
            logger.error("introduction_generation_error", book_id=book_id, error=str(e))
            return {'content': '', 'thinking': '', 'usage': {'total_tokens': 0}}
    
    async def _generate_conclusion(self, book_id: int, book_params: Dict[str, Any], 
                                 approved_architecture: Dict[str, Any], complete_content: str) -> Dict[str, Any]:
        """
        Genera la conclusión específica del libro basada en la arquitectura aprobada y el contenido generado.
        """
        try:
            conclusion_info = approved_architecture.get('structure', {}).get('conclusion', {})
            
            if not conclusion_info or not book_params.get('include_conclusion', True):
                return {'content': '', 'thinking': '', 'usage': {'total_tokens': 0}}
            
            language_map = {'es': 'Spanish', 'en': 'English', 'pt': 'Portuguese', 'fr': 'French'}
            language_name = language_map.get(book_params.get('language', 'es'), 'Spanish')
            
            # Calcular palabras precisas para conclusión
            page_size = book_params.get('page_size', approved_architecture.get('page_size', 'pocket'))
            line_spacing = book_params.get('line_spacing', approved_architecture.get('line_spacing', 'medium'))
            words_per_page_matrix = {
                ('pocket', 'single'): 300, ('pocket', 'medium'): 240, ('pocket', 'double'): 180,
                ('A5', 'single'): 400, ('A5', 'medium'): 320, ('A5', 'double'): 240,
                ('B5', 'single'): 500, ('B5', 'medium'): 400, ('B5', 'double'): 300,
                ('letter', 'single'): 600, ('letter', 'medium'): 480, ('letter', 'double'): 360,
            }
            words_per_page = words_per_page_matrix.get((page_size, line_spacing), 240)
            conclusion_pages = conclusion_info.get('pages', conclusion_info.get('estimated_pages', 3))
            conclusion_words = conclusion_pages * words_per_page
            
            # Usar últimos 2000 caracteres del contenido para contexto
            content_context = complete_content[-2000:] if complete_content else ""
            
            prompt = f"""
**GENERACIÓN DE CONCLUSIÓN PROFESIONAL**

Escribe la conclusión completa para este libro siguiendo exactamente la arquitectura aprobada y sintetizando el contenido generado.

**📚 INFORMACIÓN DEL LIBRO:**
- Título: {book_params.get('title', approved_architecture.get('title', 'Sin título'))}
- Descripción: {approved_architecture.get('summary', 'Descripción del libro')}
- Género: {book_params.get('genre', approved_architecture.get('genre', 'General'))}
- Audiencia: {book_params.get('target_audience', approved_architecture.get('target_audience', 'General'))}
- Tono: {book_params.get('tone', approved_architecture.get('tone', 'Profesional'))}
- Estilo: {book_params.get('writing_style', approved_architecture.get('writing_style', 'Professional and engaging'))}

**📝 CONCLUSIÓN A GENERAR:**
- Título: {conclusion_info.get('title', 'Conclusión')}
- Resumen: {conclusion_info.get('summary', 'Resumen y reflexiones finales')}
- Páginas target: {conclusion_pages}
- Palabras target: {conclusion_words:,} (formato {page_size}/{line_spacing})

**📖 CONTEXTO DEL CONTENIDO FINAL:**
```
{content_context}
```

**🎯 INSTRUCCIONES ESPECÍFICAS:**
1. Escribe en {language_name.upper()} exclusivamente
2. Mantén el tono {book_params.get('tone', 'profesional').upper()} y estilo "{book_params.get('writing_style', 'Professional and engaging')}"
3. Adapta para audiencia {book_params.get('target_audience', 'general')}
4. Genera exactamente {conclusion_words:,} palabras de contenido valioso
5. Sintetiza los puntos clave del libro completo
6. Incluye: resumen de aprendizajes, reflexiones finales, próximos pasos
7. Cierra de manera inspiradora y coherente con todo el contenido

Genera la conclusión completa ahora:
"""

            messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
            
            conclusion_content = []
            conclusion_thinking = []
            current_block_index = None
            
            from app.routes.websocket import emit_generation_log
            emit_generation_log(book_id, 'info', 'Generando conclusión personalizada...')
            
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens // 4,  # Menos tokens para conclusión
                temperature=self.temperature,
                messages=messages,
                thinking={"type": "enabled", "budget_tokens": self.thinking_budget // 4}
            ) as stream:
                
                async for event in stream:
                    if event.type == "content_block_start" and event.content_block.type == "thinking":
                        current_block_index = event.index
                    elif event.type == "content_block_delta" and hasattr(event, 'delta'):
                        if hasattr(event.delta, 'text'):
                            text_chunk = event.delta.text
                            if current_block_index is not None and event.index == current_block_index:
                                conclusion_thinking.append(text_chunk)
                            else:
                                conclusion_content.append(text_chunk)
                    elif event.type == "content_block_stop":
                        if current_block_index == event.index:
                            current_block_index = None
                
                final_message = await stream.get_final_message()
            
            final_conclusion_content = ''.join(conclusion_content)
            final_conclusion_thinking = ''.join(conclusion_thinking)
            
            emit_generation_log(book_id, 'success', f'Conclusión generada: {len(final_conclusion_content.split())} palabras')
            
            return {
                'content': final_conclusion_content,
                'thinking': final_conclusion_thinking,
                'usage': {
                    'total_tokens': final_message.usage.input_tokens + final_message.usage.output_tokens if hasattr(final_message, 'usage') else 0,
                    'thinking_tokens': getattr(final_message.usage, 'thinking_tokens', 0) if hasattr(final_message, 'usage') else 0
                }
            }
            
        except Exception as e:
            logger.error("conclusion_generation_error", book_id=book_id, error=str(e))
            return {'content': '', 'thinking': '', 'usage': {'total_tokens': 0}}
    
    def _build_chunk_messages(self, chunk_info: Dict, book_params: Dict[str, Any], 
                            approved_architecture: Dict[str, Any], previous_content: str, 
                            chunk_summaries: List[Dict]) -> List[Dict[str, Any]]:
        """
        Construye los mensajes para generar un chunk específico manteniendo continuidad.
        """
        language_map = {
            'es': 'Spanish',
            'en': 'English', 
            'pt': 'Portuguese',
            'fr': 'French'
        }
        
        user_language = book_params.get('language', 'es')
        language_name = language_map.get(user_language, user_language)
        
        # Construir contexto de continuidad
        continuity_context = ""
        if previous_content:
            # Últimos 1000 caracteres para continuidad
            continuity_context = f"""
**CONTENIDO PREVIO (para continuidad):**
```
{previous_content[-1000:]}
```

**RESÚMENES DE CHUNKS ANTERIORES:**
{chr(10).join([f"Chunk {s['chunk_number']} (Cap {s['chapters']}): {s['word_count']} palabras - {s['summary'][:200]}..." for s in chunk_summaries])}
"""
        
        # Capítulos a generar en este chunk
        chapters_to_generate = ""
        
        # 🚨 MANEJO INTELIGENTE DE CHUNKS DE CONTINUACIÓN
        if chunk_info.get('is_continuation', False):
            continuation_strategy = chunk_info.get('continuation_strategy', {})
            strategy_type = continuation_strategy.get('type', 'expand_existing')
            target_pages_remaining = chunk_info.get('target_pages_remaining', 50)
            target_words_remaining = chunk_info.get('target_words_remaining', 17500)
            generated_chapters = chunk_info.get('generated_chapters', [])
            
            if strategy_type == 'expand_existing':
                strategy_prompt = f"""
**🔄 EXPANSIÓN DE CONTENIDO EXISTENTE**
- Expandir capítulos ya generados con contenido adicional detallado
- Agregar subsecciones, ejemplos prácticos más profundos, casos de estudio
- Incluir ejercicios adicionales, FAQ, troubleshooting
- NO crear nuevos capítulos, solo EXPANDIR los existentes
"""
            elif strategy_type == 'add_sections':
                strategy_prompt = f"""
**🔄 AGREGAR SECCIONES ESPECIALES**
- Crear secciones complementarias: Apéndices, Glosario, Recursos adicionales
- Casos de estudio reales detallados, proyectos prácticos completos
- Sección de mejores prácticas, patrones comunes, anti-patrones
- Referencias bibliográficas expandidas, lecturas recomendadas
"""
            else:  # add_chapters
                strategy_prompt = f"""
**🔄 AGREGAR CAPÍTULOS ADICIONALES**
- Crear nuevos capítulos que complementen los existentes
- Temas avanzados, casos de uso especializados
- Capítulos de implementación práctica, proyectos completos
- Conclusiones expandidas, roadmap futuro, recursos adicionales
"""
            
            chapters_to_generate = f"""
{strategy_prompt}

**CONTEXTO DE CONTINUACIÓN:**
- Páginas restantes necesarias: {target_pages_remaining}
- Palabras aproximadas a generar: {target_words_remaining:,}
- Capítulos ya generados: {', '.join(generated_chapters[:5])}{'...' if len(generated_chapters) > 5 else ''}
- CRÍTICO: NO repetir contenido ya generado
- ENFOQUE: {continuation_strategy.get('strategy', 'Expandir contenido existente')}
"""
        else:
            # Chunk normal con capítulos específicos de la arquitectura
            total_chunk_pages = chunk_info.get('target_pages', 0)
            
            chapters_to_generate += f"""
**📋 CHUNK PLANIFICADO - {total_chunk_pages} PÁGINAS TARGET**

"""
            # Calcular palabras precisas por página basado en formato
            page_size = book_params.get('page_size', approved_architecture.get('page_size', 'pocket'))
            line_spacing = book_params.get('line_spacing', approved_architecture.get('line_spacing', 'medium'))
            
            # Palabras por página específicas por formato (más precisas)
            words_per_page_matrix = {
                ('pocket', 'single'): 300, ('pocket', 'medium'): 240, ('pocket', 'double'): 180,
                ('A5', 'single'): 400, ('A5', 'medium'): 320, ('A5', 'double'): 240,
                ('B5', 'single'): 500, ('B5', 'medium'): 400, ('B5', 'double'): 300,
                ('letter', 'single'): 600, ('letter', 'medium'): 480, ('letter', 'double'): 360,
            }
            words_per_page = words_per_page_matrix.get((page_size, line_spacing), 240)
            
            for i, chapter in enumerate(chunk_info['chapters']):
                chapter_pages = chapter.get('estimated_pages', chapter.get('pages', 0))
                chapter_words = chapter_pages * words_per_page
                chapters_to_generate += f"""
**CAPÍTULO {chapter.get('number', chapter.get('chapter_number', chunk_info['start_chapter'] + i))}: {chapter.get('title', f'Capítulo {chunk_info["start_chapter"] + i}')}**
- Resumen: {chapter.get('summary', 'Contenido del capítulo')}
- Puntos clave: {', '.join(chapter.get('key_points', []))}
- Objetivos de aprendizaje: {', '.join(chapter.get('learning_objectives', []))}
- 🎯 PÁGINAS TARGET PARA ESTE CAPÍTULO: {chapter_pages}
- 📝 PALABRAS PRECISAS TARGET: {chapter_words:,} (basado en formato {page_size}/{line_spacing})
"""
        
        # Tipo de chunk para instrucciones específicas
        chunk_type = "DE CONTINUACIÓN" if chunk_info.get('is_continuation', False) else "PLANIFICADO"
        
        user_prompt = f"""
**CLAUDE SONNET 4 - GENERACIÓN MULTI-CHUNKED DE ALTA CALIDAD**

Estás generando el CHUNK {chunk_type} {chunk_info['index']} de un libro. Debes mantener PERFECTA CONTINUIDAD y MÁXIMA CALIDAD.

{continuity_context}

**📚 INFORMACIÓN COMPLETA DEL LIBRO:**
- Título: {book_params.get('title', approved_architecture.get('title', 'Sin título'))}
- Descripción general: {approved_architecture.get('summary', 'Descripción del libro')}
- Género: {book_params.get('genre', approved_architecture.get('genre', 'General'))}
- Idioma: {language_name.upper()}
- Audiencia objetivo: {book_params.get('target_audience', approved_architecture.get('target_audience', 'General'))}
- Tono requerido: {book_params.get('tone', approved_architecture.get('tone', 'Profesional'))}
- Estilo de escritura: {book_params.get('writing_style', approved_architecture.get('writing_style', 'Professional and engaging'))}

**📖 ESTRUCTURA COMPLETA DEL LIBRO (para evitar duplicación):**
{self._build_complete_book_structure(approved_architecture)}

**📖 ESPECIFICACIONES DE FORMATO:**
- Formato de página: {book_params.get('page_size', approved_architecture.get('page_size', 'pocket'))}
- Interlineado: {book_params.get('line_spacing', approved_architecture.get('line_spacing', 'medium'))}
- Target páginas total: {approved_architecture.get('target_pages', 'No especificado')}
- Target palabras total: {approved_architecture.get('estimated_words', 'No especificado'):,}
- Include TOC: {book_params.get('include_toc', approved_architecture.get('include_toc', True))}
- Include Introduction: {book_params.get('include_introduction', approved_architecture.get('include_introduction', True))}
- Include Conclusion: {book_params.get('include_conclusion', approved_architecture.get('include_conclusion', True))}

**📝 CONTENIDO A GENERAR:**
{chapters_to_generate}

**🎯 INSTRUCCIONES CRÍTICAS DE CALIDAD:**
1. **IDIOMA**: Escribe en {language_name.upper()} exclusivamente
2. **GÉNERO**: Adapta el contenido específicamente al género {book_params.get('genre', approved_architecture.get('genre', 'General')).upper()} - usa técnicas, estructura y enfoque apropiados
3. **ESTILO DE ESCRITURA**: Sigue estrictamente el estilo "{book_params.get('writing_style', approved_architecture.get('writing_style', 'Professional and engaging'))}" en cada párrafo
4. **TONO**: Mantén consistentemente el tono {book_params.get('tone', approved_architecture.get('tone', 'Profesional')).upper()} durante todo el contenido
5. **AUDIENCIA**: Escribe específicamente para {book_params.get('target_audience', approved_architecture.get('target_audience', 'General'))} - adapta vocabulario y ejemplos
6. **CONTENIDO**: Genera contenido COMPLETO, EXTENSO y VALIOSO (no resúmenes ni relleno)
7. **CONTINUIDAD**: Mantén perfección narrativa con contenido anterior - sin cortes abruptos
8. **ESTRUCTURA**: {"Continúa expandiendo orgánicamente donde quedó" if chunk_info.get('is_continuation', False) else "Empieza directamente con el primer capítulo de este chunk"}
9. **PROFUNDIDAD**: Cada concepto debe desarrollarse con múltiples niveles de profundidad
10. **EJEMPLOS**: Incluye casos reales, anécdotas, metáforas que ilustren cada punto específicos del contexto descrito
11. **VALOR PRÁCTICO**: Proporciona consejos implementables, herramientas y metodologías relevantes al tema
12. **ENGAGEMENT**: Mantén al lector enganchado con contenido interesante y relevante al género y audiencia
13. **🚨 NO DUPLICACIÓN**: NUNCA repitas información que ya aparece en otros capítulos de la estructura completa mostrada arriba. Cada capítulo debe tener contenido único y específico

**📚 TÉCNICAS DE EXPANSIÓN NATURAL:**
- **Contexto histórico**: Cómo evolucionaron los conceptos, antecedentes relevantes
- **Múltiples perspectivas**: Diferentes escuelas de pensamiento, enfoques alternativos  
- **Casos de estudio detallados**: Ejemplos reales con análisis profundo
- **Implementación práctica**: Pasos específicos, frameworks, metodologías
- **Problemas y soluciones**: Challenges comunes y cómo resolverlos
- **Herramientas y recursos**: Software, técnicas, recursos útiles
- **Conexiones interdisciplinarias**: Cómo se relaciona con otros campos
- **Ejercicios reflexivos**: Preguntas que inviten al análisis del lector

**🚨 CALIDAD SOBRE CANTIDAD**: El objetivo es generar contenido naturalmente extenso de ALTO VALOR, no relleno. Cada párrafo debe aportar valor único al lector.

{"🔄 CONTINUACIÓN: Expande orgánicamente el contenido para alcanzar las páginas faltantes manteniendo la excelencia" if chunk_info.get('is_continuation', False) else "✍️ CREACIÓN: Desarrolla cada capítulo con la profundidad que merece según la arquitectura aprobada"}"""

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
    
    def _build_complete_book_structure(self, approved_architecture: Dict[str, Any]) -> str:
        """
        Construye una vista completa de la estructura del libro para evitar duplicación entre chunks.
        """
        structure = approved_architecture.get('structure', {})
        chapters = structure.get('chapters', [])
        
        if not chapters:
            return "Estructura de capítulos no disponible"
        
        structure_text = "TODOS LOS CAPÍTULOS DEL LIBRO (NO duplicar contenido entre ellos):\n"
        
        # Incluir introducción si existe
        if structure.get('introduction'):
            intro = structure['introduction']
            structure_text += f"📖 INTRODUCCIÓN: {intro.get('title', 'Introducción')}\n"
            structure_text += f"   - Resumen: {intro.get('summary', 'Introducción al libro')}\n"
            structure_text += f"   - Páginas: {intro.get('pages', 'N/A')}\n\n"
        
        # Incluir todos los capítulos
        for i, chapter in enumerate(chapters, 1):
            chapter_title = chapter.get('title', f'Capítulo {i}')
            chapter_summary = chapter.get('summary', 'Sin resumen')
            chapter_pages = chapter.get('pages', chapter.get('estimated_pages', 'N/A'))
            key_points = chapter.get('key_points', [])
            
            structure_text += f"📚 CAPÍTULO {i}: {chapter_title}\n"
            structure_text += f"   - Resumen: {chapter_summary}\n"
            structure_text += f"   - Páginas: {chapter_pages}\n"
            if key_points:
                structure_text += f"   - Puntos clave: {', '.join(key_points[:3])}\n"
            structure_text += "\n"
        
        # Incluir conclusión si existe
        if structure.get('conclusion'):
            conclusion = structure['conclusion']
            structure_text += f"📖 CONCLUSIÓN: {conclusion.get('title', 'Conclusión')}\n"
            structure_text += f"   - Resumen: {conclusion.get('summary', 'Conclusión del libro')}\n"
            structure_text += f"   - Páginas: {conclusion.get('pages', 'N/A')}\n\n"
        
        structure_text += """🚨 REGLAS DE NO DUPLICACIÓN:
• NO generes el contenido principal que ya pertenezca a otros capítulos listados arriba
• SÍ puedes hacer referencias breves a temas de otros capítulos si complementan el objetivo del capítulo actual
• SÍ puedes mencionar conceptos de otros capítulos para dar contexto o conectar ideas
• NO desarrolles en profundidad temas que son el foco principal de otros capítulos
• Mantén el enfoque en el propósito específico del capítulo que estás generando"""
        
        return structure_text
    
    # =====================================
    # EXPANSIÓN ORGÁNICA PARA CUMPLIMIENTO DE PÁGINAS
    # =====================================
    
    async def _expand_content_organically(self, content: str, target_words: int, book_params: Dict[str, Any], 
                                        approved_architecture: Dict[str, Any]) -> str:
        """Expande contenido de manera orgánica manteniendo calidad y fluidez narrativa"""
        
        current_words = len(content.split())
        words_needed = target_words - current_words
        
        if words_needed <= 0:
            return content
        
        # Obtener información del libro para contexto
        language_map = {'es': 'Spanish', 'en': 'English', 'pt': 'Portuguese', 'fr': 'French'}
        language_name = language_map.get(book_params.get('language', 'es'), 'Spanish')
        
        expansion_prompt = f"""**EXPANSIÓN ORGÁNICA DE CONTENIDO DE ALTA CALIDAD**

Eres un editor experto especializado en enriquecer libros manteniendo fluidez narrativa perfecta.

**CONTENIDO ACTUAL A EXPANDIR:**
```
{content}
```

**OBJETIVO DE EXPANSIÓN:**
- Palabras actuales: {current_words:,}
- Palabras objetivo: {target_words:,}
- Palabras a agregar: {words_needed:,}
- Idioma: {language_name.upper()}

**INFORMACIÓN DEL LIBRO (mantener coherencia):**
- Título: {book_params.get('title', 'Sin título')}
- Género: {book_params.get('genre', 'General')}
- Audiencia: {book_params.get('target_audience', 'General')}
- Tono: {book_params.get('tone', 'Profesional')}

**ESTRUCTURA COMPLETA DEL LIBRO (NO duplicar contenido de otros capítulos):**
{self._build_complete_book_structure(approved_architecture)}

**TÉCNICAS DE EXPANSIÓN ORGÁNICA (NO usar todas, elegir las más apropiadas):**

1. **PROFUNDIZACIÓN CONCEPTUAL:**
   - Desarrolla más las ideas principales con explicaciones adicionales
   - Agrega niveles de detalle que no estaban presentes
   - Incluye matices y sutilezas importantes

2. **CASOS PRÁCTICOS REALES:**
   - Ejemplos específicos de la vida real o industria
   - Estudios de caso con análisis detallado
   - Escenarios hipotéticos pero realistas

3. **IMPLEMENTACIÓN DETALLADA:**
   - Pasos específicos y metodologías
   - Herramientas y técnicas concretas
   - Frameworks y procesos detallados

4. **CONTEXTO ENRIQUECEDOR:**
   - Antecedentes históricos relevantes
   - Evolución de conceptos o técnicas
   - Perspectivas culturales o regionales

5. **MÚLTIPLES PERSPECTIVAS:**
   - Diferentes enfoques o escuelas de pensamiento
   - Pros y contras de distintas aproximaciones
   - Debates actuales en el campo

6. **VALOR PRÁCTICO ADICIONAL:**
   - Consejos implementables inmediatamente
   - Errores comunes y cómo evitarlos
   - Mejores prácticas y lecciones aprendidas

7. **CONEXIONES Y SÍNTESIS:**
   - Relaciones con otros conceptos del libro
   - Aplicaciones en diferentes contextos
   - Síntesis de múltiples ideas

**RESTRICCIONES CRÍTICAS:**
❌ NO repetir información ya presente
❌ NO agregar relleno o contenido irrelevante  
❌ NO cambiar el tono o estilo existente
❌ NO romper la fluidez narrativa
❌ NO crear secciones desconectadas

✅ MANTENER la estructura y organización actual
✅ RESPETAR los títulos y subtítulos existentes
✅ PRESERVAR las transiciones naturales
✅ ASEGURAR que cada adición sea valiosa

**RESULTADO ESPERADO:**
Contenido expandido que se lea como si siempre hubiera tenido esa extensión, rico en valor y perfectamente fluido. El lector no debe notar dónde terminaba el contenido original y dónde empezó la expansión.

**INSTRUCCIÓN FINAL:**
Devuelve el contenido completo expandido, manteniendo TODO el contenido original más las adiciones orgánicas. Escribe en {language_name.upper()} exclusivamente."""

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=32000,  # Suficiente para expansión
                temperature=0.7,   # Creatividad controlada
                messages=[{
                    "role": "user",
                    "content": expansion_prompt
                }]
            )
            
            expanded_content = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    expanded_content += block.text
            
            logger.info("organic_expansion_completed",
                       original_words=current_words,
                       target_words=target_words,
                       final_words=len(expanded_content.split()),
                       expansion_success=len(expanded_content.split()) > current_words)
            
            return expanded_content.strip()
            
        except Exception as e:
            logger.error("organic_expansion_failed", error=str(e))
            return content  # Devolver contenido original si falla
    
    async def _validate_chunk_quality_and_length(self, chunk_content: str, target_pages: int, 
                                                book_id: int, chunk_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validación suave que prioriza calidad pero busca cumplir target de páginas"""
        
        actual_words = len(chunk_content.split())
        actual_pages = actual_words // 350
        target_words = target_pages * 350
        
        compliance_ratio = actual_pages / target_pages if target_pages > 0 else 1
        
        # Validación con rangos flexibles que priorizan calidad
        if compliance_ratio >= 0.90:  # 90% o más es excelente
            status = "excellent" if compliance_ratio >= 0.95 else "very_good"
            return {
                'status': status,
                'actual_words': actual_words,
                'actual_pages': actual_pages,
                'target_pages': target_pages,
                'compliance_ratio': compliance_ratio,
                'meets_target': True,
                'needs_expansion': False,
                'quality_preserved': True,
                'message': f"✅ Chunk {chunk_info.get('index', '?')}: {actual_pages}/{target_pages} páginas ({compliance_ratio:.1%})"
            }
        
        elif compliance_ratio >= 0.75:  # 75-90% - expansión orgánica recomendada
            return {
                'status': 'expandable',
                'actual_words': actual_words,
                'actual_pages': actual_pages,
                'target_pages': target_pages,
                'compliance_ratio': compliance_ratio,
                'meets_target': compliance_ratio >= 0.90,
                'needs_expansion': True,
                'expansion_words': target_words - actual_words,
                'quality_preserved': True,
                'message': f"📈 Chunk {chunk_info.get('index', '?')}: {actual_pages}/{target_pages} páginas - Expansión orgánica recomendada"
            }
        
        else:  # Menos de 75% - posible problema en la generación
            logger.warning("chunk_significantly_under_target", 
                          book_id=book_id, 
                          chunk_index=chunk_info.get('index', '?'),
                          actual_pages=actual_pages, 
                          target_pages=target_pages)
            return {
                'status': 'concerning',
                'actual_words': actual_words,
                'actual_pages': actual_pages,
                'target_pages': target_pages,
                'compliance_ratio': compliance_ratio,
                'meets_target': False,
                'needs_expansion': True,
                'expansion_words': target_words - actual_words,
                'quality_preserved': True,
                'message': f"⚠️ Chunk {chunk_info.get('index', '?')}: {actual_pages}/{target_pages} páginas - Revisión necesaria"
            }

    # =====================================
    # MÉTODOS DE SOPORTE PARA REGENERACIÓN DE CAPÍTULOS
    # =====================================
    
    def _build_chapter_regeneration_messages(self, chapter_content: str, feedback: Dict[str, str], book=None) -> List[Dict[str, Any]]:
        """Construye los mensajes para la regeneración de capítulos."""
        return [
            {
                "role": "system",
                "content": self._build_chapter_regeneration_system_prompt()
            },
            {
                "role": "user", 
                "content": self._build_chapter_regeneration_user_prompt(chapter_content, feedback, book)
            }
        ]
    
    async def _generate_chunk_parallel(self, book_id: int, chunk_info: Dict, book_params: Dict[str, Any], 
                                     approved_architecture: Dict[str, Any], introduction_content: str, 
                                     chunk_idx: int) -> Dict[str, Any]:
        """
        🚀 Genera un chunk de forma independiente para ejecución paralela.
        Optimizado para máxima velocidad sin sacrificar calidad.
        """
        from app.routes.websocket import emit_generation_log
        
        try:
            chunk_num = chunk_info['index']
            
            emit_generation_log(book_id, 'info', 
                f'🚀 Chunk paralelo {chunk_num} iniciado: {len(chunk_info["chapters"])} capítulos')
            
            # Generar contenido usando el método existente pero sin contexto de chunks previos
            chunk_result = await self._generate_single_chunk(
                book_id=book_id,
                chunk_info=chunk_info,
                book_params=book_params,
                approved_architecture=approved_architecture,
                previous_content=introduction_content,  # Solo usar introducción como contexto
                chunk_summaries=[],  # Sin dependencias de chunks previos
                progress_base=30 + (chunk_idx * 30)  # Progreso distribuido
            )
            
            emit_generation_log(book_id, 'success', 
                f'✅ Chunk paralelo {chunk_num} completado: {len(chunk_result["content"].split())} palabras')
            
            return chunk_result
            
        except Exception as e:
            emit_generation_log(book_id, 'error', 
                f'❌ Error en chunk paralelo {chunk_num}: {str(e)}')
            raise
    
    def _build_chapter_regeneration_system_prompt(self) -> str:
        """Prompt del sistema para regeneración de capítulos."""
        return """Eres un escritor experto y editor profesional especializado en mejorar capítulos de libros basándote en feedback específico de usuarios.

Tu tarea es regenerar completamente capítulos existentes, mejorándolos según las indicaciones del usuario, manteniendo siempre:
- Coherencia con el tema y propósito del libro
- Estructura profesional y bien organizada
- Contenido más extenso y detallado que el original
- Ejemplos prácticos y casos de estudio relevantes
- Formato Markdown apropiado y profesional
- Tono profesional pero accesible

Características específicas de formato y estructura que DEBES seguir:

**📝 FORMATO MARKDOWN PROFESIONAL:**
- Utiliza encabezados H2 (##) para títulos principales
- Utiliza encabezados H3 (###) para subtemas y secciones
- Utiliza encabezados H4 (####) para subsecciones cuando sea necesario
- Incluye listas con viñetas (-) y numeradas (1.) según corresponda
- Utiliza **texto en negrita** para términos clave e importantes
- Utiliza *cursiva* para énfasis y conceptos
- Incluye citas y bloques destacados usando > cuando sea apropiado
- Utiliza tablas en Markdown cuando ayuden a organizar información
- Incluye separadores (---) entre secciones principales cuando mejore la legibilidad

**📊 ESTRUCTURA Y ORGANIZACIÓN:**
- Comienza cada capítulo con una breve introducción que contextualice el tema
- Organiza el contenido en secciones lógicas y bien definidas
- Incluye ejemplos prácticos, casos de estudio y anécdotas relevantes
- Termina cada capítulo con una conclusión o resumen de puntos clave
- Asegúrate de que haya transiciones suaves entre secciones
- Mantén un flujo narrativo coherente y profesional

**📏 EXTENSIÓN Y DETALLE:**
- Haz el contenido significativamente más extenso que el original
- Desarrolla cada punto con profundidad y detalle
- Incluye múltiples ejemplos y casos prácticos
- Agrega contexto histórico, estadísticas o datos relevantes cuando sea apropiado
- Expande conceptos con explicaciones claras y accesibles

**✅ INSTRUCCIONES FINALES:**
- Mantén el título del capítulo pero transforma completamente el contenido
- Responde EXCLUSIVAMENTE con el contenido del capítulo regenerado en Markdown
- NO incluyas metadatos, comentarios o explicaciones fuera del contenido del capítulo
- Asegúrate de que el resultado sea un capítulo completo, profesional y bien estructurado"""
    
    def _build_chapter_regeneration_user_prompt(self, chapter_content: str, feedback: Dict[str, str], book=None) -> str:
        """Prompt del usuario para regeneración de capítulos."""
        
        # Calcular palabras recomendadas basado en la arquitectura del libro +20%
        target_words = "extenso y detallado"
        if book and hasattr(book, 'architecture') and book.architecture:
            try:
                # Obtener palabras estimadas de la arquitectura
                estimated_words = book.architecture.get('estimated_words', 0)
                if estimated_words > 0:
                    # Obtener número de capítulos
                    chapters = book.architecture.get('structure', {}).get('chapters', [])
                    chapter_count = len(chapters) if chapters else book.chapter_count or 10
                    
                    # Calcular palabras por capítulo promedio + 20%
                    words_per_chapter = int((estimated_words / chapter_count) * 1.2)
                    target_words = f"extenso y detallado (aproximadamente {words_per_chapter:,} palabras)"
                else:
                    target_words = "extenso y detallado"
            except Exception:
                # Si hay error en el cálculo, usar descripción genérica
                target_words = "extenso y detallado"
        
        return f"""CAPÍTULO ACTUAL A REGENERAR:
{chapter_content}

FEEDBACK DEL USUARIO:
- Qué no le gusta: {feedback.get('whatDislike', '')}
- Qué quiere cambiar: {feedback.get('whatChange', '')}
- Cómo le gustaría que quedara: {feedback.get('howWant', '')}

INSTRUCCIONES ESPECÍFICAS DE REGENERACIÓN:

**🎯 OBJETIVO PRINCIPAL:**
Regenera COMPLETAMENTE el capítulo considerando todo el feedback del usuario y aplicando las mejores prácticas de escritura profesional.

**📝 FORMATO Y ESTRUCTURA REQUERIDOS:**
1. Mantén el título del capítulo (##) pero transforma completamente todo el contenido
2. Utiliza la estructura de formato Markdown profesional especificada en las instrucciones del sistema
3. Organiza el contenido en secciones lógicas con encabezados H3 (###) y H4 (####) cuando sea necesario
4. Incluye listas, tablas, citas y elementos visuales en Markdown para mejorar la legibilidad
5. Asegúrate de usar **texto en negrita** para conceptos clave y *cursiva* para énfasis

**📊 CONTENIDO Y EXTENSIÓN:**
6. Haz el contenido mucho más {target_words}
7. Desarrolla cada concepto con profundidad, incluyendo:
   - Explicaciones detalladas y claras
   - Ejemplos prácticos y casos de estudio relevantes
   - Anécdotas, datos, estadísticas o contexto histórico cuando sea apropiado
   - Múltiples perspectivas o enfoques del tema
8. Asegúrate de que cada sección tenga suficiente contenido y desarrollo

**🎨 CALIDAD Y TONO:**
9. Mantén un tono profesional pero accesible y atractivo para el lector
10. Crea transiciones suaves entre secciones para mantener el flujo narrativo
11. Termina el capítulo con una conclusión o síntesis que refuerce los puntos clave
12. Asegúrate de que el resultado sea significativamente superior al contenido original

**✅ RESULTADO ESPERADO:**
El capítulo regenerado debe ser un contenido completamente nuevo, mucho más extenso, mejor organizado, y que responda específicamente a todas las solicitudes del feedback del usuario.

Regenera el capítulo ahora en formato Markdown siguiendo todas estas especificaciones:"""


# Singleton instance
_claude_service: Optional[ClaudeService] = None


def get_claude_service() -> ClaudeService:
    """Get or create Claude service instance."""
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeService()
    return _claude_service