## Context

Ver `proposal.md — Why` para la motivacion. El estado actual relevante:

- El repo ya tiene una convencion establecida de scripts pareados: `scripts/backup.sh` + `scripts/backup.ps1` y `openssl/generate-certs.sh` + `openssl/generate-certs.ps1`. Cada par implementa el mismo flujo por sistema operativo.
- `docker-compose.yml` fija `name: mesa_local`; servicios: nginx (80/443), postgres (5433), redis (6379), backend (interno), frontend (interno), n8n (5678). El backend ejecuta `alembic upgrade head` automaticamente al arrancar.
- `App/Backend/.env` es la ubicacion real del entorno, con plantilla en `App/Backend/.env.example`. El hook `.githooks/pre-commit` bloquea commits con secretos.
- `n8n/workflow.json` no tiene un `id` de workflow de nivel superior (solo ids de nodo), por lo que la importacion via CLI no es idempotente.
- No existe `Makefile` en el repo.

## Goals / Non-Goals

**Goals:**

- Un unico comando reproducible que lleve el stack de cero a sano, con fallo ruidoso ante prerrequisitos faltantes.
- Comportamiento equivalente en Linux/macOS y Windows, siguiendo la convencion de scripts pareados ya presente.
- Alias opcional con `make` que no introduce una segunda fuente de verdad.

**Non-Goals:**

- Importar `n8n/workflow.json` automaticamente (no es idempotente en el contrato actual de N8N).
- Gestionar secretos o credenciales de N8N/Outlook/Twilio/Gemini.
- Modificar `docker-compose.yml` o cualquier codigo bajo `App/**`.
- Reemplazar el camino manual documentado en el README; el comando unico es el camino recomendado, no el unico.

## Decisions

### D1 — Scripts pareados `.sh` + `.ps1` como base (Opcion A), Makefile como alias fino (Opcion B)

Se implementa primero `scripts/up.sh` y `scripts/up.ps1`, replicando la convencion de `scripts/backup.*` y `openssl/generate-certs.*`. El `Makefile` en la raiz es una capa fina que detecta el SO y delega en el script correspondiente (`up`, `down`, `ps`, `logs`, `health`).

- **Razon**: la logica vive en un solo lugar por SO; Make no reimplementa nada ni se convierte en un segundo punto de mantenimiento. Un operador sin `make` (tipico en Windows recien instalado) sigue teniendo el camino completo via `.ps1`.
- **Alternativas consideradas**: (a) Makefile unico con logica embebida — descartado porque fuerza `make` como prerrequisito obligatorio y mezcla bash de POSIX con deteccion de SO en un solo archivo fragil; (b) script Python unico multiplataforma — descartado porque agrega una dependencia de lenguaje que el repo no usa para operaciones de shell y rompe la convencion de scripts pareados ya establecida.

### D2 — Deteccion de placeholders sin exponer valores

El preflight lee `App/Backend/.env`, extrae `GEMINI_API_KEY` y `PSEUDONYMIZATION_ENCRYPTION_KEY`, y considera invalido un valor si esta ausente, vacio, o coincide con el valor placeholder de `.env.example`. La salida nombra la variable faltante, nunca su valor.

- **Razon**: el modo de fallo real no es "`.env` ausente" (obvio) sino "`.env` copiado de la plantilla sin reemplazar", que produce fallos tardios y confusos dentro del contenedor. Comparar contra la plantilla detecta ese caso de forma determinista.
- **Alternativas consideradas**: solo verificar no-vacio — descartado porque `changeme`/`your-key-here` pasan. Comparar hashes de secretos reales — imposible sin conocer los valores.

### D3 — Invocacion del generador de certificados existente, sin duplicar logica

Si `openssl/mesa.crt` o `openssl/mesa.key` faltan, `up.sh` invoca `bash openssl/generate-certs.sh` y `up.ps1` invoca `openssl/generate-certs.ps1`. Si existen, no se regeneran.

- **Razon**: la generacion de certificados ya es responsabilidad de un script idempotente y probado; duplicar la logica de OpenSSL en `up.*` crearia dos fuentes de verdad para SANs y validez.
- **Trade-off**: `up.*` depende de que el generador exista en su ruta actual. Mitigado con el mensaje de error accionable del preflight de certificados.

### D4 — Arranque sin `-p` y espera acotada sobre `docker compose ps`

Se ejecuta `docker compose up -d --build` sin `-p` (el nombre `mesa_local` ya esta fijado en `docker-compose.yml`) y se consulta `docker compose ps` en un bucle con timeout acotado hasta que los servicios reporten estado sano.

- **Razon**: pasar `-p` explicitamente duplicaria una decision de configuracion ya presente en el repo y podria divergir. El timeout acotado evita que el comando cuelgue indefinidamente si un servicio nunca llega a sano.
- **Alternativas consideradas**: `docker compose up --wait` — no esta garantizado en todas las versiones de Docker Compose v2 del entorno objetivo, por lo que el bucle explicito es mas portable.

### D5 — Verificacion de salud con `curl -k` y salida de URLs/recordatorios

Se verifica `curl -k https://localhost/api/v1/health` y `curl -k https://localhost/api/v1/health/db`. Al pasar, se imprimen `https://localhost/` y `http://localhost:5678` (admin/admin) mas el recordatorio manual de importar `n8n/workflow.json` y configurar credenciales de Outlook/Twilio/Gemini.

- **Razon**: `-k` es necesario porque el certificado es auto-firmado; el healthcheck de nginx valida el borde TLS, no solo el proceso backend. El recordatorio manual es la unica opcion correcta dado que la importacion CLI no es idempotente.
- **Trade-off**: `curl` se asume disponible; si no lo esta, la verificacion falla y el mensaje indica el endpoint, lo que hace el problema accionable.

## Risks / Trade-offs

- **[Deteccion de placeholder fragil ante cambios de `.env.example`]** -> el preflight compara contra los valores actuales de la plantilla; si la plantilla cambia sus placeholders, hay que ajustar la comparacion. Mitigacion: mantener el set de placeholders como constante unica nombrada en cada script.
- **[Timeout de salud mal calibrado]** -> en equipos lentos (build inicial de imagenes) el timeout podria agotarse antes de que el stack quede sano. Mitigacion: timeout generoso y mensaje que imprime `docker compose ps` para diagnosticar.
- **[Makefile no disponible en Windows por defecto]** -> un operador podria asumir que `make up` es obligatorio. Mitigacion: el README documenta `choco install make` y la alternativa directa `scripts/up.ps1`.
- **[Deriva entre `.sh` y `.ps1`]** -> dos implementaciones pueden divergir con el tiempo. Mitigacion: los specs fijan el mismo contrato observable para ambos y los objetivos del Makefile no contienen logica adicional.

## Migration Plan

1. Agregar `scripts/up.sh` y `scripts/up.ps1`.
2. Agregar `Makefile` en la raiz con los objetivos `up`, `down`, `ps`, `logs`, `health`.
3. Actualizar la seccion de despliegue local de `README.md`.
4. Rollback: eliminar los dos scripts y el `Makefile` y revertir el README; no hay estado persistente ni migracion de datos involucrada.