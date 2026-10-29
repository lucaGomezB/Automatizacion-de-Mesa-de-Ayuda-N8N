## ADDED Requirements

### Requirement: Registro de los errores por frontera y de los aciertos laxos entre los errores estrictos

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar, en una seccion propia atribuida a c-159 y anunciada en su lista de upserts, los errores estrictos por frontera de confusion (par no ordenado de sectores) con su proporcion sobre el total de errores estrictos, los aciertos laxos entre esos errores por frontera y en total, los errores fuera del conjunto de verdad y los casos ilustrativos de la subseccion de analisis de errores (identificador, etapa, confianza y condicion de acierto laxo). Cada valor SHALL registrarse con estado `vigente` y con su procedencia verificable: la salida del recomputo deterministico de `docs/Tesis/Correcciones/recontar_errores_frontera.py` y la linea de `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` que lo cita. Los valores SHALL satisfacer la identidad aciertos estrictos mas aciertos laxos entre los errores estrictos igual a aciertos laxos totales, y su registro MUST NOT modificar ningun valor vigente previo del memo.

#### Scenario: Valores registrados con procedencia y estado

- **WHEN** se recorre la seccion de c-159 del memo
- **THEN** figuran los errores por frontera (14, 12, 11 y 16, total 53), los aciertos laxos por frontera (5, 10, 8 y 9, total 32), los errores fuera del conjunto de verdad (21) y los casos R001, R032 y R015
- **AND** cada valor declara estado `vigente`, la salida del recomputo y la linea de `07-resultados.tex` que lo cita

#### Scenario: Identidad con la exactitud laxa canonica

- **WHEN** se suman los aciertos estrictos canonicos (147) y los aciertos laxos entre los errores estrictos (32)
- **THEN** el resultado es igual a los aciertos laxos canonicos (179)
- **AND** los errores fuera del conjunto de verdad (21) son iguales a 200 menos 179

#### Scenario: Sin cambio de valores previos

- **WHEN** se compara el memo antes y despues del change
- **THEN** ninguna fila previa cambia de valor ni de estado
- **AND** las cifras de la Tabla `tab:errores`, que no tenian entrada, quedan registradas

### Requirement: Recomputo deterministico y de solo lectura de los errores por frontera

El proyecto SHALL proveer `docs/Tesis/Correcciones/recontar_errores_frontera.py`, un script que solo usa la biblioteca estandar de Python y recomputa los valores del requisito anterior desde `data/corpus_evaluacion_pseudonimizado.json` y `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`, sin invocar al clasificador, sin acceso a red y sin escribir en el repositorio. Antes de computar SHALL validar el SHA-256 del corpus, con los fines de linea normalizados a LF, contra el valor canonico `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`; la `cache_meta` de la evidencia (hash del corpus igual al del corpus, 200 casos y version `hybrid-v3`); y la union caso por caso de predicciones y corpus por identificador, con descripciones identicas. Ante cualquier discrepancia SHALL terminar con un codigo de salida distinto de cero sin emitir cifras. SHALL reutilizar la definicion de acierto laxo de `evaluation/metrics.py` en lugar de reimplementarla, MUST NOT usar funciones que escriban el corpus, SHALL redondear los porcentajes a un decimal con el criterio mitad hacia arriba y SHALL producir una salida identica en ejecuciones sucesivas. Sus funciones SHALL estar cubiertas por pruebas pytest en `docs/Tesis/Correcciones/test_recontar_errores_frontera.py`, escritas antes del codigo que prueban.

#### Scenario: Reproduccion sobre la evidencia oficial

- **WHEN** se ejecuta el script desde la raiz del repositorio sobre el corpus y la evidencia versionados
- **THEN** informa 53 errores estrictos, 32 de ellos aciertos laxos, y por frontera 14 y 5 (Soporte Tecnico Hardware-Soporte Tecnico Software), 12 y 10 (Sistemas-Soporte Tecnico Software), 11 y 8 (Seguridad Informatica-Soporte Tecnico Software) y 16 y 9 (demas fronteras)
- **AND** reproduce literalmente las descripciones, sectores, confianzas y etapas de R001, R032 y R015

#### Scenario: Hash del corpus discrepante

- **WHEN** el corpus leido no tiene el SHA-256 canonico tras normalizar los fines de linea
- **THEN** el script termina con codigo distinto de cero
- **AND** no imprime ninguna cifra de errores ni de aciertos

#### Scenario: Evidencia o union inconsistente

- **WHEN** la `cache_meta` de la evidencia no coincide con el corpus, o un caso falta, se repite o tiene una descripcion distinta
- **THEN** el script termina con codigo distinto de cero sin emitir cifras

#### Scenario: Solo lectura y determinismo

- **WHEN** se ejecuta el script dos veces seguidas
- **THEN** ambas salidas son identicas
- **AND** `git status --porcelain` no muestra archivos modificados por la ejecucion

#### Scenario: Definicion canonica reutilizada y redondeo

- **WHEN** se inspecciona el script y se computa el porcentaje de 9 sobre 16
- **THEN** el script importa la definicion de acierto laxo de `evaluation.metrics`
- **AND** el porcentaje se informa como 56,3

#### Scenario: Pruebas presentes y en verde

- **WHEN** se ejecuta `python -m pytest docs/Tesis/Correcciones/test_recontar_errores_frontera.py -q` en un entorno con pytest
- **THEN** todas las pruebas pasan
- **AND** cubren la validacion del hash, de la `cache_meta` y de la union, el agrupamiento por frontera, el redondeo y la salida
