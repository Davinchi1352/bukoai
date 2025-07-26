"""
Sistema de logging estructurado para Buko AI.
"""
import json
import logging
import sys
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from flask import request, g, has_request_context
from pythonjsonlogger import jsonlogger
import structlog


class StructuredLogger:
    """
    Logger estructurado que genera logs en formato JSON.
    """
    
    def __init__(self, name: str = __name__):
        self.logger = logging.getLogger(name)
        self._configure_structured_logging()
    
    def _configure_structured_logging(self):
        """Configura el logging estructurado."""
        # Configurar structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    def get_request_context(self) -> Dict[str, Any]:
        """Obtiene el contexto de la petición HTTP actual."""
        context = {}
        
        if has_request_context():
            context.update({
                'request_id': getattr(g, 'request_id', None),
                'user_id': getattr(g, 'current_user_id', None),
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'method': request.method,
                'url': request.url,
                'endpoint': request.endpoint,
                'referrer': request.referrer
            })
        
        return context
    
    def log(self, level: str, message: str, **kwargs):
        """
        Registra un mensaje con contexto estructurado.
        
        Args:
            level: Nivel del log (debug, info, warning, error, critical)
            message: Mensaje principal
            **kwargs: Contexto adicional
        """
        # Combinar contexto de request con kwargs
        context = self.get_request_context()
        context.update(kwargs)
        
        # Obtener logger de structlog
        logger = structlog.get_logger(self.logger.name)
        
        # Registrar mensaje
        getattr(logger, level.lower())(message, **context)
    
    def info(self, message: str, **kwargs):
        """Registra mensaje de información."""
        self.log('info', message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Registra mensaje de debug."""
        self.log('debug', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Registra mensaje de advertencia."""
        self.log('warning', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Registra mensaje de error."""
        self.log('error', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Registra mensaje crítico."""
        self.log('critical', message, **kwargs)
    
    def exception(self, message: str, exc_info=True, **kwargs):
        """Registra una excepción con traceback."""
        if exc_info:
            kwargs['exception'] = traceback.format_exc()
        self.error(message, **kwargs)


class RequestLoggingMiddleware:
    """
    Middleware para logging automático de requests con contexto estructurado.
    """
    
    def __init__(self, app=None):
        self.logger = StructuredLogger('request_middleware')
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa el middleware con la aplicación Flask."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown)
    
    def before_request(self):
        """Se ejecuta antes de cada request."""
        import uuid
        
        # Generar ID único para la request
        g.request_id = str(uuid.uuid4())
        g.start_time = datetime.utcnow()
        
        # Obtener usuario actual si está autenticado
        if hasattr(g, 'current_user') and g.current_user and g.current_user.is_authenticated:
            g.current_user_id = g.current_user.id
        
        # Log de inicio de request
        if request.endpoint and not request.endpoint.startswith('static'):
            self.logger.info(
                "Request started",
                event_type="request_start",
                content_length=request.content_length,
                args=dict(request.args),
                form_data=self._sanitize_form_data(request.form)
            )
    
    def after_request(self, response):
        """Se ejecuta después de cada request."""
        if hasattr(g, 'start_time') and request.endpoint and not request.endpoint.startswith('static'):
            # Calcular tiempo de respuesta
            duration = (datetime.utcnow() - g.start_time).total_seconds()
            
            # Log de finalización de request
            self.logger.info(
                "Request completed",
                event_type="request_end",
                status_code=response.status_code,
                response_size=response.content_length,
                duration_seconds=duration,
                cache_control=response.cache_control.to_header() if response.cache_control else None
            )
        
        return response
    
    def teardown(self, exception):
        """Se ejecuta al final del contexto de request."""
        if exception:
            self.logger.exception(
                "Request failed with exception",
                event_type="request_exception",
                exception_type=type(exception).__name__
            )
    
    def _sanitize_form_data(self, form_data):
        """Sanitiza datos de formulario para logging seguro."""
        sensitive_fields = ['password', 'passwd', 'secret', 'token', 'key', 'api_key']
        sanitized = {}
        
        for key, value in form_data.items():
            if any(field in key.lower() for field in sensitive_fields):
                sanitized[key] = '***REDACTED***'
            else:
                sanitized[key] = value
        
        return sanitized


class PerformanceLogger:
    """
    Logger especializado para métricas de performance.
    """
    
    def __init__(self):
        self.logger = StructuredLogger('performance')
    
    def log_database_query(self, query: str, duration: float, rows_affected: int = None):
        """Registra métricas de consultas de base de datos."""
        self.logger.info(
            "Database query executed",
            event_type="db_query",
            query_preview=query[:100] + "..." if len(query) > 100 else query,
            duration_seconds=duration,
            rows_affected=rows_affected,
            slow_query=duration > 1.0  # Marcar consultas lentas
        )
    
    def log_cache_operation(self, operation: str, key: str, hit: bool = None, duration: float = None):
        """Registra operaciones de cache."""
        self.logger.info(
            f"Cache {operation}",
            event_type="cache_operation",
            operation=operation,
            cache_key=key,
            cache_hit=hit,
            duration_seconds=duration
        )
    
    def log_external_api_call(self, service: str, endpoint: str, method: str, 
                             status_code: int, duration: float, retries: int = 0):
        """Registra llamadas a APIs externas."""
        self.logger.info(
            f"External API call to {service}",
            event_type="external_api",
            service=service,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            duration_seconds=duration,
            retries=retries,
            success=200 <= status_code < 300
        )
    
    def log_celery_task(self, task_name: str, task_id: str, status: str, 
                       duration: float = None, retries: int = 0):
        """Registra ejecución de tareas de Celery."""
        self.logger.info(
            f"Celery task {status}",
            event_type="celery_task",
            task_name=task_name,
            task_id=task_id,
            status=status,
            duration_seconds=duration,
            retries=retries
        )


class SecurityLogger:
    """
    Logger especializado para eventos de seguridad.
    """
    
    def __init__(self):
        self.logger = StructuredLogger('security')
    
    def log_authentication_attempt(self, email: str, success: bool, 
                                  failure_reason: str = None, ip_address: str = None):
        """Registra intentos de autenticación."""
        self.logger.info(
            "Authentication attempt",
            event_type="auth_attempt",
            email=email,
            success=success,
            failure_reason=failure_reason,
            ip_address=ip_address or (request.remote_addr if has_request_context() else None)
        )
    
    def log_authorization_failure(self, user_id: int, resource: str, action: str):
        """Registra fallos de autorización."""
        self.logger.warning(
            "Authorization denied",
            event_type="auth_denied",
            user_id=user_id,
            resource=resource,
            action=action
        )
    
    def log_suspicious_activity(self, activity_type: str, user_id: int = None, 
                               ip_address: str = None, details: Dict[str, Any] = None):
        """Registra actividad sospechosa."""
        self.logger.warning(
            f"Suspicious activity detected: {activity_type}",
            event_type="suspicious_activity",
            activity_type=activity_type,
            user_id=user_id,
            ip_address=ip_address,
            details=details or {}
        )
    
    def log_rate_limit_exceeded(self, ip_address: str, endpoint: str, limit: str):
        """Registra cuando se exceden límites de rate limiting."""
        self.logger.warning(
            "Rate limit exceeded",
            event_type="rate_limit_exceeded",
            ip_address=ip_address,
            endpoint=endpoint,
            limit=limit
        )


class BookGenerationMonitor:
    """
    Monitor especializado para generación de libros con 10K usuarios.
    Proporciona métricas detalladas de rendimiento y salud del sistema.
    """
    
    def __init__(self):
        self.logger = StructuredLogger('book_monitor')
        self.start_times = {}  # Track start times por book_id
    
    def start_generation_tracking(self, book_id: int, user_id: int, generation_type: str, params: dict):
        """Inicia tracking de una generación de libro."""
        import time
        self.start_times[book_id] = time.time()
        
        self.logger.info(
            f"Started {generation_type} generation tracking",
            event_type="generation_start",
            book_id=book_id,
            user_id=user_id,
            generation_type=generation_type,
            target_pages=params.get('page_count', 0),
            target_chapters=params.get('chapter_count', 0),
            language=params.get('language', 'unknown'),
            genre=params.get('genre', 'unknown'),
            model_config={
                'max_tokens': params.get('max_tokens', 0),
                'thinking_budget': params.get('thinking_budget', 0)
            }
        )
    
    def log_chunk_progress(self, book_id: int, chunk_num: int, total_chunks: int, 
                          chunk_pages: int, tokens_used: int, duration: float):
        """Registra progreso de un chunk individual."""
        progress_pct = (chunk_num / total_chunks) * 100 if total_chunks > 0 else 0
        
        self.logger.info(
            f"Chunk {chunk_num}/{total_chunks} completed",
            event_type="chunk_progress",
            book_id=book_id,
            chunk_number=chunk_num,
            total_chunks=total_chunks,
            progress_percentage=round(progress_pct, 1),
            chunk_pages=chunk_pages,
            tokens_used=tokens_used,
            chunk_duration_seconds=duration,
            tokens_per_second=round(tokens_used / duration, 2) if duration > 0 else 0,
            pages_per_minute=round((chunk_pages * 60) / duration, 2) if duration > 0 else 0
        )
    
    def log_claude_api_metrics(self, book_id: int, operation: str, response_time: float, 
                              tokens_consumed: int, status: str, model: str):
        """Registra métricas de llamadas a Claude API."""
        self.logger.info(
            f"Claude API {operation} - {status}",
            event_type="claude_api_metrics",
            book_id=book_id,
            operation=operation,
            response_time_seconds=response_time,
            tokens_consumed=tokens_consumed,
            status=status,
            model=model,
            tokens_per_second=round(tokens_consumed / response_time, 2) if response_time > 0 else 0,
            is_slow_response=response_time > 30.0,  # Flag slow responses
            is_high_token_usage=tokens_consumed > 50000  # Flag high token usage
        )
    
    def log_queue_metrics(self, queue_name: str, depth: int, active_workers: int, 
                         processing_rate: float, avg_wait_time: float):
        """Registra métricas de colas para 10K usuarios."""
        self.logger.info(
            f"Queue metrics for {queue_name}",
            event_type="queue_metrics",
            queue_name=queue_name,
            queue_depth=depth,
            active_workers=active_workers,
            processing_rate_per_minute=processing_rate,
            avg_wait_time_minutes=avg_wait_time,
            is_backlogged=depth > (active_workers * 5),  # Alert if queue is backing up
            saturation_level=round((depth / max(active_workers * 10, 1)) * 100, 1)  # Queue saturation %
        )
    
    def log_user_experience_metrics(self, book_id: int, user_id: int, experience_type: str, 
                                   value: float, threshold: float = None):
        """Registra métricas de experiencia de usuario."""
        is_degraded = threshold and value > threshold
        
        self.logger.info(
            f"User experience metric: {experience_type}",
            event_type="user_experience",
            book_id=book_id,
            user_id=user_id,
            metric_type=experience_type,
            value=value,
            threshold=threshold,
            is_degraded=is_degraded,
            user_impact_level="high" if is_degraded else "normal"
        )
    
    def complete_generation_tracking(self, book_id: int, user_id: int, status: str, 
                                   final_pages: int, final_words: int, total_tokens: int, 
                                   error_message: str = None):
        """Completa tracking de generación y calcula métricas finales."""
        import time
        
        total_duration = 0
        if book_id in self.start_times:
            total_duration = time.time() - self.start_times[book_id]
            del self.start_times[book_id]
        
        # Calcular métricas de eficiencia
        words_per_minute = (final_words * 60) / total_duration if total_duration > 0 else 0
        pages_per_hour = (final_pages * 3600) / total_duration if total_duration > 0 else 0
        tokens_per_second = total_tokens / total_duration if total_duration > 0 else 0
        
        self.logger.info(
            f"Generation completed with status: {status}",
            event_type="generation_complete",
            book_id=book_id,
            user_id=user_id,
            status=status,
            total_duration_seconds=total_duration,
            total_duration_minutes=round(total_duration / 60, 1),
            final_pages=final_pages,
            final_words=final_words,
            total_tokens=total_tokens,
            efficiency_metrics={
                'words_per_minute': round(words_per_minute, 1),
                'pages_per_hour': round(pages_per_hour, 1),
                'tokens_per_second': round(tokens_per_second, 1)
            },
            quality_indicators={
                'words_per_page': round(final_words / final_pages, 0) if final_pages > 0 else 0,
                'completion_rate': 100.0 if status == 'completed' else 0.0
            },
            error_message=error_message,
            is_successful=status == 'completed',
            performance_tier=self._classify_performance(total_duration, final_pages)
        )
    
    def _classify_performance(self, duration: float, pages: int) -> str:
        """Clasifica el rendimiento de la generación."""
        if duration == 0 or pages == 0:
            return 'unknown'
        
        minutes_per_page = (duration / 60) / pages
        
        if minutes_per_page < 2:
            return 'excellent'
        elif minutes_per_page < 4:
            return 'good'
        elif minutes_per_page < 8:
            return 'acceptable'
        else:
            return 'poor'
    
    def log_system_health(self, cpu_percent: float, memory_percent: float, 
                         disk_usage_percent: float, active_connections: int):
        """Registra métricas de salud del sistema."""
        self.logger.info(
            "System health check",
            event_type="system_health",
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_usage_percent=disk_usage_percent,
            active_connections=active_connections,
            is_cpu_stressed=cpu_percent > 80,
            is_memory_stressed=memory_percent > 80,
            is_disk_stressed=disk_usage_percent > 85,
            overall_health="healthy" if all([
                cpu_percent < 80,
                memory_percent < 80,
                disk_usage_percent < 85
            ]) else "stressed"
        )


class BusinessLogger:
    """
    Logger especializado para eventos de negocio.
    """
    
    def __init__(self):
        self.logger = StructuredLogger('business')
    
    def log_user_registration(self, user_id: int, email: str, subscription_type: str):
        """Registra registro de usuario."""
        self.logger.info(
            "User registered",
            event_type="user_registration",
            user_id=user_id,
            email=email,
            subscription_type=subscription_type
        )
    
    def log_book_generation_started(self, user_id: int, book_id: int, 
                                   title: str, parameters: Dict[str, Any]):
        """Registra inicio de generación de libro."""
        self.logger.info(
            "Book generation started",
            event_type="book_generation_start",
            user_id=user_id,
            book_id=book_id,
            title=title,
            parameters=parameters
        )
    
    def log_book_generation_completed(self, user_id: int, book_id: int, 
                                    duration: float, tokens_used: int, cost: float):
        """Registra finalización de generación de libro."""
        self.logger.info(
            "Book generation completed",
            event_type="book_generation_complete",
            user_id=user_id,
            book_id=book_id,
            duration_seconds=duration,
            tokens_used=tokens_used,
            cost_usd=cost
        )
    
    def log_subscription_change(self, user_id: int, old_plan: str, new_plan: str, 
                               payment_method: str = None):
        """Registra cambio de suscripción."""
        self.logger.info(
            "Subscription changed",
            event_type="subscription_change",
            user_id=user_id,
            old_plan=old_plan,
            new_plan=new_plan,
            payment_method=payment_method
        )
    
    def log_payment_processed(self, user_id: int, payment_id: int, 
                             amount: float, currency: str, status: str):
        """Registra procesamiento de pago."""
        self.logger.info(
            "Payment processed",
            event_type="payment_processed",
            user_id=user_id,
            payment_id=payment_id,
            amount=amount,
            currency=currency,
            status=status
        )


# Instancias globales de loggers especializados
performance_logger = PerformanceLogger()
security_logger = SecurityLogger()
business_logger = BusinessLogger()
book_generation_monitor = BookGenerationMonitor()

# Logger estructurado principal
structured_logger = StructuredLogger('buko_ai')

# Funciones de conveniencia para monitoreo
def track_book_generation_start(book_id: int, user_id: int, generation_type: str, params: dict):
    """Inicia tracking de generación de libro."""
    book_generation_monitor.start_generation_tracking(book_id, user_id, generation_type, params)

def track_chunk_progress(book_id: int, chunk_num: int, total_chunks: int, 
                        chunk_pages: int, tokens_used: int, duration: float):
    """Registra progreso de chunk."""
    book_generation_monitor.log_chunk_progress(book_id, chunk_num, total_chunks, 
                                             chunk_pages, tokens_used, duration)

def track_claude_api_call(book_id: int, operation: str, response_time: float,
                         tokens_consumed: int, status: str, model: str):
    """Registra llamada a Claude API."""
    book_generation_monitor.log_claude_api_metrics(book_id, operation, response_time,
                                                  tokens_consumed, status, model)

def track_generation_complete(book_id: int, user_id: int, status: str,
                             final_pages: int, final_words: int, total_tokens: int,
                             error_message: str = None):
    """Completa tracking de generación."""
    book_generation_monitor.complete_generation_tracking(book_id, user_id, status,
                                                        final_pages, final_words, 
                                                        total_tokens, error_message)