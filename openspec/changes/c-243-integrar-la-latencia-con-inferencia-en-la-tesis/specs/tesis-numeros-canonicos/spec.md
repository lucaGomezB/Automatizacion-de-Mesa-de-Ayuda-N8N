## ADDED Requirements

### Requirement: Registro aditivo de la sonda de latencia con inferencia incluida

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar una seccion nueva y aditiva con el numero inmediatamente posterior a la ultima seccion vigente al aplicar (la `3.47` al redactar este change, posterior a la `3.46`), sin renumerar ni alterar ninguna seccion previa y sin reutilizar los huecos de numeracion existentes. La seccion SHALL registrar, con procedencia por valor (archivo `evaluation/evidence/load_test_inferencia_2026-11-17.json` y ruta de clave) y estado `condicional`: el commit, la fecha UTC, el identificador de corrida, la version de N8N, el perfil, el SHA-256 de la fixture, las constantes prerregistradas (niveles 1/5/10/20, 20 solicitudes por nivel, una repeticion, techo de p95 de 5000 ms, tolerancia de throughput de 0,10, tasa de error 0, T = 4, tope de 1,00 USD y mezcla escalada esperada de 0,5), las metricas por nivel de las dos capas (p50, p95, p99, media, throughput, tasa de error, escalados, fraccion escalada, p95 del subconjunto escalado, p95 del subconjunto deterministico y cociente) y los dos veredictos con la condicion violada. La seccion SHALL declarar que los valores provienen de una sonda ancilar de una sola corrida con n = 10 por subconjunto, que NO son cifras canonicas de capacidad y que NO reemplazan ni modifican la seccion `3.29`. SHALL declarar que la evidencia no registra el gasto y que el gasto no se estima como medido. SHALL agregar una nota de remision en la seccion `3.29` hacia la seccion nueva, sin editar sus cifras ni su estado. MUST NOT modificar ningun valor ni estado previo y MUST NOT presentar la sonda como contraste de capacidad ni extrapolarla.

#### Scenario: Seccion aditiva con el primer numero libre

- **WHEN** se aplica el change y se relee el indice del memo
- **THEN** la seccion nueva ocupa el primer numero libre posterior a la ultima seccion vigente
- **AND** ninguna seccion previa se renumera, cambia de cifra ni cambia de estado

#### Scenario: Valores previos intactos

- **WHEN** se comparan las secciones previas antes y despues del change
- **THEN** todas conservan sus valores y estados
- **AND** la unica edicion en una seccion previa es la nota de remision agregada en la `3.29`

#### Scenario: Cifras con procedencia y estado condicional

- **WHEN** se recorre la seccion nueva
- **THEN** cada valor declara su archivo y ruta de clave y el estado `condicional`
- **AND** figuran las metricas por nivel de las dos capas y los dos veredictos con su condicion

#### Scenario: Limites y gasto declarados

- **WHEN** se lee la seccion nueva
- **THEN** figuran la corrida unica, el tamano de subconjunto, la maquina unica, el entorno desechable, la no comparabilidad con la corrida canonica y la no extrapolacion
- **AND** consta que el gasto no esta registrado en la evidencia y que no se estima como medido

#### Scenario: Sin reemplazo de la capacidad canonica

- **WHEN** se lee la seccion nueva junto a la `3.29`
- **THEN** la `3.29` sigue siendo la lectura canonica de capacidad
- **AND** la seccion nueva figura como sonda ancilar que no la modifica ni la supera
