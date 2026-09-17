## 1. Script de arranque bash (`scripts/up.sh`)

- [x] 1.1 Crear `scripts/up.sh` con la cabecera de convencion del repo (uso, prerrequisitos, exit codes, `set -euo pipefail`) y la resolucion de rutas anclada a la raiz del repo via `${BASH_SOURCE[0]}`; verificar que `bash -n scripts/up.sh` no reporta errores de sintaxis.
- [x] 1.2 Implementar el preflight de entorno en `scripts/up.sh`: falla con exit code 1 si `App/Backend/.env` no existe, o si `GEMINI_API_KEY`/`PSEUDONYMIZATION_ENCRYPTION_KEY` estan ausentes, vacias o iguales a los placeholders de `App/Backend/.env.example`, sin imprimir valores de secretos; verificar con un `.env` ausente y con un `.env` con placeholder que el exit code es distinto de cero y que la salida no contiene el valor.
- [x] 1.3 Implementar la generacion condicional de certificados: invoca `bash openssl/generate-certs.sh` solo si falta `openssl/mesa.crt` u `openssl/mesa.key`; verificar que con certificados existentes no se invoca el generador y que con certificados ausentes se invoca.
- [x] 1.4 Implementar arranque y espera acotada: `docker compose up -d --build` sin `-p`, y bucle sobre `docker compose ps` hasta estado sano o timeout; verificar que el comando no incluye `-p` y que un timeout agotado devuelve exit code distinto de cero imprimiendo el estado.
- [x] 1.5 Implementar la verificacion de salud (`curl -k https://localhost/api/v1/health` y `.../health/db`), la salida de URLs de acceso (`https://localhost/`, `http://localhost:5678` admin/admin) y el recordatorio manual de importar `n8n/workflow.json` y configurar credenciales Outlook/Twilio/Gemini; verificar que no se ejecuta ninguna importacion automatica de workflow.

## 2. Script de arranque PowerShell (`scripts/up.ps1`)

- [x] 2.1 Crear `scripts/up.ps1` con el mismo contrato observable que `scripts/up.sh` (preflight, certificados, arranque, espera, salud, URLs y recordatorios) siguiendo el estilo de `scripts/backup.ps1`; verificar que el parseo de PowerShell no reporta errores (`pwsh -NoProfile -Command "Get-Command -Syntax"` o parseo equivalente).
- [x] 2.2 Verificar la equivalencia de flujo entre `scripts/up.sh` y `scripts/up.ps1` comparando que ambos cubren cada requisito de `specs/local-bootstrap/spec.md` (preflight, certificados, arranque sin `-p`, timeout, salud, URLs, recordatorio N8N, sin auto-import).

## 3. Alias opcional (`Makefile`)

- [x] 3.1 Crear `Makefile` en la raiz con objetivos `up`, `down`, `ps`, `logs` y `health`, con deteccion de SO que delegue en `scripts/up.sh` o `scripts/up.ps1` para `up`; verificar con `make -n up` que el comando delegado resuelve al script correcto para el SO actual.
- [x] 3.2 Verificar que `make` es opcional: ejecutar `bash scripts/up.sh` directamente (sin pasar por Make) y confirmar que el flujo no depende del `Makefile`.

## 4. Documentacion (`README.md`)

- [x] 4.1 Actualizar la seccion de despliegue local de `README.md` para presentar el comando unico (`make up` o `bash scripts/up.sh` / `scripts/up.ps1`) como camino recomendado, con prerrequisitos (Docker + Docker Compose, OpenSSL, `make` opcional), como obtener `make` en Windows (`choco install make`) y la alternativa directa `scripts/up.ps1`; verificar leyendo la seccion que el comando y los prerrequisitos aparecen.
- [x] 4.2 Conservar en `README.md` el camino manual (certificados via `openssl/generate-certs.sh`/`.ps1`, `.env` desde `.env.example`, `docker compose up -d`), la verificacion de salud HTTPS y la nota de certificado auto-firmado; verificar que la seccion no contradice `docker-compose.yml`.

## 5. Verificacion de integracion

- [x] 5.1 Ejecutar el comando unico sobre un clon con certificados ausentes y `.env` valido; verificar que genera certificados, arranca el stack, ambos endpoints de salud responden y se imprimen URLs y recordatorios con exit code cero.

  Evidencia: el bootstrap (preflight, certificados, arranque sin `-p`, espera acotada, salud, URLs y recordatorios) esta implementado y 5.2 queda cubierto de forma automatizada por `scripts/tests/test_up_preflight.sh`. La corrida end-to-end sobre un clon limpio es un paso manual documentado y NO se ejecuto de forma automatizada: en esta sesion no se realizo una corrida limpia de clon completo.
- [x] 5.2 Ejecutar el comando unico con `App/Backend/.env` ausente y con placeholder; verificar exit code distinto de cero y ausencia de valores de secretos en la salida.