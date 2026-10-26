## ADDED Requirements

### Requirement: Portabilidad del CLI de sensibilidad entre versiones de Python 3.12

El CLI `python -m evaluation.sensibilidad_ajustes` SHALL aceptar los nombres exactos de
sus opciones con independencia de la política de abreviaturas del módulo `argparse` de
la versión de parche de Python 3.12. El parser de nivel superior SHALL deshabilitar la
resolución por prefijo (`allow_abbrev=False`), de modo que `prompt --brazo vigente` se
interprete siempre como la opción del subcomando y no como una abreviatura ambigua de
`--brazo-vigente` o `--brazo-sin-reglas`. La suite SHALL incluir una prueba de regresión
que fije ese comportamiento y que pase en Python 3.12.3 y en Python 3.12.15.

El modo `python -m evaluation.run_evaluation --solo-tiempos` SHALL informar la ausencia
del reporte con un error de línea de comandos legible y un código de salida distinto de
cero, sin propagar una traza cruda de `FileNotFoundError`.

#### Scenario: Abreviatura ambigua no se resuelve por prefijo

- **WHEN** se ejecuta `python -m evaluation.sensibilidad_ajustes prompt --brazo vigente` en Python 3.12.3
- **THEN** el parser reconoce `--brazo` como opción del subcomando `prompt`
- **AND** no falla con `error: ambiguous option: --brazo`

#### Scenario: Opciones de nivel superior con nombre exacto

- **WHEN** se ejecuta el CLI con `--brazo-vigente` o `--brazo-sin-reglas`
- **THEN** el parser las reconoce por su nombre exacto
- **AND** un prefijo no exacto que colisione con ambas no se resuelve silenciosamente

#### Scenario: Prueba de regresión en la suite

- **WHEN** se ejecuta `cd evaluation && pytest tests/test_sensibilidad_ajustes.py -q` en Python 3.12.3
- **THEN** las pruebas del CLI pasan sin fallos
- **AND** existe una prueba que falla si se elimina `allow_abbrev=False` del parser de nivel superior

#### Scenario: Reporte ausente en modo solo tiempos

- **WHEN** se ejecuta `python -m evaluation.run_evaluation --solo-tiempos` sin un `report.md` previo
- **THEN** el proceso termina con un código distinto de cero
- **AND** imprime un mensaje de error legible sin una traza cruda de `FileNotFoundError`
