---
allowed-tools: Task
argument-hint: [performance|database|code|fullstack|all]
description: Optimización integral del proyecto (multi-agente)
---

## Métricas Baseline
- Response time p95: !`docker exec buko-ai-web-dev grep "response_time" logs/metrics.log 2>/dev/null | tail -1 || echo "N/A"`
- DB queries promedio: !`docker exec buko-ai-web-dev grep "query_count" logs/metrics.log 2>/dev/null | tail -1 || echo "N/A"`
- Memory usage: !`docker exec buko-ai-web-dev ps aux | grep python | awk '{sum+=$4} END {print sum}' 2>/dev/null || echo "0"`

## Tu Tarea

Realiza optimización ${ARGUMENTS:-completa} coordinando múltiples agentes:

### 1. Backend Optimization (desarrollador-fullstack-backend)
- Optimizar sistemas backend preservando calidad de libros
- APIs robustas y escalables
- Integración Claude AI optimizada
- Containerización Docker

### 2. Performance (analizador-rendimiento)
- Identificar bottlenecks principales
- Optimizar endpoints lentos
- Mejorar tiempos de respuesta

### 3. Base de Datos (optimizador-base-datos)
- Optimizar queries lentas
- Añadir índices necesarios
- Eliminar N+1 queries

### 4. Código (limpiador-codigo-profundo)
- Eliminar código muerto
- Refactorizar duplicados
- Simplificar lógica compleja

### 5. Frontend (desarrollador-frontend-ux)
- Optimizar assets
- Lazy loading
- Minificación y compresión
- Coordinación perfecta con backend

### 6. Infraestructura (experto-escalabilidad)
- Configuración de caché
- Connection pooling
- Worker optimization

### Optimización Fullstack Especializada:
**Para `fullstack`:** Coordinación perfecta entre desarrollador-fullstack-backend y desarrollador-frontend-ux
**Para `performance`:** Focus en velocidad sin comprometer calidad
**Para `database`:** Optimización específica de DB
**Para `code`:** Limpieza de código y refactoring

Resultados esperados:
- -30% tiempo de respuesta
- -50% queries a DB
- -20% uso de memoria