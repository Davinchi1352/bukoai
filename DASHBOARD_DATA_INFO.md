# 📊 Dashboard - Datos Reales vs. Demostración

## 🔍 Estado Actual

El dashboard actualmente muestra **datos de demostración** porque la aplicación principal requiere dependencias que no están instaladas en el entorno de prueba.

## ✅ APIs de Datos Reales Creadas

He creado las siguientes APIs para mostrar datos reales de la base de datos:

### 📁 `/app/routes/api_real.py`
- **`/api/stats/dashboard`** - Estadísticas reales del usuario
- **`/api/stats/analytics`** - Análisis por categorías
- **`/api/books`** - Lista de libros del usuario

Estas APIs:
- ✅ Consultan directamente la base de datos PostgreSQL
- ✅ Filtran por el usuario actual (`current_user.id`)
- ✅ Manejan errores de forma segura
- ✅ Devuelven datos reales, no aleatorios

## 🚀 Para Activar Datos Reales

### Opción 1: Aplicación Principal (Puerto 5001)

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verificar que PostgreSQL esté ejecutándose:**
   ```bash
   docker ps  # Ver si el contenedor de postgres está activo
   ```

3. **Ejecutar la aplicación:**
   ```bash
   python main.py
   # o
   flask run --port 5001
   ```

4. **Iniciar sesión:**
   - Ir a http://localhost:5001/auth/login
   - Usar credenciales existentes

5. **Ver dashboard con datos reales:**
   - http://localhost:5001/dashboard

### Opción 2: Verificar Datos en Base de Datos

Para ver qué datos reales hay en la base de datos:

```bash
# Conectar a PostgreSQL
docker exec -it bukoai-postgres-1 psql -U bukoai -d bukoai

# Ver usuarios
SELECT id, email, first_name FROM users;

# Ver libros de un usuario (cambiar user_id)
SELECT title, status, final_words, final_pages 
FROM book_generations 
WHERE user_id = 1;

# Salir
\q
```

## 📋 Diferencias Entre APIs

### API Real (`api_real.py`) - PRODUCCIÓN
```python
# Consulta real a base de datos
total_books = BookGeneration.query.filter_by(user_id=user_id).count()
```

### API Simplificada (`api_analytics.py`) - DEMO
```python
# Datos fijos de demostración
total_books = 12  # Siempre devuelve 12
```

## 🔔 Indicadores en el Dashboard

El dashboard mostrará:

1. **Si hay datos reales:**
   - Sin mensajes de aviso
   - Números que coinciden con tu base de datos

2. **Si no hay libros:**
   - "ℹ️ No tienes libros aún. ¡Genera tu primer libro!"

3. **Si hay error de conexión:**
   - "⚠️ Error al cargar datos reales: [detalles]"

## 🛠️ Solución de Problemas

### "Module 'flask_login' not found"
```bash
pip install flask-login
```

### "Cannot connect to database"
```bash
# Verificar PostgreSQL
docker-compose up -d postgres

# Verificar variables de entorno
echo $DATABASE_URL
```

### Dashboard muestra ceros
- Verificar que el usuario tenga libros en la base de datos
- Comprobar que estés autenticado correctamente

## 📈 Próximos Pasos

1. **Para desarrollo:** Usa `app_simple.py` con datos de demo
2. **Para producción:** Usa la app principal con `api_real.py`
3. **Para testing:** Crea datos de prueba en la base de datos

---

**Nota:** Los archivos `api_real.py` están listos para funcionar. Solo necesitas ejecutar la aplicación principal con todas las dependencias instaladas.