## 0. Preparación y red de seguridad

- [x] 0.1 Ejecutar la suite estructural de línea base desde `App/Backend/`: `pytest tests/test_n8n_workflow.py -q`. Registrar el conteo observado (baseline real sobre el workflow de c-39: 107 passed + 1 xfailed; 108 funciones `test_`) y confirmar que no hay fallos preexistentes.
- [x] 0.2 Confirmar el punto de partida sobre el `n8n/workflow.json` resultante de c-39 (campo de timestamp de ingreso presente) y que no se redefine el contrato de timing. Verificación: diff de `n8n/workflow.json` contra el estado de c-39 sin tocar el campo de c-39.

## 1. Cierre de ramas terminales del webhook web (N8N-WEBHOOK-003)

- [x] 1.1 RED: agregar en `App/Backend/tests/test_n8n_workflow.py` los tests que verifican que `Es correo?` `main#1` alcanza la guarda `Es web?`, que `Es web?` `main#0` alcanza el `respondToWebhook` de cierre, y que las ramas de rechazo de `Entrada valida`, error del POST y revisión humana llegan a un `respondToWebhook` para el canal web. Verificación: los tests fallan contra el workflow actual.
- [x] 1.2 GREEN: agregar el nodo `if` `Es web?` (condición `$('Normalizar entrada del incidente').item.json.canal_origen == 'web'`) y el nodo `respondToWebhook` `Respuesta web de cierre` (`respondWith: json`, `options.responseCode: 200`, cuerpo con `incidente_id: null` y `resultado: 'sin_alta'`); cablear `Es correo?` `main#1` -> `Es web?` -> `Respuesta web de cierre`. Verificación: los tests de 1.1 pasan.
- [x] 1.3 TRIANGULATE: agregar un test que verifique que la guarda `Es web?` no emite respuesta web para un canal distinto de `web`. Verificación: el test pasa y no rompe `test_c29_webhook_response_node_has_reachable_responder`.

## 2. Destinatario de confirmación por correo (N8N-EMAIL-002)

- [x] 2.1 RED: agregar tests que verifican que el nodo normalizador emite `remitente`, que `toRecipients` de `Correo de confirmacion al usuario` referencia `Normalizar entrada del incidente`, y que ni el cuerpo del POST ni el código de auditoría contienen `remitente`. Verificación: los tests fallan contra el workflow actual.
- [x] 2.2 GREEN: en el `jsCode` del normalizador agregar `remitente: item.json.remitente || item.json.from || null`; cambiar `toRecipients` del nodo de confirmación a `={{ $('Normalizar entrada del incidente').item.json.remitente || '' }}`. Verificación: los tests de 2.1 pasan y `test_email_confirmation_node_exists` sigue verde.

## 3. Confirmación telefónica sin nodo de correo (N8N-PHONE-002)

- [x] 3.1 RED: agregar tests que verifican que las salidas telefonía y fallback del switch no alcanzan `Correo de confirmacion al usuario`, y que la salida correo sí lo conserva. Verificación: los tests de telefonía/fallback fallan contra el cableado actual.
- [x] 3.2 GREEN: eliminar las conexiones de `Rutear por canal de origen` `index 2` (Telefonía) e `index 3` (Otros) hacia `Correo de confirmacion al usuario`, conservando la salida `index 1` (Correo). Verificación: los tests de 3.1 pasan y `test_notification_only_after_successful_creation` sigue verde.

## 4. Memoria Redis configurada (N8N-MEMORY-001)

- [x] 4.1 RED: agregar tests que verifican que el nodo `memoryRedisChat` declara credencial no vacía y parámetros no vacíos, y extender `CREDENTIAL_REQUIRING_NODE_TYPES` con `@n8n/n8n-nodes-langchain.memoryRedisChat` de modo que el test de credenciales lo cubra. Verificación: el test de configuración del nodo falla contra el estado actual.
- [x] 4.2 GREEN: declarar en el nodo `memoryRedisChat` la credencial `redis` con placeholder `REPLACE_WITH_REDIS_CREDENTIAL_ID` y parámetros de sesión no vacíos según el schema del nodo. Verificación: `test_c29_credential_requiring_nodes_declare_credentials` y los tests de 4.1 pasan.

## 5. Mecanismo único de autenticación (N8N-AUTH-002)

- [x] 5.1 RED: agregar tests que verifican que `HTTP POST a MTM-SRU` no combina credencial `httpHeaderAuth` con header `Authorization` explícito, que el header referencia el token de `Login operador` y que no declara credencial `httpHeaderAuth`; actualizar `test_c29_incidentes_http_node_declares_authentication` al contrato corregido (exactamente un mecanismo, header dinámico). Verificación: los tests nuevos fallan contra el estado actual.
- [x] 5.2 GREEN: remover `authentication`, `genericAuthType` y `credentials.httpHeaderAuth` del nodo `HTTP POST a MTM-SRU`, conservando el header explícito `=Bearer {{ $('Login operador').item.json.access_token }}`. Verificación: los tests de 5.1 pasan y `test_login_and_incidentes_nodes_use_env_backend_url` sigue verde.

## 6. Auditoría en el camino de error del backend (N8N-AUDIT-002)

- [x] 6.1 RED: agregar tests que verifican que `Registro de auditoria` es alcanzable desde `HTTP POST a MTM-SRU` `main#1`, que `Es correo?` se conserva en esa salida, y que el resultado de la rama de error no es `creado`. Verificación: el test de alcance de auditoría falla contra el estado actual.
- [x] 6.2 GREEN: agregar `Registro de auditoria` como sucesor de `HTTP POST a MTM-SRU` `main#1` en paralelo a `Es correo?`; refinar la detección de resultado del `jsCode` de auditoría para que un ítem de error de backend se registre con un `resultado` distinto de `creado`. Verificación: los tests de 6.1 pasan y `test_c33_error_branch_declares_continue_error_output_and_reaches_mark_read` sigue verde.

## 7. Fallo de notificación no omite auditoría (N8N-AUDIT-003)

- [x] 7.1 RED: agregar tests que verifican que `Notificar operador designado` declara `onError` de continuación y que `Registro de auditoria` sigue siendo alcanzable desde el nodo de notificación. Verificación: el test de `onError` falla contra el estado actual.
- [x] 7.2 GREEN: declarar `onError: "continueRegularOutput"` en `Notificar operador designado`, conservando la arista hacia `Registro de auditoria`. Verificación: los tests de 7.1 pasan y `test_notificar_operador_reaches_audit` sigue verde.

## 8. Sincronización de la guía (N8N-DOC-001)

- [x] 8.1 RED: agregar tests que parsean el conteo de nodos y el conteo de propiedades declarados en `docs/n8n-workflow-guide.md` y los comparan con `n8n/workflow.json` y con el número de funciones `test_` de la suite; agregar un test que verifica que la excepción obsoleta de la rama de revisión no está presente. Verificación: los tests fallan contra la guía actual.
- [x] 8.2 GREEN: actualizar `docs/n8n-workflow-guide.md` (conteo de nodos, conteo de propiedades de la suite, excepción conocida de la rama de revisión en las líneas 65-67, y cualquier tabla de nodos afectada). Verificación: los tests de 8.1 pasan.

## 9. Verificación integral

- [x] 9.1 Ejecutar la suite estructural completa: `cd App/Backend && pytest tests/test_n8n_workflow.py -q`. Verificación: todas las pruebas pasan y el único xfail sigue siendo el documentado.
- [x] 9.2 Ejecutar el subconjunto offline del backend para detectar regresiones: `cd App/Backend && pytest -m "not integration" -q`. Verificación: sin fallos.
- [x] 9.3 Validar el change: `openspec validate --strict --change c-40-n8n-wiring-fixes`. Verificación: validación estricta sin errores.
