"""
Servicio de cache específico para Buko AI con estrategias optimizadas.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from flask import current_app
from app.utils.cache_manager import CacheStrategies, cached_result, cache_user_data, invalidate_user_cache
from app.utils.structured_logging import performance_logger


class BookCacheService:
    """
    Servicio de cache especializado para libros.
    """
    
    @staticmethod
    @cached_result(cache_type='book_metadata', key_prefix='book_meta')
    def get_book_metadata(book_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene metadatos de libro con cache.
        """
        from app.models.book_generation import BookGeneration
        
        book = BookGeneration.query.get(book_id)
        if not book:
            return None
        
        return {
            'id': book.id,
            'title': book.title,
            'genre': book.genre,
            'status': book.status.value,
            'chapter_count': book.chapter_count,
            'page_count': book.page_count,
            'created_at': book.created_at.isoformat(),
            'completed_at': book.completed_at.isoformat() if book.completed_at else None
        }
    
    @staticmethod
    @cached_result(cache_type='api_response', key_prefix='book_list')
    def get_user_books_summary(user_id: int, status: str = None) -> List[Dict[str, Any]]:
        """
        Obtiene resumen de libros de usuario con cache.
        """
        from app.models.book_generation import BookGeneration, BookStatus
        from sqlalchemy import and_
        
        query = BookGeneration.query.filter(BookGeneration.user_id == user_id)
        
        if status:
            query = query.filter(BookGeneration.status == BookStatus[status.upper()])
        
        books = query.order_by(BookGeneration.created_at.desc()).limit(50).all()
        
        return [{
            'id': book.id,
            'title': book.title,
            'status': book.status.value,
            'created_at': book.created_at.isoformat(),
            'progress': BookCacheService._calculate_progress(book)
        } for book in books]
    
    @staticmethod
    def _calculate_progress(book) -> int:
        """Calcula progreso de generación de libro."""
        if book.status.value == 'COMPLETED':
            return 100
        elif book.status.value == 'PROCESSING':
            return 50  # Estimación básica
        elif book.status.value == 'QUEUED':
            return 10
        else:
            return 0
    
    @staticmethod
    def invalidate_book_cache(book_id: int):
        """Invalida cache relacionado con un libro."""
        cache_manager = getattr(current_app, 'cache_manager', None)
        if cache_manager:
            # Invalidar metadatos del libro
            book_key = CacheStrategies.book_cache_key(book_id)
            cache_manager.delete(book_key)
            
            # Invalidar listas que puedan contener este libro
            pattern = f"book_list:*"
            cache_manager.delete_pattern(pattern)


class UserCacheService:
    """
    Servicio de cache especializado para usuarios.
    """
    
    @staticmethod
    @cache_user_data(data_type='profile', ttl=1800)
    def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene perfil de usuario con cache.
        """
        from app.models.user import User
        
        user = User.query.get(user_id)
        if not user:
            return None
        
        return {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'subscription_type': user.subscription_type.value,
            'books_used_this_month': user.books_used_this_month,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'created_at': user.created_at.isoformat()
        }
    
    @staticmethod
    @cache_user_data(data_type='subscription', ttl=3600)
    def get_user_subscription_info(user_id: int) -> Dict[str, Any]:
        """
        Obtiene información de suscripción con cache.
        """
        from app.models.user import User
        from app.models.subscription import Subscription
        
        user = User.query.get(user_id)
        if not user:
            return {}
        
        # Obtener suscripción activa
        subscription = Subscription.query.filter_by(user_id=user_id).order_by(
            Subscription.created_at.desc()
        ).first()
        
        info = {
            'current_plan': user.subscription_type.value,
            'books_used': user.books_used_this_month,
            'subscription_start': user.subscription_start.isoformat() if user.subscription_start else None,
            'subscription_end': user.subscription_end.isoformat() if user.subscription_end else None
        }
        
        if subscription:
            info.update({
                'subscription_id': subscription.id,
                'status': subscription.status.value,
                'trial_end': subscription.trial_end.isoformat() if subscription.trial_end else None
            })
        
        return info
    
    @staticmethod
    @invalidate_user_cache(data_type='profile')
    def update_user_profile(user_id: int, **kwargs):
        """
        Actualiza perfil de usuario e invalida cache.
        """
        from app.models.user import User
        from app import db
        
        user = User.query.get(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            db.session.commit()
            return True
        return False


class SubscriptionCacheService:
    """
    Servicio de cache para datos de suscripciones.
    """
    
    @staticmethod
    @cached_result(cache_type='subscription_info', key_prefix='sub_limits')
    def get_subscription_limits(plan_type: str) -> Dict[str, Any]:
        """
        Obtiene límites de suscripción con cache.
        """
        # Definir límites por plan
        limits = {
            'FREE': {
                'monthly_books': 1,
                'max_pages': 50,
                'formats': ['PDF'],
                'priority': 0,
                'features': ['basic_generation']
            },
            'STARTER': {
                'monthly_books': 5,
                'max_pages': 100,
                'formats': ['PDF', 'EPUB'],
                'priority': 1,
                'features': ['basic_generation', 'cover_generation']
            },
            'PRO': {
                'monthly_books': 20,
                'max_pages': 200,
                'formats': ['PDF', 'EPUB', 'DOCX'],
                'priority': 2,
                'features': ['basic_generation', 'cover_generation', 'advanced_styles']
            },
            'BUSINESS': {
                'monthly_books': 50,
                'max_pages': 300,
                'formats': ['PDF', 'EPUB', 'DOCX'],
                'priority': 3,
                'features': ['basic_generation', 'cover_generation', 'advanced_styles', 'api_access']
            },
            'ENTERPRISE': {
                'monthly_books': -1,  # Ilimitado
                'max_pages': 500,
                'formats': ['PDF', 'EPUB', 'DOCX'],
                'priority': 4,
                'features': ['basic_generation', 'cover_generation', 'advanced_styles', 'api_access', 'priority_support']
            }
        }
        
        return limits.get(plan_type, limits['FREE'])
    
    @staticmethod
    def check_user_limits(user_id: int) -> Dict[str, Any]:
        """
        Verifica límites de usuario con cache optimizado.
        """
        cache_key = f"user_limits:{user_id}"
        cache_manager = getattr(current_app, 'cache_manager', None)
        
        if cache_manager:
            cached_limits = cache_manager.get(cache_key)
            if cached_limits:
                return cached_limits
        
        # Calcular límites
        user_info = UserCacheService.get_user_subscription_info(user_id)
        plan_type = user_info.get('current_plan', 'FREE')
        limits = SubscriptionCacheService.get_subscription_limits(plan_type)
        
        # Verificar uso actual
        books_used = user_info.get('books_used', 0)
        monthly_limit = limits['monthly_books']
        
        result = {
            'plan_type': plan_type,
            'monthly_books_limit': monthly_limit,
            'books_used': books_used,
            'books_remaining': monthly_limit - books_used if monthly_limit > 0 else -1,
            'can_generate': monthly_limit == -1 or books_used < monthly_limit,
            'limits': limits
        }
        
        # Cachear resultado por 5 minutos
        if cache_manager:
            cache_manager.set(cache_key, result, timeout=300)
        
        return result


class StatsCacheService:
    """
    Servicio de cache para estadísticas del sistema.
    """
    
    @staticmethod
    @cached_result(cache_type='long_term', key_prefix='global_stats')
    def get_global_stats() -> Dict[str, Any]:
        """
        Obtiene estadísticas globales con cache de larga duración.
        """
        from app.models.user import User
        from app.models.book_generation import BookGeneration, BookStatus
        from sqlalchemy import func
        from app import db
        
        # Estadísticas de usuarios
        user_stats = db.session.query(
            func.count(User.id).label('total_users'),
            func.count(User.id).filter(User.status == 'ACTIVE').label('active_users')
        ).first()
        
        # Estadísticas de libros
        book_stats = db.session.query(
            func.count(BookGeneration.id).label('total_books'),
            func.count(BookGeneration.id).filter(BookGeneration.status == BookStatus.COMPLETED).label('completed_books'),
            func.sum(BookGeneration.total_tokens).filter(BookGeneration.status == BookStatus.COMPLETED).label('total_tokens'),
            func.avg(BookGeneration.final_pages).filter(BookGeneration.status == BookStatus.COMPLETED).label('avg_pages')
        ).first()
        
        return {
            'users': {
                'total': user_stats.total_users or 0,
                'active': user_stats.active_users or 0
            },
            'books': {
                'total': book_stats.total_books or 0,
                'completed': book_stats.completed_books or 0,
                'total_tokens': int(book_stats.total_tokens or 0),
                'avg_pages': round(float(book_stats.avg_pages or 0), 1)
            },
            'last_updated': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def invalidate_global_stats():
        """Invalida cache de estadísticas globales."""
        cache_manager = getattr(current_app, 'cache_manager', None)
        if cache_manager:
            pattern = "global_stats:*"
            cache_manager.delete_pattern(pattern)


class CacheWarmupService:
    """
    Servicio para pre-calentar cache con datos frecuentemente accedidos.
    """
    
    @staticmethod
    def warmup_user_cache(user_id: int):
        """
        Pre-calienta cache para un usuario específico.
        """
        try:
            # Pre-cargar datos del usuario
            UserCacheService.get_user_profile(user_id)
            UserCacheService.get_user_subscription_info(user_id)
            SubscriptionCacheService.check_user_limits(user_id)
            BookCacheService.get_user_books_summary(user_id)
            
            performance_logger.info(
                "Cache warmup completed for user",
                user_id=user_id,
                event_type="cache_warmup"
            )
            
        except Exception as e:
            performance_logger.error(
                "Cache warmup failed for user",
                user_id=user_id,
                error=str(e),
                event_type="cache_warmup_error"
            )
    
    @staticmethod
    def warmup_global_cache():
        """
        Pre-calienta cache global del sistema.
        """
        try:
            # Pre-cargar estadísticas globales
            StatsCacheService.get_global_stats()
            
            # Pre-cargar límites de suscripciones
            for plan in ['FREE', 'STARTER', 'PRO', 'BUSINESS', 'ENTERPRISE']:
                SubscriptionCacheService.get_subscription_limits(plan)
            
            performance_logger.info(
                "Global cache warmup completed",
                event_type="global_cache_warmup"
            )
            
        except Exception as e:
            performance_logger.error(
                "Global cache warmup failed",
                error=str(e),
                event_type="global_cache_warmup_error"
            )