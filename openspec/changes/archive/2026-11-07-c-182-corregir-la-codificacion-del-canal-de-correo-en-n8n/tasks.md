## 1. Linea base y RED del harness (TDD — defensa en profundidad)

- [x] 1.1 Ejecutar la linea base `cd scripts/corpus_ingest; python -m pytest test_ingest_via_n8n.py -q` y registrar el conteo de tests verdes (safety net; no debe haber fallos preexistentes).
- [x] 1.2 Agregar en `scripts/corpus_ingest/test_ingest_via_n8n.py` un test que construya `ivn.build_email_message(...)` y afirme `msg["Content-Transfer-Encoding"].lower() == "base64"`; confirmar que RED falla hoy (la linea 1064 no pasa `cte`).
- [x] 1.3 Agregar el caso triangulado de round-trip: con `descripcion` acentuada (por ejemplo `"Reunion de red y senal con conexion"` con tildes y enies) afirmar que el cuerpo decodificado del mensaje es identico a la descripcion; confirmar RED.

## 2. GREEN del harness (defensa en profundidad)

- [x] 2.1 Cambiar `build_email_message` (`scripts/corpus_ingest/ingest_via_n8n.py:1064`) a `msg.set_content(descripcion, cte="base64")`.
- [x] 2.2 Ejecutar `cd scripts/corpus_ingest; python -m pytest test_ingest_via_n8n.py -q` y confirmar GREEN con los dos casos (header base64 y round-trip acentuado).
- [x] 2.3 Confirmar que `test_build_email_message_sets_deterministic_message_id` sigue verde (la correlacion por `Message-ID` no se altera).
- [x] 2.4 Escribir en el retorno del apply la tabla de evidencia del ciclo TDD (archivo de test, capa, safety net, RED, GREEN, triangulacion, refactor).

## 3. Imagen N8N derivada y parche (artefactos versionados)

- [x] 3.1 Crear `docker/n8n/Dockerfile` con `FROM n8nio/n8n:2.11.2` que copie y aplique el parche sobre `@n8n/imap/dist/imap-simple.js`; verificar que el build falla si la ruta del archivo no existe o la sustitucion no se aplica (el Dockerfile valida ambos casos y aborta el build).
- [x] 3.2 Crear el parche versionado que cambia la linea 86 a `resolve(part_data_1.PartData.fromData(data, encoding, part.params?.charset));`; verificar que aplica limpio contra el `@n8n/imap/dist/imap-simple.js` extraido de la imagen pinneada (por ejemplo con `docker run --rm --entrypoint sh n8nio/n8n:2.11.2 -c "cat <path>"` y un `patch --dry-run`).
- [x] 3.3 Editar `docker-compose.yml` para que `n8n` (linea 135) y `n8n-corpus` (linea 382) usen `build:` de `docker/n8n` en lugar de `image: n8nio/n8n:2.11.2`; verificar con `docker compose config` que la definicion resuelve sin ejecutar build ni up.

## 4. Documentacion

- [x] 4.1 Documentar la correccion (causa raiz, ruta exacta del parche, comando de build, procedimiento de verificacion y rollback) en un runbook versionado; si se amplia `docs/runbook-reparacion-encoding-descripciones.md`, actualizar su seccion 8 (hoy dice que la causa es `c-182`, fuera de alcance).
- [x] 4.2 Declarar que `App/Backend/scripts/reparar_encoding_descripciones.py` (`c-181`) permanece disponible para reparar cualquier fila legacy corrupta.

## 5. Verificacion manual de la correccion (NO ejecutada en apply; requiere aprobacion y stack en pie)

- [x] 5.1 MANUAL/gated: construir la imagen derivada (`docker compose build n8n n8n-corpus`) y confirmar dentro de la imagen que el parche quedo aplicado (`docker run --rm --entrypoint sh <img> -c "grep -n 'part.params' <path>"`).
- [x] 5.2 MANUAL/gated: recrear el servicio `n8n` con la imagen derivada y confirmar que el stack queda sano (`docker compose ps`).
- [x] 5.3 MANUAL/gated: enviar por el flujo real un correo con cuerpo acentuado de mas de 78 bytes; verificar que la `descripcion_pseudonimizada` almacenada no contiene `Ã` (por ejemplo `es_mojibake` de `c-181` sobre el valor) y conserva los acentos correctos.
- [x] 5.4 MANUAL/gated: registrar la evidencia (fecha, digest de la imagen derivada, resultado de la verificacion y, si se ejecuto, del control contra la imagen pinneada).

## 6. Rollback

- [x] 6.1 (verificada el 2026-11-12 sobre el stack local; evidencia en la sección 5.1 de `docs/runbook-fix-encoding-correo-n8n.md`) MANUAL/gated: definir y documentar el rollback (revertir `n8n`/`n8n-corpus` a `image: n8nio/n8n:2.11.2` y recrear); verificar que el stack vuelve a la imagen upstream sin migracion ni restauracion de datos.
