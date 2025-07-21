#!/usr/bin/env python
"""
Script para procesar un libro manualmente sin usar Celery.
Solución temporal mientras se arregla el problema del registro de tareas.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.book_generation import BookGeneration
from app.tasks.book_generation import generate_book_task


def process_book_manually(book_id):
    """Procesa un libro manualmente sin usar Celery"""
    app = create_app()
    
    with app.app_context():
        # Verificar que el libro existe
        book = BookGeneration.query.get(book_id)
        if not book:
            print(f"❌ Libro con ID {book_id} no encontrado")
            return False
            
        print(f"📚 Procesando libro '{book.title}' (ID: {book_id})")
        print(f"📊 Estado actual: {book.status}")
        
        # Llamar directamente a la función de generación
        try:
            result = generate_book_task(book_id)
            print(f"✅ Resultado: {result}")
            return True
        except Exception as e:
            print(f"❌ Error procesando libro: {str(e)}")
            return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python process_book_manually.py <book_id>")
        sys.exit(1)
    
    try:
        book_id = int(sys.argv[1])
        success = process_book_manually(book_id)
        sys.exit(0 if success else 1)
    except ValueError:
        print("Error: El book_id debe ser un número entero")
        sys.exit(1)