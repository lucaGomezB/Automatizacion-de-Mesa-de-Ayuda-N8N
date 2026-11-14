## REMOVED Requirements

### Requirement: Tabla de la validación fuera de muestra y estado del arbitraje

**Reason**: el requisito exigía declarar que el arbitraje de los casos discordantes por un tercer
etiquetador no se ejecutó y quedaba diferido, y su escenario «Arbitraje declarado como diferido»
exigía no informar ningún resultado del arbitraje. El arbitraje se ejecutó (`64` casos arbitrados
por `E5`, corpus arbitrado de `206` casos, `142` aciertos) y `07-resultados.tex` ya informa su
resultado: el requisito y ese escenario quedaron falsos y no pueden conservarse con su nombre.

**Migration**: lo reemplaza el requisito «Tabla de la validación fuera de muestra y arbitraje
ejecutado» de este mismo delta, que conserva la tabla de la etapa previa (peor caso, macro-F1,
acuerdo `E3`/`E4`) y exige declarar el arbitraje como ejecutado, con la cifra primaria del corpus
arbitrado y sus lecturas complementarias.

## MODIFIED Requirements

### Requirement: Validación fuera de muestra en las conclusiones

`09-conclusiones.tex` SHALL incorporar la validación fuera de muestra en la prosa y en la fila
del segundo objetivo de `tab:cumplimiento-objetivos`, con la cifra primaria del corpus arbitrado y
sus lecturas complementarias. La estimación con exclusión sobre `103` casos SHALL figurar en esa
fila rotulada como etapa previa, y la prosa SHALL remitir a ella sin repetir la cifra, según la
regla de «Repetición de cifras acotada y remisión a la tabla fuera de muestra». MUST NOT
presentarla como acreditación del umbral de `0,85` ni cambiar el estado del segundo objetivo.

#### Scenario: Resultado con su límite

- **WHEN** se leen las conclusiones sobre el segundo objetivo
- **THEN** figura la exactitud fuera de muestra del corpus arbitrado con sus lecturas complementarias
- **AND** la estimación sobre `103` casos figura solo en la fila del segundo objetivo, rotulada como etapa previa
- **AND** el objetivo sigue como no alcanzado

## ADDED Requirements

### Requirement: Tabla de la validación fuera de muestra y arbitraje ejecutado

`07-resultados.tex` SHALL presentar una tabla de la validación fuera de muestra con el n
primario, los casos discordantes excluidos, el n efectivo, el acuerdo y el kappa entre los
etiquetadores `E3` y `E4`, la exactitud estricta y laxa con su IC de Wilson, la exactitud
ponderada, la macro-F1, la *balanced accuracy*, el kappa del clasificador contra la
referencia y los escenarios de peor caso, mejor caso y cota de la exclusión, rotulados como
etapa previa. La tabla SHALL incluir además el bloque del corpus arbitrado, con la exactitud
estricta cruda como cifra primaria y las lecturas complementarias ponderada y sobre los casos del
diseño original. Los valores SHALL tomarse del memo canónico. El texto SHALL declarar que el
arbitraje de los casos discordantes por un tercer etiquetador se ejecutó, SHALL informar su
resultado y MUST NOT presentar el arbitraje como pendiente ni el n efectivo de la etapa previa
como cobertura del corpus.

#### Scenario: Tabla presente con el peor caso

- **WHEN** se lee la subsección de la validación fuera de muestra en `07-resultados.tex`
- **THEN** figura la tabla de la validación fuera de muestra con el peor caso, la macro-F1 y el acuerdo `E3`/`E4` rotulados como etapa previa
- **AND** cada valor coincide con el memo canónico

#### Scenario: Arbitraje declarado como ejecutado

- **WHEN** se lee el tratamiento de los casos discordantes en `07-resultados.tex`
- **THEN** el texto dice que el arbitraje se ejecutó e informa la cifra primaria del corpus arbitrado y sus lecturas complementarias
- **AND** no se describe el arbitraje como diferido
