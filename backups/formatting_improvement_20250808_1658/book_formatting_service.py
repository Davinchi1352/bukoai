"""
Professional Book Formatting Service
Módulo de formateo profesional para libros con opciones personalizadas
para diferentes plataformas de comercio de ebooks.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class FormattingPlatform(Enum):
    """Plataformas de comercio de ebooks con diferentes estándares."""
    AMAZON_KDP = "amazon_kdp"
    GOOGLE_PLAY_BOOKS = "google_play_books"
    APPLE_BOOKS = "apple_books"
    KOBO = "kobo"
    SMASHWORDS = "smashwords"
    DRAFT2DIGITAL = "draft2digital"
    UNIVERSAL = "universal"


class ElementType(Enum):
    """Tipos de elementos identificados en el contenido del libro."""
    MAIN_TITLE = "main_title"
    CHAPTER_HEADER = "chapter_header"
    CHAPTER_TITLE = "chapter_title"
    SECTION_HEADING = "section_heading"
    SUBSECTION_HEADING = "subsection_heading"
    NUMBERED_EXPRESSION = "numbered_expression"
    PHONETIC_TRANSCRIPTION = "phonetic_transcription"
    TRANSLATION_LITERAL = "translation_literal"
    TRANSLATION_CONTEXTUAL = "translation_contextual"
    USAGE_DESCRIPTION = "usage_description"
    EXAMPLE_TEXT = "example_text"
    BULLET_LIST = "bullet_list"
    PARAGRAPH = "paragraph"
    SEPARATOR = "separator"
    BOLD_TEXT = "bold_text"
    ITALIC_TEXT = "italic_text"


@dataclass
class FormattingOptions:
    """Opciones de formateo profesional."""
    
    # Configuración de plataforma
    platform: FormattingPlatform = FormattingPlatform.UNIVERSAL
    
    # Opciones de estructura del libro
    include_cover_page: bool = True
    include_title_page: bool = True
    include_copyright_page: bool = True
    include_dedication: bool = False
    include_acknowledgments: bool = False
    include_prologue: bool = False
    include_table_of_contents: bool = True
    include_introduction: bool = True
    include_epilogue: bool = False
    include_about_author: bool = True
    include_bibliography: bool = False
    include_index: bool = False
    
    # Opciones de formato de texto
    font_family: str = "Times New Roman"
    font_size_body: int = 12
    font_size_headings: Dict[str, int] = None
    line_spacing: float = 1.5
    paragraph_spacing: float = 6.0
    first_line_indent: float = 12.0
    
    # Opciones de márgenes y página
    page_width: float = 6.0  # pulgadas
    page_height: float = 9.0  # pulgadas
    margin_top: float = 1.0
    margin_bottom: float = 1.0
    margin_left: float = 1.0
    margin_right: float = 1.0
    
    # Opciones de elementos especiales
    highlight_expressions: bool = True
    show_phonetic_pronunciation: bool = True
    emphasize_translations: bool = True
    number_chapters: bool = True
    number_sections: bool = False
    
    # Opciones de estilo profesional
    use_drop_caps: bool = False
    use_chapter_breaks: bool = True
    use_headers_footers: bool = True
    use_professional_typography: bool = True
    
    # Opciones de colores (para formatos digitales)
    text_color: str = "#000000"
    heading_color: str = "#2c3e50"
    accent_color: str = "#3498db"
    background_color: str = "#ffffff"
    
    def __post_init__(self):
        if self.font_size_headings is None:
            self.font_size_headings = {
                'chapter': 18,
                'section': 16,
                'subsection': 14,
                'subsubsection': 13
            }


@dataclass
class BookElement:
    """Elemento individual del libro con sus propiedades de formateo."""
    element_type: ElementType
    content: str
    level: int = 0
    formatting: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.formatting is None:
            self.formatting = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class BookStructure:
    """Estructura completa del libro con todos sus elementos."""
    title: str
    author: str = ""
    elements: List[BookElement] = None
    metadata: Dict[str, Any] = None
    statistics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.elements is None:
            self.elements = []
        if self.metadata is None:
            self.metadata = {}
        if self.statistics is None:
            self.statistics = {}


class PlatformSpecifications:
    """Especificaciones técnicas para diferentes plataformas de ebooks."""
    
    SPECS = {
        FormattingPlatform.AMAZON_KDP: {
            "page_size": (6.0, 9.0),  # 6"x9" estándar
            "margins": {"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
            "fonts": {
                "preferred": ["Times New Roman", "Georgia", "Palatino", "Book Antiqua"],
                "minimum_size": 9,
                "recommended_size": 11
            },
            "line_spacing": {"minimum": 1.2, "recommended": 1.5},
            "max_pages": 828,  # Límite de Amazon para paperback
            "file_size_limit": "650MB",
            "cover_requirements": {
                "min_resolution": (1600, 2560),
                "recommended_resolution": (2560, 1600),
                "format": ["JPEG", "PNG", "TIFF"]
            }
        },
        
        FormattingPlatform.GOOGLE_PLAY_BOOKS: {
            "page_size": (6.0, 9.0),
            "margins": {"top": 0.75, "bottom": 0.75, "left": 0.75, "right": 0.75},
            "fonts": {
                "preferred": ["Times New Roman", "Arial", "Georgia"],
                "minimum_size": 10,
                "recommended_size": 12
            },
            "line_spacing": {"minimum": 1.15, "recommended": 1.5},
            "file_size_limit": "100MB",
            "supports_interactive": True
        },
        
        FormattingPlatform.APPLE_BOOKS: {
            "page_size": (6.0, 9.0),
            "margins": {"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
            "fonts": {
                "preferred": ["Times New Roman", "Palatino", "Georgia"],
                "minimum_size": 10,
                "recommended_size": 12
            },
            "line_spacing": {"minimum": 1.2, "recommended": 1.5},
            "supports_enhanced": True,
            "supports_fixed_layout": True
        },
        
        FormattingPlatform.KOBO: {
            "page_size": (6.0, 9.0),
            "margins": {"top": 0.75, "bottom": 0.75, "left": 0.75, "right": 0.75},
            "fonts": {
                "preferred": ["Times New Roman", "Georgia", "Arial"],
                "minimum_size": 10,
                "recommended_size": 12
            },
            "line_spacing": {"minimum": 1.2, "recommended": 1.5}
        }
    }
    
    @classmethod
    def get_specifications(cls, platform: FormattingPlatform) -> Dict[str, Any]:
        """Obtiene las especificaciones para una plataforma específica."""
        return cls.SPECS.get(platform, cls.SPECS[FormattingPlatform.AMAZON_KDP])


class BookFormattingService:
    """Servicio principal de formateo profesional de libros."""
    
    def __init__(self):
        self.platform_specs = PlatformSpecifications()
    
    def analyze_content_structure(self, content: str) -> BookStructure:
        """Analiza el contenido del libro e identifica todos los elementos estructurales."""
        
        # Dividir contenido en líneas para análisis
        lines = content.split('\n')
        elements = []
        statistics = {
            'total_lines': len(lines),
            'chapters': 0,
            'sections': 0,
            'subsections': 0,
            'expressions': 0,
            'bullet_points': 0,
            'phonetic_transcriptions': 0,
            'word_count_estimated': 0
        }
        
        current_chapter = 0
        current_section = 0
        current_subsection = 0
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            
            if not line:
                continue
                
            element = self._identify_element(line, line_num)
            
            if element:
                # Actualizar estadísticas
                if element.element_type == ElementType.CHAPTER_HEADER:
                    current_chapter += 1
                    statistics['chapters'] = current_chapter
                    element.metadata['chapter_number'] = current_chapter
                    
                elif element.element_type == ElementType.SECTION_HEADING:
                    current_section += 1
                    statistics['sections'] = current_section
                    element.metadata['section_number'] = current_section
                    
                elif element.element_type == ElementType.SUBSECTION_HEADING:
                    current_subsection += 1
                    statistics['subsections'] = current_subsection
                    element.metadata['subsection_number'] = current_subsection
                    
                elif element.element_type == ElementType.NUMBERED_EXPRESSION:
                    statistics['expressions'] += 1
                    
                elif element.element_type == ElementType.PHONETIC_TRANSCRIPTION:
                    statistics['phonetic_transcriptions'] += 1
                    
                elif element.element_type == ElementType.BULLET_LIST:
                    statistics['bullet_points'] += 1
                
                # Contar palabras estimadas
                word_count = len(element.content.split())
                statistics['word_count_estimated'] += word_count
                element.metadata['word_count'] = word_count
                
                elements.append(element)
        
        return BookStructure(
            title=self._extract_title(content),
            elements=elements,
            statistics=statistics
        )
    
    def _identify_element(self, line: str, line_num: int) -> Optional[BookElement]:
        """Identifica el tipo de elemento basado en patrones de markdown."""
        
        # Título principal del libro (primera línea que empieza con #)
        if line.startswith('# ') and not line.startswith('## '):
            return BookElement(
                element_type=ElementType.MAIN_TITLE,
                content=line[2:].strip(),
                level=1,
                metadata={'line_number': line_num}
            )
        
        # Capítulo (# CAPÍTULO)
        if line.startswith('# CAPÍTULO'):
            return BookElement(
                element_type=ElementType.CHAPTER_HEADER,
                content=line[2:].strip(),
                level=1,
                metadata={'line_number': line_num}
            )
        
        # Título de capítulo (##)
        if line.startswith('## ') and not line.startswith('### '):
            return BookElement(
                element_type=ElementType.CHAPTER_TITLE,
                content=line[3:].strip(),
                level=2,
                metadata={'line_number': line_num}
            )
        
        # Sección (###)
        if line.startswith('### ') and not line.startswith('#### '):
            return BookElement(
                element_type=ElementType.SECTION_HEADING,
                content=line[4:].strip(),
                level=3,
                metadata={'line_number': line_num}
            )
        
        # Subsección (####)
        if line.startswith('#### '):
            return BookElement(
                element_type=ElementType.SUBSECTION_HEADING,
                content=line[5:].strip(),
                level=4,
                metadata={'line_number': line_num}
            )
        
        # Expresión numerada (**1. Expresión**)
        numbered_expr_pattern = r'^\*\*(\d+)\.\s+(.+?)\*\*$'
        if re.match(numbered_expr_pattern, line):
            match = re.match(numbered_expr_pattern, line)
            return BookElement(
                element_type=ElementType.NUMBERED_EXPRESSION,
                content=line,
                level=0,
                metadata={
                    'line_number': line_num,
                    'expression_number': int(match.group(1)),
                    'expression_text': match.group(2)
                }
            )
        
        # Transcripción fonética (*[fonética]*)
        phonetic_pattern = r'^\*\[.+?\]\*$'
        if re.match(phonetic_pattern, line):
            return BookElement(
                element_type=ElementType.PHONETIC_TRANSCRIPTION,
                content=line,
                level=0,
                metadata={'line_number': line_num}
            )
        
        # Traducción literal (**Traducción literal:**)
        if line.startswith('**Traducción literal:**'):
            return BookElement(
                element_type=ElementType.TRANSLATION_LITERAL,
                content=line,
                level=0,
                metadata={'line_number': line_num}
            )
        
        # Traducción contextual (**Traducción contextual:**)
        if line.startswith('**Traducción contextual:**'):
            return BookElement(
                element_type=ElementType.TRANSLATION_CONTEXTUAL,
                content=line,
                level=0,
                metadata={'line_number': line_num}
            )
        
        # Uso (**Uso:**)
        if line.startswith('**Uso:**'):
            return BookElement(
                element_type=ElementType.USAGE_DESCRIPTION,
                content=line,
                level=0,
                metadata={'line_number': line_num}
            )
        
        # Ejemplo (**Ejemplo:**)
        if line.startswith('**Ejemplo:**'):
            return BookElement(
                element_type=ElementType.EXAMPLE_TEXT,
                content=line,
                level=0,
                metadata={'line_number': line_num}
            )
        
        # Lista de bullets (- texto)
        if line.startswith('- ') or line.startswith('* '):
            return BookElement(
                element_type=ElementType.BULLET_LIST,
                content=line,
                level=0,
                metadata={'line_number': line_num}
            )
        
        # Separador (---)
        if line.strip() == '---':
            return BookElement(
                element_type=ElementType.SEPARATOR,
                content=line,
                level=0,
                metadata={'line_number': line_num}
            )
        
        # Párrafo regular (cualquier otro texto)
        if line.strip():
            return BookElement(
                element_type=ElementType.PARAGRAPH,
                content=line,
                level=0,
                metadata={
                    'line_number': line_num,
                    'has_bold': '**' in line,
                    'has_italic': '*' in line and '**' not in line
                }
            )
        
        return None
    
    def _extract_title(self, content: str) -> str:
        """Extrae el título principal del contenido."""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# ') and not line.startswith('## '):
                return line[2:].strip()
        return "Untitled Book"
    
    def generate_professional_elements(self, book_structure: BookStructure, 
                                     options: FormattingOptions) -> BookStructure:
        """Genera elementos profesionales adicionales para el libro."""
        
        new_elements = []
        
        # Página de portada
        if options.include_cover_page:
            new_elements.append(BookElement(
                element_type=ElementType.MAIN_TITLE,
                content=f"PORTADA: {book_structure.title}",
                level=0,
                metadata={'page_type': 'cover', 'generated': True}
            ))
        
        # Página de título
        if options.include_title_page:
            new_elements.append(BookElement(
                element_type=ElementType.MAIN_TITLE,
                content=f"PÁGINA DE TÍTULO: {book_structure.title}",
                level=0,
                metadata={'page_type': 'title', 'generated': True}
            ))
        
        # Página de derechos de autor
        if options.include_copyright_page:
            copyright_text = f"""PÁGINA DE DERECHOS DE AUTOR
            
Copyright © 2025 {book_structure.author if book_structure.author else 'Autor'}

Todos los derechos reservados. Ninguna parte de esta publicación puede ser reproducida, distribuida o transmitida en cualquier forma o por cualquier medio, incluyendo fotocopias, grabación u otros métodos electrónicos o mecánicos, sin el permiso previo por escrito del editor, excepto en el caso de citas breves incorporadas en reseñas críticas y ciertos otros usos no comerciales permitidos por la ley de derechos de autor.

Primera edición: 2025

ISBN: [A asignar]

Publicado por Buko AI Editorial
Inteligencia Artificial Educativa
"""
            new_elements.append(BookElement(
                element_type=ElementType.PARAGRAPH,
                content=copyright_text,
                level=0,
                metadata={'page_type': 'copyright', 'generated': True}
            ))
        
        # Dedicatoria
        if options.include_dedication:
            new_elements.append(BookElement(
                element_type=ElementType.PARAGRAPH,
                content="DEDICATORIA\n\n[Espacio para dedicatoria personalizada]",
                level=0,
                metadata={'page_type': 'dedication', 'generated': True}
            ))
        
        # Agradecimientos
        if options.include_acknowledgments:
            new_elements.append(BookElement(
                element_type=ElementType.PARAGRAPH,
                content="AGRADECIMIENTOS\n\n[Espacio para agradecimientos personalizados]",
                level=0,
                metadata={'page_type': 'acknowledgments', 'generated': True}
            ))
        
        # Prólogo
        if options.include_prologue:
            prologue_text = f"""PRÓLOGO

Este libro representa una aproximación innovadora al aprendizaje del alemán, diseñada específicamente para hispanohablantes que buscan dominar los "Redemittel" - esas expresiones idiomáticas que son fundamentales para una comunicación natural y efectiva en alemán.

Los "Redemittel" son mucho más que simples frases hechas; son las herramientas lingüísticas que permiten a los hablantes nativos expresar ideas complejas de manera concisa y culturalmente apropiada. Para los estudiantes de alemán como lengua extranjera, dominar estos elementos representa la diferencia entre una comunicación funcional y una comunicación verdaderamente fluida.

En estas páginas encontrarás 500 expresiones cuidadosamente seleccionadas, organizadas de manera progresiva y acompañadas de explicaciones detalladas que incluyen pronunciación fonética, traducciones múltiples y contextos de uso específicos. Cada expresión ha sido elegida por su frecuencia de uso en el alemán contemporáneo y su utilidad práctica en situaciones reales de comunicación.

La metodología empleada en este libro combina principios de lingüística aplicada con técnicas de memorización probadas, creando un sistema de aprendizaje que permite la adquisición eficiente y la retención a largo plazo de estas estructuras lingüísticas esenciales.

Esperamos que este recurso se convierta en tu compañero indispensable en el fascinante viaje hacia el dominio del alemán.

¡Viel Erfolg beim Lernen!"""
            
            new_elements.append(BookElement(
                element_type=ElementType.PARAGRAPH,
                content=prologue_text,
                level=0,
                metadata={'page_type': 'prologue', 'generated': True}
            ))
        
        # Tabla de contenidos (si se requiere)
        if options.include_table_of_contents:
            toc_elements = self._generate_table_of_contents(book_structure)
            new_elements.extend(toc_elements)
        
        # Epílogo
        if options.include_epilogue:
            epilogue_text = """EPÍLOGO

Has completado un viaje extraordinario a través de 500 expresiones fundamentales del alemán. Este recorrido te ha llevado desde los fundamentos básicos de los "Redemittel" hasta las estructuras más sofisticadas utilizadas en contextos profesionales y académicos.

La maestría en el uso de estas expresiones no termina con la lectura de este libro. El dominio real viene con la práctica constante, la exposición al alemán auténtico y la aplicación consciente de estos elementos en situaciones reales de comunicación.

Te animamos a continuar expandiendo tu repertorio de "Redemittel", manteniéndote siempre atento a las nuevas expresiones que encuentres en tu interacción con el alemán contemporáneo. Recuerda que el idioma es un organismo vivo que evoluciona constantemente.

¡Herzlichen Glückwunsch! Has dado un paso significativo hacia la fluidez en alemán."""
            
            new_elements.append(BookElement(
                element_type=ElementType.PARAGRAPH,
                content=epilogue_text,
                level=0,
                metadata={'page_type': 'epilogue', 'generated': True}
            ))
        
        # Acerca del autor
        if options.include_about_author:
            new_elements.append(BookElement(
                element_type=ElementType.PARAGRAPH,
                content="ACERCA DEL AUTOR\n\n[Espacio para información del autor]",
                level=0,
                metadata={'page_type': 'about_author', 'generated': True}
            ))
        
        # Combinar elementos nuevos con los existentes
        book_structure.elements = new_elements + book_structure.elements
        
        return book_structure
    
    def _generate_table_of_contents(self, book_structure: BookStructure) -> List[BookElement]:
        """Genera una tabla de contenidos navegable basada en la estructura del libro."""
        
        toc_elements = []
        
        # Título de la tabla de contenidos
        toc_elements.append(BookElement(
            element_type=ElementType.CHAPTER_TITLE,
            content="TABLA DE CONTENIDOS",
            level=2,
            metadata={'page_type': 'toc', 'generated': True}
        ))
        
        # Recopilar capítulos y secciones principales
        toc_content = []
        current_chapter = None
        
        for element in book_structure.elements:
            if element.element_type == ElementType.CHAPTER_HEADER:
                current_chapter = element.content
                toc_content.append(f"**{current_chapter}**")
                
            elif element.element_type == ElementType.CHAPTER_TITLE and current_chapter:
                toc_content.append(f"    {element.content}")
                
            elif element.element_type == ElementType.SECTION_HEADING:
                toc_content.append(f"        {element.content}")
        
        # Agregar contenido de TOC
        for toc_line in toc_content:
            toc_elements.append(BookElement(
                element_type=ElementType.PARAGRAPH,
                content=toc_line,
                level=0,
                metadata={'page_type': 'toc', 'generated': True}
            ))
        
        return toc_elements
    
    def apply_platform_formatting(self, book_structure: BookStructure, 
                                 options: FormattingOptions) -> BookStructure:
        """Aplica formateo específico de plataforma a todos los elementos."""
        
        specs = self.platform_specs.get_specifications(options.platform)
        
        # Aplicar especificaciones de plataforma a las opciones
        if specs:
            # Ajustar tamaños de fuente según especificaciones
            min_size = specs.get('fonts', {}).get('minimum_size', 10)
            if options.font_size_body < min_size:
                options.font_size_body = min_size
            
            # Ajustar espaciado de línea
            min_spacing = specs.get('line_spacing', {}).get('minimum', 1.2)
            if options.line_spacing < min_spacing:
                options.line_spacing = min_spacing
        
        # Aplicar formateo a cada elemento
        for element in book_structure.elements:
            element.formatting = self._get_element_formatting(element, options, specs)
        
        return book_structure
    
    def _get_element_formatting(self, element: BookElement, 
                               options: FormattingOptions, 
                               specs: Dict[str, Any]) -> Dict[str, Any]:
        """Obtiene el formateo específico para un elemento."""
        
        base_formatting = {
            'font_family': options.font_family,
            'font_size': options.font_size_body,
            'line_spacing': options.line_spacing,
            'text_color': options.text_color,
            'background_color': options.background_color
        }
        
        # Formateo específico por tipo de elemento
        if element.element_type == ElementType.MAIN_TITLE:
            base_formatting.update({
                'font_size': options.font_size_headings.get('chapter', 18) + 4,
                'font_weight': 'bold',
                'text_align': 'center',
                'color': options.heading_color,
                'margin_top': 48,
                'margin_bottom': 36
            })
        
        elif element.element_type == ElementType.CHAPTER_HEADER:
            base_formatting.update({
                'font_size': options.font_size_headings.get('chapter', 18),
                'font_weight': 'bold',
                'text_align': 'center',
                'color': options.heading_color,
                'margin_top': 36,
                'margin_bottom': 24,
                'page_break_before': True
            })
        
        elif element.element_type == ElementType.CHAPTER_TITLE:
            base_formatting.update({
                'font_size': options.font_size_headings.get('section', 16),
                'font_weight': 'bold',
                'color': options.heading_color,
                'margin_top': 24,
                'margin_bottom': 18
            })
        
        elif element.element_type == ElementType.SECTION_HEADING:
            base_formatting.update({
                'font_size': options.font_size_headings.get('subsection', 14),
                'font_weight': 'bold',
                'color': options.heading_color,
                'margin_top': 18,
                'margin_bottom': 12
            })
        
        elif element.element_type == ElementType.NUMBERED_EXPRESSION:
            base_formatting.update({
                'font_weight': 'bold',
                'color': options.accent_color,
                'margin_top': 12,
                'margin_bottom': 6,
                'highlight': options.highlight_expressions
            })
        
        elif element.element_type == ElementType.PHONETIC_TRANSCRIPTION:
            base_formatting.update({
                'font_style': 'italic',
                'font_family': 'Courier New',  # Monospace para fonética
                'color': '#666666',
                'visible': options.show_phonetic_pronunciation
            })
        
        elif element.element_type == ElementType.TRANSLATION_LITERAL:
            base_formatting.update({
                'font_weight': 'bold',
                'color': options.accent_color if options.emphasize_translations else options.text_color
            })
        
        elif element.element_type == ElementType.TRANSLATION_CONTEXTUAL:
            base_formatting.update({
                'font_weight': 'bold',
                'color': options.accent_color if options.emphasize_translations else options.text_color
            })
        
        return base_formatting
    
    def get_formatting_preview_data(self, book_structure: BookStructure, 
                                   options: FormattingOptions) -> Dict[str, Any]:
        """Genera datos de vista previa para el visor de formateo."""
        
        # Aplicar formateo de plataforma
        formatted_structure = self.apply_platform_formatting(book_structure, options)
        
        # Convertir options a dict manualmente para manejar enums
        options_dict = asdict(options)
        options_dict['platform'] = options.platform.value  # Convertir enum a string
        
        preview_data = {
            'book_info': {
                'title': formatted_structure.title,
                'author': formatted_structure.author,
                'statistics': formatted_structure.statistics,
                'platform': options.platform.value,
                'total_elements': len(formatted_structure.elements)
            },
            'formatting_options': options_dict,
            'platform_specs': PlatformSpecifications.get_specifications(options.platform),
            'elements_sample': [],
            'structure_overview': self._generate_structure_overview(formatted_structure),
            'formatting_quality_score': self._calculate_formatting_quality(formatted_structure, options)
        }
        
        # Generar muestra de elementos formateados (primeros 50)
        for element in formatted_structure.elements[:50]:
            preview_data['elements_sample'].append({
                'type': element.element_type.value,
                'content': element.content[:200] + "..." if len(element.content) > 200 else element.content,
                'level': element.level,
                'formatting': element.formatting,
                'metadata': element.metadata
            })
        
        return preview_data
    
    def _generate_structure_overview(self, book_structure: BookStructure) -> Dict[str, Any]:
        """Genera un resumen de la estructura del libro."""
        
        overview = {
            'chapters': [],
            'total_chapters': 0,
            'total_sections': 0,
            'total_expressions': 0,
            'content_distribution': {}
        }
        
        current_chapter = None
        current_sections = []
        
        for element in book_structure.elements:
            if element.element_type == ElementType.CHAPTER_HEADER:
                if current_chapter:
                    overview['chapters'].append({
                        'title': current_chapter,
                        'sections': current_sections.copy()
                    })
                current_chapter = element.content
                current_sections = []
                overview['total_chapters'] += 1
                
            elif element.element_type == ElementType.SECTION_HEADING:
                current_sections.append(element.content)
                overview['total_sections'] += 1
                
            elif element.element_type == ElementType.NUMBERED_EXPRESSION:
                overview['total_expressions'] += 1
        
        # Agregar último capítulo
        if current_chapter:
            overview['chapters'].append({
                'title': current_chapter,
                'sections': current_sections
            })
        
        return overview
    
    def _calculate_formatting_quality(self, book_structure: BookStructure, 
                                    options: FormattingOptions) -> Dict[str, Any]:
        """Calcula un puntaje de calidad del formateo."""
        
        quality_score = {
            'overall_score': 0,
            'structure_score': 0,
            'typography_score': 0,
            'platform_compliance': 0,
            'professional_elements': 0,
            'recommendations': []
        }
        
        # Evaluar estructura (0-25 puntos)
        structure_points = 0
        if options.include_title_page: structure_points += 3
        if options.include_table_of_contents: structure_points += 5
        if options.include_copyright_page: structure_points += 3
        if options.include_prologue: structure_points += 4
        if options.include_about_author: structure_points += 2
        if book_structure.statistics.get('chapters', 0) > 0: structure_points += 8
        
        quality_score['structure_score'] = min(structure_points, 25)
        
        # Evaluar tipografía (0-25 puntos)
        typography_points = 0
        if options.use_professional_typography: typography_points += 8
        if options.line_spacing >= 1.2: typography_points += 5
        if options.font_size_body >= 10: typography_points += 5
        if options.use_chapter_breaks: typography_points += 4
        if options.first_line_indent > 0: typography_points += 3
        
        quality_score['typography_score'] = min(typography_points, 25)
        
        # Evaluar cumplimiento de plataforma (0-25 puntos)
        specs = PlatformSpecifications.get_specifications(options.platform)
        compliance_points = 25  # Empezar con puntuación completa
        
        if specs:
            min_font = specs.get('fonts', {}).get('minimum_size', 10)
            if options.font_size_body < min_font:
                compliance_points -= 5
                quality_score['recommendations'].append(f"Aumentar tamaño de fuente a mínimo {min_font}pt")
            
            min_spacing = specs.get('line_spacing', {}).get('minimum', 1.2)
            if options.line_spacing < min_spacing:
                compliance_points -= 5
                quality_score['recommendations'].append(f"Aumentar espaciado de línea a mínimo {min_spacing}")
        
        quality_score['platform_compliance'] = max(compliance_points, 0)
        
        # Evaluar elementos profesionales (0-25 puntos)
        professional_points = 0
        if options.highlight_expressions: professional_points += 5
        if options.show_phonetic_pronunciation: professional_points += 5
        if options.emphasize_translations: professional_points += 5
        if options.use_headers_footers: professional_points += 5
        if options.use_professional_typography: professional_points += 5
        
        quality_score['professional_elements'] = min(professional_points, 25)
        
        # Calcular puntaje general
        quality_score['overall_score'] = (
            quality_score['structure_score'] + 
            quality_score['typography_score'] + 
            quality_score['platform_compliance'] + 
            quality_score['professional_elements']
        )
        
        # Agregar recomendaciones basadas en el puntaje
        if quality_score['overall_score'] < 70:
            quality_score['recommendations'].append("Considerar agregar más elementos profesionales")
        if not options.include_prologue:
            quality_score['recommendations'].append("Agregar prólogo para contexto profesional")
        if not options.include_table_of_contents:
            quality_score['recommendations'].append("La tabla de contenidos es esencial para navegación")
        
        return quality_score