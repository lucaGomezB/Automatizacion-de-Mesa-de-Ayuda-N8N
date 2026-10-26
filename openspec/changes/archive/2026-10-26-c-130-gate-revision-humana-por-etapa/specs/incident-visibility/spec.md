## MODIFIED Requirements

### Requirement: VIS-005 — Derivacion a revision humana ante reportante no identificado

El sistema SHALL derivar el incidente a revision humana (`requiere_revision_humana = true`) cuando NO pueda identificar al reportante, es decir, cuando no haya contacto de canal (ni email de remitente ni telefono de llamante, segun el canal), cuando el contacto no resuelva a un empleado ACTIVO del directorio (NO ENCONTRADO o AMBIGUO), o cuando la cuenta web autenticada no tenga empleado vinculado. La derivacion SHALL persistir `reportante_empleado_id = NULL` y MUST NOT bloquear ni demorar el alta.

El sistema SHALL combinar esta derivacion por OR con el indicador de revision del clasificador: `requiere_revision_humana = (indicador del clasificador) OR (reportante no identificado)`, donde el indicador del clasificador es verdadero cuando la etapa Gemini devuelve una confianza inferior a 0.70 o interviene la etapa fallback, y falso cuando la etapa determinista cortocircuita, cualquiera sea su confianza; de modo que un incidente ya marcado por el clasificador NUNCA deje de requerir revision. La identificacion exitosa del reportante MUST NOT forzar revision humana por si misma. La trazabilidad SHALL registrar el canal y el resultado sin email ni telefono en claro.

#### Scenario: Sin contacto de canal deriva a revision

- **WHEN** el alta de correo o telefonia no transporta contacto del remitente o llamante
- **THEN** el incidente se persiste con `reportante_empleado_id` nulo y `requiere_revision_humana = true`, sin bloquear el alta

#### Scenario: Contacto no resoluble deriva a revision

- **WHEN** el contacto del remitente o llamante no corresponde a ningun empleado activo
- **THEN** el incidente se persiste con reportante nulo y `requiere_revision_humana = true`

#### Scenario: Cuenta web sin empleado deriva a revision

- **WHEN** la cuenta web autenticada que crea el incidente no tiene empleado vinculado
- **THEN** el incidente se persiste con reportante nulo y `requiere_revision_humana = true`

#### Scenario: La derivacion no quita una revision ya marcada

- **WHEN** el clasificador ya marco el incidente para revision (etapa Gemini con confianza inferior a 0.70, o etapa fallback) aunque el reportante se identifique
- **THEN** el incidente conserva `requiere_revision_humana = true`

#### Scenario: La derivacion por reportante alcanza al cortocircuito determinista

- **WHEN** la etapa determinista cortocircuita la clasificacion y el reportante no se identifica
- **THEN** el incidente se persiste con `requiere_revision_humana = true` aunque el indicador del clasificador sea falso

#### Scenario: Reportante identificado no fuerza revision

- **WHEN** el reportante se identifica y el clasificador no exige revision
- **THEN** el incidente queda con `requiere_revision_humana = false` y el reportante persistido

#### Scenario: La derivacion no bloquea el alta

- **WHEN** el reportante no se identifica y el incidente se deriva a revision humana
- **THEN** la respuesta de creacion del incidente se completa con normalidad (HTTP 201)
