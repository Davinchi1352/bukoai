---
allowed-tools: Task
argument-hint: [staging|production|docker]
description: Preparar paquete de despliegue completo
---

## Verificaciones Pre-Deploy
- Tests passing: !`docker exec buko-ai-web-dev pytest --co -q 2>/dev/null | tail -1 || echo "N/A"`
- Linting: !`docker exec buko-ai-web-dev ruff check . 2>/dev/null | tail -1 || echo "N/A"`
- Migraciones: !`docker exec buko-ai-web-dev alembic current 2>/dev/null || echo "N/A"`
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