## ADDED Requirements

### Requirement: Validación fuera de muestra declarada como realizada con su resultado y sus límites

Cuando la campaña de validación fuera de muestra concluya, la tesis SHALL declarar la
validación como REALIZADA con el clasificador congelado sobre el corpus independiente, e
informar el resultado y sus límites: la exactitud estricta y la laxa sobre el n efectivo, su
IC de Wilson, el número de casos excluidos por discordancia y la advertencia de que esa
exclusión sesga la referencia hacia los casos más fáciles. La tesis MUST NOT seguir afirmando
que la validación "queda como no realizada", que "no se realizó" o que "continúa pendiente".
El estado SHALL ser idéntico en las secciones que hoy la declaran no realizada: el párrafo de
validación fuera de muestra de `07-resultados.tex`, los párrafos de `08-discusion.tex`
(`subsec:interpretacion-resultados` y `subsec:limitaciones-estudio`), la sección de
recomendaciones sobre el corpus independiente (`10-recomendaciones.tex`,
`subsec:corpus-independiente`) y las remisiones de `subsec:clasificador-supervisado`. Los
valores SHALL tomarse de la salida de `evaluar_fuera_de_muestra` y registrarse en
`docs/Tesis/Correcciones/numeros-canonicos.md` con su fuente. El resumen y el abstract SHALL
incorporar el resultado SOLO si este amerita cambiar el veredicto de la sub-hipótesis de
clasificación, sin superar 250 palabras cada uno. La limitación que la exclusión introduce y el
carácter del resultado (estimación sobre el n efectivo) SHALL declararse; la validación MUST
NOT presentarse como una confirmación fuerte ni extrapolarse.

#### Scenario: Estado realizado en todas las secciones

- **WHEN** se buscan "no realizada", "no se realizó" y "continúa pendiente" asociados a la validación fuera de muestra en los archivos de sección
- **THEN** no quedan referencias que la declaren no realizada
- **AND** las secciones afectadas declaran la validación como realizada con el mismo resultado

#### Scenario: Resultado con n efectivo e IC

- **WHEN** se lee el resultado fuera de muestra en la tesis
- **THEN** figuran la exactitud estricta y la laxa con su IC de Wilson sobre el n efectivo y el conteo de casos excluidos
- **AND** se declara que la exclusión de discordantes sesga la referencia hacia los casos más fáciles

#### Scenario: Valores registrados con su fuente

- **WHEN** se buscan los valores del resultado fuera de muestra en `numeros-canonicos.md`
- **THEN** cada cifra figura con su archivo fuente y el comando que la produce

#### Scenario: Resumen y abstract dentro del tope

- **WHEN** se cuentan las palabras del resumen y del abstract con la regla registrada
- **THEN** cada uno tiene a lo sumo 250 palabras
- **AND** si incorporan el resultado, lo hacen sin sobreafirmar la confirmación

### Requirement: Reformulación de la atribución a Galup (2009) en 2.1 y 1.2

La definición de ITSM de la sección 2.1 (`02-marco-teorico.tex`) SHALL enunciarse como una
definición general de la disciplina y MUST NOT atribuir a Galup et al. (2009) una
caracterización específica; Galup2009 SHALL citarse como panorama del campo mediante
`\parencite{Galup2009_itsm}`. La sección 1.2 (`01-introduccion.tex`) SHALL retirar "de Galup"
y presentar la caracterización como general. Galup2009 SHALL conservarse como entrada
verificada de `Bibliography_base.bib` y `verify_citations.py` SHALL dar PASS.

#### Scenario: 2.1 sin atribución específica a Galup

- **WHEN** se lee la definición de ITSM en 2.1
- **THEN** la definición es general y Galup2009 se cita con `\parencite{Galup2009_itsm}` como panorama del campo
- **AND** no se le atribuye una afirmación específica entrecomillada o parafraseada

#### Scenario: 1.2 sin "de Galup"

- **WHEN** se busca "de Galup" en `01-introduccion.tex`
- **THEN** no hay coincidencias
- **AND** la caracterización de la gestión de servicios de TI se presenta como general

#### Scenario: Bibliografía y citas consistentes

- **WHEN** se compila con biber y se corre `verify_citations.py`
- **THEN** Galup2009 sigue como entrada verificada y `verify_citations.py` reporta PASS
- **AND** biber no registra advertencias

### Requirement: Trazabilidad del cierre de la validación fuera de muestra en el registro y el Anexo I

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL incluir una sección para este change
que registre el cierre del dock "validación fuera de muestra no realizada" (criterio 4) con las
decisiones de los autores (estratos, etiquetadores `E3`/`E4`) y su estado. El Anexo I
(`12-anexos.tex`, `sec:anexo-trazabilidad`) SHALL actualizar la fila del límite estructural de
la validación fuera de muestra para reflejar su cierre, y su frase de cabecera SHALL contar el
dictamen correspondiente. El dictamen del 2026-11-09 SHALL permanecer versionado en
`auditorias/`.

#### Scenario: Registro del cierre

- **WHEN** se lee la sección del change en `dictamen-correcciones.md`
- **THEN** figura el cierre del dock de la validación fuera de muestra con las decisiones de estratos y etiquetadores y su estado
- **AND** el verificador de la matriz de trazabilidad no reporta fallas sobre el árbol

#### Scenario: Anexo I actualizado

- **WHEN** se compila y se lee el Anexo I
- **THEN** la fila del límite estructural de la validación fuera de muestra refleja su cierre con la remisión a la sección de resultados

#### Scenario: Dictamen versionado

- **WHEN** se ejecuta `git ls-tree v1.3.0 auditorias/`
- **THEN** figura `Dictamen_Tesis_v10_v1.2.12_CONEAU_2026-11-09.md`
