## ADDED Requirements

### Requirement: Registro aditivo del rango de robustez de tiempos

El memo canonico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar una seccion nueva
y aditiva, posterior a la ultima seccion vigente, sin renumerar ni alterar las anteriores. La
seccion SHALL registrar, como minimo: el rango del estimando primario (reduccion de la media global
de la campana 2026-10) con sus escenarios de descuento de `5 s` y `10 s`, el escenario que lo
minimiza y su valor; el desagregado por canal con la reduccion intra-canal; los tiempos por
operador con la aclaracion de que provienen de la campana complementaria y no son comparables con
el brazo de 2026-10; el efecto de posicion con su medida y su efecto minimo detectable; y la cota
inferior del instrumento (multiplos de `5 s` y `10 s`, y la telefonia como cota inferior de la
duracion real de la llamada). Cada valor SHALL llevar su archivo y ruta de origen, o el comando que
lo reproduce, y un estado en `{vigente, sensibilidad, reinterpretacion, condicional, retirado}`. La
seccion SHALL declarar de forma explicita que el consolidado es una sintesis de escenarios ya
calculados, que no mide de nuevo, que no cambia la cifra primaria `71,2 %` ni su intervalo y que no
modifica ningun valor ni estado de las secciones 3.1 a 3.36. La seccion SHALL distinguir el minimo
del estimando primario de las cotas de alcance y MUST NOT presentar el valor por operador mas
adverso como minimo global.

#### Scenario: Seccion aditiva con el primer numero libre

- **WHEN** se aplica el change y se relee el indice del memo
- **THEN** la seccion nueva ocupa el primer numero libre posterior a la ultima seccion vigente
- **AND** ninguna seccion previa se renumera ni se reescribe

#### Scenario: Cada escenario con procedencia y estado

- **WHEN** se lee la seccion nueva del memo
- **THEN** cada escenario tiene archivo fuente o comando, ambito y estado
- **AND** la sintesis esta rotulada como sensibilidad o reinterpretacion, no como medicion nueva

#### Scenario: Rango y minimo declarados sin cambiar la cifra primaria

- **WHEN** se busca el rango de robustez de tiempos
- **THEN** la seccion declara el rango del estimando primario y el escenario que lo minimiza
- **AND** la cifra primaria `71,2 %` y su intervalo siguen sin cambios
- **AND** las cotas de alcance por canal y por operador quedan separadas del minimo global

#### Scenario: Valores previos intactos

- **WHEN** se comparan las secciones 3.1 a 3.36 antes y despues del change
- **THEN** cada valor conserva su cifra y su estado
- **AND** solo se agrega la seccion nueva