## Context

Ver `proposal.md - Why`. Estado actual verificado que condiciona el approach:

- Cuatro roles en `app/models/empleado.py` (`RolEmpleado`) con el CHECK en la migracion `012`. El conocimiento de rol esta duplicado en: el enum, el CHECK, `PRIVILEGED_ROLE_VALUES` (`app/services/privilege_service.py`), la cadena if/elif de `alcance_desde_empleado` (`app/services/incident_visibility.py`) y los guards `require_directorio_admin`/`require_directorio_lectura` (`app/routes/directorio.py`).
- `incident_visibility` deriva por request el alcance del `Empleado` vinculado via `user_id`; modos GLOBAL/SECTOR/REVISION/VACIO.
- La coherencia rol/sector vive solo en `DirectorioService._validar_sector_por_rol` (servicio), no en la base.
- El incidente NO tiene vinculo de reportante (`app/models/incidente.py`). El alta (`POST /api/v1/incidentes`) recibe `current_user` pero lo ignora; para web el `current_user` ES el reportante, para correo/telefono ES el operador de N8N (`n8n/workflow.json` usa `Login operador`).
- `ContactResolutionService` resuelve por email/telefono/usuario pero no esta cableado al alta.
- `NotificationRecipientService.resolver_destinatarios_revision(sector_id)` usa `EmpleadoRepository.listar_operadores_por_sector`.
- El seed dev (`scripts/seed_directorio.py`) crea un empleado por rol; la cuenta `admin` de la migracion `003` NO tiene empleado (su alcance efectivo hoy es VACIO; OQ-3 lo resuelve creandole un empleado `administrador_directorio` via migracion, ver D9).

## Goals / Non-Goals

**Goals:**

- Uniformar el RBAC a tres roles y dos modos de visibilidad, sin duplicar el conocimiento de rol.
- Que `usuario_final` pueda ver los incidentes que reporto, mediante un vinculo de reportante poblado por canal.
- Migrar datos existentes (`operador`) de forma append-only y reversible en lo razonable.

**Non-Goals:**

- La representacion en el frontend (es el change `c-81-frontend-rbac`, que depende de este).
- Cambiar el clasificador, la pseudonimizacion o el sobre de error.
- Resolver la ambiguedad de identidad del reportante mas alla de persistir el vinculo nulo.

## Decisions

### D1 — Vocabulario de tres roles y visibilidad PROPIO/GLOBAL

**Decision**: `RolEmpleado` pasa a `usuario_final`, `mesa_de_ayuda`, `administrador_directorio`. `ModoAlcance` pasa a `PROPIO`, `GLOBAL`, `VACIO` (se eliminan SECTOR y REVISION). `alcance_desde_empleado` deriva: `usuario_final` -> PROPIO (usa el `id` del empleado como reportante); `mesa_de_ayuda`/`administrador_directorio` -> GLOBAL; sin empleado -> VACIO. El sector deja de intervenir.

**Alternativas**: mantener SECTOR como modo y simplemente reasignar roles (no cumple la decision de eliminar el aislamiento por sector); conservar REVISION como vista de cola (se descarta: `mesa_de_ayuda` ahora es GLOBAL y la cola es una vista, no un alcance).

### D2 — Registro central de politica de rol (fuente unica de verdad)

**Decision**: nuevo modulo `app/services/role_policy.py` con:

- `ROLES_VALIDOS: tuple[str, ...]` derivado del enum (usado por el CHECK y por la verificacion de coherencia).
- `PoliticaRol` (dataclass frozen) con `requires_sector`, `visibilidad` (ModoAlcance), `privileged`, `manages_directory`, `can_read_directory`, `notification_recipient`.
- `ROLE_POLICY: Mapping[RolEmpleado, PoliticaRol]` con las tres entradas.

Consumidores que DEJAN de duplicar rol: `privilege_service` (deriva el conjunto privilegiado del registro), `incident_visibility` (deriva el modo del registro), `directorio.py` (guards derivan de `manages_directory`/`can_read_directory`), `notification_recipient_service` (deriva `notification_recipient`), y el enum/CHECK (derivan de `ROLES_VALIDOS`). El CHECK sigue enumerando los valores porque la base no lee codigo: `ROLES_VALIDOS` los emite y un test verifica que coincidan.

**Alternativas**: propiedades en el enum (mezcla dominio de datos con politica y no cubre el CHECK ni las rutas); un YAML/JSON de config (IO en runtime, sin tipo, no testeable en import); dejar el enum como fuente y agregar helpers por modulo (sigue duplicando). Se elige el registro Python en codigo por tipado, testabilidad e import unico.

**OQ-4 resuelto**: `can_read_directory` es verdadero para `mesa_de_ayuda` y `administrador_directorio`, y falso para `usuario_final`. El guard `require_directorio_lectura` (`app/routes/directorio.py:71-78`) hoy es una LISTA NEGRA (`empleado.rol == usuario_final`) que habilita por omision a cualquier rol no enumerado; se reemplaza por una LISTA BLANCA derivada de `can_read_directory` del registro, de modo que ningun rol quede habilitado por omision. La gestion (`manages_directory`) sigue siendo exclusiva de `administrador_directorio`.

### D3 — Vinculo de reportante y resolucion por canal (OQ-1 resuelto)

**Decision**: nueva columna nullable `reportante_empleado_id` en `incidente` (FK -> `directorio_empleado.id`, ON DELETE SET NULL, indexada). `IncidenteService.create_and_classify` recibe un `reportante_empleado_id: int | None` que la RUTA resuelve y le pasa (la ruta no ejecuta reglas; solo orquesta la dependencia). El contacto del reportante se toma IMPLICITAMENTE de los metadatos del canal: el payload de N8N ya transporta el contacto que N8N posee (email del remitente en correo, telefono del llamante en telefonia); NUNCA lo tipea el usuario. La resolucion por canal:

- Web (`canal_origen_id=2`): `ContactResolutionService.resolver_por_usuario(current_user.id)`; si la cuenta autenticada no tiene empleado vinculado, el reportante NO se identifica.
- Correo/telefonia: el `current_user` es el operador de N8N, NO el reportante; se resuelve desde el contacto implicito del payload (`reportante_email` / `reportante_telefono`, derivado del remitente/llamante por N8N) via `resolver_por_email` / `resolver_por_telefono`.
- ENCONTRADO -> se persiste el id. NO_ENCONTRADO, AMBIGUO, contacto de canal ausente o cuenta web sin empleado -> `reportante_empleado_id = NULL`, SIN elegir un contacto arbitrario y SIN bloquear el alta (paralelo a NR-007).
- Cuando el reportante NO se identifica, el incidente se deriva a revision humana (`requiere_revision_humana = true`) — ver D10 y el requisito VIS-005.

**Alternativas**: resolver dentro del `create_and_classify` a partir de `current_user` (acopla el servicio a la sesion HTTP); agregar claims de identidad al JWT (staleness); no persistir el vinculo y derivarlo (imposible para correo/telefono). Se elige resolver en la ruta y persistir, porque el reportante es dato del incidente.

### D4 — Destinatarios de revision: todos los `mesa_de_ayuda` activos

**Decision**: `resolver_destinatarios_revision()` pierde el parametro de sector y `EmpleadoRepository.listar_operadores_por_sector` se reemplaza por `listar_mesa_de_ayuda_activos()` (rol `mesa_de_ayuda`, `activo=true`, sin filtro de sector). El servicio deriva el rol destinatario del registro de politica (RP-002).

### D5 — Migracion Alembic `017` append-only (OQ-2 resuelto)

**Decision**: migracion nueva (`down_revision="016"`), sin editar migraciones publicadas:

1. `batch_alter_table("incidente")`: agregar `reportante_empleado_id` (Integer, null, FK `directorio_empleado.id` ON DELETE SET NULL) + indice.
2. Backfill ANTES del CHECK nuevo: `UPDATE directorio_empleado SET rol='mesa_de_ayuda' WHERE rol='operador'` (OQ-2 CONFIRMADO: las filas existentes con `rol='operador'` migran a `mesa_de_ayuda`, GLOBAL). Mismo criterio para cualquier fila legacy.
3. `batch_alter_table("directorio_empleado")`: drop del CHECK de cuatro valores y creacion del CHECK de tres valores (`usuario_final`, `mesa_de_ayuda`, `administrador_directorio`).
4. Insercion condicional del empleado sintetico de la cuenta `admin` (ver D9).
5. `downgrade`: recrea el CHECK de cuatro valores y elimina la columna/index del reportante. El mapeo `operador -> mesa_de_ayuda` NO es reversible: el rollback restaura el vocabulario pero no re-marca filas (documentado y aceptable sin datos reales).

**Alternativa**: `operador` -> `usuario_final` (menos privilegio) — se descarta porque `mesa_de_ayuda` ABSORBE semanticamente al operador (GLOBAL) y es el destino decidido por el autor.

### D6 — Eliminacion de la coherencia rol/sector

`DirectorioService._validar_sector_por_rol` y `_ROLES_CON_SECTOR` se eliminan; `sector_id` se valida solo como FK al catalogo cuando viene (existe) y se persiste opcional. El alcance deja de mirar `sector_id`.

### D7 — Governance

Nivel **CRITICAL** (RBAC/auth + datos personales de directorio + migracion de datos con cambio de comportamiento de acceso). Por governance, la implementacion REQUIERE aprobacion humana explicita antes de escribir codigo (el change queda propose-only). La porcion de guard de UI pertenece a `c-81` (tambien CRITICAL); este change no la toca.

### D8 — TDD y capas

Backend con pytest (subset SQLite offline + `@pytest.mark.integration`): tests de politica de rol, coherencia enum/CHECK/registro, visibilidad PROPIO/GLOBAL, resolucion de reportante por canal (mock de `ContactResolutionService`), destinatarios `mesa_de_ayuda`, y migracion (patron `test_migration_*.py`). Cada tarea sigue RED/GREEN/TRIANGULATE. Capas: ruta -> servicio -> repositorio -> modelo, sin logica en la ruta ni lazy-load.

### D9 — Empleado sintetico para la cuenta `admin` sembrada (OQ-3 resuelto)

**Decision**: la migracion `017` crea un `Empleado` con rol `administrador_directorio` para la cuenta `admin` de la migracion `003`, de modo que su alcance efectivo sea GLOBAL y no VACIO. El mecanismo es la MIGRACION (no el seed dev): la cuenta `admin` existe en TODOS los entornos, mientras que `scripts/seed_directorio.py` es dev-only y solo gestiona su propio `directorio.admin`. La regla "Alembic no siembra PII real" se respeta: el empleado es SINTETICO (legajo determinista `SYS-ADMIN`, nombre generico, `email` sintetico con dominio reservado `sys-admin@example.test`, `telefono` nulo), por lo que no hay PII. ATENCION: `email` es NOT NULL y UNIQUE por el esquema (`app/models/empleado.py:81-83`, DIR-002), por lo que NO puede quedar nulo; se usa el valor sintetico del dominio reservado `.test` (misma convencion que `scripts/seed_directorio.py`). El insert es CONDICIONAL e IDEMPOTENTE: solo si existe el usuario `admin` y NO tiene empleado vinculado (`directorio_empleado.user_id`), con SQL crudo y sin importar modelos (mismo estilo que la migracion `003`). El modo VACIO sigue existiendo para cuentas sin empleado.

**Alternativas**: crear el empleado en el seed dev (no cubre produccion: la cuenta `admin` quedaria VACIO); una excepcion de codigo que trate a `admin` como GLOBAL (duplica el conocimiento de rol fuera del registro y rompe "fuente unica"). Se elige la migracion por cobertura universal y por no introducir una excepcion de rol.

### D10 — Derivacion a revision humana ante reportante no identificado (OQ-1 resuelto)

**Decision**: `create_and_classify` deriva `requiere_revision_humana = (confianza < 0.70) OR (reportante no identificado)`, donde "no identificado" cubre: contacto de canal ausente (correo/telefonia), contacto que no resuelve a un empleado ACTIVO (NO ENCONTRADO o AMBIGUO), o cuenta web sin empleado vinculado. La derivacion persiste `reportante_empleado_id = NULL` y NO bloquea el alta. El OR garantiza que un incidente ya marcado por el clasificador NUNCA deje de requerir revision; la identificacion exitosa del reportante no fuerza revision por si misma (el flag sigue dependiendo del clasificador).

**Nota de contrato**: `openspec/specs/n8n-workflow/spec.md` afirma hoy `requiere_revision_humana = confianza < 0.70`; el OR de este change AMPLIA esa condicion. El gate post-POST de N8N solo lee el flag booleano, por lo que su comportamiento no cambia; la reconciliacion del texto de esa spec queda como follow-up documental (tarea 9.4), fuera del delta de este change (que se limita a `incident-visibility`).

## Risks / Trade-offs

- [Cambio de comportamiento de acceso al quitar el aislamiento por sector] -> El mapeo `operador -> mesa_de_ayuda` es GLOBAL; se documenta el cambio de alcance y se cubre con tests; requiere aprobacion humana (CRITICAL).
- [Incidentes historicos sin reportante quedan invisibles para `usuario_final`] -> Documentado; no hay backfill fiable para correo/telefono legacy. Los roles GLOBAL los siguen viendo.
- [Reportante no resuelto o ambiguo deja el incidente sin duenio] -> RESUELTO (OQ-1/D10): se persiste NULL y el incidente se deriva a revision humana (`requiere_revision_humana = true`), sin bloquear el alta.
- [La cuenta `admin` sembrada no tiene empleado -> VACIO] -> RESUELTO (OQ-3/D9): la migracion `017` le crea un empleado `administrador_directorio` sintetico -> alcance GLOBAL; el modo VACIO queda para cuentas sin empleado.
- [Derivacion a revision humana por reportante no identificado] -> Se combina por OR con el clasificador (nunca quita una revision ya marcada); se cubre con tests en la tarea 7.5/7.6.
- [Regenerar `docs/openapi.json`] -> Tarea explicita; `test_openapi_sync.py` falla si se olvida.

## Migration Plan

1. Nuevo modulo de politica + refactor de consumidores (enum, privilegio, visibilidad, guards — incluido el paso de lista negra a lista blanca en `require_directorio_lectura` —, destinatarios), sin cambiar aun el vocabulario observado.
2. Migracion `017`: columna de reportante + CHECK nuevo + backfill `operador -> mesa_de_ayuda` + empleado sintetico de la cuenta `admin` (condicional/idempotente).
3. Cablear la resolucion del reportante en el alta, aplicar el OR de revision humana (D10) y actualizar schemas; regenerar `docs/openapi.json`.
4. Rollback: `alembic downgrade 016` restaura el vocabulario (sin re-marcar `operador`), elimina la columna de reportante y el empleado sintetico de `admin`; revertir el commit. La migracion es append-only.

## Open Questions (RESUELTAS)

Todas las preguntas fueron resueltas por el autor. Se conservan con su resolucion:

- **OQ-1 — RESUELTA**: el contacto del reportante se toma IMPLICITAMENTE del canal (email del remitente en correo, telefono del llamante en telefonia; la cuenta autenticada en web), NUNCA lo tipea el usuario. El payload de N8N ya transporta ese contacto. Resultado: id del empleado o NULL. NUEVO comportamiento: si el reportante NO se identifica (sin contacto, contacto no resoluble a un empleado ACTIVO, o cuenta web sin empleado) el incidente se deriva a revision humana (`requiere_revision_humana = true`) ademas de persistir `reportante_empleado_id = NULL`. Se mantiene la regla de NO elegir arbitrariamente ante AMBIGUO. Detalle en D3/D10 y requisito VIS-005.
- **OQ-2 — RESUELTA**: SI, las filas existentes con `rol='operador'` se migran a `mesa_de_ayuda` (backfill ANTES del CHECK nuevo). El `downgrade` NO re-marca filas (mapeo no reversible). Detalle en D5.
- **OQ-3 — RESUELTA**: SI, se crea un `Empleado` `administrador_directorio` (sintetico, sin PII real) para la cuenta `admin` sembrada, de modo que su alcance sea GLOBAL y no VACIO. Mecanismo: MIGRACION `017` (condicional e idempotente), no el seed dev. Detalle en D9.
- **OQ-4 — RESUELTA (CONFIRMADA)**: `mesa_de_ayuda` y `administrador_directorio` MAY leer el directorio; `usuario_final` NO. Esto corrige el bug de lista negra de `require_directorio_lectura` (`app/routes/directorio.py:71-78`). Detalle en D2 y requisito RP-004.
