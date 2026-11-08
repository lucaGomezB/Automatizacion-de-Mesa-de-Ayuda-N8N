# frontend-session-ui Specification

## Purpose

Define el chrome de sesión del frontend: las affordances de interfaz ligadas a la sesión del usuario — cerrar sesión desde la navegación global y controlar la visibilidad de la contraseña en el acceso — sin alterar la lógica de autenticación.

## Requirements

### Requirement: FSU-001 — Cierre de sesión desde la navegación global

El Header global SHALL renderizar un control de "Cerrar sesión" ubicado al extremo derecho de la barra de navegación, después del indicador de salud de la API. El control SHALL ser visible para TODO usuario autenticado, con independencia de su `alcance.modo` (GLOBAL, PROPIO o cualquier otro). Al accionarlo, SHALL invocar la función `logout()` ya existente del contexto de autenticación y luego navegar a `/login`. El control NO SHALL introducir lógica de autenticación nueva: reutiliza exclusivamente el `logout()` existente.

#### Scenario: Todo usuario autenticado ve el control de cierre de sesión

- **WHEN** un usuario autenticado carga cualquier página con el Header global, sin importar su `alcance.modo` (GLOBAL o PROPIO)
- **THEN** el Header muestra el control "Cerrar sesión" al extremo derecho de la barra

#### Scenario: La visibilidad del control no depende del alcance

- **WHEN** el usuario autenticado tiene `alcance.modo` distinto de GLOBAL
- **THEN** el control "Cerrar sesión" sigue renderizándose (a diferencia del indicador de salud de la API, que solo aparece en GLOBAL)

#### Scenario: Accionar el control cierra la sesión y navega al login

- **WHEN** el usuario autenticado acciona el control "Cerrar sesión"
- **THEN** el sistema invoca el `logout()` existente del contexto de autenticación y navega a `/login`

### Requirement: FSU-002 — Control de visibilidad de la contraseña en el acceso

El campo de contraseña del formulario de login SHALL incluir un control para mostrar u ocultar la contraseña tipeada. La contraseña SHALL estar oculta por defecto (`type="password"`); tras alternar el control, el campo SHALL pasar a `type="text"` y viceversa. El control SHALL ser accesible: un `button` real con un `aria-label` que refleje su estado (por ejemplo "Mostrar contraseña" / "Ocultar contraseña"), operable por teclado. El control NO SHALL alterar la lógica de login ni el manejo de credenciales: solo la presentación del input.

#### Scenario: La contraseña está oculta por defecto

- **WHEN** el usuario carga la página de login
- **THEN** el campo de contraseña tiene `type="password"` y una contraseña tipeada no es visible

#### Scenario: Alternar el control muestra la contraseña

- **WHEN** el usuario acciona el control de visibilidad con la contraseña oculta
- **THEN** el campo pasa a `type="text"` y el `aria-label` del control refleja el nuevo estado ("Ocultar contraseña")

#### Scenario: Alternar el control vuelve a ocultar la contraseña

- **WHEN** el usuario acciona el control de visibilidad con la contraseña visible
- **THEN** el campo vuelve a `type="password"` y el `aria-label` del control refleja el estado oculto ("Mostrar contraseña")

#### Scenario: El control es accesible y operable por teclado

- **WHEN** el usuario navega con el teclado hasta el control de visibilidad y lo activa
- **THEN** el control es un `button` con `aria-label` descriptivo y responde a la activación por teclado

#### Scenario: La lógica de credenciales no cambia

- **WHEN** el usuario alterna la visibilidad de la contraseña y luego envía el formulario
- **THEN** el valor enviado a la lógica de login es la misma contraseña tipeada, sin transformaciones

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
