# ⚡ Guía Completa de Comandos Personalizados - BukoAI

## 🛡️ SISTEMA ANTI-CICLOS IMPLEMENTADO

**🎯 GARANTÍA DE SEGURIDAD:**
- ✅ **Comandos seguros:** Todos operan bajo jerarquía anti-ciclos
- ✅ **Sin bucles infinitos:** Arquitectura validada sin referencias circulares
- ✅ **Flujos predecibles:** Ejecución controlada y terminación garantizada
- ✅ **Operación estable:** De 30+ ciclos peligrosos a **0 ciclos**

## Descripción General

BukoAI incluye **28 comandos slash personalizados** que automatizan tareas complejas aprovechando el ecosistema de 18 agentes especializados **organizados en jerarquía anti-ciclos de 7 niveles**. Estos comandos proporcionan acceso rápido a funcionalidades avanzadas mediante una sintaxis simple y consistente, **garantizando operación segura sin bucles infinitos**, culminando con el comando de **meta-supervisión del ecosistema completo**.

## 📋 Índice Completo de Comandos (28 COMANDOS)

### 🏗️ **ARQUITECTURA Y ANÁLISIS**

#### `/architecture-analyze [full|dependencies|structure|patterns]`
- **Agente**: `analizador-arquitectura`
- **Descripción**: Analiza la arquitectura completa del proyecto
- **Argumentos**:
  - `full` (default): Análisis arquitectónico completo
  - `dependencies`: Focus en dependencias entre componentes
  - `structure`: Análisis de estructura de directorios
  - `patterns`: Identificación de patrones de diseño
- **Salida**: Documentación arquitectónica detallada
- **Ejemplo**: `/architecture-analyze full`

### 🔒 **SEGURIDAD**

#### `/security-audit [full|quick|owasp]`
- **Agente**: `guardian-seguridad`
- **Descripción**: Auditoría completa de seguridad del proyecto
- **Argumentos**:
  - `full` (default): Auditoría integral de seguridad
  - `quick`: Verificación rápida de vulnerabilidades críticas
  - `owasp`: Análisis específico OWASP Top 10
- **Salida**: Reporte de seguridad con vulnerabilidades y fixes
- **Ejemplo**: `/security-audit full`

#### `/security-auth [login|jwt|sessions]`
- **Agente**: `guardian-seguridad`
- **Descripción**: Revisión especializada del sistema de autenticación
- **Argumentos**:
  - `login`: Análisis del sistema de login
  - `jwt`: Validación de implementación JWT
  - `sessions`: Revisión de gestión de sesiones
- **Salida**: Análisis específico de autenticación
- **Ejemplo**: `/security-auth jwt`

### ⚡ **PERFORMANCE Y OPTIMIZACIÓN**

#### `/performance-analyze [full|api|database]`
- **Agente**: `analizador-rendimiento`
- **Descripción**: Análisis completo de rendimiento
- **Argumentos**:
  - `full` (default): Análisis integral de performance
  - `api`: Focus en rendimiento de APIs
  - `database`: Análisis específico de consultas DB
- **Salida**: Reporte de performance con optimizaciones
- **Ejemplo**: `/performance-analyze full`

#### `/performance-endpoint <ruta>`
- **Agente**: `analizador-rendimiento`
- **Descripción**: Analiza rendimiento de endpoint específico
- **Argumentos**:
  - `<ruta>` (requerido): Ruta del endpoint a analizar
- **Salida**: Análisis detallado del endpoint
- **Ejemplo**: `/performance-endpoint /api/books/generate`

### 📈 **ESCALABILIDAD**

#### `/scale-analyze <usuarios>`
- **Agente**: `experto-escalabilidad`
- **Descripción**: Analiza capacidad para N usuarios concurrentes
- **Argumentos**:
  - `<usuarios>` (requerido): Número de usuarios objetivo
- **Salida**: Plan de escalabilidad y recomendaciones
- **Ejemplo**: `/scale-analyze 10000`

### 💾 **BASE DE DATOS**

#### `/db-optimize [queries|schema|indexes]`
- **Agente**: `optimizador-base-datos`
- **Descripción**: Optimización integral de base de datos
- **Argumentos**:
  - `queries`: Optimización de consultas lentas
  - `schema`: Análisis y mejora de esquema
  - `indexes`: Recomendaciones de índices
- **Salida**: Consultas optimizadas e índices recomendados
- **Ejemplo**: `/db-optimize queries`

### 🧪 **TESTING Y CALIDAD**

#### `/test-generate <modulo>`
- **Agente**: `arquitecto-pruebas`
- **Descripción**: Genera tests comprehensivos para módulo específico
- **Argumentos**:
  - `<modulo>` (requerido): Módulo a testear
- **Salida**: Suite completa de pruebas
- **Ejemplo**: `/test-generate app/auth`

#### `/book-generate-test [quick|full|stress]`
- **Agente**: `arquitecto-pruebas`
- **Descripción**: Tests específicos para pipeline de generación de libros
- **Argumentos**:
  - `quick`: Tests básicos de generación
  - `full` (default): Suite completa de tests
  - `stress`: Tests de carga y stress
- **Salida**: Tests especializados en generación
- **Ejemplo**: `/book-generate-test full`

### ⚙️ **BACKEND Y ARQUITECTURA**

#### `/backend-develop [api|claude-integration|docker]`
- **Agente**: `desarrollador-fullstack-backend`
- **Descripción**: Desarrollo backend completo con Python/Flask/PostgreSQL
- **Argumentos**:
  - `api`: Desarrollo de APIs robustas y escalables
  - `claude-integration`: Integración avanzada con Claude AI SDK
  - `docker`: Containerización completa y optimización
- **Salida**: Sistema backend robusto y optimizado
- **Ejemplo**: `/backend-develop claude-integration`

#### `/backend-optimize [performance|scaling|quality]`
- **Agente**: `desarrollador-fullstack-backend`
- **Descripción**: Optimización de sistemas backend existentes
- **Argumentos**:
  - `performance`: Optimización de rendimiento backend
  - `scaling`: Preparación para escalamiento horizontal
  - `quality`: Optimizaciones que preservan calidad de contenido
- **Salida**: Backend optimizado sin comprometer calidad
- **Ejemplo**: `/backend-optimize quality`

#### `/fullstack-coordinate [frontend-backend|api-design|integration]`
- **Agentes**: `desarrollador-fullstack-backend` + `desarrollador-frontend-ux`
- **Descripción**: Coordinación perfecta entre desarrollo frontend y backend
- **Argumentos**:
  - `frontend-backend`: Integración completa frontend-backend
  - `api-design`: Diseño de APIs optimizadas para frontend
  - `integration`: Optimización de comunicación frontend-backend
- **Salida**: Experiencia fullstack perfectamente integrada
- **Ejemplo**: `/fullstack-coordinate integration`

### 🎨 **FRONTEND Y UX**

#### `/ux-improve <componente>`
- **Agente**: `desarrollador-frontend-ux`
- **Descripción**: Mejora UX de componente específico con HTMX
- **Argumentos**:
  - `<componente>` (requerido): Componente/página a mejorar
- **Salida**: Interface modernizada con HTMX
- **Ejemplo**: `/ux-improve dashboard`

### 📚 **DOCUMENTACIÓN**

#### `/docs-api [openapi|swagger]`
- **Agente**: `generador-documentacion-api`
- **Descripción**: Genera documentación de API
- **Argumentos**:
  - `openapi`: Especificación OpenAPI 3.0
  - `swagger` (default): Documentación Swagger UI
- **Salida**: Documentación interactiva de API
- **Ejemplo**: `/docs-api swagger`

### 🌍 **INTERNACIONALIZACIÓN**

#### `/i18n-setup <idiomas>`
- **Agente**: `agente-internacionalizacion`
- **Descripción**: Configura soporte multi-idioma
- **Argumentos**:
  - `<idiomas>` (requerido): Lista de idiomas separados por comas
- **Salida**: Configuración completa de i18n
- **Ejemplo**: `/i18n-setup en,fr,de`

### 📊 **INTELIGENCIA DE NEGOCIO**

#### `/bi-dashboard [kpis|retention|revenue|usage]`
- **Agente**: `agente-inteligencia-negocio`
- **Descripción**: Genera dashboard de métricas de negocio
- **Argumentos**:
  - `kpis` (default): KPIs principales
  - `retention`: Análisis de retención
  - `revenue`: Métricas de ingresos
  - `usage`: Patrones de uso
- **Salida**: Dashboard interactivo con métricas
- **Ejemplo**: `/bi-dashboard kpis`

#### `/claude-costs [daily|weekly|monthly]`
- **Agente**: `agente-inteligencia-negocio`
- **Descripción**: Análisis de costos de Claude API
- **Argumentos**:
  - `daily`: Costos diarios
  - `weekly`: Costos semanales
  - `monthly` (default): Costos mensuales
- **Salida**: Análisis detallado de costos API
- **Ejemplo**: `/claude-costs monthly`

### 🧹 **LIMPIEZA Y MANTENIMIENTO**

#### `/clean-dead-code [analyze|remove]`
- **Agente**: `limpiador-codigo-profundo`
- **Descripción**: Elimina código muerto y optimiza codebase
- **Argumentos**:
  - `analyze` (default): Análisis de código muerto
  - `remove`: Eliminación activa de código no usado
- **Salida**: Código limpio y reportes de limpieza
- **Ejemplo**: `/clean-dead-code analyze`

### 📖 **EDITORIAL**

#### `/editorial-setup [epub|pdf|kindle]`
- **Agente**: `desarrollador-editorial`
- **Descripción**: Configura módulo editorial para formatos específicos
- **Argumentos**:
  - `epub`: Setup para formato EPUB
  - `pdf`: Configuración PDF
  - `kindle`: Optimización para Kindle
- **Salida**: Módulo editorial funcional
- **Ejemplo**: `/editorial-setup epub`

#### `/editorial-backend-integration`
- **Agentes**: `desarrollador-editorial` + `desarrollador-fullstack-backend`
- **Descripción**: Integración optimizada entre módulo editorial y backend robusto
- **Salida**: Sistema editorial con APIs backend optimizadas
- **Ejemplo**: `/editorial-backend-integration`

### 🚀 **DEPLOYMENT**

#### `/deploy-prepare [staging|production]`
- **Agente**: `gestor-despliegue`
- **Descripción**: Prepara paquete de despliegue
- **Argumentos**:
  - `staging`: Configuración para staging
  - `production` (default): Setup de producción
- **Salida**: Paquete completo de deployment
- **Ejemplo**: `/deploy-prepare production`

### 🐛 **DEBUGGING**

#### `/debug-error <error>`
- **Agente**: `depurador`
- **Descripción**: Analiza y resuelve error específico
- **Argumentos**:
  - `<error>` (requerido): Descripción del error o stack trace
- **Salida**: Diagnóstico y solución del error
- **Ejemplo**: `/debug-error "Internal Server Error 500"`

### 🧠 **META-GESTIÓN DEL ECOSISTEMA**

#### `/ecosystem-audit [analyze|interactive-fix|auto-fix|full]`
- **Agente**: `supervisor-ecosistema-completo`
- **Descripción**: Auditoría y corrección inteligente del ecosistema de agentes y comandos
- **Argumentos**:
  - `analyze` (default): Solo detecta y reporta problemas (seguro, read-only)
  - `interactive-fix`: Detecta problemas Y ofrece correcciones con confirmación del usuario ⭐
  - `auto-fix`: Corrige automáticamente solo problemas seguros (typos, formatting, referencias)
  - `full`: Pipeline completo: análisis + corrección interactiva + documentación actualizada
- **Salida**: Reportes de calidad + modificaciones aplicadas (según modo)
- **Ejemplo**: `/ecosystem-audit interactive-fix`
- **⭐ NUEVAS CAPACIDADES HÍBRIDAS**:
  - **Modo Seguro**: Análisis sin modificaciones para exploración
  - **Corrección Interactiva**: Control total con preview y confirmación individual
  - **Corrección Automática**: Eficiencia para problemas de bajo riesgo
  - **Sistema de Confirmación**: y/n/s/q/p para control granular
  - **Backup Automático**: Restauración segura antes de cambios

### 💻 **DESARROLLO**

#### `/dev-start [full|minimal|debug]`
- **Agente**: Coordinación multi-agente
- **Descripción**: Inicializa entorno de desarrollo
- **Argumentos**:
  - `full`: Setup completo de desarrollo
  - `minimal` (default): Setup básico
  - `debug`: Entorno con debugging habilitado
- **Salida**: Entorno de desarrollo configurado
- **Ejemplo**: `/dev-start full`

#### `/docker-optimize [development|production|deployment]`
- **Agente**: `desarrollador-fullstack-backend`
- **Descripción**: Optimización completa de containerización Docker
- **Argumentos**:
  - `development`: Setup Docker para desarrollo
  - `production`: Configuración Docker para producción
  - `deployment`: Optimización de deployment con Docker
- **Salida**: Configuración Docker optimizada
- **Ejemplo**: `/docker-optimize production`

#### `/monitor-health [quick|detailed]`
- **Agente**: `analizador-rendimiento`
- **Descripción**: Monitoreo de salud del sistema
- **Argumentos**:
  - `quick` (default): Verificación rápida
  - `detailed`: Análisis detallado de salud
- **Salida**: Reporte de estado del sistema
- **Ejemplo**: `/monitor-health detailed`

### 🔄 **COMANDOS COMPUESTOS (Multi-Agente) - FLUJOS SEGUROS**

#### `/release-prepare [major|minor|patch]`
- **Agentes**: Coordinación secuencial sin ciclos
- **Descripción**: Preparación completa para release con jerarquía anti-ciclos
- **Argumentos**:
  - `major`: Release mayor con breaking changes
  - `minor` (default): Release con nuevas funcionalidades
  - `patch`: Release de bug fixes
- **🛡️ Flujo Anti-Ciclos (LECTURA SOLAMENTE):**
  1. **Usuario** → Solicita `analizador-arquitectura` si necesario
  2. **Usuario** → Lee análisis para `guardian-seguridad` (auditoría)
  3. **Usuario** → Lee reportes para `arquitecto-pruebas` (tests)
  4. **Usuario** → Lee análisis para `analizador-rendimiento` (performance)
  5. **Usuario** → Lee todos los reportes para `documentador-integral`
  6. **Usuario** → Lee toda la información para `gestor-despliegue`
- **Salida**: Release completamente preparado sin riesgo de bucles
- **Ejemplo**: `/release-prepare minor`

#### `/optimize-all [performance|database|code|fullstack]`
- **Agentes**: Coordinación jerárquica sin referencias circulares
- **Descripción**: Optimización integral respetando jerarquía anti-ciclos
- **Argumentos**:
  - `performance`: Focus en performance
  - `database`: Optimización de DB
  - `code`: Limpieza de código
  - `fullstack`: Optimización completa frontend + backend
- **🛡️ Flujo Jerárquico Seguro:**
  1. **Nivel 0** → `analizador-arquitectura` genera análisis base
  2. **Nivel 1** → `analizador-rendimiento` lee análisis (no ejecuta)
  3. **Nivel 1** → `desarrollador-fullstack-backend` lee reportes
  4. **Nivel 1** → `optimizador-base-datos` lee análisis base
  5. **Nivel 1** → `desarrollador-frontend-ux` lee reportes disponibles
  6. **Nivel 2** → `limpiador-codigo-profundo` lee todos los niveles 0-1
- **Salida**: Sistema optimizado sin riesgo de bucles infinitos
- **Ejemplo**: `/optimize-all fullstack`

#### `/onboard-developer [junior|senior|fullstack]`
- **Agentes**: Flujo jerárquico de documentación
- **Descripción**: Onboarding seguro respetando protocolos anti-ciclos
- **Argumentos**:
  - `junior`: Onboarding para desarrollador junior
  - `senior`: Setup para desarrollador senior
  - `fullstack`: Onboarding fullstack
- **🛡️ Flujo Anti-Ciclos:**
  1. **Nivel 0** → `analizador-arquitectura` genera documentación base
  2. **Nivel 1** → `arquitecto-pruebas` lee análisis para guías testing
  3. **Nivel 1** → `guardian-seguridad` lee análisis para políticas
  4. **Nivel 3** → `documentador-integral` integra TODA la información
- **Salida**: Paquete de onboarding sin referencias circulares
- **Ejemplo**: `/onboard-developer fullstack`

## 🎯 Sintaxis y Ejemplos de Uso

### **Formato Básico**
```
/<comando> [argumentos]
```

### **Ejemplos Prácticos**

```bash
# Análisis completo de arquitectura
/architecture-analyze full

# Auditoría de seguridad rápida
/security-audit quick

# Optimizar endpoint específico
/performance-endpoint /api/books/generate

# Preparar para 5000 usuarios
/scale-analyze 5000

# Generar tests para autenticación
/test-generate app/auth

# Mejorar UX del dashboard
/ux-improve dashboard

# Setup multi-idioma
/i18n-setup en,es,fr

# Dashboard de KPIs
/bi-dashboard kpis

# Auditoría segura del ecosistema (modo read-only)
/ecosystem-audit analyze

# Corrección interactiva con control del usuario (RECOMENDADO)
/ecosystem-audit interactive-fix

# Corrección automática de problemas seguros
/ecosystem-audit auto-fix

# Pipeline completo de auditoría y corrección
/ecosystem-audit full

# Preparar release menor
/release-prepare minor

# Optimización integral
/optimize-all performance
```

## 🛡️ FLUJOS SEGUROS SIN CICLOS

### **Desarrollo de Nueva Funcionalidad (Anti-Ciclos)**
```bash
# FLUJO JERÁRQUICO SEGURO:
/architecture-analyze full              # Nivel 0: Análisis base
# Usuario lee análisis, luego:
/backend-develop api                   # Nivel 1: Backend (lee Nivel 0)
# Usuario lee reportes, luego:
/ux-improve <nueva-funcionalidad>      # Nivel 1: Frontend (lee Nivel 0)
# Usuario coordina manualmente (SIN ejecución circular):
/test-generate <modulo>               # Nivel 1: Tests (lee Nivel 0)
/security-audit quick                # Nivel 1: Seguridad (lee Nivel 0)
# RESULTADO: Funcionalidad sin bucles infinitos
```

### **Optimización de Performance (Flujo Seguro)**
```bash
# JERARQUÍA ANTI-CICLOS:
/architecture-analyze dependencies    # Nivel 0: Base
# Usuario lee análisis, ejecuta en paralelo (mismo nivel):
/performance-analyze full           # Nivel 1: Bottlenecks (lee Nivel 0)
/db-optimize queries               # Nivel 1: DB (lee Nivel 0)  
/backend-optimize performance        # Nivel 1: Backend (lee Nivel 0)
/scale-analyze <usuarios-objetivo>  # Nivel 1: Escalabilidad (lee Nivel 0)
# Nivel superior integra:
/docker-optimize production        # Nivel 1: Docker (lee Nivel 0)
# RESULTADO: Optimización sin referencias circulares
```

### **Preparación para Producción (Protocolo Seguro)**
```bash
# PROTOCOLO ANTI-CICLOS:
/architecture-analyze full        # Nivel 0: Base obligatoria
# Usuario lee, ejecuta en paralelo (Nivel 1):
/security-audit full              # Nivel 1: Auditoría (lee Nivel 0)
/performance-analyze full         # Nivel 1: Performance (lee Nivel 0)
/test-generate app                # Nivel 1: Tests (lee Nivel 0)
# Nivel superior para orquestación:
/deploy-prepare production        # Nivel 5: Deployment (lee todos)
# RESULTADO: Producción lista sin riesgo de bucles
```

### **Mantenimiento Regular (Operación Segura)**
```bash
# MANTENIMIENTO SIN CICLOS:
/architecture-analyze structure   # Nivel 0: Análisis actual
# Operaciones independientes por nivel:
/clean-dead-code analyze         # Nivel 2: Limpieza (lee Niveles 0-1)
/monitor-health detailed         # Nivel 1: Monitoreo (lee Nivel 0)
/claude-costs monthly           # Nivel 4: Costos (lee todos los niveles)
/bi-dashboard kpis             # Nivel 4: Métricas (lee todos)
# RESULTADO: Mantenimiento predecible y seguro
```

## ⚙️ Configuración y Personalización

### **Modificar Comandos Existentes**
1. Editar archivo correspondiente en `.claude/commands/`
2. Modificar frontmatter o contenido según necesidades
3. Los cambios se aplican inmediatamente

### **Crear Nuevos Comandos**
```markdown
---
allowed-tools: Task
argument-hint: [argumentos]
description: Descripción del comando
---

## Tu Tarea
Definir la tarea que ejecutará el comando...
```

### **Argumentos y Variables**
- `${ARGUMENTS}`: Captura argumentos del comando
- `${ARGUMENTS:-default}`: Valor por defecto si no hay argumentos
- Variables de contexto automáticas disponibles

## 🚨 Troubleshooting

### **Problemas Comunes**

#### **Error: "Agente no encontrado"**
- **Causa**: Nombre de agente incorrecto en comando
- **Solución**: Verificar nombre en `.claude/agents/`

#### **Error: "Análisis arquitectónico requerido"**
- **Causa**: Agente requiere análisis base no disponible
- **Solución**: Ejecutar `/architecture-analyze full` primero

#### **Comando no responde**
- **Causa**: Argumentos incorrectos o faltantes
- **Solución**: Verificar sintaxis y argumentos requeridos

### **Mejores Prácticas**

1. **Secuencia**: Ejecutar comandos en orden lógico
2. **Argumentos**: Usar argumentos específicos para mejor resultado
3. **Verificación**: Revisar outputs antes del siguiente comando
4. **Iteración**: Re-ejecutar comandos según sea necesario

## 📊 Métricas y Monitoring

### **Comandos de Monitoreo**
- `/monitor-health`: Estado general del sistema
- `/claude-costs`: Control de costos API
- `/bi-dashboard`: Métricas de negocio
- `/performance-analyze`: Performance en tiempo real

### **Reportes Automáticos**
- Logs de ejecución en `logs/structured.jsonl`
- Reportes generados en `docs/` respectivas carpetas
- Métricas almacenadas para análisis histórico

## 🎓 Tips Avanzados

### **Comandos Compuestos**
- Usar comandos multi-agente para flujos completos
- `/release-prepare` y `/optimize-all` coordinan múltiples agentes
- Permiten flujos automatizados complejos

### **Argumentos Avanzados**
- Combinar argumentos para resultados específicos
- Usar valores por defecto inteligentemente
- Experimentar con diferentes combinaciones

### **Integración con CI/CD**
- Comandos pueden integrarse en pipelines
- Outputs estructurados para automation
- Reportes parseables para herramientas externas

---

*Esta documentación es parte del ecosistema BukoAI - Sistema de Generación de Libros con IA*