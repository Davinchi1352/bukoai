#!/bin/bash

# ===========================================
# BUKO AI - SCRIPT DE PRODUCCIÓN
# ===========================================

set -e

echo "🚀 Iniciando Buko AI en modo producción..."

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
    print_error "Archivo .env no encontrado. Configura las variables de entorno para producción"
    exit 1
fi

# Cargar variables de entorno
export $(cat .env | grep -v '^#' | xargs)

# Configurar Flask para producción
export FLASK_APP=app.py
export FLASK_ENV=production
export FLASK_DEBUG=0

# Verificar configuración crítica
print_info "Verificando configuración de producción..."

# Verificar base de datos
if [ -z "$DATABASE_URL" ]; then
    print_error "DATABASE_URL no está configurada"
    exit 1
fi

# Verificar Claude API
if [ -z "$ANTHROPIC_API_KEY" ]; then
    print_error "ANTHROPIC_API_KEY no está configurada"
    exit 1
fi

# Verificar Redis
if [ -z "$REDIS_URL" ]; then
    print_error "REDIS_URL no está configurada"
    exit 1
fi

# Verificar configuración de email
if [ -z "$MAIL_USERNAME" ] || [ -z "$MAIL_PASSWORD" ]; then
    print_warning "Configuración de email no está completa"
fi

# Verificar configuración de pagos
if [ -z "$PAYPAL_CLIENT_ID" ] && [ -z "$MP_ACCESS_TOKEN" ]; then
    print_warning "Configuración de pagos no está completa"
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
python -c "import flask, sqlalchemy, celery, anthropic, gunicorn" || {
    print_error "Dependencias faltantes. Ejecuta ./scripts/install.sh"
    exit 1
}

# Ejecutar migraciones
print_info "Ejecutando migraciones..."
flask db upgrade

# Inicializar datos de producción si es necesario
if [ -f "scripts/init_db.py" ]; then
    print_info "Inicializando datos de producción..."
    python scripts/init_db.py --production
fi

# Recopilar archivos estáticos (si aplica)
print_info "Optimizando archivos estáticos..."
# Aquí se puede agregar minificación de CSS/JS

# Mostrar información del entorno
echo ""
echo "🎯 Configuración del entorno de producción:"
echo "   - Flask App: $FLASK_APP"
echo "   - Flask Env: $FLASK_ENV"
echo "   - Debug: $FLASK_DEBUG"
echo "   - Workers: ${GUNICORN_WORKERS:-4}"
echo "   - Port: ${PORT:-5000}"
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

# Iniciar Celery worker en background
print_info "Iniciando Celery worker..."
celery -A app.celery worker --loglevel=warning --concurrency=${CELERY_WORKER_CONCURRENCY:-4} &
CELERY_PID=$!
print_success "Celery worker iniciado (PID: $CELERY_PID)"

# Iniciar Celery beat para tareas periódicas
print_info "Iniciando Celery beat..."
celery -A app.celery beat --loglevel=warning &
BEAT_PID=$!
print_success "Celery beat iniciado (PID: $BEAT_PID)"

# Iniciar Gunicorn
print_info "Iniciando Gunicorn..."
print_success "Servidor disponible en: http://0.0.0.0:${PORT:-5000}"

exec gunicorn \
    --bind 0.0.0.0:${PORT:-5000} \
    --workers ${GUNICORN_WORKERS:-4} \
    --worker-class eventlet \
    --worker-connections 1000 \
    --timeout 30 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --preload \
    --log-level warning \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    app:app