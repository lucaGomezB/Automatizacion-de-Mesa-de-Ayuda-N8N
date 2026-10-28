# ADR-001 — Reversion de DIR-005: cifrado at-rest del contacto del directorio

> **Tipo**: Architecture Decision Record (reversion de decision).
> **Estado**: ACEPTADO — 2026-10-28 (aprobacion humana HIGH del autor CONCEDIDA).
> **Alcance**: reversion de la decision de minimizacion y adopcion del cifrado at-rest del
> contacto del directorio (`directorio_empleado`) con indice ciego determinista.
> **Encuadre**: stack de desarrollo local; documento **alineado con** los marcos; no es
> certificacion ni auditoria. Los controles organizacionales competen al adoptante.
> **Decide sobre**: `docs/seguridad/justificacion-minimizacion-directorio.md` (v1,
> 2026-10-19), que queda marcada como **SUPERADA**.
> **Control mapeado**: ISO/IEC 27002:2022 5.34 (Privacidad y proteccion de PII) y
> 8.12 (Prevencion de fuga de datos). Hallazgo **5.34/8.12**.
> **Fuente de la decision revertida**: `App/Backend/app/models/empleado.py:16-18`
> (D4 / DIR-005), hallazgos 5.34/8.12 de
> `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`.
> **Gobernanza**: HIGH — datos personales bajo Ley 25.326; habilitar datos reales
> exige aprobacion humana HIGH registrada de forma verificable.

## 1. Contexto

La decision vigente (DIR-005 / DIR-010) almacenaba `email` y `telefono` de
`directorio_empleado` en **texto plano** (`VARCHAR`), sin cifrado de aplicacion ni
indice ciego, y la justificaba por **minimizacion**
(`docs/seguridad/justificacion-minimizacion-directorio.md`). Esa decision tenia
como finalidad no comprometida la operacion del directorio, pero dejaba el
contacto expuesto en reposo (`empleado.py:16-18`).

El hallazgo 5.34/8.12 seguia abierto a nivel de control tecnico: la proteccion
dependia de RBAC + red aislada + auditoria, sin proteccion criptografica del dato
en reposo. La reversion de DIR-005 es la condicion habilitante para poder tratar
PII real de forma segura.

## 2. Decision

Se REVIERTE DIR-005/DIR-010. El email y el telefono del directorio pasan a
CIFRARSE at-rest mediante el TypeDecorator `EncryptedText` (Fernet, el mismo
primitivo ya auditado del incidente). El contacto en claro NO se persiste. La
busqueda por igualdad se resuelve con un **indice ciego determinista**
(`email_bidx`, `telefono_bidx`; HMAC-SHA-256 con clave dedicada), porque Fernet
no es determinista (IV aleatorio por operacion). La unicidad logica del email se
preserva sobre el indice determinista. DIR-005/DIR-010 se REMUEVEN y se sustituyen
por DIR-011 (cifrado at-rest con indice ciego) y DIR-016 (este ADR).

## 3. Motivacion

- **Habilitar PII real con el contacto protegido en reposo**: sin cifrado, tratar
  datos reales expondria el contacto a cualquiera con acceso a la base o a un
  respaldo.
- **Cerrar el hallazgo 5.34/8.12 con un control tecnico**, no solo con RBAC, red
  aislada y auditoria.
- **Coherencia con el primitivo ya auditado**: se reutiliza `EncryptedText`
  (Fernet) y su rotacion (`scripts/rotate_fernet_key.py`) en lugar de introducir
  un mecanismo nuevo.

## 4. Alternativas evaluadas

| Alternativa | Descripcion | Veredicto |
|-------------|-------------|-----------|
| **A. Mantener el texto plano** | La decision que este ADR revierte | **Descartada**: bloquea habilitar datos reales con PII en reposo |
| **B. Cifrado por campo ad hoc en la capa de aplicacion** | Cifrar en el servicio con una clave propia | **Descartada**: duplica el mecanismo `EncryptedText` y su custodia |
| **C. TDE / pgcrypto del motor** | Cifrado a nivel de PostgreSQL | **Descartada**: acopla el cifrado al despliegue y no cubre el modelo de claves de la aplicacion |
| **D. Cifrado + indice ciego determinista (ELEGIDA)** | `EncryptedText` + HMAC-SHA-256 con clave dedicada | **Elegida**: cifra en reposo, permite busqueda por igualdad y unicidad, y desacopla la clave del indice de la clave de cifrado |
| **E. Hash sin clave (SHA-256 puro)** | Indice determinista sin clave | **Descartada**: el espacio email/telefono es enumerable; sin clave es vulnerable a diccionario y reversible por fuerza bruta |

Para la busqueda, se descarta ademas la igualdad sobre la columna cifrada (Fernet
produce ciphertext distinto por IV: la igualdad siempre falla) y el filtrado en
memoria descifrando toda la tabla (impracticable y filtra PII al proceso).

## 5. Consecuencias

- **En reposo**: `email`/`telefono` se leen como ciphertext Fernet; nunca en claro.
- **Busqueda/unicidad**: por indice ciego determinista (HMAC-SHA-256 con clave
  dedicada), no por la columna cifrada.
- **Custodia de claves**: una clave de cifrado del directorio y una clave de
  indice ciego DEDICADAS, independientes de la clave de pseudonimizacion del
  incidente. Generacion, custodia y rotacion documentadas en
  `docs/seguridad/gestion-secretos-y-rotacion.md`; la rotacion Fernet del
  directorio se cablea en el inventario de `scripts/rotate_fernet_key.py` con
  respaldo previo obligatorio.
- **Migracion**: `ALTER TABLE` reversible (revision 021) con backfill cifrando el
  contacto existente. Un rollback que devuelva el contacto a texto plano es una
  accion HIGH y exige justificacion escrita.
- **Justificacion previa**: se conserva como registro historico marcado como
  **SUPERADA**; no se reescribe su contenido.

## 6. Trazabilidad

- **Revierte**: DIR-005 (almacenamiento en texto plano) y DIR-010 (justificacion
  documental de la minimizacion en texto plano).
- **Sustituye por**: DIR-011 (cifrado at-rest con indice ciego) y DIR-016 (este
  ADR).
- **Hallazgo**: 5.34/8.12 del gap assessment ISO/IEC 27002 / NIST CSF 2.0.
- **Commit/fuente**: `App/Backend/app/models/empleado.py:16-18` (D4 / DIR-005).
- **Change**: `c-153-endurecer-el-directorio-para-datos-reales`.
