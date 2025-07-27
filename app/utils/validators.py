"""
Validation utilities for Buko AI.
"""

import re
from typing import Dict, Any, List


def validate_book_parameters(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate book generation parameters.
    
    Args:
        data: Dictionary containing book parameters
        
    Returns:
        Dictionary with validation result and errors
    """
    errors = []
    
    # Required fields
    if not data.get('title'):
        errors.append('Title is required')
    elif len(data['title'].strip()) < 3:
        errors.append('Title must be at least 3 characters long')
    elif len(data['title']) > 500:
        errors.append('Title must be less than 500 characters')
    
    # Optional but validated fields
    if data.get('genre') and len(data['genre']) > 100:
        errors.append('Genre must be less than 100 characters')
    
    if data.get('target_audience') and len(data['target_audience']) > 200:
        errors.append('Target audience must be less than 200 characters')
    
    if data.get('tone') and len(data['tone']) > 100:
        errors.append('Tone must be less than 100 characters')
    
    if data.get('key_topics') and len(data['key_topics']) > 1000:
        errors.append('Key topics must be less than 1000 characters')
    
    if data.get('additional_instructions') and len(data['additional_instructions']) > 2000:
        errors.append('Additional instructions must be less than 2000 characters')
    
    if data.get('writing_style') and len(data['writing_style']) > 200:
        errors.append('Writing style must be less than 200 characters')
    
    # Numeric validations
    chapter_count = data.get('chapter_count', 10)
    if not isinstance(chapter_count, int) or chapter_count < 1 or chapter_count > 50:
        errors.append('Chapter count must be between 1 and 50')
    
    page_count = data.get('page_count', 50)
    if not isinstance(page_count, int) or page_count < 5 or page_count > 500:
        errors.append('Page count must be between 5 and 500')
    
    # Format size validation
    format_size = data.get('format_size', 'A4')
    valid_formats = ['A4', 'A5', 'Letter', 'Legal']
    if format_size not in valid_formats:
        errors.append(f'Format size must be one of: {", ".join(valid_formats)}')
    
    # Language validation
    language = data.get('language', 'es')
    valid_languages = ['es', 'en', 'de']
    if language not in valid_languages:
        errors.append(f'Language must be one of: {", ".join(valid_languages)}')
    
    # Boolean validations
    boolean_fields = ['include_toc', 'include_introduction', 'include_conclusion']
    for field in boolean_fields:
        if field in data and not isinstance(data[field], bool):
            errors.append(f'{field} must be a boolean value')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> Dict[str, Any]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Dictionary with validation result and requirements
    """
    errors = []
    
    if not password:
        errors.append('Password is required')
        return {'valid': False, 'errors': errors}
    
    if len(password) < 8:
        errors.append('Password must be at least 8 characters long')
    
    if len(password) > 128:
        errors.append('Password must be less than 128 characters')
    
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter')
    
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter')
    
    if not re.search(r'\d', password):
        errors.append('Password must contain at least one number')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Password must contain at least one special character')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'strength': _calculate_password_strength(password)
    }


def _calculate_password_strength(password: str) -> str:
    """
    Calculate password strength.
    
    Args:
        password: Password to evaluate
        
    Returns:
        Password strength level: 'weak', 'medium', 'strong'
    """
    score = 0
    
    # Length
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    
    # Character types
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'\d', password):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    
    # Complexity
    if len(set(password)) >= len(password) * 0.7:  # Good character diversity
        score += 1
    
    if score <= 3:
        return 'weak'
    elif score <= 5:
        return 'medium'
    else:
        return 'strong'


def validate_user_registration(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate user registration data.
    
    Args:
        data: Registration data
        
    Returns:
        Dictionary with validation result and errors
    """
    errors = []
    
    # Email validation
    email = data.get('email', '').strip().lower()
    if not email:
        errors.append('Email is required')
    elif not validate_email(email):
        errors.append('Invalid email format')
    
    # Password validation
    password = data.get('password', '')
    password_validation = validate_password(password)
    if not password_validation['valid']:
        errors.extend(password_validation['errors'])
    
    # Name validations
    first_name = data.get('first_name', '').strip()
    if not first_name:
        errors.append('First name is required')
    elif len(first_name) < 2:
        errors.append('First name must be at least 2 characters long')
    elif len(first_name) > 50:
        errors.append('First name must be less than 50 characters')
    elif not re.match(r'^[a-zA-ZàáâäçéêëíîïñóôöúûüýÿÀÁÂÄÇÉÊËÍÎÏÑÓÔÖÚÛÜÝŸ\s\'-]+$', first_name):
        errors.append('First name contains invalid characters')
    
    last_name = data.get('last_name', '').strip()
    if not last_name:
        errors.append('Last name is required')
    elif len(last_name) < 2:
        errors.append('Last name must be at least 2 characters long')
    elif len(last_name) > 50:
        errors.append('Last name must be less than 50 characters')
    elif not re.match(r'^[a-zA-ZàáâäçéêëíîïñóôöúûüýÿÀÁÂÄÇÉÊËÍÎÏÑÓÔÖÚÛÜÝŸ\s\'-]+$', last_name):
        errors.append('Last name contains invalid characters')
    
    # Terms acceptance
    if not data.get('accept_terms'):
        errors.append('You must accept the terms and conditions')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_user_profile_update(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate user profile update data.
    
    Args:
        data: Profile update data
        
    Returns:
        Dictionary with validation result and errors
    """
    errors = []
    
    # Optional email validation
    if 'email' in data:
        email = data['email'].strip().lower()
        if email and not validate_email(email):
            errors.append('Invalid email format')
    
    # Optional name validations
    if 'first_name' in data:
        first_name = data['first_name'].strip()
        if first_name:
            if len(first_name) < 2:
                errors.append('First name must be at least 2 characters long')
            elif len(first_name) > 50:
                errors.append('First name must be less than 50 characters')
            elif not re.match(r'^[a-zA-ZàáâäçéêëíîïñóôöúûüýÿÀÁÂÄÇÉÊËÍÎÏÑÓÔÖÚÛÜÝŸ\s\'-]+$', first_name):
                errors.append('First name contains invalid characters')
    
    if 'last_name' in data:
        last_name = data['last_name'].strip()
        if last_name:
            if len(last_name) < 2:
                errors.append('Last name must be at least 2 characters long')
            elif len(last_name) > 50:
                errors.append('Last name must be less than 50 characters')
            elif not re.match(r'^[a-zA-ZàáâäçéêëíîïñóôöúûüýÿÀÁÂÄÇÉÊËÍÎÏÑÓÔÖÚÛÜÝŸ\s\'-]+$', last_name):
                errors.append('Last name contains invalid characters')
    
    # Optional bio validation
    if 'bio' in data and data['bio']:
        if len(data['bio']) > 500:
            errors.append('Bio must be less than 500 characters')
    
    # Optional website validation
    if 'website' in data and data['website']:
        website = data['website'].strip()
        if not re.match(r'^https?://.+\..+', website):
            errors.append('Website must be a valid URL')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_payment_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate payment data.
    
    Args:
        data: Payment data
        
    Returns:
        Dictionary with validation result and errors
    """
    errors = []
    
    # Amount validation
    amount = data.get('amount')
    if not amount:
        errors.append('Amount is required')
    elif not isinstance(amount, (int, float)) or amount <= 0:
        errors.append('Amount must be a positive number')
    elif amount > 10000:  # Max $10,000
        errors.append('Amount cannot exceed $10,000')
    
    # Currency validation
    currency = data.get('currency', '').upper()
    valid_currencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD']
    if currency and currency not in valid_currencies:
        errors.append(f'Currency must be one of: {", ".join(valid_currencies)}')
    
    # Payment method validation
    payment_method = data.get('payment_method')
    valid_methods = ['card', 'paypal', 'bank_transfer']
    if payment_method and payment_method not in valid_methods:
        errors.append(f'Payment method must be one of: {", ".join(valid_methods)}')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path separators and other dangerous characters
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_length = 255 - len(ext) - 1 if ext else 255
        filename = name[:max_name_length] + ('.' + ext if ext else '')
    
    # Ensure it's not empty
    if not filename:
        filename = 'file'
    
    return filename


def validate_file_upload(file_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate file upload data.
    
    Args:
        file_data: File upload data
        
    Returns:
        Dictionary with validation result and errors
    """
    errors = []
    
    # File size validation (in bytes)
    max_size = 10 * 1024 * 1024  # 10MB
    file_size = file_data.get('size', 0)
    if file_size > max_size:
        errors.append(f'File size cannot exceed {max_size // (1024 * 1024)}MB')
    
    # File type validation
    filename = file_data.get('filename', '')
    if filename:
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.docx', '.doc']
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        if f'.{file_ext}' not in allowed_extensions:
            errors.append(f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def validate_search_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate search parameters.
    
    Args:
        params: Search parameters
        
    Returns:
        Dictionary with validation result and errors
    """
    errors = []
    
    # Query validation
    query = params.get('query', '').strip()
    if query and len(query) < 2:
        errors.append('Search query must be at least 2 characters long')
    elif query and len(query) > 200:
        errors.append('Search query must be less than 200 characters')
    
    # Pagination validation
    page = params.get('page', 1)
    if not isinstance(page, int) or page < 1:
        errors.append('Page must be a positive integer')
    elif page > 1000:
        errors.append('Page cannot exceed 1000')
    
    limit = params.get('limit', 20)
    if not isinstance(limit, int) or limit < 1:
        errors.append('Limit must be a positive integer')
    elif limit > 100:
        errors.append('Limit cannot exceed 100')
    
    # Sort validation
    sort_by = params.get('sort_by')
    if sort_by:
        valid_sorts = ['created_at', 'updated_at', 'title', 'status']
        if sort_by not in valid_sorts:
            errors.append(f'Sort field must be one of: {", ".join(valid_sorts)}')
    
    sort_order = params.get('sort_order', 'desc')
    if sort_order not in ['asc', 'desc']:
        errors.append('Sort order must be "asc" or "desc"')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }