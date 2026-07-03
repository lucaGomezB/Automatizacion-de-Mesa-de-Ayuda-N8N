# C-20: TLS/HTTPS for Docker Compose Stack

## Why

The thesis (Chapter 11, §11.4) explicitly requires TLS 1.3 encryption in transit between all system components as part of the security technical measures underpinning the confidentiality-integrity-availability triad. Currently the `docker-compose.yml` stack exposes all services over plain HTTP -- backend on port 8000, N8N on port 5678, and frontend on port 3000. This gap means the deployed system does not meet its own stated security requirements. Adding a reverse-proxy TLS termination layer closes this gap without modifying any application code.

## What Changes

- Add an **nginx reverse proxy** service to the compose stack that terminates TLS 1.3 at the edge
- Add a **certificate generation helper script** (`scripts/generate-certs.sh` and `scripts/generate-certs.ps1`) that creates self-signed certificates for development; the compose is designed so production certificates (Let's Encrypt, corporate CA) can be substituted by volume-mounting real certs
- Expose services on **HTTPS port 443** through the proxy: `/api/v1/` routes to backend, `/` routes to frontend, `/n8n/` (or subdomain equivalent) routes to N8N
- Redirect **HTTP port 80 → HTTPS 443** for all incoming traffic
- Enable **HSTS** headers (`Strict-Transport-Security`) on the nginx proxy
- Update **N8N environment variables**: `N8N_PROTOCOL: https`, `WEBHOOK_URL: https://localhost/n8n/` (or equivalent)
- Update **frontend `VITE_API_BASE_URL`** to `https://localhost/api/v1`
- Update **README.md** and **docs/operational-guide.md** with new port numbers (443) and HTTPS URLs
- All internal container-to-container communication stays on plain HTTP over the Docker bridge network (no change to internal healthchecks, backend→postgres, n8n→backend, or backend→n8n webhook URLs)
- Keep the developer UX simple: `docker compose up -d` must still work after running the cert generation script once

## Capabilities

### New Capabilities

- `tls-docker-compose`: TLS 1.3 termination at the reverse proxy layer for the docker-compose development stack. Covers nginx configuration, self-signed certificate generation, HTTP→HTTPS redirect, HSTS headers, and updated service URLs.

### Modified Capabilities

- `project-documentation`: README.md and docs/operational-guide.md must reflect the new HTTPS URLs, ports (443 instead of 8000/5678/3000 for external access), and the certificate generation prerequisite step.

## Impact

- **docker-compose.yml**: New `nginx` service, updated port mappings (80, 443 exposed), updated environment variables for n8n and frontend services
- **New files**: `nginx/nginx.conf` (reverse proxy configuration), `nginx/Dockerfile` or direct use of `nginx:alpine` image, `scripts/generate-certs.sh`, `scripts/generate-certs.ps1`
- **Documentation**: `README.md` (deployment section), `docs/operational-guide.md` (deployment, health verification, N8N access sections)
- **No application code changes**: Backend FastAPI, frontend React, and N8N workflow code are not touched
- **No database changes**
- **Breaking change for external consumers**: URLs change from `http://localhost:8000/api/v1` to `https://localhost/api/v1`, N8N from `http://localhost:5678` to `https://localhost/n8n/`. Internal Docker-network URLs are unaffected.
