# Design: Instrumentar la campana (brazo manual e intervencion)

## Context

Ver `proposal.md` - Why. El unico registro de validacion humana vive en `clasificacion_log` (`sector_id_validado` + conjuntos N:N) mutado por `PATCH /clasificaciones/{log_id}/validar`; el route ya tiene `current_user` en scope. La metrica actual `tasa_revision_humana` cuenta casos MARCADOS (`requiere_revision_humana`), no intervenciones efectivas. El corpus (`data/corpus_evaluacion_pseudonimizado.json`) provee `sector_asignado` (consenso) y `tiempo_manual_s`, pero no la clasificacion del operador manual.

## Goals / Non-Goals

- **Goals**: instrumento de captura del brazo manual; metadatos de intervencion persistidos en el log; runbook de campana; metrica de intervencion real.
- **Non-Goals (design-level)**: ejecutar la campana; UI de etiquetado; historial append-only de multiples intervenciones por caso; tocar `docs/Tesis/v9 (IA)/`, categorias o numeros canonicos.

## Decisions

- **D1 — Instrumento de captura: OFFLINE (planilla + CSV), recomendado.** Alternativa: endpoint/tabla en la app. Tradeoff: offline no acopla la captura a la DB de produccion, es operable por etiquetadores sin cuenta y no expone PII; la app da validacion de formato y trazabilidad automatica pero agrega superficie de datos personales y requiere despliegue. Se elige OFFLINE para la campana; la app queda como alternativa documentada. El CSV se versiona sin PII (solo id de corpus + id de etiquetador + sector).
- **D2 — Persistencia de la intervencion: EXTENDER `clasificacion_log`.** Columnas nuevas nullable: `validado_por_empleado_id` (FK empleado, `SET NULL`, sin PII en claro), `validado_en` (instante propio, distinto de `created_at`), `origen_intervencion` (string acotado al conjunto `gate|review|sample|manual_completion|reassignment`). El DELTA antes/despues es RECONSTRUIBLE desde `sector_id_predicho`/`sectores_predichos` vs `sector_id_validado`/`sectores_validados`: no requiere columnas nuevas. Alternativa: tabla dedicada `intervencion_humana` (append-only, multiple por caso); se descarta por ser 1:1 con el log en el alcance actual; se reevalua si aparece mas de una intervencion por caso.
- **D3 — Governance ALTA (auditoria): CONFIRMACION HUMANA OBLIGATORIA** antes de aplicar la migracion y de tocar `clasificacion_log`. El apply DEBE detenerse en un checkpoint y esperar aprobacion explicita del autor; sin aprobacion, no se ejecuta `alembic upgrade` sobre datos reales.
- **D4 — Migracion Alembic nueva** (no mutar `001`): agrega las columnas nullable y la FK a `empleado`; `downgrade` funcional; idempotente sobre la cabeza actual.
- **D5 — Metrica de intervencion real**: `estadisticas_repository.contar_intervenciones` filtra por `validado_en` no nulo en rango; `estadisticas_service` expone `tasa_intervencion_humana` junto a (no en lugar de) `tasa_revision_humana`.
- **D6 — TDD**: tests unitarios (subset SQLite) para repositorio/servicio/origen; tests de integracion PostgreSQL para la migracion y la FK.

## Risks / Trade-offs

- Mutar el esquema de auditoria → checkpoint de confirmacion humana (D3) + migracion nullable reversible.
- Etiquetado no independiente contamina la exactitud → el runbook exige >=2 etiquetadores sin ver la prediccion.
- `origen_intervencion` con valores libres → acotarlo al conjunto canonico y validarlo en schema.

## Migration Plan

1. Revision Alembic con columnas `validado_por_empleado_id`, `validado_en`, `origen_intervencion` (nullable) + FK.
2. Backfill: N/A (columnas nuevas NULL = estado no intervenido).
3. Rollback: `alembic downgrade -1` retira columnas/FK sin tocar filas existentes.

## Open Questions

- Minimo de casos de la campana (N): se fija en el runbook, no cambia el spec ni el enfoque.
