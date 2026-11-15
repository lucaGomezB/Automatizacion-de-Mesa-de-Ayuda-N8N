## Context

Ver `proposal.md` — Why. El change parte de los artefactos ya versionados por la campaña
complementaria y no requiere datos nuevos ni llamadas pagas:

- `evaluation/data/campana/doble_etiquetado_arbitrado.csv` (`476` filas): etiquetas de `E3`, `E4`
  y `E5` por caso, con marcas de tiempo.
- `evaluation/data/campana/arbitraje_tres_vias.json` (`206` casos): `origen` por caso
  (`consenso_e3_e4` o `arbitraje_e5`) y bandera `tres_vias`.
- `evaluation/data/campana/predicciones_arbitrado.json`: predicción congelada de `hybrid-v3`
  sobre los `206`, necesaria para calcular el efecto de reasignar los `6` casos.
- `evaluation/data/campana/corpus_independiente_arbitrado.json`: referencia vigente de los `206`.
- Funciones puras reutilizables: `evaluation/metrics.py` (`matriz_confusion`,
  `precision_por_clase`, `sensibilidad_por_clase`, `f1_por_clase`, `f1_macro`,
  `intervalo_wilson`).

Al redactar este diseño el memo canónico terminaba en la sección `3.33` (c-222); al aplicar, la
sección nueva de este change quedó en la `3.35`, porque c-223 tomó la `3.34` (primer número libre
al aplicar).

## Goals / Non-Goals

**Goals:**

- Producir, con un único script versionado y probado, la coincidencia entre la regla vigente y
  la mayoría de `{E3, E4, E5}` (`200/206`), la lista de los `6` casos sin mayoría y el rango de
  exactitud y métricas por clase (`142/206` a `147/206`).
- Registrar esas cifras en una sección aditiva del memo canónico y llevarlas a la tesis solo
  después.
- Corregir la limitación 8 y reformular el trabajo futuro de `10-recomendaciones.tex` sin
  cambiar la cifra primaria ni el veredicto del umbral.

**Non-Goals:**

- Reabrir mediciones, reclasificar, reentrenar, invocar a Gemini o ejecutar una corrida paga.
- Cambiar `0,6893` (`142/206`), `0,7024`, el umbral de `0,85` o cualquier valor vigente del memo.
- Elegir una etiqueta "verdadera" para los `6` casos sin mayoría: se informa el rango.
- Modificar `App/`, `n8n/`, el clasificador, el corpus, las predicciones o los artefactos
  congelados.
- Resolver la fragilidad de la referencia: solo se acota su efecto y se corrige su descripción.

## Decisions

### D1 — Un único script de análisis nuevo, de solo lectura

Script `evaluation/data/campana/analisis/analisis_arbitraje_mayoria_c224.py`, pruebas en
`test_analisis_arbitraje_mayoria_c224.py`, salidas `analisis_arbitraje_mayoria_c224.json`,
`.md` y `.SHA256SUMS.txt` en la misma carpeta (UTF-8 sin BOM, LF). Solo lectura, sin red, sin
Gemini, determinista; imprime el SHA-256 de entradas y salidas. El docstring fija el método y
los anclajes antes de escribir código.

Funciones puras (cada una con pruebas sintéticas antes de implementarla):

| Función | Qué calcula |
|---|---|
| `cargar_etiquetas(ruta)` | `dict` caso → etiquetas de `E3`, `E4`, `E5` (o `None`) |
| `cargar_origen(ruta)` | `dict` caso → `origen` y `tres_vias` |
| `cargar_predicciones(ruta)` | `dict` caso → sector predicho por el clasificador congelado |
| `regla_vigente(etiquetas, origen)` | Etiqueta de consenso `E3`/`E4` o la de `E5` si difieren |
| `mayoria(etiquetas)` | Etiqueta que aparece al menos dos veces, o `None` |
| `acuerdo_con_mayoria(casos)` | Cuenta y lista de casos donde la regla vigente coincide con la mayoría |
| `casos_sin_mayoria(casos)` | Lista de los `6` casos con tres etiquetas distintas |
| `rango_exactitud(referencia, predicciones, seis)` | Aciertos mínimos y máximos al reasignar los `6` |
| `metricas_por_clase_bajo_extremos(referencia, predicciones, seis)` | Matriz `5×5` y métricas por clase en ambos extremos |

**Anclajes que abortan antes de escribir** (exit distinto de cero, sin salidas): `200` casos
con acuerdo, `6` casos sin mayoría (`I033`, `I042`, `I056`, `I130`, `I194`, `I198`), `64`
arbitrados, `142/206` de exactitud estricta y macro-F1 `0,7024` sobre la referencia vigente, y
el rango `142/206`–`147/206`. Los conjuntos se derivan de los archivos, no de constantes.

Alternativas descartadas: ampliar `analisis_propagacion_arbitraje_c221.py` (cambiaría un
artefacto con SHA-256 registrado y su contrato) o `analisis_ruido_referencia_c216.py` (mide otra
cosa: ruido de referencia, no la coincidencia con la mayoría).

### D2 — La coincidencia `200/206` es estructural; no se presenta como medición nueva

El hallazgo central es una identidad algebraica, no una medición independiente:

- En los `142` casos de consenso `E3 = E4`, la regla vigente usa esa etiqueta y la mayoría de
  `{E3, E4}` es la misma: coinciden por construcción.
- En los `64` casos arbitrados, `E5` fija la referencia. Si la etiqueta de `E5` coincide con la
  de `E3` o con la de `E4`, hay mayoría y la regla vigente ya es esa mayoría (coinciden). Si
  `E5` es distinta de ambas, hay tres etiquetas distintas y **no hay mayoría**: son los `6`
  casos.

Por eso `200 = 142 + 58` coinciden y los `6` restantes carecen de mayoría. El script lo
verifica desde los archivos y el JSON lo declara; la prosa lo rotula como **precisión
estructural**, no como una medición nueva. Alternativa descartada: presentarlo como un
"descubrimiento empírico", porque sobrestima lo que el análisis agrega.

### D3 — Rango de exactitud y métricas por clase bajo dos extremos

La exactitud vigente es `142/206`. Para cada uno de los `6` casos sin mayoría, el script lee la
predicción del clasificador y comprueba si esa predicción está entre las tres etiquetas
posibles. Si lo está, el caso puede reasignarse a una etiqueta que acierta; si no, no puede
convertirse en acierto con ninguna asignación. El máximo es `142 + k`, con `k` los casos donde
la predicción está en el conjunto; el mínimo es `142` (los `6` siguen como errores). El anclaje
exige `k = 5`, de modo que el rango es `142/206` (`0,6893`) a `147/206` (`0,7136`).

Las métricas por clase se calculan en los dos extremos: (a) referencia vigente (los `6` con la
etiqueta de `E5`), y (b) cada caso reasignado a la etiqueta que coincide con la predicción
cuando existe, o a `E5` si no. El JSON guarda ambas matrices y ambos vectores de precisión,
sensibilidad y F1, con el soporte. El rango se rotula como **cota de sensibilidad**, no como
exactitud corregida, y no reemplaza la cifra primaria.

### D4 — Prosa: tres pasajes y un criterio de no regresión

| Pasaje | Cambio mínimo | Verificación |
|---|---|---|
| `08-discusion.tex` (limitación 8, párrafo «Octavo») | Agregar que la regla vigente coincide con la mayoría de `{E3, E4, E5}` en `200` de `206` casos y que los `6` restantes acotan la exactitud estricta entre `0,6893` y `0,7136`; conservar la fragilidad de la referencia como limitación de fondo | `rg -n "200 de 206" 08-discusion.tex` devuelve la línea |
| `07-resultados.tex` (párrafo del arbitraje) | Agregar una oración con el rango `142/206`–`147/206`, rotulado como sensibilidad, y remitir a la sección `3.35` del memo; no cambiar las cifras vigentes del párrafo | `rg -n "147/206" 07-resultados.tex` devuelve la línea y el resto del párrafo conserva `0,6893`, `0,7864`, `0,7489`, `0,7467`, `31/61` |
| `10-recomendaciones.tex` (`subsec:corpus-independiente`) | Sustituir «con arbitraje por mayoría de tres etiquetadores, en lugar de la regla actual en que decide un único tercer etiquetador» por «con más etiquetadores independientes que permitan estimar la mayoría sin depender de un único tercer etiquetador» | `rg -n "más etiquetadores independientes" 10-recomendaciones.tex` devuelve la línea; `rg "mayoría de tres"` no devuelve coincidencias en ese archivo |

Criterio único: ninguna cifra vigente (`0,6893`, `0,7024`, `0,85`, `64`, `206`) cambia de valor;
los `6` casos y el rango son adiciones rotuladas como sensibilidad. No se introducen
identificadores internos `c-NNN` en el cuerpo.

### D5 — Memo canónico: sección `3.35` aditiva

Se agrega `### 3.35 Acotación del arbitraje por mayoría (c-224)` al final de la Sección 3, con
el primer número libre al aplicar, y con una tabla de valores aditivos: `200/206` de
coincidencia; `6` casos sin mayoría con sus identificadores y sus tres etiquetas; el rango
`142/206`–`147/206`; y las métricas por clase en ambos extremos. Cada valor con archivo fuente
(`analisis_arbitraje_mayoria_c224.json`, ruta JSON) y el comando que lo produce. La sección
declara que es aditiva y que no modifica ni reemplaza ningún valor ni estado de las secciones
3.1 a 3.33. Se agrega la remisión desde la sección `3.30` (c-219) o `3.27` (c-216) si el cambio
de descripción lo requiere, sin reescribir su contenido.

### D6 — Trazabilidad y gobernanza

Se agrega a `docs/Tesis/Correcciones/dictamen-correcciones.md` la sección «c-224: acotación del
arbitraje por mayoría» con las filas `C24/a` a `C24/w`: script y pruebas, salidas JSON/MD/SHA,
sección `3.35` del memo, los tres pasajes de prosa y el estado de la limitación 1. Gobernanza
**MEDIUM**: sin tag, sin push y sin tocar artefactos congelados. El apply verifica con `git diff`
que ningún corpus, predicción o artefacto congelado cambió.

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| El `200/206` se lee como una medición nueva | D2: se declara identidad estructural (`142 + 58`); el JSON y la prosa lo rotulan como precisión, no como descubrimiento |
| El rango `142`–`147` se lee como exactitud corregida | D3: rótulo de cota de sensibilidad; la cifra primaria sigue siendo `142/206` |
| La prosa de `10` promete una medición no hecha | D4: se propone más etiquetadores (datos nuevos), no una medición ejecutada |
| Colisión de numeración del memo con c-225/c-226 | D5: primer número libre al aplicar; coordinación registrada en la tarea 0.4 |
| El script altera artefactos congelados | D1/D6: solo lectura y `git diff` al cierre; nombres fijos de salida |

## Migration Plan

1. Preparación y línea de base (tareas 0).
2. Script TDD y salidas (tareas 1).
3. Memo, sección `3.35` (tarea 2).
4. Prosa (tarea 3).
5. Trazabilidad y cierre (tarea 4).

**Rollback**: `git revert` de los `.tex`, del script, de sus salidas y de la sección `3.35`;
la sección de c-224 de `dictamen-correcciones.md` se retira en la misma reversión. Nada toca
artefactos congelados.

## Open Questions

Ninguna. Los `6` casos, sus etiquetas y las predicciones están versionados; el número de la
sección del memo es el único dato que depende del estado de `main` al aplicar y se fija en la
tarea 0.4.