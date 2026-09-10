## ADDED Requirements

### Requirement: TLS termination via nginx reverse proxy

The docker-compose stack SHALL include an nginx reverse proxy service that terminates TLS 1.3 for all external HTTP traffic. The proxy MUST serve the backend API under the `/api/` path prefix and the frontend SPA under the root path `/`. Internal container-to-container communication on the Docker bridge network MUST remain on plain HTTP.

#### Scenario: Backend API accessible through HTTPS via nginx

- **WHEN** a client sends an HTTPS GET request to `https://localhost/api/v1/health`
- **THEN** the nginx proxy forwards the request to `http://backend:8000/api/v1/health` and returns the backend's JSON response with HTTP 200

#### Scenario: Frontend accessible through HTTPS via nginx

- **WHEN** a client sends an HTTPS GET request to `https://localhost/`
- **THEN** the nginx proxy forwards the request to `http://frontend:3000/` and returns the React SPA's HTML

#### Scenario: Internal backend-to-N8N communication stays on plain HTTP

- **WHEN** the backend service sends a request to `http://n8n:5678/webhook`
- **THEN** the request reaches N8N directly over the Docker bridge network without passing through nginx

#### Scenario: Internal healthchecks continue to work over plain HTTP

- **WHEN** Docker Compose runs healthchecks for the backend service
- **THEN** the healthcheck command `urllib.request.urlopen('http://localhost:8000/health')` succeeds as before because it runs inside the backend container on the internal HTTP port

### Requirement: Self-signed certificate generation script

The project SHALL provide two certificate generation scripts — `scripts/generate-certs.sh` (bash) and `scripts/generate-certs.ps1` (PowerShell) — that create a self-signed X.509 certificate and private key in `nginx/certs/server.crt` and `nginx/certs/server.key`. The certificate MUST use RSA 2048-bit key, SHA-256 signature, and a 365-day validity period. The scripts MUST be idempotent (re-running overwrites existing certificates). The `nginx/certs/` directory MUST contain a `.gitkeep` file to ensure it survives `git clone`.

#### Scenario: Bash script generates certificate on Linux/macOS

- **WHEN** `scripts/generate-certs.sh` is executed on a system with `openssl` available
- **THEN** `nginx/certs/server.crt` and `nginx/certs/server.key` are created and the certificate is a valid self-signed X.509 certificate with a 365-day validity

#### Scenario: PowerShell script generates certificate on Windows

- **WHEN** `scripts/generate-certs.ps1` is executed on Windows with OpenSSL available (via Git Bash, Docker, or chocolatey)
- **THEN** `nginx/certs/server.crt` and `nginx/certs/server.key` are created with the same properties as the bash-generated certificate

#### Scenario: Script is idempotent

- **WHEN** the generate-certs script is executed a second time while `server.crt` and `server.key` already exist
- **THEN** the existing files are overwritten with a new certificate without error

### Requirement: HTTP to HTTPS redirect

The nginx reverse proxy SHALL listen on port 80 and return an HTTP 301 redirect to the equivalent HTTPS URL for every incoming request. The redirect MUST preserve the request path and query string.

#### Scenario: Plain HTTP request is redirected to HTTPS

- **WHEN** a client sends `GET http://localhost/api/v1/health`
- **THEN** the response has HTTP status 301 and the `Location` header is `https://localhost/api/v1/health`

#### Scenario: Redirect preserves query parameters

- **WHEN** a client sends `GET http://localhost/?tab=tickets`
- **THEN** the response redirects to `https://localhost/?tab=tickets`

### Requirement: HSTS header on HTTPS responses

The nginx reverse proxy SHALL include the `Strict-Transport-Security` header with `max-age=31536000` and `includeSubDomains` on all HTTPS responses.

#### Scenario: HTTPS response includes HSTS header

- **WHEN** a client sends an HTTPS request to any path served by nginx
- **THEN** the response includes the header `Strict-Transport-Security: max-age=31536000; includeSubDomains`

#### Scenario: HTTP redirect response does not include HSTS

- **WHEN** a client sends an HTTP request that triggers a 301 redirect
- **THEN** the response does NOT include the `Strict-Transport-Security` header (HSTS must only be served over HTTPS per RFC 6797)

### Requirement: N8N environment variables reflect HTTPS external URL

The N8N service in docker-compose.yml SHALL have `N8N_PROTOCOL` set to `https` and `WEBHOOK_URL` set to an HTTPS URL so that N8N constructs webhook URLs with the correct scheme. Internal communication between the backend and N8N (the `N8N_WEBHOOK_URL` environment variable in the backend service) MUST remain `http://n8n:5678/webhook` because it traverses the Docker bridge network internally.

#### Scenario: N8N_PROTOCOL is set to https

- **WHEN** `docker compose up -d` starts the N8N container
- **THEN** the N8N instance reports its protocol as `https` in the settings UI

#### Scenario: Backend still calls N8N webhooks internally over HTTP

- **WHEN** the backend service's `N8N_WEBHOOK_URL` is inspected
- **THEN** its value is `http://n8n:5678/webhook` (internal Docker DNS, unchanged)

### Requirement: Frontend API base URL uses HTTPS

The frontend service in docker-compose.yml SHALL have `VITE_API_BASE_URL` set to `https://localhost/api/v1` so that the React SPA makes API calls over HTTPS through the nginx reverse proxy.

#### Scenario: Frontend environment variable uses HTTPS

- **WHEN** the frontend container starts
- **THEN** the Vite dev server receives `VITE_API_BASE_URL=https://localhost/api/v1` and the bundled JavaScript uses this URL for all API calls

### Requirement: Docker Compose UX preserved

The command `docker compose up -d` SHALL work after a one-time prerequisite step of running the certificate generation script. The nginx service MUST wait for the backend and frontend services to be running before accepting traffic, using Docker Compose `depends_on` with `condition: service_started`.

#### Scenario: First-time setup works end-to-end

- **WHEN** a developer clones the repo, runs the certificate generation script, and executes `docker compose up -d`
- **THEN** all services (postgres, redis, backend, n8n, frontend, nginx) reach healthy/running state

#### Scenario: Nginx starts after backend and frontend

- **WHEN** docker compose starts the stack
- **THEN** the nginx container does not start until the backend and frontend containers are at least in `service_started` state, preventing 502 errors during startup

### Requirement: Certificate and key files excluded from version control

The `nginx/certs/server.crt` and `nginx/certs/server.key` files SHALL be excluded from Git via `.gitignore`. The `nginx/certs/.gitkeep` file SHALL be tracked to preserve the directory structure on clone.

#### Scenario: Certificate files are gitignored

- **WHEN** `git status` is run after certificate generation
- **THEN** `server.crt` and `server.key` under `nginx/certs/` do not appear as untracked or staged files

#### Scenario: Certs directory exists after clone

- **WHEN** a developer clones the repository
- **THEN** the directory `nginx/certs/` exists (containing at least `.gitkeep`) so the generation script has a target location
