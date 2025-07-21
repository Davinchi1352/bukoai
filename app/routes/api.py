"""
Rutas de API (placeholder para futuras épicas).
"""
from flask import Blueprint, jsonify

bp = Blueprint('api', __name__)


@bp.route('/status')
def api_status():
    """Status de API."""
    return jsonify({
        'message': 'API system ready',
        'status': 'placeholder',
        'endpoints': []
    })