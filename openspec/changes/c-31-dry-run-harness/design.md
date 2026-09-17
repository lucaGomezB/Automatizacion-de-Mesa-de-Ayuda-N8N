## Context

Ver `proposal.md — Why` para la motivación. Estado actual y restricciones que moldean el enfoque:

- Los tres canales (correo Outlook, webhook de formulario web, teléfono Twilio) convergen en un tramo compartido: normalizar -> validar -> login dinámico -> `POST /api/v1/incidentes/` -> persistir + clasificar -> confirmación. El trigger es lo único específico de cada canal, por lo que validar el canal web valida el tramo compartido.
- El stack corre con `docker compose` y nombre de proyecto fijo `mesa_local` (declarado en `docker-compose.yml:29`). Servicios relevantes: `nginx` (80/443, terminación TLS), `backend` (interno, `alembic upgrade head` al arrancar), `n8n` (5678 publicado), `postgres` (5433).
- `docker-compose.yml:69` usa `env_file: ./App/Backend/.env` para el backend y `environment:` para overrides puntuales. El override por `environment` tiene mayor precedencia que `env_file`.
- Autenticación: `POST /api/v1/auth/login` (JSON `{"username","password"}` -> `{"access_token","token_type"}`); la migration `003_add_users_table.py` siembra un operador local `admin`/`admin123` si la tabla está vacía.
- Clasificación: umbral determinístico 0.90 y umbral de revisión humana 0.70 (`openspec/config.yaml`). `GeminiClassifier` documenta estrategia de resiliencia: ante cualquier falla (timeout, respuesta inválida, API no disponible) retorna fallback con `confianza=0.0` y `requires_revision_humana=True`.
- `n8n/workflow.json` tiene un `id` de workflow de nivel superior estable (`P7w2iELDu7O3e8B0`), `active: false`, y el nodo webhook del formulario usa la ruta `incidente-web`. El contenedor monta el JSON en `/data/Automatizacion_Mesa_de_Ayuda.json`.
- Convención de automatización existente: scripts pareados `.sh` + `.ps1` para operaciones de shell (`scripts/backup.*`, `openssl/generate-certs.*`, `scripts/up.*`) y un `Makefile` opcional como alias. La suite de backend es offline por diseño (conftest fuerza SQLite in-memory y mockea Gemini/N8N), por lo que no sirve para un recorrido contra el stack real.
- Dependencia funcional: `c-30-bugfix-seams` corrige los defectos de cableado que este arnés ejercita. Sin c-30 aplicado, el recorrido del arnés debe fallar ruidosamente en el punto roto (ese es su propósito), pero un recorrido en verde exige c-30.

## Goals / Non-Goals

**Goals:**

- Un único punto de entrada ejecutable que lleve a un recorrido web end-to-end de costo cero, con verificación de persistencia y canal, y fallo ruidoso y accionable.
- Preflight de contratos que falle temprano y barato, antes de gastar tiempo en el recorrido completo.
- Guardarraíles duros y verificables de ausencia de servicios pagos (Gemini y Twilio).
- Topología local reutilizable, no destructiva y multiplataforma.

**Non-Goals:**

- Cubrir el canal telefónico en el camino de costo cero; solo se documenta un procedimiento manual.
- Automatizar la importación de credenciales de Outlook/Twilio/Gemini.
- Reemplazar las suites de tests existentes (unit/integration offline) ni la evaluación del clasificador.
- Modificar `docker-compose.yml`, `n8n/workflow.json` o código de producto bajo `App/**`.

## Decisions

### D1 — CLI Python standalone en `scripts/dry_run/` (no scripts pareados `.sh`/`.ps1`, no pytest)

El arnés se implementa como un ejecutable Python 3.12 con biblioteca estándar (HTTP, JSON, sondeo acotado, aserciones, salida estructurada de checks) bajo `scripts/dry_run/`, con un alias opcional en el `Makefile` (por ejemplo `make dry-run`).

- **Razón**: la lógica del arnés es intensiva en HTTP/JSON y en aserciones con mensajes accionables, y necesita ser idéntica en Linux/macOS y Windows. Python 3.12 ya es dependencia del proyecto (backend), así que no introduce un lenguaje nuevo. Los scripts pareados `.sh`/`.ps1` de la casa son apropiados para operaciones de shell, no para un orquestador con lógica; mantener dos implementaciones duplicaría la lógica y la probabilidad de deriva.
- **Alternativas consideradas**: (a) bash + `curl` + `jq` — descartado porque `jq` no está garantizado y las aserciones JSON en shell son frágiles; (b) extender pytest — descartado porque la suite backend es offline por contrato (SQLite in-memory, Gemini/N8N mockeados) y no puede contra un stack real; (c) script único en uno de los dos SO — descartado por la promesa multiplataforma.

### D2 — Aislamiento del costo con un archivo de override de Compose que inyecta `GEMINI_API_KEY` ficticia

El arnés levanta (o reutiliza) el backend pasando un archivo de override propio (`scripts/dry_run/compose.dry-run.yml`, nuevo) que fija `environment: GEMINI_API_KEY=<ficticia>` para el servicio `backend`, mediante `docker compose -f docker-compose.yml -f scripts/dry_run/compose.dry-run.yml up -d`. NO se modifica `docker-compose.yml` ni `App/Backend/.env`. Antes de ejecutar el recorrido, el arnés afirma la clave efectiva con `docker compose exec backend printenv GEMINI_API_KEY` (o consultando la configuración del proceso) y aborta si no es ficticia.

- **Razón**: `docker-compose.yml` no interpola `GEMINI_API_KEY` sino que la toma de `env_file`, por lo que exportar una variable en el shell no la sobreescribe. La precedencia de `environment` sobre `env_file` permite inyectar una clave ficticia sin tocar los archivos versionados. El override es un archivo nuevo y efímero del arnés, no un cambio a la topología de producto.
- **Alternativas consideradas**: (a) editar `App/Backend/.env` con una clave ficticia — descartado porque pisaría la clave real del usuario y es destructivo; (b) exportar la variable en el shell — descartado porque `env_file` la ignoraría; (c) un contenedor backend dedicado — descartado por agregar superficie y duplicar la configuración del servicio.
- **Trade-off**: un archivo de override adicional que debe mantenerse alineado con el servicio `backend` si este cambia. Mitigado porque el override solo setea una variable de entorno.

### D3 — El canal web es el recorrido obligatorio; el correo es opcional y el teléfono queda fuera

El recorrido obligatorio simula el formulario web: `POST` al webhook de N8N (`incidente-web`) con el payload de un incidente, y verificación posterior de que el incidente fue persistido consultando `GET /api/v1/incidentes/{id}` con token de login, afirmando `canal_origen_id == 2`. El canal correo se documenta como paso gratuito y opcionalmente automatizable; el teléfono se documenta como procedimiento manual acotado.

- **Razón**: como los tres canales convergen, validar el canal web valida todo el tramo compartido (normalización, login dinámico, alta, persistencia, clasificación y ruteo). El correo depende de credenciales de Outlook y el teléfono de Twilio; ninguno es necesario para probar la plomería compartida.
- **Alternativas consideradas**: (a) recorrer los tres canales — descartado por requerir credenciales y, en el caso de Twilio, costo real; (b) pegarle directo a `POST /api/v1/incidentes/` sin pasar por N8N — descartado porque dejaría sin validar el tramo N8N, que es donde viven la mayoría de los defectos de cableado que c-30 corrige.

### D4 — Preflight como aserciones sobre contratos observables, con redirects deshabilitados

El preflight verifica: login devuelve `access_token`/`token_type`; alta válida devuelve 201; descripción de menos de 10 caracteres devuelve 422; la ruta sin barra final se detecta como 307 (sin seguir redirects, para no ocultar la pérdida de `Authorization` y body); webhook de N8N alcanzable. Cada verificación produce un check nombrado con resultado y, al fallar, un mensaje accionable.

- **Razón**: son exactamente los contratos que la tarea de memoria humana no retiene y que rompen el flujo de forma silenciosa (el 307 con pérdida de credenciales es el caso paradigmático). Detectar 307 exige deshabilitar el seguimiento automático de redirects en el cliente HTTP.
- **Alternativas consideradas**: confiar en la suite de tests — descartado porque los tests usan rutas bien formadas contra ASGI y no ejercitan el proxy ni el webhook real.

### D5 — Descripciones determinísticas y aceptación del fallback seguro

Las descripciones de prueba se eligen para contener palabras clave que el clasificador determinístico resuelve con confianza `>= 0.90`, evitando escalar. Si por elección de la descripción se escala igual, con la clave ficticia la escalada falla de forma segura a `confianza=0.0` (comportamiento documentado de resiliencia de `GeminiClassifier`); el incidente debe persistir igual y el arnés reporta la etapa observada.

- **Razón**: el objetivo del arnés es probar la persistencia y el cableado, no medir calidad de clasificación. Forzar casos determinísticos evita cualquier chance de llamada paga y hace el resultado reproducible.
- **Alternativas consideradas**: usar casos ambiguos para ejercitar la escalada — descartado porque introduciría variabilidad y una dependencia innecesaria del camino pago.

### D6 — Import/activación idempotente del workflow de N8N por id estable

El arnés importa `n8n/workflow.json` como `/data/Automatizacion_Mesa_de_Ayuda.json` dentro del contenedor `n8n` y lo activa, apoyándose en el `id` de nivel superior estable (`P7w2iELDu7O3e8B0`) para que reimportar actualice el mismo workflow en vez de duplicarlo. Si el workflow ya está activo, lo reutiliza. Tras importar y activar, el arnés afirma que la ruta `incidente-web` responde; si detecta duplicados del workflow, falla ruidosamente con instrucciones de limpieza.

- **Razón**: el JSON ya trae un id estable, lo que resuelve la preocupación de idempotencia anotada en `c-28-bootstrap-un-comando` (que asumía ausencia de id de nivel superior). La aserción posterior del webhook es la prueba real de que importar y activar funcionaron, más robusta que confiar en el código de salida del CLI.
- **Alternativas consideradas**: (a) no importar y documentar la importación manual (postura de c-28) — descartado porque la tarea pide que el arnés importe/active el workflow para ser verdaderamente end-to-end; (b) reconciliar por API REST interna con credenciales de N8N — descartado como camino primario por depender de endpoints internos no versionados; el CLI dentro del contenedor es el camino documentado en la guía operativa.

### D7 — Credenciales locales por variables de entorno, sin loguear secretos

El arnés obtiene `username`/`password` de variables de entorno (`DRY_RUN_USERNAME`/`DRY_RUN_PASSWORD`) con default al operador local sembrado (`admin`/`admin123`). La password nunca se imprime ni se incluye en el resumen de checks.

- **Razón**: permite usar el operador sembrado en el camino feliz sin hardcodear credenciales como única vía y sin filtrar valores a la salida, en línea con el estilo del preflight de `scripts/up.sh`.
- **Trade-off**: el default usa la credencial de desarrollo documentada; en un entorno con `JWT_SECRET_KEY` distinto, el operador puede sobreescribir con variables.

### D8 — Documentación de canales en la misma capacidad, sin delta sobre `project-documentation`

La documentación del arnés (uso, preflight, guardarraíles, procedimiento de correo y procedimiento telefónico manual) se entrega como parte de esta capacidad nueva y no modifica `project-documentation`.

- **Razón**: `c-28-bootstrap-un-comando` ya tiene un delta pendiente sobre `project-documentation` sin archivar; agregar otro delta ahí aumentaría el riesgo de conflicto al archivar. El comportamiento documentado del arnés es parte de su contrato y se especifica en `dry-run-harness`.

## Risks / Trade-offs

- **[Esquema del webhook de N8N ambiguo]** `docker-compose.yml` declara `N8N_PROTOCOL: https` y `WEBHOOK_URL: https://localhost:5678/`, pero publica el puerto `5678` como HTTP plano sin configuración TLS. → Mitigación: el arnés prueba ambos esquemas de forma acotada y falla ruidosamente indicando cuál respondió y cuál no; el resultado no cambia el contrato de la especificación.
- **[Semántica de import según versión de N8N]** la imagen es `n8nio/n8n:latest`, por lo que el comportamiento de import puede variar. → Mitigación: aserción posterior de que el webhook responde y de que no hay duplicados; fallo accionable con pasos de limpieza.
- **[Precedencia del override de Compose]** si cambia la forma en que el backend toma `GEMINI_API_KEY`, el override podría no tener efecto. → Mitigación: afirmar la clave efectiva con `printenv` dentro del contenedor antes de ejecutar; abortar si no es ficticia.
- **[Recorrido en verde bloqueado por c-30]** los defectos de cableado actuales harán fallar el arnés. → Mitigación: es el comportamiento deseado; el arnés debe fallar en el punto exacto con mensaje accionable, y el recorrido en verde se espera recién con c-30 aplicado.
- **[Falso negativo por corrida parcial]** un problema de timing (el webhook responde antes de que el backend persista) podría dar un falso rojo. → Mitigación: el arnés sondea la persistencia con timeout acotado y reintentos, no una única lectura inmediata.
- **[Deriva del archivo de override]** si el servicio `backend` cambia de nombre o de variables, el override puede quedar desalineado. → Mitigación: el override solo fija `GEMINI_API_KEY` y el preflight afirma su efecto; un desalineamiento produce fallo ruidoso, no un falso verde.

## Migration Plan

1. Agregar `scripts/dry_run/` (entrypoint CLI, módulos de preflight, recorrido y guardarraíles) y `scripts/dry_run/compose.dry-run.yml`.
2. Agregar el objetivo opcional `dry-run` al `Makefile` (alias de conveniencia; los scripts no dependen de `make`).
3. Documentar el arnés, incluido el procedimiento gratuito de correo (opcional) y el procedimiento telefónico manual y acotado.
4. Rollback: eliminar `scripts/dry_run/`, el objetivo del `Makefile` y la sección de documentación; no hay estado persistente ni migración de datos involucrada.

## Open Questions

- El esquema y el eventual header de autenticación básica del webhook de N8N (`http` vs `https` en 5678) se resuelven durante la implementación probando ambos; no cambian la especificación ni el desglose de tareas.
- La disponibilidad de comandos de importación/activación y de limpieza por CLI en la imagen `n8nio/n8n:latest` se verifica al implementar; la aserción posterior del webhook se mantiene como criterio de aceptación independientemente del comando usado.
