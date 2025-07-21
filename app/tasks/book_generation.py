"""
Tareas de Celery para generación de libros con Claude AI.
Utiliza el servicio Claude actualizado con generación completa y streaming.
"""
import asyncio
import logging
import traceback
import structlog
from datetime import datetime, timezone
from typing import Dict, Any
from celery import Celery, shared_task
from app.models.book_generation import BookGeneration, BookStatus
from app.models.user import User
from app.services.claude_service import get_claude_service
from app.services.email_service import EmailService
from app.utils.logging import log_system_event

# Import WebSocket functions (with conditional import to avoid circular dependencies)
try:
    from app.routes.websocket import emit_book_progress_update, emit_book_completed, emit_book_failed
except ImportError:
    emit_book_progress_update = None
    emit_book_completed = None 
    emit_book_failed = None

logger = structlog.get_logger()
logging_logger = logging.getLogger(__name__)


def get_db():
    """Lazy import de db para evitar circular imports"""
    from app import db
    return db

# Import celery app after initialization to avoid circular imports
def get_celery_app():
    """Get celery instance after app initialization"""
    from app import celery
    return celery

# Define tasks with manual decorator application
def _generate_book_task_impl(self, book_id):
    """
    Tarea principal para generar un libro completo usando Claude AI.
    Utiliza el nuevo método de generación completa con streaming.
    """
    try:
        logger.info("starting_book_generation", book_id=book_id)
        
        # Obtener el libro de la base de datos
        book = BookGeneration.query.get(book_id)
        if not book:
            logger.error("book_not_found", book_id=book_id)
            return {'status': 'error', 'message': 'Libro no encontrado'}
        
        # Actualizar estado y timestamp de inicio
        book.status = BookStatus.PROCESSING
        book.started_at = datetime.now(timezone.utc)
        book.retry_count = 0
        get_db().session.commit()
        
        # Obtener usuario
        user = User.query.get(book.user_id)
        if not user:
            raise Exception("Usuario no encontrado")
        
        # Log del evento
        log_system_event(
            user_id=user.id,
            action="book_generation_started",
            details={"book_id": book_id, "title": book.title}
        )
        
        # Obtener servicio de Claude
        claude_service = get_claude_service()
        
        # Validar parámetros del libro (usar método que construye parámetros completos)
        validated_params = claude_service.validate_book_params(book._build_parameters())
        
        # Estimar tiempo de generación
        estimated_time = claude_service.estimate_generation_time(validated_params)
        
        # Actualizar progreso inicial
        progress_data = {
            'current': 5, 
            'total': 100, 
            'status': 'Iniciando generación con Claude AI...',
            'estimated_time': estimated_time
        }
        # Update state using self if available
        try:
            self.update_state(state='PROGRESS', meta=progress_data)
        except:
            pass
        
        # Emit WebSocket progress update
        if emit_book_progress_update:
            emit_book_progress_update(book_id, progress_data)
        
        # Generar libro completo usando streaming
        # Nota: El streaming se maneja internamente en el servicio Claude
        # con WebSocket events para progreso en tiempo real
        result = asyncio.run(claude_service.generate_book_content_stream(book_id, validated_params))
        
        # Actualizar progreso - generación completada
        progress_data = {
            'current': 85, 
            'total': 100, 
            'status': 'Contenido generado, finalizando...'
        }
        # Update state using self if available
        try:
            self.update_state(state='PROGRESS', meta=progress_data)
        except:
            pass
        
        if emit_book_progress_update:
            emit_book_progress_update(book_id, progress_data)
        
        # Actualizar libro con el contenido generado
        book.content = result['content']
        book.thinking_content = result.get('thinking', '')
        
        # Actualizar estadísticas
        if 'usage' in result:
            usage = result['usage']
            book.prompt_tokens = usage.get('prompt_tokens', 0)
            book.completion_tokens = usage.get('completion_tokens', 0)
            book.thinking_tokens = usage.get('thinking_tokens', 0)
            book.total_tokens = usage.get('total_tokens', 0)
        
        if 'streaming_stats' in result:
            stats = result['streaming_stats']
            book.final_words = stats.get('estimated_words', 0)
            book.final_pages = stats.get('estimated_pages', 0)
        
        # Generar archivos en diferentes formatos
        progress_data = {
            'current': 90, 
            'total': 100, 
            'status': 'Generando archivos de descarga...'
        }
        # Update state using self if available
        try:
            self.update_state(state='PROGRESS', meta=progress_data)
        except:
            pass
        
        if emit_book_progress_update:
            emit_book_progress_update(book_id, progress_data)
        
        # Generar archivos (PDF, EPUB, DOCX)
        file_paths = {}
        try:
            from app.utils.file_generation import generate_pdf, generate_epub, generate_docx
            
            # Generar PDF
            pdf_path = generate_pdf(book)
            if pdf_path:
                file_paths['pdf'] = pdf_path
            
            # Generar EPUB
            epub_path = generate_epub(book)
            if epub_path:
                file_paths['epub'] = epub_path
            
            # Generar DOCX
            docx_path = generate_docx(book)
            if docx_path:
                file_paths['docx'] = docx_path
                
        except ImportError:
            logger.warning("file_generation_modules_not_available", book_id=book_id)
            # Continuar sin archivos si los módulos no están disponibles
            pass
        
        # Actualizar libro con rutas de archivos
        if file_paths:
            book.file_paths = file_paths
        
        # Completar la generación
        book.status = BookStatus.COMPLETED
        book.completed_at = datetime.now(timezone.utc)
        
        # El tiempo de procesamiento se calcula automáticamente como property
        
        get_db().session.commit()
        
        # Progreso final
        progress_data = {
            'current': 98, 
            'total': 100, 
            'status': 'Enviando notificación...'
        }
        # Update state using self if available
        try:
            self.update_state(state='PROGRESS', meta=progress_data)
        except:
            pass
        
        if emit_book_progress_update:
            emit_book_progress_update(book_id, progress_data)
        
        # Log del evento de completado
        log_system_event(
            user_id=user.id,
            action="book_generation_completed",
            details={
                "book_id": book_id,
                "title": book.title,
                "final_pages": book.final_pages,
                "final_words": book.final_words,
                "total_tokens": book.total_tokens,
                "processing_time": book.processing_time
            }
        )
        
        # Enviar notificación por email
        get_celery_app().send_task('app.tasks.book_generation.send_book_completion_email', args=[book_id])
        
        # Completado
        progress_data = {
            'current': 100, 
            'total': 100, 
            'status': '¡Libro generado exitosamente!'
        }
        self.update_state(state='SUCCESS', meta=progress_data)
        
        # Emit final WebSocket updates
        if emit_book_progress_update:
            emit_book_progress_update(book_id, progress_data)
        if emit_book_completed:
            emit_book_completed(book_id)
        
        logger.info("book_generation_completed",
                   book_id=book_id,
                   words=book.final_words,
                   pages=book.final_pages,
                   tokens=book.total_tokens)
        
        return {
            'status': 'completed',
            'book_id': book_id,
            'file_paths': file_paths,
            'stats': {
                'pages': book.final_pages,
                'words': book.final_words,
                'tokens': book.total_tokens,
                'processing_time': book.processing_time
            }
        }
        
    except Exception as exc:
        logger.error("book_generation_failed",
                    book_id=book_id,
                    error=str(exc),
                    traceback=traceback.format_exc())
        
        # Check if it's a temporary error that should be retried
        error_str = str(exc)
        is_temporary_error = any(keyword in error_str.lower() for keyword in [
            'overloaded', 'rate_limit', 'timeout', 'temporary', 'service_unavailable'
        ])
        
        # Actualizar el libro con error
        book = BookGeneration.query.get(book_id)
        if book:
            current_retry_count = getattr(book, 'retry_count', 0)
            max_retries = getattr(book, 'max_retries', 3)
            
            # If it's a temporary error and we haven't exceeded max retries, schedule retry
            if is_temporary_error and current_retry_count < max_retries:
                book.retry_count = current_retry_count + 1
                book.status = BookStatus.QUEUED  # Reset to queued for retry
                book.error_message = f"Error temporal (intento {book.retry_count}/{max_retries}): {str(exc)}"
                get_db().session.commit()
                
                # Schedule retry with exponential backoff (2^retry_count minutes)
                retry_delay = (2 ** current_retry_count) * 60  # seconds
                
                logger.info("book_generation_retry_scheduled",
                           book_id=book_id,
                           retry_count=book.retry_count,
                           retry_delay_minutes=retry_delay/60,
                           error=str(exc))
                
                # Schedule the retry task
                from app import get_celery_app
                get_celery_app().send_task('app.tasks.book_generation.generate_book_task', 
                                         args=[book_id], 
                                         countdown=retry_delay)
                
                # Emit retry notification
                if emit_book_progress_update:
                    emit_book_progress_update(book_id, {
                        'current': 0,
                        'total': 100,
                        'status': 'retrying',
                        'status_message': f'Error temporal. Reintentando en {retry_delay//60} minutos... (intento {book.retry_count}/{max_retries})',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
                
                return  # Don't mark as failed, it will be retried
            
            # If not a temporary error or max retries exceeded, mark as failed
            book.status = BookStatus.FAILED
            book.error_message = str(exc)
            if not is_temporary_error:
                book.retry_count = 0  # Reset for manual retry if needed
            get_db().session.commit()
            
            # Log del error
            log_system_event(
                user_id=book.user_id,
                action="book_generation_failed",
                details={
                    "book_id": book_id,
                    "error": str(exc),
                    "retry_count": book.retry_count,
                    "is_temporary": is_temporary_error,
                    "max_retries_exceeded": is_temporary_error and current_retry_count >= max_retries
                },
                level="ERROR"
            )
            
            # Emit WebSocket failure notification
            if emit_book_failed:
                emit_book_failed(book_id, str(exc))
        
        # Sin reintentos automáticos por ahora
        
        return {'status': 'failed', 'error': str(exc)}


def _send_book_completion_email_impl(self, book_id):
    """
    Envía email de notificación cuando se completa un libro.
    """
    try:
        logger.info("sending_book_completion_email", book_id=book_id)
        
        book = BookGeneration.query.get(book_id)
        if not book or book.status != BookStatus.COMPLETED:
            logger.warning("book_not_completed_for_email", book_id=book_id)
            return
        
        user = User.query.get(book.user_id)
        if not user:
            logger.error("user_not_found_for_email", book_id=book_id)
            return
        
        # Usar servicio de email
        email_service = EmailService()
        
        # Calcular tiempo de procesamiento
        processing_time = "N/A"
        if book.processing_time:
            if book.processing_time < 60:
                processing_time = f"{int(book.processing_time)} segundos"
            elif book.processing_time < 3600:
                minutes = int(book.processing_time // 60)
                processing_time = f"{minutes} minuto{'s' if minutes != 1 else ''}"
            else:
                hours = int(book.processing_time // 3600)
                minutes = int((book.processing_time % 3600) // 60)
                processing_time = f"{hours} hora{'s' if hours != 1 else ''} {minutes} minuto{'s' if minutes != 1 else ''}"
        
        # Preparar datos del email
        email_data = {
            'first_name': user.first_name,
            'book_title': book.title,
            'pages': book.final_pages or 'N/A',
            'words': book.final_words or 'N/A',
            'generation_time': processing_time,
            'download_url': f'/my-books/{book.uuid}'
        }
        
        # Enviar email
        success = email_service.send_template_email(
            to_email=user.email,
            template_name='book_completed',
            **email_data
        )
        
        if success:
            logger.info("book_completion_email_sent",
                       book_id=book_id,
                       user_email=user.email)
        else:
            logger.error("book_completion_email_failed",
                        book_id=book_id,
                        user_email=user.email)
        
        return {'status': 'success' if success else 'failed'}
        
    except Exception as exc:
        logger.error("book_completion_email_error",
                    book_id=book_id,
                    error=str(exc))
        return {'status': 'error', 'error': str(exc)}


def _update_book_generation_stats_impl(self):
    """
    Actualiza estadísticas de generación de libros.
    """
    try:
        from sqlalchemy import func
        
        # Estadísticas por estado
        stats = get_db().session.query(
            BookGeneration.status,
            func.count(BookGeneration.id).label('count')
        ).group_by(BookGeneration.status).all()
        
        # Estadísticas de tokens y costos
        total_stats = get_db().session.query(
            func.sum(BookGeneration.total_tokens).label('total_tokens'),
            func.sum(BookGeneration.estimated_cost).label('total_cost'),
            func.avg(BookGeneration.final_pages).label('avg_pages'),
            func.avg(BookGeneration.final_words).label('avg_words')
        ).filter(BookGeneration.status == BookStatus.COMPLETED).first()
        
        logger.info("book_stats_updated", 
                   status_stats={stat.status.value: stat.count for stat in stats},
                   totals=total_stats)
        
        return {
            'status_stats': {stat.status.value: stat.count for stat in stats},
            'totals': {
                'tokens': int(total_stats.total_tokens or 0),
                'cost': float(total_stats.total_cost or 0),
                'avg_pages': int(total_stats.avg_pages or 0),
                'avg_words': int(total_stats.avg_words or 0)
            }
        }
        
    except Exception as exc:
        logger.error("book_stats_update_failed", error=str(exc))
        return {'error': str(exc)}


# Task wrappers that will be decorated properly
@shared_task(bind=True, name='app.tasks.book_generation.generate_book_task')
def generate_book_task(self, book_id):
    """Wrapper para la tarea principal de generación de libros"""
    return _generate_book_task_impl(self, book_id)


@shared_task(bind=True, name='app.tasks.book_generation.send_book_completion_email')
def send_book_completion_email(self, book_id):
    """Wrapper para la tarea de envío de email"""
    return _send_book_completion_email_impl(self, book_id)


@shared_task(bind=True, name='app.tasks.book_generation.update_book_generation_stats')
def update_book_generation_stats(self):
    """Wrapper para la tarea de actualización de estadísticas"""
    return _update_book_generation_stats_impl(self)