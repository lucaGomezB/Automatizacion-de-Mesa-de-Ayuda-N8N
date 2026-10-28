## ADDED Requirements

### Requirement: Coherencia del indice de changes con el archivo de changes

`CHANGES.md` SHALL reflejar el estado real de cada change respecto de `openspec/changes/archive/`. Un change archivado MUST NOT presentarse como aplicado-en-curso, "en aplicacion", activo ni "pendiente de archive". Cada change archivado dentro del alcance de la numeracion vigente SHALL tener una entrada en el indice, y las lineas de resumen (Total, Fases y numeracion) SHALL ser consistentes con el contenido real del directorio de archivo y con el conjunto de changes activos. La correccion de una afirmacion de estado obsoleta SHALL aplicar el estado vigente; las actualizaciones fechadas previas MUST conservarse sin reescribirse.

#### Scenario: Un change archivado deja de figurar como pendiente

- **WHEN** se leen las entradas de C-151 y C-153 en `CHANGES.md`
- **THEN** ambas declaran de forma explicita el estado ARCHIVADO con su fecha
- **AND** las frases "pendiente de archive" y "EN APLICACION" no aparecen asociadas a esos changes

#### Scenario: Las entradas faltantes del archivo se registran

- **WHEN** se recorre `openspec/changes/archive/2026-10-28-*` y se compara con las entradas de `CHANGES.md`
- **THEN** C-152 (`corregir-deriva-documental-knowledge-base-y-guia-n8n`) y C-154 (`corregir-el-harness-de-la-ablacion-paga`) tienen una entrada en el indice
- **AND** cada entrada declara el estado ARCHIVADO, su scope, su verificacion y su rollback

#### Scenario: Las lineas de resumen no se detienen en un change archivado anterior

- **WHEN** se leen las lineas Total, Fases y numeracion de `CHANGES.md`
- **THEN** la numeracion documentada alcanza al ultimo change archivado (C-154)
- **AND** las fases registradas incluyen las que agrupan C-150, C-151, C-152, C-153 y C-154
- **AND** ninguna linea de resumen detiene la numeracion en C-149

#### Scenario: La correccion de estado no reescribe la historia

- **WHEN** se corrigen los estados de C-151 y C-153 en el indice
- **THEN** las actualizaciones fechadas previas de `CHANGES.md` se conservan integras
- **AND** la afirmacion de estado obsoleta se corrige sin falsificar el hecho previo

### Requirement: Descripcion vigente del canal telefonico en la base de conocimiento

La descripcion del canal telefonico en `knowledge-base/07_flujos_principales.md` SHALL describir la arquitectura vigente: el backend resuelve la clasificacion telefonica con la cascada `HybridClassifier`. Los componentes retirados por C-72 —el `AI Agent` de LangChain, la memoria de sesion en Redis y el bucle de refinamiento del agente— MUST NOT describirse como un paso vigente. Si alguno de esos hechos se conserva, SHALL rotularse de forma explicita como historico o superado.

#### Scenario: El flujo telefonico no describe componentes retirados como vigentes

- **WHEN** se lee el Flujo 3 de `knowledge-base/07_flujos_principales.md`
- **THEN** no describe el agente LangChain, la sesion en Redis ni el bucle de refinamiento como pasos vigentes
- **AND** declara que el backend clasifica la telefonia con la cascada hibrida

#### Scenario: Un componente retirado conservado queda rotulado

- **WHEN** el Flujo 3 menciona el agente telefonico retirado como antecedente
- **THEN** la mencion aparece rotulada como historica o superada
- **AND** no se presenta como el mecanismo actual

### Requirement: Politica de visibilidad documentada coincide con el codigo

`knowledge-base/03_actores_y_roles.md` SHALL declarar los modos de visibilidad de incidentes que existen en el codigo (`ModoAlcance` de `App/Backend/app/services/role_policy.py`: PROPIO, GLOBAL, SECTOR y VACIO). El texto MUST NOT afirmar que el aislamiento por sector no existe. El modo SECTOR, asociado al rol `gestion_incidentes`, SHALL documentarse como vigente y consistente con la regla VIS-007.

#### Scenario: El modo SECTOR figura entre los modos de visibilidad

- **WHEN** se leen los modos de visibilidad declarados en `knowledge-base/03_actores_y_roles.md`
- **THEN** incluyen SECTOR ademas de PROPIO, GLOBAL y VACIO
- **AND** coinciden con los valores de `ModoAlcance` del codigo

#### Scenario: No se afirma la inexistencia del aislamiento por sector

- **WHEN** se busca en `knowledge-base/03_actores_y_roles.md` la afirmacion "el aislamiento por sector NO existe"
- **THEN** la afirmacion no aparece como vigente
- **AND** el documento describe el alcance SECTOR de `gestion_incidentes`

### Requirement: Umbrales y estado de la documentacion operativa sincronizados con el codigo

`docs/por_implementar.md` SHALL declarar umbrales reproducibles desde `App/Backend/app/config/settings.py` (`deterministic_score_threshold` = 0.5166 y `human_review_threshold` = 0.70). El documento MUST NOT citar un umbral retirado (por ejemplo `< 0.90`) como vigente. Su encabezado de estado SHALL reflejar el estado vigente o rotular de forma explicita como historicas las secciones desactualizadas.

#### Scenario: El umbral citado es el vigente

- **WHEN** se lee la nota de impacto de `GEMINI_API_KEY` en `docs/por_implementar.md`
- **THEN** el umbral de revision humana citado coincide con `Settings.human_review_threshold` (0.70)
- **AND** el umbral `< 0.90` no figura como valor vigente

#### Scenario: El encabezado de estado no presenta un estado retirado como actual

- **WHEN** se lee el encabezado de estado de `docs/por_implementar.md`
- **THEN** la fecha o el estado declarado refleja la revision actual
- **AND** las secciones que se conserven desactualizadas quedan rotuladas como historicas
