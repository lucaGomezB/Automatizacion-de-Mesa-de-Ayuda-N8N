## ADDED Requirements

### Requirement: Registro del contraste de la hipótesis subsidiaria de integración multicanal con el test de carga

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL registrar el contraste de capacidad de la integración multicanal en una sección nueva y aditiva (sección `3.29`), posterior a la `3.28` vigente (de c-217), con procedencia por valor (archivo y ruta del reporte JSON del arnés de carga) y estado en `{vigente, retirado, condicional}`. La sección SHALL registrar: el entorno (perfil `corpus` desechable, costo cero), las constantes prerregistradas del criterio (niveles de concurrencia, techo de p95, tolerancia de throughput), las métricas por nivel (p50, p95, p99, media, throughput y tasa de error) para el punto de convergencia del backend y para el webhook web de N8N, el veredicto de tres vías y los límites declarados (medición en una sola máquina, camino determinístico sin inferencia paga, complejidad percibida no instrumentada). MUST NOT modificar ningún valor ni estado de las secciones `3.1` a `3.28`; las frases previas que declaran la hipótesis multicanal «sin contrastar» SHALL quedar superadas por remisión a la sección nueva, sin borrar ni reescribir su contenido.

#### Scenario: Sección aditiva con procedencia

- **WHEN** se recorre la sección `3.29` del memo
- **THEN** cada valor declara su archivo y ruta de origen y un estado en `{vigente, retirado, condicional}`
- **AND** la sección aparece después de la `3.28` sin renumerar ni alterar las secciones anteriores

#### Scenario: Valores previos intactos

- **WHEN** se comparan las secciones `3.1` a `3.28` antes y después del change
- **THEN** ningún valor ni estado cambia
- **AND** solo se agrega la sección `3.29` y, si corresponde, una remisión desde la sección que declaraba la hipótesis sin contrastar

#### Scenario: Veredicto y métricas registrados

- **WHEN** se lee la sección `3.29`
- **THEN** figuran el veredicto de tres vías, las constantes prerregistradas y las métricas por nivel de las dos capas
- **AND** figuran los límites declarados del contraste

#### Scenario: Costo cero registrado

- **WHEN** se lee la sección `3.29`
- **THEN** consta que la corrida se hizo con la clave ficticia y el presupuesto nulo, sin invocaciones a Gemini ni a Twilio
- **AND** consta el entorno desechable sobre el que se corrió
