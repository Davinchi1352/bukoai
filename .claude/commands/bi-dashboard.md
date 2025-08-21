---
allowed-tools: Task
argument-hint: [kpis|retention|revenue|usage]
description: Generar dashboard de inteligencia de negocio
---

## Métricas Disponibles
- Usuarios totales: !`docker exec buko-ai-db-dev psql -U postgres -d bukoai -c "SELECT COUNT(*) FROM users" 2>/dev/null | grep -E "[0-9]+" | head -1 || echo "0"`
- Libros generados: !`docker exec buko-ai-db-dev psql -U postgres -d bukoai -c "SELECT COUNT(*) FROM books" 2>/dev/null | grep -E "[0-9]+" | head -1 || echo "0"`
- Suscripciones activas: !`docker exec buko-ai-db-dev psql -U postgres -d bukoai -c "SELECT subscription_tier, COUNT(*) FROM users GROUP BY subscription_tier" 2>/dev/null || echo "N/A"`

## Tu Tarea

Genera un dashboard de ${ARGUMENTS:-KPIs completos} usando el agente agente-inteligencia-negocio.

Analizar y visualizar:
1. **KPIs Principales**:
   - MRR (Monthly Recurring Revenue)
   - CAC (Customer Acquisition Cost)
   - LTV (Lifetime Value)
   - Churn rate
2. **Retención de Usuarios**:
   - Cohort analysis
   - Engagement metrics
   - Feature adoption
3. **Revenue Analytics**:
   - Revenue por tier
   - Upgrade/downgrade patterns
   - Forecast proyecciones
4. **Uso de Claude API**:
   - Tokens consumidos
   - Costo por libro
   - ROI por tier

Generar:
- Dashboard interactivo
- Queries SQL optimizadas
- Visualizaciones clave
- Insights accionables