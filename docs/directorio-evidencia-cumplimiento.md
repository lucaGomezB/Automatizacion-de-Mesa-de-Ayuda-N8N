# Directorio — Evidencia de cumplimiento (c-60)

Documento de evidencia de las confirmaciones de la revision humana HIGH del
directorio (c-54 tarea 7.5, cerrada por c-60 seccion 7). Cubre la politica de
retencion/ARCO (DIR-007), la ausencia de PII real y de indice ciego
(DIR-005/DIR-009) y la regla de visibilidad por rol (VIS-001/VIS-002).

Este documento NO activa datos reales: la aprobacion humana HIGH sigue PENDIENTE
(ver seccion 4).

## 1. Politica de retencion y ARCO (DIR-007)

Politica CONFIRMADA por el autor (c-60 OQ3):

- La relacion laboral se CONSERVA mientras este activa mas 1 anio.
- La desactivacion NO es borrado: marca `activo=false` y sella `fecha_baja`
  (instante UTC). La reactivacion limpia `fecha_baja`.
- El borrado FISICO ocurre SOLO por vencimiento del plazo (`fecha_baja + 1 anio`)
  o por una solicitud ARCO de supresion; nunca es el camino operativo por defecto.
- El vencimiento se evalua como `fecha_baja + 1 anio` (funcion pura
  `retencion_vencida`, con ajuste de 29-feb a 28-feb).
- La purga por vencimiento es MANUAL y disparada por un operador
  (`administrador_directorio`) via API (`POST /api/v1/directorio/purga`) o script
  CLI (`python -m scripts.purgar_directorio`). NO existe cron, scheduler ni worker.
- La purga es IDEMPOTENTE: conserva activos y bajas recientes; una segunda corrida
  no vuelve a borrar.
- El registro de auditoria incluye el conteo y los **ids** de las filas eliminadas.
  Los ids son identificadores internos, NO datos personales; NUNCA se registran
  email, telefono ni nombre en claro.

Evidencia por tests:

- `tests/test_directorio_service.py` (retencion, ids auditados, idempotencia, sin PII).
- `tests/test_purgar_directorio_script.py` (script CLI reporta ids, idempotencia).
- `tests/test_api_directorio_purga.py` (admin 200, otro rol 403, anonimo 401).
- `tests/test_directorio_purga_no_automatica.py` (sin scheduler/cron).

## 2. Visibilidad de incidentes por rol y su alcance (VIS-001/VIS-002)

Regla del directorio, consistente con VIS-001/VIS-002:

| Rol                                | Alcance de incidentes                                              |
|------------------------------------|--------------------------------------------------------------------|
| `administrador_directorio` (ADMIN) | TODOS los incidentes, sin importar el sector.                      |
| `mesa_de_ayuda`                    | Solo incidentes SIN sector o que requieren revision humana.        |
| `usuario_final` / `operador` (sector S) | Solo incidentes del sector S.                                 |
| Cuenta sin empleado o sin sector   | Alcance VACIO (no ve incidentes por esta via).                     |

La cola `GET /api/v1/clasificaciones/revision-pendiente` aplica la MISMA regla:
administrador y `mesa_de_ayuda` ven la cola completa; un sector-bound ve solo los
pendientes de su sector; un alcance vacio ve una lista vacia; el acceso anonimo
es 401. El orden FIFO y la definicion de "pendiente" se preservan.

Exclusiones aplicadas en la API: un incidente fuera de alcance responde como NO
ENCONTRADO (HTTP 404), sin revelar existencia ni contenido. La representacion en el
frontend queda diferida.

## 3. Ausencia de PII real y de indice ciego (DIR-005/DIR-009)

- Contactos SINTETICOS: el seed dev-only usa el dominio reservado `.test`; no hay
  PII real en el repositorio ni en la base.
- SIN clave de indice ciego: no existe `directory_blind_index_key` ni una columna
  de hash ciega del directorio. Email y telefono se almacenan en TEXTO PLANO; la
  proteccion se logra con minimizacion, control de acceso por rol y auditoria.

Evidencia por test: `tests/test_directorio_cumplimiento.py` (settings sin clave de
indice ciego, migraciones/codigo sin indice ciego, tabla sin columnas de hash,
contactos del seed con dominio `.test`).

## 4. Revision humana HIGH — PENDIENTE de aprobacion (c-60 7.4)

Estado: **PENDIENTE**. La politica de retencion/ARCO quedo CONFIRMADA por el autor
(OQ3) y la regla de visibilidad por rol documentada (seccion 2), pero la
APROBACION HUMANA HIGH para ACTIVAR DATOS PERSONALES REALES sigue sin registrarse.

Consecuencias vinculantes:

- Activar datos reales en el directorio queda BLOQUEADO.
- La implementacion opera exclusivamente con datos SINTETICOS.
- La confirmacion de la politica NO habilita por si sola el uso de datos reales:
  es una aprobacion humana separada.

Esta tarea (7.4) NO se marca resuelta; su aprobacion queda explicitamente pendiente.
