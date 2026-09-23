## Why

La mesa de ayuda no sabe QUIEN reporta ni a QUIEN avisar: no existe un directorio de empleados. El canal correo captura `remitente` en N8N pero no lo persiste; el web autentica al reportante, pero `users` es solo autenticacion y no tiene email; la telefonia guarda el llamante cifrado (`telefonia_ingreso.caller_cifrado`) pero sin identidad. Sin directorio no hay resolucion de contactos por sector/rol, no hay notificaciones enriquecidas y no existe un modelo de roles (hoy inexistente: `users` es auth-only y `sector` es el catalogo canonico de clasificacion).

## What Changes

- Nueva entidad de directorio **`directorio_empleado`** (tabla propia), SEPARADA de `users` (auth), con vinculo opcional a una cuenta.
- Modelo de roles minimo (`usuario_final` / `operador` / `administrador_directorio`) y vinculo al catalogo `sector` canonico (los cinco strings vigentes). NO se crea un vocabulario nuevo de sectores.
- Resolucion de contactos: telefono -> empleado, email -> empleado, usuario autenticado -> empleado, con "no encontrado" no fatal.
- PII (Ley 25.326): email/telefono cifrados at-rest + **indice ciego** (HMAC) para busqueda por igualdad; control de acceso a lectura/escritura.
- Migracion aditiva **009**, estrategia de seed sin inventar PII y tests SQLite (unit) / PostgreSQL (integration).
- Punto de enganche con **c-53** (resolucion de contacto) SIN implementar notificaciones aqui.

### Out of scope

- El envio de notificaciones (pertenece a c-53).
- Twilio Media Streams / agente conversacional (diferido; tesis cap. 10).
- Sincronizacion con un sistema de RRHH y RBAC completo de la aplicacion.
- Cambios a los cinco sectores/strings canonicos de clasificacion.

## Capabilities

### New Capabilities

- `employee-directory`: entidad de directorio de empleados (email, telefono E.164, nombre, sector, rol, activo), modelo de roles, manejo de PII (cifrado at-rest + indice ciego), control de acceso y ciclo de vida.
- `contact-resolution`: resolucion de un contacto a partir de telefono/email/usuario autenticado, comportamiento ante no-encontrado y contrato de enganche para c-53.

### Modified Capabilities

- None — c-53 (`incident-notification`) aun no esta en `openspec/specs/` (change sin archivar), por lo que este change la consume via un contrato nuevo, no via delta.

## Impact

| Area | Impacto | Descripcion |
|------|---------|-------------|
| `App/Backend/alembic/versions/009_*.py` | New | Migracion aditiva: `directorio_empleado` + indices |
| `App/Backend/app/models/empleado.py` | New | ORM del directorio; enums de rol |
| `App/Backend/app/repositories/empleado_repository.py` | New | Acceso por hash ciego (telefono/email) y por `user_id` |
| `App/Backend/app/services/directorio_service.py` | New | CRUD + reglas de activo/rol |
| `App/Backend/app/services/contact_resolution_service.py` | New | Contrato de resolucion (seam c-53) |
| `App/Backend/app/routes/directorio.py`, `app/schemas/directorio.py` | New | API de gestion (autenticada y autorizada) |
| `App/Backend/app/utils/blind_index.py` | New | HMAC-SHA256 para igualdad sobre datos cifrados |
| `App/Backend/app/config/settings.py`, `.env.example` | Modified | Clave del indice ciego |
| `App/Backend/tests/test_directorio_*.py` | New | Unit + integration |
| `docs/openapi.json` | Modified | Sincronizacion del contrato |

## Open Questions

1. **Origen de los datos**: export de RRHH, carga CSV/API, o UI de administracion. Afecta si entra un frontend en este change.
2. **Campos obligatorios y unicidad**: legajo obligatorio; email unico por empleado o compartido por area.
3. **Vocabulario de roles**: alcanza con los tres roles propuestos; un operador pertenece a un solo sector.
4. **Politica de ambiguedad**: numeros/emails compartidos (mesa de area). Ver `design.md` D6.
5. **Clave del indice ciego**: nueva clave dedicada o derivada de la existente; implicancias de rotacion.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Fuga de PII (email/telefono) | Med | Cifrado at-rest + indice ciego; sin PII en logs/auditoria; acceso autorizado |
| Matching incorrecto (identidad equivocada) | Med | Igualdad exacta sobre hash normalizado; ambiguos => no resuelve; trazabilidad |
| Indice ciego debil o clave filtrada | Low | HMAC con clave dedicada en `settings`; revisar en fase de seguridad |
| Directorio desactualizado o vacio | Med | Deactivacion, no borrado; resolucion no fatal; seed dev sin PII real |
| Colision de migracion con c-52/c-53 | Low | Revision 009 aditiva; no toca tablas existentes |

## Rollback Plan

Revertir el commit elimina modelo/repositorio/servicio/rutas y la migracion se revierte con `cd App/Backend; alembic downgrade -1`, que dropea `directorio_empleado` (no hay datos de negocio que restaurar: las filas son cargables de nuevo desde la fuente). c-53 NO depende del directorio para funcionar, por lo que su rollback es independiente. Los tests nuevos se eliminan con el commit.

## Success Criteria

- [ ] Existe un directorio de empleados separado de `users`, con sector/rol/activo.
- [ ] Telefono, email y usuario autenticado resuelven a un empleado; "no encontrado" no es fatal.
- [ ] Email/telefono estan cifrados at-rest y se buscan por indice ciego sin descifrado masivo.
- [ ] El acceso al directorio esta restringido y no expone PII en logs.
- [ ] `openspec validate --strict --changes c-54-directorio-usuarios` pasa.
