# Design: Afinar la escritura y las correcciones por capitulo de la tesis (N-02 y concision)

## Context

Ver `proposal.md` para la motivacion. Fuente: devolucion de segunda instancia del tribunal del
11-11-2026 sobre `v1.2.18` (seccion 3, cierre de N-07; seccion 5, N-02; seccion 6, calificacion por
capitulo con su "Motivo principal"). Los deltas viven en `specs/tesis-document/spec.md`.

**Numeracion.** Capitulo del PDF -> archivo: 1 = `01-introduccion`, 2-3 = `02-marco-teorico` y
`03-estado-del-arte`, 4 = `04-marco-metodologico`, 5 = `05-arquitectura`, 6 = `06-implementacion`,
7 (Resultados) = `07-resultados`, 8 (Discusion) = `08-discusion`, 9 (Conclusiones) =
`09-conclusiones`, 10 = `10-recomendaciones`, 11 (legal) = `11-aspectos-legales`, 12 =
`12-anexos`. `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` = `docs/Tesis/Correcciones/`.

**Estado de partida verificado al proponer** (solo lectura, 2026-11-11, rama `main`):

- La auditoria del 4 de agosto de 2026 figura **solo en prosa** en `S/12-anexos.tex`, en la
  subseccion "Revisiones que originaron las correcciones" (parrafos en las lineas ~239-241), que la
  describe con sus datos (105 hallazgos, 28 criticos, 3,9/10) y la ruta
  `auditorias/Auditoria_Tesis_Gomez_Bustos_Sevilla_040802026.pdf`. La primera tabla de la
  trazabilidad (`tab:anexo-trazabilidad`, lineas ~247-279) es especifica del dictamen del 22 de
  octubre de 2026 y no incluye la auditoria de agosto.
- La linea base de escritura es la que declara el brief del orquestador (referencia indicativa;
  el apply la fija con la regla registrada): oraciones de mas de 60 palabras, ~24; de mas de 40
  palabras, ~8,8 %; "de modo que", ~29.
- `c-196` introdujo, en su delta, el requisito "Nota de versiones y trazabilidad de la auditoria
  del tribunal en el Anexo I", que quedo satisfecho con la auditoria **en prosa** ("primera fila o
  bloque"). `c-196` esta APLICADO (release `v1.2.19`) y **aun no archivado**, por lo que ese
  requisito todavia no esta en `openspec/specs/tesis-document/spec.md`.
- Hecho protegido (N-06): las 81 llamadas de la campana 2026-10 las recito un autor (respaldado por
  `c-70` y por los autores) y las de la campana complementaria, los operadores `O1`/`O2` (runbooks).
  La tesis es CORRECTA; `4.5`, `4.8` y `9.1` no se tocan por este motivo.

## Goals / Non-Goals

**Goals:**

- Agregar la auditoria del 4 de agosto de 2026 como **fila** de la trazabilidad del Anexo I, con
  los datos que el texto ya declara, sin inventar cifras.
- Bajar, de forma medible y verificable, las oraciones largas y la formula "de modo que", y retirar
  valoraciones residuales sin respaldo, sin cambiar ninguna cifra canonica ni el contenido
  sustantivo.
- Afinar, capitulo por capitulo, segun el "Motivo principal" de la seccion 6 de la devolucion.
- Que cada edicion quede registrada y que la recompilacion cierre sin referencias indefinidas.

**Non-Goals:**

- N-06 (recitacion de las llamadas): fuera de alcance; la tesis es correcta.
- Identificadores de cambio en el cuerpo (N-07a): ya atendidos por `c-196`.
- Cifras, hechos y mediciones nuevas; artefactos de release (version, tag, hash).
- `App/`, `n8n/`, `docker/`, `evaluation/`; el change activo `c-191` y el `c-198`.

## Decisions

- **D1 — Regla de medicion de la concision.** Una unica regla de conteo registrada cuenta
  oraciones (una por signo de cierre `.!?`), excluyendo comandos LaTeX, matematicas, pies de tabla,
  listados y comentarios; y cuenta las ocurrencias de "de modo que". La linea base se mide con esa
  regla al iniciar el apply y se consigna con el comando y su salida en
  `C/dictamen-correcciones.md`. Las cifras del brief son referencia indicativa, no la verdad del
  conteo. Alternativa descartada: usar el conteo crudo de una herramienta externa, no reproducible
  dentro del repo.
- **D2 — N-02 por MODIFIED, no por ADDED.** El requisito que rige la trazabilidad del Anexo I es el
  que introdujo `c-196`. Se lo MODIFICA para exigir la auditoria como **fila de tabla** (y no como
  prosa), preservando sus cuatro escenarios. Alternativa descartada: agregar un requisito nuevo,
  que duplicaria semanticamente ese requisito y complicaria el archive. **Dependencia de orden:**
  `c-196` debe archivarse antes que `c-197`; si se archivara `c-197` primero, el archive abortaria
  ("MODIFIED ... not found"). Se declara en `proposal.md`, en `CHANGES.md` y en las tareas.
- **D3 — Forma de la fila N-02.** Se inserta una tabla compacta al inicio de la trazabilidad de las
  correcciones (`sec:anexo-trazabilidad`), inmediatamente despues de la subseccion
  "Revisiones que originaron las correcciones" y antes de `tab:anexo-trazabilidad`. Su **primera
  fila** es la auditoria del 4 de agosto de 2026; las filas siguientes identifican la serie de
  autoevaluaciones internas y la devolucion del 11-11 (los tres tipos de revision que el requisito
  exige distinguir). Todos los datos de la fila provienen de la prosa existente (lineas ~239-241) y
  de `auditorias/`; el rotulo de etiqueta es nuevo (`tab:trazabilidad-revisiones`). Alternativa
  descartada: anteponer la fila a `tab:anexo-trazabilidad`, porque esa tabla es especifica del
  dictamen del 22 de octubre y su columna "Rec." se refiere a recomendaciones de ese dictamen.
- **D4 — Pase de escritura por capitulo.** La edicion es oracion por oracion: se parte una oracion
  larga en dos o mas sin agregar ninguna oracion de mas de 60 palabras; se reemplaza "de modo que"
  por punto, "por lo tanto" o "porque" segun el sentido. La asignacion por capitulo sigue la seccion
  6 de la devolucion (ver el requisito "Afinado de escritura por capitulo"). Cada pasaje editado se
  registra con su ubicacion previa en `C/dictamen-correcciones.md`.
- **D5 — Guardarrailes.** No se renumeran etiquetas; no se cambia ninguna cifra canonica; no se
  tocan `4.5`, `4.8` ni `9.1` por N-06; no se reintroducen los residuos que `c-196` retiro (kappa
  0,87 como evidencia, identificadores de cambio fuera del Anexo I, declaraciones de procedencia);
  no se edita la portada ni la version/hash del Anexo B.
- **D6 — Derivado.** `docs/Tesis/v10 (IA)/tesis_para_agente.md` se regenera con el script vigente
  (`build_tesis_para_agente.py`) despues de cerrar las ediciones, y `paper/compilacion.md` con
  `resumir_registro_compilacion.py`; ninguno se edita a mano.

## Risks / Trade-offs

- [Al partir oraciones se altera una cifra o una cita] -> no se mueven cifras ni claves de cita; el
  verificador de citas (`verify_citations.py`) y el diff por archivo lo comprueban al cierre.
- [El pase baja la concision pero sube la ambiguedad] -> cada oracion partida conserva su sujeto y
  su verbo; se revisa que el sentido causal se mantenga.
- [La tabla N-02 excede el margen o desborda el Anexo I] -> se usa `\footnotesize` y columnas
  `>{\raggedright\arraybackslash}p{...}`; se verifica la ausencia de `Overfull \hbox` nuevos de esa
  tabla tras compilar.
- [Se archiva `c-197` antes que `c-196`] -> se declara la dependencia de orden y el orquestador
  archiva `c-196` primero.
- [El tope de paginas] -> la tesis tiene un tope de paginas ya honrado; el pase recorta oraciones y
  no agrega contenido, por lo que el delta esperado es neutro o negativo. Se consigna el total.

## Migration Plan

1. Medir la linea base de escritura y congelar la foto de cifras canonicas.
2. Editar el Anexo I (D3) y aplicar el pase por capitulo (D4).
3. Recompilar y verificar (citas, referencias, margenes); regenerar derivados.
4. Registrar en `C/dictamen-correcciones.md` y `CHANGES.md`.

Rollback: `git revert` del commit de contenido restaura el texto previo; no hay migracion de datos
ni cambios de codigo.

## Open Questions

- Rotulo y columnas exactos de la tabla de revisiones de D3 (propuesta por defecto: "Revision",
  "Alcance", "Origen/archivo", "Seccion"). A confirmar con el orquestador antes de compilar; no
  cambia los specs ni el desglose de tareas, que solo exigen la auditoria como primera fila.
