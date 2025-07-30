"""
Professional Ebook Formatting Service
Servicio avanzado de formateo profesional para ebooks comerciales.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from bs4 import BeautifulSoup
import uuid
from datetime import datetime

from .book_formatting_service import FormattingPlatform, FormattingOptions, PlatformSpecifications
from .markdown_to_html_service import MarkdownToHTMLConverter, BookStructure, HTMLElement


@dataclass
class ProfessionalFormattingOptions(FormattingOptions):
    """Opciones extendidas de formateo profesional."""
    
    # Características de ebook comercial
    enable_toc_navigation: bool = True
    enable_index_generation: bool = True
    enable_cross_references: bool = True
    enable_footnotes: bool = True
    enable_page_numbers: bool = True
    enable_chapter_thumbnails: bool = False
    
    # Estilo visual avanzado
    theme: str = "classic"  # classic, modern, minimal, academic
    color_scheme: str = "default"  # default, sepia, dark, high-contrast
    
    # Optimizaciones por plataforma
    optimize_file_size: bool = True
    embed_fonts: bool = True
    include_metadata: bool = True
    
    # Características interactivas
    enable_highlights: bool = True
    enable_annotations: bool = True
    enable_bookmarks: bool = True
    enable_search: bool = True
    
    # Elementos comerciales
    include_isbn: str = ""
    include_publisher_info: bool = True
    include_legal_notice: bool = True
    include_marketing_pages: bool = False


class EbookQualityAnalyzer:
    """Analizador de calidad para ebooks comerciales."""
    
    def __init__(self):
        self.quality_criteria = {
            'structure': {
                'has_toc': 10,
                'has_chapters': 10,
                'has_metadata': 5,
                'has_cover': 5
            },
            'formatting': {
                'consistent_styles': 10,
                'proper_hierarchy': 10,
                'readable_fonts': 5,
                'good_spacing': 5
            },
            'navigation': {
                'working_links': 10,
                'chapter_breaks': 5,
                'page_numbers': 5,
                'bookmarks': 5
            },
            'commercial': {
                'isbn_present': 5,
                'copyright_info': 5,
                'publisher_data': 5,
                'professional_layout': 10
            }
        }
    
    def analyze_quality(self, book_structure: BookStructure, 
                       options: ProfessionalFormattingOptions) -> Dict[str, Any]:
        """Analiza la calidad del ebook según estándares comerciales."""
        
        scores = {
            'structure': self._analyze_structure(book_structure, options),
            'formatting': self._analyze_formatting(book_structure, options),
            'navigation': self._analyze_navigation(book_structure, options),
            'commercial': self._analyze_commercial(book_structure, options)
        }
        
        total_score = sum(score['score'] for score in scores.values())
        max_score = sum(sum(criteria.values()) for criteria in self.quality_criteria.values())
        
        return {
            'total_score': total_score,
            'max_score': max_score,
            'percentage': round((total_score / max_score) * 100),
            'category_scores': scores,
            'recommendations': self._generate_recommendations(scores),
            'platform_compliance': self._check_platform_compliance(book_structure, options),
            'market_readiness': self._assess_market_readiness(total_score, max_score)
        }
    
    def _analyze_structure(self, book_structure: BookStructure, 
                          options: ProfessionalFormattingOptions) -> Dict[str, Any]:
        """Analiza la estructura del ebook."""
        score = 0
        issues = []
        
        if book_structure.toc:
            score += self.quality_criteria['structure']['has_toc']
        else:
            issues.append("Falta tabla de contenidos navegable")
        
        chapter_count = len([e for e in book_structure.elements 
                           if e and e.type.value == "chapter"])
        if chapter_count > 0:
            score += self.quality_criteria['structure']['has_chapters']
        else:
            issues.append("No se detectaron capítulos")
        
        if book_structure.metadata:
            score += self.quality_criteria['structure']['has_metadata']
        else:
            issues.append("Metadatos incompletos")
        
        if options.include_cover_page:
            score += self.quality_criteria['structure']['has_cover']
        else:
            issues.append("Falta página de portada")
        
        return {
            'score': score,
            'issues': issues,
            'details': {
                'chapter_count': chapter_count,
                'has_toc': bool(book_structure.toc),
                'metadata_complete': bool(book_structure.metadata)
            }
        }
    
    def _analyze_formatting(self, book_structure: BookStructure,
                          options: ProfessionalFormattingOptions) -> Dict[str, Any]:
        """Analiza el formateo del ebook."""
        score = 0
        issues = []
        
        # Verificar consistencia de estilos
        if options.use_professional_typography:
            score += self.quality_criteria['formatting']['consistent_styles']
        else:
            issues.append("Tipografía no profesional")
        
        # Verificar jerarquía
        has_hierarchy = self._check_heading_hierarchy(book_structure)
        if has_hierarchy:
            score += self.quality_criteria['formatting']['proper_hierarchy']
        else:
            issues.append("Jerarquía de encabezados inconsistente")
        
        # Verificar legibilidad
        if options.font_size_body >= 11:
            score += self.quality_criteria['formatting']['readable_fonts']
        else:
            issues.append(f"Tamaño de fuente muy pequeño: {options.font_size_body}pt")
        
        # Verificar espaciado
        if options.line_spacing >= 1.2:
            score += self.quality_criteria['formatting']['good_spacing']
        else:
            issues.append("Espaciado de línea insuficiente")
        
        return {
            'score': score,
            'issues': issues,
            'details': {
                'font_size': options.font_size_body,
                'line_spacing': options.line_spacing,
                'typography_quality': 'professional' if options.use_professional_typography else 'basic'
            }
        }
    
    def _analyze_navigation(self, book_structure: BookStructure,
                          options: ProfessionalFormattingOptions) -> Dict[str, Any]:
        """Analiza la navegación del ebook."""
        score = 0
        issues = []
        
        # Enlaces funcionales (asumimos que están bien si hay TOC)
        if book_structure.toc:
            score += self.quality_criteria['navigation']['working_links']
        else:
            issues.append("Sin enlaces de navegación")
        
        # Saltos de capítulo
        if options.use_chapter_breaks:
            score += self.quality_criteria['navigation']['chapter_breaks']
        else:
            issues.append("Sin saltos de página entre capítulos")
        
        # Números de página
        if options.enable_page_numbers:
            score += self.quality_criteria['navigation']['page_numbers']
        else:
            issues.append("Sin números de página")
        
        # Marcadores
        if options.enable_bookmarks:
            score += self.quality_criteria['navigation']['bookmarks']
        else:
            issues.append("Sin soporte para marcadores")
        
        return {
            'score': score,
            'issues': issues,
            'details': {
                'navigation_features': {
                    'toc': bool(book_structure.toc),
                    'chapter_breaks': options.use_chapter_breaks,
                    'page_numbers': options.enable_page_numbers,
                    'bookmarks': options.enable_bookmarks
                }
            }
        }
    
    def _analyze_commercial(self, book_structure: BookStructure,
                          options: ProfessionalFormattingOptions) -> Dict[str, Any]:
        """Analiza aspectos comerciales del ebook."""
        score = 0
        issues = []
        
        # ISBN
        if options.include_isbn:
            score += self.quality_criteria['commercial']['isbn_present']
        else:
            issues.append("Sin ISBN asignado")
        
        # Información de copyright
        if options.include_copyright_page:
            score += self.quality_criteria['commercial']['copyright_info']
        else:
            issues.append("Falta página de copyright")
        
        # Datos del editor
        if options.include_publisher_info:
            score += self.quality_criteria['commercial']['publisher_data']
        else:
            issues.append("Sin información del editor")
        
        # Diseño profesional
        if self._has_professional_layout(options):
            score += self.quality_criteria['commercial']['professional_layout']
        else:
            issues.append("Diseño no cumple estándares comerciales")
        
        return {
            'score': score,
            'issues': issues,
            'details': {
                'isbn': options.include_isbn or 'No asignado',
                'publisher_ready': score >= 20
            }
        }
    
    def _check_heading_hierarchy(self, book_structure: BookStructure) -> bool:
        """Verifica que la jerarquía de encabezados sea correcta."""
        heading_levels = []
        for element in book_structure.elements:
            if hasattr(element, 'attributes') and 'data-level' in element.attributes:
                heading_levels.append(int(element.attributes['data-level']))
        
        # Verificar que no haya saltos de nivel
        for i in range(1, len(heading_levels)):
            if heading_levels[i] > heading_levels[i-1] + 1:
                return False
        
        return True
    
    def _has_professional_layout(self, options: ProfessionalFormattingOptions) -> bool:
        """Verifica si el diseño cumple estándares profesionales."""
        return all([
            options.use_professional_typography,
            options.use_chapter_breaks,
            options.use_headers_footers,
            options.font_size_body >= 10,
            options.line_spacing >= 1.2
        ])
    
    def _generate_recommendations(self, scores: Dict[str, Dict]) -> List[str]:
        """Genera recomendaciones basadas en el análisis."""
        recommendations = []
        
        for category, data in scores.items():
            if data['issues']:
                for issue in data['issues'][:3]:  # Top 3 issues
                    recommendations.append(f"[{category.upper()}] {issue}")
        
        # Recomendaciones adicionales prioritarias
        total_issues = sum(len(data['issues']) for data in scores.values())
        if total_issues > 10:
            recommendations.insert(0, "⚠️ Se detectaron múltiples problemas que afectan la calidad comercial")
        
        return recommendations
    
    def _check_platform_compliance(self, book_structure: BookStructure,
                                  options: ProfessionalFormattingOptions) -> Dict[str, bool]:
        """Verifica cumplimiento con requisitos de plataformas."""
        compliance = {}
        
        # Amazon KDP
        compliance['amazon_kdp'] = all([
            options.font_size_body >= 9,
            options.line_spacing >= 1.2,
            options.include_copyright_page,
            options.use_chapter_breaks
        ])
        
        # Apple Books
        compliance['apple_books'] = all([
            options.font_size_body >= 10,
            options.include_table_of_contents,
            book_structure.metadata.get('language') is not None
        ])
        
        # Google Play Books
        compliance['google_play'] = all([
            options.font_size_body >= 10,
            options.line_spacing >= 1.15,
            options.optimize_file_size
        ])
        
        return compliance
    
    def _assess_market_readiness(self, total_score: int, max_score: int) -> Dict[str, Any]:
        """Evalúa si el ebook está listo para el mercado."""
        percentage = (total_score / max_score) * 100
        
        if percentage >= 90:
            status = "Listo para publicación"
            level = "excellent"
        elif percentage >= 75:
            status = "Requiere ajustes menores"
            level = "good"
        elif percentage >= 60:
            status = "Necesita mejoras significativas"
            level = "fair"
        else:
            status = "No apto para publicación comercial"
            level = "poor"
        
        return {
            'status': status,
            'level': level,
            'percentage': round(percentage),
            'ready_for_market': percentage >= 75
        }


class ProfessionalFormattingService:
    """Servicio principal de formateo profesional para ebooks comerciales."""
    
    def __init__(self):
        self.quality_analyzer = EbookQualityAnalyzer()
        self.platform_specs = PlatformSpecifications()
        self.html_converter = MarkdownToHTMLConverter()
    
    def format_for_commercial_distribution(self, book: Any,
                                          options: ProfessionalFormattingOptions) -> Dict[str, Any]:
        """Formatea un libro para distribución comercial."""
        
        # Obtener contenido (preferir HTML sobre markdown)
        content = book.content_html if book.content_html else book.content
        
        # Si es markdown, convertir a HTML
        if not book.content_html and book.content:
            book_structure = self.html_converter.convert(
                book.content,
                book.title,
                book.user.full_name if hasattr(book, 'user') and book.user else "",
                book.language
            )
        else:
            # Parsear HTML existente
            book_structure = self._parse_html_content(content, book)
        
        # Aplicar formateo profesional
        formatted_structure = self._apply_professional_formatting(book_structure, options)
        
        # Generar elementos adicionales
        formatted_structure = self._add_commercial_elements(formatted_structure, options, book)
        
        # Analizar calidad
        quality_analysis = self.quality_analyzer.analyze_quality(formatted_structure, options)
        
        # Generar vista previa
        preview_data = self._generate_preview_data(formatted_structure, options, quality_analysis)
        
        return {
            'formatted_content': formatted_structure.to_html_content(),  # Para embedding en template
            'formatted_document': formatted_structure.to_html_document(),  # Para exportación completa
            'structure': formatted_structure,
            'quality_analysis': quality_analysis,
            'preview_data': preview_data,
            'export_ready': quality_analysis['market_readiness']['ready_for_market']
        }
    
    def _parse_html_content(self, html_content: str, book: Any) -> BookStructure:
        """Parsea contenido HTML existente a BookStructure."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        elements = []
        toc = []
        index = {}
        
        # Extraer elementos del HTML
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'div', 'section']):
            # Convertir a HTMLElement
            html_elem = self._soup_to_html_element(element)
            if html_elem:
                elements.append(html_elem)
        
        # Construir TOC desde encabezados
        for element in elements:
            if element.type.value in ['book-title', 'chapter', 'chapter-title', 'section']:
                toc_entry = {
                    'id': element.id,
                    'title': element.content,
                    'level': int(element.attributes.get('data-level', 1)),
                    'children': []
                }
                toc.append(toc_entry)
        
        return BookStructure(
            title=book.title,
            author=book.user.full_name if hasattr(book, 'user') and book.user else "",
            language=book.language,
            elements=elements,
            toc=toc,
            index=index,
            metadata={
                'book_id': book.id,
                'created_at': str(book.created_at) if hasattr(book, 'created_at') else None
            }
        )
    
    def _soup_to_html_element(self, soup_element) -> Optional[HTMLElement]:
        """Convierte un elemento BeautifulSoup a HTMLElement."""
        # Mapeo de tags a tipos
        tag_type_map = {
            'h1': 'book-title',
            'h2': 'chapter-title',
            'h3': 'section',
            'h4': 'subsection',
            'p': 'paragraph',
            'div': 'div',
            'section': 'chapter'
        }
        
        element_type = tag_type_map.get(soup_element.name, 'div')
        
        # Extraer atributos
        attributes = {}
        for attr, value in soup_element.attrs.items():
            if isinstance(value, list):
                attributes[attr] = ' '.join(value)
            else:
                attributes[attr] = str(value)
        
        # Crear HTMLElement
        from ..services.markdown_to_html_service import HTMLElementType
        
        return HTMLElement(
            id=soup_element.get('id', f"element-{uuid.uuid4().hex[:8]}"),
            type=HTMLElementType(element_type),
            content=soup_element.get_text(),
            attributes=attributes,
            children=[],
            metadata={}
        )
    
    def _apply_professional_formatting(self, book_structure: BookStructure,
                                     options: ProfessionalFormattingOptions) -> BookStructure:
        """Aplica formateo profesional a la estructura del libro."""
        
        # Aplicar tema visual
        self._apply_theme(book_structure, options.theme)
        
        # Optimizar tipografía
        self._optimize_typography(book_structure, options)
        
        # Mejorar navegación
        if options.enable_toc_navigation:
            self._enhance_navigation(book_structure)
        
        # Generar índice automático
        if options.enable_index_generation:
            book_structure.index = self._generate_automatic_index(book_structure)
        
        # Aplicar optimizaciones de plataforma
        self._apply_platform_optimizations(book_structure, options)
        
        return book_structure
    
    def _add_commercial_elements(self, book_structure: BookStructure,
                                options: ProfessionalFormattingOptions,
                                book: Any) -> BookStructure:
        """Agrega elementos comerciales al libro."""
        
        new_elements = []
        
        # Página de título profesional
        if options.include_title_page:
            title_page = self._create_professional_title_page(book_structure, options, book)
            new_elements.append(title_page)
        
        # Página de copyright extendida
        if options.include_copyright_page:
            copyright_page = self._create_extended_copyright_page(book_structure, options, book)
            new_elements.append(copyright_page)
        
        # ISBN y datos de catalogación
        if options.include_isbn:
            catalog_page = self._create_cataloging_page(options.include_isbn, book)
            new_elements.append(catalog_page)
        
        # Páginas de marketing (si aplica)
        if options.include_marketing_pages:
            marketing_pages = self._create_marketing_pages(book)
            new_elements.extend(marketing_pages)
        
        # Insertar al inicio
        book_structure.elements = new_elements + book_structure.elements
        
        return book_structure
    
    def _apply_theme(self, book_structure: BookStructure, theme: str) -> None:
        """Aplica un tema visual al libro."""
        theme_classes = {
            'classic': 'theme-classic',
            'modern': 'theme-modern',
            'minimal': 'theme-minimal',
            'academic': 'theme-academic'
        }
        
        # Agregar clase de tema a todos los elementos
        for element in book_structure.elements:
            current_class = element.attributes.get('class', '')
            element.attributes['class'] = f"{current_class} {theme_classes.get(theme, 'theme-classic')}"
    
    def _optimize_typography(self, book_structure: BookStructure,
                           options: ProfessionalFormattingOptions) -> None:
        """Optimiza la tipografía para lectura profesional."""
        
        # Aplicar kerning y ligaduras
        for element in book_structure.elements:
            if element and element.type.value in ['paragraph', 'chapter-title', 'section']:
                element.attributes['style'] = (
                    f"font-family: {options.font_family}; "
                    f"font-size: {options.font_size_body}pt; "
                    f"line-height: {options.line_spacing}; "
                    f"text-rendering: optimizeLegibility; "
                    f"font-feature-settings: 'kern' 1, 'liga' 1;"
                )
    
    def _enhance_navigation(self, book_structure: BookStructure) -> None:
        """Mejora la navegación del ebook."""
        
        # Agregar anclas a todos los elementos importantes
        for i, element in enumerate(book_structure.elements):
            if element and element.type.value in ['chapter', 'section', 'subsection']:
                # Asegurar ID único y descriptivo
                if not element.id or element.id.startswith('element-'):
                    text_slug = re.sub(r'[^\w\s-]', '', element.content.lower())
                    text_slug = re.sub(r'[-\s]+', '-', text_slug)[:50]
                    element.id = f"{element.type.value}-{i}-{text_slug}"
    
    def _generate_automatic_index(self, book_structure: BookStructure) -> Dict[str, List[str]]:
        """Genera un índice automático de términos importantes."""
        index = {}
        
        # Términos a indexar (expresiones, conceptos clave)
        for element in book_structure.elements:
            if element and element.type.value == 'expression':
                # Extraer término principal
                term = self._extract_index_term(element.content)
                if term:
                    if term not in index:
                        index[term] = []
                    index[term].append(f"#{element.id}")
            
            # También indexar términos en negritas
            if element and element.type.value == 'paragraph' and '<strong>' in element.content:
                terms = re.findall(r'<strong>([^<]+)</strong>', element.content)
                for term in terms:
                    if len(term) > 3 and term not in index:
                        index[term] = []
                    if term in index:
                        index[term].append(f"#{element.id}")
        
        return index
    
    def _extract_index_term(self, content: str) -> Optional[str]:
        """Extrae el término principal de un contenido."""
        # Remover HTML tags
        clean_content = re.sub(r'<[^>]+>', '', content)
        # Extraer primera frase significativa
        match = re.match(r'^[\d.]*\s*(.+?)(?:[.,:;]|$)', clean_content)
        if match:
            return match.group(1).strip()
        return None
    
    def _apply_platform_optimizations(self, book_structure: BookStructure,
                                    options: ProfessionalFormattingOptions) -> None:
        """Aplica optimizaciones específicas de plataforma."""
        
        platform_specs = self.platform_specs.get_specifications(options.platform)
        
        # Ajustar tamaños según plataforma
        if platform_specs:
            min_font = platform_specs.get('fonts', {}).get('minimum_size', 10)
            
            for element in book_structure.elements:
                if 'style' in element.attributes:
                    # Asegurar tamaño mínimo de fuente
                    element.attributes['style'] = re.sub(
                        r'font-size:\s*(\d+)pt',
                        lambda m: f"font-size: {max(int(m.group(1)), min_font)}pt",
                        element.attributes['style']
                    )
    
    def _create_professional_title_page(self, book_structure: BookStructure,
                                      options: ProfessionalFormattingOptions,
                                      book: Any) -> HTMLElement:
        """Crea una página de título profesional."""
        from ..services.markdown_to_html_service import HTMLElement, HTMLElementType
        
        content = f"""
        <div class="title-page-content">
            <h1 class="book-main-title">{book_structure.title}</h1>
            <div class="title-divider"></div>
            <p class="book-author">Por {book_structure.author or 'Autor'}</p>
            <div class="publisher-info">
                <p class="publisher-name">Buko AI Editorial</p>
                <p class="publication-year">{datetime.now().year}</p>
            </div>
        </div>
        """
        
        return HTMLElement(
            id="professional-title-page",
            type=HTMLElementType.BOOK_TITLE,
            content=content,
            attributes={
                'class': 'professional-title-page',
                'data-page-type': 'title'
            },
            children=[],
            metadata={'generated': True}
        )
    
    def _create_extended_copyright_page(self, book_structure: BookStructure,
                                      options: ProfessionalFormattingOptions,
                                      book: Any) -> HTMLElement:
        """Crea una página de copyright extendida."""
        from ..services.markdown_to_html_service import HTMLElement, HTMLElementType
        
        isbn = options.include_isbn or "[ISBN pendiente]"
        
        content = f"""
        <div class="copyright-content">
            <p class="copyright-notice">
                Copyright © {datetime.now().year} {book_structure.author or 'Autor'}
            </p>
            
            <p class="rights-reserved">
                Todos los derechos reservados. Ninguna parte de esta publicación puede ser
                reproducida, distribuida o transmitida en cualquier forma o por cualquier medio,
                incluyendo fotocopias, grabación u otros métodos electrónicos o mecánicos,
                sin el permiso previo por escrito del editor.
            </p>
            
            <div class="publication-data">
                <p>Primera edición digital: {datetime.now().strftime('%B %Y')}</p>
                <p>ISBN: {isbn}</p>
                <p>Generado con tecnología de Inteligencia Artificial</p>
            </div>
            
            <div class="publisher-data">
                <p><strong>Publicado por:</strong></p>
                <p>Buko AI Editorial</p>
                <p>División de Publicaciones Digitales</p>
                <p>www.buko-ai.com</p>
            </div>
            
            <div class="legal-deposit">
                <p>Depósito Legal: [Pendiente]</p>
                <p>Categoría: {book.genre or 'General'}</p>
            </div>
        </div>
        """
        
        return HTMLElement(
            id="extended-copyright-page",
            type=HTMLElementType.PARAGRAPH,
            content=content,
            attributes={
                'class': 'copyright-page extended',
                'data-page-type': 'copyright'
            },
            children=[],
            metadata={'generated': True}
        )
    
    def _create_cataloging_page(self, isbn: str, book: Any) -> HTMLElement:
        """Crea página de catalogación bibliográfica."""
        from ..services.markdown_to_html_service import HTMLElement, HTMLElementType
        
        content = f"""
        <div class="cataloging-data">
            <h3>Catalogación en la Fuente</h3>
            
            <div class="catalog-record">
                <p>{book.user.full_name if hasattr(book, 'user') and book.user else 'Autor'}</p>
                <p class="indent">{book.title} / {book.user.full_name if hasattr(book, 'user') and book.user else 'Autor'}.
                -- 1ª ed. -- Buko AI Editorial, {datetime.now().year}.</p>
                <p class="indent">{book.page_count or '200'} p. ; 23 cm.</p>
                <p class="indent">ISBN {isbn}</p>
                <p class="indent">1. {book.genre or 'Literatura'}. I. Título.</p>
            </div>
            
            <div class="classification-data">
                <p>CDD: 860</p>
                <p>CDU: 82-3</p>
            </div>
        </div>
        """
        
        return HTMLElement(
            id="cataloging-page",
            type=HTMLElementType.PARAGRAPH,
            content=content,
            attributes={
                'class': 'cataloging-page',
                'data-page-type': 'cataloging'
            },
            children=[],
            metadata={'generated': True}
        )
    
    def _create_marketing_pages(self, book: Any) -> List[HTMLElement]:
        """Crea páginas de marketing (otros libros, biografía extendida, etc)."""
        from ..services.markdown_to_html_service import HTMLElement, HTMLElementType
        
        pages = []
        
        # Página "Acerca del Autor" extendida
        about_author = HTMLElement(
            id="about-author-extended",
            type=HTMLElementType.PARAGRAPH,
            content=f"""
            <div class="about-author-extended">
                <h2>Acerca del Autor</h2>
                <div class="author-bio">
                    <p>{book.user.full_name if hasattr(book, 'user') and book.user else 'Autor'} es un autor
                    dedicado a la creación de contenido educativo de alta calidad.</p>
                    <p>Con la ayuda de tecnología de inteligencia artificial avanzada,
                    ha logrado producir obras que combinan rigor académico con accesibilidad.</p>
                </div>
                <div class="author-contact">
                    <p>Para más información, visite: www.buko-ai.com</p>
                </div>
            </div>
            """,
            attributes={
                'class': 'marketing-page about-author',
                'data-page-type': 'marketing'
            },
            children=[],
            metadata={'generated': True}
        )
        pages.append(about_author)
        
        return pages
    
    def _generate_preview_data(self, book_structure: BookStructure,
                              options: ProfessionalFormattingOptions,
                              quality_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Genera datos de vista previa para la interfaz."""
        
        # Estadísticas del libro
        stats = {
            'total_elements': len(book_structure.elements),
            'chapters': len([e for e in book_structure.elements if e and e.type.value == 'chapter']),
            'words_estimated': sum(len(e.content.split()) for e in book_structure.elements if e and hasattr(e, 'content') and e.content),
            'index_entries': len(book_structure.index),
            'toc_entries': len(book_structure.toc)
        }
        
        # Muestra de elementos formateados
        sample_elements = []
        for element in book_structure.elements[:20]:
            if element:  # Verificar que el elemento no sea None
                sample_elements.append({
                    'type': element.type.value,
                    'content': element.content[:200] + '...' if len(element.content) > 200 else element.content,
                    'id': element.id,
                    'formatting': element.attributes
                })
        
        return {
            'statistics': stats,
            'quality_score': quality_analysis,
            'sample_elements': sample_elements,
            'platform_settings': asdict(options),
            'export_formats': self._get_available_export_formats(quality_analysis),
            'estimated_pages': self._calculate_estimated_pages(book_structure, options)
        }
    
    def _get_available_export_formats(self, quality_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Determina formatos de exportación disponibles según calidad."""
        formats = []
        
        # PDF siempre disponible
        formats.append({
            'format': 'PDF',
            'available': True,
            'quality': 'high',
            'features': ['Impresión', 'Navegación', 'Búsqueda']
        })
        
        # EPUB si cumple requisitos
        if quality_analysis['percentage'] >= 70:
            formats.append({
                'format': 'EPUB',
                'available': True,
                'quality': 'high',
                'features': ['Reflowable', 'Navegación TOC', 'Búsqueda', 'Anotaciones']
            })
        
        # MOBI/AZW3 para Kindle
        if quality_analysis['platform_compliance'].get('amazon_kdp', False):
            formats.append({
                'format': 'MOBI/AZW3',
                'available': True,
                'quality': 'high',
                'features': ['Kindle Compatible', 'Whispersync', 'X-Ray']
            })
        
        return formats
    
    def _calculate_estimated_pages(self, book_structure: BookStructure,
                                 options: ProfessionalFormattingOptions) -> int:
        """Calcula número estimado de páginas según formato."""
        
        # Calcular palabras totales
        total_words = sum(len(e.content.split()) for e in book_structure.elements if e and hasattr(e, 'content') and e.content)
        
        # Palabras por página según formato
        words_per_page = {
            'pocket': 220,
            'A5': 250,
            'B5': 280,
            'letter': 350
        }
        
        # Usar formato de página configurado
        page_format = getattr(options, 'page_size', 'A5')
        wpp = words_per_page.get(page_format, 250)
        
        # Calcular páginas base
        base_pages = total_words // wpp
        
        # Agregar páginas adicionales (portada, copyright, etc)
        additional_pages = 0
        if options.include_cover_page: additional_pages += 1
        if options.include_title_page: additional_pages += 1
        if options.include_copyright_page: additional_pages += 1
        if options.include_table_of_contents: additional_pages += 2
        if options.include_about_author: additional_pages += 1
        
        return base_pages + additional_pages