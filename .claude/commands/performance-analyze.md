---
allowed-tools: Task
argument-hint: [full|api|database|frontend]
description: Análisis completo de rendimiento del sistema
---

## Métricas Actuales
- Procesos Python: !`docker exec buko-ai-web-dev ps aux | grep python | wc -l 2>/dev/null || echo "0"`
- Uso de memoria: !`docker exec buko-ai-web-dev free -h | grep Mem 2>/dev/null || echo "N/A"`
- Conexiones DB: !`docker exec buko-ai-db-dev netstat -an | grep 5432 | wc -l 2>/dev/null || echo "0"`
- Workers Celery: !`docker exec buko-ai-worker-dev celery -A app.celery inspect active 2>/dev/null | grep -c "worker" || echo "0"`

## Tu Tarea

Realiza un análisis de rendimiento ${ARGUMENTS:-completo} usando el agente performance-analyzer.

Analizar:
1. **Endpoints lentos**: Tiempos de respuesta > 500ms
2. **Queries de base de datos**: N+1, missing indexes
3. **Uso de memoria**: Memory leaks, objetos grandes
4. **Caché**: Estrategias de Redis, hit rates
5. **Celery workers**: Throughput, queue lengths
6. **Claude API**: Latencia, retry patterns
7. **Static files**: Compresión, CDN readiness

Generar reporte con:
- Top 10 bottlenecks
- Quick wins (mejoras fáciles)
- Optimizaciones sugeridas con impacto estimado