<!--
  Delta de c-245 sobre la capacidad `tesis-numeros-canonicos`.

  Requisito ADDED (no MODIFIED): el registro de la facturacion del proveedor (Cloud
  Billing) del periodo y la armonizacion de los items (e)(iv) y (f)(5) de la seccion 3.47
  hacia la subseccion (h) es una preocupacion nueva. No reescribe el requisito
  "Registro aditivo de la sonda de latencia con inferencia incluida" que el delta de c-243
  introduce (openspec/changes/c-243-.../specs/tesis-numeros-canonicos/spec.md), porque ese
  requisito aun no esta en la spec principal; este delta agrega un requisito propio que
  gobierna la subseccion (h) y la armonizacion.

  El requisito ADDED es de documento (no hay implementacion de codigo). El cambio de
  comportamiento es a nivel de spec, por lo que no aplica `skip_specs`.
-->

## ADDED Requirements

### Requirement: Registro de la facturacion del proveedor del periodo y remision de los items de la sonda

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL registrar, en la seccion de la sonda de latencia con inferencia incluida (la `3.47` de c-243), la facturacion del proveedor (Google Cloud Billing) del periodo de las dos corridas como entrada propia, con su procedencia (`evaluation/evidence/billing-gemini-2026-11-17-18-oficial.csv`, `sha256 7c75fc01\ldots`, y `billing-gemini-2026-11-17-18-resumen.csv`, `sha256 5ffaf26b\ldots`), el total del periodo (`366.909` tokens y USD `0,300897`) declarado como cota inferior, el contraste con `usage_metadata` de la corrida ampliada (`281.568` tokens y USD `0,23112`; aproximadamente `+30\,\%` en ambos tipos de token, misma proporcion) y la confirmacion del precio (precio implicito igual al escenario declarado de la tesis). El memo SHALL armonizar los items (e)(iv) — que hoy afirma que la procedencia del gasto es `tokens_calculado`, «no facturacion del proveedor» — y (f)(5) — «el gasto solo consta en la corrida ampliada, con procedencia `tokens_calculado`» — remitiendolos a la subseccion «Billing del proveedor (Cloud Billing)» ya escrita, conservando la distincion: el costo **por corrida** es `tokens_calculado`; el **periodo** tiene Cloud Billing como `gasto_origen`. La armonizacion MUST NOT modificar el item (g) (tokens y costo de la corrida ampliada), ni ningun valor canonico `vigente` ni estado previo, y SHALL dejar la numeracion de la Seccion 3 consecutiva y sin duplicados.

#### Scenario: Registro de la facturacion del periodo con procedencia

- **WHEN** se recorre la seccion de la sonda en el memo
- **THEN** figura la facturacion del periodo con sus dos archivos de evidencia, sus prefijos de SHA-256 y su estado
- **AND** el total figura como cota inferior con la salvedad de la exportacion abierta

#### Scenario: Item (e)(iv) remite a la subseccion de billing

- **WHEN** se lee el item (e)(iv) de la seccion `3.47`
- **THEN** remite a la subseccion «Billing del proveedor (Cloud Billing)»
- **AND** conserva que el costo por corrida es `tokens_calculado`

#### Scenario: Item (f)(5) remite a la subseccion de billing

- **WHEN** se lee el limite (f)(5) de la seccion `3.47`
- **THEN** remite a la subseccion «Billing del proveedor (Cloud Billing)»
- **AND** no afirma de forma aislada que el gasto no es facturacion del proveedor

#### Scenario: Distincion por corrida y por periodo conservada

- **WHEN** se leen juntos el item (g), la subseccion (h) y los items armonizados
- **THEN** el costo por corrida queda como `tokens_calculado` y el periodo como Cloud Billing
- **AND** ninguno se presenta como sustituto del otro

#### Scenario: Valores canonicos y estados previos intactos

- **WHEN** se compara el memo antes y despues del change
- **THEN** el item (g) conserva su tokens y su costo
- **AND** ningun valor `vigente` ni estado previo cambia, y la numeracion sigue consecutiva
