# Gestion de secretos y rotacion de claves

| Campo | Contenido |
|-------|-----------|
| Control mapeado | ISO/IEC 27002:2022 8.2 (derechos de acceso privilegiado, incluida la gestion de claves) y 8.24 (uso de criptografia); requisito IAH-008..010 del change `c-63c` |
| Estado | v1 — aprobada por el autor el 2026-10-08 (governance CRITICO) |
| Alcance | Inventario de secretos, inventario de columnas cifradas con Fernet y runbook de rotacion (JWT y Fernet). No define la politica de secretos de un despliegue productivo |
| Encuadre | Stack de desarrollo local (`docker-compose.yml`, `name: mesa_local`). Los controles organizacionales competen a la organizacion adoptante (O) |
| Aviso de lenguaje | Alineado con ISO/IEC 27002:2022 8.2 y 8.24. No constituye certificacion ni auditoria |

## 1. Proposito

Dejar verificable y reversible la rotacion de las claves del sistema: el secreto
de firma JWT y la clave Fernet de cifrado at-rest. El documento es la fuente
unica del inventario de secretos y del procedimiento operativo; la herramienta
`App/Backend/scripts/rotate_fernet_key.py` implementa la rotacion Fernet y un
test verifica que su inventario cubre exactamente las columnas cifradas.

## 2. Inventario de secretos

| # | Secreto | Variable | Uso | Obligatorio | Sensibilidad |
|---|---------|----------|-----|-------------|--------------|
| 1 | Secreto de firma JWT (activo) | `JWT_SECRET_KEY` | Firma de access tokens, tickets MFA (HS256) | Si | CRITICA |
| 2 | Secreto de firma JWT (anterior) | `JWT_PREVIOUS_SECRET_KEY` | Respaldo de rotacion; verifica tokens en la ventana | No | CRITICA |
| 3 | Clave Fernet (activa) | `PSEUDONYMIZATION_ENCRYPTION_KEY` | Cifrado at-rest de PII (Fernet) | Si | CRITICA |
| 4 | Clave Fernet (anterior) | `PSEUDONYMIZATION_ENCRYPTION_KEY_PREVIOUS` | Respaldo de rotacion; descifra datos previos | No | CRITICA |
| 5 | API key de Gemini | `GEMINI_API_KEY` | Clasificacion y STT | Si | ALTA |
| 6 | Secreto del webhook N8N | `N8N_WEBHOOK_SECRET` | Header `X-N8N-Secret` en handoffs | Si (si hay webhook) | ALTA |
| 7 | Secreto compartido de la guarda de costo | `COST_GUARD_SHARED_SECRET` | Header `X-Cost-Guard-Secret` | Si (si la guarda esta activa) | ALTA |
| 8 | Token de autenticacion de Twilio | `TWILIO_AUTH_TOKEN` | Firma del webhook de voz y descarga autenticada | No (canal opcional) | ALTA |
| 9 | Account SID de Twilio | `TWILIO_ACCOUNT_SID` | Usuario del HTTP Basic de la grabacion | No | MEDIA |

Reglas:
- Ningun valor real se versiona. La fuente actual es `.env` + variables de
  entorno (ver §4). El archivo `App/Backend/.env.example` documenta las claves
  SIN valores reales.
- El secreto de la cuenta TOTP de cada usuario (`users.totp_secret`) y los
  codigos de recuperacion se cifran/hashean en la base; no son secretos de
  configuracion y no se rotan por este runbook (se regeneran por enrollment).

## 3. Inventario de columnas cifradas con Fernet (prerequisito D-C5)

Verificado en el codigo: toda columna declarada con el TypeDecorator
`EncryptedText` (`App/Backend/app/utils/encryption.py`). El script de rotacion
enumera esta lista de forma explicita (NO infiere tablas) y un test verifica que
la lista cubre exactamente las columnas cifradas del modelo ORM.

| Tabla | Columna | Nulabilidad | Sensibilidad | Notas |
|-------|---------|-------------|--------------|-------|
| `incidente` | `descripcion_original` | NOT NULL | PII (Ley 25.326) | Texto crudo del incidente |
| `telefonia_ingreso` | `caller_cifrado` | nullable | PII (numero llamante) | Canal de telefonia (c-52) |
| `telefonia_ingreso` | `transcript_original` | nullable | PII (transcript crudo) | Solo auditoria / ARCO |
| `users` | `totp_secret` | nullable | Secreto de autenticacion | Segundo factor TOTP (c-63b) |

El respaldo previo obligatorio y el re-cifrado abarcan las CUATRO columnas; en
particular `telefonia_ingreso` entra en el respaldo (no se acota a
`descripcion_original`).

## 4. Postura de gestion de secretos

- **Fuente actual**: `.env` (dev/local) y variables de entorno inyectadas por el
  stack (`docker-compose.yml`, `name: mesa_local`). Es una postura pragmatica
  para un stack de desarrollo local; no hay un gestor de secretos dedicado.
- **Opciones NO adoptadas por ahora** (documentadas, no implementadas):
  - SOPS (cifrado de archivos de secretos en repositorio).
  - Docker secrets (secretos montados por el orquestador de contenedores).
  - Vault (gestor de secretos y KMS con rotacion dinamica).
- La eleccion actual prioriza reproducibilidad del entorno de tesis sobre la
  operacion productiva; adoptar un gestor de secretos es un cambio futuro.

## 5. Prerequisito de despliegue (futuro / organizacional — NO implementado)

Los siguientes controles son un **prerequisito de despliegue productivo** y NO
se presentan como implementados por este repositorio:

- **Gestor de secretos / KMS**: custodia y rotacion automatica de claves.
- **PAM (Privileged Access Management)**: gestion y auditoria de accesos
  privilegiados.
- **CA real de produccion**: emision de material TLS validado por una autoridad
  de certificacion (el stack local usa TLS self-signed).

Su implementacion es responsabilidad de la organizacion adoptante (O) y de los
changes de infraestructura del workstream de cumplimiento. Ver
`docs/security-hardening.md`.

## 6. Runbook: rotacion del secreto JWT (IAH-008)

Keyring aditivo de a lo sumo dos claves (activa + anterior) con ventana de
solapamiento. La firma siempre usa la activa y agrega su `kid`; la verificacion
acepta la anterior y los tokens legacy sin `kid` hasta `JWT_PREVIOUS_KEY_EXPIRES_AT`.

Configuracion (variables relevantes):

| Variable | Rol |
|----------|-----|
| `JWT_SECRET_KEY` | Clave activa (firma) |
| `JWT_KEY_ID` | `kid` de la clave activa (default `v1`) |
| `JWT_PREVIOUS_SECRET_KEY` | Clave anterior (respaldo) |
| `JWT_PREVIOUS_KEY_ID` | `kid` de la clave anterior |
| `JWT_PREVIOUS_KEY_EXPIRES_AT` | Instante ISO-8601 UTC de cierre de la ventana (vacio = sin vencimiento) |

Procedimiento:

1. Generar una clave nueva: `python -c "import secrets; print(secrets.token_urlsafe(32))"`.
2. Mover la clave activa actual a `JWT_PREVIOUS_SECRET_KEY` y su `kid` a
   `JWT_PREVIOUS_KEY_ID`.
3. Poner la clave nueva en `JWT_SECRET_KEY` y actualizar `JWT_KEY_ID`.
4. Fijar `JWT_PREVIOUS_KEY_EXPIRES_AT` con el cierre de la ventana (mayor que la
   vida del access token).
5. Reiniciar el backend. Los tokens vigentes (firmados con la anterior) y los
   legacy sin `kid` siguen validando durante la ventana.
6. Al cerrarse la ventana, los tokens de la clave anterior se rechazan con 401.
   Recien entonces retirar `JWT_PREVIOUS_SECRET_KEY` / `JWT_PREVIOUS_KEY_ID`.

Guardas fail-fast de configuracion (S1/S3):

- `jwt_previous_key_id` DEBE diferir de `jwt_key_id` cuando hay una clave
  anterior configurada; ids iguales hacen la rotacion ambigua y el arranque
  falla con un error de configuracion claro.
- `jwt_previous_key_expires_at`, si no esta vacio, DEBE ser un instante
  ISO-8601 valido; un valor ilegible NO abre una ventana indefinida: el arranque
  falla y, como defensa adicional, el keyring trata la ventana como CERRADA.

Revertir: volver a poner la clave anterior como activa (`JWT_SECRET_KEY`)
revalida los tokens vigentes. Ninguna operacion es irreversible.

## 7. Runbook: rotacion de la clave Fernet (IAH-009)

El backend usa `MultiFernet([activa, anterior?])`: al cifrar usa siempre la
activa; al descifrar prueba el conjunto. La herramienta
`App/Backend/scripts/rotate_fernet_key.py` re-cifra las CUATRO columnas del
inventario (§3) en UNA transaccion y exige un respaldo previo obligatorio.

Procedimiento:

1. Generar la clave nueva:
   `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`.
2. **Tomar un respaldo de la base** (obligatorio). Por ejemplo:
   `pg_dump ... > /ruta/respaldo.dump`. El respaldo debe ser un dump de
   `pg_dump` (formato plano `-- PostgreSQL database dump` o formato custom
   `PGDMP`); el script aborta si no es un dump usable (S2).
3. Configurar el conjunto: la clave nueva en
   `PSEUDONYMIZATION_ENCRYPTION_KEY`, la anterior en
   `PSEUDONYMIZATION_ENCRYPTION_KEY_PREVIOUS`.
4. Ejecutar desde `App/Backend`:
   `python -m scripts.rotate_fernet_key --backup-path /ruta/respaldo.dump`.
5. Confirmar el conteo reportado por columna y que los datos quedan legibles.
6. Recien entonces retirar la clave anterior
   (`PSEUDONYMIZATION_ENCRYPTION_KEY_PREVIOUS` vacia).

Garantias de la herramienta:
- Respaldo previo OBLIGATORIO y USABLE: si falta, no existe, es demasiado
  pequeno o no presenta el marcador de un dump de `pg_dump`, aborta con codigo
  de salida no-cero SIN tocar datos.
- Re-cifrado en UNA transaccion: cualquier fallo revierte todo (sin estado
  parcial).
- Inventario explicito: cubre exactamente las columnas `EncryptedText` (un test
  lo verifica).

Revertir: reponer la clave anterior como activa (o restaurar el respaldo tomado
en el paso 2) deja los datos legibles. La clave anterior se conserva en el
conjunto hasta confirmar el re-cifrado.

## 8. Higiene y verificacion

- Ninguna credencial real en el repositorio. La verificacion de higiene es
  `python3 scripts/security/scan_engram_secrets.py .engram` y el hook
  `.githooks/pre-commit`.
- Rotacion JWT: tests `App/Backend/tests/test_c63c_jwt_rotation.py` (ventana,
  legacy sin `kid`, cota de verificacion).
- Rotacion Fernet: tests `App/Backend/tests/test_c63c_fernet_rotation.py`
  (inventario exhaustivo, respaldo obligatorio, transaccionalidad, reversion).

## 9. Fuentes internas

- `docs/security-hardening.md` — higiene y rotacion de credenciales expuestas.
- `docs/pseudonymization.md` — riesgo de perdida de la clave Fernet.
- `App/Backend/app/core/jwt_keyring.py` — keyring `kid` y ventana.
- `App/Backend/app/utils/encryption.py` — `MultiFernet`.
- `App/Backend/scripts/rotate_fernet_key.py` — herramienta de rotacion.
- `docs/seguridad/README.md` — indice del cuerpo documental.
