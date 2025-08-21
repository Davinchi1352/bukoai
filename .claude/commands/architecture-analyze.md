---
allowed-tools: Task
argument-hint: [full|dependencies|structure|patterns]
description: Analizar arquitectura completa del proyecto
---

## Estructura del Proyecto
- Archivos Python: !`find . -name "*.py" | wc -l`
- Templates: !`find app/templates -name "*.html" | wc -l`
- Líneas de código: !`find . -name "*.py" -exec wc -l {} + | tail -1`
- Estructura principal: !`tree -L 2 -d 2>/dev/null | head -20`

## Tu Tarea

Analiza la arquitectura ${ARGUMENTS:-completa} del proyecto usando el agente analizador-arquitectura.

Mapear y documentar:
1. **Estructura de directorios**: Organización y propósito
2. **Componentes principales**: Módulos y sus responsabilidades
3. **Flujos de datos**: Request/response pipelines
4. **Patrones de diseño**: Factory, Repository, etc.
5. **Dependencias**: Internas y externas
6. **Integraciones**: APIs, servicios externos
7. **Puntos de extensión**: Plugins, hooks

Generar:
- Diagrama de arquitectura
- Mapa de dependencias
- Documentación técnica
- Recomendaciones de mejora