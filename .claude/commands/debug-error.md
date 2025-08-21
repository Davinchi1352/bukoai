---
allowed-tools: Task
argument-hint: <mensaje_de_error_o_traceback>
description: Analizar y resolver error específico
---

## Error a Analizar: ${ARGUMENTS}

## Contexto de Debugging
- Logs recientes: !`tail -20 logs/app.log 2>/dev/null | grep -i error`
- Celery errors: !`tail -20 logs/celery.log 2>/dev/null | grep -i error`
- Tracebacks: !`grep -r "Traceback" logs/ | tail -5`

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