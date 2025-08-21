---
allowed-tools: Task
argument-hint: <numero_usuarios_concurrentes>
description: Analizar capacidad de escalamiento para N usuarios
model: claude-3-5-sonnet-20241022
---

## Objetivo de Escalamiento: ${ARGUMENTS:-10000} usuarios concurrentes

## Infraestructura Actual
- CPU cores: !`nproc`
- RAM disponible: !`free -g | grep Mem | awk '{print $2}'`
- Workers configurados: !`grep -r "CELERY_WORKER\|WORKERS" config/ .env`
- Pool de conexiones DB: !`grep -r "SQLALCHEMY_POOL\|pool_size" config/`

## Tu Tarea

Analiza la capacidad de escalamiento para ${ARGUMENTS:-10000} usuarios concurrentes usando el agente experto-escalabilidad.

Evaluar:
1. **Base de datos**: Connection pooling, read replicas necesarias
2. **Aplicación Flask**: Gunicorn workers, threading
3. **Celery**: Workers necesarios, queue partitioning
4. **Redis**: Memory requirements, clustering
5. **Claude API**: Rate limits, concurrent requests
6. **File storage**: I/O bottlenecks, S3 migration
7. **Network**: Bandwidth, load balancing

Generar:
- Capacidad actual real
- Bottlenecks para objetivo
- Plan de escalamiento por fases
- Costos estimados de infraestructura
- Timeline de implementación