"""
Dynamic Content Generator for Professional Formatting
Genera contenido dinámico para elementos profesionales de ebooks usando Claude AI.

SEGURIDAD: Este módulo es INDEPENDIENTE del sistema de generación de libros.
Solo se usa en formateo profesional que está actualmente DESHABILITADO.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ContentGenerationParams:
    """Parámetros para generación de contenido dinámico."""
    title: str
    genre: str
    language: str
    target_audience: str
    author_name: str
    key_topics: Optional[str] = None
    tone: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para usar en prompts."""
        return {
            'title': self.title,
            'genre': self.genre,
            'language': self.language,
            'target_audience': self.target_audience,
            'author_name': self.author_name,
            'key_topics': self.key_topics or '',
            'tone': self.tone or 'professional'
        }


class DynamicContentGenerator:
    """
    Generador de contenido dinámico para elementos profesionales.
    
    IMPORTANTE: Este servicio es INDEPENDIENTE de la generación de libros.
    Solo se usa en formateo profesional opcional.
    """
    
    def __init__(self):
        """Inicializa el generador de contenido dinámico."""
        # Mapeo de idiomas para prompts
        self.language_names = {
            'es': 'español',
            'en': 'inglés', 
            'de': 'alemán',
            'fr': 'francés',
            'pt': 'portugués',
            'it': 'italiano'
        }
        
        # Mapeo de géneros para contexto
        self.genre_contexts = {
            'educational': 'educativo',
            'technical': 'técnico',
            'fiction': 'ficción',
            'non_fiction': 'no ficción',
            'biography': 'biográfico',
            'self_help': 'autoayuda',
            'business': 'empresarial',
            'academic': 'académico'
        }
    
    async def generate_dedication(self, params: ContentGenerationParams, architecture: Dict[str, Any] = None) -> str:
        """
        Genera una dedicatoria personalizada usando Claude AI y la arquitectura del libro.
        
        Args:
            params: Parámetros del libro para personalización
            architecture: Arquitectura completa del libro generada por Claude
            
        Returns:
            HTML de la dedicatoria personalizada
        """
        try:
            # Obtener servicio Claude (de forma segura)
            claude_service = self._get_claude_service()
            if not claude_service:
                return self._get_fallback_dedication(params)
            
            system_prompt = self._build_dedication_system_prompt()
            user_prompt = self._build_dedication_user_prompt_with_architecture(params, architecture)
            
            # Generar contenido con Claude usando el método correcto del servicio
            result = await self._call_claude_api(
                claude_service=claude_service,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=1000
            )
            
            if result.get('success') and result.get('content'):
                return self._wrap_dedication_html(result['content'])
            else:
                logger.warning("Claude dedication generation failed, using fallback")
                return self._get_fallback_dedication(params)
                
        except Exception as e:
            logger.error(f"Error generating dedication: {str(e)}")
            return self._get_fallback_dedication(params)
    
    async def generate_prologue(self, params: ContentGenerationParams, architecture: Dict[str, Any] = None) -> str:
        """
        Genera un prólogo personalizado usando Claude AI y la arquitectura del libro.
        
        Args:
            params: Parámetros del libro
            architecture: Arquitectura completa del libro
            
        Returns:
            HTML del prólogo personalizado
        """
        try:
            claude_service = self._get_claude_service()
            if not claude_service:
                return self._get_fallback_prologue(params)
            
            system_prompt = self._build_prologue_system_prompt()
            user_prompt = self._build_prologue_user_prompt_with_architecture(params, architecture)
            
            result = await self._call_claude_api(
                claude_service=claude_service,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=2000
            )
            
            if result.get('success') and result.get('content'):
                return self._wrap_prologue_html(result['content'])
            else:
                return self._get_fallback_prologue(params)
                
        except Exception as e:
            logger.error(f"Error generating prologue: {str(e)}")
            return self._get_fallback_prologue(params)
    
    async def generate_epilogue(self, params: ContentGenerationParams, architecture: Dict[str, Any] = None) -> str:
        """Genera un epílogo personalizado usando la arquitectura del libro."""
        try:
            claude_service = self._get_claude_service()
            if not claude_service:
                return self._get_fallback_epilogue(params)
            
            system_prompt = self._build_epilogue_system_prompt()
            user_prompt = self._build_epilogue_user_prompt_with_architecture(params, architecture)
            
            result = await self._call_claude_api(
                claude_service=claude_service,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=1500
            )
            
            if result.get('success') and result.get('content'):
                return self._wrap_epilogue_html(result['content'])
            else:
                return self._get_fallback_epilogue(params)
                
        except Exception as e:
            logger.error(f"Error generating epilogue: {str(e)}")
            return self._get_fallback_epilogue(params)
    
    async def generate_acknowledgments(self, params: ContentGenerationParams, architecture: Dict[str, Any] = None) -> str:
        """Genera agradecimientos personalizados usando la arquitectura del libro."""
        try:
            claude_service = self._get_claude_service()
            if not claude_service:
                return self._get_fallback_acknowledgments(params)
            
            system_prompt = self._build_acknowledgments_system_prompt()
            user_prompt = self._build_acknowledgments_user_prompt_with_architecture(params, architecture)
            
            result = await self._call_claude_api(
                claude_service=claude_service,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=1200
            )
            
            if result.get('success') and result.get('content'):
                return self._wrap_acknowledgments_html(result['content'])
            else:
                return self._get_fallback_acknowledgments(params)
                
        except Exception as e:
            logger.error(f"Error generating acknowledgments: {str(e)}")
            return self._get_fallback_acknowledgments(params)
    
    async def generate_about_author(self, params: ContentGenerationParams, architecture: Dict[str, Any] = None) -> str:
        """Genera página 'Acerca del Autor' personalizada usando la arquitectura del libro."""
        try:
            claude_service = self._get_claude_service()
            if not claude_service:
                return self._get_fallback_about_author(params)
            
            system_prompt = self._build_about_author_system_prompt()
            user_prompt = self._build_about_author_user_prompt_with_architecture(params, architecture)
            
            result = await self._call_claude_api(
                claude_service=claude_service,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=1000
            )
            
            if result.get('success') and result.get('content'):
                return self._wrap_about_author_html(result['content'])
            else:
                return self._get_fallback_about_author(params)
                
        except Exception as e:
            logger.error(f"Error generating about author: {str(e)}")
            return self._get_fallback_about_author(params)
    
    # ================================
    # SYSTEM PROMPTS PARA CLAUDE AI
    # ================================
    
    def _build_dedication_system_prompt(self) -> str:
        """Construye el system prompt para dedicatorias."""
        return """Eres un escritor profesional especializado en crear dedicatorias elegantes y personalizadas para libros.

Tu tarea es crear una dedicatoria profesional que sea:
1. APROPIADA para el tema y género del libro
2. PERSONALIZADA según el idioma y audiencia
3. ELEGANTE y profesional en tono
4. ESPECÍFICA al contenido del libro (no genérica)
5. BREVE pero significativa (2-4 párrafos máximo)

REGLAS:
- Escribe ÚNICAMENTE en el idioma especificado por el usuario
- NO uses frases genéricas como "Este libro está dedicado..."
- SÍ crea dedicatorias específicas al tema del libro
- Mantén un tono profesional pero cálido
- NO incluyas HTML tags, solo el texto

Responde únicamente con el texto de la dedicatoria, sin explicaciones adicionales."""
    
    def _build_dedication_user_prompt_with_architecture(self, params: ContentGenerationParams, architecture: Dict[str, Any] = None) -> str:
        """Construye el user prompt para dedicatorias usando la arquitectura del libro."""
        language_name = self.language_names.get(params.language, params.language)
        genre_name = self.genre_contexts.get(params.genre, params.genre)
        
        # Extraer información rica de la arquitectura si está disponible
        architecture_context = ""
        if architecture:
            # Extraer temas principales de la arquitectura
            themes = architecture.get('themes', [])
            if themes:
                themes_text = ", ".join(themes[:3])  # Primeros 3 temas
                architecture_context += f"\n- Temas principales del libro: {themes_text}"
            
            # Extraer información de personajes si es ficción
            characters = architecture.get('characters', [])
            if characters and len(characters) > 0:
                main_char = characters[0].get('name', '')
                if main_char:
                    architecture_context += f"\n- Personaje principal: {main_char}"
            
            # Extraer setting si está disponible
            setting = architecture.get('setting', {})
            if setting:
                time_period = setting.get('time', '')
                location = setting.get('location', '')
                if time_period or location:
                    architecture_context += f"\n- Contexto: {time_period} {location}".strip()
            
            # Extraer estructura del plot si es ficción
            plot = architecture.get('plot_structure', {})
            if plot:
                exposition = plot.get('exposition', '')
                if exposition:
                    architecture_context += f"\n- Enfoque narrativo: {exposition[:100]}..."
        
        return f"""Crea una dedicatoria profesional para este libro usando TODA la información disponible:

**Información básica del libro:**
- Título: "{params.title}"
- Género: {genre_name}
- Idioma: {language_name}
- Audiencia: {params.target_audience}
- Temas clave: {params.key_topics}
- Autor: {params.author_name}

**Información detallada de la arquitectura:**{architecture_context}

**Instrucciones específicas:**
- Escribe completamente en {language_name}
- Que sea específica para el contenido real del libro
- Usa los temas, personajes y contexto de la arquitectura
- Tono {params.tone} y profesional
- 2-3 párrafos máximo
- Sin HTML, solo texto plano
- Que refleje la esencia y propósito único de este libro específico

Crea una dedicatoria que realmente conecte con los lectores de este libro específico basándote en su contenido y arquitectura."""
    
    def _build_prologue_system_prompt(self) -> str:
        """System prompt para prólogos profesionales."""
        return """Eres un escritor profesional especializado en crear prólogos cautivadores para libros educativos y profesionales.

Tu tarea es crear un prólogo que:
1. ESTABLEZCA el contexto y propósito del libro
2. CONECTE con la audiencia objetivo específica
3. EXPLIQUE la metodología o enfoque único
4. GENERE expectativa y motivación para seguir leyendo
5. SEA ESPECÍFICO al contenido (no genérico)

ESTRUCTURA RECOMENDADA:
- Párrafo 1: Contexto e importancia del tema
- Párrafo 2-3: Enfoque único del libro y metodología
- Párrafo 4: Beneficios específicos para el lector
- Párrafo 5: Invitación a la acción/lectura

REGLAS:
- Escribe ÚNICAMENTE en el idioma especificado
- NO uses frases cliché como "Este libro representa..."
- SÍ crea contenido específico al tema del libro
- Mantén un tono profesional pero accesible
- 4-6 párrafos, longitud profesional

Responde únicamente con el texto del prólogo."""
    
    def _build_prologue_user_prompt_with_architecture(self, params: ContentGenerationParams, architecture: Dict[str, Any] = None) -> str:
        """User prompt para prólogos usando la arquitectura completa del libro."""
        language_name = self.language_names.get(params.language, params.language)
        genre_name = self.genre_contexts.get(params.genre, params.genre)
        
        # Extraer información completa de la arquitectura
        architecture_details = ""
        if architecture:
            # Extraer capítulos y estructura
            chapters = architecture.get('chapters', [])
            if chapters:
                chapter_count = len(chapters)
                first_chapters = [ch.get('title', '') for ch in chapters[:3] if ch.get('title')]
                if first_chapters:
                    architecture_details += f"\n- Estructura: {chapter_count} capítulos, comenzando con: {', '.join(first_chapters)}"
            
            # Extraer temática profunda
            themes = architecture.get('themes', [])
            if themes:
                themes_text = ", ".join(themes)
                architecture_details += f"\n- Temas centrales: {themes_text}"
            
            # Extraer metodología o enfoque
            plot_structure = architecture.get('plot_structure', {})
            if plot_structure:
                exposition = plot_structure.get('exposition', '')
                if exposition:
                    architecture_details += f"\n- Enfoque del libro: {exposition}"
            
            # Extraer objetivo y páginas
            target_pages = architecture.get('target_pages', 0)
            estimated_words = architecture.get('estimated_words', 0)
            if target_pages or estimated_words:
                scope_info = []
                if target_pages: scope_info.append(f"{target_pages} páginas")
                if estimated_words: scope_info.append(f"{estimated_words} palabras")
                architecture_details += f"\n- Alcance: {', '.join(scope_info)}"
            
            # Extraer elementos especiales
            special_elements = architecture.get('special_elements', [])
            if special_elements:
                elements = [elem.get('type', '') for elem in special_elements if elem.get('type')]
                if elements:
                    architecture_details += f"\n- Elementos adicionales: {', '.join(elements)}"
        
        return f"""Crea un prólogo profesional para este libro usando TODA la información de la arquitectura:

**Información básica del libro:**
- Título: "{params.title}"
- Género: {genre_name}
- Idioma: {language_name}  
- Audiencia: {params.target_audience}
- Temas clave: {params.key_topics}
- Tono: {params.tone}
- Autor: {params.author_name}

**Arquitectura completa del libro:**{architecture_details}

**Contexto pedagógico:**
- El libro debe ser útil y práctico para {params.target_audience}
- Debe establecer credibilidad académica y profesional
- Enfócate en los beneficios específicos basados en la estructura real
- Conecta con la metodología y enfoque específico del contenido

**Instrucciones críticas:**
- Escribe completamente en {language_name}
- 4-6 párrafos de longitud profesional
- Tono {params.tone} pero accesible y motivador
- USA la información de la arquitectura para ser específico
- Menciona la estructura, temas y enfoque real del libro
- Sin HTML, solo texto plano
- Haz que el lector se emocione por el contenido específico que va a encontrar

Crea un prólogo que realmente refleje el libro específico basándote en su arquitectura completa y haga que los lectores estén ansiosos por comenzar."""
    
    # ================================
    # MÉTODOS DE CONSTRUCCIÓN HTML
    # ================================
    
    def _wrap_dedication_html(self, content: str) -> str:
        """Envuelve el contenido de dedicatoria en HTML profesional."""
        return f"""
        <div class="dedication-content">
            <h2 class="dedication-title">DEDICATORIA</h2>
            <div class="dedication-divider"></div>
            <div class="dedication-text">
                {self._paragraphs_to_html(content)}
            </div>
        </div>
        """
    
    def _wrap_prologue_html(self, content: str) -> str:
        """Envuelve el prólogo en HTML profesional."""
        return f"""
        <div class="prologue-content">
            <h2 class="prologue-title">PRÓLOGO</h2>
            <div class="prologue-divider"></div>
            <div class="prologue-text">
                {self._paragraphs_to_html(content)}
            </div>
        </div>
        """
    
    def _paragraphs_to_html(self, content: str) -> str:
        """Convierte texto plano a párrafos HTML."""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        return '\n'.join([f'                <p>{p}</p>' for p in paragraphs])
    
    # ================================
    # MÉTODOS AUXILIARES
    # ================================
    
    def _get_claude_service(self):
        """Obtiene el servicio Claude de forma segura."""
        try:
            from app.services.claude_service import get_claude_service
            return get_claude_service()
        except Exception as e:
            logger.warning(f"No se pudo obtener Claude service: {e}")
            return None
    
    async def _call_claude_api(self, claude_service, system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Llama a la API de Claude de forma segura.
        
        Args:
            claude_service: Servicio de Claude
            system_prompt: Prompt del sistema
            user_prompt: Prompt del usuario
            max_tokens: Tokens máximos
            
        Returns:
            Resultado de la API de Claude
        """
        try:
            # Usar el método correcto del claude service para generar contenido simple
            # Esto es compatible con la arquitectura existente de claude_service
            
            # Preparar mensajes en formato de Claude API
            messages = [
                {
                    "role": "user", 
                    "content": user_prompt
                }
            ]
            
            # Llamar a Claude usando el cliente interno
            response = await claude_service.content_generator.client.client.messages.create(
                model=claude_service.content_generator.config.model,
                max_tokens=max_tokens,
                temperature=claude_service.content_generator.config.temperature,
                system=system_prompt,
                messages=messages
            )
            
            # Extraer contenido de la respuesta
            if response and hasattr(response, 'content') and len(response.content) > 0:
                content = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
                return {
                    'success': True,
                    'content': content
                }
            else:
                return {
                    'success': False,
                    'error': 'No content in Claude response'
                }
                
        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_fallback_dedication(self, params: ContentGenerationParams) -> str:
        """Dedicatoria de respaldo si Claude falla."""
        return f"""
        <div class="dedication-content">
            <h2 class="dedication-title">DEDICATORIA</h2>
            <div class="dedication-divider"></div>
            <div class="dedication-text">
                <p>Dedicado a todos los lectores que buscan expandir sus conocimientos y mejorar sus habilidades a través del aprendizaje continuo.</p>
                <p>A quienes creen que cada libro es una oportunidad de crecimiento personal y profesional.</p>
            </div>
        </div>
        """
    
    def _get_fallback_prologue(self, params: ContentGenerationParams) -> str:
        """Prólogo de respaldo si Claude falla."""
        return f"""
        <div class="prologue-content">
            <h2 class="prologue-title">PRÓLOGO</h2>
            <div class="prologue-divider"></div>
            <div class="prologue-text">
                <p>"{params.title}" ha sido creado con el objetivo de proporcionar a los lectores una experiencia de aprendizaje valiosa y práctica.</p>
                <p>Este libro combina principios fundamentales con aplicaciones prácticas, diseñado específicamente para {params.target_audience}.</p>
                <p>Esperamos que encuentres este recurso útil y enriquecedor en tu camino de aprendizaje.</p>
            </div>
        </div>
        """

    # ================================
    # MÉTODOS ADICIONALES DE PROMPTS
    # ================================
    
    def _build_epilogue_system_prompt(self) -> str:
        """System prompt para epílogos."""
        return """Eres un escritor profesional especializado en crear epílogos inspiradores y reflexivos.

Crea un epílogo que:
1. REFUERCE los conceptos principales aprendidos
2. MOTIVE a continuar el aprendizaje 
3. CONECTE el conocimiento con aplicación práctica
4. INSPIRE confianza en el lector
5. CIERRE de manera profesional y memorable

El epílogo debe sentirse como una conclusión natural y satisfactoria.
Escribe únicamente en el idioma especificado, sin HTML tags."""
    
    def _build_epilogue_user_prompt_with_architecture(self, params: ContentGenerationParams, architecture: Dict[str, Any] = None) -> str:
        """User prompt para epílogos usando la arquitectura del libro."""
        language_name = self.language_names.get(params.language, params.language)
        
        # Extraer información de cierre de la arquitectura
        architecture_closure = ""
        if architecture:
            # Extraer resolución del plot
            plot_structure = architecture.get('plot_structure', {})
            if plot_structure:
                resolution = plot_structure.get('resolution', '')
                falling_action = plot_structure.get('falling_action', '')
                if resolution:
                    architecture_closure += f"\n- Resolución del libro: {resolution}"
                if falling_action:
                    architecture_closure += f"\n- Desarrollo final: {falling_action}"
            
            # Extraer temas para reflexión final
            themes = architecture.get('themes', [])
            if themes:
                main_themes = themes[:2]  # Primeros 2 temas más importantes
                architecture_closure += f"\n- Temas centrales para reflexionar: {', '.join(main_themes)}"
            
            # Extraer el recorrido completo
            chapters = architecture.get('chapters', [])
            if chapters:
                first_chapter = chapters[0].get('title', '') if len(chapters) > 0 else ''
                last_chapter = chapters[-1].get('title', '') if len(chapters) > 0 else ''
                if first_chapter and last_chapter:
                    architecture_closure += f"\n- Recorrido: desde '{first_chapter}' hasta '{last_chapter}'"
            
            # Extraer objetivo final
            target_pages = architecture.get('target_pages', 0)
            estimated_words = architecture.get('estimated_words', 0)
            if target_pages or estimated_words:
                completion_info = []
                if target_pages: completion_info.append(f"{target_pages} páginas")
                if estimated_words: completion_info.append(f"{estimated_words} palabras")
                architecture_closure += f"\n- Logro completado: {', '.join(completion_info)} de contenido especializado"
        
        return f"""Crea un epílogo profesional e inspirador para este libro usando la arquitectura completa:

**Información del libro:**
- Título: "{params.title}"
- Género: {params.genre}
- Idioma: {language_name}
- Audiencia: {params.target_audience}
- Temas clave: {params.key_topics}
- Autor: {params.author_name}

**Arquitectura y cierre del libro:**{architecture_closure}

**Propósito del epílogo:**
- Celebrar lo que el lector ha logrado con el contenido específico
- Reflexionar sobre el recorrido realizado a través de la estructura
- Conectar con los temas principales desarrollados
- Inspirar para la aplicación práctica del conocimiento
- Motivar para el crecimiento continuo

**Instrucciones específicas:**
- Escribe completamente en {language_name}
- 3-4 párrafos de cierre inspirador
- Tono celebrativo y motivador
- Refleja el recorrido específico del libro basándote en la arquitectura
- Menciona los logros específicos del lector
- Sin HTML, solo texto plano
- Haz que el lector se sienta orgulloso del conocimiento adquirido

Crea un epílogo que genuinamente celebre el recorrido específico que el lector acaba de completar con este libro."""
    
    def _build_acknowledgments_system_prompt(self) -> str:
        """System prompt para agradecimientos.""" 
        return """Crea agradecimientos profesionales que reconozcan contribuciones de manera genuina y específica al tema del libro.
        
Incluye reconocimiento a:
1. Expertos en el tema
2. Revisores y colaboradores
3. Comunidad de usuarios/estudiantes
4. Equipo técnico
5. Fuentes de inspiración

Mantén un tono genuino y profesional. Solo texto, sin HTML."""
    
    def _build_acknowledgments_user_prompt_with_architecture(self, params: ContentGenerationParams, architecture: Dict[str, Any] = None) -> str:
        """User prompt para agradecimientos usando la arquitectura del libro."""
        language_name = self.language_names.get(params.language, params.language)
        
        # Extraer información para agradecimientos específicos
        architecture_contributors = ""
        if architecture:
            # Identificar tipos de expertise requeridos
            themes = architecture.get('themes', [])
            if themes:
                expertise_areas = themes[:3]  # Primeros 3 temas más importantes
                architecture_contributors += f"\n- Áreas de expertise que requirieron colaboración: {', '.join(expertise_areas)}"
            
            # Identificar complejidad del contenido
            chapters = architecture.get('chapters', [])
            target_pages = architecture.get('target_pages', 0)
            if chapters and target_pages:
                complexity_level = "alta" if target_pages > 200 else "media" if target_pages > 100 else "especializada"
                architecture_contributors += f"\n- Complejidad del proyecto: {len(chapters)} capítulos, {target_pages} páginas de contenido {complexity_level}"
            
            # Identificar elementos especiales que requirieron expertise
            special_elements = architecture.get('special_elements', [])
            if special_elements:
                special_types = [elem.get('type', '') for elem in special_elements if elem.get('type')]
                if special_types:
                    architecture_contributors += f"\n- Elementos especializados desarrollados: {', '.join(special_types)}"
            
            # Identificar audiencia para agradecimientos específicos
            estimated_words = architecture.get('estimated_words', 0)
            if estimated_words:
                scope = "extenso" if estimated_words > 50000 else "comprehensivo" if estimated_words > 20000 else "especializado"
                architecture_contributors += f"\n- Alcance del trabajo: {estimated_words} palabras de contenido {scope}"
        
        return f"""Crea agradecimientos profesionales y genuinos para este libro específico:

**Información del libro:**
- Título: "{params.title}"
- Género: {params.genre}
- Idioma: {language_name}
- Audiencia: {params.target_audience}
- Temas clave: {params.key_topics}
- Autor: {params.author_name}

**Arquitectura y complejidad del proyecto:**{architecture_contributors}

**Tipos de colaboradores para reconocer específicamente:**
- Expertos en el tema específico del libro
- Revisores técnicos o académicos del área
- Profesionales que validaron el contenido
- Comunidad de usuarios/estudiantes del tema
- Equipo técnico y editorial especializado
- Fuentes de investigación y referencias académicas

**Instrucciones específicas:**
- Escribe completamente en {language_name}
- Reconoce contribuciones específicas al tema del libro
- Menciona la complejidad y alcance del proyecto
- Agradece expertise en las áreas temáticas específicas
- Tono genuino, profesional y específico
- 4-5 párrafos organizados por tipo de contribución
- Sin HTML, solo texto plano
- Que refleje el trabajo real requerido para este libro específico

Crea agradecimientos que genuinamente reconozcan las contribuciones necesarias para crear específicamente este libro."""
    
    def _build_about_author_system_prompt(self) -> str:
        """System prompt para 'Acerca del Autor'."""
        return """Crea una biografía profesional del autor que establezca credibilidad y conexión con el tema del libro.

La biografía debe:
1. Ser profesional pero accesible
2. Destacar credenciales relevantes al tema
3. Mostrar pasión por la educación
4. Ser inspiradora pero creíble

Solo texto, sin HTML tags."""
    
    def _build_about_author_user_prompt_with_architecture(self, params: ContentGenerationParams, architecture: Dict[str, Any] = None) -> str:
        """User prompt para 'Acerca del Autor' usando la arquitectura del libro."""
        language_name = self.language_names.get(params.language, params.language)
        
        # Extraer información de expertise requerida de la arquitectura
        expertise_profile = ""
        if architecture:
            # Identificar áreas de expertise demostradas
            themes = architecture.get('themes', [])
            if themes:
                expertise_areas = themes[:3]  # Primeras 3 áreas más importantes
                expertise_profile += f"\n- Expertise demostrada en: {', '.join(expertise_areas)}"
            
            # Identificar complejidad del trabajo realizado
            chapters = architecture.get('chapters', [])
            target_pages = architecture.get('target_pages', 0)
            estimated_words = architecture.get('estimated_words', 0)
            if chapters and (target_pages or estimated_words):
                work_complexity = []
                if len(chapters) > 15: work_complexity.append("estructura compleja")
                elif len(chapters) > 10: work_complexity.append("estructura comprehensiva")
                else: work_complexity.append("estructura especializada")
                
                if target_pages > 300: work_complexity.append("extenso")
                elif target_pages > 150: work_complexity.append("comprehensivo")
                else: work_complexity.append("detallado")
                
                expertise_profile += f"\n- Obra creada: {len(chapters)} capítulos, {target_pages} páginas - trabajo {' y '.join(work_complexity)}"
            
            # Identificar metodología o enfoque único
            plot_structure = architecture.get('plot_structure', {})
            if plot_structure:
                exposition = plot_structure.get('exposition', '')
                if exposition:
                    expertise_profile += f"\n- Metodología empleada: {exposition[:80]}..."
            
            # Identificar audiencia específica para establecer credibilidad
            if params.target_audience:
                audience_mapping = {
                    'children': 'pedagogía infantil',
                    'teens': 'educación adolescente',
                    'adult': 'formación profesional',
                    'young_adult': 'desarrollo de competencias jóvenes',
                    'seniors': 'educación para adultos mayores'
                }
                audience_expertise = audience_mapping.get(params.target_audience, f'educación para {params.target_audience}')
                expertise_profile += f"\n- Especialización en: {audience_expertise}"
        
        return f"""Crea una biografía profesional del autor que establezca credibilidad específica para este libro:

**Información del autor:**
- Nombre: {params.author_name}
- Obra creada: "{params.title}"
- Género: {params.genre}
- Idioma: {language_name}
- Audiencia: {params.target_audience}
- Temas clave: {params.key_topics}

**Expertise demostrada en la arquitectura:**{expertise_profile}

**Propósito de la biografía:**
- Establecer credibilidad específica en el tema del libro
- Demostrar experiencia relevante a los temas desarrollados
- Conectar con la audiencia específica del libro
- Mostrar autoridad en la metodología empleada
- Inspirar confianza en el conocimiento presentado

**Instrucciones específicas:**
- Escribe completamente en {language_name}
- Enfócate en credenciales relevantes al tema específico
- Menciona experiencia en las áreas temáticas del libro
- Establece autoridad pedagógica para {params.target_audience}
- Tono profesional pero accesible
- 3-4 párrafos que inspiren credibilidad
- Sin HTML, solo texto plano
- Que refleje la expertise real necesaria para crear este libro específico

Crea una biografía que genuinamente establezca la autoridad del autor en el tema específico de este libro y conecte con su audiencia objetivo."""
    
    def _wrap_epilogue_html(self, content: str) -> str:
        """Envuelve epílogo en HTML."""
        return f"""
        <div class="epilogue-content">
            <h2 class="epilogue-title">EPÍLOGO</h2>
            <div class="epilogue-divider"></div>
            <div class="epilogue-text">
                {self._paragraphs_to_html(content)}
            </div>
        </div>
        """
    
    def _wrap_acknowledgments_html(self, content: str) -> str:
        """Envuelve agradecimientos en HTML."""
        return f"""
        <div class="acknowledgments-content">
            <h2 class="acknowledgments-title">AGRADECIMIENTOS</h2>
            <div class="acknowledgments-divider"></div>
            <div class="acknowledgments-text">
                {self._paragraphs_to_html(content)}
            </div>
        </div>
        """
    
    def _wrap_about_author_html(self, content: str) -> str:
        """Envuelve 'Acerca del Autor' en HTML."""
        return f"""
        <div class="about-author-content">
            <h2 class="about-author-title">ACERCA DEL AUTOR</h2>
            <div class="about-author-divider"></div>
            <div class="about-author-text">
                {self._paragraphs_to_html(content)}
            </div>
        </div>
        """
    
    def _get_fallback_epilogue(self, params: ContentGenerationParams) -> str:
        """Epílogo de respaldo."""
        return self._wrap_epilogue_html("Has completado un valioso recorrido de aprendizaje. Te animamos a continuar aplicando estos conocimientos en tu desarrollo personal y profesional.")
    
    def _get_fallback_acknowledgments(self, params: ContentGenerationParams) -> str:
        """Agradecimientos de respaldo."""
        return self._wrap_acknowledgments_html("Agradecemos a todos los expertos, educadores y miembros de la comunidad que hicieron posible la creación de este recurso educativo.")
    
    def _get_fallback_about_author(self, params: ContentGenerationParams) -> str:
        """'Acerca del Autor' de respaldo."""
        return self._wrap_about_author_html(f"{params.author_name} es un autor comprometido con la creación de recursos educativos de alta calidad, utilizando tecnología avanzada para democratizar el acceso al conocimiento.")