# Dictamen de evaluación — Tesis de grado (criterios CONEAU)

**Documento:** «Automatización inteligente del registro de incidentes en mesas de ayuda empresariales mediante orquestación de flujos con N8N y procesamiento de lenguaje natural basado en modelos de lenguaje grandes» (Gomez, Bustos, Sevilla), Universidad Tecnológica Nacional, Facultad Regional Mendoza, Tecnicatura Universitaria en Programación.

**Versión examinada:** v10, tag anotado `v1.6.4` (objeto `1ccd36e1`, 24-11-2026, 18:20), que apunta al commit de contenido `f05ef2d6` (C3, 18:19). El commit siguiente, `c64832fc` (C4), consigna el hash en `paper/compilacion.md`; `main` está en `f2b75161` tras el merge de c-249 (`52e77723`) y, en `paper/`, difiere del tag únicamente en ese registro. PDF versionado de 157 páginas, SHA-256 `0c208da8…626e71`, idéntico en el árbol del tag, en `main` y en la copia de entrega `docs/Tesis/tesis_ultima_version.pdf`. Portada: «24 de noviembre de 2026, Versión 1.6.4». El tag está publicado en `origin` con el mismo objeto.

**Fecha:** 24 de noviembre de 2026.

**Método.** Lectura completa de las quince secciones `.tex` del tag (unas 54.800 palabras con comandos; 157 páginas), cotejo del diferencial `v1.6.3..v1.6.4` contra las catorce recomendaciones del dictamen del 23-11-2026, contra las respuestas de los autores registradas en las compuertas OQ-01 a OQ-06 de c-249 (`docs/Tesis/Correcciones/dictamen-correcciones.md`, sección c-249) y contra los artefactos del repositorio. Tres verificaciones independientes en paralelo: aritmética con recómputo en Python puro desde el corpus, las predicciones, las tablas de la campaña, los JSON de carga y los CSV de facturación; bibliografía con Crossref, arXiv, EUR-Lex y resolución de URL; seguimiento, forma y figuras (apertura de las imágenes). Convención de cita: `04:46` es la línea 46 de `04-marco-metodologico.tex`; `00r` es el Resumen. El capítulo legal (`11-…tex`) se compila como sección 7 y Resultados (`07-…tex`) como sección 8.

---

## Veredicto general

**APROBADA CON OBSERVACIONES.** Calificación sugerida del documento escrito: **8 (ocho)**; 8,45 ponderado según la rúbrica de la cátedra (sube desde 8,19 para `v1.6.3`).

La versión `v1.6.4` aplica, en un solo día de trabajo y con sus seis compuertas de autores respondidas por escrito, la casi totalidad de lo que el dictamen anterior pedía. De las seis recomendaciones necesarias, cuatro están atendidas (instrumento del cronometraje, sub-hipótesis 2 y lectura con consenso, reencuadre del Resumen y de los capítulos 7 a 10, lectura por régimen y nivel 5 de la sonda) y dos lo están en lo sustancial pero con una contradicción nueva cada una (titularidad del régimen (a); brecha del artículo 5). De las ocho de consistencia y forma, seis están atendidas y dos parcialmente. Las 55 cifras principales de los capítulos de resultados, discusión y conclusiones se reproducen desde los artefactos versionados, con una sola diferencia de redondeo. La bibliografía tiene 93 entradas sin huérfanas, con los 44 DOI y los 3 arXiv verificados y la fecha de la Decisión 2003/490/CE corregida. El marco teórico incorpora el modelo económico y los métodos estadísticos que faltaban; el estado del arte completa por fin la ficha de Paket (2024) y explica su criterio temporal.

Lo que este dictamen agrega no proviene de releer lo corregido sino de cotejar las declaraciones nuevas con la evidencia que la propia tesis imprime o versiona, y son cinco cosas.

Primera, y de veracidad. El capítulo legal explica los 145 incidentes de la captura del dashboard como «los 119 casos de la corrida del 2026-10-02 y 26 registros de prueba del 2026-10-13» y afirma que entre el 21-09 y el 1-10 «no hay registro de envíos a la API» (`11:34`). La Figura 5 que la tesis imprime (`figures/dashboard.png`) muestra, ampliada, puntos distintos de cero el 29-09, el 30-09 y el 1-10 (una docena de incidentes en conjunto), un pico del 2-10 cercano a 130 y apenas dos incidentes el 13-10; la Figura 4 (`panel_admin.png`), ordenada por identificador descendente, muestra solo dos tickets del 13-10 (`#00164`, `#00163`) y pasa al `#00155` del 2-10 a las 21:01. La explicación de `11:34`, que proviene de la respuesta OQ-03 (2) de los autores, no coincide con las dos capturas. Una base con incidentes anteriores al 2-10 no demuestra por sí sola una transferencia al proveedor, pero sí refuta la reconstrucción que la tesis ofrece de su propia cronología, en el párrafo que sostiene que «el consentimiento verbal precedió a todas las transferencias».

Segunda, también de veracidad. Para unificar la titularidad del régimen (a), los autores declararon que los reportantes son «los integrantes del entorno operativo del propio equipo, los autores y las personas de su círculo», y el registro precisa que ese círculo son «familiares y conocidos». El capítulo legal afirma a renglón seguido que «en el origen de ese régimen los titulares de los datos y los responsables del tratamiento son las mismas personas, de modo que no existe un responsable del tratamiento ajeno al grupo» (`11:46`). Para los familiares y conocidos, cuyos identificadores de usuario constaban en los originales (`11:18`), esa identidad es falsa, y la recolección y disociación de esos originales fue un tratamiento de datos de terceros que el capítulo no funda.

Tercera, de rigor. La tesis llama ahora «regla y denominador prefijados» al cociente 25/200 que decide la sub-hipótesis 2 (`01:34`, `04:109`, `07:185`). El denominador de 200 es, en efecto, el prerregistrado; el numerador no lo es. El diseño congelado antes de la campaña (c-167, 30-10-2026, decisión D7) definió la tasa de intervención humana como «casos con al menos una intervención vinculada / casos de la corrida», lo que da 147/200 = 0,735 y «refutada»; el numerador «cambios de derivación» (25) se introdujo después de ver los datos, y el veredicto del Resumen cambió cuatro veces entre `v1.2.8` y `v1.2.19`. La decisión de los autores en OQ-04 (opción a) es legítima como enmienda declarada; el rótulo «prefijado» para el numerador no lo es.

Cuarta, de release. Por la regla de tags elegida (opción A), el Anexo B remite al registro `compilacion.md` como «la referencia verificable de la versión entregada» (`12:60`). En el árbol del tag ese registro describe la release anterior: «release v1.6.3», 158 páginas y SHA `f6bebd9e…`, cuando el PDF del mismo árbol tiene 157 páginas y SHA `0c208da8…`. El registro correcto existe solo en `main`, un commit después. El tag no es verificable desde su propio contenido.

Quinta, de método. La nueva subsección «Medición del costo de reasignación» fija un mínimo de 30 reasignaciones y afirma que, con la dispersión observada, «ese mínimo acota la media con una precisión del orden del 10 %» (`10:38`). Con el desvío de los 24 cambios de sector de la campaña (54 s), 30 observaciones acotan la media en unos ±19 s, el 28 % de 69,5 s; el 10 % exigiría del orden de 230. El registro de c-249 consigna ese mínimo como «a ratificar por los autores», y salió publicado sin ratificación.

A estas cinco se suman contradicciones menores que las correcciones trajeron consigo: quién llevó el registro del cronometraje (`04:97` dice `A1`; `04:16` y `04:46`, los dos por turno); una carga del ticket «del orden de 10 s» sumada a todos los casos cuando cuatro casos valen 10 s en total (`R037`, `R186`, `R187`, `R198`); un acta T2 cuyo encabezado dice «consentimiento verbal prestado y documentado el 2026-10-02» mientras la tesis declara que «la única documentación del 2-10 es el acta redactada el 17-11» (`11:36`); incidentes «recogidos … exclusivamente en su entorno operativo diario» (`04:46`) reportados por familiares y conocidos; y la fila del OE3 con veredicto «No sostenida» en la tabla de cumplimiento (`09:26`) frente a «se alcanza parcialmente» en la prosa (`09:40`).

Ninguna de estas observaciones exige medir de nuevo. Las de veracidad exigen cotejar lo declarado con la base, el export o el acta y escribir lo que resulte; las de rigor, un rótulo honesto; las de release y método, una línea cada una.

---

## Seguimiento de las catorce recomendaciones del dictamen anterior

| N.º | Recomendación (resumen) | Estado | Evidencia en `v1.6.4` |
|---|---|---|---|
| 1 | Reescribir `04:97` sobre el instrumento que quedó; falta de registro primario en la primera amenaza; OE5 y `01:54` | **Atendida, con una contradicción nueva** | `04:97` («registro de cronometraje … llevado en vivo por `A1` … no se conserva en su forma original, pero sí en la pseudonimizada»); `04:117`; `01:54`; `09:28`. La hoja `data/Corpus Tesis - Hoja 1 (pseudonimizado).csv` existe, versionada el 9-10-2026 (`ea625764`), con una sola columna de tiempo cuyos 200 valores son los del corpus. `04:97` atribuye el registro a `A1`; `04:16` y `04:46` dicen que `A1` y `T1` cronometraron por turnos. El registro del equipo pasó de «las planillas no existen» (c-247, OQ-02 (5), 20-11) a «la hoja ERA la planilla» (c-249, OQ-01 (1), 24-11). |
| 2 | Unificar la titularidad del régimen (a); PII de los originales; «se redactaron» frente a «coinciden»; empleadores; `01:72` | **Parcial** | Fórmula única en `01:16`, `04:46`, `11:16`, `11:46`, `11:54`; PII en `11:18`, `11:26`, `12:155` y `data/README.md`; reescritura de los 119 en `04:129` y `09:25`; «texto de origen» redefinido en `12:157`; `01:72` acotado. Queda `11:46` (titular = responsable, falso para el círculo). |
| 3 | Analizar la brecha del artículo 5; «expreso»; corrida del 2-10; período 21-09 a 1-10; «desliz»; acta T2 | **Atendida en el texto; contradicha por las figuras y por el acta** | `11:32` (verbal el 2-10, escrito el 20-11; corrida posterior); `11:36` (brecha valorada); `11:34` (período declarado); «expreso» y «desliz» desaparecieron; acta T2 revisada por anexo §7. `11:34` no coincide con las Figuras 4 y 5; el encabezado del acta dice «documentado el 2026-10-02». |
| 4 | Ordenar el veredicto de la sub-hipótesis 2; nombre único; lectura con consenso de la 3 | **Atendida, con un rótulo inexacto y un residuo** | `01:34`, `04:109`, `07:10`, `07:25-26`, `07:185`, `08:8`, `09:6`, `09:22`, `09:27`, `09:42`, `10:22`, `00r:10` y `00r:26`; variable única «intervención manual sobre la derivación»; consenso en `07:24`, `07:154`, `08:62`. El numerador no es prefijado (c-167 D7); `10:6` conserva «estimación puntual por encima de la cota». |
| 5 | Completar el reencuadre: Resumen, `07:37`, `09:22`, `01:18`, rótulos del volumen, `08:68`, `08:42`, `09:49`, `09:47`, `01:38`, `04:46`, `04:54` | **Atendida en lo sustancial** | `00r:8` y `00r:24` (escenario, 119/81, laboratorio); `00r:12`, `08:72`, `08:118` («volumen supuesto»); `07:38`; `08:42`; `08:68`; `09:48` («técnicamente integrable»); `09:50`; `01:38`; `04:46`; `04:54`. Residuos: `09:48` «corpus propio de la organización»; `01:18` «la medición vigente» sin «laboratorio»; `08:70` «sectores responsables». |
| 6 | Lectura por régimen en `08:18`; `08:50`; «un autor»; nivel 5 en `07:376` | **Atendida** | `08:18` (94/119 = 0,790 [0,708; 0,854]; 53/81 = 0,654 [0,546; 0,749]); `08:50`; `07:377` (3.660,4 ms y 5.024,7 ms). El límite 0,854 es 0,853 en el artefacto; «los autores» persiste en `04:129`, `12:149` y `12:241`. |
| 7 | Ventana «junio a agosto» como declaración; origen de los 2 min 45 s; `04:89`; constructo | **Atendida** | `04:46`; `04:89` («no hubo búsqueda»); `04:131` (octava amenaza); OQ-01 (3) decidió conservar `01:18`. |
| 8 | `12:60`; tarea 6.3 de c-248; «EN CURSO»; `compilacion.md` con el commit; Nota de versiones; regla de tags | **Parcial** | `12:60` reescrito; enmienda en `tasks.md` de c-248; c-247 y c-248 en «ARCHIVADO»; regla (A) escrita (OQ-05 (1)); Nota de versiones sin `v1.6.2`/`v1.6.3` ni erratum por decisión OQ-05 (3). El `compilacion.md` del árbol del tag es el de `v1.6.3`; `dictamen-correcciones.md:7095` dice «c-249 … EN CURSO». |
| 9 | Metadato del corpus; `data/README.md`; Anexo F desde §4.4 | **Atendida** | `12:151`; `data/README.md` (párrafo superado); `\autoref{sec:anexo-corpus}` en `04:48`. |
| 10 | Ficha de Paket; criterio temporal; conteos; Zapier/Make/Power Automate; `03:28`; `03:24`; `03:90-92`; Revina | **Atendida** | `03:49` (cifras de Paket transcritas de la copia de los autores); `03:8` (criterio temporal, búsqueda dirigida, conteos de C1 y C2 y declaración de los no registrados); `03:22`; `03:24`; `03:47`; `03:90-92`. |
| 11 | Modelo económico en el marco teórico; `02:100`; duplicados; umbrales y fechas; `02:20` | **Atendida** | `02:98` (`subsec:modelo-economico`); `02:104`; `02:12` y `02:20` como inferencias; fechas de implementación fuera del capítulo 2. El cardinal «once ejes» (`02:6`) no se actualizó: hay doce subsecciones. |
| 12 | OE2 en dos filas; OG «prototipo»; OE3; subsección de reasignación; `10:6`, `10:14`, `10:38`; línea por régimen; `06:62`, `06:74`, `06:97` | **Parcial** | `09:24-25`; `01:42`; `09:26`; `10:36`; `10:26`; `06:38`; `06:60`. Residuos: «No sostenida» en la fila del OE3 frente a `09:40`; `01:48` sigue llamando al umbral «criterio de éxito de este objetivo» tras la separación; la subsección de primer nivel `10:36` aparece después de las de segundo nivel, contra lo que `10:6` declara; `10:38` con la cifra de precisión sin sostén. |
| 13 | Flotantes; glosario; «F1 macro de umbral»; p unilateral; tope de páginas | **Atendida, con una salvedad** | Figuras 12 a 14 en pp. 144-146, antes del Anexo F (`\FloatBarrier`, `12:145`); glosario en 50 filas completas; `01:36`; `01:32`/`04:103`. El exceso (+57 páginas) se declaró solo en el registro de correcciones, no en la tesis. |
| 14 | Decisión 2003/490/CE; «s. f.»; referencia del modelo; inventario 1250/1251 | **Atendida** | `Bibliography_base.bib:906` («L 168, 5 de julio de 2003, pp. 19-22»); cuatro entradas en «s. f.»; referencia de Gemini no agregada por decisión registrada («no hay página oficial verificable»); `12:255` «165 de 1278», verificado. |

En suma: de las seis necesarias, cuatro atendidas (1, 4, 5, 6, las dos primeras con un residuo propio) y dos parciales (2, 3); de las ocho de consistencia y forma, seis atendidas (7, 9, 10, 11, 13, 14) y dos parciales (8, 12). Esta vez el equipo atendió también las de forma, que en rondas anteriores quedaban relegadas.

---

## Seguimiento de la devolución de cuarta instancia del tribunal

| Código | Estado | Evidencia |
|---|---|---|
| R-01 (escenario ficticio) | Atendida, con dos residuos | `01:16`, `01:18`, `04:46`, `11:44`, `12:245`; residuos `09:48` y `08:70`. |
| R-02 (composición, autoría, asistente de IA, amenaza) | Parcial | `04:46`, `04:129`, `08:50`, `12:149`. La reescritura de los 119 casos por los autores (`04:129`, `09:25`) no llegó al Resumen (`00r:8`), a `08:50` ni a `09:54`, que limitan la coautoría a las 81; «sin asistente de inteligencia artificial» se declara solo para el régimen (b). |
| R-03 (flujo manual como laboratorio) | Atendida, con residuos | `04:46`, `04:89`, `04:97`, `04:131`, Tabla `04:78`; quedan la ambigüedad sobre quién cronometró y la lectura «cota superior solo por redondeo». |
| R-04 (N supuesto) | Atendida | `04:46`, `04:54`, `00r:12`, `08:72`, `08:118`, `09:6`. |
| R-05 (capítulo legal) | Parcial | Reescrito por régimen; pendientes `11:34` y `11:46`. |
| R-06 (limitaciones) | Atendida | `08:50`, `09:50`, `09:52`. |
| R-07 (Nota de versiones) | Atendida | `12:245`. |
| B-01 (nombres de sector) | Atendida | Ninguna cadena canónica cruda en la prosa. |

---

## Observaciones por sección

### 1. Estructura general — Cumple, con observaciones

Fortalezas. El orden es el de la serie: Resumen y Abstract paralelos (234 y 232 palabras de prosa), once capítulos con el legal antes de los resultados y una oración que lo justifica, once anexos A a K, glosario de 100 entradas reorganizado sin celdas vacías, 44 flotantes citados y con fuente, cero referencias indefinidas. La síntesis de cifras primarias (`07:12-34`) sigue siendo el mejor dispositivo de lectura del documento y ahora distingue la regla prefijada del dato post hoc en dos filas.

Debilidades. **Extensión:** 157 páginas, 57 sobre el tope de 100 que el equipo adoptó; la renuncia se declaró por escrito en el registro de correcciones con magnitud, fecha y decisión, pero el ejemplar no la menciona. **Orden del capítulo 11:** `10:6` afirma que «el orden de las subsecciones siguientes» respeta los tres niveles de prioridad; la subsección de primer nivel «Medición del costo de reasignación» (`10:36`) aparece después de cuatro de segundo nivel. **Cardinales:** `02:6` anuncia «once ejes temáticos» y el capítulo tiene doce subsecciones desde que se agregó el modelo económico. **Release:** el registro al que el Anexo B remite describe otra versión dentro del árbol del tag (véase el Anexo A de este dictamen). **Nota de versiones:** no registra `v1.6.1` a `v1.6.4` ni el erratum del PDF de `v1.6.2`, por decisión fundada de los autores; un lector del PDF de `v1.6.2` sigue sin tener modo de saber que su Anexo B imprime otro hash. **Formato de números:** separador de miles inconsistente en un mismo párrafo (`07:377`: «3.660,4 ms» y «5.024,7 ms» frente a «7545,7; 8352,7 y 10183,6 ms») y en la Tabla `07:325-333`.

### 2. Claridad y formulación de la hipótesis — Cumple, con una observación de rigor

Fortalezas. Tres sub-hipótesis con contraste, estadístico y criterio de falsación propios; «F1 macro de umbral» definido en la hipótesis (`01:36`); la convención del valor p declarada con el unilateral global (`01:32`); la subsidiaria de eficiencia declarada sin contraste y la de integración acotada a capacidad (`01:38`); la variable de la sub-hipótesis 2 con un solo nombre en los nueve lugares donde aparece; la lectura con consenso de la sub-hipótesis 3 alineada con la regla (`07:24`, `07:154`, `08:62`).

Debilidad de rigor. La regla de la sub-hipótesis 2 se enuncia ahora de forma coherente entre la introducción, el método y los resultados, y eso es un avance real. Pero el texto afirma que «el cociente sobre los 200 casos es la aplicación prefijada de la regla» (`01:34`) y que el 147 «se adoptó después de conocer los datos». El prerregistro del repositorio dice otra cosa: el diseño D7 de c-167 (30-10-2026), congelado antes de la campaña, definió `tasa_intervencion_humana` como «casos con al menos una intervención vinculada / casos de la corrida», es decir 147/200, y su salida versionada da 0,735 y «refutada». Lo que es post hoc no es el denominador de 147 sino el numerador de 25: la restricción de «intervención» a «cambio de la derivación» se formuló después de ver que 147 de 200 casos habían sido revisados por la regla del reportante. El historial del Resumen lo muestra: refutada con 73,5 % (`v1.2.8`), no concluyente con 12,5 % (`v1.2.11`), refutada sobre 147 (`v1.2.15`), no concluyente (`v1.2.19` en adelante). La redacción de `v1.2.0` («se falsea si su límite superior no queda por debajo de 0,15») tampoco era la de tres vías, y con ella 25/200 (límite superior 17,8 %) también se falsaría. La opción (a) que los autores eligieron en OQ-04 es defendible como enmienda declarada; presentarla como aplicación prefijada no lo es. Residuo: `10:6` dice que la campaña dejó la sub-hipótesis «no concluyente con estimación puntual por encima de la cota», que es la lectura sobre 147, no la que ahora decide.

### 3. Definición y coherencia de los objetivos — Cumple, con observaciones

Fortalezas. Objetivo general sobre un prototipo (`01:42`); OE2 separado en implementación (alcanzado) y desempeño (no alcanzado) en la tabla (`09:24-25`); fila del OE3 con la exclusión de correo y telefonía del ensayo y la remisión correcta (`09:26`); OE5 acotado al registro disponible (`01:54`, `09:28`); criterio de éxito del umbral fundado en tres criterios a priori y separado de las lecturas posteriores (`01:48`).

Debilidades. **OE3:** la tabla le asigna «No sostenida», que es un veredicto de hipótesis y no un grado de cumplimiento, y la prosa dice «El tercer objetivo específico se alcanza parcialmente (latencia y exactitud medidas por canal)» (`09:40`); `08:18` le atribuye al OE3 una «dimensión de calidad» que su enunciado (`01:50`) no tiene. **OE2:** `01:48` sigue diciendo que el umbral «constituye el criterio de éxito de este objetivo» cuando el objetivo ya se partió en dos y la mitad de implementación se da por alcanzada sin ese criterio. **Objetivo general:** `09:6` afirma que la combinación «resultó operativa y eficiente», con la subsidiaria de eficiencia sin contrastar (`01:38`, `07:10`). **Pregunta de investigación:** sigue hablando del umbral «definido para una mesa de ayuda empresarial mediana» (`01:26`), objeto que el resto del documento reencuadró como escenario.

### 4. Estado del arte — Cumple

Fortalezas. Protocolo con seis bases, siete cadenas, dos fechas de corte y, ahora, el criterio temporal explicado (2023-2026 para A1 a A4; Paramesh 2019 y Revina 2020 por búsqueda dirigida de líneas de base), los conteos de C1 y C2 y la declaración de que los de A1 a A4 y B1 no se registraron (`03:8`); limitación regional declarada (`03:10`); la ficha de Paket (2024) completa por primera vez con corpus, clases, fechas y cifras por modelo (`03:49`), y la de Revina releída sobre el original (`03:47`); Zapier, Make y Power Automate como relevamiento propio fechado; la brecha acotada «en el alcance revisado» y «dentro de la muestra y sobre el corpus propio» (`03:90-92`); Colavito con la aclaración de que sus corpus no son tickets.

Debilidades. Las cifras de Paket (2024) y la exactitud 1,000 de Revina (2020) se transcribieron de copias que están fuera del repositorio y que un verificador externo no puede leer (IEEE cerrado; IEEE Access bloquea la descarga automatizada); los metadatos y el resumen de Paket confirman turco, 172 clases y la superioridad de BERT, pero no las cifras por modelo ni la caída «por encima de 70 clases». Conviene citar la página de cada cifra. El criterio de inclusión «idioma español o multilingüe» (`03:8`) no lo cumple ninguno de los seis trabajos de la Tabla 1 (turco, inglés, no reportado); el protocolo debería decir que ese criterio se aplicó a A3 y no a A1 y A2. Afirmaciones de relevamiento propio sin cita siguen siendo relevamiento propio (`03:14-18`), y la tabla comparativa compara productos con una fuente por producto consultada en una fecha.

### 5. Marco teórico — Cumple

Fortalezas. Doce subsecciones con fuentes primarias verificadas; la nueva subsección del modelo económico (`02:98-100`) formaliza el balance neto y la exactitud de equilibrio que el Resumen cita; la subsección estadística incorpora Shapiro-Wilk, Hodges-Lehmann, binomial exacta y rank-biserial (`02:104`); las dos afirmaciones empíricas sin cita quedaron declaradas inferencias de los autores (`02:12`, `02:20`); los duplicados con el capítulo 3 y las fechas de implementación salieron del capítulo.

Debilidades. «Once ejes» por doce (`02:6`). La justificación de la orquestación frente a la coreografía «en línea con los requisitos de la Ley 25.326» (`02:28`) es un salto: la trazabilidad centralizada facilita el artículo 9, pero la ley no prescribe un paradigma de integración. El acuerdo entre anotadores se trata en una subsección de ocho líneas para un problema que la discusión reconoce como la octava limitación del trabajo; faltan el PABAK y la noción de prevalencia que los resultados usan (`07:283`). La calibración y las cascadas se fundamentan bien; la relación entre confianza verbalizada y AUROC, que decide una conclusión, se enuncia en una oración (`02:88`).

### 6. Desarrollo metodológico y propuesta — Cumple, con observaciones de fondo

Fortalezas. El método declara hoy, con palabras propias, casi todo lo que el equipo sabe: la ventana «junio a agosto» como declaración sin registro fechado; la composición 119/81 como declaración sin registro por caso; la tarea de laboratorio en domicilio con planilla; la medición manual como lectura medida más carga estimada, con la octava amenaza de constructo (`04:131`); «no hubo búsqueda» (`04:89`); la resolución de 5 s del instrumento ligada a los descuentos del análisis de sensibilidad (`04:16`, `04:117`); la Tabla de procedencia de cifras por corrida; el protocolo de la campaña complementaria; el test de carga y la sonda con sus prerregistros. El capítulo legal ordena las transferencias respecto del consentimiento verbal, valora la brecha del artículo 5 con un texto aprobado por los autores y declara que la única documentación del 2-10 es posterior al hecho (`11:36`). El sistema sigue siendo funcional, documentado y reproducible, con coincidencia verificada entre lo descrito y lo versionado (68 rutas citadas, todas existentes y versionadas).

Debilidades de veracidad.

(a) **La cronología declarada no coincide con las capturas.** `11:34` dice que los 145 incidentes de la Figura 5 son 119 del 2-10 y 26 de prueba del 13-10, y que entre el 21-09 y el 1-10 no hubo envíos a la API. La curva diaria de la Figura 5 tiene puntos distintos de cero el 29-09, el 30-09 y el 1-10, un pico del 2-10 cercano a 130 y unos dos incidentes el 13-10; la Figura 4 muestra solo dos tickets del 13-10 y, entre el `#00155` del 2-10 y el `#00163` del 13-10, siete identificadores que no aparecen. Las dos figuras son del 21-10-2026 y no cambiaron desde `v1.6.3`. La respuesta OQ-03 (2) debió cotejarse con la base o con el export antes de escribirse; tal como está, el párrafo que sostiene que «el consentimiento verbal precedió a todas las transferencias» se apoya en una reconstrucción que la propia tesis refuta. La tesis debe decir qué son esos incidentes del 29-09 al 1-10 (registros de prueba, casos del corpus, otra cosa) y si alguno escaló a Gemini.

(b) **Titularidad del régimen (a).** La fórmula única incluye «las personas de su círculo» (familiares y conocidos, según OQ-02 (1)). `11:46` afirma que «en el origen de ese régimen los titulares de los datos y los responsables del tratamiento son las mismas personas». Para esos terceros no lo son: sus identificadores de usuario constaban en los originales (`11:18`), y la recolección, la reescritura y la disociación de esos originales fueron un tratamiento de datos personales de terceros anterior a la disociación, que el capítulo no funda en ninguna base de licitud ni en consentimiento. La afirmación de `11:18` de que «no se tratan … datos personales ni información reservada de sus sistemas» vale para lo que se conserva y transfiere, no para lo que se recolectó. En la misma línea, `04:46` dice que los 119 incidentes se recogieron «exclusivamente en su entorno operativo diario», y `01:76` y `09:52` hablan de «un único entorno operativo, del sector servicios»; incidentes reportados por familiares y conocidos no provienen de un único entorno operativo ni, necesariamente, del sector servicios.

(c) **Instrumento del cronometraje.** El registro del equipo cambió de signo en cuatro días: «las planillas de cronometraje no existen» (c-247, OQ-02 (5), 20-11) frente a «el registro EXISTE: la hoja de campaña … ERA la planilla» (c-249, OQ-01 (1), 24-11). La tesis adopta la segunda. La hoja versionada (`data/Corpus Tesis - Hoja 1 (pseudonimizado).csv`, commit del 9-10-2026) tiene una sola columna de tiempo cuyos 200 valores son exactamente los de `tiempo_manual_s`: es el registro de los valores finales, no de las lecturas, y no permite separar la lectura medida de la carga estimada. Tres inconsistencias derivan de ahí. Primera, `04:97` dice que el registro lo llevó «`A1`, el analista externo», mientras `04:16` y `04:46` dicen que `A1` y `T1` cronometraron por turnos; si `T1` cronometró a `A1` en la mitad de los casos, el registro no es de `A1`. Segunda, `04:89` y `04:131` dicen que a cada lectura se le sumó una carga fija «del orden de 10 s»; cuatro casos (`R037`, `R186`, `R187`, `R198`, del formulario web) valen 10 s en total, lo que implica una lectura de 0 s o una carga menor. Tercera, `04:117` y `09:28` llaman a `R017` (72 s) «la única medición exacta» cuando también incluye la constante estimada. Además, como la carga estimada es del orden del descuento de 10 s del análisis de sensibilidad, la tesis ya tiene una cota de la octava amenaza (65,6 %) y no la conecta: sigue leyendo el 71,2 % como «cota superior por redondeo» (`07:22`, `07:38`, `07:89`, `09:22`, `00r:10`), sin la carga estimada.

(d) **Acta T2.** Su encabezado (`docs/seguridad/acta-consentimiento-t2.md:7-8`) dice «consentimiento verbal prestado y documentado el 2026-10-02»; la tesis dice que «entre el 2026-10-02 … y el 2026-11-20 … no existió constancia escrita» y que «la única documentación del 2-10 es el acta redactada el 17-11» (`11:36`). El acta se creó el 17-11 (`efef2952`); su fecha de firma apareció el 22-11 (`b5554673`; antes decía «sin fecha de firma consignada»). La revisión por anexo fue una decisión razonable para no reescribir un documento firmado, pero el encabezado quedó contradiciendo a la tesis en el punto exacto que el dictamen anterior señaló.

(e) **Régimen definido por canal.** La lectura por régimen que el dictamen anterior pidió se escribió con cifras recomputadas por un script versionado y con pruebas, lo que es correcto. El script define el régimen (b) como el canal telefónico, porque el corpus no tiene campo de régimen; la equivalencia «telefonía = reconstrucciones» descansa en la declaración de los autores y conviene decirlo en `08:18`.

Debilidades de procedimiento. Las seis compuertas se presentaron, se respondieron y se aplicaron entre las 13:00 y las 18:19 del 24-11, el mismo día de la release; dos de las respuestas (OQ-01 (1) y OQ-03 (2)) resultaron contradichas por evidencia que estaba en el repositorio. El método de compuertas es bueno; su cadencia no dejó lugar al cotejo. La ampliación del universo de reportantes a «personas de su círculo» y la calificación del régimen (a) como disociado se decidieron en la misma ronda, y sus consecuencias legales (tratamiento de terceros antes de la disociación) no se analizaron. El brazo manual precedió al automatizado en los 200 casos de la campaña complementaria y el efecto de orden sigue sin estimar, como antes.

### 7. Conclusiones — Cumple, con observaciones

Fortalezas. Los veredictos de las tres sub-hipótesis coinciden entre la síntesis, los resultados, la discusión y las conclusiones; la tabla de cumplimiento distingue el OE2 en dos filas y declara la coautoría sobre los 200 casos (`09:25`); el balance neto se presenta como cota superior con su signo condicionado; la generalización se limita a este corpus y el escenario «solo dimensiona el problema» (`09:50`); las tres contribuciones se enuncian con sus límites (`09:54`); «técnicamente viable» pasó a «técnicamente integrable … pero su exactitud no alcanza el criterio» (`09:48`).

Debilidades. `09:48` conserva «No se midió un clasificador entrenado sobre el corpus propio de la organización», la organización que el reencuadre retiró. La fila del OE3 y la prosa de `09:40` se contradicen. «Eficiente» en `09:6`. `09:52` y `01:76` sostienen «un único entorno operativo, del sector servicios» frente a la nueva fórmula de reportantes. La coautoría declarada en `09:25` y `04:129` (los autores reescribieron los 119 y uno construyó las 81) se reduce a «81 reconstrucciones redactadas por uno de ellos» en el Resumen (`00r:8`), en `08:50` y en `09:54`, y `12:149` y `12:241` vuelven a «redactadas por los autores». `08:118` remite la medición del costo de reasignación a `subsec:estudios-replicacion` cuando ahora existe `subsec:medicion-costo-reasignacion`. El límite 0,854 del régimen (a) es 0,853 en el artefacto (`08:18`); la cita «línea 98» de `08:64` apunta a la línea de los aciertos y el valor p está en la 101.

### 8. Propuestas de trabajos futuros — Cumple, con una observación de fondo

Fortalezas. Tres niveles de prioridad anclados en limitaciones medidas; cada línea con criterio de éxito y, donde corresponde, tamaño de muestra; la subsección de primer nivel sobre el costo de reasignación que el dictamen anterior pidió; la línea de medición por régimen o sustitución de las reconstrucciones por llamadas reales (`10:26`); la lista de ampliaciones de producto separada y declarada sin criterio de éxito; los changes abiertos del repositorio (c-228, c-229, c-230, c-232) no se dan por ejecutados.

Debilidad de fondo. `10:38` fija «un mínimo de 30 reasignaciones» y afirma que «con la dispersión observada en la campaña (media 69,5 s; IC [33,4; 106,6]), ese mínimo acota la media con una precisión del orden del 10 %». La dispersión observada no lo sostiene: el componente de corrección en la compuerta proviene de 24 cambios de sector con desvío de 54 s y 114 confirmaciones con desvío de 40 s (`analisis_costo_derivacion_c220.json`); con 30 observaciones y ese desvío, la semiamplitud del intervalo es de unos 19 s, el 28 % de la media, y una precisión del 10 % exige del orden de 230 reasignaciones. El registro de c-249 (grupo 7, tarea 7.6) consigna el mínimo de 30 como «a ratificar por los autores»: la cifra se publicó sin la ratificación que el propio equipo había previsto. Residuos: `10:6` (veredicto viejo) y el orden de las subsecciones frente a los niveles declarados.

### 9. Bibliografía — Cumple

Fortalezas. 93 entradas, 93 claves citadas, 0 huérfanas en ambos sentidos (`verify_citations.py` PASS, replicado); APA 7 uniforme con biblatex y biber sin advertencias; 44 DOI y 3 arXiv consultados, todos existentes y coincidentes en título, autores, año y páginas; la fecha de la Decisión 2003/490/CE corregida en el `.bib` y en `11:12`; las cuatro entradas de documentación en «s. f.» con fecha de consulta; la entrada del repositorio actualizada a `v1.6.4`; sin duplicados ni caracteres rotos en el `.bbl`.

Debilidades. Las cifras tomadas de Paket (2024) y de Revina (2020) no son verificables por un tercero sin las copias de los autores; conviene citar la página de cada una. `Powers2011_evaluation` nombra la revista con una variante («Journal of Machine Learning Technologies» por «International Journal of Machine Learning Technology»); `Paramesh2019_it_service_desk` lleva 2019 donde Crossref registra 2018 (la edición impresa de LNNS 43 justificaría 2019, pero no se dice); las claves de las cuatro entradas sin año conservan «2024». En la capa de texto del PDF (p. 131) «Şenerkek» pierde la «Ş»; el `.bbl` la tiene y el defecto puede ser solo de extracción, pero conviene mirar la página. No se agregó referencia técnica del modelo Gemini 3.6 Flash, por la razón registrada de que no existe página oficial verificable; la tesis cita precios, términos y la página de audio. De las 16 entradas de 2026, 12 son páginas de proveedor; la literatura académica comparable es escasa y de acceso cerrado, y el texto lo declara.

---

## Recomendaciones

**Necesarias antes de la defensa (afectan la veracidad o el rigor del documento):**

**1. Reconciliar `11:34` con las Figuras 4 y 5.** Consultar la base o el export de la instancia de la captura y decir qué son los incidentes del 29-09, el 30-09 y el 1-10 y los del 2-10 que exceden los 119 (registros de prueba, casos del corpus, reintentos), cuántos hubo el 13-10 y qué fue de los identificadores `#00156` a `#00162`. Si alguno de los anteriores al 2-10 escaló a Gemini, decirlo y extender la valoración de la brecha del artículo 5 a ese intervalo; si no puede reconstruirse, escribirlo así («la base de la captura no se conservó; la composición de los 145 no es verificable») en lugar de una explicación que las figuras desmienten. Alinear el pie de las dos figuras con lo que se concluya.

**2. Corregir `11:46` y fundar el tratamiento de los terceros del círculo.** Retirar «titulares y responsables del tratamiento son las mismas personas» o acotarlo a los incidentes reportados por los propios autores. Para los familiares y conocidos: decir cuántos de los 119 casos provienen de ellos si se sabe, y, si no, declararlo; reconocer que la recolección y la disociación de sus originales (con `ID USUARIO`) fue un tratamiento de datos personales de terceros anterior a la disociación, y fundarlo (consentimiento, relación personal con fines exclusivamente académicos, artículo 5 inciso 2 si alguno aplica) o declarar la brecha como se hizo con el artículo 5. Reescribir «no se tratan» (`11:18`) como «no se conservan ni se transfieren». Corregir «exclusivamente en su entorno operativo diario» (`04:46`), «un único entorno operativo» (`01:76`, `09:52`) y «del sector servicios» donde se refiera a los 119 casos.

**3. Rotular con exactitud la sub-hipótesis 2.** Decir en `01:34` y `04:109` que la definición prerregistrada de la variable (c-167, D7) era «casos con al menos una intervención sobre casos de la corrida» (147/200, refutada), que la restricción a «cambios de la derivación» (25) se adoptó después de conocer que la revisión actuó por la regla del reportante, y que por eso el veredicto vigente es una enmienda declarada y no la aplicación prefijada. Conservar la lectura 25/200 como la que los autores sostienen, con su motivo (la regla del reportante mide la configuración de la prueba y no la necesidad de revisión), e informar 147/200 y 25/147 como las otras dos lecturas. Corregir `10:6`.

**4. Cerrar las contradicciones del instrumento manual y del acta.** Unificar quién llevó el registro (`04:97` frente a `04:16` y `04:46`); decir que la hoja versionada contiene los valores finales (lectura más carga) en una sola columna y que la lectura no se conserva por separado; explicar los cuatro casos de 10 s (`R037`, `R186`, `R187`, `R198`) frente a la carga «del orden de 10 s», o corregir la magnitud; retirar «la única medición exacta» para `R017` o precisar «el único valor no redondeado»; conectar la octava amenaza con el escenario de descuento de 10 s del Anexo K y leer el 71,2 % como cota superior «por el redondeo y por la carga estimada» en `07:22`, `07:38`, `07:89`, `09:22` y el Resumen. En el acta T2, reemplazar «documentado el 2026-10-02» por «prestado verbalmente el 2026-10-02 y documentado el 2026-11-17» mediante el mismo anexo §7, ya que el cuerpo no se reescribe.

**5. Hacer verificable el tag desde su propio contenido.** Con la regla A, el commit de contenido puede consignar en `compilacion.md` todo lo que no depende del hash (páginas, SHA-256 del PDF, fecha, «release v1.6.4, C3») y dejar solo la fila del hash para C4; así el registro del tag describe su propia versión y `12:60` deja de remitir a un registro ajeno. Escribirlo en el requisito de release de `tesis-document`. Pasar el encabezado de c-249 (`dictamen-correcciones.md:7095`) a «ARCHIVADO (2026-11-24)».

**6. Sostener o corregir el tamaño de muestra de `10:38`.** Recalcular con el desvío observado (54 s en los cambios de sector): para una semiamplitud del 10 % de la media hacen falta unas 230 reasignaciones; para el mínimo de 30, la precisión es del orden del 30 %. Elegir una de las dos redacciones y registrar la ratificación de los autores que el propio change dejó pendiente.

**De consistencia:**

7. Tabla de cumplimiento: dar al OE3 un grado de cumplimiento («Alcanzado parcialmente: integración lograda; capacidad no sostenida en la capa de orquestación») y dejar «no sostenida» para la hipótesis; alinear `09:40`; reescribir `01:48` para que el umbral sea el criterio de la mitad de desempeño del OE2; retirar «eficiente» de `09:6`; quitar «dimensión de calidad del tercer objetivo» de `08:18`; reformular «para una mesa de ayuda empresarial mediana» en la pregunta de investigación (`01:26`).
8. Residuos del reencuadre y de la autoría: `09:48` («corpus propio de la organización» → «corpus propio acumulado en operación»); `08:70` («sectores responsables» → «sectores receptores» o «revisores»); `01:18` («la medición vigente de la tarea de laboratorio»); `08:118` (remitir a `subsec:medicion-costo-reasignacion`); Resumen, Abstract, `08:50` y `09:54` con la coautoría sobre los 200 casos (119 reescritos por los autores y 81 construidas por uno de ellos), y `12:149` y `12:241` con «uno de los autores»; `04:46` «pseudonimizada» → «disociada» para el régimen (b); declarar en `04:46` o `04:129` si la reescritura de los 119 se hizo sin asistente de inteligencia artificial.
9. Lectura por régimen: corregir 0,854 → 0,853 en `08:18` y en el PDF; declarar que el régimen se asigna por canal porque el corpus no registra la procedencia por caso; corregir «línea 98» → «línea 101» en `08:64`.
10. Capítulo 11: mover `subsec:medicion-costo-reasignacion` junto a las de primer nivel o reescribir `10:6` sin la promesa de orden. Capítulo 2: «once ejes» → «doce». Figura 11 (cronograma): la barra dice «Campaña automatizada (sep-oct)» y el texto, «octubre de 2026».
11. Capítulo legal: `11:16` dice que el consentimiento «no dispensa el deber de información del artículo 6» en un régimen que, según el mismo párrafo, no trata datos personales; o bien hay tratamiento y hay deber de información, o bien no lo hay. `11:122` sigue apoyando los controles de privacidad en «la base de licitud del artículo 5 … [y] el instrumento de transferencia internacional del artículo 12», que el capítulo declara inexistentes para el estudio; acotarlo a la organización adoptante.
12. Registro del equipo: la nota «Anexo F: 146-157» del libro de páginas es «146»; la entrada 7.1 de c-249 describe un `12:60` que no es el final; el SHA256SUMS de `analisis_regimen_c249` falla en un checkout de Windows con `core.autocrlf=true` (fin de línea), lo que conviene declarar en el README de `evaluation/` o cubrir con `.gitattributes`.

**De forma:**

13. Separador de miles uniforme en `07:325-333` y `07:377`; «F1 macro de umbral» (`01:36`) frente a «macro-F1 de umbral» (resto); remisión fuera de la oración en `08:62`; expandir «LLM» en su primera aparición (`01:66`); glosario: agregar JAIIO, CSV, PDF, IEEE y ACM, y quitar URL, VoIP y OAuth2 si no se usan en el cuerpo; declarar en la tesis (Anexo B o Nota de versiones) la renuncia al tope de 100 páginas con su fundamento, hoy solo en el registro; revisar la «Ş» de Şenerkek en la p. 131 del PDF.
14. Bibliografía: revista de `Powers2011_evaluation`; año de `Paramesh2019_it_service_desk` con la nota de edición impresa; claves de las cuatro entradas «s. f.»; página de origen de cada cifra de Paket (2024) y de Revina (2020) en el texto o en la entrada.

---

## Consideración final

Hace un día el dictamen anterior señalaba «los últimos lugares» donde el reencuadre no había llegado y dos lugares donde el registro del equipo contradecía al texto. La versión `v1.6.4` llegó a casi todos: el Resumen declara el escenario, la composición y el laboratorio; el método describe el instrumento que hay y no el que no hay; la sub-hipótesis 2 se decide con una regla que se enuncia igual en cinco capítulos; la lectura por régimen está escrita con cifras recomputadas por un script con pruebas; el capítulo legal valora la brecha del artículo 5 en vez de omitirla; el marco teórico y el estado del arte cerraron sus huecos; y la bibliografía está limpia. Es la ronda en que más recomendaciones se atendieron, incluidas las de forma, y la nota lo refleja.

Lo que este dictamen encuentra es de otra naturaleza, y conviene decirlo con precisión para que no se lea como una repetición. No es que el reencuadre no haya llegado a un pasaje; es que dos de las respuestas que los autores dieron en las compuertas, y que la tesis transcribió de buena fe, no resisten el cotejo con lo que el propio repositorio y el propio documento contienen. La explicación de los 145 incidentes del dashboard no coincide con la curva que la tesis imprime dos capítulos antes. La identidad entre titulares y responsables no vale para los familiares y conocidos que la misma oración incorpora como reportantes. Y el rótulo «prefijado» con que se cierra la discusión de la sub-hipótesis 2 no coincide con la definición que el prerregistro versionado dejó escrita un mes antes. A eso se suman un registro de compilación que, dentro del tag, describe la versión anterior, y un tamaño de muestra publicado con la etiqueta «a ratificar» todavía puesta en el registro.

Estas cosas comparten una causa, que es la cadencia: seis compuertas presentadas, respondidas y aplicadas en cinco horas, el mismo día de la release. El método de compuertas, que esta serie de dictámenes ha elogiado, funciona cuando la respuesta de los autores se coteja con la evidencia antes de escribirse. En esta ronda no hubo tiempo para eso, y lo que entró fue la memoria de los autores en lugar del registro. Ninguna de las correcciones que quedan exige medir nada: exigen abrir una base, un export, un acta y un diseño archivado, y escribir lo que hay. Con eso, y con los rótulos honestos de las recomendaciones 3 y 6, el documento queda en el estado que esta serie viene describiendo como alcanzable: un prototipo real, con cifras reproducibles desde artefactos versionados, evaluado con honestidad sobre un corpus cuya procedencia está dicha hasta el final, dentro de un escenario que se declara ficticio en cada lugar donde se usa, y con un capítulo legal que analiza su propia debilidad sin contradecir a sus propias figuras.

---

## Calificación sugerida según la rúbrica de la cátedra

Se aplica la *Rúbrica de Evaluación de Tesis de Ingeniería* con las advertencias habituales de la serie: las ponderaciones suman 115, el décimo criterio (defensa oral, peso 10) no es evaluable y la nota del documento escrito se computa sobre los nueve criterios restantes (peso 105).

| Criterio | Peso | Puntaje | Fundamento |
|---|---|---|---|
| 1. Definición del problema | 15 | 8,5 | Pregunta e hipótesis falsables; Resumen con escenario, composición y laboratorio; `01:38` y `01:72` corregidos; regla de la sub-hipótesis 2 coherente entre capítulos. Resta: el rótulo «prefijado» frente al prerregistro de c-167; `01:26` y `01:76` sin reencuadrar; residuo de `10:6`. |
| 2. Justificación y relevancia | 10 | 8,5 | Justificación académica sólida y fuentes verificadas; «estos indicadores justifican» y `03:24`, `03:90-92` acotados. Resta: la dimensión organizacional sigue apoyada en premisas y en «la experiencia de los autores» (`08:74`). |
| 3. Marco teórico y revisión bibliográfica | 15 | 9,0 | Modelo económico y métodos estadísticos incorporados; duplicados retirados; ficha de Paket completa; criterio temporal explicado; fuentes primarias verificadas. Resta: «once ejes»; `02:28`; criterio de idioma del protocolo; cifras de Paket y Revina no verificables por terceros. |
| 4. Metodología de investigación | 20 | 7,5 | Avances reales: instrumento descrito como es, ventana y composición como declaraciones, octava amenaza, brecha del artículo 5 analizada, fórmula única de reportantes. Resta: `11:34` contradicho por las Figuras 4 y 5; `11:46` falso para el círculo; tratamiento de terceros sin base; `A1` frente a par; carga de 10 s frente a casos de 10 s; acta T2 frente a `11:36`; «exclusivamente en su entorno operativo diario». |
| 5. Desarrollo técnico o experimental | 15 | 9,0 | Sistema funcional, documentado y reproducible; 68 rutas citadas existentes y versionadas; arnés de carga y sonda con evidencia; recomputo por régimen con script y pruebas. |
| 6. Resultados y análisis | 10 | 8,5 | 55 cifras reproducidas; lectura por régimen y nivel 5 escritos; sub-hipótesis 2 ordenada; síntesis con la regla y el dato post hoc en filas distintas. Resta: 0,854 por 0,853; «cota superior por redondeo» sin la carga estimada; régimen asignado por canal sin declararlo; `08:64`. |
| 7. Conclusiones y aportes | 10 | 8,5 | Veredictos coherentes; OE2 separado; aportes con la coautoría; «técnicamente integrable»; escenario que «solo dimensiona». Resta: fila del OE3 frente a `09:40`; «eficiente»; `09:48`; `09:52`; coautoría de los 119 ausente del Resumen, `08:50` y `09:54`. |
| 8. Redacción académica y estructura | 5 | 7,5 | Glosario reorganizado, flotantes en su anexo, portada con versión, 44 flotantes citados. Resta: 157 páginas con la renuncia solo en el registro; orden del capítulo 11; «once ejes»; separador de miles; registro del tag con la versión anterior. |
| 9. Uso de referencias y normas de citación | 5 | 9,5 | 93 entradas sin huérfanas; 44 DOI y 3 arXiv verificados; Decisión 2003/490/CE y «s. f.» corregidos; APA 7 uniforme. Resta: variantes de revista y año en dos entradas; páginas de Paket y Revina. |
| 10. Defensa oral | 10 | — | No evaluable. |

**Cálculo.** 8,5 × 15 + 8,5 × 10 + 9,0 × 15 + 7,5 × 20 + 9,0 × 15 + 8,5 × 10 + 8,5 × 10 + 7,5 × 5 + 9,5 × 5 = 887,5. Dividido por el peso efectivo (105): **8,45**.

**Calificación sugerida del documento escrito: 8 (ocho) por redondeo; 8,45 ponderado.**

**Relación con el dictamen anterior (8,19 para `v1.6.3`).** La suba de 0,26 puntos supera la proyección de 8,38 que aquel dictamen hacía para sus seis recomendaciones necesarias, porque el equipo atendió además las ocho de consistencia y forma y porque el marco teórico y el estado del arte mejoraron más de lo previsto. No sube más porque el criterio 4 se mantiene en 7,5: las dos inexactitudes de veracidad que aquel dictamen señalaba (planilla y titularidad) se reemplazaron por dos nuevas (cronología frente a las figuras; titular = responsable frente al círculo), y la decisión sobre la sub-hipótesis 2 vino con un rótulo que el prerregistro desmiente.

**Proyección tras las recomendaciones necesarias de este dictamen** (1 a 6). El criterio 1 pasaría a 9,0, el 4 a 8,5 y el 8 a 8,0: 917,5 sobre 105, **8,74**.

**Proyección con defensa oral** (sobre 115, partiendo de 887,5): con una defensa de 7, la nota final resulta 8,33; con 8, 8,41; con 9, 8,50; con 10, 8,59.

**Sobre la escala del tribunal.** La devolución de cuarta instancia proyectaba 7,5 para una versión con R-01 a R-07 aplicados y el flujo manual declarado como laboratorio. `v1.6.4` cumple esas condiciones, responde las preguntas de procedencia y agrega la lectura por régimen que el tribunal no había pedido. En esa escala, que pesa más la metodología, una lectura entre 7,5 y 8 sigue siendo la razonable, y las recomendaciones 1 a 3 de este dictamen son lo que un tribunal que abra las Figuras 4 y 5 y el diseño de c-167 preguntará antes de conceder el extremo superior.

---

## Anexo del dictamen: evidencia verificada

### A. Cronología de la release

| Momento (24-11-2026, −0300) | Hecho | Evidencia |
|---|---|---|
| 13:00:00 a 16:54:04 | Seis commits aplican las compuertas OQ-01 a OQ-06 (`c8ac511f`, `91a33eaf`, `56fa9cb8`, `0c9fc009`, `bdc01401`, `37feb74c`). | `git log v1.6.3..v1.6.4` |
| 17:09 a 17:13 | Reducción de los capítulos 2, 4, 5 y 6 (−3,1 páginas medidas). | `0a62e00d`, `c81577ea`, `a8d0910c` |
| 17:32:38 | Script, prueba y JSON por régimen (`89580b65`) y reencuadre (`90b497e0`) en el mismo segundo: el RED antes del GREEN no se distingue en el historial. | `git log --format=%ai` |
| 17:56 y 18:10 | Grupos 7 a 9; barreras de flotantes y «s. f.» (157 páginas). | `c1df1f2f`, `76ec9603` |
| 18:19:39 | C3 `f05ef2d6`: «release v1.6.4». Su `compilacion.md` sigue diciendo «release v1.6.3; C4, hash consignado», 158 páginas, SHA `f6bebd9e…`. Su `main.pdf`: 157 páginas, SHA `0c208da8…`, Anexo B sin hash. | `git show v1.6.4:…/compilacion.md`; `pdftotext` |
| 18:20:11 | Objeto de tag `1ccd36e1` sobre C3 y C4 `c64832fc` («consignar el hash de la release v1.6.4 en compilacion.md»), el mismo segundo. | `git cat-file -p v1.6.4`; `git log` |
| 18:22 a 18:40 | Archivo de c-249, merge a `main` (`52e77723`, con merge commit), cierre de la tarea 10.6, sincronización de Engram. | `git log` |
| — | `origin` tiene `v1.6.4` en `1ccd36e1` y `v1.6.3` en `7da7f1aa`, iguales al local; `v1.6.2` y `v1.6.3` no se movieron. | `git ls-remote origin` |
| — | `main.pdf` del tag = `main.pdf` de `main` = `tesis_ultima_version.pdf`; `main.log`, `main.aux` y `main.blg` están ignorados por git, de modo que los avisos de compilación solo constan en `compilacion.md` (0 errores, 0 referencias indefinidas, 8 overfull de hasta 6,9 pt, biber limpio). | `sha256sum`; `git check-ignore -v` |
| — | Inventario de asistentes: `git rev-list --count f05ef2d6^` = 1278; 165 commits con `Co-Authored-By`. Coincide con `12:255`. | `git log` |

### B. Pasajes con contradicción interna o con el registro, en `v1.6.4`

| Archivo:línea | Pasaje | Problema |
|---|---|---|
| `11:34` | «corresponden a los 119 casos de la corrida del corpus del 2026-10-02 y a 26 registros de prueba del 2026-10-13 … No hay registro de envíos a la API en ese intervalo» | Figura 5: puntos distintos de cero el 29-09, 30-09 y 1-10; pico del 2-10 ≈ 130; ≈ 2 el 13-10. Figura 4: dos tickets del 13-10; `#00156` a `#00162` ausentes. |
| `11:46` | «titulares de los datos y los responsables del tratamiento son las mismas personas» | Reportantes incluyen «las personas de su círculo» (familiares y conocidos, OQ-02 (1)); sus `ID USUARIO` constaban en los originales (`11:18`). |
| `01:34`, `04:109`, `07:185` | «regla y denominador prefijados» para 25/200 | c-167 D7 (30-10-2026): tasa = casos con ≥ 1 intervención / casos de la corrida = 147/200; el numerador de 25 es posterior a los datos. |
| `12:60`, `12:62` | «el hash se consigna en `compilacion.md` … la referencia verificable de la versión entregada es el tag y ese registro» | En el árbol del tag, `compilacion.md` describe `v1.6.3` (158 pp., SHA `f6bebd9e…`). |
| `10:38` | «mínimo de 30 reasignaciones … precisión del orden del 10 %» | Desvío de 54 s en los 24 cambios: ±19 s (28 %) con n = 30; registro c-249: «a ratificar por los autores». |
| `04:97` frente a `04:16`, `04:46` | «llevado en vivo por `A1`» frente a «`A1` o `T1` según el turno» y «cronometraron por pares» | Autoría del registro contradictoria. |
| `04:89`, `04:131` frente al corpus | carga fija «del orden de 10 s» sumada a cada caso | `R037`, `R186`, `R187`, `R198` valen 10 s en total. |
| `04:117`, `09:28` | `R017` (72 s) «la única medición exacta» | Incluye la carga estimada; es el único valor no redondeado. |
| `04:46` | «recogidos … exclusivamente en su entorno operativo diario» | Reportantes incluyen familiares y conocidos. |
| `01:76`, `09:52` | «un único entorno operativo, del sector servicios» | Ídem. |
| `11:36` frente a `acta-consentimiento-t2.md:7-8` | «la única documentación del 2-10 es el acta redactada el 17-11» frente a «consentimiento verbal prestado y documentado el 2026-10-02» | Acta creada el 17-11 (`efef2952`); fecha de firma agregada el 22-11 (`b5554673`). |
| `09:26` frente a `09:40` | OE3 «No sostenida» frente a «se alcanza parcialmente» | Escala de hipótesis en la columna de cumplimiento. |
| `01:48` | el umbral «constituye el criterio de éxito de este objetivo» | El OE2 se partió en dos filas (`09:24-25`). |
| `10:6` | «no concluyente con estimación puntual por encima de la cota» | Con 25/200 la estimación (12,5 %) está por debajo. |
| `10:6` frente a `10:36` | «el orden de las subsecciones siguientes los respeta» | La de primer nivel aparece después de cuatro de segundo nivel. |
| `09:48` | «corpus propio de la organización» | Organización retirada por el reencuadre. |
| `09:6` | «resultó operativa y eficiente» | Subsidiaria de eficiencia sin contraste (`01:38`). |
| `00r:8`, `08:50`, `09:54` frente a `04:129`, `09:25` | coautoría solo sobre las 81 frente a los 200 casos reescritos | Propagación incompleta de R-02. |
| `12:149`, `12:241` | «redactadas por los autores» | Frente a «uno de ellos» en `04:46`, `08:50`, `09:25`. |
| `08:18` | «IC [0,708; 0,854]» | Artefacto: 0,853456. |
| `08:64` | «línea~98» para p = 0,3438 | El p está en la línea 101. |
| `08:118` | remite a `subsec:estudios-replicacion` | Existe `subsec:medicion-costo-reasignacion`. |
| `02:6` | «once ejes temáticos» | Doce subsecciones. |
| `11:16` | «no dispensa el deber de información del artículo 6» | En un régimen declarado sin dato personal. |
| `11:122` | controles apoyados en «la base de licitud del artículo 5 … [y] el instrumento … del artículo 12» | Ambos declarados inexistentes para el estudio. |
| Figura 11 | barra «Campaña automatizada (sep-oct)» | Texto: octubre de 2026. |

Pasajes revisados y conformes: `00r:8`, `00r:10`, `00r:12`, `01:16`, `01:18` (parámetro), `01:22`, `01:38`, `01:42`, `01:62`, `01:72`, `02:12`, `02:20`, `02:98-104`, `03:8`, `03:22`, `03:24`, `03:47`, `03:49`, `03:90-92`, `04:46` (universo, composición, ventana, laboratorio), `04:54`, `04:89`, `04:131`, `06:38`, `06:60`, `07:10`, `07:24-26`, `07:38`, `07:154`, `07:185`, `07:377`, `08:8`, `08:18` (salvo el redondeo), `08:42`, `08:50`, `08:62`, `08:68`, `08:72`, `08:118` (rótulos), `09:24-25`, `09:48` (integrable), `09:50`, `10:22`, `10:26`, `11:12`, `11:32`, `11:36`, `11:44`, `12:60` (sin hash, coherente con la regla A), `12:151`, `12:157`, `12:245`, `12:255`.

### C. Verificación aritmética

Recómputo independiente con Python 3.13 puro (sin numpy ni scipy; el bootstrap con el generador de la biblioteca estándar, por lo que sus intervalos difieren en ≤ 0,1 punto) sobre `data/corpus_evaluacion_pseudonimizado.json`, `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`, `evaluation/data/campana/{doble_etiquetado,brazo_manual,intervenciones}.csv`, `corpus_campana.json`, los `sidecar_*.json`, los tres JSON de carga, los dos CSV de facturación y los JSON de análisis de c-214, c-220, c-236 y c-249. Los separadores de `sectores_adicionales` son «|». «Coincide» admite la diferencia de redondeo a la cifra publicada.

| Cifra | Texto | Recomputado | Coincide |
|---|---|---|---|
| Tiempo manual | 61,6; 50,0; 44,9; 10–300 (`07:38`) | 61,585; 50,0; 44,896; 10–300 | Sí |
| Tiempo automatizado | 17,76; 17,47; 13,52; 0,525–65,834 | idénticos | Sí |
| Reducción | 71,2 %; mediana 65,1 %; IC [67,2; 74,6]; diferencia [37,93; 50,33] | 71,16 %; 65,06 %; [67,1; 74,6]; [37,92; 50,33] | Sí |
| Wilcoxon | W = 363; T⁺ 19.737; p 3,08e-32; r 0,9639; d_z 1,00; 188/12 | idénticos | Sí |
| Por canal (`07:74-76`) | medias, reducciones, p y d_z de los tres canales | idénticos | Sí |
| Matriz de confusión; 147/200 [0,670; 0,791]; laxa 179 | — | idénticos | Sí |
| Macro-F1 0,6508 / 0,5207; F1 por clase | — | 0,65084 / 0,52067; idénticos | Sí |
| Etapas 97/131, 50/69; canales 53/81, 51/66, 43/53; multietiqueta 49/81, 15/53 | — | idénticos | Sí |
| Régimen (a) 94/119 = 0,790 [0,708; 0,854]; (b) 53/81 = 0,654 [0,546; 0,749] | `08:18` | [0,7082; 0,8535]; idéntico | (a): 0,853, no 0,854 |
| Bandas de confianza; 124 < 0,70; 46 ≥ 0,90 con 13 errores; 53 errores (32 laxos) | — | idénticos | Sí |
| AUROC 0,5168 [0,3796; 0,6528]; ECE 0,1868; Brier 0,2362; confianza media 0,9114; 24/7/35/3 | `07:233`, `07:240` | 0,51684; resto en el JSON de c-214 | Sí |
| Barrido de umbrales 45 (0,711), 38 (0,737), 3 (1,000) | `07:242` | idénticos | Sí |
| κ 0,5569; p_o 0,69; p_e 0,30; PABAK 0,6125; 138 consensos; 116/138 | — | 0,55686; 0,69; 0,30045; 0,6125; 138; 116 | Sí |
| Consenso: 110/138 [0,722; 0,856]; 109/138; laxas 125 y 117; 38/62; macro-F1 0,757 | — | idénticos; 0,75725 | Sí |
| Intervenciones 147 (66 + 81 + 0); 25 cambios (14 telefonía, 11 correo); 122 = 83,0 % / 61,0 % | — | idénticos | Sí |
| 25/200 [8,6; 17,8]; 25/147 [11,8; 23,9]; binomial 0,28 / 0,49 | — | [0,0861; 0,1780]; [0,1179; 0,2390]; 0,2796 / 0,4882 | Sí |
| 85 confirmaciones con consenso (11 incorrectas); 13 cambios con consenso (9/1/3) | `07:187` | idénticos | Sí |
| Proporción del tiempo 0,5307 [0,4407; 0,6111]; cobertura 0,9388 | `07:189` | idénticos | Sí |
| O1 20,1 (9,2) / 13,3 / 33,8 % / 9,8e-7 / 0,54; O2 76,6 (21,4) / 15,5 / 79,7 % / 9,0e-20 / 1,00; agregado 47,6 / 14,6 / 69,3 % / 3,0e-28 / 0,90; 20 dobles (20,1 y 92,8) | `07:297-307` | idénticos | Sí |
| Exactitud manual 71/80, 54/71, 125/151, laxa 130/151; 13 dobles con consenso; 13 casos en vivo distintos (7 + 6) | `07:309` | idénticos | Sí |
| Spearman −0,0628 (p 0,51); −0,3604; MDE 0,276 | `07:311` | −0,06278; −0,36036; 0,27625 | Sí |
| Carga (8 niveles); caída 9,8 %; cocientes 19,5 y 20,06; 1,36; e2e 246,0 y 4118,0 | `07:325-342` | idénticos | Sí |
| Sonda (8 filas); cocientes originales 11,27 / 5,04 / 3,47 / 1,76; determinístico 1782,9; nivel 5 de N8N 3660,4 / 7545,7 / 5024,7 | `07:360-379` | idénticos | Sí |
| Facturación 455.309 (444.634 + 10.675); USD 0,373501; 286.259 vs 281.568 (4.691, 1,7 %); 2.064 vs 764 (2,7); precio 0,75 / 3,75 | `07:372` | idénticos | Sí |
| Balance 25,47; +18,7 [12,9; 24,1]; [6,7; 28,2]; a* 43,1 [33,6; 53,7]; c* 898,8; c 69,5 [33,4; 106,6]; rejilla | `08:78-118` | idénticos | Sí |
| Costo de API ≈ 1 USD; 32,2 h; −10 s → 65,6 % | `08:22`, `08:72` | 0,59 USD; 32,21 h; 65,57 % | Sí (orden) |
| McNemar 96/130 vs 88/130, p 0,1516; ablación 50/69 vs 46/69, p 0,3438; 0,7405 → 0,5270 | `08:10`, `08:64` | idénticos (p en la línea 101 del reporte) | Sí |
| Mínimo de 30 reasignaciones con «precisión del orden del 10 %» | `10:38` | con s = 54 s, ±19,4 s (28 %); 10 % exige n ≈ 230 | **No** |
| 165 de 1278 commits | `12:255` | 165 / 1278 | Sí |

Comprobaciones de artefactos: las 68 rutas citadas con `\path{}` o `\texttt{}` existen, no están vacías y están versionadas (los `corpus_resultados*.json` tienen regla de negación en `.gitignore`); `doble_etiquetado.csv` tiene 400 registros; `corpus_resultados_web_correo.json` tiene 118 casos y el faltante es `R001`; `corpus_resultados_telefonia.json` coincide en los 81 tiempos (25 el 5-10 y 56 el 6-10); los dos SHA de `analisis_regimen_c249.SHA256SUMS.txt` corresponden a los blobs del tag; los CSV de facturación tienen los SHA `f860b5cd…` y `636fdd70…` citados. No verificable: la equivalencia régimen = canal; la hora del consentimiento verbal del 2-10 frente a la ingesta de ese día (20:50, −03); la magnitud de la carga estimada; la regeneración del JSON de c-249 sin scipy. Observación de reproducibilidad: en un checkout de Windows con `core.autocrlf=true`, `sha256sum -c` falla sobre los archivos de c-249 y sobre tres de sus cinco entradas por el fin de línea; en los blobs todo coincide.

### D. Verificación bibliográfica

Método: 44 DOI consultados en Crossref u OpenAlex (29 respuestas completas; el resto por la URL del DOI), 3 arXiv en su API, EUR-Lex para la Decisión 2003/490/CE, y todas las URL resueltas con `curl -L`. Resultado: ninguna referencia inexistente; 0 huérfanas; biber sin advertencias; sin duplicados ni caracteres rotos en el `.bbl`.

| Entrada | Vía | Existe | Observación |
|---|---|---|---|
| paket2024itservice | Crossref, OpenAlex | Sí | 4 autores, UBMK 2024, pp. 135-140; resumen confirma turco, 172 clases, BERT > LLM; cifras por modelo no verificables sin la copia |
| Revina2020_it_tickets | Crossref | Sí | IEEE Access 8; exactitud 1,000 no verificable (descarga bloqueada) |
| Paramesh2018_csitss | Crossref + arXiv 2103.15822 | Sí | 10.742 tickets; 90,60 / 91,81 / 92,04 % verificados en el PDF de arXiv |
| Paramesh2019_it_service_desk | Crossref | Sí | Crossref: 2018; `.bib`: 2019 (edición impresa) |
| Decision2003_490_CE | EUR-Lex | Sí | Corregida: 30-06-2003; DO L 168 de 5-07-2003, pp. 19-22 |
| Powers2011_evaluation | arXiv 2010.16061 | Sí | Revista: «International Journal of Machine Learning Technology» |
| MosqueiraRey2023_human_in_the_loop | Crossref | Sí | En línea 2022; vol. 56(4), 2023 |
| liu2025tickit, zangari2023ticket, colavito2025benchmarking, mayorrocher2026spanish, ramonferrer2026tripletotext, bernalbeltran2025mexicanspanish, grandury2025laleaderboard, xuan2025mmluprox, ahuja2023mega, lai2023okapi, zhang2023multilingual | Crossref | Sí | Sin discrepancias |
| Cohen1960, Landis1977, Fleiss1969, Wilcoxon1945, Shapiro1965, McNemar1947, Hodges1956, Brier1950, Kerby2014, Tsoumakas2007, NiculescuMizil2005, McCambridge2014, Guo2017, Zhao2021, Radford2023, Tian2023, Varshney2022, Ji2023, Amershi2019, Shneiderman2020, Zanzotto2019, Wu2022, Efron1994, NIST2024, Fielding2002, Galup2009, Sokolova2009, Virtanen2020, Wilson1927, Pedregosa2011, Brown2020, Vaswani2017, Touvron2023, Opitz2019 | Crossref, arXiv, PMLR, JMLR | Sí | Sin discrepancias |
| Xiong2024, Chen2024 | OpenReview | Sí (URL) | OpenReview bloquea la descarga automatizada; Chen coincide con arXiv 2305.05176 |
| Normas y leyes (GDPR2016, Ley25326_2000, Decreto1558_2001, DNPDP2016, AAIP2023), ISO 27001/27002/27701, SEPyME2026, APA2017, Jurafsky2026 | URL | Sí | Plausibles; contenido no cotejado salvo la Decisión |
| Documentación (Apache, n8n, PostgreSQL, FastAPI) | URL | Sí | Ahora «s. f.» con fecha de consulta; las claves conservan «2024» |
| Páginas de proveedor (Google ×3, DigitalOcean, Zendesk, Freshdesk, ServiceNow, Docker, Atlassian, osTicket, Twilio, 12factor) | URL | Sí | Páginas vivas; `ai.google.dev/gemini-api/docs/pricing` redirige a `aistudio.google.com/docs/pricing` |
| Gomez2026_repositorio | GitHub | Sí | «Versión 1.6.4», `urldate` 2026-11-24 |
| Libros sin DOI (Crispin, Date, Hernández Sampieri, Hohpe, Ladas, Pressman, Rabiner, Russell, Stallings, OGC, Cohen 1988) | — | No verificable por API | Ediciones habituales |

Distribución temporal: mediana 2020; 42 entradas posteriores a 2020; 36 de 2023 en adelante; 16 de 2026, de las cuales 12 son páginas de proveedor o sitio; 12 anteriores a 2000 (clásicos estadísticos y de ingeniería).

### E. Figuras cotejadas

| Figura | Archivo | Resultado |
|---|---|---|
| 4 (panel de administración) | `panel_admin.png` (21-10-2026, sin cambios desde `v1.6.3`) | Ordenada por ID descendente: `#00164` y `#00163` del 13-10; `#00155` a `#00146` del 2-10 entre las 20:33 y las 21:01. Cola de revisión: 94. Incompatible con «26 registros de prueba del 13-10». |
| 5 (dashboard) | `dashboard.png` (ídem) | Rango 21-09 a 21-10; 145 incidentes; 64,8 % de revisión; promedio 4,7 por día. Curva diaria: ≈ 0 hasta el 28-09; puntos distintos de cero el 29-09, 30-09 y 1-10 (≈ 12 en conjunto); pico del 2-10 ≈ 130; ≈ 2 el 13-10. Incompatible con `11:34`. El pie de la figura es correcto. |
| 6 (boxplot) | `boxplot_tiempos.pdf` | Medianas 20,00 / 1,26; 50,00 / 25,82; 72,00 / 18,70: coinciden con `07:74-76`. |
| 11 (cronograma) | `cronograma.png` | Hitos 24-09, 2-10, 5-6-10 y 19-10 coinciden; la barra dice «Campaña automatizada (sep-oct)» y el texto, «octubre». |
| 1 (arquitectura) | `arquitectura_sistema.png` | «Gemini solo si el filtro no resuelve» describe la clasificación; la transcripción telefónica siempre pasa por la Gemini API (`11:28`). Menor. |
| 12 a 14 (flujo N8N) | `flujo_n8n_{a,b,c}.png` | En las pp. 144-146, antes del Anexo F (corregido). No se cotejó su contenido nodo por nodo. |
