## Context

Ver `proposal.md — Why` para la motivacion. El estado relevante para disenar la correccion:

- Las suites estan en verde pero el flujo real esta roto: el backend exige JWT desde `C-15` (`3ed4dbf`) y N8N nunca se actualizo; el nodo `AI Agent` no tiene Chat Model; el `Switch` de canal esta en modo expresion; y el envelope de error es inconsistente (`detail` en 422/401).
- El stack esta documentado en `openspec/config.yaml`: FastAPI 0.115 + SQLAlchemy 2.0 async sobre PostgreSQL 15.5 (produccion) y SQLite in-memory (tests); N8N 1.62 autoalojado; React 18 + React Query + Axios.
- Este change DEFINE el trabajo. La ejecucion con TDD depende de `c-29-seam-tests`, que escribe los tests que fallan (RED). Sin esos tests, GREEN no tiene criterio de aceptacion verificable.
- Gobernanza por dominio: los cambios de auth (header `Authorization`, JWT) son CRITICA; N8N y servicios backend son ALTA; pseudonimizacion es ALTA (Ley 25.326); frontend e infra de tests son MEDIA/BAJA. En CRITICA y ALTA se propone y se espera aprobacion humana antes de escribir.

## Goals / Non-Goals

**Goals:**

- Definir el orden de correccion por severidad y las decisiones tecnicas que hacen cada fix verificable por un test de `c-29-seam-tests`.
- Cerrar las costuras que hoy dejan pasar defectos (auth N8N, contrato agente-validador, envelope de error, FK, SQL portable, pseudonimizador, capa de datos del frontend).
- Mantener intactos los contratos ya congelados: strings canonicos de sector (C-27), contrato multietiqueta, rutas `/api/v1/`.

**Non-Goals:**

- No se implementan correcciones en este change; se declaran requirements, decisiones y tareas.
- No se alinea el documento de tesis (referencia, no criterio de aceptacion).
- No se cambia el esquema de base de datos ni los strings de dominio.
- No se elimina el webhook de N8N ni se cambia el alta del formulario web para llamar directo a la API del backend; el formulario usa el webhook (B-09), con middleware si hiciera falta.

## Decisions

### D1 — Orden de ejecucion por severidad, con TDD dependiente de c-29

Las tareas se ordenan: blockers (N8N B-01..B-07, BE B1, FE 1) -> alto (B-08..B-12, BE B2/B3/B4, FE 2) -> medio (B-13..B-16, BE B5..B8) -> bajo (B-17, FE 3..8) -> verificacion de sospechas. Cada tarea de correccion referencia el test RED de `c-29-seam-tests` que la valida; si el test no existe, la tarea se bloquea. Razon: el sistema entero esta roto en las costuras; arreglar en orden de impacto evita refactors prematuros sobre comportamiento aun no fijado. Alternativa descartada: agrupar por componente (todo N8N, todo backend); no respeta dependencias reales (por ejemplo, FE 1 sin B-01 sigue dando 401).

### D2 — Auth N8N via nodo de login dinamico, no token estatico

El workflow SHALL obtener el JWT con un nodo de login dentro del propio flujo: un HTTP Request a `POST /api/v1/auth/login` con las credenciales del operador (almacenadas como credencial de N8N, nunca en `n8n/workflow.json`), que extrae el token de la respuesta; el nodo que crea el incidente envia `Authorization: Bearer {{ <token> }}`. Razon: el JWT del backend expira (`JWT_EXPIRE_MINUTES=1440`, 24 h), por lo que un Bearer estatico guardado en una credencial `httpHeaderAuth` falla a diario y el workflow regresa a 401; el login dinamico renueva el token en cada ejecucion y ademas evita secretos en el repo (el hook `.githooks/pre-commit` bloquea secretos). Alternativa descartada: credencial estatica `httpHeaderAuth` con un token de larga vida (muere cada 24 h y no hay refresh). Gobernanza CRITICA: aprobacion humana explicita antes de tocar auth.

### D3 — Contrato del agente: JSON `{sector_predicho, confianza}` validado como tipo

El prompt SHALL exigir JSON con `sector_predicho` y `confianza`; el nodo de validacion SHALL parsear y validar tipo/rango, rechazando booleanos y valores fuera del vocabulario canonico. Se alinea el validador N8N con el validador backend (`Anexo H §H.3`) para que no existan dos contratos. Alternativa descartada: parsear texto libre y extraer con regex (fragil, ya causante de B-04/B-15).

### D4 — Switch en modo reglas con `fallbackOutput`

`Rutear por canal de origen` pasa a modo `rules` con una regla por valor normalizado (`correo`, `web`, `telefonia`), `fallbackOutput` definido y salida como indice entero. Razon: el modo expresion ignora reglas y no produce un indice; evaluar la respuesta del backend es un error de capa. Alternativa descartada: un IF por canal (duplica ramas y complica el grafo).

### D5 — `responseMode: responseNode` con `respondToWebhook` alcanzable

Se conserva `responseNode` pero se garantiza que toda rama que deba responder alcance un `respondToWebhook` con respuesta definida; el webhook de "fire-and-forget" puede usar `onReceived`/`lastNode`. Razon: hoy hay un `respondToWebhook` inalcanzable que deja al cliente sin respuesta. Alternativa descartada: `lastNode` global (el flujo tiene ramas asincronas).

### D6 — Envelope de error centralizado en `core/error_handlers.py`

Se registran handlers para `RequestValidationError` (422), errores de auth (401/403) y errores de dominio (`CanalOrigenNotFoundError`, `EstadoNotFoundError`, `SectorNotFoundError`) que emiten `{"error": {code, message, details?}}`. La validacion de existencia de FK se hace en la capa de servicio consultando el repositorio antes de persistir. Razon: un solo punto de traduccion a HTTP; evita 500 y `detail` filtrado. Alternativa descartada: try/except por endpoint (duplica logica y deja huecos, como B3).

### D7 — SQL portable para agrupacion temporal, seleccionada por dialecto

`estadisticas_service.py` deja de usar `func.strftime`. La agrupacion se expresa con un helper que elige la funcion segun `bind.dialect.name` (`date_trunc`/`to_char` en PostgreSQL; `strftime` en SQLite), con una funcion pura de calculo de periodo testeable sin base de datos. Razon: SQLite-only rompe PostgreSQL (BE B1) y el helper testeable permite cubrir ambos dialectos en la costura. Alternativa descartada: agregar en Python tras traer todas las filas (correcto pero costoso y no escala).

### D8 — Pseudonimizador con allowlist previa a la regla de personas

Antes de aplicar la deteccion de nombres propios, el pseudonimizador consulta una lista de terminos tecnicos/productos/marcas (`Windows Server`, `Active Directory`, `SQL Server`, `Google Chrome`, etc.) que quedan exentos. El orden no altera el conteo de reemplazos. Razon: el sobre-enmascaramiento degrada la clasificacion y las metricas F1 (BE B4). Alternativa descartada: agrandar la exclusion de sectores (no cubre productos).

### D9 — Base URL del frontend desde una unica fuente y propagada en build

`api.ts` lee `import.meta.env.VITE_API_BASE_URL` con un unico fallback documentado; se normaliza barra final para evitar 307 (FE 2). El `Dockerfile` recibe `ARG VITE_API_BASE_URL` + `ENV` antes de `npm run build`, y `docker-compose.yml` lo pasa como build arg. Razon: hoy hay dos fuentes (constante y env) y Docker la ignora (FE 1). Alternativa descartada: inyectar la URL en runtime (mas complejo que el costo del defecto).

### D10 — Fire-and-forget con referencia retenida

La utilidad de notificacion conserva la tarea en un `set` a nivel de modulo con `add_done_callback` que la descarta. Razon: un `asyncio.create_task` sin referencia puede ser recolectado antes de completarse (BE B6). Alternativa descartada: `BackgroundTasks` de FastAPI (cambia el contrato de la utilidad y no cubre el caso de webhook en flujo interno).

### D11 — Cliente Gemini reutilizado y cerrado en el ciclo de vida

`genai.Client` se instancia una vez (lazy) y se cierra en el shutdown de la aplicacion, en lugar de crear uno por request (BE B7). Razon: fuga de recursos y overhead por request. Alternativa descartada: pool de clientes (complejidad innecesaria para el volumen esperado).

### D12 — Disciplina de capas: acceso a datos fuera de rutas

El acceso directo a la sesion/ORM en rutas o servicios se mueve a la capa de repositorios (BE B8). Se verifica por inspeccion. Razon: es la regla del proyecto en `AGENTS.md` y el origen de varios 500 por consultas mal ubicadas.

### D13 — Costuras de test: FK en SQLite y alcance de event loop en PG

`conftest.py` habilita `PRAGMA foreign_keys=ON` por conexion (event listener de SQLAlchemy). La suite PG corrige el alcance del event loop para que fixtures y tests compartan el bucle correcto. Razon: sin esto, defectos de FK (BE B2) y fallos de infraestructura de test (observados) no se detectan o se atribuyen mal. Estas correcciones son habilitadoras de `c-29-seam-tests`, no producto.

## Risks / Trade-offs

- [Login dinamico depende del endpoint `POST /api/v1/auth/login` y agrega una llamada por ejecucion] -> El nodo de login debe propagar el error si el login falla; los tests de costura cubren login exitoso y fallido.
- [Cambiar `responseMode` puede alterar el contrato del webhook del formulario] -> Verificar contra el cliente frontend (B-09, FE 1) antes de fijar la respuesta.
- [Allowlist de marcas puede dejar pasar un nombre propio] -> Cubrir con tests que exijan que un nombre real siga enmascarado (incluido en el spec).
- [Helper SQL dialect-aware puede divergir entre motores] -> Cubrir `dia`/`mes` en SQLite y PostgreSQL con los mismos casos esperados.
- [Corregir envelope 422/401 puede romper clientes que leian `detail`] -> El frontend usa `extractApiErrorMessage`; actualizar su normalizacion y cubrirla con tests.
- [Volumen de 33 bugs + sospechas] -> El orden por severidad y la dependencia explicita de c-29 evitan bloqueos; cada tarea es atomica.

## Migration Plan

1. `c-29-seam-tests` escribe los tests RED bloqueantes por severidad.
2. Aplicar fixes en el orden de D1, con el checkpoint de gobernanza en auth (CRITICA) y N8N/servicios (ALTA).
3. Re-ejecutar backend (`pytest`), frontend (`npm run test`), evaluacion (`pytest` en `evaluation/`) y validar `test_openapi_sync.py` si cambian contratos.
4. Rollback: revertir `n8n/workflow.json` y los archivos de codigo tocados; no hay migracion de datos ni cambio de esquema. Los specs no se ven afectados por el rollback.

## Open Questions

- Si el webhook del formulario debe esperar respuesta sincronica del backend o encolar. No cambia el enfoque; se resuelve con el test de costura del canal web.
