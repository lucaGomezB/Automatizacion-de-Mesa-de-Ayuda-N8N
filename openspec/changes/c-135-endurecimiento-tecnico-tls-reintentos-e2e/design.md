## Context

La motivacion esta en `proposal.md` (Why): el dictamen v10/v1.1.0 descuenta en el criterio 5 la falta de TLS en la instancia validada, la invocacion sincronica sin reintentos y la ausencia de pruebas E2E con N8N, y situa esas lineas fuera de sus recomendaciones. Este change es opcional y se organiza en tres bloques aplicables por separado. Estado verificado del repositorio (solo lectura, rama `ramagonzalo`):

**Borde TLS (bloque 1)**

- `nginx/nginx.conf`: `ssl_protocols TLSv1.2 TLSv1.3` en el bloque HTTPS y en el catch-all; `return 301 https://$host$request_uri` en el bloque HTTP; `add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always` solo en el bloque 443; catch-all `default_server` con `return 444`; `server_tokens off`; `Referrer-Policy`, `Permissions-Policy`, `X-Content-Type-Options`, `X-Frame-Options`; certificados `/etc/nginx/certs/mesa.{crt,key}`.
- `docker-compose.yml`: el servicio `nginx` (imagen fijada `nginx:1.31.7-alpine`) monta `./openssl:/etc/nginx/certs:ro` y publica `"80:80"` y `"443:443"`, es decir, en todas las interfaces; el comentario de cabecera afirma que 80/443 estan "acotados a loopback", lo cual es falso. `postgres` y `n8n` publican en `127.0.0.1`. N8N corre con `N8N_PROTOCOL=http` y `WEBHOOK_URL=http://localhost:5678/` (callback OAuth local), solo en la red `automation` y solo en loopback; Nginx no enruta hacia N8N.
- `openssl/generate-certs.{sh,ps1}` generan `openssl/mesa.{crt,key}` (RSA 2048, SHA-256, 365 dias, SAN `localhost`, `mesa.local`, `127.0.0.1`); `.gitignore` excluye `openssl/*.crt|*.key|*.pem|*.csr` y se versiona `openssl/.gitkeep`.
- `App/Backend/tests/test_c62_infra_hardening.py` verifica el borde de forma estructural (version oculta, cabeceras, limite de tasa, catch-all y redireccion), pero su guarda `test_no_published_port_is_exposed_on_all_interfaces` solo detecta el prefijo explicito `0.0.0.0:` y no un mapeo desnudo como `"80:80"`. Ninguna prueba ejercita el borde en ejecucion.
- La spec `openspec/specs/tls-docker-compose/spec.md` (C-20) quedo desalineada: exige solo TLS 1.3, certificados `nginx/certs/server.{crt,key}`, scripts `scripts/generate-certs.*`, `N8N_PROTOCOL=https` con `WEBHOOK_URL` HTTPS, `VITE_API_BASE_URL=https://localhost/api/v1` y un stack con Redis. Lo desplegado difiere en los seis puntos.
- Tesis: `05-arquitectura.tex:8` ("el despliegue publicado para la validacion experimental no incluyo dicho proxy, por lo que la terminacion TLS corresponde al diseno y no a una capacidad verificada en la instancia publicada"), `11-aspectos-legales.tex:24` (misma salvedad) y `12-anexos.tex:10` ("no incluido en el despliegue publicado"). `docs/diagrams/despliegue.md:18` rotula "TLS 1.3 termination". Coherente con la tesis, el perfil `corpus` de la corrida de medicion telefonica (c-70) expone `backend-corpus` por un tunel propio sobre `127.0.0.1:8001`, sin pasar por Nginx.

**Tramo de alta N8N -> backend (bloque 2)**

- `n8n/workflow.json` (32 nodos, 29 operativos): `HTTP POST a MESA-AYUDAS` (`httpRequest` v4.4) declara `onError: continueErrorOutput` y `parameters.options: {}` (sin `timeout`, sin `retryOnFail`); su salida de error va a `Es correo?` y `Registro de auditoria`. `Login operador` (`httpRequest` v4.4), primera llamada al backend del tramo de alta, no declara reintento, timeout ni ruteo de error: si falla, la ejecucion se detiene sin auditoria. El cuerpo del POST toma `origen_message_id` de `$('Normalizar entrada del incidente')`, que se calcula una vez por ejecucion (correo: Message-ID o UID; telefonia: CallSid; web: id explicito o `web-<execution.id>-<timestamp>`).
- `Responder handoff telefonia` (y=620) cuelga del webhook en paralelo con `Sellar ingreso telefonia` (y=528); con `executionOrder: v1` las ramas se ejecutan por posicion, de modo que la respuesta del handoff se emite despues de la cadena de alta. El backend espera esa respuesta con `TELEFONIA_HANDOFF_TIMEOUT_S = 30.0` (`App/Backend/app/utils/n8n_webhook.py`, fire-and-forget: un timeout solo produce el log `telefonia_handoff_failed`).
- `docker-compose.yml`: `EXECUTIONS_TIMEOUT=300` y `EXECUTIONS_TIMEOUT_MAX=600` para N8N (C-36), preservados por `test_n8n_execution_timeouts_are_preserved`.
- Backend `App/Backend/app/services/incidente_service.py::create_and_classify`: Paso 0 cortocircuita por `origen_message_id` y devuelve el incidente existente sin reclasificar ni notificar; Paso 4 inserta con `flush()` ANTES de clasificar, y el indice UNIQUE (migracion 005) serializa la carrera: la segunda insercion concurrente espera el commit de la primera, recibe `IntegrityError`, hace rollback y devuelve la ganadora. `ClasificacionLog` tiene un unico sitio de alta (`_apply_classification`), por lo que hay exactamente un registro por incidente creado por el intake. En ambos caminos de replay la respuesta (`IncidenteCreateResponse`) sale con `destinatarios_revision = []` (solo se resuelven en el alta original), y N8N cae entonces al respaldo `$env.OPERATOR_EMAIL`.
- Resiliencia Gemini del backend (C-58): `gemini_timeout_seconds=30`, `gemini_max_retries=2`, `gemini_total_timeout_seconds=60`; el presupuesto total solo impide agendar nuevos intentos, por lo que la latencia practica de peor caso de una clasificacion ronda 60-62 s (cota teorica inferior a 90 s).
- Pruebas existentes: `test_api_incidentes.py::test_c33_idempotencia_por_origen_message_id` cubre el replay secuencial en SQLite; no hay prueba de carrera contra PostgreSQL. `test_n8n_workflow.py` declara una politica de reintento para nodos pagos (tope 3, espera minima 500 ms) y su conteo de funciones `test_` esta atado a la guia (`Verifica 171 propiedades estructurales`, `test_c40_guide_test_count_matches_suite`).

**Pruebas de extremo a extremo (bloque 3)**

- `scripts/dry_run/dry_run.py` levanta el stack con `scripts/dry_run/compose.dry-run.yml` (clave Gemini ficticia, codigo fuente montado), importa y publica una copia de costo cero del workflow (`_workflow_for_dry_run`: inyecta credenciales locales en `Login operador` REEMPLAZANDO sus `parameters` ---con lo que se perderia un `options.timeout`---, elimina los nodos con credenciales `REPLACE_WITH_*`, entre ellos el trigger IMAP y el webhook telefonico) y verifica por el webhook `incidente-web` la persistencia y el canal (`e2e:webhook-response`, `e2e:persisted`, `e2e:canal`). Llama al backend por `https://localhost` con `ssl.CERT_NONE`. No afirma la etapa del clasificador, pese a que el escenario "Resolucion deterministica sin escalada" de la spec `dry-run-harness` lo exige.
- El arnes es manual (`make dry-run`); ni el arnes ni sus pruebas (`scripts/dry_run/test_*.py`) corren en `.github/workflows/ci.yml`.
- La guarda de costo (c-45) evalua contadores post-reserva (`budget_cost_usd > budget_usd`): con `COST_GUARD_BUDGET_USD=0` toda llamada paga se deniega y la politica `deterministic_review` degrada sin invocar al proveedor.
- Tesis: `06-implementacion.tex:85` ("En el nivel superior no se dispone de pruebas de extremo a extremo que instancien N8N ..."), y en el mismo parrafo una clausula desactualizada: las pruebas PostgreSQL usan "un mecanismo de omision automatica (`pytest.skip`)", cuando la suite vigente falla de forma ruidosa (`pytest.fail` en `tests/conftest.py`).
- Spec `tesis-document`: el requisito "Verificabilidad de las afirmaciones de pruebas del Capitulo 6" prohibe declarar pruebas E2E "porque ninguna prueba del repositorio instancia N8N", y el escenario "Perimetro de seguridad consistente" de "Coherencia tecnica entre la tesis y el sistema implementado" exige redaccion condicional si el proxy no forma parte del despliegue publicado.

Interesados: el equipo (decide si aplica el change y cada bloque), c-128 (tabla de objetivos), c-136 (integracion de la release `v1.2.0`) y, como lector, el evaluador.

## Goals / Non-Goals

**Goals:**

- Bloque 1: convertir el borde TLS existente en una capacidad **verificada en ejecucion** sobre el despliegue de referencia de la release, con evidencia reproducible, y alinear la spec y la tesis con lo desplegado sin sobreafirmar.
- Bloque 2: agregar reintentos **acotados e idempotentes** en el tramo de alta N8N -> backend, demostrar con PostgreSQL que ningun entrelazado de intentos duplica incidentes ni clasificaciones, y mantener la respuesta de replay observablemente equivalente.
- Bloque 3: convertir el arnes existente en una **prueba de humo de extremo a extremo** con N8N activo, de costo cero garantizado, ejecutable en CI de forma opcional y con evidencia versionable.
- Los tres: actualizar la tesis solo en la medida de lo efectivamente aplicado y definir la interfaz con c-128 y c-136.

**Non-Goals:**

- **Cola de respaldo en el backend y alta asincronica.** Un outbox o un broker con trabajador de reproceso, o un alta `202 Accepted` con completitud diferida, cambiaria el contrato de alta que consumen el formulario web (que espera el numero de incidente en la respuesta), el SMS al llamante y la medicion `ingresado_en`/`persistido_en` en la que se apoyan los resultados centrales del capitulo 7; ademas exige infraestructura que el stack retiro (Redis, c-62). Su costo y su radio de impacto exceden un change opcional sobre una tesis en revision final. Queda como trabajo futuro en `10-recomendaciones.tex`.
- Afirmar que la campana experimental corrio con TLS o con reintentos: ambos cambios son posteriores a la medicion y no la alteran.
- Reconfigurar el borde: no se pasa a TLS 1.3 exclusivo, no se agrega mTLS interno, no se cambia el binding de 80/443 ni se incorporan certificados de una CA publica (responsabilidad del adoptante).
- Ruteo de error para `Login operador` (`continueErrorOutput` con auditoria): cambiaria el contrato N8N-AUDIT-002 y las guardas de canal; se registra como riesgo residual.
- Reubicar `Responder handoff telefonia` para responder al recibir (ack inmediato): alteraria el flujo telefonico medido en c-52/c-70.
- Prueba E2E del canal telefonico (Twilio es pago) y de la etapa Gemini real.
- Cambios de esquema de base de datos, de OpenAPI, de las cinco cadenas de categoria o de los numeros canonicos del capitulo 7.
- Reescribir la tabla de cumplimiento de objetivos (`09-conclusiones.tex`): la posee c-128. A lo sumo, si c-128 ya se aplico, este change actualiza el calificativo de la fila del objetivo especifico 1 (D11).

## Decisions

### D1 - Tres bloques independientes con una superficie compartida minima

Cada bloque tiene su seccion de tareas, su verificacion y su texto de tesis, y puede aplicarse solo. La superficie compartida se reduce a dos piezas: el arnes `scripts/dry_run/` (ya existe, cada bloque agrega su grupo de checks) y el workflow de CI opcional `smoke-stack.yml`, que crea el primero de los bloques 1 o 3 que se aplique (seccion 4 de `tasks.md`). La unica dependencia dura es `e2e:reintento` (bloque 3), que solo se habilita si el bloque 2 esta aplicado. Los deltas de `specs/` de un bloque que no se aplique se retiran antes de archivar (tarea 10.5 de `tasks.md`, con el mapa requisito -> bloque), para que las specs archivadas no declaren capacidades inexistentes.

Orden sugerido: bloque 2 (resiliencia real del sistema) -> bloque 3 (verifica el 2 en ejecucion y deja la infraestructura de humo) -> bloque 1 (reutiliza esa infraestructura) -> texto de tesis de los bloques aplicados -> corrida de evidencia.

**Alternativas consideradas:** un change monolitico (descartado: el change es opcional y el equipo debe poder adoptar solo una parte) y tres changes separados (descartado: comparten parrafos de la tesis, el arnes y la interfaz con c-128/c-136; separarlos multiplica la coordinacion).

### D2 - TLS: verificar lo existente en ejecucion, sin reconfigurar el borde

"Despliegue de referencia de la release" se define como la composicion versionada en el commit de la release (`docker-compose.yml` + `nginx/nginx.conf`) levantada en limpio con certificados autofirmados efimeros generados por `openssl/generate-certs.sh`. Sobre ese stack, un grupo `tls:*` del arnes verifica: `docker compose config` valido; handshake TLS 1.3 y TLS 1.2 exitosos con SNI `localhost`; rechazo de TLS 1.1 (el cliente ofrece como maximo 1.1 con nivel de seguridad que lo habilite; si el cliente local no puede ofrecerlo, el check queda PENDING y no cuenta como exito); identidad del servidor contra el certificado generado (como ancla de confianza o, si el verificador de la plataforma rechaza un autofirmado sin `CA:TRUE`, por huella SHA-256); `GET http://localhost/api/v1/health` -> 301 a `https://localhost/api/v1/health`, con ruta y query preservadas y sin HSTS; `GET https://localhost/api/v1/health` -> 200 desde el backend, con HSTS `max-age=31536000; includeSubDomains`, cabeceras de seguridad y `Server` sin version; Host/SNI desconocido -> conexion cerrada sin respuesta (444). Pruebas estructurales offline complementan: rutas de certificados consistentes entre compose, `nginx.conf` y los scripts; solo TLSv1.2/TLSv1.3 en toda directiva `ssl_protocols`; HSTS solo en el bloque 443.

Se implementa en Python de biblioteca estandar dentro del arnes (mismo modelo de checks y contrato de exit code).

**Alternativas consideradas:** (a) pruebas con contenedores dentro de la suite del backend (descartado: la suite debe seguir offline; Docker solo en el workflow opcional); (b) escaneres externos como testssl.sh o sslyze (descartado: dependencia de terceros con procedencia a verificar, red y alcance excesivo para un humo); (c) script bash con curl/openssl (descartado: portabilidad con PowerShell y duplicacion del arnes); (d) llevar el borde a TLS 1.3 exclusivo para cumplir la spec vieja (descartado: la tesis ya declara 1.2/1.3, TLS 1.2 conserva compatibilidad con los clientes del tunel y con Twilio, y tocar la configuracion productiva es HIGH sin beneficio). Se reconcilia la spec con lo desplegado.

### D3 - Invariante de exposicion: Nginx es la unica superficie fuera de loopback

Se corrige el comentario de cabecera de `docker-compose.yml` (unico cambio previsto en configuracion, CP1) y se agrega una prueba estructural que trata un mapeo desnudo `"<host>:<contenedor>"` como publicacion en todas las interfaces y exige que solo `nginx` la use, con 80 y 443. El grupo `tls:*` lo confirma sobre `docker compose config`.

**Alternativa considerada:** acotar Nginx a `127.0.0.1` (descartado: el borde debe atender a los clientes de la organizacion; un borde solo-loopback anula su funcion y la decision de exposicion corresponde al adoptante).

### D4 - Alcance exacto de la afirmacion TLS en la tesis

La tesis pasa a declarar que la terminacion TLS 1.2/1.3 en Nginx "se verifica de forma automatizada sobre el despliegue de referencia de la release v1.2.0" (prueba de humo, Anexo B / runbook) y conserva, en la misma frase o la siguiente, que el despliegue usado para la campana experimental no incluyo el proxy, de modo que las mediciones del capitulo 7 no dependen de TLS. Se aclara que el certificado de referencia es autofirmado y que la produccion requiere un certificado emitido por una CA (adoptante). Afecta `05-arquitectura.tex` (`subsec:vision-general`), `11-aspectos-legales.tex` (`subsec:seguridad-tecnica`) y el Anexo A de `12-anexos.tex`. Ningun texto afirma TLS en la campana ni en la red interna de Docker (que sigue siendo HTTP dentro del perimetro de confianza).

**Alternativa considerada:** mantener la redaccion condicional actual y solo agregar la evidencia en el repositorio (descartado: el descuento del criterio 5 es sobre lo que la tesis declara; sin texto, la evidencia no se lee).

### D5 - Reintento con los parametros nativos de N8N, sin nodos nuevos

Se declaran `retryOnFail`, `maxTries`, `waitBetweenTries` y `parameters.options.timeout` en los dos nodos HTTP del tramo de alta. N8N 2.11.2 admite `maxTries` entre 2 y 5 y `waitBetweenTries` entre 0 y 5000 ms, con espera fija (sin retroceso exponencial). Valores propuestos (a confirmar en CP3):

| Nodo | `maxTries` | `waitBetweenTries` | `timeout` por intento | Peor caso del nodo | Ventana ante falla inmediata |
|------|-----------:|-------------------:|----------------------:|-------------------:|-----------------------------:|
| `Login operador` | 3 | 5000 ms | 10000 ms | 3x10 + 2x5 = 40 s | 10 s |
| `HTTP POST a MESA-AYUDAS` | 3 | 5000 ms | 75000 ms | 3x75 + 2x5 = 235 s | 10 s |

Invariantes que fijan las pruebas estructurales (no solo los valores): (i) peor caso combinado del tramo (40 + 235 = 275 s) por debajo de `EXECUTIONS_TIMEOUT` (300 s), de modo que aun en el caso patologico la ejecucion alcanza la rama de error y la auditoria en lugar de ser cancelada por el tope global; (ii) `timeout` del POST mayor que el presupuesto de clasificacion del backend (la prueba lo fija contra `gemini_total_timeout_seconds` = 60 s; los 75 s elegidos dejan margen sobre la latencia practica de peor caso de ~62 s, ver Context), para que una clasificacion lenta pero valida no dispare un reintento espurio; (iii) `maxTries` del POST no mayor que 3, el mismo tope que el proyecto fija para reintentos con potencial costo pago (C-36/c-58); (iv) `onError: continueErrorOutput` del POST preservado como camino terminal tras agotar los intentos.

N8N reintenta cualquier error, incluidos los 4xx. Para el POST es inocuo (el alta es idempotente y un 422 es deterministico: tres intentos y rama de error). Para el login, un 401 por credencial mal configurada suma intentos fallidos al bloqueo por cuenta (c-63a); se acepta como riesgo documentado (ver Risks).

La espera fija no es retroceso exponencial: la tesis lo declara asi. El retroceso exponencial con jitter sigue donde importa, entre el backend y Gemini (C-58).

**Alternativas consideradas:** (a) bucle `Wait` + `Code` con retroceso exponencial y clasificacion de codigos de estado (descartado: agrega 3-4 nodos, rompe los conteos canonicos 32/29 propagados en tesis, guia, pruebas y `conteos-canonicos-tecnicos.md` (c-109), y los bucles en N8N son una fuente conocida de ejecuciones colgadas); (b) reintentar solo el POST (descartado: el login es la primera llamada al backend; un reinicio del backend falla ahi primero y sin ruteo de error, de modo que la proteccion seria nominal); (c) `maxTries=5` (descartado: rompe el presupuesto de 300 s y amplifica el costo pago patologico); (d) `Never Error` para filtrar 4xx (descartado: cambia la semantica de fallo aguas abajo y exige ramas nuevas).

### D6 - La idempotencia se apoya en el backend existente; se demuestra contra PostgreSQL

No se toca el esquema ni el normalizador. El reintento de N8N reenvia el mismo cuerpo porque la expresion lee la salida de `Normalizar entrada del incidente`, calculada una sola vez por ejecucion (incluido el id web generado). El invariante es: para un mismo `origen_message_id`, cualquier entrelazado de intentos (replay secuencial, carrera concurrente, timeout del lado N8N con commit tardio del primer intento) produce exactamente una fila de `incidente`, exactamente un registro de `clasificacion_log` y respuestas con el mismo `id`. Se verifica con una prueba de integracion PostgreSQL que lanza altas concurrentes (`asyncio.gather`) con un clasificador espia lento: la insercion se serializa en el indice UNIQUE, la perdedora toma la rama `IntegrityError` y el clasificador se invoca una sola vez. SQLite no modela la espera por bloqueo de fila, por eso la prueba es `@pytest.mark.integration`.

Residual: una entrada sin `origen_message_id` (correo sin Message-ID ni UID, telefonia sin CallSid; no observado y contrario a los contratos vigentes) no queda protegida. No se genera una clave de respaldo para correo o telefonia porque N8N-WEB-DEDUP-001 exige que esas ramas no cambien y alteraria la deduplicacion entre ejecuciones de C-69.

### D7 - Equivalencia observable de la respuesta de replay

En los dos caminos de replay (cortocircuito y `IntegrityError`), si el incidente existente requiere revision humana, el servicio re-resuelve `destinatarios_revision` con `NotificationRecipientService` (la misma lectura del alta original) antes de devolverlo. No se reclasifica, no se re-despacha `notify_n8n`, no se persiste nada nuevo y el contrato OpenAPI no cambia (el campo ya existe). Sin esto, el caso que este change vuelve probable (reintento tras timeout con commit tardio) notificaria al respaldo `OPERATOR_EMAIL` en lugar de a los destinatarios del sector.

**Alternativas consideradas:** aceptar el respaldo (descartado: degradacion silenciosa justo en el camino que se introduce); persistir los destinatarios (descartado: NR-006 prohibe persistirlos o exponerlos).

### D8 - Trazabilidad de los intentos

`clasificacion_log` conserva exactamente un registro por clasificacion ejecutada: un replay no agrega registros porque no reclasifica (tampoco paga). Cada replay que alcanza el backend emite `incidente_idempotente` o `incidente_idempotente_carrera` con `origen_message_id` e `incidente_id`, sin PII; los intentos que no alcanzan el backend (conexion rechazada) solo son visibles en N8N. La frase de `06-implementacion.tex` que afirma que `clasificacion_log` "preserva el historial de cada intento" se corrige a esta semantica.

**Alternativa considerada:** persistir un contador o una tabla de replays (descartado: migracion y cambio de OpenAPI sin consumidor analitico).

### D9 - Timeout del handoff telefonico acorde al presupuesto de reintentos

Como la respuesta del handoff se emite despues de la cadena de alta (Context), los reintentos pueden superar los 30 s que espera el backend y producir `telefonia_handoff_failed` falsos. Se eleva `TELEFONIA_HANDOFF_TIMEOUT_S` a un valor no menor que el peor caso del tramo de alta (se propone igualarlo a `EXECUTIONS_TIMEOUT`, 300 s) y una prueba cruzada lo compara con el presupuesto calculado desde `n8n/workflow.json`. El handoff sigue siendo fire-and-forget en una tarea retenida: un margen amplio no afecta la respuesta HTTP del callback (la propia justificacion de c-70).

**Alternativas consideradas:** responder el handoff al recibir, reubicando el nodo (diferido: altera el flujo telefonico medido); aceptar los falsos fallos (descartado: la observabilidad mentiria).

### D10 - Producto acotado entre reintentos de transporte y reintentos del proveedor

El peor caso de invocaciones pagas por incidente es `maxTries(POST) x (gemini_max_retries + 1) = 3 x 3 = 9`, y solo si cada intento alcanza la clasificacion y luego falla antes del commit; en la practica el primer intento que confirma cortocircuita a los siguientes (D6). La guarda de costo reserva el peor caso de cada clasificacion y sigue siendo el tope global. Una prueba de configuracion verifica el producto contra los valores vigentes del workflow y de `Settings`.

### D11 - Interfaz con c-128: el objetivo especifico 1

El objetivo especifico 1 exige arquitectura distribuida y modular, "comunicacion asincronica entre componentes" e "interfaces REST sobre HTTP cifrado". Contrato que este change ofrece a c-128:

| Componente del objetivo 1 | Sin c-135 | Con bloque 1 | Con bloque 2 | Con bloque 3 |
|---|---|---|---|---|
| HTTP cifrado | diseno no verificado | verificado en el despliegue de referencia (no en la campana) | sin cambio | el humo recorre la API a traves del borde |
| Comunicacion asincronica | alta sincronica sin reintentos; notificaciones y handoff ya son fire-and-forget | sin cambio | alta **sincronica** con reintentos idempotentes acotados | sin cambio |
| Interfaces REST, modularidad | cumplido | sin cambio | sin cambio | ejercitado de extremo a extremo |

Regla: los reintentos no vuelven asincronica la invocacion de alta, por lo que este change, por si solo, no habilita el rotulo "Alcanzado" con la redaccion vigente del objetivo. Recomendacion: c-128 mantiene "Alcanzado parcialmente" y actualiza el calificativo segun los bloques aplicados (por ejemplo, "alta sincronica con reintentos idempotentes; TLS verificado en el despliegue de referencia"). El rotulo "Alcanzado" solo procede si el usuario decide en c-128 reformular el objetivo con justificacion explicita (pregunta abierta OQ3). Si c-128 ya esta aplicado cuando se aplique este change, este change actualiza solo el calificativo de esa fila; si este change no se aplica, c-128 usa el calificativo sin c-135.

### D12 - La prueba E2E extiende el arnes existente

Se reutilizan el levantado del stack, la transformacion de costo cero, el modelo de checks y el contrato de exit code. Grupos nuevos:

- `e2e:etapa`: `GET /api/v1/clasificaciones/incidente/{id}` devuelve exactamente un registro y su etapa es la deterministica (cierra la brecha con el escenario vigente de la spec `dry-run-harness`).
- `e2e:idempotencia`: dos envios al webhook web con el mismo `origen_message_id` explicito (`smoke-<uuid>`) devuelven el mismo incidente y el listado filtrado por ese identificador devuelve uno.
- `e2e:reintento` (opt-in, requiere bloque 2): se desconecta el backend de la red `automation` (DNS/conexion fallan de inmediato), se envia el webhook en segundo plano, se reconecta a los ~2 s (antes de los 5 s de espera) y se exige respuesta con incidente y una sola fila para ese origen; un bloque `finally` garantiza la reconexion.
- Reporte JSON (`--json-out`) con commit, fecha, version de N8N y resultado por check.

La transformacion de costo cero debe conservar el tramo de alta y sus ajustes de nivel de nodo y `options` (hoy reemplaza los `parameters` del login): se ajusta para fusionar `options` y una prueba lo fija. La tesis declara que el humo corre una variante de costo cero del workflow versionado (sin los nodos con credenciales de terceros).

**Alternativas consideradas:** E2E de navegador (descartado: el portal no pasa por N8N y el frontend ya tiene su suite); contenedores en la suite del backend (descartado: debe seguir offline); un runner nuevo (descartado: duplica el arnes).

### D13 - Doble guardarrail de costo cero

Ademas de la clave Gemini ficticia (vigente) y de la asercion de etapa deterministica, el override del arnes fija `COST_GUARD_BUDGET_USD=0`: cualquier escalada se deniega en la guarda y degrada sin intentar la llamada al proveedor (ni siquiera una peticion de red con clave falsa). Twilio no se toca en ninguna variante.

### D14 - Workflow de CI opcional y pruebas offline del arnes en `backend-tests`

`.github/workflows/smoke-stack.yml` se dispara por `workflow_dispatch` y por `push` de tags `v*`, nunca en pull requests. Genera un `App/Backend/.env` de valores ficticios desde `.env.example` y certificados efimeros, levanta el stack de referencia, corre el arnes con los grupos de los bloques aplicados, publica el reporte JSON y los logs de `docker compose` como artefactos y desmonta siempre el stack. Sin secretos, acciones fijadas a version mayor y `timeout-minutes` acotado. Ademas, `backend-tests` ejecuta `python -m pytest scripts/dry_run -q` (offline, segundos) para que el arnes no se degrade. Las pruebas estructurales nuevas del workflow N8N van en un archivo propio (`test_c135_n8n_retry_policy.py`) para no alterar el conteo de `test_n8n_workflow.py` atado a la guia.

**Alternativas consideradas:** job en cada pull request (descartado: +6 a 10 min por PR, builds de imagenes y riesgo de inestabilidad en el camino de fusion); ejecucion programada nocturna (descartado: sin consumidor; puede agregarse luego).

### D15 - Variante de correo con servidor IMAP/SMTP simulado: opcional y separable

Si el equipo la aplica (OQ4), un override propio del arnes agrega un servidor de prueba IMAP/SMTP fijado por digest (procedencia verificada segun AGENTS.md, CP6), el arnes importa credenciales de prueba en N8N (`n8n import:credentials`, sin secretos) y re-vincula el trigger IMAP y los nodos `emailSend` en lugar de eliminarlos, y agrega `email-sim:persisted` (canal 1) y `email-sim:confirmacion` (correo de confirmacion capturado). Si no se aplica, la tesis declara solo el canal web.

**Alternativas consideradas:** buzon real (variante manual vigente; descartado para CI por secretos y red); servidores solo-SMTP (descartados: el trigger necesita IMAP).

### D16 - Texto de la tesis condicionado y con numeros registrados

Cada parrafo se edita solo si su bloque esta aplicado y verificado; ningun texto declara un bloque no aplicado. Los parametros de reintento citados (intentos, espera, timeout) se registran en `docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md` con su fuente (`n8n/workflow.json`), siguiendo la disciplina de c-102/c-109. Se preservan los `\label` existentes. La mencion al reproceso manual de ejecuciones fallidas desde N8N solo se incluye si se verifica en la instancia durante el apply. En el parrafo de pruebas se corrige ademas la clausula `pytest.skip` (la suite falla de forma ruidosa) y se contrasta el conteo de pruebas PostgreSQL citado con la suite vigente. Estimacion de impacto: +15 a +25 lineas netas (+0,3 a +0,5 paginas) con los tres bloques.

## Risks / Trade-offs

- [Romper el flujo N8N operativo al reimportar] -> pruebas estructurales y humo E2E en verde antes de reimportar; exportar el workflow vigente como respaldo; la reimportacion la hace el equipo (CP5); rollback por reimportacion del JSON previo.
- [Duplicados por reintento] -> idempotencia verificada en secuencia (SQLite) y en carrera (PostgreSQL) y en ejecucion (`e2e:idempotencia`); residual de clave nula documentado (D6).
- [Amplificacion del costo pago] -> producto acotado a 9 en el caso patologico (D10), guarda de costo como tope global, `maxTries` del POST con tope 3.
- [Bloqueo de la cuenta del operador por reintentos de un 401] -> solo ocurre con credencial mal configurada, que ya bloquea toda ejecucion; el runbook exige verificar el login tras importar y documenta el desbloqueo.
- [Login agotado sin ruteo de error] -> riesgo preexistente que los reintentos reducen pero no eliminan; queda como Non-Goal y linea futura.
- [Tope global de ejecucion] -> el presupuesto de 275 s deja la rama de error alcanzable; una prueba cruzada compara contra `EXECUTIONS_TIMEOUT`.
- [Tiempo de CI] -> el humo no corre en pull requests; `backend-tests` solo suma pruebas offline.
- [Inestabilidad del humo (Docker, tiempos)] -> ventanas de sondeo amplias; reintento opt-in con margen (reconexion a ~2 s frente a 5 s de espera); desmontaje garantizado.
- [Falsa sensacion de seguridad por certificado autofirmado] -> la tesis y el runbook declaran que el certificado de referencia es autofirmado y que produccion requiere uno emitido por una CA.
- [Divergencia entre el workflow transformado del humo y el versionado] -> prueba que fija que la transformacion conserva el tramo de alta y sus ajustes; la tesis declara la variante.
- [Puertos 80/443 ocupados en la maquina local] -> el runbook lo advierte; el workflow de CI corre en un runner limpio.
- [Conflictos de edicion con c-125, c-130, c-131 y c-132] -> aplicar el texto de este change despues de c-125 y c-131 y antes de c-132; coordinar con c-128 por D11.
- [Deriva de specs preexistente] -> N8N-DOC-004 fija conteos viejos (29/163) que la guia ya no usa; este change no los toca y ubica sus pruebas en un archivo propio para no ampliar esa deriva.
- [Colision de deltas MODIFIED con otros changes de la familia (por ejemplo c-125 sobre el escenario del gate en "Coherencia técnica entre la tesis y el sistema implementado")] -> al archivar, MODIFIED reemplaza el requisito completo; el change que archive en segundo lugar re-basa su bloque sobre la spec vigente conservando ambos cambios (tarea 10.4).
- [La spec `tls-docker-compose` se reconcilia aunque el bloque 1 no se aplique] -> si el bloque 1 se descarta, sus deltas de `tls-docker-compose` y los requisitos TLS de `dry-run-harness` se retiran del change antes de archivar, para no declarar una verificacion inexistente; la reconciliacion pura (sin el requisito de verificacion automatizada) puede conservarse porque describe lo ya desplegado.

## Migration Plan

1. Preparacion: red de seguridad de cada bloque (suites vigentes en verde) y confirmacion de los checkpoints CP1-CP6 segun los bloques que se apliquen.
2. Bloque 2: pruebas y cambios del backend (TDD), luego `n8n/workflow.json` (CP3), guia y transformacion del arnes. Despliegue: exportar el workflow vigente de la instancia operativa, importar el nuevo, verificar credenciales y activacion (CP5).
3. Bloque 3: grupos del arnes, override de costo cero, workflow de CI (CP6) y paso offline en `backend-tests`; corrida local completa.
4. Bloque 1: pruebas estructurales, grupo `tls:*`, comentario del compose (CP1), spec reconciliada, runbook y rotulo del diagrama.
5. Tesis: parrafos de los bloques aplicados (CP2 para TLS), registro de numeros, compilacion y control de paginas.
6. Evidencia: corrida del workflow de humo sobre el commit candidato y resumen en `docs/Tesis/Correcciones/dictamen-correcciones.md`; c-136 la reejecuta sobre el tag `v1.2.0`.

Rollback: por bloque, segun `proposal.md` (Rollback). No hay migraciones de base de datos ni cambios de OpenAPI que deshacer.

## Open Questions

- **OQ1 (usuario):** la organizacion adoptante, ¿opera hoy con TLS en su borde (proxy propio, certificado de una CA)? Si lo confirma con evidencia, la tesis puede mencionarlo; si no, solo se declara el despliegue de referencia.
- **OQ2 (usuario):** ¿se dispone de una instancia N8N para el E2E en CI (runner de GitHub con Docker, repositorio publico) o se prefiere ejecutar el humo solo de forma local y versionar el resumen? ¿Es aceptable el disparo por tag?
- **OQ3 (usuario, interfaz c-128):** ¿se mantiene el objetivo especifico 1 como "Alcanzado parcialmente" con calificativo actualizado (recomendado) o se reformula el objetivo para habilitar "Alcanzado"?
- **OQ4 (usuario):** ¿se aplica la variante de correo con servidor IMAP/SMTP simulado o el humo se limita al canal web?
- **OQ5 (CP3):** confirmar los valores de reintento de D5 (3 intentos, 5000 ms, 10 s para el login y 75 s para el POST).
