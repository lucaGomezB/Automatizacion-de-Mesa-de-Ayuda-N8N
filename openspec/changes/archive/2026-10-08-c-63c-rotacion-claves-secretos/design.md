# Design: c-63c-rotacion-claves-secretos

## Context

Ver `proposal.md — Why`. Fase C del split de `c-63-identidad-accesos-claves`; las decisiones de fase C son el D8 (rotacion JWT) y D9 (rotacion Fernet) del `design.md` master, ya resueltas por el autor. Restricciones verificadas que moldean el enfoque:

- **JWT actual.** HS256 con clave unica `settings.jwt_secret_key`; `core/security.py` decodifica exigiendo `exp`; `auth_service.create_access_token` firma con la misma clave. No hay `kid`. c-63a agrega vida corta, refresco y revocacion; la rotacion de `c-63c` se apoya en ese contrato.
- **Fernet actual.** `utils/encryption.py` expone `EncryptedText` sobre una unica `Fernet`, con cache lazy invalidado por cambio de clave. Columnas cifradas verificadas en el codigo: `incidente.descripcion_original` (NOT NULL), `telefonia_ingreso.caller_cifrado` y `telefonia_ingreso.transcript_original` (nullable). El enunciado de la fase citaba solo la primera: el inventario real es de tres columnas.
- **Sin despliegue productivo.** Stack `mesa_local` (compose); TLS self-signed. KMS/Vault, PAM y CA real no tienen infraestructura: se documentan, no se implementan.
- **Flujo dev/CI.** Suite backend SQLite offline + PostgreSQL `@pytest.mark.integration`; fallback Fernet y configuraciones sembradas deben seguir funcionando sin pasos extra.
- **Documentacion.** `docs/seguridad/README.md` (indice C-61, archivado) mapea controles a documentos; `docs/security-hardening.md` (secret-hygiene) ya documenta la rotacion de credenciales expuestas; `docs/pseudonymization.md` documenta el riesgo de perdida de la clave Fernet.
- **Governance CRITICO.** Decisiones resueltas por el autor; el agente las implementa y registra como Open Question cualquier tension NUEVA.

## Goals / Non-Goals

**Goals:**

- Rotar el secreto JWT con keyring `kid` + ventana de solapamiento, sin re-login masivo y con verificacion acotada.
- Rotar la clave Fernet con `MultiFernet` y una herramienta que re-cifra transaccionalmente con respaldo previo obligatorio y es revertible.
- Dejar inventario de secretos + runbook de rotacion, y documentar postura `.env` y KMS/PAM/CA como futuro.
- Documentar 5.16/5.18 como control organizacional, referenciado desde el indice de `docs/seguridad/`.

**Non-Goals:**

- Implementar KMS/Vault, PAM o una CA real de produccion (sin infraestructura).
- Adoptar SOPS/Docker secrets/Vault ahora.
- Cambiar el algoritmo de firma JWT ni el contrato de login (eso es de c-63a).
- Modificar `CHANGES.md`, otros changes o la prosa de tesis.

## Decisions

### D-C1 — Estrategia de verificacion del keyring JWT ("probar claves") y su cota

**Recomendado: keyring de a lo sumo dos claves (activa + anterior) con prueba acotada.**

- Al firmar, siempre la clave activa y su `kid` en el header (claim aditivo).
- Al verificar: leer el `kid` no verificado del header; si coincide con la clave activa, verificar con ella; si coincide con la anterior y la ventana esta abierta, verificar con la anterior; si el token no trae `kid` (legacy), probar activa y luego anterior.
- **Cota**: como maximo dos verificaciones por token (una por clave vigente). No existe lista ilimitada de claves; las claves fuera del keyring no se intentan.
- Alternativas: denylist por `jti` (no resuelve la rotacion de la clave), rotar forzando re-login (invalida sesiones), clave por entorno sin versionado (no convive). Descartadas.

### D-C2 — Configuracion aditiva del keyring

**Recomendado: mantener `jwt_secret_key` como clave activa y agregar parametros opcionales.**

- `jwt_secret_key` (existente) = clave activa; se agrega `jwt_key_id` (default `v1`) como su `kid`.
- `jwt_previous_secret_key` (default vacio) y `jwt_previous_key_id` (default vacio): la clave anterior.
- `jwt_previous_key_expires_at` (default vacio): instante hasta el que se acepta la clave anterior; vacio = sin ventana.
- Retrocompatible: sin clave anterior, el comportamiento es el actual (un token por la clave activa). Los tests existentes de `test_auth.py` no cambian.

### D-C3 — `MultiFernet` y cache de claves

**Recomendado: `MultiFernet([activa, anterior?])` en `utils/encryption.py`.**

- La clave activa es `pseudonymization_encryption_key` (existente); se agrega `pseudonymization_encryption_key_previous` (default vacio).
- Al cifrar, `MultiFernet` usa siempre la primera clave (la activa); al descifrar, prueba las claves del conjunto.
- El cache se invalida por el **conjunto** de claves (no por una sola): si cambia la activa o la anterior, se reconstruye.
- Alternativa: re-cifrado manual (propenso a error). Descartada.

### D-C4 — Herramienta de rotacion Fernet: respaldo, transaccion y orden

**Recomendado: `scripts/rotate_fernet_key.py` con respaldo previo obligatorio y re-cifrado en una transaccion.**

- **Respaldo previo obligatorio**: el script exige una ruta de respaldo existente (p. ej. `--backup-path`); si falta o el archivo no existe, aborta con codigo no-cero sin tocar datos.
- Enumera de forma **explicita** las columnas del inventario (D-C5); no infiere tablas.
- Re-cifra fila por fila dentro de UNA transaccion; cualquier error revierte todo (sin estado parcial).
- Orden de rotacion: (1) se configura la clave nueva como activa y la anterior como respaldo; (2) se ejecuta el script y re-cifra con la nueva; (3) se confirma por conteo/verificacion; (4) recien entonces se retira la anterior del conjunto.
- Revertir: reponer la anterior como activa (o restaurar el respaldo) permite descifrar los datos.
- Alternativa: `alembic` data-migration (acopla la rotacion al esquema y a la configuracion); manual (sin verificacion). Descartadas.

### D-C5 — Inventario Fernet como prerequisito

**Recomendado: inventariar antes de escribir el script.**

- El inventario exacto (tabla, columna, nulabilidad, sensibilidad) es una tarea previa y un artefacto documentado.
- Hoy: `incidente.descripcion_original`, `telefonia_ingreso.caller_cifrado`, `telefonia_ingreso.transcript_original`. Futuro: columna del secreto TOTP de c-63b (se incorpora al inventario cuando c-63b aterrice).
- El script y la documentacion comparten el inventario como fuente unica; un test verifica que el script cubre todas las columnas del inventario.

### D-C6 — Ubicacion de inventario, runbook y encuadre

**Recomendado: nuevo documento `docs/seguridad/gestion-secretos-y-rotacion.md` + actualizacion del indice.**

- Contiene el inventario de secretos (JWT, Fernet, y los ya existentes de la plataforma), el runbook de rotacion (procedimiento y orden), la postura `.env` y las opciones no adoptadas (SOPS/Docker secrets/Vault), y el encuadre de KMS/PAM/CA como futuro.
- Se referencia desde `docs/seguridad/README.md` y se cruza con `docs/security-hardening.md` (rotacion de credenciales expuestas) y `docs/pseudonymization.md` (riesgo de perdida de la clave).
- Alternativa: extender solo `docs/security-hardening.md` (mezcla dos propositos: exposicion y rotacion planificada). Descartada.

### D-C7 — Controles organizacionales 5.16 / 5.18

**Recomendado: documento(s) en `docs/seguridad/` marcados como (O).**

- Ciclo de vida de identidades (alta, cambio, baja) y aprobacion/revision periodica de derechos, como responsabilidad de la organizacion adoptante.
- Sin codigo; requisito documental y verificable (IAH-011), referenciado desde el indice.

### D-C8 — Compatibilidad dev/CI

**Recomendado: defaults retrocompatibles.**

- Sin `jwt_previous_secret_key` y sin clave Fernet anterior, el sistema se comporta como hoy.
- Los tests de rotacion JWT inyectan claves y ventana; los de Fernet usan datos de prueba en SQLite.
- El subconjunto offline no depende de tiempos reales: la ventana se evalua contra un instante inyectable.

## Risks / Trade-offs

- **[Perdida de datos at-rest en la rotacion Fernet]** → MultiFernet + respaldo previo obligatorio + transaccion unica (D-C4).
- **[Inventario incompleto]** → inventario como prerequisito y test que verifica cobertura del script (D-C5).
- **[Tokens previos rechazados por una ventana mal configurada]** → `jwt_previous_key_expires_at` explicito y tests de borde (D-C1/D-C2).
- **[Sobredeclarar KMS/PAM/CA]** → encuadre explicito en IAH-010 y D-C6.
- **[Acoplamiento con c-63b]** → el inventario es la fuente unica; la columna TOTP se agrega al aterrizar c-63b.

## Migration Plan

1. **Pre-apply:** confirmar dependencias c-63a/c-63b y registrar la resolucion de OQ-C1.
2. **Inventario:** producir el inventario exacto de columnas Fernet (prerequisito) y de secretos.
3. **JWT:** configuracion del keyring + `kid` en la firma + verificacion acotada con ventana + tests.
4. **Fernet:** `MultiFernet` + `scripts/rotate_fernet_key.py` (respaldo + transaccion) + tests de rotacion y revertibilidad.
5. **Docs:** `gestion-secretos-y-rotacion.md`, 5.16/5.18, indice actualizado y encuadre de KMS/PAM/CA.
6. **Cierre:** suites backend/frontend verdes; higiene de secretos sin hallazgos; `openspec validate c-63c-rotacion-claves-secretos --strict`.
7. **Rollback:** reponer la clave anterior (JWT y Fernet) o restaurar el respaldo; revertir los commits de codigo y configuracion.

## Open Questions — RESUELTAS (autor, 2026-10-08)

- **OQ-C1 (inventario Fernet real) = alcance ampliado CONFIRMADO.** El respaldo y el re-cifrado abarcan las **tres** columnas Fernet vigentes (`incidente.descripcion_original`, `telefonia_ingreso.caller_cifrado`, `telefonia_ingreso.transcript_original`) mas el secreto TOTP de c-63b; `telefonia_ingreso` entra en el respaldo previo obligatorio (no se acota a `descripcion_original`).
