## Context

Ver `proposal.md — Why`. Restricciones verificadas que moldean el enfoque:

- **No existe un modelo de roles.** `App/Backend/app/models/user.py` (`users`) es exclusivamente autenticacion (`id`, `username`, `hashed_password`, `is_active`) y su docstring declara que NO se relaciona con `Incidente` ni con el dominio de clasificacion. Las unicas apariciones de "roles" en el codigo son etiquetas internas de contadores de costo (`app/cost_guard/guard.py`), sin relacion con autorizacion. Por lo tanto, definir roles es parte de este change.
- **Catalogo de sectores vs. categorias de clasificacion.** En el codigo vigente son el MISMO vocabulario: `app/constants.py` define `SECTORES_CANONICOS` con los cinco strings y la tabla `sector` (`app/models/catalog.py`) los persiste igual. NO existe en el codigo una derivacion de "tres sectores" (Sistemas/Operaciones/Soporte Tecnico): `Operaciones` fue eliminado (C-27) y `Sistemas` es categoria propia. El directorio MUST enlazar al catalogo `sector` existente; no se crea vocabulario nuevo.
- **Realidad de datos de contacto por canal.**
  - Correo: el remitente se captura en N8N (`remitente` en `Normalizar entrada del incidente`; `from` del trigger Outlook) y se usa para la confirmacion; no se persiste en el backend.
  - Web: el reportante esta autenticado (`Depends(get_current_user)`), pero `users` no tiene email y ni el formulario ni `IncidenteCreate` capturan uno.
  - Telefonia: el llamante se captura ENCRYPTED en `telefonia_ingreso.caller_cifrado`; el `From` esta disponible en el webhook de VOZ (`app/routes/cost_guard.py`). No hay email.
- **Cifrado existente.** `app/utils/encryption.py` provee `EncryptedText` (Fernet, NO determinista) sobre `pseudonymization_encryption_key`. El cifrado no determinista impide busqueda por igualdad directa: resuelve un indice ciego (blind index).
- **Convenciones.** Capas `routes -> services -> repositories -> models`; async SQLAlchemy con `selectinload()`; migraciones en `App/Backend/alembic/versions/` (ultima: `008`); identificadores de dominio en español.
- **Sibling `c-53-notificacion-numero-incidente`.** Ya propuesto; su design D10 declara que NO implementa el directorio y que la resolucion de contactos hoy es directa (el propio numero llamante), dejando el directorio como estrategia enchufable futura. c-53 funciona SIN el directorio; c-54 lo provee.

## Goals / Non-Goals

**Goals:**

- Modelar un directorio de empleados con datos de contacto, sector, rol y estado activo, separado de la autenticacion.
- Definir el modelo de roles que hoy no existe, con el minimo vocabulario que tiene uso real.
- Hacer resolubles telefono, email y usuario autenticado hacia un empleado, con "no encontrado" no fatal.
- Proteger la PII (Ley 25.326) con cifrado at-rest, indice ciego para busqueda y control de acceso.
- Dejar un contrato de resolucion estable para que c-53 lo consuma sin cambiar su entrega.

**Non-Goals:**

- Enviar notificaciones (c-53), SMS o correo.
- Twilio Media Streams / agente conversacional (diferido; tesis cap. 10).
- Sincronizar con un sistema de RRHH o construir una UI de administracion completa.
- RBAC transversal de toda la aplicacion ni cambios a los cinco sectores canonicos.
- Implementar codigo en esta fase (propose only).

## Decisions

### D1: Tabla propia `directorio_empleado`, NO extender `users`

Se crea una entidad dedicada (`directorio_empleado`) y se mantiene `users` como dominio de autenticacion. Razon: `users` es auth-only por diseno y su docstring prohibe mezclarlo con el dominio; extenderlo obligaria a que toda cuenta de acceso tenga datos de contacto y a que el directorio dependa del ciclo de vida del login. Se ofrece un vinculo opcional `user_id` (FK nullable a `users.id`) para saber que cuenta corresponde a que empleado, sin fusionar ambos dominios (DIR-001). Alternativa considerada: agregar `email`/`telefono`/`sector`/`rol` a `users` — descartada por acoplar PII al alta de credenciales y romper la separacion de responsabilidades.

### D2: Modelo de roles minimo de tres valores

Se define el rol como enum `RolEmpleado` con exactamente: `usuario_final`, `operador`, `administrador_directorio`. Uso real verificado: (a) `usuario_final` es el reportante, que no administra el directorio; (b) `operador` es quien atiende y puede ser destino de enrutamiento de su sector; (c) `administrador_directorio` es quien carga/mantiene la PII. Se descarta un RBAC con permisos granular: no hay caso de uso que lo justifique y aumentaria la superficie de seguridad. El rol NO interviene en la clasificacion (DIR-003). Alternativa considerada: derivar el rol implicitamente del sector — descartada: confundiria "que sector atiende" con "que puede hacer".

### D3: Vinculo al catalogo canonico `sector`, sin vocabulario nuevo

El directorio referencia `sector.id` (FK nullable). Se reutiliza el catalogo de cinco sectores vigente y NO se introduce una lista propia ni se resucita un conjunto de tres sectores. Esto alinea el enrutamiento por sector con la clasificacion ya existente (DIR-004). Alternativa considerada: guardar el nombre del sector como string en el directorio — descartada: permitiria strings fuera del vocabulario canonico y romperia la integridad referencial semantica.

### D4: Indice ciego (HMAC) + cifrado at-rest para email y telefono

La resolucion exige busqueda por igualdad, pero el cifrado Fernet del proyecto es no determinista. Se almacena: (a) el valor cifrado (`EncryptedText`) para retrieval autorizado y uso por c-53; (b) un indice ciego `HMAC-SHA256(clave, valor_normalizado)` en columna indexada para la busqueda. Normalizacion: email a minusculas y trim; telefono a E.164. Se agrega una clave dedicada `directory_blind_index_key` en `settings.py`/`.env.example` (distinta de la de cifrado) (DIR-005). Alternativa considerada: comparar descifrando todas las filas — descartada por costo y exposicion masiva de PII; alternativa considerada: hash sin clave — descartada por ser vulnerable a diccionario.

### D5: Acceso: gestion con rol, resolucion interna sin HTTP

La API de gestion vive en `routes/directorio.py` y exige autenticacion; las escrituras exigen rol `administrador_directorio` (dependencia de autorizacion nueva, acotada al directorio). La resolucion que consume c-53 es un servicio in-process (`contact_resolution_service`), sin borde HTTP ni token, para no ampliar la superficie de PII ni requerir red (DIR-006/RES-005). Se descarta exponer un endpoint de resolucion publico: seria un oraculo de PII. Alternativa considerada: enforcement de rol global — diferida; este change solo autoriza directorio.

### D6: Ambiguedad => no resuelve

Si un telefono/email normalizado corresponde a mas de un empleado activo (numeros de mesa de area, casilla compartida), la resolucion registra la ambiguedad y NO elige arbitrariamente (RES-004). Alternativa considerada: "primer match" — descartada por riesgo de notificar a la persona equivocada. Alternativa considerada: forzar unicidad estricta de email/telefono — descartada porque la realidad operativa admite casillas de area; se aplica unicidad a nivel de indice ciego como defensa, pero el contrato contempla la ambiguedad.

### D7: Ciclo de vida por desactivacion

`activo=false` en lugar de borrado; la resolucion ignora inactivos (DIR-007). El borrado fisico queda reservado a derechos ARCO. Alternativa considerada: soft-delete con timestamp — innecesario; el flag alcanza y mantiene la fila referenciable.

### D8: Migracion aditiva 009 y seed sin PII real

Nueva revision `009` (posterior a `008`), aditiva: crea `directorio_empleado` con indices (incluido el indice unico/indice del ciego) y FKs. NO se siembra PII real en la migracion de produccion: la fuente es RRHH (Open Question 1). Los tests usan fixtures que crean empleados sinteticos; el seed de demo, si se implementa, sera un script dev-only fuera de Alembic. Alternativa considerada: seed en la migracion — descartada por inventar PII y ensuciar produccion.

### D9: Estrategia de tests

- **Unit (SQLite, `-m "not integration"`)**: validaciones de campos/rol, normalizacion, calculo del indice ciego, reglas de autorizacion, resolucion encontrado/no-encontrado/ambiguo, no-PII en logs. El cifrado y el indice ciego son `TypeDecorator`/funciones puras y funcionan en SQLite.
- **Integration (PostgreSQL, `-m integration`)**: FK a `sector` y `users`, indices unicos sobre el ciego, comportamiento de `ON DELETE` y busqueda por igualdad real. Se usa la base desechable existente.

### D10: Contrato de enganche con c-53

`contact_resolution_service` expone `resolver_por_telefono`, `resolver_por_email` y `resolver_por_usuario`, cada una devolviendo un `ResultadoResolucion` con el empleado o vacio, distinguible de error. c-53 lo consume como estrategia opcional: sin contacto, conserva su resolucion directa. Este change NO toca el codigo de c-53 ni su contrato de entrega (RES-005). Dependencia: c-54 NO depende de que c-53 este implementado; c-53 PUEDE engancharlo cuando ambos esten aplicados. Orden sugerido de archivado: c-52 (ya presente) -> c-53 y c-54 en cualquier orden, ya que c-54 no modifica specs de c-53.

### D11: Gobierno (gobernanza)

- Entidad, cifrado, indice ciego, matching y control de acceso son **HIGH/CRITICAL**: PII de empleados y Ley 25.326. No se escribe codigo en esta fase; la implementacion requiere revision humana de la clave del indice ciego y de la politica de retencion.
- Migracion y API de gestion: **HIGH**. Repositorio/servicio/test: MEDIUM.

### D12: Sin cambios a clasificacion ni a notificaciones

No se tocan `constants.py`, el clasificador, los cinco sectores ni `n8n/workflow.json` en lo relativo a notificaciones. El unico cambio de configuración es la clave del indice ciego (D4).

## Risks / Trade-offs

- **[Fuga de PII]** email/telefono sensibles → Mitigacion: cifrado at-rest + indice ciego, sin PII en logs, acceso autorizado (DIR-005/006).
- **[Matching erroneo]** notificar a la persona equivocada → Mitigacion: igualdad exacta sobre normalizado; ambiguo => no resuelve (D6).
- **[Indice ciego vulnerable]** hash sin clave o clave filtrada → Mitigacion: HMAC con clave dedicada en configuracion; revision de seguridad (Open Question 5).
- **[Directorio vacio/desactualizado]** resolucion sin contacto → Mitigacion: "no encontrado" no fatal, c-53 sigue funcionando; deactivacion.
- **[Acoplamiento con c-53]** romper su entrega → Mitigacion: contrato estable y consume opcional (D10); c-54 no modifica specs ni codigo de c-53.
- **[Choque de migraciones]** varias changes activas → Mitigacion: 009 aditiva, no muta tablas previas.
- **[Sobre-ingenieria de roles]** RBAC excesivo → Mitigacion: solo tres roles y autorizacion acotada al directorio (D2/D5).
- **[Verificacion de PII en logs]** dificil de automatizar → Mitigacion: tests unitarios que aseveran ausencia del dato en claro.

## Migration Plan

1. Agregar `directory_blind_index_key` a `settings.py` y `.env.example` (sin valor en claro en el repo).
2. Crear `utils/blind_index.py` (funcion pura HMAC-SHA256 + normalizadores) con tests.
3. Modelo `models/empleado.py` (tabla `directorio_empleado`, enums, FKs) y migracion `009` aditiva.
4. Repositorio `empleado_repository.py` (busqueda por ciego, por email/telefono, por `user_id`) con `selectinload` donde aplique.
5. Servicio `directorio_service.py` (CRUD, activacion, reglas de rol) y `contact_resolution_service.py` (seam c-53).
6. Rutas `routes/directorio.py` + schemas + dependencia de autorizacion; regenerar `docs/openapi.json`.
7. Fixtures de tests (empleados sinteticos) y suites unit/integration.
8. Rollback: revertir el commit y ejecutar `cd App/Backend; alembic downgrade -1` (dropea la tabla; sin backfill). c-53 no se ve afectado.

## Open Questions

1. **Origen de los datos del directorio**: export de RRHH, carga CSV/API, o UI de administracion. Define si entra un frontend en este change. Recomendacion: API + herramienta de importacion; UI diferida.
2. **Campos obligatorios y unicidad**: legajo obligatorio; email unico por empleado o admitido por area (afecta D6).
3. **Vocabulario de roles**: confirmar los tres roles; si un operador pertenece a un solo sector.
4. **Politica de ambiguedad**: validar que casillas/numeros de area se tratan como "no concluyente" (D6).
5. **Clave del indice ciego**: nueva clave dedicada vs. derivada de la existente, y plan de rotacion. Revision de seguridad.
6. **Retencion y ARCO**: plazo de conservacion y proceso de supresion fisica (D7).
