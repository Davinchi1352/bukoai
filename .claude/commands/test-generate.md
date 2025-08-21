---
allowed-tools: Task
argument-hint: <modulo_o_archivo>
description: Generar tests completos para módulo específico
---

## Módulo a Testear: ${ARGUMENTS}

## Contexto de Testing
- Framework: !`grep pytest requirements.txt || echo "No pytest found"`
- Coverage actual: !`docker exec buko-ai-web-dev coverage report 2>/dev/null | grep "${ARGUMENTS}" || echo "Sin coverage"`
- Tests existentes: !`find tests -name "*${ARGUMENTS}*" 2>/dev/null | head -5`
- Código a testear: @${ARGUMENTS}

## Tu Tarea

Genera tests completos para ${ARGUMENTS} usando el agente test-architect.

Crear:
1. **Unit tests**: Funciones individuales
2. **Integration tests**: Flujos completos
3. **Edge cases**: Validaciones y errores
4. **Fixtures**: Datos de prueba
5. **Mocks**: Servicios externos (Claude API)
6. **Parametrización**: Múltiples escenarios

Asegurar:
- Coverage > 90%
- Tests independientes
- Nombres descriptivos
- Assertions claras