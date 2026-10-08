# Tasks: c-62-hardening-infra-red

> BLOQUEANTE: ninguna tarea de implementacion (grupos 2-7) puede empezar sin cerrar el grupo 1. Las Open Questions de `design.md` (OQ-1..OQ-8) cambian el compose y los comandos documentados.

## 1. Baseline y resolucion de decisiones

- [x] 1.1 Capturar el baseline del estado actual: `docker compose config`, `docker compose ps`, y correr `python scripts/preflight/cost_readiness.py`. Verificacion: se registran los puertos publicados actuales y el preflight termina en verde.
- [x] 1.2 Resolver OQ-1..OQ-8 con el autor y registrar la decision elegida en `design.md` (seccion Decisions). Verificacion: no queda ninguna OQ sin respuesta explicita. **RESUELTAS (autor, 2026-10-08): OQ-1=A loopback; OQ-2=A retirar Redis; OQ-3=SI 3 redes; OQ-4=A loopback UI; OQ-5=B override `docker-compose.dev.yml`; OQ-6=SI nginx (diferir CSP); OQ-7=SI corpus loopback; OQ-8=OK sin cambios de comandos.**
- [x] 1.3 Registrar el checklist de no-regresion de CI: imagen de n8n pineada, `N8N_WEBHOOK_URL` con ruta dedicada, `EXECUTIONS_TIMEOUT`/`EXECUTIONS_TIMEOUT_MAX`, y `VITE_API_BASE_URL` del frontend como build arg. Verificacion: el checklist queda escrito y se ejecuta al final (7.5).

## 2. Puertos (D1 / OQ-1, OQ-7, OQ-8)

- [x] 2.1 Aplicar la estrategia de puertos elegida en el compose base (loopback o retiro de publicacion + override) para `postgres`, `redis` y `n8n`. Verificacion: `docker compose config` no muestra publicacion en `0.0.0.0` para 5433/6379/5678.
- [x] 2.2 Aplicar la misma politica al perfil corpus (`postgres-corpus`, `backend-corpus`, `n8n-corpus`) segun OQ-7. Verificacion: `docker compose --profile corpus config` refleja la politica acordada.
- [x] 2.3 Si OQ-1 elige el retiro, crear el mecanismo de acceso de desarrollo opt-in (override o perfil) y verificar que `docker compose` por defecto queda endurecido. Verificacion: el estado por defecto no expone; el opt-in si.
- [x] 2.4 Actualizar los consumidores afectados por el cambio de puerto: `App/Backend/tests/conftest.py` (default `localhost:5433`), `scripts/dry_run/dry_run.py` (`--n8n-port 5678`), `scripts/corpus_ingest/test_corpus_compose_isolation.py` (literales de puerto) y `scripts/up.sh`/`up.ps1` si imprimen URLs. Verificacion: cada archivo referencia el canal de acceso vigente.
- [x] 2.5 Agregar un test estructural (pytest) que lea `docker-compose.yml` y afirme la postura de puertos elegida (por ejemplo, que `postgres` y `redis` no publican, y que `n8n` no esta en `0.0.0.0`). Verificacion: el test pasa con el cambio y falla si se reintroduce la publicacion.

## 3. Redis (D2 / OQ-2)

- [x] 3.1 Confirmar los consumidores reales de Redis: inspeccionar `QUEUE_BULL_REDIS_*`, `EXECUTIONS_MODE`, el workflow y las importaciones del backend; documentar la lista. Verificacion: la lista de consumidores (o su ausencia) queda registrada.
- [x] 3.2 Segun OQ-2, implementar una de las dos opciones: retirar el servicio `redis` (y sus `depends_on`) o aplicar `requirepass` y propagar la credencial a todos los consumidores. Verificacion: `redis-cli` sin credenciales falla, o el servicio no existe.
- [x] 3.3 Si Redis se conserva, agregar `REDIS_PASSWORD` a `.env.example` (raiz) con sustitucion no adivinable y actualizar la documentacion. Verificacion: la credencial vive solo en el `.env` gitignorado.

## 4. Segmentacion de red (D3 / OQ-3, OQ-7)

- [x] 4.1 Declarar las redes `edge`, `data` (`internal: true`) y `automation` en el compose base. Verificacion: `docker compose config` las muestra.
- [x] 4.2 Asignar los servicios base: `edge` (nginx, frontend, backend), `data` (postgres, backend), `automation` (n8n, backend, redis si aplica). Verificacion: `n8n` y `postgres` no comparten ninguna red.
- [x] 4.3 Replicar la segmentacion en el perfil corpus. Verificacion: `docker compose --profile corpus config` respeta las invariantes.
- [x] 4.4 Arrancar el stack y verificar healthchecks y verificacion de salud del arranque. Verificacion: todos los servicios sanos y `/api/v1/health` responde.
- [x] 4.5 Agregar un test estructural que afirme que ninguna red contiene simultaneamente `n8n` y `postgres`. Verificacion: el test pasa.

## 5. nginx y UI de N8N (D4, D6 / OQ-4, OQ-6)

- [x] 5.1 Aplicar `server_tokens off` y los headers de seguridad acordados (`Referrer-Policy`, `Permissions-Policy`, y CSP si se aprueba). Verificacion: `curl -kI https://localhost/` no expone la version y muestra los headers.
- [x] 5.2 Aplicar `limit_req` sobre los endpoints publicos con el umbral acordado. Verificacion: superar el limite produce HTTP 429.
- [x] 5.3 Restringir la UI de N8N segun OQ-4 (loopback, nginx tras autenticacion o solo override). Verificacion: la UI no queda accesible sin autenticacion en `0.0.0.0`.
- [x] 5.4 Verificar que el catch-all `return 444` y la redireccion HTTP->HTTPS siguen intactos. Verificacion: Host desconocido cierra la conexion; `http://localhost/` redirige a HTTPS.

## 6. Separacion de entornos (D5 / OQ-5)

- [x] 6.1 Implementar el mecanismo elegido (perfiles, override o archivos por entorno) con el modo por defecto endurecido. Verificacion: `docker compose config` por defecto aplica la postura endurecida.
- [x] 6.2 Documentar la postura y el comando de cada entorno (dev/test/no-desarrollo). Verificacion: cada entorno tiene su comando de arranque documentado.
- [x] 6.3 Ajustar `scripts/up.sh` y `scripts/up.ps1` si el arranque por defecto cambia (por ejemplo, elegir el perfil de desarrollo para el flujo local). Verificacion: `bash scripts/up.sh` sigue llegando a health OK.

## 7. Documentacion y verificacion

- [x] 7.1 Actualizar `docs/operational-guide.md` (seccion de arranque, `docker compose ps`, acceso a N8N, `TEST_PG_URL`) con los accesos vigentes. Verificacion: la guia no menciona puertos removidos sin su equivalente.
- [x] 7.2 Actualizar `README.md` y `AGENTS.md` (comandos de desarrollo y nota de puertos). Verificacion: los comandos citados funcionan.
- [x] 7.3 Actualizar `.env.example` (raiz) con las variables nuevas (por ejemplo `REDIS_PASSWORD`, si aplica). Verificacion: ninguna credencial real queda versionada.
- [x] 7.4 Recorrer todos los comandos documentados que usaban puertos publicados y ejecutar cada uno o su equivalente. Verificacion: ninguno falla por conexion rechazada.
- [x] 7.5 Correr la verificacion de no-regresion: `python scripts/preflight/cost_readiness.py`, `cd App/Backend && pytest -m "not integration" -q` y el test de aislamiento del corpus. Verificacion: todo en verde y el checklist 1.3 completo.
- [x] 7.6 Ejecutar `openspec validate c-62-hardening-infra-red --strict`. Verificacion: termina sin errores.

## 8. Alineacion del preflight con el workflow post-C-72 (INFRA-008)

> Regresion detectada en el apply de c-62: c-72 retiro el `AI Agent` y el `clasificacion` del body de `n8n/workflow.json` pero NO actualizo `scripts/preflight/`, que corre en CI (job `backend-tests`). Hoy `cost_readiness.py` (2 guardas) y `gemini_readiness.py` (2 guardas) dan RED. Se pliega a c-62.

- [x] 8.1 RED: en `scripts/preflight/test_cost_readiness.py` y `test_gemini_readiness.py`, actualizar los casos al contrato post-c-72 y agregar los faltantes. Verificacion: los tests fallan contra el preflight actual.
- [x] 8.2 GREEN — neutralizar guardas de nodos retirados (patron c-55 `Marcar correo como leido`): en `cost_readiness.py` la guarda `AI Agent`/`options.maxIterations`, y en `gemini_readiness.py` las guardas del nodo modelo Gemini y del `AI Agent` SHALL pasar cuando el nodo esta AUSENTE (retirado por c-72) y fallar solo si reaparece mal configurado. Verificacion: ambas guardas pasan con el workflow de 29 nodos.
- [x] 8.3 GREEN — corregir la guarda del body del `HTTP POST a MESA-AYUDAS` a la postura post-c-72: exigir `origen_message_id` + `origen_evento` y prohibir `clasificacion`/`sector_predicho`/`confianza`. Verificacion: la guarda pasa y falla si se reintroduce `clasificacion`.
- [x] 8.4 Ejecutar `python3 scripts/preflight/cost_readiness.py` y `python3 scripts/preflight/gemini_readiness.py` (ambos GREEN) y `python3 -m pytest scripts/preflight -q` (verde). Verificacion: sin regresiones; `INFRA-008` satisfacible.
