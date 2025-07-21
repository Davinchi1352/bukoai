#!/bin/bash

# Script para configurar el entorno de desarrollo y resolver errores del IDE

echo "🔧 CONFIGURACIÓN DE ENTORNO BUKO AI 🔧"
echo "======================================"
echo ""

# Verificar si ya existe un entorno virtual
if [ -d "venv" ]; then
    echo "📁 Entorno virtual encontrado"
    read -p "¿Quieres recrear el entorno virtual? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Eliminando entorno virtual existente..."
        rm -rf venv
        echo "✅ Entorno virtual eliminado"
    else
        echo "📦 Usando entorno virtual existente"
    fi
else
    echo "📁 No se encontró entorno virtual"
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo ""
    echo "🐍 Creando entorno virtual..."
    python3 -m venv venv
    
    if [ $? -eq 0 ]; then
        echo "✅ Entorno virtual creado exitosamente"
    else
        echo "❌ Error al crear entorno virtual"
        exit 1
    fi
fi

echo ""
echo "🔗 Activando entorno virtual..."
source venv/bin/activate

echo "✅ Entorno virtual activado"
echo "📍 Python ejecutable: $(which python)"
echo "📍 Versión Python: $(python --version)"

echo ""
echo "📦 Actualizando pip..."
python -m pip install --upgrade pip

echo ""
echo "📥 Instalando dependencias desde requirements.txt..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencias instaladas exitosamente"
else
    echo "⚠️  Algunas dependencias pueden haber fallado"
    echo "Esto es normal si faltan dependencias del sistema (como PostgreSQL headers)"
fi

echo ""
echo "🔍 Verificando instalación de paquetes clave..."
python -c "
import sys
packages = [
    'flask', 'flask_login', 'flask_migrate', 'flask_mail', 
    'flask_cors', 'flask_limiter', 'flask_socketio', 'flask_caching'
]

missing = []
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}')
    except ImportError:
        print(f'❌ {pkg}')
        missing.append(pkg)

if missing:
    print(f'\\n⚠️  Paquetes faltantes: {missing}')
else:
    print('\\n🎉 Todos los paquetes Flask están instalados!')
"

echo ""
echo "📝 CONFIGURACIÓN DEL IDE:"
echo "========================"
echo ""
echo "Para VS Code:"
echo "1. Abrir VS Code en este directorio"
echo "2. Presionar Ctrl+Shift+P"
echo "3. Buscar 'Python: Select Interpreter'"
echo "4. Seleccionar: $(pwd)/venv/bin/python"
echo ""
echo "Para PyCharm:"
echo "1. File > Settings > Project > Python Interpreter"
echo "2. Gear icon > Add > Existing Environment"
echo "3. Seleccionar: $(pwd)/venv/bin/python"
echo "4. Apply y OK"
echo ""
echo "🔄 REINICIA TU IDE después de cambiar el intérprete"

echo ""
echo "🧪 PRUEBA RÁPIDA:"
echo "================="
echo "Ejecutar para probar que todo funciona:"
echo "source venv/bin/activate"
echo "python3 -c \"from app import create_app; print('✅ App importada correctamente')\""

echo ""
echo "🎯 RESULTADO ESPERADO:"
echo "======================"
echo "- ✅ Sin errores de importación en el IDE"
echo "- ✅ Syntax highlighting funcionando"
echo "- ✅ Autocompletado Flask activo"
echo "- ✅ No más líneas rojas en imports"

echo ""
echo "🚀 ¡CONFIGURACIÓN COMPLETADA!"
echo "Recuerda: SIEMPRE activa el entorno virtual antes de trabajar:"
echo "source venv/bin/activate"