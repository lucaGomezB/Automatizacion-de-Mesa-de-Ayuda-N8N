## 0. Safety net y preparación

- [x] 0.1 Correr la suite existente y capturar baseline (esperado: 112 passed / 1 skipped / 1 xfailed). Si algo falla → reportar como falla preexistente, no arreglar.
- [x] 0.2 Correr `pytest tests/test_n8n_workflow.py -v` y confirmar que los tests estructurales de C-04 pasan contra el JSON actual (baseline del workflow). Reutilizar los helpers `load_workflow()` e `index_nodes()` ya presentes.
- [x] 0.3 Confirmar contra el JSON actual los nombres/tipos exactos de los triggers (`microsoftOutlookTrigger`, `twilioTrigger`), del normalizador ("Normalizar entrada del incidente") y de los `httpRequest` de persistencia, para cablear los nodos nuevos por `type`/`name` (no por índice).

## 1. Trigger Webhook del formulario web (spec: Trigger Webhook para el formulario web)

- [x] 1.1 RED: test `test_web_webhook_trigger_exists` que afirma la presencia de un nodo `type == n8n-nodes-base.webhook` con `httpMethod == "POST"` y `path` no vacío. Debe fallar (hoy no existe).
- [x] 1.2 GREEN: agregar al JSON el nodo `webhook` del formulario web (`httpMethod: POST`, `path: "incidente-web"`, `responseMode: responseNode`). Test pasa.
- [x] 1.3 RED: test `test_web_webhook_marks_canal_web` que afirma que la salida del webhook se marca con `canal_raw = "web"` (vía un nodo `set`/`code` intermedio o en el propio normalizador). Falla.
- [x] 1.4 GREEN: cablear el webhook web → marcado `canal_raw = "web"` → nodo de normalización. Test pasa.
- [x] 1.5 TRIANGULATE: test `test_web_webhook_wired_to_normalizer` que verifica, en `connections`, que la ruta del webhook alcanza "Normalizar entrada del incidente".
- [x] 1.6 REFACTOR: extraer en el test las constantes del nodo webhook (nombre, path); correr suite → verde.

## 2. Identificación explícita de canal por trigger (spec: triggers de correo / telefonía identificados + convergencia)

- [x] 2.1 RED: test `test_each_trigger_marks_canal_raw` que afirma que el flujo de correo propaga `canal_raw = "correo"`, el de web `"web"` y el de telefonía `"telefonia"` antes de la normalización. Falla si algún canal no queda marcado explícitamente.
- [x] 2.2 GREEN: asegurar el marcado explícito de `canal_raw` por canal (correo y telefonía ya lo marcan en C-04; agregar el de web). Test pasa.
- [x] 2.3 TRIANGULATE: test `test_three_channels_converge_on_normalizer` que verifica en `connections` que los tres caminos (correo, web, telefonía) alcanzan el normalizador antes del `httpRequest` de persistencia.
- [x] 2.4 REFACTOR: centralizar en el test el mapa {trigger → canal_raw esperado}; suite → verde.

## 3. Notificación al usuario post-registro (spec: notificación al usuario post-registro por canal)

- [x] 3.1 RED: test `test_web_confirmation_node_exists` que afirma la presencia de un nodo `respondToWebhook` cableado tras el `httpRequest` de persistencia del flujo web, con un cuerpo que referencia el identificador del incidente. Falla.
- [x] 3.2 GREEN: agregar el nodo `respondToWebhook` con `{ incidente_id, mensaje }` cableado desde la salida del `httpRequest`. Test pasa.
- [x] 3.3 RED: test `test_email_confirmation_node_exists` que afirma la presencia de un nodo de envío de correo (`microsoftOutlook`) de confirmación cableado tras la persistencia del flujo de correo. Falla.
- [x] 3.4 GREEN: agregar el nodo de correo de confirmación cableado desde la salida del `httpRequest` de correo. Test pasa.
- [x] 3.5 TRIANGULATE: test `test_notification_only_after_successful_creation` que verifica que los nodos de notificación cuelgan de la salida del `httpRequest` (alta exitosa) y NO de las ramas false de los `if` (validación fallida / revisión).
- [x] 3.6 TRIANGULATE: test `test_notification_does_not_block_audit` que verifica que la salida del `httpRequest` se ramifica tanto a notificación como a auditoría (ambas cuelgan en paralelo).
- [x] 3.7 REFACTOR: nombrar claramente los nodos de notificación; suite → verde.

## 4. Registro de auditoría con retención de 30 días (spec: registro de auditoría)

- [x] 4.1 RED: test `test_audit_node_exists` que afirma la presencia de un nodo de auditoría (`code` JS, por nombre p. ej. "Registro de auditoria") cableado tras la persistencia. Falla.
- [x] 4.2 GREEN: agregar el nodo `code` de auditoría que arme `{incidente_id, canal_origen, timestamp, categoria, confianza, resultado, retencion_dias: 30}`. Test pasa.
- [x] 4.3 RED: test `test_audit_node_has_required_metadata` que verifica que el `jsCode` del nodo de auditoría referencia `incidente_id`/`id`, `canal_origen`, `timestamp`, `categor`, `confianza` y `resultado`. Falla hasta completar el objeto.
- [x] 4.4 GREEN: completar los campos de metadatos en el `jsCode`. Test pasa.
- [x] 4.5 RED: test `test_audit_node_no_pii` que verifica que el `jsCode` del nodo de auditoría NO emite la `descripcion` cruda (no la incluye en el objeto de log). Falla si la incluye.
- [x] 4.6 GREEN: asegurar que el objeto de auditoría excluye `descripcion`/PII (solo metadatos y referencias). Test pasa.
- [x] 4.7 TRIANGULATE: test `test_audit_retention_30_days_declared` que verifica que la retención de 30 días está declarada (campo `retencion_dias: 30` en el `jsCode` o mención explícita "30" + "auditor"/"retencion"). 
- [x] 4.8 REFACTOR: documentar en comentario del `jsCode` el contrato del evento de auditoría y la exclusión de PII; suite → verde.

## 5. Cierre estructural y no regresión (spec: estructura de canales y cierre de ciclo verificable)

- [x] 5.1 TRIANGULATE: test `test_workflow_still_inactive` que ratifica `active == false` tras todos los cambios (no se activa desde el repo).
- [x] 5.2 TRIANGULATE: confirmar que los tests estructurales de C-04 (normalización, validación, ruteo, endpoint, xfail PII) siguen verdes sin regresiones tras agregar los nodos nuevos.
- [x] 5.3 REFACTOR: revisar duplicación en los asserts de cableado (helpers para recorrer `connections`); suite → verde.
- [x] 5.4 Correr la suite completa: nuevos tests verdes + baseline sin regresiones (≥ 112 passed previos + nuevos; xfail PII de C-04 intacto).

## 6. Documentación

- [x] 6.1 Actualizar `docs/n8n-workflow-guide.md`: agregar el trigger `webhook` web (ruta `POST /webhook/incidente-web`), la equivalencia "Outlook trigger ≈ IMAP" (Decisión 1), y la tabla de los tres canales con su `canal_raw`.
- [x] 6.2 Documentar los nodos de notificación por canal (confirmación web, correo de confirmación, nota sobre telefonía) y el nodo de auditoría (campos, exclusión de PII, retención de 30 días y recomendación de destino del log).
- [x] 6.3 Registrar las Open Questions resueltas durante el apply (notificación telefónica, ramas auditadas, destino del log, auth del webhook) para alimentar el Anexo E de la tesis (C-10).

## 7. Verificación funcional manual (entorno de pruebas — requiere Docker N8N vivo)

> Verificación ejecutada 2026-06-11. Entorno: N8N 2.25.7 (latest), backend FastAPI healthy en
> puerto 8000, PostgreSQL 15.5, Redis 7.2. N8N corre con `BACKEND_URL=http://backend:8000`.
> Detalles completos en `docs/n8n-workflow-guide.md` (sección Verificación C-05).

- [x] 7.1 Importar `Automatizacion_Mesa_de_Ayuda.json` en N8N Docker con `BACKEND_URL` configurado.
      → `n8n import:workflow --input=/data/Automatizacion_Mesa_de_Ayuda.json` → "Successfully imported 1 workflow."
      → Confirmado vía API pública: ID P7w2iELDu7O3e8B0, 19 nodos, active=false. VERIFICADO.
- [x] 7.2 Canal web: `POST` al webhook `incidente-web` — VERIFICADO POST-FIX (D-1..D-5 corregidos, 2026-06-11).
      → Verificación original (C-05 apply): BLOQUEADO POR DEFECTO #1 (`const item = .item;`, SyntaxError).
      → POST-FIX (sesión de corrección): workflow temp `TEST-canal-web-D1` con fixes D-1..D-4 aplicados.
        Ejecución #19: 5 nodos ejecutados exitosamente — `Webhook formulario web` → `Marcar canal web`
        → `Normalizar entrada del incidente` → `La informacion esta OK` (rama true) → `HTTP POST a MTM-SRU`.
        Backend respondió HTTP 201: incidente_id=15, sector={nombre: "Sistemas"}, requiere_revision_humana=false.
        D-1 verificado: `Marcar canal web` corre sin SyntaxError (usa `$input.item`).
        D-2 verificado: normalizer sintetiza `confianza=1.0` para canal web → IF toma rama true.
        Fix adicional: extracción de `webBody` del campo `item.json.body` (body anidado del webhook).
- [x] 7.3 Canal correo: PARCIAL — trigger Outlook requiere credenciales corporativas no disponibles.
      → Backend verificado directamente: POST con descripción de correo → 201, sector Soporte Técnico
        (incidente_id: 9, etapa: deterministic, confianza 0.9999). Pipeline backend verificado.
      → El trigger `microsoftOutlookTrigger` y el validador de correo no se pudieron ejecutar
        end-to-end sin credenciales OAuth2. Se documenta alcance real.
- [x] 7.4 Canal telefonía: PARCIAL — `twilioTrigger` requiere credenciales Twilio + AI Agent requiere credenciales LLM.
      → Backend verificado: POST con descripción de transcripción → 201 vía Gemini (incidente_id: 10,
        etapa: gemini, confianza 0.9, sector Soporte Técnico). Pipeline backend OK.
      → DEFECTO #2 (latente): IF node (`La informacion esta OK`) chequea `$json.confianza >= 0.70`,
        pero para canales correo y web `confianza` no está seteado antes del IF (solo telefonia
        lo setea en `Se verifica lo que trajo la IA`). Correo y web siempre irían a rama false.
- [x] 7.5 Auditoría: VERIFICADO POST-FIX (D-3 + D-4 corregidos, 2026-06-11).
      → Verificación original (C-05 apply): PARCIAL — D-3/D-4 latentes; ejecución bloqueada por D-1.
      → POST-FIX (sesión de corrección):
        D-3 verificado (estructural + runtime): `Registro de auditoria` usa `item.sector?.nombre` en
          lugar de `item.categoria`. El response del backend de la ejecución #19 confirma que
          `sector: {id:1, nombre:"Sistemas"}` está disponible; el fix lee `sector?.nombre` correctamente.
        D-4 verificado (estructural + runtime): el nodo auditoría lee `canal_origen` y `confianza`
          desde `$('Normalizar entrada del incidente').item.json` (upstream). La ejecución #19
          confirma que el normalizador produjo `canal_origen='web'` / `confianza=1.0`; estos valores
          habrían sido `null` en el response body del HTTP POST.
        PII exclusion: CORRECTO — `descripcion` no aparece en el evento de auditoría (sin cambios).
        Rama de rechazo: cableada desde IF false branch → Registro de auditoria (estructura confirmada;
          verificación funcional de rama de rechazo pendiente — requiere workflow completo activo con
          validador de datos que emita `es_valido=false`).
      → Suite pytest: 58 tests pasando (8 tests D-1..D-4 agregados y verdes, 0 regresiones).
- [x] 7.6 `active: false` confirmado en el JSON versionado (`Automatizacion_Mesa_de_Ayuda.json`).
      → python: `wf['active'] == False` → True. El workflow de producción no quedó activado.

### Defectos encontrados en C-05 — CORREGIDOS en sesión post-apply (2026-06-11)

| # | Nodo | Severidad | Descripción original | Estado |
|---|------|-----------|---------------------|--------|
| D-1 | Marcar canal web | CRÍTICO | `const item = .item;` — SyntaxError JS. Canal web inutilizable. | CORREGIDO → `const item = $input.item;` |
| D-2 | La informacion esta OK (IF) | ALTO | Correo/web nunca seteaban `confianza`; siempre iban a rama false. | CORREGIDO → normalizador sintetiza `confianza` desde `es_valido` |
| D-3 | Registro de auditoria | MEDIO | Leía `item.categoria` pero backend responde `sector.nombre`. | CORREGIDO → `item.sector?.nombre` |
| D-4 | Registro de auditoria | MEDIO | `canal_origen` se perdía tras HTTP POST (response body no lo incluye). | CORREGIDO → lee de `$('Normalizar entrada del incidente').item.json.canal_origen` |
| D-5 | Normalizar entrada del incidente | BAJO | Body del webhook web llegaba como `item.json.body` (objeto anidado), no como campos planos; `descripcion` resultaba `[object Object]`. | CORREGIDO → declara `webBody` antes del bloque if-else y usa `webBody.descripcion` / `webBody.prioridad` para canal web. |

Suite pytest post-fix: **58 passed / 1 xfailed / 0 failed** (8 tests D-1..D-4 añadidos, baseline 50/1/0).

## 8. Cierre

- [x] 8.1 `openspec validate --strict --changes c-05-n8n-channel-triggers` (o `openspec validate --changes`) sin errores.
- [x] 8.2 Elevar al usuario las decisiones de governance MEDIO pendientes de confirmación (Decisiones 2, 3 y 4 de design.md: notificación telefónica, ramas auditadas, destino/retención del log) antes de archivar.
