---
allowed-tools: Task
argument-hint: [epub|pdf|kindle|all]
description: Configurar módulo editorial profesional para BukoAI
---

## Estado Editorial Actual
- Generación de libros: @app/services/book_generator.py
- Formatos soportados: !`grep -r "format\|FORMAT" app/services/ | grep -i "pdf\|epub"`
- Templates de libros: !`ls app/templates/book_* 2>/dev/null`

## Tu Tarea

Configura el módulo editorial ${ARGUMENTS:-completo} usando el agente desarrollador-editorial.

Implementar:
1. **Generación EPUB**:
   - Estructura estándar EPUB 3.0
   - Metadatos Dublin Core
   - TOC navegable
   - Estilos personalizables
2. **Generación PDF**:
   - Diseño profesional
   - Headers/footers
   - Numeración de páginas
   - Índice automático
3. **Compatibilidad Kindle**:
   - Formato MOBI/AZW3
   - Validación KDP
   - Preview tool
4. **Metadatos**:
   - ISBN management
   - Autor/Editorial
   - Categorías y tags
   - DRM options

Integrar con:
- Sistema actual de generación
- Base de datos de libros
- UI de usuario