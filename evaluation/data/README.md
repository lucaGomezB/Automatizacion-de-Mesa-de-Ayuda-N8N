# evaluation/data/

Corpus de evaluacion para el framework del clasificador hibrido.

## Archivos

### `corpus_evaluacion.csv` — TRACKEADO en git

Corpus simulado de 200 casos generado por `evaluation/generate_corpus.py`.

**DATOS SIMULADOS. NO contiene PII real.** Usa nombres placeholder genericos
(Juan Perez, Maria Garcia, etc.), emails fake (usuario@empresa.com.ar),
telefonos fake (+54 261 5XX-XXXX) y nombres de sistemas genericos.

**ADVERTENCIA:** los numeros de metricas generados con este corpus NO son
validos para el Capitulo 7 de la tesis. El corpus real debe colocarse en
`data/corpus_evaluacion_pseudonimizado.csv` (no trackeado en git).

Distribucion (tesis Capitulo 4, Seccion 4.4):
- **Sistemas**: 82 casos (41%)
- **Operaciones**: 64 casos (32%)
- **Soporte Tecnico**: 54 casos (27%)

### Regeneracion

```bash
# Desde la raiz del repositorio:
python evaluation/generate_corpus.py
```

El script usa un seed fijo (42) — la salida es identica en cada ejecucion.

## Columnas del CSV

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `id` | int | Identificador secuencial (1-200) |
| `descripcion` | string | Texto del incidente en espanol rioplatense |
| `canal_origen` | string | Canal de entrada (correo, formulario, telefono) |
| `categoria_real` | string | Etiqueta de verdad fundamental |

Valores validos para `categoria_real` (exactos, sensibles a mayusculas):
`Sistemas`, `Operaciones`, `Soporte Tecnico`

## Realismo

El corpus incluye variaciones deliberadas para simular incidentes reales:
- ~10% de las descripciones contienen errores de tipeo (ej. "nesecito", "conecsion")
- ~8% omiten tildes (escritura apurada)
- Variedad de registros: formal, informal, tecnico, urgente
- Distribucion de canales: correo ~60%, formulario ~25%, telefono ~15%
- Longitud variable: 10-80 palabras por descripcion
