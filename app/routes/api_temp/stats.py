"""
API routes for statistics and monitoring.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import structlog

from app import db
from app.models.book_generation import BookGeneration, BookStatus
from app.models.user import User, SubscriptionType
from app.models.system_log import SystemLog, BookDownload
from app.utils.decorators import admin_required

logger = structlog.get_logger()

# Create blueprint
bp = Blueprint('stats_api', __name__, url_prefix='/api/stats')


@bp.route('/user', methods=['GET'])
@login_required
def get_user_stats():
    """
    Get statistics for the current user.
    """
    try:
        stats = current_user.get_statistics()
        
        # Add recent books
        recent_books = BookGeneration.query.filter_by(user_id=current_user.id)\
                                          .order_by(desc(BookGeneration.created_at))\
                                          .limit(5)\
                                          .all()
        
        stats['recent_books'] = [
            {
                'id': book.id,
                'uuid': str(book.uuid),
                'title': book.title,
                'status': book.status.value,
                'created_at': book.created_at.isoformat(),
                'final_pages': book.final_pages,
                'final_words': book.final_words
            }
            for book in recent_books
        ]
        
        # Add monthly usage trend
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        monthly_books = db.session.query(
            func.date(BookGeneration.created_at).label('date'),
            func.count(BookGeneration.id).label('count')
        ).filter(
            BookGeneration.user_id == current_user.id,
            BookGeneration.created_at >= thirty_days_ago
        ).group_by(func.date(BookGeneration.created_at)).all()
        
        stats['monthly_trend'] = [
            {
                'date': str(item.date),
                'books_created': item.count
            }
            for item in monthly_books
        ]
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error("error_getting_user_stats", user_id=current_user.id, error=str(e))
        return jsonify({'error': 'Failed to retrieve user statistics'}), 500


@bp.route('/dashboard', methods=['GET'])
@login_required
def get_dashboard_stats():
    """
    Get dashboard statistics for the current user.
    """
    try:
        # Quick stats
        total_books = BookGeneration.query.filter_by(user_id=current_user.id).count()
        completed_books = BookGeneration.query.filter_by(
            user_id=current_user.id,
            status=BookStatus.COMPLETED
        ).count()
        processing_books = BookGeneration.query.filter_by(
            user_id=current_user.id,
            status=BookStatus.PROCESSING
        ).count()
        
        # Usage this month
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        books_this_month = BookGeneration.query.filter(
            BookGeneration.user_id == current_user.id,
            BookGeneration.created_at >= month_start
        ).count()
        
        # Downloads this month
        downloads_this_month = BookDownload.query.filter(
            BookDownload.user_id == current_user.id,
            BookDownload.created_at >= month_start
        ).count()
        
        # Most popular format
        popular_format = db.session.query(
            BookDownload.format_type,
            func.count(BookDownload.id).label('count')
        ).filter(
            BookDownload.user_id == current_user.id
        ).group_by(BookDownload.format_type).order_by(desc('count')).first()
        
        # Recent activity (last 10 items)
        recent_books = BookGeneration.query.filter_by(user_id=current_user.id)\
                                          .order_by(desc(BookGeneration.updated_at))\
                                          .limit(10)\
                                          .all()
        
        activity = []
        for book in recent_books:
            activity.append({
                'type': 'book',
                'action': f'Book "{book.title}" {book.status.value}',
                'timestamp': book.updated_at.isoformat(),
                'book_uuid': str(book.uuid),
                'status': book.status.value
            })
        
        return jsonify({
            'quick_stats': {
                'total_books': total_books,
                'completed_books': completed_books,
                'processing_books': processing_books,
                'books_this_month': books_this_month,
                'downloads_this_month': downloads_this_month,
                'remaining_books': current_user.remaining_books,
                'subscription_type': current_user.subscription_type.value
            },
            'popular_format': popular_format.format_type if popular_format else None,
            'recent_activity': activity
        })
        
    except Exception as e:
        logger.error("error_getting_dashboard_stats", user_id=current_user.id, error=str(e))
        return jsonify({'error': 'Failed to retrieve dashboard statistics'}), 500


@bp.route('/system', methods=['GET'])
@admin_required
def get_system_stats():
    """
    Get system-wide statistics (admin only).
    """
    try:
        # User statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(status='active').count()
        verified_users = User.query.filter_by(email_verified=True).count()
        
        # Subscription breakdown
        subscription_stats = {}
        for sub_type in SubscriptionType:
            count = User.query.filter_by(subscription_type=sub_type).count()
            subscription_stats[sub_type.value] = count
        
        # Book statistics
        total_books = BookGeneration.query.count()
        completed_books = BookGeneration.query.filter_by(status=BookStatus.COMPLETED).count()
        failed_books = BookGeneration.query.filter_by(status=BookStatus.FAILED).count()
        processing_books = BookGeneration.query.filter_by(status=BookStatus.PROCESSING).count()
        queued_books = BookGeneration.query.filter_by(status=BookStatus.QUEUED).count()
        
        # Success rate
        success_rate = (completed_books / total_books * 100) if total_books > 0 else 0
        
        # Average processing time
        avg_processing_time = db.session.query(
            func.avg(
                func.extract('epoch', BookGeneration.completed_at - BookGeneration.started_at)
            )
        ).filter(
            BookGeneration.status == BookStatus.COMPLETED,
            BookGeneration.started_at.isnot(None),
            BookGeneration.completed_at.isnot(None)
        ).scalar()
        
        # Recent activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        daily_books = db.session.query(
            func.date(BookGeneration.created_at).label('date'),
            func.count(BookGeneration.id).label('count')
        ).filter(
            BookGeneration.created_at >= thirty_days_ago
        ).group_by(func.date(BookGeneration.created_at)).order_by('date').all()
        
        daily_users = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= thirty_days_ago
        ).group_by(func.date(User.created_at)).order_by('date').all()
        
        # Top genres
        top_genres = db.session.query(
            BookGeneration.genre,
            func.count(BookGeneration.id).label('count')
        ).filter(
            BookGeneration.genre.isnot(None)
        ).group_by(BookGeneration.genre).order_by(desc('count')).limit(10).all()
        
        # System load
        queue_size = BookGeneration.query.filter_by(status=BookStatus.QUEUED).count()
        processing_load = BookGeneration.query.filter_by(status=BookStatus.PROCESSING).count()
        
        return jsonify({
            'users': {
                'total': total_users,
                'active': active_users,
                'verified': verified_users,
                'by_subscription': subscription_stats
            },
            'books': {
                'total': total_books,
                'completed': completed_books,
                'failed': failed_books,
                'processing': processing_books,
                'queued': queued_books,
                'success_rate': round(success_rate, 2)
            },
            'performance': {
                'avg_processing_time': round(avg_processing_time or 0, 2),
                'queue_size': queue_size,
                'processing_load': processing_load
            },
            'trends': {
                'daily_books': [
                    {'date': str(item.date), 'count': item.count}
                    for item in daily_books
                ],
                'daily_users': [
                    {'date': str(item.date), 'count': item.count}
                    for item in daily_users
                ]
            },
            'top_genres': [
                {'genre': item.genre, 'count': item.count}
                for item in top_genres
            ]
        })
        
    except Exception as e:
        logger.error("error_getting_system_stats", error=str(e))
        return jsonify({'error': 'Failed to retrieve system statistics'}), 500


@bp.route('/usage', methods=['GET'])
@login_required
def get_usage_stats():
    """
    Get detailed usage statistics for the current user.
    """
    try:
        # Time range filter
        days = int(request.args.get('days', 30))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Books created in time range
        books_query = BookGeneration.query.filter(
            BookGeneration.user_id == current_user.id,
            BookGeneration.created_at >= start_date,
            BookGeneration.created_at <= end_date
        )
        
        # Status breakdown
        status_breakdown = {}
        for status in BookStatus:
            count = books_query.filter_by(status=status).count()
            status_breakdown[status.value] = count
        
        # Daily breakdown
        daily_stats = db.session.query(
            func.date(BookGeneration.created_at).label('date'),
            func.count(BookGeneration.id).label('books_created'),
            func.sum(BookGeneration.final_pages).label('total_pages'),
            func.sum(BookGeneration.final_words).label('total_words')
        ).filter(
            BookGeneration.user_id == current_user.id,
            BookGeneration.created_at >= start_date,
            BookGeneration.created_at <= end_date
        ).group_by(func.date(BookGeneration.created_at)).order_by('date').all()
        
        # Genre preferences
        genre_stats = db.session.query(
            BookGeneration.genre,
            func.count(BookGeneration.id).label('count')
        ).filter(
            BookGeneration.user_id == current_user.id,
            BookGeneration.genre.isnot(None),
            BookGeneration.created_at >= start_date
        ).group_by(BookGeneration.genre).order_by(desc('count')).all()
        
        # Download patterns
        downloads = db.session.query(
            BookDownload.format_type,
            func.count(BookDownload.id).label('count')
        ).filter(
            BookDownload.user_id == current_user.id,
            BookDownload.created_at >= start_date
        ).group_by(BookDownload.format_type).order_by(desc('count')).all()
        
        # Average metrics
        avg_stats = db.session.query(
            func.avg(BookGeneration.final_pages).label('avg_pages'),
            func.avg(BookGeneration.final_words).label('avg_words'),
            func.avg(
                func.extract('epoch', BookGeneration.completed_at - BookGeneration.started_at)
            ).label('avg_processing_time')
        ).filter(
            BookGeneration.user_id == current_user.id,
            BookGeneration.status == BookStatus.COMPLETED,
            BookGeneration.created_at >= start_date
        ).first()
        
        return jsonify({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'status_breakdown': status_breakdown,
            'daily_stats': [
                {
                    'date': str(item.date),
                    'books_created': item.books_created or 0,
                    'total_pages': item.total_pages or 0,
                    'total_words': item.total_words or 0
                }
                for item in daily_stats
            ],
            'genre_preferences': [
                {'genre': item.genre, 'count': item.count}
                for item in genre_stats
            ],
            'download_patterns': [
                {'format': item.format_type, 'count': item.count}
                for item in downloads
            ],
            'averages': {
                'pages_per_book': round(avg_stats.avg_pages or 0, 1),
                'words_per_book': round(avg_stats.avg_words or 0, 1),
                'processing_time': round(avg_stats.avg_processing_time or 0, 1)
            }
        })
        
    except Exception as e:
        logger.error("error_getting_usage_stats", user_id=current_user.id, error=str(e))
        return jsonify({'error': 'Failed to retrieve usage statistics'}), 500


@bp.route('/health', methods=['GET'])
def health_check():
    """
    Basic health check endpoint.
    """
    try:
        # Test database connectivity
        db.session.execute('SELECT 1')
        
        # Basic system stats
        total_users = User.query.count()
        total_books = BookGeneration.query.count()
        processing_books = BookGeneration.query.filter_by(status=BookStatus.PROCESSING).count()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'stats': {
                'total_users': total_users,
                'total_books': total_books,
                'processing_books': processing_books
            }
        })
        
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500