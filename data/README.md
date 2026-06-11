# data/

Esta carpeta contiene los corpus de evaluación del clasificador híbrido.

## Archivos

### `corpus_sintetico_provisional.csv` — TRACKEADO en git

200 casos sintéticos generados por Claude (no por Gemini) para validar el
pipeline de evaluación antes de disponer del corpus real.

**No contiene PII real.** Usa tokens del pseudonimizador donde aplica:
`[HOST]`, `[PERSONA]`, `[EMAIL]`, `[TELEFONO]`.

Distribución (muestreo estratificado de la tesis §4.4):
- **Sistemas**: 82 casos
- **Operaciones**: 64 casos
- **Soporte Técnico**: 54 casos

**Advertencia:** los números de métricas generados con este corpus NO son
válidos para el Capítulo 7 de la tesis. Ver `evaluation/README.md` para detalle.

---

### `corpus_evaluacion_pseudonimizado.csv` — NO trackeado en git

El corpus real de 200 casos recolectados de incidentes productivos y
pseudonimizados por el módulo de C-03.

**No está en git por privacidad** (aunque está pseudonimizado, contiene
patrones de incidentes internos de la organización). Se coloca manualmente
antes de ejecutar la corrida real.

Para la corrida real:

```bash
# Verificar que el archivo esté en la carpeta:
ls data/corpus_evaluacion_pseudonimizado.csv

# Ejecutar la evaluación real:
PYTHONPATH=Gestion_Incidentes python -m evaluation.run_evaluation
```

El reporte real se escribe en `evaluation/report.md` (reservado para el corpus real).

---

## Columnas del CSV (ambos archivos)

| Columna | Tipo | Requerida | Descripción |
|---------|------|-----------|-------------|
| `id` | string | Sí | Identificador único |
| `descripcion` | string | Sí | Texto del incidente (pseudonimizado) |
| `categoria_real` | string | Sí | Etiqueta de verdad fundamental |
| `tiempo_manual_s` | float | No | Segundos del flujo manual (solo corpus real) |
| `tiempo_automatizado_s` | float | No | Segundos del flujo automatizado (solo corpus real) |

Valores válidos para `categoria_real` (exactos, sensibles a mayúsculas):
`Sistemas`, `Operaciones`, `Soporte Técnico`
