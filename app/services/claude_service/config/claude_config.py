"""
Claude AI Configuration Management

Configuración centralizada para todos los componentes del sistema Claude AI.
Extrae toda la configuración hardcodeada del ClaudeService original.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class ClaudeConfig:
    """
    Configuración centralizada para Claude API.
    
    Esta clase reemplaza la configuración hardcodeada distribuida
    en ClaudeService original, centralizando todos los parámetros.
    """
    
    # =====================================
    # API CONFIGURATION
    # =====================================
    api_key: Optional[str] = None
    model: str = 'claude-sonnet-4-20250514'
    temperature: float = 1.0
    
    # =====================================
    # TOKEN CONFIGURATION
    # =====================================
    max_tokens: int = 28000
    thinking_budget: int = 45000
    
    # Token limits por tipo de contenido (extraído de claude_service.py línea 70-77)
    token_limits: Dict[str, int] = None
    
    # =====================================
    # TIMEOUT CONFIGURATION 
    # =====================================
    # Timeouts extraídos de claude_service.py línea 86-89
    architecture_timeout: int = 2400  # 40 minutos
    chunk_timeout: int = 3600         # 60 minutos  
    thinking_timeout: int = 1200      # 20 minutos
    
    # HTTP timeouts
    http_connect_timeout: int = 60
    http_read_timeout: int = 1800
    http_write_timeout: int = 60
    http_pool_timeout: int = 60
    
    # =====================================
    # CHUNK CONFIGURATION
    # =====================================
    # Multi-chunk config extraído de claude_service.py línea 82-84
    chunk_overlap: int = 500
    max_chunks: int = 7
    
    # =====================================
    # CIRCUIT BREAKER CONFIGURATION
    # =====================================
    circuit_failure_threshold: int = 5
    circuit_timeout: int = 300  # 5 minutos
    
    # =====================================
    # ARCHITECTURE GENERATION CONFIGURATION
    # =====================================
    # Configuraciones específicas para generación de arquitectura
    progress_check_interval: int = 10  # Intervalo para actualizar progreso
    min_content_length: int = 100      # Mínimo caracteres para arquitectura válida
    default_target_pages: int = 150    # Páginas por defecto si no se especifica
    
    # Configuraciones de progreso
    progress_update_frequency: int = 50  # Cada cuántos deltas actualizar progreso
    progress_start: int = 15            # Progreso inicial de generación
    progress_divider: int = 10          # Divisor para cálculo de progreso
    progress_max: int = 85              # Progreso máximo durante generación
    
    # Etapas de progreso fijas
    progress_connecting: int = 5        # Conectando con API
    progress_thinking: int = 15         # Claude pensando
    progress_processing: int = 90       # Procesando resultado
    progress_completed: int = 100       # Completado
    
    # =====================================
    # BOOK STRUCTURE CONFIGURATION
    # =====================================
    # Configuraciones para estructura de libros
    min_chapters: int = 8               # Mínimo capítulos
    max_chapters: int = 25              # Máximo capítulos
    min_words_per_page: int = 250       # Mínimo palabras por página
    max_words_per_page: int = 350       # Máximo palabras por página
    
    def __post_init__(self):
        """Initialize token_limits if not provided."""
        if self.token_limits is None:
            # Configuración exacta de token_limits de claude_service.py línea 70-77
            self.token_limits = {
                'architecture': 12000,      # 🚀 Reducido de 16K→12K - Arquitectura eficiente
                'chunk_main': 40000,        # 🚀 Aumentado de 32K→40K - Buffer ampliado para evitar truncamiento
                'introduction': 6000,       # 🚀 Reducido de 8K→6K - Introducciones eficientes
                'conclusion': 6000,         # 🚀 Reducido de 8K→6K - Conclusiones eficientes  
                'continuation': 20000,      # 🚀 Aumentado de 16K→20K - Continuaciones más sustanciales
                'expansion': 10000          # 🚀 Reducido de 12K→10K - Expansiones precisas
            }
        
        # Inicializar token_config para compatibilidad
        from .token_config import TokenConfig
        self.token_config = TokenConfig()
    
    @classmethod
    def from_app_config(cls, app_config: Dict[str, Any]) -> 'ClaudeConfig':
        """
        Crear configuración desde Flask app.config.
        
        Mantiene exactamente la misma lógica de configuración que
        ClaudeService.__init__() líneas 44-89.
        """
        return cls(
            api_key=app_config.get('ANTHROPIC_API_KEY'),
            model=app_config.get('CLAUDE_MODEL', 'claude-sonnet-4-20250514'),
            max_tokens=app_config.get('CLAUDE_MAX_TOKENS', 28000),
            temperature=app_config.get('CLAUDE_TEMPERATURE', 1.0),
            thinking_budget=app_config.get('CLAUDE_THINKING_BUDGET', 45000)
        )
    
    def get_tokens_for_content_type(self, content_type: str) -> int:
        """
        Obtiene tokens optimizados según tipo de contenido.
        
        Equivale a ClaudeService._get_optimized_tokens() línea 120-122.
        """
        return self.token_limits.get(content_type, self.max_tokens)
    
    def get_thinking_budget_for_content_type(self, content_type: str) -> int:
        """
        Obtiene thinking budget optimizado según tipo de contenido.
        
        Equivale a ClaudeService._get_optimized_thinking_budget() línea 124-128.
        """
        max_tokens = self.get_tokens_for_content_type(content_type)
        # 🧠 PENSAMIENTO EXTENDIDO: Usar todo el budget disponible para máxima calidad
        return min(max_tokens - 500, self.thinking_budget)  # Reducido margen de 1000→500 para más thinking
    
    def validate(self, require_api_key: bool = True) -> None:
        """
        Valida que la configuración sea válida.
        
        Args:
            require_api_key: Si True, requiere API key. False para testing.
        """
        if require_api_key and not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")
        
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        
        if self.thinking_budget <= 0:
            raise ValueError("thinking_budget must be positive")
        
        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("temperature must be between 0 and 2")
        
        logger.info(f"Claude configuration validated: model={self.model}, "
                   f"max_tokens={self.max_tokens}, thinking_budget={self.thinking_budget}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    def __str__(self) -> str:
        """String representation hiding sensitive data."""
        return (f"ClaudeConfig(model={self.model}, max_tokens={self.max_tokens}, "
               f"max_chunks={self.max_chunks}, api_key={'***' if self.api_key else 'None'})")