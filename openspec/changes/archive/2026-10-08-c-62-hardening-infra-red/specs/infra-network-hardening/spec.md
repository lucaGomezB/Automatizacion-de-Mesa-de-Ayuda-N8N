# infra-network-hardening — Delta Spec

## Purpose

Define el endurecimiento de infraestructura y red del stack local: no exponer los servicios internos al host, autenticar Redis cuando exista, segmentar las redes Docker, restringir la UI de N8N, endurecer nginx y separar entornos de forma declarativa y reversible.

## ADDED Requirements

### Requirement: INFRA-001 — Servicios internos acotados a loopback

En la configuracion efectiva por defecto (`docker compose config`), los puertos de PostgreSQL y de administracion de N8N SHALL publicarse UNICAMENTE en la interfaz de loopback (`127.0.0.1`) y MUST NOT quedar publicados en `0.0.0.0` ni en otras interfaces del host. La comunicacion backend↔PostgreSQL y backend↔N8N MUST ocurrir por la red Docker interna.

#### Scenario: PostgreSQL y N8N publican solo en loopback

- **WHEN** se inspecciona la configuracion efectiva por defecto (`docker compose config`)
- **THEN** los puertos publicados de `postgres` y `n8n` tienen `host_ip: 127.0.0.1` y no `0.0.0.0`

#### Scenario: Backend alcanza N8N por la red interna

- **WHEN** el backend envia una peticion a `http://n8n:5678/webhook`
- **THEN** la peticion llega a N8N por la red Docker interna sin pasar por el host

### Requirement: INFRA-002 — Acceso de desarrollo por loopback

El subconjunto de integracion PostgreSQL SHALL alcanzar la base por `localhost` (loopback) sin exponer PostgreSQL a la red local (`0.0.0.0`). El canal por defecto MUST ser loopback; no se requiere publicar en todas las interfaces ni un archivo adicional para el flujo de tests documentado.

#### Scenario: Tests de integracion alcanzan PostgreSQL por loopback

- **WHEN** un desarrollador ejecuta el flujo documentado del subconjunto de integracion PostgreSQL contra `localhost:5433`
- **THEN** la suite alcanza la base y provisiona su base descartable

#### Scenario: PostgreSQL no queda expuesto a la LAN

- **WHEN** se inspecciona la configuracion por defecto
- **THEN** el puerto de PostgreSQL no esta publicado en `0.0.0.0`

### Requirement: INFRA-003 — Autenticacion de Redis

Si el servicio Redis permanece en el stack, SHALL requerir autenticacion (`requirepass` o equivalente) y TODOS sus consumidores MUST recibir la credencial por variable de entorno, de modo que ninguno quede sin autenticarse. Si ningun servicio consume Redis, el servicio MUST retirarse del stack o la documentacion MUST justificar explicitamente su conservacion.

#### Scenario: Redis con autenticacion y consumidores sincronizados

- **WHEN** se inspecciona el compose con Redis presente
- **THEN** Redis declara autenticacion
- **AND** cada consumidor (n8n y, si aplica, backend) recibe la credencial por variable de entorno

#### Scenario: Acceso sin credenciales es rechazado

- **WHEN** un cliente intenta un comando Redis sin credenciales
- **THEN** el comando falla con error de autenticacion

#### Scenario: Redis sin consumidores

- **WHEN** ningun servicio consume Redis
- **THEN** el retiro del servicio o su justificacion de conservacion queda documentada

### Requirement: INFRA-004 — Segmentacion de red Docker

El stack SHALL declarar al menos tres redes logicas diferenciadas: una de borde para el proxy y el frontend, una de datos para PostgreSQL y una de automatizacion para N8N. La red de datos MUST ser `internal: true`. PostgreSQL MUST NOT compartir ninguna red con N8N. nginx y el frontend MUST NOT estar en la red de datos. La red de automatizacion MUST conservar egreso a internet para que N8N alcance sus proveedores externos. Los servicios de datos que necesiten publicacion en loopback MAY unirse ademas a una red de soporte no-`internal` dedicada a ese fin, que MUST NOT incluir N8N, nginx ni el frontend.

#### Scenario: N8N y PostgreSQL no comparten red

- **WHEN** se inspecciona la agenda de red del stack
- **THEN** no existe ninguna red que contenga simultaneamente `n8n` y `postgres`

#### Scenario: La red de soporte de publicacion no incluye N8N ni el proxy

- **WHEN** se inspecciona la agenda de red del stack
- **THEN** la red de soporte usada para publicar PostgreSQL en loopback no contiene `n8n`, `nginx` ni `frontend`

#### Scenario: El arranque sigue sano con la segmentacion

- **WHEN** se arranca el stack con las redes segmentadas
- **THEN** los servicios alcanzan estado sano y las verificaciones de salud del arranque pasan

### Requirement: INFRA-005 — UI de N8N restringida

La UI de administracion de N8N SHALL NOT quedar accesible sin autenticacion en todas las interfaces del host. Debe alcanzarse unicamente desde loopback o a traves de nginx tras autenticacion.

#### Scenario: La UI no esta expuesta sin autenticacion

- **WHEN** se inspecciona la configuracion efectiva del servicio N8N
- **THEN** su UI no queda publicada en `0.0.0.0` sin autenticacion

#### Scenario: El canal habilitado exige autenticacion

- **WHEN** un cliente alcanza la UI de N8N por el canal habilitado
- **THEN** se le exige autenticacion antes de servir contenido de administracion

### Requirement: INFRA-006 — nginx endurecido

nginx SHALL ocultar su version en el header de respuesta, SHALL aplicar headers de seguridad adicionales (al menos `Referrer-Policy` y `Permissions-Policy`, y `Content-Security-Policy` cuando se acuerde), y SHALL limitar la tasa de peticiones sobre los endpoints publicos. nginx MUST conservar el comportamiento catch-all que rechaza Host/SNI desconocidos y la redireccion HTTP hacia HTTPS.

#### Scenario: La version de nginx no se expone

- **WHEN** nginx responde a una peticion
- **THEN** el header `Server` no contiene el numero de version de nginx

#### Scenario: Limite de tasa sobre endpoint publico

- **WHEN** un cliente supera el limite de tasa acordado sobre un endpoint publico
- **THEN** nginx responde con HTTP 429

#### Scenario: Host desconocido rechazado

- **WHEN** un Host o SNI desconocido alcanza nginx
- **THEN** la conexion se cierra con HTTP 444

### Requirement: INFRA-007 — Separacion de entornos reversible

El proyecto SHALL separar de forma declarativa y reversible los entornos de desarrollo y no-desarrollo mediante perfiles, archivos override o archivos por entorno. El modo por defecto MUST ser el endurecido; el acceso de desarrollo MUST ser opt-in y MUST NOT requerir editar archivos versionados a mano. No se exige un despliegue productivo real.

#### Scenario: El modo por defecto aplica la postura endurecida

- **WHEN** se arranca el stack sin opt-in de desarrollo
- **THEN** aplican las restricciones de red, puertos y acceso de este capability

#### Scenario: Acceso de desarrollo opt-in

- **WHEN** un desarrollador habilita el mecanismo de desarrollo
- **THEN** recupera los accesos locales necesarios sin editar archivos versionados

### Requirement: INFRA-008 — CI no se rompe

El preflight de costo que parsea `docker-compose.yml` SHALL seguir aprobando, preservando la imagen de n8n pineada, `N8N_WEBHOOK_URL` con la ruta dedicada y las variables `EXECUTIONS_TIMEOUT`. El subconjunto de integracion en CI MUST seguir usando su service container propio en `localhost:5432`.

#### Scenario: Preflight de costo pasa con el compose modificado

- **WHEN** CI ejecuta `python scripts/preflight/cost_readiness.py`
- **THEN** el comando termina con exit code cero

#### Scenario: CI no depende del compose

- **WHEN** CI ejecuta el subconjunto de integracion
- **THEN** usa `TEST_PG_URL` apuntando a `localhost:5432` y no el compose del repositorio

### Requirement: INFRA-009 — Comandos de desarrollo documentados preservados

Todo comando de desarrollo documentado que dependa de una publicacion de puerto removida SHALL seguir funcionando o SHALL tener un comando equivalente documentado en los mismos documentos. Incluye al menos los tests de integracion PostgreSQL, el acceso a la UI y a los webhooks de N8N, y el harness `scripts/dry_run`.

#### Scenario: Documentacion vigente sin accesos rotos

- **WHEN** se recorre la documentacion operativa vigente
- **THEN** no queda ningun comando que apunte a un puerto removido sin su equivalente documentado

#### Scenario: Dry-run alcanza N8N

- **WHEN** se ejecuta el harness `scripts/dry_run`
- **THEN** alcanza N8N por el canal habilitado por la estrategia de acceso elegida
