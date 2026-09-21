# Como cargar los datos del corpus de evaluacion

Procedimiento para construir el corpus real de evaluacion del clasificador
hibrido (Capitulo 7 de la tesis) a partir de tickets etiquetados manualmente.

---

## 1. Ubicacion del archivo

```
data/corpus_evaluacion_pseudonimizado.json
```

Este es el camino exacto que espera el framework de evaluacion
(`evaluation/run_evaluation.py`, constante `CORPUS_REAL_PATH`).

El archivo **NO se trackea en git** (esta en `.gitignore`). Contiene patrones
de incidentes internos de la organizacion y, aunque este pseudonimizado, se
mantiene fuera del repositorio por privacidad y cumplimiento de la Ley 25.326.

---

## 2. Esquema del JSON

Codificacion UTF-8. El documento tiene tres claves de primer nivel:
`schema_version`, `metadata` y `casos`.

```json
{
  "schema_version": 1,
  "metadata": {
    "descripcion": "Corpus de evaluacion pseudonimizado (mesa de ayuda)",
    "total_casos": 3
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
    },
    {
      "id": "R003",
      "descripcion": "No puedo abrir Outlook, la aplicacion se traba.",
      "canal_origen": "llamada telefónica",
      "sector_asignado": "Soporte Tecnico Software",
      "sectores_adicionales": [],
      "tiempo_manual_s": 160.12,
      "tiempo_automatizado_s": 19.44
    }
  ]
}
```

### Campos de cada caso

| Campo | Tipo | Requerido | Descripcion |
|-------|------|-----------|-------------|
| `id` | string | SI | Identificador unico del caso |
| `descripcion` | string | SI | Texto del incidente, **ya pseudonimizado** |
| `canal_origen` | string | SI | Canal de ingreso del incidente |
| `sector_asignado` | string | SI | Sector principal de verdad fundamental |
| `sectores_adicionales` | arreglo | SI | Sectores adicionales de verdad; `[]` si no hay. **No repite** el asignado |
| `tiempo_manual_s` | number | SI | Tiempo del flujo manual en segundos |
| `tiempo_automatizado_s` | number | SI | Tiempo del flujo automatizado en segundos |

Todos los campos son requeridos. La columna `categoria_real` del esquema CSV
anterior **ya no existe**.

`metadata.total_casos` debe coincidir con la cantidad de elementos de `casos`.
Si no coincide, el loader lo **normaliza** a `len(casos)` y vuelve a escribir
el archivo antes de validarlo (no es un error).

---

## 3. Valores validos de sector

Exactos, sensibles a mayusculas y **sin tildes**. Cualquier variante (minusculas,
con tilde, espacios mal puestos) produce un error en la carga:

- `Seguridad Informatica`
- `Soporte Tecnico Hardware`
- `Soporte Tecnico Software`
- `Bases de Datos`
- `Sistemas`

`Operaciones` ya no pertenece al vocabulario.

### Invariantes multietiqueta

1. `sector_asignado` es un unico string canonico.
2. `sectores_adicionales` esta siempre presente (`[]` cuando no hay).
3. `sector_asignado` no puede repetirse dentro de `sectores_adicionales`.
4. Todos los valores pertenecen al conjunto canonico de cinco sectores.

---

## 4. Convencion de IDs

Usar el prefijo `R` (de "real") seguido de numero secuencial: `R001`, `R002`, ...
El corpus sintetico y sus ids `S###` fueron eliminados (C-27); no hay colision
posible.

---

## 5. Pseudonimizacion

Cada `descripcion` DEBE estar pseudonimizada antes de ingresar al JSON. Los
tokens a usar (mismos que emite el modulo del proyecto en
`App/Backend/app/utils/pseudonymizer.py`):

| Token | Reemplaza a |
|-------|-------------|
| `[EMAIL]` | Direcciones de correo |
| `[TELEFONO]` | Numeros de telefono |
| `[HOST]` | Nombres de servidores / hostnames |
| `[PERSONA]` | Nombres propios de personas |

### Orden de aplicacion (para evitar colisiones)

1. `[EMAIL]`
2. `[TELEFONO]`
3. `[HOST]`
4. `[PERSONA]` (ultimo; es la heuristica mas laxa)

### Ejemplo

Texto crudo:

> La notebook de Maria Garcia no responde. Coordinen con juan.perez@empresa.com
> al 261 555-1234. El servidor srv-app-01 tambien tiene problemas.

Texto pseudonimizado:

> La notebook de [PERSONA] no responde. Coordinen con [EMAIL]
> al [TELEFONO]. El servidor [HOST] tambien tiene problemas.

---

## 6. Tamano del corpus

El corpus es provisto externamente; el proyecto no genera datos sinteticos. La
distribucion por sector se calcula dinamicamente a partir de los casos cargados
y se reporta con el intervalo de confianza de Wilson (95 %).

### Recomendacion

1. No fijar de antemano una cantidad de casos por sector.
2. Cargar todos los casos etiquetados disponibles (por tandas).
3. Ejecutar el framework: el reporte calcula el IC de Wilson real con los datos.
4. Incorporar mas casos si el limite inferior del IC queda por debajo del
   umbral objetivo de la tesis (85 %).

---

## 7. Proceso de carga (manual, por tandas)

1. Crear `data/corpus_evaluacion_pseudonimizado.json` con la estructura de la
   seccion 2 (`schema_version`, `metadata`, `casos: []`).
2. Por cada ticket etiquetado:
   - Pseudonimizar la descripcion (seccion 5).
   - Asignar `id` secuencial `R###`.
   - Verificar que `sector_asignado` y `sectores_adicionales` usen los strings
     exactos (seccion 3).
   - Completar `canal_origen` y los dos tiempos.
3. Agregar los casos a `casos` por tandas, sin importar el orden de los sectores.
4. Dejar que el loader normalice `total_casos` en la primera carga; si se edito
   a mano, verificar la consistencia antes de la corrida final.

---

## 8. Ejecutar la evaluacion

```bash
# Desde la raiz del repositorio:
cd evaluation
PYTHONPATH=App/Backend python -m evaluation.run_evaluation
```

Resultados producidos:

- `evaluation/predicciones.json` — resultado por caso (no re-invoca Gemini)
- `evaluation/report.md` — metricas: exactitud primaria, IC de Wilson (igualdad
  estricta y pertenencia), matriz de confusion 5x5, subset accuracy, perdida de
  Hamming, F1 micro/macro, tabla por sector y analisis de Wilcoxon (si hay tiempos)

Requiere `GEMINI_API_KEY` solo para los casos que no resuelve la etapa
deterministica. Si el corpus no existe, el runner falla con un error claro y no
inventa datos.

---

## 9. Verificar que el archivo no se suba a git

El archivo esta en `.gitignore`, pero conviene confirmar antes de cada commit:

```bash
git status --short | grep corpus
```

Si aparece listado, NO agregarlo. Si se agrego por error, removerlo del indice
sin borrarlo del disco:

```bash
git rm --cached data/corpus_evaluacion_pseudonimizado.json
```
