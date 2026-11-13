## ADDED Requirements

### Requirement: GSOLO-001 — Brazo «Gemini solo» con la etapa congelada

El ejecutor SHALL clasificar los 200 casos del corpus de ajuste y los 103 casos del bloque fuera
de muestra con la etapa Gemini REAL del backend (mismo modelo, prompt, parámetros de muestreo,
validación del Anexo H y reintentos que el híbrido), sin reglas determinísticas, inyectándole un
cliente instrumentado. MUST NOT duplicar el prompt ni la validación ni modificar `App/Backend/`.
Antes de la primera llamada SHALL verificar que el SHA-256 del prompt cargado coincide con el de
`docs/prompt_gemini.txt`.

#### Scenario: Todos los casos pasan por Gemini

- **WHEN** el ejecutor procesa un conjunto de casos con un cliente simulado
- **THEN** cada caso produce exactamente un registro con `etapa` `gemini` o `fallback` y ninguno con `deterministic`
- **AND** el cliente simulado recibió el prompt completo con la descripción del caso

#### Scenario: Prompt distinto del congelado

- **WHEN** el prompt cargado por el backend difiere de `docs/prompt_gemini.txt`
- **THEN** el ejecutor aborta antes de la primera llamada con un error que nombra ambos SHA-256

### Requirement: GSOLO-002 — Caché incremental y registro por caso

El ejecutor SHALL escribir un caché JSONL con una línea de metadatos (hashes de corpus, modelo,
parámetros, SHA-256 del prompt, versión del SDK, precios, tope) y una línea por caso terminado,
con predicción, confianza, etapa, intentos, latencia total y por intento, tokens de entrada,
salida y total, origen de los tokens y error. SHALL persistir cada caso apenas termina y, al
reanudar, SHALL omitir los casos ya registrados sin volver a llamar. SHALL abortar si los
metadatos del caché existente no coinciden con los de la corrida actual.

#### Scenario: Reanudación tras un corte

- **WHEN** una corrida se corta tras registrar parte de los casos y se relanza sobre el mismo caché
- **THEN** solo se llama para los casos no registrados y el total de registros es el de todos los casos sin duplicados

#### Scenario: Metadatos incompatibles

- **WHEN** el caché existente fue escrito con otro modelo, otro prompt o otro hash de corpus
- **THEN** el ejecutor aborta sin llamar y sin modificar el caché

### Requirement: GSOLO-003 — Tope duro de llamadas

El ejecutor SHALL contar cada intento a la API, reintentos incluidos, de forma acumulada entre
reanudaciones, y distinguir los intentos que obtuvieron respuesta del modelo de los que fallaron
antes de obtenerla (fallo técnico: indisponibilidad o transporte, sin tokens). El tope de 400 SHALL
aplicarse a las llamadas con respuesta del modelo; los intentos sin respuesta SHALL contarse e
informarse aparte y no consumir ese tope. Un cinturón de seguridad SHALL acotar los intentos
totales (con o sin respuesta) en 600. El ejecutor MUST NOT emitir una llamada que superaría
cualquiera de los dos topes, y ninguno SHALL poder aumentarse por línea de comandos. Al alcanzar
uno SHALL conservar lo hecho, informar los casos pendientes y terminar con un código de salida
distinto de cero específico.

#### Scenario: Tope alcanzado

- **WHEN** el contador acumulado de llamadas con respuesta (400) o de intentos totales (600) alcanza su tope con casos pendientes
- **THEN** el cliente instrumentado no emite más llamadas, el caché conserva los casos terminados y el ejecutor sale con código 3

#### Scenario: Tope superior al prerregistrado

- **WHEN** se pide un tope de respuestas mayor que 400 o un tope de intentos mayor que 600
- **THEN** el ejecutor aborta antes de llamar con un mensaje que cita el tope prerregistrado

#### Scenario: Intento sin respuesta del modelo

- **WHEN** un intento falla por indisponibilidad o transporte y no produce tokens
- **THEN** se cuenta como intento, se informa como intento sin respuesta y no consume el tope de 400 respuestas

### Requirement: GSOLO-004 — Guardas de costo, entorno y credencial

El ejecutor SHALL exigir `--confirmar-costo` para llamar a la API; sin él, SHALL abortar con
código 2 sin llamar. SHALL verificar que la versión de `google-genai` cumpla `>=2.33,<3` y abortar
con un mensaje claro si no. SHALL leer `GEMINI_API_KEY` únicamente del entorno en tiempo de
ejecución, y MUST NOT imprimirla, registrarla ni guardarla. El modo `--dry-run` SHALL contar los
casos pendientes, las llamadas mínimas y máximas y el costo estimado sin llamar a la API, sin leer
la clave y sin escribir el caché.

#### Scenario: Corrida sin confirmación

- **WHEN** se ejecuta sin `--confirmar-costo` y sin `--dry-run`
- **THEN** el código de salida es 2, no se emite ninguna llamada y el mensaje nombra el flag

#### Scenario: Versión de SDK fuera del pin

- **WHEN** la versión instalada de `google-genai` es menor que 2.33 o mayor o igual que 3
- **THEN** el ejecutor aborta con un mensaje que cita la versión instalada y el rango exigido

#### Scenario: Dry-run sin efectos

- **WHEN** se ejecuta con `--dry-run`
- **THEN** imprime casos pendientes, llamadas mínimas y máximas y costo estimado en ambos escenarios de precio
- **AND** no emite llamadas, no escribe el caché y no imprime ningún valor de credencial

### Requirement: GSOLO-005 — Análisis pareado y eficiencia

El análisis SHALL tomar el caché del brazo y las predicciones congeladas de `hybrid-v3` y producir,
por bloque, exactitud estricta y laxa con IC de Wilson, macro-F1, la tabla 2×2 y McNemar exacta
bilateral, la diferencia de exactitudes con IC95 bootstrap pareado (semilla 20261021), las razones
de llamadas y de costo con IC95, tokens y latencia por caso, y la sensibilidad H\*. Las salidas
SHALL ser JSON y Markdown deterministas (LF, UTF-8 sin BOM) con SHA-256. SHALL abortar sin escribir
si el caché no existe, está incompleto o su hash de corpus difiere del vigente.

#### Scenario: Contraste con cachés sintéticos

- **WHEN** el análisis corre sobre cachés sintéticos de H y L con aciertos conocidos
- **THEN** la tabla 2×2, la diferencia de exactitudes y el p de McNemar coinciden con el cálculo manual

#### Scenario: Caché real inexistente

- **WHEN** no existe el caché del brazo
- **THEN** el análisis termina con código distinto de cero, un mensaje claro y sin escribir salidas

#### Scenario: Salidas deterministas

- **WHEN** el análisis corre dos veces sobre las mismas entradas
- **THEN** las salidas JSON y Markdown son idénticas byte a byte

### Requirement: GSOLO-006 — Regla de decisión prerregistrada y control de deriva

El análisis SHALL aplicar sobre el bloque primario de 103 casos la regla de tres vías de
`design.md` D7 (margen de no inferioridad 0,05; eficiencia cumplida si el límite superior del IC de
las razones de costo y de llamadas es menor que 0,90) y SHALL emitir «sostenida», «no sostenida» o
«no concluyente». SHALL forzar «no concluyente» si los `fallback` o errores del brazo superan 5 %
del bloque. SHALL calcular el control de deriva como la concordancia, con IC de Wilson, entre la
nueva predicción de Gemini y la cacheada de H en los casos que H ya escaló, y marcar la bandera si
es menor que 0,90. Los análisis secundarios MUST NOT cambiar el veredicto.

#### Scenario: Hipótesis sostenida

- **WHEN** el límite inferior del IC de `Δ` es mayor que −0,05 y los límites superiores de ambas razones son menores que 0,90
- **THEN** el veredicto es «sostenida»

#### Scenario: Hipótesis no sostenida por inferioridad

- **WHEN** el límite superior del IC de `Δ` es menor que −0,05
- **THEN** el veredicto es «no sostenida» aunque la eficiencia se cumpla

#### Scenario: Indeterminado con eficiencia cumplida

- **WHEN** el IC de `Δ` contiene −0,05 y la eficiencia se cumple
- **THEN** el veredicto es «no concluyente»

#### Scenario: Corrida con demasiados fallos

- **WHEN** más de 5 % de los casos del bloque primario del brazo L terminaron en `fallback` o error
- **THEN** el veredicto es «no concluyente» y el motivo figura en las salidas

#### Scenario: Bandera de deriva

- **WHEN** la concordancia con las predicciones cacheadas de H en los casos escalados es menor que 0,90
- **THEN** las salidas incluyen la bandera de deriva o ruido relevante
