# Directorio — Evidencia de cumplimiento (c-60; endurecimiento c-153)

Documento de evidencia de las confirmaciones de la revision humana HIGH del
directorio (c-54 tarea 7.5, cerrada por c-60 seccion 7; endurecida por c-153
seccion 7). Cubre la politica de retencion/ARCO (DIR-007/DIR-015), el cifrado
at-rest del contacto con indice ciego determinista (DIR-011/DIR-016), la ausencia
de PII real (DIR-009), la auditoria durable sin PII (DIR-013) y el mecanismo
deliberado y auditado de activacion de datos reales (DIR-014), ademas de la
visibilidad por rol (VIS-001/VIS-002).

Este documento registra el estado de la revision humana HIGH. La aprobacion del
autor para el endurecimiento fue **CONCEDIDA el 2026-10-28** (ver seccion 4); la
activacion de datos reales, en cambio, sigue gobernada por el mecanismo
deliberado y auditado (DIR-014) y no se habilita por este documento.

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

## 3. Cifrado del contacto y ausencia de PII real (DIR-011/DIR-009)

- Contactos SINTETICOS: el seed dev-only usa el dominio reservado `.test`; no hay
  PII real en el repositorio ni en la base.
- Cifrado at-rest: `directorio_empleado.email` y `directorio_empleado.telefono` se
  almacenan CIFRADOS con el TypeDecorator `EncryptedText` (Fernet); el contacto NO
  se persiste en claro (DIR-011). La garantia original de texto plano
  (DIR-005/DIR-010) queda SUPERADA por el ADR
  `docs/seguridad/adr-001-reversion-dir-005-cifrado-contacto.md`.
- Indice ciego: el directorio usa la clave DEDICADA `directory_blind_index_key` y
  las columnas derivadas `email_bidx`/`telefono_bidx` (HMAC-SHA-256 de la forma
  normalizada). La garantia original de ausencia de indice ciego (DIR-005) queda
  SUPERADA (DIR-011).

Evidencia por test: `tests/test_directorio_cumplimiento.py` (presencia de la clave
de indice ciego, columnas derivadas, codigo/migraciones con indice ciego, contactos
del seed con dominio `.test`), `tests/test_c153_directorio_cifrado.py` (el contacto
se lee como ciphertext en la fila cruda) y `tests/test_c153_directorio_indice_ciego.py`
(determinismo, dependencia de clave y busqueda por indice).

## 4. Revision humana HIGH — aprobacion CONCEDIDA (2026-10-28)

Estado ANTERIOR (historico, c-60 7.4): la aprobacion humana HIGH figuraba
**PENDIENTE** y activar datos reales estaba **BLOQUEADO**; la implementacion
operaba solo con datos **SINTETICOS**.

Estado ACTUAL: la **APROBACION HUMANA HIGH** para endurecer el directorio y
habilitar el tratamiento de **DATOS REALES** fue **CONCEDIDA** por el autor el
**2026-10-28**, en el marco del change `c-153-endurecer-el-directorio-para-datos-reales`.
Este registro es la evidencia verificable de la aprobacion (DIR-009), previa a
toda tarea de implementacion desde el grupo 2 en adelante.

Alcance de la aprobacion concedida:

- Habilita la IMPLEMENTACION del endurecimiento (cifrado at-rest, indice ciego,
  auditoria durable, control de acceso por sujeto, retencion/ARCO), que es lo que
  `c-153` ejecuta por etapas.
- **NO** equivale a activar datos reales por si misma: mientras no exista el
  mecanismo deliberado y auditado de activacion (DIR-014) con su artefacto de
  aprobacion, el directorio continua operando solo con datos SINTETICOS.

La tarea 7.4 (registrar la aprobacion) se mantiene cerrada; la aprobacion HIGH
dejo de estar PENDIENTE al concederse el 2026-10-28.

### 4.1 Mecanismo de activacion de datos reales (DIR-014)

La compuerta historica "sin mecanismo de activacion" queda REEMPLAZADA por el
mecanismo DELIBERADO y AUDITADO que exige DIR-014:

- Implementacion: `App/Backend/app/services/directorio_activacion.py` y el CLI
  env-gateado `App/Backend/scripts/activar_directorio.py`.
- Gobierno: gate de entorno `DIRECTORY_ACTIVATION_APPROVAL_ARTIFACT` mas la
  verificacion de este artefacto de aprobacion (seccion 4, estado `CONCEDIDA` con
  fecha verificable).
- Bloqueado por defecto: sin aprobacion verificable NO hay activacion y el
  directorio permanece en modo SINTETICO.
- Con la aprobacion registrada, la activacion deja constancia en la traza durable
  `directorio_auditoria` (`activacion_datos_reales` / `ok`), sin PII.
- NO existe un interruptor de runtime oculto: ni un flag booleano de `Settings` ni
  un endpoint HTTP. La unica via es el mecanismo deliberado.

Evidencia por test: `tests/test_c153_directorio_activacion.py` (sin aprobacion no
hay activacion; con aprobacion queda auditada; sin interruptor oculto).
