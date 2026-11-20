## ADDED Requirements

### Requirement: Registro aditivo de la sonda de latencia con inferencia incluida

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar una seccion nueva y aditiva con el numero inmediatamente posterior a la ultima seccion vigente al aplicar (la `3.47` al redactar este change, posterior a la `3.46`), sin renumerar ni alterar ninguna seccion previa y sin reutilizar los huecos de numeracion existentes. La seccion SHALL registrar, con procedencia por valor (archivo `evaluation/evidence/load_test_inferencia_ampliada_2026-11-18.json` para los niveles 1 y 5 y `evaluation/evidence/load_test_inferencia_2026-11-17.json` para los niveles 10 y 20, y ruta de clave) y estado `condicional`: el commit, la fecha UTC y el identificador de corrida de **cada** corrida, la version de N8N, el perfil, el SHA-256 de la fixture, las constantes prerregistradas de **ambas** corridas (niveles, solicitudes por nivel, repeticiones y tope de cada una; techo de p95 de 5000 ms, tolerancia de throughput de 0,10, tasa de error 0, T = 4 y mezcla escalada esperada de 0,5 comunes), las metricas de las **8 filas** por capa y nivel con su corrida de origen y su n (p50, p95, p99, media, throughput, tasa de error, escalados, fraccion escalada, p95 del subconjunto escalado, p95 del subconjunto deterministico y cociente) y los **tres veredictos** con la condicion violada. La seccion SHALL declarar que los niveles 1 y 5 provienen de la corrida ampliada (n = 90 por subconjunto, 3 repeticiones) y los niveles 10 y 20 de la corrida original (n = 10, 1 repeticion), que los valores NO son cifras canonicas de capacidad y que NO reemplazan ni modifican la seccion `3.29`. SHALL declarar que el gasto solo consta en la corrida ampliada y que su procedencia es `tokens_calculado` (no facturacion del proveedor), y que la corrida original no lo estima. SHALL agregar una nota de remision en la seccion `3.29` hacia la seccion nueva, sin editar sus cifras ni su estado. MUST NOT modificar ningun valor ni estado previo y MUST NOT presentar la sonda como contraste de capacidad ni extrapolarla.

#### Scenario: Seccion aditiva con el primer numero libre

- **WHEN** se aplica el change y se relee el indice del memo
- **THEN** la seccion nueva ocupa el primer numero libre posterior a la ultima seccion vigente
- **AND** ninguna seccion previa se renumera, cambia de cifra ni cambia de estado

#### Scenario: Valores previos intactos

- **WHEN** se comparan las secciones previas antes y despues del change
- **THEN** todas conservan sus valores y estados
- **AND** la unica edicion en una seccion previa es la nota de remision agregada en la `3.29`

#### Scenario: Ocho filas con procedencia por corrida de origen

- **WHEN** se recorre la seccion nueva
- **THEN** figuran las 8 filas (dos capas por cuatro niveles), cada una con su corrida de origen y su n escalado
- **AND** cada valor declara su archivo y ruta de clave y el estado `condicional`
- **AND** figuran los tres veredictos con su condicion

#### Scenario: Constantes de ambas corridas registradas

- **WHEN** se leen las constantes de la seccion nueva
- **THEN** figuran las de la corrida ampliada (niveles 1 y 5, 60 solicitudes por nivel, 3 repeticiones, tope USD 1,25)
- **AND** figuran las de la corrida original (niveles 1/5/10/20, 20 solicitudes por nivel, 1 repeticion, tope USD 1,00)

#### Scenario: Limites y gasto declarados

- **WHEN** se lee la seccion nueva
- **THEN** figuran las dos corridas complementarias, el n y las repeticiones por corrida, la maquina unica, el entorno desechable, la no comparabilidad con la corrida canonica y la no extrapolacion
- **AND** consta que el gasto solo consta en la corrida ampliada, con procedencia `tokens_calculado`, y que la corrida original no lo estima

#### Scenario: Sin reemplazo de la capacidad canonica

- **WHEN** se lee la seccion nueva junto a la `3.29`
- **THEN** la `3.29` sigue siendo la lectura canonica de capacidad
- **AND** la seccion nueva figura como sonda ancilar que no la modifica ni la supera
