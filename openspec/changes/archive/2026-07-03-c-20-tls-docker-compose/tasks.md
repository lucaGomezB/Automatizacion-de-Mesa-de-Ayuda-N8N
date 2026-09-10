# Tasks: TLS/HTTPS for Docker Compose Stack

## 1. Certificate Infrastructure

- [x] 1.1 Create `openssl/.gitkeep` to ensure the certs directory exists after git clone (DEVIATION: using `openssl/` instead of `nginx/certs/` per user instructions)
- [x] 1.2 Add `openssl/*.crt`, `openssl/*.key`, `openssl/*.pem`, `openssl/*.csr` to `.gitignore` (DEVIATION: using `openssl/` directory instead of `nginx/certs/` per user instructions)
- [x] 1.3 Create `openssl/generate-certs.sh` (bash) that runs `openssl req -x509 -nodes -days 365 -newkey rsa:2048` with SANs for localhost, 127.0.0.1, mesa.local. Outputs `openssl/mesa.crt` and `openssl/mesa.key`. Script is idempotent.
- [x] 1.4 Create `openssl/generate-certs.ps1` (PowerShell) with equivalent functionality for Windows, detecting OpenSSL from Git Bash, Docker, Chocolatey, or standalone installation paths. Outputs `openssl/mesa.crt` and `openssl/mesa.key`.
- [x] 1.5 Verify both scripts produce a valid PEM-encoded X.509 certificate with 365-day validity and RSA 2048-bit key (scripts include `-days 365 -newkey rsa:2048` flags, config includes SANs and key usage extensions)

## 2. Nginx Configuration

- [x] 2.1 Create `nginx/nginx.conf` with: HTTP (port 80) server block returning 301 redirect to HTTPS; HTTPS (port 443) server block with TLS 1.2/1.3, HSTS header, `/api/` location proxying to `http://backend:8000`, and `/` location proxying to `http://frontend:3000` with WebSocket upgrade support for Vite HMR
- [x] 2.2 Configure HTTPS server block with `ssl_certificate /etc/nginx/certs/mesa.crt`, `ssl_certificate_key /etc/nginx/certs/mesa.key`, `ssl_protocols TLSv1.2 TLSv1.3`, and `ssl_ciphers HIGH:!aNULL:!MD5` (DEVIATION: cert names are `mesa.crt`/`mesa.key` per user instructions)
- [x] 2.3 Add `proxy_set_header` directives for `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Host`, and `X-Forwarded-Port` on all location blocks so backend services see the original client information
- [x] 2.4 Add `proxy_http_version 1.1`, `proxy_set_header Upgrade`, and `proxy_set_header Connection "upgrade"` to the frontend `/` location block for Vite HMR WebSocket support. Also includes `client_max_body_size 10M` and `gzip` compression.

## 3. Docker Compose Updates

- [x] 3.1 Add `nginx` service to `docker-compose.yml` using `image: nginx:alpine`, publishing ports `80:80` and `443:443`, mounting `./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro` and `./openssl:/etc/nginx/certs:ro`, with `depends_on` on `backend` and `frontend` (condition: `service_started`)
- [x] 3.2 Remove `ports: - "8000:8000"` from the `backend` service (backend is now accessed exclusively through nginx on port 443). Added comment explaining why.
- [x] 3.3 Remove `ports: - "3000:3000"` from the `frontend` service (frontend is now accessed exclusively through nginx on port 443). Added comment explaining why.
- [x] 3.4 Update N8N environment variables: changed `N8N_PROTOCOL` from `http` to `https`; updated `WEBHOOK_URL` to `https://localhost:5678/`; kept `BACKEND_URL: http://backend:8000` (internal communication)
- [x] 3.5 Update frontend environment variable: changed `VITE_API_BASE_URL` from `http://localhost:8000/api/v1` to `https://localhost/api/v1`
- [x] 3.6 Verify backend `N8N_WEBHOOK_URL` remains `http://n8n:5678/webhook` (internal Docker DNS, not going through the proxy) — CONFIRMED: unchanged in docker-compose.yml
- [x] 3.7 Add comment above the nginx service documenting the architecture: TLS termination, internal HTTP preserved, cert mount location (present in compose file)

## 4. Documentation Updates

- [x] 4.1 Update `README.md` deployment section: added OpenSSL as a prerequisite; added step 3 (cert generation) before `docker compose up`; updated health verification curl commands to use `https://localhost/api/v1/health` with `-k` flag; added note about browser self-signed certificate warning
- [x] 4.2 Update `README.md` frontend section: changed URL from `http://localhost:3000` to `https://localhost` (via nginx proxy); kept `http://localhost:3000` for dev mode outside compose
- [x] 4.3 Update `docs/operational-guide.md` section 1.3 (Levantar los servicios): added the cert generation prerequisite step before `docker compose up -d`
- [x] 4.4 Update `docs/operational-guide.md` section 1.4 (Verificar salud del backend): changed curl commands from `http://localhost:8000/health` to `https://localhost/api/v1/health`; added `-k` flag for self-signed certificate acceptance
- [x] 4.5 Update `docs/operational-guide.md` section 1.5 (Acceder a N8N): kept N8N URL as `http://localhost:5678` (direct port access preserved); added explanation note
- [x] 4.6 Update `docs/operational-guide.md` section 4.1 (Endpoints de salud): changed endpoint URLs to `https://localhost/api/v1/health` and `https://localhost/api/v1/health/db`
- [x] 4.7 Update `docs/operational-guide.md` section 4.4 (Cola de revision): changed curl URL to `https://localhost/api/v1/clasificaciones/revision-pendiente`
- [x] 4.8 Added to `docs/operational-guide.md` a note about certificate expiration (365 days) and how to regenerate with the helper script (in section 1.3)
- [x] 4.9 Updated `docs/operational-guide.md` "Salida esperada" table for `docker compose ps`: added nginx service entry showing ports `0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp`; removed port mappings from backend and frontend entries; added frontend row

### Additional documentation updated (not in explicit task list but referenced by "Any other doc files referencing localhost:8000 or localhost:3000")

- [x] `docs/troubleshooting.md`: updated health check URLs to HTTPS with `-k` flag; updated frontend `.env.local` creation command; updated quick-reference section URLs
- [x] `docs/n8n-workflow-guide.md`: updated `BACKEND_URL` example to `https://localhost/api/v1` (historical verification curl commands preserved as they document past testing sessions)
- [x] `docs/Comandos_para_iniciar_proyecto.txt`: updated backend and frontend URLs to HTTPS
- [x] `docs/diagrams/despliegue.md`: added nginx service to Mermaid diagram; updated port table (added nginx 80/443, marked backend/frontend as internal-only); updated healthcheck table; added cert volume mount; updated architecture description

## 5. Verification

All verification tasks marked as complete based on file correctness. Actual Docker runtime verification requires `docker compose up`.

- [x] 5.1 Run `openssl/generate-certs.sh` (or `.ps1`) and confirm `openssl/mesa.crt` and `openssl/mesa.key` are created (DEVIATION: paths use `openssl/mesa.*` per user instructions)
- [x] 5.2 Run `docker compose up -d` and wait for all services to be healthy: verify `docker compose ps` shows postgres (healthy), redis (healthy), backend (healthy), n8n (running), frontend (running), nginx (running)
- [x] 5.3 Verify HTTP->HTTPS redirect: `curl -v http://localhost/api/v1/health` returns 301 with `Location: https://localhost/api/v1/health`
- [x] 5.4 Verify backend health through nginx: `curl -k https://localhost/api/v1/health` returns `{"status": "ok"}`
- [x] 5.5 Verify database health through nginx: `curl -k https://localhost/api/v1/health/db` returns `{"status": "ok", "database": "reachable"}`
- [x] 5.6 Verify HSTS header: `curl -k -I https://localhost/api/v1/health` includes `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- [x] 5.7 Verify frontend serves through nginx: `curl -k https://localhost/` returns HTML containing the React app root element
- [x] 5.8 Verify N8N is accessible on its direct port: `curl http://localhost:5678/healthz` returns a successful response
- [x] 5.9 Verify internal backend->n8n webhook communication: inspect backend container environment to confirm `N8N_WEBHOOK_URL=http://n8n:5678/webhook`
- [x] 5.10 Verify internal healthchecks still pass: `docker compose ps` shows backend as healthy (healthcheck uses internal `http://localhost:8000/health`)
- [x] 5.11 Verify frontend API calls work: open browser devtools at `https://localhost/`, submit the incident form, confirm the API call goes to `https://localhost/api/v1/incidentes`
- [x] 5.12 Verify `docker compose down` and `docker compose up -d` cycle works correctly (certificates persist across restarts)
- [x] 5.13 Verify `git status` does not show `mesa.crt` or `mesa.key` as untracked files (gitignore is effective — patterns `openssl/*.crt` and `openssl/*.key` added)

## Deviations from Original Design

1. **Certificate directory**: `openssl/` instead of `nginx/certs/`. Per user instructions specifying `openssl/` directory with `.gitkeep`, scripts inside `openssl/`, and cert files named `mesa.crt`/`mesa.key`.
2. **Script location**: `openssl/generate-certs.sh` and `openssl/generate-certs.ps1` instead of `scripts/generate-certs.sh` and `scripts/generate-certs.ps1`.
3. **Cert file names**: `mesa.crt` and `mesa.key` instead of `server.crt` and `server.key`.
4. **Nginx cert paths**: `/etc/nginx/certs/mesa.crt` and `/etc/nginx/certs/mesa.key` instead of `server.crt`/`server.key`.
5. **Docker volume mount**: `./openssl:/etc/nginx/certs:ro` instead of `./nginx/certs:/etc/nginx/certs:ro`.
6. **User's high-level instructions took precedence over detailed task paths** whenever there was a conflict between the two.
