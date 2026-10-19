## Leer antes (obligatorio)

- `docs/cumplimiento/plan-cambios-cumplimiento.md` (fila C-64; fase 21).
- `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` (brechas 8.7, 8.8, 8.28, 8.29).
- `docs/seguridad/modelado-amenazas-sdlc.md` §4 (amenaza "Dependencias sin control de CVE" -> C-64).
- `design.md` de este change (D1-D9 y preguntas abiertas).
- `openspec/specs/ci-pipeline/spec.md`, `openspec/specs/security-governance-docs/spec.md` (SGD-001, SGD-011).
- `docs/seguridad/README.md` (regla de lenguaje y mapa de trazabilidad a extender).

## 1. Preparacion y red de seguridad

- [x] 1.1 Activar el hook y confirmar el estado del change (`git config core.hooksPath .githooks`; `openspec status --change c-64-vulnerabilidades-supply-chain --json`). Verificacion: el status lista `proposal`, `specs` y `design` como `done`.
- [x] 1.2 Capturar el baseline de CI de estructura: parsear `.github/workflows/ci.yml` y registrar los jobs existentes (deben ser `backend-tests`, `frontend-tests`, `secret-scan`). Verificacion: baseline capturado; sin jobs de escaneo de seguridad hoy.
- [x] 1.3 Capturar el baseline de imagenes e dependencias: confirmar que `.github/dependabot.yml` NO existe y que `docker-compose.yml` referencia `nginx:alpine` y `ngrok/ngrok:latest` (`grep -n "image:" docker-compose.yml`). Verificacion: baseline capturado (una entrada flotante como minimo).
- [x] 1.4 Red de seguridad: `cd App/Backend; pytest -m "not integration" -q` y `cd App/Frontend; npm run test` deben quedar verdes ANTES de tocar nada (este change no toca codigo, pero fija el baseline). Verificacion: ambos verdes.

## 2. Dependabot (T)

- [x] 2.1 RED: escribir una verificacion estructural que falle porque `.github/dependabot.yml` no existe: parsear el YAML y exigir `version: 2` con entradas `pip`/`App/Backend`, `npm`/`App/Frontend` y `github-actions`/`/`. Verificacion: la verificacion falla por archivo ausente.
- [x] 2.2 GREEN: crear `.github/dependabot.yml` con `version: 2`, las tres entradas, `schedule.interval: weekly` y agrupacion (`groups`) por ecosistema (design D9). Verificacion: la verificacion de 2.1 pasa.
- [x] 2.3 TRIANGULATE: agregar casos que verifiquen (a) el directorio exacto de cada ecosistema; (b) que no hay tokens ni valores de credenciales; (c) que cada entrada tiene programacion recurrente y agrupacion; (d) que no hay auto-merge ni auto-approve. Verificacion: todos pasan.
- [x] 2.4 REFACTOR: ordenar entradas y comentarios del archivo; re-correr la verificacion. Verificacion: verde tras el refactor.

## 3. Fijado de imagenes Docker (T)

- [x] 3.1 RED: escribir una verificacion que falle hoy: extraer las lineas `image:` de `docker-compose.yml` y exigir que ninguna termine en `:latest` ni quede sin tag. Verificacion: falla por `nginx:alpine` y `ngrok/ngrok:latest`.
- [x] 3.2 GREEN: resolver el tag estable vigente de cada imagen contra el registro y fijarlo en `docker-compose.yml` (design D5). Verificacion: la verificacion de 3.1 pasa.
- [x] 3.3 TRIANGULATE: validar el stack con `docker compose config` (no debe fallar) y confirmar por grep que no quedan referencias `:latest`. Verificacion: `docker compose config` sin errores y grep sin `:latest` en lineas `image:`.
- [x] 3.4 Verificar que las imagenes ya fijadas (`postgres:15.5-alpine`, `n8nio/n8n:2.11.2`) no se tocan. Verificacion: `git diff docker-compose.yml` solo muestra `nginx` y `ngrok`.

## 4. Pinning de dependencias Python y JavaScript (T)

- [x] 4.1 RED: escribir una verificacion que falle hoy: detectar en `App/Backend/requirements.txt` las dependencias con `>=` sin cota superior y exigir que cada una tenga cota o una justificacion registrada. Verificacion: falla por `google-genai`, `cryptography`, `python-jose` y `bcrypt` sin cota.
- [x] 4.2 GREEN: acotar las fronteras de mayor seguras (`google-genai>=2.20.0,<3`, `bcrypt>=4.0.0,<5`, `python-jose[cryptography]>=3.3.0,<4`) y dejar `cryptography>=43.0.0` documentada como excepcion (design D6). Verificacion: la verificacion de 4.1 pasa con la excepcion justificada.
- [x] 4.3 TRIANGULATE: confirmar que el arbol resuelve sin conflicto con `cd App/Backend; pip install --dry-run -r requirements.txt` y que las dependencias ya fijadas no cambian. Verificacion: `--dry-run` resuelve sin error y el diff solo toca las cuatro lineas previstas.
- [x] 4.4 Documentar la decision de pinning del frontend (mantener `^` + `package-lock.json` versionado + `npm ci`). Verificacion: `git ls-files App/Frontend/package-lock.json` lista el archivo; `grep -n "npm ci" .github/workflows/ci.yml` lo encuentra.
- [x] 4.5 REFACTOR: agrupar/ordenar los comentarios de `requirements.txt` que explican las cotas; re-correr 4.1 y 4.3. Verificacion: verdes tras el refactor.

## 5. Job de escaneo de seguridad en CI (T)

- [x] 5.1 RED: escribir una verificacion estructural que falle hoy: parsear `.github/workflows/ci.yml` y exigir un job `security-scan` con los tres escaneos (auditoria de dependencias backend, SAST backend, auditoria de dependencias frontend). Verificacion: falla por job ausente.
- [x] 5.2 GREEN: agregar el job `security-scan` en paralelo a los existentes, sobre Python 3.12 y Node 20, con herramientas fijadas e instaladas en su propio entorno (design D1). Verificacion: la verificacion de 5.1 pasa.
- [x] 5.3 TRIANGULATE: verificar (a) el job declara su politica de bloqueo (SAST bloquea en severidad alta; auditoria backend bloquea ante vulnerabilidades corregibles; auditoria frontend no bloqueante) en comentarios/parametros; (b) el job no usa `secrets.*`; (c) el job no modifica el arbol de dependencias de los jobs de pruebas. Verificacion: los tres casos pasan.
- [x] 5.4 Smoke local de los escaneos donde sea posible sin red de CI: instalar `bandit` y correr `bandit -r App/Backend/app -lll`; correr `pip-audit -r App/Backend/requirements.txt`; correr `npm audit --audit-level=high` en `App/Frontend/`. Verificacion: los comandos ejecutan; registrar hallazgos preexistentes y su tratamiento (corregir o exceptuar con motivo).
- [x] 5.5 REFACTOR: extraer los parametros repetidos (rutas, nivel de severidad) a comentarios claros y re-correr 5.1/5.3. Verificacion: verdes tras el refactor.

## 6. Evaluacion de seguridad de proveedores (D)

- [x] 6.1 RED: escribir una verificacion que falle porque `docs/seguridad/evaluacion-seguridad-proveedores.md` no existe. Verificacion: falla por archivo ausente.
- [x] 6.2 GREEN: crear `docs/seguridad/evaluacion-seguridad-proveedores.md` con una seccion por proveedor (Twilio, Gemini/Google, Microsoft, N8N), separando postura observable publicamente de clausulas a evaluar por la organizacion adoptante (design D7, SGD-016). Verificacion: la verificacion de 6.1 pasa.
- [x] 6.3 TRIANGULATE: verificar (a) los cuatro proveedores aparecen; (b) cada seccion distingue postura observable de garantia contractual; (c) las garantias no suscritas quedan como accion pendiente; (d) el documento usa "alineado con"/"controles mapeados a" y NO contiene "compliant" ni "certificado". Verificacion: los cuatro casos pasan (`grep` de terminos prohibidos sin coincidencias).
- [x] 6.4 REFACTOR: homogeneizar el formato de las secciones; re-correr 6.3. Verificacion: verde tras el refactor.

## 7. Actualizacion del indice y trazabilidad de gobernanza (D)

- [x] 7.1 Agregar `docs/seguridad/evaluacion-seguridad-proveedores.md` al indice `docs/seguridad/README.md` con su proposito. Verificacion: el indice lista el documento y la referencia resuelve a un archivo existente.
- [x] 7.2 Extender el mapa de trazabilidad del indice con los controles 5.19, 5.20, 5.21, 5.22 y 5.23 apuntando al documento nuevo (SGD-001 modificado). Verificacion: los cinco controles figuran mapeados al documento.
- [x] 7.3 Verificar que la regla de lenguaje sigue cumpliendose en el indice y que no se rompen referencias cruzadas previas (5.1, 5.2, 5.9, 5.12, 5.13, 5.24-5.27, 5.31, 8.26). Verificacion: revision del mapa; todas las referencias resuelven.

## 8. Cierre y validacion

- [x] 8.1 Correr la red de seguridad completa y confirmar sin regresion: `cd App/Backend; pytest -m "not integration" -q`; `cd App/Backend; ruff check .`; `cd App/Frontend; npm run test`; `cd App/Frontend; npm run lint`. Verificacion: todo verde.
- [x] 8.2 Validar el change con `openspec validate --strict c-64-vulnerabilidades-supply-chain`. Verificacion: 0 fallos.
- [x] 8.3 Validar el conjunto con `openspec validate --strict --changes`. Verificacion: 0 fallos.
- [x] 8.4 Confirmar los no-goals: trivy y SBOM NO implementados (solo registrados como diferidos en `design.md`), sin DAST/pentest ni lenguaje de certificacion. Verificacion: `grep -rni "trivy\|sbom" .github/ docker-compose.yml` sin resultados de implementacion; `grep -rni "compliant\|certificado" docs/seguridad/evaluacion-seguridad-proveedores.md` sin coincidencias.
