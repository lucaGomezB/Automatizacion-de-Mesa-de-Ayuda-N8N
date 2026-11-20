## ADDED Requirements

### Requirement: Instruccion de release ante el PDF del tag con hash ajeno (OQ-04)

El proyecto SHALL registrar en `docs/Tesis/Correcciones/dictamen-correcciones.md` (seccion
c-247) la decision de autores y director sobre el desfasaje del tag `v1.6.2`, cuyo arbol
contiene un `main.pdf` que imprime en el Anexo B el hash `17aa6d21` del candidato previo en
lugar de `e7013127`. La decision SHALL elegir entre: (A) dejar `v1.6.2` inmutable con nota de
erratum y compilar en el commit del proximo tag un PDF cuyo Anexo B no imprima ningun hash;
(B) no versionar PDF en el commit del tag; (C) mover el tag una sola vez, opcion que exige
modificar expresamente el requisito "Publicacion de una release de correccion sin mover tags
publicados". El change de release siguiente SHALL aplicar la opcion elegida y
`docs/Tesis/v10 (IA)/paper/compilacion.md` SHALL nombrar el commit compilado. Este change MUST
NOT mover, borrar ni recrear ningun tag ni recompilar el PDF.

#### Scenario: Decision registrada

- **WHEN** se lee la seccion c-247 de `dictamen-correcciones.md`
- **THEN** figura la opcion elegida (A, B o C), con fecha y responsables (autores y director)
- **AND** figura la instruccion para el change de release

#### Scenario: Tag intacto en este change

- **WHEN** se compara `git rev-parse v1.6.2^{commit}` antes y despues del apply de c-247
- **THEN** el valor no cambia

#### Scenario: Commit compilado nombrado

- **WHEN** el change de release recompila y se lee `compilacion.md`
- **THEN** la fila "Fuente compilada" nombra un commit y no "arbol de trabajo"
