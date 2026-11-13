# confidence-gate-calibration Specification

## Purpose
TBD - created by archiving change c-214-calibracion-y-punto-de-operacion-del-gate-de-confianza. Update Purpose after archive.

## Requirements

### Requirement: CAL-001 — Métricas de calibración y discriminación por etapa

El análisis SHALL informar, por etapa de la cascada y por corpus (los 200 casos y el bloque fuera
de muestra), la tabla de fiabilidad por valor observado de la señal, el ECE con 10 bandas de
igual ancho, el puntaje de Brier, la sobreconfianza media y el AUROC de la señal para separar
aciertos de errores, cada uno con IC95 bootstrap de semilla fija. Las métricas SHALL
implementarse como funciones puras probadas y MUST NOT llamar a la red ni al modelo.

#### Scenario: Señal perfectamente ordenada

- **WHEN** todos los aciertos tienen una confianza mayor que todos los errores
- **THEN** el AUROC es `1.0`

#### Scenario: Señal constante

- **WHEN** todos los casos tienen la misma confianza
- **THEN** el AUROC es `0.5` y la tabla de fiabilidad tiene una sola fila

#### Scenario: ECE de una señal calibrada

- **WHEN** en cada banda la exactitud coincide con la confianza media
- **THEN** el ECE es `0.0`

### Requirement: CAL-002 — Barrido de umbral y riesgo-cobertura

Para la etapa Gemini, el análisis SHALL evaluar cada umbral candidato fijado en el diseño,
incluido el vigente `0,70` y la opción de derivar todo lo escalado, e informar la cobertura, la
exactitud selectiva de los aceptados con IC de Wilson, los errores atrapados entre los derivados
y la carga de revisión a nivel del sistema.

#### Scenario: Umbral vigente sin derivaciones

- **WHEN** ninguna confianza escalada es menor que `0,70`
- **THEN** el barrido informa cobertura `1.0` y cero casos derivados para ese umbral

#### Scenario: Derivar todo

- **WHEN** se evalúa la opción de derivar todo lo escalado
- **THEN** la cobertura es `0.0` y la carga de revisión es la proporción de casos escalados del corpus

### Requirement: CAL-003 — Selección dentro de la muestra y evaluación fuera de ella

El umbral y cualquier política de derivación SHALL elegirse con la regla prerregistrada sobre
los 200 casos (piso `φ = 0,85`, mínimo de 10 aceptados) y SHALL evaluarse sin reajuste sobre el
bloque fuera de muestra, con resultado `confirmado`, `no confirmado` o `no estimable`. Si
ninguna opción cumple el piso dentro de la muestra, el resultado SHALL ser que la señal no
sostiene un umbral con ese piso. El análisis MUST NOT elegir umbrales con los datos del bloque
fuera de muestra.

#### Scenario: Ningún umbral cumple el piso

- **WHEN** ningún umbral candidato alcanza `φ` con al menos 10 aceptados en los 200 casos
- **THEN** el resultado es «la señal no sostiene un umbral con el piso fijado»
- **AND** fuera de la muestra el barrido se informa solo como descripción

#### Scenario: Umbral confirmado fuera de la muestra

- **WHEN** el umbral elegido en los 200 da fuera de la muestra una exactitud selectiva `≥ φ` con al menos 10 aceptados y la exactitud de los derivados es menor que la de los aceptados
- **THEN** el resultado es `confirmado`

#### Scenario: Pocos aceptados fuera de la muestra

- **WHEN** el umbral elegido deja menos de 10 casos aceptados fuera de la muestra
- **THEN** el resultado es `no estimable`

### Requirement: CAL-004 — Señales alternativas recomputadas sin costo

El análisis SHALL evaluar, con la misma regla de CAL-003, el acuerdo entre el sector de las
reglas y el de Gemini en los casos escalados y el `score_correctitud` de las reglas. Ambas
señales SHALL recomputarse offline con el clasificador determinístico, persistirse en un archivo
versionado y verificarse contra las cachés: el recómputo MUST reproducir exactamente la etapa y
el sector de los casos cortocircuitados.

#### Scenario: Recómputo fiel

- **WHEN** se recomputan las señales de las reglas sobre los 200 casos
- **THEN** la etapa y el sector de cada caso cortocircuitado coinciden con la caché versionada
- **AND** el análisis se detiene si hay alguna diferencia

#### Scenario: Reglas sin predicción

- **WHEN** las reglas no tienen sector ganador en un caso escalado
- **THEN** el caso se clasifica como «sin predicción de las reglas» para la señal de acuerdo

### Requirement: CAL-005 — Sin cambio de configuración productiva

El change MUST NOT modificar `openspec/config.yaml`, `App/Backend/app/config/settings.py`, el
prompt ni el código del clasificador. Si una política queda `confirmada`, el análisis SHALL
registrarla como recomendación con su evidencia y su límite, para un change posterior de
gobernanza HIGH.

#### Scenario: Política confirmada

- **WHEN** una política queda `confirmada` fuera de la muestra
- **THEN** el memo canónico y la sección de recomendaciones la registran como recomendación
- **AND** la configuración productiva no cambia

### Requirement: CAL-006 — Artefactos y registro canónico

Las salidas del análisis y el archivo de señales recomputadas SHALL versionarse con LF y UTF-8
sin BOM y con su SHA-256 registrado. Cada cifra que llegue a la tesis SHALL registrarse en una
sección nueva del memo canónico con archivo fuente y comando, junto con la declaración de que el
prerregistro no fue ciego.

#### Scenario: Reproducibilidad del análisis

- **WHEN** el script de análisis se ejecuta dos veces sobre los mismos artefactos
- **THEN** las salidas tienen el mismo SHA-256
