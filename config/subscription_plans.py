"""
Subscription plans configuration for Buko AI.
"""

# Subscription plans with their features and limits
SUBSCRIPTION_PLANS = {
    'free': {
        'name': 'Plan Gratuito',
        'books_per_month': 1,
        'max_pages': 30,
        'max_chapters': 10,
        'formats': ['pdf', 'txt'],
        'features': [
            'Generación de libros básica',
            'Descarga en PDF y TXT',
            'Soporte por email'
        ],
        'price': 0,
        'currency': 'USD'
    },
    'starter': {
        'name': 'Plan Starter',
        'books_per_month': 5,
        'max_pages': 100,
        'max_chapters': 20,
        'formats': ['pdf', 'epub', 'docx', 'txt'],
        'features': [
            'Generación avanzada de libros',
            'Todos los formatos de descarga',
            'Personalización de estilo',
            'Soporte prioritario'
        ],
        'price': 9.99,
        'currency': 'USD'
    },
    'pro': {
        'name': 'Plan Pro',
        'books_per_month': 15,
        'max_pages': 200,
        'max_chapters': 50,
        'formats': ['pdf', 'epub', 'docx', 'txt'],
        'features': [
            'Generación profesional de libros',
            'Todos los formatos de descarga',
            'Personalización avanzada',
            'Portadas automáticas',
            'API de acceso',
            'Soporte 24/7'
        ],
        'price': 29.99,
        'currency': 'USD'
    },
    'business': {
        'name': 'Plan Business',
        'books_per_month': 50,
        'max_pages': 500,
        'max_chapters': 100,
        'formats': ['pdf', 'epub', 'docx', 'txt'],
        'features': [
            'Generación empresarial de libros',
            'Todos los formatos de descarga',
            'Personalización completa',
            'Portadas automáticas',
            'API de acceso completa',
            'Integraciones webhook',
            'Soporte dedicado',
            'Análisis y reportes'
        ],
        'price': 99.99,
        'currency': 'USD'
    },
    'enterprise': {
        'name': 'Plan Enterprise',
        'books_per_month': -1,  # Unlimited
        'max_pages': -1,        # Unlimited
        'max_chapters': -1,     # Unlimited
        'formats': ['pdf', 'epub', 'docx', 'txt'],
        'features': [
            'Generación ilimitada de libros',
            'Todos los formatos de descarga',
            'Personalización completa',
            'Portadas automáticas',
            'API de acceso completa',
            'Integraciones webhook',
            'Soporte dedicado 24/7',
            'Análisis y reportes avanzados',
            'Panel de administración',
            'Despliegue on-premise',
            'SLA garantizado'
        ],
        'price': 299.99,
        'currency': 'USD'
    }
}

# Feature matrix for easy comparison
FEATURE_MATRIX = {
    'basic_generation': ['free', 'starter', 'pro', 'business', 'enterprise'],
    'advanced_generation': ['starter', 'pro', 'business', 'enterprise'],
    'professional_generation': ['pro', 'business', 'enterprise'],
    'enterprise_generation': ['enterprise'],
    
    'pdf_format': ['free', 'starter', 'pro', 'business', 'enterprise'],
    'txt_format': ['free', 'starter', 'pro', 'business', 'enterprise'],
    'epub_format': ['starter', 'pro', 'business', 'enterprise'],
    'docx_format': ['starter', 'pro', 'business', 'enterprise'],
    
    'basic_customization': ['starter', 'pro', 'business', 'enterprise'],
    'advanced_customization': ['pro', 'business', 'enterprise'],
    'complete_customization': ['business', 'enterprise'],
    
    'automatic_covers': ['pro', 'business', 'enterprise'],
    'api_access': ['pro', 'business', 'enterprise'],
    'webhook_integrations': ['business', 'enterprise'],
    'analytics_reports': ['business', 'enterprise'],
    'admin_panel': ['enterprise'],
    'on_premise': ['enterprise'],
    'sla_guarantee': ['enterprise'],
    
    'email_support': ['free', 'starter', 'pro', 'business', 'enterprise'],
    'priority_support': ['starter', 'pro', 'business', 'enterprise'],
    'support_24_7': ['pro', 'business', 'enterprise'],
    'dedicated_support': ['business', 'enterprise']
}

# Pricing configuration
PRICING_CONFIG = {
    'currencies': ['USD', 'EUR', 'GBP'],
    'default_currency': 'USD',
    'billing_cycles': ['monthly', 'yearly'],
    'yearly_discount': 0.20,  # 20% discount for yearly billing
    'tax_rates': {
        'US': 0.08,
        'EU': 0.21,
        'UK': 0.20,
        'default': 0.0
    }
}

# Usage limits and restrictions
USAGE_LIMITS = {
    'free': {
        'api_requests_per_hour': 10,
        'concurrent_generations': 1,
        'queue_priority': 0
    },
    'starter': {
        'api_requests_per_hour': 100,
        'concurrent_generations': 2,
        'queue_priority': 1
    },
    'pro': {
        'api_requests_per_hour': 500,
        'concurrent_generations': 3,
        'queue_priority': 2
    },
    'business': {
        'api_requests_per_hour': 2000,
        'concurrent_generations': 5,
        'queue_priority': 3
    },
    'enterprise': {
        'api_requests_per_hour': -1,  # Unlimited
        'concurrent_generations': -1,  # Unlimited
        'queue_priority': 4
    }
}


def get_plan_details(plan_type):
    """
    Get details for a specific subscription plan.
    
    Args:
        plan_type: The plan type (free, starter, pro, business, enterprise)
        
    Returns:
        Dictionary with plan details or None if plan doesn't exist
    """
    return SUBSCRIPTION_PLANS.get(plan_type)


def get_plan_price(plan_type, billing_cycle='monthly', currency='USD'):
    """
    Get the price for a plan with billing cycle and currency.
    
    Args:
        plan_type: The plan type
        billing_cycle: 'monthly' or 'yearly'
        currency: Currency code
        
    Returns:
        Price as float or None if plan doesn't exist
    """
    plan = get_plan_details(plan_type)
    if not plan:
        return None
    
    base_price = plan['price']
    
    if billing_cycle == 'yearly':
        # Apply yearly discount
        base_price *= 12 * (1 - PRICING_CONFIG['yearly_discount'])
    
    # TODO: Add currency conversion logic here
    # For now, return the price in USD
    return base_price


def user_has_feature(user_subscription_type, feature_name):
    """
    Check if a user's subscription includes a specific feature.
    
    Args:
        user_subscription_type: User's subscription type
        feature_name: Feature to check
        
    Returns:
        Boolean indicating if user has access to the feature
    """
    allowed_plans = FEATURE_MATRIX.get(feature_name, [])
    return user_subscription_type in allowed_plans


def get_usage_limits(plan_type):
    """
    Get usage limits for a subscription plan.
    
    Args:
        plan_type: The plan type
        
    Returns:
        Dictionary with usage limits
    """
    return USAGE_LIMITS.get(plan_type, USAGE_LIMITS['free'])


def get_all_plans():
    """
    Get all available subscription plans.
    
    Returns:
        Dictionary with all plans
    """
    return SUBSCRIPTION_PLANS


def compare_plans(plan_types=None):
    """
    Get a comparison matrix of subscription plans.
    
    Args:
        plan_types: List of plan types to compare (default: all)
        
    Returns:
        Dictionary with plan comparison data
    """
    if plan_types is None:
        plan_types = list(SUBSCRIPTION_PLANS.keys())
    
    comparison = {}
    
    for plan_type in plan_types:
        plan = get_plan_details(plan_type)
        if plan:
            comparison[plan_type] = {
                'name': plan['name'],
                'price': plan['price'],
                'books_per_month': plan['books_per_month'],
                'max_pages': plan['max_pages'],
                'max_chapters': plan['max_chapters'],
                'formats': plan['formats'],
                'features': plan['features'],
                'usage_limits': get_usage_limits(plan_type)
            }
    
    return comparison