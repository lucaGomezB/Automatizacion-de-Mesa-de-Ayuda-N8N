# Dictamen de evaluación — Tesis de grado (criterios CONEAU)

**Documento:** «Automatización de Mesa de Ayuda con N8N» (Gomez, Bustos, Sevilla), UTN, Facultad Regional Mendoza.
**Versión examinada:** v10, rama `main`, commit `5734ea8` (13-11-2026, 20:02). Es posterior al tag `v1.3.0` y no tiene tag propio. Fuente LaTeX en `docs/Tesis/v10 (IA)/paper/sections/`, bibliografía en `Bibliography_base.bib` y PDF versionado de 147 páginas.
**Fecha:** 13 de noviembre de 2026.
**Antecedente inmediato:** dictamen sobre `v1.3.0` (commit `6615376`, misma fecha), al que responden los cambios c-205 a c-214.

**Alcance y límites de esta evaluación.** Se leyó completo el texto fuente de las secciones de resumen, introducción, marco teórico, estado del arte, metodología, resultados, discusión, conclusiones y recomendaciones, y los anexos de repositorio, corpus y trazabilidad. Las cifras incorporadas después del dictamen anterior se recalcularon desde los datos versionados. Los 44 DOI de la bibliografía se consultaron en Crossref y los dos identificadores de arXiv, en su API. No se evaluó la legibilidad de las figuras en el PDF. No se verificaron los once libros sin DOI, el contenido de la documentación de proveedores ni los originales firmados de los consentimientos, que el texto declara conservados en papel. Las secciones de arquitectura e implementación no cambiaron desde el dictamen anterior y se revisaron solo en los puntos señalados.

**Nota de vigencia.** Mientras se realizaba esta evaluación, la rama `main` avanzó ocho commits, hasta `5e25bf7` (cambio c-216, 13-11-2026, 21:24). Ese cambio agrega una subsección de sensibilidad a la referencia de verdad al final del capítulo de resultados, reencuadra dos párrafos sobre la revisión humana, declara la equivalencia del clasificador entre la configuración evaluada y la entregada y divide párrafos del capítulo legal. Se comprobó sobre `5e25bf7` que no modifica el fondo de los pasajes observados en este dictamen: el resumen, la discusión sobre el arbitraje, las cifras de la clase Sistemas, las dos líneas de trabajo futuro, la tabla de calibración, la portada y el Anexo B conservan su contenido. Con una salvedad de forma: c-216 sí reescribe dos de los tres pasajes de la discusión sobre el arbitraje (`08-discusion.tex:20` y `:60`), donde el literal de `0,8447` pasa a una remisión a la tabla fuera de muestra; el razonamiento sobre el arbitraje pendiente se mantiene, pero esas dos líneas ya no contienen la cifra literal. La subsección nueva no fue evaluada y queda fuera de este dictamen.

---

## Veredicto general

**APROBADO CON OBSERVACIONES.**

Entre el dictamen anterior y esta versión el trabajo incorporó evidencia nueva, que era lo único que podía mejorar su punto más débil. Se arbitraron los casos discordantes de la validación fuera de muestra con un tercer etiquetador, se reforzaron las clases chicas, se midió una línea de base supervisada clásica, se analizó la calibración de la confianza con una regla fijada antes de calcular y se informó el intervalo de confianza de la reducción de tiempo. Todas las cifras nuevas se reprodujeron desde los datos. Las afirmaciones excesivas que el dictamen anterior señaló en las conclusiones fueron retiradas.

La observación central de esta evaluación es de integración. El resultado más riguroso del trabajo, la exactitud fuera de muestra sin exclusión de casos, es desfavorable (0,6893 sobre 206 casos) y está informado con honestidad en el capítulo de resultados. Sin embargo, el resumen no lo menciona, la discusión sigue razonando como si el arbitraje estuviera pendiente y las recomendaciones proponen como trabajo futuro mediciones que ya se ejecutaron. Además, esa cifra se presenta sin ponderar pese a que el refuerzo alteró la composición del corpus, y la calibración fuera de muestra quedó calculada sobre el subconjunto que el propio texto califica de sesgado. Son defectos corregibles con redacción y con cálculos sobre datos que ya están versionados.

---

## Observaciones por sección

### 1. Estructura general — Cumple, con observaciones

El documento conserva el orden canónico y ahora justifica de forma expresa la ubicación del capítulo legal antes de los resultados, con el argumento de que las condiciones del tratamiento de datos condicionan la lectura de la evidencia. El Anexo I dejó de ser una bitácora y se redujo a una nota de versiones de dos subsecciones, lo que atiende la observación anterior.

Subsisten cuatro problemas. El primero es de jerarquía: la validación fuera de muestra, el arbitraje y la comparación con la línea de base figuran como párrafos de la subsección «Resultados de la campaña complementaria de medición» (`07-resultados.tex:278`), aunque usan otro corpus, otros etiquetadores y otro propósito. Son los resultados que más pesan sobre la tercera sub-hipótesis y merecen subsección propia; la frase inicial del capítulo, que anuncia siete apartados (`07-resultados.tex:6`), tampoco los nombra. El segundo es de identificación del documento: la portada dice «9 de noviembre de 2026, Versión 1.2.19» (`00-portada.tex:30-31`) y el Anexo B declara que la versión entregada es el tag `v1.3.0` y que «los commits posteriores no modifican las fuentes de la tesis» (`12-anexos.tex:58`). Esa afirmación es falsa en la versión examinada: después del tag hay veintidós commits que modifican las secciones, y el corpus arbitrado, la línea de base y el análisis de calibración no existen en `v1.3.0`. El lector que siga la referencia verificable que ofrece el anexo no encontrará la evidencia que el texto informa. El tercero es la reaparición de identificadores internos en el cuerpo («change c-206», en `07-resultados.tex:316`, en la tabla de la línea 328 y su nota, y en `09-conclusiones.tex:37`), que el dictamen anterior había dado por retirados. El cuarto es el Anexo J, que reproduce respuestas a preguntas del tribunal: es material de preparación de la defensa y no contenido de una tesis.

### 2. Hipótesis — Cumple

La hipótesis principal se desdobla en tres sub-hipótesis, cada una con su contraste y su criterio de falsación. La introducción ya no mezcla el enunciado con el veredicto y remite a resultados; la asimetría de la regla de tres vías está declarada en la introducción y en la metodología, junto con el carácter posterior del denominador de 147 casos. Son correcciones bien hechas.

Quedan dos debilidades de origen, ambas declaradas. La primera sub-hipótesis no fija un efecto mínimo relevante. Las dos hipótesis subsidiarias, entre ellas la de eficiencia del esquema híbrido, siguen sin contraste, y la línea de base incorporada no las aborda porque no incluye un brazo de modelo de lenguaje solo, como el texto reconoce (`04-marco-metodologico.tex:83`).

### 3. Objetivos — Cumple, con observaciones menores

El objetivo general es evaluable y los específicos fueron ajustados: el primero ya pide comunicación sincrónica, que es lo implementado, y el tercero dejó de exigir una complejidad percibida que no se midió. El cuarto promete intervalos de confianza y ahora los cumple también para la reducción de tiempo.

El umbral del 85 % sigue apoyado en una estimación propia del costo de una derivación errónea, sin registro cuantitativo, lo que el texto admite. El alcance declara fuera del trabajo «los modelos de aprendizaje supervisado entrenados con corpus propios» (`01-introduccion.tex:74`), mientras la versión actual entrena y evalúa uno como línea de base; la delimitación debe precisar que lo excluido es un modelo afinado con el corpus acumulado en operación.

### 4. Estado del arte — Cumple, con observaciones

Mantiene sus fortalezas: protocolo de búsqueda explícito con cadenas, bases y fechas de corte, limitación declarada sobre repositorios regionales y una lectura que no oculta resultados adversos al enfoque propio. La verificación externa confirmó la existencia y los metadatos de todas las fuentes de 2025 y 2026.

Las debilidades son las ya conocidas y no se modificaron. Son seis los trabajos específicos y uno de ellos, el de Colavito y colaboradores, clasifica incidencias de GitHub y no tickets de mesa de ayuda, sin que el texto haga la salvedad. Varias fichas descansan en el resumen del artículo; las cifras atribuidas a Paramesh (90,60 % y 91,81 %) y a Colavito no pudieron comprobarse en los resúmenes disponibles. La afirmación de que ningún trabajo declara un corpus en español se apoya en un dato ausente en cuatro de seis filas.

### 5. Marco teórico — Cumple

Se incorporaron los conceptos que faltaban: acuerdo entre anotadores y kappa, clasificación multietiqueta y las pruebas estadísticas empleadas, cada uno con su fuente primaria. El marco quedó alineado con la evidencia.

Faltan, por las incorporaciones de esta versión, los fundamentos de la línea de base (representación TF-IDF y regresión logística) y de las medidas de discriminación (puntaje de Brier y AUROC), que se definen recién en la metodología; el glosario tampoco los recoge. En el pasaje sobre intervención humana se atribuye a Mosqueira-Rey y colaboradores que las correcciones humanas mejoran la calidad del modelo cuando los datos escasean (`02-marco-teorico.tex:32`); el resumen de ese artículo describe una revisión taxonómica y no respalda esa afirmación, que debe verificarse en el texto completo o atenuarse.

### 6. Desarrollo metodológico y propuesta — Cumple, con observaciones de fondo

La propuesta técnica es consistente y reproducible. La metodología ganó tres piezas valiosas: una línea de base entrenada con los 200 casos de ajuste y evaluada sobre casos que no intervinieron en el entrenamiento, con contraste pareado; un análisis de calibración con regla de selección fijada antes de calcular las salidas, cuyo carácter no ciego se declara; y el intervalo por remuestreo de la reducción de tiempo. La verificación confirmó que no hay solapamiento entre el corpus de ajuste y el de prueba y que la regla de calibración se escribió antes que los resultados, aunque esto último solo se demuestra con las fechas de autor de los commits, porque las fechas de commit están igualadas.

Las observaciones de esta versión son las siguientes.

**El diseño de la validación fuera de muestra no está descrito en la metodología.** El resultado que decide la lectura de la tercera sub-hipótesis no tiene apartado metodológico: su diseño aparece en dos oraciones dentro de resultados (`07-resultados.tex:312-316`). El texto no informa de dónde ni de qué período provienen los 150 casos, que se reunieron por cuotas de canal con sobremuestreo deliberado de Bases de Datos, según el protocolo del repositorio. Tampoco informa que los 56 casos de refuerzo se reunieron y etiquetaron el 13 de noviembre, cuando ya se conocía el mal desempeño en Sistemas, sin una cuota fijada de antemano, y que 40 de esos 56 pertenecen a esa clase. Esa selección perjudica al clasificador y por eso no es sospechosa de favorecer el resultado, pero es una decisión de muestreo posterior a los datos y debe declararse como tal.

**La referencia arbitrada depende de una sola persona en un tercio de los casos.** El tercer etiquetador fijó la referencia en 64 de los 206 casos. La regla no es de mayoría: cuando los dos primeros difieren, decide el tercero. En seis casos los tres asignaron sectores distintos y prevaleció el tercero; el repositorio los marca, pero la tesis no los menciona. El clasificador acierta 109 de los 142 casos con consenso (0,768) y 33 de los 64 arbitrados (0,516).

**La cifra de 0,6893 no es comparable sin ponderación.** El corpus arbitrado tiene 61 casos de Sistemas sobre 206, cuando el corpus de ajuste tenía 16 sobre 200. El diseño del cambio que introdujo el refuerzo preveía informar el resultado con y sin ponderación, y el texto solo informa la cifra cruda para el clasificador híbrido, aunque sí pondera la de la línea de base. Recalculada en esta evaluación con la composición del corpus de 200, la exactitud estricta es de 0,7489, con un intervalo por remuestreo de [0,68; 0,81]. Sobre los 150 casos del diseño original, sin exclusión, es de 112 de 150 (0,7467; intervalo de Wilson aproximado [0,67; 0,81]). Ninguna de las dos figura en el texto. Ambas confirman la refutación del umbral, porque sus límites superiores quedan por debajo de 0,85, pero sitúan el desempeño fuera de muestra en el mismo orden que el medido dentro de ella (0,735) y no siete puntos por debajo.

**La calibración fuera de muestra se calculó sobre el subconjunto con exclusión.** La metodología y la tabla correspondiente usan los 34 casos de la etapa Gemini entre los 103 con consenso (`04-marco-metodologico.tex:85`, `07-resultados.tex:195-221`), que es la referencia que el propio texto declara sesgada hacia los casos fáciles. Sobre los 91 casos de esa etapa en el corpus arbitrado, recalculados en esta evaluación, la exactitud es de 0,5934 con una confianza media de 0,9055: la sobreconfianza es de 0,31 y no de 0,15, el error de calibración esperado sube de 0,17 a 0,32 y el umbral de 0,86, que en la descripción del texto aceptaba 25 casos con exactitud de 0,880, acepta 55 con 0,745. La conclusión cualitativa del texto se sostiene y se refuerza, pero las magnitudes informadas subestiman el problema.

**Subsisten las limitaciones estructurales ya señaladas**, todas declaradas: muestra por conveniencia de una sola organización, ajuste del clasificador sobre el corpus de evaluación, instrumentos distintos en los dos brazos de la comparación de tiempos, orden fijo entre brazos y llamadas recitadas por un autor. La sección de amenazas a la validez sigue enumerando seis (`04-marco-metodologico.tex:89`) y no incorpora las propias de la validación fuera de muestra.

Una nota sobre reproducibilidad: el clasificador congelado produjo los mismos sectores en las dos corridas sobre los 103 casos comunes, pero la confianza de Gemini difirió en 7 de sus 34 casos. La señal sobre la que se construye la revisión humana no es estable entre ejecuciones, y eso corresponde decirlo junto al análisis de calibración. Además, el commit que registra la primera corrida fuera de muestra (`561b3c4`) no es alcanzable desde ninguna rama ni tag del repositorio: quedó como objeto colgante, de modo que no se reproduce desde un clon y la corrida que identifica no es reconstruible.

### 7. Conclusiones — Cumple, con observaciones

Las correcciones pedidas se hicieron. Ya no se afirma que el marco normativo permite operar sin riesgos de cumplimiento: se dice que la operación con datos reales queda condicionada a un instrumento de transferencia que aún no está suscrito. Se retiró la afirmación sobre el costo de inferencia, la viabilidad económica se declara condicional y la generalización regional pasó a ser una hipótesis por validar. El balance neto se rehízo con una referencia común para los dos brazos. La tabla de cumplimiento de objetivos incorpora el resultado arbitrado.

Los problemas actuales provienen de no haber propagado el arbitraje a todo el razonamiento.

La discusión interpreta la validación fuera de muestra únicamente con la cifra de 0,8447 sobre 103 casos, y sostiene que esa cifra «no puede presentarse como superación del umbral sin el arbitraje de los 47 discordantes» y que alcanzar 0,85 exigiría que acertaran 41 de los 47 (`08-discusion.tex:8` y `:20`). El arbitraje ya se hizo: el clasificador acertó 25 de los 47. El análisis de escenarios quedó reemplazado por una medición y la discusión no lo dice. La séptima limitación (`08-discusion.tex:60`) repite el mismo cuadro sin el resultado arbitrado.

La clase Sistemas se describe en la discusión, en las conclusiones y en las recomendaciones con un F1 de 0,2222 sobre 5 casos (`08-discusion.tex:28`, `09-conclusiones.tex:37`, `10-recomendaciones.tex:18`), y se afirma que hoy no puede estimarse con la precisión necesaria. El capítulo de resultados informa que pasó a 61 casos y dejó de ser no estimable, con F1 de 0,5905 y sensibilidad de 0,5082. El párrafo de conclusiones contiene las dos versiones a pocas líneas de distancia. Con 61 casos el trabajo ya tiene material para responder la pregunta que plantea sobre esa frontera, y no lo analiza: 16 de los 30 errores van a Soporte Técnico Software y 8 a Seguridad Informática.

El resumen no menciona la validación fuera de muestra, el arbitraje, la línea de base ni la calibración (`00-resumen.tex:11-15`). Informa solo cifras dentro de la muestra y por eso no representa las conclusiones del trabajo.

El balance neto usa la tasa de error medida dentro de la muestra. Si se la reemplaza por la tasa fuera de muestra ponderada (0,2511), el balance pasa a ser de aproximadamente +14,8, −2,6 y −20,0 horas-persona por trimestre con 5, 10 y 15 minutos por derivación errónea; con la tasa cruda de 0,3107 es de +1,7, −28,9 y −59,4. Ese cálculo mezcla corpus y referencias y solo vale como sensibilidad, pero muestra que la frase «con una referencia común el balance neto no resulta negativo» depende de usar la exactitud del corpus sobre el que se ajustó el clasificador. Debe informarse.

Por último, dos afirmaciones merecen ajuste. La conclusión de que el modelo de lenguaje resultó «una alternativa técnicamente viable para la clasificación de tickets» (`09-conclusiones.tex:47`) convive con una sub-hipótesis de exactitud refutada dentro y fuera de la muestra, y fuera de la muestra la etapa Gemini es la más débil (54 de 91 frente a 88 de 115 de las reglas). Y la sección de arquitectura conserva que el diseño «reduce la latencia y el costo de inferencia» (`05-arquitectura.tex:68`), afirmación que la discusión declara no contrastada.

### 8. Trabajos futuros — Cumple, con observaciones

La sección quedó ordenada en tres niveles de prioridad que las subsecciones respetan; la mayoría de las líneas tiene criterio de éxito y las ampliaciones de producto se rotulan expresamente como no derivadas de una limitación medida. La línea de calibración se reescribió con lo ya medido y distingue con claridad qué no funcionó de qué resta probar.

Dos líneas proponen lo que esta versión ya ejecutó. La de la frontera entre Sistemas y Soporte Técnico Software plantea como próximo paso el sobremuestreo con doble etiquetado y arbitraje por un tercer etiquetador (`10-recomendaciones.tex:18`), que es exactamente lo realizado. La de validación sobre un corpus independiente fija como criterio de éxito que el arbitraje se ejecute antes de reportar la exactitud (`10-recomendaciones.tex:26`). Ambas deben reformularse a partir del resultado obtenido: la primera, hacia el análisis de la taxonomía con los 61 casos disponibles; la segunda, hacia un corpus de composición natural y con arbitraje por mayoría de tres etiquetadores.

### 9. Bibliografía — Cumple

Tiene 92 entradas, todas citadas y sin citas huérfanas. De los 46 identificadores consultados, 44 DOI resolvieron en Crossref a la obra citada, con título, primer autor y publicación coincidentes, y los dos restantes son identificadores de arXiv verificados por su vía. Todas las entradas de 2025 y 2026 existen. La verificación externa que el dictamen anterior dejó pendiente queda cumplida, y no se encontró ninguna fuente inexistente. Se corrigieron la versión de la entrada del repositorio, los tipos de entrada de tres actas y la página de la cita de Zanzotto; la referencia de Brier agregada en esta versión es correcta. La normativa argentina citada coincide con las fuentes oficiales.

Quedan defectos menores: cinco claves cuyo año no coincide con el del campo, la dirección de ServiceNow que no respondió a la consulta y no pudo verificarse, y la conveniencia de mencionar en el capítulo legal la Resolución 198/2023 de la Agencia de Acceso a la Información Pública sobre cláusulas modelo, que complementa la Disposición 60-E/2016 citada. La entrada del repositorio deberá actualizarse cuando se fije la nueva versión.

---

## Seguimiento del dictamen sobre v1.3.0

De las quince recomendaciones, once están resueltas: la tabla de la validación fuera de muestra con peor caso y macro-F1 y la ejecución del arbitraje (1), la incorporación de esa validación a las conclusiones (3), el consentimiento de los etiquetadores nuevos y su mención en el capítulo legal (4), el balance neto con referencia común (5), el intervalo de la reducción de tiempo (6), la declaración de la asimetría de la regla (7), la separación entre enunciado y veredicto (8), la reformulación de los objetivos primero y tercero (9), la ampliación del marco teórico (11), la justificación de la posición del capítulo legal (12) y el orden de los trabajos futuros (15).

Cuatro quedan parciales. La corrección de las conclusiones y del resumen (2) está hecha, pero la afirmación sobre latencia y costo sobrevive en la sección de arquitectura. La limpieza de referencias internas (10) se cumplió para las versiones y los dictámenes, y se perdió en parte al introducir de nuevo identificadores de cambio en resultados y conclusiones. La bibliografía (13) conserva las claves con año distinto y la dirección no verificada. El glosario (14) sumó las siglas pedidas y le faltan AUROC, Brier y TF-IDF.

De la devolución de segunda instancia siguen abiertos la repetición de cifras, que ahora afecta al bloque de la validación sobre 103 casos, repetido con la misma estructura tres veces en la discusión, y la copia del artículo de Paket y colaboradores, cuya ficha sigue apoyada en el resumen, limitación que el texto declara.

Sobre el consentimiento cabe una precisión: el registro versionado consigna información verbal el 12 de noviembre y confirmación escrita el 13, de modo que para los dos primeros etiquetadores la constancia escrita es posterior a su participación. El texto lo dice y remite los originales al expediente físico; desde el repositorio solo se comprueba la plantilla y la tabla de fechas.

---

## Recomendaciones

**Necesarias antes de la defensa:**

1. Reescribir en la discusión los tres pasajes sobre la validación fuera de muestra (`08-discusion.tex:8`, `:20` y `:60`) a partir del resultado arbitrado. Informar que el clasificador acertó 25 de los 47 casos antes excluidos y retirar el análisis de escenarios como argumento principal.
2. Informar la exactitud fuera de muestra en tres lecturas: cruda sobre 206 casos, ponderada por la composición del corpus de ajuste y sobre los 150 casos del diseño original sin exclusión. Agregar la matriz de confusión y las métricas por clase del corpus arbitrado como tabla.
3. Recalcular la calibración fuera de muestra sobre los 91 casos de la etapa Gemini del corpus arbitrado y presentarla junto a la de los 34 casos con consenso.
4. Incorporar al resumen la exactitud fuera de muestra y la comparación con la línea de base.
5. Actualizar todo lo que se dice de la clase Sistemas en discusión, conclusiones y recomendaciones con los 61 casos, y reformular las dos líneas de trabajo futuro que ya se ejecutaron.
6. Describir en la metodología el diseño de la validación fuera de muestra: procedencia y período de los casos, cuotas, sobremuestreo, carácter posterior del refuerzo, regla de arbitraje y los seis casos con tres etiquetas distintas. Sumar las amenazas correspondientes a la sección de validez.
7. Crear un tag nuevo que contenga el texto y la evidencia vigentes, y corregir con él el Anexo B, la entrada bibliográfica del repositorio y la portada, que hoy indica una versión y una fecha anteriores.

**De consistencia:**

8. Agregar al balance neto la sensibilidad con la tasa de error fuera de muestra.
9. Dar a la validación fuera de muestra y a la línea de base una subsección propia en resultados y actualizar la frase que enumera los apartados.
10. Retirar los identificadores internos de cambio del cuerpo y de la tabla, y la afirmación sobre latencia y costo de la sección de arquitectura.
11. Matizar la conclusión sobre la viabilidad técnica del modelo de lenguaje para la clasificación, a la luz del desempeño de la etapa Gemini fuera de muestra.
12. Declarar que la confianza de Gemini varió entre corridas en 7 de 34 casos.
13. Precisar en el alcance qué tipo de modelo supervisado queda fuera del trabajo.

**De forma:**

14. Completar el glosario con AUROC, puntaje de Brier y TF-IDF, y agregar al marco teórico una mención breve de la línea de base.
15. Reducir la repetición del bloque de cifras de la validación sobre 103 casos.
16. Corregir las cinco claves bibliográficas con año distinto, verificar o reemplazar la dirección de ServiceNow y revisar la atribución a Mosqueira-Rey.
17. Retirar el Anexo J del documento o trasladarlo al material de la defensa, y actualizar el cronograma, que no registra la validación fuera de muestra, el arbitraje ni la línea de base.

---

## Consideración final

El trabajo está en condiciones de ser defendido y es mejor que el evaluado en la versión anterior, porque respondió a las observaciones de fondo con mediciones y no con redacción. El arbitraje dio un resultado adverso y se lo informó sin atenuarlo en el capítulo de resultados, lo que habla bien del criterio de los autores. La tarea pendiente es que el resto del documento razone a partir de ese resultado. Un tribunal que lea el resumen y la discusión creerá que la exactitud fuera de muestra es de 0,84 con un arbitraje pendiente, y encontrará en la tabla de resultados que es de 0,69 con el arbitraje hecho. Esa distancia entre capítulos es hoy el principal riesgo en la defensa, y se cierra con los datos que ya están en el repositorio.

---

## Calificación sugerida según la rúbrica de la cátedra

Se aplica la *Rúbrica de Evaluación de Tesis de Ingeniería* con las advertencias habituales: las ponderaciones suman 115, el décimo criterio (defensa oral, peso 10) no es evaluable y la nota del documento escrito se computa sobre los nueve criterios restantes (peso 105).

| Criterio | Peso | Puntaje | Fundamento |
|---|---|---|---|
| 1. Definición del problema | 15 | 8,5 | Sub-hipótesis con contraste y falsación, enunciado separado del veredicto, asimetría de la regla declarada. Descuenta: umbral del 85 % apoyado en estimación propia, hipótesis subsidiarias sin contraste. |
| 2. Justificación y relevancia | 10 | 8 | Sin cambios respecto de la versión anterior. |
| 3. Marco teórico y revisión bibliográfica | 15 | 8,5 | Marco ampliado con acuerdo entre anotadores, multietiqueta y pruebas. Descuenta: fichas apoyadas en resúmenes, un trabajo ajeno al dominio sin salvedad, fundamentos de la línea de base ausentes. |
| 4. Metodología de investigación | 20 | 8 | Arbitraje sin exclusión, línea de base con contraste pareado, calibración con regla previa, intervalo de la reducción. Descuenta: diseño fuera de muestra sin apartado metodológico, refuerzo posterior a los datos y no declarado, un solo árbitro en el 31 % de las referencias, limitaciones estructurales previas. |
| 5. Desarrollo técnico o experimental | 15 | 9 | Sistema completo, pruebas, integración continua y evidencia versionada con sumas de verificación. Descuenta: la versión declarada como entregada no contiene la evidencia nueva. |
| 6. Resultados y análisis | 10 | 8,5 | Todas las cifras nuevas se reprodujeron. Descuenta: resultado arbitrado sin ponderación ni tabla por clase, calibración fuera de muestra sobre el subconjunto con exclusión. |
| 7. Conclusiones y aportes | 10 | 7,5 | Se retiraron las afirmaciones excesivas y se corrigió la contradicción con el capítulo legal. Descuenta: discusión y resumen no integran el resultado arbitrado, cifras superadas sobre la clase Sistemas, balance neto sin la tasa fuera de muestra. |
| 8. Redacción académica y estructura | 5 | 7 | Anexo I reducido y posición del capítulo legal justificada. Descuenta: portada y Anexo B desactualizados, identificadores internos reintroducidos, resultados principales anidados en otra subsección, repetición de cifras. |
| 9. Uso de referencias y normas de citación | 5 | 9 | 92 entradas citadas, sin huérfanas, con los DOI verificados externamente. Descuenta: defectos formales menores. |
| 10. Defensa oral | 10 | — | No evaluable. |

**Cálculo.** 8,5 × 15 + 8 × 10 + 8,5 × 15 + 8 × 20 + 9 × 15 + 8,5 × 10 + 7,5 × 10 + 7 × 5 + 9 × 5 = 870. Dividido por el peso efectivo (105): **8,29**.

**Calificación sugerida del documento escrito: 8 (ocho); 8,29 ponderado.**

**Relación con el dictamen anterior (7,83).** La mejora de 0,46 puntos se explica sobre todo por el criterio de metodología, que sube de 7 a 8 por la evidencia nueva, y por la verificación externa de la bibliografía. La proyección que aquel dictamen hacía para las correcciones de redacción (8,05) quedó superada porque los autores ejecutaron además el arbitraje y la línea de base, que allí se señalaban como la única vía para mejorar ese criterio.

**Proyección tras las siete recomendaciones necesarias.** El criterio 4 pasaría a 8,5, el 6 a 9, el 7 a 8,5 y el 8 a 8: 900 sobre 105, **8,57**.

**Proyección con defensa oral** (sobre 115, partiendo de 870): con una defensa de 7, la nota final resulta 8,17; con 8, 8,26; con 9, 8,35; con 10, 8,43.

Esta calificación es una sugerencia del evaluador y no anticipa la del tribunal.
