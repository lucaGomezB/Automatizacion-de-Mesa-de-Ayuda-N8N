## MODIFIED Requirements

### Requirement: TLS termination via nginx reverse proxy

El stack de docker-compose SHALL incluir un servicio nginx que actue como proxy inverso y termine TLS para todo el trafico HTTP externo. El proxy SHALL aceptar exclusivamente TLS 1.2 y TLS 1.3 en todos sus bloques `server` que escuchan en 443 (incluido el catch-all) y MUST rechazar el handshake de versiones anteriores. El proxy MUST servir la API del backend bajo el prefijo `/api/` y la SPA del frontend bajo la ruta raiz `/`. La comunicacion entre contenedores en la red Docker MUST permanecer en HTTP plano, dentro del perimetro de confianza.

#### Scenario: Backend API accessible through HTTPS via nginx

- **WHEN** un cliente envia `GET https://localhost/api/v1/health`
- **THEN** nginx reenvia la peticion a `http://backend:8000/api/v1/health` y devuelve la respuesta JSON del backend con HTTP 200

#### Scenario: Frontend accessible through HTTPS via nginx

- **WHEN** un cliente envia `GET https://localhost/`
- **THEN** nginx reenvia la peticion a `http://frontend:3000/` y devuelve el HTML de la SPA

#### Scenario: Se negocian unicamente TLS 1.2 y TLS 1.3

- **WHEN** un cliente que ofrece hasta TLS 1.3 se conecta a `localhost:443` con SNI `localhost`
- **THEN** el handshake se completa con TLS 1.3
- **AND** un cliente limitado a TLS 1.2 completa el handshake con TLS 1.2

#### Scenario: Las versiones anteriores a TLS 1.2 se rechazan

- **WHEN** un cliente que ofrece como maximo TLS 1.1 intenta el handshake contra `localhost:443`
- **THEN** el handshake falla y no se establece la sesion TLS

#### Scenario: Internal backend-to-N8N communication stays on plain HTTP

- **WHEN** el backend envia una peticion a un webhook de N8N (por ejemplo `http://n8n:5678/webhook/notificacion-clasificacion`)
- **THEN** la peticion alcanza a N8N directamente por la red Docker sin pasar por nginx

#### Scenario: Internal healthchecks continue to work over plain HTTP

- **WHEN** Docker Compose ejecuta el healthcheck del servicio backend
- **THEN** `urllib.request.urlopen('http://localhost:8000/health')` tiene exito porque corre dentro del contenedor sobre el puerto HTTP interno

### Requirement: Self-signed certificate generation script

El proyecto SHALL proveer dos scripts de generacion de certificados, `openssl/generate-certs.sh` (bash) y `openssl/generate-certs.ps1` (PowerShell), que creen un certificado X.509 autofirmado y su clave privada en `openssl/mesa.crt` y `openssl/mesa.key`. El certificado MUST usar clave RSA de 2048 bits, firma SHA-256, validez de 365 dias y nombres alternativos (SAN) para `localhost`, `mesa.local` e `127.0.0.1`. Los scripts MUST ser idempotentes (una nueva ejecucion sobrescribe los archivos). El directorio `openssl/` MUST contener un `.gitkeep` versionado. El servicio nginx MUST montar `./openssl` en `/etc/nginx/certs` en modo solo lectura, y `nginx/nginx.conf` MUST referenciar `/etc/nginx/certs/mesa.crt` y `/etc/nginx/certs/mesa.key`.

#### Scenario: Bash script generates certificate on Linux/macOS

- **WHEN** se ejecuta `bash openssl/generate-certs.sh` en un sistema con `openssl` disponible
- **THEN** se crean `openssl/mesa.crt` y `openssl/mesa.key`, y el certificado es un X.509 autofirmado valido por 365 dias con SAN `localhost`, `mesa.local` e `127.0.0.1`

#### Scenario: PowerShell script generates certificate on Windows

- **WHEN** se ejecuta `.\openssl\generate-certs.ps1` en Windows con OpenSSL disponible (Git for Windows, Chocolatey o instalacion independiente)
- **THEN** se crean `openssl/mesa.crt` y `openssl/mesa.key` con las mismas propiedades que los generados por el script bash

#### Scenario: Script is idempotent

- **WHEN** el script se ejecuta por segunda vez con `mesa.crt` y `mesa.key` ya presentes
- **THEN** los archivos existentes se sobrescriben con un certificado nuevo sin error

#### Scenario: Rutas de certificados coherentes entre artefactos

- **WHEN** una prueba estructural compara el montaje del servicio nginx en `docker-compose.yml`, las directivas `ssl_certificate` y `ssl_certificate_key` de `nginx/nginx.conf` y los nombres de salida de los scripts
- **THEN** las tres fuentes resuelven a los mismos archivos `mesa.crt` y `mesa.key` montados en `/etc/nginx/certs`

### Requirement: Frontend API base URL uses HTTPS

El servicio `frontend` de docker-compose SHALL recibir como argumento de build `VITE_API_BASE_URL=https://localhost`, es decir, el ORIGEN sin el prefijo `/api/v1` (que el cliente HTTP de la SPA agrega una sola vez), de modo que el bundle compilado llame a la API por HTTPS a traves del proxy nginx. El valor MUST llegar como argumento de build y no como variable de entorno de runtime, porque el bundle estatico ya compilado ignora el entorno de ejecucion.

#### Scenario: Frontend environment variable uses HTTPS

- **WHEN** se inspecciona la seccion `build.args` del servicio `frontend` en `docker-compose.yml`
- **THEN** `VITE_API_BASE_URL` vale `https://localhost`, sin el sufijo `/api/v1`

#### Scenario: La SPA llama a la API por HTTPS

- **WHEN** la SPA compilada realiza una llamada a la API
- **THEN** la URL resultante es `https://localhost/api/v1/...` y atraviesa el proxy nginx

### Requirement: Docker Compose UX preserved

El comando `docker compose up -d` SHALL funcionar tras los pasos previos unicos de generar los certificados y crear `App/Backend/.env` a partir de su plantilla. El stack base (sin perfiles) SHALL estar compuesto por `postgres`, `backend`, `n8n`, `frontend` y `nginx`; Redis fue retirado (c-62) y MUST NOT reaparecer. El servicio nginx MUST esperar a backend y frontend mediante `depends_on` con `condition: service_started`.

#### Scenario: First-time setup works end-to-end

- **WHEN** un desarrollador clona el repositorio, genera los certificados, crea `App/Backend/.env` y ejecuta `docker compose up -d`
- **THEN** `postgres`, `backend`, `n8n`, `frontend` y `nginx` alcanzan el estado healthy o running

#### Scenario: Nginx starts after backend and frontend

- **WHEN** docker compose arranca el stack
- **THEN** el contenedor nginx no arranca hasta que backend y frontend esten al menos en estado `service_started`, evitando respuestas 502 durante el arranque

### Requirement: Certificate and key files excluded from version control

Los archivos generados `openssl/*.crt`, `openssl/*.key`, `openssl/*.pem` y `openssl/*.csr` SHALL estar excluidos de Git mediante `.gitignore`. El archivo `openssl/.gitkeep` SHALL estar versionado para preservar el directorio al clonar. Ninguna verificacion automatizada del borde MUST versionar certificados ni claves que genere.

#### Scenario: Certificate files are gitignored

- **WHEN** se ejecuta `git check-ignore openssl/mesa.crt openssl/mesa.key` despues de generar los certificados
- **THEN** ambos archivos figuran como ignorados y no aparecen como no rastreados ni preparados en `git status`

#### Scenario: Certs directory exists after clone

- **WHEN** un desarrollador clona el repositorio
- **THEN** el directorio `openssl/` existe y contiene al menos `.gitkeep` y los scripts de generacion

## REMOVED Requirements

### Requirement: N8N environment variables reflect HTTPS external URL

**Reason**: contradice la postura implementada y validada desde c-62: N8N se sirve en HTTP sobre `127.0.0.1:5678` (`N8N_PROTOCOL=http`, `WEBHOOK_URL=http://localhost:5678/`) porque el callback OAuth local solo admite `http://localhost`, y nginx no enruta hacia N8N, de modo que N8N nunca forma parte del borde TLS.

**Migration**: reemplazado por el requisito agregado "N8N fuera del borde TLS y acotado a loopback". La comunicacion backend -> N8N sigue en `http://n8n:5678/webhook/...` por la red interna.

## ADDED Requirements

### Requirement: N8N fuera del borde TLS y acotado a loopback

El servicio `n8n` SHALL publicarse unicamente en la interfaz de loopback (`127.0.0.1:5678`) con `N8N_PROTOCOL=http`, y MUST NOT exponerse fuera del host ni a traves de nginx: ninguna `location` de `nginx/nginx.conf` SHALL enrutar hacia N8N. El backend SHALL alcanzar los webhooks de N8N por la red Docker interna en HTTP plano.

#### Scenario: N8N publicado solo en loopback

- **WHEN** se inspecciona la configuracion efectiva del servicio `n8n` con `docker compose config`
- **THEN** su unica publicacion es `127.0.0.1:5678 -> 5678` y `N8N_PROTOCOL` vale `http`

#### Scenario: Nginx no enruta hacia N8N

- **WHEN** una prueba estructural recorre las directivas `proxy_pass` de `nginx/nginx.conf`
- **THEN** ninguna apunta al servicio `n8n`

### Requirement: Exposicion unica del borde

En la configuracion efectiva por defecto (`docker compose config`), el unico servicio publicado fuera de loopback SHALL ser `nginx`, con los puertos 80 y 443; todo otro puerto publicado por el stack base MUST estar acotado a `127.0.0.1`. Un mapeo sin direccion de host (por ejemplo `"80:80"`) SHALL tratarse como publicacion en todas las interfaces. La documentacion del archivo de compose MUST describir esta postura y MUST NOT afirmar que 80 y 443 estan acotados a loopback.

#### Scenario: Solo nginx se publica fuera de loopback

- **WHEN** una prueba estructural clasifica cada publicacion de puertos del stack base
- **THEN** las unicas publicaciones fuera de loopback pertenecen a `nginx` y corresponden a los puertos 80 y 443

#### Scenario: Un mapeo desnudo se detecta como exposicion total

- **WHEN** un servicio distinto de `nginx` declara una publicacion sin direccion de host
- **THEN** la prueba estructural falla e identifica el servicio y el puerto expuesto

#### Scenario: El comentario del compose describe la postura real

- **WHEN** se lee el comentario de cabecera de `docker-compose.yml`
- **THEN** declara que nginx publica 80/443 en todas las interfaces como unico borde y que PostgreSQL y N8N quedan acotados a loopback

### Requirement: Verificacion automatizada del borde TLS en el despliegue de referencia

El repositorio SHALL proveer una verificacion automatizada que, sobre el despliegue de referencia (la composicion versionada `docker-compose.yml` + `nginx/nginx.conf` levantada en limpio con certificados autofirmados efimeros generados por `openssl/generate-certs.sh`), compruebe en ejecucion: el handshake TLS 1.3 y TLS 1.2 con la identidad del servidor verificada contra el certificado generado (como ancla de confianza o por huella SHA-256), el rechazo de TLS 1.1, la redireccion 301 de HTTP a HTTPS con ruta y query preservadas y sin `Strict-Transport-Security`, la respuesta HTTPS del backend a traves del proxy con `Strict-Transport-Security: max-age=31536000; includeSubDomains` y las cabeceras de seguridad configuradas, la cabecera `Server` sin numero de version y el cierre de la conexion sin respuesta ante un Host desconocido. La verificacion MUST terminar con exit code distinto de cero ante cualquier incumplimiento o comprobacion no ejecutada, MUST NOT requerir secretos y MUST NOT versionar certificados ni claves. Su resultado SHALL poder conservarse como evidencia con el commit verificado y la fecha.

#### Scenario: Handshake moderno con identidad verificada

- **WHEN** la verificacion se conecta a `localhost:443` con SNI `localhost` ofreciendo TLS 1.3 y luego limitada a TLS 1.2
- **THEN** ambos handshakes se completan con la version esperada y el certificado presentado coincide con el generado para la corrida

#### Scenario: Version heredada rechazada o no verificable

- **WHEN** la verificacion intenta un handshake ofreciendo como maximo TLS 1.1
- **THEN** el handshake falla por rechazo del servidor y el check pasa
- **AND** si el cliente local no puede ofrecer TLS 1.1, el check queda pendiente y la verificacion no informa exito

#### Scenario: Redireccion HTTP a HTTPS preservando ruta y query

- **WHEN** la verificacion envia `GET http://localhost/api/v1/health?origen=smoke`
- **THEN** recibe HTTP 301 con `Location: https://localhost/api/v1/health?origen=smoke` y sin cabecera `Strict-Transport-Security`

#### Scenario: Respuesta HTTPS con HSTS y cabeceras de seguridad

- **WHEN** la verificacion envia `GET https://localhost/api/v1/health`
- **THEN** recibe HTTP 200 del backend con `Strict-Transport-Security: max-age=31536000; includeSubDomains`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` y `Permissions-Policy`
- **AND** la cabecera `Server` no incluye numero de version

#### Scenario: Host desconocido rechazado por el catch-all

- **WHEN** la verificacion envia una peticion con un Host que no figura en la lista de `server_name`
- **THEN** la conexion se cierra sin respuesta HTTP

#### Scenario: Evidencia sin secretos

- **WHEN** la verificacion completa y produce su reporte
- **THEN** el reporte registra el commit, la fecha y el resultado de cada comprobacion, y no contiene claves privadas ni certificados
