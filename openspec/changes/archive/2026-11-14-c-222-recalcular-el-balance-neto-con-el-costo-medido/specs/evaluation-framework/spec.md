## ADDED Requirements

### Requirement: Recomputo offline del balance neto con el costo medido

El análisis SHALL implementarse en un script de solo lectura, biblioteca estándar, sin red, sin Gemini y sin base de datos, que lea los artefactos versionados de c-220 y de c-221 y la referencia común de la sección 3.21, y recalcule `B` y `a*` con el `c` medido. Antes de calcular, el script SHALL reproducir los anclajes `+25,4`, `+18,7` y `+11,9` horas-persona por trimestre y el valor `69,51 s`, y SHALL abortar sin escribir si alguno difiere. El recomputo SHALL informar el intervalo de `B` combinando la incertidumbre del `c` con la de `e_aut − e_man`, con el método de propagación declarado, y SHALL informar por separado el intervalo condicional con `c` fijo. Las salidas `.json`, `.md` y `SHA256SUMS.txt` SHALL ser deterministas byte a byte entre corridas. El script MUST NOT modificar los artefactos de entrada ni ningún valor congelado.

#### Scenario: Ejecución determinista y offline

- **WHEN** el script se ejecuta dos veces desde la raíz del repositorio
- **THEN** las salidas son idénticas byte a byte
- **AND** no se realiza ninguna llamada de red ni a Gemini

#### Scenario: Anclajes reproducidos antes de calcular

- **WHEN** el script lee los artefactos de entrada
- **THEN** verifica los valores `+25,4`, `+18,7`, `+11,9` y `69,51` s
- **AND** aborta sin escribir si alguno no coincide

#### Scenario: Incertidumbre y signo declarados

- **WHEN** se lee la salida del recomputo
- **THEN** `B` figura con su intervalo combinado y con el intervalo condicional a `c` fijo
- **AND** el signo se enuncia solo si el intervalo combinado lo fija

#### Scenario: Trazabilidad de las entradas

- **WHEN** se revisa el manifiesto de huellas
- **THEN** cada artefacto de entrada figura con su SHA-256
- **AND** cada cifra de la salida remite a la clave del `.json` que la produce