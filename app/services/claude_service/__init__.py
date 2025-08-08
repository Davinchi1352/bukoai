"""
Claude Service Module (Refactored)

Service module for Claude AI integration with component-based architecture.
Este módulo exporta el ClaudeServiceFacade como ClaudeService para mantener
compatibilidad completa con el código existente.
"""

import logging
from typing import Optional
from .claude_service_facade import ClaudeServiceFacade

logger = logging.getLogger(__name__)

# Exportar el facade como ClaudeService para compatibilidad
ClaudeService = ClaudeServiceFacade

# Singleton instance para compatibilidad con el código original
_claude_service: Optional[ClaudeService] = None

def get_claude_service() -> ClaudeService:
    """
    Get or create Claude service singleton instance.
    
    Función de compatibilidad que mantiene el mismo patrón singleton
    del ClaudeService original.
    
    Returns:
        ClaudeService: Instancia singleton del servicio Claude
    """
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeService()
    return _claude_service

# También exportar componentes individuales para uso avanzado
from .config.claude_config import ClaudeConfig
from .clients.claude_client import ClaudeClient
from .generators.architecture_generator import ArchitectureGenerator
from .generators.content_generator import ContentGenerator
from .builders.regeneration_builder import RegenerationBuilder
from .builders.structure_builder import StructureBuilder
from .builders.message_builder import MessageBuilder

__all__ = [
    "ClaudeService",  # Facade principal (compatibilidad)
    "get_claude_service",  # Función singleton (compatibilidad)
    # Componentes individuales
    "ClaudeConfig",
    "ClaudeClient", 
    "ArchitectureGenerator",
    "ContentGenerator",
    "RegenerationBuilder",
    "StructureBuilder",
    "MessageBuilder"
]

logger.info("ClaudeService refactored architecture loaded successfully")