# Revisión previa al apply del programa de medición (c-165 a c-169)

Fecha: 2026-10-29. Base: `main` en `a1b15c7` (commit de proposición `dbaf556`; los cinco tree hashes coinciden con los que pasó Lucas). Los cinco changes pasan `openspec validate --strict`, pero esa validación no compara contra las specs principales ni contra el código. Revisión de solo lectura: no se aplicó nada.

## Veredicto global

**Ninguno de los cinco se aplica tal cual. Los cinco son APLICAR CON ENMIENDAS; ninguno requiere re-proponer el enfoque.** El programa es correcto en su diagnóstico (ataca exactamente los ítems del dictamen v1.2.5) y en su descomposición. Lo que falla son los contratos entre changes y tres decisiones metodológicas que, si se aplican como están, dejarían una campaña cuyos datos no sirven para responder lo que la auditoría pide.

| Change | Veredicto | Bloqueantes |
|---|---|---|
| c-165 | Con enmiendas | 3 |
| c-166 | Con enmiendas | 2 |
| c-167 | Con enmiendas | 4 |
| c-168 | Con enmiendas | 0 (5 importantes) |
| c-169 | Con enmiendas (sigue gateado) | 4, incluido uno que hace fallar el archive |

## Los cuatro problemas transversales (resolver primero, afectan a varios changes)

### T1. Tres esquemas distintos para la misma planilla etiquetador x caso

- c-165 tarea 1.1: `id_corpus, id_etiquetador, sector, adicionales`.
- c-167 design D4: `id_corpus, etiquetador, sector`.
- c-168 ECM-008: `id_caso, id_etiquetador, sector_asignado, sectores_adicionales, timestamp`.
- El corpus real identifica el caso por `id` (`R001..R200`); el sidecar de c-166 usa `case_id`.

c-167 no puede leer lo que c-165 y c-168 producen. Además `sector_asignado` en c-168 es el campo del etiquetador, pero en el corpus `sector_asignado` es el consenso, y ECM-010 ("no ver el consenso `sector_asignado`") queda ambiguo.

**Enmienda:** un único esquema, dueño c-168, adoptado por c-165 y c-167: `id_caso` (= `id` del corpus), `id_etiquetador` (alias sin PII), `sector_etiquetado`, `sectores_adicionales_etiquetados` (separador interno fijo), `timestamp` ISO-8601, más una columna `tarea` (`brazo_manual` | `doble_etiquetado`). Un solo validador que importe `SECTORES_CANONICOS` de `evaluation/corpus.py`.

### T2. Circularidad del gold y cegado roto

La tesis declara (`04-marco-metodologico.tex:55`, `:85`) que los dos analistas que fijaron el consenso son los mismos que operaron el brazo manual. Si vuelven a etiquetar (c-168) o a operar (c-165) y se los mide "contra el consenso", la exactitud del brazo manual queda sesgada hacia arriba y el cegado de ECM-010 no se cumple. Es precisamente la limitación que el dictamen marcó.

**Enmienda:** en ECM-001 y ECM-010 exigir operadores y etiquetadores distintos de los dos originales y de los autores (o declarar la limitación de forma explícita); en c-167 la referencia (gold) es un parámetro y el análisis recibe la lista de quienes la produjeron y rechaza el solape con los sujetos del brazo manual.

### T3. El contrabalanceo apunta al sujeto equivocado

c-166 agrega `--orden {directo,inverso,alternado,aleatorio}` a los harnesses de ingesta, que reordenan el procesamiento del **brazo automatizado**. Una máquina no aprende ni se fatiga: ese orden no produce el efecto de orden que la auditoría pide. El efecto de orden relevante es el del **operador humano** y el orden de condición (manual-primero vs automatizado-primero), como lo define la propia tesis (`04:14`) y la KB (`11_evaluacion_experimental.md:56`). Además el campo `orden` del sidecar guarda el modo ("alternado"), idéntico para todos los casos, y no la posición; y `write_sidecar_json` mergea por `case_id`, por lo que una segunda corrida pisa la primera.

**Enmienda:** `ordenar_casos` genera y exporta un **plan de campaña por caso** (`id_caso, posicion, mitad, brazo_primero, seed`) que guía al brazo manual (fuera del repo) y a los harnesses; en `CaseResult` van `orden`, `posicion` y `mitad` con default `None` al final del dataclass; sidecars separados por corrida. En c-167, el efecto de orden define respuesta (tiempo del operador), pareo por caso entre corridas, posición desde el plan, mínimo n >= 6 pares y MDE reportado (dz ~ 0,21 con n = 200). Telefonía se controla por el plan, no por `ingest_telefonia_corpus.py` (ese script no ingesta: lee mediciones).

### T4. La proporción de tiempo de intervención no es estimable con lo que registra c-165

c-165 persiste un solo instante (`validado_en`). La tesis (11.3, `10-recomendaciones.tex:18`) pide inicio y fin, y c-167 promete "proporción del tiempo con IC", y además con IC de Wilson, que no corresponde a un cociente de sumas continuas.

**Enmienda:** agregar `intervencion_inicio_en` en c-165 (o declarar en ambos changes que la proporción de tiempo queda fuera), definir el denominador (hoy `tiempo_automatizado_s` mide solo el registro) y usar bootstrap por caso del cociente, no Wilson. c-165 también necesita una tarea de **export pseudonimizado** del dataset de intervención (`id_caso, incidente_id, validado_en, origen_intervencion, inicio, fin`) para que c-167 tenga qué leer.

## Hallazgos por change

### c-165 (gobernanza ALTA)

Bloqueantes:
1. **`origen_intervencion` no tiene quién lo fije.** Hoy el único flujo que escribe el log es `PATCH /clasificaciones/{id}/validar` desde la cola; la reasignación va por `PATCH /incidentes` y no toca el log; no existen flujos de muestreo ni de completado manual; `review` no tiene equivalente en la tesis. No hay task para el payload (`ClasificacionValidar`), ni para el frontend (`ValidarClasificacionDialog.tsx`). Enmienda: alinear el vocabulario con la tesis, agregar el campo opcional al payload/schema/frontend con valor por defecto derivado (`gate` si `log.requiere_revision_humana`, si no `sample`), y registrar la reasignación o sacarla del alcance declarándolo.
2. Falta el instante de inicio (T4).
3. ECM-001 no exige operadores distintos de los etiquetadores de la referencia (T2).

Importantes:
4. Impact mal citado: la validación vive en `app/services/clasificacion_service.py:215-315`, no en `incidente_service.py`; la FK es a `directorio_empleado.id`.
5. El actor debe ser nullable de forma explícita: `current_user` es un `User`, no un empleado; se resuelve con `EmpleadoDep`. El fixture de tests usa `User(id=1)` sin empleado; exigir empleado rompe unos 50 tests.
6. Datos legados: las filas ya validadas quedarían con `validado_en` NULL y ECM-003 las contaría como no intervenidas. Definir un estado legado o restringir la métrica a logs posteriores a la migración.
7. Premisa errónea en el design: `tasa_revision_humana` cuenta `Incidente.requiere_revision_humana`, que `validate()` pone en False, así que mide pendientes, no marcados. Definir numerador y denominador sobre la misma cohorte y si una confirmación sin cambios cuenta como intervención.
8. Tasks faltantes: migración `024` con `batch_alter_table` y FK nombrada (precedente `019_soft_delete_incidente.py`); actualizar `tests/test_migration_023_directorio_auditoria.py:145` (asserta head == "023"); `ResumenResponse` + regenerar `docs/openapi.json` (si no, falla `test_openapi_sync.py`); exportador para c-167; `docs/anexo_c_esquema_bd.md`.
9. Choque de nombres: `tasa_intervencion_humana` existe en c-165 (backend) y en c-167 (offline) con semánticas distintas.

Menores: task 1.4 pertenece a la suite `evaluation/`, no al subset SQLite; valores de origen en inglés frente a la convención en español; re-validación sobrescribe sin historial y `sectores_validados` no se reemplaza si llega vacío; registrar en `CHANGES.md`.

El checkpoint 2.1 está bien ubicado (antes de tocar el esquema). Recomendación para ese checkpoint: presentar las columnas, la migración `024` y el ajuste del test de `023`, y no avanzar sin confirmación explícita.

### c-166

Bloqueantes: T3 (campo `orden` sin posición; contrabalanceo de la máquina en vez de la condición).

Importantes:
- ECM-007 y la sección 5 de tasks duplican "evaluación out-of-sample" de c-167 (`evaluar_fuera_de_muestra`). Dejar un solo dueño.
- `run_evaluation.py` no tiene `--corpus` ni `--predicciones`; correrlo contra otro corpus **sobrescribe `evaluation/predicciones.json` (artefacto v9 congelado)** y dispara la corrida paga. Hacen falta flags y protección.
- `ingest_via_n8n.run` hace merge sobre `data/corpus_evaluacion_pseudonimizado.json` por defecto: una corrida de campaña con los defaults **pisaría los tiempos canónicos (17,76 s)** y los sidecars versionados como evidencia. El runbook debe obligar `--json` y `--sidecar` propios de la campaña, o el código debe protegerlos.
- `ingest_corpus.py` no usa `CaseResult` (tiene `CorpusResult` y un sidecar que sobrescribe todo): la tarea 2.4 no lo cubre.
- `CaseResult` no tiene defaults y se construye en 6 lugares: el campo nuevo va al final con `= None`.
- `--limit` se aplica antes del orden: `--limit N --orden inverso` da el reverso de los primeros N. Fijar la regla.
- `verificar_no_solape` sin ubicación: va en `evaluation/` (en CI); el control por `id` exige prefijo propio para el corpus independiente; el hash exacto no detecta paráfrasis (declararlo o agregar similitud de tokens).
- Los tests de `scripts/corpus_ingest/` no corren en CI: el TDD de c-166 no queda en el gate.

Menores: proposal dice "BREAKING menor" para un cambio aditivo; rutas de tests incompletas en 2.6; `--orden aleatorio` sin semilla y "paso previo obligatorio" sin escenario.

### c-167

Bloqueantes: T1 (contratos), T2 (gold), T4 (tiempo), T3 (efecto de orden mal especificado: sin variable respuesta, sin unidad de pareo, sin fuente de posición; si la respuesta fuera acierto corresponde McNemar, que ya existe en `stats.py`).

Importantes:
- Cohen exige dos etiquetadores fijos; c-168 admite "al menos dos". Exigir exactamente dos `id_etiquetador` fijos (fallar si no) o agregar Fleiss; declarar que el kappa es sobre la etiqueta primaria, 5 clases, no ponderado.
- Fórmula del IC asintótico sin especificar: usar la varianza bajo H1 de Fleiss, Cohen y Everitt (1969), no la de H0. Oráculo para el test: matriz [[20,5,0],[3,15,2],[0,4,11]] (n = 60) da kappa = 0,642553 y SE(H1) = 0,083594. Recortar los límites a [-1, 1]; diagonal perfecta da IC [1, 1]; p_e = 1 solo con p_o = 1, no estimable; definir política para remuestras degeneradas en el bootstrap.
- Pseudo-replicación: Wilson sobre 2N observaciones (dos etiquetadores, mismos casos) da un IC demasiado estrecho. Bootstrap por caso o solo por etiquetador.
- Out-of-sample sin regla de congelamiento: exigir `classifier_version` y commit iguales a los del in-sample, tau/prompt/vocabulario fijos, re-ejecutar `verificar_no_solape`, y leer predicciones con `cargar_predicciones`/`cargar_cache_meta` (nunca `main()`, que llama a Gemini).
- Falta el contraste manual vs automatizado por caso (McNemar con `contraste_mcnemar`), que es el objetivo 4 de la tesis.

Lo que está bien y debe reutilizarse: `resumen_exactitud`/`desglose_exactitud` (estricta/laxa con Wilson por grupo), `intervalo_wilson`, `SEMILLA_BOOTSTRAP = 20261021`, `REMUESTREOS_BOOTSTRAP = 2000`, `wilcoxon_tiempos_detallado`, `tamano_efecto_dz`, `efecto_minimo_detectable`. `scipy` ya está en requirements; no hace falta nada nuevo. Hay precedente de fixture sintético en `evaluation/tests/fixtures/`.

Menores: spec admite "término de orden" y el design lo descarta; proposal deja abierta la ubicación del código; tasks sin Landis-Koch, sin "IC no computable", sin safety net ni REFACTOR; 6.1 crea el fixture después de usarlo; D7 omite c-168; citar `subsec:medicion-intervencion` en vez de "11.3"; explicitar que `report.md` y `predicciones.json` no se tocan.

### c-168

Las cinco cadenas canónicas coinciden carácter por carácter con `evaluation/corpus.py:52-58`, `sector-taxonomy` y la migración `004`. Esa parte está bien.

Importantes:
- T1 (esquema único) y T2 (cegado: los etiquetadores originales no están ciegos al consenso).
- Renombrar la columna `sector_asignado` del etiquetador o desambiguar ECM-010.
- La tarea 2.5 pide "constantes de cadenas canónicas": invita a duplicarlas; importar `SECTORES_CANONICOS`.
- Faltan en ECM-009: `id_caso` desconocido, regla de no repetición entre principal y adicionales, formato de `timestamp`, codificación de la lista en CSV, y la variable sobre la que se calcula el acuerdo.
- La motivación es que la tabla primaria "no se conservó": el criterio de aceptación debe exigir versionar la tabla validada (sin PII) con SHA-256, citada en `numeros-canonicos.md`.

Menores: el importador (4.1) no tiene requisito ni formato de entrada real (quitarlo o sustentarlo); nombres en inglés (`double_labeling.py`); cubrir el corpus independiente en el runbook; `tasks.md` sin título.

### c-169 (gateado)

Bloqueantes:
1. **El archive falla hoy:** el MODIFIED `Declaracion del estado de la hipótesis principal` no coincide con la principal (`tesis-document/spec.md:2013`, "Declaración" con tilde).
2. Siete requisitos de la principal quedarían contradictorios sin MODIFIED ni REMOVED: `:4173` (exactitud manual "no medida"), `:4330` (sub-hipótesis 2 "no contrastada" propagada), `:4676` (exige `subsec:medicion-intervencion`, que 4.2 retira), `:4267`, `:4724`, `:4285`, `:5330`.
3. Kappa nuevo vs 0,87 original sin resolver: el MODIFIED fija el rótulo "casi perfecto" y "junto al 0,87", pero c-168 re-etiqueta con otras personas y da un kappa nuevo. Decidir valor, rótulo, estado del 0,87 en el memo y un caso negativo coherente en los tres requisitos.
4. Alcance desfasado: la numeración real es 4.6 métricas, 4.7 análisis estadístico, 4.8 amenazas (el change dice 4.7/4.8). Faltan `01-introduccion.tex:34`, `09-conclusiones.tex` completo, Anexo B (la campaña corre con otro código: tercera configuración), `10:6/:42-48`, `08:20/:22/:97`, el balance neto, `07:6` y el cronograma.

Importantes: gate mecánico (rutas: `openspec/changes/archive/*-c-16[5-8]-*`, `evaluation/kappa.py`, runbooks, salidas de campaña versionadas con SHA en `evaluation/evidence/`); prever los desenlaces negativos (sub-hipótesis 2 refutada si el límite superior de Wilson >= 0,15, registro incompleto, dataset ausente) o dividir el change por dataset; tareas de PDF, renders, release y hash, `verify_citations`, tildes y recuento del resumen (margen actual: 1 palabra en ES, 5 en EN); sección en `dictamen-correcciones.md`; "etiquetadores = operadores" en `04:55` y `08`.

## Orden de aplicación

El orden propuesto por Lucas (c-165 con checkpoint, luego c-166, c-168, c-167, campaña, c-169) es correcto, y el archive de la capability `evaluation-campaign-instrumentation` es seguro en cualquier orden (verificado con OpenSpec 1.6.0 sobre copias: sin ADDED repetidos, sin MODIFIED en c-166/c-168). Dos ajustes:

- c-166 y c-168 no dependen de la migración de c-165: no hace falta que esperen el checkpoint de gobernanza ALTA.
- Completar a mano el `## Purpose` de la capability nueva después del primer archive (queda "TBD").

## Recomendación

Enmendar los cinco changes **antes** del primer apply, en este orden: (1) fijar T1 en c-168 y propagarlo a c-165 y c-167; (2) fijar T3 en c-166 y c-167; (3) fijar T2 y T4 en c-165, c-167 y c-168; (4) corregir el encabezado y los siete requisitos huérfanos de c-169. Después aplicar c-165 hasta el checkpoint 2.1. Alternativa pragmática si urge avanzar: aplicar primero kappa + exactitud manual de c-167 (secciones 1 y 2) con las enmiendas metodológicas, que no dependen de la migración ni del contrabalanceo.

Pendientes administrativos: registrar c-165 a c-169 como FASE 52 en `CHANGES.md` (hoy no figuran, y la sección de pendientes está desfasada) y corregir `plan-campana-de-medicion.md:3` ("después de aplicar c-165 a c-169" contradice la tabla, que marca c-169 como post-campaña).

## Apéndice (2026-10-30): estado tras las enmiendas

Los cinco changes fueron enmendados en la rama `docs/enmiendas-c-165-a-c-169` (sin commit), cada uno dentro de su propio directorio. Los cinco pasan `openspec validate --strict`, y la simulación de archive sobre una copia (orden c-165, c-166, c-168, c-167, c-169) termina con 65 specs válidas, ECM-001 a ECM-010 completos y cero changes activos. Queda un paso manual conocido: completar el `## Purpose` de `evaluation-campaign-instrumentation` después del primer archive (el CLI lo deja en "TBD").

### Contratos compartidos fijados (los cinco los adoptan textualmente)

| Contrato | Dueño | Contenido |
|---|---|---|
| Planilla única de etiquetado | c-168 (ECM-008) | `evaluation/data/plantilla_etiquetado.csv` con `id_caso, id_etiquetador, tarea, sector_etiquetado, sectores_adicionales_etiquetados, inicio, timestamp`. `tarea` en `doble_etiquetado` o `brazo_manual`; `inicio` obligatorio en brazo manual; `sector_asignado` queda reservado al consenso del corpus. Validador único `evaluation/doble_etiquetado.py` con reglas (a)-(j) y exit codes. |
| Sujetos | c-168 (ECM-010) | `registro_sujetos.csv` con `alias, rol, persona`; etiquetadores E1/E2 y operadores O1/O2 distintos entre sí, de los analistas originales y de los autores; el solape se detecta por `persona`. Referencia del brazo manual = coincidencia E1 = E2; discordantes aparte. Si no hay sujetos nuevos, se declara como limitación, nunca como cegado. |
| Intervención | c-165 | Columnas `validado_por_empleado_id`, `intervencion_inicio_en`, `validado_en`, `origen_intervencion` (migración 024, batch). Origen derivado siempre por el backend (`gate`, `muestreo`, `rederivacion`; `completado_manual` reservado sin escritor); el cliente solo envía `intervencion_inicio_en`. Métrica backend `tasa_intervencion_backend`; export pseudonimizado `evaluation/data/campana/intervenciones.csv` para c-167. |
| Plan de campaña | c-166 | `evaluation/data/campana/plan_campana.csv` con `id_caso, posicion, mitad, brazo_primero, modo, seed`; contrabalanceo de condición (qué brazo va primero por caso); los harnesses reciben `--plan`, escriben sidecar propio por corrida y abortan si apuntan a los archivos versionados. |
| Out-of-sample | c-166 / c-167 | c-166 genera `predicciones_independiente.json` con `classifier_version`, `commit` y `pines`, verifica no solape y registra `pines_in_sample` en el README; c-167 compara versión y pines (commit solo si ambos lo traen) y produce el reporte in-sample / out-of-sample. |
| Kappa y memo | c-167 / c-169 | Kappa de Cohen nuevo (E1 vs E2, 5 clases, etiqueta primaria) con IC de Fleiss-Cohen-Everitt 1969 y bootstrap (B = 2000, semilla 20261021). El 0,87 original queda `vigente (sin IC)`; el nuevo entra como valor distinto. Sub-hipótesis 2 con cuatro desenlaces: compatible, refutada, no concluyente, no contrastada por registro incompleto. |

### Decisiones tomadas durante la enmienda que conviene que Lucas confirme

- Denominación en la tesis: "campaña complementaria de medición" (el Anexo A y el cronograma ya llaman "campañas de medición" a las corridas de 2026).
- El efecto de condición se mide entre grupos independientes (100 manual-primero vs 100 automatizado-primero, MDE d ≈ 0,43); el MDE pareado dz ≈ 0,21 no aplica a ese análisis.
- Los pines in-sample de v9 salen de `openspec/config.yaml` y del Anexo B, no del cache de predicciones (que no los registra); el commit in-sample se declara no registrado.
- La exactitud de v9 contra la referencia nueva es un número nuevo y rotulado; no reemplaza el 73,5 %.

### Pendientes administrativos

- Registrar c-165 a c-169 como FASE 52 en `CHANGES.md` (el requisito de coherencia del índice lo exige al archivar; conviene hacerlo ya).
- Completar el `## Purpose` de la capability nueva tras el primer archive.
- El archivo `docs/Tesis/Correcciones/mensaje-para-lucas-pr-63.md` es un resto de la sesión anterior (PR 63 ya mergeado).
