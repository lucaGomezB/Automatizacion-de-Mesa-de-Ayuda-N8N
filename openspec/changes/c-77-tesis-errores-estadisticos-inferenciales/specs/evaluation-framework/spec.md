## MODIFIED Requirements

### Requirement: Análisis estadístico de tiempos

El framework SHALL aplicar la prueba de Wilcoxon de rangos con signo sobre los pares (tiempo_manual, tiempo_automatizado) para contrastar la igualdad de medianas entre ambos flujos, y SHALL reportar el tamaño del efecto rank-biserial asociado, conforme a §4.7 y §7.1 de la tesis. El framework MUST declarar explícitamente la convención del estadístico de Wilcoxon empleado y MUST reportar ambos estadísticos de rango, `T+` (suma de rangos positivos) y `T−` (suma de rangos negativos), además del valor p. El tamaño del efecto MUST calcularse con la fórmula rank-biserial `r = (T+ − T−) / (n(n+1)/2)`, equivalente a `1 − 4W/(n(n+1))` cuando `W = T− = min(T+, T−)`; MUST NOT usarse `r = 1 − 2W/(n(n+1))`. El cálculo SHALL ser una función pura que recibe las dos series pareadas y devuelve, como mínimo, el estadístico de contraste, `T+`, `T−`, el valor p y el tamaño del efecto.

#### Scenario: Diferencia sistemática produce p significativo

- **WHEN** el flujo automatizado es consistentemente más rápido que el manual en la mayoría de los pares
- **THEN** la prueba devuelve un valor p por debajo del nivel de significancia 0.05 y un tamaño del efecto de magnitud alta

#### Scenario: Series de distinta longitud son rechazadas

- **WHEN** se invoca la prueba con dos series de cantidad de elementos distinta
- **THEN** el framework lanza un error en lugar de producir un resultado inválido

#### Scenario: Convención de W y ambos estadísticos reportados

- **WHEN** el framework devuelve el resultado de la prueba de Wilcoxon
- **THEN** informa explícitamente la convención de `W` adoptada
- **AND** reporta `T+` y `T−` de forma diferenciada

#### Scenario: Fórmula rank-biserial correcta y rango verdadero

- **WHEN** se calcula el tamaño del efecto sobre los pares reales
- **THEN** el resultado es `(T+ − T−) / (n(n+1)/2)` (por ejemplo `0,9667` para `T+=19765`, `T−=335`, `n=200`)
- **AND** no se reporta el valor espurio `1,00` ni se documenta un rango `[-1,+1]` para `1 − 2W/(n(n+1))`

#### Scenario: Código y tesis usan la misma fórmula

- **WHEN** se compara la implementación del framework con la fórmula declarada en la tesis
- **THEN** ambas emplean la misma definición `r = (T+ − T−) / (n(n+1)/2)` (o su equivalente `1 − 4W/(n(n+1))`)
- **AND** no se emplea una aproximación distinta basada en el conteo de pares concordantes y discordantes sin ponderar por rango

## ADDED Requirements

### Requirement: Reporte de calibración de la confianza del clasificador

El framework SHALL reportar la calibración de la confianza del clasificador: la
relación entre el valor de `confianza` devuelto por caso y la exactitud estricta
de la predicción. El reporte MUST incluir, como mínimo, la precisión del segmento
de confianza `>= 0,70` y la del segmento `< 0,70`, la cantidad de errores con
confianza `>= 0,90`, y una tabla de calibración por bandas de confianza. El
cálculo SHALL ser una función pura sobre las predicciones ya recolectadas.

#### Scenario: Tabla de calibración por bandas

- **WHEN** el framework procesa las predicciones con `confianza` y `sector_predicho`
- **THEN** produce una tabla de calibración con, al menos, las bandas `[0;0,5)`, `[0,5;0,7)`, `[0,7;0,85)`, `[0,85;0,95)` y `[0,95;1,0]`
- **AND** por cada banda reporta la cantidad de casos y la exactitud observada

#### Scenario: Contingencia alta/baja confianza

- **WHEN** el framework reporta la calibración
- **THEN** informa la precisión del segmento con confianza `>= 0,70` y la del segmento con confianza `< 0,70`
- **AND** informa la cantidad de errores entre las predicciones con confianza `>= 0,90`

#### Scenario: El reporte no altera las métricas primarias

- **WHEN** se agrega el reporte de calibración
- **THEN** las métricas primarias de clasificación (exactitud, F1 macro/micro, matriz 5x5) no cambian de valor
- **AND** la calibración se calcula como salida adicional sobre las mismas predicciones
