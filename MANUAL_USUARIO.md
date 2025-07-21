# 📖 Manual de Usuario - Buko AI

## 🎯 Guía Completa para Probar y Monitorear la Aplicación

> **NOTA:** Este manual asume que la aplicación Buko AI ya está levantada y funcionando. Si necesitas ayuda para levantar la aplicación, consulta el archivo `README.md` o `ESTADO_APLICACION.md`.

---

### 📋 Tabla de Contenidos

1. [Estado de la Aplicación](#estado-de-la-aplicación)
2. [URLs de Acceso](#urls-de-acceso)
3. [Pruebas Funcionales](#pruebas-funcionales)
4. [Página de Inicio Hipermega Atractiva](#página-de-inicio-hipermega-atractiva)
5. [Generación de Libros](#generación-de-libros)
6. [Monitoreo y Logs](#monitoreo-y-logs)
7. [Diferentes Entornos](#diferentes-entornos)
8. [Troubleshooting](#troubleshooting)
9. [Comandos Útiles](#comandos-útiles)

---

## 🚀 Estado de la Aplicación

### ✅ **Aplicación Operacional**
- **Estado:** FUNCIONANDO
- **Versión:** v1.0.0
- **Última actualización:** 2025-07-17
- **Progreso:** 27% completado (14/51 tareas)

### 🔍 **Verificación Rápida**
```bash
# Verificar que todos los contenedores estén corriendo con health checks
docker-compose -f docker-compose.dev.yml ps

# Verificar estado de la aplicación
curl -s http://localhost:5001/health | jq

# Verificar health checks de todos los servicios
curl -s http://localhost:5001/health    # Aplicación principal
curl -s http://localhost:5555/api/workers  # Flower (Celery monitor)
curl -s http://localhost:8025           # MailHog (Email testing)
curl -s http://localhost:8081           # Adminer (DB admin)
```

---

## 🌐 URLs de Acceso

| 🎯 Servicio | 🌍 URL | 📊 Puerto | 🔒 Credenciales | ✅ Estado | 🏥 Health Check |
|-------------|--------|-----------|------------------|-----------|-------------|
| **🚀 Aplicación Principal** | http://localhost:5001 | 5001 | Ver sección pruebas | ✅ FUNCIONANDO | ✅ HEALTHY |
| **🗄️ Base de Datos (Adminer)** | http://localhost:8081 | 8081 | postgres/postgres | ✅ FUNCIONANDO | ✅ HEALTHY |
| **📧 Email Testing (MailHog)** | http://localhost:8025 | 8025 | Sin credenciales | ✅ FUNCIONANDO | ✅ HEALTHY |
| **🌺 Monitor Celery (Flower)** | http://localhost:5555 | 5555 | Sin credenciales | ✅ FUNCIONANDO | ✅ HEALTHY |
| **⚖️ Reverse Proxy (Nginx)** | http://localhost:8082 | 8082 | Sin credenciales | ✅ FUNCIONANDO | ✅ HEALTHY |
| **🔄 Celery Beat** | - | - | - | ✅ FUNCIONANDO | ✅ HEALTHY |
| **👷 Celery Worker** | - | - | - | ✅ FUNCIONANDO | ✅ HEALTHY |
| **🗃️ PostgreSQL** | localhost:5434 | 5434 | postgres/postgres | ✅ FUNCIONANDO | ✅ HEALTHY |
| **🔴 Redis** | localhost:6380 | 6380 | Sin contraseña | ✅ FUNCIONANDO | ✅ HEALTHY |

### 🌟 **Servicios Esenciales para el Desarrollo**

#### 📧 **MailHog - Sistema de Email Testing**
- **Función:** Captura y muestra todos los emails enviados por la aplicación
- **URL:** http://localhost:8025
- **Características:**
  - Interfaz web intuitiva para visualizar emails
  - Captura automática de todos los emails SMTP
  - Soporte para HTML y texto plano
  - Búsqueda y filtrado de emails
  - API REST para integración
- **Casos de uso:**
  - Verificar emails de registro de usuarios
  - Probar emails de recuperación de contraseña
  - Validar templates de email
  - Depurar problemas de envío

#### 🗄️ **Adminer - Administrador de Base de Datos**
- **Función:** Interfaz web para gestión completa de PostgreSQL
- **URL:** http://localhost:8081
- **Características:**
  - Editor SQL con autocompletado
  - Explorador de tablas y datos
  - Importación/exportación de datos
  - Gestión de usuarios y permisos
  - Visualización de relaciones entre tablas
- **Casos de uso:**
  - Explorar estructura de la base de datos
  - Ejecutar consultas SQL personalizadas
  - Verificar datos de prueba
  - Realizar backups y restauraciones

### 🔐 **Credenciales de Acceso**

#### **Base de Datos PostgreSQL:**
- **Host:** localhost:5434
- **Database:** buko_ai_dev
- **Username:** postgres
- **Password:** postgres

#### **Redis:**
- **Host:** localhost:6380
- **Database:** 0
- **Password:** (sin contraseña)

---

## 🧪 Pruebas Funcionales

### 1. 🔐 **Probar Sistema de Autenticación**

#### **Registro de Usuario**
1. Ve a: http://localhost:5001/auth/register
2. Completa el formulario con datos válidos:
   ```
   Nombre: Juan
   Apellido: Pérez
   Email: juan@example.com
   Contraseña: MiPassword123!
   País: Colombia
   Ciudad: Bogotá
   Idioma: Español
   ✅ Acepto términos y condiciones
   ```
3. Haz clic en "Crear Cuenta"
4. **Resultado esperado:** Redirección a página principal con mensaje de éxito

#### **Inicio de Sesión**
1. Ve a: http://localhost:5001/auth/login
2. Ingresa credenciales:
   ```
   Email: juan@example.com
   Contraseña: MiPassword123!
   ✅ Recordarme (opcional)
   ```
3. Haz clic en "Iniciar Sesión"
4. **Resultado esperado:** Redirección al dashboard con mensaje de bienvenida

#### **Recuperación de Contraseña**
1. Ve a: http://localhost:5001/auth/login
2. Haz clic en "¿Olvidaste tu contraseña?"
3. Ingresa tu email
4. **Resultado esperado:** Mensaje de confirmación
5. **Verificar email:** Ve a http://localhost:8025 para ver el email

### 2. 📊 **Probar Endpoints de API**

#### **Health Check**
```bash
curl -s http://localhost:5001/health | jq
```
**Resultado esperado:**
```json
{
  "service": "buko-ai",
  "status": "healthy",
  "timestamp": "2025-01-17"
}
```

#### **Estado de Autenticación**
```bash
curl -s http://localhost:5001/auth/status | jq
```
**Resultado esperado:**
```json
{
  "api_routes": ["api/check-email", "api/session"],
  "message": "Authentication system fully implemented",
  "routes": ["login", "logout", "register", ...],
  "status": "active"
}
```

#### **Verificar Disponibilidad de Email**
```bash
curl -X POST http://localhost:5001/auth/api/check-email \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}' | jq
```

### 3. 🌐 **Probar Páginas Principales**

#### **Navegación Principal**
- **Inicio:** http://localhost:5001/
- **Características:** http://localhost:5001/features
- **Precios:** http://localhost:5001/pricing
- **Acerca de:** http://localhost:5001/about
- **Contacto:** http://localhost:5001/contact

#### **Dashboard (Requiere Login)**
- **Dashboard:** http://localhost:5001/dashboard
- **Mis Libros:** http://localhost:5001/my-books
- **Generar Libro:** http://localhost:5001/generate-book
- **Suscripción:** http://localhost:5001/subscription

### 4. 📧 **Probar Sistema de Email con MailHog**

#### **🎯 Acceder a MailHog**
1. Ve a: http://localhost:8025
2. **Interfaz disponible:**
   - Lista de emails capturados
   - Previsualización HTML/texto
   - Búsqueda por remitente, destinatario, asunto
   - Exportación de emails

#### **🧪 Probar Envío de Emails**
1. **Registro de Usuario:**
   - Registra un nuevo usuario en http://localhost:5001/auth/register
   - Ve a MailHog: http://localhost:8025
   - **Resultado esperado:** Email de bienvenida con template HTML

2. **Recuperación de Contraseña:**
   - Solicita recuperación en http://localhost:5001/auth/login
   - Ve a MailHog: http://localhost:8025
   - **Resultado esperado:** Email con enlace de recuperación

3. **Verificación de Email:**
   - Si está habilitada, verifica el email de confirmación
   - **Resultado esperado:** Email con enlace de verificación

#### **📧 Características Avanzadas de MailHog**
- **API REST:** `curl http://localhost:8025/api/v1/messages`
- **Eliminar emails:** Botón "Clear" en la interfaz
- **Descargar emails:** Formato .eml
- **Búsqueda:** Filtros por fecha, remitente, destinatario

---

## 🎨 Página de Inicio Hipermega Atractiva

### 🌟 **Características Implementadas**
Buko AI ahora cuenta con una página de inicio completamente rediseñada con tecnologías modernas y efectos visuales impactantes.

### 🎯 **Acceso a la Página**
- **URL:** http://localhost:5001
- **Descripción:** Landing page principal con diseño innovador
- **Tecnologías:** CSS3, JavaScript ES6, Bootstrap 5, animaciones CSS

### 🚀 **Secciones Implementadas**

#### **1. Hero Section**
- **Título dinámico:** "Transforma Ideas en Libros Épicos"
- **Animación shimmer:** Efecto de brillo en el texto
- **Gradientes modernos:** Múltiples gradientes CSS variables
- **Botones interactivos:** Efectos hover y animaciones
- **Partículas flotantes:** 15 partículas animadas con JavaScript

#### **2. Libro Flotante 3D**
- **Animación float:** Movimiento suave de arriba/abajo
- **Efectos 3D:** Transformaciones perspective y rotateY
- **Barra de progreso:** Animación de llenado continuo
- **Efectos pulse:** Resplandor sutil de fondo

#### **3. Sección de Estadísticas**
- **Números animados:** Conteo automático al aparecer en viewport
- **Backdrop blur:** Efecto glassmorphism
- **Hover effects:** Transformaciones al pasar el mouse
- **Gradientes en texto:** Colores degradados en números

#### **4. Grid de Características**
- **6 características principales** con iconos únicos
- **Micro-interacciones:** Hover con translateY y shadow
- **Gradientes por icono:** Cada característica tiene su color
- **Animaciones de bounce:** Iconos que "saltan" continuamente

#### **5. Testimonios con Glassmorphism**
- **3 testimonios dinámicos** con avatares
- **Efecto glass:** Blur y transparencia
- **Responsive grid:** Adaptable a diferentes pantallas
- **Hover effects:** Elevación y cambio de opacidad

#### **6. Call-to-Action Final**
- **Botones hero:** Estilos personalizados con gradientes
- **Efectos shine:** Brillo que se desplaza en hover
- **Responsive design:** Adaptable a móviles

### 🎨 **Efectos Visuales Implementados**

#### **Animaciones CSS**
```css
- shimmer: Efecto de brillo en títulos
- float-bg: Fondo animado con rotación
- float-book: Libro flotante 3D
- pulse: Resplandor pulsante
- progress-fill: Barra de progreso animada
- particle-float: Partículas flotantes
- icon-bounce: Iconos que rebotan
```

#### **Efectos JavaScript**
```javascript
- Animación de números en estadísticas
- Generación dinámica de partículas
- Efecto parallax en scroll
- Intersection Observer para animaciones
```

### 🧪 **Pruebas de la Página de Inicio**

#### **Prueba 1: Animaciones Hero**
```bash
# Test: Efectos visuales del hero
1. Ve a: http://localhost:5001
2. Observa el título principal
3. Resultado esperado: Efecto shimmer en "Transforma Ideas en Libros Épicos"
4. Observa las partículas flotantes
5. Resultado esperado: Múltiples puntos animados subiendo
```

#### **Prueba 2: Libro Flotante 3D**
```bash
# Test: Animación del libro
1. Observa el libro en el lado derecho
2. Resultado esperado: Libro flotando suavemente
3. Observa la barra de progreso
4. Resultado esperado: Barra se llena y resetea continuamente
```

#### **Prueba 3: Estadísticas Animadas**
```bash
# Test: Conteo automático
1. Scroll hacia la sección de estadísticas
2. Resultado esperado: Números empiezan a contar desde 0
3. Observa el efecto glass en las tarjetas
4. Resultado esperado: Fondo translúcido con blur
```

#### **Prueba 4: Características Interactivas**
```bash
# Test: Hover effects
1. Pasa el mouse sobre las tarjetas de características
2. Resultado esperado: Tarjeta se eleva y cambia shadow
3. Observa los iconos
4. Resultado esperado: Iconos rebotan continuamente
```

#### **Prueba 5: Responsive Design**
```bash
# Test: Adaptabilidad móvil
1. Redimensiona la ventana del navegador
2. Resultado esperado: Layout se adapta a pantallas pequeñas
3. Prueba en móvil/tablet
4. Resultado esperado: Todos los elementos se reorganizan correctamente
```

### 🎯 **Características Técnicas**

#### **Performance**
- **CSS optimizado:** Variables CSS para reutilización
- **Animaciones GPU:** Uso de transform y opacity
- **Lazy loading:** Intersection Observer para animaciones
- **Código limpio:** Separación de estilos y lógica

#### **Accesibilidad**
- **Contraste adecuado:** Colores accesibles
- **Responsive design:** Adaptable a todos los dispositivos
- **Animaciones opcionales:** Respeta prefer-reduced-motion
- **Semantic HTML:** Estructura semántica correcta

### 🌐 **Compatibilidad**
- **Navegadores:** Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- **Dispositivos:** Desktop, tablet, móvil
- **Resoluciones:** 320px - 4K
- **Tecnologías:** CSS Grid, Flexbox, CSS Custom Properties

### 🔧 **Personalización**
```css
/* Variables CSS principales */
:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    --accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    --success-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    --warning-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    --dark-gradient: linear-gradient(135deg, #434343 0%, #000000 100%);
}
```

---

## 📚 Generación de Libros

### 🎯 **Introducción**
Buko AI ahora incluye un formulario wizard multi-paso para generar libros con inteligencia artificial. El formulario es completamente responsivo y incluye validación en tiempo real.

### 🚀 **Acceso al Generador**
1. **Acceder:** http://localhost:5001/books/generate
2. **Requisitos:** Usuario autenticado con suscripción activa
3. **Navegación:** Menú superior → "Generar Libro"

### 🎨 **Pasos del Wizard**

#### **Paso 1: Información Básica**
- **Título del Libro:** Mínimo 3 caracteres, máximo 100
- **Género:** Selección visual entre 12 géneros disponibles
  - Ficción, No Ficción, Infantil, Poesía, Técnico, Autoayuda
  - Biografía, Historia, Ciencia Ficción, Romance, Misterio, Fantasía
- **Idioma:** Español, Inglés, Portugués, Francés
- **Validación:** En tiempo real mientras escribes

#### **Paso 2: Descripción y Audiencia**
- **Descripción:** Mínimo 20 caracteres, máximo 1000
- **Audiencia Objetivo:** Niños, Adolescentes, Adultos, Todas las edades
- **Tono:** Formal, Casual, Humorístico, Serio, Inspiracional, Educativo
- **Validación:** En tiempo real con contador de caracteres

#### **Paso 3: Configuración Avanzada**
- **Número de Capítulos:** Entre 1 y 50
- **Longitud del Libro:** Corto (50-100 páginas), Medio (100-200), Largo (200+)
- **Instrucciones Adicionales:** Opcional, máximo 500 caracteres
- **Validación:** Rangos automáticos y mensajes de error

#### **Paso 4: Revisión y Confirmación**
- **Resumen:** Todos los datos ingresados
- **Estimación:** Tiempo de generación (5-15 minutos)
- **Confirmación:** Botón "Generar Libro"

### 🔍 **Vista Previa en Tiempo Real**
- **Panel derecho:** Actualización automática
- **Información mostrada:**
  - Título del libro
  - Páginas estimadas
  - Palabras aproximadas
  - Tabla de contenidos (capítulos)
- **Información de suscripción:** Límites y uso actual

### 📊 **Limitaciones por Suscripción**
- **Free:** 1 libro por mes
- **Starter:** 5 libros por mes
- **Pro:** 20 libros por mes
- **Business:** 50 libros por mes
- **Enterprise:** 999 libros por mes

### 🔄 **Proceso de Generación**
1. **Envío:** Formulario se envía al backend
2. **Validación:** Servidor valida todos los datos
3. **Cola:** Tarea se agrega a Celery
4. **Redirección:** Usuario va a página de estado
5. **Generación:** IA procesa el libro
6. **Notificación:** Estado se actualiza en tiempo real

### 🧪 **Pruebas del Formulario**

#### **Prueba 1: Validación en Tiempo Real**
```bash
# Test: Validación de título
1. Ve a: http://localhost:5001/books/generate
2. Campo título: Escribe "Hi" (menos de 3 caracteres)
3. Resultado esperado: Error "El título debe tener al menos 3 caracteres"
4. Escribe un título válido
5. Resultado esperado: Error desaparece
```

#### **Prueba 2: Selector de Géneros**
```bash
# Test: Selección visual de géneros
1. Paso 1 del wizard
2. Haz clic en diferentes géneros
3. Resultado esperado: Tarjeta se resalta en azul
4. Selecciona "Ficción"
5. Resultado esperado: Género seleccionado, validación OK
```

#### **Prueba 3: Vista Previa**
```bash
# Test: Preview en tiempo real
1. Completa Paso 1 con título y género
2. Observa panel derecho
3. Resultado esperado: Vista previa se actualiza
4. Cambia número de capítulos en Paso 3
5. Resultado esperado: Vista previa refleja cambios
```

#### **Prueba 4: Navegación del Wizard**
```bash
# Test: Navegación entre pasos
1. Completa Paso 1 correctamente
2. Clic en "Siguiente"
3. Resultado esperado: Avanza a Paso 2
4. Clic en "Anterior"
5. Resultado esperado: Regresa a Paso 1 con datos intactos
```

#### **Prueba 5: Validación de Suscripción**
```bash
# Test: Límites de suscripción
1. Usuario con plan Free que ya generó 1 libro
2. Intenta acceder a /books/generate
3. Resultado esperado: Redirección a pricing con mensaje de límite
4. Usuario con plan activo
5. Resultado esperado: Acceso normal al wizard
```

### 🌐 **URLs Relacionadas**
- **Generador:** http://localhost:5001/books/generate
- **Mis Libros:** http://localhost:5001/books/my-books
- **Estado de Generación:** http://localhost:5001/books/generation/{id}
- **Ver Libro:** http://localhost:5001/books/book/{id}

### 🎯 **Próximas Funcionalidades**
- **Sistema de Colas:** Procesamiento asíncrono con Celery
- **Generación de Archivos:** PDF, EPUB, DOCX
- **WebSocket:** Actualizaciones en tiempo real
- **Gestión de Libros:** Biblioteca personal completa

---

## 📊 Monitoreo y Logs

### 1. 📈 **Monitoreo de Contenedores**

#### **Estado General con Health Checks**
```bash
# Ver estado de todos los contenedores con health checks
docker-compose -f docker-compose.dev.yml ps

# Monitoreo de recursos en tiempo real
docker stats

# Verificar health checks específicos
docker inspect --format='{{.State.Health.Status}}' buko-ai-web-dev
docker inspect --format='{{.State.Health.Status}}' buko-ai-flower-dev
docker inspect --format='{{.State.Health.Status}}' buko-ai-mailhog-dev
docker inspect --format='{{.State.Health.Status}}' buko-ai-adminer-dev

# Verificar logs de todos los servicios
docker-compose -f docker-compose.dev.yml logs --tail=50
```

#### **Monitoreo por Servicio**
```bash
# Logs de la aplicación web
docker-compose -f docker-compose.dev.yml logs -f web

# Logs de la base de datos
docker-compose -f docker-compose.dev.yml logs -f db

# Logs de Redis
docker-compose -f docker-compose.dev.yml logs -f redis

# Logs de Celery Worker
docker-compose -f docker-compose.dev.yml logs -f worker
```

### 2. 🔍 **Monitoreo de Celery**

#### **Flower Dashboard**
1. Ve a: http://localhost:5555
2. **Funcionalidades disponibles:**
   - Monitor de workers activos
   - Estadísticas de tareas
   - Métricas de rendimiento
   - Historial de tareas

#### **Comandos de Celery**
```bash
# Estado de workers
docker-compose -f docker-compose.dev.yml exec worker celery -A app.celery status

# Inspeccionar workers
docker-compose -f docker-compose.dev.yml exec worker celery -A app.celery inspect active

# Estadísticas de tareas
docker-compose -f docker-compose.dev.yml exec worker celery -A app.celery inspect stats
```

### 3. 🗄️ **Monitoreo de Base de Datos con Adminer**

#### **🎯 Acceder a Adminer**
1. Ve a: http://localhost:8081
2. **Credenciales de acceso:**
   - **Sistema:** PostgreSQL
   - **Servidor:** db
   - **Usuario:** postgres
   - **Contraseña:** postgres
   - **Base de datos:** buko_ai_dev

#### **🔧 Funcionalidades Principales**
1. **Explorador de Tablas:**
   - Ver estructura de tablas
   - Navegar entre relaciones
   - Visualizar índices y constrains

2. **Editor SQL:**
   - Autocompletado de comandos
   - Ejecución de consultas personalizadas
   - Historial de consultas

3. **Gestión de Datos:**
   - Insertar, editar, eliminar registros
   - Importar/exportar datos (CSV, SQL)
   - Búsqueda avanzada

#### **📊 Consultas Útiles para Buko AI**
```sql
-- Ver todos los usuarios registrados
SELECT id, first_name, last_name, email, created_at 
FROM users 
ORDER BY created_at DESC;

-- Contar usuarios por país
SELECT country, COUNT(*) as total_users 
FROM users 
GROUP BY country 
ORDER BY total_users DESC;

-- Ver actividad reciente
SELECT * FROM users 
WHERE created_at > NOW() - INTERVAL '7 days';

-- Verificar integridad de datos
SELECT COUNT(*) as total_users FROM users;
SELECT COUNT(*) as active_users FROM users WHERE is_active = true;
```

#### **🔍 Comandos Directos (Opcional)**
```bash
# Conectar a PostgreSQL desde línea de comandos
docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d buko_ai_dev

# Comandos útiles SQL
\dt              # Listar tablas
\d users         # Describir tabla users
\l               # Listar bases de datos
\q               # Salir
```

#### **⚠️ Mejores Prácticas con Adminer**
- **Desarrollo:** Usar libremente para explorar y depurar
- **Staging:** Acceso solo lectura recomendado
- **Producción:** Acceso restringido con credenciales específicas
- **Backup:** Siempre hacer backup antes de modificaciones importantes

### 4. 🔄 **Monitoreo de Redis**

#### **Redis CLI**
```bash
# Conectar a Redis
docker-compose -f docker-compose.dev.yml exec redis redis-cli

# Comandos útiles Redis
INFO            # Información del servidor
KEYS *          # Ver todas las keys
DBSIZE          # Tamaño de la base de datos
FLUSHDB         # Limpiar base de datos (cuidado!)
EXIT            # Salir
```

---

## 🌍 Diferentes Entornos

### 🛠️ **Entorno de Desarrollo**
- **Características:** Debug habilitado, hot reload, datos de prueba
- **URL:** http://localhost:5001
- **Comando:** `docker-compose -f docker-compose.dev.yml up -d`

#### **Pruebas Específicas de Desarrollo:**
```bash
# Verificar hot reload
# 1. Modifica cualquier archivo Python
# 2. Observa los logs: docker-compose -f docker-compose.dev.yml logs -f web
# 3. Resultado: Aplicación se reinicia automáticamente

# Verificar debug mode
# 1. Causa un error intencional visitando una URL inexistente
# 2. Resultado: Página de error detallada con stack trace
```

### 🎭 **Entorno de Staging**
- **Características:** Producción simulada, SSL, datos realistas
- **URL:** http://localhost:8080
- **Comando:** `docker-compose -f docker-compose.staging.yml up -d`

#### **Pruebas Específicas de Staging:**
```bash
# Verificar SSL
curl -I http://localhost:8080
# Resultado: Debe redirigir a HTTPS

# Verificar rendimiento
curl -o /dev/null -s -w "Time: %{time_total}s\n" http://localhost:8080
# Resultado: Tiempo de respuesta optimizado
```

### 🚀 **Entorno de Producción**
- **Características:** Máximo rendimiento, seguridad, monitoreo completo
- **URL:** http://localhost (puerto 80/443)
- **Comando:** `docker-compose -f docker-compose.prod.yml up -d`

#### **Pruebas Específicas de Producción:**
```bash
# Verificar headers de seguridad
curl -I http://localhost | grep -i security
# Resultado: Headers de seguridad configurados

# Verificar compresión
curl -I -H "Accept-Encoding: gzip" http://localhost
# Resultado: Content-Encoding: gzip

# Verificar cache
curl -I http://localhost/static/css/main.css
# Resultado: Cache-Control headers configurados
```

---

## 🔧 Troubleshooting

### 🚨 **Problemas Comunes**

#### **Aplicación no responde**
```bash
# 1. Verificar estado de contenedores con health checks
docker-compose -f docker-compose.dev.yml ps

# 2. Verificar health checks específicos
docker inspect --format='{{.State.Health.Status}}' buko-ai-web-dev
curl -s http://localhost:5001/health

# 3. Ver logs de errores
docker-compose -f docker-compose.dev.yml logs web --tail=50

# 4. Reiniciar aplicación
docker-compose -f docker-compose.dev.yml restart web
```

#### **Base de datos no conecta**
```bash
# 1. Verificar PostgreSQL
docker-compose -f docker-compose.dev.yml exec db pg_isready -U postgres

# 2. Verificar logs de BD
docker-compose -f docker-compose.dev.yml logs db --tail=20

# 3. Reiniciar BD
docker-compose -f docker-compose.dev.yml restart db
```

#### **Redis no funciona**
```bash
# 1. Verificar Redis
docker-compose -f docker-compose.dev.yml exec redis redis-cli ping

# 2. Ver logs de Redis
docker-compose -f docker-compose.dev.yml logs redis --tail=20

# 3. Verificar health check de Redis
docker inspect --format='{{.State.Health.Status}}' buko-ai-redis-dev
```

#### **Health Checks Fallan**
```bash
# 1. Verificar estado de todos los health checks
docker-compose -f docker-compose.dev.yml ps

# 2. Verificar logs de health checks
docker inspect --format='{{.State.Health.Log}}' buko-ai-web-dev
docker inspect --format='{{.State.Health.Log}}' buko-ai-flower-dev
docker inspect --format='{{.State.Health.Log}}' buko-ai-mailhog-dev
docker inspect --format='{{.State.Health.Log}}' buko-ai-adminer-dev

# 3. Probar health checks manualmente
curl -s http://localhost:5001/health
curl -s http://localhost:5555/api/workers
curl -s http://localhost:8025
curl -s http://localhost:8081

# 4. Reiniciar servicios con problemas
docker-compose -f docker-compose.dev.yml restart flower mailhog adminer
```


#### **Emails no se envían**
```bash
# 1. Verificar MailHog
curl -I http://localhost:8025

# 2. Ver logs de aplicación
docker-compose -f docker-compose.dev.yml logs web | grep -i mail

# 3. Reiniciar MailHog
docker-compose -f docker-compose.dev.yml restart mailhog
```

### 🩺 **Diagnóstico Avanzado**

#### **Verificar Conectividad de Red**
```bash
# Verificar conectividad entre servicios
docker-compose -f docker-compose.dev.yml exec web ping db
docker-compose -f docker-compose.dev.yml exec web ping redis

# Verificar DNS interno
docker-compose -f docker-compose.dev.yml exec web nslookup db
```

#### **Verificar Recursos del Sistema**
```bash
# Uso de memoria y CPU
docker stats --no-stream

# Espacio en disco
docker system df

# Limpiar recursos si es necesario
docker system prune -a
```

---

## 📋 Comandos Útiles

### 🔄 **Gestión de Contenedores**
```bash
# Iniciar todos los servicios
docker-compose -f docker-compose.dev.yml up -d

# Parar todos los servicios
docker-compose -f docker-compose.dev.yml down

# Reiniciar servicio específico
docker-compose -f docker-compose.dev.yml restart web

# Reconstruir y levantar
docker-compose -f docker-compose.dev.yml up -d --build

# Ver logs en tiempo real
docker-compose -f docker-compose.dev.yml logs -f

# Ejecutar comandos en contenedor
docker-compose -f docker-compose.dev.yml exec web bash
```

### 🗄️ **Gestión de Base de Datos**
```bash
# Ejecutar migraciones
docker-compose -f docker-compose.dev.yml exec web flask db upgrade

# Crear nueva migración
docker-compose -f docker-compose.dev.yml exec web flask db migrate -m "Descripción"

# Ver estado de migraciones
docker-compose -f docker-compose.dev.yml exec web flask db current

# Backup de base de datos
docker-compose -f docker-compose.dev.yml exec db pg_dump -U postgres buko_ai_dev > backup.sql
```

### 🧪 **Comandos de Testing**
```bash
# Ejecutar tests
docker-compose -f docker-compose.dev.yml exec web pytest

# Tests con coverage
docker-compose -f docker-compose.dev.yml exec web pytest --cov=app

# Linting
docker-compose -f docker-compose.dev.yml exec web flake8 app

# Formatear código
docker-compose -f docker-compose.dev.yml exec web black app
```

---

## 📊 Checklist de Verificación

### ✅ **Verificación Completa**
- [ ] **Aplicación Principal:** Accesible en http://localhost:5001
- [ ] **Health Check:** Retorna status "healthy"
- [ ] **Autenticación:** Registro de usuario funciona correctamente
- [ ] **Autenticación:** Login/logout funciona correctamente
- [ ] **MailHog:** Emails se capturan y visualizan correctamente
- [ ] **Adminer:** Base de datos accesible y funcional
- [ ] **Redis:** Cache y message broker funcionando
- [ ] **Logs:** Estructurados y accesibles
- [ ] **Celery:** Workers y Beat están activos
- [ ] **API:** Todos los endpoints responden correctamente
- [ ] **Docker:** Todos los servicios muestran "healthy"
- [ ] **Flower:** Monitor Celery accesible en http://localhost:5555
- [ ] **MailHog:** Interfaz web accesible en http://localhost:8025
- [ ] **Adminer:** Interfaz DB accesible en http://localhost:8081
- [ ] **Health Checks:** API funcionan correctamente

### 🔧 **Verificación Específica de MailHog**
- [ ] **Interfaz Web:** http://localhost:8025 carga correctamente
- [ ] **Captura de Emails:** Emails de registro aparecen automáticamente
- [ ] **Templates HTML:** Se visualizan correctamente
- [ ] **Búsqueda:** Funciona el filtrado de emails
- [ ] **API REST:** `curl http://localhost:8025/api/v1/messages` responde

### 🔧 **Verificación Específica de Adminer**
- [ ] **Interfaz Web:** http://localhost:8081 carga correctamente
- [ ] **Conexión DB:** Se conecta con credenciales postgres/postgres
- [ ] **Explorador:** Muestra todas las tablas correctamente
- [ ] **Editor SQL:** Ejecuta consultas sin errores
- [ ] **Datos:** Muestra registros de usuarios existentes

### 🎯 **Métricas de Rendimiento**
- [ ] Tiempo de respuesta < 500ms para todos los endpoints
- [ ] Uso de memoria < 512MB por servicio
- [ ] Uso de CPU < 50% por servicio
- [ ] Sin errores en logs de aplicación
- [ ] Todos los health checks pasan (9/9 servicios)
- [ ] Health checks responden en < 10 segundos
- [ ] Servicios se reinician automáticamente si fallan

---

## 🆘 Contacto y Soporte

### 📞 **¿Necesitas Ayuda?**
1. **Consulta logs:** `docker-compose -f docker-compose.dev.yml logs`
2. **Verifica configuración:** Revisa archivos `.env`
3. **Reinicia servicios:** `docker-compose -f docker-compose.dev.yml restart`
4. **Reinicio completo:** `docker-compose -f docker-compose.dev.yml down -v && docker-compose -f docker-compose.dev.yml up -d`

### 📚 **Recursos Adicionales**
- [Documentación Docker](https://docs.docker.com/)
- [Documentación Flask](https://flask.palletsprojects.com/)
- [Documentación PostgreSQL](https://www.postgresql.org/docs/)
- [Documentación Redis](https://redis.io/documentation)

---

**¡Feliz testing! 🎉**

*Última actualización: 2025-07-17 - Agregados health checks completos y documentación detallada de MailHog y Adminer*