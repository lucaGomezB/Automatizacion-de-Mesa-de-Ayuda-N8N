## 1. Red de seguridad y delimitación del alcance

- [x] 1.1 Ejecutar la línea base de las pruebas del Header (`cd App/Frontend; npm run test src/components/layout/Header.test.tsx`) y registrar el conteo en verde. Verificación: el comando reporta la línea base sin fallos preexistentes.
- [x] 1.2 Confirmar que `Header.tsx` NO lee hoy `username` y que `AuthContext` SÍ lo expone. Verificación: `grep -n "useAuth()" App/Frontend/src/components/layout/Header.tsx` no muestra `username`; `grep -n "username" App/Frontend/src/contexts/AuthContext.tsx` muestra el campo en `AuthState`. No se toca el contexto.
- [x] 1.3 Confirmar que `Header.test.tsx` ya mockea `useAuth` y que su helper `authState` incluye `username`. Verificación: la lectura del archivo confirma el mock y el campo.

## 2. Render del nombre de usuario (TDD)

- [x] 2.1 RED: agregar en `App/Frontend/src/components/layout/Header.test.tsx` un bloque `describe` para FSU-003 que afirme que, con un `username` dado (p. ej. `usuario_final`), el Header lo muestra. Verificación: `cd App/Frontend; npm run test src/components/layout/Header.test.tsx` falla contra la implementación vigente (el nombre no se renderiza).
- [x] 2.2 GREEN: en `App/Frontend/src/components/layout/Header.tsx`, agregar `username` al destructuring de `useAuth()` y renderizar el nombre dentro de la zona de sesión con el mínimo cambio para pasar 2.1. Verificación: la prueba de 2.1 pasa.
- [x] 2.3 TRIANGULATE: agregar el caso con `username` nulo (no se renderiza texto de nombre y el botón "Cerrar sesión" sigue presente) y un caso con otro valor de `username` para fijar que el texto mostrado coincide con el provisto por el contexto. Verificación: ambas pruebas pasan sin romper 2.2.

## 3. Ubicación arriba del botón (TDD)

- [x] 3.1 RED: agregar en `Header.test.tsx` una prueba que afirme que el elemento del nombre de usuario precede al control "Cerrar sesión" en el orden del documento dentro de la zona de sesión (p. ej. `compareDocumentPosition` con `Node.DOCUMENT_POSITION_FOLLOWING`, o comparar el orden dentro del contenedor de la zona de sesión). Verificación: la prueba falla si el orden del DOM no pone el nombre antes del botón.
- [x] 3.2 GREEN: ajustar el JSX de `Header.tsx` para que el `span`/`p` del nombre quede ANTES del `<button>` "Cerrar sesión" y la zona de sesión sea una pila vertical (`flex flex-col items-end`) usando utilidades Tailwind v3 (sin sintaxis v4). Verificación: la prueba de 3.1 pasa.
- [x] 3.3 TRIANGULATE: afirmar que, con el nombre presente, el botón "Cerrar sesión" sigue visible y accesible (rol button, nombre /cerrar sesión/i), preservando FSU-001. Verificación: la prueba pasa con las pruebas existentes de cierre de sesión intactas.

## 4. Refactor

- [x] 4.1 REFACTOR: revisar que el nombre del usuario y el botón compartan el contenedor de la zona de sesión sin duplicar condicionales ni clases; mejorar nombres/comentarios si aplica. Verificación: `cd App/Frontend; npm run test src/components/layout/Header.test.tsx` sigue en verde tras cada paso.

## 5. Verificación final

- [x] 5.1 Ejecutar la suite completa del frontend (`cd App/Frontend; npm run test`). Verificación: verde, sin romper las pruebas de navegación por alcance/rol ni las de cierre de sesión (FSU-001).
- [x] 5.2 Ejecutar el linter del frontend (`cd App/Frontend; npm run lint`). Verificación: sin errores.
- [x] 5.3 Ejecutar `openspec validate "c-183-mostrar-el-usuario-logueado-en-la-ui" --strict --no-interactive`. Verificación: PASS.
- [x] 5.4 Confirmar ausencia de cambios de backend: `git diff --name-only` limitado a `App/Frontend/src/components/layout/Header.tsx` y `App/Frontend/src/components/layout/Header.test.tsx`. Verificación: no hay archivos fuera de alcance.

## 6. Deploy (manual)

- [x] 6.1 DEPLOY: reconstruir y reiniciar el frontend en la instancia de campaña (`cd <repo>; docker compose up -d --build frontend`). Verificación: el contenedor del frontend queda healthy.
- [ ] 6.2 Verificación en navegador con HARD REFRESH (Ctrl+Shift+R) para evitar el bundle cacheado: iniciar sesión y comprobar que el Header muestra el nombre del usuario ARRIBA del botón "Cerrar sesión". Verificación: el nombre visible coincide con el usuario autenticado y el orden es nombre arriba, botón abajo. Antecedente: un incidente reciente sirvió una imagen cacheada obsoleta; el hard refresh es obligatorio para descartar el bundle viejo.
