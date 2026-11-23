# Respuestas del grupo a las preguntas del tribunal

Documento de respuestas del grupo de autores a dos devoluciones del tribunal. La primera parte responde a las dieciséis preguntas de la Sección 8 de la devolución de segunda instancia (11 de noviembre de 2026, sobre la versión `v1.2.18`); la segunda, a las doce preguntas de la Sección 8 de la devolución de tercera instancia (16 de noviembre de 2026, sobre la versión `v1.5.2`). Las respuestas se verificaron contra el ejemplar corregido en la versión `v1.6.0`, posterior a los changes c-235 a c-238. Cada parte se agrupa en los cuatro bloques de la Sección 8 respectiva.

**Nota de alcance.** Cada respuesta enuncia la pregunta y la responde de forma autónoma. Las respuestas son del grupo de autores: el documento no se atribuye a un modelo de lenguaje ni a ninguna herramienta de IA. Cada hecho afirmado remite a un artefacto versionado del repositorio o a un insumo escrito de los autores registrado en la trazabilidad del proyecto. Toda cifra de resultado coincide con un valor vigente de `docs/Tesis/Correcciones/numeros-canonicos.md` o se recalcula desde un artefacto versionado. Lo que solo pueden aportar los autores se marca como pendiente y no se presenta como hecho verificado.

---

# Primera parte. Devolución de segunda instancia (11-11-2026)

## Bloque 1. Procedencia de los datos

### Q1. ¿En qué fecha etiquetaron los analistas originales los 200 casos y dónde está la planilla del κ = 0,87, si ese valor ya figuraba en la versión del 3 de julio?

Cada caso del corpus real fue revisado y etiquetado de forma independiente por dos analistas con experiencia en la mesa de ayuda: uno externo al equipo de autores y otro que es también autor del trabajo. Las discrepancias entre analistas se resolvieron por consenso bajo la supervisión del director del trabajo. Ahora bien, el valor κ = 0,87 que figuraba en versiones anteriores **no proviene de un etiquetado sobre incidentes reales**: proviene del primer corpus, **sintético**, que los analistas originales sintetizaron alrededor de junio de 2026, antes de contar con el corpus real. Su planilla no se conservó, y por eso ese valor no se presenta como evidencia de fiabilidad. La fecha exacta de ese primer corpus sintético no consta más allá de su primera aparición registrada (4 de junio de 2026).

La fiabilidad de la referencia se estima hoy con el doble etiquetado independiente de la campaña complementaria, a cargo de los etiquetadores `E1` y `E2`, distintos entre sí, de los dos analistas originales, de los autores y de los operadores del brazo manual. Su kappa de Cohen es 0,5569 (moderado), con un intervalo de confianza del 95 % [0,4725; 0,6413], y su tabla primaria se conserva con su SHA-256.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (§4.4, `subsec:poblacion-muestra-corpus`); `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I, `subsec:nota-versiones`); `docs/Tesis/Correcciones/numeros-canonicos.md` (secciones 3.5, 3.14 y 3.17a); `evaluation/data/campana/doble_etiquetado.csv`; `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-01).

### Q2. La versión de julio informó 165,3 s, 92 % y W = 0. ¿De dónde salieron esas cifras y por qué la tesis actual no lo dice?

La versión del 3 de julio de 2026 informó una reducción del tiempo medio de registro de 165,3 s a 18,2 s (89,0 %), una exactitud de 92 %, `W = 0` y un kappa de 0,87. Esas cifras provenían de un corpus sintético de 200 casos generado durante el desarrollo, no de incidentes reales. Ese corpus se descartó y se eliminó del repositorio.

La versión actual reemplaza esas cifras por las del corpus real pseudonimizado: tiempo medio de 61,6 s a 17,76 s (reducción de 71,2 %), exactitud de 73,5 % y `W = 363`. El kappa de 0,87 figuraba en aquella versión, pero sus planillas no se conservan; por eso ya no se presenta como evidencia de fiabilidad.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I, `subsec:nota-versiones`); `docs/anexo_f_corpus.md`; `docs/Tesis/Correcciones/dictamen-correcciones.md`; `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-02).

### Q3. ¿Cómo eligieron 200 incidentes entre unos 2.646, y en qué fechas exactas transcurrió el período relevado?

El universo aproximado es de 2.646 incidentes, proyectado como 42 incidentes diarios sobre los 63 días hábiles del período relevado, del 16 de junio al 10 de septiembre de 2026 (42 × 63 ≈ 2.646). De ese universo se tomó un corpus de 200 casos pseudonimizados mediante un muestreo no probabilístico por conveniencia (disponibilidad): los 200 casos son los incidentes cronometrados en la campaña manual. No hubo estratificación ni asignación proporcional.

La fórmula clásica de muestreo aleatorio simple con corrección por finitud se usa para informar el margen de error implicado por el tamaño del corpus (6,66 %), no como diseño muestral: presupone un muestreo aleatorio que no se realizó, de modo que es una referencia y no una garantía de representatividad.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (§4.4, `subsec:poblacion-muestra-corpus`); `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.4); `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-04).

### Q4. ¿De qué registro se transcribieron los 119 tiempos automatizados de correo y formulario del 2 de octubre?

Los tiempos de correo y formulario (119 casos) se midieron el 2 de octubre de 2026 con el arnés de ingesta `scripts/corpus_ingest/ingest_via_n8n.py`, que envió cada caso por el canal real del flujo N8N con la descripción pseudonimizada. Esos 119 valores constan en el corpus y su registro primario pseudonimizado se versiona en `data/corpus_resultados_web_correo.json`, que reúne 118 de los 119 casos con las marcas de tiempo de la base (ingreso y persistencia); `R001` es el único caso sin registro. El archivo se extrajo del respaldo de la base operativa, que no se versiona.

Ese registro respalda la existencia y la procedencia de los incidentes, no la medición de extremo a extremo: aporta las marcas de tiempo de la base y no el tiempo del corpus, que incluye el envío. El archivo `data/corpus_resultados.json` corresponde a otra corrida y no los respalda. Los 81 tiempos telefónicos, en cambio, coinciden con su registro, `data/corpus_resultados_telefonia.json` (81 de 81).

Fuentes: `data/corpus_resultados_web_correo.json`; `data/README.md`; `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (§4.5, `subsec:protocolo-pruebas`); `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (§8.1, `subsec:comparacion-tiempos`); `docs/anexo_f_corpus.md`; `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.17e); `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-05).

## Bloque 2. Contraste de tiempos

### Q5. En la campaña complementaria O1 tardó 20,1 s de media y O2 76,6 s. ¿Cuánto de la reducción del 71,2 % depende de quién opere?

En la campaña complementaria, la reducción de la media frente al brazo automatizado de la misma campaña va del 33,8 % con `O1` al 79,7 % con `O2`, y ambas son significativas; el agregado por caso es de 47,6 s frente a 14,6 s, con una reducción del 69,3 %. La magnitud depende de quién opere, porque el tiempo manual no es una propiedad estable del incidente. La reducción se mantiene significativa con el operador más rápido.

Conviene precisar que el brazo automatizado de esta comparación es el de la corrida propia de la campaña complementaria (media de 14,6 s), no el del corpus canónico (17,76 s). Con los tiempos automatizados del corpus canónico sobre esos mismos casos, las reducciones serían del 19,6 % para `O1`, del 75,9 % para `O2` y del 62,7 % en el agregado.

Fuentes: `evaluation/data/campana/brazo_manual.csv`; `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (§8.6, `subsec:resultados-campana-medicion`, `tab:tiempos-manual-complementaria`); `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` (§9.1, `subsec:interpretacion-resultados`); `docs/Tesis/Correcciones/numeros-canonicos.md` (secciones 3.14 y 3.17c); `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-03).

### Q6. ¿La tarea manual de la campaña complementaria (inicio a fin en la planilla) es la misma que la de la campaña 2026-10 (lectura, búsqueda y carga del ticket)?

No. Son tareas distintas. En la campaña complementaria, cada operador recibió una hoja con el identificador y la descripción de cada caso y registró el instante en que tomó el caso y el instante en que asignó el sector; el tiempo así medido corresponde a la decisión de sector y no incluye la lectura, la búsqueda ni la carga del ticket. En la campaña 2026-10, en cambio, el cronometraje incluyó la lectura, la comprensión, la búsqueda y la carga del ticket, y la escucha en telefonía.

Por esa diferencia, los tiempos de la campaña complementaria no son comparables con los de la campaña 2026-10 ni reemplazan el contraste principal de tiempos; alimentan el análisis del efecto de posición y la proporción de tiempo.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (§4.5, `subsec:protocolo-pruebas`, y §4.6, `subsec:metricas-instrumentos`); `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (§8.6, `subsec:resultados-campana-medicion`); `evaluation/data/campana/brazo_manual.csv`; `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-03).

### Q7. ¿Por qué los tiempos manuales del mismo caso no se correlacionan entre las dos campañas?

El tiempo manual por caso casi no correlaciona entre campañas (Spearman de 0,15 para `O1` y de −0,05 para `O2`), mientras que los tiempos automatizados de las dos campañas sí correlacionan (ρ = 0,70). La causa es que la tarea manual difiere entre campañas (véase Q6) y que el tiempo manual no es una propiedad estable del incidente: depende de quién opera. Los tiempos automatizados, en cambio, son reproducibles porque no dependen del operador.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (§8.6, `subsec:resultados-campana-medicion`); `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.17c); `evaluation/data/campana/brazo_manual.csv`; `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-03).

### Q8. ¿Qué efecto tiene que las llamadas automatizadas las haya recitado un autor que conocía el caso?

Es la sexta amenaza a la validez declarada en el capítulo metodológico. En la campaña 2026-10, un autor que conocía el caso y el sistema recitó las 81 llamadas del canal telefónico parafraseando la descripción pseudonimizada, desde un softphone VoIP. Un locutor así habla más claro y más breve que un usuario real, lo que favorece el tiempo medido. Pudo favorecer también la transcripción, aunque el canal telefónico obtuvo la exactitud más baja (0,654). No se estimó la magnitud del sesgo y las cifras telefónicas no se extrapolan a usuarios reales.

Las llamadas del brazo telefónico de la campaña complementaria (noviembre de 2026) no las recitó un autor: las recitaron los operadores `O1` y `O2`. Ambas campañas se declaran por separado y no se confunden.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (§4.8, `subsec:amenazas-validez`, y §4.5, `subsec:protocolo-pruebas`); `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` (§9.1, `subsec:interpretacion-resultados`); `docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex` (§10); `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex` (§7.3, `subsec:transferencia-internacional`); `evaluation/data/campana/`; `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-06).

### Q9. En el formulario web el automático mide 1,88 s desde el envío y el manual 28,7 s desde la lectura. ¿Miden el mismo tramo del proceso?

No. Miden tramos distintos. En el flujo automatizado, el tiempo del formulario web (1,88 s de media) se mide como latencia de extremo a extremo de su procesamiento, desde el envío hasta la persistencia del incidente. En el flujo manual, el tiempo (28,7 s de media) se mide desde la lectura del caso hasta el registro. El tramo automatizado comienza en el envío y el manual, en la lectura.

La misma distinción rige para los demás canales: en telefonía, el tiempo automatizado comprende la duración de la llamada grabada más la latencia de procesamiento posterior al cuelgue, mientras que correo electrónico y formulario web se miden como latencia de extremo a extremo.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (§4.5, `subsec:protocolo-pruebas`, y §4.6, `subsec:metricas-instrumentos`); `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (§8.1, `subsec:comparacion-tiempos`); `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.8).

## Bloque 3. Clasificación y supervisión humana

### Q10. Si el consenso independiente coincide con la etiqueta original solo en el 84 % de los casos, ¿cuál es la exactitud «verdadera» del clasificador?

La referencia primaria del estudio es el etiquetado original, y las métricas primarias se calculan contra ella. La exactitud estricta contra el consenso independiente `E1 = E2` (138 casos con consenso; el consenso coincide con la etiqueta original en 116 de 138, el 84,1 %) es de 0,7971 (110 de 138, es decir 110/138), con un intervalo de Wilson del 95 % [0,7224; 0,8557], frente al 73,5 % (147 de 200) contra la referencia original.

La exactitud «verdadera» no puede fijarse con una sola cifra: el consenso tiene a su vez fiabilidad limitada (kappa 0,5569). Contra el consenso, el límite superior de la exactitud estricta (0,856) supera el umbral de 0,85, de modo que con esa referencia el criterio de exactitud sería no concluyente; el macro-F1 contra el consenso (0,757) sigue por debajo. El veredicto de la tercera sub-hipótesis se mantiene sobre la referencia primaria.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (§8.2, `subsec:matriz-metricas`, `tab:exactitud-etapa-canal`); `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` (§9.3, `subsec:limitaciones-estudio`); `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.17d); `evaluation/data/campana/doble_etiquetado.csv`; `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-08).

### Q11. La compuerta de 0,70 no derivó ningún caso y la etapa determinística resuelve el 65,5 % sin derivación por confianza. ¿Qué supervisión humana efectiva tiene hoy el sistema?

La compuerta de 0,70 no derivó ningún caso del corpus. En 124 de los 200 casos (62 %) la confianza registrada fue inferior a 0,70, pero todos pertenecen a la etapa determinística, cuya confianza mide fuerza de señal y no es el disparador de la derivación. Los 69 casos de la etapa Gemini declararon siempre al menos 0,85 y la etapa de reserva no se activó; el umbral de confianza nunca dispara revisión. El 65,5 % (131 de 200) es la cobertura de la etapa determinística, no una proporción de derivación.

La supervisión humana efectiva tiene tres componentes. El primero es la compuerta sobre la salida de Gemini, que no se activa en el rango observado. El segundo es la regla de derivación por reportante no identificado, que el backend aplica desde el 13 de octubre de 2026 cuando el reportante no se resuelve en el directorio de empleados (requisito `VIS-005`); por esa regla la revisión alcanzó 66 casos de correo electrónico y 81 de telefonía y ninguno de los 53 del formulario web, y el export de intervenciones de la campaña complementaria registró 147 intervenciones instrumentadas por caso con su origen. El tercero es la reasignación trazable del incidente, disponible en la interfaz REST. El análisis de calibración muestra que el umbral de 0,70 no garantiza la detección de errores.

Fuentes: `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 4 y sección 3.7, gate por etapa); `docs/Tesis/v10 (IA)/paper/sections/05-arquitectura.tex` (§5, `subsec:subsistema-clasificacion`); `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (§8.3, `subsec:reduccion-intervencion`, y §8.4, `subsec:calibracion`); `evaluation/data/campana/intervenciones.csv`.

### Q12. De 85 confirmaciones humanas con consenso disponible, 11 confirmaron un sector incorrecto. ¿Qué dice eso de la revisión como salvaguarda?

Se informa como dato, sin lectura causal. De las 85 confirmaciones con consenso disponible, 11 confirmaron un sector que el consenso considera incorrecto; de los 25 cambios de derivación, 13 tienen consenso (9 correcciones, 1 empeoramiento y 3 de un error a otro). La revisión humana no es, por lo tanto, una salvaguarda perfecta: confirma un sector incorrecto en una fracción de los casos con consenso disponible. La referencia contra la que se mide esa confirmación tiene, a su vez, fiabilidad limitada (kappa 0,5569).

Fuentes: `evaluation/data/campana/intervenciones.csv`; `evaluation/data/campana/doble_etiquetado.csv`; `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (§8.3, `subsec:reduccion-intervencion`); `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-08).

### Q13. ¿Cuándo se fijó la regla de tres vías de la segunda sub-hipótesis, antes o después de conocer el 17,0 %?

Después. La regla de tres vías prefijada (compatible, refutada o no concluyente según el intervalo de Wilson frente a la cota de 0,15) se aplicó al cociente 25 de 200 (12,5 %; IC de Wilson [8,6 %, 17,8 %]), cuyo límite superior supera 0,15, y dio un resultado no concluyente. El denominador de 147 casos revisados y la lectura de la regla con ese denominador se adoptaron después de conocer los datos: no estaban fijados de antemano.

Sobre los 147 revisados, la estimación puntual (17,0 %) queda por encima de la cota y la lectura literal de la regla daría refutada; sin embargo, el intervalo [11,8 %, 23,9 %] contiene 0,15 y la prueba binomial unilateral no rechaza la cota (p = 0,28 unilateral; 0,49 bilateral). El estado vigente de la segunda sub-hipótesis es no concluyente, con estimación puntual por encima de la cota.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/01-introduccion.tex` (§1.4, `subsec:hipotesis-trabajo`); `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (§4.7, `subsec:analisis-estadistico`); `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (§8.3, `subsec:reduccion-intervencion`); `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I); `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.17b); `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-09).

### Q14. La versión anterior informaba, con el escenario central, un balance neto de −18,5 a −43,9 horas-persona por trimestre (lectura superada y retirada). ¿Recomendarían adoptar el sistema hoy?

El balance neto vigente es una **cota superior condicional**, no un valor con el signo fijado por la muestra. El costo de una derivación errónea se mide como `c = 69,51 s` (IC 95 % [33,42; 106,56] s) y cubre solo el tramo activo —la corrección en la compuerta de revisión y la re-decisión de sector tomada como proxy del rediagnóstico—, porque la compuerta no detecta errores en la configuración evaluada (AUROC 0,5168; ninguna derivación por confianza): el error llega al sector receptor y el tramo de reanudación queda sin cota. Por eso `c` es una cota inferior del costo. Con el término de revisión incorporado (`ρ·r = 0,735 × 22,06 s`) y ambas tasas de error medidas contra la referencia común (`e_aut = 28/138`; `e_man = 26/151`), el balance neto trimestral es `B_r = +18,7` horas-persona, con intervalo condicional [+12,9; +24,1] y cota combinada [+6,7; +28,2], que corresponde al tramo activo medido y no al balance real. La exactitud mínima de equilibrio es `a*_r = 43,1 %` (IC condicional [33,6; 53,7] %).

La recomendación del grupo es adoptar el sistema de forma gradual y condicionada. La viabilidad técnica (reducción del 71,2 % del tiempo de registro) y el costo monetario marginal de la inferencia están sostenidos; la viabilidad operativa es condicional a que la exactitud efectiva supere la exactitud mínima de equilibrio. Cronometrar por separado cada reasignación —incluido el tiempo que el sector receptor tarda en advertir el error y devolver el ticket— es la medición que fijaría el signo del balance. La lectura histórica de la versión anterior (balance de −18,5 a −43,9 horas-persona, con un costo supuesto y sin término de revisión) queda superada y no es la lectura vigente.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` (§9.5, `subsec:balance-neto`, `tab:balance-neto`); `docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex` (§10); `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex` (§11); `docs/Tesis/Correcciones/numeros-canonicos.md` (secciones 3.11 y 3.46).

## Bloque 4. Marco legal

### Q15. ¿Se firmó alguna cláusula contractual modelo de la Disposición 60-E/2016 con Google o Twilio, o en el estudio solo se transfirieron datos pseudonimizados y audio recitado?

En el estudio no se suscribieron cláusulas contractuales modelo de la Disposición 60-E/2016 con Google ni con Twilio. El instrumento aplicado para el régimen (a) del corpus —incidentes reales del entorno operativo del propio equipo, pseudonimizados— fue el consentimiento expreso de los titulares, notificado el 2026-10-01 y prestado verbalmente el 2026-10-02, documentado en el acta T2 (`docs/seguridad/acta-consentimiento-t2.md`), redactada el 2026-11-17 y firmada el 2026-11-20; son posteriores a la notificación la corrida de texto del 2026-10-02, la corrida de clasificación del 2026-10-07, las transferencias de audio del 5 y 6 de octubre, la campaña complementaria del 5 y 6 de noviembre, las corridas pagas del 12 y 13 de noviembre y las sondas pagas del 17 y 18 de noviembre; la pseudonimización y la minimización refuerzan esa salvaguarda, pero no sustituyen el instrumento. El régimen (b) del corpus —reconstrucciones de tipos de incidente reales sin datos de terceros— no contiene datos personales ni supone transferencia de datos personales. El instrumento de transferencia internacional está documentado en el repositorio, pero no está suscrito: la suscripción es una acción organizacional de la organización adoptante, fuera del alcance del repositorio.

A los proveedores llegaron, en primer lugar, descripciones pseudonimizadas de los incidentes, en forma de texto (119 casos) y de audio recitado por uno de los autores a partir de esas descripciones (81 casos). En las corridas pagas del 12 y el 13 de noviembre de 2026 se enviaron además los textos de la validación fuera de muestra retirada de la presente versión (véase Q16): descripciones de incidentes elaboradas por los autores, sin datos personales ni de terceros. Las condiciones de servicio aceptadas con cada proveedor complementan el instrumento, pero no lo sustituyen. El instrumento de transferencia queda como requisito previo para la organización adoptante antes de operar con datos reales de sus usuarios.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex` (§7.3, `subsec:transferencia-internacional`, y §7.5, `subsec:consentimiento-derechos`); `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I, `subsec:nota-versiones`); `docs/seguridad/instrumento-transferencia-internacional.md`; `docs/seguridad/acta-consentimiento-t2.md`; `auditorias/Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.md` (N-13).

### Q16. Las autoevaluaciones del Anexo I se generaron con un modelo de lenguaje. ¿Qué parte del texto de la tesis fue redactada con asistencia de un modelo de lenguaje y cómo lo declaran?

La declaración vigente del uso de asistentes de inteligencia artificial consta en la subsección «Declaración de uso de asistentes de inteligencia artificial» del Anexo I (`subsec:declaracion-uso-ia`). El desarrollo del sistema, los scripts de análisis y evaluación y la redacción de la tesis se realizaron con asistencia sistemática de agentes de código basados en modelos de lenguaje; el trabajo se organizó en changes con especificación previa (propuesta, diseño y tareas) que los autores definían y revisaban, y el agente implementaba las tareas mientras los autores aceptaban o rechazaban cada resultado.

La declaración detalla, por ámbito, qué produjo el asistente y cómo verificaron los autores cada cifra y cada afirmación: el código del sistema (backend, frontend y flujo N8N), los scripts de análisis y evaluación (y el recálculo de las cifras que citan), el texto de la tesis (borradores de prosa), los diagramas y las autoevaluaciones estilo CONEAU. La verificación de los autores se apoyó en las suites de pruebas del backend y de `evaluation/`, en `verify_citations.py`, en el memo de números canónicos y en la revisión de cada change antes de archivarlo. Las autoevaluaciones del Anexo I son informes internos frente a criterios de la CONEAU, elaborados con el perfil de evaluador `Prompt2.docx`; no son una revisión por pares ni son vinculantes. El diseño metodológico, la recolección de datos (que comprende las mediciones de tiempo y el etiquetado) y las decisiones de contenido son de los autores, que asumen la responsabilidad final de cada cifra y cada afirmación.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I, `subsec:declaracion-uso-ia`); `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md`; `docs/Tesis/Correcciones/dictamen-correcciones.md`.

---

# Segunda parte. Devolución de tercera instancia (16-11-2026)

## Bloque 1. Corpus fuera de muestra

### P1. ¿Quiénes son E3, E4 y E5 respecto de la compañía financiera y de los autores, y cómo registraron el inicio y el fin de cada caso?

`E3`, `E4` y `E5` son etiquetadores externos al proyecto: personas distintas entre sí y distintas de los autores, con formularios de consentimiento firmados; efectivamente etiquetaron. No hubo, sin embargo, una compañía financiera que autorizara el uso de sus incidentes: el corpus que se presentaba como «fuera de muestra» no provenía de una organización. Por eso la validación fuera de muestra se retiró del ejemplar y no puede acreditarse cómo se generaron las marcas temporales ni las etiquetas de `E3`, `E4` y `E5`.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I, `subsec:nota-versiones`); `docs/Tesis/Correcciones/dictamen-correcciones.md` (entrada `c-235`, compuertas P1, P2 y P8); `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.45).

### P2. ¿Por qué todas las duraciones de E3, E4 y E5 caen entre 30 y 90 s y ninguna pausa entre casos supera los 8 s?

No puede acreditarse cómo se generaron las marcas temporales de `E3`, `E4` y `E5`, ni por qué sus duraciones caen en ese intervalo y sus pausas son tan breves. Esa imposibilidad de acreditación es una de las razones por las que la validación fuera de muestra se retiró del ejemplar: la tesis no la presenta como un registro primario de una organización.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I, `subsec:nota-versiones`); `docs/Tesis/Correcciones/dictamen-correcciones.md` (entrada `c-235`, compuerta P2); `auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md` (K-01).

### P3. ¿De qué sistema se exportaron los 56 casos de refuerzo (retirados del ejemplar)? ¿En qué fecha ocurrieron, por ejemplo, la intrusión en SCADA (I182) y el incendio del CPD (I194)?

Los 56 casos de refuerzo, retirados del ejemplar, no se exportaron de un sistema de una compañía: los redactó un autor el 13 de noviembre de 2026 a partir de una investigación en fuentes de internet sobre incidentes comunes de la clase `Sistemas`. Las fechas y los eventos que describen (entre ellos las intrusiones y el incendio mencionados) forman parte de la construcción de los casos y no la ocurrencia de incidentes reales. Los 56 casos de refuerzo se retiran del ejemplar junto con la validación fuera de muestra.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I, `subsec:nota-versiones`); `docs/Tesis/Correcciones/dictamen-correcciones.md` (entrada `c-235`, compuertas P3 y P6); `auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md` (K-01).

### P4. ¿La compañía autorizó el uso de sus incidentes, su publicación en el repositorio y su envío a Google?

No hay una compañía que autorice: los 150 textos presentados como «originales» los construyó un autor sobre escenarios base generados por un asistente de inteligencia artificial (Gemini 3.1), curados y adaptados a mano, y no contienen datos personales ni de terceros. Se enviaron a la Gemini API en la corrida paga, lo que consta en el §7.3. Como no había datos de terceros, no correspondía una autorización de organización; la presentación del corpus como registro de una compañía no era exacta, y por eso se retiran de la versión vigente del repositorio público los dos archivos del corpus de esa validación.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex` (§7.3, `subsec:transferencia-internacional`, y §7.5, `subsec:consentimiento-derechos`); `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I, `subsec:nota-versiones`); `docs/Tesis/Correcciones/dictamen-correcciones.md` (entradas `c-235` y `c-240`, compuertas P4 y Alcance del retiro).

### P5. ¿Cómo se asignaron las áreas de la compañía a los cinco sectores de la organización de Mendoza?

No hay áreas de una compañía que mapear. Como el corpus no provenía de una organización real, no existe una correspondencia de áreas a los cinco sectores; los etiquetadores asignaron el sector al etiquetar cada descripción construida. La validación fuera de muestra se retiró del ejemplar y con ella la cuestión del desajuste de taxonomía entre organizaciones.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I, `subsec:nota-versiones`); `docs/Tesis/Correcciones/dictamen-correcciones.md` (entrada `c-235`, compuerta P5); `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.45).

## Bloque 2. Balance neto

### P6. Cuando una derivación errónea llega al sector equivocado, ¿cuánto tarda ese sector en advertirlo y devolverla? ¿Por qué los 45,5 s de decisión de sector del brazo manual representan ese costo?

El tramo de reanudación —advertir el error y devolver el ticket— no se midió y queda sin cota disponible, como declara el Anexo J. Los 45,50 s son la mediana de decisión de sector del brazo manual, que se usa como proxy del rediagnóstico (el tramo activo), no de la reanudación. Por eso el costo medido `c = 69,51 s` es una cota inferior del costo real: suma 24,01 s del tramo de corrección en la compuerta de revisión y 45,50 s del proxy de rediagnóstico, y deja fuera la reanudación.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` (§9.5, `subsec:balance-neto`); `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo J, `sec:anexo-numeros-canonicos`); `docs/Tesis/Correcciones/numeros-canonicos.md` (secciones 3.11 y 3.46).

### P7. ¿Por qué el balance no descuenta los 22 s de revisión por caso que su propio análisis midió?

El balance vigente **sí** descuenta el término de revisión: incorpora `ρ·r = 0,735 × 22,06 s`, donde `r = 22,06 s` es el tiempo-persona medio por revisión (media de las 138 duraciones) que el propio análisis del grupo midió. La versión anterior no incluía ese término; la corrección que lo incorpora es la que sostiene la lectura vigente como cota superior. El término de revisión solo resta del lado automatizado, porque el flujo manual no tiene una revisión equivalente posterior al registro.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` (§9.5, `subsec:balance-neto`); `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo J); `docs/Tesis/Correcciones/numeros-canonicos.md` (secciones 3.46).

### P8. La versión anterior informaba que, con la exactitud fuera de muestra y 10 minutos por reasignación, el balance era de −28,9 horas-persona (lectura retirada con la validación fuera de muestra). ¿Qué le recomendarían hoy a una organización adoptante?

La lectura con la exactitud fuera de muestra ya no forma parte del ejemplar: la validación fuera de muestra se retiró. El balance vigente es una cota superior condicional: `B_r = +18,7` horas-persona por trimestre, con el término de revisión incluido y el costo medido como cota inferior; el signo depende del tramo de reanudación no medido. La recomendación a una organización adoptante es adoptar de forma gradual y condicionada: sostener la viabilidad técnica y el costo monetario marginal, monitorear la exactitud efectiva frente a la exactitud mínima de equilibrio (`a*_r = 43,1 %`) y cronometrar por separado cada reasignación antes de un despliegue definitivo. Es la misma recomendación de Q14.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` (§9.5, `subsec:balance-neto`, `tab:balance-neto`); `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I, `subsec:nota-versiones`); `docs/Tesis/Correcciones/numeros-canonicos.md` (secciones 3.45 y 3.46).

## Bloque 3. Clasificación

### P9. En el bloque primario, el brazo de modelo solo acertó más que el híbrido. ¿Qué aporta hoy la etapa de reglas, además del ahorro de llamadas?

La hipótesis subsidiaria de eficiencia frente a un esquema solo de modelo queda **sin contraste limpio**: la comparación anclaba en la validación fuera de muestra, que se retiró del ejemplar. La etapa de reglas aporta la mayor parte de la cobertura del sistema: resuelve el 65,5 % de los casos (131 de 200) sin escalar a la etapa Gemini, con lo que evita esas llamadas y acota el costo monetario marginal de la inferencia. En el rango observado, la confianza de Gemini no discrimina aciertos de errores (AUROC 0,5168), de modo que el aporte de la etapa de reglas es de cobertura y de costo, no de exactitud adicional; el veredicto de la tercera sub-hipótesis se mantiene sobre la referencia primaria dentro de la muestra.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (§8.3, `subsec:reduccion-intervencion`, y §8.4, `subsec:calibracion`); `docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex` (§10); `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I, `subsec:nota-versiones`); `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.46).

### P10. ¿Por qué el contraste de eficiencia usaba los 103 casos de consenso y, en la versión anterior, la exactitud primaria sobre los 206 casos (corpus retirado)?

El contraste de eficiencia se midió sobre los 103 casos de consenso porque era el subconjunto con referencia arbitrada del brazo de modelo solo, el canario de deriva conservado como insumo técnico. La exactitud primaria, en cambio, se informa ahora dentro de la muestra, sobre el corpus de 200 casos. La comparación con la exactitud fuera de muestra (206 casos) se retira con esa validación: el corpus fuera de muestra se retiró del ejemplar (Anexo I.1) y esa lectura no es vigente. Por eso la hipótesis subsidiaria de eficiencia queda sin contraste limpio y su conclusión se acota.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` (§8.2, `subsec:matriz-metricas`); `docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex` (§10); `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I, `subsec:nota-versiones`); `docs/Tesis/Correcciones/numeros-canonicos.md` (sección 3.45).

## Bloque 4. Autoría

### P11. ¿Qué partes del código de análisis y del texto de la tesis produjeron los asistentes de IA registrados en el repositorio, y cómo verificaron los autores cada cifra?

La declaración vigente (`subsec:declaracion-uso-ia`) detalla, por ámbito, qué produjo el asistente y cómo verificaron los autores cada cifra. En el código del sistema (backend, frontend y flujo N8N), el asistente implementó rutas, servicios, repositorios y componentes de interfaz, y el flujo N8N, a partir de tareas especificadas y revisadas por los autores. En los scripts de análisis y evaluación, produjo los scripts y el recálculo de las cifras que citan. En el texto de la tesis, produjo borradores de prosa (redacción, además de corrección de estilo y edición) a partir de tareas especificadas. Los diagramas se generaron con un modelo de lenguaje a partir de fuentes Mermaid versionadas. La verificación de los autores se apoyó en las suites de pruebas del backend y de `evaluation/`, en `verify_citations.py`, en `verificar_matriz_trazabilidad.py`, en el memo de números canónicos, en `resumir_registro_compilacion.py` y en la revisión de cada change antes de archivarlo; los autores confirman que ninguna parte se aceptó sin revisión previa. El detalle y los conteos del inventario constan en el anexo de trazabilidad.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo I, `subsec:declaracion-uso-ia`); `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` (secciones 5 y 6); `docs/Tesis/Correcciones/dictamen-correcciones.md` (entrada `c-237`).

### P12. ¿Cómo se distribuyó entre los tres autores el trabajo de esta última versión?

La distribución del trabajo de esta versión se declara por alias, en el mismo orden en que los roles aparecen en el apartado de gestión del proyecto. `T1` tuvo a su cargo la coordinación general, la integración de componentes y el canal telefónico (Twilio). `T2`, la implementación inicial del módulo Python, la base de datos, el frontend y el flujo N8N. `T3`, la revisión de la tesis, los anexos y la corroboración de fuentes. La dirección académica correspondió a los directores consignados en la portada. El mapeo entre cada alias y su identidad se conserva fuera del repositorio y no se publica.

Fuentes: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (§4.9, `subsec:gestion-scrumban`); `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` (sección 5.2, OQ3); `docs/Tesis/Correcciones/dictamen-correcciones.md` (entrada `c-239`).
