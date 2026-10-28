## 1. Preparacion, red de seguridad y puerta de gobernanza

- [x] 1.1 Activar el hook y confirmar el estado del change (`git config core.hooksPath .githooks`; `openspec status --change c-153-endurecer-el-directorio-para-datos-reales --json`). Verificacion: el status lista proposal/specs/design como `done` y `tasks` como artefacto pendiente de completar.
- [x] 1.2 Correr la red de seguridad del directorio antes de tocar nada (`cd App/Backend; pytest tests/ -k directorio -m "not integration" -q`) y registrar el baseline (N tests pasando). Verificacion: baseline capturado; si hay fallos, detener y reportarlos como preexistentes.
- [x] 1.3 GATE (governance HIGH): registrar el estado de la aprobacion humana HIGH en `docs/directorio-evidencia-cumplimiento.md` seccion 4 y en `CHANGES.md` ANTES de implementar. Verificacion: el aviso declara CONCEDIDA (con fecha) o el change queda BLOQUEADO y ninguna tarea desde el grupo 2 en adelante se ejecuta. Mientras la aprobacion no exista, el directorio permanece en modo sintetico.

## 2. Tema A — Cifrado at-rest del contacto

- [x] 2.1 Crear el ADR de reversion en `docs/seguridad/` que revierta DIR-005, registre la motivacion (habilitar PII real con cifrado en reposo), las alternativas evaluadas y el vinculo con el hallazgo 5.34/8.12; marcar la justificacion por minimizacion previa como SUPERADA sin reescribir su contenido. Verificacion: el ADR existe, contiene la reversion, el motivo y las alternativas; la justificacion previa queda marcada como SUPERADA.
- [x] 2.2 RED: agregar en `App/Backend/tests/` un test que falla porque el email y el telefono se leen en claro en la fila del directorio. Verificacion: `cd App/Backend; pytest tests/ -k directorio -m "not integration" -q` falla en el caso nuevo.
- [x] 2.3 GREEN: convertir `email` y `telefono` a `EncryptedText` en `App/Backend/app/models/empleado.py`. Verificacion: el test 2.2 pasa y la red de seguridad del directorio (1.2) sigue verde.
- [x] 2.4 RED (no-plaintext): agregar un test de integracion (`@pytest.mark.integration`) que falla porque tras la migracion quedan valores en claro. Verificacion: `cd App/Backend; pytest -m integration tests/ -k directorio -q` falla en el caso nuevo.
- [x] 2.5 GREEN: crear la migracion Alembic REVERSIBLE que agrega las columnas y rellena (backfill) las filas existentes cifrando el contacto, con downgrade documentado. Verificacion: la migracion se aplica y revierte; el test 2.4 pasa.
- [x] 2.6 TRIANGULATE: casos con y sin telefono, multiples filas, y verificacion de que el ciphertext es distinto por fila (IV de Fernet). Verificacion: todos los casos pasan.
- [x] 2.7 REFACTOR: encapsular el acceso cifrado sin cambiar comportamiento. Verificacion: `cd App/Backend; pytest tests/ -k directorio -m "not integration" -q` verde tras cada paso.

## 3. Tema B — Indice ciego y busqueda determinista

- [x] 3.1 RED: agregar tests que fallan porque no existen `email_bidx`/`telefono_bidx` ni la busqueda por indice. Verificacion: los tests nuevos fallan.
- [x] 3.2 GREEN: agregar las columnas `email_bidx` y `telefono_bidx` (HMAC-SHA-256 de la forma normalizada) y un helper de derivacion con la clave dedicada `directory_blind_index_key`; apuntar las busquedas de `empleado_repository.py` al indice ciego. Verificacion: los tests 3.1 pasan y la red de seguridad sigue verde.
- [x] 3.3 Preservar la unicidad del email sobre el indice determinista y mantener la unicidad del telefono repetible (sin unique) sobre `telefono_bidx`. Verificacion: el alta con email duplicado se rechaza; dos empleados con el mismo telefono se persisten.
- [x] 3.4 TRIANGULATE: tests de determinismo (mismo valor y clave -> mismo digest), dependencia de clave (clave distinta -> digest distinto) y ausencia de colisiones en el conjunto de prueba. Verificacion: los tres casos pasan.
- [x] 3.5 REFACTOR: extraer la derivacion del indice ciego a una funcion pura y testeable. Verificacion: `cd App/Backend; pytest tests/ -k directorio -m "not integration" -q` verde.

## 4. Tema C — Control de acceso

- [x] 4.1 RED: agregar tests que fallan porque no esta formalizado el acceso por sujeto ni la denegacion por defecto. Verificacion: los tests nuevos fallan.
- [x] 4.2 GREEN: formalizar en `App/Backend/app/services/role_policy.py` la politica de lectura del directorio: `administrador_directorio` y `mesa_de_ayuda` leen; `usuario_final` lee UNICAMENTE su propia fila; `gestion_incidentes` no lee. Verificacion: los tests 4.1 pasan.
- [x] 4.3 GREEN: aplicar limitacion de tasa y anti-enumeracion en los endpoints de lectura del directorio (`App/Backend/app/routes/directorio.py`). Verificacion: peticiones repetidas/masivas se acotan y las respuestas no revelan filas fuera de alcance.
- [x] 4.4 TRIANGULATE (aislamiento entre sectores, VIS-001/VIS-002): agregar un test NEGATIVO para `usuario_final` que verifica que no accede a filas ajenas ni a incidentes fuera de su alcance. Verificacion: el test negativo pasa y la verificacion de aislamiento sigue verde.
- [x] 4.5 REFACTOR: consumir la politica desde el registro unico (sin listas de rol duplicadas). Verificacion: `cd App/Backend; pytest tests/ -k "directorio or role_policy" -m "not integration" -q` verde.

## 5. Tema D — Auditoria durable

- [x] 5.1 RED: agregar tests que fallan porque no existe almacen durable de auditoria del directorio. Verificacion: los tests nuevos fallan.
- [x] 5.2 GREEN: crear la tabla de auditoria durable append-only sin PII (patron de `incidente_evento`) con su migracion; sin endpoint de edicion ni borrado. Verificacion: los tests 5.1 pasan.
- [x] 5.3 GREEN: enrutar la auditoria del directorio al almacen durable ADEMAS de structlog (`directorio_service.py`). Verificacion: cada operacion produce una fila durable con actor, operacion, resultado e instante.
- [x] 5.4 GREEN: registrar en el almacen durable la auditoria de los canales de resolucion de contacto, sin el valor de contacto en claro. Verificacion: la resolucion por email/telefono deja traza durable sin PII.
- [x] 5.5 TRIANGULATE: tests que prueben que la tabla NO contiene email, telefono ni nombre en claro, y que es append-only. Verificacion: ambos casos pasan.
- [x] 5.6 REFACTOR: compartir el helper de emision de eventos de auditoria sin duplicar logica. Verificacion: `cd App/Backend; pytest tests/ -k directorio -m "not integration" -q` verde.

## 6. Tema E — Retencion, ARCO y minimizacion

- [x] 6.1 Documentar el runbook operativo y la alerta de acumulacion de filas que superan `fecha_baja + 1 año` sin purgar, SIN introducir cron/scheduler/worker en el codigo. Verificacion: el runbook existe; un test verifica que no hay automatizacion de purga.
- [x] 6.2 Implementar la alerta operativa de acumulacion (conteo, sin PII). Verificacion: con filas vencidas acumuladas se emite la alerta; la alerta no expone datos personales.
- [x] 6.3 Documentar el ARCO de ACCESO y RECTIFICACION (ademas de la supresion) con procedimiento y constancia auditable, alineado con `docs/seguridad/procedimiento-arco.md`. Verificacion: el procedimiento cubre acceso y rectificacion con plazos y constancia; no limita el ARCO a la supresion.
- [x] 6.4 Definir y documentar la ventana de retencion de los registros de auditoria del directorio, alineada con el ciclo de vida. Verificacion: la ventana queda documentada en `docs/seguridad/` y es coherente con el borrado del directorio.
- [x] 6.5 Re-ejecutar la revision de minimizacion y confirmar que no se agregan columnas PII (solo el indice ciego no-PII). Verificacion: `grep -n` sobre `models/empleado.py` no muestra campos personales nuevos; la verificacion de minimizacion pasa.

## 7. Tema F — Operacion, gobernanza y specs

- [x] 7.1 Extender el inventario de `App/Backend/scripts/rotate_fernet_key.py` a las columnas cifradas del directorio y documentar las claves dedicadas (generacion, custodia, rotacion) en `docs/seguridad/gestion-secretos-y-rotacion.md`. Verificacion: el inventario cubre las columnas `EncryptedText` del directorio y el test de cobertura del inventario pasa.
- [x] 7.2 Agregar las nuevas variables de clave dedicada en `App/Backend/app/config/settings.py`, `App/Backend/.env.example`, `App/Backend/tests/conftest.py` y la dummy de la CI (`.github/workflows/ci.yml`). Verificacion: `cd App/Backend; pytest -m "not integration" -q` verde con las variables provistas.
- [x] 7.3 Reemplazar la compuerta "sin mecanismo de activacion" por el mecanismo deliberado y auditado (migracion/env gateado + artefacto de aprobacion), bloqueado por defecto. Verificacion: sin aprobacion no hay activacion; con aprobacion registrada la activacion queda auditada; no existe interruptor oculto.
- [x] 7.4 Al archivar, sincronizar el delta de `employee-directory`: remover DIR-005/DIR-010 y aplicar DIR-011/DIR-016, mas las modificaciones de DIR-002/DIR-006/DIR-009 y los agregados DIR-012/DIR-013/DIR-015. Verificacion: `openspec validate --strict c-153-endurecer-el-directorio-para-datos-reales` pasa y el archivo no conserva escenarios contradictorios.
- [x] 7.5 Regenerar `docs/openapi.json` si el contrato de lectura del directorio cambia, con el generador canonico. Verificacion: `cd App/Backend; python scripts/export_openapi.py` y `pytest tests/test_openapi_sync.py -v` verde.
- [x] 7.6 Actualizar los procedimientos de `docs/seguridad/` (retencion, ARCO, minimizacion, secretos) y `docs/directorio-evidencia-cumplimiento.md` para reflejar el estado real. Verificacion: las referencias cruzadas resuelven y no queda texto stale sobre "texto plano" ni sobre "sin mecanismo de activacion".
- [x] 7.7 Registrar en `CHANGES.md` el nuevo change y, cuando se conceda, la aprobacion humana HIGH con su fecha. Verificacion: `CHANGES.md` lista `c-153` y la aprobacion figura como CONCEDIDA solo si existe de forma verificable.

## 8. Verificacion de integracion y validacion OPSX

- [x] 8.1 Correr la suite backend completa (subconjunto offline y subconjunto de integracion contra la base desechable) y confirmar que no hay regresiones. Verificacion: `cd App/Backend; pytest -m "not integration" -q` y `cd App/Backend; pytest -m integration -q` verdes.
- [x] 8.2 Correr lint backend y verificar el build del frontend si cambia el contrato. Verificacion: `cd App/Backend; ruff check .` sin errores; `cd App/Frontend; npm run build` y `npm run lint` sin errores si aplica.
- [x] 8.3 Validar el change con `openspec validate --strict --no-interactive c-153-endurecer-el-directorio-para-datos-reales`. Verificacion: la validacion pasa sin errores.
- [x] 8.4 Revision humana (governance HIGH): confirmar que el ADR de reversion, el mecanismo de activacion, la auditoria durable sin PII y el no-PII en logs estan completos y que la aprobacion humana HIGH precede a toda implementacion. Verificacion: checklist firmado por el autor.
