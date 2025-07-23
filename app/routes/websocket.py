"""
WebSocket handlers for real-time communication.
"""

from datetime import datetime, timezone
from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room, disconnect
from celery.result import AsyncResult
import structlog

from app import socketio, celery
from app.models.book_generation import BookGeneration
from app.utils.logging import log_system_event

logger = structlog.get_logger()


@socketio.on('connect')
def handle_connect():
    """
    Handle client connection.
    """
    if not current_user.is_authenticated:
        logger.warning("unauthenticated_websocket_connection", 
                      client_id=request.sid)
        disconnect()
        return False
    
    logger.info("websocket_connected", 
               user_id=current_user.id,
               client_id=request.sid)
    
    # Join user-specific room
    join_room(f"user_{current_user.id}")
    
    emit('connected', {
        'status': 'connected',
        'user_id': current_user.id,
        'message': 'Connected to Buko AI WebSocket'
    })


@socketio.on('disconnect')
def handle_disconnect():
    """
    Handle client disconnection.
    """
    if current_user.is_authenticated:
        logger.info("websocket_disconnected", 
                   user_id=current_user.id,
                   client_id=request.sid)
        
        # Leave user-specific room
        leave_room(f"user_{current_user.id}")


@socketio.on('subscribe_book_progress')
def handle_subscribe_book_progress(data):
    """
    Subscribe to book generation progress updates.
    
    Expected data:
    {
        "book_uuid": "uuid-string"
    }
    """
    logger.info("websocket_subscription_attempt", 
               data=data,
               authenticated=current_user.is_authenticated,
               user_id=getattr(current_user, 'id', None))
    
    if not current_user.is_authenticated:
        logger.warning("websocket_authentication_failed")
        emit('error', {'message': 'Authentication required'})
        return
    
    try:
        book_uuid = data.get('book_uuid')
        logger.info("processing_book_uuid", book_uuid=book_uuid)
        
        if not book_uuid:
            logger.warning("book_uuid_missing")
            emit('error', {'message': 'book_uuid is required'})
            return
        
        # Find the book
        book = BookGeneration.find_by_uuid(book_uuid)
        logger.info("book_lookup_result", 
                   book_found=book is not None,
                   book_id=book.id if book else None)
        
        if not book:
            logger.warning("book_not_found", book_uuid=book_uuid)
            emit('error', {'message': 'Book not found'})
            return
        
        # Check ownership
        if book.user_id != current_user.id:
            logger.warning("access_denied", 
                          book_user_id=book.user_id,
                          current_user_id=current_user.id)
            emit('error', {'message': 'Access denied'})
            return
        
        # Join book-specific room
        room_name = f"book_{book.id}"
        join_room(room_name)
        
        logger.info("subscribed_to_book_progress", 
                   user_id=current_user.id,
                   book_id=book.id,
                   room=room_name)
        
        # Send current progress
        progress_info = book.get_progress_info()
        
        # Only check Celery task status for books that are actively processing
        if hasattr(book, 'task_id') and book.task_id and book.status.value in ['queued', 'processing']:
            try:
                task_result = AsyncResult(book.task_id, app=celery)
                if task_result.state == 'PROGRESS':
                    celery_meta = task_result.info or {}
                    current = celery_meta.get('current', 0)
                    total = celery_meta.get('total', 100)
                    progress_info.update({
                        'current': current,
                        'total': total,
                        'progress': int((current / total) * 100) if total > 0 else 0,
                        'status_message': celery_meta.get('status', 'Processing...')
                    })
                elif task_result.state == 'SUCCESS':
                    # Only report success if the book is actually completed in DB
                    if book.status.value == 'completed':
                        progress_info.update({
                            'current': 100,
                            'total': 100,
                            'progress': 100,
                            'status_message': 'Completed successfully'
                        })
                elif task_result.state == 'FAILURE':
                    progress_info.update({
                        'error': str(task_result.info),
                        'status_message': 'Generation failed'
                    })
            except Exception as task_error:
                logger.warning("celery_task_status_error", 
                             task_id=book.task_id,
                             error=str(task_error))
        
        emit('book_progress', {
            'book_uuid': str(book.uuid),
            'progress': progress_info['progress'],  # Send just the progress number
            'status': progress_info['status'],
            'message': progress_info.get('status_message', progress_info.get('error_message', ''))
        })
        
        emit('subscription_confirmed', {
            'book_uuid': str(book.uuid),
            'room': room_name
        })
        
    except Exception as e:
        logger.error("error_subscribing_to_book_progress", 
                    user_id=getattr(current_user, 'id', None),
                    error=str(e),
                    error_type=type(e).__name__,
                    traceback=str(e))
        emit('error', {'message': 'Failed to subscribe to book progress'})


@socketio.on('unsubscribe_book_progress')
def handle_unsubscribe_book_progress(data):
    """
    Unsubscribe from book generation progress updates.
    
    Expected data:
    {
        "book_uuid": "uuid-string"
    }
    """
    if not current_user.is_authenticated:
        emit('error', {'message': 'Authentication required'})
        return
    
    try:
        book_uuid = data.get('book_uuid')
        if not book_uuid:
            emit('error', {'message': 'book_uuid is required'})
            return
        
        # Find the book
        book = BookGeneration.find_by_uuid(book_uuid)
        if not book:
            emit('error', {'message': 'Book not found'})
            return
        
        # Leave book-specific room
        room_name = f"book_{book.id}"
        leave_room(room_name)
        
        logger.info("unsubscribed_from_book_progress", 
                   user_id=current_user.id,
                   book_id=book.id,
                   room=room_name)
        
        emit('unsubscription_confirmed', {
            'book_uuid': str(book.uuid),
            'room': room_name
        })
        
    except Exception as e:
        logger.error("error_unsubscribing_from_book_progress", 
                    user_id=current_user.id,
                    error=str(e))
        emit('error', {'message': 'Failed to unsubscribe from book progress'})


@socketio.on('get_user_stats')
def handle_get_user_stats():
    """
    Get real-time user statistics.
    """
    if not current_user.is_authenticated:
        emit('error', {'message': 'Authentication required'})
        return
    
    try:
        stats = current_user.get_statistics()
        
        emit('user_stats', {
            'stats': stats,
            'timestamp': stats.get('timestamp')
        })
        
    except Exception as e:
        logger.error("error_getting_user_stats_ws", 
                    user_id=current_user.id,
                    error=str(e))
        emit('error', {'message': 'Failed to retrieve user statistics'})


def emit_book_progress_update(book_id, progress_data):
    """
    Emit book progress update to subscribed clients.
    
    This function is called from Celery tasks to update progress.
    
    Args:
        book_id: Book ID
        progress_data: Progress information
    """
    try:
        room_name = f"book_{book_id}"
        
        # Get book info
        book = BookGeneration.query.get(book_id)
        if not book:
            logger.warning("book_not_found_for_progress_update", book_id=book_id)
            return
        
        # Emit to all clients in the book's room
        socketio.emit('book_progress', {
            'book_id': book_id,
            'book_uuid': str(book.uuid),
            'progress': progress_data
        }, room=room_name)
        
        # Also emit to user's room for dashboard updates
        user_room = f"user_{book.user_id}"
        socketio.emit('book_update', {
            'book_uuid': str(book.uuid),
            'book_id': book.id,
            'title': book.title,
            'progress': progress_data
        }, room=user_room)
        
        logger.info("progress_update_emitted", 
                   book_id=book_id,
                   room=room_name,
                   progress=progress_data.get('current', 0))
        
    except Exception as e:
        logger.error("error_emitting_progress_update", 
                    book_id=book_id,
                    error=str(e))


def emit_thinking_start(book_id):
    """
    Emit thinking start event.
    
    Args:
        book_id: Book ID
    """
    try:
        book = BookGeneration.query.get(book_id)
        if not book:
            return
        
        room_name = f"book_{book_id}"
        socketio.emit('thinking_start', {
            'book_uuid': str(book.uuid),
            'book_id': book.id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }, room=room_name)
        
        logger.info("thinking_start_emitted", book_id=book_id)
        
    except Exception as e:
        logger.error("error_emitting_thinking_start", 
                    book_id=book_id,
                    error=str(e))


def emit_thinking_update(book_id, chunk, stats=None):
    """
    Emit thinking update with chunk of thinking content.
    
    Args:
        book_id: Book ID
        chunk: Thinking content chunk
        stats: Optional stats about thinking content
    """
    try:
        book = BookGeneration.query.get(book_id)
        if not book:
            return
        
        room_name = f"book_{book_id}"
        data = {
            'book_uuid': str(book.uuid),
            'book_id': book.id,
            'chunk': chunk,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        if stats:
            data['stats'] = stats
        
        socketio.emit('thinking_update', data, room=room_name)
        
    except Exception as e:
        logger.error("error_emitting_thinking_update", 
                    book_id=book_id,
                    error=str(e))


def emit_thinking_complete(book_id, total_stats):
    """
    Emit thinking complete event.
    
    Args:
        book_id: Book ID
        total_stats: Total thinking stats
    """
    try:
        book = BookGeneration.query.get(book_id)
        if not book:
            return
        
        room_name = f"book_{book_id}"
        socketio.emit('thinking_complete', {
            'book_uuid': str(book.uuid),
            'book_id': book.id,
            'stats': total_stats,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }, room=room_name)
        
        logger.info("thinking_complete_emitted", 
                   book_id=book_id,
                   stats=total_stats)
        
    except Exception as e:
        logger.error("error_emitting_thinking_complete", 
                    book_id=book_id,
                    error=str(e))


def emit_generation_log(book_id, log_type, message, details=None):
    """
    Emit generation log entry.
    
    Args:
        book_id: Book ID
        log_type: Log type (info, success, warning, error, thinking)
        message: Log message
        details: Optional additional details
    """
    try:
        book = BookGeneration.query.get(book_id)
        if not book:
            return
        
        room_name = f"book_{book_id}"
        data = {
            'book_uuid': str(book.uuid),
            'book_id': book.id,
            'type': log_type,
            'message': message,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        if details:
            data['details'] = details
        
        socketio.emit('generation_log', data, room=room_name)
        
    except Exception as e:
        logger.error("error_emitting_generation_log", 
                    book_id=book_id,
                    error=str(e))


def emit_book_completed(book_id):
    """
    Emit book completion notification.
    
    Args:
        book_id: Book ID
    """
    try:
        book = BookGeneration.query.get(book_id)
        if not book:
            logger.warning("book_not_found_for_completion_notification", book_id=book_id)
            return
        
        completion_data = {
            'book_uuid': str(book.uuid),
            'book_id': book.id,
            'title': book.title,
            'status': book.status.value,
            'final_pages': book.final_pages,
            'final_words': book.final_words,
            'file_formats': book.file_formats,
            'processing_time': book.processing_time,
            'completed_at': book.completed_at.isoformat() if book.completed_at else None,
            'final_stats': {
                'pages': book.final_pages,
                'words': book.final_words,
                'chapters': book.chapter_count or 10
            }
        }
        
        # Emit to book room
        room_name = f"book_{book_id}"
        socketio.emit('book_completed', completion_data, room=room_name)
        
        # Emit to user room
        user_room = f"user_{book.user_id}"
        socketio.emit('book_completed', completion_data, room=user_room)
        
        # Emit general notification
        socketio.emit('notification', {
            'type': 'success',
            'title': 'Book Completed',
            'message': f'Your book "{book.title}" has been generated successfully!',
            'book_uuid': str(book.uuid)
        }, room=user_room)
        
        logger.info("book_completion_notification_sent", 
                   book_id=book_id,
                   user_id=book.user_id)
        
    except Exception as e:
        logger.error("error_emitting_book_completion", 
                    book_id=book_id,
                    error=str(e))


def emit_architecture_ready(book_id, data):
    """
    Emit architecture ready notification for automatic redirection.
    
    Args:
        book_id: Book ID
        data: Architecture data including book_uuid and architecture
    """
    try:
        book = BookGeneration.query.get(book_id)
        if not book:
            logger.warning("book_not_found_for_architecture_notification", book_id=book_id)
            return
        
        architecture_data = {
            'book_uuid': str(book.uuid),
            'book_id': book.id,
            'title': book.title,
            'status': 'architecture_review',
            'architecture': data.get('architecture')
        }
        
        # Emit to book room for automatic redirection
        room_name = f"book_{book_id}"
        socketio.emit('architecture_ready', architecture_data, room=room_name)
        
        # Emit to user room for dashboard updates
        user_room = f"user_{book.user_id}"
        socketio.emit('architecture_ready', architecture_data, room=user_room)
        
        logger.info("architecture_ready_notification_sent", 
                   book_id=book_id,
                   user_id=book.user_id)
        
    except Exception as e:
        logger.error("error_emitting_architecture_ready", 
                    book_id=book_id,
                    error=str(e))


def emit_book_failed(book_id, error_message):
    """
    Emit book generation failure notification.
    
    Args:
        book_id: Book ID
        error_message: Error message
    """
    try:
        book = BookGeneration.query.get(book_id)
        if not book:
            logger.warning("book_not_found_for_failure_notification", book_id=book_id)
            return
        
        failure_data = {
            'book_uuid': str(book.uuid),
            'book_id': book.id,
            'title': book.title,
            'status': book.status.value,
            'error_message': error_message,
            'can_retry': book.can_retry,
            'retry_count': book.retry_count
        }
        
        # Emit to book room
        room_name = f"book_{book_id}"
        socketio.emit('book_failed', failure_data, room=room_name)
        
        # Emit to user room
        user_room = f"user_{book.user_id}"
        socketio.emit('book_failed', failure_data, room=user_room)
        
        # Emit error notification
        socketio.emit('notification', {
            'type': 'error',
            'title': 'Book Generation Failed',
            'message': f'Generation of "{book.title}" failed. {error_message}',
            'book_uuid': str(book.uuid),
            'can_retry': book.can_retry
        }, room=user_room)
        
        logger.info("book_failure_notification_sent", 
                   book_id=book_id,
                   user_id=book.user_id,
                   error=error_message)
        
    except Exception as e:
        logger.error("error_emitting_book_failure", 
                    book_id=book_id,
                    error=str(e))


def emit_system_notification(user_id, notification_data):
    """
    Emit system notification to a specific user.
    
    Args:
        user_id: User ID
        notification_data: Notification data
    """
    try:
        user_room = f"user_{user_id}"
        socketio.emit('notification', notification_data, room=user_room)
        
        logger.info("system_notification_sent", 
                   user_id=user_id,
                   notification_type=notification_data.get('type'))
        
    except Exception as e:
        logger.error("error_emitting_system_notification", 
                    user_id=user_id,
                    error=str(e))


def emit_queue_update(user_id, queue_position):
    """
    Emit queue position update.
    
    Args:
        user_id: User ID
        queue_position: Current position in queue
    """
    try:
        user_room = f"user_{user_id}"
        socketio.emit('queue_update', {
            'queue_position': queue_position,
            'estimated_wait_time': queue_position * 60  # Rough estimate: 1 minute per position
        }, room=user_room)
        
    except Exception as e:
        logger.error("error_emitting_queue_update", 
                    user_id=user_id,
                    error=str(e))