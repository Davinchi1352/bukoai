"""
Rutas principales de la aplicación.
"""
from flask import Blueprint, render_template, jsonify

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Página principal."""
    return render_template('index.html')


@bp.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'buko-ai',
        'timestamp': '2025-01-17'
    })


@bp.route('/features')
def features():
    """Características del producto."""
    return jsonify({
        'message': 'Features page',
        'status': 'active'
    })


@bp.route('/pricing')
def pricing():
    """Precios del producto."""
    return jsonify({
        'message': 'Pricing page',
        'status': 'active'
    })


@bp.route('/dashboard')
def dashboard():
    """Dashboard del usuario."""
    return jsonify({
        'message': 'Dashboard page',
        'status': 'active'
    })


@bp.route('/my-books')
def my_books():
    """Mis libros."""
    return jsonify({
        'message': 'My Books page',
        'status': 'active'
    })


@bp.route('/generate-book')
def generate_book():
    """Generar libro."""
    return jsonify({
        'message': 'Generate Book page',
        'status': 'active'
    })


@bp.route('/subscription')
def subscription():
    """Suscripción."""
    return jsonify({
        'message': 'Subscription page',
        'status': 'active'
    })


@bp.route('/api-docs')
def api_docs():
    """Documentación API."""
    return jsonify({
        'message': 'API Documentation page',
        'status': 'active'
    })


@bp.route('/about')
def about():
    """Acerca de."""
    return jsonify({
        'message': 'About page',
        'status': 'active'
    })


@bp.route('/contact')
def contact():
    """Contacto."""
    return jsonify({
        'message': 'Contact page',
        'status': 'active'
    })


@bp.route('/blog')
def blog():
    """Blog."""
    return jsonify({
        'message': 'Blog page',
        'status': 'active'
    })


@bp.route('/help')
def help():
    """Centro de ayuda."""
    return jsonify({
        'message': 'Help page',
        'status': 'active'
    })


@bp.route('/faq')
def faq():
    """Preguntas frecuentes."""
    return jsonify({
        'message': 'FAQ page',
        'status': 'active'
    })


@bp.route('/status')
def status():
    """Estado del sistema."""
    return jsonify({
        'message': 'System Status page',
        'status': 'active'
    })


@bp.route('/privacy')
def privacy():
    """Política de privacidad."""
    return jsonify({
        'message': 'Privacy Policy page',
        'status': 'active'
    })


@bp.route('/terms')
def terms():
    """Términos y condiciones."""
    return jsonify({
        'message': 'Terms of Service page',
        'status': 'active'
    })


@bp.route('/cookies')
def cookies():
    """Política de cookies."""
    return jsonify({
        'message': 'Cookie Policy page',
        'status': 'active'
    })