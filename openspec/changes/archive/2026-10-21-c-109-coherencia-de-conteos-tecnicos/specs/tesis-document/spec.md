## ADDED Requirements

### Requirement: Conteo unico de entidades del modelo de datos

La tesis SHALL declarar un unico numero de entidades principales del modelo de
datos, igual a **siete**, en todos los pasajes que lo mencionan
(`05-arquitectura.tex`, `06-implementacion.tex`, `12-anexos.tex` y la Tabla
`tab:entidades`). El numero canonico SHALL derivarse de la Tabla `tab:entidades` y
del ORM versionado, que incluye `directorio_empleado`. El texto MUST NOT declarar
"seis entidades" en ningun pasaje.

#### Scenario: Conteo unico de entidades en el cuerpo

- **WHEN** se busca "seis entidades" o "siete entidades" en los `.tex` y en el PDF compilado
- **THEN** la unica declaracion vigente es "siete entidades principales"
- **AND** no queda ninguna ocurrencia de "seis entidades" como conteo del modelo final

#### Scenario: Coherencia con la tabla de entidades

- **WHEN** se compara el conteo declarado con las filas de la Tabla `tab:entidades`
- **THEN** el numero de filas de entidades principales es siete
- **AND** incluye `incidente`, `sector`, `estado`, `canal_origen`, `clasificacion_log`, `users` y `directorio_empleado`

### Requirement: Conteo unico de etapas y nodos del flujo N8N

La tesis SHALL declarar un unico numero de etapas funcionales del flujo N8N, igual
a **siete**, derivado de la agrupacion funcional de `n8n/workflow.json`, en
`06-implementacion.tex` y `12-anexos.tex`. Cuando el texto describa el patron de
procesamiento por canal, SHALL rotularlo explicitamente como tal y MUST NOT
presentarlo como el conteo total de etapas del flujo. La tesis SHALL declarar el
conteo de nodos como **29 operativos mas 3 notas adhesivas (32 nodos totales)**.
El texto MUST NOT declarar "26 operativos" ni presentar "29" como el total de
nodos.

#### Scenario: Conteo unico de etapas del flujo

- **WHEN** se leen el Capitulo 6 y el Anexo del flujo en el PDF compilado
- **THEN** ambos declaran siete etapas funcionales del flujo
- **AND** no se presenta "cinco etapas" como el conteo total de etapas del flujo

#### Scenario: Conteo de nodos operativos y totales

- **WHEN** se busca el conteo de nodos del flujo en los `.tex` y en el PDF compilado
- **THEN** el conteo declarado es 29 nodos operativos mas 3 notas adhesivas, es decir 32 nodos totales
- **AND** no aparece "26 operativos" ni "29 nodos" presentado como el total

#### Scenario: Conteo verificable contra el flujo exportado

- **WHEN** se cuentan los nodos de `n8n/workflow.json` por tipo
- **THEN** el total es 32, de los cuales 3 son `stickyNote` y 29 son operativos
- **AND** el conteo declarado en la tesis coincide con ese resultado

### Requirement: Nombre canonico del SDK de Google

La tesis SHALL nombrar el paquete del SDK de Google como **`google-genai`** (SDK
unificado) en todos sus pasajes, incluido el Anexo de parametros de inferencia. El
documento MUST NOT presentar `google-generativeai` como el paquete utilizado. La
fuente de verdad del nombre y del rango de version es
`App/Backend/requirements.txt` (`google-genai>=2.20.0,<3`).

#### Scenario: Nombre unico del SDK

- **WHEN** se busca `google-generativeai` o `google-genai` en los `.tex` y en el PDF compilado
- **THEN** la unica denominacion vigente del paquete usado es `google-genai`
- **AND** no queda `google-generativeai` presentado como el SDK invocado

#### Scenario: Coherencia con requirements.txt

- **WHEN** se compara el paquete declarado en la tesis con `App/Backend/requirements.txt`
- **THEN** ambos coinciden en `google-genai`
- **AND** el rango de version declarado es compatible con `>=2.20.0,<3`
