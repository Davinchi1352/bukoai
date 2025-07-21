"""
Configuración para entorno de producción
"""

import os

from .base import BaseConfig


class ProductionConfig(BaseConfig):
    """Configuración para producción - máxima seguridad y performance"""

    DEBUG = False
    TESTING = False
    
    # Database con configuración optimizada
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "postgresql://user:password@localhost:5432/buko_ai_prod"
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 20,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
        "pool_timeout": 30,
        "max_overflow": 40,
    }
    
    # Debug toolbar deshabilitado
    DEBUG_TB_ENABLED = False
    
    # Email configuración producción
    MAIL_SUPPRESS_SEND = False
    MAIL_DEBUG = False
    
    # Logging optimizado
    LOG_LEVEL = "WARNING"
    
    # Cache optimizado
    CACHE_TYPE = "redis"
    CACHE_DEFAULT_TIMEOUT = 3600
    
    # WebSocket optimizado
    SOCKETIO_LOGGER = False
    SOCKETIO_ENGINEIO_LOGGER = False
    
    # Celery configuración producción
    CELERY_ALWAYS_EAGER = False
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = False
    CELERY_WORKER_CONCURRENCY = 8
    
    # Rate limiting estricto
    RATELIMIT_ENABLED = True
    
    # Pagos en vivo
    PAYPAL_MODE = "live"
    
    # Seguridad máxima
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"
    
    # Templates optimizados
    TEMPLATES_AUTO_RELOAD = False
    
    # Producción específico
    EXPLAIN_TEMPLATE_LOADING = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    
    # Features controladas por flags
    FEATURE_COVER_GENERATION = os.environ.get("FEATURE_COVER_GENERATION", "True").lower() in ["true", "1", "yes"]
    FEATURE_EPUB_EXPORT = os.environ.get("FEATURE_EPUB_EXPORT", "True").lower() in ["true", "1", "yes"]
    FEATURE_DOCX_EXPORT = os.environ.get("FEATURE_DOCX_EXPORT", "True").lower() in ["true", "1", "yes"]
    FEATURE_COLLABORATION = os.environ.get("FEATURE_COLLABORATION", "False").lower() in ["true", "1", "yes"]
    FEATURE_API_ACCESS = os.environ.get("FEATURE_API_ACCESS", "False").lower() in ["true", "1", "yes"]
    FEATURE_REFERRAL_PROGRAM = os.environ.get("FEATURE_REFERRAL_PROGRAM", "False").lower() in ["true", "1", "yes"]
    
    # Métricas optimizadas
    ADMIN_METRICS_ENABLED = True
    SQLALCHEMY_RECORD_QUERIES = False
    
    # Archivos en storage externo
    UPLOAD_FOLDER = "/storage/uploads"
    BOOKS_FOLDER = "/storage/books"
    COVERS_FOLDER = "/storage/covers"
    
    # Dominio de producción
    DOMAIN = os.environ.get("DOMAIN", "buko-ai.com")
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://buko-ai.com")
    API_URL = os.environ.get("API_URL", "https://buko-ai.com/api")
    
    # SSL configuración
    SSL_CERT_PATH = os.environ.get("SSL_CERT_PATH")
    SSL_KEY_PATH = os.environ.get("SSL_KEY_PATH")
    
    @staticmethod
    def init_app(app):
        """Configuración específica para producción"""
        BaseConfig.init_app(app)
        
        # Configurar logging para producción
        import logging
        from logging.handlers import RotatingFileHandler, SMTPHandler
        
        # Crear directorio de logs
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        # File handler para logs
        file_handler = RotatingFileHandler(
            "logs/buko-ai-prod.log",
            maxBytes=10240000,
            backupCount=20
        )
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s"
        ))
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)
        
        # Email handler para errores críticos
        if app.config.get("MAIL_SERVER") and app.config.get("ADMIN_EMAIL"):
            auth = None
            if app.config.get("MAIL_USERNAME") and app.config.get("MAIL_PASSWORD"):
                auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            
            secure = None
            if app.config.get("MAIL_USE_TLS"):
                secure = ()
            
            mail_handler = SMTPHandler(
                mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr=app.config["MAIL_DEFAULT_SENDER"],
                toaddrs=[app.config["ADMIN_EMAIL"]],
                subject="Buko AI Error",
                credentials=auth,
                secure=secure,
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        
        app.logger.setLevel(logging.WARNING)
        app.logger.info("Buko AI Production startup")
        
        # Configurar Sentry para producción
        if app.config.get("SENTRY_DSN"):
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            from sentry_sdk.integrations.celery import CeleryIntegration
            
            sentry_sdk.init(
                dsn=app.config["SENTRY_DSN"],
                integrations=[
                    FlaskIntegration(),
                    SqlalchemyIntegration(),
                    CeleryIntegration(),
                ],
                traces_sample_rate=0.01,
                environment="production",
            )
        
        # Configurar SSL si está disponible
        if app.config.get("SSL_CERT_PATH") and app.config.get("SSL_KEY_PATH"):
            context = (app.config["SSL_CERT_PATH"], app.config["SSL_KEY_PATH"])
            app.run(host="0.0.0.0", port=443, ssl_context=context)