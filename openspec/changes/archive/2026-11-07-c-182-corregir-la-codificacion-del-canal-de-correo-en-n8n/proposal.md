## Why

Los correos que ingresan por el trigger IMAP de N8N se persisten con mojibake (doble codificacion)
cuando el cuerpo viaja como `quoted-printable` (lineas de mas de 78 bytes): los acentos se guardan como
`Ã±`, `Ã³`, etc. La causa raiz es que el paquete `@n8n/imap` incluido en la imagen pinneada
`n8nio/n8n:2.11.2` llama `PartData.fromData(data, encoding)` sin pasar el charset de la parte, de modo
que la rama `quoted-printable` re-codifica los bytes latin-1 como UTF-8. El change `c-181` ya reparo los
datos corruptos; `c-182` corrige la FUENTE para que los correos nuevos no se corrompan. Solo el canal
`correo electronico` esta afectado; los canales web y telefonia no pasan por `@n8n/imap`.

## What Changes

- **Fix en la imagen N8N (A1, recomendado):** un Dockerfile derivado (`docker/n8n/Dockerfile`, `FROM
  n8nio/n8n:2.11.2`) que aplica un parche quirurgico versionado a
  `@n8n/imap/dist/imap-simple.js` para pasar `part.params?.charset` a `PartData.fromData`; los servicios
  `n8n` y `n8n-corpus` de `docker-compose.yml` pasan a construir esa imagen. Se conserva la version
  pinneada de N8N.
- **Defensa en profundidad del harness (A3):** `scripts/corpus_ingest/ingest_via_n8n.py` construye el
  correo de ingesta del corpus con `cte="base64"`, de modo que la ruta del corpus no dependa de la rama
  `quoted-printable` defectuosa.
- **Documentacion y verificacion:** un runbook que documenta el parche, la verificacion reproducible
  (envio de un cuerpo acentuado de mas de 78 bytes) y el rollback.
- Fuera de alcance: el upgrade de N8N (A2, evaluado y diferido) y `format: "resolved"` (A4, descartado);
  el detalle esta en `design.md`.
- Sin cambios en el modelo, la API, el esquema de base ni el frontend.

## Capabilities

### New Capabilities
- `n8n-email-decoding`: decodificacion con el charset declarado de las partes `quoted-printable` del
  canal de correo en la imagen N8N, entregada como imagen derivada reproducible, verificable y reversible.

### Modified Capabilities
- `corpus-n8n-ingest`: el harness de ingesta del corpus codifica el correo con
  `Content-Transfer-Encoding: base64` (defensa en profundidad), preservando el `Message-ID`
  deterministico y el round-trip exacto del cuerpo.

## Impact

- `docker-compose.yml`: los servicios `n8n` (linea 135) y `n8n-corpus` (linea 382) pasan de `image:`
  a `build:` de la imagen derivada.
- Nuevo `docker/n8n/Dockerfile` mas el parche versionado de `@n8n/imap`.
- `scripts/corpus_ingest/ingest_via_n8n.py` (`build_email_message`, linea 1064) y su suite de tests
  `scripts/corpus_ingest/test_ingest_via_n8n.py`.
- `docs/`: runbook de la correccion (causa, parche, verificacion, rollback).
- Governance HIGH (infraestructura / imagen N8N pinneada): construir la imagen derivada, editar el
  compose y reiniciar el stack requiere aprobacion explicita del usuario antes de aplicarse. El plan de
  rollback es revertir a la imagen pinneada `n8nio/n8n:2.11.2` (sin migracion ni restauracion de datos).
- La reparacion de datos de `c-181` ya se ejecuto; el script
  `App/Backend/scripts/reparar_encoding_descripciones.py` permanece disponible para cualquier fila legacy
  corrupta.
