## 1. Prerequisitos y anclaje canonico

- [x] 1.1 Verificar que `evaluation/data/campana/README.md` no se modifico: `git diff --quiet -- evaluation/data/campana/README.md` termina con exit 0 y `git status --porcelain evaluation/data/campana/README.md` no lista nada.
- [x] 1.2 Confirmar los valores canonicos que se van a transcribir: `sed -n '127,145p' evaluation/data/campana/README.md` muestra "un caso de cada diez por `posicion`", "20 casos en total", "O1 recibe 110" y "O2 recibe 110".
- [x] 1.3 Confirmar el registro real de sujetos: `cat evaluation/data/campana/registro_sujetos.csv` lista 8 filas (`E1`,`E2`,`O1`,`O2`,`A1`,`T1`,`T2`,`T3`) sin `A2` y sin solapes por `persona`.

## 2. `docs/campana-medicion/guia-ejecucion-campana.md`

- [x] 2.1 Corregir D1: reemplazar "100 casos cada uno" por "110 casos cada uno" (100 de su mitad + 10 cruzados) en la seccion 1.3 y en la seccion 3; verificar con `grep -n "110 casos" docs/campana-medicion/guia-ejecucion-campana.md` y `grep -c "100 casos cada uno"` = 0.
- [x] 2.2 Corregir D2: eliminar "opcional" del criterio de doble cobertura y declarar el criterio fijo (1 de cada 10 por `posicion` por mitad, 20 casos compartidos); verificar con `grep -n "un caso de cada diez" docs/campana-medicion/guia-ejecucion-campana.md` y `grep -n "opcional"` sin coincidencias en esa seccion.
- [x] 2.3 Corregir D5 y D6: agregar prerequisitos explicitos `alembic current` = `024 (head)`, app y N8N en pie; verificar con `grep -n "024 (head)" docs/campana-medicion/guia-ejecucion-campana.md`.
- [x] 2.4 Corregir D4: generar los 8 sub-planes (2 mitades x 2 brazos x 2 turnos) en la seccion 1.5; verificar con `grep -c "subplan_m" docs/campana-medicion/guia-ejecucion-campana.md` >= 8 y que aparezcan `_automatizado_`.
- [x] 2.5 Corregir D3: agregar la seccion del brazo automatizado con los 3 harnesses x 4 sub-planes `automatizado`, flags `--id-corrida`/`--sidecar`/`--json corpus_campana.json` y `--dry-run` primero; verificar con `grep -n "ingest_via_n8n.py\|ingest_corpus.py\|ingest_telefonia_corpus.py" docs/campana-medicion/guia-ejecucion-campana.md`.
- [x] 2.6 Corregir D7: declarar los sidecars (`evaluation/data/campana/sidecar_<id_corrida>.json`) como entradas producidas por el paso de harnesses; verificar con `grep -n "sidecar_<id_corrida>" docs/campana-medicion/guia-ejecucion-campana.md`.
- [x] 2.7 Corregir D8: reordenar el flujo para que el brazo automatizado quede entre la generacion de sub-planes y el export de intervenciones; verificar leyendo la seccion 1.5 y comprobando que el bloque de harnesses precede al bloque de export.
- [x] 2.8 Corregir D9: reemplazar la nota "solo falta la columna `persona`" por la descripcion del registro completo (8 filas, P1..P8, sin solapes); verificar con `grep -n "solo falta" docs/campana-medicion/guia-ejecucion-campana.md` = 0.
- [x] 2.9 Corregir D10: agregar `brazo_manual.csv` a la lista del gate de c-169; verificar con `grep -n "brazo_manual.csv" docs/campana-medicion/guia-ejecucion-campana.md` en la seccion 1.6.
- [x] 2.10 Corregir D11 y D12: envolver el export con `cd App/Backend`, agregar su verificacion de salida y declarar legados y vinculos faltantes; verificar con `grep -n "cd App/Backend" docs/campana-medicion/guia-ejecucion-campana.md` y que el texto mencione la verificacion del export.
- [x] 2.11 Corregir D13: reemplazar "director (Luca)" por "el director de la tesis"; verificar con `grep -n "Luca" docs/campana-medicion/guia-ejecucion-campana.md` = 0.
- [x] 2.12 Corregir D14: enumerar las cinco cadenas canonicas de sector; verificar con `grep -n "Seguridad Informatica" docs/campana-medicion/guia-ejecucion-campana.md` y que aparezcan las cinco.

## 3. `docs/campana-medicion/runbook-brazo-manual-e-intervencion.md`

- [x] 3.1 Alinear la doble cobertura: reemplazar "opcional y deseable" por el criterio fijo con conteos 110/110 y 20 casos compartidos; verificar con `grep -n "opcional y deseable" docs/campana-medicion/runbook-brazo-manual-e-intervencion.md` = 0 y `grep -n "110"` en la seccion 2.2.
- [x] 3.2 Alinear el registro de sujetos: reemplazar el ejemplo con `A2` por `A1` + `T1`; verificar con `grep -n "A2,analista_original" docs/campana-medicion/runbook-brazo-manual-e-intervencion.md` = 0.

## 4. `docs/campana-medicion/runbook-doble-etiquetado.md`

- [x] 4.1 Alinear el registro de sujetos: reemplazar `A2` por `A1` + `T1` en la tabla de alias y en el ejemplo sintetico; verificar con `grep -rwn "A2" docs/campana-medicion/runbook-doble-etiquetado.md` sin coincidencias (con palabra completa, para no matchear la subcadena de `SHA256`).

## 5. Verificacion transversal

- [x] 5.1 Verificar que no se toco codigo ni la fuente de verdad: `git status --porcelain` lista solo los tres documentos de `docs/campana-medicion/` y el directorio del change.
- [x] 5.2 Verificar que no quedan referencias erroneas: `grep -rn "100 casos cada uno\|opcional y deseable\|A2,analista_original\|director (Luca)" docs/campana-medicion/` sin coincidencias.
- [x] 5.3 Verificar las cinco cadenas canonicas sin tildes en la guia: `grep -n "Seguridad Informatica\|Soporte Tecnico Hardware\|Soporte Tecnico Software\|Bases de Datos\|Sistemas" docs/campana-medicion/guia-ejecucion-campana.md`.
- [x] 5.4 Ejecutar `openspec validate "c-171-corregir-la-deriva-de-la-guia-y-los-runbooks-de-la-campana" --strict --no-interactive` y confirmar PASS.
