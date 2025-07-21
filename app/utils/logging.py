"""
Utilidades para logging del sistema.
"""
import logging
import traceback
from datetime import datetime
from flask import request, g
from app import db
from app.models.system_log import SystemLog, LogLevel, LogStatus

logger = logging.getLogger(__name__)


def log_system_event(action, details=None, level="INFO", status="SUCCESS", 
                    user_id=None, ip_address=None, user_agent=None, 
                    session_id=None, error_message=None, execution_time=None):
    """
    Registra un evento del sistema en la base de datos.
    
    Args:
        action (str): Descripción de la acción realizada
        details (dict, optional): Detalles adicionales en formato JSON
        level (str): Nivel del log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        status (str): Estado del evento (SUCCESS, ERROR, WARNING)
        user_id (int, optional): ID del usuario asociado
        ip_address (str, optional): Dirección IP del cliente
        user_agent (str, optional): User agent del cliente
        session_id (str, optional): ID de la sesión
        error_message (str, optional): Mensaje de error si aplica
        execution_time (int, optional): Tiempo de ejecución en milisegundos
    """
    try:
        # Obtener información del contexto de request si está disponible
        if not ip_address and request:
            ip_address = get_client_ip()
        
        if not user_agent and request:
            user_agent = request.headers.get('User-Agent')
        
        if not session_id and request:
            session_id = request.cookies.get('session')
        
        if not user_id and hasattr(g, 'current_user') and g.current_user:
            user_id = g.current_user.id
        
        # Crear registro de log
        log_entry = SystemLog(
            user_id=user_id,
            action=action,
            details=details,
            level=LogLevel[level.upper()],
            status=LogStatus[status.upper()],
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            error_message=error_message,
            execution_time=execution_time
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
        # También loggear en el sistema de archivos
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.log(log_level, f"[{action}] {details or ''}")
        
    except Exception as exc:
        # Si falla el logging, al menos registrar en archivo
        logger.error(f"Error registrando evento del sistema: {str(exc)}")
        logger.error(f"Evento original: action={action}, details={details}")


def log_user_action(action, user_id=None, details=None, status="SUCCESS"):
    """
    Registra una acción específica del usuario.
    """
    log_system_event(
        action=f"user_{action}",
        details=details,
        level="INFO",
        status=status,
        user_id=user_id
    )


def log_api_request(endpoint, method, status_code, response_time=None, user_id=None):
    """
    Registra una petición API.
    """
    status = "SUCCESS" if status_code < 400 else "ERROR"
    level = "INFO" if status_code < 400 else "WARNING" if status_code < 500 else "ERROR"
    
    log_system_event(
        action="api_request",
        details={
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time_ms": response_time
        },
        level=level,
        status=status,
        user_id=user_id,
        execution_time=response_time
    )


def log_book_generation_event(event_type, book_id, user_id, details=None, status="SUCCESS"):
    """
    Registra eventos relacionados con generación de libros.
    """
    log_system_event(
        action=f"book_generation_{event_type}",
        details={
            "book_id": book_id,
            **(details or {})
        },
        level="INFO",
        status=status,
        user_id=user_id
    )


def log_payment_event(event_type, payment_id, user_id, amount=None, details=None, status="SUCCESS"):
    """
    Registra eventos relacionados con pagos.
    """
    log_system_event(
        action=f"payment_{event_type}",
        details={
            "payment_id": payment_id,
            "amount": amount,
            **(details or {})
        },
        level="INFO",
        status=status,
        user_id=user_id
    )


def log_error(error, context=None, user_id=None):
    """
    Registra un error del sistema con traceback completo.
    """
    error_details = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
        **(context or {})
    }
    
    log_system_event(
        action="system_error",
        details=error_details,
        level="ERROR",
        status="ERROR",
        user_id=user_id,
        error_message=str(error)
    )


def log_security_event(event_type, details=None, level="WARNING", user_id=None):
    """
    Registra eventos de seguridad.
    """
    log_system_event(
        action=f"security_{event_type}",
        details=details,
        level=level,
        status="WARNING",
        user_id=user_id
    )


def get_client_ip():
    """
    Obtiene la dirección IP real del cliente.
    """
    if not request:
        return None
    
    # Verificar headers de proxy
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    elif request.headers.get('X-Client-IP'):
        return request.headers.get('X-Client-IP')
    else:
        return request.remote_addr


class RequestLoggingMiddleware:
    """
    Middleware para logging automático de requests.
    """
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa el middleware con la app Flask."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown)
    
    def before_request(self):
        """Se ejecuta antes de cada request."""
        g.start_time = datetime.utcnow()
        
        # Log de request entrante
        if request.endpoint and not request.endpoint.startswith('static'):
            log_system_event(
                action="request_start",
                details={
                    "endpoint": request.endpoint,
                    "method": request.method,
                    "url": request.url,
                    "args": dict(request.args),
                    "content_length": request.content_length
                },
                level="DEBUG"
            )
    
    def after_request(self, response):
        """Se ejecuta después de cada request."""
        if hasattr(g, 'start_time') and request.endpoint and not request.endpoint.startswith('static'):
            # Calcular tiempo de respuesta
            response_time = (datetime.utcnow() - g.start_time).total_seconds() * 1000
            
            # Log de respuesta
            log_api_request(
                endpoint=request.endpoint,
                method=request.method,
                status_code=response.status_code,
                response_time=int(response_time),
                user_id=getattr(g, 'current_user_id', None)
            )
        
        return response
    
    def teardown(self, exception):
        """Se ejecuta al final del contexto de request."""
        if exception:
            log_error(
                error=exception,
                context={
                    "endpoint": getattr(request, 'endpoint', None),
                    "method": getattr(request, 'method', None),
                    "url": getattr(request, 'url', None)
                },
                user_id=getattr(g, 'current_user_id', None)
            )


def setup_logging(app):
    """
    Configura el sistema de logging para la aplicación.
    """
    import os
    from logging.handlers import RotatingFileHandler, SMTPHandler
    
    # Configurar nivel de logging
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s [%(name)s] %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # Handler para archivo
    if not app.config.get('LOG_TO_STDOUT'):
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/buko_ai.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
    
    # Handler para consola
    if app.config.get('LOG_TO_STDOUT'):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(log_level)
        app.logger.addHandler(stream_handler)
    
    # Handler para emails en producción
    if not app.debug and app.config.get('MAIL_SERVER'):
        auth = None
        if app.config.get('MAIL_USERNAME') or app.config.get('MAIL_PASSWORD'):
            auth = (app.config.get('MAIL_USERNAME'), app.config.get('MAIL_PASSWORD'))
        
        secure = None
        if app.config.get('MAIL_USE_TLS'):
            secure = ()
        
        mail_handler = SMTPHandler(
            mailhost=(app.config.get('MAIL_SERVER'), app.config.get('MAIL_PORT')),
            fromaddr=app.config.get('MAIL_DEFAULT_SENDER'),
            toaddrs=app.config.get('ADMINS', []),
            subject='Buko AI Error',
            credentials=auth,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        mail_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(mail_handler)
    
    # Configurar nivel del logger principal
    app.logger.setLevel(log_level)
    
    # Configurar loggers de librerías externas
    logging.getLogger('sqlalchemy.engine').setLevel(
        logging.INFO if app.config.get('SQLALCHEMY_ECHO') else logging.WARNING
    )
    logging.getLogger('celery').setLevel(logging.INFO)
    logging.getLogger('redis').setLevel(logging.WARNING)
    
    app.logger.info('Buko AI logging configurado')