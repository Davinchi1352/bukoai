#!/bin/bash

# ===========================================
# BUKO AI - SCRIPT DE INSTALACIÓN
# ===========================================

set -e

echo "🚀 Instalando Buko AI..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar si está corriendo en el directorio correcto
if [ ! -f "README.md" ] || [ ! -f "requirements.txt" ]; then
    print_error "Por favor ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar Python
print_info "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION encontrado"

# Verificar Python 3.12+
if ! python3 -c "import sys; assert sys.version_info >= (3, 12)" 2>/dev/null; then
    print_error "Python 3.12+ es requerido. Versión actual: $PYTHON_VERSION"
    exit 1
fi

# Crear entorno virtual
print_info "Creando entorno virtual..."
if [ -d "venv" ]; then
    print_warning "Entorno virtual ya existe. Eliminando..."
    rm -rf venv
fi

python3 -m venv venv
print_success "Entorno virtual creado"

# Activar entorno virtual
print_info "Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
print_info "Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
print_info "Instalando dependencias..."
pip install -r requirements.txt
print_success "Dependencias instaladas"

# Instalar dependencias de desarrollo
print_info "Instalando dependencias de desarrollo..."
pip install -e ".[dev]"
print_success "Dependencias de desarrollo instaladas"

# Configurar archivos de entorno
print_info "Configurando archivos de entorno..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_success "Archivo .env creado desde .env.example"
    print_warning "Por favor configura las variables de entorno en .env"
else
    print_info "Archivo .env ya existe"
fi

# Crear directorios necesarios
print_info "Creando directorios necesarios..."
mkdir -p logs
mkdir -p storage/uploads
mkdir -p storage/books
mkdir -p storage/covers
print_success "Directorios creados"

# Configurar pre-commit hooks
print_info "Configurando pre-commit hooks..."
pre-commit install
print_success "Pre-commit hooks configurados"

# Verificar instalación
print_info "Verificando instalación..."

# Verificar Flask
if python -c "import flask" 2>/dev/null; then
    print_success "Flask instalado correctamente"
else
    print_error "Error al instalar Flask"
    exit 1
fi

# Verificar otras dependencias críticas
CRITICAL_DEPS=("sqlalchemy" "celery" "redis" "anthropic" "reportlab")
for dep in "${CRITICAL_DEPS[@]}"; do
    if python -c "import $dep" 2>/dev/null; then
        print_success "$dep instalado correctamente"
    else
        print_error "Error al instalar $dep"
        exit 1
    fi
done

# Crear archivo de configuración inicial
print_info "Creando configuración inicial..."
cat > app.py << 'EOF'
from flask import Flask
from config import get_config

def create_app(config_name='development'):
    app = Flask(__name__)
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    config_class.init_app(app)
    
    @app.route('/')
    def index():
        return {
            'message': 'Buko AI API',
            'version': '0.1.0',
            'status': 'healthy'
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
EOF

print_success "Archivo app.py creado"

# Mostrar información final
echo ""
echo "🎉 ¡Instalación completada exitosamente!"
echo ""
echo "Para comenzar a desarrollar:"
echo "1. Configura las variables de entorno en .env"
echo "2. Ejecuta: source venv/bin/activate"
echo "3. Ejecuta: python app.py"
echo ""
echo "Para usar Docker:"
echo "1. Ejecuta: docker-compose up --build"
echo ""
echo "Documentación disponible en: https://docs.buko-ai.com"
echo ""
print_success "¡Listo para comenzar a desarrollar!"