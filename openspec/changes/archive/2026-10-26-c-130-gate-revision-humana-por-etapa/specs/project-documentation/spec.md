## ADDED Requirements

### Requirement: DOC-004 — Descripcion del gate de revision y del cortocircuito sincronizada con el comportamiento

La configuracion para agentes (`openspec/config.yaml`, `CLAUDE.md`), la base de conocimiento (`knowledge-base/`) y los comentarios de los clasificadores (`App/Backend/app/classifiers/hybrid.py`, `deterministic.py` y `gemini_classifier.py`) SHALL describir el gate de revision humana y el cortocircuito conforme a `Settings` y al codigo: el cortocircuito deterministico se decide por `score_correctitud >= deterministic_score_threshold` con senal dominante; `human_review_threshold` (0.70) se aplica solo a la salida de Gemini; la etapa fallback marca revision siempre con confianza 0.0; la etapa deterministica no marca revision por su confianza; y el backend tambien deriva a revision ante un reportante no identificado. Ninguno de esos artefactos MUST declarar un umbral de cortocircuito de 0.90 sobre la confianza ni un umbral de 0.70 aplicable a toda clasificacion. Los cambios en los clasificadores MUST limitarse a comentarios y docstrings, sin alterar el comportamiento. El contrato SHALL quedar fijado por un test que verifique que el cortocircuito deterministico no marca revision aunque la confianza sea inferior a 0.70.

#### Scenario: Umbrales declarados en la configuracion del proyecto

- **WHEN** se lee `conventions.thresholds` en `openspec/config.yaml`
- **THEN** declara el punto de operacion del score de correctitud (0.5166) y el umbral de revision (0.70) con su alcance
- **AND** no declara un umbral deterministico de 0.90

#### Scenario: Instrucciones para agentes alineadas

- **WHEN** se leen las lineas de `CLAUDE.md` que describen el umbral de confianza y los nodos IF del flujo
- **THEN** describen el alcance del gate por etapa y el cortocircuito por score de correctitud
- **AND** distinguen el IF de validacion de entrada previo al POST del IF que evalua el indicador del backend

#### Scenario: Base de conocimiento sin reglas retiradas

- **WHEN** se busca en `knowledge-base/` un umbral de 0,90 como criterio de cortocircuito o un umbral de 0,70 aplicado a toda clasificacion
- **THEN** no aparece como regla, decision ni flujo vigente

#### Scenario: Docstrings coherentes y sin cambio de comportamiento

- **WHEN** se leen los docstrings y comentarios de los tres clasificadores
- **THEN** no afirman un umbral de cortocircuito de 0.90 ni que la revision humana se evalue para cualquier etapa
- **AND** el arbol sintactico de cada archivo, sin docstrings, es identico al previo al change

#### Scenario: Contrato fijado por test de caracterizacion

- **WHEN** se ejecuta el test con un resultado deterministico cuyo score alcanza el punto de operacion y cuya confianza vale 0.0, 1/6 o 0.5
- **THEN** el resultado tiene `etapa == "deterministic"` y `requiere_revision_humana is False`
- **AND** la etapa Gemini no se invoca
