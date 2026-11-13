## ADDED Requirements

### Requirement: Registro del contraste de la hipotesis de eficiencia con el brazo solo-LLM

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL registrar el contraste de eficiencia en una sección nueva y aditiva (sección `3.27`), posterior a la `3.26` vigente, con procedencia por valor (archivo y ruta JSON de las salidas del análisis del brazo) y estado en `{vigente, retirado, condicional}`. La sección SHALL registrar, para el bloque primario de 103 casos con consenso de `E3` y `E4`: la exactitud estricta y laxa de cada brazo con IC de Wilson, la tabla 2×2, McNemar exacta, la diferencia de exactitudes con IC bootstrap, las llamadas por caso y las razones de llamadas y de costo con sus intervalos, los tokens, el costo en ambos escenarios de precio, la tasa de fallos, el componente de exactitud, el componente de eficiencia y el veredicto de tres vías. SHALL registrar el bloque dentro de la muestra como `condicional` (informativo, no limpio) y el control de deriva como `condicional`. SHALL registrar la desviación del preregistro por el reintento de fallos técnicos y su amenaza a la validez. MUST NOT modificar ningún valor ni estado de las secciones `3.1` a `3.26`; las frases previas que declaran la hipótesis de eficiencia «sin contrastar» SHALL quedar superadas por remisión a la sección nueva, sin borrar ni reescribir su contenido.

#### Scenario: Sección aditiva con procedencia

- **WHEN** se recorre la sección `3.27` del memo
- **THEN** cada valor declara su archivo y ruta de origen y un estado en `{vigente, retirado, condicional}`
- **AND** la sección aparece después de la `3.26` sin renumerar ni alterar las secciones anteriores

#### Scenario: Valores previos intactos

- **WHEN** se comparan las secciones `3.1` a `3.26` antes y después del change
- **THEN** ningún valor ni estado vigente cambia
- **AND** solo se agrega la sección `3.27` y, si corresponde, una remisión desde la sección que declaraba la hipótesis sin contrastar

#### Scenario: Veredicto y ahorro registrados

- **WHEN** se lee la sección `3.27`
- **THEN** figuran el veredicto «no concluyente», el ahorro de llamadas y de costo con sus intervalos y el estado «contrastada: no concluyente» de la hipótesis
- **AND** el bloque dentro de la muestra y el control de deriva figuran como `condicional`

#### Scenario: Desviación trazada

- **WHEN** se lee la sección `3.27`
- **THEN** consta la desviación del preregistro por el reintento de fallos técnicos con sus conteos y la declaración de que el bloque primario no se vio afectado
- **AND** consta la amenaza a la validez por la decisión posterior de reintentar