# Proposal: Atender las observaciones de la quinta instancia del tribunal

## Why

El dictamen de quinta instancia sobre `v1.6.4` (
`auditorias/Devolucion_Quinta_Instancia_TFI_v1.6.4_2026-11-25.md`, 2026-11-25) dicta **APTA PARA DEFENSA**, 7,3/10
(proyectada 7,5 con C-01 a C-04 resueltas). Es la quinta devolución escrita del tribunal y la
**última ronda antes de fijar fecha de defensa**. La v1.6.4 aplicó el reencuadre autorizado (R-01 a
R-07 y B-01 quedan corregidas), pero el propio reencuadre puso a la vista siete observaciones
nuevas (C-01 a C-07), tres de prioridad alta que afectan la línea base manual de la sub-hipótesis 1,
la única que el trabajo corrobora: la cronología de la campaña manual (C-01), el componente estimado
de la carga del ticket (~10 s) que no existe en los datos (C-02) y la asimetría de entrada por brazo
en telefonía (C-03). Las cinco compuertas de autores (OQ-01 a OQ-05) ya fueron **respondidas** por el
equipo: no queda ningún hecho pendiente de confirmar. Ninguna observación exige medir nada nuevo ni
cambiar el código: todas exigen escribir con honestidad lo que el equipo ya resolvió, recomputar
cifras derivables de artefactos versionados y corregir el reencuadre de procedencia. La condición
para fijar fecha es el visto bueno escrito del director; la versión de defensa debe incorporar C-01 a
C-04, y C-01 se resuelve con la evidencia fechada de la campaña de octubre (commits `68d06ec` /
`ea62576`), que acredita la procedencia de los 200 casos vigentes.

## What Changes

Se producen siete correcciones, cada una con su pasaje exacto (referencias `archivo:línea` sobre las
fuentes `.tex` de `main`; los números de línea son los de la v1.6.4 y el apply los re-verifica):

- **C-01 (alta). Cronología de la campaña manual, propagada al corpus vigente (200 casos).** La
  clasificación manual del corpus **real** ocurrió en **OCTUBRE 2026**, no en junio–agosto. La ventana
  "junio a agosto" del texto actual (`04:14`, `04:46`, Tabla 4 `04:78`; `01:16`) es un artefacto de la
  era sintética y debe reemplazarse por **octubre 2026** (corpus real). Evidencia fechada: commit
  `68d06ec` (2026-06-11) versiona el corpus **sintético**; commit `ea62576` (2026-10-09) versiona el
  corpus **real**. La declaración honesta ("declaración de los autores sin registro fechado") se
  conserva; cae "junio–agosto". El número sintético 165,3 s del 3 de julio queda solo en la Nota de
  versiones como histórico. **[Resuelto por los autores: la campaña del corpus vigente es octubre 2026;
  el sintético de junio–julio es histórico].**
- **C-02 (alta). Componente "~10 s de carga del ticket" REMOVIDO, no declarado.** El "~10 s de carga
  del ticket estimada" es una **fabricación**: no aparece en los datos. Evidencia:
  `data/corpus_evaluacion_pseudonimizado.json` dice que los tiempos manuales corresponden a la
  **clasificación manual**; `docs/anexo_f_corpus.md:99` define `tiempo_manual_s` = "Tiempo de
  **clasificación manual**"; el CSV solo tiene "Tiempo de Registro Manual (segundos)", sin columna de
  carga. El tiempo manual es **clasificación manual (lectura + decisión de sector)**, no E2E, sin
  componente de carga. Se retira "carga ~10 s" de `04:89`, `04:131` (octava amenaza), `12:153`,
  `07-resultados.tex:285`, `01:18`, Resumen, Abstract, Tabla 10 y Tabla 23, y `data/README.md`. Se da
  una definición operacional **por brazo** en Tabla 3 (`04:31`): manual = clasificación (lectura +
  decisión), automatizado = E2E (recepción → persistencia). **Matiz que el apply NO debe malinterpretar:**
  el Anexo K (`12-anexos.tex:351,353,367`) ya computa −10 s → 51,6 s / 65,6 % como una **sensibilidad de
  redondeo** (los valores se redondearon ARRIBA a múltiplos de 5 s); esa sensibilidad es legítima y
  PERMANECE como tal, no es "quitar el componente de carga" (la carga nunca existió).
- **C-03 (alta). En telefonía cada brazo procesó una entrada distinta.** Sin cambio de fondo, con
  encuadre actualizado. Ver C-03 de design; las cifras ya estaban resueltas. Informar mediana Y media
  de las 81 grabaciones (`duracion_segundos`: mediana 7,0 s / media 7,26 s; el `t_e2e_s` mediana 18,7 s
  es grabación+procesamiento, no confundir); informar la sub-hipótesis 1 también **sin telefonía**
  (correo+formulario ≈44,1 s → ≈16,2 s, ≈63,3 %, recomputado por pares con intervalos). Con el ~10 s
  removido, el 87,2 s manual es clasificación pura y el 20,09 s automatizado es E2E: la asimetría es
  aún más fundamental (distinto alcance Y distinta entrada). Script TDD (como `analisis_regimen_c249.py`).
- **C-04 (media). Unificar el estado del registro primario.** Reescribir `07-resultados.tex:38` a: 81
  telefónicos respaldados por `corpus_resultados_telefonia.json`; 119 correo/formulario respaldados
  por `corpus_resultados_web_correo.json` = 118/119, `R001` el único caso sin registro. Alinear con
  `04:66`, `04:79`, `12-anexos.tex:149`, `data/README.md:40-47`. Sin cambio de datos.
- **C-05 (media). Separar consentimiento de colaboradores del de titulares; licitud por disociación
  (arts. 2 y 28).** El corpus fue SIEMPRE genérico ("sistema principal"/"sistema secundario"), sin
  nombres de sistema ni ID USUARIO. Se RETIRA la afirmación "los originales no versionados contenían
  los nombres reales de sus sistemas + ID USUARIO" (`11:18`, `data/README.md:55-63`): no hay
  originales con identificadores, ni custodio ni fecha de destrucción que declarar. Se separa el
  consentimiento de los colaboradores (autores + A1) del de los TITULARES (los reportantes del
  círculo). Se retira "los titulares de los datos y los responsables del tratamiento son las mismas
  personas" (`11:46`). La licitud se funda en la DISOCIACIÓN citando arts. **2 Y 28** (art. 28 es
  adición neta; hoy solo art. 2 en `11:12`). La notificación a los integrantes del grupo fue **verbal
  el 2026-09-30** (corrige el 2026-10-01 actual), comunicando el uso pseudonimizado y disociado de sus
  incidentes.
- **C-06 (media). Originales de empleadores: DISUELTO, reencuadre de procedencia.** El origen real es
  **familiares y amigos (el círculo)**, no los empleadores de los autores. Se RETIRA "los empleadores
  reales de los autores" y "no se requirió autorización de esas organizaciones" (`11:18`). No hay
  empleador, por lo tanto NO se necesita el aval escrito del director (la afirmación que respaldaba se
  retiró). Se AGREGA el deber de confidencialidad (**art. 10**, Ley 25.326) a los principios generales
  (hoy solo la tríada CIA en `11:40`).
- **C-07 (baja). Coherencia y redacción.** Agregar fila a la Tabla 26 (`12:257-277`): redacción del
  corpus → **"sin IA"** (no se usó IA en las 119 descripciones). Corregir I.3 `12:279`: el etiquetado
  lo hicieron A1/T1/E1/E2, no "de los autores". Unificar "por los autores" (I.1 `12:241`) / "por ese
  autor" (`04:46`) / "uno de ellos" (`09:25`). Agregar "Gemini 3.1" en §7.5 (`11:54`) para la
  validación retirada (hoy solo en I.1 `12:243`). Dejar "dispositivo de dimensionamiento y no el lugar
  de recolección" una sola vez (hoy 8×). Retirar "corpus propio de la organización" (`09:48`).
  Aclarar "en su domicilio" (`04:46`).

**Procedencia (reencuadre, nuevo, conforme a C-06 y C-01).** El régimen (a) de procedencia pasa de
"los integrantes del entorno operativo del propio equipo, los autores y las personas de su círculo" a
"los autores y las personas de su círculo (**familiares y amigos**)". Se retira "integrantes del
entorno operativo del propio equipo" de toda mención de procedencia (`01:16`, `01:48`, `01:72`,
`04:46`, `08:22`, `08:42`, `08:50`, `09:52`, `11:16`, `11:46`, `11:54`, Resumen). Se CONSERVA: (a) el
escenario FICTICIO "organización mediana del sector servicios / 120 usuarios / 42 diarios" (es el
dispositivo de dimensionamiento, explícitamente no-real, establecido por R-01); (b) "organización
adoptante" (despliegue futuro). El reencuadre se registra en la Nota de versiones como una corrección
de veracidad (como R-01 a R-07), con el mismo estilo de declaración honesta.

**Release.** Este change produce la **versión de defensa**: `v1.6.4` → `v1.6.5`, siguiendo el
procedimiento de release de c-249 (commit de contenido, commit hash-en-Anexo-B, tag anotado,
recompilación + derivados, `CHANGES.md`, `README.md`, `knowledge-base/`,
`docs/Tesis/Correcciones/dictamen-correcciones.md` con sección c-250, y las respuestas de defensa).
Al no existir ya la necesidad del aval del director por C-06, NO se requiere esa gestión: la versión
de defensa avanza con el visto bueno escrito del director (condición del tribunal), sin tarea de aval.

**BREAKING (afirmaciones del método, del capítulo legal y de las conclusiones):** la tesis deja de
presentar el 3 de julio (165,3 s) como base de medición (histórico en Nota de versiones) y fecha la
campaña real en octubre 2026; los tiempos manuales dejan de llevar el componente "~10 s" (se declaran
clasificación manual pura); la reducción del 71,2 % deja de presentarse sin su lectura sin telefonía
y sin componente de carga; el capítulo legal separa el consentimiento de colaboradores del de
titulares, funda la licitud en la disociación (arts. 2 y 28) con deber de confidencialidad (art. 10),
y retira la referencia a empleadores reales en favor de la procedencia del círculo (familiares y
amigos).

Fuera de alcance: cifras canónicas (61,6 s, 17,76 s, 71,2 %, 73,5 %, W = 363, 0,6508, 87,2 s,
20,09 s, 77,0 %, etc.); casos del corpus y sus JSON congelados (SHA-256 `1fd17d7e...`); `App/`,
`n8n/`; artefactos existentes de `evaluation/` (solo se AGREGA un script de análisis con su prueba y
su salida); mover, borrar o recrear tags `v1.6.2`, `v1.6.3` ni `v1.6.4`.

**Gobernanza: MEDIUM** (prosa de la tesis y documentación; sin código de backend). Sube a **HIGH** el
capítulo legal (`11-aspectos-legales.tex`, C-05 y C-06), `docs/seguridad/`, `data/README.md` y el
grupo de release (toca el ejemplar defendido y publica un tag; OK expreso de los autores antes de
cada commit y del tag).

**Skills de dominio:** el cambio es de LaTeX y documentación; de `.agents/SKILLS.md` solo aplica
`python-testing-patterns` al script de recomputo por pares (C-03). Las demás no corresponden.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tesis-reencuadre-cuarta-instancia`: se AGREGAN requisitos que cierran las observaciones C-01 a
  C-07 de la quinta instancia: cronología de la campaña manual en octubre 2026 referida al corpus
  vigente (C-01), retiro del componente "~10 s" de carga (C-02), asimetría telefónica por brazo y
  sub-hipótesis 1 sin telefonía (C-03), estado unificado del registro primario (C-04), consentimiento
  de colaboradores vs. titulares y licitud por disociación (arts. 2 y 28) sin originales con
  identificadores (C-05), disolución de los "empleadores reales" con deber de confidencialidad
  (art. 10) y reencuadre de procedencia al círculo (C-06), y coherencia/redacción con fila "sin IA"
  (C-07).
- `tesis-document`: se AGREGA el requisito de la trazabilidad de la release `v1.6.5` en el texto del
  ejemplar (bump de versión, Anexo B, Nota de versiones, `compilacion.md`, hash consignado, tag
  anotado) y el registro de la versión de defensa.

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `docs/Tesis/v10 (IA)/paper/sections/00-resumen.tex`, `00-portada.tex` | Modificado | Retiro del componente de carga en Resumen/Abstract; procedencia del círculo; versión `v1.6.5` |
| `.../sections/01-introduccion.tex` | Modificado | §1.2 (C-02), §1.6 procedencia (C-06), sub-hipótesis 1 (C-03) |
| `.../sections/04-marco-metodologico.tex` | Modificado | §4.2/§4.4/§4.5/§4.8, Tabla 3, Tabla 4 (C-01, C-02, C-06, C-07) |
| `.../sections/07-resultados.tex` | Modificado | §8.1, Tabla 10, Tabla 12 (C-02, C-03, C-04) |
| `.../sections/08-discusion.tex` | Modificado | Procedencia (§8.2, §8.4, §8.5), lectura sin telefonía |
| `.../sections/09-conclusiones.tex` | Modificado | Tabla 23, "corpus propio de la organización", "uno de ellos", procedencia |
| `.../sections/11-aspectos-legales.tex` | Modificado (HIGH) | C-05, C-06 (arts. 2, 28, 10; sin originales; sin empleadores) |
| `.../sections/12-anexos.tex` | Modificado | Anexo K (sensibilidad de redondeo se conserva), Tabla 26, I.1, I.3, Nota de versiones |
| `data/README.md` | Modificado (HIGH) | Sin originales con identificadores; estado del registro (C-04, C-05) |
| `evaluation/data/campana/analisis/analisis_quinta_instancia_c250.{py,json,md,SHA256SUMS.txt}`, `test_analisis_quinta_instancia_c250.py` | Nuevo (aditivo) | Recomputo por pares sin telefonía (C-03) |
| `docs/Tesis/Correcciones/respuestas-tribunal-cuarta-instancia.md`, `docs/defensa/respuestas-tribunal.md` | Modificado | Respuestas a las 10 preguntas probables del tribunal, si las tocan |
| `docs/Tesis/v10 (IA)/paper/main.pdf`, `compilacion.md`, `tesis_para_agente.md`, `tesis_*.txt`, extractos, `docs/Tesis/tesis_ultima_version.pdf` | Regenerado | Release `v1.6.5` (versión de defensa) |
| `README.md`, `knowledge-base/`, `CHANGES.md` | Modificado | Propagación de la versión y registro del change |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Sección c-250: decisiones OQ-01 a OQ-05 resueltas, ANTES/DESPUES, release |