# Actores y Roles

## Actores del sistema

| Actor | Descripción | Cómo interactúa |
|---|---|---|
| Usuario interno | Empleado (~120 en la organización) que reporta un incidente | Correo, formulario web (React) o llamada a número Twilio |
| Operador de mesa de ayuda | Personal técnico que supervisa la cola de revisión | Frontend → pestaña Administración → modal "Validación Humana" |
| Sector responsable | Sistemas / Operaciones / Soporte Técnico; atiende y puede corregir la derivación | `PATCH /clasificaciones/{id}/validar` |
| Responsable de protección de datos | Atiende solicitudes ARCO (acceso 10 días, rectificación/supresión 5 días) | Procedimiento documentado fuera del sistema |
| N8N (actor sistema) | Orquestador que normaliza canales e invoca la API | HTTP REST contra el módulo Python |
| Clasificador híbrido (actor sistema) | Decide el sector con confianza asociada | Interno: `HybridClassifier` en `app/classifiers/` |

## RBAC — Matriz de permisos

> ⚠️ **Estado actual: la API no implementa autenticación.** La tesis (§5.7) declara tokens portadores firmados validados contra clave compartida con N8N; el código no lo tiene aún. Gap registrado en [10_preguntas_abiertas.md](10_preguntas_abiertas.md) IN-02. La matriz siguiente es la **objetivo** según la tesis.

| Rol | Recurso | Permisos |
|---|---|---|
| Usuario interno | incidentes (propios) | Crear; consultar estado |
| Operador / Sector | incidentes | Leer todos; actualizar estado/sector |
| Operador / Sector | clasificaciones | Leer cola; validar (cierra ciclo de revisión) |
| N8N (token servicio) | incidentes, clasificar | Crear incidentes; invocar clasificación |
| Monitoreo externo | health | Solo lectura |

## Rutas públicas

Estado actual (sin auth — todas son de facto públicas en la red interna):

- `GET /health`, `GET /health/db` — diseñadas para monitoreo sin credenciales.
- Resto de `/api/v1/*` — **deberían** requerir token según la tesis; hoy abiertas. El frontend (localhost:3000) consume directo vía CORS.

## Supervisión humana (human in the loop)

Principio rector (§11.5 de la tesis): ninguna decisión automatizada es definitiva sin posibilidad de revisión humana. Materialización:

1. Confianza < 0,70 → `requiere_revision_humana = true` → entra a la cola FIFO.
2. El sector receptor puede corregir cualquier clasificación; la corrección queda en `clasificacion_log.sector_id_validado`.
3. Toda decisión (automática o humana) es trazable: etapa, confianza, respuesta cruda de Gemini, timestamps.
