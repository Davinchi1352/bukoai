---
allowed-tools: Task
argument-hint: [major|minor|patch]
description: Preparación completa para release (multi-agente)
model: claude-3-5-sonnet-20241022
---

## Versión Actual
- Version: !`grep version setup.py 2>/dev/null || grep version pyproject.toml`
- Último tag: !`git describe --tags --abbrev=0 2>/dev/null`
- Commits desde último release: !`git log --oneline $(git describe --tags --abbrev=0)..HEAD | wc -l`

## Tu Tarea

Prepara un release ${ARGUMENTS:-minor} completo coordinando múltiples agentes:

### 1. Seguridad (guardian-seguridad)
- Auditoría completa de vulnerabilidades
- Validación de configuraciones
- Revisión de secrets

### 2. Testing (arquitecto-pruebas)
- Ejecutar suite completa
- Verificar coverage > 80%
- Tests de integración

### 3. Performance (analizador-rendimiento)
- Verificar no hay regresiones
- Optimizaciones finales
- Benchmark vs versión anterior

### 4. Documentación (documentador-integral)
- Actualizar CHANGELOG
- Documentar nuevas features
- Release notes

### 5. Deployment (gestor-despliegue)
- Generar paquete de despliegue
- Scripts y configuraciones
- Rollback plan

Generar:
- Checklist completo
- Release tag
- Artifacts listos
- Documentación actualizada