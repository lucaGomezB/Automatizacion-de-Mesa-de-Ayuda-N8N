## MODIFIED Requirements

### Requirement: Conclusiones y resumen acotados a la evidencia

`09-conclusiones.tex` MUST NOT afirmar que el marco permite operar sin barreras legales ni
riesgos de cumplimiento; SHALL condicionar la operación con datos reales a la suscripción del
instrumento de transferencia internacional, en concordancia con `11-aspectos-legales.tex`.
Sobre el filtro determinístico, SHALL informar el ahorro de llamadas y de costo medido frente al
brazo de modelo solo (aproximadamente un tercio) solo junto con el veredicto «no concluyente» de
la hipótesis de eficiencia, y MUST NOT afirmar que ese ahorro se obtuvo sin costo de exactitud ni
que el híbrido no es inferior en exactitud. SHALL acotar la generalización a la organización
estudiada y MUST NOT afirmar independencia de servicios o licencias de terceros que el sistema
usa. `00-resumen.tex` (resumen y *abstract*) MUST NOT afirmar la viabilidad económica sin la
condición del balance neto, y SHALL respetar el límite de 250 palabras. La lectura del balance
neto SHALL ser la misma en el resumen, la discusión y las conclusiones.

#### Scenario: Sin contradicción con el capítulo legal

- **WHEN** se compara la tercera contribución de `09-conclusiones.tex` con la transferencia internacional de `11-aspectos-legales.tex`
- **THEN** las conclusiones condicionan la operación a la suscripción del instrumento
- **AND** no aparece la frase sobre la ausencia de barreras legales

#### Scenario: Sin afirmación de costo ni de viabilidad económica incondicional

- **WHEN** se leen `09-conclusiones.tex` y `00-resumen.tex`
- **THEN** el ahorro de llamadas y de costo, si se informa, aparece con el veredicto «no concluyente» de la hipótesis de eficiencia
- **AND** no figura una afirmación de no inferioridad de la exactitud
- **AND** la viabilidad económica aparece condicionada al balance neto en resumen y *abstract*

#### Scenario: Lectura única del balance neto

- **WHEN** se compara la calificación del balance neto en `00-resumen.tex`, `08-discusion.tex` y `09-conclusiones.tex`
- **THEN** los tres usan la misma lectura