"""
Professional Ebook Formatting Service
Servicio avanzado de formateo profesional para ebooks comerciales.
"""

import re
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from bs4 import BeautifulSoup
import uuid
from datetime import datetime

from .book_formatting_service import FormattingPlatform, FormattingOptions, PlatformSpecifications
from .dynamic_content_generator import ContentGenerationParams
from .html_shared_classes import HTMLElement, HTMLElementType

# SWITCH DE COMPATIBILIDAD SEGURO - MIGRACIÓN GRADUAL
# Variable de entorno para alternar entre parsers durante transición
USE_NEW_HTML_PARSER = os.getenv('USE_NEW_HTML_PARSER', 'true').lower() == 'true'

if USE_NEW_HTML_PARSER:
    # Usar nuevo parser HTML (desarrollado para esta refactorización)
    from .html_structure_service import HTMLStructureParser as HTMLConverter
    from .html_shared_classes import BookStructure, HTMLElement  # Mantener clases compartidas
    print("🔄 ProfessionalFormattingService usando NUEVO HTMLStructureParser")
else:
    # Usar parser original markdown (comportamiento actual)
    from .html_shared_classes import MarkdownToHTMLConverter as HTMLConverter, BookStructure, HTMLElement
    print("📜 ProfessionalFormattingService usando MarkdownToHTMLConverter ORIGINAL")


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
    
    # 📝 CRÍTICO: Nombre del autor para secciones profesionales
    author_name: str = ""


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
        # Usar parser según variable de entorno (switch seguro)
        self.html_converter = HTMLConverter()
    
    def format_for_commercial_distribution(self, book: Any,
                                          options: ProfessionalFormattingOptions) -> Dict[str, Any]:
        """Formatea un libro para distribución comercial."""
        
        # 🚀 CORRECCIÓN CRÍTICA: Siempre usar contenido original para evitar duplicación
        # El problema era que usaba content_html (ya formateado) como base, causando duplicación acumulativa
        if book.content:
            # Caso normal: usar contenido original limpio
            content = book.content
            starting_from_original = True
        else:
            # Fallback para libros antiguos sin content original
            # Limpiar elementos comerciales del content_html si existen
            content = self._clean_commercial_elements(book.content_html) if book.content_html else ""
            starting_from_original = False
        
        # Si es markdown o contenido sin formateo previo, convertir a HTML
        if starting_from_original and book.content and not book.content_html:
            # Usar método correcto según parser activo
            if USE_NEW_HTML_PARSER:
                # Nuevo parser usa parse() 
                book_structure = self.html_converter.parse(
                    book.content,
                    book.title,
                    book.user.full_name if hasattr(book, 'user') and book.user else "",
                    book.language
                )
            else:
                # Parser original usa convert()
                book_structure = self.html_converter.convert(
                    book.content,
                    book.title,
                    book.user.full_name if hasattr(book, 'user') and book.user else "",
                    book.language
                )
        else:
            # Parsear HTML existente con opciones para obtener author_name
            book_structure = self._parse_html_content(content, book, options)
        
        # Aplicar formateo profesional
        formatted_structure = self._apply_professional_formatting(book_structure, options)
        
        # Generar elementos adicionales
        formatted_structure = self._add_commercial_elements(formatted_structure, options, book)
        
        # Analizar calidad
        quality_analysis = self.quality_analyzer.analyze_quality(formatted_structure, options)
        
        # Generar vista previa
        preview_data = self._generate_preview_data(formatted_structure, options, quality_analysis)
        
        # Generar contenido HTML final
        html_content = formatted_structure.to_html_content()
        
        # 🚀 FIX SIMPLIFICADO: Limpieza básica ya que desactivamos los métodos problemáticos
        html_content = self._basic_cleanup(html_content)
        
        # 🎯 REINGENIERÍA: Template moderno no necesita wrappers adicionales
        
        return {
            'formatted_content': html_content,  # Para embedding en template
            'formatted_document': formatted_structure.to_html_document(),  # Para exportación completa
            'structure': formatted_structure,
            'quality_analysis': quality_analysis,
            'preview_data': preview_data,
            'export_ready': quality_analysis['market_readiness']['ready_for_market']
        }
    
    def _clean_commercial_elements(self, html_content: str) -> str:
        """
        🧹 LIMPIEZA DE ELEMENTOS COMERCIALES: Elimina elementos de formateo profesional existentes.
        
        Este método es crucial para evitar duplicación cuando se usa content_html como fallback.
        Elimina dedicatorias, prólogos, epílogos, etc. que pueden estar duplicados.
        """
        if not html_content:
            return ""
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Lista de tipos de página comerciales que pueden duplicarse
            commercial_page_types = [
                'title', 'copyright', 'dedication', 'acknowledgments', 
                'prologue', 'epilogue', 'about-author', 'marketing'
            ]
            
            # Buscar y eliminar elementos por data-page-type
            for page_type in commercial_page_types:
                elements_to_remove = soup.find_all(attrs={'data-page-type': page_type})
                for element in elements_to_remove:
                    element.decompose()  # Eliminar completamente del DOM
            
            # También buscar por clases específicas (fallback)
            commercial_classes = [
                'title-page', 'copyright-page', 'dedication-page', 
                'acknowledgments-page', 'prologue-page', 'epilogue-page',
                'about-author-page', 'marketing-page'
            ]
            
            for css_class in commercial_classes:
                elements_to_remove = soup.find_all(class_=css_class)
                for element in elements_to_remove:
                    element.decompose()
            
            # Buscar por IDs específicos (fallback adicional)
            commercial_ids = [
                'professional-title-page', 'extended-copyright-page',
                'dedication-page', 'acknowledgments-page', 'prologue-page',
                'epilogue-page', 'about-author-page'
            ]
            
            for element_id in commercial_ids:
                element_to_remove = soup.find(id=element_id)
                if element_to_remove:
                    element_to_remove.decompose()
            
            cleaned_html = str(soup)
            
            # Log de limpieza para debugging
            original_length = len(html_content)
            cleaned_length = len(cleaned_html)
            elements_removed = original_length - cleaned_length
            
            if elements_removed > 0:
                print(f"🧹 Elementos comerciales limpiados: {elements_removed} caracteres removidos")
            
            return cleaned_html
            
        except Exception as e:
            # Si falla la limpieza, devolver contenido original
            print(f"⚠️ Error limpiando elementos comerciales: {e}")
            return html_content
    
    def _clean_css_corruption_from_content(self, html_content: str) -> str:
        """
        🧹 LIMPIEZA INTELIGENTE DE CORRUPCIÓN: Elimina solo atributos HTML que aparecen como TEXTO PLANO.
        
        ALGORITMO INTELIGENTE:
        1. Identifica contenido DENTRO de etiquetas HTML (entre >...< ) 
        2. Solo limpia atributos corruptos que aparecen mezclados con TEXTO del libro
        3. PRESERVA atributos válidos dentro de etiquetas HTML
        
        Esto soluciona el problema original sin romper el HTML válido.
        """
        if not html_content:
            return html_content
        
        try:
            import re
            cleaned_content = html_content
            total_removals = 0
            
            # 🎯 ESTRATEGIA INTELIGENTE: Solo limpiar CONTENIDO DE TEXTO, no atributos HTML válidos
            
            # Paso 1: Encontrar todo el texto que está DENTRO de elementos HTML (contenido visible)
            # Buscar patrones como: >TEXTO CORRUPTOR<
            text_content_pattern = r'>([^<]*(?:class=|style=|data-[a-zA-Z-]+=|expression-highlight|translation-emphasis)[^<]*)<'
            
            def clean_text_content(match):
                """Limpia solo el contenido de texto que tiene corrupción, preservando las etiquetas"""
                corrupted_text = match.group(1)
                
                # Patrones específicos de corrupción que aparecen como TEXTO
                corruption_patterns = [
                    r'class="[^"]*"',
                    r'style="[^"]*"', 
                    r'data-[a-zA-Z-]+="[^"]*"',
                    r'"expression-highlight"',
                    r'"translation-emphasis"',
                    r'data-expression-type="auto"',
                    r'data-translation="true"',
                    r'data-has-highlighting="true"',
                    r'data-searchable="true"',
                    r'font-family:\s*[^;]*;',
                    r'font-size:\s*[^;]*;',
                    r'line-height:\s*[^;]*;',
                    r'margin-bottom:\s*[^;]*;',
                    r'-webkit-font-smoothing:\s*[^;]*',
                    r'-moz-osx-font-smoothing:\s*[^;]*',
                    r'font-optical-sizing:\s*[^;]*',
                    r'hyphenate-limit-zone:\s*[^;]*',
                    r'te-limit-zone:\s*8%',
                    r';\s*;\s*;+',  # ; ; ; sequences
                    r'ebook-div\s+expression\s+theme-classic',
                    r'professional-typography',
                    r'enhanced-typography',
                ]
                
                cleaned_text = corrupted_text
                local_removals = 0
                
                for pattern in corruption_patterns:
                    matches_before = len(re.findall(pattern, cleaned_text, re.IGNORECASE))
                    if matches_before > 0:
                        cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
                        matches_after = len(re.findall(pattern, cleaned_text, re.IGNORECASE))
                        local_removals += (matches_before - matches_after)
                
                # Limpiar espacios extra resultado de la limpieza
                cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
                
                return f'>{cleaned_text}<'
            
            # Aplicar limpieza inteligente solo al contenido de texto
            matches_before_text = len(re.findall(text_content_pattern, cleaned_content))
            if matches_before_text > 0:
                cleaned_content = re.sub(text_content_pattern, clean_text_content, cleaned_content)
                matches_after_text = len(re.findall(text_content_pattern, cleaned_content))
                total_removals += (matches_before_text - matches_after_text)
                print(f"🧹 Smart cleaning: Fixed {matches_before_text} corrupted text sections")
            
            # Paso 2: Limpieza adicional de fragmentos huérfanos (que no están dentro de tags válidos)
            orphaned_patterns = [
                r'\s+"expression-highlight"\s+',
                r'\s+"translation-emphasis"\s+', 
                r'\s+data-[a-zA-Z-]+="[^"]*"\s+',
                r'\s+style="[^"]*"\s+',
                r'\s+class="[^"]*"\s+',
            ]
            
            for pattern in orphaned_patterns:
                matches_orphaned = len(re.findall(pattern, cleaned_content))
                if matches_orphaned > 0:
                    cleaned_content = re.sub(pattern, ' ', cleaned_content)
                    total_removals += matches_orphaned
                    print(f"🧹 Orphaned cleanup: Removed {matches_orphaned} orphaned attributes")
            
            # Paso 3: Limpieza de espacios y normalización CONSERVADORA
            cleaned_content = re.sub(r'\s{3,}', ' ', cleaned_content)  # Solo espacios excesivos (3+)
            cleaned_content = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_content)  # Solo líneas excesivas
            
            if total_removals > 0:
                print(f"✅ SMART CORRUPTION FIX: {total_removals} corrupted fragments cleaned from TEXT content")
                print(f"📊 HTML structure preserved, only text corruption removed")
            else:
                print("🔍 No corruption detected in text content - HTML structure clean")
            
            return cleaned_content
            
        except Exception as e:
            print(f"⚠️ Error in smart corruption cleaning: {e}")
            # En caso de error, devolver contenido original sin modificar
            return html_content
    
    def _basic_cleanup(self, html_content: str) -> str:
        """
        🧹 LIMPIEZA BÁSICA: Solo normalización de espacios, sin procesamiento complejo.
        
        Como desactivamos los métodos problemáticos (_apply_enhanced_professional_typography, etc.),
        solo necesitamos una limpieza muy básica.
        """
        if not html_content:
            return html_content
            
        try:
            import re
            
            # Solo limpieza de espacios excesivos y normalización básica
            cleaned_content = html_content
            
            # Espacios múltiples → espacio simple
            cleaned_content = re.sub(r'\s{3,}', ' ', cleaned_content)
            
            # Líneas vacías múltiples → máximo 2 líneas vacías
            cleaned_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_content)
            
            # Espacios al inicio/final de líneas
            lines = cleaned_content.split('\n')
            cleaned_lines = [line.rstrip() for line in lines]
            cleaned_content = '\n'.join(cleaned_lines)
            
            print("🧽 Basic cleanup: Only space normalization applied")
            return cleaned_content
            
        except Exception as e:
            print(f"⚠️ Error in basic cleanup: {e}")
            return html_content
    
    def _wrap_with_ebook_containers(self, html_content: str) -> str:
        """
        🎯 FIX CRÍTICO: Envolver contenido con estructura que CSS profesional espera
        
        El CSS ebook-professional.css espera esta estructura:
        <div class='ebook-body'>
          <div class='ebook-container'>
            <!-- contenido aquí -->
          </div>
        </div>
        
        Sin estos wrappers, el contenido se muestra sin formateo profesional.
        Soluciona el problema de fondo gris y falta de estilos.
        """
        if not html_content:
            return ""
        
        wrapped_content = f"""
<div class='ebook-body'>
  <div class='ebook-container'>
{html_content}
  </div>
</div>"""
        
        return wrapped_content
    
    def generate_professional_preview(self, book: Any, options: ProfessionalFormattingOptions) -> Dict[str, Any]:
        """
        🎯 MÉTODO ESPECÍFICO PARA VISTA PREVIA PROFESIONAL
        
        Genera una vista previa profesional optimizada para el formatting-viewer.
        Es un wrapper del método principal con optimizaciones específicas para preview.
        """
        try:
            # Usar el método principal de formateo
            result = self.format_for_commercial_distribution(book, options)
            
            # Optimizaciones específicas para vista previa
            preview_data = result.get('preview_data', {})
            
            # Asegurar que tiene estadísticas básicas para la vista previa
            if 'statistics' not in preview_data:
                preview_data['statistics'] = {
                    'total_elements': len(result.get('structure', {}).elements) if result.get('structure') else 0,
                    'chapters': book.chapter_count or 10,
                    'words_estimated': book.get_word_count() if hasattr(book, 'get_word_count') else 0,
                    'index_entries': 0,
                    'toc_entries': 0
                }
            
            # Asegurar que tiene quality_score para la vista previa
            if 'quality_score' not in preview_data:
                quality_analysis = result.get('quality_analysis', {})
                preview_data['quality_score'] = {
                    'overall': quality_analysis.get('overall_score', 85.0),
                    'structure': quality_analysis.get('structure_score', 90.0),
                    'formatting': quality_analysis.get('formatting_score', 80.0),
                    'readability': quality_analysis.get('readability_score', 85.0),
                    'recommendations': ["Vista previa profesional generada exitosamente"]
                }
            
            return {
                'formatted_content': result.get('formatted_content', ''),
                'preview_data': preview_data,
                'quality_analysis': result.get('quality_analysis', {}),
                'structure': result.get('structure')
            }
            
        except Exception as e:
            # Fallback robusto para vista previa
            fallback_content = book.content_html or book.content or ""
            # 🎯 REINGENIERÍA: Template moderno maneja estructura directamente
            return {
                'formatted_content': fallback_content,
                'preview_data': {
                    'statistics': {
                        'total_elements': 0,
                        'chapters': book.chapter_count or 10,
                        'words_estimated': book.get_word_count() if hasattr(book, 'get_word_count') else 0,
                        'index_entries': 0,
                        'toc_entries': 0
                    },
                    'quality_score': {
                        'overall': 75.0,
                        'structure': 75.0,
                        'formatting': 75.0,
                        'readability': 75.0,
                        'recommendations': [f"Vista previa con contenido original: {str(e)}"]
                    },
                    'elements': []
                },
                'quality_analysis': {'overall_score': 75.0},
                'error': str(e)
            }
    
    def _parse_html_content(self, html_content: str, book: Any, options: ProfessionalFormattingOptions = None) -> BookStructure:
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
        
        # 🚀 MEJORA: Usar author_name de opciones si está disponible
        author_name = ""
        if options and hasattr(options, 'author_name') and options.author_name:
            author_name = options.author_name
        elif hasattr(book, 'user') and book.user and book.user.full_name:
            author_name = book.user.full_name
        
        return BookStructure(
            title=book.title,
            author=author_name,
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
        from ..services.html_shared_classes import HTMLElementType
        
        # Mapeo robusto de tags a tipos
        tag_type_map = {
            'h1': HTMLElementType.BOOK_TITLE,
            'h2': HTMLElementType.CHAPTER_TITLE,
            'h3': HTMLElementType.SECTION,
            'h4': HTMLElementType.SUBSECTION,
            'p': HTMLElementType.PARAGRAPH,
            'div': HTMLElementType.DIV,
            'span': HTMLElementType.SPAN,
            'section': HTMLElementType.CHAPTER,
            'em': HTMLElementType.EMPHASIS,
            'strong': HTMLElementType.STRONG,
            'blockquote': HTMLElementType.BLOCKQUOTE,
            'code': HTMLElementType.CODE,
            'ul': HTMLElementType.LIST,
            'ol': HTMLElementType.LIST,
            'li': HTMLElementType.LIST_ITEM
        }
        
        # Usar el tipo apropiado o UNKNOWN para elementos desconocidos
        element_type = tag_type_map.get(soup_element.name, HTMLElementType.UNKNOWN)
        
        # Extraer atributos
        attributes = {}
        for attr, value in soup_element.attrs.items():
            if isinstance(value, list):
                attributes[attr] = ' '.join(value)
            else:
                attributes[attr] = str(value)
        
        # Crear HTMLElement
        return HTMLElement(
            id=soup_element.get('id', f"element-{uuid.uuid4().hex[:8]}"),
            type=element_type,
            content=soup_element.get_text(),
            attributes=attributes,
            children=[],
            metadata={}
        )
    
    def _apply_professional_formatting(self, book_structure: BookStructure,
                                     options: ProfessionalFormattingOptions) -> BookStructure:
        """Aplica formateo profesional a la estructura del libro."""
        
        # Aplicar formateo profesional según opciones configuradas
        
        # Aplicar tema visual
        self._apply_theme(book_structure, options.theme)
        
        # Optimizar tipografía
        self._optimize_typography(book_structure, options)
        
        # 🎨 IMPLEMENTACIONES DE ESTILO
        
        # Drop Caps (Capitulares)
        if options.use_drop_caps:
            self._apply_drop_caps(book_structure, options)
        
        # Saltos de capítulo
        if options.use_chapter_breaks:
            self._apply_chapter_breaks(book_structure, options)
        
        # Encabezados y pies de página
        if options.use_headers_footers:
            self._apply_headers_footers(book_structure, options)
        
        # Tipografía profesional mejorada
        # 🚨 TEMPORALMENTE DESACTIVADO: Causaba corrupción de atributos en texto
        # TODO: Reimplementar de forma más limpia
        if False:  # options.use_professional_typography:
            self._apply_enhanced_professional_typography(book_structure, options)
        
        # Resaltar expresiones
        # 🚨 TEMPORALMENTE DESACTIVADO: También causa corrupción de atributos
        if False:  # options.highlight_expressions:
            self._apply_expression_highlighting(book_structure, options)
        
        # Enfatizar traducciones
        # 🚨 TEMPORALMENTE DESACTIVADO: También causa corrupción de atributos  
        if False:  # options.emphasize_translations:
            self._apply_translation_emphasis(book_structure, options)
        
        # ⚙️ IMPLEMENTACIONES AVANZADAS
        
        # Navegación TOC mejorada
        if options.enable_toc_navigation:
            self._enhance_navigation(book_structure)
            self._apply_advanced_toc_navigation(book_structure, options)
        
        # Índice automático real
        if options.enable_index_generation:
            book_structure.index = self._generate_automatic_index(book_structure)
            self._apply_real_index_generation(book_structure, options)
        
        # Marcadores
        if options.enable_bookmarks:
            self._apply_bookmark_generation(book_structure, options)
        
        # Funcionalidad de búsqueda
        if options.enable_search:
            self._apply_search_functionality(book_structure, options)
        
        # Optimización de tamaño de archivo
        if options.optimize_file_size:
            self._apply_file_size_optimization(book_structure, options)
        
        # Información editorial
        if options.include_publisher_info:
            self._apply_publisher_information(book_structure, options)
        
        # 📐 OTRAS IMPLEMENTACIONES
        
        # Espaciado mejorado de párrafos
        self._apply_enhanced_paragraph_spacing(book_structure, options)
        
        # ISBN completo
        if options.include_isbn and options.include_isbn.strip():
            self._apply_complete_isbn_integration(book_structure, options)
        
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
        
        # Dedicatoria
        if options.include_dedication:
            dedication_page = self._create_dedication_page(book_structure, options, book)
            new_elements.append(dedication_page)
        
        # Agradecimientos
        if options.include_acknowledgments:
            acknowledgments_page = self._create_acknowledgments_page(book_structure, options, book)
            new_elements.append(acknowledgments_page)
        
        # Prólogo
        if options.include_prologue:
            prologue_page = self._create_prologue_page(book_structure, options, book)
            new_elements.append(prologue_page)
        
        # ISBN y datos de catalogación
        if options.include_isbn:
            catalog_page = self._create_cataloging_page(options.include_isbn, book)
            new_elements.append(catalog_page)
        
        # Páginas de marketing (si aplica)
        if options.include_marketing_pages:
            marketing_pages = self._create_marketing_pages(book)
            new_elements.extend(marketing_pages)
        
        # Insertar elementos al inicio
        book_structure.elements = new_elements + book_structure.elements
        
        # Agregar elementos al final del libro
        end_elements = []
        
        # Epílogo (al final)
        if options.include_epilogue:
            epilogue_page = self._create_epilogue_page(book_structure, options, book)
            end_elements.append(epilogue_page)
        
        # Acerca del autor (al final)
        if options.include_about_author:
            about_author_page = self._create_about_author_page(book_structure, options, book)
            end_elements.append(about_author_page)
        
        # Agregar elementos finales
        book_structure.elements.extend(end_elements)
        
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
        
        # 🚫 MÉTODO DESHABILITADO: Causa corrupción con -webkit-font-smoothing y -moz-osx-font-smoothing
        # Estas propiedades CSS aparecían como texto plano en lugar de aplicarse correctamente
        return
        
        # Definir tipos de elementos que reciben formateo tipográfico
        typography_elements = [
            'paragraph', 'chapter-title', 'section', 'subsection', 
            'book-title', 'chapter', 'div', 'blockquote'
        ]
        
        # Estilos profesionales base
        professional_styles = {
            'text-rendering': 'optimizeLegibility',
            'font-feature-settings': "'kern' 1, 'liga' 1",
            '-webkit-font-smoothing': 'antialiased',
            '-moz-osx-font-smoothing': 'grayscale'
        }
        
        # Aplicar tipografía profesional a todos los elementos relevantes
        for element in book_structure.elements:
            if not element:
                continue
                
            should_format = (
                element.type.value in typography_elements or
                element.attributes.get('data-page-type') in [
                    'dedication', 'acknowledgments', 'prologue', 
                    'epilogue', 'about-author', 'title', 'copyright'
                ]
            )
            
            if should_format:
                # Preservar estilos existentes
                existing_style = element.attributes.get('style', '')
                
                # Crear diccionario de estilos desde string existente
                existing_styles = {}
                if existing_style:
                    for style_item in existing_style.split(';'):
                        if ':' in style_item:
                            key, value = style_item.split(':', 1)
                            existing_styles[key.strip()] = value.strip()
                
                # Determinar tamaño de fuente apropiado por tipo de elemento
                if 'title' in element.type.value.lower():
                    font_size = min(options.font_size_body + 8, 24)  # Títulos más grandes
                elif element.attributes.get('data-page-type') in ['dedication', 'acknowledgments', 'prologue', 'epilogue']:
                    font_size = options.font_size_body + 1  # Ligeramente más grande para páginas especiales
                else:
                    font_size = options.font_size_body
                
                # Aplicar nuevos estilos (preservando existentes)
                new_styles = {
                    'font-family': options.font_family,
                    'font-size': f'{font_size}pt',
                    'line-height': str(options.line_spacing),
                    **professional_styles
                }
                
                # Si hay espaciado de párrafo configurado, aplicarlo a párrafos
                if hasattr(options, 'paragraph_spacing') and element.type.value == 'paragraph':
                    new_styles['margin-bottom'] = f'{options.paragraph_spacing}pt'
                
                # Combinar estilos existentes con nuevos (nuevos tienen prioridad)
                final_styles = {**existing_styles, **new_styles}
                
                # Convertir diccionario de estilos a string CSS
                style_string = '; '.join([f'{key}: {value}' for key, value in final_styles.items()])
                element.attributes['style'] = style_string
                
                # Agregar clase para estilos profesionales si no existe
                current_class = element.attributes.get('class', '')
                if 'professional-typography' not in current_class:
                    element.attributes['class'] = f"{current_class} professional-typography".strip()
    
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
        from ..services.html_shared_classes import HTMLElement, HTMLElementType
        
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
        from ..services.html_shared_classes import HTMLElement, HTMLElementType
        
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
        from ..services.html_shared_classes import HTMLElement, HTMLElementType
        
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
        from ..services.html_shared_classes import HTMLElement, HTMLElementType
        
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
    
    def _create_dedication_page(self, book_structure: BookStructure,
                              options: ProfessionalFormattingOptions,
                              book: Any) -> 'HTMLElement':
        """
        🚀 REFACTORIZADO: Crea una página de dedicatoria profesional usando helper consolidado.
        
        Elimina ~50 líneas de código duplicado usando _create_content_page_generic().
        """
        return self._create_content_page_generic(
            book_structure=book_structure,
            options=options,
            book=book,
            content_type='dedication',
            claude_generator_method='generate_dedication',
            smart_fallback_method='_generate_smart_dedication',
            final_fallback_method='_get_smart_fallback_dedication'
        )
    
    def _generate_smart_dedication(self, params: ContentGenerationParams) -> str:
        """
        🚀 MEJORADO: Genera dedicatorias inteligentes completamente dinámicas.
        
        Sin hardcodes de idiomas específicos. Usa parámetros del libro para personalización.
        """
        # Determinar el enfoque basado en género y audiencia
        is_educational = params.genre.lower() in ['educational', 'academic', 'learning', 'tutorial']
        is_technical = params.genre.lower() in ['technical', 'programming', 'technology', 'software']
        is_business = params.genre.lower() in ['business', 'management', 'marketing', 'finance']
        is_creative = params.genre.lower() in ['fiction', 'creative', 'storytelling', 'narrative']
        is_self_help = params.genre.lower() in ['self_help', 'personal_development', 'motivation']
        
        # Determinar audiencia principal
        audience_context = ""
        if params.target_audience == 'children':
            audience_context = "jóvenes mentes curiosas"
        elif params.target_audience == 'teens':
            audience_context = "adolescentes en formación"
        elif params.target_audience in ['adult', 'young_adult']:
            audience_context = "adultos comprometidos con su crecimiento"
        elif params.target_audience == 'seniors':
            audience_context = "personas con experiencia que siguen aprendiendo"
        else:
            audience_context = "lectores dedicados"
        
        # Construir dedicatorias específicas pero genéricas
        if is_educational:
            dedication_focus = "estudiantes curiosos que nunca dejan de hacer preguntas y buscar respuestas"
            secondary_focus = "educadores comprometidos que transforman información en conocimiento y conocimiento en sabiduría"
            universal_message = "quienes creen que el aprendizaje es un viaje continuo de descubrimiento y crecimiento personal"
        elif is_technical:
            dedication_focus = "desarrolladores y tecnólogos apasionados que construyen el futuro con líneas de código"
            secondary_focus = "mentores técnicos que comparten su experiencia y guían a la próxima generación de innovadores"
            universal_message = "quienes ven en la tecnología una herramienta para resolver problemas reales y mejorar vidas"
        elif is_business:
            dedication_focus = "emprendedores visionarios y profesionales dedicados que buscan la excelencia en su campo"
            secondary_focus = "líderes empresariales que inspiran con su ejemplo y transforman organizaciones"
            universal_message = "quienes creen en el poder de la innovación, la estrategia y la ejecución efectiva"
        elif is_creative:
            dedication_focus = "soñadores y creativos que dan vida a historias y despiertan emociones a través de las palabras"
            secondary_focus = "lectores apasionados que encuentran en cada libro un mundo nuevo por explorar"
            universal_message = "quienes creen en el poder transformador de las narrativas y la imaginación"
        elif is_self_help:
            dedication_focus = "personas valientes que buscan activamente mejorar sus vidas y alcanzar su máximo potencial"
            secondary_focus = "individuos que no se conforman con la mediocridad y luchan por crear la mejor versión de sí mismos"
            universal_message = "quienes entienden que el cambio positivo comienza con una decisión y se sostiene con acción constante"
        else:
            # Dedicatoria genérica profesional
            dedication_focus = f"{audience_context} que buscan expandir sus conocimientos en esta área de especialización"
            secondary_focus = "profesionales y expertos que comparten generosamente su sabiduría y experiencia"
            universal_message = "quienes ven en cada libro una oportunidad de crecimiento, transformación y desarrollo personal"
        
        return f"""
        <div class="dedication-content">
            <h2 class="dedication-title">DEDICATORIA</h2>
            <div class="dedication-divider"></div>
            <div class="dedication-text">
                <p>Dedicado a {dedication_focus}.</p>
                
                <p>A {secondary_focus}, cuya dedicación y pasión hacen posible que recursos como este lleguen a manos de quienes más los necesitan.</p>
                
                <p>Y especialmente a {universal_message}.</p>
            </div>
        </div>
        """
    
    def _get_smart_fallback_dedication(self, params: ContentGenerationParams) -> str:
        """Dedicatoria de respaldo inteligente."""
        return f"""
        <div class="dedication-content">
            <h2 class="dedication-title">DEDICATORIA</h2>
            <div class="dedication-divider"></div>
            <div class="dedication-text">
                <p>Dedicado a todos los lectores comprometidos con el aprendizaje y el crecimiento personal.</p>
                <p>A quienes ven en el conocimiento una herramienta de transformación y progreso.</p>
            </div>
        </div>
        """
    
    def _create_acknowledgments_page(self, book_structure: BookStructure,
                                  options: ProfessionalFormattingOptions,
                                  book: Any) -> 'HTMLElement':
        """
        🚀 REFACTORIZADO: Crea una página de agradecimientos profesional usando helper consolidado.
        
        Elimina ~55 líneas de código duplicado usando _create_content_page_generic().
        """
        return self._create_content_page_generic(
            book_structure=book_structure,
            options=options,
            book=book,
            content_type='acknowledgments',
            claude_generator_method='generate_acknowledgments',
            smart_fallback_method='_generate_smart_acknowledgments',
            final_fallback_method='_get_smart_fallback_acknowledgments'
        )
    
    def _create_prologue_page(self, book_structure: BookStructure,
                            options: ProfessionalFormattingOptions,
                            book: Any) -> 'HTMLElement':
        """
        🚀 REFACTORIZADO: Crea un prólogo profesional usando helper consolidado.
        
        Elimina ~50 líneas de código duplicado usando _create_content_page_generic().
        """
        return self._create_content_page_generic(
            book_structure=book_structure,
            options=options,
            book=book,
            content_type='prologue',
            claude_generator_method='generate_prologue',
            smart_fallback_method='_generate_smart_prologue',
            final_fallback_method='_get_smart_fallback_prologue'
        )
    
    def _generate_smart_prologue(self, params: ContentGenerationParams) -> str:
        """
        🚀 MEJORADO: Genera prólogo inteligente completamente dinámico.
        
        Sin hardcodes de idiomas específicos. Usa género y contexto para personalización.
        """
        genre = params.genre.lower() if params.genre else "general"
        
        # Determinar categorías dinámicamente basadas en género, no en idioma específico
        is_educational = genre in ['educational', 'academic', 'learning', 'tutorial']
        is_technical = genre in ['technical', 'programming', 'technology', 'software']
        is_business = genre in ['business', 'management', 'marketing', 'finance']
        is_creative = genre in ['fiction', 'creative', 'storytelling', 'narrative', 'novel']
        is_self_help = genre in ['self_help', 'personal_development', 'motivation', 'lifestyle']
        
        # Prólogos dinámicos por categoría (no por idioma específico)
        if is_educational:
            approach_text = "una aproximación innovadora al aprendizaje"
            methodology_text = "metodología empleada combina principios pedagógicos modernos con técnicas probadas"
            goal_text = "que este recurso se convierta en tu compañero indispensable en este fascinante viaje de aprendizaje"
        elif is_technical:
            approach_text = "una guía práctica y actualizada en el dinámico mundo de la tecnología"
            methodology_text = "metodología combina fundamentos sólidos con aplicaciones prácticas"
            goal_text = "que este conocimiento se convierta en una herramienta poderosa para tu crecimiento profesional"
        elif is_business:
            approach_text = "una herramienta integral para el desarrollo profesional y empresarial"
            methodology_text = "enfoque combina teoría empresarial con estrategias prácticas comprobadas"
            goal_text = "que este recurso impulse tu éxito en el mundo empresarial"
        elif is_creative:
            approach_text = "una ventana hacia la exploración creativa y narrativa"
            methodology_text = "metodología integra técnicas narrativas con principios de construcción creativa"
            goal_text = "que esta obra inspire tu propia creatividad y expresión"
        elif is_self_help:
            approach_text = "una guía transformadora para el crecimiento personal"
            methodology_text = "enfoque combina principios psicológicos con estrategias prácticas de desarrollo personal"
            goal_text = "que este libro sea el catalizador de tu transformación personal"
        else:
            # Genérico profesional dinámico
            approach_text = "una herramienta integral para el aprendizaje y desarrollo"
            methodology_text = "metodología combina teoría fundamentada con aplicaciones prácticas"
            goal_text = "que este conocimiento transforme tu perspectiva y potenciar tu desarrollo"
        
        return f"""
        <div class="prologue-content">
            <h2 class="prologue-title">PRÓLOGO</h2>
            <div class="prologue-divider"></div>
            <div class="prologue-text">
                <p>"{params.title}" representa {approach_text}, diseñada para ofrecer una experiencia de aprendizaje enriquecedora, práctica y transformadora.</p>

                <p>En un mundo donde el conocimiento evoluciona constantemente, la capacidad de aprender, adaptarse y aplicar nuevos conceptos se convierte en la diferencia entre el estancamiento y el crecimiento continuo.</p>

                <p>Este libro presenta un enfoque integral estructurado cuidadosamente. La {methodology_text}, creando un sistema de aprendizaje eficiente y motivador.</p>

                <p>Cada sección ha sido desarrollada siguiendo principios pedagógicos modernos, incorporando ejemplos relevantes, casos de estudio y ejercicios que refuerzan el aprendizaje y facilitan la implementación efectiva.</p>

                <p>Esperamos {goal_text}. Te invitamos a descubrir las oportunidades que este conocimiento puede abrir en tu camino.</p>
                
                <p class="prologue-signature">
                    <strong>Los autores</strong><br>
                    <em>Buko AI Editorial</em>
                </p>
            </div>
        </div>
        """
    
    def _get_smart_fallback_prologue(self, params: ContentGenerationParams) -> str:
        """Prólogo de respaldo inteligente."""
        return f"""
        <div class="prologue-content">
            <h2 class="prologue-title">PRÓLOGO</h2>
            <div class="prologue-divider"></div>
            <div class="prologue-text">
                <p>"{params.title}" es el resultado de un cuidadoso proceso de investigación y desarrollo, diseñado para ofrecer una experiencia de aprendizaje valiosa y transformadora.</p>
                <p>Esperamos que este libro se convierta en una herramienta indispensable en tu camino hacia el dominio del tema y el crecimiento personal.</p>
                
                <p class="prologue-signature">
                    <strong>Los autores</strong><br>
                    <em>Buko AI Editorial</em>
                </p>
            </div>
        </div>
        """
    
    def _create_epilogue_page(self, book_structure: BookStructure,
                            options: ProfessionalFormattingOptions,
                            book: Any) -> 'HTMLElement':
        """
        🚀 REFACTORIZADO: Crea un epílogo profesional usando helper consolidado.
        
        Elimina ~55 líneas de código duplicado usando _create_content_page_generic().
        """
        return self._create_content_page_generic(
            book_structure=book_structure,
            options=options,
            book=book,
            content_type='epilogue',
            claude_generator_method='generate_epilogue',
            smart_fallback_method='_generate_smart_epilogue',
            final_fallback_method='_get_smart_fallback_epilogue'
        )
    
    def _generate_smart_epilogue(self, params: ContentGenerationParams) -> str:
        """
        🚀 MEJORADO: Genera epílogo inteligente completamente dinámico.
        
        Sin hardcodes de idiomas específicos. Usa género y contexto para personalización.
        """
        genre = params.genre.lower() if params.genre else "general"
        
        # Determinar categorías dinámicamente basadas en género, no en idioma específico
        is_educational = genre in ['educational', 'academic', 'learning', 'tutorial']
        is_technical = genre in ['technical', 'programming', 'technology', 'software']
        is_business = genre in ['business', 'management', 'marketing', 'finance']
        is_creative = genre in ['fiction', 'creative', 'storytelling', 'narrative', 'novel']
        is_self_help = genre in ['self_help', 'personal_development', 'motivation', 'lifestyle']
        
        # Epílogos dinámicos por categoría (no por idioma específico)
        if is_educational:
            journey_text = "Has completado un valioso recorrido por este fascinante campo del conocimiento"
            process_text = "El dominio de cualquier disciplina es un proceso continuo que trasciende las páginas de cualquier libro"
            encouragement_text = "Te animamos a continuar expandiendo tus conocimientos, manteniéndote siempre receptivo a nuevas ideas y enfoques"
            mastery_text = "El camino hacia la maestría es gradual pero extraordinariamente gratificante"
            closing_text = "¡Felicitaciones! Has dado un paso importante hacia el dominio de este conocimiento"
        elif is_technical:
            journey_text = "Has completado un importante recorrido por conceptos y técnicas que fortalecerán significativamente tus habilidades profesionales"
            process_text = "En el mundo de la tecnología, el aprendizaje nunca termina. Las tendencias evolucionan, surgen nuevos paradigmas y las mejores prácticas se refinan constantemente"
            encouragement_text = "Te animamos a aplicar estos conocimientos en proyectos reales, experimentar con diferentes enfoques y mantener siempre una mentalidad de mejora continua"
            mastery_text = "La maestría se construye a través de la práctica deliberada y la reflexión constante"
            closing_text = "¡Felicitaciones por completar este paso en tu desarrollo profesional!"
        elif is_business:
            journey_text = "Has completado un importante capítulo en tu desarrollo profesional y empresarial"
            process_text = "En el dinámico mundo de los negocios, el crecimiento continuo es esencial para mantener la relevancia y competitividad"
            encouragement_text = "Te alentamos a aplicar estas estrategias en tu contexto profesional, adaptándolas a tu realidad específica"
            mastery_text = "El éxito empresarial se construye día a día, decisión tras decisión, estrategia tras estrategia"
            closing_text = "¡Felicitaciones! Estás en el camino correcto hacia el éxito empresarial"
        elif is_creative:
            journey_text = "Has completado una exploración creativa que ha enriquecido tu perspectiva artística y narrativa"
            process_text = "La creatividad es un proceso en constante evolución, alimentado por nuevas experiencias y perspectivas"
            encouragement_text = "Te animamos a continuar explorando, experimentando y expresando tu voz única"
            mastery_text = "La maestría creativa se desarrolla a través de la práctica constante y la búsqueda de inspiración"
            closing_text = "¡Felicitaciones por nutrir tu espíritu creativo!"
        elif is_self_help:
            journey_text = "Has completado un importante viaje de autodescubrimiento y crecimiento personal"
            process_text = "El desarrollo personal es un proceso continuo de reflexión, aprendizaje y transformación"
            encouragement_text = "Te animamos a integrar conscientemente estos principios en tu vida diaria"
            mastery_text = "El crecimiento personal se construye a través de pequeñas acciones consistentes y reflexión honesta"
            closing_text = "¡Felicitaciones por invertir en tu crecimiento personal!"
        else:
            # Genérico profesional dinámico
            journey_text = f'Al completar "{params.title}", has dado un paso significativo en tu proceso de crecimiento y desarrollo'
            process_text = "El verdadero valor del conocimiento se revela cuando se aplica en la práctica"
            encouragement_text = "Te animamos a reflexionar sobre lo aprendido, a cuestionarlo, a expandirlo y a compartirlo con otros"
            mastery_text = "El conocimiento se multiplica cuando se transmite y encuentra su mayor propósito cuando transforma positivamente la realidad"
            closing_text = "Gracias por acompañarnos en este viaje de descubrimiento"
        
        return f"""
        <div class="epilogue-content">
            <h2 class="epilogue-title">EPÍLOGO</h2>
            <div class="epilogue-divider"></div>
            <div class="epilogue-text">
                <p>{journey_text}. Este viaje te ha llevado desde conceptos fundamentales hasta aplicaciones avanzadas que enriquecen tu comprensión y capacidades.</p>

                <p>{process_text}. La verdadera maestría se alcanza a través de la práctica constante, la aplicación consciente de lo aprendido y la búsqueda continua de mejora.</p>

                <p>{encouragement_text}. Mantente siempre abierto a nuevas oportunidades de aprendizaje y crecimiento.</p>

                <p>{mastery_text}. Cada paso que das te acerca más a la excelencia en este campo.</p>

                <p class="epilogue-closing"><strong>{closing_text}</strong></p>
                
                <p class="epilogue-signature">
                    <em>Que este conocimiento abra nuevos horizontes de oportunidad</em><br>
                    <strong>Buko AI Editorial</strong>
                </p>
            </div>
        </div>
        """
    
    def _get_smart_fallback_epilogue(self, params: ContentGenerationParams) -> str:
        """Epílogo de respaldo inteligente."""
        return f"""
        <div class="epilogue-content">
            <h2 class="epilogue-title">EPÍLOGO</h2>
            <div class="epilogue-divider"></div>
            <div class="epilogue-text">
                <p>Has completado exitosamente "{params.title}". Esperamos que este conocimiento se convierta en una herramienta valiosa para tu crecimiento personal y profesional.</p>
                <p>Te agradecemos por acompañarnos en este viaje de aprendizaje.</p>
                
                <p class="epilogue-signature">
                    <strong>Con nuestros mejores deseos</strong><br>
                    <em>Buko AI Editorial</em>
                </p>
            </div>
        </div>
        """
    
    def _create_about_author_page(self, book_structure: BookStructure,
                                options: ProfessionalFormattingOptions,
                                book: Any) -> 'HTMLElement':
        """
        🚀 REFACTORIZADO: Crea una página 'Acerca del Autor' profesional usando helper consolidado.
        
        Elimina ~155 líneas de código duplicado usando _create_content_page_generic().
        """
        return self._create_content_page_generic(
            book_structure=book_structure,
            options=options,
            book=book,
            content_type='about-author',
            claude_generator_method='generate_about_author',
            smart_fallback_method='_generate_smart_about_author',
            final_fallback_method='_get_smart_fallback_about_author'
        )
    
    def _generate_smart_about_author(self, params: ContentGenerationParams) -> str:
        """
        🚀 MEJORADO: Genera página 'Acerca del Autor' completamente dinámica.
        
        Sin hardcodes de idiomas específicos. Usa género y contexto para personalización.
        """
        author_name = params.author_name
        genre = params.genre.lower() if params.genre else "general"
        
        # Determinar categorías dinámicamente basadas en género, no en idioma específico
        is_educational = genre in ['educational', 'academic', 'learning', 'tutorial']
        is_technical = genre in ['technical', 'programming', 'technology', 'software']
        is_business = genre in ['business', 'management', 'marketing', 'finance']
        is_creative = genre in ['fiction', 'creative', 'storytelling', 'narrative', 'novel']
        is_self_help = genre in ['self_help', 'personal_development', 'motivation', 'lifestyle']
        
        # Biografías dinámicas por categoría (no por idioma específico)
        if is_educational:
            bio_focus = """es un especialista en pedagogía y educación, con particular expertise en la creación de recursos de aprendizaje efectivos. Su enfoque combina metodologías tradicionales con innovaciones tecnológicas para crear experiencias de aprendizaje motivadoras."""
            expertise = """Especializado en pedagogía moderna y técnicas de aprendizaje acelerado, ha desarrollado metodologías únicas que facilitan la adquisición natural de conocimientos complejos."""
        elif is_technical:
            bio_focus = """es un desarrollador y educador técnico con amplia experiencia en la creación de recursos educativos para profesionales de la tecnología."""
            expertise = """Especializado en pedagogía técnica y desarrollo de software, combina experiencia práctica en la industria con habilidades pedagógicas para crear contenido técnico accesible y aplicable."""
        elif is_business:
            bio_focus = """es un consultor empresarial y educador especializado en el desarrollo de recursos formativos para profesionales y empresarios."""
            expertise = """Con experiencia en estrategia empresarial y desarrollo profesional, ha creado recursos que preparan a los lectores para enfrentar desafíos del mundo empresarial moderno."""
        elif is_creative:
            bio_focus = """es un escritor y educador creativo con amplia experiencia en el desarrollo de contenidos narrativos y artísticos."""
            expertise = """Especializado en técnicas de escritura creativa y desarrollo narrativo, combina inspiración artística con metodología estructurada para crear obras que conectan con el lector."""
        elif is_self_help:
            bio_focus = """es un coach y educador especializado en desarrollo personal, enfocado en crear recursos que empoderen a las personas en su crecimiento personal."""
            expertise = """Con experiencia en psicología aplicada y coaching personal, ha desarrollado metodologías que combinan ciencia del comportamiento con aplicación práctica."""
        else:
            # Genérico profesional dinámico
            bio_focus = f"""es un autor y educador comprometido con la creación de recursos de aprendizaje de alta calidad en el área de {genre}, enfocado en hacer el conocimiento accesible y aplicable."""
            expertise = """Con experiencia en diseño pedagógico y desarrollo de contenidos educativos, se especializa en crear experiencias de aprendizaje estructuradas que faciliten la comprensión y aplicación práctica."""
        
        return f"""
        <div class="about-author-content">
            <h2 class="about-author-title">ACERCA DEL AUTOR</h2>
            <div class="about-author-divider"></div>
            <div class="about-author-text">
                <div class="author-bio">
                    <p><strong>{author_name}</strong> {bio_focus}</p>
                    
                    <p>{expertise}</p>
                    
                    <p>Utilizando tecnología de inteligencia artificial avanzada, ha desarrollado una metodología innovadora que combina rigor académico con accesibilidad, creando recursos educativos que se adaptan a diferentes estilos de aprendizaje y niveles de experiencia.</p>
                    
                    <p>Su filosofía educativa se centra en la creación de experiencias de aprendizaje que no solo transmitan conocimiento, sino que también inspiren confianza y motiven el crecimiento continuo de los estudiantes.</p>
                </div>
                
                <div class="author-works">
                    <h3>Enfoque Pedagógico</h3>
                    <p>Cada obra de {author_name} está diseñada con principios pedagógicos sólidos, incorporando técnicas probadas de retención y aplicación del conocimiento. Su objetivo es crear recursos que no solo eduquen, sino que también empoderen a los lectores para aplicar lo aprendido en situaciones reales.</p>
                </div>
                
                <div class="author-mission">
                    <h3>Misión</h3>
                    <p>Democratizar el acceso a educación de calidad, utilizando tecnología innovadora para crear recursos que transformen la manera en que las personas aprenden y crecen profesionalmente.</p>
                </div>
                
                <div class="author-contact">
                    <h3>Más Información</h3>
                    <p>Descubre más recursos educativos innovadores en:</p>
                    <p><strong>www.buko-ai.com</strong></p>
                    <p>Contacto: contacto@buko-ai.com</p>
                </div>
                
                <div class="author-acknowledgment">
                    <p><em>"La educación de calidad es un derecho universal. Mi compromiso es hacerla accesible, práctica y transformadora para cada persona que busca crecer y mejorar."</em></p>
                    <p class="signature">— {author_name}</p>
                </div>
            </div>
        </div>
        """
    
    def _get_smart_fallback_about_author(self, params: ContentGenerationParams) -> str:
        """Página 'Acerca del Autor' de respaldo inteligente."""
        return f"""
        <div class="about-author-content">
            <h2 class="about-author-title">ACERCA DEL AUTOR</h2>
            <div class="about-author-divider"></div>
            <div class="about-author-text">
                <div class="author-bio">
                    <p><strong>{params.author_name}</strong> es un autor comprometido con la creación de contenido educativo de alta calidad.</p>
                    <p>Su enfoque combina experiencia pedagógica con innovación tecnológica para crear recursos de aprendizaje efectivos y accesibles.</p>
                </div>
                
                <div class="author-contact">
                    <h3>Más Información</h3>
                    <p><strong>www.buko-ai.com</strong></p>
                </div>
                
                <div class="author-acknowledgment">
                    <p><em>"El conocimiento es poder cuando se comparte y aplica."</em></p>
                    <p class="signature">— {params.author_name}</p>
                </div>
            </div>
        </div>
        """
    
    def _generate_smart_acknowledgments(self, params: ContentGenerationParams) -> str:
        """
        🚀 MEJORADO: Genera agradecimientos inteligentes completamente dinámicos.
        
        Sin hardcodes de idiomas específicos. Usa parámetros del libro para personalización.
        """
        # Determinar categorías basadas en género y contexto
        is_educational = params.genre.lower() in ['educational', 'academic', 'learning', 'tutorial']
        is_technical = params.genre.lower() in ['technical', 'programming', 'technology', 'software']
        is_business = params.genre.lower() in ['business', 'management', 'marketing', 'finance']
        is_creative = params.genre.lower() in ['fiction', 'creative', 'storytelling', 'narrative']
        
        # Construir categorías de colaboradores dinámicamente
        expert_category = "expertos en la materia"
        reviewers_category = "revisores especializados"
        community_category = "comunidad de lectores"
        institutional_category = "instituciones colaboradoras"
        
        if is_educational:
            expert_category = "académicos e investigadores educativos"
            reviewers_category = "pedagogos y educadores"
            community_category = "estudiantes y profesionales del aprendizaje"
            institutional_category = "instituciones educativas y bibliotecas académicas"
        elif is_technical:
            expert_category = "desarrolladores senior y expertos técnicos"
            reviewers_category = "equipos de revisión técnica"
            community_category = "comunidad de desarrolladores y tecnólogos"
            institutional_category = "empresas tecnológicas e innovadoras"
        elif is_business:
            expert_category = "profesionales y consultores empresariales"
            reviewers_category = "líderes y ejecutivos del sector"
            community_category = "emprendedores y profesionales de negocios"
            institutional_category = "organizaciones empresariales y cámaras de comercio"
        elif is_creative:
            expert_category = "escritores y creativos profesionales"
            reviewers_category = "editores y correctores literarios"
            community_category = "lectores y amantes de la literatura"
            institutional_category = "editoriales y centros culturales"
        
        return f"""
        <div class="acknowledgments-content">
            <h2 class="acknowledgments-title">AGRADECIMIENTOS</h2>
            <div class="acknowledgments-divider"></div>
            <div class="acknowledgments-text">
                <p>Queremos expresar nuestro más sincero agradecimiento a todas las personas e instituciones que hicieron posible la creación de "{params.title}".</p>
                
                <p><strong>A los {expert_category}</strong> que han compartido su conocimiento especializado, experiencia práctica y mejores prácticas, enriqueciendo significativamente el contenido y la calidad profesional de esta obra.</p>
                
                <p><strong>A los {reviewers_category}</strong> que han dedicado tiempo y expertise a validar la exactitud, relevancia y utilidad del material presentado, asegurando que cumpla con los más altos estándares de su área de especialización.</p>
                
                <p><strong>A la {community_category}</strong> cuyas preguntas, sugerencias y retroalimentación continua han ayudado a identificar las necesidades más importantes y a refinar constantemente el enfoque y contenido de este recurso.</p>
                
                <p><strong>A las {institutional_category}</strong> que han facilitado acceso a recursos especializados, investigaciones actualizadas y datos necesarios para desarrollar un contenido completo, actualizado y de alta calidad.</p>
                
                <p><strong>Al equipo de {params.author_name} y Buko AI</strong> por su innovación tecnológica y compromiso inquebrantable con la creación de recursos educativos de excelencia y accesibles para todos.</p>
                
                <p>Sin su colaboración, expertise y apoyo constante, este proyecto no habría alcanzado el nivel de profesionalidad y utilidad que presenta.</p>
                
                <p class="acknowledgments-signature">
                    <em>Con profunda gratitud por la colaboración recibida</em><br>
                    <strong>{params.author_name}</strong><br>
                    <em>Autor</em>
                </p>
            </div>
        </div>
        """
    
    def _get_smart_fallback_acknowledgments(self, params: ContentGenerationParams) -> str:
        """Agradecimientos de respaldo inteligente."""
        return f"""
        <div class="acknowledgments-content">
            <h2 class="acknowledgments-title">AGRADECIMIENTOS</h2>
            <div class="acknowledgments-divider"></div>
            <div class="acknowledgments-text">
                <p>Agradecemos profundamente a todos los expertos, educadores y miembros de la comunidad que hicieron posible la creación de "{params.title}".</p>
                
                <p>Su colaboración y expertise han sido fundamentales para desarrollar este recurso educativo de calidad.</p>
                
                <p class="acknowledgments-signature">
                    <strong>El equipo editorial</strong><br>
                    <em>Buko AI</em>
                </p>
            </div>
        </div>
        """
    
    # ========================================
    # 🚀 MÉTODOS HELPER CONSOLIDADOS
    # ========================================
    
    def _prepare_content_generation_params(self, book_structure: BookStructure, book: Any) -> 'ContentGenerationParams':
        """
        Helper consolidado para preparar parámetros de generación de contenido.
        
        Evita duplicación en todos los métodos _create_*_page().
        """
        from .dynamic_content_generator import ContentGenerationParams
        
        return ContentGenerationParams(
            title=book_structure.title or getattr(book, 'title', 'Libro'),
            genre=getattr(book, 'genre', 'educativo'),
            language=getattr(book, 'language', 'es'),
            target_audience=getattr(book, 'target_audience', 'general'),
            author_name=book_structure.author or 'Autor',
            key_topics=getattr(book, 'key_topics', None),
            tone=getattr(book, 'tone', 'professional')
        )
    
    def _extract_book_architecture(self, book: Any) -> dict:
        """
        Helper consolidado para extraer arquitectura del libro.
        
        Evita duplicación en todos los métodos _create_*_page().
        """
        architecture = getattr(book, 'architecture', {}) if hasattr(book, 'architecture') else {}
        if isinstance(architecture, str):
            try:
                import json
                architecture = json.loads(architecture)
            except:
                architecture = {}
        return architecture
    
    def _create_content_page_generic(self, 
                                   book_structure: BookStructure,
                                   options: 'ProfessionalFormattingOptions',
                                   book: Any,
                                   content_type: str,
                                   claude_generator_method: str,
                                   smart_fallback_method: str,
                                   final_fallback_method: str) -> 'HTMLElement':
        """
        🚀 HELPER GENÉRICO: Consolida la lógica común de todos los métodos _create_*_page.
        
        Elimina duplicación masiva reduciendo ~200 líneas de código repetitivo.
        
        Args:
            content_type: Tipo de contenido ('dedication', 'prologue', 'epilogue', etc.)
            claude_generator_method: Nombre del método en DynamicContentGenerator
            smart_fallback_method: Nombre del método _generate_smart_*
            final_fallback_method: Nombre del método _get_smart_fallback_*
        """
        from ..services.html_shared_classes import HTMLElement, HTMLElementType
        from .dynamic_content_generator import DynamicContentGenerator
        
        # Preparar parámetros (lógica consolidada)
        params = self._prepare_content_generation_params(book_structure, book)
        
        # Extraer arquitectura (lógica consolidada)
        architecture = self._extract_book_architecture(book)
        
        # Generar contenido con sistema de fallback triple
        try:
            generator = DynamicContentGenerator()
            
            # Intentar Claude AI primero
            import asyncio
            try:
                claude_method = getattr(generator, claude_generator_method)
                content = asyncio.run(claude_method(params, architecture))
            except Exception as async_error:
                # Fallback a método inteligente
                smart_method = getattr(self, smart_fallback_method)
                content = smart_method(params)
        except Exception as e:
            # Fallback final a método genérico
            final_method = getattr(self, final_fallback_method)
            content = final_method(params)
        
        return HTMLElement(
            id=f"{content_type.replace('_', '-')}-page",
            type=HTMLElementType.PARAGRAPH,
            content=content,
            attributes={
                'class': f'{content_type.replace("_", "-")}-page professional dynamic-content',
                'data-page-type': content_type
            },
            children=[],
            metadata={
                'content_type': content_type,
                'generation_method': 'dynamic_ai_enhanced',
                'optional_element': True, 
                'dynamic_content': True,
                'personalized': True
            }
        )
    
    
    # ========================================
    # 🎨 IMPLEMENTACIONES DE ESTILO PROFESIONAL
    # ========================================
    
    def _apply_drop_caps(self, book_structure: BookStructure, options: ProfessionalFormattingOptions) -> None:
        """Implementa Drop Caps (Capitulares) para primeros párrafos de capítulos."""
        
        # Implementación más robusta que funciona con diferentes estructuras
        drop_caps_applied = 0
        
        for i, element in enumerate(book_structure.elements):
            if not element or not element.content:
                continue
            
            # Aplicar drop caps a elementos que parecen inicios de capítulo
            # O a los primeros párrafos si no hay estructura de capítulo clara
            should_apply_drop_cap = False
            
            # Caso 1: Es un elemento chapter
            if element.type.value == 'chapter':
                should_apply_drop_cap = True
            
            # Caso 2: Es un párrafo que parece inicio de capítulo (contiene títulos)
            elif element.type.value == 'paragraph':
                content_clean = element.content.strip()
                # Si contiene h1, h2, o parece un título
                if any(tag in content_clean.lower() for tag in ['<h1', '<h2', 'capítulo', 'chapter']):
                    should_apply_drop_cap = True
                # O si es uno de los primeros elementos del libro
                elif i < 5 and len(content_clean) > 50:
                    should_apply_drop_cap = True
            
            if should_apply_drop_cap and drop_caps_applied < 3:  # Limitar a 3 drop caps
                content = element.content.strip()
                
                # Extraer primer carácter de texto real (no HTML)
                import re
                text_content = re.sub(r'<[^>]+>', '', content)
                text_content = text_content.strip()
                
                if text_content and len(text_content) > 1:
                    first_char = text_content[0]
                    
                    # Modificar el contenido para incluir drop cap
                    drop_cap_span = f'<span class="drop-cap-letter" data-first-letter="{first_char}">{first_char}</span>'
                    
                    # Insertar el drop cap al inicio del contenido de texto
                    if content.startswith('<'):
                        # Si empieza con HTML, insertar después del primer tag
                        modified_content = re.sub(r'^(<[^>]+>)(.)', r'\1' + drop_cap_span + r'\2', content, count=1)
                        if modified_content == content:  # Si no se pudo insertar así
                            modified_content = drop_cap_span + content
                    else:
                        # Si es texto plano, reemplazar primer carácter
                        modified_content = drop_cap_span + content[1:]
                    
                    element.content = modified_content
                    
                    # Añadir atributos de drop cap
                    current_class = element.attributes.get('class', '')
                    element.attributes['class'] = f"{current_class} has-drop-cap".strip()
                    element.attributes['data-drop-cap'] = 'true'
                    element.attributes['data-drop-cap-char'] = first_char
                    
                    drop_caps_applied += 1
    
    def _apply_chapter_breaks(self, book_structure: BookStructure, options: ProfessionalFormattingOptions) -> None:
        """Implementa saltos de página profesionales entre capítulos."""
        
        for i, element in enumerate(book_structure.elements):
            if not element or element.type.value != 'chapter':
                continue
                
            # Aplicar salto de página antes del capítulo (excepto el primero)
            if i > 0:
                element.attributes['style'] = element.attributes.get('style', '') + '; page-break-before: always;'
                element.attributes['data-chapter-break'] = 'true'
            
            # Añadir clase para styling específico
            current_class = element.attributes.get('class', '')
            element.attributes['class'] = f"{current_class} chapter-with-breaks".strip()
            
            # Configurar área de capítulo
            element.attributes['data-formatting'] = 'professional-chapter'
    
    def _apply_headers_footers(self, book_structure: BookStructure, options: ProfessionalFormattingOptions) -> None:
        """Implementa encabezados y pies de página profesionales."""
        
        # Configuración de headers/footers
        book_title = book_structure.title or "Libro"
        author_name = book_structure.author or "Autor"
        
        # Aplicar headers y footers a elementos principales
        for element in book_structure.elements:
            if not element:
                continue
                
            # Solo aplicar a capítulos y secciones principales
            if element.type.value in ['chapter', 'section']:
                
                # Header con título del libro (páginas pares)
                header_content = f'''
                <div class="page-header even-page" data-header-type="book-title">
                    <span class="header-text">{book_title}</span>
                </div>'''
                
                # Header con nombre del capítulo (páginas impares)
                chapter_title = self._extract_chapter_title(element)
                header_odd_content = f'''
                <div class="page-header odd-page" data-header-type="chapter-title">
                    <span class="header-text">{chapter_title}</span>
                </div>'''
                
                # Footer con número de página y autor
                footer_content = f'''
                <div class="page-footer" data-footer-type="author-page">
                    <span class="footer-left">{author_name}</span>
                    <span class="footer-center">·</span>
                    <span class="footer-right page-number" data-page-number="auto">{{page}}</span>
                </div>'''
                
                # Agregar headers y footers como metadatos del elemento
                element.metadata['header_even'] = header_content.strip()
                element.metadata['header_odd'] = header_odd_content.strip() 
                element.metadata['footer'] = footer_content.strip()
                element.attributes['data-has-headers-footers'] = 'true'
    
    def _extract_chapter_title(self, chapter_element: HTMLElement) -> str:
        """Extrae el título de un capítulo para headers."""
        # Buscar título en el contenido del capítulo
        content = chapter_element.content
        
        # Extraer de HTML si existe
        import re
        title_match = re.search(r'<h[1-6][^>]*>([^<]+)</h[1-6]>', content)
        if title_match:
            return title_match.group(1).strip()
        
        # Extraer título simple
        title_match = re.search(r'^([^\n\.]{1,60})', content.strip())
        if title_match:
            return title_match.group(1).strip()
        
        return "Capítulo"
    
    def _apply_enhanced_professional_typography(self, book_structure: BookStructure, options: ProfessionalFormattingOptions) -> None:
        """Aplica tipografía profesional mejorada con características avanzadas."""
        
        # 🚫 MÉTODO DESHABILITADO: Causa corrupción de CSS en el contenido
        # Las propiedades CSS como hyphenate-limit-zone, font-smoothing, etc.
        # aparecían como texto plano en lugar de aplicarse correctamente
        return
        
        # Configuraciones tipográficas avanzadas
        advanced_typography = {
            'font-feature-settings': '"kern" 1, "liga" 1, "clig" 1, "calt" 1',
            'font-variant-ligatures': 'common-ligatures',
            'text-rendering': 'optimizeLegibility',
            'font-smooth': 'always',
            '-webkit-font-smoothing': 'antialiased',
            '-moz-osx-font-smoothing': 'grayscale',
            'font-optical-sizing': 'auto',
            'hyphens': 'auto',
            'hyphenate-limit-chars': '6 3 3',
            'hyphenate-limit-lines': '2',
            'hyphenate-limit-last': 'always',
            'hyphenate-limit-zone': '8%'
        }
        
        # Aplicar a todos los elementos de texto
        for element in book_structure.elements:
            if not element:
                continue
                
            if element.type.value in ['paragraph', 'chapter', 'section', 'subsection']:
                
                # Construir estilos mejorados
                current_style = element.attributes.get('style', '')
                new_styles = []
                
                for prop, value in advanced_typography.items():
                    new_styles.append(f"{prop}: {value}")
                
                enhanced_style = "; ".join(new_styles)
                
                if current_style:
                    element.attributes['style'] = f"{current_style}; {enhanced_style}"
                else:
                    element.attributes['style'] = enhanced_style
                
                # Agregar clases específicas
                current_class = element.attributes.get('class', '')
                element.attributes['class'] = f"{current_class} enhanced-typography".strip()
                element.attributes['data-typography'] = 'enhanced-professional'
    
    def _apply_expression_highlighting(self, book_structure: BookStructure, options: ProfessionalFormattingOptions) -> None:
        """Implementa resaltado de expresiones importantes."""
        
        # 🚫 MÉTODO DESHABILITADO: Causa corrupción con clases expression-highlight
        # que aparecían como texto plano en lugar de aplicarse como CSS
        return
        
        # Patrones de expresiones que deben ser resaltadas
        expression_patterns = [
            r'\b\d+\.\s*(.{10,100}?)(?=\n|\.|:|;)',  # Expresiones numeradas
            r'<strong>([^<]+)</strong>',  # Texto en negrita
            r'\*\*([^*]+)\*\*',  # Texto en markdown bold
            r'"([^"]{5,50})"',  # Frases entre comillas
            r'([A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+(?:\s+[a-záéíóúüñ]+)*):',  # Términos seguidos de dos puntos
        ]
        
        for element in book_structure.elements:
            if not element or element.type.value not in ['paragraph', 'section', 'subsection']:
                continue
                
            content = element.content
            if not content:
                continue
            
            # Aplicar highlighting a cada patrón
            modified_content = content
            import re
            
            for pattern in expression_patterns:
                def highlight_match(match):
                    highlighted_text = match.group(1) if match.groups() else match.group(0)
                    return f'<span class="expression-highlight" data-expression-type="auto">{highlighted_text}</span>'
                
                modified_content = re.sub(pattern, highlight_match, modified_content)
            
            # Solo actualizar si hubo cambios
            if modified_content != content:
                element.content = modified_content
                element.attributes['data-has-highlighting'] = 'true'
                
                current_class = element.attributes.get('class', '')
                element.attributes['class'] = f"{current_class} has-expression-highlighting".strip()
    
    def _apply_translation_emphasis(self, book_structure: BookStructure, options: ProfessionalFormattingOptions) -> None:
        """Implementa énfasis en traducciones para libros de idiomas."""
        
        # 🚫 MÉTODO DESHABILITADO: Causa corrupción con clases translation-emphasis
        # que aparecían como texto plano en lugar de aplicarse como CSS
        return
        
        # Patrones de traducción comunes
        translation_patterns = [
            r'(?:significa|means|signifie|bedeutet)\s*[:""]?\s*([^".\n]{5,50})["."]?',  # "significa X"
            r'(?:Traducción|Translation|Traduction|Übersetzung):\s*([^.\n]{5,100})',  # "Traducción: X"
            r'\(([^)]{5,50})\)',  # Texto entre paréntesis
            r'=\s*([^.\n]{5,50})',  # Traducciones con =
            r'→\s*([^.\n]{5,50})',  # Traducciones con →
        ]
        
        for element in book_structure.elements:
            if not element or element.type.value not in ['paragraph', 'section']:
                continue
                
            content = element.content
            if not content:
                continue
            
            modified_content = content
            import re
            
            for pattern in translation_patterns:
                def emphasize_translation(match):
                    translation = match.group(1).strip()
                    return f'<span class="translation-emphasis" data-translation="true" title="Traducción">{translation}</span>'
                
                modified_content = re.sub(pattern, emphasize_translation, modified_content)
            
            # Solo actualizar si hubo cambios
            if modified_content != content:
                element.content = modified_content
                element.attributes['data-has-translations'] = 'true'
                
                current_class = element.attributes.get('class', '')
                element.attributes['class'] = f"{current_class} has-translation-emphasis".strip()
    
    
    # ========================================
    # ⚙️ IMPLEMENTACIONES AVANZADAS
    # ========================================
    
    def _apply_advanced_toc_navigation(self, book_structure: BookStructure, options: ProfessionalFormattingOptions) -> None:
        """Implementa navegación TOC avanzada con enlaces dinámicos."""
        
        # Generar TOC navegable si no existe
        if not book_structure.toc or len(book_structure.toc) == 0:
            book_structure.toc = self._generate_enhanced_toc(book_structure)
        
        # Mejorar TOC existente con navegación
        enhanced_toc = []
        
        for i, toc_entry in enumerate(book_structure.toc):
            if isinstance(toc_entry, dict):
                title = toc_entry.get('title', f'Sección {i+1}')
                page = toc_entry.get('page', i+1)
                level = toc_entry.get('level', 1)
                anchor_id = toc_entry.get('id', f'section-{i}')
            else:
                title = str(toc_entry)
                page = i + 1
                level = 1
                anchor_id = f'section-{i}'
            
            # Crear entrada mejorada
            enhanced_entry = {
                'title': title,
                'page': page,
                'level': level,
                'id': anchor_id,
                'anchor_link': f'#{anchor_id}',
                'navigation_type': 'enhanced',
                'interactive': True,
                'clickable': True
            }
            
            enhanced_toc.append(enhanced_entry)
        
        book_structure.toc = enhanced_toc
        book_structure.metadata['enhanced_navigation'] = True
        book_structure.metadata['toc_type'] = 'interactive'
    
    def _generate_enhanced_toc(self, book_structure: BookStructure) -> List[Dict]:
        """Genera una TOC mejorada automáticamente."""
        toc_entries = []
        
        for i, element in enumerate(book_structure.elements):
            if not element:
                continue
                
            if element.type.value == 'chapter':
                title = self._extract_chapter_title(element)
                entry = {
                    'title': title,
                    'page': i + 1,
                    'level': 1,
                    'id': element.id or f'chapter-{i}',
                    'type': 'chapter'
                }
                toc_entries.append(entry)
            
            elif element.type.value == 'section':
                title = element.content[:50] + '...' if len(element.content) > 50 else element.content
                entry = {
                    'title': title,
                    'page': i + 1,
                    'level': 2,
                    'id': element.id or f'section-{i}',
                    'type': 'section'
                }
                toc_entries.append(entry)
        
        return toc_entries
    
    def _apply_real_index_generation(self, book_structure: BookStructure, options: ProfessionalFormattingOptions) -> None:
        """Implementa generación real de índice temático visible."""
        
        # El índice automático ya se generó, ahora crear página visible
        if not book_structure.index:
            return
            
        # Crear página de índice temático
        index_entries = []
        
        for term, references in book_structure.index.items():
            if term and len(term) > 2:  # Filtrar términos muy cortos
                index_entry = {
                    'term': term,
                    'references': references,
                    'page_count': len(references),
                    'alphabetical_order': term.lower()
                }
                index_entries.append(index_entry)
        
        # Ordenar alfabéticamente
        index_entries.sort(key=lambda x: x['alphabetical_order'])
        
        # Generar HTML del índice
        index_html = '<div class="thematic-index-page" data-page-type="index">\n'
        index_html += '<h2 class="index-title">Índice Temático</h2>\n'
        index_html += '<div class="index-content">\n'
        
        current_letter = ''
        for entry in index_entries:
            term = entry['term']
            first_letter = term[0].upper()
            
            # Separador alfabético
            if first_letter != current_letter:
                if current_letter:
                    index_html += '</div>\n'
                index_html += f'<div class="index-section" data-letter="{first_letter}">\n'
                index_html += f'<h3 class="index-letter">{first_letter}</h3>\n'
                current_letter = first_letter
            
            # Entrada del índice
            references_text = ', '.join([ref.replace('#', '') for ref in entry['references']])
            index_html += f'<div class="index-entry" data-term="{term}">\n'
            index_html += f'  <span class="index-term">{term}</span>\n'
            index_html += f'  <span class="index-references" data-references="{references_text}">{references_text}</span>\n'
            index_html += '</div>\n'
        
        if current_letter:
            index_html += '</div>\n'
        
        index_html += '</div>\n</div>'
        
        # Crear elemento de índice
        index_element = HTMLElement(
            id="thematic-index-page",
            type=HTMLElementType.PARAGRAPH,
            content=index_html,
            attributes={
                'class': 'thematic-index professional-index',
                'data-page-type': 'index',
                'data-index-entries': str(len(index_entries))
            },
            children=[],
            metadata={
                'content_type': 'thematic_index',
                'generation_method': 'automatic',
                'entry_count': len(index_entries),
                'alphabetically_sorted': True
            }
        )
        
        # Agregar al final del libro
        book_structure.elements.append(index_element)
    
    def _apply_bookmark_generation(self, book_structure: BookStructure, options: ProfessionalFormattingOptions) -> None:
        """Implementa generación de marcadores para navegación."""
        
        bookmarks = []
        
        for element in book_structure.elements:
            if not element:
                continue
                
            # Crear marcadores para capítulos y secciones importantes
            if element.type.value in ['chapter', 'section']:
                title = self._extract_chapter_title(element) if element.type.value == 'chapter' else element.content[:50]
                
                bookmark = {
                    'id': element.id or f'bookmark-{len(bookmarks)}',
                    'title': title,
                    'type': element.type.value,
                    'anchor': f'#{element.id}' if element.id else f'#bookmark-{len(bookmarks)}',
                    'level': 1 if element.type.value == 'chapter' else 2
                }
                
                bookmarks.append(bookmark)
                
                # Agregar atributos de marcador al elemento
                element.attributes['data-bookmark'] = 'true'
                element.attributes['data-bookmark-title'] = title
                element.attributes['data-bookmark-level'] = str(bookmark['level'])
        
        # Guardar marcadores en metadatos
        book_structure.metadata['bookmarks'] = bookmarks
        book_structure.metadata['bookmark_count'] = len(bookmarks)
        book_structure.metadata['bookmarks_enabled'] = True
    
    def _apply_search_functionality(self, book_structure: BookStructure, options: ProfessionalFormattingOptions) -> None:
        """Implementa funcionalidad de búsqueda en el contenido."""
        
        # Crear índice de búsqueda
        search_index = []
        word_index = {}
        
        for i, element in enumerate(book_structure.elements):
            if not element or not element.content:
                continue
                
            # Extraer texto limpio para indexación
            import re
            clean_text = re.sub(r'<[^>]+>', '', element.content)
            words = re.findall(r'\b\w{3,}\b', clean_text.lower())
            
            # Crear entrada de búsqueda
            search_entry = {
                'element_id': element.id or f'element-{i}',
                'element_type': element.type.value,
                'content_preview': clean_text[:200] + '...' if len(clean_text) > 200 else clean_text,
                'word_count': len(words),
                'searchable': True
            }
            
            search_index.append(search_entry)
            
            # Indexar palabras
            for word in set(words):  # usar set para evitar duplicados
                if word not in word_index:
                    word_index[word] = []
                word_index[word].append({
                    'element_id': search_entry['element_id'],
                    'element_type': element.type.value,
                    'preview': clean_text[:100]
                })
            
            # Agregar atributos de búsqueda
            element.attributes['data-searchable'] = 'true'
            element.attributes['data-word-count'] = str(len(words))
        
        # Guardar índices de búsqueda
        book_structure.metadata['search_index'] = search_index
        book_structure.metadata['word_index'] = word_index
        book_structure.metadata['searchable_elements'] = len(search_index)
        book_structure.metadata['indexed_words'] = len(word_index)
        book_structure.metadata['search_enabled'] = True
    
    def _apply_file_size_optimization(self, book_structure: BookStructure, options: ProfessionalFormattingOptions) -> None:
        """Implementa optimización de tamaño de archivo."""
        
        optimization_stats = {
            'original_elements': len(book_structure.elements),
            'optimized_elements': 0,
            'removed_redundancy': 0,
            'compressed_content': 0
        }
        
        for element in book_structure.elements:
            if not element:
                continue
                
            original_content = element.content
            if not original_content:
                continue
            
            # Optimizar contenido
            optimized_content = original_content
            
            # Remover espacios extra
            import re
            optimized_content = re.sub(r'\s+', ' ', optimized_content)
            optimized_content = re.sub(r'>\s+<', '><', optimized_content)
            
            # Remover comentarios HTML
            optimized_content = re.sub(r'<!--.*?-->', '', optimized_content, flags=re.DOTALL)
            
            # Minimizar atributos repetidos
            optimized_content = re.sub(r'\s*(data-[^=]+="[^"]*")\s*\1', r' \1', optimized_content)
            
            # Actualizar si hay mejora significativa (>5%)
            if len(optimized_content) < len(original_content) * 0.95:
                element.content = optimized_content.strip()
                optimization_stats['optimized_elements'] += 1
                optimization_stats['compressed_content'] += len(original_content) - len(optimized_content)
            
            # Agregar atributos de optimización
            element.attributes['data-optimized'] = 'true'
            element.attributes['data-compression-ratio'] = f"{len(optimized_content)/len(original_content):.2f}"
        
        # Guardar estadísticas
        book_structure.metadata['file_optimization'] = optimization_stats
        book_structure.metadata['optimization_enabled'] = True
        book_structure.metadata['estimated_size_reduction'] = f"{optimization_stats['compressed_content']} chars"
    
    def _apply_publisher_information(self, book_structure: BookStructure, options: ProfessionalFormattingOptions) -> None:
        """Implementa información editorial profesional."""
        
        publisher_info = {
            'publisher_name': 'Buko AI Publishing',
            'publication_year': '2024',
            'edition': 'Primera Edición',
            'isbn': options.include_isbn or 'Por asignar',
            'legal_deposit': 'Pendiente',
            'print_info': 'Impreso bajo demanda',
            'contact_info': 'contact@buko-ai.com',
            'website': 'https://buko-ai.com'
        }
        
        # Crear página de información editorial
        publisher_html = f'''
        <div class="publisher-information-page" data-page-type="publisher-info">
            <div class="publisher-content">
                <h3 class="publisher-title">Información Editorial</h3>
                
                <div class="publisher-details">
                    <p class="publisher-name"><strong>Editorial:</strong> {publisher_info['publisher_name']}</p>
                    <p class="publication-year"><strong>Año de Publicación:</strong> {publisher_info['publication_year']}</p>
                    <p class="edition-info"><strong>Edición:</strong> {publisher_info['edition']}</p>
                    
                    {f'<p class="isbn-info"><strong>ISBN:</strong> {publisher_info["isbn"]}</p>' if publisher_info['isbn'] != 'Por asignar' else ''}
                    
                    <p class="legal-info"><strong>Depósito Legal:</strong> {publisher_info['legal_deposit']}</p>
                    <p class="print-info"><strong>Impresión:</strong> {publisher_info['print_info']}</p>
                </div>
                
                <div class="contact-information">
                    <h4>Contacto Editorial</h4>
                    <p class="contact-email">Email: {publisher_info['contact_info']}</p>
                    <p class="contact-website">Web: {publisher_info['website']}</p>
                </div>
                
                <div class="legal-notice">
                    <p class="copyright-notice">
                        © {publisher_info['publication_year']} {publisher_info['publisher_name']}. 
                        Todos los derechos reservados. Esta publicación no puede ser reproducida, 
                        distribuida, o transmitida de ninguna forma sin el permiso previo del editor.
                    </p>
                </div>
            </div>
        </div>'''
        
        # Crear elemento de información editorial
        publisher_element = HTMLElement(
            id="publisher-information-page",
            type=HTMLElementType.PARAGRAPH,
            content=publisher_html,
            attributes={
                'class': 'publisher-information professional-publishing-info',
                'data-page-type': 'publisher-info'
            },
            children=[],
            metadata={
                'content_type': 'publisher_information',
                'generation_method': 'automatic',
                'publisher_data': publisher_info
            }
        )
        
        # Agregar cerca del principio del libro (después del copyright)
        insertion_index = 2  # Después de título y copyright
        if insertion_index < len(book_structure.elements):
            book_structure.elements.insert(insertion_index, publisher_element)
        else:
            book_structure.elements.append(publisher_element)
    
    
    # ========================================
    # 📐 IMPLEMENTACIONES ADICIONALES
    # ========================================
    
    def _apply_enhanced_paragraph_spacing(self, book_structure: BookStructure, options: ProfessionalFormattingOptions) -> None:
        """Implementa espaciado mejorado de párrafos con control preciso."""
        
        # Obtener configuración de espaciado
        paragraph_spacing = getattr(options, 'paragraph_spacing', 6.0)
        line_height_multiplier = max(1.2, getattr(options, 'line_spacing', 1.5))
        
        # Calcular espaciado óptimo
        base_spacing = paragraph_spacing
        enhanced_spacing = base_spacing * 1.2  # 20% más espacio para mejor legibilidad
        
        for element in book_structure.elements:
            if not element or element.type.value != 'paragraph':
                continue
                
            # Aplicar espaciado mejorado
            current_style = element.attributes.get('style', '')
            
            spacing_styles = [
                f'margin-bottom: {enhanced_spacing}pt',
                f'margin-top: {base_spacing * 0.5}pt',  # Menor espacio arriba
                f'line-height: {line_height_multiplier}',
                'text-align: justify',
                'text-justify: inter-word',
                'orphans: 2',
                'widows: 2'
            ]
            
            # Combinar estilos
            enhanced_style = '; '.join(spacing_styles)
            
            if current_style:
                element.attributes['style'] = f"{current_style}; {enhanced_style}"
            else:
                element.attributes['style'] = enhanced_style
            
            # Agregar atributos de espaciado
            element.attributes['data-enhanced-spacing'] = 'true'
            element.attributes['data-paragraph-spacing'] = str(enhanced_spacing)
            
            current_class = element.attributes.get('class', '')
            element.attributes['class'] = f"{current_class} enhanced-paragraph-spacing".strip()
    
    def _apply_complete_isbn_integration(self, book_structure: BookStructure, options: ProfessionalFormattingOptions) -> None:
        """Implementa integración completa del ISBN en múltiples ubicaciones."""
        
        isbn = options.include_isbn.strip()
        if not isbn:
            return
            
        # Validar formato básico del ISBN
        import re
        isbn_clean = re.sub(r'[^0-9X]', '', isbn.upper())
        
        if len(isbn_clean) not in [10, 13]:
            # ISBN inválido, usar como texto
            isbn_display = isbn
            isbn_valid = False
        else:
            # Formatear ISBN correctamente
            if len(isbn_clean) == 13:
                isbn_display = f"{isbn_clean[:3]}-{isbn_clean[3]}-{isbn_clean[4:6]}-{isbn_clean[6:12]}-{isbn_clean[12]}"
            else:
                isbn_display = f"{isbn_clean[:1]}-{isbn_clean[1:4]}-{isbn_clean[4:9]}-{isbn_clean[9]}"
            isbn_valid = True
        
        # 1. Agregar a página de copyright
        self._add_isbn_to_copyright_page(book_structure, isbn_display, isbn_valid)
        
        # 2. Agregar metadatos al libro
        book_structure.metadata['isbn'] = isbn_display
        book_structure.metadata['isbn_valid'] = isbn_valid
        book_structure.metadata['isbn_type'] = 'ISBN-13' if len(isbn_clean) == 13 else 'ISBN-10'
        
        # 3. Crear página de catalogación si es válido
        if isbn_valid:
            self._create_cataloging_page_with_isbn(book_structure, isbn_display, options)
    
    def _add_isbn_to_copyright_page(self, book_structure: BookStructure, isbn_display: str, isbn_valid: bool) -> None:
        """Agrega ISBN a la página de copyright existente."""
        
        for element in book_structure.elements:
            if not element:
                continue
                
            if (element.attributes.get('data-page-type') == 'copyright' or 
                'copyright' in element.attributes.get('class', '').lower()):
                
                # Encontrar contenido de copyright y agregar ISBN
                content = element.content
                
                isbn_section = f'''
                <div class="isbn-information" data-isbn="{isbn_display}">
                    <p class="isbn-line">
                        <strong>ISBN:</strong> <span class="isbn-number" data-valid="{isbn_valid}">{isbn_display}</span>
                    </p>
                </div>'''
                
                # Insertar antes del cierre del div principal
                if '</div>' in content:
                    content = content.replace('</div>', f'{isbn_section}\n</div>')
                else:
                    content += isbn_section
                
                element.content = content
                element.attributes['data-has-isbn'] = 'true'
                break
    
    def _create_cataloging_page_with_isbn(self, book_structure: BookStructure, isbn_display: str, options: ProfessionalFormattingOptions) -> None:
        """Crea página de catalogación profesional con ISBN."""
        
        book_title = book_structure.title or "Título del Libro"
        author_name = book_structure.author or options.author_name or "Autor"
        
        cataloging_html = f'''
        <div class="cataloging-page" data-page-type="cataloging">
            <div class="cataloging-content">
                <h3 class="cataloging-title">Datos de Catalogación</h3>
                
                <div class="bibliographic-data">
                    <p class="catalog-title"><strong>Título:</strong> {book_title}</p>
                    <p class="catalog-author"><strong>Autor:</strong> {author_name}</p>
                    <p class="catalog-isbn"><strong>ISBN:</strong> {isbn_display}</p>
                    <p class="catalog-publisher"><strong>Editorial:</strong> Buko AI Publishing</p>
                    <p class="catalog-year"><strong>Año:</strong> 2024</p>
                    <p class="catalog-format"><strong>Formato:</strong> Digital / Impreso bajo demanda</p>
                </div>
                
                <div class="classification-data">
                    <h4>Clasificación Temática</h4>
                    <p class="dewey-classification">Clasificación Dewey: Por asignar</p>
                    <p class="subject-headings">Materias: Educación, Aprendizaje, Literatura Digital</p>
                </div>
                
                <div class="technical-data">
                    <h4>Datos Técnicos</h4>
                    <p class="pages-estimate">Páginas estimadas: {len(book_structure.elements)} secciones</p>
                    <p class="language">Idioma: Español</p>
                    <p class="edition">Edición: Primera edición digital</p>
                </div>
            </div>
        </div>'''
        
        cataloging_element = HTMLElement(
            id="cataloging-page-with-isbn",
            type=HTMLElementType.PARAGRAPH,
            content=cataloging_html,
            attributes={
                'class': 'cataloging-page professional-cataloging',
                'data-page-type': 'cataloging',
                'data-isbn': isbn_display
            },
            children=[],
            metadata={
                'content_type': 'cataloging',
                'generation_method': 'automatic',
                'isbn': isbn_display,
                'bibliographic_complete': True
            }
        )
        
        # Insertar después de copyright
        insertion_index = self._find_copyright_page_index(book_structure) + 1
        if insertion_index < len(book_structure.elements):
            book_structure.elements.insert(insertion_index, cataloging_element)
        else:
            book_structure.elements.append(cataloging_element)
    
    def _find_copyright_page_index(self, book_structure: BookStructure) -> int:
        """Encuentra el índice de la página de copyright."""
        for i, element in enumerate(book_structure.elements):
            if (element and 
                (element.attributes.get('data-page-type') == 'copyright' or 
                 'copyright' in element.attributes.get('class', '').lower())):
                return i
        return 1  # Fallback