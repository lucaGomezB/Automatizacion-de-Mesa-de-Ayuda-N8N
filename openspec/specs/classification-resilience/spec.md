# classification-resilience Specification

## Purpose
Define el contrato de resiliencia de la clasificacion semantica con Gemini ante fallas transitorias del proveedor: que fallas se reintentan y cuales no, como se acotan los reintentos (backoff, jitter, latencia total y costo), que ocurre al agotarlos y como se observa el proceso, de modo que una indisponibilidad transitoria no degrade indebidamente la clasificacion a revision humana.

## Requirements

### Requirement: Reintento acotado ante fallas transitorias del proveedor

La clasificacion con Gemini SHALL reintentar una falla transitoria del proveedor hasta un maximo de intentos configurable, con espera exponencial creciente entre intentos y una componente de jitter. El numero de intentos y la latencia total de la operacion MUST quedar acotados por configuracion. Al agotarse el presupuesto de intentos o de latencia, el sistema SHALL dejar de reintentar y SHALL aplicar el fallback definido en el requisito de fallback tras agotar los reintentos. La clasificacion MUST NOT abandonar el bucle de reintentos antes de agotar el maximo de intentos configurado, salvo que se agote el presupuesto de latencia total.

#### Scenario: Una falla transitoria seguida de exito no degrada la clasificacion

- **WHEN** el primer intento de clasificacion falla con una condicion transitoria del proveedor y un intento posterior tiene exito
- **THEN** el sistema conserva la clasificacion valida del intento exitoso, con su sector y confianza, y NO cae al fallback

#### Scenario: Una falla transitoria persistente agota los intentos configurados

- **WHEN** todos los intentos de clasificacion fallan con una condicion transitoria del proveedor
- **THEN** el sistema realiza exactamente el maximo de intentos configurado y luego aplica el fallback, sin exceder el maximo

#### Scenario: La espera entre intentos crece y esta acotada

- **WHEN** el sistema agenda reintentos sucesivos
- **THEN** la espera entre intentos crece exponencialmente respecto de la espera base y MUST NOT superar la espera maxima configurada, incorporando jitter

#### Scenario: El presupuesto de latencia total acota la operacion

- **WHEN** el tiempo consumido por los intentos y las esperas alcanza el presupuesto de latencia total configurado
- **THEN** el sistema deja de agendar reintentos y aplica el fallback, aunque no haya agotado el maximo de intentos

### Requirement: Taxonomia de errores transitorios y terminales

El sistema SHALL distinguir las fallas transitorias de las terminales. SHALL considerar transitorias, y por lo tanto elegibles para reintento, a las respuestas de indisponibilidad del proveedor (estado 503), a los limites de tasa transitorios (estado 429), a los demas errores de servidor (5xx) y a los timeouts de la llamada. SHALL considerar terminales, y por lo tanto NO elegibles para reintento, a los errores de peticion invalida (400), de autenticacion o autorizacion (401/403) y a las respuestas del proveedor que no superan la validacion del contrato JSON. Una falla terminal MUST NOT consumir reintentos ni esperas.

#### Scenario: Un error de peticion invalida no se reintenta

- **WHEN** el proveedor responde con un error terminal (peticion invalida o de autenticacion)
- **THEN** el sistema realiza un unico intento, NO agenda reintentos y trata la falla segun la semantica vigente para errores no recuperables

#### Scenario: Un error de servidor se reintenta

- **WHEN** el proveedor responde con un error de servidor (5xx) o un limite de tasa (429)
- **THEN** el sistema lo trata como transitorio y agenda un reintento acotado

#### Scenario: Un timeout se reintenta

- **WHEN** la llamada al proveedor excede el tiempo de espera por intento
- **THEN** el sistema lo trata como transitorio y agenda un reintento acotado

#### Scenario: Una respuesta invalida no se reintenta

- **WHEN** el proveedor responde con contenido que no supera la validacion del contrato JSON del clasificador
- **THEN** el sistema NO agenda reintentos y aplica el fallback de respuesta invalida vigente

### Requirement: Parametros de resiliencia configurables

El numero maximo de intentos, la espera base, la espera maxima, la proporcion de jitter y el presupuesto de latencia total SHALL ser configurables sin modificar el codigo, con valores por defecto seguros y override por entorno. El sistema MUST conservar un unico limite de tiempo por intento, independiente del presupuesto de latencia total. Los valores por defecto MUST acotar el peor caso de intentos a un numero pequeno y positivo.

#### Scenario: La configuracion por entorno cambia el maximo de intentos

- **WHEN** se define el maximo de intentos por variable de entorno
- **THEN** el clasificador respeta ese valor en lugar del default, sin recompilar

#### Scenario: El timeout por intento se mantiene acotado

- **WHEN** el clasificador invoca al proveedor en cualquier intento
- **THEN** cada intento queda acotado por el limite de tiempo por intento vigente, ademas del presupuesto total

#### Scenario: Los defaults son seguros

- **WHEN** no se configura ningun parametro de resiliencia
- **THEN** el clasificador aplica un maximo de intentos pequeno y positivo, un presupuesto de latencia total mayor que el limite por intento y una espera base no nula

### Requirement: Fallback tras agotar los reintentos

Agotados los intentos sin exito, el sistema SHALL aplicar el fallback vigente: un resultado con `etapa=fallback`, `confianza=0.0` y `requiere_revision_humana=true`, preservando la mejor estimacion disponible de la etapa deterministica. Cuando la etapa deterministica no produjo ninguna estimacion (ausencia de prediccion), el fallback MUST preservar esa ausencia y MUST NOT fabricar un sector canonico. El fallback MUST NOT propagar la excepcion del proveedor al llamador del clasificador hibrido.

#### Scenario: Agotar los reintentos produce el fallback con revision humana

- **WHEN** se agotan los intentos configurados sin una clasificacion valida
- **THEN** el resultado tiene `etapa=fallback`, `confianza=0.0` y `requiere_revision_humana=true`

#### Scenario: El fallback conserva la mejor estimacion deterministica

- **WHEN** el clasificador deterministico produjo una estimacion con confianza insuficiente antes de escalar a Gemini
- **THEN** el fallback conserva el sector del deterministico como mejor estimacion disponible

#### Scenario: El fallback no fabrica un sector sin estimacion

- **WHEN** se agotan los reintentos y la etapa deterministica no produjo ninguna prediccion
- **THEN** el fallback no inventa un sector canonico, conserva la ausencia de estimacion y marca revision humana

#### Scenario: El fallback no propaga la excepcion

- **WHEN** se agotan los reintentos por una falla de indisponibilidad o timeout
- **THEN** el clasificador hibrido devuelve el resultado de fallback y NO propaga la excepcion del proveedor

### Requirement: Observabilidad de los reintentos

El sistema SHALL emitir eventos estructurados por cada reintento agendado, por el agotamiento de los intentos y por las fallas terminales que no se reintentan. Cada evento SHALL identificar el numero de intento, el motivo (condicion transitoria) y, cuando corresponda, la cantidad de intentos consumidos. El evento MUST NOT incluir la clave de API ni el contenido crudo de la descripcion del incidente.

#### Scenario: Un reintento agendado queda registrado

- **WHEN** el sistema agenda un reintento por una falla transitoria
- **THEN** emite un evento estructurado con el numero de intento y el motivo transitorio

#### Scenario: El agotamiento queda registrado

- **WHEN** se agotan los intentos sin exito
- **THEN** emite un evento estructurado con la cantidad de intentos consumidos y el ultimo motivo

#### Scenario: La falla terminal no se reintenta y queda registrada

- **WHEN** ocurre una falla terminal
- **THEN** emite un evento estructurado que indica que no se reintenta

#### Scenario: La observabilidad no expone secretos ni PII

- **WHEN** se emite cualquier evento de reintento o agotamiento
- **THEN** el evento NO contiene la clave de API ni el texto crudo de la descripcion del incidente

### Requirement: Resiliencia del canal telefonico ante fallas transitorias del modelo

En el canal telefonico, una falla transitoria del modelo de lenguaje de n8n SHALL ser reintentada de forma acotada, de modo que NO aborte la clasificacion del incidente telefonico ni fuerce su derivacion a revision humana por una indisponibilidad momentanea. El reintento de transporte MUST NOT reemplazar el tope de refinamiento por respuestas invalidas: los refinamientos y los reintentos de transporte son mecanismos distintos y su producto MUST quedar acotado.

#### Scenario: Una falla transitoria del modelo no aborta la clasificacion telefonica

- **WHEN** el modelo de lenguaje del agente falla de forma transitoria durante la clasificacion de una llamada
- **THEN** el workflow reintenta la invocacion de forma acotada y, si un intento tiene exito, continua la clasificacion normal del incidente

#### Scenario: El tope total de invocaciones pagas queda acotado

- **WHEN** se inspecciona el workflow exportado del canal telefonico
- **THEN** la cantidad maxima de invocaciones pagas por incidente queda acotada por el producto entre los intentos de transporte y los intentos de refinamiento, ambos explicitos

#### Scenario: Agotado el reintento de transporte se conserva un camino terminal

- **WHEN** todos los intentos de transporte fallan de forma persistente
- **THEN** el flujo conserva un camino terminal que persiste el incidente con `requiere_revision_humana=true` y `confianza=0.0`, sin reejecutar indefinidamente la invocacion paga

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

### Requirement: Escalamiento ante ausencia de prediccion o ambiguedad

El clasificador hibrido SHALL escalar a la etapa semantica cuando el resultado determinista senale ausencia de prediccion o ambiguedad, con independencia del umbral de cortocircuito. Una ausencia de prediccion o un empate MUST NOT cortocircuitar el pipeline ni derivar directamente a revision humana como unica via, salvo la politica resuelta por el autor para el no-match. El escalamiento SHALL quedar observable con la causa (sin senal o ambiguo).

#### Scenario: La ausencia de prediccion escala

- **WHEN** el resultado determinista senala ausencia de prediccion
- **THEN** el pipeline escala a la etapa semantica y no cortocircuita

#### Scenario: La ambiguedad escala

- **WHEN** el resultado determinista se marca como ambiguo por empate
- **THEN** el pipeline escala a la etapa semantica y no cortocircuita

#### Scenario: El escalamiento es observable

- **WHEN** el pipeline escala por ausencia de prediccion o ambiguedad
- **THEN** emite un evento estructurado con la causa del escalamiento, sin incluir el contenido crudo de la descripcion
