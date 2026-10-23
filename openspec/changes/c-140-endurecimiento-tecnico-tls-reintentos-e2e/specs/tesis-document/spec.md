## MODIFIED Requirements

### Requirement: Verificabilidad de las afirmaciones de pruebas del Capitulo 6

La tesis SHALL afirmar unicamente lo que el repositorio permite verificar. El §6.7 SHALL declarar pruebas de extremo a extremo que instancien N8N solo si el repositorio contiene una prueba ejecutable de ese tipo (el arnes de `scripts/dry_run/` con sus checks de recorrido y el workflow de humo que lo ejecuta), y en ese caso SHALL describir su alcance exacto: que corre una variante de costo cero del workflow versionado (sin los nodos con credenciales de terceros), que canales recorre, que propiedades verifica y que deja fuera (la etapa Gemini real y el canal telefonico). Si esa prueba no existe, el §6.7 SHALL NOT declarar pruebas de extremo a extremo y SHALL describir lo que existe (pruebas estructurales del `n8n/workflow.json`, pruebas de API y pruebas de integracion contra PostgreSQL). La descripcion de las pruebas de integracion contra PostgreSQL SHALL coincidir con el comportamiento vigente de la suite (falla de forma ruidosa si PostgreSQL no esta disponible; no se omite) y el recuento citado SHALL ser reproducible o retirarse. El recuento y la cobertura de la suite de frontend declarados en §6.7 SHALL ser reproducibles contra el estado del repositorio en el momento de la correccion, o SHALL acompanarse de un informe de cobertura versionado como evidencia; la tesis SHALL NOT publicar cifras de pruebas o de cobertura que el repositorio no reproduzca.

#### Scenario: Afirmacion de pruebas e2e respaldada por el repositorio

- **WHEN** el §6.7 declara una prueba de extremo a extremo con N8N activo
- **THEN** el repositorio contiene el arnes con los checks de recorrido declarados y el workflow que lo ejecuta
- **AND** el alcance declarado (variante de costo cero, canales, propiedades verificadas y exclusiones) coincide con los checks implementados

#### Scenario: Sin afirmacion de pruebas e2e de N8N no verificable

- **WHEN** se busca en el repositorio una prueba ejecutable que instancie N8N y recorra el flujo hasta la persistencia y no existe
- **THEN** el §6.7 no afirma que tales pruebas existan o se hayan ejecutado

#### Scenario: Pruebas de integracion PostgreSQL descritas con exactitud

- **WHEN** se compara la descripcion del subconjunto PostgreSQL en §6.7 con `App/Backend/tests/conftest.py` y la suite marcada `integration`
- **THEN** el texto no afirma una omision automatica (`pytest.skip`) que la suite ya no aplica, y el recuento citado coincide con la suite o se retira

#### Scenario: Recuento y cobertura de frontend reproducibles

- **WHEN** se cuenta la suite de pruebas de frontend en HEAD y se genera el informe de cobertura con el comando documentado
- **THEN** las cifras declaradas en §6.7 coinciden con el resultado reproducible, o existe un informe de cobertura versionado que las respalda
- **AND** no queda publicada la cifra 89/98,6 % sin evidencia que la respalde

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
- **AND** la afirmacion distingue el despliegue de referencia, cuya terminacion TLS esta verificada por la prueba automatizada del borde, del despliegue usado en la campana experimental, que no incluyo el proxy
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

## ADDED Requirements

### Requirement: Declaracion acotada del endurecimiento tecnico

La tesis SHALL declarar cada capacidad de endurecimiento tecnico (TLS verificado en el borde, reintentos idempotentes del alta, prueba de humo de extremo a extremo) solo si el bloque correspondiente del change c-140 esta aplicado y verificado en el repositorio, y SHALL conservar la redaccion de limitacion vigente para todo bloque no aplicado. En particular: (a) TLS se declara verificado en el despliegue de referencia de la release, nunca en la campana experimental, en `05-arquitectura.tex` (`subsec:vision-general`), `11-aspectos-legales.tex` (`subsec:seguridad-tecnica`) y el Anexo A, aclarando que el certificado de referencia es autofirmado; (b) el primer y el tercer desafio de `06-implementacion.tex` (`subsec:desafios-integracion`) describen la invocacion de alta como sincronica con reintento acotado e idempotente, con los valores de `n8n/workflow.json`, el desvio a la rama de error tras agotar los intentos y la semantica de `clasificacion_log` (un registro por clasificacion ejecutada; los replays no agregan registros), y `10-recomendaciones.tex` conserva la cola de respaldo y el alta asincronica como trabajo futuro; (c) el §6.7 (`subsec:pruebas-automatizadas`) describe la prueba de humo con su alcance exacto. Toda cifra nueva citada (intentos, esperas, tiempos maximos) SHALL registrarse en `docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md` con su fuente. Los resultados del capitulo 7 MUST NOT modificarse por este motivo.

#### Scenario: TLS declarado sin sobreafirmar

- **WHEN** se leen `subsec:vision-general`, `subsec:seguridad-tecnica` y el Anexo A con el bloque TLS aplicado
- **THEN** declaran TLS 1.2/1.3 en Nginx como verificado en el despliegue de referencia mediante la prueba automatizada del borde
- **AND** declaran que el despliegue de la campana experimental no incluyo el proxy y que el certificado de referencia es autofirmado

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

### Requirement: Interfaz del objetivo especifico 1 con el endurecimiento tecnico

La fila del objetivo especifico 1 en la tabla de cumplimiento de objetivos (`tab:cumplimiento-objetivos`) SHALL reflejar por componente la evidencia disponible: HTTP cifrado (verificado en el despliegue de referencia solo si el bloque TLS esta aplicado) y comunicacion asincronica (el alta sigue siendo sincronica; los reintentos idempotentes no la vuelven asincronica). El rotulo MUST NOT pasar a "Alcanzado" con la sola evidencia de los reintentos mientras el enunciado del objetivo exija comunicacion asincronica; el rotulo "Alcanzado" SHALL requerir que el enunciado del objetivo se reformule con justificacion explicita en el change que posee la tabla. El calificativo de la fila SHALL nombrar los componentes no cumplidos.

#### Scenario: Calificativo coherente con los bloques aplicados

- **WHEN** se lee la fila del objetivo especifico 1 con uno o mas bloques de c-140 aplicados
- **THEN** el calificativo menciona el alta sincronica con reintentos idempotentes (si aplica) y el estado de TLS en el despliegue de referencia (si aplica)

#### Scenario: Sin rotulo de cumplimiento pleno por reintentos

- **WHEN** el enunciado del objetivo especifico 1 sigue exigiendo comunicacion asincronica
- **THEN** la fila no se rotula "Alcanzado" con base en los reintentos del alta

### Requirement: Evidencia de la prueba de humo asociada a la release

Cuando la tesis cite la verificacion automatizada del borde TLS o la prueba de humo de extremo a extremo, el repositorio SHALL conservar un resumen de su ultima corrida sobre el commit de la release (commit, fecha, resultado por grupo de checks y enlace a la corrida del workflow de humo) en `docs/Tesis/Correcciones/dictamen-correcciones.md`. La tesis SHALL citar el mecanismo (arnes y workflow) y ese resumen, y MUST NOT citar un identificador de corrida que no figure en el repositorio.

#### Scenario: Resumen de corrida versionado

- **WHEN** la tesis declara TLS verificado o la prueba de humo
- **THEN** `dictamen-correcciones.md` contiene el resumen de la corrida sobre el commit de la release con todos los grupos citados en verde

#### Scenario: Sin referencias a corridas no versionadas

- **WHEN** se buscan en la tesis referencias a corridas del workflow de humo
- **THEN** solo remiten al mecanismo y al resumen versionado
