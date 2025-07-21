#!/usr/bin/env python3
"""
Script para probar la configuración de Celery.
"""
import os
import sys
from flask import Flask

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, create_celery_app

def test_celery_configuration():
    """Prueba la configuración de Celery."""
    print("=== Prueba de Configuración de Celery ===")
    
    # Crear aplicación Flask
    print("1. Creando aplicación Flask...")
    app = create_app('development')
    
    with app.app_context():
        print("2. Creando aplicación Celery...")
        celery_app = create_celery_app(app)
        
        print("3. Configuración de Celery:")
        print(f"   - Broker URL: {celery_app.conf.broker_url}")
        print(f"   - Result Backend: {celery_app.conf.result_backend}")
        print(f"   - Task Serializer: {celery_app.conf.task_serializer}")
        print(f"   - Accept Content: {celery_app.conf.accept_content}")
        
        print("4. Probando conexión al broker...")
        try:
            # Inspeccionar el broker
            inspector = celery_app.control.inspect()
            stats = inspector.stats()
            if stats:
                print("   ✓ Conexión al broker exitosa")
                print(f"   - Workers activos: {len(stats)}")
            else:
                print("   ⚠ No hay workers activos")
        except Exception as e:
            print(f"   ✗ Error conectando al broker: {e}")
        
        print("5. Tareas registradas:")
        for task_name in celery_app.tasks:
            if not task_name.startswith('celery.'):
                print(f"   - {task_name}")
        
        print("6. Probando tarea simple...")
        try:
            from app.tasks.email_tasks import send_email_task
            
            # Crear tarea de prueba (no se ejecutará sin worker)
            result = send_email_task.apply_async(
                args=['Test Subject', 'test@example.com', 'Test body'],
                countdown=1
            )
            print(f"   ✓ Tarea creada con ID: {result.id}")
            print(f"   - Estado: {result.state}")
            
        except Exception as e:
            print(f"   ✗ Error creando tarea: {e}")
    
    print("\n=== Prueba Completada ===")

if __name__ == '__main__':
    test_celery_configuration()