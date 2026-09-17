## Why

El proyecto va a consumir servicios pagos por uso: Gemini cobra cada clasificacion que escala mas alla del clasificador deterministico y Twilio cobra cada llamada y cada transcripcion. Hoy no existe una forma local y sin costo de probar el tramo compartido de registro de incidentes: la unica validacion end-to-end disponible es "configurar credenciales reales, mandar un incidente y mirar", lo que convierte cualquier error de cableado en credito quemado. Se necesita un arnés local que pruebe la plomería de punta a punta antes de que la primera credencial externa toque el sistema.

## What Changes

Se define (no se implementa en este change) un arnés de ejecución en seco, local y de costo cero:

- Nuevo CLI local, con hogar sugerido `scripts/dry_run/`, que levanta o reutiliza el stack `mesa_local` con una `GEMINI_API_KEY` ficticia, importa/activa el workflow de N8N, envía un incidente simulado del formulario web por el webhook de N8N, y verifica que el incidente quede PERSISTIDO con el `canal_origen_id` correcto.
- El arnés falla RUIDOSAMENTE con un mensaje accionable ante cualquier quiebre de cableado, en lugar de devolver un resultado ambiguo.
- Verificaciones de contrato automatizadas previas (preflight) contra el backend y el webhook de N8N: login local devuelve `access_token`, un alta válida devuelve 201, una descripción de menos de 10 caracteres devuelve 422, la falta de barra final se detecta (307) y el webhook de N8N está alcanzable.
- Guardarraíles obligatorios: el arnés NO DEBE invocar servicios pagos (ni Gemini real ni Twilio) y DEBE afirmar que una clave ficticia de Gemini está en efecto antes de ejecutar.
- Estrategia de mock barato: correr el backend con `GEMINI_API_KEY` ficticia para que el clasificador determinístico resuelva los casos de alta confianza y cualquier escalada falle a un fallback seguro (`confianza=0.0`) en vez de llamar (y pagar) a Gemini; las descripciones de prueba se eligen para pegar en las palabras clave determinísticas.
- Canal correo (Outlook) como paso documentado y opcionalmente automatizado, ya que recibir es gratis (el trigger hace polling).
- Canal teléfono (Twilio) FUERA del camino de costo cero: solo se documenta un procedimiento manual acotado a 1-2 llamadas para cuando el usuario tenga credenciales.

Fuera de alcance explícito:

- Implementar el arnés, sus scripts o sus tests (este change solo declara requirements, decisiones y tareas).
- Cambios de producto bajo `App/**`, cambios de `docker-compose.yml`, o cambios de `n8n/workflow.json`.
- Modificar el contrato de la API, los strings canónicos de sector o el pipeline de clasificación.
- Ejecutar llamadas reales a Twilio o a Gemini en cualquier punto del arnés.
- Alineación con el documento de tesis (la tesis es referencia, no criterio de aceptación).

## Capabilities

### New Capabilities

- `dry-run-harness`: validación local, reproducible y de costo cero del tramo compartido de registro de incidentes, con preflight de contratos, guardarraíles que garantizan ausencia de servicios pagos, verificación end-to-end del canal web (webhook N8N -> normalización/validación/login dinámico -> `POST /api/v1/incidentes/` -> persistencia con canal correcto), fallo ruidoso accionable, y documentación del canal correo (gratis, paso opcional) y del canal teléfono (manual, fuera del camino de costo cero).

### Modified Capabilities

- Ninguna. El arnés es una capacidad nueva de herramienta de desarrollo; no cambia el comportamiento especificado de ninguna capacidad de producto existente.

## Impact

- **Nuevos archivos (a implementar en el change, no aquí)**: `scripts/dry_run/` (entrypoint CLI y módulos del arnés) y su documentación operativa.
- **Documentación**: una sección nueva del arnés de ejecución en seco en la guía operativa (o doc dedicada en `docs/`) y un objetivo opcional en el `Makefile` como alias de conveniencia.
- **Sin cambios de producto**: no se toca `App/**`, ni `docker-compose.yml`, ni `n8n/workflow.json`, ni migraciones, ni contratos de API.
- **Contratos que el arnés verifica (no modifica)**: `POST /api/v1/auth/login` (JSON `{"username","password"}` -> `{"access_token","token_type"}`), `Authorization: Bearer <access_token>`, `POST /api/v1/incidentes/` (`descripcion` con `min_length=10`, `prioridad` opcional, `canal_origen_id` entero donde 1=correo, 2=formulario web, 3=llamada telefónica), y exigencia de barra final para evitar el 307 que pierde `Authorization` y body.
- **Gobernanza**: MEDIA (herramienta de desarrollo, sin efecto sobre una capacidad de producto y sin datos personales reales), con un componente de disciplina de costo tratado como guardarraíl duro.
- **Dependencias**: Docker + Docker Compose (proyecto fijo `mesa_local`, sin `-p`), el stack `mesa_local`, N8N accesible en `http://localhost:5678`, y `curl` o cliente HTTP equivalente. Para un recorrido en verde, depende de `c-30-bugfix-seams` (los defectos de cableado que el arnés ejercita y que hoy lo harían fallar).
