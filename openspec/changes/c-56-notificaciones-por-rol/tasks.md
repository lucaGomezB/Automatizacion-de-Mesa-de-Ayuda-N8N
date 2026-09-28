## 1. Preparacion, decisiones y safety net

- [ ] 1.1 Resolver las Open Questions del `design.md` con el humano antes de escribir codigo: (a) D2 contrato (respuesta de alta vs webhook dedicado); (b) D8 frontera de PII de los emails de operador frente a `DIR-006`; (c) D7 alcance (solo sector principal); (d) D3 propiedad del fallback; (e) disponibilidad de la casilla Gmail de c-55 y de un operador en el directorio para el smoke. Si la decision difiere de la recomendacion, actualizar `proposal.md`, `design.md` y los specs ANTES de continuar. Verificacion: decisiones registradas en `design.md` (Open Questions marcadas RESUELTAS) o documento de decision adjunto.
- [ ] 1.2 Registrar el baseline: `cd App/Backend; pytest -m "not integration" -q` y anotar el conteo en verde. Registrar tambien el baseline dirigido: `pytest -m "not integration" tests/test_n8n_workflow.py tests/test_openapi_sync.py tests/test_incidentes.py -q`. Si algo falla, reportarlo como fallo preexistente y NO corregirlo en este change. Verificacion: conteo baseline anotado, sin fallos nuevos atribuibles al change.
- [ ] 1.3 Confirmar que c-54 (directorio + migraciones 009/010) y c-55 (`emailSend`/SMTP) estan archivados o, al menos, aplicados en el arbol de trabajo; si no, registrar el bloqueo del apply. Verificacion: `directorio_empleado` existe en el esquema y el nodo del operador es `emailSend`.

## 2. Enumeracion de operadores por sector (repositorio)

- [ ] 2.1 RED: escribir `App/Backend/tests/test_notification_recipients.py` que exija `EmpleadoRepository.listar_operadores_por_sector(sector_id)` devolviendo SOLO empleados `activo=true` con `rol=operador` del sector, y lista vacia cuando no hay coincidencias. Verificacion: el test falla por metodo inexistente.
- [ ] 2.2 GREEN: agregar `listar_operadores_por_sector` a `App/Backend/app/repositories/empleado_repository.py` (consulta async, `selectinload` de `sector` si se serializa). Verificacion: los tests de 2.1 pasan.
- [ ] 2.3 TRIANGULATE: cubrir (a) sector con varios operadores; (b) operador inactivo excluido; (c) `usuario_final`/`administrador_directorio` excluidos; (d) sector `None` o inexistente devuelve lista vacia sin excepcion; (e) sin duplicados. Verificacion: casos en verde.
- [ ] 2.4 INTEGRATION: agregar a `App/Backend/tests/integration/` un caso `@pytest.mark.integration` que verifique la FK a `sector`, el indice de `sector_id` y la igualdad real de la enumeracion. Verificacion: `cd App/Backend; pytest -m integration` en verde contra la base descartable.

## 3. Servicio de destinatarios (seam c-54, sin duplicar)

- [ ] 3.1 RED: escribir los casos que describan `NotificationRecipientService.resolver_destinatarios_revision(sector_id) -> list[str]`: emails de operadores activos normalizados (`normalizar_email`), lista vacia ante 0 coincidencias, y trazabilidad (sector + resultado) SIN emails en claro. Verificacion: el test falla por servicio inexistente.
- [ ] 3.2 GREEN: crear `App/Backend/app/services/notification_recipient_service.py` que componga `EmpleadoRepository` y `normalizar_email`, reutilizando el directorio de c-54 sin reimplementar la resolucion de identidad. Verificacion: los tests de 3.1 pasan.
- [ ] 3.3 TRIANGULATE: cubrir 1 y N destinatarios, directorio vacio, sector nulo, y que no se emite ningun email en el log estructurado (inyectar un capturador de logs). Verificacion: casos en verde.

## 4. Contrato de alta y enganche en el servicio (RED/GREEN)

- [ ] 4.1 RED: extender `App/Backend/tests/test_incidentes.py` (o el archivo de 2.1) para exigir que la respuesta de alta `POST /api/v1/incidentes` incluya `destinatarios_revision` poblada SOLO cuando `requiere_revision_humana=true`, con los operadores del sector; y vacia cuando no hay revision, cuando no hay sector o cuando el directorio no tiene operador. Verificacion: los tests fallan contra el contrato actual.
- [ ] 4.2 GREEN: agregar `destinatarios_revision` al modelo de respuesta de creacion en `App/Backend/app/schemas/incidente.py` (campo con default vacio o modelo dedicado de creacion, de modo que NO aparezca en `GET`/list) y poblar la lista en `IncidenteService.create_and_classify`/`_apply_classification` cuando haya revision. Verificacion: los tests de 4.1 pasan.
- [ ] 4.3 GREEN: asegurar que un fallo o directorio vacio en la resolucion NO propaga excepcion ni altera la respuesta; la lista queda vacia y el flujo continua. Verificacion: test que simula el directorio vacio y obtiene `201` con lista vacia.
- [ ] 4.4 TRIANGULATE: cubrir (a) un incidente de otro sector recibe los operadores de SU sector; (b) un incidente sin revision NO incluye destinatarios; (c) la resolucion no agrega una lectura cuando no hay revision (o se documenta la cota); (d) sin bloqueo observable de la respuesta. Verificacion: casos en verde.
- [ ] 4.5 Regenerar `docs/openapi.json` con el comando documentado y ejecutar `cd App/Backend; pytest tests/test_openapi_sync.py -v`. Verificacion: sincronizacion en verde.

## 5. Cableado N8N (RED/GREEN)

- [ ] 5.1 RED: extender `App/Backend/tests/test_n8n_workflow.py` para exigir: (a) un Code node `Preparar destinatarios de revision` que lee `destinatarios_revision` y usa `[ $env.OPERATOR_EMAIL ]` cuando esta vacio, emitiendo un item por destinatario; (b) `Notificar operador designado` usa `toEmail = {{ $json.destinatario }}` y NO la lista en un `To` compartido; (c) el respaldo `$env.OPERATOR_EMAIL` aparece solo en el nodo de preparacion; (d) `onError: continueRegularOutput`; (e) `Registro de auditoria` alcanzable desde la rama de revision aun si el envio falla. Verificacion: los tests fallan contra el workflow actual.
- [ ] 5.2 GREEN: editar `n8n/workflow.json`: agregar el Code node, rewire de `Requiere revision humana[true]` -> `Preparar destinatarios de revision` -> `Notificar operador designado`, y `Registro de auditoria` en paralelo desde la rama true; `toEmail` por item; `onError`. Verificacion: los tests de 5.1 pasan.
- [ ] 5.3 TRIANGULATE: prueba de no regresion de c-38/c-40/c-53/c-55 (gate post-POST intacto, `Confirmar correo en revision?`, cierre web, IMAP/SMTP, `Notificar operador designado` sigue siendo `emailSend`). Verificacion: casos en verde.

## 6. Documentacion

- [ ] 6.1 Actualizar `docs/n8n-workflow-guide.md`: describir `destinatarios_revision`, el Code node, el envio por destinatario, `OPERATOR_EMAIL` como RESPALDO, y ajustar el conteo de nodos (37 -> 38) y el de pruebas; sin secretos ni emails reales.
- [ ] 6.2 Documentar la resolucion por rol/sector, la precedencia/fallback y la frontera de PII (referencia a `design.md` D2/D3/D8) en la documentacion afectada; NUNCA emails reales.
- [ ] 6.3 Actualizar la tabla de variables de entorno de la guia y `docker-compose.yml`/`.env.example` si la descripcion de `OPERATOR_EMAIL` cambia (sin alterar su valor placeholder).

## 7. Verificacion final

- [ ] 7.1 Ejecutar la suite offline: `cd App/Backend; pytest -m "not integration"`. Verificacion: sin regresiones respecto del baseline de 1.2.
- [ ] 7.2 Ejecutar la suite de integracion: `cd App/Backend; pytest -m integration`. Verificacion: en verde contra la base descartable, sin tocar la base de aplicacion.
- [ ] 7.3 Ejecutar lint: `cd App/Backend; ruff check .`. Verificacion: sin errores E nuevos.
- [ ] 7.4 Ejecutar `openspec validate --strict --changes c-56-notificaciones-por-rol`. Verificacion: validacion estricta sin errores.
- [ ] 7.5 Smoke manual (requiere la casilla Gmail de c-55 y un operador cargado en el directorio): un incidente que requiere revision notifica al operador resuelto; con el directorio sin operador del sector, notifica al respaldo `OPERATOR_EMAIL`. Verificacion: correo recibido con el numero correcto y una entrada de auditoria. MANUAL, no automatizable en CI.
- [ ] 7.6 Revision humana (ALTO): confirmar la frontera de PII (emails de operador en la respuesta de alta autenticada), el alcance por sector principal y que no hay emails reales en los artefactos. Verificacion: aprobacion registrada antes de activar datos reales en el directorio.