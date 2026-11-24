# Proposal: Aplicar las recomendaciones del dictamen sobre v1.6.3

## Why

El dictamen CONEAU del 2026-11-23 sobre `v1.6.3`
(`auditorias/Dictamen_Tesis_v10_v1.6.3_CONEAU_2026-11-23.md`) dicta **APROBADA CON
OBSERVACIONES** (8,19 ponderado; 8,38 proyectado con las recomendaciones necesarias 1 a 6). Las
tres aclaraciones de procedencia y la condicion de release del dictamen anterior quedaron
respondidas por c-247 y c-248, pero el dictamen senala siete observaciones nuevas, dos de ellas de
veracidad: el metodo describe como existente una planilla de cronometraje que los propios autores
declararon inexistente (`04:97` frente a OQ-02 (5) de c-247, `dictamen-correcciones.md:6913`), y
la titularidad del regimen (a) esta escrita con dos formulas distintas (`11:40` frente a `04:46`,
`11:16`, `11:48`) con tres tensiones del repositorio sin explicar. Suma una brecha legal sin
analizar (siete semanas de transferencias sobre un consentimiento verbal que el texto llama
"expreso", `11:30`), una regla de decision de la sub-hipotesis 2 distinta de la aplicada
(`01:34` frente a `07:184`), el reencuadre ausente del Resumen, del Abstract y de los capitulos 7
a 10, la lectura por regimen no escrita (`08:18`) y un texto de release desactualizado por el
movimiento del tag `v1.6.3` (`12:60`). Ninguna exige medir nada nuevo: todas exigen escribir lo
que el equipo ya sabe o ya registro. Es la ultima ronda antes de la defensa.

## What Changes

- **A. Recomendaciones necesarias de veracidad y licitud (1 a 3), bloqueadas por compuertas de
  autores.** Cada una depende de un hecho que solo los autores conocen; el agente MUST NOT
  inventarlo.
  - **OQ-01 (instrumento y protocolo del flujo manual; rec. 1 y 7):** que quedo de verdad del
    cronometraje de los 61,6 s (`04:97`), que se busco y que campos se completaron en "la busqueda
    y la carga del ticket" sobre una planilla (`04:89`), de donde salio la premisa de 2 min 45 s
    (coincide con los 165,3 s del corpus sintetico de julio, `12:237`) y la ventana "junio a
    agosto" de los 119 casos (`04:46`) como declaracion sin registro fechado. Lleva la falta de
    registro primario a la primera amenaza (`04:117`), a la fila del OE5 (`09:27`) y a `01:54`.
  - **OQ-02 (titularidad del regimen (a); rec. 2):** una sola formula de reportantes en `04:46`,
    `11:16`, `11:48` y `11:40`; si titulares y responsables del tratamiento son las mismas
    personas; que PII contenian los originales no versionados (`data/README.md:53`) frente a
    `11:24` y `12:151`; "se redactaron" (`04:46`) frente a "coinciden con el texto de origen"
    (`12:153`) y, segun la respuesta, la septima amenaza (`04:129`) extendida a los 200 casos;
    informacion de los empleadores reales; `01:72` acotado.
  - **OQ-03 (consentimiento y articulo 5; rec. 3):** "consentimiento expreso" pasa a
    "consentimiento verbal del 2-10-2026, confirmado por escrito el 20-11-2026", con la brecha
    analizada; transferencias ordenadas respecto del consentimiento y no de la notificacion;
    corridas entre el 21-09 y el 1-10 (`06:111`); constancia contemporanea del 2-10 o su
    inexistencia en lugar de "desliz de redaccion"; acta T2 §2 alineada con `11:30`.
- **B. Recomendaciones necesarias de rigor y propagacion (4 a 6).**
  - **Rec. 4 (gated OQ-04, ratificacion de veredictos):** sub-hipotesis 2 con la regla y el
    denominador prefijados (25/200) o con la regla enmendada y declarada post hoc; variable con un
    solo nombre; lectura con consenso de la sub-hipotesis 3 alineada con la disyuncion de `01:36`
    (`07:153`, `08:62`).
  - **Rec. 5 (sin compuerta salvo el Resumen, que respeta el tope de 250 palabras):** una oracion
    de escenario, composicion y laboratorio en Resumen y Abstract (`00r:11-13`, `:27-29`);
    "tarea de laboratorio" en `01:18`, `07:37`, `09:6`, `09:22`, `09:41`; `07:37` sin "sustituye";
    "1 USD trimestral" (`00r:15`, `:31`, `08:118`) y "32,2 horas-persona" (`08:72`) rotulados;
    `08:42`, `08:68`, `09:47`, `09:49` reescritos; `01:38` sin prometer un contraste inexistente;
    `04:46` y `04:54` sin extraer una muestra de un universo supuesto.
  - **Rec. 6 (sin compuerta, cifras recomputadas desde artefactos):** lectura por regimen en
    `08:18` (94/119 y 53/81 con Wilson), proporcion 81/200 y clausula declarativa en `08:50`,
    "un autor" unificado (registro de c-246 OQ-01), p95 de la corrida original del nivel 5 de N8N
    en `07:376`. Un script de analisis aditivo con su prueba produce las cifras.
- **C. Consistencia (rec. 7 a 12).** Release: `12:60`, enmienda de la tarea 6.3 archivada de
  c-248, encabezado "EN CURSO" de `dictamen-correcciones.md:7081`, `compilacion.md` con commit,
  Nota de versiones con `v1.6.2`, `v1.6.3` y el erratum, y regla escrita de movimiento de tags
  (gated OQ-05). Corpus: metadato declarado historico en el Anexo F (D4 (i) de c-247, ya
  decidida), parrafo de c-242 marcado como superado en `data/README.md`, Anexo F referenciado
  desde §4.4. Estado del arte (`03:8`, `:22`, `:24`, `:28`, `:47`, `:49`, `:90-92`), marco teorico
  (`02:20`, `:34`, `:46`, `:67`, `:100`, modelo economico, duplicados con el cap. 3), objetivos y
  trabajos futuros (`01:42`, OE2, `09:22`, `09:25`, `10:6`, `10:14`, `10:34`, `10:38`, linea por
  regimen) y observaciones del desarrollo sin medicion (`06:62`, `06:74`, `06:97`).
- **D. Forma (rec. 13 y 14).** Flotantes del Anexo F (`\FloatBarrier`), glosario sin celdas
  vacias, "F1 macro de umbral" definido en la hipotesis, p unilateral alineado con H1, tope de
  paginas (gated OQ-06), fecha de la Decision 2003/490/CE (DO L 168 de 5-07-2003, pp. 19-22),
  "s. f." en cuatro entradas de documentacion, referencia tecnica del modelo, cifra 1250/1251 del
  inventario de IA.
- **E. Release `v1.6.4`.** Recompilacion, derivados (`tesis_para_agente.md`, extractos, copia de
  entrega), patron C3/C4 segun la regla que fije OQ-05, tag anotado, merge a `main`,
  `CHANGES.md` y registro en `dictamen-correcciones.md`.

**BREAKING (afirmaciones del metodo y del capitulo legal):** el documento deja de describir la
planilla de cronometraje como instrumento existente y deja de llamar "expreso" al consentimiento
del 2-10; segun OQ-02, puede extender la coautoria de los datos a los 200 casos; segun OQ-04, el
veredicto escrito de la sub-hipotesis 2 cambia de rotulo.

Fuera de alcance: cifras canonicas (61,6 s, 17,76 s, 71,2 %, 73,5 %, W = 363, 0,6508, 25,47 s,
+18,7 h, 43,1 %, 898,8 s); casos del corpus y su JSON congelado (SHA-256 `1fd17d7e...`); `App/`,
`n8n/`; artefactos existentes de `evaluation/` (solo se AGREGA un script de analisis con su
prueba y su salida); mover, borrar o recrear `v1.6.2` o `v1.6.3`.

**Gobernanza: MEDIUM** (prosa de la tesis y documentacion; sin codigo de backend). Suben a **HIGH**
las tareas sobre `11-aspectos-legales.tex`, `docs/seguridad/` y `data/README.md` (texto mostrado a
los autores antes de escribir) y el grupo de release (toca el ejemplar defendido y publica un tag;
OK expreso de los autores antes de cada commit y del tag).

**Skills de dominio:** el cambio es de LaTeX y documentacion; de `.agents/SKILLS.md` solo aplica
`python-testing-patterns` al script de analisis por regimen (grupo 4). Las demas
(`sqlalchemy-postgres`, `tailwind-design-system`, `python-design-patterns`, `pytest-coverage`) no
corresponden.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tesis-reencuadre-cuarta-instancia`: se AGREGAN requisitos que cierran los residuos del dictamen
  sobre `v1.6.3`: instrumento del flujo manual veraz (OQ-01), titularidad unica del regimen (a) y
  tensiones del repositorio explicadas (OQ-02), brecha del articulo 5 analizada (OQ-03), reglas de
  decision de las sub-hipotesis aplicadas como se enuncian (OQ-04), reencuadre completo en Resumen,
  Abstract y capitulos 7 a 10, lectura por regimen escrita con cifras recomputadas, consistencia
  de los capitulos 2, 3, 6 y 10, forma, y registro de compuertas de c-249.
- `tesis-document`: se AGREGAN el requisito de la regla escrita de movimiento de tags (OQ-05) y el
  de la trazabilidad de la release `v1.6.4` en el texto del ejemplar (`12:60`, Nota de versiones,
  `compilacion.md`, registro de c-248 enmendado).

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `docs/Tesis/v10 (IA)/paper/sections/00-resumen.tex`, `00-glosario.tex`, `00-portada.tex` | Modificado | Reencuadre del Resumen y del Abstract, glosario, fecha y version |
| `.../sections/01-introduccion.tex`, `02-marco-teorico.tex`, `03-estado-del-arte.tex` | Modificado | Hipotesis, objetivos, `01:72`, marco del modelo economico, fichas y criterio temporal |
| `.../sections/04-marco-metodologico.tex` | Modificado (gated OQ-01, OQ-02) | Instrumento, carga del ticket, titularidad, poblacion y muestra, amenazas |
| `.../sections/06-implementacion.tex`, `07-resultados.tex` | Modificado | Observaciones sin medicion, `07:37`, sub-hipotesis 2 y 3, nivel 5 de N8N |
| `.../sections/08-discusion.tex`, `09-conclusiones.tex`, `10-recomendaciones.tex` | Modificado | Lectura por regimen, rotulos, filas OG/OE3/OE5, subseccion del costo de reasignacion |
| `.../sections/11-aspectos-legales.tex` | Modificado (HIGH, gated OQ-02, OQ-03) | Titularidad, empleadores, consentimiento verbal y articulo 5 |
| `.../sections/12-anexos.tex`, `Bibliography_base.bib` | Modificado | Anexo B (`12:60`), Anexo F, Nota de versiones, inventario de IA, bibliografia |
| `docs/seguridad/acta-consentimiento-t2.md` | Modificado (HIGH, gated OQ-03) | Vocabulario de §2 alineado con `11:30` |
| `data/README.md` | Modificado (HIGH, gated OQ-02) | PII de los originales; parrafo de c-242 marcado como superado |
| `evaluation/data/campana/analisis/analisis_regimen_c249.{py,json,md,SHA256SUMS.txt}`, `test_analisis_regimen_c249.py` | Nuevo (aditivo) | Recomputo de la exactitud por regimen, sub-hipotesis 2 y p95 del nivel 5 |
| `docs/Tesis/Correcciones/respuestas-tribunal-cuarta-instancia.md` | Modificado | Respuestas alineadas con `11:30` y con la titularidad |
| `openspec/changes/archive/2026-11-22-c-248-.../tasks.md` | Enmienda aditiva | Nota sobre la tarea 6.3 (estado final del tag) |
| `docs/Tesis/v10 (IA)/paper/main.pdf`, `compilacion.md`, `tesis_para_agente.md`, `tesis_*.txt`, `docs/Tesis/tesis_ultima_version.pdf` | Regenerado | Release `v1.6.4` |
| `README.md`, `knowledge-base/`, `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md`, `CHANGES.md` | Modificado | Propagacion de la version y registro del change |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo (+ encabezado de c-248) | Seccion c-249: compuertas, ANTES/DESPUES, release |
