# ===========================================
# BUKO AI - MAKEFILE
# ===========================================

.PHONY: help install dev prod test clean lint format docker-build docker-up docker-down

# Colores para output
BLUE=\033[0;34m
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

# Ayuda por defecto
help:
	@echo "$(BLUE)🚀 Buko AI - Comandos disponibles:$(NC)"
	@echo ""
	@echo "$(GREEN)📦 Instalación:$(NC)"
	@echo "  make install     - Instalar dependencias y configurar proyecto"
	@echo "  make clean       - Limpiar archivos temporales y caché"
	@echo ""
	@echo "$(GREEN)🔧 Desarrollo:$(NC)"
	@echo "  make dev         - Iniciar servidor de desarrollo"
	@echo "  make prod        - Iniciar servidor de producción"
	@echo "  make test        - Ejecutar todos los tests"
	@echo "  make lint        - Ejecutar linting"
	@echo "  make format      - Formatear código automáticamente"
	@echo ""
	@echo "$(GREEN)🐳 Docker:$(NC)"
	@echo "  make docker-build - Construir imagen Docker"
	@echo "  make docker-up    - Levantar servicios con Docker Compose"
	@echo "  make docker-down  - Detener servicios Docker"
	@echo ""
	@echo "$(GREEN)📊 Base de datos:$(NC)"
	@echo "  make db-init     - Inicializar base de datos"
	@echo "  make db-migrate  - Crear nueva migración"
	@echo "  make db-upgrade  - Ejecutar migraciones"
	@echo "  make db-seed     - Poblar base de datos con datos de prueba"
	@echo ""

# Instalación
install:
	@echo "$(BLUE)📦 Instalando Buko AI...$(NC)"
	@chmod +x scripts/install.sh
	@./scripts/install.sh

# Desarrollo
dev:
	@echo "$(BLUE)🔧 Iniciando servidor de desarrollo...$(NC)"
	@chmod +x scripts/start-dev.sh
	@./scripts/start-dev.sh

# Producción
prod:
	@echo "$(BLUE)🚀 Iniciando servidor de producción...$(NC)"
	@chmod +x scripts/start-prod.sh
	@./scripts/start-prod.sh

# Testing
test:
	@echo "$(BLUE)🧪 Ejecutando tests...$(NC)"
	@chmod +x scripts/test.sh
	@./scripts/test.sh

# Linting
lint:
	@echo "$(BLUE)🔍 Ejecutando linting...$(NC)"
	@if [ -d "venv" ]; then \
		. venv/bin/activate && \
		echo "$(YELLOW)Ejecutando flake8...$(NC)" && \
		flake8 app tests && \
		echo "$(YELLOW)Ejecutando mypy...$(NC)" && \
		mypy app --ignore-missing-imports && \
		echo "$(YELLOW)Ejecutando bandit...$(NC)" && \
		bandit -r app && \
		echo "$(GREEN)✅ Linting completado$(NC)"; \
	else \
		echo "$(RED)❌ Entorno virtual no encontrado. Ejecuta 'make install' primero$(NC)"; \
	fi

# Formateo
format:
	@echo "$(BLUE)🎨 Formateando código...$(NC)"
	@if [ -d "venv" ]; then \
		. venv/bin/activate && \
		echo "$(YELLOW)Ejecutando black...$(NC)" && \
		black app tests && \
		echo "$(YELLOW)Ejecutando isort...$(NC)" && \
		isort app tests && \
		echo "$(GREEN)✅ Formateo completado$(NC)"; \
	else \
		echo "$(RED)❌ Entorno virtual no encontrado. Ejecuta 'make install' primero$(NC)"; \
	fi

# Docker
docker-build:
	@echo "$(BLUE)🐳 Construyendo imagen Docker...$(NC)"
	@docker-compose build

docker-up:
	@echo "$(BLUE)🐳 Levantando servicios con Docker Compose...$(NC)"
	@docker-compose up --build

docker-down:
	@echo "$(BLUE)🐳 Deteniendo servicios Docker...$(NC)"
	@docker-compose down

# Base de datos
db-init:
	@echo "$(BLUE)📊 Inicializando base de datos...$(NC)"
	@if [ -d "venv" ]; then \
		. venv/bin/activate && \
		export FLASK_APP=app.py && \
		flask db init; \
	else \
		echo "$(RED)❌ Entorno virtual no encontrado. Ejecuta 'make install' primero$(NC)"; \
	fi

db-migrate:
	@echo "$(BLUE)📊 Creando nueva migración...$(NC)"
	@if [ -d "venv" ]; then \
		. venv/bin/activate && \
		export FLASK_APP=app.py && \
		flask db migrate -m "$(MSG)"; \
	else \
		echo "$(RED)❌ Entorno virtual no encontrado. Ejecuta 'make install' primero$(NC)"; \
	fi

db-upgrade:
	@echo "$(BLUE)📊 Ejecutando migraciones...$(NC)"
	@if [ -d "venv" ]; then \
		. venv/bin/activate && \
		export FLASK_APP=app.py && \
		flask db upgrade; \
	else \
		echo "$(RED)❌ Entorno virtual no encontrado. Ejecuta 'make install' primero$(NC)"; \
	fi

db-seed:
	@echo "$(BLUE)📊 Poblando base de datos con datos de prueba...$(NC)"
	@if [ -d "venv" ]; then \
		. venv/bin/activate && \
		python scripts/init_db.py --development; \
	else \
		echo "$(RED)❌ Entorno virtual no encontrado. Ejecuta 'make install' primero$(NC)"; \
	fi

# Limpieza
clean:
	@echo "$(BLUE)🧹 Limpiando archivos temporales...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@rm -rf build/
	@rm -rf dist/
	@rm -rf .pytest_cache/
	@rm -rf .coverage
	@rm -rf reports/
	@rm -rf .mypy_cache/
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

# Comandos avanzados
deps-update:
	@echo "$(BLUE)📦 Actualizando dependencias...$(NC)"
	@if [ -d "venv" ]; then \
		. venv/bin/activate && \
		pip install --upgrade pip && \
		pip install -r requirements.txt --upgrade; \
	else \
		echo "$(RED)❌ Entorno virtual no encontrado. Ejecuta 'make install' primero$(NC)"; \
	fi

security-check:
	@echo "$(BLUE)🔒 Ejecutando análisis de seguridad...$(NC)"
	@if [ -d "venv" ]; then \
		. venv/bin/activate && \
		safety check && \
		bandit -r app; \
	else \
		echo "$(RED)❌ Entorno virtual no encontrado. Ejecuta 'make install' primero$(NC)"; \
	fi

# Comandos de utilidad
logs:
	@echo "$(BLUE)📋 Mostrando logs...$(NC)"
	@if [ -f "logs/buko-ai.log" ]; then \
		tail -f logs/buko-ai.log; \
	else \
		echo "$(YELLOW)⚠️  No se encontraron logs$(NC)"; \
	fi

status:
	@echo "$(BLUE)📊 Estado del proyecto:$(NC)"
	@echo ""
	@echo "$(GREEN)📁 Estructura:$(NC)"
	@ls -la
	@echo ""
	@if [ -d "venv" ]; then \
		echo "$(GREEN)🐍 Entorno virtual: ✅ Configurado$(NC)"; \
	else \
		echo "$(RED)🐍 Entorno virtual: ❌ No configurado$(NC)"; \
	fi
	@if [ -f ".env" ]; then \
		echo "$(GREEN)⚙️  Variables de entorno: ✅ Configuradas$(NC)"; \
	else \
		echo "$(RED)⚙️  Variables de entorno: ❌ No configuradas$(NC)"; \
	fi
	@if [ -d "migrations" ]; then \
		echo "$(GREEN)📊 Migraciones: ✅ Inicializadas$(NC)"; \
	else \
		echo "$(RED)📊 Migraciones: ❌ No inicializadas$(NC)"; \
	fi