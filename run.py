"""
Entry point for running the Flask application
"""
from app import create_app, create_celery_app

# Create the app using the proper factory function from app/__init__.py
app = create_app()

# Configure Celery if needed
celery = create_celery_app(app)

if __name__ == "__main__":
    app.run()