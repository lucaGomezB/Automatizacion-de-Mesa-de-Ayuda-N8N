# evaluation/evidence/

Evidencia congelada del repositorio: predicciones del clasificador híbrido, corridas
de carga y facturación del período de la sonda. Cada snapshot es una copia
byte-idéntica de su fuente en el momento de su publicación, versionada para respaldar
las métricas del Capítulo 7, los costos y la auditoría CONEAU.

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

### `billing-gemini-2026-11-17-18-oficial.csv`

| Campo | Valor |
|-------|-------|
| `sha256` | `7c75fc0128101f93c567060825d56c20f86f3fdc28aad5a1c183649f0d3324a4` |
| Origen | Cloud Billing > Informes (agrupado por Fecha > SKU), "Descargar CSV", 2026-11-18 |
| Período | 2026-11-17 y 2026-11-18 (hora del Pacífico, UTC-8) |
| Servicio / SKU | Gemini API (`AEFD-7695-64FA`); entrada `2F9F-F0E4-699C`, salida `90DC-1471-C3D3`; `gemini-3.6-flash` |
| Total del período | 366.909 tokens (358.336 entrada + 8.573 salida); USD 0,300897 sin impuesto |

Export oficial de Cloud Billing tal como lo emite la consola. No contiene número de proyecto, ID de cuenta ni datos de pago: solo el ID de servicio y los ID de SKU del catálogo público de Google (identificadores del SKU, no de la cuenta). Es la evidencia de gasto del período de las dos corridas de la sonda de latencia con inferencia (`v1.6.1`).

### `billing-gemini-2026-11-17-18-resumen.csv`

| Campo | Valor |
|-------|-------|
| `sha256` | `5ffaf26b5c63d93e439488242397a3ee90cfc55ffd74d923047ad1151c4bf1cd` |
| Origen | resumen derivado del export oficial anterior |
| Contenido | las cuatro filas del export (por fecha y tipo de token), más zona horaria, precio implícito y totales |

Resumen de una página con las mismas cuatro filas del export oficial, más el `precio_implicito_usd_por_millon` (0,75 de entrada y 3,75 de salida, precio introductorio) y los totales del período. Sin datos de cuenta.

**Contraste con `usage_metadata`.** El billing del período da 366.909 tokens (USD 0,300897), mientras la evidencia de la corrida ampliada registra 281.568 tokens (USD 0,23112): un 30 % más en ambos tipos de token, con la misma proporción, atribuible a llamadas que `usage_metadata` no contó (reintentos técnicos, pruebas previas o llamadas fuera de las dos corridas). El precio implícito cierra exacto en el precio introductorio declarado por la tesis, de modo que no es una diferencia de precio. Se registra como total del período con esa explicación; el costo por corrida, desde los tokens.

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
