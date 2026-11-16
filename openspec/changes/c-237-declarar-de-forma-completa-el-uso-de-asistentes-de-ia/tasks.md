# Tasks: Declarar de forma completa el uso de asistentes de IA

Al final de cada tarea, entre parentesis, el requisito del change que cumple (nombre corto). Nombres cortos: `TD` (`tesis-document`) «Declaracion IA» (declaracion completa del uso de asistentes), «Inventario IA» (inventario reproducible). Las tareas de preparacion y las verificaciones transversales no llevan parentesis.

Gobernanza: el script y el inventario son **BAJA** (utilidad de solo lectura) y siguen **Strict TDD** (RED, GREEN, TRIANGULATE, REFACTOR, con evidencia en el resumen de apply). La declaracion en el `.tex` es **ALTA** (autoria): **CHECKPOINT** de la compuerta de autores (grupo 3) antes del grupo 4. Ningun nombre real: solo T1, T2, T3 y P<n>. Cero llamadas a Gemini. No se tocan `App/`, `n8n/`, `evaluation/`, el corpus, `CHANGES.md`, `.engram/` ni `docs/defensa/`.

## 0. Preparacion y linea base

- [ ] 0.1 Leer `proposal.md`, `design.md` (D1 a D10) y el spec delta; leer `.agents/SKILLS.md` y cargar `python-testing-patterns` para el script.
- [ ] 0.2 Capturar la linea base: `git status`, `git rev-parse HEAD`, `git describe --tags`; registrar modificaciones preexistentes ajenas y no tocarlas.
- [ ] 0.3 Re-verificar los anclajes de `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`: `sec:anexo-trazabilidad` (L231), `subsec:nota-versiones` (L233), `\subsection{Revisiones que originaron las correcciones}` (L237, sin etiqueta), declaracion vigente (L241); si c-235 o c-238 ya se aplicaron, repuntar lineas y registrar el desplazamiento.
- [ ] 0.4 **Red de seguridad:** `cd docs/Tesis/Correcciones && python -m unittest test_resumir_registro_compilacion test_verificar_matriz_trazabilidad test_recontar_errores_frontera -v` y `cd "docs/Tesis/v10 (IA)" && python verify_citations.py`; registrar el baseline (pruebas en verde y `STATUS: PASS`). Si algo falla, detener y reportarlo como falla preexistente.

## 1. Script de conteo (Strict TDD)

- [ ] 1.1 RED: crear `docs/Tesis/Correcciones/test_contar_uso_asistentes.py` (`unittest`, estilo de `test_resumir_registro_compilacion.py`) con pruebas de `parsear_log` sobre un log sin trailers y uno con trailers de varios modelos; ejecutar y confirmar que fallan por ausencia del modulo. (TD «Inventario IA»)
- [ ] 1.2 GREEN: crear `docs/Tesis/Correcciones/contar_uso_asistentes.py` con `parsear_log` minimo; ejecutar y confirmar verde. (TD «Inventario IA»)
- [ ] 1.3 TRIANGULATE `contar`: casos de total, con y sin trailer, desglose por modelo (la suma del desglose igual al total con marca), co-autor humano en la categoria "otros co-autores" y no contado como asistencia, linea vacia o malformada; ejecutar hasta verde. (TD «Inventario IA»)
- [ ] 1.4 TRIANGULATE `clasificar_change`: `tasks.md` con rutas `.tex`, con `App/`, con scripts de `evaluation/` o `docs/Tesis/Correcciones/*.py`, con `n8n/workflow` y sin ninguna; ejecutar hasta verde. (TD «Inventario IA»)
- [ ] 1.5 `renderizar_markdown` y `main` (`--ref`, `--desde-ref`, `--archivo-changes`, `--salida`; `subprocess` sin `shell=True`, unica funcion con I/O): prueba de orden estable y de que la salida no contiene `@` ni identidades de autor; ejecutar hasta verde. (TD «Inventario IA»)
- [ ] 1.6 REFACTOR: extraer constantes (patrones de asistente y de ambito), mejorar nombres; ejecutar la suite tras cada paso. (TD «Inventario IA»)
- [ ] 1.7 Ejecutar el script real: sobre `v1.2.18..v1.5.2` debe dar 253 / 41; sobre el historial hasta `v1.5.2` registrar total, con marca y desglose por modelo (al proponer, a `88edd02`: 1.173 / 154; Fable 5.1: 65, Fable 5.2: 41, Fable 5: 35, Opus 5.5: 11, Sonnet 4.6: 2); si difiere, explicar la diferencia por ref y no ajustar el script para forzar el valor. (TD «Inventario IA»)

## 2. Inventario reproducible

- [ ] 2.1 Crear `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` con las secciones 1 a 6 de D1; secciones 1-2 con la ref, la salida del script y el comando exacto, y la aclaracion de cota inferior (D2). (TD «Inventario IA»)
- [ ] 2.2 Seccion 3: lista de artefactos de orquestacion (`AGENTS.md`, `CLAUDE.md`, `CHANGES.md`, `.agents/`, `.opencode/`, `.engram/`, `openspec/`, `knowledge-base/`, `docs/Tesis/Correcciones/Prompt2.docx`) con una linea de funcion cada uno; verificar existencia con `ls`. (TD «Inventario IA»)
- [ ] 2.3 Seccion 4: mapa de changes archivados por ambito con la salida de `clasificar_change` y al menos un ejemplo verificable por ambito (incluido c-222, bloque "Prosa de la tesis", `openspec/changes/archive/2026-11-14-c-222-*/tasks.md`). (TD «Inventario IA»)
- [ ] 2.4 Verificar que el inventario no contiene nombres reales ni correos (`rg -n '@' docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` sin coincidencias de correo; revision de nombres). (TD «Inventario IA»)

## 3. Compuerta de autores (CHECKPOINT ALTA)

- [ ] 3.1 Preparar en la seccion 5 del inventario el cuestionario OQ1 a OQ6 de `design.md` y el borrador D7 con sus huecos `[CONFIRMAR: ...]`; entregarlo al orquestador para que lo haga llegar a los autores. (TD «Declaracion IA»)
- [ ] 3.2 **CHECKPOINT:** detener la aplicacion hasta recibir las respuestas de T1, T2 y T3. Registrar cada respuesta por alias y fecha en la seccion 5, sin correos ni nombres; registrar la respuesta sobre la normativa (OQ4) con su referencia, o la declaracion de su ausencia. (TD «Declaracion IA»)
- [ ] 3.3 Redactar la seccion 6 (texto fuente de la declaracion) con D6 y solo los hechos confirmados: cada procedimiento de verificacion con su confirmacion trazable a la seccion 5; lo no confirmado se omite o se declara como no exhaustivo; sin huecos `[CONFIRMAR]` remanentes. (TD «Declaracion IA»)
- [ ] 3.4 Obtener la aprobacion explicita de los autores sobre el texto de la seccion 6 (registrar alias y fecha). (TD «Declaracion IA»)

## 4. Declaracion en el Anexo I

- [ ] 4.1 `12-anexos.tex`: retirar el parrafo de la declaracion vigente (L241) del Anexo I.2, conservando el parrafo sobre las revisiones. (TD «Declaracion IA»)
- [ ] 4.2 Agregar tras I.2 `\subsection{Declaracion de uso de asistentes de inteligencia artificial}\label{subsec:declaracion-uso-ia}` con el texto aprobado (apertura, tabla de cinco ambitos, cierre), o reescribir en el lugar si OQ6 asi lo decidio; usar `\path{}` para rutas y el estilo de tablas del anexo. (TD «Declaracion IA»)
- [ ] 4.3 Verificar con `rg` que el pasaje "para la correccion de estilo y la edicion del texto, y para la generacion de diagramas de flujo" ya no figura como declaracion, que `subsec:declaracion-uso-ia` es unica y que no hay huecos `[CONFIRMAR]` en el `.tex`. (TD «Declaracion IA»)
- [ ] 4.4 Contrastar la declaracion con el inventario: cada ambito con asistencia registrada figura; el ambito del texto declara redaccion de prosa; el conteo se presenta como cota inferior con su ref; registrar el contraste. (TD «Declaracion IA»)
- [ ] 4.5 Compilacion local de comprobacion con la imagen `texlive-thesis` (sin regenerar `compilacion.md`, que es de c-239): 0 errores fatales, 0 referencias indefinidas, 0 etiquetas duplicadas, y la subseccion ocupa como maximo una pagina; registrar la pagina de inicio y fin. (TD «Declaracion IA»)

## 5. Verificacion de cierre y traspaso

- [ ] 5.1 `git diff --stat`: confirmar que solo cambiaron `12-anexos.tex`, el inventario, el script y su prueba (mas los artefactos del change); ninguna cifra de resultado ni numero canonico cambio.
- [ ] 5.2 Ejecutar la suite de 0.4 mas `test_contar_uso_asistentes` y `verify_citations.py`; confirmar verde y `STATUS: PASS`.
- [ ] 5.3 Dejar registrado en el resumen de apply, para c-239: la seccion 6 del inventario como texto fuente de Q16 (`docs/defensa/respuestas-tribunal.md` L133-139), el comando para re-ejecutar el conteo sobre la ref de la release y la necesidad de actualizar las cifras de I.3 si cambian.
- [ ] 5.4 Correr `openspec validate c-237-declarar-de-forma-completa-el-uso-de-asistentes-de-ia --strict` y registrar el codigo de salida.
- [ ] 5.5 No commitear ni pushear sin instruccion de los autores; el `engram sync` queda a cargo del orquestador. Guardar en Engram el resumen del apply (`opsx/c-237-declarar-de-forma-completa-el-uso-de-asistentes-de-ia/apply`).
