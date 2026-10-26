## Context

El change cierra la observacion de fondo A3 del dictamen CONEAU 2026-10-22 sobre la tesis v10 (`auditorias/Dictamen_Tesis_v10_v1.1.0_CONEAU_2026-10-22.md`: VEREDICTO punto 3, seccion 7 (c) y su parrafo de "Observaciones adicionales", RECOMENDACION A3; ver `proposal.md` - Why). Es documental: edita LaTeX bajo `docs/Tesis/v10 (IA)/paper/sections/` y dos memos de `docs/Tesis/Correcciones/`. No exige mediciones nuevas: todos los insumos ya estan en el documento.

Estado verificado de las fuentes (solo lectura, release `v1.1.1`; numeracion de `grep -n`, que coincide con la del editor porque los archivos ya no contienen CR sueltos):

- `01-introduccion.tex:18` (planteamiento): las "mediciones preliminares realizadas durante una semana laboral representativa" dan 42 incidentes diarios, 2 min 45 s de registro manual y "una tasa de derivacion erronea inicial cercana al 15 %". El parrafo declara que los 2 min 45 s fueron una estimacion a priori sin cronometraje por caso, luego corregida a 61,6 s; el 15 %, de identico origen, no se califica ni se re-mide. El mismo parrafo proyecta "32,2 horas-persona por trimestre" y cierra con "Este tiempo representa un costo de oportunidad significativo para la organizacion".
- `01-introduccion.tex:48` (segundo criterio del umbral del 85 %): "el costo organizacional de una derivacion erronea se estima en el orden de 10 a 15 minutos adicionales de reasignacion, estimacion propia de los autores ... sin un registro cuantitativo conservado".
- `01-introduccion.tex:62` (justificacion, dimension organizacional): "libera capacidad operativa del personal tecnico, reduce el tiempo de respuesta percibido por los usuarios ... permite cuantificar esa mejora ... para estimar el retorno esperado de una inversion similar".
- `04-marco-metodologico.tex:45,51`: universo `N ~ 2.646 = 42 x 63` dias habiles. `04-marco-metodologico.tex:55` y `:87`: los dos analistas que etiquetaron la referencia son las mismas personas que operaron el brazo manual.
- `12-anexos.tex` (`sec:anexo-corpus`): cada caso tiene siete campos (`id`, `descripcion`, `canal_origen`, `sector_asignado`, `sectores_adicionales`, `tiempo_manual_s`, `tiempo_automatizado_s`); ninguno registra la derivacion efectuada por el operador del brazo manual. Confirmado sobre `data/Corpus Tesis - Hoja 1 (pseudonimizado).csv`.
- `07-resultados.tex:75` (147/200 = 73,5 %) y `:107` (IC de Wilson [67,0 %; 79,1 %]; referencia multietiqueta en 107/200 = 53,5 % de los casos). El valor "26,5 %" NO figura literalmente en el `.tex`: es `53/200 = 1 - 0,735`.
- `08-discusion.tex:14` (`subsec:interpretacion-resultados`): abre con "El sistema absorbe la carga rutinaria sin sustituir el juicio humano en los casos que verdaderamente lo demandan. Este equilibrio entre automatizacion y supervision preserva la calidad del servicio y libera capacidad operativa significativa."; proyecta 32,2 h con nota al pie (`43,8 s x 2.646 / 3.600`) y cierra con "La magnitud de esta liberacion ---equivalente a unas cuatro jornadas laborales completas de un operador--- transforma la automatizacion del registro de un proyecto de optimizacion marginal en una intervencion con impacto organizacional medible."
- `08-discusion.tex:16`: parrafo del gate y la calibracion ("el gate de revision (confianza inferior a 0,70) no derivo ningun caso"), dominio de `c-130`.
- `08-discusion.tex:50`: sexta limitacion (etiquetadores = operadores). `:54`: "pueden obtener beneficios sustanciales". `:58`: costo economico (infraestructura 24-32 USD/mes; API ~1 USD/trimestre, "un valor marginal frente a las 32,2 horas-persona liberadas"). `:60`: "beneficios cuantificados ---reduccion del 71,2 % ... y exactitud estricta del 73,5 %---".
- `09-conclusiones.tex:6`: "resulto viable, eficiente y economicamente accesible para organizaciones medianas". `:41`: "el sistema libera al personal tecnico de la carga rutinaria de registro, redirigiendo ese tiempo hacia la resolucion efectiva de los casos". `:47`: "resulto una alternativa viable para la clasificacion de tickets". `:49`: "su costo operativo esta dominado por el consumo de API de inferencia" (contradice `08-discusion.tex:58`: la infraestructura, 72-96 USD por trimestre, supera en mas de un orden de magnitud a la API, 1-2 USD por trimestre).
- `00-resumen.tex:15` y `:31`: "confirman la viabilidad tecnica, economica y operativa" / "confirm the technical, economic, and operational feasibility" (34 y 31 palabras).
- `10-recomendaciones.tex:30` (`subsec:estudios-replicacion`): replicaciones por tamano, sector y region; nada sobre exactitud manual.
- `docs/Tesis/Correcciones/numeros-canonicos.md`: Seccion 3.1 (`43,82 s` vigente; el `.tex` lo aproxima como 43,8 s), 3.2 (`0,7350`, IC Wilson), 3.4 (`~2.646`, `~32,2 h` vigentes). No hay entrada para el 15 %, los 10-15 min ni el 26,5 %.
- `evaluation/predicciones.json` esta en `.gitignore` y no existe en el arbol de trabajo local: la exactitud laxa no puede computarse aqui sin re-ejecutar el clasificador (dominio de `c-131`).

Restricciones que condicionan el diseno:

- **Numeros canonicos congelados:** ningun valor existente cambia; todo valor nuevo se registra en el memo con procedencia y estado (`tesis-numeros-canonicos`, "Registro canonico con procedencia por valor"); esta rama declara sus objetivos de propagacion ANTES/DESPUES y la reversibilidad de cada decision editorial ("Obligacion de propagacion de las ramas consumidoras").
- **Sin fabricacion:** no se inventa ni se estima una tasa manual "medida"; la rejilla de sensibilidad se rotula como supuesta.
- **Presupuesto de paginas:** el PDF tiene 101 paginas; c-116/c-121 lo trataron como tope duro. Los capitulos 1, 9, 10 y 11 terminan en paginas casi llenas (31-32 lineas de ~33). Interlineado doble (~400-440 palabras por pagina); flotantes a espacio simple.
- **Resumen:** requisito vigente "Presupuesto de palabras del resumen en espanol" (<= 250 palabras de prosa, regla de conteo de c-106 D5). Con esa regla, el resumen actual suma ~264-266 palabras (ES) y ~254 (EN): posible exceso preexistente que no introduce este change (ver Risks).
- **Archivos con CRLF:** los `.tex` y `.md` objetivo tienen fin de linea CRLF en el arbol de trabajo (`core.autocrlf=true`, LF en el indice).

## Goals / Non-Goals

**Goals:**

- Computar en la discusion el balance neto entre el ahorro de registro y el costo de las derivaciones erroneas, con formula explicita, tabla de escenarios y punto de equilibrio.
- Declarar que la exactitud manual no se midio, que el 15 % es preliminar y que, por ello, el balance es indeterminado.
- Presentar la viabilidad tecnica y economica como sostenidas y la operativa como condicional en resumen, abstract, introduccion, discusion y conclusiones.
- Retirar la afirmacion sobre la preservacion del juicio humano por el gate.
- Conectar con una linea futura de medicion y registrar los valores nuevos en el memo canonico.
- Mantener el resumen neutro en palabras y el impacto en paginas en <= +1 pagina neta.

**Non-Goals:**

- No se mide ni se estima la exactitud manual, ni se re-ejecuta el clasificador, ni se computa la exactitud laxa (`c-131`).
- No se cambia ningun valor canonico existente (32,2 h, 43,82 s, 73,5 %, IC, 2.646, etc.).
- No se reescribe la descripcion del gate ni el parrafo `08-discusion.tex:16` (`c-130`); no se toca `tab:cumplimiento-objetivos`, las hipotesis, la metrica primaria ni la justificacion del umbral del 85 % en `01-introduccion.tex:48` (`c-133`); no se agregan subsecciones de recomendaciones (`c-136`); no se hace la revision ortotipografica general (`c-137`); no se crean tags ni se regeneran `tesis_para_agente.md`, `tesis_completa_extraida.txt` ni `tesis_para_evaluacion.txt` (`c-141`).
- No se valoriza el tiempo en moneda (el documento no tiene datos salariales).
- No se editan `04-marco-metodologico.tex`, `07-resultados.tex` ni `Bibliography_base.bib`.

## Decisions

### D1 - Ubicacion: subseccion propia despues de "Implicancias practicas"

Se crea `\subsection{Balance neto de la automatizacion}\label{subsec:balance-neto}` en `08-discusion.tex`, entre `subsec:implicancias-practicas` y `subsec:reflexiones-generalizacion`. Razones: (i) queda contigua al parrafo economico (`:58`), que define el costo monetario de operacion, de modo que los planos economico y operativo se leen juntos; (ii) da una etiqueta unica que el resumen no necesita pero que citan la introduccion, las conclusiones, las recomendaciones y, si lo decide, `c-133` en la tabla de objetivos; (iii) solo renumera "Reflexiones sobre la generalizacion" (9.5 -> 9.6) y no desplaza "Comparacion con la literatura" ni "Limitaciones", que editan `c-134`/`c-135`; (iv) el parrafo `:14` conserva la proyeccion bruta y remite a la subseccion.

**Alternativas consideradas:** (a) parrafos dentro de "Implicancias practicas": se descarta porque el calculo no seria referenciable como unidad; (b) subseccion inmediatamente despues de "Interpretacion de los resultados": renumera cuatro subsecciones y separa el balance del parrafo economico; (c) ubicarlo en resultados: se descarta porque el balance depende de supuestos no medidos y es interpretacion, no resultado.

### D2 - Modelo: balance por incidente escalado al universo y punto de equilibrio

Notacion (inline, como la formula de `04-marco-metodologico.tex:51`; sin ecuaciones desplegadas, que el documento no usa):

- `N = 2.646` incidentes por trimestre (canonico); `Delta t = 43,82 s` de ahorro medio por incidente (canonico; el texto muestra 43,8 s); `e_aut = 0,265` tasa de error estricta del clasificador (`53/200`); `e_man` tasa de derivacion erronea manual (supuesto; 15 % preliminar); `c` costo de una derivacion erronea en segundos (600-900 s = 10-15 min).
- Balance neto trimestral, en horas-persona: `B = (N / 3.600) x [Delta t - (e_aut - e_man) x c]`.
- Exactitud minima de equilibrio (`B = 0`): `a* = 1 - e_man - Delta t / c`; equivalente a una tasa de error automatizada maxima `e_aut* = e_man + Delta t / c` y a un exceso de error tolerable `Delta e* = Delta t / c` (14,6 / 7,3 / 4,9 puntos porcentuales para 5 / 10 / 15 min).
- Propiedad que se declara en el texto: `a*` no depende de `N`; el universo escala el balance pero no su signo, de modo que la conclusion es robusta al criterio de universo (dias habiles o calendario).
- Supuestos explicitos: cada derivacion erronea cuesta `c` en ambos flujos; el ahorro `Delta t` aplica a todo `N`; la tasa automatizada es la del corpus; el flujo automatizado no agrega tiempo de revision (el gate no derivo casos); relacion lineal.

Esqueleto de la subseccion (texto final con ortografia completa; presupuestos de prosa para D10):

- **P1 (<= 90 palabras):** la proyeccion de 32,2 h es un ahorro bruto; insumos con su procedencia (remisiones a `subsec:planteamiento-problema`, `subsec:objetivos-especificos`, `subsec:interpretacion-resultados`, `sec:resultados`); formulas de `B` y `a*`; independencia de `N`.
- **Tabla `tab:balance-neto`** (D3).
- **P2 (<= 120 palabras):** calculo central con los supuestos del documento (~304 derivaciones adicionales; 50,7-76,1 h; balance de -18,5 a -43,9 h; exceso tolerable de 7,3-4,9 puntos frente a 11,5 observados); lectura de la tabla (el signo depende de los supuestos); comparacion de `a*` con el IC de Wilson; relacion con el umbral del 85 % (coincide con la paridad respecto del 15 % manual; `a*`, que acredita el ahorro de registro, es menos exigente, de modo que el umbral opera como criterio conservador); frase laxa segun D4.
- **P3 (<= 110 palabras):** indeterminacion (D5), los tres planos de viabilidad y la condicion operativa (D6), y remision a `subsec:estudios-replicacion` (D8).

**Alternativas consideradas:** (a) balance monetario en pesos o dolares: se descarta porque exige un costo horario que el documento no tiene y que habria que inventar; (b) solo el calculo puntual del dictamen: oculta la dependencia de supuestos no medidos y no permite concluir la indeterminacion que A3 exige declarar; (c) modelo probabilistico (bootstrap o Monte Carlo sobre `e_man` y `c`): requeriria distribuciones a priori inventadas; (d) ecuaciones desplegadas: el documento no las usa y cuestan lineas (D10).

### D3 - Rejilla de escenarios y forma de la tabla

Rejilla: `e_man` en {10 %, 15 % (estimacion preliminar del documento), 20 %, 26,5 % (paridad con el error automatizado)}; `c` en {5 min (escenario optimista por debajo de la estimacion propia), 10 min, 15 min (rango del documento)}. 10 % y 20 % son +/-5 puntos alrededor del 15 %. Todos se rotulan como supuestos de sensibilidad, no como datos.

Forma: 4 filas x 2 grupos de 3 columnas (booktabs, `\small`, linea "Fuente: elaboracion propia" como `tab:cumplimiento-objetivos`): "Exactitud minima de equilibrio `a*` (%)" para `c` = 5/10/15 min y "Balance neto `B` con exactitud estricta (h-persona por trimestre)" para `c` = 5/10/15 min. Nota bajo la tabla: comparacion con la exactitud estricta 73,5 % (IC 95 % [67,0 %; 79,1 %]) y, si existe, con la laxa (D4); convencion numerica; signo explicito en los positivos; negativos con signo menos tipografico en modo matematico.

Valores (verificados con el comando de referencia de D9; `Delta t = 43,82 s`, `N = 2.646`, `e_aut = 53/200`, redondeo a una decimal mitad hacia arriba):

| `e_man` | `a*` 5 min | `a*` 10 min | `a*` 15 min | `B` 5 min | `B` 10 min | `B` 15 min |
|---|---|---|---|---|---|---|
| 10 % | 75,4 | 82,7 | 85,1 | -4,2 | -40,6 | -76,9 |
| 15 % | 70,4 | 77,7 | 80,1 | +6,9 | -18,5 | -43,9 |
| 20 % | 65,4 | 72,7 | 75,1 | +17,9 | +3,5 | -10,8 |
| 26,5 % | 58,9 | 66,2 | 68,6 | +32,2 | +32,2 | +32,2 |

Escenario central: derivaciones adicionales `(0,265 - 0,15) x 2.646 = 304,3 ~ 304`; costo 50,7 h (10 min) y 76,1 h (15 min); exceso observado 11,5 puntos. Lectura: con la exactitud estricta, `B > 0` solo cuando `e_man >= 20 %` con `c <= 10 min`, con `e_man = 15 %` y `c = 5 min`, o en paridad; es negativo en los escenarios centrales del documento. `a*(15 %, 10 min) = 77,7 %` cae dentro del IC de Wilson, de modo que ni con esos supuestos la muestra determina el signo; `a*(15 %, 15 min) = 80,1 %` supera el limite superior (79,1 %). Con `Delta t = 43,8 s` dos celdas difieren en 0,1 (`B(15 %, 5 min) = 6,8`; `B(10 %, 15 min) = -77,0`): la convencion se declara en la nota de la tabla y en el memo.

**Alternativas consideradas:** (a) tabla larga de 12 filas (`e_man x c`): duplica el espacio vertical; (b) tabla de 9 columnas con `B` laxo: ancho excesivo y dependencia dura de `c-131`; (c) dos tablas: mas espacio; (d) solo `B` sin `a*`: A3 pide el punto de equilibrio, y `a*` permite comparar cualquier exactitud (estricta, laxa o futura) sin recalcular; (e) horas enteras (robustas al redondeo de `Delta t`): se descarta por coherencia con la precision del 32,2 y de las cifras del dictamen; queda como alternativa si la revision de los autores prefiere evitar falsa precision.

### D4 - Exactitud laxa como escenario condicional (dependencia blanda de c-131)

Regla al aplicar: si `numeros-canonicos.md` ya contiene la exactitud laxa `a_laxa` registrada por `c-131` (con su IC), la nota de la tabla la incluye y P2 agrega una frase con los escenarios donde `a* <= a_laxa` y el balance laxo del escenario central (`e_aut = 1 - a_laxa`), registrado en el memo como `condicional`. Si no existe, la subseccion se publica con la exactitud estricta y una frase que declara que el 26,5 % es una cota superior de la tasa operativa de derivacion erronea atribuible al clasificador, porque el 53,5 % de los casos admite mas de un sector valido; la comparacion laxa la agrega `c-131` (o `c-141`) cuando el valor exista. En ningun caso `c-132` computa ni estima `a_laxa`.

**Alternativas consideradas:** computar la laxa aqui: duplica `c-131`, requiere la cache de predicciones ausente o nuevas llamadas a Gemini, y arriesga definiciones divergentes; hacer de `c-131` un prerrequisito duro: bloquearia A3 por una sensibilidad opcional.

### D5 - Balance declarado indeterminado, sin tasa manual inventada

El texto declara que el balance neto es indeterminado con el diseno actual por tres razones verificables: (i) la exactitud del brazo manual sobre el corpus no se midio: el corpus no registra la derivacion del operador por caso (`sec:anexo-corpus`) y los operadores son los mismos analistas que fijaron la referencia (`04-marco-metodologico.tex:55`), por lo que una medicion sobre este corpus estaria sesgada hacia el acuerdo; (ii) el 15 % es una estimacion preliminar del mismo origen que los 2 min 45 s (promedio semanal sin registro por caso) y nunca se re-midio, y esa misma fuente sobreestimo el tiempo manual (165 s frente a 61,6 s medidos); (iii) las definiciones no son homogeneas: el 15 % es operativo (reasignaciones), mientras que el 26,5 % es estricto contra la etiqueta principal en un corpus con 53,5 % de casos multietiqueta, de modo que es una cota superior de la tasa operativa. Consecuencia: la tesis no afirma el signo del balance como resultado; enuncia la condicion bajo la cual es positivo (`a >= a*`) y la medicion que lo cerraria (D8). Ubicacion: P3 de la subseccion (principal), la sexta limitacion (`:50`, <= 30 palabras) y el planteamiento del problema (`01-introduccion.tex:18`, <= 25 palabras).

**Reversibilidad:** si una replicacion mide `e_man` y `c`, el memo se actualiza (upsert), la tabla se recalcula y la conclusion puede firmarse en un sentido u otro.

**Alternativas consideradas:** declarar el balance negativo, como sugiere el calculo puntual: el propio evaluador no lo afirma y supondria tratar una estimacion preliminar como dato; declararlo positivo bajo la lectura laxa: tambien depende de `e_man`, no medida.

### D6 - Tres planos de viabilidad y objetivos de propagacion (ANTES/DESPUES)

Delimitacion que se enuncia una vez en P3 y se respeta en todo el documento: **tecnica** = el sistema se construyo, proceso los 200 casos y redujo el tiempo de registro en 71,2 % (medido); **economica** = el costo monetario de operacion (infraestructura de 24-32 USD/mes e inferencia del orden de 1 USD por trimestre) es marginal (`08-discusion.tex:58`); **operativa** = saldo neto de horas-persona del personal (ahorro de registro menos costo de las derivaciones erroneas), **condicionada** a que la exactitud efectiva supere `a*`, por mejora del clasificador o porque la revision humana del sector responsable reduzca la tasa o el costo efectivos de las derivaciones erroneas. Las 32,2 horas-persona se califican como ahorro bruto; el numero no cambia.

Objetivos de propagacion (las citas se transcriben sin tildes por convencion de los artefactos; en el `.tex` se escriben con ortografia completa; la localizacion se hace por texto, no por numero de linea; los DESPUES son borradores que el apply puede pulir dentro del presupuesto indicado):

| # | Archivo y ancla | ANTES | DESPUES (borrador) | Presupuesto |
|---|---|---|---|---|
| T1 | `00-resumen.tex`, parrafo "Los hallazgos" | "Los hallazgos confirman la viabilidad tecnica, economica y operativa de automatizar el registro de tickets en organizaciones medianas, y aportan una arquitectura reproducible y evidencia empirica sobre modelos de lenguaje grandes en espanol rioplatense." | "Los hallazgos confirman la viabilidad tecnica y economica; la operativa es condicional, porque el balance neto frente a las derivaciones erroneas resulta indeterminado. Se aporta una arquitectura reproducible y evidencia empirica en espanol rioplatense." | <= 34 palabras |
| T2 | `00-resumen.tex`, parrafo "The findings" | "The findings confirm the technical, economic, and operational feasibility of automating ticket registration in medium-sized organizations, and provide a reproducible architecture and empirical evidence on large language models in Rioplatense Spanish." | "The findings confirm technical and economic feasibility; operational feasibility is conditional, since the net balance against misrouted incidents remains undetermined. A reproducible architecture and empirical evidence in Rioplatense Spanish are provided." | <= 31 palabras |
| T3 | `01-introduccion.tex`, planteamiento ("cercana al 15") | (a) tras "...y sirvio para dimensionar el problema." no hay calificacion del 15 %; (b) "32,2 horas-persona por trimestre"; (c) "Este tiempo representa un costo de oportunidad significativo para la organizacion." | (a) agregar "La tasa de derivacion erronea del 15 % comparte esa naturaleza preliminar y no fue re-medida, por lo que el saldo neto del ahorro queda indeterminado (\autoref{subsec:balance-neto})."; (b) "32,2 horas-persona brutas por trimestre"; (c) retirar la frase (valoracion no medida que el saldo neto condiciona) | neto <= +15 palabras |
| T4 | `01-introduccion.tex`, justificacion ("libera capacidad operativa") | "...la automatizacion propuesta libera capacidad operativa del personal tecnico, reduce el tiempo de respuesta percibido por los usuarios y disminuye la variabilidad introducida por el criterio individual. La evidencia recogida en este trabajo permite cuantificar esa mejora en el contexto especifico de una organizacion mediana argentina, aportando un caso documentado que otras organizaciones pueden utilizar como referencia para estimar el retorno esperado de una inversion similar." | "...la automatizacion propuesta busca liberar capacidad operativa del personal tecnico, reducir el tiempo de registro y la variabilidad del criterio individual. La evidencia recogida en una organizacion mediana argentina cuantifica el ahorro bruto de registro y el punto de equilibrio frente al costo de las derivaciones erroneas (\autoref{subsec:balance-neto}), con el que otras organizaciones pueden estimar, con sus propias tasas, el retorno de una inversion similar." | <= 70 palabras (`wc -w` del parrafo en `v1.1.1`; el borrador tiene 69) |
| T5 | `08-discusion.tex`, `subsec:interpretacion-resultados` ("absorbe la carga rutinaria") | S1 "El sistema absorbe la carga rutinaria ... lo demandan."; S2 "Este equilibrio ... capacidad operativa significativa."; proyeccion "...liberaria aproximadamente 32,2 horas-persona por trimestre," con nota al pie; S4 "La magnitud de esta liberacion ... impacto organizacional medible." | retirar S1 y S2 (D7); "32,2 horas-persona brutas por trimestre ---unas cuatro jornadas laborales de un operador---," con la nota al pie intacta; reemplazar S4 por "Ese ahorro es bruto: no descuenta el costo de las derivaciones erroneas que el clasificador agrega respecto del flujo manual, cuyo balance se analiza en la \autoref{subsec:balance-neto}." | neto <= -20 palabras |
| T6 | `08-discusion.tex`, sexta limitacion ("acota la independencia del") | "...lo que acota la independencia del \emph{ground truth}." | "...lo que acota la independencia del \emph{ground truth} y, junto con la falta de registro por caso de la derivacion manual, impide medir sin sesgo la exactitud del brazo manual (\autoref{subsec:balance-neto})." | <= +30 palabras |
| T7 | `08-discusion.tex`, implicancias ("pueden obtener beneficios sustanciales") | "...pueden obtener beneficios sustanciales mediante la implementacion de soluciones hibridas similares a la propuesta." | "...pueden reducir sustancialmente el tiempo de registro mediante soluciones hibridas similares a la propuesta, con un saldo neto que depende de la exactitud efectiva (\autoref{subsec:balance-neto})." | <= +12 palabras |
| T8 | `08-discusion.tex`, parrafo economico ("un valor marginal frente a") | "...un valor marginal frente a las 32,2 horas-persona liberadas." | "...un valor marginal frente a las 32,2 horas-persona brutas liberadas." | +1 palabra |
| T9 | `08-discusion.tex`, adopcion ("mejoras organizacionales sostenibles") | "...los beneficios cuantificados ---reduccion del 71,2 % en el tiempo de registro y exactitud estricta del 73,5 %--- se traduzcan..." | "...los beneficios cuantificados ---reduccion del 71,2 % en el tiempo de registro--- se traduzcan..." (la exactitud del 73,5 % no es un beneficio: queda bajo el umbral y bajo el equilibrio central) | -6 palabras |
| T10 | `09-conclusiones.tex`, parrafo inicial ("viable, eficiente y") | "...resulto viable, eficiente y economicamente accesible para organizaciones medianas." | "...resulto tecnicamente viable, eficiente en el registro y economicamente accesible para organizaciones medianas, con viabilidad operativa condicionada al balance neto de la \autoref{subsec:balance-neto}." | <= +15 palabras |
| T11 | `09-conclusiones.tex`, evaluacion comparativa ("redirigiendo ese tiempo"); solo la clausula final, la del gate es de `c-130` | "...el sistema libera al personal tecnico de la carga rutinaria de registro, redirigiendo ese tiempo hacia la resolucion efectiva de los casos." | "...el sistema libera tiempo bruto de registro, cuyo saldo neto depende del costo de las derivaciones erroneas (\autoref{subsec:balance-neto})." | <= 0 palabras |
| T12 | `09-conclusiones.tex`, aportes ("una alternativa viable para la") | "...resulto una alternativa viable para la clasificacion de tickets..." | "...resulto una alternativa tecnicamente viable para la clasificacion de tickets..." | +1 palabra |
| T13 | `09-conclusiones.tex`, aportes ("dominado por el consumo de API") - colateral, ver Open Questions | "...su costo operativo esta dominado por el consumo de API de inferencia, cuyo orden de magnitud se cuantifica en la \autoref{sec:discusion}." | "...su costo monetario de operacion, dominado por la infraestructura autoalojada y no por la inferencia, se cuantifica en la \autoref{subsec:implicancias-practicas}." | <= +2 palabras |
| T14 | `10-recomendaciones.tex`, `subsec:estudios-replicacion` ("supere las 100 unidades") | (sin mencion de la exactitud manual) | agregar al final: "Toda replicacion deberia registrar ademas la derivacion manual por caso, con etiquetadores distintos de los operadores, y cronometrar las reasignaciones (\autoref{subsec:balance-neto})." | <= +25 palabras (el borrador tiene 21; el detalle queda en P3) |

**Reversibilidad:** si una replicacion mide un balance positivo, la viabilidad operativa puede enunciarse como sostenida para ese contexto (upsert del memo y propagacion inversa de T1, T2, T10).

**Alternativas consideradas:** retirar por completo la palabra "viabilidad" del resumen: pierde la respuesta al objetivo general, que es evaluar viabilidad (requisito vigente "Reformulacion del objetivo general como evaluacion de viabilidad y desempeno"); conservar "operativa" con un matiz en la discusion: el dictamen pide explicitamente ajustar resumen y abstract.

### D7 - Retiro, no matiz, de la frase sobre el juicio humano

Se retiran S1 ("El sistema absorbe la carga rutinaria sin sustituir el juicio humano en los casos que verdaderamente lo demandan.") y S2 ("Este equilibrio entre automatizacion y supervision preserva la calidad del servicio y libera capacidad operativa significativa.") de `08-discusion.tex:14`. Razones: el gate no derivo ninguno de los 200 casos y su aporte se declara no medido (`09-conclusiones.tex:41`); 124 casos con confianza inferior a 0,70 no se escalaron (A1, `c-130`); "preserva la calidad del servicio" no se sostiene con 26,5 % de error estricto frente al 15 % preliminar; y el requisito vigente "Afirmaciones respaldadas por la evidencia" exige retirar juicios no respaldados. El comportamiento real del gate ya se trata en `:16`, que reescribe `c-130`.

**Reversibilidad:** si `c-130` (u otro change) implementa y mide un gate que derive casos con cobertura cuantificada, una afirmacion respaldada sobre el juicio humano puede reintroducirse con esa evidencia.

**Alternativas consideradas:** matizar ("sin que el gate haya derivado casos..."): duplicaria `:16` y arriesgaria redacciones contradictorias entre `c-130` y `c-132`; moverla a limitaciones: no es una limitacion sino una afirmacion sin respaldo.

### D8 - Linea futura en "Estudios de replicacion"

Una frase (T14, <= 25 palabras) al final de `subsec:estudios-replicacion`, subseccion que no pertenece al alcance de `c-136`; P3 remite a ella. Contenido: registro por caso de la derivacion del brazo manual, etiquetadores distintos de los operadores y cronometraje de cada reasignacion (mide `e_man` y `c`). `c-136` no debe duplicarla.

**Alternativas consideradas:** subseccion nueva "Medicion de la exactitud del flujo manual": cuesta paginas e interfiere con la lista de prioridades de `c-136`; dejarla solo en la discusion: A3 y la familia piden conectarla con las lineas futuras.

### D9 - Registro canonico y trazabilidad

Seccion nueva en `docs/Tesis/Correcciones/numeros-canonicos.md`, "3.N Balance neto de derivaciones erroneas (c-132)", con `N` = siguiente numero libre al aplicar (`c-131` puede haber agregado 3.7), redactada con la ortografia del memo (con tildes) y con una linea de upsert en la cabecera ("Upsert c-132: ... No modifica ningun valor canonico existente"). Contenido:

- Insumos (valor | procedencia `archivo:linea` | estado): `N ~ 2.646` (ref. 3.4) vigente; `Delta t = 43,82 s` (ref. 3.1) vigente; `e_aut = 0,265 = 53/200` (`07-resultados.tex:75`; `report.md:18-19`) vigente, derivado; `e_man ~ 15 %` (`01-introduccion.tex:18`) condicional, estimacion preliminar no medida; `c = 10-15 min` (`01-introduccion.tex:48`) condicional, estimacion propia sin registro; rejilla 10 %, 20 %, 26,5 % y 5 min: supuestos de sensibilidad de c-132, condicional; `a_laxa`: referencia a la seccion de `c-131` si existe.
- Formulas de `B`, `a*`, `e_aut*` y `Delta e*`; tabla de D3; escenario central (304,3; 50,7 h; 76,1 h; -18,5 h; -43,9 h; 11,5 puntos; `Delta e*` 14,6 / 7,3 / 4,9).
- Comando de referencia (solo lectura, sin invocar el clasificador):

```bash
python3 -c "
from decimal import Decimal as D, ROUND_HALF_UP
r=lambda x: D(x).quantize(D('0.1'), ROUND_HALF_UP)
dt, N, ea = D('43.82'), D('2646'), D(53)/D(200)
S = dt*N/3600
for em in ('0.10','0.15','0.20','0.265'):
    em = D(em)
    print(em, [r((1-em-dt/(60*c))*100) for c in (5,10,15)], [r(S-(ea-em)*N*c/60) for c in (5,10,15)])
"
```

- Nota de redondeo (con 43,8 s difieren dos celdas en 0,1) y reversibilidad (upsert si una replicacion mide `e_man` o `c`).
- Todos los valores derivados de supuestos llevan estado `condicional`.

Ademas, una entrada "A3 - Balance neto de derivaciones erroneas - APLICADO por c-132 (fecha)" en `docs/Tesis/Correcciones/dictamen-correcciones.md`, dentro de un grupo del dictamen v10/v1.1.0 (2026-10-22); si otro change de la familia ya creo el grupo, se agrega la entrada; si no, se crea el grupo. La entrada mapea la observacion a los archivos editados (T1-T14 y la subseccion).

**Alternativas consideradas:** registrar los valores solo en el `.tex`: viola la regla de Gate 0 (todo numero citable en el memo); registrarlos como `vigente`: dependen de supuestos no medidos.

### D10 - Presupuesto de paginas

Medicion de partida: 101 paginas; finales de capitulo casi llenos (cap. 1 en p. 17, cap. 9 en p. 80, cap. 10 en p. 83, cap. 11 en p. 87). Estimacion por capitulo (interlineado doble, ~400-440 palabras por pagina; la tabla, flotante a espacio simple, ocupa ~0,2 pagina):

- Cap. 1 (p. 17, ~2 lineas libres): T3 + T4, neto <= +15 palabras -> probablemente 0 paginas.
- Cap. 9 (p. 80, ~2 lineas libres): subseccion (encabezado, tabla y prosa) + T5-T9 (~+17 palabras netas) -> +1 pagina si la prosa nueva no supera ~280 palabras; +2 si llega al maximo de 320 de D2.
- Cap. 10 (p. 83, sin lineas libres): T10-T13, neto ~+11 palabras -> 0 o +1 pagina.
- Cap. 11 (p. 87, ~1-2 lineas libres): T14, ~+21 palabras -> 0 o +1 pagina.

Impacto: +1 a +3 paginas (central +2) si no se compensa, porque cada capitulo empieza en pagina nueva.

Politica local: (1) presupuestos por objetivo (D6) y por parrafo (D2); (2) medir antes y despues el total y la pagina de inicio de cada capitulo (`main.toc` o `pdftotext`); (3) si el delta neto supera +1, aplicar palancas admisibles de c-116 en los mismos capitulos (pasajes duplicados, leyendas sobre-extendidas): acortar T14 al minimo y dejar el detalle en P3, condensar la nota de la tabla, condensar `08-discusion.tex:60`; (4) no retirar contenido cientifico; (5) informar el delta a `c-141`, que decide el tope global de `v1.2.0`.

**Alternativas consideradas:** tope duro de 101 para `c-132` aislado: obligaria a recortar contenido cientifico u omitir partes exigidas por A3, mientras el resto de la familia agrega contenido; mover la tabla a un anexo: separa el calculo de su lectura en la discusion (queda como ultimo recurso para `c-141`).

### D11 - Coordinacion con la familia y orden sugerido

Fronteras por archivo y parrafo:

- `00-resumen.tex`: `c-132` es dueno de los parrafos "Los hallazgos" / "The findings"; `c-133` de los parrafos de resultados (metrica primaria). Restriccion compartida: requisito de <= 250 palabras; delta de `c-132` <= 0.
- `01-introduccion.tex`: `c-132` edita el planteamiento (15 % y 32,2 brutas) y la justificacion organizacional; `c-133` es dueno de hipotesis, objetivos y la justificacion del umbral del 85 % (`:48`), a quien se informa la relacion umbral-equilibrio de P2.
- `08-discusion.tex`: `c-132` edita `:14` (S1, S2, S4 y "brutas"), la sexta limitacion, `:54`, `:58`, `:60` y crea `subsec:balance-neto`; `c-130` es dueno de `:16`; `c-133` de la afirmacion sobre la eficiencia del esquema hibrido (`:10`); `c-134` del desagregado por canal (`:20`); `c-135` de la cuarta limitacion (`:46`).
- `09-conclusiones.tex`: `c-132` edita la clausula de viabilidad de `:6`, la clausula final de `:41`, `:47` y `:49`; `c-133` es dueno de la tabla de objetivos y de la frase del objetivo 2 en `:6`, y puede citar `subsec:balance-neto` como evidencia; `c-130` de la clausula del gate en `:41`; `c-134`/`c-135` de la salvedad del canal telefonico en `:39`.
- `10-recomendaciones.tex`: `c-132` agrega solo el final de `:30`; `c-136` es dueno del parrafo introductorio y de las subsecciones nuevas.
- `numeros-canonicos.md`: cada change agrega su propia seccion con el siguiente numero libre.

Regla operativa: localizar cada ancla por texto (`grep`) y releer el parrafo antes de editar, porque otros changes pueden haber desplazado lineas.

Orden sugerido: `c-130` -> `c-131` -> `c-132` -> `c-133` -> `c-136` -> (`c-134`, `c-135`, `c-138`, `c-139`, `c-140`) -> `c-137` -> `c-141`. `c-131` antes para disponer de la laxa (D4); `c-133` despues para poder citar el balance en la tabla de objetivos; `c-136` despues para no duplicar T14; `c-137` barre la ortografia al final; `c-141` integra, verifica paginas y publica. Si `c-131` se demora, `c-132` aplica con el fallback de D4.

## Risks / Trade-offs

- **[El delta de paginas supera +1]** -> Mitigacion: presupuestos de D2/D6, medicion por capitulo y palancas admisibles (D10); la decision global queda en `c-141` (Open Questions).
- **[La exactitud laxa no esta disponible porque la cache de predicciones no esta en el arbol]** -> Mitigacion: fallback de D4; la tabla con `a*` permite agregar la comparacion despues sin recalcular.
- **[El lector interpreta la tabla como "el sistema tiene balance negativo"]** -> Mitigacion: P3 declara la indeterminacion; `e_man` y `c` se rotulan como supuestos no medidos; la rejilla muestra que el signo cambia con los supuestos.
- **[Falsa precision (una decimal) sobre supuestos gruesos]** -> Mitigacion: convencion declarada; las cifras ilustran sensibilidad, no estimaciones; alternativa de horas enteras disponible (D3).
- **[Divergencia de redondeo entre 43,8 s y 43,82 s]** -> Mitigacion: la nota de la tabla y el memo declaran `Delta t = 43,82 s`; dos celdas difieren en 0,1.
- **[Ediciones concurrentes de `c-130`/`c-133` en los mismos parrafos]** -> Mitigacion: fronteras de D11, anclas por texto y relectura previa.
- **[El resumen ya supera 250 palabras con la regla literal de c-106 (~264-266 ES; ~254 EN)]** -> Mitigacion: `c-132` es neutro (T1, T2); se informa a `c-133`/`c-141` para el ajuste global.
- **[Tension con la justificacion del umbral del 85 % (`01-introduccion.tex:48`)]** -> Mitigacion: P2 explica que el umbral coincide con la paridad y que `a*` es menos exigente; `c-133` queda informado.
- **[Ortografia del texto nuevo y anclas que `c-137` va a cambiar (p. ej. "erronea")]** -> Mitigacion: el texto nuevo se escribe con tildes; las anclas de `tasks.md` evitan palabras que `c-137` corrige.
- **[Finales de linea CRLF]** -> Mitigacion: preservar CRLF en el arbol de trabajo y revisar `git diff --stat` sin cambios espurios de fin de linea.
- **[Renumeracion de "Reflexiones sobre la generalizacion" (9.5 -> 9.6)]** -> Mitigacion: las remisiones usan etiquetas; las menciones numericas en registros historicos no se reescriben.

## Migration Plan

1. Linea de base: compilar el PDF vigente; registrar paginas (101) y pagina de inicio de cada capitulo; verificar si el memo ya contiene la exactitud laxa (`c-131`) y si `c-130`/`c-133` ya se aplicaron (releer las anclas).
2. Memo primero (Gate 0): agregar la seccion de D9 con los valores del comando de referencia.
3. Discusion: crear `subsec:balance-neto` y `tab:balance-neto`; aplicar T5-T9.
4. Propagacion: T1-T4 y T10-T14.
5. Compilar con XeLaTeX (`latexmk`, o el contenedor `texlive-thesis` de `paper/Dockerfile`); verificar referencias, etiquetas y delta de paginas; aplicar palancas de D10 si hace falta.
6. Verificar con `grep` la ausencia de las frases retiradas, la presencia de las nuevas y la identidad texto-memo; registrar la entrada A3 en `dictamen-correcciones.md`.
7. Rollback: `git checkout <commit-previo> -- <archivo>` sobre los cinco `.tex` y los dos `.md`, y recompilar. No hay tags que revertir.

## Open Questions

1. **Tope de paginas de `v1.2.0`:** se mantiene el tope de 101 paginas de c-116/c-121, o `c-141` fija un presupuesto para la familia? Solo `c-132` agrega entre +1 y +3 paginas. Recomendacion: presupuesto de familia decidido en `c-141`; `c-132` apunta a <= +1.
2. **Correccion colateral T13:** se incluye en `c-132` la correccion de "su costo operativo esta dominado por el consumo de API de inferencia" (`09-conclusiones.tex:49`), que contradice la discusion? Recomendacion: si, porque este change delimita la viabilidad economica; alternativa: derivarla a `c-135`.
3. **Orden respecto de `c-131`:** se acepta aplicar `c-132` con el fallback de D4 si `c-131` no esta aplicado, o se prefiere esperar la exactitud laxa? Recomendacion: no esperar; la tabla con `a*` admite la comparacion laxa posterior.
