"""
Servicio Inteligente de Generación de Contenido
Utiliza Claude AI para generar contenido profesional y dinámico para cualquier tipo de libro.

Este servicio reemplaza completamente el enfoque hardcodeado anterior con:
- Análisis semántico del contenido del libro
- Generación dinámica basada en género y audiencia
- Algoritmos avanzados de procesamiento de texto
- Patrones factory para diferentes tipos de contenido
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from app.models.book_generation import BookGeneration
from app.services.claude_service import get_claude_service

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Tipos de contenido que puede generar el sistema"""
    DEDICATION = "dedication"
    PROLOGUE = "prologue"
    EPILOGUE = "epilogue"
    ACKNOWLEDGMENTS = "acknowledgments"
    ABOUT_AUTHOR = "about_author"
    CHAPTER_TITLES = "chapter_titles"
    TABLE_OF_CONTENTS = "table_of_contents"
    COVER_TEXT = "cover_text"


class BookGenre(Enum):
    """Géneros de libros soportados dinámicamente"""
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    EDUCATIONAL = "educational"
    BIOGRAPHY = "biography"
    TECHNICAL = "technical"
    CHILDREN = "children"
    POETRY = "poetry"
    REFERENCE = "reference"
    RELIGIOUS = "religious"
    SELF_HELP = "self_help"
    MYSTERY = "mystery"
    ROMANCE = "romance"
    SCIENCE_FICTION = "science_fiction"
    FANTASY = "fantasy"


@dataclass
class BookAnalysis:
    """Resultado del análisis semántico del libro"""
    genre: BookGenre
    main_themes: List[str]
    tone: str  # formal, casual, academic, inspirational, etc.
    target_audience: str  # children, adults, professionals, students, etc.
    language_style: str  # descriptive, technical, narrative, instructional, etc.
    key_concepts: List[str]
    chapter_structure: List[Dict[str, Any]]
    estimated_reading_level: str
    cultural_context: str


@dataclass
class ContentGenerationRequest:
    """Solicitud de generación de contenido"""
    content_type: ContentType
    book_analysis: BookAnalysis
    specific_requirements: Dict[str, Any]
    author_info: Optional[Dict[str, str]] = None
    custom_style: Optional[str] = None


class IntelligentContentGenerator:
    """
    Generador inteligente de contenido que utiliza Claude AI para crear
    contenido dinámico y profesional para cualquier tipo de libro.
    """
    
    def __init__(self):
        # Initialize Claude service with fallback mode
        try:
            self.claude_service = get_claude_service()
            self.has_claude_ai = True
        except Exception as e:
            logger.warning(f"Claude AI not available, using fallback mode: {e}")
            self.claude_service = None
            self.has_claude_ai = False
            
        self.content_factories = {
            ContentType.DEDICATION: self._generate_dedication,
            ContentType.PROLOGUE: self._generate_prologue,
            ContentType.EPILOGUE: self._generate_epilogue,
            ContentType.ACKNOWLEDGMENTS: self._generate_acknowledgments,
            ContentType.ABOUT_AUTHOR: self._generate_about_author,
            ContentType.CHAPTER_TITLES: self._generate_chapter_titles,
            ContentType.TABLE_OF_CONTENTS: self._generate_table_of_contents,
            ContentType.COVER_TEXT: self._generate_cover_text,
        }
    
    def analyze_book_content(self, book: BookGeneration) -> BookAnalysis:
        """
        Realiza análisis semántico avanzado del contenido del libro
        utilizando Claude AI para determinar características dinámicamente.
        En modo fallback, utiliza análisis heurístico básico.
        """
        if not self.has_claude_ai:
            # Fallback mode: Use heuristic analysis
            return self._analyze_book_content_fallback(book)
            
        try:
            content_sample = self._extract_representative_sample(book.content)
            
            analysis_prompt = f"""
            Analiza el siguiente contenido de libro y proporciona un análisis semántico detallado.
            
            CONTENIDO A ANALIZAR:
            {content_sample}
            
            INFORMACIÓN ADICIONAL:
            - Título: {book.title}
            - Descripción: {book.parameters.get('description', 'No disponible') if book.parameters else 'No disponible'}
            - Temas clave: {book.key_topics or 'No especificados'}
            
            Proporciona el análisis en el siguiente formato JSON:
            {{
                "genre": "uno de: fiction, non_fiction, educational, biography, technical, children, poetry, reference, religious, self_help, mystery, romance, science_fiction, fantasy",
                "main_themes": ["tema1", "tema2", "tema3"],
                "tone": "descripción del tono (formal, casual, academic, inspirational, etc.)",
                "target_audience": "audiencia objetivo (children, adults, professionals, students, etc.)",
                "language_style": "estilo del lenguaje (descriptive, technical, narrative, instructional, etc.)",
                "key_concepts": ["concepto1", "concepto2", "concepto3"],
                "estimated_reading_level": "nivel de lectura estimado",
                "cultural_context": "contexto cultural identificado"
            }}
            """
            
            response = self.claude_service.generate_content(
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=1000
            )
            
            analysis_data = self._parse_json_response(response)
            chapter_structure = self._analyze_chapter_structure(book.content)
            
            return BookAnalysis(
                genre=BookGenre(analysis_data.get("genre", "non_fiction")),
                main_themes=analysis_data.get("main_themes", []),
                tone=analysis_data.get("tone", "neutral"),
                target_audience=analysis_data.get("target_audience", "adults"),
                language_style=analysis_data.get("language_style", "narrative"),
                key_concepts=analysis_data.get("key_concepts", []),
                chapter_structure=chapter_structure,
                estimated_reading_level=analysis_data.get("estimated_reading_level", "intermediate"),
                cultural_context=analysis_data.get("cultural_context", "general")
            )
            
        except Exception as e:
            logger.error(f"Error en análisis de contenido: {str(e)}")
            return self._get_fallback_analysis(book)
    
    def generate_content(self, request: ContentGenerationRequest) -> str:
        """
        Genera contenido específico usando el factory pattern correspondiente.
        """
        try:
            factory_method = self.content_factories.get(request.content_type)
            if not factory_method:
                raise ValueError(f"Tipo de contenido no soportado: {request.content_type}")
            
            return factory_method(request)
            
        except Exception as e:
            logger.error(f"Error generando contenido {request.content_type}: {str(e)}")
            return self._get_fallback_content(request.content_type)
    
    def _generate_dedication(self, request: ContentGenerationRequest) -> str:
        """Genera una dedicatoria personalizada basada en el análisis del libro."""
        prompt = f"""
        Genera una dedicatoria elegante y apropiada para un libro con estas características:
        
        ANÁLISIS DEL LIBRO:
        - Género: {request.book_analysis.genre.value}
        - Temas principales: {', '.join(request.book_analysis.main_themes)}
        - Tono: {request.book_analysis.tone}
        - Audiencia: {request.book_analysis.target_audience}
        - Contexto cultural: {request.book_analysis.cultural_context}
        
        REQUISITOS:
        - La dedicatoria debe ser apropiada para el género y tono del libro
        - Debe reflejar los temas principales de manera sutil
        - Longitud: 1-3 oraciones máximo
        - Estilo elegante y profesional
        - NO incluir nombres específicos (usar placeholders como "A mis queridos...")
        
        Genera SOLO la dedicatoria, sin explicaciones adicionales.
        """
        
        response = self.claude_service.generate_content(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        
        return self._clean_generated_content(response)
    
    def _generate_prologue(self, request: ContentGenerationRequest) -> str:
        """Genera un prólogo personalizado basado en el contenido real del libro."""
        prompt = f"""
        Genera un prólogo profesional para un libro con estas características:
        
        ANÁLISIS DEL LIBRO:
        - Género: {request.book_analysis.genre.value}
        - Temas principales: {', '.join(request.book_analysis.main_themes)}
        - Conceptos clave: {', '.join(request.book_analysis.key_concepts)}
        - Estilo del lenguaje: {request.book_analysis.language_style}
        - Audiencia objetivo: {request.book_analysis.target_audience}
        - Nivel de lectura: {request.book_analysis.estimated_reading_level}
        
        ESTRUCTURA DE CAPÍTULOS:
        {self._format_chapter_structure(request.book_analysis.chapter_structure)}
        
        REQUISITOS:
        - El prólogo debe introducir los temas principales del libro
        - Debe establecer expectativas apropiadas para la audiencia
        - Longitud: 200-400 palabras
        - Tono profesional pero accesible
        - Debe motivar al lector a continuar
        - NO mencionar nombres de autor específicos
        
        Genera SOLO el prólogo, sin título ni explicaciones adicionales.
        """
        
        response = self.claude_service.generate_content(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        
        return self._clean_generated_content(response)
    
    def _generate_epilogue(self, request: ContentGenerationRequest) -> str:
        """Genera un epílogo que concluye apropiadamente el libro."""
        prompt = f"""
        Genera un epílogo conclusivo para un libro con estas características:
        
        ANÁLISIS DEL LIBRO:
        - Género: {request.book_analysis.genre.value}
        - Temas principales: {', '.join(request.book_analysis.main_themes)}
        - Conceptos clave: {', '.join(request.book_analysis.key_concepts)}
        - Tono: {request.book_analysis.tone}
        - Audiencia: {request.book_analysis.target_audience}
        
        REQUISITOS:
        - Debe proporcionar cierre a los temas principales
        - Debe inspirar reflexión o acción según el género
        - Longitud: 150-300 palabras
        - Tono consistente con el análisis
        - Debe dejar al lector con una impresión positiva
        
        Genera SOLO el epílogo, sin título ni explicaciones adicionales.
        """
        
        response = self.claude_service.generate_content(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600
        )
        
        return self._clean_generated_content(response)
    
    def _generate_acknowledgments(self, request: ContentGenerationRequest) -> str:
        """Genera agradecimientos apropiados para el tipo de libro."""
        prompt = f"""
        Genera una sección de agradecimientos profesional para un libro de tipo {request.book_analysis.genre.value}.
        
        CONTEXTO:
        - Género: {request.book_analysis.genre.value}
        - Tono: {request.book_analysis.tone}
        - Contexto cultural: {request.book_analysis.cultural_context}
        
        REQUISITOS:
        - Agradecimientos apropiados para el tipo de libro
        - Mencionar colaboradores generales (editores, revisores, familia)
        - Longitud: 100-200 palabras
        - Tono agradecido pero profesional
        - NO incluir nombres específicos reales
        
        Genera SOLO los agradecimientos, sin título.
        """
        
        response = self.claude_service.generate_content(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        
        return self._clean_generated_content(response)
    
    def _generate_about_author(self, request: ContentGenerationRequest) -> str:
        """Genera una sección 'Acerca del Autor' profesional."""
        author_info = request.author_info or {}
        
        prompt = f"""
        Genera una biografía profesional de autor para un libro de tipo {request.book_analysis.genre.value}.
        
        INFORMACIÓN DEL AUTOR (si disponible):
        {self._format_author_info(author_info)}
        
        CONTEXTO DEL LIBRO:
        - Género: {request.book_analysis.genre.value}
        - Temas: {', '.join(request.book_analysis.main_themes)}
        - Audiencia: {request.book_analysis.target_audience}
        
        REQUISITOS:
        - Biografía profesional y creíble
        - Debe mencionar experiencia relevante al género del libro
        - Longitud: 100-150 palabras
        - Tono profesional pero personal
        - Si no hay información del autor, crear un perfil genérico profesional
        
        Genera SOLO la biografía, sin título.
        """
        
        response = self.claude_service.generate_content(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        
        return self._clean_generated_content(response)
    
    def _generate_chapter_titles(self, request: ContentGenerationRequest) -> List[str]:
        """Genera títulos de capítulos basados en el contenido real."""
        chapter_structure = request.book_analysis.chapter_structure
        
        prompt = f"""
        Genera títulos de capítulos mejorados basados en el contenido real del libro.
        
        ESTRUCTURA ACTUAL:
        {self._format_chapter_structure_for_titles(chapter_structure)}
        
        ANÁLISIS DEL LIBRO:
        - Género: {request.book_analysis.genre.value}
        - Temas: {', '.join(request.book_analysis.main_themes)}
        - Estilo: {request.book_analysis.language_style}
        - Audiencia: {request.book_analysis.target_audience}
        
        REQUISITOS:
        - Títulos descriptivos y atractivos
        - Consistentes con el tono del libro
        - Que reflejen el contenido real de cada capítulo
        - Format: un título por línea
        - NO incluir numeración
        
        Genera SOLO los títulos, uno por línea.
        """
        
        response = self.claude_service.generate_content(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        titles = [title.strip() for title in response.split('\n') if title.strip()]
        return titles[:len(chapter_structure)]  # Asegurar que coincida con la estructura
    
    def _generate_table_of_contents(self, request: ContentGenerationRequest) -> str:
        """Genera una tabla de contenidos profesional."""
        chapter_titles = self._generate_chapter_titles(request)
        
        toc_html = '<nav class="ebook-toc">\n'
        toc_html += '  <h2 class="toc-title">Tabla de Contenidos</h2>\n'
        toc_html += '  <ul class="toc-list">\n'
        
        # Agregar secciones preliminares si están incluidas
        if request.specific_requirements.get('include_prologue', False):
            toc_html += '    <li class="toc-item"><a href="#prologue" class="toc-link">Prólogo</a></li>\n'
        
        # Agregar capítulos
        for i, title in enumerate(chapter_titles, 1):
            toc_html += f'    <li class="toc-item toc-chapter">\n'
            toc_html += f'      <a href="#chapter-{i}" class="toc-link">\n'
            toc_html += f'        <span class="chapter-number">Capítulo {i}</span>\n'
            toc_html += f'        <span class="chapter-title">{title}</span>\n'
            toc_html += f'      </a>\n'
            toc_html += f'    </li>\n'
        
        # Agregar secciones finales si están incluidas
        if request.specific_requirements.get('include_epilogue', False):
            toc_html += '    <li class="toc-item"><a href="#epilogue" class="toc-link">Epílogo</a></li>\n'
        
        if request.specific_requirements.get('include_about_author', False):
            toc_html += '    <li class="toc-item"><a href="#about-author" class="toc-link">Acerca del Autor</a></li>\n'
        
        toc_html += '  </ul>\n'
        toc_html += '</nav>'
        
        return toc_html
    
    def _generate_cover_text(self, request: ContentGenerationRequest) -> Dict[str, str]:
        """Genera texto para la portada del libro."""
        # Verificar si hay un prompt personalizado en los requisitos específicos
        if 'custom_prompt' in request.specific_requirements:
            prompt = request.specific_requirements['custom_prompt']
        else:
            prompt = f"""
            Genera texto profesional para la portada de un libro con estas características:
            
            ANÁLISIS DEL LIBRO:
            - Género: {request.book_analysis.genre.value}
            - Temas principales: {', '.join(request.book_analysis.main_themes)}
            - Audiencia: {request.book_analysis.target_audience}
            - Nivel: {request.book_analysis.estimated_reading_level}
            
            REQUISITOS:
            - Subtítulo atractivo (opcional)
            - Descripción breve para contraportada (50-100 palabras)
            - Texto promocional profesional
            
            Formato JSON:
            {{
                "subtitle": "subtítulo opcional",
                "back_cover_description": "descripción para contraportada",
                "promotional_text": "texto promocional"
            }}
            """
        
        response = self.claude_service.generate_content(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        
        # Si es un prompt personalizado, devolver la respuesta cruda
        if 'custom_prompt' in request.specific_requirements:
            return response
        
        # Para prompts estándar, intentar parsear JSON
        try:
            return self._parse_json_response(response)
        except:
            return {
                "subtitle": "",
                "back_cover_description": "Un libro que explora temas importantes de manera accesible y profesional.",
                "promotional_text": "Una obra esencial para lectores interesados en profundizar sus conocimientos."
            }
    
    # Métodos auxiliares de procesamiento
    
    def _extract_representative_sample(self, content: str, max_words: int = 1000) -> str:
        """Extrae una muestra representativa del contenido para análisis."""
        words = content.split()
        if len(words) <= max_words:
            return content
        
        # Tomar muestra del inicio, medio y final
        chunk_size = max_words // 3
        start_chunk = ' '.join(words[:chunk_size])
        middle_start = len(words) // 2 - chunk_size // 2
        middle_chunk = ' '.join(words[middle_start:middle_start + chunk_size])
        end_chunk = ' '.join(words[-chunk_size:])
        
        return f"{start_chunk}\n\n[...]\n\n{middle_chunk}\n\n[...]\n\n{end_chunk}"
    
    def _analyze_chapter_structure(self, content: str) -> List[Dict[str, Any]]:
        """Analiza la estructura de capítulos del contenido."""
        chapters = []
        
        # Patrones para detectar capítulos
        chapter_patterns = [
            r'(?i)cap[íi]tulo\s+(\d+)[:\.]?\s*([^\n]+)',
            r'(?i)chapter\s+(\d+)[:\.]?\s*([^\n]+)',
            r'(?i)^(\d+)[:\.]?\s*([^\n]+)',
            r'(?i)^([A-Z][^.!?]*[.!?])\s*$'  # Títulos en mayúsculas
        ]
        
        lines = content.split('\n')
        current_chapter = None
        chapter_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Buscar indicadores de capítulo
            is_chapter_title = False
            for pattern in chapter_patterns:
                match = re.match(pattern, line)
                if match:
                    # Guardar capítulo anterior si existe
                    if current_chapter:
                        current_chapter['content_preview'] = ' '.join(chapter_content[:50])  # Primeras 50 palabras
                        current_chapter['word_count'] = len(' '.join(chapter_content).split())
                        chapters.append(current_chapter)
                    
                    # Iniciar nuevo capítulo
                    chapter_num = len(chapters) + 1
                    current_chapter = {
                        'number': chapter_num,
                        'title': match.group(2) if len(match.groups()) > 1 else line,
                        'detected_pattern': pattern
                    }
                    chapter_content = []
                    is_chapter_title = True
                    break
            
            if not is_chapter_title and current_chapter:
                chapter_content.append(line)
        
        # Agregar último capítulo
        if current_chapter:
            current_chapter['content_preview'] = ' '.join(chapter_content[:50])
            current_chapter['word_count'] = len(' '.join(chapter_content).split())
            chapters.append(current_chapter)
        
        return chapters
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parsea respuesta JSON de Claude AI con manejo de errores."""
        import json
        
        try:
            # Buscar JSON en la respuesta
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("No se encontró JSON válido en la respuesta")
                
        except Exception as e:
            logger.error(f"Error parseando JSON: {str(e)}")
            raise
    
    def _clean_generated_content(self, content: str) -> str:
        """Limpia y formatea el contenido generado."""
        # Eliminar comillas innecesarias
        content = content.strip(' "\'')
        
        # Eliminar prefijos comunes
        prefixes_to_remove = [
            'Aquí tienes',
            'Aquí está',
            'Aquí tienes la',
            'Aquí está la',
            'La dedicatoria es:',
            'El prólogo es:',
        ]
        
        for prefix in prefixes_to_remove:
            if content.lower().startswith(prefix.lower()):
                content = content[len(prefix):].strip()
                content = content.lstrip(':').strip()
        
        return content
    
    def _format_chapter_structure(self, chapters: List[Dict[str, Any]]) -> str:
        """Formatea la estructura de capítulos para prompts."""
        if not chapters:
            return "No se detectó estructura de capítulos clara."
        
        formatted = []
        for chapter in chapters[:10]:  # Limitar a primeros 10 capítulos
            formatted.append(
                f"Capítulo {chapter['number']}: {chapter.get('title', 'Sin título')} "
                f"({chapter.get('word_count', 0)} palabras)"
            )
        
        return '\n'.join(formatted)
    
    def _format_chapter_structure_for_titles(self, chapters: List[Dict[str, Any]]) -> str:
        """Formatea estructura para generación de títulos."""
        if not chapters:
            return "No hay capítulos detectados."
        
        formatted = []
        for chapter in chapters:
            preview = chapter.get('content_preview', '')[:200]  # Primeras 200 chars
            formatted.append(
                f"Capítulo {chapter['number']}: "
                f"Contenido: {preview}..."
            )
        
        return '\n'.join(formatted)
    
    def _format_author_info(self, author_info: Dict[str, str]) -> str:
        """Formatea información del autor para prompts."""
        if not author_info:
            return "No hay información específica del autor disponible."
        
        formatted = []
        for key, value in author_info.items():
            if value:
                formatted.append(f"- {key.replace('_', ' ').title()}: {value}")
        
        return '\n'.join(formatted) if formatted else "No hay información específica del autor disponible."
    
    def _analyze_book_content_fallback(self, book: BookGeneration) -> BookAnalysis:
        """
        Análisis heurístico del contenido del libro cuando Claude AI no está disponible.
        Utiliza análisis de texto básico y patrones para determinar características.
        """
        content = book.content.lower() if book.content else ""
        title = book.title.lower() if book.title else ""
        
        # Determinar género basado en palabras clave
        genre = BookGenre.NON_FICTION  # Default
        if any(word in content + title for word in ['alemán', 'german', 'idioma', 'language', 'aprender', 'learn']):
            genre = BookGenre.EDUCATIONAL
        elif any(word in content + title for word in ['ficción', 'novela', 'cuento', 'historia', 'personaje']):
            genre = BookGenre.FICTION
        elif any(word in content + title for word in ['técnico', 'programming', 'código', 'algoritmo', 'technology']):
            genre = BookGenre.TECHNICAL
        elif any(word in content + title for word in ['biografía', 'vida', 'biography', 'memoir']):
            genre = BookGenre.BIOGRAPHY
        
        # Determinar temas principales basado en contenido
        main_themes = []
        if 'alemán' in content or 'german' in content:
            main_themes.extend(['aprendizaje de idiomas', 'alemán', 'comunicación'])
        if 'redemittel' in content:
            main_themes.extend(['expresiones idiomáticas', 'frases útiles'])
        if 'capítulo' in content:
            main_themes.append('contenido estructurado')
        
        # Defaults si no se encuentran temas específicos
        if not main_themes:
            main_themes = ['conocimiento', 'aprendizaje', 'desarrollo']
        
        # Determinar audiencia basado en complejidad del texto
        avg_word_length = sum(len(word) for word in content.split()) / max(len(content.split()), 1)
        if avg_word_length < 4:
            target_audience = 'principiantes'
            estimated_reading_level = 'básico'
        elif avg_word_length < 6:
            target_audience = 'intermedios'
            estimated_reading_level = 'intermedio'
        else:
            target_audience = 'avanzados'
            estimated_reading_level = 'avanzado'
        
        # Analizar estructura de capítulos
        chapter_structure = self._analyze_chapter_structure_basic(content)
        
        return BookAnalysis(
            genre=genre,
            main_themes=main_themes[:5],  # Limitar a 5 temas
            tone='educativo' if genre == BookGenre.EDUCATIONAL else 'informativo',
            target_audience=target_audience,
            language_style='instructivo' if genre == BookGenre.EDUCATIONAL else 'descriptivo',
            key_concepts=main_themes[:3],  # Primeros 3 como conceptos clave
            chapter_structure=chapter_structure,
            estimated_reading_level=estimated_reading_level,
            cultural_context='multicultural' if any(lang in content for lang in ['alemán', 'german', 'english', 'spanish']) else 'general'
        )
    
    def _analyze_chapter_structure_basic(self, content: str) -> List[Dict[str, Any]]:
        """Análisis básico de estructura de capítulos sin Claude AI."""
        chapters = []
        
        # Buscar patrones de capítulos
        import re
        chapter_patterns = [
            r'capítulo\s+(\d+)',
            r'chapter\s+(\d+)',
            r'lección\s+(\d+)',
            r'tema\s+(\d+)'
        ]
        
        chapter_matches = []
        for pattern in chapter_patterns:
            matches = re.findall(pattern, content.lower())
            chapter_matches.extend(matches)
        
        # Crear estructura básica de capítulos
        unique_chapters = sorted(set(int(match) for match in chapter_matches if match.isdigit()))
        
        for i, chapter_num in enumerate(unique_chapters[:20]):  # Máximo 20 capítulos
            chapters.append({
                'number': chapter_num,
                'title': f'Capítulo {chapter_num}',
                'word_count': len(content.split()) // len(unique_chapters) if unique_chapters else 1000,
                'content_preview': f'Contenido del capítulo {chapter_num}...'
            })
        
        # Si no se encuentran capítulos, crear estructura básica
        if not chapters:
            estimated_chapters = min(max(len(content.split()) // 2000, 1), 15)  # 1-15 capítulos basado en longitud
            for i in range(estimated_chapters):
                chapters.append({
                    'number': i + 1,
                    'title': f'Capítulo {i + 1}',
                    'word_count': len(content.split()) // estimated_chapters,
                    'content_preview': f'Contenido del capítulo {i + 1}...'
                })
        
        return chapters
    
    def _get_fallback_analysis(self, book: BookGeneration) -> BookAnalysis:
        """Proporciona análisis de respaldo en caso de error."""
        return BookAnalysis(
            genre=BookGenre.NON_FICTION,
            main_themes=["conocimiento", "aprendizaje", "desarrollo"],
            tone="profesional",
            target_audience="adultos",
            language_style="informativo",
            key_concepts=["conceptos clave", "ideas principales"],
            chapter_structure=[],
            estimated_reading_level="intermedio",
            cultural_context="general"
        )
    
    def _get_fallback_content(self, content_type: ContentType) -> str:
        """Proporciona contenido de respaldo en caso de error."""
        fallbacks = {
            ContentType.DEDICATION: "A todos aquellos que buscan conocimiento y crecimiento personal.",
            ContentType.PROLOGUE: "Este libro representa un viaje de descubrimiento y aprendizaje. A través de sus páginas, exploraremos conceptos importantes que pueden enriquecer nuestra comprensión del mundo.",
            ContentType.EPILOGUE: "Esperamos que este recorrido haya sido enriquecedor y que los conocimientos compartidos sean de utilidad en su camino personal y profesional.",
            ContentType.ACKNOWLEDGMENTS: "Agradecemos a todos los que hicieron posible esta obra: editores, revisores, y especialmente a los lectores que encuentran valor en estas páginas.",
            ContentType.ABOUT_AUTHOR: "El autor es un profesional dedicado a compartir conocimientos y experiencias a través de la escritura, con el objetivo de contribuir al crecimiento y desarrollo de los lectores."
        }
        
        return fallbacks.get(content_type, "Contenido no disponible.")