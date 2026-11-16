## ADDED Requirements

### Requirement: Registro aditivo de los anclajes del clasificador supervisado y del techo sobre los 206

El memo canonico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar
una seccion nueva y aditiva (la `3.41`, primera libre tras la `3.37`), sin
renumerar ni alterar las anteriores. La seccion SHALL registrar, como minimo y con
su procedencia y su estado: la exactitud estricta fuera de muestra vigente
(`142/206`, `0,6893`); los `+34` aciertos necesarios para alcanzar `0,85` sobre
los `206`; el techo `0,835` al corregir los `30` errores de `Sistemas`; la
exactitud del brazo manual sobre la misma referencia (`0,8278`); y la ambiguedad
de la frontera `Sistemas`↔`Soporte Tecnico Software` (`16` de `64` errores). Cada
valor SHALL figurar con archivo fuente o comando, su ambito y un estado en
`{vigente, sensibilidad, reinterpretacion, condicional, retirado}`. La seccion
SHALL declarar de forma explicita que registra anclajes de una linea de trabajo
futuro que **depende de datos inexistentes y de etiquetado humano con
consentimiento**, que no mide de nuevo, que no cambia `0,6893`, el macro-F1
`0,7024` ni el veredicto del umbral `0,85`, y que no modifica ningun valor ni
estado de las secciones `3.1` a `3.37`.

#### Scenario: Seccion aditiva con anclajes y procedencia

- **WHEN** se lee la seccion `3.41` del memo
- **THEN** figuran `0,6893`, los `+34`, el techo `0,835`, el manual `0,8278` y la frontera `16/64`
- **AND** cada valor tiene archivo fuente o comando, ambito y estado

#### Scenario: Dependencia de datos declarada y valores previos intactos

- **WHEN** se comparan las secciones `3.1` a `3.37` antes y despues
- **THEN** ningun valor ni estado cambia y solo se agrega la seccion nueva
- **AND** la seccion declara que la linea depende de datos inexistentes y que `0,85` no es alcanzable sobre los `206`
