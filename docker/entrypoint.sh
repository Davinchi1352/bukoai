#!/bin/bash

# ===========================================
# BUKO AI - DOCKER ENTRYPOINT
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

print_info "🚀 Iniciando Buko AI Docker Container..."
print_info "Parámetros recibidos: $@"
print_info "Primer parámetro: $1"
print_info "Tipo de servicio detectado: $1"

# Verificar variables de entorno críticas basado en el tipo de servicio
case "$1" in
    "worker"|"beat"|"flower")
        # Servicios Celery solo necesitan Redis
        print_info "Detectado como servicio Celery: $1"
        if [ -z "$REDIS_URL" ]; then
            print_error "REDIS_URL no está configurada"
            exit 1
        fi
        ;;
    *)
        # Servicios web necesitan tanto PostgreSQL como Redis
        print_info "Detectado como servicio web: $1"
        if [ -z "$DATABASE_URL" ]; then
            print_error "DATABASE_URL no está configurada"
            exit 1
        fi
        if [ -z "$REDIS_URL" ]; then
            print_error "REDIS_URL no está configurada"
            exit 1
        fi
        if [ -z "$ANTHROPIC_API_KEY" ]; then
            print_warning "ANTHROPIC_API_KEY no está configurada"
        fi
        ;;
esac

# Esperar a los servicios necesarios según el tipo
case "$1" in
    "worker"|"beat"|"flower")
        # Servicios Celery solo necesitan Redis
        print_info "Esperando a que Redis esté listo..."
        while ! python -c "import redis; r = redis.Redis(host='redis', port=6379); r.ping()" > /dev/null 2>&1; do
            print_info "Redis no está listo, esperando..."
            sleep 2
        done
        print_success "Redis está listo"
        ;;
    *)
        # Servicios web necesitan tanto PostgreSQL como Redis
        print_info "Esperando a que PostgreSQL esté listo..."
        while ! pg_isready -h db -p 5432 > /dev/null 2>&1; do
            print_info "PostgreSQL no está listo, esperando..."
            sleep 2
        done
        print_success "PostgreSQL está listo"

        print_info "Esperando a que Redis esté listo..."
        while ! python -c "import redis; r = redis.Redis(host='redis', port=6379); r.ping()" > /dev/null 2>&1; do
            print_info "Redis no está listo, esperando..."
            sleep 2
        done
        print_success "Redis está listo"
        ;;
esac

# Crear directorios necesarios
print_info "Creando directorios necesarios..."
mkdir -p logs storage/uploads storage/books storage/covers migrations/versions
print_success "Directorios creados"

# Configurar Flask
export FLASK_APP=app.py

# Ejecutar migraciones de base de datos solo para servicios web
case "$1" in
    "worker"|"beat"|"flower")
        print_info "Servicio Celery - Saltando migraciones de base de datos"
        ;;
    *)
        print_info "Ejecutando migraciones de base de datos..."
        if [ ! -f "migrations/alembic.ini" ]; then
            print_info "Inicializando migraciones..."
            flask db init
        fi

        flask db upgrade
        print_success "Migraciones ejecutadas"

        # Inicializar datos si es necesario
        if [ "$FLASK_ENV" = "development" ] && [ -f "scripts/init_db.py" ]; then
            print_info "Saltando inicialización de datos de desarrollo para evitar conflictos..."
            # python scripts/init_db.py --environment development
        fi
        ;;
esac

# Función para manejar la terminación graceful
cleanup() {
    print_info "Recibida señal de terminación, cerrando servicios..."
    if [ ! -z "$CELERY_PID" ]; then
        kill $CELERY_PID
    fi
    if [ ! -z "$BEAT_PID" ]; then
        kill $BEAT_PID
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

# Manejar diferentes tipos de comando
case "$1" in
    "web")
        print_info "Iniciando servidor web..."
        shift
        exec gunicorn --bind 0.0.0.0:5000 --workers 4 --worker-class sync --timeout 30 --keep-alive 2 --max-requests 1000 --max-requests-jitter 50 --preload --log-level info --access-logfile - --error-logfile - app:app "$@"
        ;;
    "worker")
        print_info "Iniciando Celery worker..."
        shift
        exec celery -A app worker --loglevel=info --concurrency=4 "$@"
        ;;
    "beat")
        print_info "Iniciando Celery beat..."
        shift
        exec celery -A app beat --loglevel=info "$@"
        ;;
    "flower")
        print_info "Iniciando Celery flower..."
        shift
        # Flower no necesita conexión a PostgreSQL, solo Redis
        exec celery -A app flower --host=0.0.0.0 --port=5555 "$@"
        ;;
    "shell")
        print_info "Iniciando shell de Flask..."
        shift
        exec flask shell "$@"
        ;;
    "db")
        print_info "Comando de base de datos..."
        shift
        exec flask db "$@"
        ;;
    "migrate")
        print_info "Ejecutando migración..."
        shift
        exec flask db migrate -m "${1:-Auto migration}" "$@"
        ;;
    "upgrade")
        print_info "Ejecutando upgrade de base de datos..."
        shift
        exec flask db upgrade "$@"
        ;;
    "init-db")
        print_info "Inicializando base de datos..."
        shift
        exec python scripts/init_db.py "$@"
        ;;
    "test")
        print_info "Ejecutando tests..."
        shift
        exec pytest "$@"
        ;;
    "lint")
        print_info "Ejecutando linting..."
        shift
        exec flake8 app tests "$@"
        ;;
    "format")
        print_info "Formateando código..."
        shift
        black app tests && isort app tests
        ;;
    "bash")
        print_info "Iniciando bash shell..."
        shift
        exec /bin/bash "$@"
        ;;
    *)
        print_info "Iniciando comando personalizado: $@"
        exec "$@"
        ;;
esac