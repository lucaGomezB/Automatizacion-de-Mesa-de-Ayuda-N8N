# Tasks — c-108 — Paradigma metrico y tratamiento de la clase unitaria

> Governance ALTO. Decisiones y reversibilidad en `design.md`. NO se edita `.tex`
> fuera de `docs/Tesis/v9 (IA)/paper/sections/{04,07,08}`. NO se re-ejecuta el
> clasificador ni servicios externos. Modo TDD estricto en las funciones nuevas
> de `evaluation/`.

## 0. Prerrequisitos (solo lectura)

- [ ] 0.1 Confirmar el Gate 0 c-102 archivado y leer el memo canonico
  `docs/Tesis/Correcciones/numeros-canonicos.md` (Secciones 3.2, 3.5 y 5, items 5 y 6).
- [ ] 0.2 Confirmar con `git status` el arbol limpio y que c-107 ya se aplico
  (dependencia de secuenciacion, D7).
- [ ] 0.3 Registrar el conteo de paginas de partida (`main.pdf` = 103) y la fecha
  de verificacion.
- [ ] 0.4 Verificar si existen etiquetas por analista (doble etiquetado) en
  `data/Corpus Tesis - Hoja 1*.csv` u otra fuente (D5). Registrar el hallazgo.

## 1. Incertidumbre de las metricas por clase (RED -> GREEN -> TRIANGULATE -> REFACTOR)

- [ ] 1.1 RED: escribir test en `evaluation/tests/` que exija los IC por clase
  (precision, sensibilidad, F1) para las clases estimables y `None`/no estimable
  para `Bases de Datos`. Ejecutar y confirmar el fallo.
- [ ] 1.2 GREEN: implementar la funcion pura en `evaluation/metrics.py` que usa
  `intervalo_wilson` para precision/sensibilidad y bootstrap percentil con semilla
  fija y `B >= 2.000` para F1. Ejecutar `pytest` y confirmar verde.
- [ ] 1.3 TRIANGULATE: agregar un segundo caso con datos de juguete y distintos
  conteos; confirmar que el bootstrap es determinista y reproducible.
- [ ] 1.4 REFACTOR: extraer constantes (semilla, `B`, nivel de confianza) y
  limpiar; reejecutar la suite de `evaluation/`.
- [ ] 1.5 Calcular los IC reales sobre `evaluation/predicciones.json` y el corpus,
  y registrar los valores con su procedimiento.

## 2. Incertidumbre de las metricas de conjunto

- [ ] 2.1 RED: test que exija IC bootstrap a nivel de caso para subset accuracy,
  Hamming loss y micro-F1.
- [ ] 2.2 GREEN: implementar el remuestreo a nivel de caso (misma semilla y `B`).
- [ ] 2.3 TRIANGULATE: segundo caso de juguete con verdad multietiqueta; confirmar
  reproducibilidad.
- [ ] 2.4 REFACTOR y reejecutar `evaluation/`.
- [ ] 2.5 Calcular y registrar los IC reales de las tres metricas de conjunto.

## 3. IC del kappa (D5)

- [ ] 3.1 Con el hallazgo de 0.4: si hay etiquetas por analista, RED + GREEN +
  TRIANGULATE del IC por bootstrap del kappa; registrar el valor.
- [ ] 3.2 Si no hay fuente: registrar en el memo que el IC del kappa NO es
  computable desde las fuentes permitidas, con la condicion de reversibilidad.
- [ ] 3.3 Redactar el pasaje de metodologia (4.4/4.8) con el IC o con la
  declaracion de no computabilidad; conservar el rotulo "casi perfecto" (Landis & Koch).

## 4. Registro en el memo canonico (D6)

- [ ] 4.1 Upsert en `docs/Tesis/Correcciones/numeros-canonicos.md`: IC del kappa,
  IC por clase, IC de conjunto y la no-estimabilidad de `Bases de Datos` en los IC.
- [ ] 4.2 Declarar el estado (`vigente`/`condicional`/`no estimable`) de cada valor
  nuevo y su procedencia (archivo/funcion).

## 5. Redaccion de los capitulos (D1)

- [ ] 5.1 `04-marco-metodologico.tex`: declarar el paradigma (referencia
  multietiqueta) y enunciar metricas primarias monoetiqueta y secundarias multietiqueta.
- [ ] 5.2 `07-resultados.tex:108`: reemplazar el parrafo de metricas por un marco
  unico (tabla o texto) con la referencia declarada, la advertencia de penalizacion
  estructural y la no equivalencia micro-F1 vs exactitud.
- [ ] 5.3 `07-resultados.tex` (tabla por clase, `:112-123`): agregar la columna de
  IC y marcar `Bases de Datos` como no estimable.
- [ ] 5.4 `07-resultados.tex`: reportar el macro-F1 de umbral sobre 4 clases
  (`0,6508`) y conservar el de 5 clases (`0,5207`) como informativo.
- [ ] 5.5 `08-discusion.tex:22,28,30,34`: alinear la discusion con el marco
  unificado y la no-estimabilidad de `Bases de Datos`; matizar la comparacion con
  la literatura por diferencia de tarea. No introducir numeros fuera del memo.

## 6. Verificacion y compilacion

- [ ] 6.1 Verificar con `grep` que `04/07/08` no dejan micro-F1 presentado como
  equivalente de la exactitud ni `0,0000` de `Bases de Datos` como evidencia.
- [ ] 6.2 Recalcular en un script de solo lectura y comparar contra el memo: IC del
  kappa, IC por clase, IC de conjunto, macro-F1 4 y 5 clases.
- [ ] 6.3 Compilar con Docker:
  `docker run --rm -v "/home/skywalker/Desktop/notas/Tesis/Automatizacion-de-Mesa-de-Ayuda-N8N/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`
  y confirmar 0 errores fatales.
- [ ] 6.4 Registrar el conteo de paginas resultante (`main.pdf`).
- [ ] 6.5 Ejecutar la suite de `evaluation/` (`cd evaluation; pytest`) y confirmar
  verde.
- [ ] 6.6 Documentar en el commit que c-108 depende de c-107 y comparte archivos
  con las demas ramas de contenido (D7).
