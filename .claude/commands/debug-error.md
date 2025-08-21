---
allowed-tools: Task
argument-hint: <mensaje_de_error_o_traceback>
description: Analizar y resolver error específico
---

## Error a Analizar: ${ARGUMENTS}

## Contexto de Debugging
- Logs recientes: !`docker exec buko-ai-web-dev tail -20 logs/app.log 2>/dev/null | grep -i error || echo "No errors"`
- Celery errors: !`docker exec buko-ai-worker-dev tail -20 logs/celery.log 2>/dev/null | grep -i error || echo "No errors"`
- Tracebacks: !`docker exec buko-ai-web-dev grep -r "Traceback" logs/ 2>/dev/null | tail -5 || echo "No tracebacks"`

## Tu Tarea

Analiza y resuelve el error "${ARGUMENTS}" usando el agente depurador.

Investigar:
1. **Stack trace completo**: Línea exacta del error
2. **Contexto del error**: Variables, estado
3. **Reproducción**: Pasos para reproducir
4. **Causa raíz**: Análisis profundo
5. **Impacto**: Qué funcionalidades afecta
6. **Historial**: Errores similares previos

Entregar:
- Diagnóstico completo
- Solución con código
- Tests para prevenir regresión
- Documentación del fix