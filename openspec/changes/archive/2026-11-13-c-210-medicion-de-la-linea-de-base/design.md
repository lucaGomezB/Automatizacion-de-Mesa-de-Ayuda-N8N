## Context

Ver `proposal.md` — Why. La change consume el modulo de c-209
(`evaluation/linea_de_base.py`) y los artefactos versionados:

- `evaluation/data/campana/corpus_campana.json` — `200` casos in-sample.
- `evaluation/data/campana/corpus_independiente.json` — `103` casos fuera de muestra con
  referencia por consenso.
- `evaluation/data/campana/analisis/analisis_fuera_de_muestra_c205.json` — cifras canonicas
  del hibrido en el mismo `n` efectivo `103` (se LEEN, no se recalculan).

El borrador de tesis vive en el directorio de la change. No se edita ningun `.tex`.

## Goals / Non-Goals

**Goals:**

- Ejecutar la linea de base de c-209 y producir artefactos deterministas y versionados.
- Comparar la linea de base con el hibrido en el mismo conjunto de `103` casos.
- Reportar las metricas en lectura muestral y en lectura ponderada a la prevalencia natural.
- Dejar un borrador de seccion de resultados listo para integrar, con el veredicto honesto.

**Non-Goals:**

- Editar `.tex`, `Bibliography_base.bib`, `CHANGES.md` o changes ajenas.
- Cambiar, corregir o reinterpretar cualquier numero canonico.
- Arbitrar los `47` discordantes o evaluar sobre el `150` completo.
- Reentrenar o modificar el clasificador de produccion.

## Decisions

### D1 — Ejecucion desde el CLI de c-209 y salidas en el directorio de la change

La medicion corre `python3 -m evaluation.linea_de_base --salida <dir>` con las rutas por
defecto a los dos corpus versionados. El CLI escribe `linea_de_base_clasica_c210.json`,
`linea_de_base_clasica_c210.md` y `SHA256SUMS.txt` en el directorio de la change. Se ejecuta
dos veces y se comparan los bytes. Alternativa descartada: escribir en
`evaluation/data/campana/analisis/`, que ya contiene las salidas de c-205/c-207 y mezclaria
responsabilidades.

### D2 — Tabla comparativa con las cifras del hibrido tomadas de c-205

La tabla arma las filas de la linea de base con las metricas del JSON nuevo y las filas del
hibrido con `analisis_fuera_de_muestra_c205.json`. No se recalcula el hibrido ni se toca su
JSON. Las cifras del hibrido se citan con su archivo de procedencia. La tabla incluye
exactitud estricta, exactitud laxa, macro-F1, *balanced accuracy* y F1 por clase con soporte
para ambos sistemas. Alternativa descartada: recalcular el hibrido desde las predicciones, que
duplicaria c-205 y arriesgaria una deriva de cifras.

### D3 — Dos lecturas: muestral y ponderada a la prevalencia natural

La lectura muestral usa los `103` casos tal como estan. La lectura ponderada usa la
distribucion de los `200` casos in-sample como prevalencia natural y re-pondera las metricas
por clase. La tabla muestra ambas para la linea de base y, cuando corresponde, para el hibrido.
Se rotula cada lectura y se declara que la ponderada es una post-estratificacion. Alternativa
descartada: presentar solo la exactitud muestral, que sobrestima las clases sobrerrepresentadas
en la muestra de `103`.

### D4 — Veredicto honesto y sin maquillaje

El documento y el borrador declaran si la linea de base ayuda o perjudica el caso de la tesis.
Si queda por debajo del hibrido, se reporta con las cifras exactas. Si supera o iguala al
hibrido, tambien se reporta con las cifras exactas. No se cambia la conclusion metodologica ni
se omiten resultados desfavorables. Alternativa descartada: quedarse con la variante mas
favorable sin declarar la otra, que inflaria la lectura.

### D5 — Soporte y rotulos de clase sin transferencia

El soporte por clase de los `103` casos es `40` hardware, `24` software, `21` seguridad, `13`
bases de datos y `5` sistemas. La clase debil del HIBRIDO es `Sistemas` (`F1 0.2222`, soporte
`5`); la mejor clase del HIBRIDO es `Bases de Datos` (`F1 0.963`, soporte `13`). El documento
mantiene esos rotulos atados al hibrido y reporta la F1 de la linea de base por clase sin
transferirle debil/fuerte. Alternativa descartada: rotular la linea de base con la debilidad
del hibrido, que confundiria dos sistemas distintos.

### D6 — Determinismo y prueba de reproducibilidad

La salida se serializa con `sort_keys=True`, `indent=2`, `ensure_ascii=False`, LF y UTF-8 sin
BOM. El script imprime el SHA-256 de cada salida. El `SHA256SUMS.txt` lista las salidas y las
entradas. La medicion se corre dos veces; se comparan los bytes y se registran los hashes en el
documento. Alternativa descartada: confiar en una sola corrida sin comparacion.

### D7 — Registro aditivo y archivos ajenos intactos

Las cifras nuevas se registran en los artefactos de la change y en el borrador. No se edita el
memo canonico (`docs/Tesis/Correcciones/numeros-canonicos.md`), ni `CHANGES.md`, ni los `.tex`,
porque pertenecen a otro flujo de trabajo. El registro en `CHANGES.md` se omite y se declara la
omision. Alternativa descartada: insertar una seccion nueva en el memo canonico, que el usuario
prohibio tocar.

## Risks / Trade-offs

- [La linea de base rinde peor que el hibrido y el resultado es desfavorable] → se reporta con
  las cifras exactas; la honestidad es el activo evaluado. No se oculta ni se cambia la
  conclusion.
- [La lectura muestral se confunde con la ponderada] → se rotulan ambas y se declara la
  procedencia de la prevalencia natural.
- [El hibrido se recalculado y deriva de c-205] → se lee el JSON de c-205 y se cita; no se
  recalcula.
- [Se transfieren los rotulos de clase debil/fuerte del hibrido a la linea de base] → se
  mantienen atados al hibrido y se reporta la F1 de la linea de base por separado.
- [Se edita un archivo ajeno por error] → el CLI escribe solo en el directorio de la change y
  el diff se revisa antes de commitear.

## Migration Plan

No hay migraciones ni datos productivos. Rollback: eliminar los artefactos nuevos del
directorio de la change; el repositorio vuelve al estado previo. No se toca `App/`, `n8n/`, el
corpus, los numeros canonicos ni la tesis.
