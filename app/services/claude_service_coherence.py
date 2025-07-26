"""
Sistema refinado para garantizar coherencia y cumplimiento de páginas por capítulo según arquitectura
"""
import json
import re
from typing import Dict, List, Any, Tuple
import structlog

logger = structlog.get_logger()

class BookCoherenceManager:
    """Gestiona la coherencia y distribución de páginas basado en la arquitectura aprobada"""
    
    def __init__(self):
        self.words_per_page = 350  # Estándar
        
    def extract_target_pages_from_architecture(self, approved_architecture: Dict[str, Any], book_params: Dict[str, Any]) -> int:
        """Extrae el target de páginas correcto desde la arquitectura"""
        
        # 1. Intentar desde arquitectura aprobada
        if isinstance(approved_architecture, dict):
            # Si tiene raw_content, parsear
            if 'raw_content' in approved_architecture:
                parsed_arch = self._parse_raw_architecture(approved_architecture['raw_content'])
                if parsed_arch and 'target_pages' in parsed_arch:
                    logger.info("target_pages_from_raw_content", pages=int(parsed_arch['target_pages']))
                    return int(parsed_arch['target_pages'])
            
            # Si ya es JSON estructurado (formato directo)
            if 'target_pages' in approved_architecture:
                logger.info("target_pages_from_direct_architecture", pages=int(approved_architecture['target_pages']))
                return int(approved_architecture['target_pages'])
        
        # 2. Fallback a book_params - USAR effective_pages configurado por el usuario
        fallback_pages = book_params.get('page_count', book_params.get('effective_pages', 200))
        logger.info("target_pages_fallback_to_user_configuration", 
                   pages=fallback_pages,
                   source="page_count" if 'page_count' in book_params else "effective_pages")
        return fallback_pages
    
    def _parse_raw_architecture(self, raw_content: str) -> Dict[str, Any]:
        """Parsea raw_content para extraer JSON de arquitectura"""
        try:
            # Buscar bloque JSON
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            json_match = re.search(json_pattern, raw_content, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)
            
            # Buscar JSON sin marcadores
            start = raw_content.find('{')
            end = raw_content.rfind('}') + 1
            if start != -1 and end > start:
                json_str = raw_content[start:end]
                return json.loads(json_str)
                
        except Exception as e:
            logger.error("error_parsing_architecture", error=str(e))
        
        return {}
    
    def validate_and_structure_chapters(self, approved_architecture: Dict[str, Any], target_pages: int) -> List[Dict[str, Any]]:
        """Valida y estructura capítulos con páginas target"""
        
        # Extraer capítulos de la arquitectura
        chapters = []
        parsed_arch = approved_architecture
        
        # Si tiene raw_content, parsear
        if 'raw_content' in approved_architecture:
            parsed_arch = self._parse_raw_architecture(approved_architecture['raw_content'])
            logger.info("parsed_architecture_from_raw_content", 
                       parsed_keys=list(parsed_arch.keys()) if parsed_arch else [])
        else:
            # La arquitectura ya está estructurada (formato directo)
            logger.info("using_direct_structured_architecture", 
                       architecture_keys=list(approved_architecture.keys()))
        
        # Buscar capítulos en la estructura
        if parsed_arch and 'structure' in parsed_arch:
            chapters = parsed_arch['structure'].get('chapters', [])
        elif 'structure' in approved_architecture:
            # Caso directo sin raw_content
            chapters = approved_architecture['structure'].get('chapters', [])
        
        if not chapters:
            logger.warning("no_chapters_in_architecture", 
                          architecture_keys=list(parsed_arch.keys() if parsed_arch else approved_architecture.keys()))
            # Crear estructura básica si no hay capítulos
            chapters = self._create_default_chapters(target_pages)
        else:
            logger.info("chapters_found_in_architecture", count=len(chapters))
        
        # Validar y ajustar páginas de capítulos
        structured_chapters = self._validate_chapter_pages(chapters, target_pages)
        
        return structured_chapters
    
    def _create_default_chapters(self, target_pages: int) -> List[Dict[str, Any]]:
        """Crea estructura de capítulos por defecto si la arquitectura está vacía"""
        num_chapters = max(10, target_pages // 20)  # ~20 páginas por capítulo
        pages_per_chapter = target_pages // num_chapters
        
        chapters = []
        for i in range(num_chapters):
            chapters.append({
                'number': i + 1,
                'title': f'Capítulo {i + 1}',
                'summary': f'Contenido del capítulo {i + 1}',
                'estimated_pages': pages_per_chapter,
                'key_points': ['Punto clave 1', 'Punto clave 2'],
                'learning_objectives': ['Objetivo de aprendizaje']
            })
        
        return chapters
    
    def _validate_chapter_pages(self, chapters: List[Dict[str, Any]], target_pages: int) -> List[Dict[str, Any]]:
        """Valida y ajusta las páginas de cada capítulo para cumplir el target"""
        
        if not chapters:
            return self._create_default_chapters(target_pages)
        
        # Calcular páginas totales actuales (support both 'pages' and 'estimated_pages')
        def get_chapter_pages(ch):
            return ch.get('estimated_pages', ch.get('pages', 0))
        
        total_current_pages = sum(get_chapter_pages(ch) for ch in chapters)
        
        # Si no hay páginas en ningún capítulo, distribúyelas igualmente
        if total_current_pages == 0:
            pages_per_chapter = target_pages // len(chapters)
            remaining_pages = target_pages % len(chapters)
            
            logger.info("initializing_chapter_pages", 
                       chapters_count=len(chapters),
                       pages_per_chapter=pages_per_chapter)
            
            for i, chapter in enumerate(chapters):
                chapter_pages = pages_per_chapter + (1 if i < remaining_pages else 0)
                chapter['estimated_pages'] = chapter_pages
            
            total_current_pages = target_pages
        
        # Si no coincide con target, ajustar proporcionalmente
        if total_current_pages != target_pages and total_current_pages > 0:
            adjustment_factor = target_pages / total_current_pages
            
            logger.info("adjusting_chapter_pages",
                       total_current=total_current_pages,
                       target_pages=target_pages,
                       factor=adjustment_factor)
            
            adjusted_total = 0
            for i, chapter in enumerate(chapters):
                original_pages = get_chapter_pages(chapter) or 10
                adjusted_pages = int(original_pages * adjustment_factor)
                
                # Asegurar mínimo 1 página por capítulo
                adjusted_pages = max(1, adjusted_pages)
                
                # Use consistent field name for output
                chapter['estimated_pages'] = adjusted_pages
                adjusted_total += adjusted_pages
            
            # Ajuste final para páginas exactas
            page_diff = target_pages - adjusted_total
            if page_diff != 0 and chapters:
                # Distribuir diferencia en los primeros capítulos
                for i in range(min(abs(page_diff), len(chapters))):
                    if page_diff > 0:
                        chapters[i]['estimated_pages'] += 1
                    elif chapters[i]['estimated_pages'] > 1:
                        chapters[i]['estimated_pages'] -= 1
        
        return chapters
    
    def calculate_chunk_page_distribution(self, structured_chapters: List[Dict[str, Any]], target_pages: int) -> List[Dict[str, Any]]:
        """Calcula distribución de páginas por chunk manteniendo coherencia"""
        
        max_chapters_per_chunk = 5  # Máximo para mantener coherencia
        chunks = []
        
        for i in range(0, len(structured_chapters), max_chapters_per_chunk):
            chunk_chapters = structured_chapters[i:i + max_chapters_per_chunk]
            chunk_pages = sum(ch.get('estimated_pages', 0) for ch in chunk_chapters)
            
            chunks.append({
                'index': len(chunks) + 1,
                'chapters': chunk_chapters,
                'target_pages': chunk_pages,
                'target_words': chunk_pages * self.words_per_page,
                'start_chapter': i + 1,
                'end_chapter': min(i + max_chapters_per_chunk, len(structured_chapters))
            })
        
        return chunks
    
    def validate_chunk_against_target(self, chunk_content: str, chunk_target_pages: int) -> Dict[str, Any]:
        """Valida si un chunk cumple con sus páginas target"""
        
        content_words = len(chunk_content.split())
        content_pages = content_words // self.words_per_page
        
        compliance_ratio = content_pages / chunk_target_pages if chunk_target_pages > 0 else 1
        
        return {
            'actual_words': content_words,
            'actual_pages': content_pages,
            'target_pages': chunk_target_pages,
            'compliance_ratio': compliance_ratio,
            'meets_target': compliance_ratio >= 0.9,  # 90% threshold
            'words_needed': max(0, (chunk_target_pages * self.words_per_page) - content_words)
        }
    
    def detect_content_duplicates(self, new_content: str, existing_content: List[str]) -> bool:
        """Detecta duplicados de contenido para evitar repeticiones"""
        
        if not existing_content:
            return False
        
        # Extraer frases significativas del nuevo contenido
        new_sentences = self._extract_significant_sentences(new_content)
        
        # Comparar con contenido existente
        for existing in existing_content:
            existing_sentences = self._extract_significant_sentences(existing)
            
            # Verificar overlap
            overlap = len(set(new_sentences) & set(existing_sentences))
            if overlap > len(new_sentences) * 0.3:  # 30% overlap threshold
                return True
        
        return False
    
    def _extract_significant_sentences(self, content: str) -> List[str]:
        """Extrae frases significativas para detección de duplicados"""
        
        # Dividir en oraciones
        sentences = re.split(r'[.!?]+', content)
        
        # Filtrar oraciones significativas (más de 20 caracteres)
        significant = []
        for sentence in sentences:
            clean_sentence = sentence.strip()
            if len(clean_sentence) > 20:
                # Normalizar (minúsculas, sin espacios extra)
                normalized = ' '.join(clean_sentence.lower().split())
                significant.append(normalized)
        
        return significant
    
    def generate_continuation_strategy(self, current_pages: int, target_pages: int, 
                                     completed_chapters: List[str]) -> Dict[str, Any]:
        """Genera estrategia de continuación inteligente"""
        
        pages_deficit = target_pages - current_pages
        
        if pages_deficit <= 0:
            return {'type': 'complete', 'strategy': 'Target achieved'}
        
        # Determinar estrategia basada en déficit
        if pages_deficit < 20:
            strategy_type = 'expand_existing'
            strategy = f'Expandir capítulos existentes con {pages_deficit} páginas adicionales'
        elif pages_deficit < 50:
            strategy_type = 'add_sections'
            strategy = f'Agregar secciones especiales (ejercicios, casos de estudio) - {pages_deficit} páginas'
        else:
            strategy_type = 'add_chapters'
            new_chapters = (pages_deficit // 15) + 1
            strategy = f'Agregar {new_chapters} capítulos adicionales - {pages_deficit} páginas'
        
        return {
            'type': strategy_type,
            'strategy': strategy,
            'pages_deficit': pages_deficit,
            'target_words': pages_deficit * self.words_per_page,
            'completed_chapters': completed_chapters
        }