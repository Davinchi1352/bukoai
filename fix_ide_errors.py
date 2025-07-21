"""
Script para diagnosticar y resolver errores de importación en el IDE.
"""

import sys
import os
import subprocess

def check_python_environment():
    """Verificar el entorno de Python actual."""
    print("=== Diagnóstico de Entorno Python ===\n")
    
    print(f"Python ejecutable: {sys.executable}")
    print(f"Versión de Python: {sys.version}")
    print(f"Directorio de trabajo: {os.getcwd()}")
    
    # Verificar si estamos en un entorno virtual
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Ejecutándose en entorno virtual")
        print(f"Prefijo del entorno virtual: {sys.prefix}")
    else:
        print("⚠️  NO está en entorno virtual")
        print("Recomendación: Crear y activar un entorno virtual")

def check_installed_packages():
    """Verificar qué paquetes están instalados."""
    print("\n=== Verificando Paquetes Flask ===\n")
    
    required_packages = [
        'flask',
        'flask-login',
        'flask-migrate',
        'flask-mail',
        'flask-cors',
        'flask-limiter',
        'flask-socketio',
        'flask-caching',
        'redis',
        'celery',
        'sqlalchemy',
        'psycopg2-binary'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}: Instalado")
        except ImportError:
            print(f"❌ {package}: NO instalado")
            missing_packages.append(package)
    
    return missing_packages

def suggest_fixes(missing_packages):
    """Sugerir soluciones para los errores."""
    print("\n=== Soluciones Recomendadas ===\n")
    
    if missing_packages:
        print("1. INSTALAR PAQUETES FALTANTES:")
        print(f"   pip install {' '.join(missing_packages)}")
        print("\n   O instalar todo desde requirements.txt:")
        print("   pip install -r requirements.txt")
    
    print("\n2. CONFIGURAR IDE (VS Code/PyCharm):")
    print("   • VS Code:")
    print("     - Ctrl+Shift+P > 'Python: Select Interpreter'")
    print("     - Seleccionar el intérprete del entorno virtual")
    print("     - Debería ser algo como: ./venv/bin/python")
    
    print("\n   • PyCharm:")
    print("     - File > Settings > Project > Python Interpreter")
    print("     - Add Interpreter > Existing Environment")
    print("     - Apuntar a ./venv/bin/python")
    
    print("\n3. VERIFICAR ENTORNO VIRTUAL:")
    print("   # Crear entorno virtual (si no existe)")
    print("   python3 -m venv venv")
    print("\n   # Activar entorno virtual")
    print("   source venv/bin/activate  # Linux/Mac")
    print("   # o")
    print("   venv\\Scripts\\activate     # Windows")
    print("\n   # Instalar dependencias")
    print("   pip install -r requirements.txt")
    
    print("\n4. REINICIAR IDE:")
    print("   Después de cambiar el intérprete, reinicia el IDE")

def check_requirements_file():
    """Verificar si existe requirements.txt."""
    print("\n=== Verificando requirements.txt ===\n")
    
    if os.path.exists('requirements.txt'):
        print("✅ requirements.txt encontrado")
        with open('requirements.txt', 'r') as f:
            lines = f.readlines()
        print(f"Contiene {len(lines)} dependencias")
        
        # Mostrar algunas dependencias clave
        flask_deps = [line.strip() for line in lines if 'flask' in line.lower()]
        if flask_deps:
            print("\nDependencias Flask encontradas:")
            for dep in flask_deps[:10]:  # Mostrar primeras 10
                print(f"  - {dep}")
    else:
        print("❌ requirements.txt NO encontrado")
        print("Crear uno con las dependencias básicas")

if __name__ == '__main__':
    check_python_environment()
    check_requirements_file()
    missing = check_installed_packages()
    suggest_fixes(missing)
    
    print("\n" + "="*50)
    print("RESUMEN:")
    print("- Los errores del IDE son por falta de dependencias")
    print("- Instalar paquetes: pip install -r requirements.txt") 
    print("- Configurar intérprete Python en el IDE")
    print("- Reiniciar el IDE después de los cambios")
    print("="*50)