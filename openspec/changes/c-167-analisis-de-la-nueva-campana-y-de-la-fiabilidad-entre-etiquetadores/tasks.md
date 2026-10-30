# Tasks: Análisis de la campaña y fiabilidad entre etiquetadores

Reglas de todo el change: TDD estricto (RED, GREEN, triangulación, REFACTOR) con ejecución de
`python -m pytest evaluation` en cada paso; ningún código de producción sin un test que falle
antes; identificadores en español; sin red ni Gemini. No se escriben ni se regeneran
`evaluation/report.md`, `evaluation/predicciones.json` ni números canónicos v9.

## 0. Preparación

- [x] 0.1 Safety net: ejecutar `python -m pytest evaluation` desde la raíz y registrar "N tests pasando"; si algo falla, detenerse y reportarlo como falla preexistente (no corregirla)
- [x] 0.2 Registrar el SHA-256 de `evaluation/report.md`, `evaluation/predicciones.json` y `evaluation/predicciones_calibracion.json` como línea base para el cierre
- [x] 0.3 Verificar que los changes de los que depende están aplicados: `evaluation/doble_etiquetado.py` (c-168), `evaluation/brazo_manual.py` con `reconstruir_posicion_real` y `desvios_respecto_del_plan` y el formato de `intervenciones.csv` (c-165), `evaluation/no_solape.py::verificar_no_solape` y el formato de `plan_campana.csv` (c-166); si falta alguno, aplicar solo las secciones que no lo requieren y reportar
- [x] 0.4 Crear `evaluation/tests/fixtures/campana/` con README que los marque SINTÉTICOS (no son datos de campo) y los fixtures, antes de cualquier test que los use:
  - `plantilla_etiquetado.csv` con el orden de columnas de C1 (`id_caso, id_etiquetador, tarea, sector_etiquetado, sectores_adicionales_etiquetados, inicio, timestamp`): `E1`/`E2` en todos los casos de `doble_etiquetado`, con concordantes y al menos tres discordantes; `O1`/`O2` en `brazo_manual` con casos compartidos y casos exclusivos de cada operador
  - `registro_sujetos.csv` (`alias, rol, persona`) válido y `registro_sujetos_solape.csv` con una misma `persona` como `operador` y `etiquetador` bajo dos alias
  - `corpus_campana.json` sintético con `sector_asignado`, `sectores_adicionales` y `tiempo_automatizado_s`
  - `plan_campana.csv` (`id_caso, posicion, mitad, brazo_primero, modo, seed`) con al menos 6 casos por condición y por mitad
  - `intervenciones.csv` con el esquema C5 (solo filas intervenidas), con varios orígenes, con y sin `cambio_sector`, una fila con `id_caso` nulo y una con `duracion_s` nulo
  - `predicciones_in_sample.json` (`cache_meta` como el de v9: `classifier_version`, sin `pines` ni `commit`) y `predicciones_independiente.json` (`classifier_version`, `pines`, `commit`), más una variante independiente con `pines` distintos; los `pines_in_sample` del fixture van en el README sintético y `corpus_independiente.json` con ids `I001..`, más una variante con `classifier_version` distinto y otra con un caso en solape
- [x] 0.5 Verificar con un test de humo que los fixtures cargan y respetan los encabezados de C1, C2, C5 y C6

## 1. Promoción de los helpers de bootstrap (`evaluation/metrics.py`)

- [x] 1.1 RED: test que importa `percentil_intervalo` y `remuestreos_indices` desde `evaluation.metrics` y verifica, sobre una muestra fija, el mismo resultado que hoy dan los helpers privados; verificar que falla por nombre inexistente
- [x] 1.2 GREEN: renombrar `_percentil_intervalo` (:407) a `percentil_intervalo` y `_remuestreos_indices` (:433) a `remuestreos_indices`, y actualizar sus llamadas en `intervalos_por_clase` e `intervalos_conjunto`; ejecutar la suite completa y verificar que todo sigue verde
- [x] 1.3 Triangular: test de que `intervalos_por_clase` e `intervalos_conjunto` devuelven exactamente los mismos intervalos que antes del renombre sobre el fixture existente `corpus_fixture.json`
- [x] 1.4 REFACTOR: docstrings de los helpers públicos; suite verde

## 2. Kappa de Cohen (`evaluation/kappa.py`)

- [x] 2.1 RED: test del oráculo con la matriz [[20, 5, 0], [3, 15, 2], [0, 4, 11]] (n = 60) inmersa en las 5 clases de `SECTORES_CANONICOS`: κ = 0,642553, p_o = 0,766667, p_e = 0,347222 (tolerancia 1e-6); verificar que falla
- [x] 2.2 GREEN: implementar `kappa_cohen` a partir de pares (E1, E2) con las clases importadas de `evaluation/corpus.py`; verificar el test 2.1
- [x] 2.3 Triangular: diagonal perfecta con más de un sector (κ = 1); matriz de acuerdo igual al azar (κ = 0); todos los casos con el mismo único sector (p_e = 1, no estimable sin valor numérico)
- [x] 2.4 RED: test del error estándar asintótico del oráculo, SE = 0,083594, e IC 95 % [0,478711; 0,806395]; verificar que falla
- [x] 2.5 GREEN: implementar la varianza bajo H1 de Fleiss, Cohen y Everitt (1969) con Var negativo por redondeo llevado a 0; verificar 2.4
- [x] 2.6 Triangular: diagonal perfecta da IC [1, 1]; la matriz [[9, 1], [0, 10]] (κ = 0,9; κ + 1,96·SE ≈ 1,09) da límite superior recortado a 1; p_e = 1 no devuelve IC
- [x] 2.7 RED: test de que el IC bootstrap es idéntico en dos corridas y de consistencia: `kappa.percentil_intervalo is metrics.percentil_intervalo`, `kappa.remuestreos_indices is metrics.remuestreos_indices` y uso de `SEMILLA_BOOTSTRAP` y `REMUESTREOS_BOOTSTRAP`; verificar que falla
- [x] 2.8 GREEN: implementar el bootstrap por casos con `random.Random(SEMILLA_BOOTSTRAP)`, descarte y conteo de remuestras con p_e = 1; verificar 2.7
- [x] 2.9 Triangular: dataset chico con un sector dominante donde más del 5 % de las remuestras son degeneradas da "IC bootstrap no computable" con el conteo; con menos del 5 % el IC se emite y el conteo se reporta
- [x] 2.10 RED/GREEN: PABAK = (5·p_o − 1)/4 (oráculo 0,708333) y rótulo de Landis y Koch con tests en los bordes (−0,01 pobre; 0,20 leve; 0,2001 aceptable; 0,40; 0,60; 0,80; 0,8001 casi perfecto) y rótulos de los límites de cada IC (oráculo: "sustancial", IC abarca "moderado" y "sustancial")
- [x] 2.11 RED/GREEN: con uno o con tres `id_etiquetador` en `doble_etiquetado`, o con un caso sin etiqueta de `E2`, `ValueError` que nombra los alias o el caso; la salida declara "Fleiss fuera del alcance" y "kappa de etiquetadores nuevos, no IC del 0,87 original"
- [x] 2.12 REFACTOR: dataclass congelada del resultado, constantes de rótulos, nombres; suite verde

## 3. Registro de sujetos y referencia (`evaluation/campana.py`)

- [x] 3.1 RED: con `registro_sujetos_solape.csv` (misma `persona` con roles `operador` y `etiquetador` bajo dos alias) `validar_registro_sujetos` lanza `ValueError` que nombra persona, alias y roles; verificar que falla
- [x] 3.2 GREEN: implementar el control por `persona`; verificar 3.1
- [x] 3.3 Triangular: alias con dos roles; alias de la planilla no registrado; `E1` con rol `operador`; persona con rol `analista_original` o `autor` presente en la planilla; registro válido sin error
- [x] 3.4 RED/GREEN: `construir_referencia(consenso_doble_etiquetado)` devuelve los concordantes con conjunto de verdad = sector consensuado más la intersección de adicionales, y declara conteo e ids de discordantes con la advertencia de sesgo hacia casos fáciles
- [x] 3.5 Triangular: `construir_referencia(consenso_original)` devuelve `sector_asignado` y `conjunto_verdad` del corpus y el rótulo `consenso_original`
- [x] 3.6 REFACTOR; suite verde

## 4. Exactitud del brazo manual

- [x] 4.1 RED: exactitud estricta y laxa por operador, sobre los casos que cada operador etiquetó, con Wilson y nivel declarado, y cobertura (etiquetados, compartidos, exclusivos); verificar que falla
- [x] 4.2 GREEN: implementar `exactitud_brazo_manual` con `desglose_exactitud(claves = id_etiquetador)`; verificar 4.1
- [x] 4.3 Triangular: caso donde la laxa supera a la estricta; caso exclusivo de `O1` no cuenta como error de `O2`; casos discordantes excluidos y contados
- [x] 4.4 RED/GREEN: agregada = Σ aciertos / Σ etiquetas sobre la unión de casos con IC bootstrap por caso; test de que el IC difiere de `intervalo_wilson(aciertos, etiquetas)` y de que es reproducible
- [x] 4.5 RED/GREEN: McNemar por operador pareado por `(id_caso, id_etiquetador)` contra la predicción in-sample leída con `cargar_predicciones`; test de que el archivo de predicciones conserva su SHA-256
- [x] 4.6 Triangular: operador sin discordancias con la predicción da McNemar "no aplicable"; referencia alternativa cambia `referencia_usada` y los números
- [x] 4.7 REFACTOR; suite verde

## 5. Tasa de intervención humana de campaña

- [x] 5.1 RED: con 20 de 200 casos intervenidos, `tasa_intervencion_humana` = 0,10, Wilson [0,065670; 0,149406] y contraste "compatible"; verificar que falla
- [x] 5.2 GREEN: implementar con el denominador tomado del plan o del sidecar de la corrida (nunca del export); verificar 5.1
- [x] 5.3 Triangular: 26 de 200 da 0,13, Wilson [0,090282; 0,183664] y "no compatible" con estimación y límites; cero intervenciones da tasa 0 sin división por cero
- [x] 5.4 RED/GREEN: desglose por `origen_intervencion` y por `cambio_sector`; fila con `id_caso` nulo contada como no vinculable; `id_caso` fuera de la corrida da error; test de que `actor_alias` no aparece como clave en el resultado
- [x] 5.5 RED/GREEN: proporción de tiempo con 10 casos de 20 s de registro y dos intervenidos de 30 s y 50 s = 80 / 280 = 0,285714, IC bootstrap por caso del cociente y denominador rotulado "tiempo de registro automatizado"
- [x] 5.6 Triangular: cobertura 4 de 5 (80 %) estimable; 3 de 4 (75 %) "no estimable" con el motivo; caso sin `tiempo_automatizado_s` excluido y contado
- [x] 5.7 REFACTOR; suite verde

## 6. Efecto de orden de condición y de posición

- [x] 6.1 RED: `contraste_pareado(grupo_a, grupo_b)` envuelve `wilcoxon_tiempos_detallado` con nombres neutros y devuelve no aplicable cuando todas las diferencias son cero; verificar que falla
- [x] 6.2 GREEN: implementar capturando `ValueError` y p NaN como `_wilcoxon_o_no_aplicable`; verificar 6.1
- [x] 6.3 RED/GREEN: `contraste_independiente` (Mann-Whitney bilateral) con r = 2·U_a/(n_a·n_b) − 1; triangular con grupos separados (r = −1 cuando todo `grupo_a` es menor) y con grupos iguales
- [x] 6.4 RED/GREEN: duración del brazo manual = `timestamp − inicio` por `(id_caso, id_etiquetador)`; duración negativa da error que nombra caso y operador; test de que `tiempo_manual_s` del corpus no se usa
- [x] 6.5 RED/GREEN: orden de condición por operador con grupos independientes (plan sin cruce) y con Wilcoxon pareado más d_z (plan cruzado); n < 6 en un grupo da no aplicable
- [x] 6.6 RED/GREEN: efecto de posición con Spearman contra la posición real importada de `evaluation/brazo_manual.py::reconstruir_posicion_real` y mitad 1 vs mitad 2 con Mann-Whitney; cantidad de desvíos desde `desvios_respecto_del_plan`; test de que las funciones de c-165 se importan y no se redefinen
- [x] 6.7 RED/GREEN: MDE con `efecto_minimo_detectable(eficiencia_relativa = ARE_WILCOXON_MINIMA)`: pareado n = 200 → 0,2131 y n = 100 → 0,3014 (escala d_z); independientes 100 y 100 → n efectivo 50 → 0,4262 (escala d)
- [x] 6.8 RED/GREEN: con p ≥ 0,05 el rótulo es "no significativo; efectos menores que el MDE no son detectables" y nunca "sin efecto"
- [x] 6.9 RED/GREEN: acierto estricto secundario con `contraste_mcnemar` en diseño cruzado y Wilson por grupo más Fisher exacta en grupos independientes
- [x] 6.10 REFACTOR; suite verde

## 7. Evaluación fuera de muestra

- [x] 7.1 RED: `evaluar_fuera_de_muestra` sobre los fixtures devuelve bloques rotulados in-sample y out-of-sample con exactitud global, Wilson y desglose por etapa en el orden de `ETAPAS_PIPELINE`; verificar que falla
- [x] 7.2 GREEN: implementar `evaluar_fuera_de_muestra(..., pines_in_sample, commit_in_sample=None)` leyendo solo con `cargar_predicciones` y `cargar_cache_meta` (`classifier_version` in-sample desde el cache de v9; pines in-sample desde el parámetro); verificar 7.1
- [x] 7.3 Triangular: `classifier_version` distinto aborta mostrando ambos valores; `pines` del cache independiente distintos de `pines_in_sample` abortan; sin `pines_in_sample` falla con error accionable; commit distinto aborta solo cuando ambos bloques lo traen (o se provee `commit_in_sample`); in-sample sin `commit` y sin `commit_in_sample`, con versión y pines iguales, NO aborta y la salida declara "commit in-sample no registrado; comparabilidad verificada por versión y pines"
- [x] 7.4 RED/GREEN: re-ejecución de `verificar_no_solape` (c-166); con el fixture en solape aborta nombrando los casos
- [x] 7.5 RED/GREEN: corpus independiente o predicciones ausentes declaran "no se obtuvo" con el artefacto faltante, sin métricas in-sample en su lugar
- [x] 7.6 Test de que `run_evaluation.main` y `_resolver_clasificador_real` no se invocan (monkeypatch que lanza si se llaman)
- [x] 7.7 REFACTOR; suite verde

## 8. CLI de solo lectura (`evaluation/analisis_campana.py`)

- [ ] 8.1 RED: test end-to-end del CLI sobre los fixtures en `tmp_path` con red bloqueada (monkeypatch de `socket.socket`): escribe `resultados.json`, `resultados.md` y `SHA256SUMS.txt` y ningún otro archivo; verificar que falla
- [ ] 8.2 GREEN: implementar el CLI (lectura, validación mínima con error que nombra archivo y columna, delegación, escritura); verificar 8.1
- [ ] 8.3 Triangular: sin `intervenciones.csv` la sección de intervención dice "no se obtuvo" y kappa y exactitud se reportan; columna `inicio` faltante da error que la nombra
- [ ] 8.4 Reproducibilidad: dos corridas producen `resultados.json` y `SHA256SUMS.txt` idénticos
- [ ] 8.5 Crear `evaluation/data/campana/analisis/README.md` con procedencia, entradas esperadas, semilla, remuestreos y el significado de `SHA256SUMS.txt`
- [ ] 8.6 REFACTOR; suite verde

## 9. Cierre

- [ ] 9.1 Ejecutar `python -m pytest evaluation` y verificar la suite completa verde, offline, con al menos los N tests de la línea base más los nuevos
- [ ] 9.2 Ejecutar `openspec validate c-167-analisis-de-la-nueva-campana-y-de-la-fiabilidad-entre-etiquetadores --strict --no-interactive`
- [ ] 9.3 Ejecutar `git diff --stat` y verificar que `evaluation/report.md`, `evaluation/predicciones.json`, `evaluation/predicciones_calibracion.json` y los números canónicos v9 no figuran; comparar sus SHA-256 con la línea base de 0.2
