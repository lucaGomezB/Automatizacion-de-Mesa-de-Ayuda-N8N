# Design: Análisis de la campaña y fiabilidad entre etiquetadores

## Context

Ver `proposal.md` (Why) y la revisión previa al apply
(`docs/campana-medicion/revision-pre-apply-c-165-a-c-169.md`, transversales T1 a T4 y
sección c-167). Estado del código verificado en la rama de enmiendas:

- `evaluation/metrics.py`: `intervalo_wilson` (:159), `SEMILLA_BOOTSTRAP = 20261021` (:379),
  `REMUESTREOS_BOOTSTRAP = 2000` (:380), `NIVEL_CONFIANZA = 0.95` (:381),
  `_percentil_intervalo` (:407) y `_remuestreos_indices` (:433) privados (sus únicos
  llamadores son `intervalos_por_clase` y `intervalos_conjunto`, en el mismo módulo),
  `aciertos_laxos` (:539), `resumen_exactitud` (:589), `ETAPAS_PIPELINE` y
  `desglose_exactitud` (:616).
- `evaluation/stats.py`: `wilcoxon_tiempos_detallado` (:74, semántica fija
  manual − automatizado, lanza `ValueError` si todas las diferencias son cero),
  `tamano_efecto_dz` (:404), `ARE_WILCOXON_MINIMA = 0.864` y `efecto_minimo_detectable`
  (:441), `contraste_mcnemar` (:608).
- `evaluation/run_evaluation.py`: `_wilcoxon_o_no_aplicable` (:224, precedente de captura
  del caso degenerado), `cargar_cache_meta` (:1286), `cargar_predicciones` (:1304);
  `main()` (:1523) llama a Gemini y no se usa.
- `evaluation/predicciones.json` (v9, congelado): `cache_meta` con `corpus_hash`,
  `corpus_count`, `classifier_version` (`hybrid-v3`) y `generated_at`; **no tiene campo de
  commit** (ver Open Questions).
- No existe ninguna función de kappa en el repositorio.

## Goals / Non-Goals

- **Goals**: seis análisis puros (kappa, exactitud manual, intervención, orden de
  condición, orden de posición, fuera de muestra), CLI de solo lectura, tests offline TDD,
  salidas con README y SHA-256.
- **Non-Goals**: ejecutar la campaña; producir la planilla, el export de intervención, el
  plan o las predicciones del corpus independiente (los producen c-165, c-166 y c-168);
  validar en profundidad la planilla (lo hace `validar_doble_etiquetado` de c-168); kappa de
  Fleiss para más de dos etiquetadores; kappa ponderado o sobre el conjunto multietiqueta;
  editar la tesis (c-169); agregar dependencias; regenerar `report.md`.

## Contratos consumidos

| Contrato | Archivo | Dueño | Uso en c-167 |
|---|---|---|---|
| C1 | `evaluation/data/plantilla_etiquetado.csv` (`id_caso, id_etiquetador, tarea, sector_etiquetado, sectores_adicionales_etiquetados, inicio, timestamp`, ambos instantes ISO-8601; en `brazo_manual` `inicio` es obligatorio y `timestamp` es el fin). `doble_etiquetado`: `E1` y `E2` fijos, ambos en todos los casos. `brazo_manual`: `O1` y `O2` fijos, cada caso con al menos un operador, a lo sumo un registro por `(id_caso, id_etiquetador)`; no se exige que ambos operadores cubran todos los casos | c-168 | Kappa (`tarea = doble_etiquetado`), referencia nueva y exactitud manual (`tarea = brazo_manual`) |
| C2 | `evaluation/data/campana/registro_sujetos.csv` (`alias, rol, persona`; rol en `etiquetador`, `operador`, `analista_original`, `autor`; `persona` = seudónimo estable `P<n>`, cuya correspondencia con identidades custodia el director fuera del repo) | orquestador (contrato compartido) | Rechazo de solapes de rol por `persona` |
| C5 | `evaluation/data/campana/intervenciones.csv` | c-165 | `tasa_intervencion_humana` y proporción de tiempo |
| C6 | `evaluation/data/campana/plan_campana.csv` (`id_caso, posicion, mitad, brazo_primero, modo, seed`) | c-166 | Universo de casos de campaña, efecto de orden |
| C9 | `evaluation/data/campana/predicciones_independiente.json`, `evaluation/no_solape.py::verificar_no_solape` | c-166 | `evaluar_fuera_de_muestra` |

Además se leen, en solo lectura: el corpus `data/corpus_evaluacion_pseudonimizado.json`
(`sector_asignado`, `sectores_adicionales`, `tiempo_automatizado_s`) y
`evaluation/predicciones.json` (bloque in-sample y predicción v9 por caso).

## Decisions

- **D1 — Ubicación (C7).** `evaluation/kappa.py` (kappa, varianza asintótica, bootstrap,
  PABAK, Landis y Koch), `evaluation/campana.py` (registro de sujetos y referencia,
  exactitud manual, intervención, orden, fuera de muestra) y el CLI
  `evaluation/analisis_campana.py` (solo lectura, validación mínima, delegación y escritura
  en `evaluation/data/campana/analisis/`). Fixtures sintéticos en
  `evaluation/tests/fixtures/campana/` con README que los marca SINTÉTICOS. No se engorda
  `metrics.py` ni `stats.py`.

- **D2 — Reutilización, no reimplementación.** Exactitud estricta y laxa: `resumen_exactitud`
  y `desglose_exactitud`. Wilson: `intervalo_wilson`. McNemar: `contraste_mcnemar`.
  Contraste pareado: `wilcoxon_tiempos_detallado` envuelto. Posición real y desvíos del
  plan: `reconstruir_posicion_real` y `desvios_respecto_del_plan` de
  `evaluation/brazo_manual.py` (c-165). d_z: `tamano_efecto_dz`. MDE:
  `efecto_minimo_detectable` con `ARE_WILCOXON_MINIMA`. Bootstrap: los helpers de
  `metrics.py` promovidos (D3). Lo único estadísticamente nuevo es el kappa con su varianza
  y los envoltorios de `scipy.stats.mannwhitneyu` y `scipy.stats.spearmanr`.

- **D3 — Promoción de los helpers de bootstrap a públicos.** `_percentil_intervalo` pasa a
  `percentil_intervalo` y `_remuestreos_indices` a `remuestreos_indices` en `metrics.py`; se
  actualizan sus llamadas internas en `intervalos_por_clase` e `intervalos_conjunto`. Se
  elige promover (y no importar nombres privados desde otro módulo) porque pasan a ser API
  compartida por tres consumidores. Sin cambio de comportamiento: la suite existente sigue
  verde y los IC bootstrap de v9 no cambian. Un test de consistencia exige que `kappa.py` y
  `campana.py` usen esos objetos importados de `metrics.py` (identidad) y las constantes
  `SEMILLA_BOOTSTRAP` y `REMUESTREOS_BOOTSTRAP`, con generador `random.Random(semilla)`.

- **D4 — Kappa de Cohen.** No ponderado, sobre `sector_etiquetado`, con las 5 clases de
  `SECTORES_CANONICOS` importadas de `evaluation/corpus.py` (las clases sin uso no alteran κ
  ni su varianza). Exige exactamente dos `id_etiquetador` distintos en
  `tarea = doble_etiquetado`, cada uno con una etiqueta por caso; si no, `ValueError` que
  nombra los alias encontrados. Fleiss queda fuera del alcance y se declara en la salida.
  Con la matriz de proporciones p_ij (filas E1, columnas E2), p_o = Σ p_ii,
  p_e = Σ p_i. p_.i, κ = (p_o − p_e) / (1 − p_e).
  - **IC asintótico** con la varianza bajo H1 de Fleiss, Cohen y Everitt (1969):
    Var(κ) = [Σ_i p_ii (1 − (p_i. + p_.i)(1 − κ))² + (1 − κ)² Σ_{i≠j} p_ij (p_.i + p_j.)²
    − (κ − p_e (1 − κ))²] / (n (1 − p_e)²); IC = κ ± z · raíz(Var), con z del
    `NIVEL_CONFIANZA`. Un Var negativo por redondeo se lleva a 0. Límites recortados a
    [−1, 1]. Diagonal perfecta: κ = 1 e IC [1, 1]. p_e = 1 (solo posible con p_o = 1, un
    único sector usado por ambos): κ no estimable, sin valor numérico ni IC.
  - **Oráculo** (verificado con Python): matriz [[20, 5, 0], [3, 15, 2], [0, 4, 11]],
    n = 60 → p_o = 0,766667, p_e = 0,347222, κ = 0,642553, SE = 0,083594, IC 95 %
    asintótico [0,478711; 0,806395]; PABAK con k = 5 = 0,708333; rótulo "sustancial" y el
    IC abarca "moderado" y "sustancial".
  - **IC bootstrap** por casos (se remuestrean pares E1/E2), `SEMILLA_BOOTSTRAP` y
    `REMUESTREOS_BOOTSTRAP`, percentiles 2,5 y 97,5 con `percentil_intervalo`. Remuestras
    con p_e = 1 se descartan y se cuentan; si superan el 5 % de los remuestreos, el
    resultado es "IC bootstrap no computable" con el conteo, sin intervalo.
  - **Reporte**: κ, ambos IC (método y nivel), p_o, p_e, PABAK = (k·p_o − 1)/(k − 1) con
    k = 5, n, remuestras degeneradas, rótulo de Landis y Koch del valor puntual (pobre < 0;
    leve [0; 0,20]; aceptable (0,20; 0,40]; moderado (0,40; 0,60]; sustancial (0,60; 0,80];
    casi perfecto (0,80; 1]) y, por cada IC, los rótulos de sus límites con la nota de que el
    rótulo del IC puede abarcar dos o más categorías.
  - **Alcance declarado**: kappa de los etiquetadores nuevos; no es un IC del 0,87 original
    (c-169 decide la presentación conjunta).

- **D5 — Registro de sujetos y referencia (C2).** `validar_registro_sujetos` lee
  `registro_sujetos.csv` (`alias, rol, persona`) y rechaza con `ValueError`: una misma
  `persona` con más de un rol (el control de solape es por persona, no por alias, porque una
  persona puede tener varios alias); un alias con más de un rol o más de una persona;
  cualquier `id_etiquetador` de la planilla que no figure en el registro; un alias de
  `tarea = doble_etiquetado` que no sea `etiquetador`; un alias de `tarea = brazo_manual` que
  no sea `operador`; y un alias de la planilla cuya persona tenga rol `analista_original` o
  `autor`. El error nombra persona, alias y roles. `construir_referencia`
  admite dos referencias rotuladas:
  - `consenso_doble_etiquetado` (por defecto): casos donde E1 y E2 coinciden en
    `sector_etiquetado`. Conjunto de verdad para la exactitud laxa = sector consensuado más
    la **intersección** de los `sectores_adicionales_etiquetados` de E1 y E2 (análogo del
    consenso: solo lo que ambos marcaron). Los casos discordantes no entran en la exactitud;
    la salida declara cuántos casos quedaron excluidos por discordancia (conteo e ids) con la
    advertencia de que la exclusión sesga la referencia hacia casos fáciles y, por lo tanto,
    tiende a sobrestimar la exactitud de ambos brazos.
  - `consenso_original`: `sector_asignado` y `conjunto_verdad` del corpus, idéntico al brazo
    automatizado de v9.
  Toda salida declara `referencia_usada`.

- **D6 — Exactitud del brazo manual.** El brazo manual no exige que ambos operadores
  cubran todos los casos (C1): cada operador se evalúa sobre los casos de la referencia que
  etiquetó, con `desglose_exactitud(claves = id_etiquetador)`: estricta =
  `sector_etiquetado` igual al de referencia; laxa = `sector_etiquetado` dentro del conjunto
  de verdad (misma definición que `aciertos_laxos` para el brazo automatizado: se evalúa solo
  la etiqueta primaria del operador). Wilson por operador. Un caso no etiquetado por un
  operador no es error de ese operador; la salida declara la cobertura (casos etiquetados,
  compartidos y exclusivos de cada operador) y advierte que, si las coberturas difieren, la
  comparación entre operadores mezcla operador con dificultad de los casos. La **agregada**
  es Σ aciertos / Σ etiquetas sobre la unión de casos de la referencia, con IC bootstrap por
  caso: se remuestrean casos y cada caso aporta las etiquetas (una o dos) de los operadores
  que lo etiquetaron (evita la pseudo-replicación de Wilson sobre el total de etiquetas).
  **Contraste manual vs automatizado** por operador: `contraste_mcnemar(acierto estricto del
  operador, acierto estricto de la predicción v9)` pareado por `(id_caso, id_etiquetador)`,
  es decir, sobre los casos de la referencia que ese operador etiquetó, con la predicción
  leída de `predicciones.json` por `cargar_predicciones` (solo lectura). La exactitud de v9 contra la
  referencia nueva es un número nuevo, rotulado, que no reemplaza los números canónicos v9.

- **D7 — Tasa de intervención humana (`subsec:medicion-intervencion`).** Universo = casos de
  la corrida, tomados de `plan_campana.csv` (C6) o del sidecar de la corrida; nunca del export
  C5, que contiene solo filas intervenidas. `tasa_intervencion_humana` = casos con al menos
  una intervención vinculada / casos de la corrida, con Wilson; filas con `id_caso` nulo se
  cuentan como no vinculables y quedan fuera; un `id_caso` fuera de la corrida es error
  accionable. `actor_alias` es un HMAC truncado y no se usa como clave de análisis. Desgloses por
  `origen_intervencion` (casos con al menos una intervención de ese origen; un caso puede
  figurar en varios y se declara) y por `cambio_sector`. Contraste con la cota 0,15 de la
  sub-hipótesis 2: límite superior de Wilson < 0,15 → "compatible"; ≥ 0,15 → "no compatible"
  (incluye la estimación puntual menor a 0,15 con IC que cruza la cota; la salida trae
  estimación y ambos límites para que c-169 lo redacte). Ejemplos verificados: 20/200 →
  [0,065670; 0,149406] compatible; 26/200 → [0,090282; 0,183664] no compatible.
  **Proporción de tiempo** = Σ duracion_s / Σ (tiempo_automatizado_s + duracion_s) sobre los
  casos del plan con tiempo conocido: los no intervenidos aportan duración 0 y los
  intervenidos aportan la suma de sus `duracion_s`; los intervenidos con alguna `duracion_s`
  nula (sin inicio) se excluyen del cociente. IC bootstrap por caso del cociente de sumas, no
  Wilson. Cobertura = k de m casos intervenidos con duración completa; si es menor al 80 %
  la proporción se declara "no estimable" con el motivo. El denominador se rotula "tiempo de
  registro automatizado" (limitación: `tiempo_automatizado_s` mide solo el registro). Casos
  sin `tiempo_automatizado_s` se excluyen y se cuentan.

- **D8 — Efecto de orden (alineado con la spec; no hay término de orden en modelo).**
  Respuesta primaria: duración del brazo manual `duracion_s = timestamp − inicio` (segundos)
  por `(id_caso, id_etiquetador)` de la planilla con `tarea = brazo_manual`; secundaria:
  acierto estricto, pareado igual. No se usa el `tiempo_manual_s` del corpus (canónico de la
  campaña 2026-10, intocable). El nombre `duracion_s` coincide con la columna de C5 pero mide
  otra cosa: en la salida vive bajo la sección de orden y se rotula "duración del brazo
  manual". Una duración negativa es error accionable (caso y operador). Cada operador se
  analiza sobre los casos que etiquetó. `posicion`, `mitad` y `brazo_primero` vienen del plan (C6). Análisis por
  operador:
  - **Orden de condición**: tiempo manual de los casos con `brazo_primero = manual` frente a
    `automatizado`. Si el plan no cruza casos (cada caso tiene una sola condición), grupos
    independientes con Mann-Whitney bilateral y r rank-biserial = 2·U_a/(n_a·n_b) − 1. Solo
    si el plan cruza los mismos casos en dos corridas con condición opuesta, Wilcoxon pareado
    por `id_caso` con r y d_z. El diseño lo declara el plan, no el análisis.
  - **Posición** (aprendizaje o fatiga): Spearman de la duración contra la posición real
    del caso para el operador, y mitad 1 frente a mitad 2 del plan con Mann-Whitney y r. La
    posición real y los desvíos respecto del plan se importan de c-165
    (`evaluation/brazo_manual.py::reconstruir_posicion_real` y `desvios_respecto_del_plan`),
    no se reimplementan. Decisión: el aprendizaje o la fatiga dependen del orden en que el
    operador efectivamente trabajó, por eso Spearman usa la posición real; la comparación de
    mitades usa la `mitad` asignada en el plan (análisis por asignación) y la salida declara
    la cantidad de desvíos para que se lea con esa salvedad.
  - **Mínimo**: n ≥ 6 por grupo (o 6 pares), umbral al que p < 0,05 es alcanzable en las
    tres pruebas; si no se alcanza, "no aplicable" sin valor de efecto.
  - **MDE** con `efecto_minimo_detectable(eficiencia_relativa = ARE_WILCOXON_MINIMA)`:
    diseño pareado, n = pares, escala d_z (≈ 0,21 con 200 pares; ≈ 0,30 con 100); grupos
    independientes, n efectivo = n_a·n_b/(n_a + n_b), escala d (≈ 0,43 con 100 y 100).
  - **Lectura**: un resultado no significativo se rotula "no significativo; efectos menores
    que el MDE no son detectables", nunca "sin efecto de orden".
  - **Envoltorios neutros**: `contraste_pareado(grupo_a, grupo_b)` llama a
    `wilcoxon_tiempos_detallado(grupo_a, grupo_b)` y renombra el resultado (el p unilateral
    se rotula grupo_a > grupo_b); captura el `ValueError` de "todas las diferencias cero" (y
    un p NaN) como no aplicable, como `_wilcoxon_o_no_aplicable`. `contraste_independiente`
    envuelve `mannwhitneyu`.
  - **Secundaria (acierto estricto)**: en el diseño cruzado, `contraste_mcnemar` pareado por
    caso; en grupos independientes McNemar no corresponde (no hay pares) y se reporta Wilson
    por grupo con la prueba exacta de Fisher bilateral (`scipy.stats.fisher_exact`).

- **D9 — Fuera de muestra (C9).** `evaluar_fuera_de_muestra` lee las predicciones solo con
  `cargar_predicciones` y `cargar_cache_meta` (nunca `main()`). Firma:
  `evaluar_fuera_de_muestra(..., pines_in_sample, commit_in_sample=None)`. Aborta si la
  `classifier_version` del `cache_meta` in-sample (`predicciones.json`, solo lectura) difiere
  de la del independiente, o si `pines_in_sample` (obligatorio; versión de `google-genai` y
  modelo, tomados del README de `evaluation/data/campana/` que escribe c-166 en su tarea 4.9 a
  partir de `openspec/config.yaml` y del Anexo B, porque el cache de v9 no los registra)
  difiere de los `pines` del cache independiente; compara el
  commit solo cuando ambos lo traen (o se provee el parámetro opcional `commit_in_sample`) y,
  si falta en el in-sample, no aborta y declara la limitación "commit in-sample no registrado; comparabilidad verificada por versión y pines"; re-ejecuta
  `verificar_no_solape` de c-166 y aborta si informa solape, y verifica la alineación de ids
  entre predicciones y corpus independiente. "Ambas etapas" = desglose por etapa en cascada
  con `desglose_exactitud(orden = ETAPAS_PIPELINE)` más la exactitud global con Wilson, igual
  que in-sample. Los bloques se rotulan in-sample y out-of-sample y nunca se mezclan. Si el
  corpus independiente o sus predicciones no existen, la sección se declara "no se obtuvo"
  con el artefacto faltante y no se sustituye por in-sample. `report.md` no se regenera.

- **D10 — Contrato de las funciones y del CLI.** Las funciones reciben registros ya cargados
  (listas de dicts o dataclasses) y devuelven dataclasses congeladas; no hacen I/O. El CLI
  lee rutas con valores por defecto de C1, C5, C6 y C9, re-verifica lo mínimo (columnas
  presentes; `E1` y `E2` fijos en todos los casos de `doble_etiquetado`; a lo sumo `O1` y
  `O2` y un registro por `(id_caso, id_etiquetador)` en `brazo_manual`) con error accionable que nombra archivo y
  columna, ejecuta cada sección de forma independiente (un dataset ausente marca su sección
  "no se obtuvo" sin abortar las otras; los abort de D5 y D9 sí detienen su sección) y
  escribe `resultados.json`, `resultados.md` y `SHA256SUMS.txt` (hash de cada salida y de
  cada entrada leída) en `evaluation/data/campana/analisis/`, junto a un README de
  procedencia.

- **D11 — TDD estricto.** Safety net de la suite `evaluation/` antes de tocar nada; fixtures
  creados antes de usarse; por función RED, GREEN, triangulación y REFACTOR con ejecución de
  la suite en cada paso. Semillas fijas.

- **D12 — Coordinación.** c-165, c-166 y c-168 AGREGAN requisitos a
  `evaluation-campaign-instrumentation` (instrumento, diseño y doble etiquetado); c-167
  AGREGA requisitos a `evaluation-framework` porque gobierna `metrics.py`/`stats.py` y
  consume, no produce, los datasets. Se archiva después de c-165, c-166 y c-168. c-169
  consume las salidas de c-167.

## Lo que NO cambia

- `evaluation/report.md`, `evaluation/predicciones.json`, `evaluation/predicciones_calibracion.json`
  y los números canónicos v9: no se escriben ni se regeneran.
- `run_evaluation.main()` y `generar_reporte` no se invocan.
- El comportamiento de `metrics.py` y `stats.py` (solo cambia el nombre de dos helpers).
- Las cadenas canónicas de sectores, el corpus y `docs/Tesis/`.
- Los requisitos existentes de `evaluation-framework`.

## Risks / Trade-offs

- Kappa con n chico produce IC ancho y remuestras degeneradas → ambos IC, conteo de
  degeneradas y regla del 5 %.
- La intersección de adicionales en la referencia nueva es más estricta que la unión → se
  declara; la referencia alternativa reproduce la definición de v9.
- Grupos independientes en el orden de condición tienen menos potencia que un diseño cruzado
  → MDE reportado y lectura prudente del resultado no significativo.
- El denominador de la proporción de tiempo mide solo el registro automatizado → rotulado
  como limitación.
- Divergencia entre los CSV de campo y los contratos → validación mínima con error
  accionable; la validación completa es de c-168.

## Migration Plan

1. Promover los helpers en `metrics.py` (suite existente verde).
2. Agregar fixtures sintéticos, `kappa.py`, `campana.py` y sus tests.
3. Agregar el CLI y su test end-to-end offline.
4. Rollback: eliminar los archivos nuevos y revertir el renombre.

## Open Questions

- **Tiempo manual por operador y caso (resuelta).** El orquestador agregó a C1 la columna
  `inicio`; la respuesta del efecto de orden es `timestamp − inicio` de la planilla.
- **Commit del clasificador in-sample (resuelta por el orquestador).** La copia congelada de
  v9 no registró commit; la comparabilidad se verifica por `classifier_version` y `pines`, el
  commit se compara solo si ambos bloques lo traen y su ausencia en el in-sample es una
  limitación declarada, no un aborto. `commit_in_sample` es opcional.
- **Pines del bloque in-sample (resuelta por el orquestador).** El cache de v9 no registra
  `pines`; salen del README de `evaluation/data/campana/` (c-166, tarea 4.9, desde
  `openspec/config.yaml` y el Anexo B) y entran como parámetro obligatorio `pines_in_sample`.
  `classifier_version` in-sample sí se lee del cache de v9. El CLI expone ambos como
  argumentos (`--pines-in-sample`, `--commit-in-sample` opcional).
