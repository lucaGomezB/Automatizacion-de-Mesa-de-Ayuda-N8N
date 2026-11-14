## MODIFIED Requirements

### Requirement: Contraste acotado de la hipotesis subsidiaria de eficiencia con salvedades declaradas

El documento SHALL informar el contraste de la hipotesis subsidiaria de eficiencia como un contraste pareado del híbrido congelado frente al brazo «Gemini solo», sobre el bloque primario de 103 casos fuera de muestra con consenso de los etiquetadores `E3` y `E4`, con la regla de decisión de tres vías fijada antes de observar datos (margen de no inferioridad 0,05; ahorro material si los límites superiores del IC de las razones de llamadas y de costo son menores que 0,90). El pasaje SHALL declarar, con remisión a la tabla correspondiente y al memo canónico: la exactitud de cada brazo, la prueba de McNemar exacta bilateral, la diferencia de exactitudes con su intervalo bootstrap pareado, el veredicto «no concluyente», el ahorro medido de llamadas y de costo (aproximadamente un tercio), que la estimación puntual fuera de muestra favorece al brazo de modelo solo, y que «no se detectó diferencia» no equivale a «equivalentes». SHALL conservar, como salvedades declaradas, las cifras dentro de la muestra sobre los 131 casos que resuelve la etapa de reglas (exactitud de la etapa de reglas `0,7405`, 97/131, frente a Gemini ejecutado sobre 130 de esos casos con el cortocircuito deshabilitado, `0,6769`, 88/130, segun `docs/deterministic_calibration.md`), rotuladas como estimaciones dentro de la muestra y con remisión al analisis de sensibilidad de los ajustes del clasificador (`subsec:sensibilidad-ajustes`); que la comparacion in-corpus no es prueba limpia; que la latencia no se midio por etapa, salvo que otro change la reporte; y la corrida única a temperatura 0,3, el análisis no ciego y la desviación del preregistro por el reintento de fallos técnicos. MUST NOT presentar las cifras dentro de la muestra (`0,7405` y `0,6769`) como el contraste de eficiencia ni como confirmación de la hipótesis. MUST NOT afirmar que la exactitud del híbrido no es inferior. La prueba pareada (McNemar exacta) del brazo SHALL citarse solo si figura registrada en el memo canonico (sección `3.28`), computada fuera de linea sobre los pares por caso. El change MUST NOT ejecutar llamadas pagas nuevas al proveedor: toda cifra proviene del caché versionado por el brazo.

#### Scenario: Cifras del contraste con procedencia

- **WHEN** se leen las cifras del contraste de eficiencia en `07-resultados.tex`
- **THEN** coinciden con las salidas del brazo y con la sección `3.28` del memo canonico
- **AND** cada cifra figura en `docs/Tesis/Correcciones/numeros-canonicos.md` con su procedencia

#### Scenario: Salvedades presentes

- **WHEN** se lee el pasaje del contraste
- **THEN** declara la corrida única a temperatura 0,3, el origen in-corpus de los ajustes, la latencia no medida por etapa, el análisis no ciego y el reintento de fallos técnicos
- **AND** el estado se rotula "contrastada: no concluyente", no "confirmada" ni "no contrastada"

#### Scenario: Estimacion dentro de la muestra

- **WHEN** se leen las cifras `0,7405` y `0,6769` en `08-discusion.tex`
- **THEN** el texto las califica como estimaciones dentro de la muestra y sin prueba pareada
- **AND** remite a `subsec:sensibilidad-ajustes`

#### Scenario: Regla de decision con el vocabulario previo

- **WHEN** la variante del analisis de sensibilidad con el vocabulario previo al ajuste muestra que la etapa de reglas no supera a Gemini en exactitud sobre los casos que resuelve
- **THEN** esa variante se declara como salvedad y no cambia el veredicto del contraste medido con el brazo
- **AND** el veredicto sigue siendo "contrastada: no concluyente" y la discusion no presenta la ventaja in-corpus como evidencia favorable

#### Scenario: Prueba pareada condicionada al memo

- **WHEN** el memo canonico no registra la prueba pareada del brazo (porque su sección `3.28` no se agrego)
- **THEN** el texto declara que la diferencia no se sometio a una prueba pareada
- **AND** no se cita ningun valor p para este contraste

#### Scenario: Sin llamadas pagas

- **WHEN** se revisa el registro de ejecucion del change
- **THEN** no hubo invocaciones nuevas a Gemini ni re-ejecucion del brazo
- **AND** toda cifra nueva proviene del caché y de las salidas ya versionadas

#### Scenario: Veredicto y ahorro informados

- **WHEN** se lee el pasaje del contraste en `07-resultados.tex`
- **THEN** figuran la exactitud de los dos brazos, McNemar exacta, la diferencia con su intervalo y el veredicto «no concluyente»
- **AND** se informa el ahorro de llamadas y de costo con sus intervalos
- **AND** se declara que la estimación puntual fuera de muestra favorece al brazo de modelo solo

#### Scenario: Sin sobreventa de la no inferioridad

- **WHEN** se leen los pasajes de eficiencia en `07-resultados.tex`, `08-discusion.tex`, `09-conclusiones.tex` y `10-recomendaciones.tex`
- **THEN** ninguno afirma que el híbrido no es inferior en exactitud
- **AND** todos distinguen «no se detectó diferencia» de «equivalentes»

### Requirement: Estado declarado de las hipotesis subsidiarias

Las dos hipotesis subsidiarias de `01-introduccion.tex` SHALL tener un estado declarado y coherente en la introduccion, la discusion y las conclusiones. La de integracion multicanal sin cuellos de botella SHALL declararse "no contrastada" mientras no se mida la capacidad bajo carga concurrente. La de mayor eficiencia del esquema hibrido frente a un esquema solo de modelo SHALL declararse "contrastada: no concluyente" en todos los capitulos, porque se midio con el brazo «Gemini solo» bajo una regla de decision prerregistrada y el resultado fue no concluyente: el ahorro de llamadas y de costo se cumplio, pero la no inferioridad de la exactitud no se establecio. MUST NOT declararse "no contrastada" ni "confirmada". La discusion y las conclusiones MUST NOT afirmar consistencia con la hipotesis de eficiencia apoyandose solo en la proporcion de casos resueltos sin invocar al modelo.

#### Scenario: Estados declarados en los tres capitulos

- **WHEN** se leen la introduccion, la discusion y las conclusiones
- **THEN** cada hipotesis subsidiaria tiene un estado explicito
- **AND** la de eficiencia figura como "contrastada: no concluyente" en los tres capitulos
- **AND** la de integracion multicanal figura como "no contrastada" en los tres capitulos

#### Scenario: Frase de consistencia sin sustento retirada

- **WHEN** se busca en `08-discusion.tex` la afirmacion de consistencia con la hipotesis subsidiaria de eficiencia
- **THEN** no aparece apoyada solo en el 65,5 % de casos resueltos sin el modelo
- **AND** en su lugar figura el contraste medido con su veredicto no concluyente

#### Scenario: Subsidiaria multicanal no contrastada

- **WHEN** se leen las conclusiones sobre la integracion de los tres canales
- **THEN** el texto no afirma que la integracion "confirmo" la ausencia de dispersion operativa o de cuellos de botella
- **AND** declara que la hipotesis subsidiaria de integracion multicanal no se contrasto

## ADDED Requirements

### Requirement: Declaracion de la relacion de referencias del contraste de eficiencia

El documento SHALL declarar de forma explícita, allí donde informa el contraste de eficiencia, que la referencia de ese contraste es el bloque de 103 casos fuera de muestra con consenso de `E3` y `E4` (etapa previa y prerregistrada), y que la referencia arbitrada de 206 casos es el complemento de exactitud fuera de muestra del capítulo de resultados, reportado por separado. SHALL aclarar que el bloque de 103 es un subconjunto limpio del corpus arbitrado y que las dos estimaciones no se agrupan en una sola. MUST NOT presentar el contraste de eficiencia como si se hubiera medido sobre los 206 casos arbitrados ni sugerir que la corrida se repitió sobre esa referencia.

#### Scenario: Referencias declaradas y no agrupadas

- **WHEN** se lee la subsección de resultados que informa el contraste de eficiencia
- **THEN** declara que el bloque primario es de 103 casos con consenso de `E3` y `E4`
- **AND** remite a la referencia arbitrada de 206 como complemento de exactitud, informado aparte
- **AND** no presenta una estimación agrupada de 103 y 206

#### Scenario: Sin corrida sobre la referencia arbitrada

- **WHEN** se busca en el texto una afirmación de que el brazo de modelo solo se corrió sobre los 206 casos arbitrados
- **THEN** esa afirmación no aparece
- **AND** el texto declara que el contraste se midió sobre el bloque de 103