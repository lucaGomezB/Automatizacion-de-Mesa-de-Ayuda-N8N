## ADDED Requirements

### Requirement: Consistencia del parrafo introductorio con las columnas de la tabla comparativa del estado del arte

El parrafo introductorio de la tabla comparativa de soluciones (`\label{tab:comparativa}` en `03-estado-del-arte.tex`) SHALL declarar un numero de dimensiones coherente con las columnas efectivamente presentes en la tabla, y SHALL NOT enunciar como dimension una propiedad que no tenga columna propia. La tabla SHALL conservar sus cuatro columnas (Solucion, Despliegue, Clasificacion automatica, Modelo de costo) y su rotulo.

#### Scenario: Dimensiones declaradas coinciden con las columnas

- **WHEN** se lee el parrafo introductorio de `tab:comparativa` y se cuentan las columnas de la tabla
- **THEN** el numero de dimensiones enunciadas coincide con el numero de columnas de la tabla
- **AND** "soberania sobre los datos" no se enumera como dimension de la tabla si no existe como columna

#### Scenario: Propiedades sin columna conservadas como prosa

- **WHEN** se lee el parrafo introductorio y la sintesis posterior a la tabla
- **THEN** cualquier propiedad relevante que no tenga columna (por ejemplo, la soberania sobre los datos) se mantiene en la prosa circundante
- **AND** no se elimina del texto ninguna propiedad sustantiva de la comparacion

### Requirement: Hallazgo del gate de clasificacion presentado como resultado propio

La tesis SHALL presentar la conducta observada del gate de clasificacion en el corpus (la etapa Gemini nunca devolvio una confianza inferior a 0,85 sobre los 200 casos, de modo que el gate de revision no derivo ningun caso) como un hallazgo empirico con valor propio sobre el comportamiento del clasificador en el dominio evaluado, ademas de su uso como justificacion de la sub-hipotesis no contrastada. El hallazgo SHALL enunciarse en el capitulo de discusion y/o en la subseccion de intervencion humana de resultados (`subsec:reduccion-intervencion`) y MUST NOT introducir valores numericos distintos de los ya canonicos.

#### Scenario: Hallazgo enunciado como resultado positivo

- **WHEN** se lee el capitulo de discusion y/o la subseccion de intervencion humana de resultados
- **THEN** se declara que la etapa Gemini nunca devolvio una confianza inferior a 0,85 en el corpus
- **AND** ese comportamiento se presenta como un hallazgo positivo sobre el clasificador en el dominio evaluado, no solo como motivo de la no contraste de la sub-hipotesis

#### Scenario: Sin numeros nuevos

- **WHEN** se revisa el texto agregado para el hallazgo del gate
- **THEN** no aparece ningun valor numerico que no figure ya en `docs/Tesis/Correcciones/numeros-canonicos.md`
- **AND** el umbral 0,85 y el umbral 0,70 del gate se citan con el mismo valor y sentido que en el resto del documento

### Requirement: Cobertura bibliografica formal de las plataformas comerciales

Toda mencion a las plataformas comerciales Zendesk, Freshdesk y ServiceNow en `01-introduccion.tex` SHALL acompanarse de una entrada bibliografica formal en `Bibliography_base.bib` y de su cita en el texto. Cada entrada nueva SHALL tiparse como `@online` e incluir entidad autora, titulo, ano, `url`, `urldate` y una `note` de fecha de consulta, siguiendo el patron de las entradas `DigitalOcean2026_pricing` y `Google2026_vertex_pricing`. El documento MUST NOT introducir cifras de precio no verificables: cuando no exista una figura comprobable, la `note` SHALL declarar la pagina de documentacion de la plataforma y la prosa SHALL mantenerse como observacion de relevamiento.

#### Scenario: Entradas y citas incorporadas

- **WHEN** se inspecciona `Bibliography_base.bib` y `01-introduccion.tex`
- **THEN** existen entradas `@online` para Zendesk, Freshdesk y ServiceNow con `url`, `urldate = {2026-10-19}` y `note` de consulta
- **AND** la mencion a las tres plataformas en la introduccion se acompana de `\parencite` a esas entradas

#### Scenario: Sin cifras de precio fabricadas

- **WHEN** se revisa la prosa y la `note` de las entradas nuevas
- **THEN** no se afirma ninguna cifra de precio o de capacidad que no pueda verificarse contra la pagina de documentacion citada
- **AND** la formulacion se mantiene como observacion de relevamiento propio declarado

#### Scenario: Correspondencia citas-bibliografia preservada

- **WHEN** se ejecuta la verificacion de citas contra `Bibliography_base.bib` tras agregar las entradas
- **THEN** no se introduce ninguna cita huerfana
- **AND** no queda ninguna entrada nueva sin usar

<!-- REC 4 (trazabilidad del conteo bibliografico) retirada: la verificacion directa demuestra que no existe discrepancia de conteo (54 -> 56, delta +2 explicado por c-120). Vease la fe de errata del dictamen y la nota de alcance en proposal.md. -->

### Requirement: Etiqueta de la release v1.1.0 y trazabilidad del hash

La version de trabajo de la tesis `docs/Tesis/v10 (IA)/` SHALL publicarse mediante un tag anotado `v1.1.0` creado sobre el commit que cierra la migracion a v10 (c-122) y las tres observaciones del dictamen (este change). El manuscrito (`sections/12-anexos.tex`, `sec:anexo-repositorio`) SHALL identificar la version entregada con el tag `v1.1.0` y consignar el hash completo de 40 caracteres del commit etiquetado, coincidente con `git rev-parse v1.1.0^{commit}`. Los tags previos `v1.0.0` y `v1.0.1` MUST NOT moverse.

#### Scenario: Tag anotado v1.1.0 sobre el commit de cierre

- **WHEN** se ejecuta `git cat-file -t v1.1.0` y `git rev-parse v1.1.0^{commit}`
- **THEN** el tag existe, es anotado (devuelve `tag`, no `commit`) y apunta a un commit posterior a la aplicacion de c-122 y c-121
- **AND** el tag esta publicado en `origin` (`git ls-remote --tags origin v1.1.0` lo devuelve)

#### Scenario: Hash consignado y coherente con el tag

- **WHEN** se lee `sec:anexo-repositorio` en `12-anexos.tex` y se compara con `git rev-parse v1.1.0^{commit}`
- **THEN** figura el tag `v1.1.0` y el hash completo de 40 caracteres del commit etiquetado
- **AND** el hash coincide en los 40 caracteres y tambien figura en `docs/Tesis/Correcciones/dictamen-correcciones.md`

#### Scenario: Tags previos inmutables

- **WHEN** se comparan `git rev-parse v1.0.0^{commit}` y `git rev-parse v1.0.1^{commit}` con sus valores previos
- **THEN** `v1.0.0` sigue en `61a6b117dd1321fbee25f9792d9f29b884e5ac8d` y `v1.0.1` sigue en `bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0`
- **AND** ningun tag existente fue reescrito o re-creado

