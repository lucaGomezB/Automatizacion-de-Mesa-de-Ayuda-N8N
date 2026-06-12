## Context

El repositorio tiene dos suites de prueba listas para CI pero nada que las orqueste automáticamente:

- **Backend** (`Gestion_Incidentes/`): FastAPI, pytest 8.3 con `asyncio_mode = auto` (`pytest.ini`), 187 passed / 1 skipped / 1 xfailed, cobertura 89% en `app.routes`/`app.services`/`app.repositories` (medida en dev local con Python 3.13). `pytest-cov==5.0.0` ya está en `requirements.txt` (añadido en C-06). El comando canónico de cobertura quedó establecido en el design de C-06: `pytest --cov=app.routes --cov=app.services --cov=app.repositories --cov-report=term-missing`, ejecutado desde `Gestion_Incidentes/`. La suite corre 100% offline (Gemini/Twilio/Outlook/N8N mockeados, SQLite in-memory vía `aiosqlite`).
- **Frontend** (`Frontend/`): React 18 + TS 5.5 + Vite 5.4, Vitest 2.1.9 con proveedor de cobertura `v8`, 68 tests, cobertura 98.6% en alcance, `tsc --noEmit` limpio. `package.json` ya expone `test` (`vitest run --passWithNoTests`) y `test:coverage` (`vitest run --coverage`), ambos de C-07.
- **Módulo de evaluación** (`evaluation/`): proyecto pytest separado, con su propio `pytest.ini` y `requirements.txt` (scikit-learn, pandas, etc.). Sus tests usan un `corpus_fixture.csv` versionado y un `FakeClassifier` — **no** dependen del corpus real (`data/corpus_evaluacion_pseudonimizado.csv`, no trackeado).

Estado a cubrir: **no existe el directorio `.github/`**, no hay ESLint configurado en el frontend (proyecto Vite sin `eslint.config.*` ni script `lint`), y no hay ruff ni `pyproject.toml`/`ruff.toml` en `Gestion_Incidentes/` ni en la raíz. Governance del change: **BAJO**. Restricción dura: el CI no puede requerir ningún secreto.

El §6.5 de la tesis ya afirma que el CI corre en cada PR con GitHub Actions antes del merge a `main`; C-09 materializa esa afirmación.

## Goals / Non-Goals

**Goals:**

- Un único workflow `.github/workflows/ci.yml` con dos jobs paralelos (`backend-tests`, `frontend-tests`) disparado en `push` a `main` y en `pull_request`.
- Ejecutar las suites existentes con cobertura, exactamente con los comandos ya canónicos de C-06 y C-07, sin reescribirlos.
- Introducir linting en ambas bases de código de forma **no bloqueante para el código preexistente**: ruff (backend) y ESLint (frontend), arrancando permisivos.
- Mantener el pipeline reproducible (acciones pinneadas, cachés de pip/npm) y simple (KISS: dos jobs, sin matriz).
- Garantizar que el pipeline corre sin secretos.
- Mostrar un badge de estado de CI en el `README.md`.

**Non-Goals:**

- **No** se implementa el workflow en esta fase (esto es propose; el YAML se escribe en apply).
- **No** se configura despliegue/CD real (deploy a un entorno): el "CD" del nombre del change se limita a la automatización de calidad pre-merge; no hay paso de deployment.
- **No** se sube cobertura a Codecov/Coveralls ni se publica un porcentaje numérico vía terceros (requeriría cuenta/secreto).
- **No** se corrige la deuda de estilo del código existente (ruff/ESLint arrancan permisivos; limpiar warnings es trabajo futuro fuera de C-09).
- **No** se fija un `--cov-fail-under` agresivo que pueda romper CI por la diferencia 3.12/3.13 (ver Decisión 5).
- **No** se modifica el comportamiento de las suites ni el código de aplicación.

## Decisions

### Decisión 1: Un workflow con dos jobs paralelos, sin matriz

`ci.yml` define `backend-tests` y `frontend-tests` como jobs independientes que corren en paralelo (default de Actions), sobre `ubuntu-latest`. No se usa estrategia de matriz: el roadmap fija una sola versión por stack (Python 3.12, Node 20), así que una matriz solo agregaría complejidad sin valor. Triggers: `on: { push: { branches: [main] }, pull_request: {} }`.

- *Alternativa descartada*: un único job que corre ambas suites secuencialmente → más lento y mezcla logs; los jobs separados dan feedback granular (qué stack falló) y corren en paralelo.

### Decisión 2: Reusar los comandos de prueba ya canónicos (no reinventar)

- Backend (desde `Gestion_Incidentes/`): `pip install -r requirements.txt` y luego `pytest --cov=app.routes --cov=app.services --cov=app.repositories --cov-report=term-missing` — el mismo comando del design de C-06. `pytest.ini` no tiene markers `slow`, así que no hay un "fast pass" que separar; se corre la suite completa.
- Frontend (desde `Frontend/`): `npm ci` y `npm run test:coverage` — el script ya existe de C-07 (`vitest run --coverage`, proveedor `v8`).

Esto mantiene una sola fuente de verdad para "cómo se corren las pruebas" y evita divergencia CI vs. local.

- *Alternativa descartada*: redefinir flags de cobertura solo en el YAML → duplicaría la definición y se desincronizaría con la doc de C-06.

### Decisión 3: `setup-python@v5` + `setup-node@v4` con caché, acciones pinneadas a versión mayor

Se pinnean `actions/checkout@v4`, `actions/setup-python@v5` (con `cache: pip`), `actions/setup-node@v4` (con `cache: npm` apuntando a `Frontend/package-lock.json`). Python 3.12 explícito en el setup; Node 20 explícito. Pin a versión mayor (`@v4`/`@v5`), no a SHA: equilibrio razonable entre reproducibilidad y mantenimiento para un proyecto de tesis (KISS); no a rama flotante.

- *Nota de implementación*: `npm ci` requiere `Frontend/package-lock.json`. Si el lockfile no estuviera versionado, apply debe generarlo y commitearlo (es un prerequisito de `npm ci` y del caché de npm). Verificar en apply.

### Decisión 4: Linters introducidos en modo permisivo

- **Backend — ruff**: se instala con versión fija dentro del job de CI (`pip install ruff==<pin>`), **no** se agrega a `requirements.txt` para no contaminar las dependencias de runtime/test del módulo. Se versiona `Gestion_Incidentes/ruff.toml` con una configuración mínima y conservadora (regla por defecto `E`/`F` o un subconjunto seguro; `target-version = py312`). El paso corre `ruff check .` desde `Gestion_Incidentes/`. Si el código existente arrastra violaciones, apply debe arrancar con un set de reglas que el código ya cumple (medir primero) o acotar reglas, de modo que el step pase desde el día uno — el objetivo de C-09 es **instalar el guardarraíl**, no saldar deuda de estilo.
- **Frontend — ESLint**: el proyecto Vite no trae ESLint. Se agrega como `devDependency` con flat config (`Frontend/eslint.config.js`) para TS + React (typescript-eslint + plugins de react/react-hooks), un script `lint` en `package.json`, y el job lo corre con `npm run lint`. Igual criterio permisivo: la config debe pasar sobre el código actual (ajustar reglas a `warn` o desactivar las que el código viole masivamente, midiendo primero en apply).

- *Alternativa descartada (ruff en requirements)*: agregar ruff a `requirements.txt` → mezcla herramienta de lint con dependencias del paquete; el pin en el workflow lo aísla.
- *Alternativa descartada (lint bloqueante estricto desde el inicio)*: arrancar con el ruleset completo y `--exit-non-zero-on-fix` → bloquearía el primer PR del propio C-09 por deuda preexistente, contradiciendo el GATE. Se elige permisivo y se deja el endurecimiento como trabajo futuro.

### Decisión 5: Umbral de cobertura — medir en 3.12 antes de fijar `--cov-fail-under`

El 89% del backend se midió en Python 3.13 dev local; coverage.py 7.x reporta más bajo en 3.13 por un artefacto con líneas post-`await` (documentado en C-06: `clasificacion_repository.py` figura 65% por el artefacto aunque los tests la ejerciten). En CI corre Python 3.12, donde el número puede diferir. Por eso:

- C-09 **no fija** un `--cov-fail-under` agresivo en el YAML. El gate de cobertura del proyecto se mantiene como en C-06 (no se fija globalmente en `pytest.ini`).
- Si en apply se decide poner un piso, se mide primero el porcentaje real en 3.12 vía la corrida real de CI en el PR, y se fija con holgura (p. ej. un valor varios puntos por debajo del medido), nunca por encima de lo que CI mide.

- *Alternativa descartada*: fijar `--cov-fail-under=85` a ciegas → riesgo de romper CI por la diferencia de versión y el artefacto post-`await`.

### Decisión 6: Alcance del job de backend — suite de `Gestion_Incidentes/`, no `evaluation/`

El job `backend-tests` corre la suite de `Gestion_Incidentes/tests/` (la que mide cobertura de la app). La suite de `evaluation/` es un proyecto pytest separado con dependencias propias (scikit-learn, pandas) y su propio `pytest.ini`; **no** mide cobertura de `app.*` y es autocontenida (usa `corpus_fixture.csv` + `FakeClassifier`). Para C-09 se mantiene fuera del job de backend por defecto, para no inflar tiempos/instalaciones; queda como posible job adicional futuro. Esta decisión se marca explícita por si el usuario prefiere incluirla (es barato sumarla como step o job extra, pero no es requisito del scope de C-09).

- *Nota*: si se incluyera, correría perfectamente sin el corpus real porque usa el fixture versionado.

### Decisión 7: Badge de estado de CI (nativo de GitHub), no badge de porcentaje de cobertura

Se agrega al `README.md` el badge de estado del workflow vía la URL nativa de GitHub Actions:
`https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N/actions/workflows/ci.yml/badge.svg`. No requiere cuenta ni token de terceros, respetando la restricción de "sin secretos". El README hoy no tiene ningún badge; se ubica cerca del título.

- *Alternativa descartada (Codecov/Coveralls)*: dan un badge de porcentaje real, pero requieren cuenta externa y, para repos privados, un token (secreto) — choca con la restricción dura. Un badge de cobertura "estático" hardcodeado se descarta por engañoso (se desactualiza). Para la tesis basta con evidenciar que el CI corre y pasa.

## Risks / Trade-offs

- **[Falta `Frontend/package-lock.json` → `npm ci` y `cache: npm` fallan]** → En apply, verificar que el lockfile esté versionado; si no, generarlo (`npm install`) y commitearlo antes de habilitar `npm ci`.
- **[ruff/ESLint marcan deuda preexistente y rompen el primer CI]** → Arrancar permisivos: medir las violaciones reales en apply y calibrar la config (subconjunto de reglas / `warn`) para que el step pase sobre el código actual. El endurecimiento es trabajo futuro, no de C-09.
- **[Cobertura difiere entre 3.13 local y 3.12 CI]** → No fijar `--cov-fail-under` a ciegas; medir en la corrida real de CI y, si se fija piso, hacerlo con holgura (Decisión 5).
- **[Un secreto se cuela en el YAML]** → El spec lo prohíbe explícitamente y hay un escenario de verificación (inspección del YAML sin `secrets.*`); además los PRs desde forks no tienen secretos, lo que actúa como prueba natural.
- **[YAML es config, no código testeable unitariamente]** → La verificación se hace por (a) validación de sintaxis del workflow (actionlint si está disponible, o validación local), (b) ejecución local de los comandos exactos que el workflow corre, y (c) la corrida real de CI en el PR como verificación final. Si apply escribiera algún helper script, ese sí seguiría TDD estricto.

## Migration Plan

1. Crear `.github/workflows/ci.yml` con los dos jobs (Decisiones 1–3).
2. Agregar config de ruff (`Gestion_Incidentes/ruff.toml`) calibrada permisiva y el step de lint del backend (Decisión 4).
3. Agregar ESLint al frontend (devDependency + `eslint.config.js` + script `lint`) calibrado permisivo y el step de lint del frontend (Decisión 4).
4. Verificar/commitear `Frontend/package-lock.json` si falta.
5. Agregar el badge de estado de CI al `README.md` (Decisión 7).
6. Verificación local: correr los comandos exactos del workflow (pytest con cobertura desde `Gestion_Incidentes/`, `npm ci` + `npm run test:coverage` + `npm run lint` desde `Frontend/`, `ruff check .` desde `Gestion_Incidentes/`).
7. Verificación final: abrir el PR y confirmar que ambos jobs pasan en GitHub Actions; recién ahí, si se desea, medir la cobertura real en 3.12 para decidir un piso.

Rollback: como es aditivo (solo agrega `.github/`, configs de lint y un badge), revertir es borrar esos archivos; no afecta runtime ni las suites.

## Open Questions

- ¿Se desea incluir la suite de `evaluation/` como job/step adicional del CI? Por defecto C-09 la deja fuera (Decisión 6); sumarla es barato y no requiere el corpus real. Decisión diferible a apply o a criterio del usuario.
