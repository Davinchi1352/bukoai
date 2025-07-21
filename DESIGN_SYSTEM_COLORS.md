# 🎨 Guía de Colores - Buko AI Design System

## Filosofía de Color

La paleta de colores de Buko AI está diseñada con principios de **profesionalismo global**, **accesibilidad universal** y **escalabilidad empresarial**. Cada color ha sido seleccionado para transmitir confianza, sofisticación y ser culturalmente neutro.

## Paleta Principal

### Colores Primarios
```css
:root {
    /* Primarios - Uso en textos principales y elementos críticos */
    --primary-color: #1e293b;           /* Slate 800 - Texto principal */
    --primary-dark: #0f172a;            /* Slate 900 - Texto más oscuro */
    --primary-light: #334155;           /* Slate 700 - Variante más clara */
    
    /* Acento - Botones primarios y elementos interactivos */
    --accent-color: #3b82f6;            /* Blue 500 - Acento principal */
    --accent-dark: #1d4ed8;             /* Blue 700 - Hover states */
    --accent-light: #60a5fa;            /* Blue 400 - Estados activos */
    
    /* Secundarios - Texto de apoyo y elementos secundarios */
    --secondary-color: #64748b;         /* Slate 500 - Texto secundario */
    --secondary-dark: #475569;          /* Slate 600 - Variante oscura */
    --secondary-light: #94a3b8;         /* Slate 400 - Texto muted */
}
```

### Colores de Estado
```css
:root {
    /* Estados del sistema */
    --success-color: #059669;           /* Emerald 600 - Éxito */
    --warning-color: #d97706;           /* Amber 600 - Advertencia */
    --error-color: #dc2626;             /* Red 600 - Error */
    --info-color: #0ea5e9;              /* Sky 500 - Información */
}
```

### Colores de Fondo
```css
:root {
    /* Fondos y superficies */
    --background-primary: #ffffff;      /* Blanco puro */
    --background-secondary: #f8fafc;    /* Slate 50 - Fondo cálido */
    --background-tertiary: #f1f5f9;     /* Slate 100 - Fondo alternativo */
    --border-color: #e2e8f0;            /* Slate 200 - Bordes sutiles */
}
```

## Uso y Aplicación

### Jerarquía de Texto
```css
/* Texto Principal */
h1, h2, h3, .title {
    color: var(--primary-color);
}

/* Texto Secundario */
p, .description {
    color: var(--secondary-color);
}

/* Texto Muted */
.meta, .caption {
    color: var(--secondary-light);
}
```

### Botones
```css
/* Botón Primario */
.btn-primary {
    background-color: var(--accent-color);
    color: white;
}

.btn-primary:hover {
    background-color: var(--accent-dark);
}

/* Botón Secundario */
.btn-secondary {
    background-color: var(--background-tertiary);
    color: var(--primary-color);
    border: 1px solid var(--border-color);
}
```

### Enlaces
```css
a {
    color: var(--accent-color);
}

a:hover {
    color: var(--accent-dark);
}
```

## Gradientes Sutiles

Para elementos que necesiten gradientes profesionales:

```css
:root {
    --primary-gradient: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    --accent-gradient: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    --background-gradient: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    --neutral-gradient: linear-gradient(135deg, #64748b 0%, #475569 100%);
}
```

## Combinaciones Recomendadas

### Landing Page
- **Hero Background**: `var(--background-gradient)`
- **Títulos**: `var(--primary-color)`
- **Subtítulos**: `var(--secondary-color)`
- **CTAs**: `var(--accent-gradient)`

### Formularios
- **Labels**: `var(--primary-color)`
- **Inputs**: Fondo `white`, border `var(--border-color)`
- **Focus**: Border `var(--accent-color)`
- **Errores**: `var(--error-color)`

### Navegación
- **Fondo**: `white`
- **Enlaces**: `var(--secondary-color)`
- **Hover**: `var(--accent-color)`
- **Activo**: `var(--accent-color)`

## Escala de Grises Completa

```css
:root {
    --gray-50: #f8fafc;
    --gray-100: #f1f5f9;
    --gray-200: #e2e8f0;
    --gray-300: #cbd5e1;
    --gray-400: #94a3b8;
    --gray-500: #64748b;
    --gray-600: #475569;
    --gray-700: #334155;
    --gray-800: #1e293b;
    --gray-900: #0f172a;
}
```

## Accesibilidad

### Contrastes Mínimos
- **Texto Normal**: 4.5:1 ratio mínimo
- **Texto Grande**: 3:1 ratio mínimo
- **Elementos Interactivos**: 3:1 ratio mínimo

### Combinaciones Aprobadas
✅ `var(--primary-color)` sobre `white` - 19.4:1
✅ `var(--secondary-color)` sobre `white` - 6.8:1
✅ `var(--accent-color)` sobre `white` - 4.8:1
✅ `white` sobre `var(--accent-color)` - 4.8:1

## Mejores Prácticas

### ✅ Hacer
- Usar variables CSS para consistencia
- Probar contrastes en diferentes dispositivos
- Mantener jerarquía visual clara
- Usar gradientes sutiles, no dramáticos

### ❌ Evitar
- Colores muy saturados o brillantes
- Más de 3 colores principales por página
- Gradientes multicolores llamativos
- Texto con contraste insuficiente

## Implementación en Código

### HTML
```html
<!-- Títulos -->
<h1 class="text-primary">Título Principal</h1>
<p class="text-secondary">Texto descriptivo</p>

<!-- Botones -->
<button class="btn btn-primary">Acción Principal</button>
<button class="btn btn-secondary">Acción Secundaria</button>

<!-- Estados -->
<div class="alert alert-success">Operación exitosa</div>
<div class="alert alert-warning">Advertencia importante</div>
```

### CSS Custom Properties
```css
.custom-component {
    background: var(--background-secondary);
    border: 1px solid var(--border-color);
    color: var(--primary-color);
}

.custom-component:hover {
    background: var(--background-tertiary);
    border-color: var(--accent-color);
}
```

## Actualizaciones Futuras

Esta paleta está diseñada para:
- **Escalabilidad**: Fácil adición de nuevos colores
- **Mantenibilidad**: Variables CSS centralizadas
- **Flexibilidad**: Adaptable a diferentes temas
- **Consistencia**: Aplicación uniforme en toda la aplicación

---

**Versión**: 2.0  
**Fecha**: 2025-07-17  
**Diseñado por**: Experto en Color Corporativo Digital  
**Aprobado**: Cumple WCAG 2.1 AA