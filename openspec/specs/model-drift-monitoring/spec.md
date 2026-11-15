# model-drift-monitoring Specification

## Purpose
Define un regimen de monitoreo continuo de las metricas de clasificacion para gestionar como riesgo operativo las limitaciones de la dependencia de un servicio externo de inferencia y de una version especifica de modelo. El regimen se apoya en un conjunto canario fijo, un job de reevaluacion offline que recalcula las metricas y detecta deriva contra una linea de base congelada, umbrales de alerta y la documentacion del fallback. Es una senal operativa: no mide de nuevo la tesis ni modifica ningun numero canonico ni la evidencia congelada.

## Requirements

### Requirement: Conjunto canario fijo y disjunto del corpus de ajuste

El sistema SHALL definir un conjunto canario fijo y versionado, con su composicion estable (casos, sectores, canales) y su huella criptografica registrada, de modo que una deriva sea medible entre corridas. El conjunto canario SHALL ser disjunto del corpus usado para ajustar o calibrar el clasificador y MUST NOT usarse para ajustar, calibrar ni seleccionar el vocabulario, el prompt ni el punto de operacion. El conjunto canario SHALL acompanarse de una linea de base congelada de las metricas de clasificacion sobre esos mismos casos.

#### Scenario: El canario es fijo y versionado

- **WHEN** se versiona el conjunto canario
- **THEN** su composicion y su huella criptografica quedan registradas y son estables entre corridas

#### Scenario: El canario es disjunto del corpus de ajuste

- **WHEN** se compara el conjunto canario con el corpus usado para ajustar el clasificador
- **THEN** no hay solapamiento de casos y ningun elemento del canario intervino en el ajuste

#### Scenario: El canario no se usa para ajustar

- **WHEN** se inspecciona el procedimiento de ajuste y calibracion
- **THEN** ninguna decision de vocabulario, prompt o punto de operacion se deriva del conjunto canario

### Requirement: Job de reevaluacion periodica offline por defecto

El sistema SHALL ofrecer un job que recalcule las metricas de clasificacion sobre el conjunto canario con las mismas definiciones del framework de evaluacion (exactitud estricta, F1 macro, metricas por sector y conteo por etapa). El job SHALL ser offline por defecto: SHALL reproducir la linea de base congelada a partir de los artefactos versionados sin invocar al proveedor de inferencia. Cuando el job invoque al proveedor para obtener predicciones frescas, SHALL exigir confirmacion explicita del operador y MUST NOT ejecutarse sin ella. El job SHALL ser determinista y su salida SHALL escribirse en rutas nuevas y fechadas.

#### Scenario: El job reproduce la linea de base sin invocar al proveedor

- **WHEN** el job se ejecuta en modo offline con los artefactos versionados disponibles
- **THEN** reproduce las metricas de la linea de base congelada y no realiza ninguna invocacion al proveedor

#### Scenario: La corrida paga exige confirmacion

- **WHEN** el job se ejecuta sin la confirmacion explicita y necesita predicciones frescas del proveedor
- **THEN** aborta con un error claro sin invocar al proveedor

#### Scenario: El job es determinista

- **WHEN** el job se ejecuta dos veces sobre las mismas entradas
- **THEN** sus salidas son identicas byte a byte

### Requirement: Deteccion de deriva contra la linea de base

El job SHALL comparar las metricas recalculadas del canario contra la linea de base congelada y SHALL declarar deriva cuando una metrica monitoreada se degrade mas alla de una tolerancia configurable. La deteccion SHALL distinguir un cambio de identidad del proveedor o de la version de modelo de un cambio de las metricas con identidad estable, y ambos casos SHALL reportarse de forma separada. Cuando no haya cambio de identidad ni degradacion por encima de la tolerancia, el job SHALL declarar ausencia de deriva.

#### Scenario: Una degradacion por encima de la tolerancia se reporta como deriva

- **WHEN** una metrica monitoreada cae por debajo de su linea de base mas alla de la tolerancia
- **THEN** el job declara deriva e identifica la metrica y la magnitud de la caida

#### Scenario: Sin cambio no hay deriva

- **WHEN** las metricas recalculadas no se degradan mas alla de la tolerancia y la identidad del proveedor y del modelo no cambio
- **THEN** el job declara ausencia de deriva

#### Scenario: El cambio de version se distingue del cambio de metrica

- **WHEN** la identidad del proveedor o de la version de modelo difiere de la de la linea de base
- **THEN** el job lo reporta como cambio de identidad, separado de cualquier cambio de las metricas

### Requirement: Umbrales de alerta configurables y fallback documentado

El sistema SHALL definir umbrales explicitos (un piso) por metrica monitoreada, configurables sin recompilar y con valores por defecto derivados de la linea de base congelada. Cuando una metrica cae por debajo de su piso, el job SHALL emitir una alerta que identifique la metrica, su valor, su piso y la corrida. La alerta SHALL documentar el fallback operativo vigente: ante la indisponibilidad del servicio de inferencia, la cascada degrada al filtro deterministico con revision humana, conforme a `classification-resilience`, y SHALL indicar el criterio para restablecer el servicio. La alerta MUST NOT exigir ni provocar un cambio automatico del clasificador.

#### Scenario: Una metrica bajo su piso emite alerta

- **WHEN** una metrica monitoreada queda por debajo de su piso configurado
- **THEN** el job emite una alerta con la metrica, su valor, su piso y la corrida

#### Scenario: La alerta documenta el fallback y el criterio de restablecimiento

- **WHEN** se emite una alerta por degradacion del servicio de inferencia
- **THEN** la alerta remite al fallback deterministico con revision humana y declara el criterio para restablecer el servicio

#### Scenario: Los umbrales se ajustan por configuracion

- **WHEN** se define un piso distinto por variable de entorno
- **THEN** el job usa ese valor en lugar del default, sin recompilar

### Requirement: Preservacion de los numeros canonicos y de la evidencia congelada

El monitoreo SHALL NOT modificar ningun numero canonico ni la cifra primaria de la tesis, y MUST NOT sobrescribir la evidencia congelada (`evaluation/evidence/`), el corpus de evaluacion, las predicciones canonicas ni los artefactos de la campana. Las metricas del canario SHALL informarse como senales operativas de monitoreo y MUST NOT presentarse como resultados canonicos de la tesis ni reemplazar la linea de base congelada. Cuando el monitoreo produzca un valor que se decida citar, SHALL registrarse por el mecanismo vigente del memo canonico, sin retirar ni reemplazar ningun valor vigente.

#### Scenario: La evidencia congelada queda intacta

- **WHEN** se ejecuta el job de monitoreo
- **THEN** los archivos de `evaluation/evidence/` quedan byte a byte identicos y ningun artefacto canonico cambia

#### Scenario: Las metricas del canario no reemplazan un numero canonico

- **WHEN** se revisan los valores publicados de la tesis
- **THEN** la cifra primaria y los demas valores canonicos permanecen, y las metricas del canario figuran solo como senal de monitoreo

#### Scenario: Un valor citado se registra sin retirar el vigente

- **WHEN** se decide citar un valor producido por el monitoreo
- **THEN** se registra por el mecanismo vigente del memo canonico sin retirar ni reemplazar ningun valor vigente
