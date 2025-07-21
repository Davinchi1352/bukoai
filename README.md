# Buko AI - Generador de Libros con Inteligencia Artificial

![Buko AI Logo](./app/static/img/logo.png)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-85%25-yellow)
![License](https://img.shields.io/badge/license-MIT-blue)

## 📚 Descripción

Buko AI democratiza la creación de libros profesionales usando IA avanzada. Transforma ideas en libros completos en minutos, no meses.

## 🚀 Características Principales

- ✨ Generación de libros con Claude AI (streaming)
- 📖 Múltiples formatos: PDF, EPUB, DOCX
- 💳 Sistema de suscripciones con PayPal y MercadoPago
- 🎨 Editor de portadas con IA
- 📊 Dashboard analytics en tiempo real
- 🌐 Multiidioma (ES/EN)

## 🛠️ Stack Tecnológico

- **Backend**: Python 3.12+, Flask 3.0+, SQLAlchemy
- **Frontend**: Tailwind CSS, Alpine.js, Three.js
- **Base de datos**: PostgreSQL 16+
- **Queue**: Celery + Redis
- **IA**: Claude AI API (Anthropic)
- **Infraestructura**: Docker, Nginx, Gunicorn

## 📋 Requisitos Previos

- Docker y Docker Compose
- Python 3.12+
- Node.js 18+ (para assets)
- PostgreSQL 16+
- Redis 7+
- Cuenta de Anthropic API

## ⚡ Instalación Rápida

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tuempresa/buko-ai.git
   cd buko-ai
   ```

2. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus credenciales
   ```

3. **Construir y ejecutar con Docker**
   ```bash
   docker-compose up --build
   ```

4. **Ejecutar migraciones**
   ```bash
   docker-compose exec web flask db upgrade
   ```

5. **Inicializar datos**
   ```bash
   docker-compose exec web python scripts/init_db.py
   ```

La aplicación estará disponible en http://localhost

## 🔧 Desarrollo Local

### Sin Docker

1. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar base de datos**
   ```bash
   flask db upgrade
   ```

4. **Ejecutar aplicación**
   ```bash
   flask run
   ```

### Ejecutar Celery Worker

```bash
celery -A app.celery worker --loglevel=info
```

## 🏗️ Arquitectura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Cliente   │────▶│    Nginx    │────▶│    Flask    │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
                    ┌─────────────┐     ┌─────────────┐
                    │    Redis    │◀────│   Celery    │
                    └─────────────┘     └─────────────┘
                                               │
                    ┌─────────────┐            ▼
                    │ PostgreSQL  │     ┌─────────────┐
                    └─────────────┘     │ Claude API  │
                                        └─────────────┘
```

## 📁 Estructura del Proyecto

- `app/` - Aplicación principal Flask
- `app/models/` - Modelos de base de datos
- `app/routes/` - Endpoints y vistas
- `app/services/` - Lógica de negocio
- `app/static/` - Assets estáticos
- `app/templates/` - Templates HTML
- `config/` - Configuraciones
- `docs/` - Documentación técnica
- `tests/` - Tests unitarios y de integración

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=app

# Tests específicos
pytest tests/test_book_generation.py
```

## 📚 Documentación

- [Guía de API](./docs/api.md)
- [Arquitectura Detallada](./docs/architecture.md)
- [Guía de Deployment](./docs/deployment.md)
- [Troubleshooting](./docs/troubleshooting.md)

## 🚀 Deployment

### Producción con Docker

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Variables de Entorno Importantes

```env
# Claude AI
ANTHROPIC_API_KEY=your-api-key

# Base de datos
DATABASE_URL=postgresql://user:pass@localhost/buko_ai

# Redis
REDIS_URL=redis://localhost:6379

# Pagos
PAYPAL_CLIENT_ID=your-paypal-id
MP_ACCESS_TOKEN=your-mercadopago-token

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

### Estándares de Código

- Python: PEP 8
- JavaScript: ESLint config
- Commits: Conventional Commits
- Tests: Mínimo 80% coverage

## 📈 Monitoreo

- Logs: `docker-compose logs -f`
- Métricas: Dashboard admin en `/admin`
- Errores: Sentry (si configurado)

## 🐛 Troubleshooting

### Error: "Connection refused to PostgreSQL"
```bash
docker-compose restart db
```

### Error: "Celery worker not processing tasks"
```bash
docker-compose restart celery
```

Más soluciones en [docs/troubleshooting.md](./docs/troubleshooting.md)

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para detalles.

## 🌟 Agradecimientos

- Claude AI por la generación de contenido
- Comunidad Flask por el framework
- Contribuidores del proyecto

## 📞 Contacto

- Email: soporte@buko-ai.com
- Website: https://buko-ai.com
- Twitter: @BukoAI

---

Hecho con ❤️ por el equipo de Buko AI