## 1. Preparación y red de seguridad (safety net)

- [x] 1.1 Desde `App/Backend`, correr `pytest tests/test_n8n_workflow.py -q` y registrar el baseline (cantidad de tests passed/xfailed) antes de tocar el workflow; verificar que arranca en verde. Es la prueba de que C-47 no rompe lo existente.
- [x] 1.2 Confirmar con `git status` y `git diff --stat` que el único artefacto de producto a modificar es `n8n/workflow.json` (más tests y guía); no debe haber cambios en `App/Backend/app/` ni en `alembic/`.

## 2. RED — pruebas estructurales (TDD)

- [x] 2.1 Agregar a `App/Backend/tests/test_n8n_workflow.py` un test que exija un nodo `code` de restauración con conexión entrante desde `Guard de costo` y saliente hacia `Guard permite?`, cuyo `jsCode` referencie `$('Sellar ingreso telefonia').first()`; verificar que FALLA (RED) contra el workflow actual.
- [x] 2.2 Agregar un test que exija que el `AI Agent` sea alcanzable desde el nodo de restauración y que el `jsCode` de restauración fusione el item sellado (contenga `$('Sellar ingreso telefonia').first()`) y fije `allowed`; verificar que FALLA (RED).
- [x] 2.3 Agregar un test que inspeccione el `body` del nodo `Guard de costo` y exija que `caller` resuelva desde `$json` (`$json.From` / `$json.from`) y la AUSENCIA de toda referencia a `$('Sellar ingreso telefonia')` (ni `.item` ni `.first()`); verificar que FALLA (RED).
- [x] 2.4 Agregar un test de no regresión de C-46: el `jsCode` de `Derivar a revision humana` conserva `.first()`, emite `console.warn`/`ingreso_sellado_ausente` y fija `requiere_revision_humana`; verificar que PASA contra el workflow actual (guarda de no regresión, no transición RED→GREEN).
- [x] 2.5 Correr `pytest tests/test_n8n_workflow.py -q -k c47` y registrar la evidencia RED (los tests 2.1–2.3 fallan; 2.4 pasa).

## 3. GREEN — implementación del workflow

- [x] 3.1 Agregar en `n8n/workflow.json` el nodo `code` "Restaurar item telefonia" con `jsCode` que recupere `$('Sellar ingreso telefonia').first().json`, lea `$input.item.json.allowed` y devuelva `{...sellado, allowed}`; verificar que el JSON parsea (`python -c "import json; json.load(open('n8n/workflow.json'))"`).
- [x] 3.2 Re-cablear las conexiones `Guard de costo` main[0] → "Restaurar item telefonia" → `Guard permite?`, manteniendo intactas la salida de error de la guarda y la rama falsa hacia `Derivar a revision humana`; verificar que 2.1 y 2.2 pasan.
- [x] 3.3 Reemplazar en el `body` del nodo `Guard de costo` las dos apariciones de `$('Sellar ingreso telefonia').item` por el item corriente del propio nodo (`$json.From || $json.from`); verificar que 2.3 pasa y que 2.4 sigue pasando.
- [x] 3.4 Correr `pytest tests/test_n8n_workflow.py -q -k c47` y confirmar GREEN; correr `pytest tests/test_n8n_workflow.py -q` completo y confirmar 0 fallos.
- [x] 3.5 Triangular: agregar casos con datos distintos — (a) `caller` ausente resuelve `null` sin abortar la guarda; (b) la rama denegada conserva el contenido del item sellado en `Derivar a revision humana`; verificar que pasan.

## 4. Documentación

- [x] 4.1 Actualizar `docs/n8n-workflow-guide.md`: documentar la restauración del item a través de la guarda, actualizar la tabla de nodos (nodo nuevo entre 2d y 2e) y el conteo declarado de propiedades estructurales; verificar que `pytest tests/test_n8n_workflow.py -q -k test_c40_guide_test_count_matches_suite` pasa.

## 5. Verificación integral

- [x] 5.1 Desde `App/Backend`, correr `pytest -m "not integration" -q` y confirmar 0 fallos (suite offline completa).
- [x] 5.2 Correr `openspec validate --strict --changes c-47-guard-costo-item` y confirmar que pasa.
- [x] 5.3 Correr `ruff check tests/test_n8n_workflow.py` y confirmar "All checks passed".
- [ ] 5.4 Verificación manual en N8N en vivo (no bloqueante, documentar resultado): confirmar que el `AI Agent` recibe el item sellado (no solo el cuerpo de la guarda) y que el incidente telefonico se crea; dejar constancia en `docs/n8n-workflow-guide.md` de la limitación estructural de la suite.
