"""
Sistema de cache avanzado para Buko AI.
"""
import json
import pickle
import hashlib
import functools
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from flask import current_app, request, g
from flask_caching import Cache
import redis
from app.utils.structured_logging import performance_logger


class CacheManager:
    """
    Gestor avanzado de cache con estrategias de invalidación y métricas.
    """
    
    def __init__(self, cache_instance: Cache, redis_client: redis.Redis = None):
        self.cache = cache_instance
        self.redis_client = redis_client
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor del cache con métricas.
        """
        start_time = datetime.utcnow()
        try:
            value = self.cache.get(key)
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            if value is not None:
                self.cache_stats['hits'] += 1
                performance_logger.log_cache_operation('get', key, hit=True, duration=duration)
                return value
            else:
                self.cache_stats['misses'] += 1
                performance_logger.log_cache_operation('get', key, hit=False, duration=duration)
                return default
                
        except Exception as e:
            current_app.logger.error(f"Cache get error for key {key}: {str(e)}")
            return default
    
    def set(self, key: str, value: Any, timeout: int = None) -> bool:
        """
        Establece un valor en el cache con métricas.
        """
        start_time = datetime.utcnow()
        try:
            result = self.cache.set(key, value, timeout=timeout)
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            if result:
                self.cache_stats['sets'] += 1
                performance_logger.log_cache_operation('set', key, duration=duration)
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Cache set error for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Elimina un valor del cache.
        """
        start_time = datetime.utcnow()
        try:
            result = self.cache.delete(key)
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            if result:
                self.cache_stats['deletes'] += 1
                performance_logger.log_cache_operation('delete', key, duration=duration)
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Elimina claves que coinciden con un patrón.
        """
        if not self.redis_client:
            current_app.logger.warning("Redis client not available for pattern deletion")
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                self.cache_stats['deletes'] += deleted
                performance_logger.log_cache_operation('delete_pattern', pattern)
                return deleted
            return 0
            
        except Exception as e:
            current_app.logger.error(f"Cache delete pattern error for {pattern}: {str(e)}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del cache.
        """
        total_operations = sum(self.cache_stats.values())
        hit_rate = (self.cache_stats['hits'] / 
                   (self.cache_stats['hits'] + self.cache_stats['misses'])) * 100 if total_operations > 0 else 0
        
        return {
            **self.cache_stats,
            'total_operations': total_operations,
            'hit_rate_percent': round(hit_rate, 2)
        }
    
    def clear_stats(self):
        """Limpia las estadísticas del cache."""
        for key in self.cache_stats:
            self.cache_stats[key] = 0


class CacheStrategies:
    """
    Estrategias de cache predefinidas para diferentes tipos de datos.
    """
    
    # TTL por tipo de datos
    TTL_CONFIGS = {
        'user_session': 3600,        # 1 hora
        'user_profile': 1800,        # 30 minutos
        'book_metadata': 7200,       # 2 horas
        'subscription_info': 3600,   # 1 hora
        'api_response': 300,         # 5 minutos
        'database_query': 600,       # 10 minutos
        'static_content': 86400,     # 24 horas
        'temporary': 60,             # 1 minuto
        'long_term': 604800         # 7 días
    }
    
    @staticmethod
    def get_ttl(cache_type: str) -> int:
        """Obtiene TTL para un tipo de cache."""
        return CacheStrategies.TTL_CONFIGS.get(cache_type, 300)
    
    @staticmethod
    def generate_key(prefix: str, *args, **kwargs) -> str:
        """
        Genera una clave de cache única basada en argumentos.
        """
        # Crear una representación string de los argumentos
        key_parts = [prefix]
        
        # Agregar argumentos posicionales
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            else:
                # Usar hash para objetos complejos
                key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
        
        # Agregar argumentos nombrados
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            kwargs_str = json.dumps(sorted_kwargs, sort_keys=True)
            key_parts.append(hashlib.md5(kwargs_str.encode()).hexdigest()[:8])
        
        # Agregar información de contexto si está disponible
        if hasattr(g, 'current_user_id'):
            key_parts.append(f"user_{g.current_user_id}")
        
        return ":".join(key_parts)
    
    @staticmethod
    def user_cache_key(user_id: int, data_type: str = "profile") -> str:
        """Genera clave de cache para datos de usuario."""
        return f"user:{user_id}:{data_type}"
    
    @staticmethod
    def book_cache_key(book_id: int, data_type: str = "metadata") -> str:
        """Genera clave de cache para datos de libro."""
        return f"book:{book_id}:{data_type}"
    
    @staticmethod
    def api_cache_key(endpoint: str, **params) -> str:
        """Genera clave de cache para respuestas de API."""
        return CacheStrategies.generate_key("api", endpoint, **params)


class CacheDecorators:
    """
    Decoradores para cache automático de funciones.
    """
    
    @staticmethod
    def cached_result(cache_type: str = 'temporary', key_prefix: str = None,
                     unless: Callable = None, make_cache_key: Callable = None):
        """
        Decorador para cachear resultados de funciones.
        
        Args:
            cache_type: Tipo de cache para determinar TTL
            key_prefix: Prefijo para la clave de cache
            unless: Función que determina si NO cachear
            make_cache_key: Función personalizada para generar clave
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Verificar si debemos omitir cache
                if unless and unless():
                    return func(*args, **kwargs)
                
                # Generar clave de cache
                if make_cache_key:
                    cache_key = make_cache_key(*args, **kwargs)
                else:
                    prefix = key_prefix or f"func:{func.__name__}"
                    cache_key = CacheStrategies.generate_key(prefix, *args, **kwargs)
                
                # Intentar obtener del cache
                from flask import current_app
                cache_manager = getattr(current_app, 'cache_manager', None)
                if not cache_manager:
                    return func(*args, **kwargs)
                
                cached_result = cache_manager.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Ejecutar función y cachear resultado
                result = func(*args, **kwargs)
                ttl = CacheStrategies.get_ttl(cache_type)
                cache_manager.set(cache_key, result, timeout=ttl)
                
                return result
            return wrapper
        return decorator
    
    @staticmethod
    def cache_user_data(data_type: str = 'profile', ttl: int = None):
        """
        Decorador específico para cachear datos de usuario.
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(user_id, *args, **kwargs):
                cache_key = CacheStrategies.user_cache_key(user_id, data_type)
                
                from flask import current_app
                cache_manager = getattr(current_app, 'cache_manager', None)
                if not cache_manager:
                    return func(user_id, *args, **kwargs)
                
                # Intentar obtener del cache
                cached_result = cache_manager.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Ejecutar función y cachear
                result = func(user_id, *args, **kwargs)
                timeout = ttl or CacheStrategies.get_ttl('user_profile')
                cache_manager.set(cache_key, result, timeout=timeout)
                
                return result
            return wrapper
        return decorator
    
    @staticmethod
    def invalidate_user_cache(data_type: str = None):
        """
        Decorador para invalidar cache de usuario después de modificaciones.
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(user_id, *args, **kwargs):
                result = func(user_id, *args, **kwargs)
                
                # Invalidar cache
                from flask import current_app
                cache_manager = getattr(current_app, 'cache_manager', None)
                if cache_manager:
                    if data_type:
                        cache_key = CacheStrategies.user_cache_key(user_id, data_type)
                        cache_manager.delete(cache_key)
                    else:
                        # Invalidar todos los datos del usuario
                        pattern = f"user:{user_id}:*"
                        cache_manager.delete_pattern(pattern)
                
                return result
            return wrapper
        return decorator


class SessionCache:
    """
    Cache especializado para manejo de sesiones de usuario.
    """
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.session_ttl = 3600  # 1 hora por defecto
    
    def set_session_data(self, session_id: str, user_id: int, data: Dict[str, Any]) -> bool:
        """
        Almacena datos de sesión en cache.
        """
        cache_key = f"session:{session_id}"
        session_data = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'data': data
        }
        return self.cache_manager.set(cache_key, session_data, timeout=self.session_ttl)
    
    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos de sesión del cache.
        """
        cache_key = f"session:{session_id}"
        return self.cache_manager.get(cache_key)
    
    def invalidate_session(self, session_id: str) -> bool:
        """
        Invalida una sesión específica.
        """
        cache_key = f"session:{session_id}"
        return self.cache_manager.delete(cache_key)
    
    def invalidate_user_sessions(self, user_id: int) -> int:
        """
        Invalida todas las sesiones de un usuario.
        """
        pattern = f"session:*"
        # Nota: Esto requiere una implementación más sofisticada
        # para buscar por user_id dentro de los datos de sesión
        return self.cache_manager.delete_pattern(pattern)


class QueryCache:
    """
    Cache especializado para consultas de base de datos.
    """
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.query_ttl = 600  # 10 minutos por defecto
    
    def cache_query_result(self, query_hash: str, result: Any, ttl: int = None) -> bool:
        """
        Cachea el resultado de una consulta.
        """
        cache_key = f"query:{query_hash}"
        timeout = ttl or self.query_ttl
        return self.cache_manager.set(cache_key, result, timeout=timeout)
    
    def get_cached_query(self, query_hash: str) -> Any:
        """
        Obtiene resultado de consulta cacheado.
        """
        cache_key = f"query:{query_hash}"
        return self.cache_manager.get(cache_key)
    
    def invalidate_table_cache(self, table_name: str) -> int:
        """
        Invalida cache relacionado con una tabla específica.
        """
        pattern = f"query:*{table_name}*"
        return self.cache_manager.delete_pattern(pattern)
    
    def generate_query_hash(self, query_str: str, params: tuple = None) -> str:
        """
        Genera hash único para una consulta y sus parámetros.
        """
        query_data = f"{query_str}:{params}" if params else query_str
        return hashlib.sha256(query_data.encode()).hexdigest()[:16]


def init_cache_system(app, redis_client):
    """
    Inicializa el sistema de cache completo.
    """
    # Crear instancia del gestor de cache
    cache_manager = CacheManager(app.extensions['cache'], redis_client)
    
    # Registrar en la aplicación
    app.cache_manager = cache_manager
    
    # Crear instancias especializadas
    app.session_cache = SessionCache(cache_manager)
    app.query_cache = QueryCache(cache_manager)
    
    # Log de inicialización
    app.logger.info("Sistema de cache inicializado correctamente")
    
    return cache_manager


# Decoradores exportados para uso directo
cached_result = CacheDecorators.cached_result
cache_user_data = CacheDecorators.cache_user_data
invalidate_user_cache = CacheDecorators.invalidate_user_cache