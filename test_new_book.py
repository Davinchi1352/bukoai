#!/usr/bin/env python3
"""
Script para crear un nuevo libro y verificar que el fix de parámetros funciona.
"""

import sys
import os
sys.path.append('/home/davinchi/bukoai')

from app import create_app, db
from app.models.book_generation import BookGeneration, BookStatus
from app.models.user import User
from app.tasks.book_generation import generate_book_task

def create_test_book():
    """Crear un libro de prueba con el fix aplicado"""
    app = create_app()
    
    with app.app_context():
        # Obtener usuario ID 1
        user = User.query.get(1)
        if not user:
            print("Error: Usuario ID 1 no encontrado")
            return None
            
        # Crear nuevo libro
        book = BookGeneration(
            user_id=user.id,
            title="Python Avanzado - Testing Fix",
            genre="technical",
            target_audience="developers",
            tone="professional",
            key_topics="Programación avanzada en Python: decoradores, context managers, metaclasses, async/await",
            chapter_count=6,
            page_count=35,
            format_size="pocket",
            line_spacing="medium",
            language="es",
            additional_instructions="Incluir ejemplos avanzados y mejores prácticas",
            writing_style="Professional and engaging",
            include_toc=True,
            include_introduction=True,
            include_conclusion=True
        )
        
        db.session.add(book)
        db.session.commit()
        
        print(f"✅ Libro creado con ID: {book.id}")
        print(f"   UUID: {book.uuid}")
        print(f"   Título: {book.title}")
        print(f"   Estado: {book.status}")
        
        # Enviar a la cola para procesamiento
        task = generate_book_task.delay(book.id)
        book.task_id = task.id
        db.session.commit()
        
        print(f"✅ Tarea enviada a la cola: {task.id}")
        
        return book.id, book.uuid

if __name__ == "__main__":
    book_id, book_uuid = create_test_book()
    print(f"\n🔗 URL de monitoreo: http://localhost:5001/books/generation/{book_id}")
    print(f"📋 Verificar en: http://localhost:5001/books/generation/{book_uuid}")