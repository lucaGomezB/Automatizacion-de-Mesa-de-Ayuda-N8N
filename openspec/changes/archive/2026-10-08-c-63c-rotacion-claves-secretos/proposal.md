# Proposal: c-63c-rotacion-claves-secretos

## Why

Fase C del split de `c-63-identidad-accesos-claves`. Cierra en lo tecnico y reversible los controles ISO/IEC 27002 8.2 (derechos de acceso privilegiado, incluida la gestion de claves) y 8.24 (uso de criptografia): hoy `jwt_secret_key` y la clave Fernet (`pseudonymization_encryption_key`) viven en `.env` sin procedimiento de rotacion, no hay `kid` ni ventana de solapamiento, y no existe inventario de secretos ni runbook. Depende de `c-63a` (contrato JWT de vida corta, refresco y revocacion) y de `c-63b` (secreto TOTP cifrado con Fernet, que entra en el inventario de rotacion). Governance CRITICO: el agente propone, el autor ya resolvio las decisiones de abajo.

## What Changes

- **Rotacion del secreto JWT**: keyring con `kid` + ventana de solapamiento. La firma usa la clave activa; los tokens firmados con la clave anterior y los legacy sin `kid` se aceptan hasta `jwt_previous_key_expires_at`; la verificacion esta acotada (como maximo dos claves por token).
- **Rotacion de la clave Fernet**: `MultiFernet` (clave nueva primero, anterior de respaldo) + `scripts/rotate_fernet_key.py` que re-cifra en UNA transaccion todas las columnas cifradas con Fernet, con **respaldo previo obligatorio**. La clave anterior se retira recien al confirmar el re-cifrado; revertir = volver a la clave previa.
- **PREREQUISITO (tarea explicita)**: inventario exacto de los datos cifrados con Fernet antes de escribir el script. Verificado en el codigo: `incidente.descripcion_original`, `telefonia_ingreso.caller_cifrado` y `telefonia_ingreso.transcript_original` (el enunciado citaba solo la primera); a futuro tambien el secreto TOTP de `c-63b`.
- **Higiene/gestion de secretos**: inventario de secretos + runbook de rotacion; ninguna credencial en el repositorio. Postura `.env` + variables; SOPS/Docker secrets/Vault documentados como opciones no adoptadas por ahora.
- **Organizacional (5.16 ciclo de vida de identidades, 5.18 aprobacion/revision de accesos)**: extender `docs/seguridad/` (documental, verificable), referenciado desde el indice de C-61.
- **KMS/Vault, PAM y CA real**: documentar como prerequisito de despliegue (futuro/organizacional); NO implementar.

## Capabilities

### New Capabilities

- `identity-access-hardening`: fase C de la capacidad — rotacion del secreto JWT con keyring `kid` y ventana de solapamiento, rotacion de la clave Fernet con `MultiFernet` y re-cifrado transaccional con respaldo previo, inventario de secretos y runbook de rotacion, postura pragmatica de `.env` y encuadre de KMS/PAM/CA como futuro, y documentacion organizacional de ciclo de vida y revision de accesos.

### Modified Capabilities

- None — `c-63c` es aditivo sobre la capacidad que introduce el split de `c-63`; no modifica requisitos de capacidades ya existentes.

## Impact

| Area | Impacto | Descripcion |
|------|---------|-------------|
| `App/Backend/app/core/security.py` | Modified | Decodificacion con keyring (`kid`) y ventana de solapamiento |
| `App/Backend/app/services/auth_service.py` | Modified | Firma con la clave activa y `kid` en el header |
| `App/Backend/app/utils/encryption.py` | Modified | `MultiFernet` (clave activa + anterior) y cache por conjunto de claves |
| `App/Backend/app/config/settings.py`, `App/Backend/.env.example` | Modified | Keyring JWT, clave Fernet anterior y ventana |
| `App/Backend/scripts/rotate_fernet_key.py` | New | Re-cifrado transaccional con respaldo previo obligatorio |
| `App/Backend/tests/test_*` | New | Rotacion JWT (ventana) y rotacion Fernet (re-cifrado y revertibilidad) |
| `docs/seguridad/*` | Modified/New | Inventario de secretos, runbook de rotacion, ciclo de vida 5.16 y revision 5.18 |

## Governance: CRITICO

Nivel CRITICO (claves y secretos). El agente **propone**; las decisiones de esta fase ya fueron resueltas por el autor (ver `design.md`). Toda tension NUEVA se registra como Open Question (OQ-C*) y NO se asume. Delta specs y tasks son incrementales, reversibles y defendibles en la tesis. No se escribe codigo en la fase de propose.

## Risks

| Risk | Prob. | Mitigacion |
|------|-------|------------|
| Rotacion de la clave Fernet pierde datos at-rest | Alta | MultiFernet + respaldo previo obligatorio + re-cifrado transaccional (design D-C4) |
| Rotacion del secreto JWT invalida todas las sesiones | Media | Keyring con ventana de solapamiento (design D-C1/D-C2) |
| Inventario Fernet incompleto deja columnas sin re-cifrar | Media | Inventario como prerequisito explicito (design D-C5); el script enumera columnas, no las infiere |
| Sobredeclarar KMS/PAM/CA | Alta | Encuadre explicito como futuro/no implementado (IAH-010) |
| Romper el flujo dev/CI | Baja | Keyring y MultiFernet aditivos; defaults retrocompatibles (design D-C2/D-C3) |

## Rollback Plan

Revertir los commits de codigo y configuracion restaura la firma/descifrado actuales. Para la clave Fernet la clave anterior se conserva en el conjunto hasta confirmar el re-cifrado, por lo que revertir = reponer la clave previa como activa (o restaurar el respaldo tomado antes de la rotacion). Para el secreto JWT, volver a la clave anterior como activa revalida los tokens vigentes. Ninguna operacion es irreversible.

## Dependencies

- `c-63a-auth-hardening` — el keyring `kid` se apoya en el contrato de tokens (vida corta, refresco, revocacion) que fija `c-63a`.
- `c-63b-mfa-y-rol-privilegiado` — el secreto TOTP cifrado con Fernet se incorpora al inventario de rotacion.
- `c-63-identidad-accesos-claves` (master, D8/D9) — referencia de decisiones de fase C.
- `C-61 compliance-gobernanza` (archivado) — indice `docs/seguridad/README.md` que se extiende.

## Success Criteria

- [ ] Un token firmado con la clave anterior se acepta dentro de la ventana y se rechaza tras ella (tests).
- [ ] Los tokens legacy sin `kid` se validan durante la transicion sin re-login masivo (tests).
- [ ] Existe un inventario exacto de columnas Fernet y el script re-cifra en una transaccion con respaldo previo (tests).
- [ ] Un dato cifrado con la clave anterior se descifra y queda legible con la clave nueva; la rotacion es reversible (tests).
- [ ] No hay secretos en el repositorio; inventario de secretos y runbook de rotacion documentados.
- [ ] KMS/Vault, PAM y CA real quedan documentados como futuro/no implementado.
- [ ] 5.16 y 5.18 quedan documentados como responsabilidad de la organizacion adoptante y referenciados desde el indice.
- [ ] Las suites backend/frontend siguen verdes; `openspec validate c-63c-rotacion-claves-secretos --strict` pasa.
