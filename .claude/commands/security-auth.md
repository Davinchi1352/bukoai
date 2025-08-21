---
allowed-tools: Task
argument-hint: [login|jwt|sessions|oauth]
description: Revisar sistema de autenticación y autorización
---

## Contexto de Autenticación
- Rutas protegidas: !`grep -r "@login_required" app/ | wc -l`
- Configuración Flask-Login: @app/utils/auth.py
- Modelos de usuario: @app/models.py
- Configuración JWT: !`grep -r "JWT\|SECRET_KEY" config/`

## Tu Tarea

Analiza el sistema de autenticación ${ARGUMENTS:-completo} usando el agente security-guardian.

Validar:
1. Implementación de Flask-Login
2. Hashing de passwords con bcrypt
3. Manejo de sesiones y cookies
4. Tokens JWT (si aplica)
5. Rate limiting en login
6. Protección contra brute force
7. Logout seguro y limpieza de sesiones
8. Roles y permisos por tier