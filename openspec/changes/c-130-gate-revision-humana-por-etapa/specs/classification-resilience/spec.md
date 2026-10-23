## MODIFIED Requirements

### Requirement: Clasificacion telefonica determinista-primero

El canal telefonico SHALL beneficiarse del mismo pipeline que los canales correo y web: la etapa determinista se ejecuta primero sobre la descripcion pseudonimizada y, si su senal es dominante y su score de correctitud alcanza el punto de operacion vigente, SHALL cortocircuitar la etapa semantica paga. Si el score de correctitud queda por debajo del punto de operacion o el determinista senala ausencia de prediccion o ambiguedad, el pipeline SHALL escalar a la etapa semantica conforme al comportamiento vigente. La `confianza` determinista MUST NOT usarse como criterio de cortocircuito en este canal, igual que en correo y web. Cuando la cascada escala para un incidente telefonico, la operacion paga SHALL quedar sujeta a la guarda de costo vigente del backend. El comportamiento SHALL ser identico al de correo y web.

#### Scenario: El cortocircuito determinista evita la llamada paga en telefonia

- **WHEN** la etapa determinista tiene senal dominante y su score de correctitud alcanza el punto de operacion sobre la descripcion pseudonimizada de un incidente telefonico
- **THEN** el pipeline omite la etapa semantica paga y persiste el resultado determinista

#### Scenario: La escalacion de telefonia queda sujeta a la guarda

- **WHEN** el score de correctitud de la etapa determinista queda por debajo del punto de operacion, o el determinista senala ausencia de prediccion o ambiguedad, para un incidente telefonico y el pipeline escala
- **THEN** la operacion paga se reserva contra la superficie del backend conforme a la guarda vigente

#### Scenario: El pipeline telefonico es el mismo que correo y web

- **WHEN** se comparan los pasos de clasificacion de los tres canales
- **THEN** los tres usan la etapa determinista primero, la etapa semantica como escalamiento y el fallback con revision humana
