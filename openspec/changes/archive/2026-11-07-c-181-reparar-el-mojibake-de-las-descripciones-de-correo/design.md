## Context

Ver `proposal.md` — Why. Estado actual y restricciones que condicionan el enfoque:

- La `descripcion_pseudonimizada` (`app/models/incidente.py:92`, `Text` en claro) es la representacion
  operativa que consume el clasificador y expone la API. La `descripcion_original`
  (`app/models/incidente.py:88`, `EncryptedText` Fernet) guarda el texto crudo para auditoria; su
  TEXTO PLANO tambien quedo corrupto, aunque no se muestra en ninguna superficie.
- El helper de cifrado es `app/utils/encryption.py`: `decrypt_value` / `encrypt_value` y el
  TypeDecorator `EncryptedText` (cifra en `process_bind_param`, descifra en `process_result_value`).
  La clave sale de `settings.pseudonymization_encryption_key` (lazy).
- El reverso del mojibake es `value.encode('latin-1').decode('utf-8')`, verificado por round-trip en
  todas las filas afectadas (13/66 en `mesa_de_ayuda_campana`; 47/133 en `mesa_de_ayuda`).
- Precedentes de scripts en `App/Backend/scripts/`: `rotate_fernet_key.py` (respaldo previo
  obligatorio, una transaccion, `asyncio.run`, `async_sessionmaker` sobre `app.core.database.engine`)
  y `purgar_directorio.py` (logica en una funcion coroutine testeable + CLI delgado). Este change sigue
  esa forma: nucleo testeable y CLI delgado.
- La suite de tests del backend corre offline con SQLite in-memory (subset sin `@pytest.mark.integration`).
- Governance MEDIUM: la base de la campana es evidencia de tesis; la aplicacion requiere aprobacion
  explicita del usuario. La causa raiz (imagen/harness N8N) es `c-182`, fuera de alcance.

## Goals / Non-Goals

**Goals:**

- Reparar de forma idempotente y selectiva las descripciones pseudonimizadas y cifradas corruptas por
  mojibake, dejando intactas las filas limpias.
- Exponer la logica PURA de deteccion/reverso como unidad testeable sin base de datos.
- Ofrecer DRY-RUN por defecto y escritura explicita con `--apply`, con reporte de conteos y
  transaccion por fila.
- Poder apuntar el mismo script a `mesa_de_ayuda_campana` o a `mesa_de_ayuda` sin duplicar codigo.
- Documentar causa raiz, volumen, reverso, procedimiento, verificacion y evidencia.

**Non-Goals:**

- No corregir la causa (imagen/harness N8N): `c-182`.
- No re-ingestar casos ni tocar el corpus en disco.
- No escribir una migracion de Alembic (la app esta congelada en la migracion 020; una reparacion de
  datos de una sola vez no debe auto-ejecutarse en cada entorno).
- No cambiar el modelo, la API, el frontend ni el esquema.

## Decisions

### D1 — Script standalone, NO migracion de Alembic

**Decision: `App/Backend/scripts/reparar_encoding_descripciones.py`, ejecutado a mano.** Una migracion
de Alembic se auto-aplicaria en cada `alembic upgrade` de cada entorno, incluidos los efimeros y los
tests; una reparacion de datos puntual no debe repetirse ni siquiera existir fuera de la base que
realmente tiene la corrupcion. Ademas la app de `mesa_de_ayuda` esta congelada en la migracion 020 y
agregar una version superior la marcaria como pendiente. Alternativa considerada (migracion de datos):
descartada por los riesgos anteriores.

### D2 — Separar la logica PURA del I/O para testear sin base

**Decision: las funciones de deteccion y reverso viven en el modulo del script y son puras.** Firma
propuesta:

```
def revertir_mojibake(value: str) -> str | None   # None si no es reversible
def es_mojibake(value: str) -> bool               # deteccion (firma + reverso + diferencia estricta)
```

Las pruebas unitarias importan esas funciones y NO requieren base ni red. La parte de seleccion/escritura
(`reparar_descripciones(session, *, apply)`) se prueba offline con SQLite in-memory siguiendo las
convenciones del backend. Alternativa considerada (meter la logica en un util de `app/utils/`): valida,
pero no hace falta exportarla como API de la app; el script es su unico consumidor y mantenerla en el
script evita inflar la superficie publica. Se documenta que el import del modulo es seguro sin clave
(configurada lazy) para que el test pure no dependa del entorno.

### D3 — Definicion exacta de la deteccion (evita falsos positivos)

**Decision: deteccion positiva solo si se cumplen las tres condiciones.** (a) firma del mojibake: el
texto contiene la firma clasica de bytes UTF-8 renderizados como latin-1, es decir un caracter lead en
`\u00c2`, `\u00c3`, `\u00e2`, `\u00f0` seguido de un caracter en el rango `\u0080-\u00bf`; (b) reverso
`value.encode('latin-1').decode('utf-8')` con exito; (c) el resultado difiere estrictamente del original
Y ya no contiene la firma. Se captura `UnicodeEncodeError`/`UnicodeDecodeError` y se devuelve "no
corrupto" sin propagar. La firma como guarda adicional es lo que separa un texto limpio extraño (que
casualmente revierta) de un texto realmente corrupto; un texto limpio normal (por ejemplo "café") NO es
`latin-1`-codificable a `utf-8` valido y queda fuera. Alternativa considerada (solo "el reverso difiere"):
descartada por mas falsos positivos.

### D4 — Reparacion de la columna cifrada en la misma fila

**Decision: para cada fila corrupta, reparar `descripcion_pseudonimizada` (reverso directo) y
`descripcion_original` (descifrado por el TypeDecorator -> reverso del texto plano -> re-cifrado en el
siguiente flush, forzado con `flag_modified`).** El texto plano de la columna cifrada se revierte solo
si tambien es detectado como corrupto; si ya viniera limpio se conserva tal cual (no es un error). Un
token NO descifrable (`InvalidToken`) es un error de la fila: se reporta y NO se escribe la pseudonimizada
de esa fila (sin cambios parciales). Alternativa considerada (reparar solo la pseudonimizada): se
mantiene como fallback documentado, pero el default repara ambas porque el round-trip esta verificado y
el texto cifrado es evidencia de auditoria. Se reutilizan `decrypt_value`/`encrypt_value` de
`app/utils/encryption.py`, sin reimplementar Fernet.

### D5 — Seleccion por firma, no por canal; sin filtro de borrado logico

**Decision: recorrer las filas de `incidente` y aplicar la deteccion por firma, sin filtrar por canal ni
por `deleted_at`.** La firma es el criterio autoritativo de corrupcion; el defecto es a nivel de datos y
no se confia en un filtro de canal (aunque el mojibake solo aparezca en correo). Incluir filas con
borrado logico es correcto: su texto sigue corrompido y la fila es parte de la evidencia/auditoria.
Alternativa considerada (filtrar `canal_origen = correo`): descartada por fragil (depende del catalogo y
de ids por entorno) y porque la firma ya es suficiente. Los volumenes son chicos (cientos de filas), asi
que el escaneo completo es aceptable.

### D6 — Longitud de la excepcion: transaccion por fila (no una unica transaccion)

**Decision: confirmar cada fila en su propia transaccion** (`session.commit()` por fila; `rollback` solo
de la fila fallida). El spec exige que el fallo de una fila no produzca escrituras parciales ni impida
procesar el resto, y que la reparacion sea reanudable. Esto DIFIERE a proposito de `rotate_fernet_key.py`
(una sola transaccion): alli la atomicidad total es deseable porque el re-cifrado es indivisible; aqui la
resiliencia y la idempotencia pesan mas. Trade-off: no hay atomicidad global; una interrupcion deja las
filas previas ya reparadas, que es el resultado deseado (la re-ejecucion no las vuelve a tocar).

### D7 — Puntero a la base via `--database-url` opcional, default el engine de la app

**Decision: el script usa `app.core.database.engine` por defecto (base de la app) y acepta
`--database-url` opcional para apuntar explicitamente a `mesa_de_ayuda_campana` u otra base.** Asi el
mismo codigo sirve a las dos bases sin duplicar el script ni depender de reconfigurar el `.env`. La
escritura sigue gobernada por `--apply`: sin el flag, el script NUNCA escribe, aun con `--database-url`.
Alternativa considerada (depender solo de `DATABASE_URL`): descartada por riesgo de apuntar al `.env`
equivocado sin que el operador lo note; un flag explicito es verificable en el comando registrado como
evidencia.

### D8 — Ubicacion del runbook

**Decision: `docs/runbook-reparacion-encoding-descripciones.md`.** Sigue la convencion existente de
runbooks en `docs/` (`runbook-corpus-telefonia.md`, `runbook-smoke-stack-referencia.md`), es
descubrible y queda versionado junto al resto de la documentacion operativa. Alternativa considerada
(`docs/campana-medicion/`): descartada porque la reparacion cubre ambas bases, no solo la campana.

### D9 — Ubicacion de las pruebas

**Decision: `App/Backend/tests/test_reparar_encoding_descripciones.py`.** Corre en el subset SQLite
offline (sin `@pytest.mark.integration`). Cubre la logica pura (D2) con casos de corrupto/limpio/no
reversible y la idempotencia con SQLite in-memory; no requiere PostgreSQL ni servicios externos.

## Risks / Trade-offs

- Falso positivo que toque una fila limpia -> Mitigacion: triple condicion (D3); el test fija que un
  texto limpio y un texto no reversible se omiten sin cambios.
- Corromper el ciphertext de `descripcion_original` -> Mitigacion: round-trip verificado, dry-run
  previo obligatorio y respaldo de la base antes del `--apply` (documentado en el runbook); si la fila
  no descifra, se reporta como error y no se escribe nada.
- Interrupcion a mitad de la corrida -> Mitigacion: transaccion por fila (D6); lo ya reparado queda
  consistente y la re-ejecucion es idempotente.
- Apuntar por error a la base equivocada -> Mitigacion: `--database-url` explicito (D7) y dry-run por
  defecto; la aplicacion sobre la campana requiere aprobacion del usuario.
- El escaneo sin filtro de canal podria tocar mas filas de las esperadas -> Mitigacion: la seleccion es
  por firma, asi que solo filas realmente corruptas cambian; el dry-run reporta los candidatos antes de
  escribir.

## Migration Plan

1. Preparar: activar el hook de pre-commit, respaldar la base objetivo con `pg_dump` (obligatorio antes
   de escribir) y configurar `PSEUDONYMIZATION_ENCRYPTION_KEY`.
2. Dry-run sobre la base objetivo (`--database-url` de `mesa_de_ayuda_campana`): revisar los conteos de
   candidatos/reparables/omitidos/errores.
3. Con aprobacion del usuario, `--apply` sobre `mesa_de_ayuda_campana`; registrar los conteos antes/despues.
4. Repetir dry-run para confirmar idempotencia (cero candidatos) y verificacion de ausencia de la firma.
5. Opcional y con aprobacion: mismo procedimiento apuntado a `mesa_de_ayuda`.

Rollback: restaurar el respaldo de la base intervenida. El script no borra filas ni toca otros campos.

## Open Questions

- Si la `descripcion_original` de alguna fila no descifra por una clave ausente en el entorno, queda
  como fila en error y se resuelve en la corrida con la clave correcta; no cambia el enfoque ni los
  specs.
