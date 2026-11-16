## Why

La limitación 2 del análisis de limitaciones estructurales de la tesis v1.4.1
(`docs/Tesis/Correcciones/analisis-limitaciones-estructurales-v1.4.1.md`, sección 3, propuesta P2) es
que el contraste del híbrido frente a la línea de base clásica se evaluó sobre la referencia
arbitrada completa (`206` casos) y, en su etapa previa, sobre los `103` casos con consenso, pero la
tesis informa el resultado del híbrido bajo dos lecturas más —consenso `E3`/`E4` (`n = 142`) y los
`150` originales sin exclusión (`n = 150`)— sin la lectura correspondiente de la línea de base. La
brecha híbrido menos línea de base (`+0,1990` sobre `206`) queda así atada a una sola elección de
referencia. El dictamen CONEAU post-v1.3.0 y el análisis preguntan si esa brecha es robusta a la
referencia; hoy no existe artefacto que lo responda.

Causa raíz: el contraste pareado de c-213 (capacidad `evaluation-baseline-paired-contrast`,
requisitos LBP-01 a LBP-03) acepta una única referencia por corrida (`--referencia`, `--n-esperado`)
y sus salidas versionadas cubren `103` y `206`, no los tres subconjuntos alineados con las lecturas
de la tesis. No es un defecto de datos: las predicciones por caso de ambos clasificadores están
versionadas y las tres particiones son derivables de artefactos existentes.

## What Changes

| Bloque | Qué cambia | Gobernanza |
|---|---|---|
| **A. Análisis** | Script nuevo de solo lectura, determinista y con pruebas (TDD estricto), `evaluation/data/campana/analisis/analisis_robustez_linea_de_base_c225.py`, que reconstruye las predicciones por caso de la línea de base (mismo módulo y semilla de c-209/c-213), lee las del híbrido de `predicciones_arbitrado.json` y reporta la brecha híbrido menos línea de base con IC bootstrap percentil pareado sobre tres subconjuntos: consenso `E3`/`E4` (`n = 142`), `150` originales sin exclusión (`n = 150`) y corpus arbitrado completo (`n = 206`). Reutiliza las funciones puras ya existentes de `evaluation.linea_de_base`, `evaluation.stats` y `evaluation.metrics`; no modifica el script ni los artefactos de c-213. | MEDIUM |
| **B. Prosa** | Tabla o párrafo nuevo en `07-resultados.tex` (junto a `tab:linea-base-clasica`) con la brecha y su IC en los tres subconjuntos, rotulada como sensibilidad/robustez; actualización breve de `08-discusion.tex` (limitación quinta) y, si el diseño lo confirma, un toque en la limitación séptima o en trabajo futuro. | MEDIUM |
| **C. Memo y trazabilidad** | Sección aditiva nueva `3.36` en `docs/Tesis/Correcciones/numeros-canonicos.md` (la `3.35` es de c-224), con cada cifra, su fuente y su comando; entrada en `docs/Tesis/Correcciones/dictamen-correcciones.md` con la matriz de trazabilidad. | MEDIUM |

**No objetivos.**

- No se cambia la cifra primaria `0,6893/206`, el macro-F1 `0,7024`, el veredicto del umbral `0,85`
  ni ningún otro valor `vigente` del memo canónico: todo es aditivo y rotulado como sensibilidad.
- No hay llamadas pagas a Gemini, no hay datos nuevos, no se reclasifica ni se reentrena.
- No se toca `App/`, `n8n/`, el clasificador de producción, `docker-compose.yml`, la configuración,
  el corpus ni las predicciones; no se modifica el script ni los artefactos de c-213.
- No se reabre la subsección `subsec:ruido-referencia` (c-216) ni `subsec:sesgo-corpus-referencia`
  (c-219); solo se remite a ellas si el diseño lo considera.
- No se edita `CHANGES.md` en esta fase (lo actualiza el orquestador al aplicar).
- No se recompila el PDF en este change (lo recompila el dueño al final).

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `evaluation-baseline-paired-contrast`: se agrega el requisito LBP-04, que extiende el contraste
  pareado a los tres subconjuntos de referencia (consenso `E3`/`E4`, `150` originales, arbitrado
  completo) con su IC por subconjunto, sus anclas verificadas y su carácter aditivo.
- `tesis-document`: se agrega un requisito que exige la tabla o párrafo de robustez de la brecha en
  `07-resultados.tex` y la lectura acotada en `08-discusion.tex`, sin cambiar cifras canónicas.
- `tesis-numeros-canonicos`: se agrega el requisito de registro aditivo de las cifras de robustez
  de la línea de base frente a la referencia, con su fuente y su comando.

`evaluation-framework` NO se modifica: la obligación es específica del contraste pareado de la línea
de base y vive mejor en la capacidad que ya gobierna ese contraste (`evaluation-baseline-paired-contrast`),
coherente con el precedente de c-223 («la obligación es específica ... y vive mejor en la capacidad
que ya gobierna esos artefactos»). Duplicarla en `evaluation-framework` fragmentaría la regla.

## Impact

| Área | Impacto | Descripción |
|---|---|---|
| `evaluation/data/campana/analisis/` | Nuevo | `analisis_robustez_linea_de_base_c225.py`, su prueba, `.json`, `.md` y `.SHA256SUMS.txt`; entrada en el README de la carpeta |
| `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` | Modificado | Tabla o párrafo de robustez junto a `tab:linea-base-clasica` |
| `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` | Modificado | Lectura acotada en la limitación quinta; toque condicional en la séptima |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Nuevo (aditivo) | Sección `3.36`, sin reemplazar valores previos |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Nuevo (aditivo) | Entrada que cierra la observación de robustez de la brecha |
| `openspec/specs/…` | Delta | LBP-04, requisito de prosa en `tesis-document`, registro aditivo en `tesis-numeros-canonicos` |

Sin cambios en `App/`, `n8n/`, el clasificador, la configuración, los corpus ni las predicciones.
Cero llamadas a Gemini.

## Risks

| Riesgo | Prob. | Mitigación |
|---|---|---|
| Que la lectura sobre tres subconjuntos parezca una medición nueva o elegida por favorable | Media | Rotular todo como sensibilidad/robustez; declarar que la cifra primaria sigue siendo `0,6893/206`; reportar los tres subconjuntos juntos, no el favorable solo |
| Que la brecha no sea robusta y contradiga el relato | Baja | Es un resultado admisible: se informa el rango real; si algún subconjunto pierde significación, se declara sin ocultarlo (el veredicto del umbral no cambia) |
| Deriva de anclas si se regeneran artefactos | Baja | El script aborta sin escribir si no reproduce `142/206`, `109/142` y `112/150`; no regenera insumos |
| Aumento del PDF por la tabla nueva | Media | Tabla compacta o párrafo dentro de la subsección existente; verificar `abspage@last` y compensar si hace falta |
| Colisión de la sección `3.36` del memo con otro change en curso | Baja | Tomar el primer número libre al aplicar (tarea 0.5); c-223 tomó la `3.34` y c-224 la `3.35` (ambas archivadas), así que el próximo libre es la `3.36` y la colisión posible es con el otro change activo (c-226) |

## Rollback Plan

- `git revert` del commit que agrega el script y sus salidas, la sección `3.36` del memo, la entrada
  de trazabilidad y los cambios de prosa en `07` y `08`.
- El script es aditivo y no modifica insumos ni artefactos de c-213: revertirlo no afecta ningún
  valor canónico ni el contraste vigente.

## Dependencies

- c-213 (`evaluation-baseline-paired-contrast`, script y artefactos del contraste), c-206/c-221
  (`predicciones_arbitrado.json`, `corpus_independiente_arbitrado.json`, `arbitraje_tres_vias.json`)
  y c-219 (lecturas por origen de la referencia que se reutilizan como anclas).
- Sin dependencias nuevas (scikit-learn, SciPy y las funciones puras de `evaluation/` ya están en uso).

## Success Criteria

- [ ] El script reproduce `142/206`, `109/142` y `112/150` antes de calcular y es determinista (dos corridas con el mismo SHA-256).
- [ ] Reporta la brecha híbrido menos línea de base con IC 95 % en los tres subconjuntos, para las dos variantes de la línea de base.
- [ ] Ninguna cifra nueva entra a la tesis sin estar antes en la sección `3.36` del memo.
- [ ] La cifra primaria `0,6893/206`, el macro-F1 `0,7024` y el veredicto del umbral `0,85` no cambian.
- [ ] `rg "c-[0-9]{3}"` sobre `sections/*.tex` no devuelve líneas fuera de comentarios; compilación sin errores ni citas indefinidas.
- [ ] `openspec validate c-225-robustez-de-la-linea-de-base-frente-a-la-referencia --strict` pasa.
