## 0. Baseline y resolucion de decisiones (pre-apply)

- [ ] 0.1 Resolver OQ-B1 y OQ-B2 por decision del autor y registrarlas en `design.md`, verificando que cada OQ queda marcada como resuelta antes de tocar codigo.
- [ ] 0.2 Capturar la linea base de pruebas: ejecutar `cd App/Backend; pytest -m "not integration"` y `cd App/Frontend; npm run test`, y registrar el conteo de tests que pasan (red de seguridad).
- [ ] 0.3 Confirmar que la suite de linea base esta verde; si hay fallas preexistentes, reportarlas sin corregirlas.
- [ ] 0.4 Inventariar los consumidores del contrato de login (`App/Backend/app/routes/auth.py`, `App/Backend/app/services/auth_service.py`, `App/Backend/app/schemas/auth.py`, `App/Frontend/src/contexts/AuthContext.tsx`, `App/Frontend/src/services/api.ts`) y verificar que el listado cubre todos los usos.

## 1. Rol privilegiado a nivel identidad (IAH-005)

- [ ] 1.1 Agregar la migracion alembic de `is_privileged` (`bool`, default `false`, `nullable=False`) con el `UPDATE` que marca `admin` privilegiado, y verificar que `alembic upgrade head` y `downgrade` corren sin error.
- [ ] 1.2 Escribir los tests de privilegio (admin privilegiado, cuenta vinculada a rol privilegiado, `usuario_final` no privilegiado, cuenta nueva con default falso) y verificar que fallan (RED).
- [ ] 1.3 Implementar el campo y el marcado al crear/actualizar el vinculo segun OQ-B1 (con derivacion defensiva en el chequeo) y verificar que los tests de 1.2 pasan (GREEN).
- [ ] 1.4 Triangular con desvinculacion (`user_id = NULL`) y cambio de rol privilegiado a `usuario_final`, y verificar que `is_privileged` cubre todos los escenarios de IAH-005.

## 2. Servicio MFA TOTP (IAH-006)

- [ ] 2.1 Agregar la migracion de los campos MFA (`totp_secret`, `totp_enabled`, codigos de recuperacion) y verificar upgrade/downgrade.
- [ ] 2.2 Escribir los tests de MFA (enrollment entrega URI `otpauth`, TOTP valido verifica, TOTP invalido/expirado rechaza, codigo de recuperacion de un solo uso, secreto no almacenado en claro, bandera apagada no exige MFA) y verificar que fallan (RED).
- [ ] 2.3 Implementar `App/Backend/app/services/mfa_service.py` (enrollment, verificacion RFC 6238, codigos de recuperacion bcrypt, secreto cifrado at-rest reutilizando `utils/encryption.py`) y verificar que los tests de 2.2 pasan (GREEN).
- [ ] 2.4 Triangular con codigo en el borde de la ventana, reuso de un codigo de recuperacion ya consumido y formato del URI, y verificar que cubre todos los escenarios de IAH-006.
- [ ] 2.5 Exponer en `settings.py`/`.env.example` la bandera `mfa_required_for_privileged` (default `false`), el TTL del ticket, el issuer y la cantidad de codigos, y verificar que los defaults no rompen los seeds de desarrollo.

## 3. Login en dos pasos y endpoints MFA (IAH-007)

- [ ] 3.1 Escribir los tests del flujo en dos pasos (privilegiada recibe reto sin token, verify con segundo factor valido emite `access_token`/`token_type`, ticket invalido/expirado rechazado, no privilegiada en un paso, bandera apagada con `admin` en un paso) y verificar que fallan (RED).
- [ ] 3.2 Implementar los schemas aditivos, los endpoints `POST /auth/mfa/enroll` y `POST /auth/mfa/verify`, y el login en dos pasos, y verificar que los tests de 3.1 pasan (GREEN).
- [ ] 3.3 Triangular con un ticket de `scope` incorrecto rechazado en rutas protegidas y con un ticket expirado, y verificar que cubre todos los escenarios de IAH-007.
- [ ] 3.4 Verificar de forma explicita la compatibilidad aditiva del contrato: `POST /auth/login` sigue devolviendo `access_token` y `token_type` (test de contrato).

## 4. Frontend reto MFA (IAH-007)

- [ ] 4.1 Escribir los tests de frontend del reto (respuesta `mfa_required` muestra el paso de verificacion, codigo valido completa el login, primer acceso muestra el enrollment) y verificar que fallan (RED).
- [ ] 4.2 Adaptar `AuthContext.tsx`, `services/api.ts` y la pantalla de login al reto MFA y al enrollment, y verificar que los tests de 4.1 pasan (GREEN).
- [ ] 4.3 Triangular con el caso de codigo invalido (muestra error y no autentica) y verificar que la suite de frontend pasa.

## 5. Verificacion final

- [ ] 5.1 Verificar de forma explicita la seguridad: privilegio derivado, reto MFA, TOTP valido/invalido, recuperacion y bandera apagada, mediante sus tests dedicados.
- [ ] 5.2 Ejecutar la suite backend completa (`cd App/Backend; pytest`) incluyendo el subconjunto `integration`, y verificar que pasa.
- [ ] 5.3 Ejecutar la suite frontend (`cd App/Frontend; npm run test`) y verificar que pasa.
- [ ] 5.4 Verificar el flujo de desarrollo documentado con la bandera apagada (`admin`/`admin123`, `directorio.admin`, dry-run).
- [ ] 5.5 Documentar `mfa_required_for_privileged` como requisito de despliegue en produccion y verificar que queda documentado.
- [ ] 5.6 Ejecutar `openspec validate c-63b-mfa-y-rol-privilegiado --strict` y verificar que pasa.
