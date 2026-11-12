## ADDED Requirements

### Requirement: Descripcion precisa de la pseudonimizacion en la tesis

La tesis SHALL describir la pseudonimizacion del corpus de forma consistente con el artefacto versionado. La descripcion del campo `descripcion` del Anexo I SHALL presentarse como el texto pseudonimizado producido por el modulo, y MUST NOT afirmar que el corpus del estudio contiene etiquetas genericas como `[EMAIL]`, `[TELEFONO]`, `[HOST]` o `[PERSONA]`: el corpus versionado `data/corpus_evaluacion_pseudonimizado.json` no contiene ninguna de esas etiquetas porque los incidentes del estudio no incluian identificadores personales directos. La descripcion del mecanismo SHALL precisar que el modulo local pseudonimiza el texto antes de la llamada a Gemini y SHALL aclarar que en el corpus del estudio no habia identificadores directos. La tesis SHALL documentar el hallazgo de la correccion del sobreenmascarado (`c-201`) de forma factual y breve, sin presentarlo como una falla que altere las conclusiones, y MUST NOT cambiar ninguna cifra canonica ni tocar los archivos del corpus.

#### Scenario: El Anexo I no afirma etiquetas inexistentes

- **WHEN** se lee la seccion del Anexo I titulada "Corpus de validacion" en la seccion 12 (`12-anexos.tex`)
- **THEN** describe el campo `descripcion` como el texto pseudonimizado producido por el modulo
- **AND** no afirma que el corpus del estudio contiene etiquetas como `[EMAIL]`, `[TELEFONO]`, `[HOST]` o `[PERSONA]`

#### Scenario: Se declara que el corpus del estudio no tenia identificadores directos

- **WHEN** se busca en los archivos de seccion de la tesis un pasaje sobre las etiquetas de pseudonimizacion
- **THEN** la tesis declara que en el corpus del estudio no habia identificadores personales directos, y que por eso no aparecen etiquetas
- **AND** la pseudonimizacion se declara aplicada al incidente en produccion antes de su clasificacion y persistencia

#### Scenario: Mecanismo preciso en la seccion de aspectos legales

- **WHEN** se lee la subseccion de transferencia internacional en la seccion 11 (`11-aspectos-legales.tex`)
- **THEN** se precisa que el modulo Python local es lo que pseudonimiza el texto antes de la llamada a Gemini
- **AND** se aclara que en el corpus del estudio no habia identificadores directos, sin debilitar el encuadre legal sobre la transferencia internacional

#### Scenario: Hallazgo de c-201 documentado sin cambiar cifras

- **WHEN** se busca en la tesis el hallazgo de la correccion del sobreenmascarado del pseudonimizador
- **THEN** se documenta que la heuristica sobreenmascaraba terminos no-persona (por ejemplo `Su PC`, `Adobe PDF Reader`, `Recursos Humanos`), que `c-201` lo corrigio, y que el corpus evaluado no se ve afectado porque repetir la clasificacion es un no-op
- **AND** no se altera ninguna cifra canonica, metrica ni el contenido sustantivo del documento

#### Scenario: Ejemplos de los documentos de soporte rotulados como ilustrativos

- **WHEN** se leen los ejemplos con etiquetas en `docs/anexo_f_corpus.md` y `docs/como_cargar_datos_corpus.md`
- **THEN** los ejemplos se rotulan como ilustrativos del formato de pseudonimizacion
- **AND** no se presentan como contenido literal del corpus del estudio
