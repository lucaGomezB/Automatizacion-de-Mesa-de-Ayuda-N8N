# Design: Declarar de forma completa el uso de asistentes de IA

## Context

Ver `proposal.md` - Why. Estado y restricciones que moldean el enfoque:

- Fuente: devolucion de tercera instancia (`auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md`): observacion **A-03** (L442-461), seccion 7 punto 5 (L688-689) y preguntas 11 y 12 de la seccion 8 (L726-729).
- Anclajes verificados en `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (v1.5.2): `\section{Trazabilidad de las correcciones de los dictamenes}\label{sec:anexo-trazabilidad}` en L231 (Anexo I); `\subsection{Nota de versiones}\label{subsec:nota-versiones}` en L233 (I.1, terreno de c-235); `\subsection{Revisiones que originaron las correcciones}` en L237 **sin `\label`** (I.2); parrafo de la declaracion vigente en **L241**; `\section{Numeros canonicos citados}` en L243 (Anexo J).
- Respuesta de defensa que repite la declaracion vieja: `docs/defensa/respuestas-tribunal.md` Q16 (L133-139); su actualizacion es de c-239.
- No existe requisito previo sobre la declaracion de asistencia de IA en `openspec/specs/tesis-document/spec.md` (busqueda por "asisten", "modelo de lenguaje", "Revisiones que originaron", "nota de versiones"); el mas cercano es "Atribucion de roles del equipo coherente con la autoria registrada en el repositorio" (L3985), que trata roles, no asistencia de IA, y no se modifica.
- No se encontro en el repositorio normativa de la facultad ni de la UTN sobre uso de IA en trabajos finales.
- Patron de scripts verificables en `docs/Tesis/Correcciones/` (`resumir_registro_compilacion.py` + `test_resumir_registro_compilacion.py`, `unittest`, ejecucion `python -m unittest` desde esa carpeta).

### Conteos recalculados (verificados al proponer, HEAD `88edd02`)

| Medida | Valor | Comando |
|---|---|---|
| Commits del historial | 1.173 | `git rev-list --count HEAD` |
| Commits con trailer de asistente (historial) | 154 | `git log --format='%H%x09%(trailers:key=Co-Authored-By,valueonly,separator=\|)' \| awk -F'\t' '$2!=""' \| wc -l` |
| Por modelo (historial) | Claude Fable 5.1: 65; Claude Fable 5.2: 41; Claude Fable 5: 35; Claude Opus 5.5: 11; Claude Sonnet 4.6: 2 | `git log --format='%(trailers:key=Co-Authored-By,valueonly)' \| grep -v '^$' \| sed 's/ *<.*//' \| sort \| uniq -c` |
| Rango `v1.2.18..v1.5.2` (version evaluada en tercera instancia) | 253 commits, 41 con trailer | `git rev-list --count v1.2.18..v1.5.2`; `git log v1.2.18..v1.5.2 --format='%(trailers:key=Co-Authored-By,valueonly,separator=\|)' \| grep -c .` |
| Desde 2026-11-11 (por fecha, incluye commits posteriores al tag) | 258 commits, 41 con trailer | `git rev-list --count --since=2026-11-11T00:00 HEAD` y analogo con trailer |
| Primer commit / primer commit con trailer | 2026-04-06 / 2026-05-21 | `git log --reverse --format=%ad --date=short` (con y sin `--grep='Co-Authored-By' -i`) |
| Identidades de autor distintas (sin nombrarlas) | 5 en el historial; 4 en `v1.2.18..v1.5.2` | `git log --format='%ae' \| sort -u \| wc -l` |
| Changes archivados / specs principales | 226 / 85 | `ls openspec/changes/archive`; `ls openspec/specs` |
| Changes archivados cuyo `tasks.md` nombra cada ambito (aprox., por `grep`) | `.tex`: 111; `App/`: 112; scripts de analisis/evaluacion: 135; `n8n/workflow`: 37 | `grep -l -E '<patron>' openspec/changes/archive/*/tasks.md \| wc -l` |

Los conteos coinciden con los del tribunal (41 de 253) y con los del brief (154 en todo el historial).

## Goals / Non-Goals

**Goals:**

- Un **inventario reproducible** del uso de asistentes, derivado solo del repositorio y regenerable con un comando.
- Una **declaracion completa** en el Anexo I, por ambitos, que no subdeclare ni sobredeclare, legible en una pagina.
- Una **compuerta de autores** explicita: los hechos que el repositorio no muestra (herramientas externas, verificacion efectiva, reparto del trabajo, normativa) los aportan T1, T2 y T3.
- Dejar el **texto fuente** para que c-239 actualice Q16.

**Non-Goals:**

- Medir la proporcion de texto o de codigo "escrita por IA" (no es medible desde el repositorio con fiabilidad; ver D2).
- Actualizar `respuestas-tribunal.md`, la matriz de trazabilidad, bump, recompilacion de cierre o tag (c-239).
- Tocar la nota de versiones I.1 (c-235) o el formato general de anexos (c-238).
- Cambiar cifras de resultado o numeros canonicos; tocar `App/`, `n8n/`, `evaluation/`, el corpus, `CHANGES.md` o `.engram/`.

## Decisions

### D1 — Inventario como documento de respaldo en `docs/Tesis/Correcciones/`

Archivo nuevo `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` con secciones fijas:

1. **Alcance y ref**: ref congelada sobre la que se cuenta (por defecto el tag `v1.5.2`; c-239 re-ejecuta sobre la ref de la release siguiente) y aclaracion de que no contiene nombres ni correos.
2. **Conteos de commits**: tabla por periodo (historial completo; `v1.2.18..v1.5.2`; y, si los autores lo piden, por tag) y por modelo, con y sin trailer, con el comando exacto que la genera.
3. **Artefactos de orquestacion de agentes**: `AGENTS.md`, `CLAUDE.md`, `CHANGES.md`, `.agents/` (skills vendorizadas y `SKILLS.md`), `.opencode/` (skills y comandos de flujo OPSX), `.engram/` (memoria persistente de agentes), `openspec/` (specs y changes), `knowledge-base/`, `docs/Tesis/Correcciones/Prompt2.docx` (perfil de evaluador para autoevaluaciones), con una linea sobre su funcion.
4. **Mapa de changes por ambito**: conteo de changes archivados cuyo `tasks.md` nombra cada ambito (codigo del sistema, scripts de analisis/evaluacion, prosa `.tex`, flujo N8N) y ejemplos verificables (p. ej. c-222, bloque "Prosa de la tesis").
5. **Respuestas de los autores** (compuerta, D5): por alias y fecha.
6. **Texto fuente de la declaracion** (para el `.tex` y para Q16 en c-239).

Alternativa descartada: volcar el inventario en el propio Anexo; se descarta por extension (el tribunal critica el registro de bitacora en M-03) y porque el anexo debe leerse en una pagina.

### D2 — El trailer es cota inferior, no medida de autoria

El trailer `Co-Authored-By` lo agrega la herramienta del asistente al commit cuando se usa ese flujo. Por eso:

- Un commit **con** trailer indica que un asistente participo en ese commit, no que haya producido todo su contenido.
- Un commit **sin** trailer no prueba que no hubo asistencia (sesiones con otras herramientas, commits manuales de trabajo asistido, periodo previo al 2026-05-21).
- El conteo se declara como **cota inferior de commits asistidos** y no se traduce a porcentaje de autoria del texto o del codigo. La declaracion dice que el flujo de trabajo fue asistido por agentes de forma sistematica cuando los autores lo confirmen (D5), en lugar de apoyarse solo en la proporcion de trailers.

Alternativa descartada: estimar lineas "escritas por IA" con `git blame` y trailers; se descarta porque mezcla autoria del commit con autoria del contenido y produciria una cifra con falsa precision.

### D3 — Script minimo `contar_uso_asistentes.py` con Strict TDD

Ubicacion `docs/Tesis/Correcciones/contar_uso_asistentes.py`, prueba `test_contar_uso_asistentes.py` (`unittest`, mismo estilo que `test_resumir_registro_compilacion.py`). Diseno por funciones puras, con el I/O de `git` aislado:

- `parsear_log(texto) -> list[Commit]`: recibe la salida de `git log --format='%H%x09%ad%x09%(trailers:key=Co-Authored-By,valueonly,separator=|)' --date=short` y devuelve hash, fecha y lista de co-autores (solo el nombre del asistente, sin correo).
- `contar(commits) -> Conteo`: total, con trailer, sin trailer y desglose por modelo.
- `clasificar_change(texto_tasks) -> set[str]`: ambitos (`codigo`, `analisis`, `prosa`, `n8n`) segun las rutas que nombra el `tasks.md` (patrones fijados en el script y en la prueba).
- `renderizar_markdown(...) -> str`: tablas para las secciones 2 y 4 del inventario.
- `main(--ref, --desde-ref, --archivo-changes, --salida)`: unica funcion que invoca `git` (via `subprocess`, sin `shell=True`) y lee el arbol.

Reglas: el script **no emite** `%an` ni `%ae` (privacidad); el filtro de trailer reconoce solo valores con nombre de asistente conocido y deja los demas co-autores en una categoria "otros co-autores" para no confundir co-autoria humana con asistencia. Pruebas minimas (al menos dos casos por comportamiento): log sin trailers; log con trailers de varios modelos; co-autor humano no contado como asistente; linea vacia o malformada; `tasks.md` con y sin rutas `.tex`; orden estable de la salida. Criterio de aceptacion: re-ejecutado sobre `v1.2.18..v1.5.2` da 253/41 y sobre el historial a `88edd02` da 1.173/154 (o el valor del dia, registrado con su ref).

Alternativa descartada: documentar solo los one-liners de shell; se descarta porque el tribunal recalcula y un script probado es mas auditable y re-ejecutable en c-239.

### D4 — Ubicacion: subseccion nueva I.3 con etiqueta

Se **retira** el parrafo de L241 de I.2 (que queda con su primer parrafo sobre las revisiones) y se agrega, tras I.2, `\subsection{Declaracion de uso de asistentes de inteligencia artificial}\label{subsec:declaracion-uso-ia}` (I.3). Razones: I.2 trata de las revisiones que originaron correcciones y mezcla dos temas; una subseccion propia es localizable desde el indice y citable por c-239 (Q16) con `\autoref`. Alternativa considerada: reescribir en el lugar dentro de I.2 (es lo que nombra literalmente el tribunal); se descarta porque el tribunal pide "reemplazar la declaracion", no conservar el titulo, y una subseccion propia lo hace visible. Si los autores prefieren conservarla en I.2 (OQ6), se reescribe en el lugar con el mismo contenido.

### D5 — Compuerta de autores (gobernanza ALTA)

El `.tex` **no se escribe** hasta que las respuestas de T1, T2 y T3 a las preguntas de "Open Questions" (OQ1-OQ5) esten registradas en la seccion 5 del inventario, con alias y fecha. Reglas de redaccion:

- Un procedimiento de verificacion figura en la declaracion solo si al menos un autor confirma haberlo aplicado y a que ambito.
- Si un ambito no tiene verificacion confirmada para todo su contenido, la declaracion lo dice (p. ej. "verificacion por muestreo" o "revision de lectura") en lugar de afirmar una verificacion exhaustiva.
- Los procedimientos candidatos que el repositorio respalda (a confirmar, no a afirmar): suite de pruebas del backend y de `evaluation/`; recalculo de cifras desde artefactos versionados y su registro en el memo `docs/Tesis/Correcciones/numeros-canonicos.md`; matriz de trazabilidad verificada por `verificar_matriz_trazabilidad.py`; `verify_citations.py` para la bibliografia; revision humana de cada change antes de archivarlo; recompilacion con `compilacion.md`.
- Ningun nombre real: solo T1, T2, T3 y P<n>.

### D6 — Contenido de la declaracion (estructura de una pagina)

Un parrafo de apertura, una tabla de cinco filas y un parrafo de cierre:

- **Apertura**: el desarrollo del sistema, el analisis y la redaccion se realizaron con asistencia sistematica de agentes de codigo basados en modelos de lenguaje, organizada en changes con especificacion previa; remision al inventario versionado (ruta) y a la ref de conteo; el conteo de commits con trailer como cota inferior (D2).
- **Tabla** (`ambito | herramienta y modelo | que produjo el asistente | verificacion de los autores`): (a) codigo del sistema (backend, frontend, flujo N8N); (b) scripts de analisis y evaluacion; (c) texto de la tesis (borradores de prosa a partir de tareas especificadas por los autores, no solo estilo); (d) diagramas; (e) autoevaluaciones estilo CONEAU (perfil `Prompt2.docx`; no son revision por pares).
- **Cierre**: que hicieron los autores sin asistencia (diseno metodologico, recoleccion de datos, decisiones de contenido; solo lo confirmado); responsabilidad final de los autores sobre cada cifra y afirmacion; adecuacion a la normativa (OQ4).

Sin fechas de sesion ni enumeracion de changes (registro de bitacora excluido); el detalle vive en el inventario. Limite: una pagina impresa del PDF.

### D7 — Borrador de la declaracion (a confirmar)

Borrador para la compuerta. Los corchetes `[CONFIRMAR: ...]` son huecos que solo los autores pueden llenar; no se trasladan al `.tex` sin respuesta.

> **Declaracion de uso de asistentes de inteligencia artificial.** El desarrollo del sistema, los scripts de analisis y la redaccion de esta tesis se realizaron con asistencia sistematica de agentes de codigo basados en modelos de lenguaje. El trabajo se organizo en cambios con especificacion previa (propuesta, diseno y tareas) que los autores definian y revisaban; el agente implementaba las tareas y los autores aceptaban o rechazaban el resultado. El inventario versionado `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` reproduce los conteos: en la version `v1.5.2`, 154 de 1.173 commits llevan la marca de co-autoria de un asistente, cifra que es una cota inferior porque la marca solo se registra con una de las herramientas. [CONFIRMAR: herramientas usadas fuera del repositorio.]
>
> | Ambito | Herramienta y modelo | Que produjo el asistente | Verificacion de los autores |
> |---|---|---|---|
> | Codigo del sistema | [CONFIRMAR: herramienta, p. ej. Claude Code y/o opencode]; modelos registrados en los trailers: Claude Fable 5, 5.1 y 5.2, Claude Opus 5.5, Claude Sonnet 4.6 [CONFIRMAR: otros modelos] | [CONFIRMAR] | [CONFIRMAR: pruebas automatizadas, revision de diff] |
> | Scripts de analisis y evaluacion | idem [CONFIRMAR] | [CONFIRMAR] | [CONFIRMAR: recalculo desde artefactos versionados, memo de numeros canonicos] |
> | Texto de la tesis | idem [CONFIRMAR] | borradores de prosa a partir de tareas definidas por los autores, ademas de estilo y edicion [CONFIRMAR] | [CONFIRMAR: revision humana de cada afirmacion, matriz de trazabilidad, `verify_citations.py`] |
> | Diagramas | [CONFIRMAR] | diagramas de flujo a partir de la estructura planteada por los autores | [CONFIRMAR] |
> | Autoevaluaciones estilo CONEAU | [CONFIRMAR: herramienta y modelo] con el perfil `Prompt2.docx` | informes de autoevaluacion; no son revision por pares | [CONFIRMAR] |
>
> El diseno metodologico, la recoleccion de datos, [CONFIRMAR: el resto] y las decisiones de contenido son de los autores, que asumen la responsabilidad final de cada cifra y cada afirmacion. [CONFIRMAR: normativa aplicable o declaracion de su ausencia.]

### D8 — Frontera con c-235, c-238 y c-239

- **c-235**: edita I.1 (`subsec:nota-versiones`) en el mismo archivo; c-237 solo toca I.2 (retiro de L241) y agrega I.3. Si c-235 se aplica antes, se repuntan lineas.
- **c-238**: formato y legibilidad de anexos (M-03, B-01, B-03). c-237 entrega I.3 ya en formato de una pagina y sin bitacora; c-238 puede ajustar estilo pero no contenido factual.
- **c-239**: actualiza Q16 con la seccion 6 del inventario, re-ejecuta `contar_uso_asistentes.py` sobre la ref de la release y actualiza las cifras de I.3 si cambian, recompila, matriz de trazabilidad, bump y tag.

### D9 — Cifras de la declaracion y memo de numeros canonicos

Los conteos de commits no son resultados de la investigacion; su fuente de verdad es el inventario (y el script). No se agrega seccion al memo `numeros-canonicos.md`. Alternativa considerada: registrarlos como numero canonico; se descarta porque cambian con cada commit y su vigencia se ancla a una ref, no a una corrida. Si c-239 decide citarlos en otra parte del cuerpo, decide alli.

### D10 — Gobernanza y verificacion

- Script e inventario: **BAJA** (solo lectura), Strict TDD (RED-GREEN-TRIANGULATE-REFACTOR) con evidencia en el resumen de apply.
- Declaracion en el `.tex`: **ALTA** (autoria); compuerta D5 obligatoria.
- Verificacion del `.tex`: busqueda textual de que el parrafo viejo ya no esta; `\label{subsec:declaracion-uso-ia}` unica; compilacion local de comprobacion (sin regenerar `compilacion.md`, que es de c-239) y verificacion de que I.3 no excede una pagina.

## Risks / Trade-offs

- [Subdeclaracion por inercia del texto viejo] → Requisito de coherencia con el inventario: cada ambito con evidencia en el repo debe figurar.
- [Sobredeclaracion de verificacion] → D5: solo procedimientos confirmados; los no exhaustivos se declaran como tales.
- [El trailer se lee como porcentaje de autoria] → D2: cota inferior, sin porcentaje.
- [Exposicion de identidades] → el script no emite autor ni correo; alias en el texto.
- [Las 4 identidades de autor del rango no se corresponden 1:1 con T1..T3] → OQ3: los autores aclaran el mapeo (sin publicarlo).
- [Respuestas de autores tardias] → la compuerta solo bloquea el `.tex`; inventario, script y borrador quedan listos.
- [Colision de lineas en `12-anexos.tex`] → D8.

## Migration Plan

1. Script y prueba (TDD) → inventario secciones 1-4.
2. Envio del cuestionario (OQ1-OQ6) a los autores; registro de respuestas (seccion 5).
3. Texto final (seccion 6) → edicion del `.tex` → verificacion.
Rollback: `git revert` del commit de contenido; archivos nuevos y una sustitucion textual.

## Open Questions

Preguntas para los autores (compuerta D5). Ninguna se responde por inferencia del agente.

- **OQ1 — Herramientas fuera del repositorio.** Cada autor (T1, T2, T3): ¿que asistentes de IA uso que el repositorio no registra (asistentes de chat, autocompletado en el editor, opencode con que modelos, herramientas de diagramas, traductores)? ¿Para que ambito (a)-(e) y en que periodo? ¿Con que herramienta y modelo se generaron las autoevaluaciones con `Prompt2.docx` y los diagramas de flujo?
- **OQ2 — Verificacion de cifras y afirmaciones.** Cada autor: ¿como verifico las cifras que el asistente escribio en la tesis (recalculo desde los artefactos versionados, comparacion con el memo de numeros canonicos, ejecucion de los scripts, muestreo)? ¿Como verifico las afirmaciones no numericas y las citas (lectura de la fuente, `verify_citations.py`)? ¿Reviso cada diff antes de aceptarlo o por muestreo? ¿Hubo partes aceptadas sin revision linea por linea?
- **OQ3 — Distribucion del trabajo en esta version (pregunta 12 del tribunal).** ¿Como se repartieron entre T1, T2 y T3 el codigo, el analisis, la redaccion y la verificacion entre `v1.2.18` y `v1.5.2`? ¿A que autor corresponde cada una de las 4 identidades de commit del rango (respuesta solo para el inventario, sin publicar correos)? ¿Quien opero las sesiones de agente?
- **OQ4 — Normativa aplicable.** ¿Existe una norma de la facultad (UTN-FRM) o de la UTN sobre uso de IA en trabajos finales? Consultarlo con los directores; si existe, citarla con su numero y fecha; si no existe, la declaracion lo dice asi y remite a la indicacion del tribunal.
- **OQ5 — Lo hecho sin asistencia.** ¿Que partes confirman los autores como realizadas sin asistente (diseno metodologico, recoleccion y etiquetado de datos, mediciones de tiempo, decisiones de contenido, otras)?
- **OQ6 — Ubicacion.** ¿Aceptan la subseccion nueva I.3 (D4) o prefieren reescribir en el lugar dentro de I.2?
