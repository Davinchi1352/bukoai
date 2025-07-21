# ===========================================
# BUKO AI - DOCKERFILE
# ===========================================

# Usar Python 3.12 slim como base
FROM python:3.12-slim

# Metadata
LABEL maintainer="Buko AI Team <soporte@buko-ai.com>"
LABEL description="Buko AI - Generador de libros con IA"
LABEL version="0.1.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PATH="/app/.venv/bin:$PATH"

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    pkg-config \
    curl \
    wget \
    git \
    redis-tools \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash app && \
    mkdir -p /app /storage/uploads /storage/books /storage/covers /app/logs && \
    chown -R app:app /app /storage

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt pyproject.toml ./

# Instalar dependencias de Python y desinstalar eventlet
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    pip uninstall -y eventlet

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p logs storage/uploads storage/books storage/covers migrations/versions

# Configurar permisos
RUN chown -R app:app /app /storage && \
    find scripts -name "*.sh" -exec chmod +x {} \; || true

# Cambiar a usuario no-root
USER app

# Crear punto de entrada
COPY docker/entrypoint.sh /entrypoint.sh
COPY docker/entrypoint-celery.sh /entrypoint-celery.sh
USER root
RUN chmod +x /entrypoint.sh /entrypoint-celery.sh
USER app

# Exponer puerto
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Punto de entrada
ENTRYPOINT ["/entrypoint.sh"]

# Comando por defecto
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--worker-class", "sync", "--timeout", "30", "--keep-alive", "2", "--max-requests", "1000", "--max-requests-jitter", "50", "--preload", "--log-level", "info", "--access-logfile", "-", "--error-logfile", "-", "app:app"]