## MODIFIED Requirements

### Requirement: Presupuesto de páginas preservado

El total de paginas del PDF de la tesis SHALL cumplir el tope vigente de paginas, que SHALL declararse en un unico lugar: la seccion de presupuesto de paginas de `docs/Tesis/Correcciones/dictamen-correcciones.md`, con su regla de medicion, su valor, su fuente (exigencia de la catedra o decision del equipo) y su fecha. Para la release `v1.2.2`, la regla vigente SHALL ser: metrica = **total del PDF**; valor = **100 paginas**; fuente = **exigencia de la catedra**; y la medicion SHALL hacerse con `pdfinfo main.pdf | grep Pages` o un conteo equivalente de saltos de pagina del PDF. Cuando el total supere el valor del tope, el exceso SHALL estar declarado y honrado por decision registrada de los autores, con su magnitud y fecha, y SHALL defenderse ante la catedra; un exceso no declarado MUST NOT presentarse como cumplimiento. La portada SHALL seguir ocupando exactamente una pagina. Una reduccion para acercarse al tope MUST NOT eliminar contenido cientifico, numeros canonicos, figuras o tablas requeridas, referencias ni correcciones previas, y MUST NOT dejar referencias colgadas (`\ref` o `\autoref` sin destino) ni listados de codigo removidos con referencias en la prosa.

#### Scenario: Conteo de páginas sin cambios

- **WHEN** se compila `main.tex` en el entorno de registro y se ejecuta `pdfinfo main.pdf | grep Pages` (o el conteo equivalente de saltos de pagina del PDF) sobre el PDF de la release
- **THEN** el total de paginas se mide sobre el PDF completo y queda registrado en el libro mayor con su regla, su valor, su fuente y su fecha
- **AND** la portada sigue ocupando exactamente una pagina
- **AND** cuando el total supera las 100 paginas, la magnitud del exceso, su fecha y la decision de sostenerlo quedan registradas, y el requisito no se reescribe para dar el tope por cumplido

#### Scenario: Tope medido sobre el total

- **WHEN** se cuenta el total de paginas del PDF
- **THEN** el conteo incluye portada, indices, glosario, cuerpo, referencias y anexos
- **AND** no se computa un subconjunto (por ejemplo, solo el cuerpo o el cuerpo sin anexos) para dar por cumplido el tope

#### Scenario: Tope total declarado en un unico lugar

- **WHEN** se lee la seccion de presupuesto de paginas de `docs/Tesis/Correcciones/dictamen-correcciones.md`
- **THEN** figuran la metrica (total del PDF), el valor (100 paginas), la fuente (exigencia de la catedra) y la fecha
- **AND** ninguna otra regla de tope de paginas se presenta como vigente

#### Scenario: Exceso honrado y defendido

- **WHEN** el total del PDF de la release supera las 100 paginas
- **THEN** el registro declara la magnitud del exceso, su fecha y la decision de los autores de sostenerlo y defenderlo
- **AND** el PDF no se presenta como si cumpliera el tope sin exceso

#### Scenario: Reduccion sin perdida de contenido ni referencias colgadas

- **WHEN** se compacta el documento para acercarlo al tope
- **THEN** los numeros canonicos, las figuras y tablas requeridas, las referencias y las correcciones previas permanecen
- **AND** no queda ninguna referencia colgada ni un listado de codigo removido con una referencia en la prosa
- **AND** las palancas aplicadas son de forma (indices, listas, tamano de anexos, ancho de figuras, espaciado)

#### Scenario: Portada de una sola pagina

- **WHEN** se mide el PDF compilado
- **THEN** la portada ocupa exactamente una pagina

### Requirement: Coherencia de la version bibliografica con la release publicada

La entrada `Gomez2026_repositorio` de `docs/Tesis/v10 (IA)/Bibliography_base.bib` SHALL declarar en su titulo la misma version que el tag de release que identifica el Anexo B (`sec:anexo-repositorio`). Para la release `v1.2.2`, el titulo SHALL enunciar la version `1.2.2`, con la etiqueta "Version" o con su forma acentuada si la revision ortotipografica la acentuo por decision registrada, y SHALL NOT conservar numeros de version anteriores como `1.2.1`, `1.2.0`, `1.1.1` o `1.0.0`. El numero de version SHALL actualizarlo el change que publica la release, en el mismo commit que cambia el tag del Anexo B; ningun otro change MUST modificar ese numero. Los demas campos de la entrada (autoria, ano, `url` y `note`) SHALL conservarse y la referencia SHALL seguir imprimiendose en la seccion de Referencias.

#### Scenario: Version bibliografica alineada con la release

- **WHEN** se compara el titulo de `Gomez2026_repositorio` con el tag que consigna el Anexo B
- **THEN** el titulo enuncia la version `1.2.2` y el Anexo B enuncia `v1.2.2`
- **AND** el titulo de `Gomez2026_repositorio` no conserva los numeros de version `1.2.1`, `1.2.0`, `1.1.1` ni `1.0.0`

#### Scenario: Integridad de la entrada preservada

- **WHEN** se ejecuta la verificacion de citas contra `Bibliography_base.bib`
- **THEN** la entrada sigue existiendo y sigue siendo referenciada por las citas del anexo
- **AND** sus campos `author`, `year`, `url` y `note` se mantienen, sin introducir citas huerfanas ni entradas sin usar

## ADDED Requirements

### Requirement: Publicacion de la release de integracion v1.2.2

La version de trabajo de la tesis `docs/Tesis/v10 (IA)/` SHALL publicarse como release `v1.2.2` integrando los changes ya aplicados `c-146-completar-metricas-trabajos-previos` y `c-140-endurecimiento-tecnico-tls-reintentos-e2e`, mas la compactacion de forma aplicada en el commit `8c0cf6d`. La release SHALL usar el patron de dos commits: el commit C1 SHALL cambiar el tag del Anexo B a `v1.2.2`, retirar la linea del hash de la release anterior y actualizar la version de `Gomez2026_repositorio`, y el commit C2 SHALL consignar en el Anexo B el hash completo de 40 caracteres del commit etiquetado, coincidente con `git rev-parse v1.2.2^{commit}`, y registrar el mismo hash en `docs/Tesis/Correcciones/dictamen-correcciones.md`. El tag SHALL ser anotado y SHALL crearse sobre C1 solo despues de recompilar el PDF en el entorno de registro (`texlive-thesis`) y verificar cero errores fatales, cero referencias o citas indefinidas, cero etiquetas duplicadas y el conteo de paginas del tope vigente. El tag SHALL publicarse en `origin` y la integracion a `main` SHALL hacerse con merge commit (nunca squash ni rebase). Antes de etiquetar, las tareas pendientes de c-140 (3.8 de regresion de backend y 3.9 de documentacion de la guia del workflow) SHALL estar cerradas y la tarea 3.10 (reimportacion en la instancia operativa) SHALL figurar como ejecutada por el equipo, no por el agente. Los tags `v1.0.0`, `v1.0.1`, `v1.1.0`, `v1.1.1`, `v1.2.0` y `v1.2.1` MUST NOT moverse ni borrarse; `v1.2.1` queda registrada como superada.

#### Scenario: Tag anotado sobre C1

- **WHEN** se ejecutan `git cat-file -t v1.2.2` y `git rev-parse v1.2.2^{commit}`
- **THEN** el tag existe, es anotado (devuelve `tag`, no `commit`) y apunta a C1
- **AND** el tag esta publicado en `origin` (`git ls-remote --tags origin v1.2.2` lo devuelve)

#### Scenario: Commit etiquetado sin el hash de la release anterior

- **WHEN** se lee `sec:anexo-repositorio` en `git show v1.2.2:"docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex"`
- **THEN** figura el tag `v1.2.2`
- **AND** no figura el hash `509ffff105c21fed0c07cbf9a46245ba6c53e0e1` de `v1.2.1`

#### Scenario: Hash consignado y coherente con el tag

- **WHEN** se lee `sec:anexo-repositorio` en el commit C2 y se compara con `git rev-parse v1.2.2^{commit}`
- **THEN** figura el hash completo de 40 caracteres del commit etiquetado
- **AND** el hash coincide en los 40 caracteres y tambien figura en `docs/Tesis/Correcciones/dictamen-correcciones.md`

#### Scenario: Compilacion verificada antes del tag

- **WHEN** se compila la fuente que se va a etiquetar en el entorno `texlive-thesis`
- **THEN** el log no contiene errores fatales, referencias ni citas indefinidas, ni etiquetas `multiply defined`
- **AND** el conteo de paginas totales cumple la regla registrada (100, con el exceso honrado y defendido)

#### Scenario: Tareas pendientes de c-140 cerradas antes del tag

- **WHEN** se revisa el `tasks.md` de `c-140-endurecimiento-tecnico-tls-reintentos-e2e` antes de crear el tag
- **THEN** las tareas 3.8 (regresion completa de backend) y 3.9 (seccion de la guia del workflow) estan cerradas con su evidencia
- **AND** la tarea 3.10 (reimportacion en la instancia operativa) figura como ejecutada por el equipo

#### Scenario: Tags previos inmutables

- **WHEN** se comparan `git rev-parse v1.0.0^{commit}`, `v1.0.1^{commit}`, `v1.1.0^{commit}`, `v1.1.1^{commit}`, `v1.2.0^{commit}` y `v1.2.1^{commit}` con sus valores previos
- **THEN** `v1.0.0` sigue en `61a6b117dd1321fbee25f9792d9f29b884e5ac8d`, `v1.0.1` en `bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0`, `v1.1.0` en `7103b649d8c4f51737ad6ad4095dad22c9406400`, `v1.1.1` en `4160d84286623b073d2904353e6f9163ae211de7`, `v1.2.0` en `a49d035c67b32ae17e633ec04b09ecdd2781aac6` y `v1.2.1` en `509ffff105c21fed0c07cbf9a46245ba6c53e0e1`
- **AND** ningun tag existente fue reescrito, recreado ni borrado

#### Scenario: Tag alcanzable desde la rama principal

- **WHEN** el PR de la rama de release a `main` se integro con merge commit y se ejecuta `git fetch origin`
- **THEN** `git merge-base --is-ancestor v1.2.2 origin/main` es verdadero

#### Scenario: Changes integrados archivados

- **WHEN** se ejecuta `openspec list --json` despues de la release
- **THEN** `c-146-completar-metricas-trabajos-previos` y `c-140-endurecimiento-tecnico-tls-reintentos-e2e` no figuran como activos
- **AND** sus delta specs quedaron sincronizados en `openspec/specs/`
