## MODIFIED Requirements

### Requirement: Estado de la segunda sub-hipotesis coherente con la variable medida

El estado de la segunda sub-hipotesis SHALL quedar fijado como "refutada" (design D3 de c-192),
con el denominador de los casos que tuvieron oportunidad de revision humana y con el matiz de
incertidumbre que el dictamen del 2026-11-09 sobre `v1.2.13` exige. El texto SHALL declarar la
estimacion de 25 de 147 casos revisados (17,0 %; IC de Wilson [11,8 %; 23,9 %]) y que, segun la
regla de tres vias declarada, la estimacion alcanza la cota de 0,15, de modo que la
sub-hipotesis resulta refutada. El texto SHALL ademas consignar el matiz explicito: el IC de
Wilson contiene 0,15 y la prueba binomial (25 exitos sobre 147 con p = 0,15) da p = 0,28, por lo
que la evidencia es compatible con un valor cercano al umbral y la lectura conservadora es que
no se puede descartar 0,15. Se conserva el cociente 25 de 200 (12,5 %; IC [8,6 %; 17,8 %]) como
dato secundario, con la advertencia de que cuenta 53 casos web sin oportunidad de revision. El
texto SHALL declarar que la revision humana de la campaña complementaria alcanzo solo los
canales de correo (66) y telefonia (81) por la regla de derivacion por reportante no
identificado, y que los 53 casos del formulario web no tuvieron revision. Las confirmaciones
SHALL informarse con ambos denominadores explicitos: 122 de 200 (61,0 %) y 122 de 147 (83,0 %);
MUST NOT quedar un "122 (61,0 %)" adyacente al denominador de 147 que pueda leerse como
122 de 147. Ese estado y su matiz SHALL ser identicos donde el veredicto se enuncia: 8.3
(`subsec:reduccion-intervencion`) y la Tabla 18 (`tab:cumplimiento-objetivos`, filas del
objetivo general y del objetivo especifico 4); la seccion 9.1 (`08-discusion.tex`) SHALL
mencionar la segunda sub-hipotesis al resumir el estado de la hipotesis principal y MAY llevar
el matiz. El resumen (`00-resumen.tex`) y el abstract MUST NOT superar 250 palabras cada uno; si
incluyen el matiz, SHALL compensar palabras en el mismo resumen. La celda del objetivo
especifico 4 de la Tabla 18 MUST NOT contradecir el veredicto: MUST NOT declarar a la vez
"refutada" y "sin medicion valida por la regla del reportante".

#### Scenario: Veredicto unico de la sub-hipotesis 2

- **WHEN** se comparan 8.3, 9.1 y las filas del objetivo general y del objetivo especifico 4 de la Tabla 18
- **THEN** todos declaran la sub-hipotesis 2 como "refutada" con el denominador de 25 de 147
- **AND** ninguno la declara "no concluyente" con 25 de 200 como unico fundamento
- **AND** la celda del objetivo especifico 4 no declara a la vez "refutada" y "sin medicion valida"

#### Scenario: Matiz de incertidumbre declarado

- **WHEN** se lee 8.3
- **THEN** figuran el IC de Wilson [11,8 %; 23,9 %] que contiene 0,15 y la prueba binomial con p = 0,28
- **AND** el texto declara que no se puede descartar 0,15 sin cambiar el veredicto "refutada"

#### Scenario: Denominadores del 122 explicitos

- **WHEN** se lee la oracion de las confirmaciones en 8.3
- **THEN** figura 122 de 200 (61,0 %) y 122 de 147 (83,0 %) con ambos denominadores explicitos
- **AND** no queda un "122 (61,0 %)" que pueda leerse como 122 de 147

#### Scenario: Estado unico de la sub-hipotesis 2

- **WHEN** se comparan el resumen, el abstract, 1.4, 4.7, 8.3, 9.1, el capitulo 10, la Tabla 18 y 11.3
- **THEN** todos declaran el mismo estado de la sub-hipotesis 2 ("refutada") con el mismo denominador (25 de 147)
- **AND** ninguno la declara "no concluyente" con 25 de 200 como unico fundamento
- **AND** ninguno la declara "refutada" por la tasa de 73,5 %

#### Scenario: Alcance de la revision declarado

- **WHEN** se lee 8.3
- **THEN** se declara que la revision humana alcanzo 66 casos de correo y 81 de telefonia y ninguno de los 53 del formulario web
- **AND** se declara que la regla del reportante determino que casos se revisaban

#### Scenario: Resumen sin ambiguedad de magnitud

- **WHEN** se lee la oracion del resumen y del abstract que enuncia los estados por sub-hipotesis
- **THEN** la cifra de intervencion nombra su magnitud y su denominador
- **AND** no queda un parentesis con 73,5 % y [67,0 %, 79,1 %] adyacente a la intervencion humana

#### Scenario: 11.3 reformulada

- **WHEN** se lee `subsec:medicion-intervencion`
- **THEN** no aparece "respecto del 73,5 %" como meta de reduccion
- **AND** se propone medir la variable con reportantes identificados en el directorio

## ADDED Requirements

### Requirement: Regla de hash de release sin imprimir el hash de la release previa

El commit de contenido que se etiqueta como release SHALL llevar, en el Anexo B
(`12-anexos.tex`), una oracion de reemplazo en lugar del hash completo de la release, que
declare que el PDF compilado en el propio tag no imprime ese hash y que el hash completo se
consigna en el commit que sigue al tag en la rama principal. El PDF etiquetado de una release
MUST NOT imprimir el hash de una release previa. El commit inmediatamente posterior al tag SHALL
reemplazar la oracion de reemplazo por el hash completo del commit de contenido, y los commits
posteriores MUST NOT modificar las fuentes de la tesis. El mecanismo (un commit no puede
contener su propio hash) SHALL explicarse sin imprimir el hash de una release anterior.

#### Scenario: PDF etiquetado sin hash ajeno

- **WHEN** se extrae el texto del PDF etiquetado de la release y se busca el hash de la release previa
- **THEN** el PDF etiquetado no contiene el hash de la release previa
- **AND** el Anexo B del PDF etiquetado muestra la oracion de reemplazo

#### Scenario: Commit del hash posterior al tag

- **WHEN** se compara el commit del tag con el commit inmediatamente posterior, limitado a `docs/Tesis/v10 (IA)/paper/sections`
- **THEN** `git diff --stat` entre ambos muestra una sola linea (la del hash)
- **AND** esa linea reemplaza la oracion de reemplazo por el hash completo del commit de contenido

### Requirement: Efecto minimo detectable del Spearman sin la eficiencia relativa de Wilcoxon

El efecto minimo detectable del contraste de posicion por correlacion de rangos de Spearman
SHALL calcularse con la transformacion de Fisher de la correlacion sin la correccion por
eficiencia relativa asintotica de Wilcoxon: `rho_MDE = tanh((z_{1-alfa/2} + z_{potencia}) /
sqrt(n - 3))`, que con `n = 110` (`n - 3 = 107`) da 0,2644. La tesis MUST NOT informar el MDE
del Spearman multiplicando el denominador por la ARE de Wilcoxon (0,864), que corresponde a la
prueba de rangos con signo y no a la correlacion de rangos. El valor corregido SHALL figurar en
la seccion 8.7 (`07-resultados.tex`) y en `docs/Tesis/Correcciones/numeros-canonicos.md` con su
fuente. `analisis/resultados.json` MUST NOT editarse; si conserva el valor previo, la tesis SHALL
declarar la discrepancia.

#### Scenario: MDE del Spearman reproducible

- **WHEN** se recalcula el MDE del Spearman con la formula y el `n` que declara el texto
- **THEN** el resultado es 0,2644 a cuatro decimales
- **AND** el texto no contiene el valor 0,2834 ni la multiplicacion por la ARE de Wilcoxon para el Spearman

#### Scenario: Registro del valor corregido

- **WHEN** se busca el MDE del Spearman en `numeros-canonicos.md`
- **THEN** figura 0,2644 con la formula sin ARE y la anotacion de la correccion

### Requirement: Atribucion separada del kappa de 1.6 y del doble etiquetado de la campana

La seccion 1.6 (`01-introduccion.tex`) SHALL atribuir cada coeficiente de acuerdo a su par de
evaluadores. El acuerdo moderado de 0,5569 (`p_o = 0,69`; `p_e = 0,30`) SHALL atribuirse al
doble etiquetado de la campana realizado por `E1` y `E2`. El acuerdo de 0,87 SHALL atribuirse al
par formado por el analista externo y el analista autor del trabajo, y SHALL informarse sin
intervalo de confianza cuando su tabla primaria no se conservo. La tesis MUST NOT atribuir el
0,5569 al par autor/analista ni presentar ambos valores como el mismo acuerdo. La descripcion
MUST NOT incluir datos personales: solo codigos y roles.

#### Scenario: Dos pares separados

- **WHEN** se lee 1.6 y se comparan sus menciones con 4.4, 8.7 y 9.3
- **THEN** el 0,5569 figura atribuido al par `E1`/`E2` y el 0,87 al par analista externo + analista autor
- **AND** ningun pasaje atribuye el 0,5569 al par autor/analista

### Requirement: Conjunto laxo del brazo manual por interseccion de los adicionales

La seccion 8.7 (`07-resultados.tex`, "Exactitud del brazo manual") SHALL definir el conjunto de
verdad laxo del brazo manual como el consenso de `E1` y `E2` mas la INTERSECCION de los sectores
adicionales de ambos etiquetadores, que es lo que calcula `evaluation/campana.py`
(`construir_referencia`). La tesis MUST NOT describirlo como la union de los adicionales. La
cifra publicada de exactitud laxa manual SHALL seguir siendo la que produce la interseccion (130
de 151); si se menciona la union, SHALL declararse solo como valor alternativo (137) con su
fuente, sin reemplazar la cifra publicada.

#### Scenario: Criterio del conjunto laxo exacto

- **WHEN** se busca "union de los sectores adicionales" en `07-resultados.tex`
- **THEN** no hay coincidencias
- **AND** la definicion nombra la interseccion de los adicionales de `E1` y `E2`

#### Scenario: Cifra laxa manual coherente

- **WHEN** se recalcula la exactitud laxa manual con la interseccion documentada
- **THEN** el resultado coincide con la cifra publicada (130 de 151)

### Requirement: Canal telefonico descrito por el callback de grabacion y residuales del dictamen v1.2.13

La seccion 6.3 (`06-implementacion.tex`, lista de recepcion) MUST NOT describir el canal
telefonico como "telefonia (trigger de Twilio)"; SHALL describirlo como "telefonia (callback de
grabacion de Twilio)", coherente con 6.4. La seccion 3.1 (`03-estado-del-arte.tex`) MUST NOT
atribuir a Xiong et al. (2024) una "poca capacidad para separar aciertos de errores"; SHALL decir
que predecir las fallas sigue siendo un desafio, conservando la sobreconfianza y la
concentracion en la parte alta de la escala, como en 2.5 y 9.2. La sigla `VIS` SHALL
desarrollarse en su primer uso en el cuerpo ("regla de visibilidad y derivacion por reportante no
identificado (VIS-005)") o agregarse al glosario, y cada entrada del glosario SHALL tener uso en
el cuerpo. La entrada bibliografica de FrugalGPT SHALL conservar la URL de OpenReview
(`cSimKw5p6R`) de TMLR como evidencia o SHALL agregar el preprint de arXiv (`2305.05176`) como
respaldo, con la decision registrada; MUST NOT inventarse un venue. El exceso de paginas sobre el
tope total de 100 SHALL registrarse como residual declarado en el libro mayor, con su magnitud,
fecha y decision, sin reduccion en este change.

#### Scenario: Canal telefonico en la lista de recepcion

- **WHEN** se busca "trigger de Twilio" en `06-implementacion.tex`
- **THEN** no hay coincidencias
- **AND** la lista de recepcion describe la telefonia por el callback de grabacion de Twilio

#### Scenario: Atribucion de Xiong atenuada

- **WHEN** se busca "separar aciertos de errores" en `03-estado-del-arte.tex`
- **THEN** no hay coincidencias
- **AND** el texto declara que predecir las fallas sigue siendo un desafio

#### Scenario: VIS desarrollada con uso

- **WHEN** se busca `VIS` con `rg -w` en `sections/`
- **THEN** figura desarrollada en su primer uso o en el glosario
- **AND** tiene uso en el cuerpo

#### Scenario: FrugalGPT sin venue inventado

- **WHEN** se lee la entrada de FrugalGPT en la bibliografia
- **THEN** conserva la URL de OpenReview de TMLR o agrega el preprint de arXiv como respaldo
- **AND** la decision figura registrada en el memo

#### Scenario: Exceso de paginas declarado

- **WHEN** se lee el libro mayor de paginas en `dictamen-correcciones.md`
- **THEN** figura el exceso sobre el tope de 100 con su magnitud, fecha y decision
- **AND** el PDF del tag de la release no supera 118 paginas

### Requirement: Trazabilidad del dictamen del 9 de noviembre sobre v1.2.13 en el registro y el Anexo I

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL incluir una seccion "Dictamen v10 /
v1.2.13 (2026-11-09) - c-192" con una matriz de 7 columnas (Rec | Sintesis | Change |
Archivo:linea | Ancla | Fragmento verificable | Estado) que cubra cada una de las cuatro
observaciones, el item 12 y cada residual, con su estado, y las decisiones de los autores del
design de c-192. `verificar_matriz_trazabilidad.py` SHALL reportar 0 fallas sobre el arbol y
sobre el tag de la release. El Anexo I (`sec:anexo-trazabilidad`) SHALL incluir una tabla de
trazabilidad del dictamen del 9-11 sobre `v1.2.13` (o actualizar la existente) con las secciones
tocadas y `\autoref`, sin numeros de linea. El archivo del dictamen
(`auditorias/Dictamen_Tesis_v10_v1.2.13_CONEAU_2026-11-09.md`) SHALL versionarse cuando este
disponible, sin bloquear la release.

#### Scenario: Matriz completa del dictamen v1.2.13

- **WHEN** se lee la seccion de c-192 de `dictamen-correcciones.md`
- **THEN** cada observacion, el item 12 y cada residual tiene una fila con archivo, fragmento verificable y estado
- **AND** `verificar_matriz_trazabilidad.py` reporta 0 fallas

#### Scenario: Anexo I actualizado

- **WHEN** se compila y se lee el Anexo I
- **THEN** la tabla de trazabilidad del dictamen del 9-11 sobre v1.2.13 resuelve con sus `\autoref`

#### Scenario: Versionado no bloqueante del dictamen

- **WHEN** el archivo del dictamen no esta todavia en `auditorias/`
- **THEN** la tarea de versionarlo queda declarada y la release no se bloquea
- **AND** cuando el archivo se agrega, queda versionado en `auditorias/`
