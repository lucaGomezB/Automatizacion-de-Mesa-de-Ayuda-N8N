# evaluation/data/campana/analisis/

Salidas del analisis de solo lectura de la campana (c-167). Las produce
`evaluation/analisis_campana.py` corriendo offline sobre las entradas de
`evaluation/data/campana/`. Esta carpeta no es una fuente de datos: es un reporte derivado y
regenerable.

## Procedencia

- Productor: `evaluation/analisis_campana.py` (CLI de solo lectura).
- Comando de referencia:

  ```bash
  python -m evaluation.analisis_campana \
    --entrada evaluation/data/campana \
    --salida evaluation/data/campana/analisis \
    --pines-in-sample '{"google_genai": ">=2.20.0", "modelo": "gemini-3.6-flash"}' \
    --rango-google-genai-vigente ">=2.33,<3"
  ```

- El analisis NO usa red ni Gemini, NO regenera `evaluation/report.md`,
  `evaluation/predicciones.json` ni los numeros canonicos de v9, y NO escribe fuera de la
  carpeta de salida. La proteccion de los artefactos congelados es POR CONSTRUCCION: el CLI
  escribe exactamente tres nombres fijos (`resultados.json`, `resultados.md` y
  `SHA256SUMS.txt`), asi que nunca toca `evaluation/report.md`, `evaluation/predicciones.json`,
  `evaluation/predicciones_calibracion.json`, `data/corpus_resultados*.json` ni
  `evaluation/evidence/`.
- Referencia por defecto del brazo manual: `consenso_doble_etiquetado`. La referencia
  alternativa `consenso_original` se pide con `--referencia`.

## Entradas esperadas

Se leen de la carpeta `--entrada`, con estos nombres canonicos:

| Archivo | Contrato | Que aporta |
|---|---|---|
| `plantilla_etiquetado.csv` | C1 | Filas de `doble_etiquetado` (kappa y referencia) y de `brazo_manual` (exactitud y orden) |
| `registro_sujetos.csv` | C2 | Independencia de roles (`alias, rol, persona`) |
| `intervenciones.csv` | C5 | `tasa_intervencion_humana` y proporcion de tiempo |
| `plan_campana.csv` | C6 | Universo de casos de la corrida y efecto de orden |
| `corpus_campana.json` | C1/corpus | `tiempo_automatizado_s` y verdad del corpus de ajuste |
| `predicciones_in_sample.json` | v9/C9 | Bloque in-sample y contraste manual vs automatizado |
| `predicciones_independiente.json` | C9 | Bloque out-of-sample |
| `corpus_independiente.json` | C9 | Verdad del corpus independiente |

Cada seccion se ejecuta de forma independiente: si falta el archivo de una seccion, esa
seccion se declara "no se obtuvo" con el artefacto faltante y las demas se reportan igual.
Una columna faltante en un archivo presente aborta el CLI con un error que nombra el archivo
y la columna.

## Semilla y remuestreos

- Semilla bootstrap: `SEMILLA_BOOTSTRAP` de `evaluation/metrics.py` (`20261021`).
- Remuestreos bootstrap: `REMUESTREOS_BOOTSTRAP` de `evaluation/metrics.py` (`2000`).
- Nivel de confianza: `NIVEL_CONFIANZA` de `evaluation/metrics.py` (`0.95`).
- Semilla y remuestreos se listan en `resultados.json` y en `resultados.md`. Con las mismas
  entradas, dos corridas producen `resultados.json`, `resultados.md` y `SHA256SUMS.txt`
  identicos byte a byte.

## Salidas

- `resultados.json`: documento deterministico con la referencia usada, la semilla, los
  remuestreos, el SHA-256 de cada entrada leida y las cinco secciones (`kappa`,
  `exactitud_brazo_manual`, `intervencion`, `orden`, `fuera_de_muestra`).
- `resultados.md`: resumen legible del mismo analisis.
- `SHA256SUMS.txt`: una linea `hash  nombre` por cada salida y por cada entrada leida. Sirve
  para verificar que una corrida uso exactamente las entradas esperadas y para comparar dos
  corridas. No incluye su propio hash. Su formato es el de `sha256sum`.
