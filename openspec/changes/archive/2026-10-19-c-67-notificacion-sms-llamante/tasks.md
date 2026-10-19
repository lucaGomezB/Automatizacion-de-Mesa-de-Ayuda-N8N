## 0. Prerequisitos y decisiones

- [ ] 0.1 Cerrar OQ3 — spike de entregabilidad de Twilio SMS a Argentina (+54). Resultado requerido antes de habilitar cualquier envío real: reporte del spike con veredicto sobre la entregabilidad. Verificación: spike cerrado con veredicto documentado. — blocked by OQ3 (AR SMS spike)
- [ ] 0.2 Alinear con `C-66` (privacidad-transferencias): confirmar que el marco de licitud/minimización y el instrumento de transferencia internacional (EE. UU. NO es país adecuado) están provistos por `C-66`. `c-67` los consume; no los redefine. Verificación: marco de `C-66` disponible y referenciado. — blocked by C-66
- [ ] 0.3 Registrar el baseline de las suites afectadas: `cd App/Backend; pytest -m "not integration" tests/test_n8n_workflow.py tests/test_openapi_sync.py tests/test_incidentes.py tests/test_telefonia_service.py tests/test_runtime_cost_guard.py` y anotar el conteo en verde. Si algo falla, reportarlo como fallo preexistente y NO corregirlo en este change. Verificación: conteo baseline anotado y sin fallos nuevos atribuibles al change. **Baseline heredado de c-53: offline 693 passed / 26 deselected / 1 xfailed; archivos afectados 216 passed / 1 xfailed.**

## 2. Configuración, guarda de costo y cliente de SMS

- [ ] 2.1 RED: escribir `App/Backend/tests/test_cost_guard_sms.py` que exija la superficie `twilio_sms` en `constants.py` y su costo unitario en `config.py`/`settings.py` (`cost_guard_unit_cost_twilio_sms_usd`). Verificación: el test falla por superficie desconocida. — blocked by OQ3 (AR SMS spike)
- [ ] 2.2 GREEN: agregar `PROVIDER_TWILIO_SMS` a `App/Backend/app/cost_guard/constants.py` e incorporarlo a `PAID_PROVIDERS`, y agregar `cost_guard_unit_cost_twilio_sms_usd` a `settings.py` y al mapa de `from_settings` en `cost_guard/config.py`. Verificación: los tests de 2.1 pasan. — blocked by OQ3 (AR SMS spike)
- [ ] 2.3 TRIANGULATE: cubrir que `twilio_sms` es una superficie distinta de `twilio` con su propio costo unitario y que el rate por origen usa el número llamante como clave. Verificación: casos en verde. — blocked by OQ3 (AR SMS spike)
- [ ] 2.4 RED: escribir `App/Backend/tests/test_twilio_sms_client.py` con el cliente inyectado, exigiendo: remitente configurable (número o Messaging Service), destinatario = número llamante, cuerpo = número de incidente, y propagación controlada del error del proveedor. Verificación: el test falla por cliente inexistente. — blocked by OQ3 (AR SMS spike)
- [ ] 2.5 GREEN: crear `App/Backend/app/clients/twilio_sms.py` que reutilice `twilio_account_sid`/`twilio_auth_token` y el patrón de cliente inyectable. Verificación: los tests pasan con transporte simulado. — blocked by OQ3 (AR SMS spike)
- [ ] 2.6 TRIANGULATE: cubrir respuesta de error del proveedor, timeout y número inválido sin excepción no controlada. Verificación: casos en verde. — blocked by OQ3 (AR SMS spike)
- [ ] 2.7 Actualizar `App/Backend/.env.example` con las claves nuevas del SMS (`cost_guard_unit_cost_twilio_sms_usd`, remitente/Messaging Service) y el costo unitario documentado como ESTIMACION; verificar que los defaults coinciden con `settings.py`. Verificación: claves presentes y defaults coincidentes. — blocked by OQ3 (AR SMS spike)

## 3. Captura y persistencia del número llamante (webhook de voz)

- [ ] 3.1 RED: extender `App/Backend/tests/test_runtime_cost_guard.py` (o `test_cost_guard_voice.py`) para exigir que el webhook de voz persista `{call_sid, caller_cifrado}` correlacionado por `CallSid` cuando el `From` está presente, y que no lo haga cuando falta. Verificación: el test falla contra el comportamiento actual. — blocked by OQ3 (AR SMS spike)
- [ ] 3.2 GREEN: modificar `App/Backend/app/routes/cost_guard.py` para capturar `CallSid` y `From` y hacer upsert (por `call_sid`) del ingreso con `caller_cifrado` y `transcripcion_estado = pendiente`, preservando la firma `X-Twilio-Signature`. Verificación: el test de 3.1 pasa. — blocked by OQ3 (AR SMS spike)
- [ ] 3.3 RED: extender `App/Backend/tests/test_telefonia_ingreso_repository.py` para exigir un método de upsert/creación por `CallSid` desde el webhook de voz, idempotente ante llamadas repetidas. Verificación: el test falla por método inexistente. — blocked by OQ3 (AR SMS spike)
- [ ] 3.4 GREEN: agregar el método al repositorio `telefonia_ingreso_repository.py`. Verificación: el test pasa. — blocked by OQ3 (AR SMS spike)
- [ ] 3.5 TRIANGULATE: cubrir (a) que el callback de estado de grabación conserva el `caller_cifrado` persistido por el webhook de voz; (b) que un segundo webhook de voz con el mismo `CallSid` no duplica fila; (c) que el número no aparece en claro en respuestas ni logs. Verificación: casos en verde. — blocked by OQ3 (AR SMS spike)
- [ ] 3.6 TRIANGULATE: prueba de no regresión de c-52 en el callback de grabación (sigue creando/persistiendo el ingreso y respetando la idempotencia por `CallSid`). Verificación: los tests de telefonia existentes siguen en verde. — blocked by OQ3 (AR SMS spike)

## 4. Servicio de notificación SMS y enganche en el alta

- [ ] 4.1 RED: escribir `App/Backend/tests/test_telefonia_notification_service.py` que describa: resolver el llamante por `CallSid` desde el ingreso persistido, reservar `twilio_sms` ANTES de enviar, enviar el SMS con el número del incidente, y omitir el envío con log si falta el llamante o la guarda deniega. Verificación: el test falla por servicio inexistente. — blocked by OQ3 (AR SMS spike)
- [ ] 4.2 GREEN: crear `App/Backend/app/services/telefonia_notification_service.py` con dependencias inyectadas (repositorio de ingreso, guarda, cliente SMS). Verificación: los tests pasan. — blocked by OQ3 (AR SMS spike)
- [ ] 4.3 TRIANGULATE: cubrir (a) guarda denegada no invoca al cliente y no falla el alta; (b) sin llamante no se envía y queda traza observable; (c) un `CallSid` repetido no produce un segundo SMS. Verificación: casos en verde. — blocked by OQ3 (AR SMS spike)
- [ ] 4.4 RED: extender `App/Backend/tests/test_incidentes.py` para exigir que la creación de un incidente de telefonía dispare la notificación SMS como tarea fire-and-forget que NO altera la respuesta ni propaga fallos, y que un incidente de otro canal no la dispare. Verificación: el test falla. — blocked by OQ3 (AR SMS spike)
- [ ] 4.5 GREEN: enganchar la notificación en `App/Backend/app/services/incidente_service.py` (tarea asíncrona con referencia retenida, análoga a `notify_n8n`), condicionada al canal de telefonía y a la existencia de un `CallSid` correlacionable. Verificación: los tests de 4.4 pasan. — blocked by OQ3 (AR SMS spike)
- [ ] 4.6 TRIANGULATE: cubrir que un fallo del SMS no afecta la respuesta del alta y que la tarea no es cancelada por el recolector de basura. Verificación: casos en verde. — blocked by OQ3 (AR SMS spike)

## 6. Documentación y verificación final

- [ ] 6.1 Documentar la postura de consentimiento/minimización (Ley 25.326) y el uso transaccional del número llamante en la documentación afectada, consumiendo el marco provisto por `C-66`. Verificación: la postura queda declarada de forma verificable y referenciada a `C-66`. — blocked by C-66
- [ ] 6.4 Ejecutar la verificación en vivo documentada: una llamada de prueba que produzca incidente y un SMS al número llamante con el número de incidente; documentar el resultado. Verificación: el SMS llega con el número correcto y el incidente existe. — blocked by OQ3 (AR SMS spike)
