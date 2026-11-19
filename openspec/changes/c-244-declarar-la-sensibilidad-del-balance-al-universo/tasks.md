# Tasks: Declarar la sensibilidad del balance al universo

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` = `docs/Tesis/Correcciones/`.
Equivalente de Strict TDD para prosa: cada tarea de edición tiene una verificación que se corre
ANTES (línea base; debe mostrar la ausencia de la declaración) y DESPUÉS (estado deseado), y
ambas salidas se reportan en `C/dictamen-correcciones.md` (sección `c-244`). Reglas: no
commitear ni pushear sin pedido; no cambiar cifras canónicas (en particular `+18,7`); español
sin emojis; solo alias (`E1`, `E2`, `O1`, `O2`), nunca nombres reales; no tocar `App/`, `n8n/`,
`evaluation/` ni `CHANGES.md`. Orden duro: aplicar DESPUÉS de `c-242` (mismo archivo).

## 1. Guardas y lectura

- [x] 1.1 Leer `proposal.md`, `design.md` (D1-D5 + OQ-01), los deltas `specs/tesis-document/spec.md` y `specs/tesis-numeros-canonicos/spec.md`, y el estado actual de `S/08-discusion.tex`. Verificación (línea base): `rg -n "independiente de|2\.646|18,7" "S/08-discusion.tex"` muestra que NO existe ninguna declaración de sensibilidad a `N`.
- [x] 1.2 Confirmar que `c-242` está aplicado sobre `S/08-discusion.tex` (la oración se inserta sobre su texto) y que `subsec:balance-neto` conserva `N = 2.646` como premisa. Verificación: `git log`/`git diff` o `rg -n "subsec:balance-neto|2\.646" "S/08-discusion.tex"`; si `c-242` no está aplicado, detener y reportar.
- [x] 1.3 Confirmar la lectura del memo: última sección de la Sección 3 y primer número libre al aplicar. Verificación: `rg -n "^### 3\." C/numeros-canonicos.md` (hoy `3.46` es la última; `c-242`/`c-243` pueden ocupar números intermedios).
- [x] 1.4 Reproducir (o citar) el corchete `25,4688` s y los tres valores derivados. Verificación: `python3 evaluation/data/campana/analisis/analisis_balance_neto_c236.py` reproduce los anclajes; el cálculo `(N/3.600) × 25,4688` da `+7,07`, `+35,37` y `+70,75` para `N = 1.000`, `5.000` y `10.000`.

## 2. tesis-document — oración de sensibilidad en `subsec:balance-neto`

- [x] 2.1 `S/08-discusion.tex`: insertar el párrafo nuevo (D2/D3) entre el primer párrafo de `subsec:balance-neto` (hoy L80, termina en «...`independiente de \(N\)`.») y `\begin{table}` (hoy L82). Verificación (ANTES): no existe la oración; (DESPUÉS): `rg -n "escala de forma lineal con|no dependen de \(N\)" "S/08-discusion.tex"` devuelve la oración.
- [x] 2.2 Verificar que la oración es una sola, que cita `+7,1`, `+35,4` y `+70,7` (una decimal) para `N = 1.000`, `5.000` y `10.000`, que los tres valores figuran en la oración del cuerpo (no solo en un anexo) y que rotula `N` como premisa del escenario narrativo. Verificación: lectura del párrafo; la oración es única y `< 60` palabras.
- [x] 2.3 Verificar que `a*_r` y `c*` figuran como independientes de `N` y que no se introduce ninguna tabla en el cuerpo. Verificación: `rg -n "no dependen de \(N\)" "S/08-discusion.tex"`; `git diff` no agrega `\begin{table}` en `subsec:balance-neto`.
- [x] 2.4 Verificar que ningún número canónico cambia. Verificación: `git diff` de `S/08-discusion.tex` no altera `+18,7`, `43,82`, `0,735`, `69,51`, `898,8` ni `43,1`; cotejo multiconjunto de cifras antes/después (`foto-cifras`) si se dispone.

## 3. tesis-numeros-canonicos — sección aditiva del memo

- [x] 3.1 `C/numeros-canonicos.md`: agregar una sección aditiva con el primer número libre de la Sección 3 (D4), sin renumerar ni alterar las anteriores. Verificación: `rg -n "^### 3\." C/numeros-canonicos.md` muestra numeración consecutiva y sin duplicados.
- [x] 3.2 Registrar los tres valores de referencia (`N = 1.000 → +7,1`; `5.000 → +35,4`; `10.000 → +70,7`) con procedencia (corchete `25,4688` s; generador `analisis_balance_neto_c236.py`), comando de recálculo y estado `condicional`. Verificación: la sección contiene las tres filas con estado y procedencia; ninguna se rotula `vigente` ni canónica.
- [x] 3.3 Declarar en la cabecera que `B_r` escala linealmente con `N`, que `a*_r` y `c*` no dependen de `N` y que `N` es una premisa del escenario narrativo. Verificación: `rg -n "lineal|premisa|no dependen de" C/numeros-canonicos.md` devuelve la sección nueva.
- [x] 3.4 Verificar que ningún valor ni estado previo cambia. Verificación: el `diff` del memo se limita a la sección nueva y a su entrada de encabezado/upsert; `+18,7` y su estado quedan intactos.

## 4. Verificación y cierre (recompilación y release — NO ejecutar en el propose)

- [x] 4.1 Registrar la entrada de `c-244` en `C/dictamen-correcciones.md` (tabla de trazabilidad del follow-up OQ-05 de `c-242`), con las salidas ANTES/DESPUÉS de `rg`. Verificación: la fila existe y remite a `subsec:balance-neto` y a la sección nueva del memo.
- [x] 4.2 Validar el change. Verificación: `openspec validate c-244-declarar-la-sensibilidad-del-balance-al-universo --strict` pasa.
- [x] 4.3 (Release) Recompilar `paper/main.pdf` con `latexmk -xelatex`, sin errores fatales, referencias ni citas indefinidas. Verificación: `P/compilacion.md` regenerado con el SHA-256 del PDF; 0 etiquetas duplicadas. **Ejecutado (2026-11-19, tramo no destructivo de la release `v1.6.1`):** 155 páginas, 0 errores fatales, 0 referencias/citas indefinidas, 0 etiquetas duplicadas; `compilacion.md` con SHA-256 `a83b5478...`.
- [x] 4.4 (Release) Regenerar derivados: `tesis_para_agente.md` con `build_tesis_para_agente.py`, extractos y `compilacion.md`. Verificación: los derivados citan la oración de sensibilidad y no quedan vacíos. **Ejecutado (2026-11-19):** `tesis_para_evaluacion.txt`, `tesis_completa_extraida.txt` y `tesis_para_agente.md` (`v1.6.1`) regenerados; «escala de forma lineal con» figura en el extracto; copia de entrega `docs/Tesis/tesis_ultima_version.pdf` byte a byte igual a `main.pdf` (SHA-256 `a83b5478...`).
- [ ] 4.5 (Release) Actualizar el hash y la versión en el Anexo B (`12-anexos.tex`, `sec:anexo-repositorio`) y la portada, y crear el tag anotado. Verificación: el Anexo B consigna el hash del commit de la release y el tag existe. Coordinar con `c-243` si comparten la release `v1.6.1` o si va en su propia release de parche (OQ-01). **Parcial (2026-11-19):** el bump de versión a `v1.6.1` de la portada y del Anexo B (`:58`, `:62`) ya está aplicado; el hash del Anexo B y el tag anotado quedan PENDIENTES, bloqueados por la compuerta del director (`c-242` 2.6) y la autorización G3/G4 (`c-243` 7.1).
