## Context

Ver `proposal.md` — Why. Estado actual que condiciona el diseño:

- `08-discusion.tex:84` usa `c` = `10 a 15 min` (estimación propia, memo `3.11`) y computa
  `B = (N/3.600)[Δt − (e_aut − e_man)·c]` con `e_aut = 53/200` (etiquetado original) y
  `e_man = 15 %` (supuesto). `:111` recalculó con la referencia común de la `3.21` pero todavía
  sobre la rejilla `5/10/15 min`, y declara el balance `condicional` al costo porque `c` no se
  cronometró. `tab:balance-neto` y la prosa de `:107`, `:111` y `:117` arrastran esa lectura.
- c-220 fijó `c` compuesto medido `69,51 s`, IC 95 % `[33,42; 106,56] s` (memo `3.31`; IC por
  **suma de extremos** de los intervalos bootstrap de cada tramo). Su compuerta D5 quedó en rama B
  y el dueño eligió la opción (i): recalcular `B` en este change.
- La referencia común de la `3.21` (c-207) da `e_aut = 28/138 = 0,2029`, `e_man = 26/151 = 0,1722`,
  `e_aut − e_man = +0,0307`, IC `[−0,0460; +0,1070]`, `N = 2.646`, `Δt = 43,82 s`, y las celdas
  `+25,4 / +18,7 / +11,9` para `c = 5/10/15 min` con IC bootstrap por caso
  `[+8,6; +42,4]`, `[−15,0; +52,5]`, `[−38,6; +62,7]`. El artefacto `analisis_dictamen_c207.json`
  conserva los intervalos, no la distribución bootstrap por caso.
- c-221 (memo `3.32`) aportó la sensibilidad mixta `+28,2 / +25,1`, rotulada como sensibilidad que
  mezcla corpus y referencias y que no reemplaza el balance con referencia común.
- Disciplina del memo: secciones **aditivas**, numeración = primer número libre, estado por valor
  en `{vigente, condicional, retirado}`, procedencia `archivo:línea` o comando reproducible.
- Los análisis de campaña son scripts de solo lectura, biblioteca estándar, semilla
  `20261021`, `B = 2000`, salidas idénticas byte a byte (`analisis_costo_derivacion_c220.py`,
  `analisis_propagacion_arbitraje_c221.py`), con anclajes que **abortan antes de escribir**.

Valores esperados que el script deberá reproducir (no canónicos hasta que el memo los registre):
`B` central `≈ +30,6 h-persona/trimestre`; `a* ≈ 19,7 %`.

## Goals / Non-Goals

**Goals:**

- Convertir el `c` medido en el insumo central del balance canónico, con `B` y `a*` recalculados y
  su incertidumbre declarada, sin mover el umbral del 85 %.
- Que la misma lectura del balance aparezca en `00`, `08`, `09` y `12`, y que la grilla previa
  quede como sensibilidad superada con sus cifras conservadas.
- Producir el recomputo con un único script offline, determinista y anclado, y registrarlo antes
  de tocar la prosa.

**Non-Goals:**

- Medir de nuevo `c`, `e_aut` o `e_man`; tocar la campaña, el corpus o las predicciones.
- Promover la sensibilidad mixta de c-221; incorporar el término `r = 22,06 s` a `B`; reabrir el
  umbral del 85 %.
- Recalcular cualquier valor de las secciones `3.1` a `3.32` del memo; editar `CHANGES.md`.
- Fijar el número de sección del memo en el diseño (política, no valor).

## Decisions

### D1 — Propagación de incertidumbre: suma de extremos, con intervalo condicional por separado

**Elegido.** Dos intervalos distintos y rotulados:

1. **Condicional con `c` fijo.** Bootstrap percentil por caso al 95 % (`B = 2000`, semilla
   `20261021`) con `c = 69,51 s` como constante: aísla la incertidumbre muestral de
   `e_aut − e_man`. Se recomputa (no se interpola): el IC de `B` de la `3.21` depende del
   emparejamiento por caso y no es `c · (N/3.600) · IC(diferencia)`, de modo que no puede
   extrapolarse desde la rejilla `5/10/15`.
2. **Combinado.** Suma de extremos (aritmética de intervalos) sobre el intervalo de `c`
   `[33,42; 106,56] s` y el intervalo del término `(e_aut − e_man)`: `B` se evalúa en las cuatro
   esquinas y se toma el mínimo y el máximo. Cota exterior conservadora; no asume independencia.

Se derivan de la misma mecánica `a*` (que depende de `e_man` y `c`, no de `N` ni de `e_aut`).

**Alternativa descartada — bootstrap conjunto.** Requeriría un índice común entre la población de
`c` (intervenciones de la campaña complementaria y decisiones del brazo manual) y la población de
`e_aut − e_man` (138 casos de consenso / 151 derivaciones). Ese índice **no existe**: las
poblaciones son distintas y el memo ya declara el desajuste de unidad (`e_aut` por caso, `e_man`
por derivación) como límite no igualable. Un bootstrap conjunto exigiría asumir una dependencia
que no está medida, y además re-derivar por caso la composición de `c`, que c-220 ya fijó por suma
de extremos. La coherencia con c-220 y la ausencia de un vínculo medido deciden la suma de extremos.

### D2 — Referencia base y estatus de la grilla previa

**Elegido.**

- **Base canónica:** la **referencia común de la `3.21`** (consenso `E1`/`E2`:
  `e_aut = 28/138`, `e_man = 26/151`), con `c = 69,51 s` de la `3.31`. Es la lectura central del
  balance y la única que reemplaza al supuesto.
- **Grilla previa:** la rejilla de `e_man ∈ {10 %, 15 %, 20 %, 26,5 %}` y `c ∈ {5, 10, 15} min`
  (memo `3.11`) y el resultado «10 a 15 minutos» de `08` **se conservan con sus cifras** y se
  rotulan como **sensibilidad del supuesto superado** (estado `condicional`), no como insumo
  vigente. La fila central de `tab:balance-neto` pasa a ser el `c` medido.
- **Sensibilidad mixta de c-221** (`+28,2 / +25,1`): se conserva citada desde la `3.32` como
  sensibilidad que mezcla corpus y referencias; **no** se promueve ni reemplaza al balance.

**Alternativa descartada:** usar la sensibilidad de c-221 (tasa fuera de muestra) como lectura
central, porque mezcla corpus y referencias y el memo la rotula explícitamente como no
sustitutiva. **Alternativa descartada:** retirar la grilla superada, porque la spec exige
«con sus cifras conservadas» y el tribunal valoró la trazabilidad del supuesto reemplazado.

### D3 — Pasajes de la tesis y consistencia con `a*`

| Pasaje | Qué cambia | Por qué |
|---|---|---|
| `08-discusion.tex:84` (definición de `c`) | El insumo central pasa a ser `c = 69,51 s`, IC `[33,42; 106,56] s` (memo nueva sección, `3.31`), con remisión. El supuesto `10 a 15 min` se rotula como reemplazado | El balance deja de apoyarse en una estimación sin registro |
| `08-discusion.tex:107` | Se conserva y rotula como sensibilidad del supuesto superado (cifras `304`, `50,7/76,1 h`, `−18,5/−43,9 h` conservadas) | La spec exige conservar la grilla con sus cifras |
| `08-discusion.tex:111` | La fila del `c` medido pasa a lectura central; el intervalo combinado y el condicional se informan; el signo se enuncia solo si el intervalo lo fija | La lectura canónica la fija el `c` medido |
| `08-discusion.tex:115` | Intacta (sensibilidad mixta de c-221, rotulada) | No se promueve |
| `08-discusion.tex:117` | La viabilidad operativa se declara con el signo y el rango que el intervalo sostenga, y remite a `subsec:balance-neto` | La condición pasó de «costo supuesto» a «costo medido» |
| `tab:balance-neto` | Fila/columna central = `c` medido; la rejilla rotulada como superada; nota con el método de propagación y el redondeo | Coincidencia con el memo |
| `00-resumen.tex`, `09-conclusiones.tex` | Misma lectura y mismo signo; sin aumentar el conteo de palabras (≤ 34 ES / ≤ 31 EN) | Lectura única |
| `10-recomendaciones.tex` | El cronometraje pasa a **refinamiento del tramo largo** de `c`, no a condición para cerrar el balance | El balance ya usa el `c` compuesto medido |
| `12-anexos.tex` | Solo si existe una mención del balance; si no, queda sin cambios y sale del alcance | No crear una mención para luego citarla |

**Consistencia con `a*`.** Con el `c` medido, `a* ≈ 19,7 %`: muy por debajo de la exactitud estricta
observada contra la referencia común (`0,7971`) y del propio umbral del `85 %`. La prosa MUST NOT
presentar `a*` como fundamento del umbral (la justificación del `85 %` es la paridad medida de c-220
D6) ni reutilizar los `a* = 68,2/75,5/77,9 %` de la rejilla como lectura vigente; esos valores
quedan en la grilla superada. La contradicción a evitar es que el texto siga diciendo que el signo
depende del costo supuesto: con el `c` medido y el intervalo combinado el signo queda fijado, y esa
afirmación debe reemplazarse por el intervalo y la remisión.

**Checkpoint de gobernanza:** el cambio de estatus de la viabilidad operativa (de condicional a
positiva, si el intervalo lo fija) se confirma con los autores **antes** de editar `00`, `08`, `09`,
`10` y `12` (bloque C).

### D4 — Política de numeración del memo (sin fijar el número)

La sección nueva del memo toma el **primer número libre posterior a la última sección vigente**,
releyendo el índice al aplicar. Hoy la última es `3.32` (c-221), de modo que el número esperado es
`3.33`, pero **el diseño no lo fija** y ninguna tarea lo hardcodea: si al aplicar entra otra sección
(por ejemplo, coordinación con c-218/c-219/c-220), la nueva toma el libre que corresponda. La `3.21`
solo recibe líneas agregadas de remisión; no se renumera ni se reescribe ninguna sección previa.

### D5 — Diseño del script de recomputo

Archivo nuevo `evaluation/data/campana/analisis/analisis_balance_neto_c222.py` (pruebas en
`test_analisis_balance_neto_c222.py`), salidas `analisis_balance_neto_c222.json` y `.md` y
`.SHA256SUMS.txt` en la misma carpeta (UTF-8 sin BOM, LF, claves ordenadas). Solo lectura,
biblioteca estándar, sin red, sin Gemini, sin base de datos; determinista (`B = 2000`, semilla
`20261021`, nivel `0,95`); dos corridas byte a byte idénticas; `git status` limpio para entradas
después de correr.

Funciones puras, cada una con pruebas sintéticas antes de implementarla:

| Función | Qué calcula | Reutiliza |
|---|---|---|
| `balance_neto(n, delta_t, e_aut, e_man, c_s)` | `B = (N/3.600)[Δt − (e_aut − e_man)·c]` | — (patrón de c-221) |
| `exactitud_equilibrio(e_man, delta_t, c_s)` | `a* = 1 − e_man − Δt/c` | — |
| `ic_bootstrap_condicional(casos, c_s, b, semilla)` | Percentil por caso con `c` fijo (empareja derivaciones con su caso) | `evaluation/metrics.remuestreos_indices`, `percentil_intervalo` |
| `suma_de_extremos(valores)` | `min`/`max` sobre las esquinas `c ∈ {lo, hi}` × término ∈ `{lo, hi}` | — |

**Anclajes que abortan antes de escribir** (exit distinto de cero, sin salidas):
`+25,4 / +18,7 / +11,9` h-persona (referencia común, `c = 5/10/15 min`); `69,51 s` de c-220; y los
IC de la `3.21` en la rejilla (`[+8,6; +42,4]`, `[−15,0; +52,5]`, `[−38,6; +62,7]`), que validan la
reutilización del bootstrap por caso. Los conjuntos y umbrales se leen de los artefactos
versionados, no de constantes.

**Contrato de salida del `.json`:** `change`, `generador`, `entradas_sha256`, `anclajes`,
`insumos` (`n`, `delta_t_s`, `e_aut`, `e_man`, `c_s`, `c_ic`), `condicional_c_fijo` (`B`,
`B_ic`, `a_estrella`, `a_estrella_ic`), `combinado` (`B_ic`, `signo_fijado`, `metodo`),
`referencia_comun` y `grilla_superada` (celdas conservadas, rotuladas), y `trazabilidad` (cada
cifra remite a la clave que la produce).

### D6 — Gobernanza por bloque y checkpoints

| Bloque | Gobernanza | Checkpoint |
|---|---|---|
| A. Script de análisis | MEDIUM | Anclajes abortan; revisión del `git status` antes de congelar salidas |
| B. Memo canónico (sección aditiva + remisión `3.21`) | MEDIUM | `git diff` acotado a líneas agregadas; ninguna sección `3.1`–`3.32` cambia de cifra ni estado |
| C. Prosa de la tesis (`00`, `08`, `09`, `10`, `12`) | MEDIUM | **Confirmación de los autores** sobre la lectura central y el signo antes de editar (ver D3) |
| D. Trazabilidad (`dictamen-correcciones.md`) | MEDIUM | Matriz C22 con archivos y líneas; cierre de la decisión (i) |

Ningún bloque es HIGH: no hay datos de usuario, credenciales, migraciones de esquema ni artefactos
congelados. La única acción hacia afuera (publicar tag / PR) es responsabilidad del orquestador, no
de este change.

### D7 — Protocolo de verificación y unicidad de lecturas

- Anclajes del script: reproducir antes de escribir, abortar si no coinciden (bloque A).
- Memo: cada cifra nueva con archivo y ruta de origen o comando; las secciones `3.1`–`3.32`
  verificadas con `git diff` dirigido (solo líneas agregadas).
- Prosa: `rg` de las cadenas retiradas (`10 a 15 minutos` como insumo, `estimación propia` para `c`)
  y de las nuevas (cifra medida, remisión a la sección del memo); labels `subsec:balance-neto` y
  `tab:balance-neto` únicos; misma lectura y mismo signo en `00`, `08`, `09` y `12`; conteo de
  palabras del resumen sin aumentar.
- El número de sección del memo se relee al aplicar (D4), no se asume.

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| Promover la sensibilidad mixta de c-221 a balance canónico | D2 fija la referencia común; D7 verifica con `rg` que no reemplace al balance |
| Intervalo combinado mal propagado | D1 declara suma de extremos (cota conservadora) y reporta el condicional por separado; anclajes validan el bootstrap |
| El bootstrap condicional no reproduce la `3.21` por emparejamiento por caso | Anclajes sobre los tres IC de la `3.21`; aborta antes de escribir |
| Doble conteo del término de revisión `r` | `r` se mantiene aditivo y separado (c-220 D7); el escenario central no lo incorpora |
| Contradicción con `a*` (umbral del 85 % frente a `a* ≈ 19,7 %`) | D3 separa la justificación del umbral (paridad medida) de `a*`; la `a*` vieja queda en la grilla superada |
| Colisión de numeración del memo | D4: primer número libre al aplicar, releyendo el índice |
| Cambio de estatus de la viabilidad operativa sin respaldo | Checkpoint de los autores antes del bloque C (D6) |
| Deriva entre resumen, discusión, conclusiones y anexos | D7 compara la lectura en los cuatro; `12-anexos` solo si tiene mención |
| El resumen excede 250 palabras | Presupuesto explícito: se conserva el signo y el rango, el detalle remite al capítulo |
| Deriva de un artefacto de entrada por error | El script escribe solo tres nombres fijos; `git status` al final |

## Migration Plan

No hay migración de datos ni de esquema. Orden de aplicación:

1. Escribir test y script TDD; correr, reproducir anclajes y congelar salidas con su SHA-256.
2. Escribir la sección aditiva del memo (número libre) y la remisión desde la `3.21`; verificar que
   `3.1`–`3.32` no cambian.
3. Confirmación de los autores (D3/D6).
4. Editar la prosa de `00`, `08`, `09`, `10` y, si corresponde, `12`.
5. Registrar la entrada y la matriz C22 en `dictamen-correcciones.md`.
6. Correr `openspec validate … --strict` y las verificaciones `rg`.

**Rollback:** `git revert` del commit del change. El script, sus salidas y la sección nueva del memo
son aditivos; la `3.21` solo recibe una remisión y las ediciones de prosa son reemplazos localizados.
Como la grilla `5/10/15 min` se conserva como sensibilidad, el rollback no reconstruye valores ni
migra datos.

## Open Questions

- [ ] **Autores (bloquea bloque C):** confirmar la lectura central positiva y el cambio de estatus
      de la viabilidad operativa (de condicional a positiva) antes de editar la prosa.
- [ ] **Alcance de `12-anexos.tex`:** confirmar al aplicar si hay una mención del balance; si no,
      el archivo queda sin cambios y sale del alcance.
- [ ] **Resumen:** si el signo y el rango no entran en el límite de 250 palabras, decidir qué cifra
      se conserva y cuál remite al capítulo.
- [ ] **Número de la sección del memo:** el primer libre al aplicar (hoy `3.33`). No cambia specs,
      enfoque ni tareas.
- [ ] **Presentación en `tab:balance-neto`:** si la fila central informa el intervalo combinado, el
      condicional, o ambos, en nota al pie. Decisión editorial.
