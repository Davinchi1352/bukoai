"""
Sistema refinado para garantizar coherencia y cumplimiento de páginas por capítulo según arquitectura
"""
import json
import re
from typing import Dict, List, Any, Tuple
import structlog
from ..utils.page_calculations import get_words_per_page, calculate_target_words

logger = structlog.get_logger()

class BookCoherenceManager:
    """Gestiona la coherencia y distribución de páginas basado en la arquitectura aprobada"""
    
    def __init__(self, page_size: str = 'pocket', line_spacing: str = 'medium'):
        # Usar cálculo dinámico pero AGREGAR 20% más para forzar más contenido
        base_words_per_page = get_words_per_page(page_size, line_spacing)
        self.words_per_page = int(base_words_per_page * 1.2)  # 20% más para forzar contenido extra
        self.page_size = page_size
        self.line_spacing = line_spacing
        
        # Track chunk content for coherence
        self.chunk_contents = {}  # chunk_index -> content
        self.total_words_generated = 0
        
        logger.info("coherence_manager_initialized", 
                   base_words_per_page=base_words_per_page,
                   enhanced_words_per_page=self.words_per_page,
                   page_size=page_size, 
                   line_spacing=line_spacing)
        
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
        """Parsea raw_content para extraer JSON de arquitectura con manejo robusto de casos edge"""
        try:
            # Método 1: Buscar bloque JSON con markdown (```json...```)
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            json_match = re.search(json_pattern, raw_content, re.DOTALL | re.IGNORECASE)
            
            if json_match:
                json_str = json_match.group(1)
                parsed = self._sanitize_and_parse_json(json_str)
                if parsed:
                    return parsed
            
            # Método 2: Buscar bloques con ``` genéricos 
            generic_pattern = r'```\s*(\{.*?\})\s*```'
            generic_match = re.search(generic_pattern, raw_content, re.DOTALL)
            
            if generic_match:
                json_str = generic_match.group(1)
                parsed = self._sanitize_and_parse_json(json_str)
                if parsed:
                    return parsed
            
            # Método 3: Buscar JSON por detección de llaves con balance
            json_content = self._extract_balanced_json(raw_content)
            if json_content:
                parsed = self._sanitize_and_parse_json(json_content)
                if parsed:
                    return parsed
            
            # Método 4: Búsqueda agresiva por primera y última llave
            start = raw_content.find('{')
            end = raw_content.rfind('}') + 1
            if start != -1 and end > start:
                json_str = raw_content[start:end]
                parsed = self._sanitize_and_parse_json(json_str)
                if parsed:
                    return parsed
                
        except Exception as e:
            logger.error("error_parsing_architecture", 
                        error=str(e), 
                        raw_content_preview=raw_content[:200],
                        content_length=len(raw_content))
        
        return {}
    
    def _sanitize_and_parse_json(self, json_str: str) -> Dict[str, Any]:
        """Sanitiza y parsea JSON con múltiples estrategias de limpieza"""
        if not json_str or not json_str.strip():
            return {}
        
        # Lista de estrategias de sanitización
        sanitization_strategies = [
            # Estrategia 1: Sin modificaciones
            lambda s: s,
            
            # Estrategia 2: Limpiar escapes básicos
            lambda s: s.replace('\\"', '"').replace('\\n', '').replace('\\t', ''),
            
            # Estrategia 3: Limpiar escapes y caracteres de control
            lambda s: s.replace('\\"', '"').replace('\\n', '').replace('\\t', '').replace('\\r', ''),
            
            # Estrategia 4: Remover comentarios de estilo JS
            lambda s: re.sub(r'//.*?\n', '\n', s),
            
            # Estrategia 5: Normalizar comillas
            lambda s: s.replace("'", '"'),
            
            # Estrategia 6: Limpieza agresiva (último recurso)
            lambda s: re.sub(r'[^\x20-\x7E\n\r\t]', '', s).replace('\\"', '"')
        ]
        
        for i, strategy in enumerate(sanitization_strategies):
            try:
                sanitized = strategy(json_str.strip())
                return json.loads(sanitized)
            except json.JSONDecodeError as e:
                logger.debug(f"json_sanitization_strategy_{i+1}_failed", 
                           error=str(e), 
                           strategy_index=i+1)
                continue
            except Exception as e:
                logger.debug(f"json_sanitization_strategy_{i+1}_error", 
                           error=str(e), 
                           strategy_index=i+1)
                continue
        
        return {}
    
    def _extract_balanced_json(self, content: str) -> str:
        """Extrae JSON balanceado por conteo de llaves"""
        lines = content.split('\n')
        json_lines = []
        inside_json = False
        brace_count = 0
        bracket_count = 0
        
        for line in lines:
            stripped_line = line.strip()
            
            # Detectar inicio de JSON
            if not inside_json and '{' in stripped_line:
                inside_json = True
                brace_count = 0
                bracket_count = 0
                # Buscar desde la primera llave
                start_idx = stripped_line.find('{')
                line = line[line.find('{'):]
                stripped_line = line.strip()
            
            if inside_json:
                json_lines.append(line)
                
                # Contar llaves y corchetes
                brace_count += stripped_line.count('{') - stripped_line.count('}')
                bracket_count += stripped_line.count('[') - stripped_line.count(']')
                
                # Si todo está balanceado y termina con llave, hemos terminado
                if brace_count <= 0 and bracket_count <= 0 and stripped_line.endswith('}'):
                    break
                    
                # Protección contra loops infinitos
                if len(json_lines) > 1000:  # Máximo 1000 líneas
                    break
        
        return '\n'.join(json_lines) if json_lines else ""
    
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
        
        # Buscar capítulos en la estructura - MEJORADO para múltiples formatos
        if parsed_arch and 'structure' in parsed_arch:
            chapters = parsed_arch['structure'].get('chapters', [])
        elif parsed_arch and 'chapters' in parsed_arch:
            # Capítulos directamente en la arquitectura parseada
            chapters = parsed_arch['chapters']
        elif 'structure' in approved_architecture:
            # Caso directo sin raw_content
            chapters = approved_architecture['structure'].get('chapters', [])
        elif 'chapters' in approved_architecture:
            # Capítulos directamente en la arquitectura aprobada
            chapters = approved_architecture['chapters']
        
        if not chapters:
            logger.warning("no_chapters_in_architecture", 
                          architecture_keys=list(parsed_arch.keys() if parsed_arch else approved_architecture.keys()),
                          parsed_arch_keys=list(parsed_arch.keys()) if parsed_arch else [],
                          direct_arch_keys=list(approved_architecture.keys()))
            # Crear estructura básica si no hay capítulos
            chapters = self._create_default_chapters(target_pages)
        else:
            # Log detallado de los capítulos encontrados
            chapter_titles = [ch.get('title', ch.get('name', f"Cap {i+1}")) for i, ch in enumerate(chapters)]
            logger.info("chapters_found_in_architecture", 
                       count=len(chapters),
                       chapter_titles=chapter_titles[:5],  # Primeros 5 títulos
                       chapter_keys=list(chapters[0].keys()) if chapters else [])
        
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
        
        max_chapters_per_chunk = 2   # 🚀 OPTIMIZADO: Control preciso de páginas (2-3 capítulos por chunk para 5 chunks)
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
    
    def plan_pages_distribution(self, target_pages: int, num_chunks: int, total_chapters: int, 
                              approved_architecture: Dict[str, Any] = None, book_params: Dict[str, Any] = None) -> List[int]:
        """
        Planifica la distribución de páginas por chunk basado en CAPÍTULOS COMPLETOS.
        Garantiza que cada chunk contenga capítulos completos para evitar contenidos cortados.
        
        Args:
            target_pages: Número total de páginas objetivo
            num_chunks: Número de chunks a generar
            total_chapters: Número total de capítulos
            approved_architecture: Arquitectura aprobada para extraer capítulos
            book_params: Parámetros del libro
            
        Returns:
            Lista con páginas por chunk basada en capítulos completos: [pages_chunk1, pages_chunk2, ...]
        """
        if num_chunks <= 0:
            logger.warning("invalid_num_chunks", num_chunks=num_chunks)
            return [target_pages]
        
        # Si tenemos arquitectura, usar capítulos reales para distribución inteligente
        if approved_architecture and book_params:
            try:
                # Extraer y estructurar capítulos de la arquitectura
                structured_chapters = self.validate_and_structure_chapters(approved_architecture, target_pages)
                
                if structured_chapters:
                    # Usar lógica existente de distribución por capítulos completos
                    chunk_distribution = self.calculate_chunk_page_distribution(structured_chapters, target_pages)
                    
                    # Extraer solo las páginas por chunk
                    pages_per_chunk = [chunk['target_pages'] for chunk in chunk_distribution]
                    
                    logger.info("chapter_based_distribution", 
                               total_chapters=len(structured_chapters),
                               chunks_created=len(pages_per_chunk),
                               pages_distribution=pages_per_chunk,
                               chapters_per_chunk=[len(chunk['chapters']) for chunk in chunk_distribution])
                    
                    return pages_per_chunk
                    
            except Exception as e:
                logger.warning("fallback_to_simple_distribution", error=str(e))
        
        # Fallback: distribución simple por capítulos estimados
        if total_chapters > 0:
            # Calcular capítulos por chunk
            chapters_per_chunk = max(1, total_chapters // num_chunks)
            pages_per_chapter = target_pages // total_chapters if total_chapters > 0 else target_pages // num_chunks
            
            pages_distribution = []
            remaining_chapters = total_chapters
            remaining_pages = target_pages
            
            for i in range(num_chunks):
                if i == num_chunks - 1:  # Último chunk toma todo lo restante
                    chunk_chapters = remaining_chapters
                    chunk_pages = remaining_pages
                else:
                    chunk_chapters = min(chapters_per_chunk, remaining_chapters)
                    chunk_pages = chunk_chapters * pages_per_chapter
                
                pages_distribution.append(max(1, chunk_pages))
                remaining_chapters -= chunk_chapters
                remaining_pages -= chunk_pages
                
                if remaining_chapters <= 0:
                    break
            
            logger.info("fallback_chapter_distribution", 
                       total_chapters=total_chapters,
                       chapters_per_chunk=chapters_per_chunk,
                       pages_per_chapter=pages_per_chapter,
                       distribution=pages_distribution)
            
            return pages_distribution
        
        # Fallback final: distribución simple por páginas
        base_pages_per_chunk = target_pages // num_chunks
        remaining_pages = target_pages % num_chunks
        
        pages_distribution = []
        for i in range(num_chunks):
            chunk_pages = base_pages_per_chunk + (1 if i < remaining_pages else 0)
            pages_distribution.append(max(1, chunk_pages))
        
        logger.warning("simple_pages_distribution_fallback", 
                      target_pages=target_pages,
                      num_chunks=num_chunks,
                      distribution=pages_distribution)
        
        return pages_distribution
    
    def build_coherence_context(self, approved_architecture: Dict[str, Any], book_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construye contexto de coherencia detallado para el content generator.
        Incluye mapeo de capítulos por chunk y directrices para evitar duplicidades.
        
        Args:
            approved_architecture: Arquitectura aprobada del libro
            book_params: Parámetros del libro (título, descripción, etc.)
            
        Returns:
            Diccionario con contexto de coherencia detallado
        """
        # Extraer target_pages usando método existente
        target_pages = self.extract_target_pages_from_architecture(approved_architecture, book_params)
        
        # Extraer y estructurar capítulos completos de la arquitectura
        structured_chapters = self.validate_and_structure_chapters(approved_architecture, target_pages)
        
        # Crear distribución de chunks basada en capítulos completos
        chunk_distribution = []
        if structured_chapters:
            chunk_distribution = self.calculate_chunk_page_distribution(structured_chapters, target_pages)
        
        # Extraer información adicional de la arquitectura
        book_title = book_params.get('title', 'Libro sin título')
        book_description = book_params.get('description', '')
        key_topics = book_params.get('key_topics', '')
        book_genre = book_params.get('genre', 'general')
        target_audience = book_params.get('target_audience', 'general')
        
        # Extraer temas y estructura global de la arquitectura
        parsed_arch = approved_architecture
        if 'raw_content' in approved_architecture:
            parsed_arch = self._parse_raw_architecture(approved_architecture['raw_content'])
        
        global_themes = []
        if isinstance(parsed_arch, dict):
            global_themes = parsed_arch.get('themes', parsed_arch.get('main_themes', []))
        
        # Construir contexto de coherencia detallado
        coherence_context = {
            'book_metadata': {
                'title': book_title,
                'description': book_description,
                'genre': book_genre,
                'target_audience': target_audience,
                'key_topics': key_topics,
                'global_themes': global_themes
            },
            'structure_info': {
                'target_pages': target_pages,
                'total_chapters': len(structured_chapters),
                'total_chunks': len(chunk_distribution),
                'words_per_page': self.words_per_page,
                'page_size': self.page_size,
                'line_spacing': self.line_spacing
            },
            'chapters_mapping': [
                {
                    'number': ch.get('number', i + 1),
                    'title': ch.get('title', f'Capítulo {i + 1}'),
                    'summary': ch.get('summary', ''),
                    'key_points': ch.get('key_points', []),
                    'learning_objectives': ch.get('learning_objectives', []),
                    'estimated_pages': ch.get('estimated_pages', 0),
                    'target_words': ch.get('estimated_pages', 0) * self.words_per_page
                }
                for i, ch in enumerate(structured_chapters)
            ],
            'chunk_distribution': [
                {
                    'chunk_index': chunk['index'],
                    'chapters_included': [
                        {
                            'number': ch.get('number', i + 1),
                            'title': ch.get('title', f'Capítulo {i + 1}'),
                            'summary': ch.get('summary', ''),
                            'key_points': ch.get('key_points', [])
                        }
                        for i, ch in enumerate(chunk['chapters'])
                    ],
                    'target_pages': chunk['target_pages'],
                    'target_words': chunk['target_words'],
                    'start_chapter': chunk['start_chapter'],
                    'end_chapter': chunk['end_chapter']
                }
                for chunk in chunk_distribution
            ],
            'coherence_guidelines': {
                'maintain_consistency': True,
                'follow_architecture_strictly': True,
                'avoid_content_duplication': True,
                'respect_chapter_boundaries': True,
                'maintain_narrative_flow': True,
                'use_consistent_terminology': True,
                'reference_previous_chapters_appropriately': True
            },
            'anti_duplication_rules': {
                'track_covered_topics': True,
                'avoid_repeating_examples': True,
                'build_on_previous_content': True,
                'maintain_chapter_uniqueness': True,
                'check_against_existing_chunks': True
            },
            'quality_targets': {
                'target_word_count_total': target_pages * self.words_per_page,
                'minimum_words_per_chapter': (target_pages * self.words_per_page) // max(len(structured_chapters), 1),
                'consistency_score_target': 0.85,
                'architecture_adherence_target': 0.90
            }
        }
        
        logger.info("detailed_coherence_context_built",
                   target_pages=target_pages,
                   total_chapters=len(structured_chapters),
                   total_chunks=len(chunk_distribution),
                   book_title=book_title,
                   context_size=len(str(coherence_context)))
        
        return coherence_context
    
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
    
    def update_with_chunk_content(self, chunk_index: int, chunk_content: str) -> None:
        """
        Actualiza el manager con contenido de chunk generado para tracking de coherencia.
        
        Args:
            chunk_index: Índice del chunk (0-based)
            chunk_content: Contenido generado para el chunk
        """
        if not isinstance(chunk_content, str):
            chunk_content = str(chunk_content)
        
        # Store chunk content
        self.chunk_contents[chunk_index] = chunk_content
        
        # Update total word count
        chunk_words = len(chunk_content.split())
        self.total_words_generated += chunk_words
        
        # Calculate pages generated so far
        total_pages_generated = self.total_words_generated // self.words_per_page
        
        logger.info("chunk_content_updated",
                   chunk_index=chunk_index,
                   chunk_words=chunk_words,
                   chunk_pages=chunk_words // self.words_per_page,
                   total_words_generated=self.total_words_generated,
                   total_pages_generated=total_pages_generated,
                   chunks_completed=len(self.chunk_contents))
    
    def get_generation_progress(self) -> Dict[str, Any]:
        """
        Obtiene el progreso actual de generación.
        
        Returns:
            Dict con estadísticas de progreso de generación
        """
        return {
            'chunks_completed': len(self.chunk_contents),
            'total_words_generated': self.total_words_generated,
            'total_pages_generated': self.total_words_generated // self.words_per_page,
            'average_words_per_chunk': self.total_words_generated // len(self.chunk_contents) if self.chunk_contents else 0,
            'average_pages_per_chunk': (self.total_words_generated // self.words_per_page) // len(self.chunk_contents) if self.chunk_contents else 0
        }