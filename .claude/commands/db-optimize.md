---
allowed-tools: Task
argument-hint: [queries|schema|indexes|all]
description: Optimizar base de datos y queries SQLAlchemy
---

## Estado de Base de Datos
- Tamaño DB: !`psql -U postgres -d bukoai -c "SELECT pg_database_size('bukoai')/1024/1024 as size_mb" 2>/dev/null | grep -E "[0-9]+"`
- Tablas: !`psql -U postgres -d bukoai -c "\dt" 2>/dev/null | grep -c rows`
- Índices: !`psql -U postgres -d bukoai -c "\di" 2>/dev/null | grep -c rows`
- Modelos SQLAlchemy: @app/models.py

## Tu Tarea

Optimiza ${ARGUMENTS:-todo} en la base de datos usando el agente database-optimizer.

Analizar y optimizar:
1. **Queries lentas**: EXPLAIN ANALYZE de queries problemáticas
2. **Índices faltantes**: Columnas frecuentes en WHERE/JOIN
3. **N+1 queries**: Eager loading con SQLAlchemy
4. **Connection pooling**: Configuración óptima
5. **Vacuum y Analyze**: Mantenimiento de PostgreSQL
6. **Particionamiento**: Tablas grandes (books, generations)
7. **Caché de queries**: Redis integration

Generar:
- Scripts de optimización
- Migraciones necesarias
- Mejoras en modelos SQLAlchemy