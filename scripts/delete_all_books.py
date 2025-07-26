#!/usr/bin/env python3
"""
Script para eliminar todos los libros y empezar desde cero
"""

import sys
import os
import shutil
from datetime import datetime
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.book_generation import BookGeneration, BookStatus

def print_section(title: str):
    """Imprime un separador de sección"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def show_current_stats():
    """Muestra estadísticas actuales de libros"""
    print("📊 Estado actual de libros:")
    print("-" * 40)
    
    # Contar libros por estado
    status_counts = {}
    for status in BookStatus:
        count = BookGeneration.query.filter(BookGeneration.status == status).count()
        if count > 0:
            status_counts[status.value] = count
    
    if not status_counts:
        print("📚 No hay libros en el sistema")
        return 0
    
    total = 0
    for status, count in status_counts.items():
        print(f"   {status.upper()}: {count} libros")
        total += count
    
    print(f"\n📚 Total: {total} libros")
    return total

def cleanup_storage_files():
    """Limpia archivos de storage relacionados con libros"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    storage_path = os.path.join(project_root, 'storage')
    
    if not os.path.exists(storage_path):
        print("📁 No existe directorio storage")
        return 0
    
    deleted_files = 0
    deleted_dirs = 0
    
    print("🧹 Limpiando archivos de storage...")
    
    # Eliminar archivos de libros generados
    books_dir = os.path.join(storage_path, 'books')
    if os.path.exists(books_dir):
        try:
            file_count = len(list(Path(books_dir).rglob('*')))
            shutil.rmtree(books_dir)
            print(f"🗑️  Eliminado directorio books/ ({file_count} archivos)")
            deleted_dirs += 1
        except Exception as e:
            print(f"❌ Error eliminando directorio books: {e}")
    
    # Eliminar archivos de covers
    covers_dir = os.path.join(storage_path, 'covers')
    if os.path.exists(covers_dir):
        try:
            file_count = len(list(Path(covers_dir).rglob('*')))
            shutil.rmtree(covers_dir)
            print(f"🗑️  Eliminado directorio covers/ ({file_count} archivos)")
            deleted_dirs += 1
        except Exception as e:
            print(f"❌ Error eliminando directorio covers: {e}")
    
    # Eliminar archivos temporales de generación
    temp_dir = os.path.join(storage_path, 'temp')
    if os.path.exists(temp_dir):
        try:
            file_count = len(list(Path(temp_dir).rglob('*')))
            shutil.rmtree(temp_dir)
            print(f"🗑️  Eliminado directorio temp/ ({file_count} archivos)")
            deleted_dirs += 1
        except Exception as e:
            print(f"❌ Error eliminando directorio temp: {e}")
    
    return deleted_dirs

def delete_all_books():
    """Elimina todos los libros de la base de datos"""
    print("🗑️  Eliminando todos los libros de la base de datos...")
    
    try:
        # Obtener conteo antes de eliminar
        total_books = BookGeneration.query.count()
        
        if total_books == 0:
            print("✅ No hay libros para eliminar")
            return 0
        
        # Eliminar todos los libros (cascade eliminará downloads relacionados)
        deleted_count = BookGeneration.query.delete()
        
        # Confirmar los cambios
        db.session.commit()
        
        print(f"✅ Eliminados {deleted_count} libros de la base de datos")
        return deleted_count
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error eliminando libros: {e}")
        raise

def reset_auto_increment():
    """Resetea los auto increment para empezar desde 1"""
    try:
        # Reset auto increment para PostgreSQL
        db.session.execute("ALTER SEQUENCE book_generations_id_seq RESTART WITH 1")
        db.session.execute("ALTER SEQUENCE book_downloads_id_seq RESTART WITH 1")
        db.session.commit()
        print("🔄 Reseteados auto-increment sequences")
    except Exception as e:
        print(f"⚠️  Error reseteando sequences: {e}")

def main():
    """Función principal"""
    print_section("ELIMINACIÓN COMPLETA DE LIBROS - BUKO AI")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Crear aplicación Flask
    app = create_app('development')
    
    with app.app_context():
        # Mostrar estado actual
        total_books = show_current_stats()
        
        if total_books == 0:
            print("✅ No hay libros para eliminar")
            return
        
        print(f"\n⚠️  ¡ATENCIÓN! Esto eliminará TODOS los {total_books} libros del sistema.")
        print("Esta acción NO se puede deshacer.")
        print("\nEsto incluye:")
        print("   - Todos los registros de libros en la base de datos")
        print("   - Todos los archivos generados (PDF, EPUB, etc.)")
        print("   - Todas las portadas")
        print("   - Todos los archivos temporales")
        
        # Confirmar eliminación
        confirm = input(f"\n¿Eliminar TODOS los {total_books} libros? (escriba 'ELIMINAR' para confirmar): ").strip()
        
        if confirm != 'ELIMINAR':
            print("❌ Operación cancelada")
            return
        
        print("\n🚀 Iniciando eliminación completa...")
        
        # Eliminar de la base de datos
        deleted_books = delete_all_books()
        
        # Limpiar archivos de storage
        deleted_dirs = cleanup_storage_files()
        
        # Reset auto increment
        reset_auto_increment()
        
        print_section("ELIMINACIÓN COMPLETADA")
        print(f"✅ Libros eliminados: {deleted_books}")
        print(f"✅ Directorios limpiados: {deleted_dirs}")
        print(f"✅ Sistema reseteado para empezar desde cero")
        print(f"🕒 Completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Verificar estado final
        print("\n📊 Estado final:")
        show_current_stats()

if __name__ == '__main__':
    main()