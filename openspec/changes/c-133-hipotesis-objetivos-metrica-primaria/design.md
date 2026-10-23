## Context

El change cierra las recomendaciones B4, B5 y B6 del dictamen CONEAU 2026-10-22 sobre la version de trabajo v10 (ver `proposal.md` - Why). Es documental: edita LaTeX bajo `docs/Tesis/v10 (IA)/paper/sections/` y dos memos de `docs/Tesis/Correcciones/`. Forma parte de la familia c-130..c-141 que atiende ese dictamen; varios de sus parrafos son compartidos con otros changes de la familia, y el orden de aplicacion lo fija c-141 (D7).

Convencion de transcripcion: los fragmentos ANTES/DESPUES de este documento se transcriben sin tildes por convencion de los artefactos OpenSpec del proyecto. Al aplicarlos en LaTeX se escriben con la acentuacion normalizada del manuscrito (requisito "Acentuacion normalizada del manuscrito", c-106), y los `grep` de verificacion usan subcadenas sin caracteres acentuados.

Restricciones que condicionan el diseno:

- **Numeros canonicos congelados** (`docs/Tesis/Correcciones/numeros-canonicos.md`, Gate 0 de c-102): toda cifra que el texto cite debe figurar alli con procedencia (archivo:linea) y estado; ninguna se inventa. La rama consumidora debe registrar en su `design.md` los sitios de propagacion con texto ANTES/DESPUES y la reversibilidad de cada decision editorial (requisito "Obligacion de propagacion de las ramas consumidoras" de `tesis-numeros-canonicos`).
- **Sin llamadas pagas ni re-ejecucion del clasificador.** Las caches `evaluation/predicciones.json` y `evaluation/predicciones_calibracion.json` estan en `.gitignore` (lineas 72-73) y **no existen en el arbol de trabajo actual**; su recuperacion es de c-131.
- **Presupuesto de paginas**: el PDF compilado tiene 101 paginas. Las ultimas paginas de los capitulos que este change edita, medidas con `pdftotext -layout` sobre `paper/main.pdf`, quedan asi: introduccion pp. 11-17 (p. 17 llena), marco metodologico pp. 31-39 (p. 39 con unas 3-4 lineas libres), resultados pp. 67-73 (p. 73 con unas 20 lineas libres), discusion pp. 74-80 (p. 80 llena), conclusiones pp. 81-83 (p. 83 llena); resumen p. 2 y abstract p. 3. Como cada capitulo termina en `\newpage`, cualquier crecimiento neto en la introduccion, la discusion o las conclusiones agrega una pagina. El tope global de la familia no se asume fijo en 101: lo decide c-141 en su gate G0, con consulta al usuario. c-133 solo se compromete a no aumentar paginas respecto del estado inmediatamente anterior a su apply (D8).
- **Presupuesto de palabras del resumen** (`<= 250`, regla de conteo de c-106: palabras de prosa, sin comandos LaTeX, sin la linea de palabras clave ni puntuacion suelta). Con un conteo de tokens con contenido alfanumerico, el resumen en espanol ya suma unas 266 palabras (256 sin tokens numericos) y el abstract unas 254 (244): el exceso es previo a este change.

Estado verificado de las fuentes (solo lectura; numeracion de `grep -n`):

- `01-introduccion.tex:34`: la segunda sub-hipotesis compara contra el proceso manual y "contra la fraccion esperada", que no se especifica; se declara "no contrastada por ausencia de registro primario".
- `01-introduccion.tex:36`: la tercera sub-hipotesis cita "macro-F1 de cinco clases de 0,5207".
- `01-introduccion.tex:38`: las dos hipotesis subsidiarias se enuncian sin contraste ni estado.
- `01-introduccion.tex:42,46,48,50,52`: objetivo general (tres componentes: tiempo de registro, calidad de la clasificacion, proporcion de intervencion humana) y objetivos especificos 1 ("comunicacion asincronica ... REST sobre HTTP cifrado"), 2 (umbral de 85 % y 0,85, con tres criterios fundados y una ultima oracion que repite lo dicho al inicio del parrafo), 3 ("sin incrementar la complejidad operativa percibida por los usuarios finales") y 4 ("tiempo medio de registro, dispersion, exactitud de clasificacion y proporcion de intervencion humana"). La pregunta subsidiaria 3 (`01:28`) pide integrar canales "sin degradar la latencia ni la calidad de la clasificacion".
- `05-arquitectura.tex:8` (`subsec:vision-general`): la terminacion TLS "corresponde al diseno y no a una capacidad verificada en la instancia publicada".
- `06-implementacion.tex:60` (`subsec:desafios-integracion`): "El nodo HTTP de N8N invoca el endpoint de clasificacion de manera sincronica".
- `04-marco-metodologico.tex:33` (`tab:variables`): el F1 macro se define sobre "cada uno de los cinco sectores objetivo"; `:65` afirma que la proporcion de intervencion humana "se reporta"; `:79` ya excluye Bases de Datos del "macro-F1 de umbral".
- `07-resultados.tex:107` (`subsec:matriz-metricas`; linea 108 en editores, por el CR suelto que documenta el memo): ya declara `0,6508` como macro-F1 de umbral y `0,5207` como informativo. `:136` describe el gate (propiedad de c-130); `:138` declara la sub-hipotesis no contrastada.
- `08-discusion.tex:10`: "Este hallazgo es consistente con la hipotesis subsidiaria sobre la eficiencia del esquema hibrido", apoyado solo en el 65,5 % de casos resueltos sin el modelo. `:30` y `:34` ya citan `0,6508` con su aclaracion.
- `08-discusion.tex:38-50` (`subsec:limitaciones-estudio`, hallazgo de c-136): "El estudio presenta seis limitaciones" y ninguna menciona la intervencion humana no medida. Sin embargo, `01-introduccion.tex:34` remite alli por esa razon y `10-recomendaciones.tex:8` afirma que la correccion de la medicion de intervencion humana ataca un defecto "reconocido entre las limitaciones". c-142 agrega antes de c-133 una limitacion sobre los ajustes con el corpus, de modo que la lista llegara con siete.
- Observacion A5 del dictamen (c-142): el vocabulario del filtro, las reglas de frontera del prompt y tau se ajustaron con el corpus de evaluacion. c-142 agrega `subsec:sensibilidad-ajustes` en `07-resultados.tex`, con la variante E4 (vocabulario previo al ajuste), y una limitacion en `08-discusion.tex`; se aplica antes de c-132 y c-133.
- `09-conclusiones.tex:6,22-28,35,37,39,41`: estado por sub-hipotesis; tabla con objetivo general y objetivos 1, 3 y 4 "Alcanzado"; objetivo 2 con "macro-F1 0,5207"; el parrafo de canales afirma, para el canal telefonico, "20,1 segundos ... una via practicamente util" sin la salvedad de cota inferior; esa salvedad (B13) es de c-135 y c-133 no toca esa oracion.
- `00-resumen.tex:13,29`: "el macro-F1 de cinco clases, 0,5207" / "the five-class macro-F1 was 0.5207".
- `numeros-canonicos.md`: el macro-F1 de cuatro clases figura `condicional` en la Seccion 3.2 y "Primaria de umbral" en la 3.6, mientras el item 5 de la Seccion 5 todavia lista `0,5207` como primario; la Seccion 7, punto 4, deja la decision "reversible si el autor prefiere 0,5207". Los porcentajes 65,5 % y 34,5 % se citan en `08-discusion.tex:10,58` pero no estan en el memo.
- `docs/deterministic_calibration.md:40-41` y `:67-68`: sobre el conjunto cortocircuitable `S` (131 casos), `precision_det(S) = 0,7405 (97/131)` y `precision_gem(S) = 0,6769 (88/130)`, con Gemini cacheado en la corrida FORCE-ESCALATE (cache `hybrid-v2`, 199 casos por Gemini y 1 por reglas; un caso de `S` sin prediccion de Gemini, excluido y no fabricado). Segun `openspec/changes/archive/2026-10-07-c-74-calibracion-cortocircuito-determinista/tasks.md:64`, el criterio comparativo del cortocircuito se adopto el 2026-10-07 despues de observar esa diferencia. La cache `hybrid-v2` nace en c-71 (2026-10-06), posterior a la migracion del clasificador a `gemini-3.6-flash` (commit `11036be`, 2026-09-24).
- `knowledge-base/01_vision_y_objetivos.md:46`: la meta a priori de intervencion humana era "Reduccion sustancial", sin cifra; el `9,5 %` alli consignado esta `retirado`.
- Requisitos vigentes de `openspec/specs/tesis-document/spec.md` que citan `0,5207` como el macro-F1 de referencia: "English abstract", "Alineacion de la tesis con el corpus real de evaluacion", "Coherencia de los datos en los capitulos 7.2 y 1.6", "Declaración del estado de la hipótesis principal" y "Presupuesto de palabras del resumen en español". Se modifican en la delta (D1). "Correccion de defectos residuales de forma y consistencia del PDF" y "Reducción sin pérdida de contenido científico" siguen cumpliendose sin cambios, porque `0,5207` sigue en el PDF, fuera del intervalo de la fila del objetivo 2.

## Goals / Non-Goals

**Goals:**

- Cerrar B4, B5 y B6 con el minimo de texto nuevo, de forma coherente entre resumen, abstract, introduccion, metodologia, resultados, discusion y conclusiones.
- Hacer contrastable la segunda sub-hipotesis tal como queda escrita, sin fabricar una confirmacion con los datos actuales.
- Dar estado explicito a las hipotesis subsidiarias y sustituir la afirmacion no sostenida sobre la eficiencia del esquema hibrido por un contraste acotado con sus salvedades.
- Fijar un unico macro-F1 primario y rotular el otro en cada aparicion.
- Hacer coherente la remision de la segunda sub-hipotesis con la lista de limitaciones del estudio.
- No introducir ninguna cifra fuera de `numeros-canonicos.md`; dejar coherente el propio memo.
- No aumentar paginas ni palabras del resumen y del abstract, y fijar por escrito la propiedad de cada parrafo compartido.

**Non-Goals:**

- No calcular metricas nuevas por canal, por etapa ni laxas (c-131), no redefinir el gate ni la confianza de la etapa determinista (c-130), no computar el balance neto (c-132), no rehacer el analisis de sensibilidad de los ajustes con el corpus (c-142), no tocar contrastes de tiempos, valor p unilateral ni `d_z` (c-134), cronologia (c-135), recomendaciones (c-136), ortotipografia general (c-137), estado del arte (c-138) ni atribuciones (c-139).
- No re-ejecutar el clasificador, no invocar Gemini, no recuperar caches ni calcular la prueba de McNemar (todo de c-131). La alternativa paga de ~0,1 USD no se ejecuta en este change.
- No agregar la salvedad de cota inferior del canal telefonico en las conclusiones (B13, c-135) y no fijar el tope global de paginas (c-141, gate G0).
- No reformular el enunciado de ningun objetivo (general ni especificos) para acomodarlo a los resultados; solo cambia su grado de cumplimiento.
- No sustituir la exactitud estricta por la laxa como criterio del umbral del 85 %.
- No crear tags ni releases, no regenerar el render final (c-141) y no corregir el exceso previo de palabras del resumen mas alla de lo que piden las propias ediciones del change (D8).

## Decisions

### D1 - Metrica primaria del F1 macro: `0,6508` sobre cuatro clases estimables

El macro-F1 de umbral sobre las cuatro clases estimables (`0,6508`) es el primario y el unico referente del criterio `0,85`. El de cinco clases (`0,5207`) aparece solo acompanado de su aclaracion. Rotulos canonicos:

- Primario: "macro-F1 de umbral, sobre las cuatro clases estimables" (en ingles: "threshold macro-F1 over the four estimable classes").
- Secundario: "macro-F1 de cinco clases (0,5207), que incluye Bases de Datos, con un unico caso y no estimable" (formas abreviadas admitidas: "0,5207 con las cinco clases", "0,5207 al incluir la clase de soporte unitario").

Justificacion que el texto debe recoger (en `07-resultados.tex`, donde hay margen de pagina): con un unico caso, el F1 de Bases de Datos depende de un solo incidente y pesaria un quinto del promedio de cinco clases; la exclusion aplica la regla general del memo para clases de soporte unitario, no una eleccion ad hoc. Ademas, ambos valores quedan por debajo de `0,85`, de modo que la eleccion no altera el veredicto de la tercera sub-hipotesis ni el del objetivo 2. Esa robustez es la defensa explicita frente a la sospecha de elegir la metrica segun el resultado.

**Alternativas consideradas:** (a) `0,5207` como primario (la condicion de reversibilidad del memo, Seccion 7, punto 4): se descarta porque resultados y metodologia ya definen `0,6508` como metrica de umbral, y promediar una clase no estimable contradice la regla del memo para clases de soporte unitario; (b) informar ambos sin jerarquia: se descarta porque el dictamen exige un valor primario unico.

**Reversibilidad:** reversible si el autor decide que `0,5207` sea el primario; en ese caso se invierten los rotulos en los mismos sitios de la tabla ANTES/DESPUES y el memo vuelve a marcar `0,6508` como informativo.

**Efecto en specs:** la delta modifica los cinco requisitos vigentes que citan `0,5207` como el macro-F1 de referencia (ver Context).

### D2 - Segunda sub-hipotesis: fraccion esperada explicita, estado "no contrastada"

Se reformula con una fraccion esperada numerica y se mantiene su estado:

- **Enunciado:** en el flujo automatizado, la proporcion de casos que requieren accion manual de un operador (definicion ya operacionalizada en `tab:variables`) no supera `0,15`.
- **Origen de la cota:** `0,15 = 1 - 0,85`, el complemento del umbral de exactitud fijado a priori en el segundo objetivo especifico. Un clasificador que alcanzara ese umbral dejaria a lo sumo esa fraccion de casos para correccion humana; un flujo que exigiera mas accion manual trasladaria a los operadores una carga mayor que la que el propio criterio de desempeno admite.
- **Contraste y falsacion:** la proporcion con su intervalo de confianza de Wilson al 95 %; se falsa si el limite superior del intervalo no queda por debajo de `0,15`. Es el mismo estilo que la tercera sub-hipotesis.
- **Transparencia:** el texto declara que la formulacion original (comparacion con el proceso manual, donde la intervencion es total por definicion, contra una fraccion esperada no especificada) no era contrastable y que la cota se explicita en esta version. Asi la reformulacion no se presenta como si hubiera estado desde el inicio.
- **Estado:** "no contrastada por ausencia de registro primario". No existe registro por caso de accion manual, y las derivaciones del gate (0 de 200) no operacionalizan la variable: la etapa determinista no activa el gate (c-130) y Gemini nunca declaro una confianza inferior a 0,85. El texto **no** debe presentar el 0 de 200 como contraste ni como confirmacion: seria una confirmacion espuria que repetiria el defecto senalado en A1.
- **Memo:** `0,15` entra como "cota de la segunda sub-hipotesis" con procedencia en el umbral del 85 % (`01-introduccion.tex:48`), con la nota "explicitada por c-133; no es un resultado".
- **Remision coherente (hallazgo de c-136):** la sub-hipotesis remite a `subsec:limitaciones-estudio`, cuya lista no menciona la intervencion humana.
  - Opcion principal: incorporar a esa lista una limitacion de una oracion (T18): la proporcion de intervencion humana por caso no se midio por falta de registro primario, de modo que la segunda sub-hipotesis queda no contrastada. Tambien se actualiza el conteo de la oracion introductoria al numero real de limitaciones listadas al momento del apply: tras c-142 la lista deberia tener siete, de modo que la nueva seria la octava, pero el cardinal se verifica contra la lista y no se asume. Asi la remision de T1 apunta a un destino que la sostiene y queda respaldada la afirmacion de `10-recomendaciones.tex:8`.
  - Fallback, si el autor lo prefiere o la discusion no admite esas lineas: en T1 remitir a `subsec:reduccion-intervencion` y avisar a c-136 (posterior) para que ajuste su anclaje en `10-recomendaciones.tex:8`.

**Alternativas consideradas:**

- (B) Reemplazarla por una hipotesis de cobertura efectiva del gate ("el gate opera sobre toda clasificacion automatica" o "deriva al menos una fraccion `c0` de los errores"). Es contrastable ya y quedaria refutada (opera sobre 69 de 200 clasificaciones; 0 de 53 errores derivados). Se descarta como opcion principal por tres razones: tras c-130 la exencion de la etapa determinista sera explicita por diseno, de modo que la refutacion seria por construccion y no empirica; `c0` tampoco tiene un valor a priori; y cambiaria el titular del resumen (dos sub-hipotesis refutadas) y obligaria a modificar el requisito vigente "Rotulo de la sub-hipotesis de intervencion humana como no contrastada". Queda como pregunta abierta para el autor.
- (C) Conservar el enunciado y solo agregar la fraccion: se descarta, porque la comparacion "respecto del proceso manual" sigue siendo trivial.
- (D) Usar `9,5 %` del `knowledge-base`: prohibido, es un valor `retirado`.

**Reversibilidad:** reversible si el autor fija otra cota a priori documentable o elige la alternativa (B); en ese caso se actualizan el memo y los sitios T1, T9, T17 y T18.

**Coordinacion:** c-136 (subseccion "correccion de la medicion de intervencion humana") debe proponer como linea futura el registro primario por caso que permitiria contrastar esta sub-hipotesis contra `0,15`.

### D3 - Hipotesis subsidiarias: estados y contraste acotado de la de eficiencia

- **Subsidiaria 1 (integracion multicanal sin cuellos de botella): "no contrastada".** No se midio la capacidad bajo carga concurrente (la invocacion N8N-clasificacion es sincronica, punto unico de falla reconocido en `subsec:desafios-integracion`) ni, salvo que c-131 la haya publicado, la calidad por canal. La latencia por canal (`tab:tiempos-canal`) y la exactitud por canal que aporte c-131 son evidencia descriptiva compatible, no un contraste. Aunque c-131 aporte la calidad por canal, el estado se mantiene, porque los cuellos de botella siguen sin medirse.
- **Subsidiaria 2 (eficiencia del esquema hibrido frente a solo modelo): "contrastada de forma acotada"** (opcion principal). Se define en la introduccion como evidencia descriptiva favorable sobre un subconjunto, sin prueba inferencial, que no equivale a "confirmada". Evidencia ya documentada y sin costo: en los 131 casos que resuelve la etapa de reglas, esta acierta 97 (`0,7405`); Gemini, ejecutado sobre 130 de esos casos con el cortocircuito deshabilitado, acierta 88 (`0,6769`); y el esquema evita esas invocaciones (65,5 % de los casos). La latencia no se midio por etapa: solo se infiere por construccion, salvo que c-131 la reporte. Salvedades que el texto debe declarar:
  1. Sin prueba pareada. Requiere los pares por caso de la cache FORCE-ESCALATE, ausente del arbol; si c-131 la recupera, es c-131 quien calcula la prueba.
  2. Estimacion dentro de la muestra. El vocabulario del filtro, las reglas de frontera del prompt y el umbral tau se ajustaron con el mismo corpus (observacion A5 del dictamen, analizada por c-142 en `subsec:sensibilidad-ajustes`), y el criterio comparativo se adopto tras observar esta diferencia (c-74). El ajuste out-of-fold del umbral mitiga, pero no elimina, ese sesgo. `S` queda definido por la no ambiguedad de la senal: los umbrales 0 y 0,5166 seleccionan los mismos 131 casos, asi que la seleccion no recorto casos desfavorables. El texto califica ambas cifras como estimaciones dentro de la muestra y remite a `subsec:sensibilidad-ajustes`.
  3. Denominadores 131 frente a 130: un caso sin prediccion de Gemini, excluido y no fabricado.
  4. Las predicciones de Gemini provienen de la corrida de calibracion (`hybrid-v2`), no de la oficial. Sobre los 69 casos restantes, ambas corridas difieren en un acierto neto (exactitud global 0,7300 offline frente a 0,7350 oficial, `docs/deterministic_calibration.md:171-174`). La coincidencia de modelo y prompt la verifica c-131 con `cache_meta` al recuperar la cache.
- **Prueba pareada (de c-131):** la prueba exacta de McNemar sobre los 130 pares (b = reglas aciertan y Gemini falla; c = a la inversa; `p` bilateral, convencion de c-134) la calcula c-131, dueno de las caches, y la registra en el memo. c-133 no la calcula. Si al momento de su apply figura en el memo, T10 la cita, y aun con significacion el rotulo sigue "acotado" por la salvedad 2; si no figura, el texto dice "sin prueba pareada". Si c-131 la publicara despues del apply de c-133, la actualizacion de esa oracion queda para la integracion (c-141).
- **Regla de decision con la variante E4 de c-142:** si en la variante E4 (vocabulario previo al ajuste con el corpus) la etapa de reglas no supera a Gemini en exactitud sobre los casos que resuelve, la ventaja observada depende del ajuste dentro de la muestra: la subsidiaria 2 se rotula "no contrastada" y T10 aplica la variante de fallback. Si E4 mantiene la ventaja, se conserva "contrastada de forma acotada" con la calificacion de estimacion dentro de la muestra. Si c-142 no reporta E4, se conserva el rotulo acotado con esa calificacion y la ausencia se anota en `dictamen-correcciones.md`. c-133 remite a E4 a traves de `subsec:sensibilidad-ajustes`; si citara cifras de E4, deben figurar en el memo (las registra c-142).
- **Fallback:** si el autor rechaza el contraste acotado, si el registro de c-131 sobre `cache_meta` revela otro modelo o prompt, o si se cumple la regla de decision de E4, la subsidiaria 2 se rotula "no contrastada" y se retira la frase de `08-discusion.tex:10` (primera opcion del dictamen).

**Alternativas consideradas:** (a) "no contrastada" para ambas y retirar la frase: es mas simple, pero desperdicia evidencia ya documentada que el propio dictamen sugiere usar, y queda como fallback; (b) re-ejecutar Gemini sobre los 131 casos (~0,1 USD): es redundante, porque los datos existen; solo procede si la procedencia de la cache no se puede verificar, con aprobacion explicita del usuario, y le corresponde a c-131.

**Reversibilidad:** reversible al fallback sin otros efectos (sitios T3, T10, T11 y T14).

### D4 - Tabla de cumplimiento: regla de grados, desglose y reversion

Regla aplicada a cada fila (vocabulario vigente, sin estados nuevos):

- "Alcanzado": cada componente exigido por el enunciado literal del objetivo (`01-introduccion.tex`) esta evidenciado en la version evaluada.
- "Alcanzado parcialmente": al menos un componente evidenciado y al menos uno no cumplido o no medido. La celda de evidencia nombra el componente faltante.
- "No alcanzado": no se cumple el criterio del objetivo.

Filas resultantes:

- **Objetivo general: "Alcanzado parcialmente"**, con el desglose dentro de la celda de evidencia: tiempo de registro alcanzado (71,2 %); calidad de la clasificacion evaluada, por debajo del umbral (objetivo 2); intervencion humana no medida. Se elige una fila con desglose interno en lugar de tres subfilas para contener la altura de la tabla (D8); el dictamen pide el estado individual de cada componente, no un formato. Si no agrega lineas, la celda puede remitir a `subsec:balance-neto` (c-132) como sustento de la viabilidad condicional.
- **Objetivo 1: "Alcanzado parcialmente"**: arquitectura integrada sobre REST; invocacion sincronica (`subsec:desafios-integracion`) y TLS no verificado en la instancia publicada (`subsec:vision-general`). El enunciado del objetivo no se reformula.
- **Objetivo 2: "No alcanzado"**: exactitud 73,5 %, IC [67,0 %, 79,1 %]; macro-F1 de umbral 0,6508 (0,5207 con cinco clases, una no estimable).
- **Objetivo 3: "Alcanzado parcialmente"**: integracion (`subsec:capa-canales`) y latencia por canal (`tab:tiempos-canal`); calidad por canal no medida. Como c-131 se aplica antes, la celda cita su tabla o subseccion de calidad por canal; solo si c-131 no la publico, dice "no medida".
- **Objetivo 4: "Alcanzado parcialmente"**: tiempo y dispersion comparados (`subsec:comparacion-tiempos`); exactitud solo del flujo automatizado (la del brazo manual no se midio; remite a `subsec:balance-neto`, de c-132); intervencion humana no medida.
- **Objetivo 5:** sin cambio.
- **Objetivo 6: "Alcanzado"**, decision de c-133 con la evidencia de c-142 (recomendacion del orquestador). La evidencia se amplia: tipologia de errores (`subsec:analisis-errores`), calibracion por etapa (etiqueta de c-131) y analisis de sensibilidad de los ajustes (`subsec:sensibilidad-ajustes`, de c-142). Si al aplicar falta alguna de esas piezas o alguna contradice la caracterizacion de la confianza, se aplica la regla general de esta decision (por ejemplo, "Alcanzado parcialmente" si la calibracion por etapa no se publico).

Reglas de reversion, fijadas antes de conocer los datos que las disparan:

- **Objetivo 1 con c-140:** vuelve a "Alcanzado" solo si c-140 se aplica y cita evidencia para cada propiedad faltante: TLS verificado en la instancia publicada y comunicacion asincronica (cola o callback). Si solo resuelve el TLS, la fila sigue "Alcanzado parcialmente" y su frase conserva solo la invocacion sincronica. Como la validacion experimental corrio sin esas propiedades, la celda dice "incorporado despues de la validacion experimental". c-140 se aplica despues de c-133 y queda autorizado a actualizar solo esa fila y la oracion del objetivo 1 en `09:35`, segun esta regla.
- **Objetivo 3 con los datos de c-131 (aplicado antes):** al aplicar c-133, la fila pasa a "Alcanzado" solo si se cumplen tres condiciones: (i) c-131 reporta la exactitud estricta por canal con IC de Wilson; (ii) el IC de cada canal contiene la exactitud global (0,735), es decir, no hay evidencia de degradacion (rotulado como tal, no como "sin degradacion"); y (iii) el autor acepta que la "complejidad operativa percibida" se satisface por construccion (los usuarios conservan sus canales). Si falta cualquiera, sigue "Alcanzado parcialmente" con la frase actualizada.

**Alternativas consideradas:** (a) reformular los objetivos 1 y 3 para que su enunciado coincida con lo construido, opcion que el dictamen menciona para el 1: se descarta porque reescribir objetivos despues de conocer los resultados resta credibilidad a la tabla; (b) mantener "Alcanzado" para el general con una nota: se descarta porque, desglosado, un componente no se midio.

### D5 - Propagacion de estados a la prosa

La prosa debe coincidir con la tabla y con D2/D3:

- `09-conclusiones.tex:6`: el objetivo general se cumple parcialmente y el estado por sub-hipotesis agrega el de las subsidiarias.
- `09-conclusiones.tex:35`: el parrafo de arquitectura se condensa y declara el cumplimiento parcial del objetivo 1.
- `09-conclusiones.tex:37`: el parrafo del clasificador hibrido remite al contraste acotado y no a una eficiencia demostrada.
- `09-conclusiones.tex:39`: el parrafo de canales rotula como no contrastada la subsidiaria 1 y declara el cumplimiento del objetivo 3 en su dimension de construccion. **No toca la oracion del canal telefonico** ("El canal telefonico ... demostracion de laboratorio"), cuya salvedad de cota inferior (B13) agrega c-135.
- `09-conclusiones.tex:41`: el parrafo de comparacion explicita lo que el objetivo 4 no cubre.
- `08-discusion.tex:10`: reemplaza la frase de consistencia por el contraste acotado (D3).
- `07-resultados.tex:138`: alinea el estado de la segunda sub-hipotesis.
- `08-discusion.tex` (`subsec:limitaciones-estudio`): incorpora la limitacion de intervencion humana no medida y actualiza el conteo (D2, T18).

### D6 - Numeros nuevos y memo canonico (Gate 0 primero)

Antes de editar los `.tex` se actualiza `numeros-canonicos.md`:

- **Seccion 3.2:** el macro-F1 de cuatro clases estimables `0,6508` pasa de `condicional` a `vigente`, con la nota "Primaria de umbral (c-133 D1)". La fila de `0,5207` agrega "Informativa; toda cita lleva su aclaracion".
- **Seccion 3.3:** agregar `65,5 %` (131/200) y `34,5 %` (69/200), con procedencia `evaluation/report.md:9-10`, `08-discusion.tex:10,58`.
- **Nueva Seccion 3.7, "Contraste acotado de la hipotesis subsidiaria de eficiencia (c-133)":**
  - `precision_det(S) = 0,7405 (97/131)`, procedencia `docs/deterministic_calibration.md:40,67`.
  - `precision_gem(S) = 0,6769 (88/130)`, procedencia `:41,68`.
  - Notas: cache FORCE-ESCALATE `hybrid-v2`; un caso excluido; comando de reproduccion `PYTHONPATH=../.. python3 -m evaluation.deterministic_measurement --umbral-actual 1.0`, que requiere la cache, hoy ausente (recuperacion a cargo de c-131).
  - `0,15`, cota de la segunda sub-hipotesis (`1 - 0,85`), procedencia `01-introduccion.tex:48`, estado `vigente`, nota "explicitada por c-133; no es un resultado".
  - McNemar: c-133 no agrega filas; si c-131 registro b, c y `p`, el texto cita esas filas.
- **Encabezado y decisiones previas:** agregar la linea "Upsert c-133". Anotar el item 5 de la Seccion 5 ("superado por c-133 D1: el primario de umbral es 0,6508") y el punto 4 de la Seccion 7 ("decision ratificada por c-133"). No se edita el resto del texto historico de c-102.

Toda cifra que aparezca en el texto nuevo debe figurar en el memo; la tarea de verificacion lo comprueba por `grep`.

### D7 - Propiedad de parrafos y orden de aplicacion

Orden definitivo fijado por c-141: G0 (gate de paginas de c-141) -> c-130 -> c-134 (bloque de codigo) -> c-131 -> c-142 -> c-132 -> **c-133** -> c-134 (bloque de tesis) -> c-138 -> c-136 -> c-135 -> c-139 -> c-140 -> c-137 -> c-141. Consecuencias:

- Al aplicarse c-133 ya estan los datos de c-131 (calidad por canal y, si pudo calcularla, la prueba de McNemar), el analisis de sensibilidad de c-142 (`subsec:sensibilidad-ajustes`, variante E4 y su limitacion nueva) y los textos de c-132, cuyas clausulas c-133 conserva literalmente en la forma en que c-132 las dejo.
- Los changes posteriores conservan literalmente las oraciones de c-133.
- Autorizaciones: c-135 edita la oracion del canal telefonico de `09:39` (B13); c-140 puede actualizar la fila del objetivo 1 y su oracion en `09:35` segun la regla de D4; si la prueba de McNemar aparece despues del apply de c-133, la oracion de `08:10` la actualiza c-141.

Protocolo comun: antes de editar un archivo compartido, cada change relee el parrafo vigente y conserva literalmente las oraciones asignadas a otros; los conflictos se escalan al orquestador.

| Archivo | Parrafo o elemento (numeracion actual de `grep -n`) | Propietario |
|---|---|---|
| `00-resumen.tex` | :9 / :25 (descripcion del sistema) | c-133, solo para compresion si el conteo supera 250 (D8) |
| `00-resumen.tex` | :13 / :29, oraciones de exactitud, macro-F1 y estado por sub-hipotesis | c-133 |
| `00-resumen.tex` | :13 / :29, oraciones de tiempos y Wilcoxon | sin cambio (c-134 decide si la convencion de `p` lo requiere) |
| `00-resumen.tex` | :15 / :31 (viabilidad) | c-132 (aplicado antes; c-133 no lo toca) |
| `01-introduccion.tex` | :18 (mediciones preliminares, 15 % de derivacion erronea) | c-132 |
| `01-introduccion.tex` | :32 (primera sub-hipotesis, H1) | c-134 (B12) |
| `01-introduccion.tex` | :34 (H2), :36 (H3), :38 (subsidiarias) | c-133 |
| `01-introduccion.tex` | :48, solo la ultima oracion (compensacion; se conservan los tres criterios y sus fuentes) | c-133 |
| `01-introduccion.tex` | :66 (justificacion academica) | c-139 |
| `01-introduccion.tex` | :76 (delimitaciones, fechas) | c-135 |
| `04-marco-metodologico.tex` | `tab:variables`, fila "F1 macro promediado" (:33) | c-133 |
| `04-marco-metodologico.tex` | :65, oraciones "La tercera..." y "La cuarta..." | c-133 |
| `04-marco-metodologico.tex` | :65, oracion nueva sobre exactitud laxa | c-131 |
| `04-marco-metodologico.tex` | :79, oracion "La clase de soporte unitario..." | c-133 |
| `04-marco-metodologico.tex` | resto de `subsec:analisis-estadistico` y `subsec:amenazas-validez` | c-134 / c-135 |
| `07-resultados.tex` | :6 (parrafo introductorio) | c-135 (B10) |
| `07-resultados.tex` | :107, parrafo del marco metrico | c-131 (aplicado antes; c-133 conserva literal sus agregados) |
| `07-resultados.tex` | :107, oracion del macro-F1 | c-133 |
| `07-resultados.tex` | :136 (gate) | c-130 |
| `07-resultados.tex` | `subsec:sensibilidad-ajustes` (nueva) | c-142 (aplicado antes; c-133 solo la cita desde `08:10` y la fila del objetivo 6) |
| `07-resultados.tex` | :138 (estado de H2) | c-133 |
| `07-resultados.tex` | `subsec:calibracion`, `tab:tiempos-canal`, :32 | c-131 / c-134 |
| `08-discusion.tex` | :8 (estado de la hipotesis; la oracion "Tres aspectos..." como compensacion opcional) | c-133 |
| `08-discusion.tex` | :10 (eficiencia del esquema hibrido) | c-133 |
| `08-discusion.tex` | :14 (carga rutinaria, 32,2 h) | c-132 |
| `08-discusion.tex` | `subsec:balance-neto` (nueva) | c-132 (c-133 solo la cita desde la tabla de objetivos) |
| `08-discusion.tex` | :16 (gate y calibracion) | c-130 / c-131 |
| `08-discusion.tex` | :20 (explicaciones rivales, desagregado por canal) | c-134 |
| `08-discusion.tex` | :30, :34 (macro-F1 ya rotulado) | c-133, solo verificacion |
| `08-discusion.tex` | limitacion nueva sobre los ajustes con el corpus | c-142 (aplicado antes) |
| `08-discusion.tex` | :38 (conteo de limitaciones, que c-142 deja en siete) y limitacion nueva al final de la lista (T18) | c-133 |
| `08-discusion.tex` | :46 (cuarta limitacion) | c-135 |
| `09-conclusiones.tex` | :6, salvo la clausula "...resulto viable, eficiente y economicamente accesible para organizaciones medianas" | c-133 |
| `09-conclusiones.tex` | :6, esa clausula | c-132 (aplicado antes; c-133 la conserva literal) |
| `09-conclusiones.tex` | :10 y `tab:cumplimiento-objetivos` | c-133 (c-140, posterior, solo la fila del objetivo 1) |
| `09-conclusiones.tex` | :35, :37 | c-133 (en :37 usa la terminologia de c-130 para la etapa determinista; c-140, posterior, solo la oracion del objetivo 1 en :35) |
| `09-conclusiones.tex` | :39, salvo la oracion del canal telefonico | c-133 |
| `09-conclusiones.tex` | :39, oracion del canal telefonico ("El canal telefonico ... demostracion de laboratorio") | c-135 (B13); c-133 no la toca |
| `09-conclusiones.tex` | :41, oracion de intervencion humana y objetivo 4 | c-133 |
| `09-conclusiones.tex` | :41, clausula "el sistema libera al personal tecnico ... resolucion efectiva de los casos" | c-132 (aplicado antes; c-133 la conserva literal) |
| `09-conclusiones.tex` | :43 y `subsec:aportes-generalizacion` | fuera de c-133 (c-131 / c-132) |

### D8 - Presupuesto de paginas y de palabras

Meta: variacion de paginas nula, medida compilando inmediatamente antes y despues de aplicar c-133. Se comparan el total de paginas y las paginas de inicio de cada capitulo tocado y del siguiente. Estimacion por capitulo, en lineas de texto de cuerpo (unas 14 palabras por linea):

| Capitulo (paginas) | Crecimiento bruto | Compensacion propia | Neto estimado | Holgura |
|---|---|---|---|---|
| Introduccion (11-17) | H2 +1,5; H3 +0,5; subsidiarias +1,5 | ultima oracion del parrafo del objetivo 2 (-2,5) | +0 a +1 | ninguna (p. 17 llena) |
| Marco metodologico (31-39) | tabla +0,5; :65 +0,5; :79 +0,5 | - | +1,5 | 3-4 lineas (compartidas con c-134/c-135) |
| Resultados (67-73) | :107 +2,5; :138 +1 | - | +3,5 | ~20 lineas en v1.1.1, que c-142 consume en parte con `subsec:sensibilidad-ajustes` |
| Discusion (74-80 en v1.1.1) | :10 ~0 (reescritura de longitud neutra); T18 +2,5 | :8 "Tres aspectos..." (-1) | +1,5 | ninguna (p. 80 llena; c-142 y c-132 agregan texto antes) |
| Conclusiones (81-83) | tabla +4; :6 +1,5; :41 +1; :39 +0,5 (sin tocar la oracion telefonica) | :35 (-1,5); :37 (-2) | +2 a +3,5 | ninguna (p. 83 llena) |
| Resumen / abstract (2-3) | macro-F1 +4 / +3 palabras | oracion de estados -11 / -8 palabras | -7 / -5 palabras | tope de 250 palabras |

Si tras las compensaciones listadas algun capitulo crece una pagina, el exceso (lineas y paginas) se registra en `dictamen-correcciones.md` y se deriva al gate de paginas G0 de c-141, que fija el tope global. No se recorta texto asignado a otros changes. La estimacion anticipa un riesgo alto de una pagina mas en las conclusiones y un riesgo moderado en la discusion. Para el resumen, si tras las ediciones el espanol sigue por encima de 250 palabras (estimacion: ~259), c-133 comprime la descripcion del sistema (:9), que no tiene otro propietario, hasta `<= 250`; el abstract (~249 estimado) se verifica con la misma regla. c-132 debe conservar ese tope.

### D9 - Textos propuestos (ANTES -> DESPUES)

Fragmentos ANTES literales salvo tildes. Los DESPUES son la redaccion objetivo: el apply puede ajustarla para cumplir D8, sin cambiar cifras, rotulos ni estados.

| Id | Sitio | ANTES | DESPUES |
|---|---|---|---|
| T1 | `01:34` (H2) | "La segunda postula que la automatizacion no incrementa la proporcion de intervencion humana respecto del proceso manual: su contraste previsto es la proporcion de casos derivados a revision por gate contra la fraccion esperada, y su criterio de falsacion es que esa proporcion no resulte inferior a la esperada. No se realiza con la evidencia disponible ---no existe un registro primario de intervencion por caso y el gate de confianza (inferior a 0,70) no deriva casos en el corpus---, de modo que se declara \emph{no contrastada por ausencia de registro primario} y no se cuantifica (vease \autoref{subsec:limitaciones-estudio})." | "La segunda postula que la proporcion de casos del flujo automatizado que requieren accion manual de un operador no supera 0,15, complemento del umbral de exactitud fijado a priori en el segundo objetivo especifico; se contrasta con el intervalo de Wilson de esa proporcion y se falsa si su limite superior no queda por debajo de 0,15. Esta cota explicita la fraccion esperada que la formulacion original, referida al proceso manual ---donde la intervencion es total por definicion---, no especificaba, por lo que aquella no era contrastable. Con la evidencia disponible tampoco esta se contrasta: no existe registro primario de intervencion por caso y las derivaciones del gate no la miden, porque la etapa deterministica no lo activa; se declara \emph{no contrastada por ausencia de registro primario} y no se cuantifica (vease \autoref{subsec:limitaciones-estudio})." |
| T2 | `01:36` (H3) | "(exactitud no inferior al 85~\% y F1 macro no inferior a 0,85)" ... "y macro-F1 de cinco clases de 0,5207 (\autoref{sec:resultados})" | "(exactitud no inferior al 85~\% y F1 macro de umbral no inferior a 0,85)" ... "y macro-F1 de umbral de 0,6508 sobre las cuatro clases estimables (\autoref{sec:resultados})" |
| T3 | `01:38` (subsidiarias), al final | (sin estado) | "Ninguna tiene contraste formal: la primera se declara \emph{no contrastada} y la segunda solo admite el contraste acotado de la \autoref{subsec:interpretacion-resultados}, sin prueba inferencial." Con el fallback de D3: "Ninguna tiene contraste formal y ambas se declaran \emph{no contrastadas}." |
| T4 | `01:48` (objetivo 2), ultima oracion | "Se trata, en consecuencia, de un criterio de desempeno verificable contra la exactitud observada y su intervalo de confianza, distinto del contraste sobre la mediana de los tiempos formulado en la \autoref{subsec:hipotesis-trabajo}." | (se elimina: repite la segunda oracion del parrafo; la distincion con el contraste de tiempos ya consta en H3) |
| T5 | `04:33` (`tab:variables`) | "Promedio aritmetico del valor F1 calculado de forma independiente para cada uno de los cinco sectores objetivo." | "Promedio aritmetico del valor F1 de cada sector; la metrica de umbral excluye los sectores con soporte unitario, no estimables." |
| T6 | `04:65` | "La cuarta es la proporcion de intervencion humana, que se reporta de forma rotulada en dos dimensiones complementarias:" | "La cuarta es la proporcion de intervencion humana, prevista en dos dimensiones complementarias rotuladas:" ... y al final de la oracion: "; en la version evaluada no se midio por ausencia de registro primario (\autoref{subsec:hipotesis-trabajo})" |
| T7 | `04:79` | "La clase de soporte unitario (Bases de Datos, \(n = 1\)) se declara no estimable y se excluye del macro-F1 de umbral." | "La clase de soporte unitario (Bases de Datos, \(n = 1\)) se declara no estimable y se excluye del macro-F1 de umbral, contra el cual se evalua el criterio de 0,85; el de cinco clases se informa como complementario." |
| T8 | `07:107`, oracion del macro-F1 | "El macro-F1 de umbral se reporta sobre las cuatro clases estimables (0,6508), excluida Bases de Datos (\(n = 1\), no estimable), y el de cinco clases (0,5207) se conserva como valor informativo." | "El macro-F1 de umbral, metrica primaria contra la que se evalua el criterio de 0,85, se reporta sobre las cuatro clases estimables (0,6508), excluida Bases de Datos (\(n = 1\), no estimable: su F1 depende de un unico incidente y pesaria un quinto del promedio), y el de cinco clases (0,5207) se conserva como valor informativo; ambos quedan por debajo del criterio, de modo que la eleccion no altera el veredicto." |
| T9 | `07:138` | "La sub-hipotesis de intervencion humana por caso se declara no contrastada por ausencia de registro primario: la proporcion no se computa como resultado, de modo que el aporte operativo asociado al gate queda, por lo tanto, como no medido." | "La segunda sub-hipotesis ---proporcion de casos con accion manual no superior a 0,15 (\autoref{subsec:hipotesis-trabajo})--- se declara no contrastada por ausencia de registro primario: la proporcion no se computa como resultado y las derivaciones del gate no la sustituyen, de modo que el aporte operativo asociado al gate queda como no medido." |
| T10 | `08:10` (completo) | "La reduccion de tiempo se sostiene incluso al incorporar el costo de inferencia ... dado que la primera etapa deterministica del clasificador resuelve el 65,5~\% de los casos sin invocar al modelo de Google. Este hallazgo es consistente con la hipotesis subsidiaria sobre la eficiencia del esquema hibrido: ... Desde una perspectiva operativa, esta propiedad ... y no al volumen completo de incidentes." | "La reduccion de tiempo se sostiene aun computando la inferencia externa: la etapa deterministica resuelve el 65,5~\% de los casos sin invocar al modelo. La hipotesis subsidiaria de eficiencia del esquema hibrido admite un contraste acotado: en esos 131 casos la etapa de reglas acerto 97 (0,7405) y Gemini, ejecutado sobre 130 de ellos con el cortocircuito deshabilitado, 88 (0,6769), estimaciones dentro de la muestra (\autoref{subsec:sensibilidad-ajustes}). El esquema no resigno exactitud en ese subconjunto y evito sus invocaciones, pero la diferencia carece de prueba pareada, proviene del corpus con que se ajustaron el vocabulario, las reglas del prompt y el punto de operacion, y la latencia no se midio por etapa: la hipotesis queda contrastada solo de forma acotada. El costo de inferencia recae asi unicamente en los casos que el filtro no resuelve." (Con McNemar disponible, "carece de prueba pareada" se reemplaza por el resultado de la prueba; con el fallback de D3, incluida la regla de decision de E4, la segunda a cuarta oraciones se reemplazan por "La hipotesis subsidiaria de eficiencia del esquema hibrido no se contrasto: resolver casos sin el modelo no demuestra mayor eficiencia sin comparar la exactitud de cada alternativa.") |
| T11 | `09:6` | "El trabajo desarrollado ha cumplido con el objetivo general ... como medio: la combinacion de N8N ..." ... "la exactitud estricta del 73,5~\% y el F1 macro quedaron por debajo" ... "El estado de la hipotesis principal se declara, en consecuencia, por sub-hipotesis: confirmada en tiempo de registro, refutada en el umbral de clasificacion y la sub-hipotesis de intervencion humana por caso se declara no contrastada por ausencia de registro primario." | "El trabajo desarrollado ha cumplido parcialmente el objetivo general de evaluar la viabilidad y el desempeno de la automatizacion del registro inicial de incidentes ---no se midio la proporcion de intervencion humana---, con el desarrollo y la implementacion del sistema como medio. La combinacion de N8N ... [clausula de c-132, literal, en la forma que dejo c-132]" ... "la exactitud estricta del 73,5~\% y el macro-F1 de umbral (0,6508) quedaron por debajo" ... "Por sub-hipotesis, la hipotesis principal se confirma en tiempo de registro y se refuta en el umbral de clasificacion, y la de intervencion humana queda no contrastada por ausencia de registro primario; de las subsidiarias, la de integracion multicanal no se contrasto y la de eficiencia del esquema hibrido solo admitio un contraste acotado (\autoref{subsec:interpretacion-resultados})." |
| T12 | `09:22-26` (filas) | general, 1, 3 y 4 "Alcanzado"; 2 "... macro-F1 0,5207" | Segun D4 (la fila del objetivo 4 remite a `subsec:balance-neto`; la del objetivo 6 amplia su evidencia con la calibracion por etapa de c-131 y `subsec:sensibilidad-ajustes` de c-142). Objetivo 2: "Exactitud 73,5~\%, IC [67,0~\%, 79,1~\%]; macro-F1 de umbral 0,6508 (0,5207 con cinco clases, una no estimable)" (el corchete del IC queda cerrado). |
| T13 | `09:35` | Parrafo de tres oraciones sobre principios de diseno, cinco capas y eleccion tecnologica | "La arquitectura de cinco capas ---canales de entrada, orquestacion, procesamiento, inferencia y persistencia--- distribuyo las responsabilidades entre componentes independientes comunicados mediante interfaces REST, y la eleccion de tecnologias maduras y autoalojadas (Docker, PostgreSQL, N8N) respondio a las restricciones presupuestarias, cambiarias y normativas de las organizaciones medianas argentinas. El primer objetivo especifico se alcanza, sin embargo, solo parcialmente: la invocacion de N8N al servicio de clasificacion es sincronica y la terminacion TLS prevista en el diseno no se verifico en la instancia publicada." |
| T14 | `09:37` | "... resulto, sin embargo, el rasgo mas relevante del sistema: la mayor parte del volumen se resuelve sin inferencia externa y el modelo se emplea como arbitro de ultimo recurso antes que como clasificador universal, con el equilibrio entre costo, latencia y exactitud que se detalla en la \autoref{subsec:subsistema-clasificacion}." | "Sobre esa arquitectura se construyo el clasificador hibrido, cuyo desempeno quedo por debajo de las cotas del segundo objetivo especifico (\autoref{sec:discusion}). La estrategia compositiva ---un filtro deterministico de primera etapa y un modelo de lenguaje grande reservado para los casos que el filtro no resuelve [terminologia de c-130]--- resulto el rasgo mas relevante del sistema: el 65,5~\% de los casos se resuelve sin inferencia externa y, en ese subconjunto, sin perdida de exactitud frente al modelo segun el contraste acotado de la \autoref{subsec:interpretacion-resultados}, insuficiente para confirmar la hipotesis subsidiaria de eficiencia." |
| T15 | `09:39`: primera y tercera oraciones, mas una oracion nueva al final. La segunda oracion (canal telefonico) queda intacta: es de c-135 (B13) | "La integracion de los tres canales paralelos dentro de un unico flujo de orquestacion confirmo que la diversidad de vias de entrada no introduce dispersion operativa cuando la normalizacion se realiza tempranamente en el flujo." ... "La decision de normalizar la entrada en el propio N8N, antes de invocar al servicio de clasificacion, resulto acertada: aislo la complejidad de cada protocolo de recepcion del nucleo de procesamiento, permitiendo que el servicio Python operara siempre sobre la misma estructura de datos independientemente del canal de origen." | "La integracion de los tres canales en un unico flujo de orquestacion quedo construida y operativa." [oracion del canal telefonico: sin cambios en c-133] "La normalizacion de la entrada en el propio N8N, antes de invocar al servicio de clasificacion, aislo la complejidad de cada protocolo de recepcion del nucleo de procesamiento. Estos resultados son compatibles con la hipotesis subsidiaria de integracion multicanal, pero no la contrastan: no se midio la capacidad bajo carga concurrente [ni la calidad de clasificacion por canal, si c-131 no la publico], de modo que el tercer objetivo especifico se alcanza solo en su dimension de construccion." (Si c-131 publico la calidad por canal, la oracion final remite a su etiqueta; si la fila del objetivo 3 pasa a "Alcanzado" segun D4, la clausula final se reemplaza por esa remision.) |
| T16 | `09:41` | "La intervencion humana por caso en el flujo automatizado queda no contrastada por ausencia de registro primario, de modo que el aporte operativo asociado al gate de revision se declara como no medido:" | "La comparacion cubre el tiempo y la dispersion, pero no la exactitud del brazo manual ni la intervencion humana por caso, que queda no contrastada por ausencia de registro primario; por eso el cuarto objetivo especifico se alcanza parcialmente y el aporte operativo asociado al gate de revision se declara como no medido:" [clausula de c-132, literal, en la forma que dejo c-132] |
| T17 | `00:13` / `00:29` | "y el macro-F1 de cinco clases, 0,5207. El estado de la hipotesis principal se declara por sub-hipotesis: se confirma en la reduccion del tiempo de registro, se refuta en el umbral de clasificacion y la sub-hipotesis de intervencion humana por caso se declara no contrastada por ausencia de registro primario." / "and the five-class macro-F1 was 0.5207. The state of the main hypothesis is declared per sub-hypothesis: it is confirmed in registration time, refuted in the classification threshold, and not tested due to the absence of a primary record for per-case human intervention." | "y el macro-F1 de umbral, sobre las cuatro clases estimables, 0,6508. Por sub-hipotesis, la hipotesis principal se confirma en tiempo de registro y se refuta en el umbral de clasificacion, y la de intervencion humana queda no contrastada por ausencia de registro primario." / "and the threshold macro-F1, over the four estimable classes, 0.6508. Per sub-hypothesis, the main hypothesis is confirmed in registration time, refuted in the classification threshold, and not tested for human intervention due to the absence of a primary record." |
| T18 | `08:38` y final de la lista de `subsec:limitaciones-estudio` | Tras c-142: "El estudio presenta siete limitaciones que deben considerarse al interpretar los hallazgos y al planificar replicaciones futuras." (las seis de v1.1.1 mas la de c-142; ninguna trata la intervencion humana). El cardinal se verifica contra la lista al aplicar, sin asumirlo. | "El estudio presenta ocho limitaciones [o el numero real al momento del apply] que deben considerarse..." y, al final de la lista: "Octavo [u ordinal que corresponda], no se conservo un registro primario de la accion manual de los operadores por caso, de modo que la proporcion de intervencion humana no se midio y la segunda sub-hipotesis queda no contrastada (\autoref{subsec:reduccion-intervencion})." Con el fallback de D2 no se agrega la limitacion, y en T1 la remision pasa a `\autoref{subsec:reduccion-intervencion}`. |

Comprobacion de rotulos: tras T1-T18, `0,5207` solo aparece en `07:107`, `08:30` y la fila del objetivo 2, siempre con su aclaracion; `0,6508` aparece rotulado como "de umbral" o "cuatro clases estimables".

## Risks / Trade-offs

- **[La reformulacion de H2 se lee como ajuste posterior a los datos (HARKing)]** -> Mitigacion: la cota deriva de un umbral fijado a priori, el texto declara que se explicita en esta version y que la formulacion original no era contrastable, y la sub-hipotesis sigue no contrastada: de ella no se extrae ninguna conclusion.
- **[El 0 de 200 del gate se usa como confirmacion de H2]** -> Mitigacion: D2 lo prohibe expresamente; el texto explica por que las derivaciones del gate no operacionalizan la variable.
- **[El contraste acotado de la subsidiaria 2 se percibe como circular]** -> Mitigacion: el texto declara las cuatro salvedades de D3 y el rotulo "acotado"; queda el fallback a "no contrastada".
- **[La ventaja de la etapa de reglas depende de ajustes hechos con el propio corpus (A5)]** -> Mitigacion: las cifras se califican como estimaciones dentro de la muestra con remision a `subsec:sensibilidad-ajustes`, y la regla de decision de E4 (D3) rotula la subsidiaria "no contrastada" si con el vocabulario previo la ventaja desaparece.
- **[La cache de calibracion corresponde a otro modelo o prompt]** -> Mitigacion: c-131 verifica `cache_meta` al recuperar la cache; si no coincide, c-133 aplica el fallback de D3.
- **[Crecimiento de paginas en capitulos con la ultima pagina llena]** -> Mitigacion: compensaciones propias de D8, medicion antes/despues y derivacion del exceso al gate G0 de c-141, sin recortar parrafos ajenos.
- **[La limitacion nueva agrega lineas en una discusion que ya crece con `subsec:balance-neto` de c-132]** -> Mitigacion: limitacion de una oracion, compensacion en `:8` y, si no alcanza, el fallback de D2 con aviso a c-136.
- **[Resumen por encima de 250 palabras antes del change]** -> Mitigacion: las ediciones de c-133 reducen palabras; si hace falta, se comprime la descripcion del sistema (D8); c-132 hereda el tope.
- **[Conflictos de edicion con c-130, c-131, c-132, c-134, c-135 y c-140]** -> Mitigacion: tabla de propiedad de D7, orden fijado por c-141 y relectura previa de cada parrafo compartido.
- **[Las clausulas de c-132 ya no coinciden con el texto de v1.1.1 cuando se aplica c-133]** -> Mitigacion: c-133 relee cada parrafo compartido y conserva literal la forma que dejo c-132; las verificaciones de esas clausulas usan `git diff`, no cadenas fijas.
- **[El criterio de "sin evidencia de degradacion" del objetivo 3 resulta laxo]** -> Mitigacion: se rotula como ausencia de evidencia, no como ausencia de degradacion, y la mejora a "Alcanzado" exige ademas la decision del autor.
- **[Requisitos vigentes de la spec citan 0,5207 como el macro-F1 de referencia]** -> Mitigacion: la delta modifica los cinco requisitos afectados.
- **[Referencias por numero de linea desplazadas (CR suelto en `07-resultados.tex`, ediciones de otros changes)]** -> Mitigacion: las tareas ubican cada sitio por etiqueta o por subcadena con `grep`.

## Migration Plan

1. Precondiciones (orden de c-141): c-130, c-131, c-142 y c-132 aplicados. Relevar lo que publicaron:
   - c-130: terminologia de la etapa determinista.
   - c-131: calidad por canal, prueba de McNemar y verificacion de `cache_meta`.
   - c-142: `subsec:sensibilidad-ajustes`, resultado de la variante E4 (para la regla de decision de D3) y su limitacion nueva (cardinal de la lista).
   - c-132: `subsec:balance-neto` y la forma final de sus clausulas en `09-conclusiones.tex` y `00-resumen.tex`.
2. Linea base: compilar el PDF del arbol vigente y registrar total de paginas, paginas de inicio de los capitulos y conteo de palabras del resumen y del abstract.
3. Gate 0: actualizar `numeros-canonicos.md` (D6).
4. Editar por bloques: B6 (T2, T5, T7, T8, T12-objetivo 2, T17), luego B5 (T1, T3, T9, T10, T11, T14, T15, T18) y luego B4 (T12 con las filas del objetivo general y de los objetivos 1, 3, 4 y 6, T13 y T16), con las compensaciones de D8.
5. Compilar, medir y compensar hasta variacion de paginas nula, o documentar el exceso para c-141.
6. Verificar con `grep` (rotulos, estados, cifras contra el memo) y registrar la seccion del change en `dictamen-correcciones.md`.
7. Regenerar `tesis_para_agente.md` como verificacion y ejecutar `openspec validate --strict`.

Rollback: `git checkout <commit-previo> -- <archivos>` y recompilar (ver `proposal.md`). No hay tags ni codigo que restaurar.

## Open Questions

1. **Segunda sub-hipotesis (decision de autor):** confirmar la opcion A (cota `0,15 = 1 - 0,85`, estado "no contrastada") o elegir la B (cobertura efectiva del gate, contrastable y refutada). Si se prefiere otra cota, debe existir un fundamento a priori documentable.
2. **Subsidiaria de eficiencia (decision de autor):** confirmar el rotulo "contrastada de forma acotada" con las salvedades de D3 o aplicar el fallback "no contrastada" con retiro de la frase.
3. **Objetivo 3 tras c-131:** confirmar si el autor acepta que la complejidad percibida se satisface por construccion (condicion iii de D4). Sin esa aceptacion, la fila queda "Alcanzado parcialmente" aunque c-131 aporte la calidad por canal.

Resueltas por el orquestador:

- El tope de paginas lo decide c-141 en su gate G0, con consulta al usuario.
- B13 queda en c-135 (su D10); c-133 no toca la oracion del canal telefonico.
- La prueba de McNemar la calcula c-131; c-133 solo la cita si existe.
- c-132 se aplica antes de c-133, en el orden fijado por c-141.
- c-142 se aplica antes de c-132 y de c-133. El objetivo 6 lo decide c-133 con la evidencia de c-142 (recomendacion: "Alcanzado").
