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

> Estas tareas requieren N8N 1.62 + backend FastAPI + PostgreSQL levantados; quedan documentadas y pendientes de entorno (como las 8.x de C-04).

- [ ] 7.1 Importar `Automatizacion_Mesa_de_Ayuda.json` en una instancia N8N 1.62 de pruebas con `BACKEND_URL` configurado.
- [ ] 7.2 Canal web: hacer `POST` al webhook `incidente-web` con un JSON de formulario y observar `201` del backend + respuesta de confirmación con el número de incidente.
- [ ] 7.3 Canal correo: disparar un correo de prueba y observar el alta + el correo de confirmación al usuario.
- [ ] 7.4 Canal telefonía: enviar una transcripción simulada al `twilioTrigger` y observar el ruteo por confianza y el cierre del ciclo.
- [ ] 7.5 Verificar que el nodo de auditoría registra los metadatos (sin PII) de cada ejecución.
- [ ] 7.6 Confirmar que `active` permanece `false` en el JSON versionado y registrar los resultados de la verificación en la guía.

## 8. Cierre

- [x] 8.1 `openspec validate --strict --changes c-05-n8n-channel-triggers` (o `openspec validate --changes`) sin errores.
- [x] 8.2 Elevar al usuario las decisiones de governance MEDIO pendientes de confirmación (Decisiones 2, 3 y 4 de design.md: notificación telefónica, ramas auditadas, destino/retención del log) antes de archivar.
