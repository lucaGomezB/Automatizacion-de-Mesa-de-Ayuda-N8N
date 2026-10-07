# Delta for classification-resilience

## MODIFIED Requirements

### Requirement: Decision de cortocircuito calibrada por precision y cobertura

La decision de cortocircuitar la etapa semantica SHALL gobernarse por un SCORE DE CORRECTITUD emitido por la etapa determinista, y MUST NOT depender de la `confianza` ad-hoc ni de un valor degenerado que en la practica equivalga a "un solo sector matcheo". El score SHALL ordenar la correctitud esperada de la prediccion determinista a partir de features observables (score ganador, runner-up, margen, cantidad de matches, longitud del texto y senales por sector), y SHALL ser la senal de seleccion del cortocircuito. El sistema SHALL fijar un PUNTO DE OPERACION explicito definido por un PISO COMPARATIVO: la precision estimada del subconjunto cortocircuitado SHALL ser mayor o igual a la precision estimada de la etapa semantica (Gemini) sobre ese mismo subconjunto, ambas estimadas out-of-fold; el sistema SHALL seleccionar el punto de operacion maximizando la cobertura sujeto a ese piso comparativo. Cuando el piso comparativo se cumple en todo el conjunto cortocircuitable, el punto de operacion equivale a cortocircuitar todo el conjunto con senal no ambigua. El punto de operacion resultante SHALL ser explicito, documentado y verificable, y SHALL poder ajustarse sin recompilar. La calibracion MUST NOT invocar al proveedor pago y MUST NOT derivarse del corpus de evaluacion usado como test set reportado (ver el requisito de procedencia anti-fuga en `evaluation-framework`).

#### Scenario: El cortocircuito respeta el piso de precision

- **WHEN** se evalua sobre el conjunto de test reportado el subconjunto de casos cortocircuitados con el punto de operacion elegido
- **THEN** la precision del subconjunto es mayor o igual a la precision estimada de la etapa semantica sobre ese mismo subconjunto (piso comparativo)

#### Scenario: La cobertura queda justificada

- **WHEN** se elige el punto de operacion
- **THEN** existe una curva precision/cobertura documentada que justifica el tradeoff y el punto de operacion se deriva de ella

#### Scenario: La calibracion es offline

- **WHEN** se corre la calibracion del score
- **THEN** no se realiza ninguna llamada a Gemini (puede reutilizar predicciones cacheadas de una corrida previa) y el calculo depende solo del clasificador determinista y de datos de calibracion no usados como test reportado

## ADDED Requirements

### Requirement: Seleccion por score de correctitud

El clasificador hibrido SHALL cortocircuitar la etapa semantica si y solo si el resultado determinista no senala ausencia de prediccion, no esta marcado como ambiguo, y su score de correctitud alcanza el punto de operacion vigente. El cortocircuito MUST NOT usar la `confianza` determinista como criterio de seleccion ni un gate de cantidad minima de matches como sustituto del score. Los disparadores de escalamiento `sin_prediccion` y `ambiguo` SHALL mantenerse vigentes con independencia del score. El evento de cortocircuito SHALL registrar el score y el punto de operacion usados.

#### Scenario: El cortocircuito exige el score de correctitud

- **WHEN** el resultado determinista tiene senal dominante y su score de correctitud alcanza el punto de operacion
- **THEN** el pipeline cortocircuita la etapa semantica y retorna el resultado determinista

#### Scenario: El score insuficiente escala

- **WHEN** el resultado determinista tiene senal dominante pero su score de correctitud queda por debajo del punto de operacion
- **THEN** el pipeline escala a la etapa semantica

#### Scenario: Los disparadores de escalamiento no dependen del score

- **WHEN** el resultado determinista senala ausencia de prediccion o ambiguedad
- **THEN** el pipeline escala a la etapa semantica aunque el score fuera alto
