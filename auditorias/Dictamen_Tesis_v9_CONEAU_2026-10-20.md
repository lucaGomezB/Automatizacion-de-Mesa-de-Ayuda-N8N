# DICTAMEN DE EVALUACIÓN ACADÉMICA

**Documento evaluado:** *Automatización inteligente del registro de incidentes en mesas de ayuda empresariales mediante orquestación de flujos con N8N y procesamiento de lenguaje natural basado en modelos de lenguaje grandes*. Trabajo Final de Carrera, Tecnicatura Universitaria en Programación, UTN Facultad Regional Mendoza. Versión v9, `docs/Tesis/v9 (IA)/paper/main.pdf`, 103 páginas, compilada el 20 de octubre de 2026. Autores: Gomez, Bustos y Sevilla. Director: Prof. Alberto Cortez.

**Alcance del examen:** se analizó el cuerpo completo (capítulos 1 a 11, referencias y anexos), el archivo de bibliografía y los artefactos de compilación. Se verificó la correspondencia entre citas y referencias, la resolución de los identificadores DOI, la existencia de las figuras y la coherencia numérica interna. No se re-ejecutó el sistema ni se auditó la base de datos primaria: las observaciones sobre resultados se sustentan en la consistencia interna del documento, no en una replicación experimental. La verificación bibliográfica acreditó existencia y resolución de las obras, pero no la exactitud individual de cada metadato contra el registro del editor.

**Nivel de exigencia aplicado:** criterios de evaluación universitaria argentina (CONEAU) calibrados al nivel de una tecnicatura, no de una licenciatura o posgrado. Se valoró la pertinencia del trabajo final como cierre de una formación técnica superior, sin trasladar exigencias de investigación original propias de otros niveles.

---

## VEREDICTO GENERAL

**APROBADO CON OBSERVACIONES DE CARÁCTER MAYOR.**

El trabajo acredita un esfuerzo metodológico muy superior al promedio de un trabajo final de tecnicatura: pregunta de investigación explícita, hipótesis falsable, diseño cuasiexperimental con muestras pareadas, prueba no paramétrica con tamaño del efecto, análisis de sensibilidad, discusión con explicaciones rivales y una bibliografía actual, pertinente y verificable. El sistema existe, fue desplegado y evaluado sobre un corpus documentado de 200 casos. Esa combinación no es habitual y debe reconocerse.

Sin embargo, el dictamen positivo queda condicionado a la resolución de una inconsistencia interna que afecta el resultado operativo central del capítulo 7 y a un conjunto de defectos formales y de trazabilidad que un jurado adversarial detectará de inmediato. La tesis declara con honestidad que no alcanzó el umbral de clasificación del 85 %, lo cual es un gesto académico valioso; pero al mismo tiempo reporta una proporción de intervención humana del 9,5 % que no se reconcilia con su propia tabla de calibración. Ese punto debe esclarecerse antes de la defensa. Si la inconsistencia no se resuelve con los datos primarios, la afirmación del 9,5 % debe retirarse y el trabajo revaluarse.

---

## OBSERVACIONES POR DIMENSIÓN

### 1. Estructura general del documento

**Cumple parcialmente.**

La arquitectura de capítulos es la esperable y está completa: introducción con problema, pregunta, hipótesis y objetivos; marco teórico; estado del arte; marco metodológico con operacionalización de variables y amenazas a la validez; arquitectura; implementación; resultados; discusión; conclusiones; recomendaciones; aspectos legales; referencias y anexos. La progresión es lógica y cada capítulo prepara el siguiente.

Los defectos son de disciplina formal, no de organización. El documento se compila con `\documentclass{article}`, de modo que los encabezados se renderizan como "1", "1.1", mientras la prosa denomina sistemáticamente "Capítulo 2", "Capítulo 7". Las remisiones cruzadas están escritas a mano en lugar de resolverse con `\ref`: existen apenas ocho etiquetas en todo el cuerpo. Eso ya produjo un error concreto, la remisión del capítulo 7 a la "Sección 4.4" para la cota de 45 segundos, cuando esa cota se enuncia en 4.6. El capítulo 11, dedicado a consideraciones éticas y legales, está ubicado después de conclusiones y recomendaciones, lo que lo convierte en un apéndice encubierto y lo desconecta del flujo argumental. El resumen en español tiene 538 palabras frente a un límite de 250 que el propio archivo declara; el abstract tiene 292. La asimetría y el exceso son objetivos.

Se observa además una acentuación irregular: conviven títulos correctamente acentuados con centenares de ocurrencias sin tilde en el cuerpo ("realizandose", "informaticos", "clasificacion", "Capitulo"), lo que sugiere pasajes redactados en ASCII y no normalizados. Hay errores puntuales de redacción, como "trazabilidad auditiva" en lugar de "auditable".

**Recomendación:** migrar todas las remisiones a `\ref`/`\autoref`; corregir la remisión 4.4 por 4.6; reducir el resumen a 250 palabras; normalizar la acentuación en todo el manuscrito; unificar la clase de documento o reemplazar "Capítulo" por "Sección" en la prosa; reubicar el capítulo legal antes de resultados o integrarlo a la metodología.

### 2. Hipótesis

**Cumple, con reservas en su formulación.**

La hipótesis es explícita, cuantificada y falsable. Se enuncia en la introducción y se formaliza con hipótesis nula y alternativa sobre las medianas del tiempo de registro. Es un estándar poco frecuente en trabajos de este nivel y debe destacarse.

El problema es de diseño lógico: la hipótesis principal combina una afirmación de mecanismo ("permite reducir significativamente el tiempo y la intervención humana") con un umbral de desempeño ("alcanzando una exactitud no inferior al 85 % y un F1 macro no inferior a 0,85"). Al obtener 73,5 % de exactitud y 0,5207 de F1 macro, la hipótesis entendida como conjunción es falsa. La tesis lo reconoce en las conclusiones, pero no rotula el estado global de la hipótesis como parcialmente refutada, y el resumen no informa que el umbral predefinido no se alcanzó. Un lector del resumen podría inferir éxito pleno. Además, solo la parte temporal tiene hipótesis nula operacionalizada; la parte de clasificación no.

**Recomendación:** desdoblar la hipótesis en tres sub-hipótesis (tiempo, intervención humana, exactitud/F1), cada una con su contraste y su criterio de falsación; declarar en el resumen y en las conclusiones que la hipótesis principal se confirma en tiempo e intervención y se refuta en clasificación.

### 3. Objetivos

**Cumple parcialmente.**

Hay un objetivo general y cinco específicos, mutuamente consistentes y alineados con la pregunta. El objetivo cuarto es propiamente investigativo y medible. La justificación del umbral del 85 % con tres criterios convergentes es un acierto.

Pero el objetivo general está formulado en clave de desarrollo ("desarrollar e implementar"), no de investigación. El objetivo específico segundo incorpora una meta de desempeño como si fuera un objetivo, cuando en realidad es un criterio de éxito contingente; precisamente por eso hoy figura como no alcanzado. El objetivo quinto ("documentar exhaustivamente") no es verificable, porque "exhaustivamente" no admite contraste. Y no existe un objetivo específico que corresponda al análisis de errores ni a la calibración de la confianza, que son aportes centrales del capítulo 7.

**Recomendación:** reformular el objetivo general en términos de evaluar viabilidad y desempeño, dejando el desarrollo como medio; separar en el objetivo segundo la acción de implementar del umbral de desempeño; reescribir el quinto en clave reproducible; agregar un objetivo sobre análisis de errores y calibración; incluir una tabla de objetivos, cumplimiento y evidencia en las conclusiones.

### 4. Estado del arte

**Cumple parcialmente.**

La literatura es actual, pertinente y real. Se verificaron los identificadores DOI y las obras resuelven a publicaciones existentes, incluidas las de 2025 y 2026 que podían generar dudas. El capítulo discute los trabajos y no se limita a listarlos: el contraste con Paramesh y Revina es sustantivo, e incluso se usa a Revina para tensionar la propia elección metodológica. La brecha está formulada y conectada con la contribución.

Los déficits son tres. Primero, no se describe el protocolo de revisión: no se indican bases consultadas, cadenas de búsqueda, criterios de inclusión ni período. Sin ese protocolo, la afirmación de que "no existe artículo arbitrado 2023-2026 que evalúe Gemini sobre tickets en español" es una declaración de vacancia no verificable, y se usa dos veces como motivación. Segundo, varios trabajos se agrupan en una sola oración con una afirmación genérica, sin reportar corpus, métricas ni condiciones, lo que impide juzgar su comparabilidad. Tercero, el subapartado de soluciones comerciales se apoya en páginas de producto y no en literatura; afirmaciones como el dominio del segmento o el crecimiento sostenido de la adopción quedan sin respaldo formal.

**Recomendación:** agregar un párrafo de metodología de revisión y acotar la afirmación de vacancia a lo efectivamente buscado; convertir los agrupamientos en una tabla comparativa de trabajos académicos; citar informes de mercado o reformular como observación propia documentada las afirmaciones sobre plataformas comerciales.

### 5. Marco teórico

**Cumple parcialmente.**

El marco teórico no es decorativo: cada eje desemboca en una decisión de diseño verificable en los capítulos 5 y 6. La inclusión de calibración, alucinación y métricas multiclase, con fórmulas operativas, excede el estándar habitual.

El hueco conceptual más serio es que "human in the loop" estructura el resumen, las palabras clave y el aporte, pero nunca se define ni se fundamenta en el marco teórico; su única mención conceptual aparece tardíamente en el capítulo legal. Lo mismo ocurre con "automatización de procesos empresariales" y "plataformas de integración como servicio", definidas sin fuente. La atribución de "soberanía digital" a la Ley 25.326 es jurídicamente imprecisa: una ley de protección de datos no enuncia ese principio. La definición de alucinación carece de cita canónica. El eje de reconocimiento automático del habla se desarrolla y luego se admite que no se usa en la implementación, lo que lo vuelve casi prescindible.

**Recomendación:** incorporar una subsección sobre human-in-the-loop con definición, grados de autonomía y fuentes; citar o reformular como glosa propia los conceptos definidos por aserción; sustituir "soberanía digital" por la formulación jurídica exacta; recortar el eje de ASR o justificar su inclusión.

### 6. Desarrollo metodológico y propuesta

**Cumple parcialmente.**

El diseño es sólido y está documentado con un detalle poco habitual: muestreo, potencia a priori, doble etiquetado con kappa, Shapiro-Wilk para justificar la prueba no paramétrica, tamaño del efecto rank-biserial, intervalos de Wilson, análisis de sensibilidad y amenazas a la validez tratadas una por una, incluida la admisión de que una mitigación no funciona. La arquitectura está justificada por comparación con alternativas y el flujo es replicable en principio.

Hay cuatro debilidades metodológicas que deben señalarse. La primera es que el margen de error del 6,74 % se eligió para reproducir exactamente el corpus de 200 casos, en reemplazo de un 6,5 % que habría arrojado 214. Eso invierte la lógica del muestreo: el margen debe fijarse a priori, no calibrarse sobre el tamaño ya obtenido. La segunda es que el universo de 3.700 incidentes se calcula multiplicando 42 incidentes diarios por 88 días de calendario, cuando la tasa diaria proviene de una semana laboral; si se aplicara a días hábiles, el universo rondaría los 2.650 casos y la proyección de 45 horas-persona caería a aproximadamente 32 horas. La tercera es que los dos etiquetadores de la verdad de referencia son las mismas personas que operaron el brazo manual; la tesis lo declara, pero eso acota la independencia del patrón de comparación y no queda suficientemente reflejado en las conclusiones. La cuarta es que la clase "Bases de Datos" tiene un solo caso: el F1 macro incluye un cero estructural y el umbral de 0,85 sobre esa métrica pierde sentido práctico. La tesis lo advierte en la discusión, pero el objetivo se formuló sin esa salvedad.

A esto se suma un problema de trazabilidad: el anexo declara que la creación del tag de la versión evaluada "queda como acción pendiente", de modo que la reproducibilidad es declarativa hasta que se consigne el hash del commit.

**Recomendación:** justificar el margen a priori o declarar que el tamaño se fijó por disponibilidad operativa; recalcular el universo y la proyección horaria sobre días hábiles o justificar explícitamente el criterio calendario; reportar intervalo de confianza del kappa y métricas por clase con su incertidumbre; tratar la clase con n=1 como no estimable en el cómputo macro o excluirla con justificación; cerrar el tag y consignar el hash.

### 7. Resultados y coherencia con las conclusiones

**No cumple en su estado actual, por una inconsistencia crítica.**

Los resultados se presentan con tablas, figuras existentes y métricas definidas. Los cálculos principales son reproducibles: la reducción del 71,2 %, el estadístico de Wilcoxon con sus sumas de rangos, el efecto rank-biserial, el intervalo de Wilson y el promedio macro de F1 se rehacen sin error a partir de los datos reportados. El análisis de sensibilidad que descuenta 5 y 10 segundos al flujo manual es ejemplar y reconocer que la reducción debe leerse como cota superior es un gesto de rigor.

Sin embargo, el subsistema de confianza e intervención humana no cierra. La Tabla 7.5 reporta 98 casos en la banda [0,00; 0,50) y 26 en [0,50; 0,70), es decir, 124 casos con confianza inferior a 0,70. El texto afirma que el operador intervino cuando la confianza fue inferior al 70 % y que solo 19 casos (9,5 %) requirieron intervención. Ambos enunciados no pueden ser verdaderos simultáneamente. A ello se agrega que se declaran 131 casos resueltos por la vía determinística y 69 por Gemini, mientras la misma tabla solo registra 46 casos con confianza igual o superior a 0,90, lo que obliga a explicar qué confianza asigna la etapa determinística y por qué no dispara revisión. El "46 casos con confianza ≥ 0,90 y 13 errores" tampoco se deduce de la tabla tal como está publicada.

Hay además una mezcla de paradigmas métricos. El micro-F1 reportado (0,6654) no es compatible con una tarea monoetiqueta, donde coincidiría con la exactitud (0,735). La presencia simultánea de subset accuracy y Hamming loss sugiere una verdad de referencia multietiqueta que el clasificador no produce, y esos indicadores penalizan estructuralmente una salida que el prompt fuerza a ser única. Sin definición explícita de la tarea, el lector no puede interpretar el conjunto.

Estas inconsistencias no prueban fabricación; son compatibles con un error de reporte o con una definición del gate distinta de la declarada. Pero mientras no se reconcilien, el resultado operativo más citado del trabajo —9,5 % de intervención humana— no está sustentado por la evidencia publicada.

Las conclusiones, por su parte, responden correctamente a los objetivos y asumen el fracaso del segundo. Contienen dos defectos: la frase "la reducción de la intervención humana alcanzó el 9,5 %" confunde el residual con la reducción, que es 90,5 %; y calificar el diseño como "riguroso" sin matizar la dependencia entre etiquetadores y operadores constituye un sobreclaim frente a lo admitido en el capítulo 4.

**Recomendación:** reconstruir la Tabla 7.5 junto con la lógica exacta del gate y el conteo de intervenciones, y publicar la tabla de contingencia que las vincula; definir si la tarea es mono o multietiqueta y unificar las métricas en consecuencia; corregir la frase del 9,5 %; rotular el estado de la hipótesis principal. Mientras eso no ocurra, el capítulo 7 no cumple el estándar de verificabilidad interna exigible.

### 8. Propuestas de trabajos futuros

**Cumple.**

Las líneas futuras están ancladas en las limitaciones y en el análisis de errores, no en fórmulas de manual. El agente conversacional telefónico es el mejor ejemplo: justifica técnicamente por qué no se implementó —WebSocket, transcodificación mu-law a PCM, detección de actividad de voz, cambio del modelo de costos— y propone conservar el modo degradado como respaldo. El clasificador supervisado con corpus propio y el aprendizaje activo responden directamente al problema de calibración detectado.

Dos observaciones menores: el umbral de "5.000 casos" para migrar a un clasificador propio se repite cuatro veces sin justificación empírica ni cálculo de potencia, y algunas líneas —Slack, Teams, aplicaciones móviles, base de conocimientos— son genéricas y no se derivan de los resultados. La tesis reconoce que su cuantificación excede el alcance, lo que atenúa el problema.

**Recomendación:** justificar el umbral de 5.000 casos o degradarlo a valor indicativo; priorizar explícitamente las líneas que atacan los defectos medidos: calibración del gate, clasificador supervisado y corrección de la medición de intervención.

### 9. Bibliografía

**Cumple.**

La auditoría arroja correspondencia perfecta: 48 entradas en el archivo, 48 claves renderizadas y 48 claves citadas. No hay huérfanas, no hay entradas sin usar, no hay duplicados ni referencias sin resolver. Los 22 identificadores DOI resuelven a publicaciones reales; las URLs verificadas responden. La distribución temporal es adecuada: 26 entradas de 2020 o posterior y 21 de 2023-2026, con clásicos metodológicos correctamente empleados (Wilson, Cohen, Landis y Koch). El estilo es autor-año consistente y las citas de los capítulos teóricos son sustantivas, no decorativas.

Los defectos son menores pero corregibles. `Touvron2023` está tipada como artículo de revista y se renderiza con "arXiv preprint" como si fuera una publicación periódica; `Jurafsky2023` es un borrador no publicado presentado como libro de Stanford University Press. Las descripciones de plataformas comerciales carecen de entrada bibliográfica formal.

**Recomendación:** corregir el tipado de las dos entradas; incorporar referencias formales o reemplazar por observación propia las afirmaciones sobre productos comerciales.

---

## SÍNTESIS DE VEREDICTOS

| Dimensión | Veredicto |
|---|---|
| 1. Estructura general | Cumple parcialmente |
| 2. Hipótesis | Cumple, con reservas de formulación |
| 3. Objetivos | Cumple parcialmente |
| 4. Estado del arte | Cumple parcialmente |
| 5. Marco teórico | Cumple parcialmente |
| 6. Metodología y propuesta | Cumple parcialmente |
| 7. Resultados y conclusiones | No cumple en su estado actual |
| 8. Trabajos futuros | Cumple |
| 9. Bibliografía | Cumple |

---

## RECOMENDACIONES PRIORIZADAS

**Obligatorias antes de la defensa**

1. Reconciliar la Tabla 7.5 con el 9,5 % de intervención y con la distribución 131/69. Publicar la tabla de contingencia confianza-intervención y la regla exacta del gate. Si no se resuelve, retirar la cifra del 9,5 % y reformular el aporte operativo.
2. Declarar el estado de la hipótesis principal como parcialmente confirmada y parcialmente refutada, en el resumen, las conclusiones y la discusión.
3. Corregir "la reducción de la intervención humana alcanzó el 9,5 %" por "la proporción de intervención humana se redujo al 9,5 %".
4. Recalcular el universo de 3.700 incidentes y la proyección de 45 horas-persona, o justificar explícitamente el uso de días calendario.
5. Definir la tarea como mono o multietiqueta y unificar micro-F1, exactitud, subset accuracy y Hamming loss en un mismo marco.
6. Corregir las discrepancias de conteo: seis frente a siete entidades, cinco frente a siete etapas del flujo, 26 operativos más 3 notas frente a 29 operativos, y `google-genai` frente a `google-generativeai`.
7. Corregir la remisión del capítulo 7 a la Sección 4.4, que debe ser 4.6.
8. Reducir el resumen a 250 palabras y normalizar la acentuación del manuscrito.

**Recomendadas**

9. Justificar a priori el margen del 6,74 % o declarar que el tamaño muestral se fijó por disponibilidad operativa.
10. Reportar intervalo de confianza del kappa y de las métricas por clase; tratar la clase con n=1 como no estimable.
11. Añadir el protocolo de revisión de literatura y acotar la afirmación de vacancia.
12. Incorporar una subsección teórica sobre human-in-the-loop con fuentes.
13. Cerrar el tag de la versión evaluada y consignar el hash del commit.
14. Corregir el tipado de las entradas `Touvron2023` y `Jurafsky2023`.
15. Reubicar el capítulo de aspectos legales y agregar un glosario de siglas.

---

## CONSIDERACIÓN FINAL

Estamos ante un trabajo que demuestra competencia técnica real y una madurez metodológica infrecuente para su nivel. La decisión de declarar el incumplimiento del umbral del 85 % en lugar de maquillarlo es, en sí misma, un indicador de integridad académica y debe valorarse. El dictamen positivo, no obstante, queda condicionado a que la tesis demuestre que sus propias cifras cierran. Un trabajo que exige rigor estadístico a su clasificador no puede permitirse que su tabla de calibración contradiga su tasa de intervención. Resolver esa contradicción no debilita el aporte: lo vuelve defendible.
