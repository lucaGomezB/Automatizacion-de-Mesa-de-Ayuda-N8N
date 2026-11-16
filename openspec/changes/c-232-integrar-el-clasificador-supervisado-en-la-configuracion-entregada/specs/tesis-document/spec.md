## ADDED Requirements

### Requirement: Veredicto honesto del clasificador supervisado en la configuracion entregada

`07-resultados.tex` SHALL informar el contraste cabeza a cabeza del modelo supervisado contra
el hibrido vigente, por sistema y por lectura (referencia retenida y corpus de prevalencia
natural), con sus intervalos de confianza, rotulado; MUST NOT presentar una sola lectura como
si la otra no existiera. `08-discusion.tex` SHALL acotar el alcance y las limitaciones del
veredicto, sin afirmar mas de lo medido. `09-conclusiones.tex` y `10-recomendaciones.tex`
SHALL declarar el **veredicto** de la regla pre-registrada (reemplazar, complementar o
conservar), incluido el resultado «no supera al hibrido», y su consecuencia sobre la
configuracion entregada: si el veredicto no es reemplazar, el texto SHALL declarar que el
hibrido sigue siendo el clasificador entregado. La prosa SHALL declarar que la linea depende
de `c-228`, `c-229` y `c-230` y de **datos que todavia no existen**. El texto MUST NOT
presentar el modelo supervisado como entregado si el veredicto no es reemplazar, MUST NOT
introducir identificadores internos de cambio `c-NNN` en el cuerpo y MUST NOT cambiar
`0,6893`, el macro-F1 `0,7024` ni el veredicto del umbral `0,85`. Si el veredicto es
reemplazar, se SHALL revisar con los autores la declaracion de la configuracion entregada
(Anexo B / nota de version) y actualizarla.

#### Scenario: Resultados informan el contraste

- **WHEN** se leen los resultados
- **THEN** figura el contraste cabeza a cabeza por sistema y por lectura, con sus intervalos, rotulado
- **AND** ninguna lectura se presenta como si la otra no existiera

#### Scenario: Veredicto declarado sin sobreafirmar

- **WHEN** se leen conclusiones y recomendaciones
- **THEN** figura el veredicto (reemplazar, complementar o conservar) y, si no es reemplazar, que el hibrido sigue siendo el clasificador entregado
- **AND** no se presenta el modelo supervisado como entregado ni se afirma una mejora no medida

#### Scenario: Declaracion de configuracion entregada solo al reemplazar

- **WHEN** el veredicto es reemplazar
- **THEN** la declaracion de configuracion entregada (Anexo B / nota de version) se revisa con los autores y se actualiza
- **AND** si el veredicto no es reemplazar, la declaracion no cambia
