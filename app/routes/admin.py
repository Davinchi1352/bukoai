"""
Rutas administrativas para monitoreo y gestión.
"""
from flask import Blueprint, jsonify, request
from app.utils.log_config import LogAnalyzer
from app.utils.structured_logging import structured_logger
from app import cache

bp = Blueprint('admin', __name__)


@bp.route('/logs/stats')
def log_stats():
    """Obtiene estadísticas de logs."""
    try:
        stats = LogAnalyzer.get_log_stats('logs')
        return jsonify(stats)
    except Exception as e:
        structured_logger.error("Error getting log stats", error=str(e))
        return jsonify({'error': str(e)}), 500


@bp.route('/logs/errors')
def error_analysis():
    """Analiza patrones de errores."""
    try:
        hours = request.args.get('hours', 24, type=int)
        analysis = LogAnalyzer.analyze_error_patterns('logs/errors.log', hours)
        return jsonify(analysis)
    except Exception as e:
        structured_logger.error("Error analyzing errors", error=str(e))
        return jsonify({'error': str(e)}), 500


@bp.route('/cache/stats')
def cache_stats():
    """Obtiene estadísticas del cache."""
    try:
        from flask import current_app
        cache_manager = getattr(current_app, 'cache_manager', None)
        if cache_manager:
            stats = cache_manager.get_stats()
            return jsonify(stats)
        return jsonify({'error': 'Cache manager not available'}), 503
    except Exception as e:
        structured_logger.error("Error getting cache stats", error=str(e))
        return jsonify({'error': str(e)}), 500


@bp.route('/health')
def health_check():
    """Health check completo del sistema."""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': structured_logger.get_request_context(),
            'services': {
                'database': 'healthy',
                'redis': 'healthy',
                'cache': 'healthy',
                'logging': 'healthy'
            }
        }
        
        # Verificar Redis
        try:
            from flask import current_app
            redis_client = getattr(current_app, 'redis_client', None)
            if redis_client:
                redis_client.ping()
            else:
                health_status['services']['redis'] = 'unavailable'
        except Exception:
            health_status['services']['redis'] = 'unhealthy'
            health_status['status'] = 'degraded'
        
        # Verificar Cache
        try:
            cache.get('health_check')
            cache.set('health_check', 'ok', timeout=60)
        except Exception:
            health_status['services']['cache'] = 'unhealthy'
            health_status['status'] = 'degraded'
        
        return jsonify(health_status)
        
    except Exception as e:
        structured_logger.error("Health check failed", error=str(e))
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500