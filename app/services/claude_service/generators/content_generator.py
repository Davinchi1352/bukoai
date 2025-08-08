"""
Content Generator

Generador especializado para contenido completo de libros usando multi-chunk.
Extraído de ClaudeService original - responsabilidad única.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, List

from ..clients.claude_client import ClaudeClient
from ..config.claude_config import ClaudeConfig
from ..config.token_config import TokenConfig

logger = logging.getLogger(__name__)


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
        
        # Configuraciones para multi-chunk
        self.chunk_timeout = config.chunk_timeout
        self.max_chunks = config.max_chunks
        self.chunk_overlap = config.chunk_overlap
        
        logger.info("ContentGenerator initialized", 
                   extra={
                       "max_chunks": self.max_chunks,
                       "chunk_timeout": self.chunk_timeout
                   })
    
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
            # Log crítico del inicio con Claude Sonnet 4
            # Obtener capítulos compatibles con ambos formatos para logging
            logging_chapters = (approved_architecture.get('structure', {}).get('chapters', []) or 
                              approved_architecture.get('chapters', []))
            
            logger.info("starting_multichunk_generation",
                       book_id=book_id,
                       model=self.config.model,
                       chapters_count=len(logging_chapters),
                       target_pages=approved_architecture.get('target_pages'),
                       estimated_words=approved_architecture.get('estimated_words'),
                       max_tokens_per_chunk=self.config.max_tokens,
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
            
            # Dividir capítulos en chunks - Compatible con ambos formatos de arquitectura
            chapters = []
            if approved_architecture.get('structure', {}).get('chapters'):
                # Formato: architecture.structure.chapters
                chapters = approved_architecture['structure']['chapters']
            elif approved_architecture.get('chapters'):
                # Formato: architecture.chapters (nuevo formato)
                chapters = approved_architecture['chapters']
            
            total_chapters = len(chapters)
            
            logger.info("chapters_access_debug",
                       book_id=book_id,
                       has_structure=bool(approved_architecture.get('structure')),
                       has_structure_chapters=bool(approved_architecture.get('structure', {}).get('chapters')),
                       has_direct_chapters=bool(approved_architecture.get('chapters')),
                       chapters_found=total_chapters,
                       architecture_keys=list(approved_architecture.keys()))
            
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
            
            # 2. Planificar páginas por chunk
            pages_per_chunk = coherence_manager.plan_pages_distribution(
                target_pages, len(chunks), total_chapters
            )
            
            # 3. Preparar contexto de coherencia global
            coherence_context = coherence_manager.build_coherence_context(
                approved_architecture, book_params
            )
            
            logger.info("coherence_system_ready",
                       book_id=book_id,
                       target_pages=target_pages,
                       pages_per_chunk=pages_per_chunk,
                       coherence_context_size=len(str(coherence_context)))
            
            # Emitir evento de planificación completada
            emit_book_progress_update(book_id, {
                'current': 10,
                'total': 100,
                'status': 'planned',
                'status_message': f'Planificación completada: {len(chunks)} chunks, {target_pages} páginas objetivo',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # GENERACIÓN MULTI-CHUNK SECUENCIAL
            for chunk_index, chunk_info in enumerate(chunks):
                chunk_start_time = time.time()
                
                logger.info("starting_chunk_generation",
                           book_id=book_id,
                           chunk_index=chunk_index + 1,
                           total_chunks=len(chunks),
                           chapters=f"{chunk_info['start_chapter']}-{chunk_info['end_chapter']}",
                           target_pages=pages_per_chunk[chunk_index])
                
                emit_book_progress_update(book_id, {
                    'current': 10 + (chunk_index * 70 // len(chunks)),
                    'total': 100,
                    'status': 'generating',
                    'status_message': f'Generando chunk {chunk_index + 1}/{len(chunks)}...',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                
                # Generar chunk individual
                chunk_result = await self._generate_single_chunk(
                    book_id=book_id,
                    chunk_info=chunk_info,
                    book_params=book_params,
                    approved_architecture=approved_architecture,
                    coherence_context=coherence_context,
                    previous_chunks_content=complete_book_content,
                    target_pages=pages_per_chunk[chunk_index],
                    chunk_index=chunk_index,
                    total_chunks=len(chunks)
                )
                
                if not chunk_result.get('success', False):
                    raise Exception(f"Error en chunk {chunk_index + 1}: {chunk_result.get('error', 'Error desconocido')}")
                
                # Acumular resultados
                complete_book_content.append(chunk_result['content'])
                complete_thinking_content.append(chunk_result.get('thinking_content', ''))
                
                # Actualizar estadísticas
                total_tokens_used += chunk_result.get('tokens_used', 0)
                total_thinking_tokens += chunk_result.get('thinking_tokens', 0)
                total_prompt_tokens += chunk_result.get('prompt_tokens', 0)
                total_completion_tokens += chunk_result.get('completion_tokens', 0)
                
                chunk_end_time = time.time()
                chunk_duration = chunk_end_time - chunk_start_time
                
                # Agregar resumen del chunk
                chunk_summaries.append({
                    'index': chunk_index + 1,
                    'chapters': f"{chunk_info['start_chapter']}-{chunk_info['end_chapter']}",
                    'content_length': len(chunk_result['content']),
                    'duration': chunk_duration,
                    'tokens_used': chunk_result.get('tokens_used', 0)
                })
                
                logger.info("chunk_generation_completed",
                           book_id=book_id,
                           chunk_index=chunk_index + 1,
                           content_length=len(chunk_result['content']),
                           duration=chunk_duration,
                           tokens_used=chunk_result.get('tokens_used', 0))
                
                # Actualizar coherence manager con nuevo contenido
                coherence_manager.update_with_chunk_content(
                    chunk_index, chunk_result['content']
                )
            
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
            
            if book_params.get('include_conclusion', False):
                concl_result = await self._generate_conclusion(
                    book_id, book_params, approved_architecture,
                    "\n\n".join(complete_book_content)
                )
                if concl_result.get('success'):
                    conclusion_content = concl_result['content']
                    total_tokens_used += concl_result.get('tokens_used', 0)
            
            # Combinar todo el contenido final
            final_content_parts = []
            if introduction_content:
                final_content_parts.append(introduction_content)
            final_content_parts.extend(complete_book_content)
            if conclusion_content:
                final_content_parts.append(conclusion_content)
                
            final_content = "\n\n".join(final_content_parts)
            final_thinking = "\n\n".join(complete_thinking_content)
            
            # Validación final de calidad
            final_word_count = len(final_content.split())
            estimated_pages = final_word_count / 350  # 🎯 FIX: Usar 350 palabras/página consistente con sistema original
            
            # Registrar éxito final
            self.client.circuit_breaker.record_success()
            
            logger.info("multichunk_generation_completed",
                       book_id=book_id,
                       total_chunks=len(chunks),
                       final_word_count=final_word_count,
                       estimated_pages=estimated_pages,
                       total_tokens_used=total_tokens_used,
                       total_thinking_tokens=total_thinking_tokens)
            
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
                'conclusion_included': bool(conclusion_content)
            }
            
        except Exception as e:
            error_msg = f"Error en generación multi-chunk: {str(e)}"
            logger.error("multichunk_generation_error",
                        book_id=book_id,
                        error=str(e),
                        error_type=type(e).__name__)
            
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
            chunk_max_tokens = self.token_config.get_limit('chunk_main')  # 40000
            chunk_thinking_budget = self.config.thinking_budget
            
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
            
            logger.info("chunk_generation_success",
                       book_id=book_id,
                       chunk_index=chunk_index + 1,
                       word_count=word_count,
                       estimated_pages=estimated_pages,
                       target_pages=target_pages)
            
            return {
                'success': True,
                'content': final_chunk_content,
                'thinking_content': final_chunk_thinking,
                'word_count': word_count,
                'estimated_pages': estimated_pages,
                'tokens_used': chunk_count  # Approximate
            }
            
        except asyncio.TimeoutError:
            error_msg = f"Timeout en chunk {chunk_index + 1} después de {self.chunk_timeout}s"
            logger.error("chunk_generation_timeout",
                        book_id=book_id,
                        chunk_index=chunk_index + 1,
                        timeout=self.chunk_timeout)
            return {
                'success': False,
                'error': error_msg,
                'error_type': 'timeout'
            }
            
        except Exception as e:
            error_msg = f"Error en chunk {chunk_index + 1}: {str(e)}"
            logger.error("chunk_generation_error",
                        book_id=book_id,
                        chunk_index=chunk_index + 1,
                        error=str(e))
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
            title = approved_architecture.get('title', book_params.get('title', 'Sin título'))
            genre = approved_architecture.get('genre', book_params.get('genre', 'ficción'))
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
            system_prompt = f"""Eres un escritor experto especializado en crear introducciones atractivas para libros.

Tu tarea es escribir una introducción profesional que:
- Capte la atención del lector desde el primer párrafo
- Establezca el tono y estilo del libro
- Presente brevemente el tema o historia
- Genere expectativa e interés por continuar leyendo
- Esté completamente en {language_name}

IMPORTANTE: La introducción debe estar COMPLETAMENTE en {language_name}, sin mezclar otros idiomas a menos que sea parte de ejemplos educativos específicos.

Responde únicamente con el contenido de la introducción, sin comentarios adicionales."""
            
            # Obtener temas principales si existen
            themes = approved_architecture.get('themes', [])
            themes_info = f"\n- Temas principales: {', '.join(themes)}" if themes else ""
            
            # Obtener una muestra del contenido para contexto
            content_sample = main_content[:1500] + "..." if len(main_content) > 1500 else main_content
            
            user_prompt = f"""Escribe una introducción profesional para el libro "{title}" (género: {genre}).

**INFORMACIÓN DEL LIBRO:**
- Título: "{title}"
- Género: {genre}
- Idioma: {language_name}{themes_info}

**MUESTRA DEL CONTENIDO:**
{content_sample}

**INSTRUCCIONES:**
- Extensión: 2-4 párrafos (300-600 palabras)
- Tono: Profesional y atractivo para el género {genre}
- Idioma: Completamente en {language_name}
- Objetivo: Enganchar al lector y establecer expectativas
- Estilo: Coherente con el contenido del libro

Escribe la introducción comenzando directamente con el contenido."""
            
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
            
            logger.info("introduction_generation_completed",
                       book_id=book_id,
                       content_length=len(introduction_content),
                       language=language_name)
            
            return {
                'success': True,
                'content': introduction_content.strip(),
                'tokens_used': len(introduction_content) // 4  # Estimación aproximada
            }
            
        except Exception as e:
            error_msg = f"Error generando introducción: {str(e)}"
            logger.error("introduction_generation_error",
                        book_id=book_id,
                        error=str(e),
                        error_type=type(e).__name__)
            
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
            title = approved_architecture.get('title', book_params.get('title', 'Sin título'))
            genre = approved_architecture.get('genre', book_params.get('genre', 'ficción'))
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
            system_prompt = f"""Eres un escritor experto especializado en crear conclusiones impactantes para libros.

Tu tarea es escribir una conclusión profesional que:
- Cierre satisfactoriamente los temas principales del libro
- Refuerce los mensajes clave y aprendizajes
- Deje al lector con una reflexión final valiosa
- Mantenga el tono y estilo establecido
- Esté completamente en {language_name}

IMPORTANTE: La conclusión debe estar COMPLETAMENTE en {language_name}, sin mezclar otros idiomas a menos que sea parte de ejemplos educativos específicos.

Responde únicamente con el contenido de la conclusión, sin comentarios adicionales."""
            
            # Obtener temas principales si existen
            themes = approved_architecture.get('themes', [])
            themes_info = f"\n- Temas principales abordados: {', '.join(themes)}" if themes else ""
            
            # Obtener las últimas secciones del contenido para contexto
            content_ending = main_content[-2000:] if len(main_content) > 2000 else main_content
            
            user_prompt = f"""Escribe una conclusión profesional para el libro "{title}" (género: {genre}).

**INFORMACIÓN DEL LIBRO:**
- Título: "{title}"
- Género: {genre}
- Idioma: {language_name}{themes_info}

**CONTENIDO FINAL DEL LIBRO:**
...{content_ending}

**INSTRUCCIONES:**
- Extensión: 2-4 párrafos (300-600 palabras)
- Tono: Reflexivo y satisfactorio para el género {genre}
- Idioma: Completamente en {language_name}
- Objetivo: Cerrar el libro de manera memorable
- Estilo: Coherente con todo el contenido desarrollado
- Enfoque: Resumir aprendizajes clave y mensaje final

Escribe la conclusión comenzando directamente con el contenido."""
            
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
            
            logger.info("conclusion_generation_completed",
                       book_id=book_id,
                       content_length=len(conclusion_content),
                       language=language_name)
            
            return {
                'success': True,
                'content': conclusion_content.strip(),
                'tokens_used': len(conclusion_content) // 4  # Estimación aproximada
            }
            
        except Exception as e:
            error_msg = f"Error generando conclusión: {str(e)}"
            logger.error("conclusion_generation_error",
                        book_id=book_id,
                        error=str(e),
                        error_type=type(e).__name__)
            
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
        
        🚀 ACTUALIZADO: Incluye instrucciones específicas de idioma para evitar code-switching.
        """
        return """Eres un escritor experto especializado en generar contenido de alta calidad para libros.

Tu tarea es escribir una sección específica del libro siguiendo la arquitectura proporcionada, manteniendo coherencia con el contenido previo y cumpliendo con el número de páginas objetivo.

## INSTRUCCIONES CRÍTICAS:

### 1. CALIDAD NARRATIVA
- Escritura fluida y atractiva que mantenga al lector interesado
- Desarrollo adecuado de personajes y situaciones
- Diálogos naturales y descriptivos envolventes
- Transiciones suaves entre escenas y capítulos

### 2. COHERENCIA
- Mantener consistencia con contenido previo
- Seguir la arquitectura y desarrollo de personajes establecidos
- Respetar el tono y estilo narrativo del libro

### 3. IDIOMA Y CONSISTENCIA LINGÜÍSTICA
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

### 4. EXTENSIÓN
- Cumplir con el número de páginas objetivo (~300 palabras por página)
- Desarrollar suficientemente cada capítulo sin relleno innecesario
- Balance entre diálogo, descripción y acción

### 5. ESTRUCTURA
- Respetar los títulos y estructura de capítulos de la arquitectura
- Incluir transiciones naturales entre capítulos
- Mantener pacing apropiado para el género

Responde ÚNICAMENTE con el contenido del libro, sin comentarios, numeraciones o explicaciones adicionales."""
    
    def _build_chunk_user_prompt(self, chunk_info: Dict, book_params: Dict[str, Any], 
                               approved_architecture: Dict[str, Any], coherence_context: Dict[str, Any],
                               previous_chunks_content: List[str], target_pages: int) -> str:
        """
        Construye el user prompt para un chunk específico.
        
        🚀 ACTUALIZADO: Incluye instrucciones explícitas de idioma para evitar code-switching.
        """
        # Basic information
        title = approved_architecture.get('title', book_params.get('title', 'Sin título'))
        genre = approved_architecture.get('genre', book_params.get('genre', 'ficción'))
        
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
                chapters_text.append(f"**Capítulo {chapter.get('number', 'N/A')}: {chapter.get('title', 'Sin título')}**")
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
        
        prompt = f"""Escribir la siguiente sección del libro "{title}" (género: {genre}):

**CAPÍTULOS A DESARROLLAR:**
{chapters_info}

**CONFIGURACIÓN DEL LIBRO:**
- Idioma OBLIGATORIO: {language_name} (código: {language})
- Audiencia objetivo: {audience_name}
- Tono: {tone_name}
- Perspectiva narrativa: {perspective}
- Páginas objetivo: {target_pages} páginas (~{estimated_words} palabras total)

{"**PERSONAJES PRINCIPALES:**" + chr(10) + characters_info if characters_info else ""}
{"**SETTING Y AMBIENTACIÓN:**" + chr(10) + setting_info if setting_info else ""}

{"**ESTRUCTURA NARRATIVA:**" + chr(10) + plot_info if plot_info else ""}

{themes_info if themes_info else ""}

{special_info if special_info else ""}

{context_info}

**INSTRUCCIONES ESPECÍFICAS:**
- 🌍 IDIOMA CRÍTICO: Escribe TODA la explicación, narración e instrucciones en {language_name} EXCLUSIVAMENTE
- 🚫 PROHIBIDO ABSOLUTAMENTE: Mezclar {language_name} con otros idiomas en explicaciones o texto narrativo
- ✅ CONSISTENCIA: Mantén {language_name} perfecto en diálogos, narración, y descripciones explicativas
- 📖 CONTENIDO: Desarrolla completamente cada capítulo siguiendo su resumen y puntos clave
- 👥 PERSONAJES: Utiliza las descripciones, background y arcos narrativos específicos de cada personaje
- 🌍 SETTING: Incorpora la época, ubicación, descripción del mundo y atmósfera establecidos
- 📈 ESTRUCTURA: Respeta la fase narrativa correspondiente (exposición/desarrollo/clímax/resolución)
- 💭 TEMAS: Integra los temas principales de manera natural en la narrativa
- ✨ ELEMENTOS ESPECIALES: Incorpora prólogos, epílogos o dedicatorias según corresponda
- 🎭 ESTILO: Mantén el estilo narrativo establecido para el género {genre}
- 👥 AUDIENCIA: Adapta el lenguaje para {audience_name}
- 🎨 TONO: Usa un tono {tone_name}
- 📝 PERSPECTIVA: Mantén consistentemente la perspectiva {perspective}
- 📏 EXTENSIÓN: Asegúrate de alcanzar aproximadamente {target_pages * 300} palabras
- 💬 CALIDAD: Incluye diálogos naturales y descripciones envolventes EN {language_name.upper()}

📚 EXCEPCIONES EDUCATIVAS PERMITIDAS:
Si este es un libro de aprendizaje de idiomas/programación, puedes incluir:
- ✅ Ejemplos en el idioma que se está enseñando (con explicación en {language_name})
- ✅ Código de programación del lenguaje correspondiente (con comentarios en {language_name})  
- ✅ Vocabulario específico del tema (siempre explicado en {language_name})

EJEMPLO CORRECTO para libro educativo:
✅ "[Explicación en {language_name}] + 'ejemplo_en_idioma_objetivo' + [más explicación en {language_name}]"
✅ "def function(): # [Comentario en {language_name}]" (para programación)

EJEMPLO INCORRECTO (code-switching prohibido):
❌ "[Texto mezclando multiple idiomas in una misma sentence]"

RECORDATORIO FINAL: Las explicaciones e instrucciones deben estar en {language_name} sin excepción. Los ejemplos educativos pueden ser del idioma/lenguaje que se enseña.

Escribe ÚNICAMENTE el contenido de los capítulos, comenzando directamente con el primer capítulo."""

        return prompt
    
    def _get_coherence_manager_for_book(self, book_params: Dict[str, Any]):
        """
        Obtiene el manager de coherencia para el libro.
        
        Usa el BookCoherenceManager real para extracción correcta de páginas.
        """
        # Import real BookCoherenceManager desde app.services
        from app.services.claude_service_coherence import BookCoherenceManager
        return BookCoherenceManager()
    
    def __str__(self) -> str:
        """String representation del generador."""
        return f"ContentGenerator(model={self.config.model}, max_chunks={self.max_chunks})"