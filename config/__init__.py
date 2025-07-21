"""
Factory de configuracion para diferentes entornos de Buko AI
"""

import os

from .base import BaseConfig
from .development import DevelopmentConfig
from .production import ProductionConfig
from .staging import StagingConfig
from .testing import TestingConfig

# Mapeo de entornos a clases de configuracion
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config(environment=None):
    """
    Obtiene la configuraci�n apropiada basada en el entorno
    
    Args:
        environment (str): Nombre del entorno (development, staging, production, testing)
        
    Returns:
        BaseConfig: Clase de configuraci�n apropiada
    """
    if environment is None:
        environment = os.getenv("FLASK_ENV", "development")
    
    return config.get(environment, config["default"])


def configure_app(app, environment=None):
    """
    Configura la aplicaci�n Flask con la configuraci�n apropiada
    
    Args:
        app (Flask): Instancia de la aplicaci�n Flask
        environment (str): Nombre del entorno
    """
    config_class = get_config(environment)
    app.config.from_object(config_class)
    config_class.init_app(app)
    
    # Configurar logging b�sico
    import logging
    from logging.handlers import RotatingFileHandler
    
    if not app.debug and not app.testing:
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        file_handler = RotatingFileHandler(
            "logs/buko-ai.log",
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s [in %(pathname)s:%(lineno)d]"
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info("Buko AI startup")