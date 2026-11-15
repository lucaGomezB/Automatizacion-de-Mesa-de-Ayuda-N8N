## ADDED Requirements

### Requirement: Estado honesto del clasificador supervisado como trabajo futuro dependiente de datos

`10-recomendaciones.tex` SHALL declarar, en `subsec:clasificador-supervisado` y en
`subsec:frontera-sistemas`, que el clasificador supervisado entrenado sobre el
corpus acumulado **depende de datos que todavia no existen** (el volumen que la
organizacion acumulara en `clasificacion_log`) y de **etiquetado humano con
consentimiento**, y que no se entrena ni se mide en este trabajo. La subseccion
SHALL declarar de forma explicita que sobre la referencia de `206` casos el umbral
`0,85` **no es alcanzable** (harían falta `+34` aciertos; aun corrigiendo los `30`
errores de `Sistemas` el techo es `0,835`, y el brazo manual anota `0,8278`), y que
la fuente dominante de error es la ambiguedad de la frontera `Sistemas`↔`Soporte
Tecnico Software`. `subsec:evaluacion-modelos-abiertos` SHALL mantener su criterio
de exito sobre un corpus independiente. El texto MUST NOT presentar el
entrenamiento como realizado, MUST NOT introducir un valor canonico nuevo y MUST
NOT reunir el umbral de volumen con una justificacion distinta de la indicativa
vigente.

#### Scenario: Dependencia declarada

- **WHEN** se leen `subsec:clasificador-supervisado` y `subsec:frontera-sistemas`
- **THEN** declaran que la linea depende de datos inexistentes y de consentimiento
- **AND** declaran que no se entrena ni se mide en este trabajo

#### Scenario: No alcanzabilidad sobre los 206 declarada

- **WHEN** se busca el tratamiento del umbral en la subseccion del clasificador supervisado
- **THEN** se declara que `0,85` no es alcanzable sobre los `206` casos, con el techo `0,835` y el `+34`
- **AND** no se introduce un valor canonico nuevo ni se presenta el entrenamiento como realizado

### Requirement: Frontera Sistemas-Software descrita como problema de taxonomia y de codebook

`08-discusion.tex` SHALL precisar, en la limitacion correspondiente al desempeno
de `Sistemas`, que la frontera `Sistemas`↔`Soporte Tecnico Software` es —antes que
una limitacion de capacidad del clasificador— un problema de taxonomia o de
criterio de etiquetado, con `16` de `64` errores dirigidos a `Soporte Tecnico
Software`, y SHALL remitir a la revisión del codebook como linea de trabajo futuro
y a la no alcanzabilidad del umbral sobre los `206`. La formulacion MUST NOT
afirmar que el clasificador mejorara esa clase.

#### Scenario: Frontera descrita y remitida

- **WHEN** se lee la limitacion sobre `Sistemas` en `08-discusion.tex`
- **THEN** describe la frontera como problema de taxonomia o de criterio de etiquetado
- **AND** remite a la revision del codebook y a la no alcanzabilidad del `0,85` sobre los `206`

#### Scenario: Sin promesa de mejora

- **WHEN** se busca una afirmacion sobre la mejora del clasificador en esa clase
- **THEN** no se afirma que el clasificador mejorara
- **AND** la revision se presenta como analisis de la taxonomia
