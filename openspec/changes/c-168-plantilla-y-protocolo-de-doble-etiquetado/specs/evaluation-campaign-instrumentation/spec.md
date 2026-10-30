## Purpose

Define el instrumento y los protocolos de la campana de campo que producen, de forma
verificable y sin PII, los datos que la evaluacion necesita para medir el brazo manual,
la intervencion humana, el efecto de orden y el acuerdo entre etiquetadores con su
intervalo de confianza.

## ADDED Requirements

### Requirement: ECM-008 — Plantilla de doble etiquetado con campos minimos

El proyecto SHALL proveer una plantilla versionada `evaluation/data/plantilla_etiquetado.csv`
(UTF-8, separador `,`, encabezado obligatorio) que es el esquema UNICO de toda planilla
etiquetador x caso de la campana, adoptado por el doble etiquetado y por el brazo manual.
Las columnas MUST ser, en este orden: `id_caso`, `id_etiquetador`, `tarea`,
`sector_etiquetado`, `sectores_adicionales_etiquetados`, `inicio` y `timestamp`, donde:

- `id_caso` es igual al `id` de un caso del corpus indicado (`R001..R200` en el corpus de
  ajuste; prefijo `I` en el corpus independiente).
- `id_etiquetador` es un alias sin PII (`E1`, `E2` para doble etiquetado; `O1`, `O2` para
  operadores del brazo manual), nunca nombre, correo ni legajo.
- `tarea` vale `doble_etiquetado` o `brazo_manual`.
- `sector_etiquetado` es exactamente una de las cinco cadenas canonicas
  `Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`,
  `Bases de Datos` y `Sistemas` (sin tildes, sensibles a mayusculas), tomadas de
  `SECTORES_CANONICOS` de `evaluation/corpus.py` y nunca duplicadas como constantes
  propias.
- `sectores_adicionales_etiquetados` es una lista separada por `|`, posiblemente vacia,
  cuyos elementos son cadenas canonicas y que no repite `sector_etiquetado`.
- `inicio` es el instante ISO-8601 con zona horaria en que empieza la clasificacion del
  caso; es obligatorio para `brazo_manual` y opcional (puede ir vacio) para
  `doble_etiquetado`.
- `timestamp` es el instante ISO-8601 con zona horaria (por ejemplo
  `2026-11-03T14:05:00-03:00`) en que termina la clasificacion del caso.

Para `brazo_manual`, `inicio <= timestamp`, de modo que la duracion por caso
(`timestamp - inicio`) es la variable respuesta del efecto de orden sobre el tiempo del
operador.

La columna del etiquetador MUST NOT llamarse `sector_asignado` ni `sectores_adicionales`:
esos nombres quedan reservados al consenso del corpus. La variable sobre la que se
calcula el acuerdo entre etiquetadores es `sector_etiquetado`. La plantilla MUST NOT
contener columnas con PII ni la descripcion del caso. La planilla de doble etiquetado
validada MUST versionarse sin PII en `evaluation/data/campana/doble_etiquetado.csv`, junto
a `evaluation/data/campana/README.md` con su SHA-256 y su fecha; la conservacion de esa
tabla primaria es criterio de aceptacion de la campana.

#### Scenario: Dos registros por caso

- **WHEN** se completa la plantilla para un caso del corpus con dos etiquetadores
- **THEN** la planilla contiene dos filas con el mismo `id_caso`, la misma `tarea` y distinto `id_etiquetador` (`E1` y `E2`), cada una con su `sector_etiquetado` y su `timestamp`

#### Scenario: Plantilla sin PII y sin el nombre del consenso

- **WHEN** se inspecciona el encabezado de `evaluation/data/plantilla_etiquetado.csv`
- **THEN** contiene exactamente las siete columnas en orden, ninguna columna de PII ni `descripcion`, y ninguna columna llamada `sector_asignado` ni `sectores_adicionales`

#### Scenario: Corpus independiente con prefijo I

- **WHEN** se etiqueta el corpus independiente cuyos ids empiezan con `I`
- **THEN** se usa la misma plantilla con `id_caso` igual a esos ids, sin cambiar columnas ni separadores

#### Scenario: Tabla primaria versionada con hash

- **WHEN** existe `evaluation/data/campana/doble_etiquetado.csv`
- **THEN** pasa el validador de ECM-009 sin ofensas y su SHA-256 coincide con el declarado en `evaluation/data/campana/README.md`, junto con la fecha de versionado

### Requirement: ECM-009 — Validacion offline del doble etiquetado

El proyecto SHALL proveer en `evaluation/doble_etiquetado.py` la funcion pura
`validar_doble_etiquetado(registros, corpus, tarea)`, que recibe los registros como
secuencia de diccionarios, el corpus cargado con `cargar_corpus` y la tarea, y devuelve
un `ResultadoValidacion` con la lista de ofensas (cada una con regla, `id_caso`,
`id_etiquetador` y detalle) y un resumen (cantidad de casos, cantidad de registros y
etiquetadores). Es el UNICO validador de planillas de la campana: el brazo manual y el
corpus independiente lo reutilizan. Reglas:

- (a) etiquetadores fijos por `tarea`: para `doble_etiquetado`, exactamente dos
  `id_etiquetador` distintos; para `brazo_manual`, AMBOS operadores `O1` y `O2` (cada
  uno con al menos un registro) y ningun tercero;
- (b) cobertura: para `doble_etiquetado`, cada `id` del corpus tiene un registro de cada
  uno de los dos etiquetadores; para `brazo_manual`, cada `id` del corpus tiene registro
  de AL MENOS UN operador (la cobertura doble no es obligatoria);
- (c) sin duplicados: como maximo un registro por `(id_caso, id_etiquetador, tarea)`;
- (d) todo `id_caso` existe en el corpus indicado;
- (e) `sector_etiquetado` y cada adicional pertenecen a `SECTORES_CANONICOS`;
- (f) los adicionales no repiten `sector_etiquetado`;
- (g) `timestamp`, y `inicio` cuando no esta vacio, son ISO-8601 parseables con zona
  horaria;
- (h) sin PII: ninguna columna `nombre`, `email`, `correo`, `legajo`, `telefono` ni
  `descripcion` (sin distinguir mayusculas), y alias con forma `E<n>` para
  `doble_etiquetado` u `O<n>` para `brazo_manual`;
- (i) `tarea` vale `doble_etiquetado` o `brazo_manual`;
- (j) para `brazo_manual`, `inicio` es obligatorio y `inicio <= timestamp`; para
  `doble_etiquetado`, `inicio` puede ir vacio y, si se informa, MUST cumplir
  `inicio <= timestamp`.

El CLI `python -m evaluation.doble_etiquetado --planilla RUTA --corpus RUTA --tarea TAREA`
MUST leer el CSV, reportar todas las ofensas y salir con `0` si no hay ofensas o con el
codigo de la primera regla ofendida en orden (a) 10, (b) 11, (c) 12, (d) 13, (e) 14,
(f) 15, (g) 16, (h) 17, (i) 18, (j) 19, y `2` ante errores de uso o archivo ilegible. La
herramienta MUST operar sin red ni servicios externos. El calculo con mas de dos
etiquetadores (Fleiss) queda fuera del alcance.

#### Scenario: Regla (a) tercer etiquetador

- **WHEN** una planilla de `doble_etiquetado` contiene registros de `E1`, `E2` y `E3`
- **THEN** la validacion falla por la regla (a) identificando `E3` y el CLI sale con codigo 10

#### Scenario: Regla (a) tercer operador en el brazo manual

- **WHEN** una planilla de `brazo_manual` contiene registros de `O1`, `O2` y `O3`
- **THEN** la validacion falla por la regla (a) identificando `O3` y el CLI sale con codigo 10

#### Scenario: Regla (a) un solo operador en el brazo manual

- **WHEN** una planilla de `brazo_manual` solo contiene registros de `O1`, aunque cubra todos los casos del corpus
- **THEN** la validacion falla por la regla (a) indicando que falta `O2` y el CLI sale con codigo 10

#### Scenario: Regla (b) cobertura incompleta en el doble etiquetado

- **WHEN** en una planilla de `doble_etiquetado` un caso del corpus no tiene registro de uno de los dos etiquetadores
- **THEN** la validacion falla por la regla (b) identificando el `id_caso` y el `id_etiquetador` faltantes y el CLI sale con codigo 11

#### Scenario: Regla (b) cobertura parcial valida en el brazo manual

- **WHEN** en una planilla de `brazo_manual` cada caso del corpus tiene registro de exactamente uno de `O1` u `O2` y algunos casos tienen registro de ambos
- **THEN** la validacion no reporta ofensas por la regla (b)

#### Scenario: Regla (b) caso sin ningun operador en el brazo manual

- **WHEN** en una planilla de `brazo_manual` un caso del corpus no tiene registro de ningun operador
- **THEN** la validacion falla por la regla (b) identificando ese `id_caso` y el CLI sale con codigo 11

#### Scenario: Regla (c) registro duplicado

- **WHEN** existen dos filas con la misma terna `(id_caso, id_etiquetador, tarea)`
- **THEN** la validacion falla por la regla (c) identificando la terna y el CLI sale con codigo 12

#### Scenario: Regla (d) id de caso desconocido

- **WHEN** una fila tiene un `id_caso` que no existe en el corpus indicado
- **THEN** la validacion falla por la regla (d) identificando ese `id_caso` y el CLI sale con codigo 13

#### Scenario: Regla (e) sector no canonico

- **WHEN** `sector_etiquetado` o un adicional vale `Soporte Técnico Hardware`, `sistemas` u `Operaciones`
- **THEN** la validacion falla por la regla (e) identificando el registro y el valor, y el CLI sale con codigo 14

#### Scenario: Regla (f) adicional repite el principal

- **WHEN** una fila tiene `sector_etiquetado` igual a `Sistemas` y adicionales `Sistemas|Bases de Datos`
- **THEN** la validacion falla por la regla (f) identificando el registro y el CLI sale con codigo 15

#### Scenario: Regla (g) timestamp invalido

- **WHEN** el `timestamp` de una fila es `03/11/2026 14:05`, carece de zona horaria o esta vacio
- **THEN** la validacion falla por la regla (g) identificando el registro y el CLI sale con codigo 16

#### Scenario: Regla (h) columna con PII

- **WHEN** la planilla contiene una columna `nombre`, `email`, `correo`, `legajo`, `telefono` o `descripcion`, o un `id_etiquetador` que no tiene la forma de alias de la tarea
- **THEN** la validacion falla por la regla (h) identificando la columna o el alias y el CLI sale con codigo 17

#### Scenario: Regla (i) tarea invalida

- **WHEN** una fila o el argumento `--tarea` tiene un valor distinto de `doble_etiquetado` y `brazo_manual`
- **THEN** la validacion falla por la regla (i) y el CLI sale con codigo 18

#### Scenario: Regla (j) inicio ausente en el brazo manual

- **WHEN** una fila de `brazo_manual` tiene `inicio` vacio
- **THEN** la validacion falla por la regla (j) identificando el `id_caso` y el `id_etiquetador`, y el CLI sale con codigo 19

#### Scenario: Regla (j) inicio posterior al fin

- **WHEN** una fila de `brazo_manual` tiene `inicio` igual a `2026-11-03T14:10:00-03:00` y `timestamp` igual a `2026-11-03T14:05:00-03:00`
- **THEN** la validacion falla por la regla (j) identificando el registro y el CLI sale con codigo 19

#### Scenario: Inicio vacio admitido en el doble etiquetado

- **WHEN** una fila de `doble_etiquetado` tiene `inicio` vacio y un `timestamp` valido
- **THEN** la validacion no reporta ofensas por las reglas (g) ni (j) para esa fila

#### Scenario: Planilla valida habilita el consumo

- **WHEN** una planilla de `doble_etiquetado` cubre todos los casos del corpus con exactamente dos alias, sin duplicados, con sectores canonicos, `inicio` y `timestamp` validos y sin PII
- **THEN** la validacion no reporta ofensas, el resumen informa casos, registros y etiquetadores, y el CLI sale con codigo 0

### Requirement: ECM-010 — Protocolo de doble etiquetado independiente y ruta de recuperacion

El proyecto SHALL incluir el runbook `docs/campana-medicion/runbook-doble-etiquetado.md`,
ejecutable sin conocimiento tacito, que defina:

- Sujetos: `E1` y `E2` MUST ser personas distintas entre si, distintas de los dos
  analistas que fijaron el consenso original, distintas de los autores de la tesis y
  distintas de los operadores del brazo manual (`O*`).
- Cegado: los etiquetadores MUST NOT ver `sector_asignado` ni `sectores_adicionales` del
  corpus, ni la prediccion del clasificador, ni las etiquetas del otro etiquetador.
- Codebook: el mismo para ambos etiquetadores, congelado antes de etiquetar y compuesto a
  partir de `openspec/specs/sector-taxonomy/spec.md`, `docs/anexo_f_corpus.md` y
  `knowledge-base/05_reglas_de_negocio.md`, sin materiales del clasificador.
- Registro de sujetos `evaluation/data/campana/registro_sujetos.csv` sin nombres, con
  columnas `alias`, `rol` (`etiquetador`, `operador`, `analista_original` o `autor`) y
  `persona` (codigo seudonimo `P<n>` estable entre roles, cuya correspondencia con
  identidades se custodia fuera del repositorio); el solape se detecta por `persona`.
- Tamano: los 200 casos del corpus de ajuste completos; el corpus independiente usa la
  misma plantilla y el mismo validador con `id_caso` de prefijo `I`.
- Aceptacion: el validador de ECM-009 sin ofensas, y la tabla primaria versionada con
  SHA-256 segun ECM-008.
- Discordancias: MUST NOT resolverse por consenso a posteriori para el calculo del
  kappa; la referencia para medir el brazo manual son los casos donde coinciden `E1` y
  `E2`, y los discordantes quedan fuera de esa referencia.
- Limitacion declarada: si no se consiguen etiquetadores nuevos, se registra como
  limitacion y MUST NOT presentarse como cegado.
- Recuperacion: si reaparece una tabla parcial del etiquetado original, se transcribe a
  mano al esquema de ECM-008 y se pasa por el mismo validador; no hay codigo de
  importacion y el camino por defecto es el re-etiquetado.

#### Scenario: Etiquetador que coincide con un analista original es inelegible

- **WHEN** una persona propuesta como `E1` o `E2` es uno de los dos analistas que fijaron el consenso original, un autor de la tesis o un operador del brazo manual
- **THEN** el runbook la declara inelegible como etiquetador y exige reemplazarla o registrar la limitacion

#### Scenario: Limitacion declarada

- **WHEN** por restricciones de campo no se consiguen etiquetadores distintos de los analistas originales, autores u operadores
- **THEN** `evaluation/data/campana/README.md` registra `estado_cegado: limitacion_declarada` con el motivo y los roles solapados, y el resultado se reporta como limitacion y no como etiquetado ciego

#### Scenario: Registro de sujetos sin nombres

- **WHEN** se inspecciona `evaluation/data/campana/registro_sujetos.csv`
- **THEN** cada fila tiene `alias`, un `rol` en `etiquetador`, `operador`, `analista_original` o `autor` y una `persona` seudonima, sin nombres, correos ni legajos, de modo que el analisis pueda rechazar como solape una misma `persona` con rol `etiquetador` y cualquier otro rol

#### Scenario: Discordancias no se consensuan para el kappa

- **WHEN** `E1` y `E2` asignan distinto `sector_etiquetado` a un caso
- **THEN** el runbook prohibe resolver esa discordancia antes de calcular el kappa, que se computa sobre las etiquetas tal como se registraron

#### Scenario: Consenso por coincidencia como referencia del brazo manual

- **WHEN** se arma la referencia para medir la exactitud del brazo manual
- **THEN** la referencia incluye solo los casos donde `E1` y `E2` coinciden en `sector_etiquetado`, excluye los discordantes y reporta cuantos quedaron fuera

#### Scenario: Recuperacion manual de una tabla parcial

- **WHEN** reaparece una tabla parcial con etiquetas por analista original
- **THEN** el runbook indica transcribirla a mano al esquema de ECM-008 y pasarla por el validador de ECM-009, sin codigo de importacion, manteniendo el re-etiquetado como camino por defecto
