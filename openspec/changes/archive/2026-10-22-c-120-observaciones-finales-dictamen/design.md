## Context

Ver `proposal.md` - Why. La tesis v9 de `docs/Tesis/v9 (IA)/paper/` compila a un PDF de 101 paginas y el dictamen CONEAU 2026-10-21 la aprueba dejando 7 observaciones de forma y completitud. Esta fase es de solo planificacion: NO se edita ningun `.tex` ni el `.bib`.

Evidencia verificada sobre el codigo fuente (no sobre el PDF):

- La subseccion homonima de la sub-hipotesis de intervencion humana vive en `sections/07-resultados.tex:134` (`\subsection{Reducción de la intervención humana}`), NO en `08-discusion.tex`. El texto ya declara "no medido" en `01-introduccion.tex:34`, `00-resumen.tex:13` y `09-conclusiones.tex:6,41`, pero no usa la formula "no contrastada por ausencia de registro primario".
- Las afirmaciones comerciales sobre plataformas estan en `03-estado-del-arte.tex:12,14,22,79` y `01-introduccion.tex:68`; los precios (DigitalOcean, Vertex AI) estan en `08-discusion.tex:58` (notas al pie con URL). NO aparecen en `10-recomendaciones.tex` ni en `11-aspectos-legales.tex`, a diferencia de lo supuesto en el pedido.
- El kappa no tiene tabla primaria recuperable: `docs/Tesis/Correcciones/numeros-canonicos.md` seccion 3.6 declara que `data/Corpus Tesis - Hoja 1.csv` y su version pseudonimizada no tienen columnas de doble etiquetado por analista, y `evaluation/` solo conserva el valor agregado. La tesis ya declara la no computabilidad en `04-marco-metodologico.tex:55`.
- El umbral de 5.000 casos aparece tres veces y ya esta rotulado como indicativo: `10-recomendaciones.tex:12`, `08-discusion.tex:56` y `12-anexos.tex:139`.
- El eje de ASR ocupa `02-marco-teorico.tex:56-62` (tres parrafos). Las citas `Rabiner1993_speech_recognition` y `Radford2023_whisper` se usan UNICAMENTE alli.
- El capitulo legal tiene dos `\section` de nivel superior (`11-aspectos-legales.tex:4` y `:36`); la clase es `article`, de modo que cada `\section` consume un numero de capitulo y desplaza la numeracion de los capitulos siguientes en uno.
- La justificacion del umbral del 85~\% con los tres criterios esta en `01-introduccion.tex:48`; el segundo criterio se apoya en "las mediciones preliminares de la organización" sin fuente. NO esta en `04-marco-metodologico.tex`.

Restricciones duras: no alterar contenido cientifico, numeros canonicos, las cinco cadenas de categoria ni c-102..c-119; no tocar codigo de aplicacion, `evaluation/`, `CHANGES.md`; sin emojis; presupuesto de paginas HARD: la tesis MUST permanecer en <= 101 paginas; el tag `v1.0.0` NO se mueve.

## Goals / Non-Goals

**Goals:**

- Cerrar las 7 observaciones del dictamen con cambios documentales, preservando numeros canonicos y el presupuesto de paginas.
- Dejar una verificacion reproducible por defecto (comando + valor esperado) para cada observacion.
- Mantener la correspondencia citas-bibliografia (cero citas huerfanas, cero entradas sin usar).

**Non-Goals:**

- No modificar codigo de aplicacion, `evaluation/` ni numeros canonicos.
- No fabricar un intervalo de confianza del kappa ni una medicion organizacional inexistente.
- No publicar un tag nuevo ni mover `v1.0.0`.
- No reescribir contenido cientifico mas alla de lo que exige cada observacion.

## Decisions

### D1. Rotulo de la sub-hipotesis de intervencion humana (obs 1)

Decision: adoptar la formula exacta del dictamen "no contrastada por ausencia de registro primario" en las cuatro ubicaciones en español (`00-resumen.tex:13`, `01-introduccion.tex:34`, `09-conclusiones.tex:6,41`) y retitular la subseccion `07-resultados.tex:134`.

Titulo nuevo propuesto: `\subsection{Intervención humana en el flujo automatizado}\label{subsec:reduccion-intervencion}` (se conserva el label para no romper las `\autoref` existentes). El titulo actual "Reducción de la intervención humana" promete un resultado no entregado.

El abstract en ingles (`00-resumen.tex:29`) hoy dice "declared not measured for per-case human intervention"; se alinea a "not tested due to the absence of a primary record" para consistencia bilingue.

Alternativa considerada: solo retitular la subseccion sin tocar el cuerpo. Se descarta: el dictamen pide el rotulo explicito en la sub-hipotesis, no solo el titulo.

Verificacion: `grep -c "no contrastada por ausencia de registro primario"` >= 4 en `sections/`; `grep -c "Reducción de la intervención humana"` == 0; el indice muestra el titulo nuevo.

Reconciliacion (post-verificacion, 2026-10-22): el spec REQ-01 exige la formula en CUATRO secciones (resumen, introduccion, resultados y conclusiones). Esta decision la habia enumerado solo en tres ubicaciones y parafraseaba en `07-resultados.tex:138`; una verificacion adversarial independiente detecto la discrepancia. Se corrigio `07-resultados.tex` (§8.3) para que incluya la formula exacta, de modo que el PDF la exhibe en las cuatro secciones. El presupuesto de paginas se mantiene en 101 (substitucion a nivel de palabras, sin crecimiento).

### D2. Afirmaciones comerciales y precios (obs 2)

Dos sub-decisiones, porque la naturaleza de la afirmacion difiere.

**D2a - Capacidades de plataformas (`03-estado-del-arte.tex:12,14,22,79`, `01-introduccion.tex:68`).** Las descripciones de capacidades de producto no son academicamente citables con una fuente arbitrada. Decision: reformularlas como observacion propia declarada del relevamiento ("el relevamiento propio de la documentacion publica de los proveedores, consultada el 19-10-2026, muestra que..."), manteniendo las URLs de la nota de la tabla como punteros de fuente, sin inventar referencias academicas. Alternativa considerada: agregar entradas `@online` de las paginas de producto. Se descarta porque una pagina de marketing de proveedor sigue sin ser una referencia academica y no satisface el fondo de la observacion.

**D2b - Precios (`08-discusion.tex:58`).** El precio de lista es un dato factual fechado que se beneficia de una cita formal. Decision: agregar dos entradas `@online` a `Bibliography_base.bib` (`DigitalOcean2026_pricing`, `Google2026_vertex_pricing`) con `url`, `urldate = {2026-10-19}` y `note` de fecha de consulta, y citarlas en el cuerpo en lugar de dejar la URL solo en la nota. El calculo de la nota al pie se conserva.

Trade-off: D2a es neutral en paginas; D2b agrega 2 entradas al `.bib` (crecimiento marginal, compensado por el recorte de D5). El resultado neto MUST ser <= 0 paginas.

Verificacion: `grep -n "digitalocean.com\|cloud.google.com/vertex-ai" sections/*.tex` muestra la cita `\parencite` ademas de (o en lugar de) la URL cruda; `verify_citations.py` sigue reportando cero huerfanas y cero sin usar; compilar y confirmar <= 101 paginas.

### D3. Intervalo de confianza del kappa (obs 3)

Investigacion: la tabla primaria de doble etiquetado NO es recuperable. `numeros-canonicos.md` seccion 3.6 lo declara explicitamente y las fuentes de datos (`data/*.csv`, `data/corpus_evaluacion_pseudonimizado.json`) no contienen columnas por analista; `evaluation/` solo conserva el valor agregado.

Decision: mantener la declaracion de no computabilidad. La tesis ya la contiene en `04-marco-metodologico.tex:55`; la tarea es de verificacion y consistencia, sin fabricar un intervalo. No se edita ningun `.tex` salvo que la verificacion detecte que la declaracion falta o es ambigua en alguna de las ubicaciones del kappa (`04-marco-metodologico.tex:55,87` y `00-resumen.tex:11`). Si el autor aporta la tabla primaria, el requisito del spec preve el calculo por bootstrap con semilla fija (reversible).

Alternativa considerada: estimar el IC a partir de supuestos. Se descarta de plano: fabricar el intervalo viola la integridad metodologica que el propio dictamen elogia.

Verificacion: `grep -n "intervalo de confianza del kappa" 04-marco-metodologico.tex` encuentra la declaracion de no computabilidad; no aparece ningun IC numerico del kappa.

### D4. Umbral de 5.000 casos (obs 4)

Hallazgo: las tres ocurrencias ya lo rotulan como indicativo (`10-recomendaciones.tex:12`, `08-discusion.tex:56`, `12-anexos.tex:139`). Decision: elevar la formulacion a "referencia indicativa de orden de magnitud, no derivada del corpus actual ni de un calculo de potencia estadistica", de forma uniforme en las tres ubicaciones. Es un ajuste de redaccion, no un cambio de valor.

Alternativa considerada: justificar el umbral con un calculo de tamano de muestra. Se descarta: no hay parametros (numero de clases efectivo, presupuesto de etiquetado) que permitan un calculo honesto; el dictamen admite explicitamente la degradacion a orden de magnitud.

Verificacion: `grep -c "orden de magnitud" sections/*.tex` cubre las tres ocurrencias; `grep -c "5\.000"` == 3 (no se agrega ninguna ocurrencia nueva).

### D5. Recorte del eje de ASR (obs 5)

Decision: comprimir `02-marco-teorico.tex:56-62` (tres parrafos) a un unico parrafo de dos o tres oraciones que conserven: (i) la nocion conceptual de ASR, (ii) el exponente del estado del arte con su cita, y (iii) la declaracion explicita de que el sistema delega la transcripcion en un servicio externo y no integra un motor de ASR.

Restriccion critica: `Rabiner1993_speech_recognition` y `Radford2023_whisper` se citan SOLO en este pasaje. Si el recorte elimina una de las dos citas, esa entrada queda sin usar y se rompe el requisito "cero entradas sin usar" de `tesis-document`. Por lo tanto el parrafo comprimido MUST conservar AMBAS citas (o, alternativamente, retirar tambien las entradas del `.bib`, lo que amplia innecesariamente el alcance). Se conservan ambas.

Se eliminan del cuerpo los detalles de menor valor conceptual (las 680.000 horas de entrenamiento de Whisper y el recuento historico de los HMM) sin tocar la conclusion.

Alternativa considerada: eliminar la subseccion entera y mover la nocion al marco de telefonia. Se descarta: perderia las dos citas y obligaria a tocar el `.bib` y la numeracion de subsecciones.

Verificacion: la subseccion `subsec:reconocimiento-habla` pasa de tres parrafos a uno; `grep -c "Rabiner1993\|Radford2023" 02-marco-teorico.tex` == 2; el numero de paginas del cuerpo no aumenta.

### D6. Numeracion del capitulo legal (obs 6)

Decision: restructurar `11-aspectos-legales.tex` a una unica `\section` de nivel superior. El capitulo conserva `\section{Consideraciones éticas y aspectos legales}` (linea 4); la segunda `\section{Cumplimiento normativo y alineación con estándares}` (linea 36) se degrada a `\subsection{Cumplimiento normativo y alineación con estándares}` con label propio (nuevo `subsec:cumplimiento`), y sus cinco `\subsection` (lineas 38, 42, 66, 92, 96) se degradan a `\subsubsection` conservando sus labels. Asi el capitulo legal consume UN solo numero y la numeracion de Resultados, Discusion, Conclusiones y Recomendaciones vuelve a 8, 9, 10 y 11.

Se actualizan ademas los comentarios internos de numeracion: `11-aspectos-legales.tex:2` (hoy "Capítulo 7" pese a estar en la posicion 7 tras la reubicacion, correcto en posicion pero el comentario debe declarar la posicion real y no confundirse con el numero de archivo) y los comentarios de `main.tex:57-70`, que hoy asignan a Resultados el numero 8 cuando tras la correccion pasa a ser el 8 (coincide) pero hoy el PDF lo numera 9; los comentarios MUST declarar la posicion real del documento compilado.

Alternativa considerada: dejar el detalle cosmetico (el dictamen lo declara opcional). Se descarta porque el pedido incluye "revisar los comentarios internos de numeracion", que sin la restructura quedarian declarando numeros falsos, y porque la numeracion limpia es un criterio de calidad explicito.

Trade-off: la degradacion introduce un tercer nivel de anidamiento en el indice para el bloque de cumplimiento. Riesgo de desplazamiento de paginas: bajo (mismo contenido, un nivel mas de encabezado). Se verifica con el conteo final.

Verificacion: `grep -c "^\\\\section{" 11-aspectos-legales.tex` == 1; el PDF numera Resultados como 8 y Conclusiones como 10; compilar y confirmar <= 101 paginas.

### D7. Fuente del criterio del umbral del 85~\% (obs 7)

Hallazgo: el pasaje esta en `01-introduccion.tex:48`, no en `04-marco-metodologico.tex`. El segundo de los tres criterios dice "el costo organizacional de una derivación erronea implica al menos 10 a 15 minutos adicionales de reasignación según las mediciones preliminares de la organización". Los otros dos criterios ya tienen respaldo (Paramesh2019 tiene cita; el tercero es un argumento logico de margen del IC).

Decision: reformular el segundo criterio como estimacion propia declarada, sin presentarlo como medicion de respaldo: "el costo organizacional de una derivación erronea se estima en el orden de 10 a 15 minutos adicionales de reasignacion, estimacion propia de los autores a partir de la observacion operativa de la organización adoptante, sin un registro cuantitativo conservado". Se elimina la apelacion a "mediciones preliminares" no citadas.

Alternativa considerada: citar una fuente externa sobre el costo de reasignacion de tickets. Se descarta: introducir una referencia que no respalda el valor especifico de la organizacion seria peor que declarar la estimacion propia.

Verificacion: `grep -c "mediciones preliminares de la organización" 01-introduccion.tex` == 0; el pasaje declara la estimacion como propia; no se introduce ningun numero nuevo.

## Risks / Trade-offs

- Presupuesto de paginas (HARD): D2b suma entradas al `.bib` y D6 cambia el anidamiento; D5 recorta. Mitigacion: compilar y confirmar <= 101 paginas; si D2b empuja por encima, se aplica el fallback de reformular tambien los precios como observacion propia (sin entradas nuevas) antes de tocar otra seccion.
- D5 y la correspondencia citas-bibliografia: recortar el eje de ASR podria dejar `Rabiner1993` o `Radford2023` sin usar. Mitigacion: conservar ambas citas en el parrafo comprimido; verificar con `verify_citations.py`.
- D6 y las `\autoref` internas: degradar secciones cambia `\thesection`, no los labels; las referencias por label se preservan. Mitigacion: conservar todos los labels; verificar cero referencias indefinidas en el `.log`.
- D1 y el indice de la subseccion: el retitulo cambia la entrada del indice. Mitigacion: verificar que la entrada refleja el titulo nuevo y que ninguna `\autoref{subsec:reduccion-intervencion}` se rompe (se conserva el label).
- D3 sin edicion: si la verificacion confirma que la declaracion ya existe, la tarea cierra como verificacion documentada; no se inventa trabajo.

## Migration Plan

1. Aplicar los cambios en la fase apply, solo `.tex` y `Bibliography_base.bib`, en el orden D1, D2, D4, D5, D7, D6, D3 (D3 ultima por ser de verificacion).
2. Compilar:
   `docker run --rm -v "/home/skywalker/Desktop/notas/Tesis/Automatizacion-de-Mesa-de-Ayuda-N8N/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`
3. Ejecutar las verificaciones D1-D7 y la de presupuesto de paginas; confirmar <= 101 paginas y cero referencias indefinidas.
4. Rollback: `git checkout -- "docs/Tesis/v9 (IA)/paper" "docs/Tesis/v9 (IA)/Bibliography_base.bib"` restaura el estado previo. No se mueve ningun tag; `v1.0.0` permanece intacto.

## Open Questions

Ninguna. Las dos que podrian parecerlo ya estan cerradas y se registran aqui para trazabilidad.

**D3 RESUELTA — decision canonica, no pregunta abierta.** La recuperabilidad de la tabla primaria de doble etiquetado NO depende del autor hoy: ya fue decidida en `docs/Tesis/Correcciones/numeros-canonicos.md` seccion 3.6 (agregada por `c-108`, 2026-10-21) y confirmada por el autor. La tabla NO existe en las fuentes permitidas (`data/Corpus Tesis - Hoja 1.csv` y su version pseudonimizada no tienen columnas por analista; `evaluation/` solo conserva el valor agregado), y el IC del kappa se declara NO estimable, sin fabricarlo. La unica condicion de cambio es que el autor cargue explicitamente la tabla primaria (ruta reversible prevista por el spec `tesis-numeros-canonicos`), condicion que hoy no se cumple. Por lo tanto la tarea de D3 es de VERIFICACION de la declaracion existente (`04-marco-metodologico.tex:55`), no de decision ni de consulta al autor.

**D6 RESUELTA** — se restructura `11-aspectos-legales.tex` a una unica `\section` de nivel superior (ver D6). No requiere input del autor.
