"""
Token Configuration Management

Maneja específicamente la configuración de tokens y límites para diferentes tipos de contenido.
Extraído de la lógica de tokens del ClaudeService original.
"""

from typing import Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TokenConfig:
    """
    Configuración específica de tokens por tipo de contenido.
    
    Centraliza toda la lógica de límites de tokens que estaba
    distribuida en ClaudeService original.
    """
    
    # Límites base extraídos de claude_service.py línea 70-77
    TOKEN_LIMITS: Dict[str, int] = None
    
    # Configuración de thinking
    base_thinking_budget: int = 45000
    thinking_margin: int = 500  # Margen reducido de 1000→500 para más thinking
    
    def __post_init__(self):
        """Initialize token limits if not provided."""
        if self.TOKEN_LIMITS is None:
            # 🚀 MAX_TOKENS OPTIMIZADOS: Eficiencia máxima SIN comprometer páginas
            # Extraído exactamente de claude_service.py línea 70-77
            self.TOKEN_LIMITS = {
                'architecture': 12000,      # 🚀 Reducido de 16K→12K - Arquitectura eficiente
                'chunk_main': 40000,        # 🚀 Aumentado de 32K→40K - Buffer ampliado para evitar truncamiento
                'introduction': 6000,       # 🚀 Reducido de 8K→6K - Introducciones eficientes
                'conclusion': 6000,         # 🚀 Reducido de 8K→6K - Conclusiones eficientes  
                'continuation': 20000,      # 🚀 Aumentado de 16K→20K - Continuaciones más sustanciales
                'expansion': 10000          # 🚀 Reducido de 12K→10K - Expansiones precisas
            }
    
    def get_tokens_for_content_type(self, content_type: str, default: int = 28000) -> int:
        """
        Obtiene tokens optimizados según tipo de contenido.
        
        Equivale exactamente a ClaudeService._get_optimized_tokens() línea 120-122.
        
        Args:
            content_type: Tipo de contenido ('architecture', 'chunk_main', etc.)
            default: Valor por defecto si no se encuentra el tipo
        
        Returns:
            Número de tokens para el tipo de contenido
        """
        tokens = self.TOKEN_LIMITS.get(content_type, default)
        logger.debug(f"Tokens for content type '{content_type}': {tokens}")
        return tokens
    
    def get_limit(self, content_type: str, default: int = 28000) -> int:
        """
        Método alias para compatibilidad hacia atrás.
        
        DEPRECATED: Usar get_tokens_for_content_type() en lugar de este método.
        Este método existe solo para evitar errores en código legacy.
        
        Args:
            content_type: Tipo de contenido ('architecture', 'chunk_main', etc.)
            default: Valor por defecto si no se encuentra el tipo
        
        Returns:
            Número de tokens para el tipo de contenido
        """
        logger.warning(f"DEPRECATED: get_limit() called for '{content_type}'. Use get_tokens_for_content_type() instead.")
        return self.get_tokens_for_content_type(content_type, default)
    
    def get_thinking_budget_for_content_type(self, content_type: str, 
                                           max_thinking_budget: int = None) -> int:
        """
        Obtiene thinking budget optimizado según tipo de contenido.
        
        Equivale exactamente a ClaudeService._get_optimized_thinking_budget() línea 124-128.
        
        Args:
            content_type: Tipo de contenido
            max_thinking_budget: Budget máximo (usa base si None)
        
        Returns:
            Thinking budget optimizado para el tipo de contenido
        """
        if max_thinking_budget is None:
            max_thinking_budget = self.base_thinking_budget
            
        max_tokens = self.get_tokens_for_content_type(content_type)
        
        # 🧠 PENSAMIENTO EXTENDIDO: Usar todo el budget disponible para máxima calidad
        thinking_budget = min(max_tokens - self.thinking_margin, max_thinking_budget)
        
        logger.debug(f"Thinking budget for '{content_type}': {thinking_budget} "
                    f"(max_tokens={max_tokens}, margin={self.thinking_margin})")
        
        return thinking_budget
    
    def get_all_token_limits(self) -> Dict[str, int]:
        """Retorna todos los límites de tokens configurados."""
        return self.TOKEN_LIMITS.copy()
    
    def is_valid_content_type(self, content_type: str) -> bool:
        """Verifica si un tipo de contenido es válido."""
        return content_type in self.TOKEN_LIMITS
    
    def get_supported_content_types(self) -> list:
        """Retorna lista de tipos de contenido soportados."""
        return list(self.TOKEN_LIMITS.keys())
    
    def calculate_total_tokens_for_book(self, chapters: int, include_intro: bool = True, 
                                      include_conclusion: bool = True) -> int:
        """
        Calcula tokens totales estimados para un libro completo.
        
        Args:
            chapters: Número de capítulos
            include_intro: Si incluir introducción
            include_conclusion: Si incluir conclusión
            
        Returns:
            Estimación de tokens totales
        """
        total = 0
        
        # Arquitectura
        total += self.get_tokens_for_content_type('architecture')
        
        # Introducción
        if include_intro:
            total += self.get_tokens_for_content_type('introduction')
        
        # Capítulos principales (usando chunk_main como estimación por capítulo)
        total += chapters * self.get_tokens_for_content_type('chunk_main')
        
        # Conclusión
        if include_conclusion:
            total += self.get_tokens_for_content_type('conclusion')
        
        logger.info(f"Estimated total tokens for {chapters} chapters: {total:,}")
        return total
    
    def __str__(self) -> str:
        """String representation of token configuration."""
        limits = ', '.join(f"{k}={v}" for k, v in self.TOKEN_LIMITS.items())
        return f"TokenConfig(thinking_budget={self.base_thinking_budget}, limits={{{limits}}})"