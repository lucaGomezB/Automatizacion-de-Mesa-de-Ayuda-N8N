# Proposal: Atender las observaciones de la sexta instancia del tribunal

## Why

El dictamen de sexta instancia sobre `v1.6.5` (`auditorias/Devolución de sexta instancia — TFI
«Automatización inteligente del registro de.pdf`, 2026-11-26) dicta **APTA PARA DEFENSA**, 7,5/10
(quinta instancia: 7,3), y alcanza la calificación proyectada: resuelve C-03, C-04, C-05 y casi todo
C-07. Es la sexta devolución escrita del tribunal y el cierre formal de la ronda de correcciones antes
de fijar fecha de defensa. Las correcciones C-01, C-02 y C-06 quedaron atendidas dentro del reencuadre
autorizado (escenario de referencia ficticio) pero **falta documentarlas y cerrarlas por coherencia**;
de ahí surgen seis observaciones nuevas: tres de prioridad alta (D-01 a D-03), dos media y una baja.
A diferencia de c-250 (que ya traía las compuertas resueltas), c-252 arrancó con **cuatro decisiones de
hecho que solo los autores podían precisar** —cronología de la campaña manual, definición del tiempo manual,
ámbito laboral del régimen (a) y cronometraje "por pares"— y quedaron **RESUELTAS el 2026-11-26** (OQ-01 a
OQ-04). La condición para fijar fecha es doble: (1) la versión de defensa debe incorporar D-01 a
D-03, y (2) el director debe dar su **visto bueno escrito** a esa versión (el tribunal lo reinstala como
condición, a diferencia de c-250 donde C-06 la disolvió). Ninguna observación exige medir latencias ni
cambiar código: todas son prosa, documentación y una estadística descriptiva derivable de artefactos
versionados. El techo de la calificación lo fija la naturaleza de laboratorio de la evidencia (corpus
redactado por los autores).

## What Changes

Se producen seis correcciones, cada una con su pasaje exacto (referencias `archivo:línea` sobre las
fuentes `.tex` de `main`, versión `v1.6.5`; el apply las re-verifica). Las cuatro compuertas de autor
(OQ-01 a OQ-04) quedaron **RESUELTAS** y se consigna cada resolución:

- **D-01 (alta). Cronología día por día de la campaña manual.** La v1.6.5 ubica todo en octubre pero la
  cronología no cierra a nivel de día: entre el 01/10 (notificación) y el 02/10 (corrida automatizada de
  119 casos) debieron ocurrir recolección, redacción disociada, doble etiquetado con consenso y
  cronometraje manual por pares; la Figura 11 (`fig:cronograma`, `12-anexos.tex:53`) extiende la barra
  manual a todo octubre aunque el 09/10 es su cota. Hay que (a) declarar la cronología día por día con la
  evidencia de cada fecha, (b) declarar en §4.2 (`04:14`), §4.4 (`04:46`), Tabla 4
  (`tab:procedencia-numeros`, `04:71`) y Figura 11 que la fecha del cronometraje manual es declaración de
  los autores acotada por el commit del 09/10 (`ea62576`), (c) citar `68d06ec` (sintético) y `ea62576`
  (real) que hoy **no** aparecen, y (d) declarar que los 165,3 s del 3 de julio provenían del corpus
  sintético (simulado), no de una medición real del corpus vigente. **[OQ-1 RESUELTA: orden real automatizado primero (02/10) y manual después (antes del
  09/10); el manual no precedió. Los 165,3 s se declaran como valor sintético, no medido.]**
- **D-02 (alta). Definición del tiempo manual sin registro del cambio.** La v1.6.4 declaraba "lectura +
  carga estimada ~10 s"; la v1.6.5 declara "sin componente de carga" (Tabla 3 `04:31`, octava amenaza
  `04:131`, `07:38`, `07:285`), con **cifras idénticas** en ambas versiones. Ambas descripciones no pueden
  ser ciertas a la vez. Hay que (a) declarar cuál es la correcta y por qué la otra figuró en una versión
  entregada, (b) registrarla en el Anexo I.1 (Nota de versiones), y (c) reemplazar "retirado el componente
  de carga" (`04:127`) y "componente que la presente versión ya no contempla" (`12:354`) por redacción que
  no sugiera un cambio en los valores. **[OQ-2 RESUELTA: el componente nunca se sumó (clasificación pura); la descripción de v1.6.4 era inexacta y la
Nota de versiones debe decirlo; la cifra primaria se mantiene en 71,2 %.]** Esta compuerta zanja además la
contradicción abierta entre c-250 (D4: "sensibilidad de redondeo") y c-251 (E5: "herencia del componente carga
retirado"): el `-10 s` es el escenario C-02, no "remoción de carga" ni "redondeo".
- **D-03 (alta). Rastros del origen anterior del régimen (a).** La v1.6.5 declara el régimen (a) como "los
  autores y las personas de su círculo (familiares y amigos)" pero conserva léxico de una organización:
  "del sector servicios y con sede en la provincia de Mendoza" (`01:16`, `09:52`, `01:76`), y léxico
  corporativo "cliente/sucursal/estado de cuenta/sistema principal" (§4.4, §7.2 `11:18`, caso R015
  `07:277`). Hay que (a) declarar si los incidentes ocurrieron en el ámbito laboral de los reportantes, (b)
  si fue así, citar el deber de confidencialidad (art. 10, Ley 25.326), (c) retirar o explicar "del sector
  servicios y con sede en la provincia de Mendoza", y (d) registrar el cambio de origen en el Anexo I.1.
  **[OQ-3 RESUELTA: ámbito laboral sí, disociado de forma irreversible desde la recolección; corresponde art. 10
y corregir `11:18`; más el visto bueno escrito del director sobre la procedencia declarada — condición global
del tribunal.]**
- **D-04 (media). Plausibilidad de la lectura telefónica.** Leer una descripción tomó 87,2 s y recitar su
  paráfrasis 7,26 s (doce veces menos), pero §4.4 describe las 81 descripciones como "generales, sin
  detalles explícitos". Hay que (a) informar la extensión media (palabras/caracteres) por canal y por
  régimen, con un script TDD aditivo (`analisis_sexta_instancia_c252.py`) que la compute de
  `data/corpus_evaluacion_pseudonimizado.json` (campo `descripcion`), y (b) explicar qué parte de los 87,2 s
  es lectura y qué parte es decisión. Sin compuerta: derivable de datos versionados.
- **D-05 (media). Propagación y trazabilidad.** El Resumen, el Abstract y la Tabla 10 deben decir que el
  brazo manual midió solo la clasificación (no el registro) e informar también el 63,3 % sin telefonía
  (hoy solo en §8.1 `07:60` y `08:8`); el Anexo I.1 debe registrar el cambio de fechas (junio–agosto →
  octubre) y el del componente de carga (hoy ninguno está registrado); el Anexo I.2 (`12:251`) debe sumar
  la devolución de quinta instancia (25/11/2026) — hoy se detiene en la cuarta (19-11). Sin compuerta.
- **D-06 (baja). Coherencia y redacción.** Aclarar cómo A1 y T1 se cronometraron "por pares" (`04:16`)
  trabajando en domicilios separados; unificar Anexo F "redactadas por los autores" (`12:149`) con §4.4 "por
  uno de los autores" (`04:129`, `09:54`, `06:54`); en §8.1 reemplazar "respaldados por" (`07:38`) por la
  fórmula de §4.5; en §7.5 corregir "titulares… distintos de los autores" (`11:46`) porque los autores
  también son reportantes; reemplazar "registro histórico/retirado" (`12:247`) por una forma sin barra.
  **[OQ-4 RESUELTA: A1 y T1 cronometraron juntos, en el domicilio de uno de los autores; atribución única de
autoría.]**

**Release.** Este change produce la **versión de defensa** `v1.6.5` → `v1.6.6` siguiendo el procedimiento
de c-250 (bump, Anexo B con hash/tag, Nota de versiones, recompilación + derivados, `CHANGES.md`,
`knowledge-base/`, `dictamen-correcciones.md` con sección c-252, respuestas de defensa). A diferencia de
c-250, aquí SÍ hay una tarea de **obtener el visto bueno escrito del director** (condición reinstalada por
el tribunal), y la release queda BLOQUEADA hasta que (1) D-01 a D-03 estén aplicados y (2) el director
firme. El grupo de release es gobernanza **HIGH**.

**Versionado de la devolución.** Se versiona la transcripción `.md` de la sexta instancia como
`auditorias/Devolucion_Sexta_Instancia_TFI_v1.6.5_2026-11-26.md` (mismo formato que la quinta), y el PDF
queda como evidencia de referencia.

**BREAKING (afirmaciones de método y de procedencia):** la tesis declara la cronología real de la campaña manual
(automatizado primero 02/10, manual después antes del 09/10; ya no "manual precedió"), define el tiempo manual
como clasificación pura y registra en la Nota de versiones que la v1.6.4 estaba mal descrita (declaraba una carga
~10 s que nunca existió), y declara el ámbito laboral del régimen (a) —disociado desde la recolección— con el deber
de confidencialidad del art. 10. OQ-2 resuelta: el componente "~10 s" NUNCA se sumó, por lo que la cifra primaria
se mantiene en 71,2 % (no baja a 65,6 %).

Fuera de alcance: arquitectura, código, latencias del flujo automatizado, campaña complementaria (E1, E2,
O1, O2), balance neto y sensibilidad del Anexo K (se conservan, la sexta instancia lo confirmó); cifras
canónicas globales y por canal (61,57 s, 17,76 s, 51,6 s / 65,6 % con descuento) no cambian salvo lo que
OQ-2 determine; `App/`, `n8n/`; casos del corpus y sus JSON (SHA-256 congelado; el campo
`metadata.descripcion` histórico de `12:151` se deja intacto); mover, borrar o recrear tags anteriores.

**Gobernanza: MEDIUM** (prosa de la tesis y documentación). Sube a **HIGH** el capítulo legal
(`11-aspectos-legales.tex`, D-03 y D-06 en §7.5), `docs/seguridad/`, `data/README.md`, el grupo de release
(publica un tag sobre el ejemplar defendido), y la gestión del visto bueno escrito del director. Las cuatro
compuertas OQ-01 a OQ-04 bloquean las tareas correspondientes hasta que los autores las respondan.

**Skills de dominio:** el cambio es de LaTeX y documentación; de `.agents/SKILLS.md` solo aplica
`python-testing-patterns` al script TDD de longitud de descripciones (D-04). Las demás no corresponden.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tesis-reencuadre-cuarta-instancia`: se AGREGAN requisitos que cierran D-01, D-02, D-03 y D-06 de la
  sexta instancia: cronología día por día de la campaña manual con evidencia fechada (D-01), definición del
  tiempo manual registrada como corrección en la Nota de versiones sin sugerir cambio de valores (D-02),
  origen del régimen (a) sin léxico de organización y con deber de confidencialidad si corresponde (D-03), y
  coherencia de redacción (domicilio/por pares, atribución de autoría, "respaldados por", "titulares",
  "histórico/retirado"; D-06).
- `tesis-numeros-canonicos`: se AGREGA el requisito de registrar el nuevo estadístico descriptivo de
  extensión media de descripciones por canal y por régimen (D-04) con su script generador versionado, y la
  determinación de la cifra primaria de la sub-hipótesis 1 (71,2 % vs 65,6 %) según la resolución de OQ-2.
- `tesis-document`: se AGREGA el requisito de trazabilidad de la release `v1.6.6` (bump de versión, Anexo B
  con hash/tag, Anexo I.1 con cambio de fechas y de definición del tiempo manual, Anexo I.2 con quinta y
  sexta instancia, `compilacion.md`, tag anotado, `auditorias/Devolucion_Sexta_Instancia...md`) y el
  registro del cierre de la sexta instancia, condicionado al visto bueno escrito del director.

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `docs/Tesis/v10 (IA)/paper/sections/00-resumen.tex`, `00-portada.tex` | Modificado | Resumen/Abstract: solo clasificación + 63,3 % sin telefonía (D-05); versión `v1.6.6` |
| `.../sections/01-introduccion.tex` | Modificado | §1.2 retiro/explicación "del sector servicios… Mendoza" (D-03) |
| `.../sections/04-marco-metodologico.tex` | Modificado | §4.2/§4.4/§4.8, Tabla 3, Tabla 4, amenazas (D-01, D-02, D-04, D-06) |
| `.../sections/07-resultados.tex` | Modificado | §8.1 "respaldados por"→fórmula §4.5 (D-06), Tabla 10 (D-05) |
| `.../sections/08-discusion.tex` | Modificado | §9.1 explicaciones rivales corregidas al orden real automatizado→manual (D-01) |
| `.../sections/09-conclusiones.tex` | Modificado | Retiro "del sector servicios… Mendoza" (D-03) |
| `.../sections/11-aspectos-legales.tex` | Modificado (HIGH) | §7.2 léxico corporativo, §7.5 "titulares… distintos de los autores", art. 10 (D-03, D-06) |
| `.../sections/12-anexos.tex` | Modificado | Figura 11, Anexo F (atribución), Anexo sensibilidad ("ya no contempla"), I.1 (cambios), I.2 (quinta/sexta), "histórico/retirado" (D-01, D-02, D-05, D-06) |
| `evaluation/data/campana/analisis/analisis_sexta_instancia_c252.{py,json,md,SHA256SUMS.txt}`, `test_analisis_sexta_instancia_c252.py` | Nuevo (aditivo) | Extensión media de descripciones por canal/régimen (D-04) |
| `auditorias/Devolucion_Sexta_Instancia_TFI_v1.6.5_2026-11-26.md` | Nuevo (aditivo) | Transcripción `.md` de la sexta instancia |
| `docs/Tesis/Correcciones/respuestas-tribunal-sexta-instancia.md`, `docs/defensa/respuestas-tribunal.md` | Modificado/Nuevo | Respuestas a las 10 preguntas probables del tribunal (sección 6) |
| `docs/Tesis/v10 (IA)/paper/main.pdf`, `compilacion.md`, `tesis_para_agente.md`, `tesis_*.txt`, extractos, `docs/Tesis/tesis_ultima_version.pdf` | Regenerado | Release `v1.6.6` (versión de defensa, bloqueada por visto bueno del director) |
| `README.md`, `knowledge-base/`, `CHANGES.md` | Modificado | Propagación de la versión y registro del change |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Sección c-252: compuertas OQ-01 a OQ-04, ANTES/DESPUES, release |