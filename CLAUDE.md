# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BukoAI is a professional AI-powered book generation platform built with Flask, optimized for 10,000 concurrent users. It uses Claude Sonnet 4 to transform ideas into complete books in multiple professional formats (PDF, EPUB, DOCX, MOBI, AZW3).

**Key Features:**
- Advanced AI book generation with thinking (63K tokens context)
- Approvable architecture system - users review before generation
- Multi-chunk system for extensive, coherent content
- Real-time WebSocket streaming with progress tracking
- Professional document generation stack (100% libre)
- Subscription system with PayPal/MercadoPago integration
- Scalable architecture supporting 10K concurrent users

## Common Development Commands

### Installation and Setup
```bash
# Complete installation
make install
# OR manually:
chmod +x scripts/install.sh && ./scripts/install.sh

# Development setup
cp .env.example .env  # Configure with your API keys
```

### Development Server
```bash
# Start development server (recommended)
make dev
# OR manually:
chmod +x scripts/start-dev.sh && ./scripts/start-dev.sh

# Alternative Flask run (basic)
source venv/bin/activate
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

### Production Server
```bash
make prod
# OR manually:
chmod +x scripts/start-prod.sh && ./scripts/start-prod.sh
```

### Database Operations
```bash
# Initialize migrations (first time only)
make db-init

# Create migration
make db-migrate MSG="description of changes"

# Apply migrations
make db-upgrade

# Seed development data
make db-seed
```

### Testing
```bash
# Run all tests
make test
# OR: pytest

# Test with coverage
pytest --cov=app

# Test specific file
pytest tests/test_book_generation.py

# 10K users system test (comprehensive)
./scripts/test_10k_users_system.sh

# System verification only
./scripts/test_10k_users_system.sh verify
```

### Code Quality
```bash
# Run linting
make lint

# Format code
make format

# Security check
make security-check
```

### Celery Operations (Background Tasks)
```bash
# Basic worker
celery -A app.celery worker --loglevel=info

# Optimized worker for high load
celery -A app.celery worker \
  --loglevel=info \
  --concurrency=8 \
  --prefetch-multiplier=4 \
  --max-tasks-per-child=20 \
  --queues=architecture_high,book_generation_normal,emails_low

# Monitor tasks
celery -A app.celery flower --port=5555
```

### Docker Operations
```bash
# Development with hot reload
docker-compose -f docker-compose.dev.yml up --build

# Standard development
docker-compose up --build

# Production
docker-compose -f docker-compose.prod.yml up -d

# 10K users testing environment
docker-compose -f docker-compose.test.yml up --build
```

## High-Level Architecture

### Core Architecture Pattern
The application implements a **hybrid microservices architecture** combining multiple design patterns:

- **Factory Pattern**: Flask app + Celery worker creation
- **Facade Pattern**: Claude AI service with 7 specialized components
- **Service Layer Pattern**: Independent, testable business services
- **Repository Pattern**: SQLAlchemy models with ORM abstraction
- **Task Queue Pattern**: Celery with prioritized queues
- **Circuit Breaker Pattern**: External API protection with auto-recovery

### System Layers
```
┌─────────────────────────────────────────┐
│ PRESENTATION LAYER                      │
│ Jinja2 Templates + Tailwind + Alpine.js│
│ WebSocket Real-time + REST API          │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ CONTROLLER LAYER                        │
│ Flask Blueprints: main, auth, books,    │
│ api, admin + Rate Limiting + Security   │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ SERVICE LAYER                           │
│ Claude AI Facade + Email + Cache +      │
│ PostProcessor + Circuit Breakers        │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ ASYNC TASK LAYER                        │
│ Celery: 8 Workers + Priority Queues +   │
│ Retry Logic + Real-time Progress        │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ PERSISTENCE LAYER                       │
│ PostgreSQL (50 conns) + Redis Cache +   │
│ File System Storage                     │
└─────────────────────────────────────────┘
```

### Key Components

#### `/app/__init__.py` - Application Factory
Central application factory implementing the Factory pattern. Creates Flask app with all extensions, Celery integration, and environment-specific configurations. Critical for understanding app initialization.

#### `/app/models/book_generation.py` - Core Domain Model
Main business domain model (458 lines). Implements state machine for book generation:
- States: QUEUED → ARCHITECTURE_REVIEW → PROCESSING → COMPLETED/FAILED
- Approvable architecture system with user feedback
- Automatic token/cost metrics calculation
- Real-time progress tracking

#### `/app/services/claude_service/` - Refactored AI Service
Complete Claude AI integration refactored into 7 specialized components:
- **claude_service_facade.py**: Unified interface maintaining backward compatibility
- **clients/claude_client.py**: API client with circuit breaker protection
- **generators/**: Architecture + content generation specialists
- **builders/**: Message construction and regeneration logic
- **config/**: Centralized configuration management

#### `/app/tasks/book_generation.py` - Main Async Task
Coordinates the complete book generation flow:
- Approvable architecture generation
- Multi-chunk content generation with coherence
- Real-time WebSocket progress streaming
- Robust retry with exponential backoff
- Circuit breaker integration

#### `/app/routes/books.py` - Book Management
CRUD operations for books including:
- Architecture generation and approval flow
- Professional eBook viewer with multiple formats
- Download system for all formats
- Regeneration with feedback
- Progress streaming

### Scalability Optimizations (10K Users)

#### Database (PostgreSQL)
- **Connection Pool**: 20 base + 30 overflow = 50 total connections
- **Query Optimization**: Indexes on frequent queries, connection pooling
- **Health Checks**: Automatic connection validation

#### Cache (Redis)
- **Multi-database usage**:
  - DB 0: Celery broker (task queues)
  - DB 1: Rate limiting
  - DB 2: Application cache (user data, statistics)
- **1000 concurrent clients** supported
- **Connection pooling** with keepalive optimization

#### Async Processing (Celery)
- **8 concurrent workers** per node
- **Prioritized queues**: architecture_high, book_generation_normal, emails_low
- **Smart timeouts**: 90min soft, 2h hard limits
- **Retry with jitter** to prevent thundering herd
- **Rate limiting per user** to prevent abuse

#### WebSocket Optimization
- **Optimized timeouts**: 120s ping timeout, 60s keepalive
- **100KB message buffer** for high-throughput streaming
- **Real-time progress streaming** with backpressure handling

### Professional Document Generation Stack

The system uses a completely libre (free) stack for document generation:
- **python-docx**: Professional Word documents
- **ReportLab**: Commercial-quality PDFs
- **WeasyPrint**: Advanced HTML-to-PDF with typography
- **EbookLib**: Standard EPUB generation
- **Calibre**: Kindle format conversion (MOBI/AZW3)
- **BeautifulSoup**: HTML/XML processing

**No commercial dependencies** - entire document generation pipeline is free and open source.

## Critical Integration Points

### Claude AI Integration
- **Model**: claude-sonnet-4-20250514
- **Context**: 63K tokens with thinking budget optimization
- **Features**: Thinking mode, multi-chunk generation, architecture approval
- **Protection**: Circuit breaker with auto-recovery, retry with exponential backoff
- **API Key**: Required in ANTHROPIC_API_KEY environment variable

### Payment Systems
- **PayPal**: Subscription management with webhooks
- **MercadoPago**: Latin American market support
- **Webhook Handling**: Automatic subscription updates with verification

### Email System
- **SMTP Integration**: Gmail/SendGrid support
- **Template System**: HTML + text templates with personalization
- **Async Processing**: Celery-based with retry logic

## File Structure Understanding

### Configuration (`/config/`)
Environment-based configuration with inheritance:
- `base.py`: Core optimizations for 10K users
- `development.py`: SQLite + debug settings
- `production.py`: PostgreSQL + performance optimizations
- `testing.py`: Isolated test environment

### Models (`/app/models/`)
SQLAlchemy models with modern 2.0+ patterns:
- `base.py`: Abstract base with UUID PKs, timestamps, utilities
- `book_generation.py`: Main domain model with state machine
- `user.py`: User management with subscription integration
- `subscription.py`: Payment system integration

### Services (`/app/services/`)
Business logic layer with specialized services:
- `claude_service/`: Refactored AI service with 7 components
- `email_service.py`: Email with templates and queuing
- `cache_service.py`: Advanced Redis cache management
- `book_postprocessor.py`: Multi-format document generation

### Tasks (`/app/tasks/`)
Celery async tasks optimized for high concurrency:
- `book_generation.py`: Main generation coordinator
- `email_tasks.py`: Async email sending
- `cleanup_tasks.py`: Automatic file cleanup
- `payment_tasks.py`: Payment processing

### Routes (`/app/routes/`)
Flask Blueprints organized by functionality:
- `main.py`: Dashboard and public pages
- `auth.py`: Authentication system
- `books.py`: Book CRUD and generation
- `api.py`: REST API endpoints
- `admin.py`: Administrative panel
- `websocket.py`: Real-time WebSocket handlers

### Static Assets (`/app/static/`)
- `css/main.css`: Tailwind CSS compilation
- `js/`: Alpine.js + Three.js integration
- `generated/`: Temporary file storage (PDF, EPUB, DOCX)
- `covers/`: Generated book covers

## Environment Variables

### Required Variables
```bash
# Claude AI (Critical)
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-sonnet-4-20250514
CLAUDE_MAX_TOKENS=64000
CLAUDE_THINKING_BUDGET=63999

# Database (Optimized for 10K users)
DATABASE_URL=postgresql://user:pass@host/db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30

# Redis (High concurrency)
REDIS_URL=redis://localhost:6379/0
CACHE_REDIS_URL=redis://localhost:6379/2
CACHE_REDIS_MAX_CONNECTIONS=50

# Celery (Optimized)
CELERY_WORKER_CONCURRENCY=8
CELERY_TASK_SOFT_TIME_LIMIT=5400
CELERY_TASK_TIME_LIMIT=7200

# WebSocket (Optimized)
SOCKETIO_PING_TIMEOUT=120
SOCKETIO_PING_INTERVAL=60
```

## Key Workflows

### Book Generation Flow
1. User creates book request → `POST /books/generate`
2. Architecture generation → Claude AI with thinking mode
3. User approval → Architecture review interface
4. Content generation → Multi-chunk processing with coherence
5. Document processing → Multi-format generation (PDF, EPUB, DOCX, etc.)
6. Real-time updates → WebSocket progress streaming

### Professional eBook Generation
1. Access viewer → `/books/book/<id>/professional-ebook-viewer`
2. Configure format → Font, margins, style presets
3. Preview generation → 5-page preview with selected config
4. Full document generation → Complete eBook in chosen format
5. Download → Direct download with proper metadata

### System Architecture Verification
```bash
# Comprehensive system check
./scripts/test_10k_users_system.sh

# Verification only (no containers)
./scripts/test_10k_users_system.sh verify
```

## Performance Characteristics

### Optimized Metrics
- **Architecture Generation**: 15-25 minutes (60% improvement over previous)
- **Complete Book**: 45-90 minutes (55% improvement over previous)
- **Concurrent Throughput**: 8 books simultaneously per node
- **User Capacity**: 10,000 concurrent users supported
- **Reliability**: 99.5% uptime with automatic retry

### Monitoring
- **Structured Logging**: JSON format in `logs/structured.jsonl`
- **Real-time Metrics**: Admin dashboard with live statistics
- **Queue Monitoring**: Flower dashboard at `:5555`
- **System Health**: Automatic health checks and circuit breakers

## Development Notes

### Critical Files to Understand
- Read `/docs/Arquitecture.md` for comprehensive architectural analysis
- Review `/app/services/claude_service/claude_service_facade.py` for AI integration
- Study `/app/models/book_generation.py` for domain logic
- Check `/config/base.py` for scalability optimizations

### Testing Strategy
- Unit tests for models and services
- Integration tests for API endpoints
- Load tests for 10K user scenarios via `test_10k_users_system.sh`
- Circuit breaker tests for resilience validation

### Deployment
- Development: `make dev` or `docker-compose up`
- Production: `make prod` or `docker-compose -f docker-compose.prod.yml up -d`
- Testing: `docker-compose -f docker-compose.test.yml up` (10K user validation)

## System Status

**Current State**: ✅ Stable and production-ready
- Optimized for 10,000 concurrent users
- Professional document generation pipeline
- Advanced AI integration with Claude Sonnet 4
- Comprehensive monitoring and resilience patterns
- 99.5% reliability with automatic recovery systems