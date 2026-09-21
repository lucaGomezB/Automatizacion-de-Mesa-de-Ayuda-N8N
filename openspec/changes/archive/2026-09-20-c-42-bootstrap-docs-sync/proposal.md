## Why

Los changes de Fase 1 (c-39/c-40/c-41) cambiaron el bootstrap local: el preflight de entorno ahora exige `JWT_SECRET_KEY` y los scripts de arranque ejecutan un gate de costo con bypass explicito (`UP_SKIP_COST_PREFLIGHT=1`). La documentacion operativa no acompanó ese cambio y quedo desincronizada de las specs vivas.

## What Changes

- **README — seccion "Despliegue local"**: documentar `JWT_SECRET_KEY` entre las variables cuyo placeholder o ausencia hacen fallar el comando unico, y mencionar el gate de preflight de costo junto con su bypass audible `UP_SKIP_COST_PREFLIGHT=1`.
- **`docs/operational-guide.md` — seccion 1.3**: presentar el comando unico (`bash scripts/up.sh` / `make up` / `.\scripts\up.ps1`) como camino recomendado, documentar el gate de costo y su bypass, manteniendo el camino manual (`openssl/generate-certs.*` + `docker compose up -d`) como alternativa.
- Change atómico, documentación únicamente: sin tocar código de producción, scripts ni `n8n/workflow.json`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `project-documentation`: el requisito "README de despliegue local reproducible" suma `JWT_SECRET_KEY` y el gate de costo con bypass; el requisito "Anexo G — Guía operativa" exige presentar el comando unico como camino recomendado y documentar el gate y su bypass.

## Impact

| Área | Impacto | Descripción |
|------|---------|-------------|
| `README.md` (líneas 37-66) | Modified | Fallo del comando incluye `JWT_SECRET_KEY`; se agrega gate de costo y bypass |
| `docs/operational-guide.md` (sección 1.3, líneas 66-115) | Modified | Comando unico como camino recomendado; gate de costo documentado; manual preservado |
| `App/Backend/tests/` (nuevo test estructural) | Modified | Assertions sobre contenido de README y guía (patrón `test_n8n_workflow.py`) |

Sin cambios en API, esquema de datos, dependencias ni infraestructura.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| El test estructural sobre docs acopla la suite backend a texto de prosa | Med | Asserts solo sobre tokens estables (`JWT_SECRET_KEY`, `UP_SKIP_COST_PREFLIGHT`, `scripts/up.sh`) |
| Duplicar el gate en README y guía con redacciones divergentes | Low | La guía es fuente; el README enlaza y resume |

## Rollback Plan

Revertir el commit de docs y eliminar el test estructural. Ningún artefacto de runtime se ve afectado, por lo que no hay estado que restaurar.

## Success Criteria

- [ ] `README.md` nombra `JWT_SECRET_KEY` entre las condiciones de fallo y menciona `UP_SKIP_COST_PREFLIGHT=1`.
- [ ] `docs/operational-guide.md` presenta el comando unico como camino recomendado y documenta el gate y el bypass.
- [ ] El camino manual sigue documentado en ambos archivos.
- [ ] `openspec validate --strict --changes c-42-bootstrap-docs-sync` pasa.