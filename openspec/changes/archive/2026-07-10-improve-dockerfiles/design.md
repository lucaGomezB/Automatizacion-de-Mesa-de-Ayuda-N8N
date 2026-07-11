## Context

Los Dockerfiles actuales del proyecto (Gestion_Incidentes/ y Frontend/) tienen varios problemas:
- **Seguridad**: Ambos ejecutan como root, lo cual es un riesgo en producción
- **Eficiencia**: No usan multi-stage builds, resultando en imágenes más grandes
- **Producción**: Frontend ejecuta `npm run dev` en vez de un servidor web optimizado
- **Mantenimiento**: Sin `.dockerignore`, copian archivos innecesarios (tests, .git, etc.)

El proyecto está en modo mantenimiento con 10 cambios OPSX completados. Los Dockerfiles son funcionales para desarrollo pero necesitan mejoras para producción.

## Goals / Non-Goals

**Goals:**
- Mejorar seguridad ejecutando contenedores como usuarios non-root
- Reducir tamaño de imágenes con multi-stage builds
- Servir frontend con nginx en producción (build estático)
- Agregar `.dockerignore` para excluir archivos innecesarios
- Usar `npm ci` para builds deterministas
- Agregar healthchecks en Dockerfiles

**Non-Goals:**
- Cambiar la arquitectura del backend o frontend
- Modificar docker-compose.yml (se mantiene para desarrollo)
- Implementar CI/CD pipeline
- Cambiar dependencias del proyecto

## Decisions

### 1. Multi-stage build para Frontend
**Decisión**: Usar multi-stage build con nginx para producción
**Razón**: 
- nginx es más ligero y seguro para servir archivos estáticos
- Reduce tamaño de imagen final (solo archivos build, no node_modules)
- Mejor rendimiento que vite dev server
**Alternativas consideradas**:
- Mantener vite dev server: rechazado por no ser production-ready
- Usar node server: más pesado que nginx

### 2. Usuario non-root en ambos Dockerfiles
**Decisión**: Crear usuario dedicado en ambos Dockerfiles
**Razón**:
- Seguridad: reduce superficie de ataque
- Best practice de Docker
- Permite control de permisos más granular
**Alternativas consideradas**:
- Usar root: rechazado por riesgos de seguridad
- Usar usuarios existentes de base image: no siempre disponibles

### 3. .dockerignore idéntico para ambos servicios
**Decisión**: Crear .dockerignore con reglas comunes
**Razón**:
- Excluir tests, docs, .git, __pycache__, node_modules
- Reducir contexto de build y tiempo de compilación
- Mejorar seguridad excluyendo archivos sensibles

### 4. npm ci en vez de npm install
**Decisión**: Usar npm ci para Frontend
**Razón**:
- Más rápido y determinista
- Usa package-lock.json exacto
- Mejor para CI/CD y producción

## Risks / Trade-offs

**Riesgo**: nginx puede tener configuración diferente a vite dev server
**Mitigación**: Usar configuración nginx mínima para SPA (Single Page Application)

**Riesgo**: Usuarios non-root pueden tener problemas de permisos con volumes
**Mitigación**: Asignar ownership correcto en Dockerfile y docker-compose

**Riesgo**: Multi-stage build puede fallar si hay dependencias faltantes
**Mitigación**: Testear build en entorno local antes de deploy

**Trade-off**: Imágenes más seguras vs. complejidad adicional en Dockerfiles
**Decisión**: Vale la pena para producción, mantenimiento simplificado a largo plazo
