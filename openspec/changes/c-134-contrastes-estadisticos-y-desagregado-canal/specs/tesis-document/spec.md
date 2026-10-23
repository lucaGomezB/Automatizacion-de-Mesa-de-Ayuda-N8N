## ADDED Requirements

### Requirement: Tabla de tiempos por canal con brazo manual y contraste intra-canal

La tabla de tiempos por canal de origen (`\label{tab:tiempos-canal}` en `07-resultados.tex`) SHALL presentar, para cada canal (llamada telefonica, correo electronico, formulario web) y para el total, la cantidad de casos, la media y la mediana del tiempo manual, la media y la mediana del tiempo automatizado, la reduccion relativa de la media, la cantidad de pares en que el flujo automatizado no fue mas rapido, el valor p del contraste de Wilcoxon intra-canal sobre los pares del canal (bajo la convencion declarada) y el tamano del efecto estandarizado `d_z`. Todos los valores MUST coincidir con la seccion "Tiempos" de `evaluation/report.md` regenerada y con el valor vigente de `docs/Tesis/Correcciones/numeros-canonicos.md`. Los estadisticos de rango por canal (`W`, `T+`, `T-`, `r`) SHALL quedar disponibles en `evaluation/report.md` y la tabla o su nota SHALL remitir a ese reporte; la tabla y el texto MUST NOT presentar `W = 0` ni un tamano del efecto rank-biserial `r = 1,00` como resultado del contraste, en coherencia con el requisito "Rigor inferencial del tamano del efecto" (en los canales sin pares desfavorables el texto lo expresa como "el flujo automatizado fue mas rapido en todos los pares del canal"). El tamano del efecto `d_z` SHALL rotularse siempre como `d_z`, de modo que su valor global (1,00) no se confunda con el rank-biserial. La fila telefonica SHALL conservar su rotulo de cota inferior y la tabla SHALL conservar su linea de fuente. Toda afirmacion de la discusion sobre reducciones por canal SHALL remitir a esta tabla y MUST NOT presentar el contraste intra-canal apareado como un analisis pendiente.

#### Scenario: Brazo manual y contraste presentes por canal

- **WHEN** se lee `tab:tiempos-canal` en el PDF compilado
- **THEN** cada canal y el total muestran casos, media y mediana manual, media y mediana automatizada, reduccion relativa, pares no mas rapidos, p y `d_z`
- **AND** la fila "Global" reproduce los valores de `tab:tiempos` (61,6 s y 17,76 s de media)

#### Scenario: Sin W = 0 ni r = 1,00 en la tesis

- **WHEN** se buscan en las secciones de la tesis los resultados del contraste por canal
- **THEN** no aparece `W = 0` ni un rank-biserial `r = 1,00` presentado como resultado
- **AND** la ausencia de pares desfavorables en telefonia y formulario web se expresa con el conteo de pares no mas rapidos (0) y la remision al reporte, y todo `d_z` aparece rotulado como tal

#### Scenario: Afirmacion de la discusion verificable desde el texto

- **WHEN** se lee en `08-discusion.tex` la explicacion rival de la mezcla de canales
- **THEN** la afirmacion de reducciones positivas en los tres canales remite a `tab:tiempos-canal` y al contraste de Wilcoxon intra-canal ya realizado
- **AND** el texto no afirma que la explicacion "se descartaria con un contraste intra-canal apareado" como si ese contraste no existiera

#### Scenario: Valores trazables al reporte y al memo

- **WHEN** se compara cada celda numerica de `tab:tiempos-canal` con `evaluation/report.md` y con `numeros-canonicos.md`
- **THEN** cada valor coincide con el reporte regenerado (con el redondeo declarado) y figura en el memo con su procedencia y estado `vigente`
- **AND** la tabla declara su linea de fuente y la fila telefonica conserva el rotulo de cota inferior

### Requirement: Convencion declarada del valor p frente a la hipotesis direccional de tiempos

Cuando la primera sub-hipotesis de tiempos se formule con una alternativa direccional (`H1: M_manual > M_automatizado`), la tesis SHALL declarar explicitamente la convencion de los valores p que reporta para los contrastes de tiempos: los valores p reportados son bilaterales (variante de dos colas de `scipy.stats.wilcoxon`, coherente con `W = min(T+, T-)`) y, por lo tanto, conservadores respecto de la hipotesis direccional. La tesis SHALL informar al menos una vez el valor p unilateral del contraste global (`1,54e-32`), calculado por el framework con la variante direccional, en el capitulo de marco metodologico y en el enunciado de la sub-hipotesis. Los valores p bilaterales vigentes (`3,08e-32` global, escenarios de sensibilidad y contrastes por canal) MUST NOT cambiar de valor, y ningun valor p de tiempos MUST quedar sin convencion declarada.

#### Scenario: Convencion declarada en metodologia y en la hipotesis

- **WHEN** se leen la subseccion de analisis estadistico de `04-marco-metodologico.tex` y el enunciado de la primera sub-hipotesis en `01-introduccion.tex`
- **THEN** ambos declaran que el p reportado es bilateral y conservador frente a la alternativa direccional
- **AND** ambos informan el p unilateral global `1,54e-32`, igual al valor vigente del memo

#### Scenario: Valores bilaterales preservados

- **WHEN** se buscan los valores p de tiempos en `01-introduccion.tex` y `07-resultados.tex`
- **THEN** el p global bilateral sigue siendo `3,08e-32` con `W = 363`, `T+ = 19.737` y `T- = 363`
- **AND** los p de los escenarios de sensibilidad y de los contrastes por canal quedan cubiertos por la misma convencion declarada

### Requirement: Comparacion de potencia homogenea sobre el tamano del efecto d_z

El analisis de potencia del marco metodologico SHALL comparar el efecto minimo detectable, expresado como tamano del efecto estandarizado de muestras pareadas `d_z`, con el `d_z` observado, calculado como la media de las diferencias pareadas dividida por su desvio estandar muestral. El texto MUST NOT comparar el efecto minimo detectable con la reduccion relativa (71,2 %) ni con ninguna otra magnitud no estandarizada. SHALL declarar los supuestos del efecto minimo detectable (alfa, lateralidad, potencia, `n` y la eficiencia relativa asintotica usada para el ajuste de la prueba de rangos) y, cuando se citen contrastes por canal, SHALL comparar el `d_z` de cada canal con el efecto minimo detectable para su propio `n`.

#### Scenario: d_z observado frente al minimo detectable

- **WHEN** se lee el analisis de potencia en `04-marco-metodologico.tex`
- **THEN** el efecto minimo detectable (`d_z` aproximadamente 0,20; 0,21 con la eficiencia relativa asintotica declarada) se compara con el `d_z` observado de 1,00
- **AND** la reduccion relativa del 71,2 % no aparece como termino de esa comparacion

#### Scenario: Supuestos y valores trazables

- **WHEN** se verifican los valores de potencia citados
- **THEN** alfa, lateralidad, potencia, `n` y la eficiencia relativa asintotica estan declarados en el texto
- **AND** el `d_z` observado y los efectos minimos detectables global y por canal figuran en `numeros-canonicos.md` con procedencia en el reporte regenerado

### Requirement: Verificabilidad del muestreo y de la asignacion por sector

La descripcion del muestreo en `04-marco-metodologico.tex` SHALL ser verificable con la informacion que el documento aporta. Si la distribucion del universo por sector esta disponible, la tesis SHALL reportarla junto a la distribucion de la muestra para que la proporcionalidad sea comprobable. Si no esta disponible, la tesis SHALL declarar que la composicion por sector de la muestra refleja la distribucion observada en el periodo relevado y que su proporcionalidad respecto del universo no es verificable, y MUST NOT afirmar una proporcionalidad respecto del universo que el documento no permite comprobar. En ambos casos la tesis SHALL discutir la consecuencia de la asignacion resultante para Bases de Datos (`n = 1`, clase no estimable) y la alternativa de una asignacion no proporcional con sobremuestreo de las clases minoritarias para replicaciones. El resumen y el abstract MUST describir el muestreo de forma coherente con el capitulo 4.

#### Scenario: Universo por sector disponible

- **WHEN** el autor aporta la distribucion del universo por sector
- **THEN** el capitulo 4 la reporta junto a la distribucion muestral (85/67/31/16/1)
- **AND** cada cifra nueva figura en `numeros-canonicos.md` con su procedencia

#### Scenario: Universo por sector no disponible

- **WHEN** la distribucion del universo por sector no esta disponible
- **THEN** el capitulo 4 declara que la composicion de la muestra refleja la distribucion observada en el periodo relevado y que la proporcionalidad frente al universo no es verificable
- **AND** el texto no afirma un muestreo proporcional al universo sin respaldo

#### Scenario: Asignacion de Bases de Datos discutida

- **WHEN** se lee la descripcion del muestreo
- **THEN** se explica que la asignacion dejo a Bases de Datos con un unico caso, no estimable para la inferencia por clase
- **AND** se menciona la asignacion no proporcional con sobremuestreo de clases minoritarias como alternativa para replicaciones

#### Scenario: Resumen y abstract coherentes

- **WHEN** se comparan `00-resumen.tex` (resumen y abstract) con el capitulo 4
- **THEN** la caracterizacion del muestreo es la misma en los tres lugares
- **AND** el abstract no conserva "proportional stratified sampling" si el capitulo 4 declara la proporcionalidad como no verificable

### Requirement: Procedimiento de cronometraje precisado y compatible con la mitigacion del efecto Hawthorne

La tesis SHALL describir el procedimiento de cronometraje manual de forma unica y precisa en `04-marco-metodologico.tex` (diseno experimental e instrumentos), `08-discusion.tex` (explicacion rival del efecto Hawthorne) y `11-aspectos-legales.tex` (sesion de esclarecimiento): quien cronometro, que conocia el operador cronometrado durante la campana, que aspecto concreto no se anuncio y que se informo en el debriefing. El texto MUST NOT afirmar a la vez que el cronometraje no fue anunciado al operador y que un companero lo cronometraba en vivo sin explicar como ambas afirmaciones son compatibles. SHALL declarar la granularidad observada de los registros manuales (valores multiplos de 5 s y mayormente de 10 s, verificable en el corpus) y su relacion con los escenarios de sensibilidad de 5 s y 10 s. Si el procedimiento no elimina el efecto Hawthorne, la tesis SHALL presentarlo como atenuado y residual, no como mitigado por completo.

#### Scenario: Sin contradiccion entre medicion no anunciada y cronometraje en vivo

- **WHEN** se leen la subseccion de diseno experimental y la de instrumentos de `04-marco-metodologico.tex`
- **THEN** el texto explica que conocia el operador y que aspecto de la medicion no se anuncio
- **AND** no subsisten juntas, sin explicacion, "no fue anunciado en tiempo real" y "lo cronometro en vivo el companero"

#### Scenario: Relato consistente entre capitulos

- **WHEN** se comparan `04-marco-metodologico.tex`, `08-discusion.tex` y `11-aspectos-legales.tex`
- **THEN** los tres describen el mismo procedimiento y el mismo alcance del conocimiento diferido
- **AND** el efecto Hawthorne figura como atenuado y residual si el procedimiento no lo elimina

#### Scenario: Granularidad declarada y verificable

- **WHEN** se lee la descripcion del instrumento manual
- **THEN** declara que los registros son multiplos de 5 s (199 de 200) y mayormente de 10 s (180 de 200)
- **AND** esas cifras coinciden con la granularidad emitida por el reporte de evaluacion y figuran en `numeros-canonicos.md`

### Requirement: Convencion unica del desvio estandar y correspondencia de los estadisticos de tiempo declarados

Todos los desvios estandar de tiempos que la tesis reporte SHALL usar la misma convencion que el framework de evaluacion (desvio muestral, divisor `n - 1`). El desvio del flujo automatizado SHALL reportarse como 13,52 s, y el valor 13,48 s (convencion poblacional) MUST NOT aparecer en las fuentes. Los estadisticos de tiempo que el marco metodologico declara como parte de la metrica de tiempo MUST coincidir con los que el capitulo de resultados efectivamente reporta.

#### Scenario: Desvio automatizado unificado

- **WHEN** se buscan los desvios estandar de tiempos en `07-resultados.tex` y `08-discusion.tex`
- **THEN** el desvio automatizado es 13,52 s y el manual 44,9 s, ambos con divisor `n - 1`
- **AND** `13,48` no aparece en ninguna seccion y figura como `retirado` en `numeros-canonicos.md`

#### Scenario: Estadisticos declarados igual a reportados

- **WHEN** se compara la definicion de la metrica de tiempo en `04-marco-metodologico.tex` con `tab:tiempos` y `tab:tiempos-canal`
- **THEN** cada estadistico declarado (media, mediana, desvio, minimo, maximo y los que se agreguen) se reporta en resultados
- **AND** no se declara un intervalo de confianza del tiempo medio que el capitulo de resultados no informe
