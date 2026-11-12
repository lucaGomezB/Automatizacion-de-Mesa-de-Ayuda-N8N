# Respuestas del grupo a las preguntas del tribunal

Documento de respuestas del grupo de autores a las dieciséis preguntas probables de la Sección 8 de la devolución de segunda instancia del tribunal (11 de noviembre de 2026, sobre la versión `v1.2.18`). Las respuestas se agrupan en los cuatro bloques de esa sección: procedencia de los datos (Q1 a Q4), contraste de tiempos (Q5 a Q9), clasificación y supervisión humana (Q10 a Q14) y marco legal (Q15 y Q16).

**Nota de alcance.** Cada respuesta enuncia la pregunta y la responde de forma autónoma. Las respuestas son del grupo de autores: el documento no se atribuye a un modelo de lenguaje ni a ninguna herramienta de IA. Cada hecho afirmado remite a un artefacto versionado del repositorio. Toda cifra de resultado coincide con un valor vigente de `docs/Tesis/Correcciones/numeros-canonicos.md` o se recalcula desde un artefacto versionado. Lo que solo pueden aportar los autores se marca como pendiente y no se presenta como hecho verificado.

---

## Bloque 1. Procedencia de los datos

### Q1. ¿En qué fecha etiquetaron los analistas originales los 200 casos y dónde está la planilla del κ = 0,87, si ese valor ya figuraba en la versión del 3 de julio?

Cada caso del corpus real fue revisado y etiquetado de forma independiente por dos analistas con experiencia en la mesa de ayuda: uno externo al equipo de autores y otro que es también autor del trabajo. Las discrepancias entre analistas se resolvieron por consenso bajo la supervisión del director del trabajo. Ahora bien, el valor κ = 0{,}87 que figuraba en versiones anteriores **no proviene de un etiquetado sobre incidentes reales**: proviene del primer corpus, **sintético**, que los analistas originales sintetizaron alrededor de junio de 2026, antes de contar con el corpus real. Su planilla no se conservó, y por eso ese valor no se presenta como evidencia de fiabilidad. La fecha exacta de ese primer corpus sintético no consta más allá de su primera aparición registrada (4 de junio de 2026).

La fiabilidad de la referencia se estima hoy con el doble etiquetado independiente de la campaña complementaria, a cargo de los etiquetadores `E1` y `E2`, distintos entre sí, de los dos analistas originales, de los autores y de los operadores del brazo manual. Su kappa de Cohen es 0{,}5569 (moderado), con un intervalo de confianza del 95~\% [0{,}4725; 0{,}6413], y su tabla primaria se conserva con su SHA-256.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (subsección 4.4, `subsec:poblacion-muestra-corpus`); `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I, `subsec:nota-versiones`); `docs/Tesis/Correcciones/numeros-canonicos.md` (secciones 3.5, 3.14 y 3.17a); `evaluation/data/campana/doble_etiquetado.csv`; `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-01).

### Q2. La versión de julio informó 165,3 s, 92 % y W = 0. ¿De dónde salieron esas cifras y por qué la tesis actual no lo dice?

La versión del 3 de julio de 2026 informó una reducción del tiempo medio de registro de 165,3 s a 18,2 s (89,0~\%), una exactitud de 92~\%, `W = 0` y un kappa de 0{,}87. Esas cifras provenían de un corpus sintético de 200 casos generado durante el desarrollo, no de incidentes reales. Ese corpus se descartó y se eliminó del repositorio.

La versión actual reemplaza esas cifras por las del corpus real pseudonimizado: tiempo medio de 61,6 s a 17,76 s (reducción de 71,2~\%), exactitud de 73,5~\% y `W = 363`. El kappa de 0{,}87 figuraba en aquella versión, pero sus planillas no se conservan; por eso ya no se presenta como evidencia de fiabilidad.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I, `subsec:nota-versiones`); `docs/anexo_f_corpus.md`; `docs/Tesis/Correcciones/dictamen-correcciones.md`; `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-02).

### Q3. ¿Cómo eligieron 200 incidentes entre unos 2.646, y en qué fechas exactas transcurrió el período relevado?

El universo aproximado es de 2.646 incidentes, proyectado como 42 incidentes diarios sobre los 63 días hábiles del período relevado, del 16 de junio al 10 de septiembre de 2026 (42 × 63 ≈ 2.646). De ese universo se tomó un corpus de 200 casos pseudonimizados mediante un muestreo no probabilístico por conveniencia (disponibilidad): los 200 casos son los incidentes cronometrados en la campaña manual. No hubo estratificación ni asignación proporcional.

La fórmula clásica de muestreo aleatorio simple con corrección por finitud se usa para informar el margen de error implicado por el tamaño del corpus (6{,}66~\%), no como diseño muestral: presupone un muestreo aleatorio que no se realizó, de modo que es una referencia y no una garantía de representatividad.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (subsección 4.4, `subsec:poblacion-muestra-corpus`); `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.4); `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-04).

### Q4. ¿De qué registro se transcribieron los 119 tiempos automatizados de correo y formulario del 2 de octubre?

Los tiempos de correo y formulario (119 casos) se midieron el 2 de octubre de 2026 con el arnés de ingesta `scripts/corpus_ingest/ingest_via_n8n.py`, que envió cada caso por el canal real del flujo N8N con la descripción pseudonimizada. Esos 119 valores constan en el corpus y su registro primario pseudonimizado se versiona en `data/corpus_resultados_web_correo.json`, que reúne 118 de los 119 casos con las marcas de tiempo de la base (ingreso y persistencia); `R001` es el único caso sin registro. El archivo se extrajo del respaldo de la base operativa, que no se versiona.

Ese registro respalda la existencia y la procedencia de los incidentes, no la medición de extremo a extremo: aporta las marcas de tiempo de la base y no el tiempo del corpus, que incluye el envío. El archivo `data/corpus_resultados.json` corresponde a otra corrida y no los respalda. Los 81 tiempos telefónicos, en cambio, coinciden con su registro, `data/corpus_resultados_telefonia.json` (81 de 81).

Fuentes: `data/corpus_resultados_web_correo.json`; `data/README.md`; `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (subsección 4.5); `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (subsección 8.1); `docs/anexo_f_corpus.md`; `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.17e); `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-05).

## Bloque 2. Contraste de tiempos

### Q5. En la campaña complementaria O1 tardó 20,1 s de media y O2 76,6 s. ¿Cuánto de la reducción del 71,2 % depende de quién opere?

En la campaña complementaria, la reducción de la media frente al brazo automatizado de la misma campaña va del 33{,}8~\% con `O1` al 79{,}7~\% con `O2`, y ambas son significativas; el agregado por caso es de 47,6 s frente a 14,6 s, con una reducción del 69{,}3~\%. La magnitud depende de quién opere, porque el tiempo manual no es una propiedad estable del incidente. La reducción se mantiene significativa con el operador más rápido.

Conviene precisar que el brazo automatizado de esta comparación es el de la corrida propia de la campaña complementaria (media de 14,6 s), no el del corpus canónico (17,76 s). Con los tiempos automatizados del corpus canónico sobre esos mismos casos, las reducciones serían del 19,6~\% para `O1`, del 75,9~\% para `O2` y del 62,7~\% en el agregado.

Fuentes: `evaluation/data/campana/brazo_manual.csv`; `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (subsección 8.7, `tab:tiempos-manual-complementaria`); `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` (subsección 9.1); `docs/Tesis/Correcciones/numeros-canonicos.md` (secciones 3.14 y 3.17c); `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-03).

### Q6. ¿La tarea manual de la campaña complementaria (inicio a fin en la planilla) es la misma que la de la campaña 2026-10 (lectura, búsqueda y carga del ticket)?

No. Son tareas distintas. En la campaña complementaria, cada operador recibió una hoja con el identificador y la descripción de cada caso y registró el instante en que tomó el caso y el instante en que asignó el sector; el tiempo así medido corresponde a la decisión de sector y no incluye la lectura, la búsqueda ni la carga del ticket. En la campaña 2026-10, en cambio, el cronometraje incluyó la lectura, la comprensión, la búsqueda y la carga del ticket, y la escucha en telefonía.

Por esa diferencia, los tiempos de la campaña complementaria no son comparables con los de la campaña 2026-10 ni reemplazan el contraste principal de tiempos; alimentan el análisis del efecto de posición y la proporción de tiempo.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (subsecciones 4.5 y 4.6); `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (subsección 8.7); `evaluation/data/campana/brazo_manual.csv`; `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-03).

### Q7. ¿Por qué los tiempos manuales del mismo caso no se correlacionan entre las dos campañas?

El tiempo manual por caso casi no correlaciona entre campañas (Spearman de 0{,}15 para `O1` y de −0{,}05 para `O2`), mientras que los tiempos automatizados de las dos campañas sí correlacionan (ρ = 0{,}70). La causa es que la tarea manual difiere entre campañas (véase Q6) y que el tiempo manual no es una propiedad estable del incidente: depende de quién opera. Los tiempos automatizados, en cambio, son reproducibles porque no dependen del operador.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (subsección 8.7); `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.17c); `evaluation/data/campana/brazo_manual.csv`; `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-03).

### Q8. ¿Qué efecto tiene que las llamadas automatizadas las haya recitado un autor que conocía el caso?

Es la sexta amenaza a la validez declarada en el capítulo metodológico. En la campaña 2026-10, un autor que conocía el caso y el sistema recitó las 81 llamadas del canal telefónico parafraseando la descripción pseudonimizada, desde un softphone VoIP. Un locutor así habla más claro y más breve que un usuario real, lo que favorece el tiempo medido. Pudo favorecer también la transcripción, aunque el canal telefónico obtuvo la exactitud más baja (0,654). No se estimó la magnitud del sesgo y las cifras telefónicas no se extrapolan a usuarios reales.

Las llamadas del brazo telefónico de la campaña complementaria (noviembre de 2026) no las recitó un autor: las recitaron los operadores `O1` y `O2`. Ambas campañas se declaran por separado y no se confunden.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (subsecciones 4.8 y 4.5); `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` (subsección 9.1); `docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex`; `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex` (subsección 11.3); `evaluation/data/campana/`; `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-06).

### Q9. En el formulario web el automático mide 1,88 s desde el envío y el manual 28,7 s desde la lectura. ¿Miden el mismo tramo del proceso?

No. Miden tramos distintos. En el flujo automatizado, el tiempo del formulario web (1,88 s de media) se mide como latencia de extremo a extremo de su procesamiento, desde el envío hasta la persistencia del incidente. En el flujo manual, el tiempo (28,7 s de media) se mide desde la lectura del caso hasta el registro. El tramo automatizado comienza en el envío y el manual, en la lectura.

La misma distinción rige para los demás canales: en telefonía, el tiempo automatizado comprende la duración de la llamada grabada más la latencia de procesamiento posterior al cuelgue, mientras que correo electrónico y formulario web se miden como latencia de extremo a extremo.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (subsecciones 4.5 y 7.1); `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (comparación por canal); `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.8).

## Bloque 3. Clasificación y supervisión humana

### Q10. Si el consenso independiente coincide con la etiqueta original solo en el 84 % de los casos, ¿cuál es la exactitud «verdadera» del clasificador?

La referencia primaria del estudio es el etiquetado original, y las métricas primarias se calculan contra ella. La exactitud estricta contra el consenso independiente `E1 = E2` (138 casos con consenso; el consenso coincide con la etiqueta original en 116 de 138, el 84,1~\%) es de 0{,}7971 (110 de 138, es decir 110/138), con un intervalo de Wilson del 95~\% [0{,}7224; 0{,}8557], frente al 73,5~\% (147 de 200) contra la referencia original.

La exactitud «verdadera» no puede fijarse con una sola cifra: el consenso tiene a su vez fiabilidad limitada (kappa 0{,}5569). Contra el consenso, el límite superior de la exactitud estricta (0{,}856) supera el umbral de 0,85, de modo que con esa referencia el criterio de exactitud sería no concluyente; el macro-F1 contra el consenso (0{,}757) sigue por debajo. El veredicto de la tercera sub-hipótesis se mantiene sobre la referencia primaria.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (`tab:exactitud-etapa-canal`); `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` (subsección 9.3); `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.17d); `evaluation/data/campana/doble_etiquetado.csv`; `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-08).

### Q11. La compuerta de 0,70 no derivó ningún caso y la etapa determinística resuelve el 65,5 % sin derivación por confianza. ¿Qué supervisión humana efectiva tiene hoy el sistema?

La compuerta de 0,70 no derivó ningún caso del corpus. En 124 de los 200 casos (62~\%) la confianza registrada fue inferior a 0,70, pero todos pertenecen a la etapa determinística, cuya confianza mide fuerza de señal y no es el disparador de la derivación. Los 69 casos de la etapa Gemini declararon siempre al menos 0,85 y la etapa de reserva no se activó; el umbral de confianza nunca dispara revisión. El 65,5~\% (131 de 200) es la cobertura de la etapa determinística, no una proporción de derivación.

La supervisión humana efectiva tiene tres componentes. El primero es la compuerta sobre la salida de Gemini, que no se activa en el rango observado. El segundo es la regla de derivación por reportante no identificado, que el backend aplica desde el 13 de octubre de 2026 cuando el reportante no se resuelve en el directorio de empleados (requisito `VIS-005`); por esa regla la revisión alcanzó 66 casos de correo electrónico y 81 de telefonía y ninguno de los 53 del formulario web, y el export de intervenciones de la campaña complementaria registró 147 intervenciones instrumentadas por caso con su origen. El tercero es la reasignación trazable del incidente, disponible en la interfaz REST. El análisis de calibración muestra que el umbral de 0,70 no garantiza la detección de errores.

Fuentes: `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 4 y sección 3.7, gate por etapa); `docs/Tesis/v10 (IA)/paper/sections/05-arquitectura.tex`; `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (subsección 8.4); `evaluation/data/campana/intervenciones.csv`.

### Q12. De 85 confirmaciones humanas con consenso disponible, 11 confirmaron un sector incorrecto. ¿Qué dice eso de la revisión como salvaguarda?

Se informa como dato, sin lectura causal. De las 85 confirmaciones con consenso disponible, 11 confirmaron un sector que el consenso considera incorrecto; de los 25 cambios de derivación, 13 tienen consenso (9 correcciones, 1 empeoramiento y 3 de un error a otro). La revisión humana no es, por lo tanto, una salvaguarda perfecta: confirma un sector incorrecto en una fracción de los casos con consenso disponible. La referencia contra la que se mide esa confirmación tiene, a su vez, fiabilidad limitada (kappa 0{,}5569).

Fuentes: `evaluation/data/campana/intervenciones.csv`; `evaluation/data/campana/doble_etiquetado.csv`; `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (subsección 8.4); `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-08).

### Q13. ¿Cuándo se fijó la regla de tres vías de la segunda sub-hipótesis, antes o después de conocer el 17,0 %?

Después. La regla de tres vías prefijada (compatible, refutada o no concluyente según el intervalo de Wilson frente a la cota de 0,15) se aplicó al cociente 25 de 200 (12,5~\%; IC de Wilson [8,6~\%, 17,8~\%]), cuyo límite superior supera 0,15, y dio un resultado no concluyente. El denominador de 147 casos revisados y la lectura de la regla con ese denominador se adoptaron después de conocer los datos: no estaban fijados de antemano.

Sobre los 147 revisados, la estimación puntual (17,0~\%) queda por encima de la cota y la lectura literal de la regla daría refutada; sin embargo, el intervalo [11,8~\%, 23,9~\%] contiene 0,15 y la prueba binomial unilateral no rechaza la cota (p = 0{,}28 unilateral; 0{,}49 bilateral). El estado vigente de la segunda sub-hipótesis es no concluyente, con estimación puntual por encima de la cota.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/01-introduccion.tex` (subsección 1.4); `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (subsección 4.7); `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (subsección 8.3); `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I); `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.17b); `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-09).

### Q14. Con el escenario central el balance neto es de −18,5 a −43,9 horas-persona por trimestre. ¿Recomendarían adoptar el sistema hoy?

El balance neto es condicional al costo por derivación errónea, que es una estimación propia (10 a 15 minutos) porque la campaña no cronometra las reasignaciones. Con una tasa de derivación errónea manual del 15~\% y entre 10 y 15 minutos por reasignación, el clasificador agrega unas 304 derivaciones erróneas por trimestre, que cuestan entre 50,7 y 76,1 horas-persona frente a las 32,2 de ahorro bruto: un balance de −18{,}5 a −43{,}9 horas-persona. El intervalo de Wilson de la exactitud estricta, [67,0~\%, 79,1~\%], contiene a la exactitud mínima de equilibrio 77,7~\% (15~\%, 10 minutos), de modo que ni con esos supuestos la muestra fija el signo del balance; con 15 minutos, la exactitud mínima de equilibrio (80,1~\%) lo supera.

La recomendación del grupo es adoptar el sistema de forma gradual y condicionada. Están sostenidas la viabilidad técnica (reducción del 71,2~\% del tiempo de registro) y la económica (costo monetario marginal); la viabilidad operativa es condicional a que la exactitud efectiva supere la exactitud mínima de equilibrio. Por eso la recomendación incluye monitorear la exactitud y cronometrar las reasignaciones antes de un despliegue definitivo.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` (subsección 9.5, `subsec:balance-neto`, `tab:balance-neto`); `docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex`; `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex`; `docs/Tesis/Correcciones/numeros-canonicos.md` (secciones 3.11 y 3.14).

## Bloque 4. Marco legal

### Q15. ¿Se firmó alguna cláusula contractual modelo de la Disposición 60-E/2016 con Google o Twilio, o en el estudio solo se transfirieron datos pseudonimizados y audio recitado?

En el estudio no se suscribieron cláusulas contractuales modelo de la Disposición 60-E/2016 con Google ni con Twilio, y no se recabó el consentimiento de los titulares para la transferencia. El instrumento de transferencia internacional está documentado en el repositorio, pero no está suscrito: la suscripción es una acción organizacional de la organización adoptante, fuera del alcance del repositorio.

A los proveedores llegaron solo descripciones pseudonimizadas de los incidentes, en forma de texto (119 casos) y de audio recitado por uno de los autores a partir de esas descripciones (81 casos). Las condiciones de servicio aceptadas con cada proveedor complementan el instrumento, pero no lo sustituyen. El instrumento de transferencia queda como requisito previo para la organización adoptante antes de operar con datos reales de sus usuarios.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex` (subsección 11.3, `subsec:transferencia-internacional`); `docs/seguridad/instrumento-transferencia-internacional.md`; `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-13).

### Q16. Las autoevaluaciones del Anexo I se generaron con un modelo de lenguaje. ¿Qué parte del texto de la tesis fue redactada con asistencia de un modelo de lenguaje y cómo lo declaran?

Las autoevaluaciones del Anexo I se generaron con un modelo de lenguaje: son nueve revisiones de control de calidad interno frente a criterios de la CONEAU, elaboradas aplicando un perfil de evaluador versionado en `docs/Tesis/Correcciones/Prompt2.docx`. No son una revisión por pares: no las emitieron el jurado, la dirección, la cátedra ni la CONEAU, y no son vinculantes. El Anexo I las declara como tales.

Sobre la redacción del cuerpo del documento (declaración de los autores): la redacción de esta tesis contó con asistencia de un modelo de lenguaje para la corrección de estilo y la edición del texto, y para la generación de diagramas de flujo a partir de la estructura planteada previamente. El diseño metodológico, la recolección y verificación de datos, las decisiones de contenido y la responsabilidad final del texto son de los autores. Esta declaración consta también en el Anexo I.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I, `subsec:nota-versiones` y trazabilidad); `docs/Tesis/Correcciones/dictamen-correcciones.md`.
