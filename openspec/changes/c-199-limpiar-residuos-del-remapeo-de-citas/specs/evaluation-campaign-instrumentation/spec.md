## ADDED Requirements

### Requirement: ECM-015 — Verificación offline de las tablas SHA-256 del README de campaña

El proyecto SHALL proveer un test offline (sin red ni servicios externos, solo
biblioteca estándar) que recorra `evaluation/data/campana/README.md`, ubique cada tabla
Markdown cuyo encabezado sea `| Archivo | SHA-256 |` y, por cada fila con un valor de
hash en minúsculas de 64 hex, calcule el SHA-256 real del archivo nombrado (resuelto
relativo al directorio del README) y lo compare con el declarado. El test MUST cubrir
las tres tablas con ese encabezado: la de "SHA-256 por archivo" (c-166), la de
`intervenciones.csv` (c-165) y la de `brazo_manual.csv` (c-165). Las filas con valor
`pendiente` y las filas cuyo archivo no exista en el checkout MUST omitirse sin fallar.
Cuando un hash declarado difiera del real, el test MUST fallar nombrando el archivo y
ambos valores (declarado y real). El test MUST ser determinista y no escribir ningún
archivo.

#### Scenario: Hash declarado coincide con el real

- **WHEN** una fila de una tabla `| Archivo | SHA-256 |` declara el SHA-256 real de un archivo existente
- **THEN** el test pasa sin ofensas

#### Scenario: Hash declarado desactualizado

- **WHEN** una fila declara para un archivo existente un SHA-256 distinto del real (por ejemplo, `registro_sujetos.csv` con el hash previo a `ed4b386`)
- **THEN** el test falla nombrando el archivo, el hash declarado y el hash real

#### Scenario: Fila pendiente omitida

- **WHEN** una fila de la tabla declara el valor literal `pendiente`
- **THEN** el test omite esa fila sin fallar

#### Scenario: Fila de archivo ausente omitida

- **WHEN** una fila nombra un archivo que no existe en el checkout (por ejemplo, un artefacto aún no versionado)
- **THEN** el test omite esa fila sin fallar
