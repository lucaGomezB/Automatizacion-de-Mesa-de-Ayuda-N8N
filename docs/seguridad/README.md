# Gobernanza de seguridad y privacidad — indice y trazabilidad

Proyecto: Automatizacion de Mesa de Ayuda N8N (tesis UTN-FRM 2026).
Change: `c-61-compliance-gobernanza` (categoria D — documental; governance MEDIO).
Fecha del cuerpo documental: 2026-10-01.

> **Control mapeado**: transversal. Cubre el mapa de trazabilidad de los controles
> ISO/IEC 27002:2022 5.1, 5.2, 5.9, 5.12, 5.13, 5.24, 5.25, 5.26, 5.27, 5.31, 8.26
> y las funciones NIST CSF 2.0 Govern (GV) e Identify (ID). Requisito: SGD-001.
> **Estado**: v1 — aprobada por el autor el 2026-10-01 (governance MEDIO).
> **Alcance**: documentos de gobernanza de seguridad y privacidad del sistema, en
> `docs/seguridad/`. No cubre implementacion tecnica de controles.
> **Encuadre**: ver §3.

## 1. Proposito

Reunir en un cuerpo documental coherente y trazable las politicas, clasificacion,
roles, planes y registros de seguridad y privacidad del proyecto, destilados de:

- `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` (brechas y controles).
- `docs/cumplimiento/marco-legal-ar-2026.md` (Ley 25.326, AAIP, plazos, transferencias).
- `docs/cumplimiento/plan-cambios-cumplimiento.md` (alcance del workstream de cumplimiento).

Este cuerpo es insumo de los ANEXOS de la tesis. No es prosa de tesis ni reemplaza al
gap assessment: los documentos describen el **objetivo/norma** o el **marco documental**;
el diagnostico del estado actual vive en el gap assessment.

## 2. Regla de lenguaje (transversal — SGD-011)

Todos los documentos de esta carpeta usan **"alineado con"** y **"controles mapeados a"**
al referirse a ISO/IEC 27001:2022, ISO/IEC 27002:2022, ISO/IEC 27701, NIST CSF 2.0 y la
Ley 25.326. Los documentos **no afirman** que el sistema este en estado de certificacion,
sea "compliant" ni que "cumple ISO/NIST".

Lista de terminos prohibidos para describir el sistema (solo se admiten aqui, como lista
de terminos a evitar): `certificado`, `compliant`, `cumple ISO`, `cumple NIST`. Toda
aparicion fuera de esta lista es un defecto de redaccion.

La documentacion es de **alineacion** y **no constituye una certificacion ni una auditoria
formal**.

## 3. Encuadre (D)/(O) y stack de desarrollo local

- El repositorio corresponde a un **stack de desarrollo local** (`docker-compose.yml`,
  `name: mesa_local`). No existe un despliegue productivo declarado.
- Los controles de tipo **(D) documental** son los que este change entrega.
- Los controles **organizacionales (tema 6.x) y fisicos (tema 7.x)** — seleccion de
  personal, formacion, sanciones, contratos, responsabilidades tras el cese, controles
  fisicos, endpoints — competen a la **organizacion adoptante (O)**. No se documentan
  como implementados por el repositorio.
- Los controles de tipo **(T) tecnico** que aun no estan implementados se mapean a los
  changes C-62 a C-67, sin declararlos implementados (ver §7).

## 4. Plantilla comun de documento

Cada documento de `docs/seguridad/` abre con un encabezado con estos campos:

| Campo | Contenido |
|-------|-----------|
| Control mapeado | Control(es) ISO/IEC 27002:2022 + funcion NIST CSF 2.0 + requisito SGD |
| Estado | v1 (aprobada 2026-10-01) / revision periodica |
| Alcance | Que cubre el documento y que queda fuera |
| Encuadre | Nota de stack de desarrollo local y de controles (O) como responsabilidad del adoptante |
| Aviso de lenguaje | "Alineado con"; no es certificacion ni auditoria |

Luego desarrolla las secciones exigidas por su requisito SGD. La periodicidad de revision
sugerida es anual, o ante cambio de alcance, normativa o infraestructura.

## 5. Estado de los documentos

| Documento | Proposito | Estado | Revision sugerida |
|-----------|-----------|--------|-------------------|
| `README.md` | Indice, plantilla, encuadre y mapa de trazabilidad | v1 (aprobada 2026-10-01) | Anual |
| `politica-seguridad-informacion.md` | Politica de seguridad de la informacion (5.1) | v1 (aprobada 2026-10-01) | Anual |
| `clasificacion-etiquetado-informacion.md` | Esquema de clasificacion y etiquetado (5.12, 5.13) | v1 (aprobada 2026-10-01) | Anual |
| `roles-responsabilidades-seguridad.md` | Roles de seguridad y matriz RACI (5.2) | v1 (aprobada 2026-10-01) | Anual |
| `plan-respuesta-incidentes-seguridad.md` | Plan de respuesta a incidentes (5.24, 5.26) | v1 (aprobada 2026-10-01) | Anual |
| `procedimiento-reporte-eventos.md` | Reporte de eventos y lecciones aprendidas (5.25, 5.27, 6.8) | v1 (aprobada 2026-10-01) | Anual |
| `inventario-activos-informacion.md` | Inventario de activos de informacion (5.9) | v1 (aprobada 2026-10-01) | Anual |
| `registro-requisitos-legales.md` | Registro de requisitos legales y regulatorios (5.31) | v1 (aprobada 2026-10-01) | Anual |
| `modelado-amenazas-sdlc.md` | Modelado de amenazas y seguridad en el SDLC (8.26) | v1 (aprobada 2026-10-01) | Anual |
| `politica-privacidad-runtime.md` | Politica de privacidad objetivo/norma (5.34) | v1 (aprobada 2026-10-01) | Anual |
| `registro-actividades-tratamiento.md` | ROPA (Ley 25.326) y tratamientos T1/T2/T3 | v1 (aprobada 2026-10-01) | Anual |
| `gestion-secretos-y-rotacion.md` | Gestion de secretos, inventario de columnas cifradas y runbook de rotacion (8.2, 8.24; IAH-008..010) | v1 (aprobada 2026-10-08) | Anual |
| `ciclo-vida-identidades-y-revision-accesos.md` | Ciclo de vida de identidades y revision de accesos — control organizacional (5.16, 5.18; IAH-011) | v1 (aprobada 2026-10-08) | Anual |

Anexo del cuerpo documental (no es uno de los 11 documentos de gobernanza):

| Documento | Proposito | Estado |
|-----------|-----------|--------|
| `acta-consentimiento-t1.md` | Acta de consentimiento informado del grupo para el tratamiento T1 | v1 (aprobada/firmada 2026-10-01) |

## 6. Mapa de trazabilidad control -> documento -> requisito

### 6.1 ISO/IEC 27002:2022 y NIST CSF 2.0

| Control ISO 27002:2022 | Funcion NIST CSF 2.0 | Documento que lo cubre | Requisito SGD |
|------------------------|----------------------|-------------------------|---------------|
| 5.1 Politicas de seguridad de la informacion | GV | `politica-seguridad-informacion.md` | SGD-002 |
| 5.2 Roles y responsabilidades de seguridad | GV | `roles-responsabilidades-seguridad.md` | SGD-004 |
| 5.9 Inventario de activos de informacion | ID | `inventario-activos-informacion.md` | SGD-006 |
| 5.12 Clasificacion de la informacion | ID | `clasificacion-etiquetado-informacion.md` | SGD-003 |
| 5.13 Etiquetado de la informacion | ID | `clasificacion-etiquetado-informacion.md` | SGD-003 |
| 5.24 Planificacion de gestion de incidentes | RS | `plan-respuesta-incidentes-seguridad.md` | SGD-005 |
| 5.25 Evaluacion de eventos de seguridad | RS | `procedimiento-reporte-eventos.md` | SGD-005 |
| 5.26 Respuesta a incidentes de seguridad | RS | `plan-respuesta-incidentes-seguridad.md` | SGD-005 |
| 5.27 Aprendizaje de incidentes | RS | `procedimiento-reporte-eventos.md`, `plan-respuesta-incidentes-seguridad.md` | SGD-005 |
| 5.31 Requisitos legales y contractuales | GV | `registro-requisitos-legales.md` | SGD-007 |
| 8.26 Requisitos de seguridad de aplicaciones | GV, ID | `modelado-amenazas-sdlc.md` | SGD-008 |
| 8.2 Derechos de acceso privilegiado (gestion de claves) | PR | `gestion-secretos-y-rotacion.md` | IAH-008..010 |
| 8.24 Uso de criptografia | PR | `gestion-secretos-y-rotacion.md` | IAH-008..010 |
| 5.16 Gestion del ciclo de vida de la identidad | GV | `ciclo-vida-identidades-y-revision-accesos.md` | IAH-011 |
| 5.18 Derechos de acceso | GV | `ciclo-vida-identidades-y-revision-accesos.md` | IAH-011 |
| 5.34 Privacidad y proteccion de PII | GV, PR | `politica-privacidad-runtime.md` | SGD-009 |
| ROPA (Ley 25.326) | GV | `registro-actividades-tratamiento.md` | SGD-010 |

Funciones NIST CSF 2.0 cubiertas: **Govern (GV)** — 5.1, 5.2, 5.31, 8.26, 5.34, ROPA;
**Identify (ID)** — 5.9, 5.12, 5.13, 8.26. Las funciones Proteger (PR), Detectar (DE),
Responder (RS) y Recuperar (RC) se cubren parcialmente; su cierre tecnico esta en C-62 a
C-67.

### 6.2 Matriz requisito SGD -> documento

| Requisito | Documento(s) |
|-----------|--------------|
| SGD-001 Ubicacion, indice y trazabilidad | `README.md` |
| SGD-002 Politica de seguridad de la informacion | `politica-seguridad-informacion.md` |
| SGD-003 Clasificacion y etiquetado | `clasificacion-etiquetado-informacion.md` |
| SGD-004 Roles y responsabilidades | `roles-responsabilidades-seguridad.md` |
| SGD-005 IR y reporte de eventos | `plan-respuesta-incidentes-seguridad.md`, `procedimiento-reporte-eventos.md` |
| SGD-006 Inventario de activos | `inventario-activos-informacion.md` |
| SGD-007 Registro de requisitos legales | `registro-requisitos-legales.md` |
| SGD-008 Modelado de amenazas y SDLC | `modelado-amenazas-sdlc.md` |
| SGD-009 Privacidad en runtime | `politica-privacidad-runtime.md` |
| SGD-010 ROPA | `registro-actividades-tratamiento.md` |
| SGD-011 Regla de lenguaje y encuadre | transversal (§2 y §3); aplica a todos |
| SGD-012 Responsable y los tres tratamientos | `registro-actividades-tratamiento.md`, `registro-requisitos-legales.md`, `acta-consentimiento-t1.md` |
| IAH-008 Rotacion del secreto JWT (keyring `kid`) | `gestion-secretos-y-rotacion.md` |
| IAH-009 Rotacion de la clave Fernet | `gestion-secretos-y-rotacion.md` |
| IAH-010 Higiene y gestion de secretos | `gestion-secretos-y-rotacion.md` |
| IAH-011 Ciclo de vida de identidades y revision de accesos | `ciclo-vida-identidades-y-revision-accesos.md` |

## 7. Relaciones entre changes

- C-61 **habilita C-63** (`identidad-accesos-claves`) fijando los parametros de politica
  (clasificacion, roles, requisitos) que C-63 consume.
- El desglose de C-63 (`c-63a`, `c-63b`, `c-63c`) extiende este cuerpo documental:
  `c-63c` agrega `gestion-secretos-y-rotacion.md` (8.2/8.24; IAH-008..010) y
  `ciclo-vida-identidades-y-revision-accesos.md` (5.16/5.18; IAH-011).
- **C-62** (`hardening-infra-red`), **C-64** (`vulnerabilidades-supply-chain`), **C-65**
  (`backup-continuidad`), **C-66** (`privacidad-transferencias`) y **C-67**
  (`notificacion-sms-llamante`) son **changes separados**. C-61 documenta el marco; ellos
  implementan y extienden. Ver `docs/cumplimiento/plan-cambios-cumplimiento.md` §2-§4.
- La politica de privacidad en runtime y el ROPA documentan el marco legal; el tratamiento
  del numero llamante y los instrumentos de transferencia son de C-66.

## 8. Verificacion y estado de aprobacion

- La verificacion de este change es **MANUAL**: la lista de comprobacion de
  `openspec/changes/c-61-compliance-gobernanza/tasks.md` (existencia de los 11 documentos,
  secciones, encuadre, terminos prohibidos) mas
  `openspec validate --strict --changes c-61-compliance-gobernanza`.
- **No** se implementa doc-lint automatizado en C-61. Queda registrado como **change
  futuro** (patron c-42), que agregaria un script/test que valide estructura, encabezados y
  terminos prohibidos de esta carpeta.
- **Aprobacion humana completada (governance MEDIO)**: la politica de seguridad
  (`politica-seguridad-informacion.md`) y los roles
  (`roles-responsabilidades-seguridad.md`) fueron **aprobados como v1 por el autor el
  2026-10-01**; el resto de los documentos del cuerpo se eleva a **v1 aprobada**. El piloto
  opera con datos reales del grupo (T1) bajo consentimiento documentado
  (`acta-consentimiento-t1.md`). Los datos de produccion de un adoptante (T3) **no se
  activan** sin su aprobacion.
- **Pendiente para el orquestador**: evaluar la actualizacion de `CHANGES.md` con la
  entrada de C-61 (governance MEDIO, habilita C-63, dependencias nulas). `CHANGES.md` NO
  se modifica en este change.

## 9. Fuentes internas

- `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`
- `docs/cumplimiento/marco-legal-ar-2026.md`
- `docs/cumplimiento/plan-cambios-cumplimiento.md`
- `docs/security-hardening.md`
- `openspec/changes/c-61-compliance-gobernanza/{proposal.md,design.md,tasks.md}`
- `knowledge-base/03_actores_y_roles.md`, `knowledge-base/04_modelo_de_datos.md`
