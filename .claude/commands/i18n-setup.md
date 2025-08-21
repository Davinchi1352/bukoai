---
allowed-tools: Task
argument-hint: <idiomas_separados_por_coma>
description: Configurar internacionalización para múltiples idiomas
---

## Idiomas Objetivo: ${ARGUMENTS:-es,en,fr,pt}

## Estado Actual
- Flask-Babel: !`grep Flask-Babel requirements.txt || echo "No instalado"`
- Strings en templates: !`grep -r "{{.*}}" app/templates/ | wc -l`
- Textos hardcoded: !`grep -r "\".*\"" app/ | grep -v import | wc -l`

## Tu Tarea

Configura internacionalización para los idiomas ${ARGUMENTS:-es,en,fr,pt} usando el agente agente-internacionalizacion.

Implementar:
1. **Flask-Babel setup**: Configuración inicial
2. **Extracción de strings**: De Python y templates
3. **Archivos de traducción**: .po y .mo files
4. **Selección de idioma**: Por usuario/sesión
5. **Formateo regional**: Fechas, números, moneda
6. **RTL support**: Para árabe/hebreo si aplica
7. **Fallback**: Idioma por defecto

Generar:
- babel.cfg configuración
- Scripts de extracción
- Archivos base de traducción
- Documentación para traductores