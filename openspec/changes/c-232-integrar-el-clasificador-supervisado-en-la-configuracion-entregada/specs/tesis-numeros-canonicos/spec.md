## ADDED Requirements

### Requirement: Registro aditivo del contraste cabeza a cabeza y del veredicto del clasificador supervisado

El memo canonico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar una seccion
nueva y aditiva (el primer numero libre al aplicar; la ultima planificada es la `3.41`;
esperado `3.42`), sin renumerar ni alterar las anteriores. La seccion SHALL registrar, como
minimo y con su procedencia y su estado: la exactitud estricta y el macro-F1 del modelo
supervisado y del hibrido vigente sobre la referencia retenida y sobre el corpus de
prevalencia natural, con sus intervalos; la diferencia pareada y el resultado de McNemar; y el
**veredicto** de la regla pre-registrada (reemplazar, complementar o conservar). Cada valor
SHALL figurar con archivo fuente o comando que lo produce, su ambito y un estado en
`{vigente, sensibilidad, reinterpretacion, condicional, retirado}`. La seccion SHALL declarar
de forma explicita que no cambia `0,6893`, el macro-F1 `0,7024` ni el veredicto del umbral
`0,85`, que la linea depende de **datos que todavia no existen**, y que no modifica ningun
valor ni estado de las secciones `3.1` a `3.41`.

#### Scenario: Seccion aditiva con el contraste y el veredicto

- **WHEN** se lee la seccion nueva del memo
- **THEN** figuran las dos lecturas (modelo supervisado y hibrido) con sus intervalos, la diferencia pareada, McNemar y el veredicto
- **AND** cada valor tiene archivo fuente o comando, ambito y estado

#### Scenario: Valores previos intactos y dependencia declarada

- **WHEN** se comparan las secciones `3.1` a `3.41` antes y despues
- **THEN** ningun valor ni estado cambia y solo se agrega la seccion nueva
- **AND** la seccion declara que la linea depende de datos inexistentes y que no cambia `0,6893`, el macro-F1 `0,7024` ni el veredicto del `0,85`
