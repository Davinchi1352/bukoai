"""
Real API routes for dashboard - safe database queries.
"""

from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

bp = Blueprint('api_real', __name__)


@bp.route('/stats/dashboard', methods=['GET'])
@login_required
def get_dashboard_stats():
    """
    Get real dashboard statistics from database - safe implementation.
    """
    try:
        # Import models here to avoid circular imports
        from app.models.book_generation import BookGeneration, BookStatus
        from app.models.system_log import BookDownload
        from app import db
        
        user_id = current_user.id
        
        # Time ranges
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (month_start - timedelta(days=32)).replace(day=1)
        
        # Basic counts - simple queries
        total_books = BookGeneration.query.filter_by(user_id=user_id).count()
        
        completed_books = BookGeneration.query.filter_by(
            user_id=user_id,
            status=BookStatus.COMPLETED
        ).count()
        
        processing_books = BookGeneration.query.filter_by(
            user_id=user_id,
            status=BookStatus.PROCESSING
        ).count()
        
        # Books this month
        books_this_month = BookGeneration.query.filter(
            BookGeneration.user_id == user_id,
            BookGeneration.created_at >= month_start
        ).count()
        
        books_last_month = BookGeneration.query.filter(
            BookGeneration.user_id == user_id,
            BookGeneration.created_at >= last_month_start,
            BookGeneration.created_at < month_start
        ).count()
        
        # Word and page statistics - simplified
        total_words = 0
        total_pages = 0
        total_cost = 0.0
        completed_books_list = BookGeneration.query.filter_by(
            user_id=user_id,
            status=BookStatus.COMPLETED
        ).all()
        
        for book in completed_books_list:
            if book.final_words:
                total_words += book.final_words
            if book.final_pages:
                total_pages += book.final_pages
            if book.estimated_cost:
                total_cost += float(book.estimated_cost)
        
        avg_words = total_words // len(completed_books_list) if completed_books_list else 0
        avg_cost = total_cost / len(completed_books_list) if completed_books_list else 0
        
        # Downloads count
        total_downloads = BookDownload.query.filter_by(user_id=user_id).count()
        
        # Success rate
        success_rate = (completed_books / total_books * 100) if total_books > 0 else 0
        
        # Changes
        total_books_change = books_this_month - books_last_month
        
        stats = {
            'total_books': total_books,
            'completed_books': completed_books,
            'processing_books': processing_books,
            'books_this_month': books_this_month,
            'total_books_change': total_books_change,
            'total_words': total_words,
            'avg_words_per_book': avg_words,
            'total_pages': total_pages,
            'total_downloads': total_downloads,
            'success_rate': round(success_rate, 1),
            'total_cost': round(total_cost, 2),
            'avg_cost_per_book': round(avg_cost, 2)
        }
        
        return jsonify(stats)
        
    except Exception as e:
        # Return safe fallback data instead of error
        return jsonify({
            'total_books': 0,
            'completed_books': 0,
            'processing_books': 0,
            'books_this_month': 0,
            'total_books_change': 0,
            'total_words': 0,
            'avg_words_per_book': 0,
            'total_pages': 0,
            'total_downloads': 0,
            'success_rate': 0,
            'total_cost': 0,
            'avg_cost_per_book': 0,
            'error': str(e)  # Include error for debugging
        })


@bp.route('/stats/analytics', methods=['GET'])
@login_required
def get_detailed_analytics():
    """
    Get real analytics for the dashboard - simplified queries.
    """
    try:
        from app.models.book_generation import BookGeneration, BookStatus
        from app.models.system_log import BookDownload
        from app import db
        
        user_id = current_user.id
        
        # Get all completed books
        completed_books = BookGeneration.query.filter_by(
            user_id=user_id,
            status=BookStatus.COMPLETED
        ).all()
        
        # Count by genre
        genre_counts = {}
        format_counts = {}
        audience_counts = {}
        tone_counts = {}
        
        for book in completed_books:
            # Genre
            genre = book.genre or 'Sin categoría'
            if genre in genre_counts:
                genre_counts[genre]['count'] += 1
                if book.final_words:
                    genre_counts[genre]['total_words'] += book.final_words
            else:
                genre_counts[genre] = {
                    'count': 1,
                    'total_words': book.final_words or 0
                }
            
            # Format
            format_size = book.format_size or 'standard'
            if format_size in format_counts:
                format_counts[format_size]['count'] += 1
                if book.final_pages:
                    format_counts[format_size]['total_pages'] += book.final_pages
            else:
                format_counts[format_size] = {
                    'count': 1,
                    'total_pages': book.final_pages or 0
                }
            
            # Audience
            audience = book.target_audience or 'General'
            audience_counts[audience] = audience_counts.get(audience, 0) + 1
            
            # Tone
            tone = book.tone or 'Neutral'
            tone_counts[tone] = tone_counts.get(tone, 0) + 1
        
        # Download formats
        downloads = BookDownload.query.filter_by(user_id=user_id).all()
        download_format_counts = {}
        
        for download in downloads:
            format_str = str(download.format).split('.')[-1] if hasattr(download.format, 'value') else str(download.format)
            if format_str in download_format_counts:
                download_format_counts[format_str]['count'] += 1
                download_format_counts[format_str]['total_downloads'] += download.download_count or 1
            else:
                download_format_counts[format_str] = {
                    'count': 1,
                    'total_downloads': download.download_count or 1
                }
        
        # Build response
        analytics = {
            'books_by_genre': [
                {
                    'genre': genre,
                    'count': data['count'],
                    'avg_words': data['total_words'] // data['count'] if data['count'] > 0 else 0,
                    'avg_pages': 0  # Calculate if needed
                }
                for genre, data in sorted(genre_counts.items(), key=lambda x: x[1]['count'], reverse=True)
            ],
            'books_by_format': [
                {
                    'format': format_size,
                    'count': data['count'],
                    'avg_pages': data['total_pages'] // data['count'] if data['count'] > 0 else 0
                }
                for format_size, data in sorted(format_counts.items(), key=lambda x: x[1]['count'], reverse=True)
            ],
            'books_by_audience': [
                {
                    'audience': audience,
                    'count': count
                }
                for audience, count in sorted(audience_counts.items(), key=lambda x: x[1], reverse=True)
            ],
            'books_by_tone': [
                {
                    'tone': tone,
                    'count': count
                }
                for tone, count in sorted(tone_counts.items(), key=lambda x: x[1], reverse=True)
            ],
            'download_formats': [
                {
                    'format': format_name.upper(),
                    'count': data['count'],
                    'total_downloads': data['total_downloads']
                }
                for format_name, data in sorted(download_format_counts.items(), key=lambda x: x[1]['total_downloads'], reverse=True)
            ]
        }
        
        return jsonify(analytics)
        
    except Exception as e:
        # Return empty analytics on error
        return jsonify({
            'books_by_genre': [],
            'books_by_format': [],
            'books_by_audience': [],
            'books_by_tone': [],
            'download_formats': [],
            'error': str(e)
        })


@bp.route('/books', methods=['GET'])
@login_required
def get_books():
    """
    Get real user's books from database.
    """
    try:
        from app.models.book_generation import BookGeneration, BookStatus
        from app import db
        
        user_id = current_user.id
        
        # Get query parameters
        limit = int(request.args.get('limit', 5))
        offset = int(request.args.get('offset', 0))
        
        # Get books ordered by creation date
        books = BookGeneration.query.filter_by(user_id=user_id).order_by(
            BookGeneration.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        # Get total count
        total_count = BookGeneration.query.filter_by(user_id=user_id).count()
        
        # Convert to JSON
        books_data = []
        for book in books:
            book_dict = {
                'id': book.id,
                'title': book.title,
                'status': book.status.value if book.status else 'unknown',
                'genre': book.genre,
                'created_at': book.created_at.isoformat() if book.created_at else None,
                'final_words': book.final_words,
                'final_pages': book.final_pages
            }
            books_data.append(book_dict)
        
        response = {
            'books': books_data,
            'total': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total_count
        }
        
        return jsonify(response)
        
    except Exception as e:
        # Return empty list on error
        return jsonify({
            'books': [],
            'total': 0,
            'limit': limit if 'limit' in locals() else 5,
            'offset': 0,
            'has_more': False,
            'error': str(e)
        })


@bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({
        'status': 'healthy',
        'service': 'api-real',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0-real-db'
    })