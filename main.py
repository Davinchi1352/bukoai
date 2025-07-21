"""
Buko AI - Aplicación principal
"""

import os
from datetime import datetime

from flask import Flask, jsonify
from flask_migrate import Migrate

from config import configure_app
from app.models import db, init_db


def create_app(config_name=None):
    """
    Factory de aplicación Flask
    
    Args:
        config_name (str): Nombre de la configuración (development, testing, staging, production)
        
    Returns:
        Flask: Instancia de la aplicación configurada
    """
    app = Flask(__name__)
    
    # Configurar la aplicación
    configure_app(app, config_name)
    
    # Inicializar base de datos
    db.init_app(app)
    
    # Configurar Flask-Migrate
    migrate = Migrate(app, db)
    
    # Registrar blueprints aquí cuando estén disponibles
    # from app.routes import main_bp
    # app.register_blueprint(main_bp)
    
    # Ruta temporal para verificar que la aplicación funciona
    @app.route("/")
    def index():
        return jsonify({
            "message": "Buko AI API",
            "version": "0.1.0",
            "status": "healthy",
            "environment": app.config.get("FLASK_ENV", "development"),
            "features": {
                "cover_generation": app.config.get("FEATURE_COVER_GENERATION", False),
                "epub_export": app.config.get("FEATURE_EPUB_EXPORT", False),
                "docx_export": app.config.get("FEATURE_DOCX_EXPORT", False),
                "collaboration": app.config.get("FEATURE_COLLABORATION", False),
                "api_access": app.config.get("FEATURE_API_ACCESS", False),
                "referral_program": app.config.get("FEATURE_REFERRAL_PROGRAM", False),
            }
        })
    
    @app.route("/health")
    def health_check():
        """Endpoint de salud para monitoreo"""
        # Verificar conexión a base de datos
        try:
            db.session.execute("SELECT 1")
            db_status = "connected"
        except Exception:
            db_status = "disconnected"
        
        # Verificar Redis (implementar después)
        redis_status = "connected"
        
        # Verificar Claude API (implementar después)
        claude_status = "available"
        
        return jsonify({
            "status": "healthy" if db_status == "connected" else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "0.1.0",
            "database": db_status,
            "redis": redis_status,
            "claude_api": claude_status
        })
    
    @app.route("/api/v1/info")
    def api_info():
        """Información de la API"""
        return jsonify({
            "api_version": "1.0",
            "name": "Buko AI API",
            "description": "API para generación de libros con IA",
            "endpoints": {
                "health": "/health",
                "generate_book": "/api/v1/books/generate",
                "user_books": "/api/v1/books",
                "subscription": "/api/v1/subscription",
                "auth": "/api/v1/auth"
            },
            "authentication": "Bearer token required",
            "rate_limits": {
                "book_generation": "5 per minute",
                "api_calls": "1000 per hour"
            }
        })
    
    return app


# Crear instancia de la aplicación
app = create_app()


if __name__ == "__main__":
    """
    Punto de entrada principal para desarrollo
    """
    # Configurar variables de entorno por defecto
    os.environ.setdefault("FLASK_APP", "app.py")
    os.environ.setdefault("FLASK_ENV", "development")
    
    # Obtener configuración del entorno
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    # Mostrar información de inicio
    print(f"🚀 Iniciando Buko AI en modo {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🌐 Servidor disponible en: http://{host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    
    # Iniciar la aplicación
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )