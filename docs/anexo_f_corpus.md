# Anexo F — Corpus de Validación

---

## Declaración de integridad académica

> **El corpus sintético de 200 casos fue descartado por los revisores de la tesis
> y eliminado del repositorio.**
>
> Existió como artefacto provisional (`data/corpus_sintetico_provisional.csv`) para
> verificar el funcionamiento del framework de evaluación durante el desarrollo.
> **No representaba datos reales de una mesa de ayuda y no constituye evidencia
> experimental del desempeño del sistema.** Fue retirado junto con su generador y
> su andamiaje (`generate_corpus.py`, `FakeClassifier` calibrado, columna
> `categoria_real`). Ninguno de sus números (82/64/54, exactitud 92 %, F1 0,919,
> Tabla 7) puede citarse como resultado vigente.
>
> El corpus real, pseudonimizado y extraído de incidentes reales de una
> organización, es **trabajo de campo futuro** de la etapa de evaluación
> experimental. No está versionado en git por privacidad y cumplimiento de la
> Ley 25.326 (Protección de Datos Personales de la República Argentina).

---

## Descripción del corpus

El corpus de validación es el conjunto de datos etiquetados que permite medir la
exactitud del sistema de clasificación automática propuesto. Cada caso representa
un incidente de mesa de ayuda con su **sector asignado** y, opcionalmente,
**sectores adicionales**, confirmados por un operador humano experto. La verdad
es multietiqueta: el conjunto de verdad de un caso es
`{sector_asignado} ∪ sectores_adicionales`.

---

## Esquema del archivo JSON

El corpus se almacena como un documento JSON codificado en UTF-8:

```json
{
  "schema_version": 1,
  "metadata": {
    "descripcion": "Corpus de evaluación pseudonimizado (mesa de ayuda)",
    "total_casos": 2
  },
  "casos": [
    {
      "id": "R001",
      "descripcion": "El servidor [HOST] esta caido desde las 4 AM.",
      "canal_origen": "correo electrónico",
      "sector_asignado": "Sistemas",
      "sectores_adicionales": ["Bases de Datos"],
      "tiempo_manual_s": 169.06,
      "tiempo_automatizado_s": 22.97
    },
    {
      "id": "R002",
      "descripcion": "El touchpad de la notebook de [PERSONA] no responde.",
      "canal_origen": "formulario web",
      "sector_asignado": "Soporte Tecnico Hardware",
      "sectores_adicionales": [],
      "tiempo_manual_s": 155.77,
      "tiempo_automatizado_s": 21.08
    }
  ]
}
```

### Nivel documento

| Campo            | Tipo     | Requerido | Descripción |
|------------------|----------|-----------|-------------|
| `schema_version` | entero   | sí        | Versión del esquema; permite evolucionarlo |
| `metadata`       | objeto   | sí        | Metadatos del corpus |
| `casos`          | arreglo  | sí        | Lista de casos etiquetados |

`metadata` contiene al menos `descripcion` (string) y `total_casos` (entero). El
loader **normaliza** `total_casos = len(casos)` y persiste el archivo antes de
validarlo y usarlo, de modo que la cabecera nunca quede desincronizada. Si ya
coincidía, la escritura es idempotente (no reescribe).

### Campos del caso

| Campo                    | Tipo    | Requerido | Descripción |
|--------------------------|---------|-----------|-------------|
| `id`                     | string  | sí        | Identificador único del caso (p. ej. `"R001"`) |
| `descripcion`            | string  | sí        | Texto del incidente **pseudonimizado** (PII reemplazada por `[EMAIL]`, `[TELEFONO]`, `[HOST]`, `[PERSONA]`) |
| `canal_origen`           | string  | sí        | Canal de ingreso (`correo electrónico`, `formulario web`, `llamada telefónica`) |
| `sector_asignado`        | string  | sí        | Sector principal de verdad, exactamente uno de los cinco canónicos |
| `sectores_adicionales`   | arreglo | sí        | Sectores adicionales de verdad; `[]` cuando no hay. **No repite** el sector asignado |
| `tiempo_manual_s`        | number  | sí        | Tiempo de clasificación manual en segundos |
| `tiempo_automatizado_s`  | number  | sí        | Tiempo del sistema automatizado en segundos |

La columna `categoria_real` del esquema CSV anterior **ya no existe**.

---

## Categorías válidas

Tanto `sector_asignado` como cada valor de `sectores_adicionales` deben ser
exactamente uno de estos cinco valores (sensibles a mayúsculas y **sin tildes**):

| Categoría                  | Ámbito |
|----------------------------|--------|
| `Seguridad Informatica`    | Ciberseguridad, firewall, VPN, malware, phishing, accesos e identidad |
| `Soporte Tecnico Hardware` | Equipamiento de usuarios, periféricos, impresoras, fallas físicas |
| `Soporte Tecnico Software` | Aplicaciones de escritorio, instalación, configuración, asistencia remota |
| `Bases de Datos`           | Motores de datos, consultas, replicación, backup y recuperación |
| `Sistemas`                 | Infraestructura, redes, servidores y servicios de plataforma |

`Operaciones` **no** pertenece al vocabulario vigente. Cualquier valor fuera de
este conjunto es rechazado por el validador del framework de evaluación con un
error explícito (ver `evaluation/corpus.py`, constante `CATEGORIAS_VALIDAS`).

---

## Invariantes de la verdad multietiqueta

1. `sector_asignado` es un único string canónico.
2. `sectores_adicionales` está presente en todos los casos (`[]` cuando no hay).
3. `sector_asignado` no puede repetirse dentro de `sectores_adicionales`.
4. Todos los valores pertenecen al conjunto canónico de cinco sectores.

---

## Contrato con el framework de evaluación

El módulo `evaluation/corpus.py` define el contrato formal del corpus:

```python
SECTORES_CANONICOS = (
    "Seguridad Informatica",
    "Soporte Tecnico Hardware",
    "Soporte Tecnico Software",
    "Bases de Datos",
    "Sistemas",
)
CATEGORIAS_VALIDAS = frozenset(SECTORES_CANONICOS)
CAMPOS_CASO_REQUERIDOS = (
    "id", "descripcion", "canal_origen", "sector_asignado",
    "sectores_adicionales", "tiempo_manual_s", "tiempo_automatizado_s",
)
```

El cargador `cargar_corpus(path)` valida:
1. Que el archivo existe en la ruta indicada.
2. Que el documento es un objeto JSON con `schema_version`, `metadata` y `casos`.
3. Que cada caso contiene los siete campos requeridos.
4. Que `sector_asignado` y `sectores_adicionales` pertenecen al conjunto canónico.
5. Las invariantes multietiqueta (ver sección anterior).

Este Anexo F es consistente con ese contrato: los mismos campos, las mismas
cinco categorías exactas.

---

## Corpus real (trabajo de campo futuro)

El corpus real se obtendrá mediante el siguiente procedimiento:

1. **Recolección**: exportar registros de `clasificacion_log` de la base de datos
   en producción, seleccionando los casos representativos por sector.
2. **Pseudonimización**: exportar desde `descripcion_pseudonimizada` (nunca
   `descripcion_original`) para cumplir la Ley 25.326.
3. **Etiquetado**: un operador humano experto valida el sector principal
   (`sector_id_validado`) y los sectores adicionales
   (`clasificacion_sector_validado`), constituyendo el ground truth.
4. **Almacenamiento**: el corpus real se guarda como
   `data/corpus_evaluacion_pseudonimizado.json` (gitignorado por privacidad).

El framework de evaluación lee el corpus real con `cargar_corpus()`. Si el
archivo no está presente, el runner termina con un error claro y no inventa
datos.
