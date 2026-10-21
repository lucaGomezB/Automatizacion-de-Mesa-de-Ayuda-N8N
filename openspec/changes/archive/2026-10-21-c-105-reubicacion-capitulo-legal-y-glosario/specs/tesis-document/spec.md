# tesis-document — Delta (c-105)

## ADDED Requirements

### Requirement: Ubicación del capítulo de consideraciones éticas y legales

El capítulo de consideraciones éticas y legales SHALL ubicarse dentro del flujo
argumental del cuerpo, antes del capítulo de resultados, y MUST NOT quedar
después de conclusiones y recomendaciones. La reubicación SHALL realizarse
reordenando la línea `\input` correspondiente en `main.tex`, sin renombrar el
archivo fuente. La numeración del capítulo y de los capítulos posteriores SHALL
recalcularse automáticamente, y toda remisión cruzada SHALL seguir resolviéndose
por `\label`/`\autoref`, sin edición manual de números.

#### Scenario: Capítulo legal antes de resultados

- **WHEN** se lee el orden de los `\input` de `sections/` en `main.tex`
- **THEN** `sections/11-aspectos-legales.tex` aparece después de
  `sections/06-implementacion.tex` y antes de `sections/07-resultados.tex`
- **AND** no aparece después de `sections/09-conclusiones.tex` ni de
  `sections/10-recomendaciones.tex`

#### Scenario: Numeración recalculada y referencias intactas

- **WHEN** se compila el documento tras la reubicación
- **THEN** el capítulo legal recibe la numeración correspondiente a su nueva
  posición y los capítulos posteriores se renumeran
- **AND** el log no contiene "undefined reference" ni "multiply defined label"
- **AND** las remisiones a `\autoref{sec:aspectos-legales}` siguen resolviendo,
  sin edición manual de números

#### Scenario: Capítulo fuera de la condición de apéndice encubierto

- **WHEN** se lee el índice general del PDF compilado
- **THEN** el capítulo de consideraciones éticas y legales figura antes de
  resultados
- **AND** no figura como último capítulo del cuerpo, después de las conclusiones
  y las recomendaciones

### Requirement: Glosario de siglas y acrónimos

El documento SHALL incluir una sección "Glosario de siglas y acrónimos" en el
material preliminar, después de los índices y antes del cuerpo. El glosario
SHALL listar en orden alfabético cada sigla o acrónimo usado en el cuerpo con su
expansión completa. Toda sigla presente en `sections/*.tex` SHALL tener una
entrada en el glosario y toda entrada SHALL corresponder a una sigla efectivamente
usada en el cuerpo.

#### Scenario: Cobertura completa del glosario

- **WHEN** se comparan las siglas relevantes del cuerpo (`sections/*.tex`) con
  las entradas del glosario
- **THEN** no queda ninguna sigla del cuerpo sin entrada
- **AND** no queda ninguna entrada del glosario sin uso en el cuerpo

#### Scenario: Ubicación y formato del glosario

- **WHEN** se lee el índice general y el material preliminar del PDF
- **THEN** el glosario aparece listado después de los índices
- **AND** cada entrada presenta la sigla y su expansión completa, en orden
  alfabético

#### Scenario: Glosario sin romper la compilación ni el presupuesto de referencias

- **WHEN** se compila el documento con el glosario agregado
- **THEN** el log no contiene "undefined reference" ni "multiply defined label"
- **AND** no se introducen glosarios automáticos que requieran un paso de build
  adicional fuera del `latexmk` vigente
