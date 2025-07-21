#!/bin/bash

# ===========================================
# BUKO AI - FLOWER ENTRYPOINT
# ===========================================

set -e

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

print_info "🌺 Iniciando Flower - Celery Monitor..."

# Verificar variables de entorno críticas para Flower
if [ -z "$CELERY_BROKER_URL" ]; then
    print_error "CELERY_BROKER_URL no está configurada"
    exit 1
fi

# Esperar a que Redis esté listo
print_info "Esperando a que Redis esté listo..."
while ! redis-cli -h redis -p 6379 ping > /dev/null 2>&1; do
    print_info "Redis no está listo, esperando..."
    sleep 2
done
print_success "Redis está listo"

# Crear directorios necesarios
print_info "Creando directorios necesarios..."
mkdir -p logs
print_success "Directorios creados"

# Función para manejar la terminación graceful
cleanup() {
    print_info "Recibida señal de terminación, cerrando Flower..."
    exit 0
}

trap cleanup SIGINT SIGTERM

print_info "Iniciando Flower en 0.0.0.0:5555..."
exec celery -A app.celery flower --host=0.0.0.0 --port=5555 "$@"