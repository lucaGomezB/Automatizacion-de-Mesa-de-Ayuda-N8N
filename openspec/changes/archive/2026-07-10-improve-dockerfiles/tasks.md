## 1. Backend Dockerfile Security Hardening

- [x] 1.1 Create .dockerignore file in Gestion_Incidentes/ directory
- [x] 1.2 Add non-root user creation to Gestion_Incidentes/Dockerfile
- [x] 1.3 Add HEALTHCHECK instruction to Gestion_Incidentes/Dockerfile
- [x] 1.4 Test backend container runs as non-root user
- [x] 1.5 Verify backend healthcheck works correctly

## 2. Frontend Production Build

- [x] 2.1 Create .dockerignore file in Frontend/ directory
- [x] 2.2 Rewrite Frontend/Dockerfile with multi-stage build
- [x] 2.3 Create nginx configuration file for SPA routing
- [x] 2.4 Add non-root user to frontend production stage
- [x] 2.5 Add HEALTHCHECK instruction to frontend Dockerfile
- [x] 2.6 Use npm ci instead of npm install in build stage

## 3. Nginx Configuration

- [x] 3.1 Create nginx.conf file with SPA routing rules
- [x] 3.2 Configure static asset caching headers
- [x] 3.3 Set up index.html fallback for client-side routing
- [x] 3.4 Test nginx serves frontend correctly on port 3000

## 4. Docker Compose Integration

- [x] 4.1 Update docker-compose.yml if needed for new healthchecks
- [x] 4.2 Test full stack starts with docker compose up -d
- [x] 4.3 Verify all healthchecks pass in docker compose
- [x] 4.4 Test frontend serves production build via nginx

## 5. Testing and Validation

- [x] 5.1 Build backend Docker image and verify non-root user
- [x] 5.2 Build frontend Docker image and verify multi-stage build
- [x] 5.3 Test .dockerignore files exclude correct files
- [x] 5.4 Verify nginx serves static assets correctly
- [x] 5.5 Test SPA routing with nginx (direct URL access)
- [x] 5.6 Validate healthchecks in both Dockerfiles
