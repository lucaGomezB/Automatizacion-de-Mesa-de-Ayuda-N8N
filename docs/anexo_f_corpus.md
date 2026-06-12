# Anexo F — Corpus de Validación

---

## ⚠️ Declaración de integridad académica

> **El corpus de validación disponible actualmente en el repositorio
> (`data/corpus_sintetico_provisional.csv`) es SINTÉTICO y PROVISIONAL.**
>
> Fue generado programáticamente con el único propósito de verificar el
> correcto funcionamiento del framework de evaluación (módulo `evaluation/`)
> durante el desarrollo. **No representa datos reales de una mesa de ayuda y
> no debe interpretarse como evidencia experimental del desempeño del sistema.**
>
> El corpus real, constituido por 200 casos pseudonimizados extraídos de
> incidentes reales de una organización, es **trabajo de campo futuro** que
> se realizará en la etapa de evaluación experimental de la tesis. Ese corpus
> no está versionado en git por razones de privacidad y cumplimiento de la
> Ley 25.326 (Protección de Datos Personales de la República Argentina).
>
> (Decisión D5 del diseño de C-10.)

---

## Descripción del corpus

El corpus de validación es el conjunto de datos etiquetados que permite
medir la exactitud del sistema de clasificación automática propuesto en
esta tesis. Cada caso representa un incidente de mesa de ayuda con su
categoría real confirmada por un operador humano experto.

### Tamaño objetivo

**200 casos** etiquetados manualmente, distribuidos de forma representativa
entre las tres categorías del sistema. El tamaño fue determinado para
proveer poder estadístico suficiente para calcular accuracy e intervalos
de confianza al 95 % (estimación previa: ≈ 150–200 casos para un margen
de ±5 pp con distribución balanceada).

---

## Esquema del archivo CSV

El corpus se almacena como CSV con codificación UTF-8 y las siguientes columnas:

### Columnas requeridas

| Columna          | Tipo   | Descripción |
|------------------|--------|-------------|
| `id`             | string | Identificador único del caso (p. ej. `"001"`, `"caso_042"`) |
| `descripcion`    | string | Texto del incidente **pseudonimizado** (PII reemplazada por etiquetas `[EMAIL]`, `[TELEFONO]`, `[HOST]`, `[PERSONA]`) |
| `categoria_real` | string | Categoría correcta confirmada por el operador humano; debe ser exactamente uno de los tres valores válidos (ver abajo) |

### Columnas opcionales (cronometraje)

| Columna                | Tipo   | Descripción |
|------------------------|--------|-------------|
| `tiempo_manual_s`      | float  | Tiempo en segundos que tomó clasificar el incidente manualmente |
| `tiempo_automatizado_s`| float  | Tiempo en segundos que tomó el sistema automatizado en clasificarlo |

Estas columnas son opcionales; el framework de evaluación las incluye solo
si están presentes en el CSV. Se usan para calcular la comparativa de
eficiencia temporal entre el proceso manual y el automatizado (objetivo
secundario de la tesis).

---

## Categorías válidas

El campo `categoria_real` debe contener exactamente uno de estos tres
valores (sensible a mayúsculas, en español):

| Categoría         | Ámbito |
|-------------------|--------|
| `Sistemas`        | Infraestructura, redes, servidores, bases de datos, ciberseguridad |
| `Operaciones`     | Procesos compartidos, gestión de servicios, planificación, continuidad del negocio |
| `Soporte Técnico` | Equipamiento de usuarios, periféricos, software cliente, asistencia remota |

Cualquier valor fuera de este conjunto es rechazado por el validador del
framework de evaluación con un error explícito (ver `evaluation/corpus.py`,
constante `CATEGORIAS_VALIDAS`).

---

## Contrato con el framework de evaluación

El módulo `evaluation/corpus.py` (C-08) define el contrato formal del corpus:

```python
CATEGORIAS_VALIDAS = frozenset({"Sistemas", "Operaciones", "Soporte Técnico"})
COLUMNAS_REQUERIDAS = ["id", "descripcion", "categoria_real"]
```

El cargador `cargar_corpus(path)` valida:
1. Que el archivo existe en la ruta indicada.
2. Que las columnas requeridas están presentes.
3. Que cada valor de `categoria_real` pertenece al conjunto válido.

Este Anexo F es consistente con ese contrato: las mismas columnas, las
mismas categorías exactas.

---

## Corpus provisional disponible en el repositorio

**Archivo**: `data/corpus_sintetico_provisional.csv`

Este archivo fue generado por un script de síntesis para que los tests del
framework de evaluación (`evaluation/tests/`) puedan correr en CI sin depender
de datos reales. Sus características:

- Generado programáticamente; **no proviene de incidentes reales**.
- Respeta el esquema CSV (columnas `id`, `descripcion`, `categoria_real`).
- Las descripciones son ejemplos artificiales que cubren patrones lexicales
  de cada categoría, suficientes para testear el clasificador pero sin validez
  estadística para medir el desempeño real del sistema.
- **No se debe citar como evidencia experimental** en la tesis ni en publicaciones.

---

## Corpus real (trabajo de campo futuro)

El corpus real se obtendrá mediante el siguiente procedimiento:

1. **Recolección**: exportar registros de `clasificacion_log` de la base de datos
   en producción, filtrando los 200 casos con mayor representatividad por categoría.
2. **Pseudonimización**: todos los registros deben exportarse desde la columna
   `descripcion_pseudonimizada` (nunca `descripcion_original`) para garantizar
   el cumplimiento de la Ley 25.326.
3. **Etiquetado**: un operador humano experto valida la categoría de cada caso
   (columna `sector_id_validado` en `clasificacion_log`), constituyendo el
   ground truth.
4. **Almacenamiento**: el corpus real se guarda como
   `data/corpus_evaluacion_pseudonimizado.csv` (gitignorado por privacidad).

El framework de evaluación leerá el corpus real con el mismo `cargar_corpus()`
que usa hoy con el corpus sintético, sin cambios de código.
