## 0. Baseline, dependencias e inventario (pre-apply)

- [ ] 0.1 Verificar que `c-63a` (JWT de vida corta, refresco y revocacion) y `c-63b` (secreto TOTP cifrado con Fernet) estan aplicados o acordados como interfaz; registrar el contrato consumido y verificar que no hay conflicto con el keyring `kid`.
- [ ] 0.2 Capturar la linea base: ejecutar `cd App/Backend; pytest -m "not integration"` y registrar el conteo de tests que pasan (red de seguridad).
- [ ] 0.3 Producir el **inventario exacto** de columnas cifradas con Fernet verificando `EncryptedText` en `App/Backend/app/models/`: enumerar tabla, columna, nulabilidad y sensibilidad, y confirmar que incluye `incidente.descripcion_original`, `telefonia_ingreso.caller_cifrado` y `telefonia_ingreso.transcript_original` (artefacto del inventario).
- [ ] 0.4 Registrar el inventario de secretos del sistema (secreto JWT, clave Fernet y los ya existentes de la plataforma) como insumo del runbook.
- [ ] 0.5 Resolver OQ-C1 con el autor (alcance del respaldo/re-cifrado sobre las tres columnas Fernet) y registrarlo en `design.md` antes de escribir el script.

## 1. Rotacion del secreto JWT — keyring `kid` (IAH-008)

- [ ] 1.1 Escribir los tests de rotacion JWT (token con clave anterior aceptado en la ventana, rechazado tras la ventana, token legacy sin `kid` aceptado en la transicion) y verificar que fallan (RED).
- [ ] 1.2 Agregar los parametros del keyring en `settings.py` (`jwt_key_id`, `jwt_previous_secret_key`, `jwt_previous_key_id`, `jwt_previous_key_expires_at`) con defaults retrocompatibles, y documentarlos en `.env.example`; verificar que la configuracion actual sigue construyendo sin cambios.
- [ ] 1.3 Implementar la firma con la clave activa + `kid` en `auth_service.py` y la verificacion acotada en `core/security.py` (activa -> anterior si la ventana esta abierta; legacy sin `kid` prueba activa y anterior) y verificar que los tests de 1.1 pasan (GREEN).
- [ ] 1.4 Triangular con casos borde: ventana vencida al segundo, `kid` desconocido y token sin `kid` con solo clave activa; verificar que la verificacion no intenta claves fuera del keyring.
- [ ] 1.5 Verificar con el test de contrato existente que `POST /api/v1/auth/login` y `test_auth.py` siguen verdes sin cambios de entorno.

## 2. Rotacion de la clave Fernet — `MultiFernet` y script (IAH-009)

- [ ] 2.1 Agregar `pseudonymization_encryption_key_previous` (default vacio) en `settings.py` y `.env.example`; verificar que sin clave anterior el comportamiento es el actual.
- [ ] 2.2 Escribir los tests de rotacion Fernet (dato cifrado con la clave anterior se descifra; dato re-cifrado queda legible con la nueva; fallo a mitad revierte sin estado parcial) y verificar que fallan (RED).
- [ ] 2.3 Implementar `MultiFernet([activa, anterior?])` en `utils/encryption.py` con cache invalidado por el conjunto de claves y verificar que los tests de 2.2 pasan (GREEN).
- [ ] 2.4 Escribir los tests del script de rotacion (exige respaldo previo y aborta sin el; re-cifra solo las columnas del inventario; reporta conteo) y verificar que fallan (RED).
- [ ] 2.5 Implementar `App/Backend/scripts/rotate_fernet_key.py`: respaldo previo obligatorio, re-cifrado en UNA transaccion, columnas enumeradas desde el inventario, y verificacion de conteo; verificar que los tests de 2.4 pasan (GREEN).
- [ ] 2.6 Triangular con un test de revertibilidad: reponer la clave anterior como activa permite descifrar los datos respaldados y no deja filas ilegibles.

## 3. Higiene y gestion de secretos (IAH-010)

- [ ] 3.1 Crear `docs/seguridad/gestion-secretos-y-rotacion.md` con el inventario de secretos y el runbook de rotacion (JWT y Fernet), cruzado con `docs/security-hardening.md` y `docs/pseudonymization.md`; verificar que el documento existe y referencia ambos procesos.
- [ ] 3.2 Documentar la postura `.env`/variables como fuente actual y SOPS, Docker secrets y Vault como opciones no adoptadas; verificar que quedan listadas como no adoptadas.
- [ ] 3.3 Documentar KMS/Vault, PAM y CA real como prerequisito de despliegue (futuro/organizacional); verificar que se encuadran como no implementados.
- [ ] 3.4 Ejecutar la verificacion de higiene (`python3 scripts/security/scan_engram_secrets.py .engram` y el hook pre-commit si aplica) y verificar que no hay hallazgos sin resolver.

## 4. Documentacion organizacional 5.16 / 5.18 (IAH-011)

- [ ] 4.1 Documentar en `docs/seguridad/` el ciclo de vida de identidades (alta, cambio y baja) como responsabilidad de la organizacion adoptante (5.16), marcado como control (O).
- [ ] 4.2 Documentar en `docs/seguridad/` el proceso y la periodicidad de aprobacion/revision de derechos de acceso (5.18), marcado como control (O).
- [ ] 4.3 Actualizar `docs/seguridad/README.md` para referenciar los documentos de 5.16/5.18 y el documento de gestion de secretos; verificar que las referencias cruzadas resuelven a archivos existentes.

## 5. Verificacion final

- [ ] 5.1 Verificar de forma explicita las dos rotaciones mediante sus tests dedicados (JWT: ventana y legacy; Fernet: descifrado previo, re-cifrado, revertibilidad).
- [ ] 5.2 Ejecutar la suite backend completa (`cd App/Backend; pytest`), incluido el subconjunto `integration`, y verificar que pasa.
- [ ] 5.3 Ejecutar la suite frontend (`cd App/Frontend; npm run test`) y verificar que pasa sin cambios.
- [ ] 5.4 Verificar que el flujo de desarrollo documentado sigue funcionando (`admin`/`admin123`, `directorio.admin`) con los defaults retrocompatibles del keyring y de Fernet.
- [ ] 5.5 Ejecutar `openspec validate c-63c-rotacion-claves-secretos --strict` y verificar que pasa.
