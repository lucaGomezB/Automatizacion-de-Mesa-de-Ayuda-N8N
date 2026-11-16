## ADDED Requirements

### Requirement: Registro aditivo del retiro de la validacion fuera de muestra

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar una seccion **aditiva** con el primer numero libre de la Seccion 3 al aplicar (esperado `3.45` mientras `3.39`-`3.42` sigan reservadas a `c-230`/`c-229`/`c-228`/`c-232` y `3.43`-`3.44` esten ocupadas) que registre el retiro de la validacion fuera de muestra (c-235): la causa (procedencia no acreditable como registro primario; textos que no eran incidentes extraidos de una organizacion), la fecha de la decision de los autores y la lista de secciones y valores afectados. Cada valor que dependa del corpus retirado SHALL pasar a estado `retirado` por upsert, con remision a la seccion nueva, sin borrarse y sin cambiar su cifra: como minimo los de las secciones `3.19`, `3.20`, `3.22`, `3.23`, `3.25`, `3.26`, `3.27`, `3.30`, `3.32`, `3.34`, `3.35` y `3.36`, y la parte fuera de muestra de `3.14`, `3.21` (acuerdo y kappa `E3`/`E4`), `3.24`, `3.28` (bloque primario) y `3.33` (sensibilidad). El bloque dentro de la muestra de `3.28` SHALL conservar el estado `condicional` y la seccion nueva SHALL registrar el estado "sin contraste limpio" de la hipotesis de eficiencia. La seccion MUST NOT renumerar secciones ni cambiar el valor de ninguna cifra, y SHALL dejar la numeracion de la Seccion 3 consecutiva y sin duplicados.

#### Scenario: Valores afectados marcados como retirados

- **WHEN** se recorren las secciones listadas despues del change
- **THEN** cada valor que depende del corpus retirado figura con estado `retirado` y remision a la seccion nueva
- **AND** su cifra no cambio

#### Scenario: Causa y lista registradas

- **WHEN** se lee la seccion nueva
- **THEN** figuran la causa del retiro, la fecha de la decision de los autores y la lista de secciones y valores afectados
- **AND** figura el estado "sin contraste limpio" de la hipotesis de eficiencia

#### Scenario: Ninguna cifra retirada citada como vigente

- **WHEN** se cruzan los valores marcados `retirado` con `sections/*.tex`
- **THEN** ninguno aparece en la tesis fuera de `subsec:nota-versiones`

#### Scenario: Numeracion consecutiva

- **WHEN** se listan los encabezados `3.N` antes y despues del change
- **THEN** la seccion nueva ocupa el primer numero libre y no hay renumeraciones ni duplicados

## MODIFIED Requirements

### Requirement: Registro aditivo de la robustez de la línea de base frente a la referencia

El memo canónico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL conservar la sección aditiva
`3.36` (primera libre tras la `3.35` de c-224) que registra, por subconjunto de referencia
—consenso `E3`/`E4` (`n = 142`), `150` originales (`n = 150`) y arbitrado completo (`n = 206`)—, la
brecha híbrido menos línea de base con su IC 95 %, sus aciertos, el criterio de McNemar aplicado, la
fuente (el JSON del análisis de robustez) y el comando que lo produce. Cada valor, incorporado con
estado `vigente (nuevo)`, SHALL pasar a estado `retirado` por el upsert del retiro de la validación
fuera de muestra (c-235), con remisión a la sección de ese retiro, sin borrarse ni cambiar su cifra.
La sección MUST NOT reemplazar ningún valor de las secciones `3.1` a `3.35` y SHALL conservar la
constancia de que, al incorporarse, no cambió la cifra primaria `0,6893/206`, el macro-F1 `0,7024`
ni el veredicto del umbral `0,85`.

#### Scenario: Sección conservada con procedencia por valor

- **WHEN** se lee la sección `3.36` del memo
- **THEN** cada cifra de la brecha por subconjunto figura con su fuente (JSON) y su comando
- **AND** cada valor figura con estado `retirado` y remisión a la sección del retiro

#### Scenario: Valores previos intactos

- **WHEN** se comparan las secciones `3.1` a `3.35` antes y después del change
- **THEN** ninguna cifra cambia
- **AND** los únicos cambios de estado son los del upsert del retiro de c-235
