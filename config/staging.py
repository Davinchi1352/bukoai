"""
Configuración para entorno de staging
"""

import os

from .base import BaseConfig


class StagingConfig(BaseConfig):
    """Configuración para staging - ambiente similar a producción pero con más logging"""

    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "postgresql://user:password@localhost:5432/buko_ai_staging"
    SQLALCHEMY_ECHO = False
    
    # Debug toolbar deshabilitado
    DEBUG_TB_ENABLED = False
    
    # Email configuración real
    MAIL_SUPPRESS_SEND = False
    MAIL_DEBUG = False
    
    # Logging intermedio
    LOG_LEVEL = "INFO"
    
    # Cache habilitado
    CACHE_TYPE = "redis"
    CACHE_DEFAULT_TIMEOUT = 300
    
    # WebSocket sin logging detallado
    SOCKETIO_LOGGER = False
    SOCKETIO_ENGINEIO_LOGGER = False
    
    # Celery configuración normal
    CELERY_ALWAYS_EAGER = False
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = False
    
    # Rate limiting habilitado pero permisivo
    RATELIMIT_ENABLED = True
    
    # Pagos en sandbox para testing
    PAYPAL_MODE = "sandbox"
    
    # Seguridad intermedia
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    
    # Templates no auto-reload
    TEMPLATES_AUTO_RELOAD = False
    
    # Staging específico
    EXPLAIN_TEMPLATE_LOADING = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    
    # Features habilitadas para testing
    FEATURE_COVER_GENERATION = True
    FEATURE_EPUB_EXPORT = True
    FEATURE_DOCX_EXPORT = True
    FEATURE_COLLABORATION = True
    FEATURE_API_ACCESS = True
    FEATURE_REFERRAL_PROGRAM = True
    
    # Métricas habilitadas
    ADMIN_METRICS_ENABLED = True
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Archivos en storage compartido
    UPLOAD_FOLDER = "/storage/uploads"
    BOOKS_FOLDER = "/storage/books"
    COVERS_FOLDER = "/storage/covers"
    
    # Dominio de staging
    DOMAIN = os.environ.get("DOMAIN", "staging.buko-ai.com")
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://staging.buko-ai.com")
    API_URL = os.environ.get("API_URL", "https://staging.buko-ai.com/api")
    
    @staticmethod
    def init_app(app):
        """Configuración específica para staging"""
        BaseConfig.init_app(app)
        
        # Configurar logging para staging
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        file_handler = RotatingFileHandler(
            "logs/buko-ai-staging.log",
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s"
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("Buko AI Staging startup")
        
        # Configurar Sentry para staging
        if app.config.get("SENTRY_DSN"):
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            
            sentry_sdk.init(
                dsn=app.config["SENTRY_DSN"],
                integrations=[
                    FlaskIntegration(),
                    SqlalchemyIntegration(),
                ],
                traces_sample_rate=0.1,
                environment="staging",
            )