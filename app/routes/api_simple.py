"""
Simplified API routes for dashboard functionality.
Provides mock data without complex dependencies.
"""

from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
import random

bp = Blueprint('api_simple', __name__)


@bp.route('/stats/dashboard', methods=['GET'])
def get_dashboard_stats():
    """
    Get dashboard statistics - simplified version with mock data.
    """
    try:
        # Mock statistics for demonstration
        stats = {
            'total_books': random.randint(5, 25),
            'completed_books': random.randint(3, 20),
            'processing_books': random.randint(0, 3),
            'books_this_month': random.randint(1, 8),
            'total_books_change': random.randint(-2, 5),
            'completed_books_change': random.randint(0, 4),
            'monthly_books_change': random.randint(0, 3),
            'downloads_this_month': random.randint(2, 15),
            'avg_generation_time': round(random.uniform(2.5, 8.5), 1),
            'success_rate': round(random.uniform(85.0, 98.5), 1)
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve dashboard statistics'}), 500


@bp.route('/books', methods=['GET'])
def get_books():
    """
    Get user's books - simplified version with mock data.
    """
    try:
        # Get query parameters
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        status_filter = request.args.get('status')
        
        # Mock book data
        book_titles = [
            "Guía Completa de Python para Principiantes",
            "Marketing Digital en la Era de la IA",
            "Introducción a la Ciencia de Datos",
            "Desarrollo Web con Flask y React",
            "Finanzas Personales para Millennials",
            "Historia del Arte Contemporáneo",
            "Cocina Mediterránea Saludable",
            "Mindfulness y Productividad",
            "Fotografía Digital Profesional",
            "Emprendimiento en el Siglo XXI"
        ]
        
        statuses = ['completed', 'processing', 'error', 'pending']
        
        # Generate mock books
        all_books = []
        for i in range(min(len(book_titles), 10)):
            created_date = datetime.now() - timedelta(days=random.randint(1, 30))
            status = random.choice(statuses) if not status_filter else status_filter
            
            # Bias towards completed books
            if not status_filter and random.random() < 0.7:
                status = 'completed'
            
            book = {
                'id': i + 1,
                'uuid': f'book-{i+1}-uuid-mock',
                'title': book_titles[i],
                'status': status,
                'created_at': created_date.isoformat(),
                'updated_at': created_date.isoformat(),
                'word_count': random.randint(1500, 8000),
                'page_count': random.randint(10, 50),
                'format': random.choice(['pocket', 'standard', 'large']),
                'genre': random.choice(['tecnología', 'negocios', 'educación', 'salud', 'arte']),
                'progress': 100 if status == 'completed' else random.randint(0, 95) if status == 'processing' else 0
            }
            all_books.append(book)
        
        # Apply filtering
        filtered_books = all_books
        if status_filter:
            filtered_books = [book for book in all_books if book['status'] == status_filter]
        
        # Apply pagination
        total_count = len(filtered_books)
        books_page = filtered_books[offset:offset + limit]
        
        response = {
            'books': books_page,
            'total': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total_count
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve books'}), 500


@bp.route('/books/recent', methods=['GET'])
def get_recent_books():
    """
    Get recent books - redirect to main books endpoint with limit.
    """
    limit = request.args.get('limit', '5')
    return get_books()


@bp.route('/stats/user', methods=['GET'])
def get_user_stats():
    """
    Get user statistics with recent books.
    """
    try:
        # Get recent books first
        recent_response = get_books()
        recent_data = recent_response.get_json()
        recent_books = recent_data.get('books', [])[:5]
        
        stats = {
            'user_id': 'mock-user-id',
            'total_books': len(recent_books) + random.randint(0, 10),
            'completed_books': sum(1 for book in recent_books if book['status'] == 'completed'),
            'processing_books': sum(1 for book in recent_books if book['status'] == 'processing'),
            'recent_books': recent_books,
            'total_downloads': random.randint(5, 50),
            'total_words': sum(book.get('word_count', 0) for book in recent_books),
            'avg_generation_time': round(random.uniform(3.0, 7.5), 1),
            'success_rate': round(random.uniform(88.0, 96.5), 1),
            'preferred_format': 'pocket',
            'most_used_genre': 'tecnología'
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve user statistics'}), 500


@bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for the simplified API.
    """
    return jsonify({
        'status': 'healthy',
        'service': 'api-simple',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0-mock'
    })


# Additional mock endpoints for completeness

@bp.route('/books/<book_id>/progress', methods=['GET'])
def get_book_progress(book_id):
    """
    Get progress for a specific book.
    """
    progress = random.randint(0, 100)
    status = 'completed' if progress == 100 else 'processing' if progress > 0 else 'pending'
    
    return jsonify({
        'book_id': book_id,
        'progress': progress,
        'status': status,
        'current_step': 'Generando capítulo 3...' if status == 'processing' else 'Completado',
        'estimated_time_remaining': random.randint(1, 15) if status == 'processing' else 0
    })


@bp.route('/stats/usage', methods=['GET'])
def get_usage_stats():
    """
    Get detailed usage statistics.
    """
    return jsonify({
        'daily_usage': [
            {'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'), 
             'books_generated': random.randint(0, 3)}
            for i in range(7)
        ],
        'monthly_total': random.randint(8, 25),
        'weekly_total': random.randint(2, 8),
        'most_active_day': 'Monday',
        'most_used_format': 'pocket',
        'avg_words_per_book': random.randint(2500, 6000)
    })