# Design: c-96 — Citas, tablas y evidencia transversal

## Context

Ver `proposal.md` — Why. Estado relevante verificado contra el arbol de trabajo
v9 (2026-10-19):

- **Tabla~1** (`03-estado-del-arte.tex:36-54`, `tab:comparativa`): cinco filas de
  soluciones comerciales (Zendesk Suite, Freshdesk, Jira Service Management,
  ServiceNow ITSM, osTicket) mas una fila `\textbf{Propuesta}`
  (`:51`). Ninguna fila tiene cita; la tabla no tiene linea de fuente ni fecha de
  consulta; la fila "Propuesta" usa los mismos criterios que las soluciones de
  terceros (autoevaluacion).
- **Definicion de empresa mediana** (`01-introduccion.tex:12`, §1.1): atribuye a
  la "Secretaria de la Pequena y Mediana Empresa" el rango 50-200 trabajadores
  sin cita ni entrada en el `.bib`.
- **Cita huerfana "(APA, 2017)"** (`11-aspectos-legales.tex:28`, §11.5): sostiene
  la justificacion etica del debriefing; no existe `APA2017` en el `.bib`.
- **N8N "codigo abierto"**: `01-introduccion.tex:60` (§1.7) enumera "herramientas
  de bajo costo y codigo abierto ---N8N, Python, FastAPI, PostgreSQL---";
  `06-implementacion.tex:8` (§6.1) afirma "exclusivamente tecnologias de codigo
  abierto". En contraste, `03-estado-del-arte.tex:20` (§3.2) dice "licencia
  Sustainable Use" y `06-implementacion.tex:32` (§6.3) dice "licencia de codigo
  fuente disponible (fair-code)".
- **Organizacion adoptante**: `01-introduccion.tex:16` (§1.2) "una organizacion
  mediana del sector servicios con sede en la provincia de Mendoza"; `:68` (§1.8)
  "una unica organizacion del sector servicios". Atributos: ~120 usuarios, cinco
  areas, Mendoza.
- **Nueve tablas sin linea de fuente**: `03:36`, `04:22`, `05:12`, `05:66`,
  `05:92`, `07:12`, `07:42`, `07:61`, `07:92`. Ninguna declara fuente APA~7.
- **Densidad de citas** (conteo `rg` de comandos de cita): 03 = 5 citas / ~1.209
  palabras; 06 = 6 / ~3.269; **07 = 0 / ~1.471**; 08 = 5 / ~1.879; 09 = 0 /
  ~1.119; 10 = 2 / ~1.509. El Capitulo~7 no cita nada y el Capitulo~6 tiene baja
  densidad para su extension.
- La bibliografia moderna 2023-2026 es propiedad de **c-78**; el formato de tablas
  (`\small`, `\raggedright`) es propiedad de **c-80**. El aparato de citas usa
  `biblatex` con `style=apa` (`preambles/preamble.tex:92`).

Restriccion dura: la tesis se compila en Overleaf (sin toolchain LaTeX local). No
se toca `App/**`. No se editan artefactos de c-76/c-77/c-78/c-80 ni `CHANGES.md`.

Discrepancia de alcance: la consigna menciona `.../_.tex` para las lineas de
fuente; NO existe ningun archivo `_.tex` en el arbol (verificado con `find`). Las
lineas de fuente se agregan en cada archivo de seccion dueno de su tabla.

## Goals / Non-Goals

**Goals:**

- Dar trazabilidad de fuentes a la Tabla~1 y eliminar su sesgo de autoevaluacion.
- Resolver las dos atribuciones sin respaldo (SEPyME en §1.1 y la cita huerfana
  APA~2017 en §11.5).
- Corregir el rotulo "codigo abierto" de N8N en §1.7 y §6.1.
- Unificar la descripcion de la organizacion adoptante en §1.2 y §1.8.
- Agregar linea de fuente a las nueve tablas sin invadir el formato de c-80.
- Aumentar la densidad de citas donde hay afirmaciones apoyadas en literatura,
  reutilizando la bibliografia de c-78.

**Non-Goals:**

- No tocar el formato de tablas (`\small`, `\raggedright`): es c-80.
- No modernizar la bibliografia 2023-2026 ni corregir metadatos existentes: es
  c-78.
- No tocar los numeros del corpus, la estadistica, la ventana temporal ni el
  prompt (c-76 / c-77).
- No modificar `evaluation-framework` ni `App/**`.
- No recompilar localmente (Overleaf).
- No fabricar referencias para cubrir las citas faltantes.

## Decisions

### D-A26 — Tabla 1: fuente, citas y fecha de consulta; sin autoevaluacion

La tabla compara afirmaciones comerciales sin respaldo. La correccion agrega:

1. Una linea de fuente tras `\bottomrule` con la referencia de cada proveedor y
   la fecha de consulta (p. ej. documentacion oficial de cada plataforma,
   consultada en la fecha de cierre de la revision).
2. Una cita por fila de solucion comercial, apoyada en la documentacion o en una
   referencia de la bibliografia existente. Se reutilizan entradas del `.bib`
   cuando corresponda; si una plataforma no tiene entrada, se evalua si la
   documentacion oficial justifica una entrada nueva — **pero el presupuesto de
   entradas nuevas de este change es de DOS** (SEPyME y APA~2017). Por lo tanto,
   la via preferente es citar documentacion oficial en la linea de fuente con
   URL y fecha, sin crear entradas nuevas, o reformular la afirmacion para que no
   requiera cita.
3. **Retiro de la fila "Propuesta"** de la grilla comparativa (`:51`). La
   propuesta se compara contra las soluciones en prosa (que ya existe en
   `:56-58`) con respaldo, en lugar de autoevaluarse con los mismos criterios
   dentro de la tabla.

**Alternativa considerada**: mantener la fila "Propuesta" y agregarle una nota
"autoevaluacion". Se descarta porque el sesgo persiste mientras la propuesta
comparta grilla y criterios con los terceros; la separacion es mas honesta
academicamente.

### D-M01 — SEPyME y cita huerfana APA 2017

- **SEPyME**: agregar la cita en §1.1 y una entrada nueva en
  `Bibliography_base.bib` (organismo oficial; `author` institucional, `title`,
  `year`, `url` de la fuente oficial y fecha de consulta). Si no se puede
  verificar la fuente oficial exacta del rango 50-200, la alternativa es
  reformular la afirmacion para no atribuirla a una fuente especifica (el rango
  igual queda como dato de contexto sin atribucion). La opcion preferida es la
  cita formal con entrada verificable.
- **APA 2017** (`11-aspectos-legales.tex:28`): la cita se refiere a las
  recomendaciones de la Asociacion Americana de Psicologia para investigaciones
  con observacion sin conocimiento previo. Se agrega la entrada `APA2017` al
  `.bib` (Ethical Principles of Psychologists and Code of Conduct, APA, 2017) o,
  si no se puede verificar la edicion/ano exactos, se retira la cita y se sostiene
  el argumento sin ella. La resolucion MUST eliminar la cita huerfana.

**Alternativa considerada**: dejar la cita y no agregar entrada. Se descarta:
produce cita huerfana, que el invariante del documento prohibe.

### D-A27 — N8N: retirar del rotulo "codigo abierto" y matizar la licencia

- §1.7 (`01-introduccion.tex:60`): reescribir la enumeracion para no incluir a
  N8N bajo "codigo abierto". Opciones: (a) separar N8N y describirlo como
  herramienta de orquestacion autoalojada con licencia Sustainable Use;
  (b) citar solo las piezas que SI son codigo abierto (Python, FastAPI,
  PostgreSQL) y tratar N8N aparte. Se prefiere (a), que preserva el sentido
  ("bajo costo y autoalojable") sin el error de licencia.
- §6.1 (`06-implementacion.tex:8`): reemplazar "exclusivamente tecnologias de
  codigo abierto" por una formulacion que distinga las piezas de codigo abierto
  de N8N, cuya licencia es Sustainable Use (fair-code), consistente con §3.2 y
  §6.3. No se toca `:10` (version de N8N), que es alcance de c-80.

**Alternativa considerada**: usar "codigo abierto" en sentido amplio (código
disponible). Se descarta: la tesis ya uso el termino tecnico correcto en §3.2 y
§6.3, y la inconsistencia es precisamente el defecto A-27.

### D-B01 — Organizacion adoptante consistente

Elegir UNA denominacion y UN conjunto de atributos y aplicarlos en §1.2 (`:16`) y
§1.8 (`:68`). La caracterizacion canonica es "una organizacion mediana del sector
servicios con sede en la provincia de Mendoza, de aproximadamente 120 usuarios
internos distribuidos en cinco areas funcionales". §1.8 deja de decir "una unica
organizacion" como si fuera una entidad distinta y adopta la misma etiqueta. No se
introduce un nombre propio (la organizacion es anonima en la tesis).

### D-T1 — Linea de fuente en las nueve tablas (coordinado con c-80)

Agregar a cada tabla una linea de fuente APA~7 inmediatamente despues del cierre
tabular, dentro del entorno `table` (p. ej. `\par\smallskip\footnotesize Fuente:
elaboracion propia.` o la referencia). La linea es de CONTENIDO (fuente), no de
formato; c-80 sigue siendo dueno de `\small`/`\raggedright`. Para las tablas de
resultados (`tab:tiempos`, `tab:matriz`, `tab:metricas`, `tab:errores`) la fuente
es "elaboracion propia a partir del corpus de validacion (n = 200)"; para
`tab:variables` y `tab:capas`/`tab:entidades`/`tab:api`, "elaboracion propia". La
Tabla~1 usa la linea de fuente con las referencias y fecha de consulta de D-A26.

**Alternativa considerada**: delegar toda la linea de fuente a c-80. Se descarta:
c-80 no tiene las citas ni la fecha de consulta de la Tabla~1, que son evidencia,
no formato; pero se MUST coordinar para no duplicar ni pisar la composicion.

### D-T2 — Densidad de citas sin duplicar c-78

Agregar citas donde hay afirmaciones apoyadas en literatura:

- **Capitulo~7** (`07-resultados.tex`, hoy 0 citas): las afirmaciones
  metodologicas/interpretativas que invocan practicas de terceros (p. ej.
  metricas de evaluacion, intervalos de confianza, pruebas no parametricas) se
  respaldan con entradas existentes (`Sokolova2009_performance_measures`,
  `Wilson1927_probable_inference`, etc.) o con las referencias 2023-2026 que c-78
  ya incorporo.
- **Capitulo~6** (`06-implementacion.tex`): reforzar afirmaciones metodologicas
  con entradas existentes; no crear referencias nuevas.
- **Capitulo~3**: la Tabla~1 se respalda segun D-A26.

Regla dura: el unico presupuesto de entradas nuevas es el de D-M01 (SEPyME y
APA~2017). Cualquier otra cita MUST resolverse contra entradas ya existentes en
el `.bib`, incluidas las de c-78. Si c-78 aun no esta aplicado, las citas se
limitan a las entradas ya presentes y se difiere el resto (ver Open Questions).

### D-ORDER — Orden de aplicacion

Aplicar **despues** de c-78 (para citar su bibliografia 2023-2026) y **en
coordinacion** con c-80 (para no pisar el formato de tablas). Si c-78 no esta
aplicado al momento de implementar, T2 se ejecuta solo con la bibliografia
preexistente y la parte que depende de las referencias nuevas queda como tarea
condicionada. No comparte archivos con c-76/c-77 salvo `07-resultados.tex` (c-76
es dueno de los numeros); este change NO edita cifras.

## Risks / Trade-offs

- **[Conflicto de edicion con c-80 en las tablas]** → c-80 posee `\small` y
  `\raggedright`; c-96 solo agrega la linea de fuente. Aplicar despues de c-80 y
  limitar el diff a la linea de fuente.
- **[Conflicto con c-78 en el `.bib`]** → c-78 agrega referencias 2023-2026;
  c-96 agrega solo SEPyME y APA~2017. Coordinar para no duplicar claves y
  re-verificar cero huerfanas tras ambas.
- **[Fuente oficial de SEPyME no verificable]** → si el rango 50-200 no se puede
  respaldar con la fuente oficial, reformular la afirmacion sin atribucion en
  lugar de fabricar la referencia.
- **[Cita huerfana reintroducida]** → la resolucion de "(APA, 2017)" MUST dejar
  cero huerfanas; verificar con el script de citas y con `rg`.
- **[Exceso de citas artificial]** → agregar citas solo donde hay afirmaciones
  apoyadas en literatura; no inflar la densidad de forma mecanica.
- **[Longitud > 100 paginas]** → los cambios son textuales acotados; no deberian
  mover el conteo. Verificar en la recompilacion.

## Migration Plan

1. Aplicar D-M01 (entradas SEPyME/APA~2017 en el `.bib` y citas en 01/11).
2. Aplicar D-A27 (01:60, 06:8) y D-B01 (01:16, 01:68).
3. Aplicar D-A26 (Tabla~1) y D-T1 (linea de fuente en las nueve tablas).
4. Aplicar D-T2 (citas en 03/06/07) reutilizando la bibliografia de c-78.
5. Recompilar en Overleaf (XeLaTeX) y validar con `openspec validate --strict`.

**Rollback**: `git checkout --` sobre los `.tex` y `Bibliography_base.bib`
afectados, o `git revert` del commit del change.

## Open Questions

- **OQ-C96-1**: si c-78 no esta aplicado al implementar, las citas de T2 que
  dependen de las referencias 2023-2026 quedan condicionadas a la aplicacion de
  c-78. No cambia specs ni enfoque: la tarea se marca como condicionada y el
  resto se ejecuta con la bibliografia existente.
- **OQ-C96-2**: la fecha de consulta de la Tabla~1 se fija a la fecha de cierre
  de la revision bibliografica de la tesis; se documenta en la linea de fuente.
