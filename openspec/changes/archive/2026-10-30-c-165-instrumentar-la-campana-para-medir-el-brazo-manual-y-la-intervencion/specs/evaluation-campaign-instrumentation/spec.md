## Purpose

Define el instrumento y el protocolo de la campana de medicion: la captura de la clasificacion del brazo manual sobre la planilla unica de etiquetado, los sujetos y la referencia contra la que se mide, la tasa de intervencion humana registrada por el backend y el export pseudonimizado que consume el analisis, de modo que ambos datasets sean producibles, registrados y verificables sin escribir sobre los artefactos congelados.

## ADDED Requirements

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
