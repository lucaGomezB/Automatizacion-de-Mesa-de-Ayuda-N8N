## ADDED Requirements

### Requirement: Reemplazo de nombres propios con exclusion de sectores canonicos
La función `pseudonymize` SHALL reemplazar los nombres propios de personas por la etiqueta `[PERSONA]` (conteo en categoría `persona`), según el patrón heurístico basado en expresiones regulares definido en el diseño. El conjunto de exclusión de personas MUST incluir los cinco nombres canónicos de sector, de modo que nunca se enmascaren como `[PERSONA]`. El sistema SHALL aceptar explícitamente el tradeoff de cobertura del enfoque regex (posibles falsos positivos y falsos negativos sobre nombres en español), documentado en `docs/pseudonymization.md`; NO SHALL incorporar NER ni modelos de aprendizaje automático.

#### Scenario: Nombre y apellido se reemplazan
- **WHEN** se invoca `pseudonymize("El usuario Juan Pérez reportó el problema", [])`
- **THEN** el resultado contiene `[PERSONA]` y NO contiene `Juan Pérez`

#### Scenario: Las cinco categorías de incidente nunca se pseudonimizan como persona
- **WHEN** se invoca `pseudonymize` sobre un texto que menciona los sectores del dominio `"Seguridad Informatica"`, `"Soporte Tecnico Hardware"`, `"Soporte Tecnico Software"`, `"Bases de Datos"` o `"Sistemas"` sin nombres propios de personas
- **THEN** esas cadenas de sector permanecen intactas y NO son reemplazadas por `[PERSONA]`

## REMOVED Requirements

### Requirement: Reemplazo de nombres propios
**Reason**: El conjunto de exclusión listaba las tres categorías anteriores; con la nueva taxonomía de cinco sectores ya no protege los nombres canónicos vigentes.

**Migration**: Reemplazado por "Reemplazo de nombres propios con exclusion de sectores canonicos", que extiende la exclusión a los cinco sectores.
