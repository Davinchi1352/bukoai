---
allowed-tools: Task, Bash(git:*), Bash(make:*)
argument-hint: [junior|senior|fullstack]
description: Onboarding completo para nuevo desarrollador
---

## Información del Proyecto
- Repositorio: !`git remote -v | head -1`
- Branch principal: !`git branch --show-current`
- Colaboradores: !`git shortlog -sn | wc -l`
- Actividad reciente: !`git log --oneline -10`

## Tu Tarea

Prepara onboarding completo para desarrollador ${ARGUMENTS:-fullstack}:

### 1. Arquitectura (analizador-arquitectura)
- Mapeo completo del proyecto
- Explicación de componentes
- Flujos principales de datos
- Patrones y convenciones

### 2. Documentación (documentador-integral)
- README actualizado
- Guía de instalación
- Convenciones de código
- Workflow de desarrollo

### 3. Entorno de Desarrollo
- Setup paso a paso
- Configuración de IDE
- Herramientas necesarias
- Accesos y permisos

### 4. Codebase Tour
- Estructura de directorios
- Módulos principales
- Puntos de entrada
- Tests y CI/CD

### 5. Tareas de Inicio
- Good first issues
- Bugs simples para familiarizarse
- Documentación a completar

Generar:
- Guía personalizada de onboarding
- Checklist de setup
- Recursos y enlaces útiles
- Contactos del equipo