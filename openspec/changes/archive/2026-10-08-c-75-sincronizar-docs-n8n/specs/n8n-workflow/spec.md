# Delta for n8n-workflow

## ADDED Requirements

### Requirement: N8N-DOC-004 — Documentación del workflow alineada con el JSON exportado

La documentación que describe la estructura del workflow N8N (`docs/n8n-workflow-guide.md` y los documentos que referencian su grafo, como `docs/por_implementar.md` y `docs/runbook-verificacion-telefonia-c52.md`) SHALL reflejar el JSON exportado vigente (`n8n/workflow.json`): 29 nodos (26 operativos + 3 sticky notes) y el flujo telefónico `Llamada telefonica -> Sellar ingreso telefonia -> Normalizar entrada del incidente -> Entrada valida -> Login operador -> HTTP POST a MESA-AYUDAS -> Requiere revision humana`. La documentación MUST NOT presentar como vigentes los nodos retirados por c-72: `AI Agent`, `Google Gemini Chat Model`, `memoryRedisChat`, `Se verifica lo que trajo la IA`, `La clasificacion de la IA es valida`, `Tope de refinamiento alcanzado`, `Guard de costo`, `Restaurar item telefonia`, `Guard permite?` y `Derivar a revision humana`. La línea de estado de la guía SHALL conservar el formato `Estado: <N> nodos (<M> operativos + <S> sticky notes)` con los valores `29`, `26` y `3`, y su línea de cobertura SHALL conservar `Verifica 163 propiedades estructurales`. La guía MUST NOT contener `queda sin marcar` ni `no** pasa por \`Marcar correo como leido\`` ni `TwiML` ni `<Say>`, y SHALL conservar `notificacion-clasificacion`, `N8N_WEBHOOK_URL` e `incidente-web`.

#### Scenario: La guía conserva el conteo de nodos y de propiedades estructurales

- **WHEN** se ejecuta `pytest tests/test_n8n_workflow.py` sobre la guía corregida
- **THEN** `test_c40_guide_node_count_matches_workflow` y `test_c40_guide_test_count_matches_suite` pasan, porque la línea de estado sigue siendo `29 nodos (26 operativos + 3 sticky notes)` y la cobertura sigue diciendo `Verifica 163 propiedades estructurales`

#### Scenario: La tabla del canal telefonía refleja el flujo vigente

- **WHEN** se lee la tabla del canal telefonía de `docs/n8n-workflow-guide.md`
- **THEN** los nodos listados corresponden al flujo vigente `Llamada telefonica -> Sellar ingreso telefonia -> Normalizar entrada del incidente` y no aparecen como vigentes los nodos `AI Agent`, `Guard de costo`, `Restaurar item telefonia`, `Guard permite?`, `Se verifica lo que trajo la IA`, `La clasificacion de la IA es valida`, `Tope de refinamiento alcanzado` ni `Derivar a revision humana`

#### Scenario: Los documentos que describen el grafo no presentan nodos retirados

- **WHEN** se inspeccionan `docs/n8n-workflow-guide.md`, `docs/por_implementar.md` y `docs/runbook-verificacion-telefonia-c52.md`
- **THEN** ninguno describe como vigentes los nodos retirados por c-72, y el runbook describe el flujo telefónico vigente `Sellar -> Normalizar` en lugar de `Guard de costo -> AI Agent`

#### Scenario: La excepción obsoleta de la rama de revisión no reaparece

- **WHEN** se ejecuta `test_c40_guide_has_no_stale_review_branch_exception`
- **THEN** la guía no contiene `queda sin marcar` ni `no** pasa por \`Marcar correo como leido\``

#### Scenario: La guía no reintroduce una confirmación telefónica por TwiML

- **WHEN** se ejecuta `test_c53_guia_no_afirma_confirmacion_telefonica_por_twiml`
- **THEN** la guía no contiene `TwiML` ni `<Say>`

#### Scenario: Se conservan los tokens del webhook dedicado de clasificación

- **WHEN** se ejecuta `test_c33_cost_guard_wiring.py`
- **THEN** `docs/n8n-workflow-guide.md` sigue conteniendo `notificacion-clasificacion`, `N8N_WEBHOOK_URL` e `incidente-web`

### Requirement: N8N-DOC-005 — Transporte de correo, credenciales y entorno alineados con el workflow vigente

La documentación que describe el transporte de correo y las credenciales del workflow (`docs/n8n-workflow-guide.md`, `docs/por_implementar.md`, `docs/dry-run-harness.md`, `docs/troubleshooting.md` y `docs/medicion-latencia-e2e.md`) SHALL reflejar el transporte vigente tras c-55: disparador `n8n-nodes-base.emailReadImap` con `postProcessAction=read` y marca `\SEEN`, envío saliente `n8n-nodes-base.emailSend` sobre SMTP, y credenciales `imap` (`imap.gmail.com:993`) y `smtp` (`smtp.gmail.com:465`). Esa documentación MUST NOT presentar como vigentes `microsoftOutlookTrigger`, `microsoftOutlook`, credenciales `microsoftOutlook*`, un nodo `twilioTrigger`, un nodo de memoria Redis (`memoryRedisChat`) ni variables `TWILIO_*` o `REDIS_URL` usadas por el workflow. La referencia a la imagen de N8N SHALL ser la fijada por el compose (`n8nio/n8n:2.11.2`) y MUST NOT ser `n8nio/n8n:latest`. La documentación SHALL presentar el origen de `BACKEND_URL` sin el sufijo `/api/v1` (por ejemplo `http://backend:8000`) y SHALL documentar las variables que el workflow usa: `BACKEND_URL`, `OPERATOR_EMAIL` y `SMTP_FROM_EMAIL`.

#### Scenario: El transporte documentado es IMAP/SMTP

- **WHEN** se leen las secciones de correo de los documentos en alcance
- **THEN** describen el disparador `emailReadImap` y el envío `emailSend` por SMTP con las credenciales `imap` y `smtp`, y no dependen de un proveedor propietario

#### Scenario: No reaparecen Outlook, Twilio ni Redis de workflow

- **WHEN** se buscan tokens prohibidos en los documentos en alcance
- **THEN** no aparecen `microsoftOutlookTrigger`, `microsoftOutlook`, `microsoftOutlook*`, un nodo `twilioTrigger`, `memoryRedisChat` ni `REDIS_URL` como componentes vigentes del workflow

#### Scenario: La versión de N8N documentada es la fijada por el compose

- **WHEN** se inspecciona la referencia a la imagen de N8N en la documentación
- **THEN** cita `n8nio/n8n:2.11.2` y no `n8nio/n8n:latest`

#### Scenario: El ejemplo de BACKEND_URL no incluye el prefijo de versión

- **WHEN** se inspecciona el ejemplo de `BACKEND_URL` en la documentación
- **THEN** el origen no incluye `/api/v1` y las variables documentadas son `BACKEND_URL`, `OPERATOR_EMAIL` y `SMTP_FROM_EMAIL`

### Requirement: N8N-DOC-006 — La documentación operativa y los diagramas no describen componentes retirados

La guía operativa (`docs/operational-guide.md`) y los diagramas (`docs/diagrams/despliegue.md`, `docs/diagrams/secuencia.md`) SHALL describir la topología y el transporte vigentes. La guía operativa MUST NOT presentar un `AI Agent` de n8n ni el nodo `Guard de costo` como componentes vigentes, y sus constantes de costo SHALL coincidir con el código: `COST_GUARD_UNIT_COST_TWILIO_TRANSCRIPTION_USD=0.0075` y la presencia de `COST_GUARD_UNIT_COST_BACKEND_STT_USD`. Los diagramas MUST NOT representar un flujo de Outlook ni un canal `Twilio -> N8N` como vigentes, ni una arista de memoria Redis del `AI Agent`, y SHALL citar la versión de imagen de N8N que usa el compose. El runbook `docs/runbook-verificacion-telefonia-c52.md` MUST NOT afirmar que variables del handoff no están definidas en el repositorio. La corrección MUST NOT introducir `Gestion_Incidentes`, `generate_corpus.py` ni `seed fijo`, y SHALL conservar las invariantes de bootstrap que leen `test_docs_bootstrap_sync.py`, `test_docs_restructure_sync.py` y `test_docs_evaluation_sync.py`.

#### Scenario: La guía operativa no describe el agente retirado ni la guarda de costo de n8n

- **WHEN** se lee la sección sobre N8N de `docs/operational-guide.md`
- **THEN** no presenta un `AI Agent` de n8n ni el nodo `Guard de costo` como componentes vigentes

#### Scenario: Las constantes de costo documentadas coinciden con el código

- **WHEN** se inspeccionan las constantes de costo en `docs/operational-guide.md`
- **THEN** `COST_GUARD_UNIT_COST_TWILIO_TRANSCRIPTION_USD` vale `0.0075` y aparece `COST_GUARD_UNIT_COST_BACKEND_STT_USD`

#### Scenario: Los diagramas reflejan la topología vigente

- **WHEN** se inspeccionan `docs/diagrams/despliegue.md` y `docs/diagrams/secuencia.md`
- **THEN** no representan Outlook ni `Twilio -> N8N` como vigentes ni una arista de memoria Redis del `AI Agent`, y citan la versión de imagen de N8N del compose

#### Scenario: El runbook no afirma variables inexistentes

- **WHEN** se lee `docs/runbook-verificacion-telefonia-c52.md`
- **THEN** no afirma que `BACKEND_PUBLIC_BASE_URL`, `N8N_TELEFONIA_WEBHOOK_URL` ni `N8N_WEBHOOK_SECRET` no están definidas en el repositorio

#### Scenario: Se preservan las invariantes de bootstrap de la guía operativa y el README

- **WHEN** se ejecutan `test_docs_bootstrap_sync.py`, `test_docs_restructure_sync.py` y `test_docs_evaluation_sync.py`
- **THEN** los tres pasan, conservando `scripts/up.sh`/`make up`, `UP_SKIP_COST_PREFLIGHT`, `docker compose up -d`, `openssl/generate-certs.sh`, `JWT_SECRET_KEY`, `App/Backend/` y el comando de evaluación de la sección 8, sin introducir `Gestion_Incidentes`, `generate_corpus.py` ni `seed fijo`
