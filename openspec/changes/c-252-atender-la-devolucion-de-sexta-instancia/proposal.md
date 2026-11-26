# Proposal: Atender la devolución de sexta instancia del tribunal

## Why

La devolución de sexta instancia sobre `v1.6.5` (`auditorias/Devolucion_Sexta_Instancia_TFI_v1.6.5_2026-11-26.md`,
emitida el 26/11/2026; PDF de referencia en el mismo directorio) dictamina **APTA PARA DEFENSA**, 7,5/10
(quinta instancia: 7,3). El tribunal acepta el reencuadre de la cuarta instancia y da por corregidas C-03,
C-04 y C-05 (C-07 casi corregida), pero C-01, C-02 y C-06 quedaron "atendidas con el reencuadre" y sin
documentación suficiente, y pasan a tres observaciones de prioridad alta (D-01 a D-03) que tocan la línea
base manual, la única que sostiene la sub-hipótesis corroborada. **Condición para fijar fecha:** (1) la
versión de defensa incorpora D-01 a D-03; (2) el director da su visto bueno escrito a esa versión. D-04 a
D-06 pueden resolverse en la misma versión o exponerse en la defensa, y el grupo debe poder responder las
preguntas 1 a 4 de la sección 6. A diferencia de c-250, aquí **varios hechos solo los pueden declarar los
autores** (cronología día por día, quién midió los 165,3 s, si el tiempo manual incluyó carga, si los
incidentes del régimen (a) son laborales): el change los modela como compuertas OQ y no los inventa.

## What Changes

Seis correcciones, cada una anclada en el texto vigente de `main` (`S/` = `docs/Tesis/v10 (IA)/paper/sections/`;
líneas de `main` al 2026-11-26, que ya contiene el estado aplicado de c-251; el apply las re-verifica con `rg`):

- **D-01 (alta). Cronología día por día de la campaña 2026-10.** Hoy §4.2 (`S/04-marco-metodologico.tex:14`)
  afirma que los 200 casos se procesaron "primero por el flujo manual (octubre de 2026) y luego por el
  automatizado (octubre de 2026)"; §4.4 (`04:46`) y la Tabla 4 (`04:78`, fila "Campaña 2026-10 (oct 2026)")
  ubican el cronometraje en octubre; la Figura 11 (`S/12-anexos.tex:53`, fuente `docs/diagrams/cronograma.md`)
  dibuja la barra de la campaña manual del 01/10 al 31/10 aunque el 09/10 (`ea62576`) es su cota superior. El
  change agrega una cronología día por día (recolección, redacción disociada, doble etiquetado con consenso,
  cronometraje manual por mitad y por operador, corridas automatizadas del 02/10 y del 05-06/10) con la
  evidencia de cada fecha; declara en §4.2, §4.4, Tabla 4 y Figura 11 que la fecha del cronometraje manual es
  una **declaración de los autores acotada por el commit del 09/10**; y, si el orden manual → automatizado no
  se sostiene para los 119 casos, corrige §4.2 (`04:14`), la primera amenaza (`04:117`) y la tercera
  explicación rival de §9.1 (`S/08-discusion.tex:22`). Responde quién midió los 165,3 s de la versión del 3 de
  julio y sobre qué textos (I.1, `S/12-anexos.tex:241`). **[GATED OQ-01]**
- **D-02 (alta). Registro del cambio en la definición del tiempo manual.** La v1.6.4 (`v1.6.4:04:89`) decía
  que a la lectura "se le sumó un tiempo fijo de carga del ticket [...] en el orden de 10 s [...] ya incluido
  en `tiempo_manual_s`"; la v1.6.5 dice que "no incluye componente de carga" (`04:31`, `04:46`, `04:89`,
  `S/07-resultados.tex:38`, `07:285`, `08:22`) con cifras idénticas. Se declara cuál de las dos descripciones
  es la correcta y por qué la otra figuró en una versión entregada; se registra en el Anexo I.1 con el mismo
  criterio que los retiros anteriores; se reemplaza "retirado el componente de carga" (`04:127`) y "componente
  que la presente versión ya no contempla" (`S/12-anexos.tex:354`, frase que introdujo c-251 E5) por una
  redacción que no sugiera un cambio de valores. Si el componente se sumó, la cifra primaria pasa a ser la del
  descuento de 10 s (65,6 %) y no 71,2 %, con propagación completa. **[GATED OQ-02]**
- **D-03 (alta). Rastros del origen anterior del régimen (a).** Se retira o explica "del sector servicios y
  con sede en la provincia de Mendoza" aplicado a las personas del círculo (`S/01-introduccion.tex:16`,
  repetido en `S/09-conclusiones.tex:52`); se declara si los incidentes del régimen (a) ocurrieron en el ámbito
  laboral de quienes los reportaron y, si fue así, el deber de confidencialidad (art. 10, Ley 25.326) en el
  capítulo legal (`S/11-aspectos-legales.tex:16`, `:18`, `:46`, `:54`); se explica una sola vez en §4.4
  (`04:46`) el léxico corporativo («cliente», «sucursal», «estado de cuenta», «sistema principal»), los casos
  de trabajo de §8.5 (`S/07-resultados.tex:277`, R015) y los sectores de la Tabla 18 (`07:255`), y que la
  composición 119/81 descansa en la declaración de los autores; se registra en I.1 el cambio de origen
  respecto de la v1.6.4; se incorpora el visto bueno escrito del director sobre la procedencia declarada.
  **[GATED OQ-03; HIGH]**
- **D-04 (media). Plausibilidad de la lectura telefónica.** Script TDD aditivo
  (`evaluation/data/campana/analisis/analisis_sexta_instancia_c252.py`, prueba primero) que calcula la extensión
  media de las descripciones (palabras y caracteres) por canal y por régimen, y el tiempo manual por palabra.
  La prosa de §4.4 (`04:46`), la sexta amenaza (`04:127`), §8.1 y la Tabla 12 (`07:57-65`) informa esas cifras
  y declara qué parte de los 87,2 s es lectura y qué parte es decisión, conforme a la declaración de los
  autores. **[script sin compuerta; prosa GATED OQ-05]**
- **D-05 (media). Propagación y trazabilidad.** Resumen y Abstract (`S/00-resumen.tex:11-13`, `:27-29`) y la
  Tabla 10 (`07:22`) dicen que el brazo manual midió solo la clasificación (no el registro) e informan el
  63,3 % sin telefonía; se corrige "cronometró en vivo el registro manual" (`04:16`); el Anexo I.1
  (`12:239-247`) registra el cambio de fechas (junio-agosto → octubre) y el del componente de carga; el Anexo
  I.2 (`12:251`) suma la devolución de quinta instancia (25/11/2026) y la de sexta (26/11/2026).
- **D-06 (baja). Coherencia y redacción.** Aclarar el cronometraje "por pares" "en el domicilio de cada
  analista" (`04:46`, `04:16`) **[GATED OQ-04]**; unificar Anexo F "redactadas por los autores"
  (`12:149`) con §4.4 "por uno de los autores" (`04:46`); en §8.1 reemplazar "respaldados por" (`07:38`, dos
  veces) por la fórmula de §4.5 (`04:66`: "respalda la existencia y la procedencia de los incidentes, no la
  medición de extremo a extremo"); en §7.5 corregir "titulares [...] distintos de los autores" (`11:46`),
  porque los autores también son reportantes; reemplazar "registro histórico/retirado" (`12:247`) por una
  forma sin barra.
- **Preparación de la defensa.** Respuestas escritas a las diez preguntas de la sección 6 (obligatorias la 1
  a la 4) en `docs/Tesis/Correcciones/respuestas-tribunal-sexta-instancia.md`, con alineación de
  `docs/defensa/respuestas-tribunal.md`.
- **Release `v1.6.6` (versión de defensa).** Patrón de c-250: commit de contenido (C3), commit del hash en el
  Anexo B (C4), tag anotado sobre C3, `compilacion.md`, Anexo I.1/I.2 actualizados, derivados regenerados,
  `CHANGES.md`, sección c-252 en `docs/Tesis/Correcciones/dictamen-correcciones.md`, y autoverificación
  estilo CONEAU antes del tag.

**Dependencia con c-251 (activo).** c-251 (`openspec/changes/c-251-corregir-los-errores-verificables-de-la-auditoria-gonzalo/`)
figura en `openspec list` con 0/23 tareas marcadas, pero su contenido **ya está aplicado en `main`**
(commits `a4437a1a`, `049eb353`, `f1854521`; la sección c-251 de `dictamen-correcciones.md` lo registra como
"APLICADO"): art. 28/2/11.3.e reformulados y fecha de notificación 2026-10-01 en `S/11-aspectos-legales.tex`,
retiro de la frase sobre la v1.6.0, dirección de la asimetría de alcance en `08:22`, etiqueta del −10 s en
el Anexo K (`12:354`) y en `04:16`, y la Figura 11 con la campaña manual en "oct" (01/10 a 31/10). Por eso:
(a) c-252 se aplica **sobre el estado aplicado de c-251** y conviene cerrar c-251 (marcar tareas y archivar)
antes del apply de c-252, para que el sync de specs no se cruce; (b) c-252 **no repite** nada de c-251;
(c) dos puntos de c-252 **retocan texto que introdujo c-251**: la frase del Anexo K "componente que la presente
versión ya no contempla" (`12:354`, D-02) y la barra de la Figura 11 que c-251 alineó a todo octubre
(D-01: debe acotarse al 09/10); (d) la Figura 11 y "junio-agosto → octubre" están parcialmente resueltos por
c-250/c-251 en el texto, pero falta la cota del 09/10 y su registro en I.1 (D-05).

**BREAKING (afirmaciones del método y, condicionalmente, de la cifra primaria):** la cronología de la campaña
manual pasa de "octubre de 2026" a una cronología día por día acotada por evidencia; si OQ-01 no sostiene el
orden manual → automatizado, cambian §4.2, la primera amenaza y la tercera explicación rival; si OQ-02 declara
que la carga se sumó, la cifra primaria de la sub-hipótesis 1 pasa de 71,2 % a 65,6 % y se propaga a Resumen,
Abstract, Tablas 10, 12 y 23, Discusión y Conclusiones.

Fuera de alcance: arquitectura, código (`App/`, `n8n/`), latencias del flujo automatizado, campaña
complementaria (E1, E2, O1, O2), balance neto (25,5 s-persona; +18,7 h-persona), sensibilidad del Anexo K
(salvo su redacción, D-02), casos del corpus y sus JSON (hashes protegidos), artefactos existentes de
`evaluation/` (solo se AGREGA un script con su prueba y su salida), los tags `v1.6.0` a `v1.6.5`, y todo lo
que c-251 ya aplicó.

**Gobernanza: MEDIUM** para la prosa y el script. **HIGH/CRITICAL** para el capítulo legal
(`11-aspectos-legales.tex`, art. 10), las declaraciones de procedencia y de cronología que solo pueden hacer
los autores (OQ-01 a OQ-05), el visto bueno del director y el grupo de release (OK expreso antes de cada
commit y del tag).

**Skills de dominio:** de `.agents/SKILLS.md` aplica `python-testing-patterns` (y `python-testing`) al script
de D-04; el resto del cambio es LaTeX y documentación.

## Capabilities

### New Capabilities

- `tesis-sexta-instancia`: requisitos que cierran D-01 a D-06 de la devolución de sexta instancia
  (cronología día por día acotada por evidencia, decisión registrada sobre el componente de carga, procedencia
  del régimen (a) sin rastros de versiones anteriores y con visto bueno del director, extensión de las
  descripciones por canal y régimen, propagación a Resumen/Abstract/Tabla 10 y trazabilidad en I.1/I.2,
  coherencia de redacción), las compuertas OQ-01 a OQ-05, las respuestas escritas a las diez preguntas y la
  autoverificación previa a la release.

### Modified Capabilities

- `tesis-reencuadre-cuarta-instancia`: se MODIFICAN dos requisitos de c-250 que la sexta instancia contradice
  en parte: "Cronología de la campaña manual en octubre 2026 referida al corpus vigente (C-01 de c-250)" (la
  fecha pasa a cronología día por día acotada por el commit del 09/10, y la Figura 11 deja de cubrir todo
  octubre) y "Componente "~10 s de carga del ticket" retirado (C-02 de c-250)" (la descripción del tiempo
  manual queda sujeta a la decisión OQ-02 registrada, con su nota en I.1, y la redacción del Anexo K deja de
  sugerir un cambio de valores).
- `tesis-document`: se AGREGA la trazabilidad de la release `v1.6.6` (versión de defensa tras la sexta
  instancia) en el texto del ejemplar.

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `S/00-resumen.tex`, `S/00-portada.tex` | Modificado | D-05 (clasificación, no registro; 63,3 % sin telefonía); versión `v1.6.6`; D-02 rama A si corresponde |
| `S/01-introduccion.tex` | Modificado | D-03 (`:16` "del sector servicios y con sede en [...] Mendoza") |
| `S/04-marco-metodologico.tex` | Modificado | D-01 (`:14`, `:46`, Tabla 4 `:78`, `:117`), D-02 (`:31`, `:89`, `:127`, `:131`), D-03 y D-04 (`:46`), D-05 (`:16`), D-06 (`:16`, `:46`) |
| `S/07-resultados.tex` | Modificado | D-04 (§8.1, Tabla 12), D-05 (Tabla 10), D-06 (`:38`), D-03 (`:277`, Tabla 18 `:255`) |
| `S/08-discusion.tex` | Modificado | D-01 rama B (tercera explicación rival, `:22`); D-02 rama A |
| `S/09-conclusiones.tex` | Modificado | D-03 (`:52`); D-02 rama A (Tabla 23) |
| `S/11-aspectos-legales.tex` | Modificado (HIGH) | D-03 (ámbito laboral, art. 10), D-06 (`:46`) |
| `S/12-anexos.tex`, `docs/diagrams/cronograma.md`, `paper/figures/cronograma.png` | Modificado | Figura 11 (D-01), Anexo F (D-06), I.1 (D-01, D-02, D-03, D-05), I.2 (D-05), Anexo K (D-02), Anexo B |
| `evaluation/data/campana/analisis/analisis_sexta_instancia_c252.{py,json,md,SHA256SUMS.txt}`, `test_analisis_sexta_instancia_c252.py` | Nuevo (aditivo) | D-04: extensión de descripciones por canal y régimen |
| `docs/Tesis/Correcciones/respuestas-tribunal-sexta-instancia.md`, `docs/defensa/respuestas-tribunal.md` | Nuevo / Modificado | Respuestas a las 10 preguntas de la sección 6 |
| `docs/Tesis/Correcciones/dictamen-correcciones.md`, `numeros-canonicos.md` | Aditivo | Sección c-252 (compuertas, ANTES/DESPUES, release); cifras de D-04 y, en rama A de OQ-02, nueva cifra primaria |
| `docs/Tesis/v10 (IA)/paper/main.pdf`, `compilacion.md`, derivados, `docs/Tesis/tesis_ultima_version.pdf`, `README.md`, `knowledge-base/`, `CHANGES.md` | Regenerado / Modificado | Release `v1.6.6` |
