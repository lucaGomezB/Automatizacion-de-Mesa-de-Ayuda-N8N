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

**Pendiente de campaña.** Todavía no existe `doble_etiquetado.csv`: el etiquetado
real corre fuera del repositorio y la tabla se agrega después, siguiendo el
runbook. Mientras el archivo no exista, el test de integridad
(`test_tabla_primaria_versionada_integra`) se omite.

## Archivos de esta carpeta

- `doble_etiquetado.csv`: tabla primaria validada (se agrega después de la campaña).
- `registro_sujetos.csv`: columnas `alias, rol, persona` (se agrega después de la
  campaña; sin nombres, ver el runbook).
- `*.csv` se versionan con fin de línea LF (`.gitattributes`) para que el SHA-256
  coincida en Windows y Linux.

## Procedencia de la tabla primaria

Completar **al versionar** la tabla, con una línea `- campo: valor` por campo. El
test de integridad lee `sha256` de esta sección y lo compara con el hash real del
archivo. Mientras no exista la tabla, los valores quedan en `pendiente`.

- archivo: pendiente
- sha256: pendiente
- fecha: pendiente
- corpus: pendiente
- corpus_sha256: pendiente
- tarea: pendiente
- comando_de_validacion: pendiente
- codebook_sha256: pendiente
- estado_cegado: pendiente
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

## Artefactos de la campaña contrabalanceada y del corpus independiente (c-166)

Esta carpeta también aloja, desde c-166, los artefactos de la campaña contrabalanceada y de la clasificación del corpus independiente. Ninguno contiene datos personales ni sobrescribe un artefacto de la v9: los harnesses y el runner abortan antes de escribir si se los apunta a `data/corpus_evaluacion_pseudonimizado.json`, a `data/corpus_resultados*.json`, a `evaluation/predicciones.json` o a `evaluation/report.md`. Los protocolos están en `docs/campana-medicion/runbook-campana-contrabalanceada.md` y `docs/campana-medicion/runbook-corpus-independiente.md`.

| Archivo | Qué es | Cómo se genera |
|---|---|---|
| `plan_campana.csv` | Plan de campaña por caso: `id_caso,posicion,mitad,brazo_primero,modo,seed` | `python -m evaluation.plan_campana generar` |
| `subplan_m<mitad>_<brazo>_t<turno>.csv` | Sub-plan de un turno (conserva la `posicion` global); se versionan los efectivamente usados | `python -m evaluation.plan_campana subplan` |
| `corpus_campana.json` | Copia de campaña del corpus canónico con `tiempo_automatizado_s` y `tiempo_manual_s` en `null`: es el `--json` de las corridas con `--plan` | `python -m evaluation.plan_campana preparar-corpus` |
| `sidecar_<id_corrida>.json` | Sidecar propio de una corrida (sin descripciones), con `orden`, `posicion`, `mitad`, `brazo_primero` e `id_corrida` por caso | `--sidecar` de los harnesses |
| `sidecar_<id_corrida>.json.plan.csv` | Plan que dejó `--orden` junto al sidecar (solo si se usó ese atajo) | `--orden` de los harnesses |
| `corpus_independiente.json` | Corpus independiente pseudonimizado (ids `I001..`), solo en su forma pseudonimizada; ruta recomendada | runbook del corpus independiente |
| `predicciones_independiente.json` | Cache de predicciones del corpus independiente; su `cache_meta` trae `corpus_hash`, `corpus_count`, `classifier_version`, `generated_at`, `commit` y `pines` | `python -m evaluation.run_evaluation --corpus ... --predicciones ... --reporte ...` |
| `reporte_independiente.md` | Reporte propio de esa corrida (ruta recomendada de `--reporte`) | idem |

La copia de campaña tiene más valores nulos que el corpus canónico: es intencional. Un caso no medido en la campaña queda nulo y no hereda el tiempo canónico (`merge_evaluation_json` solo escribe mediciones válidas).

### SHA-256 por archivo

Al versionar cada archivo se completa su SHA-256 (en minúsculas, calculado sobre el archivo tal como queda versionado, con fin de línea LF: `.gitattributes` lo fija para los `*.csv`, `*.json` y `*.md` de esta carpeta; un archivo generado en Windows con CRLF se normaliza antes con `sed -i 's/$//' <archivo>`), con el mismo patrón que `evaluation/evidence/README.md`. Mientras un archivo no exista, su hash queda en `pendiente`. Esta tabla no usa el formato `- campo: valor` de la sección de procedencia de la tabla primaria, que lee el test de integridad de c-168.

| Archivo | SHA-256 |
|---|---|
| `plan_campana.csv` | pendiente |
| `corpus_campana.json` | pendiente |
| `corpus_independiente.json` | pendiente |
| `predicciones_independiente.json` | pendiente |
| `reporte_independiente.md` | pendiente |
| cada `sidecar_<id_corrida>.json` y `subplan_*.csv` usado | pendiente (una fila por archivo, al versionarlo) |

Los datos de la campaña se citan desde `evaluation/data/README.md`, que describe el resto de esta jerarquía.

## Referencia in-sample de la validación fuera de muestra (c-166)

La corrida in-sample de referencia es la de `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`, copia congelada del cache de v9 (`generated_at` `2026-10-07T22:22:01Z`; evidencia publicada en `fec4c42`, c-143). El análisis de c-167 la compara con `predicciones_independiente.json` y recibe estos valores como parámetro (`pines_in_sample`). Esta sección usa el formato `- campo: valor`, con nombres distintos de los de la procedencia de la tabla primaria.

- classifier_version_in_sample: hybrid-v3
- commit_in_sample: no registrado en la generación (2026-10-07); evidencia publicada en fec4c42 (c-143)
- pines_in_sample: google_genai >=2.20.0 (rango declarado, versión instalada no registrada); modelo gemini-3.6-flash

Valor del parámetro `pines_in_sample` de c-167 (el `google_genai` del in-sample es un **rango declarado**, no una versión instalada):

```json
{"google_genai": ">=2.20.0", "modelo": "gemini-3.6-flash"}
```

### Fuentes de los pines

1. **`openspec/config.yaml`, `stack.inference`**: hoy declara `Gemini 3.6 Flash (google-genai >=2.33,<3)`. El modelo coincide con el de v9; el rango de `google-genai` es el de la configuración **entregada** (`v1.2.7`), no el de la corrida in-sample.
2. **Anexo B de la tesis (v10), Tabla "Configuración evaluada y configuración entregada"** (`docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`, etiqueta `tab:configuracion-evaluada-entregada`): la configuración evaluada es la del commit `d6bb474` (2026-10-07), con `google-genai >=2.20.0`, y el modelo `gemini-3.6-flash` figura "sin cambios" entre la evaluada y la entregada.

Verificación contra el commit evaluado: `git show d6bb474:App/Backend/requirements.txt` declara `google-genai>=2.20.0`, `git show d6bb474:App/Backend/app/config/settings.py` fija `gemini_model = "gemini-3.6-flash"` y `git show d6bb474:App/Backend/app/constants.py` fija `HYBRID_CACHE_VERSION = "hybrid-v3"`. En ese mismo commit `openspec/config.yaml` todavía decía `Gemini 2.5 Flash (google-genai >= 1.0)`: la fuente 1 se actualizó después y **no describe** la corrida de v9.

**Discrepancia declarada**: las dos fuentes difieren en el rango de `google-genai` (`>=2.20.0` evaluada frente a `>=2.33,<3` entregada). Para v9 vale la evaluada (fuente 2 y `git show d6bb474`); el rango de `openspec/config.yaml` es el vigente y se usa para el cache independiente solo como contexto.

### Limitación declarada

La evidencia congelada no registró `commit` ni `pines`: su `cache_meta` trae solo `corpus_hash`, `corpus_count`, `classifier_version` y `generated_at`. Por eso:

- La comparabilidad in-sample/out-of-sample se verifica por `classifier_version` idéntico (`hybrid-v3`) y por `pines`: el `modelo` debe coincidir exactamente. El in-sample solo conserva el **rango** declarado de `google-genai`, mientras que el cache independiente registra la versión **instalada**: la igualdad exacta de versiones instaladas no es verificable, y lo comprobable es que la versión del cache independiente cumpla el rango del in-sample; esa versión se informa junto con los resultados.
- El `commit` es obligatorio solo en el cache independiente (se registra con `git rev-parse --short HEAD` al generarlo y la corrida falla antes de clasificar si no puede obtenerse). En el in-sample no se puede recuperar el commit de generación: solo se sabe que la cascada `hybrid-v3` está versionada desde `d6bb474` y que la evidencia se publicó en `fec4c42`.
