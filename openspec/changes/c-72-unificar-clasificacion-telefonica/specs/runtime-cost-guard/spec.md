# Delta for runtime-cost-guard

## MODIFIED Requirements

### Requirement: Enforcement del AI Agent de n8n antes de invocarlo

La clasificacion de un incidente telefonico MUST NOT reservar la superficie `n8n_gemini`, porque el canal se clasifica con la cascada del backend (determinista primero) y la invocacion paga, cuando ocurre, es la del backend. Cuando la cascada del backend escala a la etapa semantica para un incidente telefonico, la reserva SHALL corresponder a la superficie `backend_gemini` conforme al enforcement vigente. Si el workflow conserva una invocacion reducida a un modelo de n8n para un sub-caso (OQ1), esa invocacion MUST quedar sujeta a la guarda mediante un endpoint del backend y acotada de forma explicita; la mera clasificacion de telefonia MUST NOT reservar `n8n_gemini`.

#### Scenario: La guarda permite y el AI Agent se invoca

- **WHEN** el workflow conserva una invocacion reducida al `AI Agent`, consulta la guarda y la guarda permite
- **THEN** el `AI Agent` se invoca normalmente, sin que esa invocacion determine el sector persistido

#### Scenario: La guarda deniega y el AI Agent no se invoca

- **WHEN** el workflow conserva una invocacion reducida al `AI Agent`, consulta la guarda y la guarda deniega
- **THEN** el `AI Agent` NO se invoca y el incidente se resuelve con la cascada del backend

#### Scenario: La clasificacion telefonica no reserva n8n_gemini

- **WHEN** un incidente telefonico se clasifica con la cascada del backend
- **THEN** no se reserva presupuesto de la superficie `n8n_gemini` por clasificar telefonia

#### Scenario: La escalacion telefonica reserva la superficie del backend

- **WHEN** la cascada del backend escala a la etapa semantica para un incidente telefonico y la guarda permite
- **THEN** la reserva corresponde a la superficie `backend_gemini`
