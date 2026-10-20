# Proposal: c-93 — Rigor metodológico del Capítulo 4

## Why

Una auditoría del Capítulo 4 (Marco metodológico) detectó que el documento
declara un diseño metodológico cuya aritmética y supuestos no son reproducibles:
el tamaño muestral declarado (95 % de confianza, 6,5 % de margen, corrección por
finitud) no reproduce `n = 200`; la cobertura de pruebas unitarias se afirma
(«superior al 80 %», «87 %») sin publicar el reporte ni el comando que la genera;
no existe un análisis de potencia a priori pese a que el propio capítulo 4
identifica el tamaño muestral como amenaza a la validez de conclusión; y la
rotación de operadores entre las dos mitades del corpus se presenta como
mitigación cuando, con dos operadores y dos mitades, queda confundida con el
efecto del operador. Faltan además criterios de exclusión del corpus, la
declaración de los analistas etiquetadores y la demarcación entre el método de
investigación y el método de construcción del artefacto. c-93 corrige el aparato
metodológico del Capítulo 4 y el tercer criterio del umbral del 85 % en §1.6.

## What Changes

### Grupo A — Rigor cuantitativo (Altas)

| Id | Corrección | Evidencia |
|----|-----------|-----------|
| A-07 | §4.4 declara 95 % de confianza, 6,5 % de margen y corrección por finitud, pero no publica el cálculo ni la proporción esperada. Con `N=3.700`, `z=1,96`, `p=0,5`, `e=0,065` el tamaño no es 200. Publicar la fórmula y los insumos (y la proporción esperada), o corregir el margen declarado para reproducir 200 | `04-marco-metodologico.tex:43,45` |
| A-08 | §4.5 afirma cobertura de pruebas unitarias «superior al 80 %» y §6.7 «87 %» (pytest-cov 5.0.0); ninguno publica el reporte ni el comando generador. Publicar el reporte/comando o retraer las cifras | `04-marco-metodologico.tex:51`; `06-implementacion.tex:83` |
| A-09 | No existe análisis de potencia estadística a priori, pese a que §4.8 identifica el tamaño muestral (`n=200`) como amenaza a la validez de conclusión. Agregar el análisis de potencia | `04-marco-metodologico.tex:83` |
| A-10 | §4.2 declara «rotación de operadores entre las dos mitades del corpus» como mitigación del efecto de aprendizaje; con dos operadores y dos mitades la rotación queda confundida con el efecto del operador. Reconocer el confundido o rediseñar la afirmación | `04-marco-metodologico.tex:14,77` |
| A-03 (parcial) | §1.6, tercer criterio del umbral del 85 %, confunde el contraste de hipótesis sobre tiempos (`H0`/`H1` de §1.4) con el umbral de exactitud del clasificador; no existe «zona de rechazo» para la exactitud. Reformular el criterio (coordinar con c-77 B1, que reformula `H1`) | `01-introduccion.tex:46` |

### Grupo M — Rigor cualitativo y demarcación (Medias)

| Id | Corrección | Evidencia |
|----|-----------|-----------|
| M-05 | No hay criterios de exclusión de incidentes del corpus (duplicados, descripciones vacías, multicategoría), pese a que §7.4 identifica descripciones cortas y mezcla de categorías como patrones de error dominantes. Declarar los criterios de exclusión | `07-resultados.tex:108`; `04-marco-metodologico.tex:41-47` |
| M-06 | §4.9 (Scrumban) es gestión de proyecto, no metodología de investigación. Reubicar o demarcar para que el método de estudio quede separado del método de construcción del artefacto | `04-marco-metodologico.tex:85-100` |
| M-07 | Los dos analistas que etiquetaron el corpus no están declarados, ni su independencia respecto de los autores, ni si uno de ellos es también operador del brazo manual. Declarar | `04-marco-metodologico.tex:47,53` |

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `tesis-document`: rigor metodológico verificable del Capítulo 4 y del criterio
  del umbral del 85 % en §1.6 — cálculo reproducible del tamaño muestral,
  evidencia de cobertura de pruebas, análisis de potencia a priori, tratamiento
  honesto del confundido de la rotación de operadores, criterios de exclusión del
  corpus, demarcación método de investigación vs. construcción del artefacto,
  declaración de los analistas etiquetadores y reformulación del criterio de
  exactitud sin «zona de rechazo».

## Impact

Solo documentación (NO se toca `App/**`):

- `docs/Tesis/v9 (IA)/paper/sections/04-marco-metodologico.tex` (§4.2, §4.4,
  §4.5, §4.8, §4.9; §4.7 solo si corresponde).
- `docs/Tesis/v9 (IA)/paper/sections/01-introduccion.tex` (§1.6).
- `main.pdf` (recompilado en Overleaf).

Coordinación (sin duplicar alcance):

- c-76 es dueño de la ventana temporal (T6) y del instrumento único de medición
  manual (T7) → c-93 los referencia, no los redefine.
- c-77 es dueño de la reformulación de `H1` (B1) y de la aritmética del universo
  trimestral (A7) → c-93 reformula el criterio de exactitud de §1.6 sin redefinir
  `H1` ni el universo; el criterio de exclusión (M-05) y la ventana (c-76) se
  citan.
- Fuente de verdad de datos: `data/corpus_evaluacion_pseudonimizado.json` y
  `evaluation/report.md` (no se alteran).

## Rollback Plan

`git checkout --` sobre los dos `.tex` afectados, o `git revert` del commit del
change. Los artefactos OPSX se descartan con el directorio del change.

## Success Criteria

- [ ] §4.4 publica la fórmula del tamaño muestral con sus insumos (incluida la
      proporción esperada) y el valor declarado es reproducible; o el margen
      declarado se corrige para reproducir `n = 200`.
- [ ] §4.5 y §6.7 publican el reporte de cobertura y el comando que lo genera, o
      retraen las cifras.
- [ ] §4.8 (o el lugar metodológico correcto) contiene un análisis de potencia a
      priori con sus supuestos y el efecto mínimo detectable.
- [ ] §4.2/§4.8 reconocen el confundido de la rotación de operadores (o
      rediseñan la afirmación); no se presenta como mitigación no calificada.
- [ ] §4.4 declara los criterios de exclusión del corpus (duplicados,
      descripciones vacías, multicategoría).
- [ ] §4.9 queda demarcado (o reubicado) de modo que el método de investigación
      sea distinguible del método de construcción del artefacto.
- [ ] §4.4 declara los dos analistas etiquetadores, su independencia respecto de
      los autores y si alguno opera el brazo manual.
- [ ] §1.6 reformula el tercer criterio del umbral del 85 % sin invocar una
      «zona de rechazo» de exactitud ni el contraste de tiempos; coherente con
      c-77 B1.
- [ ] `pdf` recompilado en Overleaf sin errores fatales.
- [ ] `openspec validate c-93-tesis-metodologia-rigor --strict` pasa.
