#!/usr/bin/env python3
"""
Script para limpieza manual de archivos específicos obsoletos en Buko AI
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

def print_section(title: str):
    """Imprime un separador de sección"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def manual_cleanup():
    """Limpieza manual de archivos específicos"""
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Archivos obsoletos identificados manualmente
    obsolete_files = [
        'analyze_book.py',
        'app_simple.py', 
        'check_api_response.py',
        'check_book_38.py',
        'create_german_book_admin.py',
        'export_book_content.py',
        'extract_raw_content.py',
        'fix_ide_errors.py',
        'test_celery.py',
        'test_multichunk_book.py',
        'test_multichunk_standalone.py',
        'test_new_book.py',
        'test_real_apis.py',
        'test_websocket.py',
        'verificar_configuracion.py',
        'verify_real_data.py',
        'cookies.txt',
        'celery_worker.log',
        'celery_worker_book_generation.log',
        'celerybeat-schedule',
        'setup_environment.sh',
    ]
    
    # Directorios obsoletos
    obsolete_dirs = [
        'book_34_extracted_content',
        'app/routes/api_temp',
        'ssl',  # Vacío y no usado en development
    ]
    
    print_section("LIMPIEZA MANUAL DE ARCHIVOS OBSOLETOS")
    print(f"Proyecto: {project_root}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Mostrar archivos a eliminar
    print("\n📁 Archivos identificados para eliminación:")
    existing_files = []
    for file_path in obsolete_files:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            existing_files.append(file_path)
            file_size = os.path.getsize(full_path)
            print(f"   - {file_path} ({file_size} bytes)")
    
    print("\n📂 Directorios identificados para eliminación:")
    existing_dirs = []
    for dir_path in obsolete_dirs:
        full_path = os.path.join(project_root, dir_path)
        if os.path.exists(full_path):
            existing_dirs.append(dir_path)
            try:
                dir_size = sum(f.stat().st_size for f in Path(full_path).rglob('*') if f.is_file())
                file_count = len(list(Path(full_path).rglob('*')))
                print(f"   - {dir_path}/ ({file_count} archivos, {dir_size} bytes)")
            except:
                print(f"   - {dir_path}/ (no se pudo calcular tamaño)")
    
    if not existing_files and not existing_dirs:
        print("✅ No se encontraron archivos obsoletos para eliminar")
        return
    
    total_items = len(existing_files) + len(existing_dirs)
    print(f"\n📊 Total: {total_items} elementos para eliminar")
    
    # Confirmar eliminación
    confirm = input(f"\n¿Eliminar estos {total_items} elementos? (s/N): ").strip().lower()
    
    if confirm not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Operación cancelada")
        return
    
    # Eliminar archivos
    deleted_files = 0
    for file_path in existing_files:
        full_path = os.path.join(project_root, file_path)
        try:
            os.remove(full_path)
            print(f"🗑️  Archivo eliminado: {file_path}")
            deleted_files += 1
        except Exception as e:
            print(f"❌ Error eliminando archivo {file_path}: {e}")
    
    # Eliminar directorios
    deleted_dirs = 0
    for dir_path in existing_dirs:
        full_path = os.path.join(project_root, dir_path)
        try:
            shutil.rmtree(full_path)
            print(f"🗑️  Directorio eliminado: {dir_path}/")
            deleted_dirs += 1
        except Exception as e:
            print(f"❌ Error eliminando directorio {dir_path}: {e}")
    
    print(f"\n🎉 Limpieza completada!")
    print(f"   - Archivos eliminados: {deleted_files}")
    print(f"   - Directorios eliminados: {deleted_dirs}")
    print(f"   - Total eliminado: {deleted_files + deleted_dirs} elementos")

def cleanup_logs():
    """Limpia logs antiguos y temporales"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_dir = os.path.join(project_root, 'logs')
    
    if not os.path.exists(logs_dir):
        return
    
    print("\n📝 Limpiando logs antiguos...")
    
    # Archivos de log a limpiar (mantener estructura pero vaciar contenido)
    log_files_to_clean = [
        'buko-ai-dev.log.1',
        'buko-ai-dev.log.2', 
        'buko-ai.log.1',
        'buko-ai.log.2',
        'business.log',
        'errors.log',
        'performance.log',
        'security.log',
    ]
    
    cleaned_logs = 0
    for log_file in log_files_to_clean:
        log_path = os.path.join(logs_dir, log_file)
        if os.path.exists(log_path):
            try:
                # Vaciar el archivo en lugar de eliminarlo
                with open(log_path, 'w') as f:
                    f.write("")
                print(f"🧹 Log limpiado: {log_file}")
                cleaned_logs += 1
            except Exception as e:
                print(f"❌ Error limpiando log {log_file}: {e}")
    
    if cleaned_logs > 0:
        print(f"✅ {cleaned_logs} archivos de log limpiados")

def consolidate_docs():
    """Sugiere consolidación de documentación"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    docs = []
    for file in os.listdir(project_root):
        if file.endswith('.md') and file not in ['README.md']:
            docs.append(file)
    
    if docs:
        print(f"\n📚 Documentos encontrados ({len(docs)}):")
        for doc in sorted(docs):
            print(f"   - {doc}")
        
        print("\n💡 Sugerencia: Considera consolidar documentos similares")
        print("   Por ejemplo, combinar archivos de estado o análisis")

def main():
    """Función principal"""
    print("🧹 LIMPIEZA MANUAL DE ARCHIVOS OBSOLETOS - BUKO AI")
    
    try:
        # Limpieza principal
        manual_cleanup()
        
        # Limpieza de logs
        cleanup_logs()
        
        # Sugerencias de consolidación
        consolidate_docs()
        
        print("\n✅ Proceso de limpieza completado")
        
    except KeyboardInterrupt:
        print("\n⚠️  Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la limpieza: {e}")

if __name__ == '__main__':
    main()