## ADDED Requirements

### Requirement: DIR-010 — Justificacion documental de la minimizacion del contacto en texto plano

El directorio SHALL mantener el email y el telefono del empleado en TEXTO PLANO conforme a DIR-005; este change NO agrega cifrado de aplicacion ni indice ciego. El proyecto SHALL documentar, bajo `docs/seguridad/`, la justificacion por **minimizacion** del almacenamiento en texto plano, alineada con la tesis: el contacto se almacena en claro a fin de preservar la auditabilidad directa y las consultas operativas, y su proteccion se sustenta en el control de acceso por rol (DIR-006), el aislamiento de la red interna y la minimizacion de campos (DIR-002). La documentacion MUST registrar que el cifrado de aplicacion fue evaluado y descartado como alternativa, indicando el motivo (costo de custodia de claves frente a un beneficio marginal para un dato personal no sensible bajo el art. 2 de la Ley 25.326), y MUST vincular la decision con el hallazgo del gap assessment (ISO/IEC 27002 5.34 y 8.12; `models/empleado.py:16-18`). El esquema y la configuracion del directorio MUST NOT incorporar una clave de cifrado ni una columna de hash ciega a raiz de este requisito.

#### Scenario: La justificacion por minimizacion queda documentada

- **WHEN** se inspecciona `docs/seguridad/` en busca de la justificacion del contacto en texto plano
- **THEN** existe un documento que justifica por minimizacion el almacenamiento en claro del email y el telefono del directorio y lo alinea con la tesis

#### Scenario: El cifrado se registra como alternativa descartada

- **WHEN** se lee la justificacion
- **THEN** registra que el cifrado de aplicacion fue evaluado y descartado, con el motivo, y vincula la decision con el hallazgo 5.34/8.12 sobre `models/empleado.py`

#### Scenario: El directorio sigue en texto plano sin cifrado ni indice ciego

- **WHEN** se revisa el esquema de `directorio_empleado` y la configuracion del backend
- **THEN** el email y el telefono permanecen en columnas varchar en claro, sin `EncryptedText` ni columna de hash ciego ni clave de cifrado del directorio (sin regresion de DIR-005)
