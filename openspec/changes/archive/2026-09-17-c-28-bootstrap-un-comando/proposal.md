## Why

Levantar el stack completo hoy exige recordar y ejecutar manualmente varios pasos dispersos: verificar `App/Backend/.env`, generar los certificados TLS si faltan, correr `docker compose up -d --build`, esperar a que los servicios queden sanos y verificar la salud por HTTPS. Este conocimiento vive solo en el README y en la cabeza del operador, lo que produce arranques incompletos (por ejemplo, `.env` ausente o con placeholders sin reemplazar) que fallan más tarde con errores confusos. Un unico comando de arranque reproduce el camino feliz de forma determinista y falla ruidosamente cuando falta un prerrequisito.

## What Changes

- Agregar un par de scripts de arranque que siguen la convencion ya existente de scripts pareados `.sh` + `.ps1` (como `scripts/backup.sh` + `scripts/backup.ps1` y `openssl/generate-certs.sh` + `.ps1`):
  - `scripts/up.sh` (Linux/macOS, bash)
  - `scripts/up.ps1` (Windows, PowerShell)
- Ambos scripts implementan el mismo comportamiento:
  - Preflight que falla con exit code distinto de cero si `App/Backend/.env` no existe, o si `GEMINI_API_KEY` / `PSEUDONYMIZATION_ENCRYPTION_KEY` estan vacias o siguen siendo placeholders. Nunca imprime valores de secretos.
  - Generacion de certificados TLS si `openssl/mesa.crt` u `openssl/mesa.key` faltan, invocando el generador existente (`openssl/generate-certs.sh` o `openssl/generate-certs.ps1`).
  - Arranque del stack con `docker compose up -d --build`, sin pasar `-p` (el nombre de proyecto esta fijado a `mesa_local` en `docker-compose.yml`).
  - Espera acotada (timeout) hasta que los servicios queden sanos segun `docker compose ps`.
  - Verificacion de salud con `curl -k https://localhost/api/v1/health` y `curl -k https://localhost/api/v1/health/db`.
  - Impresion de las URLs de acceso (`https://localhost/`, `http://localhost:5678` admin/admin) y un recordatorio manual explicito para importar `n8n/workflow.json` y configurar las credenciales de Outlook/Twilio/Gemini en N8N.
- Agregar un `Makefile` en la raiz como conveniencia OPCIONAL con objetivos finos (`up`, `down`, `ps`, `logs`, `health`) que detectan el sistema operativo y delegan en el script correspondiente. Make NO reemplaza a los scripts; es un alias.
- Actualizar `README.md` para documentar el camino de un solo comando, sus prerrequisitos (incluyendo como obtener `make` en Windows: `choco install make`, o ejecutar el `.ps1` directamente sin make).

Fuera de alcance explicito:
- Auto-import de `n8n/workflow.json`: el JSON no tiene `id` de workflow de nivel superior (solo ids de nodo), por lo que `n8n import:workflow` no es idempotente y crearia workflows duplicados en cada ejecucion. El script solo imprime el recordatorio manual.
- Automatizar secretos/credenciales: imposible sin hardcodear claves, lo que el hook anti-secretos bloquea.
- Modificar `docker-compose.yml`.
- Cualquier cambio de codigo de producto bajo `App/**`.
- `docs/Tesis/**`.

## Capabilities

### New Capabilities

- `local-bootstrap`: arranque local del stack completo mediante un unico comando, con preflight de entorno, generacion de certificados TLS cuando faltan, arranque e espera de salud de los servicios, verificacion de endpoints de salud y salida de URLs/recordatorios. Cubre los scripts pareados `.sh`/`.ps1` y el `Makefile` opcional como alias.

### Modified Capabilities

- `project-documentation`: el requisito del README de despliegue local cambia para documentar el comando unico de arranque y sus prerrequisitos (incluyendo como obtener `make` en Windows), manteniendo el detalle manual y las URL de salud HTTPS.

## Impact

- **Nuevos archivos**: `scripts/up.sh`, `scripts/up.ps1`, `Makefile`.
- **Documentacion**: `README.md` (seccion de despliegue local).
- **Sin cambios de producto**: no se toca `App/**`, ni `docker-compose.yml`, ni `docs/Tesis/**`, ni migraciones, ni contratos de API.
- **Gobernanza**: MEDIA (herramientas de desarrollo, sin efecto sobre una capacidad de producto).
- **Dependencias**: Docker + Docker Compose, bash o PowerShell, OpenSSL (ya requerido para certificados), `curl`. `make` es opcional.