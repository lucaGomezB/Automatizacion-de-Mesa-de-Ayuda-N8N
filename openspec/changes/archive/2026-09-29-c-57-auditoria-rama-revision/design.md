# Design: Auditoría correcta en la rama de revisión humana

## Context

Ver `proposal.md` — Why. Estado actual verificado en `n8n/workflow.json`:

Aristas relevantes:
- `HTTP POST a MESA-AYUDAS[main#0] -> Requiere revision humana`
- `Requiere revision humana[main#0] -> [Notificar operador designado, Es correo?, Confirmar correo en revision?]`
- `Requiere revision humana[main#1] -> [Rutear por canal de origen, Registro de auditoria]`
- `Notificar operador designado[main#0] -> Registro de auditoria`
- `Entrada valida[main#1] -> [Registro de auditoria, Es correo?]`
- `HTTP POST a MESA-AYUDAS[main#1] -> [Es correo?, Registro de auditoria]`

El `jsCode` de `Registro de auditoria` deriva el resultado así:

```
resultado = item.resultado
  || (item.error ? 'error_backend'
      : (item.es_valido === false ? 'rechazado_datos_incompletos'
          : (typeof item.id === 'number' ? 'creado' : 'rechazado_datos_incompletos')));
incidente_id = item.id || null;
```

Con la respuesta del POST (id numérico) el código ya produce `creado`; con el normalizador (`es_valido=false`) produce `rechazado_datos_incompletos`; con el item de error produce `error_backend`. **La lógica es correcta; el defecto es qué item llega.** En la rama de revisión la única entrada de la auditoría es `Notificar operador designado`, cuyo item es el resultado SMTP (sin `id`), por lo que cae al fallback.

## Goals / Non-Goals

**Goals:**
- Que la auditoría registre el resultado correcto por rama: `creado` (con `incidente_id` numérico) en éxito —incluida la revisión humana—, `rechazado_datos_incompletos` en rechazo y `error_backend` en error del backend.
- Que la auditoría de la rama de revisión consuma la respuesta del POST y no el resultado SMTP.
- Fijar la topología con tests estructurales y sincronizar la guía.

**Non-Goals:**
- Cambiar el contrato del backend ni el `jsCode` de auditoría (la lógica ya es correcta con la entrada correcta).
- La descripción obsoleta del catálogo `canal_origen` id 1 y las menciones a Outlook en el spec main (follow-up separado, ver proposal).
- La lógica de destinatarios de la notificación (c-56) y el ciclo de correo (c-55).

## Decisions

### D1 — Arreglar el cableado (opción a) en lugar del `jsCode` (opción b)

| Opción | Trade-off | Decisión |
|--------|-----------|----------|
| (a) Rewire: `Requiere revision humana[main#0] -> Registro de auditoria` y quitar `Notificar operador designado -> Registro de auditoria` | El item de entrada pasa a ser el correcto por construcción; sin código defensivo; requiere ajustar 2 tests y 2 requisitos que codificaban el orden notificación→auditoría | **Elegida** |
| (b) Que el `jsCode` lea `$('HTTP POST a MESA-AYUDAS')` con guardas `isExecuted`/try-catch | No toca la topología ni los requisitos, pero conserva un flujo de datos incorrecto y compensa con una referencia cruzada frágil (pairedItem roto desde la salida de error y desde la notificación) | Rechazada |
| (c) Mantener ambas aristas gate→auditoría y notificación→auditoría | La auditoría correría dos veces con items distintos (uno correcto, uno incorrecto) | Rechazada |

La opción (a) es la de menor superficie y mayor robustez: elimina la causa raíz (el item SMTP) en vez de compensarla, y no depende del comportamiento de salida de `emailSend` ni de la resolución de `pairedItem` entre ramas.

### D2 — Cambio exacto de cableado

En `n8n/workflow.json`, sobre las conexiones de `Requiere revision humana`:

- **Agregar** `Requiere revision humana[main#0] -> Registro de auditoria`.
- **Quitar** `Notificar operador designado[main#0] -> Registro de auditoria`.

Resultado: las cuatro entradas de la auditoría quedan:
1. `Entrada valida[main#1]` → rechazo de validación (POST no ejecutado; `es_valido=false`) → `rechazado_datos_incompletos`.
2. `HTTP POST a MESA-AYUDAS[main#1]` → salida de error del backend (`item.error`) → `error_backend`.
3. `Requiere revision humana[main#0]` → alta con revisión (response del POST, `id` numérico) → `creado`.
4. `Requiere revision humana[main#1]` → alta sin revisión (response del POST, `id` numérico) → `creado`.

Las salidas `main#0`/`main#1` de cada IF/HTTP son mutuamente excluyentes, por lo que una corrida ejecuta la auditoría exactamente una vez.

`Notificar operador designado` queda como terminal de la rama de revisión (igual que `Correo de confirmacion al usuario` en su rama). No requiere nodo sucesor: su efecto es el envío.

### D3 — Sin cambios en el `jsCode` de auditoría

Con el item correcto, el código existente ya cubre las cuatro entradas (ver Context). Se conserva su contrato `{ incidente_id, canal_origen, timestamp, sector_nombre, confianza, resultado, retencion_dias }`, su lectura de `canal_origen` desde `Normalizar entrada del incidente` (D-4) y la exclusión de PII. Único cambio permitido en el nodo: actualizar el comentario que describe las ramas de entrada. No se agregan referencias a `Notificar operador designado`.

### D4 — Auditoría en paralelo con la notificación

Al quedar hermana de `Notificar operador designado`, la auditoría se alcanza aunque la notificación falle, siempre que la ejecución no aborte: por eso se conserva `onError: continueRegularOutput` en el nodo de notificación (c-40). Se modifican los requisitos "Notificacion al operador designado" y N8N-AUDIT-003 para describir el paralelismo en lugar del encadenamiento estricto notificación→auditoría.

### D5 — Tests (Strict TDD, RED primero)

- Invertir `test_notificar_operador_reaches_audit` y `test_c40_notificar_operador_still_reaches_audit`: pasan a exigir que la auditoría **no** sea sucesora de la notificación y que sea sucesora directa de `Requiere revision humana[main#0]`.
- Agregar: la auditoría recibe la respuesta del POST en la rama de revisión; el `jsCode` de auditoría no referencia `Notificar operador designado` y conserva la distinción `creado`/`rechazado_datos_incompletos`/`error_backend`; no hay doble ejecución.
- Mantener los tests de no-regresión (`test_audit_reachable_from_success_branch`, `test_notification_does_not_block_audit`, `test_audit_reachable_from_rejected_branch`, N8N-AUDIT-002 de error).
- Actualizar el conteo de pruebas declarado en la guía (`test_c40_guide_test_count_matches_suite`).

## Risks / Trade-offs

- [Doble auditoría si se conserva la arista SMTP] → se elimina esa arista; verificación estructural de que `Notificar operador designado` no es origen de la auditoría.
- [Un fallo de notificación que aborte la ejecución] → la auditoría es hermana; se conserva `onError: continueRegularOutput`.
- [Cambios de spec percibidos como scope creep] → los dos requisitos modificados describen garantías equivalentes o más fuertes (auditoría no bloqueada por la notificación); no cambian comportamiento externo más allá del resultado auditado.
- [Conteo de pruebas de la guía] → actualizar en el mismo commit; la suite lo verifica.

## Migration / Rollout

Sin migración de datos. El workflow sigue `active=false` en el repo. Despliegue: importar el `workflow.json` actualizado en N8N y validar con un alta que dispare revisión humana. Rollback: `git revert` del commit restaura el cableado anterior.

## File Changes

| File | Acción | Descripción |
|------|--------|-------------|
| `n8n/workflow.json` | Modificar | Alta de arista `Requiere revision humana[main#0] -> Registro de auditoria`; baja de `Notificar operador designado[main#0] -> Registro de auditoria`; comentario de ramas del `jsCode` de auditoría |
| `App/Backend/tests/test_n8n_workflow.py` | Modificar | Invertir 2 aserciones; agregar tests de topología e independencia del item SMTP; sin regresión del resto |
| `docs/n8n-workflow-guide.md` | Modificar | Tablas de wiring del gate post-POST, FAQ de auditoría y conteo de pruebas |

## Testing Strategy

| Layer | Qué | Cómo |
|-------|-----|------|
| Estructural (pytest offline) | Topología gate→auditoría, ausencia de arista notificación→auditoría, independencia del item SMTP, resultados por rama | `cd App/Backend; pytest tests/test_n8n_workflow.py` |
| No regresión | Resto de la suite estructural y preflight | `pytest tests/test_n8n_workflow.py` (y `scripts/preflight` si aplica) |
| Smoke manual | Alta con `requiere_revision_humana=true` audita `creado` con id numérico | Ejecución real en N8N |

## Open Questions

- Ninguna que bloquee el diseño. El follow-up de la descripción del catálogo `canal_origen` y de las menciones a Outlook en el spec main se documenta en `proposal.md` como fuera de alcance.
