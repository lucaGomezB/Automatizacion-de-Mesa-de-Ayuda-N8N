## Context

El dictamen CONEAU posterior a `v1.3.0` evaluó `5734ea8` y formuló 17 recomendaciones (7
necesarias, 6 de consistencia, 4 de forma) más observaciones por sección (ver `proposal.md`).
Después de `5734ea8` entraron c-216 (`subsec:ruido-referencia`, reencuadre de la revisión humana,
equivalencia de la configuración entregada) y c-217 (`tab:gemini-solo`, contraste de la hipótesis
de eficiencia). Este design parte de `ebd2baa`, donde se volvió a verificar cada hallazgo.

**Insumos versionados (solo lectura):**

- `evaluation/data/campana/corpus_independiente_arbitrado.json`: `206` casos (`I001`..`I150`
  originales, `I151`..`I206` de refuerzo), con `canal_origen` y `sector_asignado`.
- `evaluation/data/campana/predicciones_arbitrado.json`: `hybrid-v3` congelado sobre los `206`
  (`commit` `1b62fdb`, alcanzable desde `origin/main`: `git merge-base --is-ancestor` devuelve `0`).
- `evaluation/data/campana/predicciones_independiente.json`: primera corrida sobre los `103` con
  consenso (`commit` registrado `561b3c4`, **no alcanzable desde `main`** ni desde ninguna rama
  publicada; el archivo lo versionó `1b17e55` según `git log --diff-filter=A`). En el clon donde
  se hizo la corrida el objeto existe como commit colgante (`git cat-file -t` devuelve `commit`);
  en otro clon `git cat-file -t` falla, porque un objeto colgante no viaja con `fetch` ni con
  `clone`. Por eso la presencia local del objeto no prueba pertenencia al historial y el control
  se hace por alcanzabilidad (D2). El dictamen corrigió la misma premisa en `c6b0cf9`.
- `evaluation/data/campana/arbitraje_tres_vias.json`: `origen` por caso (`consenso_e3_e4` o
  `arbitraje_e5`) y bandera `tres_vias` (`64` arbitrados, `6` de tres vías: `I033`, `I042`,
  `I056`, `I130`, `I194`, `I198`).
- `evaluation/data/campana/doble_etiquetado_arbitrado.csv`: marcas de tiempo de `E3`, `E4` y `E5`.
- Funciones puras reutilizables: `evaluation/metrics.py` (`matriz_confusion`,
  `precision_por_clase`, `sensibilidad_por_clase`, `f1_por_clase`, `f1_macro`,
  `intervalo_wilson`, `remuestreos_indices`, `percentil_intervalo`), `evaluation/stats.py`
  (`contraste_mcnemar`, si hace falta) y `evaluation/calibracion_gate.py` (`ece`, `brier`, `auroc`,
  `sobreconfianza`, `ic_bootstrap_metrica`, `barrido_umbral`).

**Recomputo exploratorio de este design (no es evidencia; el apply debe reproducirlo con el
script versionado):** `142/206`; consenso `109/142`; arbitrados por `E5` `33/64`; discordantes
originales `25/47`; refuerzo `30/56`; originales sin exclusión `112/150`; etapa determinística
`88/115`; etapa Gemini `54/91`; composición `Sistemas 61`, `Hardware 51`, `Software 46`,
`Seguridad 32`, `Bases de Datos 16`; refuerzo con `40` casos de `Sistemas`; errores de `Sistemas`:
`16` a `Soporte Tecnico Software`, `8` a `Seguridad Informatica`, `3` a `Soporte Tecnico Hardware`,
`3` a `Bases de Datos`; exactitud ponderada por la composición del corpus de 200 `0,7489`
(bootstrap percentil por caso, `2000` remuestreos, semilla `20261021`, aproximadamente
`[0,682; 0,810]`); etapa Gemini sobre los `91`: exactitud `0,5934` y confianza media `0,9055`;
confianza de Gemini distinta entre corridas en `7` de los `34` casos comunes (`I026`, `I043`,
`I050`, `I055`, `I067`, `I084`, `I085`). Las cifras del dictamen sobre ECE, Brier, AUROC, barrido
de umbrales y balance neto no se recomputaron aquí y quedan para el script.

**Hallazgos verificados en `ebd2baa`** (archivo:línea): `08-discusion.tex:8`, `:20`, `:28`, `:60`
sin `0,6893` y con el razonamiento de escenarios; `09-conclusiones.tex:24`, `:37` (con «change
c-206» y `F1 0,2222`), `:47`; `10-recomendaciones.tex:18`, `:26`; `00-resumen.tex` sin
validación fuera de muestra (`248` y `247` palabras); `00-portada.tex:30-31`; `12-anexos.tex:58`
(afirmación falsa sobre commits posteriores; `25` commits tocan `sections/` entre `v1.3.0` y
`origin/main`), `:151` (identificador `c-201`), `:245` (Anexo J); `07-resultados.tex:6` («siete
apartados»), `:195-221` (calibración solo sobre `34`), `:312-347` (validación anidada en la
campaña complementaria; «change c-206» en `:316`, `:328`, `:347`); `04-marco-metodologico.tex:93`
(«seis amenazas»), sin apartado del diseño fuera de muestra; `05-arquitectura.tex:68`;
`01-introduccion.tex:74`; `02-marco-teorico.tex:32`; `03-estado-del-arte.tex:51` (Colavito sin
salvedad); `Bibliography_base.bib` (`Gomez2026_repositorio` con «Versión 1.3.0»; cinco claves con
año distinto); `analisis_calibracion_gate_c214.json` con `corpus_arbitrado_c206: no ejecutado`.

## Goals / Non-Goals

**Goals:**

- Que todo el documento razone con el resultado arbitrado y que la estimación sobre `103` quede
  como etapa previa, con una sola aparición de `0,8447` fuera de resultados (criterio en D6).
- Producir, con un único script versionado y probado, todas las cifras nuevas que pide el
  dictamen, registrarlas en el memo canónico y solo entonces llevarlas a la tesis.
- Dar al diseño fuera de muestra su apartado metodológico y sus amenazas, sin inventar datos.
- Que la versión entregada declarada exista y contenga el texto y la evidencia vigentes.

**Non-Goals:**

- Reabrir mediciones, reclasificar, invocar a Gemini, re-elegir el umbral del gate o cambiar un
  valor vigente del memo.
- Evaluar o reescribir `subsec:ruido-referencia` (c-216) o el contraste de c-217.
- Resolver las limitaciones estructurales ya declaradas (muestra por conveniencia, ajuste sobre el
  corpus de evaluación, instrumentos distintos, orden fijo, llamadas recitadas).

## Decisions

### D1 — Cifra fuera de muestra primaria y rótulo de las tres lecturas

La **cifra primaria** es la exactitud estricta cruda sobre la referencia arbitrada, `142/206`
(`0,6893`, Wilson `[0,6231; 0,7486]`), la que ya informa `tab:fuera-de-muestra` y el memo 3.25.
Es la más desfavorable de las tres y es una medición sin exclusión. Se agregan dos lecturas
**complementarias**, rotuladas así en la tabla y en la prosa:

1. **Ponderada por la composición del corpus de 200** (post-estratificación: sensibilidad de cada
   clase sobre los `206` ponderada por la composición del corpus de ajuste: `Sistemas` 16,
   `Soporte Tecnico Hardware` 85, `Soporte Tecnico Software` 67, `Seguridad Informatica` 31 y
   `Bases de Datos` 1, suma 200; el script la lee de `sector_asignado` en
   `data/corpus_evaluacion_pseudonimizado.json`, como c-191, y usa ese vector como anclaje), con
   intervalo bootstrap
   percentil por caso (`2000` remuestreos, semilla `20261021`). No es una elección posterior a los
   datos: la ponderación estaba prevista desde el diseño de c-191 (`runbook-corpus-independiente.md`,
   «Estratos de la campaña de 150»: ponderación por la composición del corpus de 200 y reporte de
   ambas), el design de c-206 la exigía para el refuerzo («se informa con y sin ponderación»,
   riesgo «El refuerzo desbalancea el global»), y la tesis ya la informa para la etapa con exclusión
   (`0,8146`) y para la línea de base (`07-resultados.tex:350`).
2. **Sobre los 150 casos del diseño original, sin exclusión** (`I001`..`I150` con referencia
   arbitrada), con intervalo de Wilson. Responde al diseño prefijado de `150` casos y aísla el
   efecto del refuerzo.

Regla de lectura: el veredicto sobre el umbral de `0,85` se lee con las tres; se declara refutado
fuera de muestra solo si los límites superiores de las tres quedan por debajo de `0,85` (el script
lo calcula y el texto no lo anticipa). Ninguna lectura reemplaza a la primaria ni al valor vigente.
La comparación con la exactitud dentro de la muestra (`0,7350`) se hace con las lecturas
complementarias y se rotula como comparación de órdenes de magnitud, no como contraste.

Alternativas descartadas: (a) ponderada como primaria, porque parecería elegida por favorable y
no es la medición; (b) informar solo la cruda, porque el dictamen la declara no comparable y el
diseño previo ya prometía la ponderada; (c) re-ponderar por la mezcla operativa por canal, porque
la composición por sector es la que el refuerzo alteró.

### D2 — Un único script de análisis nuevo

Script `evaluation/data/campana/analisis/analisis_propagacion_arbitraje_c221.py`, pruebas en
`test_analisis_propagacion_arbitraje_c221.py`, salidas `analisis_propagacion_arbitraje_c221.json`,
`.md` y `.SHA256SUMS.txt` en la misma carpeta (UTF-8 sin BOM, LF). Solo lectura, sin red, sin
Gemini, determinista; imprime los SHA-256 de entradas y salidas y registra los de entrada con la
misma normalización LF que c-213, c-207 y c-214 (commit `64a14b5`).

Funciones puras (cada una con pruebas sintéticas antes de implementarla):

| Función | Qué calcula | Reutiliza |
|---|---|---|
| `exactitud_ponderada(reales, predichos, pesos)` | Suma de `peso_c × sensibilidad_c`; error si una clase con peso no tiene soporte | `metrics.matriz_confusion`, `sensibilidad_por_clase` |
| `ic_bootstrap_ponderada(reales, predichos, pesos, b, semilla)` | Percentil por caso; descarta y cuenta las réplicas sin alguna clase | `metrics.remuestreos_indices`, `percentil_intervalo` |
| `desglose(casos, clave)` | Aciertos, n, exactitud y Wilson por grupo (origen, etapa, bloque original o refuerzo, canal) | `metrics.intervalo_wilson` |
| `metricas_por_clase(reales, predichos)` | Matriz `5×5`, precisión, sensibilidad, F1 y soporte | `metrics.*` |
| `destinos_de_error(reales, predichos, clase)` | Conteo de sectores predichos en los errores de una clase | — |
| `calibracion_descriptiva(confianzas, aciertos, umbrales)` | Exactitud, confianza media, sobreconfianza, ECE (10 bandas), Brier, AUROC con IC y barrido de umbrales, **sin** seleccionar umbral | `calibracion_gate.ece`, `brier`, `auroc`, `sobreconfianza`, `ic_bootstrap_metrica`, `barrido_umbral` |
| `balance_neto(n, delta_t, e_aut, e_man, costo_s)` | `B = (N/3600)·[Δt − (e_aut − e_man)·c]` en horas-persona | — |
| `diferencias_entre_corridas(pred_a, pred_b)` | Casos comunes con sector, etapa o confianza distintos | — |

**Anclajes que abortan antes de escribir** (exit distinto de cero, sin salidas): `142/206` y
macro-F1 `0,7024` sobre el arbitrado; `87/103` y la ponderada `0,8146` sobre los `103` de
`predicciones_independiente.json` (valida `exactitud_ponderada` contra un valor vigente); ECE
`0,1715` y Brier `0,1935` sobre los `34` casos Gemini con consenso (valida la reutilización de
`calibracion_gate`); celda `+6,9` de `tab:balance-neto` (15 %, 5 minutos, `e_aut = 53/200`) y
`+25,4/+18,7/+11,9` con la referencia común (valida `balance_neto`); `64` arbitrados, `47`
discordantes originales, `56` de refuerzo, `6` de tres vías y los `103` incluidos en
`I001`..`I150`; el vector de pesos `Sistemas` 16, `Soporte Tecnico Hardware` 85, `Soporte
Tecnico Software` 67, `Seguridad Informatica` 31, `Bases de Datos` 1 leído del corpus de ajuste;
y, si `analisis_sesgo_corpus_referencia_c219.json` está presente, los aciertos y el n por origen
de la referencia de c-219 (`109/142` y `33/64` en la rama del PR 110). Los conjuntos se derivan de
los archivos, no de constantes: el refuerzo es
`I151`..`I206` según la sección 14 de `runbook-arbitraje-discordantes.md`, y el script verifica
que esos `56` casos no están en `predicciones_independiente.json`.

**Desglose por origen y c-219.** El script conserva el cálculo por origen de la referencia porque
lo necesita como anclaje y como base de las lecturas que c-219 no cubre (`47` discordantes
originales, `56` de refuerzo, por etapa y por canal). La cifra consenso frente a arbitrado no es
una cifra nueva de c-221: si el artefacto de c-219 está presente, el script la verifica contra él
y aborta si difiere, y el memo y la tesis la citan desde la sección de c-219; solo si c-219 no
entró a `main` al aplicar, la sección de c-221 la registra con nota de conciliación (OOS-021).

**Control del `commit` declarado.** Para cada archivo de predicciones el script ejecuta
`git merge-base --is-ancestor <commit> origin/main`: `0` es alcanzable; `1` no lo es; cualquier
otro código (por ejemplo `128`, objeto ausente del clon) se registra también como no alcanzable y
la consola informa que el objeto no está en este clon. Si no es alcanzable, registra el commit
que versionó el archivo con `git log --diff-filter=A --format=%h -- <archivo>`. El JSON guarda
solo la alcanzabilidad y ese commit, para que las salidas no dependan del clon (OOS-023).

Salidas del JSON: tres lecturas; desglose por origen, por bloque, por etapa y por canal; matriz y
métricas por clase; destinos de error de `Sistemas` (total y por bloque); calibración descriptiva
de los `91` casos y, como contraste, de los `34`; balance neto con `e_aut` ponderada (`1 − lectura
ponderada`) y cruda (`64/206`), `e_man = 26/151`, `N = 2.646`, `Δt = 43,82` s y `c` de 5, 10 y 15
minutos (rejilla propia, que no espera a c-220: si al aplicar c-220 ya fijó en el memo un costo
con procedencia, se agrega como escenario adicional o se usa como central con la rejilla como
sensibilidad; si no lo fijó, por ejemplo en su rama B, se corre solo con la rejilla); diferencias entre corridas; cuotas observadas por canal y por sector de los `150` y de los
`56`; ventana de etiquetado del refuerzo desde `doble_etiquetado_arbitrado.csv`.

Alternativas descartadas: ampliar `analisis_calibracion_gate_c214.py` (cambiaría un artefacto con
SHA-256 registrado y su prerregistro) o `reporte_arbitrado.py` (otro contrato y otro consumidor);
varios scripts chicos (más superficie de registro sin beneficio).

### D3 — Calibración fuera de muestra sobre el corpus arbitrado

Se agrega a `tab:calibracion-gate` una tercera fila, «Fuera de la muestra, referencia arbitrada
(descriptiva)», con los `91` casos de la etapa Gemini. La fila de `34` se conserva. La nota de la
tabla dice que la regla prerregistrada de c-214 elige el umbral solo con los `200` casos de ajuste,
que la fila nueva es descriptiva y que no cambia el resultado de la selección. El barrido sobre los
`91`, con los mismos candidatos de la regla prerregistrada de c-214 (`0,70` vigente, `0,86`,
`0,91`, `0,96`, `0,99` y derivar todo lo escalado), se informa en prosa como descripción. Se agrega la
declaración de inestabilidad: entre las dos corridas sobre los `103` casos comunes, el sector y la
etapa coinciden y la confianza de Gemini difiere en `7` de `34`. Alternativa descartada: reemplazar
la fila de `34`, porque es la del prerregistro.

### D4 — Reestructuración de `07-resultados.tex` sin romper etiquetas

- Después de `subsec:resultados-campana-medicion` y antes de `subsec:ruido-referencia` se crean:
  - `\subsection{Validación fuera de muestra}\label{subsec:validacion-fuera-muestra}`: recibe el
    párrafo de la etapa con exclusión (hoy `:312`), el de fiabilidad `E3`/`E4` (`:314`), el del
    arbitraje (`:316`, reescrito), `tab:fuera-de-muestra` (con las filas de las lecturas
    complementarias), la tabla nueva `tab:fuera-de-muestra-clases` (matriz `5×5` del arbitrado con
    precisión, sensibilidad, F1 y soporte; los datos coinciden con
    `evaluation/data/campana/reporte_arbitrado.md`) y el desglose por origen y por etapa.
  - `\subsection{Comparación con esquemas alternativos}\label{subsec:comparacion-alternativas}`:
    recibe sin cambios de cifras los párrafos de la línea de base (`:350`, `:372`) y del modelo de
    lenguaje solo (`:374`-`:396`) con `tab:linea-base-clasica` y `tab:gemini-solo`.
- Las etiquetas existentes no cambian de nombre. Las remisiones a
  `subsec:resultados-campana-medicion` que hablan de la validación fuera de muestra
  (`08-discusion.tex:20`, `:28`, `:60`; `10-recomendaciones.tex:26`) pasan a
  `subsec:validacion-fuera-muestra`; las que hablan del brazo manual o del doble etiquetado
  `E1`/`E2` se conservan. Como el requisito vigente «Reporte de la validacion fuera de muestra» de
  `tesis-document` ubica ese reporte en `subsec:resultados-campana-medicion`, el delta lo modifica
  para ubicarlo en `subsec:validacion-fuera-muestra`, con sus dos escenarios.
- La frase de `07-resultados.tex:6` enumera los nueve apartados resultantes.
- Se corrige en el párrafo del arbitraje el rótulo de `Sistemas`: `0,5082` es su sensibilidad
  (`31/61`), no una «exactitud estricta».
- Verificación: `\paragraph` de la validación y de la línea de base fuera de
  `subsec:resultados-campana-medicion`; cero referencias indefinidas; cero etiquetas duplicadas.

Alternativa descartada: una sola subsección para validación y comparaciones, porque el dictamen
pide que la validación tenga entidad propia y la línea de base usa además el corpus de ajuste.

### D5 — Apartado metodológico del diseño fuera de muestra y amenazas

En `subsec:poblacion-muestra-corpus` se agrega `\paragraph{Corpus independiente de validación.}`
con: procedencia y período de los `150` casos (**pendiente de los autores, OQ1**; sin ese dato la
tarea queda bloqueada y no se escribe nada en su lugar); cuotas `50` correo / `40` web / `60`
telefonía con sobremuestreo de `Bases de Datos` (objetivo ≥ `10`), tomadas de
`runbook-corpus-independiente.md`, y la composición observada que calcula el script; el doble
etiquetado ciego de `E3` y `E4`; el refuerzo de `56` casos (`I151`..`I206`) reunido y etiquetado el
13-11-2026 (ventana de `E3`/`E4` tomada del CSV por el script), después de conocer el desempeño en
`Sistemas` y sin cuota fijada de antemano (`runbook-arbitraje-discordantes.md`, 1.2 y sección
14), con `40` casos de esa clase; la regla de arbitraje (si `E3` y `E4` difieren decide `E5`; no es
mayoría); que `E5` fija `64` de las `206` referencias; y los `6` casos de tres vías, con remisión a
`subsec:ruido-referencia`. En `subsec:analisis-estadistico` se agrega una oración por cada lectura
de D1 y por la calibración descriptiva de D3, y la nota de que el orden del prerregistro de c-214
se demuestra con las fechas de autor de los commits (las de commit quedaron igualadas por un
rebase).

En `subsec:amenazas-validez` se agregan dos amenazas y se actualiza el conteo: (séptima) selección
del refuerzo posterior a los datos y composición alterada (con su dirección: perjudica al
clasificador; mitigación: lecturas ponderada y de `150`); (octava) dependencia de un único árbitro
en `64` de `206` referencias con regla no mayoritaria, más la inestabilidad de la confianza entre
corridas. Alternativa descartada: una subsección metodológica nueva, por paginación.

### D6 — Pasajes que se reescriben y contenido mínimo

| Pasaje | Contenido mínimo nuevo | Retira |
|---|---|---|
| `08-discusion.tex:8` | Cifra primaria `0,6893/206`, lecturas complementarias, límites superiores frente a `0,85`, remisión a `subsec:validacion-fuera-muestra` | La oración sobre `0,8447` como cifra de lectura |
| `08-discusion.tex:20` | El arbitraje reemplazó los escenarios: `25` de `47` aciertos, `112/150` sin exclusión; el ajuste sobre el mismo corpus sigue como limitación | «sin el arbitraje de los 47», «41 de los 47», peor/mejor caso como argumento |
| `08-discusion.tex:28` | `Sistemas` con `61` casos: F1, sensibilidad `31/61`, destinos de error (`16`, `8`, `3`, `3`), `40` del refuerzo; lectura de taxonomía con ese material | `F1 0,2222`, «no puede estimarse», «dirigido a una única clase adyacente» (con `61` casos el error se reparte en más de una clase) |
| `08-discusion.tex:60` | Remisión a la subsección, sin repetir el bloque de cifras | Bloque `103`/Wilson/`0,8146` |
| `subsec:balance-neto` | Párrafo de sensibilidad con `e_aut` ponderada y cruda; rotulado como sensibilidad que mezcla corpus y referencias; ajuste de la síntesis «con una referencia común el balance neto no resulta negativo» para decir de qué exactitud depende | — |
| `09-conclusiones.tex:24` | Fila del objetivo 2 con primaria y lecturas complementarias; `103` como etapa previa | Peor caso como dato central |
| `09-conclusiones.tex:37` | Arbitraje ejecutado, `Sistemas` con `61` | «change c-206», `F1 0,2222`, la propuesta de sobremuestreo |
| `09-conclusiones.tex:47` | La viabilidad del modelo de lenguaje se acota: dentro y fuera de la muestra la exactitud no alcanza el umbral; fuera de muestra la etapa Gemini acierta `54/91` frente a `88/115` de las reglas, con la salvedad de que recibe los casos que las reglas no resuelven y de que el brazo solo-LLM de c-217 no mostró diferencia de exactitud sobre `103` | «alternativa técnicamente viable para la clasificación de tickets» sin matiz |
| `10-recomendaciones.tex:18` | Análisis de la taxonomía con los `61` casos disponibles (definiciones, casos de error, revisión del codebook) y criterio de éxito | El sobremuestreo con arbitraje como próximo paso |
| `10-recomendaciones.tex:26` | Corpus de composición natural, cuotas prefijadas y arbitraje por mayoría de tres etiquetadores | «que el arbitraje se ejecute antes de reportar» |
| `05-arquitectura.tex:68` | Lo medido por c-217: cerca de un tercio de llamadas y costo estimado frente al esquema solo, con remisión a `tab:gemini-solo`; la latencia solo como cota inferior del lado del cliente | «reduce la latencia y el costo de inferencia» sin respaldo |
| `01-introduccion.tex:74` | Lo excluido es un modelo supervisado afinado con el corpus acumulado en operación; la línea de base clásica se usa solo como referencia | La exclusión genérica |
| `00-resumen.tex` (ES y EN) | Exactitud fuera de muestra (primaria y ponderada) y resultado frente a la línea de base, ≤ 250 palabras cada uno según la regla de c-106; la lectura del balance neto igual a la de la discusión | Detalle prescindible (por ejemplo `W` y `r`) para hacer lugar |

Cada pasaje se verifica con `rg` (cadenas retiradas ausentes y anclajes nuevos presentes).

**Criterio único para la estimación sobre `103`.** Fuera de `07-resultados.tex`, `0,8447` aparece
una sola vez en todo `sections/*.tex`, tablas incluidas: en la fila del segundo objetivo de
`tab:cumplimiento-objetivos` (`09-conclusiones.tex:24`), rotulada como etapa previa. Verificación:
`rg -n "0,8447" "docs/Tesis/v10 (IA)/paper/sections" -g "!07-resultados.tex"` devuelve exactamente
esa línea. Se elige este criterio, y no «a lo sumo una vez por capítulo», porque (a) se verifica
con un solo comando sin distinguir prosa de tabla; (b) coincide con lo que el change reescribe:
`08-discusion.tex:8` y `:60` retiran la cifra, `09-conclusiones.tex:24` la conserva como etapa
previa, `10-recomendaciones.tex` y `00-resumen.tex` no la tienen; y (c) es más estricto que la
regla vigente de c-216 («Repetición de cifras acotada y remisión a la tabla fuera de muestra»),
cuyo texto y cuyo escenario además no coincidían (una vez fuera de resultados frente a una vez por
capítulo). Esa regla se modifica en el delta de `tesis-document` para fijar este criterio para
`0,8447`, conservar el de una vez por capítulo para `0,6893` y agregar
`subsec:validacion-fuera-muestra` como destino válido de las remisiones.

### D7 — Identificadores internos

Criterio único: en `sections/*.tex`, fuera de comentarios, no aparece ningún identificador de
cambio con la forma `c-NNN` (prosa, celdas, títulos ni notas). Los nombres de archivos versionados
que llevan sufijo `_cNNN` se admiten solo en las notas «Fuente» de tablas y como rutas
(`\texttt`/`\path`), porque son la referencia verificable del dato y no un identificador de
proceso. Se corrigen `07-resultados.tex:316`, `:328`, `:347`, `09-conclusiones.tex:37` y
`12-anexos.tex:151`. Verificación: `rg -n "c-[0-9]{3}" sections/*.tex` sin líneas que no empiecen
con `%`. Alternativa descartada: retirar también los nombres de archivo, porque se perdería la
trazabilidad que el tribunal valoró.

### D8 — Orden de las tareas: ninguna cifra entra antes de existir

1. Línea de base y estado (`git fetch`, conteos, compilación de partida).
2. Script TDD y salidas con SHA-256.
3. Sección de c-221 del memo con cada valor, archivo y comando.
4. Recién entonces la prosa: estructura de resultados, método, discusión, conclusiones,
   recomendaciones, resumen.
5. Marco teórico, glosario, bibliografía, forma.
6. Compilación y verificaciones.
7. Release: tag con confirmación.

Cada tarea de prosa cita la clave del memo de la que toma la cifra; el verificador de la matriz
de trazabilidad recibe filas `C18/…` con archivo, línea y frase ancla.

### D9 — Versión entregada y tag

- **Número y fecha**: decisión de los autores (OQ2). Recomendación: `v1.4.0`, porque cambian
  evidencia y conclusiones, no solo forma.
- **Patrón de dos commits** (el PDF no puede contener el hash de su propio commit): C1 fija
  fuentes, PDF y `compilacion.md`, con la portada y la entrada `Gomez2026_repositorio` en la versión
  nueva y el Anexo B con el nombre del tag; el tag anotado se crea sobre C1; C2 solo consigna en el
  Anexo B el hash completo de C1 y regenera el PDF. Riesgo conocido: regresiones previas del
  hash. Verificación obligatoria antes de publicar: `git rev-parse <tag>^{commit}` igual al hash del
  Anexo B de C2; `git diff <tag> C2 -- "docs/Tesis/v10 (IA)/paper/sections"` limitado a la línea del
  hash; `git show <tag>:` de `analisis_propagacion_arbitraje_c221.json`,
  `predicciones_arbitrado.json`, `contraste_linea_de_base_c213_arbitrado.json`,
  `analisis_ruido_referencia_c216.json` y `analisis_brazo_gemini_solo_c215.json` existen.
- **Redacción del Anexo B**: se reemplaza «los commits posteriores no modifican las fuentes de la
  tesis» por una afirmación verificable: el tag fija el contenido y el commit siguiente solo
  consigna el hash.
- Crear y publicar el tag, y el push de la rama, son acciones hacia afuera: tareas marcadas
  **[CONFIRMACIÓN]**, que no se ejecutan sin el «sí» expreso de los autores. El flujo es rama
  nueva, `engram sync` a cargo de los autores y PR, nunca push directo a `main`.

### D10 — Bibliografía y capítulo legal

- **Claves con año distinto**: se verifica el año de la edición citada (catálogo de la editorial o
  ISBN); el campo `year` queda con el año verificado y la clave se renombra para coincidir. Costo:
  `8` usos en `sections/` (Date `1`, Hohpe `2`, Jurafsky `1`, Stallings `1`, Efron `3`); ningún
  script ni dato versionado referencia esas claves, y los documentos históricos (changes
  archivados, memos) no se tocan. Alternativa descartada: dejar las claves (invisibles en el PDF),
  porque la observación es de las que el dictamen ya marcó dos veces y el arreglo es barato.
- **ServiceNow**: se comprueba la URL; si no responde, se reemplaza por una página oficial
  accesible del mismo contenido con `urldate` nueva; si no hay ninguna, se cita la que exista con
  la fecha de consulta y se registra la imposibilidad. No se inventa contenido.
- **Resolución AAIP 198/2023**: el repositorio ya la menciona
  (`docs/cumplimiento/marco-legal-ar-2026.md:149` y `:361`, con URL de `argentina.gob.ar`), pero
  eso no es verificación. Solo si se comprueba en el Boletín Oficial o en Infoleg (número, fecha,
  organismo y objeto) se agrega la entrada y una oración en `11-aspectos-legales.tex` junto a la
  Disposición 60-E/2016. Gobernanza HIGH: diff revisado por los autores antes de escribir (OQ4).
- **Mosqueira-Rey et al.**: se lee el texto completo (acceso abierto); si respalda la afirmación,
  se agrega la página o sección; si no, se atenúa a lo que el artículo hace (una revisión que
  sistematiza el aprendizaje con intervención humana).
- **Colavito et al.**: se agrega la salvedad de que clasifica incidencias de GitHub y no tickets
  de mesa de ayuda, en la tabla y en la prosa de `03-estado-del-arte.tex`.
- **Cifras de Paramesh y Colavito**: se verifican en el texto completo; si solo están en el
  resumen o no se encuentran, se declara la fuente efectiva.
- **`Gomez2026_repositorio`**: versión y `urldate` de la release nueva.

### D11 — Marco teórico y glosario

En `02-marco-teorico.tex`, dentro de `sec:metricas-multiclase` o en `subsec:nlp-llm`, un párrafo
breve sobre TF-IDF y regresión logística como clasificador clásico de texto (con fuente primaria
ya presente o nueva verificada) y otro sobre el puntaje de Brier y el AUROC como medidas de
calibración y discriminación (`Brier1950_verification` y `Sokolova2009_performance_measures` ya
están en la bibliografía). El capítulo 4 deja de ser el primer lugar donde se definen. El glosario
suma AUROC, Brier (como término) y TF-IDF en orden alfabético.

### D12 — Anexo J y cronograma

- **Anexo J**: la recomendación es **retirarlo** de la tesis, porque su fuente
  (`docs/defensa/respuestas-tribunal.md`) ya existe y es material de defensa; ninguna referencia
  del cuerpo apunta a `sec:anexo-respuestas-tribunal`, y el retiro compensa páginas. Decisión de
  los autores (OQ3). El delta de `tesis-defensa` es condicional y tiene un escenario por rama:
  si lo retiran, `12-anexos.tex` no contiene `sec:anexo-respuestas-tribunal` y el documento queda
  como material de defensa; si lo conservan, el anexo reproduce el documento fuente y las cifras de
  ambos se actualizan al arbitraje. Así, archivar el change no deja una spec falsa en ninguna de las
  dos decisiones, y no hace falta descartar el delta.
- **Cronograma**: se agregan a `docs/diagrams/cronograma.md` los hitos del 12 y 13-11-2026 (doble
  etiquetado `E3`/`E4`, arbitraje de `E5` y refuerzo, línea de base, calibración, análisis de
  ruido y brazo solo-LLM), con fecha de la evidencia (marcas del CSV y fechas de autor de los
  commits) y la regla de precisión vigente (sin interpolar). La figura se regenera con el comando
  documentado en ese archivo.

### D13 — Gobernanza y presupuesto de páginas

- Script, memo y prosa de resultados, método y discusión: **MEDIUM**, con checkpoint de los
  autores sobre D1 y D6 antes de editar.
- Capítulo legal (Resolución 198/2023): **HIGH**, diff previo.
- Tag, push y PR: **HIGH**, confirmación expresa.
- Páginas: el PDF vigente tiene `152` (`paper/compilacion.md`, sobre `6e06ba1`); el tope de la
  cátedra es `100` totales con exceso declarado y honrado (`dictamen-correcciones.md`, G0.1 y libro
  mayor). Presupuesto: crecimiento neto ≤ `0` si se retira el Anexo J, ≤ `+3` si no; fila `+c-221`
  en el libro mayor con el delta y su causa.

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| La lectura ponderada parece elegida por favorable | Primaria cruda; antecedentes de c-191 y c-206 citados; regla de lectura con las tres |
| La comparación «mismo orden que dentro de la muestra» se lee como equivalencia | Se rotula como orden de magnitud; los intervalos se informan |
| El matiz sobre la etapa Gemini se lee como inferioridad del modelo | Se explicita el efecto de selección (recibe los casos difíciles) y el resultado de c-217 |
| Resumen al límite de 250 palabras | Recorte explícito en D6; conteo con la regla de c-106 antes y después |
| Crecimiento de páginas y desplazamientos que rompen la paginación del Anexo I | Retiro del Anexo J; compilación y libro mayor; revisión visual de los anexos |
| Regresión del hash del tag | Patrón de dos commits con las verificaciones de D9 antes del push |
| Colisión con trabajo en curso sobre `main` (Lucas) | `git fetch` y comparación con `origin/main` al iniciar cada bloque de prosa; rebase antes del PR; puntos de contacto con c-218, c-219 y c-220 en la sección «Coordinación» de `proposal.md` y en la tarea 0.5 |
| El dato de procedencia de los 150 no llega | Tarea bloqueada; el resto avanza; no se escribe nada en su lugar |
| Falso positivo de gitleaks en prosa | Revisión del diff con el patrón conocido antes de cada commit |
| Cambiar artefactos congelados por error | El script escribe solo tres nombres fijos; `git status` al final |

## Migration Plan

1. Preparación y línea de base (tareas 0).
2. Script TDD y salidas (tareas 1).
3. Memo, sección de c-221 (tareas 2).
4. Prosa en el orden de D8 (tareas 3 a 7), con checkpoint de los autores antes de la 4.
5. Forma, bibliografía, cronograma y Anexo J (tareas 8 y 9).
6. Compilación y verificaciones (tareas 10).
7. Release con confirmación (tareas 11).

**Rollback**: `git revert` de los commits del change; el script y sus salidas son aditivos; la
sección de c-221 del memo se retira sin tocar las anteriores. Un tag publicado no se borra: se supera con otro.

## Open Questions

- **OQ1 (autores, bloquea 5.1)**: ¿de dónde y de qué período provienen los `150` casos del corpus
  independiente (sistema de origen, rango de fechas de los incidentes, criterio de extracción)? Y
  los `56` de refuerzo: ¿mismo origen, qué período? No consta en el repositorio.
- **OQ2 (autores, bloquea 11)**: número de la versión nueva (se recomienda `v1.4.0`) y fecha de la
  portada.
- **OQ3 (autores, bloquea 9.1)**: ¿se retira el Anexo J (recomendado) o se traslada a otro
  material? Si se conserva, se actualizan sus cifras al arbitraje en el anexo y en el documento
  fuente; el delta de `tesis-defensa` cubre las dos ramas y se verifica con el escenario de la
  decisión registrada.
- **OQ4 (autores, bloquea 8.5)**: si la Resolución AAIP 198/2023 se verifica en fuente oficial,
  ¿se autoriza la oración en el capítulo legal? Por defecto, sin verificación o sin autorización no
  se agrega.
- **OQ5 (autores, bloquea 11.3 y 11.4)**: confirmación expresa para crear el tag, pushear la rama
  y abrir el PR.
- **OQ6 (autores)**: confirmar la regla de lectura de D1 (primaria cruda; veredicto con las tres)
  antes de escribir la discusión.
