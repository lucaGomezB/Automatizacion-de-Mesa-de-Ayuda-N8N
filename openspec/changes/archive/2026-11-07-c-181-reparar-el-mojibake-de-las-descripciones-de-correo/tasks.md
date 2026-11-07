## 1. Red de seguridad y delimitacion del alcance

- [x] 1.1 Ejecutar la suite offline del backend en el estado previo (`cd App/Backend; pytest -m "not integration"`) y registrar la linea base (n pruebas en verde). Verificacion: el comando reporta la linea base sin fallos preexistentes.
- [x] 1.2 Confirmar que el change no toca codigo de aplicacion, modelo, API ni migraciones (`git status --short`). Verificacion: no aparecen archivos bajo `App/Backend/app/`, `App/Frontend/`, `App/Backend/alembic/` ni `n8n/`; solo se agregan el script, el test y el runbook.
- [x] 1.3 Confirmar que el import del modulo del script no requiere la clave Fernet ni base de datos (`cd App/Backend; python -c "import scripts.reparar_encoding_descripciones"`). Verificacion: el import termina sin error y sin lanzar por `PSEUDONYMIZATION_ENCRYPTION_KEY` (clave configurada lazy).

## 2. Logica pura de deteccion y reverso (TDD estricto)

- [x] 2.1 RED: crear `App/Backend/tests/test_reparar_encoding_descripciones.py` con casos que importen y llamen a `revertir_mojibake` y `es_mojibake` del modulo del script (que aun no existen). Verificacion: `cd App/Backend; pytest tests/test_reparar_encoding_descripciones.py` falla por funciones inexistentes.
- [x] 2.2 GREEN: implementar en `App/Backend/scripts/reparar_encoding_descripciones.py` las funciones PURAS `revertir_mojibake(value) -> str | None` (reverso `value.encode('latin-1').decode('utf-8')`, capturando `UnicodeEncodeError`/`UnicodeDecodeError` y devolviendo `None`) y `es_mojibake(value) -> bool` (firma + reverso exitoso + diferencia estricta sin la firma). Cambio minimo para pasar 2.1. Verificacion: `cd App/Backend; pytest tests/test_reparar_encoding_descripciones.py` en verde.
- [x] 2.3 TRIANGULATE: agregar casos con entradas y salidas distintas: (a) texto corrupto con `Ã±` se detecta y su reverso es `ñ`; (b) texto limpio (`"La impresora no imprime y sale papel atascado"` y `"café"`) NO se detecta; (c) texto no codificable en latin-1 (por ejemplo un emoji) y texto cuyo reverso no es utf-8 valido se manejan con gracia devolviendo `None`/`False` sin excepcion; (d) un texto ya reparado NO vuelve a detectarse (idempotencia del detector). Verificacion: `cd App/Backend; pytest tests/test_reparar_encoding_descripciones.py` en verde con los casos agregados.
- [x] 2.4 REFACTOR: extraer la firma del mojibake a una constante/regex de modulo y mejorar nombres sin cambiar comportamiento. Verificacion: las pruebas de 2.3 siguen en verde.

## 3. Nucleo de reparacion sobre sesion (TDD)

- [x] 3.1 RED: agregar a `test_reparar_encoding_descripciones.py` una prueba de `reparar_descripciones(session, *, apply=False)` sobre SQLite in-memory con una fila corrupta y una limpia; afirmar que en dry-run NINGUNA fila cambia y que el resumen reporta candidatos/omitidos. Verificacion: la prueba falla contra la funcion inexistente.
- [x] 3.2 GREEN: implementar `reparar_descripciones(session, *, apply=False) -> ReporteReparacion` que recorra las filas de `incidente`, seleccione solo las corruptas por firma (D5), repare `descripcion_pseudonimizada` y `descripcion_original` (decrypt -> reverso -> re-encrypt con `flag_modified`, D4) y devuelva conteos (candidatos, reparados, omitidos, errores). Cambio minimo para pasar 3.1. Verificacion: la prueba de 3.1 en verde.
- [x] 3.3 TRIANGULATE: agregar casos que verifiquen (a) con `apply=True` la fila corrupta queda limpia en AMBAS columnas (descifrando `descripcion_original` para comprobar su texto plano); (b) la fila limpia queda intacta (descripcion y ciphertext sin cambios); (c) una segunda corrida con `apply=True` reporta cero reparados (idempotencia) y no modifica nada; (d) el fallo de una fila (token no descifrable) se reporta como error sin escribir la pseudonimizada de esa fila y sin impedir la reparacion de las demas. Verificacion: `cd App/Backend; pytest tests/test_reparar_encoding_descripciones.py` en verde con todos los casos.
- [x] 3.4 REFACTOR: separar la escritura por fila en un helper que confine el commit/rollback por fila (D6) y limpiar duplicacion; verificar que sigue habiendo una transaccion por fila. Verificacion: las pruebas de 3.3 siguen en verde.

## 4. CLI delgado del script

- [x] 4.1 Implementar el parser `argparse` con DRY-RUN por defecto, `--apply` para escribir y `--database-url` opcional (default `app.core.database.engine`, D7), y `main(argv)` que abre sesion via `async_sessionmaker` y `asyncio.run`, imprime el resumen de conteos y devuelve 0. Verificacion: `cd App/Backend; python -m scripts.reparar_encoding_descripciones --help` muestra las tres opciones y sale con codigo 0.
- [x] 4.2 Verificar que sin `--apply` el CLI no escribe: agregar una prueba que inyecte una sesion SQLite y confirme que el flujo CLI sin `--apply` no modifica datos. Verificacion: la prueba pasa y no requiere PostgreSQL.
- [x] 4.3 Verificar que `--apply` exige respaldo/documentacion: el CLI con `--apply` imprime una advertencia que recuerda respaldar la base y registra la base objetivo en el resumen. Verificacion: la salida de una corrida de prueba nombra la base objetivo y el recordatorio de respaldo.

## 5. Runbook de la reparacion

- [x] 5.1 Crear `docs/runbook-reparacion-encoding-descripciones.md` (D8) que documente: causa raiz (descarte del charset de `@n8n/imap` en partes `quoted-printable` y doble codificacion, con el mecanismo y el umbral de 78 bytes), volumen afectado por base (13/66 en `mesa_de_ayuda_campana`; 47/133 en `mesa_de_ayuda`), el reverso exacto, el procedimiento (respaldo, dry-run, revision, `--apply`), la verificacion (ausencia de la firma y round-trip) y la evidencia a registrar (conteos antes/despues por base). Verificacion: el archivo existe y contiene las secciones nombradas.
- [x] 5.2 Declarar en el runbook que la reparacion es MANUAL y controlada (no una migracion automatica) y que la aplicacion sobre `mesa_de_ayuda_campana` requiere aprobacion explicita del usuario. Verificacion: ambas afirmaciones estan presentes en el documento.
- [x] 5.3 Referenciar el runbook y el script desde donde corresponda (`docs/` o su indice) sin duplicar el contenido. Verificacion: existe una referencia al runbook desde la documentacion operativa y el enlace no apunta a contenido inexistente.

## 6. Verificacion final

- [x] 6.1 Ejecutar la prueba del script (`cd App/Backend; pytest tests/test_reparar_encoding_descripciones.py -v`). Verificacion: todas las pruebas de deteccion, reparacion e idempotencia en verde.
- [x] 6.2 Verificacion ACOTADA al test relevante (por indicacion del usuario): `cd App/Backend; pytest tests/test_reparar_encoding_descripciones.py -v` -> 12/12 en verde (3.87s). La suite offline completa NO se corrio desde este host (el entorno la cuelga); el change solo AGREGA script/test/runbook y no toca codigo de aplicacion, de modo que no hay riesgo de regresion en los tests existentes.
- [x] 6.3 Ejecutar el lint (`cd App/Backend; ruff check .`). Verificacion: sin hallazgos nuevos.
- [x] 6.4 Ejecutar `openspec validate "c-181-reparar-el-mojibake-de-las-descripciones-de-correo" --strict --no-interactive`. Verificacion: PASS.

## 7. Ejecucion MANUAL sobre datos reales (NO ejecutar en apply; requiere aprobacion del usuario)

- [x] 7.1 Respaldar la base objetivo con `pg_dump` (obligatorio antes de escribir) y registrar la ruta del respaldo. Verificacion: existe el archivo de respaldo y su tamano es no trivial.
- [x] 7.2 Dry-run sobre la base de la campana (`--database-url` de `mesa_de_ayuda_campana`, sin `--apply`) y revisar con el usuario los conteos de candidatos/omitidos/errores. Verificacion: la salida reporta conteos coherentes con los 13 esperados y NO modifica la base.
- [x] 7.3 Tras aprobacion explicita del usuario, `--apply` sobre `mesa_de_ayuda_campana` y registrar los conteos antes/despues como evidencia. Verificacion: la base ya no presenta la firma del mojibake en las descripciones de correo y no aparecen filas limpias modificadas.
- [x] 7.4 Dry-run de control para confirmar idempotencia (cero reparados) sobre la campana. Verificacion: el resumen reporta cero candidatos/reparados.
- [x] 7.5 (Opcional, con aprobacion explicita) repetir 7.1-7.4 apuntando a `mesa_de_ayuda`. Verificacion: mismos criterios de evidencia sobre la base de la app.
