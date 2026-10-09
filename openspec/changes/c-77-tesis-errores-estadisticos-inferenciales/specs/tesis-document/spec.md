## ADDED Requirements

### Requirement: Rigor inferencial del tamaño del efecto

El capítulo de marco metodológico y el de resultados SHALL declarar
explícitamente la convención del estadístico de Wilcoxon empleado, reportar
ambos estadísticos de rango (`T+` y `T−`) y calcular el tamaño del efecto con la
fórmula rank-biserial correcta. El documento MUST NOT presentar `W=0` ni un
tamaño del efecto igual a `1,00` como resultado del corpus real, y MUST declarar
el rango verdadero de la fórmula empleada.

#### Scenario: Convención de W declarada

- **WHEN** se lee la sección de análisis estadístico o de resultados que reporta la prueba de Wilcoxon
- **THEN** el texto enuncia si `W` denota `min(T+, T−)`, `T+` u otro estadístico
- **AND** reporta los valores de `T+` y `T−` además del estadístico de contraste

#### Scenario: Fórmula y rango correctos

- **WHEN** se lee la fórmula del tamaño del efecto
- **THEN** la fórmula es `r = (T+ − T−) / (n(n+1)/2)` (o su equivalente `1 − 4W/(n(n+1))` cuando `W=T−`)
- **AND** el rango declarado es coherente con la fórmula (no `[-1,+1]` como rango universal de `1 − 2W/(n(n+1))`)
- **AND** el valor reportado sobre el corpus real es `0,9667`, no `1,00`

#### Scenario: Sin W=0

- **WHEN** se busca `W = 0` en los archivos de sección
- **THEN** no aparece como resultado de la prueba sobre el corpus real
- **AND** el conteo de pares invertidos (12/200) es consistente con el estadístico reportado

### Requirement: Calibración de la confianza del clasificador

La tesis SHALL reportar la relación entre la confianza devuelta por el
clasificador y su exactitud. El capítulo de resultados MUST incluir al menos la
tabla de contingencia de confianza alta/baja contra acierto/error, y el capítulo
de discusión MUST interpretar su implicancia para el umbral de revisión humana
de 0,70.

#### Scenario: Tabla de contingencia o curva de calibración presente

- **WHEN** se lee el capítulo de resultados
- **THEN** existe una tabla o figura que cruza confianza con acierto/error
- **AND** se reportan al menos la precisión del segmento de confianza `>= 0,70` y la del segmento `< 0,70`

#### Scenario: Discusión de la anti-calibración

- **WHEN** se lee el capítulo de discusión
- **THEN** se reconoce que la precisión del segmento de confianza alta no supera a la del segmento de confianza baja (0,697 vs 0,758)
- **AND** se discute la implicancia de esta anti-calibración para el umbral de revisión humana de 0,70

### Requirement: Aritmética metodológica verificable

Toda proyección numérica del documento (horas-persona liberadas, universo
trimestral, tiempos de registro) SHALL ser reproducible a partir de los datos
declarados. Cuando una proyección derive de una multiplicación o división, el
documento MUST mostrar el cálculo explícito (en el cuerpo o en una nota al pie).

#### Scenario: Proyección de horas-persona con cálculo explícito

- **WHEN** se lee cualquier afirmación de horas-persona liberadas por período
- **THEN** se exponen los factores usados (ahorro por incidente × volumen) y el resultado aritmético
- **AND** el valor es compatible con los tiempos y el volumen declarados (no una cifra que implique un ahorro por incidente inexistente)

#### Scenario: Universo trimestral reconciliado con el volumen diario

- **WHEN** se leen las afirmaciones de incidentes por día y por trimestre
- **THEN** el número de días del período está declarado (calendario o laborables)
- **AND** el volumen trimestral es aritméticamente compatible con el volumen diario y los días declarados

#### Scenario: Intervención humana con una única definición o ambas explícitas

- **WHEN** se lee la variable "intervención humana" en la tabla de operacionalización y en los resultados
- **THEN** la definición es una sola (proporción de tiempo o de casos) o se reportan ambas de forma rotulada
- **AND** el valor del capítulo de resultados es consistente con la definición declarada

### Requirement: Rótulo correcto de la dispersión

El documento SHALL rotular correctamente las medidas de dispersión. Cuando
compare desvíos estándar, MUST decir "desvío estándar" (o "desviación típica"),
no "varianza"; cuando compare varianzas, MUST decir "varianza".

#### Scenario: Dispersión rotulada según la medida comparada

- **WHEN** se lee un pasaje que compara la dispersión de los tiempos manual y automatizado
- **THEN** el término empleado coincide con la medida efectivamente comparada (desvío estándar vs varianza)
- **AND** la razón citada es coherente con la medida rotulada

### Requirement: Coherencia técnica entre la tesis y el sistema implementado

El documento SHALL describir el flujo de clasificación, los canales, los
mecanismos de resiliencia y el perímetro de seguridad de forma consistente con
el código y la configuración versionados. Toda funcionalidad declarada como
implementada MUST existir en el repositorio; en su defecto, MUST presentarse como
limitación o trabajo futuro. Los residuos de la alineación tecnológica previa
SHALL quedar cerrados y su registro de decisiones anexado.

#### Scenario: Flujo de clasificación y gate correctos

- **WHEN** se lee la descripción del flujo de orquestación en N8N
- **THEN** el gate de revisión humana se describe como posterior a la clasificación (se clasifica y luego se evalúa la confianza)
- **AND** no se describe ningún modelo de lenguaje actuando en el canal telefónico

#### Scenario: Mecanismos de resiliencia verificados

- **WHEN** el documento declara un mecanismo de reintento, retroceso exponencial o cola de respaldo
- **THEN** el mecanismo existe en `n8n/workflow.json` o en `App/Backend`
- **AND** si no existe, la afirmación se reformula como limitación conocida y trabajo futuro

#### Scenario: Perímetro de seguridad consistente

- **WHEN** el documento declara terminación TLS en el proxy inverso
- **THEN** la versión de protocolo declarada coincide con la configuración de `nginx/nginx.conf`
- **AND** si el proxy no forma parte del despliegue publicado, la afirmación se redacta de forma condicional

#### Scenario: Vocabulario de categorías unificado

- **WHEN** el documento enumera las categorías de clasificación
- **THEN** coincide con los cinco sectores canónicos usados por el prompt y el backend, sin la categoría retirada "Operaciones"
- **AND** no queda ninguna referencia a un prompt con un número distinto de categorías

#### Scenario: Punteros de repositorio válidos

- **WHEN** el documento referencia un tag o un artefacto del repositorio (por ejemplo el corpus o el flujo exportado)
- **THEN** el tag existe en el repositorio (y se registra su hash) o la referencia se corrige al tag/ruta real
- **AND** la ruta apunta a un artefacto existente

#### Scenario: Residuos de C-18 cerrados y log anexado

- **WHEN** se revisan los residuos de la alineación tecnológica (por ejemplo la mención a `IMAP` frente a Outlook/Graph API)
- **THEN** las secciones afectadas quedan alineadas con el estado real
- **AND** el registro de decisiones del dictamen se adjunta como anexo del documento

### Requirement: Trazabilidad de la pregunta de investigación sobre el criterio humano

El documento SHALL garantizar que cada sub-pregunta e hipótesis enunciada tenga
un tratamiento empírico correspondiente, y SHALL explicar el origen y la
relación entre las mediciones preliminares y experimentales de tiempo.

#### Scenario: Sub-pregunta humana medida o retirada

- **WHEN** se lee la pregunta de investigación y sus sub-preguntas
- **THEN** la sub-pregunta sobre la exactitud del clasificador frente al criterio humano está medida sobre el mismo corpus, o ha sido retirada y la hipótesis reformulada
- **AND** no permanece una sub-pregunta sin respuesta empírica en el documento

#### Scenario: Medición preliminar y experimental reconciliadas

- **WHEN** se lee el tiempo de registro manual reportado en la introducción y en los resultados
- **THEN** se explica la relación entre la medición preliminar y la medición experimental
- **AND** se identifica el registro que respalda el tiempo declarado, de modo que la coincidencia no quede sin justificar
