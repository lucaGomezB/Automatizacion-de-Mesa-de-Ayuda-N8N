# Tasks: Responder las aclaraciones de procedencia del dictamen sobre v1.6.2

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` = `docs/Tesis/Correcciones/`;
`D/` = `auditorias/Dictamen_Tesis_v10_v1.6.2_CONEAU_2026-11-20.md`. Lineas de `main` `fe9ad024`;
el apply las re-verifica con `rg` antes de editar. Equivalente de Strict TDD para prosa: cada
tarea de edicion corre una verificacion ANTES (debe mostrar el defecto) y DESPUES (estado
deseado), y ambas salidas se registran en `C/dictamen-correcciones.md` seccion `c-247`. Reglas:
no commitear, taggear ni pushear sin pedido; no cambiar cifras canonicas, citas ni conclusiones
sin ratificacion de autores; espanol neutro sin emojis; solo alias (`E1`, `E2`, `O1`, `O2`,
`A1`, `T1`), nunca nombres reales ni la correspondencia alias-identidad; no tocar `App/`, `n8n/`,
`evaluation/` ni los casos del corpus. Marcas: **[GATED OQ-0n]** = bloqueada hasta que la
respuesta de autores figure en la tabla de compuertas; sin marca = aplicable sin compuerta.
Dominio HIGH (`11-aspectos-legales.tex`, `docs/seguridad/`, `data/`): mostrar el texto propuesto
a los autores antes de escribir.

## 1. Guardas y lectura

- [ ] 1.1 Leer `proposal.md`, `design.md` (D1-D8, OQ-01 a OQ-04), los dos deltas de `specs/` y
  `D/` (veredicto 0 a 6, seguimiento, seccion 6, recomendaciones 0 a 15, Anexo B). Verificacion:
  `rg -n "presentado como (un )?escenario de referencia narrativo" S/` devuelve las lineas
  `01:16`, `01:72`, `01:76`, `04:46`, `08:22`, `08:50`, `09:51` (linea base).
- [ ] 1.2 Capturar la linea base de cifras canonicas y de conteos. Verificacion:
  `rg -c "61,6|17,76|71,2|73,5|W = 363|25,47|18,7|43,07|898" S/` y el conteo de palabras de
  prosa del Resumen (~207) y del Abstract (~197) quedan registrados en la seccion c-247.
- [ ] 1.3 Registrar `git rev-parse v1.6.2^{commit}` (`e7013127...`) y `sha256sum
  data/corpus_evaluacion_pseudonimizado.json` (`1fd17d7e...`) como valores que el apply MUST NOT
  cambiar salvo decision OQ-01 (D4) u OQ-04 (D8).

## 2. Compuertas de autores y director

- [ ] 2.1 **[COMPUERTA OQ-01]** Presentar a los autores las seis preguntas de OQ-01 de
  `design.md` (reportantes y titulares del regimen (a); lugares y periodo; originales con PII y
  base; composicion 119/81 segun D3 a/b; metadato del corpus segun D4 i/ii; retiro de `01:72`).
  Registrar la respuesta literal, fecha y responsable. Verificacion: la fila existe; sin ella,
  3.1 a 3.4 quedan bloqueadas y el agente no inventa.
- [ ] 2.2 **[COMPUERTA OQ-02]** Presentar las seis preguntas de OQ-02 (lugar y sistema de carga;
  que se escucho en los 81 telefonicos; experiencia real de `A1` y `T1`; definicion de
  `tiempo_manual_s`; planillas; corrida de septiembre). Verificacion: la fila existe; sin ella,
  3.5 a 3.8 quedan bloqueadas.
- [ ] 2.3 **[COMPUERTA OQ-03]** Presentar las seis preguntas de OQ-03 (1-10 y 2-10; redaccion y
  firma del acta T2; nota del acta T1; consentimiento de `A1`; hora de la corrida del 2-10;
  explicacion de `v1.6.0`). Verificacion: la fila existe; sin ella, 3.9 a 3.13 quedan bloqueadas.
- [ ] 2.4 **[COMPUERTA OQ-04]** Presentar a autores y director las opciones D8 (A), (B), (C) y
  el texto de la nota de erratum de `v1.6.2`. Verificacion: la fila existe con ambos
  responsables; sin ella, 8.1 queda bloqueada.

## 3. Bloque A - Aclaraciones de procedencia (gated)

- [ ] 3.1 **[GATED OQ-01]** `S/04-marco-metodologico.tex:46` (§4.4) y `S/11-aspectos-legales.tex:16`,
  `:40` (§7.2, §7.5): declarar quien reporto los 119 incidentes del regimen (a), tipo de lugares
  de trabajo y periodo, y quienes son los titulares; si fueron terceros, fundar el tratamiento de
  los originales con PII en la base que declaren los autores; si fueron los autores, explicar la
  tercera persona y el lexico de clientes y sucursales. Reemplazar aqui tambien la formula
  hibrida de `04:46` (D2, D5). Verificacion ANTES: `rg -n "cuyo entorno operativo origin.|entorno operativo del propio equipo" S/04-marco-metodologico.tex S/11-aspectos-legales.tex`
  muestra la formulacion ambigua; DESPUES: la oracion de reportantes y titulares coincide con
  OQ-01 y la formula no aparece.
- [ ] 3.2 **[GATED OQ-01]** `S/01-introduccion.tex:72` (§1.8): retirar o sostener "el corpus no
  proviene de una organizacion real" segun OQ-01 y separar el entorno real de recoleccion del
  escenario (D5). Verificacion ANTES: `rg -n "no proviene de una organizaci.n real|recolectado en un .nico entorno" S/01-introduccion.tex`
  devuelve `:72`; DESPUES: la oracion coincide con OQ-01 y no afirma una recoleccion en un
  escenario.
- [ ] 3.3 **[GATED OQ-01]** Regimen (b), origen frente a contenido: `S/04-marco-metodologico.tex:46`,
  `S/11-aspectos-legales.tex:16`, `:48` y las demas menciones "sin datos de terceros".
  Verificacion ANTES: `rg -n "sin datos de terceros" S/` lista las menciones; DESPUES: cada
  contexto distingue llamadas de terceros al puesto de trabajo de un autor de descripciones sin
  dato personal, y explica por que no requiere base de licitud.
- [ ] 3.4 **[GATED OQ-01]** Base de la composicion y metadato del corpus:
  `S/04-marco-metodologico.tex:46` declara la composicion como "declaracion de los autores sin
  registro de procedencia por caso" (D3 a) o retira el desglose (D3 b) y propaga a `04:129`,
  `S/12-anexos.tex:235`, `:239`; `data/README.md` y Anexo F (`S/12-anexos.tex:145`, `:147`)
  corrigen "200 casos reales" y "clasificacion manual"; el JSON solo se edita si OQ-01 eligio D4
  (ii), y entonces se abre un change propio para propagar el hash. Verificacion ANTES:
  `rg -n "200 casos reales" data/README.md data/corpus_evaluacion_pseudonimizado.json` y
  `rg -n "119|81 reconstrucciones" S/04-marco-metodologico.tex`; DESPUES: la base declarada
  figura, la descripcion vigente no dice "200 casos reales" y `sha256sum` del JSON sigue en
  `1fd17d7e...` salvo D4 (ii).
- [ ] 3.5 **[GATED OQ-02]** `S/04-marco-metodologico.tex` §4.2/§4.4 (`:16`, `:46`): declarar el
  lugar y el sistema en que `A1` y `T1` cargaron los 200 casos. Verificacion ANTES:
  `rg -n "carga completa" S/04-marco-metodologico.tex` muestra la carga sin lugar ni sistema;
  DESPUES: la oracion de lugar y sistema coincide con OQ-02.
- [ ] 3.6 **[GATED OQ-02]** `S/04-marco-metodologico.tex:66`, `:89`: declarar que escucharon o
  leyeron `A1` y `T1` en los 81 casos telefonicos de junio a agosto, y reformular la
  justificacion del recalculo del 19-10-2026 si no hubo escucha. Verificacion ANTES:
  `rg -n "escucha" S/04-marco-metodologico.tex` devuelve `:66` y `:89` sin explicacion
  cronologica; DESPUES: ambas coinciden con OQ-02.
- [ ] 3.7 **[GATED OQ-02]** Experiencia real de `A1` y `T1` y definicion unica del tiempo
  manual: `S/04-marco-metodologico.tex:58` ("experiencia en la mesa de ayuda"), `:64`
  ("familiarizados con el dominio de la mesa de ayuda del escenario de referencia"), `:16`,
  `:46`, `S/07-resultados.tex:284`, `S/08-discusion.tex:118`, `S/12-anexos.tex:147`.
  Verificacion ANTES: `rg -n "experiencia en la mesa de ayuda|mesa de ayuda del escenario|carga completa|clasificaci.n manual" S/`;
  DESPUES: la experiencia se describe sin apelar al escenario y todas las definiciones de
  `tiempo_manual_s` son la misma.
- [ ] 3.8 **[GATED OQ-02]** Planillas y ventana del flujo automatizado: `S/12-anexos.tex:145`
  (retirar "se incluyen ademas las planillas de cronometraje" o versionarlas en `data/` con
  aprobacion), `S/04-marco-metodologico.tex:14`, `:64`, `S/06-implementacion.tex:79` ("septiembre
  a octubre" pasa a "octubre" o se declara la corrida de septiembre y su ubicacion respecto de la
  notificacion). Verificacion ANTES: `rg -n "planillas de cronometraje|septiembre a octubre" S/`
  devuelve 4 lineas; DESPUES: coinciden con OQ-02.
- [ ] 3.9 **[GATED OQ-03]** `S/11-aspectos-legales.tex:30` y §7.5 (`:40`): una sola cronologia
  (1-10, 2-10, redaccion 17-11, firma 20-11) con el vocabulario de OQ-03, la oracion sobre la
  afirmacion de `v1.6.0` y la mencion del consentimiento escrito de `A1` (2026-11-20,
  `docs/campana-medicion/confirmacion-posterior-consentimiento.md`). Verificacion ANTES:
  `rg -n "notificaci.n|2026-11-20|A1" S/11-aspectos-legales.tex` sin `A1` ni explicacion;
  DESPUES: coincide con OQ-03 y nombra solo alias.
- [ ] 3.10 **[GATED OQ-03]** `S/11-aspectos-legales.tex:30` (§7.3): completar la lista de
  transferencias con la corrida de texto del 2-10-2026 (antes o despues de la notificacion), la
  de clasificacion del 7-10-2026, la campana complementaria del 5 y 6-11-2026 y las sondas pagas
  del 17 y 18-11-2026. Verificacion ANTES: `rg -n "son posteriores a la notificaci.n" S/11-aspectos-legales.tex`
  lista solo audio y corridas pagas; DESPUES: figuran las cuatro adiciones.
- [ ] 3.11 **[GATED OQ-03]** `S/11-aspectos-legales.tex:24` (y `:46` si aplica): reconciliar
  "el comprobante de facturacion ... no se versiona" con los dos CSV versionados que cita
  `S/07-resultados.tex:371`. Verificacion ANTES: `rg -n "no se versiona" S/11-aspectos-legales.tex`
  devuelve `:24`; DESPUES: el texto distingue lo versionado (CSV de consumo) de lo no versionado.
- [ ] 3.12 **[GATED OQ-03]** `docs/seguridad/acta-consentimiento-t2.md` (`:7-9`, `:73-74`,
  `:81-88`): consignar fecha de redaccion (2026-11-17) y de firma (2026-11-20), retirar "sin
  fecha de firma consignada aqui" y alinear el vocabulario. `docs/seguridad/acta-consentimiento-t1.md`:
  agregar nota de revision por la edicion del 2026-11-18 (`b01da04d`). Dominio HIGH: texto
  aprobado por los autores antes de escribir. Verificacion ANTES: `rg -n "sin fecha de firma" docs/seguridad/acta-consentimiento-t2.md`
  devuelve `:9`; DESPUES: 0 coincidencias y la nota de T1 existe.
- [ ] 3.13 **[GATED OQ-03]** `docs/defensa/respuestas-tribunal.md:129` (Q15) y respuesta 7 de
  `C/respuestas-tribunal-cuarta-instancia.md`: alinear con la cronologia y el vocabulario de
  OQ-03 y la lista de transferencias de 3.10. Verificacion ANTES: `rg -n "prestado el 2026-10-02" docs/defensa/respuestas-tribunal.md`
  devuelve `:129`; DESPUES: coincide con §7.3/§7.5.

## 4. Bloque B - Recomendaciones necesarias 1 a 6 (sin compuerta)

- [ ] 4.1 `S/00-resumen.tex:15` y `:31`: reencuadrar Resumen y Abstract (escenario narrativo y
  composicion en una oracion; balance como ahorro neto por incidente de unos 25,5 s-persona, cota
  superior, con +18,7 h como proyeccion sobre volumen supuesto; "viabilidad economica" acotada al
  costo marginal y al balance condicional); `:29` "inconclusive" alineado con "no concluyente,
  con estimacion puntual por encima de la cota". Reemplazar en lugar de agregar (D6). Si OQ-01
  retira el desglose, la oracion de composicion se ajusta en 3.4. Verificacion ANTES:
  `rg -n "viabilidad t.cnica y econ.mica|economic feasibility|inconclusive" S/00-resumen.tex`
  devuelve `:15`, `:29`, `:31`; DESPUES: las afirmaciones estan acotadas y cada bloque tiene
  <= 250 palabras de prosa.
- [ ] 4.2 Formula hibrida fuera de los pasajes gated (D5): `S/01-introduccion.tex:16`, `:62`
  ("la evidencia recogida en el entorno operativo de referencia"), `:76`, `S/08-discusion.tex:22`,
  `:50`, `S/09-conclusiones.tex:51`. Usar dos oraciones (recoleccion real en formulacion neutra
  que 3.1/3.2 completan; escenario de 120 usuarios como dimensionamiento). Verificacion ANTES:
  `rg -n "presentado como (un )?escenario de referencia narrativo|entorno operativo de referencia" S/`
  lista las lineas; DESPUES: 0 coincidencias (sumadas las de 3.1 y 3.2).
- [ ] 4.3 Mediciones frente a premisas: `S/01-introduccion.tex:18` ("sustancialmente inferior a
  la estimacion preliminar"), `S/07-resultados.tex:37` ("reemplaza a la estimacion preliminar de
  2 minutos con 45 segundos"), fila "Tiempos manuales" de `tab:procedencia-numeros`
  (`S/04-marco-metodologico.tex:78`) con "tarea de laboratorio". Verificacion ANTES:
  `rg -n "sustancialmente inferior|reemplaza a la estimaci|Campa.a 2026-10 \(jun" S/`;
  DESPUES: la comparacion se retira o rotula la premisa y la fila contiene "laboratorio".
- [ ] 4.4 Propagar R-02 (coautoria de los datos): limitaciones de §9.3 (`S/08-discusion.tex`,
  segunda limitacion o una propia), tabla de cumplimiento del objetivo 2 (`S/09-conclusiones.tex`,
  filas `:12-33`), aportes `:53`, §10, Anexo F (`S/12-anexos.tex:143-151`) y Nota de versiones
  (`:235-239`) con el desglose de c-246 (o su retiro si OQ-01 elige D3 b). Verificacion ANTES:
  `rg -n "reconstrucci" S/08-discusion.tex S/09-conclusiones.tex S/10-recomendaciones.tex` = 0;
  DESPUES: al menos una coincidencia en §9.3, conclusiones y Anexo F.
- [ ] 4.5 "corpus real" en `S/07-resultados.tex:99` y `S/09-conclusiones.tex:37`. Verificacion
  ANTES: `rg -n "corpus real" S/07-resultados.tex S/09-conclusiones.tex` devuelve 2; DESPUES: 0
  que describan los 200 casos.
- [ ] 4.6 Residuos de R-01: `S/01-introduccion.tex:48` ("a partir de la operacion habitual":
  declarar el origen de los 10 a 15 minutos y del 15 % como experiencia previa, bibliografia o
  supuesto de diseno, segun confirmen los autores en la tabla de compuertas como nota de OQ-01; y
  retirar "representativos"), `S/02-marco-teorico.tex:12` ("la observada en el entorno
  empresarial analizado"), `S/04-marco-metodologico.tex:50-54` ("universo relevado"), `:56`
  ("representativos del entorno operativo real"), `:125` ("los demas incidentes del periodo"),
  `S/08-discusion.tex:56` y `S/10-recomendaciones.tex:14` ("acumulado por la organizacion"),
  `S/08-discusion.tex:76` ("La experiencia de campo"), `S/09-conclusiones.tex:51` ("no se relevo
  el total de incidentes del periodo"), `S/10-recomendaciones.tex:34`. Verificacion ANTES:
  `rg -n "operaci.n habitual|entorno empresarial analizado|universo relevado|entorno operativo real|del per.odo|acumulado por la organizaci|experiencia de campo|propia organizaci" S/`;
  DESPUES: 0 coincidencias que presenten el escenario como operacion observada.
- [ ] 4.7 `N = 2.646` como supuesto: `S/08-discusion.tex:80` ("Sean N = 2.646"), `:109` (fuente de
  la tabla), `S/12-anexos.tex:321` (Anexo J). Lectura primaria por incidente en `S/08-discusion.tex:120`,
  `S/09-conclusiones.tex:6` y `:22` (D6). Verificacion ANTES: `rg -n "2\.646" S/08-discusion.tex S/12-anexos.tex S/09-conclusiones.tex`;
  DESPUES: cada ocurrencia rotulada; el valor no cambia.

## 5. Bloque C - Consistencia (recomendaciones 7 a 11 y 15, sin compuerta)

- [ ] 5.1 `S/07-resultados.tex:371`: reescribir la nota de facturacion (18-11 coincide con la
  ampliada, diferencia del 1,7 % cuantificada, del orden de seis llamadas; 17-11 incluye la
  corrida original, 80 llamadas, y consumos del mismo proyecto no registrados por llamada, 2.064
  frente a 764 tokens por llamada). Verificacion ANTES: `rg -n "coincide" S/07-resultados.tex`
  en `:371`; DESPUES: la nota no atribuye el 17-11 por entero a la corrida original.
- [ ] 5.2 `S/07-resultados.tex:6` ("siete apartados" con ocho subsecciones), `S/02-marco-teorico.tex:54`
  (TF-IDF huerfana: retirar o reescribir), `S/01-introduccion.tex:38` (hipotesis subsidiarias:
  enunciar y remitir). Verificacion ANTES: `rg -n "siete apartados|l.nea de base supervisada cl.sica|queda sin contraste limpio" S/01-introduccion.tex S/02-marco-teorico.tex S/07-resultados.tex`;
  DESPUES: cardinal correcto, oracion de TF-IDF coherente con su retiro, `:38` sin resultados.
- [ ] 5.3 `S/09-conclusiones.tex:47` ("Esa viabilidad se sostiene cuando se combina con un filtro
  deterministico": fundar o retirar) y `:49` (patron de diseno sin "sobre un corpus ... sobre un
  escenario"). Verificacion ANTES: `rg -n "se sostiene cuando se combina|reproducible sobre un corpus" S/09-conclusiones.tex`;
  DESPUES: 0 coincidencias.
- [ ] 5.4 Estado del arte: `S/03-estado-del-arte.tex:49` (ficha de Paket con cifras del texto
  completo, sin inventar; si no se dispone, declararlo), `:30` (Paramesh: dos trabajos distintos;
  completar la fila con arXiv 2103.15822: 10.742 tickets, 18 clases, 70:30, maximo 92,04 % con
  Bagging, verificando contra la fuente), `:34` (atribuir a Colavito). Verificacion ANTES:
  `rg -n "versi.n arbitrada|no reportado en el resumen" S/03-estado-del-arte.tex`; DESPUES: 0
  coincidencias; nueva entrada bib si se cita el preprint, con `verify_citations.py` en verde.
- [ ] 5.5 `S/08-discusion.tex:46`, `:64` ("Novena ... superada": retirar de la lista o pasar al
  protocolo de busqueda, ajustando el cardinal) y `S/04-marco-metodologico.tex:123` (0,864 como
  cota inferior de la eficiencia relativa asintotica). Verificacion ANTES: `rg -n "nueve limitaciones|Novena|0,864|0\{,\}864" S/08-discusion.tex S/04-marco-metodologico.tex`;
  DESPUES: cardinal coherente y 0,864 rotulado.
- [ ] 5.6 §11.7 `S/10-recomendaciones.tex:14`, `:34`: sin "la organizacion", con la condicion de
  reapertura fijada al detener c-229 (marco poblacional solo si el equipo opera el prototipo como
  su propia mesa durante un periodo declarado y exporta la tabla completa) y la medicion del costo
  de reasignacion en el primer nivel. Verificacion ANTES: `rg -n "organizaci.n|c-229|reasignaci" S/10-recomendaciones.tex`;
  DESPUES: sin organizacion inexistente; condicion y prioridad presentes.
- [ ] 5.7 §8.8 (`S/04-marco-metodologico.tex:91`, `S/07-resultados.tex:347`, `:371-376`): declarar
  que el criterio de degradacion por inferencia (T = 4) se fijo para la sonda, que los
  prerregistros se versionaron junto con la evidencia, y presentar las dos corridas completas (o
  las dieciseis filas). Sin cambiar valores. Verificacion ANTES: `rg -n "T = 4|PRERREGISTRO" S/`;
  DESPUES: el origen del criterio y ambas corridas completas figuran.
- [ ] 5.8 `C/respuestas-tribunal-cuarta-instancia.md`: respuesta 1 con el "por que" del registro
  (`C/dictamen-correcciones.md`, "Por que se presento asi"); 3 sin atribuir las etiquetas a un
  solo autor y sin comparar 0,7405 con 0,5270; 4 sin "no habia una mesa en operacion"; 5 con la
  firma de `A1` (2026-11-20); 9 con "Tabla 26" y "1235"; aviso de que la Tabla 25 citada por el
  tribunal es ahora la 26. La respuesta 7 se completa en 3.13. Verificacion ANTES:
  `rg -n "dispositivo narrativo|mismo autor|no hab.a una mesa|firma solicitada|Tabla 25|1221" C/respuestas-tribunal-cuarta-instancia.md`;
  DESPUES: solo queda el aviso de renumeracion.

## 6. Bloque D - Forma (recomendaciones 12 a 14, sin compuerta)

- [ ] 6.1 `S/00-portada.tex:30` (fecha de la release que compile el change de release; dejar
  marcador para ese change si la fecha no se conoce), `S/01-introduccion.tex:80` (§1.9 con el
  Anexo K). Verificacion ANTES: `rg -n "14 de noviembre de 2026" S/00-portada.tex` y
  `rg -n "anexo-sensibilidad" S/01-introduccion.tex`; DESPUES: fecha actualizada o instruccion
  registrada; §1.9 nombra el Anexo K.
- [ ] 6.2 Remisiones al memo interno: `S/07-resultados.tex:32`, `:310`, `S/08-discusion.tex:112`
  (retirar o llevar al Anexo J lo prometido). Verificacion ANTES: `rg -n "numeros-canonicos|memo" S/07-resultados.tex S/08-discusion.tex`;
  DESPUES: sin remisiones al memo en el cuerpo.
- [ ] 6.3 `S/07-resultados.tex:8` (fragmento sin verbo) y `:343` (dos oraciones consecutivas
  "Estas cifras"). Verificacion ANTES: `rg -n "Los de correo y formulario, medidas|Estas cifras" S/07-resultados.tex`;
  DESPUES: oracion completa y sin repeticion.
- [ ] 6.4 Regla de las 60 palabras: `S/04-marco-metodologico.tex:46` (73), `:91` (77),
  `S/07-resultados.tex:374` (81), `:376` (68), `S/09-conclusiones.tex:6` (71). Coordinar con 3.1 y
  4.7 que tocan las mismas lineas. Verificacion ANTES/DESPUES: script de conteo por oracion sobre
  esos parrafos; DESPUES ninguna oracion supera 60 palabras.
- [ ] 6.5 Tablas sin cita: agregar `\ref` a `tab:balance-neto` (`S/08-discusion.tex:87`),
  `tab:declaracion-uso-ia` (`S/12-anexos.tex:255`), `tab:anexo-nc-costo` (`:286`),
  `tab:anexo-nc-balance` (`:309`). Verificacion ANTES: `rg -n "ref\{tab:(balance-neto|declaracion-uso-ia|anexo-nc-costo|anexo-nc-balance)\}" S/` = 0;
  DESPUES: >= 1 por etiqueta.
- [ ] 6.6 Linea de fuente en `fig:despliegue`, `fig:er_modelo_datos`, `fig:panel_admin`,
  `fig:dashboard`, `fig:boxplot_tiempos`, `fig:secuencia`, `fig:secuencia_b`, `fig:componentes_b`,
  las tres del flujo N8N y las dos tablas del Anexo J; flotantes de los Anexos A y J dentro de su
  anexo (`\FloatBarrier` o `[H]`). Verificacion: script que lista cada `\label{fig:...}` sin
  "Fuente" en su entorno; DESPUES lista vacia. La ubicacion en el PDF se verifica en el change de
  release.
- [ ] 6.7 Glosario (`S/00-glosario.tex`: IR, RPO, VoIP, TwiML, OAuth2, IEC) y "Recharts" en
  `S/06-implementacion.tex:97`. Verificacion ANTES: `rg -n "ReCharts" S/` devuelve `06:97`;
  DESPUES: 0 y las seis entradas presentes.
- [ ] 6.8 `Bibliography_base.bib`: volumen y paginas de Mayor-Rocher, Ramon Ferrer, Xiong y Chen
  (verificados en Crossref); editorial de Ramon Ferrer (SAGE); fecha de la Decision 2003/490/CE y
  fuente de la revalidacion 2024 o su retiro. Verificacion: `verify_citations.py` pasa y las
  cuatro entradas tienen `volume` y `pages`.

## 7. Coherencia

- [ ] 7.1 Cifras canonicas intactas: repetir el conteo de 1.2. Verificacion: mismos valores; el
  diff solo re-rotula.
- [ ] 7.2 Sin nombres reales ni correspondencia alias-identidad en la prosa nueva. Verificacion:
  `git diff` de `S/`, `docs/seguridad/`, `C/` revisado; solo alias en las oraciones agregadas.
- [ ] 7.3 Residuos globales. Verificacion: `rg -ni "presentado como (un )?escenario de referencia narrativo|operaci.n habitual|universo relevado|corpus real|experiencia de campo|sin fecha de firma|planillas de cronometraje" S/ docs/seguridad/`
  = 0 (salvo las que OQ-02 conserve con planillas versionadas).
- [ ] 7.4 Hash del corpus y tag intactos (salvo D4 ii / D8 C). Verificacion: `sha256sum` y
  `git rev-parse v1.6.2^{commit}` iguales a 1.3.

## 8. Release (instruccion, no ejecucion) y registro

- [ ] 8.1 **[GATED OQ-04]** Registrar en `C/dictamen-correcciones.md` seccion c-247 la instruccion
  para el change de release: opcion D8 elegida, nota de erratum de `v1.6.2` (PDF del arbol del
  tag imprime `17aa6d21`), `compilacion.md` con el commit compilado, fecha de portada (6.1) y
  verificacion de flotantes (6.6). Verificacion: la instruccion figura; ningun tag ni PDF cambio.
- [ ] 8.2 `C/dictamen-correcciones.md`: agregar la seccion c-247 con la tabla de compuertas OQ-01
  a OQ-04 (pregunta, respuesta literal, fecha, responsable), la tabla ANTES/DESPUES de 3.x a 6.x,
  el resultado de 7.x y la nota de dependencia (c-246 archivado; c-242 D5 y c-246 OQ-01 citados
  para la decision D3). Verificacion: la seccion existe; `git diff` del archivo es aditivo.
- [ ] 8.3 `openspec validate c-247-responder-las-aclaraciones-de-procedencia-del-dictamen-v1-6-2 --strict`
  y `openspec validate --all --strict`. Verificacion: pasan.
- [ ] 8.4 Confirmar alcance: `git status` sin cambios en `App/`, `n8n/`, `evaluation/` ni en los
  casos del corpus.
