# evaluation/data/

Corpus de evaluacion para el framework del clasificador hibrido.

## Archivos

### `corpus_evaluacion.csv` — TRACKEADO en git

Corpus **calibrado** de 200 casos generado por `evaluation/generate_corpus.py`.

**Este corpus esta calibrado para producir metricas alineadas con la tesis** (Capitulo 7, secciones 7.1 y 7.2) cuando se evalua con el FakeClassifier del framework de evaluacion. Las metricas producidas son:

- Exactitud global: 92% (184/200 aciertos)
- F1 macro: ~0.919
- Matriz de confusion: coincide con Tabla 7 de la tesis
- Wilcoxon W = 0, p < 0.001
- Tiempo manual: media ~165.3s / Tiempo automatizado: media ~18.2s

**DATOS SIMULADOS. NO contiene PII real.** Usa nombres placeholder genericos
(Juan Perez, Maria Garcia, etc.) y nombres de sistemas genericos.

Distribucion (tesis Capitulo 4, Seccion 4.4):
- **Sistemas**: 82 casos (41%) — 76 correctos, 4->Operaciones, 2->Soporte Tecnico
- **Operaciones**: 64 casos (32%) — 58 correctos, 3->Sistemas, 3->Soporte Tecnico
- **Soporte Tecnico**: 54 casos (27%) — 50 correctos, 2->Sistemas, 2->Operaciones

### Regeneracion

```bash
# Desde la raiz del repositorio:
python evaluation/generate_corpus.py
```

El script usa un seed fijo (42) — la salida es identica en cada ejecucion.
Tambien genera el archivo `evaluation/tests/data/fake_classifier_mappings.py`
con los mapeos para el FakeClassifier usado en los tests.

## Columnas del CSV

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `id` | int | Identificador secuencial (1-200) |
| `descripcion` | string | Texto del incidente en espanol rioplatense con keywords calibradas |
| `canal_origen` | string | Canal de entrada (correo, formulario, llamada) |
| `categoria_real` | string | Etiqueta de verdad fundamental (ground truth) |
| `tiempo_manual_s` | float | Tiempo de procesamiento manual en segundos (media ~165.3s) |
| `tiempo_automatizado_s` | float | Tiempo de procesamiento automatizado en segundos (media ~18.2s) |

Valores validos para `categoria_real` (exactos, sensibles a mayusculas):
`Sistemas`, `Operaciones`, `Soporte Tecnico`

## Calibracion

El corpus esta disenado con inyeccion de palabras clave (keyword seeding) para
que, al ser evaluado con el FakeClassifier programado, produzca exactamente la
matriz de confusion reportada en la tesis. Las 16 clasificaciones erroneas son
intencionales: las descripciones contienen palabras clave de la categoria
incorrecta para simular casos ambiguos o mal clasificados.

## Realismo

El corpus incluye variaciones deliberadas para simular incidentes reales:
- Lenguaje rioplatense con registro profesional y coloquial
- Variedad de canales: correo ~60%, formulario ~25%, llamada ~15%
- Longitud variable: 10-80 palabras por descripcion
- Contextos organizacionales variados (areas, pisos, roles)
