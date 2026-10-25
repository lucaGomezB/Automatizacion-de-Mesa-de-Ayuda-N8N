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

## Ubicación del Corpus Real

El corpus de evaluación (`corpus_evaluacion_pseudonimizado.json`) está
**versionado en git** en su forma pseudonimizada (los originales
pre-pseudonimización no, por privacidad). Reside en:

```
data/corpus_evaluacion_pseudonimizado.json
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

### Regenerar solo la sección "Tiempos" (`--solo-tiempos`)

```bash
# Desde la raíz del repositorio (no requiere GEMINI_API_KEY ni predicciones.json):
PYTHONPATH=App/Backend python -m evaluation.run_evaluation --solo-tiempos
```

La sección "Tiempos" depende únicamente del corpus (pares `tiempo_manual_s` /
`tiempo_automatizado_s`), de modo que este modo la recalcula sin pagar:

- **Sin Gemini y sin gate pago**: no construye ni invoca el clasificador y no
  exige `--confirm-paid` ni `EVALUATION_CONFIRM_PAID`.
- **Sin cache**: no lee ni escribe `evaluation/predicciones.json`.
- **Reemplazo acotado**: reescribe solo el bloque `## Tiempos` de
  `evaluation/report.md` (hasta el siguiente encabezado `## ` o el pie `---`);
  el resto del reporte queda idéntico byte a byte y el bloque resultante es el
  mismo que produce la corrida completa sobre el mismo corpus.
- **Requiere un reporte previo**: si `evaluation/report.md` no existe, termina
  con un error que indica generar primero el reporte completo.
- **Incompatible con `--force`, `--no-cache` y `--confirm-paid`**: combinarlo
  con ellos es un error de uso (código de salida 2).

La huella SHA-256 del corpus que emite el reporte normaliza los fines de línea
a LF: un checkout de Windows con CRLF y uno de Linux con LF producen la misma
huella (la del blob versionado).

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
- **Procedencia de las predicciones** (c-131): bajo "Total de casos evaluados",
  la `classifier_version` y el `generated_at` del `cache_meta` de las
  predicciones usadas (en un cache hit se leen del archivo; en una corrida nueva,
  del `cache_meta` recién construido). Sin metadata la línea se omite.
- **Exactitud**: tres definiciones de acierto, cada una con su IC de Wilson al
  95%: igualdad estricta del sector principal; **pertenencia** del sector
  asignado al conjunto predicho; y **laxa** (c-131), el sector predicho
  principal dentro del conjunto de verdad del caso (`sector_asignado` más
  `sectores_adicionales` del corpus). La laxa no es la pertenencia y nunca es
  menor que la estricta; es una métrica secundaria, no reemplaza a la estricta.
- **Exactitud por etapa del pipeline** (c-131): casos, aciertos, exactitud
  estricta y laxa con IC de Wilson de `deterministic`, `gemini` y `fallback`
  (una etapa sin casos se declara "no aplicable"). Suma los totales globales.
- **Exactitud por canal de origen** (c-131): lo mismo por `canal_origen`, con la
  composición por etapa y el orden del desglose de tiempos. El runner falla con
  `ValueError` (posición y ambos identificadores) si `predicciones[i].caso_id`
  no coincide con `corpus[i].id`. La composición sectorial y la proporción
  multietiqueta difieren entre canales: la comparación no aísla el efecto del canal.
- **Calibración de la confianza** (c-131): bandas globales (Tabla 7.5),
  contingencia en 0,70 y tramo `>= 0,90` globales y por etapa, bandas por etapa
  con IC de Wilson y distribución de valores de confianza por etapa. Las bandas
  agregadas comparan etapas (la confianza determinística y la de Gemini son
  magnitudes distintas); la lectura de calibración se hace por etapa.
- **Matriz de confusión primaria 5x5**: filas = sector asignado, columnas =
  sector predicho principal.
- **Métricas por sector (one-vs-rest)**: precisión, sensibilidad, F1 y soporte.
- **Métricas de conjunto**: subset accuracy, Hamming loss, micro-F1, macro-F1 y
  Jaccard (IoU) promedio.
- **Tiempos** (se puede regenerar sola con `--solo-tiempos`): normalidad
  (Shapiro-Wilk), Wilcoxon global, reducción de tiempos y desglose por canal,
  más tres subsecciones aditivas:
  - **Descriptivos global y por canal**: media, mediana, desvío muestral
    (divisor n − 1), mínimo y máximo de los brazos manual y automatizado, la
    reducción relativa de media y mediana y los pares en que el flujo
    automatizado no fue más rápido.
  - **Contraste direccional y tamaño del efecto estandarizado**: p bilateral
    (convención W = min(T+, T−)), p unilateral de H1 `manual > automatizado`,
    `d_z = media(d) / desvío(d)` y efecto mínimo detectable (MDE, en escala
    `d_z`; alfa = 0.05 bilateral, potencia = 0.80, con ARE = 1 y con la cota
    ARE = 0.864 de la prueba de rangos frente a la t pareada).
  - **Escenarios de sensibilidad del redondeo manual**: descuentos de 5 s y
    10 s a cada tiempo manual (media ajustada, reducción relativa, p bilateral,
    p unilateral y r) y la granularidad de `tiempo_manual_s` (cuántos valores
    son múltiplos de 5 s y de 10 s).

### Política de deriva y reproducción (c-131, D3)

Los valores canónicos de clasificación provienen de la corrida oficial
(`hybrid-v3`, 2026-10-07), conservada como evidencia congelada en
`evaluation/evidence/`. Para regenerar `evaluation/report.md` sin costo, copiar
esa evidencia a la ruta que espera el runner (ignorada por git) y correr el
runner: es un cache hit y no invoca a Gemini.

```bash
cp evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json evaluation/predicciones.json
PYTHONPATH=App/Backend python -m evaluation.run_evaluation
```

Una corrida de **reproducción** (nueva invocación paga al proveedor) NO debe
sobrescribir `evaluation/predicciones.json` ni `evaluation/report.md`: se escribe
en archivos separados y se rotula con su versión y fecha.

```bash
PYTHONPATH=App/Backend python -c "import asyncio, pathlib; from evaluation.run_evaluation import main_con_corpus_real; asyncio.run(main_con_corpus_real(report_path=pathlib.Path('evaluation/report_reproduccion.md'), predicciones_path=pathlib.Path('evaluation/predicciones_reproduccion.json'), force=True, confirm_paid=True))"
```

La deriva de la etapa Gemini se cuantifica contra los agregados oficiales y los
canónicos no se reemplazan salvo decisión explícita del usuario registrada en
`docs/Tesis/Correcciones/numeros-canonicos.md`.

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

## Advertencia Metodológica (procedencia de los ajustes)

> **Parte del clasificador evaluado se ajustó con el corpus de evaluación.**

El historial del repositorio registra ajustes hechos sobre
`data/corpus_evaluacion_pseudonimizado.json` antes de la corrida oficial: el
vocabulario del filtro determinístico se amplió a partir de sus errores (c-71,
commit `1368fd8`); las reglas de frontera del prompt se redactaron a partir de
casos del corpus (c-72, commit `a76851e`; R002 y R038); y el punto de operación
del cortocircuito se derivó sobre el corpus por validación cruzada fuera de
muestra (c-74, commit `d6bb474`). El protocolo fuera de muestra cubre el punto de
operación, no el vocabulario ni las reglas del prompt. No se dispuso de un corpus
independiente de preproducción. Las métricas de `report.md` son, por lo tanto,
estimaciones dentro de la muestra.

Regla vigente: el framework solo **evalúa**; el corpus de evaluación se usa
**solo para diagnóstico** y todo ajuste posterior del clasificador se mide sobre
datos separados y declara su procedencia. La validación sobre un corpus
independiente queda como línea de trabajo futuro.
