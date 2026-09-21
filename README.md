# Automatizacion-de-Mesa-de-Ayuda-N8N-

[![CI](https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N/actions/workflows/ci.yml/badge.svg)](https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N/actions/workflows/ci.yml)

En este proyecto se busca una forma eficiente de facilitar el trabajo de la Mesa de Ayuda de cualquier empresa haciendo uso una automatizacion N8N

---

## Despliegue local

> Tiempo estimado desde un clon limpio: **menos de 15 minutos**.
>
> Para procedimientos detallados (backup, monitoreo, actualizaciones), ver
> [`docs/operational-guide.md`](docs/operational-guide.md).
> Para resolver problemas frecuentes, ver
> [`docs/troubleshooting.md`](docs/troubleshooting.md).

### Prerrequisitos

- **Docker Engine 24+** y **Docker Compose v2** (plugin integrado en Docker Desktop)
- **Git 2.x**
- **OpenSSL** (para generar los certificados TLS de desarrollo)
- **curl** (para las verificaciones de salud por HTTPS)
- **make** (opcional, solo como alias de conveniencia)

Verificar:
```bash
docker --version
docker compose version
openssl version
curl --version
make --version   # opcional
```

> **Nota sobre Windows**: si `openssl` no esta disponible en el PATH, Git for Windows lo incluye en `C:\Program Files\Git\usr\bin\`. El script `openssl\generate-certs.ps1` lo detecta automaticamente.

### Camino recomendado: un solo comando

El comando unico verifica el entorno, genera los certificados TLS si faltan,
levanta el stack con `docker compose up -d --build`, espera a que los servicios
queden sanos y valida los endpoints de salud por HTTPS. Falla de forma explicita
si `App/Backend/.env` no existe o si `GEMINI_API_KEY`,
`PSEUDONYMIZATION_ENCRYPTION_KEY` o `JWT_SECRET_KEY` estan ausentes, vacias o
conservan los placeholders de la plantilla.

Antes de tocar Docker, el comando unico ejecuta un preflight de costo: si el
preflight falla, el arranque se bloquea y no se levanta ningun servicio. El bypass
explicito es `UP_SKIP_COST_PREFLIGHT=1`; al usarlo, el arranque continua pero
imprime una advertencia audible. Es una excepcion deliberada, no el camino normal.

**Linux / macOS:**
```bash
bash scripts/up.sh
# Alternativa equivalente si make esta instalado:
make up
```

**Windows (PowerShell):**
```powershell
.\scripts\up.ps1
# Alternativa equivalente si make esta instalado:
make up
```

`make` es opcional: los scripts pareados son la fuente de verdad y se pueden
ejecutar directamente. En Windows, para obtener `make` usar
`choco install make` (requiere Chocolatey); si no se desea instalar `make`,
ejecutar `.\scripts\up.ps1` directamente.

Al finalizar, el comando imprime las URLs de acceso y recuerda importar
`n8n/workflow.json` y configurar las credenciales de Outlook, Twilio y Gemini en
N8N de forma manual. La importacion del workflow NO es automatica.

Los pasos siguientes describen el camino manual equivalente.

### 1. Clonar y configurar el hook anti-secretos

```bash
git clone https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N.git
cd Automatizacion-de-Mesa-de-Ayuda-N8N

# Activar el hook pre-commit que bloquea commits con credenciales (obligatorio)
git config core.hooksPath .githooks
```

### 2. Configurar las variables de entorno

```bash
cp App/Backend/.env.example App/Backend/.env
```

Editar `App/Backend/.env` y completar:

| Variable                          | Descripción |
|-----------------------------------|-------------|
| `GEMINI_API_KEY`                  | Clave de Google Gemini (obtener en [aistudio.google.com](https://aistudio.google.com/app/apikey)) |
| `PSEUDONYMIZATION_ENCRYPTION_KEY` | Clave Fernet de 32 bytes en base64url (generar con `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`) |
| `JWT_SECRET_KEY`                  | Clave de firma HS256 de los tokens JWT (generar con `python -c "import secrets; print(secrets.token_urlsafe(32))"`) |
| `DATABASE_URL`                    | Ya configurada en `.env.example` para el compose; no cambiar el host |
| `COST_GUARD_SHARED_SECRET`        | Secreto compartido OBLIGATORIO del endpoint de reserva que consume n8n (`POST /api/v1/cost-guard/reserve`). Se envía en el header `X-Cost-Guard-Secret`; nunca por query string. En el stack Docker la fuente única es el `.env` de la raíz (docker-compose lo inyecta en backend y n8n). Si queda vacío, el endpoint responde HTTP 401 y el arranque advierte `cost_guard_secret_missing` |

La guarda de costo en runtime viene **habilitada por defecto** con un default conservador. Todas
sus variables son opcionales y se sobrescriben por `.env`:

| Variable                                    | Default     | Descripción |
|---------------------------------------------|-------------|-------------|
| `COST_GUARD_ENABLED`                        | `true`      | Habilita el enforcement del gasto pago |
| `COST_GUARD_BUDGET_USD`                     | `10.0`      | Bolsa GLOBAL compartida por ventana (USD) |
| `COST_GUARD_BUDGET_WINDOW_SECONDS`          | `604800`    | Ventana del presupuesto (7 días) |
| `COST_GUARD_UNIT_COST_BACKEND_GEMINI_USD`   | `0.0005`    | Costo unitario ESTIMADO por incidente (Gemini backend) |
| `COST_GUARD_UNIT_COST_N8N_GEMINI_USD`       | `0.0015`    | Costo unitario ESTIMADO por ejecución (AI Agent de n8n) |
| `COST_GUARD_UNIT_COST_TWILIO_TRANSCRIPTION_USD` | `0.05`  | Costo unitario ESTIMADO por llamada (transcripción Twilio) |
| `COST_GUARD_RATE_LIMIT_CALLS`               | `30`        | Límite de llamadas pagas por ventana (global) |
| `COST_GUARD_RATE_WINDOW_SECONDS`            | `3600`      | Ventana del rate global |
| `COST_GUARD_CALLER_RATE_LIMIT_CALLS`        | `3`         | Límite de llamadas pagas por número de origen |
| `COST_GUARD_CALLER_RATE_WINDOW_SECONDS`     | `3600`      | Ventana del rate por origen |
| `COST_GUARD_DEGRADATION_POLICY`             | `deterministic_review` | `deterministic_review` o `hard_block` |
| `COST_GUARD_STORE_FAILURE_POLICY`           | `fail_closed` | `fail_closed` o `fail_open`. `fail_open` permite la llamada paga sin tope cuando el almacén cae: usar solo de forma deliberada. Cualquier valor distinto de `fail_open` se trata como `fail_closed` |
| `COST_GUARD_ALERT_ENABLED`                  | `true`      | Notificación externa adicional (webhook N8N) del fail-closed. El evento estructurado `cost_guard_store_unavailable` se emite SIEMPRE |
| `COST_GUARD_SHARED_SECRET`                  | (vacío)     | Secreto compartido OBLIGATORIO del endpoint de reserva de n8n (header `X-Cost-Guard-Secret`). Vacío = endpoint cerrado (HTTP 401) y advertencia al arrancar. Fuente única en Docker: `.env` de la raíz |
| `TWILIO_AUTH_TOKEN`                         | (vacío)     | Auth token de Twilio. Con token se exige `X-Twilio-Signature` (HMAC-SHA1) en el webhook de voz; sin token el webhook responde 401 (fail-closed) y el arranque advierte `cost_guard_twilio_token_missing`. Cargar el valor real al activar el canal |

> Los costos unitarios son ESTIMACIONES configurables, no contabilidad exacta: acotan el gasto con
> un tope determinista y se ajustan por `.env`. El detalle operativo está en
> [`docs/operational-guide.md`](docs/operational-guide.md).
>
> **Detrás del proxy Nginx (stack Docker)**: el backend confía en `X-Forwarded-Proto` del proxy
> (`FORWARDED_ALLOW_IPS`, default `*` en `docker-compose.yml`) para reconstruir la URL pública
> `https://…` sobre la que Twilio calcula `X-Twilio-Signature`. Es seguro porque el puerto 8000 no
> se publica al host y Nginx sobreescribe el header. Al cargar `TWILIO_AUTH_TOKEN`, la URL pública
> configurada en Twilio debe coincidir exactamente con
> `https://<host>/api/v1/cost-guard/twilio/voice` (ver `docs/operational-guide.md` §11.6).

### 3. Generar los certificados TLS

El proyecto usa un proxy inverso Nginx con TLS 1.3 para el trafico externo.
Antes de levantar los servicios por primera vez, generar los certificados
auto-firmados:

**Linux / macOS:**
```bash
bash openssl/generate-certs.sh
```

**Windows (PowerShell):**
```powershell
.\openssl\generate-certs.ps1
```

Esto crea `openssl/mesa.crt` y `openssl/mesa.key`. Son certificados
auto-firmados validos por 365 dias. Volver a ejecutar el script para
regenerarlos cuando expiren (el script es idempotente).

> **Advertencia del navegador**: por ser un certificado auto-firmado, el
> navegador mostrara un aviso "Your connection is not private". Es seguro
> hacer clic en **Advanced → Proceed to localhost** en el entorno de
> desarrollo local.

### 4. Levantar todos los servicios

```bash
docker compose up -d
```

El compose levanta Nginx (puertos 80 y 443 — proxy TLS), PostgreSQL (5433),
Redis (6379), el backend FastAPI y N8N (5678). El backend y el frontend
NO publican puertos al host: todo el trafico HTTP/HTTPS pasa por Nginx.
Las migraciones Alembic se aplican automaticamente al iniciar el backend.

Verificar que todos los servicios estan healthy:
```bash
docker compose ps
```

### 5. Verificar salud del sistema

```bash
# Backend en funcionamiento (a traves del proxy Nginx en HTTPS)
curl -k https://localhost/api/v1/health

# Backend conectado a la base de datos
curl -k https://localhost/api/v1/health/db
```

Ambas respuestas deben devolver `{"status": "ok"}`.

> **Nota**: el flag `-k` (o `--insecure`) es necesario porque el certificado
> es auto-firmado. En produccion, con un certificado de CA reconocida, no
> hace falta.

### 6. Importar y activar el workflow N8N

1. Abrir `http://localhost:5678` (usuario: `admin`, contraseña: `admin`)
2. **Workflows → Import from file** → seleccionar `n8n/workflow.json`
3. Configurar las credenciales de Outlook, Twilio y Gemini en N8N
4. Activar el workflow con el toggle superior derecho

### Frontend

El frontend React se levanta como parte del compose y se accede a traves
del proxy Nginx en `https://localhost/`. El puerto 3000 no esta publicado
en el host; todo el trafico pasa por HTTPS.

Para desarrollo con hot reload (opcional, fuera del compose):
```bash
cd App/Frontend
npm install
npm run dev
# Disponible en http://localhost:3000 (acceso directo, sin TLS)
```

---

## Especificación Técnica

### Clasificación Automática
- **Modelo**: Google Gemini 2.5 Flash
- **Enfoque**: Híbrido (filtrado determinístico + LLM)
- **Documentación completa**: `docs/parameters_gemini.md` y `docs/ANEXO_H_Especificacion_Completa.md`
- **Prompt exacto**: `docs/prompt_gemini.txt`
- **Parámetros**: temperature=0.3, top_p=0.9, max_tokens=100, timeout=10s

### Reproducibilidad
El sistema puede ser replicado exactamente siguiendo:
1. Prompt: `docs/prompt_gemini.txt`
2. Parámetros: `docs/parameters_gemini.md`
3. Workflow: `n8n/workflow.json`
4. Código: `App/Backend/`
5. Configuración: `docker-compose.yml`

**Nota**: El corpus de validación está disponible bajo `data/corpus_evaluacion_pseudonimizado.csv` con 200 casos etiquetados.

## Hook anti-secretos (obligatorio al clonar)

El repo incluye un hook pre-commit en `.githooks/pre-commit` que bloquea commits con
API keys, claves privadas o archivos `.env` (en este proyecto ya se filtró una clave
real por commitear un `.env`). Activarlo una sola vez después de clonar:

```bash
git config core.hooksPath .githooks
```

Las claves reales van **solo** en `.env` (ignorado por git); al repo solo entran
plantillas `.env.example` con placeholders. Ante un falso positivo, agregar el
marcador `gitleaks:allow` en esa línea. Si además tenés [gitleaks](https://github.com/gitleaks/gitleaks)
instalado, el hook lo usa como capa extra de escaneo.

## Memoria compartida del proyecto (engram)

El directorio `.engram/` versiona la memoria técnica del proyecto (decisiones, bugs resueltos, convenciones) para que viaje con el código y sea recuperable por cualquier colaborador.

### Workflow

```bash
# Antes de hacer push — exportar la memoria nueva de ESTE proyecto:
engram sync
git add .engram && git commit -m "chore(engram): sync project memory"

# Después de clonar o hacer pull — importar la memoria al engram local:
engram sync --import
```

⚠️ **Nunca usar `engram sync --all`**: exportaría la memoria de TODOS los proyectos de la máquina a este repositorio. El comando sin flags filtra automáticamente por este proyecto.