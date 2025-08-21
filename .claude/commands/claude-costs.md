---
allowed-tools: Task, Bash(grep:*)
argument-hint: [daily|weekly|monthly|per-user]
description: Analizar costos y uso de Claude API
---

## Uso de Claude API
- Llamadas hoy: !`docker exec buko-ai-web-dev grep -c "claude.ai" logs/api.log 2>/dev/null || echo "0"`
- Tokens consumidos: !`docker exec buko-ai-web-dev grep "tokens_used" logs/metrics.log 2>/dev/null | tail -5 || echo "N/A"`
- Errores de API: !`docker exec buko-ai-web-dev grep -c "anthropic.*error" logs/app.log 2>/dev/null || echo "0"`

## Tu Tarea

Analiza costos de Claude API (período: ${ARGUMENTS:-monthly}) usando el agente agente-inteligencia-negocio:

### Análisis Requerido:
1. **Consumo de Tokens**:
   - Tokens por libro generado
   - Promedio por usuario
   - Tendencia de consumo
   - Picos de uso

2. **Costos**:
   - Costo total del período
   - Costo por tier de usuario
   - ROI por suscripción
   - Proyección mensual

3. **Optimizaciones**:
   - Prompts más eficientes
   - Caching de respuestas
   - Batch processing
   - Modelo más económico

4. **Alertas**:
   - Uso excesivo
   - Rate limit warnings
   - Anomalías en consumo

Generar:
- Dashboard de costos
- Recomendaciones de ahorro
- Forecast de gastos