## Why

La mesa de ayuda no sabe QUIEN reporta ni a QUIEN avisar: no existe un directorio de empleados. El canal correo captura `remitente` en N8N pero no lo persiste; el web autentica al reportante, pero `users` es solo autenticacion y no tiene email; la telefonia guarda el llamante cifrado (`telefonia_ingreso.caller_cifrado`) pero sin identidad. Sin directorio no hay resolucion de contactos por sector/rol, no hay notificaciones enriquecidas y no existe un modelo de roles (hoy inexistente: `users` es auth-only y `sector` es el catalogo canonico de clasificacion).

## What Changes

- Nueva entidad de directorio **`directorio_empleado`** (tabla propia), SEPARADA de `users` (auth), con vinculo opcional a una cuenta.
- Modelo de roles minimo (`usuario_final` / `operador` / `administrador_directorio`) y vinculo al catalogo `sector` canonico (los cinco strings vigentes). `usuario_final`/`operador` requieren sector; `administrador_directorio` no tiene sector. NO se crea un vocabulario nuevo de sectores.
- Resolucion de contactos: telefono -> empleado, email -> empleado, usuario autenticado -> empleado, con "no encontrado" no fatal.
- Datos personales (Ley 25.326): contacto en **TEXTO PLANO** (sin cifrado de aplicacion ni indice ciego), con **minimizacion** de campos, **control de acceso por rol**, **auditoria de accesos** y **no-PII en logs**.
- **Visibilidad de incidentes por rol a nivel API**: el no administrador ve solo los incidentes de su sector; `administrador_directorio` ve todos. El frontend se difiere.
- Migracion aditiva **009**, seed idempotente con un usuario sintetico por rol (sin PII real) y tests SQLite (unit) / PostgreSQL (integration).
- Punto de enganche con **c-53** (resolucion de contacto) SIN implementar notificaciones aqui.

### Out of scope

- El envio de notificaciones (pertenece a c-53).
- Twilio Media Streams / agente conversacional (diferido; tesis cap. 10).
- Sincronizacion con un sistema de RRHH, UI de administracion y la parte FRONTEND de la visibilidad por rol (diferida).
- Cambios a los cinco sectores/strings canonicos de clasificacion.
- Cambios al cifrado Fernet del contenido del incidente (permanece).

## Capabilities

### New Capabilities

- `employee-directory`: entidad de directorio de empleados (legajo, nombre, email, telefono E.164, sector, rol, activo), modelo de roles, minimizacion y texto plano del contacto, control de acceso por rol, auditoria y ciclo de vida con retencion/ARCO.
- `contact-resolution`: resolucion de un contacto a partir de telefono/email/usuario autenticado, comportamiento ante no-encontrado y ambiguedad, y contrato de enganche para c-53.
- `incident-visibility`: visibilidad de incidentes por rol a nivel API (no administrador ve su sector; `administrador_directorio` ve todos; frontend diferido).

### Modified Capabilities

- None — c-53 (`incident-notification`) aun no esta en `openspec/specs/` (change sin archivar), por lo que este change la consume via un contrato nuevo, no via delta.

## Impact

| Area | Impacto | Descripcion |
|------|---------|-------------|
| `App/Backend/alembic/versions/009_*.py` | New | Migracion aditiva: `directorio_empleado` + indices (UNIQUE legajo/email, indice telefono/sector) |
| `App/Backend/app/models/empleado.py` | New | ORM del directorio; enums de rol |
| `App/Backend/app/repositories/empleado_repository.py` | New | Acceso por email/telefono (texto plano) y por `user_id` |
| `App/Backend/app/services/directorio_service.py` | New | CRUD + reglas de activo/rol + auditoria |
| `App/Backend/app/services/contact_resolution_service.py` | New | Contrato de resolucion (seam c-53) |
| `App/Backend/app/routes/directorio.py`, `app/schemas/directorio.py` | New | API de gestion (autenticada y autorizada) |
| `App/Backend/app/utils/contactos.py` | New | Normalizadores (email, E.164) y validadores |
| `App/Backend/app/routes/incidentes.py` (y servicio asociado) | Modified | Filtro de visibilidad de incidentes por rol (API) |
| `App/Backend/scripts/seed_directorio.py` (aprox.) | New | Seed dev-only idempotente, un usuario sintetico por rol |
| `App/Backend/tests/test_directorio_*.py`, `test_incident_visibility*.py` | New | Unit + integration |
| `docs/openapi.json` | Modified | Sincronizacion del contrato |

## Open Questions

Todas RESUELTAS por decision humana (detalle en `design.md`):

1. **Origen de datos / bootstrap — RESUELTA**: seed idempotente con un usuario sintetico por rol, creando `users` + `directorio_empleado` enlazados; resuelve el primer administrador. Sin PII real.
2. **Campos obligatorios y unicidad — RESUELTA**: `legajo` obligatorio y unico; `email` unico por empleado; `telefono` MAY repetirse.
3. **Roles y sector — RESUELTA**: `usuario_final`/`operador` con sector obligatorio; `administrador_directorio` sin sector y ve todos los incidentes. Impone la visibilidad por rol a nivel API (frontend diferido).
4. **Politica de ambiguedad — RESUELTA**: telefono/casilla compartidos => no concluyente, sin notificacion.
5. **Clave del indice ciego — RESUELTA (MOOT)**: no hay indice ciego ni clave.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Exposicion de datos personales (texto plano) | Med | Minimizacion de campos, control de acceso por rol, auditoria de accesos, sin PII en logs; dato no sensible (Ley 25.326 art. 2) |
| Matching incorrecto (identidad equivocada) | Med | Igualdad exacta sobre valor normalizado; ambiguos => no resuelve; trazabilidad |
| Visibilidad por rol: fuga de incidentes entre sectores | Med | Alcance obligatorio en API/servicio, tests de aislamiento, revision humana HIGH |
| Directorio desactualizado o vacio | Med | Desactivacion no borrado; resolucion no fatal; seed dev sin PII real |
| Colision de migracion con c-52/c-53 | Low | Revision 009 aditiva; no toca tablas existentes |

## Rollback Plan

Revertir el commit elimina modelo/repositorio/servicio/rutas y la migracion se revierte con `cd App/Backend; alembic downgrade -1`, que dropea `directorio_empleado` (no hay datos de negocio que restaurar: las filas son cargables de nuevo desde la fuente). El filtro de visibilidad de incidentes se revierte con el mismo commit. c-53 NO depende del directorio para funcionar. Los tests nuevos se eliminan con el commit.

## Success Criteria

- [ ] Existe un directorio de empleados separado de `users`, con sector/rol/activo.
- [ ] Telefono, email y usuario autenticado resuelven a un empleado; "no encontrado" no es fatal.
- [ ] El contacto se almacena en texto plano (sin cifrado de aplicacion ni indice ciego), con solo los campos minimizados.
- [ ] El acceso al directorio esta restringido por rol, auditado y sin PII en logs.
- [ ] La visibilidad de incidentes por rol se aplica a nivel API.
- [ ] `openspec validate --strict --changes c-54-directorio-usuarios` pasa.
