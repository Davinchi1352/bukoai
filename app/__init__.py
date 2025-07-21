"""
Inicializaci�n de la aplicaci�n Flask para Buko AI.
"""
import logging
import os
import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
from flask_caching import Cache
from celery import Celery

# Extensiones globales
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
cors = CORS()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"]
)
socketio = SocketIO()
cache = Cache()
celery = None  # Will be initialized by create_celery_app


def create_celery_app(app=None):
    """
    Crea y configura la instancia de Celery.
    """
    app = app or create_app()
    
    # Create a new Celery instance
    celery_app = Celery(app.import_name, include=[
        'app.tasks.book_generation',
        'app.tasks.email_tasks'
    ])
    
    # Configuraci�n de Celery
    celery_app.conf.update(
        broker_url=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        result_backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        # Configuraci�n de rutas de tareas
        task_routes={
            'app.tasks.book_generation.*': {'queue': 'book_generation'},
            'app.tasks.email_tasks.*': {'queue': 'email'}
        },
        # Configuraci�n de trabajadores
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        worker_max_tasks_per_child=1000,
        # Configuraci�n de resultados
        result_expires=3600,
        # Configuraci�n de retry
        task_soft_time_limit=300,  # 5 minutos
        task_time_limit=600,       # 10 minutos
        task_max_retries=3,
        task_default_retry_delay=60,
        # Configuraci�n de beat para tareas programadas
        beat_schedule={
            # Cleanup tasks will be added when the modules are created
        }
    )
    
    # Contexto de aplicaci�n para tareas
    class ContextTask(celery_app.Task):
        """Contexto de aplicaci�n Flask para tareas de Celery."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery_app.Task = ContextTask
    
    # Configurar autodiscovery para encontrar tareas con @shared_task
    celery_app.autodiscover_tasks(['app.tasks'])
    
    # Registrar tareas después de configurar Celery
    from app.tasks import register_tasks
    register_tasks(celery_app)
    
    # Set the global celery instance in this module
    globals()['celery'] = celery_app
    
    return celery_app


def create_app(config_name=None):
    """
    Factory para crear la aplicaci�n Flask.
    """
    app = Flask(__name__)
    
    # Configuraci�n
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    if config_name == 'development':
        from config.development import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    elif config_name == 'staging':
        from config.staging import StagingConfig
        app.config.from_object(StagingConfig)
    elif config_name == 'production':
        from config.production import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        from config.development import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    cors.init_app(app)
    limiter.init_app(app)
    socketio.init_app(app, 
                     cors_allowed_origins="*",
                     async_mode='threading',  # Forzar threading mode sin eventlet
                     logger=app.config.get('SOCKETIO_LOGGER', True),
                     engineio_logger=app.config.get('SOCKETIO_ENGINEIO_LOGGER', True))
    cache.init_app(app)
    
    # Configurar Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesi�n para acceder a esta p�gina.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Registrar blueprints
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.routes.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register real API blueprints for dashboard
    from app.routes.api_real import bp as api_real_bp
    app.register_blueprint(api_real_bp, url_prefix='/api')
    
    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    from app.routes.books import bp as books_bp
    app.register_blueprint(books_bp, url_prefix='/books')
    
    # Import WebSocket handlers (this registers the socket events)
    from app.routes import websocket
    
    # Configurar sistema de logging avanzado
    from app.utils.log_config import LogConfig
    from app.utils.structured_logging import RequestLoggingMiddleware
    from app.utils.cache_manager import init_cache_system
    
    # Configurar logging estructurado
    LogConfig.setup_logging(app)
    
    # Inicializar middleware de logging
    request_logging = RequestLoggingMiddleware(app)
    
    # Configurar Redis y sistema de cache
    redis_url = app.config.get('REDIS_URL', 'redis://localhost:6380/0')
    redis_client = redis.from_url(redis_url, decode_responses=True)
    
    # Inicializar sistema de cache avanzado
    cache_manager = init_cache_system(app, redis_client)
    
    # Inicializar servicios de cache especializados
    from app.services.cache_service import CacheWarmupService
    from app.services.email_service import email_service
    
    # Pre-calentar cache global al iniciar
    try:
        CacheWarmupService.warmup_global_cache()
    except Exception as e:
        app.logger.warning(f"Cache warmup failed: {str(e)}")
    
    # Inicializar servicio de email
    email_service.init_app(app)
    
    app.logger.info('Buko AI startup - Logging, Cache, Email y Servicios configurados correctamente')
    
    # Initialize Celery if not already done
    global celery
    if celery is None:
        celery = create_celery_app(app)
    
    return app


# Importar modelos para que est�n disponibles para las migraciones
from app.models import *

# Inicializar Celery automáticamente para que esté disponible cuando se importa el módulo
try:
    _app = create_app()
    celery = create_celery_app(_app)
    
    # Importar tareas para que se registren con @shared_task
    from app.tasks import book_generation, email_tasks
    # Importar payment_tasks y cleanup_tasks si existen
    try:
        from app.tasks import payment_tasks
    except ImportError:
        pass
    try:
        from app.tasks import cleanup_tasks
    except ImportError:
        pass
    
    # Asegurar que las tareas estén disponibles
    globals()['celery'] = celery
    
except Exception as e:
    # Si hay error en inicialización, mantener celery como None
    import logging
    logging.warning(f"Error initializing Celery in app module: {e}")
    celery = None