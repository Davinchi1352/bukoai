#!/usr/bin/env python3
"""
Script para identificar y limpiar archivos no utilizados en el proyecto Buko AI
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Set, List, Dict, Tuple
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_section(title: str):
    """Imprime un separador de sección"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def find_all_files(project_root: str) -> Dict[str, List[str]]:
    """Encuentra todos los archivos del proyecto por categoría"""
    
    # Directorios a ignorar
    ignore_dirs = {
        '.git', '__pycache__', '.pytest_cache', 'node_modules', 
        'venv', 'env', '.venv', 'logs', 'storage', '.docker'
    }
    
    # Extensiones por categoría
    categories = {
        'python': ['.py'],
        'templates': ['.html', '.htm'],
        'static': ['.css', '.js', '.scss', '.less'],
        'images': ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico'],
        'config': ['.json', '.yaml', '.yml', '.toml', '.ini', '.conf'],
        'docker': ['Dockerfile', '.dockerignore'],
        'docs': ['.md', '.rst', '.txt'],
        'other': []
    }
    
    files_by_category = {cat: [] for cat in categories.keys()}
    
    for root, dirs, files in os.walk(project_root):
        # Filtrar directorios a ignorar
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, project_root)
            
            # Clasificar archivo
            file_ext = Path(file).suffix.lower()
            file_name = Path(file).name
            
            categorized = False
            for category, extensions in categories.items():
                if file_ext in extensions or file_name in extensions:
                    files_by_category[category].append(rel_path)
                    categorized = True
                    break
            
            if not categorized:
                files_by_category['other'].append(rel_path)
    
    return files_by_category

def find_imports_and_references(project_root: str) -> Dict[str, Set[str]]:
    """Encuentra todas las importaciones y referencias en archivos Python"""
    
    references = {}
    
    # Buscar archivos Python
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'__pycache__', 'logs', 'storage'}]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_root)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Buscar imports
                    import_patterns = [
                        r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',
                        r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)',
                        r'include\(["\']([^"\']+)["\']',  # Para templates
                        r'render_template\(["\']([^"\']+)["\']',  # Templates
                        r'url_for\(["\']([^"\']+)["\']',  # URLs
                    ]
                    
                    refs = set()
                    for pattern in import_patterns:
                        matches = re.findall(pattern, content)
                        refs.update(matches)
                    
                    # Buscar referencias a archivos estáticos
                    static_patterns = [
                        r'["\']([^"\']*\.css)["\']',
                        r'["\']([^"\']*\.js)["\']',
                        r'["\']([^"\']*\.png)["\']',
                        r'["\']([^"\']*\.jpg)["\']',
                        r'["\']([^"\']*\.jpeg)["\']',
                        r'["\']([^"\']*\.gif)["\']',
                        r'["\']([^"\']*\.svg)["\']',
                    ]
                    
                    for pattern in static_patterns:
                        matches = re.findall(pattern, content)
                        refs.update(matches)
                    
                    references[rel_path] = refs
                    
                except Exception as e:
                    print(f"Error leyendo {rel_path}: {e}")
    
    return references

def find_template_references(project_root: str) -> Set[str]:
    """Encuentra referencias a templates en archivos HTML"""
    
    template_refs = set()
    
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'__pycache__', 'logs', 'storage'}]
        
        for file in files:
            if file.endswith(('.html', '.htm')):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Buscar extends, includes, y otras referencias
                    patterns = [
                        r'{%\s*extends\s+["\']([^"\']+)["\']',
                        r'{%\s*include\s+["\']([^"\']+)["\']',
                        r'href=["\']([^"\']*\.css)["\']',
                        r'src=["\']([^"\']*\.js)["\']',
                        r'src=["\']([^"\']*\.png)["\']',
                        r'src=["\']([^"\']*\.jpg)["\']',
                        r'src=["\']([^"\']*\.jpeg)["\']',
                        r'src=["\']([^"\']*\.gif)["\']',
                        r'src=["\']([^"\']*\.svg)["\']',
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content)
                        template_refs.update(matches)
                        
                except Exception as e:
                    print(f"Error leyendo template {file_path}: {e}")
    
    return template_refs

def analyze_unused_files(project_root: str) -> Dict[str, List[str]]:
    """Analiza archivos no utilizados"""
    
    print("🔍 Analizando archivos del proyecto...")
    
    # Obtener todos los archivos
    files_by_category = find_all_files(project_root)
    
    # Obtener referencias
    python_refs = find_imports_and_references(project_root)
    template_refs = find_template_references(project_root)
    
    # Combinar todas las referencias
    all_refs = set()
    for refs in python_refs.values():
        all_refs.update(refs)
    all_refs.update(template_refs)
    
    # Archivos potencialmente no utilizados
    unused_files = {
        'python': [],
        'templates': [],
        'static': [],
        'config': [],
        'docs': [],
        'other': []
    }
    
    # Archivos específicos que siempre se mantienen
    keep_files = {
        'app/__init__.py',
        'app.py',
        'run.py',
        'manage.py',
        'Dockerfile',
        'docker-compose.yml',
        'docker-compose.dev.yml',
        'requirements.txt',
        'README.md',
        '.env',
        '.env.example',
        '.gitignore',
        'config/__init__.py',
        'migrations/',
    }
    
    # Analizar archivos Python
    for file_path in files_by_category['python']:
        if any(keep in file_path for keep in keep_files):
            continue
            
        # Verificar si el archivo es referenciado
        module_name = file_path.replace('/', '.').replace('.py', '')
        is_referenced = False
        
        for ref in all_refs:
            if module_name in ref or os.path.basename(file_path).replace('.py', '') in ref:
                is_referenced = True
                break
        
        # Verificar si es un archivo especial
        if file_path.endswith(('__init__.py', 'models.py', 'views.py', 'routes.py', 'tasks.py')):
            is_referenced = True
        
        if not is_referenced:
            unused_files['python'].append(file_path)
    
    # Analizar templates
    for file_path in files_by_category['templates']:
        template_name = os.path.basename(file_path)
        is_referenced = False
        
        for ref in all_refs:
            if template_name in ref or file_path in ref:
                is_referenced = True
                break
        
        if not is_referenced:
            unused_files['templates'].append(file_path)
    
    # Analizar archivos estáticos
    for file_path in files_by_category['static']:
        file_name = os.path.basename(file_path)
        is_referenced = False
        
        for ref in all_refs:
            if file_name in ref or file_path in ref:
                is_referenced = True
                break
        
        if not is_referenced:
            unused_files['static'].append(file_path)
    
    # Analizar archivos de configuración
    config_keep = {'.env', 'requirements.txt', 'Dockerfile', 'docker-compose.yml', 'docker-compose.dev.yml'}
    for file_path in files_by_category['config']:
        if os.path.basename(file_path) not in config_keep:
            unused_files['config'].append(file_path)
    
    return unused_files

def main():
    """Función principal"""
    print_section("LIMPIEZA DE ARCHIVOS NO UTILIZADOS - BUKO AI")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"Directorio del proyecto: {project_root}")
    
    # Analizar archivos
    unused_files = analyze_unused_files(project_root)
    
    print_section("ARCHIVOS POTENCIALMENTE NO UTILIZADOS")
    
    total_unused = 0
    for category, files in unused_files.items():
        if files:
            print(f"\n📁 {category.upper()}:")
            for file_path in sorted(files):
                print(f"   - {file_path}")
                total_unused += 1
    
    if total_unused == 0:
        print("✅ No se encontraron archivos no utilizados")
        return
    
    print(f"\n📊 Total de archivos potencialmente no utilizados: {total_unused}")
    
    # Confirmar eliminación
    print("\n⚠️  ATENCIÓN: Estos archivos podrían estar siendo utilizados de formas no detectadas.")
    print("Se recomienda revisar manualmente antes de eliminar.")
    
    confirm = input(f"\n¿Deseas eliminar estos {total_unused} archivos? (s/N): ").strip().lower()
    
    if confirm not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Operación cancelada")
        return
    
    # Eliminar archivos
    deleted_count = 0
    for category, files in unused_files.items():
        for file_path in files:
            full_path = os.path.join(project_root, file_path)
            try:
                if os.path.exists(full_path):
                    os.remove(full_path)
                    print(f"🗑️  Eliminado: {file_path}")
                    deleted_count += 1
            except Exception as e:
                print(f"❌ Error eliminando {file_path}: {e}")
    
    print(f"\n🎉 Limpieza completada! {deleted_count} archivos eliminados")

if __name__ == '__main__':
    main()