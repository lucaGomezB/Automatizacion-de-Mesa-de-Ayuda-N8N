## MODIFIED Requirements

### Requirement: ASG-005 — Persistencia de los conjuntos predicho y validado del log de clasificacion

El log de clasificacion SHALL soportar los conjuntos multietiqueta de sectores predichos y validados, ademas del sector principal predicho y validado. La validacion humana SHALL poder registrar el conjunto validado de sectores del caso y MUST NOT perder los sectores adicionales al confirmar o corregir una clasificacion. Ademas, cada intervencion humana SHALL registrar en el log sus metadatos: el ACTOR (`validado_por_empleado_id`, referencia nullable al empleado del directorio, sin PII en claro, que queda nula cuando la cuenta no tiene empleado vinculado), el INICIO declarado de la intervencion (`intervencion_inicio_en`, opcional), un INSTANTE de validacion propio del servidor (`validado_en`), distinguible del `created_at` del log, y el ORIGEN (`origen_intervencion`, uno de `gate`, `muestreo`, `rederivacion`, `completado_manual`). La validacion desde `PATCH /clasificaciones/{log_id}/validar` SHALL aceptar `intervencion_inicio_en` opcional y MUST rechazar con 422 un payload que traiga `origen_intervencion`: el origen lo deriva SIEMPRE el backend, como `gate` cuando el log tiene `requiere_revision_humana` y como `muestreo` cuando no. Un cambio de sector del incidente por `PATCH /incidentes/{id}` SHALL registrarse en el log mas reciente del incidente con origen `rederivacion`. El valor `completado_manual` queda reservado y sin escritor. Ante una re-validacion SHALL prevalecer la ultima escritura, incluido el reemplazo del conjunto validado aunque llegue vacio. El DELTA de sector antes/despues SHALL ser reconstruible desde el predicho y el validado, y la ausencia de intervencion MUST permanecer representable como estado no intervenido, distinto del estado legado de un log validado sin metadatos.

#### Scenario: Log guarda el conjunto predicho

- **WHEN** se registra una clasificacion con sector principal y sectores adicionales predichos
- **THEN** el log conserva el sector principal y el conjunto completo de sectores predichos

#### Scenario: Validacion humana registra el conjunto validado

- **WHEN** un operador valida o corrige una clasificacion indicando sectores adicionales
- **THEN** el log conserva el conjunto validado de sectores y el incidente refleja la correccion

#### Scenario: La intervencion persiste actor instante origen e inicio

- **WHEN** un operador con empleado vinculado valida una clasificacion enviando `intervencion_inicio_en`
- **THEN** el log persiste el id del empleado actor, el inicio enviado, un `validado_en` del servidor distinto de `created_at` y el origen de la intervencion, sin exponer email ni telefono en claro

#### Scenario: Actor nulo sin empleado vinculado

- **WHEN** una cuenta autenticada sin empleado vinculado valida una clasificacion
- **THEN** la validacion se registra, `validado_por_empleado_id` queda nulo y `validado_en` y `origen_intervencion` se persisten igual

#### Scenario: Origen derivado por el backend

- **WHEN** se valida un log con `requiere_revision_humana` verdadero y otro log con `requiere_revision_humana` falso
- **THEN** el primero queda con origen `gate` y el segundo con origen `muestreo`

#### Scenario: Origen enviado por el cliente rechazado

- **WHEN** el payload de validacion trae `origen_intervencion`, con un valor del vocabulario como `gate` o con uno ajeno como `review`
- **THEN** la API responde 422 sin reflejar el valor sometido y el log no se modifica

#### Scenario: Rederivacion desde PATCH de incidentes

- **WHEN** se actualiza un incidente por `PATCH /incidentes/{id}` con un `sector_id` distinto del actual
- **THEN** el log mas reciente del incidente registra el nuevo sector validado, `validado_en`, el actor o nulo y el origen `rederivacion`, y un PATCH sin cambio de sector no registra intervencion

#### Scenario: Re-validacion gana la ultima escritura

- **WHEN** un log ya validado se valida de nuevo con otro sector y `sectores_adicionales` vacio
- **THEN** el log conserva solo los metadatos, el sector validado y el conjunto validado de la ultima validacion, y el conjunto validado queda vacio

#### Scenario: completado_manual sin escritor

- **WHEN** se recorren los flujos que escriben `origen_intervencion` en este cambio
- **THEN** ninguno escribe `completado_manual`, que queda declarado como valor reservado sin escritor

#### Scenario: El delta de sector antes y despues queda registrado

- **WHEN** la validacion humana confirma o cambia el sector del caso
- **THEN** el log permite reconstruir el sector predicho y el validado (principal y adicionales) como delta antes/despues

#### Scenario: Un caso sin intervencion no inventa metadatos

- **WHEN** un log aun no fue validado por ningun operador
- **THEN** el log permanece en estado no intervenido, sin actor, inicio, instante de validacion ni origen ficticios

#### Scenario: Un log validado antes de la migracion queda como legado

- **WHEN** un log tiene sector validado pero `validado_en` nulo porque fue validado antes de existir los metadatos
- **THEN** se clasifica como intervencion legada sin metadatos y no se le asigna un instante ni un origen retroactivos
