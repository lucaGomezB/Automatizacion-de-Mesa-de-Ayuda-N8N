## ADDED Requirements

### Requirement: Afirmaciones sobre plataformas comerciales respaldadas o reformuladas como observación propia

Toda afirmación de contexto sobre el mercado o la adopción de plataformas
comerciales de mesa de ayuda en el estado del arte (`03-estado-del-arte.tex`)
SHALL estar respaldada por una referencia formal verificable o, en su defecto,
reformulada como observación propia documentada que explicite su base (por
ejemplo, la documentación pública de las plataformas consultada en una fecha
declarada). El documento MUST NOT presentar como hecho establecido, sin respaldo,
afirmaciones de dominancia de mercado, crecimiento de la adopción o superioridad
de una solución sobre el segmento. Cuando la afirmación se respalde con un informe
de mercado, su entrada bibliográfica SHALL agregarse de forma aditiva en
`Bibliography_base.bib` y SHALL resolver por DOI o página de aterrizaje; el
documento MUST NOT alterar entradas existentes ni las tipadas por c-104.

#### Scenario: Afirmación de dominancia de mercado acotada

- **WHEN** se lee en `03-estado-del-arte.tex` la afirmación sobre el segmento de soluciones comerciales ("dominado por plataformas integrales")
- **THEN** la afirmación cita una referencia formal verificable o se enuncia como observación propia con su base declarada
- **AND** no queda formulada como hecho de mercado sin respaldo

#### Scenario: Afirmación de crecimiento de la adopción acotada

- **WHEN** se lee la afirmación sobre el crecimiento sostenido de la adopción de capacidades de IA en plataformas comerciales
- **THEN** la afirmación cita una referencia formal verificable o se reformula como observación propia acotada a lo documentado
- **AND** no se sostiene como tendencia cuantitativa sin fuente

#### Scenario: Entrada bibliográfica nueva aditiva y resoluble

- **WHEN** se agrega un informe de mercado para respaldar una afirmación comercial
- **THEN** la entrada se agrega sin modificar entradas existentes y sigue la convención de claves `ApellidoAnio_palabra_clave`
- **AND** resuelve por DOI o página de aterrizaje

### Requirement: Umbral de migración a clasificador supervisado justificado o declarado indicativo

Toda mención del umbral de casos necesarios para migrar a un clasificador
supervisado entrenado con corpus propio SHALL estar justificada por un cálculo de
potencia o por una referencia a un régimen de aprendizaje documentado, o bien
SHALL declararse explícitamente como valor indicativo y no como umbral derivado.
El tratamiento SHALL ser consistente en todas las apariciones del documento
(`10-recomendaciones.tex`, `08-discusion.tex` y `12-anexos.tex`). El documento
MUST NOT repetir una cifra concreta como umbral fundado sin justificación
empírica.

#### Scenario: Umbral justificado o declarado indicativo

- **WHEN** se lee la recomendación de migración a un clasificador supervisado
- **THEN** el umbral se justifica con un cálculo de potencia o una referencia documentada, o se declara como valor indicativo
- **AND** no se presenta como umbral fundado sin sustento

#### Scenario: Consistencia entre las apariciones del umbral

- **WHEN** se comparan las menciones del umbral en `10-recomendaciones.tex`, `08-discusion.tex` y `12-anexos.tex`
- **THEN** todas emplean el mismo tratamiento (justificado o indicativo)
- **AND** no queda una mención con una formulación distinta de las demás

### Requirement: Priorización de las líneas de trabajo futuro sobre los defectos medidos

El capítulo de recomendaciones (`10-recomendaciones.tex`) SHALL priorizar
explícitamente las líneas de trabajo futuro que atacan los defectos medidos en el
estudio: la calibración del gate de confianza, la incorporación de un clasificador
supervisado con corpus propio y la corrección de la medición de intervención
humana. La priorización SHALL distinguir esas líneas de las extensiones genéricas
(canales adicionales, paneles, base de conocimientos) y SHALL ser coherente con
las limitaciones reconocidas en la discusión.

#### Scenario: Líneas prioritarias declaradas

- **WHEN** se lee la introducción o el cierre del capítulo de recomendaciones
- **THEN** el texto declara explícitamente cuáles líneas futuras son prioritarias
- **AND** entre ellas figuran la calibración del gate, el clasificador supervisado y la corrección de la medición de intervención

#### Scenario: Distinción respecto de las líneas genéricas

- **WHEN** se leen las líneas de canales adicionales, paneles o base de conocimientos
- **THEN** se presentan como extensiones no prioritarias o subordinadas a las líneas que atacan los defectos medidos
- **AND** la priorización es coherente con las limitaciones de la discusión
