<!--
  Delta de c-242 sobre `security-governance-docs`.

  MODIFIED: el requisito SGD-012 se reproduce completo, con TODOS sus escenarios
  vigentes (headers identicos; la fusion busca por texto). Reconciliacion con
  `docs/seguridad/registro-actividades-tratamiento.md` (ROPA),
  `docs/seguridad/registro-requisitos-legales.md`, `docs/seguridad/acta-consentimiento-t1.md`
  y `docs/seguridad/clasificacion-etiquetado-informacion.md`: la base de licitud del
  corpus se declara por regimen (consentimiento del grupo para el regimen (a); sin
  datos personales para el (b)).
-->

## MODIFIED Requirements

### Requirement: SGD-012 — Responsable del tratamiento y los tres tratamientos

El proyecto SHALL documentar, en `docs/seguridad/registro-actividades-tratamiento.md` (ROPA)
y/o `docs/seguridad/registro-requisitos-legales.md`, el **responsable del tratamiento** y los
**tres tratamientos** del sistema. Durante la tesis el responsable del tratamiento MUST ser el
propio grupo de desarrollo del proyecto, como responsable directo (NO la UTN-FRM), y el
**consentimiento informado del propio grupo** MUST quedar documentado como base de licitud del
tratamiento T1. Los tres tratamientos MUST describirse por separado: **T1** piloto/desarrollo
con datos REALES del grupo (cuentas del grupo y usuarios de prueba cuyos correos/celulares
apuntan a contactos del grupo), base de licitud consentimiento informado; **T2** corpus de
investigacion con incidentes reales pseudonimizados, responsable el grupo, salvaguarda
pseudonimizacion, aclarando que pseudonimizacion no equivale a disociacion (art. 2) porque el
original existe y es reidentificable; **T3** datos de produccion de una empresa que despliegue
el sistema, responsable la organizacion adoptante como rol funcional generico. El documento
SHALL declarar que el corpus de investigacion (T2) es una mezcla de dos regimenes y SHALL
declarar la base de licitud de cada uno: el **regimen (a)** (incidentes reales del entorno
operativo del propio equipo, pseudonimizados) se funda en el **consentimiento informado del
grupo** (articulo 5, inciso 1 de la Ley 25.326) y en la pseudonimizacion; el **regimen (b)**
(reconstrucciones de tipos de incidente reales construidas desde la practica, sin datos de
terceros) no contiene datos personales y por lo tanto no requiere base de licitud. El
documento MUST NOT presentar el articulo 5, inciso 2, apartado d) (base de empleador) como la
base de licitud del T2, por no existir una relacion de empleo. El documento MUST presentar la
organizacion adoptante como un **rol funcional generico futuro** y MUST NOT afirmar que una
organizacion real haya adoptado el sistema durante la tesis. El documento MUST dejar explicito
que el sistema no usa datos ficticios para ocultar su condicion: es un piloto con datos reales
del equipo en el regimen (a), y el regimen (b) son reconstrucciones de tipos de incidente
reales, no datos de terceros. La inscripcion de bases de datos (arts. 21/24) MUST quedar como
responsabilidad de la organizacion adoptante, con un template/checklist documental, y MUST NOT
afirmar que la tesis inscribe bases. La misma reconciliacion de la base de licitud por regimen
SHALL aplicarse a `docs/seguridad/acta-consentimiento-t1.md` y a
`docs/seguridad/clasificacion-etiquetado-informacion.md`.

#### Scenario: El responsable del tratamiento queda documentado

- **WHEN** se lee el ROPA o el registro de requisitos legales
- **THEN** identifica al grupo de desarrollo como responsable del tratamiento durante la tesis (responsable directo, no la UTN-FRM) y a la organizacion adoptante como responsable funcional de T3

#### Scenario: Los tres tratamientos se describen por separado

- **WHEN** se lee la seccion de tratamientos
- **THEN** T1 (piloto/desarrollo), T2 (corpus de investigacion) y T3 (adoptante futuro) aparecen descritos por separado con su finalidad, datos, responsable y base de licitud/salvaguarda

#### Scenario: El consentimiento del grupo respalda T1

- **WHEN** se revisa la base de licitud de T1
- **THEN** figura el consentimiento informado del propio grupo, documentado como acta breve

#### Scenario: Se distingue pseudonimizacion de disociacion en T2

- **WHEN** se lee la descripcion de T2
- **THEN** declara que los incidentes son reales y pseudonimizados y aclara que la pseudonimizacion no es disociacion (art. 2) porque el original existe y es reidentificable

#### Scenario: No se usan datos ficticios

- **WHEN** se lee la descripcion del piloto
- **THEN** declara que el sistema no usa datos ficticios para ocultar su condicion y que es un piloto con datos reales del equipo en el regimen (a), y que el regimen (b) son reconstrucciones de tipos de incidente reales

#### Scenario: La inscripcion de bases es responsabilidad del adoptante

- **WHEN** se lee la seccion de inscripcion de bases (arts. 21/24)
- **THEN** la asigna a la organizacion adoptante, entrega un template/checklist y no afirma que la tesis inscribe bases

#### Scenario: Base de licitud por regimen declarada

- **WHEN** se lee la descripcion del corpus de investigacion (T2) en el ROPA y en el registro de requisitos legales
- **THEN** declara la base de licitud del regimen (a) como consentimiento informado del grupo (articulo 5, inciso 1) y la pseudonimizacion
- **AND** declara que el regimen (b) no contiene datos personales y no requiere base de licitud
- **AND** no presenta la base de empleador (articulo 5, inciso 2, apartado d) como base del corpus

#### Scenario: El adoptante no se presenta como organizacion real

- **WHEN** se leen el ROPA, el registro de requisitos legales, el acta T1 y la clasificacion
- **THEN** la organizacion adoptante aparece como un rol funcional generico futuro
- **AND** ningun documento afirma que una organizacion real haya adoptado el sistema durante la tesis
