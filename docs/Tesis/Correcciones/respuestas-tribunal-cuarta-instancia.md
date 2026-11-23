# Respuestas probables del tribunal — Devolución de cuarta instancia (2026-11-19)

Preparación para la defensa. Las respuestas se redactaron a partir de la tesis (`docs/Tesis/v10 (IA)`)
y de las decisiones de los autores registradas en el change `c-246-aplicar-el-reencuadre-autorizado-de-cuarta-instancia`
y en `docs/Tesis/Correcciones/dictamen-correcciones.md`. Estado: borrador para revisión de los autores y del director.

## 1. ¿Por qué presentaron el escenario como una organización real hasta la v1.6.0 y qué cambió en la lectura de los resultados al declararlo ficticio?

Los autores declararon, en el registro de correcciones ("Por qué se presentó así"), que presentaron la
organización como real porque en su momento pensaban que los datos así presentados tendrían más valor y que la
tesis parecería más seria; en retrospectiva, lo que importaba eran las descripciones de los incidentes. La
decisión de reencuadrar eso no se aplicó hasta después de la v1.6.0 (tag del 17/11/2026). El reencuadre
(change c-242, 18/11/2026) declaró el escenario como ficticio y lo corrigió. Al declararlo ficticio cambia la
naturaleza de la lectura: las cifras de contexto (42 incidentes/día, 2.646 incidentes por trimestre, ~120
usuarios, "2 min 45 s") pasan de ser mediciones a ser parámetros o supuestos del escenario. No cambian el
sistema, el código, las latencias del flujo automatizado ni las mediciones dentro del corpus conservado (los
200 casos y la campaña complementaria), que siguen siendo reales. Lo que se acota es la pretensión de
generalización: la evidencia es de laboratorio sobre un corpus curado, no de operación real de una organización.

## 2. ¿Cuántos de los 200 casos son reconstrucciones y cómo se escribieron?

81 de los 200 casos son reconstrucciones (régimen (b)). Lo que se reconstruye es la descripción, no el
incidente: el autor que recolectó los incidentes redactó, sin asistente de inteligencia artificial, una
descripción general, sin detalles explícitos y pseudonimizada, de cada llamada telefónica real que recibió en
su trabajo. Los otros 119 son incidentes reales del entorno operativo del propio equipo (régimen (a)), de
correo electrónico (66) y formulario web (53), pseudonimizados.

## 3. Si los autores escribieron parte de los casos y ajustaron las reglas sobre ese mismo corpus, ¿qué parte del 73,5 % de exactitud puede atribuirse al clasificador y no a la forma en que se redactaron los casos?

El clasificador es híbrido: 131 de los 200 casos los resuelve un filtro determinístico (patrones léxicos,
cortocircuito en el punto de operación 0,5166) y los otros 69 los atiende Gemini. El 73,5 % global (147/200,
exactitud estricta) es una cifra dentro de la muestra. El vocabulario del filtro se amplió de 89 a 151 patrones
tomando léxico del propio corpus de evaluación, y las reglas de frontera del prompt se derivaron de errores
observados en esos mismos 200 casos, sin partición de validación. La tesis acota ese efecto con una lectura de sensibilidad al vocabulario, que se presenta como cota pesimista y
no como medición. Sin embargo, la tesis no aísla cuánto del 73,5 % se debe a la redacción de los casos frente al
clasificador: las 81 descripciones reconstruidas y el criterio del clasificador provienen de un autor, y las
etiquetas de referencia las fijaron dos analistas, uno externo al equipo, sobre el mismo corpus congelado. Por eso el 73,5 % se reporta como
estimación dentro de la muestra, probablemente optimista, y la magnitud del sesgo de coautoría se declara no
estimada (séptima amenaza, §4.8).

## 4. ¿Dónde y cómo se cronometró el flujo manual de 61,6 s, y en qué se diferencia esa tarea del registro real en una mesa de ayuda?

Fue una medición controlada, una tarea de laboratorio, no la observación de una mesa real en operación. Dos
operadores (A1, externo al equipo, y T1, autor) procesaron los 200 casos en pares y se cronometraron mutuamente
el tiempo total de carga, entre junio y agosto de 2026 (media 61,6 s, mediana 50,0 s, desvío 44,9 s, rango
10–300 s; §4.2 en `04-marco-metodologico.tex` y §8 Resultados en `07-resultados.tex`). Se diferencia del
registro real en una mesa de ayuda en que la tarea fue una medición controlada sobre un corpus curado de 200
casos (no un flujo entrante real) y en que los operadores sabían que se cronometraba (efecto Hawthorne,
declarado). El 61,6 s se lee, entonces, como medición de tarea controlada.

## 5. ¿Quién es A1 y qué información recibió sobre el uso de sus registros?

A1 es el analista externo al equipo de autores que (a) operó el brazo manual de la campaña 2026-10 y (b) fue
uno de los dos analistas originales que fijaron la referencia (ground truth) de los 200 casos (el otro es T1,
autor). A1 fue notificado de antemano de su participación como colaborador y sabía que la campaña registraba
tiempos, aunque se le ocultó el propósito comparativo; la sesión de esclarecimiento (debriefing) se hizo con A1.
Su consentimiento se tramita como el de los otros colaboradores (E1–E5, O1, O2); su confirmación escrita de
información y consentimiento se firmó el 2026-11-20 y se conserva en el expediente del trabajo.

## 6. Con un volumen de incidentes supuesto, ¿qué dato tendría que medir una organización real antes de decidir si adopta el sistema?

Sobre su propio entorno debería medir: (1) su volumen real de incidentes por período (N), porque el balance neto
es lineal en N y el 2.646/trimestre del estudio es un supuesto; (2) el tiempo real de registro manual incidente
por incidente de su mesa (aquí 61,6 s fue tarea controlada); (3) su tasa de derivación errónea y su costo por
error (c); y (4) su distribución por sector y canal. Con esos datos puede re-ejecutar el balance neto
(ahorro = f(N, tiempos, c)) para su caso. El estudio aporta la forma del cálculo, no los valores de esa
organización.

## 7. ¿Con qué base usaron los incidentes reales que forman parte del corpus?

Los 119 incidentes reales del régimen (a) no provienen de una tercera organización ni de terceros ajenos: son
incidentes del entorno operativo del propio equipo. La base de licitud es el consentimiento informado del grupo
(art. 5 inc. 1 de la Ley 25.326), con pseudonimización como refuerzo; notificación el 2026-10-01,
consentimiento verbal el 2026-10-02, y acta redactada el 2026-11-17 y firmada el 2026-11-20. No se
usó la base de empleador (art. 5 inc. 2 ap. d), que era la afirmación incorrecta de
versiones anteriores. Las 81 reconstrucciones (régimen (b)) no contienen datos personales y no requieren base.

## 8. En el bloque dentro de la muestra, ¿qué aporta la etapa de reglas frente a un esquema de modelo de lenguaje solo, además del ahorro de llamadas?

Además de resolver el 65,5 % (131/200) sin invocar al modelo, la etapa determinística aporta: determinismo y
reproducibilidad (mismo caso, misma predicción, sin estocasticidad), transparencia y auditabilidad (patrones
léxicos inspeccionables) y un puntaje de correctitud que gobierna el cortocircuito. Con honestidad se declara
que la hipótesis de mayor eficiencia frente a un esquema solo de modelo queda sin contraste limpio: dentro de la
muestra las reglas aciertan 97/131 (0,7405) frente a 88/130 (0,6769) de Gemini con el cortocircuito
deshabilitado (McNemar, p = 0,1516, no significativo), y el bloque prerregistrado fuera de muestra se retiró
con la validación retirada.

## 9. ¿Qué partes del texto y del análisis produjo un asistente de IA y cómo verificaron cada cifra?

El desarrollo del sistema, los scripts de análisis y evaluación y la redacción se hicieron con asistencia
sistemática de agentes de código. La declaración de uso (Anexo I.3, Tabla 26) y el inventario versionado
(`docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md`) desglosan por ámbito las herramientas y modelos, qué
produjo el asistente y cómo verificaron los autores; 162 de 1235 commits llevan marca de coautoría (cota
inferior). Cada cambio se organizó con especificación previa (propuesta, diseño y tareas) definida y revisada
por los autores; el agente implementaba y los autores aceptaban o rechazaban el resultado. Las cifras canónicas
y el reencuadre se verificaron por contraste ANTES/DESPUES y quedaron en el Anexo I (trazabilidad de las
correcciones).

Aviso de renumeración: la Tabla 25 que el tribunal cita (declaración de uso de IA) es, en esta versión, la Tabla 26.
