---
allowed-tools: Task
argument-hint: [analyze|remove|all]
description: Eliminar código muerto y duplicados del proyecto
---

## Análisis Preliminar
- Archivos Python: !`find . -name "*.py" | wc -l`
- Imports no usados: !`ruff check --select F401 . 2>/dev/null | wc -l`
- Funciones sin referencias: !`grep -r "def " app/ | wc -l`

## Tu Tarea

Realiza limpieza de código ${ARGUMENTS:-completa} usando el agente limpiador-codigo-profundo.

Identificar y eliminar:
1. **Código muerto**:
   - Funciones nunca llamadas
   - Clases no instanciadas
   - Variables no usadas
   - Imports redundantes
2. **Código duplicado**:
   - Funciones repetidas
   - Lógica duplicada
   - Patterns copy-paste
3. **Código comentado**:
   - Bloques comentados antiguos
   - TODOs obsoletos
   - Debug prints
4. **Archivos huérfanos**:
   - Templates no usados
   - Scripts de migración viejos
   - Tests rotos

Generar:
- Reporte de limpieza
- Métricas antes/después
- Commits atómicos