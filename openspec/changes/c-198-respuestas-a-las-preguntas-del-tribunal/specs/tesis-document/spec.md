## MODIFIED Requirements

### Requirement: Anexos con contenido real

Los anexos A a G y el Anexo J SHALL contener contenido real embebido (figura, tabla, listado de codigo o bloque de datos) en lugar de unicamente describirlo en prosa. El Anexo H (especificacion del prompt de Gemini) SHALL incorporarse al documento como una seccion de anexo. El Anexo J (respuestas del grupo a las preguntas del tribunal) SHALL incorporar el contenido de `docs/defensa/respuestas-tribunal.md`.

#### Scenario: Cada anexo A-G embebe su artefacto
- **WHEN** se lee cada una de las secciones de `12-anexos.tex`
- **THEN** el Anexo A embebe el diagrama de arquitectura (figura), el Anexo C embebe el esquema de base de datos (tabla o diagrama ER), el Anexo D embebe la especificacion OpenAPI (bloque de codigo o listado), el Anexo E embebe la configuracion del flujo N8N y el Anexo F embebe la estructura o declaracion del corpus
- **AND** cada anexo deja de ser exclusivamente un parrafo descriptivo sin contenido embebido

#### Scenario: Anexo H incorporado
- **WHEN** se busca el Anexo H en los archivos `.tex`
- **THEN** existe una seccion que incorpora el contenido de `docs/anexo_h_prompt_gemini.md` (estructura del prompt y parametros de configuracion)
- **AND** el Anexo H esta referenciado desde el texto principal del documento

#### Scenario: Contenido real y no meramente descriptivo
- **WHEN** se inspecciona un anexo convertido
- **THEN** contiene al menos un entorno `figure`, `table`, `lstlisting` o `verbatim` con contenido
- **AND** el anexo mantiene la prosa introductoria que lo contextualiza

#### Scenario: Anexo J incorporado
- **WHEN** se busca el Anexo J en `12-anexos.tex`
- **THEN** existe una seccion que incorpora el contenido de `docs/defensa/respuestas-tribunal.md` (las 16 respuestas)
- **AND** el Anexo J esta referenciado desde el texto del documento

## ADDED Requirements

### Requirement: Anexo J de respuestas a las preguntas del tribunal

La tesis SHALL incluir, como ultima seccion de `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`, un anexo nuevo (Anexo J, etiqueta `sec:anexo-respuestas-tribunal`) que incorpore las respuestas del grupo a las 16 preguntas de la Seccion 8 de la devolucion del 11-11-2026. La serie de anexos SHALL pasar de A-I a A-J. El Anexo J SHALL reutilizar los valores canonicos vigentes y MUST NOT introducir cifras de resultado ausentes del memo `docs/Tesis/Correcciones/numeros-canonicos.md`. El anexo MUST NOT atribuirse a un modelo de lenguaje.

#### Scenario: Anexo J presente como ultima seccion

- **WHEN** se lista el orden de las secciones de `12-anexos.tex`
- **THEN** el Anexo J es la ultima seccion y su etiqueta es `sec:anexo-respuestas-tribunal`
- **AND** la seccion de trazabilidad (`sec:anexo-trazabilidad`, Anexo I) queda inmediatamente antes

#### Scenario: La serie de anexos llega a J

- **WHEN** se compila el PDF
- **THEN** el ultimo anexo se rotula "Anexo J"
- **AND** los anexos A a I conservan su contenido y su rotulo

#### Scenario: Sin cifras no canonicas en el anexo

- **WHEN** se comparan las cifras del Anexo J con los valores vigentes del memo canonico
- **THEN** cada cifra coincide con un valor vigente del memo o con un valor recalculable desde un artefacto versionado
- **AND** no aparece ningun valor retirado (por ejemplo el kappa de 0,87 como evidencia)

#### Scenario: Compilacion sin errores fatales

- **WHEN** se compila `main.tex` con XeLaTeX y biber
- **THEN** se produce `main.pdf` sin errores fatales
- **AND** no quedan referencias ni citas indefinidas por el anexo nuevo
