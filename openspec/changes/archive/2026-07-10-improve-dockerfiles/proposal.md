## Why

Los Dockerfiles actuales tienen problemas de seguridad, eficiencia y no son adecuados para producción:
- Ejecutan como root (riesgo de seguridad)
- Incluyen dependencias de desarrollo en imágenes de producción
- No tienen `.dockerignore` (copian archivos innecesarios)
- El frontend ejecuta `npm run dev` en vez de un servidor de producción
- No usan multi-stage builds para optimizar tamaño de imágenes

## What Changes

- Agregar `.dockerignore` para excluir archivos innecesarios
- Implementar multi-stage builds para frontend (build + nginx)
- Agregar usuarios non-root en ambos Dockerfiles
- Usar `npm ci` en vez de `npm install` para builds deterministas
- Agregar healthchecks en Dockerfiles
- Frontend: servir build estático con nginx en vez de vite dev server

## Capabilities

### New Capabilities
- `docker-security-hardening`: Mejoras de seguridad en Dockerfiles (non-root user, healthchecks, .dockerignore)
- `frontend-production-build`: Multi-stage build para frontend con nginx para producción

### Modified Capabilities
- `foundation-environment`: Modificar Dockerfiles existentes para incluir mejoras de seguridad y producción

## Impact

- **Archivos modificados**:
  - `Gestion_Incidentes/Dockerfile`
  - `Frontend/Dockerfile`
  - Nuevos: `.dockerignore` en ambos directorios
- **Dependencias**: nginx para frontend en producción
- **Docker Compose**: Puede requerir ajustes para healthchecks y configuración de nginx
- **Seguridad**: Imágenes más seguras con usuarios non-root
- **Tamaño**: Imágenes más pequeñas gracias a multi-stage builds
