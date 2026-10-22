# DICTAMEN DE EVALUACION ACADEMICA

**Documento evaluado:** *Automatizacion inteligente del registro de incidentes en mesas de ayuda empresariales mediante orquestacion de flujos con N8N y procesamiento de lenguaje natural basado en modelos de lenguaje grandes*. Trabajo Final de Carrera, Tecnicatura Universitaria en Programacion, UTN Facultad Regional Mendoza. Version `v1.0.1`, commit `bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0`, `docs/Tesis/v9 (IA)/paper/main.pdf`, 101 paginas. Autores: Gomez, Bustos y Sevilla.

**Fecha del dictamen:** 2026-10-22.

**Alcance del examen:** revision completa del cuerpo del documento (capitulos 1 a 12, referencias y anexos A-I), el archivo `Bibliography_base.bib` y los artefactos de compilacion. Se verifico la correspondencia citas-referencias, la resolucion de los DOI, la existencia de figuras y tablas, la coherencia numerica interna, y el cumplimiento especifico de las siete recomendaciones formuladas en el dictamen previo del 21-10-2026. No se re-ejecuto el sistema.

**Antecedente:** este dictamen es el tercero en la serie. El dictamen del 20-10-2026 emitio un veredicto de "Aprobado con observaciones de caracter mayor" y condicionaba la aprobacion a la resolucion de una inconsistencia critica en el capitulo de resultados (la contradiccion entre la tabla de calibracion y la tasa de intervencion humana del 9,5 %). El dictamen del 21-10-2026 verifico que esa inconsistencia se resolvio, emitio veredicto "Aprobado" y formulo siete recomendaciones de forma y completitud. El presente dictamen evalua en que medida esas siete recomendaciones fueron incorporadas en la version v1.0.1.

**Nivel de exigencia:** criterios de evaluacion universitaria argentina (CONEAU) calibrados al nivel de una tecnicatura.

---

## VEREDICTO GENERAL

**APROBADO.**

La version v1.0.1 incorpora de manera satisfactoria el nucleo de las siete recomendaciones formuladas en el dictamen anterior. Las tres recomendaciones sustantivas de mayor peso (rotular la sub-hipotesis de intervencion humana como no contrastada, incorporar referencias bibliograficas formales para las plataformas comerciales, y justificar o degradar el umbral de 5.000 casos) fueron atendidas con precision textual. Las cuatro restantes, de alcance mas limitado, muestran cumplimiento parcial o mantienen observaciones cosmeticas que no comprometen la solidez del trabajo. El documento es un trabajo final de tecnicatura internamente consistente, con una integridad academica destacable, y se encuentra en condiciones de ser defendido.

---

## EVALUACION DEL CUMPLIMIENTO DE LAS SIETE RECOMENDACIONES

### Recomendacion 1. Rotular la sub-hipotesis de intervencion humana como "no contrastada por ausencia de registro primario" y retitular la seccion homonima

**Cumple sustancialmente; observacion menor persiste.**

La recomendacion ha sido atendida con rigor sistematico. La expresion exacta "no contrastada por ausencia de registro primario" aparece cuatro veces en el documento: en el resumen en espanol (linea 13), en el abstract en ingles, en la introduccion (linea 34) y en las conclusiones (linea 6). La sub-hipotesis esta formulada con `\emph{}`, lo que la distingue como estado epistemico deliberado y no como resultado omitido. El resumen en ingles usa la expresion equivalente "not tested due to the absence of a primary record for per-case human intervention", garantizando la cobertura bilingue.

Respecto del retitulado de la seccion homonima: la subseccion en `07-resultados.tex` se titula ahora `Intervencion humana en el flujo automatizado` (antes contenia la palabra "reduccion"). El titulo actual es neutral respecto del resultado, con lo que la recomendacion queda atendida en su proposito esencial. Observacion menor: el cuerpo de esa subseccion declara que el gate no derivo ningun caso (confianza de Gemini siempre mayor o igual a 0,85 en el corpus), que es un hallazgo operativo positivo. Ese resultado podria destacarse con mayor prominencia en las conclusiones, en lugar de quedar subsumido bajo la declaracion de no contraste.

### Recomendacion 2. Incorporar referencias bibliograficas formales para las afirmaciones sobre plataformas comerciales y precios

**Cumple.**

El archivo `Bibliography_base.bib` contiene ahora dos entradas `@online` especificamente creadas para este proposito: `DigitalOcean2026_pricing` (DigitalOcean Droplets Pricing, consultado el 19-10-2026) y `Google2026_vertex_pricing` (Vertex AI Generative AI Pricing, consultado el 19-10-2026), ambas con `urldate` declarado y nota de consulta. El tipo `@online` es el apropiado para recursos de red con fecha de acceso variable.

Permanece un caso limite en `01-introduccion.tex` (linea 68), donde la referencia a Zendesk, Freshdesk y ServiceNow se formula como "relevamiento propio de la documentacion publica de los proveedores, consultada el 19-10-2026" sin `\parencite` adjunto. Esta formula es aceptable como observacion propia documentada con fecha, aunque seria preferible agregar entradas bibliograficas equivalentes a las ya incorporadas para DigitalOcean y Google Cloud. No se clasifica como defecto bloqueante al nivel de tecnicatura.

### Recomendacion 3. Reportar un intervalo de confianza del kappa, o mantener la declaracion de no computabilidad

**Cumple.**

La declaracion de no computabilidad esta explicitamente formulada en `04-marco-metodologico.tex` con la razon tecnica: "su calculo exige la tabla de acuerdo observado/esperado o las etiquetas por caso de ambos analistas, registros que no se conservaron en las fuentes disponibles; el valor puntual se informa, por lo tanto, sin incertidumbre asociada." Esta es la forma correcta de manejar un dato cuya precision no puede verificarse: declarar el limite y su causa, no silenciarlo.

### Recomendacion 4. Justificar o degradar el umbral de 5.000 casos a referencia indicativa explicita

**Cumple.**

El umbral aparece en dos ubicaciones con calificacion identica: en `10-recomendaciones.tex` y en `08-discusion.tex`, ambas con el texto "referencia indicativa de orden de magnitud, no derivada del corpus actual ni de un calculo de potencia estadistica". La degradacion es precisa y honesta: el valor se conserva como heuristica orientadora sin investirlo de precision estadistica que no tiene.

### Recomendacion 5. Recortar el eje de ASR al minimo conceptual necesario

**Cumple parcialmente.**

En `02-marco-teorico.tex`, el eje de reconocimiento automatico del habla ocupa exactamente 4 lineas de prosa con 2 citas, y cierra con la aclaracion explícita de que "el sistema propuesto no integra un motor de ASR". Esto cumple la recomendacion en su espiritu. La contraparte es que el capitulo de recomendaciones dedica una subseccion completa (~15 lineas) al agente conversacional telefonico en tiempo real con ASR avanzado, lo cual es coherente: el trabajo no lo implemento, pero lo proyecta como etapa siguiente con justificacion tecnica detallada.

### Recomendacion 6. Corregir el detalle estructural del capitulo legal y revisar comentarios internos de numeracion

**Cumple.**

El archivo `11-aspectos-legales.tex` contiene exactamente un `\section{}` ("Consideraciones éticas y aspectos legales"), con el resto articulado como `\subsection{}` y `\subsubsection{}`. Los defectos formales previamente reportados (literal "aggedright" impreso, corchete sin cerrar, remision hardcodeada erronea, rotulo "Appendices" en ingles, mencion residual a Redis) no aparecen en la version v1.0.1.

### Recomendacion 7. Declarar la fuente de la justificacion del umbral del 85 %

**Cumple con matiz.**

El segundo criterio de la justificacion del umbral del 85 % esta formulado en `01-introduccion.tex` como "estimacion propia de los autores a partir de la observacion operativa de la organizacion adoptante, sin un registro cuantitativo conservado". Esta formulacion cumple la recomendacion: declara el origen, el alcance y la limitacion. No hay pretension de fuente externa que no existe.

---

## OBSERVACIONES POR DIMENSION (EVALUACION COMPLETA)

### 1. Estructura general del documento

**Cumple.** La arquitectura del documento es completa y logicamente progresiva: portada, resumen bilingue, indices (general, de tablas, de figuras), glosario de 64 siglas, capitulos 1-12, referencias y 9 anexos (A-I). Las remisiones cruzadas usan `\autoref`/`\ref` de forma consistente. Los defectos formales de versiones anteriores estan ausentes. La trazabilidad de la version esta cerrada: el tag v1.0.1 y el hash completo del commit (`bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0`) constan en el Anexo I, lo que hace la version auditoriamente reproducible.

Observacion editorial menor: la tabla comparativa de `03-estado-del-arte.tex` tiene cuatro columnas (Solucion, Despliegue, Clasificacion automatica, Modelo de costo), pero el parrafo introductorio declara "cuatro dimensiones" e incluye "soberania sobre los datos" entre ellas. Esa dimension no aparece como columna de la tabla, sino solo en la prosa circundante.

### 2. Claridad y formulacion de la hipotesis

**Cumple.** La hipotesis principal esta desdoblada en tres sub-hipotesis con sus contrastes y criterios de falsacion. La primera (tiempo de registro) se declara confirmada (W=363, p=3,08e-32, r=0,9639). La segunda (intervencion humana por caso) se declara "no contrastada por ausencia de registro primario", con la aclaracion de que el gate no derivo ningun caso en el corpus. La tercera (exactitud y F1 macro) se declara refutada (exactitud 73,5 %, IC Wilson [67,0 %; 79,1 %]). El estado se informa consistentemente en resumen, introduccion y conclusiones en ambos idiomas.

### 3. Definicion y coherencia de los objetivos

**Cumple.** El objetivo general esta formulado en clave evaluativa. Los seis objetivos especificos son medibles y el segundo tiene el umbral de desempeño separado como criterio de exito contingente. La tabla de cumplimiento en las conclusiones mapea objetivo, grado de cumplimiento y evidencia, con el objetivo 2 marcado sin eufemismos como no alcanzado.

### 4. Estado del arte

**Cumple.** La revision bibliografica esta respaldada por un protocolo declarado con seis bases, cinco cadenas de busqueda (A1-A4 y B1), criterios de inclusion/exclusion y bitacora versionada. La afirmacion de vacancia esta acotada al alcance revisado. La tabla comparativa existe y es sustantiva. Observacion menor: inconsistencia entre las dimensiones declaradas en el parrafo introductorio y las columnas efectivas de la tabla (vease seccion 1).

### 5. Marco teorico

**Cumple.** Los ocho ejes teoricos desembocan en decisiones de diseño verificables. Human-in-the-loop esta definido con fuentes y grados de autonomia. Los conceptos antes formulados por asercion (BPA, iPaaS, alucinacion, calibracion) estan fundamentados. El eje de ASR ocupa 4 lineas con declaracion explicita de su alcance conceptual.

### 6. Desarrollo metodologico y propuesta

**Cumple.** El diseño cuasiexperimental esta documentado con doble etiquetado (kappa 0,87, sin IC por registros no conservados, declarado correctamente), Shapiro-Wilk, Wilcoxon con tamaño del efecto, intervalos de Wilson, bootstrap percentil, analisis de sensibilidad y cuatro amenazas a la validez. El criterio del tamaño muestral (disponibilidad operativa) esta declarado. La dependencia entre etiquetadores y operadores se explicita como limitacion.

### 7. Conclusiones

**Cumple.** Las conclusiones responden a los seis objetivos y a las tres sub-hipotesis con tabla de cumplimiento. Los numeros son internamente consistentes. El marco metrico unificado declara la referencia multietiqueta, la metrica primaria y advierte que el micro-F1 no es equivalente de la exactitud. La subseccion de intervencion humana declara que el gate no derivo ningun caso y que el aporte operativo del gate queda como "no medido".

### 8. Propuestas de trabajos futuros

**Cumple.** Las lineas estan priorizadas: primero las que atacan los defectos medidos, luego las extensiones funcionales. El umbral de 5.000 casos esta degradado a referencia indicativa en ambas ubicaciones. El agente conversacional telefonico tiene justificacion tecnica detallada.

### 9. Bibliografia

**Cumple con observacion sobre el conteo.** Los tipos bibliograficos de las dos entradas señaladas en el dictamen anterior estan corregidos: `Touvron2023` es `@misc` y `Jurafsky2023` es `@unpublished`. Se incorporaron entradas `@online` para plataformas comerciales. La correspondencia entre citas y referencias es perfecta en la version actual (sin citas huerfanas ni entradas sin usar).

El conteo de entradas es internamente consistente y no presenta discrepancia. La version v9 reportaba 54 entradas (dictamen de 21-10-2026) y la version v1.0.1 tiene 56: un incremento de exactamente dos entradas, que corresponde a las incorporaciones `@online` del change c-120 (`DigitalOcean2026_pricing` y `Google2026_vertex_pricing`). La verificacion sobre el arbol de trabajo confirma 56 entradas con 56 claves citadas unicas (correspondencia perfecta). Se deja constancia de esta verificacion para trazabilidad.

**Fe de errata (correccion de este dictamen):** una version previa de este informe consignaba "39 entradas" y afirmaba una discrepancia de conteo "de 54 a 39". Ese conteo era erroneo y se rectifica aqui tras verificacion directa (`grep -c "^@"` sobre `Bibliography_base.bib` = 56; historia git: 54 entradas antes de c-120, 56 despues, delta +2). No existe discrepancia bibliografica alguna y la recomendacion 4 original queda sin objeto.

---

## TABLA RESUMEN DE CUMPLIMIENTO

| Dimension | 20-10-2026 | 21-10-2026 | 22-10-2026 (v1.0.1) |
|---|---|---|---|
| 1. Estructura general | Cumple parcialmente | Cumple | Cumple |
| 2. Hipotesis | Cumple, con reservas | Cumple | Cumple |
| 3. Objetivos | Cumple parcialmente | Cumple | Cumple |
| 4. Estado del arte | Cumple parcialmente | Cumple | Cumple |
| 5. Marco teorico | Cumple parcialmente | Cumple | Cumple |
| 6. Metodologia y propuesta | Cumple parcialmente | Cumple | Cumple |
| 7. Resultados y conclusiones | No cumple | Cumple | Cumple |
| 8. Trabajos futuros | Cumple | Cumple | Cumple |
| 9. Bibliografia | Cumple | Cumple | Cumple |

---

## OBSERVACIONES RESIDUALES (no bloqueantes)

1. **Tabla comparativa de estado del arte**: el parrafo introductorio declara "cuatro dimensiones" incluyendo "soberania sobre los datos", pero la tabla tiene cuatro columnas y esa dimension no aparece como encabezado. Ajustar el parrafo introductorio o agregar la columna.

2. **Hallazgo del gate**: el hecho de que el clasificador Gemini nunca haya devuelto una confianza inferior a 0,85 en los 200 casos es un resultado empirico con valor propio. Conviene presentarlo explicitamente como hallazgo en la discusion, no solo como justificacion de la no contraste.

3. **Zendesk / Freshdesk / ServiceNow**: incorporar entradas `@online` con `urldate` para completar la cobertura bibliografica, de forma analoga a lo ya hecho para DigitalOcean y Google Cloud.

<!-- La observacion 4 original (discrepancia de conteo bibliografico 54 vs 39) queda retirada: la verificacion directa demuestra que no existe discrepancia (54 -> 56, delta +2 explicado por c-120). Vease la fe de errata en la seccion 9. -->

---

## RECOMENDACIONES CONCRETAS Y ACCIONABLES

1. Corregir la inconsistencia entre el parrafo introductorio de la tabla comparativa y los encabezados de columna reales (una linea de texto).

2. Agregar en la subseccion de intervencion humana (resultados o discusion) una frase que presente el resultado del gate (confianza de Gemini siempre >= 0,85 en el corpus) como hallazgo positivo sobre el comportamiento del clasificador en el dominio evaluado.

3. Incorporar entradas `@online` para Zendesk, Freshdesk y ServiceNow siguiendo el patron ya establecido, y agregar `\parencite` en `01-introduccion.tex` linea 68.

<!-- La recomendacion 4 original (nota de trazabilidad del conteo bibliografico) queda retirada: no hay discrepancia de conteo que trazar. Vease la fe de errata en la seccion 9. -->

---

## CONSIDERACION FINAL

La version v1.0.1 cierra el ciclo de correcciones de forma satisfactoria. Las siete recomendaciones del dictamen anterior fueron incorporadas: las tres de mayor peso con precision textual demostrable; las cuatro de alcance menor con cumplimiento sustancial. El documento es verificable en su version de referencia (tag v1.0.1, hash `bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0`), internamente consistente, y demuestra una integridad academica que es infrecuente para el nivel de una tecnicatura: declara sus limitaciones con exactitud, distingue entre lo medido y lo no medido, y sostiene sus resultados con contrastes estadisticos apropiados.

Las observaciones que permanecen son de forma editorial y no comprometen el argumento central ni los aportes del trabajo. El trabajo esta en condiciones de ser sometido a defensa oral. **Se recomienda su aprobacion sin condiciones.**
