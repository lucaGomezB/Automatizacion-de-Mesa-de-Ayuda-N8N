## ADDED Requirements

### Requirement: Los tests del frontend no realizan solicitudes de red reales

La suite de pruebas del frontend SHALL aislar por completo la red. Ninguna prueba SHALL realizar una solicitud HTTP real a un backend, a un CDN ni a un servicio externo. Las capas de red (Axios u otra) SHALL mockearse en el limite de red, y cualquier intento de request no mockeado SHALL fallar la prueba en lugar de depender de la conectividad.

#### Scenario: Un request no mockeado falla la prueba

- **WHEN** una prueba dispara una llamada que no fue mockeada
- **THEN** la prueba falla por el intento de red en lugar de resolver contra un servicio real

#### Scenario: La suite pasa sin backend ni red

- **WHEN** se ejecuta la suite del frontend con la red deshabilitada
- **THEN** todas las pruebas pasan sin depender de conectividad
