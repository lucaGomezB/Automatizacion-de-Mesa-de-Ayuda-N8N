# Verification Report

**Change**: c-60-directorio-endurecimiento
**Version**: delta specs (employee-directory MODIFIED/ADDED; incident-visibility MODIFIED/ADDED)
**Mode**: Strict TDD (orchestrator-injected; authoritative)
**Verified**: 2026-10-06
**Store**: openspec (filesystem)

> **RE-VERIFICATION (2026-10-06).** This report was re-run after warning fixes. The
> prior result was PASS WITH WARNINGS with 2 PARTIAL scenarios. Both are now closed by
> executed passing tests: VIS-001 scenario 8 via
> `tests/test_clasificacion_visibility.py::test_mesa_de_ayuda_lee_en_revision_y_no_plain_404`
> and DIR-009 scenario 3 via
> `tests/test_directorio_cumplimiento.py::test_evidencia_registra_aprobacion_high_pendiente_y_datos_reales_bloqueados`
> and `::test_no_existe_un_toggle_de_activacion_de_datos_reales`. The stale `CHANGES.md`
> line (WARNING 3) is fixed. Scenario compliance moved from **31/33 to 33/33**. Residuals
> kept: task 7.4 external human HIGH approval OUTSTANDING (real data blocked) and the
> coverage-tool under-report artifact.

---

## Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 33 |
| Tasks complete `[x]` | 33 |
| Tasks incomplete `[ ]` | 0 |

All 33 tasks are checked. Task **7.4** is checked because its deliverable was to
REGISTER the pending HIGH human approval (done 2026-10-06, documented in
`docs/directorio-evidencia-cumplimiento.md` §4 and in tasks.md). The underlying
human HIGH approval remains **OUTSTANDING** and real data stays blocked. It is
reported as a WARNING/known item, not treated as a CRITICAL gate (per instructions).

---

## Build & Tests Execution

**Build**: ➖ Not applicable (Python package; no build step). Lint used as quality gate.

**Lint** (`ruff check .`): ✅ Passed — `All checks passed!` (exit 0).

**Tests — offline subset** (`pytest -m "not integration"`): ✅ **991 passed, 39 deselected, 1 xfailed, 0 failed** (127.08s). Up from 988 in the prior run (+3: the two new DIR-009 inspection tests and the new VIS-001 endpoint test).
```
1 xfailed: tests/test_n8n_workflow.py::test_payload_has_no_obvious_pii
  -> documented C-04 privacy gap (PII in clear N8N->backend), unrelated to c-60.
```

**Tests — targeted re-check** (`pytest tests/test_clasificacion_visibility.py tests/test_directorio_cumplimiento.py -m "not integration" -q`): ✅ **21 passed** (`test_clasificacion_visibility.py`: 15; `test_directorio_cumplimiento.py`: 6), 0 failed.

**Tests — PostgreSQL integration** (`pytest -m integration`, disposable DB `mesa_de_ayuda_test` on compose `mesa_local-postgres-1` :5433, healthy): ✅ **39 passed, 992 deselected, 0 failed** (23.69s). Application DB never targeted.

**OpenAPI sync** (`pytest tests/test_openapi_sync.py -v`): ✅ **5 passed**. `docs/openapi.json` regenerated and in sync (`/api/v1/directorio/purga` present; `mesa_de_ayuda` present in the rol enum).

**Strict OpenSpec validation** (`openspec validate --strict --changes c-60-directorio-endurecimiento`): ✅ **1 passed, 0 failed** (6 changes validated in the project; exit 0).

**Coverage** (offline suite, changed modules only): aggregate **85%** (726 stmts / 111 miss). Carried from the prior run — not re-executed in this pass (the prompt scoped re-run to the test suites, lint, integration, and strict validation). See Changed File Coverage for per-file detail and a tooling caveat.

---

## TDD Compliance

| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | Engram apply-progress (`sdd/c-60-directorio-endurecimiento/apply-progress`, observation #1175) contains a "TDD Cycle Evidence (PART G)" table; the remaining tasks encode RED/GREEN/TRIANGULATE inline in `tasks.md` (repo-local convention — no separate apply-progress file on disk, same as c-41/c-70). |
| All tasks have tests | ✅ | 33/33 code tasks map to a test file; all referenced files exist. |
| RED confirmed (tests exist) | ✅ | 12 changed/new offline test files + 1 integration file present and collected (113 offline tests + 2 PG tests; +3 tests added to two existing files). |
| GREEN confirmed (tests pass) | ✅ | 991 offline + 39 integration + 5 OpenAPI pass on execution. No failures. |
| Triangulation adequate | ✅ | Multi-case triangulation for the risky behaviors (4 roles parametrized; REVISION sin-sector/con-revision/sector-bound; FIFO ordering; idempotence; 201-sin-sector/422-con-sector; downgrade->upgrade). VIS-001 endpoint test triangulates positive (revision -> 200) against negative (plain -> 404). DIR-009 inspection pairs the evidence-doc assertion with the absence-of-toggle assertion. |
| Safety Net for modified files | ⚠️ | Explicitly captured for the PART G batch (20/20 service, 8/8 API) and task 1.2 (baseline 43 passed). Full per-file safety-net log for all earlier batches is not persisted. |

**TDD Compliance**: 5/6 checks fully passed, 1 partially reported (retrospective evidence, not a functional defect).

---

## Test Layer Distribution

| Layer | Tests | Files | Tools |
|-------|-------|-------|-------|
| Unit (pure / AST-static / SQLite-service) | ~61 | 6 | pytest |
| Integration/API (ASGI in-process, SQLite via httpx ASGITransport) | ~50 | 6 | pytest + httpx + pytest-asyncio |
| PostgreSQL integration (`@pytest.mark.integration`, disposable DB) | 2 | `tests/integration/test_directorio_postgres.py` | pytest + asyncpg |
| E2E | 0 | — | not installed (no browser/Playwright) |
| **Total (c-60 related)** | **113 offline + 2 PG** | **13** | |

Note: "API" tests here run the real FastAPI app in-process against SQLite (role/sector/scope
end-to-end at the API + service + repository layers). No E2E tooling is available; this is
consistent with the project's testing capabilities.

---

## Changed File Coverage

Offline suite, changed modules only (raw `--cov-report=term-missing`):

| File | Line % | Missed Lines | Rating |
|------|--------|--------------|--------|
| `app/models/empleado.py` | 96% | 118 | ✅ Excellent |
| `app/repositories/incidente_repository.py` | 98% | 225 | ✅ Excellent |
| `app/schemas/directorio.py` | 100% | — | ✅ Excellent |
| `app/services/directorio_service.py` | 94% | 144,175-179,191,194,204 | ✅ Excellent |
| `app/services/incident_visibility.py` | 92% | 76,80-82 | ✅ Excellent |
| `app/services/incidente_service.py` | 83% | 150,152,202,224,312-327,... | ✅ Acceptable |
| `app/routes/clasificaciones.py` | 93% | 121,161 | ✅ Excellent |
| `scripts/seed_directorio.py` | 80% | 164,183,192-207,211 (CLI `_main`) | ⚠️ Acceptable |
| `app/repositories/clasificacion_repository.py` | 74% | 56-61,84,129,... | ⚠️ Low* |
| `app/routes/directorio.py` | 72% | 105,121-127,... | ⚠️ Low* |
| `app/services/clasificacion_service.py` | 62% | 83,161-193,... | ⚠️ Low* |
| `scripts/purgar_directorio.py` | 55% | 59,65-78,82 (CLI `_main`) | ⚠️ Low* |

**Average changed file coverage**: 85%

`*` **Tooling caveat (verified):** coverage under-reports paths exercised through the ASGI
request coroutine in this environment. A runtime probe (wrapping `ClasificacionService.validate`
and `.list_by_incidente`) recorded **validate called 4× and list_by_incidente called 4×** by
`tests/test_clasificacion_visibility.py` — the exact tests the raw report marks as "missed"
(`validate` lines 161-193). The same anomaly affects `routes/directorio.py`,
`clasificacion_repository.py`. Reproduced under both the default core and `COVERAGE_CORE=pytrace`,
and after clearing `__pycache__`. The behavioral tests do exercise and assert these paths; the
raw percentages for API-only code paths are therefore **underestimates**, not real gaps. Lines
outside the change scope (CLI `_main`, full N-a-N validation path) legitimately remain uncovered.

---

## Assertion Quality

Scanned all 13 test files related to the change.

**Assertion quality**: ✅ All assertions verify real behavior.

- No tautologies (`assert True`, `expect(1)==1`), no type-only-only assertions, no ghost loops, no
  render-without-behavior smoke tests. Static-inspection tests (`test_directorio_purga_no_automatica`,
  `test_directorio_cumplimiento`, `test_rutas_y_servicio_no_consultan_el_entorno`) are structural
  guards against a real risk (cron/scheduler, blind index, environment leakage) and assert concrete
  set/AST/source facts — considered valid.
- Empty assertions are paired with non-empty companions (e.g. `revision-pendiente` vacío asserts
  `[]` while admin/sector tests assert non-empty `[log_a, log_b]`).
- Triangulation shows variance in expected values (roles, sector membership, ordering, idempotence).

---

## Quality Metrics

**Linter**: ✅ No errors (`ruff check .` clean; `E501` ignored by project config).
**Type Checker**: ➖ Not available (project has no mypy/pyright gate).
**Strict OpenSpec validation**: ✅ Pass.

---

## Spec Compliance Matrix

### employee-directory (DIR-007 MODIFIED; DIR-008 ADDED; DIR-009 ADDED)

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| DIR-007 | Empleado desactivado no resuelve | `tests/test_contact_resolution_service.py::test_empleado_inactivo_no_resuelve` | ✅ COMPLIANT |
| DIR-007 | Reactivacion | `tests/test_directorio_service.py::test_desactivacion_no_borra_y_reactivacion`, `::test_desactivacion_registra_fecha_baja_y_reactivacion_la_limpia` | ✅ COMPLIANT |
| DIR-007 | Borrado por retencion | `tests/test_directorio_service.py::test_purgar_vencidos_borra_solo_bajas_mayores_a_un_anio` | ✅ COMPLIANT |
| DIR-007 | Purga manual disparada por un operador | `tests/test_api_directorio_purga.py::test_admin_dispara_la_purga_y_recibe_ids`, `tests/test_purgar_directorio_script.py::test_purgar_directorio_borra_vencidos_y_conserva_activos` | ✅ COMPLIANT |
| DIR-007 | Sin automatizacion de la purga | `tests/test_directorio_purga_no_automatica.py::test_no_hay_librerias_de_scheduler_en_el_codigo_de_produccion`, `::test_la_purga_solo_se_invoca_desde_entradas_humanas` | ✅ COMPLIANT |
| DIR-007 | Registro auditable con ids | `tests/test_directorio_service.py::test_purgar_vencidos_loggea_conteo_sin_pii` (asserts `ids == [viejo.id]`, email/telefono absent) | ✅ COMPLIANT |
| DIR-007 | Borrado por retencion idempotente | `tests/test_directorio_service.py::test_purgar_vencidos_es_idempotente`, `tests/test_api_directorio_purga.py::test_admin_dispara_la_purga_y_recibe_ids` (2ª corrida `{purgados:0, ids:[]}`) | ✅ COMPLIANT |
| DIR-007 | Borrado por ARCO | `tests/test_directorio_service.py::test_borrado_arco_elimina_fisicamente` | ✅ COMPLIANT |
| DIR-008 | Seed rechazado fuera de desarrollo | `tests/test_seed_directorio_guard.py::test_seed_rechaza_production_sin_tocar_la_base`, `::test_verificar_entorno_rechaza_production_y_acepta_dev` | ✅ COMPLIANT |
| DIR-008 | Seed permitido en desarrollo | `tests/test_seed_directorio_guard.py::test_seed_procede_en_entornos_permitidos[development/local/test]` | ✅ COMPLIANT |
| DIR-008 | El runtime normal no se gatea | `tests/test_seed_directorio_guard.py::test_runtime_no_se_gatea_con_environment_production`, `::test_rutas_y_servicio_no_consultan_el_entorno` | ✅ COMPLIANT |
| DIR-009 | Sin PII real en repositorio y base | `tests/test_directorio_cumplimiento.py::test_contactos_del_seed_son_sinteticos`, `tests/test_seed_directorio.py::test_seed_usa_datos_sinteticos` | ✅ COMPLIANT |
| DIR-009 | Sin clave de indice ciego | `tests/test_directorio_cumplimiento.py::test_settings_no_expone_una_clave_de_indice_ciego`, `::test_codigo_y_migraciones_no_introducen_indice_ciego`, `::test_empleado_no_tiene_columna_de_hash_ni_indice_ciego` | ✅ COMPLIANT |
| DIR-009 | Datos reales bloqueados hasta la aprobacion | `tests/test_directorio_cumplimiento.py::test_evidencia_registra_aprobacion_high_pendiente_y_datos_reales_bloqueados` (evidence doc registers PENDIENTE / BLOQUEADO / DATOS REALES / SINTETICOS), `::test_no_existe_un_toggle_de_activacion_de_datos_reales` (no `Settings` field nor production code exposes a real-data toggle) | ✅ COMPLIANT |

### incident-visibility (VIS-001 MODIFIED; VIS-002 ADDED)

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| VIS-001 | Administrador ve todos los incidentes | `tests/test_incident_visibility.py::test_admin_ve_todos_los_incidentes` | ✅ COMPLIANT |
| VIS-001 | Mesa de ayuda ve incidentes sin sector o en revision | `tests/test_incident_visibility.py::test_mesa_de_ayuda_ve_sin_sector_y_en_revision` | ✅ COMPLIANT |
| VIS-001 | Mesa de ayuda no ve incidentes ya asignados y resueltos | `tests/test_incident_visibility.py::test_mesa_de_ayuda_acceso_puntual_respeta_revision` (404 on plain sector incident) | ✅ COMPLIANT |
| VIS-001 | No administrador ve solo su sector | `tests/test_incident_visibility.py::test_no_admin_ve_solo_su_sector` | ✅ COMPLIANT |
| VIS-001 | Sin sector no ve incidentes | `tests/test_incident_visibility.py::test_cuenta_sin_empleado_alcance_vacio` | ✅ COMPLIANT |
| VIS-001 | Alcance aplicado en el acceso puntual | `tests/test_incident_visibility.py::test_acceso_puntual_fuera_de_sector_404`, `::test_acceso_puntual_sin_empleado_404` | ✅ COMPLIANT |
| VIS-001 | Administrador lee clasificaciones de cualquier sector | `tests/test_clasificacion_visibility.py::test_admin_lee_clasificaciones_de_cualquier_sector` | ✅ COMPLIANT |
| VIS-001 | Mesa de ayuda lee clasificaciones de un incidente en revision | `tests/test_clasificacion_visibility.py::test_mesa_de_ayuda_lee_en_revision_y_no_plain_404` (revision incident as `mesa_de_ayuda` → 200 with `log_a`; plain sector incident → 404 NOT_FOUND) | ✅ COMPLIANT |
| VIS-001 | No administrador lee clasificaciones de su sector | `tests/test_clasificacion_visibility.py::test_no_admin_lee_clasificaciones_de_su_sector` | ✅ COMPLIANT |
| VIS-001 | Lectura de clasificaciones fuera de alcance es no encontrada | `tests/test_clasificacion_visibility.py::test_no_admin_lee_fuera_de_sector_404`, `::test_alcance_vacio_lee_404` | ✅ COMPLIANT |
| VIS-001 | Administrador valida clasificaciones de cualquier sector | `tests/test_clasificacion_visibility.py::test_admin_valida_cualquier_log` | ✅ COMPLIANT |
| VIS-001 | No administrador valida clasificaciones de su sector | `tests/test_clasificacion_visibility.py::test_no_admin_valida_dentro_de_sector_200` | ✅ COMPLIANT |
| VIS-001 | Validacion fuera de alcance es no encontrada y no muta | `tests/test_clasificacion_visibility.py::test_no_admin_valida_fuera_de_sector_404_y_no_muta` | ✅ COMPLIANT |
| VIS-001 | Acceso anonimo a clasificaciones es no autorizado | `tests/test_clasificacion_visibility.py::test_anonimo_401` | ✅ COMPLIANT |
| VIS-002 | Administrador ve la cola completa | `tests/test_clasificacion_visibility.py::test_revision_pendiente_admin_ve_cola_completa` (FIFO `[log_a, log_b]`) | ✅ COMPLIANT |
| VIS-002 | Mesa de ayuda ve la cola completa | `tests/test_clasificacion_visibility.py::test_revision_pendiente_mesa_de_ayuda_ve_cola_completa` | ✅ COMPLIANT |
| VIS-002 | Sector-bound ve solo su cola | `tests/test_clasificacion_visibility.py::test_revision_pendiente_sector_bound_ve_solo_su_cola` (excludes other sector) | ✅ COMPLIANT |
| VIS-002 | Alcance vacio no ve pendientes | `tests/test_clasificacion_visibility.py::test_revision_pendiente_alcance_vacio_ve_lista_vacia` | ✅ COMPLIANT |
| VIS-002 | Acceso anonimo rechazado | `tests/test_clasificacion_visibility.py::test_revision_pendiente_anonimo_401` | ✅ COMPLIANT |

**Compliance summary**: **33/33 scenarios fully compliant** (executed tests passed). 2 previously
PARTIAL scenarios are now COMPLIANT (VIS-001 scenario 8 and DIR-009 scenario 3); 0 FAILING,
0 UNTESTED, 0 PARTIAL. The DIR-009 requirement is a governance control with no runtime gate by
design; the scenario "Datos reales bloqueados hasta la aprobacion" is proven behaviorally by the
absence of any activation toggle (`Settings` and production code) plus the evidence artifact
recording the approval as PENDIENTE/BLOQUEADO.
Also covered by tests: task 2.5 CHECK real en PostgreSQL (`test_directorio_postgres.py::test_check_rol_acepta_mesa_de_ayuda_sin_sector`, `::test_check_rol_rechaza_valor_fuera_de_vocabulario`) and migration 012 (`test_migration_012_directorio_rol.py`, 3 tests: chain `down_revision="011"`, upgrade accepts `mesa_de_ayuda` / rejects invalid, downgrade restores 3-value CHECK).

---

## Correctness (Static — Structural Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| DIR-007 retencion/purga manual con ids | ✅ Implemented | `purgar_vencidos` collects ids, audits `{purgados, ids}` with no PII, returns `list[int]`; `POST /api/v1/directorio/purga` admin-only; CLI reports ids. |
| DIR-008 guardia solo seed | ✅ Implemented | `verificar_entorno_seed` called before any session/transaction; `ENTORNOS_PERMITIDOS_SEED={development,local,test}`. `app/routes/directorio.py` and `app/services/directorio_service.py` contain no `environment`/`get_settings` reference (asserted by test). |
| DIR-009 evidencia | ✅ Implemented | Settings has no `*blind*`; `Empleado.__table__` has no `hash`/`blind` columns; seed emails end in `.test`. |
| VIS-001 rol `mesa_de_ayuda` | ✅ Implemented | `RolEmpleado` + CHECK four values; `alcance_desde_empleado` maps `mesa_de_ayuda -> REVISION`; `permite_incidente(REVISION) = sector_id is None or requiere_revision_humana`; used in `get_incidente`, `list_incidentes` (`solo_revision` + per-incident final filter), and classification endpoints via `_verificar_alcance_incidente`. |
| VIS-002 cola acotada | ✅ Implemented | `list_pending_review(alcance)` returns `[]` for VACIO, filters by incident sector for SECTOR, whole queue for GLOBAL/REVISION; repo preserves FIFO (`created_at.asc()`) and pending definition (`requiere_revision_humana == True AND sector_id_validado IS NULL`). |
| Cross-section gap `mesa_de_ayuda` sector-less | ✅ Fixed & implemented | `_validar_sector_por_rol` uses `_ROLES_CON_SECTOR=(usuario_final, operador)`; `administrador_directorio`/`mesa_de_ayuda` reject non-null sector, return None. Verified service + API. |
| Migration chain 009→010→011→012 | ✅ Verified | `012 down_revision="011"`; `011 down_revision="010"`; `010 down_revision="009"`. No multi-head. `batch_alter_table` portable. |
| `alembic downgrade -1` restores 3-value CHECK | ✅ Verified | `test_downgrade_restaura_check_de_tres_valores`: downgrade then insert `mesa_de_ayuda` raises `IntegrityError`; re-upgrade accepts again. |
| Layer discipline | ✅ | routes → services → repositories → models preserved; no layer skipped. `selectinload` used for serialized relationships (`list_pending_review` eager-loads incidente). |
| No `directory_blind_index_key` / hash column | ✅ Verified | 0 matches in `app/`, `alembic/`, `scripts/`; only descriptive/doc mentions elsewhere. |
| Contacts synthetic (no real PII) | ✅ | Seed persons use `@example.test`; all fixtures use synthetic emails. |
| No cron/scheduler/worker for purge | ✅ | AST scan finds no scheduler libs; `purgar_vencidos` referenced only in service, route, CLI. |

---

## Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1 rol `mesa_de_ayuda` sin sector + migracion 012 append-only | ✅ Yes | Enum + CHECK four values; migration `012 down_revision="011"`. |
| D2 visibilidad por rol (admin global / mesa sin-sector-o-revision / sector-bound / vacio) | ✅ Yes | `alcance_desde_empleado` + `permite_incidente`; tested for all four modes. |
| D3 `AlcanceIncidentes` con modos y `permite_incidente`, conserva `permite_sector` | ✅ Yes | `ModoAlcance.{GLOBAL,SECTOR,REVISION,VACIO}`; `permite_sector` retained; call sites use `permite_incidente`. |
| D4 `revision-pendiente` acotada reutilizando `get_alcance_incidentes` | ✅ Yes | Route injects `AlcanceIncidentes`; service branches on mode; repo optional `sector_id` filter; FIFO preserved. |
| D5 purga manual por operador, sin cron, con ids | ✅ Yes | `POST /purga` admin-only + CLI; ids audited; idempotent; no scheduler. |
| D6 guardia de entorno SOLO en el seed | ✅ Yes | Guard in seed entry before DB access; runtime ungated (asserted). |
| D7 evidencia de cierre 7.5 | ✅ Yes | `docs/directorio-evidencia-cumplimiento.md` + tests; approval explicitly pending. |
| D8 migracion 012 | ✅ Yes | As specified; downgrade restores 3 values. |
| D9 estrategia de tests | ✅ Yes | Unit/API offline + PG integration + inspection tests. |
| D10 governance HIGH | ✅ Yes | No real data; approval pending registered. |
| OQ1–OQ4 resolved as declared | ✅ Yes | OQ1 no sector; OQ2 `sector_id IS NULL OR requiere_revision_humana=true`; OQ3 retention/ARCO; OQ4 `development/local/test`. |

---

## Issues Found

**CRITICAL** (must fix before archive):
- None. No failing test, no build/lint/validate failure, no functional gap.

**WARNING** (should fix):
1. **Task 7.4 — external human HIGH approval OUTSTANDING.** The registration deliverable is done (documented in `docs/directorio-evidencia-cumplimiento.md` §4 and `tasks.md` 7.4), and the scenario is now COMPLIANT, but the actual approval to activate real data is NOT granted. Real data remains blocked. This is a HIGH-governance human gate, not a code defect; it cannot be closed by any test or code change. Surfaced for the orchestrator/author. Not treated as a CRITICAL archive gate (the implementation is synthetic-data only).
2. **Coverage tool under-reports ASGI-exercised paths** in this environment (`clasificacion_service.py` raw 62%, `routes/directorio.py` 72%). Proven to be a measurement artifact via a runtime call-count probe (validate 4×, list_by_incidente 4×). Raw per-file percentages for API-only code paths should not be read as real coverage gaps.

**Closed since the prior verification** (previously WARNING):
- VIS-001 scenario 8 "Mesa de ayuda lee clasificaciones de un incidente en revision" — CLOSED. New endpoint test `test_mesa_de_ayuda_lee_en_revision_y_no_plain_404` executes the real ASGI app as a `mesa_de_ayuda` user (revision → 200, plain sector → 404) and passes.
- DIR-009 scenario 3 "Datos reales bloqueados hasta la aprobacion" — CLOSED. New inspection tests `test_evidencia_registra_aprobacion_high_pendiente_y_datos_reales_bloqueados` and `test_no_existe_un_toggle_de_activacion_de_datos_reales` pass.
- `CHANGES.md` line 1566 stale migration note — CLOSED. Now reads "La 012 (rol `mesa_de_ayuda`) la introduce c-60 (aplicado 2026-10-06)".

**SUGGESTION** (nice to have):
1. Persist a standalone `TDD Cycle Evidence` table in the change directory for the non-PART-G batches (currently only in Engram + inline in tasks.md), to ease future audits.

---

## Verdict

**PASS WITH WARNINGS**

The implementation is structurally coherent with design D1–D10, functionally complete (33/33 tasks), and behaviorally verified: offline suite 991 passed / 0 failed, PostgreSQL integration 39 passed / 0 failed, ruff clean, OpenAPI in sync, and `openspec validate --strict` passes. The delta specs are matched by **33/33 executed-and-passing scenario tests** (up from 31/33; the 2 previously-PARTIAL scenarios are closed by new passing tests). The cross-section gap (`mesa_de_ayuda` sector-less in `_validar_sector_por_rol`) is closed and proven end-to-end at both service and API layers (creatable without sector → 201; rejected with sector → 422). The migration chain 009→010→011→012 is linear and `alembic downgrade -1` is proven to restore the 3-value CHECK. No cross-sector leak is possible through REVISION: `mesa_de_ayuda` only receives `sector_id IS NULL` or `requiere_revision_humana` incidents, and plain sector incidents respond 404. Purge is manual-only with no scheduler and audits internal ids without PII.

No implementation warning remains: all scenario tests pass and no functional defect was found. The two residuals are non-blocking and external: (1) the outstanding HIGH human approval (task 7.4) keeps real data blocked — a governance gate, not a code issue; (2) the coverage tool under-reports ASGI-exercised API paths (measurement artifact). Because an open governance item remains surfaced, the verdict stays PASS WITH WARNINGS rather than a clean PASS.

Recommended next action: archive the change (the synthetic-data implementation is verified 33/33). The 7.4 approval remains an external gate for enabling real data only, not for archiving this implementation.
