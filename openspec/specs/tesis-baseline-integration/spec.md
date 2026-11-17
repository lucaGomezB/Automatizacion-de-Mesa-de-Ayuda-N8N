# tesis-baseline-integration Specification

## Purpose
TBD - created by archiving change c-213-integrar-la-linea-de-base-en-la-tesis. Update Purpose after archive.

## Requirements

### Requirement: TLB-04 — Ninguna afirmación de inexistencia de la comparación

Ningún pasaje de la tesis MUST afirmar de forma plana que el esquema híbrido nunca se comparó contra un clasificador supervisado: la comparación con la línea de base clásica (TF-IDF y regresión logística) se realizó sobre el corpus fuera de muestra retirado y SHALL declararse, en la nota de versiones (`subsec:nota-versiones`), como realizada en las versiones 1.3.0 a 1.5.2 y retirada con ese corpus. Ningún pasaje MUST presentar esa comparación ni sus cifras como evidencia vigente. Las recomendaciones y el trabajo futuro SHALL enumerar como pendiente la comparación con una línea de base clásica y con el brazo de modelo solo sobre un corpus de procedencia acreditable.

#### Scenario: Comparación retirada sin cifras vigentes

- **WHEN** se buscan en `sections/*.tex` `tab:linea-base-clasica`, `tab:robustez-linea-base` y las cifras de la línea de base
- **THEN** no hay coincidencias fuera de `subsec:nota-versiones`

#### Scenario: Grep de afirmaciones obsoletas

- **WHEN** se buscan en `sections/*.tex` las expresiones "no se comparó", "ausencia de una línea de base" y "No se realizó una comparación directa"
- **THEN** ninguna aparece sin la declaración de que la comparación se realizó y se retiró

#### Scenario: Comparación pendiente enumerada

- **WHEN** se lee `subsec:corpus-independiente`
- **THEN** figura la comparación con una línea de base clásica y con el brazo de modelo solo como trabajo futuro sobre un corpus acreditable
