# Checkpoint 2.1 de c-165: migración de auditoría e intervención humana

Fecha: 2026-10-30. Rama: `change/campana-medicion-c-165-a-c-168`. Gobernanza ALTA: este documento describe lo que c-165 va a hacer sobre el esquema de `clasificacion_log` y sobre el backend, y se detiene acá hasta la confirmación humana (Gonzalo y Lucas). Nada de lo que sigue está aplicado. Lo que sí está aplicado y commiteado es el grupo 1 (instrumento del brazo manual, solo `evaluation/`), que no toca el backend.

Rutas relativas a `App/Backend/` salvo indicación.

## 1. Columnas nuevas en `clasificacion_log`

Estado actual del modelo (`app/models/clasificacion_log.py`): diez columnas (`id`, `incidente_id`, `sector_id_predicho`, `confianza`, `etapa`, `requiere_revision_humana`, `respuesta_raw`, `sector_id_validado`, `created_at`, `updated_at`) y las relaciones `sector_validado`, `sectores_predichos` y `sectores_validados`. Hay que agregar `DateTime` al import de SQLAlchemy y `from datetime import datetime`.

Columnas nuevas, todas nullable, sin default y sin backfill, ubicadas después de `sector_validado`:

| Columna | SQLAlchemy | SQL PostgreSQL | FK / índice |
|---|---|---|---|
| `validado_por_empleado_id` | `Integer`, `ForeignKey("directorio_empleado.id", ondelete="SET NULL", name="fk_clasificacion_log_validado_por_directorio_empleado")`, `index=True` | `INTEGER` | FK nombrada con `ON DELETE SET NULL`; índice `ix_clasificacion_log_validado_por_empleado_id` |
| `intervencion_inicio_en` | `DateTime(timezone=True)` | `TIMESTAMP WITH TIME ZONE` | no |
| `validado_en` | `DateTime(timezone=True)` | `TIMESTAMP WITH TIME ZONE` | no |
| `origen_intervencion` | `String(20)` | `VARCHAR(20)` | sin CHECK; el vocabulario (`gate`, `muestreo`, `rederivacion`, `completado_manual`) se valida en la capa de aplicación |

Notas: `Base` no define `naming_convention` (`app/core/database.py:57`), así que `index=True` produce ese nombre. El precedente `Incidente.deleted_by` nombra la FK solo en la migración; acá se nombra igual en el modelo y en la migración. Con `SET NULL`, la purga de empleados por retención (DIR-007) deja el actor en NULL sin tocar el log. `ClasificacionLogRead` expondrá solo el id del empleado.

## 2. Migración `024_clasificacion_log_intervencion.py`

- `revision = "024"`, `down_revision = "023"`. La cadena 001..023 es lineal; el head actual es `023`.
- Misma forma que `alembic/versions/019_soft_delete_incidente.py` (upgrade :35-53, downgrade :56-61): `batch_alter_table("clasificacion_log")` con cuatro `add_column` (FK con `name=` explícito) y luego `op.create_index`; downgrade con `op.drop_index` y cuatro `drop_column`.
- DDL de PostgreSQL verificado por render en modo `as_sql`:

```sql
ALTER TABLE clasificacion_log ADD COLUMN validado_por_empleado_id INTEGER;
ALTER TABLE clasificacion_log ADD CONSTRAINT fk_clasificacion_log_validado_por_directorio_empleado
  FOREIGN KEY(validado_por_empleado_id) REFERENCES directorio_empleado (id) ON DELETE SET NULL;
ALTER TABLE clasificacion_log ADD COLUMN intervencion_inicio_en TIMESTAMP WITH TIME ZONE;
ALTER TABLE clasificacion_log ADD COLUMN validado_en TIMESTAMP WITH TIME ZONE;
ALTER TABLE clasificacion_log ADD COLUMN origen_intervencion VARCHAR(20);
CREATE INDEX ix_clasificacion_log_validado_por_empleado_id ON clasificacion_log (validado_por_empleado_id);
-- downgrade: DROP INDEX y DROP COLUMN de las cuatro, en orden inverso
```

- Nombres dentro del límite de 63 bytes de PostgreSQL (FK 53, índice 45). En PG 15 las columnas nullable sin default son solo metadata; el `ADD CONSTRAINT` valida una columna toda NULL con un lock breve.
- SQLite: simulado fuera del repo sobre las migraciones 001..023 con filas de prueba; el upgrade deja catorce columnas, FK e índices correctos y filas intactas; el downgrade recrea la tabla (copy-and-move, como 019) y vuelve a las diez columnas. Con `PRAGMA foreign_keys=ON` y filas huérfanas el copy-and-move falla; en PostgreSQL no ocurre y en los tests las FKs están apagadas.
- Pruebas (tarea 2.2): patrón de `tests/test_migration_019_soft_delete_incidente.py` y `tests/test_migration_023_directorio_auditoria.py`: `upgrade head` sobre SQLite temporal con `PRAGMA table_info`, `foreign_key_list` e `index_list`; `downgrade 023`; cadena `get_revision("024").down_revision == "023"`; fila insertada tras `upgrade 023` y verificada tras `upgrade 024`; en PostgreSQL, el `SET NULL` real al borrar el empleado (sobre el esquema de `create_all`, ver pregunta 3).

## 3. Tests existentes afectados

- `tests/test_migration_023_directorio_auditoria.py:145` asserta `get_current_head() == "023"`: pasa a `"024"`. Es el único test que fija el head.
- `docs/openapi.json` y `tests/test_openapi_sync.py`: el JSON incluye `ClasificacionLogRead`, `ClasificacionValidar` y `ResumenResponse`; el sync se rompe desde las tareas 2.3 y 2.4, no recién en 3.3/3.4. Decisión: regenerar `docs/openapi.json` en 2.3/2.4 y de nuevo en 3.3/3.4.
- Tests que ejercitan `/validar` o `validate()`: trece (`test_api_clasificaciones.py` 4, `test_api_validar_cascade.py` 2, `test_clasificacion_visibility.py` 5, `test_validation_error_sanitization.py` 2) más dos llamadas posicionales a `service.validate(...)` en `test_c86_notificacion_post_revision.py:135,160`. Los parámetros nuevos deben ser opcionales y por nombre.
- Sin impacto: ningún test fija el conjunto exacto de claves de `ClasificacionLogRead` ni de `ResumenResponse`; los de estadísticas solo comprueban `"tasa_revision_humana" in body`.
- Fixtures que quedarán como legados (log con `sector_id_validado` y sin `validado_en`): `tests/test_revision_pendiente_count.py:105` y `tests/integration/test_revision_count_postgres.py:74`. Solo prueban la cola pendiente.

## 4. Escritor de `rederivacion`

- Detección en `IncidenteService.update_incidente` (`app/services/incidente_service.py:495-553`): la comparación `payload.sector_id is not None and payload.sector_id != incidente.sector_id` va entre la validación del sector (:544-549) y `update_fields` (:551-553). Un incidente cerrado ya falla antes (:529-530). El servicio ya tiene `self._clasificacion_repo` (:118). La ruta (`app/routes/incidentes.py:396-434`) suma `empleado: EmpleadoDep` y pasa `actor_empleado_id`, como `soft_delete_incidente` (:555-561).
- Log destino: el de mayor `id` del incidente (método nuevo en el repositorio; `list_by_incidente` hoy ordena por `created_at desc`). Sin log, el PATCH responde igual que hoy.
- Campos: `sector_id_validado = payload.sector_id`, `validado_en = utcnow()`, `origen_intervencion = "rederivacion"`, `validado_por_empleado_id = empleado.id` o NULL, `intervencion_inicio_en = NULL`. No toca `requiere_revision_humana` del log.
- `validate()` no dispara este escritor: propaga por `IncidenteRepository.update_fields`.
- Riesgo: si el log estaba pendiente, la rederivación lo saca de la cola (`list_pending_review` filtra `requiere_revision_humana = True AND sector_id_validado IS NULL`) y baja el contador, mientras `Incidente.requiere_revision_humana` queda en True salvo que el mismo PATCH lo limpie. Quedan dos vistas distintas (cola por log; lista y `tasa_revision_humana` por incidente). Una rederivación posterior a un `gate` pisa el origen anterior (declarado en D2).
- Decisión propuesta (opción A del design D3): registrar la rederivación como está descripto, documentar y testear la divergencia entre cola y flag del incidente. `sectores_validados` no se vacía; solo se retira el nuevo principal si figuraba entre los adicionales.

## 5. Actor nullable

- `EmpleadoDep` vive en `app/routes/incidentes.py:101-116` y resuelve el empleado activo de la cuenta. `app/routes/clasificaciones.py:30` ya importa de ese módulo, así que importar `EmpleadoDep` no crea ciclos. La ruta de validación recibe `empleado: EmpleadoDep` y llama `validate_payload(..., actor_empleado_id=empleado.id if empleado else None)`; `intervencion_inicio_en` viaja en el payload.
- Tests con `User(id=1)`: `tests/conftest.py:594-598` solo sobreescribe `get_current_user` y `get_alcance_incidentes`; `get_empleado_actual` devuelve `None`, por lo que validar responde 200 con actor NULL. Afectados reales: los trece tests de `/validar`, no los 48 archivos que usan `client`. Patrón para "con empleado vinculado": `tests/test_c90_prioridad_critica_api.py:49-128`.
- Gotcha para 2.5 y el export: SQLite descarta la zona de `DateTime(timezone=True)` (`10:00-03:00` se lee como `10:00` ingenuo). Normalizar `intervencion_inicio_en` a UTC antes de persistir, o `duracion_s` queda desfasada en el subset SQLite.

## 6. Datos legados

Los seeds (001, 004, `scripts/seed_directorio.py`) no cargan logs validados y no hay dumps en `backups/`, así que las filas legadas existen solo en bases desplegadas. Para dimensionarlas antes de la 024:

```sql
SELECT count(*) FILTER (WHERE sector_id_validado IS NOT NULL) AS legadas, count(*) AS total FROM clasificacion_log;
```

Tratamiento: estado derivado `intervencion_legada_sin_metadatos` (`sector_id_validado IS NOT NULL AND validado_en IS NULL`), sin columna nueva ni backfill; la métrica los quita del numerador y del denominador y devuelve `intervenciones_legadas_excluidas`; el export no los emite y los cuenta en el resumen. Los logs de la campaña son posteriores a la 024, así que sus legados son cero por construcción.

## 7. Archivos que se tocan en los grupos 2, 3 y 4

Backend: `alembic/versions/024_clasificacion_log_intervencion.py` y `tests/test_migration_024_*.py` (nuevos), `tests/test_migration_023_directorio_auditoria.py` (2.2); `app/models/clasificacion_log.py` y `app/schemas/clasificacion.py` (2.3, 2.4); `app/repositories/clasificacion_repository.py` y `app/services/clasificacion_service.py` (2.5, 2.7, 2.8); `app/routes/clasificaciones.py` (2.6); `app/routes/incidentes.py` y `app/services/incidente_service.py` (2.8); `app/constants.py` con `ORIGENES_INTERVENCION` y un módulo nuevo `app/services/intervencion_estado.py` con la función pura de estado y los predicados SQL (2.9; no figuraba en el Impact, se aprueba acá); `app/repositories/estadisticas_repository.py`, `app/services/estadisticas_service.py`, `app/schemas/estadisticas.py` (3.x); `scripts/exportar_intervenciones.py` y su test (4.x). No se toca `app/routes/estadisticas.py`.

Frontend (2.11): `pages/Administracion/ValidarClasificacionDialog.tsx` (captura del inicio al abrir, envío en `handleValidar`), su test, y `types/clasificacion.ts`. `services/clasificacionesService.ts` no cambia.

Fuera de `App/`: `docs/openapi.json`, `docs/anexo_c_esquema_bd.md`, `CHANGES.md`, `evaluation/data/campana/README.md` y el runbook del brazo manual.

Rollback: primero revertir el código de aplicación (el código previo ignora columnas extra), después `alembic downgrade 023`, que retira índice, FK y columnas sin tocar filas. Nunca bajar el esquema antes de revertir el código.

## 8. Decisiones tomadas por el orquestador (reversibles) y pendientes humanos

Tomadas:
- Rederivación: opción A (registrar y documentar la divergencia con la cola).
- `docs/openapi.json` se regenera en cada tarea que cambia un schema.
- Test PG de la FK sobre el esquema de `create_all`, más test SQLite de la migración y render del DDL; sin `alembic upgrade` real contra PG.
- Vocabulario en `app/constants.py` y módulo nuevo `app/services/intervencion_estado.py`.
- Sin CHECK en `origen_intervencion`.
- `test_migration_023:145` pasa al literal `"024"`, siguiendo el patrón existente.
- Clave HMAC de `actor_alias`: variable de entorno propia `INTERVENCION_EXPORT_HMAC_KEY`, leída por el script de export con `os.environ`, con error explícito si falta; sin tocar `Settings`, `.env.example` ni el CI.
- Posición planeada del brazo manual (grupo 1): orden de turnos que indica el runbook de c-166 (mitad, turno 1 con `brazo_primero = manual`, luego turno 2, cada turno por `posicion`), restringido a los casos del operador; c-167 usa la posición real como covariable e informa los desvíos.

Pendientes de confirmación humana:
1. Aprobar la migración 024, las cuatro columnas y el escritor de rederivación tal como se describen, para seguir con los grupos 2 a 6.
2. Autorizar la medición de las líneas base que faltan en la máquina local: subset PostgreSQL (`docker compose up -d postgres` en 127.0.0.1:5433, monta el volumen de desarrollo) y Vitest del diálogo (`npm ci` en `App/Frontend`, descarga paquetes). Si no, las corre Gonzalo y pasa los conteos.

## 9. Línea base registrada (tarea 0.1, 2026-10-30)

- `evaluation/`: 841 passed, 1 skipped antes del grupo 1; 884 passed, 1 skipped después.
- Backend subset SQLite (`pytest -m "not integration"`): 1582 passed, 3 failed preexistentes, 60 deselected, 1 xfailed. Las tres fallas son `test_001_seed_catalogs_no_fue_modificado` en `test_migration_006_timing.py`, `test_migration_origen_message_id.py` y `test_migration_sectores.py`: con `core.autocrlf=true` el archivo `001_seed_catalogs.py` está en CRLF en disco y su hash difiere del esperado (blob LF). No son del repo y no se corrigen en c-165.
- `tests/test_openapi_sync.py`: 5 passed (fastapi 0.162.0, pydantic 2.14.2).
- Subset PostgreSQL y Vitest: no medidos (ver pendiente 2).
