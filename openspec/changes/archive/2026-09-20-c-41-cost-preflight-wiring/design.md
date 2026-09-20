## Context

Ver `proposal.md — Why` para la motivacion. Estado actual y restricciones que moldean el enfoque:

- `scripts/preflight/cost_readiness.py` ya es un checker puro, offline y callable por CLI: `main()` imprime `format_summary(checks)` y devuelve `exit_code(checks)` (0 solo si hay checks y todos PASS; `cost_readiness.py:485-541`). No necesita refactor para cablearse. Su suite `scripts/preflight/test_cost_readiness.py` ya cubre guardas presentes/ausentes con fixtures.
- `scripts/up.sh` es el camino real del operador (`make up` delega en el, `Makefile:26-27`). Su preflight de entorno hoy solo exige `GEMINI_API_KEY` y `PSEUDONYMIZATION_ENCRYPTION_KEY` (`up.sh:50`), y termina antes de Docker si falta o es placeholder (`up.sh:106-142`). `Settings()` exige ademas `JWT_SECRET_KEY` (`App/Backend/app/config/settings.py:108`), cuyo placeholder en la plantilla es `your-jwt-secret-key-here` (`App/Backend/.env.example:29`).
- `scripts/up.ps1` replica el mismo flujo en PowerShell (`up.ps1:58,117-149,253`), y la spec `local-bootstrap` exige equivalencia multiplataforma. No hay `pwsh` ni arnes de tests PowerShell en el repo.
- El harness `scripts/tests/test_up_preflight.sh` prueba el preflight de entorno por dos vias: ejecucion del script como subproceso (casos que fallan antes de Docker) y `source` + llamada a `check_env_file` en subshell (caso valido), sin levantar Docker (`test_up_preflight.sh:129-146`). Ese patron es el molde para probar el gate nuevo.
- CI (`.github/workflows/ci.yml`) tiene dos jobs. `backend-tests` ya configura Python 3.12, instala `App/Backend/requirements.txt` y tiene pytest; PyYAML NO esta en ese archivo ni en `evaluation/requirements.txt`, solo en `scripts/preflight/requirements.txt`.
- **Gobernanza**: LOW/MEDIUM. Herramientas de operacion de solo lectura; no hay logica de dominio, secretos reales ni cambios de runtime del stack.

## Goals / Non-Goals

**Goals:**

- Que una guarda de costo rota impida arrancar el stack local, con mensaje accionable y sin efectos colaterales.
- Que el preflight y su suite dejen de ser manuales: Makefile y CI los ejecutan.
- Que `JWT_SECRET_KEY` se valide en el mismo preflight de entorno, evitando el crash diferido en `Settings()`.
- Mantener el preflight como dependencia de solo lectura: ningun camino de fallo genera certificados, toca Docker ni modifica archivos.

**Non-Goals:**

- No se cambia la logica de guardas de `cost_readiness.py` ni su suite.
- No se agrega una politica de precios ni se toca el gate pago de `evaluation/run_evaluation.py`.
- No se agrega un arnes de tests PowerShell nuevo (no hay `pwsh` en el entorno); la paridad Windows se verifica de forma estructural.
- No se instala PyYAML automaticamente; el operador lo instala desde `scripts/preflight/requirements.txt`.
- No se modifican `n8n/workflow.json` ni `docker-compose.yml`.

## Decisions

### D1 — El punto de integracion primario es el arranque local (`scripts/up.sh`), y CI/Make lo complementan

El gate vive en `up.sh` porque es el camino que el operador realmente ejecuta (`make up` delega ahi). CI ejecuta la suite + CLI para detectar regresiones en `workflow.json`/`docker-compose.yml`, y el Makefile expone un objetivo `preflight` para invocacion manual discoverable. No se hace que `make up` dependa de `preflight`: los scripts ya son la fuente de verdad y duplicar la corrida seria redundante (y en Windows, si el gate vive en `up.ps1`, tambien queda cubierto).

- **Razon**: el objetivo del change es que el operador NO pueda arrancar canales pagos con guardas rotas. Solo el gate de arranque logra eso; CI por si solo solo detecta regresiones en PRs, y Make por si solo es optativo. La combinacion cubre enforcement (arranque), regresion (CI) y discoverability (Make) sin duplicar ejecucion.
- **Alternativas consideradas**: (a) solo CI — descartado porque un operador puede arrancar localmente sin pasar por CI; (b) solo Make — descartado porque `make` es opcional por spec y `up.sh` debe funcionar directo; (c) un script `preflight.sh` nuevo que envuelva el CLI — descartado porque el CLI ya cumple y una capa extra agrega superficie.

### D2 — Ubicacion del gate en `up.sh`: despues del preflight de entorno y antes de los certificados

`main()` queda: `check_env_file` -> `check_cost_preflight` -> `ensure_certificates` -> `start_stack` -> `wait_for_healthy` -> `verify_health`. Asi, un preflight de costo en FAIL aborta antes de generar certificados o tocar Docker: el fallo es no destructivo por construccion.

- **Razon**: los problemas de `.env` son el primer diagnostico esperado por el operador; el preflight de costo es una verificacion de artefactos del repo que debe bloquear cualquier efecto. Ponerlo despues de los certificados generaria archivos antes de abortar, violando "no side effects".
- **Alternativas consideradas**: (a) antes del preflight de entorno — descartado porque un `.env` faltante es un error mas basico y su mensaje debe salir primero; (b) despues de `start_stack` — descartado porque el stack ya arranco (el objetivo es impedirlo).

### D3 — Deteccion de interprete y seams de test en `up.sh`

Se agrega `COST_PREFLIGHT_SCRIPT` (default `scripts/preflight/cost_readiness.py`) con override `UP_COST_PREFLIGHT`, y deteccion perezosa de interprete (`UP_PYTHON` -> `python3` -> `python`) dentro de la funcion, no en tiempo de `source`. La funcion `check_cost_preflight` captura la salida, la imprime tal cual (el resumen ya nombra las guardas) y devuelve no-cero si el CLI falla; si no hay interprete o la dependencia falta, imprime un error accionable y devuelve no-cero.

- **Razon**: el harness actual hace `source` de `up.sh` para probar funciones puras (`test_up_preflight.sh:138-146`); cualquier deteccion de interprete a nivel top-level bajo `set -e` romperia el source. `UP_COST_PREFLIGHT` permite inyectar un stub que devuelve 0/1 y probar el gate sin PyYAML ni Docker. `UP_PYTHON` permite forzar el interprete.
- **Alternativas consideradas**: (a) invocar `python3` fijo — descartado porque en algunos entornos solo existe `python`; (b) no exponer seams — descartado porque el gate quedaria sin test automatico; (c) parsear el preflight con bash en vez de llamar al CLI — descartado por duplicar logica ya testeada.

### D4 — `JWT_SECRET_KEY` se suma a la lista de secretos requeridos, con placeholder estatico y por plantilla

En `up.sh` y `up.ps1`, `REQUIRED_SECRETS` pasa a incluir `JWT_SECRET_KEY`; se agrega `your-jwt-secret-key-here` a `PLACEHOLDER_VALUES` como respaldo, y la deteccion por plantilla (`collect_placeholders`) ya lo toma automaticamente al estar en `REQUIRED_SECRETS`.

- **Razon**: el patron existente ya resuelve presencia/vacio/placeholder de forma generica sobre `REQUIRED_SECRETS`; agregar la clave no requiere logica nueva. El placeholder estatico evita falsos PASS si la plantilla no esta disponible.
- **Alternativas consideradas**: (a) un chequeo ad-hoc separado — descartado por duplicar el patron; (b) validar formato de la clave (longitud/entropia) — descartado por fuera de alcance y porque el requisito es presencia/no-placeholder.

### D5 — Paridad Windows en `scripts/up.ps1`, verificada de forma estructural

`up.ps1` recibe el mismo `JWT_SECRET_KEY` en `$RequiredSecrets` y un `Invoke-CostPreflight` llamado antes de los certificados, con los mismos overrides `UP_COST_PREFLIGHT`/`UP_PYTHON`. Como no hay `pwsh` ni harness PowerShell, la paridad se verifica con un test estructural en bash (grep de la clave requerida y de la invocacion del preflight en `up.ps1`).

- **Razon**: la spec `local-bootstrap` exige equivalencia multiplataforma; dejar `up.ps1` atras contradiria el requisito modificado y el de equivalencia. La verificacion estructural es la capa mas fuerte disponible sin `pwsh` y es consistente con la verificacion estructural que c-37 uso para la parametrizacion.
- **Alternativas consideradas**: (a) descope de Windows — descartado por romper la equivalencia; (b) instalar `pwsh` y un harness Pester — descartado por dependencia y alcance nuevos; (c) editar `up.ps1` sin ningun test — descartado por Strict TDD.
- **Nota**: se expone como pregunta abierta para que el humano confirme el alcance Windows o lo difiera explicitamente.

### D6 — CI: pasos nuevos dentro del job `backend-tests`, no un job nuevo

Se agregan pasos al job `backend-tests`: instalar `scripts/preflight/requirements.txt`, ejecutar `python -m pytest scripts/preflight/test_cost_readiness.py -q` y ejecutar `python scripts/preflight/cost_readiness.py`, todos desde la raiz del repo.

- **Razon**: el job ya configura Python 3.12 y pytest, asi que los pasos son baratos y no agregan un runner. Un job nuevo duplicaria setup y agregaria latencia sin beneficio. La suite del preflight no corre hoy en CI (follow-up de c-36), por lo que este change cierra ese gap.
- **Alternativas consideradas**: (a) job `cost-preflight` nuevo — descartado por costo/duplicacion; (b) solo ejecutar el CLI sin la suite — descartado porque la suite cubre guardas presentes/ausentes con fixtures, que el CLI sobre el repo real no ejercita; (c) no tocar CI — descartado porque deja el preflight sin proteccion de regresion.

### D7 — Sin refactor de `cost_readiness.py`

No se toca el checker: ya expone CLI con exit code y funciones puras, y su suite ya lo cubre. Cualquier cambio de guardas queda explicitamente fuera de alcance.

- **Razon**: el change es de cableado; el checker funciona y pasa 10/10 sobre el repo actual. Tocar la logica de guardas ampliaria el riesgo y el alcance sin necesidad.
- **Alternativas consideradas**: (a) extraer un `preflight.sh` que centralice invocacion — descartado por capa innecesaria.

### D8 — Reparto de specs: cableado en `cost-readiness`, JWT en `local-bootstrap`

El requisito de cableado automatico (arranque, Make, CI) se agrega como `ADDED` en `cost-readiness`; la incorporacion de `JWT_SECRET_KEY` se hace como `MODIFIED` del requisito "Preflight de entorno con fallo ruidoso" de `local-bootstrap` (reemplazo completo del bloque, con el header identico).

- **Razon**: el cableado es la culminacion del proposito de `cost-readiness` ("demostrar que las guardas estan cableadas antes de habilitar servicios pagos"). El conjunto de variables secretas requeridas pertenece a `local-bootstrap`, que ya gobierna el preflight de arranque. `MODIFIED` es correcto para el JWT porque cambia el comportamiento del requisito existente (no se agrega una preocupacion nueva); se copia el bloque entero para evitar perdida de detalle al archivar.
- **Alternativas consideradas**: (a) todo en `local-bootstrap` — descartado porque el cableado a CI/Make no es arranque local; (b) `ADDED` para JWT — descartado porque duplicaria la semantica del preflight de entorno en dos requisitos; (c) delta de `ci-pipeline` — descartado porque sus requisitos no cambian (los pasos nuevos son aditivos y el contrato del job se mantiene).

### D9 — Bypass explicito y audible `UP_SKIP_COST_PREFLIGHT=1` (resuelve la Open Question del gate)

El gate de costo acepta una unica via de omision: la variable de entorno `UP_SKIP_COST_PREFLIGHT=1`. Cuando esta definida con el valor `1`, `check_cost_preflight` (bash) e `Invoke-CostPreflight` (PowerShell) imprimen una advertencia explicita que nombra la variable y advierte que las guardas de costo no fueron verificadas, devuelven exito y no ejecutan el checker. Cualquier otro valor deja el gate activo. La excepcion queda reflejada en la delta spec `cost-readiness` (requisito y escenarios de bypass) y en `tasks.md`.

- **Razon**: la Open Question #2 preguntaba si debia existir un opt-out para depuracion. La decision humana fue incluirlo con la condicion de que sea audible y nunca silencioso. El bypass resuelve el caso de un operador que necesita levantar el stack con una guarda conocida y transitoriamente rota, sin debilitar el camino por defecto (la omision requiere una accion explicita del operador y deja rastro en la salida).
- **Alternativas consideradas**: (a) no agregar bypass — descartado por decision humana explicita; (b) bypass silencioso — descartado porque ocultaria que las guardas no se verificaron; (c) aceptar cualquier valor no vacio como bypass — descartado porque amplia la superficie de omision accidental; se exige el valor `1`.
- **Riesgo residual**: el bypass es una excepcion al MUST de bloqueo; su existencia se documenta en la spec para que el archivado no introduzca un contrato mas estricto que el codigo.

## Risks / Trade-offs

- **[PyYAML pasa a ser dependencia del arranque]** Un operador sin PyYAML no podra arrancar. -> Mitigacion: mensaje accionable que apunta a `scripts/preflight/requirements.txt`; el preflight ya falla ruidosamente (nunca falso PASS) y la spec exige el mensaje.
- **[Gate bloquea un arranque legitimo por una guarda que el operador quiere ignorar temporalmente]** Existe un opt-out, pero es explicitamente opt-in. -> Mitigacion: `UP_SKIP_COST_PREFLIGHT=1` es la unica via de omision, es audible (nombra la variable y advierte que las guardas no se verificaron), solo se activa con el valor `1` y no altera el camino por defecto (ver D9). Seam de test `UP_COST_PREFLIGHT` existe por separado y no es un bypass de operador.
- **[Paridad Windows verificada solo estructuralmente]** `up.ps1` no se ejecuta en CI ni en tests. -> Mitigacion: test estructural bash que exige la clave y la invocacion; documentar que el comportamiento runtime de PowerShell no esta cubierto automaticamente.
- **[El preflight es estatico]** Verifica estructura, no comportamiento runtime (limitacion heredada de c-36). -> Mitigacion: su salida es explicita sobre que verifica; el arnes de c-31 cubre comportamiento end-to-end.
- **[CI acopla el preflight al job de backend]** Un fallo de guardas marca `backend-tests` como rojo. -> Mitigacion: es el comportamiento deseado (bloquear el merge); el mensaje del paso identifica el preflight.
- **[Doble corrida del preflight]** Si en el futuro `make up` dependiera de `preflight`, se ejecutaria dos veces. -> Mitigacion: se documenta que los scripts son duenos del gate y el Makefile solo expone el objetivo manual.

## Migration Plan

1. Escribir los deltas de specs y validar con `openspec validate --strict` (fase propose).
2. RED: extender `scripts/tests/test_up_preflight.sh` con los casos de JWT y del gate del preflight (stub via `UP_COST_PREFLIGHT`); falla porque `up.sh` aun no los implementa.
3. GREEN: agregar `JWT_SECRET_KEY` y `check_cost_preflight` a `up.sh`; engancharlo en `main()` antes de `ensure_certificates`; refactor y triangular.
4. RED/GREEN: test estructural de paridad y edicion equivalente en `up.ps1`.
5. Agregar el objetivo `preflight` al `Makefile` y los pasos del preflight a `.github/workflows/ci.yml`.
6. Verificar: `bash scripts/tests/test_up_preflight.sh`, `python -m pytest scripts/preflight/test_cost_readiness.py -q`, `python scripts/preflight/cost_readiness.py` (exit 0), `openspec validate c-41-cost-preflight-wiring --strict`.

**Rollback**: revertir el commit revierte los scripts, el Makefile y CI; el preflight y su suite son aditivos y no cambian el runtime del stack. Quitar el gate de `up.sh`/`up.ps1` deja el arranque como antes (sin verificacion de costo), que es exactamente el estado a evitar, por lo que el rollback del gate debe ser una decision consciente.

## Open Questions

- **Resuelta — Paridad Windows**: `scripts/up.ps1` entra en este change (implementado en la seccion 4 de `tasks.md`), por la exigencia de equivalencia multiplataforma de `local-bootstrap`.
- **Resuelta — Bypass del gate**: se incluye un opt-out explicito y audible `UP_SKIP_COST_PREFLIGHT=1`, con las condiciones de D9 (audible, solo valor `1`, documentado en la delta spec).
- Si conviene, mas adelante, mover el preflight de CI a un job propio cuando el proyecto crezca (hoy no se justifica).
