# DICTAMEN DE EVALUACIÓN ACADÉMICA

**Documento evaluado:** *Automatización inteligente del registro de incidentes en mesas de ayuda empresariales mediante orquestación de flujos con N8N y procesamiento de lenguaje natural basado en modelos de lenguaje grandes*. Trabajo Final de Carrera, Tecnicatura Universitaria en Programación, Universidad Tecnológica Nacional, Facultad Regional Mendoza. Autores: Luca Gomez, Carla Bustos y Gonzalo Sevilla. Directores: Prof. Alberto Cortez y Prof. Ariel Enferrel.

**Versión examinada:** versión de trabajo v10, release `v1.2.12` (tag anotado sobre el commit `7937efd063955f787a4fed6c10168b4744de8905`, del 9 de noviembre de 2026, 01:04 −03), según las fuentes LaTeX de `docs/Tesis/v10 (IA)/paper/sections/`, su compilación `paper/main.pdf` (118 páginas: 7 preliminares, 93 de cuerpo, 4 de referencias y 14 de anexos) y la bibliografía `Bibliography_base.bib` (91 entradas). Entre el tag y la cabeza de la rama `change/c-188-residuales-dictamen-v1-2-10` (`6338a9d`) las fuentes de la tesis solo difieren en la línea que consigna el hash en el Anexo B, como el propio anexo promete.

**Fecha del dictamen:** 9 de noviembre de 2026.

**Alcance del examen:** lectura íntegra y de novo del documento (resumen bilingüe, glosario, secciones 1 a 11 y anexos A a I); recómputo independiente, en Python puro, de todas las cifras de la sección 8 y de sus propagaciones, desde el corpus, la evidencia congelada y los artefactos de la campaña complementaria; cruce de la variable de la segunda sub-hipótesis con el export de intervenciones, los sidecars por canal y el doble etiquetado nuevo; seguimiento de cada observación y recomendación del dictamen del 8 de noviembre de 2026; cotejo de figuras, pines de dependencias, rutas, registro de compilación y PDF del tag; verificación bibliográfica externa de las entradas nuevas y de los DOI.

**Antecedentes:** séptimo dictamen de la serie iniciada el 20 de octubre de 2026. El anterior, sobre `v1.2.10`, emitió cinco observaciones de fondo (A1 a A5), siete de consistencia (B1 a B7), cinco de bibliografía y forma (C1 a C5) y un inventario de 36 correcciones puntuales, con una calificación del documento escrito de 8,48. Los autores las atendieron en dos changes (c-187, release `v1.2.11`; c-188, release `v1.2.12`), con un registro de correcciones que vincula cada observación con archivo y línea y un verificador automático que este dictamen ejecutó sin fallas (127 filas).

**Nivel de exigencia:** criterios de evaluación universitaria argentina (CONEAU), calibrados al nivel de un trabajo final de tecnicatura.

---

## VEREDICTO GENERAL

**APROBADO CON OBSERVACIONES.**

La versión examinada resuelve las cinco observaciones de fondo del dictamen anterior, y lo hace con la mejor respuesta posible: escribiendo lo que los artefactos muestran. La sección 8.3 distingue ahora la derivación por confianza (ningún caso) de la derivación por reportante no identificado (147 casos: todos los de correo y telefonía, ninguno del formulario web) y retira la lectura de la tasa bruta del 73,5 % como medida de la hipótesis. Las secciones 4.2, 4.5, 8.7 y 9.1 declaran que el contrabalanceo planificado no se ejecutó y retiran el contraste entre grupos. Los dos kappa conviven en el resumen con su naturaleza, la discusión incorpora una octava limitación sobre la fiabilidad de la referencia y la sección 4.4 consigna que uno de los analistas originales es autor. La exactitud del brazo manual se expresa por derivación (125 de 151). El PDF del tag ya no imprime el hash de otra release, la imagen derivada de N8N está declarada y la Tabla 19 identifica las revisiones de la campaña complementaria. La aritmética resiste íntegra una nueva verificación independiente: más de cien cifras recomputadas coinciden, sin un solo número con dos valores en lugares distintos del documento.

El veredicto se mantiene con observaciones por tres razones nuevas, ninguna de las cuales exige mediciones de campo.

1. **El veredicto "no concluyente" de la segunda sub-hipótesis depende de un denominador que incluye casos que nadie revisó.** La tesis mide la proporción de casos que requieren acción manual como 25 cambios de derivación sobre 200 casos (12,5 %; IC de Wilson [8,6 %; 17,8 %]) y, como el límite superior supera 0,15, declara la sub-hipótesis no concluyente. Pero los 25 cambios provienen exclusivamente de los 147 casos que se revisaron (14 telefónicos y 11 de correo). Los 53 casos del formulario web no pasaron por revisión humana y entran en el denominador como "sin acción manual" cuando, en rigor, no tuvieron oportunidad de recibirla: con la caché evaluada, 10 de esos 53 están mal derivados frente a la referencia original y 7 de 40 frente al consenso nuevo. Sobre los casos efectivamente revisados, la proporción es 25 de 147 (17,0 %; IC [11,8 %; 23,9 %]) y, con la regla de tres vías que el propio documento declara, la sub-hipótesis resulta **refutada**. También resulta refutada si la necesidad de acción se mide como error del clasificador frente al consenso nuevo (28 de 138; 20,3 %; IC [14,4 %; 27,8 %]) o frente a la referencia original (53 de 200; 26,5 %). El 25/200 es el único denominador que produce "no concluyente". Se agrega que la calidad de las revisiones no se coteja con la referencia: de las 122 confirmaciones con consenso disponible en 85 casos, 11 confirmaron un sector que el consenso considera incorrecto, y de los 25 cambios solo 13 tienen consenso (9 corrigieron, 1 empeoró y 3 pasaron de un error a otro). La lectura honesta es que esta campaña no permite medir la variable de la sub-hipótesis en las condiciones que la hipótesis supone; el documento ya lo dice para la tasa bruta y debe decirlo también para el 12,5 %.

2. **La protección contra el efecto Hawthorne que declara la sección 4.2 es incompatible con lo que la sección 4.4 consigna ahora sobre los operadores.** La sección 4.2 afirma que a los dos operadores del brazo manual de la campaña 2026-10 "no se anunciaron … el propósito comparativo del estudio", que se les informó al concluir en una sesión de esclarecimiento, y la sección 7.5 describe esa sesión. Las secciones 4.4, 4.8 y 9.3 establecen, tras la corrección de c-187, que esos operadores son los mismos dos analistas que fijaron la referencia y que uno de ellos es autor del trabajo. Un autor no puede ignorar el propósito comparativo de su propia tesis ni ser informado de él en un *debriefing*. El texto corrigió la independencia del analista y no propagó la consecuencia al operador cronometrado: para la mitad del brazo manual del contraste principal de tiempos, el enmascaramiento declarado no existió. La corrección es de redacción, pero toca la validez interna del resultado central y la descripción ética del procedimiento.

3. **La Tabla 19 afirma una equivalencia de código que el repositorio desmiente.** La nota al pie sostiene que, entre la revisión de la campaña complementaria (`cda7712`) y la entregada (`v1.2.12`), "solo `docker-compose.yml` difiere". El `git diff --stat cda7712 v1.2.12` sobre `App/`, `n8n/`, `docker/` y `docker-compose.yml` muestra 24 archivos modificados (entre ellos `App/Backend/app/cost_guard/twiml.py`, la ruta de control de costo, cinco pruebas del backend y trece archivos del frontend). Lo que sí es cierto, y es lo que la tabla necesita, es que los archivos de pines (`requirements.txt`, `package-lock.json`, `n8n/workflow.json`, `settings.py`) no cambian. La frase debe acotarse a esos archivos.

Persisten, declaradas con precisión y sin computarse como incumplimiento, las limitaciones estructurales del diseño: métricas de clasificación dentro de la muestra, validación fuera de muestra no realizada, tiempos automatizados de configuraciones anteriores a la evaluada, exactitud estricta (73,5 %) con intervalo íntegramente inferior al umbral del 85 %, efecto de orden no estimado y balance operativo condicional al costo no cronometrado de las reasignaciones.

---

## OBSERVACIONES DETALLADAS POR SECCIÓN

### 1. Estructura general del documento

**Cumple.** La organización es la canónica de un trabajo de investigación aplicada: resumen bilingüe, glosario de 81 siglas sin entradas sobrantes, once secciones, referencias y nueve anexos. Las remisiones cruzadas resuelven todas (143 etiquetas; ninguna referencia sin destino); las 10 figuras y 23 tablas están citadas y numeradas en forma consecutiva; la matriz de confusión ya no se duplica; el PDF no contiene "??" ni caracteres rotos, y la compilación local registra cero errores y cero referencias indefinidas.

Defectos de forma. El documento tiene 118 páginas frente al tope total de 100 que el propio equipo fijó; el cuerpo sí queda en 93. La sección 9.3 anuncia "siete limitaciones" y enumera ocho, porque la octava se agregó en c-187 sin actualizar la frase de apertura. La portada fecha el documento el 8 de noviembre y la release es del 9. El glosario cubre lo que se pidió, pero quedan siglas del cuerpo sin definir: TI (tres usos, con IT en el glosario), URL, E2E, MDE, VIS (en "VIS-005", 8.3), HS256 y CA, además de las abreviaturas de métodos de la Tabla 1 (NB, LR, DT). La sección 8.3 contiene un anacoluto introducido en c-187 ("se estima con una cobertura … de 0,9388 (…), la proporción del tiempo es de 0,5307"). La celda del cuarto objetivo en la Tabla 18 repite "exactitud del brazo manual" en dos cláusulas consecutivas.

### 2. Claridad y formulación de la hipótesis

**Cumple parcialmente.** La formulación sigue siendo la mejor de la serie: hipótesis principal desdoblada en tres sub-hipótesis contrastables, con estadístico, hipótesis nula sobre las diferencias pareadas, regla de decisión de tres vías para la segunda y criterio de falsación; dos subsidiarias rotuladas como no contrastadas. Los estados son ahora coherentes en el resumen, la sección 1.4, la 9.1 (que ya incluye la segunda sub-hipótesis), la Tabla 18 y el capítulo 10.

La objeción de fondo es la observación 1 del veredicto. El documento corrigió correctamente la lectura de la tasa bruta, pero reemplazó una variable inadecuada por otra cuyo veredicto depende de contar como "sin acción manual" a 53 casos que no pudieron recibirla. Con los datos disponibles, la segunda sub-hipótesis o se declara no contrastable en esta campaña (por la regla del reportante, que fijó qué casos se revisaban) o se informa con el denominador de los casos revisados, y entonces resulta refutada según la regla declarada. En cualquiera de las dos lecturas, "no concluyente" con 25/200 no se sostiene como conclusión.

### 3. Definición y coherencia de los objetivos

**Cumple.** El objetivo general y los seis específicos están bien delimitados y la Tabla 18 cierra la matriz objetivo-evidencia-conclusión con grados honestos (uno no alcanzado, cinco parcialmente y uno alcanzado). El cuarto objetivo pasó a "alcanzado parcialmente", limitado a tiempo y exactitud del brazo manual, como correspondía.

Dos reparos menores. La justificación académica (1.6) sigue anunciando una "validación rigurosa" con "doble etiquetado independiente", cuando el propio documento declara ahora que la validación es dentro de la muestra, que uno de los analistas originales es autor y que el doble etiquetado independiente produjo un acuerdo moderado. La fila del primer objetivo sigue citando los reintentos idempotentes sin la calificación explícita de "configuración entregada" que el cuerpo sí usa.

### 4. Estado del arte

**Cumple.** Protocolo de revisión con seis bases, siete cadenas, dos fechas de corte y bitácora versionada; siete trabajos sistematizados con métrica y condición; literatura de calibración y cascadas; brecha acotada "al alcance revisado". Las correcciones pedidas están hechas: la atención menor al rioplatense se rotula como inferencia de los autores, la Tabla 1 ya no califica a Zangari de inaccesible y describe a Ramya como compañero accesible de dos de los tres autores, y la Tabla 2 cita con fuente las cinco plataformas. Persiste la ausencia de búsquedas en repositorios regionales (SciELO, Redalyc, JAIIO), que habrían reforzado la brecha declarada para la literatura argentina.

### 5. Marco teórico

**Cumple.** Ocho ejes que desembocan en decisiones de diseño verificables. Las imprecisiones señaladas están resueltas: Galup et al. sostiene solo la caracterización de ITSM y la degradación con el volumen se declara inferencia de los autores; la definición del F1 macro distingue las dos fórmulas con Opitz y Burst; el efecto Hawthorne se apoya en una revisión sistemática. Las secciones 2.4 y 5.5 mantienen "posterior a las corridas de la campaña" para fechar la regla del reportante; ahí "la campaña" designa la de 2026-10, pero la campaña complementaria corrió con esa regla activa, y es precisamente la ambigüedad que motivó la observación de fondo anterior.

### 6. Desarrollo metodológico y propuesta (método, arquitectura, implementación y resultados)

**Cumple parcialmente.** Concentra las fortalezas y las tres observaciones del veredicto.

*Fortalezas.* La procedencia de las tres corridas del brazo automatizado, la tabla de configuraciones con tres columnas verificadas, el orden efectivamente ejecutado de la campaña complementaria, la naturaleza de cada kappa, el mecanismo de derivación por canal y las unidades de la exactitud manual están ahora declarados con una precisión que excede la del nivel. La arquitectura, el modelo de datos, el contrato REST (33 rutas, 41 métodos, 44 esquemas) y el flujo N8N (32 nodos) coinciden con el tag. Las figuras regeneradas coinciden con el texto, incluido el despliegue con el bundle servido por `nginx:alpine` y la imagen derivada de N8N.

*Observaciones de método.* (a) Segunda sub-hipótesis: observación 1. (b) Enmascaramiento de los operadores: observación 2. (c) La proporción del tiempo de intervención (0,5307) usa como denominador los tiempos automatizados de la campaña complementaria (`corpus_campana.json`; 2692,22 s sobre 191 casos), no los del corpus de octubre (3283,40 s, que darían 0,4811); el texto no dice cuál usa. (d) La "salida en vivo" telefónica con que se comparan las predicciones de la campaña no proviene de los sidecars, que tienen el sector nulo en los 81 casos, sino de la columna `sector_predicho` del export de intervenciones; conviene declararlo. (e) La exactitud laxa del brazo manual (130 de 151) solo se reproduce si el conjunto de verdad laxo es el consenso más la unión de los sectores adicionales de ambos etiquetadores; con los adicionales del corpus original da 128. La definición no figura. (f) El efecto mínimo detectable del Spearman (ρ = 0,2834) no se reproduce con la fórmula documentada en `evaluation/campana.py` (tanh del efecto mínimo de Fisher con n − 3 = 107, α = 0,05, potencia 0,80), que da 0,264; no altera ninguna conclusión. (g) La sección 4.5 sigue diciendo que la campaña complementaria corrió "con el clasificador congelado en la configuración evaluada, de modo que sus métricas de clasificación son comparables"; la sección 8.7 ya reconoce que la salida en vivo difiere de la caché en 13 casos y que el backend tenía activa la regla del reportante; la frase de 4.5 debe matizarse en el mismo sentido.

*Observaciones de implementación y trazabilidad.* La observación 3 del veredicto. Además, el canal telefónico tiene ahora dos descripciones incompatibles: la sección 6.4 dice, correctamente, que Twilio notifica la grabación al backend y que este la transcribe con la Gemini API; la sección 5.2 sigue diciendo que la grabación "es transcrita automáticamente por el servicio de reconocimiento del habla del proveedor y enviada al flujo N8N mediante webhook", y la etapa 4 de la sección 6.6 habla de "el webhook de transcripción". El modelo de transcripción (`gemini-3.5-transcribe` en `settings.py` del tag) no se declara en ningún lugar, cuando el de clasificación se declara con todos sus parámetros; tampoco se declara su costo, que el cálculo económico de 9.5 excluye expresamente. El diagrama de despliegue muestra la Gemini API solo para la clasificación, y su leyenda conserva "red Docker" en singular frente a las cuatro redes que la figura dibuja. Los PNG de componentes y secuencia conservan "posterior a la campaña de medición" y "posterior a la campaña" dentro de la imagen; el registro de correcciones afirma que esos rótulos estaban solo en las leyendas, lo que no es exacto para estas dos figuras. La figura `matriz_confusion.pdf` quedó en el directorio sin uso.

### 7. Conclusiones

**Cumple, con observaciones.** El capítulo responde a cada objetivo y sub-hipótesis, incorpora el kappa moderado, el efecto de posición significativo para un operador, el calificativo "dentro de la muestra" y una conclusión del cuarto objetivo acotada a lo medido. Es, otra vez, el capítulo con mejor relación entre lo que afirma y lo que la evidencia sostiene. Hereda la observación 1: el estado "no concluyente" de la intervención humana figura en el párrafo inicial, en la Tabla 18 (objetivo general y cuarto objetivo) y en la síntesis del cuarto objetivo, y debe propagarse la corrección que se adopte. El resumen y el *abstract* ("los hallazgos confirman la viabilidad técnica y económica") son más afirmativos que el capítulo, que la declara para métricas dentro de la muestra; "respaldan" sería más fiel.

### 8. Propuestas de trabajos futuros

**Cumple.** Las líneas están priorizadas y las prioritarias atacan defectos medidos. La sección 11.3 se reescribió como se pidió: la tasa bruta deja de leerse como defecto del clasificador y la nueva medición se condiciona a reportantes identificados. Conviene agregar a esa línea dos requisitos que la observación 1 muestra necesarios: que la revisión alcance a todos los canales (o a una muestra aleatoria de cada uno), para que el denominador sea el de los casos revisables, y que cada validación se coteje con una referencia independiente, para medir no solo cuántas veces cambia la derivación sino cuántas veces la revisión acierta. La cifra de 5.000 casos figura ahora una sola vez.

### 9. Bibliografía

**Cumple, con observaciones.** Las 91 entradas son reales y ninguna resultó inventada. Los 49 DOI resuelven en Crossref al trabajo citado. Cada clave citada tiene su entrada y viceversa, no hay duplicados, y biber no registra avisos. Las diez entradas incorporadas en c-188 existen y sus títulos coinciden con la página o el registro citados. El estilo es APA 7 con `biblatex-apa`, coherente. Las inconsistencias de forma señaladas en el dictamen anterior están corregidas: actas de EMNLP con año, PMLR como revista con volumen, mayúscula tras los dos puntos, "3.ª", "Publicación anticipada en línea" y "Gomez". La actualidad es adecuada: 43 de las 91 entradas son de 2022 en adelante. Hay 47 fuentes arbitradas y 12 libros, frente a 17 de documentación técnica o páginas comerciales y 7 legales.

Reparos de fidelidad. La sección 2.4 atribuye a Zanzotto (2019) que el diseño debe reservar a la persona un rol activo "ante la ambigüedad semántica y la responsabilidad sobre las consecuencias". El resumen del artículo trata otra cosa: propone el paradigma *HitAI* para retribuir a quienes producen el conocimiento que usan los sistemas. No se pudo leer el texto completo, de modo que la atribución debe reformularse o apoyarse en la página exacta. La "baja discriminación" de aciertos y errores que 2.5 y 9.2 atribuyen a Xiong et al. (2024) es más fuerte que la fuente, que dice que predecir las fallas sigue siendo un desafío. La sobreconfianza y la concentración en la parte alta de la escala sí están respaldadas. La sección 2.1 todavía atribuye a Galup et al. (2009) la noción de la mesa de ayuda como punto único de contacto, que es propia de ITIL y no pudo verificarse en Galup. Conviene citarla con `OGC2011_itil`.

Reparos de pertinencia. El cálculo económico de 9.5 cita la página de precios de Vertex AI, pero el backend usa la Gemini API. Los precios de `gemini-3.6-flash` son idénticos en ambas páginas, así que el cálculo no cambia, pero la fuente debe ser la del servicio usado. Esa misma página de la Gemini API dice que en el nivel gratuito los datos se usan para mejorar los productos de Google, y en el pago no. El capítulo 7 debe decir en qué nivel operó el sistema, porque eso cambia el tratamiento de los datos transferidos. La URL de `Zendesk2026_help_desk` lleva hoy a una nota comparativa de tipo blog y no a la ficha de Zendesk Suite. La de `Google2026_vertex_pricing` redirige a una página con otro título. La URL de infoleg del Decreto 1558/2001 no respondió, y la de argentina.gob.ar sí.

Reparos de forma. La entrada de Ramya et al. cita el preprint de arXiv, cuando existe la versión arbitrada en IEEE (CSITSS 2018, pp. 221-227), que conviene citar con su DOI. A Kerby (2014) le corresponde el localizador 3:11.IT.3.1 y no "Article 1". La entrada de Efron y Tibshirani mezcla el año de la edición original de 1993 con el DOI de la reedición de 1994. La publicación de FrugalGPT en TMLR no pudo confirmarse. A diez de los doce libros les falta el ISBN, aunque APA 7 no lo exige.

---

## TABLA RESUMEN DE CUMPLIMIENTO

| Dimensión | Dictamen v1.2.10 (8-11-2026) | Presente dictamen (v1.2.12) |
|---|---|---|
| 1. Estructura general | Cumple (defectos de forma) | Cumple (defectos de forma: páginas, "siete limitaciones", glosario residual, anacoluto) |
| 2. Hipótesis | Cumple parcialmente | Cumple parcialmente (el "no concluyente" depende del denominador) |
| 3. Objetivos | Cumple | Cumple |
| 4. Estado del arte | Cumple | Cumple |
| 5. Marco teórico | Cumple | Cumple |
| 6. Metodología y propuesta | Cumple parcialmente | Cumple parcialmente (denominador de la sub-hipótesis 2; operador autor sin enmascaramiento; nota de la Tabla 19; canal telefónico descrito de dos maneras) |
| 7. Conclusiones | Cumple, con observaciones | Cumple, con observaciones (hereda la sub-hipótesis 2) |
| 8. Trabajos futuros | Cumple | Cumple |
| 9. Bibliografía | Cumple, con observaciones de forma | Cumple, con observaciones (Zanzotto, Xiong, Galup; fuente de precios; nivel de la Gemini API) |

Las dimensiones 2 y 6 permanecen en "cumple parcialmente", pero con observaciones de menor alcance que las del dictamen anterior: entonces la variable medida no era la de la hipótesis y el contrabalanceo descrito no se había ejecutado; ahora la variable es la adecuada y lo que falla es el denominador, y lo que falta es propagar una corrección ya hecha a un párrafo que la contradice.

---

## SEGUIMIENTO DE LAS OBSERVACIONES DEL DICTAMEN ANTERIOR

| Ítem del 8-11-2026 | Estado | Evidencia en `v1.2.12` |
|---|---|---|
| A1. Mecanismo de derivación y sub-hipótesis 2 | Resuelto, con observación nueva | 8.3 retitulada; derivación por confianza (0) frente a derivación por reportante (147: 66/66, 81/81, 0/53) verificada contra los ocho sidecars; 65,5 % rotulado como cobertura; resumen, 1.4, 9.1, Tabla 18, 10 y 11.3 reformulados. Observación nueva: denominador del 12,5 % (observación 1) |
| A2. Contrabalanceo no ejecutado | Resuelto | 4.2, 4.5, 4.7, 4.8, 8.7, 9.1 y 10; fechas verificadas contra `brazo_manual.csv` y los sidecars; contraste entre grupos retirado del cuerpo; Spearman conservado |
| A3. Kappa moderado e independencia de los analistas | Resuelto, con residuo | Resumen con ambos kappa; 4.4 y 4.8 consignan el analista autor; 9.3 octava limitación con 116/138; 10.2 matizada. Residuo: la consecuencia sobre el enmascaramiento del operador (observación 2) y "doble etiquetado independiente" en 1.6 |
| A4. Denominador del brazo manual | Resuelto | 125/151 y 130/151 con unidades declaradas; `numeros-canonicos.md` corregido; `e_man` y `a*` con la unidad correcta |
| A5. Trazabilidad del tag | Resuelto, con residuo | PDF del tag con la oración de verificación; PDF de la rama con el hash correcto (`git rev-list -n1 v1.2.12` coincide); imagen derivada de N8N en 6.1 y Tabla 19; columna de la campaña completa. Residuo: nota al pie de la Tabla 19 (observación 3); portada del 8-11 frente a release del 9-11 |
| B1. Exactitud automatizada sobre la caché | Resuelto | 8.7 declara el origen y las 13 diferencias; falta decir qué predicción usa el McNemar y de dónde sale la salida en vivo telefónica |
| B2. Fechas, 65,5 %, denominador 191, "únicamente" | Resuelto, con anacoluto nuevo | 8 párrafo inicial, 8.3 y 8.7 |
| B3. Rótulo "campaña de medición" | Parcial | Leyendas, Tabla 5 y Anexo B unificados; persiste dentro de los PNG de componentes y secuencia, y "posterior a las corridas de la campaña" en 2.4, 5.5, 6.3 y 7.5 |
| B4. Métricas multietiqueta y ejemplos del prompt | Resuelto | 4.7, 8.2, 5.5 y 9.4 |
| B5. Capturas, despliegue y matriz duplicada | Resuelto, con residuo | Procedencia en las leyendas (verificada contra las imágenes); despliegue regenerado; Figura 7 retirada. Residuo: leyenda del despliegue sin actualizar; archivo huérfano |
| B6. Conclusiones faltantes y frases | Resuelto (omisión declarada) | Kappa y efecto de posición en 10; "dentro de la muestra"; 5.000 una vez; cota pesimista calificada. El efecto de posición no está en el resumen, por decisión declarada (tope de 250 palabras) |
| B7. Registro de compilación y verificador | Parcial | `compilacion.md` versionado y generado por script probado; verificador con 127 filas y cero fallas (reproducido). El `main.log` sigue ignorado, de modo que las cifras de errores solo se verifican recompilando; la Tabla 23 remite al Anexo B, que no nombra esos artefactos |
| C1. Galup, F1 macro, Hawthorne | Resuelto | 1.2, 2.2, 2.8, 4.2, 4.6 y 3.2 |
| C2. Fuentes de Gemini, Twilio, Docker, Jira, osTicket y art. 12 | Resuelto | Diez entradas nuevas citadas; 6.4 corrige además la atribución de la transcripción. Residuo: 5.2 no se corrigió en el mismo sentido |
| C3. Disociación, Tabla 1 | Resuelto | 9.6 y Tabla 1 |
| C4. Forma bibliográfica | Resuelto | Véase la sección 9 |
| C5. Glosario | Resuelto, con residuos | 81 entradas, todas usadas; faltan TI, URL, E2E, MDE, VIS, HS256, CA |
| Ítems 1 a 36 del inventario | 33 resueltos, 3 parciales | Parciales: 19 (reintentos en la Tabla 18), 26 (rótulos en PNG), 28 (leyenda del despliegue) |

---

## RECOMENDACIONES CONCRETAS Y ACCIONABLES

Las recomendaciones A son de fondo y deben resolverse antes de la defensa; las B, de consistencia interna; las C, de forma. Ninguna exige nuevas mediciones de campo.

**A1. Reformular el estado de la segunda sub-hipótesis según el denominador de los casos revisables** (secciones 1.4, 4.7, 8.3, 9.1, 10, 11.3, Tabla 18, resumen y *abstract*). Declarar que la revisión humana de la campaña complementaria alcanzó solo los canales de correo y telefonía, por la regla del reportante, y que los 53 casos web no tuvieron revisión. Elegir una de dos lecturas y sostenerla en todo el documento: (i) la sub-hipótesis no es contrastable con esta campaña, porque la regla del reportante determinó qué casos se revisaban; o (ii) sobre los casos revisados, 25 de 147 (17,0 %; IC [11,8 %; 23,9 %]) cambiaron la derivación, y con la regla declarada la sub-hipótesis resulta refutada. Informar en 8.3, como dato y sin lectura causal, que de las 85 confirmaciones con consenso nuevo 11 confirmaron un sector que el consenso considera incorrecto, y que de los 25 cambios 13 tienen consenso (9 correcciones, 1 empeoramiento, 3 de error a error).

**A2. Propagar a la descripción del enmascaramiento la condición de autor de uno de los operadores** (secciones 4.2, 4.8, 7.5, 9.1). Si los operadores del brazo manual de la campaña 2026-10 son los dos analistas originales, y uno de ellos es autor, el texto no puede afirmar que a ambos se les ocultó el propósito comparativo ni que ambos lo conocieron en el *debriefing*. Consignar que el enmascaramiento operó, a lo sumo, para uno de los dos operadores, y llevar esa condición a la amenaza del efecto Hawthorne en 4.8 y a la explicación rival de 9.1. Si en cambio los operadores de 2026-10 no son esas personas, corregir 4.4, 4.8 y 9.3, que hoy lo afirman.

**A3. Acotar la nota al pie de la Tabla 19** (`12-anexos.tex:78`). Reemplazar "solo `docker-compose.yml` difiere" por la afirmación verificable: entre `cda7712` y `v1.2.12` no cambian `requirements.txt`, `package-lock.json`, `n8n/workflow.json` ni `settings.py`; sí cambian `docker-compose.yml` (imagen derivada) y archivos del backend (control de costo y TwiML) y del frontend que no intervienen en la clasificación.

**B1.** Unificar la descripción del canal telefónico: corregir 5.2 ("la grabación es transcrita automáticamente por el servicio de reconocimiento del habla del proveedor") y la etapa 4 de 6.6 ("el webhook de transcripción") según 6.4; declarar el modelo de transcripción (`gemini-3.5-transcribe`) en 6.4, en la Tabla 19 y en el Anexo H, y su exclusión del costo en 9.5; agregar la transcripción al diagrama de despliegue y actualizar su leyenda.

**B2.** Declarar en 8.3 que el denominador de la proporción de tiempo usa los tiempos automatizados de la campaña complementaria; declarar en 8.7 que la salida en vivo telefónica proviene del export de intervenciones, qué predicción usa el McNemar, y la definición del conjunto de verdad laxo del brazo manual (consenso más la unión de los adicionales de E1 y E2); corregir o justificar el efecto mínimo detectable del Spearman (0,2834 frente a 0,264 con la fórmula del código).

**B3.** Matizar en 4.5 que la campaña complementaria corrió con `hybrid-v3` pero con la regla del reportante activa y con una salida que difiere de la caché en 13 casos. Reemplazar "posterior a las corridas de la campaña" por "posterior a la campaña 2026-10" en 2.4, 5.5, 6.3 y 7.5, y regenerar los PNG de componentes y secuencia con ese rótulo.

**B4.** En 1.6, reemplazar "validación rigurosa … con doble etiquetado independiente" por una formulación coherente con 4.4 y 9.3; en el resumen y el *abstract*, "respaldan" en lugar de "confirman"; en la fila del primer objetivo de la Tabla 18, "reintentos idempotentes de la configuración entregada".

**C1.** Corregir "siete limitaciones" por "ocho" en 9.3; resolver el anacoluto de 8.3; quitar la repetición de la celda del cuarto objetivo; completar el glosario (TI, URL, E2E, MDE, VIS, HS256, CA) o desarrollar las siglas en su primer uso; fechar la portada el día de la release; retirar `matriz_confusion.pdf` del directorio de figuras; nombrar en el Anexo B el resumen de compilación y el verificador que la Tabla 23 le atribuye.

**C2.** Reformular o paginar la atribución a Zanzotto (2.4); atenuar la "baja discriminación" atribuida a Xiong et al. (2.5 y 9.2); citar el punto único de contacto con ITIL y no con Galup (2.1); citar la página de precios de la Gemini API en 9.5 y declarar en el capítulo 7 el nivel de servicio (gratuito o pago), con su consecuencia sobre el uso de los datos; reemplazar las URL de Zendesk, Vertex y del Decreto 1558/2001; citar la versión IEEE de Ramya et al.; corregir los localizadores de Kerby y la edición de Efron y Tibshirani.

---

## CONSIDERACIÓN FINAL

Entre el dictamen anterior y este, los autores hicieron lo que se les pidió y algo más: verificaron cada observación contra el código y los artefactos antes de corregirla, registraron dónde el dictamen o su propio diseño se equivocaban, y dejaron un verificador automático que convierte el seguimiento de las correcciones en una prueba reproducible. Las cinco observaciones de fondo están resueltas con redacción veraz, y la versión es la más sólida de la serie.

Las tres observaciones nuevas tienen un origen común: una corrección bien hecha en un lugar que no se propagó a todas sus consecuencias. La regla del reportante se reconoció como causa de la tasa bruta, pero no como causa de que un cuarto del corpus quedara fuera del denominador de la tasa corregida. Uno de los analistas se reconoció como autor, pero no se advirtió que, por eso mismo, uno de los operadores cronometrados conocía el propósito del estudio. La campaña se ubicó en sus revisiones, pero la nota que compara esas revisiones con la entregada dice más de lo que el repositorio sostiene. Son correcciones de una sesión de edición con el repositorio al lado, y el equipo ha demostrado en cada versión que sabe hacerlas.

---

## CALIFICACIÓN SUGERIDA SEGÚN LA RÚBRICA DE LA CÁTEDRA

Se aplica la *Rúbrica de Evaluación de Tesis de Ingeniería* (`Rúbrica.docx`), con las advertencias de los dictámenes anteriores: las ponderaciones suman 115 % y no 100 %, de modo que el promedio se calcula sobre la suma efectiva de los pesos; el décimo criterio (defensa oral, peso 10) no es evaluable, y la calificación del documento escrito se computa sobre los nueve restantes (peso 105).

| Criterio | Peso | Puntaje | Nivel | Fundamento |
|---|---|---|---|---|
| 1. Definición del problema | 15 | 9 | Excelente | Pregunta neutra, tres sub-hipótesis con estadístico, regla de decisión y criterio de falsación, estados coherentes en todo el documento, 9.1 completa. Descuenta: el estado de la sub-hipótesis 2 depende de un denominador que incluye casos no revisados. |
| 2. Justificación y relevancia | 10 | 9 | Excelente | Tres dimensiones con argumentos verificables y punto de equilibrio reutilizable. Descuenta: "validación rigurosa con doble etiquetado independiente" en 1.6. |
| 3. Marco teórico y revisión bibliográfica | 15 | 9 | Excelente | Ocho ejes con consecuencia en el diseño; Galup, F1 macro y Hawthorne corregidos; fuentes técnicas y normativas incorporadas. Descuenta: sin búsqueda en repositorios regionales; "la campaña" ambiguo en 2.4. |
| 4. Metodología de investigación | 20 | 8,5 | Muy bueno / Excelente | Procedencia completa, orden ejecutado declarado, analista autor consignado, unidades de la exactitud manual corregidas, estadística reproducible. Descuenta: denominador de la sub-hipótesis 2; enmascaramiento de un operador autor; validación fuera de muestra no realizada. |
| 5. Desarrollo técnico o experimental | 15 | 9 | Excelente | Arquitectura, contrato, flujo y pines verificados contra el tag; trazabilidad del tag restaurada; imagen derivada declarada; figuras coherentes. Descuenta: nota falsa de la Tabla 19; canal telefónico descrito de dos maneras; modelo de transcripción no declarado. |
| 6. Resultados y análisis | 10 | 8,5 | Muy bueno / Excelente | Más de cien cifras reproducidas, mecanismo de derivación por canal verificado, unidades correctas. Descuenta: veredicto de la sub-hipótesis 2; denominador de la proporción de tiempo y salida en vivo telefónica sin declarar; exactitud laxa manual sin definición; efecto mínimo detectable no reproducible. |
| 7. Conclusiones y aportes | 10 | 9 | Excelente | Responden a cada objetivo y sub-hipótesis, incorporan kappa moderado y efecto de posición, "dentro de la muestra". Descuenta: hereda el "no concluyente"; resumen más afirmativo que el capítulo. |
| 8. Redacción académica y estructura | 5 | 8,5 | Muy bueno / Excelente | Remisiones correctas, matriz sin duplicar, glosario depurado, procedencia de las capturas declarada. Descuenta: 118 páginas frente al tope del equipo; "siete limitaciones"; anacoluto; siglas residuales. |
| 9. Uso de referencias y normas de citación | 5 | 9 | Excelente | 91 entradas reales; 49 DOI cotejados; correspondencia exacta; forma corregida; fuentes técnicas y normativas incorporadas. Descuenta: atribución a Zanzotto sin respaldo en la fuente; Xiong y Galup forzados; fuente de precios distinta del servicio usado; URL desactualizadas. |
| 10. Defensa oral | 10 | — | No evaluable | Pendiente de la instancia de defensa. |

**Cálculo.** Suma de puntaje por peso sobre los nueve criterios del documento: 9 × 15 + 9 × 10 + 9 × 15 + 8,5 × 20 + 9 × 15 + 8,5 × 10 + 9 × 10 + 8,5 × 5 + 9 × 5 = 927,5. Dividido por el peso efectivo (105): **8,83**.

**Calificación del documento escrito: 9 (nueve), nivel "Excelente" (8,83 ponderado).** Representa una mejora de 0,35 puntos respecto del dictamen anterior (8,48), la mayor de la serie. Recoge que las cinco observaciones de fondo están resueltas. Los criterios 4 y 6 no alcanzan el 9 por las observaciones 1 y 2.

**Proyección de la nota final con defensa oral** (sobre el peso total de 115): con una defensa calificada 7, la nota final resulta 8,67; con 8, 8,76; con 9, 8,85; con 10, 8,93. Con una defensa de 8 o más la nota final redondea a **9**.

**Proyección tras incorporar las recomendaciones A1 a A3 y B1 a B4.** Si se corrige el estado de la segunda sub-hipótesis, se propaga la condición de autor al enmascaramiento y se acota la nota de la Tabla 19, los criterios 4 y 6 pasarían razonablemente a 9 y el 1 a 9,5. Con las correcciones C, los criterios 8 y 9 pasarían a 9 y 9,5. El promedio ponderado del documento sería entonces del orden de 9,1 (955 sobre 105).

---

## VERIFICACIÓN CONTRA EL REPOSITORIO

- **Segunda sub-hipótesis.** `evaluation/data/campana/intervenciones.csv`: 147 filas, todas con origen `gate`, 25 con `cambio_sector` verdadero (14 telefonía, 11 correo, 0 web) y 122 confirmaciones. Cruce con `doble_etiquetado.csv` (consenso E1 = E2 en 138 casos): 85 confirmaciones con consenso, 11 de ellas a un sector distinto del consenso; 13 cambios con consenso (9 correcciones, 1 empeoramiento, 3 de error a error). Casos web: 10 de 53 mal derivados frente a la referencia original con la caché (13 con la salida del sidecar), 7 de 40 frente al consenso (10 con el sidecar). Proporciones e intervalos de Wilson: 25/200 = 0,125 [0,0861; 0,1780]; 25/147 = 0,1701 [0,1179; 0,2390]; 28/138 = 0,2029 [0,1443; 0,2776]; 53/200 = 0,265 [0,2087; 0,3302].
- **Operadores y analistas.** `04-marco-metodologico.tex:16` (operadores sin conocimiento del propósito comparativo; *debriefing*), `:55` (los dos analistas, uno de ellos autor, operaron el brazo manual), `:89`; `11-aspectos-legales.tex:32`; `evaluation/data/campana/registro_sujetos.csv` y README, sección "Sujetos" (`T1` con rol `autor`).
- **Tabla 19.** `git diff --stat cda7712 v1.2.12 -- App/ n8n/ docker/ docker-compose.yml`: 24 archivos, 1323 inserciones y 75 supresiones; sin cambios en `requirements.txt`, `package-lock.json`, `n8n/workflow.json` ni `settings.py`. Imagen derivada: commit `000abeb` (7-11-2026 18:18 −03), posterior al último sidecar automatizado (6-11 22:45 UTC).
- **Hash.** `git rev-list -n1 v1.2.12` = `7937efd…`; PDF del tag con la oración de verificación; PDF de la rama con el hash; `git diff --stat v1.2.12 HEAD -- sections`: un archivo, una línea.
- **Pines.** FastAPI 0.162.0, Uvicorn 0.54.0, SQLAlchemy 2.1.6, `google-genai >=2.33.0,<3`, pytest 9.1.1, pytest-cov 7.1.0, React 19.3.1, Python 3.12-slim, PostgreSQL 15.5-alpine, N8N derivada de 2.11.2 con parche de `@n8n/imap`: coinciden con la Tabla 19. Columna evaluada (`bf5e099`): coincide. `settings.py`: `gemini-3.6-flash`, 0,3, 0,9, 100 tokens, 30 s; `gemini_stt_model = "gemini-3.5-transcribe"` no declarado.
- **Figuras.** `dashboard.png` y `panel_admin.png` coinciden con sus leyendas (145 incidentes, 21-09 a 21-10, 94 en revisión, 64,8 %, rótulo v1.0.0). `despliegue.png` (mismo blob en el tag y en la rama) coincide con `docker-compose.yml` y el `Dockerfile` del frontend. `flujo_n8n.png`: 29 cajas operativas en siete etapas, igual que `workflow.json`. `componentes.png` y `secuencia.png`: rótulos ambiguos dentro de la imagen. `boxplot_tiempos.pdf` reproduce la Tabla 10; `matriz_confusion.pdf` sin uso.
- **Compilación.** `main.log` local: 0 errores, 0 indefinidas, 7 cajas desbordadas (máximo 8,2 pt), 0 caracteres faltantes; `main.blg` sin avisos; `compilacion.md` coincide con el SHA-256 del PDF en el tag y en la rama. El `main.log` sigue excluido del control de versiones.
- **Resumen.** 239 palabras en español y 239 en inglés con el método sobre el `.tex` (el equipo informa 237 con su regla); ambos bajo el tope de 250.

---

## VERIFICACIÓN ARITMÉTICA

Recómputo en Python puro desde `data/corpus_evaluacion_pseudonimizado.json` (SHA-256 `1fd17d7e…`), `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` y `evaluation/data/campana/`. Coinciden con lo declarado:

- Tiempos: medias 61,585 y 17,761 s; medianas 50,0 y 17,471; desvíos 44,896 y 13,516; extremos; reducciones 71,16 % y 65,06 %; Wilcoxon T⁺ = 19.737, T⁻ = W = 363, p = 3,0846 × 10⁻³²; r = 0,96388; d_z = 1,0004; 12 pares no más rápidos, todos de correo; sensibilidad −5/−10 s (56,59 y 51,59; 68,61 % y 65,57 %; p = 1,797 × 10⁻²⁶; r = 0,86826); Tabla 10 completa por canal.
- Clasificación: matriz de confusión celda a celda; exactitud estricta 147/200 [0,6698; 0,7913] y laxa 179/200 [0,8448; 0,9303]; por etapa y por canal con sus intervalos; precisión, sensibilidad y F1 de las cuatro clases estimables; macro-F1 0,65084 y 0,52067; subset accuracy 0,43, Hamming 0,35858, micro-F1 0,66544; 8 casos con sectores adicionales, todos determinísticos; 124 casos bajo 0,70, todos determinísticos; Tabla 13; 46 casos ≥ 0,90 con 13 errores; Tabla 15 (14/12/11/16 con 5/10/8/9 aciertos laxos); R001, R032 y R015 literales.
- Economía: Δt = 43,8244 s; 32,2 h-persona; las doce celdas de a* y de B de la Tabla 16; 304 derivaciones; 50,7 a 76,1 h; e_man = 0,1722; a* = 68,2/75,5/77,9 %; costo por invocación 7,1 × 10⁻⁴ USD; costo trimestral 0,65 USD (1,30 con el precio de 2027).
- Campaña complementaria: 147 intervenciones (66/81/0 por canal); 25 y 122; cobertura 0,9388; proporción de tiempo 0,5307; kappa 0,556858 (p_o 0,69; p_e 0,30045), PABAK 0,6125, IC asintótico [0,4725; 0,6413]; consenso 138, 116 coincidentes con la referencia original; O1 71/80, O2 54/71 con sus intervalos; 125/151; automatizado 110/138; McNemar 0,26685 y 1,0; 13 diferencias entre caché y salida en vivo (4 correo, 3 web, 6 telefonía); Spearman −0,06278 (p 0,51465) y −0,36040 (p 0,00011).

Discrepan o no se reproducen: el efecto mínimo detectable del Spearman (0,2834 declarado; 0,264 con la fórmula del código); la exactitud laxa manual (130/151 solo con la unión de adicionales de E1 y E2; 128/151 con los del corpus); el balance laxo máximo (+138,0 con Δt = 43,8; +138,1 con los 43,82 que la Tabla 16 dice usar), diferencia de redondeo.

No recomputables de forma independiente, cotejados con `analisis/resultados.json` y los reportes de evaluación: los intervalos por bootstrap (dependen del generador de NumPy con semilla fija), las cifras de sensibilidad y ablación, y el kappa de 0,87 de la campaña 2026-10, cuya tabla no se conservó.

---

## VERIFICACIÓN BIBLIOGRÁFICA EXTERNA

- `verify_citations.py` dio PASS: 91 entradas, 91 claves citadas en 149 comandos de cita, ninguna huérfana ni sin usar. No hay duplicados. `main.blg` no tiene avisos. `main.bbl` es posterior a la última modificación del `.bib`.
- Los 49 DOI resuelven en Crossref al trabajo citado. Hay diferencias aceptables de año entre la versión en línea y la impresa: Paramesh (2018/2019) y Mosqueira-Rey (2022/2023). Virtanen figura con autor colectivo y Mayor-Rocher como publicación anticipada en línea sin volumen.
- Las diez entradas nuevas de c-188 están verificadas: Opitz y Burst en arXiv; McCambridge et al. en Crossref; las páginas de los términos y del audio de la Gemini API; la de grabaciones de Twilio; Docker Compose; Jira Service Management; osTicket; y la Disposición 60-E/2016. El Decreto 1558/2001 se confirmó en argentina.gob.ar; su URL de infoleg devolvió 503 y 403.
- Cotejo de afirmaciones contra la fuente. Están respaldadas las de Paket, TickIt, Zangari (tamaños y mejora del 28 %), Colavito (en lo cualitativo), Revina, MMLU-ProX (versión v2), Okapi, Zhang, La Leaderboard, Mayor-Rocher, Tian, Guo, Zhao, Varshney y FrugalGPT. Están sin respaldo o forzadas las de Zanzotto, Xiong y Galup (punto único de contacto). No son verificables, por texto cerrado o cifras en tablas, las cifras de macro-F1 de Colavito, el 5,7 % y el 5,4 % de Zangari, el 1,000 frente a 0,433 de Revina y los porcentajes de Ramya.
- Gemini API frente a Vertex AI: para `gemini-3.6-flash` los precios coinciden (0,75 y 3,75 USD por millón de tokens hasta el 31-12-2026; 1,50 y 7,50 desde el 1-1-2027). La página de la Gemini API declara que en el nivel gratuito los datos se usan para mejorar los productos de Google.
- Actualidad: 11 entradas son anteriores a 2000, 12 de 2000-2009, 17 de 2010-2019, 12 de 2020-2022 y 39 de 2023-2026.
- No verificado: la página de ServiceNow (403); las de OpenReview de Xiong y Chen, que piden verificación de navegador; los textos completos de ACM, Springer, Elsevier y SAGE; y Hernández Sampieri en catálogo.

---

## ANEXO: INVENTARIO DE CORRECCIONES PUNTUALES

| N.º | Ubicación | Texto o estado actual | Corrección |
|---|---|---|---|
| 1 | `07-resultados.tex:154`, `00-resumen.tex:13` y *abstract*, `01-introduccion.tex:34`, `08-discusion.tex:8`, `09-conclusiones.tex` (párrafo inicial, Tabla 18, cuarto objetivo), `10-recomendaciones.tex:18` | Sub-hipótesis 2 "no concluyente" con 25/200 | A1 |
| 2 | `07-resultados.tex:154` | Sin cotejo de confirmaciones y cambios con el consenso | A1 |
| 3 | `04-marco-metodologico.tex:16`, `11-aspectos-legales.tex:32` | Propósito comparativo ocultado a "los dos operadores"; *debriefing* a ambos | A2 |
| 4 | `04-marco-metodologico.tex:89`, `08-discusion.tex:22` | Amenaza Hawthorne sin la condición de autor de un operador | A2 |
| 5 | `12-anexos.tex:78` | "solo `docker-compose.yml` difiere" | A3 |
| 6 | `05-arquitectura.tex:50` | Transcripción "por el servicio de reconocimiento del habla del proveedor" y webhook a N8N | Según 6.4 (B1) |
| 7 | `06-implementacion.tex:74` | "el webhook de transcripción" | Callback de grabación y transcripción en el backend (B1) |
| 8 | `06-implementacion.tex:50`, Tabla 19, Anexo H | Modelo de transcripción no declarado | `gemini-3.5-transcribe` (B1) |
| 9 | `05-arquitectura.tex:44`, `figures/despliegue.png` | "red Docker"; transcripción ausente del diagrama | B1 |
| 10 | `07-resultados.tex:156` | Denominador con tiempos de la campaña no declarado; anacoluto | B2 y C1 |
| 11 | `07-resultados.tex:249` | Salida en vivo telefónica, predicción del McNemar y definición de la laxa manual no declaradas | B2 |
| 12 | `07-resultados.tex:251` | MDE ρ = 0,2834 | Corregir o justificar (B2) |
| 13 | `04-marco-metodologico.tex:65` | "clasificador congelado … métricas comparables" | Matizar (B3) |
| 14 | `02-marco-teorico.tex` (2.4), `05-arquitectura.tex:68`, `06-implementacion.tex:40`, `11-aspectos-legales.tex:36` | "posterior a las corridas de la campaña" | "posterior a la campaña 2026-10" (B3) |
| 15 | `figures/componentes.png`, `figures/secuencia.png` | "posterior a la campaña de medición" / "posterior a la campaña" | Regenerar (B3) |
| 16 | `01-introduccion.tex:66` | "validación rigurosa … doble etiquetado independiente" | B4 |
| 17 | `00-resumen.tex:15` y *abstract* | "confirman la viabilidad" | "respaldan" (B4) |
| 18 | `09-conclusiones.tex:23` | Reintentos sin "configuración entregada" | B4 |
| 19 | `08-discusion.tex:42` | "siete limitaciones" | "ocho" (C1) |
| 20 | `09-conclusiones.tex:26` | "exactitud del brazo manual" repetido | C1 |
| 21 | `00-glosario.tex` | Faltan TI, URL, E2E, MDE, VIS, HS256, CA | C1 |
| 22 | `00-portada.tex:30` | 8 de noviembre de 2026 | Fecha de la release (C1) |
| 23 | `figures/matriz_confusion.pdf` | Sin uso | Retirar (C1) |
| 24 | `12-anexos.tex` (Anexo B) y Tabla 23 | La tabla remite al Anexo B por artefactos que este no nombra | C1 |
| 25 | `11-aspectos-legales.tex:34` | Consentimiento de los sujetos de la campaña complementaria solo por remisión genérica | Describir cómo se informó y consintió a E1, E2, O1 y O2 |
| 26 | `02-marco-teorico.tex` (2.4) | Atribución a Zanzotto sobre ambigüedad semántica y responsabilidad | Reformular o citar la página (C2) |
| 27 | `02-marco-teorico.tex` (2.5), `08-discusion.tex` (9.2) | "discrimina poco" atribuido a Xiong et al. | Atenuar (C2) |
| 28 | `02-marco-teorico.tex:12` | Punto único de contacto atribuido a Galup et al. | Citar ITIL (C2) |
| 29 | `08-discusion.tex:66`, capítulo 7 | Precios de Vertex AI; nivel de la Gemini API no declarado | Gemini API y nivel de servicio (C2) |
| 30 | `Bibliography_base.bib` | URL de Zendesk, Vertex y Decreto 1558/2001; Ramya como preprint; Kerby "Article 1"; Efron 1993 con DOI de 1994 | C2 |

---

*Dictamen elaborado como autoevaluación de control de calidad interno frente a criterios de la CONEAU, a solicitud de los autores, mediante lectura íntegra del manuscrito, recómputo independiente de las cifras, verificación bibliográfica externa y cotejo con el repositorio en el tag `v1.2.12`. No constituye revisión por pares ni pronunciamiento de la cátedra, la dirección, el jurado ni la CONEAU.*
