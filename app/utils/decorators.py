"""
Decorators for Buko AI application.
"""

from functools import wraps
from flask import jsonify, request
from flask_login import current_user
import structlog

logger = structlog.get_logger()


def admin_required(f):
    """
    Decorator to require admin privileges.
    
    Checks if the current user has admin privileges (enterprise subscription).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user has admin privileges (enterprise subscription or specific admin flag)
        if (current_user.subscription_type.value != 'enterprise' and 
            not getattr(current_user, 'is_admin', False)):
            logger.warning("unauthorized_admin_access", 
                         user_id=current_user.id,
                         endpoint=request.endpoint)
            return jsonify({'error': 'Admin privileges required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def subscription_required(min_subscription=None):
    """
    Decorator to require a minimum subscription level.
    
    Args:
        min_subscription: Minimum subscription type required
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            
            if not current_user.has_active_subscription:
                return jsonify({
                    'error': 'Active subscription required',
                    'subscription_type': current_user.subscription_type.value
                }), 402
            
            # Check minimum subscription level if specified
            if min_subscription:
                subscription_hierarchy = {
                    'free': 0,
                    'starter': 1,
                    'pro': 2,
                    'business': 3,
                    'enterprise': 4
                }
                
                user_level = subscription_hierarchy.get(current_user.subscription_type.value, 0)
                required_level = subscription_hierarchy.get(min_subscription, 0)
                
                if user_level < required_level:
                    return jsonify({
                        'error': f'Subscription level {min_subscription} or higher required',
                        'current_subscription': current_user.subscription_type.value
                    }), 402
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def rate_limit(max_requests=60, per_seconds=60):
    """
    Simple rate limiting decorator.
    
    Args:
        max_requests: Maximum number of requests
        per_seconds: Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This is a simplified rate limiter
            # In production, you'd want to use Redis or a proper rate limiting service
            
            # For now, we'll just log the attempt and continue
            logger.info("api_request", 
                       user_id=getattr(current_user, 'id', None),
                       endpoint=request.endpoint,
                       method=request.method)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_json(required_fields=None):
    """
    Decorator to validate JSON payload.
    
    Args:
        required_fields: List of required field names
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON payload'}), 400
            
            # Check required fields
            if required_fields:
                missing_fields = []
                for field in required_fields:
                    if field not in data or data[field] is None:
                        missing_fields.append(field)
                
                if missing_fields:
                    return jsonify({
                        'error': 'Missing required fields',
                        'missing_fields': missing_fields
                    }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def log_activity(action):
    """
    Decorator to log user activity.
    
    Args:
        action: Action name to log
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            
            # Log the activity
            if current_user.is_authenticated:
                from app.utils.logging import log_system_event
                
                try:
                    # Extract relevant data from kwargs or request
                    details = {}
                    if 'book_uuid' in kwargs:
                        details['book_uuid'] = str(kwargs['book_uuid'])
                    
                    if request.is_json:
                        request_data = request.get_json()
                        if request_data and isinstance(request_data, dict):
                            # Log only safe fields
                            safe_fields = ['title', 'genre', 'format_type', 'language']
                            for field in safe_fields:
                                if field in request_data:
                                    details[field] = request_data[field]
                    
                    log_system_event(
                        user_id=current_user.id,
                        action=action,
                        details=details
                    )
                    
                except Exception as e:
                    logger.warning("activity_logging_failed", 
                                 action=action,
                                 error=str(e))
            
            return result
        
        return decorated_function
    return decorator


def handle_file_upload(allowed_extensions=None, max_size=None):
    """
    Decorator to handle file uploads.
    
    Args:
        allowed_extensions: List of allowed file extensions
        max_size: Maximum file size in bytes
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Check file extension
            if allowed_extensions:
                file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
                if file_ext not in allowed_extensions:
                    return jsonify({
                        'error': f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}'
                    }), 400
            
            # Check file size
            if max_size:
                file.seek(0, 2)  # Seek to end of file
                size = file.tell()
                file.seek(0)  # Seek back to beginning
                
                if size > max_size:
                    return jsonify({
                        'error': f'File too large. Maximum size: {max_size // (1024*1024)}MB'
                    }), 400
            
            return f(file, *args, **kwargs)
        
        return decorated_function
    return decorator


def cache_response(timeout=300):
    """
    Decorator to cache API responses.
    
    Args:
        timeout: Cache timeout in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This is a placeholder for caching functionality
            # In production, you'd integrate with Redis or another caching solution
            
            # For now, just execute the function
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def api_key_required(f):
    """
    Decorator to require API key authentication.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # In production, validate the API key against a database
        # For now, just check if it's present
        if len(api_key) < 10:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def cors_enabled(origins="*"):
    """
    Decorator to enable CORS for specific endpoints.
    
    Args:
        origins: Allowed origins (default: all)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            
            # Add CORS headers
            if hasattr(response, 'headers'):
                response.headers['Access-Control-Allow-Origin'] = origins
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key'
            
            return response
        
        return decorated_function
    return decorator