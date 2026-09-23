## 1. Preparación, decisiones y safety net

- [ ] 1.1 Resolver las Open Questions del `design.md` con el humano antes de escribir código: (a) Open Question 1 — confirmar el PK `id` como número canónico (recomendado) o un número de negocio con prefijo; (b) Open Question 2 — confirmar la postura transaccional del SMS sin opt-out y el tope de gasto. Si la decisión difiere de la recomendación, actualizar `proposal.md`, `design.md` y los specs ANTES de continuar. Verificación: decisión registrada en `design.md` (Open Questions marcadas RESUELTO) o documento de decisión adjunto.
- [ ] 1.2 Registrar el baseline de las suites afectadas: `cd App/Backend; pytest -m "not integration" tests/test_n8n_workflow.py tests/test_openapi_sync.py tests/test_incidentes.py tests/test_telefonia_service.py tests/test_runtime_cost_guard.py` y anotar el conteo en verde. Si algo falla, reportarlo como fallo preexistente y NO corregirlo en este change. Verificación: conteo baseline anotado y sin fallos nuevos atribuibles al change.

## 2. Configuración, guarda de costo y cliente de SMS

- [ ] 2.1 RED: escribir `App/Backend/tests/test_cost_guard_sms.py` que exija la superficie `twilio_sms` en `constants.py` y su costo unitario en `config.py`/`settings.py` (`cost_guard_unit_cost_twilio_sms_usd`). Verificación: el test falla por superficie desconocida.
- [ ] 2.2 GREEN: agregar `PROVIDER_TWILIO_SMS` a `App/Backend/app/cost_guard/constants.py` e incorporarlo a `PAID_PROVIDERS`, y agregar `cost_guard_unit_cost_twilio_sms_usd` a `settings.py` y al mapa de `from_settings` en `cost_guard/config.py`. Verificación: los tests de 2.1 pasan.
- [ ] 2.3 TRIANGULATE: cubrir que `twilio_sms` es una superficie distinta de `twilio` con su propio costo unitario y que el rate por origen usa el número llamante como clave. Verificación: casos en verde.
- [ ] 2.4 RED: escribir `App/Backend/tests/test_twilio_sms_client.py` con el cliente inyectado, exigiendo: remitente configurable (número o Messaging Service), destinatario = número llamante, cuerpo = número de incidente, y propagación controlada del error del proveedor. Verificación: el test falla por cliente inexistente.
- [ ] 2.5 GREEN: crear `App/Backend/app/clients/twilio_sms.py` que reutilice `twilio_account_sid`/`twilio_auth_token` y el patrón de cliente inyectable. Verificación: los tests pasan con transporte simulado.
- [ ] 2.6 TRIANGULATE: cubrir respuesta de error del proveedor, timeout y número inválido sin excepción no controlada. Verificación: casos en verde.
- [ ] 2.7 Actualizar `App/Backend/.env.example` con las claves nuevas del SMS (`cost_guard_unit_cost_twilio_sms_usd`, remitente/Messaging Service) y el costo unitario documentado como ESTIMACION; verificar que los defaults coinciden con `settings.py`. Verificación: claves presentes y defaults coincidentes.

## 3. Captura y persistencia del número llamante (webhook de voz)

- [ ] 3.1 RED: extender `App/Backend/tests/test_runtime_cost_guard.py` (o `test_cost_guard_voice.py`) para exigir que el webhook de voz persista `{call_sid, caller_cifrado}` correlacionado por `CallSid` cuando el `From` está presente, y que no lo haga cuando falta. Verificación: el test falla contra el comportamiento actual.
- [ ] 3.2 GREEN: modificar `App/Backend/app/routes/cost_guard.py` para capturar `CallSid` y `From` y hacer upsert (por `call_sid`) del ingreso con `caller_cifrado` y `transcripcion_estado = pendiente`, preservando la firma `X-Twilio-Signature`. Verificación: el test de 3.1 pasa.
- [ ] 3.3 RED: extender `App/Backend/tests/test_telefonia_ingreso_repository.py` para exigir un método de upsert/creación por `CallSid` desde el webhook de voz, idempotente ante llamadas repetidas. Verificación: el test falla por método inexistente.
- [ ] 3.4 GREEN: agregar el método al repositorio `telefonia_ingreso_repository.py`. Verificación: el test pasa.
- [ ] 3.5 TRIANGULATE: cubrir (a) que el callback de estado de grabación conserva el `caller_cifrado` persistido por el webhook de voz; (b) que un segundo webhook de voz con el mismo `CallSid` no duplica fila; (c) que el número no aparece en claro en respuestas ni logs. Verificación: casos en verde.
- [ ] 3.6 TRIANGULATE: prueba de no regresión de c-52 en el callback de grabación (sigue creando/persistiendo el ingreso y respetando la idempotencia por `CallSid`). Verificación: los tests de telefonia existentes siguen en verde.

## 4. Servicio de notificación SMS y enganche en el alta

- [ ] 4.1 RED: escribir `App/Backend/tests/test_telefonia_notification_service.py` que describa: resolver el llamante por `CallSid` desde el ingreso persistido, reservar `twilio_sms` ANTES de enviar, enviar el SMS con el número del incidente, y omitir el envío con log si falta el llamante o la guarda deniega. Verificación: el test falla por servicio inexistente.
- [ ] 4.2 GREEN: crear `App/Backend/app/services/telefonia_notification_service.py` con dependencias inyectadas (repositorio de ingreso, guarda, cliente SMS). Verificación: los tests pasan.
- [ ] 4.3 TRIANGULATE: cubrir (a) guarda denegada no invoca al cliente y no falla el alta; (b) sin llamante no se envía y queda traza observable; (c) un `CallSid` repetido no produce un segundo SMS. Verificación: casos en verde.
- [ ] 4.4 RED: extender `App/Backend/tests/test_incidentes.py` para exigir que la creación de un incidente de telefonía dispare la notificación SMS como tarea fire-and-forget que NO altera la respuesta ni propaga fallos, y que un incidente de otro canal no la dispare. Verificación: el test falla.
- [ ] 4.5 GREEN: enganchar la notificación en `App/Backend/app/services/incidente_service.py` (tarea asíncrona con referencia retenida, análoga a `notify_n8n`), condicionada al canal de telefonía y a la existencia de un `CallSid` correlacionable. Verificación: los tests de 4.4 pasan.
- [ ] 4.6 TRIANGULATE: cubrir que un fallo del SMS no afecta la respuesta del alta y que la tarea no es cancelada por el recolector de basura. Verificación: casos en verde.
- [ ] 4.7 Verificar el contrato OpenAPI si cambió el webhook de voz: regenerar `docs/openapi.json` y ejecutar `cd App/Backend; pytest tests/test_openapi_sync.py -v`. Verificación: el test de sincronización pasa.

## 5. Cableado N8N: correo y cierre web

- [ ] 5.1 RED: extender `App/Backend/tests/test_n8n_workflow.py` para exigir: (a) la normalización extrae el remitente desde `from` string y desde `from.emailAddress.address`; (b) el nodo `Correo de confirmacion al usuario` es alcanzable desde la rama de revisión humana del canal correo; (c) la rama de revisión humana del web responde con `incidente_id` no nulo cuando el incidente fue creado. Verificación: los tests fallan contra el workflow actual.
- [ ] 5.2 GREEN: editar `n8n/workflow.json` para (a) normalizar el `remitente` en ambos formatos, (b) conectar la confirmación de correo también en la rama `requiere_revision_humana = true` del canal correo con `onError: continueRegularOutput`, y (c) incluir el `incidente_id` en el cierre web de la rama de revisión humana. Verificación: los tests de 5.1 pasan.
- [ ] 5.3 TRIANGULATE: prueba de no regresión de c-46/c-47/c-52 (el sello `.first()`, `Restaurar item telefonia` entre `Guard de costo` y `Guard permite?`, y la salida de telefonía del switch siguen sin desviarse al nodo de correo). Verificación: casos en verde.
- [ ] 5.4 TRIANGULATE: verificar que las ramas web sin incidente siguen declarando `sin_alta` sin número y que la guarda `Es web?` restringe la respuesta al canal web. Verificación: casos en verde.
- [ ] 5.5 Actualizar `docs/n8n-workflow-guide.md`: eliminar la afirmación de confirmación telefónica por TwiML (`<Say>`), documentar el SMS, la confirmación de correo en revisión humana y el cierre web con número, y ajustar los conteos de nodos y de pruebas. Verificación: `cd App/Backend; pytest tests/test_n8n_workflow.py -v` en verde y conteos coincidentes.

## 6. Documentación y verificación final

- [ ] 6.1 Documentar la postura de consentimiento/minimización (Ley 25.326) y el uso transaccional del número llamante en la documentación afectada. Verificación: la postura queda declarada de forma verificable.
- [ ] 6.2 Ejecutar la suite backend offline: `cd App/Backend; pytest -m "not integration"`. Verificación: sin regresiones respecto del baseline de 1.2.
- [ ] 6.3 Ejecutar lint: `cd App/Backend; ruff check .`. Verificación: sin errores E nuevos.
- [ ] 6.4 Ejecutar la verificación en vivo documentada: una llamada de prueba que produzca incidente y un SMS al número llamante con el número de incidente; documentar el resultado. Verificación: el SMS llega con el número correcto y el incidente existe.
- [ ] 6.5 Ejecutar `openspec validate --strict --changes c-53-notificacion-numero-incidente`. Verificación: validación estricta sin errores.