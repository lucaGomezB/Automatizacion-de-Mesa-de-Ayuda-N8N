## MODIFIED Requirements

### Requirement: README de despliegue local reproducible

El proyecto SHALL actualizar `README.md` con instrucciones de despliegue local que permitan levantar el sistema completo en menos de 15 minutos a partir de un clon limpio, ofreciendo un comando unico de arranque como camino recomendado. Las instrucciones MUST documentar el comando unico (`make up` o, en su defecto, `bash scripts/up.sh` en Linux/macOS y `scripts/up.ps1` en Windows), MUST listar los prerrequisitos (Docker + Docker Compose, OpenSSL para la generacion de certificados, y `make` como conveniencia opcional) incluyendo como obtener `make` en Windows (`choco install make`) o como ejecutar el `.ps1` directamente sin make, y MUST mantener documentado el camino manual (generacion de certificados via `openssl/generate-certs.sh` o `openssl/generate-certs.ps1`, configuracion de `.env` desde la plantilla `.env.example`, y `docker compose up -d`). Las URL de verificacion de salud MUST referenciar `https://localhost/api/v1/health`. La seccion MUST referenciar la guia operativa y la de troubleshooting para procedimientos detallados, e incluir una nota sobre la advertencia de certificado auto-firmado en el navegador.

#### Scenario: README cubre el camino de despliegue local

- **WHEN** se lee la seccion de despliegue local del `README.md`
- **THEN** presenta el comando unico de arranque (`make up` o `bash scripts/up.sh` / `scripts/up.ps1`) como camino recomendado, e incluye prerrequisitos (Docker + Docker Compose, OpenSSL, `make` opcional), generacion de certificados, configuracion de `.env`, el comando `docker compose up -d` y una verificacion de salud con HTTPS, sin contradecir `docker-compose.yml`

#### Scenario: README explica como obtener make en Windows

- **WHEN** se lee la seccion de despliegue local del `README.md`
- **THEN** documenta como instalar `make` en Windows (por ejemplo `choco install make`) o como ejecutar `scripts/up.ps1` directamente sin make

#### Scenario: README advierte sobre certificado auto-firmado

- **WHEN** se lee la seccion de despliegue local del `README.md`
- **THEN** incluye una nota explicando que el navegador mostrara una advertencia de seguridad por ser un certificado auto-firmado y que es seguro proceder en el entorno de desarrollo local

#### Scenario: README enlaza la documentacion operativa

- **WHEN** se revisan los enlaces del README
- **THEN** referencia `docs/operational-guide.md` y `docs/troubleshooting.md` para los procedimientos detallados