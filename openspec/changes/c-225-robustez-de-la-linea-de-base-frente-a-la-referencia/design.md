## Context

Ver `proposal.md` — Why. Estado actual que condiciona el diseño:

- `evaluation/data/campana/analisis/contraste_linea_de_base_c213.py` (c-213) ya reconstruye las
  predicciones por caso de la línea de base con `evaluation.linea_de_base.predecir` (semilla `42`),
  lee las del híbrido de un JSON de predicciones y calcula la tabla 2×2, el McNemar
  (`evaluation.stats.contraste_mcnemar`) y la diferencia de exactitudes con IC bootstrap percentil
  pareado. Sus funciones puras (`emparejar`, `contraste_pareado`, `verificar_anclas`) están probadas.
- Artefactos versionados disponibles: `predicciones_arbitrado.json` (híbrido, `206` casos),
  `corpus_independiente_arbitrado.json` (referencia arbitrada, `206` casos, ids `I001`..`I206`),
  `arbitraje_tres_vias.json` (por caso: `origen` ∈ {`consenso_e3_e4`, `arbitraje_e5`} y `tres_vias`),
  `linea_de_base_clasica_c210.json` (anclas de la línea de base) y
  `analisis_fuera_de_muestra_c205.json` (ancla del híbrido sobre `103`).
- Anclas verificadas con los artefactos (calculadas en la exploración): híbrido `142/206` sobre el
  arbitrado completo, `109/142` sobre consenso `E3`/`E4` y `112/150` sobre los `150` originales;
  línea de base balanceada `101/206` y sin re-ponderación `88/206` (c-213).
- La tesis informa las tres lecturas del híbrido (`0,6893/206`, `0,7676/142` y `0,7467/150`) en
  `subsec:validacion-fuera-muestra` y `subsec:sesgo-corpus-referencia`; la línea de base solo en
  `tab:linea-base-clasica` sobre `206`.

## Goals / Non-Goals

**Goals.**

- Reportar la brecha híbrido menos línea de base, con IC, sobre los tres subconjuntos, reutilizando
  predicciones versionadas y funciones puras ya existentes.
- Dejar la cifra primaria y el veredicto del umbral intactos; rotular todo como sensibilidad.
- Producir un artefacto determinista, con anclas verificadas, que la tesis cite como fuente única.

**Non-Goals (nivel de diseño).**

- No se modifica el script ni las salidas de c-213 (LBP-01..03 quedan vigentes tal cual).
- No se introduce una partición nueva ni un clasificador nuevo: la línea de base es la misma
  (TF-IDF + regresión logística, semilla `42`, entrenada con los `200` casos de ajuste).
- No se re-ejecuta ni se re-entrena nada; no hay I/O de red.

## Decisions

### D1. Script nuevo que reutiliza funciones puras, no extensión del script de c-213

Se crea `analisis_robustez_linea_de_base_c225.py` en lugar de editar `contraste_linea_de_base_c213.py`.

- **Por qué**: el script de c-213 es la fuente de artefactos ya citados por la tesis
  (`contraste_linea_de_base_c213_arbitrado.json`); editarlo arriesga cambiar sus salidas versionadas
  y sus anclas. Un script nuevo es aditivo, mantiene c-213 intacto y sigue el patrón del proyecto
  (cada change agrega su propio análisis: `analisis_sesgo_corpus_referencia_c219.py`,
  `analisis_propagacion_arbitraje_c221.py`, `analisis_balance_neto_c222.py`).
- **Alternativas consideradas**: (a) extender el script de c-213 con un modo `--subconjuntos`; se
  descartó por el riesgo sobre las salidas vigentes y porque mezclaría dos cambios en un artefacto.
  (b) importar el script de c-213 como módulo; se descartó porque el nombre con número lo hace
  frágil; en su lugar se reutilizan las dependencias puras compartidas
  (`evaluation.linea_de_base`, `evaluation.stats`, `evaluation.metrics`).
- **Reutilización**: `predecir` (semilla `42`), `contraste_mcnemar`, `remuestreos_indices`,
  `percentil_intervalo`, `NIVEL_CONFIANZA`, `SEMILLA_BOOTSTRAP` (`20261021`) y
  `metricas_de_prediccion`. La tabla 2×2 y el IC se calculan con la misma convención que c-213
  (IC bootstrap percentil pareado, `10000` remuestreos).

### D2. Definición de los tres subconjuntos

Derivados de artefactos versionados, sin reglas ad hoc:

- `consenso_e3_e4` (`n = 142`): casos con `origen == "consenso_e3_e4"` en `arbitraje_tres_vias.json`.
- `original_150` (`n = 150`): casos con id `I001`..`I150` del corpus arbitrado (diseño original sin
  exclusión por discordancia).
- `arbitrado_completo` (`n = 206`): todos los casos del corpus arbitrado.

La partición `arbitraje_e5` (`n = 64`) y la bandera `tres_vias` (`6` casos) se informan como
contexto, pero no son subconjuntos de contraste (los `64` no tienen consenso y su lectura ya está
en c-219/c-221).

### D3. Anclas obligatorias antes de escribir

El script aborta sin escribir salidas si no reproduce: híbrido `142/206`, `109/142` y `112/150`;
línea de base balanceada `101/206`; línea de base sin re-ponderación `88/206`. Las anclas del
híbrido sobre los subconjuntos `142` y `150` coinciden con las lecturas de `subsec:validacion-fuera-muestra`
y `subsec:sesgo-corpus-referencia`. Si un ancla falla, termina con error y no escribe.

### D4. Método de contraste idéntico al de c-213

Por subconjunto y por variante (`balanceada`, `sin_repoderacion`): tabla 2×2 (ambos aciertan, solo
híbrido, solo línea de base, ninguno), McNemar con `p` exacta bilateral y `p` corregida por
continuidad (criterio de `stats.py`: exacta si `b + c < 25`), y diferencia de exactitudes
`(b − c)/n` con IC 95 % bootstrap percentil pareado (`10000` remuestreos, semilla `20261021`). Se
declara el método en el propio artefacto. No se aplica corrección por multiplicidad: las tres
lecturas son descriptivas y se reportan juntas, con esa salvedad explícita.

### D5. Sección `3.36` del memo canónico

El memo termina en la `3.35` (c-224); la sección nueva es la `3.36`, la primera libre. Se fija en
la tarea 0.5 antes de escribir la prosa. Registra cada cifra con su fuente (JSON) y su comando, en
estado `vigente (nuevo)`.

### D6. Ubicación de la prosa en la tesis

- `07-resultados.tex`: tabla o párrafo corto dentro de la subsección donde vive `tab:linea-base-clasica`,
  con la brecha y su IC en los tres subconjuntos; fuente: el JSON nuevo.
- `08-discusion.tex`: una o dos oraciones en la limitación quinta (comparación con clasificadores
  alternativos) que declaren que la conclusión sobre la línea de base no depende de una sola
  referencia. Toque condicional en la limitación séptima (ajuste y evaluación sobre el mismo corpus)
  solo si el diseño confirma que aporta.
- Sin etiquetas nuevas de subsección si el párrafo cabe en las existentes (control de páginas).

### D7. Rótulo y no regresión

Todo el bloque se rotula «sensibilidad/robustez». La cifra primaria `0,6893/206`, el macro-F1
`0,7024` y el veredicto del umbral `0,85` no cambian; el memo lo declara en la sección `3.36`. Si la
brecha pierde significación en algún subconjunto, se informa el rango real sin ocultarlo.

### D8. Gobernanza MEDIUM

El análisis es LOW (solo lectura), pero la prosa que entra al documento evaluado por el tribunal es
MEDIUM; se aplica MEDIUM al conjunto, con checkpoints tras el análisis y tras la prosa.

## Risks / Trade-offs

- [La lectura múltiple puede leerse como selección por favorable] → se reportan los tres
  subconjuntos juntos, con la cifra primaria rotulada y la salvedad de multiplicidad (D4).
- [La brecha podría no ser robusta] → es un resultado admisible; se informa el rango y se declara
  sin sobreafirmar; el veredicto del umbral no depende de esta lectura.
- [Crecimiento de páginas] → párrafo/tabla compacta en subsecciones existentes; verificar
  `abspage@last` y compensar en el mismo bloque si hace falta.
- [Deriva de anclas] → el script aborta sin escribir; no regenera insumos (D3).

## Migration Plan

1. Escribir la prueba (TDD) de las funciones puras (derivación de subconjuntos, contraste por
   subconjunto, verificación de anclas) y verla fallar.
2. Implementar el mínimo para pasarla; triangular con casos sintéticos.
3. Correr el script sobre los artefactos reales y verificar las anclas y el determinismo.
4. Escribir la sección `3.36` del memo con las cifras producidas.
5. Llevar la prosa a `07` y `08` con las cifras del memo.
6. Registrar la trazabilidad en `dictamen-correcciones.md` y verificar (`openspec validate --strict`,
   `verify_citations.py`, compilación).
7. Rollback: `git revert` del commit del script, el memo, la trazabilidad y la prosa; no hay estado
   externo ni migración de datos.

## Open Questions

- **OQ1.** Si la brecha pierde significación en el subconjunto `original_150`, ¿la discusión la
  presenta como sensibilidad que acota la conclusión o como hallazgo que la matiza? Decisión del
  autor al aplicar; no cambia el script ni las specs. Se resuelve con la salida real del análisis.
- **OQ2.** Si el párrafo de `07-resultados.tex` conviene como tabla compacta o como prosa, según el
  impacto de páginas. Decisión al aplicar; no cambia las specs.
