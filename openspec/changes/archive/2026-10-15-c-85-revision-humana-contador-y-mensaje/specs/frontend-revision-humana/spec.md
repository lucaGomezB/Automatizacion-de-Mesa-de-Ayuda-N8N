## ADDED Requirements

### Requirement: FRH-008 — El contador de la pestaña refleja el total real de pendientes del alcance

La pestaña "Revisión Humana" SHALL mostrar como badge el TOTAL REAL de clasificaciones pendientes de revisión visibles para el alcance del usuario autenticado, y MUST NOT quedar acotado al tamaño de una página de resultados. El conteo SHALL respetar el mismo alcance de visibilidad que la cola (VIS-002): un alcance GLOBAL (`administrador_directorio`, `mesa_de_ayuda`) cuenta toda la cola; un alcance PROPIO (`usuario_final`) cuenta únicamente los pendientes cuyo incidente reportó; un alcance vacío cuenta cero. El badge SHALL ocultarse cuando el total es cero.

#### Scenario: El contador supera una página de resultados

- **WHEN** existen 50 o más clasificaciones pendientes dentro del alcance del usuario
- **THEN** el badge de la pestaña muestra el total real de pendientes, no 50

#### Scenario: El contador respeta el alcance propio

- **WHEN** un usuario con alcance PROPIO consulta la pestaña y solo una parte de la cola pertenece a los incidentes que reportó
- **THEN** el badge muestra únicamente la cantidad de pendientes dentro de su alcance

#### Scenario: Sin pendientes en el alcance no hay badge

- **WHEN** el alcance del usuario no tiene clasificaciones pendientes
- **THEN** el badge de la pestaña no se muestra

### Requirement: FRH-009 — La cola de revisión es paginable y no se trunca silenciosamente

La tabla de revisión humana SHALL permitir al operador navegar por TODAS las clasificaciones pendientes de su alcance, y MUST NOT exponer solo la primera página sin ofrecer acceso al resto. El frontend SHALL solicitar la cola por páginas (`limit`/`offset`) y SHALL ofrecer un control de paginación que permita avanzar y retroceder cuando existan más resultados que una página. La disponibilidad de páginas adicionales SHALL derivarse del total real de pendientes.

#### Scenario: Navegar más allá de la primera página

- **WHEN** el total de pendientes supera el tamaño de página y el operador acciona el control de paginación
- **THEN** la tabla muestra la siguiente página de clasificaciones pendientes

#### Scenario: No hay páginas adicionales cuando el total cabe en una página

- **WHEN** el total de pendientes es menor o igual al tamaño de página
- **THEN** el control de paginación no ofrece avanzar a una página siguiente

#### Scenario: Validar en la última página deja la vista coherente

- **WHEN** el operador valida la última clasificación de una página y esa página queda vacía
- **THEN** la vista regresa a una página con resultados o muestra el estado de cola vacía, sin una tabla vacía engañosa

### Requirement: FRH-010 — El aviso de criterio no referencia un modelo retirado

El aviso explicativo de la pestaña "Revisión Humana" SHALL describir el criterio de derivación (confianza inferior al umbral de revisión humana, 70%) y MUST NOT afirmar que el umbral fue definido por un modelo retirado. El texto SHALL ser agnóstico al modelo de lenguaje concreto, de modo que un cambio de modelo no lo deje obsoleto. El texto SHALL redactarse en español técnico neutro, sin emojis.

#### Scenario: El aviso no menciona un modelo retirado

- **WHEN** el operador abre la pestaña "Revisión Humana"
- **THEN** el aviso muestra el criterio del umbral de revisión humana sin mencionar "Gemini 2.5 Flash" ni ningún otro modelo de lenguaje por nombre

#### Scenario: El aviso comunica el umbral vigente

- **WHEN** el operador lee el aviso
- **THEN** el aviso indica que se listan los incidentes clasificados con confianza inferior al 70%
