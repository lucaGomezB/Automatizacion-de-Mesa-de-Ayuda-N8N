## ADDED Requirements

### Requirement: Ejemplar de la defensa sin cambios por la integracion del clasificador supervisado

El ejemplar que se defiende (`docs/Tesis/v10 (IA)/paper/sections/*.tex` en la version que cierra la entrega) MUST NOT modificarse por la integracion del clasificador supervisado ni por su veredicto, y la declaracion de configuracion entregada de ese ejemplar SHALL seguir declarando el hibrido. La linea SHALL figurar solo como trabajo futuro, con el texto que dejan los requisitos vigentes tras archivar `c-235`; este requisito MUST NOT exigir texto adicional en `subsec:clasificador-supervisado`, `subsec:frontera-sistemas` ni `subsec:corpus-independiente`.

#### Scenario: Ejemplar intacto

- **WHEN** se compara `docs/Tesis/v10 (IA)/paper/sections` antes y despues de aplicar este change
- **THEN** no hay diferencias atribuibles a este change
- **AND** la configuracion entregada declarada sigue siendo el hibrido

### Requirement: Veredicto del clasificador supervisado informado solo en una version posterior con compuertas cerradas

Una version de la tesis posterior a la defensa SHALL informar el contraste y el veredicto de la regla pre-registrada (reemplazar, complementar o conservar, incluido «no supera al hibrido») solo si las compuertas de procedencia y etica y legal constan cerradas y la constancia del pre-registro consta en custodia del director. Cuando lo informe, el texto SHALL rotular el conjunto (corpus probabilistico acreditado con referencia por mayoria), SHALL declarar donde corrio cada sistema y que textos se enviaron a la Gemini API, y, si el veredicto no es reemplazar, SHALL declarar que el hibrido sigue siendo el clasificador entregado. El texto MUST NOT presentar el modelo supervisado como entregado si el veredicto no es reemplazar, MUST NOT usar cifras ni artefactos retirados por `c-235` y MUST NOT introducir identificadores internos `c-NNN` en el cuerpo. Si el veredicto es reemplazar, la declaracion de configuracion entregada de esa version SHALL revisarse con los autores y actualizarse.

#### Scenario: Sin compuertas cerradas no hay informe

- **WHEN** alguna compuerta no consta cerrada o falta la constancia del pre-registro
- **THEN** la tesis no informa el contraste ni el veredicto

#### Scenario: Veredicto declarado sin sobreafirmar

- **WHEN** una version posterior informa el veredicto
- **THEN** figura el veredicto con su conjunto rotulado y, si no es reemplazar, que el hibrido sigue siendo el clasificador entregado
- **AND** no se presenta el modelo supervisado como entregado ni se afirma una mejora no medida
