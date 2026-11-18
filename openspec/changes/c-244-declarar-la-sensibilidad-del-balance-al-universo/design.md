# Design: Declarar la sensibilidad del balance al universo

## Context

Ver `proposal.md` — Why. Estado y restricciones que moldean el enfoque (verificado leyendo los archivos):

- **Follow-up pendiente.** La tabla de compuertas de `c-242` en `docs/Tesis/Correcciones/dictamen-correcciones.md` (fila OQ-05, L6632) registra «C ahora (balance condicional a N asumido); B (recta `B_r(N)`) como follow-up». El follow-up no se implementó.
- **Texto aplicado por c-242.** `08-discusion.tex`, `subsec:balance-neto` (L78-L124): el primer párrafo (L80) fija `N = 2.646` como «incidentes por trimestre» y define `B_r = (N/3.600)[Δt − ρr − (e_aut − e_man)c]` y `a*_r = 1 − e_man − (Δt − ρr)/c`, «independiente de `N`». La tabla `tab:balance-neto` (L82-L108) repite `+18,7`. `09-conclusiones.tex` (L6) y la síntesis (L118) citan «a lo sumo `+18,7` horas-persona por trimestre». Ningún pasaje declara la dependencia con `N`.
- **Fuente de los valores.** `evaluation/data/campana/analisis/analisis_balance_neto_c236.py` (y su `.json`/`.md`); los insumos `N`, `Δt`, `e_aut`, `e_man` en `analisis_balance_neto_c222.json` (`insumos.n`). El corchete `Δt − ρr − (e_aut − e_man)c` es constante: `43,82 − 0,735 × 22,0632 − 0,0307131 × 69,5074 = 25,4688` s. Por eso `B_r(N) = (N/3.600) × 25,4688` es una recta por el origen.
- **Valores derivados verificados.** `N = 1.000 → +7,07`; `N = 2.646 → +18,72`; `N = 5.000 → +35,37`; `N = 10.000 → +70,75` horas-persona por trimestre (una decimal: `+7,1`, `+18,7`, `+35,4`, `+70,7`). `a*_r = 43,1 %` y `c* = 898,8` s no contienen `N`.
- **Requisitos en main.** `openspec/specs/tesis-document/spec.md` (L735, «Aritmetica metodologica verificable») y `openspec/specs/tesis-numeros-canonicos/spec.md` (L1146, sección de c-236). Los deltas de c-244 son ADDED (preocupación nueva) y no tocan esos requisitos.
- **Numeración del memo.** La última sección es `3.46` (c-236); `c-242`/`c-243` pueden tomar números antes. El número de la sección nueva es el primer libre al aplicar.

## Goals / Non-Goals

**Goals:**

- Que el cuerpo declare en una sola oración que `B_r` escala linealmente con `N`, que `a*_r` y `c*` no dependen de `N` y que `N` es una premisa, con tres valores de referencia rotulados como derivados.
- Que el memo registre esos tres valores como derivados/`condicional`, sin tocar ninguna cifra canónica.
- Cerrar el follow-up OQ-05 con el mínimo cambio de superficie (una oración + una sección aditiva).

**Non-Goals:**

- Recomputar el balance central ni cambiar `+18,7`.
- Reemplazar `N = 2.646` por otro valor (la premisa ratificada se conserva).
- Agregar una tabla en el cuerpo (si se usa tabla, va en un anexo).
- Reencuadrar el origen/la validez externa (eso es `c-242`), tocar `evaluation/`, `App/`, `n8n/` o `CHANGES.md`.

## Decisions

### D1 — Operación del delta: ADDED en ambas capacidades

Los requisitos vigentes (`Aritmetica metodologica verificable` en `tesis-document`; `Registro aditivo del balance neto acotado con el termino de revision` en `tesis-numeros-canonicos`) describen comportamientos que NO cambian. Se elige ADDED y no MODIFIED para no arriesgar la pérdida de escenarios al archivar y porque la sensibilidad con `N` es una preocupación nueva.

Alternativa descartada: MODIFIED del requisito de c-236 en `tesis-numeros-canonicos` para colgar los tres valores de esa misma sección. Se descarta porque el patrón del memo es una sección aditiva por change y el requisito de c-236 manda `MUST NOT cambiar` sus cifras/estado; una sección propia con el primer número libre es más seguro y consistente.

### D2 — Punto de inserción exacto en `08-discusion.tex`

Párrafo nuevo entre el primer párrafo de `subsec:balance-neto` (L80, que termina en «...`independiente de \(N\)`.») y `\begin{table}` (L82). Es el lugar donde ya se enuncia `N = 2.646` y la fórmula, de modo que la sensibilidad se lee pegada al supuesto que la origina. Los tres valores de referencia van en la oración del cuerpo; una tabla en un anexo es opcional y no la sustituye (no se admite la variante de nota al pie como forma exclusiva).

### D3 — Redacción de la oración

Una sola oración, en estilo de la tesis (matemáticas LaTeX, decimales con coma, sin emojis):

> El balance \(B_r\) escala de forma lineal con \(N\) ---a modo de referencia, con \(N = 1.000\), \(5.000\) y \(10.000\) la cota superior condicional sería de \(+7{,}1\), \(+35{,}4\) y \(+70{,}7\) horas-persona por trimestre---, mientras que \(a^{*}_r\) y \(c^{*}\) no dependen de \(N\) y \(N\) permanece como premisa del escenario narrativo, no como un universo medido (\autoref{sec:anexo-numeros-canonicos}).

La oración es la forma exigida: los tres valores de referencia van en el cuerpo. No se admite la variante de nota al pie como sustituto, y una tabla en un anexo (si se usa) es opcional y nunca la reemplaza. La oración queda por debajo de 60 palabras (regla de legibilidad de `tesis-document`).

### D4 — Contenido y forma del memo

Sección aditiva con el primer número libre; tres filas (`N = 1.000 → +7,1`; `5.000 → +35,4`; `10.000 → +70,7`), cada una con procedencia (corchete `25,4688` s; generador `analisis_balance_neto_c236.py`), comando de recálculo y estado `condicional`; una cabecera que declara la linealidad, la independencia de `a*_r`/`c*` y `N` como premisa. No se reescribe la sección `3.46`.

### D5 — Números y redondeo

Una decimal, como la lectura central (`+18,7`). Los tres valores provienen de multiplicar `25,4688` por `N/3.600`; no hay remuestreo ni dato nuevo. No se presentan intervalos para estos valores: son producto de un corchete fijo por un `N` asumido, no estimaciones.

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| Leer los tres valores como mediciones | Rotularlos como derivados/`condicional` y declarar `N` como premisa en el cuerpo y en el memo |
| Conflicto con `c-242` o `c-243` sobre `08-discusion.tex` | Aplicar después de `c-242`; si `c-243` toca el mismo archivo, coordinar el release |
| Desalineación cuerpo-memo | El requisito de `tesis-numeros-canonicos` liga cada valor citado a una fila del memo |
| Pérdida de detalle al archivar | Se usa ADDED (D1): no hay requisito previo que reproducir |
| Superar las 60 palabras | D3 fija una única oración de ~55 palabras |

## Migration Plan

1. **Guardas:** confirmar que `c-242` está aplicado sobre `08-discusion.tex` (la oración se inserta sobre su texto) y que `c-244` valida `--strict`.
2. **`tesis-document` (prosa):** insertar la oración en `subsec:balance-neto` (D2/D3); verificar con `rg` que `N` queda como premisa, que `a*_r`/`c*` figuran independientes de `N` y que `+18,7` no cambia.
3. **`tesis-numeros-canonicos` (memo):** agregar la sección aditiva (D4); verificar numeración consecutiva y cifras/estados previos intactos.
4. **Registro y cierre (nota, NO ejecutado en el propose):** entrada de `c-244` en `dictamen-correcciones.md`; recompilación; regeneración de derivados (`tesis_para_agente.md`, `compilacion.md`, extractos); hash de la release y tag. Se ejecutan en el apply/release, no ahora.

Rollback: `git revert` del commit que toca `08-discusion.tex` y del que agrega la sección del memo; ambos aditivos y reversibles por separado.

## Open Questions

- **OQ-01 (autores):** ¿la oración viaja en la misma release `v1.6.1` que `c-243` (TASK B) o en su propia release de parche? No cambia specs, enfoque ni tareas; solo el punto de inserción del release. No se fija una versión más allá de `v1.6.1`.
