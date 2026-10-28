# Actores y Roles

## Actores del sistema

| Actor | Descripción | Cómo interactúa |
|---|---|---|
| Usuario interno | Empleado (~120 en la organización) que reporta un incidente | Correo, formulario web (React) o llamada a número Twilio |
| Mesa de ayuda (función) | Personal técnico que atiende los incidentes y supervisa la cola de revisión | Frontend → pestaña Administración → modal "Validación Humana" |
| Sector responsable (función) | Seguridad Informatica / Soporte Tecnico Hardware / Soporte Tecnico Software / Bases de Datos / Sistemas; recibe y puede corregir la derivación de su sector | `PATCH /clasificaciones/{id}/validar` |
| Administrador del directorio (función) | Administra el padrón de empleados (alta, edición, baja, ARCO, purga) | API del directorio |
| Responsable de protección de datos | Atiende solicitudes ARCO (acceso 10 días, rectificación/supresión 5 días) | Procedimiento documentado fuera del sistema |
| N8N (actor sistema) | Orquestador que normaliza canales e invoca la API | HTTP REST contra el módulo Python |
| Clasificador híbrido (actor sistema) | Decide el sector con confianza asociada | Interno: `HybridClassifier` en `app/classifiers/` |

Estos actores describen FUNCIONES de la organización. No todos los actores de negocio son roles del sistema: el "sector responsable" es una función organizacional (el sector es la categoría de clasificación del incidente), NO un rol de autorización.

## Roles del sistema (RBAC implementado)

El sistema autentica con JWT Bearer (implementado desde C-15) y autoriza con EXACTAMENTE TRES roles. El vocabulario vive en `RolEmpleado` (`App/Backend/app/models/empleado.py`) y la política de cada rol se centraliza en `App/Backend/app/services/role_policy.py` (fuente única de verdad). El rol `operador` ya NO existe: su comportamiento GLOBAL lo absorbe `mesa_de_ayuda`.

| Rol del sistema | Alcance de incidentes | Privilegiado (exige MFA) | Directorio | Destinatario de notificación |
|---|---|---|---|---|
| `usuario_final` | PROPIO: solo los incidentes cuyo reportante vinculado es su empleado | No | No lee; no gestiona | No |
| `mesa_de_ayuda` | GLOBAL: todos los incidentes | Sí | Lee; no gestiona | Sí (todos los `mesa_de_ayuda` activos) |
| `administrador_directorio` | GLOBAL: todos los incidentes | Sí | Lee y gestiona (alta, edición, baja, ARCO, purga) | No |
| Cuenta sin empleado vinculado | VACIO: no ve ningún incidente | Según su cuenta | No lee | No |

Los modos de visibilidad son PROPIO, GLOBAL, SECTOR y VACIO (`ModoAlcance` en `App/Backend/app/services/role_policy.py:38`, resueltos en `App/Backend/app/services/incident_visibility.py`). El modo SECTOR corresponde al rol `gestion_incidentes` (c-86, VIS-007): ve solo los incidentes de su sector, que para ese rol SI es frontera de acceso. Para los roles con alcance PROPIO y GLOBAL el `sector_id` del empleado es dato organizacional opcional sin efecto en la autorización: el sector del incidente es solo una categoría de clasificación (uno de los cinco strings canónicos), no una frontera de acceso.

El alcance se resuelve en el backend (fuente única de verdad) y el frontend (c-81) lo refleja vía `GET /api/v1/auth/me`.

## RBAC — Matriz de permisos

| Rol | Recurso | Permisos |
|---|---|---|
| `usuario_final` | incidentes | Crear; leer/listar y actualizar solo los propios (PROPIO) |
| `usuario_final` | clasificaciones | Leer y validar solo las de sus propios incidentes |
| `mesa_de_ayuda` | incidentes | Leer/listar todos (GLOBAL); actualizar estado |
| `mesa_de_ayuda` | clasificaciones | Leer la cola global; validar (cierra el ciclo de revisión) |
| `mesa_de_ayuda` | directorio | Solo lectura |
| `administrador_directorio` | incidentes | Leer/listar todos (GLOBAL) |
| `administrador_directorio` | clasificaciones | Leer y validar |
| `administrador_directorio` | directorio | Gestión completa (alta, edición, baja, ARCO, purga) |
| N8N (actor sistema) | incidentes | Crear incidentes; invocar la clasificación |
| Monitoreo externo | health | Solo lectura |

Un incidente fuera del alcance responde como no encontrado (HTTP 404), sin revelar su existencia ni su contenido. El acceso anónimo a los endpoints autenticados responde 401.

## Vínculo de reportante y visibilidad PROPIO

El incidente guarda un `reportante_empleado_id` (FK nullable a `directorio_empleado`). Ese vínculo es la base del alcance PROPIO del rol `usuario_final`: un incidente sin reportante NO es visible para ningún `usuario_final`. Los roles GLOBAL (`mesa_de_ayuda`, `administrador_directorio`) ven todos los incidentes, con o sin reportante. La resolución del reportante se hace por canal: en el formulario web desde la cuenta autenticada; en correo y telefonía desde el contacto del remitente o llamante (nunca lo tipea el usuario). Cuando el reportante no se puede identificar, el incidente se persiste con vínculo nulo y ADEMÁS se deriva a revisión humana (`requiere_revision_humana = true`, regla VIS-005), sin bloquear el alta.

## Rutas públicas

- `GET /health`, `GET /health/db` — diseñadas para monitoreo sin credenciales.
- `POST /api/v1/auth/login` y `/refresh` — públicas por diseño; emiten y rotan el token.
- Resto de `/api/v1/*` — requieren JWT Bearer válido. El frontend (localhost:3000) consume directo vía CORS enviando el token.

## Supervisión humana (human in the loop)

Principio rector (§11.5 de la tesis): ninguna decisión automatizada es definitiva sin posibilidad de revisión humana. Materialización:

1. Gemini con confianza < 0,70 o etapa fallback → `requiere_revision_humana = true` → entra a la cola FIFO. También se deriva a revisión cuando el reportante no se pudo identificar (VIS-005). La etapa determinística no deriva por su confianza.
2. La validación humana puede confirmar o corregir cualquier clasificación (no solo las de baja confianza): `mesa_de_ayuda` sobre cualquier incidente (GLOBAL) y `usuario_final` sobre los propios. La corrección queda en `clasificacion_log.sector_id_validado` y, para casos multietiqueta, en el conjunto validado (`clasificacion_sector_validado`).
3. La notificación de revisión se dirige a TODOS los `mesa_de_ayuda` activos, sin acotar por sector.
4. Toda decisión (automática o humana) es trazable: etapa, confianza, respuesta cruda de Gemini, timestamps.
