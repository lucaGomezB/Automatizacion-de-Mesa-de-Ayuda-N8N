## Why

La capability `employee-directory` (C-54/C-60, archivados) opera hoy EXCLUSIVAMENTE con datos sinteticos (`@example.test`), almacena email y telefono en TEXTO PLANO (DIR-005), no tiene indice ciego ni un mecanismo de activacion. Activar datos personales reales esta BLOQUEADO a la espera de una aprobacion humana HIGH. Sin un endurecimiento previo, habilitar datos reales expondria PII en claro en reposo, se apoyaria en una auditoria efimera (solo structlog) y careceria de un mecanismo de activacion auditable. Este change endurece el directorio para que los datos reales puedan habilitarse de forma segura mas adelante.

Governance: HIGH (datos personales bajo Ley 25.326; retencion y ARCO; visibilidad entre sectores). Este change es SOLO de planificacion (proposal, specs, design, tasks): NO se implementa codigo sin una aprobacion humana HIGH registrada de forma verificable.

## What Changes

- **BREAKING**: Revertir DIR-005/DIR-010 (texto plano) mediante un ADR nuevo. El email y el telefono se cifran at-rest con `EncryptedText` (Fernet) y se busca por un indice ciego determinista (`email_bidx`, `telefono_bidx`) derivado con HMAC y una clave dedicada `directory_blind_index_key`. Las busquedas del repositorio pasan a apuntar al indice ciego y la unicidad del email se preserva sobre el indice determinista.
- **BREAKING**: Clave de cifrado dedicada del directorio y clave de indice ciego dedicadas, con rotacion cableada en `App/Backend/scripts/rotate_fernet_key.py` y documentadas en `docs/seguridad/gestion-secretos-y-rotacion.md`.
- Migracion Alembic REVERSIBLE que rellena (backfill) las filas existentes a ciphertext e indice ciego, con un test de integracion que prueba que no queda email ni telefono en claro en la base.
- Control de acceso: formalizar el acceso por sujeto (si `usuario_final` puede leer su propia fila) en `App/Backend/app/services/role_policy.py`; limitacion de tasa y anti-enumeracion en los endpoints de lectura del directorio; re-verificar el aislamiento entre sectores (VIS-001/VIS-002) con un test negativo para `usuario_final`.
- Auditoria durable: tabla de auditoria del directorio append-only y sin PII, analoga a `incidente_evento`; enrutar la auditoria del directorio a ese almacen ademas de structlog; auditoria durable de los canales de resolucion de contacto.
- Retencion/ARCO/minimizacion: runbook operativo y alerta para las filas acumuladas que superan `fecha_baja + 1 año` (SIN cron en el codigo); flujo ARCO de acceso y rectificacion (no solo supresion) con procedimiento y auditoria; ventana de retencion de logs del directorio alineada con el ciclo de vida; re-ejecutar la revision de minimizacion para confirmar que no se agregan columnas PII.
- Ops/gobernanza: registrar la aprobacion humana HIGH en `docs/directorio-evidencia-cumplimiento.md` seccion 4 y en `CHANGES.md` cuando se conceda; reemplazar la compuerta "sin mecanismo de activacion" por un mecanismo deliberado y auditado (migracion gobernada por entorno + artefacto de aprobacion); actualizar DIR-005/DIR-009/DIR-010 de la spec y agregar un requisito de auditoria durable; regenerar `docs/openapi.json` si cambia el contrato de lectura.

Estado actual (hasta que exista la aprobacion): el directorio permanece operando SOLO con datos sinteticos.

## Capabilities

### New Capabilities

- Ninguna. El endurecimiento se expresa como cambios en la capability existente `employee-directory`.

### Modified Capabilities

- `employee-directory`: invierte la decision de texto plano. DIR-005 y DIR-010 se REMUEVEN (reversion total; representacion correcta del esquema) y se reemplazan por los requisitos nuevos `DIR-011` (cifrado at-rest con indice ciego determinista) y `DIR-016` (ADR de reversion). Se modifican DIR-002 (permite las columnas derivadas no-PII de busqueda), DIR-006 (acceso de lectura por sujeto y anti-enumeracion) y DIR-009 (mecanismo de activacion deliberado y auditado, con evidencia de la aprobacion humana HIGH). Se agregan `DIR-012` (rotacion de claves dedicadas), `DIR-013` (auditoria durable sin PII) y `DIR-015` (retencion operativa, alerta de acumulacion y ARCO de acceso y rectificacion).

## Impact

- Modelo: `App/Backend/app/models/empleado.py` (email/telefono pasan a `EncryptedText`; nuevas columnas de indice ciego).
- Repositorio: `App/Backend/app/repositories/empleado_repository.py` (busquedas por indice ciego; unicidad sobre el indice determinista).
- Servicio: `App/Backend/app/services/directorio_service.py` (auditoria durable; validaciones sin cambios de contrato externo).
- Politica de rol: `App/Backend/app/services/role_policy.py` (lectura por sujeto, anti-enumeracion).
- Utilidades: `App/Backend/app/utils/encryption.py` (uso de `EncryptedText`; helper de indice ciego).
- Script de rotacion: `App/Backend/scripts/rotate_fernet_key.py` (inventario de columnas cifradas del directorio).
- Migraciones: nueva migracion Alembic reversible (backfill).
- Documentacion: `docs/directorio-evidencia-cumplimiento.md`, `docs/seguridad/gestion-secretos-y-rotacion.md`, `docs/seguridad/procedimiento-arco.md`, `docs/seguridad/justificacion-minimizacion-directorio.md` (ADR de reversion), `docs/seguridad/` (retencion), `docs/openapi.json`, `CHANGES.md`.
- Specs: `openspec/specs/employee-directory/spec.md` (delta).
- Sin cambios en las cinco cadenas canonicas de sector, en los valores de Gemini, en `requirements.txt` ni en `openspec/config.yaml`.
