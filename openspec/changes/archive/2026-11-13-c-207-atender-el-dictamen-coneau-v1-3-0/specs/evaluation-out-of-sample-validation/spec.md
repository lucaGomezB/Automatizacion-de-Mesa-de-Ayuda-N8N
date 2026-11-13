## ADDED Requirements

### Requirement: OOS-019 — Acuerdo entre los etiquetadores E3 y E4

El análisis de c-207 SHALL calcular, sobre los casos del doble etiquetado independiente, la
proporción de acuerdo observada entre `E3` y `E4` en el sector principal y el kappa de Cohen
con sus IC asintótico y bootstrap mediante `evaluation/kappa.py::kappa_cohen`. La cantidad de
casos concordantes SHALL coincidir con el n efectivo declarado por c-191 (`103` de `150`); si
no coincide, el análisis MUST fallar y no producir salidas. El valor SHALL rotularse como
fiabilidad entre etiquetadores, distinto del kappa del clasificador contra la referencia.

#### Scenario: Concordancia con el n efectivo

- **WHEN** el análisis lee `doble_etiquetado_independiente.csv`
- **THEN** cuenta `103` casos concordantes de `150` y reporta el kappa con sus IC

#### Scenario: Inconsistencia detectada

- **WHEN** la cantidad de concordantes difiere del n efectivo de c-191
- **THEN** el análisis termina con error y no escribe los archivos de salida
