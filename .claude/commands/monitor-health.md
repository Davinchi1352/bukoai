---
allowed-tools: Bash(ps:*), Bash(docker:*), Bash(redis-cli:*), Bash(curl:*)
argument-hint: [quick|detailed|continuous]
description: Monitoreo de salud del sistema en tiempo real
---

## Health Check Rápido
- Flask app: !`curl -s http://localhost:5000/health 2>/dev/null || echo "App offline"`
- PostgreSQL: !`pg_isready -h localhost -p 5432 2>/dev/null || echo "DB offline"`
- Redis: !`redis-cli ping 2>/dev/null || echo "Redis offline"`
- Celery: !`celery -A app.celery inspect ping 2>/dev/null | grep -c pong`

## Tu Tarea

Monitorea la salud del sistema (modo: ${ARGUMENTS:-quick}):

### Verificaciones Principales:
1. **Servicios**:
   - Flask application
   - PostgreSQL database
   - Redis cache
   - Celery workers
   - Celery beat

2. **Recursos**:
   - CPU usage
   - Memory consumption
   - Disk space
   - Network latency

3. **Application**:
   - Response times
   - Error rates
   - Queue lengths
   - Active users

4. **External Services**:
   - Claude API status
   - Payment gateways
   - Email service

Reportar:
- Status dashboard
- Alertas críticas
- Tendencias preocupantes