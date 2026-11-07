# Runbook — Reparación del mojibake de las descripciones de correo (c-181)

Procedimiento MANUAL y controlado para reparar las descripciones de incidentes
de correo electrónico corrompidas por el mojibake de doble codificación
introducido en el canal de ingesta de N8N.

> **La reparación es MANUAL y CONTROLADA. NO es una migración de base de datos.**
> No se auto-ejecuta en ningún `alembic upgrade` ni en ningún entorno. Se corre a
> mano, con respaldo previo, y **su aplicación sobre `mesa_de_ayuda_campana` (la
> base de la campaña, evidencia de tesis) requiere aprobación explícita del
> usuario**.
>
> La corrección de la CAUSA (la imagen/harness N8N que genera la corrupción) es un
> change separado (`c-182`) y queda fuera de alcance de este procedimiento.

---

## 1. Causa raíz

El trigger IMAP de N8N, a través del paquete `@n8n/imap` incluido en la imagen
pinneda `n8nio/n8n:2.11.2`, **descarta el charset al decodificar las partes de
correo codificadas en `quoted-printable` y las re-codifica DOS veces**. El
mecanismo es una doble codificación clásica:

1. El cuerpo del correo llega codificado en UTF-8 (por ejemplo `ñ` = bytes
   `C3 B1`).
2. El paquete pierde la declaración de charset y trata cada byte como un
   carácter `latin-1` (single-byte): `C3` → `Ã` (U+00C3), `B1` → `±` (U+00B1).
3. Al volver a codificar a UTF-8, el texto queda almacenado como `Ã±`.

Resultado: `Reunión` se persiste como `ReuniÃ³n`, `Señal` como `SeÃ±al`, etc.

Condiciones de aparición:

- **Solo el canal `correo electrónico`.** Los demás canales no pasan por
  `@n8n/imap`.
- **Solo los cuerpos cuya línea supera los 78 bytes.** Los cuerpos cortos viajan
  como `8bit` y quedan limpios; el umbral de 78 bytes de `quoted-printable` (el
  corte de línea suave) es lo que dispara la ruta de re-codificación defectuosa.

El resultado es **DATA CORRUPTA ya persistida** en las descripciones. La
`descripcion_pseudonimizada` (texto en claro que consume el clasificador y expone
la API) y el TEXTO PLANO de `descripcion_original` (cifrado Fernet, evidencia de
auditoría) quedaron ambos corruptos.

---

## 2. Volumen afectado por base

| Base de datos            | Descripciones de correo afectadas | Total de correo | Nota |
|--------------------------|-----------------------------------|-----------------|------|
| `mesa_de_ayuda_campana`  | 13                                | 66              | Evidencia de la tesis |
| `mesa_de_ayuda` (app)    | 47                                | 133             | 43 de esos 47 provienen de Gmail real, NO de un artefacto del corpus |

El volumen es pequeño (decenas de filas por base), por lo que el escaneo
completo de la tabla `incidente` es aceptable.

---

## 3. El reverso exacto

El reverso de la doble codificación es una única operación:

```python
limpio = corrupto.encode("latin-1").decode("utf-8")
```

El script `App/Backend/scripts/reparar_encoding_descripciones.py` lo encapsula en
funciones PURAS y testeables:

- `revertir_mojibake(value) -> str | None` — aplica el reverso; devuelve `None`
  si el texto no es codificable en `latin-1` (por ejemplo un emoji) o si el
  resultado no es UTF-8 válido.
- `es_mojibake(value) -> bool` — detección positiva SOLO si se cumplen las tres
  condiciones: (a) el texto presenta la firma del mojibake (un byte lead
  `U+00C2`/`U+00C3`/`U+00E2`/`U+00F0` seguido de un byte de continuación
  `U+0080–U+00BF`); (b) el reverso tiene éxito; (c) el texto revertido difiere
  estrictamente del original y ya no presenta la firma.

El script repara, para cada fila detectada como corrupta, **ambas columnas**:
`descripcion_pseudonimizada` (reverso directo) y `descripcion_original`
(descifrado Fernet → reverso → re-cifrado, reutilizando el helper de cifrado de
la aplicación `app/utils/encryption.py`). La selección es por firma, sin filtrar
por canal ni por borrado lógico.

---

## 4. Procedimiento

`<url-campana>` y `<url-app>` son las URLs SQLAlchemy de cada base (por ejemplo
`postgresql+asyncpg://mesa:<password>@localhost:5433/mesa_de_ayuda_campana`).
Sustituir por los valores reales del entorno.

### 4.1 Respaldo previo (OBLIGATORIO antes de escribir)

```bash
# Respaldar la base objetivo con pg_dump y registrar la ruta del respaldo.
docker compose exec -T postgres pg_dump -U mesa mesa_de_ayuda_campana \
  > backups/backup_campana_$(date +%Y%m%d_%H%M%S).sql
```

Verificar que el archivo existe y tiene tamaño no trivial. No continuar sin
respaldo. (Para el esquema de respaldo/restauración general ver
`docs/operational-guide.md` §3.)

### 4.2 Dry-run y revisión de conteos

```bash
cd App/Backend
python -m scripts.reparar_encoding_descripciones --database-url "<url-campana>"
```

Sin `--apply` el script **NO escribe nada**. Imprime la base objetivo y un
resumen con los conteos:

```
[dry-run] base objetivo: mesa_de_ayuda_campana
[dry-run] resumen: candidatos=13 reparados=0 omitidos=<N> errores=0
```

Revisar con el usuario que los `candidatos` sean coherentes con los 13 esperados
y que `errores=0`. No continuar si aparecen errores inesperados.

### 4.3 Aplicar (solo con aprobación explícita)

```bash
cd App/Backend
python -m scripts.reparar_encoding_descripciones \
  --database-url "<url-campana>" --apply
```

`--apply` imprime una advertencia recordando respaldar la base e incluye el
nombre de la base objetivo en el resumen. El script procesa **fila por fila en su
propia transacción**: el fallo de una fila se reporta como error sin escrituras
parciales y sin impedir la reparación del resto. La operación es **idempotente**.

### 4.4 Verificación e idempotencia

```bash
cd App/Backend
# Control: la base ya no debe presentar candidatos.
python -m scripts.reparar_encoding_descripciones --database-url "<url-campana>"
```

Esperado: `candidatos=0 reparados=0 errores=0`. Ese `candidatos=0` es la prueba
de ausencia de la firma del mojibake y de la idempotencia.

### 4.5 Base de la aplicación (opcional, con aprobación)

Repetir 4.1–4.4 apuntando a `<url-app>` (`mesa_de_ayuda`), con la misma
aprobación explícita del usuario.

---

## 5. Verificación

1. **Ausencia de la firma:** el dry-run de control posterior reporta
   `candidatos=0` sobre la base intervenida (el detector es la autoridad de la
   firma). Un dry-run posterior con candidatos no nulos indica reparación
   incompleta o corrupción nueva.
2. **Round-trip de la columna cifrada:** para una fila reparada, descifrar
   `descripcion_original` (vía `app.utils.encryption.decrypt_value`) debe devolver
   el texto limpio, y `descripcion_pseudonimizada` debe dejar de presentar la
   firma.
3. **Filas limpias intactas:** ninguna fila limpia debe haber cambiado (ni su
   `descripcion_pseudonimizada` ni su ciphertext). El conteo `omitidos` del
   dry-run previo es la referencia de filas limpias.

---

## 6. Evidencia a registrar

Registrar por cada base intervenida, en el orden de ejecución:

- Fecha y hora de la corrida.
- Ruta del respaldo `pg_dump` tomado antes de escribir.
- El comando exacto ejecutado (incluyendo `--database-url` y, si correspondió,
  `--apply`).
- Conteos del **dry-run** previo: `candidatos`, `omitidos`, `errores`.
- Conteos del **apply**: `candidatos`, `reparados`, `errores` (y `detalles_error`
  por fila, si los hubo).
- Conteos del **dry-run de control** posterior: `candidatos=0`.
- El `git` hash del repositorio al momento de la corrida.

### Corrida ejecutada (2026-11-07)

- Commit de trabajo al momento de la corrida: `0d0bfa0` (los artefactos de c-181
  se agregaron sin commitear; ver el commit de cierre del change).
- Respaldos `pg_dump` previos: `/tmp/backup_campana_20261107-130719.sql` y
  `/tmp/backup_app_20261107-130719.sql`.
- Comando: `python3 -m scripts.reparar_encoding_descripciones --apply
  --database-url postgresql+asyncpg://mesa:***@localhost:5433/<base>`
  (contra PostgreSQL local; dentro del contenedor la base es `postgres:5432`).

| Base | Dry-run previo | Apply | Dry-run de control |
|---|---|---|---|
| `mesa_de_ayuda_campana` | candidatos=13, omitidos=187, errores=0 | reparados=13, errores=0 | candidatos=0 |
| `mesa_de_ayuda` | candidatos=47, omitidos=253, errores=0 | reparados=47, errores=0 | candidatos=0 |

- Verificacion: la firma del mojibake (`descripcion_pseudonimizada LIKE '%Ã%'`)
  quedo en `0` en ambas bases; las descripciones con tildes correctas pasaron de
  `59` a `72` en la campana y a `124` en la app. Ninguna fila limpia se modifico
  (omitidos 187 y 253 sin cambios).

---

## 7. Reparar / deshacer

- Las escrituras se limitan a las dos columnas de descripción de las filas
  detectadas como corruptas. El script no borra filas ni toca otros campos.
- Para revertir: restaurar el respaldo de la base intervenida tomado en 4.1.
- Para volver a aplicar: repetir el procedimiento (idempotente).

---

## 8. Referencias

- Script: `App/Backend/scripts/reparar_encoding_descripciones.py`
  - Opciones CLI: `--apply` (escribe; por defecto es dry-run) y
    `--database-url` (base objetivo; por defecto el engine de la aplicación).
- Pruebas: `App/Backend/tests/test_reparar_encoding_descripciones.py`
  (`cd App/Backend; pytest tests/test_reparar_encoding_descripciones.py -v`).
- Procedimiento de respaldo/restauración general: `docs/operational-guide.md` §3.
- Change de causa raíz (imagen/harness N8N): `c-182` (fuera de alcance).
