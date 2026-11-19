# Tasks: Incorporar la facturación del proveedor en la prosa de la tesis y otras correcciones

Al final de cada tarea, entre paréntesis, el requisito que cumple. `TD` (`tesis-document`): «Distinción costo por corrida / facturación del período». `TNC` (`tesis-numeros-canonicos`): «Registro de la facturación del período y remisión de los ítems».

Solo prosa LaTeX y documentación: cero llamadas a proveedores, cero corridas nuevas. **Gobernanza MEDIUM**; sube a **HIGH** si el change viaja en la release `v1.6.1` (toca el ejemplar defendido) — en ese caso, OK expreso de los autores antes de escribir cualquier `.tex`. Ninguna tarea toca `App/`, `n8n/`, `evaluation/` (más allá de lectura), `data/`, `scripts/` ni `.engram/`. Nada se commitea, taguea ni pushea sin OK expreso. La recompilación, los derivados y `compilacion.md` quedan fuera del alcance (tramo de release).

## 0. Precondiciones, línea base y evidencia

- [x] 0.1 Leer `proposal.md`, `design.md` (D1 a D6) y los dos specs delta; releer el límite «Quinto» (`07-resultados.tex:380`), la nota de `tab:carga-inferencia` (`:371`) y los ítems `(e)(iv)` y `(f)(5)` de la sección `3.47` del memo. Verificación: los tres pasajes transcriptos y la subsección `(h)` localizada. (TD, TNC)
- [x] 0.2 **Línea base:** `git status`, `git rev-parse HEAD`, `git describe --tags` y modificaciones preexistentes ajenas (no tocarlas). Verificación: HEAD, tag y modificaciones ajenas registrados como no intervenidas.
- [x] 0.3 **Verificar la evidencia de facturación:** `sha256sum evaluation/evidence/billing-gemini-2026-11-17-18-oficial.csv evaluation/evidence/billing-gemini-2026-11-17-18-resumen.csv` debe dar `7c75fc01…` y `5ffaf26b…`. Verificación: los dos hashes coinciden con los del `proposal.md`. (TD, TNC)
- [x] 0.4 **Red de seguridad:** `cd "docs/Tesis/v10 (IA)" && python verify_citations.py` (debe reportar `STATUS: PASS`); si falla, reportarlo como falla preexistente y no corregirlo aquí. Verificación: baseline registrado con su estado. Si el change viaja en la release, registrar además que la recompilación queda fuera de alcance.

## 1. Núcleo (billing) en la prosa de resultados

- [x] 1.1 En `07-resultados.tex:380` (límite «Quinto»), reemplazar «el gasto solo consta en la corrida ampliada y su procedencia es un cálculo a partir de tokens con el precio declarado de la tesis, no facturación del proveedor» por el texto de D2, que distingue el gasto **por corrida** (`tokens_calculado`) de la **facturación del período** (Cloud Billing) con remisión a la nota de `tab:carga-inferencia`. Verificación: `rg -n "no facturación del proveedor" "docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex"` sin coincidencias y el nuevo texto nombra ambos conceptos. (TD)
- [x] 1.2 En la nota de `tab:carga-inferencia` (`07-resultados.tex:371`), agregar la cita de las dos evidencias de facturación con sus prefijos de SHA-256 (`billing-gemini-2026-11-17-18-oficial.csv`, `7c75fc01…`; `billing-gemini-2026-11-17-18-resumen.csv`, `5ffaf26b…`), junto a los dos JSON existentes. Verificación: la nota cita los cuatro archivos y los dos prefijos. (TD)
- [x] 1.3 En la misma nota, agregar la oración que declara el total del período (`366.909` tokens, USD `0,300897`) como **cota inferior** (exportación del 18/11 abierta, ≈USD 0,04 más), el contraste con `usage_metadata` (`281.568` tokens, USD `0,23112`; ≈`+30\,\%`, misma proporción, llamadas no contadas) y que el **precio queda confirmado** (no es diferencia de precio). Verificación: la oración contiene el total, la salvedad de cota inferior, el contraste y la confirmación del precio. (TD)
- [x] 1.4 Verificar que ninguna oración nueva supera las 60 palabras (regla de legibilidad de `tesis-document`). Verificación: conteo de palabras de las oraciones agregadas por debajo de 60. (TD)

## 2. Armonización del memo de números canónicos

- [x] 2.1 Ajustar el ítem `(e)(iv)` de la sección `3.47` para que remita a la subsección `(h) Billing del proveedor (Cloud Billing)`, conservando que el costo por corrida es `tokens_calculado` (texto de D3). Verificación: el ítem nombra `(h)` y no afirma de forma aislada «no facturación del proveedor». (TNC)
- [x] 2.2 Ajustar el límite `(f)(5)` para remitir a `(h)`, conservando la procedencia `tokens_calculado` del costo por corrida. Verificación: el ítem remite a `(h)` y no queda la afirmación aislada. (TNC)
- [x] 2.3 Verificar que NO cambian el ítem `(g)` (tokens `281568`, costo `0,23112`), la subsección `(h)`, ni ningún otro valor o estado previo; que la numeración de la Sección 3 sigue consecutiva y sin duplicados. Verificación: `git diff` del memo se limita a los ítems `(e)(iv)` y `(f)(5)` y `rg -n "^### 3\." docs/Tesis/Correcciones/numeros-canonicos.md` sin duplicados. (TNC)

## 3. Barrido y verificación de coherencia

- [x] 3.1 Barrido de solo lectura: `rg -n "no facturaci|facturación del proveedor|Cloud Billing|tokens_calculado|gasto_origen" "docs/Tesis/v10 (IA)/paper/sections" docs/Tesis/Correcciones/`. Verificación: cada coincidencia refleja la distinción por corrida/por período; ninguna afirmación depende de la evidencia nueva sin reflejarla. (TD)
- [x] 3.2 Verificar la declaración de uso de IA (Anexo I.3, `12-anexos.tex:247`) y `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md`: deben conservar «162 de 1221» para `v1.6.1`, sin cifras stale. Verificación: ambos ficheros muestran «162 de 1221» y ninguna referencia a la facturación del proveedor. (TD)
- [x] 3.3 Registrar el resultado del barrido (hallazgos o su ausencia) en la sección de trazabilidad del change. Verificación: la entrada de `dictamen-correcciones.md` consigna el comando del barrido y su salida. (TD)

## 4. Tarea operativa diferida (NO ejecutar en el apply)

- [ ] 4.1 **[COMPUERTA operativa — pendiente]** Re-exportar el CSV de Cloud Billing el 2026-11-20 (la exportación del 18/11 estaba abierta; el total puede crecer ≈USD 0,04). La realiza el coautor con acceso a consola; no hay `gcloud` en este entorno. Verificación: **no se ejecuta aquí**; queda declarada como tarea operativa con su fecha y responsable. (TD, TNC)
- [ ] 4.2 Al recibir el CSV re-exportado: reemplazar `evaluation/evidence/billing-gemini-2026-11-17-18-oficial.csv`, recomputar su SHA-256 y actualizar `evaluation/evidence/README.md` y el memo `3.47`(h) con el total (o la cota) final. Verificación: el SHA-256 del README coincide con `sha256sum` del archivo y el total del memo coincide con el del CSV. (TD, TNC)

## 5. Trazabilidad

- [x] 5.1 Agregar en `docs/Tesis/Correcciones/dictamen-correcciones.md` la sección del change con: change, fecha, motivo (incorporar la facturación del proveedor del período y armonizar la prosa), archivos afectados (`07-resultados.tex`, `numeros-canonicos.md`, `evaluation/evidence/README.md` como fuente), lo que NO cambia (cifras canónicas, veredicto de la sonda, capacidad), verificación y gobernanza (MEDIUM; HIGH si viaja en la release). Verificación: la sección existe y nombra los campos. (TD, TNC)
- [x] 5.2 Verificar que el cuerpo no cita el memo por número de sección al referirse a la facturación. Verificación: `rg -n "Sección[~ ]3\.[0-9]{2}" "docs/Tesis/v10 (IA)/paper/sections"` sin coincidencias nuevas. (TD)
- [x] 5.3 Confirmar que NO se tocó ningún artefacto de release (`main.pdf`, `compilacion.md`, derivados) ni `App/`, `n8n/`, `evaluation/` (más allá de lectura). Verificación: `git status --porcelain` lista solo `07-resultados.tex`, `numeros-canonicos.md` y `dictamen-correcciones.md`. (TD, TNC)
- [x] 5.4 Ejecutar `openspec validate "c-245-incorporar-la-facturacion-del-proveedor-y-otras-correcciones-de-prosa" --strict`. Verificación: sin errores ni advertencias. (TD, TNC)
