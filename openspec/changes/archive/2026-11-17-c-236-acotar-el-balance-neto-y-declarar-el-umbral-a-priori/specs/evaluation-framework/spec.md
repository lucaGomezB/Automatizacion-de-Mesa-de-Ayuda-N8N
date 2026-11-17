## ADDED Requirements

### Requirement: Recomputo offline del balance neto acotado con el termino de revision

El análisis SHALL implementarse en un script sucesor y aditivo (`evaluation/data/campana/analisis/analisis_balance_neto_c236.py`), de solo lectura, con biblioteca estándar, sin red, sin Gemini y sin base de datos. El script SHALL leer los artefactos versionados de c-220 (`analisis_costo_derivacion_c220.json`) y de c-222 (`analisis_balance_neto_c222.json`) y las entradas por caso que c-222 empareja, cada uno con su SHA-256, sin constantes que reemplacen la lectura. Antes de calcular, SHALL reproducir los anclajes `B = 30,64` h-persona, `c = 69,51 s`, `r = 22,06 s` (`n = 138`) y la tasa de revisión `147/200`, y SHALL abortar sin escribir si alguno difiere. El script SHALL calcular `B_r = (N / 3.600) x [Delta t - rho x r - (e_aut - e_man) x c]` y `a*_r = 1 - e_man - (Delta t - rho x r) / c`, con `rho = 147/200` y `r` igual a la media de las duraciones de revisión. La elección de la media SHALL quedar fijada en el docstring antes de generar las salidas, con el preregistro declarado no ciego. El script SHALL informar `B_r` como cota superior respecto del tramo de reanudación no medido. SHALL informar también: el intervalo condicional bootstrap con `c` y `rho` fijos; la cota combinada por suma de extremos sobre `rho`, `r`, `e_aut - e_man` y `c`; la rejilla de 5, 10 y 15 minutos con el término de revisión, rotulada como sensibilidad al tramo no medido; el costo de equilibrio `c*` y el margen del tramo no medido; y las sensibilidades de `r` (mediana, variante sin solapamiento) y de `rho = 1`. El script MUST NOT declarar el signo del balance real como fijado. MUST NOT incluir cifras fuera de muestra. MUST NOT modificar los artefactos de c-220 ni de c-222. Las salidas `.json`, `.md` y `.SHA256SUMS.txt` SHALL ser deterministas byte a byte.

#### Scenario: Anclajes reproducidos antes de calcular

- **WHEN** el script lee los artefactos de entrada
- **THEN** verifica `B = 30,64`, `c = 69,51 s`, `r = 22,06 s` con `n = 138` y la tasa `147/200`
- **AND** aborta sin escribir ningún archivo si alguno no coincide

#### Scenario: Balance con el término de revisión

- **WHEN** se ejecuta el recomputo con los insumos versionados
- **THEN** `B_r` vale aproximadamente `+18,7` h-persona por trimestre y `a*_r` aproximadamente `43,1 %`
- **AND** el `.json` rotula `B_r` como cota superior respecto del tramo de reanudación no medido

#### Scenario: Sensibilidad al tramo no medido sin signo fijado

- **WHEN** se lee la salida
- **THEN** figuran la rejilla de 5, 10 y 15 minutos con revisión, el costo de equilibrio `c*` y el margen del tramo no medido
- **AND** ningún campo declara el signo del balance real como fijado por la muestra

#### Scenario: Ejecución determinista y sin cifras fuera de muestra

- **WHEN** el script se ejecuta dos veces desde la raíz del repositorio
- **THEN** las salidas son idénticas byte a byte y el manifiesto lista el SHA-256 de cada entrada
- **AND** la salida no contiene ninguna tasa ni balance calculado sobre el corpus fuera de muestra
