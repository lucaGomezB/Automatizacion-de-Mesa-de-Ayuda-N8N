## ADDED Requirements

### Requirement: Modelo supervisado local como proveedor seleccionable

El registro de proveedores SHALL admitir el clasificador supervisado congelado por
`supervised-classifier-integration` (SCI-001) como un proveedor o etapa **seleccionable por
configuracion**, resuelto por el mismo mecanismo del registro y sin editar el clasificador. La
seleccion MUST NOT alterar el contrato canonico: los cinco sectores exactos, el esquema del
resultado, el prompt, los parametros de inferencia y el gate permanecen intactos. El proveedor
por defecto MUST seguir resolviendo al clasificador vigente, de modo que sin configuracion
explicita el comportamiento no cambie; el default SHALL resolverse al modelo supervisado solo
si la regla de decision pre-registrada de `delivered-classifier-decision` determina reemplazar.
Un nombre de proveedor no registrado MUST seguir fallando de forma explicita en la
inicializacion.

#### Scenario: El registro admite el proveedor supervisado

- **WHEN** se configura el clasificador supervisado congelado como proveedor
- **THEN** el registro lo resuelve a una implementacion concreta sin editar el clasificador
- **AND** la clasificacion conserva el contrato canonico

#### Scenario: El default no cambia salvo reemplazo

- **WHEN** no se configura ningun proveedor distinto y el veredicto no es reemplazar
- **THEN** el sistema sigue resolviendo al clasificador vigente
- **AND** la evidencia congelada de la configuracion por defecto permanece valida

#### Scenario: Proveedor desconocido

- **WHEN** se configura un nombre de proveedor que el registro no reconoce
- **THEN** el sistema falla con un error explicito en la inicializacion
- **AND** no arranca con un proveedor silenciosamente inexistente
