## MODIFIED Requirements

### Requirement: Conclusiones y resumen acotados a la evidencia

`09-conclusiones.tex` MUST NOT afirmar que el marco permite operar sin barreras legales ni
riesgos de cumplimiento; SHALL condicionar la operación con datos reales a la suscripción del
instrumento de transferencia internacional, en concordancia con `11-aspectos-legales.tex`.
Sobre el filtro determinístico, la proporción de casos que invocan al modelo frente al brazo de
modelo solo (cerca de un tercio) SHALL informarse solo como dato descriptivo del bloque dentro de
la muestra, junto con la declaración de que la hipótesis de eficiencia quedó sin contraste limpio
tras el retiro de la validación fuera de muestra, y MUST NOT afirmar que ese ahorro se obtuvo sin
costo de exactitud ni que el híbrido no es inferior en exactitud. SHALL acotar la generalización
a la organización estudiada y MUST NOT afirmar independencia de servicios o licencias de terceros
que el sistema usa. `00-resumen.tex` (resumen y *abstract*) MUST NOT afirmar la viabilidad
económica sin la condición del balance neto, y SHALL respetar el límite de 250 palabras. La
lectura del balance neto SHALL ser la misma en el resumen, la discusión y las conclusiones.

#### Scenario: Sin contradicción con el capítulo legal

- **WHEN** se compara la tercera contribución de `09-conclusiones.tex` con la transferencia internacional de `11-aspectos-legales.tex`
- **THEN** las conclusiones condicionan la operación a la suscripción del instrumento
- **AND** no aparece la frase sobre la ausencia de barreras legales

#### Scenario: Sin afirmación de costo ni de viabilidad económica incondicional

- **WHEN** se leen `09-conclusiones.tex` y `00-resumen.tex`
- **THEN** la proporción de llamadas, si se informa, aparece como dato descriptivo junto con la declaración de que la hipótesis de eficiencia quedó sin contraste limpio
- **AND** no figura una afirmación de no inferioridad de la exactitud
- **AND** la viabilidad económica aparece condicionada al balance neto en resumen y *abstract*

#### Scenario: Lectura única del balance neto

- **WHEN** se compara la calificación del balance neto en `00-resumen.tex`, `08-discusion.tex` y `09-conclusiones.tex`
- **THEN** los tres usan la misma lectura

## REMOVED Requirements

### Requirement: Validación fuera de muestra en las conclusiones
**Reason**: La validacion fuera de muestra se retira del ejemplar (K-01, opcion 2 de la devolucion de tercera instancia del 16-11-2026).
**Migration**: La fila del segundo objetivo de `tab:cumplimiento-objetivos` y la prosa de `09-conclusiones.tex` usan solo la evidencia dentro de la muestra; ver "Retiro de la validacion fuera de muestra del ejemplar" en `tesis-document`.

### Requirement: Consentimiento de E3 y E4 según el registro
**Reason**: Con el retiro, la tesis deja de tratar a `E3`, `E4` y `E5`; el parrafo de §7.5 se elimina (K-01, K-02).
**Migration**: La exactitud de `docs/campana-medicion/confirmacion-posterior-consentimiento.md` y de las filas de `registro_sujetos.csv` se revisa con la compuerta de autores P8 de c-235 y se rotula segun OOS-026 (`evaluation-out-of-sample-validation`); ver "Declaracion de procedencia del retiro en la nota de versiones" en `tesis-document`.

### Requirement: Tabla de la validación fuera de muestra y arbitraje ejecutado
**Reason**: `tab:fuera-de-muestra` y el arbitraje de `E5` se retiran del ejemplar (K-01).
**Migration**: Ver "Retiro de la validacion fuera de muestra del ejemplar" en `tesis-document`; los valores quedan en el memo con estado `retirado`.
