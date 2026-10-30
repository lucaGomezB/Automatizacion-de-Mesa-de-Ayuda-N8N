# Design: Instrumentar la campana (brazo manual e intervencion)

## Context

Ver `proposal.md` - Why. Estado real del codigo (cotejado antes de enmendar):

- El unico flujo que escribe la validacion humana es `PATCH /clasificaciones/{log_id}/validar` (`app/routes/clasificaciones.py`), que delega en `ClasificacionService.validate_payload` / `validate` (`app/services/clasificacion_service.py:215-315`). `validate` llama a `ClasificacionRepository.set_validated_sector` (`app/repositories/clasificacion_repository.py:209-259`) y propaga el sector al incidente con `IncidenteRepository.update_fields` (NO pasa por `IncidenteService`).
- El route de validacion solo tiene `current_user: User`; el empleado se resuelve con `get_empleado_actual` / `EmpleadoDep` (`app/routes/incidentes.py:101-116`), que devuelve `None` si la cuenta no tiene empleado ACTIVO vinculado. El fixture de tests (`tests/conftest.py:595-598`) inyecta `User(id=1)` sin empleado y lo usan unos 50 tests.
- La reasignacion de sector va por `PATCH /incidentes/{id}` (`IncidenteUpdate.sector_id`, `app/schemas/incidente.py:277`) -> `IncidenteService.update_incidente`, y hoy NO toca el log.
- La cola de revision (`list_pending_review`) lista solo logs con `requiere_revision_humana = True` y `sector_id_validado IS NULL`; no hay superficie de UI para validar un log no marcado.
- `validate` solo reemplaza `sectores_validados` si llega una lista NO vacia: una re-validacion sin adicionales conserva el conjunto viejo (defecto a corregir).
- `tasa_revision_humana` (`estadisticas_repository.py:235-252`) cuenta `Incidente.requiere_revision_humana = True` por `Incidente.created_at`; como `validate()` pone ese flag en `False`, la metrica mide PENDIENTES al momento de la consulta, no casos marcados ni intervenciones. La premisa del design original ("cuenta casos MARCADOS") era erronea.
- La tabla de empleados es `directorio_empleado` (`app/models/empleado.py:99`), con borrado fisico por retencion (DIR-007): una FK hacia ella debe ser `ON DELETE SET NULL`.
- El corpus (`data/corpus_evaluacion_pseudonimizado.json`) identifica el caso por `id` (`R001..R200`) y provee `sector_asignado` (consenso original) y `tiempo_manual_s`, pero no la clasificacion del operador manual.

## Goals / Non-Goals

- **Goals**: instrumento del brazo manual sobre la planilla unica de c-168; metadatos de intervencion persistidos en el log con escritores declarados; metrica backend de intervencion con cohorte definida; export pseudonimizado para c-167; runbook de campana.
- **Non-Goals (design-level)**: ejecutar la campana; UI de etiquetado; historial append-only de multiples intervenciones por log; un flujo de `completado_manual`; una superficie de UI para muestreo; tocar la tesis, las cadenas canonicas o los numeros canonicos.

## Decisions

### D1 — Instrumento del brazo manual: OFFLINE sobre la planilla de ECM-008 (contrato C1)

Se mantiene la captura OFFLINE (planilla + CSV): no acopla la captura a la DB, es operable por personas sin cuenta y no expone PII. c-165 NO define esquema ni validador: adopta textualmente `evaluation/data/plantilla_etiquetado.csv` (dueno c-168, ECM-008) con columnas `id_caso, id_etiquetador, tarea, sector_etiquetado, sectores_adicionales_etiquetados, inicio, timestamp`, y valida con `evaluation/doble_etiquetado.py::validar_doble_etiquetado` (c-168). Lo especifico del brazo manual:

- filas con `tarea = brazo_manual` y operadores fijos `O1`, `O2`. Reparto: cada `id_caso` del plan lo clasifica AL MENOS UN operador (el reparto por mitades segun `plan_campana.csv` de c-166 es valido; la doble cobertura es opcional y deseable en una submuestra, que permite ademas medir el acuerdo entre operadores) y hay como maximo un registro por `(id_caso, id_etiquetador)`. Esas reglas las aplica el validador de c-168 con `tarea=brazo_manual`; c-165 no agrega reglas propias;
- tiempos por caso en la misma planilla: el operador registra `inicio` (ISO-8601 con zona) al tomar el caso y `timestamp` al asignar el sector, que es el FIN de la clasificacion del caso; para `tarea = brazo_manual` ambos son obligatorios (lo exige el validador de c-168) y reemplazan cualquier cronometro aparte. El tiempo del operador por caso es `timestamp - inicio`;
- `inicio` permite reconstruir la POSICION REAL de cada caso en la secuencia de cada operador. c-165 agrega `evaluation/brazo_manual.py` con dos funciones puras: `reconstruir_posicion_real(filas)` (orden por `inicio` dentro de cada `id_etiquetador`, desempate por `timestamp`, posiciones 1..N) y `desvios_respecto_del_plan(posiciones_reales, plan)` (compara contra la `posicion` de `plan_campana.csv` de c-166 y devuelve los casos desviados). Las cadenas de sector se importan de `evaluation.corpus.SECTORES_CANONICOS`; nunca se duplican.
- Los tests van en la suite `evaluation/tests/` (la que corre CI para `evaluation/`), no en el subset SQLite del backend.

Alternativa descartada: endpoint/tabla en la app (agrega superficie de datos personales y despliegue).

### D2 — Persistencia de la intervencion: EXTENDER `clasificacion_log` con cuatro columnas (contrato C4)

| Columna | Tipo | Nulabilidad | Semantica |
|---|---|---|---|
| `validado_por_empleado_id` | Integer, FK `fk_clasificacion_log_validado_por_directorio_empleado` -> `directorio_empleado.id`, `ON DELETE SET NULL`, indexada | nullable | Actor de la ultima intervencion; NULL si la cuenta no tiene empleado vinculado o si el empleado fue purgado por retencion |
| `intervencion_inicio_en` | DateTime(timezone=True) | nullable | Inicio declarado por el cliente (apertura del dialogo); NULL si no se envio o en `rederivacion` |
| `validado_en` | DateTime(timezone=True) | nullable | Instante del servidor en que se registro la intervencion; distinto de `created_at` |
| `origen_intervencion` | String(20) | nullable | Uno de `gate`, `muestreo`, `rederivacion`, `completado_manual` |

El DELTA antes/despues se reconstruye desde `sector_id_predicho`/`sectores_predichos` vs `sector_id_validado`/`sectores_validados`: no requiere columnas nuevas. El vocabulario se valida en la capa de aplicacion (Pydantic `Literal` + servicio); se descarta un CHECK en la DB porque obliga a otra migracion para ampliar el vocabulario y complica el `batch_alter_table` en SQLite (se puede reabrir en el checkpoint 2.1).

**Estados de un log** (derivados, sin columna nueva):

- `no_intervenido`: `validado_en IS NULL` y `sector_id_validado IS NULL`.
- `intervenido`: `validado_en IS NOT NULL`.
- `intervencion_legada_sin_metadatos`: `sector_id_validado IS NOT NULL` y `validado_en IS NULL` (filas validadas antes de la `024`). No hay backfill: inventar un instante o un origen seria fabricar registro primario. La metrica (D6) y el export (D7) las EXCLUYEN y declaran cuantas excluyeron.

**Re-validacion: gana la ultima escritura.** Cada intervencion sobrescribe como unidad las cuatro columnas, `sector_id_validado` y `sectores_validados`. Se corrige el defecto actual: `sectores_validados` se reemplaza SIEMPRE, incluso por el conjunto vacio cuando el payload trae `sectores_adicionales = []`. Consecuencia declarada: si un log validado por `gate` despues se re-deriva, el log queda con `origen_intervencion = rederivacion` y el `gate` previo no queda registrado (cuenta una sola vez en la tasa, con el ultimo origen). Un historial append-only (tabla `intervencion_humana`) queda fuera de alcance y se reevalua si la campana muestra re-intervenciones frecuentes.

### D3 — Escritores de `origen_intervencion` (contrato C3)

| Valor | Escritor | Regla |
|---|---|---|
| `gate` | `PATCH /clasificaciones/{log_id}/validar` | Derivado por el backend si el log tiene `requiere_revision_humana = True` |
| `muestreo` | `PATCH /clasificaciones/{log_id}/validar` | Derivado por el backend si el log NO esta marcado |
| `rederivacion` | `PATCH /incidentes/{id}` (`IncidenteService.update_incidente`), NUEVO | Cuando el payload trae `sector_id` distinto del sector actual del incidente |
| `completado_manual` | Ninguno en este change | Reservado; se declara sin escritor |

- **El cliente NO declara el origen** (decision del orquestador, para que un cliente no pueda registrar un origen falso): el backend lo deriva SIEMPRE con la tabla anterior en el endpoint de validacion, y `rederivacion` la escribe unicamente el servicio de incidentes. `ClasificacionValidar` aporta solo `intervencion_inicio_en` OPCIONAL (`AwareDatetime`: un instante sin zona responde 422). Un payload que trae la clave `origen_intervencion`, con cualquier valor, responde 422 con mensaje generico que no refleja el valor: se implementa con un validador `mode="before"` que rechaza esa clave puntual, sin pasar el schema a `extra="forbid"` (no cambia el trato de otros campos desconocidos). Los valores en ingles (`review`, `sample`, `manual_completion`, `reassignment`) desaparecen. El `origen_intervencion` sigue apareciendo en la LECTURA (`ClasificacionLogRead`).
- El frontend (`ValidarClasificacionDialog.tsx`) toma `intervencion_inicio_en` al abrir el dialogo (`open = true`) y lo envia al confirmar; NO envia `origen_intervencion`. `types/clasificacion.ts` agrega `intervencion_inicio_en?` a `ClasificacionValidar` y los campos de intervencion de solo lectura al tipo del log.
- **Rederivacion**: `update_incidente` resuelve el log mas reciente del incidente (mayor `id`) y escribe en el `sector_id_validado = nuevo sector_id`, `validado_en = now()`, `origen_intervencion = rederivacion`, actor = empleado de `EmpleadoDep` (o NULL) e `intervencion_inicio_en = NULL`; no toca `sectores_validados` ni `requiere_revision_humana`. Si el incidente no tiene log, no se registra nada y el PATCH responde igual que hoy. Un PATCH con el mismo `sector_id` actual, o sin `sector_id`, no registra intervencion. `validate()` NO dispara este escritor (propaga al incidente por el repositorio, no por el servicio), por lo que no hay doble escritura. Escribir `sector_id_validado` en la rederivacion saca el log de la cola de pendientes y lo convierte en etiqueta validada: es una decision que se presenta explicitamente en el CHECKPOINT 2.1.
- `muestreo` no tiene hoy superficie de UI (la cola solo lista marcados): el valor solo se escribe validando un log no marcado por la API. Se declara como limitacion; una superficie de muestreo queda fuera de alcance.

### D4 — Actor nullable resuelto con `EmpleadoDep`

El route de validacion inyecta `EmpleadoDep` (reutilizando `get_empleado_actual`; si el import cruzado entre routes resulta incomodo, se mueve a un modulo de dependencias compartido sin cambiar su comportamiento) y pasa `empleado.id if empleado else None` al servicio. Sin empleado vinculado la validacion NO falla: `validado_por_empleado_id` queda NULL y `validado_en` y `origen_intervencion` se registran igual. Asi no se rompen los tests que usan `User(id=1)` sin empleado. `PATCH /incidentes/{id}` agrega el mismo `EmpleadoDep` para la rederivacion.

### D5 — Governance ALTA: CHECKPOINT 2.1 obligatorio

El apply DEBE detenerse en la tarea 2.1, ANTES de cualquier tarea que toque el esquema o el modelo, y presentar al autor: (a) las cuatro columnas de D2 con tipos, nulabilidad y FK nombrada; (b) la migracion `024` (D6) con su `downgrade`; (c) el ajuste de `tests/test_migration_023_directorio_auditoria.py:145` (el head pasa a `"024"`); (d) el escritor de `rederivacion` de D3, incluida la escritura de `sector_id_validado`. Sin aprobacion explicita no se avanza ni se ejecuta `alembic upgrade` sobre datos reales.

### D6 — Migracion Alembic `024` con `batch_alter_table`

`App/Backend/alembic/versions/024_clasificacion_log_intervencion.py`, `revision = "024"`, `down_revision = "023"` (la cadena 001..023 es lineal). Siguiendo el precedente `019_soft_delete_incidente.py:36-52`: `op.batch_alter_table("clasificacion_log")` agrega las cuatro columnas nullable y la FK con nombre explicito, y despues crea el indice `ix_clasificacion_log_validado_por_empleado_id`. `downgrade` borra el indice y las columnas (FK incluida) en un `batch_alter_table`. No se muta ninguna migracion anterior. Tests: `tests/test_migration_024_clasificacion_log_intervencion.py` con el patron de `test_migration_023` (head y `down_revision`, upgrade crea las columnas nullable, downgrade las retira, filas previas intactas) y prueba de la FK `SET NULL` en el subset PostgreSQL.

### D7 — Metrica backend `tasa_intervencion_backend` (contrato C5)

- **Nombre**: `tasa_intervencion_backend`, para no chocar con `tasa_intervencion_humana` de c-167 (metrica offline de la campana, con IC). `tasa_revision_humana` se conserva sin cambios, con su descripcion corregida (pendientes al momento de la consulta).
- **Cohorte**: logs con `ClasificacionLog.created_at` en `[desde, hasta)`. Denominador = logs de la cohorte EXCLUIDOS los `intervencion_legada_sin_metadatos`. Numerador (`estadisticas_repository.contar_intervenciones(desde, hasta)`) = logs de la misma cohorte con `validado_en IS NOT NULL`. Sin logs en la cohorte la tasa es `0.0` (misma convencion que `tasa_revision_humana`).
- **Confirmacion sin cambio**: una validacion que confirma el sector predicho CUENTA como intervencion (hubo accion humana). El desglose `intervenciones_por_cambio_sector` (`{"true": n, "false": m}`) separa correcciones de confirmaciones; `cambio_sector = sector_id_validado != sector_id_predicho` (un predicho NULL cuenta como cambio).
- **Desglose por origen**: `intervenciones_por_origen` con las cuatro claves del vocabulario (cero si no hay).
- **Declaracion de legados**: `intervenciones_legadas_excluidas` (entero) en la respuesta.
- Se exponen en `ResumenResponse` (`app/schemas/estadisticas.py`) y se regenera `docs/openapi.json` con `App/Backend/scripts/export_openapi.py` (si no, falla `tests/test_openapi_sync.py`).

### D8 — Export pseudonimizado para c-167 (contrato C5)

CLI `App/Backend/scripts/exportar_intervenciones.py --sidecar <ruta> [--sidecar ...] [--desde ... --hasta ...] --salida evaluation/data/campana/intervenciones.csv`:

- Una fila por log INTERVENIDO (`validado_en IS NOT NULL`); los legados no se exportan y su cantidad se informa en el resumen de la corrida.
- Columnas, en orden: `id_caso, incidente_id, log_id, origen_intervencion, intervencion_inicio_en, validado_en, duracion_s, sector_predicho, sector_validado, cambio_sector, actor_alias`.
- `id_caso` se obtiene del sidecar de la corrida (`case_id` por `incidente_id`); vacio si no se puede vincular. `duracion_s = validado_en - intervencion_inicio_en` en segundos; vacio si falta el inicio o si el inicio es posterior a `validado_en` (desfase de reloj del cliente; se cuenta en el resumen). `sector_predicho`/`sector_validado` son nombres canonicos.
- `actor_alias` = HMAC-SHA256 del `validado_por_empleado_id` con una clave secreta tomada del entorno (no versionada), truncado a 12 hex; vacio si el actor es NULL. Un hash plano de un entero chico seria reversible por enumeracion, por eso se usa clave. Nunca se exportan nombre, email, telefono, legajo ni el id en claro.
- El denominador de la proporcion de casos NO sale del export: c-167 lo toma de los casos del plan de campana (`plan_campana.csv`) o del sidecar de la corrida.
- El CLI se niega a escribir sobre archivos congelados (D10).

### D9 — Sujetos y referencia (contrato C2) y plan de campana (contrato C6)

- Operadores del brazo manual (`O*`) y etiquetadores del doble etiquetado (`E*`) son personas distintas entre si, distintas de los dos analistas que fijaron el consenso original y distintas de los autores. Los operadores no ven la prediccion ni el consenso.
- La referencia del brazo manual es el consenso del doble etiquetado NUEVO de c-168 cuando `E1` y `E2` coinciden; los casos discordantes se reportan aparte y no se miden.
- El runbook registra a los operadores `O1`/`O2` en `evaluation/data/campana/registro_sujetos.csv` (esquema definido por c-168: `alias, rol, persona`), donde `persona` es un seudonimo estable `P<n>` que identifica a la misma persona a traves de roles; nunca nombres en el repo. La independencia de C2 se verifica por `persona` (ninguna `persona` de un `O*` aparece con otro rol: `E*`, analista del consenso original o autor). c-167 recibe ese registro y rechaza solapes.
- Los operadores siguen la `posicion` y el `brazo_primero` de `evaluation/data/campana/plan_campana.csv` (c-166); el operador registra `inicio` al tomar cada caso y `timestamp` al asignar el sector, y `inicio` permite reconstruir la posicion real (D1).

### D10 — Ubicacion de runbooks y datos (contrato C7)

Runbook en `docs/campana-medicion/runbook-brazo-manual-e-intervencion.md`. Datos de campana en `evaluation/data/campana/` (sin PII), con un `README.md` que lista cada archivo con su SHA-256 (patron de `evaluation/evidence/`). Nunca se escribe sobre `data/corpus_evaluacion_pseudonimizado.json`, `data/corpus_resultados*.json` ni `evaluation/predicciones.json`.

### D11 — TDD

Test primero en cada tarea con codigo: suite `evaluation/tests/` para D1; subset SQLite (`pytest -m "not integration"`) para repositorio, servicio, schemas, metrica y export; subset PostgreSQL (`pytest -m integration`) para la migracion `024` y la FK `SET NULL`; Vitest para el dialogo.

## Lo que NO cambia

- `docs/Tesis/` (v9 congelada; la tesis vigente solo la toca c-169).
- Las cinco cadenas canonicas de sector (`evaluation.corpus.SECTORES_CANONICOS`, `sector-taxonomy`, migracion `004`).
- Los numeros canonicos (`docs/Tesis/Correcciones/numeros-canonicos.md`) y `evaluation/report.md`.
- El corpus `data/corpus_evaluacion_pseudonimizado.json`, `data/corpus_resultados*.json`, `evaluation/predicciones.json` y los sidecars versionados como evidencia (`evaluation/evidence/`).
- Las migraciones `001..023` (solo se ajusta el assert de head en el test de `023`).
- La semantica de `tasa_revision_humana` (solo se corrige su descripcion).

## Risks / Trade-offs

- Mutar el esquema de auditoria -> CHECKPOINT 2.1 (D5) + columnas nullable + `downgrade` funcional.
- Sobrescritura de la intervencion previa en re-validacion o rederivacion -> declarada (D2); historial append-only fuera de alcance.
- `intervencion_inicio_en` depende del reloj del cliente -> se guarda tal cual; el export anula la duracion negativa y la cuenta.
- `muestreo` sin superficie de UI -> declarado (D3); la campana solo puede producirlo por la API.
- Etiquetado no independiente o circular -> C2 verificado por `persona` en `registro_sujetos.csv` y rechazo de solapes en c-167.

## Migration Plan

1. CHECKPOINT 2.1 aprobado.
2. Revision `024` (`down_revision = "023"`) con las cuatro columnas nullable, FK nombrada e indice, en `batch_alter_table`.
3. Backfill: NINGUNO. Filas previas validadas quedan como `intervencion_legada_sin_metadatos`; filas no validadas quedan `no_intervenido`.
4. Rollback: `alembic downgrade 023` retira indice, FK y columnas sin tocar filas existentes.

## Open Questions

- Minimo de casos de la campana (N): el runbook lo fija antes de la campana (por defecto, la totalidad de casos del plan de campana) y lo justifica; no cambia el spec ni el enfoque.
- Superficie de UI para `muestreo` y flujo de `completado_manual`: fuera de alcance; se registran como trabajo futuro.
