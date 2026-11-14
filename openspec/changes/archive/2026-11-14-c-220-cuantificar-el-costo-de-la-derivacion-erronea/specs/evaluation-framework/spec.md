## ADDED Requirements

### Requirement: Análisis offline del costo de la derivación errónea

El análisis de c-220 SHALL computar el costo de una derivación errónea sobre los artefactos de campaña versionados (`intervenciones.csv` y `brazo_manual.csv`), sin invocar al clasificador, sin red y sin base de datos, usando solo la biblioteca estándar. SHALL informar la duración de las intervenciones por valor de `cambio_sector`, la diferencia entre ambos grupos con su intervalo bootstrap al 95 %, el tiempo de decisión de sector del brazo manual como proxy del rediagnóstico, y la composición de `c` con sus componentes medidos y anclados. SHALL declarar la cobertura de la duración y enumerar los casos sin dato, sin imputarlos. SHALL emitir salidas `.json` y `.md` con la huella SHA-256 de cada entrada y con el comando que las reproduce. El cálculo SHALL ser determinista con semilla fija y sus salidas SHALL ser idénticas byte a byte entre corridas.

#### Scenario: Determinismo

- **WHEN** el análisis corre dos veces sobre las mismas entradas
- **THEN** las salidas son idénticas byte a byte
- **AND** la corrida declara la semilla y el número de remuestreos usados

#### Scenario: Solo lectura

- **WHEN** el análisis se ejecuta
- **THEN** no modifica ningún artefacto de entrada y no escribe fuera de sus rutas de salida
- **AND** no realiza llamadas a Gemini ni conexiones de red o de base de datos

#### Scenario: Cobertura declarada

- **WHEN** una intervención no tiene `duracion_s`
- **THEN** el análisis la excluye del cálculo de duración y la enumera en el bloque de cobertura
- **AND** no imputa ni reescribe el valor faltante

#### Scenario: Diferencia entre grupos

- **WHEN** el análisis compara las intervenciones que cambian la derivación con las que no la cambian
- **THEN** informa `n`, media, mediana, desvío e intervalo bootstrap al 95 % de cada grupo
- **AND** informa la diferencia de medias con su intervalo

#### Scenario: Composición de `c` con propagación

- **WHEN** el análisis compone los componentes medidos y el componente anclado
- **THEN** informa el intervalo compuesto y el método de propagación usado
- **AND** declara por separado el valor de cada componente y su fuente

#### Scenario: Caso sintético conocido

- **WHEN** todas las intervenciones de un grupo sintético tienen la misma duración
- **THEN** la media, la mediana y el intervalo degeneran en ese valor
- **AND** la diferencia entre grupos es exactamente la diferencia de las constantes