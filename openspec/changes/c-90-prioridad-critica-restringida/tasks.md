## 1. Registro de política de rol (RP-006)

- [ ] 1.1 Safety net: ejecutar `cd App/Backend; pytest -m "not integration" -k "role_policy or politica_de_rol or directorio"` y registrar el baseline de tests verdes antes de tocar el registro.
- [ ] 1.2 RED: escribir un test que falle y exija `puede_asignar_prioridad_critica` verdadero para `mesa_de_ayuda` y `administrador_directorio`, y falso para `usuario_final`, y que exista el helper derivado; verificar que falla por atributo/héper inexistente.
- [ ] 1.3 GREEN: agregar el atributo `puede_asignar_prioridad_critica` a `PoliticaRol` en `App/Backend/app/services/role_policy.py`, fijar sus valores por rol y exponer el/los helper(s) derivados; verificar que el test de 1.2 pasa.
- [ ] 1.4 TRIANGULATE: agregar casos con rol `None`/desconocido y verificar que el helper deniega por defecto y que `ROLE_POLICY` sigue coherente con el enum (RP-003 sin romperse).

## 2. Guard de prioridad crítica en las rutas de incidentes (RP-006)

- [ ] 2.1 Safety net: ejecutar `cd App/Backend; pytest tests/test_api_incidentes.py -m "not integration"` y registrar el baseline de tests verdes.
- [ ] 2.2 RED: escribir tests que fallen para `POST /api/v1/incidentes` y `PATCH /api/v1/incidentes/{id}`: (a) `mesa_de_ayuda` o `administrador_directorio` con `critica` es aceptado; (b) rol sin permiso con `critica` recibe 403 y no persiste; (c) rol sin permiso con `baja|media|alta` es aceptado; (d) PATCH sin tocar `prioridad` sobre un incidente ya `critica` es aceptado; verificar que fallan con el estado actual.
- [ ] 2.3 GREEN: implementar en `App/Backend/app/routes/incidentes.py` un guard que resuelva el empleado/rol del `current_user`, consulte `politica_de_rol` y lance `HTTPException(403)` cuando el payload pida `critica` sin permiso, aplicado en `create_incidente` y `update_incidente`; verificar que los tests de 2.2 pasan.
- [ ] 2.4 TRIANGULATE: agregar el caso de llamante no interactivo sin permiso que envía `critica` (403) y confirmar que el alta con prioridad no crítica permanece inalterada; verificar que el 403 usa el envelope `FORBIDDEN` de `core/error_handlers.py`.
- [ ] 2.5 Si el proyecto lo requiere para este camino, agregar un test `@pytest.mark.integration` que confirme el 403 denegado por defecto para una cuenta sin empleado vinculado; verificar que pasa contra la base descartable.

## 3. Frontend: asignación y visual de prioridad (FR-RBAC-009)

- [ ] 3.1 Safety net: ejecutar `cd App/Frontend; npm run test -- Administracion ReportarIncidente` y registrar el baseline de tests verdes.
- [ ] 3.2 RED: escribir tests que fallen para: control de prioridad visible/habilitado solo para los roles con permiso (`mesa_de_ayuda` y `administrador_directorio`); opción `critica` ofrecida únicamente a esos roles; `formatearPrioridad('critica')` y el badge de `critica` distinguibles en `TicketsTable`/`MisIncidentes`/`DetalleIncidente`; y regresión de que `IncidenteForm` NO ofrece `critica`.
- [ ] 3.3 GREEN: implementar el control editable de prioridad en `TicketDetailDialog`/`DetalleIncidente` condicionado al rol autenticado (FR-RBAC-001) y actualizar `TicketsTable.tsx`, `MisIncidentes/index.tsx`, `DetalleIncidente.tsx`, `src/utils/formatters.ts` y `src/types/incidente.ts` para mapear `critica`; verificar que los tests de 3.2 pasan.
- [ ] 3.4 TRIANGULATE: agregar el caso de respuesta 403 del backend en la asignación y verificar que la UI lo maneja sin exponer el recurso (FR-RBAC-005).

## 4. Contrato, verificación y cierre

- [ ] 4.1 Si el contrato HTTP cambió (respuesta 403 documentada), regenerar `docs/openapi.json` con `cd App/Backend; python scripts/export_openapi.py` y verificar `cd App/Backend; pytest tests/test_openapi_sync.py -v`.
- [ ] 4.2 Verificar `cd App/Backend; ruff check .` sin hallazgos nuevos y la suite SQLite `pytest -m "not integration"` verde (sin regresiones).
- [ ] 4.3 Verificar la suite frontend `cd App/Frontend; npm run test` y `npm run lint` verdes.
- [ ] 4.4 Ejecutar `openspec validate c-90-prioridad-critica-restringida --strict` y confirmar que el change sigue válido.
