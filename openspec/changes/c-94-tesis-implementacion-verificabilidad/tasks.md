# Tasks: c-94 — Verificabilidad de la implementacion y la arquitectura

> Convencion de rutas: `S = docs/Tesis/v9 (IA)/paper/sections`.
> Verificacion de texto: `rg` sobre `S` (sin compilador LaTeX local; los `.bak`
> no se editan ni se cuentan).
> Recompilacion: Overleaf (tarea final). No se edita `App/**`, ni c-76/c-77/c-80,
> ni `CHANGES.md`, ni `docs/Tesis/Correcciones/dictamen-correcciones.md`.
>
> **Orden de aplicacion (D-ORDER):** ejecutar este change DESPUES de c-76, c-77 y
> c-80. Comparte `S/05-arquitectura.tex` y `S/06-implementacion.tex` con ellos.
> **No duplicar:** c-77 C3 es dueno de la Tabla 4 (`id_canal` ->
> `canal_origen_id`) y de §5.3 (dos llamadas -> un `POST`); c-80 es dueno de las
> figuras/capturas (incluida la del dashboard, tarea 6.6) y de la nota N8N 1.62.
> **M-NUEVO:** c-76 ya alineo §1.6 de `01-introduccion.tex` y
> `docs/anexo_h_prompt_gemini.md` (tareas 9.2 y 5.3); c-94 solo edita los ocho
> archivos de seccion restantes y no re-edita esos dos.
> Este change los referencia, no los reescribe.
> **Gobernanza: MEDIUM** — cada decision de redaccion no obvia (retraer vs.
> reformular) se registra en la tarea y se expone en el resumen del apply.

## 1. Preparacion y fuentes de verdad

- [x] 1.1 Re-medir en HEAD el recuento de la suite de frontend para A-12: ejecutar `find App/Frontend/src -type f \( -name '*.test.ts' -o -name '*.test.tsx' \) | wc -l` y `rg -o "\b(it|test)\(" App/Frontend/src --glob '*.{test,spec}.{ts,tsx}' | wc -l`; registrar el valor y el comando. Confirmar que `App/Frontend/coverage` esta gitignored (`git check-ignore App/Frontend/coverage`) y que no existe informe versionado. Nota: el dictamen dice 68; HEAD puede diferir (medicion preliminar: 56 archivos / 340 ocurrencias). Verificacion: valor y comando registrados.
- [x] 1.2 Confirmar la ausencia de pruebas e2e que instancien N8N para A-11: ejecutar `rg -ln "workflow\.json|localhost:5678|httpx.*5678|docker" App/Backend/tests` y verificar que las coincidencias son pruebas estructurales del `n8n/workflow.json` o del contrato, no ejecucion del flujo; registrar los archivos hallados (`tests/test_c72_n8n_workflow.py`, `tests/test_c72_prompt_boundaries.py`, `tests/test_c72_cost_guard.py`). Verificacion: no existe prueba que instancie N8N.
- [x] 1.3 Inventariar las rutas reales de la API para M-13: ejecutar `python3 -c "import json; d=json.load(open('docs/openapi.json')); print(len(d['paths'])); [print(p) for p in sorted(d['paths'])]"` y agrupar por recurso (auth, incidentes, clasificaciones, estadisticas, salud). Verificacion: grupos y rutas registrados para la Tabla 5.
- [x] 1.4 Confirmar la titularidad de C-18 en c-77 C3: leer `openspec/changes/c-77-tesis-errores-estadisticos-inferenciales/tasks.md` (seccion 11, tareas 11.1+) y verificar que cubre la Tabla 4 (`id_canal`) y §5.3. Verificacion: constancia de que c-94 no duplica esas lineas.

## 2. Cap 6 — §6.7 Pruebas automatizadas (A-11, A-12)

- [x] 2.1 A-11: reescribir `S/06-implementacion.tex:85` para retirar la afirmacion de «pruebas extremo a extremo que ejecutaban el flujo completo desde el envio de un correo simulado hasta la persistencia del ticket, validando la integracion con N8N en su totalidad»; describir lo que existe (pruebas estructurales del `n8n/workflow.json` y pruebas de API/base de datos). Verificacion: `rg -n "extremo a extremo|correo simulado|integracion con N8N" S/06-implementacion.tex` sin la afirmacion retirada.
- [x] 2.2 A-12: corregir en `S/06-implementacion.tex:89` el recuento y la cobertura de la suite de frontend al valor reproducible medido en 1.1, y ajustar la desagregacion (27+10+43+9) o retirarla si no se reproduce; si se opta por publicar evidencia (OQ2), versionar el informe en `docs/` y citarlo. Verificacion: `rg -n "89 pruebas|98,6" S/06-implementacion.tex` sin la cifra sin respaldo.

## 3. Cap 6 — §6.4 Latencia telefonica (A-13)

- [x] 3.1 A-13: retraer o reformular `S/06-implementacion.tex:52` para que no declare la latencia de 12 a 15 s como observacion operativa atribuible sin `n`, dispersion ni procedimiento; si no hay evidencia atribuible, declarar la limitacion. Verificacion: `rg -n "12 a 15|observaciones operativas" S/06-implementacion.tex` sin la afirmacion sin respaldo.
- [x] 3.2 A-13 (coordinacion): alinear la redaccion con la metrica de tiempo telefonico de c-77 (Grupo E, `openspec/changes/c-77-tesis-errores-estadisticos-inferenciales/tasks.md:90-108`) sin redefinirla; registrar la referencia. Verificacion: la formulacion de §6.4 es consistente con c-77 y no la contradice.

## 4. Cap 6 — §6.8 Dashboard (M-08)

- [x] 4.1 M-08: reformular `S/06-implementacion.tex:101` para presentar el ejemplo de los veinte usuarios con auriculares como hipotetico, retirando «se ilustra con un caso concreto». Verificacion: `rg -n "caso concreto|veinte usuarios" S/06-implementacion.tex` con el ejemplo marcado como hipotetico y sin «caso concreto».
- [x] 4.2 M-08 (coordinacion): confirmar que la captura del dashboard permanece en c-80 (tarea 6.6) y que c-94 no agrega capturas ni duplica esa evidencia. Verificacion: constancia en el resumen del apply.

## 5. Cap 6 — §6.1 Kubernetes (M-09)

- [x] 5.1 M-09: retraer o acotar en `S/06-implementacion.tex:8` la afirmacion «preparados para migracion a un cluster Kubernetes 1.30», dejandola como intencion de diseno o trabajo futuro (no como capacidad implementada). Verificacion: `rg -n "Kubernetes" S/06-implementacion.tex` con la afirmacion acotada o retirada.

## 6. Cap 5 — §5.4 Parametros de inferencia (M-12)

- [x] 6.1 M-12: retirar o documentar el calificativo «optimizados para exactitud y latencia» en `S/05-arquitectura.tex:50`; si se documenta, describir el procedimiento y los valores alternativos evaluados. Verificacion: `rg -n "optimizados para exactitud" S/05-arquitectura.tex` sin el calificativo no respaldado (o con el procedimiento documentado).

## 7. Cap 5 — Tabla 5 puntos de entrada REST (M-13)

- [x] 7.1 M-13: completar la Tabla 5 (`tab:api`, `S/05-arquitectura.tex:92-105`) agrupando por recurso segun el inventario de 1.3: autenticacion (`/api/v1/auth`), incidentes (incluido el PATCH), clasificaciones (GET y PATCH), estadisticas y salud. Verificacion: `rg -n "auth|clasificaciones|PATCH" S/05-arquitectura.tex` con los grupos presentes en la tabla.
- [x] 7.2 M-13: agregar una nota de que la Tabla 5 no es exhaustiva, con remision al contrato completo en el Anexo D/OpenAPI. Verificacion: `rg -n "no exhaustiva|Anexo~D|OpenAPI" S/05-arquitectura.tex` con la nota presente.

## 8. Coordinacion — residuo textual de C-18 (sin duplicar)

- [x] 8.1 Verificar que la Tabla 4 (`id_canal` -> `canal_origen_id`) y §5.3 (dos llamadas -> un `POST /api/v1/incidentes`) quedan cubiertas por c-77 C3 y que c-94 no edita esas lineas. Verificacion: `rg -n "id_canal|canal_origen_id" S/05-arquitectura.tex` y constancia de que la correccion es de c-77 C3.

## 9. Verificacion final y recompilacion

- [x] 9.1 Barrido de control: ejecutar `rg -n "extremo a extremo|correo simulado|89 pruebas|98,6|12 a 15|caso concreto|Kubernetes|optimizados para exactitud" S` y verificar que no quedan afirmaciones no respaldadas de los grupos A-11/A-12/A-13/M-08/M-09/M-12.
- [x] 9.2 Verificar la completitud de la Tabla 5: `rg -n "tab:api|no exhaustiva|auth|clasificaciones" S/05-arquitectura.tex`.
- [ ] 9.3 Recompilar `main.pdf` en Overleaf (`main.tex`, XeLaTeX): sin errores fatales y con los Capitulos 5-6 reflejando las correcciones.
- [x] 9.4 Ejecutar `openspec validate c-94-tesis-implementacion-verificabilidad --strict` y confirmar que pasa sin errores.
- [x] 9.5 Residuo de A-11 en §4 (seguimiento): reformular `S/04-marco-metodologico.tex:57` que aun afirmaba «(b) pruebas de integración del flujo N8N orientadas a verificar el comportamiento extremo a extremo de cada canal» —la misma afirmacion no verificable retraida en §6.7 por A-11— para describir lo que existe: pruebas de integración de la API y de la base de datos, junto con pruebas estructurales que validan `n8n/workflow.json`, en coherencia con §6.7. Verificacion: `rg -n "extremo a extremo|flujo N8N" S/04-marco-metodologico.tex` sin la afirmacion retirada. Antes: «(b)~pruebas de integración del flujo N8N orientadas a verificar el comportamiento extremo a extremo de cada canal, y (c)~pruebas de aceptacion simuladas»; despues: «(b)~pruebas de integración de la API y de la base de datos, junto con pruebas estructurales que validan el archivo \texttt{n8n/workflow.json}, y (c)~pruebas de aceptacion simuladas».

## 10. Coherencia del nombre del modelo en el cuerpo (M-NUEVO / P2-R3)

- [x] 10.1 Verificar la fuente de verdad del identificador antes de editar: leer `App/Backend/app/config/settings.py:78` (`gemini_model: str = "gemini-3.6-flash"`), `App/Backend/.env.example:13`, `README.md:315` y `docs/anexo_h_prompt_gemini.md`; registrar el valor `gemini-3.6-flash` y confirmar que las cuatro fuentes coinciden. Verificacion: `rg -n "gemini_model|gemini-3\.6-flash" App/Backend/app/config/settings.py App/Backend/.env.example README.md docs/anexo_h_prompt_gemini.md` sin discrepancias. Confirmado: las cuatro fuentes coinciden en `gemini-3.6-flash` (README en prosa: «Google Gemini 3.6 Flash»).
- [x] 10.2 Sustituir «Gemini 2.5 Flash» / «Gemini~2.5» por `gemini-3.6-flash` en `S/00-resumen.tex` (l. 9 y 23), `S/05-arquitectura.tex` (l. 23, 50, 54, 58) y `S/06-implementacion.tex` (l. 10). Coordinar con 6.1 en `05-arquitectura.tex:50` (misma linea de M-12) y con c-76 en `05-arquitectura.tex:58` (linea ya tocada por su tarea 10.1, completada). Verificacion: `rg -n "Gemini[ ~]*2\.5" S/00-resumen.tex S/05-arquitectura.tex S/06-implementacion.tex` sin coincidencias. Hecho: prosa «Gemini 3.6 Flash»; id exacto `\texttt{gemini-3.6-flash}` en los pasajes tecnicos (`05-arquitectura.tex:65` cliente google-genai, `06-implementacion.tex:10` versiones). Las lineas reales del HEAD difieren de las anotadas (05: 24/65/69/73; 06: 10).
- [x] 10.3 Sustituir «Gemini 2.5 Flash» / «Gemini~2.5» por `gemini-3.6-flash` en `S/08-discusion.tex` (l. 34 y 46), `S/09-conclusiones.tex` (l. 6), `S/10-recomendaciones.tex` (l. 32), `S/11-aspectos-legales.tex` (l. 16) y `S/12-anexos.tex` (l. 10). Verificacion: `rg -n "Gemini[ ~]*2\.5" S/08-discusion.tex S/09-conclusiones.tex S/10-recomendaciones.tex S/11-aspectos-legales.tex S/12-anexos.tex` sin coincidencias. Hecho: prosa «Gemini 3.6 Flash» (lineas reales: 08 → 38/50).
- [x] 10.4 Verificar que el cuerpo no conserva el identificador obsoleto y que no se duplico el alcance de c-76: ejecutar `rg -n "Gemini[ ~]*2\.5" S` (debe dar cero) y `rg -n "gemini-3\.6-flash" S/00-resumen.tex S/05-arquitectura.tex S/06-implementacion.tex S/08-discusion.tex S/09-conclusiones.tex S/10-recomendaciones.tex S/11-aspectos-legales.tex S/12-anexos.tex`; confirmar que `S/01-introduccion.tex` y `docs/anexo_h_prompt_gemini.md` no se tocaron. Verificacion: cero «Gemini 2.5» en el cuerpo y constancia de que §1.6/Anexo H siguen siendo de c-76. Confirmado: barrido obsoleto = 0; forma nueva presente en los ocho archivos; `01-introduccion.tex` y `anexo_h` sin coincidencias obsoletas (c-76).
- [ ] 10.5 Recompilar `main.pdf` en Overleaf (XeLaTeX) con las sustituciones de M-NUEVO; si el grupo 10 se aplica despues de 9.3, repetir la recompilacion y confirmar que no hay errores fatales. Verificacion: PDF recompilado y sin errores fatales en el log. DIFERIDO: se recompila en Overleaf (XeLaTeX).
