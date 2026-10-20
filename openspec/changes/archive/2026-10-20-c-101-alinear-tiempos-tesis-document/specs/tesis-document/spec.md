## MODIFIED Requirements

### Requirement: Divulgacion del procedimiento de medicion de tiempos y analisis de sensibilidad

La tesis SHALL declarar que `tiempo_manual_s` es una medicion real en vivo,
registrada durante la atencion de usuarios con redondeo hacia arriba (sesgo
sistematico de medicion), y SHALL reportar el tiempo manual como cota superior
junto con una cota inferior conservadora de sensibilidad. El claim primario de
reduccion SHALL apoyarse en la mediana y en estadisticos de rango, no solo en la
media. La prueba de Wilcoxon SHALL reportar el valor real con correccion por
empates (W=363, T+=19737, T−=363, p=3,08e-32, r=0,9639) y SHALL declarar el
numero real de pares en que el flujo automatizado no fue mas rapido (12 de 200),
sin afirmar "W=0" ni "sin excepcion".

#### Scenario: Redondeo declarado y sensibilidad reportada

- **WHEN** se leen el Capitulo 4 (metodologia) y el Capitulo 7 (resultados)
- **THEN** se declara el redondeo al alza de la medicion manual
- **AND** se reporta la reduccion como cota superior (71,2 %) junto a sus cotas inferiores conservadoras (68,6 % al descontar 5 s y 65,6 % al descontar 10 s a cada medicion manual)

#### Scenario: Estadistico de Wilcoxon real

- **WHEN** se lee la comparacion de tiempos de registro
- **THEN** el estadistico reportado es W=363 con T+=19737, T−=363, p=3,08e-32 y r=0,9639
- **AND** el texto no afirma W=0 ni "sin una sola excepcion"

#### Scenario: Pares invertidos declarados

- **WHEN** se leen los resultados de tiempos
- **THEN** se declara que en 12 de 200 pares el flujo automatizado no fue mas rapido que el manual

### Requirement: Rigor inferencial del tamaño del efecto

El capítulo de marco metodológico y el de resultados SHALL declarar
explícitamente la convención del estadístico de Wilcoxon empleado, reportar
ambos estadísticos de rango (`T+` y `T−`) y calcular el tamaño del efecto con la
fórmula rank-biserial correcta. El documento MUST NOT presentar `W=0` ni un
tamaño del efecto igual a `1,00` como resultado del corpus real, y MUST declarar
el rango verdadero de la fórmula empleada.

#### Scenario: Convención de W declarada

- **WHEN** se lee la sección de análisis estadístico o de resultados que reporta la prueba de Wilcoxon
- **THEN** el texto enuncia si `W` denota `min(T+, T−)`, `T+` u otro estadístico
- **AND** reporta los valores de `T+` y `T−` además del estadístico de contraste

#### Scenario: Fórmula y rango correctos

- **WHEN** se lee la fórmula del tamaño del efecto
- **THEN** la fórmula es `r = (T+ − T−) / (n(n+1)/2)` (o su equivalente `1 − 4W/(n(n+1))` cuando `W=T−`)
- **AND** el rango declarado es coherente con la fórmula (no `[-1,+1]` como rango universal de `1 − 2W/(n(n+1))`)
- **AND** el valor reportado sobre el corpus real es `0,9639`, no `1,00`

#### Scenario: Sin W=0

- **WHEN** se busca `W = 0` en los archivos de sección
- **THEN** no aparece como resultado de la prueba sobre el corpus real
- **AND** el conteo de pares invertidos (12/200) es consistente con el estadístico reportado
