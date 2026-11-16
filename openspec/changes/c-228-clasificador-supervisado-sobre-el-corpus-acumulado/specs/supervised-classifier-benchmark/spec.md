## Purpose

Define la particion sin fuga, el entrenamiento de un clasificador supervisado tipo
BERT y el benchmark de modelos abiertos ejecutados localmente contra el
clasificador hibrido, con el conjunto de prueba retenido fuera del entrenamiento y
metricas por clase comparables.

## ADDED Requirements

### Requirement: SCB-001 — Particion disjunta sin fuga con el conjunto retenido admisible

El arnes SHALL construir una particion `train`/`dev`/`test` disjunta sobre el
corpus curado, agrupando por texto casi duplicado (un mismo incidente MUST NOT caer
en dos particiones) y estratificando por sector y por canal. El conjunto de prueba
retenido SHALL ser el corpus probabilistico acreditado de `c-229` con la referencia
por mayoria de `c-230`; mientras no exista, SHALL ser una particion `test` de
`clasificacion_log` rotulada como «particion retenida interna, no validacion
externa». El conjunto retenido MUST NOT participar del entrenamiento, del ajuste de
hiperparametros ni de la seleccion del modelo. El corpus de 200 casos MUST NOT
usarse como conjunto de prueba del clasificador supervisado. `dev` SHALL usarse
solo para parada temprana y seleccion, y `test` SHALL evaluarse una unica vez. La
particion SHALL derivarse de una funcion pura con prueba sintetica previa.

#### Scenario: Particiones disjuntas

- **WHEN** se construye la particion
- **THEN** la interseccion de textos entre `train`, `dev` y `test` es vacia
- **AND** ningun identificador del conjunto retenido aparece en `train` ni en `dev`

#### Scenario: Rotulo del conjunto retenido

- **WHEN** el corpus probabilistico acreditado no existe y el retenido sale de `clasificacion_log`
- **THEN** cada artefacto lo rotula como particion retenida interna, no validacion externa

#### Scenario: Sin fuga del conjunto de prueba

- **WHEN** se inspecciona el entrenamiento
- **THEN** ninguna descripcion, etiqueta ni metrica del conjunto retenido participa del ajuste
- **AND** el artefacto reporta el `n` de entrenamiento y el `n` de prueba por separado

### Requirement: SCB-002 — Entrenamiento tipo BERT y benchmark de modelos abiertos con lugar de ejecucion declarado

El arnes SHALL entrenar un modelo de clasificacion de secuencia de la familia BERT
(encoder de espanol o multilingue) sobre `train`, con `dev` para parada temprana, y
SHALL evaluar modelos abiertos (`Llama 3`, `Mistral`, `Qwen`) como alternativa,
comparando cada resultado contra el hibrido como base. Cada modelo SHALL declarar
donde corre; por defecto todos SHALL ejecutarse localmente con pesos fijados por
hash y sin red durante la inferencia. Ningun texto MUST enviarse a la Gemini API ni
a otro tercero sin la compuerta etica y legal cerrada y el envio declarado. Las
predicciones del hibrido SHALL tomarse de las ya registradas en `clasificacion_log`
con su version; si exigen una corrida nueva, esta SHALL quedar bloqueada hasta esa
compuerta. El arnes SHALL ser reproducible (semilla fija) y MUST NOT modificar el
clasificador de produccion ni el prompt vigente. Si el corpus no alcanza el volumen
declarado o alguna compuerta esta abierta, el arnes SHALL registrar el bloqueo en
lugar de emitir un modelo.

#### Scenario: Entrenamiento reproducible y local

- **WHEN** se ejecuta el arnes con la misma semilla y el mismo corpus
- **THEN** la particion y las metricas son identicas entre corridas
- **AND** la inferencia se realiza localmente sin enviar texto a terceros

#### Scenario: Modelos abiertos comparados con el hibrido

- **WHEN** se ejecuta el benchmark
- **THEN** cada modelo abierto se evalua sobre las mismas particiones con su lugar de ejecucion declarado
- **AND** el resultado se compara contra el hibrido con la version de sus predicciones registrada

#### Scenario: Volumen insuficiente o compuerta abierta

- **WHEN** el corpus no alcanza el volumen declarado o una compuerta esta abierta
- **THEN** el arnes registra el bloqueo
- **AND** no emite un modelo como si estuviera entrenado

### Requirement: SCB-003 — Metricas por clase y lectura rotulada

El arnes SHALL reportar exactitud estricta y laxa, macro-F1 y precision,
sensibilidad y F1 por clase con su soporte, reutilizando `evaluation/metrics.py`.
Cada lectura SHALL rotular su conjunto (corpus probabilistico acreditado o
particion retenida interna). Toda lectura sobre el corpus de 200 casos SHALL
presentarse solo como contraste descriptivo dentro de la muestra y SHALL declarar
que el hibrido se ajusto, en parte, con ese corpus, por lo que MUST NOT presentarse
como evaluacion del clasificador supervisado ni como comparacion valida con el
hibrido. El artefacto MUST NOT usar como ancla, insumo o comparador ninguna cifra ni
artefacto retirado por `c-235`.

#### Scenario: Metricas por clase comparables

- **WHEN** se reporta el resultado del modelo supervisado
- **THEN** figuran exactitud estricta y laxa, macro-F1 y P/R/F1 por clase con soporte
- **AND** cada lectura rotula su conjunto

#### Scenario: Corpus de 200 no evalua el supervisado

- **WHEN** se lee un contraste sobre el corpus de 200 casos
- **THEN** se rotula como descriptivo dentro de la muestra y se declara que el hibrido se ajusto con ese corpus
- **AND** no se presenta como evaluacion del clasificador supervisado
