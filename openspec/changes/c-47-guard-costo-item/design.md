## Context

Ver `proposal.md — Why`. Restricciones verificadas que moldean el enfoque:

- `Guard de costo` (`n8n/workflow.json:799`) es un `n8n-nodes-base.httpRequest` (typeVersion 4.4) cuyo body llama a `POST {{ $env.BACKEND_URL }}/api/v1/cost-guard/reserve` con `provider="n8n_gemini"` y `caller`. La salida de un `httpRequest` es el cuerpo de la respuesta del backend; el item de entrada NO se propaga.
- Cableado actual: `Sellar ingreso telefonia` → `Guard de costo`; `Guard de costo` main[0] → `Guard permite?`; `Guard de costo` main[1] (error, `onError: continueErrorOutput`) → `Derivar a revision humana`; `Guard permite?` main[0] (true) → `AI Agent`; main[1] (false) → `Derivar a revision humana`.
- El `AI Agent` (`workflow.json:196-210`) interpola en su prompt `{{ $json.transcript || $json.body || $json.descripcion || $json.text || '' }}`. Como su item de entrada es la respuesta de la guarda (`{allowed: ...}`), pierde el item sellado completo. Nota de alcance: el payload del trigger `call-summary.complete` no expone ninguno de esos campos (limitación heredada de C-45); C-47 corrige la pérdida del item a través de la guarda, no la ausencia del campo de transcripción.
- El item sellado que produce `Sellar ingreso telefonia` es `{...item.json del trigger, ingresado_en}` y es exactamente el item que entra al nodo de guarda (conexión directa), por lo que su recuperación es determinista.
- El body de la guarda usa `$('Sellar ingreso telefonia').item.json.From` (`workflow.json:779`), patrón idéntico al que C-46 corrigió con `.first()` en el validador y el terminal.
- C-46 ya dejó `Derivar a revision humana` recuperando `$('Sellar ingreso telefonia').first()` y marcando `ingreso_sellado_ausente` + `revision_forzada` + `requiere_revision_humana` ante sello ausente. C-47 NO debe regresar ese comportamiento.
- La suite `App/Backend/tests/test_n8n_workflow.py` es ESTRUCTURAL (inspecciona el JSON, no ejecuta N8N). No existe harness de runtime N8N en CI. `test_c40_guide_test_count_matches_suite` exige que el conteo declarado en `docs/n8n-workflow-guide.md` coincida con el número de funciones `test_` de la suite.

## Goals / Non-Goals

**Goals:**

- Que el `AI Agent` del canal de telefonía vuelva a recibir el item sellado completo (no solo el cuerpo de la guarda) aunque el flujo pase por `Guard de costo`.
- Que `Guard permite?` conserve la decisión `allowed` de la guarda y su ruteo verdadero/falso no cambie.
- Reemplazar la referencia frágil `.item` del `caller` por la referencia al item corriente del propio nodo (`$json.From || $json.from`), eliminando la dependencia de `pairedItem` sin introducir una referencia cruzada entre nodos.
- Preservar el comportamiento N8N-TIMING-003 de C-46 en el terminal y cubrirlo con una prueba de no regresión.
- Dejar la corrección cubierta por pruebas estructurales que distingan el item restaurado del cuerpo de la guarda.

**Non-Goals:**

- No cambiar la semántica de costo (monto, ventana, rate, costos unitarios, fail-closed, política de degradación) ni el contrato o el código del backend.
- No modificar el nodo terminal `Derivar a revision humana` ni el validador `Se verifica lo que trajo la IA` (C-46), solo verificarlos.
- No agregar un harness de runtime N8N ni invocar servicios pagos reales.
- No tocar `IncidenteListItem` (c-48), ni la carga/cableado del corpus (c-49/c-50).
- No cablear la fuente real de la transcripción de Twilio ni modificar el trigger: el payload de `call-summary.complete` no expone un campo de transcripción/descripción (limitación heredada de C-45), y resolverlo se rastrea en un change aparte. C-47 solo garantiza la propagación del item sellado a través de la guarda.

## Decisions

### D1: Nodo `code` de restauración entre `Guard de costo` y `Guard permite?`

Se intercala un nodo `n8n-nodes-base.code` cuya `jsCode` recupera el item sellado con `$('Sellar ingreso telefonia').first().json`, lee la decisión de la guarda del item corriente (`$input.item.json.allowed`) y devuelve `{...sellado, allowed}`. El nodo de restauración se cablea `Guard de costo` main[0] → restauración → `Guard permite?`. Resultado: el IF conserva su condición `$json.allowed`, la rama verdadera entrega al `AI Agent` el item sellado (no solo el cuerpo de la guarda), y la rama falsa entrega a `Derivar a revision humana` el item con contenido (el terminal además vuelve a fusionar el sello, de forma idempotente).

Se elige colocar la restauración ANTES del IF (no solo en la rama verdadera) porque un único nodo beneficia a ambas ramas, mantiene `allowed` explícito para el ruteo y evita duplicar la restauración.

- Alternativa considerada: incrustar la restauración solo entre `Guard permite?` (true) y `AI Agent`. Se descarta: duplica la necesidad en la rama denegada y deja la decisión de la guarda expuesta a la fragilidad del item de respuesta.
- Alternativa considerada: configurar el `httpRequest` para que incluya los campos de entrada. Se descarta: el nodo HTTP no ofrece una opción confiable de "incluir item de entrada"; la respuesta sigue siendo el cuerpo del backend.
- Alternativa considerada: cambiar el prompt del `AI Agent` para que referencie el nodo sellador directamente (`$('Sellar ingreso telefonia').first().json.transcript`). Se descarta: no preserva el item a través de la guarda —solo parchea un campo— y deja al agente sin el resto del payload; la preservación del item es la corrección semántica.
- Alternativa considerada: mover la guarda después del `AI Agent`. Se descarta: deja de prevenir el gasto pago, que es el propósito de C-45.
- Alternativa considerada: que el backend devuelva el item original en su respuesta. Se descarta: cambia el contrato de `/reserve` y la política de la guarda (gobernanza ALTO de C-45), fuera del alcance MEDIO de C-47.

### D2: `caller` desde el item corriente (`$json`) en el body de la guarda

El body del nodo pasa a `={{ $json.From || $json.from || null }}`, reemplazando ambas apariciones de `$('Sellar ingreso telefonia').item`. La conexión verificada `Sellar ingreso telefonia` → `Guard de costo` es directa, así que el item de entrada del `httpRequest` YA es el item sellado: la expresión resuelve desde el item corriente sin ninguna referencia cruzada entre nodos y sin posibilidad de lanzar. Esto elimina la dependencia de `pairedItem` que C-46 ya corrigió en el validador y el terminal, con la expresión más simple posible. Nota: en la práctica el payload de `call-summary.complete` anida el número llamante dentro del campo `data` stringificado, por lo que `caller` resuelve `null`; el spec lo contempla como campo opcional y la reserva no aborta. Extraer el `caller` real del payload se rastrea junto con la transcripción en el change aparte.

`caller` es opcional; cuando `From`/`from` faltan, la expresión resuelve `null` y la reserva continúa sin abortar el flujo.

- Alternativa considerada: `$('Sellar ingreso telefonia').first()`, el patrón que C-46 estableció aguas abajo. Se descarta como decisión principal para el body de la guarda: introduce una referencia cruzada innecesaria (el input ya es el sello) y puede lanzar si el nodo no produjo salida, sin aportar nada que `$json` no tenga. Sigue siendo el patrón correcto —y obligatorio— en el nodo de restauración de D1, cuyo item de entrada sí es la respuesta de la guarda.
- Alternativa considerada: mantener `.item` y confiar en `|| null`. Se descarta: reproduce la fragilidad de `pairedItem` que C-46 ya eliminó.

### D3: Sin cambios en `Derivar a revision humana` y en el validador; prueba de no regresión

C-47 NO edita el `jsCode` del terminal ni del validador. La restauración de D1 es idempotente con la recuperación propia del terminal (`...sellado, ...item`), así que no hay conflicto. Se agrega una prueba estructural que exige que el terminal siga referenciando `$('Sellar ingreso telefonia').first()` y emitiendo el WARN `ingreso_sellado_ausente`, de modo que una edición futura no regrese N8N-TIMING-003.

- Alternativa considerada: eliminar la recuperación interna del terminal ahora que la restauración ocurre aguas arriba. Se descarta: el terminal también recibe la rama de error de la guarda (que NO pasa por la restauración) y el tope de refinamiento; su recuperación propia sigue siendo necesaria.

### D4: Semántica de costo y backend intactos

No se modifica el endpoint `/api/v1/cost-guard/reserve`, ni `provider`, ni el header `X-Cost-Guard-Secret`, ni la configuración de la guarda, ni `App/Backend/app/`. El cambio es exclusivamente de propagación de items y de referencia de expresión en `n8n/workflow.json`. `runtime-cost-guard` no cambia.

### D5: Pruebas estructurales extendidas y guía sincronizada

Se extienden las pruebas de `test_n8n_workflow.py` (las de C-46 usan `load_workflow`, `index_nodes`, `_js_code`, `_active_js_code`, `_connections_reachable`): (a) existe un nodo de restauración entre `Guard de costo` y `Guard permite?` cuyo código referencia `$('Sellar ingreso telefonia').first()`; (b) el body de `Guard de costo` resuelve `caller` desde `$json` y NO referencia `$('Sellar ingreso telefonia')`; (c) el `AI Agent` es alcanzable desde el nodo de restauración y su item de entrada proviene del sello (el test verifica alcanzabilidad y procedencia del item, NO que el prompt resuelva un campo de descripción no vacío — esa ausencia es la limitación heredada de C-45); (d) el terminal de C-46 no regresó. `docs/n8n-workflow-guide.md` documenta la restauración y se actualiza el conteo declarado de propiedades estructurales.

Impacto no anticipado en `test_runtime_cost_guard.py`: su test `test_workflow_guarda_de_costo_entrega_al_ai_agent_y_deriva_al_denegar` (C-45) afirmaba que `Guard permite?` es sucesor DIRECTO de `Guard de costo`. Al intercalarse el nodo de restauración (D1), ese edge directo deja de existir y no hay cableado válido que lo conserve. Se aplica la adaptación mínima: el assert acepta el edge a través de `Restaurar item telefonia` y se conservan intactas las assertions de salida del IF (true → `AI Agent`, false → `Derivar a revision humana`). No se debilita el intento semántico del test ni se toca código de producto.

- Alternativa considerada: un test de runtime con N8N efímero. Se descarta: no existe harness, e invocar el agente pago tendría costo real.

## Risks / Trade-offs

- La fusión `{...sellado, allowed}` podría colisionar con campos del sello → Mitigación: el spread del sello va primero y `allowed` se fija explícitamente; la prueba (b)/(c) verifica el ruteo.
- Regresión de C-46 al editar el mismo grafo → Mitigación: no se toca el terminal; prueba de no regresión dedicada.
- Verificación estructural, no runtime → Mitigación: la restauración es determinista (conexión directa) y la verificación en vivo se documenta como obligatoria; `caller` resuelve desde `$json` sin poder lanzar, y el nodo de restauración conserva el fail-closed respecto del gasto por la salida de error de la guarda.
- Desincronización del conteo de pruebas declarado en la guía → Mitigación: actualizar `docs/n8n-workflow-guide.md` en la misma tarea; `test_c40_guide_test_count_matches_suite` lo detecta.
- Solapamiento de diffs con C-46 en el terminal → Mitigación: C-47 no edita ese nodo; revisar el diff al integrar.

## Migration Plan

1. Editar `n8n/workflow.json`: agregar el nodo de restauración, re-cablear `Guard de costo` → restauración → `Guard permite?`, y cambiar el `caller` del body a `$json.From || $json.from`.
2. Extender `App/Backend/tests/test_n8n_workflow.py` (RED antes, GREEN después con la suite estructural offline).
3. Actualizar `docs/n8n-workflow-guide.md` (restauración del item + conteo declarado).
4. Rollback: revertir el commit restaura el cableado directo `Guard de costo` → `Guard permite?`, elimina el nodo de restauración y devuelve `.item` en el body. No hay migración de datos ni cambio de backend. Reiniciar N8N re-importando el `workflow.json` revierte el comportamiento en runtime.

## Open Questions

- El nombre del campo interno que transporte la decisión de la guarda al item restaurado (`allowed` se conserva por compatibilidad con `Guard permite?`; cualquier campo adicional de observabilidad, p. ej. `guard_cause`, se decide en apply) no afecta specs, alcance ni tareas.