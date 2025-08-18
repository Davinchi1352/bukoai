"""
Sistema de Configuración Dinámico Escalable para Buko AI

Este módulo reemplaza los 50+ valores hardcodeados con un sistema dinámico
que adapta la configuración del sistema basado en las preferencias del usuario
capturadas en el formulario de generación http://localhost:5001/books/generate.

Diseñado para escalar a miles de usuarios con diferentes configuraciones.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple
import math
from ....utils.page_calculations import get_words_per_page, calculate_target_words

@dataclass
class UserConfiguration:
    """
    Captura la configuración del usuario desde el formulario de generación.
    
    Mapea directamente a los campos del formulario en generate.html líneas 554-566.
    """
    # Información básica
    title: str
    genre: str
    language: str
    
    # Configuración de contenido
    description: str
    audience: str  # children, young_adult, adult, all
    tone: str
    
    # Configuración avanzada
    chapters: int = 10  # 1-50 según form línea 207-212
    length: str = 'medium'  # short, medium, long según líneas 217-257
    page_size: str = 'pocket'  # pocket, A5, B5, letter según líneas 260-323
    line_spacing: str = 'medium'  # single, medium, double según líneas 326-367
    additional_instructions: str = ''

    def __post_init__(self):
        """Validación de configuración del usuario."""
        if not 1 <= self.chapters <= 50:
            raise ValueError(f"Chapters must be 1-50, got {self.chapters}")
        
        if self.length not in ['short', 'medium', 'long']:
            raise ValueError(f"Invalid length: {self.length}")
        
        if self.page_size not in ['pocket', 'A5', 'B5', 'letter']:
            raise ValueError(f"Invalid page_size: {self.page_size}")
        
        if self.line_spacing not in ['single', 'medium', 'double']:
            raise ValueError(f"Invalid line_spacing: {self.line_spacing}")


@dataclass
class DynamicSystemConfiguration:
    """
    Configuración del sistema adaptada dinámicamente según preferencias del usuario.
    
    Reemplaza todos los hardcodes en claude_config.py con valores calculados
    basados en la complejidad y tamaño del libro del usuario.
    """
    
    # =====================================
    # CONFIGURACIÓN DE PÁGINAS Y PALABRAS
    # =====================================
    target_pages: int
    words_per_page: int
    total_target_words: int
    
    # =====================================
    # CONFIGURACIÓN DE TOKENS DINÁMICOS
    # =====================================
    max_tokens: int
    thinking_budget: int
    token_limits: Dict[str, int]
    
    # =====================================
    # CONFIGURACIÓN DE TIMEOUTS DINÁMICOS
    # =====================================
    architecture_timeout: int  # Basado en complejidad
    chunk_timeout: int         # Basado en páginas por chunk
    thinking_timeout: int      # Basado en complejidad del contenido
    
    # =====================================
    # CONFIGURACIÓN DE CHUNKS DINÁMICOS
    # =====================================
    max_chunks: int            # Basado en número de capítulos
    chunk_overlap: int         # Basado en complejidad narrativa
    pages_per_chunk: int       # Calculado dinámicamente
    
    # =====================================
    # CONFIGURACIÓN DE PROGRESO DINÁMICO
    # =====================================
    progress_intervals: Dict[str, int]  # Intervalos adaptados al tamaño
    
    # =====================================
    # CONFIGURACIÓN DE CALIDAD DINÁMICO
    # =====================================
    min_content_length_per_chapter: int  # Basado en páginas objetivo
    quality_thresholds: Dict[str, float]  # Umbrales adaptados


class DynamicConfigurationBuilder:
    """
    Constructor de configuración dinámico que elimina todos los hardcodes.
    
    Toma UserConfiguration y produce DynamicSystemConfiguration optimizada
    para el libro específico del usuario.
    """
    
    # =====================================
    # MAPEOS DE LONGITUD A PÁGINAS
    # =====================================
    LENGTH_TO_PAGES = {
        'short': (50, 100),   # Según generate.html línea 227
        'medium': (100, 200), # Según generate.html línea 238  
        'long': (200, 300)    # Según generate.html línea 249
    }
    
    # =====================================
    # FACTORES DE COMPLEJIDAD POR GÉNERO
    # =====================================
    GENRE_COMPLEXITY_FACTORS = {
        'ficcion': 1.0,      # Base
        'no_ficcion': 1.2,   # Más investigación
        'academico': 1.4,    # Más rigor
        'tecnico': 1.3,      # Más precisión
        'biografia': 1.1,    # Más investigación leve
        'infantil': 0.8,     # Menos complejidad
        'poetry': 0.9,       # Menos contenido por página
    }
    
    # =====================================
    # FACTORES DE COMPLEJIDAD POR AUDIENCIA
    # =====================================
    AUDIENCE_COMPLEXITY_FACTORS = {
        'children': 0.7,     # Contenido más simple
        'young_adult': 0.9,  # Complejidad media
        'adult': 1.0,        # Complejidad base
        'all': 0.8           # Accesible para todos
    }
    
    @classmethod
    def build_dynamic_configuration(cls, user_config: UserConfiguration) -> DynamicSystemConfiguration:
        """
        Construye configuración dinámica eliminando todos los hardcodes.
        
        Args:
            user_config: Configuración del usuario desde el formulario
            
        Returns:
            DynamicSystemConfiguration optimizada para el libro específico
        """
        builder = cls()
        return builder._build_configuration(user_config)
    
    def _build_configuration(self, user_config: UserConfiguration) -> DynamicSystemConfiguration:
        """Construye configuración dinámica completa."""
        
        # 1. Calcular páginas y palabras target
        target_pages = self._calculate_target_pages(user_config)
        words_per_page = get_words_per_page(user_config.page_size, user_config.line_spacing)
        total_target_words = calculate_target_words(target_pages, user_config.page_size, user_config.line_spacing)
        
        # 2. Calcular factores de complejidad
        complexity_factor = self._calculate_complexity_factor(user_config)
        
        # 3. Construir configuración de tokens dinámicos
        token_config = self._build_dynamic_token_configuration(
            target_pages, total_target_words, complexity_factor, user_config
        )
        
        # 4. Construir configuración de timeouts dinámicos
        timeout_config = self._build_dynamic_timeout_configuration(
            target_pages, user_config.chapters, complexity_factor
        )
        
        # 5. Construir configuración de chunks dinámicos
        chunk_config = self._build_dynamic_chunk_configuration(
            target_pages, user_config.chapters, complexity_factor
        )
        
        # 6. Construir configuración de progreso dinámico
        progress_config = self._build_dynamic_progress_configuration(
            target_pages, user_config.chapters
        )
        
        # 7. Construir configuración de calidad dinámico
        quality_config = self._build_dynamic_quality_configuration(
            target_pages, user_config.chapters, complexity_factor
        )
        
        return DynamicSystemConfiguration(
            # Páginas y palabras
            target_pages=target_pages,
            words_per_page=words_per_page,
            total_target_words=total_target_words,
            
            # Tokens dinámicos
            max_tokens=token_config['max_tokens'],
            thinking_budget=token_config['thinking_budget'],
            token_limits=token_config['token_limits'],
            
            # Timeouts dinámicos
            architecture_timeout=timeout_config['architecture_timeout'],
            chunk_timeout=timeout_config['chunk_timeout'],
            thinking_timeout=timeout_config['thinking_timeout'],
            
            # Chunks dinámicos
            max_chunks=chunk_config['max_chunks'],
            chunk_overlap=chunk_config['chunk_overlap'],
            pages_per_chunk=chunk_config['pages_per_chunk'],
            
            # Progreso dinámico
            progress_intervals=progress_config,
            
            # Calidad dinámico
            min_content_length_per_chapter=quality_config['min_content_length_per_chapter'],
            quality_thresholds=quality_config['quality_thresholds']
        )
    
    def _calculate_target_pages(self, user_config: UserConfiguration) -> int:
        """
        Calcula páginas target basado en la longitud seleccionada por el usuario.
        
        Reemplaza el hardcode de default_target_pages: 150 en claude_config.py línea 73.
        """
        min_pages, max_pages = self.LENGTH_TO_PAGES[user_config.length]
        
        # Usar punto medio del rango como target
        # Esto permite flexibilidad pero da al usuario lo que espera
        target_pages = (min_pages + max_pages) // 2
        
        # Ajustar ligeramente basado en número de capítulos
        # Más capítulos = ligeramente más páginas para mejor desarrollo
        chapter_factor = 1.0 + (user_config.chapters - 10) * 0.02  # ±2% por capítulo
        target_pages = int(target_pages * chapter_factor)
        
        # Mantener dentro del rango
        return max(min_pages, min(max_pages, target_pages))
    
    def _calculate_complexity_factor(self, user_config: UserConfiguration) -> float:
        """
        Calcula factor de complejidad basado en género y audiencia.
        
        Reemplaza hardcodes dispersos con cálculo dinámico.
        """
        genre_factor = self.GENRE_COMPLEXITY_FACTORS.get(user_config.genre, 1.0)
        audience_factor = self.AUDIENCE_COMPLEXITY_FACTORS.get(user_config.audience, 1.0)
        
        # Factor combinado (promedio ponderado)
        return (genre_factor * 0.6) + (audience_factor * 0.4)
    
    def _build_dynamic_token_configuration(self, target_pages: int, total_words: int, 
                                         complexity_factor: float, user_config: UserConfiguration) -> Dict[str, Any]:
        """
        Construye configuración de tokens dinámicos.
        
        Reemplaza hardcodes en claude_config.py líneas 34-38, 100-107.
        """
        # Token base escalado por páginas y complejidad
        base_tokens_per_page = 120  # Tokens por página promedio
        scaled_max_tokens = int(target_pages * base_tokens_per_page * complexity_factor)
        
        # Límites prácticos
        max_tokens = max(20000, min(50000, scaled_max_tokens))
        
        # Thinking budget proporcional
        thinking_budget = int(max_tokens * 1.6 * complexity_factor)  # 160% del max_tokens
        thinking_budget = max(30000, min(80000, thinking_budget))
        
        # Token limits dinámicos por tipo de contenido
        architecture_tokens = int(max_tokens * 0.4)  # 40% para arquitectura
        chunk_main_tokens = int(max_tokens * 1.4)    # 140% para chunks principales
        introduction_tokens = int(max_tokens * 0.25) # 25% para introducciones
        conclusion_tokens = int(max_tokens * 0.25)   # 25% para conclusiones
        continuation_tokens = int(max_tokens * 0.7)  # 70% para continuaciones
        expansion_tokens = int(max_tokens * 0.35)    # 35% para expansiones
        
        return {
            'max_tokens': max_tokens,
            'thinking_budget': thinking_budget,
            'token_limits': {
                'architecture': architecture_tokens,
                'chunk_main': chunk_main_tokens,
                'introduction': introduction_tokens,
                'conclusion': conclusion_tokens,
                'continuation': continuation_tokens,
                'expansion': expansion_tokens
            }
        }
    
    def _build_dynamic_timeout_configuration(self, target_pages: int, chapters: int, 
                                           complexity_factor: float) -> Dict[str, int]:
        """
        Construye configuración de timeouts dinámicos.
        
        Reemplaza hardcodes en claude_config.py líneas 44-47.
        """
        # Timeout base por página y complejidad
        base_seconds_per_page = 8  # 8 segundos por página base
        
        architecture_timeout = int(1200 + (chapters * 60 * complexity_factor))  # Base 20min + tiempo por capítulo
        chunk_timeout = int(1800 + (target_pages * base_seconds_per_page * complexity_factor))  # Base 30min + tiempo por página
        thinking_timeout = int(600 + (target_pages * 4 * complexity_factor))  # Base 10min + tiempo de pensamiento
        
        # Límites prácticos
        architecture_timeout = max(1200, min(3600, architecture_timeout))  # 20min - 60min
        chunk_timeout = max(1800, min(7200, chunk_timeout))                # 30min - 120min
        thinking_timeout = max(600, min(2400, thinking_timeout))           # 10min - 40min
        
        return {
            'architecture_timeout': architecture_timeout,
            'chunk_timeout': chunk_timeout,
            'thinking_timeout': thinking_timeout
        }
    
    def _build_dynamic_chunk_configuration(self, target_pages: int, chapters: int, 
                                         complexity_factor: float) -> Dict[str, Any]:
        """
        Construye configuración de chunks dinámicos.
        
        Reemplaza hardcodes en claude_config.py líneas 58-59.
        """
        # Calcular chunks óptimos basado en capítulos
        # Objetivo: 2-3 capítulos por chunk para coherencia óptima
        optimal_chapters_per_chunk = 2.5
        max_chunks = max(3, min(10, math.ceil(chapters / optimal_chapters_per_chunk)))
        
        # Páginas por chunk
        pages_per_chunk = target_pages // max_chunks
        
        # Overlap dinámico basado en complejidad narrativa
        base_overlap = 300  # Palabras base
        complexity_overlap = int(base_overlap * complexity_factor)
        chunk_overlap = max(200, min(800, complexity_overlap))
        
        return {
            'max_chunks': max_chunks,
            'chunk_overlap': chunk_overlap,
            'pages_per_chunk': pages_per_chunk
        }
    
    def _build_dynamic_progress_configuration(self, target_pages: int, chapters: int) -> Dict[str, int]:
        """
        Construye configuración de progreso dinámicos.
        
        Reemplaza hardcodes en claude_config.py líneas 71-85.
        """
        # Intervalos de progreso basados en tamaño del libro
        base_interval = 10
        adjusted_interval = max(5, min(20, base_interval * (target_pages // 100)))
        
        return {
            'progress_check_interval': adjusted_interval,
            'progress_update_frequency': 50,  # Mantener fijo para UX consistente
            'progress_start': 15,             # Mantener fijo para UX consistente
            'progress_divider': 10,           # Mantener fijo para UX consistente
            'progress_max': 85,               # Mantener fijo para UX consistente
            'progress_connecting': 5,         # Mantener fijo para UX consistente
            'progress_thinking': 15,          # Mantener fijo para UX consistente
            'progress_processing': 90,        # Mantener fijo para UX consistente
            'progress_completed': 100         # Mantener fijo para UX consistente
        }
    
    def _build_dynamic_quality_configuration(self, target_pages: int, chapters: int, 
                                           complexity_factor: float) -> Dict[str, Any]:
        """
        Construye configuración de calidad dinámicos.
        
        Reemplaza hardcodes en claude_config.py líneas 91-94.
        """
        # Contenido mínimo por capítulo basado en páginas objetivo
        pages_per_chapter = target_pages / chapters
        words_per_chapter = pages_per_chapter * 300  # Promedio de palabras por página
        min_content_length_per_chapter = int(words_per_chapter * 0.8)  # 80% del objetivo
        
        # Umbrales de calidad adaptados a la complejidad
        base_coherence_threshold = 0.85
        base_architecture_adherence = 0.90
        
        quality_thresholds = {
            'coherence_score_target': base_coherence_threshold * complexity_factor,
            'architecture_adherence_target': base_architecture_adherence,
            'minimum_word_compliance': 0.8,  # 80% del objetivo mínimo
            'maximum_word_allowance': 1.3,   # 130% del objetivo máximo
            'chapter_consistency_threshold': 0.75
        }
        
        return {
            'min_content_length_per_chapter': min_content_length_per_chapter,
            'quality_thresholds': quality_thresholds
        }


# =====================================
# UTILIDAD HELPER FUNCTION
# =====================================

def create_dynamic_configuration_from_user_form(form_data: Dict[str, Any]) -> DynamicSystemConfiguration:
    """
    Crea configuración dinámica desde datos del formulario de generación.
    
    Args:
        form_data: Datos del formulario POST desde /books/generate/start
        
    Returns:
        DynamicSystemConfiguration optimizada para el usuario
        
    Example:
        form_data = {
            'title': 'Mi Libro',
            'genre': 'ficcion',
            'language': 'es',
            'description': 'Un libro sobre...',
            'audience': 'adult',
            'tone': 'serious',
            'chapters': 12,
            'length': 'medium',
            'pageSize': 'A5',
            'lineSpacing': 'medium'
        }
        
        config = create_dynamic_configuration_from_user_form(form_data)
        # Ahora config contiene toda la configuración del sistema
        # optimizada específicamente para este libro del usuario
    """
    user_config = UserConfiguration(
        title=form_data.get('title', ''),
        genre=form_data.get('genre', ''),
        language=form_data.get('language', 'es'),
        description=form_data.get('description', ''),
        audience=form_data.get('audience', 'adult'),
        tone=form_data.get('tone', ''),
        chapters=int(form_data.get('chapters', 10)),
        length=form_data.get('length', 'medium'),
        page_size=form_data.get('pageSize', 'pocket'),
        line_spacing=form_data.get('lineSpacing', 'medium'),
        additional_instructions=form_data.get('additional_instructions', '')
    )
    
    return DynamicConfigurationBuilder.build_dynamic_configuration(user_config)