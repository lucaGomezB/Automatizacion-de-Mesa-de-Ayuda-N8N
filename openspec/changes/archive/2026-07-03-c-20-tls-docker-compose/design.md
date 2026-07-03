# Design: TLS/HTTPS for Docker Compose Stack

## Context

The `docker-compose.yml` currently exposes 5 services with direct host-port mappings: PostgreSQL (5433), Redis (6379), backend FastAPI (8000), N8N (5678), and frontend React (3000). All HTTP services communicate over plain HTTP, both externally and internally. The thesis requires TLS 1.3 encryption in transit (Chapter 11, §11.4) as part of the CIA triad security model. This design adds a TLS-terminating reverse proxy at the edge of the Docker network, leaving all internal service-to-service communication on plain HTTP over the trusted Docker bridge network.

**Constraint**: Must work on Docker Desktop for Windows (the development environment).

**Stakeholders**: Developers deploying locally, thesis evaluator reviewing security compliance.

## Goals / Non-Goals

**Goals:**
- Terminate TLS 1.3 at a reverse proxy serving all HTTP-based services (backend API, frontend SPA)
- Provide a self-signed certificate generation script that works on Windows (PowerShell) and Linux/macOS (bash)
- Redirect HTTP (port 80) to HTTPS (port 443) for all incoming traffic
- Serve `Strict-Transport-Security` (HSTS) header on HTTPS responses
- Update N8N environment variables to reflect HTTPS external URL for webhook construction
- Update frontend `VITE_API_BASE_URL` to the HTTPS API endpoint
- Update README.md and docs/operational-guide.md with new deployment URLs and the certificate prerequisite step
- Keep `docker compose up -d` working: one prerequisite step (cert generation), then compose is self-contained

**Non-Goals:**
- Application-level TLS (FastAPI HTTPS, N8N internal HTTPS) — TLS termination at the proxy edge is sufficient
- Production certificate automation (Let's Encrypt, ACME) — the design supports volume-mounting real certificates but does not automate acquisition
- Mutual TLS (mTLS) between services
- Modifying backend FastAPI code, frontend React code, or N8N workflow code
- Encrypting PostgreSQL or Redis connections — these are single-node local development databases

## Decisions

### D1: nginx over Traefik as reverse proxy

**Chosen**: nginx (official `nginx:alpine` image)

**Rationale**: nginx is simpler for a static reverse-proxy configuration. Traefik would add a service discovery mechanism (Docker socket mounting, labels on services) that is unnecessary for a 5-service compose and introduces a Docker Desktop compatibility concern on Windows. nginx configuration is a single file (`nginx.conf`), easily inspected and version-controlled. No additional Docker socket permissions required.

**Alternatives considered**:
- **Traefik**: Better for dynamic service discovery in larger stacks, but overkill here. Requires mounting `/var/run/docker.sock`, which is a security concern and has file permission issues on Windows.
- **Caddy**: Automatic HTTPS with Let's Encrypt is appealing, but the self-signed certificate requirement makes Caddy's auto-TLS a complication rather than a benefit. Caddy's configuration DSL is less familiar to operators.

### D2: Self-signed certificates with a generation script

**Chosen**: OpenSSL-generated self-signed X.509 certificate (RSA 2048-bit key, SHA-256, 365-day validity) created by a helper script.

**Rationale**: Self-signed certificates are the only option for `localhost` development without a public domain. The script (`scripts/generate-certs.sh` / `scripts/generate-certs.ps1`) runs `openssl req -x509 -nodes -days 365 -newkey rsa:2048` and outputs `nginx/certs/server.crt` and `nginx/certs/server.key`. The script is idempotent: re-running overwrites existing certs.

**Alternatives considered**:
- **mkcert**: Excellent tool for localhost certificates trusted by the system root store. However, it requires installation (`choco install mkcert` on Windows, `brew install mkcert` on macOS) and CA root installation, adding a prerequisite beyond Docker.
- **Embedded cert generation in entrypoint**: Having the nginx container generate certs on startup would make `docker compose up` truly one-step, but (a) the cert would change on every restart, breaking browser trust, and (b) entrypoint complexity adds failure modes.

### D3: Port mapping — remove host exposure for backend and frontend

**Chosen**: Remove `ports` mappings for `backend:8000` and `frontend:3000`. All external HTTP access goes through nginx on ports 80 and 443. Keep direct port mappings for PostgreSQL (5433), Redis (6379), and N8N (5678) as these are non-HTTP protocols or admin tools where path-based reverse proxy is problematic.

**Rationale**: Forcing all HTTP traffic through the proxy ensures TLS is applied consistently. Backend API endpoints (`/api/v1/*`) and frontend static assets are served exclusively through nginx. N8N's web-based editor works poorly behind a path-prefixed reverse proxy (known issues with WebSocket connections and asset paths), so it retains its direct port mapping as a pragmatic exception.

**Alternatives considered**:
- **Path-prefix proxy for N8N** (`/n8n/` → `n8n:5678/`): N8N does not natively support path-prefix operation. Environment variables like `N8N_PATH` are not officially documented or reliable across versions. Subdomain-based routing requires DNS configuration beyond the compose scope.
- **Keep all ports exposed**: Defeats the purpose of TLS enforcement. Users would continue hitting plain HTTP by habit.

### D4: Internal Docker network communication remains plain HTTP

**Chosen**: All inter-container HTTP traffic (`backend` ↔ `n8n`, `backend` → `postgres`, `n8n` → `redis`) stays on plain HTTP over the internal Docker bridge network.

**Rationale**: The Docker bridge network is an isolated, trusted network segment. Adding TLS to internal communication would require certificate management for every service, breaking the "no application code changes" constraint. The thesis security requirement (§11.4) is about encryption in transit between system components and external consumers; the Docker network boundary is the appropriate trust boundary.

**Alternatives considered**:
- **Internal TLS everywhere**: Would require each service to load certificates, adding startup dependencies and configuration complexity. Not justified for a single-host development environment.

### D5: HSTS header with conservative max-age

**Chosen**: `Strict-Transport-Security: max-age=31536000; includeSubDomains` (1 year) on all HTTPS responses.

**Rationale**: HSTS instructs browsers to always use HTTPS for this origin, preventing downgrade attacks. The 1-year duration is standard. `includeSubDomains` is included for completeness but has no practical effect on `localhost`.

### D6: HTTP → HTTPS redirect

**Chosen**: nginx listens on port 80 and returns a 301 Moved Permanently redirect to the HTTPS equivalent URL.

**Rationale**: Ensures any accidental HTTP access is transparently upgraded. A 301 redirect preserves the request path.

### D7: Certificate directory structure

**Chosen**:
```
nginx/
├── nginx.conf
└── certs/
    ├── .gitkeep
    ├── server.crt     (generated, git-ignored)
    └── server.key     (generated, git-ignored)
scripts/
├── generate-certs.sh
└── generate-certs.ps1
```

**Rationale**: Certificate files are `.gitignore`d to prevent committing generated keys. The `certs/` directory is mounted as a volume into the nginx container so certificate updates take effect on container restart without a rebuild. The `.gitkeep` file ensures the directory exists after clone.

## Architecture

```
                      Docker Host
  ┌─────────────────────────────────────────────────────┐
  │                                                     │
  │  External Request (HTTPS)                           │
  │       │                                             │
  │       ▼                                             │
  │  ┌──────────────┐     ┌─────────────────────────┐   │
  │  │   nginx:443  │────▶│   nginx:alpine           │   │
  │  │   nginx:80   │     │   TLS termination        │   │
  │  │  (published) │     │   HSTS header            │   │
  │  └──────────────┘     │   HTTP→HTTPS redirect    │   │
  │                       └──────┬──────────┬────────┘   │
  │                              │          │            │
  │                    /api/v1/* │          │ /*         │
  │                              ▼          ▼            │
  │              ┌──────────────────┐  ┌──────────────┐  │
  │              │  backend:8000    │  │ frontend:3000 │  │
  │              │  (FastAPI)       │  │ (React/Vite)  │  │
  │              │  no host port    │  │ no host port  │  │
  │              └────────┬─────────┘  └──────────────┘  │
  │                       │ http://n8n:5678              │
  │                       ▼                              │
  │              ┌──────────────────┐                    │
  │              │  n8n:5678        │◀── port 5678       │
  │              │  (direct access  │   (published for   │
  │              │   for admin UI)  │    admin access)   │
  │              └──────────────────┘                    │
  │                                                     │
  │  postgres:5433 (published, non-HTTP)                │
  │  redis:6379    (published, non-HTTP)                │
  └─────────────────────────────────────────────────────┘
```

## Nginx Configuration Logic

```
server {
    listen 80;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    http2 on;

    ssl_certificate     /etc/nginx/certs/server.crt;
    ssl_certificate_key /etc/nginx/certs/server.key;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Backend API — path preserved (strip prefix handled by backend routes)
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend SPA — catch-all
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        # WebSocket support for Vite HMR
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Risks / Trade-offs

- **[Self-signed cert browser warnings]** → The browser will show a "Your connection is not private" warning on first access. Mitigation: document in README that this is expected for local development; users click "Advanced → Proceed". For team demos, instruct users to import the CA into their system trust store or use mkcert.
- **[Certificate expiration (365 days)]** → After 365 days, HTTPS breaks. Mitigation: the `generate-certs` script is idempotent; re-running it regenerates the cert. Document the expiration in the operational guide.
- **[N8N webhook external URL mismatch]** → N8N's `WEBHOOK_URL` is set to `https://localhost:5678/` (or through nginx). If a third-party service needs to call N8N webhooks, they must accept self-signed certificates. Mitigation: this is a development stack; production deployments use valid certificates.
- **[Frontend Vite HMR through proxy]** → Vite's Hot Module Replacement uses WebSockets. The nginx config includes `Upgrade` and `Connection` headers to support WebSocket proxying. If HMR fails through the proxy, the frontend port can be temporarily re-exposed for development.
- **[Port 80/443 conflict on Windows]** → Windows may have IIS or another service on port 80/443. Mitigation: document this in troubleshooting; users can change the nginx published ports via `.env` override or `COMPOSE_FILE` merge.

## Migration Plan

1. **Before change**: Services accessible via `http://localhost:8000`, `http://localhost:5678`, `http://localhost:3000`
2. **After change**: Services accessible via `https://localhost/api/v1/` (backend), `https://localhost/` (frontend), `http://localhost:5678` (N8N — unchanged direct access)
3. **Rollback**: Revert `docker-compose.yml` changes. The certs directory and nginx directory are additive; removing the nginx service entry from the compose and restoring `ports` on backend/frontend reverts to the previous state.
4. **No data migration required** — PostgreSQL and Redis volumes are unaffected.

## Open Questions

- **Should N8N also go through the proxy despite the path-prefix limitation?** Current decision: keep direct port access for N8N admin UI. If n8nio/n8n adds official path-prefix support in a future version, this can be revisited.
- **Should we add a `.env` variable for the TLS certificate path?** Current decision: hardcoded `nginx/certs/` path. Adding an env var would add flexibility but also complexity. Defer until a production deployment use case requires it.
