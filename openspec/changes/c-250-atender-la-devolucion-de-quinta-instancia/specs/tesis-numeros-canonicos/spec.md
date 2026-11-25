## ADDED Requirements

### Requirement: Registro aditivo del recomputo por pares de quinta instancia

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar una seccion nueva y aditiva con el numero inmediatamente posterior a la ultima seccion vigente al aplicar (la `3.49` al redactar este change, posterior a la `3.48`), sin renumerar ni alterar ninguna seccion previa. La seccion SHALL registrar, con procedencia por valor (archivo `evaluation/data/campana/analisis/analisis_quinta_instancia_c250.json` y ruta de clave) y el SHA-256 de cada salida: las reducciones de la media del tiempo de registro con descuentos de 0, 5 y 10 s (y el valor declarado por los autores en OQ-02 de c-250, si existe) para los 200 pares, los 119 de correo y formulario y los 81 telefonicos, con su IC bootstrap por pares (semilla `20261021`, 2000 remuestreos) y su prueba de Wilcoxon; la duracion de las 81 grabaciones frente a la lectura manual; y el conteo del registro primario de correo y formulario. Los escenarios de descuento sin valor declarado SHALL rotularse como sensibilidad (estado `condicional`) y no como estimacion. La seccion SHALL declarar que no reemplaza la cifra primaria de la seccion `3.1` (`71,2 %`) y MUST NOT modificar ningun valor ni estado previo.

#### Scenario: Seccion aditiva con el primer numero libre

- **WHEN** se aplica el change y se relee el indice del memo
- **THEN** la seccion nueva ocupa el primer numero libre posterior a la ultima seccion vigente
- **AND** ninguna seccion previa se renumera, cambia de cifra ni cambia de estado

#### Scenario: Procedencia y rotulos

- **WHEN** se recorre la seccion nueva
- **THEN** cada valor declara su archivo, su ruta de clave y su estado
- **AND** los descuentos sin valor declarado por los autores figuran como sensibilidad `condicional`

#### Scenario: Cifra primaria intacta

- **WHEN** se lee la seccion nueva junto a la `3.1`
- **THEN** la `3.1` conserva el `71,2 %` como cifra primaria y la seccion nueva figura como lectura complementaria
