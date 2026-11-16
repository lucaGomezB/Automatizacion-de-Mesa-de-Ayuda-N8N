## ADDED Requirements

### Requirement: Registro aditivo del contraste y del veredicto del clasificador supervisado en la seccion reservada 3.42

El memo canonico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar la seccion aditiva `3.42`, reservada a este change, sin renumerar ni alterar las anteriores. La seccion SHALL registrar el estado de las compuertas y la fecha de la constancia del pre-registro y, solo para valores producidos con compuertas cerradas sobre el corpus probabilistico acreditado con referencia por mayoria, como minimo: la exactitud estricta y el macro-F1 del modelo supervisado y del hibrido con sus intervalos; la diferencia pareada y el resultado de McNemar; y el **veredicto** de la regla pre-registrada. Cada valor SHALL figurar con archivo fuente o comando, su ambito y un estado en `{vigente, sensibilidad, reinterpretacion, condicional, retirado}`. Si no hay valores con compuertas cerradas, la seccion SHALL registrar el bloqueo sin cifras de resultado. La seccion MUST NOT citar como ancla, insumo o comparador ninguna cifra retirada por `c-235` y MUST NOT modificar valores ni estados de otras secciones.

#### Scenario: Seccion aditiva con el contraste y el veredicto

- **WHEN** se lee la seccion `3.42` del memo con compuertas cerradas
- **THEN** figuran las dos lecturas con sus intervalos, la diferencia pareada, McNemar y el veredicto
- **AND** cada valor tiene archivo fuente o comando, ambito y estado

#### Scenario: Bloqueo sin cifras

- **WHEN** no hay valores producidos con compuertas cerradas
- **THEN** la seccion registra el bloqueo sin cifras de resultado

#### Scenario: Valores previos intactos

- **WHEN** se comparan las demas secciones del memo antes y despues
- **THEN** ningun valor ni estado cambia y solo se agrega la seccion `3.42`
