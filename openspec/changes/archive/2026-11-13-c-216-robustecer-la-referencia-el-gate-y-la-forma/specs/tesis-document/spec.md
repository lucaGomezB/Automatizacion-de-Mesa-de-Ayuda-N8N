## ADDED Requirements

### Requirement: Análisis de sensibilidad a la referencia de verdad en resultados y método

`07-resultados.tex` SHALL incluir una subsección nueva, con etiqueta `subsec:ruido-referencia`,
después de `subsec:resultados-campana-medicion`, que presente el análisis de sensibilidad a la
referencia de verdad sobre el corpus arbitrado de `206` casos. La subsección SHALL informar: la
pregunta que responde; el método en una o dos oraciones con remisión al capítulo 4; una tabla
con la exactitud estricta y la macro-F1 observadas (`0,6893` y `0,7024`), su mediana y sus
percentiles `2,5`/`97,5` bajo referencias alternativas, la fracción `δ` y las cotas de
exactitud; la descomposición entre error atribuible a la referencia y error robusto; y el rango
de los `6` casos de tres vías. `04-marco-metodologico.tex` SHALL definir el método con sus
supuestos y sus límites: la simulación de etiquetas calibrada al kappa `E3`/`E4` (`0,6055`), la
búsqueda de la intensidad `λ`, `B = 2000` con semilla fija y las cotas distribution-free bajo un
presupuesto `δ` de error de referencia. `08-discusion.tex` SHALL leer el resultado como
sensibilidad, no como medición, y SHALL declarar que no elimina las demás amenazas a la validez
del criterio 4. La incorporación MUST NOT cambiar `0,6893/206`, `0,7024` ni ningún otro valor
canónico, y su crecimiento neto de páginas SHALL ser de a lo sumo dos páginas, registrado en el
libro mayor de `dictamen-correcciones.md`.

#### Scenario: Subsección, tabla y remisión al método

- **WHEN** se lee `07-resultados.tex`
- **THEN** existe `subsec:ruido-referencia` con la tabla de distribución y cotas
- **AND** el capítulo 4 define la simulación calibrada al kappa y las cotas
- **AND** `08-discusion.tex` remite a la subsección y la rotula como sensibilidad

#### Scenario: Anclajes canónicos y ausencia de sobreafirmación

- **WHEN** se comparan las cifras de la subsección con el memo canónico
- **THEN** la exactitud observada es `0,6893` (`142/206`) y la macro-F1 observada es `0,7024`
- **AND** el texto no presenta la simulación como medición de la verdad latente ni afirma que el error se explica por completo por el ruido de la referencia

#### Scenario: Crecimiento de páginas acotado y registrado

- **WHEN** se compara el total de páginas del PDF con el de la release de partida
- **THEN** el crecimiento neto es de a lo sumo dos páginas
- **AND** el libro mayor registra el delta y su causa

### Requirement: Reencuadre del human-in-the-loop según la señal que efectivamente actuó

La tesis SHALL dejar de afirmar que la revisión humana no actuó y SHALL afirmar, en su lugar,
que el human-in-the-loop actuó por una señal independiente de la confianza —la regla de
derivación por reportante no identificado en el directorio de empleados— y que lo que no
discriminó fue la señal de confianza. La afirmación SHALL apoyarse en las cifras vigentes: `147`
intervenciones (`66` de correo y `81` de telefonía), `25` cambios de derivación (`17,0 %`;
IC de Wilson `[11,8 %; 23,9 %]`) y AUROC de la confianza de Gemini `0,5168`
(`[0,3796; 0,6528]`) dentro de la muestra. `07-resultados.tex`, `08-discusion.tex`,
`09-conclusiones.tex`, `10-recomendaciones.tex` y `11-aspectos-legales.tex` SHALL distinguir
expresamente las dos señales y MUST NOT atribuir casos derivados al gate de confianza. La
tesis SHALL distinguir la configuración evaluada de la entregada y SHALL declarar que la regla
del reportante es posterior a la campaña 2026-10. La tesis MUST NOT ejecutar ni presentar una
corrida de la configuración entregada sin autorización escrita del dueño; sin esa autorización,
SHALL declarar la configuración entregada como no medida y como limitación. La corrida, si se
autoriza, SHALL registrarse como una corrida paga separada con el guard `--confirm-paid`.

#### Scenario: Las dos señales distinguidas

- **WHEN** se busca en el cuerpo la afirmación sobre la revisión humana
- **THEN** el texto dice que el human-in-the-loop actuó por la regla del reportante y que la señal de confianza no discriminó
- **AND** no queda ninguna afirmación que diga que la revisión humana no actuó o que el gate de confianza derivó casos

#### Scenario: Cifras y fechas consistentes

- **WHEN** se comparan las cifras del reencuadre con el memo canónico
- **THEN** `147`, `66`, `81`, `25`, `17,0 %` y AUROC `0,5168` coinciden con sus valores vigentes
- **AND** la regla del reportante figura como posterior a la campaña 2026-10

#### Scenario: Sin corrida paga no autorizada

- **WHEN** el dueño no autoriza por escrito la corrida de la configuración entregada
- **THEN** la tesis declara esa configuración como no medida y como limitación
- **AND** no se presenta ningún resultado de una corrida entregada

### Requirement: Repetición de cifras acotada y remisión a la tabla fuera de muestra

La pareja exactitud estricta fuera de muestra `0,8447` con `n = 103` y la pareja exactitud
estricta arbitrada `0,6893` con `n = 206` SHALL aparecer en prosa como máximo una vez fuera de
`07-resultados.tex`; en `08-discusion.tex`, `09-conclusiones.tex` y
`10-recomendaciones.tex` las menciones posteriores SHALL reemplazarse por una remisión a
`tab:fuera-de-muestra` o a `subsec:resultados-campana-medicion`. Las tablas, incluidas
`tab:fuera-de-muestra` y la tabla de cumplimiento de objetivos, quedan exentas de la regla. La
reducción MUST NOT cambiar el valor de ninguna cifra, cita ni afirmación sustantiva, y MUST NOT
introducir referencias cruzadas sin destino.

#### Scenario: Conteo de repeticiones en prosa

- **WHEN** se cuentan las apariciones en prosa de `0,8447` y de `0,6893` en los capítulos 8, 9 y 10
- **THEN** cada una aparece como máximo una vez por capítulo
- **AND** las demás menciones son remisiones a `tab:fuera-de-muestra` o a la subsección de resultados

#### Scenario: Cifras y citas intactas

- **WHEN** se compara el texto antes y después de la reducción
- **THEN** ninguna cifra canónica, cita o afirmación sustantiva cambia
- **AND** todas las remisiones nuevas resuelven a una etiqueta existente

### Requirement: Oraciones y párrafos acotados en el capítulo de aspectos legales

`11-aspectos-legales.tex` SHALL quedar con cero oraciones de más de `60` palabras según la regla
de conteo de `docs/Tesis/Correcciones/sent_c197.py`, y ningún párrafo de ese archivo SHALL
superar los `2000` caracteres. La partición de oraciones y párrafos SHALL preservar el
significado jurídico, las citas, las remisiones y todas las cifras; MUST NOT introducir
afirmaciones nuevas ni retirar salvedades. La lista de oraciones y párrafos partidos SHALL
registrarse en la sección del change en `dictamen-correcciones.md`.

#### Scenario: Regla de conteo en cero

- **WHEN** se ejecuta `sent_c197.py` sobre `11-aspectos-legales.tex`
- **THEN** informa `0` oraciones de más de `60` palabras
- **AND** ningún párrafo del archivo supera los `2000` caracteres

#### Scenario: Contenido jurídico intacto

- **WHEN** se revisa el diff del capítulo 11
- **THEN** las citas, remisiones, cifras y salvedades se conservan
- **AND** no se agrega ninguna afirmación nueva sobre el consentimiento ni sobre la transferencia internacional
- **AND** el registro enumera las oraciones y párrafos partidos con su ubicación previa