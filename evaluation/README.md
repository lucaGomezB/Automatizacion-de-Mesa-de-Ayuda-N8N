# Framework de Evaluación del Clasificador — Capítulo 7

Este paquete implementa el framework reproducible para calcular las métricas
multietiqueta del Capítulo 7 de la tesis ("Resultados de Evaluación") a partir
del corpus pseudonimizado en formato JSON.

## Esquema del Corpus (JSON)

El corpus es un documento JSON con la siguiente estructura:

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

### Campos requeridos por caso

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | string | Identificador único del caso |
| `descripcion` | string | Texto del incidente (pseudonimizado) |
| `canal_origen` | string | Canal de entrada (correo, formulario, llamada) |
| `sector_asignado` | string | Sector principal de verdad fundamental |
| `sectores_adicionales` | array | Sectores adicionales de verdad (`[]` si no hay) |
| `tiempo_manual_s` | number | Tiempo del flujo manual en segundos |
| `tiempo_automatizado_s` | number | Tiempo del flujo automatizado en segundos |

Valores válidos para los sectores (exactos, sensibles a mayúsculas, **sin tildes**):

- `Seguridad Informatica`
- `Soporte Tecnico Hardware`
- `Soporte Tecnico Software`
- `Bases de Datos`
- `Sistemas`

Invariantes: `sectores_adicionales` es obligatorio; `sector_asignado` no puede
repetirse dentro de `sectores_adicionales`; todos los valores pertenecen al
conjunto canónico. Cualquier otro valor (incluyendo variantes en minúscula como
`sistemas` u `Operaciones`) causa un error claro en la carga.

### Normalización de `metadata.total_casos`

Si `metadata.total_casos` no coincide con la cantidad real de `casos`, el loader
lo normaliza a `len(casos)` y lo persiste en disco antes de validar y usar el
corpus. Si ya coincide, la escritura es idempotente (no reescribe el archivo).

## Dónde Colocar el Corpus Real

El corpus de evaluación (`corpus_evaluacion_pseudonimizado.json`) **no está
trackeado en git** por privacidad. Para ejecutar la evaluación real:

```
data/
└── corpus_evaluacion_pseudonimizado.json   ← colocar aquí
```

## Comando Único de Corrida

```bash
# Desde la raíz del repositorio:
PYTHONPATH=App/Backend python -m evaluation.run_evaluation
```

Esto:
1. Carga `data/corpus_evaluacion_pseudonimizado.json`
2. Ejecuta el clasificador híbrido caso por caso
3. Persiste las predicciones en `evaluation/predicciones.json`
4. Escribe el reporte en `evaluation/report.md`

## Gate de Corrida Paga

El runner invoca el clasificador real (Gemini) y esa corrida tiene costo. Antes
de invocarlo exige confirmación explícita del operador; sin ella aborta sin
llamar al clasificador.

```bash
# Confirmación por flag:
PYTHONPATH=App/Backend python -m evaluation.run_evaluation --confirm-paid

# Confirmación por variable de entorno:
EVALUATION_CONFIRM_PAID=1 PYTHONPATH=App/Backend python -m evaluation.run_evaluation
```

Sin confirmación, la corrida aborta con código de salida 2 y un mensaje claro.
Al confirmar, el runner imprime una estimación orientativa del costo antes de
ejecutar (no es una factura).

## Setup del Entorno

### 1. Instalar dependencias de evaluación

```bash
pip install -r evaluation/requirements.txt
```

Estas dependencias (scikit-learn, scipy, pandas, matplotlib, seaborn, jupyter)
son **independientes** del runtime del backend (`App/Backend/requirements.txt`)
para no inflar la imagen de producción.

### 2. Configurar PYTHONPATH

El evaluador importa `HybridClassifier` directamente del backend (ver D1 abajo).
Para que el import resuelva, incluí `App/Backend/` en el PYTHONPATH:

```bash
# Linux/macOS
export PYTHONPATH=App/Backend

# Windows PowerShell
$env:PYTHONPATH = "App/Backend"

# O correr con el prefijo (ver Comando Único de Corrida arriba)
```

### 3. Configurar GEMINI_API_KEY

```bash
export GEMINI_API_KEY="tu-clave-aqui"
```

Solo es necesaria para los casos que no resuelve el clasificador determinístico.
Una corrida que use el clasificador real exige además confirmar el gate de
corrida paga (ver «Gate de Corrida Paga»).

## Correr los Tests del Framework

Los tests del framework **no requieren el corpus real ni GEMINI_API_KEY**; usan
el fixture JSON `tests/fixtures/corpus_fixture.json` y el `FakeClassifier`:

```bash
# Desde la raíz del repositorio:
cd evaluation
pytest
```

## Notebook de Análisis

```bash
cd evaluation
jupyter notebook analysis.ipynb
```

Requiere que `evaluation/predicciones.json` exista (generado por el runner).

## Interpretación del Reporte (`evaluation/report.md`)

El reporte incluye (design D5):

- **Etapas del pipeline**: cuántos casos resolvió cada etapa (deterministic /
  gemini / fallback).
- **Exactitud**: dos definiciones de acierto — igualdad estricta del sector
  principal y pertenencia del sector asignado al conjunto predicho — cada una
  con su IC de Wilson al 95%.
- **Matriz de confusión primaria 5x5**: filas = sector asignado, columnas =
  sector predicho principal.
- **Métricas por sector (one-vs-rest)**: precisión, sensibilidad, F1 y soporte.
- **Métricas de conjunto**: subset accuracy, Hamming loss, micro-F1, macro-F1 y
  Jaccard (IoU) promedio.

## Decisión D1: Import Directo vs HTTP al Backend

El runner invoca `HybridClassifier.classify(descripcion)` directamente (import
Python), en lugar de hacer `POST /api/v1/incidentes` al servidor FastAPI.

**Por qué import directo:**

- **Reproducibilidad**: no depende de un servidor corriendo, base de datos ni
  migraciones. La evaluación es función del corpus + código del clasificador.
- **Aislamiento**: no persiste incidentes de prueba ni dispara notificaciones
  a N8N (C-02).
- **Testabilidad**: el runner recibe el clasificador como parámetro, permitiendo
  inyectar `FakeClassifier` en tests sin llamadas a Gemini.
- **Control de costo**: se registra la etapa por caso; las predicciones se
  persisten en JSON para no re-invocar Gemini al regenerar el reporte.

**Trade-off asumido**: la evaluación mide el **clasificador**, no la capa HTTP.
El Capítulo 7 evalúa calidad de clasificación; la API ya se cubre en C-04/C-05.

## Advertencia Metodológica (Anti Data Leakage — §8.1)

> **El clasificador NO fue ajustado sobre el corpus de evaluación.**

Este framework solo **evalúa** el clasificador. Las reglas determinísticas
(keywords) y el prompt de Gemini fueron definidos antes de la recolección del
corpus final. El framework **nunca modifica** reglas ni prompts a partir de los
resultados de evaluación.

Ajustar el clasificador sobre el corpus de evaluación invalidaría las métricas
reportadas (data leakage). Si identificás errores sistemáticos y necesitás
ajustar el sistema, usá el corpus de evaluación **solo para diagnóstico** y
medí el impacto sobre datos separados.
