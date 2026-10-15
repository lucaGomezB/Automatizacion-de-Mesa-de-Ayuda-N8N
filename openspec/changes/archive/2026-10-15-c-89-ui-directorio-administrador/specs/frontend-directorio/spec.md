## Purpose

Ofrece al `administrador_directorio` una superficie en el frontend para operar el directorio de empleados (alta, listado, edicion, activar/desactivar, borrado ARCO y purga por retencion) consumiendo la API existente, con una experiencia coherente con el resto de la aplicacion.

## ADDED Requirements

### Requirement: FDIR-001 — Superficie del directorio accesible solo al administrador

El sistema SHALL ofrecer una pagina en la ruta `/directorio` para gestionar el directorio de empleados. El acceso SHALL estar restringido al usuario autenticado cuyo ROL sea `administrador_directorio`; el modo de alcance por si solo NO SHALL habilitar la ruta, porque `mesa_de_ayuda` tambien tiene alcance `GLOBAL`. Un usuario con rol distinto SHALL ser redirigido sin exponer acciones de gestion. El control de acceso de la interfaz SHALL ser de experiencia de usuario: el backend sigue siendo la frontera de seguridad.

#### Scenario: El administrador del directorio accede

- **WHEN** un usuario autenticado con rol `administrador_directorio` navega a `/directorio`
- **THEN** la UI admite la ruta y habilita las operaciones de gestion del directorio

#### Scenario: Un rol GLOBAL distinto es redirigido

- **WHEN** un usuario autenticado con rol `mesa_de_ayuda` (alcance `GLOBAL`) navega a `/directorio`
- **THEN** la UI lo redirige sin exponer el listado ni las acciones del directorio

#### Scenario: Un rol sin gestion es redirigido

- **WHEN** un usuario autenticado con rol `usuario_final` (alcance `PROPIO`) navega a `/directorio`
- **THEN** la UI lo redirige sin exponer el listado ni las acciones del directorio

#### Scenario: El acceso anonimo redirige a login

- **WHEN** una cuenta no autenticada intenta navegar a `/directorio`
- **THEN** la UI la redirige a `/login`

#### Scenario: El backend sigue siendo la frontera

- **WHEN** el backend responde 403 ante una operacion del directorio por rol no autorizado
- **THEN** la UI presenta un estado de acceso denegado sin exponer datos ni asumir acceso

### Requirement: FDIR-002 — Listado del directorio con filtro activo/inactivo

La pagina SHALL listar los empleados del directorio consumiendo `GET /api/v1/directorio/empleados`. SHALL ofrecer un filtro de estado con dos opciones: todos (por defecto) y solo activos, que se traduce al parametro `solo_activos` del endpoint. Cada fila SHALL mostrar al menos legajo, nombre, email, sector, rol y estado (activo/inactivo). La vista SHALL presentar estados de carga, error (con reintento) y vacio consistentes con el resto de la aplicacion.

#### Scenario: Listar todos los empleados

- **WHEN** el administrador abre `/directorio` con el filtro en "todos"
- **THEN** la UI lista los empleados activos e inactivos devueltos por el backend

#### Scenario: Filtrar solo activos

- **WHEN** el administrador selecciona el filtro "solo activos"
- **THEN** la UI consulta el endpoint con `solo_activos=true` y lista unicamente empleados activos

#### Scenario: Directorio sin resultados

- **WHEN** el backend devuelve una lista vacia para el filtro seleccionado
- **THEN** la UI muestra un estado vacio con un mensaje explicativo

#### Scenario: Error de carga

- **WHEN** la consulta del listado falla
- **THEN** la UI muestra un estado de error con una accion de reintento

### Requirement: FDIR-003 — Alta de empleado con rol y sector

La pagina SHALL permitir crear un empleado del directorio mediante `POST /api/v1/directorio/empleados`. El formulario SHALL capturar legajo, nombre, email (obligatorios), telefono (opcional) y rol, seleccionado de un catalogo que incluya `usuario_final`, `mesa_de_ayuda`, `administrador_directorio` y `gestion_incidentes`. El formulario SHALL mostrar un selector de sector y exigirlo cuando el rol seleccionado requiera sector (el rol `gestion_incidentes`); para los demas roles el sector SHALL ser opcional. El frontend SHALL validar los campos obligatorios y el formato del email antes de enviar, y SHALL mostrar el error del backend cuando este rechace el alta.

#### Scenario: Alta exitosa de un empleado

- **WHEN** el administrador completa legajo, nombre, email y un rol valido y confirma
- **THEN** la UI envia el alta al endpoint y, ante 201, refleja el nuevo empleado en el listado

#### Scenario: El rol que requiere sector exige sector

- **WHEN** el administrador selecciona el rol `gestion_incidentes`
- **THEN** el formulario marca el sector como obligatorio y bloquea el envio hasta que se seleccione

#### Scenario: Rol sin requisito de sector permite sector opcional

- **WHEN** el administrador selecciona un rol que no requiere sector
- **THEN** el formulario permite enviar el alta sin sector

#### Scenario: Email invalido o faltante bloquea el envio

- **WHEN** el administrador intenta enviar el alta con email vacio o con formato invalido
- **THEN** la UI no envia la solicitud y muestra el error de validacion del campo

#### Scenario: El backend rechaza el alta

- **WHEN** el backend rechaza el alta (por ejemplo email o legajo duplicado)
- **THEN** la UI muestra el mensaje de error devuelto sin perder los datos ingresados

### Requirement: FDIR-004 — Edicion y activar/desactivar empleados

La pagina SHALL permitir editar los campos de un empleado existente mediante `PATCH /api/v1/directorio/empleados/{id}`, reutilizando el mismo formulario en modo edicion. SHALL permitir desactivar y reactivar un empleado, enviando `activo=false` o `activo=true` en el mismo endpoint. Tras una mutacion exitosa, la UI SHALL refrescar el listado.

#### Scenario: Edicion exitosa

- **WHEN** el administrador modifica datos de un empleado y confirma
- **THEN** la UI envia el cambio parcial y, ante exito, el listado refleja los datos actualizados

#### Scenario: Desactivar un empleado

- **WHEN** el administrador desactiva un empleado activo
- **THEN** la UI envia `activo=false` y el empleado pasa a mostrarse como inactivo

#### Scenario: Reactivar un empleado

- **WHEN** el administrador reactiva un empleado inactivo
- **THEN** la UI envia `activo=true` y el empleado pasa a mostrarse como activo

### Requirement: FDIR-005 — Borrado ARCO con confirmacion

La pagina SHALL permitir el borrado fisico por solicitud ARCO mediante `DELETE /api/v1/directorio/empleados/{id}`, precedido SIEMPRE por una confirmacion explicita que advierta que la accion es irreversible. Tras el exito, la UI SHALL refrescar el listado.

#### Scenario: El borrado exige confirmacion

- **WHEN** el administrador solicita borrar un empleado
- **THEN** la UI muestra una confirmacion que advierte que el borrado es irreversible antes de enviar la solicitud

#### Scenario: El administrador cancela el borrado

- **WHEN** el administrador cancela la confirmacion
- **THEN** la UI no envia la solicitud y el empleado permanece sin cambios

#### Scenario: Borrado confirmado

- **WHEN** el administrador confirma el borrado
- **THEN** la UI envia la solicitud y, ante exito, el empleado deja de aparecer en el listado

### Requirement: FDIR-006 — Purga por retencion con confirmacion

La pagina SHALL permitir disparar la purga manual por retencion mediante `POST /api/v1/directorio/purga`, precedida SIEMPRE por una confirmacion explicita. Ante el exito, la UI SHALL mostrar la cantidad de registros purgados devuelta por el backend y refrescar el listado.

#### Scenario: La purga exige confirmacion

- **WHEN** el administrador solicita disparar la purga
- **THEN** la UI muestra una confirmacion antes de enviar la solicitud

#### Scenario: Purga exitosa muestra el conteo

- **WHEN** el administrador confirma la purga y el backend responde con el conteo de registros purgados
- **THEN** la UI informa al administrador la cantidad purgada y refresca el listado
