---
allowed-tools: Bash, Task
argument-hint: [quick|full|stress]
description: Test completo del pipeline de generación de libros
---

## Sistema de Generación
- Claude API Key: !`grep ANTHROPIC .env`
- Celery workers: !`docker exec buko-ai-worker-dev celery -A app.celery inspect active 2>/dev/null || echo 'Celery no activo'`
- Redis queue: !`docker exec buko-ai-redis-dev redis-cli llen celery 2>/dev/null || echo 'Redis no activo'`

## Tu Tarea

Ejecuta test ${ARGUMENTS:-completo} del pipeline de generación:

1. **Crear libro de prueba**:
   - Título: "Test Book - ${ARGUMENTS}"
   - Tema: Tecnología
   - Capítulos: 3-5

2. **Monitorear generación**:
   - Progress tracking
   - Llamadas a Claude API
   - Uso de tokens
   - Tiempo total

3. **Validar resultado**:
   - Contenido generado
   - Formato y estructura
   - Guardado en DB
   - Archivos creados

4. **Stress test** (si aplica):
   - Múltiples libros simultáneos
   - Límites de rate
   - Manejo de errores

Reportar:
- Métricas de generación
- Problemas encontrados
- Optimizaciones sugeridas