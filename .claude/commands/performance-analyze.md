---
allowed-tools: Task
argument-hint: [full|api|database|frontend]
description: Análisis completo de rendimiento del sistema
---

## Métricas Actuales
- Procesos Python: !`ps aux | grep python | wc -l`
- Uso de memoria: !`free -h | grep Mem`
- Conexiones DB: !`netstat -an | grep 5432 | wc -l`
- Workers Celery: !`celery -A app.celery inspect active 2>/dev/null | grep -c "worker"`

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