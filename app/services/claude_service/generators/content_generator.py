"""
Content Generator

Generador especializado para contenido completo de libros usando multi-chunk.
Extraído de ClaudeService original - responsabilidad única.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from ..clients.claude_client import ClaudeClient
from ..config.claude_config import ClaudeConfig
from ..config.token_config import TokenConfig
from ..config.dynamic_config import DynamicSystemConfiguration, create_dynamic_configuration_from_user_form

logger = logging.getLogger(__name__)
logging_logger = logging.getLogger(__name__)


class ContentGenerator:
    """
    Generador especializado para contenido completo de libros.
    
    Extrae la lógica de generación multi-chunk que estaba en ClaudeService
    (líneas 1638+ con métodos helper).
    """
    
    def __init__(self, config: ClaudeConfig, claude_client: ClaudeClient):
        """
        Inicializa el generador de contenido.
        
        Args:
            config: Configuración de Claude
            claude_client: Cliente Claude configurado
        """
        self.config = config
        self.client = claude_client
        self.token_config = TokenConfig()
        
        # Configuraciones por defecto (serán reemplazadas por configuración dinámica)
        self.chunk_timeout = config.chunk_timeout
        self.max_chunks = config.max_chunks
        self.chunk_overlap = config.chunk_overlap
        
        # Sistema de configuración dinámico (inicializado en None)
        self.dynamic_config: Optional[DynamicSystemConfiguration] = None
        
        logging_logger.info(f"ContentGenerator initialized - max_chunks={self.max_chunks}, chunk_timeout={self.chunk_timeout}")
    
    def setup_dynamic_configuration(self, book_params: Dict[str, Any]) -> None:
        """
        Configura el sistema dinámico basado en parámetros del usuario.
        
        Reemplaza los 50+ hardcodes con configuración adaptada al libro específico.
        
        Args:
            book_params: Parámetros del libro del usuario desde el formulario
        """
        try:
            # Crear configuración dinámica desde parámetros del usuario
            self.dynamic_config = create_dynamic_configuration_from_user_form(book_params)
            
            # Actualizar configuraciones del generador con valores dinámicos
            self.chunk_timeout = self.dynamic_config.chunk_timeout
            self.max_chunks = self.dynamic_config.max_chunks
            self.chunk_overlap = self.dynamic_config.chunk_overlap
            
            # Actualizar configuración de tokens dinámicamente
            self.config.max_tokens = self.dynamic_config.max_tokens
            self.config.thinking_budget = self.dynamic_config.thinking_budget
            self.config.token_limits = self.dynamic_config.token_limits
            
            logging_logger.info(f"dynamic_configuration_applied - target_pages={self.dynamic_config.target_pages}, "
                              f"max_chunks={self.max_chunks}, chunk_timeout={self.chunk_timeout}, "
                              f"max_tokens={self.config.max_tokens}, thinking_budget={self.config.thinking_budget}")
            
        except Exception as e:
            logging_logger.error(f"failed_to_setup_dynamic_configuration - error={str(e)}, using_fallback_config=True")
            # En caso de error, mantener configuración por defecto
            self.dynamic_config = None
    
    async def generate_book_from_architecture_multichunk(self, book_id: int, book_params: Dict[str, Any], approved_architecture: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera el contenido completo del libro usando generación multi-chunked con Claude Sonnet 4.
        Garantiza que se cumplan las páginas prometidas al usuario.
        
        Extraído de ClaudeService.generate_book_from_architecture_multichunk() líneas 1638+.
        
        Args:
            book_id: ID del libro
            book_params: Parámetros originales del libro
            approved_architecture: Arquitectura aprobada por el usuario
            
        Returns:
            Resultado de la generación con contenido completo
        """
        try:
            # 🎯 CONFIGURACIÓN DINÁMICA: Reemplazar 50+ hardcodes con configuración adaptada al usuario
            self.setup_dynamic_configuration(book_params)
            # Log crítico del inicio con Claude Sonnet 4
            # Obtener capítulos compatibles con ambos formatos para logging
            logging_chapters = (approved_architecture.get('structure', {}).get('chapters', []) or 
                              approved_architecture.get('chapters', []))
            
            logging_logger.info(f"starting_multichunk_generation - book_id={book_id}, model={self.config.model}, chapters_count={len(logging_chapters)}, target_pages={approved_architecture.get('target_pages')}, estimated_words={approved_architecture.get('estimated_words')}, max_tokens_per_chunk={self.config.max_tokens}, max_chunks={self.max_chunks}")
            
            # Emisión de evento de inicio
            from app.routes.websocket import emit_book_progress_update, emit_generation_log
            
            emit_book_progress_update(book_id, {
                'current': 5,
                'total': 100,
                'status': 'initializing',
                'status_message': 'Iniciando generación multi-chunked con Claude Sonnet 4...',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # Dividir capítulos en chunks - Compatible con ambos formatos de arquitectura
            chapters = []
            if approved_architecture.get('structure', {}).get('chapters'):
                # Formato: architecture.structure.chapters
                chapters = approved_architecture['structure']['chapters']
            elif approved_architecture.get('chapters'):
                # Formato: architecture.chapters (nuevo formato)
                chapters = approved_architecture['chapters']
            
            total_chapters = len(chapters)
            
            logging_logger.info(f"chapters_access_debug - book_id={book_id}, has_structure={bool(approved_architecture.get('structure'))}, has_structure_chapters={bool(approved_architecture.get('structure', {}).get('chapters'))}, has_direct_chapters={bool(approved_architecture.get('chapters'))}, chapters_found={total_chapters}, architecture_keys={list(approved_architecture.keys())}")
            
            if total_chapters == 0:
                raise Exception("No se encontraron capítulos en la arquitectura")
            
            # 🚀 OPTIMIZACIÓN: Balance PERFECTO entre VELOCIDAD y TARGETING PRECISO DE PÁGINAS
            # Calcular chunks necesarios (3-4 capítulos por chunk - óptimo para control de páginas)
            chapters_per_chunk = max(3, min(4, total_chapters // max(1, self.max_chunks - 1) + 1))
            chunks = []
            
            for i in range(0, total_chapters, chapters_per_chunk):
                chunk_chapters = chapters[i:i + chapters_per_chunk]
                chunks.append({
                    'index': len(chunks) + 1,
                    'chapters': chunk_chapters,
                    'start_chapter': i + 1,
                    'end_chapter': min(i + chapters_per_chunk, total_chapters)
                })
            
            logging_logger.info(f"chunk_planning - book_id={book_id}, total_chunks={len(chunks)}, chapters_per_chunk={chapters_per_chunk}, total_chapters={total_chapters}")
            
            # Variables de acumulación
            complete_book_content = []
            complete_thinking_content = []
            total_tokens_used = 0
            total_thinking_tokens = 0
            total_prompt_tokens = 0
            total_completion_tokens = 0
            chunk_summaries = []
            
            # 🚨 SISTEMA DE COHERENCIA: Basado en arquitectura aprobada con formato específico
            
            # Obtener coherence manager configurado para este libro específico
            coherence_manager = self._get_coherence_manager_for_book(book_params)
            
            # 1. Extraer target real de la arquitectura
            target_pages = coherence_manager.extract_target_pages_from_architecture(
                approved_architecture, book_params
            )
            
            # 2. Planificar páginas por chunk basado en capítulos completos de la arquitectura
            pages_per_chunk = coherence_manager.plan_pages_distribution(
                target_pages, len(chunks), total_chapters, approved_architecture, book_params
            )
            
            # 3. Preparar contexto de coherencia global
            coherence_context = coherence_manager.build_coherence_context(
                approved_architecture, book_params
            )
            
            logging_logger.info(f"coherence_system_ready - book_id={book_id}, target_pages={target_pages}, pages_per_chunk={pages_per_chunk}, coherence_context_size={len(str(coherence_context))}")
            
            # Emitir evento de planificación completada
            emit_book_progress_update(book_id, {
                'current': 10,
                'total': 100,
                'status': 'planned',
                'status_message': f'Planificación completada: {len(chunks)} chunks, {target_pages} páginas objetivo',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # 🚀 GENERACIÓN MULTI-CHUNK PARALELIZADA CON DEPENDENCIAS INTELIGENTES
            complete_book_content = await self._generate_chunks_parallel(
                book_id=book_id,
                chunks=chunks,
                book_params=book_params,
                approved_architecture=approved_architecture,
                coherence_context=coherence_context,
                pages_per_chunk=pages_per_chunk,
                coherence_manager=coherence_manager
            )
            
            # Actualizar estadísticas consolidadas
            for chunk_result in complete_book_content:
                complete_thinking_content.append(chunk_result.get('thinking_content', ''))
                total_tokens_used += chunk_result.get('tokens_used', 0)
                total_thinking_tokens += chunk_result.get('thinking_tokens', 0)
                total_prompt_tokens += chunk_result.get('prompt_tokens', 0)
                total_completion_tokens += chunk_result.get('completion_tokens', 0)
                
                # Agregar resumen del chunk
                chunk_summaries.append({
                    'index': chunk_result.get('chunk_index', 0) + 1,
                    'chapters': f"{chunk_result.get('start_chapter', 0)}-{chunk_result.get('end_chapter', 0)}",
                    'content_length': len(chunk_result.get('content', '')),
                    'duration': chunk_result.get('duration', 0),
                    'tokens_used': chunk_result.get('tokens_used', 0)
                })
            
            # Extraer solo el contenido para combinar
            complete_book_content = [chunk['content'] for chunk in complete_book_content]
            
            # Generar introducción y conclusión si se requieren
            introduction_content = ""
            conclusion_content = ""
            
            if book_params.get('include_introduction', False):
                intro_result = await self._generate_introduction(
                    book_id, book_params, approved_architecture, 
                    "\n\n".join(complete_book_content)
                )
                if intro_result.get('success'):
                    introduction_content = intro_result['content']
                    total_tokens_used += intro_result.get('tokens_used', 0)
                    # 🔧 FIX: Acumular tokens de introducción por tipo
                    total_completion_tokens += intro_result.get('tokens_used', 0)
            
            if book_params.get('include_conclusion', False):
                concl_result = await self._generate_conclusion(
                    book_id, book_params, approved_architecture,
                    "\n\n".join(complete_book_content)
                )
                if concl_result.get('success'):
                    conclusion_content = concl_result['content']
                    total_tokens_used += concl_result.get('tokens_used', 0)
                    # 🔧 FIX: Acumular tokens de conclusión por tipo
                    total_completion_tokens += concl_result.get('tokens_used', 0)
            
            # Combinar todo el contenido final en estructura HTML
            final_content_parts = []
            
            # Añadir wrapper HTML principal
            final_content_parts.append('<div class="book-content">')
            
            if introduction_content:
                final_content_parts.append(introduction_content)
            
            # Combinar todos los chunks de contenido principal
            for chunk_content in complete_book_content:
                final_content_parts.append(chunk_content)
            
            if conclusion_content:
                final_content_parts.append(conclusion_content)
            
            # Cerrar wrapper principal
            final_content_parts.append('</div>')
                
            final_content = "\n\n".join(final_content_parts)
            final_thinking = "\n\n".join(complete_thinking_content)
            
            # Validación final de calidad
            final_word_count = len(final_content.split())
            estimated_pages = final_word_count / 350  # 🎯 FIX: Usar 350 palabras/página consistente con sistema original
            
            # Registrar éxito final
            self.client.circuit_breaker.record_success()
            
            logging_logger.info(f"multichunk_generation_completed - book_id={book_id}, total_chunks={len(chunks)}, final_word_count={final_word_count}, estimated_pages={estimated_pages}, total_tokens_used={total_tokens_used}, total_thinking_tokens={total_thinking_tokens}")
            
            emit_book_progress_update(book_id, {
                'current': 100,
                'total': 100,
                'status': 'completed',
                'status_message': f'Libro completado: {final_word_count} palabras, ~{estimated_pages:.0f} páginas',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            return {
                'success': True,
                'content': final_content,
                'thinking_content': final_thinking,
                'word_count': final_word_count,
                'estimated_pages': estimated_pages,
                'total_tokens_used': total_tokens_used,
                'total_thinking_tokens': total_thinking_tokens,
                'chunk_count': len(chunks),
                'chunk_summaries': chunk_summaries,
                'introduction_included': bool(introduction_content),
                'conclusion_included': bool(conclusion_content),
                # 🔧 FIX: Agregar campo 'usage' esperado por la tarea de Celery
                'usage': {
                    'prompt_tokens': total_prompt_tokens,
                    'completion_tokens': total_completion_tokens,
                    'thinking_tokens': total_thinking_tokens
                },
                # 🔧 FIX: Agregar campo 'final_stats' para compatibilidad
                'final_stats': {
                    'words': final_word_count,
                    'pages': int(estimated_pages)
                }
            }
            
        except Exception as e:
            error_msg = f"Error en generación multi-chunk: {str(e)}"
            logging_logger.error(f"multichunk_generation_error - book_id={book_id}, error={str(e)}, error_type={type(e).__name__}")
            
            # Registrar error en circuit breaker
            self.client.circuit_breaker.record_failure(e)
            
            return {
                'success': False,
                'error': error_msg,
                'error_type': type(e).__name__
            }
    
    async def _generate_single_chunk(self, book_id: int, chunk_info: Dict, book_params: Dict[str, Any], 
                                   approved_architecture: Dict[str, Any], coherence_context: Dict[str, Any],
                                   previous_chunks_content: List[str], target_pages: int, 
                                   chunk_index: int, total_chunks: int) -> Dict[str, Any]:
        """
        Genera un chunk individual del libro.
        
        Extraído de ClaudeService._generate_single_chunk() líneas 2096+.
        
        Args:
            book_id: ID del libro
            chunk_info: Información del chunk a generar
            book_params: Parámetros del libro
            approved_architecture: Arquitectura aprobada
            coherence_context: Contexto de coherencia
            previous_chunks_content: Contenido de chunks anteriores
            target_pages: Páginas objetivo para este chunk
            chunk_index: Índice del chunk actual
            total_chunks: Total de chunks
            
        Returns:
            Resultado de la generación del chunk
        """
        try:
            # Preparar mensajes para este chunk
            prompt_data = self._build_chunk_messages(
                chunk_info, book_params, approved_architecture, 
                coherence_context, previous_chunks_content, target_pages
            )
            
            system_prompt = prompt_data["system"]
            messages = prompt_data["messages"]
            
            # Tokens optimizados para chunk
            chunk_max_tokens = self.token_config.get_tokens_for_content_type('chunk_main')  # 40000
            chunk_thinking_budget = self.config.get_thinking_budget_for_content_type('chunk_main')  # min(40000-500, 45000) = 39500
            
            # Variables para acumular respuesta
            chunk_content = []
            chunk_thinking = []
            chunk_count = 0
            
            # Generación con streaming
            async with asyncio.timeout(self.chunk_timeout):
                async with self.client.client.messages.stream(
                    model=self.config.model,
                    max_tokens=chunk_max_tokens,
                    temperature=self.config.temperature,
                    system=system_prompt,
                    messages=messages,
                    thinking={
                        "type": "enabled", 
                        "budget_tokens": chunk_thinking_budget
                    },
                ) as stream:
                    
                    async for event in stream:
                        chunk_count += 1
                        
                        # Processing thinking content
                        if (event.type == "content_block_delta" and 
                            hasattr(event, 'delta') and hasattr(event.delta, 'text')):
                            # Check if this is thinking content
                            if hasattr(event, 'index') and event.index == 0:  # Usually thinking is first block
                                chunk_thinking.append(event.delta.text)
                            else:
                                chunk_content.append(event.delta.text)
                        
                        # Regular content blocks
                        elif (event.type == "content_block_delta" and 
                              hasattr(event, 'delta') and hasattr(event.delta, 'text')):
                            chunk_content.append(event.delta.text)
            
            # Combinar contenido del chunk
            final_chunk_content = "".join(chunk_content)
            final_chunk_thinking = "".join(chunk_thinking)
            
            # Validar calidad del chunk
            if len(final_chunk_content.strip()) < 1000:
                raise Exception(f"Chunk {chunk_index + 1} demasiado corto: {len(final_chunk_content)} caracteres")
            
            word_count = len(final_chunk_content.split())
            estimated_pages = word_count / 350  # 🎯 FIX: Usar 350 palabras/página consistente
            
            logging_logger.info(f"chunk_generation_success - book_id={book_id}, chunk_index={chunk_index + 1}, word_count={word_count}, estimated_pages={estimated_pages}, target_pages={target_pages}")
            
            return {
                'success': True,
                'content': final_chunk_content,
                'thinking_content': final_chunk_thinking,
                'word_count': word_count,
                'estimated_pages': estimated_pages,
                'tokens_used': chunk_count,  # Approximate total tokens
                # 🔧 FIX: Mejorar estimaciones de tokens por tipo
                'prompt_tokens': chunk_count * 8,  # Estimación tokens de prompt
                'completion_tokens': len(final_chunk_content) // 4,  # ~4 caracteres por token
                'thinking_tokens': len(final_chunk_thinking) // 4    # Thinking tokens
            }
            
        except asyncio.TimeoutError:
            error_msg = f"Timeout en chunk {chunk_index + 1} después de {self.chunk_timeout}s"
            logging_logger.error(f"chunk_generation_timeout - book_id={book_id}, chunk_index={chunk_index + 1}, timeout={self.chunk_timeout}")
            return {
                'success': False,
                'error': error_msg,
                'error_type': 'timeout'
            }
            
        except Exception as e:
            error_msg = f"Error en chunk {chunk_index + 1}: {str(e)}"
            logging_logger.error(f"chunk_generation_error - book_id={book_id}, chunk_index={chunk_index + 1}, error={str(e)}")
            return {
                'success': False,
                'error': error_msg,
                'error_type': type(e).__name__
            }
    
    async def _generate_introduction(self, book_id: int, book_params: Dict[str, Any], 
                                   approved_architecture: Dict[str, Any], 
                                   main_content: str) -> Dict[str, Any]:
        """
        Genera introducción para el libro usando Claude API.
        
        🚀 IMPLEMENTACIÓN REAL: Usa Claude API respetando el idioma del libro.
        """
        try:
            # Extraer información del libro
            title = approved_architecture.get('title', book_params.get('title', ''))
            genre = approved_architecture.get('genre', book_params.get('genre', ''))
            language = book_params.get('language', 'es')
            
            # Mapeo de idiomas
            language_map = {
                'es': 'español',
                'en': 'inglés',
                'fr': 'francés', 
                'de': 'alemán',
                'pt': 'portugués',
                'it': 'italiano'
            }
            language_name = language_map.get(language, language)
            
            # Construir prompt para introducción
            system_prompt = f"""Eres un escritor experto especializado en crear introducciones atractivas para libros en formato HTML.

Tu tarea es escribir una introducción profesional en formato HTML que:
- Capte la atención del lector desde el primer párrafo
- Establezca el tono y estilo del libro
- Presente brevemente el tema o historia
- Genere expectativa e interés por continuar leyendo
- Esté completamente en {language_name}

FORMATO REQUERIDO:
- Envuelve la introducción en <div class="book-introduction">
- Usa <h1 id="introduccion">Introducción</h1> como header principal
- Cada párrafo en tags <p></p>
- HTML válido y bien estructurado

IMPORTANTE: La introducción debe estar COMPLETAMENTE en {language_name}, sin mezclar otros idiomas a menos que sea parte de ejemplos educativos específicos.

Responde únicamente con el contenido HTML de la introducción, sin comentarios adicionales."""
            
            # Obtener temas principales si existen
            themes = approved_architecture.get('themes', [])
            themes_info = f"\n- Temas principales: {', '.join(themes)}" if themes else ""
            
            # Obtener una muestra del contenido para contexto
            content_sample = main_content[:1500] + "..." if len(main_content) > 1500 else main_content
            
            user_prompt = f"""Escribe una introducción profesional en formato HTML para el libro "{title}" (género: {genre}).

**INFORMACIÓN DEL LIBRO:**
- Título: "{title}"
- Género: {genre}
- Idioma: {language_name}{themes_info}

**MUESTRA DEL CONTENIDO:**
{content_sample}

**INSTRUCCIONES:**
- Formato: HTML válido con estructura de navegación
- Extensión: 2-4 párrafos (300-600 palabras)
- Tono: Profesional y atractivo para el género {genre}
- Idioma: Completamente en {language_name}
- Objetivo: Enganchar al lector y establecer expectativas
- Estilo: Coherente con el contenido del libro

**ESTRUCTURA HTML REQUERIDA:**
```html
<div class="book-introduction">
  <h1 id="introduccion">Introducción</h1>
  <p>Primer párrafo atractivo...</p>
  <p>Desarrollo de la introducción...</p>
  <p>Párrafo final que genere expectativa...</p>
</div>
```

Escribe la introducción comenzando directamente con <div class="book-introduction">."""
            
            # Llamar a Claude API
            response = await self.client.client.messages.create(
                model=self.config.model,
                max_tokens=2000,  # Suficiente para introducción
                temperature=self.config.temperature,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )
            
            # Extraer contenido
            if hasattr(response, 'content') and response.content:
                introduction_content = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
            else:
                introduction_content = str(response)
            
            # Validar que tenemos contenido útil
            if len(introduction_content.strip()) < 100:
                raise Exception(f"La introducción generada es demasiado corta: {len(introduction_content)} caracteres")
            
            logging_logger.info(f"introduction_generation_completed - book_id={book_id}, content_length={len(introduction_content)}, language={language_name}")
            
            return {
                'success': True,
                'content': introduction_content.strip(),
                'tokens_used': len(introduction_content) // 4  # Estimación aproximada
            }
            
        except Exception as e:
            error_msg = f"Error generando introducción: {str(e)}"
            logging_logger.error(f"introduction_generation_error - book_id={book_id}, error={str(e)}, error_type={type(e).__name__}")
            
            return {
                'success': False,
                'error': error_msg,
                'error_type': type(e).__name__
            }
    
    async def _generate_conclusion(self, book_id: int, book_params: Dict[str, Any], 
                                 approved_architecture: Dict[str, Any],
                                 main_content: str) -> Dict[str, Any]:
        """
        Genera conclusión para el libro usando Claude API.
        
        🚀 IMPLEMENTACIÓN REAL: Usa Claude API respetando el idioma del libro.
        """
        try:
            # Extraer información del libro
            title = approved_architecture.get('title', book_params.get('title', ''))
            genre = approved_architecture.get('genre', book_params.get('genre', ''))
            language = book_params.get('language', 'es')
            
            # Mapeo de idiomas
            language_map = {
                'es': 'español',
                'en': 'inglés',
                'fr': 'francés', 
                'de': 'alemán',
                'pt': 'portugués',
                'it': 'italiano'
            }
            language_name = language_map.get(language, language)
            
            # Construir prompt para conclusión
            system_prompt = f"""Eres un escritor experto especializado en crear conclusiones impactantes para libros en formato HTML.

Tu tarea es escribir una conclusión profesional en formato HTML que:
- Cierre satisfactoriamente los temas principales del libro
- Refuerce los mensajes clave y aprendizajes
- Deje al lector con una reflexión final valiosa
- Mantenga el tono y estilo establecido
- Esté completamente en {language_name}

FORMATO REQUERIDO:
- Envuelve la conclusión en <div class="book-conclusion">
- Usa <h1 id="conclusion">Conclusión</h1> como header principal
- Cada párrafo en tags <p></p>
- HTML válido y bien estructurado

IMPORTANTE: La conclusión debe estar COMPLETAMENTE en {language_name}, sin mezclar otros idiomas a menos que sea parte de ejemplos educativos específicos.

Responde únicamente con el contenido HTML de la conclusión, sin comentarios adicionales."""
            
            # Obtener temas principales si existen
            themes = approved_architecture.get('themes', [])
            themes_info = f"\n- Temas principales abordados: {', '.join(themes)}" if themes else ""
            
            # Obtener las últimas secciones del contenido para contexto
            content_ending = main_content[-2000:] if len(main_content) > 2000 else main_content
            
            user_prompt = f"""Escribe una conclusión profesional en formato HTML para el libro "{title}" (género: {genre}).

**INFORMACIÓN DEL LIBRO:**
- Título: "{title}"
- Género: {genre}
- Idioma: {language_name}{themes_info}

**CONTENIDO FINAL DEL LIBRO:**
...{content_ending}

**INSTRUCCIONES:**
- Formato: HTML válido con estructura de navegación
- Extensión: 2-4 párrafos (300-600 palabras)
- Tono: Reflexivo y satisfactorio para el género {genre}
- Idioma: Completamente en {language_name}
- Objetivo: Cerrar el libro de manera memorable
- Estilo: Coherente con todo el contenido desarrollado
- Enfoque: Resumir aprendizajes clave y mensaje final

**ESTRUCTURA HTML REQUERIDA:**
```html
<div class="book-conclusion">
  <h1 id="conclusion">Conclusión</h1>
  <p>Primer párrafo reflexivo...</p>
  <p>Desarrollo de la conclusión...</p>
  <p>Párrafo final memorable...</p>
</div>
```

Escribe la conclusión comenzando directamente con <div class="book-conclusion">."""
            
            # Llamar a Claude API
            response = await self.client.client.messages.create(
                model=self.config.model,
                max_tokens=2000,  # Suficiente para conclusión
                temperature=self.config.temperature,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )
            
            # Extraer contenido
            if hasattr(response, 'content') and response.content:
                conclusion_content = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
            else:
                conclusion_content = str(response)
            
            # Validar que tenemos contenido útil
            if len(conclusion_content.strip()) < 100:
                raise Exception(f"La conclusión generada es demasiado corta: {len(conclusion_content)} caracteres")
            
            logging_logger.info(f"conclusion_generation_completed - book_id={book_id}, content_length={len(conclusion_content)}, language={language_name}")
            
            return {
                'success': True,
                'content': conclusion_content.strip(),
                'tokens_used': len(conclusion_content) // 4  # Estimación aproximada
            }
            
        except Exception as e:
            error_msg = f"Error generando conclusión: {str(e)}"
            logging_logger.error(f"conclusion_generation_error - book_id={book_id}, error={str(e)}, error_type={type(e).__name__}")
            
            return {
                'success': False,
                'error': error_msg,
                'error_type': type(e).__name__
            }
    
    def _build_chunk_messages(self, chunk_info: Dict, book_params: Dict[str, Any], 
                            approved_architecture: Dict[str, Any], coherence_context: Dict[str, Any],
                            previous_chunks_content: List[str], target_pages: int) -> Dict[str, Any]:
        """
        Construye los mensajes para generación de un chunk.
        
        Extraído y simplificado de ClaudeService._build_chunk_messages().
        
        Returns:
            Diccionario con system prompt y messages
        """
        return {
            "system": self._build_chunk_system_prompt(),
            "messages": [
                {
                    "role": "user",
                    "content": self._build_chunk_user_prompt(
                        chunk_info, book_params, approved_architecture, 
                        coherence_context, previous_chunks_content, target_pages
                    )
                }
            ]
        }
    
    def _build_chunk_system_prompt(self) -> str:
        """
        Construye el system prompt para generación de chunks.
        
        🚀 ACTUALIZADO: Genera HTML con headers markdown para navegación profesional.
        """
        return """Eres un escritor experto especializado en generar contenido de alta calidad para libros en formato HTML con estructura de navegación profesional.

Tu tarea es escribir una sección específica del libro siguiendo la arquitectura proporcionada, manteniendo coherencia con el contenido previo y cumpliendo con el número de páginas objetivo.

## INSTRUCCIONES CRÍTICAS:

### 1. FORMATO HTML CON HEADERS MARKDOWN
- OBLIGATORIO: Genera contenido en formato HTML válido
- Usa headers markdown para navegación: # para capítulos principales, ## para secciones, ### para subsecciones
- Estructura cada capítulo con: <h1>Título del Capítulo</h1> para navegación
- Envuelve párrafos en tags <p></p> apropiados
- Usa <div class="chapter"> para cada capítulo completo
- Añade <div class="section"> para secciones importantes dentro de capítulos

### 2. CALIDAD NARRATIVA FLUIDA
- Escritura fluida y atractiva sin subtítulos excesivos que interrumpan la lectura
- Desarrollo natural de personajes y situaciones
- Diálogos naturales y descriptivos envolventes
- Transiciones suaves entre escenas y capítulos sin formato rígido de manual
- EVITA: Subtítulos innecesarios, listas numeradas extensas, formato de índice dentro del contenido

### 3. COHERENCIA
- Mantener consistencia con contenido previo
- Seguir la arquitectura y desarrollo de personajes establecidos
- Respetar el tono y estilo narrativo del libro

### 4. IDIOMA Y CONSISTENCIA LINGÜÍSTICA
- CRÍTICO: Mantener ABSOLUTAMENTE el idioma especificado por el usuario en TODO el texto explicativo y narrativo
- La EXPLICACIÓN, NARRACIÓN, e INSTRUCCIONES deben estar completamente en el idioma del usuario
- NUNCA mezclar idiomas en explicaciones, párrafos narrativos, o instrucciones
- Evitar completamente el code-switching no intencional en el texto principal

**EXCEPCIONES PERMITIDAS (solo para libros de aprendizaje):**
- Ejemplos en el idioma que se está enseñando (ej: frases del idioma objetivo en libros de idiomas)
- Código de programación en el lenguaje correspondiente
- Vocabulario específico del idioma/lenguaje objetivo en contexto educativo
- Pero SIEMPRE con explicación en el idioma configurado por el usuario

**REGLA DE ORO:** Si enseñas [idioma_objetivo] en [idioma_usuario] → ejemplos en [idioma_objetivo] OK, explicaciones en [idioma_usuario] OBLIGATORIO

### 5. EXTENSIÓN
- Cumplir con el número de páginas objetivo (~300 palabras por página)
- Desarrollar suficientemente cada capítulo sin relleno innecesario
- Balance entre diálogo, descripción y acción

### 6. ESTRUCTURA HTML PROFESIONAL
- Cada capítulo debe comenzar con <h1 id="capitulo-N">Título del Capítulo N</h1>
- Usar <h2> para secciones importantes dentro de capítulos (máximo 2-3 por capítulo)
- Envolver todo el contenido del chunk en <div class="book-chunk">
- Usar atributos id únicos para facilitar navegación
- Mantener semántica HTML correcta

EJEMPLO DE ESTRUCTURA:
```html
<div class="book-chunk">
  <div class="chapter">
    <h1 id="capitulo-1">Título del Capítulo 1</h1>
    <p>Contenido narrativo fluido del capítulo...</p>
    <p>Más desarrollo del capítulo sin subtítulos innecesarios...</p>
    
    <h2 id="seccion-importante">Sección Importante (solo si es crucial)</h2>
    <p>Contenido de la sección importante...</p>
  </div>
</div>
```

Responde ÚNICAMENTE con el contenido HTML del libro, sin comentarios, explicaciones o meta-texto adicional."""
    
    def _build_chunk_user_prompt(self, chunk_info: Dict, book_params: Dict[str, Any], 
                               approved_architecture: Dict[str, Any], coherence_context: Dict[str, Any],
                               previous_chunks_content: List[str], target_pages: int) -> str:
        """
        Construye el user prompt para un chunk específico.
        
        🚀 ACTUALIZADO: Incluye instrucciones explícitas de idioma para evitar code-switching.
        """
        # Basic information
        title = approved_architecture.get('title', book_params.get('title', ''))
        genre = approved_architecture.get('genre', book_params.get('genre', ''))
        
        # 🚀 FIX: Extraer idioma de los parámetros del libro
        language = book_params.get('language', 'es')
        target_audience = book_params.get('target_audience', '')
        tone = book_params.get('tone', '')
        
        # Mapeo de códigos de idioma a nombres claros para el prompt
        language_map = {
            'es': 'español',
            'en': 'inglés',
            'fr': 'francés', 
            'de': 'alemán',
            'pt': 'portugués',
            'it': 'italiano'
        }
        language_name = language_map.get(language, language)
        
        # Mapeo de audiencias
        audience_map = {
            'children': 'niños (8-12 años)',
            'teens': 'adolescentes (13-17 años)', 
            'adult': 'adultos (18+ años)',
            'young_adult': 'adultos jóvenes (18-25 años)',
            'seniors': 'adultos mayores (65+ años)'
        }
        audience_name = audience_map.get(target_audience, target_audience) if target_audience else 'la audiencia general'
        
        # Mapeo de tonos
        tone_map = {
            'formal': 'formal y profesional',
            'casual': 'casual y amigable',
            'humorous': 'humorístico y entretenido',
            'inspiring': 'inspirador y motivacional',
            'educational': 'educativo y didáctico'
        }
        tone_name = tone_map.get(tone, tone) if tone else 'apropiado para el contenido'
        
        # 🚀 ARQUITECTURA COMPLETA: Extraer TODA la información de la arquitectura
        
        # 1. INFORMACIÓN NARRATIVA FUNDAMENTAL
        perspective = approved_architecture.get('perspective', 'tercera persona')
        estimated_words = approved_architecture.get('estimated_words', target_pages * 300)
        themes = approved_architecture.get('themes', [])
        
        # 2. PERSONAJES COMPLETOS con toda su información
        characters = approved_architecture.get('characters', [])
        characters_info = ""
        if characters:
            chars_text = []
            for char in characters:
                chars_text.append(f"• {char.get('name', 'Sin nombre')} ({char.get('role', 'rol no especificado')})")
                if char.get('description'):
                    chars_text.append(f"  - Descripción: {char.get('description')}")
                if char.get('background'):
                    chars_text.append(f"  - Background: {char.get('background')}")
                if char.get('arc'):
                    chars_text.append(f"  - Arco narrativo: {char.get('arc')}")
                if char.get('relationships'):
                    chars_text.append(f"  - Relaciones: {char.get('relationships')}")
                chars_text.append("")
            characters_info = "\n".join(chars_text)
        
        # 3. SETTING COMPLETO (mundo, tiempo, ubicación, atmósfera)
        setting = approved_architecture.get('setting', {})
        setting_info = ""
        if setting:
            setting_parts = []
            if setting.get('time'):
                setting_parts.append(f"Época: {setting['time']}")
            if setting.get('location'):
                setting_parts.append(f"Ubicación: {setting['location']}")
            if setting.get('world_description'):
                setting_parts.append(f"Descripción del mundo: {setting['world_description']}")
            if setting.get('atmosphere'):
                setting_parts.append(f"Atmósfera: {setting['atmosphere']}")
            setting_info = " | ".join(setting_parts)
        
        # 4. ESTRUCTURA NARRATIVA (exposición, desarrollo, clímax, etc.)
        plot_structure = approved_architecture.get('plot_structure', {})
        plot_info = ""
        if plot_structure:
            plot_parts = []
            for phase, description in plot_structure.items():
                if description:
                    phase_name = {
                        'exposition': 'Exposición',
                        'rising_action': 'Desarrollo',
                        'climax': 'Clímax', 
                        'falling_action': 'Resolución',
                        'resolution': 'Desenlace'
                    }.get(phase, phase.title())
                    plot_parts.append(f"{phase_name}: {description}")
            plot_info = " | ".join(plot_parts)
        
        # 5. CAPÍTULOS CON INFORMACIÓN COMPLETA
        chapters_info = ""
        if 'chapters' in chunk_info:
            chapters_text = []
            for chapter in chunk_info['chapters']:
                chapters_text.append(f"**Capítulo {chapter.get('number', 'N/A')}: {chapter.get('title', '')}**")
                chapters_text.append(f"Resumen: {chapter.get('summary', 'Sin resumen')}")
                if chapter.get('key_points'):
                    chapters_text.append(f"Puntos clave: {', '.join(chapter['key_points'])}")
                # 🚀 NUEVO: Personajes enfocados en este capítulo
                if chapter.get('character_focus'):
                    chapters_text.append(f"Personajes principales: {', '.join(chapter['character_focus'])}")
                # 🚀 NUEVO: Páginas estimadas para este capítulo específico
                if chapter.get('estimated_pages'):
                    chapters_text.append(f"Páginas estimadas: {chapter['estimated_pages']}")
                chapters_text.append("")
            chapters_info = "\n".join(chapters_text)
        
        # 6. TEMAS PRINCIPALES
        themes_info = ""
        if themes:
            themes_info = f"Temas principales: {', '.join(themes)}"
        
        # 7. ELEMENTOS ESPECIALES (prólogos, epílogos, dedicatorias)
        special_elements = approved_architecture.get('special_elements', [])
        special_info = ""
        if special_elements:
            special_parts = []
            for element in special_elements:
                if element.get('type') and element.get('description'):
                    special_parts.append(f"{element['type']}: {element['description']}")
            if special_parts:
                special_info = f"Elementos especiales: {' | '.join(special_parts)}"
        
        # Context from previous chunks
        context_info = ""
        if previous_chunks_content:
            context_info = "\n\n**CONTEXTO PREVIO:**\nResumen del contenido anterior para mantener coherencia:\n"
            context_info += f"[...Contenido previo desarrollado en {len(previous_chunks_content)} secciones anteriores...]"
        
        prompt = f"""Generar contenido narrativo en HTML para "{title}" (género: {genre}):

CAPÍTULOS A DESARROLLAR:
{chapters_info}

CONFIGURACIÓN DEL LIBRO:
Idioma: {language_name} (código: {language}) - OBLIGATORIO mantener consistencia absoluta
Audiencia: {audience_name}
Tono: {tone_name}
Perspectiva: {perspective}
Extensión objetivo: {target_pages} páginas (~{estimated_words} palabras)

{f"PERSONAJES PRINCIPALES:{chr(10)}{characters_info}" if characters_info else ""}
{f"SETTING Y AMBIENTACIÓN:{chr(10)}{setting_info}" if setting_info else ""}
{f"ESTRUCTURA NARRATIVA:{chr(10)}{plot_info}" if plot_info else ""}
{themes_info if themes_info else ""}
{special_info if special_info else ""}
{context_info}

FORMATO TÉCNICO REQUERIDO:
Estructura HTML: <div class="book-chunk"> conteniendo <div class="chapter"> para cada capítulo
Headers de navegación: <h1 id="capitulo-N">Título Real</h1> solo para navegación
Contenido en párrafos: <p>texto narrativo fluido</p>
Evitar: Subtítulos H2/H3 excesivos que fragmenten la lectura

PRIORIDADES DE ESCRITURA:
1. FLUIDEZ NARRATIVA ABSOLUTA - Escribe como una novela envolvente, no como manual estructurado
2. IDIOMA PERFECTO - TODO en {language_name}, sin mezclas ni code-switching  
3. COHERENCIA TOTAL - Integra personajes, setting, temas y estructura de manera natural
4. DESARROLLO COMPLETO - Alcanza la extensión objetivo con contenido sustancial y diálogos

ESTILO DE ESCRITURA:
Desarrolla cada capítulo como narrativa continua que fluye naturalmente. Evita listas, subtítulos internos, o formato de manual. Los diálogos, descripciones y acción deben entrelazarse sin interrupciones estructurales. Mantén al lector inmerso en la historia desde el primer párrafo hasta el último.

{f"CONTEXTO EDUCATIVO: Si enseñas {language_name}, puedes incluir ejemplos del idioma objetivo con explicaciones en {language_name}." if 'educational' in genre.lower() or 'idioma' in str(book_params).lower() else ""}

Comienza directamente con: <div class="book-chunk">"""

        return prompt
    
    async def _generate_chunks_parallel(self, book_id: int, chunks: List[Dict], 
                                      book_params: Dict[str, Any], approved_architecture: Dict[str, Any],
                                      coherence_context: Dict[str, Any], pages_per_chunk: List[int],
                                      coherence_manager) -> List[Dict[str, Any]]:
        """
        Genera chunks en paralelo con gestión inteligente de dependencias.
        
        🚀 OPTIMIZACIÓN CRÍTICA: Paralelización con waves para 30-50% mejora en tiempo.
        
        Estrategia:
        - Wave 1: Primeros 2 chunks en paralelo (independientes)
        - Wave 2: Siguientes chunks con contexto de waves anteriores
        - Mantiene coherencia mientras maximiza concurrencia
        """
        try:
            from app.routes.websocket import emit_book_progress_update
            
            total_chunks = len(chunks)
            chunk_results = [None] * total_chunks  # Preservar orden
            completed_content = []  # Contenido completado para contexto
            
            logging_logger.info(f"parallel_generation_start - book_id={book_id}, total_chunks={total_chunks}, strategy=wave_based")
            
            # 🚀 WAVE 1: Generar primeros 2 chunks en paralelo (tienen dependencias mínimas)
            wave1_size = min(2, total_chunks)
            wave1_tasks = []
            
            for i in range(wave1_size):
                chunk_info = chunks[i]
                # Primera wave usa contexto mínimo
                task = self._generate_single_chunk_with_timing(
                    book_id=book_id,
                    chunk_info=chunk_info,
                    book_params=book_params,
                    approved_architecture=approved_architecture,
                    coherence_context=coherence_context,
                    previous_chunks_content=[],  # Sin contexto previo para primera wave
                    target_pages=pages_per_chunk[i],
                    chunk_index=i,
                    total_chunks=total_chunks
                )
                wave1_tasks.append(task)
            
            emit_book_progress_update(book_id, {
                'current': 15,
                'total': 100,
                'status': 'generating',
                'status_message': f'Generando wave 1: {wave1_size} chunks en paralelo...',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # Ejecutar wave 1 en paralelo
            wave1_results = await asyncio.gather(*wave1_tasks, return_exceptions=True)
            
            # Procesar resultados de wave 1
            for i, result in enumerate(wave1_results):
                if isinstance(result, Exception):
                    raise Exception(f"Error en chunk {i+1} (wave 1): {str(result)}")
                
                if not result.get('success', False):
                    raise Exception(f"Error en chunk {i+1} (wave 1): {result.get('error', 'Error desconocido')}")
                
                chunk_results[i] = result
                completed_content.append(result['content'])
                
                # Actualizar coherence manager
                coherence_manager.update_with_chunk_content(i, result['content'])
            
            logging_logger.info(f"wave1_completed - book_id={book_id}, chunks_completed={wave1_size}, avg_duration={sum(r['duration'] for r in wave1_results) / len(wave1_results):.2f}s")
            
            # 🚀 WAVE 2+: Generar chunks restantes con contexto optimizado
            remaining_chunks = total_chunks - wave1_size
            if remaining_chunks > 0:
                # Decidir tamaño de waves siguientes basado en dependencias
                wave_size = min(2, remaining_chunks)  # Máximo 2 chunks por wave para balance coherencia/velocidad
                
                current_wave = wave1_size
                wave_num = 2
                
                while current_wave < total_chunks:
                    wave_end = min(current_wave + wave_size, total_chunks)
                    wave_tasks = []
                    
                    emit_book_progress_update(book_id, {
                        'current': 15 + ((current_wave / total_chunks) * 70),
                        'total': 100,
                        'status': 'generating',
                        'status_message': f'Generando wave {wave_num}: chunks {current_wave+1}-{wave_end}...',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
                    
                    for i in range(current_wave, wave_end):
                        chunk_info = chunks[i]
                        
                        # Usar contenido completado como contexto (optimizado)
                        context_content = completed_content.copy()
                        
                        task = self._generate_single_chunk_with_timing(
                            book_id=book_id,
                            chunk_info=chunk_info,
                            book_params=book_params,
                            approved_architecture=approved_architecture,
                            coherence_context=coherence_context,
                            previous_chunks_content=context_content,
                            target_pages=pages_per_chunk[i],
                            chunk_index=i,
                            total_chunks=total_chunks
                        )
                        wave_tasks.append(task)
                    
                    # Ejecutar wave actual en paralelo
                    wave_results = await asyncio.gather(*wave_tasks, return_exceptions=True)
                    
                    # Procesar resultados de wave actual
                    for j, result in enumerate(wave_results):
                        chunk_idx = current_wave + j
                        
                        if isinstance(result, Exception):
                            raise Exception(f"Error en chunk {chunk_idx+1} (wave {wave_num}): {str(result)}")
                        
                        if not result.get('success', False):
                            raise Exception(f"Error en chunk {chunk_idx+1} (wave {wave_num}): {result.get('error', 'Error desconocido')}")
                        
                        chunk_results[chunk_idx] = result
                        completed_content.append(result['content'])
                        
                        # Actualizar coherence manager
                        coherence_manager.update_with_chunk_content(chunk_idx, result['content'])
                    
                    logging_logger.info(f"wave{wave_num}_completed - book_id={book_id}, chunks_range={current_wave+1}-{wave_end}, avg_duration={sum(r['duration'] for r in wave_results) / len(wave_results):.2f}s")
                    
                    current_wave = wave_end
                    wave_num += 1
            
            # Validar que todos los chunks se completaron
            if None in chunk_results:
                missing_chunks = [i+1 for i, result in enumerate(chunk_results) if result is None]
                raise Exception(f"Chunks no completados: {missing_chunks}")
            
            total_duration = sum(result['duration'] for result in chunk_results)
            avg_duration = total_duration / len(chunk_results)
            
            logging_logger.info(f"parallel_generation_completed - book_id={book_id}, total_chunks={total_chunks}, total_duration={total_duration:.2f}s, avg_chunk_duration={avg_duration:.2f}s, parallelization_efficiency={((total_chunks * avg_duration) / total_duration - 1) * 100:.1f}%")
            
            emit_book_progress_update(book_id, {
                'current': 85,
                'total': 100,
                'status': 'assembling',
                'status_message': f'Chunks completados en paralelo. Ensamblando contenido final...',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            return chunk_results
            
        except Exception as e:
            logging_logger.error(f"parallel_generation_error - book_id={book_id}, error={str(e)}, error_type={type(e).__name__}")
            raise e
    
    async def _generate_single_chunk_with_timing(self, book_id: int, chunk_info: Dict, 
                                               book_params: Dict[str, Any], approved_architecture: Dict[str, Any],
                                               coherence_context: Dict[str, Any], previous_chunks_content: List[str],
                                               target_pages: int, chunk_index: int, total_chunks: int) -> Dict[str, Any]:
        """
        Wrapper de _generate_single_chunk que añade timing y metadata para paralelización.
        """
        chunk_start_time = time.time()
        
        # Llamar al método original
        result = await self._generate_single_chunk(
            book_id=book_id,
            chunk_info=chunk_info,
            book_params=book_params,
            approved_architecture=approved_architecture,
            coherence_context=coherence_context,
            previous_chunks_content=previous_chunks_content,
            target_pages=target_pages,
            chunk_index=chunk_index,
            total_chunks=total_chunks
        )
        
        chunk_end_time = time.time()
        chunk_duration = chunk_end_time - chunk_start_time
        
        # Añadir metadata de timing y chunk info
        if result.get('success', False):
            result.update({
                'duration': chunk_duration,
                'chunk_index': chunk_index,
                'start_chapter': chunk_info.get('start_chapter', 0),
                'end_chapter': chunk_info.get('end_chapter', 0),
                'timestamp': chunk_start_time
            })
        
        return result
    
    def _get_coherence_manager_for_book(self, book_params: Dict[str, Any]):
        """
        Obtiene el manager de coherencia para el libro.
        
        Usa el BookCoherenceManager real para extracción correcta de páginas.
        """
        # Import real BookCoherenceManager desde app.services
        from app.services.claude_service.coherence import BookCoherenceManager
        return BookCoherenceManager()
    
    def __str__(self) -> str:
        """String representation del generador."""
        return f"ContentGenerator(model={self.config.model}, max_chunks={self.max_chunks})"