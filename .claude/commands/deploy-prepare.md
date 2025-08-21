---
allowed-tools: Task
argument-hint: [staging|production|docker]
description: Preparar paquete de despliegue completo
---

## Verificaciones Pre-Deploy
- Tests passing: !`pytest --co -q 2>/dev/null | tail -1`
- Linting: !`ruff check . 2>/dev/null | tail -1`
- Migraciones: !`alembic current 2>/dev/null`
- Secrets: !`grep -c "SECRET\|KEY\|TOKEN" .env.example`

## Tu Tarea

Prepara el despliegue ${ARGUMENTS:-production} usando el agente deployment-manager.

Generar:
1. **Docker Configuration**:
   - Dockerfile optimizado multi-stage
   - docker-compose.yml production
   - .dockerignore actualizado
2. **Scripts de Despliegue**:
   - deploy.sh automatizado
   - Health checks
   - Rollback procedure
3. **Configuraciones**:
   - Nginx config
   - Gunicorn settings
   - Supervisor config
4. **Seguridad**:
   - SSL certificates
   - Firewall rules
   - Environment variables
5. **Monitoring**:
   - Prometheus metrics
   - Logging setup
   - Alerts configuration

Documentación:
- Step-by-step deployment
- Troubleshooting guide
- Rollback procedures