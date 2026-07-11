# frontend-production-build — Spec

## Purpose

Define los requisitos para builds de producción del frontend: multi-stage Docker, npm ci, y configuración nginx para SPA routing.

## Requirements

### Requirement: Frontend Dockerfile SHALL use multi-stage build
The frontend Dockerfile SHALL implement a multi-stage build process with separate build and production stages.

#### Scenario: Build stage compiles TypeScript and bundles assets
- **WHEN** the Docker build runs
- **THEN** the build stage SHALL install dependencies with npm ci
- **AND** compile TypeScript with npm run build
- **AND** generate optimized static assets in dist/ directory

#### Scenario: Production stage serves with nginx
- **WHEN** the production image is created
- **THEN** it SHALL copy only the dist/ output from the build stage
- **AND** serve static files using nginx:alpine base image
- **AND** expose port 3000 for external access

### Requirement: Frontend SHALL use npm ci for deterministic builds
The frontend Dockerfile SHALL use npm ci instead of npm install for dependency installation.

#### Scenario: npm ci installs exact dependencies
- **WHEN** the build stage runs dependency installation
- **THEN** npm ci SHALL be used to install dependencies from package-lock.json
- **AND** the installation SHALL be deterministic and reproducible

### Requirement: Nginx SHALL be configured for SPA routing
The nginx configuration SHALL support client-side routing for single-page applications.

#### Scenario: Nginx serves index.html for all routes
- **WHEN** a user navigates to any frontend route
- **THEN** nginx SHALL serve index.html to enable client-side routing
- **AND** static assets SHALL be served with appropriate caching headers

### Requirement: Frontend SHALL be accessible on port 3000
The frontend application SHALL be accessible on port 3000 in both development and production environments.

#### Scenario: Production frontend serves on port 3000
- **WHEN** the frontend container starts in production mode
- **THEN** the application SHALL be accessible on port 3000
- **AND** serve optimized static assets via nginx

#### Scenario: Development frontend serves on port 3000
- **WHEN** the frontend container starts in development mode
- **THEN** the application SHALL be accessible on port 3000
- **AND** support hot module replacement with vite dev server
