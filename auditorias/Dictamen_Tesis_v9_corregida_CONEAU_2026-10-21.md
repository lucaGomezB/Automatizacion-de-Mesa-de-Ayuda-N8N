# DICTAMEN DE EVALUACIÓN ACADÉMICA

**Documento evaluado:** *Automatización inteligente del registro de incidentes en mesas de ayuda empresariales mediante orquestación de flujos con N8N y procesamiento de lenguaje natural basado en modelos de lenguaje grandes*. Trabajo Final de Carrera, Tecnicatura Universitaria en Programación, UTN Facultad Regional Mendoza. Versión v9 corregida, `docs/Tesis/v9 (IA)/paper/main.pdf`, 101 páginas. Autores: Gomez, Bustos y Sevilla.

**Fecha del dictamen:** 2026-10-21.

**Alcance del examen:** cuerpo completo (capítulos 1 a 12, referencias y anexos A–I), archivo de bibliografía y artefactos de compilación. Se verificó la correspondencia citas↔referencias, la resolución de los DOI, la existencia de figuras y tablas, la coherencia numérica interna y la reproducibilidad de los cálculos. No se re-ejecutó el sistema.

**Nivel de exigencia:** criterios de evaluación universitaria argentina (CONEAU) calibrados al nivel de una tecnicatura.

---

## VEREDICTO GENERAL

**APROBADO.**

El trabajo acredita una madurez metodológica y una honestidad intelectual infrecuentes para el nivel. La evaluación fue realizada sobre una versión que **corrigió las inconsistencias que un dictamen previo había señalado como bloqueantes**: la contradicción entre la tabla de calibración y la tasa de intervención humana, la ambigüedad del paradigma métrico, el criterio del universo, la fundamentación de conceptos, la acotación de la vacancia y los defectos formales. La tesis declara con transparencia que **no alcanzó el umbral de exactitud del 85 %**, gesto que la honra, y sostiene el resultado central (la reducción del tiempo de registro) con un contraste no paramétrico correctamente reportado. El dictamen previo condicionaba la aprobación a que las cifras cerraran; hoy cierran.

---

## OBSERVACIONES POR DIMENSIÓN

### 1. Estructura general del documento

**Cumple.** La arquitectura es la esperable y está completa: portada, resumen en español y abstract en inglés, índice general, de tablas y de figuras, glosario de 64 siglas, capítulos 1–12, referencias y anexos A–I. La progresión es lógica. Las remisiones cruzadas usan `\autoref`/`\ref` de forma consistente (cero remisiones duras, cero referencias indefinidas). El capítulo legal fue **reubicado antes de Resultados**, lo que resuelve su condición de apéndice encubierto. Los defectos formales detectados (una tabla que imprimía el literal "aggedright", una celda con corchete sin cerrar, una remisión hardcodeada a un número de tabla equivocado, el rótulo "Appendices" en inglés y una mención residual a Redis) fueron **corregidos**. Observación menor: el capítulo legal contiene dos secciones de nivel superior, lo que incrementa en uno la numeración de los capítulos siguientes (detalle cosmético, no de fondo).

### 2. Claridad y formulación de la hipótesis

**Cumple.** Es explícita, cuantificada y falsable, y está **desdoblada en tres sub-hipótesis contrastables**, cada una con su contraste y su criterio de falsación: tiempo (confirmada: W=363, p=3,08×10⁻³², r=0,9639), intervención humana (declarada **no medida**) y exactitud/F1 (refutada: 73,5 %, IC Wilson [67,0 %; 79,1 %]). El estado se declara por sub-hipótesis en resumen, discusión y conclusiones. Reserva: la sub-hipótesis de intervención se formula y luego se deja sin resolver; conviene rotularla explícitamente como "no contrastada por ausencia de registro primario" para que no se lea como una laguna.

### 3. Definición y coherencia de los objetivos

**Cumple.** Un objetivo general (evaluar viabilidad y desempeño) y seis específicos, medibles y alineados con la hipótesis. El acierto central es haber **separado el umbral de desempeño del segundo objetivo**, declarándolo criterio de éxito contingente verificado contra el valor observado y su intervalo de confianza. La tabla de cumplimiento en las conclusiones sintetiza objetivo, grado de cumplimiento y evidencia, con el objetivo 2 marcado como **no alcanzado**. Observación: la justificación del umbral del 85 % descansa, en uno de sus tres criterios, en mediciones organizacionales preliminares sin fuente citada.

### 4. Estado del arte

**Cumple.** La literatura es actual, pertinente y verificable. Se describe un **protocolo de revisión** (seis bases, cadenas de búsqueda, criterios de inclusión/exclusión, fecha de corte 21-10-2026) con bitácora versionada. La **afirmación de vacancia está acotada al alcance revisado** ("en las fuentes consultadas hasta la fecha de corte... no se identificó artículo arbitrado 2023-2026 que evalúe Gemini sobre tickets en español"), eliminando la inexistencia absoluta. Se incorporó una **tabla comparativa de trabajos académicos** (trabajo, enfoque, corpus/idioma, métrica, condición), con celdas honestamente marcadas como "no reportado en el alcance revisado" cuando el dato no pudo establecerse. Observación: las afirmaciones sobre plataformas comerciales se apoyan en documentación pública con fecha de consulta, **no en referencias bibliográficas formales**, por lo que no son académicamente citables.

### 5. Marco teórico

**Cumple.** Ocho ejes, cada uno desembocando en una decisión de diseño verificable. El concepto de **human-in-the-loop se define con fuentes** y con grados de autonomía, aterrizando en el gate del sistema. Los conceptos que antes eran aserciones sin respaldo (**BPA**, **iPaaS**, **alucinación**, **calibración**) ahora están fundamentados o glosados con cita. El eje de reconocimiento automático del habla está **explícitamente acotado** como marco conceptual, aclarando que la transcripción la provee un servicio externo. Observación: el eje de ASR ocupa espacio para un componente no implementado; su extensión podría recortarse.

### 6. Desarrollo metodológico y propuesta

**Cumple.** Diseño cuasiexperimental de muestras pareadas sobre los mismos 200 casos, con documentación poco habitual: doble etiquetado con kappa (0,87, Landis & Koch), Shapiro-Wilk para justificar la prueba no paramétrica, Wilcoxon con tamaño del efecto rank-biserial, intervalos de Wilson y bootstrap percentil, análisis de sensibilidad y cuatro amenazas a la validez tratadas una por una. El **criterio de fijación del tamaño muestral** se declara con honestidad: 200 casos fijados por **disponibilidad operativa**, con el margen del 6,66 % como precisión implicada (no como calibración a priori). La **dependencia entre etiquetadores y operadores** se declara como limitación, no se oculta. Reservas: el kappa se reporta sin intervalo de confianza (registros no conservados); el cronometraje manual usa redondeo al alza, sesgo que infla la línea base.

### 7. Conclusiones (y coherencia con resultados)

**Cumple.** Las conclusiones responden a los objetivos y a la hipótesis: el objetivo general se declara cumplido, el segundo no alcanzado, y el estado de la hipótesis se declara por sub-hipótesis. Los números son internamente consistentes con el reporte de evaluación (reducción del 71,2 %, W=363, exactitud 73,5 %, macro-F1 0,5207 sobre cinco clases y 0,6508 sobre las cuatro estimables). Se incorporó un **marco métrico unificado** que declara la referencia multietiqueta (107/200) y advierte que el micro-F1 no es equivalente de la exactitud. La sección de intervención humana es honesta: declara que el gate **derivó cero casos** y que la proporción por caso **no se midió**. Observación: esa subsección conserva el título "Reducción de la intervención humana" y no entrega un resultado, lo que puede inducir a error; conviene retitularla.

### 8. Propuestas de trabajos futuros

**Cumple.** Las líneas están ancladas en las limitaciones y en el análisis de errores, y hay una **priorización explícita**: primero las que atacan los defectos medidos (calibración del gate, clasificador supervisado, corrección de la medición de intervención), luego las extensiones funcionales. Observación: el umbral de "5.000 casos" para migrar a un clasificador propio aparece repetido y **declarado como valor indicativo, no derivado del corpus**; se recomienda justificarlo o degradarlo a referencia de orden de magnitud.

### 9. Bibliografía

**Cumple.** 54 entradas, con correspondencia perfecta: cero citas huérfanas y cero entradas sin usar (verificado programáticamente). Los identificadores DOI resuelven a publicaciones reales; la distribución temporal es adecuada. El **tipado de las entradas preprint/borrador** (`Touvron2023` como `@misc` de arXiv; `Jurafsky2023` como `@unpublished`) es correcto y declara su condición no publicada. Observación: las afirmaciones sobre productos y precios comerciales (plataformas, DigitalOcean, Vertex AI) se citan a URLs en notas al pie, **sin entrada bibliográfica formal**.

---

## RECOMENDACIONES CONCRETAS

1. **Rotular la sub-hipótesis de intervención humana** como "no contrastada por ausencia de registro primario", y **retitular** la sección homónima para que no prometa un resultado que no entrega.
2. **Incorporar referencias formales** (o reformular como observación propia) para las afirmaciones sobre plataformas comerciales y precios.
3. **Reportar un intervalo de confianza del kappa** si se recupera la tabla de doble etiquetado; en su defecto, mantener la declaración de no computabilidad.
4. **Justificar o degradar el umbral de 5.000 casos** a una referencia indicativa explícita.
5. **Recortar el eje de ASR** al mínimo conceptual necesario, dado que no integra la implementación.
6. **Corregir el detalle estructural menor** del capítulo legal (dos secciones de nivel superior) si se desea una numeración limpia, y revisar los comentarios internos de numeración de los archivos.
7. **Declarar la fuente** de la justificación del umbral del 85 % que hoy se apoya en mediciones organizacionales preliminares.

---

## CONSIDERACIÓN FINAL

Estamos ante un trabajo que demuestra competencia técnica real y una integridad académica destacable: declara el incumplimiento de su propio umbral en lugar de maquillarlo, reconoce la dependencia entre etiquetadores y operadores, y somete sus resultados a un análisis de sensibilidad que acota su propio hallazgo. La corrección de las inconsistencias internas que un dictamen previo había señalado como condicionantes —reconciliar la tabla de calibración con la tasa de intervención, definir el paradigma métrico, fundamentar el universo y los conceptos teóricos— vuelve al capítulo 7 verificable y al trabajo defendible. Las observaciones que quedan son de forma y de completitud, no comprometen el aporte central, y son abordables antes de la defensa. **Se recomienda su aprobación.**
