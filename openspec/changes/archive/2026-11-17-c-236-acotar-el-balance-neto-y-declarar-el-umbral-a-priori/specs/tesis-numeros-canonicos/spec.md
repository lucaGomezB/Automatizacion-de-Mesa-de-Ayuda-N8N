## ADDED Requirements

### Requirement: Registro aditivo del balance neto acotado con el termino de revision

El memo canónico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar una sección nueva y aditiva con el primer número libre al aplicar, sin renumerar ni alterar las anteriores. La sección SHALL registrar: los insumos (`N`, `Delta t`, `e_aut`, `e_man`, `c = 69,51 s` como cota inferior del costo, `rho = 147/200` y `r = 22,06 s`), cada uno con procedencia y estado; las fórmulas `B_r` y `a*_r`; la regla de elección de `r` y su preregistro no ciego; `B_r` y `a*_r` como cota superior, con su intervalo condicional y su cota combinada; la rejilla de 5, 10 y 15 minutos con revisión, con estado `condicional`, rotulada como sensibilidad al tramo no medido; el costo de equilibrio `c*` con su margen; las sensibilidades de `r` y de `rho`; el comando de recálculo, los SHA-256 y la convención de redondeo. La sección SHALL declarar retirada como lectura central la cifra `B = +30,6` de la sección 3.33 y la expresión «signo fijado por la muestra», sin editar esa sección. La sección SHALL cerrar la contradicción entre la sección 3.11 (supuesto «el flujo automatizado no agrega tiempo de revisión») y la sección 3.31 (h) (el flujo sí lo agrega). Para eso, SHALL agregar notas de remisión en 3.11, 3.31 (h) y 3.33. MUST NOT cambiar ninguna cifra ni estado previo. MUST NOT registrar cifras fuera de muestra.

#### Scenario: Sección aditiva con el primer número libre

- **WHEN** se aplica el change y se relee el índice del memo
- **THEN** la sección nueva ocupa el primer número libre posterior a la última sección vigente
- **AND** ninguna sección previa se renumera ni cambia de cifra o estado

#### Scenario: Cota superior registrada con su método

- **WHEN** se lee la sección nueva
- **THEN** `B_r` figura como cota superior con `c` declarado como cota inferior, con su intervalo condicional, su cota combinada y su método
- **AND** el signo del balance real figura como dependiente del tramo de reanudación no medido

#### Scenario: Contradicción interna cerrada por nota

- **WHEN** se lee la sección 3.11 junto al supuesto sobre el tiempo de revisión
- **THEN** una línea agregada remite a la sección nueva y declara refutado el supuesto por la sección 3.31 (h)
- **AND** la sección 3.31 (h) y la sección 3.33 tienen líneas agregadas que remiten a la sección nueva, sin cambio de su texto previo
