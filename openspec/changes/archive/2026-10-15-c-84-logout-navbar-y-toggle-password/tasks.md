## 1. Preparacion y linea base

- [x] 1.1 Safety net: ejecutar la suite Vitest existente (`npm run test` en `App/Frontend/`) y registrar la linea base de tests en verde antes de tocar archivos
- [x] 1.2 Revisar el test actual de la LoginPage (`src/pages/LoginPage/LoginPage.test.tsx`) para conservar sus queries existentes (`getByLabelText('Contraseña')`) sin regresiones

## 2. Logout en la navegacion global (TDD, FSU-001)

- [x] 2.1 RED: crear `src/components/layout/Header.test.tsx` mockeando `useAuth` (con `alcance.modo = 'PROPIO'`) y `useHealthCheck`, afirmando que el boton "Cerrar sesion" se renderiza aun sin alcance GLOBAL; verificar que falla por no existir el boton
- [x] 2.2 GREEN: en `Header.tsx`, desestructurar `logout` de `useAuth`, agregar `useNavigate` e insertar el boton "Cerrar sesion" (icono `LogOut` + texto) al final de la columna derecha, siempre renderizado; verificar 2.1 en verde
- [x] 2.3 RED/GREEN: extender `Header.test.tsx` para afirmar que accionar el boton invoca `logout()` y navega a `/login` (usar `MemoryRouter` + un consumidor de ruta o mock de `useNavigate`); verificar que falla y luego pasa
- [x] 2.4 TRIANGULAR: casos con `alcance.modo` GLOBAL y PROPIO (el boton aparece en ambos); verificar que los casos pasan
- [x] 2.5 Verificar que la logica de autenticacion no cambio: el Header solo invoca `logout()`, sin logica nueva (`git diff` sobre `AuthContext.tsx` debe estar vacio)

## 3. Toggle de visibilidad de contrasena (TDD, FSU-002)

- [x] 3.1 RED: extender `LoginPage.test.tsx` afirmando que el input de contrasena tiene `type="password"` por defecto y que existe un boton accesible con `aria-label` "Mostrar contraseña"; verificar que falla
- [x] 3.2 GREEN: agregar estado local `showPassword` (default `false`) en `LoginPage/index.tsx` y renderizar el input con `type={showPassword ? 'text' : 'password'}`; verificar 3.1 en verde
- [x] 3.3 GREEN: agregar el control de ojo (`button` `type="button"`, `Eye`/`EyeOff`, `aria-label` dinamico) dentro de un contenedor `relative` del input; verificar que 3.1 pasa
- [x] 3.4 RED/GREEN: extender el test afirmando que al accionar el control el input pasa a `type="text"` y el `aria-label` cambia a "Ocultar contraseña"; verificar que falla y luego pasa
- [x] 3.5 TRIANGULAR: alternar dos veces vuelve a `type="password"`; y el valor enviado a `login()` es la contrasena tipeada sin transformaciones; verificar que los casos pasan
- [x] 3.6 Verificar que la logica de login no cambio: no se modifica la firma ni el llamado a `login()`/`verifyMfa()`

## 4. Verificacion integral

- [x] 4.1 Ejecutar `npm run lint`, `npm run test` y `npm run build` en `App/Frontend/` y verificar que todo pasa
- [x] 4.2 Verificar cobertura de los escenarios FSU-001 y FSU-002 con tests y correr `openspec validate c-84-logout-navbar-y-toggle-password --strict`
