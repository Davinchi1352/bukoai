# 🚀 Comandos Slash Personalizados para BukoAI

## Descripción General

Conjunto completo de comandos slash personalizados diseñados específicamente para el proyecto BukoAI. Estos comandos automatizan tareas rutinarias y aprovechan los 15+ agentes especializados disponibles.

## 📋 Índice de Comandos

### 🔒 Seguridad
- `/security-audit [full|quick|owasp]` - Auditoría completa de seguridad
- `/security-auth [login|jwt|sessions]` - Revisar sistema de autenticación

### ⚡ Performance
- `/performance-analyze [full|api|database]` - Análisis completo de rendimiento
- `/performance-endpoint <ruta>` - Analizar endpoint específico

### 📈 Escalabilidad
- `/scale-analyze <usuarios>` - Analizar capacidad para N usuarios

### 🗄️ Base de Datos
- `/db-optimize [queries|schema|indexes]` - Optimizar base de datos

### 🧪 Testing
- `/test-generate <modulo>` - Generar tests para módulo
- `/book-generate-test [quick|full|stress]` - Test pipeline de generación

### 🎨 Frontend/UX
- `/ux-improve <componente>` - Mejorar UX con HTMX

### 📚 Documentación
- `/docs-api [openapi|swagger]` - Generar documentación de API

### 🌍 Internacionalización
- `/i18n-setup <idiomas>` - Configurar multi-idioma

### 📊 Inteligencia de Negocio
- `/bi-dashboard [kpis|retention|revenue]` - Dashboard de métricas
- `/claude-costs [daily|weekly|monthly]` - Análisis de costos Claude API

### 🏗️ Arquitectura
- `/architecture-analyze [full|dependencies]` - Analizar arquitectura

### 🧹 Limpieza de Código
- `/clean-dead-code [analyze|remove]` - Eliminar código muerto

### 📖 Editorial
- `/editorial-setup [epub|pdf|kindle]` - Configurar módulo editorial

### 🚀 Deployment
- `/deploy-prepare [staging|production]` - Preparar despliegue

### 🐛 Debugging
- `/debug-error <error>` - Analizar y resolver error

### 💻 Desarrollo
- `/dev-start [full|minimal|debug]` - Iniciar entorno desarrollo
- `/monitor-health [quick|detailed]` - Monitoreo de salud del sistema

### 🔄 Comandos Compuestos (Multi-Agente)
- `/release-prepare [major|minor|patch]` - Preparación completa para release
- `/optimize-all [performance|database|code]` - Optimización integral
- `/onboard-developer [junior|senior|fullstack]` - Onboarding completo

## 🎯 Uso

### Sintaxis Básica
```
/<comando> [argumentos]
```

### Ejemplos
```bash
# Auditoría de seguridad completa
/security-audit full

# Analizar rendimiento de endpoint específico
/performance-endpoint /api/books/generate

# Preparar para 10,000 usuarios concurrentes
/scale-analyze 10000

# Generar tests para módulo de autenticación
/test-generate app/auth

# Preparar release minor
/release-prepare minor
```

## 🤖 Agentes Utilizados

Cada comando está respaldado por uno o más agentes especializados:

1. **guardian-seguridad** - Auditorías y validaciones de seguridad
2. **analizador-rendimiento** - Análisis de performance y bottlenecks
3. **experto-escalabilidad** - Planificación de escalamiento
4. **optimizador-base-datos** - Optimización de queries y esquemas
5. **desarrollador-frontend-ux** - Mejoras de interfaz y UX
6. **arquitecto-pruebas** - Generación de tests comprehensivos
7. **generador-documentacion-api** - Documentación de APIs
8. **agente-internacionalizacion** - Soporte multi-idioma
9. **agente-inteligencia-negocio** - Análisis de métricas y KPIs
10. **analizador-arquitectura** - Mapeo de arquitectura
11. **limpiador-codigo-profundo** - Limpieza y refactoring
12. **desarrollador-editorial** - Funcionalidades editoriales
13. **gestor-despliegue** - Preparación de deployments
14. **depurador** - Resolución de errores
15. **documentador-integral** - Documentación completa

## ⚙️ Configuración

### Instalación
Los comandos ya están instalados en `.claude/commands/`

### Personalización
Puedes modificar cualquier comando editando su archivo `.md` correspondiente.

### Crear Nuevos Comandos
1. Crea un archivo `.md` en `.claude/commands/`
2. Añade frontmatter con configuración
3. Define la tarea del comando

## 📈 Beneficios

- **Automatización**: Tareas complejas en un solo comando
- **Consistencia**: Procesos estandarizados
- **Eficiencia**: Reducción de tiempo en tareas rutinarias
- **Calidad**: Aprovecha agentes especializados
- **Documentación**: Comandos auto-documentados

## 🔧 Mantenimiento

### Actualizar Comandos
```bash
# Ver todos los comandos disponibles
/help

# Editar un comando específico
vim .claude/commands/<comando>.md
```

### Monitorear Uso
Los comandos generan logs que puedes revisar para optimizaciones.

## 💡 Tips

1. **Usa argumentos**: Muchos comandos aceptan argumentos para personalizar su comportamiento
2. **Combina comandos**: Algunos comandos están diseñados para trabajar en secuencia
3. **Revisa outputs**: Los comandos generan reportes detallados con recomendaciones
4. **Itera**: Ejecuta comandos regularmente para mantener la calidad del código

## 🆘 Soporte

Si encuentras problemas o necesitas ayuda:
1. Revisa los logs del comando
2. Verifica los prerrequisitos
3. Consulta la documentación del agente correspondiente

---

*Documentación generada para BukoAI - Sistema de Generación de Libros con IA*