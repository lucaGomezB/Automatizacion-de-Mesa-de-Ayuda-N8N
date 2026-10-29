## Purpose

Extiende el instrumento y los protocolos de la campana de campo (introducidos por c-165
y ampliados por c-166) con una plantilla y un protocolo de doble etiquetado independiente
que produzcan la tabla primaria de acuerdo observado/esperado por caso, hoy inexistente,
de modo que el coeficiente kappa y su intervalo de confianza sean computables.

## ADDED Requirements

### Requirement: ECM-008 — Plantilla de doble etiquetado con campos minimos

El proyecto SHALL proveer una plantilla versionada (CSV o JSON) para registrar el doble
etiquetado, con al menos los campos `id_caso`, `id_etiquetador`, `sector_asignado`,
`sectores_adicionales` y `timestamp`. La plantilla SHALL admitir dos registros
independientes (dos etiquetadores) por caso y MUST NOT requerir conexion a servicios
externos para registrarse. Los valores de sector MUST ser exactamente las cinco cadenas
canonicas (sin acentos, sensibilidad a mayusculas) y MUST NOT incluir datos personales:
solo descripciones pseudonimizadas.

#### Scenario: Plantilla registra dos etiquetados por caso

- **WHEN** se usa la plantilla para un caso con dos etiquetadores distintos
- **THEN** la plantilla permite dos registros con distinto `id_etiquetador` para el mismo `id_caso`, cada uno con su sector y timestamp

#### Scenario: Plantilla admite las cinco cadenas canonicas

- **WHEN** un etiquetador registra un sector
- **THEN** los valores validos son exactamente `Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos` y `Sistemas`

#### Scenario: Plantilla sin datos personales

- **WHEN** se inspecciona la plantilla y sus campos
- **THEN** no expone identificadores ni descripciones con datos personales, solo el `id_caso` pseudonimizado

### Requirement: ECM-009 — Validacion offline del doble etiquetado

El proyecto SHALL proveer una herramienta offline que, sobre un archivo de doble
etiquetado, verifique: (a) al menos dos etiquetadores independientes por caso, (b)
cobertura completa del conjunto de casos objetivo sin celdas faltantes, (c) ausencia de
duplicados `(id_caso, id_etiquetador)`, y (d) que cada sector pertenezca a las cadenas
canonicas. La herramienta MUST fallar de forma accionable (identificando el caso o celda)
cuando alguna condicion no se cumple, y MUST operar sin red ni servicios externos.

#### Scenario: Validacion bloquea cobertura incompleta

- **WHEN** un caso del conjunto objetivo no tiene al menos dos etiquetados
- **THEN** la validacion falla identificando el `id_caso` faltante y no declara completa la tabla

#### Scenario: Validacion bloquea etiquetador duplicado

- **WHEN** existen dos registros con el mismo `(id_caso, id_etiquetador)`
- **THEN** la validacion falla identificando el par duplicado

#### Scenario: Validacion bloquea sector fuera del conjunto canonico

- **WHEN** un registro usa un sector que no pertenece a las cinco cadenas canonicas (por ejemplo con acento o distinta capitalizacion)
- **THEN** la validacion falla identificando el registro y el valor invalido

#### Scenario: Tabla completa y valida habilita el consumo

- **WHEN** todos los casos objetivo tienen dos etiquetadores, sin duplicados ni sectores invalidos
- **THEN** la validacion pasa y la tabla queda disponible para el calculo de kappa e IC

### Requirement: ECM-010 — Protocolo de doble etiquetado independiente y ruta de recuperacion

El proyecto SHALL incluir un runbook versionado que defina: elegibilidad de los
etiquetadores, cegado (los etiquetadores MUST NOT ver el consenso `sector_asignado` ni
las etiquetas del otro), uso del mismo codebook que el etiquetado original, tamano de
muestra (re-etiquetar los 200 casos o un subconjunto con justificacion) y criterios de
aceptacion (cobertura completa, sin celdas faltantes). El runbook SHALL describir una
ruta de recuperacion opcional si reaparece data parcial por etiquetador original; el
camino por defecto SHALL ser el re-etiquetado. El runbook MUST ser ejecutable sin
conocimiento tacito y MUST NOT depender de datos de campo ya recolectados.

#### Scenario: El runbook define cegado y elegibilidad

- **WHEN** se lee el runbook de doble etiquetado
- **THEN** especifica que los etiquetadores no ven el consenso ni entre si, y las condiciones de elegibilidad

#### Scenario: El runbook define tamano de muestra y aceptacion

- **WHEN** un autor consulta cuantos casos re-etiquetar y como aceptar el resultado
- **THEN** el runbook fija re-etiquetar los 200 casos (o un subconjunto justificado) y los criterios de cobertura completa sin celdas faltantes

#### Scenario: Ruta de recuperacion documentada

- **WHEN** reaparece data parcial por etiquetador original
- **THEN** el runbook describe como validarla y registrarla, manteniendo el re-etiquetado como camino por defecto
