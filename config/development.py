"""
Configuración para entorno de desarrollo
"""

import os

from .base import BaseConfig


class DevelopmentConfig(BaseConfig):
    """Configuración para desarrollo"""

    DEBUG = True
    TESTING = False
    
    # Database - PostgreSQL optimizado para desarrollo con 10K usuarios
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "postgresql://postgres:postgres@localhost:5434/buko_ai_dev"
    SQLALCHEMY_ECHO = bool(os.environ.get("SQLALCHEMY_ECHO", "False"))  # Disable por defecto para performance
    
    # Override pool settings para desarrollo
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
        "pool_timeout": 30,
        "pool_size": int(os.environ.get("DB_POOL_SIZE", "10")),        # 10 conexiones en dev
        "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", "15")),  # 15 adicionales en dev
        "pool_reset_on_return": "commit",
        "echo": False,
        "connect_args": {
            "connect_timeout": 10,
            "application_name": "buko_ai_dev"
        }
    }
    
    # Debug toolbar
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    
    # Email - usar consola en desarrollo
    MAIL_SUPPRESS_SEND = False
    MAIL_DEBUG = True
    
    # Logging más detallado
    LOG_LEVEL = "DEBUG"
    
    # Redis para cache y Celery en desarrollo
    REDIS_URL = os.environ.get("REDIS_URL") or "redis://localhost:6380/0"
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.environ.get("REDIS_URL") or "redis://localhost:6380/1"
    CACHE_DEFAULT_TIMEOUT = 300  # Cache más corto en desarrollo
    
    # Redis optimizado para desarrollo
    CACHE_REDIS_CONNECTION_POOL_KWARGS = {
        'max_connections': 20,  # Menos conexiones en dev
        'retry_on_timeout': True,
        'socket_keepalive': True,
        'socket_connect_timeout': 5,
        'socket_timeout': 5,
        'health_check_interval': 60
    }
    
    # Celery - Desarrollo con simulación de 10K usuarios
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL") or "redis://localhost:6380/0"
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND") or "redis://localhost:6380/0"
    
    # Override para desarrollo (simular carga pero más rápido)
    CELERY_WORKER_CONCURRENCY = int(os.environ.get("CELERY_WORKER_CONCURRENCY", 4))  # 4 workers en dev
    CELERY_TASK_SOFT_TIME_LIMIT = int(os.environ.get("CELERY_TASK_SOFT_TIME_LIMIT", 1800))  # 30 min en dev
    CELERY_TASK_TIME_LIMIT = int(os.environ.get("CELERY_TASK_TIME_LIMIT", 2400))         # 40 min en dev
    
    # WebSocket optimizado para desarrollo
    SOCKETIO_LOGGER = bool(os.environ.get("SOCKETIO_LOGGER", "True"))    # Más logs en dev
    SOCKETIO_ENGINEIO_LOGGER = bool(os.environ.get("SOCKETIO_ENGINEIO_LOGGER", "False"))  # Reducir spam
    SOCKETIO_PING_TIMEOUT = 120       # Más tiempo en desarrollo
    SOCKETIO_PING_INTERVAL = 30       # Más frecuente en desarrollo
    
    # Configuración de desarrollo para WebSocket
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"  # Permisivo en dev
    SOCKETIO_MAX_HTTP_BUFFER_SIZE = 50000  # Menor buffer en dev
    
    # Celery configuración para desarrollo
    CELERY_ALWAYS_EAGER = os.environ.get("CELERY_ALWAYS_EAGER", "False").lower() in ["true", "1", "yes"]
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
    
    # Rate limiting más permisivo en desarrollo
    CELERY_TASK_ANNOTATIONS = {
        'app.tasks.book_generation.generate_book_architecture_task': {'rate_limit': '10/h'},
        'app.tasks.book_generation.generate_book_task': {'rate_limit': '5/h'},
        'app.tasks.email_tasks.*': {'rate_limit': '1000/m'},
    }
    
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