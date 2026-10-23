## Why

El dictamen CONEAU del 22-10-2026 sobre la v10 / release `v1.1.0` (`auditorias/Dictamen_Tesis_v10_v1.1.0_CONEAU_2026-10-22.md`) califica el criterio 5 de la rubrica ("Desarrollo tecnico o experimental", peso 15) con 8 y le descuenta, ademas del gate de revision (que atiende c-125), tres limitaciones que la propia tesis declara: **TLS no desplegado en la instancia validada**, **invocacion sincronica sin reintentos** y **ausencia de pruebas de extremo a extremo con N8N activo** (seccion 6, parrafo "En cuanto a la propuesta..."; tabla de calificacion). Las mismas carencias sostienen la observacion de la seccion 3: el objetivo especifico 1 exige "comunicacion asincronica ... sobre HTTP cifrado" y dos de sus tres propiedades no se cumplen en la version evaluada. La proyeccion final del dictamen es explicita: alcanzar la banda de excelencia "exige, ademas, atacar los descuentos residuales del criterio 5 (TLS en la instancia validada, reintentos idempotentes, pruebas de extremo a extremo)", lineas que el evaluador situa **fuera de sus recomendaciones** y plantea "como trabajo separado".

Por eso este change es **OPCIONAL para la aprobacion** (no levanta ninguna de las observaciones A1-A4 ni B4-B16, que atienden c-125 a c-134) pero **necesario para llevar el criterio 5 a la banda de excelencia**. Se ejecuta solo si el equipo decide invertir en el; sus tres bloques son independientes y cada uno puede aplicarse, posponerse o descartarse por separado.

La exploracion del repositorio (solo lectura) muestra que el punto de partida es mejor que lo que la tesis declara, pero sin evidencia citable:

- **TLS**: el borde Nginx con TLS 1.2/1.3, redireccion 301, HSTS y catch-all 444 existe desde C-20 (`nginx/nginx.conf`, `openssl/generate-certs.{sh,ps1}`), pero solo lo verifican pruebas estructurales (c-62); ninguna prueba lo ejercita en ejecucion, y la spec `tls-docker-compose` quedo desalineada de lo implementado (declara solo TLS 1.3, certificados en `nginx/certs/server.*`, scripts bajo `scripts/`, `N8N_PROTOCOL=https` y Redis).
- **Reintentos**: el backend ya es idempotente por `origen_message_id` (cortocircuito C-33, indice UNIQUE y rama `IntegrityError`, C-69), pero el nodo `HTTP POST a MESA-AYUDAS` solo declara `onError: continueErrorOutput`, sin `retryOnFail` ni `timeout` explicito, y `Login operador` ---la primera llamada al backend del tramo de alta--- no declara ni reintento ni ruteo de error.
- **E2E**: el arnes de dry-run (`scripts/dry_run/`) ya instancia N8N con una copia de costo cero del workflow y verifica el canal web hasta la persistencia, pero es manual, no corre en CI y no deja evidencia versionada, de modo que la tesis no puede citarlo.

## What Changes

Tres bloques independientes (el `design.md` define su aplicacion por separado y el `tasks.md` los agrupa en secciones autonomas):

- **Bloque 1 - TLS verificado en el despliegue de referencia** (gobernanza **HIGH**)
  - Prueba de humo automatizada del borde HTTPS sobre el stack de referencia (`docker-compose.yml` de la release): validacion de `docker compose config`, arranque con certificado autofirmado efimero, handshake TLS 1.2 y 1.3 verificado contra el certificado generado, rechazo de TLS 1.1, redireccion HTTP->HTTPS con preservacion de ruta y query, cabeceras HSTS y de seguridad, ocultamiento de version, catch-all ante Host/SNI desconocido y salud del backend a traves del proxy. Se implementa como grupo `tls:*` del arnes existente, mas pruebas estructurales offline.
  - Invariante de exposicion: el unico servicio publicado fuera de loopback es el borde Nginx (80 redirige a 443); se corrige el comentario de cabecera de `docker-compose.yml`, que hoy afirma que 80/443 estan acotados a loopback cuando se publican en todas las interfaces.
  - Reconciliacion de la spec `tls-docker-compose` con lo desplegado y runbook de verificacion con evidencia versionada.
  - Tesis: 05-arquitectura ("Vision general"), 11-aspectos-legales ("Seguridad tecnica") y Anexo A pasan de "diseno" a "capacidad verificada en el despliegue de referencia de la release v1.2.0", **sin afirmar que la campana experimental corrio con TLS** (no corrio: el despliegue de medicion no incluyo el proxy).
- **Bloque 2 - Reintentos idempotentes N8N -> backend** (gobernanza **MEDIUM**)
  - Politica de reintento acotada con los parametros nativos de N8N 2.11.2 (`retryOnFail`, `maxTries` 2-5, `waitBetweenTries` 0-5000 ms, espera fija) y `timeout` explicito en `Login operador` y `HTTP POST a MESA-AYUDAS`, con presupuesto de peor caso por debajo del tope de ejecucion (`EXECUTIONS_TIMEOUT=300`); se conserva `continueErrorOutput` como camino terminal tras agotar los intentos. Sin nodos nuevos: los conteos 32/29 no cambian.
  - Verificacion en el backend: prueba de integracion PostgreSQL de reintentos concurrentes con el mismo `origen_message_id` (una sola fila, una sola clasificacion, un solo registro en `clasificacion_log`, misma respuesta) y equivalencia observable de la respuesta de replay (se re-resuelven `destinatarios_revision` cuando el incidente requiere revision, hoy vacios en el replay).
  - Ajuste del timeout del handoff telefonico del backend para que no registre falsos `telefonia_handoff_failed` cuando N8N reintenta.
  - Pruebas estructurales nuevas del workflow; guia del workflow actualizada.
  - Tesis: 06-implementacion (primer y tercer desafio) y 10-recomendaciones (la cola de respaldo y el alta asincronica quedan como trabajo futuro). **La cola de respaldo queda fuera de alcance** (Non-Goal fundamentado en `design.md`).
- **Bloque 3 - Smoke E2E con N8N activo** (gobernanza **MEDIUM**)
  - Extension del arnes de dry-run: aserciones de etapa deterministica (costo cero por construccion), idempotencia ante reenvio por el webhook, recuperacion ante indisponibilidad transitoria del backend (si el bloque 2 esta aplicado), doble guardarrail de costo (clave Gemini ficticia y presupuesto de la guarda de costo en cero) y reporte JSON como evidencia.
  - Workflow de CI **opcional** (`workflow_dispatch` y tags `v*`), sin secretos, que levanta el stack de referencia y corre el arnes; las pruebas offline del arnes se suman al job `backend-tests`.
  - Variante opcional del canal correo con servidor IMAP/SMTP simulado (separable; si no se aplica, la tesis declara solo el canal web).
  - Tesis: 06-implementacion ("Pruebas automatizadas") pasa de "no se dispone de pruebas de extremo a extremo" a "se dispone de una prueba de humo de extremo a extremo" con su alcance exacto (variante de costo cero, canales cubiertos, Gemini y telefonia excluidos).

Ningun bloque modifica el esquema de base de datos, el contrato OpenAPI, las cinco cadenas de categoria, los numeros canonicos ni los resultados del capitulo 7.

### Gobernanza y checkpoints de aprobacion humana

| Bloque | Nivel | Checkpoints (el apply se detiene y espera aprobacion) |
|--------|-------|--------------------------------------------------------|
| 1 - TLS | HIGH | CP1: cualquier edicion de `nginx/nginx.conf`, `docker-compose.yml` u `openssl/generate-certs.*` (lo previsto es solo el comentario de cabecera del compose); CP2: redaccion de la tesis que cambia TLS de "diseno" a "verificado". |
| 2 - Reintentos | MEDIUM | CP3: valores de `maxTries`/`waitBetweenTries`/`timeout` antes de editar `n8n/workflow.json`; CP4: cambio de equivalencia del replay en el servicio; CP5: reimportacion del workflow en la instancia operativa (la ejecuta el equipo, nunca el agente). |
| 3 - Smoke E2E | MEDIUM | CP6: alta del workflow de CI con disparador por tag y, si se aplica la variante de correo, procedencia y pin de la imagen IMAP/SMTP de terceros. |

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tls-docker-compose` (bloque 1): se reconcilian los requisitos con lo desplegado (TLS 1.2/1.3, rutas de certificados y scripts, postura de N8N en loopback, URL base del frontend, servicios sin Redis) y se agregan la verificacion automatizada del borde TLS en el despliegue de referencia y el invariante de exposicion unica del borde.
- `n8n-workflow` (bloque 2): se agrega la politica de reintento acotado e idempotente de los nodos HTTP del tramo de alta, con timeout explicito, presupuesto de peor caso y preservacion del ruteo de error.
- `incident-origin-correlation` (bloque 2): se agregan la idempotencia del alta bajo reintentos concurrentes (verificada contra PostgreSQL) y la equivalencia observable de la respuesta de replay, con evento estructurado por replay.
- `classification-resilience` (bloque 2): se acota el producto entre los reintentos de transporte del alta (N8N) y los reintentos del proveedor (backend), y se exige que un replay no invoque al proveedor pago.
- `dry-run-harness` (bloques 1 y 3): nuevos grupos de verificacion (`tls`, etapa, idempotencia, reintento, correo simulado opcional), doble guardarrail de costo y reporte de evidencia.
- `ci-pipeline` (bloques 1 y 3): workflow opcional de humo del stack de referencia y ejecucion offline de las pruebas del arnes en `backend-tests`.
- `tesis-document` (bloques 1 a 3): se modifican los requisitos que hoy prohiben declarar pruebas E2E y condicionan la afirmacion de TLS, y se agrega la declaracion acotada del endurecimiento tecnico, condicionada a los bloques efectivamente aplicados.

## Impact

- **Bloque 1**: `scripts/dry_run/` (grupo `tls`, pruebas), `App/Backend/tests/` (pruebas estructurales del borde), `docker-compose.yml` (solo comentario de cabecera, CP1), `docs/dry-run-harness.md`, runbook nuevo `docs/runbook-smoke-stack-referencia.md`, `docs/diagrams/despliegue.md` (rotulo "TLS 1.3" -> "TLS 1.2/1.3"), tesis `05-arquitectura.tex`, `11-aspectos-legales.tex`, `12-anexos.tex`. Sin cambios esperados en `nginx/nginx.conf` ni en `openssl/generate-certs.*`; cualquier defecto que revele la prueba de humo se corrige solo tras aprobacion humana.
- **Bloque 2**: `n8n/workflow.json` (configuracion de 2 nodos, sin nodos nuevos), `App/Backend/app/services/incidente_service.py` (destinatarios en el replay), `App/Backend/app/utils/n8n_webhook.py` (timeout del handoff), pruebas nuevas (`test_c135_*`), `scripts/dry_run/test_workflow_transform.py`, `docs/n8n-workflow-guide.md`, tesis `06-implementacion.tex`, `10-recomendaciones.tex`. Requiere **reimportar el workflow** en la instancia N8N operativa (paso manual del equipo).
- **Bloque 3**: `scripts/dry_run/` (checks, override de compose, variante de correo opcional), `.github/workflows/smoke-stack.yml` (nuevo), `.github/workflows/ci.yml` (un paso offline), `Makefile`, `docs/dry-run-harness.md`, tesis `06-implementacion.tex`.
- **Paginas de la tesis**: estimacion +15 a +25 lineas netas (+0,3 a +0,5 paginas) si se aplican los tres bloques; el control del presupuesto global de paginas queda en c-136.
- **Dependencias**: sin dependencias de codigo con c-125 a c-134. En la tesis: comparte `06-implementacion.tex` con c-125 y c-130, `10-recomendaciones.tex` con c-131 y todo el texto con c-132 (aplicar este change antes de c-132). **Interfaz con c-128**: este change aporta evidencia para el objetivo especifico 1, pero los reintentos no vuelven asincronica la comunicacion; el rotulo de la fila lo decide c-128 segun la regla de `design.md` (D11). **Interfaz con c-136**: la release `v1.2.0` debe reejecutar la prueba de humo sobre el commit etiquetado y registrar la evidencia si este change se aplica antes.
- **CI**: el workflow de humo no corre en pull requests (no agrega tiempo al camino de fusion); el job `backend-tests` suma solo pruebas offline del arnes (segundos).

## Rollback

Cada bloque se revierte por separado con `git checkout <commit-previo> -- <archivos del bloque>`:

- Bloque 1: revertir pruebas, grupo `tls`, runbook, comentario del compose y parrafos de la tesis; la configuracion TLS no cambia, por lo que no hay despliegue que deshacer.
- Bloque 2: revertir `n8n/workflow.json` y **reimportarlo** en la instancia N8N operativa; revertir los dos archivos del backend y sus pruebas. Sin migraciones: no hay datos que restaurar.
- Bloque 3: eliminar `.github/workflows/smoke-stack.yml`, revertir el paso agregado a `ci.yml` y las extensiones del arnes.

Si la tesis ya se recompilo con el texto de un bloque revertido, ese texto se revierte en el mismo commit para no declarar una capacidad inexistente (regla de `tesis-document`).

## Success Criteria

- [ ] Bloque 1: el grupo `tls:*` del arnes pasa completo sobre el stack de referencia levantado con certificados efimeros, localmente y en el workflow de humo; las pruebas estructurales del borde pasan offline; la spec `tls-docker-compose` describe lo desplegado.
- [ ] Bloque 1: la tesis declara TLS 1.2/1.3 como verificado en el despliegue de referencia y conserva, sin ambiguedad, que la campana experimental no uso el proxy.
- [ ] Bloque 2: `n8n/workflow.json` declara la politica de reintento en `Login operador` y `HTTP POST a MESA-AYUDAS` dentro de los limites de `design.md`, con 32 nodos totales y 29 operativos; las pruebas estructurales nuevas pasan.
- [ ] Bloque 2: la prueba de integracion PostgreSQL de reintentos concurrentes con el mismo `origen_message_id` deja una sola fila de incidente y un solo registro de clasificacion, y ambas respuestas devuelven el mismo incidente.
- [ ] Bloque 3: el arnes completa en verde los grupos de etapa deterministica e idempotencia (y reintento, si el bloque 2 esta aplicado) sin ninguna llamada paga, y el workflow de humo publica el reporte JSON como artefacto.
- [ ] Global: `pytest -m "not integration"`, `pytest -m integration`, `ruff check .` y la suite estructural del workflow quedan en verde; ninguna afirmacion de la tesis declara un bloque no aplicado.
