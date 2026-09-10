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

Verificar:
```bash
docker --version
docker compose version
openssl version
```

> **Nota sobre Windows**: si `openssl` no esta disponible en el PATH, Git for Windows lo incluye en `C:\Program Files\Git\usr\bin\`. El script `openssl\generate-certs.ps1` lo detecta automaticamente.

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
| `DATABASE_URL`                    | Ya configurada en `.env.example` para el compose; no cambiar el host |

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