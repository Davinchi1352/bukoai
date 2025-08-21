---
allowed-tools: Task
argument-hint: [analyze|interactive-fix|auto-fix|full]
description: Auditoría y corrección inteligente del ecosistema de agentes y comandos
---

## Estado Actual del Ecosistema
- Agentes totales: !`find .claude/agents -name "*.md" | wc -l`
- Comandos totales: !`find .claude/commands -name "*.md" | wc -l`
- Jerarquía anti-ciclos: ✅ Implementada (6 niveles)
- Última auditoría: !`ls -la docs/supervision/ 2>/dev/null | head -3 || echo "Sin auditorías previas"`

## Tu Tarea

Ejecuta supervisión del ecosistema en modo **${ARGUMENTS:-analyze}** usando el agente supervisor-ecosistema-completo.

## 🔧 **MODOS DE OPERACIÓN HÍBRIDOS:**

### **`/ecosystem-audit analyze`** (MODO ANÁLISIS SEGURO)
- ✅ **Solo detecta y reporta** problemas (modo read-only)
- ✅ **Completamente seguro** - No modifica ningún archivo
- ✅ **Análisis exhaustivo** - Todas las 7 fases de auditoría
- ✅ **Recomendaciones detalladas** - Guía para correcciones manuales
- 📊 **Métricas objetivas** - Scores de calidad cuantificables
- 🎯 **Ideal para**: Primera auditoría, baseline, exploración sin riesgos

### **`/ecosystem-audit interactive-fix`** (MODO CORRECCIÓN INTERACTIVA) ⭐ RECOMENDADO
- 🔍 **Detecta problemas** automáticamente
- ❓ **Pregunta antes de CADA corrección** individual
- 👁️ **Muestra preview exacto** de cada cambio propuesto
- ✋ **Control total del usuario** - Aprobar/rechazar cada modificación
- 🔒 **Completamente seguro** - No hace cambios sin confirmación explícita
- 📝 **Log detallado** de decisiones y cambios aplicados
- 💾 **Backup automático** antes de modificaciones
- 🎯 **Ideal para**: Corrección controlada, learning, development activo

**Sistema de Confirmación Interactiva:**
- **`y` (yes)**: Aplicar esta corrección específica
- **`n` (no)**: Saltar, continuar con siguiente
- **`s` (skip)**: Saltar todas las correcciones de este tipo
- **`q` (quit)**: Terminar proceso de corrección
- **`p` (preview)**: Ver más detalles del cambio

### **`/ecosystem-audit auto-fix`** (MODO CORRECCIÓN AUTOMÁTICA)
- ⚡ **Corrige automáticamente** problemas de bajo riesgo
- 🎯 **Solo correcciones seguras**: typos, formatting, referencias, whitespace
- ❗ **Confirmación requerida** para cambios críticos (logic, tools, descriptions)
- 📝 **Log completo** de todos los cambios realizados
- 💾 **Backup automático** antes de modificaciones
- 🚫 **Nunca modifica**: nombres de agentes, models, colors, allowed-tools
- 🎯 **Ideal para**: Mantenimiento regular, limpieza rápida, CI/CD

### **`/ecosystem-audit full`** (PIPELINE INTEGRAL)
- 📋 **Análisis inicial completo** con todas las 7 fases
- 🔧 **Corrección interactiva** de todos los issues detectados
- 📚 **Actualización de documentación** automática post-corrección
- 📊 **Métricas antes/después** para medir mejora
- 🎯 **Pipeline completo** de calidad y corrección
- 🎯 **Ideal para**: Pre-releases, refactoring mayor, auditorías completas

## 📊 **ANÁLISIS INCLUIDO:**

### 🔍 **Calidad de Agentes Individuales**
1. **Eliminación de código hardcodeado**: Detectar patrones como comandos bash, paths absolutos, URLs fijas
2. **Claridad de descriptions**: Validar que definan CLARAMENTE cuándo activarse
3. **Mejores prácticas Claude Code**: Tools correctos, model apropiado, color único
4. **Responsabilidades definidas**: Scope específico, sin solapamientos, deliverables claros

### 🔗 **Coherencia Agentes ↔ Slash Commands**
1. **Mapeo lógico**: Cada comando usa el agente más apropiado
2. **Completitud de cobertura**: Todas las funcionalidades tienen entry points
3. **Coherencia de argumentos**: Arguments-hints alineados con capacidades de agentes
4. **Flujos estructurados**: Workflows predecibles y ejecutables

### 🎯 **Detección de Problemas Estructurales**
1. **Referencias circulares**: Mantenimiento de jerarquía anti-ciclos de 6 niveles
2. **Solapamientos funcionales**: Agentes con responsabilidades duplicadas
3. **Referencias inexistentes**: Agentes referenciados que no existen
4. **Gaps funcionales**: Casos de uso sin agente apropiado

### 📚 **Sincronización de Documentación**
1. **Coherencia docs ↔ agentes**: Información actualizada y precisa
2. **Coherencia docs ↔ comandos**: Examples y workflows ejecutables
3. **Referencias cruzadas**: Links correctos entre documentos
4. **Terminología consistente**: Naming conventions estandarizadas

### 📋 **Deliverables por Modo**

#### **MODO `analyze`**
- **docs/supervision/reporte-ecosistema-completo.md**: Análisis integral detallado
- **docs/supervision/issues-detectados.md**: Lista priorizada de problemas
- **docs/supervision/metricas-calidad.md**: Scores objetivos y benchmarks
- **docs/supervision/recomendaciones.md**: Guía de correcciones manuales

#### **MODO `interactive-fix`**
- **docs/supervision/sesion-interactiva.md**: Log completo de la sesión
- **docs/supervision/cambios-aplicados.md**: Registro de modificaciones realizadas
- **docs/supervision/cambios-pendientes.md**: Issues que requieren atención manual
- **docs/supervision/backup-pre-cambios/**: Backup automático antes de modificar

#### **MODO `auto-fix`**
- **docs/supervision/cambios-automaticos.md**: Log de correcciones aplicadas
- **docs/supervision/issues-criticos.md**: Problemas que requieren confirmación manual
- **docs/supervision/backup-automatico/**: Respaldo antes de cambios

#### **MODO `full`**
- **Todos los deliverables anteriores** +
- **docs/supervision/mejora-comparativa.md**: Métricas antes vs después
- **Documentación actualizada** en docs/ según cambios aplicados

### 📊 **Métricas de Éxito y Quality Gates**

#### **✅ EXCELENTE (95-100%)**
- **0 referencias circulares** detectadas
- **100% coherencia** agentes-comandos  
- **0 referencias** a agentes inexistentes
- **< 5% solapamiento** funcional entre agentes
- **100% sincronización** documentación
- **0 código hardcodeado** detectado

#### **✅ BUENO (85-94%)**
- **0 referencias circulares** 
- **> 95% coherencia** agentes-comandos
- **< 2 referencias incorrectas** 
- **< 10% solapamiento** funcional
- **> 95% sincronización** documentación
- **< 5% código hardcodeado**

#### **⚠️ ACEPTABLE (75-84%)**
- **0 referencias circulares críticas**
- **> 90% coherencia** agentes-comandos
- **< 5 referencias incorrectas**
- **< 15% solapamiento** funcional
- **> 90% sincronización** documentación
- **< 10% código hardcodeado**

#### **❌ REQUIERE ACCIÓN (<75%)**
- Múltiples issues críticos detectados
- Coherencia < 90% o problemas estructurales
- Referencias incorrectas > 5 o circulares
- Solapamiento funcional > 15%
- Documentación < 90% sincronizada

### 🔄 **Workflows Recomendados**

#### **Desarrollo Diario**
```bash
# Antes de cambios
/ecosystem-audit analyze

# Después de cambios  
/ecosystem-audit interactive-fix
```

#### **Mantenimiento Semanal**
```bash
# Limpieza automática
/ecosystem-audit auto-fix
```

#### **Pre-Release**
```bash
# Quality gate completo
/ecosystem-audit full
```

**Nota**: El modo `full` incluye actualización automática de documentación. Para otros modos, considera ejecutar documentador-integral después si hay cambios significativos.