# Proposal: Incorporar la facturación del proveedor en la prosa de la tesis y otras correcciones

## Why

La prosa declara, en el límite «Quinto» de la sonda de latencia, que el gasto «es un cálculo a partir de tokens con el precio declarado de la tesis, no facturación del proveedor» (`docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex:380`). Esa afirmación dejó de ser exacta: la facturación real del proveedor (Google Cloud Billing) del período de las dos corridas está versionada como evidencia en `evaluation/evidence/`. Además, varias correcciones de prosa menores por evidencia nueva conviene agruparlas en un solo change en vez de parches dispersos.

## What Changes

- **Núcleo (billing).** En `07-resultados.tex:380` (límite «Quinto») y en la nota de `tab:carga-inferencia` (`07-resultados.tex:371`), distinguir explícitamente el costo **por corrida** (calculado desde tokens; `gasto_origen = tokens_calculado`) de la facturación **del período** del proveedor (Cloud Billing). Declarar:
  - el total del período (366.909 tokens / USD 0,300897), declarado como **cota inferior** porque la exportación del 18/11 no estaba cerrada y el proveedor preveía ≈USD 0,04 más;
  - el contraste con `usage_metadata` (281.568 tokens / USD 0,23112: +30 % en ambos tipos de token, misma proporción, atribuible a llamadas que `usage_metadata` no contó — reintentos técnicos, pruebas previas, llamadas fuera de las dos corridas);
  - que el **precio queda confirmado** (el implícito es exactamente 0,75 USD por millón de entrada y 3,75 por millón de salida, el escenario de la tesis): NO es una diferencia de precio.
- **Otras correcciones.**
  - `docs/Tesis/Correcciones/numeros-canonicos.md`, sección `3.47`: armonizar sus ítems (e)(iv) y (f)(5), que todavía dicen «no facturación del proveedor», remitiéndolos a la subsección ya escrita `(h) Billing del proveedor (Cloud Billing)`, conservando la distinción: por corrida es `tokens_calculado`; el período tiene Cloud Billing.
  - Agregar la evidencia de facturación (`evaluation/evidence/billing-gemini-2026-11-17-18-oficial.csv`, `sha256 7c75fc01…`; `billing-gemini-2026-11-17-18-resumen.csv`, `sha256 5ffaf26b…`) como fuente en la nota de `tab:carga-inferencia`, junto a los dos JSON.
  - **Barrido de verificación:** confirmar que ninguna otra afirmación de la tesis dependa de esta evidencia nueva sin reflejarla; en particular verificar la declaración de uso de IA (Anexo I.3, `12-anexos.tex:247`) y `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` (ya en «162 de 1221» para `v1.6.1`).
- **Tarea operativa (no ejecutada ahora).** Re-exportar el CSV de Cloud Billing el 2026-11-20 (la exportación del 18/11 estaba abierta; el total puede crecer ≈USD 0,04). La realiza el coautor con acceso a consola; no hay `gcloud` en este entorno. Al llegar: reemplazar el CSV, recomputar SHA-256 y actualizar `evaluation/evidence/README.md` y el memo `3.47`(h).

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tesis-document`: **ADDED** «Distinción entre el costo por corrida y la facturación del proveedor del período» (prosa del límite «Quinto» y de la nota de `tab:carga-inferencia`, más el barrido de coherencia).
- `tesis-numeros-canonicos`: **ADDED** «Registro de la facturación del proveedor (Cloud Billing) del período y remisión de los ítems de la sonda» (armonización de (e)(iv) y (f)(5) hacia (h)).

## Impact

| Área | Impacto | Descripción |
|---|---|---|
| `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` | Modificado | Límite «Quinto» (`:380`) y nota de `tab:carga-inferencia` (`:371`) |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Modificado | Ítems (e)(iv) y (f)(5) de la sección `3.47` remiten a (h) |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Entrada de trazabilidad del change |
| Release (posterior) | Modificado | Recompilación, derivados y `compilacion.md`; solo si viaja en la release |

## Governance and Approval

- **Gobernanza MEDIUM** (prosa). **Sube a HIGH si viaja en la release**, porque toca el ejemplar defendido: requiere OK expreso de los autores antes de escribir cualquier `.tex` en ese caso.
- **Restricciones:** NO commit, NO tag, NO push. No tocar `App/`, `n8n/`, `evaluation/` (más allá de lectura) ni los artefactos de release.
- **Dependencias:** `c-243` (sonda de latencia) y `c-244` (sensibilidad del balance). La sección `3.47` y su subsección (h) ya fueron escritas en la sesión; el registro de evidencia en `evaluation/evidence/README.md` también.

## Risks

| Riesgo | Prob. | Mitigación |
|---|---|---|
| Leer el total del período como costo por corrida | Alta | Declarar la distinción por corrida (`tokens_calculado`) vs período (Cloud Billing) en ambos loci |
| Presentar el +30 % como diferencia de precio | Media | Declarar que el precio implícito cierra exacto en el escenario de la tesis |
| Citar el total del período como cifra cerrada | Media | Declararlo como cota inferior, con el pendiente de re-exportación |
| Fragmentos «no facturación del proveedor» sobrevivientes | Media | Barrido por texto en `.tex` y en el memo |

## Rollback Plan

Revertir los dos `.tex` y los dos archivos de `docs/Tesis/Correcciones/` a su estado previo. La evidencia en `evaluation/evidence/` y la subsección (h) del memo se conservan: el rollback retira la integración editorial, no la evidencia.

## Success Criteria

- [ ] El límite «Quinto» y la nota de `tab:carga-inferencia` distinguen costo por corrida de facturación del período.
- [ ] La nota cita las dos evidencias de billing con sus prefijos SHA-256, junto a los dos JSON.
- [ ] Los ítems (e)(iv) y (f)(5) del memo remiten a (h) sin cambiar `(g)` ni ningún valor canónico.
- [ ] El barrido confirma que ninguna otra afirmación depende de la evidencia nueva sin reflejarla.
- [ ] `openspec validate … --strict` cierra sin errores.
