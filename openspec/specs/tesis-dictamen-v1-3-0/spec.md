# tesis-dictamen-v1-3-0 Specification

## Purpose
TBD - created by archiving change c-207-atender-el-dictamen-coneau-v1-3-0. Update Purpose after archive.

## Requirements

### Requirement: Tabla de la validación fuera de muestra y estado del arbitraje

`07-resultados.tex` SHALL presentar una tabla de la validación fuera de muestra con el n
primario, los casos discordantes excluidos, el n efectivo, el acuerdo y el kappa entre los
etiquetadores `E3` y `E4`, la exactitud estricta y laxa con su IC de Wilson, la exactitud
ponderada, la macro-F1, la *balanced accuracy*, el kappa del clasificador contra la
referencia y los escenarios de peor caso, mejor caso y cota de la exclusión. Los valores
SHALL tomarse del memo canónico. El texto SHALL declarar que el arbitraje de los casos
discordantes por un tercer etiquetador no se ejecutó en esta versión y que queda diferido, y
MUST NOT anticipar su resultado ni presentar el n efectivo como cobertura del corpus primario.

#### Scenario: Tabla presente con el peor caso

- **WHEN** se lee la subsección de resultados de la campaña en `07-resultados.tex`
- **THEN** figura la tabla de la validación fuera de muestra con el peor caso, la macro-F1 y el acuerdo `E3`/`E4`
- **AND** cada valor coincide con el memo canónico

#### Scenario: Arbitraje declarado como diferido

- **WHEN** se lee el tratamiento de los casos discordantes en `07-resultados.tex`
- **THEN** el texto dice que el arbitraje no se ejecutó y queda diferido
- **AND** no se informa ningún resultado del arbitraje

### Requirement: Conclusiones y resumen acotados a la evidencia

`09-conclusiones.tex` MUST NOT afirmar que el marco permite operar sin barreras legales ni
riesgos de cumplimiento; SHALL condicionar la operación con datos reales a la suscripción del
instrumento de transferencia internacional, en concordancia con `11-aspectos-legales.tex`.
MUST NOT afirmar que el filtro determinístico reduce el costo de inferencia mientras la
hipótesis de eficiencia no esté contrastada. SHALL acotar la generalización a la organización
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
- **THEN** no figura que el filtro reduzca el costo de inferencia
- **AND** la viabilidad económica aparece condicionada al balance neto en resumen y *abstract*

#### Scenario: Lectura única del balance neto

- **WHEN** se compara la calificación del balance neto en `00-resumen.tex`, `08-discusion.tex` y `09-conclusiones.tex`
- **THEN** los tres usan la misma lectura

### Requirement: Validación fuera de muestra en las conclusiones

`09-conclusiones.tex` SHALL incorporar la validación fuera de muestra en la prosa y en la fila
del segundo objetivo de `tab:cumplimiento-objetivos`, con el n efectivo, el peor caso y el
estado del arbitraje. MUST NOT presentarla como acreditación del umbral de `0,85` ni cambiar
el estado del segundo objetivo.

#### Scenario: Resultado con su límite

- **WHEN** se leen las conclusiones sobre el segundo objetivo
- **THEN** figura la exactitud fuera de muestra con el n efectivo y el peor caso
- **AND** el objetivo sigue como no alcanzado

### Requirement: Consentimiento de E3 y E4 según el registro

`11-aspectos-legales.tex` SHALL mencionar a los etiquetadores `E3` y `E4` del doble etiquetado
independiente y al árbitro `E5`, y SHALL afirmar solo lo que respalda
`docs/campana-medicion/confirmacion-posterior-consentimiento.md`: información verbal el
`2026-11-12` y confirmación escrita firmada el `2026-11-13`, con los originales en poder del
director y fuera del repositorio. El registro de sujetos (`evaluation/data/campana/registro_sujetos.csv`)
y el README de campaña SHALL ser consistentes con ese estado: el registro SHALL contener las
filas `E3`, `E4` y `E5` sin datos personales y el README SHALL informar el número vigente de
filas. El texto MUST NOT reintroducir la afirmación de confirmación pendiente ni fechas
distintas de las registradas. Este requisito verifica y cierra la recomendación R4 del dictamen
v1.3.0; MUST NOT reescribir el capítulo legal más allá de la consistencia verificada.

#### Scenario: Registro firmado y texto consistente

- **WHEN** el registro tiene `fecha_informacion_verbal = 2026-11-12` y `fecha_confirmacion = 2026-11-13` para `E3`, `E4` y `E5`
- **THEN** el capítulo legal menciona a los tres con esas fechas
- **AND** no aparece la afirmación de que la confirmación escrita está pendiente

#### Scenario: Registro de sujetos y README consistentes

- **WHEN** se cuentan las filas de `registro_sujetos.csv`
- **THEN** el README de campaña informa ese mismo número
- **AND** las filas `E3`, `E4` y `E5` no contienen nombre, correo ni legajo

#### Scenario: Sin fechas inventadas

- **WHEN** se comparan las fechas del capítulo legal con las del registro
- **THEN** coinciden
- **AND** el texto no afirma una fecha de firma que el registro no respalde

#### Scenario: Registro pendiente

- **WHEN** el registro no tiene `fecha_confirmacion` para `E3`, `E4` o `E5`
- **THEN** el capítulo legal no afirma un consentimiento escrito ni completa la fecha por su cuenta
- **AND** el registro no se modifica para hacer que la afirmación cierre

### Requirement: Balance neto con referencia declarada

`08-discusion.tex` SHALL declarar contra qué referencia se mide cada tasa de error del balance
neto. Si la verificación confirma que el error del sistema y el manual se miden contra
referencias distintas, SHALL informar el balance con ambas tasas contra una misma referencia,
calculado por código versionado y probado, o declarar la asimetría de forma expresa. Si la
verificación no la confirma, el texto MUST NOT cambiar y el hallazgo SHALL registrarse en
`dictamen-correcciones.md`. El signo del balance MUST NOT enunciarse si su intervalo no lo fija.

#### Scenario: Asimetría confirmada

- **WHEN** el script confirma referencias distintas para `e_aut` y `e_man`
- **THEN** la discusión informa el balance con una referencia común y su intervalo
- **AND** las diferencias de unidad o de campaña que no se igualan se declaran como límite

#### Scenario: Asimetría no confirmada

- **WHEN** el script no confirma la asimetría
- **THEN** `08-discusion.tex` no cambia y el resultado de la verificación queda registrado

### Requirement: Intervalo de confianza de la reducción del tiempo

`07-resultados.tex` SHALL informar el intervalo de confianza al 95 % de la reducción relativa
de la media del tiempo de registro, calculado por código versionado y probado, con su método,
semilla y número de remuestras, y rotulado como cota superior de una muestra por
conveniencia. El cuarto objetivo específico SHALL conservar la promesa de intervalos al 95 %.

#### Scenario: IC informado

- **WHEN** se lee la comparación de tiempos en `07-resultados.tex`
- **THEN** la reducción del `71,2 %` figura con su IC al 95 % y el método
- **AND** el valor coincide con el memo canónico

### Requirement: Compilación declarada como pendiente cuando no hay toolchain

Las tareas de recompilar `main.pdf` y actualizar `compilacion.md` SHALL quedar, si el entorno
de aplicación no tiene `latexmk`, `xelatex` o `biber`, marcadas como bloqueadas y a cargo de los
autores, y MUST NOT darse por hechas.

#### Scenario: Sin LaTeX

- **WHEN** el entorno no tiene el toolchain de LaTeX
- **THEN** la tarea de compilación queda abierta y señalada como bloqueada
