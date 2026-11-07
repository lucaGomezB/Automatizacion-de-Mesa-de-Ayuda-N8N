## ADDED Requirements

### Requirement: Respeto de la tasa del API y robustez ante 429 en el harvest de telefonia

El script de recuperacion de telefonia (`scripts/corpus_ingest/ingest_telefonia_corpus.py`) SHALL ofrecer un flag `--sleep` (segundos, float) que imponga una pausa entre requests HTTP CONSECUTIVOS a `/api/v1/telefonia/`, tanto en el loop de recuperacion como en el loop de `--replace` destructivo. El default SHALL ser un valor SEGURO que mantenga el ritmo sostenido por debajo del limite de nginx (`webhook_limit = 60r/m`, `nginx/nginx.conf:17`, aplicado a `/api/v1/telefonia/` con `burst=20 nodelay`, `nginx/nginx.conf:128`), de modo que correr el harvest como lo documenta el runbook MUST NOT producir 429 por rafaga. El flag SHALL usar el MISMO nombre y semantica (segundos, float) que sus pares de los harnesses hermanos. La pausa MUST aplicarse despues del primer request y entre cada par de requests consecutivos; el PRIMER request de una corrida SHALL NOT esperar.

Ante un 429, el script SHALL reintentar el request con backoff hasta un numero acotado de intentos, HONRANDO el header `Retry-After` cuando este presente; agotados los intentos, SHALL registrar el caso como una etiqueta de error y MUST NOT escribir ni inferir `t_e2e_s`, `t_espera_s` ni `t_pipeline_s` (no se fabrica una medicion). El reintento de 429 SHALL ser una extension OPT-IN que MUST NOT alterar el comportamiento por defecto de los demas consumidores del helper de reintento compartido, que siguen reintentando solo 5xx y timeouts de red y NO reintentan 4xx. La robustez ante 429 MUST NOT tocar la metrica canonica (`derive_telefonia_metric`), el write-back ni el formato del sidecar.

El runbook de campana y el README del harness SHALL documentar el throttle `--sleep` de telefonia y la robustez ante 429, de modo que la corrida sea reproducible SIN un wrapper ad-hoc externo al repositorio.

#### Scenario: Throttle aplicado entre requests consecutivos de recuperacion

- **WHEN** se procesan dos o mas casos de telefonia con `--sleep S` con `S > 0`
- **THEN** se registra una pausa de `S` segundos entre cada par de requests HTTP consecutivos de recuperacion y no se espera antes del primer request

#### Scenario: Throttle aplicado en el loop de --replace

- **WHEN** se ejecuta `--replace` sobre varios casos
- **THEN** el borrado acotado de cada caso tambien respeta la pausa entre requests consecutivos

#### Scenario: Default seguro por debajo del limite de nginx

- **WHEN** un operador corre el harvest con el default de `--sleep` sobre los ~81 casos del plan
- **THEN** el ritmo sostenido de requests queda por debajo de 60 r/m y la corrida no produce 429 por rafaga

#### Scenario: 429 reintentado y luego exitoso

- **WHEN** un caso recibe un 429 y un intento posterior devuelve 200
- **THEN** el script reintenta con backoff (honrando `Retry-After` si esta presente) y registra la medicion de la respuesta 200

#### Scenario: 429 agotado no fabrica medicion

- **WHEN** un caso recibe 429 en todos los intentos acotados
- **THEN** el caso queda registrado con una etiqueta de error y no se escribe ni se infiere ningun valor de `t_e2e_s`, `t_espera_s` ni `t_pipeline_s`

#### Scenario: Sin opt-in el helper no reintenta 429

- **WHEN** otro consumidor del helper de reintento compartido hace un request sin habilitar el reintento de 4xx
- **THEN** un 429 se devuelve de inmediato, preservando el comportamiento previo (solo 5xx y timeouts se reintentan)

#### Scenario: Documentacion sin wrapper ad-hoc

- **WHEN** un operador consulta el runbook de campana y el README del harness
- **THEN** encuentra documentado el `--sleep` de telefonia y la robustez ante 429, sin depender de un wrapper externo al repositorio
