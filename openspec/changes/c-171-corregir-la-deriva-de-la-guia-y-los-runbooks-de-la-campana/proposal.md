## Why

La guia y los runbooks de la campana de medicion (c-165..c-169) quedaron desalineados respecto de su fuente de verdad, `evaluation/data/campana/README.md`, y de los instrumentos que c-166 ya entrego. Durante la planificacion del brazo automatizado aparecieron catorce defectos que impiden ejecutar la campana de forma confiable: el conteo de casos por operador, el criterio de doble cobertura, la ausencia del procedimiento del brazo automatizado, el orden de los pasos y los prerequisitos. Corregirlos antes de aplicar c-166/c-169 evita producir datos de campo con instrucciones erroneas.

## What Changes

- `docs/campana-medicion/guia-ejecucion-campana.md`:
  - O1 y O2 pasan de "100 casos cada uno" a **110 cada uno** (100 de su mitad + 10 cruzados; 20 casos compartidos).
  - La doble cobertura deja de ser "opcional": se declara el criterio fijo de 1 caso de cada 10 por `posicion` por mitad, 20 casos compartidos.
  - Se agrega una seccion del **brazo automatizado**: 3 harnesses (`ingest_via_n8n.py`, `ingest_corpus.py`, `ingest_telefonia_corpus.py`) por los 4 sub-planes `automatizado`, con `--id-corrida`/`--sidecar`/`--json corpus_campana.json` y `--dry-run` primero; los sidecars se escriben en `evaluation/data/campana/sidecar_<id_corrida>.json`.
  - Se generan los **8 sub-planes** (2 mitades x 2 brazos x 2 turnos), no uno.
  - Prerequisitos explicitos: `alembic current` en `024 (head)`, app y N8N en pie.
  - Se declaran los sidecars como entradas, se reordena el flujo (automatizado entre sub-planes y export), se corrige el comando de export (`cd App/Backend`), se agrega su verificacion y la declaracion de legados/vinculos faltantes.
  - `registro_sujetos.csv` se describe como completo (8 filas, P1..P8, sin solapes); se agrega `brazo_manual.csv` al gate; se generaliza "el director de la tesis"; se enumeran las cinco cadenas canonicas de sector.
- `docs/campana-medicion/runbook-brazo-manual-e-intervencion.md`: alinea la doble cobertura a 110/110 y 20 compartidos; reemplaza `A2` por `A1` + `T1` en el registro real.
- `docs/campana-medicion/runbook-doble-etiquetado.md`: alinea el registro de sujetos a `A1` + `T1` (sin `A2`).

## Capabilities

### New Capabilities

None. Es un cambio docs-only: no introduce comportamiento nuevo en el sistema.

### Modified Capabilities

None. No cambia el comportamiento especificado; solo corrige el texto de guias y runbooks para que coincida con la fuente de verdad. El cambio marca `skip_specs: true`.

Nota de residuo: `openspec/specs/evaluation-campaign-instrumentation/spec.md` (ECM-001) todavia describe la doble cobertura como "opcional". Alinear el texto del spec excede este cambio docs-only y se recomienda como cambio de spec posterior.

## Impact

- Archivos modificados: `docs/campana-medicion/guia-ejecucion-campana.md`, `docs/campana-medicion/runbook-brazo-manual-e-intervencion.md`, `docs/campana-medicion/runbook-doble-etiquetado.md`.
- NO se modifica: `evaluation/data/campana/README.md` (fuente de verdad), ni codigo bajo `App/`, `n8n/`, `evaluation/`, ni se corre la campana.
- Dependencias: c-166 (harnesses y runbook contrabalanceado) y c-168 (plantilla y registro de sujetos), ya entregados.
