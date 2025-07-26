#!/usr/bin/env python3
"""
Script para crear y monitorear un libro completo usando Flask context
"""

import sys
import os
import time
import json
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.book_generation import BookGeneration, BookStatus
from app.tasks.book_generation import generate_book_architecture_task

def print_separator(title: str):
    """Imprime un separador de sección"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def create_test_book():
    """Crea un libro de prueba"""
    print("🚀 Creando libro de prueba...")
    
    # Buscar usuario
    user = User.query.filter_by(email='maria.garcia@example.com').first()
    if not user:
        print("❌ Usuario no encontrado")
        return None
    
    # Parámetros del libro
    book_params = {
        "title": "Como asegurar mi aprendizaje aleman escuchando y hablando cuando no tengo amigos alemanes ni austriacos",
        "genre": "self_help",
        "target_audience": "Adultos que estudian alemán",
        "tone": "práctico y motivador",
        "key_topics": "técnicas de escucha, conversación autodidacta, recursos online, práctica oral",
        "chapter_count": 8,
        "page_count": 50,
        "format_size": "pocket",
        "line_spacing": "medium",
        "language": "es",
        "additional_instructions": "Incluir ejercicios prácticos y recursos específicos para hispanohablantes",
        "include_toc": True,
        "include_introduction": True,
        "include_conclusion": True,
        "writing_style": "directo y práctico con ejemplos concretos"
    }
    
    # Crear libro
    book = BookGeneration(
        user_id=user.id,
        **book_params
    )
    
    db.session.add(book)
    db.session.commit()
    
    print(f"✅ Libro creado con ID: {book.id}")
    print(f"📖 Título: {book.title}")
    print(f"👤 Usuario: {user.email}")
    print(f"📊 Estado: {book.status.value}")
    
    return book

def start_book_generation(book):
    """Inicia la generación del libro"""
    print(f"\n🎯 Iniciando generación de arquitectura para libro ID: {book.id}")
    
    # Enviar tarea para generar arquitectura
    task = generate_book_architecture_task.delay(book.id)
    
    print(f"🔄 Tarea de arquitectura enviada: {task.id}")
    
    # Actualizar task_id en el libro
    book.task_id = task.id
    book.status = BookStatus.QUEUED
    db.session.commit()
    
    return task

def monitor_book_progress(book_id, max_minutes=30):
    """Monitorea el progreso del libro"""
    print(f"\n👀 Monitoreando progreso del libro ID: {book_id}")
    print(f"⏰ Tiempo máximo de espera: {max_minutes} minutos")
    
    start_time = time.time()
    last_status = None
    check_count = 0
    
    while time.time() - start_time < max_minutes * 60:
        check_count += 1
        
        # Refrescar el libro desde la base de datos
        book = BookGeneration.query.get(book_id)
        
        if book.status != last_status:
            elapsed = int(time.time() - start_time)
            print(f"\n📊 [Check #{check_count}] Estado: {book.status.value} (⏱️ {elapsed}s)")
            print(f"   Progreso: {book.progress}%")
            print(f"   Paso actual: {book.current_step}")
            
            if book.error_message:
                print(f"   ❌ Error: {book.error_message}")
            
            if book.task_id:
                print(f"   🔄 Task ID: {book.task_id}")
            
            last_status = book.status
        
        # Verificar si está completado o falló
        if book.status in [BookStatus.COMPLETED, BookStatus.FAILED]:
            print(f"\n🏁 Generación finalizada con estado: {book.status.value}")
            return book
        
        # Verificar si está esperando revisión de arquitectura
        if book.status == BookStatus.ARCHITECTURE_REVIEW:
            print(f"\n⏸️  Libro esperando revisión de arquitectura")
            print(f"   En un flujo normal, el usuario aprobaría la arquitectura aquí")
            print(f"   Para la prueba, vamos a aprobar automáticamente...")
            
            # Aprobar arquitectura automáticamente para la prueba
            book.approve_architecture()
            print(f"   ✅ Arquitectura aprobada automáticamente")
            continue
        
        # Esperar antes del siguiente check
        time.sleep(10)
    
    print(f"\n⏰ Tiempo máximo alcanzado ({max_minutes} minutos)")
    return book

def show_book_results(book):
    """Muestra los resultados finales del libro"""
    print_separator("RESULTADOS FINALES")
    
    # Refrescar datos del libro
    db.session.refresh(book)
    
    print(f"📖 Título: {book.title}")
    print(f"📊 Estado final: {book.status.value}")
    print(f"📈 Progreso: {book.progress}%")
    
    if book.is_completed:
        print(f"✅ ¡Libro completado exitosamente!")
        print(f"📄 Páginas finales: {book.final_pages or 'N/A'}")
        print(f"🔤 Palabras finales: {book.final_words or 'N/A'}")
        print(f"⏱️  Tiempo de procesamiento: {book.processing_time or 0:.1f}s")
        print(f"🏷️  Tokens usados: {book.total_tokens}")
        print(f"💰 Costo estimado: ${book.estimated_cost}")
        
        # Mostrar formatos disponibles
        if book.file_formats:
            print(f"📂 Formatos disponibles: {', '.join(book.file_formats)}")
        
        # Mostrar contenido parcial si existe
        if book.content and len(book.content) > 0:
            content_preview = book.content[:500] if len(book.content) > 500 else book.content
            print(f"\n📝 Vista previa del contenido:")
            print(f"{'─'*50}")
            print(content_preview)
            if len(book.content) > 500:
                print("... (contenido truncado)")
            print(f"{'─'*50}")
    
    elif book.is_failed:
        print(f"❌ Libro falló")
        print(f"💬 Error: {book.error_message or 'Error desconocido'}")
        print(f"🔄 Reintentos: {book.retry_count}/{book.max_retries}")
    
    else:
        print(f"⏸️  Libro en estado: {book.status.value}")
        print(f"📝 Paso actual: {book.current_step}")

def main():
    """Función principal"""
    print_separator("PRUEBA COMPLETA DE GENERACIÓN DE LIBROS - BUKO AI")
    print(f"🕒 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Crear aplicación Flask
    app = create_app('development')
    
    with app.app_context():
        try:
            # 1. Crear libro de prueba
            book = create_test_book()
            if not book:
                return
            
            # 2. Iniciar generación
            task = start_book_generation(book)
            
            # 3. Monitorear progreso
            final_book = monitor_book_progress(book.id, max_minutes=30)
            
            # 4. Mostrar resultados
            show_book_results(final_book)
            
            print(f"\n🕒 Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"\n❌ Error durante la prueba: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()