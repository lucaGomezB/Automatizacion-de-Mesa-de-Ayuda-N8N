# Proposal: c-63b — MFA y rol privilegiado (Fase B)

## Why

La Fase B del workstream de identidad (`c-63-identidad-accesos-claves`) cierra los controles ISO/IEC 27002 **5.15** (control de acceso) y **8.5** (autenticacion segura) con el segundo factor. Hoy `User` (`App/Backend/app/models/user.py`) no distingue una cuenta privilegiada: el rol vive en `Empleado` (`RolEmpleado`) y el `admin` sembrado (migracion 003) no tiene `Empleado`, de modo que no existe una fuente unica para exigir MFA. Este change agrega el flag privilegiado a nivel identidad y el segundo factor TOTP, detras de una bandera apagada por defecto.

## What Changes

- **Rol privilegiado a nivel identidad**: columna `User.is_privileged` (bool, default false) + migracion; el seed `admin` queda privilegiado; las cuentas vinculadas a un `Empleado` de rol `operador`, `administrador_directorio` o `mesa_de_ayuda` quedan privilegiadas. El flag es la fuente para exigir MFA; `usuario_final` no.
- **MFA TOTP**: nuevo `App/Backend/app/services/mfa_service.py` con enrollment (`otpauth://` + secreto/QR), verificacion RFC 6238 y **codigos de recuperacion hasheados con bcrypt**. El **secreto TOTP se cifra at-rest con Fernet**, reutilizando `App/Backend/app/utils/encryption.py`.
- **Login en dos pasos aditivo**: `POST /auth/login` con solo password devuelve, para cuenta privilegiada con MFA activo y la bandera encendida, un estado "segundo factor requerido" (ticket corto) sin emitir token; `POST /auth/mfa/verify` completa y devuelve `{access_token, token_type, ...}`. Se agrega `POST /auth/mfa/enroll`. Los campos actuales del login se preservan.
- **Frontend**: reto MFA en el login (`AuthContext.tsx`).
- **BREAKING (acotado)**: solo para cuentas privilegiadas con `mfa_required_for_privileged=true`; con la bandera apagada (default dev/test) el flujo de un solo paso no cambia.
- **Requisito de despliegue**: `mfa_required_for_privileged` MUST habilitarse en produccion (se documenta).

## Capabilities

### New Capabilities

- `identity-access-hardening`: extiende la capability introducida por `c-63` con el flag privilegiado a nivel identidad, el segundo factor TOTP (enrollment, verificacion, codigos de recuperacion y secreto cifrado) y el login en dos pasos aditivo con reto MFA en el frontend.

### Modified Capabilities

- None — no se modifica el comportamiento especificado por C-61 ni por la Fase A (`c-63a`); se agregan requisitos a la capability de la Fase B.

## Impact

| Area | Impacto | Descripcion |
|------|---------|-------------|
| `App/Backend/app/models/user.py` | Modified | `is_privileged` (bool, default false) |
| `App/Backend/alembic/versions/` | New | Migracion de `is_privileged` y campos MFA (`totp_secret`, `totp_enabled`, codigos de recuperacion); marca `admin` privilegiado |
| `App/Backend/app/services/mfa_service.py` | New | Enrollment TOTP, verificacion RFC 6238, codigos de recuperacion (bcrypt) |
| `App/Backend/app/services/auth_service.py` | Modified | Emision/validacion del ticket corto de segundo factor (firma directa con el secreto activo, sin keyring) |
| `App/Backend/app/routes/auth.py` | Modified | `/auth/login` en dos pasos, `/auth/mfa/verify`, `/auth/mfa/enroll` |
| `App/Backend/app/schemas/auth.py` | Modified | Request/response de MFA y ticket (aditivo) |
| `App/Backend/app/config/settings.py`, `.env.example` | Modified | `mfa_required_for_privileged` (default false), TTL del ticket, issuer, cantidad de codigos |
| `App/Backend/app/services/privilege_service.py`, `app/services/directorio_service.py` | New/Modified | Derivacion/marcado y sincronizacion del privilegio al crear/actualizar/desvincular (segun OQ-B1) |
| `App/Frontend/src/contexts/AuthContext.tsx`, `src/pages/LoginPage/index.tsx`, `src/pages/MfaEnrollmentPage/**` | Modified/New | Reto MFA (enrollment y verificacion) |
| `App/Backend/tests/*`, `App/Frontend/src/**/*.test.tsx` | Modified/New | Cobertura de flag privilegiado, MFA y login en dos pasos |

## Governance: CRITICO

Autenticacion/seguridad. El agente **propone**; el autor ya resolvio mecanismo (TOTP), roles con MFA (incluido `admin` via el flag), default de la bandera y compatibilidad. Las tensiones NUEVAS no cubiertas por esas decisiones se registran como **Open Questions** en `design.md` (OQ-B1, OQ-B2) y MUST resolverse antes de `apply`. No se escribe codigo en la fase de propose.

## Risks

| Risk | Prob. | Mitigacion |
|------|-------|------------|
| Romper el flujo dev (`admin`/`admin123`, `directorio.admin`) | Media | Bandera `mfa_required_for_privileged=false` por defecto; test de compatibilidad (IAH-007) |
| MFA bloquea CI/pruebas | Media | MFA mockeable/deshabilitado; TOTP verificable con codigo calculado, sin tiempos reales |
| Secreto TOTP expuesto at-rest | Baja | Cifrado Fernet reutilizando `utils/encryption.py` |
| Doble fuente de verdad del privilegio (flag vs `Empleado`) | Media | Resolver OQ-B1 antes de apply |
| Perdida de acceso privilegiado (dispositivo + codigos) | Baja | Resolver OQ-B2 antes de apply |

## Rollback Plan

Revertir los commits de codigo, migracion y configuracion. `alembic downgrade` elimina `is_privileged` y los campos MFA y restaura el esquema previo. Con `mfa_required_for_privileged=false` el login vuelve al flujo de un solo paso y `admin`/`admin123` siguen operativos. No se alteran datos de los seeds: la marca de privilegio del `admin` se revierte al bajar la migracion.

## Dependencies

- `c-63a-auth-hardening` (Fase A) — aporta el login/JWT de dos pasos y el refresco sobre los que se apoya la emision del token tras el segundo factor.
- `C-61 compliance-gobernanza` (archivado) — parametros de politica y roles que el flag privilegiado consume.
- Sin dependencia de `c-63c-rotacion-claves-secretos`.

## Success Criteria

- [ ] El flag `is_privileged` distingue cuentas privilegiadas y el seed `admin` queda privilegiado (tests).
- [ ] Una cuenta privilegiada con MFA activo recibe un reto de segundo factor, no un token (tests).
- [ ] Un codigo TOTP valido emite el token con los campos actuales; uno invalido/expirado es rechazado (tests).
- [ ] Los codigos de recuperacion son de un solo uso, estan hasheados y el secreto TOTP esta cifrado at-rest (tests).
- [ ] Con `mfa_required_for_privileged=false`, `admin`/`admin123` inicia sesion en un solo paso (test de compatibilidad dev).
- [ ] El frontend presenta el reto MFA y el enrollment (tests).
- [ ] `pytest` (subconjuntos SQLite e integration) y `npm run test` siguen verdes.
- [ ] `openspec validate c-63b-mfa-y-rol-privilegiado --strict` pasa.
