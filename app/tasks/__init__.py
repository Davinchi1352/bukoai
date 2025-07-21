"""
Inicialización del módulo de tareas de Celery.
"""

# Importar todas las tareas para que Celery las registre automáticamente
# Usando el decorador @shared_task y imports directos

# Importar tareas de generación de libros
from .book_generation import generate_book_task, send_book_completion_email, update_book_generation_stats

# Importar tareas de email
from .email_tasks import (
    send_email_task, 
    send_template_email, 
    send_welcome_email, 
    send_password_reset_email, 
    send_subscription_confirmation_email, 
    send_bulk_email
)

# Importar otros módulos de tareas si existen
try:
    from . import payment_tasks
    from . import cleanup_tasks
except ImportError:
    # Los módulos opcionales no están disponibles
    pass

# Función legacy para compatibilidad
def register_tasks(celery_app=None):
    """Función legacy para registro de tareas (ya no necesaria con @shared_task)"""
    import logging
    logging.info("Task registration using @shared_task decorators - no explicit registration needed")
    
    # Lista de tareas que deberían estar disponibles
    expected_tasks = [
        'app.tasks.book_generation.generate_book_task',
        'app.tasks.book_generation.send_book_completion_email',
        'app.tasks.book_generation.update_book_generation_stats',
        'app.tasks.email_tasks.send_email_task',
        'app.tasks.email_tasks.send_template_email',
        'app.tasks.email_tasks.send_welcome_email',
        'app.tasks.email_tasks.send_password_reset_email',
        'app.tasks.email_tasks.send_subscription_confirmation_email',
        'app.tasks.email_tasks.send_bulk_email',
    ]
    
    logging.info(f"Expected tasks: {expected_tasks}")
    
    if celery_app:
        available_tasks = list(celery_app.tasks.keys())
        logging.info(f"Available tasks: {available_tasks}")
        
        # Verificar que las tareas estén registradas
        for task_name in expected_tasks:
            if task_name in celery_app.tasks:
                logging.info(f"✓ Task {task_name} is registered")
            else:
                logging.warning(f"✗ Task {task_name} is NOT registered")
    
    return True