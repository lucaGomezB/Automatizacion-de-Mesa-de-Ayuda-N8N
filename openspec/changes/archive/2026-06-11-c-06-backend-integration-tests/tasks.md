## 1. Preparación de infraestructura

- [x] 1.1 Agregar `pytest-cov` a la sección Development/Testing de `Gestion_Incidentes/requirements.txt` e instalarlo en el entorno.
- [x] 1.2 Capturar el baseline de la suite existente: ejecutar `pytest` desde `Gestion_Incidentes/` y registrar el conteo (~134 passed). Ningún test existente debe romperse al finalizar C-06.
- [x] 1.3 Agregar a `tests/conftest.py` la fixture `seed_catalogs` que siembra (vía el `engine` compartido, con commit) el `Estado` "nuevo", los tres `Sector` (`Sistemas`, `Operaciones`, `Soporte Técnico`) y los `CanalOrigen` del dominio, garantizando aislamiento entre tests (limpieza al finalizar o conteos relativos).
- [x] 1.4 Agregar a `tests/conftest.py` un helper/fixture para inyectar un clasificador doble vía `app.dependency_overrides[get_service]`, de modo que el `IncidenteService` use la sesión de la request y un `AsyncMock.classify` que devuelva un `ClasificacionResult` parametrizable.
- [x] 1.5 Agregar a `tests/conftest.py` una fixture (autouse acotada a los módulos de incidentes) que neutralice `notify_n8n` con `patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock)` y drene el loop con `await asyncio.sleep(0)`.

## 2. Tests de integración — POST /api/v1/incidentes (creación + clasificación)

- [x] 2.1 RED: escribir `test_api_incidentes.py::test_post_incidente_creacion_exitosa_201` — payload válido + clasificador doble (Sistemas, 0.95, sin revisión) → 201, contrato `IncidenteRead`, sector "Sistemas", `estado.nombre` "nuevo".
- [x] 2.2 GREEN: ejecutar el test contra el código de producción existente; confirmar que pasa.
- [x] 2.3 TRIANGULATE: `test_post_incidente_baja_confianza_marca_revision` — clasificador doble con confianza < 0.70 y `requiere_revision_humana` true → 201 con `requiere_revision_humana` true.
- [x] 2.4 TRIANGULATE (borde): `test_post_incidente_descripcion_invalida_422` — descripción vacía / solo espacios / bajo el mínimo → 422 y ningún incidente persistido.

## 3. Tests de integración — GET /api/v1/incidentes (listado, filtros, paginación)

- [x] 3.1 RED: `test_get_incidentes_lista_sin_filtros_200` — varios incidentes creados → 200, todos presentes, orden por fecha descendente, contrato `IncidenteListItem`.
- [x] 3.2 GREEN: ejecutar y confirmar verde.
- [x] 3.3 TRIANGULATE: `test_get_incidentes_filtro_por_sector` — filtrar por `sector_id` devuelve solo coincidentes.
- [x] 3.4 TRIANGULATE: `test_get_incidentes_filtro_por_revision_humana` — filtrar por `requiere_revision_humana=true` devuelve solo los pendientes.
- [x] 3.5 TRIANGULATE: `test_get_incidentes_paginacion_limit_offset` — con conjunto mayor que `limit`, la respuesta trae a lo sumo `limit` elementos omitiendo `offset`.

## 4. Tests de integración — GET /api/v1/incidentes/{id} (detalle + 404)

- [x] 4.1 RED: `test_get_incidente_detalle_existente_200` — incidente creado → 200, contrato `IncidenteRead` con `descripcion_pseudonimizada` y objetos de catálogo relacionados.
- [x] 4.2 GREEN: ejecutar y confirmar verde.
- [x] 4.3 TRIANGULATE: `test_get_incidente_inexistente_404` — id inexistente → 404 con cuerpo `{"error": {"code": "NOT_FOUND", ...}}`.

## 5. Tests de integración — PATCH /api/v1/incidentes/{id} (actualización parcial + 404)

- [x] 5.1 RED: `test_patch_incidente_actualiza_solo_campos_enviados_200` — PATCH que solo cambia `prioridad` → 200, prioridad actualizada, resto sin cambios.
- [x] 5.2 GREEN: ejecutar y confirmar verde.
- [x] 5.3 TRIANGULATE: `test_patch_incidente_inexistente_404` — PATCH sobre id inexistente → 404 con cuerpo de error estructurado.

## 6. Tests de integración — GET /api/v1/clasificaciones/revision-pendiente (cola FIFO)

- [x] 6.1 RED: `test_api_clasificaciones.py::test_get_revision_pendiente_solo_pendientes` — mezcla de registros (pendiente sin validar, alta confianza, ya validado) → la cola contiene solo los pendientes sin validar.
- [x] 6.2 GREEN: ejecutar y confirmar verde.
- [x] 6.3 TRIANGULATE: `test_get_revision_pendiente_orden_fifo` — múltiples pendientes en distintos momentos → orden del más antiguo al más reciente.
- [x] 6.4 TRIANGULATE: `test_get_revision_pendiente_paginacion` — `limit`/`offset` acotan la cola.

## 7. Tests de integración — PATCH /api/v1/clasificaciones/{id}/validar (validación humana)

- [x] 7.1 RED: `test_patch_validar_retira_de_la_cola_200` — operador valida un pendiente con sector existente → 200 con `sector_validado` asignado, y el registro deja de aparecer en la cola.
- [x] 7.2 GREEN: ejecutar y confirmar verde.
- [x] 7.3 TRIANGULATE: `test_patch_validar_correccion_difiere_del_predicho` — sector validado distinto del predicho → 200 y se registra la corrección.
- [x] 7.4 TRIANGULATE: `test_patch_validar_log_inexistente_404` — `log_id` inexistente → 404.
- [x] 7.5 TRIANGULATE: `test_patch_validar_sector_inexistente_404` — `sector_id_validado` inexistente → 404 y el registro no queda validado.

## 8. Tests de integración — GET /api/v1/health (health check)

- [x] 8.1 RED: `test_api_health.py::test_get_health_liveness_200` — `GET /api/v1/health` → 200 con `status` "ok" y la versión de la app.
- [x] 8.2 GREEN: ejecutar y confirmar verde.
- [x] 8.3 TRIANGULATE: `test_get_health_db_readiness_200` — `GET /api/v1/health/db` con la base de test disponible → 200 indicando base alcanzable.

## 9. Cobertura y cierre

- [x] 9.1 Ejecutar `pytest --cov=app.routes --cov=app.services --cov=app.repositories --cov-report=term-missing` desde `Gestion_Incidentes/` y registrar la cobertura por módulo.
- [x] 9.2 Iterar sobre las líneas faltantes hasta superar el 85% en `routes/`, `services/` y `repositories/`; documentar cualquier rama no alcanzable vía HTTP y decidir si amerita un test directo de repositorio.
- [x] 9.3 Ejecutar la suite completa (`pytest`) y confirmar que los ~134 tests previos siguen verdes junto con los nuevos (REFACTOR: limpiar duplicación en fixtures/helpers manteniendo todo en verde).
- [x] 9.4 Verificar el aislamiento: la suite pasa al ejecutarse completa y también por módulo individual, sin filtrado de estado entre tests.
