# evaluation/data/campana/

Esta carpeta guarda la **tabla primaria del doble etiquetado**: la planilla
etiquetador x caso que permite calcular el kappa de Cohen con su intervalo de
confianza. No contiene datos personales (PII) ni la descripción de los casos:
solo alias (`E1`, `E2`), identificadores de caso, sectores canónicos y marcas de
tiempo. El esquema es el de `evaluation/data/plantilla_etiquetado.csv` y el único
validador es `evaluation/doble_etiquetado.py`.

Desde c-166 la carpeta también aloja los artefactos de la campaña contrabalanceada y del
corpus independiente (ver la sección "Artefactos de la campaña contrabalanceada y del
corpus independiente (c-166)", al final).

La conservación de esta tabla es **criterio de aceptación de la campaña**: sin ella
el kappa vuelve a quedar sin intervalo de confianza. El protocolo completo
(sujetos, cegado, codebook, versionado) está en
`docs/campana-medicion/runbook-doble-etiquetado.md`.

## Estado actual

**Doble etiquetado, brazo manual, brazo automatizado (web/correo + telefonía), intervención, entradas del análisis y salidas de `analisis/` versionados.** Están
versionados `plan_campana.csv`, los ocho sub-planes (4 manuales + 4 automatizados,
`subplan_m<mitad>_<brazo>_t<turno>.csv`), `corpus_campana.json` (copia de campaña, con
los tiempos automatizados de los 200 casos; sin nulls), los ocho sidecars de corrida
(`sidecar_m<mitad>-automatizado-t<turno>.json` de web/correo y
`sidecar_m<mitad>-automatizado-t<turno>-tel.json` de telefonía), `registro_sujetos.csv`
(8 filas, sin solapes), `doble_etiquetado.csv` (400 registros
de `E1` y `E2` sobre los 200 casos) y `brazo_manual.csv` (220 registros de `O1` y `O2`
sobre los 200 casos, con 20 de doble cobertura). El test de integridad
(`test_tabla_primaria_versionada_integra`) ya no se omite. Están versionados también
`intervenciones.csv` (147 intervenciones), las dos entradas del análisis
(`plantilla_etiquetado.csv`, `predicciones_in_sample.json`) y las salidas de `analisis/`
(`resultados.json`, `resultados.md`, `SHA256SUMS.txt`), con sus SHA-256 en las tablas de
abajo; el análisis de solo lectura de c-167 corre end-to-end con estas entradas.

## Archivos de esta carpeta

- `doble_etiquetado.csv`: tabla primaria validada (400 registros de `E1` y `E2`
  sobre los 200 casos; ver "Procedencia de la tabla primaria").
- `registro_sujetos.csv`: columnas `alias, rol, persona` (versionado en este PR;
  sin nombres, ver el runbook).
- `*.csv` se versionan con fin de línea LF (`.gitattributes`) para que el SHA-256
  coincida en Windows y Linux.

### Sujetos: los dos analistas originales y la fila A2

El consenso `sector_asignado` del corpus lo fijaron dos analistas originales: `A1` y
`T1` (este último es también autor de la tesis). El `registro_sujetos.csv` no incluye
una fila `A2`: una versión previa de la plantilla la tenía, pero se eliminó al
confirmarse que el segundo analista original es `T1`, que ya figura con el rol
`autor`. La coincidencia analista-autor se declara como limitación en c-169 y no
habilita a `T1` como etiquetador ni operador. El registro queda con 8 filas sin
solapes: `E1`, `E2`, `O1`, `O2`, `A1`, `T1`, `T2`, `T3`.

## Procedencia de la tabla primaria

Completada **al versionar** la tabla, con una línea `- campo: valor` por campo. El
test de integridad lee `sha256` de esta sección y lo compara con el hash real del
archivo.

- archivo: evaluation/data/campana/doble_etiquetado.csv
- sha256: 8b30b15b458bb611a3eff0f45f54731a539dafb5c02a931ebf4d944a7eb47b43
- fecha: 2026-11-04
- corpus: data/corpus_evaluacion_pseudonimizado.json
- corpus_sha256: 1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb
- tarea: doble_etiquetado
- comando_de_validacion: `python -m evaluation.doble_etiquetado --planilla evaluation/data/campana/doble_etiquetado.csv --corpus data/corpus_evaluacion_pseudonimizado.json --tarea doble_etiquetado` (exit 0)
- codebook_sha256: d9777139e9eaffe7903fa63d69d2bee346ff2b43599409aedaaebd21a8be9167
- estado_cegado: cumplido
- motivo_limitacion: no aplica

Significado de cada campo:

- `archivo`: ruta de la tabla (`evaluation/data/campana/doble_etiquetado.csv`).
- `sha256`: SHA-256 del archivo tal como está versionado (LF). Calcularlo con
  `sha256sum evaluation/data/campana/doble_etiquetado.csv`.
- `fecha`: fecha ISO (`AAAA-MM-DD`) en que se versionó.
- `corpus`: corpus contra el que se validó (por ejemplo
  `data/corpus_evaluacion_pseudonimizado.json`) y, en `corpus_sha256`, su SHA-256.
- `tarea`: `doble_etiquetado`.
- `comando_de_validacion`: el comando exacto y su resultado (exit code `0`), por
  ejemplo
  `python -m evaluation.doble_etiquetado --planilla evaluation/data/campana/doble_etiquetado.csv --corpus data/corpus_evaluacion_pseudonimizado.json --tarea doble_etiquetado`.
- `codebook_sha256`: SHA-256 del codebook operativo congelado antes de etiquetar (el
  mismo documento para `E1` y `E2`; ver el runbook).
- `estado_cegado`: `cumplido` | `limitacion_declarada`.
  - `cumplido`: `E1` y `E2` son personas distintas entre sí, de los dos analistas
    originales, de los autores y de los operadores `O*`, y etiquetaron sin ver el
    consenso, las predicciones ni las etiquetas del par.
  - `limitacion_declarada`: no se consiguieron etiquetadores nuevos. En
    `motivo_limitacion` se registra el motivo y los roles solapados. El resultado
    se reporta como limitación y **no** como etiquetado ciego.

## Procedencia de la tabla primaria del corpus independiente (c-191)

Tabla primaria del doble etiquetado `E3`/`E4` sobre los 150 casos del corpus independiente
(campaña de validación fuera de muestra, c-191). Mismo formato `- campo: valor` que la sección
anterior; el test de integridad de c-168 lee solo el primer `- sha256:` del README, que sigue
siendo el de `doble_etiquetado.csv`.

- archivo: evaluation/data/campana/doble_etiquetado_independiente.csv
- sha256: 94dc2d739390a4c874e4ecfa70bf8b52266b752ec20d1e47801f2a93a562f6f7
- fecha: 2026-11-12
- corpus: /home/skywalker/Desktop/campana-hojas/campana_extra/corpus_independiente_trabajo.json (JSON de TRABAJO, fuera del repositorio)
- corpus_sha256: ef09b5b85fd6ace9d1dfdbf28fdde27e311ccca9e5dce25e1246f9332de53339
- corpus_final: evaluation/data/campana/corpus_independiente.json
- corpus_final_sha256: 8cdbec6fc06be3f7c4535f0213919d6d90b69d36e7d820ff97a84b9180cef56d
- tarea: doble_etiquetado
- comando_de_validacion: `python -m evaluation.doble_etiquetado --planilla evaluation/data/campana/doble_etiquetado_independiente.csv --corpus /home/skywalker/Desktop/campana-hojas/campana_extra/corpus_independiente_trabajo.json --tarea doble_etiquetado` (exit 0: `n_casos=150`, `n_registros=300`, `etiquetadores=E3,E4`)
- codebook_sha256: 82767d9510e0f93f90002ee3a222a2df0386fe723ddac26fc0679dc443774e36
- estado_cegado: cumplido
- motivo_limitacion: no aplica

La validación corre contra el JSON de TRABAJO (150 casos) porque el JSON final solo contiene
los 103 casos con consenso y el validador rechazaría los 47 ids discordantes como inexistentes.
El `codebook_sha256` es el del codebook entregado a `E3`/`E4`; difiere del de `E1`/`E2`
únicamente en el encabezado que identifica la campaña.

### Corrida del clasificador congelado sobre el corpus independiente (c-191)

La corrida paga de c-191 clasificó `corpus_independiente.json` (103 casos) con el clasificador
`hybrid-v3` congelado y escribió `predicciones_independiente.json` y `reporte_independiente.md`.
Su `cache_meta` registra el `commit` de `HEAD` al generar el cache y el resultado del control de
congelamiento de la tarea 0.5 (sección 6 del runbook del corpus independiente). Mismo formato
`- campo: valor` que la sección de referencia in-sample, con nombres propios.

- corrida_independiente_commit: 561b3c4 (HEAD al generar el cache, `git rev-parse --short HEAD`)
- corrida_independiente_classifier_version: hybrid-v3
- corrida_independiente_generated_at: 2026-11-12T23:58:14.687248+00:00
- corrida_independiente_corpus_hash: 8cdbec6fc06be3f7c4535f0213919d6d90b69d36e7d820ff97a84b9180cef56d (coincide con `corpus_independiente.json`)
- corrida_independiente_pines: {"google_genai": "2.34.0", "modelo": "gemini-3.6-flash"} (versión **instalada**; el modelo coincide con el del in-sample)
- corrida_independiente_control_congelamiento: `git diff bf5e099 HEAD -- App/Backend/app/classifiers docs/prompt_gemini.txt App/Backend/app/constants.py App/Backend/app/config/settings.py` solo muestra diferencias ajenas a la clasificación: docstrings/comentarios y el import perezoso del paquete (PEP 562) en `classifiers`; `CANAL_CORREO`/`ORIGEN_*` de c-165 en `constants.py`; seguridad/autenticación (claves, JWT, cookies, lockout, MFA, CORS) en `settings.py`; `docs/prompt_gemini.txt` sin diferencias. Ninguna diferencia cambia reglas, `KEYWORD_MAP`, el prompt, el vocabulario de sectores, los umbrales ni los parámetros de Gemini (control 0.5, verificado el 2026-11-12).

El clasificador queda congelado en `hybrid-v3`: el `classifier_version` coincide con el de la
referencia in-sample y el `modelo` de `pines` coincide exactamente (`gemini-3.6-flash`); la
versión instalada de `google-genai` (`2.34.0`) cumple el rango declarado del in-sample
(`>=2.20.0`). No hubo recalibración posterior (sección 6 del runbook).

**Re-ejecución con el stack entregado (2026-11-12).** El entorno se actualizó de `google-genai`
`2.32.0` a **`2.34.0`** para satisfacer el pin entregado (`openspec/config.yaml`,
`stack.inference`: `google-genai >=2.33,<3`), y la corrida paga se re-ejecutó con `--force`, de
modo que el cache registra ahora la versión del stack entregado. No cambian el `corpus_hash`
(`8cdbec6f…`), el `commit` (`561b3c4`), el `classifier_version` (`hybrid-v3`) ni el `modelo`
(`gemini-3.6-flash`); cambian solo `generated_at` y `pines.google_genai`. El SHA-256 de
`predicciones_independiente.json` y de `reporte_independiente.md` de la tabla de abajo
corresponde a esta re-ejecución.

## Artefactos de la campaña contrabalanceada y del corpus independiente (c-166)

Esta carpeta también aloja, desde c-166, los artefactos de la campaña contrabalanceada y de la clasificación del corpus independiente. Ninguno contiene datos personales ni sobrescribe un artefacto de la v9: los harnesses y el runner abortan antes de escribir si se los apunta a `data/corpus_evaluacion_pseudonimizado.json`, a `data/corpus_resultados*.json`, a `evaluation/predicciones.json` o a `evaluation/report.md`. Los protocolos están en `docs/campana-medicion/runbook-campana-contrabalanceada.md` y `docs/campana-medicion/runbook-corpus-independiente.md`.

| Archivo | Qué es | Cómo se genera |
|---|---|---|
| `plan_campana.csv` | Plan de campaña por caso: `id_caso,posicion,mitad,brazo_primero,modo,seed` | `python -m evaluation.plan_campana generar` |
| `subplan_m<mitad>_<brazo>_t<turno>.csv` | Sub-plan de un turno (conserva la `posicion` global); se versionan los efectivamente usados | `python -m evaluation.plan_campana subplan` |
| `corpus_campana.json` | Copia de campaña del corpus canónico con `tiempo_automatizado_s` y `tiempo_manual_s` en `null`: es el `--json` de las corridas con `--plan` | `python -m evaluation.plan_campana preparar-corpus` |
| `sidecar_<id_corrida>.json` | Sidecar propio de una corrida (sin descripciones), con `orden`, `posicion`, `mitad`, `brazo_primero` e `id_corrida` por caso | `--sidecar` de los harnesses |
| `sidecar_<id_corrida>.json.plan.csv` | Plan que dejó `--orden` junto al sidecar (solo si se usó ese atajo) | `--orden` de los harnesses |
| `corpus_independiente.json` | Corpus independiente pseudonimizado (ids `I001..`) con la referencia por consenso de `E3`/`E4` (103 casos; los 47 discordantes quedan excluidos y declarados), solo en su forma pseudonimizada; ruta recomendada | runbook del corpus independiente |
| `predicciones_independiente.json` | Cache de predicciones del corpus independiente; su `cache_meta` trae `corpus_hash`, `corpus_count`, `classifier_version`, `generated_at`, `commit` y `pines` | `python -m evaluation.run_evaluation --corpus ... --predicciones ... --reporte ...` |
| `reporte_independiente.md` | Reporte propio de esa corrida (ruta recomendada de `--reporte`) | idem |

La copia de campaña tiene más valores nulos que el corpus canónico: es intencional. Un caso no medido en la campaña queda nulo y no hereda el tiempo canónico (`merge_evaluation_json` solo escribe mediciones válidas).

### SHA-256 por archivo

Al versionar cada archivo se completa su SHA-256 (en minúsculas, calculado sobre el archivo tal como queda versionado, con fin de línea LF: `.gitattributes` lo fija para los `*.csv`, `*.json` y `*.md` de esta carpeta; un archivo generado en Windows con CRLF se normaliza antes con `sed -i 's/\r$//' <archivo>`), con el mismo patrón que `evaluation/evidence/README.md`. Mientras un archivo no exista, su hash queda en `pendiente`. Esta tabla no usa el formato `- campo: valor` de la sección de procedencia de la tabla primaria, que lee el test de integridad de c-168.

| Archivo | SHA-256 |
|---|---|
| `plan_campana.csv` | b619a734092cbbf2b676636386e4b27bdbeaee76df3f97a19e4b7d1beeb43243 |
| `registro_sujetos.csv` | ab17eb2b6e660b78d206d130c21fac06739ba5512d2ac37d09cf532c2a3d36da |
| `corpus_campana.json` | 99bbe84b90b6ba66b34aae08c85bd318cd0e9600ad540e58b1a4bd8eccec06a5 |
| `doble_etiquetado_independiente.csv` | 94dc2d739390a4c874e4ecfa70bf8b52266b752ec20d1e47801f2a93a562f6f7 |
| `corpus_independiente.json` | 8cdbec6fc06be3f7c4535f0213919d6d90b69d36e7d820ff97a84b9180cef56d |
| `predicciones_independiente.json` | d5ee19f7b0bf2b56a00026a1bd33a2e11ffeb9b224b6a8efa553460895a915a4 |
| `reporte_independiente.md` | 304dffcf4afdf1655c4ff7d9a6906d2ba8e134b6926281d65ca0465c629fbf92 |
| `plantilla_etiquetado.csv` | c35a58b60aca98dbc5fd03ad280fbba2f8baf2d56444ba7982ada0715f8ccd09 |
| `predicciones_in_sample.json` | 89cf956e82f660dd8675a2d23b7b4d17efd62da542c0ba35bea28e0e54572ede |
| `subplan_m1_manual_t1.csv` | 8d42417274934764c24774d10bbbca8ac47807e1d2960a22167ddb564933c41a |
| `subplan_m1_manual_t2.csv` | 30d801b5aa142005402fda2b99e8d8f405ea2b95fa7f773843be4b324e0a5d6c |
| `subplan_m2_manual_t1.csv` | 7dac79db810566f6f351ed28ce0f0a6ff4563a2f81eb03d0fbc86f0bb621438d |
| `subplan_m2_manual_t2.csv` | 8c7de56298cb573c60c59c4d5438278b9ceb9b3fb3ffc3cad885cff0eef057f9 |
| `subplan_m1_automatizado_t1.csv` | 30d801b5aa142005402fda2b99e8d8f405ea2b95fa7f773843be4b324e0a5d6c |
| `subplan_m1_automatizado_t2.csv` | 8d42417274934764c24774d10bbbca8ac47807e1d2960a22167ddb564933c41a |
| `subplan_m2_automatizado_t1.csv` | 8c7de56298cb573c60c59c4d5438278b9ceb9b3fb3ffc3cad885cff0eef057f9 |
| `subplan_m2_automatizado_t2.csv` | 7dac79db810566f6f351ed28ce0f0a6ff4563a2f81eb03d0fbc86f0bb621438d |
| `sidecar_m1-automatizado-t1.json` | d368eff0366e66c0c94cd8d878a5fc46cf23d58c845305812c47031516606bf2 |
| `sidecar_m1-automatizado-t2.json` | 9fb73e9dca813d543450cf67dd48de04a4b3eb4d61748e8562144fbcefc0844e |
| `sidecar_m2-automatizado-t1.json` | dc24315b0c7ae56e5e991dff05ad32378c4e6aa49501c7166347fbb20bc62311 |
| `sidecar_m2-automatizado-t2.json` | affea49637de4c5189af8c0008984315d94038e8d9915481c323f3e91530d07a |
| `sidecar_m1-automatizado-t1-tel.json` | 33a6b435d2e2a6fc6aec3a5a0abae77507de773a30001d1c2a6c85b52ae66875 |
| `sidecar_m1-automatizado-t2-tel.json` | 15c3e45bfb9ef785aeae7fc1cf462951ecb3850f908f0071f70a74b56a66f801 |
| `sidecar_m2-automatizado-t1-tel.json` | 603f4509519874e7255a4e59bfe2246ce08bee21abc2b3da595bdc106b27594a |
| `sidecar_m2-automatizado-t2-tel.json` | cc885c4b48f5b5c2016b95a81866b728876f015d1ab245650bdd4bd0469c7d57 |

Los datos de la campaña se citan desde `evaluation/data/README.md`, que describe el resto de esta jerarquía.

### Submuestra con doble cobertura (criterio de la campaña)

El reparto por defecto del brazo manual es `O1` = mitad 1 y `O2` = mitad 2, sin casos
compartidos. Para poder medir además el acuerdo entre operadores se fijó, antes de
empezar, una **submuestra con doble cobertura**:

- **Criterio**: un caso de cada diez por `posicion` dentro de cada mitad. Mitad 1:
  posiciones 10, 20, 30, 40, 50, 60, 70, 80, 90 y 100. Mitad 2: posiciones 110, 120,
  130, 140, 150, 160, 170, 180, 190 y 200. Son 20 casos en total.
- **Reparto**: cada operador clasifica su mitad completa más los 10 casos muestreados
  de la otra mitad. `O1` recibe 110 casos (100 de la mitad 1 + 10 de la mitad 2) y
  `O2` recibe 110 casos (100 de la mitad 2 + 10 de la mitad 1).
- **Orden**: cada hoja respeta el orden global del plan (por `posicion`), filtrado a
  los casos asignados. Los 20 casos de doble cobertura quedan con dos registros en la
  planilla, uno por operador.
- **Uso**: el acuerdo entre operadores se calcula sobre esos 20 casos; no reemplaza al
  kappa de `E1`/`E2`, que sigue siendo la medida principal. Las hojas con doble
  cobertura se generan fuera del repositorio, igual que el resto de las hojas de campo.

## Referencia in-sample de la validación fuera de muestra (c-166)

La corrida in-sample de referencia es la de `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`, copia congelada del cache de v9 (`generated_at` `2026-10-07T22:22:01Z`; evidencia publicada en `384d23f`, c-143). El análisis de c-167 la compara con `predicciones_independiente.json` y recibe estos valores como parámetro (`pines_in_sample`). Esta sección usa el formato `- campo: valor`, con nombres distintos de los de la procedencia de la tabla primaria.

- classifier_version_in_sample: hybrid-v3
- commit_in_sample: no registrado en la generación (2026-10-07); evidencia publicada en 384d23f (c-143)
- pines_in_sample: google_genai >=2.20.0 (rango declarado, versión instalada no registrada); modelo gemini-3.6-flash

Valor del parámetro `pines_in_sample` de c-167 (el `google_genai` del in-sample es un **rango declarado**, no una versión instalada):

```json
{"google_genai": ">=2.20.0", "modelo": "gemini-3.6-flash"}
```

### Fuentes de los pines

1. **`openspec/config.yaml`, `stack.inference`**: hoy declara `Gemini 3.6 Flash (google-genai >=2.33,<3)`. El modelo coincide con el de v9; el rango de `google-genai` es el de la configuración **entregada** (`v1.2.7`), no el de la corrida in-sample.
2. **Anexo B de la tesis (v10), Tabla "Configuración evaluada y configuración entregada"** (`docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`, etiqueta `tab:configuracion-evaluada-entregada`): la configuración evaluada es la del commit `bf5e099` (2026-10-07), con `google-genai >=2.20.0`, y el modelo `gemini-3.6-flash` figura "sin cambios" entre la evaluada y la entregada.

Verificación contra el commit evaluado: `git show bf5e099:App/Backend/requirements.txt` declara `google-genai>=2.20.0`, `git show bf5e099:App/Backend/app/config/settings.py` fija `gemini_model = "gemini-3.6-flash"` y `git show bf5e099:App/Backend/app/constants.py` fija `HYBRID_CACHE_VERSION = "hybrid-v3"`. En ese mismo commit `openspec/config.yaml` todavía decía `Gemini 2.5 Flash (google-genai >= 1.0)`: la fuente 1 se actualizó después y **no describe** la corrida de v9.

**Discrepancia declarada**: las dos fuentes difieren en el rango de `google-genai` (`>=2.20.0` evaluada frente a `>=2.33,<3` entregada). Para v9 vale la evaluada (fuente 2 y `git show bf5e099`); el rango de `openspec/config.yaml` es el vigente y se usa para el cache independiente solo como contexto.

### Limitación declarada

La evidencia congelada no registró `commit` ni `pines`: su `cache_meta` trae solo `corpus_hash`, `corpus_count`, `classifier_version` y `generated_at`. Por eso:

- La comparabilidad in-sample/out-of-sample se verifica por `classifier_version` idéntico (`hybrid-v3`) y por `pines`: el `modelo` debe coincidir exactamente. El in-sample solo conserva el **rango** declarado de `google-genai`, mientras que el cache independiente registra la versión **instalada**: la igualdad exacta de versiones instaladas no es verificable, y lo comprobable es que la versión del cache independiente cumpla el rango del in-sample; esa versión se informa junto con los resultados.
- El `commit` es obligatorio solo en el cache independiente (se registra con `git rev-parse --short HEAD` al generarlo y la corrida falla antes de clasificar si no puede obtenerse). En el in-sample no se puede recuperar el commit de generación: solo se sabe que la cascada `hybrid-v3` está versionada desde `bf5e099` y que la evidencia se publicó en `384d23f`.

## Export de intervenciones (c-165)

`intervenciones.csv` es el dataset de intervención humana de la campaña: lo produce `App/Backend/scripts/exportar_intervenciones.py` a partir de `clasificacion_log` y lo lee c-167 para la `tasa_intervencion_humana` y la proporción de tiempo. No contiene datos personales: el actor es un alias derivado con clave. El protocolo (cuándo y cómo se produce y cómo se verifica) está en `docs/campana-medicion/runbook-brazo-manual-e-intervencion.md`.

Columnas, en este orden: `id_caso, incidente_id, log_id, origen_intervencion, intervencion_inicio_en, validado_en, duracion_s, sector_predicho, sector_validado, cambio_sector, actor_alias`.

- Una fila por log **intervenido** (`validado_en` no nulo), ordenada por `log_id`. Los logs legados (sector validado sin `validado_en`, anteriores a la migración 024) no se exportan: el resumen del comando informa cuántos quedaron afuera.
- `id_caso` sale del sidecar de la corrida (`case_id`) por `incidente_id`; queda vacío si el incidente no figura en los sidecars o figura en dos casos distintos. El denominador de la tasa **no** sale de este archivo: c-167 lo toma de `plan_campana.csv` o del sidecar de la corrida.
- `intervencion_inicio_en` y `validado_en` son ISO-8601 en UTC con zona (`+00:00`). `duracion_s` es `validado_en - intervencion_inicio_en` en segundos; queda vacía si falta el inicio o si da negativa (reloj del cliente adelantado).
- `cambio_sector` es `true` o `false` (un sector predicho nulo cuenta como cambio). `origen_intervencion` es `gate`, `muestreo` o `rederivacion`; `completado_manual` está reservado y no tiene escritor.
- `actor_alias` es el HMAC-SHA256 del id del empleado con la clave de la variable de entorno `INTERVENCION_EXPORT_HMAC_KEY`, truncado a 12 hex; vacío si no hay actor. La clave es secreta, no se versiona ni se imprime, y debe ser **la misma** en todas las corridas de la campaña para que el alias sea estable. El archivo no trae nombre, email, teléfono, legajo ni el id del empleado.

Comando (desde `App/Backend`, con la variable definida en el entorno de esa terminal):

```bash
python -m scripts.exportar_intervenciones \
  --sidecar ../../evaluation/data/campana/sidecar_<id_corrida>.json \
  --desde AAAA-MM-DD --hasta AAAA-MM-DD \
  --salida ../../evaluation/data/campana/intervenciones.csv
```

`--sidecar` se repite una vez por corrida y `--desde`/`--hasta` acotan los logs por su `created_at` (días de negocio, ambos inclusivos). El comando se niega a escribir sobre `data/corpus_evaluacion_pseudonimizado.json`, `data/corpus_resultados*.json`, `evaluation/predicciones.json` y `evaluation/evidence/`.

Procedencia del export (completar **al versionar** `intervenciones.csv`; formato `- campo: valor`, con nombres propios para no mezclarse con los de la tabla primaria):

- intervenciones_archivo: evaluation/data/campana/intervenciones.csv
- intervenciones_sha256: eccc094d46d5ad301296428885114e298f52efb0666be4f61c2e6a266d340ba3
- intervenciones_fecha: 2026-11-08
- intervenciones_comando: (desde App/Backend; DATABASE_URL apuntando a la base de campana mesa_de_ayuda_campana) ARGS=""; for f in ../../evaluation/data/campana/sidecar_*.json; do ARGS="$ARGS --sidecar $f"; done; python -m scripts.exportar_intervenciones $ARGS --desde 2026-11-01 --hasta 2026-11-30 --salida ../../evaluation/data/campana/intervenciones.csv
- intervenciones_rango: 2026-11-01 a 2026-11-30 (dias de negocio, ambos inclusivos, por created_at del log)
- intervenciones_legados_excluidos: 0

Declaraciones del export (runbook §5.5): sin vinculo (`id_caso` vacio) 0 de 147 (0 ambiguos); sin `duracion_s` 9 de 147 (cobertura 138/147 = 93,9%), todas intervenciones de O1 sin `intervencion_inicio_en` (0 por inicio posterior a la validacion), hechas con una imagen del frontend previa a c-165 que no enviaba el inicio, se declaran y no se reescriben; el denominador de la tasa no sale de este export, c-167 lo toma de `plan_campana.csv` o del sidecar de la corrida.

| Archivo | SHA-256 |
|---|---|
| `intervenciones.csv` | eccc094d46d5ad301296428885114e298f52efb0666be4f61c2e6a266d340ba3 |

### Planilla del brazo manual (c-165)

`brazo_manual.csv` es la planilla del brazo manual (`tarea = brazo_manual`, operadores `O1` y `O2`, con `inicio` y `timestamp` obligatorios en cada fila) que pasó `python -m evaluation.doble_etiquetado --planilla evaluation/data/campana/brazo_manual.csv --corpus data/corpus_evaluacion_pseudonimizado.json --tarea brazo_manual` con exit code `0`. El procedimiento (sujetos, reparto, plan, aceptación) está en `docs/campana-medicion/runbook-brazo-manual-e-intervencion.md`. No contiene datos personales: solo alias de operador, identificadores de caso, sectores canónicos y marcas de tiempo. Versionada el 2026-11-05 (220 registros). **Desvíos de posición: 196 de 220** (98 por operador), sistemáticos y no ruido: las hojas de campo se armaron como una hoja única de 110 casos por operador ordenada por `posicion` global, no como las dos hojas por sub-plan (turno 1 -> turno 2) que describe el runbook §2.3/§3.2; los operadores siguieron su hoja al pie de la letra. El runbook §4.2 prevé los desvíos y no corrige la planilla: se informan tal cual y el análisis los trata como covariable.

- brazo_manual_desvios_informados: 196

| Archivo | SHA-256 |
|---|---|
| `brazo_manual.csv` | 25ef12ba7e4c27ba5489d3daff099c697416d996858299e25ffa57dfa2a4d46f |

## Entradas del análisis de campaña (c-170)

El análisis de solo lectura de c-167 (`evaluation/analisis_campana.py`) espera dos entradas en esta carpeta que ningún runbook producía. Las ensambla `evaluation/preparar_entradas_analisis.py` (offline, TDD), el único camino documentado para generarlas:

```bash
python -m evaluation.preparar_entradas_analisis \
  --entrada evaluation/data/campana \
  --corpus data/corpus_evaluacion_pseudonimizado.json \
  --cache-in-sample evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json
```

| Entrada | Qué es | Procedencia (fuente) |
|---|---|---|
| `plantilla_etiquetado.csv` | Unión C1, bajo un único encabezado, de `doble_etiquetado.csv` (`tarea = doble_etiquetado`) y `brazo_manual.csv` (`tarea = brazo_manual`), en el orden de origen; LF y UTF-8 sin BOM | `evaluation/data/campana/doble_etiquetado.csv` + `evaluation/data/campana/brazo_manual.csv`, re-validadas por tarea con `python -m evaluation.doble_etiquetado` |
| `predicciones_in_sample.json` | Copia **byte a byte** del cache congelado de v9 (referencia in-sample); la fuente es de solo lectura y nunca se regenera | `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` |

El helper escribe LF sin BOM, imprime el SHA-256 de cada salida y su procedencia (fuente y hash de la fuente), y aborta con un error accionable que nombra el archivo (y la `tarea`) si una fuente falta o no pasa el validador. Se niega a escribir sobre un artefacto congelado, sobre `evaluation/evidence/**` o sobre sus propias fuentes. Con las mismas fuentes, dos corridas producen salidas byte a byte idénticas; por eso `predicciones_in_sample.json` comparte el SHA-256 de la fuente congelada.

SHA-256 y procedencia (completar **al versionar** la campaña, formato `- campo: valor`):

- entradas_analisis_planilla_archivo: evaluation/data/campana/plantilla_etiquetado.csv
- entradas_analisis_planilla_sha256: c35a58b60aca98dbc5fd03ad280fbba2f8baf2d56444ba7982ada0715f8ccd09
- entradas_analisis_planilla_fuentes: doble_etiquetado.csv + brazo_manual.csv (sus SHA-256 en las filas de arriba)
- entradas_analisis_in_sample_archivo: evaluation/data/campana/predicciones_in_sample.json
- entradas_analisis_in_sample_sha256: 89cf956e82f660dd8675a2d23b7b4d17efd62da542c0ba35bea28e0e54572ede (coincide con el de evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json)
- entradas_analisis_fecha: 2026-11-08
- entradas_analisis_comando: `python -m evaluation.preparar_entradas_analisis --entrada evaluation/data/campana --corpus data/corpus_evaluacion_pseudonimizado.json --cache-in-sample evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`

### Gate de c-169 (tarea 0.2)

La recomendación de esta sección se aplicó en c-170 (commit `8a72623`): el gate de
c-169 exige también `plantilla_etiquetado.csv` y `predicciones_in_sample.json`, con su
SHA-256 coincidente, porque el análisis de c-167 no se puede correr end-to-end sin
ellas.
