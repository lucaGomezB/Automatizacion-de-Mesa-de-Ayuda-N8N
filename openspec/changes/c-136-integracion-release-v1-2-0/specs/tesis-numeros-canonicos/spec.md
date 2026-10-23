## ADDED Requirements

### Requirement: Consolidacion de los valores de la familia de correcciones del dictamen v10 antes de la release

Antes de etiquetar la release que cierra el dictamen CONEAU del 2026-10-22 sobre la tesis v10 / `v1.1.0`, el memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL registrar cada valor numerico de resultado que la familia c-125..c-137 (c-125 a c-135 y c-137) incorpore a la tesis (por ejemplo, exactitud por etapa con su intervalo de Wilson, exactitud por canal, exactitud laxa con su intervalo, contraste pareado entre etapas, tiempos manuales por canal y contraste intra-canal, valor p unilateral, d_z, distribucion del universo por sector, escenarios del balance neto, valores de sensibilidad fuera de muestra y la designacion de la metrica primaria), cada uno con su procedencia (archivo y linea de origen) y su estado (`vigente`, `retirado` o `condicional`). Ningun numero de resultado agregado a `sections/*.tex` por la familia MUST quedar sin fila en el memo. Todo valor que no pueda derivarse de las fuentes permitidas (por ejemplo, por caches de predicciones no recuperadas o por una corrida paga no autorizada) SHALL declararse en "Decisiones no resolubles" con su condicion de reversibilidad, y la tesis MUST NOT presentarlo como resultado medido. Las secciones del memo SHALL tener numeracion unica y consecutiva, asignada por orden de aplicacion de los changes, y toda remision cruzada entre secciones SHALL resolver. Ninguna corrida de sensibilidad MUST reemplazar un valor canonico vigente. El encabezado del memo SHALL identificar la version de trabajo (v10), la release (`v1.2.0`) y la fecha de consolidacion. `evaluation/report.md` y `evaluation/report_sensibilidad_ajustes.md` SHALL coincidir con los valores del memo que reportan.

#### Scenario: Valores de la familia registrados con procedencia

- **WHEN** se recorre el memo despues de aplicar la familia
- **THEN** cada valor de resultado introducido por c-125..c-135 y c-137 figura con archivo y linea de origen y con un estado en `{vigente, retirado, condicional}`
- **AND** la linea indicada existe en el archivo referenciado

#### Scenario: Tesis sin numeros huerfanos

- **WHEN** se comparan los numeros de resultado agregados por la familia en `sections/*.tex` (diff entre `v1.1.1` y el arbol del commit C1) contra el memo
- **THEN** cada uno figura en el memo como `vigente` o `condicional`
- **AND** ninguno existe solo en la tesis

#### Scenario: Valores sin procedencia declarados

- **WHEN** un valor previsto por la familia no puede derivarse de `evaluation/`, `data/` ni de las caches de predicciones disponibles, o depende de una corrida paga no autorizada
- **THEN** el memo lo declara en "Decisiones no resolubles" con la decision editorial y la condicion bajo la cual se revisaria
- **AND** la tesis no lo presenta como resultado medido

#### Scenario: Numeracion unica de las secciones del memo

- **WHEN** se listan los encabezados de la Seccion 3 del memo despues de aplicar la familia
- **THEN** cada numero `3.N` aparece una sola vez y la secuencia es consecutiva
- **AND** toda nota del tipo "ver seccion 3.N" del memo, del registro y de los artefactos archivados de la familia apunta a una seccion existente con el contenido citado

#### Scenario: Valores canonicos vigentes sin cambios por la sensibilidad

- **WHEN** se compara el memo con su estado previo a la aplicacion de c-137
- **THEN** ningun valor `vigente` cambio por efecto de una corrida de sensibilidad
- **AND** los valores de sensibilidad figuran en una seccion propia, con notas cruzadas en las filas de `97/131` y `0,7405`/`0,6769`

#### Scenario: Encabezado del memo actualizado

- **WHEN** se lee el encabezado del memo en el commit etiquetado
- **THEN** identifica la version de trabajo v10, la release `v1.2.0` y la fecha de consolidacion
- **AND** conserva el SHA-256 del corpus `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`

#### Scenario: Reportes de evaluacion coherentes con el memo

- **WHEN** se comparan los valores de `evaluation/report.md` y de `evaluation/report_sensibilidad_ajustes.md` con los valores del memo
- **THEN** coinciden en todos los valores que ambos reportan
- **AND** `evaluation/report.md` conserva sus secciones de normalidad (Shapiro-Wilk), Wilcoxon y desglose por canal
