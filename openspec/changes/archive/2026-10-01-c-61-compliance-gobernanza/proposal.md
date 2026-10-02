## Why

El gap assessment (`docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`) identifico brechas documentales de gobernanza de seguridad sin evidencia en el repositorio: politica de seguridad (5.1), clasificacion y etiquetado (5.12, 5.13), roles y responsabilidades (5.2), gestion de incidentes (5.24-5.27), inventario de activos y requisitos legales (5.9, 5.31) y seguridad en el ciclo de desarrollo (8.26). C-61 es el primer change del workstream de cumplimiento aprobado (`docs/cumplimiento/plan-cambios-cumplimiento.md`, §2 fila C-61) y establece la espina dorsal documental que los demas changes referencian. Es alcance (D) documental: NO cambia comportamiento de runtime.

## What Changes

- Crear `docs/seguridad/` con el cuerpo documental de gobernanza (11 documentos, ver Impact).
- Cada documento queda **alineado con** y mapea controles de ISO/IEC 27002:2022 y NIST CSF 2.0 (Govern/Identify), y con la Ley 25.326 cuando aplica.
- Documentar el **esquema de clasificacion y etiquetado** (incluye PII y datos del directorio) y los **roles de seguridad** (incl. responsable de proteccion de datos / DPO) como **FUNCIONES** de la organizacion adoptante, sin nombrar personas concretas.
- Documentar el **plan de respuesta a incidentes de seguridad** y el **procedimiento de reporte de eventos**, adoptando el estandar de notificacion de 72 h por prudencia (la Ley 25.326 vigente NO impone obligacion general).
- Documentar el **inventario de activos de informacion**, el **registro de requisitos legales** y el **registro de actividades de tratamiento (ROPA)** segun Ley 25.326.
- Documentar el **responsable del tratamiento** (durante la tesis, el propio grupo de desarrollo como responsable directo, NO la UTN-FRM) y los **tres tratamientos** por separado: **T1** piloto/desarrollo con datos REALES del grupo y consentimiento informado documentado; **T2** corpus de investigacion con incidentes reales pseudonimizados (pseudonimizacion != disociacion, art. 2); **T3** adoptante futuro (organizacion adoptante, rol funcional). El sistema **no usa datos ficticios**.
- Documentar el **modelado de amenazas y los requisitos de seguridad en el SDLC** y la **politica de privacidad en runtime** de cara al usuario (describe el objetivo/norma; el estado actual vive en el gap assessment).
- Dejar la **verificacion como MANUAL** (checklist + `openspec validate --strict`); el doc-lint automatizado queda registrado como **change futuro**, no se implementa en C-61.
- Fijar la regla de lenguaje transversal: "alineado con" / "controles mapeados a"; NUNCA "certificado" ni "compliant".

### Out of scope

- Implementacion de controles tecnicos: C-62 (infra/red), C-63 (identidad/accesos/claves), C-64 (vulnerabilidades/supply chain), C-65 (backup/continuidad), C-66 (privacidad/transferencias), C-67 (SMS al llamante).
- Controles organizacionales (O) fuera del repositorio (personas 6.x, fisicos 7.x): se documentan como responsabilidad de la organizacion adoptante, no se implementan.
- Prosa de tesis (`docs/Tesis/v9 (IA)`), `CHANGES.md`, backend, frontend y otros changes.
- El doc-lint automatizado de la documentacion de seguridad: se registra como change futuro, no se implementa en C-61.
- Toda modificacion de codigo, configuracion o infraestructura.

## Capabilities

### New Capabilities

- `security-governance-docs`: conjunto de documentos de gobernanza de seguridad y privacidad del proyecto (`docs/seguridad/`): indice, politica de seguridad, clasificacion/etiquetado, roles y responsabilidades, gestion de incidentes, inventario de activos, requisitos legales, SDLC seguro, privacidad en runtime y ROPA; con reglas de lenguaje, trazabilidad a controles y encuadre de stack de desarrollo local.

### Modified Capabilities

- None — no cambia comportamiento de runtime; la capacidad documental es nueva.

## Impact

| Area | Impacto | Descripcion |
|------|---------|-------------|
| `docs/seguridad/README.md` | New | Indice y mapa de trazabilidad control -> documento |
| `docs/seguridad/politica-seguridad-informacion.md` | New | 5.1; alcance, principios, aprobacion, comunicacion, revision |
| `docs/seguridad/clasificacion-etiquetado-informacion.md` | New | 5.12, 5.13; niveles, criterios, PII y datos del directorio |
| `docs/seguridad/roles-responsabilidades-seguridad.md` | New | 5.2; responsable de seguridad y DPO como funciones de la organizacion adoptante (sin nombres), matriz RACI |
| `docs/seguridad/plan-respuesta-incidentes-seguridad.md` | New | 5.24, 5.26; fases, severidad/triaje, notificacion 72 h propuesta |
| `docs/seguridad/procedimiento-reporte-eventos.md` | New | 5.25, 5.27, 6.8; canal de reporte y lecciones aprendidas |
| `docs/seguridad/inventario-activos-informacion.md` | New | 5.9; activos de informacion, software, datos y servicios |
| `docs/seguridad/registro-requisitos-legales.md` | New | 5.31; Ley 25.326, AAIP y demas requisitos; responsable del tratamiento y tratamientos T1/T2/T3 |
| `docs/seguridad/modelado-amenazas-sdlc.md` | New | 8.26; modelado de amenazas y gate de seguridad por change |
| `docs/seguridad/politica-privacidad-runtime.md` | New | 5.34; informacion al titular, base de licitud, derechos; describe el objetivo/norma |
| `docs/seguridad/registro-actividades-tratamiento.md` | New | ROPA Ley 25.326 (arts. 21/24); responsable y tratamientos T1/T2/T3; template de inscripcion para el adoptante |
| `openspec/changes/c-61-compliance-gobernanza/**` | New | Artefactos OPSX (proposal, design, specs, tasks) |

Sin cambios en API, esquema de datos, dependencias, CI ni infraestructura.

## Governance

**MEDIO (MEDIUM)**. Es documental, pero define politicas de seguridad, clasificacion de PII y manejo de incidentes que condicionan changes posteriores. No se escribe codigo en esta fase (propose/design only). Los documentos son borradores sujetos a revision del autor; la aprobacion formal de la politica de seguridad queda como tarea humana. Los roles de seguridad se documentan como funciones de la organizacion adoptante (sin nombres de personas). La verificacion es manual (checklist + validacion estricta); el doc-lint automatizado es un change futuro.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Lenguaje que sugiera certificacion | Med | Requisito SGD-009 explicito; revision de redaccion |
| Documentar controles (O) como si estuvieran implementados | Med | Encuadre (D)/(O) explicito y nota de stack de desarrollo local |
| Solapamiento con C-64/C-65/C-66 | Med | Alcance acotado a gobernanza; los demas changes referencian y extienden |
| Deriva entre documentos (versiones contradictorias) | Med | Indice unico y referencias cruzadas; tarea de validacion |
| Documentos que envejecen sin revision | Low | Campo de revision periodica en el indice |

## Rollback Plan

Revertir el commit elimina `docs/seguridad/` y el delta spec de `security-governance-docs`. No hay migraciones, datos, API ni infraestructura que restaurar: el change es puramente aditivo y no afecta runtime. Ningun otro change depende de que los documentos existan para funcionar.

## Dependencies

- `docs/cumplimiento/plan-cambios-cumplimiento.md` (plan aprobado) — insumo de alcance.
- `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` y `docs/cumplimiento/marco-legal-ar-2026.md` — insumos normativos.
- Sin dependencias de changes previos. **Habilita** C-63 (parametros de politica) y da marco a C-62/C-64/C-65/C-66/C-67, que son changes separados.

## Success Criteria

- [ ] Existen los 11 documentos en `docs/seguridad/` con las secciones requeridas por los specs.
- [ ] Cada documento declara su mapeo de controles y usa "alineado con" / "controles mapeados a"; ninguno afirma "certificado" ni "compliant".
- [ ] El indice `docs/seguridad/README.md` incluye el mapa de trazabilidad control -> documento y referencias cruzadas.
- [ ] Roles (incl. DPO), clasificacion (incl. PII/directorio), IR + reporte, ROPA, activos, requisitos legales y SDLC quedan documentados.
- [ ] Queda documentado el responsable del tratamiento (el grupo durante la tesis) y los tres tratamientos T1/T2/T3, con el consentimiento del grupo como base de licitud de T1; queda explicito que el sistema no usa datos ficticios.
- [ ] La politica de privacidad describe el objetivo/norma y remite el estado actual al gap assessment.
- [ ] Queda asentado que la inscripcion de bases (arts. 21/24) es responsabilidad del adoptante y que el sistema entrega un template/checklist.
- [ ] La verificacion es manual (checklist + validacion estricta); el doc-lint automatizado queda registrado como change futuro.
- [ ] Queda explicito que el stack es de desarrollo local y que los controles (O) competen a la organizacion adoptante.
- [ ] Se documenta que C-61 habilita C-63 y que C-62/C-64/C-65/C-66/C-67 son changes separados.
- [ ] `openspec validate --strict --changes c-61-compliance-gobernanza` pasa.
