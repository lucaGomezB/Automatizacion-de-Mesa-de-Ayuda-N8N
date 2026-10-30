# Proposal: Instrumentar la campana para medir el brazo manual y la intervencion

## Why

Una auditoria CONEAU acoto el criterio de metodologia porque el repositorio CARECE de instrumentacion para medir (a) la exactitud de clasificacion del BRAZO MANUAL y (b) la TASA DE INTERVENCION HUMANA. Sin instrumento ni protocolo de campana, ninguno de los dos datasets es producible ni verificable, y la segunda sub-hipotesis sigue "no contrastada por ausencia de registro primario". Este es el primero de cinco changes (c-165..c-169); c-169 documentara los resultados.

Este proposal fue enmendado antes del primer apply segun la revision `docs/campana-medicion/revision-pre-apply-c-165-a-c-169.md` (transversales T1, T2, T4 y bloqueantes 1 a 3 de c-165) y adopta los contratos compartidos C1..C7 del programa de medicion.

## What Changes

- **Instrumento del brazo manual (adopta el esquema de c-168)**: la clasificacion del operador por caso se registra en la planilla unica `evaluation/data/plantilla_etiquetado.csv` definida por ECM-008 (c-168), con `tarea = brazo_manual` y operadores fijos con alias `O1`, `O2`: cada `id_caso` lo clasifica AL MENOS UN operador (reparto por mitades segun el plan de c-166; doble cobertura opcional y deseable en una submuestra), con un maximo de un registro por `(id_caso, id_etiquetador)`. c-165 NO define un esquema ni un validador propios: valida con `evaluation/doble_etiquetado.py::validar_doble_etiquetado` (c-168) y agrega solo lo especifico del brazo manual (sujetos distintos, posicion real reconstruida desde `inicio` contra el plan de campana de c-166). El operador registra `inicio` (ISO-8601) al tomar el caso y `timestamp` al asignar el sector; ambos son obligatorios para `tarea = brazo_manual` y reemplazan cualquier cronometro aparte.
- **Sujetos (anti-circularidad)**: los operadores `O*` son personas distintas de los etiquetadores `E*` de c-168, de los dos analistas que fijaron el consenso original y de los autores, verificado por el seudonimo `persona` de `registro_sujetos.csv`; no ven la prediccion ni el consenso. La referencia contra la que se mide el brazo manual es el consenso del doble etiquetado NUEVO de c-168 cuando ambos etiquetadores coinciden; los casos discordantes se reportan aparte.
- **Registro de intervencion humana ampliado** en `clasificacion_log` (migracion `024`): actor (`validado_por_empleado_id`, FK nombrada a `directorio_empleado.id`, `ON DELETE SET NULL`, nullable), instante de inicio (`intervencion_inicio_en`), instante de validacion propio (`validado_en`) y ORIGEN (`origen_intervencion` en `gate | muestreo | rederivacion | completado_manual`, vocabulario de la tesis). El delta antes/despues se reconstruye desde las columnas predicho/validado existentes.
- **Escritores del origen**: `PATCH /clasificaciones/{log_id}/validar` (el backend deriva SIEMPRE `gate` o `muestreo` segun `requiere_revision_humana` del log; el cliente no puede declarar el origen) y un escritor NUEVO de `rederivacion` desde `PATCH /incidentes/{id}` cuando cambia `sector_id`. `completado_manual` queda reservado y SIN escritor en este change (declarado).
- **Payload y frontend**: `ClasificacionValidar` acepta solo `intervencion_inicio_en` opcional; un payload que trae `origen_intervencion` se rechaza con 422. `ValidarClasificacionDialog.tsx` y `types/clasificacion.ts` envian `intervencion_inicio_en`.
- **Metrica backend `tasa_intervencion_backend`** (renombrada para no chocar con `tasa_intervencion_humana` de c-167): intervenciones / logs de la misma cohorte, con desglose por origen y por cambio de sector, expuesta en `ResumenResponse`; los datos legados se excluyen y se declaran.
- **Export pseudonimizado** (`App/Backend/scripts/exportar_intervenciones.py`) que produce `evaluation/data/campana/intervenciones.csv`, sin PII, que es lo que lee c-167.
- **Runbook de campana** `docs/campana-medicion/runbook-brazo-manual-e-intervencion.md`: sujetos y alias, minimo de casos, plan de campana de c-166, instrumento, aceptacion/verificacion y prohibicion de escribir sobre archivos congelados.

## Capabilities

### New Capabilities

- `evaluation-campaign-instrumentation`: instrumento de captura del brazo manual (sobre la planilla de ECM-008), protocolo de campana registrado, medicion backend de la tasa de intervencion y export pseudonimizado para el analisis.

### Modified Capabilities

- `sector-assignment`: se MODIFICA `ASG-005` para persistir los metadatos de la intervencion (actor nullable, inicio, instante propio, origen) junto al conjunto validado, con escritores declarados por origen.

## Impact

- Backend:
  - `App/Backend/app/models/clasificacion_log.py` (cuatro columnas nuevas)
  - `App/Backend/app/repositories/clasificacion_repository.py` (persistencia de los metadatos; reemplazo de `sectores_validados` aun vacio)
  - `App/Backend/app/services/clasificacion_service.py` (`validate` / `validate_payload`: aqui vive la validacion, lineas 215-315)
  - `App/Backend/app/routes/clasificaciones.py` (resuelve el actor con `EmpleadoDep`)
  - `App/Backend/app/routes/incidentes.py` y `App/Backend/app/services/incidente_service.py` (escritor de `rederivacion` en `update_incidente`; NO son duenos de la validacion)
  - `App/Backend/app/schemas/clasificacion.py` (`ClasificacionValidar` y `ClasificacionLogRead`)
  - `App/Backend/app/repositories/estadisticas_repository.py`, `App/Backend/app/services/estadisticas_service.py`, `App/Backend/app/schemas/estadisticas.py` (`tasa_intervencion_backend` en `ResumenResponse`)
  - `App/Backend/alembic/versions/024_clasificacion_log_intervencion.py` (nueva, `down_revision = "023"`, `batch_alter_table`)
  - `App/Backend/tests/test_migration_023_directorio_auditoria.py` (el head pasa a `"024"`) y `App/Backend/tests/test_migration_024_clasificacion_log_intervencion.py` (nuevo)
  - `App/Backend/scripts/exportar_intervenciones.py` (nuevo) y su test
- Frontend: `App/Frontend/src/pages/Administracion/ValidarClasificacionDialog.tsx`, `App/Frontend/src/types/clasificacion.ts`
- Evaluacion: `evaluation/brazo_manual.py` (posicion real y desvios contra el plan) y su test en `evaluation/tests/`; `evaluation/data/campana/` (README con SHA-256; sin PII)
- Documentacion: `docs/openapi.json` (regenerado), `docs/anexo_c_esquema_bd.md` (tabla `clasificacion_log`), `docs/campana-medicion/runbook-brazo-manual-e-intervencion.md`, registro en `CHANGES.md`
- Specs: `openspec/specs/sector-assignment/` (modificado) y `evaluation-campaign-instrumentation/` (nueva)

### Out of Scope

- Ejecutar la campana de campo (corre fuera del repo; c-169 documenta resultados).
- Un flujo que escriba `completado_manual` (el valor queda reservado, sin escritor).
- Historial append-only de varias intervenciones por log (gana la ultima escritura).
- Datos de campo reales; cambios a `docs/Tesis/` (v9 congelada; la tesis vigente la toca solo c-169); cadenas canonicas de sector; numeros canonicos; corpus y sidecars versionados.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Mutar el esquema de auditoria sin revision | Med | Gobernanza ALTA: CHECKPOINT 2.1 con confirmacion humana explicita antes de tocar el esquema |
| Circularidad del gold (operadores = analistas del consenso) | Alta si no se controla | C2: sujetos distintos, referencia = consenso del doble etiquetado nuevo de c-168, independencia verificada por `persona` en `registro_sujetos.csv` (c-168) y solapes rechazados por c-167 |
| Romper los ~50 tests que usan `User(id=1)` sin empleado | Med | Actor nullable: sin empleado vinculado se registran igual `validado_en` y `origen_intervencion` |
| Datos legados contados como no intervenidos | Med | Estado `intervencion_legada_sin_metadatos`, excluido del numerador y del denominador y declarado |
| Re-identificacion del actor en el export | Baja | `actor_alias` es un hash con clave (no un hash plano del id), truncado |
| Sobrescribir archivos congelados (corpus, sidecars, predicciones) | Baja | Runbook y export los prohiben; el cierre verifica con `git diff --stat` |

## Rollback Plan

Revertir la migracion (`alembic downgrade 023`), que retira las cuatro columnas, la FK nombrada y el indice sin tocar filas existentes; revertir los cambios de payload/frontend/metrica (los campos nuevos son opcionales y aditivos) y retirar el export y el runbook. La tabla `clasificacion_log`, el corpus y los sidecars no se destruyen.

## Dependencies

- **c-168 (ECM-008/ECM-009)**: dueno del esquema de la planilla y del validador `validar_doble_etiquetado`. Orden de APLICACION recomendado: aplicar c-168 ANTES que el grupo 1 de c-165 (el grupo 2 en adelante no depende de c-168). El orden de ARCHIVO sigue c-165 -> c-166 -> c-168 y es seguro (sin ADDED repetidos ni MODIFIED cruzados sobre la capability nueva).
- **c-166**: dueno de `generar_plan_campana` y de `evaluation/data/campana/plan_campana.csv`, y de los sidecars por corrida que el export usa para vincular `incidente_id` con `id_caso`.
- **c-167**: consume `intervenciones.csv`, la planilla del brazo manual y `evaluation/data/campana/registro_sujetos.csv` (definido por c-168; `alias, rol, persona`), donde el runbook de c-165 registra a `O1`/`O2`.
- Corpus pseudonimizado (`data/corpus_evaluacion_pseudonimizado.json`) ya versionado: solo lectura.

## Success Criteria

- [ ] El brazo manual se captura en la planilla de ECM-008 (`tarea = brazo_manual`) y valida con el validador de c-168, sin esquema propio.
- [ ] El registro de intervencion persiste actor (nullable), inicio, instante y origen, con escritores declarados para cada valor del vocabulario.
- [ ] `tasa_intervencion_backend` esta expuesta en `ResumenResponse` y `docs/openapi.json` esta sincronizado.
- [ ] El export produce `evaluation/data/campana/intervenciones.csv` sin PII con las columnas acordadas.
- [ ] Existe el runbook en `docs/campana-medicion/` con sujetos, minimo de casos, plan de campana y verificacion.
- [ ] Subsets SQLite y PostgreSQL verdes; `openspec validate --strict` en verde; ningun archivo congelado modificado.
