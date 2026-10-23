## Context

Ver `proposal.md` (Why). Este change cierra la FASE 36: integra los doce changes que atienden el dictamen CONEAU del 2026-10-22 sobre la tesis v10 / `v1.1.0` (`auditorias/Dictamen_Tesis_v10_v1.1.0_CONEAU_2026-10-22.md`): c-125..c-135 y c-137. Verifica el documento resultante, traza cada recomendacion (A1-A5 y B4-B16) y publica la release. Gobernanza: **MEDIUM** (tag, push y PR; coordinacion con el equipo), con dos checkpoints de nivel **HIGH**: la compactacion de la rama (a) (dominio "eliminacion de contenido", precedente c-116) y la publicacion del tag y del PR (acciones publicas).

Estado verificado (solo lectura, 2026-10-22/23):

- **Dictamen (revision vigente).** El archivo se reviso durante la planificacion. Ahora tiene cinco observaciones de fondo: A5 pide declarar la procedencia real de los ajustes del clasificador (vocabulario de c-71, reglas de frontera del prompt de c-72, tau de c-74, todos ajustados con el corpus de evaluacion) y agregar un analisis de sensibilidad fuera de muestra. Suma la seccion "Verificacion contra el historial del repositorio", con dos hallazgos sin numero de recomendacion: la version del modelo fechada en "junio de 2026" frente a su integracion el 24-09-2026 (commit `11036be`), y el `timeout` de 10 s de la tesis y del Anexo H frente a los 30 s del backend. La rubrica baja el criterio 4 a 7 y el 6 a 6,5 (ponderado 7,67; nota 8). B14 advierte que `acentuar_tesis.py` y `acentuar_tesis_v9.py` originaron erratas y no deben reaplicarse sin depurar su diccionario.
- **Release y tags.** Release vigente `v1.1.1`. Tags anotados y publicados en `origin`: `v1.0.0` -> `61a6b117dd1321fbee25f9792d9f29b884e5ac8d`, `v1.0.1` -> `bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0`, `v1.1.0` -> `7103b649d8c4f51737ad6ad4095dad22c9406400`, `v1.1.1` -> `4160d84286623b073d2904353e6f9163ae211de7`. No existe `v1.2.0` ni local ni remoto. El patron C1/C2 se observa en los commits de c-123: C1 (`4160d84`) cambia el tag en el Anexo B y retira la linea del hash anterior; C2 (`e18b9c4`) agrega la linea con el hash nuevo y la nota en `dictamen-correcciones.md`. Ambos incluyen el PDF recompilado. Las releases previas se etiquetaron en `ramagonzalo` y se integraron a `main` con merge commit (PR #36).
- **PDF.** `paper/main.pdf` = 101 paginas (conteo de saltos de pagina con `pdftotext`). Distribucion: preliminares pp. 1-10 (glosario en p. 10), capitulos 1-11 pp. 11-87 (77 paginas), referencias pp. 88-93 (6 paginas para 59 entradas, unas 0,1 paginas por entrada), anexos pp. 94-101 (8 paginas; el Anexo I ocupa la p. 101). Cuerpo sin anexos: 93 paginas. Preambulo: `article` 11pt A4, margenes de 2,54 cm, `fontspec` con Arial y Courier New, `\doublespacing` (`setspace`) en el texto y flotantes a espacio simple, `biblatex` APA con biber. Cada capitulo empieza en pagina nueva y, segun las mediciones de c-127, c-128, c-131 y c-133, las ultimas paginas de los capitulos 1, 3, 9, 10 y 11 estan llenas: un desborde pequeno en esos capitulos cuesta una pagina entera. Hay 10 entornos `figure` y todos los `\includegraphics` resuelven (las ocho figuras de c-80 siguen presentes).
- **Registro de compilacion.** `main.blg` (Biber 2.22): 59 citekeys, 0 WARN. `main.log` no se versiona (`.gitignore`: `*.log`), como observo el dictamen. En esta maquina no hay `xelatex`, `biber`, `latexmk` ni `pdfinfo` en el PATH, Docker esta instalado pero sin la imagen `texlive-thesis`, `pandoc` no esta instalado y `pdftotext` 4.06 si. La recompilacion de v9 del 2026-10-20 uso MiKTeX (xelatex -> biber -> xelatex -> xelatex). Los comentarios de `paper/Dockerfile` aun citan rutas de v9; `OVERLEAF_INSTRUCTIONS.md` sugiere un reemplazo de Arial que altera la paginacion.
- **Anexos B, H e I.** `12-anexos.tex:17-23` (`sec:anexo-repositorio`): tag `v1.1.1` en la linea 19, hash en la linea 21. `12-anexos.tex:135` (Anexo H): afirmacion de prompt ajustado "sin exposicion al corpus" (A5) y remision a un historial del prompt inexistente. `12-anexos.tex:141-143` (`sec:anexo-trazabilidad`): un parrafo que remite al registro, sin mapeo por recomendacion.
- **Registro.** `docs/Tesis/Correcciones/dictamen-correcciones.md` tiene en "## Notas" las lineas de trazabilidad de `v1.0.0`, `v1.1.0` y `v1.1.1` y tablas de cobertura con formato `| Codigo | Hallazgo | Change |`; no tiene seccion para el dictamen v10 / `v1.1.0`.
- **Bibliografia.** `Bibliography_base.bib:613-619`, `Gomez2026_repositorio`, titulo `(Version 1.1.1)`. B16 pide mantenerla sincronizada con la release que finalmente se entregue; c-134 declara que no toca esa version y c-132 puede acentuar la etiqueta "Version" del titulo por decision registrada.
- **Renders.** `tesis_para_agente.md` se genero en `eed23a0` (16:56), antes de c-123 (19:34): no refleja la URL ni el tag `v1.1.1` del Anexo B. `build_tesis_para_agente.py` corre desde la raiz, escribe a stdout, tiene el orden de secciones cableado (15 archivos, en el orden de `main.tex`) y su encabezado declara "(v10 / v1.1.0)". `tesis_completa_extraida.txt` y `tesis_para_evaluacion.txt` provienen de la copia de v9 (`8466cbe`, 2026-10-01): texto sin tildes y con un solo director; no hay script generador en el repositorio. `paper/tesis.docx` se genera con pandoc 3.8 y `add_disclaimer.py`, y tambien es de la era v9. `openspec/config.yaml` apunta `thesis:` a `docs/Tesis/v10 (IA)/tesis_para_agente.md`, que existe.
- **Base de conocimiento.** `knowledge-base/11_evaluacion_experimental.md` dice que "los numeros definitivos se re-miden" y su linea 12 repite la afirmacion que A5 refuta ("keywords y prompt se construyeron SIN acceso al corpus de validacion; la evaluacion ... es estrictamente held-out"). `knowledge-base/README.md` cita la ruta `docs/Tesis/tesis_para_agente.md`, "Gemini 2.5 Flash" (la tesis usa `gemini-3.6-flash`) y los resultados del corpus sintetico como superados, sin los resultados reales. Ningun change de la familia corrige la KB. Ultimo commit de la KB: 2026-10-13.
- **Evaluacion.** `evaluation/run_evaluation.py:249-274` genera la seccion "Normalidad (Shapiro-Wilk)" de `evaluation/report.md` desde c-99: la advertencia de `CHANGES.md` de que regenerar el reporte la borra quedo superada. El reporte ya trae el Wilcoxon intra-canal. `evaluation/predicciones.json` esta en `.gitignore` y no existe en el arbol (dependencia de c-126 y de c-137). Con `core.autocrlf=true` (esta maquina), `sha256sum` del archivo de trabajo `data/corpus_evaluacion_pseudonimizado.json` da `7408cd2a...`; la huella canonica `1fd17d7e...` corresponde al contenido versionado con fin de linea LF (`git show HEAD:data/corpus_evaluacion_pseudonimizado.json | sha256sum`), lo que c-129 (D6) corrige en el calculo del reporte.
- **Historia del tope de paginas.** Cuatro reglas distintas: `docs/cumplimiento/plan-cambios-cumplimiento.md` §1.1, "el cuerpo no puede superar las 100 paginas; los anexos no cuentan"; c-116, total <= 100 (confirmado por el autor el 2026-10-21); c-118, "cuerpo 93 pp, total 101 paginas (gate cumplido bajo la regla del plan §1.1, confirmada por el autor)"; c-120..c-123, total <= 101 como criterio duro. El spec principal (`Presupuesto de páginas preservado`) sigue diciendo 100 sobre el total, en contradiccion con las 101 actuales. El requisito `Thesis PDF compilation` sigue apuntando a `docs/Tesis/v8 (IA)`.
- **Familia.** c-125..c-135 y c-137 tienen artefactos escritos en paralelo (c-126 con 81 tareas, que incluyen McNemar en su bloque 7; c-137 con 91). D1 y D3 se reconciliaron con lo que ya declaran (orden, propiedad de parrafos e impacto en paginas); lo que falte se reconcilia al integrar (D7, P2).
- **Partes interesadas:** autores (Gomez, Bustos, Sevilla), directores, jurado (reexamen previo a la defensa) y Luca, que trabaja en `main` y `RamaLuca` mientras este flujo corre en `ramagonzalo`.

## Goals / Non-Goals

**Goals:**

- Una sola version integrada, compilada, verificada y etiquetada (`v1.2.0`) que cierre A1-A5 y B4-B16 con trazabilidad auditable de extremo a extremo.
- Una regla unica de tope de paginas, decidida al inicio de la familia y cumplida al cierre.
- Un orden de aplicacion de la familia que resuelva los conflictos de archivos compartidos y los desacuerdos de orden entre los changes.
- Renders, base de conocimiento y punteros coherentes con la release.

**Non-Goals:**

- No reescribir el contenido sustantivo de c-125..c-137. Si una verificacion falla, se devuelve al change dueno; este change no parcha contenido ajeno, salvo la compactacion de forma de la rama (a) y las erratas de la pasada corta.
- No realizar mediciones nuevas ni re-ejecutar el clasificador, N8N o Gemini (la prueba de humo de c-135 se re-ejecuta solo si c-135 se aplico, porque c-135 lo pide como interfaz con la release; la corrida paga opcional es de c-137).
- No agregar figuras ni tablas de contenido; la unica tabla nueva posible es el mapeo compacto del Anexo I.
- No mover ni recrear `v1.0.0`, `v1.0.1`, `v1.1.0` ni `v1.1.1`.
- No tocar `App/`, `n8n/`, el codigo de `evaluation/`, `data/`, `auditorias/` ni `docs/Tesis/v9 (IA)/`.
- No versionar `main.log` (ver D6).
- No corregir la descripcion del stack en `openspec/config.yaml` ("Gemini 2.5 Flash") ni `knowledge-base/10_preguntas_abiertas.md` (menciones a v7/v8): se anotan como observaciones fuera de alcance.

## Decisions

### D1 - Orden de aplicacion de la familia y resolucion de archivos compartidos

Aplicacion estrictamente secuencial en `ramagonzalo`, un change por vez, cada uno sobre el resultado del anterior. El orden reconcilia la sugerencia del orquestador con lo que declaran los `design.md` de la familia:

| # | Change | Recomendaciones | Archivos principales | Debe ir despues de | Motivo de la posicion |
|---|---|---|---|---|---|
| 0 | c-136, grupo 1 (G0) | Decisiones bloqueantes | `dictamen-correcciones.md` | - | Tope, entorno, c-135, checkpoints de c-137, nombre de release y libro mayor antes de editar la tesis |
| 1 | c-125 | A1; A5a (mitad declarativa, su D9) | 02, 05 (:78), 06 (:75), 07, 08 (:16, :18), 11 (:34), 12 (:135, primera oracion) | G0 | Fija la "confianza" de la etapa determinista, el alcance real del gate y la procedencia declarada de los ajustes; precede a c-126, c-127, c-128, c-131 y c-137 |
| 2 | c-129, bloque de codigo (sus tareas 1 a 5) | B7a (base), B12 (base) | `evaluation/stats.py`, `run_evaluation.py`, pruebas | c-125 | c-129 D6/D12: la huella del corpus independiente del fin de linea debe existir antes de que c-126 regenere el reporte desde Windows |
| 3 | c-126 | A2, B7b, B8; McNemar (bloque 7) | `evaluation/` (metrics, report, cache), `.gitattributes`, memo, 04, 07, 08, 09, 11 | c-125 | Produce la exactitud por etapa, por canal y laxa y el contraste pareado que consumen c-137, c-127, c-128, c-131 y c-133 |
| 4 | c-137 | A5b (mitad analitica: sensibilidad fuera de muestra) | `evaluation/` (modulo `sensibilidad_ajustes.py`, pruebas, `data/sensibilidad_ajustes/`, `report_sensibilidad_ajustes.md`, README), `.gitattributes`, `.gitignore`, memo (seccion nueva), 07 (`subsec:sensibilidad-ajustes`), 08 (limitacion nueva y remision en :18), 09 (evidencia del objetivo 6), 12 (:135, segunda oracion), `docs/anexo_h_prompt_gemini.md`; 05 solo si falta la calificacion | c-125, c-126 | Necesita el parrafo de procedencia de c-125 y el McNemar, la decision de datos y la estructura de 07 de c-126; precede a c-127 y c-128, que leen su limitacion y la evidencia del objetivo 6 |
| 5 | c-127 | A3 | 00 (:15/:31), 01 (:18), 08 (:14 y subseccion nueva), 09 (clausulas de :6 y :41), memo | c-126 (laxa), c-137 | El balance no depende de c-128; ir antes permite que c-128 cite el balance en la tabla de objetivos |
| 6 | c-128 | B4, B5, B6 | 00, 01, 04, 07, 08, 09 (`tab:cumplimiento-objetivos`) | c-125, c-126, c-137, c-127 | Necesita exactitud por etapa y por canal y la evidencia del objetivo 6; actua como compresor del resumen si supera 250 palabras |
| 7 | c-129, bloque de tesis | B7a, B12, B13b (cronometraje) | 00 (:27), 01 (:32), 04, 07 (`tab:tiempos-canal`), 08 (:12, :20), 11 (:32), memo | c-127 (resumen), c-128 (01) | Orden declarado por c-129 D12 |
| 8 | c-133 | Sec. 4 del dictamen; criterio 3 residual | 02 (tras O2 de `subsec:nlp-llm`), 03, 08 (comparacion con la literatura), `.bib` (+6), bitacora | c-125, c-126 | Aporta las fuentes de calibracion que citan c-131 y c-134; conmutativo con c-134 en 02 |
| 9 | c-131 | B11 | 10 | c-125, c-126 (duras); c-127, c-128, c-133 (blandas) | Orden declarado por c-131 D11; c-134 edita despues el mismo capitulo |
| 10 | c-130 | B9, B10a-d, B13a (cota telefonica) | 01 (:76), 03 (`tab:comparativa`, `tab:trabajos-academicos`), 04, 06 (`fig:cronograma`), 07 (:6), 08 (:46), 09 (:39) | c-125, c-126, c-129, c-137 | El parrafo introductorio de 07 debe enumerar la estructura final de resultados, incluida la subseccion nueva de c-137 |
| 11 | c-134 | A4, B15, B16a | 01, 02, 03, 04, 08, 10, 11, `.bib` (+8), `verify_citations.py` | c-125, c-128, c-129, c-130, c-131 | Orden declarado por c-134 (tabla de trabajos de c-130, `01:48` de c-128, `04:71/91` de c-129) |
| 12 | c-135 (si se incluye), texto de tesis | Criterio 5 residual | 05, 06, 10, 11, 12 | c-125, c-130, c-131, c-134 | Sus bloques de codigo no comparten archivos con la familia y pueden correr en paralelo desde G0; el texto va antes de c-132 |
| 13 | c-132 | B14 | todos los `.tex`, `main.tex`, preambulo, campos `note` del `.bib` | todos los anteriores | Ultimo editor de prosa; cambios puramente diacriticos |
| 14 | c-136, grupos 2 a 9 | Cierre y B16b | 12-anexos, `.bib` (solo la version del repositorio), renders, KB, registro, memo (encabezado), `CHANGES.md` | todos | Integracion, verificacion y release |

Desacuerdos resueltos:

- **c-137 entre c-126 y c-127.** Es el orden que propone c-137 y que confirma el orquestador: c-137 consume el McNemar y la decision de datos de c-126, y c-127 y c-128 leen su limitacion y la evidencia del objetivo 6.
- **c-127 frente a c-128.** c-128 (D7) propone c-128 -> c-127; c-127 (D11) y c-131 (D11) proponen c-127 -> c-128. Se adopta c-127 -> c-128: c-127 no depende de c-128 (usa el 26,5 % de error y la estimacion manual del 15 %), la propiedad por clausula de c-128 D7 evita conflictos dentro de los parrafos compartidos, c-128 puede citar el balance en la tabla de objetivos y, como compresor del resumen, conviene que pase despues de la oracion de viabilidad de c-127. El orquestador debe actualizar el D7 de c-128.
- **c-129 en dos tramos.** Su bloque de codigo va antes de c-126 y su bloque de tesis despues de c-127 y c-128, como declara c-129 D12.
- **c-133, c-131, c-130 y c-134.** Se sigue c-131 D11 (c-133 -> c-131 -> c-134), pero c-130 pasa antes de c-134 porque c-134 declara que necesita la tabla de trabajos ya completada por c-130; c-130 no depende de c-131 ni de c-134 (fragmentos disjuntos en 03).
- **c-135 frente a c-128.** No hace falta adelantar c-135: su D11 fija que, si c-128 ya esta aplicado, c-135 actualiza solo el calificativo de la fila del objetivo 1. Si c-135 se excluye, c-128 usa el calificativo sin c-135.
- **Divisiones explicitas.** A5: procedencia declarada en `05:78`, `06:75`, `08:18` y la primera oracion de `12:135` (A5a) -> c-125 (D9); sensibilidad fuera de muestra, limitacion y evidencia del objetivo 6 (A5b) -> c-137. B7: tiempos manuales por canal y Wilcoxon intra-canal (B7a) -> c-129; exactitud por canal (B7b) -> c-126. B13: salvedad de cota inferior del canal telefonico en `09:39` (B13a) -> c-130; procedimiento de cronometraje en vivo en `04:16`, `08:20` y `11:32` (B13b) -> c-129. B16: metadatos (B16a) -> c-134; version de `Gomez2026_repositorio` (B16b) -> c-136 en C1.

**Conflicto a resolver en la integracion: numeracion de secciones del memo.** c-125 y c-126 declaran ambos una "Seccion 3.7" en `numeros-canonicos.md`, y los `design.md` de c-128 y c-129 tambien la nombran; c-127 y c-137 ya usan "siguiente numero libre al aplicar". Regla: numera el orden de aplicacion. El primero en aplicarse (c-125, segun este orden) conserva 3.7; cada change posterior que cree una seccion propia toma el siguiente numero libre al aplicar y corrige sus propias remisiones (notas "ver seccion 3.N", su grupo en `dictamen-correcciones.md`, la evidencia de sus tareas). Si cada uno crea su seccion, la secuencia esperada es 3.7 c-125, 3.8 c-126, 3.9 c-137, 3.10 c-127, 3.11 c-128 y 3.12 c-129. c-136 verifica en P4 que la numeracion sea unica y consecutiva y que toda remision resuelva.

Editores en orden por archivo compartido:

| Archivo | Orden de edicion |
|---|---|
| `00-resumen.tex` | c-126 (si corresponde) -> c-127 -> c-128 -> c-129 -> c-132 |
| `01-introduccion.tex` | c-127 (:18) -> c-128 -> c-129 (:32) -> c-130 (:76) -> c-134 -> c-132 |
| `02-marco-teorico.tex` | c-125 -> c-133 -> c-134 -> c-132 |
| `03-estado-del-arte.tex` | c-133 -> c-130 -> c-134 -> c-132 |
| `04-marco-metodologico.tex` | c-126 (:65, laxa) -> c-128 -> c-129 -> c-130 -> c-134 -> c-132 |
| `05-arquitectura.tex` | c-125 (:78) -> c-137 (solo si falta la calificacion) -> c-135 (si se incluye) -> c-132 |
| `06-implementacion.tex` | c-125 (:75) -> c-130 (`fig:cronograma`) -> c-135 (si se incluye) -> c-132 |
| `07-resultados.tex` | c-125 -> c-126 -> c-137 (`subsec:sensibilidad-ajustes`) -> c-128 -> c-129 -> c-130 (:6) -> c-132 |
| `08-discusion.tex` | c-125 (:16, :18) -> c-126 (:16) -> c-137 (remision en :18 y limitacion nueva) -> c-127 -> c-128 -> c-129 -> c-133 -> c-130 (:46) -> c-134 -> c-132 |
| `09-conclusiones.tex` | c-126 -> c-137 (celda de evidencia del objetivo 6) -> c-127 -> c-128 -> c-130 (:39) -> c-132 |
| `10-recomendaciones.tex` | c-131 -> c-134 -> c-135 (si se incluye) -> c-132 |
| `11-aspectos-legales.tex` | c-125 (:34) -> c-126 (:34) -> c-129 (:32) -> c-134 -> c-135 (si se incluye) -> c-132 |
| `12-anexos.tex` | c-125 (:135, primera oracion) -> c-137 (:135, segunda oracion) -> c-135 (si se incluye) -> c-132 -> c-136 |
| `Bibliography_base.bib` | c-133 -> c-134 -> c-132 (campos `note` y, si se decide, la etiqueta "Version") -> c-136 (solo la version del repositorio) |
| `numeros-canonicos.md` | c-125 -> c-126 -> c-137 -> c-127 -> c-128 -> c-129 -> c-136 (consolidacion, numeracion y encabezado) |
| `evaluation/run_evaluation.py`, `evaluation/report.md` | c-129 (codigo) -> c-126 -> c-129 (bloque "## Tiempos", idempotente); c-137 no los toca |
| `evaluation/README.md`, `evaluation/report_sensibilidad_ajustes.md`, `docs/anexo_h_prompt_gemini.md` | c-137 |
| `.gitattributes`, `.gitignore` | c-126 -> c-137 |
| `dictamen-correcciones.md` | c-136 (G0 y cierre); cada change agrega solo su propia seccion de grupo |
| `CHANGES.md` | orquestador (registro de la FASE 36) -> fases archive -> c-136 (cierre) |

Ningun change edita por adelantado archivos de otro; cada uno registra su fila en el libro mayor de paginas (D4) y deja en su `tasks.md` los comandos de verificacion que D7 re-ejecuta.

**Alternativas consideradas:** (a) el orden sugerido inicialmente por el orquestador (c-129 completo antes de c-128, c-134 antes de c-133, c-130 antes de c-131, c-135 al final, sin c-137): contradice dependencias declaradas por c-129, c-131, c-133, c-134 y c-137; (b) paralelizar changes con archivos disjuntos: ahorro marginal frente al riesgo de conflictos en 07, 08, 09 y el memo y a mediciones de paginas no atribuibles. La unica paralelizacion admitida es la de los bloques de codigo de c-135 (y el bloque de herramienta de c-132, que no toca la tesis).

### D2 - Gate G0: decisiones bloqueantes al inicio de la familia

Antes de aplicar c-125 se registran en una seccion "FASE 36 - decisiones G0" de `dictamen-correcciones.md`:

- **G0.1** La regla y el valor del tope de paginas (OQ1), junto con la opcion de compensacion C3 de c-137 (su tabla a un anexo), que solo rinde bajo la regla del cuerpo sin anexos.
- **G0.2** El entorno de compilacion de registro (OQ3), con la prueba de que reproduce las 101 paginas de la linea base `v1.1.1`.
- **G0.3** La inclusion o exclusion de c-135 (OQ4).
- **G0.4** El nombre de la release (OQ2; puede confirmarse hasta antes de C1).
- **G0.5** El estado de las caches de predicciones (decision propia de c-126; G0 solo registra el estado porque condiciona A2, B7b, B8 y las sensibilidades E3/E4 de c-137).
- **G0.6** El orden de D1.
- **G0.7** Los checkpoints de c-137 (OQ7), ambos de nivel HIGH: (a) autorizacion o no de la ablacion paga del prompt (nivel c: 138 invocaciones sobre los 69 casos de la etapa Gemini, del orden de 0,03 USD y como maximo 0,10 USD); sin autorizacion ni caches, la sensibilidad del prompt se declara no cuantificada; (b) existencia, forma (pseudonimizados o no) y etiquetado de los ~100 incidentes de preproduccion del Anexo H; el repositorio no los contiene, y cualquier dato personal queda sujeto a la Ley 25.326 y a aprobacion explicita.

El grupo 1 de `tasks.md` se ejecuta con un apply parcial al inicio de la familia; los grupos 2 a 9, al final.

**Alternativa considerada:** decidir el tope al cierre, como c-116. Se descarta: c-118 no alcanzo su tope al final y la familia agrega entre 5 y 12 paginas (D3); compactar todo al cierre solo con palancas de forma es inviable. Decidir antes permite que cada change compense localmente, como hicieron c-117 y c-118 con su "neutralidad de paginas".

### D3 - Tope de paginas: regla unica, dos ramas y estimacion de la familia

El tope vigente se registra una sola vez como {regla de medicion: total del PDF o cuerpo sin anexos; valor; fuente: exigencia de la catedra o decision del equipo; fecha}. El requisito modificado `Presupuesto de páginas preservado` lo hace cumplir y subsume los topes de 100 paginas de requisitos de c-116, c-117 y c-118. Mientras OQ1 no tenga respuesta, rige la rama (a): **total <= 101**, el criterio duro mas reciente (c-120..c-123). La candidata natural para la rama (b) ya figura en los registros: la regla del plan §1.1 (**cuerpo sin anexos <= 100, anexos sin limite**), que c-118 aplico con confirmacion del autor; falta confirmar si es la exigencia de la catedra.

Impacto declarado por la familia (de sus `proposal.md` y `design.md`):

| Change | Lo que declara | Neto estimado (paginas) |
|---|---|---|
| c-125 | +0,7 a +0,9 bruto antes de compensar; "puede llevar el PDF a 102" | +0,3 a +0,9 |
| c-126 | +0,6 a +0,9 bruto, con compensaciones previstas (D12) | 0 a +0,9 |
| c-137 | +1,0 a +1,4 bruto (central +1,2): subseccion nueva con tabla en 07; compensaciones en su D15 (C3: tabla a un anexo) | +1,0 a +1,4 |
| c-127 | +1 a +3 bruto (central +2); objetivo neto <= +1 | +1 a +3 |
| c-128 | Variacion nula (D8) | 0 |
| c-129 | +0,4 a +0,6 bruto; neto <= +0,4 (D10) | 0 a +0,4 |
| c-130 | Neutral (figura compensada en el capitulo 6) | 0 |
| c-131 | +1,2 a +1,5 bruto; el capitulo queda en 5 paginas como maximo | 0 a +1 |
| c-133 | +2 esperadas, +3 en el peor caso (capitulo 3 lleno y 6 entradas nuevas) | +2 a +3 |
| c-134 | +1 esperada en la bibliografia (8 entradas); cuerpo neutral; compensacion tipografica delegada a c-136 | +1 |
| c-135 (opcional) | +0,3 a +0,5 con los tres bloques | 0 a +0,5 |
| c-132 | Neutral (cambios diacriticos) | 0 |
| c-136 | Mapeo compacto del Anexo I | +0,1 a +0,6 |
| **Total sin c-135** | | **+5,4 a +12,2 (central del orden de +7,7)** |

Resultado sin compactar: total de 106 a 113 paginas (central unas 108,7); la bibliografia pasa de 59 a unas 73 entradas. Como solo el Anexo I crece fuera del cuerpo (la edicion de c-137 en `12:135` es de una oracion), el cuerpo sin anexos queda en 98 a 104,6 (central unas 100,4; con C3 de c-137, unas 0,3 a 0,5 menos). Consecuencias:

- **Regla del plan §1.1 (cuerpo <= 100):** la estimacion central queda en el limite y requiere compensar unas 0,4 paginas, que cubren las palancas de forma P1-P5 de D5 (1,6 a 2,9) o la opcion C3 de c-137; el extremo alto exige compensar hasta 4,6 paginas, lo que necesita tambien P6 y P7 (sujetas a aprobacion). Viable, con compensaciones locales disciplinadas.
- **Rama (a) (total <= 101):** hay que compactar de 5,4 a 12,2 paginas (central 7,7). Las palancas de forma rinden 1,6 a 2,9, y con las de formato P6 y P7, 2,9 a 5,1: no alcanzan ni en el extremo bajo. Solo cierran la brecha el cambio de interlineado P8 (formato de la catedra) o reducir el contenido de la familia (por ejemplo, acotar c-133 al minimo o exigir neutralidad estricta a c-127, c-131 y c-137), lo que resta cobertura del dictamen.

**Alternativa considerada:** medir el cuerpo o el total segun convenga en cada change. Se descarta: esa ambiguedad es la que produjo hoy un spec con 100 y un PDF con 101.

### D4 - Libro mayor de paginas

Seccion del registro con una fila por change (c-125..c-135 y c-137): change, commit, total, cuerpo sin anexos, anexos, delta total, delta cuerpo, regla vigente y estado. Linea base `v1.1.1`: 101, 93 y 8. Cada change registra su fila despues de su apply (el orquestador lo incluye en cada prompt de apply, y varios changes ya lo preven en sus tareas) y c-136 la consolida y la contrasta con el PDF final; la fila de c-137 se contrasta con su prevision de +1,0 a +1,4. Medicion: total con `pdfinfo` o, como equivalente, el conteo de saltos de pagina de `pdftotext`; el cuerpo sin anexos es la pagina del encabezado "Anexos" menos 1 (`\contentsline {section}{Anexos}{N}` de `main.toc`). Alarma temprana: si el delta acumulado supera el margen de la regla vigente menos 1 pagina de reserva, el orquestador se detiene y consulta antes de aplicar el change siguiente.

**Alternativa considerada:** medir solo al final. Se descarta por el precedente de c-118.

### D5 - Plan de compactacion (solo rama a)

Invariantes (de c-116 D4, ampliados a la familia): no se elimina ni altera contenido cientifico, numeros canonicos, figuras y tablas requeridas (incluidas las nuevas de la familia y sus lineas de fuente), referencias ni ninguna correccion de c-102..c-137. Las compensaciones que cada change ya declara (por ejemplo C3 de c-137) se aplican antes que las palancas de c-136. Catalogo de palancas:

| Palanca | Ahorro estimado | Clase |
|---|---|---|
| P1 Redundancia introducida por la familia (por ejemplo, la regla del gate o la procedencia de los ajustes explicadas en varios capitulos: una explicacion completa y remisiones `\autoref` en las demas) | 0,5 a 1,0 | Forma |
| P2 Leyendas sobre-extendidas de tablas y figuras nuevas (el detalle pasa a la prosa) | 0,2 a 0,4 | Forma |
| P3 Tablas nuevas con el mismo cuerpo de letra y densidad que las existentes | 0,3 a 0,5 | Forma |
| P4 Espaciado de flotantes y listas (`\textfloatsep`, `\intextsep`, listas compactas) | 0,3 a 0,5 | Forma (preambulo) |
| P5 Anexos H e I compactos | 0,3 a 0,5 | Forma |
| P6 Indices de tablas y de figuras en una misma pagina | 0,5 a 1,0 | Formato: requiere aprobacion |
| P7 Bibliografia en `\small` con `\bibitemsep` reducido (la compensacion que c-134 delega en c-136) | 0,8 a 1,2 | Formato: requiere aprobacion |
| P8 Interlineado del cuerpo de 2 a 1,5 (`\onehalfspacing`) | Del orden de 10 a 14 (estimacion gruesa) | Formato de la catedra: requiere aprobacion explicita |

El presupuesto por seccion (equivalente a la tabla D3 de c-116) se arma sobre el PDF integrado, porque la distribucion real del crecimiento se conoce recien entonces, y prioriza los capitulos cuya ultima pagina desbordo por pocas lineas (cuantizacion por inicio de capitulo en pagina nueva). Checkpoint HIGH: se propone la lista de recortes por seccion y las palancas de formato necesarias, el usuario la revisa y recien despues se edita; se mide el acumulado tras cada bloque y se verifican los invariantes.

**Alternativas consideradas:** mover contenido a los anexos (no reduce el total; solo sirve bajo la regla del plan §1.1); reducir el cuerpo de letra o los margenes del texto principal (formato de la catedra y legibilidad; peor que P8); recortar secciones (viola los invariantes).

### D6 - Entorno de compilacion de registro y evidencia

Requisitos del entorno: XeLaTeX y biber (`biblatex` APA) con las fuentes reales Arial y Courier New, secuencia xelatex -> biber -> xelatex -> xelatex o `latexmk` con `paper/latexmkrc` (modo 5, `BIBINPUTS=..//`). Opciones por orden de preferencia: (1) MiKTeX local de Gonzalo, el usado el 2026-10-20, con las fuentes del sistema Windows; (2) imagen Docker `texlive-thesis` construida con `paper/Dockerfile` (requiere red para `ttf-mscorefonts-installer`; el comando monta `docs/Tesis/v10 (IA)`, no la ruta de v9 de los comentarios); (3) Overleaf, solo para borradores salvo que tenga Arial, porque el reemplazo sugerido cambia la paginacion. El conteo de registro sale solo del entorno de registro, y G0.2 prueba que ese entorno reproduce las 101 paginas sobre las fuentes de `v1.1.1`. Todos los changes de la familia deberian medir en ese mismo entorno.

Evidencia: como `main.log` no se versiona, el registro consigna el entorno y sus versiones (`xelatex --version`, `biber --version`), el comando, los conteos de paginas (total y cuerpo) y los conteos extraidos del log: errores fatales (0), referencias y citas indefinidas (0), etiquetas duplicadas (0), `Overfull \hbox` mayores a 10pt (listados y revisados), WARN y ERROR de biber (0), estado de `verify_citations.py` (PASS) y ocurrencias de `??` en el texto del PDF (0).

**Alternativa considerada:** versionar `main.log` con `git add -f`. Se descarta: contiene rutas locales absolutas (nombre de usuario) y ruido; el resumen es reproducible recompilando.

### D7 - Precondiciones de integracion y regresion cruzada

- **P1, estado de la familia:** cada change c-125..c-134 y c-137 archivado, o aplicado (tareas N/N) y pendiente solo de archivo, en cuyo caso c-136 lo archiva. c-137 no admite exclusion porque A5 condiciona la aprobacion; sus niveles opcionales (corrida paga, conjunto de preproduccion, sensibilidades con cache) pueden quedar declarados como no cuantificados, pero la sensibilidad offline del vocabulario (E1) es obligatoria y sin costo. c-135 aplicado o excluido; si se excluye, se archiva como "NO REALIZADO" con `--skip-specs` (precedente de c-67) y los descuentos del criterio 5 quedan como limitacion declarada y trabajo futuro.
- **P2, reconciliacion:** el mapeo y las divisiones de D1 se contrastan con los artefactos de cada change. Toda parte de recomendacion u observacion sin dueno o con dos duenos se devuelve al orquestador antes de integrar (caso conocido: el `timeout` de 10 s frente a 30 s, que c-125 asigna a c-135, opcional, y que c-130 reporta fuera de alcance).
- **P3, regresion cruzada:** se re-ejecutan sobre el arbol integrado los comandos de verificacion del `tasks.md` de cada change, mas los controles de familia: valores retirados (9,5 %, 3.700, "Operaciones", W = 0 y los que la familia marque `retirado` en el memo, por ejemplo un desvio reemplazado por c-129), valores `vigente` del memo presentes, toda mencion de `97/131`, `0,7405` y `0,6769` calificada como estimacion dentro de la muestra o con remision a `subsec:sensibilidad-ajustes`, ninguna afirmacion de ausencia de fuga en la tesis, resumen <= 250 palabras y etiquetas referenciadas existentes.
- **P4, memo consolidado:** ver el requisito agregado a `tesis-numeros-canonicos`, incluida la numeracion unica de las secciones 3.N (conflicto de D1) y que ninguna corrida de sensibilidad de c-137 haya cambiado un valor vigente.
- **P5, sincronizacion con el remoto:** `git fetch origin`; se comparan `origin/main` y `origin/RamaLuca` contra la base comun en las rutas de la tesis, el registro, la KB, `evaluation/` y `CHANGES.md`; se integra `origin/main` en `ramagonzalo` con merge (no rebase, porque la rama esta publicada). Si hay conflictos en esas rutas, se detiene y se coordina con Luca.
- **P6, reportes de evaluacion:** `evaluation/report.md` conserva todas sus secciones (incluida "Normalidad (Shapiro-Wilk)", generada por `run_evaluation.py` desde c-99, y los bloques que agregan c-126 y c-129) y sus valores coinciden con el memo; `evaluation/report_sensibilidad_ajustes.md` (c-137) existe, sus valores figuran en el memo con procedencia y ninguna invocacion paga ocurrio sin autorizacion registrada; las caches oficiales y `report.md` no fueron modificados por c-137; la huella del corpus se verifica sobre el contenido versionado (`git show HEAD:data/corpus_evaluacion_pseudonimizado.json | sha256sum` = `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`), no sobre el archivo de trabajo, que en Windows con `autocrlf` da otro valor.

Regla: c-136 no corrige fallas sustantivas de otro change; las devuelve al orquestador para que las corrija el change dueno (OPSX fluido) o, si el dueno ya esta archivado, un change de correccion acotado, y repite P3. Por eso el archivo pendiente de la familia (P1) se hace despues de P3-P6.

### D8 - Renders derivados

- **`tesis_para_agente.md`:** `build_tesis_para_agente.py` pasa a recibir la release como argumento obligatorio (por ejemplo `python "docs/Tesis/v10 (IA)/build_tesis_para_agente.py" v1.2.0 > "docs/Tesis/v10 (IA)/tesis_para_agente.md"`) y falla si falta, de modo que el encabezado no vuelva a quedar desfasado; ademas falla si su lista de secciones difiere del orden de `\input` de `main.tex`. El cambio de interfaz se hace al final (grupo 7) para no romper las regeneraciones que c-125, c-126, c-128, c-129, c-132 y c-137 hacen sin argumento; hasta entonces el encabezado intermedio sigue desfasado, lo que es conocido y se corrige en la release. Se regenera en C1 (estado del tag) y en C2 (con el hash). Dos corridas consecutivas producen el mismo SHA-256.
- **Textos extraidos:** se regeneran desde el `main.pdf` de la release con `pdftotext -enc UTF-8`: `tesis_para_evaluacion.txt` conserva los saltos de pagina (permite citar paginas) y `tesis_completa_extraida.txt` es el mismo texto con espacios colapsados en un flujo continuo, como su formato historico.
- **`paper/tesis.docx`:** si hay pandoc disponible, se regenera y se le aplica `add_disclaimer.py`; si no, el registro declara que es un render legado no regenerado para `v1.2.0` (el propio documento remite a `main.pdf` como version autoritativa). Los dos `.docx` de la raiz de v10 son fuentes legadas fuera de alcance.
- **`openspec/config.yaml`:** se verifica que `thesis:` resuelva a un archivo existente; solo se repunta si la ruta cambia (no cambia en el plan base).

**Alternativas consideradas:** retirar los `.txt` (exigiria modificar el requisito de c-122 que los enumera y quitaria insumos que algun evaluador puede usar); regenerarlos desde los `.docx` (son fuentes legadas); dejar el encabezado del script cableado (asi quedo desfasado en `v1.1.0`).

### D9 - Base de conocimiento

Alcance: `knowledge-base/11_evaluacion_experimental.md` y `knowledge-base/README.md`. Se agrega un bloque "Resultados vigentes (release v1.2.0)" con valores copiados del memo y un puntero a `docs/Tesis/Correcciones/numeros-canonicos.md` como fuente unica: 200 casos; tiempos medios manual y automatizado; reduccion del 71,2 %; W = 363; r = 0,9639; exactitud estricta 73,5 % con su IC de Wilson; la macro-F1 primaria que fije c-128 (0,6508 sobre cuatro clases o 0,5207 sobre cinco) con la otra rotulada; kappa 0,87; universo de 2.646 incidentes; 32,2 horas-persona; y los valores nuevos de la familia (exactitud por etapa, por canal y laxa, p unilateral, d_z, escenarios del balance neto y sensibilidad fuera de muestra de c-137). Cualquier valor que la familia haya cambiado (por ejemplo, el desvio que recalcula c-129) se toma del memo, no de esta lista. La linea "Anti data-leakage" de `11_evaluacion_experimental.md:12` se reemplaza por la procedencia real de los ajustes (c-71, c-72 y c-74 con el corpus de evaluacion), la calificacion de las metricas como estimaciones al menos parcialmente dentro de la muestra y la remision a la sensibilidad de c-137, sin repetir la afirmacion refutada por A5. Las cifras del corpus sintetico quedan solo como historia y se retira "se re-miden". En el README se corrigen la ruta del render (`docs/Tesis/v10 (IA)/tesis_para_agente.md`), el modelo (`gemini-3.6-flash`, como en la tesis) y el resumen ejecutivo, con la viabilidad expresada como la deje c-127. No se introduce ningun numero que no este en el memo.

**Alternativa considerada:** regenerar la KB con `kb-creator`. Se descarta: reescribiria once archivos con contenido manual verificado para corregir dos.

### D10 - Trazabilidad: matriz completa en el registro y mapeo compacto en el Anexo I

- **Registro:** seccion "Dictamen v10 / v1.1.0 (2026-10-22) - cobertura por change (FASE 36)" con la matriz `| Rec | Sintesis | Change | Archivo:linea en v1.2.0 | Ancla | Fragmento verificable | Estado |`. Filas: A1, A2, A3, A4, A5a (procedencia declarada, c-125), A5b (sensibilidad fuera de muestra, c-137), B4, B5, B6, B7a, B7b, B8, B9, B10a-d, B11, B12, B13a, B13b, B14, B15, B16a (metadatos, c-134), B16b (version del repositorio, c-136), mas la literatura de calibracion y cascadas (c-133) y el criterio 5 residual (c-135 o limitacion declarada). Ancla esperada por fila (a confirmar con P2):
  - A1: `subsec:human-in-the-loop`, `subsec:subsistema-clasificacion`, `subsec:construccion-flujo-n8n`, `subsec:reduccion-intervencion`.
  - A2: `subsec:calibracion`, `tab:bandas`, `subsec:interpretacion-resultados`.
  - A3: `subsec:implicancias-practicas` o la subseccion nueva de c-127; `subsec:cumplimiento-objetivos`.
  - A4: `subsec:nlp-llm`, `subsec:trabajos-academicos`, `subsec:clasificador-supervisado`.
  - A5a: `subsec:subsistema-clasificacion` (05:78), `subsec:conexion-scrumban` (06:75), `subsec:interpretacion-resultados` (08:18), `subsec:anexo-iteracion-prompt` (12:135).
  - A5b: `subsec:sensibilidad-ajustes` (07, nueva), `subsec:limitaciones-estudio`, `tab:cumplimiento-objetivos` (objetivo 6).
  - B4: `tab:cumplimiento-objetivos`. B5: `subsec:hipotesis-trabajo`. B7a: `tab:tiempos-canal`. B8: `tab:metricas`.
  - B9: `subsec:gestion-scrumban`, `subsec:limitaciones-estudio`. B10: `sec:resultados`, `tab:comparativa`, `tab:trabajos-academicos`. B11: `sec:recomendaciones`, `subsec:aprendizaje-activo`. B12: `subsec:analisis-estadistico`, `subsec:poblacion-muestra-corpus`.
  - B13a: `subsec:cumplimiento-objetivos`. B13b: `subsec:diseno-experimental`, `subsec:consentimiento-derechos`. B15: `subsec:cumplimiento`, `subsec:analisis-estadistico`.
- **Lineas:** se calculan sobre el arbol de C1 (con la edicion del Anexo B ya hecha y despues de la compactacion y de la pasada corta), porque C2 desplaza las lineas posteriores del Anexo B en `12-anexos.tex`. La matriz declara que las lineas valen en `v1.2.0` y lleva el `\label` mas cercano como ancla estable. Verificacion: para cada fila, `git show v1.2.0:<archivo> | sed -n '<linea>p'` contiene el fragmento registrado.
- **Observaciones no numeradas:** tabla aparte con lo que el dictamen observa fuera de A1-A5 y B4-B16, cada una con su dueno o con la declaracion de que queda fuera de alcance:
  - Registros primarios del doble etiquetado no conservados: residual declarado en `subsec:poblacion-muestra-corpus`.
  - Doble fecha de consulta en las cinco entradas `@online`, seudonimo como apellido en `Tiangolo2024_fastapi`, `GDPR2016` y `Jurafsky2023_speech_language` sin enlace, sede omitida en Liu et al. 2025: c-134.
  - Ausencia de `main.log`: c-136 (evidencia de D6).
  - Version del modelo fechada en "junio de 2026" frente a `11036be` (24-09-2026): c-130 (B9).
  - `timeout` de 10 s en la tesis (`05:74`, `tab:anexo_gemini_params`) frente a 30 s en el backend: dueno a confirmar en P2.
  - Remision al inexistente `docs/prompt_gemini_history/` y afirmacion refutada en `evaluation/README.md` y `docs/anexo_h_prompt_gemini.md`: c-137.
  - Afirmacion refutada en `knowledge-base/11_evaluacion_experimental.md`: c-136 (D9).
- **Anexo I:** conserva la ruta del registro e identifica el dictamen (fecha y version examinada); agrega el mapeo recomendacion -> change -> seccion de la tesis (`\autoref`), como tabla compacta en `\small` (unos 0,5 paginas) o, si la rama (a) lo exige, como un parrafo de enumeracion (unas 8 lineas). Sin numeros de linea, que remiten a fuentes y no al PDF.

**Alternativas consideradas:** la matriz completa con archivo:linea dentro del Anexo (numeros de linea sin sentido en el PDF y cerca de 1 pagina); solo el parrafo actual (insuficiente: el jurado no puede ubicar las correcciones desde el documento).

### D11 - Verificacion contra la rubrica del dictamen

Tabla en el registro con los nueve criterios evaluables (el 10, defensa oral, no aplica): criterio, peso, puntaje del dictamen, descuentos, change que ataca cada descuento y estado tras `v1.2.0` (cerrado, parcial con justificacion o residual declarado). No asigna puntajes (eso es del jurado): registra la evidencia, que es la fila de la matriz D10. Mapeo base sobre la revision vigente del dictamen (ponderado 7,67):

| Criterio (peso; puntaje) | Descuentos del dictamen | Change |
|---|---|---|
| 1 Definicion del problema (15; 8,5) | Sub-hipotesis 2 no contrastable; hipotesis subsidiarias no contrastadas; sub-pregunta de calidad por canal sin respuesta | c-128 (B5); c-128 (B5); c-126 (B7b) |
| 2 Justificacion y relevancia (10; 9) | Sin descuentos | Verificar que c-127 no altere el argumento |
| 3 Marco teorico y revision (15; 8) | Metricas de la tabla de trabajos previos; telefonia sin columna; sin literatura de calibracion y cascadas; atribuciones imprecisas | c-130 (B10d); c-130 (B10c); c-133; c-134 (A4) |
| 4 Metodologia (20; 7) | p bilateral con hipotesis unilateral; potencia heterogenea; estratificacion no verificable y clase con n = 1; exactitud laxa; intervencion humana nunca medida; registros primarios no conservados; afirmacion de ausencia de fuga de datos desmentida por el historial | c-129 (B12); c-129 (B12); c-129 (B12); c-126 (B8); c-125 (A1) y c-128 (B5); residual declarado en `subsec:poblacion-muestra-corpus`; c-125 (A5a) y c-137 (A5b) |
| 5 Desarrollo tecnico (15; 8) | TLS no desplegado, invocacion sincronica sin reintentos, sin pruebas de extremo a extremo; gate no aplicado a la etapa determinista | c-135 o limitacion declarada; c-125 (A1) |
| 6 Resultados y analisis (10; 6,5) | Calibracion invertida como artefacto de agregacion; 124 casos no escalados; sin exactitud por etapa ni canal; tiempos manuales por canal; exactitud reportada sin advertir que es en parte una estimacion dentro de la muestra | c-126 (A2); c-125 (A1); c-126 (A2, B7b); c-129 (B7a); c-125 (A5a) y c-137 (A5b) |
| 7 Conclusiones y aportes (10; 7) | Tabla de objetivos sobreestimada; viabilidad operativa sin costo de derivacion erronea; dos lineas sin desarrollo; aprendizaje activo contradictorio | c-128 (B4); c-127 (A3); c-131 (B11); c-131 (B11) |
| 8 Redaccion y estructura (5; 7) | Tildes; cronologia; residuos de redaccion | c-132 (B14); c-130 (B9); c-130 (B10a, B10b) |
| 9 Referencias (5; 7,5) | Correspondencia texto-fuente; normas sin entrada; metadatos | c-134 (A4, B15, B16a); c-136 (B16b) |

### D12 - Release v1.2.0

- **Nombre:** `v1.2.0`. Incremento menor: analisis y correcciones de contenido sobre la misma estructura (`v1.1.1` fue un parche de metadatos). `v2.0.0` solo si el jurado o la catedra piden una version nueva numerada para el reexamen (OQ2).
- **Antes de C1:** P5 (sincronizacion con `origin/main`, para que el tag represente el estado entregado del repositorio, incluido lo ultimo de Luca) y `git ls-remote --tags origin v1.2.0` vacio.
- **C1:** en `sec:anexo-repositorio`, el tag `v1.1.1` pasa a `v1.2.0` y se retira la linea del hash de `v1.1.1`; el titulo de `Gomez2026_repositorio` pasa a la version `1.2.0`, conservando la etiqueta "Version" tal como la haya dejado c-132; se recompila y se regeneran los renders. Commit C1 en `ramagonzalo`.
- **Prueba de humo de c-135:** si c-135 se aplico con su bloque de humo, se re-ejecuta sobre C1 antes de publicar el tag (interfaz que c-135 declara con la release) y su evidencia se consigna en C2.
- **Tag:** `git tag -a v1.2.0 -m "..." <C1>`; `git cat-file -t v1.2.0` = `tag`. Push del tag y de la rama con confirmacion del usuario (checkpoint HIGH).
- **C2:** linea con el hash completo de 40 caracteres en el Anexo B, nota "Trazabilidad `v1.2.0`" en "## Notas" del registro, recompilacion y renders.
- **Integracion:** PR `ramagonzalo` -> `main` con merge commit, nunca squash ni rebase, que dejarian el commit etiquetado fuera de la historia de `main`; despues del merge, `git merge-base --is-ancestor v1.2.0 origin/main`.

**Alternativa considerada:** etiquetar en `main` despues del merge. Se descarta: el commit de merge lo crea quien mergea, puede incluir trabajo posterior a la verificacion y rompe la continuidad con `v1.0.0`..`v1.1.1`, etiquetados sobre el commit verificado.

### D13 - Cierre documental

1. Los changes de la familia se archivan antes de C1 (despues de P3-P6), en un commit propio, para que el arbol etiquetado tenga los specs sincronizados y ningun otro change activo de la familia; c-136 se archiva despues de C2, en su fase archive.
2. Pasada ortotipografica corta: se re-ejecutan las verificaciones automatizables de c-132 (formas diacriticas y palabras enumeradas por el dictamen) sobre el texto modificado despues del commit de apply de c-132 (`git diff <commit-c-132>..HEAD -- sections/`), es decir, la compactacion y el Anexo I; los aciertos se revisan a mano. No se reaplican `acentuar_tesis.py` ni `acentuar_tesis_v9.py`, que el dictamen revisado identifica como origen de erratas.
3. `CHANGES.md`: FASE 36 con el estado de cada change (ARCHIVADO con fecha y N/N, o NO REALIZADO), nota fechada en "Notas del analisis" (release, hash, paginas, regla del tope) y, en "Primer change recomendado", la numeracion C-01..C-137 y la version final publicada. La fase archive de c-136 lo pasa a ARCHIVADO.
4. El merge del PR es el ultimo paso, posterior al archive, y lo ejecuta el usuario o quien el designe.

## Risks / Trade-offs

- [El tope de 101 resulta inalcanzable con la familia completa] -> Decision temprana en G0 con la estimacion de D3 a la vista, libro mayor con alarma, aprobacion explicita de P6-P8 o rama (b) documentada.
- [Los artefactos finales de la familia difieren de D1] -> P2 reconcilia antes de integrar y devuelve al dueno; el registro deja constancia del dueno final de cada parte. El desacuerdo c-127/c-128 requiere actualizar el D7 de c-128.
- [Numeracion duplicada de secciones del memo] -> Regla de numeracion por orden de aplicacion (D1) y verificacion en P4.
- [Las caches de predicciones no se recuperan (c-126)] -> Los valores de A2, B7b, B8 y las sensibilidades E3/E4 de c-137 sin procedencia bloquearian la consolidacion del memo: el memo los declara en "Decisiones no resolubles", la matriz marca esas filas como cerradas parcialmente con justificacion y no se etiqueta con valores sin procedencia.
- [La corrida paga de c-137 no se autoriza o el conjunto de preproduccion no existe] -> La sensibilidad offline del vocabulario (E1) es suficiente para el minimo que pide A5; el prompt queda declarado como no cuantificado y la ausencia del conjunto se declara. Cualquier dato de preproduccion con datos personales queda sujeto a la Ley 25.326 y a aprobacion explicita (HIGH).
- [Observacion sin dueno (`timeout` 10 s frente a 30 s)] -> P2 la devuelve al orquestador antes de C1; si c-135 se excluye, debe reasignarse.
- [Conflictos con el trabajo de Luca en `main` o `RamaLuca`] -> P5 antes de C1; coordinacion explicita; no se reescribe historia publicada.
- [Un entorno con otras fuentes cambia la paginacion] -> Un unico entorno de registro, validado en G0.2 contra las 101 paginas de la linea base y usado por toda la familia.
- [Huella del corpus distinta en Windows] -> Verificacion sobre el contenido versionado (P6), no sobre el archivo de trabajo.
- [Las lineas de la matriz se desplazan] -> Se calculan sobre el arbol de C1, se acompanan del `\label` ancla y se verifican contra `v1.2.0`.
- [Tag prematuro o sobre el commit equivocado] -> Pasos ordenados, verificacion con `git cat-file -t` y `git rev-parse`; tras la entrega al jurado el tag no se borra (se publica `v1.2.1`).
- [Merge con squash o rebase deja el tag fuera de `main`] -> Merge commit obligatorio y verificacion posterior al merge.
- [Un change tardio reintroduce erratas] -> Pasada corta sobre el diff posterior a c-132, sin reaplicar las utilidades de acentuacion.
- [Los renders vuelven a quedar desfasados] -> Release como argumento obligatorio, regeneracion en C1 y en C2, control de determinismo.
- [Doble edicion o hueco en A5, B7, B13 o B16] -> Divisiones explicitas de D1 y control P2.
- [c-132 acentua la etiqueta "Version" del `.bib`] -> C1 conserva la etiqueta que deje c-132 y solo cambia el numero; las verificaciones buscan el numero de version, no la etiqueta.
- [Requisitos previos que fijan "8 figuras"] -> Son locales de c-80/c-118 y se refieren a las ocho figuras de c-80, que siguen presentes; la verificacion exige que ninguna figura requerida falte y que cada `\includegraphics` resuelva, no un conteo exacto (hoy hay 10 entornos `figure`; el cronograma de c-130 haria 11).

## Migration Plan

1. **G0 (antes de c-125):** registrar OQ1-OQ4 y OQ7, reproducir la linea base de 101 paginas en el entorno de registro, abrir el libro mayor y fijar el orden de D1 (grupo 1 de `tasks.md`, apply parcial).
2. **Aplicacion de la familia** en el orden de D1 (c-125 -> c-129 codigo -> c-126 -> c-137 -> c-127 -> c-128 -> c-129 tesis -> c-133 -> c-131 -> c-130 -> c-134 -> c-135 -> c-132), cada change con su fila en el libro mayor y sus comandos de verificacion.
3. **Integracion (c-136, grupos 2 a 7):** P1-P6 con el archivo de la familia en un commit propio; Anexo I; presupuesto de paginas (rama a o b); pasada corta; contenido de C1 y compilacion de registro con evidencia; matriz, observaciones no numeradas, rubrica y libro mayor final; renders; KB.
4. **Release (grupo 8):** commit C1, prueba de humo de c-135 si corresponde, tag anotado, push con confirmacion, C2, recompilacion, renders y PR.
5. **Cierre (grupo 9 y pasos posteriores):** `CHANGES.md`; fase archive de c-136 (su commit actualiza el PR abierto en el grupo 8); merge del PR con merge commit y verificacion de que `v1.2.0` es ancestro de `origin/main`.
6. **Rollback:** antes del tag, `git revert` de los commits de c-136 y recompilacion; despues del tag y antes de la entrega, borrar `v1.2.0` local y remoto solo con confirmacion; despues de la entrega, publicar `v1.2.1`. Los tags previos no se tocan.

## Open Questions

- **OQ1 (bloqueante para toda la familia, G0):** el tope de paginas, ¿es una exigencia de la catedra? ¿Se mide sobre el total o sobre el cuerpo sin anexos, y con que valor? Con la estimacion de D3 (+5,4 a +12,2 paginas), las opciones reales son: (i) confirmar la regla del plan §1.1 (cuerpo sin anexos <= 100, anexos sin limite), ya aplicada en c-118 con confirmacion del autor, que en la estimacion central queda en el limite y exige compensaciones locales (recomendada, junto con la opcion C3 de c-137); (ii) mantener total <= 101 y aprobar el cambio de interlineado P8, que solo puede autorizar la catedra; (iii) mantener total <= 101 sin P8, reduciendo el contenido de la familia (menor cobertura del dictamen).
- **OQ2:** nombre de la release: `v1.2.0` (propuesto) o `v2.0.0` si el jurado o la catedra piden una version nueva numerada para el reexamen.
- **OQ3 (bloqueante, G0):** quien recompila y en que entorno de registro: MiKTeX local de Gonzalo (no detectado en el PATH de esta maquina), imagen `texlive-thesis` (sin construir aqui) u Overleaf con Arial.
- **OQ4 (bloqueante antes de c-135):** ¿se incluye c-135? Si se incluye, sus bloques de codigo pueden empezar en paralelo y su texto va en la posicion 12 de D1; si se excluye, se archiva como NO REALIZADO, el criterio 5 queda como limitacion declarada y el `timeout` de 10 s frente a 30 s necesita otro dueno.
- **OQ5:** `paper/tesis.docx`: ¿se regenera (requiere pandoc) o se declara render legado no regenerado?
- **OQ6:** ¿quien aprueba y mergea el PR a `main`, y se confirma la estrategia de merge commit? ¿Luca modificara `docs/Tesis/`, `knowledge-base/` o `CHANGES.md` en `main` o `RamaLuca` durante la FASE 36?
- **OQ7 (G0, checkpoints HIGH de c-137):** ¿se autoriza la ablacion paga del prompt (138 invocaciones, del orden de 0,03 USD y como maximo 0,10 USD)? ¿Existen los ~100 incidentes de preproduccion del Anexo H, en que forma y con que etiquetado? Recomendacion (la de c-137): autorizar la corrida, que es la unica estimacion controlada del efecto de las reglas de frontera, y usar el conjunto de preproduccion solo si existe pseudonimizado y etiquetado en los cinco sectores.
