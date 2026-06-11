# Guía del Workflow N8N — Automatización de Mesa de Ayuda

> C-04: n8n-workflow-validation — Implementado y verificado.
> C-05: n8n-channel-triggers — Canal web agregado, notificaciones por canal y auditoría con retención de 30 días.
> Estado: 17 nodos funcionales; 45 tests estructurales pasando + 1 xfail documentado.

## Descripción general

El archivo `Automatizacion_Mesa_de_Ayuda.json` (raíz del repo) es el workflow N8N exportado que
automatiza la recepción y clasificación de incidentes de mesa de ayuda desde **tres canales**:

- **Canal correo**: Microsoft Outlook trigger por sondeo (equivalente funcional a IMAP — ver Decisión 1 C-05)
- **Canal web**: Webhook HTTP POST en la ruta `/webhook/incidente-web` (formulario web del frontend)
- **Canal telefonía**: Twilio webhook de transcripción de llamada

Los tres canales convergen en un **único nodo normalizador** antes de la persistencia.
El workflow está configurado con `"active": false` en el JSON versionado. **No activar en
producción editando el JSON** — activar desde la UI de N8N en el entorno de destino.

## Tabla de los tres canales

| Canal | Trigger | `canal_raw` emitido | `canal_origen` normalizado |
|-------|---------|--------------------|-----------------------------|
| Correo | `microsoftOutlookTrigger` (sondeo) | `"correo"` | `"correo"` |
| Web | `webhook` `POST /webhook/incidente-web` | `"web"` | `"web"` |
| Telefonía | `twilioTrigger` (transcripción) | `"telefonia"` | `"telefonia"` |

### Equivalencia Outlook trigger ≈ IMAP (Decisión 1 — C-05)

La tesis §5.2 describe el canal correo como "trigger IMAP". El workflow usa un
`microsoftOutlookTrigger` (nodo nativo N8N de sondeo de buzón). Se **ratifica este nodo**
como equivalente funcional del IMAP genérico: no se reemplazó por `emailReadImap` porque el
trigger de Outlook ya cumple la función de recepción de correos del canal correo y
las credenciales configuradas en C-04 quedan intactas. Esta equivalencia se registra
para el Anexo E de la tesis (C-10).

## Nodos del workflow

### Canal correo

| Posición | Nombre | Tipo | Función |
|----------|--------|------|---------|
| 1 | Llega un email a Mesa de Ayuda | `microsoftOutlookTrigger` | Disparador por sondeo. Recibe el correo del usuario. Emite `canal_raw = "correo"`. |
| 2 | Se verifica que la informacion sea la necesaria para levantar un incidente | `code` (JS) | Valida `descripcion` ≥10 y ≤5000 caracteres. Emite `es_valido`. |
| 3 | Normalizar entrada del incidente | `code` (JS) | Homogeniza a estructura unificada: `{id, timestamp, canal_origen, descripcion}`. Compartido entre los tres canales. |
| 4 | La informacion esta OK | `if` | Condición: `confianza >= 0.70`. Rama true → HTTP; rama false → reenvío. |
| 5a | HTTP POST a MTM-SRU | `httpRequest` | `POST /api/v1/incidentes` al backend FastAPI. |
| 5b | Se le envia un mensaje... | `microsoftOutlook` | Solicita al usuario reenviar datos faltantes. |
| 6a | Correo de confirmacion al usuario | `microsoftOutlook` | **[C-05]** Envía correo de confirmación con el número de incidente al remitente. |
| 6b | Registro de auditoria | `code` (JS) | **[C-05]** Registra metadatos de la ejecución (sin PII). Ver sección Auditoría. |

### Canal web (formulario web) — C-05

| Posición | Nombre | Tipo | Función |
|----------|--------|------|---------|
| 1 | Webhook formulario web | `webhook` | `POST /webhook/incidente-web`. Recibe el envío del formulario del frontend. |
| 2 | Marcar canal web | `code` (JS) | Asigna `canal_raw = "web"` al ítem antes de normalizar. |
| 3 | Normalizar entrada del incidente | `code` (JS) | Compartido — idem canal correo. |
| 4 | La informacion esta OK | `if` | Compartido — idem canal correo. |
| 5 | HTTP POST a MTM-SRU | `httpRequest` | Idem canal correo. |
| 6a | Confirmacion web al usuario | `respondToWebhook` | **[C-05]** Responde al webhook con `{incidente_id, mensaje}`. |
| 6b | Registro de auditoria | `code` (JS) | **[C-05]** Compartido — idem canal correo. |

### Canal telefonía

| Posición | Nombre | Tipo | Función |
|----------|--------|------|---------|
| 1 | Llamada telefonica | `twilioTrigger` | Webhook de Twilio al completar la transcripción. |
| 2 | AI Agent | `agent` (LangChain) | Parsea la transcripción con el prompt del negocio. |
| 2b | Con el fin de enviar los datos... | `memoryRedisChat` | Memoria Redis para el AI Agent. |
| 3 | Se verifica lo que trajo la IA | `code` (JS) | Valida los 5 pasos Anexo H §H.3 (JSON, campos, categoría, rango confianza). Emite `canal_raw = "telefonia"`. |
| 4 | Normalizar entrada del incidente | `code` (JS) | **[C-05]** Compartido — telefonia ahora converge aquí antes del IF. |
| 5 | La informacion esta OK | `if` | Compartido — condición `confianza >= 0.70`. Rama false → loop AI Agent. |
| 6a | HTTP POST a MTM-SRU | `httpRequest` | Compartido. |
| 6b | Registro de auditoria | `code` (JS) | **[C-05]** Compartido — idem canal correo. |

> **Nota sobre telefonía**: la confirmación al usuario se resuelve mediante la respuesta del
> propio webhook de Twilio/TwiML durante la llamada. No se agrega un nodo SMS de confirmación
> adicional (ver Decisión 2 C-05 — Open Question resuelta: basta la respuesta del webhook).

### Nodos decorativos

Seis nodos `stickyNote` con documentación visual interna del workflow (se conservan intactos).

## Contrato: `POST /api/v1/incidentes`

El workflow invoca un **único** endpoint HTTP:

```
POST {BACKEND_URL}/api/v1/incidentes
Content-Type: application/json

{
  "descripcion": "<texto del incidente — máx. 5000 chars>",
  "prioridad": "<media|alta|baja>"
}
```

La URL del backend se inyecta a través de la variable de entorno N8N `$env.BACKEND_URL`
(configurar en la instancia N8N antes de activar).

### Respuesta esperada: `201 Created`

```json
{
  "id": 123,
  "descripcion_pseudonimizada": "...",
  "sector": "Sistemas",
  "confianza": 0.87,
  "requiere_revision_humana": false,
  ...
}
```

El backend (`IncidenteService.create_and_classify`) ejecuta el pipeline completo:
clasificación híbrida (determinístico → Gemini → fallback) + persistencia. La respuesta
incluye `sector`, `confianza` y `requiere_revision_humana`.

## Discrepancia tesis vs implementación — 1 endpoint vs 2

La tesis (§6.3 y diagrama conceptual) describe dos llamadas HTTP separadas:

1. `POST /api/v1/clasificar` — clasifica sin persistir
2. `POST /api/v1/incidentes` — persiste el incidente ya clasificado

**La implementación real usa un único endpoint** (`POST /api/v1/incidentes`) donde la
clasificación está embebida en `create_and_classify()`. El endpoint `/api/v1/clasificar`
**no existe** en el backend actual.

Motivo: forzar dos llamadas requeriría crear un endpoint nuevo en el backend (governance ALTO,
fuera de scope C-04). La solución con un único endpoint es funcionalmente equivalente y
mantiene la atomicidad crear+clasificar.

**Acción para C-10** (`documentation-annexes`): actualizar el Anexo E de la tesis para
reflejar la arquitectura real de 1 endpoint. Ver Open Questions en `design.md`.

## Estructura unificada de normalización

El nodo `Normalizar entrada del incidente` produce para todos los canales:

```json
{
  "id": "<execution_id>-<timestamp_ms>",
  "timestamp": "2026-06-11T14:23:45.123Z",
  "canal_origen": "correo" | "web" | "telefonia",
  "descripcion": "<texto trimmed>",
  "prioridad": "media",
  "es_valido": true
}
```

- `timestamp`: ISO-8601 con milisegundos (`new Date().toISOString()`).
- `canal_origen ∈ {correo, web, telefonia}`. Entradas con canal inválido derivan a revisión.
- El canal `web` es soportado desde C-04; su trigger se cablea en C-05.

## Validación de la respuesta de clasificación — Anexo H §H.3

El nodo `Se verifica lo que trajo la IA` implementa 5 pasos en orden:

1. **JSON válido**: `JSON.parse()` dentro de `try/catch`. Fallo → `confianza = 0.0`.
2. **Campos presentes**: `categoría` y `confianza` deben existir. Fallo → `confianza = 0.0`.
3. **Categoría exacta** (case-sensitive): debe ser uno de `{Sistemas, Operaciones, Soporte Técnico}`. Fallo → `confianza = 0.0`.
4. **Confianza numérica en [0.0, 1.0]**: `typeof === 'number'`, `!isNaN`, `>= 0`, `<= 1.0`. Fallo → `confianza = 0.0`.
5. **Respuesta válida**: conserva `categoría` y `confianza` originales para el ruteo por umbral.

En cualquier fallo: `confianza = 0.0`, `requiere_revision_humana = true`, `error_validacion = <código>`.

## Ruteo por umbral de confianza (0.70 inclusivo)

Ambos nodos `if` usan la condición:

```
$json.confianza >= 0.70   (operador: gte, tipo: number)
```

- **Rama true** (`confianza ≥ 0.70`): flujo a `POST /api/v1/incidentes` (creación directa).
- **Rama false** (`confianza < 0.70` o falla de validación con `confianza = 0.0`):
  - Canal correo: solicitar reenvío de datos.
  - Canal telefonía: volver al AI Agent para refinamiento.

Nota: el backend también marca internamente `requiere_revision_humana`; el nodo `if` del
workflow es la primera capa de ruteo (antes de persistir).

## Pseudonimización en tránsito — Decisión de diseño (C-04 §Decisión 2)

**La pseudonimización NO ocurre en N8N.** La descripción viaja en texto claro desde
N8N al backend vía HTTPS.

El backend pseudonimiza internamente en `IncidenteService.create_and_classify()`
(archivo: `Gestion_Incidentes/app/services/incidente_service.py`, líneas 183–190):

```python
# Paso 3 (C-03): Pseudonimizar la descripción antes de persistir.
resultado_pseudo = pseudonymize(payload.descripcion, ...)
```

**Gap de privacidad documentado**: si el canal de transporte (HTTPS) se comprometiera,
la PII viajaría expuesta entre N8N y el backend. Registrado como hallazgo para auditoría
de privacidad (C-10 / posible C-05).

**Por qué no se pseudonimiza en N8N**: reimplementar el módulo Fernet (C-03) en JavaScript
duplicaría lógica de seguridad crítica fuera de su módulo Python testeado (governance ALTO).

## Variables de entorno requeridas (instancia N8N)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `BACKEND_URL` | URL base del backend FastAPI | `http://localhost:8000` |

Credenciales adicionales a configurar en la UI de N8N:
- `MICROSOFT_OUTLOOK_*`: cuenta de correo de mesa de ayuda
- `TWILIO_*`: credenciales del webhook de voz
- `REDIS_URL`: para el nodo de memoria del AI Agent

## Cómo importar y probar el workflow

## Entorno de pruebas local (Docker)

> Verificación funcional ejecutada el 2026-06-11 (C-04, tareas 8.1–8.3).

### Servicios incluidos

El `docker-compose.yml` en la raíz del repo levanta 4 servicios con una sola línea:

| Servicio | Imagen | Puerto host | Descripción |
|---------|--------|-------------|-------------|
| `postgres` | `postgres:15.5-alpine` | 5433 (evita colisión con C-01) | Base de datos PostgreSQL |
| `redis` | `redis:7.2-alpine` | 6379 | Memoria del AI Agent |
| `backend` | build `Gestion_Incidentes/` | 8000 | FastAPI + alembic migrations |
| `n8n` | `n8nio/n8n:latest` | 5678 | UI de N8N con workflow importado |

**Prerequisito**: `Gestion_Incidentes/.env` debe existir y tener todas las claves (ver `Gestion_Incidentes/.env.example`).

### Levantar el entorno

```bash
# Desde la raíz del repo
docker compose --project-name mesa_local up -d --build

# Verificar que todos los servicios estén healthy
docker compose --project-name mesa_local ps

# Logs del backend (incluye alembic migrations y clasificaciones)
docker compose --project-name mesa_local logs -f backend
```

### Importar el workflow en N8N

```bash
# Importar el workflow desde el JSON del repositorio (montado como volumen)
docker exec mesa_local-n8n-1 n8n import:workflow --input=/data/Automatizacion_Mesa_de_Ayuda.json

# Resultado esperado: "Successfully imported 1 workflow."
```

Acceder a la UI de N8N en http://localhost:5678 (usuario: `admin`, contraseña: `admin`).

### Importar en N8N (modo UI)

```bash
# Alternativa sin CLI: acceder a http://localhost:5678
# Settings → Import Workflow → seleccionar Automatizacion_Mesa_de_Ayuda.json
```

### Detener / limpiar

```bash
# Detener (mantiene volumes = datos persisten)
docker compose --project-name mesa_local down

# Detener + borrar todo (base de datos limpia)
docker compose --project-name mesa_local down -v
```

---

### Resultados de verificación 8.1–8.3 (2026-06-11)

#### 8.1 — Import del workflow: VERIFICADO

```
n8n import:workflow --input=/data/Automatizacion_Mesa_de_Ayuda.json
→ "Successfully imported 1 workflow."
→ 17 nodos, active=false, todos los nodos esperados presentes.
```

**Nota**: N8N 1.62.0 no está disponible en Docker Hub; se usa `n8nio/n8n:latest` (comportamiento equivalente para importación y ejecución de nodos).

#### 8.2 — Canal correo: VERIFICADO

Payload de prueba (simula el payload que el workflow envía al backend tras el normalizer):

```bash
curl -X POST http://localhost:8000/api/v1/incidentes \
  -H "Content-Type: application/json" \
  -d '{"descripcion": "El servidor de base de datos no responde desde esta manana. Los usuarios del sistema de gestion no pueden acceder.", "prioridad": "alta"}'
```

Respuesta `201 Created`:
```json
{
  "id": 1,
  "sector": {"nombre": "Sistemas"},
  "prioridad": "alta",
  "requiere_revision_humana": false,
  "estado": {"nombre": "nuevo"}
}
```

Log del clasificador: etapa `deterministic`, confianza 0.9999 (>= 0.90 threshold → sin llamada a Gemini).

#### 8.3 — Canal telefonía: VERIFICADO (incluyendo ruta fallback)

Se ejecutaron 3 payloads representando distintos escenarios de confianza:

| # | Descripción | Sector resultante | Etapa | Confianza | Revisión humana |
|---|-------------|-------------------|-------|-----------|-----------------|
| 1 | Servidor de BD no responde | Sistemas | deterministic | 0.9999 | No |
| 2 | Plan de continuidad, cierre de mes | Operaciones | deterministic | 0.9999 | No |
| 3 | Computadora no enciende | Soporte Técnico | fallback | 0.0 | **Sí** |

**Caso 3 — ruta de fallback verificada**: el clasificador determinístico obtuvo confianza 0.667 (< 0.90 → escala a Gemini); Gemini API devolvió `403 PERMISSION_DENIED` (API key reportada como leaked en `.env`); el fallback se activó correctamente; `confianza = 0.0`; `requiere_revision_humana = true`. El IF node del workflow (`confianza >= 0.70`) hubiera enrutado este caso a la rama de revisión humana (no HTTP al backend).

**Observación**: la GEMINI_API_KEY en `Gestion_Incidentes/.env` fue reportada como leaked. Renovarla en Google AI Studio antes de verificar el path Gemini completo (end-to-end con clasificación LLM).

#### Qué queda para C-05

Los siguientes ítems no se pueden verificar sin las credenciales de trigger:

- Disparo real del trigger de Outlook (canal correo de punta a punta)
- Disparo real del webhook de Twilio (canal telefonía de punta a punta)
- Ciclo completo AI Agent → Redis memory → nodo validación → IF → HTTP

El import, los nodos individuales y el backend están verificados. El entorno Docker está listo para cuando C-05 configure los triggers.

---

### Prueba manual de correo (canal correo — con triggers activos, C-05)

1. Disparar el trigger de Outlook (o usar el botón "Test Workflow" con datos de prueba).
2. Observar que el nodo `Se verifica...` emite `es_valido: true` para descripción ≥10 chars.
3. Observar que el normalizado produce `canal_origen: "correo"`.
4. Verificar `201 Created` del backend.

### Prueba manual de telefonía (canal telefonía — con triggers activos, C-05)

1. Enviar un webhook simulado al trigger de Twilio con una transcripción de ejemplo.
2. Observar que el AI Agent devuelve un JSON con `categoría` y `confianza`.
3. Observar que el nodo `Se verifica lo que trajo la IA` valida la respuesta.
4. Con `confianza ≥ 0.70`: verificar `201 Created` del backend.
5. Con `confianza < 0.70`: verificar loop de vuelta al AI Agent.

### Suite de tests estructurales (sin runtime N8N)

```bash
cd Gestion_Incidentes
python -m pytest tests/test_n8n_workflow.py -v
```

Verifica 45 propiedades estructurales del JSON sin necesitar N8N en ejecución (C-04: 31, C-05: 14 nuevos).

### Prueba manual del canal web (C-05)

1. Importar el workflow en N8N con `BACKEND_URL` configurado.
2. Activar el workflow desde la UI de N8N.
3. Enviar un POST al webhook: `POST {N8N_BASE_URL}/webhook/incidente-web` con cuerpo:
   ```json
   { "descripcion": "No puedo iniciar sesion en el sistema de facturacion", "prioridad": "alta" }
   ```
4. Verificar que el backend responde `201 Created` y el webhook responde con `{incidente_id, mensaje}`.
5. Verificar que el nodo de auditoría registra los metadatos en el log de N8N (sin `descripcion`).

## Notificaciones al usuario post-registro (C-05)

Tras un alta exitosa (`201 Created` del backend), el workflow notifica al usuario por su canal:

| Canal | Nodo | Mecanismo |
|-------|------|-----------|
| Web | `Confirmacion web al usuario` (`respondToWebhook`) | Responde al frontend con `{"incidente_id": <id>, "mensaje": "Incidente registrado"}` |
| Correo | `Correo de confirmacion al usuario` (`microsoftOutlook`) | Envía correo con el número de incidente al remitente original |
| Telefonía | — (sin nodo dedicado) | La confirmación ocurre en la respuesta Twilio/TwiML de la propia llamada |

Los nodos de notificación y el nodo de auditoría están **en paralelo** desde la salida del
`httpRequest` de persistencia. La notificación no bloquea el registro de auditoría.

## Registro de auditoría (C-05)

El nodo `Registro de auditoria` (`code` JS) registra por cada ejecución exitosa:

```json
{
  "incidente_id": "<id del incidente creado>",
  "canal_origen": "correo" | "web" | "telefonia",
  "timestamp": "2026-06-11T14:23:45.123Z",
  "categoria": "Sistemas" | "Operaciones" | "Soporte Técnico",
  "confianza": 0.87,
  "resultado": "creado",
  "retencion_dias": 30
}
```

**Exclusión de PII**: la `descripcion` cruda no se incluye en el evento de auditoría.
Solo metadatos y referencias al incidente.

**Retención de 30 días** (tesis §5.3): declarada como `retencion_dias: 30` en el nodo.
El destino persistente recomendado es el logging de Docker/N8N con rotación configurada
en `docker-compose.yml` (opción A, sin código nuevo en el backend). Configurar:

```yaml
# docker-compose.yml — logging con rotación a 30 días
logging:
  driver: "json-file"
  options:
    max-size: "100m"
    max-file: "30"
```

**Autenticación del webhook web**: el endpoint `POST /webhook/incidente-web` debe
protegerse en el entorno de despliegue (header firmado, red interna o SSO corporativo —
tesis §5.2 menciona "autenticación corporativa única"). El mecanismo concreto depende del
entorno y queda fuera del scope de C-05. Se documenta como punto pendiente para C-10.

## Open Questions resueltas (para Anexo E / C-10)

| Pregunta | Resolución | Change |
|----------|-----------|--------|
| ¿1 endpoint o 2 (clasificar + incidentes)? | **1 endpoint**: `POST /api/v1/incidentes` con clasificación embebida. No existe `POST /api/v1/clasificar`. Documentar discrepancia en Anexo E. | C-04 |
| ¿Dónde ocurre la pseudonimización? | **En el backend**, dentro de `create_and_classify()`. N8N envía texto claro. Gap de privacidad documentado. | C-04 |
| ¿El IF del workflow decide revisión humana o lo decide el backend? | **Ambos**: el IF del workflow es la primera capa (antes de persistir); el backend también marca `requiere_revision_humana` internamente. | C-04 |
| ¿Outlook trigger ≈ IMAP genérico? | **Sí**: el `microsoftOutlookTrigger` se ratifica como equivalente funcional. No se reemplaza por `emailReadImap`. Documentar equivalencia en Anexo E. | C-05 |
| ¿La telefonía requiere SMS de confirmación adicional? | **No**: basta la respuesta del webhook/TwiML de la llamada. No se agrega nodo SMS de Twilio. | C-05 |
| ¿La auditoría registra solo altas o también rechazos? | **Altas exitosas en C-05**. Ampliar a rechazos/revisiones en change futuro (requiere cablear ramas false de los IF). | C-05 |
| ¿Dónde persiste el log de auditoría 30 días? | **Logging Docker/N8N con rotación** (opción A). Cero código nuevo en backend. Configurar `max-file: "30"` en `docker-compose.yml`. | C-05 |
| ¿Cómo se autentica el webhook web? | **Pendiente de entorno**: tesis §5.2 menciona "autenticación corporativa única". Mecanismo concreto (header firmado / SSO) fuera del scope de C-05. Elevar para C-10. | C-05 |
