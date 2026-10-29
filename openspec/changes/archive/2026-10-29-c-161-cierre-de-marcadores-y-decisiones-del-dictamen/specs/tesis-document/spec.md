## ADDED Requirements

### Requirement: Cierre verificado de los pendientes Q1 a Q8 del dictamen

Los datos de las corridas de la campana que el repositorio no documentaba SHALL cerrarse en las fuentes de la tesis con la respuesta verificada de los autores o, cuando el dato no exista o no se conserve, con la declaracion explicita de que no consta; ninguno MUST inventarse. Las fuentes `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` (subseccion `subsec:protocolo-pruebas`) y `12-anexos.tex` (Anexo F, `sec:anexo-corpus`) MUST NOT conservar marcadores `% PENDIENTE AUTORES`. En particular: la corrida telefonica SHALL fecharse el 5 y el 6 de octubre de 2026 (25 y 56 casos; duracion aproximada de 2 h y 3 h, sin horas de reloj exactas), la version desplegada que proceso los 56 casos del 6-10 SHALL declararse desconocida, el recitado de las 81 llamadas SHALL atribuirse a un autor con lectura parafraseada desde un softphone (dispositivo SF20GM7, con repeticiones y un listado exacto pendiente), y el intervalo efectivo del disparador IMAP, el host SMTP del arnes de ingesta y la reasociacion de la `cache_meta` de `hybrid-v3` SHALL declararse no documentados. El Anexo F SHALL declarar que los registros primarios (base operativa del 2-10, respaldo del 9-10 de los 81 ingresos telefonicos y ejecuciones de N8N) no se conservan en el repositorio. La respuesta a cada consulta SHALL registrarse con su estado (cerrada o no consta) en `docs/Tesis/Correcciones/dictamen-correcciones.md`, sin reescribir las entradas provisionales previas.

#### Scenario: Marcadores ausentes de las fuentes

- **WHEN** se busca con `grep` la cadena `PENDIENTE AUTORES` en `docs/Tesis/v10 (IA)/paper/sections/`
- **THEN** no queda ninguna coincidencia en `04-marco-metodologico.tex` ni en `12-anexos.tex`

#### Scenario: Fechas telefonicas corregidas

- **WHEN** se lee la subseccion 4.5 y la subseccion 1.8 (`subsec:alcance-delimitaciones`), la leyenda de la figura telefonica y el cronograma
- **THEN** la corrida telefonica se fecha el 5 y el 6 de octubre de 2026
- **AND** no aparece la corrida telefonica fechada solo el 6 de octubre

#### Scenario: Dato faltante declarado como no consta

- **WHEN** se lee el apartado de procedencia de 4.5 y el Anexo F
- **THEN** la version desplegada, el intervalo efectivo del disparador IMAP, el host SMTP y la reasociacion de la `cache_meta` se declaran no constatables
- **AND** los registros primarios se declaran no conservados en el repositorio

#### Scenario: Cierre registrado en el ledger

- **WHEN** se lee la seccion de c-161 de `docs/Tesis/Correcciones/dictamen-correcciones.md`
- **THEN** figura el cierre de cada consulta Q1 a Q8 con su respuesta o su estado no consta
- **AND** las entradas provisionales previas se conservan como historia

## MODIFIED Requirements

### Requirement: Naturaleza de los dictamenes declarada en el Anexo I

El primer parrafo del Anexo I (`12-anexos.tex`, `sec:anexo-trazabilidad`) SHALL explicar la naturaleza de los dictamenes cuyas correcciones traza: que son autoevaluaciones de control de calidad interno frente a criterios de la CONEAU, es decir revisiones evaluativas previas a la defensa solicitadas por los propios autores y no una revision por pares; el instrumento con que se elaboraron, tal como consta en el repositorio (perfil de evaluador con criterios de la CONEAU versionado en `docs/Tesis/Correcciones/Prompt2.docx` y su modo de aplicacion mediante un modelo de lenguaje); la serie y sus fechas (del 20 al 28 de octubre de 2026) y los dictamenes que el anexo traza (22 de octubre, sobre `v1.1.0`, y 28 de octubre, sobre `v1.2.5`); su alcance segun consta en cada dictamen; su caracter no vinculante; y su ubicacion en `auditorias/` junto con la ruta del registro `docs/Tesis/Correcciones/dictamen-correcciones.md`. El parrafo MUST NOT atribuir los dictamenes al jurado, a la direccion, a la catedra ni a la CONEAU, ni presentarlos como revision por pares humana si el repositorio no lo respalda. La decision de conservar el Anexo I en el PDF, con su extension medida en paginas, SHALL registrarse en el registro de correcciones.

#### Scenario: Naturaleza explicada al inicio

- **WHEN** se lee el primer parrafo del Anexo I en el PDF compilado
- **THEN** declara que los dictamenes son autoevaluaciones de control de calidad interno previas a la defensa, solicitadas por los autores, no vinculantes, y nombra el instrumento y su ubicacion en el repositorio
- **AND** identifica los dictamenes del 22 y del 28 de octubre de 2026 con la version examinada por cada uno

#### Scenario: Sin atribucion indebida

- **WHEN** se busca en el Anexo I la atribucion de los dictamenes a un jurado, a la direccion, a la catedra o a la CONEAU
- **THEN** no aparece ninguna

#### Scenario: Conservacion documentada

- **WHEN** se lee la seccion de c-160 del registro de correcciones
- **THEN** figura la decision de conservar el Anexo I con su extension medida en paginas y las alternativas evaluadas

### Requirement: Procedencia de los datos del brazo automatizado declarada en el protocolo de pruebas

La subseccion "Protocolo de pruebas" (`subsec:protocolo-pruebas`, `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex`) SHALL incluir un apartado titulado "Procedencia de los datos del brazo automatizado" que declare, con la precision de su evidencia en el repositorio: (a) la corrida de tiempos de correo electronico y formulario web del 2-10-2026 (119 casos), su procedimiento de inyeccion por el arnes de ingesta a traves de los canales reales del flujo N8N, el texto inyectado, la metrica (desde el envio hasta la persistencia, con la espera de recogida del disparador IMAP en el correo y su configuracion declarada) y la configuracion del clasificador vigente ese dia (`hybrid-v1`: vocabulario de 89 patrones, prompt sin reglas de frontera y cortocircuito por confianza determinista >= 0,90); (b) la corrida telefonica concluida el 6-10-2026 (81 casos), su procedimiento (softphone de navegador, lectura parafraseada de la descripcion pseudonimizada, grabacion acotada a 45 s, entorno de medicion aislado) y la imposibilidad de asignarle una configuracion unica del clasificador, anterior en todo caso a c-74; (c) la corrida de clasificacion `hybrid-v3` del 7-10-2026 (22:22 UTC) como ejecucion fuera de linea del framework de evaluacion sobre el corpus JSON, con su archivo de evidencia versionado y el hash del corpus; y (d) el recalculo del tiempo telefonico del 19-10-2026 y su motivo. El apartado MUST NOT afirmar hechos que el repositorio no documenta (version desplegada en el entorno de medicion, intervalo efectivo de sondeo, host SMTP del arnes, fuente de texto distinta de la documentada); cada dato faltante SHALL declararse en el texto como "no consta" y registrarse con ese estado en `docs/Tesis/Correcciones/dictamen-correcciones.md`, sin dejar marcadores `% PENDIENTE AUTORES` en la fuente. Si el apartado afirma la direccion del sesgo de los tiempos respecto de la configuracion evaluada, SHALL presentarla como inferencia y no como medicion.

#### Scenario: Corridas fechadas y separadas

- **WHEN** se lee el apartado de procedencia de la Seccion 4.5 del PDF compilado
- **THEN** figuran la corrida del 2-10-2026 (correo y formulario, 119 casos), la corrida telefonica del 5 y el 6 de octubre de 2026 (81 casos), la clasificacion fuera de linea `hybrid-v3` del 7-10-2026 y el recalculo telefonico del 19-10-2026
- **AND** el texto ya no describe un unico procesamiento "sobre la misma infraestructura" ni un "monitoreo continuo" sin respaldo

#### Scenario: Procedimiento de inyeccion documentado

- **WHEN** se busca en el apartado quien o que introdujo los casos por cada canal y con que texto
- **THEN** declara que el arnes de ingesta envio los 119 casos de correo y formulario por los canales reales del flujo y que en telefonia una persona leyo la descripcion pseudonimizada desde un softphone de navegador
- **AND** el intervalo del disparador IMAP se presenta como configuracion declarada del flujo, no como medicion

#### Scenario: Configuracion del clasificador por corrida segun el historial

- **WHEN** se compara la configuracion declarada para cada corrida con `git log` y con los changes archivados c-68, c-70, c-71, c-72 y c-74
- **THEN** la corrida del 2-10 se describe con la configuracion `hybrid-v1` del commit `24ab238`
- **AND** la corrida telefonica no se describe como anterior a c-71 ni se le asigna una revision unica, y se la declara anterior a c-74

#### Scenario: Corrida de clasificacion fuera de linea

- **WHEN** se lee la descripcion de la corrida de clasificacion
- **THEN** remite a `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`, consigna el hash del corpus que registra la evidencia y la presenta como ejecucion del framework de evaluacion sin pasar por los canales
- **AND** la asocia a la version `hybrid-v3` que versiona el commit `d6bb474`, sin afirmar que se ejecuto sobre ese commit

#### Scenario: Datos faltantes marcados y no inventados

- **WHEN** se inspecciona la fuente `04-marco-metodologico.tex` y el PDF compilado
- **THEN** cada dato que el repositorio no documenta aparece declarado en el texto como "no consta" y no inventado, sin quedar bajo un comentario `% PENDIENTE AUTORES:`
- **AND** la misma consulta figura cerrada con ese estado en la seccion de c-161 de `dictamen-correcciones.md`

### Requirement: Descripcion exacta del tiempo telefonico y de la fuente del cronograma

La Seccion 6.4 (`06-implementacion.tex`, `subsec:integracion-canal-telefonico`) SHALL describir el tiempo automatizado telefonico como la suma de la duracion de la grabacion y la latencia desde el cuelgue hasta la persistencia del incidente, y MUST NOT describirlo como medido desde el inicio de la llamada hasta la confirmacion del numero de incidente. La corrida telefonica SHALL fecharse el 5 y el 6 de octubre de 2026 en la subseccion 1.8 (`subsec:alcance-delimitaciones`), en la subseccion 4.5, en la leyenda de la figura telefonica de resultados y en el cronograma (fuente `docs/diagrams/cronograma.md` y `fig:cronograma`). La leyenda de la figura del cronograma (`fig:cronograma`, `12-anexos.tex`) SHALL distinguir la fuente de los hitos (historial del repositorio, incluido el recalculo del tiempo telefonico del 19-10-2026) de la respuesta de los autores del 2026-10-28 sobre las fechas de la corrida telefonica, y SHALL usar un titulo corto para el indice de figuras.

#### Scenario: Tiempo telefonico descrito como se midio

- **WHEN** se lee la Seccion 6.4
- **THEN** el tiempo telefonico se describe como duracion de la grabacion mas latencia hasta la persistencia, con la grabacion acotada a 45 s
- **AND** no aparece "desde el inicio de la llamada hasta la confirmacion del numero de incidente"

#### Scenario: Fecha de la corrida telefonica en los cuatro pasajes

- **WHEN** se leen la subseccion 1.8, la subseccion 4.5, la leyenda de la figura telefonica y el cronograma
- **THEN** los cuatro fechan la corrida telefonica el 5 y el 6 de octubre de 2026

#### Scenario: Leyenda coherente con el hito del 19-10

- **WHEN** se lee la leyenda de la figura del cronograma
- **THEN** atribuye los hitos, incluido el del 19-10-2026, al historial del repositorio y la respuesta del 2026-10-28 a las fechas de la corrida telefonica
- **AND** la entrada del indice de figuras usa el titulo corto

### Requirement: Figura de arquitectura del sistema de cinco capas y tres canales desde fuente versionada

La figura `fig:arquitectura` SHALL representar la arquitectura de cinco capas de la Tabla `tab:capas` (canales de entrada, orquestacion, procesamiento, inferencia y persistencia) con sus tres canales de entrada (correo electronico, formulario web y telefonia) y SHALL generarse desde la fuente Mermaid versionada `docs/diagrams/arquitectura_sistema.md`, que es la unica fuente de la figura. La figura MUST NOT representar un flujo de un solo canal como arquitectura del sistema ni contener erratas ortograficas. Su leyenda MUST NOT remitir a un detalle del Anexo A que el anexo no contenga, y el Anexo A (`sec:anexo-diagrama-arquitectura`) SHALL inventariar la fuente versionada de la figura junto con las de los demas diagramas. El diagrama retirado `docs/diagrams/Diagrama de Capas.drawio` (y su PNG) MUST NOT figurar como fuente vigente de la figura ni quedar en el arbol activo de diagramas: SHALL archivarse bajo `docs/diagrams/` o retirarse, y toda referencia a el SHALL actualizarse. El PNG de la figura MUST NOT regenerarse en este change.

#### Scenario: Cinco capas y tres canales

- **WHEN** se inspecciona el PNG `arquitectura_sistema.png`
- **THEN** figuran las cinco capas de la Tabla `tab:capas` y los tres canales de entrada
- **AND** el canal telefonico se representa como Twilio con transcripcion en el backend y entrega a N8N, coherente con `n8n/workflow.json`

#### Scenario: Fuente versionada y reproducible

- **WHEN** se renderiza el bloque Mermaid de `docs/diagrams/arquitectura_sistema.md`
- **THEN** el resultado coincide en contenido con el PNG embebido en la tesis
- **AND** la version de `mmdc` usada queda registrada en el registro del dictamen

#### Scenario: Drawio retirado y sin referencias vigentes

- **WHEN** se busca `Diagrama de Capas` en las fuentes y los documentos del repositorio
- **THEN** ninguna referencia lo presenta como fuente vigente de `fig:arquitectura`
- **AND** el archivo `docs/diagrams/Diagrama de Capas.drawio` y su PNG ya no estan en el arbol activo de diagramas

#### Scenario: Sin remision colgada ni erratas

- **WHEN** se lee la leyenda de `fig:arquitectura` y se inspecciona la figura
- **THEN** la leyenda no remite a un detalle del Anexo A
- **AND** la figura no contiene "responsablle" ni "SI" sin tilde

#### Scenario: Fuente inventariada en el Anexo A

- **WHEN** se lee el Anexo A en el PDF compilado
- **THEN** lista la figura de arquitectura con su fuente `docs/diagrams/arquitectura_sistema.md`

### Requirement: Declaracion acotada del endurecimiento tecnico

La tesis SHALL declarar cada capacidad de endurecimiento tecnico (TLS verificado en el borde, reintentos idempotentes del alta, prueba de humo de extremo a extremo) solo si el bloque correspondiente del change c-140 esta aplicado y verificado en el repositorio, y SHALL conservar la redaccion de limitacion vigente para todo bloque no aplicado. En particular: (a) TLS se declara verificado en el despliegue de referencia de la release, en `05-arquitectura.tex` (`subsec:vision-general`), `11-aspectos-legales.tex` (`subsec:seguridad-tecnica`) y el Anexo A, aclarando que el certificado de referencia es autofirmado, que la terminacion TLS esta verificada solo sobre el despliegue de referencia y que las mediciones no dependen de TLS. Asimismo distinguen los dos despliegues de la campana: la medicion telefonica del 5 y 6 de octubre corrio sobre el perfil Compose aislado `corpus` (`postgres-corpus`, `backend-corpus`, `n8n-corpus`), que NO incluye el proxy inverso Nginx y usa su propio tunel a `backend-corpus`; la ingesta del brazo automatico del 2 de octubre (correo y formulario web, anterior a c-70) corrio sobre el stack base, que SI incluye Nginx con el certificado autofirmado de referencia; en ningun caso las mediciones dependen de TLS; (b) el primer y el tercer desafio de `06-implementacion.tex` (`subsec:desafios-integracion`) describen la invocacion de alta como sincronica con reintento acotado e idempotente, con los valores de `n8n/workflow.json`, el desvio a la rama de error tras agotar los intentos y la semantica de `clasificacion_log` (un registro por clasificacion ejecutada; los replays no agregan registros), y `10-recomendaciones.tex` conserva la cola de respaldo y el alta asincronica como trabajo futuro; (c) el §6.7 (`subsec:pruebas-automatizadas`) describe la prueba de humo con su alcance exacto. Toda cifra nueva citada (intentos, esperas, tiempos maximos) SHALL registrarse en `docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md` con su fuente. Los resultados del capitulo 7 MUST NOT modificarse por este motivo.

#### Scenario: TLS declarado sin sobreafirmar

- **WHEN** se leen `subsec:vision-general`, `subsec:seguridad-tecnica` y el Anexo A con el bloque TLS aplicado
- **THEN** declaran TLS 1.2/1.3 en Nginx como verificado en el despliegue de referencia mediante la prueba automatizada del borde
- **AND** declaran que la terminacion TLS esta verificada solo sobre el despliegue de referencia y que las mediciones no dependen de TLS
- **AND** distinguen que la medicion telefonica corrio sobre el perfil aislado `corpus` (que no incluye Nginx) mientras que la ingesta del 2 de octubre corrio sobre el stack base (que si lo incluye)

#### Scenario: Reintentos declarados con los valores del workflow

- **WHEN** se leen el primer y el tercer desafio de `subsec:desafios-integracion` con el bloque de reintentos aplicado
- **THEN** los valores citados de intentos, espera y tiempo maximo coinciden con `n8n/workflow.json` y con `conteos-canonicos-tecnicos.md`
- **AND** la invocacion se sigue describiendo como sincronica y la cola de respaldo como trabajo futuro

#### Scenario: Bloque no aplicado conserva la limitacion

- **WHEN** un bloque del change c-140 no se aplico
- **THEN** el texto correspondiente conserva la declaracion de limitacion vigente y no afirma la capacidad

#### Scenario: Prueba de humo descrita con su alcance

- **WHEN** se lee `subsec:pruebas-automatizadas` con el bloque de prueba de humo aplicado
- **THEN** el texto declara la variante de costo cero, el canal o los canales recorridos, las propiedades verificadas y la exclusion de Gemini real y del canal telefonico

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
- **THEN** el mecanismo existe en `n8n/workflow.json` o en `App/Backend`, con los parametros que el documento cita
- **AND** si no existe, la afirmación se reformula como limitación conocida y trabajo futuro
- **AND** una espera fija entre intentos no se presenta como retroceso exponencial ni un reintento como cola de respaldo

#### Scenario: Perímetro de seguridad consistente

- **WHEN** el documento declara terminación TLS en el proxy inverso
- **THEN** la versión de protocolo declarada coincide con la configuración de `nginx/nginx.conf`
- **AND** la afirmacion distingue el despliegue de referencia, cuya terminacion TLS esta verificada por la prueba automatizada del borde, de los despliegues de la campana: la medicion telefonica sobre el perfil aislado `corpus` sin proxy y la ingesta del 2 de octubre sobre el stack base con Nginx, de modo que en ningun caso las mediciones dependen de TLS
- **AND** la afirmacion es coherente con el perfil Compose `corpus` (que excluye Nginx) y con el arnes de ingesta, que en el stack base lee por defecto a traves del proxy (`--insecure` sobre `https://localhost`)
- **AND** si no existe una verificacion automatizada vigente del borde, la afirmación se redacta de forma condicional

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
