# Proposal: Propagar el contacto del reportante en el flujo N8N (c-162)

## Why

El workflow N8N entregado NO envia el contacto del reportante en `POST /api/v1/incidentes`. Como el backend resuelve al reportante contra el directorio a partir de `reportante_email` / `reportante_telefono`, TODOS los incidentes de correo y telefonia ingresados por N8N caen en revision humana por VIS-005 (c-82), sin importar la confianza de la clasificacion. La capacidad de resolver reportante ya existe en el backend; el defecto esta en el transporte.

## What Changes

- Nodo `Normalizar entrada del incidente`: emite `reportante_email` (desde `remitente`) para correo y `reportante_telefono` (desde `caller_number`) para telefonia; `null` en el canal que no corresponde.
- Nodo `HTTP POST a MESA-AYUDAS`: agrega `reportante_email` y `reportante_telefono` al `jsonBody`, resueltos por expresion desde el normalizador y null-safe (`|| null`), sin persistir el contacto crudo.
- Comentario C-40/C-53 del normalizador: se actualiza para declarar que el contacto SI viaja al POST (resolucion transitoria) aunque NO se persiste crudo ni se audita. Supersede parcial de N8N-EMAIL-002.
- Tests estructurales: `App/Backend/tests/test_n8n_workflow.py` verifica los dos campos en el POST y su alcance por canal; se revisa `test_c135_n8n_retry_policy.py`.
- Docs y tesis: `docs/n8n-workflow-guide.md` documenta los campos; tabla `tab:configuracion-evaluada-entregada` y el registro OQ5 del dictamen se actualizan.
- Nota de release v1.2.6 (planificada, NO publicada en este change).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `n8n-workflow`: la estructura normalizada propaga el contacto del reportante por canal; el POST de persistencia lo incluye; N8N-EMAIL-002 acota el MUST NOT del `remitente` a la persistencia/auditoria (no al transporte transitorio).

## Impact

| Area | Impact | Description |
|------|--------|-------------|
| `n8n/workflow.json` | Modified | Normalizador y `jsonBody` del POST |
| `App/Backend/tests/test_n8n_workflow.py` | Modified | Verificacion estructural de los campos |
| `docs/n8n-workflow-guide.md` | Modified | Seccion "Payload enriquecido del POST" |
| `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` | Modified | Tabla evaluada/entregada |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Modified | Cierre de OQ5 y supersede C-40/C-53 |
| `App/Backend/app/**` | Unchanged | Schema y resolver ya soportan el contrato |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Confundir "enviar contacto" con "persistir PII" | Med | El modelo solo guarda `reportante_empleado_id`; el contacto es transitorio. Test que niega `remitente` en body/auditoria sigue en verde |
| El canal web se mis-atribuya (auth = operador) | Med | Se acota web fuera de alcance (ver design OQ-A) |
| Regresion en la suite offline | Baja | Tests estructurales; subset SQLite en verde |

## Rollback Plan

Revertir el commit restaura el `jsonBody` anterior (sin los dos campos) y el comentario C-40/C-53. Sin migraciones ni cambios de esquema: los incidentes dejan de resolver reportante y vuelven a VIS-005, comportamiento previo. Los cambios de docs/tesis se revierten en el mismo commit.

## Dependencies

- Ninguna. c-82 (VIS-005) y el resolver `resolver_reportante` ya estan implementados; este change explota una capacidad existente.

## Success Criteria

- [ ] El POST de N8N incluye `reportante_email` y `reportante_telefono` por canal, null-safe.
- [ ] Un correo/telefonia del directorio resuelve reportante y NO deriva por VIS-005 por reportante no identificado.
- [ ] El contacto no se persiste crudo ni se escribe en auditoria; el test de no contaminacion sigue en verde.
- [ ] `openspec validate c-162-... --strict` pasa; `pytest -m "not integration"` en verde.
