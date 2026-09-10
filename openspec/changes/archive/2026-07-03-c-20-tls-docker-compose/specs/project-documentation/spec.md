## MODIFIED Requirements

### Requirement: Anexo G — Guía operativa

El proyecto SHALL incluir `docs/operational-guide.md` con los procedimientos operativos del sistema: despliegue (via `docker compose`, incluyendo la generacion de certificados TLS como prerrequisito), respaldo (backup) y restauracion de la base PostgreSQL, y monitoreo de salud mediante los endpoints de chequeo expuestos por el backend. Los comandos documentados MUST ser coherentes con la configuracion real de `docker-compose.yml` (nombres de servicios, puertos publicados — 80/443 para nginx, 5433 para postgres, 6379 para redis, 5678 para n8n —, credenciales de ejemplo y endpoints de health accesibles via `https://localhost/api/v1/health`).

#### Scenario: Procedimientos cubren despliegue, backup y monitoreo

- **WHEN** se inspecciona `docs/operational-guide.md`
- **THEN** incluye secciones para despliegue (con paso de generacion de certificados), backup/restauracion de PostgreSQL y monitoreo de salud, cada una con comandos concretos

#### Scenario: Los comandos coinciden con docker-compose

- **WHEN** se contrastan los comandos de la guia contra `docker-compose.yml`
- **THEN** los nombres de servicios referenciados existen en el compose, las URL de verificacion de salud usan HTTPS (`https://localhost/api/v1/health` en lugar de `http://localhost:8000/health`), y los puertos documentados para el proxy son 80 y 443

### Requirement: README de despliegue local reproducible

El proyecto SHALL actualizar `README.md` con instrucciones de despliegue local que permitan levantar el sistema completo en menos de 15 minutos a partir de un clon limpio. Las instrucciones MUST listar los prerrequisitos (incluyendo OpenSSL para la generacion de certificados), el paso de generacion de certificados TLS (`scripts/generate-certs.sh` o `scripts/generate-certs.ps1`), el paso de configuracion de variables de entorno (desde una plantilla `.env.example`), y el comando de arranque (`docker compose up -d`). Las URL de verificacion de salud MUST referenciar `https://localhost/api/v1/health`. La seccion MUST referenciar la guia operativa y la de troubleshooting para procedimientos detallados, e incluir una nota sobre la advertencia de certificado auto-firmado en el navegador.

#### Scenario: README cubre el camino de despliegue local

- **WHEN** se lee la seccion de despliegue local del `README.md`
- **THEN** incluye prerrequisitos (OpenSSL), generacion de certificados, configuracion de `.env`, el comando `docker compose up -d` y una verificacion de salud con HTTPS, sin contradecir `docker-compose.yml`

#### Scenario: README advierte sobre certificado auto-firmado

- **WHEN** se lee la seccion de despliegue local del `README.md`
- **THEN** incluye una nota explicando que el navegador mostrara una advertencia de seguridad por ser un certificado auto-firmado y que es seguro proceder en el entorno de desarrollo local

#### Scenario: README enlaza la documentacion operativa

- **WHEN** se revisan los enlaces del README
- **THEN** referencia `docs/operational-guide.md` y `docs/troubleshooting.md` para los procedimientos detallados
