# Tareas — c-162-propagar-el-contacto-del-reportante-en-el-flujo-n8n

> Strict TDD: cada bloque de logica sigue RED -> GREEN -> TRIANGULATE -> REFACTOR.
> Governance: MEDIA/ALTA (toca `n8n/` y el comportamiento entregado; implica release v1.2.6
> que el orquestador publica despues — este change solo deja la nota).
> No se modifica `App/Backend/app/**`: schema y resolver ya soportan el contrato.

## 0. Prerequisitos y baseline

- [x] 0.1 Confirmar que `resolver_reportante` ya consume `reportante_email`/`reportante_telefono` y que el modelo solo persiste `reportante_empleado_id`. Verificacion: `incidentes.py:207-238` resuelve por telefono/email; `models/incidente.py:136` persiste solo `reportante_empleado_id`; `App/Backend/app/**` sin cambios.
- [x] 0.2 Registrar el baseline offline: `cd App/Backend; pytest -m "not integration" -q` sin fallos preexistentes. Verificacion: baseline **1580 passed**, 60 deselected, 1 xfailed.
- [x] 0.3 Ejecutar la safety-net de los archivos a tocar: `pytest tests/test_n8n_workflow.py tests/test_c135_n8n_retry_policy.py -q`. Verificacion: **185 passed, 1 xfailed** (baseline en verde, sin fallos preexistentes).
- [x] 0.4 Registrar OQ-A (RESUELTA): el canal web queda FUERA de alcance y se declara (no envia contacto). Verificacion: design.md Decision 3 y requirement N8N-CONTACT-001 (delta spec).

## 1. Tests estructurales (RED)

- [x] 1.1 RED: agregar en `App/Backend/tests/test_n8n_workflow.py` un test que exija `reportante_email` y `reportante_telefono` en el `jsonBody` de `HTTP POST a MESA-AYUDAS` (via `http_json_body`), resueltos por expresion. Verificacion: `test_c162_post_body_includes_reportante_contact` fallo (RED) antes de editar el JSON.
- [x] 1.2 RED: test de alcance por canal — el normalizador emite `reportante_email` desde `remitente` (correo) y `reportante_telefono` desde `caller_number` (telefonia), `null` en el resto. Verificacion: `test_c162_normalizer_emits_reportante_contact_by_channel` (ejecucion real con Node) fallo (RED) antes del cambio del normalizador.
- [x] 1.3 RED: test null-safe — el `jsonBody` resuelve cada campo con fallback (`|| null`). Verificacion: `test_c162_post_body_contact_is_null_safe` fallo (RED) con el `jsonBody` actual.
- [x] 1.4 TRIANGULATE: test que niega que el contacto crudo `remitente` aparezca en el body/auditoria (no regresion de N8N-EMAIL-002 ajustado). Verificacion: `test_c162_normalizer_contact_null_for_web_and_unresolved` + `test_c162_raw_remitente_still_absent_from_post_body`; el nombre `reportante_email` no contiene `remitente`; test C-40 de no contaminacion en verde.

## 2. Implementacion del workflow (GREEN)

- [x] 2.1 RED->GREEN: en `n8n/workflow.json`, el normalizador emite `reportante_email` (correo, desde `remitenteNorm.remitente`) y `reportante_telefono` (telefonia, desde `item.json.caller_number`), `null` en el resto. Verificacion: test 1.2 en verde.
- [x] 2.2 RED->GREEN: agregar `reportante_email` y `reportante_telefono` al `jsonBody` de `HTTP POST a MESA-AYUDAS`, resueltos por expresion desde `$('Normalizar entrada del incidente')...` con `|| null`; mantener la forma de expresion unica `={{ JSON.stringify({...}) }}`. Verificacion: tests 1.1 y 1.3 en verde; `test_n8n_workflow.py::http_json_body` intacto.
- [x] 2.3 REFACTOR: reescribir el comentario C-40/C-53 del normalizador para declarar el supersede (el contacto SI viaja al POST para resolucion; NO se persiste crudo ni se audita). Verificacion: el comentario ya no afirma "NO se agrega al POST"; tests siguen en verde.

## 3. Verificacion de tests y suite

- [x] 3.1 Revisar `App/Backend/tests/test_c135_n8n_retry_policy.py`: confirmar que sigue en verde (afirma `origen_message_id` y la referencia al normalizador). Extender solo si aporta valor sin debilitar la asercion de idempotencia. Verificacion: el archivo pasa (190 passed, 1 xfailed junto a `test_n8n_workflow.py`); decision: no se extiende (la propagacion de contacto no toca la idempotencia por `origen_message_id`); solo se actualizo el numero citado en su docstring (171 -> 176).
- [x] 3.2 Correr el subset offline completo: `cd App/Backend; pytest -m "not integration" -q`. Verificacion: **1585 passed**, 60 deselected, 1 xfailed (baseline 1580 + 5 nuevas). Sin fallos nuevos.

## 4. Documentacion

- [x] 4.1 Actualizar `docs/n8n-workflow-guide.md`, seccion "Payload enriquecido del POST": documentar `reportante_email` y `reportante_telefono` (resolucion de reportante, c-82/VIS-005; correo/telefonia; web fuera de alcance; transitorio, no persistido ni auditado). Verificacion: grep de ambos campos en la guia (lineas 136 y 139) y conteo actualizado a 176.
- [x] 4.2 Actualizar la tabla `tab:configuracion-evaluada-entregada` en `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`: agregar/annotizar la fila de propagacion del contacto del reportante como capacidad de la version entregada posterior a la campaña. Verificacion: la tabla menciona `reportante_email`/`reportante_telefono` y c-162 (fila "Propagacion del contacto del reportante en el POST").
- [x] 4.3 Registrar en `docs/Tesis/Correcciones/dictamen-correcciones.md`: el cierre de OQ5 (procedencia/contacto del reportante) y el supersede parcial de C-40/C-53 por c-162. Verificacion: seccion "Dictamen v10 / v1.2.6 (2026-10-29) - c-162" con "Cierre de OQ5" y "Supersede parcial de C-40/C-53"; OQ5 tambien marcado resuelto en `preguntas-para-lucas-dictamen-2026-10-28.md`.
- [x] 4.4 Retirar/actualizar el texto que afirma que el flujo entregado NO envia el contacto (entrada de "Datos que requieren a los autores" del dictamen). Verificacion: el item (a) pasa a "[RESUELTO por c-162]" y declara que el flujo SI envia el contacto; sin afirmacion vigente de que el POST omite el contacto.

## 5. Release y cierre

- [x] 5.1 Dejar la nota de release v1.2.6 (planificada) en el registro del dictamen, SIN publicarla. Verificacion: seccion "Release" del tramo c-162 anota v1.2.6 como release que incluye c-162, sin tag ni commit creados.
- [x] 5.2 `openspec validate c-162-propagar-el-contacto-del-reportante-en-el-flujo-n8n --strict --no-interactive`. Verificacion: "Change 'c-162-...' is valid".
- [x] 5.3 Verificacion final del contrato: un correo/telefonia de empleado del directorio resuelve reportante y no deriva por VIS-005. Verificacion: cobertura API-level ya existente en `tests/test_reporter_link.py` (11 pruebas) + asercion estructural del body (`test_c162_post_body_includes_reportante_contact`).
