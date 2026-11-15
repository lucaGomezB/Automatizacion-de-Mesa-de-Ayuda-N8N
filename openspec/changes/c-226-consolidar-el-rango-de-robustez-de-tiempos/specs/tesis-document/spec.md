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
sin afirmar "W=0" ni "sin excepcion". La tesis SHALL presentar, en una sola tabla o
parrafo, la sintesis del rango de robustez de los tiempos con los escenarios ya
calculados: descuentos de `5 s` y `10 s`, desagregado por canal, tiempos por
operador, efecto de posicion y cota inferior del instrumento. La sintesis SHALL
declarar el rango completo del estimando primario (reduccion de la media global de
la campana 2026-10) y el escenario que lo minimiza, y SHALL informar las lecturas
por canal y por operador como cotas de alcance rotuladas, sin presentarlas como el
minimo global. La sintesis SHALL rotularse como sensibilidad o reinterpretacion y
MUST NOT presentarse como medicion nueva. La cifra primaria `71,2 %` y su intervalo
`[67,2 %; 74,6 %]` SHALL conservarse sin cambios. La discusion SHALL remitir desde
las seis explicaciones rivales a la sintesis, y la limitacion correspondiente y la
amenaza 1 de la metodologia SHALL precisar que el rango acota la magnitud pero no
estima el efecto de orden ni elimina la asimetria de instrumentos.

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

#### Scenario: Rango de robustez consolidado

- **WHEN** se lee la sintesis de tiempos en resultados
- **THEN** una sola tabla o parrafo reune los descuentos de 5 s y 10 s, el desagregado por canal, los tiempos por operador, el efecto de posicion y la cota inferior del instrumento
- **AND** declara el rango del estimando primario y el escenario que lo minimiza
- **AND** la sintesis esta rotulada como sensibilidad o reinterpretacion

#### Scenario: Cotas de alcance rotuladas

- **WHEN** se leen las lecturas por canal y por operador
- **THEN** se informan como cotas de alcance con su ambito, sin presentar el valor por operador mas adverso como minimo global
- **AND** la cifra primaria 71,2 % y su intervalo [67,2 %; 74,6 %] no cambian

#### Scenario: Remision desde la discusion y la limitacion

- **WHEN** se leen las seis explicaciones rivales y la limitacion de tiempos
- **THEN** remiten a la sintesis del rango de robustez
- **AND** precisan que el rango acota la magnitud pero no estima el efecto de orden ni elimina la asimetria de instrumentos