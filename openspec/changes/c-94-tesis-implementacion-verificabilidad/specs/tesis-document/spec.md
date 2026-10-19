# Delta for tesis-document

## ADDED Requirements

### Requirement: Verificabilidad de las afirmaciones de pruebas del Capitulo 6

La tesis SHALL afirmar unicamente lo que el repositorio permite verificar. El §6.7
SHALL NOT declarar pruebas de extremo a extremo que instancien N8N y ejecuten el flujo
completo desde el envio de un correo simulado hasta la persistencia del ticket, porque
ninguna prueba del repositorio instancia N8N. El §6.7 SHALL describir lo que existe
(pruebas estructurales del `n8n/workflow.json`, pruebas de API y pruebas de integracion
contra PostgreSQL) o retraer la afirmacion. El recuento y la cobertura de la suite de
frontend declarados en §6.7 SHALL ser reproducibles contra el estado del repositorio en
el momento de la correccion, o SHALL acompanarse de un informe de cobertura versionado
como evidencia; la tesis SHALL NOT publicar cifras de pruebas o de cobertura que el
repositorio no reproduzca.

#### Scenario: Sin afirmacion de pruebas e2e de N8N no verificable

- **WHEN** se busca en el repositorio una prueba que instancie N8N y ejecute el flujo completo hasta la persistencia
- **THEN** no existe ninguna prueba de ese tipo
- **AND** el §6.7 no afirma que tales pruebas existan o se hayan ejecutado

#### Scenario: Recuento y cobertura de frontend reproducibles

- **WHEN** se cuenta la suite de pruebas de frontend en HEAD y se genera el informe de cobertura con el comando documentado
- **THEN** las cifras declaradas en §6.7 coinciden con el resultado reproducible, o existe un informe de cobertura versionado que las respalda
- **AND** no queda publicada la cifra 89/98,6 % sin evidencia que la respalde

### Requirement: Atribuibilidad de la latencia telefonica del §6.4

El §6.4 SHALL NOT informar una latencia telefonica de extremo a extremo como observacion
operativa atribuible al flujo publicado sin declarar el tamano de muestra, la dispersion
y el procedimiento de medicion. Dado que C-17 establece que el agente telefonico no puede
ejecutarse como esta publicado, las observaciones de latencia del §6.4 SHALL retraerse o
reformularse con evidencia real y atribuible. La reformulacion SHALL ser coherente con la
medicion de tiempo telefonico definida en c-77 (Grupo E), sin duplicar su alcance.

#### Scenario: Latencia sin atribucion no se publica

- **WHEN** se lee el §6.4 del PDF compilado
- **THEN** no se declara una latencia de 12 a 15 s como observacion operativa del flujo publicado sin `n`, sin dispersion y sin procedimiento
- **AND** la afirmacion se retrae o se reformula con evidencia real y atribuible

#### Scenario: Coherencia con la medicion de tiempo de c-77

- **WHEN** se compara la formulacion de latencia telefonica del §6.4 con la metrica de tiempo telefonico de c-77
- **THEN** ambas son consistentes y no se contradicen
- **AND** c-94 no redefine la metrica que c-77 posee

### Requirement: Hipoteticidad declarada del ejemplo del dashboard

El §6.8 SHALL presentar el ejemplo de los veinte usuarios que reportan la rotura de
auriculares como un escenario hipotetico, y SHALL NOT presentarlo como «caso concreto» ni
como una observacion realizada. La captura del dashboard SHALL provenir de c-80 (tarea
6.6); c-94 no agrega capturas ni duplica esa evidencia.

#### Scenario: Ejemplo marcado como hipotetico

- **WHEN** se lee el cierre del §6.8
- **THEN** el ejemplo del dashboard se presenta como hipotetico
- **AND** no se afirma que sea un «caso concreto» ni un hecho observado

### Requirement: Alcance declarado de la preparacion para Kubernetes

El §6.1 SHALL NOT declarar que el despliegue esta «preparado para migracion a un cluster
Kubernetes 1.30» sin un manifiesto que lo respalde en el repositorio. La afirmacion SHALL
retraerse o acotarse explicitamente como trabajo futuro o como intencion de diseno, sin
presentarla como una capacidad implementada.

#### Scenario: Sin manifiesto no se declara preparacion implementada

- **WHEN** se busca en el repositorio un manifiesto de Kubernetes para el despliegue
- **THEN** no existe ningun manifiesto de ese tipo
- **AND** el §6.1 no declara la preparacion para Kubernetes como capacidad implementada

### Requirement: Parametros de inferencia sin calificativo no respaldado

El §5.4 SHALL NOT calificar los parametros de inferencia (temperatura, top-p, max tokens,
timeout) como «optimizados para exactitud y latencia» sin describir el procedimiento de
optimizacion ni los valores alternativos evaluados. El calificativo SHALL retirarse o el
procedimiento SHALL documentarse.

#### Scenario: Sin procedimiento no se afirma optimizacion

- **WHEN** se lee el §5.4 del PDF compilado
- **THEN** no se afirma que los parametros de inferencia esten «optimizados» sin un procedimiento de optimizacion descrito
- **AND** el calificativo se retira o el procedimiento se documenta con los valores alternativos evaluados

### Requirement: Completitud y no exhaustividad de la Tabla 5 de puntos de entrada REST

La Tabla 5 (`tab:api`, §5.7) SHALL reflejar los grupos de puntos de entrada reales de la
API —al menos autenticacion, incidentes (con su PATCH), clasificaciones (GET y PATCH),
estadisticas y salud— y SHALL declarar de forma explicita que no es exhaustiva, con
remision al contrato completo en el Anexo D/OpenAPI. La tabla SHALL NOT presentarse como
el listado completo de la API.

#### Scenario: Grupos de entrada presentes

- **WHEN** se compara la Tabla 5 con las rutas de `docs/openapi.json`
- **THEN** la tabla incluye los grupos de autenticacion, incidentes, clasificaciones, estadisticas y salud
- **AND** incluye el PATCH sobre incidentes y las operaciones GET y PATCH de clasificaciones

#### Scenario: No exhaustividad declarada

- **WHEN** se lee la Tabla 5 y su texto circundante
- **THEN** se declara que la tabla no es exhaustiva
- **AND** se remite al contrato completo en el Anexo D/OpenAPI

### Requirement: Coherencia del nombre del modelo en el cuerpo de la tesis

El cuerpo de la tesis SHALL nombrar el modelo de inferencia con el identificador real
configurado y desplegado, `gemini-3.6-flash`, en todas sus menciones. El texto SHALL NOT
usar «Gemini 2.5 Flash», «Gemini~2.5» ni cualquier otra variante del identificador
obsoleto en los archivos de seccion del cuerpo. La alineacion SHALL comprender, como
minimo, `00-resumen.tex`, `05-arquitectura.tex`, `06-implementacion.tex`,
`08-discusion.tex`, `09-conclusiones.tex`, `10-recomendaciones.tex`,
`11-aspectos-legales.tex` y `12-anexos.tex`. El §1.6 de `01-introduccion.tex` y
`docs/anexo_h_prompt_gemini.md` ya fueron alineados por c-76 y SHALL permanecer bajo su
titularidad; c-94 SHALL NOT reescribirlos ni duplicar esa correccion. La fuente de verdad
del identificador es `App/Backend/app/config/settings.py` (`gemini_model =
"gemini-3.6-flash"`), consistente con `App/Backend/.env.example`, `README.md` y el propio
Anexo H.

#### Scenario: Cuerpo alineado al identificador real

- **WHEN** se ejecuta `rg -n "Gemini[ ~]*2\.5"` sobre los ocho archivos de seccion del cuerpo
- **THEN** no hay coincidencias
- **AND** todas las menciones del modelo usan `gemini-3.6-flash`

#### Scenario: Coherencia con la configuracion desplegada

- **WHEN** se compara el nombre del modelo citado en el cuerpo con `App/Backend/app/config/settings.py`, `App/Backend/.env.example`, `README.md` y `docs/anexo_h_prompt_gemini.md`
- **THEN** todos coinciden en `gemini-3.6-flash`
- **AND** no queda ninguna mencion de «Gemini 2.5 Flash» en el cuerpo

#### Scenario: Alcance de c-76 sin duplicacion

- **WHEN** se revisa la titularidad de §1.6 de `01-introduccion.tex` y `docs/anexo_h_prompt_gemini.md`
- **THEN** ambos quedan como los dejo c-76 y c-94 no los re-edita
- **AND** c-94 solo cubre las menciones del modelo fuera de ese alcance

### Requirement: Alineacion textual del residuo de C-18 sin duplicacion

La alineacion textual del residuo de C-18 —Tabla 4 con `canal_origen_id` en lugar de
`id_canal`, y §5.3 con un unico `POST /api/v1/incidentes` que clasifica y persiste en vez
de dos llamadas— SHALL permanecer bajo la titularidad de c-77 C3. c-94 SHALL referenciar y
verificar esa alineacion, y SHALL NOT reescribirla ni duplicar su alcance.

#### Scenario: Residuo de C-18 referenciado, no duplicado

- **WHEN** se revisa el alcance de c-94 frente a c-77 C3
- **THEN** c-94 referencia la alineacion de Tabla 4 y §5.3 sin reescribirla
- **AND** no existen dos tareas en changes distintos que editen las mismas lineas del mismo archivo con el mismo objetivo
