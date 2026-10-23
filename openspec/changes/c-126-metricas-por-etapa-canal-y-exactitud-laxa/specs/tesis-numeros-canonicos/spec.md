## ADDED Requirements

### Requirement: Registro de las metricas por etapa, por canal y de la exactitud laxa

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar, en una seccion propia, la exactitud estricta y laxa por etapa del pipeline y por canal de origen con sus IC de Wilson, la descomposicion por etapa de las bandas de confianza y del tramo de confianza `>= 0,90`, la distribucion de valores de confianza por etapa y el contraste pareado de McNemar entre la etapa deterministica y Gemini sobre el conjunto cortocircuitable ---o su declaracion de no computable---, rotulado como insumo de c-128 y c-137 y acompanado de sus salvedades (otra corrida y otra version que la oficial; contraste en muestra). Cada valor SHALL registrarse con su procedencia verificable ---linea del reporte regenerado o derivacion aritmetica explicita desde valores ya canonicos--- y con su estado. Los valores ya canonicos de la calibracion (bandas `98/26/6/31/39` con `75/19/2/22/29` aciertos, contingencia `76/53` y `124/94`, tramo `46/13`) SHALL conservarse sin cambio de valor, y su lectura SHALL anotarse como efecto de composicion entre etapas. La lectura de "anti-calibracion" del clasificador en su conjunto SHALL registrarse como retirada.

#### Scenario: Valores nuevos con procedencia y estado

- **WHEN** se recorre la seccion nueva del memo
- **THEN** cada valor por etapa, por canal y de exactitud laxa declara su procedencia (archivo y linea, o derivacion explicita) y un estado en `{vigente, retirado, condicional}`
- **AND** ningun valor carece de fuente verificable

#### Scenario: Descomposicion por etapa consistente con los canonicos

- **WHEN** se suman, banda por banda, los casos y aciertos de la etapa deterministica y de la etapa Gemini
- **THEN** las sumas reproducen la tabla de bandas canonica (`98/26/6/31/39` casos y `75/19/2/22/29` aciertos)
- **AND** los totales por etapa reproducen `131/97` y `69/50`

#### Scenario: Lectura retirada anotada

- **WHEN** se lee la entrada de la contingencia de confianza o de las bandas en el memo
- **THEN** se anota que el contraste agregado `0,697` frente a `0,758` es un efecto de composicion entre etapas
- **AND** la lectura de anti-calibracion del clasificador en su conjunto figura como retirada

#### Scenario: Contraste de McNemar registrado o declarado no computable

- **WHEN** se lee la seccion nueva del memo
- **THEN** figura el contraste de McNemar (pares, `b`, `c`, estadistico, p primario y criterio) con procedencia en `docs/deterministic_calibration.md` y sus salvedades, o la declaracion de que no es computable con los artefactos disponibles
- **AND** se lo rotula como insumo de c-128 y c-137

### Requirement: Procedencia de las predicciones por caso y politica de deriva

Los valores canonicos de clasificacion SHALL provenir de la corrida oficial del clasificador (`hybrid-v3`, predicciones generadas el 2026-10-07), identificada en el memo por su `cache_meta` y por el SHA-256 del archivo de predicciones. Antes de usar como fuente un archivo de predicciones recuperado, su metadata (hash del corpus, cantidad de casos y version del clasificador) y su huella agregada (exactitud `147/200`, etapas `131/69/0`, bandas, contingencia y tramo `>= 0,90` canonicos) MUST coincidir con los valores canonicos. Una corrida de reproduccion (nueva invocacion al proveedor) MUST NOT sobrescribir las predicciones oficiales, `evaluation/report.md` ni ningun valor canonico vigente: sus resultados SHALL escribirse en archivos separados, rotularse con su version y fecha, y acompanarse de la deriva cuantificada respecto de los agregados oficiales de la etapa Gemini. El reemplazo de los canonicos por una corrida nueva SHALL requerir una decision explicita del usuario registrada en el memo.

#### Scenario: Archivo recuperado con huella coincidente

- **WHEN** se recupera un `evaluation/predicciones.json` cuya metadata y cuya huella agregada coinciden con los valores canonicos
- **THEN** el archivo se acepta como fuente de los valores nuevos
- **AND** su `cache_meta` y su SHA-256 quedan registrados en el memo

#### Scenario: Archivo recuperado con huella discrepante

- **WHEN** la metadata o algun agregado de la huella de un archivo recuperado difiere de los valores canonicos
- **THEN** el archivo se rechaza como fuente de valores canonicos
- **AND** la discrepancia se registra sin modificar ningun valor vigente

#### Scenario: Corrida de reproduccion rotulada y separada

- **WHEN** el usuario autoriza una corrida de reproduccion porque las predicciones oficiales no pudieron recuperarse
- **THEN** sus predicciones y su reporte se escriben en archivos distintos de `evaluation/predicciones.json` y `evaluation/report.md`, con su version y fecha
- **AND** el memo registra la deriva de la etapa Gemini frente a los agregados oficiales (`50/69` aciertos, bandas `31/22` y `38/28`, tramo `>= 0,90` de `45` casos con `13` errores)

#### Scenario: Sin reemplazo silencioso de los canonicos

- **WHEN** una corrida de reproduccion produce agregados distintos de los oficiales
- **THEN** los valores canonicos vigentes del memo y de la tesis no cambian
- **AND** solo una decision explicita del usuario, registrada en el memo, habilita su reemplazo
