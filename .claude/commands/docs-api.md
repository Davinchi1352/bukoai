---
allowed-tools: Task
argument-hint: [openapi|swagger|postman|all]
description: Generar documentación completa de API
---

## Endpoints Existentes
- Total rutas: !`grep -r "@.*route" app/ | wc -l`
- Blueprints: !`grep -r "Blueprint" app/ | grep -v import`
- Métodos HTTP: !`grep -r "methods=" app/ | head -10`

## Tu Tarea

Genera documentación de API ${ARGUMENTS:-completa} usando el agente documentador-integral.

Crear:
1. **OpenAPI Spec**: Definición completa en YAML/JSON
2. **Swagger UI**: Interfaz interactiva
3. **Endpoints documentation**:
   - Parámetros requeridos/opcionales
   - Request/Response schemas
   - Códigos de estado
   - Ejemplos de uso
4. **Autenticación**: Flujos y tokens
5. **Rate limiting**: Límites por tier
6. **Webhooks**: Eventos y payloads
7. **SDKs**: Python, JavaScript examples

Formatos:
- OpenAPI 3.0
- Postman collection
- Markdown documentation