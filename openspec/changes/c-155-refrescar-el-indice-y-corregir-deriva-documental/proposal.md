## Why

El registro canonico `CHANGES.md` quedo desactualizado respecto de `main`: todavia presenta C-151 y C-153 como no archivados y no registra C-152 ni C-154, que ya estan archivados. En paralelo, la base de conocimiento contradice al codigo en tres puntos verificables (el nodo JS del canal correo, el canal telefonico y el aislamiento por sector) y `docs/por_implementar.md` cita umbrales retirados. La tesis se sostiene sobre evidencia documental: un registro que no coincide con el estado archivado ni con el codigo compromete su trazabilidad.

## What Changes

- **Refrescar `CHANGES.md`**: C-151 pasa de "APLICADO ... pendiente de archive" a ARCHIVADO; C-153 pasa de "EN APLICACION" a ARCHIVADO; se agregan las entradas de C-152 y C-154 (ambas archivadas) con su scope, verificacion, rollback y "Leer antes"; y se actualizan las lineas de resumen (Total, Fases y numeracion) que hoy se detienen en C-149.
- **Corregir la deriva de la base de conocimiento**:
  - `knowledge-base/07_flujos_principales.md` — el nodo JS del canal correo deja de describirse como "hoy placeholder" (C-04/C-05 estan archivados).
  - `knowledge-base/07_flujos_principales.md` — el Flujo 3 deja de describir el `AI Agent` de LangChain, la sesion en Redis y el bucle de refinamiento (retirados por C-72) como pasos vigentes; pasa a describir la cascada `HybridClassifier` del backend.
  - `knowledge-base/03_actores_y_roles.md` — deja de afirmar que el aislamiento por sector no existe; documenta el modo de visibilidad SECTOR (`gestion_incidentes`, VIS-007) tal como lo declara `role_policy.py`.
- **Alinear `docs/por_implementar.md`**: el encabezado de estado y el umbral `< 0.90` se corrigen contra el estado vigente y `settings.py` (0.5166 / 0.70), o se rotulan explicitamente como historicos.

No se modifica codigo, ni los cinco strings canonicos de sectores, ni `requirements.txt`, ni `openspec/config.yaml`.

## Capabilities

### New Capabilities

Ninguna. El change es de higiene documental; no introduce comportamiento de sistema nuevo.

### Modified Capabilities

- `project-documentation`: el contrato de fidelidad documental se extiende para exigir que el indice `CHANGES.md` refleje el estado real del archivo de changes, que la base de conocimiento no describa componentes retirados (agente telefonico, Redis, bucle de refinamiento) como vigentes, que la politica de visibilidad documentada incluya el modo SECTOR, y que `docs/por_implementar.md` declare umbrales reproducibles desde `settings.py`.

## Impact

- **Documentacion afectada**: `CHANGES.md`, `knowledge-base/07_flujos_principales.md`, `knowledge-base/03_actores_y_roles.md`, `docs/por_implementar.md`.
- **Sin impacto en codigo**: no se tocan `App/Backend/**`, `App/Frontend/**`, `n8n/workflow.json`, `App/Backend/requirements.txt` ni `openspec/config.yaml`. La barrera `scripts/preflight/docs_stack_sync.py` se mantiene sin cambios.
- **Riesgo de consistencia**: las lineas de resumen de `CHANGES.md` son largas y repetitivas; una actualizacion parcial introduce nuevas incoherencias. Se mitiga recalculando los conteos contra `openspec/changes/archive/` y el estado activo.
