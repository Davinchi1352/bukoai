"""
Configuración para entorno de desarrollo
"""

import os

from .base import BaseConfig


class DevelopmentConfig(BaseConfig):
    """Configuración para desarrollo"""

    DEBUG = True
    TESTING = False
    
    # Database - PostgreSQL para desarrollo
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "postgresql://postgres:postgres@localhost:5434/buko_ai_dev"
    SQLALCHEMY_ECHO = True
    
    # Debug toolbar
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    
    # Email - usar consola en desarrollo
    MAIL_SUPPRESS_SEND = False
    MAIL_DEBUG = True
    
    # Logging más detallado
    LOG_LEVEL = "DEBUG"
    
    # Redis para cache y Celery
    REDIS_URL = os.environ.get("REDIS_URL") or "redis://localhost:6380/0"
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.environ.get("REDIS_URL") or "redis://localhost:6380/1"
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Celery
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL") or "redis://localhost:6380/0"
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND") or "redis://localhost:6380/0"
    
    # WebSocket con logging detallado
    SOCKETIO_LOGGER = True
    SOCKETIO_ENGINEIO_LOGGER = True
    
    # Celery configuración para desarrollo
    CELERY_ALWAYS_EAGER = os.environ.get("CELERY_ALWAYS_EAGER", "False").lower() in ["true", "1", "yes"]
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
    
    # Rate limiting más permisivo
    RATELIMIT_ENABLED = False
    
    # Pagos en sandbox
    PAYPAL_MODE = "sandbox"
    
    # Seguridad relajada para desarrollo
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    
    # Hot reload para templates
    TEMPLATES_AUTO_RELOAD = True
    
    # Desarrollo específico
    EXPLAIN_TEMPLATE_LOADING = False
    PRESERVE_CONTEXT_ON_EXCEPTION = True
    
    # Claude AI Configuration - Latest Model
    CLAUDE_MODEL = os.environ.get('CLAUDE_MODEL', 'claude-sonnet-4-20250514')
    CLAUDE_MAX_TOKENS = int(os.environ.get('CLAUDE_MAX_TOKENS', '64000'))
    CLAUDE_TEMPERATURE = float(os.environ.get('CLAUDE_TEMPERATURE', '1'))
    CLAUDE_THINKING_BUDGET = int(os.environ.get('CLAUDE_THINKING_BUDGET', '63999'))
    CLAUDE_MAX_RETRIES = int(os.environ.get('CLAUDE_MAX_RETRIES', '3'))
    CLAUDE_RETRY_DELAY = float(os.environ.get('CLAUDE_RETRY_DELAY', '1.0'))
    
    # Features habilitadas en desarrollo
    FEATURE_COVER_GENERATION = True
    FEATURE_EPUB_EXPORT = True
    FEATURE_DOCX_EXPORT = True
    FEATURE_COLLABORATION = True
    FEATURE_API_ACCESS = True
    FEATURE_REFERRAL_PROGRAM = True
    
    # Métricas detalladas
    ADMIN_METRICS_ENABLED = True
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Archivos locales
    UPLOAD_FOLDER = "storage/uploads"
    BOOKS_FOLDER = "storage/books"
    COVERS_FOLDER = "storage/covers"
    STORAGE_PATH = "storage"
    
    # Subscription plans
    from config.subscription_plans import SUBSCRIPTION_PLANS
    SUBSCRIPTION_PLANS = SUBSCRIPTION_PLANS
    
    @staticmethod
    def init_app(app):
        """Configuración específica para desarrollo"""
        BaseConfig.init_app(app)
        
        # Configurar logging para desarrollo
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        file_handler = RotatingFileHandler(
            "logs/buko-ai-dev.log",
            maxBytes=10240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s [in %(pathname)s:%(lineno)d]"
        ))
        file_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.DEBUG)
        app.logger.info("Buko AI Development startup")