## ADDED Requirements

### Requirement: FSU-003 — Identidad del usuario autenticado en el Header global

El Header global SHALL mostrar el nombre del usuario autenticado (`username`) dentro de la zona de sesión, ubicada al extremo derecho de la barra de navegación. El nombre SHALL renderizarse ARRIBA del control "Cerrar sesión" (FSU-001), de modo que la zona de sesión sea una pila vertical: la línea del nombre de usuario en la parte superior y el botón "Cerrar sesión" debajo. El nombre SHALL provenir exclusivamente del campo `username` ya expuesto por `useAuth()`; el Header NO SHALL introducir lógica de autenticación nueva ni realizar llamadas adicionales al backend para obtener la identidad. Cuando `username` es `null` (identidad aún no resuelta), el Header NO SHALL renderizar una línea de nombre vacía ni un placeholder ambiguo. Este requisito NO altera FSU-001: el control "Cerrar sesión" conserva su comportamiento y su posición al extremo derecho de la barra.

#### Scenario: El usuario autenticado ve su nombre en el Header

- **WHEN** un usuario autenticado con `username` no nulo carga cualquier página con el Header global
- **THEN** el Header muestra su nombre de usuario en la zona de sesión

#### Scenario: El nombre se ubica arriba del control "Cerrar sesión"

- **WHEN** el Header renderiza la zona de sesión con un `username` no nulo
- **THEN** el elemento del nombre de usuario precede al control "Cerrar sesión" en el orden del documento dentro de la zona de sesión, quedando visualmente por encima del botón

#### Scenario: Sin identidad resuelta no se renderiza un nombre vacío

- **WHEN** el `username` del contexto de autenticación es `null`
- **THEN** el Header no renderiza ninguna línea de nombre de usuario y el control "Cerrar sesión" sigue visible

#### Scenario: La identidad no introduce lógica de autenticación nueva

- **WHEN** el Header renderiza el nombre del usuario autenticado
- **THEN** lo obtiene del `username` ya presente en `useAuth()`, sin llamadas adicionales al backend ni cambios en la lógica de login o de cierre de sesión
