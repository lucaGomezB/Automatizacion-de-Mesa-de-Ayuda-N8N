# Design: Respuestas del grupo a las 16 preguntas del tribunal (change c-198)

## Context

Ver `proposal.md` para la motivacion. Fuente: devolucion de segunda instancia del tribunal del
11-11-2026 sobre `v1.2.18`, **Seccion 8 ("Preguntas probables del tribunal")**: 16 preguntas en
cuatro bloques. La devolucion cierra con que "la defensa se evaluara sobre el ejemplar corregido y
sobre las respuestas del grupo a la Seccion 8". El change `c-196` (APLICADO) ya atendio las 16
observaciones N-01..N-16 en el texto de la tesis y versiono la devolucion en `auditorias/`; este
change produce el artefacto que falta: el documento de respuestas.

**Estado de partida verificado al proponer** (solo lectura, 2026-11-11, rama `main`):

- `docs/defensa/` no existe (no hay documento de respuestas todavia).
- Los hechos de la Seccion 8 ya estan resueltos o declarados en la tesis por c-196: el kappa de
  0,87 retirado (`04-marco-metodologico.tex` 4.4), la nota de versiones del Anexo I
  (`12-anexos.tex`, `subsec:nota-versiones`), el muestreo por conveniencia y el periodo 16-06 a
  10-09-2026 (4.4), el registro primario `data/corpus_resultados_web_correo.json` (118/119, `R001`
  sin registro; 4.5), los tiempos por operador (`tab:tiempos-manual-complementaria`, 8.7), las
  llamadas recitadas por un autor (4.8 y 9.1), la exactitud contra el consenso (Tabla
  `tab:exactitud-etapa-canal`), la regla de tres vias no concluyente (4.7 y 8.3), el balance neto
  (9.5) y el instrumento del art. 12 no suscrito (11.3).
- `12-anexos.tex` termina en el Anexo I (`\section{...}\label{sec:anexo-trazabilidad}`, ~linea
  231), dentro de `\begin{appendices}` de `main.tex` (linea ~84); cada `\section` es una letra de
  anexo (paquete `appendix`). El Anexo J es una seccion nueva al final del archivo.
- `evaluation/data/campana/` versiona `doble_etiquetado.csv`, `brazo_manual.csv`,
  `intervenciones.csv`, `plan_campana.csv`, `registro_sujetos.csv` y los sidecars; `data/` versiona
  `corpus_evaluacion_pseudonimizado.json`, `corpus_resultados_web_correo.json` y
  `corpus_resultados_telefonia.json`; `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`
  es la evidencia congelada.
- `C/verificar_matriz_trazabilidad.py` exige que toda seccion `## Dictamen ... - c-NNN` con NNN >=
  190 tenga al menos una fila de matriz de 7 columnas ("Fragmento verificable"). Si c-198 agrega
  una seccion de ese tipo en `dictamen-correcciones.md`, debe traer su matriz.

**Abreviaturas.** `D/` = `docs/defensa/`; `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` =
`docs/Tesis/Correcciones/`; `A/` = `auditorias/`. Cada parrafo de los `.tex` es una sola linea
fisica; el apply localiza por texto (`rg -n`).

## Goals / Non-Goals

**Goals:**

- Producir `D/respuestas-tribunal.md` con las 16 respuestas (Q1..Q16), verificables contra
  artefactos versionados y con cifras canonicas o recalculables.
- Incorporarlo como Anexo J en `S/12-anexos.tex`, con la serie de anexos que pasa de A-I a A-J.
- Registrar en `C/numeros-canonicos.md` todo valor que las respuestas citen y no este en el memo.
- Dejar marcado (no afirmado) lo que solo pueden aportar los autores.

**Non-Goals:**

- No se redactan respuestas en la fase de propose (esto es el plan).
- No se crean artefactos de release (tag, version, hash); van aparte.
- No se tocan `App/`, `n8n/`, `docker/`, `evaluation/` ni el change activo `c-191`.
- No se realizan nuevas mediciones.

## Decisions

### D1. Dos entregables en dos fases: documento fuente y luego Anexo J

El documento vive primero como `D/respuestas-tribunal.md` (artefacto del repositorio, revisable de
forma independiente) y despues se incorpora como Anexo J. Alternativa descartada: escribir
directamente el anexo en LaTeX, que impide revisar el contenido fuera del PDF y acopla la
redaccion al formato. El orden es requisito de la capability `tesis-defensa`.

### D2. Estructura del documento: 16 respuestas en los cuatro bloques de la Seccion 8

`D/respuestas-tribunal.md` se organiza con un encabezado por bloque y una subseccion por pregunta
(`### Q1. <pregunta>`), seguida de la respuesta y de una linea de fuentes. Cada respuesta es
autonoma (enuncia la pregunta y la responde). El Anexo J reproduce la misma estructura con
`\section` (Anexo J), `\subsection` por bloque y `\paragraph` o item por pregunta.

### D3. Cada respuesta cita el artefacto del que sale el hecho

Cada respuesta remite a la ruta versionada de la que proviene cada hecho. Mapa de preguntas a
fuentes (el apply lo verifica por texto antes de redactar):

| Pregunta | Tema | Artefactos y secciones fuente |
|----------|------|-------------------------------|
| Q1 | Fecha de etiquetado original y planilla del kappa 0,87 | `S/04` 4.4 (`subsec:poblacion-muestra-corpus`), `S/12` Anexo I (`subsec:nota-versiones`), `C/dictamen-correcciones.md` (c-196), `A/Devolucion_..._v1.2.18_2026-11-11.md` (N-01) |
| Q2 | Cifras de la version de julio (165,3 s, 92 %, W = 0, kappa 0,87) | `S/12` Anexo I (`subsec:nota-versiones`), `docs/anexo_f_corpus.md`, `C/dictamen-correcciones.md`, N-02 |
| Q3 | Seleccion de 200 de ~2.646 y periodo relevado | `S/04` 4.4, N-04; periodo 16-06 a 10-09-2026; margen 6,66 % |
| Q4 | Registro de los 119 tiempos de correo y formulario | `data/corpus_resultados_web_correo.json` (118/119; `R001`), `data/README.md`, `S/04` 4.5, `S/07` 8.1, Anexo F, N-05 |
| Q5 | Cuanto de la reduccion depende del operador | `evaluation/data/campana/brazo_manual.csv`, `S/07` 8.7 (`tab:tiempos-manual-complementaria`), `S/08` 9.1, N-03 |
| Q6 | Misma tarea manual en ambas campanas | `S/04` 4.5 (decision de sector) y 4.2/4.6 (lectura, busqueda, carga, escucha), N-03 |
| Q7 | Sin correlacion entre campanas | `S/07` 8.7 (Spearman 0,15 y -0,05; automatizado rho = 0,70), N-03 |
| Q8 | Efecto de la recitacion por un autor | `S/04` 4.8 y 4.5, `S/08` 9.1, `S/09` conclusiones, `S/11` 11.3, N-06 |
| Q9 | Tramos distintos en formulario web | `S/04` 4.5 (manual desde la lectura) y 4.5/7.1 (automatico desde el envio), `S/07` comparacion por canal |
| Q10 | Exactitud "verdadera" del clasificador | `S/07` `tab:exactitud-etapa-canal` (0,7971 sobre 138), `S/08` 9.3, N-08 |
| Q11 | Supervision humana efectiva hoy | `C/numeros-canonicos.md` (gate por etapa), `S/05`, `S/07` 8.4, `intervenciones.csv`; gate 0,70 derivo 0 casos; deterministic 131/200 |
| Q12 | 11 de 85 confirmaciones humanas incorrectas | `evaluation/data/campana/intervenciones.csv` + `doble_etiquetado.csv`, `S/07`, N-08 |
| Q13 | Cuando se fijo la regla de tres vias | `S/01` 1.4, `S/04` 4.7, `S/07` 8.3, `S/12` Anexo I (Tablas 22 y 24), N-09 |
| Q14 | Recomendarian adoptar hoy | `S/08` 9.5 (`subsec:balance-neto`), `S/09`, `S/10`; balance neto -18,5 a -43,9 h; a* = 77,7 % |
| Q15 | Clausulas modelo de la Disposicion 60-E/2016 | `S/11` 11.3 (`subsec:transferencia-internacional`), `docs/seguridad/instrumento-transferencia-internacional.md`, N-13 |
| Q16 | Uso de un modelo de lenguaje en la redaccion | `S/12` Anexo I (trazabilidad y `subsec:nota-versiones`), `C/dictamen-correcciones.md` |

### D4. Cifras canonicas o recalculables; nada retirado

Toda cifra coincide con un valor vigente de `C/numeros-canonicos.md` o se reproduce desde un
artefacto versionado. El kappa de 0,87 no se reintroduce como evidencia. Si una respuesta necesita
un valor nuevo, se registra en el memo (capability `tesis-numeros-canonicos`) antes de citarlo.

### D5. Hechos de la Seccion 8 declarados con precision

El documento declara, con el respaldo de c-196: (a) el kappa de 0,87 se retiro y su origen fue un
oversight sin planilla conservada; (b) la version de julio (3-7-2026) informo un corpus sintetico;
(c) el periodo relevado es 16-06-2026 a 10-09-2026, con muestreo por conveniencia; (d) el registro
primario de los 119 tiempos esta versionado y cubre 118 de 119 (`R001` sin registro); (e) las 81
llamadas de 2026-10 las recito un autor y las del brazo telefonico de la campana complementaria las
recitaron `O1` y `O2`.

### D6. Anexo J al final de `S/12-anexos.tex`

Se agrega, despues del Anexo I, `\section{Respuestas del grupo a las preguntas del tribunal}
\label{sec:anexo-respuestas-tribunal}`. La serie de anexos pasa de A-I a A-J. Se evita una linea
`Overfull \hbox`: rutas largas en `\path{}` y columnas de prosa `>{\raggedright\arraybackslash}p{}`.

### D7. Sin atribucion a un modelo de lenguaje; espanol neutro, sin emojis

El documento y el anexo se presentan como respuesta del grupo. No se declara autoria de IA ni se
usan emojis. Q16 responde sobre el uso de un modelo de lenguaje en la redaccion de la tesis: lo que
puedan aportar los autores queda como marcador `% PENDIENTE-AUTORES(Q16)` y el texto visible no
afirma un hecho no registrado.

### D8. Registro y trazabilidad

`C/numeros-canonicos.md` recibe los valores nuevos. `C/dictamen-correcciones.md` registra el change
(con matriz de 7 columnas si se abre una seccion `## ... - c-198`). `CHANGES.md` recibe la fase.

## Risks / Trade-offs

- **Cifra no canonica en una respuesta** -> Mitigacion: verificacion por grep contra
  `C/numeros-canonicos.md` antes de fijar cada cifra; si falta, se registra en el memo (tarea 4).
- **El anexo agrega paginas y agrava la concision (N-07)** -> Mitigacion: respuestas concisas,
  oraciones cortas; el Cierre registra el efecto en el libro mayor de paginas.
- **Q1 y Q16 dependen de datos solo de los autores** -> Mitigacion: marcador
  `% PENDIENTE-AUTORES(...)` y texto visible verdadero sin el dato.
- **Reintroducir un valor retirado (kappa 0,87 como evidencia)** -> Mitigacion: grep de aceptacion
  que exige 0 ocurrencias del 0,87 como evidencia.
- **Referencias colgadas en el anexo nuevo** -> Mitigacion: la compilacion exige cero referencias
  indefinidas y `verify_citations.py` en PASS.

## Migration Plan

1. Escribir `D/respuestas-tribunal.md` (16 respuestas).
2. Registrar valores nuevos en `C/numeros-canonicos.md`.
3. Incorporar el Anexo J en `S/12-anexos.tex`.
4. Recompilar (`main.pdf`, `compilacion.md`), registrar en `C/dictamen-correcciones.md` y
   `CHANGES.md`.

**Rollback:** revertir los archivos tocados (`D/respuestas-tribunal.md`, `S/12-anexos.tex`,
`C/numeros-canonicos.md`, `C/dictamen-correcciones.md`, `CHANGES.md`); ninguno es prerequisito de
codigo. El PDF previo se recupera con `git checkout` de `main.pdf` y `compilacion.md`.

## Open Questions

- La **fecha exacta** en que los analistas originales etiquetaron los 200 casos (Q1) puede no
  constar en el repositorio; si no consta, la respuesta lo declara y el dato queda como
  `PENDIENTE-AUTORES(Q1)`. No cambia el diseno ni las tareas.
- El **alcance del uso de un modelo de lenguaje en la redaccion** (Q16) es una declaracion de los
  autores; el documento la deja marcada, sin afirmarla. No cambia el diseno.
