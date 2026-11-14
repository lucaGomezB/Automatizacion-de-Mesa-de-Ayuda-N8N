## ADDED Requirements

### Requirement: Contraste de la hipótesis subsidiaria de integración multicanal declarado

`01-introduccion.tex` SHALL declarar el estado de la hipótesis subsidiaria de integración multicanal de forma coherente con el contraste efectivamente realizado, de modo que el criterio 1 del dictamen (hipótesis subsidiarias sin contraste) no siga descontándose por una subsidiaria declarada sin medir. El enunciado SHALL informar que la dimensión de capacidad bajo carga concurrente quedó contrastada con un test de carga reproducible y de costo cero, con su veredicto de tres vías, y SHALL declarar que la dimensión de complejidad operativa percibida permanece sin instrumento. MUST NOT afirmar que la hipótesis se confirma en su totalidad ni que se midió la complejidad percibida; MUST NOT dejar el enunciado y el veredicto mezclados en la introducción.

#### Scenario: Estado coherente con el contraste realizado

- **WHEN** se lee el enunciado de la hipótesis subsidiaria de integración multicanal en `01-introduccion.tex`
- **THEN** declara que la dimensión de capacidad se contrastó con el test de carga y su veredicto
- **AND** declara que la complejidad operativa percibida no se midió

#### Scenario: Sin descuento por subsidiaria sin contraste

- **WHEN** se busca en el cuerpo una afirmación de que la hipótesis subsidiaria de integración multicanal no se contrastó
- **THEN** esa afirmación no aparece sin la calificación de la dimensión medida
- **AND** el texto remite al contraste de capacidad registrado en el memo canónico

#### Scenario: Enunciado y veredicto separados

- **WHEN** se lee la introducción
- **THEN** el enunciado de la hipótesis no incorpora su veredicto
- **AND** el veredicto figura en los resultados y las conclusiones
