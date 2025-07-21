"""
Punto de entrada principal para Buko AI
"""

import os
from app import create_app, create_celery_app

# Crear la aplicación usando la factory function
app = create_app()

# Configurar Celery
celery = create_celery_app(app)

# Importar tareas para que se registren con @shared_task
from app.tasks import book_generation, email_tasks

# Exponer la instancia de Celery para que el worker pueda acceder
import app as app_module
app_module.celery = celery

if __name__ == "__main__":
    """
    Punto de entrada para desarrollo directo
    """
    # Configurar variables de entorno por defecto
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