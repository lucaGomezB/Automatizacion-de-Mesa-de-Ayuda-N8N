# tesis-dictamen-v1-3-0 Specification

## Purpose
TBD - created by archiving change c-207-atender-el-dictamen-coneau-v1-3-0. Update Purpose after archive.

## Requirements

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
