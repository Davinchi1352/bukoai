---
allowed-tools: Task
argument-hint: [full|quick|owasp]
description: Auditoría completa de seguridad del proyecto BukoAI
model: claude-3-5-sonnet-20241022
---

## Contexto del Sistema
- Versión Python: !`python --version`
- Dependencias: !`pip list | grep -E "Flask|SQLAlchemy|bcrypt|JWT"`
- Archivos sensibles: !`find . -name "*.env*" -o -name "*secret*" -o -name "*key*" | head -20`
- Configuración actual: @config/config.py

## Tu Tarea

Realiza una auditoría de seguridad ${ARGUMENTS:-completa} del proyecto BukoAI usando el agente security-guardian.

Enfócate en:
1. **Autenticación y Autorización**: Sistema de login, JWT, sesiones
2. **Validación de Entrada**: SQLi, XSS, CSRF protections
3. **Configuraciones**: Secrets management, headers de seguridad
4. **API de Claude**: Manejo seguro de API keys
5. **File Upload**: Validaciones y sanitización
6. **OWASP Top 10**: Checklist completo
7. **Dependencias**: Vulnerabilidades conocidas

Genera un reporte detallado con:
- Vulnerabilidades críticas (URGENTE)
- Problemas de seguridad medios
- Mejoras recomendadas
- Código de ejemplo para fixes