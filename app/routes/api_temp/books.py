"""
API routes for book generation and management.
"""

import os
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from celery.result import AsyncResult
from sqlalchemy.exc import SQLAlchemyError
import structlog

from app import db, celery
from app.models.book_generation import BookGeneration, BookStatus
from app.models.system_log import BookDownload
from app.tasks.book_generation import generate_book_task
from app.utils.logging import log_system_event
from app.utils.validators import validate_book_parameters

logger = structlog.get_logger()

# Create blueprint
bp = Blueprint('books_api', __name__, url_prefix='/api/books')


@bp.route('/', methods=['POST'])
@login_required
def create_book():
    """
    Create a new book generation request.
    
    Expected JSON payload:
    {
        "title": "Book Title",
        "genre": "Fiction",
        "target_audience": "Adults",
        "tone": "Casual",
        "key_topics": "Adventure, friendship",
        "chapter_count": 10,
        "page_count": 50,
        "format_size": "A4",
        "language": "es",
        "additional_instructions": "Optional instructions",
        "include_toc": true,
        "include_introduction": true,
        "include_conclusion": true,
        "writing_style": "Narrative"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('title'):
            return jsonify({
                'error': 'Title is required'
            }), 400
        
        # Validate book parameters
        validation_result = validate_book_parameters(data)
        if not validation_result['valid']:
            return jsonify({
                'error': 'Invalid parameters',
                'details': validation_result['errors']
            }), 400
        
        # Check user's book generation limits
        if not current_user.can_generate_book():
            return jsonify({
                'error': 'Book generation limit reached for your subscription',
                'limit': current_user.get_book_generation_limit(),
                'used': current_user.books_generated_this_month
            }), 429
        
        # Create book generation record
        book = BookGeneration(
            user_id=current_user.id,
            title=data.get('title'),
            genre=data.get('genre'),
            target_audience=data.get('target_audience'),
            tone=data.get('tone'),
            key_topics=data.get('key_topics'),
            chapter_count=data.get('chapter_count', 10),
            page_count=data.get('page_count', 50),
            format_size=data.get('format_size', 'A4'),
            language=data.get('language', 'es'),
            additional_instructions=data.get('additional_instructions'),
            include_toc=data.get('include_toc', True),
            include_introduction=data.get('include_introduction', True),
            include_conclusion=data.get('include_conclusion', True),
            writing_style=data.get('writing_style'),
            status=BookStatus.QUEUED
        )
        
        # Save to database
        book.save()
        
        # Update user's monthly usage
        current_user.increment_books_generated()
        
        # Queue the book generation task
        task = generate_book_task.delay(book.id)
        
        # Update book with task ID
        book.task_id = task.id
        book.save()
        
        # Log the event
        log_system_event(
            user_id=current_user.id,
            action="book_generation_requested",
            details={
                "book_id": book.id,
                "title": book.title,
                "task_id": task.id
            }
        )
        
        logger.info("book_generation_requested", 
                   book_id=book.id, 
                   user_id=current_user.id,
                   task_id=task.id)
        
        return jsonify({
            'book_id': book.id,
            'uuid': str(book.uuid),
            'task_id': task.id,
            'status': book.status.value,
            'message': 'Book generation started successfully'
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error("database_error_creating_book", error=str(e))
        return jsonify({'error': 'Database error occurred'}), 500
        
    except Exception as e:
        logger.error("unexpected_error_creating_book", error=str(e))
        return jsonify({'error': 'An unexpected error occurred'}), 500


@bp.route('/', methods=['GET'])
@login_required
def list_books():
    """
    Get all books for the current user.
    
    Query parameters:
    - status: Filter by status (optional)
    - limit: Number of books to return (default: 20)
    - offset: Number of books to skip (default: 0)
    """
    try:
        # Get query parameters
        status = request.args.get('status')
        limit = min(int(request.args.get('limit', 20)), 100)  # Max 100
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = BookGeneration.query.filter_by(user_id=current_user.id)
        
        if status:
            try:
                status_enum = BookStatus(status)
                query = query.filter_by(status=status_enum)
            except ValueError:
                return jsonify({'error': f'Invalid status: {status}'}), 400
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        books = query.order_by(BookGeneration.created_at.desc())\
                    .offset(offset)\
                    .limit(limit)\
                    .all()
        
        # Convert to dict
        books_data = []
        for book in books:
            book_dict = book.to_dict()
            # Add progress info for non-completed books
            if not book.is_completed:
                book_dict['progress'] = book.get_progress_info()
            books_data.append(book_dict)
        
        return jsonify({
            'books': books_data,
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total
        })
        
    except Exception as e:
        logger.error("error_listing_books", user_id=current_user.id, error=str(e))
        return jsonify({'error': 'Failed to retrieve books'}), 500


@bp.route('/<uuid:book_uuid>', methods=['GET'])
@login_required
def get_book(book_uuid):
    """
    Get a specific book by UUID.
    """
    try:
        book = BookGeneration.find_by_uuid(book_uuid)
        
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        # Check ownership
        if book.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        book_dict = book.to_dict()
        
        # Add progress info for non-completed books
        if not book.is_completed:
            book_dict['progress'] = book.get_progress_info()
        
        return jsonify(book_dict)
        
    except Exception as e:
        logger.error("error_getting_book", book_uuid=str(book_uuid), error=str(e))
        return jsonify({'error': 'Failed to retrieve book'}), 500


@bp.route('/<uuid:book_uuid>/progress', methods=['GET'])
@login_required
def get_book_progress(book_uuid):
    """
    Get real-time progress for a book generation.
    """
    try:
        book = BookGeneration.find_by_uuid(book_uuid)
        
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        # Check ownership
        if book.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        progress_info = book.get_progress_info()
        
        # If book has a task ID, get Celery task status
        if hasattr(book, 'task_id') and book.task_id:
            try:
                task_result = AsyncResult(book.task_id, app=celery)
                if task_result.state == 'PROGRESS':
                    # Update progress with Celery task info
                    celery_meta = task_result.info or {}
                    progress_info.update({
                        'current': celery_meta.get('current', 0),
                        'total': celery_meta.get('total', 100),
                        'status_message': celery_meta.get('status', 'Processing...')
                    })
                elif task_result.state == 'SUCCESS':
                    progress_info.update({
                        'current': 100,
                        'total': 100,
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
        
        return jsonify(progress_info)
        
    except Exception as e:
        logger.error("error_getting_progress", book_uuid=str(book_uuid), error=str(e))
        return jsonify({'error': 'Failed to retrieve progress'}), 500


@bp.route('/<uuid:book_uuid>/cancel', methods=['POST'])
@login_required
def cancel_book(book_uuid):
    """
    Cancel a book generation in progress.
    """
    try:
        book = BookGeneration.find_by_uuid(book_uuid)
        
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        # Check ownership
        if book.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if book can be cancelled
        if book.status not in [BookStatus.QUEUED, BookStatus.PROCESSING]:
            return jsonify({
                'error': f'Cannot cancel book with status: {book.status.value}'
            }), 400
        
        # Cancel Celery task if exists
        if hasattr(book, 'task_id') and book.task_id:
            try:
                celery.control.revoke(book.task_id, terminate=True)
            except Exception as task_error:
                logger.warning("celery_task_cancel_error", 
                             task_id=book.task_id, 
                             error=str(task_error))
        
        # Update book status
        book.cancel_generation()
        
        # Log the event
        log_system_event(
            user_id=current_user.id,
            action="book_generation_cancelled",
            details={"book_id": book.id, "title": book.title}
        )
        
        logger.info("book_generation_cancelled", 
                   book_id=book.id, 
                   user_id=current_user.id)
        
        return jsonify({
            'message': 'Book generation cancelled successfully',
            'status': book.status.value
        })
        
    except Exception as e:
        logger.error("error_cancelling_book", book_uuid=str(book_uuid), error=str(e))
        return jsonify({'error': 'Failed to cancel book generation'}), 500


@bp.route('/<uuid:book_uuid>/retry', methods=['POST'])
@login_required
def retry_book(book_uuid):
    """
    Retry a failed book generation.
    """
    try:
        book = BookGeneration.find_by_uuid(book_uuid)
        
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        # Check ownership
        if book.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if book can be retried
        if not book.can_retry:
            return jsonify({
                'error': 'Book cannot be retried',
                'reason': f'Status: {book.status.value}, Retries: {book.retry_count}/{book.max_retries}'
            }), 400
        
        # Check user's book generation limits
        if not current_user.can_generate_book():
            return jsonify({
                'error': 'Book generation limit reached for your subscription',
                'limit': current_user.get_book_generation_limit(),
                'used': current_user.books_generated_this_month
            }), 429
        
        # Retry the generation
        book.retry_generation()
        
        # Queue new task
        task = generate_book_task.delay(book.id)
        book.task_id = task.id
        book.save()
        
        # Update user's monthly usage
        current_user.increment_books_generated()
        
        # Log the event
        log_system_event(
            user_id=current_user.id,
            action="book_generation_retried",
            details={
                "book_id": book.id,
                "title": book.title,
                "retry_count": book.retry_count,
                "task_id": task.id
            }
        )
        
        logger.info("book_generation_retried", 
                   book_id=book.id, 
                   retry_count=book.retry_count,
                   task_id=task.id)
        
        return jsonify({
            'message': 'Book generation restarted successfully',
            'task_id': task.id,
            'status': book.status.value,
            'retry_count': book.retry_count
        })
        
    except Exception as e:
        logger.error("error_retrying_book", book_uuid=str(book_uuid), error=str(e))
        return jsonify({'error': 'Failed to retry book generation'}), 500


@bp.route('/<uuid:book_uuid>/download/<format_type>', methods=['GET'])
@login_required
def download_book(book_uuid, format_type):
    """
    Download a book in the specified format.
    
    Supported formats: pdf, epub, docx, txt
    """
    try:
        book = BookGeneration.find_by_uuid(book_uuid)
        
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        # Check ownership
        if book.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if book is completed
        if not book.is_completed:
            return jsonify({
                'error': 'Book is not ready for download',
                'status': book.status.value
            }), 400
        
        # Validate format
        if format_type not in ['pdf', 'epub', 'docx', 'txt']:
            return jsonify({'error': f'Unsupported format: {format_type}'}), 400
        
        # Get file path
        file_path = book.get_file_path(format_type)
        
        if not file_path or not os.path.exists(file_path):
            # Try to generate the file if it doesn't exist
            if format_type == 'txt':
                from app.utils.file_generation import generate_txt
                file_path = generate_txt(book)
            else:
                return jsonify({
                    'error': f'{format_type.upper()} file not available',
                    'available_formats': book.file_formats
                }), 404
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({
                'error': f'Failed to generate {format_type.upper()} file'
            }), 500
        
        # Log the download
        download = BookDownload(
            book_id=book.id,
            user_id=current_user.id,
            format_type=format_type,
            file_size=os.path.getsize(file_path)
        )
        download.save()
        
        # Log the event
        log_system_event(
            user_id=current_user.id,
            action="book_downloaded",
            details={
                "book_id": book.id,
                "title": book.title,
                "format": format_type,
                "file_size": os.path.getsize(file_path)
            }
        )
        
        logger.info("book_downloaded", 
                   book_id=book.id,
                   user_id=current_user.id,
                   format=format_type)
        
        # Send file
        filename = f"{book.title}.{format_type}"
        # Clean filename for download
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype=_get_mimetype(format_type)
        )
        
    except Exception as e:
        logger.error("error_downloading_book", 
                    book_uuid=str(book_uuid), 
                    format=format_type,
                    error=str(e))
        return jsonify({'error': 'Failed to download book'}), 500


@bp.route('/<uuid:book_uuid>', methods=['DELETE'])
@login_required
def delete_book(book_uuid):
    """
    Delete a book and its associated files.
    """
    try:
        book = BookGeneration.find_by_uuid(book_uuid)
        
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        # Check ownership
        if book.user_id != current_user.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Cancel task if still running
        if book.status in [BookStatus.QUEUED, BookStatus.PROCESSING]:
            if hasattr(book, 'task_id') and book.task_id:
                try:
                    celery.control.revoke(book.task_id, terminate=True)
                except Exception:
                    pass  # Task might not exist
        
        # Delete associated files
        if book.file_paths:
            for format_type, file_path in book.file_paths.items():
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as file_error:
                    logger.warning("file_deletion_error", 
                                 file_path=file_path, 
                                 error=str(file_error))
        
        # Log the event before deletion
        log_system_event(
            user_id=current_user.id,
            action="book_deleted",
            details={
                "book_id": book.id,
                "title": book.title,
                "status": book.status.value
            }
        )
        
        logger.info("book_deleted", 
                   book_id=book.id, 
                   user_id=current_user.id)
        
        # Delete from database (cascade will handle related records)
        book.delete()
        
        return jsonify({'message': 'Book deleted successfully'})
        
    except Exception as e:
        logger.error("error_deleting_book", book_uuid=str(book_uuid), error=str(e))
        return jsonify({'error': 'Failed to delete book'}), 500


def _get_mimetype(format_type: str) -> str:
    """Get MIME type for file format."""
    mimetypes = {
        'pdf': 'application/pdf',
        'epub': 'application/epub+zip',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'txt': 'text/plain'
    }
    return mimetypes.get(format_type, 'application/octet-stream')


# Error handlers
@bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400


@bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500