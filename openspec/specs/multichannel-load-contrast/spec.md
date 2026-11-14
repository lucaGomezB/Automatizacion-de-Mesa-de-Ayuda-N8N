# multichannel-load-contrast Specification

## Purpose
Medir, de forma reproducible y de costo cero, la capacidad del tramo compartido donde convergen los tres canales de entrada (backend FastAPI y su entrada vía N8N) bajo carga concurrente creciente, para contrastar la dimensión medible de la hipótesis subsidiaria de integración multicanal: que integrar los canales no introduce cuellos de botella adicionales. El arnés reporta latencia (p50/p95), throughput y tasa de error por nivel de concurrencia, y emite un veredicto de tres vías bajo un criterio fijado antes de observar datos.

## Requirements

### Requirement: MLC-001 — Entorno desechable de costo cero

El arnés SHALL ejecutarse sobre el perfil `corpus` aislado del stack (base `mesa_de_ayuda_corpus` y su backend y N8N dedicados), NUNCA sobre la base operativa `mesa_de_ayuda`. SHALL inyectar mediante un override de compose una `GEMINI_API_KEY` ficticia y `COST_GUARD_BUDGET_USD=0`, y SHALL afirmar dentro del contenedor del backend que ambas capas están en efecto antes de enviar cualquier solicitud, abortando con código distinto de cero si detecta una clave real o un presupuesto distinto de cero. El arnés MUST NOT invocar a Gemini ni a Twilio, y MUST NOT modificar `docker-compose.yml`, `n8n/workflow.json` ni código de producto bajo `App/**`.

#### Scenario: Clave ficticia y presupuesto nulo afirmados antes de cargar

- **WHEN** el arnés inicia su corrida
- **THEN** verifica que la `GEMINI_API_KEY` efectiva del backend es la ficticia y que el presupuesto de la guarda es cero
- **AND** aborta con código distinto de cero sin enviar solicitudes si cualquiera de las dos afirmaciones falla

#### Scenario: Escalada denegada no genera costo

- **WHEN** una descripción del fixture no se resuelve en la etapa determinística y el clasificador intenta escalar
- **THEN** la guarda de costo deniega la llamada paga, el backend degrada con revisión humana y no se emite ninguna petición al proveedor de Gemini

#### Scenario: Base operativa intacta

- **WHEN** el arnés completa su corrida
- **THEN** la base `mesa_de_ayuda` de la aplicación no recibió ninguna escritura
- **AND** ningún artefacto versionado del stack quedó modificado

### Requirement: MLC-002 — Punto de convergencia y entradas de carga

El arnés SHALL cargar el tramo compartido donde convergen los canales, con dos capas: (a) el punto de convergencia del backend `POST /api/v1/incidentes/` con autenticación `Bearer`, y (b) el webhook del canal web de N8N `POST /webhook/incidente-web`, que ejercita N8N -> backend. Cada solicitud SHALL portar un `origen_message_id` único por corrida para no ser deduplicada por idempotencia. Los canales de correo (sondado IMAP, no apto para concurrencia) y telefonía (pago) SHALL quedar explícitamente excluidos de la inyección concurrente y su exclusión SHALL quedar declarada en el reporte.

#### Scenario: Las dos capas se ejercitan

- **WHEN** el arnés ejecuta un nivel de concurrencia
- **THEN** dispara solicitudes concurrentes contra el punto de convergencia del backend y contra el webhook web de N8N
- **AND** ambas capas reportan métricas por separado

#### Scenario: Sin deduplicación por idempotencia

- **WHEN** el arnés envía solicitudes en un nivel de concurrencia
- **THEN** cada solicitud lleva un `origen_message_id` distinto
- **AND** el conteo de respuestas 2xx coincide con el conteo de solicitudes enviadas

#### Scenario: Exclusión declarada

- **WHEN** se lee el reporte de la corrida
- **THEN** declara que los canales de correo y telefonía quedaron fuera de la inyección concurrente y por qué

### Requirement: MLC-003 — Fixture determinística sin escalada

El arnés SHALL usar un fixture versionado de descripciones elegidas para resolverse en la etapa determinística del clasificador, de modo que ninguna solicitud escale al proveedor pago. Al finalizar cada nivel, el arnés SHALL verificar que ninguna solicitud escaló (etapa de clasificación determinística y sin `fallback`) y SHALL fallar de forma ruidosa si alguna lo hizo.

#### Scenario: Fixture resuelto por reglas

- **WHEN** el arnés procesa las descripciones del fixture
- **THEN** cada incidente se clasifica en la etapa determinística sin invocar al modelo pago
- **AND** el arnés lo verifica contra el registro de clasificación del incidente

#### Scenario: Escalada detectada como fallo

- **WHEN** una solicitud del fixture escala a la etapa semántica o cae en `fallback`
- **THEN** el arnés termina con código distinto de cero e informa la descripción y la etapa observada

### Requirement: MLC-004 — Niveles de concurrencia y métricas

El arnés SHALL ejecutar niveles de concurrencia crecientes (por defecto 1, 5, 10 y 20 solicitudes concurrentes, configurables), con una cantidad de solicitudes fija por nivel y al menos una repetición por nivel. SHALL registrar la latencia por solicitud medida por el cliente (reloj de pared de envío a respuesta) y la latencia end-to-end del servidor (`latencia_e2e_ms`), y SHALL calcular por nivel: p50, p95, p99 y media de latencia, throughput (solicitudes por segundo) y tasa de error (respuestas no 2xx más timeouts). El arnés MUST NOT descartar silenciosamente solicitudes fallidas del cómputo de la tasa de error.

#### Scenario: Métricas por nivel

- **WHEN** el arnés completa un nivel de concurrencia
- **THEN** el reporte incluye p50, p95, p99, media, throughput y tasa de error para ese nivel
- **AND** distingue la latencia de cliente de la `latencia_e2e_ms` del servidor

#### Scenario: Solicitud fallida contabilizada

- **WHEN** una solicitud responde con un estado no 2xx o vence su timeout
- **THEN** se cuenta en la tasa de error del nivel y no se excluye del denominador

### Requirement: MLC-005 — Criterio de decisión prerregistrado

El arnés SHALL aplicar un criterio de tres vías fijado antes de observar datos, con un techo absoluto de p95 y una tolerancia de throughput como constantes prerregistradas. El veredicto SHALL ser «sostenida» si en todos los niveles la tasa de error es cero, el p95 no supera el techo y el throughput no decrece más allá de la tolerancia; «no sostenida» si algún nivel viola cualquiera de las tres condiciones; y «no concluyente» si la corrida queda incompleta o el entorno es inestable. Las constantes MUST NOT reajustarse después de ver los resultados.

#### Scenario: Sin cuello de botella

- **WHEN** en todos los niveles la tasa de error es cero, el p95 no supera el techo y el throughput no decrece más allá de la tolerancia
- **THEN** el veredicto es «sostenida»

#### Scenario: Cuello de botella detectado

- **WHEN** algún nivel presenta tasa de error mayor que cero, p95 por encima del techo o caída de throughput más allá de la tolerancia
- **THEN** el veredicto es «no sostenida» y el reporte nombra el nivel y la condición violada

#### Scenario: Corrida inestable

- **WHEN** la corrida queda incompleta o el entorno reporta fallos ajenos a la carga
- **THEN** el veredicto es «no concluyente» y el reporte declara el motivo

### Requirement: MLC-006 — Reporte de evidencia versionado

El arnés SHALL escribir, bajo una opción explícita, un reporte JSON y su resumen Markdown con: el commit verificado, la fecha y hora en UTC, la versión de N8N del stack, el perfil de entorno, el hash del fixture, las constantes del criterio, las métricas por nivel y el veredicto. Las salidas SHALL ser deterministas (LF, UTF-8 sin BOM) y MUST NOT contener contraseñas, tokens, claves ni material criptográfico.

#### Scenario: Reporte con trazabilidad

- **WHEN** el arnés se ejecuta con la opción de reporte
- **THEN** el archivo JSON incluye commit, fecha UTC, versión de N8N, hash del fixture, constantes del criterio, métricas por nivel y veredicto

#### Scenario: Reporte sin secretos

- **WHEN** se inspecciona el reporte generado
- **THEN** no contiene la contraseña del operador, el token de acceso, claves de API ni material criptográfico

#### Scenario: Salidas deterministas

- **WHEN** el arnés genera el reporte dos veces sobre las mismas métricas
- **THEN** las salidas JSON y Markdown son idénticas byte a byte

### Requirement: MLC-007 — Reproducibilidad y no destructividad

El arnés SHALL exponer un comando documentado y una meta del `Makefile` para ejecutarlo. SHALL operar sobre el proyecto de Compose con nombre fijo y MUST NOT pasar el flag `-p`, y SHALL reutilizar el stack ya en ejecución cuando exista o levantarlo cuando no exista.

#### Scenario: Ejecución documentada

- **WHEN** un operador consulta la documentación del arnés
- **THEN** encuentra el comando y la meta para ejecutarlo, y la descripción del entorno desechable

#### Scenario: Proyecto de Compose fijado

- **WHEN** el arnés invoca `docker compose`
- **THEN** no incluye `-p` y opera sobre el proyecto de nombre fijo
