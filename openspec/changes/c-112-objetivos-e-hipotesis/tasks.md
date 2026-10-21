# Tasks — c-112-objetivos-e-hipotesis

> Governance ALTO. Las decisiones editoriales y su reversibilidad están en
> `design.md`. NO se edita el memo canónico, `CHANGES.md`, `dictamen-correcciones.md`
> ni ningún archivo fuera de `docs/Tesis/v9 (IA)/paper/`. En la fase de propuesta NO
> se edita ningún `.tex`.

## 0. Prerrequisitos (solo lectura)

- [ ] 0.1 Confirmar la fuente de verdad numérica en
  `docs/Tesis/Correcciones/numeros-canonicos.md` (Secciones 3.1 a 3.6 y 7) y
  registrar que c-102 y c-107 están archivados.
- [ ] 0.2 Registrar el conteo de páginas de partida (`main.pdf` = 104) y la fecha de
  verificación (2026-10-21).
- [ ] 0.3 Confirmar con `git status` que el árbol está limpio antes de empezar.
- [ ] 0.4 Confirmar que la imagen Docker `texlive-thesis` existe
  (`docker image inspect texlive-thesis`).

## 1. Desdoblamiento de la hipótesis principal (D1, D2)

- [ ] 1.1 `01-introduccion.tex` §1.4: reemplazar la hipótesis principal conjuntiva
  por tres sub-hipótesis contrastables (tiempo; intervención humana; exactitud/F1),
  cada una con su contraste y su criterio de falsación.
- [ ] 1.2 Sub-hipótesis de tiempo: conservar `H0: M_manual = M_auto` y
  `H1: M_manual > M_auto` sobre las medianas del tiempo de registro, con la
  falsación ("no rechazar `H0`") y los valores vigentes (`W = 363`,
  `p = 3,08e-32`, `r = 0,9639`).
- [ ] 1.3 Sub-hipótesis de intervención humana: declarar su criterio de falsación y
  su estado **NO MEDIDA** (c-107); no cuantificar la proporción; no reintroducir el
  `9,5 %`.
- [ ] 1.4 Sub-hipótesis de exactitud/F1: formularla como criterio de desempeño
  (`85 %`/`0,85`) verificado contra el intervalo de confianza de Wilson (exactitud
  `73,5 %`, IC `[67,0 %; 79,1 %]`; macro-F1 `0,5207`); no invocar la zona de rechazo
  del contraste de tiempos.
- [ ] 1.5 Verificar que la hipótesis principal ya no se presenta como una
  conjunción indivisible ni se declara confirmada o refutada en bloque.

## 2. Objetivos (D3, D4, D5, D6)

- [ ] 2.1 `01-introduccion.tex` §1.5: reformular el objetivo general como
  evaluación de la viabilidad y el desempeño, con el desarrollo e implementación
  como medio; eliminar "desarrollar e implementar" como objetivo.
- [ ] 2.2 `01-introduccion.tex` §1.6: separar en el segundo objetivo la acción de
  implementar el clasificador del umbral de desempeño, que pasa a criterio de éxito
  contingente verificable contra el resultado observado y su intervalo de confianza.
- [ ] 2.3 `01-introduccion.tex` §1.6: reescribir el quinto objetivo en clave
  verificable y reproducible; eliminar el calificador "exhaustivamente".
- [ ] 2.4 `01-introduccion.tex` §1.6: agregar el objetivo específico de análisis de
  errores y calibración de la confianza, alineado con el Capítulo de resultados.
- [ ] 2.5 Verificar que los objetivos siguen siendo mutuamente consistentes y
  alineados con la pregunta de investigación.

## 3. Estado de la hipótesis y tabla de objetivos (D2, D7)

- [ ] 3.1 `00-resumen.tex`: declarar la sub-hipótesis confirmada (tiempo), la
  refutada (exactitud/F1) y la no medida (intervención humana); sin `9,5 %`; no
  presentar la hipótesis como plenamente confirmada.
- [ ] 3.2 `09-conclusiones.tex`: declarar el estado por sub-hipótesis, coherente
  con 3.1 y anclado en las métricas de clasificación reportadas.
- [ ] 3.3 `09-conclusiones.tex` (§Cumplimiento): incorporar la tabla de objetivos,
  cumplimiento y evidencia; el segundo objetivo figura como **no alcanzado** y la
  tabla es coherente con el estado parcial de la hipótesis.

## 4. Verificación de contenido

- [ ] 4.1 Buscar `9,5 %`, `3.700` y `45,0` en `00-resumen.tex`,
  `01-introduccion.tex` y `09-conclusiones.tex` y confirmar que no reaparecen como
  resultado vigente.
- [ ] 4.2 Confirmar que el objetivo general no dice "desarrollar e implementar" y
  que el quinto objetivo no contiene "exhaustivamente".
- [ ] 4.3 Confirmar que existe el objetivo de análisis de errores y calibración y
  que la tabla de objetivos cubre el objetivo general y todos los específicos.
- [ ] 4.4 Confirmar que ningún `.tex` fuera de `docs/Tesis/v9 (IA)/paper/` fue
  tocado y que no se modificó el memo canónico ni `CHANGES.md`.

## 5. Compilación y presupuesto de páginas

- [ ] 5.1 Compilar con la imagen local:
  `docker run --rm -v "<repo>/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`.
- [ ] 5.2 Confirmar cero errores fatales y cero referencias indefinidas; registrar
  el conteo de páginas. Parte de `104`; **c-116 reduce a `≤ 100`** DESPUÉS. Este
  change MUST NOT aumentar el conteo; si sube, usar la variante de redacción más corta.

## 6. Verificación del change (OpenSpec)

- [ ] 6.1 Ejecutar `openspec validate c-112-objetivos-e-hipotesis --strict`.
- [ ] 6.2 Ejecutar `openspec status --change c-112-objetivos-e-hipotesis --json` y
  confirmar `isPlanningComplete: true`.
- [ ] 6.3 Confirmar con `git status` que NO se modificó el memo canónico,
  `CHANGES.md` ni `dictamen-correcciones.md`.
