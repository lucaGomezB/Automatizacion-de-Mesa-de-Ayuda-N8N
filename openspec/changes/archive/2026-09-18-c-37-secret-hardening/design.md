## Context

Ver `proposal.md — Why` para la motivacion. Estado actual y restricciones que moldean el enfoque:

- **Repositorio publico** en `lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N`. El arbol actual esta limpio de secretos; el riesgo es historico y de configuracion, no de codigo en HEAD.
- **Hecho verificado**: el commit `597c03e` (en `origin/main`) ya parametrizo los defaults de desarrollo. `POSTGRES_PASSWORD` paso de `mesa` a `mesa_local_dev`; la password de basic auth de N8N paso de `admin` a `n8n_local_dev`; ambos compose usan `${VAR:-default}` sobreescribible por el `.env` gitignorado de la raiz; `scripts/create_db.sql` exige `psql -v db_password=...`; CI usa `mesa_ci_local`; `conftest.py` y `test_disposable_test_db.py` quedaron alineados. Este change NO reimplementa esa rotacion: la formaliza.
- **Hecho verificado**: `2784b1b` destrackeo `.claude/settings.local.json` y `App/Backend/.claude/settings.local.json` (`git rm --cached`), que siguen presentes localmente y ahora estan cubiertos por `.gitignore` (`.claude/`).
- **Hecho verificado (GitHub)**: `secret_scanning` y `secret_scanning_push_protection` estan habilitados. `secret_scanning_non_provider_patterns` y `secret_scanning_validity_checks` NO estan disponibles en este repo: la API REST los ignora en silencio y la UI no muestra los toggles (requieren GitHub Secret Protection, plan pago). Verificado el 2026-09-18 con y sin el header `X-GitHub-Api-Version: 2026-03-10` y por inspeccion del operador en la UI.
- **Hecho verificado (alertas)**: existe exactamente 1 alerta abierta: numero `1`, `secret_type: google_api_key`, `state: open`, `resolution: null`. Es la clave historica YA revocada (`Gestion_Incidentes/.env`, blob `be1ab368`, commits `0d430b5`/`eee5c84`, removida en `02e845c`). Debe resolverse con `resolution: revoked`.
- **Hook pre-commit existente** en `.githooks/pre-commit`: bloquea `.env` staged y asignaciones genericas de key/secret/token/password con valores de 20+ caracteres, admite el marcador `gitleaks:allow`, y corre gitleaks como capa opcional si esta instalado. Requiere `git config core.hooksPath .githooks`.
- **Spec principal editada directamente**: `openspec/specs/local-bootstrap/spec.md` fue modificada en `597c03e` (commit que no es un apply OPSX) para quitar la mencion a la credencial hardcodeada `admin/admin`. Esa edicion carece de proveniencia OPSX y debe formalizarse sin duplicar ni contradecir el texto ya presente.
- **Gobernanza**: seguridad es CRITICAL. Este change PROPONE; el apply MUST obtener checkpoint humano antes de ejecutar acciones con efecto externo (resolver la alerta, cambiar la configuracion del repositorio en GitHub).

## Goals / Non-Goals

**Goals:**

- Codificar en specs la postura de seguridad ya vigente y la que falta cerrar: hook local, escaneo de GitHub, triaje de alertas y runbook de rotacion.
- Dar proveniencia OPSX a la parametrizacion de credenciales locales y a la edicion directa de `local-bootstrap`, sin reescribir el texto ya editado.
- Proveer una automatizacion idempotente y sin secretos que habilite lo configurable por API e imprima lo que no esta disponible en el plan actual.
- Dejar la alerta historica de Gemini triada y resuelta con una resolucion veraz (`revoked`).
- Que el estado final sea auditable: un operador puede verificar con comandos que la postura se mantiene.

**Non-Goals:**

- No se reescribe el historial de git (la clave ya fue revocada; remover el historial es innecesario).
- No se reimplementa la rotacion de `597c03e`.
- No se agrega gitleaks a CI ni se cambia el pipeline: el escaneo server-side de GitHub + el hook local cubren el caso.
- No se modifica `.githooks/pre-commit` (ya cumple; solo se caracteriza y se documenta su instalacion).
- No se crea una spec para el contenido documental del runbook mas alla del requisito verificable de su cobertura.
- No se automatiza ni se intenta habilitar `secret_scanning_non_provider_patterns` ni `secret_scanning_validity_checks`: no estan disponibles en el plan gratuito (requieren GitHub Secret Protection) y la API REST los ignora.

## Decisions

### D1 — Nueva capacidad `secret-hygiene` y delta `ADDED` a `local-bootstrap`

La deteccion/escaneo/triaje/rotacion de secretos se agrupa en una capacidad nueva `secret-hygiene`. La parametrizacion de credenciales de desarrollo local se agrega como requisito nuevo (`## ADDED Requirements`) de la capacidad existente `local-bootstrap`.

- **Razon**: `secret-hygiene` es una preocupacion de seguridad transversal al repositorio (hook, GitHub, alertas, runbook) que no pertenece a ninguna spec existente. `docker-security-hardening` cubre contenedores; `foundation-environment` cubre configuracion base, prompt, migraciones, engram y Docker; `local-bootstrap` cubre el arranque local. Colocar el escaneo de GitHub en cualquiera de ellas seria sorprendente para un lector. En cambio, las credenciales de desarrollo local SI pertenecen a `local-bootstrap`, porque es la capacidad que ya gobierna el preflight de secretos y la salida de acceso "sin hardcodear valores en el repo".
- **Alternativas consideradas**: (a) meter todo en `local-bootstrap` — descartado porque el escaneo del lado de GitHub no tiene relacion con el arranque local; (b) meter todo en `docker-security-hardening` — descartado porque no es una preocupacion de contenedores; (c) `skip_specs: true` — descartado porque hay comportamiento verificable nuevo (el contrato del script y la resolucion de alertas).

### D2 — Delta de `local-bootstrap` como `ADDED`, sin `## Purpose`, sin tocar el texto ya editado

El delta `specs/local-bootstrap/spec.md` usa `## ADDED Requirements` con un unico requisito nuevo ("Credenciales de desarrollo local parametrizadas por entorno"). No incluye `## Purpose` (la spec existente ya lo tiene) y no re-declara ni modifica el requisito "Verificacion de salud y salida de acceso" que ya fue editado directamente.

- **Razon**: el texto de `local-bootstrap` ya fue editado en `597c03e` para quitar `admin/admin`. Usar `## MODIFIED Requirements` sobre ese bloque obligaria a copiar su contenido completo y arriesgaria una divergencia con lo ya presente en la spec principal (el workflow de MODIFIED exige que el header coincida y el contenido completo se reemplace al archivar). Un requisito `ADDED` independiente da proveniencia OPSX a la intencion sin tocar el texto existente ni duplicarlo. El requisito nuevo es mas amplio que la mencion puntual eliminada: cubre compose, scripts, CI y tests.
- **Alternativas consideradas**: (a) `MODIFIED` del requisito de salida de acceso — descartado por el riesgo de divergencia y porque el texto ya refleja el comportamiento deseado; (b) `skip_specs` para `local-bootstrap` — descartado porque la parametrizacion es comportamiento verificable (sustitucion por entorno, defaults no adivinables) y el pedido exige proveniencia OPSX.

### D3 — Script `scripts/security/configure_github_secret_scanning.sh`: API-settable via `gh api`, UI-only impreso, idempotente

El script resuelve el repositorio (default `gh repo view`, override `--repo owner/name`), lee el estado actual, habilita por `gh api` las dos protecciones configurables por API (`security_and_analysis.secret_scanning.status` y `security_and_analysis.secret_scanning_push_protection.status` via `PATCH /repos/{owner}/{repo}`), y SIEMPRE imprime los pasos manuales para `secret_scanning_non_provider_patterns` y `secret_scanning_validity_checks`, aclarando que la API REST los ignora en silencio. La idempotencia se logra consultando el estado antes de escribir: si ya esta `enabled`, no reescribe y lo reporta. Soporta `--dry-run` (imprime las llamadas y los pasos sin ejecutarlos) y `--resolve-alert N --resolution X --confirm` (opt-in). Permite override del binario con `GH_BIN` (default `gh`) para poder testearlo sin red. Sin secretos embebidos; no ejecuta comandos de reescritura de historial.

- **Razon**: `gh api` es el mecanismo soportado para las claves API-settable; imprimir lo solo-UI evita que el operador asuma cobertura total. `--dry-run` + `GH_BIN` hacen el script testeable sin tocar GitHub, requisito para TDD con un stub de `gh`. La resolucion de alertas es opt-in porque es una accion externa con gobernanza CRITICAL.
- **Alternativas consideradas**: (a) `curl` con `GITHUB_TOKEN` — descartado porque `gh` ya esta asumido en el flujo del proyecto y maneja autenticacion/permisos con mejor mensaje de error; (b) intentar setear tambien las claves solo-UI — descartado porque la API las ignora en silencio y daria una falsa sensacion de exito; (c) resolver la alerta por defecto — descartado por gobernanza (accion externa irreversible-ish) y porque el pedido la marca como opcional.

### D4 — Semantica de resolucion de alertas: `revoked`, nunca descarte ciego

La alerta numero `1` (`google_api_key`) se resuelve con `{"state": "resolved", "resolution": "revoked"}` porque la clave ya fue revocada en Google. El runbook define el arbol de decision de `resolution` (`revoked`, `false_positive`, `used_in_tests`, `wont_fix`) y prohibe dejar `resolution` en nulo o descartar sin criterio.

- **Razon**: la alerta corresponde a un secreto ya revocado y removido del arbol (`02e845c`); `revoked` es la resolucion que refleja la realidad y evita que la alerta siga contando como riesgo abierto. Un descarte ciego ocultaria la causa raiz y degradaria la auditabilidad.
- **Alternativas consideradas**: (a) `wont_fix` — descartado porque no describe el hecho (la clave ya no es valida); (b) `false_positive` — descartado porque el secreto fue real; (c) dejar la alerta abierta — descartado porque el pedido exige cerrar la brecha.

### D5 — Runbook `docs/security-hardening.md` con la filtracion de Gemini como caso de estudio

El runbook cubre: API-settable vs no disponibles (plan pago), proteccion de push, triaje/resolucion de alertas (`state`/`resolution`), instalacion del hook (`git config core.hooksPath .githooks`), y el procedimiento de rotacion: revocar primero en el proveedor, rotar el valor en el `.env` gitignorado, verificar que el arbol queda limpio, y NO reescribir el historial una vez revocada la credencial. La filtracion historica de Gemini se documenta como caso de estudio con sus commits (`0d430b5`/`eee5c84`, removida en `02e845c`) y la resolucion de la alerta.

- **Razon**: el pedido exige un runbook operativo y un caso de estudio real. Documentar el caso de Gemini convierte el procedimiento abstracto en algo verificable contra el historial real y deja registro de por que no se reescribe el historial.
- **Alternativas consideradas**: (a) runbook generico sin caso de estudio — descartado por pedido explicito; (b) documentar la reescritura de historial como opcion — descartado porque contradice la postura (innecesaria tras revocar) y es una operacion destructiva.

### D6 — El hook pre-commit se caracteriza, no se modifica

La spec `secret-hygiene` describe el contrato del hook existente (`.env` staged, patrones, `gitleaks:allow`, activacion por `core.hooksPath`) sin cambiar su implementacion. La capa opcional de gitleaks se mantiene opcional.

- **Razon**: el hook ya cumple el objetivo y esta probado por uso; reescribirlo agrega riesgo sin valor. Caracterizarlo en una spec lo vuelve verificable y auditable, y documentar su activacion cierra el unico gap real (un clon nuevo no lo tiene activo hasta correr `git config`).
- **Alternativas consideradas**: (a) portar el hook a `pre-commit` framework — descartado por dependencia nueva y porque el hook actual no lo necesita; (b) reimplementar el hook — descartado por riesgo innecesario.

### D7 — Gobernanza CRITICAL: el script por defecto solo lee e imprime; las escrituras externas son opt-in con confirmacion

Por defecto el script habilita las protecciones API-settable (idempotente, no destructivo) y lista las alertas. La resolucion de una alerta y cualquier cambio de configuracion externa requiere confirmacion explicita del operador (`--confirm`) y checkpoint humano registrado en el apply. El script no reescribe historial ni toca ramas.

- **Razon**: la seguridad es CRITICAL en el modelo de gobernanza. Habilitar protecciones es de bajo riesgo y revierte facil; resolver una alerta cambia el estado de auditoria del repositorio y debe ser una decision humana consciente. Mantener el default en modo lectura/impresion permite que un operador inspeccione antes de actuar.
- **Alternativas consideradas**: (a) que el script resuelva la alerta automaticamente — descartado por gobernanza; (b) que el script exija confirmacion tambien para habilitar protecciones — descartado porque habilitar es seguro y el pedido pide automatizarlo.

### D8 — Sin gitleaks en CI

No se agrega una dependencia de gitleaks al pipeline de CI. La cobertura es el escaneo server-side de GitHub (secret scanning + push protection) mas el hook local; gitleaks queda como capa opcional del hook si esta instalado.

- **Razon**: agregar gitleaks a CI introduce una dependencia, un pin de version y un job nuevo para una capacidad que GitHub ya presta sobre un repo publico. El pedido explicita que no se agregue salvo justificacion, y no hay justificacion: el escaneo server-side cubre el historial y la proteccion de push cubre el push.
- **Alternativas consideradas**: (a) gitleaks en CI — descartado por dependencia innecesaria; (b) `pre-commit` framework — descartado por la misma razon.

### D9 — Las dos funciones de escaneo restantes quedan como NO disponibles (requieren plan pago)

`secret_scanning_non_provider_patterns` y `secret_scanning_validity_checks` no se habilitan: requieren **GitHub Secret Protection** (GitHub Team o Enterprise, plan pago). Verificado el 2026-09-18: la API REST las ignora con y sin el header `X-GitHub-Api-Version: 2026-03-10`, y el operador confirmo que los toggles no existen en la UI del repo (plan gratuito, user-owned publico). El script y el runbook las reportan como no disponibles en lugar de mandar a un toggle inexistente.

- **Razon**: no hay accion tecnica posible en el plan actual. Tratarlas como "solo-UI" seria enganoso: un operador buscaria un toggle que no existe. La tarea 5.1 se cierra como "no disponible" con evidencia, no como pendiente.
- **Alternativas consideradas**: (a) dejarlas como tarea pendiente — descartado porque nunca se podria completar en este plan y bloquearia el archive; (b) omitirlas del runbook — descartado porque el runbook debe explicar por que no estan y que haria falta para tenerlas.

## Risks / Trade-offs

- **[La API REST ignora en silencio las claves no disponibles]** Un script que intente setear `secret_scanning_non_provider_patterns`/`validity_checks` puede reportar exito falso. → Mitigacion: el script no las envia; las imprime como no disponibles y el runbook explica el motivo (plan pago). La spec las declara explicitamente como no disponibles por plan.
- **[El token de `gh` no tiene permisos de administracion]** El `PATCH` falla. → Mitigacion: el script falla ruidosamente con mensaje accionable (permisos requeridos) y codigo de salida no-cero, sin reportar exito parcial.
- **[El hook es evitable con `--no-verify`]** Un commit consciente puede saltear la deteccion local. → Mitigacion: la proteccion de push del lado de GitHub es el backstop server-side; el runbook lo explicita.
- **[Resolver la alerta es una accion externa]** Cambia el estado de auditoria del repositorio. → Mitigacion: gobernanza CRITICAL, opt-in con `--confirm`, checkpoint humano en el apply y resolucion veraz (`revoked`), reversible reabriendo la alerta si hiciera falta.
- **[Script bash-only]** No hay version `.ps1` para Windows, a diferencia de `scripts/up`/`scripts/backup`. → Mitigacion: el proyecto se mantiene en Linux/macOS; un operador Windows puede usar `gh` directamente siguiendo el runbook. Portar a `.ps1` es un follow-up si se necesita, sin cambio de spec.
- **[La parametrizacion ya aplicada no se re-verifica en CI]** El requisito `ADDED` de `local-bootstrap` no tiene un test automatico dedicado. → Mitigacion: las tareas incluyen una verificacion estructural por comandos (grep de sustitucion `${VAR:-default}` y ausencia de defaults adivinables); si se quiere un test permanente, es un follow-up de bajo costo.
- **[Duplicacion entre spec y runbook]** Parte del contenido (API vs UI, triaje) aparece en la spec y en el runbook. → Mitigacion: la spec fija el contrato verificable; el runbook es el procedimiento operativo con detalle y caso de estudio. Es una duplicacion deliberada de audiencias distintas (validador vs operador).

## Migration Plan

1. Crear el delta de specs (`secret-hygiene`, `local-bootstrap`) y validar con `openspec validate --strict` (fase propose).
2. Escribir `docs/security-hardening.md` (runbook) con el caso de estudio de Gemini.
3. RED: escribir los tests del script (`scripts/security/test_configure_github_secret_scanning.py`) con un stub de `gh` via `GH_BIN`; cubrir `--dry-run`, idempotencia, impresion de pasos solo-UI, fallo sin `gh`, y resolucion opt-in.
4. GREEN: implementar `scripts/security/configure_github_secret_scanning.sh` hasta pasar los tests; triangulate y refactor.
5. CHECKPOINT CRITICAL: confirmar con el operador la resolucion de la alerta #1 como `revoked` y la habilitacion de las funciones solo-UI. Luego ejecutar el script y los pasos manuales.
6. Verificar: `gh api` reporta `secret_scanning=enabled`, `push_protection=enabled`, cero alertas abiertas, alerta #1 `resolved`/`revoked`; `openspec validate c-37-secret-hardening --strict` PASS.

**Rollback**: el runbook y los tests son aditivos y se revierten con el commit. La habilitacion de protecciones se revierte poniendo `status: disabled`; la alerta #1 se revierte reabriendola. El delta de specs se revierte descartando el change antes de archivar. No hay operacion destructiva que requiera plan de recuperacion (no se reescribe historial).

## Open Questions

- Si conviene portar el script a PowerShell para paridad multiplataforma (follow-up, no cambia specs ni tareas).
- Si conviene agregar un test estructural permanente de la parametrizacion de credenciales en la suite del backend (follow-up de bajo costo; hoy se verifica por comandos en tareas).
- Valor de `ESTIMATED_COST...` no aplica aqui; sin preguntas abiertas que afecten el enfoque.
