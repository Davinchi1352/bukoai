"""
Configuración para entorno de testing
"""

import os
import tempfile

from .base import BaseConfig


class TestingConfig(BaseConfig):
    """Configuración para testing - optimizada para velocidad y aislamiento"""

    DEBUG = False
    TESTING = True
    
    # Database en memoria para tests
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or "sqlite:///:memory:"
    SQLALCHEMY_ECHO = False
    
    # Debug toolbar deshabilitado
    DEBUG_TB_ENABLED = False
    
    # Email mock
    MAIL_SUPPRESS_SEND = True
    MAIL_DEBUG = False
    
    # Logging silenciado
    LOG_LEVEL = "ERROR"
    
    # Cache simple para tests
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 1
    
    # WebSocket sin logging
    SOCKETIO_LOGGER = False
    SOCKETIO_ENGINEIO_LOGGER = False
    
    # Celery eager para tests síncronos
    CELERY_ALWAYS_EAGER = True
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
    
    # Rate limiting deshabilitado
    RATELIMIT_ENABLED = False
    
    # Pagos mock
    PAYPAL_MODE = "sandbox"
    
    # Seguridad relajada para tests
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SAMESITE = None
    
    # Templates sin cache
    TEMPLATES_AUTO_RELOAD = True
    
    # Testing específico
    EXPLAIN_TEMPLATE_LOADING = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    
    # Features todas habilitadas para testing
    FEATURE_COVER_GENERATION = True
    FEATURE_EPUB_EXPORT = True
    FEATURE_DOCX_EXPORT = True
    FEATURE_COLLABORATION = True
    FEATURE_API_ACCESS = True
    FEATURE_REFERRAL_PROGRAM = True
    
    # Métricas deshabilitadas
    ADMIN_METRICS_ENABLED = False
    SQLALCHEMY_RECORD_QUERIES = False
    
    # Archivos temporales
    UPLOAD_FOLDER = tempfile.mkdtemp()
    BOOKS_FOLDER = tempfile.mkdtemp()
    COVERS_FOLDER = tempfile.mkdtemp()
    
    # URLs para testing
    DOMAIN = "localhost"
    FRONTEND_URL = "http://localhost:5000"
    API_URL = "http://localhost:5000/api"
    
    # Claude AI mock
    ANTHROPIC_API_KEY = "test-api-key"
    
    # Límites reducidos para tests
    FREE_PLAN_BOOKS_LIMIT = 1
    FREE_PLAN_PAGES_LIMIT = 10
    
    # Timeouts reducidos
    MAX_GENERATION_TIME = 30
    QUEUE_DEFAULT_TIMEOUT = 60
    
    # Configuración específica para tests
    SERVER_NAME = "localhost"
    APPLICATION_ROOT = "/"
    PREFERRED_URL_SCHEME = "http"
    
    @staticmethod
    def init_app(app):
        """Configuración específica para testing"""
        BaseConfig.init_app(app)
        
        # Configurar logging mínimo
        import logging
        app.logger.setLevel(logging.ERROR)
        
        # Deshabilitar logging de werkzeug
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        
        # Configurar contexto de aplicación
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        
        # Limpiar archivos temporales al finalizar
        import atexit
        import shutil
        
        def cleanup():
            try:
                shutil.rmtree(app.config["UPLOAD_FOLDER"])
                shutil.rmtree(app.config["BOOKS_FOLDER"])
                shutil.rmtree(app.config["COVERS_FOLDER"])
            except Exception:
                pass
        
        atexit.register(cleanup)