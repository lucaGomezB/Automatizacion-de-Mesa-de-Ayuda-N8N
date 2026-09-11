## ADDED Requirements

### Requirement: Dashboard page with five-sector distribution chart
The frontend SHALL render a pie or donut chart (`SectorPieChart`) that shows the distribution of incidents across the five canonical sectors: `Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos`, and `Sistemas`.

#### Scenario: Pie chart renders with five sectors
- **WHEN** the summary data is loaded and contains non-zero counts for sectors
- **THEN** the `SectorPieChart` SHALL display one slice per sector present, with proper proportions and sector labels

#### Scenario: Pie chart with zero-value sector
- **WHEN** one sector has zero incidents in the selected range
- **THEN** the `SectorPieChart` SHALL still display the sector with a zero-value slice or omit it gracefully

#### Scenario: Pie chart tolerates an unknown sector label
- **WHEN** the distribution contains a sector name outside the five canonical names
- **THEN** the `SectorPieChart` SHALL render it with a default color without throwing

## REMOVED Requirements

### Requirement: Dashboard page with sector distribution chart
**Reason**: El gráfico debe contemplar los cinco sectores canónicos; el requisito anterior estaba fijado a los tres sectores de la taxonomía eliminada.

**Migration**: Reemplazado por "Dashboard page with five-sector distribution chart", que mantiene el comportamiento de la torta y cubre los cinco sectores.
