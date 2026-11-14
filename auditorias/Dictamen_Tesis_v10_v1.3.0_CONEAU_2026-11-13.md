# Dictamen de evaluación — Tesis de grado (criterios CONEAU)

**Documento:** «Automatización de Mesa de Ayuda con N8N» (Gomez Bustos, Sevilla), UTN.
**Versión examinada:** v10, release `v1.3.0`; rama `main`, commit `6615376`. Fuente LaTeX en `docs/Tesis/v10 (IA)/paper/sections/` y `Bibliography_base.bib`.
**Fecha:** 13 de noviembre de 2026.
**Antecedentes considerados:** dictamen sobre v1.2.16 (9-11-2026), devolución de segunda instancia del tribunal sobre v1.2.18 (11-11-2026) y los pull requests 84 a 96.

**Alcance y límites de esta evaluación.** Se evaluó el texto fuente, no el PDF compilado: no se examinaron la legibilidad de las figuras ni la paginación. La correspondencia entre citas y bibliografía se verificó de forma automática; la existencia real de cada fuente no se comprobó contra bases externas. La lectura de los capítulos se hizo por partes independientes y los puntos dudosos se contrastaron luego contra el texto. Lo que no pudo verificarse se indica como tal.

---

## Veredicto general

**APROBADO CON OBSERVACIONES.**

El trabajo presenta un sistema completo y funcionando, una metodología declarada con una transparencia poco habitual en el nivel de grado y resultados cuya aritmética cierra. Reconoce sin atenuantes que la sub-hipótesis de exactitud quedó refutada dentro de la muestra y que la de intervención humana quedó no concluyente. Esa honestidad es su principal fortaleza.

Las observaciones son de dos órdenes. Las primeras son estructurales y ya no se corrigen con redacción: la referencia de verdad es frágil (acuerdo entre etiquetadores moderado, kappa de 0,5569), el clasificador se ajustó sobre el mismo corpus con el que se lo evaluó, no hay línea de base contra la cual comparar el enfoque híbrido y los dos brazos de la comparación de tiempos se midieron con instrumentos distintos y en orden fijo. El texto las declara casi todas. Las segundas sí son corregibles antes de la defensa: las conclusiones afirman en algunos pasajes más de lo que los resultados sostienen y hay tres puntos de las devoluciones anteriores que no están cerrados.

Respecto de la pregunta sobre los arreglos: **no están todos hechos, aunque sí la gran mayoría.** El detalle figura en la sección «Seguimiento de las correcciones».

---

## Observaciones por sección

### 1. Estructura general — Cumple, con observaciones

El documento sigue el orden canónico: resumen, glosario, introducción, marco teórico, estado del arte, metodología, arquitectura, implementación, resultados, discusión, conclusiones, recomendaciones y anexos. Tres rasgos lo debilitan.

El capítulo de aspectos legales se inserta entre implementación y resultados (`main.tex:58`), lo que interrumpe el paso natural del desarrollo a la evidencia. Los resultados aparecen anticipados en el resumen, en la introducción y en la metodología, de modo que los capítulos previos no son neutros respecto de lo que se va a demostrar. Por último, el cuerpo conserva prosa propia de un control de cambios: «una versión anterior de esta tesis la declaró refutada» (`01-introduccion.tex:34`, `04-marco-metodologico.tex:81`), rutas internas del repositorio (`03-estado-del-arte.tex:8`) y seis etiquetas de versión conviviendo. Un lector externo no tiene esas versiones ni esas rutas. El Anexo I, que reproduce la historia de nueve dictámenes, agrava el problema: es una bitácora de proceso, no un anexo de tesis.

### 2. Hipótesis — Cumple, con observaciones

No hay una hipótesis única sino una principal desdoblada en tres sub-hipótesis contrastables, cada una con prueba y criterio de falsación (`01-introduccion.tex:32-38`). Es una formulación comprobable y bien delimitada. Las observaciones son las siguientes.

La primera sub-hipótesis (reducción del tiempo) no fija un efecto mínimo relevante: cualquier diferencia significativa la confirma. La segunda (acción manual no superior a 0,15) usa una regla de tres vías que declara «refutado» cuando la estimación puntual alcanza la cota, sin emplear el intervalo; el texto admite que el denominador se adoptó después de conocer los datos, pero no dice de forma expresa que esa regla es asimétrica. La tercera une exactitud y F1 macro en una conjunción y excluye del promedio a la clase Bases de Datos, con un solo caso, sin que conste que esa exclusión se fijó de antemano. Las dos hipótesis subsidiarias, entre ellas la de mayor eficiencia del enfoque híbrido frente al modelo de lenguaje solo, quedan «no contrastadas» pese a que el enfoque híbrido es el núcleo del diseño.

El enunciado de cada hipótesis aparece mezclado con su resultado («esta sub-hipótesis se declara confirmada»). En la introducción corresponde enunciar; el veredicto pertenece a resultados y conclusiones.

### 3. Objetivos — Cumple, con observaciones

El objetivo general es claro y los específicos cuarto y sexto son verificables. Los objetivos primero, tercero y quinto son entregables antes que metas medibles; el tercero exige integrar los canales «sin incrementar la complejidad operativa percibida» (`01-introduccion.tex:50`) y no existe métrica ni instrumento para esa percepción. El primero pide «comunicación asincrónica» y la implementación es sincrónica, lo que las conclusiones reconocen sin que el objetivo se haya reformulado.

El umbral del 85 % carece de fundamento numérico: el propio texto dice que la literatura «no permite fijar un piso numérico común» (`01-introduccion.tex:48`). Además el segundo objetivo lo rebaja a «criterio de éxito contingente», mientras la pregunta de investigación y la tercera sub-hipótesis lo tratan como criterio central. Conviene una sola posición.

### 4. Estado del arte — Cumple, con observaciones

Es de lo mejor resuelto: protocolo de búsqueda explícito, con bases, cadenas y criterios, limitación declarada, comparación crítica que incluye resultados adversos a la propia propuesta y una brecha formulada con cautela. Las fuentes son actuales.

Las debilidades son de cobertura. Los trabajos específicos sobre clasificación de tickets son seis, y uno trata de incidencias de GitHub y no de mesa de ayuda. Varias fichas se apoyan solo en el resumen del artículo por tratarse de textos de acceso cerrado, y el idioma del corpus figura como «no reportado» en cuatro de seis filas; de ahí que la afirmación de que ningún trabajo declara un corpus en español descanse en una ausencia de dato y no en una constatación. Las soluciones comerciales se describen a partir de documentación de los proveedores. Subsiste una tensión sin resolver: se señala la dependencia de servicios extranjeros como problema y se presenta el autoalojamiento como diferenciador, pero la inferencia y la telefonía dependen de proveedores externos.

### 5. Marco teórico — Cumple, con observaciones

Los ejes son pertinentes y están bien vinculados con el problema, y se distingue lo que afirman las fuentes de lo que infieren los autores. Faltan, sin embargo, los conceptos sobre los que descansa la evidencia: acuerdo entre anotadores y coeficiente kappa, clasificación multietiqueta (que afecta a 107 de los 200 casos), diseño cuasiexperimental y las pruebas estadísticas empleadas. Aparecen recién en la metodología, sin sustento teórico previo. A la inversa, se desarrolla el reconocimiento automático del habla y luego se aclara que el sistema no integra un motor propio. Hay siglas usadas y no definidas en el glosario (iPaaS, SaaS, kNN, CoT) y un detalle de implementación fechado dentro del marco teórico (`02-marco-teorico.tex:34`).

### 6. Desarrollo metodológico y propuesta — Cumple, con observaciones de fondo

La propuesta técnica es consistente: la arquitectura en capas se corresponde con el flujo, el modelo de datos y la interfaz, y las decisiones de diseño se justifican frente a alternativas. La estadística es apropiada para los datos (prueba de Wilcoxon, intervalos de Wilson, remuestreo, prueba de McNemar) y las cifras revisadas cierran entre tablas y texto. Se declaran las amenazas a la validez.

Las debilidades son las que limitan el alcance de las conclusiones:

- **Corpus.** Doscientos casos por conveniencia, de una sola organización, con clases de uno y dieciséis casos. El margen de error informado presupone un muestreo aleatorio que no se hizo, como el texto admite.
- **Referencia de verdad.** Las planillas del etiquetado original no se conservaron, el acuerdo del nuevo doble etiquetado es moderado y los etiquetadores fueron los operadores del brazo manual, uno de ellos autor.
- **Validación dentro de la muestra.** El vocabulario, las reglas y el texto de instrucción del modelo se ajustaron sobre los mismos doscientos casos.
- **Comparación de tiempos.** El brazo manual se cronometró en vivo con redondeo y siempre antes que el automatizado; el automatizado, con marcas del sistema. Las 81 llamadas fueron recitadas por un autor. Los dos operadores manuales difieren casi cuatro veces entre sí (20,1 s frente a 76,6 s), de modo que la magnitud de la reducción depende de quién opere. No se localizó un intervalo de confianza para la reducción del 71,2 %, pese a que el cuarto objetivo lo anuncia.
- **Lo evaluado no es lo entregado.** Varias funciones de la versión v1.3.0 son posteriores a la campaña de medición. El Anexo B lo documenta con una tabla correcta, pero el cuerpo no siempre lo recuerda.
- **Revisión humana inoperante.** El umbral de confianza no derivó ningún caso a revisión en el corpus (`07-resultados.tex:157`); el mecanismo de supervisión previsto por diseño no actuó.
- **Sin línea de base.** No hay comparación con el modelo de lenguaje solo ni con un clasificador supervisado clásico.

La validación fuera de muestra incorporada en v1.3.0 es el aporte que más mejora el trabajo: 150 casos nuevos, doble etiquetado ciego y clasificador congelado, con exactitud estricta de 0,8447 e intervalo [0,7625; 0,9021]. Está, no obstante, subinformada. Ocupa un párrafo sin tabla (`07-resultados.tex:284`), excluye 47 casos discordantes, casi un tercio del corpus, y no informa el peor caso ni el F1 macro. El texto reconoce que esa exclusión sesga hacia los casos fáciles.

### 7. Conclusiones — Cumple, con observaciones

Responden a cada objetivo mediante una tabla y a cada sub-hipótesis por separado, y declaran límites. Hay, con todo, afirmaciones que exceden la evidencia y que un tribunal va a señalar:

- Se afirma que el marco normativo permite operar «sin requerir sortear barreras legales ni asumir riesgos» de cumplimiento (`09-conclusiones.tex:51`). El capítulo legal dice que el instrumento exigido para la transferencia internacional no está suscrito y que el audio se envía al exterior antes de pseudonimizarse (`11-aspectos-legales.tex:18-22`). Es la inconsistencia más seria del documento.
- Se sostiene que el filtro determinístico «reduce el costo de inferencia» (`09-conclusiones.tex:47`), cuando la hipótesis de eficiencia se declaró no contrastada.
- Se habla de un patrón reproducible para organizaciones medianas de América Latina y de una arquitectura que «no depende de licencias propietarias», con evidencia de una sola organización y dependencia de Gemini y de N8N.
- El resumen dice que los resultados «respaldan la viabilidad técnica y económica» mientras el balance neto se declara indeterminado.

Las conclusiones tampoco incorporan la validación fuera de muestra, que solo aparece en discusión y recomendaciones. Es el único resultado que matiza la refutación de la tercera sub-hipótesis y debe figurar, con su límite.

Queda un punto por revisar que no se pudo cerrar: el balance neto de la discusión (`08-discusion.tex:99`) parece usar para el error del sistema la referencia original y para el error manual la de consenso. Si así fuera, la comparación sería asimétrica y el signo del balance podría cambiar.

### 8. Trabajos futuros — Cumple, con observaciones

Los primeros ítems derivan de defectos medidos (el umbral de confianza que no discrimina, la falta de un clasificador supervisado) y están fundamentados con citas y con tres niveles de prioridad. El resto es una lista de ampliaciones de producto sin relación con ninguna limitación medida ni fundamento: tableros de monitoreo, integración con mensajería, base de conocimientos, agente conversacional. El orden de las subsecciones no sigue la prioridad declarada y ningún ítem, salvo uno, trae criterio de éxito ni tamaño de muestra. La sección informa además un resultado, la validación fuera de muestra, que corresponde a resultados, y propone una comparación futura sobre el mismo corpus que ya se reconoció ajustado.

### 9. Bibliografía — Cumple, con observaciones

Tiene 91 entradas, todas citadas y sin citas huérfanas, en formato APA 7. Cerca de la mitad es de los últimos cinco años y predominan las fuentes con referato; las anteriores a 2015 son en su mayoría clásicos estadísticos justificados. Se cita normativa primaria.

Observaciones formales: la entrada del repositorio propio figura como versión 1.2.13 y el anexo cita v1.3.0; algunas actas están cargadas como artículo; hay claves cuyo año no coincide con el campo; Paket et al. se cita solo a partir del resumen; la atribución a Zanzotto sigue sin número de página. Queda pendiente una verificación externa de DOI, en especial de las dieciséis entradas de 2026. El propio documento reconoce que versiones anteriores tuvieron citas inexistentes, de modo que esa comprobación no es opcional.

---

## Seguimiento de las correcciones

### Dictamen sobre v1.2.16 (PR 84 y posteriores)

De los diecinueve puntos, dieciséis están resueltos en el texto vigente: el pasaje sobre la segunda sub-hipótesis, el Anexo I (nueve dictámenes), el tamaño del efecto mínimo detectable (0,276, coincidente con el código y los resultados), los tres disparadores de canal, el cronometraje mutuo, el nombre único de la caché, las erratas y el retiro del kappa de 0,87. Quedan:

- **Asimetría de la regla de tres vías: parcial.** El contenido está, pero no se declara expresamente.
- **Página de Zanzotto: sin atender**, aunque se redujo la atribución, que era la alternativa admitida.
- **Dirección web de ServiceNow: no verificada.**

### Devolución de segunda instancia sobre v1.2.18 (PR 85)

Las dos observaciones críticas (N-01, retiro del kappa de 0,87; N-02, nota sobre las cifras sintéticas de julio) están resueltas. También N-03 (tiempos por operador), N-04 (selección por conveniencia, con fechas), N-06 (llamadas recitadas, declaradas en metodología, discusión y conclusiones), N-08 (exactitud contra el consenso), N-09 (prueba unilateral y carácter posterior del denominador), N-10 (cobertura), N-13 (instrumento de transferencia no suscrito) y N-14.

- **N-05, procedencia de los tiempos automatizados: resuelta en lo sustancial.** El archivo versionado contiene 118 de los 119 casos de correo y formulario; uno queda sin registro, y el texto lo dice.
- **N-07 (oraciones largas), N-11 (legibilidad de figuras) y N-15 (tildes): no verificadas** en esta evaluación. Los identificadores internos de cambio fueron retirados del cuerpo.
- **N-12: parcial.** Se quitó la expresión objetada; la repetición de cifras persiste (la validación fuera de muestra aparece cuatro veces).
- **N-16: atendida.** El texto completo de Paket et al. se obtuvo el 14 de noviembre de 2026 y se depositó en la carpeta de fuentes del proyecto; la copia queda disponible para verificación. Mayor-Rocher et al. se cita en su versión de revista (preliminar en arXiv:2409.15334).

### Pendientes nuevos, posteriores a las devoluciones

- **Consentimiento de los etiquetadores E3 y E4.** El registro los tiene con la confirmación «por completar» y el capítulo legal solo menciona a los cuatro participantes anteriores. Es el mismo patrón que ya se objetó: una afirmación que se adelanta a su respaldo.
- **PR 94, sin integrar.** Amplía el análisis fuera de muestra con el peor caso (0,58 si los 47 excluidos se cuentan como errores), el F1 macro (0,7447) y la advertencia de que 0,8447 no puede presentarse como superación del umbral. Es justamente lo que le falta al texto vigente.
- **PR 95, sin integrar y con trabajo de campo por hacer.** El arbitraje de los 47 discordantes con un tercer etiquetador lleva 7 de 25 tareas.
- **PR 96**, de infraestructura, no afecta la tesis.

---

## Recomendaciones

**Antes de la defensa (necesarias):**

1. Integrar el PR 94 y llevar al capítulo de resultados una tabla de la validación fuera de muestra con el peor caso, el F1 macro y el acuerdo de los etiquetadores. Decidir si el arbitraje de los 47 casos se ejecuta o se declara diferido, y decirlo en el texto.
2. Corregir las conclusiones y el resumen: eliminar la frase sobre la ausencia de barreras legales o condicionarla a la suscripción del instrumento de transferencia; retirar la afirmación sobre el costo de inferencia; reemplazar «viabilidad económica» por la lectura condicional que ya figura en la discusión; acotar la generalización regional.
3. Incorporar la validación fuera de muestra a las conclusiones, con su límite.
4. Completar el registro de consentimiento de E3 y E4 y mencionarlos en el capítulo legal.
5. Revisar el balance neto para que el error del sistema y el manual se midan contra la misma referencia.
6. Informar un intervalo de confianza para la reducción del tiempo o retirar esa promesa del cuarto objetivo.

**De consistencia:**

7. Declarar en la introducción y en la metodología que la regla de tres vías es asimétrica.
8. Separar enunciado y veredicto de las hipótesis; unificar la posición sobre el umbral del 85 %.
9. Reformular el primer objetivo (comunicación sincrónica) y el tercero (quitar la complejidad percibida o medirla).
10. Limpiar del cuerpo las referencias a versiones anteriores y a rutas internas; reducir el Anexo I a una nota de versiones.
11. Agregar al marco teórico el acuerdo entre anotadores, la clasificación multietiqueta y las pruebas estadísticas.
12. Reubicar el capítulo legal después de la discusión o justificar su posición.

**De forma:**

13. Actualizar la versión de la entrada del repositorio, corregir los tipos de entrada, agregar la página de Zanzotto y verificar los DOI de las entradas de 2025 y 2026.
14. Completar el glosario con las siglas faltantes.
15. Ordenar los trabajos futuros por la prioridad declarada y quitar o fundamentar los que no derivan de una limitación medida.

---

## Consideración final

El trabajo está en condiciones de ser defendido. Su valor reside menos en los números alcanzados que en haber medido con método y declarado lo que no se alcanzó. El riesgo en la defensa se concentra en las conclusiones que contradicen al propio capítulo legal y en la validación fuera de muestra, que hoy se informa con su cifra más favorable y sin el peor caso. Ambas cosas se corrigen con trabajo de redacción y con la integración de un cambio que ya está escrito.

---

## Calificación sugerida según la rúbrica de la cátedra

Se aplica la *Rúbrica de Evaluación de Tesis de Ingeniería* con las mismas advertencias de los dictámenes anteriores: las ponderaciones suman 115, el décimo criterio (defensa oral, peso 10) no es evaluable y la nota del documento escrito se computa sobre los nueve criterios restantes (peso 105).

| Criterio | Peso | Puntaje | Fundamento |
|---|---|---|---|
| 1. Definición del problema | 15 | 8 | Tres sub-hipótesis con prueba y criterio de falsación. Descuenta: umbral del 85 % sin fundamento numérico, regla de tres vías asimétrica no declarada, enunciado mezclado con veredicto, hipótesis subsidiarias sin contraste. |
| 2. Justificación y relevancia | 10 | 8 | Problema real y bien situado. Descuenta: la estimación previa del tiempo manual (165 s) quedó lejos de lo medido (61,6 s) y la brecha de «autoalojamiento» convive con dependencia de proveedores externos. |
| 3. Marco teórico y revisión bibliográfica | 15 | 8 | Estado del arte con protocolo explícito y lectura crítica. Descuenta: faltan los conceptos que sostienen la evidencia (acuerdo entre anotadores, multietiqueta, pruebas), fichas apoyadas solo en resúmenes. |
| 4. Metodología de investigación | 20 | 7 | Estadística apropiada y amenazas declaradas. Descuenta: referencia de verdad frágil, ajuste y evaluación sobre el mismo corpus, sin línea de base, instrumentos asimétricos y orden fijo entre brazos, validación fuera de muestra con 31 % de exclusión. |
| 5. Desarrollo técnico o experimental | 15 | 9 | Sistema completo, con pruebas, integración continua y trazabilidad. Descuenta: lo evaluado no es lo entregado y la revisión humana por confianza no actuó en el corpus. |
| 6. Resultados y análisis | 10 | 8 | Cifras consistentes, con intervalos y análisis de sensibilidad. Descuenta: validación fuera de muestra sin tabla ni peor caso, sin intervalo para la reducción del tiempo. |
| 7. Conclusiones y aportes | 10 | 7 | Responden objetivo por objetivo y declaran límites. Descuenta: contradicción con el capítulo legal, afirmaciones de costo y viabilidad económica no sostenidas, omisión de la validación fuera de muestra. |
| 8. Redacción académica y estructura | 5 | 7 | Orden canónico y remisiones correctas. Descuenta: prosa de control de versiones en el cuerpo, Anexo I como bitácora, posición del capítulo legal. No se evaluó el PDF. |
| 9. Uso de referencias y normas de citación | 5 | 8,5 | 91 entradas citadas, sin huérfanas, APA 7. Descuenta: defectos formales menores y verificación externa de DOI pendiente. |
| 10. Defensa oral | 10 | — | No evaluable. |

**Cálculo.** 8 × 15 + 8 × 10 + 8 × 15 + 7 × 20 + 9 × 15 + 8 × 10 + 7 × 10 + 7 × 5 + 8,5 × 5 = 822,5. Dividido por el peso efectivo (105): **7,83**.

**Calificación sugerida del documento escrito: 8 (ocho); 7,83 ponderado.**

**Por qué difiere de la serie anterior (9,21 sobre v1.2.16).** Aquellos dictámenes midieron sobre todo el cumplimiento de las observaciones previas, y en eso el avance es real. Esta evaluación partió de una lectura independiente de los capítulos, sin los dictámenes a la vista, y pondera las limitaciones de diseño que la redacción no puede resolver. El resultado queda más cerca del 7,0 que asignó el tribunal en segunda instancia sobre v1.2.18, con la mejora atribuible a las correcciones de v1.2.19 y a la validación fuera de muestra de v1.3.0. No hay una caída de calidad entre versiones: cambia el criterio de exigencia.

**Proyección tras las seis recomendaciones necesarias.** Los criterios 6 y 7 pasarían a 8,5 y el 8 a 7,5: 845 sobre 105, **8,05**. Un puntaje mayor en el criterio 4 exige evidencia nueva (arbitraje de los 47 discordantes, línea de base), no redacción.

**Proyección con defensa oral** (sobre 115, partiendo de 7,83): con una defensa de 7, la nota final resulta 7,76; con 8, 7,85; con 9, 7,93; con 10, 8,02.

Esta calificación es una sugerencia del evaluador y no anticipa la del tribunal.
