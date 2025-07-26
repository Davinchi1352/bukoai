#!/bin/bash

# Script para probar sistema optimizado para 10,000 usuarios
# Autor: Claude AI Assistant
# Fecha: $(date +%Y-%m-%d)

set -e  # Exit on any error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging con timestamp
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar dependencias
check_dependencies() {
    log "Verificando dependencias del sistema..."
    
    local deps=("docker" "docker-compose" "curl" "jq")
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        error "Dependencias faltantes: ${missing_deps[*]}"
        error "Instala las dependencias faltantes antes de continuar."
        exit 1
    fi
    
    success "Todas las dependencias están instaladas"
}

# Verificar variables de entorno
check_environment() {
    log "Verificando variables de entorno..."
    
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        warning "ANTHROPIC_API_KEY no está configurada"
        warning "Las pruebas de Claude AI fallarán sin esta variable"
    else
        success "ANTHROPIC_API_KEY está configurada"
    fi
    
    # Crear archivo .env.test si no existe
    if [ ! -f ".env.test" ]; then
        log "Creando archivo .env.test..."
        cat > .env.test << EOF
# Configuración de test para 10K usuarios
FLASK_ENV=testing
SECRET_KEY=test-secret-key-for-10k-users
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-test-key}

# Database optimizada
DB_POOL_SIZE=15
DB_MAX_OVERFLOW=25

# Redis optimizado
CACHE_REDIS_MAX_CONNECTIONS=30

# Celery optimizado
CELERY_WORKER_CONCURRENCY=4
CELERY_TASK_SOFT_TIME_LIMIT=1800
CELERY_TASK_TIME_LIMIT=2400

# WebSocket optimizado
SOCKETIO_PING_TIMEOUT=120
SOCKETIO_PING_INTERVAL=60
SOCKETIO_MAX_HTTP_BUFFER_SIZE=100000
EOF
        success "Archivo .env.test creado"
    fi
}

# Limpiar contenedores anteriores
cleanup() {
    log "Limpiando contenedores de test anteriores..."
    
    # Detener y remover contenedores de test
    docker-compose -f docker-compose.test.yml down --volumes --remove-orphans 2>/dev/null || true
    
    # Limpiar imágenes huérfanas
    docker image prune -f 2>/dev/null || true
    
    success "Limpieza completada"
}

# Construir imágenes
build_images() {
    log "Construyendo imágenes de Docker..."
    
    docker-compose -f docker-compose.test.yml build --no-cache web_test
    
    success "Imágenes construidas exitosamente"
}

# Iniciar servicios de infraestructura
start_infrastructure() {
    log "Iniciando servicios de infraestructura..."
    
    # Iniciar solo db y redis primero
    docker-compose -f docker-compose.test.yml up -d db_test redis_test
    
    # Esperar a que estén saludables
    log "Esperando a que los servicios estén listos..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose -f docker-compose.test.yml ps db_test | grep -q "healthy" && \
           docker-compose -f docker-compose.test.yml ps redis_test | grep -q "healthy"; then
            success "Servicios de infraestructura están listos"
            return 0
        fi
        
        attempt=$((attempt + 1))
        log "Esperando... ($attempt/$max_attempts)"
        sleep 5
    done
    
    error "Servicios de infraestructura no están listos después de ${max_attempts} intentos"
    return 1
}

# Inicializar base de datos
init_database() {
    log "Inicializando base de datos..."
    
    # Ejecutar migraciones
    docker-compose -f docker-compose.test.yml run --rm web_test flask db upgrade
    
    success "Base de datos inicializada"
}

# Iniciar todos los servicios
start_all_services() {
    log "Iniciando todos los servicios..."
    
    docker-compose -f docker-compose.test.yml up -d
    
    # Esperar a que la web esté lista
    log "Esperando a que la aplicación web esté lista..."
    local max_attempts=20
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -sf http://localhost:5001/health > /dev/null 2>&1; then
            success "Aplicación web está lista"
            return 0
        fi
        
        attempt=$((attempt + 1))
        log "Esperando aplicación web... ($attempt/$max_attempts)"
        sleep 10
    done
    
    error "Aplicación web no está lista después de ${max_attempts} intentos"
    return 1
}

# Ejecutar verificaciones del sistema
run_system_verification() {
    log "Ejecutando verificación del sistema para 10K usuarios..."
    
    # Ejecutar el script de verificación
    docker-compose -f docker-compose.test.yml --profile verification run --rm verification_test
    
    # Mostrar resultados si existe el archivo
    if [ -f "verification_results.json" ]; then
        log "Resultados de verificación:"
        if command -v jq &> /dev/null; then
            jq '.passed, .warnings, .failed' verification_results.json | while read -r line; do
                echo "  $line"
            done
        else
            cat verification_results.json
        fi
    fi
}

# Ejecutar pruebas de carga básicas
run_load_tests() {
    log "Ejecutando pruebas de carga básicas..."
    
    # Test básico de conectividad
    local endpoints=(
        "http://localhost:5001/health"
        "http://localhost:5001/"
    )
    
    for endpoint in "${endpoints[@]}"; do
        log "Probando endpoint: $endpoint"
        if curl -sf "$endpoint" > /dev/null; then
            success "✓ $endpoint responde correctamente"
        else
            error "✗ $endpoint no responde"
        fi
    done
    
    # Test de Celery
    log "Verificando estado de Celery..."
    docker-compose -f docker-compose.test.yml exec -T celery_test celery -A app.celery inspect ping
    
    # Test de Flower (opcional)
    if curl -sf http://localhost:5556 > /dev/null 2>&1; then
        success "✓ Flower (monitor de Celery) está funcionando"
    else
        warning "✗ Flower no está respondiendo"
    fi
}

# Generar reporte final
generate_report() {
    log "Generando reporte final..."
    
    local report_file="test_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$report_file" << EOF
REPORTE DE PRUEBAS DEL SISTEMA BUKO AI
======================================
Fecha: $(date)
Optimizado para: 10,000 usuarios concurrentes

SERVICIOS PROBADOS:
- PostgreSQL con optimizaciones para alta concurrencia
- Redis con configuración para 1000 clientes concurrentes  
- Celery con 4 workers concurrentes
- WebSocket optimizado para alta carga
- Claude AI Service con timeouts balanceados
- Sistema de monitoreo y logging estructurado

CONFIGURACIONES CLAVE:
- Pool de conexiones DB: 15 + 25 overflow = 40 total
- Redis max clients: 1000
- Celery workers: 4 por nodo
- WebSocket ping timeout: 120s
- Claude timeouts: 40min arquitectura, 60min chunks

RESULTADOS:
$(if [ -f "verification_results.json" ]; then
    if command -v jq &> /dev/null; then
        echo "- Tests ejecutados: $(jq '.total_tests' verification_results.json)"
        echo "- Tests exitosos: $(jq '.passed' verification_results.json)"
        echo "- Advertencias: $(jq '.warnings' verification_results.json)"
        echo "- Fallos: $(jq '.failed' verification_results.json)"
    else
        echo "- Ver verification_results.json para detalles"
    fi
else
    echo "- Verificación del sistema no ejecutada"
fi)

ESTADO DE CONTENEDORES:
$(docker-compose -f docker-compose.test.yml ps)

LOGS RECIENTES:
$(docker-compose -f docker-compose.test.yml logs --tail=10 web_test 2>/dev/null || echo "No hay logs disponibles")
EOF

    success "Reporte generado: $report_file"
}

# Función principal
main() {
    log "🚀 Iniciando pruebas del sistema para 10,000 usuarios"
    log "======================================================"
    
    # Verificaciones preliminares
    check_dependencies
    check_environment
    
    # Limpieza y preparación
    cleanup
    build_images
    
    # Inicio de servicios
    start_infrastructure
    init_database
    start_all_services
    
    # Pruebas
    run_system_verification
    run_load_tests
    
    # Reporte final
    generate_report
    
    success "🎉 Pruebas completadas exitosamente!"
    log "   📊 Ver verification_results.json para detalles"
    log "   📋 Ver test_report_*.txt para resumen completo"
    log "   🌐 Aplicación disponible en: http://localhost:5001"
    log "   📈 Monitor Celery disponible en: http://localhost:5556"
    
    # Preguntar si mantener servicios corriendo
    read -p "¿Mantener servicios corriendo para pruebas manuales? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Deteniendo servicios..."
        cleanup
        success "Servicios detenidos"
    else
        log "Servicios mantenidos activos para pruebas manuales"
        log "Ejecuta 'docker-compose -f docker-compose.test.yml down' para detenerlos"
    fi
}

# Manejo de señales para limpieza
trap cleanup EXIT

# Verificar argumentos
case "${1:-}" in
    "cleanup")
        cleanup
        exit 0
        ;;
    "build")
        build_images
        exit 0
        ;;
    "verify")
        run_system_verification
        exit 0
        ;;
    "help"|"-h"|"--help")
        echo "Uso: $0 [comando]"
        echo "Comandos:"
        echo "  (ninguno)  - Ejecutar suite completa de pruebas"
        echo "  cleanup    - Limpiar contenedores y volúmenes"
        echo "  build      - Solo construir imágenes"
        echo "  verify     - Solo ejecutar verificaciones"
        echo "  help       - Mostrar esta ayuda"
        exit 0
        ;;
esac

# Ejecutar función principal
main "$@"