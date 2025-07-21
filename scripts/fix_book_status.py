#!/usr/bin/env python
"""
Script para corregir el estado del libro ID 26 y marcarlo como completado
"""

import sys
import os
from datetime import datetime, timezone

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.book_generation import BookGeneration, BookStatus


def fix_book_status(book_id):
    """Corrige el estado del libro y lo marca como completado"""
    app = create_app()
    
    with app.app_context():
        # Obtener el libro
        book = BookGeneration.query.get(book_id)
        if not book:
            print(f"❌ Libro con ID {book_id} no encontrado")
            return False
        
        print(f"📚 Libro: {book.title}")
        print(f"📊 Estado actual: {book.status}")
        print(f"📄 Contenido: {'Sí' if book.content else 'No'}")
        print(f"📝 Palabras: {book.final_words}")
        print(f"📖 Páginas: {book.final_pages}")
        print(f"🔄 Tokens: {book.total_tokens}")
        
        # Si el libro tiene contenido y está marcado como fallido, corregirlo
        if book.content and book.status == BookStatus.FAILED:
            print("\n🔧 Corrigiendo estado del libro...")
            
            # Actualizar estado
            book.status = BookStatus.COMPLETED
            book.error_message = None
            
            # Asegurar que tiene completed_at
            if not book.completed_at:
                book.completed_at = datetime.now(timezone.utc)
            
            # Commit los cambios
            db.session.commit()
            
            print("✅ Estado del libro corregido exitosamente")
            print(f"📊 Nuevo estado: {book.status}")
            print(f"⏰ Tiempo de procesamiento: {book.processing_time:.2f} segundos")
            
            return True
        else:
            print("ℹ️ El libro no necesita corrección")
            return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python fix_book_status.py <book_id>")
        sys.exit(1)
    
    try:
        book_id = int(sys.argv[1])
        success = fix_book_status(book_id)
        sys.exit(0 if success else 1)
    except ValueError:
        print("Error: El book_id debe ser un número entero")
        sys.exit(1)