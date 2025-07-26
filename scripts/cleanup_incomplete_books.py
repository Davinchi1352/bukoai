#!/usr/bin/env python3
"""
Script para marcar como fallidos los libros que no fueron completados
"""

import sys
import os
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.book_generation import BookGeneration, BookStatus

def cleanup_incomplete_books():
    """Marca como fallidos todos los libros que están en estado incompleto"""
    
    # Estados que consideramos incompletos
    incomplete_statuses = [
        BookStatus.QUEUED,
        BookStatus.ARCHITECTURE_REVIEW,
        BookStatus.PROCESSING
    ]
    
    print("🧹 Limpiando libros incompletos...")
    print("=" * 60)
    
    # Buscar libros incompletos
    incomplete_books = BookGeneration.query.filter(
        BookGeneration.status.in_(incomplete_statuses)
    ).all()
    
    if not incomplete_books:
        print("✅ No hay libros incompletos para limpiar")
        return
    
    print(f"📚 Encontrados {len(incomplete_books)} libros incompletos:")
    print()
    
    # Mostrar información de los libros que se van a marcar como fallidos
    for book in incomplete_books:
        print(f"ID: {book.id}")
        print(f"   Título: {book.title}")
        print(f"   Estado actual: {book.status.value}")
        print(f"   Usuario ID: {book.user_id}")
        print(f"   Creado: {book.created_at}")
        if book.task_id:
            print(f"   Task ID: {book.task_id}")
        print()
    
    # Confirmar la acción
    confirm = input(f"¿Marcar estos {len(incomplete_books)} libros como FAILED? (s/N): ").strip().lower()
    
    if confirm not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Operación cancelada")
        return
    
    # Marcar como fallidos
    updated_count = 0
    
    for book in incomplete_books:
        old_status = book.status.value
        book.status = BookStatus.FAILED
        book.updated_at = datetime.utcnow()
        
        # Agregar información de por qué falló
        if not book.parameters:
            book.parameters = {}
        
        book.parameters['cleanup_reason'] = f"Marcado como fallido durante limpieza del sistema (estado anterior: {old_status})"
        book.parameters['cleanup_timestamp'] = datetime.utcnow().isoformat()
        
        updated_count += 1
        print(f"✅ {book.title} (ID: {book.id}) - {old_status} → FAILED")
    
    try:
        # Guardar cambios
        db.session.commit()
        print()
        print(f"🎉 ¡Limpieza completada! {updated_count} libros marcados como FAILED")
        print()
        print("📊 Resumen:")
        print(f"   - Libros procesados: {updated_count}")
        print(f"   - Estado final: FAILED")
        print(f"   - Timestamp: {datetime.utcnow()}")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al guardar cambios: {e}")
        raise

def show_current_status():
    """Muestra el estado actual de todos los libros"""
    print("📊 Estado actual de libros en el sistema:")
    print("=" * 60)
    
    # Contar libros por estado
    status_counts = {}
    for status in BookStatus:
        count = BookGeneration.query.filter(BookGeneration.status == status).count()
        if count > 0:
            status_counts[status.value] = count
    
    if not status_counts:
        print("📚 No hay libros en el sistema")
        return
    
    for status, count in status_counts.items():
        print(f"   {status.upper()}: {count} libros")
    
    total = sum(status_counts.values())
    print(f"\n📚 Total: {total} libros")

def main():
    """Función principal"""
    print("\n🔍 LIMPIEZA DE LIBROS INCOMPLETOS - BUKO AI")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Crear aplicación Flask
    app = create_app('development')
    
    with app.app_context():
        # Mostrar estado actual
        show_current_status()
        print()
        
        # Limpiar libros incompletos
        cleanup_incomplete_books()
        print()
        
        # Mostrar estado final
        print("📊 Estado después de la limpieza:")
        print("-" * 40)
        show_current_status()

if __name__ == '__main__':
    main()