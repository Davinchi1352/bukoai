"""
Servicio de post-procesamiento de libros para BukoAI
Maneja la limpieza y optimización del contenido final del libro
"""

import re
import structlog
from typing import Dict, List, Any, Tuple

logger = structlog.get_logger()

class BookPostProcessor:
    """
    Post-procesador de contenido de libros que:
    1. Elimina títulos técnicos (CHUNK, referencias internas)
    2. Renumera automáticamente h1, h2, h3 de forma consecutiva
    3. Limpia contenido duplicado del título del libro
    """
    
    def __init__(self):
        self.chapter_counter = 0
        self.section_counters = {}  # {chapter_num: section_counter}
        self.subsection_counters = {} # {chapter_num: {section_num: subsection_counter}}
    
    def process_book_content(self, content: str, book_title: str) -> str:
        """
        Procesa el contenido completo del libro aplicando todas las optimizaciones.
        
        Args:
            content: Contenido HTML del libro
            book_title: Título del libro para filtrar duplicados
            
        Returns:
            Contenido procesado y optimizado
        """
        logger.info("book_postprocessor_start", content_length=len(content))
        
        try:
            # 1. Limpiar títulos técnicos y referencias internas
            cleaned_content = self._remove_technical_titles(content)
            
            # 2. Eliminar repeticiones del títulos del libro
            cleaned_content = self._remove_duplicate_book_title(cleaned_content, book_title)
            
            # 3. Renumerar encabezados automáticamente
            renumbered_content = self._renumber_headings(cleaned_content)
            
            # 4. Optimizar formato HTML
            optimized_content = self._optimize_html_format(renumbered_content)
            
            logger.info("book_postprocessor_completed", 
                       original_length=len(content),
                       processed_length=len(optimized_content),
                       chapters_numbered=self.chapter_counter)
            
            return optimized_content
            
        except Exception as e:
            logger.error("book_postprocessor_error", error=str(e))
            return content  # Devolver contenido original si hay error
    
    def _remove_technical_titles(self, content: str) -> str:
        """Elimina títulos técnicos de organización interna."""
        
        # Patrones de títulos técnicos a eliminar
        technical_patterns = [
            r'<h[1-6][^>]*>\s*\*\*.*?CHUNK.*?\*\*\s*</h[1-6]>',
            r'<h[1-6][^>]*>\s*CHUNK.*?</h[1-6]>',
            r'<h[1-6][^>]*>\s*#.*?CHUNK.*?</h[1-6]>',
            r'<h[1-6][^>]*>\s*📋.*?CHUNK.*?</h[1-6]>',
            r'<h[1-6][^>]*>\s*\*\*.*?CONTENIDO PLANIFICADO.*?\*\*\s*</h[1-6]>',
            r'<h[1-6][^>]*>\s*CONTENIDO PLANIFICADO.*?</h[1-6]>',
            r'<h[1-6][^>]*>\s*\*\*.*?SECCIÓN.*?\*\*\s*</h[1-6]>',
            r'<h[1-6][^>]*>\s*\*\*.*?PARTE.*?\*\*\s*</h[1-6]>',
            r'<h[1-6][^>]*>\s*\*\*.*?PÁGINAS TARGET.*?\*\*\s*</h[1-6]>',
        ]
        
        cleaned = content
        for pattern in technical_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
        
        # Eliminar líneas vacías múltiples que quedan después del filtrado
        cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
        
        return cleaned
    
    def _remove_duplicate_book_title(self, content: str, book_title: str) -> str:
        """Elimina repeticiones del título principal del libro."""
        
        if not book_title:
            return content
        
        # Normalizar título para comparación
        normalized_title = re.sub(r'[^\w\s]', '', book_title.lower()).strip()
        
        # Patrones para encontrar títulos duplicados
        title_patterns = [
            rf'<h1[^>]*>\s*\*\*\s*{re.escape(book_title)}\s*\*\*\s*</h1>',
            rf'<h1[^>]*>\s*{re.escape(book_title)}\s*</h1>',
            rf'<h1[^>]*>\s*#\s*\*\*\s*{re.escape(book_title)}\s*\*\*\s*</h1>',
        ]
        
        cleaned = content
        for pattern in title_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        return cleaned
    
    def _renumber_headings(self, content: str) -> str:
        """Renumera automáticamente todos los encabezados de forma consecutiva."""
        
        # Reiniciar contadores
        self.chapter_counter = 0
        self.section_counters = {}
        self.subsection_counters = {}
        
        def replace_heading(match):
            heading_tag = match.group(1)  # h1, h2, h3
            attributes = match.group(2)   # atributos del tag
            content_text = match.group(3) # contenido del encabezado
            
            if heading_tag == 'h1':
                # Nuevo capítulo
                self.chapter_counter += 1
                self.section_counters[self.chapter_counter] = 0
                self.subsection_counters[self.chapter_counter] = {}
                
                # Limpiar TODA numeración existente (incluye números simples al inicio)
                clean_content = re.sub(r'^(Capítulo\s+\d+\s*[:.-]\s*|Chapter\s+\d+\s*[:.-]\s*)', '', content_text, flags=re.IGNORECASE).strip()
                # Eliminar cualquier numeración adicional
                clean_content = re.sub(r'^\d+(?:\.\d+)*\s+', '', clean_content).strip()
                clean_content = re.sub(r'^\d+\s+', '', clean_content).strip()
                
                return f'<h1{attributes}>Capítulo {self.chapter_counter}: {clean_content}</h1>'
                
            elif heading_tag == 'h2':
                # Nueva sección
                current_chapter = self.chapter_counter if self.chapter_counter > 0 else 1
                
                if current_chapter not in self.section_counters:
                    self.section_counters[current_chapter] = 0
                
                self.section_counters[current_chapter] += 1
                current_section = self.section_counters[current_chapter]
                
                # Reiniciar contador de subsecciones para esta sección
                if current_chapter not in self.subsection_counters:
                    self.subsection_counters[current_chapter] = {}
                self.subsection_counters[current_chapter][current_section] = 0
                
                # Limpiar TODA numeración existente de forma más agresiva
                # Primero eliminar cualquier numeración estructural (1.2.3, 1.2, etc)
                clean_content = re.sub(r'^\d+(?:\.\d+)*\s+', '', content_text).strip()
                # Luego eliminar cualquier número simple al inicio
                clean_content = re.sub(r'^\d+\s+', '', clean_content).strip()
                
                return f'<h2{attributes}>{current_chapter}.{current_section} {clean_content}</h2>'
                
            elif heading_tag == 'h3':
                # Nueva subsección
                current_chapter = self.chapter_counter if self.chapter_counter > 0 else 1
                current_section = self.section_counters.get(current_chapter, 1)
                
                if current_chapter not in self.subsection_counters:
                    self.subsection_counters[current_chapter] = {}
                if current_section not in self.subsection_counters[current_chapter]:
                    self.subsection_counters[current_chapter][current_section] = 0
                    
                self.subsection_counters[current_chapter][current_section] += 1
                current_subsection = self.subsection_counters[current_chapter][current_section]
                
                # Limpiar TODA numeración existente de forma más agresiva
                # Primero eliminar cualquier numeración estructural (1.2.3, 1.2, etc)
                clean_content = re.sub(r'^\d+(?:\.\d+)*\s+', '', content_text).strip()
                # Luego eliminar cualquier número simple al inicio
                clean_content = re.sub(r'^\d+\s+', '', clean_content).strip()
                
                return f'<h3{attributes}>{current_chapter}.{current_section}.{current_subsection} {clean_content}</h3>'
            
            # Si no es h1, h2, o h3, devolver tal como está
            return match.group(0)
        
        # Procesar todos los encabezados secuencialmente en una sola pasada
        content = re.sub(r'<(h[1-3])([^>]*)>(.*?)</h[1-3]>', replace_heading, content, flags=re.DOTALL)
        
        return content
    
    def _optimize_html_format(self, content: str) -> str:
        """Optimiza el formato HTML final."""
        
        # Eliminar espacios en blanco excesivos
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        # Asegurar espaciado consistente alrededor de encabezados
        content = re.sub(r'(<h[1-6][^>]*>)', r'\n\1', content)
        content = re.sub(r'(</h[1-6]>)', r'\1\n', content)
        
        # Limpiar espacios al inicio y final
        content = content.strip()
        
        return content
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del procesamiento."""
        return {
            'chapters_numbered': self.chapter_counter,
            'sections_per_chapter': dict(self.section_counters),
            'total_sections': sum(self.section_counters.values()),
            'subsections_per_chapter': dict(self.subsection_counters)
        }