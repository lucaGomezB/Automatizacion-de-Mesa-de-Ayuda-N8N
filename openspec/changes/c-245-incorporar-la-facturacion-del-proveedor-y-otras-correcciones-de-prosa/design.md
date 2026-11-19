# Design: Incorporar la facturación del proveedor en la prosa de la tesis y otras correcciones

## Context

Ver `proposal.md` — Why. Hechos del repositorio y restricciones que moldean el enfoque (verificados leyendo los archivos, 2026-11-19):

- **La afirmación a corregir.** `07-resultados.tex:380`, límite «Quinto»: «el gasto solo consta en la corrida ampliada y su procedencia es un cálculo a partir de tokens con el precio declarado de la tesis, no facturación del proveedor».
- **La nota de la tabla.** `07-resultados.tex:371` cierra con «Fuente: `evaluation/evidence/load_test_inferencia_ampliada_2026-11-18.json` y `evaluation/evidence/load_test_inferencia_2026-11-17.json`».
- **La evidencia de facturación existe y está versionada.** `evaluation/evidence/billing-gemini-2026-11-17-18-oficial.csv` (`sha256 7c75fc0128101f93c567060825d56c20f86f3fdc28aad5a1c183649f0d3324a4`) y `billing-gemini-2026-11-17-18-resumen.csv` (`sha256 5ffaf26b5c63d93e439488242397a3ee90cfc55ffd74d923047ad1151c4bf1cd`), ambos registrados en `evaluation/evidence/README.md`. Hashes recomputados y coincidentes.
- **Total del período.** 366.909 tokens (358.336 entrada + 8.573 salida), USD 0,300897 sin impuesto, hora del Pacífico (UTC-8), período 2026-11-17/18. Cota inferior: la exportación del 18/11 no estaba cerrada; el proveedor preveía ≈USD 0,04 más.
- **Contraste.** `usage_metadata` de la corrida ampliada: 281.568 tokens (274.920 + 6.648), USD 0,23112. +30 % en ambos tipos de token, misma proporción. Precio implícito exacto: 0,75 USD/millón de entrada y 3,75 de salida (escenario de la tesis).
- **El memo ya tiene la subsección (h).** `numeros-canonicos.md`, sección `3.47` (c-243), subsección `(h) Billing del proveedor (Cloud Billing)` ya escrita esta sesión. Los ítems `(e)(iv)` (L3208-3210) y `(f)(5)` (L3216) todavía dicen «no facturación del proveedor».
- **Contexto de release.** `v1.6.1` en curso: bump de versión aplicado, compilación limpia (155 páginas, 0 errores), bloqueada por dos compuertas (director `c-242` tarea 2.6; G3/G4 `c-243` tarea 7.1).
- **Requisitos en main.** `tesis-document` L1736 («Fuentes y cotas de costos operativos») y L8463 («Acreditacion del nivel pago de la Gemini API…») describen preocupaciones distintas. `tesis-numeros-canonicos` no tiene requisito de billing. Los deltas de c-245 son ADDED.

## Goals / Non-Goals

**Goals:**

- Distinguir en el cuerpo el costo por corrida (`tokens_calculado`) de la facturación del período (Cloud Billing), con el total como cota inferior, el contraste con `usage_metadata` y el precio confirmado.
- Agregar la evidencia de facturación como fuente en la nota de `tab:carga-inferencia`.
- Armonizar los ítems (e)(iv) y (f)(5) del memo hacia la subsección (h), sin tocar `(g)` ni valores canónicos.
- Dejar la tarea de re-exportación como tarea operativa, sin ejecutarla.

**Non-Goals:**

- Reescribir la subsección (h) del memo (ya escrita) más allá de la armonización de los dos ítems.
- Recompilar, regenerar derivados o tocar artefactos de release (solo si el change viaja en la release).
- Modificar `App/`, `n8n/`, `evaluation/` (más allá de lectura), `data/`, `scripts/` ni `.engram/`.
- Commit, tag o push.
- Cambiar alguna cifra canónica de capacidad o el veredicto de la sonda.

## Decisions

### D1 — Operación del delta: ADDED en ambas capacidades

Los requisitos vigentes que podrían solaparse (`Fuentes y cotas de costos operativos`, `Acreditacion del nivel pago…`) describen comportamientos que NO cambian. El requisito de la sonda con inferencia (c-243) no está aún en la spec principal, porque `c-243` sigue `in-progress`. Se elige **ADDED** y no MODIFIED para no arriesgar la pérdida de escenarios al archivar y porque la distinción por corrida/por período es una preocupación nueva. Es el mismo criterio que el delta de `c-244`.

**Alternativa descartada:** MODIFIED del requisito de la sonda de `c-243`. Se descarta porque ese requisito no está en la spec principal.

### D2 — Insertos exactos en `07-resultados.tex`

**Límite «Quinto» (`:380`).** El texto vigente «el gasto solo consta en la corrida ampliada y su procedencia es un cálculo a partir de tokens con el precio declarado de la tesis, no facturación del proveedor» pasa a distinguir los dos conceptos:

> Quinto, el gasto **por corrida** solo consta en la corrida ampliada y su procedencia es un cálculo a partir de tokens con el precio declarado de la tesis (`tokens_calculado`); la **facturación del período** de las dos corridas, que proviene del proveedor (Cloud Billing), es evidencia versionada aparte y se informa en la nota de la `\autoref{tab:carga-inferencia}`.

**Nota de `tab:carga-inferencia` (`:371`).** Se agrega, tras los dos JSON de las fuentes:

- la cita de las dos evidencias de facturación con sus prefijos de SHA-256 (`\texttt{evaluation/evidence/billing-gemini-2026-11-17-18-oficial.csv}`, `\texttt{sha256 7c75fc01\ldots}`; y `billing-gemini-2026-11-17-18-resumen.csv`, `5ffaf26b\ldots`);
- una oración que declare el total del período (`366.909` tokens, USD `0,300897`) como **cota inferior** (exportación del 18/11 abierta, ≈USD 0,04 más previstos), el contraste con `usage_metadata` (`281.568` tokens, USD `0,23112`; ≈`+30\,\%`, misma proporción, llamadas no contadas por `usage_metadata`) y que el precio implícito coincide con el escenario declarado de la tesis (por lo tanto NO es una diferencia de precio).

El detalle numérico vive en la **nota**; el límite «Quinto» conserva la distinción conceptual. Así la tabla, que ya rotula el gasto de la corrida, queda autocontenida.

### D3 — Armonización del memo (sección `3.47`)

- **`(e)(iv)`** (L3208-3210): el texto «El gasto solo consta en la corrida ampliada y su procedencia es `tokens_calculado` …, **no** facturación del proveedor» pasa a remitir a `(h)`: «El gasto **por corrida** solo consta en la corrida ampliada y su procedencia es `tokens_calculado`; la **facturación del período** del proveedor se registra en `(h)`».
- **`(f)(5)`** (L3216): «El gasto solo consta en la corrida ampliada, con procedencia `tokens_calculado`» pasa a remitir a `(h)` conservando que el costo por corrida es `tokens_calculado`.
- NO se toca `(g)` (tokens `281568`, costo `0,23112`) ni `(h)` (ya escrita) ni ningún otro ítem o sección.

### D4 — Barrido de coherencia (ítem (d))

Barrido de solo lectura por texto: `rg -n "no facturaci|facturación del proveedor|Cloud Billing|tokens_calculado|gasto_origen" "docs/Tesis/v10 (IA)/paper/sections" docs/Tesis/Correcciones/`. Objetivo: confirmar que ninguna afirmación dependa de la evidencia nueva sin reflejarla. Verificación puntual de la declaración de uso de IA (Anexo I.3, `12-anexos.tex:247`) y de `inventario-uso-asistentes-ia.md`, que ya están en «162 de 1221» para `v1.6.1` (referidos a commits, sin dependencia de la evidencia de billing). Si aparece una cifra stale, se reporta sin corregirla fuera del alcance del change.

### D5 — La re-exportación es operativa, no se ejecuta

La tarea `4.x` de `tasks.md` queda como tarea operativa pendiente: re-exportar el CSV de Cloud Billing el 2026-11-20, reemplazar el archivo, recomputar SHA-256 y actualizar `evaluation/evidence/README.md` y el memo `3.47`(h). La realiza el coautor con acceso a consola; no hay `gcloud` en este entorno. NO se ejecuta en el apply.

### D6 — Gobernanza MEDIUM, HIGH si viaja en la release

El cambio es de prosa (MEDIUM). Si el cambio viaja en la release `v1.6.1`, toca el ejemplar defendido y sube a HIGH: se requiere OK expreso de los autores antes de escribir cualquier `.tex`. No se commitea, taguea ni pushea sin OK.

## Risks / Trade-offs

- **Total del período citado como cerrado** → declararlo como cota inferior en prosa y memo; la re-exportación queda como tarea operativa.
- **+30 % leído como diferencia de precio** → declarar que el precio implícito cierra exacto en el escenario de la tesis.
- **Recompilación no ejecutada en este change** → si viaja en la release, la recompilación, los derivados y `compilacion.md` se ejecutan en la release, no aquí; se anotan como fuera de alcance.
- **Colisión con `c-243`/`c-244` en el memo** → se editan solo dos ítems de la `3.47`; el número de sección no cambia; no se renumera nada.

## Migration Plan

- **Rollback:** revertir los dos `.tex` y los dos archivos de `docs/Tesis/Correcciones/`; retirar la entrada de trazabilidad. La evidencia y la subsección (h) permanecen.
- **Orden de aplicación:** `07-resultados.tex` y memo no dependen de otros changes; si se aplica junto a la release, hacerlo tras las compuertas de `c-242` y `c-243`.

## Open Questions

Ninguna que bloquee el diseño. El único pendiente (re-exportación del CSV y el valor final del total del período) es una tarea operativa diferida que ya está contemplada: si el total cambia, se actualizan el número, el SHA-256 y las dos referencias (README y memo (h)) sin cambiar el enfoque, los specs ni la lista de tareas.
