## 0. Dependencia de c-29-seam-tests y baseline

- [x] 0.1 Confirmar que el change `c-29-seam-tests` existe y contiene los tests RED de las costuras listadas en este change; ejecutar el subconjunto RED y verificar que falla por el defecto esperado (no por error de coleccion). Sin esto, no iniciar GREEN.
- [x] 0.2 Congelar el baseline actual antes de tocar codigo: `cd App/Backend; pytest` (267 passed, 18 skipped, 1 xfailed), `cd App/Frontend; npm run test` y `cd evaluation; pytest`; registrar los numeros para probar que no se rompio lo verde.
- [x] 0.3 Verificar que `openspec status --change c-30-bugfix-seams` marca `tasks` como listo y que `openspec validate c-30-bugfix-seams --strict` pasa.

## 1. Blockers N8N — autenticacion y agente (B-01 a B-07)

- [x] 1.1 (B-01, CRITICO — gobernanza CRITICA: proponer y esperar aprobacion antes de escribir) Agregar un nodo de login dinamico al workflow que invoque `POST /api/v1/auth/login` con las credenciales del operador (almacenadas como credencial de N8N, nunca en `n8n/workflow.json`), extraiga el token de la respuesta y lo inyecte como `Authorization: Bearer {{ ... }}` en los nodos HTTP que llaman al backend; verificar con el test RED de `c-29-seam-tests` que el alta llega con header y responde 201, que sin credencial valida responde 401 de forma visible y que el login corre en cada ejecucion (no un Bearer estatico de 24 h).
- [x] 1.2 (B-02) Conectar y configurar un Chat Model en el nodo `AI Agent`; verificar con el test RED que el agente produce salida no vacia en la ejecucion.
- [x] 1.3 (B-03) Reemplazar el prompt estatico por interpolacion de la descripcion del payload del trigger (pseudonimizada); verificar con el test RED que el prompt enviado contiene la descripcion concreta del trigger.
- [x] 1.4 (B-04) Alinear el contrato del agente a JSON `{sector_predicho, confianza}` y ajustar el nodo de validacion (tipo/rango, rechazo de booleanos, vocabulario canonico); verificar con el test RED que una salida valida se acepta y una con sector invalido deriva a revision humana.
- [x] 1.5 (B-05) Reconfigurar `Rutear por canal de origen` en modo reglas con una regla por canal normalizado y `fallbackOutput` definido; verificar con el test RED que cada canal produce su indice y un canal desconocido usa el fallback.
- [x] 1.6 (B-06) Corregir `responseMode`/grafo para que todo `respondToWebhook` sea alcanzable y ninguna rama que deba responder quede sin respuesta; verificar con el test RED que el cliente recibe respuesta con codigo y cuerpo definidos.
- [x] 1.7 (B-07) Extraer la descripcion del correo desde la ruta efectiva del payload de Outlook en modo `simple`; verificar con el test RED que un correo con cuerpo produce descripcion no vacia y pasa la validacion cuando cumple el minimo.

## 2. Blockers backend y frontend (BE B1, FE 1)

- [x] 2.1 (BE B1) Reemplazar `func.strftime` en `App/Backend/app/services/estadisticas_service.py` por un helper de agrupacion temporal portable por dialecto (`date_trunc`/`to_char` en PostgreSQL, `strftime` en SQLite) con funcion pura de calculo de periodo; verificar con el test RED que `/api/v1/estadisticas/tendencias` responde 200 en PostgreSQL y en SQLite con la misma forma de `series`.
- [x] 2.2 (FE 1) Unificar la base URL en `App/Frontend/src/services/api.ts` leyendo `VITE_API_BASE_URL` con un unico fallback, y propagarla en la build (`ARG`/`ENV` en `App/Frontend/Dockerfile` mas build arg en `docker-compose.yml`); verificar con el test RED que la constante no se duplica y que la build usa el valor provisto.

## 3. Alto (B-08 a B-12, BE B2/B3/B4, FE 2)

- [x] 3.1 (B-08) Incluir `canal_origen_id` en la estructura normalizada enviada al backend; verificar con el test RED que el incidente persistido tiene canal distinto de `NULL` en los tres canales.
- [x] 3.2 (B-09) Conectar el formulario web al webhook N8N para el alta de incidentes (middleware permitido si hiciera falta), NO directo a la API del backend; verificar con el test RED que el formulario dispara el webhook (no `POST /api/v1/incidentes`) y muestra exito/error de forma observable. Eliminar el webhook N8N queda FUERA de alcance.
- [x] 3.3 (B-10) Alinear `n8n/twilio/twiml.xml` (`transcribeCallback` vs Event Streams) y eliminar el dominio placeholder en `n8n/twilio/README.md`; verificar con el test RED que la configuracion de transcripcion apunta al endpoint correcto y sin dominio placeholder.
- [x] 3.4 (B-11) Reemplazar `$env.BACKEND_URL` por una construccion de URL compatible con N8N v2; verificar con el test RED que el workflow resuelve la URL base sin variables bloqueadas.
- [x] 3.5 (B-12) Eliminar el nodo de reenvio vacio conectado en bucle; verificar con el test RED de estructura del grafo que no existe el bucle.
- [x] 3.6 (BE B2) Validar la existencia de FK de catalogo en la capa de servicio antes de persistir (PATCH y creacion); verificar con el test RED que una FK inexistente responde 4xx y no persiste ni corrompe, tanto en SQLite (con `PRAGMA foreign_keys=ON`) como en PostgreSQL.
- [x] 3.7 (BE B3) Registrar handler para `CanalOrigenNotFoundError` (y errores de dominio equivalentes) que responde 4xx con el envelope; verificar con el test RED que un canal inexistente no produce 500.
- [x] 3.8 (BE B4, gobernanza ALTA — datos personales) Agregar allowlist de terminos tecnicos/productos/marcas previa a la regla de `[PERSONA]` en `App/Backend/app/utils/pseudonymizer.py`; verificar con el test RED que `Windows Server`, `Active Directory`, `SQL Server` y `Google Chrome` se preservan y que un nombre propio real sigue enmascarado.
- [x] 3.9 (FE 2) Normalizar la barra final en la construccion de rutas del cliente para evitar el 307 que pierde `Authorization` y body; verificar con el test RED que la llamada autenticada no redirige y conserva header y cuerpo.

## 4. Medio (B-13 a B-16, BE B5 a B8)

- [x] 4.1 (B-13) Corregir las expresiones `.id` invalidas de los nodos; verificar con el test RED que toda expresion referencia un campo existente del payload.
- [x] 4.2 (B-14) Corregir el registro de auditoria para distinguir creados de rechazados; verificar con el test RED que una entrada rechazada no se audita como alta.
- [x] 4.3 (B-15) Conservar la causa del fallo del validador IA sin reetiquetar el canal a `correo`; verificar con el test RED que un fallo de validacion en canal `web` mantiene `web`.
- [x] 4.4 (B-16) Conectar la rama falsa del telefono de regreso al agente o a un camino que complete el flujo; verificar con el test RED que una transcripcion que no cumple la condicion no termina en un nodo sin continuacion.
- [x] 4.5 (BE B5) Centralizar el envelope de error en `App/Backend/app/core/error_handlers.py` para 422 y 401/403 (sin `detail` en la raiz); verificar con el test RED que ambos codigos responden con `error.code`/`error.message` y que `extractApiErrorMessage` del frontend sigue normalizando.
- [x] 4.6 (BE B6) Conservar referencia de la tarea `asyncio.create_task` fire-and-forget en un `set` con `add_done_callback`; verificar con el test RED que la tarea no es recolectada y el webhook se invoca.
- [x] 4.7 (BE B7) Reutilizar `genai.Client` (lazy) y cerrarlo en el shutdown de la aplicacion en lugar de instanciarlo por request; verificar con el test RED que no se crea un cliente por request y que se cierra al apagar la app.
- [x] 4.8 (BE B8) Mover el acceso directo a sesion/ORM de rutas y servicios hacia la capa de repositorios; verificar por inspeccion y con el test RED que ninguna ruta instancia repositorios ni usa la sesion directamente.

## 5. Bajo (B-17, FE 3 a FE 8)

- [x] 5.1 (B-17) Corregir la URL del backend sin barra final en los nodos; verificar con el test RED que la URL termina en `/api/v1/` correcto y no hay 307/404 por barra.
- [x] 5.2 (FE 3) Invalidar la query del detalle del ticket tras mutaciones (edicion y cambio de estado); verificar con el test RED que el detalle se refetcha con los datos nuevos.
- [x] 5.3 (FE 4) Cambiar el contador de revision humana para que refleje el total del backend y no el tamano de la pagina; verificar con el test RED que con mas items que la pagina el contador muestra el total.
- [x] 5.4 (FE 5) Corregir el calculo de fechas del dashboard para que no se desplacen por UTC; verificar con el test RED que la fecha mostrada coincide con la local.
- [x] 5.5 (FE 6) Corregir el estado de carga compuesto (cargando con al menos una consulta pendiente; error solo con todas fallidas sin datos); verificar con el test RED de ambos escenarios.
- [x] 5.6 (FE 7) Corregir los volumenes de hot-reload para que monten la ruta que el proceso ejecuta; verificar que una edicion de fuente se refleja en el contenedor de desarrollo.
- [x] 5.7 (FE 8) Aislar la red en los tests del frontend (mock en el limite de red, fallo ante request no mockeado); verificar que la suite pasa con la red deshabilitada.

## 6. Verificacion de sospechas (no confirmadas)

- [x] 6.1 VERIFICAR `_RE_TELEFONO`: agregar caso RED con un telefono seguido de digito para comprobar si deja un digito orfano; si queda orfano, corregir el patron y confirmar el fix con el test.
- [x] 6.2 VERIFICAR `_validate_gemini_response`: agregar caso RED con `confianza` booleana para comprobar si la acepta; si la acepta, endurecer la validacion de tipo y confirmar.
- [x] 6.3 VERIFICAR cache de rotacion de la clave de cifrado de pseudonimizacion: probar la rotacion de clave y determinar si hay cache stale; si la hay, invalidarla y confirmar con el test.
- [x] 6.4 VERIFICAR JWT sin `exp` obligatorio: probar un token sin `exp` y determinar si se acepta; si se acepta, exigir `exp` y confirmar (gobernanza CRITICA: proponer antes de escribir).
- [x] 6.5 VERIFICAR dedupe de correos duplicados: probar dos correos identicos y determinar si se crean dos incidentes; si no hay dedupe, decidir e implementar segun corresponda (gobernanza ALTA).
- [x] 6.6 VERIFICAR `typeVersions` hardcodeados en N8N vs imagen `latest`: comprobar compatibilidad de versiones del workflow con la imagen desplegada y documentar o ajustar sin romper el contrato.

## 6b. Eliminacion del skip restante (directiva no-skips)

- [x] 6b.1 Agregar el fixture `seed_catalogs` al test `test_endpoint_detalle_no_expone_original` de `App/Backend/tests/test_schemas_pseudonimizacion.py` para que `POST /api/v1/incidentes/` disponga de catalogo (Estado/CanalOrigen/Sector) y devuelva 201.
- [x] 6b.2 Eliminar el bloque `pytest.skip(...)` de ese test y reemplazarlo por `assert response.status_code == 201, response.text`; el test debe correr SIEMPRE y fallar fuerte ante regresiones, nunca auto-omitirse.
- [x] 6b.3 Verificar que la suite backend ya no reporta ningun `skip` (0 skipped salvo el `xfail` preexistente) y adjuntar la evidencia del conteo.

## 7. Verificacion de integracion y cierre

- [x] 7.1 Ejecutar todas las suites tras los fixes (`cd App/Backend; pytest`, `cd App/Frontend; npm run test`, `cd evaluation; pytest`) y verificar que los numeros son iguales o mejores que el baseline de 0.2, con los tests de `c-29-seam-tests` ahora en GREEN.
- [x] 7.2 Ejecutar `cd App/Backend; pytest tests/test_openapi_sync.py -v` y verificar que el contrato OpenAPI sigue sincronizado; si cambio, regenerar `docs/openapi.json` con el comando documentado en `AGENTS.md`.
- [x] 7.3 Ejecutar `cd App/Backend; ruff check .` y `cd App/Frontend; npm run lint` y verificar cero errores nuevos respecto del baseline.
- [x] 7.4 Verificar end-to-end con el stack levantado (`docker compose up -d` con nombre fijo `mesa_local`) el tramo compartido de alta de incidente autenticado segun `c-29-seam-tests`. Alcance alcanzado: el canal WEB queda verificado end-to-end de forma automatizada y de costo cero por el arnes de c-31 (`scripts/dry_run/dry_run.py`: webhook N8N -> normalizacion/validacion -> login dinamico -> `POST /api/v1/incidentes/` -> persistencia con canal correcto); evidencia previa de la sesion de implementacion de c-31: 12/12 checks, costo cero. El canal CORREO es opt-in (`--with-email`) y requiere credenciales SMTP/Outlook no configuradas en el entorno local, por lo que queda como verificacion manual de despliegue. El canal TELEFONO requiere Twilio (servicio pago), fuera del alcance de costo cero, y queda como verificacion manual de despliegue. Nota de honestidad: el arnes NO se re-ejecuto en esta sesion de division de PR porque `scripts/dry_run/` es entregado por c-31 y no esta presente en esta rama; se cita la evidencia previa, no una corrida nueva.
- [x] 7.5 Verificar que no se modificaron los strings canonicos de sector ni el contrato multietiqueta de C-27 y que no se toco `docs/Tesis/**`; confirmar con `git diff --stat`.
- [x] 7.6 Corregir el body de respuesta del webhook N8N (B-06 incompleto): `Confirmacion web al usuario` (`respondToWebhook`) responde 200 con body VACIO, por lo que el usuario no recibe el JSON de confirmacion. Diagnosticar (sospecha: `respondWith: json` con `responseBody` stringificado via `JSON.stringify`) y corregir en `n8n/workflow.json`; verificar con el harness de C-31 que el check `e2e:webhook-response` pasa a GREEN y que los tests de contrato N8N siguen verdes.
