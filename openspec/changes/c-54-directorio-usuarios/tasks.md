## 1. Preparación, decisiones y safety net

- [ ] 1.1 Resolver las Open Questions del `design.md` con el humano antes de escribir código: (a) origen de los datos — export RRHH vs CSV/API vs UI; (b) campos obligatorios y unicidad de email; (c) confirmar los tres roles; (d) política de ambigüedad; (e) clave del índice ciego; (f) retención/ARCO. Si la decisión difiere de la recomendación, actualizar `proposal.md`, `design.md` y los specs ANTES de continuar. Verificación: decisiones registradas en `design.md` (Open Questions marcadas RESUELTO) o documento de decisión adjunto.
- [ ] 1.2 Registrar el baseline de las suites afectadas: `cd App/Backend; pytest -m "not integration" tests/test_openapi_sync.py tests/test_auth.py` y anotar el conteo en verde. Si algo falla, reportarlo como fallo preexistente y NO corregirlo en este change. Verificación: conteo baseline anotado y sin fallos nuevos atribuibles al change.

## 2. Clave, normalización e índice ciego

- [ ] 2.1 RED: escribir `App/Backend/tests/test_blind_index.py` que exija (a) normalización de email a minúsculas/trim y de teléfono a E.164; (b) `blind_index(valor)` determinista (mismo valor normalizado => mismo hash); (c) valores distintos en mayúsculas/espacios colapsan al mismo hash; (d) entradas distintas producen hashes distintos; (e) el hash no expone el valor. Verificación: el test falla por módulo inexistente.
- [ ] 2.2 GREEN: crear `App/Backend/app/utils/blind_index.py` con los normalizadores y el HMAC-SHA256 usando una clave inyectada. Verificación: los tests de 2.1 pasan.
- [ ] 2.3 TRIANGULATE: cubrir teléfono inválido respecto de E.164 y email malformado (rechazo accionable), y que dos claves distintas producen hashes distintos para el mismo valor. Verificación: casos en verde.
- [ ] 2.4 RED: escribir un test que exija `directory_blind_index_key` en `App/Backend/app/config/settings.py` (sin default en claro) y su presencia en `.env.example`. Verificación: el test falla por clave inexistente.
- [ ] 2.5 GREEN: agregar `directory_blind_index_key` a `settings.py` y a `.env.example`. Verificación: el test de 2.4 pasa.

## 3. Modelo, migración y repositorio

- [ ] 3.1 RED: escribir `App/Backend/tests/test_empleado_model.py` que exija la tabla `directorio_empleado` con: nombre, email cifrado + `email_hash`, teléfono cifrado + `telefono_hash`, `sector_id` (FK nullable a `sector`), `rol` (enum de tres valores), `activo`, `user_id` (FK nullable a `users`), timestamps. Verificación: el test falla por modelo inexistente.
- [ ] 3.2 GREEN: crear `App/Backend/app/models/empleado.py` (ORM, `EncryptedText`, enums `RolEmpleado`) y registrarlo en `app/models/__init__.py`. Verificación: el test de 3.1 pasa en SQLite.
- [ ] 3.3 GREEN: crear la migración aditiva `App/Backend/alembic/versions/009_directorio_empleado.py` (revision `009`, `down_revision = "008"`) con tabla, índices sobre `email_hash`/`telefono_hash` y FKs (`ON DELETE SET NULL` para `user_id`). NO sembrar PII real (D8). Verificación: `cd App/Backend; alembic upgrade head` y `alembic downgrade -1` corren sin error.
- [ ] 3.4 RED: escribir `App/Backend/tests/test_empleado_repository.py` que exija búsquedas por `email_hash`, por `telefono_hash` y por `user_id`, devolviendo solo empleados activos y usando `selectinload` para `sector` cuando se serializa. Verificación: el test falla por repositorio inexistente.
- [ ] 3.5 GREEN: crear `App/Backend/app/repositories/empleado_repository.py` con las búsquedas por índice ciego y por `user_id`, y CRUD básico. Verificación: el test de 3.4 pasa.
- [ ] 3.6 TRIANGULATE: cubrir búsqueda que devuelve múltiples coincidencias (ambigüedad), empleado inactivo excluido, y sector nulo serializado sin lazy-load. Verificación: casos en verde.
- [ ] 3.7 INTEGRATION: agregar `App/Backend/tests/integration/test_directorio_postgres.py` marcado `@pytest.mark.integration` para verificar FK a `sector` y `users`, índices sobre los hash e igualdad real. Verificación: `cd App/Backend; pytest -m integration tests/integration/test_directorio_postgres.py` en verde contra la base desechable.

## 4. Servicio de directorio y autorización

- [ ] 4.1 RED: escribir `App/Backend/tests/test_directorio_service.py` que exija: alta con validación de campos (al menos email o teléfono), rol válido, E.164, normalización+hash al persistir, y desactivación en lugar de borrado. Verificación: el test falla por servicio inexistente.
- [ ] 4.2 GREEN: crear `App/Backend/app/services/directorio_service.py` con CRUD, reglas de activo y cálculo del índice ciego. Verificación: los tests de 4.1 pasan.
- [ ] 4.3 TRIANGULATE: cubrir registro sin ningún dato de contacto (rechazo), rol inválido (rechazo), sector inexistente (rechazo), y reactivación. Verificación: casos en verde.
- [ ] 4.4 RED: escribir un test que exija que el email/telefono en claro NO aparezca en los logs estructurados de una operación de alta o desactivación. Verificación: el test falla contra el logging ingenuo.
- [ ] 4.5 GREEN: ajustar los eventos de log del servicio para emitir solo identificadores internos y resultado, nunca el dato en claro. Verificación: el test de 4.4 pasa.

## 5. Resolución de contactos (seam c-53)

- [ ] 5.1 RED: escribir `App/Backend/tests/test_contact_resolution_service.py` que describa `resolver_por_telefono`, `resolver_por_email` y `resolver_por_usuario`, con un `ResultadoResolucion` que distinga encontrado / no encontrado / ambiguo. Verificación: el test falla por servicio inexistente.
- [ ] 5.2 GREEN: crear `App/Backend/app/services/contact_resolution_service.py` con dependencias inyectadas (repositorio) y el modelo de resultado. Verificación: los tests de 5.1 pasan.
- [ ] 5.3 TRIANGULATE: cubrir teléfono desconocido, email desconocido, usuario sin empleado vinculado, empleado inactivo, y coincidencia múltiple (ambigua => no concluyente). Verificación: casos en verde.
- [ ] 5.4 TRIANGULATE: cubrir que la resolución NO envía notificaciones (sin SMS/correo) y que registra trazabilidad (canal + resultado) sin PII en claro. Verificación: casos en verde.
- [ ] 5.5 Verificar el contrato de enganche: test que instancie la resolución con un directorio vacío y confirme que devuelve "no encontrado" sin excepción, de modo que c-53 conserve su resolución directa (RES-005). Verificación: el test pasa.

## 6. API de gestión, OpenAPI y documentación

- [ ] 6.1 RED: escribir `App/Backend/tests/test_api_directorio.py` que exija: escritura con rol `administrador_directorio` (éxito), escritura con otro rol (403), acceso anónimo (401), y lectura autorizada. Verificación: el test falla por rutas inexistentes.
- [ ] 6.2 GREEN: crear `App/Backend/app/schemas/directorio.py`, `App/Backend/app/routes/directorio.py` y la dependencia de autorización acotada al directorio; registrar el router. Verificación: los tests de 6.1 pasan.
- [ ] 6.3 TRIANGULATE: cubrir que las respuestas y los errores no incluyen email/telefono en claro y que el listado no expone PII completa. Verificación: casos en verde.
- [ ] 6.4 Regenerar `docs/openapi.json` con el comando documentado y ejecutar `cd App/Backend; pytest tests/test_openapi_sync.py -v`. Verificación: el test de sincronización pasa.
- [ ] 6.5 Documentar el directorio (campos, roles, resolución, política de PII/retención y el punto de enganche con c-53) en la documentación afectada, sin PII de ejemplo real. Verificación: documentación verificable y coherente con los specs.

## 7. Verificación final

- [ ] 7.1 Ejecutar la suite offline: `cd App/Backend; pytest -m "not integration"`. Verificación: sin regresiones respecto del baseline de 1.2.
- [ ] 7.2 Ejecutar la suite de integración del directorio: `cd App/Backend; pytest -m integration`. Verificación: en verde contra la base desechable, sin tocar la base de aplicación.
- [ ] 7.3 Ejecutar lint: `cd App/Backend; ruff check .`. Verificación: sin errores E nuevos.
- [ ] 7.4 Ejecutar `openspec validate --strict --changes c-54-directorio-usuarios`. Verificación: validación estricta sin errores.
- [ ] 7.5 Revisión humana (HIGH/CRITICAL): confirmar la clave del índice ciego, la política de retención/ARCO y que no hay PII en claro en el repositorio ni en la base. Verificación: aprobación registrada antes de activar datos reales.
