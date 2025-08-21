---
allowed-tools: Task
argument-hint: [development|production|deployment]
description: Optimización completa de containerización Docker para desarrollo y producción
---

## Tu Tarea

Usa el agente `desarrollador-fullstack-backend` para optimizar la containerización Docker completa del proyecto.

**Entorno objetivo:** ${ARGUMENTS:-production}

### Instrucciones específicas:

**Para `development`:** Setup Docker optimizado para desarrollo local y debugging
**Para `production`:** Configuración Docker para producción con máxima eficiencia y seguridad
**Para `deployment`:** Optimización de deployment con orquestación y CI/CD

### Objetivos de optimización Docker:

1. **Multi-stage Builds**: Dockerfiles optimizados con builds multi-etapa
2. **Image Optimization**: Imágenes mínimas con distroless base images
3. **Security Hardening**: Configuración segura con minimal attack surface
4. **Performance Optimization**: Layer caching y build time optimization
5. **Production Readiness**: Health checks, monitoring, y observabilidad

### Áreas de optimización:

#### Development Environment
- Docker Compose stack completo para desarrollo
- Hot reloading y debugging capabilities
- Development databases y servicios auxiliares
- Networking optimizado para desarrollo local

#### Production Environment
- Multi-stage Dockerfiles para producción
- Optimización de tamaño de imagen
- Security scanning y vulnerability management
- Resource limits y optimization

#### Deployment & Orchestration
- Kubernetes manifests production-ready
- Health checks comprehensivos
- Service discovery y load balancing
- Blue-green deployment strategies

### Componentes a containerizar:
- Aplicación Flask principal
- Base de datos PostgreSQL
- Redis para caching y sessions
- Nginx para reverse proxy
- Monitoring stack (Prometheus, Grafana)
- Logging aggregation

### Configuraciones específicas:
- Environment management seguro
- Secrets management
- Volume management para persistencia
- Network policies y security
- Resource quotas y limits
- Backup strategies

### Coordinación obligatoria:
- Análisis arquitectónico con `analizador-arquitectura`
- Validación de seguridad con `security-guardian`
- Optimización de performance con `performance-analyzer`
- Testing de containers con `test-architect`

Crea una configuración Docker completa que soporte tanto desarrollo ágil como deployment de producción robusto y escalable.