#!/bin/bash

# ===========================================
# BUKO AI - SCRIPT DE DESARROLLO
# ===========================================

set -e

echo "🚀 Iniciando Buko AI en modo desarrollo..."

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

# Verificar entorno virtual
if [ ! -d "venv" ]; then
    print_error "Entorno virtual no encontrado. Ejecuta ./scripts/install.sh primero"
    exit 1
fi

# Activar entorno virtual
source venv/bin/activate

# Verificar archivo .env
if [ ! -f ".env" ]; then
    print_warning "Archivo .env no encontrado. Creando desde .env.example..."
    cp .env.example .env
    print_info "Por favor configura las variables de entorno en .env"
fi

# Verificar servicios externos
print_info "Verificando servicios externos..."

# Verificar PostgreSQL
if ! command -v psql &> /dev/null; then
    print_warning "PostgreSQL no está instalado. Usando SQLite para desarrollo."
    export DATABASE_URL="sqlite:///buko_ai_dev.db"
fi

# Verificar Redis
if ! command -v redis-server &> /dev/null; then
    print_warning "Redis no está instalado. Celery funcionará en modo eager."
    export CELERY_ALWAYS_EAGER=True
fi

# Crear directorios necesarios
print_info "Creando directorios necesarios..."
mkdir -p logs
mkdir -p storage/uploads
mkdir -p storage/books
mkdir -p storage/covers
mkdir -p migrations/versions

# Verificar dependencias críticas
print_info "Verificando dependencias críticas..."
python -c "import flask, sqlalchemy, celery, anthropic" || {
    print_error "Dependencias faltantes. Ejecuta ./scripts/install.sh"
    exit 1
}

# Configurar Flask
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Inicializar base de datos si no existe
if [ ! -f "migrations/alembic.ini" ]; then
    print_info "Inicializando migraciones de base de datos..."
    flask db init
fi

# Ejecutar migraciones
print_info "Ejecutando migraciones..."
flask db upgrade

# Inicializar datos de prueba
if [ -f "scripts/init_db.py" ]; then
    print_info "Inicializando datos de prueba..."
    python scripts/init_db.py --development
fi

# Mostrar información del entorno
echo ""
echo "🎯 Configuración del entorno de desarrollo:"
echo "   - Flask App: $FLASK_APP"
echo "   - Flask Env: $FLASK_ENV"
echo "   - Debug: $FLASK_DEBUG"
echo "   - Database: ${DATABASE_URL:-postgresql://user:password@localhost:5432/buko_ai_dev}"
echo "   - Redis: ${REDIS_URL:-redis://localhost:6379/0}"
echo ""

# Función para manejar la terminación
cleanup() {
    echo ""
    print_info "Deteniendo servicios..."
    jobs -p | xargs -r kill
    print_success "Servicios detenidos"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Iniciar Celery worker en background si Redis está disponible
if command -v redis-server &> /dev/null && [ "$CELERY_ALWAYS_EAGER" != "True" ]; then
    print_info "Iniciando Celery worker..."
    celery -A app.celery worker --loglevel=info --pool=solo &
    CELERY_PID=$!
    print_success "Celery worker iniciado (PID: $CELERY_PID)"
fi

# Iniciar Flask
print_info "Iniciando Flask en modo desarrollo..."
print_success "Servidor disponible en: http://localhost:5000"
print_info "Presiona Ctrl+C para detener"

flask run --host=0.0.0.0 --port=5000 --reload