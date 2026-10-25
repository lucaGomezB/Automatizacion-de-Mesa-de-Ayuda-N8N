# evaluation/evidence/

Evidencia congelada de las predicciones del clasificador híbrido. Cada archivo es
una copia byte-idéntica del cache de predicciones en el momento de su publicación,
versionada para respaldar las métricas del Capítulo 7 y la auditoría CONEAU.

El cache vivo (`evaluation/predicciones.json` y
`evaluation/predicciones_calibracion.json`) permanece excluido del repositorio
(`.gitignore`): es un artefacto regenerable con `generated_at` variable. La evidencia
de esta carpeta es estable, inmutable y citable por su hash.

## Archivos

### `predicciones_hybrid-v3_2026-10-07.json`

| Campo | Valor |
|-------|-------|
| `classifier_version` | `hybrid-v3` |
| `corpus_hash` | `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb` |
| `corpus_count` | 200 |
| `generated_at` | `2026-10-07T22:22:01.947873+00:00` |

Corresponde a la corrida principal de evaluación. Su `corpus_hash` coincide con el
corpus pseudonimizado público actual
(`data/corpus_evaluacion_pseudonimizado.json`, `sha256`
`1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`).

### `predicciones_calibracion_hybrid-v2_2026-10-07.json`

| Campo | Valor |
|-------|-------|
| `classifier_version` | `hybrid-v2` |
| `corpus_hash` | `5f062e1466facd1a522d80c2693d1d256017aae37372c2d288646ba104f46a93` |
| `corpus_count` | 200 |
| `generated_at` | `2026-10-07T20:33:03.438926+00:00` |

Corresponde a la corrida de calibración sobre una versión anterior del clasificador.

> **ADVERTENCIA**: el `corpus_hash` de este snapshot (`5f062e14…`) NO coincide con el
> hash del corpus actual (`1fd17d7e…`). Este archivo documenta un estado ANTERIOR del
> corpus y del clasificador (`hybrid-v2`); NO debe interpretarse como representativo
> del corpus vigente. Úsese únicamente como evidencia histórica de la calibración.

## Contenido de cada archivo

Cada archivo tiene la estructura del formato de cache documentado en la spec
`evaluation-prediction-cache`:

```json
{
  "cache_meta": {
    "corpus_hash": "…",
    "corpus_count": 200,
    "classifier_version": "…",
    "generated_at": "…"
  },
  "predictions": [
    {
      "caso_id": "R001",
      "descripcion": "…",
      "sector_asignado": "Seguridad Informatica",
      "sector_predicho": "Soporte Tecnico Software",
      "confianza": 0.95,
      "etapa": "gemini",
      "sectores_adicionales": []
    }
  ]
}
```

## Recálculo por caso sin invocar Gemini

La evidencia permite recomputar métricas por caso sin invocar al clasificador
pagado. Las predicciones se unen con el corpus pseudonimizado público por
identificador de caso: `caso_id` en las predicciones ↔ `id` en el corpus.

```python
import json

predicciones = json.load(open(
    "evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json"
))
corpus = json.load(open("data/corpus_evaluacion_pseudonimizado.json"))

por_id = {caso["id"]: caso for caso in corpus["casos"]}

for pred in predicciones["predictions"]:
    caso = por_id[pred["caso_id"]]
    # verdad fundamental: caso["sector_asignado"], caso["sectores_adicionales"]
    # predicción: pred["sector_predicho"], pred["sectores_adicionales"]
    ...
```

El campo `descripcion` de cada predicción es idéntico al del corpus público, por lo
que la evidencia no incorpora datos personales nuevos.

## Verificación de fidelidad

La copia es byte a byte idéntica a su archivo de origen en el momento de la
publicación. Para verificarla contra el cache vivo (si estuviera presente):

```bash
sha256sum evaluation/predicciones.json \
          evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json
```
