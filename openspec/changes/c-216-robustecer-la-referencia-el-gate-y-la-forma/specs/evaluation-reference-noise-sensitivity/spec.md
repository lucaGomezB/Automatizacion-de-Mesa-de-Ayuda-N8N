## Purpose

Cuantificar, de forma offline y reproducible, cuánto del error observado del clasificador
sobre la referencia arbitrada de `206` casos es atribuible a ruido de la referencia de verdad
consistente con el acuerdo inter-etiquetador medido, y cuánto es error robusto del clasificador,
sin cambiar ningún valor canónico ni exigir trabajo de campo.

## ADDED Requirements

### Requirement: RN-001 — Alcance, entradas versionadas y operación offline

El análisis SHALL medir solo la referencia de verdad del corpus arbitrado y su efecto sobre la
exactitud estricta y la macro-F1 del clasificador congelado. SHALL leer exclusivamente
artefactos versionados: `evaluation/data/campana/corpus_independiente_arbitrado.json`,
`evaluation/data/campana/predicciones_arbitrado.json`,
`evaluation/data/campana/doble_etiquetado_arbitrado.csv` y
`evaluation/data/campana/arbitraje_tres_vias.json`. MUST NOT invocar a Gemini, a la red ni al
clasificador, MUST NOT modificar los corpus, las predicciones ni ningún valor canónico, y MUST
NOT requerir trabajo de campo ni corrida paga. Antes de simular, el análisis SHALL reproducir
los anclajes canónicos `142/206` de exactitud estricta (`0,6893`) y macro-F1 `0,7024`; si no los
reproduce, SHALL abortar sin escribir salidas.

#### Scenario: Entradas y anclajes reproducidos

- **WHEN** el análisis se ejecuta sobre los cuatro artefactos versionados
- **THEN** reproduce `142/206` aciertos estrictos y macro-F1 `0,7024` antes de cualquier simulación
- **AND** registra el SHA-256 de cada entrada leída

#### Scenario: Inconsistencia detectada

- **WHEN** el conteo de casos, el número de discordantes o los anclajes no coinciden con los artefactos
- **THEN** el análisis termina con error y no escribe archivos de salida

#### Scenario: Sin red ni escritura fuera de su carpeta

- **WHEN** el análisis corre dos veces seguidas
- **THEN** no se realiza ninguna llamada de red y `git status` no muestra archivos modificados por la ejecución

### Requirement: RN-002 — Método primario: simulación de etiquetas calibrada al kappa observado

El análisis SHALL implementar una simulación Monte Carlo de referencias alternativas calibrada
al acuerdo observado entre `E3` y `E4` sobre el sector principal: `p_o = 0,6867` (`103` de
`150`) y kappa de Cohen `0,6055`. SHALL estimar una matriz de confusión fila-estocástica `Q`
entre la referencia arbitrada y las etiquetas recolectadas (las de `E3` y `E4` sobre los `206`
casos y las de `E5` sobre los `64` arbitrados) y SHALL definir la mezcla convexa
`Q_λ = (1 − λ)·Q + λ·m`, donde `m` es la distribución marginal empírica de clases, que degrada
la concordancia desde la del kernel empírico (`λ = 0`) hasta la independencia (`λ = 1`). SHALL
calibrar `λ` por bisección con semilla fija, de modo que una etiqueta simulada con `Q_λ*`
reproduzca el kappa observado contra la referencia dentro de una tolerancia declarada (a lo
sumo `±0,005`). Para cada una de las `B = 2000` réplicas, SHALL generar una referencia
alternativa por caso y recalcular la exactitud estricta y la macro-F1 del clasificador fijo.
SHALL informar la mediana, los percentiles `2,5` y `97,5`, la proporción de réplicas con
exactitud igual o superior a `0,6893` y la descomposición del error observado en una parte
atribuible a la referencia y una parte robusta al ruido de referencia. La simulación SHALL
rotularse como análisis de sensibilidad y MUST NOT presentarse como medición de la verdad
latente.

#### Scenario: Calibración del kappa

- **WHEN** se calibra `λ` con la semilla declarada
- **THEN** el kappa entre una etiqueta simulada con `Q_λ*` y la referencia difiere del observado `0,6055` en a lo sumo `0,005`
- **AND** el `λ` calibrado, la semilla y `B` quedan registrados en la salida

#### Scenario: Distribución y descomposición informadas

- **WHEN** se lee la salida del análisis
- **THEN** figuran la mediana, los percentiles `2,5` y `97,5` de la exactitud estricta y de la macro-F1 bajo referencias alternativas
- **AND** figura la descomposición entre error atribuible a la referencia y error robusto, rotulada como sensibilidad

### Requirement: RN-003 — Método secundario: cotas bajo un presupuesto máximo de error de referencia

El análisis SHALL informar cotas inferior y superior de la exactitud estricta bajo el supuesto
de que a lo sumo una fracción `δ` de las etiquetas de referencia es errónea, con `δ` derivada
del desacuerdo observado y de su cota superior de Wilson al 95 %. Las cotas SHALL calcularse de
forma distribution-free como `[max(0, (aciertos − m)/n), min(1, (aciertos + m)/n)]`, con
`m = δ·n` redondeado al entero más próximo, y SHALL rotularse como cotas, no como mediciones.
El análisis SHALL declarar que las cotas y la simulación son complementarias: la simulación
explora referencias plausibles y las cotas acotan el peor caso bajo un presupuesto declarado.

#### Scenario: Cotas informadas y rotuladas

- **WHEN** se lee la salida del análisis
- **THEN** figuran `δ`, `m` y las cotas inferior y superior de la exactitud estricta
- **AND** las cotas contienen el valor canónico `0,6893`
- **AND** se rotulan como cotas de sensibilidad, no como mediciones de la exactitud verdadera

### Requirement: RN-004 — Tratamiento explícito de los casos de discordancia de tres vías

El análisis SHALL identificar los `6` casos con bandera `tres_vias = true` en
`arbitraje_tres_vias.json` y, para cada uno, SHALL informar su identificador, las etiquetas de
`E3`, `E4` y `E5`, la referencia usada, si el clasificador acertó y el rango de exactitud
estricta que resulta de asignar el caso a cada una de sus tres etiquetas. MUST NOT presentar
ninguna de las tres etiquetas como verdadera ni elegir una asignación por conveniencia.

#### Scenario: Los seis casos quedan listados

- **WHEN** se lee la salida del análisis
- **THEN** figuran los `6` identificadores con sus tres etiquetas y la referencia usada
- **AND** figura el rango de exactitud estricta asociado a las tres asignaciones posibles
- **AND** no se afirma cuál etiqueta es la verdadera

### Requirement: RN-005 — Salidas versionadas, determinismo y registro canónico

El análisis SHALL implementarse como un script de solo lectura en
`evaluation/data/campana/analisis/analisis_ruido_referencia_c216.py` y SHALL escribir
`analisis_ruido_referencia_c216.json`, `analisis_ruido_referencia_c216.md` y
`analisis_ruido_referencia_c216.SHA256SUMS.txt` en esa misma carpeta, en UTF-8 sin BOM y LF.
Dos corridas con las mismas entradas SHALL producir salidas idénticas byte a byte y el script
SHALL imprimir el SHA-256 de cada salida. Cada cifra que llegue a la tesis SHALL registrarse en
una sección nueva del memo canónico con su archivo fuente y el comando que la produce. El
change MUST NOT modificar ningún valor ni estado `vigente` de las secciones anteriores del
memo.

#### Scenario: Reproducibilidad byte a byte

- **WHEN** el script se ejecuta dos veces sobre los mismos artefactos
- **THEN** el JSON, el Markdown y el archivo de sumas son idénticos byte a byte
- **AND** el script imprime el SHA-256 de cada salida

#### Scenario: Registro con procedencia

- **WHEN** se buscan en el memo canónico las cifras del análisis
- **THEN** cada una figura con su archivo fuente y el comando que la produce
- **AND** los valores `vigente` de las secciones anteriores conservan su valor y su estado