## MODIFIED Requirements

### Requirement: Especificación OpenAPI 3.1 estática generada desde la app

El proyecto SHALL publicar la especificación OpenAPI 3.1 de la interfaz REST en `docs/openapi.json`, generada **desde la aplicación FastAPI** (`app.main:app`) mediante un script reproducible, nunca escrita a mano. El documento MUST declarar versión OpenAPI `3.1.x` y MUST contener los puntos de entrada efectivamente expuestos por la app (incidentes, clasificaciones, health). El script de generación MUST poder ejecutarse en un entorno limpio, sin base de datos en ejecución y sin variables de entorno reales, inyectando dummies suficientes para instanciar `Settings`; ese conjunto MUST incluir explícitamente `JWT_SECRET_KEY`, además de `DATABASE_URL`, `GEMINI_API_KEY` y `PSEUDONYMIZATION_ENCRYPTION_KEY`. El uso documentado del script (docstring) MUST referenciar las rutas vigentes bajo `App/Backend/`, MUST NOT presentar `Gestion_Incidentes/` como ubicación del módulo ni de sus comandos, y su ejemplo de `--output` MUST ser consistente con la ruta de salida por defecto real del script.

#### Scenario: openapi.json es un OpenAPI 3.1 bien formado

- **WHEN** se carga `docs/openapi.json`
- **THEN** es JSON válido, su campo `openapi` comienza con `3.1`, y contiene un objeto `paths` no vacío con las rutas bajo `/api/v1`

#### Scenario: El spec se genera desde la app, no a mano

- **WHEN** se ejecuta el script de generación apuntando a `app.main:app`
- **THEN** produce un `openapi.json` cuyos `paths` coinciden con los `@router` declarados en `App/Backend/app/routes/`

#### Scenario: El script corre con dummies suficientes, sin JWT_SECRET_KEY real

- **WHEN** se ejecuta el script de generación en un entorno sin `JWT_SECRET_KEY` definida y sin un `.env` descubrible, apuntando a una salida temporal
- **THEN** termina con código de salida 0 y produce un documento OpenAPI 3.1 válido, sin fallar la validación de `Settings`

#### Scenario: El uso documentado del script no referencia la ruta obsoleta

- **WHEN** se inspecciona el docstring de `App/Backend/scripts/export_openapi.py`
- **THEN** los comandos y rutas que documenta referencian `App/Backend/` y su ejemplo de `--output` es consistente con la salida por defecto real
- **AND** no presenta `Gestion_Incidentes` como ubicación del módulo, de su `.env` ni de sus archivos

### Requirement: Anexo G — Guía operativa

La guia operativa (`docs/operational-guide.md`) SHALL presentar el comando unico de arranque (`bash scripts/up.sh` en Linux/macOS, `.\scripts\up.ps1` en Windows, o `make up` cuando `make` este disponible) como el camino recomendado para desplegar el stack local, y MUST mantener el camino manual (`openssl/generate-certs.sh` o `openssl/generate-certs.ps1` seguido de `docker compose up -d`) documentado como alternativa. La guia SHALL documentar que el comando unico ejecuta el preflight de costo antes de tocar Docker y que, si el preflight falla, el arranque se bloquea; asimismo MUST documentar el bypass explicito `UP_SKIP_COST_PREFLIGHT=1` y la advertencia audible que el arranque imprime al usarlo. El bloque dotenv de la seccion 1.2 (Configurar variables de entorno) MUST listar `JWT_SECRET_KEY`, ademas de `DATABASE_URL`, `GEMINI_API_KEY` y `PSEUDONYMIZATION_ENCRYPTION_KEY`, con una descripcion de su proposito como clave de firma HS256. Los comandos y rutas de archivo de la guia MUST referenciar la ubicacion post-reestructuracion del modulo (`App/Backend/`) y MUST NOT presentar `Gestion_Incidentes/` como la ubicacion vigente del modulo, de su `.env` o de sus archivos. La guia SHALL incluir referencias a los scripts automatizados de backup (`scripts/backup.sh` y `scripts/backup.ps1`) como metodo recomendado para backups diarios, reemplazando el comando manual de cron documentado en la seccion 3. La seccion 8 (Evaluacion del clasificador) MUST documentar la invocacion real del runner desde la raiz del repositorio (`PYTHONPATH=App/Backend python -m evaluation.run_evaluation`), MUST NOT indicar `python run_evaluation.py` ni un `cd evaluation` que no resuelva los imports del paquete, MUST NOT referenciar `evaluation/generate_corpus.py` ni afirmar la existencia de un generador de corpus con seed fijo, y MUST apuntar al procedimiento real de carga del corpus documentado en `docs/como_cargar_datos_corpus.md`. La seccion 8 MUST documentar el gate de corrida paga del runner: que una corrida que invocaria el clasificador real exige confirmacion explicita con `--confirm-paid` o `EVALUATION_CONFIRM_PAID=1`, que sin confirmacion aborta con codigo de salida 2, y que al confirmar se imprime una estimacion de costo.

#### Scenario: Despliegue presenta el comando unico como camino recomendado

- **WHEN** se lee la seccion 1.3 (Generar certificados TLS y levantar los servicios) de `docs/operational-guide.md`
- **THEN** el documento referencia el comando unico (`bash scripts/up.sh`, `.\scripts\up.ps1` o `make up`) como camino recomendado
- **AND** describe que ese comando genera los certificados TLS si faltan, levanta el stack y valida la salud

#### Scenario: Gate de costo y bypass documentados en la guia

- **WHEN** se lee la seccion de despliegue de `docs/operational-guide.md`
- **THEN** el documento menciona el preflight de costo que corre antes del arranque
- **AND** documenta el bypass explicito `UP_SKIP_COST_PREFLIGHT=1` y que su uso emite una advertencia audible

#### Scenario: Camino manual permanece documentado

- **WHEN** se lee la seccion 1.3 de la guia operativa
- **THEN** los comandos de generacion manual de certificados (`openssl/generate-certs.sh` / `openssl/generate-certs.ps1`) y `docker compose up -d` siguen documentados como alternativa
- **AND** la guia no afirma que el camino manual sea el recomendado

#### Scenario: Seccion 1.2 lista JWT_SECRET_KEY

- **WHEN** se lee la seccion 1.2 (Configurar variables de entorno) de `docs/operational-guide.md`
- **THEN** el bloque dotenv incluye `JWT_SECRET_KEY` junto a `DATABASE_URL`, `GEMINI_API_KEY` y `PSEUDONYMIZATION_ENCRYPTION_KEY`
- **AND** describe `JWT_SECRET_KEY` como la clave de firma HS256 e incluye como generarla

#### Scenario: Comandos de la guia usan rutas post-reestructuracion

- **WHEN** se inspeccionan los comandos y rutas de archivo de `docs/operational-guide.md`
- **THEN** referencian `App/Backend/.env`, `App/Backend/requirements.txt` y `App/Backend/` donde corresponde
- **AND** no presentan `Gestion_Incidentes/` como la ubicacion vigente del modulo

#### Scenario: Seccion de backup referencia scripts

- **WHEN** se lee la seccion 3 (Backup y restauracion de PostgreSQL) de `docs/operational-guide.md`
- **THEN** el documento referencia los scripts `scripts/backup.sh` y `scripts/backup.ps1`
- **AND** describe como configurar la ejecucion automatica via cron (Linux/macOS) o Task Scheduler (Windows)
- **AND** incluye el comando de ejemplo para ambos entornos

#### Scenario: Comando manual permanece documentado

- **WHEN** se lee la seccion 3 de la guia operativa
- **THEN** el comando `docker compose exec postgres pg_dump` sigue documentado como alternativa manual
- **AND** la documentacion de restauracion no sufre cambios

#### Scenario: Seccion 8 usa la invocacion real del runner

- **WHEN** se lee la seccion 8 (Evaluacion del clasificador) de `docs/operational-guide.md`
- **THEN** el comando de corrida documentado es `PYTHONPATH=App/Backend python -m evaluation.run_evaluation`, ejecutado desde la raiz del repositorio
- **AND** el documento no presenta `python run_evaluation.py` ni un `cd evaluation` como forma de invocacion

#### Scenario: Seccion 8 no referencia el generador de corpus eliminado

- **WHEN** se inspecciona la seccion 8 de `docs/operational-guide.md`
- **THEN** el documento no referencia `evaluation/generate_corpus.py` ni afirma un generador de corpus con seed fijo
- **AND** apunta al procedimiento real de carga del corpus en `docs/como_cargar_datos_corpus.md`

#### Scenario: Gate de corrida paga documentado en la guia

- **WHEN** se lee la seccion 8 de `docs/operational-guide.md`
- **THEN** el documento menciona que una corrida que invocaria el clasificador real exige confirmacion explicita con `--confirm-paid` o `EVALUATION_CONFIRM_PAID=1`
- **AND** documenta que sin confirmacion la corrida aborta con codigo de salida 2 y que al confirmar se imprime una estimacion de costo
