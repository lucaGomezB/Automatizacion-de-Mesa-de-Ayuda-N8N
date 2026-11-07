# Proposal: Reparar el mojibake de las descripciones de correo

## Why

El trigger IMAP de N8N (paquete `@n8n/imap` incluido en la imagen pinneada `n8nio/n8n:2.11.2`)
descarta el charset al decodificar las partes de correo en `quoted-printable` y las re-codifica
DOS veces, produciendo el mojibake clasico (`ñ` se almacena como `Ã±`, etc.). Solo afecta al canal
`correo electronico`, y solo a los cuerpos cuya linea supera los 78 bytes (los cortos viajan como
`8bit` y quedan limpios). El resultado es DATA CORRUPTA ya persistida en descripciones de correo en
DOS bases: la de la campana (`mesa_de_ayuda_campana`, 13 de 66 incidentes de correo) y la de la app
(`mesa_de_ayuda`, 47 de 133; 43 de esos 47 provienen de Gmail real, asi que NO es un artefacto del
corpus). La campana es evidencia de la tesis y la descripcion es el texto que consume el
clasificador: hay que repararla AHORA, antes del analisis.

Este change es la MITAD de reparacion de DATOS. La correccion de la CAUSA (la imagen/harness N8N que
genera la corrupcion) es un change SEPARADO (`c-182`) y queda fuera de alcance.

## What Changes

- Nuevo script de reparacion `App/Backend/scripts/reparar_encoding_descripciones.py`, idempotente y
  documentado, siguiendo la convencion de los scripts existentes (`rotate_fernet_key.py`,
  `purgar_directorio.py`): DRY-RUN por defecto, escritura solo con `--apply`, y un resumen de conteos
  impreso (candidatos, reparados, omitidos, errores).
- El script selecciona SOLO las filas realmente corruptas: `descripcion_pseudonimizada` que coincide
  con la firma del mojibake Y cuyo reverso `value.encode('latin-1').decode('utf-8')` tiene exito Y
  produce un texto estrictamente distinto/mas limpio. Las filas limpias quedan intactas.
- Repara `descripcion_pseudonimizada` y, para las mismas filas, `descripcion_original` mediante
  descifrado -> reverso -> re-cifrado, usando el helper de cifrado de la app
  (`app/utils/encryption.py`) y `PSEUDONYMIZATION_ENCRYPTION_KEY`.
- Escribe fila por fila (transaccion por fila; sin escrituras parciales) y reporta conteos. Re-ejecutar
  no encuentra nada que reparar (idempotencia).
- Nueva documentacion (runbook) con la causa raiz, el volumen afectado por base, el reverso exacto, el
  procedimiento (dry-run, revision, apply), la verificacion y la evidencia a registrar (conteos
  antes/despues).
- Pruebas unitarias (pytest, offline) de la logica PURA de deteccion/reverso: detecta corrupto vs
  limpio, es idempotente, deja intactas las filas limpias y maneja texto no-latin1/indecodificable sin
  romper.

**Fuera de alcance (documentado, NO se implementa aqui):**

- NO se corrige la causa (imagen/harness N8N, `@n8n/imap` QP charset drop). Eso es `c-182`.
- NO se re-ingesta ningun caso.
- NO se cambia el encoding del backend ni del frontend (no existe tal cambio).
- NO se usar una migracion de Alembic: es una reparacion de datos de una sola vez que NO debe
  auto-ejecutarse en cada entorno (la app esta congelada en la migracion 020).

**BREAKING:** ninguna.

## Capabilities

### New Capabilities

- `description-encoding-repair`: repara de forma idempotente las descripciones de correo corrompidas
  por el mojibake (deteccion selectiva de la corrupcion, reparacion de la columna pseudonimizada y de
  la cifrada, modo dry-run/apply, reporte de conteos y runbook con la causa raiz y el procedimiento).

### Modified Capabilities

- (ninguna: no cambia el comportamiento de `corpus-n8n-ingest`; ese flujo es la causa y su correccion
  de codigo vive en `c-182`. Este change repara datos ya persistidos.)

## Impact

| Area | Impact | Description |
|------|--------|-------------|
| `App/Backend/scripts/reparar_encoding_descripciones.py` | New | Script de reparacion idempotente (dry-run/apply) |
| `App/Backend/tests/` (nuevo test del script) | New | Pruebas unitarias offline de la logica pura |
| `docs/` (runbook de la reparacion) | New | Causa raiz, volumen, procedimiento, verificacion, evidencia |
| `mesa_de_ayuda_campana` (campana, evidencia de tesis) | Data repair | 13 de 66 descripciones de correo a reparar (MANUAL, con aprobacion del usuario) |
| `mesa_de_ayuda` (app) | Data repair | 47 de 133 descripciones de correo reparables por el mismo script (MANUAL) |
| `App/Frontend/`, API, esquemas, Docker, migraciones | Sin cambios | No hay cambio de encoding; la app queda en la migracion 020 |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Reparar una fila que NO estaba corrupta (falso positivo) | Low | Reverso validado: `latin-1` encode + `utf-8` decode con exito Y resultado estrictamente distinto; si no, se omite |
| Perder datos por una re-codificacion incorrecta | Low | Transaccion por fila; si el reverso falla se omite sin escribir; conteos antes/despues documentados |
| Corromper el ciphertext de `descripcion_original` | Medium | round-trip verificado (decrypt -> reverse -> re-encrypt) y dry-run previo; si se juzga riesgoso, se documenta y se repara al menos la columna pseudonimizada |
| Correccion parcial ante una interrupcion | Low | Cada fila es una transaccion; el reporte de errores es explicito y la re-ejecucion es idempotente |

## Rollback Plan

Las escrituras se limitan a las dos columnas de descripcion de las filas detectadas como corruptas.
Para revertir: restaurar el respaldo previo de la base intervenida (el procedimiento documenta tomar
un `pg_dump` antes del `--apply`). El script en si no borra filas ni toca otros campos, de modo que
una restauracion del respaldo es suficiente. En la app, la reparacion es reversible repitiendo el
procedimiento sobre el respaldo.

## Success Criteria

- [ ] Existe `App/Backend/scripts/reparar_encoding_descripciones.py` con DRY-RUN por defecto y `--apply` para escribir.
- [ ] Dry-run reporta los conteos de candidatos/reparables/omitidos/errores sin tocar la base.
- [ ] El script es idempotente: una segunda corrida no encuentra filas a reparar.
- [ ] Solo se reparan filas realmente corruptas; las limpias quedan intactas.
- [ ] `descripcion_pseudonimizada` y `descripcion_original` (decrypt -> reverse -> re-encrypt) se reparan para las mismas filas.
- [ ] Pruebas unitarias offline de la logica pura en verde.
- [ ] Existe el runbook con causa raiz, volumen por base, reverso, procedimiento, verificacion y evidencia.
- [ ] `openspec validate "c-181-reparar-el-mojibake-de-las-descripciones-de-correo" --strict` en PASS.
- [ ] (MANUAL, con aprobacion del usuario) Reparar `mesa_de_ayuda_campana` y, si corresponde, `mesa_de_ayuda`.
