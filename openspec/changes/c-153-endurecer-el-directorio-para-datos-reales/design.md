## Context

Ver `proposal.md` (Why) para la motivacion. Estado y restricciones que condicionan el diseno (verificados 2026-10-28 por la revision de seguridad):

- El directorio (`App/Backend/app/models/empleado.py`) almacena `email` (`varchar`, UNIQUE, indexado) y `telefono` (`varchar`, indexado, repetible) en TEXTO PLANO (D4/DIR-005). El repositorio (`empleado_repository.py`) resuelve contactos por igualdad exacta sobre esas columnas en claro.
- La auditoria del directorio vive SOLO en structlog (`directorio_service.py:_auditar`, `purgar_vencidos`); no hay traza durable. El contraste disponible es `incidente_evento` (`App/Backend/app/models/incidente.py:310`), append-only y sin PII.
- `EncryptedText` (`App/Backend/app/utils/encryption.py`) es Fernet con `MultiFernet([activa, anterior?])` y clave `pseudonymization_encryption_key`. Fernet usa un IV aleatorio por operacion, de modo que el ciphertext NO es determinista: no sirve para buscar por igualdad sobre la columna cifrada.
- `role_policy.py` es el registro unico de politica de rol; ya expone `manages_directory` y `can_read_directory`. NO existe una politica explicita de acceso por sujeto (si `usuario_final` lee su propia fila) ni anti-enumeracion.
- La rotacion Fernet (`scripts/rotate_fernet_key.py`) usa un INVENTARIO explicito de columnas `EncryptedText` y exige respaldo previo; un test verifica que el inventario cubre exactamente las columnas cifradas del modelo.
- La compuerta actual es "sin mecanismo de activacion": DIR-005 prohibe cifrado e indice ciego y DIR-009 bloquea datos reales; la aprobacion humana HIGH esta PENDIENTE (`docs/directorio-evidencia-cumplimiento.md` seccion 4).
- La justificacion por minimizacion vigente (`docs/seguridad/justificacion-minimizacion-directorio.md`) registra el cifrado y el indice ciego como alternativas DESCARTADAS; este change las ADOPTA, por lo que la decision previa debe relativizarse. El procedimiento ARCO (`docs/seguridad/procedimiento-arco.md`) cubre acceso/rectificacion/actualizacion/supresion, pero la implementacion del directorio documentada hasta hoy enfatiza la supresion.
- Governance HIGH: datos personales bajo Ley 25.326; activar datos reales requiere aprobacion humana HIGH. Este change es SOLO de planificacion.

### Referencias de lectura (Leer antes)

- `openspec/specs/employee-directory/spec.md` (DIR-001..DIR-010 y fidelidad de gobernanza).
- `docs/directorio-evidencia-cumplimiento.md` (seccion 4: aprobacion HIGH pendiente).
- `docs/seguridad/justificacion-minimizacion-directorio.md` y `docs/seguridad/procedimiento-arco.md`.
- `docs/seguridad/gestion-secretos-y-rotacion.md` (inventario de columnas cifradas y runbook Fernet).
- `App/Backend/app/models/incidente.py` (`IncidenteEvento` como patron de auditoria durable sin PII).
- `CHANGES.md` y `openspec/config.yaml` (formato e indexacion).

## Goals / Non-Goals

**Goals:**

- Poder almacenar y resolver el contacto del directorio de forma segura cuando se habilite PII real: cifrado at-rest mas indice ciego determinista.
- Preservar la operacion del directorio (resolucion por igualdad, unicidad de email, telefono repetible) pese al cifrado.
- Formalizar el acceso de lectura por sujeto y la anti-enumeracion, y re-verificar el aislamiento entre sectores.
- Reemplazar la auditoria efimera por una traza durable append-only sin PII.
- Sustituir la compuerta "sin activacion" por un mecanismo deliberado y auditado, con aprobacion humana HIGH registrada.
- Cerrar los huecos operativos de retencion/ARCO (alerta de acumulacion, ARCO de acceso y rectificacion, retencion de auditoria).

**Non-Goals:**

- Activar datos reales: queda BLOQUEADO hasta la aprobacion humana HIGH; este change no la concede.
- Implementar codigo: este change produce solo artefactos de planificacion.
- Cifrado homomorfico, TDE/PGCrypto a nivel de motor, o busqueda por rango/orden sobre el contacto (fuera de alcance).
- SIEM, centralizacion de logs o deteccion de anomalias.
- Cambiar las cinco cadenas canonicas de sector, los valores de Gemini, `requirements.txt` o `config.yaml`.
- Reescribir el contenido historico de la justificacion por minimizacion: se conserva y se marca como SUPERADA.

## Decisions

### D1 — Revertir DIR-005 via ADR y cifrar el contacto con EncryptedText

Se crea un ADR nuevo en `docs/seguridad/` que revierte la decision de texto plano; el email y el telefono pasan a `EncryptedText` (Fernet). La justificacion por minimizacion previa se conserva como registro historico marcado como SUPERADA.

- **Alternativa A (descartada): mantener el texto plano.** Bloquea habilitar datos reales con PII en reposo; es la decision que este change viene a revertir.
- **Alternativa B (descartada): cifrado por campo en la capa de aplicacion con clave ad hoc.** Duplica el mecanismo ya existente (`EncryptedText`) y su custodia.
- **Alternativa C (descartada): TDE/pgcrypto del motor.** Depende del despliegue, acopla el cifrado a PostgreSQL y no cubre el modelo de claves de la aplicacion.
- **Elegida: `EncryptedText` (Fernet), el mismo primitivo ya auditado del incidente.**

### D2 — Indice ciego determinista para la busqueda (HMAC-SHA-256 con clave dedicada)

Como Fernet no es determinista, se agregan columnas `email_bidx` y `telefono_bidx` con HMAC-SHA-256 de la forma normalizada del contacto, usando una clave dedicada `directory_blind_index_key`. El repositorio busca por el indice; la unicidad del email se preserva sobre `email_bidx`.

- **Alternativa A (descartada): igualdad sobre la columna cifrada.** Fernet produce ciphertext distinto por IV: la igualdad siempre falla.
- **Alternativa B (descartada): hash sin clave (SHA-256 puro).** El espacio email/telefono es enumerable; un hash sin clave es vulnerable a diccionario y no es no reversible.
- **Alternativa C (descartada): descifrar toda la tabla y filtrar en memoria.** Impracticable y filtra PII al proceso sin necesidad.
- **Elegida: HMAC-SHA-256 con clave dedicada.** Deterministico (busqueda por igualdad), no reversible sin la clave, y desacoplado de la clave de cifrado.

Longitud: se usa el digest completo en hexadecimal para minimizar colisiones (la longitud no afecta la garantia de igualdad; solo reduce el riesgo de falso positivo de unicidad).

### D3 — Claves dedicadas del directorio, independientes de la de pseudonimizacion

Se introducen una clave de cifrado del directorio y una clave de indice ciego dedicadas, separadas de `pseudonymization_encryption_key`.

- **Alternativa A (descartada): reutilizar la clave de pseudonimizacion.** Reutiliza material de clave entre propositos y acopla la rotacion del directorio a la del incidente.
- **Alternativa B (descartada): una unica clave combinada para cifrado e indice.** Mezcla dos primitivas (Fernet y HMAC) y una sola clave no debe servir a ambas.
- **Elegida: claves dedicadas.** Rotacion y custodia desacopladas; la rotacion Fernet del directorio se cablea en `scripts/rotate_fernet_key.py` (inventario) y en `docs/seguridad/gestion-secretos-y-rotacion.md`.

### D4 — Auditoria durable sin PII, analoga a incidente_evento

Se agrega una tabla append-only de auditoria del directorio, siguiendo el patron de `IncidenteEvento`, y la auditoria se enruta a ella ademas de structlog.

- **Alternativa A (descartada): mantener solo structlog.** La traza es efimera y no constituye evidencia durable.
- **Alternativa B (descartada): registrar el valor de contacto.** Violaria el no-PII; la tabla guarda solo identificadores internos.
- **Elegida: tabla durable sin PII.** Coincide con el patron ya usado en incidentes y es testeable.

### D5 — Activacion deliberada y auditada, con aprobacion humana HIGH

Se reemplaza la compuerta "sin mecanismo de activacion" por un mecanismo explicito: migracion gobernada por entorno mas artefacto de aprobacion registrado. No hay interruptor de runtime oculto.

- **Alternativa A (descartada): mantener el bloqueo absoluto.** Impide habilitar datos reales incluso con aprobacion.
- **Alternativa B (descartada): feature flag de runtime.** Es un interruptor oculto que activaria datos reales sin aprobacion verificable.
- **Elegida: migracion/env gateado + artefacto de aprobacion.** Deliberado, auditable y bloqueado por defecto.

### D6 — Retencion operativa: runbook y alerta, sin cron en el codigo

Se documenta un runbook y se define una alerta de acumulacion de filas vencidas (`fecha_baja + 1 año`); la purga sigue siendo MANUAL.

- **Alternativa A (descartada): purga automatica (cron/worker).** Contradice DIR-007 y la decision explicita del autor.
- **Alternativa B (descartada): purga manual sin alerta.** La acumulacion silenciosa es una brecha de retencion.
- **Elegida: runbook + alerta, purga manual.** Mantiene la decision y cierra el hueco operativo.

### D7 — ARCO de acceso y rectificacion, ademas de supresion

El flujo ARCO del directorio cubre acceso y rectificacion con procedimiento y constancia auditable, alineado con `docs/seguridad/procedimiento-arco.md`.

- **Alternativa A (descartada): limitar el ARCO a la supresion.** Deja sin tratamiento los derechos de acceso y rectificacion sobre contacto real.
- **Elegida: cubrir acceso y rectificacion** con el procedimiento existente como base.

### D8 — Migracion reversible con backfill y prueba de no-plaintext

Una migracion Alembic REVERSIBLE agrega las columnas cifradas e indice ciego, rellena las filas existentes (cifrando el contacto y derivando el indice) y un test de integracion prueba que no queda email ni telefono en claro.

- **Alternativa A (descartada): recrear la tabla.** Rompe FKs entrantes (`incidente.reportante_empleado_id`) y es mas riesgosa que un `ALTER TABLE` con backfill.
- **Elegida: `ALTER TABLE` reversible con backfill transaccional y prueba de no-plaintext.**

## Risks / Trade-offs

- [Revertir DIR-005 reabre un hallazgo cerrado] → El ADR documenta la reversion, su motivo y el nuevo control (cifrado + indice ciego + custodia de claves); la justificacion previa se conserva como SUPERADA.
- [El indice ciego filtra igualdad] → Es el tradeoff aceptado del patron: permite unicidad y busqueda determinista sin exponer el valor; el digest va con clave dedicada y no es reversible sin ella.
- [Backfill sobre datos existentes] → Migracion reversible, transaccional y con respaldo previo; test de integracion que verifica que no queda plaintext.
- [Gestion de las claves dedicadas] → Se documenta generacion, custodia y rotacion; la rotacion se cablea al inventario de `rotate_fernet_key.py` con respaldo obligatorio.
- [Rollback del cifrado reintroduce plaintext] → Un rollback que devuelva el contacto a texto plano es una accion HIGH y debe justificarse por escrito; se documenta en el plan de migracion.
- [Alerta de retencion sin PII] → La alerta reporta solo conteos; el detalle de ids es interno y se mantiene fuera de la superficie.
- [La activacion accidental de datos reales] → Mecanismo deliberado con aprobacion registrada; bloqueado por defecto y auditado.
- [Deriva documental (spec, evidencia, CHANGES)] → Referencias cruzadas y tareas de validacion de consistencia.

## Migration Plan

- **Modelo y migracion**: `ALTER TABLE` reversible que agrega `email_bidx`/`telefono_bidx` y convierte `email`/`telefono` a `EncryptedText` con backfill. El downgrade revierte a texto plano (accion HIGH; exige justificacion escrita).
- **Configuracion**: nuevas variables de clave dedicada (cifrado del directorio e indice ciego), documentadas en `App/Backend/.env.example` y en `docs/seguridad/gestion-secretos-y-rotacion.md`; dummies en la CI y en `conftest.py` para el subconjunto offline.
- **Rotacion**: extension del inventario de `scripts/rotate_fernet_key.py` a las columnas del directorio; test que verifica la cobertura del inventario.
- **Auditoria**: nueva tabla durable, append-only y sin PII; enrutado de la auditoria del directorio.
- **Activacion**: migracion/env gateado mas artefacto de aprobacion; mientras no exista, el directorio sigue solo con datos sinteticos.
- **Rollback**: revertir el commit restaura el comportamiento previo SOLO si se revierte tambien la migracion; volver a plaintext queda prohibido sin justificacion escrita (HIGH).
- **Governance**: ningun paso de implementacion se ejecuta sin la aprobacion humana HIGH registrada en `docs/directorio-evidencia-cumplimiento.md` seccion 4 y `CHANGES.md`.

## Open Questions

- Omitidas: la unica ambiguedad relevante (si `usuario_final` lee su propia fila) se resuelve en D5/la spec como lectura de la propia fila unicamente, porque cambia el contrato de DIR-006; no queda como pregunta diferible.
