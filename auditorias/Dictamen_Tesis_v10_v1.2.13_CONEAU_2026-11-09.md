# DICTAMEN DE EVALUACIÓN ACADÉMICA

**Documento evaluado:** *Automatización inteligente del registro de incidentes en mesas de ayuda empresariales mediante orquestación de flujos con N8N y procesamiento de lenguaje natural basado en modelos de lenguaje grandes*. Trabajo Final de Carrera, Tecnicatura Universitaria en Programación, Universidad Tecnológica Nacional, Facultad Regional Mendoza. Autores: Luca Gomez, Carla Bustos y Gonzalo Sevilla. Directores: Prof. Alberto Cortez y Prof. Ariel Enferrel.

**Versión examinada:** versión de trabajo v10, release `v1.2.13`. Es un tag anotado sobre el commit `f527722e57369848358dc6bafa333fcfb97653ef`, del 9 de noviembre de 2026 a las 15:01 −03. El examen usa:

- las fuentes LaTeX de `docs/Tesis/v10 (IA)/paper/sections/`;
- su compilación `paper/main.pdf`: 118 páginas (7 preliminares, 93 de cuerpo, 4 de referencias y 14 de anexos);
- la bibliografía `Bibliography_base.bib`, con 91 entradas.

Entre el tag y la cabeza de `main` (`a19c369`), las fuentes de la tesis solo difieren en la línea del Anexo B que consigna el hash.

**Fecha del dictamen:** 9 de noviembre de 2026.

**Alcance del examen:**

- lectura íntegra del documento: resumen bilingüe, glosario, secciones 1 a 11 y anexos;
- recómputo independiente, en Python, de todas las cifras de la sección 8 y de sus propagaciones, desde el corpus, la evidencia congelada y los artefactos de la campaña complementaria;
- seguimiento de cada observación y de cada ítem del inventario del dictamen anterior;
- cotejo de figuras, pines, hash, registro de compilación y PDF del tag;
- verificación bibliográfica externa, con Crossref y lectura de las páginas citadas.

**Antecedentes:** octavo dictamen de la serie iniciada el 20 de octubre de 2026. El anterior, del 9 de noviembre de 2026 sobre `v1.2.12`, formuló:

- tres observaciones de fondo (A1 a A3);
- cuatro de consistencia (B1 a B4);
- dos de forma y bibliografía (C1 y C2);
- un inventario de 30 correcciones puntuales.

Calificó el documento escrito con 8,83. Los autores lo atendieron en el change `c-190` (release `v1.2.13`), con una tabla de trazabilidad nueva en el Anexo I. Su verificador automático, ejecutado para este dictamen, registra 171 filas sin fallas.

**Nivel de exigencia:** criterios de evaluación universitaria argentina (CONEAU), calibrados al nivel de un trabajo final de tecnicatura.

---

## VEREDICTO GENERAL

**APROBADO CON OBSERVACIONES.**

La versión examinada atiende las nueve recomendaciones del dictamen anterior y 29 de los 30 ítems de su inventario. Las tres observaciones de fondo están resueltas en el texto:

- **Segunda sub-hipótesis.** Se informa sobre el denominador de los casos revisados (25 de 147; 17,0 %; IC de Wilson [11,8 %; 23,9 %]) y se declara refutada, con el 12,5 % sobre 200 como dato secundario. El estado es el mismo en el resumen, el *abstract*, 1.4, 4.7, 8.3, 9.1, la Tabla 18, el capítulo 10 y la sección 11.3. El cotejo de las revisiones con el consenso nuevo figura como dato.
- **Enmascaramiento de los operadores.** Está corregido con coherencia en 4.2, 4.8, 7.5 y 9.1: no existió para el operador que es autor, y el *debriefing* alcanzó solo al operador externo.
- **Nota al pie de la Tabla 19.** Dice ahora lo que el `git diff` muestra: 24 archivos, sin cambios en los archivos de pines.

También se resolvieron las observaciones de consistencia:

- el canal telefónico tiene una sola descripción y el modelo de transcripción (`gemini-3.5-transcribe`) está declarado en 6.4, en la Tabla 19, en el Anexo H y en 9.5;
- los rótulos de las figuras regeneradas son coherentes;
- el glosario tiene 87 entradas;
- la portada lleva la fecha de la release;
- se retiró la figura huérfana;
- la bibliografía corrigió todas las atribuciones y fuentes señaladas menos una.

La aritmética resiste otra verificación independiente, sin una sola regresión en el núcleo.

El veredicto se mantiene con observaciones por cuatro razones nuevas, todas corregibles en una sesión de edición y ninguna con nuevas mediciones.

1. **El PDF del tag vuelve a imprimir el hash de otra release.** El Anexo B del PDF versionado en `v1.2.13` afirma: "El hash completo de ese commit es `7937efd063955f787a4fed6c10168b4744de8905`, que constituye la referencia verificable de la versión corregida". Ese es el commit de `v1.2.12`. El de `v1.2.13` es `f527722…` y solo figura en el PDF de `main`, compilado después. En `v1.2.12` el problema estaba resuelto: el PDF del tag no imprimía un hash ajeno, sino una oración de verificación (`git rev-list -n1`). En `c-190` el anexo pasó a consignar el hash en el propio tag, y eso reintrodujo el defecto del patrón de dos commits. Un jurado que abra el PDF de la versión entregada lee una referencia que apunta a la versión anterior.

2. **La segunda sub-hipótesis afirma, a la vez, una refutación y la falta de una medición válida.** El dictamen anterior pidió elegir entre dos lecturas y sostener una sola: (i) no contrastable en esta campaña, o (ii) refutada sobre los casos revisados. El texto adopta la segunda, pero conserva frases de la primera:
   - la celda del cuarto objetivo en la Tabla 18 dice "intervención humana refutada sobre los casos revisados (25 de 147), sin medición válida por la regla del reportante";
   - la sección 8.3 cierra el párrafo de la refutación con "Medirla en condiciones válidas exige una corrida con reportantes identificados".

   Si la medición no es válida, no refuta. Si refuta, la frase sobre condiciones válidas debe reformularse como condición para generalizar.

   El recómputo agrega un matiz que el texto debe consignar. La regla de tres vías es asimétrica: exige que el límite superior del intervalo quede bajo 0,15 para declarar compatibilidad, pero refuta con la sola estimación puntual. Con 25/147, el intervalo de Wilson [11,8 %; 23,9 %] contiene 0,15, y la prueba binomial exacta unilateral de H₀: p ≤ 0,15 da p = 0,28. La refutación es correcta según la regla declarada, pero no hay evidencia estadística de que la proporción supere la cota. Lo honesto es decir "refutada según la regla declarada (la estimación puntual supera la cota; el intervalo la contiene)".

   La misma oración de 8.3 mezcla denominadores: "25 de los 147 casos revisados (17,0 %) … con 122 confirmaciones (61,0 %)". El 61,0 % es 122/200; sobre los 147 revisados es 83,0 %.

3. **La justificación (1.6) atribuye el kappa moderado a quienes no lo produjeron.** La corrección de B4 dice que la validación se hizo "con un doble etiquetado de acuerdo moderado a cargo de un analista externo y de un analista que es autor del trabajo". Las personas no coinciden con el valor:
   - el par analista externo más analista autor (`A1` y `T1`) es el de la campaña 2026-10, cuyo acuerdo fue κ = 0,87 ("casi perfecto", según 4.4);
   - el acuerdo moderado (κ = 0,5569) es el del doble etiquetado nuevo, a cargo de `E1` y `E2`, que según 4.4 y `registro_sujetos.csv` son distintos de los autores y de los analistas originales.

   La frase debe distinguir las dos campañas.

4. **La definición del conjunto de verdad laxo del brazo manual es falsa, y el error es de este evaluador.** El dictamen anterior afirmó que el 130/151 solo se reproducía con "el consenso más la unión de los sectores adicionales de ambos etiquetadores", y la tesis copió esa definición en 8.7. El recómputo actual muestra que la unión da 137/151. El 130/151 sale con la intersección de los adicionales de `E1` y `E2`, que es lo que define el docstring de `construir_referencia` en `evaluation/campana.py`: "sector consensuado más la INTERSECCIÓN". Con esa misma regla, el brazo automatizado da 117/138, igual que `analisis/resultados.json`. La cifra de la tesis es correcta; la frase que la define, no. Este dictamen rectifica su observación anterior.

Persisten, declaradas con precisión y sin computarse como incumplimiento, las limitaciones estructurales del diseño:

- métricas de clasificación dentro de la muestra y validación fuera de muestra no realizada;
- tiempos automatizados de configuraciones anteriores a la evaluada;
- exactitud estricta (73,5 %) con intervalo íntegramente inferior al umbral del 85 %;
- efecto de orden no estimado;
- balance operativo condicional al costo no cronometrado de las reasignaciones;
- ausencia de un registro del consentimiento de los cuatro sujetos de la campaña complementaria, que el texto ahora declara.

---

## OBSERVACIONES DETALLADAS POR SECCIÓN

### 1. Estructura general del documento

**Cumple.** La organización es la canónica de un trabajo de investigación aplicada: resumen bilingüe, glosario, once secciones, referencias y nueve anexos.

- Las remisiones resuelven todas: no hay "??" en el PDF ni referencias indefinidas.
- La sección 9.3 anuncia ocho limitaciones y enumera ocho.
- El anacoluto de 8.3 y la repetición de la Tabla 18 desaparecieron.
- El Anexo B nombra el resumen de compilación y el verificador que la Tabla 23 le atribuye.
- El Anexo I incorpora una tabla de trazabilidad para el dictamen anterior.

Defectos de forma:

- El documento conserva 118 páginas frente al tope total de 100 que el propio equipo fijó. El cuerpo queda en 93, y el exceso está sostenido por una decisión registrada en `c-190` (D7).
- La sigla VIS (regla `VIS-005`, sección 8.3) sigue sin desarrollarse en ningún lugar, aunque el diseño de `c-190` lo preveía. HS256 y CA, en cambio, se desarrollan en su primer uso.
- La fila "Lím." del Anexo I ("deja entonces sin concluir … refutada después") puede leerse como dos estados. Conviene escribirla como secuencia temporal explícita.

### 2. Claridad y formulación de la hipótesis

**Cumple, con observaciones.** La formulación sigue siendo la mejor de la serie:

- una hipótesis principal desdoblada en tres sub-hipótesis contrastables, con estadístico, hipótesis nula sobre las diferencias pareadas, regla de tres vías y criterio de falsación;
- dos subsidiarias rotuladas como no contrastadas;
- los estados coinciden en todo el documento.

La dimensión pasa de "cumple parcialmente" a "cumple" porque la segunda sub-hipótesis ya no depende de un denominador que incluya casos sin revisión. La observación 2 del veredicto impide la calificación plena. Las dos lecturas conviven en la Tabla 18 y en 8.3. Además, la refutación descansa en la rama de la regla que usa la estimación puntual, con un intervalo que contiene la cota.

Conviene declarar en 1.4 que la regla es deliberadamente asimétrica. Así, "refutada" se lee como "no compatible con la cota según la regla fijada a priori" y no como rechazo estadístico de p ≤ 0,15. La generalización tiene un alcance adicional, que el texto acota bien en 8.3 pero no en el objetivo general de la Tabla 18. Los 147 casos revisados no son una muestra aleatoria del flujo: son los de correo y telefonía, que la regla del reportante seleccionó y que tienen menor exactitud que el formulario web (0,654 y 0,773 frente a 0,811).

### 3. Definición y coherencia de los objetivos

**Cumple.** El objetivo general y los seis específicos están bien delimitados. La Tabla 18 cierra la matriz objetivo-evidencia-conclusión con grados honestos: uno no alcanzado, cinco parcialmente y uno alcanzado. La fila del primer objetivo califica ahora los reintentos como "de la configuración entregada".

Persiste una inexactitud en la justificación académica (1.6), señalada en la observación 3 del veredicto. La corrección retiró "validación rigurosa" y "doble etiquetado independiente", como se pidió, pero el acuerdo moderado se atribuye al par equivocado.

### 4. Estado del arte

**Cumple.** Tiene un protocolo de revisión con seis bases, siete cadenas, dos fechas de corte y bitácora versionada. Hay siete trabajos sistematizados con métrica y condición, y literatura de calibración y cascadas. La brecha está acotada "al alcance revisado".

Correcciones atendidas:

- la ausencia de búsquedas en repositorios regionales (SciELO, Redalyc, JAIIO) se declara ahora como limitación del protocolo;
- la Tabla 1 cita la versión arbitrada de Paramesh et al. (IEEE CSITSS 2018, pp. 221-227), en lugar del preprint.

Queda un residuo: el párrafo sobre calibración (`03-estado-del-arte.tex:62`) sigue atribuyendo a Xiong et al. (2024) "poca capacidad para separar aciertos de errores". Es la formulación que se atenuó en 2.5 y 9.2 por exceder lo que la fuente sostiene.

### 5. Marco teórico

**Cumple.** Ocho ejes desembocan en decisiones de diseño verificables. Las imprecisiones señaladas están resueltas:

- el punto único de contacto se atribuye a ITIL;
- "posterior a la campaña 2026-10" reemplaza al rótulo ambiguo en 2.4 y en el resto del documento;
- la atribución a Zanzotto (2019) se reformula como inferencia de los autores, con la referencia limitada al paradigma *HitAI*.

Esa reformulación es aceptable, aunque la oración resultante encadena la inferencia propia y el contenido de la fuente con una sintaxis forzada ("los autores de esta tesis infieren que … en el paradigma *HitAI*, que reclama …"). Conviene separarla en dos oraciones y, si se puede, paginar la cita.

### 6. Desarrollo metodológico y propuesta (método, arquitectura, implementación y resultados)

**Cumple, con observaciones.** Concentra las fortalezas del trabajo y tres de las cuatro observaciones del veredicto.

*Fortalezas.*

- **Procedencia y configuraciones.** La procedencia de las tres corridas automatizadas, la tabla de configuraciones con tres columnas verificadas y el orden ejecutado de la campaña complementaria están declarados con una precisión que excede la del nivel.
- **Campaña complementaria.** Están declarados la naturaleza de cada kappa, el mecanismo de derivación por canal, las unidades de la exactitud manual y el denominador de la proporción de tiempo (tiempos de `corpus_campana.json`, 191 casos). También el origen de la salida en vivo telefónica (export de intervenciones) y la predicción que usa el McNemar (caché del 7-10).
- **Enmascaramiento.** El operador autor queda explícitamente fuera de la atenuación del efecto Hawthorne, y su consecuencia llega a 9.1.
- **Arquitectura e implementación.** El canal telefónico tiene una única descripción, coherente con el código y con las cuatro figuras. Los pines de la Tabla 19 coinciden con `requirements.txt`, `package-lock.json`, `docker-compose.yml` y `settings.py` del tag. La columna "evaluada" del modelo de transcripción es correcta, porque `gemini_stt_model` ya figuraba en `d6bb474`.

*Observaciones de método.*

- **(a) Segunda sub-hipótesis:** observación 2 del veredicto.
- **(b) Conjunto de verdad laxo del brazo manual:** observación 4.
- **(c) Efecto mínimo detectable del Spearman.** El valor 0,2834 se justifica ahora con "la corrección por eficiencia relativa de la prueba empleada (ARE = 0,864)". Ese 0,864 es la cota inferior de Hodges y Lehmann para la prueba de Wilcoxon frente a la *t*, y el código lo nombra `ARE_WILCOXON_MINIMA`. No es la eficiencia de la correlación de Spearman, que frente a la de Pearson vale 9/π² ≈ 0,912 bajo normalidad (MDE ≈ 0,276). El número se reproduce y la diferencia no altera ninguna conclusión, pero la atribución es imprecisa: debe decir que se usa la cota del Wilcoxon como aproximación conservadora, o usar el valor del Spearman.
- **(d) Hawthorne y cronometraje mutuo.** Los operadores de la campaña 2026-10 "trabajaron en pares y se cronometraron mutuamente". Si el autor `T1` cronometró a `A1`, el observador conocía el propósito comparativo aun cuando el observado no. La atenuación declarada para `A1` es más débil de lo que el texto sugiere, y conviene consignarlo.
- **(e) Cifras pedidas que figuran solo en el memo.** Los casos web mal derivados (10 de 53 frente a la referencia original; 7 de 40 frente al consenso) figuran solo en `numeros-canonicos.md`. El texto no las necesita para su veredicto, pero 8.3 se apoya en esos 53 casos para justificar el cambio de denominador.
- **(f) Consentimiento de los sujetos.** La sección 7.5 declara que no se conservó registro del procedimiento de información y consentimiento de `E1`, `E2`, `O1` y `O2`. La declaración es veraz y preferible a una reconstrucción. Sin embargo, la misma oración afirma que las tablas se versionan "en consonancia con el consentimiento informado", y eso no puede sostenerse sin registro. Para un jurado es una debilidad ética menor que conviene subsanar con una constancia firmada de los participantes antes de la defensa.

*Observaciones de implementación y trazabilidad.*

- **Hash del tag:** observación 1 del veredicto.
- **Trigger telefónico.** La etapa de recepción de la sección 6.3 (`06-implementacion.tex:37`) sigue diciendo "telefonía (trigger de Twilio)". El disparador de N8N es el webhook `telefonia-handoff` del backend, como describen 5.2, 6.4, 6.6 y el `workflow.json` del tag.
- **Dos nombres para la misma caché.** La caché del 7-10 aparece como `predicciones_in_sample.json` y como `predicciones_hybrid-v3_2026-10-07.json`. Este dictamen verificó que las dos coinciden en los 200 sectores predichos, pero el texto no lo dice.
- **Nivel de servicio de la Gemini API.** El nivel pago se acredita con `docs/gemini-api-key-setup.md`, una guía de configuración del 24-09-2026 que recomienda el nivel pago y describe un "plan B" gratuito. Como fuente de un hecho operativo es débil: un comprobante de facturación o la captura del proyecto en *Paid tier* lo acreditarían.

### 7. Conclusiones

**Cumple, con observaciones.** El capítulo responde a cada objetivo y sub-hipótesis, incorpora el kappa moderado de la campaña complementaria, el efecto de posición y el calificativo "dentro de la muestra". La conclusión del cuarto objetivo está acotada a lo medido. Sigue siendo el capítulo con mejor relación entre lo que afirma y lo que la evidencia sostiene. El resumen y el *abstract* dicen ahora "respaldan" y "support", como se pidió.

Hereda la observación 2: en la Tabla 18, la fila del cuarto objetivo afirma la refutación y la falta de medición válida en la misma celda. Además, la fila del objetivo general proyecta la refutación al flujo sin la acotación a correo y telefonía que el cuerpo sí hace.

### 8. Propuestas de trabajos futuros

**Cumple.** Las líneas están priorizadas y las prioritarias atacan defectos medidos. La sección 11.3 incorpora los dos requisitos pedidos para la nueva medición de la intervención humana: revisión de todos los canales, o de una muestra aleatoria de cada uno, y cotejo de cada validación con una referencia independiente. Conviene agregar un tercer requisito, que la observación 2 muestra necesario: dimensionar la muestra para que el intervalo de la proporción pueda quedar por debajo de 0,15, porque con 147 casos y una proporción cercana a la cota la regla nunca puede declarar compatibilidad.

### 9. Bibliografía

**Cumple.** Las 91 entradas son reales y `verify_citations.py` da PASS: 91 claves citadas en 151 comandos de cita, ninguna huérfana ni sin usar, sin duplicados. `main.blg` no registra avisos. Los 43 DOI consultados resuelven en Crossref al trabajo citado; las únicas diferencias son de año entre la versión en línea y la impresa (Paramesh 2018/2019; Mosqueira-Rey 2022/2023).

Correcciones atendidas:

- se incorporó la versión IEEE de Paramesh et al. (DOI 10.1109/CSITSS.2018.8768734; Crossref coincide en título, autores y páginas);
- Kerby (2014) lleva el localizador 11.IT.3.1;
- Efron y Tibshirani concilian año y DOI (1994);
- la fuente de precios es la de la Gemini API: su URL redirige a la página de AI Studio, que lista `gemini-3.6-flash` a 0,75 y 3,75 USD por millón de tokens hasta el 31-12-2026 y distingue el uso de datos entre los niveles gratuito y pago, como afirma el capítulo 7;
- las URL de Zendesk y del Decreto 1558/2001 responden y corresponden a lo citado.

La actualidad es adecuada: al menos 43 entradas son de 2022 en adelante y 39 de 2023 a 2026, frente a 11 anteriores a 2000, que son los clásicos metodológicos.

Residuos menores:

- la caracterización de Xiong et al. en el capítulo 3 (sección 4 de este dictamen);
- la publicación de FrugalGPT en TMLR, que sigue sin confirmarse y debería citarse como preprint si no se acredita;
- la cita de Zanzotto, sin página;
- la nota de `Zendesk2026_help_desk`, que dice "capacidades y precios", cuando la página nueva no muestra precios;
- dos URL que no respondieron en esta verificación (`web.stanford.edu/~jurafsky/slp3` y la página de ServiceNow ITSM), que conviene revisar.

---

## TABLA RESUMEN DE CUMPLIMIENTO

| Dimensión | Dictamen v1.2.12 (9-11-2026) | Presente dictamen (v1.2.13) |
|---|---|---|
| 1. Estructura general | Cumple (defectos de forma) | Cumple (118 páginas; VIS; fila del Anexo I) |
| 2. Hipótesis | Cumple parcialmente | Cumple, con observaciones (dos lecturas conviven; regla asimétrica no declarada) |
| 3. Objetivos | Cumple | Cumple (atribución del kappa en 1.6) |
| 4. Estado del arte | Cumple | Cumple (residuo de Xiong en el capítulo 3) |
| 5. Marco teórico | Cumple | Cumple |
| 6. Metodología y propuesta | Cumple parcialmente | Cumple, con observaciones (hash del tag; definición del laxo manual; ARE del Spearman; trigger telefónico; consentimiento sin registro) |
| 7. Conclusiones | Cumple, con observaciones | Cumple, con observaciones (Tabla 18) |
| 8. Trabajos futuros | Cumple | Cumple |
| 9. Bibliografía | Cumple, con observaciones | Cumple (residuos menores) |

Por primera vez en la serie, ninguna dimensión queda en "cumple parcialmente". Las observaciones de las dimensiones 2 y 6 ya no tocan la validez de lo medido: tocan la redacción de su estado y la trazabilidad del PDF entregado.

---

## SEGUIMIENTO DE LAS OBSERVACIONES DEL DICTAMEN ANTERIOR

| Ítem del 9-11-2026 (v1.2.12) | Estado | Evidencia en `v1.2.13` |
|---|---|---|
| A1. Sub-hipótesis 2 según los casos revisables | Resuelto, con observación nueva | Lectura (ii) adoptada en los nueve lugares; 25/147 [11,8; 23,9]; cotejo con el consenso (85/11; 13 = 9 + 1 + 3) en 8.3. Observación nueva: conviven frases de la lectura (i) en la Tabla 18 y en 8.3; denominador del 61,0 %; asimetría de la regla (observación 2) |
| A2. Enmascaramiento del operador autor | Resuelto | 4.2, 4.8, 9.1 y 7.5 coherentes; ningún otro lugar lo contradice. Matiz: el cronometraje mutuo (sección 6, inciso d) |
| A3. Nota de la Tabla 19 | Resuelto | 24 archivos; sin cambios en los archivos de pines (verificado con `git diff --stat cda7712 v1.2.13`) |
| B1. Canal telefónico | Resuelto, con residuo | 5.2, 6.4, 6.6, Tabla 5, Tabla 19, Anexo H, 9.5, despliegue con las cuatro redes y la transcripción. Residuo: "trigger de Twilio" en 6.3 |
| B2. Denominadores, salida en vivo, laxo manual, MDE | Resuelto en lo declarativo, con dos problemas | Denominador de la proporción de tiempo, salida en vivo y McNemar declarados. Problemas: la definición del laxo (unión en lugar de intersección; error del dictamen anterior) y la ARE prestada del Wilcoxon |
| B3. Campaña complementaria y rótulos | Resuelto | 4.5 matizada; "posterior a la campaña 2026-10" en todo el texto y en los PNG regenerados |
| B4. Justificación, "respaldan", reintentos | Resuelto, con problema nuevo | "Respaldan" y "support"; reintentos calificados. Problema: 1.6 atribuye el kappa moderado al par de la campaña 2026-10 (observación 3) |
| C1. Forma | Resuelto, con residuo | Ocho limitaciones; anacoluto y repetición resueltos; glosario con 87 entradas; portada del 9-11; figura huérfana retirada; Anexo B nombra los artefactos. Residuo: VIS |
| C2. Bibliografía | Resuelto, con residuos | Galup e ITIL, Gemini API, nivel pago, URL, Paramesh IEEE, Kerby, Efron. Residuos: Xiong en el capítulo 3, Zanzotto sin página, FrugalGPT |
| Ítems 1 a 30 del inventario | 29 resueltos, 1 parcial | Parcial: 12 (MDE: número justificado con una eficiencia que no corresponde a la prueba) |
| Hash del tag (A5 del dictamen v1.2.10) | **Regresión** | Resuelto en `v1.2.12`; el PDF de `v1.2.13` imprime `7937efd…` como hash de la versión corregida (observación 1) |

---

## RECOMENDACIONES CONCRETAS Y ACCIONABLES

Las recomendaciones A deben resolverse antes de la defensa, las B son de consistencia y las C de forma. Ninguna exige nuevas mediciones de campo.

**A1. Restituir la trazabilidad del PDF entregado** (`12-anexos.tex:46`). Volver a la solución de `v1.2.12`: que el PDF compilado en el tag no imprima ningún hash, solo la instrucción verificable (`git rev-list -n1 v1.2.13`), y que el hash completo figure solo en el commit posterior de `main`. Si se prefiere imprimir el hash, entregar al jurado el PDF de `main` y no el del tag, y declararlo en el Anexo B. En cualquier caso, el PDF que reciba el jurado no debe nombrar el commit de otra release como "referencia verificable de la versión corregida".

**A2. Sostener una sola lectura de la segunda sub-hipótesis** (Tabla 18, fila del cuarto objetivo; 8.3; 1.4).

- Retirar "sin medición válida por la regla del reportante" de la Tabla 18.
- Reformular el cierre de 8.3 como condición de generalización: "extender la conclusión al formulario web y a reportantes identificados exige una corrida con …".
- Declarar en 1.4 y en 8.3 que la regla de tres vías es asimétrica y que, con 25/147, la refutación responde a la estimación puntual (17,0 % ≥ 15 %) con un intervalo que contiene la cota (prueba binomial exacta unilateral, p = 0,28).
- En la fila del objetivo general, acotar la refutación a los casos de correo y telefonía revisados.
- Expresar las confirmaciones sobre el mismo denominador: 122 de 147 (83,0 %).

**A3. Corregir la atribución del acuerdo en 1.6** (`01-introduccion.tex:66`). Distinguir el doble etiquetado original, a cargo de un analista externo y de uno que es autor (κ = 0,87, sin intervalo), del doble etiquetado nuevo, a cargo de dos etiquetadores independientes del equipo (κ = 0,5569, moderado, con intervalo).

**B1. Corregir la definición del conjunto de verdad laxo del brazo manual** (`07-resultados.tex`, sección 8.7, y `numeros-canonicos.md:920`). Reemplazar "la unión de los sectores adicionales de ambos etiquetadores" por "la intersección de los sectores adicionales que marcaron ambos etiquetadores", que es la regla del código y la que produce 130/151. La observación del dictamen anterior era errónea en ese punto.

**B2. Justificar la eficiencia del efecto mínimo detectable del Spearman** (8.7). Declarar que 0,864 es la cota del Wilcoxon de Hodges y Lehmann, usada como aproximación conservadora, o recalcular con 9/π² ≈ 0,912 (ρ ≈ 0,276). En el primer caso, renombrar o documentar la constante en `evaluation/stats.py`.

**B3. Completar la propagación de las correcciones.**

- 6.3: "trigger de Twilio" → "webhook del backend (`telefonia-handoff`)".
- 3.x (`03-estado-del-arte.tex:62`): atenuar Xiong et al. como en 2.5 y 9.2.
- 4.2: consignar que en los pares de cronometraje el observador de `A1` era el autor.
- 7.5: retirar "en consonancia con el consentimiento informado" para la campaña complementaria o reemplazarlo por la constancia que se obtenga.
- 8.7: decir que `predicciones_in_sample.json` y `predicciones_hybrid-v3_2026-10-07.json` contienen las mismas predicciones.
- Actualizar `numeros-canonicos.md`, que en las líneas 816-826 conserva el estado "no concluyente".

**B4. Respaldar las declaraciones que dependen de hechos operativos.** Acreditar el nivel pago de la Gemini API con un comprobante de facturación o con la captura del proyecto (la guía de configuración no lo prueba). Obtener de `E1`, `E2`, `O1` y `O2` una constancia firmada de consentimiento, aunque sea posterior, y mencionarla en 7.5.

**C1.** Desarrollar VIS en su primer uso o incorporarla al glosario. Reescribir la fila "Lím." del Anexo I como secuencia temporal ("primero no concluyente, con `c-169`; luego refutada sobre los casos revisados, con `c-190`"). Separar en dos oraciones la atribución a Zanzotto y paginarla si es posible.

**C2.** Confirmar la publicación de FrugalGPT en TMLR o citarla como preprint. Ajustar la nota de `Zendesk2026_help_desk` a lo que la página muestra. Revisar las URL de Jurafsky y Martin y de ServiceNow, que no respondieron.

---

## CONSIDERACIÓN FINAL

La serie de dictámenes muestra un trabajo que mejora en cada versión, y esta es la más sólida. Las tres observaciones de fondo anteriores se resolvieron en todos los lugares donde el hecho corregido se apoyaba, y esa era precisamente la falla que el dictamen anterior había diagnosticado. La aritmética resiste íntegra un nuevo recómputo. La bibliografía quedó prácticamente depurada.

Lo que queda tiene otro origen: las correcciones nuevas trajeron sus propios desajustes.

- Para atender la trazabilidad del hash se cambió una solución que funcionaba por otra que reintroduce el defecto en el PDF del tag.
- Para atender la justificación se escribió una frase que asigna el acuerdo moderado al par equivocado.
- Para adoptar la refutación se conservaron frases de la lectura alternativa.
- Para definir el laxo manual se copió una descripción de este evaluador que era falsa.

Ninguno de estos puntos cambia una cifra ni un resultado. Todos se corrigen con el repositorio al lado y con una relectura de la Tabla 18, de la sección 1.6 y del Anexo B antes de compilar.

---

## CALIFICACIÓN SUGERIDA SEGÚN LA RÚBRICA DE LA CÁTEDRA

Se aplica la *Rúbrica de Evaluación de Tesis de Ingeniería* (`Rúbrica.docx`), con las advertencias de los dictámenes anteriores:

- las ponderaciones suman 115 % y no 100 %, de modo que el promedio se calcula sobre la suma efectiva de los pesos;
- el décimo criterio (defensa oral, peso 10) no es evaluable;
- la calificación del documento escrito se computa sobre los nueve criterios restantes (peso 105).

| Criterio | Peso | Puntaje | Nivel | Fundamento |
|---|---|---|---|---|
| 1. Definición del problema | 15 | 9 | Excelente | Tres sub-hipótesis con estadístico, regla y falsación; estados coherentes en todo el documento; denominador correcto. Descuenta: dos lecturas en la Tabla 18 y 8.3; asimetría de la regla no declarada. |
| 2. Justificación y relevancia | 10 | 9 | Excelente | Tres dimensiones con argumentos verificables y punto de equilibrio reutilizable. Descuenta: la atribución del kappa moderado en 1.6. |
| 3. Marco teórico y revisión bibliográfica | 15 | 9 | Excelente | Ocho ejes con consecuencia en el diseño; atribuciones corregidas; ausencia de repositorios regionales declarada. Descuenta: residuo de Xiong en el capítulo 3; Zanzotto sin página. |
| 4. Metodología de investigación | 20 | 9 | Excelente | Procedencia completa, orden ejecutado y enmascaramiento declarados con veracidad, estadística reproducible, denominador corregido. Descuenta: regla asimétrica; cronometraje mutuo; consentimiento sin registro; validación fuera de muestra no realizada. |
| 5. Desarrollo técnico o experimental | 15 | 9 | Excelente | Arquitectura, contrato, flujo, pines y modelo de transcripción verificados contra el tag; canal telefónico unificado; figuras coherentes. Descuenta: el PDF del tag imprime el hash de `v1.2.12`; "trigger de Twilio" en 6.3. |
| 6. Resultados y análisis | 10 | 9 | Excelente | Más de cien cifras reproducidas sin regresión; denominadores y orígenes declarados. Descuenta: la definición del laxo manual (unión por intersección); la ARE del Spearman; 61,0 % sobre otro denominador. |
| 7. Conclusiones y aportes | 10 | 9 | Excelente | Responden a cada objetivo y sub-hipótesis con el alcance medido; "respaldan". Descuenta: la celda del cuarto objetivo y la proyección al objetivo general. |
| 8. Redacción académica y estructura | 5 | 8,5 | Muy bueno / Excelente | Remisiones correctas, glosario depurado, trazabilidad de correcciones en el Anexo I. Descuenta: 118 páginas frente al tope del equipo; VIS; fila "Lím." ambigua. |
| 9. Uso de referencias y normas de citación | 5 | 9,5 | Excelente | 91 entradas reales; DOI cotejados; correspondencia exacta; versión arbitrada de Paramesh; fuente de precios correcta. Descuenta: Xiong en el capítulo 3; FrugalGPT sin confirmar; nota de Zendesk. |
| 10. Defensa oral | 10 | — | No evaluable | Pendiente de la instancia de defensa. |

**Cálculo.** Suma de puntaje por peso sobre los nueve criterios del documento: 9 × 15 + 9 × 10 + 9 × 15 + 9 × 20 + 9 × 15 + 9 × 10 + 9 × 10 + 8,5 × 5 + 9,5 × 5 = 945. Dividido por el peso efectivo (105): **9,00**.

**Calificación del documento escrito: 9 (nueve), nivel "Excelente" (9,00 ponderado).** Representa una mejora de 0,17 puntos respecto del dictamen anterior (8,83), y la serie queda en 7,67 → 8,40 → 8,48 → 8,83 → 9,00. Los criterios 4 y 6 alcanzan el 9 por la resolución de las observaciones de fondo anteriores. Ninguno supera ese valor por las cuatro observaciones de este dictamen.

**Proyección de la nota final con defensa oral** (sobre el peso total de 115): con una defensa calificada 7, la nota final resulta 8,83; con 8, 8,91; con 9, 9,00; con 10, 9,09. Con una defensa de 7 o más, la nota final redondea a **9**.

**Proyección tras incorporar las recomendaciones A1 a A3 y B1 a B3.** Si se restituye la trazabilidad del PDF, se sostiene una sola lectura de la segunda sub-hipótesis, se corrige 1.6 y se corrigen la definición del laxo y la ARE, los criterios 1, 5 y 6 pasarían razonablemente a 9,5. Con las correcciones C y B4, el criterio 8 pasaría a 9. El promedio ponderado del documento sería entonces del orden de 9,2 (967,5 sobre 105).

---

## VERIFICACIÓN CONTRA EL REPOSITORIO

**Hash.**

- `git rev-list -n1 v1.2.13` = `f527722e57369848358dc6bafa333fcfb97653ef`.
- `git show v1.2.13:"docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex"`, línea 46: "El hash completo de ese commit es `7937efd063955f787a4fed6c10168b4744de8905`" (commit de `v1.2.12`).
- La misma línea en `main`: `f527722…`.
- `git diff --stat v1.2.13 HEAD -- sections`: un archivo, una línea.
- `compilacion.md` coincide con el SHA-256 de su PDF, tanto en el tag como en `main`.

**Segunda sub-hipótesis.**

- `07-resultados.tex` (8.3): "25 de los 147 casos revisados (17,0 %; …), con 122 confirmaciones (61,0 %)" y "Medirla en condiciones válidas exige una corrida con reportantes identificados".
- `09-conclusiones.tex`, Tabla 18, fila del cuarto objetivo: "refutada sobre los casos revisados (25 de 147), sin medición válida por la regla del reportante".
- Recómputo: 25/147 = 0,1701, Wilson [0,1179; 0,2390], Clopper-Pearson [0,113; 0,241]; prueba binomial exacta unilateral de H₀: p ≤ 0,15, p = 0,28; 122/147 = 0,830; 122/200 = 0,610.

**Analistas y etiquetadores.**

- `registro_sujetos.csv`: `E1` y `E2` con rol de etiquetador (personas P1 y P2); `A1` analista original (P5); `T1` autor (P6).
- `04-marco-metodologico.tex`: el doble etiquetado original, "uno externo … y otro que es también autor", con κ = 0,87; `E1` y `E2`, "distintos … de los autores".
- `01-introduccion.tex:66`: "doble etiquetado de acuerdo moderado a cargo de un analista externo y de un analista que es autor".

**Laxo manual.**

- `evaluation/campana.py:249`: "el sector consensuado más la INTERSECCIÓN" de los adicionales.
- Recómputo sobre las 151 derivaciones con consenso: intersección 130/151 (automatizado 117/138, igual que `analisis/resultados.json`); unión 137/151; adicionales del corpus 128/151; solo `E1` 131, solo `E2` 136.

**Efecto mínimo detectable.**

- `evaluation/stats.py:438`: `ARE_WILCOXON_MINIMA = 0.864`.
- `evaluation/campana.py:1593`: `tanh(efecto_minimo_detectable(n - 3, eficiencia_relativa=ARE_WILCOXON_MINIMA))`.
- tanh(2,80158/√(107 × 0,864)) = 0,2834; sin ARE, 0,2644; con 9/π², 0,276.
- `brazo_manual.csv`: 110 filas por operador.

**Cachés.** `evaluation/data/campana/predicciones_in_sample.json` y `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` coinciden en los 200 sectores predichos.

**Tabla 19.**

- `git diff --stat cda7712 v1.2.13 -- App/ n8n/ docker/ docker-compose.yml`: 24 archivos, 1323 inserciones y 75 supresiones.
- Sin cambios en `requirements.txt`, `package-lock.json`, `n8n/workflow.json` ni `settings.py`.
- `gemini_stt_model = "gemini-3.5-transcribe"` en `settings.py` del tag (línea 238) y de `d6bb474` (línea 225).

**Pines.** FastAPI 0.162.0, Uvicorn 0.54.0, SQLAlchemy 2.1.6, `google-genai >=2.33.0,<3`, pytest 9.1.1, pytest-cov 7.1.0, React 19.3.1, Python 3.12-slim, PostgreSQL 15.5-alpine y N8N derivada de 2.11.2. En `settings.py`: `gemini-3.6-flash`, 0,3, 0,9, 100 tokens y 30 s. Todo coincide con la Tabla 19.

**Figuras.** `componentes.png`, `secuencia.png` y `despliegue.png` coinciden con el texto y con sus leyendas:

- "posterior a la campaña 2026-10";
- las cuatro redes Docker;
- Gemini "clasificación y transcripción";
- el *callback* de grabación de Twilio.

`matriz_confusion.pdf` fue retirada.

**Disparador telefónico.** `06-implementacion.tex:37`: "telefonía (trigger de Twilio)". En `n8n/workflow.json` del tag, el nodo "Llamada telefonica" es de tipo `n8n-nodes-base.webhook`, con path `telefonia-handoff`.

**Nivel de la Gemini API.** `docs/gemini-api-key-setup.md` (commit `1aa691a`, 24-09-2026) es una guía para crear una clave con créditos prepagos. Incluye un "Plan B de costo cero" con claves gratuitas y no constituye registro de qué nivel operó.

**Trazabilidad.** `verificar_matriz_trazabilidad.py`: 171 filas, 0 avisos y 0 fallas (44 de `c-190`).

**Forma.**

- 118 páginas: 7 + 93 + 4 + 14.
- 0 "??".
- Compilación con 0 errores, 0 indefinidas y 7 cajas desbordadas (máximo 8,2 pt), según `compilacion.md`.
- Resumen de 239 palabras en español y 239 en inglés según el equipo; ambos bajo el tope de 250 con cualquier regla de conteo.

---

## VERIFICACIÓN ARITMÉTICA

Recómputo en Python desde `data/corpus_evaluacion_pseudonimizado.json`, `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` y `evaluation/data/campana/`. Coinciden con lo declarado:

- **Tiempos.** Medias 61,585 y 17,761 s; medianas 50,0 y 17,471; desvíos 44,896 y 13,516; extremos; reducciones de 71,16 % y 65,06 %. Wilcoxon: T⁺ = 19.737, T⁻ = W = 363, p = 3,08 × 10⁻³²; r = 0,9639; d_z = 1,0004. Hay 12 pares no más rápidos, todos de correo. Shapiro-Wilk de los tres conjuntos. Sensibilidad con −5 s y −10 s: 56,6 y 51,6 s; 68,6 % y 65,6 %; p = 1,8 × 10⁻²⁶; r = 0,8683. Tabla 10 completa por canal.
- **Clasificación.** Matriz de confusión celda a celda. Exactitud estricta 147/200 [0,670; 0,791] y laxa 179/200 [0,845; 0,930], por etapa y por canal, con sus intervalos. Precisión, sensibilidad y F1 de las cuatro clases estimables; macro-F1 de 0,6508 y 0,5207. Subset accuracy 0,43, Hamming 0,3586 y micro-F1 0,6654. Bandas de confianza; 46 casos con confianza ≥ 0,90 y 13 errores; Tabla 15 (14/12/11/16, con 5/10/8/9 aciertos laxos); Sistemas, 7 de 16.
- **Economía.** Δt = 43,8244 s y 32,2 h-persona. Las 24 celdas de la Tabla 16. 304 derivaciones y 50,7 a 76,1 h. Rango laxo de +28,9 a +138,1. e_man = 0,1722 [0,1118; 0,2353]; a* = 68,2, 75,5 y 77,9 %.
- **Campaña complementaria.**
  - Intervenciones: 147 (66/81/0 por canal), todas de origen `gate`, con 25 cambios y 122 confirmaciones.
  - Cotejo con el consenso: 85 confirmaciones y 11; 13 = 9 + 1 + 3.
  - Proporción de tiempo: 0,5307 = 3044,717/(2692,22 + 3044,717); cobertura 0,9388; con los tiempos del corpus original daría 0,4811.
  - Kappa 0,556858 (p_o 0,69; p_e 0,30045), PABAK 0,6125 e IC asintótico [0,4725; 0,6413]; consenso igual al sector original en 116 de 138.
  - Brazo manual: O1 71/80 y O2 54/71 con sus intervalos; 125/151; laxa 130/151 (con intersección).
  - Contrastes: McNemar 0,2668 y 1,0000; automatizado 110/138 [0,7224; 0,8557]; 13 diferencias entre caché y salida en vivo; sidecars telefónicos con sector nulo en 81 casos; Spearman −0,0628 (p 0,5147) y −0,3604 (p 0,00011).
  - Ablación: 50/69 frente a 46/69 (p = 0,3438); 48/66.

Discrepan:

- la definición del laxo manual (observación 4);
- el 61,0 %, correcto como 122/200 pero presentado junto a un denominador de 147;
- el memo `numeros-canonicos.md`, internamente contradictorio entre las líneas 816-826 y 909-910.

No recomputables de forma independiente, pero coincidentes en orden de magnitud y con `analisis/resultados.json`:

- los intervalos bootstrap con semilla: exactitud manual [0,7647; 0,8882], proporción de tiempo [0,4407; 0,6111] y kappa [0,4751; 0,6387];
- el 88/130 de Gemini con el cortocircuito deshabilitado y su p = 0,1516;
- los 89 patrones del vocabulario previo;
- el kappa de 0,87 de la campaña 2026-10.

---

## VERIFICACIÓN BIBLIOGRÁFICA EXTERNA

- `verify_citations.py`: PASS, con 91 entradas, 91 claves citadas en 151 comandos de cita, ninguna huérfana ni sin usar y sin duplicados. `main.blg` (biber, 9-11-2026) no tiene avisos.
- Los 43 DOI del `.bib` resuelven en Crossref al trabajo citado. Las diferencias de año entre la versión en línea y la impresa son aceptables. Tres DOI de arXiv (Llama 2, Opitz y Burst, y uno ya no citado) no figuran en Crossref, pero existen en DataCite.
- **Entradas nuevas.** `Paramesh2018_csitss` coincide en título, autores (Paramesh, Ramya y Shreedhara), año y páginas 221-227. `Google2026_gemini_api_pricing` redirige a la página de precios de AI Studio, que confirma los precios y la distinción de uso de datos por nivel. Se retiraron `ramya2021classifying` y `Google2026_vertex_pricing`; no queda ninguna mención de Vertex AI.
- **URL.** Zendesk (`zendesk.com/service/`) y el Decreto 1558/2001 en argentina.gob.ar responden y corresponden a lo citado. Ocho URL de editoriales devuelven 403 por bloqueo automático y dos de IEEE devuelven 202 sin contenido. No respondieron `web.stanford.edu/~jurafsky/slp3` ni `servicenow.com/products/itsm.html`.
- **Frases cotejadas.** Están resueltas Galup e ITIL, la Gemini API y Xiong en 2.5 y 9.2. Zanzotto quedó reformulado como inferencia propia. Persisten Xiong en el capítulo 3 y FrugalGPT en TMLR sin confirmar.
- **No verificado:** los textos completos de Zanzotto, Xiong y Paramesh (IEEE), por acceso cerrado o por la verificación de navegador de OpenReview; y el nivel de servicio efectivamente usado, que solo los autores pueden acreditar.

---

## ANEXO: INVENTARIO DE CORRECCIONES PUNTUALES

| N.º | Ubicación | Texto o estado actual | Corrección |
|---|---|---|---|
| 1 | `12-anexos.tex:46` (PDF del tag) | "El hash completo de ese commit es `7937efd…`" | A1 |
| 2 | `09-conclusiones.tex`, Tabla 18, fila del cuarto objetivo | "refutada … sin medición válida por la regla del reportante" | A2 |
| 3 | `07-resultados.tex` (8.3) | "Medirla en condiciones válidas exige una corrida con reportantes identificados" | Reformular como condición de generalización (A2) |
| 4 | `07-resultados.tex` (8.3) | "122 confirmaciones (61,0 %)" junto a 25/147 | 122 de 147 (83,0 %) (A2) |
| 5 | `01-introduccion.tex` (1.4), `07-resultados.tex` (8.3) | Regla de tres vías sin declarar su asimetría | Declarar la asimetría y la prueba binomial con p = 0,28 (A2) |
| 6 | `09-conclusiones.tex`, Tabla 18, objetivo general | Refutación proyectada al flujo | Acotar a correo y telefonía revisados (A2) |
| 7 | `01-introduccion.tex:66` | "acuerdo moderado a cargo de un analista externo y de un analista que es autor" | A3 |
| 8 | `07-resultados.tex` (8.7), `numeros-canonicos.md:920` | "la unión de los sectores adicionales de ambos etiquetadores" | "la intersección" (B1) |
| 9 | `07-resultados.tex` (8.7), `evaluation/stats.py:438` | "ARE de la prueba empleada (0,864)" | Cota del Wilcoxon declarada como aproximación, o 9/π² (B2) |
| 10 | `06-implementacion.tex:37` | "telefonía (trigger de Twilio)" | Webhook `telefonia-handoff` del backend (B3) |
| 11 | `03-estado-del-arte.tex:62` | Xiong: "poca capacidad para separar aciertos de errores" | Atenuar como en 2.5 y 9.2 (B3) |
| 12 | `04-marco-metodologico.tex` (4.2) | Cronometraje mutuo sin mencionar que el observador de `A1` era autor | B3 |
| 13 | `11-aspectos-legales.tex:34` | "en consonancia con el consentimiento informado" sin registro | Retirar o respaldar con una constancia (B3, B4) |
| 14 | `07-resultados.tex` (8.7) | Dos nombres para la caché del 7-10 | Declarar que son idénticas (B3) |
| 15 | `docs/Tesis/Correcciones/numeros-canonicos.md:816-826` | Estado "no concluyente" | Actualizar (B3) |
| 16 | `11-aspectos-legales.tex:16` | Nivel pago acreditado con una guía de configuración | Comprobante o captura (B4) |
| 17 | `07-resultados.tex` (8.3), `00-glosario.tex` | VIS sin desarrollar | C1 |
| 18 | `12-anexos.tex` (Anexo I, fila "Lím.") | "deja entonces sin concluir … refutada después" | Secuencia temporal explícita (C1) |
| 19 | `02-marco-teorico.tex` (2.4) | Inferencia propia y Zanzotto en una sola oración, sin página | Dividir y paginar (C1) |
| 20 | `Bibliography_base.bib` | FrugalGPT en TMLR sin confirmar; nota de Zendesk con "precios"; URL de Jurafsky y Martin y de ServiceNow sin respuesta | C2 |
| 21 | `11-aspectos-legales.tex` y PDF | 118 páginas frente al tope de 100 del equipo | Decisión D7 registrada; se consigna sin penalizar el cuerpo |

---

*Dictamen elaborado como autoevaluación de control de calidad interno frente a criterios de la CONEAU, a solicitud de los autores. Se basa en la lectura íntegra del manuscrito, el recómputo independiente de las cifras, la verificación bibliográfica externa y el cotejo con el repositorio en el tag `v1.2.13`. No constituye revisión por pares ni pronunciamiento de la cátedra, la dirección, el jurado ni la CONEAU. Rectifica expresamente la definición del conjunto de verdad laxo del brazo manual que el dictamen del 9 de noviembre de 2026 sobre `v1.2.12` había consignado como "unión".*
