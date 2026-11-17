# Design: Acotar el balance neto y declarar el umbral a priori

## Context

**Estado vigente (v1.5.2).** §9.5 (`08-discusion.tex` L82-127, `subsec:balance-neto`) usa
`B = (N/3.600)[Δt − (e_aut − e_man)·c]` y `a* = 1 − e_man − Δt/c`, con `N = 2.646`, `Δt = 43,82` s,
`e_aut = 28/138`, `e_man = 26/151` y `c = 69,51` s (IC `[33,42; 106,56]`). De ahí salen `B = +30,6` h-persona
(IC condicional `[+26,7; +34,6]`, cota combinada `[+23,8; +35,8]`) y `a* = 19,7 %`. La fuente es
`analisis_balance_neto_c222.json` (`condicional_c_fijo`, `combinado`). L121 y L127 concluyen «el signo
queda así fijado por la muestra» y «la viabilidad económica y operativa... resulta también positiva».

**Anclajes verificados para este diseño** (verificados el 2026-11-16 contra los archivos).

| Anclaje | Ubicación | Contenido |
|---|---|---|
| Fórmula e insumos | `08-discusion.tex:84` | Sin término de revisión |
| Tabla | `08-discusion.tex:86-115` | Fila central L96. Rejilla histórica con `e_aut = 53/200` en L100-112 (−18,5 / −43,9 en L108). Nota L114 |
| Umbral = paridad 15 % | `08-discusion.tex:117` | «El umbral del 85 % equivale a la paridad con el 15 % manual» |
| Signo fijado; justificación del 85 % por paridad medida | `08-discusion.tex:121` | |
| Sensibilidad fuera de muestra | `08-discusion.tex:125` | La retira c-235 |
| Síntesis | `08-discusion.tex:127` | «viabilidad económica y operativa... positiva» |
| Resumen y Abstract | `00-resumen.tex:15`, `:31` | Párrafos de 34 y 29 palabras; resumen completo con 240 y 218 palabras (`wc -w` L7-15 y L23-31) |
| Saldo condicional a la tasa a priori | `01-introduccion.tex:18` | Hoy es inconsistente con §9.5 |
| Umbral con tres criterios | `01-introduccion.tex:48` | El segundo usa `c` medido, la paridad 82,78 % y 0,5 h por punto |
| Justificación sin mejora neta | `01-introduccion.tex:62` | Ya es coherente; solo se verifica |
| Definición de `c` | `04-marco-metodologico.tex:101` | «el umbral del 85 % y el balance neto no se modifican» |
| Conclusiones | `09-conclusiones.tex:6`, `:22` | «viabilidad económica y operativa resulta positiva»; fila «viabilidad operativa positiva con el costo medido» |
| Recomendaciones | `10-recomendaciones.tex:34` | «esa medición no es condición para cerrarlo» |
| Anexo J | `12-anexos.tex:247-289` | Filas del `c` (L258-262; L261-262 paridad y costo marginal) y del balance (L278-286) |
| Término de revisión | `analisis_costo_derivacion_c220.json` (`termino_revision`) | media 22,063167 s; n 138; IC media [15,4893; 29,3933]; mediana 9,9565; desvío 43,40 |
| Tasa de revisión | `07-resultados.tex:186` | 147 de 200 (73,5 %; Wilson [67,0 %; 79,1 %]); regla VIS-005: 66 casos de correo, 81 de telefonía, 0 de web |
| Contradicción del memo | `numeros-canonicos.md:585` frente a `:2255-2260` | 3.11 dice «no agrega tiempo de revisión»; 3.31 (h) dice que sí |
| Lectura condicional de referencia | `git show v1.3.0:".../08-discusion.tex"` L97-99 | «El balance neto es, entonces, condicional al costo...; la operativa es condicional» |

**Hallazgo lateral.** Las claves de procedencia del Anexo J (`escenario_central`, `grilla_minutos`,
L278 y L285-286) no existen en `analisis_balance_neto_c222.json`. Este change reemplaza esas filas
por las claves reales del `.json` sucesor. El formato de la tabla sigue a cargo de c-238.

**Orden.** c-235 se aplica antes y retira de §9.5 las sensibilidades fuera de muestra (L119 en lo que
corresponda y L125), además de los párrafos del Anexo J sobre el arbitraje por mayoría y la robustez de
la brecha. Al aplicar, las líneas citadas pueden haberse desplazado. La tarea 0.2 relee el estado real.

## Goals / Non-Goals

**Goals:**

- Incluir el término de revisión en `B` y en `a*` con una regla fijada antes de calcular.
- Presentar `c = 69,51` s como cota inferior (solo el tramo activo) y `B` como cota superior.
- Restituir la lectura condicional: el signo del balance depende del tramo de reanudación no medido.
- Declarar el 85 % como criterio fijado a priori y mover a §9.5 los argumentos posteriores.
- Cerrar por nota la contradicción de las secciones 3.11 y 3.31 (h) del memo.

**Non-Goals:**

- Medir el tramo de reanudación o cronometrar reasignaciones.
- Cualquier cifra fuera de muestra (c-235).
- El formato del Anexo J (c-238), las respuestas al tribunal y el release (c-239).
- Cambiar `c`, `r`, `ρ`, `e_aut`, `e_man`, el umbral o cualquier veredicto.

## Decisions

### D1. Forma del término de revisión

`B_r = (N/3.600) · [Δt − ρ·r − (e_aut − e_man)·c]` y `a*_r = 1 − e_man − (Δt − ρ·r)/c`.

- `ρ = 147/200 = 0,735` es la proporción de casos que reciben revisión humana en la configuración
  evaluada (regla VIS-005). `r` es el tiempo-persona medio por revisión. El flujo manual no tiene una
  revisión equivalente posterior al registro: su decisión de sector ya está dentro de los 61,6 s.
  Por eso el término solo resta del lado automatizado.
- **Alternativa descartada: `ρ = 1`.** Aplica `r` a todo `N`, como el efecto de 16,22 h de la 3.31 (h).
  Sobreestima la revisión, porque el formulario web (53 de 200) no se revisa con esa regla. Queda como
  sensibilidad (`B ≈ +14,4`).
- **Alternativa descartada: `ρ = 25/200` (solo cambios).** Confunde costo de revisión con costo de
  corrección. Toda revisión consume tiempo, la confirme o la cambie.
- **Límite declarado.** `ρ` depende de la mezcla de canales del corpus (59 % de canales sin
  identificación automática del reportante) y de la regla VIS-005. Un universo con otra mezcla tiene
  otro `ρ`.

### D2. Media y no mediana de `r` (fijado antes de generar las salidas)

Se usa la **media** (22,0632 s). `B` agrega tiempo sobre `N·ρ` revisiones: el estimador del total es
`N·ρ·media`. La mediana (9,9565 s), con una distribución sesgada a derecha (desvío 43,40 > media),
subestimaría el total. La mediana se informa solo como sensibilidad (`B ≈ +25,3`) y nunca como lectura
central.

**Preregistro no ciego.** La regla se fija en el docstring del script antes de generar sus salidas.
El valor central ya es conocido (el tribunal lo publicó: `+18,7`). Se declara así en el `.md`, el `.json` y
el memo, como hicieron c-220 y c-222.

**Inconsistencia declarada, sin corregir.** El tramo de rediagnóstico de `c` usa una mediana (45,50 s),
no una media (48,36 s). Cambiarlo reescribiría el `c` canónico de la 3.31, fuera del alcance. Se
declara como límite: con la media, `c` sería mayor y `B`, menor. Esto refuerza la lectura de cota
superior.

### D3. Solapamiento entre `r` y el tramo de compuerta de `c`

`r` promedia las 138 revisiones, incluidas 24 con `cambio_sector = true`. El tramo de compuerta de `c`
(24,01 s) es el tiempo **adicional** de esas correcciones. Contar ambos podría imputar dos veces unos
`24·24,01/138 ≈ 4,18` s por revisión, unas 2,3 h-persona por trimestre.

- **Decisión:** la lectura central usa la `r` total (22,06 s), que es la cifra medida y la que el tribunal
  recalculó. La variante sin solapamiento (`r` de las confirmaciones, 17,89 s) da `B ≈ +21,0` y se
  registra en el memo como sensibilidad. Ninguna de las dos fija el signo del balance real (D5).
- **Alternativa descartada:** tomar la variante sin solapamiento como central. Daría una cifra más
  favorable, apoyada en un supuesto sobre qué eventos cubre `c` que c-220 no define.

### D4. Incertidumbre

1. **Intervalo condicional** (`c` y `ρ` fijos): bootstrap percentil al 95 %, `B = 2000`, semilla `20261021`.
   Se remuestrean de forma independiente los casos de la referencia común (para `e_aut − e_man`, como
   en c-222, reutilizando su emparejamiento) y las 138 duraciones (para `r`). El supuesto de
   independencia se declara: son artefactos y sujetos distintos.
2. **Cota combinada por suma de extremos** sobre 16 esquinas: `ρ ∈` Wilson `[0,6698; 0,7913]`,
   `r ∈ [15,49; 29,39]`, `e_aut − e_man ∈ [−0,0460; +0,1070]`, `c ∈ [33,42; 106,56]`. Es la cota
   exterior conservadora, coherente con c-220 y c-222. Se rotula como cota **del tramo activo medido**,
   no como intervalo del balance real, porque `c` no tiene cota superior.

### D5. Lectura: cota superior y sensibilidad al tramo no medido

- `B_r` se informa como **cota superior** del balance: incluye solo el tramo activo de `c`. Si se suma el
  tramo de reanudación, `c` crece y `B` baja.
- La rejilla de 5, 10 y 15 minutos vuelve a ser **sensibilidad al tramo no medido** (deja de ser
  «supuesto superado»). Se recalcula con la referencia común **y** con el término de revisión.
- Se informa el **costo de equilibrio** `c* = (Δt − ρ·r)/(e_aut − e_man)` y el margen del tramo no
  medido, `c* − 69,51` s. También se informa `c*` con el extremo superior de `e_aut − e_man`.
- El signo **no** se declara fijado. La viabilidad operativa es condicional a que el tramo de
  reanudación quede por debajo de ese margen. El texto lo dice con las cifras.

**Valores esperados** (cálculo directo con los insumos versionados; el script los reproduce y los fija):

| Magnitud | Valor esperado |
|---|---|
| Efecto de la revisión `N·ρ·r/3.600` | 11,919 h-persona |
| `B_r` central (cota superior) | **+18,72** (sin revisión: +30,64) |
| `a*_r` central | **43,07 %** (sin revisión: 19,74 %) |
| Intervalo condicional de `B_r` | aprox. [+13; +24]; lo fija el script. Desplazar el de c-222 da [+14,8; +22,6], sin variar `r` |
| Cota combinada (16 esquinas) | [+6,73; +28,19] |
| Rejilla con revisión, 5 / 10 / 15 min: `B_r` | +13,52 / +6,74 / −0,03 |
| Rejilla con revisión, 5 / 10 / 15 min: `a*_r` | 73,58 % / 78,18 % / 79,71 % |
| `c*` (punto) | 898,8 s (15,0 min); margen del tramo no medido ≈ 829 s (13,8 min) |
| `c*` con `e_aut − e_man = +0,1070` | ≈ 258 s (4,3 min); margen ≈ 188 s (3,1 min) |
| Sensibilidades | `r` mediana: +25,26; sin solapamiento: ≈ +21,0; `ρ = 1`: +14,42 |

Con 15 minutos, `a*_r` (79,71 %) coincide con la exactitud estricta contra el consenso (0,7971): el
balance central se anula. La lectura del texto es: la cota superior es positiva, pero basta un tramo
de reanudación del orden de 14 minutos (o de unos 3 minutos con el extremo desfavorable de la
diferencia de errores) para anularla.

### D6. Tabla `tab:balance-neto`

- **Panel 1, lectura central:** `B_r` y `a*_r` con el `c` medido como cota inferior, con su intervalo
  condicional y su cota combinada en la nota.
- **Panel 2, sensibilidad al tramo no medido:** referencia común con revisión, `c` = 5, 10 y 15 min,
  `B_r` y `a*_r` con sus intervalos bootstrap.
- La rejilla histórica (`e_aut = 53/200`, tasas manuales 10/15/20/26,5 %, sin revisión) sale de la tabla.
  Queda en el memo (3.11) y en una oración de §9.5 como lectura de la versión anterior
  (`−18,5 / −43,9`). Razón: mezcla referencias (L119 lo reconoce) y alarga la tabla que M-03 pide
  aliviar. Si los autores la quieren conservar, pasa al anexo de robustez de c-238 (Open Question 2).
- Las cifras del balance con exactitud laxa (`+42,1`, `+52,1`, `+62,0` y el rango `+28,9` a `+138,1`)
  pertenecen a la rejilla histórica sin revisión. Salen de §9.5 con ella y quedan en el memo.

### D7. Umbral del 85 % a priori (M-01)

- §1.6 declara que el 85 % es un criterio **fijado a priori por los autores**. Lo apoyan solo
  argumentos disponibles antes de medir: (i) la literatura toma como referencia a los clasificadores
  supervisados clásicos, sin piso numérico común; (ii) la estimación propia de los autores, a partir de
  la operación (10 a 15 minutos por reasignación y tasa preliminar del 15 %), según la cual el 85 %
  equivalía a la paridad con el flujo manual. Ambas son estimaciones a priori sin registro
  cuantitativo, como dice `v1.3.0`; (iii) el margen para que el intervalo pueda superar la frontera.
- Salen de §1.6 y pasan a §9.5, bajo el rótulo «lecturas posteriores (medidas en noviembre de
  2026), que no fundamentan el umbral»: el `c` medido, la paridad 82,78 %, el «0,5 h por punto» y
  `a*_r`. También sale la frase «una exactitud inferior al 85 % resultaría en tiempos de resolución
  comparables a los del flujo manual», que las cifras refutan.
- `08-discusion.tex:117` («equivale a la paridad con el 15 % manual») pasa a decir que esa
  equivalencia era la estimación a priori. L121 («cuya justificación es la paridad medida») pasa a decir
  que el umbral es un criterio a priori y que la paridad medida es una lectura posterior. Anexo J
  L261-262: las filas de paridad y costo marginal se rotulan como lecturas posteriores, no como
  justificación (solo el texto de la celda; el formato es de c-238). `04-marco-metodologico.tex:101`:
  «el umbral del 85 % y el balance neto no se modifican» pasa a decir que el umbral no se modifica y
  que el balance usa `c` como cota inferior del costo.

### D8. Memo canónico

- Sección nueva `3.N` (primer libre al aplicar, después de c-235; hoy `3.45`). Contiene insumos con
  procedencia y estado, fórmulas `B_r` y `a*_r`, D1 a D5 resumidos, valores, intervalos, `c*`,
  sensibilidades, comando de recálculo, SHA-256 y redondeo (una decimal, mitad hacia arriba).
- **Estados:** `B_r` y `a*_r` quedan `vigente` como cota superior. La rejilla con revisión queda
  `condicional`, porque depende del tramo no medido. `B = +30,6` de la 3.33 queda `retirado` como lectura
  central; se declara en la sección nueva, sin editar la 3.33. Las sensibilidades quedan
  `vigente (sensibilidad)`.
- **Notas agregadas, sin reescribir:**
  - 3.11, junto a L585: el supuesto «no agrega tiempo de revisión» quedó refutado por la 3.31 (h) y se
    corrige en la `3.N`.
  - 3.31 (h): `r` se incorpora a `B` desde la `3.N`, con `ρ = 147/200`.
  - 3.33: la lectura «signo fijado» queda retirada por la `3.N`.

### D9. Resumen y Abstract

El párrafo de cierre no supera 34 palabras (ES) y 31 (EN), y cada resumen no supera 250. Borradores
orientativos (los fija el checkpoint):

- ES (24 + 8 palabras): «Los hallazgos respaldan la viabilidad técnica y económica; la operativa es
  condicional: el balance neto, revisión incluida, es a lo sumo +18,7 horas-persona trimestrales.»
- EN (22 + 9): «The findings support technical and economic feasibility; operational viability is
  conditional: the net balance, including review, is at most +18.7 person-hours per quarter.»

«Económica» se refiere aquí al costo monetario de operación, que sigue siendo marginal; no al
balance de tiempo (Open Question 1).

## Risks / Trade-offs

- [El lector toma `+18,7` como el balance] → Se rotula siempre «a lo sumo» o «cota superior» y va
  junto al margen del tramo no medido.
- [La decisión media o mediana parece posterior] → Preregistro no ciego declarado; la regla
  (estimador del total) es independiente del signo; la mediana se reporta.
- [Doble conteo entre `r` y `c`] → D3: variante sin solapamiento en el memo.
- [Desplazamiento de líneas por c-235] → Tarea 0.2: se relee y se localiza por frase ancla, no por
  número de línea.
- [Requisitos de c-235 sobre los mismos bloques de spec] → Open Question 4.
- [Las cifras del Anexo J divergen de §9.5] → Una sola fuente (`analisis_balance_neto_c236.json`) y
  verificación con `rg`.

## Migration Plan

1. Análisis con TDD (grupo 1); el `.json` es la fuente única.
2. Memo (grupo 2).
3. Checkpoint de autores (0.4) y luego prosa (grupos 3 y 4).
4. Verificación con `rg`, recuento de palabras y compilación de control (grupo 5). La compilación final
   y el tag son de c-239.

Rollback: `git revert`; todo es aditivo o un reemplazo localizado.

## Open Questions

1. **«Viabilidad económica» en el Resumen.** ¿Se conserva como «costo monetario marginal», separada
   del balance de tiempo, como en `v1.3.0`? ¿O se elimina la palabra para no reabrir la objeción del
   tribunal? Recomendación: conservarla y definirla en §9.5 y §10 como costo monetario.
2. **Rejilla histórica (`e_aut = 53/200`, −18,5 / −43,9) y exactitud laxa.** ¿Salen de la tabla y quedan
   en una oración y en el memo (D6)? ¿O pasan al anexo de robustez de c-238?
3. **Variante central de `r`.** D3 elige la `r` total (+18,7, que coincide con el tribunal). ¿Los autores
   prefieren la variante sin solapamiento (+21,0) como central? Ninguna cambia la lectura condicional.
4. **Coordinación de specs con c-235.** Este change modifica «Balance neto entre el ahorro de registro
   y el costo de las derivaciones erroneas» y omite el escenario de la sensibilidad mixta fuera de
   muestra. Supone que c-235 retira «Balance neto con sensibilidad fuera de muestra» (REMOVED). Si
   c-235 también modifica el mismo requisito, al archivar c-236 (después) hay que integrar su
   texto.
5. **`ρ` para el universo.** ¿Se agrega una sensibilidad con la mezcla de canales del universo
   trimestral, si está registrada en el memo? Si no está, `ρ` queda como la del corpus, con su límite
   declarado.
