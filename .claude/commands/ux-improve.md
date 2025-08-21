---
allowed-tools: Task
argument-hint: <componente_o_pagina>
description: Mejorar UX de componente específico con HTMX
---

## Componente a Mejorar: ${ARGUMENTS}

## Contexto del Componente
- Template actual: @app/templates/${ARGUMENTS}
- Estilos: !`find app/static/css -name "*${ARGUMENTS}*" | head -3`
- JavaScript: !`grep -r "${ARGUMENTS}" app/static/js/ | head -5`
- Rutas relacionadas: !`grep -r "${ARGUMENTS}" app/ | grep route | head -3`

## Tu Tarea

Mejora la experiencia de usuario del componente ${ARGUMENTS} usando el agente desarrollador-frontend-ux.

Implementar:
1. **Interactividad HTMX**: Updates dinámicos sin JavaScript
2. **Responsividad**: Mobile-first design
3. **Animaciones**: Transiciones suaves con CSS
4. **Loading states**: Indicadores de progreso
5. **Error handling**: Mensajes amigables
6. **Accesibilidad**: ARIA labels, keyboard nav
7. **Performance**: Lazy loading, optimización

Entregar:
- Templates actualizados
- Estilos CSS modernos
- Integración HTMX
- Tests de usabilidad