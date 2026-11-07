## MODIFIED Requirements

### Requirement: FRH-010 — El aviso de criterio no referencia un modelo retirado

El aviso explicativo de la pestaña "Revisión Humana" SHALL describir TODAS las causas reales de
derivación a revisión humana: (1) la confianza del clasificador inferior al umbral de revisión
humana (70%), (2) la clasificación resuelta en la etapa de respaldo (fallback), y (3) el reportante
no identificado. El aviso MUST NOT afirmar que la cola contiene únicamente incidentes con confianza
inferior al 70%, y MUST NOT afirmar que el umbral fue definido por un modelo retirado. El texto
SHALL conservar la indicación de revisar y confirmar el sector correcto para cada incidente. El
texto SHALL ser agnóstico al modelo de lenguaje concreto, de modo que un cambio de modelo no lo deje
obsoleto. El texto SHALL redactarse en español técnico neutro, sin emojis.

#### Scenario: El aviso no menciona un modelo retirado

- **WHEN** el operador abre la pestaña "Revisión Humana"
- **THEN** el aviso muestra las causas de derivación sin mencionar "Gemini 2.5 Flash" ni ningún otro modelo de lenguaje por nombre

#### Scenario: El aviso comunica el umbral vigente

- **WHEN** el operador lee el aviso
- **THEN** el aviso indica que una de las causas de derivación es la confianza inferior al 70%, sin afirmar que sea la única causa

#### Scenario: El aviso menciona la etapa de respaldo

- **WHEN** el operador lee el aviso
- **THEN** el aviso indica que una clasificación resuelta en la etapa de respaldo también deriva a revisión humana

#### Scenario: El aviso menciona el reportante no identificado

- **WHEN** el operador lee el aviso
- **THEN** el aviso indica que un incidente cuyo reportante no fue identificado también deriva a revisión humana, con independencia de la confianza

#### Scenario: El aviso no reduce la cola a un solo criterio

- **WHEN** el operador lee el aviso
- **THEN** el aviso describe las tres causas de derivación y no presenta la confianza inferior al umbral como el único motivo de la cola
