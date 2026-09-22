## Context

Ver `proposal.md` — Why. El diseño se apoya en el estado verificado del workflow y del backend:

- `Sellar ingreso telefonia` (`n8n/workflow.json`) hace `...item.json, ingresado_en: new Date().toISOString()` y corre aguas arriba del `AI Agent`.
- `Se verifica lo que trajo la IA` recupera con `$('Sellar ingreso telefonia').item.json.ingresado_en || null` dentro de un `try/catch` que retorna `null` en silencio. El `item` corriente proviene del `AI Agent`, que no propaga los campos de entrada; la resolución `pairedItem` implícita en `.item` se rompe.
- `Derivar a revision humana` (salida terminal, también entrada de la rama denegada de la guarda de costo de C-45) usa el mismo patrón `.item` con `catch → {}`.
- `Normalizar entrada del incidente` propaga `ingresado_en: item.json.ingresado_en || null` y calcula `revision_forzada = item.json.revision_forzada === true` y `requiere_revision_humana = item.json.requiere_revision_humana === true || revision_forzada`.
- El IF pre-POST `Entrada valida` combina con OR `confianza >= 0.70` y `$('Normalizar...').revision_forzada == true`: una revisión forzada persiste el ticket aun con `confianza = 0.0` (mecanismo C-33).
- El backend honra `clasificacion.requiere_revision_humana` cuando es distinto de `None` (`incidente_service.py:322-325`), así que un flag explícito fuerza la revisión post-POST.
- La suite estructural (`test_n8n_workflow.py::test_c39_telefonia_preserva_ingreso_a_traves_del_agente`) sólo aserta la subcadena `"ingresado_en"`.

Restricción clave: no existe harness de runtime N8N en CI. La suite estructural es una guarda de regresión, no una prueba de ejecución.

## Goals / Non-Goals

**Goals:**

- Recuperar el sello de ingreso de telefonía de forma robusta a través del `AI Agent` sin depender de `pairedItem`.
- Garantizar que un sello irresoluble NO se silencie: WARN estructurado + revisión humana, con el ticket igualmente creado y la ejecución sin abortar.
- Dejar la corrección cubierta por pruebas estructurales que distingan `.first()` de `.item` y el fallback a revisión.

**Non-Goals:**

- No cambiar el contrato ni el código del backend (`ingresado_en` sigue nullable; el flag de revisión ya existe).
- No alterar el comportamiento existente de clasificación inválida distinto del eje del sello.
- No tocar el nodo `Guard de costo` ni el bucle de refinamiento (c-47).
- No exponer campos de tiempo en endpoints de listado (c-48) ni cablear el corpus (c-49/c-50).

## Decisions

### D1: Recuperación con `.first()` en lugar de `.item`

Tanto el validador como el terminal recuperan el sello con `$('Sellar ingreso telefonia').first().json.ingresado_en`. `.first()` resuelve el primer item de la salida del nodo referenciado sin exigir emparejamiento `pairedItem` con el item corriente; `.item` sí lo exige y por eso falla cuando el item viene del agente.

- Alternativa considerada: mantener `.item` y agregar un fallback a `.first()` sólo en el `catch`. Se descarta: deja el camino frágil como primario y agrega complejidad sin beneficio; el verificador C-39 recomendó `.first()` directo.
- Alternativa considerada: re-sellar el ingreso después del agente. Se descarta: incluiría el tiempo del agente pago dentro del sello y destruiría la medición end-to-end (excluiría el costo dominante).
- Alternativa considerada: leer el sello desde `$('Sellar ingreso telefonia').all()[0]`. Se descarta: `.first()` ya expresa esa intención y es idiomático en N8N.

### D2: Sello ausente → WARN estructurado + revisión forzada, ticket igualmente creado

La resolución vive en un `try/catch` (`.first()` puede lanzar si el nodo no produjo salida), pero el `catch` NO retorna null en silencio: marca `ingreso_sellado_ausente = true`, emite `console.warn` con un evento estructurado y fija `revision_forzada = true` y `requiere_revision_humana = true` en el item resultante, en AMBAS ramas (válida e inválida).

Efecto en el flujo: el normalizador propaga `revision_forzada = true`, el IF pre-POST `Entrada valida` se satisface por su rama OR aunque `confianza = 0.0`, el POST ocurre (ticket creado) y el backend honra `clasificacion.requiere_revision_humana = true`, de modo que el IF post-POST deriva a notificación del operador.

- Alternativa considerada: fijar sólo `requiere_revision_humana = true` sin forzar. Se descarta: con `confianza < 0.70` el IF pre-POST rutearía a la rama de revisión sin crear el ticket, violando "nunca perder el ticket".
- Alternativa considerada: dejar que el `catch` devuelva `null` y que el backend detecte el nulo. Se descarta: reproduce el silencio actual; el backend no puede distinguir un nulo legítimo de un fallo de recuperación.
- Alternativa considerada: abortar la ejecución para forzar diagnóstico. Se descarta explícitamente: perdería el ticket y el incidente.

### D3: Terminal `Derivar a revision humana` con la misma corrección

El terminal recupera el item sellado con `.first()`; si no resuelve, emite WARN y continúa fusionando el item corriente. Su salida ya fija `confianza = 0.0`, `requiere_revision_humana = true` y `revision_forzada = true`, por lo que la revisión está garantizada sin cambios adicionales.

### D4: Contrato del backend intacto

No se modifica `IncidenteCreate.ingresado_en` (nullable), ni su validador, ni `IncidenteService`, ni migraciones. El incidente creado por el fallback puede persistir `ingresado_en` nulo; la diferencia es que ahora queda marcado para revisión y con un WARN, en lugar de nulo silencioso. `latencia_e2e_ms` sigue derivándose nula cuando falta el ingreso, conforme a `e2e-timing-instrumentation`.

### D5: Pruebas estructurales extendidas (guarda de regresión, no verificación runtime)

Se extienden las pruebas de `test_n8n_workflow.py` para asertar: (a) el `jsCode` del validador y del terminal referencian `$('Sellar ingreso telefonia').first()` y NO `$('Sellar ingreso telefonia').item`; (b) el validador marca revisión forzada y emite WARN ante sello ausente; (c) el normalizador propaga `ingreso_sellado_ausente`/revisión; (d) el body del POST sigue enviando `ingresado_en` por expresión. La verificación de comportamiento real (que `.first()` resuelva en N8N y que el incidente se cree con revisión) exige una ejecución N8N en vivo, que no corre en CI.

- Alternativa considerada: un test de runtime con N8N efímero. Se descarta en este change: no existe harness, e invocar el agente pago/Gemini tendría costo real; queda como verificación manual previa a confiar en la latencia de telefonía.

## Risks / Trade-offs

- La verificación es estructural, no runtime → Mitigación: el fallback a WARN + revisión evita que un fallo de `.first()` vuelva a ser silencioso; se documenta la verificación en vivo obligatoria.
- Posible exceso de revisión humana si `.first()` falla con frecuencia → Mitigación: el ticket nunca se pierde y el WARN permite detectarlo; `.first()` es la opción recomendada por el verificador.
- Solapamiento con `c-47` en el terminal `Derivar a revision humana` → Mitigación: ambos cambios editan el mismo nodo; c-46 aplica primero la corrección de recuperación y c-47 reordena la fusión del item, sin conflicto semántico. Revisar el diff del nodo al integrar.
- Conflación de `revision_forzada` con el tope de refinamiento → Mitigación: se agrega el marcador explícito `ingreso_sellado_ausente` y `motivo_revision_forzada`, de modo que la causa queda trazada.

## Migration Plan

1. Editar `n8n/workflow.json`: corregir la recuperación en `Se verifica lo que trajo la IA` y en `Derivar a revision humana`.
2. Extender `App/Backend/tests/test_n8n_workflow.py` (RED antes, GREEN después con la suite estructural offline).
3. Actualizar `docs/n8n-workflow-guide.md` si declara conteos o el contrato de recuperación.
4. Rollback: revertir el commit restaura el patrón `.item` + `try/catch` previo; no hay migración de datos ni cambio de backend. Reiniciar N8N re-importando el `workflow.json` revierte el comportamiento en runtime.

## Open Questions

- El nombre exacto del marcador (`ingreso_sellado_ausente`) y su inclusión en el body del POST quedan a criterio de implementación; no afectan specs, alcance ni tareas, siempre que no se envíen al backend como campo desconocido. Se decide en apply.