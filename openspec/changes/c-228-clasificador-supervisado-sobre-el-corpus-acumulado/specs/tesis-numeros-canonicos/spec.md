## ADDED Requirements

### Requirement: Registro aditivo del clasificador supervisado en la seccion reservada 3.41

El memo canonico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar la seccion aditiva `3.41`, reservada a este change, sin renumerar ni alterar las anteriores. La seccion SHALL registrar el estado de las compuertas de procedencia y etica y legal y, solo para valores producidos con esas compuertas cerradas, como minimo: el volumen curado y su conteo por sector; el `n` de entrenamiento y de prueba; la exactitud estricta y el macro-F1 del clasificador supervisado y del hibrido sobre el conjunto retenido, con su rotulo (corpus probabilistico acreditado o particion retenida interna); y la ambiguedad de la frontera `Sistemas`↔`Soporte Tecnico Software` antes (doble etiquetado E1/E2 sobre el corpus de 200 casos) y despues (etiquetado nuevo bajo compuertas), si existe. Cada valor SHALL figurar con archivo fuente o comando, su ambito y un estado en `{vigente, sensibilidad, reinterpretacion, condicional, retirado}`. Si no hay valores con compuertas cerradas, la seccion SHALL registrar el bloqueo sin cifras de resultado. La seccion MUST NOT citar como ancla, insumo o comparador ninguna cifra retirada por `c-235` y MUST NOT modificar valores ni estados de otras secciones.

#### Scenario: Seccion aditiva con procedencia

- **WHEN** se lee la seccion `3.41` del memo
- **THEN** figura el estado de las compuertas y cada valor tiene archivo fuente o comando, ambito y estado
- **AND** ninguna cifra retirada por `c-235` aparece como ancla o comparador

#### Scenario: Bloqueo sin cifras

- **WHEN** no hay valores producidos con compuertas cerradas
- **THEN** la seccion registra el bloqueo
- **AND** no contiene cifras de resultado del clasificador supervisado

#### Scenario: Valores previos intactos

- **WHEN** se comparan las demas secciones del memo antes y despues
- **THEN** ningun valor ni estado cambia y solo se agrega la seccion `3.41`
