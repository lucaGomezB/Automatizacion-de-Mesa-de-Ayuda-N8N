## Context

Ver `proposal.md — Why`. Restricciones verificadas que moldean el enfoque:

- **No existe un modelo de roles.** `App/Backend/app/models/user.py` (`users`) es exclusivamente autenticacion (`id`, `username`, `hashed_password`, `is_active`) y su docstring declara que NO se relaciona con `Incidente` ni con el dominio de clasificacion. Las unicas apariciones de "roles" en el codigo son etiquetas internas de contadores de costo (`app/cost_guard/guard.py`), sin relacion con autorizacion. Por lo tanto, definir roles es parte de este change.
- **Catalogo de sectores vs. categorias de clasificacion.** En el codigo vigente son el MISMO vocabulario: `app/constants.py` define `SECTORES_CANONICOS` con los cinco strings y la tabla `sector` (`app/models/catalog.py`) los persiste igual. NO existe en el codigo una derivacion de "tres sectores". El directorio MUST enlazar al catalogo `sector` existente; no se crea vocabulario nuevo.
- **Realidad de datos de contacto por canal.**
  - Correo: el remitente se captura en N8N (`remitente`; `from` del trigger Outlook) y se usa para la confirmacion; no se persiste en el backend.
  - Web: el reportante esta autenticado (`Depends(get_current_user)`), pero `users` no tiene email y ni el formulario ni `IncidenteCreate` capturan uno.
  - Telefonia: el llamante se captura ENCRYPTED en `telefonia_ingreso.caller_cifrado`; el `From` esta disponible en el webhook de VOZ (`app/routes/cost_guard.py`). No hay email.
- **Cifrado existente.** `app/utils/encryption.py` provee `EncryptedText` (Fernet, NO determinista) sobre `pseudonymization_encryption_key`. Aplica al contenido del incidente y al llamante de telefonia; NO se extiende al directorio: por decision humana (v8, cap. 11.2/11.4) el contacto del empleado se guarda en texto plano.
- **Decision humana (v8):** el directorio almacena contacto en TEXTO PLANO, sin cifrado de aplicacion ni indice ciego, porque (a) la auditabilidad directa y las consultas SQL operativas deben funcionar sin custodia/aprobacion de claves, y (b) el dato es personal pero NO sensible bajo Ley 25.326 art. 2. La tesis v8 ya declara esta postura (cap. 11.2/11.4) y agrega `directorio_empleado` (cap. 5.6, Tabla 4 / Anexo C).
- **Convenciones.** Capas `routes -> services -> repositories -> models`; async SQLAlchemy con `selectinload()`; migraciones en `App/Backend/alembic/versions/` (ultima: `008`); identificadores de dominio en español.
- **Sibling `c-53-notificacion-numero-incidente`.** Ya propuesto; su design declara que NO implementa el directorio y deja la resolucion de contactos como estrategia enchufable futura. c-53 funciona SIN el directorio; c-54 lo provee.

## Goals / Non-Goals

**Goals:**

- Modelar un directorio de empleados con datos de contacto, sector, rol y estado activo, separado de la autenticacion.
- Definir el modelo de roles que hoy no existe, con el minimo vocabulario que tiene uso real.
- Hacer resolubles telefono, email y usuario autenticado hacia un empleado, con "no encontrado" no fatal.
- Proteger el dato personal (Ley 25.326) con MINIMIZACION de campos, control de acceso por rol, auditoria de accesos y ausencia de PII en logs — sobre texto plano.
- Aplicar visibilidad de incidentes por rol a nivel API.
- Dejar un contrato de resolucion estable para que c-53 lo consuma sin cambiar su entrega.

**Non-Goals:**

- Enviar notificaciones (c-53), SMS o correo.
- Twilio Media Streams / agente conversacional (diferido; tesis cap. 10).
- Sincronizar con un sistema de RRHH o construir una UI de administracion completa.
- La parte FRONTEND de la visibilidad por rol (diferida a un change posterior; en c-54 solo el filtrado a nivel API).
- RBAC transversal de toda la aplicacion ni cambios a los cinco sectores canonicos.
- Implementar codigo en esta fase (propose/design only).

## Decisions

### D1: Tabla propia `directorio_empleado`, NO extender `users`

Se crea una entidad dedicada y se mantiene `users` como dominio de autenticacion. Razon: `users` es auth-only por diseno y su docstring prohibe mezclarlo con el dominio; extenderlo obligaria a que toda cuenta de acceso tenga datos de contacto. Se ofrece un vinculo opcional `user_id` (FK nullable a `users.id`, `ON DELETE SET NULL`) para saber que cuenta corresponde a que empleado, sin fusionar ambos dominios (DIR-001). Alternativa considerada: agregar contacto a `users` — descartada por acoplar PII al alta de credenciales.

### D2: Modelo de roles minimo de tres valores, con sector obligatorio por rol

Rol como enum `RolEmpleado` con exactamente: `usuario_final`, `operador`, `administrador_directorio`. Uso real: (a) `usuario_final` es el reportante; (b) `operador` atiende y puede ser destino de enrutamiento de su sector; (c) `administrador_directorio` carga/mantiene el directorio. Para `usuario_final`/`operador` el `sector_id` es OBLIGATORIO; el `administrador_directorio` NO tiene sector y puede ver TODOS los incidentes (OQ3). El rol NO interviene en la clasificacion (DIR-003). Alternativa considerada: rol implicito del sector — descartada: confundiria "que sector atiende" con "que puede hacer".

### D3: Vinculo al catalogo canonico `sector`, sin vocabulario nuevo

El directorio referencia `sector.id` (FK). Se reutiliza el catalogo de cinco sectores vigente y NO se introduce una lista propia. `sector_id` es obligatorio cuando el rol es `usuario_final`/`operador` y MUST ser nulo para `administrador_directorio` (DIR-004). Alternativa considerada: guardar el nombre como string — descartada: permitiria strings fuera del vocabulario canonico.

### D4: Contacto en TEXTO PLANO, sin cifrado de aplicacion ni indice ciego

El email y el telefono se almacenan en claro en columnas `varchar`. NO se aplica `EncryptedText` ni un indice ciego HMAC, y NO se agrega una clave `directory_blind_index_key`. Razon (decision humana, v8 cap. 11.2/11.4): auditabilidad directa y consultas SQL operativas sin custodia de claves; dato personal pero no sensible bajo Ley 25.326 art. 2. Se compensa con MINIMIZACION (solo los campos de D6b), control de acceso por rol, auditoria de accesos y no-PII en logs (DIR-005). Alternativa considerada: cifrado + indice ciego — descartada por la decision humana y por su costo operacional; se mantiene solo para el contenido del incidente (Fernet), que NO se toca.

### D5: Acceso: gestion con rol, resolucion interna sin HTTP

La API de gestion vive en `routes/directorio.py` y exige autenticacion; escrituras con rol `administrador_directorio` (dependencia de autorizacion nueva, acotada al directorio). La resolucion que consume c-53 es un servicio in-process (`contact_resolution_service`), sin borde HTTP ni token, para no ampliar la superficie de dato ni requerir red (DIR-006/RES-005). Se descarta exponer un endpoint de resolucion publico: seria un oraculo de contacto. Alternativa considerada: enforcement de rol global — diferida.

### D6: Ambiguedad => no resuelve

Si un telefono normalizado corresponde a mas de un empleado activo (numeros de mesa de area), la resolucion registra la ambiguedad y NO elige arbitrariamente (RES-004/OQ4). El `telefono` MAY repetirse (no unique); el `email` es unico por empleado. Alternativa considerada: "primer match" — descartada por riesgo de avisar a la persona equivocada.

### D6b: Modelo definitivo `directorio_empleado` (minimizacion)

Campos EXACTOS (nada mas se almacena): `id` (PK), `legajo` (varchar, NOT NULL, UNIQUE), `nombre` (varchar, NOT NULL), `email` (varchar, NOT NULL, UNIQUE, indexado), `telefono` (varchar E.164, NULL, indexado, MAY repetirse), `sector_id` (FK -> `sector`, NULL), `rol` (enum), `activo` (bool default true), `fecha_baja` (timestamp con zona, NULL; instante de desactivacion y base de la retencion D8, se limpia al reactivar), `user_id` (FK -> `users`, NULL, ON DELETE SET NULL), `created_at`/`updated_at`.

### D7: Visibilidad de incidentes por rol — a nivel API (frontend diferido)

Para usuarios NO administradores, los endpoints de lectura/listado de incidentes SHALL devolver solo los incidentes del sector del empleado autenticado; `administrador_directorio` SHALL ver todos. Se implementa como regla de alcance (scope) en la capa de API/servicio de incidentes. GOVERNANCE: HIGH. La interfaz de usuario que refleje esta visibilidad queda FUERA de c-54 y se difiere a un change posterior (solo se entrega el filtrado API). Requisito: `incident-visibility/VIS-001`.

### D8: Ciclo de vida: desactivacion, retencion y ARCO

`activo=false` en lugar de borrado operativo; la resolucion ignora inactivos (DIR-007). Retencion (OQ6): mientras la relacion laboral este activa + 1 año, luego borrado fisico. Implementacion: al desactivar se sella `fecha_baja = utcnow()` y al reactivar se limpia a `NULL`; el vencimiento se evalua con una funcion pura (`retencion_vencida(fecha_baja, ahora)` = `fecha_baja + 1 año <= ahora`, con clamp de 29-feb). La purga (`DirectorioService.purgar_vencidos`) borra SOLO filas `activo=false` con `fecha_baja` vencida, es IDEMPOTENTE y deja un evento de auditoria con el conteo, sin PII. El camino ejecutable es el script CLI `scripts/purgar_directorio.py` (`python -m scripts.purgar_directorio`), que espeja el seed dev-only; el borrado por retencion NO es el camino operativo por defecto. El borrado fisico tambien se ejecuta ante cancelacion ARCO, por `administrador_directorio` (accion explicita via API). Alternativa considerada: soft-delete con timestamp — descartada; `activo` + `fecha_baja` alcanzan.

### D9: Migracion aditiva 009 y seed idempotente sin PII real

Nueva revision `009` (posterior a `008`), aditiva: crea `directorio_empleado` con indices (UNIQUE en `legajo` y `email`; indice en `telefono` y `sector_id`) y FKs. La retencion de D8 agrega una revision APPEND-ONLY `010` (`down_revision = "009"`) que añade la columna nullable `fecha_baja`; la `009` ya fue publicada y NO se edita. OQ1 RESUELTA: seed idempotente con UN (1) usuario sintetico por rol, con datos de contacto utiles, creando AMBAS filas —`users` (login) y `directorio_empleado`— enlazadas por `user_id`. Esto tambien resuelve el bootstrap del primer administrador (sin huevo-y-gallina). NO se siembra PII real; el seed es script dev-only fuera de Alembic. Alternativa considerada: seed en la migracion — descartada por inventar PII y ensuciar produccion.

### D10: Estrategia de tests

- **Unit (SQLite, `-m "not integration"`)**: validaciones de campos/rol, normalizacion (email minusculas/trim, E.164), unicidad de `legajo`/`email`, repositorio/CRUD, reglas de autorizacion, resolucion encontrado/no-encontrado/ambiguo, visibilidad de incidentes por rol, y no-PII en logs/auditoria.
- **Integration (PostgreSQL, `-m integration`)**: FK a `sector` y `users`, UNIQUE de `legajo`/`email`, indice de `telefono`, comportamiento de `ON DELETE SET NULL` y busqueda por igualdad. Base desechable existente.

### D11: Contrato de enganche con c-53

`contact_resolution_service` expone `resolver_por_telefono`, `resolver_por_email` y `resolver_por_usuario`, cada una devolviendo un `ResultadoResolucion` con el empleado o vacio, distinguible de error. c-53 lo consume como estrategia opcional: sin contacto, conserva su resolucion directa. Este change NO toca el codigo ni el contrato de c-53 (RES-005). Orden de archivado: c-52 -> c-53 y c-54 en cualquier orden.

### D12: Gobierno (gobernanza)

- Entidad, control de acceso, matching, auditoria, retencion/ARCO y la visibilidad por rol (D7) son **HIGH**: datos personales de empleados y Ley 25.326; D7 ademas expone informacion de incidentes entre sectores. No se escribe codigo en esta fase; la implementacion requiere revision humana de la politica de retencion/ARCO y de la regla de visibilidad.
- Migracion y API de gestion: **HIGH**. Repositorio/servicio/test: MEDIUM.

### D13: Sin cambios a clasificacion ni a notificaciones

No se tocan `constants.py`, el clasificador, los cinco sectores ni `n8n/workflow.json` en lo relativo a notificaciones. El cifrado Fernet del contenido del incidente (`app/utils/encryption.py`, `caller_cifrado`) PERMANECE sin cambios. c-54 NO agrega claves de configuracion nuevas.

### D14: Los errores 422 NO reflejan el valor enviado (fix W1)

El handler global de `RequestValidationError` serializaba `exc.errors()`, que incluye `input` (el valor enviado) y `ctx`; un telefono/email invalido devolvia el dato en claro en el cuerpo del 422, contra DIR-006. Se sanea en el envelope global (`_sanitize_validation_errors`) conservando solo `loc`, `msg` y `type`, y descartando `input`, `ctx` y `url`. Aplica a TODA la API, no solo al directorio.

### D15: El alcance por rol aplica tambien a las ESCRITURAS por ID (fix W3)

`GET` list/detail ya aplicaban `alcance` (D7), pero `PATCH /incidentes/{id}` llamaba a `get_by_id` sin alcance, permitiendo a un no administrador leer/mutar por ID un incidente fuera de su sector. Se propaga `alcance` a `update_incidente` (y a su re-lectura), de modo que un incidente fuera de alcance responde 404 y NUNCA se modifica. El alcance es obligatorio en todas las rutas por ID (lectura y escritura).

## Risks / Trade-offs

- **[Exposicion de datos personales]** texto plano en la base → Mitigacion: minimizacion (D6b), control de acceso por rol (D5), auditoria de accesos y no-PII en logs (DIR-006); dato no sensible bajo Ley 25.326 art. 2 (decision v8).
- **[Matching erroneo]** avisar a la persona equivocada → Mitigacion: igualdad exacta sobre normalizado; ambiguo => no resuelve (D6).
- **[Visibilidad por rol]** fuga de informacion de incidentes entre sectores → Mitigacion: alcance obligatorio en la capa de API/servicio, tests de aislamiento; revision humana HIGH (D7/D12).
- **[Directorio vacio/desactualizado]** resolucion sin contacto → Mitigacion: "no encontrado" no fatal, c-53 sigue funcionando; desactivacion; seed dev.
- **[Acoplamiento con c-53]** romper su entrega → Mitigacion: contrato estable y consumo opcional (D11); c-54 no modifica specs ni codigo de c-53.
- **[Choque de migraciones]** varias changes activas → Mitigacion: 009 aditiva, no muta tablas previas.
- **[Sobre-ingenieria de roles]** RBAC excesivo → Mitigacion: solo tres roles y autorizacion acotada (D2/D5).
- **[Verificacion de no-PII en logs]** dificil de automatizar → Mitigacion: tests unitarios que aseveran ausencia del dato en claro.

## Migration Plan

1. Modelo `models/empleado.py` (tabla `directorio_empleado`, enums, FKs) y migracion `009` aditiva (`down_revision = "008"`); la columna `fecha_baja` de la retencion se agrega con la migracion append-only `010` (`down_revision = "009"`).
2. `utils/contactos.py`: normalizadores (email minusculas/trim, telefono E.164) y validadores, con tests.
3. Repositorio `empleado_repository.py` (busqueda por email/telefono/`user_id`, CRUD) con `selectinload` donde aplique.
4. Servicio `directorio_service.py` (CRUD, activacion, reglas de rol, auditoria de accesos) y `contact_resolution_service.py` (seam c-53).
5. Rutas `routes/directorio.py` + schemas + dependencia de autorizacion; filtro de visibilidad por rol en los endpoints de incidentes (D7); regenerar `docs/openapi.json`.
6. Seed dev-only idempotente (un usuario sintetico por rol) con `users` + `directorio_empleado`.
7. Fixtures de tests (empleados sinteticos) y suites unit/integration.
8. Purga por retencion: `DirectorioService.purgar_vencidos` + script CLI `scripts/purgar_directorio.py` (idempotente, conteo sin PII).
9. Rollback: revertir el commit y `cd App/Backend; alembic downgrade -1` (dropea la tabla; sin backfill). c-53 no se ve afectado.

## Open Questions

RESUELTAS (registro de decision humana):

1. **Origen de datos / bootstrap — RESUELTA**: seed idempotente con UN usuario sintetico por rol (contacto util), creando `users` + `directorio_empleado` enlazados por `user_id`; resuelve el primer administrador. Sin PII real.
2. **Campos obligatorios y unicidad — RESUELTA**: `legajo` obligatorio y unico; `email` unico por empleado; `telefono` MAY repetirse.
3. **Roles y sector — RESUELTA**: `usuario_final`/`operador` pertenecen a un sector (obligatorio); `administrador_directorio` sin sector y ve todos los incidentes. Impone la regla de visibilidad a nivel API (D7); su FRONTEND queda diferido; governance HIGH.
4. **Politica de ambiguedad — RESUELTA**: telefono/casilla compartidos => no concluyente, sin notificacion.
5. **Clave del indice ciego — RESUELTA (MOOT)**: no hay indice ciego ni clave.
6. **Retencion y ARCO — RESUELTA**: relacion laboral activa + 1 año, luego borrado fisico; borrado fisico tambien ante cancelacion ARCO, ejecutado por `administrador_directorio`.

Riesgo residual abierto: la implementacion de D7 requiere definir COMO se determina el sector efectivo del usuario autenticado (via `directorio_empleado.user_id -> sector_id`); si una cuenta no tiene empleado vinculado con sector, el alcance de incidentes debe ser vacio o restringido. Esto se documenta como decision de implementacion bajo governance HIGH.