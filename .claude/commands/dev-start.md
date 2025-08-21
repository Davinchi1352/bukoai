---
allowed-tools: Bash(docker:*), Bash(make:*), Bash(python:*), Bash(redis-cli:*)
argument-hint: [full|minimal|debug]
description: Iniciar entorno de desarrollo BukoAI
---

## Estado del Sistema
- Docker: !`docker ps | grep -c buko-ai || echo "0 containers"`
- PostgreSQL: !`docker exec buko-ai-db-dev pg_isready 2>/dev/null || echo "PostgreSQL offline"`
- Redis: !`docker exec buko-ai-redis-dev redis-cli ping 2>/dev/null || echo "Redis offline"`
- Celery: !`docker exec buko-ai-worker-dev ps aux | grep celery | grep -v grep | wc -l 2>/dev/null || echo "0"`

## Tu Tarea

Iniciar el entorno de desarrollo ${ARGUMENTS:-completo}:

1. **Verificar dependencias**:
   - Python 3.10+
   - PostgreSQL 14+
   - Redis 6+
   - Node.js 16+ (para assets)

2. **Levantar servicios**:
   - Docker containers (DB, Redis)
   - Aplicar migraciones pendientes
   - Seed de datos de prueba

3. **Iniciar aplicación**:
   - Flask en modo debug
   - Celery workers
   - Celery beat scheduler

4. **Verificar salud**:
   - Endpoints principales
   - Conexión a Claude API
   - Workers activos

Mostrar:
- URLs de acceso
- Credenciales de prueba
- Logs en tiempo real