## Context

Ver `proposal.md` (Why) para la motivacion. Estado y restricciones que condicionan el diseno:

- `.github/` contiene solo `workflows/ci.yml`. No existe `.github/dependabot.yml`.
- El workflow tiene tres jobs (`backend-tests`, `frontend-tests`, `secret-scan`); ninguno hace auditoria de dependencias ni SAST. `secret-scan` ya demuestra el patron de descargar un binario fijado con checksum verificado.
- `App/Backend/requirements.txt` fija exacto la mayoria, pero usa rango para `pydantic>=2.12.5,<3`, `google-genai>=2.20.0`, `cryptography>=43.0.0`, `python-jose[cryptography]>=3.3.0` y `bcrypt>=4.0.0`.
- `App/Frontend/package.json` usa `^` en todas las dependencias y `package-lock.json` esta versionado; el job de frontend instala con `npm ci`.
- `docker-compose.yml`: `postgres:15.5-alpine` y `n8nio/n8n:2.11.2` estan fijadas; `nginx:alpine` y `ngrok/ngrok:latest` no lo estan.
- No existe documento de evaluacion de seguridad de proveedores; `docs/seguridad/instrumento-transferencia-internacional.md` (C-66) es legal, no de seguridad del proveedor.
- El stack es de desarrollo local; el repositorio puede cerrar lo (T) tecnico y lo (D) documental, no lo (O) organizacional.
- `docs/seguridad/modelado-amenazas-sdlc.md:56` mapea la brecha a 8.8/8.28/8.29 -> C-64; el gap assessment la lista en 8.7, 8.8, 8.28 y 8.29.

### Referencias de lectura (Leer antes)

- `docs/cumplimiento/plan-cambios-cumplimiento.md` (fila C-64; fase 21).
- `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` (8.7, 8.8, 8.28, 8.29).
- `docs/seguridad/modelado-amenazas-sdlc.md` §4 (amenaza "Dependencias sin control de CVE").
- `.github/workflows/ci.yml` (patron de jobs y de binario fijado con checksum).
- `docs/seguridad/README.md` (regla de lenguaje y mapa de trazabilidad a extender).

## Goals / Non-Goals

**Goals:**

- Dejar el repositorio con deteccion automatizada de vulnerabilidades de dependencias y SAST, y con actualizaciones automatizadas de dependencias.
- Fijar las imagenes Docker flotantes del stack sin romper el arranque local.
- Mejorar el pinning de dependencias de forma conservadora (acotar lo seguro, documentar el resto) sin degradar la capacidad de recibir parches de seguridad.
- Documentar la evaluacion de seguridad de proveedores con lenguaje de alineacion, sin declarar conformidad.

**Non-Goals:**

- trivy (escaneo de imagenes) y SBOM: evaluados y diferidos (ver D8). No se implementan.
- DAST, pentest, formacion en seguridad, NDA y controles de trabajo remoto.
- Cambios de codigo de aplicacion en `App/Backend/app/` o `App/Frontend/src/`.
- Certificacion ISO/NIST o cualquier afirmacion de conformidad.

## Decisions

### D1 — Job de escaneo dedicado en lugar de pasos dentro de los jobs de pruebas

Se agrega un cuarto job `security-scan` en `.github/workflows/ci.yml`, en paralelo a los existentes, en lugar de insertar los escaneos como pasos de `backend-tests`/`frontend-tests`.

- Razon: semantica de fallo independiente (un hallazgo de seguridad no debe confundirse con un test roto), entorno aislado (las herramientas de escaneo no contaminan el arbol de dependencias de las pruebas) y trazabilidad clara del resultado.
- Alternativas descartadas: (a) pasos dentro de los jobs de pruebas (acopla seguridad a pruebas y ensucia el entorno); (b) job unico combinando backend y frontend (menos legible y sin cache de Python/Node coherente).
- El job instala las herramientas fijadas (mismo patron que `ruff==0.8.4` y gitleaks fijado) para corridas reproducibles.

### D2 — SAST con bandit, bloqueo solo en severidad alta

El SAST del backend es `bandit` sobre `App/Backend/app/` (el codigo de aplicacion; se excluyen `tests/` y `alembic/`).

- Razon: bandit es puro Python, offline, sin reglas pesadas ni servicios; encaja con la CI sin secretos.
- Politica de bloqueo: bloquear ante hallazgos de severidad **alta** (`-lll`); reportar media y baja sin bloquear. El arranque conservador evita bloquear el pipeline por deuda preexistente y mantiene la señal util.
- Alternativas descartadas: (a) semgrep (reglas mas ricas pero mayor costo de red y mantenimiento; puede reconsiderarse); (b) bloquear ante severidad media (riesgo de bloquear por falsos positivos y deuda, ver Risks).

### D3 — pip-audit bloqueante ante vulnerabilidades corregibles

`pip-audit` corre sobre `App/Backend/requirements.txt`. Política: la corrida **falla** ante vulnerabilidades conocidas que tengan corrección disponible; las que no la tengan se reportan sin bloquear.

- Razon: forzar la actualización cuando existe el arreglo es el valor real del control; bloquear por hallazgos sin arreglo dejaria la CI permanentemente roja por dependencias transitivas fuera de control.
- Via documentada para exceptuar: `--ignore-vuln <ID>` con el identificador y su motivo registrados, cuando un hallazgo no tenga corrección aplicable. Las excepciones son explicitas y auditables, nunca un `--continue-on-error` global.
- Alternativa descartada: fallar ante cualquier hallazgo (bloqueo permanente por deuda no accionable).

### D4 — npm audit no bloqueante en esta iteracion

`npm audit --audit-level=high` corre sobre `App/Frontend/` en modo **reporte** (no bloqueante) en esta primera iteracion.

- Razon: una fraccion importante de los avisos del ecosistema npm proviene de dependencias de desarrollo transitivas sin correccion simple; forzar el bloqueo hoy romperia la CI por deuda no accionable. El frontend ya tiene suite de pruebas y lint como red.
- La decision de pasar a bloqueante (y su umbral) queda como pregunta abierta (OQ1), sin cambiar specs ni enfoque. OQ1 fue resuelta por el autor: se ACEPTA mantener `npm audit` NO bloqueante (modo reporte) en esta primera iteracion, revisable en una iteracion futura.

### D5 — Fijar las imagenes Docker flotantes a versiones explicitas

`nginx:alpine` y `ngrok/ngrok:latest` se fijan a una version explicita.

- Mecanismo: resolver la version estable vigente al momento del apply inspeccionando el registro (`docker manifest inspect` / `docker pull`), fijar el tag concreto en `docker-compose.yml` y verificar el stack con `docker compose config`.
- Razon: `latest` produce cambios silenciosos y no reproducibles; fijar la version es el cambio de cadena de suministro de mayor valor y menor riesgo.
- Alternativa descartada: fijar por digest (aun mas fuerte) — se evalua como mejora posterior; el tag explicito es suficiente para esta iteracion y mas legible. Se evaluara en un change posterior la combinacion tag+digest.

### D6 — Pinning de Python/JS conservador (acotar lo seguro, documentar el resto)

No se convierten todos los rangos en pins duros. Mejora elegida:

- **Frontend**: se mantiene `^` en `package.json` y `package-lock.json` versionado; la reproducibilidad la garantiza `npm ci`. No hay cambio de archivo; se documenta la decision. Razon: el lockfile ya fija el arbol efectivo; convertir a pins duros en `package.json` agrega mantenimiento sin ganancia real.
- **Backend**: se agregan cotas superiores donde la version mayor es una frontera de compatibilidad real: `google-genai>=2.20.0,<3`, `bcrypt>=4.0.0,<5`, `python-jose[cryptography]>=3.3.0,<4`. `cryptography>=43.0.0` se deja **sin** cota superior y se documenta: los parches de seguridad llegan en releases menores y una cota impediria adoptarlos a tiempo.
- Razon: acotar las fronteras de mayor reduce el riesgo de un salto incompatible sin frenar los parches.
- Alternativas descartadas: (a) pin duro de todo (rompe el flujo de parches y multiplica el mantenimiento; el propio `requirements.txt` documenta pisos que rompen al bajarlos); (b) no tocar nada y solo documentar (deja el riesgo de salto de mayor sin mitigar).

### D7 — Evaluacion de seguridad de proveedores como documento de gobernanza

Se crea `docs/seguridad/evaluacion-seguridad-proveedores.md` bajo `docs/seguridad/`, con una seccion por proveedor (Twilio, Gemini/Google, Microsoft, N8N) que separa la postura observable publicamente de las clausulas a evaluar por la organizacion adoptante.

- Razon: es un documento de gobernanza de seguridad; su lugar natural es `docs/seguridad/`, junto al resto de los documentos (SGD-001). Se referencia desde el indice y se mapea a 5.19-5.23.
- Alternativa descartada: ubicarlo en `docs/cumplimiento/` (mezcla gobernanza con el diagnostico del gap assessment).
- Regla de lenguaje: "alineado con" / "controles mapeados a"; prohibido "compliant" y "certificado". El documento documenta el mecanismo de evaluacion; no declara garantias suscritas.

### D8 — trivy y SBOM evaluados y diferidos

El escaneo de imagenes (trivy) y la generacion de SBOM se evaluan y se difieren en este change.

- Razon: trivy agrega costo de red (descarga de base de vulnerabilidades) y complejidad de CI (umbral, cache, ruido de CVEs de base image) frente a un valor de anexo menor en esta etapa; el SBOM es un artefacto util para auditoria pero de bajo retorno operativo hoy. Ambos quedan registrados como decididos (design.md) para justificar el alcance y evitar que se lean como olvidos.
- Alternativa descartada: implementarlos ahora (mayor costo sin cambio en el objetivo de defensa/annex).
- No se declaran implementados en ningun artefacto.

### D9 — Dependabot agrupado y sin auto-merge

`.github/dependabot.yml` con `version: 2`, tres entradas (`pip` en `/App/Backend`, `npm` en `/App/Frontend`, `github-actions` en `/`), `schedule.interval: weekly` y `groups` por ecosistema. Sin auto-merge ni auto-aprobacion.

- Razon: agrupar evita una avalancha de PRs; dejar la fusion a revision humana mantiene el control sobre los cambios de dependencias.
- Alternativa descartada: actualizaciones diarias sin agrupacion (ruido excesivo).

## Risks / Trade-offs

- [bandit produce falsos positivos o hallazgos de severidad alta preexistentes] -> El bloqueo se limita a severidad alta; si aparece un hallazgo real, se corrige o se exceptua con `# nosec`/exclusion justificada en el mismo change.
- [pip-audit reporta vulnerabilidades sin correccion disponible] -> No bloquean; se registran como excepcion explicita (`--ignore-vuln`) solo si reaparecen como ruido, evitando un `continue-on-error` global.
- [fijar nginx/ngrok a un tag inexistente o incompatible rompe el stack local] -> Resolver el tag contra el registro antes de fijarlo y validar con `docker compose config`; el pin se registra en el mismo archivo ya versionado.
- [acotar cotas superiores en el backend bloquea una actualizacion necesaria] -> Las cotas se eligen en fronteras de mayor reales; el flujo de Dependabot propone la subida de la cota cuando corresponda.
- [npm audit no bloqueante da falsa sensacion de cobertura] -> Se declara explicitamente en el job y en design.md; la decision de mantenerlo no bloqueante en esta iteracion fue aceptada por el autor (OQ1) y queda revisable.
- [el job de escaneo agrega tiempo de CI] -> Corre en paralelo a los jobs de pruebas y usa caches de pip/npm; no alarga la ruta critica de merge salvo por los escaneos mismos.

## Open Questions

- **OQ1 (ACEPTADO por el autor)**: `npm audit` permanece NO bloqueante (modo reporte) en esta primera iteracion; se ACEPTA explicitamente y queda revisable en una iteracion futura (umbral `high`/`critical` a decidir entonces). No cambia specs ni el enfoque de este change.
- **OQ2**: el tag exacto con el que se fijan `nginx` y `ngrok` se resuelve al apply contra el registro; no altera el enfoque.
- **OQ3**: si conviene versionar un archivo de excepciones de `pip-audit` (allowlist de `--ignore-vuln`) en lugar de inline en el workflow. Se decide al apply segun aparezcan o no excepciones reales.
