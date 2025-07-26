"""
Configuración base para Buko AI
"""

import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    """Configuración base que será heredada por otros entornos"""

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"
    
    # Database - Optimizado para 10K usuarios concurrentes
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "postgresql://postgres:postgres@localhost:5432/buko_ai"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = bool(os.environ.get("SQLALCHEMY_RECORD_QUERIES", "False"))  # Solo en debug
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,        # 30 minutos para conexiones largas
        "pool_timeout": 30,          # 30 segundos timeout
        "pool_size": int(os.environ.get("DB_POOL_SIZE", "20")),        # 20 conexiones por proceso
        "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", "30")),  # 30 conexiones adicionales
        "pool_reset_on_return": "commit",  # Reset automático
        "echo": False,  # Disable SQL logging for performance
        "connect_args": {
            "connect_timeout": 10,
            "application_name": "buko_ai"
        }
    }
    
    # Redis
    REDIS_URL = os.environ.get("REDIS_URL") or "redis://localhost:6379/0"
    
    # Celery - Optimizado para 10,000 usuarios con libros de alta calidad
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL") or "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND") or "redis://localhost:6379/0"
    
    # Configuración para alta concurrencia (10K usuarios)
    CELERY_WORKER_CONCURRENCY = int(os.environ.get("CELERY_WORKER_CONCURRENCY", 8))  # 8 workers por nodo
    CELERY_TASK_SOFT_TIME_LIMIT = int(os.environ.get("CELERY_TASK_SOFT_TIME_LIMIT", 5400))  # 90 min soft (calidad)
    CELERY_TASK_TIME_LIMIT = int(os.environ.get("CELERY_TASK_TIME_LIMIT", 7200))      # 2h hard limit
    CELERY_WORKER_PREFETCH_MULTIPLIER = int(os.environ.get("CELERY_WORKER_PREFETCH_MULTIPLIER", 4))  # 4 tareas por worker
    
    # Retry configuration para errores temporales
    CELERY_MAX_RETRIES = int(os.environ.get("CELERY_MAX_RETRIES", 3))
    CELERY_RETRY_DELAY = int(os.environ.get("CELERY_RETRY_DELAY", 180))  # 3 minutos entre reintentos
    CELERY_RETRY_BACKOFF = bool(os.environ.get("CELERY_RETRY_BACKOFF", "True"))  # Exponential backoff
    CELERY_RETRY_JITTER = bool(os.environ.get("CELERY_RETRY_JITTER", "True"))  # Random jitter
    
    # Worker configuration para estabilidad con alta carga
    CELERY_WORKER_MAX_TASKS_PER_CHILD = int(os.environ.get("CELERY_WORKER_MAX_TASKS_PER_CHILD", 20))  # Más tareas por worker
    CELERY_WORKER_MAX_MEMORY_PER_CHILD = int(os.environ.get("CELERY_WORKER_MAX_MEMORY_PER_CHILD", 1000000))  # 1GB limite
    CELERY_WORKER_DISABLE_RATE_LIMITS = bool(os.environ.get("CELERY_WORKER_DISABLE_RATE_LIMITS", "True"))
    
    # Task routing con prioridades para 10K usuarios
    CELERY_TASK_ROUTES = {
        'app.tasks.book_generation.generate_book_architecture_task': {
            'queue': 'architecture_high',
            'priority': 7
        },
        'app.tasks.book_generation.generate_book_task': {
            'queue': 'book_generation_normal', 
            'priority': 5
        },
        'app.tasks.book_generation.regenerate_book_architecture_task': {
            'queue': 'architecture_high',
            'priority': 8
        },
        'app.tasks.email_tasks.*': {
            'queue': 'emails_low',
            'priority': 3
        },
    }
    
    # Priority queues para manejar 10K usuarios
    CELERY_TASK_DEFAULT_PRIORITY = 5
    CELERY_TASK_INHERIT_PARENT_PRIORITY = True
    
    # Broker configuration para alta carga
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
    CELERY_BROKER_CONNECTION_MAX_RETRIES = 10
    CELERY_BROKER_POOL_LIMIT = 20
    
    # Result backend optimizado
    CELERY_RESULT_EXPIRES = int(os.environ.get("CELERY_RESULT_EXPIRES", 3600))  # 1 hora (limpieza rápida)
    CELERY_RESULT_BACKEND_MAX_RETRIES = 5
    CELERY_RESULT_BACKEND_RETRY_DELAY = 1
    
    # Monitoring y metrics para 10K usuarios
    CELERY_SEND_TASK_EVENTS = True
    CELERY_SEND_EVENTS = True
    CELERY_TASK_SEND_SENT_EVENT = True
    
    # Rate limiting por usuario para prevenir abuse
    CELERY_TASK_ANNOTATIONS = {
        'app.tasks.book_generation.generate_book_architecture_task': {'rate_limit': '3/h'},  # 3 arquitecturas por hora
        'app.tasks.book_generation.generate_book_task': {'rate_limit': '2/h'},              # 2 libros por hora
        'app.tasks.email_tasks.*': {'rate_limit': '100/m'},                                 # 100 emails por minuto
    }
    
    # Claude AI - Latest Model Configuration (claude-sonnet-4-20250514)
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
    CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")
    CLAUDE_MAX_TOKENS = int(os.environ.get("CLAUDE_MAX_TOKENS", 64000))
    CLAUDE_TEMPERATURE = float(os.environ.get("CLAUDE_TEMPERATURE", 1))
    CLAUDE_THINKING_BUDGET = int(os.environ.get("CLAUDE_THINKING_BUDGET", 63999))
    CLAUDE_MAX_RETRIES = int(os.environ.get("CLAUDE_MAX_RETRIES", 3))
    CLAUDE_RETRY_DELAY = float(os.environ.get("CLAUDE_RETRY_DELAY", 1.0))
    
    # Email
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True").lower() in ["true", "1", "yes"]
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "False").lower() in ["true", "1", "yes"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@buko-ai.com")
    
    # Payments
    PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID")
    PAYPAL_CLIENT_SECRET = os.environ.get("PAYPAL_CLIENT_SECRET")
    PAYPAL_MODE = os.environ.get("PAYPAL_MODE", "sandbox")
    PAYPAL_WEBHOOK_ID = os.environ.get("PAYPAL_WEBHOOK_ID")
    
    MP_ACCESS_TOKEN = os.environ.get("MP_ACCESS_TOKEN")
    MP_CLIENT_ID = os.environ.get("MP_CLIENT_ID")
    MP_CLIENT_SECRET = os.environ.get("MP_CLIENT_SECRET")
    MP_WEBHOOK_SECRET = os.environ.get("MP_WEBHOOK_SECRET")
    
    # Business
    DEFAULT_BOOK_PRICE = float(os.environ.get("DEFAULT_BOOK_PRICE", 15.00))
    CURRENCY = os.environ.get("CURRENCY", "USD")
    FREE_PLAN_BOOKS_LIMIT = int(os.environ.get("FREE_PLAN_BOOKS_LIMIT", 1))
    FREE_PLAN_PAGES_LIMIT = int(os.environ.get("FREE_PLAN_PAGES_LIMIT", 30))
    
    # Subscription plans
    SUBSCRIPTION_PLANS = {
        "free": {
            "name": "Free",
            "price": 0,
            "books_per_month": FREE_PLAN_BOOKS_LIMIT,
            "max_pages": FREE_PLAN_PAGES_LIMIT,
            "features": ["Libro básico", "Formato PDF"],
        },
        "starter": {
            "name": "Starter",
            "price": float(os.environ.get("STARTER_PLAN_PRICE", 19.00)),
            "books_per_month": 2,
            "max_pages": 100,
            "features": ["Todos los formatos", "Soporte email"],
        },
        "pro": {
            "name": "Pro",
            "price": float(os.environ.get("PRO_PLAN_PRICE", 49.00)),
            "books_per_month": 5,
            "max_pages": 150,
            "features": ["Prioridad en cola", "Diseño portada básico"],
        },
        "business": {
            "name": "Business",
            "price": float(os.environ.get("BUSINESS_PLAN_PRICE", 149.00)),
            "books_per_month": 15,
            "max_pages": 200,
            "features": ["API access", "Soporte prioritario"],
        },
        "enterprise": {
            "name": "Enterprise",
            "price": float(os.environ.get("ENTERPRISE_PLAN_PRICE", 399.00)),
            "books_per_month": 50,
            "max_pages": 200,
            "features": ["Dedicado", "SLA garantizado"],
        },
    }
    
    # Add-ons
    ADDONS = {
        "cover_design": {"price": 5.00, "name": "Diseño de Portada Premium"},
        "formatting": {"price": 3.00, "name": "Formateo Profesional"},
    }
    
    # File Storage
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "storage/uploads")
    BOOKS_FOLDER = os.environ.get("BOOKS_FOLDER", "storage/books")
    COVERS_FOLDER = os.environ.get("COVERS_FOLDER", "storage/covers")
    MAX_UPLOAD_SIZE = int(os.environ.get("MAX_UPLOAD_SIZE", 10485760))
    ALLOWED_EXTENSIONS = set(
        os.environ.get("ALLOWED_EXTENSIONS", "txt,pdf,png,jpg,jpeg,gif,doc,docx").split(",")
    )
    
    # Security
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES", 86400))
    )
    PASSWORD_RESET_TOKEN_EXPIRES = int(os.environ.get("PASSWORD_RESET_TOKEN_EXPIRES", 3600))
    EMAIL_VERIFICATION_TOKEN_EXPIRES = int(os.environ.get("EMAIL_VERIFICATION_TOKEN_EXPIRES", 86400))
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get("RATE_LIMIT_STORAGE_URL", "redis://localhost:6379/1")
    RATELIMIT_PER_METHOD = os.environ.get("RATE_LIMIT_PER_METHOD", "True").lower() in ["true", "1", "yes"]
    RATELIMIT_HEADERS_ENABLED = os.environ.get("RATE_LIMIT_HEADERS_ENABLED", "True").lower() in ["true", "1", "yes"]
    
    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE = os.environ.get("LOG_FILE", "logs/buko-ai.log")
    LOG_MAX_SIZE = int(os.environ.get("LOG_MAX_SIZE", 10485760))
    LOG_BACKUP_COUNT = int(os.environ.get("LOG_BACKUP_COUNT", 5))
    LOG_FORMAT = os.environ.get("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # WebSocket - Optimizado para 10K usuarios concurrentes
    SOCKETIO_ASYNC_MODE = os.environ.get("SOCKETIO_ASYNC_MODE", "threading")
    SOCKETIO_LOGGER = os.environ.get("SOCKETIO_LOGGER", "False").lower() in ["true", "1", "yes"]  # Reducir logs
    SOCKETIO_ENGINEIO_LOGGER = os.environ.get("SOCKETIO_ENGINEIO_LOGGER", "False").lower() in ["true", "1", "yes"]
    
    # Timeouts optimizados para alta concurrencia
    SOCKETIO_PING_TIMEOUT = int(os.environ.get("SOCKETIO_PING_TIMEOUT", 120))     # 2 minutos 
    SOCKETIO_PING_INTERVAL = int(os.environ.get("SOCKETIO_PING_INTERVAL", 60))   # 1 minuto
    
    # Configuración adicional para 10K usuarios
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.environ.get("SOCKETIO_CORS_ALLOWED_ORIGINS", "*")
    SOCKETIO_MAX_HTTP_BUFFER_SIZE = int(os.environ.get("SOCKETIO_MAX_HTTP_BUFFER_SIZE", 100000))  # 100KB buffer
    SOCKETIO_ALLOW_UPGRADES = bool(os.environ.get("SOCKETIO_ALLOW_UPGRADES", "True"))
    SOCKETIO_TRANSPORTS = os.environ.get("SOCKETIO_TRANSPORTS", "websocket,polling").split(",")
    
    # Connection management para alta concurrencia
    SOCKETIO_CLIENT_MANAGER_LOGGER = False  # Reducir overhead
    SOCKETIO_ALWAYS_CONNECT = False         # Evitar conexiones innecesarias
    
    # Cache - Optimizado para 10K usuarios
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "redis")
    CACHE_REDIS_URL = os.environ.get("CACHE_REDIS_URL", "redis://localhost:6379/2")
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", 900))  # 15 minutos cache
    CACHE_KEY_PREFIX = os.environ.get("CACHE_KEY_PREFIX", "buko_ai_")
    
    # Redis configuration para alta concurrencia
    CACHE_REDIS_CONNECTION_POOL_KWARGS = {
        'max_connections': int(os.environ.get("CACHE_REDIS_MAX_CONNECTIONS", "50")),
        'retry_on_timeout': True,
        'socket_keepalive': True,
        'socket_keepalive_options': {},
        'socket_connect_timeout': 5,
        'socket_timeout': 5,
        'health_check_interval': 30
    }
    
    # Cache strategies para diferentes tipos de datos
    CACHE_USER_SESSION_TIMEOUT = int(os.environ.get("CACHE_USER_SESSION_TIMEOUT", 3600))    # 1 hora
    CACHE_BOOK_DATA_TIMEOUT = int(os.environ.get("CACHE_BOOK_DATA_TIMEOUT", 1800))        # 30 minutos
    CACHE_STATISTICS_TIMEOUT = int(os.environ.get("CACHE_STATISTICS_TIMEOUT", 300))       # 5 minutos
    
    # Book Generation
    MAX_GENERATION_TIME = int(os.environ.get("MAX_GENERATION_TIME", 3600))  # 60 minutos - coincide con task_soft_time_limit
    QUEUE_DEFAULT_TIMEOUT = int(os.environ.get("QUEUE_DEFAULT_TIMEOUT", 3600))
    BOOK_GENERATION_RETRIES = int(os.environ.get("BOOK_GENERATION_RETRIES", 3))
    THINKING_ENABLED = os.environ.get("THINKING_ENABLED", "True").lower() in ["true", "1", "yes"]
    STREAMING_ENABLED = os.environ.get("STREAMING_ENABLED", "True").lower() in ["true", "1", "yes"]
    
    # Feature Flags
    FEATURE_COVER_GENERATION = os.environ.get("FEATURE_COVER_GENERATION", "True").lower() in ["true", "1", "yes"]
    FEATURE_EPUB_EXPORT = os.environ.get("FEATURE_EPUB_EXPORT", "True").lower() in ["true", "1", "yes"]
    FEATURE_DOCX_EXPORT = os.environ.get("FEATURE_DOCX_EXPORT", "True").lower() in ["true", "1", "yes"]
    FEATURE_COLLABORATION = os.environ.get("FEATURE_COLLABORATION", "False").lower() in ["true", "1", "yes"]
    FEATURE_API_ACCESS = os.environ.get("FEATURE_API_ACCESS", "False").lower() in ["true", "1", "yes"]
    FEATURE_REFERRAL_PROGRAM = os.environ.get("FEATURE_REFERRAL_PROGRAM", "False").lower() in ["true", "1", "yes"]
    
    # Localization
    LANGUAGES = os.environ.get("LANGUAGES", "es,en").split(",")
    DEFAULT_LANGUAGE = os.environ.get("DEFAULT_LANGUAGE", "es")
    BABEL_DEFAULT_LOCALE = os.environ.get("BABEL_DEFAULT_LOCALE", "es")
    BABEL_DEFAULT_TIMEZONE = os.environ.get("BABEL_DEFAULT_TIMEZONE", "UTC")
    
    # Admin
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@buko-ai.com")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "change-this-admin-password")
    ADMIN_DASHBOARD_ENABLED = os.environ.get("ADMIN_DASHBOARD_ENABLED", "True").lower() in ["true", "1", "yes"]
    ADMIN_METRICS_ENABLED = os.environ.get("ADMIN_METRICS_ENABLED", "True").lower() in ["true", "1", "yes"]
    
    # Monitoring
    SENTRY_DSN = os.environ.get("SENTRY_DSN")
    NEW_RELIC_LICENSE_KEY = os.environ.get("NEW_RELIC_LICENSE_KEY")
    NEW_RELIC_APP_NAME = os.environ.get("NEW_RELIC_APP_NAME", "Buko AI")
    
    # Analytics
    GOOGLE_ANALYTICS_ID = os.environ.get("GOOGLE_ANALYTICS_ID")
    
    # Domain and URLs
    DOMAIN = os.environ.get("DOMAIN", "localhost")
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5000")
    API_URL = os.environ.get("API_URL", "http://localhost:5000/api")
    
    # Flask-WTF
    WTF_CSRF_ENABLED = os.environ.get("WTF_CSRF_ENABLED", "True").lower() in ["true", "1", "yes"]
    WTF_CSRF_TIME_LIMIT = int(os.environ.get("WTF_CSRF_TIME_LIMIT", 3600))
    
    @staticmethod
    def init_app(app):
        """Inicialización específica de la aplicación"""
        pass