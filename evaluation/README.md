# Framework de Evaluación del Clasificador — Capítulo 7

Este paquete implementa el framework reproducible para calcular las métricas del
Capítulo 7 de la tesis ("Resultados de Evaluación") a partir del corpus
pseudonimizado de 200 casos (§4.4).

## Esquema del CSV del Corpus

### Columnas requeridas

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | string/int | Identificador único del caso |
| `descripcion` | string | Texto del incidente (pseudonimizado) |
| `categoria_real` | string | Etiqueta de verdad fundamental |

Valores válidos para `categoria_real` (exactos, sensibles a mayúsculas):
- `Sistemas`
- `Operaciones`
- `Soporte Técnico`

Cualquier otro valor (incluyendo variantes en minúscula como `sistemas`) causa
un error claro en la carga.

### Columnas opcionales (para análisis de tiempos §7.1)

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `tiempo_manual_s` | float | Tiempo del flujo manual en segundos |
| `tiempo_automatizado_s` | float | Tiempo del flujo automatizado en segundos |

Si estas columnas están presentes, el runner habilita automáticamente el
análisis de Wilcoxon (§7.1). Si no están, esa sección del reporte se omite
sin error.

## Dónde Colocar el Corpus Real

El corpus de evaluación (`corpus_evaluacion_pseudonimizado.csv`) **no está
trackeado en git** por privacidad. Para ejecutar la evaluación real:

```
data/
└── corpus_evaluacion_pseudonimizado.csv   ← colocar aquí
```

## Comando Único de Corrida

```bash
# Desde la raíz del repositorio:
PYTHONPATH=Gestion_Incidentes python -m evaluation.run_evaluation
```

Esto:
1. Carga `data/corpus_evaluacion_pseudonimizado.csv`
2. Ejecuta el clasificador híbrido caso por caso
3. Persiste las predicciones en `evaluation/predicciones.json`
4. Escribe el reporte en `evaluation/report.md`

## Setup del Entorno

### 1. Instalar dependencias de evaluación

```bash
pip install -r evaluation/requirements.txt
```

Estas dependencias (scikit-learn, scipy, pandas, matplotlib, seaborn, jupyter)
son **independientes** del runtime del backend (`Gestion_Incidentes/requirements.txt`)
para no inflar la imagen de producción.

### 2. Configurar PYTHONPATH

El evaluador importa `HybridClassifier` directamente del backend (ver D1 abajo).
Para que el import resuelva, incluí `Gestion_Incidentes/` en el PYTHONPATH:

```bash
# Linux/macOS
export PYTHONPATH=Gestion_Incidentes

# Windows PowerShell
$env:PYTHONPATH = "Gestion_Incidentes"

# O correr con el prefijo (ver Comando Único de Corrida arriba)
```

### 3. Configurar GEMINI_API_KEY

```bash
export GEMINI_API_KEY="tu-clave-aqui"
```

Solo es necesaria para los casos que no resuelve el clasificador determinístico
(en la tesis: ~38% de los casos pasan a Gemini según §7.1).

## Correr los Tests del Framework

Los tests del framework **no requieren el corpus real ni GEMINI_API_KEY**; usan
el fixture sintético y el `FakeClassifier`:

```bash
# Desde la raíz del repositorio:
cd evaluation
python -m pytest tests/ -v
```

## Notebook de Análisis

```bash
cd evaluation
jupyter notebook analysis.ipynb
```

Requiere que `evaluation/predicciones.json` exista (generado por el runner).
Produce tres figuras guardadas en `evaluation/`:
- `figura_matriz_confusion.png`
- `figura_confianzas_por_etapa.png`
- `figura_calibracion.png`

## Interpretación del Reporte (`evaluation/report.md`)

El reporte incluye:

- **Etapas del pipeline**: cuántos casos resolvió cada etapa (deterministic /
  gemini / fallback), útil para verificar la tasa de cortocircuito determinístico.
- **Exactitud global**: proporción de aciertos, con IC de Wilson al 95% (§4.7).
- **Matriz de confusión**: filas = categoría real, columnas = categoría predicha.
  Los valores de la diagonal son aciertos; fuera de la diagonal son errores.
- **Métricas por clase**: precisión, sensibilidad y F1 para cada una de las tres
  categorías. Denominador cero → 0.0 (no produce excepción).
- **F1 Macro**: promedio aritmético de los tres F1, que pondera las clases por
  igual independiente de la distribución del corpus.

Los valores esperados para el corpus de 200 casos (tesis, §7.2):
- Exactitud: 92% (IC Wilson 95%: [0.872, 0.952])
- F1 Macro: ≈ 0.919

## Decisión D1: Import Directo vs HTTP al Backend

El runner invoca `HybridClassifier.classify(descripcion)` directamente (import
Python), en lugar de hacer `POST /api/v1/incidentes` al servidor FastAPI.

**Por qué import directo:**
- **Reproducibilidad**: no depende de un servidor corriendo, base de datos ni
  migraciones. La evaluación es función del corpus + código del clasificador.
- **Aislamiento**: no persiste 200 incidentes de prueba ni dispara notificaciones
  a N8N (C-02).
- **Testabilidad**: el runner recibe el clasificador como parámetro, permitiendo
  inyectar `FakeClassifier` en tests sin llamadas a Gemini.
- **Control de costo**: se registra la etapa por caso; las predicciones se
  persisten en JSON para no re-invocar Gemini al regenerar el reporte.

**Trade-off asumido**: la evaluación mide el **clasificador**, no la capa HTTP.
El Capítulo 7 evalúa calidad de clasificación; la API ya se cubre en C-04/C-05.

## Advertencia Metodológica (Anti Data Leakage — §8.1)

> **El clasificador NO fue ajustado sobre el corpus de 200 casos.**

Este framework solo **evalúa** el clasificador. Las reglas determinísticas
(keywords) y el prompt de Gemini fueron definidos antes de la recolección del
corpus final. El framework **nunca modifica** reglas ni prompts a partir de los
resultados de evaluación.

Ajustar el clasificador sobre el corpus de evaluación invalidaría las métricas
reportadas (data leakage). Si identificás errores sistemáticos y necesitás
ajustar el sistema, usá el corpus de evaluación **solo para diagnóstico** y
medí el impacto sobre datos separados.
