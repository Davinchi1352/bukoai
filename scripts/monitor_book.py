#!/usr/bin/env python
"""
Script para monitorear el progreso de generación de un libro
"""

import sys
import os
import time
from datetime import datetime, timezone

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.book_generation import BookGeneration


def monitor_book(book_id):
    """Monitorea el progreso de un libro"""
    app = create_app()
    
    with app.app_context():
        book = BookGeneration.query.get(book_id)
        if not book:
            print(f"❌ Libro con ID {book_id} no encontrado")
            return
        
        now = datetime.now(timezone.utc)
        elapsed = (now - book.started_at).total_seconds() if book.started_at else 0
        
        print(f"📚 Libro: {book.title}")
        print(f"📊 Estado: {book.status}")
        print(f"⏰ Tiempo transcurrido: {int(elapsed//60)}m {int(elapsed%60)}s")
        print(f"📄 Contenido generado: {'Sí' if book.content else 'No'}")
        print(f"🔄 Tokens procesados: {book.total_tokens or 0}")
        print(f"💰 Costo estimado: ${book.estimated_cost or 0}")
        print(f"❌ Error: {book.error_message or 'Ninguno'}")
        print(f"📖 Páginas finales: {book.final_pages or 'N/A'}")
        print(f"📝 Palabras finales: {book.final_words or 'N/A'}")
        print(f"📅 Iniciado: {book.started_at.strftime('%H:%M:%S') if book.started_at else 'N/A'}")
        print(f"✅ Completado: {book.completed_at.strftime('%H:%M:%S') if book.completed_at else 'N/A'}")
        
        # Mostrar contenido si está disponible
        if book.content:
            content_length = len(book.content)
            print(f"📄 Longitud del contenido: {content_length} caracteres")
            if content_length > 100:
                print(f"📝 Inicio del contenido: {book.content[:100]}...")
        
        return book.status


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python monitor_book.py <book_id>")
        sys.exit(1)
    
    try:
        book_id = int(sys.argv[1])
        status = monitor_book(book_id)
        print(f"\n🔍 Estado actual: {status}")
    except ValueError:
        print("Error: El book_id debe ser un número entero")
        sys.exit(1)