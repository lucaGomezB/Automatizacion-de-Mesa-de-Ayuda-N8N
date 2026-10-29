# data/

Esta carpeta contiene el corpus de evaluación del clasificador híbrido.

## Archivos versionados

### `corpus_evaluacion_pseudonimizado.json`

El corpus real de evaluación (200 casos), pseudonimizado por el módulo de C-03.
**SI se versiona** (descripciones genéricas, sin PII residual).

### `Corpus Tesis - Hoja 1 (pseudonimizado).csv`

Corpus de registro pseudonimizado (formato Hoja 1). **SI se versiona**.

### Sidecars de resultados `corpus_resultados*.json`

`corpus_resultados.json` (200 filas) y `corpus_resultados_telefonia.json` (81 filas)
son los sidecars de trazabilidad de los harness de ingesta que corresponden a
corridas completas. **SI se versionan** como evidencia agregada: son libres de PII
por construcción (solo `case_id`, canal, `incidente_id`, sector, marcas temporales
y latencias; sin descripciones de caso). El sidecar `corpus_resultados_n8n.json`
tiene 4 filas locales frente a las 119 de la corrida del 2-10-2026: **NO se versiona**
hasta confirmar cuál artefacto es el autoritativo (pregunta abierta OQ2); `.gitignore`
lo excluye por defecto junto con cualquier otro sidecar del patrón.

## Archivos NO versionados (Ley 25.326)

- `Corpus Tesis.xlsx` y `Corpus Tesis - Hoja 1.csv` — originales
  **pre-pseudonimización**; contienen PII y NUNCA se commitean.
- `corpus_resultados_n8n.json` — sidecar de la ingesta por N8N, pendiente de
  resolver su discrepancia de conteo (4 filas vs 119; OQ2); no se versiona por ahora.

El corpus sintético provisional de 200 casos (`corpus_sintetico_provisional.csv`)
y su andamiaje de generación fueron **eliminados permanentemente** en C-27.

## Esquema JSON

```json
{
  "schema_version": 1,
  "metadata": {"descripcion": "...", "total_casos": 1},
  "casos": [
    {
      "id": "R001",
      "descripcion": "Texto del incidente (pseudonimizado)",
      "canal_origen": "correo",
      "sector_asignado": "Seguridad Informatica",
      "sectores_adicionales": ["Soporte Tecnico Software"],
      "tiempo_manual_s": 75,
      "tiempo_automatizado_s": 30
    }
  ]
}
```

### Campos por caso

| Campo | Tipo | Requerida | Descripción |
|-------|------|-----------|-------------|
| `id` | string | Sí | Identificador único |
| `descripcion` | string | Sí | Texto del incidente (pseudonimizado) |
| `canal_origen` | string | Sí | Canal de entrada (correo, formulario, llamada) |
| `sector_asignado` | string | Sí | Sector principal de verdad fundamental |
| `sectores_adicionales` | array | Sí | Sectores adicionales de verdad (`[]` si no hay) |
| `tiempo_manual_s` | number | Sí | Segundos del flujo manual |
| `tiempo_automatizado_s` | number | Sí | Segundos del flujo automatizado |

Valores válidos para los sectores (exactos, sensibles a mayúsculas, **sin tildes**):

- `Seguridad Informatica`
- `Soporte Tecnico Hardware`
- `Soporte Tecnico Software`
- `Bases de Datos`
- `Sistemas`

`metadata.total_casos` se normaliza a `len(casos)` y se persiste al cargar el
corpus si estaba desincronizado.

## Ejecutar la corrida real

```bash
# Verificar que el archivo esté en la carpeta:
ls data/corpus_evaluacion_pseudonimizado.json

# Ejecutar la evaluación real:
PYTHONPATH=App/Backend python -m evaluation.run_evaluation
```

El reporte real se escribe en `evaluation/report.md`.
