# Proposal: Recalcular el balance neto con el costo medido

## Why

El dictamen CONEAU del 2026-11-13 sobre `v1.3.0` descuenta los criterios 1 («Definición del
problema») y 3 («Objetivos») porque el umbral del 85 % «carece de fundamento numérico» y una de
sus anclas era una «estimación de los autores, sin un registro cuantitativo conservado». c-220
midió el costo de la derivación errónea: `c = 69,51` s, IC 95 % `[33,42; 106,56]` s, compuesto por
un tramo activo medido (24,01 s más una mediana proxy de rediagnóstico de 45,50 s). Su compuerta
D5 pre-registrada quedó en la rama B: el intervalo excluye la banda `[600; 900]` s, de modo que el
change no recalculó `B`. El dueño eligió la opción (i) el 2026-11-14: recalcular el balance neto
con el `c` medido en un change sucesor.

La tesis sigue, por lo tanto, con un costo que ya está medido pero con un balance que no lo usa:
`08-discusion.tex` conserva la grilla de 5, 10 y 15 minutos y el rango «10 a 15 minutos» como
supuesto, y la viabilidad operativa se declara condicional a un costo que dejó de ser una
estimación. c-221 aportó una sensibilidad con el `c` medido (`+28,2` y `+25,1` horas-persona por
trimestre), pero la rotuló explícitamente como sensibilidad que mezcla corpus y referencias y que
no reemplaza el balance con referencia común. Este change cierra esa brecha: convierte el `c`
medido en el insumo central del balance canónico y propaga el resultado a toda la prosa.

## What Changes

| Bloque | Qué cambia | Gobernanza |
|---|---|---|
| **A. Análisis offline** | Script nuevo de solo lectura `evaluation/data/campana/analisis/analisis_balance_neto_c222.py` (con pruebas TDD) que reproduce los anclajes de la referencia común de la sección 3.21 y el `c` de la 3.31, recalcula `B` y `a*` con el `c` medido, propaga la incertidumbre del `c` y de `e_aut − e_man` con el método declarado, y emite `.json`, `.md` y `SHA256SUMS` byte a byte deterministas. | MEDIUM |
| **B. Memo canónico** | Sección aditiva nueva en `numeros-canonicos.md`, posterior a la última vigente. El memo termina hoy en la `3.32`; la sección toma el primer número libre al aplicar (hoy sería `3.33`; el número no se fija en esta propuesta). Registra insumos, fórmulas, `B`, `a*`, intervalos, procedencia y estado por valor, y remite desde la `3.21` sin reescribirla. | MEDIUM |
| **C. Prosa de la tesis** | `08-discusion.tex` reemplaza el supuesto «10 a 15 minutos» por el `c` medido como insumo central, agrega el escenario medido y su intervalo a `tab:balance-neto`, rotula la grilla previa como sensibilidad superada y declara el signo solo si el intervalo lo fija. `00-resumen.tex`, `09-conclusiones.tex`, `10-recomendaciones.tex` y `12-anexos.tex` alinean la misma lectura. | MEDIUM |
| **D. Trazabilidad** | Entrada nueva en `dictamen-correcciones.md` que cierra la decisión (i) de D5 de c-220 y la observación del dictamen v1.3.0, con matriz C22 y los archivos afectados. | MEDIUM |

**No objetivos.**

- No se mide de nuevo: el `c` de c-220 es la fuente única y no se toca la campaña, el corpus ni
  las predicciones.
- No se promueve la sensibilidad mixta de c-221 (`+28,2` y `+25,1`) a balance canónico: mezcla
  corpus y referencias. La lectura central sigue siendo la referencia común de la sección 3.21.
- No se incorpora a `B` el término de revisión `r = 22,06` s: c-220 lo declara aditivo y separado.
- No se mueve el umbral del 85 %, no se reentrena, no se reclasifica y no se invoca a Gemini.
- No se modifica ningún valor ni estado de las secciones 3.1 a 3.32 del memo. La sección nueva es
  aditiva y la `3.21` solo recibe una remisión.
- No se edita `CHANGES.md` en esta fase (lo actualiza el orquestador).

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tesis-numeros-canonicos`: se agrega el requisito del registro aditivo del balance recalculado
  con el costo medido, con su incertidumbre, procedencia y estado por valor, y con el reemplazo
  explícito del supuesto previo.
- `tesis-document`: se modifican «Balance neto entre el ahorro de registro y el costo de las
  derivaciones erroneas» (el `c` medido pasa a insumo central y la grilla previa a sensibilidad
  superada), «Registro canonico del balance neto y sus supuestos» (estado del balance medido y de
  la grilla superada) y «Linea futura de medicion de la exactitud manual y del costo de
  reasignacion» (la cronometría directa pasa a refinar el tramo largo y no a condicionar el cierre
  del balance).
- `evaluation-framework`: se agrega el requisito del recomputo offline, determinista y de solo
  lectura del balance con el `c` medido.

## Impact

| Área | Impacto | Descripción |
|---|---|---|
| `evaluation/data/campana/analisis/analisis_balance_neto_c222.py` | Nuevo | Recomputo de solo lectura, biblioteca estándar, sin red ni base de datos |
| `evaluation/data/campana/analisis/test_analisis_balance_neto_c222.py` | Nuevo | TDD de las funciones puras y de los anclajes |
| `evaluation/data/campana/analisis/analisis_balance_neto_c222.json` | Nuevo | Salida versionada determinista |
| `evaluation/data/campana/analisis/analisis_balance_neto_c222.md` | Nuevo | Vista legible de las mismas cifras |
| `evaluation/data/campana/analisis/analisis_balance_neto_c222.SHA256SUMS.txt` | Nuevo | Huellas de las salidas y de las entradas |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Nuevo (aditivo) | Sección del balance recalculado y remisión desde la `3.21` |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Nuevo (aditivo) | Entrada de cierre de la decisión (i) y matriz C22 |
| `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` | Modificado | Insumo central, tabla, incertidumbre y lectura del balance |
| `docs/Tesis/v10 (IA)/paper/sections/00-resumen.tex` | Modificado | Lectura única del balance, sin aumentar el conteo de palabras |
| `docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex` | Modificado | Viabilidad operativa y remisión al balance |
| `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex` | Modificado | Cronometría futura como refinamiento, no como bloqueo |
| `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` | Modificado | Mención coherente con el balance recalculado, si la hubiera |

Sin cambios en `App/`, `n8n/`, el clasificador, `docker-compose.yml`, la configuración, los corpus
ni las predicciones. Cero llamadas a Gemini. La propuesta no edita ningún `.tex`: las ediciones de
prosa pertenecen a la fase de aplicación.

## Trazabilidad con el dictamen CONEAU

| Origen | Qué decía | Cómo lo cierra este change |
|---|---|---|
| Dictamen CONEAU 2026-11-13 sobre `v1.3.0`, criterios 1 y 3 | El umbral del 85 % «carece de fundamento numérico»; una de sus tres anclas era el costo de la derivación errónea, «estimación de los autores, sin un registro cuantitativo conservado» | c-220 reemplazó la estimación por una medición (sección 3.31). c-222 cierra la consecuencia pendiente: el balance que usa ese costo se recalcula con la cifra medida y con su incertidumbre, y deja de declararse condicional a un supuesto |
| Decisión del dueño (2026-11-14), opción (i) de D5 de c-220 | Recalcular `B` con el `c` medido (`~69,51` s) en un change sucesor | Este change es ese sucesor. La opción (ii) —mantener «10 a 15 min» rotulado como tiempo calendario— quedó descartada y no se aplica |
| Memo canónico, sección 3.11 | El balance es «reversible si una réplica mide `c`» | La condición se activa: el `c` está medido y el balance se recalcula en la sección nueva, sin reescribir la 3.11 |
| c-221, sección 3.32 (h) | Sensibilidad con el `c` medido, rotulada como mezcla de corpus y referencias, que no reemplaza el balance con referencia común | Se conserva como sensibilidad. La lectura canónica se recalcula sobre la referencia común de la 3.21, no sobre la sensibilidad mixta |

No se abre una recomendación nueva del dictamen. La entrada de `dictamen-correcciones.md` registra
el cierre y remite a los artefactos de c-220 y c-221.

## Open Questions

- **Propagación de la incertidumbre.** El artefacto de c-207 conserva los intervalos de `B` y de
  `e_aut − e_man`, no la distribución bootstrap por caso. El diseño debe elegir entre la suma de
  extremos —cota conservadora, coherente con c-220— o un bootstrap conjunto si los insumos por caso
  están disponibles. La propuesta no fija el método; sí exige declararlo y reportar por separado el
  intervalo condicional con `c` fijo.
- **Límite de palabras del resumen.** El resumen y el *abstract* tienen un límite de 250 palabras y
  el margen es estrecho. Si el signo y el rango no entran sin exceder el límite, el diseño debe
  decidir qué cifra se conserva y cuál remite al capítulo.
- **Alcance de `12-anexos.tex`.** No se encontró una mención del balance en los anexos; al aplicar
  se confirma si la hay y, si no, el archivo queda sin cambios y se retira del alcance.

## Risks

| Riesgo | Prob. | Mitigación |
|---|---|---|
| Promover la sensibilidad mixta de c-221 a balance canónico | Media | La propuesta y el diseño fijan la referencia común de la 3.21 como lectura central; la mezcla queda rotulada como sensibilidad y una prueba de grep impide que reemplace al balance |
| Doble conteo del término de revisión `r` | Media | `r` se mantiene aditivo y separado, como lo declara c-220; el escenario central no lo incorpora |
| Intervalo combinado mal propagado (`c` e `e_aut − e_man`) | Media | Se declara el método (suma de extremos como cota conservadora, o bootstrap conjunto si el artefacto lo permite) y se informa por separado el intervalo condicional con `c` fijo |
| Colisión de numeración de la sección del memo | Media | Se toma el primer número libre al aplicar, releyendo el índice; no se fija en la propuesta |
| Deriva entre resumen, discusión, conclusiones y anexos | Media | Una sola lectura y verificación con `rg` de las cadenas prohibidas y de las cifras |
| El texto de recomendaciones siga diciendo que falta cronometrar para cerrar el balance | Media | Se modifica el requisito correspondiente y se ajusta la prosa en `10-recomendaciones.tex` |

## Rollback Plan

`git revert` del commit del change. El análisis es aditivo y de solo lectura: borrar el script, sus
salidas y la sección nueva del memo deja el repositorio en el estado previo. La `3.21` solo recibe
una remisión y las ediciones de `08`, `00`, `09`, `10` y `12` son reemplazos localizados y
reversibles con el diff. Como la grilla de 5, 10 y 15 minutos se conserva como sensibilidad, el
rollback no requiere reconstruir valores ni migrar datos.

## Dependencies

- Artefactos de c-220: `analisis_costo_derivacion_c220.json` y su vista `.md`, con el `c` compuesto
  `69,51` s e IC `[33,42; 106,56]` s.
- Artefactos de c-221: `analisis_propagacion_arbitraje_c221.json` y su vista `.md`, con la
  sensibilidad del balance y sus anclajes.
- Referencia común de la sección 3.21: `analisis_dictamen_c207.json`
  (`balance_neto_referencia_comun`), que aporta `B` y `a*` para 5, 10 y 15 minutos y el IC de
  `e_aut − e_man`.
- Memo canónico vigente hasta la sección 3.32 y la disciplina de estado por valor.
- `openspec/specs/tesis-numeros-canonicos/spec.md`,
  `openspec/specs/tesis-document/spec.md` y `openspec/specs/evaluation-framework/spec.md` vigentes.

## Success Criteria

- [ ] El script reproduce antes de calcular los anclajes `+25,4`, `+18,7`, `+11,9` y `69,51` s, y
      aborta sin escribir si no coinciden.
- [ ] `B` y `a*` se informan recalculados con el `c` medido y con su incertidumbre; el signo se
      enuncia solo si el intervalo lo fija.
- [ ] El supuesto «10 a 15 minutos» queda reemplazado como insumo central y la grilla previa queda
      rotulada como sensibilidad superada, sin borrar sus cifras.
- [ ] La lectura del balance es la misma en `00-resumen.tex`, `08-discusion.tex`,
      `09-conclusiones.tex` y `12-anexos.tex`, y no crece el conteo de palabras del resumen.
- [ ] Ningún valor ni estado de las secciones 3.1 a 3.32 del memo cambia; la sección nueva es
      aditiva y la numeración se fija al aplicar.
- [ ] Cada cifra nueva de la tesis existe antes en la sección del memo, con archivo y línea de
      origen o con el comando que la reproduce.
- [ ] `openspec validate c-222-recalcular-el-balance-neto-con-el-costo-medido --strict` pasa.