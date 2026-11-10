# DICTAMEN DE EVALUACIÓN ACADÉMICA

**Documento evaluado:** *Automatización inteligente del registro de incidentes en mesas de ayuda empresariales mediante orquestación de flujos con N8N y procesamiento de lenguaje natural basado en modelos de lenguaje grandes*. Trabajo Final de Carrera, Tecnicatura Universitaria en Programación, Universidad Tecnológica Nacional, Facultad Regional Mendoza. Autores: Luca Gomez, Carla Bustos y Gonzalo Sevilla. Directores: Prof. Alberto Cortez y Prof. Ariel Enferrel.

**Versión examinada:** versión de trabajo v10, release `v1.2.16`. Es un tag anotado sobre el commit `ca3c88510be5b1484ed413a8de8bcdffccedc417`, del 9 de noviembre de 2026 a las 19:47 −03. El examen usa:

- las fuentes LaTeX de `docs/Tesis/v10 (IA)/paper/sections/`;
- el PDF versionado en el tag (`paper/main.pdf`, SHA-256 `72a3dd11…`, igual al que registra `compilacion.md`): 118 páginas;
- la bibliografía `Bibliography_base.bib`, con 91 entradas.

Entre el tag y la cabeza de `main` (`49b1f96`), las fuentes de la tesis solo difieren en la línea del Anexo B que consigna el hash.

**Fecha del dictamen:** 9 de noviembre de 2026.

**Alcance del examen:**

- lectura íntegra del documento: resumen bilingüe, secciones 1 a 11 y anexos;
- cotejo, palabra por palabra, de las diferencias entre `v1.2.13` y `v1.2.16` (changes `c-192`, `c-193` y `c-194`);
- seguimiento de cada recomendación y de cada ítem del inventario del dictamen anterior;
- cotejo con el repositorio: PDF del tag, flujo N8N, código y artefactos del análisis de la campaña complementaria, registro de correcciones, plantilla de consentimiento;
- verificación bibliográfica externa de los puntos pendientes, con Crossref y lectura de las fuentes accesibles.

**Antecedentes:** noveno dictamen de la serie iniciada el 20 de octubre de 2026. El anterior, del 9 de noviembre de 2026 sobre `v1.2.13`, formuló tres recomendaciones de fondo (A1 a A3), cuatro de consistencia (B1 a B4), dos de forma (C1 y C2) y un inventario de 21 ítems. Calificó el documento escrito con 9,00. Los autores lo atendieron en tres releases sucesivas del mismo día: `v1.2.14` (`c-192`), `v1.2.15` (`c-193`, nivel pago y consentimiento) y `v1.2.16` (`c-194`, residuales de forma).

**Nivel de exigencia:** criterios de evaluación universitaria argentina (CONEAU), calibrados al nivel de un trabajo final de tecnicatura.

---

## VEREDICTO GENERAL

**APROBADO CON OBSERVACIONES.**

La versión examinada resuelve la mayor parte de lo pedido y no presenta ninguna regresión en las cifras. Tres de las cuatro observaciones de fondo del dictamen anterior quedan cerradas por completo:

- **Trazabilidad del PDF entregado.** El PDF del tag ya no imprime el hash de otra release. En su lugar dice que el hash "se consigna en el commit que sigue al tag" y da la orden de verificación (`git rev-list -n1 v1.2.16`). El PDF de `main` imprime `ca3c885…`, que es el commit del tag. Es la solución de `v1.2.12`, ahora estabilizada en tres releases consecutivas.
- **Justificación (1.6).** Distingue el acuerdo de los dos analistas originales (κ = 0,87, sin intervalo) del doble etiquetado nuevo de `E1` y `E2` (κ = 0,5569, moderado, con intervalo).
- **Conjunto de verdad laxo del brazo manual.** La sección 8.7 lo define como "el consenso de `E1` y `E2` más la intersección de los sectores adicionales que marcaron ambos etiquetadores". Coincide con `evaluation/campana.py` y con el 130/151.

También quedan resueltos:

- el denominador de las confirmaciones (122 de 147, 83,0 %);
- la atenuación de Xiong et al. en el capítulo 3, que ahora reproduce fielmente la fuente;
- el "trigger de Twilio", aunque solo en parte;
- la fila "Lím." del Anexo I, escrita ahora como secuencia temporal;
- la nota de FrugalGPT, cuya publicación en TMLR (diciembre de 2024) acredita el sitio del primer autor.

El veredicto se mantiene con observaciones por tres razones. La primera es nueva y es la de mayor peso de este dictamen.

1. **El texto afirma que el repositorio conserva un registro del consentimiento que no existe.** La sección 7.5 dice que los cuatro participantes de la campaña complementaria fueron informados verbalmente y que "con posterioridad a su participación firmaron una confirmación escrita". Agrega: "El repositorio conserva la plantilla de la confirmación y el registro de que se recabó para los cuatro participantes".

   La plantilla existe (`docs/campana-medicion/confirmacion-posterior-consentimiento.md`, creada en el commit `f72e6c8` el 9-11-2026 a las 19:04). Su tabla de registro, en cambio, tiene vacías las columnas `fecha_informacion_verbal` y `fecha_confirmacion` de `E1`, `E2`, `O1` y `O2`. La plantilla manda completar el registro en el README de `evaluation/data/campana/`, y ese README no lo contiene. Ningún otro archivo versionado lo contiene.

   Este evaluador no puede saber si las firmas se obtuvieron, y no lo presume. Lo verificable es que la oración sobre el repositorio es falsa en el tag entregado. En un punto ético, un jurado que la compruebe leerá la discrepancia como una declaración no respaldada. El dictamen anterior había valorado como "veraz y preferible a una reconstrucción" la declaración de que no existía registro. La versión actual la reemplazó por una afirmación que el repositorio no sostiene.

2. **La segunda sub-hipótesis conserva la frase que el dictamen anterior pidió reformular.** La refutación quedó bien matizada en 8.3, 9.1 y la Tabla 18: la estimación puntual supera la cota, el intervalo [11,8 %; 23,9 %] la contiene y la prueba binomial exacta no la rechaza (p = 0,28, que este evaluador reproduce). Sin embargo, 8.3 sigue diciendo "Medirla en condiciones válidas exige una corrida con reportantes identificados". Si la medición no fue válida, no puede refutar. Además, la asimetría de la regla de tres vías se declara en los resultados, pero no en su definición (1.4 y 4.7), donde un lector la buscaría primero.

3. **El Anexo I deja de trazar el último dictamen.** El anexo sigue diciendo que la serie "comprende siete dictámenes" y traza cuatro. El repositorio versiona ocho, y el octavo, sobre `v1.2.13`, es el que motivó `c-192` a `c-194`. El diseño de `c-192` (D7) preveía "tabla de trazabilidad del dictamen del 9-11 sobre v1.2.13", y no se agregó. `verificar_matriz_trazabilidad.py` cuenta las mismas 171 filas que antes, sin sección para `c-192`. Es la primera vez desde `c-160` que un ciclo de correcciones no queda trazado en el documento.

Persisten, declaradas con precisión y sin computarse como incumplimiento, las limitaciones estructurales del diseño:

- métricas de clasificación dentro de la muestra; la validación fuera de muestra (`c-191`) está propuesta pero no ejecutada;
- tiempos automatizados de configuraciones anteriores a la evaluada;
- exactitud estricta (73,5 %) con un intervalo que queda entero por debajo del umbral del 85 %;
- efecto de orden no estimado;
- balance operativo condicional al costo no cronometrado de las reasignaciones.

---

## OBSERVACIONES DETALLADAS POR SECCIÓN

### 1. Estructura general del documento

**Cumple.** La organización es la canónica de un trabajo de investigación aplicada: resumen bilingüe, glosario, once secciones, referencias y nueve anexos. Las remisiones resuelven todas: el texto extraído del PDF del tag no contiene "??", y `compilacion.md` registra 0 errores, 0 referencias indefinidas y 7 cajas desbordadas (máximo 8,2 pt). El PDF del tag coincide byte a byte con el SHA-256 que declara ese resumen.

Defectos de forma:

- **Anexo I desactualizado** (observación 3 del veredicto).
- **Errata nueva** en 2.4 (`02-marco-teorico.tex:32`): "cuando los datos escasean o el dominio es ambiguo; Los autores de esta tesis infieren". La mayúscula tras punto y coma la introdujo `c-194` al partir la oración.
- **Extensión.** Se mantienen 118 páginas frente al tope de 100 que el propio equipo fijó. Es una decisión registrada y no se penaliza el cuerpo.

### 2. Claridad y formulación de la hipótesis

**Cumple, con observaciones.** La formulación sigue siendo la mejor de la serie: una hipótesis principal desdoblada en tres sub-hipótesis contrastables, con estadístico, hipótesis nula sobre diferencias pareadas, regla de decisión y criterio de falsación, más dos subsidiarias rotuladas como no contrastadas.

La segunda sub-hipótesis mejoró en lo sustantivo. El texto de 8.3 y de 9.1 consigna que el intervalo contiene la cota, que la prueba binomial no la rechaza y que "la lectura conservadora es que no se puede descartar un valor cercano al umbral". La Tabla 18 ya no afirma a la vez la refutación y la falta de medición válida.

Quedan dos puntos (observación 2 del veredicto):

- la frase "Medirla en condiciones válidas…" en 8.3;
- la asimetría de la regla de tres vías, que no se declara en 1.4 ni en 4.7.

La regla exige que el límite superior quede bajo 0,15 para declarar compatibilidad, pero refuta con la sola estimación puntual. Un lector que se detenga en 1.4 o en el resumen ("se refuta sobre los 147 casos revisados") no recibe esa advertencia.

La fórmula "no se puede descartar un valor cercano al umbral" también es imprecisa. Lo que el intervalo no permite descartar es que la proporción sea **inferior** a la cota (llega a 11,8 %), y eso es más fuerte que "cercano".

### 3. Definición y coherencia de los objetivos

**Cumple.** El objetivo general y los seis específicos están bien delimitados. La Tabla 18 cierra la matriz objetivo-evidencia-conclusión con grados honestos: uno no alcanzado, cinco alcanzados parcialmente y uno alcanzado. La fila del cuarto objetivo dice ahora "refutada sobre los casos revisados (25 de 147; el intervalo no excluye 0,15 y la regla del reportante acotó la revisión)". Es una formulación coherente.

La justificación académica (1.6) atribuye cada kappa al par que lo produjo, como se pidió. La fila del objetivo general acota la refutación a "los casos revisados", lo que satisface lo esencial de la observación anterior, aunque no nombra los canales.

### 4. Estado del arte

**Cumple.** El protocolo de revisión tiene seis bases, siete cadenas, dos fechas de corte y bitácora versionada, y declara la ausencia de repositorios regionales. Siete trabajos están sistematizados con métrica y condición. La brecha está acotada al alcance revisado. La caracterización de Xiong et al. (`03-estado-del-arte.tex:62`) dice ahora "sobreconfianza, valores concentrados en el extremo alto de la escala y que predecir las fallas sigue siendo un desafío", y la lectura de la fuente (arXiv 2306.13063) la respalda en sus tres partes. Los doce DOI cotejados en Crossref coinciden en título, primer autor y año.

### 5. Marco teórico

**Cumple, con una observación menor.** Los ocho ejes conservan su relación con decisiones de diseño verificables. La atribución a Galup et al. se redujo a la caracterización general de la disciplina, con `\parencite`.

La reformulación de Zanzotto (2019) separó, como se pidió, la inferencia propia de la fuente, pero cambió el peso de la atribución. Ahora dice que "Zanzotto reclama retribuir a quienes producen el conocimiento que usan los sistemas y sostener la supervisión humana". El resumen del artículo respalda la primera parte: el paradigma *HitAI* compensa a quienes aportaron conocimiento. No respalda la segunda, porque allí las personas son fuentes de conocimiento y no supervisoras. Este evaluador no pudo acceder al cuerpo del artículo. La afirmación debe paginarse o reducirse a lo que el resumen sostiene.

### 6. Desarrollo metodológico y propuesta (método, arquitectura, implementación y resultados)

**Cumple, con observaciones.** Concentra las fortalezas del trabajo y la observación 1 del veredicto.

*Fortalezas.*

- **Procedencia.** La procedencia de las tres corridas, la tabla de configuraciones verificada sobre tres revisiones y el orden real de la campaña complementaria siguen declarados con una precisión que excede la del nivel.
- **Recómputo.** Los valores nuevos o modificados se reproducen:
  - 122/147 = 0,830;
  - binomial exacta unilateral de H₀: p ≤ 0,15 con 25/147, p = 0,28;
  - tanh(2,80158/√(107 × 0,912)) = 0,276.
- **Hash del tag.** La trazabilidad del PDF del tag está resuelta y verificada: el texto extraído no contiene ningún hash de 40 caracteres, y el de `main` contiene solo el del tag.
- **Nivel pago.** Se declara que el comprobante de facturación queda en custodia del director y no se versiona porque contiene datos de la cuenta. Es una declaración razonable, y el jurado puede pedir verlo en la defensa.

*Observaciones de método.*

- **(a) Consentimiento de la campaña complementaria:** observación 1 del veredicto. Hay además una inconsistencia interna en la plantilla. Su encabezado describe el registro como `alias, rol, fecha_consentimiento`, y la tabla usa cinco columnas distintas.
- **(b) Efecto mínimo detectable del Spearman.** El texto adopta 9/π² y da ρ = 0,276. El análisis versionado (`analisis/resultados.json`, generado por `evaluation/campana.py:1593` con `ARE_WILCOXON_MINIMA`) sigue produciendo 0,2834. La cifra impresa ya no es la que produce el código del repositorio. El memo de números canónicos lo reconoce ("superado por c-192"), pero la tesis no. Hay que actualizar el código y regenerar el análisis, o declarar en 8.7 que el valor se recalculó fuera del análisis versionado.
- **(c) Cronometraje mutuo.** El ítem 12 del inventario anterior sigue sin atenderse. En los pares de la campaña 2026-10, el compañero que no registraba cronometraba. Por lo tanto, el observador de `A1` era `T1`, que es autor. La atenuación del efecto Hawthorne que 4.2 atribuye a `A1` es más débil de lo que el texto sugiere.

*Observaciones de implementación y trazabilidad.*

- **Disparador telefónico.** En 6.3 se reemplazó "trigger de Twilio" por "callback de grabación de Twilio", que sigue siendo inexacto. El callback de Twilio llega al backend. El disparador de N8N es el webhook `telefonia-handoff`, al que el backend entrega la transcripción, como describen 5.2 y 6.4 y como muestra `n8n/workflow.json` (nodo "Llamada telefonica", tipo `webhook`). La misma enumeración dice "tres disparadores", y el Anexo E enumera cuatro: correo, telefonía, formulario y notificación de clasificación. Conviene decir "tres disparadores de canal".
- **Dos nombres para la misma caché.** 8.7 sigue nombrando `predicciones_in_sample.json` y `predicciones_hybrid-v3_2026-10-07.json` sin decir que contienen las mismas 200 predicciones (ítem 14 del inventario anterior).
- **Memo de números canónicos.** `numeros-canonicos.md` conserva en las líneas 811-826 el estado "no concluyente" y en la línea 920 la definición del laxo por "unión". El memo no forma parte de la tesis, pero el Anexo I lo presenta como fuente de las correcciones.
- **Identificador VIS-005.** Se presenta como "regla de visibilidad y derivación por reportante no identificado". Es el quinto requisito de la especificación `incident-visibility` de c-82, un identificador interno que el jurado no puede resolver. Conviene decirlo así o retirarlo.

### 7. Conclusiones

**Cumple.** El capítulo responde a cada objetivo y sub-hipótesis con el alcance medido. La Tabla 18 es coherente consigo misma y con 8.3. Sigue siendo el capítulo con mejor relación entre lo que afirma y lo que la evidencia sostiene. El párrafo inicial resume la refutación de la intervención humana "sobre el denominador de los casos revisados" sin el matiz del intervalo. Es aceptable en una síntesis, porque la tabla que sigue lo consigna.

### 8. Propuestas de trabajos futuros

**Cumple.** Las líneas están priorizadas, y las prioritarias atacan defectos medidos. La sección 11.3 incorpora los dos requisitos pedidos para la nueva medición de la intervención humana. Falta el tercero que el dictamen anterior sugirió: dimensionar la muestra para que el intervalo pueda quedar por debajo de 0,15. Con una proporción cercana a la cota, ninguna muestra del orden de 150 casos permite declarar compatibilidad. La validación fuera de muestra tiene ahora un change propuesto (`c-191`, 150 casos, clasificador congelado y dos etiquetadores nuevos). Eso da a la línea 11.8 un plan concreto, aunque la tesis todavía no lo menciona.

La oración introductoria del capítulo 11 dice que la medición de la intervención humana "que la campaña complementaria de medición refutó". Lo refutado fue la sub-hipótesis, no la medición.

### 9. Bibliografía

**Cumple.** `verify_citations.py` da PASS: 91 entradas, 91 claves citadas en 151 comandos de cita, ninguna huérfana ni sin usar. `main.blg` no tiene avisos.

Correcciones atendidas:

- FrugalGPT lleva la nota "TMLR; versión previa: arXiv:2305.05176", y la publicación en TMLR de diciembre de 2024 la confirman el sitio del primer autor y el repositorio oficial del proyecto;
- la nota de Zendesk describe ahora una página de producto, sin "precios";
- la URL de Jurafsky y Martin responde y muestra la versión del 19 de agosto de 2026 que declara la entrada.

Residuos menores:

- Zanzotto, por la atribución de la supervisión humana y la falta de página (sección 5);
- la página de ServiceNow ITSM, que no respondió a la verificación automática;
- la denominación "Zendesk Suite" en la nota, que la página citada no usa.

---

## TABLA RESUMEN DE CUMPLIMIENTO

| Dimensión | Dictamen v1.2.13 (9-11-2026) | Presente dictamen (v1.2.16) |
|---|---|---|
| 1. Estructura general | Cumple (118 páginas; VIS; fila del Anexo I) | Cumple (Anexo I sin el octavo dictamen; errata en 2.4; 118 páginas) |
| 2. Hipótesis | Cumple, con observaciones | Cumple, con observaciones ("condiciones válidas" en 8.3; asimetría no declarada en 1.4 ni en 4.7) |
| 3. Objetivos | Cumple (atribución del kappa en 1.6) | Cumple |
| 4. Estado del arte | Cumple (residuo de Xiong) | Cumple |
| 5. Marco teórico | Cumple | Cumple (atribución a Zanzotto) |
| 6. Metodología y propuesta | Cumple, con observaciones | Cumple, con observaciones (registro de consentimiento inexistente; MDE distinto del análisis versionado; disparador telefónico; cronometraje mutuo) |
| 7. Conclusiones | Cumple, con observaciones (Tabla 18) | Cumple |
| 8. Trabajos futuros | Cumple | Cumple |
| 9. Bibliografía | Cumple (residuos menores) | Cumple (residuos menores) |

Las conclusiones pasan a "cumple" sin reservas. Ninguna dimensión queda en "cumple parcialmente". La observación de mayor peso ya no toca la validez de lo medido: toca la veracidad de una declaración ética sobre el repositorio.

---

## SEGUIMIENTO DE LAS OBSERVACIONES DEL DICTAMEN ANTERIOR

| Ítem del 9-11-2026 (v1.2.13) | Estado | Evidencia en `v1.2.16` |
|---|---|---|
| A1. Trazabilidad del PDF del tag | **Resuelto** | El PDF del tag no contiene hashes; da la orden `git rev-list -n1 v1.2.16`. El PDF de `main` imprime `ca3c885…`, que es el commit del tag |
| A2. Una sola lectura de la segunda sub-hipótesis | Resuelto en parte | Celda de la Tabla 18 corregida; 122 de 147 (83,0 %); intervalo y p = 0,28 en 8.3 y 9.1; objetivo general acotado a los casos revisados. Pendiente: "Medirla en condiciones válidas…" en 8.3; asimetría en 1.4 y 4.7 |
| A3. Atribución del kappa en 1.6 | **Resuelto** | κ = 0,87 de los analistas originales y κ = 0,5569 de `E1` y `E2`, separados |
| B1. Definición del laxo manual | Resuelto en la tesis | 8.7: "intersección". Pendiente en el memo (línea 920) |
| B2. Eficiencia del MDE del Spearman | Resuelto en el texto, con problema nuevo | 9/π² y ρ = 0,276, reproducido. El análisis versionado sigue dando 0,2834 |
| B3. Propagación de correcciones | Resuelto en parte | Xiong: resuelto. "Trigger de Twilio": sustituido por otra expresión inexacta. Consentimiento: sustituido (ver B4). Cronometraje mutuo, cachés y memo: no atendidos |
| B4. Hechos operativos | Resuelto en parte, con problema nuevo | Nivel pago: comprobante declarado en custodia del director. Consentimiento: el texto afirma un registro en el repositorio que está vacío (observación 1) |
| C1. VIS, fila "Lím.", Zanzotto | Resuelto en parte | Fila "Lím." como secuencia temporal; VIS expandida; Zanzotto separado en dos oraciones, sin página y con atribución reforzada; errata introducida |
| C2. FrugalGPT, Zendesk, URL | Resuelto | TMLR confirmado; nota de Zendesk ajustada; Jurafsky responde. ServiceNow no verificable |
| Trazabilidad del dictamen en el Anexo I | **Regresión** | "Siete dictámenes"; sin tabla para el dictamen sobre `v1.2.13`, prevista en `c-192` D7 |

---

## RECOMENDACIONES CONCRETAS Y ACCIONABLES

Las recomendaciones A deben resolverse antes de la defensa, las B son de consistencia y las C de forma. Ninguna exige nuevas mediciones de campo.

**A1. Hacer verdadera la declaración del consentimiento** (`11-aspectos-legales.tex`, sección 7.5).

- Si las confirmaciones están firmadas, completar el registro sin identidad (`alias, rol, fecha_informacion_verbal, fecha_confirmacion, custodia`) en el README de `evaluation/data/campana/`, como manda la plantilla, y citar ese archivo en 7.5.
- Si todavía no están firmadas, reescribir 7.5 en el tiempo que corresponda ("se recabará antes de la defensa") y retirar "firmaron" y "el registro de que se recabó".
- En cualquier caso, unificar las columnas del registro entre el encabezado y la tabla de la plantilla.

**A2. Cerrar la lectura única de la segunda sub-hipótesis.**

- 8.3: reemplazar "Medirla en condiciones válidas exige una corrida con reportantes identificados" por una condición de generalización: "extender la conclusión al formulario web y a reportantes identificados exige una corrida con …".
- 1.4 y 4.7: declarar, al definir la regla de tres vías, que es asimétrica y que "refutada" significa "la estimación puntual alcanza la cota", no un rechazo estadístico de p ≤ 0,15.
- 8.3 y 9.1: precisar que el intervalo no permite descartar una proporción **inferior** a la cota.

**A3. Trazar el octavo dictamen en el Anexo I** (`12-anexos.tex`, `sec:anexo-trazabilidad`). Corregir "siete" por "ocho" y agregar la tabla del dictamen del 9-11 sobre `v1.2.13`, con los changes `c-192`, `c-193` y `c-194`. Extender `verificar_matriz_trazabilidad.py` para que la cubra.

**B1. Alinear el MDE con el análisis versionado.** Actualizar `evaluation/campana.py:1593` para usar 9/π² (o una constante `ARE_SPEARMAN = 9/π²`) y regenerar `analisis/resultados.json`. Si no se regenera, declarar en 8.7 que 0,276 se recalculó fuera del análisis, cuyo valor es 0,2834.

**B2. Completar la propagación pendiente.**

- 6.3: "telefonía (webhook `telefonia-handoff`, al que el backend entrega la transcripción)" y "tres disparadores de canal".
- 4.2: consignar que en los pares de cronometraje el observador de `A1` era el autor `T1`.
- 8.7: decir que las dos cachés del 7-10 contienen las mismas predicciones.
- `numeros-canonicos.md`: actualizar las líneas 811-826 y 920.

**B3. Ajustar la atribución a Zanzotto** (2.4). Limitarla a lo que el artículo sostiene (retribuir a quienes aportan conocimiento) o paginar el pasaje que respalda "sostener la supervisión humana".

**C1.** Corregir "; Los autores" en 2.4. Presentar VIS-005 como requisito de la especificación de visibilidad de incidentes (c-82) o retirar el identificador. En el capítulo 11, decir que la campaña refutó la sub-hipótesis, no la medición.

**C2.** Agregar a 11.3 el requisito de dimensionar la muestra para que el intervalo pueda quedar por debajo de 0,15. Mencionar en 11.8 el plan de validación fuera de muestra si se ejecuta antes de la defensa. Quitar "Suite" de la nota de Zendesk y revisar la URL de ServiceNow.

---

## CONSIDERACIÓN FINAL

La serie de dictámenes muestra un trabajo que sigue mejorando en cada versión, y esta es la más sólida. El defecto que más se había repetido, el hash del PDF entregado, quedó estabilizado. La justificación y la definición del laxo manual dicen ahora lo que el código y los datos sostienen. La aritmética resiste un nuevo cotejo sin una sola regresión.

Lo que queda tiene un patrón distinto al de los dictámenes anteriores. Ya no son correcciones que olvidan dónde más se apoyaba el hecho corregido, sino declaraciones que se adelantan a su respaldo:

- 7.5 afirma un registro que el repositorio todavía no tiene;
- 8.7 imprime un MDE que el análisis versionado todavía no produce;
- el diseño de `c-192` prometía una tabla del Anexo I que no llegó.

En los tres casos la corrección es la misma: hacer que el repositorio diga lo que el texto afirma, o que el texto diga solo lo que el repositorio muestra. En un trabajo cuyo mayor mérito es la trazabilidad entre texto y evidencia, ese criterio debe aplicarse con más rigor en la sección ética.

---

## CALIFICACIÓN SUGERIDA SEGÚN LA RÚBRICA DE LA CÁTEDRA

Se aplica la *Rúbrica de Evaluación de Tesis de Ingeniería* (`Rúbrica.docx`), con las advertencias de los dictámenes anteriores:

- las ponderaciones suman 115 % y no 100 %;
- el décimo criterio (defensa oral, peso 10) no es evaluable;
- la calificación del documento escrito se computa sobre los nueve criterios restantes (peso 105).

| Criterio | Peso | Puntaje | Nivel | Fundamento |
|---|---|---|---|---|
| 1. Definición del problema | 15 | 9 | Excelente | Tres sub-hipótesis con estadístico, regla y falsación; refutación matizada con intervalo y prueba exacta. Descuenta: "condiciones válidas" en 8.3; asimetría no declarada donde se define la regla. |
| 2. Justificación y relevancia | 10 | 9,5 | Excelente | Tres dimensiones con argumentos verificables; kappas atribuidos al par correcto. |
| 3. Marco teórico y revisión bibliográfica | 15 | 9 | Excelente | Ocho ejes con consecuencia en el diseño; Xiong corregido y verificado. Descuenta: atribución reforzada a Zanzotto sin página. |
| 4. Metodología de investigación | 20 | 9 | Excelente | Procedencia, orden ejecutado y estadística reproducibles. Descuenta: declaración del consentimiento no respaldada por el repositorio; cronometraje mutuo; validación fuera de muestra no realizada. |
| 5. Desarrollo técnico o experimental | 15 | 9,5 | Excelente | Trazabilidad del PDF estabilizada; arquitectura, pines y flujo verificados contra el tag. Descuenta: disparador telefónico en 6.3. |
| 6. Resultados y análisis | 10 | 9,5 | Excelente | Cifras reproducidas sin regresión; laxo y denominadores corregidos. Descuenta: MDE impreso distinto del análisis versionado; cachés con dos nombres. |
| 7. Conclusiones y aportes | 10 | 9,5 | Excelente | Tabla 18 coherente; cada objetivo con el alcance medido. |
| 8. Redacción académica y estructura | 5 | 8,5 | Muy bueno / Excelente | Remisiones correctas y compilación limpia. Descuenta: Anexo I sin el octavo dictamen; errata en 2.4; 118 páginas frente al tope del equipo. |
| 9. Uso de referencias y normas de citación | 5 | 9,5 | Excelente | 91 entradas reales; doce DOI cotejados; FrugalGPT acreditado. Descuenta: Zanzotto; nota de Zendesk. |
| 10. Defensa oral | 10 | — | No evaluable | Pendiente de la instancia de defensa. |

**Cálculo.** Suma de puntaje por peso sobre los nueve criterios del documento: 9 × 15 + 9,5 × 10 + 9 × 15 + 9 × 20 + 9,5 × 15 + 9,5 × 10 + 9,5 × 10 + 8,5 × 5 + 9,5 × 5 = 967,5. Dividido por el peso efectivo (105): **9,21**.

**Calificación del documento escrito: 9 (nueve), nivel "Excelente" (9,21 ponderado).** Representa una mejora de 0,21 puntos respecto del dictamen anterior (9,00). La serie queda en 7,67 → 8,40 → 8,48 → 8,83 → 9,00 → 9,21. Los criterios 2, 5, 6 y 7 suben por la resolución de las observaciones de fondo. El criterio 4 no sube: la declaración del consentimiento reemplaza un descuento por otro de igual peso.

**Proyección de la nota final con defensa oral** (sobre el peso total de 115): con una defensa calificada 7, la nota final resulta 9,02; con 8, 9,11; con 9, 9,20; con 10, 9,28. Con una defensa de 7 o más, la nota final redondea a **9**.

**Proyección tras incorporar las recomendaciones A y B.** Los criterios 1, 3 y 4 pasarían razonablemente a 9,5, y el criterio 8 a 9. El promedio ponderado del documento sería del orden de 9,5 (995 sobre 105). Un 10 en el criterio 4 exige además la validación fuera de muestra (`c-191`).

---

## VERIFICACIÓN CONTRA EL REPOSITORIO

**Hash y PDF.**

- `git rev-list -n1 v1.2.16` = `ca3c88510be5b1484ed413a8de8bcdffccedc417`.
- SHA-256 de `git show v1.2.16:…/main.pdf` = `72a3dd113bba…`, igual al de `compilacion.md` del tag.
- `pdftotext` del PDF del tag: 0 cadenas hexadecimales de 40 caracteres; Anexo B: "El PDF compilado en el propio tag no imprime ese hash…".
- `pdftotext` del PDF de `main`: una sola cadena, `ca3c885…`.
- `git diff --stat v1.2.16 HEAD -- sections`: un archivo, una línea.

**Consentimiento.**

- `11-aspectos-legales.tex:34`: "El repositorio conserva la plantilla de la confirmación y el registro de que se recabó para los cuatro participantes".
- `docs/campana-medicion/confirmacion-posterior-consentimiento.md` (commit `f72e6c8`, 9-11-2026 19:04): tabla de registro con `fecha_informacion_verbal` y `fecha_confirmacion` vacías para `E1`, `E2`, `O1` y `O2`.
- `evaluation/data/campana/README.md`: sin registro de consentimiento.
- La búsqueda de `fecha_confirmacion`, `fecha_consentimiento` y `fecha_informacion_verbal` en archivos `.md` y `.csv` fuera de los changes archivados solo encuentra la plantilla, el registro de correcciones y la especificación.

**Segunda sub-hipótesis.**

- `07-resultados.tex:154`: "las 122 confirmaciones restantes son el 83,0 % de los 147 revisados y el 61,0 % de los 200 casos"; "la prueba binomial no rechaza la cota (p = 0,28)"; "Medirla en condiciones válidas exige una corrida con reportantes identificados".
- `01-introduccion.tex:34` y `04-marco-metodologico.tex:81`: regla de tres vías sin mención de su asimetría.
- Recómputo: 25/147 = 0,1701; Wilson [0,1179; 0,2390]; P(X ≥ 25 | n = 147, p = 0,15) ≈ 0,28; 122/147 = 0,830.

**Efecto mínimo detectable.**

- `07-resultados.tex:253`: ρ = 0,276 con 9/π².
- `evaluation/campana.py:1593`: `tanh(efecto_minimo_detectable(n - 3, eficiencia_relativa=ARE_WILCOXON_MINIMA))`.
- `analisis/resultados.json`: `"mde": 0.2834015929824635`.
- `numeros-canonicos.md:928-932`: reconoce la diferencia.

**Disparador telefónico.** En `n8n/workflow.json`, los nodos de entrada son:

- "Llega un email a Mesa de Ayuda" (`emailReadImap`);
- "Llamada telefonica" (`webhook`, `telefonia-handoff`);
- "Webhook formulario web" (`webhook`, `incidente-web`);
- "notificacion-clasificacion" (`webhook`).

`App/Backend/app/cost_guard/twiml.py:14`: "el backend transcribe, pseudonimiza y hace handoff a n8n".

**Trazabilidad.**

- `ls auditorias/*.md`: ocho dictámenes.
- `12-anexos.tex:205`: "La serie comprende siete dictámenes".
- `openspec/changes/archive/2026-11-09-c-192-…/design.md`, D7: "Anexo I: tabla de trazabilidad del dictamen del 9-11 sobre v1.2.13".
- `verificar_matriz_trazabilidad.py`: 171 filas, 0 avisos y 0 fallas, sin sección de `c-192`.

**Forma.**

- 118 páginas; 0 "??"; 0 errores; 7 cajas desbordadas (8,2 pt).
- Errata: `02-marco-teorico.tex:32`, "; Los autores".

**Pendiente en el repositorio.** `openspec/changes/c-191-validacion-fuera-de-muestra-150-casos/` (propuesto, no aplicado).

---

## VERIFICACIÓN BIBLIOGRÁFICA EXTERNA

- `verify_citations.py`: PASS (91 entradas, 91 claves citadas, 151 comandos de cita, 0 huérfanas, 0 sin usar). `main.blg` sin WARN ni ERROR.
- **Crossref.** Doce DOI coinciden en título, primer autor y año: Mayor-Rocher 2026, Bernal-Beltrán 2025, Ramón-Ferrer 2026, Paket 2024, Liu 2025, Zangari 2023, Colavito 2025, Xuan 2025, Grandury 2025, Ji 2023, Zanzotto 2019 y Galup 2009.
- **FrugalGPT.** El sitio del primer autor y el repositorio `stanford-futuredata/FrugalGPT` lo citan como TMLR, 12/2024. OpenReview y DBLP no permitieron el acceso automático.
- **Xiong et al. (2024).** El texto completo de arXiv respalda la sobreconfianza, la concentración en el extremo alto y la dificultad de predecir fallas.
- **Zanzotto (2019).** El resumen respalda la retribución a quienes aportan conocimiento y no menciona la supervisión humana. El texto completo no fue accesible.
- **Galup et al. (2009).** Datos bibliográficos confirmados (CACM 52(5)). El texto no fue accesible (403).
- **URL.**
  - `zendesk.com/service/` responde y es la página de producto de servicio al cliente, sin la denominación "Suite".
  - `web.stanford.edu/~jurafsky/slp3/` responde, con la versión del 19-08-2026.
  - `servicenow.com/products/itsm.html` no respondió (403 y fallo de conexión).
- **No verificado:** los textos completos de Zanzotto y Galup; la existencia de las confirmaciones firmadas y del comprobante de facturación, que solo los autores y el director pueden acreditar.

---

## ANEXO: INVENTARIO DE CORRECCIONES PUNTUALES

| N.º | Ubicación | Texto o estado actual | Corrección |
|---|---|---|---|
| 1 | `11-aspectos-legales.tex:34` | "firmaron una confirmación escrita"; "el registro de que se recabó para los cuatro participantes" | A1 |
| 2 | `docs/campana-medicion/confirmacion-posterior-consentimiento.md` | Registro con fechas vacías; columnas distintas entre el encabezado y la tabla | A1 |
| 3 | `07-resultados.tex:154` (8.3) | "Medirla en condiciones válidas exige una corrida con reportantes identificados" | Condición de generalización (A2) |
| 4 | `01-introduccion.tex:34` (1.4), `04-marco-metodologico.tex:81` (4.7) | Regla de tres vías sin su asimetría | A2 |
| 5 | `07-resultados.tex:154`, `08-discusion.tex:8` | "no se puede descartar un valor cercano al umbral" | "no se puede descartar una proporción inferior a la cota" (A2) |
| 6 | `12-anexos.tex:205` y tablas del Anexo I | "siete dictámenes"; sin tabla del dictamen sobre `v1.2.13` | A3 |
| 7 | `evaluation/campana.py:1593`, `analisis/resultados.json` | MDE 0,2834 frente al 0,276 del texto | B1 |
| 8 | `06-implementacion.tex:37` (6.3) | "telefonía (callback de grabación de Twilio)"; "Tres disparadores" | B2 |
| 9 | `04-marco-metodologico.tex:16` (4.2) | Cronometraje mutuo sin mencionar que el observador de `A1` era `T1` | B2 |
| 10 | `07-resultados.tex:251` (8.7) | Dos nombres para la caché del 7-10 | B2 |
| 11 | `docs/Tesis/Correcciones/numeros-canonicos.md:811-826, 920` | "no concluyente"; "unión" | B2 |
| 12 | `02-marco-teorico.tex:32` (2.4) | "Zanzotto reclama … y sostener la supervisión humana", sin página | B3 |
| 13 | `02-marco-teorico.tex:32` (2.4) | "; Los autores de esta tesis infieren" | C1 |
| 14 | `07-resultados.tex:154` (8.3) | "regla de visibilidad y derivación … (`VIS-005`)" | C1 |
| 15 | `10-recomendaciones.tex:6` | "que la campaña complementaria de medición refutó" (referido a la medición) | C1 |
| 16 | `10-recomendaciones.tex:18` (11.3) | Sin requisito de tamaño muestral para la nueva medición | C2 |
| 17 | `Bibliography_base.bib` | Nota de Zendesk con "Suite"; URL de ServiceNow sin respuesta | C2 |
| 18 | `11-aspectos-legales.tex` y PDF | 118 páginas frente al tope de 100 del equipo | Decisión registrada; se consigna sin penalizar el cuerpo |

---

*Dictamen elaborado como autoevaluación de control de calidad interno frente a criterios de la CONEAU, a solicitud de los autores. Se basa en la lectura íntegra del manuscrito, el cotejo de las diferencias desde `v1.2.13`, la verificación bibliográfica externa y el cotejo con el repositorio en el tag `v1.2.16`. No constituye revisión por pares ni pronunciamiento de la cátedra, la dirección, el jurado ni la CONEAU.*
