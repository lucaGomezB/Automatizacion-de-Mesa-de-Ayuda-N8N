## 1. Línea base y red de seguridad

- [ ] 1.1 Registrar el conteo de passed/skipped de la suite SQLite (`pytest -m "not integration"`) y de la suite de integración (`pytest -m integration`) antes de tocar `conftest.py`; verificación: ambos conteos quedan documentados en la evidencia del change.
- [ ] 1.2 Registrar el conteo de filas de la base de datos de la aplicación (por ejemplo `SELECT count(*) FROM incidente`) antes de la verificación; verificación: el valor queda documentado como referencia para demostrar que no cambió.

## 2. Fase RED — tests que fijan el contrato

- [ ] 2.1 Escribir un test que afirme que, sin `TEST_PG_URL`, la URL resuelta por `_get_pg_url()` apunta a una base con marcador de test y NO a `mesa_de_ayuda`; verificación: el test FALLA contra el código actual (RED).
- [ ] 2.2 Escribir un test que afirme que la guardia aborta (exit code distinto de cero y mensaje accionable) cuando la base destino coincide en nombre con la base de la aplicación y no hay habilitación explícita; verificación: el test FALLA contra el código actual (RED).
- [ ] 2.3 Escribir un test que afirme que `TEST_PG_URL` definida se honra como destino efectivo; verificación: el test pasa (comportamiento ya existente que no debe romperse).

## 3. Resolución de la URL de test

- [ ] 3.1 Cambiar el default de `_get_pg_url()` para resolver a la base descartable dedicada `mesa_de_ayuda_test` derivada de las credenciales de desarrollo; verificación: el test 2.1 pasa (GREEN).
- [ ] 3.2 Mantener `TEST_PG_URL` como override con prioridad sobre el default; verificación: el test 2.3 sigue en verde.
- [ ] 3.3 Verificar que ningún camino de resolución, con `TEST_PG_URL` ausente, produce el nombre de la base de la aplicación; verificación: el test 2.1 cubre los caminos y pasa.

## 4. Guardia de seguridad

- [ ] 4.1 Implementar la comparación del nombre de base destino contra el de la base de la aplicación (derivada de `DATABASE_URL`) antes de aplicar DDL destructivo; verificación: el test 2.2 pasa (GREEN).
- [ ] 4.2 Emitir un mensaje de aborto accionable que nombre la base destino, la base de la aplicación y la remediación, con exit code distinto de cero; verificación: el escenario de aborto del test 2.2 verifica mensaje y código.
- [ ] 4.3 Implementar la habilitación explícita `TEST_PG_ALLOW_APP_DB` como única vía para permitir un destino cuyo nombre coincide con la base de la aplicación; verificación: un test con la variable definida procede sin abortar y sin ella aborta.
- [ ] 4.4 Verificar que la guardia evalúa ANTES de cualquier `drop_all`/`create_all`; verificación: en el caso de aborto, la base de la aplicación no sufre DDL.

## 5. Aprovisionamiento y descarte de la base descartable

- [ ] 5.1 Implementar la creación de la base descartable vía conexión de mantenimiento (base `postgres` del mismo servidor, derivando host/puerto/credenciales del destino); verificación: la base existe durante la corrida y se consulta su nombre.
- [ ] 5.2 Integrar el aprovisionamiento con el fixture de esquema de sesión (`pg_schema`): crear la base, luego `drop_all` + `create_all` + seed dentro de ella; verificación: los tests de integración obtienen el catálogo sembrado.
- [ ] 5.3 Implementar el descarte en el teardown: disponer todos los engines y ejecutar `DROP DATABASE`; verificación: la base descartable ya no existe al terminar la sesión.
- [ ] 5.4 Implementar el fallback cuando `CREATE DATABASE` no es posible: continuar con el ciclo de esquema sobre el destino resuelto solo si NO es la base de la aplicación, emitiendo advertencia visible; verificación: un test simula el escenario y comprueba la advertencia y la ausencia de aborto indebido.
- [ ] 5.5 Verificar que el descarte maneja el caso de conexiones activas sin colgar la sesión; verificación: la suite de integración termina sin procesos colgados y con la base eliminada.

## 6. Preservación de las garantías de c-29 y regresión

- [ ] 6.1 Verificar que PostgreSQL ausente sigue fallando ruidosamente (exit code distinto de cero, sin skips, mensaje con la URL efectiva y la remediación); verificación: ejecución con una URL no alcanzable.
- [ ] 6.2 Verificar que el listener `PRAGMA foreign_keys=ON` del engine SQLite permanece intacto; verificación: test de violación de FK en SQLite falla como corresponde.
- [ ] 6.3 Verificar que el scope de event loop declarado y el scope de función de `pg_engine` permanecen intactos; verificación: la suite SQLite y la de integración no levantan `RuntimeError` de loop.
- [ ] 6.4 Verificar que la suite de integración completa corre en verde contra la base descartable; verificación: `pytest -m integration -v` sin fallos.
- [ ] 6.5 Verificar que la base de datos de la aplicación queda intacta tras la corrida completa; verificación: el conteo registrado en 1.2 no cambió.

## 7. Corrección de la documentación

- [ ] 7.1 Corregir `AGENTS.md`: declarar que el subconjunto de integración requiere una instancia PostgreSQL, acotar la afirmación de "offline / no Docker" a la suite SQLite y documentar el flujo local seguro con el destino descartable; verificación: los scenarios de documentación del spec se cumplen.
- [ ] 7.2 Corregir la descripción de `testing` del backend en `openspec/config.yaml` para mencionar el subconjunto de integración PostgreSQL además de SQLite in-memory; verificación: la sección refleja ambas suites.
- [ ] 7.3 Revisar `CLAUDE.md` y `README.md` y corregir cualquier afirmación que repita el "offline / sin Docker" sin acotar; verificación: no queda la afirmación sin acotar en los documentos de desarrollo.
- [ ] 7.4 Documentar el comando del flujo local seguro (levantar PostgreSQL y ejecutar `-m integration` apuntando a la base descartable) y la excepción `TEST_PG_ALLOW_APP_DB`; verificación: el comando documentado se ejecuta y no toca la base de la aplicación.

## 8. Compatibilidad con CI y cierre

- [ ] 8.1 Verificar que la guardia no bloquea el escenario del CI (nombres de base distintos entre `DATABASE_URL` y `TEST_PG_URL`); verificación: simular las variables del CI y comprobar que la suite procede sin `TEST_PG_ALLOW_APP_DB`.
- [ ] 8.2 Confirmar que `.github/workflows/ci.yml` no requiere cambios; verificación: el diff del change no toca el workflow y el escenario de D3 se cumple.
- [ ] 8.3 Registrar el conteo posterior de passed/skipped y compararlo con la línea base de 1.1; verificación: no hay regresiones atribuibles a la infraestructura modificada.
- [ ] 8.4 Ejecutar `openspec validate c-32-disposable-test-db` y confirmar que el change es válido; verificación: validación sin errores.
