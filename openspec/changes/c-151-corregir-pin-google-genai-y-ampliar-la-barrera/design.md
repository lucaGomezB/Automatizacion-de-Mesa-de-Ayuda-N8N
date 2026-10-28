## Context

La barrera `scripts/preflight/docs_stack_sync.py` ejecuta 17 chequeos estaticos sobre artefactos del repositorio (c-145, ampliada por c-148 y c-149). El chequeo 17 (_check_versiones_componentes*) deriva de `App/Backend/requirements.txt` y de `docker-compose.yml` las versiones de FastAPI, Uvicorn, `google-genai` y N8N, y las compara contra lo declarado en la base de conocimiento; pero su superficie es solo `_leer_superficie_kb(kb_dir)`, es decir `knowledge-base/**`. El material de referencia (`DOCS_REFERENCIA = (docs/parameters_gemini.md, docs/n8n-workflow-guide.md)`) ya existe y lo consumen los chequeos 13, 14 y 15 via `_archivos_superficie(kb_dir, referencia_paths)`, pero el chequeo 17 no lo incluye.

Consecuencia verificada: `docs/parameters_gemini.md` declara `google-genai >=2.31,<3` en la linea 5 (seccion `## Invocación de API`, valor vigente) y en la linea 101 (nota de valor vigente dentro de `## Historial de Cambios`), mientras el pin es `>=2.33.0,<3`. La barrera imprime 17/17 PASS porque nunca compara esas lineas. Ver `proposal.md` para la motivacion.

Dos hechos del material de referencia condicionan el alcance:

- La linea 101 esta bajo el encabezado `## Historial de Cambios (registro historico; ...)`, que `_lineas_con_marcador` reconoce como marcador historico (`historico`, `antecedentes`): la linea ya queda exenta. La linea 5, en cambio, esta bajo `## Invocación de API`, sin marcador: es la que la barrera ampliada reportaria.
- `docs/n8n-workflow-guide.md:767` cita `N8N 2.25.7` dentro de "Resultados de verificación ... (2026-06-11, C-05)", un registro historico que NO lleva marcador reconocido (`verificación` no esta en `MARCADORES_HISTORICOS`). Si el chequeo 17 ampliara TODO su barrido al material de referencia, esa linea produciria un FAIL ajeno al change.

## Goals / Non-Goals

**Goals:**

- Corregir los dos pasajes vigentes de `docs/parameters_gemini.md` (lineas 5 y 101) a `google-genai >=2.33,<3`, conservando el registro historico.
- Ampliar la COMPARACION de la restriccion de `google-genai` del chequeo 17 para que su superficie incluya `DOCS_REFERENCIA`, reutilizando los helpers y la regla de exencion historica existentes.
- Desarrollar la ampliacion con TDD estricto: RED (test que falla con `2.31` en un pasaje no historico) -> GREEN (implementacion) -> triangulacion (pasa con `2.33`, falla con `2.31`; exencion historica).
- Mantener la barrera en 17/17 PASS sobre el arbol corregido.

**Non-Goals:**

- No se agrega un chequeo 18 (los 17 chequeos se conservan); la ampliacion es de superficie, no de cardinalidad.
- No se amplian los barridos de N8N, FastAPI ni Uvicorn al material de referencia; quedan sobre `knowledge-base/**`. En particular NO se abre la discrepancia `n8n-workflow-guide.md:767`.
- No se toca `App/Backend/requirements.txt` (el pin ya es `>=2.33.0,<3`), `openspec/config.yaml`, `knowledge-base/**`, el modelo `gemini-3.6-flash`, los parametros de inferencia ni las cinco cadenas de categoria.
- No se reescribe el registro historico de `parameters_gemini.md`; la correccion de la linea 101 consiste en actualizar la restriccion vigente que la nota cita, sin alterar el sentido historico del encabezado.

## Decisions

**D1 — Corregir ambas ocurrencias vigentes (lineas 5 y 101).** La linea 5 es una declaracion de valor vigente ("Versión de cliente"); tras la ampliacion seria la que dispara el FAIL si quedara en `2.31`. La linea 101 cita explicitamente "El valor vigente es ... `google-genai >=2.31,<3`", por lo que tambien es un valor vigente embebido en una seccion historica. Corregir solo una deja el residuo. Alternativa descartada: corregir solo la 101 (como enunciaba el pedido original); la barrera ampliada habria fallado por la linea 5.

**D2 — Ampliar solo la restriccion de `google-genai`, no todo el barrido.** El chequeo 17 agrupa cuatro comparaciones (N8N, FastAPI, Uvicorn, `google-genai`). Se amplia a `_archivos_superficie` unicamente el bucle de `_restricciones_genai_en_linea`; los otros tres siguen iterando `_leer_superficie_kb(kb_dir)`. Razon: la resolución del residual es de `google-genai`, y ampliar el resto arrastraria `n8n-workflow-guide.md:767` (`N8N 2.25.7`), una discrepancia preexistente y ajena. Alternativa descartada: ampliar todo el chequeo a `_archivos_superficie`; introduciria un FAIL no relacionado y obligaria a resolver o rotular la linea 767 dentro de este change, ampliando su alcance sin necesidad.

**D3 — Reutilizar los helpers y la regla de exencion.** La implementacion usa `_restricciones_genai_en_linea(linea)` y `_restriccion_compatible(restriccion, genai_req)` (ya probados por los tests del chequeo 17) y `_lineas_con_marcador(ruta)`, que exime por encabezado historico. No se introduce logica nueva de parseo. El valor esperado (`genai_req`) se sigue derivando de `requirements.txt` en tiempo de ejecucion; no se hardcodea `2.33`. Alternativa descartada: un comparador ad-hoc para el material de referencia; duplicaria logica y podria divergir del que usa la KB.

**D4 — Estructura del codigo: un unico helper de barrido con superficie parametrizable.** Para no duplicar el bucle de `google-genai`, se extrae el escaneo de la restriccion a una funcion pura que recibe la lista de rutas (`_restricciones_genai_no_compatibles(rutas, genai_req)` o equivalente), invocada dos veces: una con `_leer_superficie_kb(kb_dir)` y otra con los `referencia_paths`. Alternativa descartada: un segundo bloque de codigo casi identico; el proyecto prefiere funciones puras y sin duplicacion (skill python-design-patterns).

**D5 — TDD sobre el arbol sintetico de la suite.** La suite es hermética (c-149): su fixture `docs/parameters_gemini.md` actual solo declara modelo y timeout, sin restriccion de `google-genai`. El test RED debe (a) escribir/inyectar una linea `google-genai >=2.31,<3` sin rotulacion historica en el fixture y verificar que el chequeo 17 falla nombrando `parameters_gemini.md`, y (b) verificar que con `>=2.33,<3` (o bajo un encabezado historico) pasa. Se puede mutar el arbol con el helper existente `_mutar` o extender `_contenido_arbol` para emitir la restriccion. Alternativa descartada: probar contra el archivo real; rompe la hermeticidad que exige DOC-005.

## Risks / Trade-offs

- **[La ampliacion abre una discrepancia ajena en el material de referencia]** -> Mitigado por D2: solo se amplia el barrido de `google-genai`; `n8n-workflow-guide.md:767` (`N8N 2.25.7`) queda fuera del alcance y no produce FAIL.
- **[La correccion de la linea 101 se interpreta como reescritura del registro historico]** -> Mitigado: se conserva el encabezado y el texto historico; solo se actualiza la restriccion vigente que la nota cita, coherente con la nota de c-148/c-149 sobre hechos vigentes vs historicos.
- **[Falso positivo por el pasaje historico]** -> Mitigado: `_lineas_con_marcador` exime la linea 101 por el encabezado "Historial de Cambios"; el test de triangulacion fija esa propiedad (una restriccion bajo un encabezado con marcador no falla).
- **[Duplicacion del bucle de `google-genai` en el chequeo]** -> Mitigado por D4: un helper puro parametrizado por superficie.
- **[El fixture sintetico no refleja el archivo real corregido]** -> Aceptado: la suite verifica la LOGICA del chequeo; la verificacion del arbol real la hace el CLI `python3 scripts/preflight/docs_stack_sync.py`, que corre en CI.

## Migration Plan

1. Bloque B (RED): agregar en `scripts/preflight/test_docs_stack_sync.py` el test que falla al declarar `google-genai >=2.31,<3` en un pasaje no historico de `parameters_gemini.md` del fixture. Registrar la RED (`python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q`).
2. Bloque B (GREEN): implementar en `scripts/preflight/docs_stack_sync.py` la ampliacion de la superficie de la comparacion de `google-genai` (D2/D4). El test RED pasa; la suite completa sigue verde.
3. Bloque B (TRIANGULATE): agregar casos que (a) pasan con `>=2.33,<3`, (b) eximen la restriccion cuando su encabezado es historico, y (c) confirman que los chequeos de N8N no se amplian al material de referencia.
4. Bloque A: corregir `docs/parameters_gemini.md` lineas 5 y 101 a `google-genai >=2.33,<3`.
5. Verificar `python3 scripts/preflight/docs_stack_sync.py` -> 17/17 PASS, exit 0.

Rollback: `git revert` de los commits del change; no hay tag ni release.

## Open Questions

- Ninguna que bloquee la implementacion. La decision de no ampliar los barridos de N8N/FastAPI/Uvicorn (D2) queda explicitamente fuera de alcance; si mas adelante se quisiera cubrir el material de referencia completo, exigiria rotular o corregir `docs/n8n-workflow-guide.md:767` en un change aparte.
