## ADDED Requirements

### Requirement: Registro canonico del gate por etapa y del punto de operacion del cortocircuito

El memo canonico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL registrar, con archivo y linea de origen y estado, los valores que la tesis cita para describir el gate de revision por etapa y el cortocircuito de la etapa deterministica: los casos con confianza inferior a 0,70 sin escalamiento (`124/200`, `62,0 %`, todos de la etapa deterministica), la confianza minima declarada por la etapa Gemini (`0,85` en sus `69` casos), el punto de operacion del cortocircuito (`0,5166`, derivado por validacion cruzada de cinco pliegues), su cobertura (`131/200`), la precision del filtro sobre el conjunto cortocircuitable (`97/131`, `0,7405`) y la de la etapa Gemini sobre ese conjunto (`88/130`, `0,6769`). El memo SHALL declarar que ambas precisiones son estimaciones dentro de la muestra, que `88/130` proviene de la cache FORCE-ESCALATE con un caso excluido por no tener prediccion de Gemini, y SHALL registrar en "Decisiones no resolubles" la procedencia no documentada de esa cache con su condicion de reversibilidad. El memo MUST NOT modificar ningun valor vigente previo.

#### Scenario: Filas con procedencia y estado

- **WHEN** se lee la seccion del gate por etapa del memo
- **THEN** cada uno de los valores `124/200`, `62,0 %`, `0,85`, `0,5166`, `131/200`, `97/131`, `0,7405`, `88/130` y `0,6769` declara un archivo y una linea de origen que existen, y el estado `vigente`
- **AND** ningun valor vigente de las Secciones 3.1 a 3.6 cambia

#### Scenario: Salvedades declaradas

- **WHEN** se leen las notas de `97/131` y `88/130`
- **THEN** se declara que son estimaciones dentro de la muestra
- **AND** se declara la exclusion del caso sin prediccion de Gemini y la fuente de la cache FORCE-ESCALATE

#### Scenario: Procedencia de la cache registrada como no resoluble

- **WHEN** no puede verificarse desde fuentes versionadas la fecha ni la version del prompt de la cache FORCE-ESCALATE
- **THEN** la Seccion 7 del memo lo declara con la decision editorial adoptada
- **AND** registra que se revisa si el autor aporta el `cache_meta` de la cache

#### Scenario: Consumo por la tesis

- **WHEN** la tesis cita 124, 62 %, 0,85, 0,5166, 131, 0,7405 o 0,6769 en el contexto del gate o del cortocircuito
- **THEN** el valor coincide con el valor vigente del memo
