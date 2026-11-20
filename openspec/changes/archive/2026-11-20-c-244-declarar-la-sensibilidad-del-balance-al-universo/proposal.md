## Why

Los autores ratificaron OQ-05 de `c-242` como «C ahora» (mantener el balance neto condicional al `N` asumido) con «B (la recta `B_r(N)`) como follow-up». Ese follow-up nunca se implementó: el texto aplicado por `c-242` conserva `N = 2.646` como premisa/proyección del escenario narrativo y no declara cómo se mueve el balance al cambiar el universo. Un lector puede leer `N = 2.646` y el `+18,7` horas-persona como una medición cuando son una premisa. Este cambio cierra esa brecha con una única oración de sensibilidad.

## What Changes

- **Una oración** en `08-discusion.tex` (`subsec:balance-neto`), como párrafo nuevo inmediatamente después del primer párrafo que fija `N = 2.646` y define `B_r` y `a*_r` (hoy la línea 80), antes de `\begin{table}`. Declara que `B_r` escala linealmente con `N`, que `a*_r` y `c*` NO dependen de `N`, y cita los tres valores de referencia (`+7,1`, `+35,4` y `+70,7` horas-persona por trimestre para `N = 1.000`, `5.000` y `10.000`) con `N` rotulado como premisa del escenario narrativo, no como universo medido. Los tres valores de referencia van en la oración del cuerpo; una tabla en un anexo es opcional y en ningún caso la sustituye.
- **Sin tabla en el cuerpo.** Una tabla en un anexo es opcional y nunca sustituye a la oración del cuerpo.
- **Ningún número canónico cambia**; la cifra `+18,7` horas-persona se conserva.
- **Delta `tesis-document`**: requisito nuevo (ADDED) — el balance declara su dependencia lineal con `N` y las cantidades independientes de `N`, sin presentar `N` como medido.
- **Delta `tesis-numeros-canonicos`**: requisito nuevo (ADDED) — el memo registra los tres valores de referencia como derivados/`condicional` en una sección aditiva, nunca como canónicos.

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `tesis-document`: se agrega el requisito de declarar la sensibilidad del balance al universo asumido.
- `tesis-numeros-canonicos`: se agrega el requisito de registrar los valores de `N` de referencia como derivados/condicionales.

## Impact

| Archivo | Cambio |
|---|---|
| `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` | Oración nueva en `subsec:balance-neto` (una oración, sin tabla) |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Sección aditiva con los tres valores derivados/`condicional` |
| `openspec/specs/tesis-document/spec.md`, `openspec/specs/tesis-numeros-canonicos/spec.md` | Deltas del change (se archivan al cerrar) |

Sin cambios en `App/`, `n8n/`, `evaluation/`, `data/`, `Bibliography_base.bib`, cifras canónicas ni `CHANGES.md`. Sin llamadas pagas.

## Approach

La ecuación `B_r = (N/3.600)[Δt − ρr − (e_aut − e_man)c]` tiene un corchete constante de `25,4688` s; los tres valores de referencia salen de multiplicar ese corchete por `N/3.600` (aritmética derivada, sin datos nuevos). `a*_r = 43,1 %` y `c* = 898,8` s no contienen `N`.

## Risks

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| Leer los tres valores como mediciones | Media | Rotularlos como derivados y `condicional`; declarar `N` como premisa |
| Desalinear el memo con el cuerpo | Baja | El requisito de `tesis-numeros-canonicos` liga cada valor citado a una fila del memo |
| Conflicto con `c-242`/`c-243` sobre `08-discusion.tex` | Media | Aplicar después de `c-242`; puede compartir la release `v1.6.1` con `c-243` o ir en su propia release de parche |

## Dependencies

- Después de `c-242` (mismo archivo `08-discusion.tex`). Puede compartir la release `v1.6.1` con `c-243` o ir en su propia release de parche. Gobernanza MEDIUM: aritmética derivada, sin datos nuevos, sin llamadas pagas.

## Rollback Plan

`git revert` del commit que toca `08-discusion.tex` y de la sección aditiva del memo. Ambos son aditivos y reversibles por separado; ninguna cifra ni estado previo del memo se modifica.

## Success Criteria

- [ ] La oración de sensibilidad está en `subsec:balance-neto`, es una sola oración y cita los tres valores de referencia (`+7,1`, `+35,4`, `+70,7`) en el cuerpo, sin tabla en el cuerpo.
- [ ] `+18,7` y todos los números canónicos quedan idénticos.
- [ ] `rg` confirma `N` rotulado como premisa y `a*_r`/`c*` declarados independientes de `N`.
- [ ] Los tres valores de referencia figuran en el memo como derivados/`condicional`.
- [ ] `openspec validate c-244-... --strict` pasa.
