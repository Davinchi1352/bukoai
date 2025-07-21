#!/usr/bin/env python3
"""
Script para verificar si la configuración del IDE está correcta.
Ejecutar después de configurar el intérprete en VS Code/PyCharm.
"""

import sys
import os

def verificar_entorno():
    """Verificar configuración del entorno."""
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN IDE")
    print("=" * 40)
    print()
    
    # 1. Verificar ubicación de Python
    python_path = sys.executable
    print(f"📍 Python ejecutable: {python_path}")
    
    if "venv" in python_path:
        print("✅ Ejecutándose desde entorno virtual")
    else:
        print("❌ NO está usando entorno virtual")
        print("   Configura tu IDE para usar: ./venv/bin/python")
        return False
    
    print(f"📍 Versión Python: {sys.version}")
    print()
    
    # 2. Verificar importaciones críticas
    print("🧪 VERIFICANDO IMPORTACIONES:")
    print("-" * 30)
    
    imports_criticos = [
        ("flask", "Flask"),
        ("flask_login", "Flask-Login"),
        ("flask_migrate", "Flask-Migrate"), 
        ("flask_mail", "Flask-Mail"),
        ("flask_cors", "Flask-CORS"),
        ("flask_limiter", "Flask-Limiter"),
        ("flask_socketio", "Flask-SocketIO"),
        ("flask_caching", "Flask-Caching"),
        ("celery", "Celery"),
        ("redis", "Redis")
    ]
    
    errores = []
    for modulo, nombre in imports_criticos:
        try:
            __import__(modulo)
            print(f"✅ {nombre}")
        except ImportError as e:
            print(f"❌ {nombre}: {e}")
            errores.append(nombre)
    
    print()
    
    # 3. Verificar importación de la app
    print("🔧 VERIFICANDO APLICACIÓN:")
    print("-" * 25)
    
    try:
        from app import create_app
        print("✅ App principal importada correctamente")
        
        # Intentar crear la app
        app = create_app()
        print("✅ App creada exitosamente")
        
    except Exception as e:
        print(f"❌ Error al importar/crear app: {e}")
        errores.append("App principal")
    
    print()
    
    # 4. Resultado final
    if not errores:
        print("🎉 CONFIGURACIÓN PERFECTA!")
        print("Tu IDE debería mostrar:")
        print("  - Sin errores rojos en imports")
        print("  - Autocompletado funcionando")
        print("  - Navegación de código activa")
        print()
        print("Si aún ves errores rojos, reinicia tu IDE.")
        return True
    else:
        print("⚠️  PROBLEMAS ENCONTRADOS:")
        print("Tu IDE aún no está configurado correctamente.")
        print()
        print("SOLUCIONES:")
        print("1. Verificar que el IDE use: ./venv/bin/python")
        print("2. Reiniciar el IDE después del cambio")
        print("3. En terminal: source venv/bin/activate")
        print()
        print(f"Módulos con problemas: {', '.join(errores)}")
        return False

def mostrar_informacion_ide():
    """Mostrar información para configurar IDEs."""
    print()
    print("📝 CONFIGURACIÓN IDE:")
    print("=" * 20)
    print()
    print("VS Code:")
    print("  1. Ctrl+Shift+P")
    print("  2. 'Python: Select Interpreter'")
    print("  3. Seleccionar: ./venv/bin/python")
    print()
    print("PyCharm:")
    print("  1. File > Settings > Project > Python Interpreter")
    print("  2. Gear icon > Add > Existing Environment")
    print("  3. Seleccionar: ./venv/bin/python")
    print()
    print("🔄 ¡REINICIA TU IDE después del cambio!")

if __name__ == "__main__":
    resultado = verificar_entorno()
    
    if not resultado:
        mostrar_informacion_ide()
    
    print()
    print("Ejecutar este script periódicamente para verificar la configuración.")