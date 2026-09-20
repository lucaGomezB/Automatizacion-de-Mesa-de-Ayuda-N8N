## Context

Ver `proposal.md — Why`. El bootstrap local ya tiene su contrato en las specs vivas:

- `openspec/specs/local-bootstrap/spec.md` — el preflight de entorno incluye `JWT_SECRET_KEY` (y sus escenarios de ausente/placeholder).
- `openspec/specs/cost-readiness/spec.md` — requirement "Cableado automatico del preflight a los caminos de arranque y CI", con los escenarios de bloqueo y bypass (`UP_SKIP_COST_PREFLIGHT=1`, solo valor `1`).
- `openspec/specs/project-documentation/spec.md` — los dos requisitos que este change MODIFICA.

La documentacion afectada vive fuera de la suite: `README.md` (raiz) y `docs/operational-guide.md`. El repo ya tiene precedentes de tests estructurales de contenido sin runtime: `App/Backend/tests/test_n8n_workflow.py` (asserta sobre `n8n/workflow.json`) y `scripts/tests/test_up_preflight.sh` (asserta estructura de `up.ps1` incluso sin PowerShell). No existe hoy ningun test que asserta sobre README o la guia operativa.

## Goals / Non-Goals

**Goals:**

- Sincronizar README y guia operativa con el comportamiento real del bootstrap (`JWT_SECRET_KEY`, gate de costo, bypass).
- Dejar una red de seguridad que falle si el texto vuelve a desincronizarse en los tokens estables.
- Respetar Strict TDD: test primero (RED) sobre los tokens, luego editar la doc (GREEN).

**Non-Goals:**

- No se toca `scripts/up.sh`, `scripts/up.ps1`, el Makefile, el preflight ni `n8n/workflow.json`.
- No se reescribe la guia operativa completa: se interviene la seccion 1.3 y, si aplica, la seccion de backup.
- No se valida prosa: los tests solo verifican presencia de tokens estables y ausencia de contradicciones evidentes.

## Decisions

### D1 — Test estructural en la suite backend (Python/pytest), no en `scripts/tests/`

**Decision:** agregar `App/Backend/tests/test_docs_bootstrap_sync.py`, que lee `README.md` y `docs/operational-guide.md` por path relativo a la raiz del repo y asserta tokens.

**Rationale:** `test_n8n_workflow.py` ya establece el patron de test estructural de archivos no-Python desde la suite backend, y esa suite corre en CI (`backend-tests`). El harness bash `scripts/tests/test_up_preflight.sh` esta atado a logica de scripts, no a prosa.

**Alternativas consideradas:**
- Test en `scripts/tests/` en bash: desaprovecha pytest y duplica harness; peor ergonomia para asserts de texto.
- Sin test, solo verificacion manual: descartado por el mandato de Strict TDD y por el riesgo real de re-desincronizacion.

### D2 — Assertar tokens estables, no frases completas

**Decision:** los asserts buscan `JWT_SECRET_KEY`, `UP_SKIP_COST_PREFLIGHT`, `scripts/up.sh` / `scripts/up.ps1` / `make up`, y `docker compose up -d`, mas la seccion de la guia.

**Rationale:** tokens que las specs ya nombran y que no deberian cambiar. Un assert sobre una oracion completa convierte cualquier mejora de redaccion en un falso rojo.

**Alternativas consideradas:** snapshot del archivo entero — demasiado fragil y no expresa la intencion.

### D3 — Guia operativa como fuente narrativa; README resume y enlaza

**Decision:** la seccion 1.3 de la guia describe el comando unico, el gate y el bypass; el README documenta las condiciones de fallo y el bypass en su seccion del comando unico, y delega el detalle a la guia via el enlace ya existente.

**Rationale:** evita duplicar procedimiento extenso en dos archivos y mantener dos redacciones divergentes.

### D4 — Bypass documentado como excepcion, no como camino

**Decision:** ambos documentos presentan `UP_SKIP_COST_PREFLIGHT=1` como escape explicito que emite advertencia audible y no sustituye al gate.

**Rationale:** la spec de `cost-readiness` lo define como "unica excepcion" y exige la advertencia; la doc no debe normalizar el bypass.

## Risks / Trade-offs

- [El test de docs acopla la suite a prosa] → Asserts solo sobre tokens estables, no frases; documentarlo en el docstring del test.
- [Divergencia entre README y guia] → El README enlaza a la guia y solo resume; tokens compartidos cubiertos por el mismo test.
- [Path relativo fragil desde `App/Backend/tests/`] → Reutilizar el patron `parents[3]` de `test_n8n_workflow.py`.

## Migration Plan

Documentacion y test, sin migracion de datos ni de esquema. Rollback: revertir el commit (borra test y restaura los dos archivos). No hay estado de runtime que restaurar.

## Open Questions

- Ninguna que bloquee. Si en el apply la seccion 1.2 muestra `Gestion_Incidentes/.env.example` (ruta aparentemente obsoleta frente a `App/Backend/.env`), se documentara el desajuste como observacion sin corregirlo, para mantener el change atomico y centrado en el bootstrap.