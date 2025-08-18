# Prompt para Desarrollo de Buko AI - Plataforma de Generación de Libros con IA

## 🎯 OBJETIVO PRINCIPAL
Desarrollar una plataforma web completa llamada "Buko AI" que permita a usuarios generar libros profesionales usando Claude AI, con sistema de suscripciones, pagos integrados y panel administrativo. El desarrollo debe ser modular, escalable y desplegable en Docker para VPS.

## 📋 CONTEXTO DEL PROBLEMA
- Escribir un libro tradicionalmente toma 6-12 meses
- Los ghostwriters cobran entre $5,000-$50,000
- Existe una barrera alta para personas con buenas ideas pero sin habilidades de escritura
- Solución: Democratizar la creación de libros mediante IA

## 🏗️ ARQUITECTURA TÉCNICA

### Stack Tecnológico
- **Backend**: Python 3.12+, Flask 3.0+, SQLAlchemy, Flask-Migrate
- **Base de datos**: PostgreSQL 16+
- **Frontend**: HTML5, Tailwind CSS 3.0+, Alpine.js para interactividad
- **Queue**: Celery + Redis para procesamiento en background
- **Servidor**: Nginx (load balancing), Gunicorn
- **Contenedores**: Docker + Docker Compose
- **IA**: Claude AI API (Anthropic)
- **Pagos**: PayPal + MercadoPago
- **Idiomas**: Español (base) + inglés (plugin i18n)

### Estructura de Carpetas
```
buko-ai/
├── app/
│   ├── __init__.py
│   ├── models/          # Modelos SQLAlchemy
│   ├── routes/          # Blueprints Flask
│   ├── services/        # Lógica de negocio
│   ├── templates/       # HTML templates
│   ├── static/
│   │   ├── css/
│   │   ├── js/         # JavaScript separado
│   │   └── img/
│   └── utils/          # Utilidades
├── migrations/         # Flask-Migrate
├── config/
├── docker/
├── docs/              # Documentación técnica
├── tests/
├── requirements.txt
├── docker-compose.yml
├── README.md          # Documentación principal
├── CHANGELOG.md       # Historial de cambios
├── LICENSE            # Licencia del proyecto
└── .env.example
```

### Contenido del README.md
El README.md debe incluir:

```markdown
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
```

## 💼 MODELO DE NEGOCIO

### Planes de Suscripción (configurables desde admin)
```python
SUBSCRIPTION_PLANS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'books_per_month': 1,
        'max_pages': 30,
        'features': ['Libro básico', 'Formato PDF']
    },
    'starter': {
        'name': 'Starter',
        'price': 19,
        'books_per_month': 2,
        'max_pages': 100,
        'features': ['Todos los formatos', 'Soporte email']
    },
    'pro': {
        'name': 'Pro',
        'price': 49,
        'books_per_month': 5,
        'max_pages': 150,
        'features': ['Prioridad en cola', 'Diseño portada básico']
    },
    'business': {
        'name': 'Business',
        'price': 149,
        'books_per_month': 15,
        'max_pages': 200,
        'features': ['API access', 'Soporte prioritario']
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 399,
        'books_per_month': 50,
        'max_pages': 200,
        'features': ['Dedicado', 'SLA garantizado']
    }
}

# Add-ons
ADDONS = {
    'cover_design': {'price': 5, 'name': 'Diseño de Portada Premium'},
    'formatting': {'price': 3, 'name': 'Formateo Profesional'}
}

# Pay-per-book
PAY_PER_BOOK_PRICE = 15  # Configurable desde admin
```

## 🔧 FUNCIONALIDADES CORE

### 1. Sistema de Usuarios
```python
# Modelo de Usuario
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_country = db.Column(db.String(5))
    phone_number = db.Column(db.String(20))
    country = db.Column(db.String(50))
    city = db.Column(db.String(50))
    billing_address = db.Column(db.Text)
    subscription_type = db.Column(db.String(20), default='free')
    subscription_end = db.Column(db.DateTime)
    books_used_this_month = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    preferred_language = db.Column(db.String(5), default='es')
```

### 2. Generador de Libros - Interfaz Usuario
```python
# Campos del formulario de generación
book_form_fields = {
    'title': 'Título del libro',
    'genre': 'Género/Tipo (ficción, no-ficción, técnico, etc.)',
    'target_audience': 'Audiencia objetivo',
    'tone': 'Tono (formal, casual, académico, etc.)',
    'key_topics': 'Temas principales a cubrir',
    'chapter_count': 'Número aproximado de capítulos',
    'page_count': 'Número de páginas deseadas (máx según plan)',
    'format_size': 'Formato (Carta, A4, 6x9", 5.5x8.5", etc.)',
    'language': 'Idioma del libro (es/en)',
    'additional_instructions': 'Instrucciones adicionales',
    'include_toc': 'Incluir tabla de contenidos',
    'include_introduction': 'Incluir introducción',
    'include_conclusion': 'Incluir conclusión',
    'writing_style': 'Estilo de escritura específico'
}
```

### 3. Integración Claude AI con Streaming
```python
import anthropic
import os
from typing import Dict, Any, AsyncGenerator
import asyncio
import json

# Configuración de Claude AI
CLAUDE_CONFIG = {
    'api_key': os.environ.get("ANTHROPIC_API_KEY"),
    'model': 'claude-opus-4-20250514',  # Modelo correcto según docs
    'max_tokens': 64000,
    'temperature': 1,
    'thinking_budget': 63999  # Budget para pensamiento extendido
}

# Servicio asíncrono desde el inicio
class BookGenerationService:
    def __init__(self):
        self.claude_client = anthropic.Anthropic(
            api_key=CLAUDE_CONFIG['api_key']
        )
        # Cliente async para streaming
        self.async_claude_client = anthropic.AsyncAnthropic(
            api_key=CLAUDE_CONFIG['api_key']
        )
    
    def initiate_generation(self, user_id: int, book_params: Dict[str, Any]) -> Dict[str, Any]:
        # Crear registro en BD
        book = BookGeneration(
            user_id=user_id,
            title=book_params['title'],
            parameters=book_params,
            status='queued',
            created_at=datetime.utcnow()
        )
        db.session.add(book)
        db.session.commit()
        
        # Enviar a cola asíncrona inmediatamente
        generate_book_async.delay(book.id)
        
        # Retornar ID para tracking
        return {
            'book_id': book.id,
            'status': 'queued',
            'estimated_time': self.estimate_generation_time(book_params),
            'position_in_queue': self.get_queue_position(book.id)
        }
    
    async def generate_book_content_stream(self, book_id: int, book_params: Dict[str, Any]) -> Dict[str, Any]:
        """Genera el contenido del libro usando Claude AI con streaming SSE"""
        try:
            # Preparar el prompt con los detalles del libro
            messages = self._build_messages(book_params)
            
            # Variables para acumular respuesta y métricas
            full_content = []
            thinking_content = []
            chunk_count = 0
            total_chars = 0
            current_block_index = None
            block_type = None
            usage_data = {}
            
            # Crear stream con Claude API
            async with self.async_claude_client.messages.stream(
                model=CLAUDE_CONFIG['model'],
                max_tokens=CLAUDE_CONFIG['max_tokens'],
                temperature=CLAUDE_CONFIG['temperature'],
                messages=messages,
                thinking={
                    "type": "enabled",
                    "budget_tokens": CLAUDE_CONFIG['thinking_budget']
                },
                stream=True
            ) as stream:
                # Procesar eventos SSE conforme llegan
                async for event in stream:
                    # message_start - inicio del stream
                    if event.type == 'message_start':
                        await self._emit_progress(book_id, {
                            'progress': 0,
                            'message': 'Claude está comenzando a procesar tu libro...',
                            'status': 'started',
                            'event_type': 'message_start'
                        })
                    
                    # content_block_start - inicio de bloque de contenido
                    elif event.type == 'content_block_start':
                        current_block_index = event.index
                        block_type = event.content_block.type
                        
                        if block_type == 'thinking':
                            await self._emit_progress(book_id, {
                                'progress': 5,
                                'message': 'Claude está pensando en la estructura de tu libro...',
                                'status': 'thinking',
                                'event_type': 'thinking_start'
                            })
                        elif block_type == 'text':
                            await self._emit_progress(book_id, {
                                'progress': 15,
                                'message': 'Comenzando a escribir el contenido...',
                                'status': 'writing',
                                'event_type': 'writing_start'
                            })
                    
                    # content_block_delta - chunks de contenido
                    elif event.type == 'content_block_delta':
                        if event.delta.type == 'thinking_delta':
                            # Acumular contenido de pensamiento
                            thinking_chunk = event.delta.thinking
                            thinking_content.append(thinking_chunk)
                            
                            # Actualizar progreso ocasionalmente
                            if len(thinking_content) % 10 == 0:
                                await self._emit_progress(book_id, {
                                    'progress': min(10, 5 + len(thinking_content) // 20),
                                    'message': 'Analizando estructura y contenido...',
                                    'status': 'thinking',
                                    'thinking_preview': thinking_chunk[:100] + '...'
                                })
                        
                        elif event.delta.type == 'text_delta':
                            # Acumular texto del libro
                            chunk_text = event.delta.text
                            full_content.append(chunk_text)
                            chunk_count += 1
                            total_chars += len(chunk_text)
                            
                            # Calcular progreso basado en páginas objetivo
                            pages_written = total_chars / 2000  # ~2000 chars por página
                            target_pages = book_params.get('page_count', 50)
                            progress = min(90, 15 + int((pages_written / target_pages) * 75))
                            
                            # Actualizar progreso cada 50 chunks o 2000 caracteres
                            if chunk_count % 50 == 0 or total_chars % 2000 == 0:
                                await self._emit_progress(book_id, {
                                    'progress': progress,
                                    'message': f'Escribiendo... Página {int(pages_written)} de ~{target_pages}',
                                    'status': 'writing',
                                    'stats': {
                                        'chunks_received': chunk_count,
                                        'total_characters': total_chars,
                                        'estimated_pages': int(pages_written),
                                        'words_written': int(total_chars / 5)  # Estimación de palabras
                                    }
                                })
                        
                        elif event.delta.type == 'signature_delta':
                            # Firma de verificación para thinking blocks
                            logger.debug(f"Signature received: {event.delta.signature[:20]}...")
                    
                    # content_block_stop - fin de bloque
                    elif event.type == 'content_block_stop':
                        if block_type == 'thinking':
                            await self._emit_progress(book_id, {
                                'progress': 15,
                                'message': 'Análisis completado, comenzando a escribir...',
                                'status': 'thinking_complete'
                            })
                        elif block_type == 'text':
                            # Progreso al 90% cuando termina de escribir
                            await self._emit_progress(book_id, {
                                'progress': 90,
                                'message': 'Contenido completado, finalizando...',
                                'status': 'writing_complete'
                            })
                    
                    # message_delta - actualizaciones de uso (tokens acumulativos)
                    elif event.type == 'message_delta':
                        if hasattr(event, 'usage'):
                            usage_data = {
                                'output_tokens': event.usage.output_tokens,
                                'stop_reason': event.delta.stop_reason if hasattr(event.delta, 'stop_reason') else None
                            }
                    
                    # ping events - mantener conexión viva
                    elif event.type == 'ping':
                        logger.debug("Ping received - connection alive")
                    
                    # error events - manejar errores del stream
                    elif event.type == 'error':
                        error_msg = f"Stream error: {event.error.type} - {event.error.message}"
                        logger.error(error_msg)
                        
                        # Manejar overloaded_error específicamente
                        if event.error.type == 'overloaded_error':
                            await self._emit_progress(book_id, {
                                'progress': -1,
                                'message': 'El servicio está sobrecargado, reintentando...',
                                'status': 'error',
                                'error_type': 'overloaded'
                            })
                            raise Exception("Service overloaded, will retry")
                        else:
                            raise Exception(error_msg)
                
                # Obtener mensaje final con métricas completas
                final_message = await stream.get_final_message()
            
            # Procesar respuesta completa
            complete_content = ''.join(full_content)
            complete_thinking = ''.join(thinking_content)
            
            # Calcular métricas finales
            final_pages = int(total_chars / 2000)
            final_words = int(total_chars / 5)
            
            return {
                'content': complete_content,
                'thinking': complete_thinking,
                'usage': {
                    'prompt_tokens': final_message.usage.input_tokens,
                    'completion_tokens': final_message.usage.output_tokens,
                    'thinking_tokens': getattr(final_message.usage, 'thinking_tokens', 0),
                    'total_tokens': final_message.usage.input_tokens + final_message.usage.output_tokens
                },
                'model': final_message.model,
                'stop_reason': final_message.stop_reason,
                'streaming_stats': {
                    'total_chunks': chunk_count,
                    'total_characters': total_chars,
                    'estimated_pages': final_pages,
                    'estimated_words': final_words,
                    'thinking_length': len(complete_thinking)
                }
            }
            
        except anthropic.APIError as e:
            logger.error(f"Claude API error: {str(e)}")
            # Emitir error al usuario
            await self._emit_progress(book_id, {
                'progress': -1,
                'message': 'Error en la API de Claude',
                'status': 'error',
                'error_details': str(e)
            })
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating book: {str(e)}")
            await self._emit_progress(book_id, {
                'progress': -1,
                'message': 'Error inesperado generando el libro',
                'status': 'error',
                'error_details': str(e)
            })
            raise
    
    def _build_messages(self, book_params: Dict[str, Any]) -> list:
        """Construye los mensajes para la API según el formato correcto"""
        system_prompt = self._build_system_prompt(book_params)
        user_prompt = self._build_user_prompt(book_params)
        
        return [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    
    async def _emit_progress(self, book_id: int, progress_data: Dict[str, Any]):
        """Emite progreso via WebSocket de manera asíncrona"""
        book = await self._get_book_async(book_id)
        if book:
            # Agregar timestamp al evento
            progress_data['timestamp'] = datetime.utcnow().isoformat()
            progress_data['book_id'] = book_id
            
            socketio.emit('book_progress', progress_data, room=f'user_{book.user_id}')
    
    async def _get_book_async(self, book_id: int):
        """Obtiene libro de manera asíncrona"""
        # En producción, usar SQLAlchemy async
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, BookGeneration.query.get, book_id)
    
    def _build_system_prompt(self, book_params: Dict[str, Any]) -> str:
        """Construye el prompt del sistema optimizado"""
        return f"""
        Eres un escritor profesional experto en crear libros de alta calidad.
        
        INSTRUCCIONES:
        - Genera un libro completo, coherente y profesional
        - Mantén consistencia en estilo y tono
        - Estructura clara con capítulos bien definidos
        - Contenido original y valioso
        - Formato: {book_params.get('format_size', 'Carta')}
        - Páginas objetivo: {book_params.get('page_count', 50)}
        - Idioma: {book_params.get('language', 'es')}
        
        OPTIMIZACIÓN:
        - Sé conciso pero completo
        - Evita repeticiones innecesarias
        - Mantén calidad profesional
        - Usa formato markdown para facilitar el procesamiento
        
        ESTRUCTURA PARA STREAMING:
        - Comienza con # Título del Libro
        - Sigue con ## Tabla de Contenidos
        - Escribe cada capítulo con ### Capítulo N: Título
        - Usa marcadores claros entre secciones
        - Mantén formato consistente para facilitar parsing
        """
    
    def _build_user_prompt(self, book_params: Dict[str, Any]) -> str:
        """Construye el prompt del usuario con los detalles del libro"""
        # Construir detalles del libro
        book_details = f"""
        Título: {book_params.get('title', 'Sin título')}
        Género: {book_params.get('genre', 'General')}
        Audiencia objetivo: {book_params.get('target_audience', 'General')}
        Tono: {book_params.get('tone', 'Profesional')}
        Temas principales: {book_params.get('key_topics', 'N/A')}
        Número de capítulos: {book_params.get('chapter_count', 10)}
        Estilo de escritura: {book_params.get('writing_style', 'Claro y conciso')}
        
        Instrucciones adicionales: {book_params.get('additional_instructions', 'N/A')}
        """
        
        includes = []
        if book_params.get('include_toc', True):
            includes.append("- Tabla de contenidos detallada al inicio")
        if book_params.get('include_introduction', True):
            includes.append("- Introducción atractiva que enganche al lector")
        if book_params.get('include_conclusion', True):
            includes.append("- Conclusión impactante que deje una impresión duradera")
        
        includes_text = "\n".join(includes) if includes else "N/A"
        
        return f"""
        Genera un libro completo basándote en los siguientes detalles:
        
        <book_details>
        {book_details}
        </book_details>
        
        El libro debe incluir:
        {includes_text}
        
        Estructura esperada en markdown:
        
        # {book_params.get('title', 'Título del Libro')}
        
        ## Tabla de Contenidos
        
        ## Introducción
        [Contenido de introducción si se solicitó]
        
        ### Capítulo 1: [Título del Capítulo]
        [Contenido sustancial del capítulo]
        
        ### Capítulo 2: [Título del Capítulo]
        [Contenido sustancial del capítulo]
        
        [... más capítulos según lo solicitado ...]
        
        ## Conclusión
        [Contenido de conclusión si se solicitó]
        
        IMPORTANTE:
        - Cada capítulo debe tener al menos 3-5 páginas de contenido real
        - Mantén coherencia narrativa entre capítulos
        - Usa subtítulos y secciones para mejor organización
        - El contenido debe ser profesional y bien investigado
        
        Genera el libro completo ahora, escribiendo de forma continua y fluida.
        """
    
    def estimate_generation_time(self, book_params: Dict[str, Any]) -> int:
        """Estima el tiempo de generación basado en parámetros"""
        # Base de cálculo según páginas
        base_time = book_params.get('page_count', 50) * 0.3
        
        # Factor de complejidad según el género
        complexity_factors = {
            'fiction': 1.2,
            'technical': 1.5,
            'academic': 1.8,
            'children': 0.8,
            'general': 1.0
        }
        genre = book_params.get('genre', 'general').lower()
        complexity = complexity_factors.get(genre, 1.0)
        
        # Factor de carga del sistema
        queue_factor = self.get_current_queue_load()
        
        # Tiempo estimado en segundos
        estimated_seconds = int(base_time * complexity * queue_factor)
        
        return estimated_seconds
    
    def get_current_queue_load(self) -> float:
        """Obtiene el factor de carga actual del sistema"""
        # Contar tareas en cola
        pending_tasks = BookGeneration.query.filter_by(status='queued').count()
        processing_tasks = BookGeneration.query.filter_by(status='processing').count()
        
        # Factor basado en carga
        if pending_tasks + processing_tasks < 5:
            return 1.0  # Carga baja
        elif pending_tasks + processing_tasks < 20:
            return 1.5  # Carga media
        else:
            return 2.0  # Carga alta
    
    def get_queue_position(self, book_id: int) -> int:
        """Obtiene la posición en la cola de un libro"""
        # Contar libros anteriores en cola
        position = BookGeneration.query.filter(
            BookGeneration.status.in_(['queued', 'processing']),
            BookGeneration.id < book_id
        ).count()
        
        return position + 1

# Tarea asíncrona de Celery
@celery.task(bind=True, max_retries=3)
def generate_book_async(self, book_id: int):
    """Tarea asíncrona para generar un libro con streaming SSE"""
    try:
        book = BookGeneration.query.get(book_id)
        if not book:
            raise ValueError(f"Book {book_id} not found")
        
        # Actualizar estado
        book.status = 'processing'
        book.started_at = datetime.utcnow()
        db.session.commit()
        
        # Notificar inicio via WebSocket
        socketio.emit('book_progress', {
            'book_id': book_id,
            'status': 'processing',
            'progress': 0,
            'message': 'Iniciando generación de tu libro...',
            'timestamp': datetime.utcnow().isoformat()
        }, room=f'user_{book.user_id}')
        
        # Crear event loop para async dentro de Celery
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Generar contenido con Claude usando streaming
            service = BookGenerationService()
            result = loop.run_until_complete(
                service.generate_book_content_stream(book_id, book.parameters)
            )
            
            # Actualizar progreso - contenido generado
            socketio.emit('book_progress', {
                'book_id': book_id,
                'progress': 92,
                'message': 'Procesando y formateando tu libro...',
                'status': 'formatting',
                'timestamp': datetime.utcnow().isoformat()
            }, room=f'user_{book.user_id}')
            
            # Guardar thinking content si existe
            if result.get('thinking'):
                book.thinking_content = result['thinking']
                book.thinking_length = result['streaming_stats']['thinking_length']
            
            # Crear archivos en diferentes formatos
            pdf_service = PDFGenerationService()
            files = pdf_service.create_book_files(
                content=result['content'],
                metadata={
                    'title': book.title,
                    'author': book.user.full_name,
                    'created_at': book.created_at,
                    'total_pages': result['streaming_stats']['estimated_pages'],
                    'total_words': result['streaming_stats']['estimated_words']
                },
                formats=['pdf', 'epub', 'docx']
            )
            
            # Actualizar libro con resultados
            book.status = 'completed'
            book.completed_at = datetime.utcnow()
            book.file_paths = files
            book.prompt_tokens = result['usage']['prompt_tokens']
            book.completion_tokens = result['usage']['completion_tokens']
            book.thinking_tokens = result['usage']['thinking_tokens']
            book.total_tokens = result['usage']['total_tokens']
            book.streaming_stats = result['streaming_stats']
            book.final_pages = result['streaming_stats']['estimated_pages']
            book.final_words = result['streaming_stats']['estimated_words']
            
            # Calcular costo estimado (ejemplo: $0.015 por 1K tokens de entrada, $0.075 por 1K de salida)
            input_cost = (book.prompt_tokens / 1000) * 0.015
            output_cost = (book.completion_tokens / 1000) * 0.075
            thinking_cost = (book.thinking_tokens / 1000) * 0.015  # Mismo precio que input
            book.estimated_cost = round(input_cost + output_cost + thinking_cost, 4)
            
            db.session.commit()
            
            # Notificar finalización con celebración
            socketio.emit('book_completed', {
                'book_id': book_id,
                'title': book.title,
                'coverUrl': files.get('cover_url'),
                'downloadUrls': files,
                'stats': {
                    'pages': result['streaming_stats']['estimated_pages'],
                    'words': result['streaming_stats']['estimated_words'],
                    'characters': result['streaming_stats']['total_characters'],
                    'generation_time': round((book.completed_at - book.started_at).total_seconds(), 1),
                    'chunks_processed': result['streaming_stats']['total_chunks']
                },
                'message': '¡Tu libro está listo! 🎉',
                'timestamp': datetime.utcnow().isoformat()
            }, room=f'user_{book.user_id}')
            
            # Enviar email con libro adjunto
            send_book_ready_email(book.user, book)
            
            # Log exitoso con métricas detalladas
            log_event('book_generated', {
                'book_id': book_id,
                'user_id': book.user_id,
                'tokens_used': book.total_tokens,
                'thinking_tokens': book.thinking_tokens,
                'cost': book.estimated_cost,
                'generation_time': (book.completed_at - book.started_at).total_seconds(),
                'streaming_chunks': result['streaming_stats']['total_chunks'],
                'final_pages': book.final_pages,
                'final_words': book.final_words
            })
            
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"Error generating book {book_id}: {str(e)}")
        
        # Actualizar estado de error
        book = BookGeneration.query.get(book_id)
        if book:
            book.status = 'failed'
            book.error_message = str(e)
            book.completed_at = datetime.utcnow()
            db.session.commit()
        
        # Determinar si es un error recuperable
        is_overloaded = 'overloaded' in str(e).lower()
        retry_delay = 120 if is_overloaded else 60  # Más tiempo si está sobrecargado
        
        # Notificar error al usuario
        socketio.emit('book_error', {
            'book_id': book_id,
            'message': 'Hubo un error generando tu libro. Reintentando automáticamente...' if self.request.retries < self.max_retries else 'Error al generar el libro. Por favor intenta nuevamente.',
            'error_type': 'overloaded' if is_overloaded else 'general',
            'will_retry': self.request.retries < self.max_retries,
            'timestamp': datetime.utcnow().isoformat()
        }, room=f'user_{book.user_id}')
        
        # Reintentar si es posible
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=retry_delay * (self.request.retries + 1))

# Cliente JavaScript mejorado para manejar streaming SSE
"""
// Frontend: Manejo avanzado de eventos SSE de streaming
class BookGenerationTracker {
    constructor(bookId) {
        this.bookId = bookId;
        this.socket = io('/books');
        this.progressBar = document.getElementById('progress-bar');
        this.statusText = document.getElementById('status-text');
        this.streamingStats = document.getElementById('streaming-stats');
        this.currentStats = {
            chunks: 0,
            pages: 0,
            words: 0,
            startTime: Date.now()
        };
        
        this.setupListeners();
    }
    
    setupListeners() {
        // Escuchar todos los eventos de progreso
        this.socket.on('book_progress', (data) => {
            if (data.book_id === this.bookId) {
                this.handleProgressEvent(data);
            }
        });
        
        // Evento de completado
        this.socket.on('book_completed', (data) => {
            if (data.book_id === this.bookId) {
                this.onComplete(data);
            }
        });
        
        // Evento de error
        this.socket.on('book_error', (data) => {
            if (data.book_id === this.bookId) {
                this.onError(data);
            }
        });
    }
    
    handleProgressEvent(data) {
        // Actualizar barra de progreso con animación suave
        this.animateProgress(data.progress);
        
        // Actualizar mensaje de estado
        this.statusText.textContent = data.message;
        
        // Manejar diferentes tipos de eventos
        switch(data.event_type) {
            case 'message_start':
                this.onMessageStart();
                break;
            
            case 'thinking_start':
                this.onThinkingStart();
                break;
            
            case 'writing_start':
                this.onWritingStart();
                break;
            
            case 'thinking_complete':
                this.showNotification('Análisis completado', 'info');
                break;
            
            case 'writing_complete':
                this.showNotification('Contenido listo', 'success');
                break;
        }
        
        // Actualizar estadísticas si están disponibles
        if (data.stats) {
            this.updateStreamingStats(data.stats);
        }
        
        // Mostrar preview de thinking si está disponible
        if (data.thinking_preview) {
            this.showThinkingPreview(data.thinking_preview);
        }
    }
    
    animateProgress(targetProgress) {
        // Animación suave de la barra de progreso
        const currentWidth = parseFloat(this.progressBar.style.width) || 0;
        const duration = 500; // ms
        const steps = 30;
        const increment = (targetProgress - currentWidth) / steps;
        let step = 0;
        
        const animation = setInterval(() => {
            step++;
            const newWidth = currentWidth + (increment * step);
            this.progressBar.style.width = `${newWidth}%`;
            
            if (step >= steps) {
                clearInterval(animation);
                this.progressBar.style.width = `${targetProgress}%`;
            }
        }, duration / steps);
    }
    
    onThinkingStart() {
        // Animación especial para thinking
        this.progressBar.classList.add('thinking-animation');
        this.addVisualEffect('brain-wave');
    }
    
    onWritingStart() {
        // Cambiar a animación de escritura
        this.progressBar.classList.remove('thinking-animation');
        this.progressBar.classList.add('writing-animation');
        this.addVisualEffect('typewriter');
    }
    
    updateStreamingStats(stats) {
        this.currentStats = { ...this.currentStats, ...stats };
        
        // Calcular velocidad de escritura
        const elapsedSeconds = (Date.now() - this.currentStats.startTime) / 1000;
        const wordsPerMinute = Math.round((stats.words_written / elapsedSeconds) * 60);
        
        // Actualizar display con animación
        this.streamingStats.innerHTML = `
            <div class="stats-grid animate-fade-in">
                <div class="stat-item">
                    <i class="icon-file-text"></i>
                    <span class="stat-value counter" data-target="${stats.estimated_pages}">
                        ${stats.estimated_pages}
                    </span>
                    <span class="stat-label">páginas</span>
                </div>
                <div class="stat-item">
                    <i class="icon-edit-3"></i>
                    <span class="stat-value counter" data-target="${stats.words_written}">
                        ${stats.words_written.toLocaleString()}
                    </span>
                    <span class="stat-label">palabras</span>
                </div>
                <div class="stat-item">
                    <i class="icon-zap"></i>
                    <span class="stat-value">${wordsPerMinute}</span>
                    <span class="stat-label">palabras/min</span>
                </div>
                <div class="stat-item">
                    <i class="icon-layers"></i>
                    <span class="stat-value">${stats.chunks_received}</span>
                    <span class="stat-label">fragmentos</span>
                </div>
            </div>
        `;
        
        // Animar contadores
        this.animateCounters();
    }
    
    showThinkingPreview(preview) {
        // Mostrar preview del proceso de thinking
        const thinkingBox = document.getElementById('thinking-preview');
        if (thinkingBox) {
            thinkingBox.innerHTML = `
                <div class="thinking-content">
                    <i class="icon-cpu animate-pulse"></i>
                    <p class="thinking-text">${preview}</p>
                </div>
            `;
            thinkingBox.classList.add('visible');
        }
    }
    
    onComplete(data) {
        // Ocultar thinking preview
        const thinkingBox = document.getElementById('thinking-preview');
        if (thinkingBox) {
            thinkingBox.classList.remove('visible');
        }
        
        // Animación de celebración
        this.progressBar.style.width = '100%';
        this.progressBar.classList.add('complete-animation');
        
        // Mostrar estadísticas finales con animación
        const completionStats = `
            <div class="completion-stats animate-scale-in">
                <h3 class="success-title">
                    <i class="icon-check-circle"></i>
                    ¡${data.title} está listo!
                </h3>
                <div class="final-stats">
                    <div class="stat-row">
                        <span>${data.stats.pages} páginas</span>
                        <span>•</span>
                        <span>${data.stats.words.toLocaleString()} palabras</span>
                    </div>
                    <div class="stat-row">
                        <span>${data.stats.generation_time}s de generación</span>
                        <span>•</span>
                        <span>${data.stats.chunks_processed} fragmentos procesados</span>
                    </div>
                </div>
                <div class="action-buttons">
                    <button onclick="readBook(${data.book_id})" class="btn-primary">
                        <i class="icon-book-open"></i> Leer ahora
                    </button>
                    <button onclick="downloadBook(${data.book_id})" class="btn-secondary">
                        <i class="icon-download"></i> Descargar
                    </button>
                </div>
            </div>
        `;
        
        this.streamingStats.innerHTML = completionStats;
        
        // Confetti y efectos de celebración
        this.celebrate();
        
        // Notificación del sistema
        this.showSystemNotification('¡Tu libro está listo!', data.title);
    }
    
    onError(data) {
        // Manejar diferentes tipos de errores
        this.progressBar.classList.add('error-animation');
        
        if (data.error_type === 'overloaded') {
            this.statusText.innerHTML = `
                <i class="icon-alert-circle"></i>
                El servicio está sobrecargado. 
                ${data.will_retry ? 'Reintentando automáticamente...' : 'Por favor intenta más tarde.'}
            `;
        } else {
            this.statusText.innerHTML = `
                <i class="icon-x-circle"></i>
                ${data.message}
            `;
        }
        
        if (!data.will_retry) {
            // Mostrar botón de reintentar
            this.showRetryButton();
        }
    }
    
    celebrate() {
        // Animación de confetti
        confetti({
            particleCount: 200,
            spread: 90,
            origin: { y: 0.6 },
            colors: ['#667eea', '#764ba2', '#f093fb', '#f5576c']
        });
        
        // Sonido de celebración (opcional)
        const audio = new Audio('/sounds/success.mp3');
        audio.play().catch(() => {}); // Silenciar error si autoplay está bloqueado
    }
    
    showSystemNotification(title, body) {
        // Notificación del navegador si tiene permisos
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: body,
                icon: '/img/book-icon.png',
                badge: '/img/badge.png'
            });
        }
    }
}

// CSS para animaciones
const streamingStyles = `
<style>
/* Animación de thinking */
@keyframes thinking-pulse {
    0%, 100% { 
        background-position: 0% 50%;
        opacity: 0.8;
    }
    50% { 
        background-position: 100% 50%;
        opacity: 1;
    }
}

.thinking-animation {
    background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
    background-size: 200% 100%;
    animation: thinking-pulse 2s ease-in-out infinite;
}

/* Animación de escritura */
@keyframes writing-flow {
    0% { transform: scaleX(0); }
    100% { transform: scaleX(1); }
}

.writing-animation {
    background: linear-gradient(90deg, #4CAF50, #8BC34A);
    transform-origin: left;
    animation: writing-flow 0.5s ease-out;
}

/* Animación de completado */
@keyframes complete-glow {
    0%, 100% { box-shadow: 0 0 5px rgba(76, 175, 80, 0.5); }
    50% { box-shadow: 0 0 20px rgba(76, 175, 80, 0.8); }
}

.complete-animation {
    animation: complete-glow 1s ease-in-out infinite;
}

/* Animación de error */
@keyframes error-shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

.error-animation {
    background: #f44336;
    animation: error-shake 0.5s ease-in-out;
}

/* Estadísticas animadas */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.stat-item {
    text-align: center;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    backdrop-filter: blur(10px);
}

.stat-value {
    font-size: 2rem;
    font-weight: bold;
    display: block;
    margin: 0.5rem 0;
}

/* Preview de thinking */
.thinking-content {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: rgba(102, 126, 234, 0.1);
    border-radius: 8px;
    margin: 1rem 0;
}

.thinking-text {
    font-style: italic;
    color: #666;
    margin: 0;
}

/* Animaciones de entrada */
@keyframes fade-in {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes scale-in {
    from { transform: scale(0.9); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}

.animate-fade-in {
    animation: fade-in 0.5s ease-out;
}

.animate-scale-in {
    animation: scale-in 0.5s ease-out;
}
</style>
`;
"""
```

### 4. Sistema de Logs y Monitoreo
```python
class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100))
    details = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20))  # success, error, warning
    error_message = db.Column(db.Text)

class BookGeneration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(200))
    parameters = db.Column(db.JSON)  # Todos los parámetros del libro
    prompt_tokens = db.Column(db.Integer)
    thinking_tokens = db.Column(db.Integer)
    completion_tokens = db.Column(db.Integer)
    total_cost = db.Column(db.Float)
    status = db.Column(db.String(20))  # pending, processing, completed, failed
    file_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
```

## 🎨 EXPERIENCIA DE USUARIO (UX/UI)

### Landing Page Atractiva
```html
<!-- Estructura de la landing page -->
<section class="hero-section">
    <!-- Hero con animación parallax -->
    <div class="animated-background">
        <canvas id="particle-canvas"></canvas> <!-- Partículas animadas -->
        <h1 class="text-6xl font-bold gradient-text animate-fade-in">
            Tu libro en minutos, no en meses
        </h1>
        <p class="text-xl mt-4 animate-slide-up">
            Transforma tus ideas en libros profesionales con IA
        </p>
        <button class="cta-button pulse-animation">
            Crear mi primer libro GRATIS
        </button>
    </div>
    
    <!-- Demo interactivo -->
    <div class="demo-section">
        <div class="book-preview-3d" id="book-demo">
            <!-- Three.js libro 3D que rota -->
        </div>
        <div class="demo-steps">
            <div class="step active" data-step="1">
                <span class="step-number">1</span>
                <p>Describe tu idea</p>
            </div>
            <div class="step" data-step="2">
                <span class="step-number">2</span>
                <p>Personaliza detalles</p>
            </div>
            <div class="step" data-step="3">
                <span class="step-number">3</span>
                <p>Recibe tu libro</p>
            </div>
        </div>
    </div>
    
    <!-- Estadísticas animadas -->
    <div class="stats-grid">
        <div class="stat-card" data-aos="fade-up">
            <span class="counter" data-target="1000">0</span>+
            <p>Libros creados</p>
        </div>
        <div class="stat-card" data-aos="fade-up" data-aos-delay="100">
            <span class="counter" data-target="90">0</span>%
            <p>Ahorro vs. ghostwriter</p>
        </div>
        <div class="stat-card" data-aos="fade-up" data-aos-delay="200">
            <span class="timer">15 min</span>
            <p>Tiempo promedio</p>
        </div>
    </div>
</section>

<!-- CSS con Tailwind + animaciones personalizadas -->
<style>
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-20px); }
}

@keyframes bookFlip {
    0% { transform: rotateY(0deg); }
    100% { transform: rotateY(360deg); }
}

.gradient-text {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.pulse-animation {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Efectos hover interactivos */
.book-card {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.book-card:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

/* Loading creativo durante generación */
.generating-animation {
    position: relative;
    width: 300px;
    height: 400px;
}

.generating-animation .page {
    position: absolute;
    width: 100%;
    height: 100%;
    background: white;
    border: 1px solid #e5e7eb;
    animation: pageWrite 2s infinite;
}

@keyframes pageWrite {
    0% { transform: translateX(0); opacity: 0; }
    50% { opacity: 1; }
    100% { transform: translateX(100px); opacity: 0; }
}
</style>

<!-- JavaScript para interactividad -->
<script>
// Partículas animadas en el hero
class ParticleAnimation {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.particles = [];
        this.init();
    }
    
    init() {
        // Crear red de partículas conectadas
        for(let i = 0; i < 100; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                radius: Math.random() * 2 + 1
            });
        }
        this.animate();
    }
    
    animate() {
        // Animación suave de partículas
        requestAnimationFrame(() => this.animate());
        // ... lógica de animación
    }
}

// Libro 3D con Three.js
class Book3D {
    constructor(container) {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, container.offsetWidth / container.offsetHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ alpha: true });
        this.createBook();
        this.animate();
    }
    
    createBook() {
        // Crear libro 3D con texturas dinámicas
        const geometry = new THREE.BoxGeometry(3, 4, 0.5);
        const materials = [
            new THREE.MeshBasicMaterial({ map: this.createCoverTexture() }),
            // ... más materiales
        ];
        this.book = new THREE.Mesh(geometry, materials);
        this.scene.add(this.book);
    }
    
    createCoverTexture() {
        // Canvas dinámico para portada
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        // ... dibujar portada dinámica
        return new THREE.CanvasTexture(canvas);
    }
}
</script>
```

### Dashboard Usuario Premium
```html
<!-- Dashboard con experiencia fluida -->
<div class="dashboard-container">
    <!-- Sidebar animado -->
    <aside class="sidebar slide-in">
        <div class="user-profile">
            <img src="" alt="" class="avatar pulse-on-hover">
            <h3 class="user-name">{{ user.name }}</h3>
            <div class="subscription-badge">{{ user.plan }}</div>
        </div>
        
        <nav class="nav-menu">
            <a href="#" class="nav-item active">
                <i class="icon-book"></i>
                <span>Mis Libros</span>
                <span class="badge">{{ books_count }}</span>
            </a>
            <!-- más items -->
        </nav>
    </aside>
    
    <!-- Contenido principal -->
    <main class="main-content">
        <!-- Wizard de creación -->
        <div class="book-wizard" v-if="creating">
            <div class="wizard-progress">
                <div class="progress-bar" :style="{width: progress + '%'}"></div>
            </div>
            
            <!-- Step 1: Información básica -->
            <div class="wizard-step" v-show="currentStep === 1">
                <h2 class="step-title animate-fade-in">
                    ¿Sobre qué quieres escribir?
                </h2>
                
                <div class="input-group">
                    <input 
                        type="text" 
                        v-model="bookData.title"
                        class="input-fancy"
                        placeholder="El título de tu obra maestra..."
                    >
                    <span class="input-hint">
                        Un buen título es memorable y describe la esencia del libro
                    </span>
                </div>
                
                <!-- Selector de género con cards visuales -->
                <div class="genre-grid">
                    <div 
                        v-for="genre in genres" 
                        :key="genre.id"
                        class="genre-card"
                        :class="{active: bookData.genre === genre.id}"
                        @click="selectGenre(genre.id)"
                    >
                        <i :class="genre.icon"></i>
                        <h3>{{ genre.name }}</h3>
                        <p>{{ genre.description }}</p>
                    </div>
                </div>
            </div>
            
            <!-- Step 2: Personalización -->
            <div class="wizard-step" v-show="currentStep === 2">
                <!-- Sliders interactivos para configuración -->
                <div class="config-section">
                    <label>Número de páginas</label>
                    <div class="slider-container">
                        <input 
                            type="range" 
                            v-model="bookData.pages"
                            :max="maxPages"
                            class="slider-fancy"
                        >
                        <div class="slider-value">{{ bookData.pages }}</div>
                    </div>
                </div>
                
                <!-- Preview en tiempo real -->
                <div class="live-preview">
                    <div class="preview-book">
                        <div class="preview-cover">
                            <h4>{{ bookData.title || 'Tu Libro' }}</h4>
                            <p>{{ bookData.pages }} páginas</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Step 3: Generación -->
            <div class="wizard-step" v-show="currentStep === 3">
                <div class="generation-status">
                    <!-- Animación creativa de generación -->
                    <div class="ai-brain-animation">
                        <svg><!-- SVG animado de cerebro/IA --></svg>
                    </div>
                    
                    <h2>Tu libro está cobrando vida...</h2>
                    <p class="status-text">{{ statusMessage }}</p>
                    
                    <!-- Progress con detalles -->
                    <div class="detailed-progress">
                        <div class="progress-item" :class="{completed: progress > 20}">
                            <i class="icon-check"></i>
                            <span>Analizando tu idea</span>
                        </div>
                        <div class="progress-item" :class="{completed: progress > 50}">
                            <i class="icon-check"></i>
                            <span>Creando estructura</span>
                        </div>
                        <div class="progress-item" :class="{completed: progress > 80}">
                            <i class="icon-check"></i>
                            <span>Escribiendo contenido</span>
                        </div>
                        <div class="progress-item" :class="{completed: progress > 95}">
                            <i class="icon-check"></i>
                            <span>Puliendo detalles</span>
                        </div>
                    </div>
                    
                    <!-- Tips mientras espera -->
                    <div class="waiting-tips">
                        <p class="tip animate-fade">
                            💡 {{ currentTip }}
                        </p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Biblioteca de libros -->
        <div class="books-library" v-else>
            <!-- Filtros avanzados -->
            <div class="filters-bar">
                <input 
                    type="search" 
                    placeholder="Buscar en tu biblioteca..."
                    class="search-input"
                >
                <div class="view-toggle">
                    <button @click="viewMode = 'grid'" :class="{active: viewMode === 'grid'}">
                        <i class="icon-grid"></i>
                    </button>
                    <button @click="viewMode = 'list'" :class="{active: viewMode === 'list'}">
                        <i class="icon-list"></i>
                    </button>
                </div>
            </div>
            
            <!-- Grid de libros con hover effects -->
            <div :class="['books-grid', viewMode]">
                <div 
                    v-for="book in books" 
                    :key="book.id"
                    class="book-item"
                    @click="openBook(book)"
                >
                    <div class="book-cover">
                        <img :src="book.cover" :alt="book.title">
                        <div class="book-overlay">
                            <button class="btn-read">
                                <i class="icon-eye"></i> Leer
                            </button>
                            <button class="btn-download">
                                <i class="icon-download"></i> Descargar
                            </button>
                        </div>
                    </div>
                    <h3 class="book-title">{{ book.title }}</h3>
                    <p class="book-meta">
                        {{ book.pages }} páginas • {{ book.created_at }}
                    </p>
                </div>
            </div>
        </div>
    </main>
</div>

<!-- Modal de lectura con page flip effect -->
<div class="book-reader-modal" v-if="readingBook">
    <div class="reader-container">
        <div class="book-flipper">
            <!-- Implementar turn.js o similar -->
        </div>
        <div class="reader-controls">
            <button @click="previousPage">
                <i class="icon-arrow-left"></i>
            </button>
            <span class="page-indicator">
                {{ currentPage }} / {{ totalPages }}
            </span>
            <button @click="nextPage">
                <i class="icon-arrow-right"></i>
            </button>
        </div>
    </div>
</div>
```

### Sistema de Notificaciones en Tiempo Real
```javascript
// WebSocket para actualizaciones instantáneas
class BookNotificationSystem {
    constructor() {
        this.socket = io('/books');
        this.setupListeners();
    }
    
    setupListeners() {
        this.socket.on('book_progress', (data) => {
            // Actualizar UI con progreso
            this.updateProgress(data.bookId, data.progress);
            
            // Mostrar notificación suave
            this.showNotification({
                type: 'info',
                message: data.message,
                icon: 'book-open'
            });
        });
        
        this.socket.on('book_completed', (data) => {
            // Animación de celebración
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 }
            });
            
            // Notificación con preview
            this.showBookReadyNotification(data);
        });
    }
    
    showBookReadyNotification(bookData) {
        // Notificación personalizada con miniatura del libro
        const notification = document.createElement('div');
        notification.className = 'notification-card book-ready animate-slide-in';
        notification.innerHTML = `
            <div class="notification-content">
                <div class="book-thumbnail">
                    <img src="${bookData.coverUrl}" alt="">
                </div>
                <div class="notification-text">
                    <h4>¡Tu libro está listo!</h4>
                    <p>${bookData.title}</p>
                    <div class="notification-actions">
                        <button onclick="readBook(${bookData.id})">Leer ahora</button>
                        <button onclick="downloadBook(${bookData.id})">Descargar</button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(notification);
    }
}
```

## 🔐 SEGURIDAD Y CONTROL DE ACCESO

```python
# Decoradores de acceso
def require_subscription(allowed_plans=['free', 'starter', 'pro', 'business', 'enterprise']):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            if current_user.subscription_type not in allowed_plans:
                flash('Necesitas actualizar tu plan para acceder a esta función', 'warning')
                return redirect(url_for('billing.upgrade'))
            
            # Verificar límites mensuales
            if current_user.books_used_this_month >= get_plan_limit(current_user.subscription_type):
                flash('Has alcanzado el límite mensual de libros', 'error')
                return redirect(url_for('billing.upgrade'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rate limiting
from flask_limiter import Limiter
limiter = Limiter(
    app,
    key_func=lambda: current_user.id if current_user.is_authenticated else get_remote_address(),
    storage_uri="redis://localhost:6379"
)

@limiter.limit("5 per minute")
@app.route('/api/generate-book', methods=['POST'])
def generate_book():
    pass
```

## 💳 INTEGRACIÓN DE PAGOS

```python
# PayPal + MercadoPago
class PaymentService:
    def __init__(self):
        self.paypal_client = PayPalClient(
            client_id=os.getenv('PAYPAL_CLIENT_ID'),
            client_secret=os.getenv('PAYPAL_CLIENT_SECRET')
        )
        self.mp_client = mercadopago.SDK(os.getenv('MP_ACCESS_TOKEN'))
    
    def create_subscription(self, user, plan, payment_method='paypal'):
        if payment_method == 'paypal':
            return self._create_paypal_subscription(user, plan)
        elif payment_method == 'mercadopago':
            return self._create_mp_subscription(user, plan)
    
    def process_webhook(self, provider, data):
        # Verificar webhook signature
        # Actualizar estado de suscripción
        # Registrar en logs
        pass
```

## 🚀 FASES DE DESARROLLO

### FASE 1: MVP COMPLETO
**Filosofía**: Experiencia premium desde el día 1, todo asíncrono, preparado para escalar

#### 1.1 Infraestructura y Base
- **Setup completo con Docker**
  - Web app (Flask + Gunicorn)
  - PostgreSQL con todas las tablas
  - Redis para caché y queues
  - Celery workers
  - Nginx con SSL
- **Modelos de datos completos**
- **Sistema de logs estructurado**
- **Variables de entorno configurables**

#### 1.2 Sistema de Generación Asíncrono
- **Queue system con Celery desde el inicio**
  ```python
  @celery.task(bind=True, max_retries=3)
  def generate_book_async(self, book_id):
      try:
          book = BookGeneration.query.get(book_id)
          book.status = 'processing'
          db.session.commit()
          
          # Generar con Claude
          result = claude_service.generate_book(book.parameters)
          
          # Guardar libro
          pdf_path = pdf_service.create_book(result)
          
          book.status = 'completed'
          book.file_path = pdf_path
          book.tokens_used = result['usage']
          db.session.commit()
          
          # Notificar al usuario
          send_book_ready_email(book.user)
          send_websocket_notification(book.user_id, 'book_completed')
          
      except Exception as e:
          book.status = 'failed'
          book.error_message = str(e)
          db.session.commit()
          raise self.retry(exc=e, countdown=60)
  ```

- **WebSockets para actualizaciones en tiempo real**
- **Sistema de notificaciones (email + in-app)**
- **Progress tracking con porcentajes**

#### 1.3 UI/UX Premium
- **Landing page impactante**
  - Hero animado con Three.js o particles.js
  - Testimonios con carrusel
  - Demo interactivo del proceso
  - Pricing cards con animaciones
  - FAQ desplegable
  - Footer completo

- **Dashboard profesional**
  ```javascript
  // Componentes React para dashboard
  const BookGenerator = () => {
      const [step, setStep] = useState(1);
      const [bookData, setBookData] = useState({});
      const [generating, setGenerating] = useState(false);
      const [progress, setProgress] = useState(0);
      
      // Wizard multi-paso con validación
      // Animaciones entre pasos
      // Preview en tiempo real
      // Drag & drop para recursos adicionales
  };
  
  const BookLibrary = () => {
      // Grid/List view toggle
      // Filtros avanzados
      // Búsqueda instantánea
      // Preview modal con flip book effect
      // Bulk actions
  };
  ```

- **Formulario de generación tipo wizard**
  - Multi-paso con progress bar
  - Validación en tiempo real
  - Tooltips explicativos
  - Preview del libro mientras configura
  - Guardar borradores

- **Experiencia de espera optimizada**
  - Loading screen creativo (no spinner básico)
  - Tips mientras espera
  - Estimación de tiempo realista
  - Opción de notificación browser/email

#### 1.4 Sistema de Pagos Completo
- **Checkout profesional**
  - PayPal + MercadoPago integrados
  - Formulario de tarjeta embebido
  - Validación PCI compliant
  - Facturación automática

- **Gestión de suscripciones**
  - Portal self-service
  - Cambio de planes inmediato
  - Historial de pagos
  - Descarga de facturas PDF

- **Sistema de trials y ofertas**
  ```python
  class SubscriptionService:
      def create_trial(self, user, days=7):
          # Trial automático al registrarse
          subscription = Subscription(
              user_id=user.id,
              plan='pro_trial',
              status='active',
              trial_end=datetime.now() + timedelta(days=days),
              features=PLANS['pro']['features']
          )
          
          # Programar recordatorios
          schedule_trial_reminders(user, subscription)
          
          return subscription
  ```

#### 1.5 Features Premium del MVP
- **Editor de portadas con IA**
  - Templates prediseñados
  - Generación con DALL-E o Stable Diffusion
  - Editor básico (texto, colores)

- **Formatos múltiples**
  - PDF optimizado para impresión
  - EPUB para e-readers
  - DOCX editable
  - Vista web compartible

- **Analytics para usuarios**
  - Palabras totales generadas
  - Tiempo promedio de generación
  - Géneros más usados
  - Gráficas de uso mensual

- **Sistema de templates**
  - Templates por género
  - Guardar configuraciones propias
  - Compartir templates (marketplace futuro)

### FASE 2: Panel Administrativo y Optimización

#### 2.1 Panel Admin Completo
- **Dashboard ejecutivo**
  - KPIs en tiempo real
  - Gráficas interactivas (Chart.js/D3.js)
  - Alertas configurables
  - Exportación de reportes

- **Gestión avanzada**
  - CRUD completo de usuarios
  - Editor de planes y precios
  - Sistema de cupones/descuentos
  - Gestión de contenido (CMS básico)
  - Editor de prompts con versioning

- **Herramientas de soporte**
  - Sistema de tickets integrado
  - Chat en vivo (preparado para futuro)
  - Base de conocimientos

#### 2.2 Optimización y Performance
- **Optimización de costos**
  - A/B testing de prompts
  - Caché inteligente de respuestas similares
  - Compresión de respuestas

- **Performance**
  - CDN para assets (Cloudflare)
  - Lazy loading agresivo
  - Service workers para offline
  - Optimización de imágenes

- **Seguridad reforzada**
  - 2FA opcional
  - Logs de auditoría
  - Backup automático
  - Rate limiting adaptativo

### FASE 3: Features Avanzadas y Escala

#### 3.1 Features de Retención
- **Colaboración**
  - Compartir libros para revisión
  - Comentarios en libros
  - Co-autoría (futuro)

- **Marketplace de recursos**
  - Vender/comprar templates
  - Portadas premium
  - Servicios de edición

- **API para desarrolladores**
  - API REST documentada
  - Webhooks para eventos
  - SDK Python/JS

#### 3.2 Preparación para Escala
- **Infraestructura**
  - Auto-scaling configurado
  - Multi-region ready
  - Disaster recovery plan

- **Internacionalización completa**
  - Soporte para 5+ idiomas
  - Monedas locales
  - Contenido localizado

- **Growth features**
  - Programa de referidos
  - Affiliate system
  - Email marketing automation

## 🐳 CONFIGURACIÓN DOCKER

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=${FLASK_ENV}
      - DATABASE_URL=postgresql://user:pass@db:5432/buko_ai
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./app:/app
      - ./storage:/storage
    command: ./scripts/start-${FLASK_ENV}.sh

  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=buko_ai
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery:
    build: .
    command: celery -A app.celery worker --loglevel=info
    depends_on:
      - redis
      - db

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

volumes:
  postgres_data:
```

## 📊 MÓDULO DE MÉTRICAS DE NEGOCIO

```python
class BusinessMetrics:
    def __init__(self):
        self.metrics = {
            'mrr': self.calculate_mrr,
            'churn_rate': self.calculate_churn,
            'ltv': self.calculate_ltv,
            'cac': self.calculate_cac,
            'conversion_rate': self.calculate_conversion
        }
    
    def get_dashboard_data(self):
        return {
            'revenue': {
                'mrr': self.calculate_mrr(),
                'arr': self.calculate_mrr() * 12,
                'growth': self.calculate_growth_rate()
            },
            'users': {
                'total': User.query.count(),
                'active': User.query.filter_by(is_active=True).count(),
                'by_plan': self.users_by_plan()
            },
            'books': {
                'total_generated': BookGeneration.query.count(),
                'this_month': self.books_this_month(),
                'avg_pages': self.average_pages(),
                'token_cost': self.total_token_cost()
            }
        }
```

## 🔧 VARIABLES DE ENTORNO

```bash
# .env.example
# Flask
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/buko_ai

# Claude AI
CLAUDE_API_KEY=your-claude-api-key
MAX_TOKENS=90000
THINKING_BUDGET=20000
DEFAULT_TEMPERATURE=1.0

# Payments
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-client-secret
MP_ACCESS_TOKEN=your-mercadopago-token

# Redis
REDIS_URL=redis://localhost:6379

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-password

# Business Config
MAX_PAGES_DEFAULT=200
DEFAULT_BOOK_PRICE=15
CURRENCY=USD

# Storage
UPLOAD_FOLDER=/storage/uploads
BOOKS_FOLDER=/storage/books
MAX_UPLOAD_SIZE=10485760
```

## 📝 SCRIPTS DE MANTENIMIENTO

```bash
#!/bin/bash
# scripts/start-development.sh
echo "Starting Buko AI in development mode..."

# Verificar entorno
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please configure it."
    exit 1
fi

# Migraciones
flask db upgrade

# Inicializar datos
python scripts/init_db.py

# Iniciar servidor
flask run --host=0.0.0.0 --port=5000

---

#!/bin/bash
# scripts/start-production.sh
echo "Starting Buko AI in production mode..."

# Migraciones
flask db upgrade

# Inicializar datos si es necesario
python scripts/init_db.py --production

# Iniciar Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📚 DOCUMENTACIÓN REQUERIDA

### Para cada módulo crear en /docs:
1. **setup.md** - Guía de instalación paso a paso
2. **architecture.md** - Arquitectura y decisiones técnicas
3. **api.md** - Documentación de endpoints
4. **deployment.md** - Guía de despliegue en VPS
5. **admin-guide.md** - Manual del administrador
6. **troubleshooting.md** - Solución de problemas comunes

## 🎯 ENTREGABLES ESPERADOS

1. **Código fuente completo** organizado por módulos
2. **Documentación técnica** estilo "for dummies"
3. **Scripts de deployment** para Docker
4. **Datos de prueba** y fixtures
5. **Tests unitarios** para funciones críticas
6. **Postman collection** para APIs
7. **Manual de usuario** con capturas de pantalla

## ⚡ OPTIMIZACIONES CLAVE

1. **Caché agresivo** para contenido estático
2. **Lazy loading** de componentes pesados
3. **Compresión** de respuestas (gzip)
4. **Minificación** de CSS/JS en producción
5. **Índices** optimizados en PostgreSQL
6. **Connection pooling** para base de datos
7. **Rate limiting** inteligente por usuario

## 🔍 CONSIDERACIONES FINALES

- Priorizar la experiencia del usuario sobre la complejidad técnica
- Mantener el código DRY y bien comentado
- Seguir las convenciones de Flask y PEP-8
- Implementar logging exhaustivo para debugging
- Preparar para escalar desde día 1
- Documentar cada decisión técnica importante

## 📋 BACKLOG COMPLETO DE DESARROLLO

### ÉPICA 1: CONFIGURACIÓN INICIAL Y ARQUITECTURA
**Objetivo**: Establecer la base técnica completa del proyecto

#### Sprint 0: Setup del Proyecto
```yaml
TAREAS:
  1. Inicialización del Proyecto:
     - Crear estructura de carpetas según arquitectura definida
     - Inicializar repositorio Git con .gitignore apropiado
     - Crear README.md completo con:
       * Descripción del proyecto y su propósito
       * Requisitos del sistema y dependencias
       * Instrucciones de instalación paso a paso
       * Guía de configuración de variables de entorno
       * Comandos para ejecutar en desarrollo y producción
       * Arquitectura del proyecto con diagrama
       * Guía de contribución y estándares de código
       * Enlaces a documentación adicional
       * Badges de estado (build, coverage, license)
     - Configurar pre-commit hooks para calidad de código
     - Crear archivo LICENSE (elegir licencia apropiada)
     - Crear CHANGELOG.md para tracking de versiones
     - Configurar .editorconfig para consistencia
     Entregable: Repositorio estructurado y documentado

  2. Configuración de Entorno:
     - Crear requirements.txt con todas las dependencias
     - Crear archivo .env.example con todas las variables
     - Configurar entornos: development, staging, production
     - Crear scripts de instalación automatizada
     Entregable: Setup reproducible en cualquier máquina

  3. Docker Configuration:
     - Crear Dockerfile para aplicación Flask
     - Crear docker-compose.yml con todos los servicios
     - Configurar volúmenes para persistencia
     - Crear scripts docker-entrypoint.sh
     Entregable: Aplicación ejecutable con docker-compose up

  4. Base de Datos:
     - Diseñar esquema completo de base de datos
     - Crear modelos SQLAlchemy para todas las tablas
     - Configurar Flask-Migrate
     - Crear script de inicialización con datos de prueba
     Entregable: Base de datos funcional con migraciones

  5. Configuración de Servicios:
     - Configurar Celery + Redis para tareas asíncronas
     - Configurar Nginx con SSL (Let's Encrypt)
     - Configurar logging estructurado
     - Configurar sistema de caché
     Entregable: Infraestructura de servicios operativa
```

### ÉPICA 2: SISTEMA DE AUTENTICACIÓN Y USUARIOS
**Objetivo**: Sistema completo de gestión de usuarios

#### Sprint 1: Autenticación Base
```yaml
TAREAS:
  1. Modelos de Usuario:
     - Crear modelo User con todos los campos requeridos
     - Implementar hashing seguro de contraseñas (bcrypt)
     - Crear modelo de sesiones
     - Implementar soft delete para usuarios
     Entregable: Modelos de usuario completos y seguros

  2. Sistema de Registro:
     - Crear formulario de registro con validación completa
     - Implementar verificación de email único
     - Crear flujo de activación por email
     - Implementar captcha para evitar bots
     Entregable: Registro funcional con verificación

  3. Sistema de Login:
     - Crear formulario de login responsive
     - Implementar remember me funcional
     - Configurar sesiones seguras
     - Implementar límite de intentos fallidos
     Entregable: Login seguro y user-friendly

  4. Recuperación de Contraseña:
     - Implementar flujo "Olvidé mi contraseña"
     - Crear tokens temporales seguros
     - Enviar emails con templates bonitos
     - Validar y actualizar contraseña
     Entregable: Recuperación de contraseña completa

  5. Dashboard de Usuario:
     - Crear layout base del dashboard
     - Implementar menú de navegación responsive
     - Crear página de perfil editable
     - Implementar cambio de contraseña
     Entregable: Dashboard funcional y atractivo
```

### ÉPICA 3: GENERADOR DE LIBROS CON IA
**Objetivo**: Sistema completo de generación de libros

#### Sprint 2: Integración Claude AI
```yaml
TAREAS:
  1. Servicio de Claude AI:
     - Implementar clase BookGenerationService completa
     - Configurar cliente async con streaming SSE
     - Implementar manejo de todos los eventos SSE
     - Crear sistema de retry con backoff exponencial
     Entregable: Servicio Claude funcionando con streaming

  2. Formulario de Generación:
     - Crear wizard multi-paso con React/Alpine.js
     - Implementar validación en tiempo real
     - Crear selector visual de géneros
     - Implementar preview dinámico del libro
     Entregable: Wizard UX premium funcionando

  3. Sistema de Colas:
     - Configurar Celery tasks para generación
     - Implementar prioridades por plan de suscripción
     - Crear sistema de monitoreo de cola
     - Implementar cancelación de tareas
     Entregable: Sistema asíncrono robusto

  4. Generación de Archivos:
     - Implementar generador de PDF con ReportLab
     - Crear generador de EPUB
     - Implementar exportador DOCX
     - Crear sistema de portadas automáticas
     Entregable: Libros en múltiples formatos

  5. Sistema de Progreso:
     - Implementar WebSockets con Socket.io
     - Crear actualizaciones granulares de progreso
     - Implementar animaciones según estado
     - Crear notificaciones del navegador
     Entregable: Tracking en tiempo real funcionando
```

### ÉPICA 4: LANDING PAGE Y EXPERIENCIA VISUAL
**Objetivo**: Crear una landing page que venda

#### Sprint 3: Frontend Premium
```yaml
TAREAS:
  1. Landing Page Hero:
     - Implementar hero con partículas animadas
     - Crear título con efecto gradiente animado
     - Implementar botón CTA con micro-interacciones
     - Crear animación de libro 3D con Three.js
     Entregable: Hero section impactante

  2. Secciones de Contenido:
     - Crear sección de beneficios con iconos animados
     - Implementar testimonios con carrusel
     - Crear comparación visual vs ghostwriters
     - Implementar FAQ con acordeón suave
     Entregable: Landing page completa y persuasiva

  3. Pricing Cards:
     - Crear cards de precios con hover effects
     - Implementar toggle mensual/anual
     - Destacar plan recomendado
     - Crear tabla comparativa de features
     Entregable: Sección de precios clara y atractiva

  4. Optimización Mobile:
     - Hacer todo 100% responsive
     - Optimizar animaciones para móvil
     - Implementar menú hamburguesa elegante
     - Testear en múltiples dispositivos
     Entregable: Experiencia mobile perfecta

  5. Performance:
     - Implementar lazy loading de imágenes
     - Minificar CSS/JS
     - Optimizar assets con WebP
     - Implementar Service Worker básico
     Entregable: PageSpeed score > 90
```

### ÉPICA 5: SISTEMA DE PAGOS Y SUSCRIPCIONES
**Objetivo**: Monetización completa y automatizada

#### Sprint 4: Integración de Pagos
```yaml
TAREAS:
  1. Modelos de Suscripción:
     - Crear modelo Subscription con estados
     - Implementar modelo Payment con historial
     - Crear modelo Invoice para facturas
     - Implementar sistema de créditos/límites
     Entregable: Estructura de datos de pagos completa

  2. Integración PayPal:
     - Implementar PayPal Checkout
     - Configurar webhooks de PayPal
     - Manejar suscripciones recurrentes
     - Implementar cancelaciones y reembolsos
     Entregable: PayPal 100% funcional

  3. Integración MercadoPago:
     - Implementar MercadoPago Checkout Pro
     - Configurar IPN/Webhooks
     - Manejar pagos en múltiples monedas
     - Implementar pagos con tarjeta
     Entregable: MercadoPago operativo

  4. Gestión de Planes:
     - Crear página de upgrade/downgrade
     - Implementar cambios de plan prorrateados
     - Crear sistema de trials automáticos
     - Implementar límites por plan
     Entregable: Gestión de planes completa

  5. Facturación:
     - Generar facturas PDF automáticas
     - Enviar facturas por email
     - Crear página de historial de pagos
     - Implementar descarga de facturas
     Entregable: Sistema de facturación automatizado
```

### ÉPICA 6: BIBLIOTECA Y GESTIÓN DE LIBROS
**Objetivo**: Experiencia completa de biblioteca digital

#### Sprint 5: Biblioteca de Usuario
```yaml
TAREAS:
  1. Vista de Biblioteca:
     - Crear grid/list view con toggle
     - Implementar filtros avanzados
     - Crear búsqueda en tiempo real
     - Implementar ordenamiento múltiple
     Entregable: Biblioteca con UX profesional

  2. Lector de Libros:
     - Implementar visor PDF con PDF.js
     - Crear lector EPUB con turn.js
     - Implementar marcadores y notas
     - Crear modo lectura nocturna
     Entregable: Lector inmersivo funcionando

  3. Gestión de Archivos:
     - Implementar descarga segura de archivos
     - Crear sistema de compartir temporal
     - Implementar eliminación con papelera
     - Crear respaldos automáticos
     Entregable: Gestión de archivos robusta

  4. Estadísticas de Usuario:
     - Crear dashboard con métricas personales
     - Implementar gráficas con Chart.js
     - Mostrar uso vs límites del plan
     - Crear historial de generaciones
     Entregable: Analytics personal completo

  5. Funciones Sociales:
     - Implementar sistema de favoritos
     - Crear colecciones organizables
     - Implementar compartir en redes
     - Crear sistema de reseñas internas
     Entregable: Features sociales básicas
```

### ÉPICA 7: PANEL ADMINISTRATIVO
**Objetivo**: Control total del negocio

#### Sprint 6: Admin Dashboard
```yaml
TAREAS:
  1. Dashboard Ejecutivo:
     - Crear vista de KPIs en tiempo real
     - Implementar gráficas de ingresos (MRR, ARR)
     - Crear mapas de calor de uso
     - Implementar alertas automáticas
     Entregable: Dashboard ejecutivo completo

  2. Gestión de Usuarios:
     - Crear CRUD completo de usuarios
     - Implementar búsqueda y filtros avanzados
     - Crear acciones en lote
     - Implementar exportación a CSV/Excel
     Entregable: Gestión de usuarios profesional

  3. Gestión de Suscripciones:
     - Ver/editar suscripciones activas
     - Implementar cancelaciones manuales
     - Crear sistema de créditos/ajustes
     - Implementar cupones de descuento
     Entregable: Control total de suscripciones

  4. Sistema de Contenido:
     - Editor de prompts con versionado
     - Gestión de templates de libros
     - Editor de emails transaccionales
     - Gestión de páginas de contenido
     Entregable: CMS básico integrado

  5. Herramientas de Soporte:
     - Sistema de tickets interno
     - Vista de logs en tiempo real
     - Herramientas de debugging
     - Sistema de anuncios a usuarios
     Entregable: Herramientas de soporte completas
```

### ÉPICA 8: OPTIMIZACIÓN Y ESCALABILIDAD
**Objetivo**: Preparar para crecimiento masivo

#### Sprint 7: Optimización
```yaml
TAREAS:
  1. Optimización de Base de Datos:
     - Crear índices optimizados
     - Implementar particionamiento de tablas grandes
     - Configurar connection pooling
     - Optimizar queries lentas
     Entregable: BD optimizada para escala

  2. Caché Inteligente:
     - Implementar caché de respuestas similares
     - Configurar Redis para sesiones
     - Crear caché de archivos generados
     - Implementar invalidación inteligente
     Entregable: Sistema de caché multicapa

  3. CDN y Assets:
     - Configurar Cloudflare CDN
     - Implementar versionado de assets
     - Optimizar imágenes automáticamente
     - Configurar caché headers correctos
     Entregable: Assets servidos globalmente rápido

  4. Monitoreo y Alertas:
     - Implementar APM con Sentry
     - Configurar métricas con Prometheus
     - Crear dashboards en Grafana
     - Configurar alertas automáticas
     Entregable: Observabilidad completa

  5. Seguridad Reforzada:
     - Implementar rate limiting adaptativo
     - Configurar WAF rules
     - Crear auditoría de seguridad
     - Implementar 2FA opcional
     Entregable: Seguridad nivel enterprise
```

### ÉPICA 9: FEATURES AVANZADAS Y GROWTH
**Objetivo**: Diferenciación y crecimiento viral

#### Sprint 8: Features Premium
```yaml
TAREAS:
  1. Editor de Portadas AI:
     - Integrar generación con DALL-E 3
     - Crear editor visual drag & drop
     - Implementar templates de portadas
     - Guardar diseños personalizados
     Entregable: Generador de portadas con IA

  2. Programa de Referidos:
     - Crear sistema de códigos únicos
     - Implementar tracking de referidos
     - Crear página de afiliados
     - Automatizar pagos de comisiones
     Entregable: Sistema de referidos viral

  3. API Pública:
     - Crear API REST documentada
     - Implementar autenticación OAuth2
     - Crear límites por plan
     - Generar documentación con Swagger
     Entregable: API lista para developers

  4. Integraciones:
     - Integrar con Google Docs
     - Conectar con WordPress
     - Integrar con Medium
     - Crear plugin de Chrome
     Entregable: Ecosistema de integraciones

  5. Mobile App PWA:
     - Convertir a Progressive Web App
     - Implementar offline reading
     - Crear push notifications
     - Optimizar para app stores
     Entregable: App móvil funcional
```

### ÉPICA 10: LANZAMIENTO Y POST-LANZAMIENTO
**Objetivo**: Lanzamiento exitoso y mejora continua

#### Sprint 9: Preparación para Lanzamiento
```yaml
TAREAS:
  1. Testing Completo:
     - Ejecutar suite de tests automatizados
     - Realizar pruebas de carga con Locust
     - Hacer pruebas de penetración básicas
     - Validar en múltiples navegadores
     Entregable: Aplicación testeada y estable

  2. Documentación Final:
     - Completar documentación técnica
     - Crear guías de usuario con screenshots
     - Grabar videos tutoriales
     - Preparar FAQs completas
     Entregable: Documentación profesional

  3. Preparación de Infraestructura:
     - Configurar backups automáticos
     - Preparar plan de disaster recovery
     - Configurar monitoreo 24/7
     - Crear runbooks de operación
     Entregable: Infraestructura production-ready

  4. Marketing y Lanzamiento:
     - Preparar landing de lanzamiento
     - Crear campaña de email
     - Preparar posts para redes sociales
     - Configurar analytics y conversiones
     Entregable: Lanzamiento preparado

  5. Post-Lanzamiento:
     - Monitorear métricas en tiempo real
     - Responder feedback inmediato
     - Hacer ajustes rápidos
     - Planear siguiente iteración
     Entregable: Lanzamiento exitoso
```

## 📊 MÉTRICAS DE ÉXITO POR FASE

```yaml
FASE 1 (MVP):
  - Setup completo: 100% tests pasando
  - Generación funcional: Optimizada para velocidad
  - UX Score: > 4.5/5 en pruebas de usuario
  - Pagos integrados: 0% errores en transacciones

FASE 2 (Admin):
  - Dashboard cargando: Rápido y eficiente
  - Datos en tiempo real: Baja latencia
  - Gestión eficiente: Mínimos clicks para tareas comunes

FASE 3 (Optimización):
  - Performance: PageSpeed > 90
  - Uptime: 99.9%
  - Escalabilidad: Soportar múltiples usuarios concurrentes
  - Seguridad: 0 vulnerabilidades críticas
```

## 🚀 ORDEN DE IMPLEMENTACIÓN RECOMENDADO

1. **Primera Etapa**: Épicas 1-2 (Base + Auth)
2. **Segunda Etapa**: Épicas 3-4 (Generador + Landing)
3. **Tercera Etapa**: Épicas 5-6 (Pagos + Biblioteca)
4. **Cuarta Etapa**: Épicas 7-8 (Admin + Optimización)
5. **Quinta Etapa**: Épicas 9-10 (Features + Lanzamiento)

## ⚡ DEFINICIÓN DE "HECHO" (DoD)

Para considerar una tarea completada:
- ✅ Código funcionando en desarrollo
- ✅ Tests unitarios escritos y pasando
- ✅ Documentación actualizada
- ✅ Code review aprobado
- ✅ Funciona en Docker
- ✅ Sin errores en logs
- ✅ Responsive en móvil
- ✅ Accesible (WCAG 2.1 AA)

## 🎯 ENTREGABLES CRÍTICOS POR SPRINT

Cada sprint debe entregar:
1. **Código fuente** funcionando y documentado
2. **Scripts SQL** de migración si aplica
3. **Documentación** actualizada en /docs
4. **Tests** automatizados
5. **Demo** grabado del feature
6. **Métricas** de performance

---

**IMPORTANTE**: Este backlog debe ejecutarse de manera incremental, asegurando que cada fase construye sobre la anterior. La IA debe generar código production-ready desde el inicio, no prototipos.