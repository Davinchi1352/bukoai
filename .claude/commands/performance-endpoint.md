---
allowed-tools: Task
argument-hint: <ruta_endpoint>
description: Analizar rendimiento de endpoint específico
---

## Endpoint a Analizar: ${ARGUMENTS}

## Contexto del Endpoint
- Rutas disponibles: !`grep -r "@app.route\|@.*blueprint.route" app/ | grep "${ARGUMENTS}" | head -5`
- Función handler: !`grep -A 20 "${ARGUMENTS}" app/`

## Tu Tarea

Analiza el rendimiento del endpoint ${ARGUMENTS} usando el agente performance-analyzer.

Evaluar:
1. Tiempo de respuesta promedio
2. Queries ejecutadas
3. Uso de caché
4. Serialización de datos
5. Middleware overhead
6. Potencial para async

Optimizaciones:
- Query optimization
- Caching strategy
- Response pagination
- Lazy loading