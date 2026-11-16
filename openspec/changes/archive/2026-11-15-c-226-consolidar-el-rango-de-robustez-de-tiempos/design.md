# Design: Consolidar el rango de robustez de los tiempos

## Context

La limitación 4 (instrumentos asimétricos, orden fijo, llamadas recitadas) se acota hoy con
sensibilidades dispersas: los descuentos de `5 s` y `10 s` viven en `07-resultados.tex:63` y en
la Sección 3.8 del memo; el desagregado por canal en `tab:tiempos-canal` y en la Sección 3.8; los
tiempos por operador (`O1 33,8 %`, `O2 79,7 %`, agregado `69,3 %`) en la Sección 3.17 y el efecto de posición en la
Sección 3.14; la cota del instrumento (múltiplos de `5 s` `199/200` y de `10 s` `180/200`, y la
telefonía como cota inferior por la grabación acotada a `45 s`) en `04-marco-metodologico.tex:16`
y `:76`. Las seis explicaciones rivales de `08-discusion.tex:22-24` citan cifras aisladas.

**Insumos versionados (solo lectura):**

- `data/corpus_evaluacion_pseudonimizado.json`: `200` casos con `tiempo_manual_s`,
  `tiempo_automatizado_s` y `canal_origen`.
- `evaluation/stats.py`: `reduccion_relativa`, `escenario_sensibilidad`,
  `granularidad_manual`, `estadisticos_descriptivos`, `wilcoxon_tiempos_detallado`.
- `evaluation/data/campana/brazo_manual.csv` (duraciones manuales por `id_etiquetador`) cruzado
  con `evaluation/data/campana/corpus_campana.json` (`tiempo_automatizado_s` de la corrida
  propia): de ahí salen las reducciones por operador, como las derivó c-196 (Sección 3.17).
- `evaluation/data/campana/analisis/resultados.json`: efecto de posición (Spearman) de la
  campaña complementaria (Sección 3.14 del memo).
- Valores canónicos de referencia en `docs/Tesis/Correcciones/numeros-canonicos.md`
  (Secciones 3.8, 3.14 y 3.17) y en `07-resultados.tex:12-63`.

**Hecho del estado actual:** la cifra primaria `71,2 %` (media) y su IC `[67,2 %; 74,6 %]` no se
tocan. Ningún escenario nuevo se mide: todos ya fueron calculados y registrados.

## Goals / Non-Goals

**Goals:**

- Reunir en una sola tabla (o párrafo, según espacio) los escenarios ya calculados y declarar el
  rango completo, el escenario que minimiza el estimando primario y las cotas de alcance.
- Rotular cada escenario por su ámbito y por la dirección de la cota (superior o inferior), para
  que no se lean como un único estimando comparable.
- Remitir desde las seis explicaciones rivales y precisar la limitación y la amenaza 1.
- Dejar una fuente reproducible y anclada de cada cifra en una sección aditiva del memo.

**Non-Goals:**

- Medir de nuevo, reejecutar la campaña, invocar a Gemini o tocar el corpus/las predicciones.
- Cambiar `71,2 %`, su IC, el `p` de Wilcoxon, `r` o `d_z`.
- Reescribir los escenarios existentes de resultados y discusión.
- Resolver las limitaciones que exigen datos nuevos (muestra por conveniencia, remedición con
  instrumento único, llamadas con usuarios reales, contrabalanceo del orden).

## Decisions

### D1 — Definición de dos niveles: rango primario y cotas de alcance

El objeto de la consolidación es la **reducción de la media del tiempo de registro de la campaña
2026-10**. Sobre ese estimando, los escenarios ya calculados que se pueden comparar entre sí son los
descuentos de redondeo:

| Escenario | Media manual | Reducción de la media | Rol |
|---|---|---|---|
| Sin descuento | `61,585 s` | `71,16 %` (`71,2 %` en la tesis) | cifra primaria (cota superior) |
| Descuento `5 s` | `56,585 s` | `68,61 %` (`68,6 %`) | cota inferior conservadora |
| Descuento `10 s` | `51,585 s` | `65,57 %` (`65,6 %`) | **mínimo del estimando primario** |

**Rango del estimando primario:** `[65,57 %; 71,16 %]`. El escenario que lo minimiza es el
descuento de `10 s`, coherente con la resolución efectiva de la planilla (`180/200` valores son
múltiplos de `10 s`; `199/200` de `5 s`).

Las demás sensibilidades **no** son el mismo estimando y se informan como **cotas de alcance**,
cada una rotulada:
- **Por canal** (`76,98 / 51,07 / 93,44 %`): la menor es correo electrónico `51,07 %`; no se
  presenta como mínimo global, porque es una reducción intra-canal.
- **Por operador** (`O1 33,8 %`, `O2 79,7 %`, agregado `69,3 %`): proviene de la campaña
  complementaria (`brazo_manual.csv` cruzado con `corpus_campana.json`, Sección 3.17), cuyo brazo
  manual mide solo la decisión de sector y no es comparable con el brazo de `2026-10`. La lectura
  `33,8 %` es la más adversa entre escenarios rotulados, pero no el mínimo del estimando primario.
- **Efecto de posición**: significativo para uno de los dos operadores y acotado por su MDE; no
  produce una cifra de reducción, pero acota la estabilidad del orden.
- **Cota inferior del instrumento**: la telefonía automatizada es cota inferior de la duración
  real de la llamada (grabación acotada a `45 s`), de modo que su reducción medida (`77,0 %`) es
  cota superior de la reducción telefónica real.

La tabla final debe declarar las dos cosas: el rango `[65,57 %; 71,16 %]` con su mínimo, y las
cotas de alcance con su rótulo. Alternativa descartada: un único número «mínimo de todos los
escenarios» (`33,8 %`), porque mezcla estimandos y se leería como una reducción del estudio
principal.

### D2 — Un único script de consolidación, de solo lectura

Script `evaluation/data/campana/analisis/analisis_rango_robustez_tiempos_c226.py`, pruebas en
`test_analisis_rango_robustez_tiempos_c226.py`, salidas `analisis_rango_robustez_tiempos_c226.json`,
`.md` y `.SHA256SUMS.txt` en la misma carpeta (UTF-8 sin BOM, LF). Solo lectura, sin red, sin
Gemini, determinista.

Funciones puras (con prueba sintética antes de implementar):

| Función | Qué calcula | Reutiliza |
|---|---|---|
| `rango_descuentos(manual, automatizado, descuentos)` | Reducción por descuento y el mínimo | `stats.escenario_sensibilidad`, `stats.reduccion_relativa` |
| `resumen_por_canal(casos)` | Reducción intra-canal y canal mínimo | `stats.reduccion_relativa` |
| `resumen_por_operador(registros_manual, automatizado_por_caso)` | Reducciones `O1`, `O2` y agregada desde `brazo_manual.csv` × `corpus_campana.json` | lectura de los artefactos |
| `resumen_posicion(resultados)` | Coeficiente, `p` y MDE del efecto de posición | lectura del artefacto |
| `cota_instrumento(manual)` | Múltiplos de `5 s` y `10 s` y la nota de la telefonía | `stats.granularidad_manual` |

**Anclajes que abortan antes de escribir** (exit distinto de cero, sin salidas): `71,16 %`,
`68,61 %` y `65,57 %` de reducción global; `76,98 %`, `51,07 %` y `93,44 %` por canal;
`199/200` y `180/200` de granularidad; `33,8 %`, `79,7 %` y `69,3 %` por operador; y los valores
de efecto de posición de la Sección 3.14. Las series se leen del corpus y el bloque por operador de
`brazo_manual.csv` y `corpus_campana.json`, no de constantes.

Salidas del JSON: rango primario con mínimo y escenario; tabla por canal; tabla por operador;
efecto de posición; cota del instrumento; SHA-256 de las entradas; y una nota de no comparabilidad
entre estimandos. Alternativa descartada: escribir la tabla solo desde el memo, porque no dejaría
comando reproducible ni anclaje automático (la práctica del proyecto desde c-207).

### D3 — Ubicación y forma en la tesis

- `07-resultados.tex`: dentro de `subsec:comparacion-tiempos` (no se agrega subsección, por lo que
  la enumeración de «doce apartados» de `:6` no cambia), después del párrafo de sensibilidad de
  `:63`, una tabla `tab:rango-robustez-tiempos` con las filas de D1 y una nota que declare: rango
  primario, mínimo, rótulo de sensibilidad y no comparabilidad de las cotas de alcance. Si la
  paginación lo impide, un párrafo equivalente de una a dos oraciones con el rango y el mínimo,
  más remisión a la sección del memo.
- `08-discusion.tex:22-24`: en el cierre de las seis explicaciones rivales se agrega una remisión
  a la tabla y la frase que declara el rango `[65,6 %; 71,2 %]` y su mínimo `65,6 %`, más la
  lectura adversa de operador y de canal con su rótulo. No se retiran las cifras existentes.
- `08-discusion.tex` (subsección de limitaciones): se precisa la limitación de tiempos con el
  alcance del rango y la nota de que ninguna sensibilidad elimina la asimetría de instrumentos ni
  el orden fijo.
- `04-marco-metodologico.tex:106` (amenaza 1): se agrega una oración que remite a la síntesis y
  declara que el rango acota la magnitud pero no estima el efecto de orden.

Alternativa descartada: una subsección nueva en resultados, porque infla la estructura y obliga a
renumerar la enumeración y las remisiones.

### D4 — Sección aditiva del memo

Se agrega la Sección `3.N` (primer número libre al aplicar; hoy la última es `3.36`, esperado
`3.37`) con: el rango primario y el mínimo; la tabla por canal; la tabla por operador; el efecto de
posición; la cota del instrumento; la procedencia de cada valor (corpus, `brazo_manual.csv`,
`corpus_campana.json`, `resultados.json`, clave y comando); y el estado (`vigente` para los valores ya canónicos reutilizados; `sensibilidad` /
`reinterpretación` para la síntesis). Declara de forma explícita que no mide de nuevo y que no
modifica las Secciones 3.1 a 3.36.

### D5 — Orden de las tareas

1. Línea de base y verificación de estado (incluye fijar el número libre del memo).
2. Script TDD, salidas y SHA-256 con anclajes.
3. Sección aditiva del memo.
4. Recién entonces la prosa: tabla y remisiones.
5. Trazabilidad en `dictamen-correcciones.md`.
6. Compilación y verificaciones; cierre.

Cada tarea de prosa cita la clave del memo de la que toma la cifra.

### D6 — Gobernanza y frontera

- Script, memo y prosa de resultados/discusión/método: **MEDIUM**, con checkpoint de los autores
  sobre D1 antes de editar la tabla (la lectura de «mínimo» es una decisión editorial).
- No hay bloque HIGH: no se toca el capítulo legal, no se crea tag ni se publica nada.
- Sin cambios en `App/`, `n8n/`, el clasificador, la configuración, el corpus ni las predicciones.
- Cero llamadas pagas.

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| La tabla se lee como medición nueva | Rótulo «sensibilidad» en el encabezado, la nota y la prosa; la cifra primaria sigue siendo `71,2 %` |
| Un único mínimo (`33,8 %`) se lee como reducción del estudio | D1 separa estimando primario y cotas de alcance; la nota de no comparabilidad es obligatoria |
| Duplicar cifras y romper la repetición acotada | La tabla es la síntesis; resultados y discusión conservan sus cifras con remisión |
| Crecer en páginas | Tabla compacta o párrafo; verificar `\@abspage@last` y compensar dentro del mismo bloque |
| Colisión de numeración del memo | Fijar el primer número libre al aplicar (tarea 0.5) |
| Deriva del corpus, de `brazo_manual.csv` o de `resultados.json` | Los anclajes abortan sin escribir; SHA-256 de las entradas en el JSON |

## Migration Plan

1. Preparación y línea de base (tareas 0).
2. Script TDD y salidas (tareas 1).
3. Sección del memo (tareas 2).
4. Prosa en el orden de D5 (tareas 3 y 4), con checkpoint de los autores antes de la 3.
5. Compilación y verificaciones (tareas 5).

## Open Questions

- **OQ1 (autores, bloquea 3.1)**: confirmar la lectura de D1: el «escenario que minimiza» es el
  descuento de `10 s` (`65,6 %`) para el estimando primario, y las lecturas de operador (`33,8 %`)
  y de canal (`51,1 %`) se informan como cotas de alcance, no como mínimos.
- **OQ2 (autores, opcional)**: si la paginación impide la tabla, ¿se acepta el párrafo compacto con
  remisión a la sección del memo?