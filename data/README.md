# data/

Esta carpeta contiene el corpus de evaluación del clasificador híbrido.

## Archivos

### `corpus_evaluacion_pseudonimizado.json` — NO trackeado en git

El corpus real de evaluación, pseudonimizado por el módulo de C-03.

**No está en git por privacidad** (aunque está pseudonimizado, contiene
patrones de incidentes internos de la organización). Se coloca manualmente
antes de ejecutar la corrida real.

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
