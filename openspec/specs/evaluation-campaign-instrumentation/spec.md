# evaluation-campaign-instrumentation Specification

## Purpose
Define el instrumento y el protocolo de la campana de medicion: la captura de la clasificacion del brazo manual sobre la planilla unica de etiquetado, los sujetos y la referencia contra la que se mide, la tasa de intervencion humana registrada por el backend y el export pseudonimizado que consume el analisis, de modo que ambos datasets sean producibles, registrados y verificables sin escribir sobre los artefactos congelados.

## Requirements

### Requirement: ECM-001 — Instrumento de captura del brazo manual

El proyecto SHALL registrar la clasificacion del BRAZO MANUAL en la planilla unica de etiquetado definida por ECM-008 (`evaluation/data/plantilla_etiquetado.csv`, columnas `id_caso, id_etiquetador, tarea, sector_etiquetado, sectores_adicionales_etiquetados, inicio, timestamp`), con `tarea = brazo_manual` y operadores fijos con alias `O1`, `O2`, donde cada `id_caso` del plan SHALL ser clasificado por AL MENOS UN operador (el reparto por mitades segun el plan de campana es valido y la doble cobertura de una submuestra es opcional) con un maximo de un registro por `(id_caso, id_etiquetador)`, y MUST validarla con el validador unico de ECM-009 (`evaluation/doble_etiquetado.py::validar_doble_etiquetado`) sin definir un esquema ni un validador propios. Las cadenas de sector MUST importarse de `evaluation.corpus.SECTORES_CANONICOS`. Los operadores `O*` MUST ser personas distintas de los etiquetadores `E*` del doble etiquetado, de los dos analistas que fijaron el consenso original (`sector_asignado` del corpus) y de los autores, verificado por el seudonimo `persona` del registro de sujetos `evaluation/data/campana/registro_sujetos.csv` (`alias, rol, persona`), y MUST NOT ver la prediccion ni el consenso. La referencia contra la que se mide el brazo manual SHALL ser el consenso del doble etiquetado nuevo de ECM-008 cuando ambos etiquetadores coinciden; los casos discordantes MUST reportarse aparte y no medirse. Los operadores SHALL seguir la `posicion` y el `brazo_primero` del plan de campana (`evaluation/data/campana/plan_campana.csv`) El operador SHALL registrar `inicio` (ISO-8601) al tomar el caso y `timestamp` al asignar el sector, que es el fin de la clasificacion del caso; para `tarea = brazo_manual` ambos MUST estar presentes y reemplazan cualquier cronometro aparte. `inicio` SHALL permitir reconstruir la posicion real de cada caso y sus desvios respecto del plan. El instrumento MUST NOT almacenar PII en claro ni acoplar la captura a la base de datos de produccion.

#### Scenario: Registro por operador con tarea brazo_manual

- **WHEN** el operador `O1` clasifica un caso del plan de campana
- **THEN** la planilla contiene una fila con el `id_caso` del corpus, `id_etiquetador = O1`, `tarea = brazo_manual`, un `sector_etiquetado` canonico, un `inicio` registrado al tomar el caso y un `timestamp` registrado al asignar el sector, ambos ISO-8601 con zona, y la planilla completa valida con `validar_doble_etiquetado`

#### Scenario: Reparto por mitades aceptado

- **WHEN** `O1` clasifica la primera mitad del plan y `O2` la segunda, y un caso de la submuestra lo clasifican ambos
- **THEN** la planilla valida con `tarea = brazo_manual`

#### Scenario: Fila de brazo manual sin inicio rechazada

- **WHEN** una fila con `tarea = brazo_manual` no tiene `inicio`
- **THEN** la validacion de la planilla falla e informa la fila

#### Scenario: Caso sin operador o registro duplicado rechazado

- **WHEN** un `id_caso` del plan no tiene ningun registro de operador, o un mismo `(id_caso, id_etiquetador)` aparece dos veces
- **THEN** la validacion de la planilla falla e informa el caso

#### Scenario: Operador distinto de etiquetadores y analistas

- **WHEN** se registran los operadores `O1`/`O2` en `registro_sujetos.csv`
- **THEN** la `persona` de ningun operador `O*` aparece con rol de etiquetador `E*`, de analista del consenso original ni de autor, y un solape por `persona` se reporta como incumplimiento del protocolo

#### Scenario: Referencia igual al consenso del doble etiquetado nuevo

- **WHEN** los dos etiquetadores del doble etiquetado asignan el mismo sector a un caso
- **THEN** ese sector es la referencia contra la que se compara la clasificacion de cada operador del brazo manual, y no el `sector_asignado` original del corpus

#### Scenario: Caso discordante reportado aparte

- **WHEN** los dos etiquetadores del doble etiquetado asignan sectores distintos a un caso
- **THEN** el caso no entra en la medicion de exactitud del brazo manual y se reporta en un conteo aparte

#### Scenario: Posicion real reconstruida contra el plan

- **WHEN** un operador clasifico los casos en un orden distinto del de `plan_campana.csv`
- **THEN** la posicion real reconstruida desde `inicio` difiere de la planeada y el caso se informa como desvio con ambas posiciones

### Requirement: ECM-002 — Protocolo de campana registrado en el repositorio

El proyecto SHALL incluir el runbook versionado `docs/campana-medicion/runbook-brazo-manual-e-intervencion.md` que defina: el registro de los operadores en `evaluation/data/campana/registro_sujetos.csv` con su alias, rol y `persona` (sin nombres en el repositorio) y la exigencia de independencia de ECM-001 verificada por `persona`; el reparto de casos entre operadores; el minimo de casos, fijado antes de la campana y justificado; el uso del plan de campana por caso; el instrumento de cada dataset (la planilla de ECM-008 para el brazo manual; el registro de intervencion y su export para la intervencion); y el criterio de aceptacion/verificacion de cada dataset. Los datos producidos SHALL ubicarse en `evaluation/data/campana/` sin PII, con su SHA-256 en un README. El runbook MUST prohibir escribir sobre `data/corpus_evaluacion_pseudonimizado.json`, `data/corpus_resultados*.json`, `evaluation/predicciones.json` y los sidecars versionados como evidencia, y MUST ser ejecutable por los autores sin depender de conocimiento tacito.

#### Scenario: El protocolo define sujetos casos e independencia

- **WHEN** se lee el runbook de campana
- **THEN** especifica el registro de los operadores en `registro_sujetos.csv` con alias, rol y `persona`, el reparto de casos entre `O1` y `O2`, la exigencia de que sean personas distintas entre si, de los analistas del consenso original y de los autores, y el minimo de casos con su justificacion

#### Scenario: El protocolo remite al plan de campana

- **WHEN** un operador inicia su sesion del brazo manual
- **THEN** el runbook le indica seguir la `posicion` y el `brazo_primero` de `plan_campana.csv` y registrar en la planilla `inicio` al tomar cada caso y `timestamp` al asignar el sector, sin cronometro aparte

#### Scenario: El protocolo define aceptacion y verificacion

- **WHEN** se completa la campana
- **THEN** el runbook provee para cada dataset un criterio explicito de aceptacion (planilla valida, desvios de posicion reportados, export sin PII, legados y vinculos faltantes declarados) y el registro de su SHA-256 en `evaluation/data/campana/README.md`

#### Scenario: Archivos congelados no se escriben

- **WHEN** se ejecuta cualquier paso del runbook
- **THEN** ningun paso escribe sobre el corpus pseudonimizado, los resultados del corpus, `evaluation/predicciones.json` ni los sidecars versionados como evidencia

### Requirement: ECM-003 — Tasa de intervencion registrada por el backend y export pseudonimizado

El sistema SHALL calcular `tasa_intervencion_backend` sobre la cohorte de logs de clasificacion creados en un rango temporal: el numerador cuenta los logs de la cohorte con `validado_en` no nulo y el denominador los logs de la cohorte, EXCLUIDOS de ambos los logs en estado `intervencion_legada_sin_metadatos` (sector validado sin `validado_en`), cuya cantidad MUST declararse. Una confirmacion del sector predicho SHALL contar como intervencion. La metrica SHALL desglosarse por `origen_intervencion` y por cambio de sector, MUST NOT confundir un caso marcado `requiere_revision_humana` no intervenido con uno intervenido, MUST ser reproducible y SHALL exponerse en el resumen de estadisticas junto a (no en lugar de) `tasa_revision_humana`. El proyecto SHALL proveer un export pseudonimizado que produzca `evaluation/data/campana/intervenciones.csv` con las columnas `id_caso, incidente_id, log_id, origen_intervencion, intervencion_inicio_en, validado_en, duracion_s, sector_predicho, sector_validado, cambio_sector, actor_alias`, donde `id_caso` se vincula por `incidente_id` desde el sidecar de la corrida y `actor_alias` es un alias derivado con clave; el export MUST NOT contener nombre, email, telefono, legajo ni el id del empleado en claro.

#### Scenario: La tasa cuenta solo logs con validado_en

- **WHEN** se calcula la tasa para un rango con un log validado y un log marcado `requiere_revision_humana` todavia no validado
- **THEN** solo el log con `validado_en` no nulo cuenta en el numerador y ambos cuentan en el denominador

#### Scenario: Una confirmacion sin cambio de sector cuenta

- **WHEN** un operador valida un log confirmando el sector predicho
- **THEN** el log cuenta como intervencion y aparece en el desglose con cambio de sector falso

#### Scenario: Desglose por origen

- **WHEN** en el rango hay intervenciones con origen `gate`, `muestreo` y `rederivacion`
- **THEN** el resumen informa la cantidad por cada valor del vocabulario, con cero para `completado_manual`

#### Scenario: Legados excluidos y declarados

- **WHEN** la cohorte contiene un log con sector validado y `validado_en` nulo, anterior a la migracion de intervencion
- **THEN** ese log no entra ni al numerador ni al denominador y el resumen informa la cantidad de legados excluidos

#### Scenario: La metrica es reproducible

- **WHEN** se recalcula la tasa sobre el mismo rango y los mismos datos
- **THEN** el valor resultante es identico

#### Scenario: Export sin PII con las columnas acordadas

- **WHEN** se ejecuta el export sobre una cohorte con intervenciones y el sidecar de la corrida
- **THEN** `intervenciones.csv` tiene exactamente las columnas acordadas en ese orden, `id_caso` vacio solo cuando el `incidente_id` no figura en el sidecar, `duracion_s` vacio cuando falta el inicio, y ninguna celda contiene nombre, email, telefono, legajo ni el id del empleado en claro

#### Scenario: El export no escribe sobre archivos congelados

- **WHEN** se invoca el export con una salida que apunta al corpus pseudonimizado, a los resultados del corpus o a `evaluation/predicciones.json`
- **THEN** el export se niega a escribir y termina con error sin modificar el archivo

### Requirement: ECM-004 — Plan de campaña por caso y contrabalanceo de condición

El proyecto SHALL proveer en `evaluation/plan_campana.py` una función pura `generar_plan_campana(casos, modo, seed)` que componga `ordenar_casos(casos, modo, seed)` (modos `directo`, `inverso`, `alternado`, `aleatorio`) y asigne a cada caso `id_caso`, `posicion` (1..n), `mitad` (1 o 2), `brazo_primero` (`manual` o `automatizado`), `modo` y `seed`. El contrabalanceo SHALL ser de CONDICIÓN: dentro de cada mitad, la cantidad de casos `manual`-primero y `automatizado`-primero MUST diferir en a lo sumo 1. Con N impar, la primera mitad SHALL tener ⌊n/2⌋ casos y la segunda ⌈n/2⌉. El modo `aleatorio` MUST requerir semilla y, con la misma semilla y los mismos casos, MUST producir el mismo plan. El plan SHALL exportarse a CSV UTF-8 con separador `,` (`evaluation/data/campana/plan_campana.csv`). Los harnesses `scripts/corpus_ingest/ingest_via_n8n.py` y `scripts/corpus_ingest/ingest_corpus.py` SHALL aceptar `--plan <csv>` y enviar en el orden de `posicion`, y `--orden/--seed` como atajo que genera el plan y lo escribe junto al sidecar; `scripts/corpus_ingest/ingest_telefonia_corpus.py` no ingesta y, con `--plan`, SHALL limitarse a copiar `posicion`, `mitad` y `brazo_primero` al sidecar. `CaseResult` y `CorpusResult` SHALL recibir al final, con default `None`, los campos `orden`, `posicion`, `mitad`, `brazo_primero` e `id_corrida`. `--limit` SHALL aplicarse antes del orden. Ninguna de estas operaciones MUST requerir servicios externos para ser verificada.

#### Scenario: Plan balanceado por mitad

- **WHEN** se genera el plan de 200 casos con cualquier modo
- **THEN** cada mitad tiene 100 casos, 50 con `brazo_primero` igual a `manual` y 50 con `automatizado`, y `verificar_balance` pasa

#### Scenario: N impar documentado

- **WHEN** se genera el plan de 7 casos
- **THEN** la mitad 1 tiene 3 casos y la mitad 2 tiene 4, y en cada mitad la diferencia entre `manual` y `automatizado` es a lo sumo 1

#### Scenario: Plan reproducible con semilla

- **WHEN** se genera dos veces el plan con `modo` `aleatorio` y la misma semilla sobre los mismos casos
- **THEN** ambos planes son idénticos fila por fila y cada fila registra la semilla

#### Scenario: Aleatorio sin semilla falla

- **WHEN** se pide un plan o un harness con `aleatorio` sin semilla
- **THEN** la operación termina con un error que indica pasar `--seed` y no se genera plan ni se envía ningún caso

#### Scenario: El límite se aplica antes del orden

- **WHEN** un harness corre con `--orden inverso --limit 3`
- **THEN** procesa el reverso de los tres primeros casos del corpus, no los tres últimos

#### Scenario: El harness sigue el plan y registra la asignación

- **WHEN** `ingest_via_n8n.py` o `ingest_corpus.py` corren con `--plan` e `--id-corrida`
- **THEN** envían los casos en orden de `posicion` y cada entrada del sidecar registra `posicion`, `mitad`, `brazo_primero`, `orden` e `id_corrida`

#### Scenario: Telefonía copia el plan sin ingestar

- **WHEN** `ingest_telefonia_corpus.py` corre con `--plan`
- **THEN** recupera las mediciones por `corpus_case_id` como antes y copia `posicion`, `mitad` y `brazo_primero` del plan al sidecar, sin decidir el orden de las llamadas

#### Scenario: Sidecars históricos siguen válidos

- **WHEN** se lee o se mergea un sidecar previo que no tiene los campos nuevos
- **THEN** se procesa sin errores y los campos ausentes valen `None`

### Requirement: ECM-005 — Protocolo de campaña contrabalanceada registrado

El proyecto SHALL incluir el runbook versionado `docs/campana-medicion/runbook-campana-contrabalanceada.md` que defina cómo se genera y verifica el plan, cómo se reparten los casos por `brazo_primero` dentro de cada mitad, cómo el operador manual sigue el plan fuera del repositorio, qué registra en la planilla de c-168 con `tarea` igual a `brazo_manual` (`inicio` en ISO-8601 al tomar el caso y `timestamp` al asignar el sector, de modo que `timestamp - inicio` es la duración por caso), con qué flags se corren los harnesses, y un criterio de aceptación explícito: contrabalanceo efectivo registrado por caso. Los operadores del brazo manual MUST ser distintos de los etiquetadores del doble etiquetado, de los dos analistas originales y de los autores. El runbook MUST NOT depender de datos de campo ya recolectados y SHALL delegar la estimación del efecto de orden a c-167.

#### Scenario: El operador sigue el plan

- **WHEN** un operador ejecuta el brazo manual según el runbook
- **THEN** procesa los casos en orden de `posicion`, en el turno que indica `brazo_primero`, y registra cada caso en la planilla con `tarea` igual a `brazo_manual`, `inicio` al tomar el caso y `timestamp` al asignar el sector

#### Scenario: Contrabalanceo efectivo registrado por caso

- **WHEN** se cierra la campaña
- **THEN** cada caso tiene `posicion`, `mitad` y `brazo_primero` en el sidecar y su registro manual, la asignación realizada coincide con el plan y `verificar_balance` pasa

#### Scenario: Estimación del efecto de orden delegada a c-167

- **WHEN** un autor consulta cómo estimar el efecto de orden
- **THEN** el runbook remite al análisis de c-167, que parea por caso las mediciones de las distintas corridas y toma la posición del plan

### Requirement: ECM-006 — Corpus independiente sin solape con el corpus de ajuste

El proyecto SHALL proveer `evaluation/no_solape.py::verificar_no_solape(ajuste, candidato)` y el runbook `docs/campana-medicion/runbook-corpus-independiente.md`. Los ids del corpus independiente MUST llevar el prefijo `I` (`I001..`). La verificación MUST fallar de forma accionable, nombrando el caso, si un id del candidato no tiene el prefijo, si un id aparece en ambos corpus o si coincide el SHA-256 de la descripción normalizada (NFKC, minúsculas, espacios colapsados); la similitud Jaccard de tokens por encima de un umbral SHALL reportarse como advertencia. La verificación SHALL declarar que no detecta paráfrasis y MUST ejecutarse como paso previo obligatorio antes de clasificar el corpus independiente. El corpus independiente SHALL pseudonimizarse con el mismo protocolo que el de ajuste y doble-etiquetarse con la plantilla y el validador de c-168, y SHALL clasificarse con el clasificador CONGELADO (`classifier_version` y commit iguales a los del in-sample), sin recalibrar tau, prompt ni vocabulario después de ver el corpus.

#### Scenario: Prefijo obligatorio

- **WHEN** un caso del corpus candidato tiene un id sin el prefijo `I`
- **THEN** la verificación falla y nombra ese caso

#### Scenario: Mismo caso con otro id bloquea la corrida

- **WHEN** un caso del candidato tiene un id nuevo pero su descripción normalizada coincide con la de un caso de ajuste
- **THEN** la verificación falla identificando ambos casos y no se clasifica el corpus independiente

#### Scenario: Corpus disjunto habilita la medición

- **WHEN** el candidato no comparte ids ni descripciones normalizadas con el corpus de ajuste
- **THEN** la verificación pasa, devuelve las advertencias de similitud si se pidió umbral, y la clasificación puede proceder

#### Scenario: Mismo protocolo y clasificador congelado

- **WHEN** se prepara y clasifica el corpus independiente según el runbook
- **THEN** se aplican la misma pseudonimización, la plantilla y el validador de c-168 y el clasificador con el mismo `classifier_version` y commit que el in-sample, sin recalibración posterior

### Requirement: ECM-007 — Protección de los artefactos congelados en la campaña y en el corpus independiente

Las corridas de campaña y la clasificación del corpus independiente MUST NOT escribir sobre los artefactos de la v9. Los harnesses SHALL abortar con error accionable, antes de enviar nada, si con `--plan` u `--orden` el `--json` o el `--sidecar` apuntan a `data/corpus_evaluacion_pseudonimizado.json` o a cualquier `data/corpus_resultados*.json`; con `--plan`, `--sidecar` SHALL ser obligatorio y propio de la corrida. `evaluation/run_evaluation.py` SHALL aceptar `--corpus`, `--predicciones` y `--reporte`; si `--corpus` no es el canónico, `--predicciones` y `--reporte` SHALL ser obligatorios y el runner MUST abortar si apuntan a `evaluation/predicciones.json` o `evaluation/report.md`. Las predicciones del corpus independiente SHALL guardarse separadas (`evaluation/data/campana/predicciones_independiente.json`) y su `cache_meta` SHALL incluir, además de `corpus_hash`, `corpus_count`, `classifier_version` y `generated_at`, los campos `commit` (hash corto de `HEAD` al generar) y `pines` (versión de `google-genai` y modelo); si el commit o los pines no pueden obtenerse, la corrida MUST fallar antes de escribir. El README de `evaluation/data/campana/` SHALL registrar `classifier_version`, `commit_in_sample` y `pines_in_sample` (versión de google-genai y modelo de v9, citando `openspec/config.yaml` `stack.inference` y la Tabla de configuración evaluada del Anexo B) de la corrida in-sample de referencia; como la copia congelada de v9 no registró commit, la comparabilidad SHALL verificarse por `classifier_version` y `pines` idénticos, y el commit es obligatorio solo en el cache independiente. El reporte out-of-sample es de c-167.

#### Scenario: Abort por json congelado

- **WHEN** un harness corre con `--plan` y `--json` apunta a `data/corpus_evaluacion_pseudonimizado.json`, o lo deja en su default
- **THEN** termina con código distinto de cero, nombra el archivo y la ruta de campaña a usar, y no envía ningún caso

#### Scenario: Abort por sidecar versionado

- **WHEN** un harness corre con `--plan` y `--sidecar` apunta a un `data/corpus_resultados*.json`
- **THEN** termina con error accionable sin enviar ni escribir nada

#### Scenario: Abort por predicciones o reporte canónicos

- **WHEN** `run_evaluation.py` corre con un `--corpus` no canónico y `--predicciones` apunta a `evaluation/predicciones.json` o `--reporte` a `evaluation/report.md`, o alguno de los dos falta
- **THEN** aborta antes de construir el clasificador y no modifica ningún archivo

#### Scenario: Predicciones independientes separadas

- **WHEN** se clasifica el corpus independiente con rutas propias
- **THEN** las predicciones quedan en `evaluation/data/campana/predicciones_independiente.json` y `evaluation/predicciones.json` y `evaluation/report.md` no cambian

#### Scenario: Procedencia completa del cache independiente

- **WHEN** se clasifica el corpus independiente con rutas propias
- **THEN** el `cache_meta` de `predicciones_independiente.json` trae `classifier_version`, `commit` y `pines` además de `corpus_hash`, `corpus_count` y `generated_at`

#### Scenario: Cache sin commit falla antes de escribir

- **WHEN** al clasificar el corpus independiente no se puede obtener el commit o los pines
- **THEN** la corrida termina con error accionable antes de invocar al clasificador y no escribe el archivo de predicciones

#### Scenario: Sin flags nuevos la conducta no cambia

- **WHEN** los harnesses o `run_evaluation.py` corren sin los flags nuevos
- **THEN** se comportan exactamente como antes de este change
