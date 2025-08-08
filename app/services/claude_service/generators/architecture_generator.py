"""
Architecture Generator

Generador especializado para arquitecturas de libros.
Extraído de ClaudeService original - responsabilidad única.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any

from ..clients.claude_client import ClaudeClient
from ..config.claude_config import ClaudeConfig
from ..config.token_config import TokenConfig

logger = logging.getLogger(__name__)


class ArchitectureGenerator:
    """
    Generador especializado para arquitecturas de libros.
    
    Extrae la lógica de generación de arquitectura que estaba en ClaudeService
    (líneas 197-586 + métodos helper).
    """
    
    def __init__(self, config: ClaudeConfig, claude_client: ClaudeClient):
        """
        Inicializa el generador de arquitectura.
        
        Args:
            config: Configuración de Claude
            claude_client: Cliente Claude configurado
        """
        self.config = config
        self.client = claude_client
        self.token_config = TokenConfig()
        
        # Configuraciones específicas para arquitectura
        self.architecture_timeout = config.architecture_timeout
        self.progress_check_interval = config.progress_check_interval
        
        logger.info("ArchitectureGenerator initialized", 
                   extra={"timeout": self.architecture_timeout})
    
    async def generate_book_architecture(self, book_id: int, book_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera únicamente la arquitectura del libro (estructura, capítulos, personajes, etc.)
        para que el usuario pueda revisar y aprobar antes de la generación completa.
        
        Extraído de ClaudeService.generate_book_architecture() líneas 197-586.
        
        Args:
            book_id: ID del libro
            book_params: Parámetros del libro
            
        Returns:
            Resultado con la arquitectura generada
        """
        try:
            # Iniciar tracking de generación
            from app.tracking.analytics import track_book_generation_start
            track_book_generation_start(book_id, book_params.get('user_id', 0), 
                                       'architecture', book_params)
            
            # Preparar el prompt específico para arquitectura
            prompt_data = self._build_architecture_messages(book_params)
            
            # Extract system prompt and messages separately for new Claude API format
            system_prompt = prompt_data["system"]
            messages = prompt_data["messages"]
            
            # Track inicio de llamada a Claude API
            api_start_time = time.time()
            
            # Variables para acumular respuesta
            full_content = []
            thinking_content = []
            chunk_count = 0
            
            # Emisión de evento de inicio
            from app.routes.websocket import emit_book_progress_update, emit_generation_log
            
            emit_book_progress_update(book_id, {
                'current': self.config.progress_connecting,
                'total': 100,
                'status': 'connecting',
                'status_message': 'Conectando con Claude AI para generar arquitectura...',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # 🚀 OPTIMIZACIÓN: Tokens específicos optimizados para arquitectura
            arch_max_tokens = self.token_config.get_limit('architecture')  # 12000 optimizado
            arch_budget_tokens = self.config.thinking_budget  # Budget default
            
            logger.info("starting_architecture_stream",
                       book_id=book_id,
                       max_tokens=arch_max_tokens,
                       thinking_budget=arch_budget_tokens,
                       timeout=self.architecture_timeout)
            
            # Usar timeout generoso pero efectivo para arquitectura de calidad
            async with asyncio.timeout(self.architecture_timeout):
                async with self.client.client.messages.stream(
                    model=self.config.model,
                    max_tokens=arch_max_tokens,
                    temperature=self.config.temperature,
                    system=system_prompt,  # Use separate system parameter for new Claude API
                    messages=messages,
                    thinking={
                        "type": "enabled",
                        "budget_tokens": arch_budget_tokens
                    },
                ) as stream:
                    
                    emit_book_progress_update(book_id, {
                        'current': self.config.progress_thinking,
                        'total': 100,
                        'status': 'thinking',
                        'status_message': 'Claude está diseñando la arquitectura de tu libro...',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
                    
                    current_block_index = None
                    
                    async for event in stream:
                        chunk_count += 1
                        
                        # Debug: Log todos los tipos de eventos para investigar thinking_delta
                        if hasattr(event, 'type'):
                            if 'thinking' in str(event.type).lower() or chunk_count <= 5:  # Log thinking events + primeros 5
                                logger.info("stream_event_debug", 
                                           book_id=book_id,
                                           event_type=event.type,
                                           chunk_count=chunk_count,
                                           has_delta=hasattr(event, 'delta'),
                                           event_attributes=list(vars(event).keys()) if hasattr(event, '__dict__') else [])
                        
                        # Actualizar progreso optimizado para 10K usuarios (menos overhead)
                        if chunk_count % self.progress_check_interval == 0:
                            self._update_progress(book_id, "architecture_generation", 
                                                f"Procesando chunk {chunk_count}")
                        
                        # Thinking blocks
                        if event.type == "content_block_start" and hasattr(event, 'content_block') and event.content_block.type == "thinking":
                            current_block_index = event.index
                        
                        if event.type == "content_block_delta" and hasattr(event, 'delta'):
                            if current_block_index is not None and hasattr(event.delta, 'text'):
                                thinking_content.append(event.delta.text)
                        
                        if event.type == "content_block_stop" and hasattr(event, 'index'):
                            if event.index == current_block_index:
                                current_block_index = None
                        
                        # Regular content
                        if event.type == "content_block_delta" and hasattr(event, 'delta'):
                            if current_block_index is None and hasattr(event.delta, 'text'):
                                full_content.append(event.delta.text)
                                
                                # Update progress más granular para arquitectura
                                if len(full_content) % self.config.progress_update_frequency == 0:
                                    progress = min(
                                        self.config.progress_start + (len(full_content) // self.config.progress_divider), 
                                        self.config.progress_max
                                    )
                                    emit_book_progress_update(book_id, {
                                        'current': progress,
                                        'total': 100,
                                        'status': 'generating',
                                        'status_message': f'Generando arquitectura... {len(full_content)} fragmentos',
                                        'timestamp': datetime.now(timezone.utc).isoformat()
                                    })
            
            # Combinar contenido
            complete_content = "".join(full_content)
            complete_thinking = "".join(thinking_content)
            
            # API call time
            api_end_time = time.time()
            api_duration = api_end_time - api_start_time
            
            # Validar que tenemos contenido útil
            if len(complete_content.strip()) < self.config.min_content_length:
                raise Exception(f"La arquitectura generada es demasiado corta (mínimo {self.config.min_content_length} caracteres)")
            
            # Registrar éxito en circuit breaker
            self.client.circuit_breaker.record_success()
            
            logger.info("architecture_generation_completed",
                       book_id=book_id,
                       content_length=len(complete_content),
                       thinking_length=len(complete_thinking),
                       api_duration=api_duration,
                       chunk_count=chunk_count)
            
            emit_book_progress_update(book_id, {
                'current': self.config.progress_processing,
                'total': 100,
                'status': 'processing',
                'status_message': 'Procesando arquitectura generada...',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # Tracking de finalización
            from app.tracking.analytics import track_book_generation_end
            track_book_generation_end(book_id, book_params.get('user_id', 0), 
                                     'architecture', api_duration, len(complete_content))
            
            emit_book_progress_update(book_id, {
                'current': self.config.progress_completed,
                'total': 100,
                'status': 'completed',
                'status_message': 'Arquitectura generada exitosamente',
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            return {
                'success': True,
                'architecture': complete_content,
                'thinking_content': complete_thinking,
                'api_duration': api_duration,
                'content_length': len(complete_content),
                'thinking_length': len(complete_thinking),
                'chunk_count': chunk_count
            }
            
        except asyncio.TimeoutError:
            error_msg = f"Timeout generando arquitectura después de {self.architecture_timeout}s"
            logger.error("architecture_generation_timeout", 
                        book_id=book_id,
                        timeout=self.architecture_timeout)
            
            # Registrar error en circuit breaker
            self.client.circuit_breaker.record_failure(Exception(error_msg))
            
            return {
                'success': False,
                'error': error_msg,
                'error_type': 'timeout'
            }
            
        except Exception as e:
            error_msg = f"Error generando arquitectura: {str(e)}"
            logger.error("architecture_generation_error",
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
    
    def _build_architecture_messages(self, book_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construye los mensajes para generación de arquitectura.
        
        Extraído de ClaudeService._build_architecture_messages() líneas 587-609.
        
        Args:
            book_params: Parámetros del libro
            
        Returns:
            Diccionario con system prompt y messages
        """
        return {
            "system": self._build_architecture_system_prompt(),
            "messages": [
                {
                    "role": "user",
                    "content": self._build_architecture_user_prompt(book_params)
                }
            ]
        }
    
    def _build_architecture_system_prompt(self) -> str:
        """
        Construye el system prompt para generación de arquitectura.
        
        Extraído de ClaudeService._build_architecture_system_prompt() líneas 610-711.
        
        Returns:
            System prompt para arquitectura
        """
        return """Eres un arquitecto experto de libros que diseña estructuras detalladas y completas para libros de cualquier género.

Tu trabajo es crear una arquitectura completa y bien estructurada que sirva como blueprint perfecto para la generación posterior del contenido.

## INSTRUCCIONES CRÍTICAS:

### 1. FORMATO DE RESPUESTA OBLIGATORIO
Debes responder EXACTAMENTE con este formato JSON válido (sin markdown, sin comentarios):

{
  "title": "Título definitivo del libro",
  "genre": "género_específico",
  "target_audience": "audiencia_objetivo",
  "target_pages": número_páginas_estimadas,
  "estimated_words": número_palabras_estimadas,
  "tone": "tono_narrativo",
  "perspective": "perspectiva_narrativa",
  "chapters": [
    {
      "number": 1,
      "title": "Título del capítulo",
      "summary": "Resumen detallado de lo que sucede en el capítulo",
      "key_points": ["punto_clave_1", "punto_clave_2"],
      "estimated_pages": páginas_estimadas,
      "character_focus": ["personaje_principal", "personaje_secundario"]
    }
  ],
  "characters": [
    {
      "name": "Nombre del personaje",
      "role": "protagonista/antagonista/secundario",
      "description": "Descripción física y psicológica detallada",
      "background": "Historia personal y motivaciones",
      "arc": "Evolución del personaje a través de la historia",
      "relationships": "Relaciones con otros personajes"
    }
  ],
  "setting": {
    "time": "época_temporal",
    "location": "ubicación_geográfica",
    "world_description": "Descripción detallada del mundo/ambiente",
    "atmosphere": "Atmósfera y mood general"
  },
  "themes": ["tema_principal", "tema_secundario"],
  "plot_structure": {
    "exposition": "Planteamiento inicial",
    "rising_action": "Desarrollo y complicaciones",
    "climax": "Punto álgido de la historia",
    "falling_action": "Resolución de conflictos",
    "resolution": "Desenlace final"
  },
  "special_elements": [
    {
      "type": "prólogo/epílogo/dedicatoria",
      "title": "título_elemento",
      "description": "qué_incluye"
    }
  ]
}

### 2. ESPECIFICACIONES TÉCNICAS:
- **Páginas objetivo**: Siempre cumple el número de páginas solicitado por el usuario
- **Capítulos**: Entre {self.config.min_chapters}-{self.config.max_chapters} capítulos dependiendo del género y extensión
- **Estimación palabras**: ~{self.config.min_words_per_page}-{self.config.max_words_per_page} palabras por página
- **Balance**: Distribución equilibrada de contenido entre capítulos
- **Coherencia**: Todos los elementos deben estar interconectados

### 3. CALIDAD NARRATIVA:
- Personajes tridimensionales con arcos de desarrollo
- Estructura narrativa sólida con inicio, desarrollo y cierre satisfactorio
- Temas profundos y relevantes para el género
- Conflictos bien definidos y resoluciones convincentes
- Pacing adecuado para mantener el interés

### 4. GENRES ESPECÍFICOS - ADAPTACIONES:
- **Ficción**: Énfasis en personajes y conflictos emocionales
- **Fantasía/Sci-Fi**: Worldbuilding detallado, sistemas mágicos/tecnológicos
- **Misterio/Thriller**: Estructura de pistas, red herrings, revelaciones
- **Romance**: Desarrollo de relación, tensión romántica, resolución satisfactoria
- **No-ficción**: Estructura lógica, puntos de aprendizaje, casos prácticos
- **Biografía**: Cronología vital, momentos clave, impacto histórico

Recuerda: Tu arquitectura será la base para generar todo el contenido. Debe ser completa, detallada y profesional."""
    
    def _build_architecture_user_prompt(self, book_params: Dict[str, Any]) -> str:
        """
        Construye el user prompt para generación de arquitectura.
        
        🚀 ACTUALIZADO: Incluye TODOS los campos configurados por el usuario.
        
        Args:
            book_params: Parámetros del libro
            
        Returns:
            User prompt para arquitectura
        """
        # Extraer TODOS los parámetros del usuario
        title = book_params.get('title', 'Sin título')
        genre = book_params.get('genre', 'ficción')
        description = book_params.get('description', '')
        target_audience = book_params.get('target_audience', '')
        tone = book_params.get('tone', '')
        language = book_params.get('language', 'es')
        chapter_count = book_params.get('chapter_count', 10)
        page_count = book_params.get('page_count', self.config.default_target_pages)
        target_pages = book_params.get('target_pages', page_count)  # Usar page_count si no hay target_pages
        writing_style = book_params.get('writing_style', 'profesional')
        additional_instructions = book_params.get('additional_instructions', '')
        
        # Procesar key_topics (fix: no iterar string como lista)
        key_topics = book_params.get('key_topics', '')
        topics_text = ""
        if key_topics and isinstance(key_topics, str) and key_topics.strip():
            # Si key_topics es un string (como description), usarlo como tema principal
            topics_text = f"\n\n**Temas clave a incluir:**\n- {key_topics.strip()}"
        elif key_topics and isinstance(key_topics, list) and len(key_topics) > 0:
            # Si es una lista real de topics
            topics_list = [f"- {topic}" for topic in key_topics if topic and str(topic).strip()]
            if topics_list:
                topics_text = f"\n\n**Temas clave a incluir:**\n" + "\n".join(topics_list)
        
        # Construir requisitos adicionales
        requirements_text = ""
        if additional_instructions and additional_instructions.strip():
            requirements_text = f"\n\n**Requisitos adicionales:**\n{additional_instructions.strip()}"
        
        # Mapeo de audiencias y tonos para mejor contexto
        audience_context = ""
        if target_audience:
            audience_map = {
                'children': 'niños (8-12 años)',
                'teens': 'adolescentes (13-17 años)', 
                'adult': 'adultos (18+ años)',
                'young_adult': 'adultos jóvenes (18-25 años)',
                'seniors': 'adultos mayores (65+ años)'
            }
            audience_context = f"\n- Audiencia objetivo: {audience_map.get(target_audience, target_audience)}"
        
        tone_context = ""
        if tone:
            tone_map = {
                'formal': 'tono formal y profesional',
                'casual': 'tono casual y amigable',
                'humorous': 'tono humorístico y entretenido',
                'inspiring': 'tono inspirador y motivacional',
                'educational': 'tono educativo y didáctico'
            }
            tone_context = f"\n- Tono narrativo: {tone_map.get(tone, tone)}"
        
        language_context = ""
        if language:
            language_map = {
                'es': 'español',
                'en': 'inglés', 
                'fr': 'francés',
                'de': 'alemán',
                'pt': 'portugués'
            }
            language_context = f"\n- Idioma: {language_map.get(language, language)}"
        
        prompt = f"""Diseña la arquitectura completa para el siguiente libro:

**Información básica:**
- Título: "{title}"
- Género: {genre}
- Páginas objetivo: {target_pages} páginas
- Capítulos planificados: {chapter_count} capítulos
- Estilo de escritura: {writing_style}{audience_context}{tone_context}{language_context}

**Descripción del libro:**
{description}

{topics_text}

{requirements_text}

**INSTRUCCIONES ESPECÍFICAS:**

1. **Estructura de capítulos**: Crea exactamente {chapter_count} capítulos como solicitó el usuario
2. **Páginas por capítulo**: Distribuye las {target_pages} páginas de manera equilibrada entre los {chapter_count} capítulos
3. **Audiencia y tono**: Adapta el contenido para {target_audience if target_audience else 'la audiencia general'} con {tone if tone else 'el tono apropiado'}
4. **Personajes**: Desarrolla personajes apropiados para el género {genre}
5. **Coherencia**: Asegúrate de que todos los elementos estén interconectados
6. **Idioma**: El contenido debe estar completamente en {language_map.get(language, language) if language else 'el idioma especificado'}

**CALIDAD REQUERIDA:**
- Arquitectura profesional que rivalice con bestsellers publicados
- Personajes apropiados para {target_audience if target_audience else 'la audiencia objetivo'}
- Estructura narrativa con {tone if tone else 'tono apropiado'} y pacing adecuado
- Temas profundos y relevantes para el género {genre}
- Detalles suficientes para generar {target_pages} páginas de contenido de calidad
- Contenido completamente en {language_map.get(language, language) if language else 'el idioma solicitado'}

Responde ÚNICAMENTE con el JSON de arquitectura, sin explicaciones adicionales."""

        return prompt
    
    def _update_progress(self, book_id: int, operation: str, details: str = None):
        """
        Actualiza el progreso de la operación.
        
        Extraído de ClaudeService._update_progress().
        
        Args:
            book_id: ID del libro
            operation: Nombre de la operación
            details: Detalles adicionales
        """
        try:
            from app.routes.websocket import emit_generation_log
            emit_generation_log(book_id, f"[{operation}] {details or 'En progreso...'}")
        except Exception as e:
            # No fallar por errores de WebSocket
            logger.debug(f"WebSocket progress update failed: {e}")
    
    def __str__(self) -> str:
        """String representation del generador."""
        return f"ArchitectureGenerator(model={self.config.model}, timeout={self.architecture_timeout})"