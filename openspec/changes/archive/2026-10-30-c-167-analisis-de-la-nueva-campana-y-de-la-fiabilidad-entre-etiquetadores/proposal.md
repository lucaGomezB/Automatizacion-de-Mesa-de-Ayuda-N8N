# Proposal: Análisis de la nueva campaña y de la fiabilidad entre etiquetadores

## Why

Los datasets de la campaña (brazo manual e intervención, c-165), del contrabalanceo y del
corpus independiente (c-166) y del doble etiquetado nuevo (c-168) no tienen consumidores
analíticos: hoy no existe código que calcule la exactitud del brazo manual, la tasa de
intervención humana con IC, el efecto de orden, las métricas fuera de muestra ni el kappa
con intervalo de confianza. Sin ese análisis la tesis no puede reportar los resultados que
esos datasets habilitan, y la revisión previa al apply
(`docs/campana-medicion/revision-pre-apply-c-165-a-c-169.md`, transversales T1 a T4)
mostró que la versión anterior de este change no podía leer lo que los otros producen,
medía contra un gold circular, especificaba mal el efecto de orden y prometía un IC de
Wilson para un cociente de tiempos.

## What Changes

- **Kappa de Cohen con IC** (`evaluation/kappa.py`): no ponderado, 5 clases
  (`SECTORES_CANONICOS`), sobre la etiqueta primaria `sector_etiquetado`, con exactamente
  dos etiquetadores fijos. IC asintótico con la varianza bajo H1 de Fleiss, Cohen y Everitt
  (1969) e IC bootstrap por casos con la semilla y los remuestreos de `metrics.py`. Se
  reportan además p_o, p_e, PABAK, n y el rótulo de Landis y Koch. Fleiss (más de dos
  etiquetadores) queda fuera del alcance.
- **Exactitud del brazo manual** (`evaluation/campana.py`): estricta y laxa por operador
  con IC de Wilson, reutilizando `resumen_exactitud`/`desglose_exactitud`; agregada con IC
  bootstrap por caso (no Wilson sobre el total de etiquetas); contraste por caso manual vs automatizado con
  `contraste_mcnemar` por operador. La referencia es el consenso del doble etiquetado nuevo
  (casos donde `E1` y `E2` coinciden); el `sector_asignado` original del corpus queda como
  referencia alternativa parametrizable y rotulada; se declara cuántos casos quedaron
  excluidos por discordancia E1 ≠ E2 (sesgo hacia casos fáciles). Cada operador se evalúa
  sobre los casos que etiquetó y McNemar se parea por `(id_caso, id_etiquetador)`. El
  `registro_sujetos` rechaza cualquier persona con más de un rol.
- **Tasa de intervención humana de campaña** (`tasa_intervencion_humana`): proporción de
  casos con IC de Wilson, desglosada por `origen_intervencion` y por `cambio_sector`, y
  contrastada contra la cota 0,15 de la sub-hipótesis 2; proporción del tiempo con IC
  bootstrap por caso del cociente y regla de cobertura mínima del 80 %.
- **Efecto de orden**: de condición (brazo manual primero vs segundo, desde el plan de
  campaña) y de posición (aprendizaje o fatiga del operador), con respuesta la duración del
  brazo manual (`timestamp − inicio` de la planilla, por caso y operador; no el
  `tiempo_manual_s` canónico del corpus), mínimo de 6 casos por grupo y efecto mínimo
  detectable reportado.
- **Evaluación fuera de muestra** (`evaluar_fuera_de_muestra`): corpus independiente con el
  clasificador congelado, bloques rotulados in-sample y out-of-sample, desglose por etapa en
  cascada, verificación de versión y pines del clasificador (commit solo si ambos bloques lo traen) y re-ejecución de
  `verificar_no_solape`.
- **Promoción a públicos** de `_percentil_intervalo` y `_remuestreos_indices` de
  `evaluation/metrics.py` (pasan a `percentil_intervalo` y `remuestreos_indices`), sin
  cambio de comportamiento, para que kappa, exactitud agregada e intervención compartan el
  mismo bootstrap.
- **CLI de solo lectura** `evaluation/analisis_campana.py`, con salidas en
  `evaluation/data/campana/analisis/` (README y SHA-256), y fixtures sintéticos en
  `evaluation/tests/fixtures/campana/`.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `evaluation-framework`: se AGREGAN seis requisitos (kappa con IC; exactitud del brazo
  manual con registro de sujetos y referencia declarada; tasa de intervención humana de
  campaña; efecto de orden de condición y de posición; evaluación fuera de muestra con
  clasificador congelado; ejecución offline, determinista y de solo lectura). No se modifica
  ningún requisito existente.

## Contratos consumidos (c-167 lee, no produce)

- **C1 — planilla de etiquetado** (dueño c-168): `evaluation/data/plantilla_etiquetado.csv`
  con `id_caso`, `id_etiquetador`, `tarea` (`doble_etiquetado` | `brazo_manual`),
  `sector_etiquetado`, `sectores_adicionales_etiquetados` (separador `|`), `inicio` y
  `timestamp` ISO-8601 (en `brazo_manual`, `inicio` es obligatorio y `timestamp` es el fin).
  `doble_etiquetado`: `E1` y `E2` fijos en todos los casos. `brazo_manual`: `O1` y `O2`
  fijos, cada caso con al menos un operador y a lo sumo un registro por
  `(id_caso, id_etiquetador)`. c-167 asume datos validados por
  `evaluation/doble_etiquetado.py::validar_doble_etiquetado` y re-verifica solo lo mínimo.
- **C2 — sujetos y referencia**: `evaluation/data/campana/registro_sujetos.csv`
  (`alias, rol, persona`, con `persona` seudónimo estable `P<n>`; la correspondencia con
  identidades la custodia el director fuera del repo). Operadores `O*` y etiquetadores `E*`
  son personas distintas entre sí, de los dos analistas del consenso original y de los
  autores; el solape se controla por `persona`; referencia por defecto = consenso
  del doble etiquetado nuevo.
- **C5 — export de intervención** (dueño c-165): `evaluation/data/campana/intervenciones.csv`,
  solo con filas intervenidas: el denominador de la tasa (casos de la corrida) se toma de
  `plan_campana.csv` o del sidecar de la corrida, nunca del export; `actor_alias` es un HMAC
  truncado y no se usa como clave de análisis. La métrica backend de c-165 es `tasa_intervencion_backend`; la de c-167, offline y de
  campaña, es `tasa_intervencion_humana` y es la que va a la tesis.
- **C6 — plan de campaña** (dueño c-166): `evaluation/data/campana/plan_campana.csv`
  (`id_caso, posicion, mitad, brazo_primero, modo, seed`).
- **C9 — fuera de muestra** (reparto con c-166): c-166 genera
  `evaluation/data/campana/predicciones_independiente.json` y `evaluation/no_solape.py`;
  c-167 es dueño de `evaluar_fuera_de_muestra` y del reporte.

## Impact

- Código nuevo: `evaluation/kappa.py`, `evaluation/campana.py`, `evaluation/analisis_campana.py`.
- Código modificado: `evaluation/metrics.py` (solo el renombre de dos helpers de bootstrap a
  públicos y la actualización de sus llamadas internas; sin cambio de comportamiento).
- Tests nuevos: `evaluation/tests/test_kappa.py`, `evaluation/tests/test_campana.py`,
  `evaluation/tests/test_analisis_campana.py`; fixtures sintéticos en
  `evaluation/tests/fixtures/campana/` con README que los marca SINTÉTICOS.
- Salidas: `evaluation/data/campana/analisis/` con README y `SHA256SUMS.txt`.
- Dependencias: ninguna nueva. `scipy>=1.13` ya figura en `evaluation/requirements.txt`
  (Mann-Whitney, Spearman, McNemar). Los tests que dependan de scikit-learn usan `importorskip`.
- CI: los tests nuevos viven en `evaluation/tests/` y corren en el job de `evaluation/`,
  offline y sin Gemini.
- Sin cambios en `evaluation/report.md`, `evaluation/predicciones.json`, los números
  canónicos de v9, `docs/Tesis/` ni las cadenas canónicas de sectores.

## Approach

Biblioteca pura y determinista: cada análisis es una función que recibe registros ya
cargados; el CLI solo lee rutas, valida lo mínimo, delega y escribe en la carpeta de salida.
Exactitudes, Wilson, McNemar, Wilcoxon, d_z y MDE se reutilizan de `metrics.py` y
`stats.py`; el único cálculo estadístico nuevo es el kappa (con su varianza asintótica),
más los envoltorios de Mann-Whitney y Spearman sobre scipy.

## Declaración sobre el kappa

El kappa que calcula este change es el de los **etiquetadores nuevos** (`E1`, `E2`) del
doble etiquetado de c-168, sobre la etiqueta primaria. **No es un intervalo de confianza
del kappa 0,87 original**, que se obtuvo con otras personas (los dos analistas del consenso)
y cuya tabla primaria no se conservó. Ambos valores miden la fiabilidad del constructo con
personas distintas; cómo se presentan juntos en la tesis lo decide c-169.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Datos de campo ausentes al implementar | Alta | Tests con fixtures sintéticos; cada sección del análisis sin su dataset se declara "no se obtuvo" con el motivo, sin abortar el resto |
| Contratos de c-165, c-166 o c-168 cambian después de este change | Media | Contratos C1, C5, C6 y C9 citados textualmente; validación mínima con error accionable que nombra la columna o el archivo |
| IC del kappa inestable con n chico | Media | IC asintótico y bootstrap; remuestras degeneradas contadas; "IC bootstrap no computable" si superan el 5 % |
| Lectura de "no significativo" como "sin efecto" | Media | Efecto mínimo detectable reportado junto a cada contraste de orden; rótulo explícito |
| Tocar por error artefactos v9 congelados | Baja | El CLI no importa `main()` ni `generar_reporte`; test de solo lectura; cierre con `git diff --stat` |

## Rollback Plan

Eliminar los tres módulos nuevos, sus tests y fixtures, y revertir el renombre de los dos
helpers en `metrics.py`. No hay migraciones, cambios de esquema ni dependencias nuevas; el
corpus y los artefactos v9 quedan intactos.

## Dependencies

- **c-168** aplicado: esquema C1 y validador `validar_doble_etiquetado`.
- **c-165** aplicado: export C5 (`intervenciones.csv`, solo filas intervenidas) y
  `evaluation/brazo_manual.py` (`reconstruir_posicion_real`, `desvios_respecto_del_plan`),
  que c-167 importa para el efecto de posición.
- **c-166** aplicado: plan C6 (`plan_campana.csv`), `predicciones_independiente.json` y
  `evaluation/no_solape.py::verificar_no_solape` (C9).
- Orden de apply: c-165 (hasta su checkpoint), c-166, c-168, c-167. Las secciones de kappa y
  exactitud manual pueden aplicarse antes que intervención, orden y fuera de muestra si urge
  avanzar, porque no dependen de la migración de c-165 ni del plan de c-166.

## Success Criteria

- [ ] Cada análisis es una función pura cubierta por tests offline sobre fixtures sintéticos.
- [ ] El kappa reproduce el oráculo (κ = 0,642553; SE = 0,083594) y reporta IC asintótico,
      IC bootstrap, p_o, p_e, PABAK, n y rótulo de Landis y Koch.
- [ ] Ningún alias del `registro_sujetos` aparece con más de un rol sin que el análisis falle.
- [ ] La exactitud agregada del brazo manual usa bootstrap por caso, no Wilson sobre el total de etiquetas.
- [ ] La proporción de tiempo de intervención usa bootstrap por caso del cociente, no Wilson.
- [ ] Cada contraste de orden reporta su efecto mínimo detectable.
- [ ] El bloque fuera de muestra aborta si la versión o los pines del clasificador difieren; sin commit in-sample declara la limitación sin abortar.
- [ ] `report.md`, `predicciones.json` y los números v9 quedan intactos (`git diff --stat`).
