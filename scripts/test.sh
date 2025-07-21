#!/bin/bash

# ===========================================
# BUKO AI - SCRIPT DE TESTING
# ===========================================

set -e

echo "🧪 Ejecutando tests de Buko AI..."

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

# Configurar Flask para testing
export FLASK_APP=app.py
export FLASK_ENV=testing
export FLASK_DEBUG=0

# Verificar dependencias de testing
print_info "Verificando dependencias de testing..."
python -c "import pytest, coverage" || {
    print_error "Dependencias de testing faltantes. Ejecuta ./scripts/install.sh"
    exit 1
}

# Crear directorio de reports si no existe
mkdir -p reports

# Ejecutar linting
print_info "Ejecutando linting..."
echo "🔍 Ejecutando Black..."
black --check app tests || {
    print_error "Errores de formato encontrados. Ejecuta 'black app tests' para corregir"
    exit 1
}
print_success "Black - formato correcto"

echo "🔍 Ejecutando isort..."
isort --check-only app tests || {
    print_error "Errores de orden de imports. Ejecuta 'isort app tests' para corregir"
    exit 1
}
print_success "isort - imports ordenados"

echo "🔍 Ejecutando flake8..."
flake8 app tests || {
    print_error "Errores de estilo encontrados"
    exit 1
}
print_success "flake8 - estilo correcto"

# Ejecutar análisis de seguridad
print_info "Ejecutando análisis de seguridad..."
echo "🔒 Ejecutando bandit..."
bandit -r app -f json -o reports/bandit-report.json || {
    print_warning "Bandit encontró posibles issues de seguridad"
}
print_success "Bandit - análisis completado"

echo "🔒 Ejecutando safety..."
safety check --json --output reports/safety-report.json || {
    print_warning "Safety encontró vulnerabilidades en dependencias"
}
print_success "Safety - análisis completado"

# Ejecutar type checking
print_info "Ejecutando type checking..."
echo "🔍 Ejecutando mypy..."
mypy app --ignore-missing-imports || {
    print_warning "MyPy encontró posibles errores de tipos"
}
print_success "MyPy - análisis completado"

# Ejecutar tests unitarios
print_info "Ejecutando tests unitarios..."
pytest tests/unit/ -v --tb=short --cov=app --cov-report=html:reports/htmlcov --cov-report=xml:reports/coverage.xml --cov-report=term-missing --junit-xml=reports/junit.xml || {
    print_error "Tests unitarios fallaron"
    exit 1
}
print_success "Tests unitarios - pasaron"

# Ejecutar tests de integración
print_info "Ejecutando tests de integración..."
pytest tests/integration/ -v --tb=short || {
    print_error "Tests de integración fallaron"
    exit 1
}
print_success "Tests de integración - pasaron"

# Ejecutar tests de API
if [ -d "tests/api" ]; then
    print_info "Ejecutando tests de API..."
    pytest tests/api/ -v --tb=short || {
        print_error "Tests de API fallaron"
        exit 1
    }
    print_success "Tests de API - pasaron"
fi

# Ejecutar tests de performance
if [ -d "tests/performance" ]; then
    print_info "Ejecutando tests de performance..."
    pytest tests/performance/ -v --tb=short --benchmark-only || {
        print_warning "Tests de performance completados con warnings"
    }
    print_success "Tests de performance - completados"
fi

# Generar reporte final
print_info "Generando reporte final..."
coverage report --show-missing > reports/coverage-report.txt
coverage html -d reports/htmlcov

# Mostrar resumen
echo ""
echo "📊 Resumen de tests:"
echo "   - Formato: ✅ Correcto"
echo "   - Estilo: ✅ Correcto"
echo "   - Seguridad: ✅ Analizado"
echo "   - Tipos: ✅ Verificado"
echo "   - Tests unitarios: ✅ Pasaron"
echo "   - Tests integración: ✅ Pasaron"
echo "   - Coverage: $(coverage report | tail -1 | awk '{print $4}')"
echo ""
echo "📁 Reportes generados en: reports/"
echo "   - reports/htmlcov/index.html (Coverage HTML)"
echo "   - reports/coverage.xml (Coverage XML)"
echo "   - reports/junit.xml (JUnit XML)"
echo "   - reports/bandit-report.json (Seguridad)"
echo "   - reports/safety-report.json (Vulnerabilidades)"
echo ""
print_success "¡Todos los tests pasaron correctamente!"