## 0. Gate de decisiones humanas (gobernanza HIGH — bloquea todo lo demás)

- [x] 0.1 Resolver con el humano las Open Questions 1-6 de `design.md` y registrarlas resueltas en la sección "Decisiones resueltas (registro)" con su valor concreto. Valores registrados: (1) bolsa GLOBAL compartida de USD 10/semana para las tres superficies; (2) enforcement en las TRES superficies (backend Gemini, n8n AI Agent, Twilio); (3) degradación = determinístico + revisión humana; (4) almacén PostgreSQL (migración Alembic 007) y fail-closed con notificación; (5) Twilio entra con webhook de voz pre-llamada; (6) estado por defecto habilitado conservador con override por `.env`. Verificar releyendo `design.md` que cada respuesta figura con su valor concreto.
- [x] 0.2 Obtener aprobación humana explícita del plan resultante antes de escribir código; verificar que la aprobación quede registrada en la sesión. APROBADO — registrado en engram obs #953; se autoriza escribir código.

## 1. RED — Red de seguridad y tests que fallan primero (offline)

- [x] 1.1 Ejecutar la suite offline como línea base: `cd App/Backend; pytest -m "not integration" -q` y registrar el número de tests pasando. Línea base: 469 passed, 22 deselected, 1 xfailed (0 fallos preexistentes).
- [x] 1.2 Crear `App/Backend/tests/test_runtime_cost_guard.py` con un test que exija que, con gasto global por debajo del presupuesto, la guarda permita la llamada; ejecutar `cd App/Backend; pytest tests/test_runtime_cost_guard.py -q` y confirmar RED (el módulo no existe).
- [x] 1.3 Agregar el test de presupuesto global agotado (gasto acumulado >= presupuesto deniega en cualquier superficie) y confirmar RED.
- [x] 1.4 Agregar el test de costo unitario por superficie: dos superficies con costos unitarios distintos descuentan de la MISMA bolsa global; confirmar RED.
- [x] 1.5 Agregar el test de reinicio de ventana con reloj inyectado (avanzar el reloj más allá de la ventana reinicia el gasto y permite) y confirmar RED.
- [x] 1.6 Agregar el test de límite de tasa global excedido (cantidad de llamadas >= límite deniega) y confirmar RED.
- [x] 1.7 Agregar el test de límite de tasa por número de origen excedido (el origen excedido deniega y no bloquea a otros orígenes por debajo de su límite) y confirmar RED.
- [x] 1.8 Agregar el test de almacén inalcanzable que exija fail-closed (denegar), degradar a determinístico con revisión humana y emitir la notificación estructurada; confirmar RED.
- [x] 1.9 Agregar el test de degradación en backend: con la guarda disparada, el proveedor pago falso NO recibe llamada y el resultado queda marcado para revisión humana; confirmar RED.
- [x] 1.10 Agregar el test del endpoint de guarda para n8n: responde permitido/denegado según la evaluación; confirmar RED.
- [x] 1.11 Agregar el test del webhook de voz pre-llamada de Twilio: permitido devuelve TwiML con `<Record transcribe="true">`; denegado devuelve `<Say>` + `<Hangup>`; confirmar RED.
- [x] 1.12 Agregar el test de que el número de origen crudo aparece en los eventos de la guarda y que el corpus de evaluación no lo consume; confirmar RED.

## 2. GREEN — Configuración en Settings

- [x] 2.1 Agregar a `App/Backend/app/config/settings.py` los campos de la guarda con los defaults resueltos (`cost_guard_enabled=True`, `cost_guard_budget_usd=10.0`, `cost_guard_budget_window_seconds=604800`, costos unitarios por superficie, rate global y por caller, `cost_guard_degradation_policy="deterministic_review"`, `cost_guard_store_failure_policy="fail_closed"`, `cost_guard_alert_enabled=True`); verificar que `Settings` instancia con los dummies de test.
- [x] 2.2 Documentar en el docstring de cada campo que los costos unitarios son ESTIMACIONES configurables, no contabilidad exacta, y que los defaults están sujetos a override por `.env`.

## 3. GREEN — Modelo PostgreSQL y migración Alembic 007

- [x] 3.1 Crear el modelo ORM `costo_guarda_contador` (columnas `ambito`, `clave`, `ventana_inicio`, `llamadas`, `costo_usd`, `TimestampMixin`; restricción única `(ambito, clave, ventana_inicio)`; índice por `ventana_inicio`), siguiendo el estilo de `app/models/base.py` e `incidente.py`.
- [x] 3.2 Crear `App/Backend/alembic/versions/007_cost_guard_counters.py` (`revision = "007"`, `down_revision = "006"`) que crea la tabla en `upgrade` y la dropea en `downgrade`; incluir en el docstring la nota "Aprobacion humana explicita (gobernanza ALTA)", siguiendo el estilo de `006_add_timing_instrumentation.py`.
- [x] 3.3 Verificar la migración: `cd App/Backend; alembic upgrade head` y luego `alembic downgrade 006` contra la base descartable (subconjunto integration), confirmando que no rompe migraciones previas. Verificado offline con la cadena Alembic sobre SQLite (upgrade head + downgrade 006 + re-upgrade) en tests/test_migration_007_cost_guard.py. Verificado ADEMAS contra PostgreSQL 15.5 en base descartable dedicada `mesa_de_ayuda_migration_test` (creada y dropeada): `alembic upgrade head` aplico 001->007 (exit 0), la tabla `costo_guarda_contador` quedo con la unica `(ambito, clave, ventana_inicio)` y el indice `ix_costo_guarda_contador_ventana_inicio`, `alembic downgrade 006` elimino la tabla (exit 0) y el re-upgrade la recreo. No rompe migraciones previas.

## 4. GREEN — Función de decisión pura, protocolos y fake en memoria

- [x] 4.1 Crear el módulo de la guarda (ubicación recomendada `App/Backend/app/cost_guard/`) con el protocolo de almacén de contadores y el protocolo de fuente de tiempo.
- [x] 4.2 Implementar la función de decisión PURA sobre (contadores resultantes, configuración, instante) que devuelve permitir/denegar con causa (`budget`, `rate`, `caller_rate`); ejecutar `cd App/Backend; pytest tests/test_runtime_cost_guard.py -q` y confirmar GREEN de 1.2-1.7.
- [x] 4.3 Implementar el almacén falso en memoria (fake inyectable, sin red) y usarlo en los tests de ventana, costo unitario y límites; confirmar GREEN de 1.4-1.7.

## 5. GREEN — Adaptador PostgreSQL con reserva atómica

- [x] 5.1 Implementar el adaptador de almacén PostgreSQL que ejecuta la reserva en su PROPIA sesión/transacción (fuera de la transacción del incidente) con `INSERT ... ON CONFLICT (ambito, clave, ventana_inicio) DO UPDATE ... RETURNING` para `global`, `surface` y `caller`.
- [x] 5.2 Implementar el ROLLBACK de la reserva cuando la función pura deniega (no cuenta porque no hubo llamada) y el COMMIT cuando permite.
- [x] 5.3 Verificar con un test de integración PostgreSQL (base descartable) que dos reservas concurrentes no exceden el límite por la carrera de chequeo e incremento. Test escrito en tests/test_runtime_cost_guard_integration.py (10 reservas concurrentes + rollback); VERIFICADO contra PostgreSQL 15.5 en base descartable: `pytest -m integration` -> 25 passed, incluidos `test_reserva_atomica_concurrente_no_excede` (10 incrementos concurrentes exactos, sin perder incrementos), `test_rollback_no_consolida_la_reserva` y `test_guarda_contra_postgresql_permite_y_reserva`.
- [x] 5.4 Verificar que la construcción del adaptador no abre conexión hasta el primer uso.

## 6. GREEN — Enforcement en backend antes de Gemini y degradación

- [x] 6.1 Cablear la evaluación de la guarda antes de la invocación de Gemini en el backend: si deniega, lanzar `CostGuardTrippedError` sin invocar al proveedor; verificar con un test que el proveedor falso no recibe llamada cuando la guarda deniega (GREEN de 1.9).
- [x] 6.2 Manejar `CostGuardTrippedError` en `HybridClassifier` aplicando la degradación resuelta (determinístico + `requiere_revision_humana=True`), reutilizando el patrón de `hybrid.py:135-150`; confirmar GREEN de 1.9.
- [x] 6.3 Confirmar que la clasificación precalculada (`incidente_service.py:298-299`) y el cortocircuito determinístico (`hybrid.py:115-123`) NO consultan la guarda ni descuentan gasto ni tasa.

## 7. GREEN — Enforcement del AI Agent de n8n (workflow.json)

- [x] 7.1 Implementar el endpoint de guarda para n8n (p. ej. `POST /api/v1/cost-guard/reserve` con `provider="n8n_gemini"` y caller opcional) con autenticación por secreto compartido; verificar GREEN de 1.10.
- [x] 7.2 Modificar `n8n/workflow.json`: insertar el nodo HTTP "Guard de costo" entre `Sellar ingreso telefonia` y `AI Agent`, y un nodo IF que rutee PERMITIDO → `AI Agent` y DENEGADO → `Derivar a revision humana`; re-cablear las conexiones correspondientes.
- [x] 7.3 Verificar que `n8n/workflow.json` parsea como JSON válido y que las conexiones referencian nodos existentes (sin nodos huérfanos).
- [x] 7.4 Documentar que el costo unitario `n8n_gemini` es una estimación por ejecución que cubre el número acotado de invocaciones (`maxIterations=2` más el bucle de refinamiento) y que se reserva una sola vez por ejecución.

## 8. GREEN — Webhook de voz pre-llamada de Twilio y twiml.xml

- [x] 8.1 Implementar el endpoint público de cara a Twilio (p. ej. `POST /api/v1/cost-guard/twilio/voice`), sin JWT de operador, que recibe los parámetros estándar (`From`, `To`, `CallSid`, `AccountSid`, `CallStatus`, `Direction`) y consulta la guarda; verificar GREEN de 1.11.
- [x] 8.2 Responder TwiML: PERMITIDO con `<Say>` + `<Record maxLength="45" finishOnKey="#" transcribe="true" playBeep="true"/>` + `<Say>`; DENEGADO con `<Say>` + `<Hangup/>`; `Content-Type: text/xml`.
- [x] 8.3 Reservar exactamente una unidad de `cost_guard_unit_cost_twilio_transcription_usd` por llamada concedida (duración desconocida al inicio, consistente con el modelo de cantidad de llamadas por costo unitario).
- [x] 8.4 Actualizar `n8n/twilio/twiml.xml` para que la grabación con transcripción quede servida por el endpoint (o dejar constancia de que la URL de voz del número apunta al endpoint); verificar que el XML es válido.
- [x] 8.5 Implementar y verificar la validación de la petición de Twilio (firma o secreto compartido); confirmar en apply el nombre exacto del header de firma contra la documentación de Twilio antes de depender de él.

## 9. GREEN — Captura y registro del número de origen crudo

- [x] 9.1 Capturar `From` en el webhook pre-llamada y, cuando esté disponible, el caller del evento call-summary; usarlo como clave del contador `caller` y emitirlo CRUDO en los eventos de la guarda.
- [x] 9.2 Verificar con un test que el número crudo aparece en los eventos de la guarda y que `evaluation/` no lo consume (exclusión del corpus); confirmar GREEN de 1.12.
- [x] 9.3 Acotar la retención del contador `caller` a la ventana del rate por origen (purga de ventanas vencidas).

## 10. GREEN — Fail-closed y notificación

- [x] 10.1 Aplicar la política `fail_closed` por defecto: ante error del almacén, denegar la llamada paga en las tres superficies y degradar de forma segura; confirmar GREEN de 1.8.
- [x] 10.2 Emitir el evento estructurado `cost_guard_store_unavailable` (causa, superficie, ventana, límite, caller, clase de error; sin secretos) y la notificación/alerta; verificar con un test que captura logs.
- [x] 10.3 Verificar que la degradación por store caído es coherente en las tres superficies: backend determinístico + revisión humana, n8n derivar a revisión humana, Twilio `<Say>` + `<Hangup>`.

## 11. GREEN — Observabilidad (tripped, store_unavailable y postura)

- [x] 11.1 Emitir el evento estructurado `cost_guard_tripped` (causa, superficie, ventana, límite, caller; sin secretos) cuando la guarda se dispara, y no emitirlo cuando permite; verificar con un test que captura logs y asserta la causa y la ausencia del evento en el caso permitido.
- [x] 11.2 Registrar la postura efectiva de la guarda al arranque (lifespan de FastAPI): habilitada/deshabilitada, presupuesto, ventana, costos unitarios, tasas y política de degradación; verificar con un test de arranque que la postura aparece en los logs.
- [x] 11.3 Manejar configuración inválida (monto/límite no numérico) fallando de forma explícita o aplicando el default documentado, sin arrancar en estado de gasto no acotado sin advertirlo; verificar con un test que el arranque no queda silencioso ante configuración inválida.

## 12. GREEN — Documentación

- [x] 12.1 Agregar a la tabla de variables de `README.md` (sección "Configurar las variables de entorno") las variables de la guarda con su descripción y default; verificar releyendo la sección que lista presupuesto, ventana, costos unitarios, tasas, política de degradación y fail-closed.
- [x] 12.2 Documentar en `docs/operational-guide.md` el comportamiento operativo: postura al arranque, degradación al excederse, fail-closed y cómo deshabilitarla, el webhook pre-llamada de Twilio y el nodo de guarda de n8n; verificar que el texto nombra las mismas variables que `README.md`.
- [x] 12.3 Actualizar `App/Backend/.env.example` con las variables de la guarda y sus defaults documentados.

## 13. TRIANGULATE — Cobertura de los escenarios de la spec

- [x] 13.1 Agregar el test de que la clasificación precalculada no consulta la guarda ni descuenta gasto ni tasa; confirmar que pasa.
- [x] 13.2 Agregar el test de que el cortocircuito determinístico no consulta la guarda ni descuenta gasto ni tasa; confirmar que pasa.
- [x] 13.3 Agregar el test de default determinista sin configuración: dos instanciaciones sin configuración producen el mismo comportamiento por defecto y arranca habilitada conservadora; confirmar que pasa.
- [x] 13.4 Agregar el test de reinicio de la ventana de tasa global y de la ventana por origen (el contador se reinicia y vuelve a permitir); confirmar que pasa.
- [x] 13.5 Agregar el test de que una llamada permitida no emite evento de disparo; confirmar que pasa.
- [x] 13.6 Agregar el test de que el gasto de una superficie consume la bolsa compartida y afecta la evaluación de otra superficie; confirmar que pasa.
- [x] 13.7 Confirmar que cada escenario de `specs/runtime-cost-guard/spec.md` tiene al menos un test que lo ejerce; listar el mapeo escenario -> test en la sesión de apply. Mapeo escenario -> test documentado en el reporte de apply (todos los escenarios de specs/runtime-cost-guard/spec.md tienen al menos un test).

## 14. REFACTOR — Mejora sin cambiar comportamiento

- [x] 14.1 Extraer constantes y la función de decisión pura, mejorar nombres y eliminar duplicación; ejecutar `cd App/Backend; pytest tests/test_runtime_cost_guard.py -q` tras cada paso y confirmar que sigue GREEN. Constantes y funcion de decision pura extraidas; tests en verde tras cada paso.
- [x] 14.2 Ejecutar `cd App/Backend; ruff check .` y corregir lo reportado en los archivos nuevos.
- [x] 14.3 Ejecutar la suite offline completa `cd App/Backend; pytest -m "not integration" -q` y confirmar que no hay regresiones respecto de la línea base de 1.1.

## 15. Verificación final

- [x] 15.1 Ejecutar `cd App/Backend; pytest -m "not integration" -q` y confirmar que pasa completo y offline.
- [x] 15.2 Ejecutar `cd App/Backend; pytest tests/test_runtime_cost_guard.py -q` y confirmar que cubre bolsa global, costo unitario por superficie, ventana, tasa global, tasa por origen, fail-closed, degradación, bypass precalculado/determinístico, webhook Twilio, endpoint n8n, caller crudo y observabilidad.
- [x] 15.3 Ejecutar `cd App/Backend; pytest -m integration` (base descartable) y confirmar que la migración 007 y la reserva atómica funcionan contra PostgreSQL. EJECUTADO contra PostgreSQL 15.5: `pytest -m integration -q` -> 25 passed, 520 deselected en 63.49s (incluye la reserva atomica concurrente y el rollback); la migracion 007 se verifico ademas con `alembic upgrade head` / `alembic downgrade 006` / re-upgrade sobre una base descartable dedicada.
- [x] 15.4 Ejecutar `cd App/Backend; ruff check .` y confirmar que no reporta hallazgos nuevos.
- [x] 15.5 Verificar que `n8n/workflow.json` parsea como JSON y que `n8n/twilio/twiml.xml` es XML válido.
- [x] 15.6 Ejecutar `openspec validate --strict --changes c-45-runtime-cost-guard` y confirmar que pasa.
- [x] 15.7 Ejecutar `openspec status --change c-45-runtime-cost-guard` y confirmar que las tareas quedan registradas.

## 16. Hardening post-verify (correcciones a los warnings del verify-report)

- [x] 16.1 Warning 1: exigir el secreto compartido en el header `X-Cost-Guard-Secret` en AMBOS endpoints (n8n y webhook de voz); prohibir la via por query string. Sin secreto configurado los endpoints rechazan con HTTP 401 (envelope estandar) y el arranque emite `cost_guard_secret_missing`; no existe configuracion con la guarda habilitada y los endpoints abiertos. Tests: sin secreto, secreto incorrecto, secreto correcto, sin configuracion, query rechazado.
- [x] 16.2 Warning 2: implementar `cost_guard_store_failure_policy` (`fail_closed` default, `fail_open` soportado) y hacer que `cost_guard_alert_enabled` controle la notificacion externa adicional (webhook N8N) sin suprimir el evento estructurado obligatorio. Tests: fail_open permite, fail_closed default deniega, alert on/off, fallo de la alerta no altera la decision.
- [x] 16.3 Warning 3: implementar y verificar la validacion de `X-Twilio-Signature` (HMAC-SHA1) gateada en `TWILIO_AUTH_TOKEN`; sin token se omite la firma pero el secreto compartido sigue siendo obligatorio. Algoritmo confirmado contra la documentacion de Twilio y el SDK oficial; validado con el vector de prueba del SDK. Tests: firma valida, firma invalida, token ausente.
- [x] 16.4 Warning 3: reconciliar los artefactos (`design.md` D7/contrato, docstring de la ruta) con la firma de Twilio ya implementada y verificada.
- [x] 16.5 Warning 4: documentar en `docs/operational-guide.md` (§11.7) y `docs/n8n-workflow-guide.md` que el campo de transcripcion de Twilio sigue NO verificado y como ajustar el fallback hardcodeado del `AI Agent`.
- [x] 16.6 Warning 5: documentar en `docs/operational-guide.md` (§11.8) la deriva de credenciales del volumen PostgreSQL de integracion y la recuperacion segura (base descartable distinta de la de la aplicacion; nunca `TEST_PG_ALLOW_APP_DB` contra datos reales).
- [x] 16.7 Actualizar `README.md`, `App/Backend/.env.example` y la configuracion de tests; regenerar `docs/openapi.json` tras agregar los headers al contrato.

## 17. Fix post-verify: blockers de autenticacion B1 y B2 (gobernanza HIGH — aprobacion humana otorgada)

- [x] 17.1 B1 RED: tests que exigen que el webhook de voz de Twilio se autentique solo con `X-Twilio-Signature` (sin `X-Cost-Guard-Secret`) y que quede cerrado (HTTP 401) cuando `TWILIO_AUTH_TOKEN` no esta configurado; confirmar RED (6 fallos, 200 vs 401).
- [x] 17.2 B1 GREEN: eliminar la exigencia del secreto compartido del endpoint `POST /twilio/voice`; hacer de `X-Twilio-Signature` el unico gate, exigido siempre que `TWILIO_AUTH_TOKEN` este configurado y con 401 fail-closed si falta. Confirmar GREEN (9 passed en los tests de Twilio).
- [x] 17.3 B1 postura + triangulacion: agregar `twilio_auth_token_configured` a `CostGuardConfig`, el evento `cost_guard_twilio_token_missing` a la postura de arranque y el test de firma valida de OTRA URL (caveat de proxy). Confirmar GREEN.
- [x] 17.4 B2 RED: tests estructurales que exigen que el nodo `Guard de costo` referencie `$env.COST_GUARD_SHARED_SECRET`, que `docker-compose.yml` defina `COST_GUARD_SHARED_SECRET` para el servicio n8n y que backend y n8n interpolen la MISMA variable de la raiz `.env`; confirmar RED (2 fallos).
- [x] 17.5 B2 GREEN: cablear `COST_GUARD_SHARED_SECRET` en `docker-compose.yml` para n8n y backend con la misma interpolacion `${COST_GUARD_SHARED_SECRET:-}` y documentarlo como fuente unica en el `.env.example` de la raiz. Confirmar GREEN; `docker compose config` muestra el mismo valor en ambos servicios.
- [x] 17.6 Coherencia de artefactos: actualizar `design.md` (D7 y riesgo), `docs/operational-guide.md` (§11.2, §11.6 y bloque de variables), `docs/n8n-workflow-guide.md` (§2), `README.md`, `App/Backend/.env.example` (con `TWILIO_AUTH_TOKEN` marcado "cargar el valor real luego"), `n8n/twilio/README.md` (reescrito: Method POST, sin hosting estatico que omita la guarda) y `n8n/twilio/twiml.xml` (nota de auth).
- [x] 17.7 Regenerar `docs/openapi.json` (el endpoint de Twilio deja de declarar `X-Cost-Guard-Secret`); verificar `pytest tests/test_runtime_cost_guard.py`, `pytest -m "not integration"`, `ruff check .`, `pytest tests/test_openapi_sync.py` y `openspec validate --strict`. Resultados: 67 passed, 540 passed, ruff limpio, 5 passed, validate 1 passed.

## 18. Cierre W1/W2 (post post-verify)

- [x] 18.1 W1 RED: tests que exigen que el backend confie en los headers reenviados del proxy (`FORWARDED_ALLOW_IPS` en el servicio backend de `docker-compose.yml`) y que la firma calculada sobre la URL publica `https://...` valide a traves del middleware de Uvicorn, mas la triangulacion de que una firma `http://...` NO valide cuando el proxy declara `https`. Confirmar RED (5 fallos: config ausente y OpenAPI sin `text/xml`/`401`).
- [x] 18.2 W1 GREEN: definir `FORWARDED_ALLOW_IPS: ${FORWARDED_ALLOW_IPS:-*}` en el servicio backend de `docker-compose.yml` (Uvicorn honra `X-Forwarded-Proto` para reconstruir `request.url`). Documentar el supuesto de confianza (el puerto 8000 NO se publica; Nginx sobreescribe `X-Forwarded-Proto` con `$scheme`, por lo que un cliente externo no puede falsificarlo) en `docs/operational-guide.md` §11.6, `README.md` y el `.env.example` de la raiz, incluyendo la accion del operador al cargar `TWILIO_AUTH_TOKEN` (la URL publica en Twilio debe coincidir con la reconstruida). Confirmar GREEN.
- [x] 18.3 W2 RED: tests que exigen que el OpenAPI generado declare `text/xml` para el 200 del webhook TwiML (y no `application/json`) y `401` en ambos endpoints de guarda. Confirmar RED (2 fallos).
- [x] 18.4 W2 GREEN: declarar `response_class=TwimlResponse` (media type `text/xml`) y `responses={401: ...}` en las rutas de `App/Backend/app/routes/cost_guard.py`; regenerar `docs/openapi.json` con `scripts/export_openapi.py`; confirmar GREEN.
- [x] 18.5 Verificacion final W1/W2: `pytest tests/test_runtime_cost_guard.py -q` (72 passed), `pytest -m "not integration" -q` (545 passed), `ruff check .` (limpio), `pytest tests/test_openapi_sync.py -q` (5 passed) y `openspec validate --strict` en verde.
