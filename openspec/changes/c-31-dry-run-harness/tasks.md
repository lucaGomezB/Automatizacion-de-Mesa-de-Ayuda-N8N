## 0. Baseline y dependencia

- [x] 0.1 Confirmar el estado del change `c-30-bugfix-seams` (`openspec status --change c-30-bugfix-seams --json`): registrar si está aplicado o pendiente. El arnés puede implementarse y probar su fallo ruidoso sin c-30, pero un recorrido en verde requiere c-30 corregido.
- [x] 0.2 Registrar el baseline de las suites offline antes de tocar nada: `cd App/Backend; pytest`, `cd App/Frontend; npm run test`, `cd evaluation; pytest`; anotar los números para probar que este change no rompió tests existentes.
- [x] 0.3 Verificar que el stack `mesa_local` levanta sano con la topología documentada (`docker compose ps` con backend/postgres/n8n healthies) y confirmar la versión efectiva de la imagen de N8N.

## 1. Estructura del arnés y entrypoint CLI

- [x] 1.1 Crear `scripts/dry_run/` con un entrypoint CLI ejecutable (Python 3.12, biblioteca estándar) y un módulo de checks; verificar que `python scripts/dry_run/<entrypoint>.py --help` liste las opciones soportadas sin errores de importación.
- [x] 1.2 Definir el modelo de resultado de check (nombre, estado, detalle, acción sugerida) y su impresión de resumen; verificar con tests unitarios de la función pura de formateo que un fallo incluye nombre y acción y que un éxito no imprime secretos.
- [x] 1.3 Definir el contrato de exit codes (cero solo si todas las verificaciones pasan; distinto de cero ante cualquier quiebre o verificación pendiente); verificar con tests unitarios de la función pura que decide el exit code a partir del conjunto de resultados.

## 2. Guardarraíl de costo cero

- [x] 2.1 Crear `scripts/dry_run/compose.dry-run.yml` (archivo nuevo, sin modificar `docker-compose.yml`) que fije `GEMINI_API_KEY` ficticia para el servicio `backend`; verificar que `docker compose -f docker-compose.yml -f scripts/dry_run/compose.dry-run.yml config` resuelve el backend con la clave ficticia.
- [x] 2.2 Implementar la afirmación de la clave efectiva (`docker compose exec backend printenv GEMINI_API_KEY` o equivalente) que aborta si no es ficticia; verificar con un test unitario de la clasificación de claves (ficticia vs real) y con una ejecución manual contra el stack.
- [x] 2.3 Implementar guardarraíles que garanticen ausencia de llamadas a Twilio y de llamadas Gemini reales; verificar que una ejecución completa no crea recursos ni llamadas de Twilio y que ninguna rama del arnés invoca el cliente pago.
- [x] 2.4 Verificar que las descripciones de prueba eligen el camino determinístico y que, ante escalada, el resultado observado es el fallback seguro `confianza=0.0` sin llamada paga; documentar la evidencia.

## 3. Levantado/reutilización del stack e import del workflow N8N

- [x] 3.1 Implementar el levantamiento/reutilización no destructivo del stack con nombre fijo `mesa_local` y sin `-p`, con espera acotada de salud; verificar que reutiliza un stack ya sano y que levanta uno detenido, sin recrear contenedores sanos.
- [x] 3.2 Implementar la importación y activación idempotente de `n8n/workflow.json` apoyada en el id estable de nivel superior y la verificación posterior de que la ruta `incidente-web` existe; verificar con una reimportación que no aparecen workflows duplicados.
- [x] 3.3 Verificar que el arnés no deja modificados `docker-compose.yml`, `n8n/workflow.json` ni archivos bajo `App/**` (por ejemplo con `git status --porcelain` al final de una corrida).

## 4. Preflight de contratos

- [x] 4.1 Implementar el preflight de login: `POST /api/v1/auth/login` con `{"username","password"}` devuelve `access_token` y `token_type`; verificar con una ejecución contra el stack y con el check reportado en el resumen.
- [x] 4.2 Implementar la verificación de alta válida que responda 201 usando `Authorization: Bearer <access_token>`; verificar la respuesta y el reporte del check.
- [x] 4.3 Implementar la verificación de `descripcion` con menos de 10 caracteres que debe responder 422; verificar el código y el reporte del check.
- [x] 4.4 Implementar la detección de la falta de barra final como 307 con redirects deshabilitados (sin seguir el redirect); verificar que se observa el 307 y que se reporta la pérdida de `Authorization` y body.
- [x] 4.5 Implementar la verificación de alcanzabilidad del webhook de N8N resolviendo el esquema (`http`/`https` en 5678) de forma acotada; verificar que registra cuál esquema respondió y que falla ruidosamente si ninguno responde.
- [x] 4.6 Implementar el aborto temprano del recorrido end-to-end cuando un check de preflight falla; verificar con un fallo inducido que no se envía ningún incidente y que el exit code es distinto de cero.

## 5. Recorrido end-to-end del canal web

- [x] 5.1 Implementar el envío del incidente simulado del formulario web por el webhook de N8N con descripción determinística; verificar que el webhook responde y que el arnés continúa al sondeo.
- [x] 5.2 Implementar el sondeo acotado de persistencia consultando `GET /api/v1/incidentes/{id}` con token; verificar que un incidente correctamente cableado se recupera y que un incidente no persistido produce fallo ruidoso con mensaje accionable.
- [x] 5.3 Afirmar que el incidente persistido tiene `canal_origen_id` igual a 2 (formulario web); verificar con un caso de canal incorrecto que el arnés falla e informa canal observado y esperado.
- [x] 5.4 Verificar en un recorrido completo (con c-30 aplicado) que las verificaciones de preflight y de recorrido terminan en verde y el exit code es cero.

## 6. Fallo ruidoso y resumen

- [x] 6.1 Implementar el reporte por verificación y el resumen final de checks ejecutados; verificar que un quiebre de cableado produce exit code distinto de cero con el componente afectado y el siguiente paso concreto.
- [x] 6.2 Verificar que una verificación omitida o incompleta nunca se reporta como éxito; cubrir con un test que marque una verificación como pendiente y confirme el exit code distinto de cero.

## 7. Canal correo (gratuito, opcional)

- [x] 7.1 Documentar el procedimiento de ejecución en seco del canal correo: inducción del mensaje, verificación de persistencia con `canal_origen_id` igual a 1 y credenciales requeridas; verificar que el procedimiento es reproducible sin credenciales reales para el camino mínimo.
- [x] 7.2 Implementar (opcional, gated por opt-in y ausente del camino mínimo obligatorio) la variante automatizada del canal correo; verificar que el arnés completa sin credenciales de correo y que la variante automatizada no se ejecuta por defecto.

## 8. Canal teléfono (manual, fuera del camino de costo cero)

- [x] 8.1 Documentar el procedimiento manual acotado a una o dos llamadas para el canal teléfono, marcado explícitamente como pago y fuera del camino de costo cero; verificar que la documentación incluye credenciales requeridas y pasos de verificación de persistencia con `canal_origen_id` igual a 3.
- [x] 8.2 Verificar que ninguna variante del arnés marca, crea o dispara recursos o llamadas de Twilio; cubrir con una inspección del camino de ejecución y, si aplica, un test que garantice que no hay invocación a Twilio.

## 9. Integración en Makefile y documentación

- [x] 9.1 Agregar el objetivo opcional `dry-run` al `Makefile` que delega en el entrypoint; verificar que `make dry-run` funciona y que el entrypoint sigue siendo ejecutable sin `make`.
- [x] 9.2 Documentar en la guía operativa (o doc dedicada bajo `docs/`) el uso del arnés: prerrequisitos, guardarraíles de costo, preflight, recorrido web, canal correo opcional y canal teléfono manual; verificar que un operador puede seguir el procedimiento sin leer el código.
- [x] 9.3 Confirmar que no se abre un delta sobre `project-documentation` y que la documentación del arnés vive en la capacidad `dry-run-harness`; verificar que `openspec validate c-31-dry-run-harness --strict` pasa.

## 10. Verificación final e integración

- [x] 10.1 Ejecutar el arnés de punta a punta contra un stack `mesa_local` limpio y confirmar el recorrido web en verde con todas las verificaciones reportadas.
- [x] 10.2 Ejecutar el arnés contra un quiebre de cableado inducido (por ejemplo, sin c-30 aplicado o con el webhook inalcanzable) y confirmar el fallo ruidoso accionable y el exit code distinto de cero.
- [x] 10.3 Repetir las suites offline del baseline (`cd App/Backend; pytest`, `cd evaluation; pytest`) y confirmar que el change no rompió tests existentes.
- [x] 10.4 Verificar que el repositorio queda sin artefactos temporales ni secretos (revisar `git status --porcelain` y que el arnés no deja archivos con credenciales).