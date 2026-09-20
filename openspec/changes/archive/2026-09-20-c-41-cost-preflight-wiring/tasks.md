## 1. Red de seguridad previa (Strict TDD)

- [x] 1.1 Ejecutar `bash scripts/tests/test_up_preflight.sh` y `python -m pytest scripts/preflight/test_cost_readiness.py -q` antes de tocar archivos; registrar la linea base ("N assertions, 0 failure(s)" y "M passed") y confirmar que no hay fallos preexistentes. Si hay fallos, detenerse y reportarlos (no se arreglan en este change).

## 2. `JWT_SECRET_KEY` en el preflight de entorno de `scripts/up.sh`

- [x] 2.1 RED: extender `scripts/tests/test_up_preflight.sh` con fixtures de `.env` para `JWT_SECRET_KEY` ausente, vacia y con placeholder (`your-jwt-secret-key-here`), y actualizar los fixtures validos para incluir la clave; cada caso debe asertar exit no-cero, que el output nombre `JWT_SECRET_KEY` y que nunca imprima el valor secreto. Ejecutar el harness y confirmar que los casos nuevos fallan.
- [x] 2.2 GREEN: en `scripts/up.sh` agregar `JWT_SECRET_KEY` a `REQUIRED_SECRETS` y `your-jwt-secret-key-here` a `PLACEHOLDER_VALUES`; ejecutar el harness y confirmar que todos los casos pasan.
- [x] 2.3 TRIANGULATE: agregar un caso con un placeholder de JWT definido en una plantilla custom (deteccion por plantilla) y un caso con valor entrecomillado valido; ejecutar el harness y confirmar deteccion/pass segun corresponda, sin imprimir el valor.

## 3. Gate del preflight de costo en `scripts/up.sh`

- [x] 3.1 RED: en `scripts/tests/test_up_preflight.sh` agregar un stub de preflight (via `UP_COST_PREFLIGHT`) que sale 1 con un resumen con `FAIL`; ejecutar `up.sh` como subproceso con un `.env` valido y asertar exit no-cero, que el output nombre la guarda en FAIL, y que NO se llega a `start_stack` (colocar un `docker` falso en `PATH` que escriba un centinela y asertar su ausencia). Agregar el caso verde llamando `check_cost_preflight` por `source` con un stub que sale 0 y asertar retorno 0. Ejecutar y confirmar que falla antes de implementar.
- [x] 3.2 GREEN: en `scripts/up.sh` agregar `COST_PREFLIGHT_SCRIPT` con override `UP_COST_PREFLIGHT`, deteccion perezosa de interprete (`UP_PYTHON` -> `python3` -> `python`) y la funcion `check_cost_preflight` (imprime la salida del CLI, emite error accionable y devuelve no-cero si falla o si falta el interprete); engancharla en `main()` entre `check_env_file` y `ensure_certificates`. Ejecutar el harness y confirmar que todos los casos pasan.
- [x] 3.3 TRIANGULATE: agregar casos para (a) stub de preflight inexistente -> exit no-cero con mensaje accionable; (b) interprete invalido via `UP_PYTHON=/nonexistent/python` -> exit no-cero con mensaje accionable; (c) stub que sale 0 e imprime resumen -> el arranque continua hasta el punto siguiente sin abortar por el gate. Ejecutar el harness.
- [x] 3.4 REFACTOR: revisar que `check_cost_preflight` y la deteccion de interprete no dupliquen logica y sigan el estilo de las funciones existentes; re-ejecutar el harness y confirmar que sigue verde.
- [x] 3.5 Bypass explicito y audible (decision D9): en `check_cost_preflight` de `scripts/up.sh` aceptar `UP_SKIP_COST_PREFLIGHT=1` como unica via de omision, imprimiendo una advertencia que nombra la variable y advierte que las guardas no se verificaron, sin ejecutar el checker y devolviendo exito; cualquier otro valor deja el gate activo. RED/GREEN/TRIANGULATE en `scripts/tests/test_up_preflight.sh`: retorno 0 con bypass, advertencia nombra la variable, el preflight no se ejecuta, y un valor distinto de `1` NO omite el gate. Reflejar la excepcion en la delta spec `cost-readiness` (requisito + escenarios de bypass) y en D9 de `design.md`. Ejecutar el harness y confirmar verde.

## 4. Paridad Windows en `scripts/up.ps1` (contingente a la confirmacion del alcance)

- [x] 4.1 RED: en `scripts/tests/test_up_preflight.sh` agregar aserciones estructurales de `scripts/up.ps1`: declara `JWT_SECRET_KEY` en `$RequiredSecrets` e invoca el preflight de costo antes de la generacion de certificados. Ejecutar y confirmar que falla.
- [x] 4.2 GREEN: en `scripts/up.ps1` agregar `JWT_SECRET_KEY` a `$RequiredSecrets`, `your-jwt-secret-key-here` a `$PlaceholderValues`, y `Invoke-CostPreflight` (con overrides `UP_COST_PREFLIGHT`/`UP_PYTHON`) invocado antes de `Invoke-EnsureCertificates`; ejecutar el test estructural y confirmar que pasa.
- [x] 4.3 Documentar en la tarea de verificacion que el runtime de PowerShell no tiene harness automatico (sin `pwsh`) y que la cobertura es estructural; no se instala `pwsh`.
  - Nota: `pwsh` no esta disponible en este entorno; no se instala. La paridad Windows de `scripts/up.ps1` (JWT en `$RequiredSecrets`, placeholder, `Invoke-CostPreflight` y su orden antes de `Invoke-EnsureCertificates`) se verifica con aserciones estructurales en `scripts/tests/test_up_preflight.sh`. El comportamiento runtime de PowerShell NO esta cubierto automaticamente.

## 5. Objetivo `preflight` del Makefile

- [x] 5.1 Agregar el objetivo `preflight` a `Makefile` que invoque `$(PYTHON) scripts/preflight/cost_readiness.py`, sumarlo a `.PHONY` y verificar que `make preflight` termina con exit 0 sobre el repo actual.

## 6. Preflight en CI

- [x] 6.1 Agregar al job `backend-tests` de `.github/workflows/ci.yml` los pasos: instalar `scripts/preflight/requirements.txt`, ejecutar `python -m pytest scripts/preflight/test_cost_readiness.py -q` y ejecutar `python scripts/preflight/cost_readiness.py`, todos desde la raiz del repo. Verificar que el YAML sigue siendo parseable (`python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"`) y que los tres comandos corren localmente con exit 0.

## 7. Verificacion final

- [x] 7.1 Ejecutar la verificacion integral: `bash scripts/tests/test_up_preflight.sh`, `python -m pytest scripts/preflight/test_cost_readiness.py -q`, `python scripts/preflight/cost_readiness.py` (exit 0), `make preflight` (exit 0) y `openspec validate --strict --change c-41-cost-preflight-wiring`; confirmar todo verde.
- [x] 7.2 Confirmar el modo de fallo no destructivo: con un stub de preflight que falla, verificar que `git status` no muestra archivos modificados ni certificados generados y que el output no contiene `Starting stack`.
