# Proposal: Acotar el balance neto y declarar el umbral a priori

## Why

La devolución de tercera instancia del tribunal (16/11/2026, 6,7/10) observa en A-01 que el balance
neto de `+30,6` horas-persona por trimestre «con signo fijado por la muestra» no está respaldado: omite
el término de revisión que el propio análisis del grupo midió (`r = 22,06` s por intervención,
`analisis_costo_derivacion_c220.md` L55-58, con el rótulo «el flujo automatizado SI agrega tiempo de
revision... NO se incorpora a `B`») y usa un costo `c = 69,51` s que solo cubre el tramo activo (24,01 s
de corrección en la compuerta más 45,50 s de mediana de decisión de sector del brazo manual como proxy
del rediagnóstico). El tramo de reanudación queda sin cota. Como la compuerta no detecta errores
(AUROC 0,5168), los errores llegan al sector receptor, de modo que `c` es una **cota inferior** del costo
y `B`, una **cota superior** del balance. Con la tasa de revisión observada (147/200), el tribunal
recalcula `B = +18,7` h-persona. Exige incluir la revisión en `B`, presentar `c` y `B` como cotas, retirar
«signo fijado por la muestra» y «viabilidad económica y operativa positiva» del Resumen, §9.5, §10 y la
Tabla 31 (`tab:cumplimiento-objetivos`), y restituir la lectura condicional de `v1.3.0`.

La observación M-01 agrega que la justificación del umbral del 85 % en §1.6 queda refutada por las
propias cifras. Con el `c` adoptado, la exactitud de equilibrio es 19,7 %, no 85 %. La paridad con el
82,78 % manual y el «0,5 horas-persona por punto» se midieron en noviembre y no pueden fundar un umbral
fijado a priori. El tribunal pide declarar el 85 % como criterio a priori de los autores y trasladar a la
discusión, rotulados como posteriores, los argumentos que dependen de mediciones nuevas.

Además, el memo canónico se contradice: la Sección 3.11 (`numeros-canonicos.md` L585) supone que «el
flujo automatizado no agrega tiempo de revisión», y la 3.31 (h) (L2255-2260) registra que sí lo agrega.

## What Changes

| Bloque | Qué cambia | Gobernanza |
|---|---|---|
| **A. Análisis offline** | Script sucesor y aditivo `evaluation/data/campana/analisis/analisis_balance_neto_c236.py`, con TDD estricto. No modifica `analisis_balance_neto_c222.*` ni `analisis_costo_derivacion_c220.*`. Lee esos artefactos con SHA-256 y reproduce sus anclajes antes de calcular. Calcula `B_r = (N/3.600)[Δt − ρ·r − (e_aut − e_man)·c]` y `a*_r = 1 − e_man − (Δt − ρ·r)/c`, con `ρ = 147/200` y `r` = media de 138 duraciones. Reporta `B_r` como cota superior respecto del tramo no medido, con su intervalo condicional y su cota combinada. Agrega la sensibilidad al tramo no medido (rejilla de 5, 10 y 15 min con revisión) y el costo de equilibrio `c*`. Emite `.json`, `.md` y `SHA256SUMS`, deterministas byte a byte. | MEDIUM |
| **B. Memo canónico** | Sección aditiva nueva en `numeros-canonicos.md` (primer número libre al aplicar; hoy la última es la `3.44`). Registra insumos, fórmula, cotas, estados y procedencia. Agrega notas, sin reescribir nada: en la 3.11, que el supuesto «no agrega tiempo de revisión» queda refutado por la 3.31 (h) y corregido en la sección nueva; en la 3.31 (h) y la 3.33, que `r` se incorpora a `B` desde la sección nueva y que «signo fijado» queda retirado. | MEDIUM |
| **C. Prosa del balance** | §9.5 completo (`08-discusion.tex` L82-127): fórmula con término de revisión, `c` como cota inferior del tramo activo, `B` como cota superior, tabla reescrita, rejilla rotulada como sensibilidad al tramo no medido y retiro de «signo fijado» y de «viabilidad... positiva». Alineados con la misma lectura: Resumen y Abstract (`00-resumen.tex` L15 y L31), §1.2 (`01-introduccion.tex` L18), §4.3 (`04-marco-metodologico.tex` L101), §10 (`09-conclusiones.tex` L6 y fila L22 de `tab:cumplimiento-objetivos`), §11 (`10-recomendaciones.tex` L34) y los valores del balance del Anexo J (`12-anexos.tex` L267-289). | MEDIUM, con checkpoint de autores antes de Resumen y conclusiones |
| **D. Umbral a priori** | §1.6 (`01-introduccion.tex` L48): el 85 % se declara criterio fijado a priori por los autores, con los argumentos que existían antes de medir (literatura, estimación propia de 10 a 15 min y tasa preliminar del 15 %, margen del intervalo). Salen de §1.6 la frase refutada «tiempos de resolución comparables» con `c` medido, la paridad 82,78 % y el «0,5 h por punto», que pasan a §9.5 rotulados como lecturas posteriores. Se concilian `08-discusion.tex` L117 y L121 y el Anexo J (`12-anexos.tex` L261-262). | MEDIUM |

**No objetivos.**

- No se mide de nuevo nada: `c`, `r`, `ρ`, `e_aut` y `e_man` salen de artefactos versionados.
- No se incorpora ninguna cifra fuera de muestra (`+13,2`, `−28,9`, `+28,2`, `+25,1`). c-235 retira esa
  validación y quita de §9.5 las líneas de sensibilidad fuera de muestra (`08-discusion.tex` L119 en
  la parte que corresponda y L125). Este change se aplica **después** de c-235 y no las restituye.
- No se mueve el umbral del 85 % ni el veredicto de la tercera sub-hipótesis.
- No se cambia el formato del Anexo J: la columna «Estado», las referencias al «memo» y el texto
  superpuesto son de c-238. Aquí solo cambian los **valores** del balance que el anexo transcribe.
- No se tocan `docs/defensa/respuestas-tribunal.md` (c-239), la matriz de trazabilidad, la versión,
  la compilación final ni el tag (c-239).
- No se modifica ningún valor ni estado de las secciones previas del memo; solo se agregan notas de
  remisión.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `evaluation-framework`: se agrega el requisito del recomputo offline del balance con el término de
  revisión, el costo como cota inferior y la sensibilidad al tramo no medido.
- `tesis-numeros-canonicos`: se agrega el requisito del registro aditivo del balance acotado y del
  cierre, por nota, de la contradicción entre las secciones 3.11 y 3.31 (h).
- `tesis-document`: se modifican «Balance neto entre el ahorro de registro y el costo de las
  derivaciones erroneas», «Viabilidad operativa presentada como condicional», «Registro canonico del
  balance neto y sus supuestos», «Linea futura de medicion de la exactitud manual y del costo de
  reasignacion», «Exactitud del brazo manual y balance neto según la campaña de medición» y «Fuente
  del criterio del umbral del 85 por ciento».

## Impact

| Área | Impacto | Descripción |
|---|---|---|
| `evaluation/data/campana/analisis/analisis_balance_neto_c236.py` | Nuevo | Recomputo de solo lectura, biblioteca estándar, sin red ni base de datos |
| `evaluation/data/campana/analisis/test_analisis_balance_neto_c236.py` | Nuevo | TDD de las funciones puras y de los anclajes |
| `evaluation/data/campana/analisis/analisis_balance_neto_c236.{json,md,SHA256SUMS.txt}` | Nuevo | Salidas deterministas |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Aditivo | Sección nueva y notas de remisión en 3.11, 3.31 (h) y 3.33 |
| `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` | Modificado | §9.5 completo |
| `docs/Tesis/v10 (IA)/paper/sections/00-resumen.tex` | Modificado | Frase de viabilidad del Resumen y del Abstract |
| `docs/Tesis/v10 (IA)/paper/sections/01-introduccion.tex` | Modificado | L18 (saldo condicional) y L48 (umbral a priori) |
| `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` | Modificado | L101 (`c` como cota inferior y uso en el balance) |
| `docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex` | Modificado | L6 y fila L22 de `tab:cumplimiento-objetivos` |
| `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex` | Modificado | L34 (el cronometraje de la reanudación vuelve a condicionar el signo) |
| `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` | Modificado (valores) | Filas del balance y del umbral del Anexo J |

No cambian `App/`, `n8n/`, el clasificador, los corpus, las predicciones ni los artefactos de c-220 y
c-222. No hay llamadas a Gemini.

## Trazabilidad con la devolución

| Origen | Qué exige | Cómo lo cierra este change |
|---|---|---|
| A-01 y §7 punto 3 | Revisión en `B`; `c` cota inferior y `B` cota superior; retirar «signo fijado» y «viabilidad económica y operativa positiva»; restituir la lectura condicional | Bloques A, B y C |
| M-01 y §7 punto 6 | 85 % como criterio a priori; argumentos posteriores a la discusión | Bloque D |
| §8 preguntas 6 y 7 | Por qué 45,5 s representan el costo; por qué no se descuenta la revisión | §9.5 declara que el proxy cubre solo el tramo activo y que la revisión se descuenta |
| §8 pregunta 8 | Recomendación con 10 minutos | §9.5 informa la rejilla con revisión y el costo de equilibrio (sin cifras fuera de muestra) |

## Risks

| Riesgo | Prob. | Mitigación |
|---|---|---|
| Elegir media o mediana de `r` después de ver el signo | Media | La elección (media, por ser el estimador del total) se fija en `design.md` D2 y en el docstring antes de generar las salidas. El preregistro se declara **no ciego**, porque el tribunal ya publicó `+18,7`. La mediana se informa solo como sensibilidad |
| Presentar `+18,7` como valor del balance real | Alta | El texto lo nombra «cota superior con el tramo activo medido». El signo del balance real no se declara fijado: depende del tramo de reanudación no medido |
| Doble conteo entre `r` y el tramo de compuerta de `c` | Media | Se declara en D3 y se informa la variante sin solapamiento como sensibilidad del memo |
| Choque con c-235 en §9.5 y en el Resumen | Media | Se aplica después de c-235. El checkpoint 0.2 relee el estado real de `08-discusion.tex` y `00-resumen.tex` antes de editar |
| Exceder 250 palabras en el Resumen | Media | La frase nueva no supera las 34 (ES) y 31 (EN) palabras del párrafo; se cuenta con la regla de c-106 |
| Colisión de numeración del memo | Media | Se toma el primer número libre al aplicar, después de c-235 |

## Rollback Plan

`git revert` del commit del change. El análisis y la sección del memo son aditivos, y las notas de
remisión son líneas agregadas. Las ediciones de prosa son reemplazos localizados que el diff revierte.

## Success Criteria

- [ ] El script reproduce los anclajes `B = 30,64` h, `c = 69,51` s y `r = 22,06` s, y aborta sin escribir
      si alguno no coincide.
- [ ] `B_r ≈ +18,7` h-persona (cota superior), con sus intervalos y método declarados; `a*_r ≈ 43,1 %`.
- [ ] Ninguna sección de la tesis dice «signo fijado», «queda fijado por la muestra» ni «viabilidad
      económica y operativa positiva». La viabilidad operativa queda condicional al tramo de reanudación
      no medido.
- [ ] §1.6 declara el 85 % como criterio a priori sin apoyarse en cifras de noviembre. §9.5 rotula
      como posteriores la paridad 82,78 % y `a*`.
- [ ] La contradicción de las secciones 3.11 y 3.31 (h) del memo queda cerrada por nota, sin cambiar
      cifras ni estados previos.
- [ ] `openspec validate c-236-acotar-el-balance-neto-y-declarar-el-umbral-a-priori --strict` pasa.
