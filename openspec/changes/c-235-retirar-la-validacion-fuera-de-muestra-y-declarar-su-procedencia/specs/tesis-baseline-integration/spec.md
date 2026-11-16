## MODIFIED Requirements

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

## REMOVED Requirements

### Requirement: TLB-01 — Método de la línea de base en el marco metodológico
**Reason**: La línea de base se probó sobre los 103 casos del corpus fuera de muestra retirado (K-01); no hay una prueba limpia alternativa porque se entrenó con los 200 casos de ajuste.
**Migration**: Se elimina el párrafo de `04-marco-metodologico.tex` (L113); ver TLB-04 (MODIFIED) y "Validacion fuera de muestra propuesta como trabajo futuro con procedencia acreditable" en `tesis-document`.

### Requirement: TLB-02 — Resultados trazables a artefactos versionados
**Reason**: La tabla de la línea de base frente al híbrido se calcula sobre el corpus retirado (K-01).
**Migration**: Se retiran `tab:linea-base-clasica` y el contraste pareado; los valores del memo pasan a `retirado` (requisito aditivo de `tesis-numeros-canonicos`); los artefactos se conservan rotulados (OOS-026).

### Requirement: TLB-03 — Lectura acotada y honesta
**Reason**: Sin resultado vigente de la línea de base no hay lectura que acotar (K-01).
**Migration**: La hipótesis de eficiencia queda "sin contraste limpio" ("Estado declarado de las hipotesis subsidiarias", MODIFIED en `tesis-document`).

### Requirement: TLB-05 — Trazabilidad y preparación para c-206
**Reason**: La preparación para repetir la comparación con la referencia arbitrada pierde objeto con el retiro (K-01).
**Migration**: La trazabilidad del retiro se registra en `dictamen-correcciones.md` (entrada de c-235); `verify_citations.py` sigue siendo la verificación de citas.
