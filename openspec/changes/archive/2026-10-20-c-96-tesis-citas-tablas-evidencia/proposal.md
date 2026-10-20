# Proposal: c-96 — Citas, tablas y evidencia transversal

## Why

La auditoria de la tesis detecto un conjunto de defectos transversales de
trazabilidad de fuentes y de respaldo evidenciario que ninguno de los changes en
curso (c-76, c-77, c-78, c-80) cubre de forma completa: la Tabla~1 (Capitulo~3)
compara seis soluciones comerciales y una fila "Propuesta" sin una sola cita, sin
linea de fuente y sin fecha de consulta, y ademas autoevalua la propuesta dentro
de la misma tabla; la definicion de empresa mediana atribuida a la "Secretaria de
la Pequena y Mediana Empresa" (§1.1) no tiene cita ni entrada bibliografica; queda
una segunda cita huerfana "(APA, 2017)" en §11.5; los pasajes §1.7 y §6.1
reintroducen el error de rotular a N8N como "codigo abierto" cuando su licencia
oficial es Sustainable Use (error que §2.3/§3.2 evitan); §1.2 y §1.8 describen de
forma inconsistente a la organizacion adoptante; ninguna de las nueve tablas tiene
linea de fuente (APA~7 exige "Fuente: elaboracion propia" o la referencia); y la
densidad de citas es desigual (el Capitulo~6 tiene pocas citas para su extension y
el Capitulo~7 tiene CERO sobre afirmaciones propias). Corregir esto es un requisito
de integridad academica y de trazabilidad evidenciaria de governance BAJO que no
altera la arquitectura ni el codigo del sistema; opera exclusivamente sobre el
arbol LaTeX `docs/Tesis/v9 (IA)/` y el `.bib`.

## What Changes

### Grupo Citas, tablas y evidencia transversal (A-26, M-01, A-27, B-01, T1-T2)

| Id | Severidad | Correccion |
|----|-----------|-----------|
| A-26 | Alta | Tabla~1 (`03-estado-del-arte.tex:36-54`): agregar linea de fuente, cita y fecha de consulta por fila; retirar/neutralizar la fila "Propuesta" que se autoevalua en la misma tabla. |
| M-01 + huerfana | Media/Alta | §1.1 (`01-introduccion.tex:12`): agregar cita y entrada bibliografica de la Secretaria de la Pequena y Mediana Empresa (SEPyME) para la definicion de empresa mediana. §11.5 (`11-aspectos-legales.tex:28`): resolver la cita huerfana "(APA, 2017)" (agregar entrada `APA2017` o retirar la cita). |
| A-27 | Alta | §1.7 (`01-introduccion.tex:60`) y §6.1 (`06-implementacion.tex:8`): retirar a N8N de la enumeracion "de codigo abierto" y matizar su licencia Sustainable Use, alineando con §2.3/§3.2. |
| B-01 | Baja | §1.2 (`01-introduccion.tex:16`) y §1.8 (`01-introduccion.tex:68`): unificar la denominacion y caracterizacion de la organizacion adoptante (una sola organizacion mediana del sector servicios, ~120 usuarios, cinco areas, Mendoza). |
| T1 (transversal) | Media | Agregar linea de fuente (`\par Fuente: ...`) a las nueve tablas del documento; coordinar con c-80, que es dueno del formato de tablas (`\small`, `\raggedright`). |
| T2 (transversal, NUEVO) | Media | Aumentar y equilibrar la densidad de citas: Capitulo~6 y, en especial, Capitulo~7 (hoy con cero citas sobre afirmaciones propias) y las filas de la Tabla~1 del Capitulo~3, usando la bibliografia ya incorporada por c-78; NO duplicar el trabajo de c-78, solo referenciarlo. |

Detalle de cada item:

- **A-26 — Tabla~1 sin respaldo**: la tabla compara Zendesk Suite, Freshdesk,
  Jira Service Management, ServiceNow ITSM, osTicket y la fila "Propuesta" con
  afirmaciones comerciales (despliegue, clasificacion automatica, modelo de costo)
  sin ninguna cita, sin linea de fuente y sin fecha de consulta; ademas la fila
  "Propuesta" se autoevalua con los mismos criterios que las soluciones de terceros,
  lo que constituye un sesgo de autoevaluacion. La correccion MUST agregar la linea
  de fuente con fecha de consulta y una cita por fila de solucion comercial, y MUST
  retirar la fila "Propuesta" de la tabla (o separarla del cuerpo comparativo) para
  eliminar la autoevaluacion en la misma grilla.
- **M-01 — Definicion de empresa mediana sin cita**: §1.1 afirma que la Secretaria
  de la Pequena y Mediana Empresa define como medianas a las organizaciones de
  entre 50 y 200 trabajadores en el sector servicios, sin cita ni entrada en el
  `.bib`. La correccion MUST agregar la cita formal y la entrada correspondiente
  (SEPyME) o reformular la afirmacion sin atribuirla a una fuente inexistente.
- **Cita huerfana "(APA, 2017)"**: §11.5 cita "(APA, 2017)" como respaldo de la
  justificacion etica de la observacion sin conocimiento previo (debriefing). La
  cita MUST resolverse: agregar la entrada `APA2017` al `.bib` o retirar la cita
  y sostener el argumento sin ella.
- **A-27 — N8N "codigo abierto"**: §1.7 enumera "herramientas de bajo costo y
  codigo abierto ---N8N, Python, FastAPI, PostgreSQL---" y §6.1 afirma que la
  implementacion uso "exclusivamente tecnologias de codigo abierto". N8N no es
  codigo abierto OSI: su licencia oficial es Sustainable Use (fair-code), tal como
  §3.2 ("licencia Sustainable Use") y §6.3 ("licencia de codigo fuente disponible
  (fair-code)") ya reconocen. La correccion MUST retirar a N8N de la enumeracion
  "de codigo abierto" y matizar su licencia en ambos pasajes.
- **B-01 — Organizacion adoptante inconsistente**: §1.2 la describe como "una
  organizacion mediana del sector servicios con sede en la provincia de Mendoza"
  y §1.8 como "una unica organizacion del sector servicios", sin nombrarla ni
  caracterizarla mas alla de los ~120 usuarios y las cinco areas. La correccion
  MUST unificar la denominacion y la caracterizacion en ambos pasajes (misma
  etiqueta, mismos atributos, sin introducir un nombre propio no autorizado).
- **T1 — Linea de fuente en las nueve tablas**: ninguna de las nueve tablas
  (`tab:comparativa` en 03; `tab:variables` en 04; `tab:capas`, `tab:entidades`,
  `tab:api` en 05; `tab:tiempos`, `tab:matriz`, `tab:metricas`, `tab:errores` en
  07) declara su fuente. APA~7 exige "Fuente: elaboracion propia" o la referencia.
  La correccion MUST agregar la linea de fuente a las nueve, en coordinacion con
  c-80 (que posee el formato de tabla) para no pisar su composicion.
- **T2 — Densidad de citas desigual**: el Capitulo~6 concentra pocas citas para su
  extension y el Capitulo~7 no tiene ninguna, de modo que afirmaciones propias
  quedan sin respaldo bibliografico; la Tabla~1 del Capitulo~3 sostiene toda su
  comparacion sin citas. La correccion MUST agregar citas donde se formulan
  afirmaciones apoyadas en literatura, reutilizando la bibliografia que c-78 ya
  incorpora (2023-2026) y sin duplicar su trabajo ni introducir referencias nuevas
  fuera de las dos entradas de M-01.

### Orden de aplicacion (dependencia blanda)

Este change comparte archivos con c-78 (`03-estado-del-arte.tex`, `.bib`) y con
c-80 (`03`, `05`, `07` por formato de tablas). MUST aplicarse **despues** de c-78
(para citar la bibliografia ya incorporada y no duplicar entradas) y **en
coordinacion** con c-80 (que es dueno del formato `\small`/`\raggedright`); T1
agrega solo la linea de fuente, no recompone la tabla. Ver `design.md`.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `tesis-document`: se modifican los requisitos de trazabilidad de fuentes
  (citas y linea de fuente en tablas), de atribucion de la definicion de empresa
  mediana y del marco etico, de exactitud de la licencia de N8N, de consistencia en
  la descripcion de la organizacion adoptante y de respaldo evidenciario de las
  afirmaciones por capitulo. No se modifica `evaluation-framework`.

## Impact

- `docs/Tesis/v9 (IA)/paper/sections/03-estado-del-arte.tex` (Tabla~1)
- `docs/Tesis/v9 (IA)/paper/sections/01-introduccion.tex` (§1.1, §1.2, §1.7, §1.8)
- `docs/Tesis/v9 (IA)/paper/sections/06-implementacion.tex` (§6.1)
- `docs/Tesis/v9 (IA)/paper/sections/11-aspectos-legales.tex` (§11.5, cita huerfana)
- `docs/Tesis/v9 (IA)/paper/sections/04-marco-metodologico.tex`,
  `05-arquitectura.tex`, `07-resultados.tex` (lineas de fuente de las tablas)
- `docs/Tesis/v9 (IA)/Bibliography_base.bib` (solo las dos entradas faltantes:
  SEPyME y APA~2017)
- `main.pdf` (se recompila despues en Overleaf, no en este repo)
- `openspec/specs/tesis-document/spec.md` (delta aplicado al archivar)

No se toca `App/**`. No se editan artefactos de c-76/c-77/c-78/c-80 ni
`CHANGES.md`. No se modifica `docs/Tesis/Correcciones/dictamen-correcciones.md`.
El alcance de tabla/formato (`\small`, `\raggedright`) es de c-80; el alcance de
bibliografia moderna 2023-2026 es de c-78. Este change solo agrega la linea de
fuente y las citas faltantes, y las dos entradas de M-01.

## Rollback Plan

`git checkout --` sobre los `.tex` y `Bibliography_base.bib` afectados, o
`git revert` del commit del change. Los artefactos OPSX se descartan con el
directorio del change.

## Success Criteria

- [ ] La Tabla~1 tiene linea de fuente con fecha de consulta y una cita por fila
      de solucion comercial; la fila "Propuesta" ya no se autoevalua dentro de la
      grilla comparativa.
- [ ] §1.1 cita formalmente a la SEPyME para la definicion de empresa mediana y
      existe la entrada correspondiente en `Bibliography_base.bib` (o la
      atribucion fue reformulada sin fuente inexistente).
- [ ] La cita huerfana "(APA, 2017)" de §11.5 quedo resuelta (entrada `APA2017`
      agregada o cita retirada); cero citas huerfanas en el documento.
- [ ] §1.7 y §6.1 ya no rotulan a N8N como codigo abierto; su licencia Sustainable
      Use queda explicitada, en consistencia con §2.3/§3.2/§6.3.
- [ ] §1.2 y §1.8 describen la organizacion adoptante de forma consistente (misma
      denominacion y mismos atributos).
- [ ] Las nueve tablas declaran su linea de fuente (APA~7) sin romper la
      composicion de c-80.
- [ ] Los capitulos 3, 6 y 7 tienen citas donde se formulan afirmaciones apoyadas
      en literatura; no se introducen referencias nuevas fuera de las dos entradas
      de M-01 ni se duplica el trabajo de c-78.
- [ ] `openspec validate c-96-tesis-citas-tablas-evidencia --strict` pasa.
- [ ] `pdf` recompilado en Overleaf (XeLaTeX) sin errores fatales (tarea posterior;
      no hay toolchain LaTeX local).
