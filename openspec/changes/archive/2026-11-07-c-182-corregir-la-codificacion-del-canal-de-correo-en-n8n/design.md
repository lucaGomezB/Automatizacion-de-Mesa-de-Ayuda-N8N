## Context

Ver `proposal.md` - Why. Estado actual y restricciones que condicionan el enfoque. Todo lo siguiente
fue verificado por inspeccion read-only de la imagen pinneada `n8nio/n8n:2.11.2`.

- Pin de la imagen en `docker-compose.yml:135` (`n8n`) y `docker-compose.yml:382` (`n8n-corpus`). El
  nodo del workflow `Llega un email a Mesa de Ayuda` es `n8n-nodes-base.emailReadImap`,
  `typeVersion: 2`, `format: "simple"` (`n8n/workflow.json:16-23`); consume `@n8n/imap` a traves de
  `EmailReadImap/v2/EmailReadImapV2.node.js` (usa `getPartData`).
- Paquete empaquetado: `@n8n/imap` version `0.16.0` (file-based, dentro de la imagen). Ruta:
  `/usr/local/lib/node_modules/n8n/node_modules/.pnpm/@n8n+imap@file+packages+@n8n+imap/node_modules/@n8n/imap/dist/`.
- `imap-simple.js:86` (confirmado): `resolve(part_data_1.PartData.fromData(data, encoding));` - SIN
  charset.
- `part-data.js` (confirmado):
  - `PartData.fromData(data, encoding, charset)`: la rama `QUOTED-PRINTABLE` construye
    `new QuotedPrintablePartData(data, charset)`.
  - `QuotedPrintablePartData(data, charset)`: `const decoded = charset?.toUpperCase() === 'UTF-8' ?
    utf8.decode(qp.decode(data)) : qp.decode(data);` seguido de `Buffer.from(decoded)`.
  - Con `charset` `undefined` cae a `qp.decode(data)` (string cuyos code units son los bytes latin-1) y
    `Buffer.from(decoded)` lo re-codifica a UTF-8: de ahi el mojibake (`C3 B1` -> `Ã±`).
  - `8BIT`/`BINARY` -> `BinaryPartData(data, charset = 'utf-8')` (default correcto); `BASE64` no depende
    del charset.
  - `part` es un `MessagePart` con `params?: { charset?: string }` (`types.d.ts:17`), de modo que
    `part.params?.charset` es la fuente correcta del charset.
- El harness construye el correo en `scripts/corpus_ingest/ingest_via_n8n.py:1050-1065`
  (`build_email_message`; `msg.set_content(descripcion)` en la linea 1064, sin `cte`). La suite
  `scripts/corpus_ingest/test_ingest_via_n8n.py` corre offline (sin red).
- Los datos ya fueron reparados por `c-181`; el script
  `App/Backend/scripts/reparar_encoding_descripciones.py` sigue disponible para filas legacy.
- Governance HIGH: infraestructura / imagen pinneada. La aplicacion (build, edicion del compose,
  reinicio del stack) requiere aprobacion explicita del usuario.

## Goals / Non-Goals

**Goals:**

- Corregir la FUENTE del mojibake en el canal de correo, para TODOS los remitentes reales (Gmail,
  Outlook), no solo el corpus.
- Conservar la version pinneada `n8nio/n8n:2.11.2` (sin ampliar el blast radius del upgrade).
- Entregar el fix como imagen derivada reproducible, con parche versionado y verificacion reproducible.
- Blindar la ruta del corpus con `Content-Transfer-Encoding: base64` como defensa en profundidad.
- Dejar un rollback de un solo cambio.

**Non-Goals:**

- NO actualizar N8N (A2): evaluado y diferido (ver D3).
- NO cambiar `format` del nodo IMAP a `resolved` (A4): descartado (ver D5).
- NO re-ingestar casos ni tocar el corpus en disco; NO reparar datos (eso fue `c-181`).
- NO cambiar el modelo, la API, el esquema, el workflow exportado ni el frontend.
- NO construir la imagen ni reiniciar el stack en la fase de apply: son tareas MANUALES y gateadas.

## Decisions

### D1 - Causa raiz y punto exacto del parche (VERIFICADO)

**Decision: el defecto es `imap-simple.js:86`, donde el charset de la parte no se propaga a
`PartData.fromData`.** El parche cambia esa unica linea a:

```js
resolve(part_data_1.PartData.fromData(data, encoding, part.params?.charset));
```

Asi la rama `quoted-printable` entra por `utf8.decode(qp.decode(data))` (cuando el charset declarado es
UTF-8), que produce el string correcto. Alternativa considerada: parchear `part-data.js` para asumir
UTF-8 por defecto en la rama QP; descartada por ser menos precisa (ignora el charset declarado) y por
tocar mas logica.

### D2 - A1 recomendado: imagen derivada con parche quirurgico

**Decision: `docker/n8n/Dockerfile` con `FROM n8nio/n8n:2.11.2` que copia un archivo de parche
versionado, lo aplica sobre `@n8n/imap/dist/imap-simple.js` y falla el build si el archivo no existe o la
sustitucion no se aplica.** Los servicios `n8n` y `n8n-corpus` pasan a `build:` con el mismo contexto.
Se parchean AMBOS porque comparten el mismo tag pinneado y divergir la imagen seria una sorpresa
operativa; el costo es una sola construccion.

Rationale: es quirurgico, conserva la version validada de N8N, corrige a TODOS los emisores y no toca
datos. Alternativa considerada (editar el archivo vendored con `sed` inline en el Dockerfile): descartada
por menor trazabilidad y mayor fragilidad que un parche versionado. Riesgo residual: se parchea un
archivo vendored dentro de la imagen; la ruta depende del layout de `pnpm` de esa version. Mitigacion:
el Dockerfile valida la aplicacion del parche y falla el build ante cualquier desvio (cubre el
escenario "El build falla si el parche no aplica" del spec).

### D3 - A2 (upgrade de N8N): no adoptado, requiere research

**Decision: no upgradear como parte de `c-182`.** Verificado: el paquete publicado `@n8n/imap@0.32.1`
(latest en npm) es una implementacion DISTINTA - basada en `imapflow`, con `downloadText()` que hace
`content.toString('utf8')` y SIN `PartData.fromData`; no es un drop-in ni comparable linea por linea con
la version `0.16.0` empaquetada en la imagen. Si una version mas nueva de N8N ya incluye la correccion
del charset es una hipotesis no verificada en runtime y NO se asume. Un upgrade amplia el blast radius y
exigiria re-verificar todo el workflow. Queda como follow-up (ver Open Questions).

### D4 - A3 incluido como defensa en profundidad

**Decision: `build_email_message` pasa a `msg.set_content(descripcion, cte="base64")`.** Elimina la
dependencia de la rama `quoted-printable` en la ruta del corpus, es testeable offline (afirmar el header
y el round-trip) y es de bajo riesgo. NO reemplaza A1: los correos reales de Gmail/Outlook siguen
viajando como `quoted-printable` y solo A1 corrige esos emisores. Por eso se incluyen A1 + A3.

### D5 - A4 (format: "resolved"): descartado

**Decision: no usar `format: "resolved"`.** Cambia la forma del item del trigger y rompe
`normalizarRemitente`; descartado.

### D6 - Verificacion reproducible

**Decision: la verificacion es un envio real de un correo con cuerpo acentuado de mas de 78 bytes por el
flujo, seguido de la comprobacion de que la `descripcion_pseudonimizada` almacenada no presenta la firma
`Ã` y si conserva los acentos.** El mismo procedimiento contra la imagen pinneada sin el parche debe
mostrar el mojibake (escenario "La verificacion distingue imagen corregida de la pinneada"). El detector
reutilizable es `es_mojibake` de `App/Backend/scripts/reparar_encoding_descripciones.py` (`c-181`), que
es la autoridad de la firma. La verificacion es MANUAL (requiere stack en pie) y NO se ejecuta en apply.

### D7 - Capability

**Decision: crear la capability nueva `n8n-email-decoding` (comportamiento de decodificacion del canal de
correo en la imagen) y agregar un requisito `ADDED` a `corpus-n8n-ingest` (codificacion base64 del correo
del harness).** Se prefiere un `ADDED` en `corpus-n8n-ingest` a un `MODIFIED` porque el comportamiento
existente del harness no cambia: se agrega una garantia nueva sin alterar los requisitos vigentes
(correlacion exacta, `Message-ID` deterministico, metricas).

### D8 - Governance HIGH, aprobacion y rollback

**Decision: la aplicacion (construir la imagen derivada, editar `docker-compose.yml`, recrear el
servicio) requiere aprobacion explicita del usuario.** El rollback es revertir los servicios a
`image: n8nio/n8n:2.11.2` y recrearlos: sin migracion, sin restauracion de datos y sin cambios de
esquema. La fase de apply de este change deja la imagen sin construir y el stack sin tocar; solo escribe
el Dockerfile, el parche, el compose apuntando a `build:` y los tests del harness.

## Risks / Trade-offs

- El parche sobre un archivo vendored puede dejar de aplicar si cambia el layout de `pnpm` de la imagen
  -> Mitigacion: el Dockerfile valida el archivo y la sustitucion y ABORTA el build si no coinciden (el
  spec lo exige). Un cambio de version base obliga a revisar el parche.
- Divergencia entre la imagen operativa y la del corpus -> Mitigacion: ambos servicios construyen la
  MISMA imagen derivada.
- El harness con `cte="base64"` podria, en teoria, alterar el cuerpo -> Mitigacion: test de round-trip
  exacto (incluidos acentos) en la suite offline.
- Aplicar el cambio podria dejar el stack momentaneamente caido al recrear `n8n` -> Mitigacion: rollback
  de un solo cambio a la imagen pinneada; la operacion es MANUAL y gateada.
- La verificacion depende de un stack en pie y de credenciales IMAP/SMTP -> Mitigacion: se documenta como
  procedimiento manual con evidencia (fecha, digest de la imagen, resultado).

## Migration Plan

1. Preparacion (sin tocar el stack): escribir tests del harness (TDD), el Dockerfile derivado, el parche
   versionado y el compose apuntando a `build:`. Correr la suite offline del harness.
2. Con aprobacion explicita: `docker compose build n8n n8n-corpus` y recrear los servicios.
3. Con aprobacion explicita: ejecutar la verificacion reproducible (envio de mas de 78 bytes con acentos)
   y registrar la evidencia; opcionalmente, confirmar el mojibake contra la imagen pinneada.
4. Rollback: revertir `n8n`/`n8n-corpus` a `image: n8nio/n8n:2.11.2` y recrear. Sin migracion ni
   restauracion de datos.

## Open Questions

- Si una version futura de N8N incluye `@n8n/imap` con la decodificacion corregida y permite retirar la
  imagen derivada (A2), requiere verificacion en runtime. No cambia los specs, el enfoque ni las tareas
  de este change; queda como follow-up.
