## ADDED Requirements

### Requirement: Preservacion de terminos tecnicos, productos y marcas

La función `pseudonymize` SHALL preservar los terminos tecnicos, nombres de productos y marcas reconocidas del dominio (por ejemplo `Windows Server`, `Active Directory`, `SQL Server`, `Google Chrome`), de modo que NO sean reemplazados por la etiqueta `[PERSONA]`. La preservacion MUST NOT depender del orden de aplicacion de los patrones y MUST NOT afectar el reemplazo de nombres propios reales ni de datos personales.

#### Scenario: Producto de infraestructura no se enmascara como persona

- **WHEN** se invoca `pseudonymize("Falla en Windows Server y Active Directory", [])`
- **THEN** el texto resultante conserva `Windows Server` y `Active Directory` y el conteo de la categoría `persona` es cero

#### Scenario: Base de datos y navegador no se enmascaran como persona

- **WHEN** el texto contiene `SQL Server` o `Google Chrome`
- **THEN** esos terminos permanecen en el texto y no se cuentan como reemplazos de la categoría `persona`

#### Scenario: Un nombre propio real se sigue enmascarando

- **WHEN** el texto contiene un nombre de persona real junto a terminos tecnicos preservados
- **THEN** el nombre real se reemplaza por `[PERSONA]` y los terminos tecnicos se conservan
