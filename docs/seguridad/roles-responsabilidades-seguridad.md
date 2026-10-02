# Roles y responsabilidades de seguridad

> **Control mapeado**: ISO/IEC 27002:2022 5.2 (Roles y responsabilidades de seguridad);
> NIST CSF 2.0 GV (Govern). Requisito SGD-004.
> **Estado**: v1 — APROBADA por el autor el 2026-10-01 (governance MEDIO).
> **Alcance**: roles de seguridad y privacidad y matriz de asignacion de responsabilidades.
> **Encuadre**: roles definidos como **FUNCIONES de la organizacion adoptante**. No se
> nombran personas. Stack de desarrollo local; documento **alineado con** los marcos; no es
> certificacion ni auditoria.

## 1. Proposito

Definir los roles de seguridad —en particular el **responsable de seguridad de la
informacion** y el **responsable de proteccion de datos (DPO)**— como **FUNCIONES** de la
organizacion adoptante, con sus responsabilidades, y fijar una matriz de asignacion
(RACI) para las actividades de seguridad y privacidad documentadas por el change.

## 2. Distincion roles organizacionales vs. roles tecnicos

| Tipo | Definicion | Ejemplos |
|------|------------|----------|
| **Organizacional (O)** | Función designada nominalmente por la organizacion adoptante. No se nombra en el repositorio | Responsable de seguridad de la informacion; DPO; responsable de aprobacion de accesos |
| **Tecnico observable** | Rol operativo que el repositorio modela y aplica en codigo/configuracion | Usuario; operador de mesa de ayuda; sector responsable; `administrador_directorio`; token de servicio N8N |

La asignacion nominal de las funciones organizacionales queda a cargo del adoptante. En la
tesis, el grupo de desarrollo actua como responsable del tratamiento del piloto (T1); esa
condicion se documenta en `acta-consentimiento-t1.md` y el ROPA, no como rol de seguridad
nominal.

## 3. Roles de seguridad

### 3.1 Responsable de seguridad de la informacion (funcion)

Responsabilidades:

- Mantener, aprobar y comunicar la politica de seguridad (`politica-seguridad-informacion.md`).
- Aprobar el esquema de clasificacion y las decisiones de tratamiento por nivel.
- Ser el punto de decision en el ciclo de respuesta a incidentes
  (`plan-respuesta-incidentes-seguridad.md`).
- Autorizar excepciones a la politica y revisarlas periodicamente.
- Coordinar la revision anual del cuerpo documental de `docs/seguridad/`.

### 3.2 Responsable de proteccion de datos / DPO (funcion)

> Nota: la Ley 25.326 vigente **no** exige la figura de un DPO con ese nombre (a diferencia
> del RGPD). Se documenta como **funcion** de buena practica, alineada con ISO/IEC 27701 y
> con el deber de informacion de la Ley 25.326.

Responsabilidades:

- Asesorar sobre el marco legal de proteccion de datos (`registro-requisitos-legales.md`).
- Mantener el ROPA (`registro-actividades-tratamiento.md`) y las bases de licitud.
- Atender y tramitar las solicitudes de los titulares (acceso, rectificacion, supresion)
  con los plazos legales.
- Supervisar las transferencias internacionales y los instrumentos aplicables.
- Coordinar la evaluacion de inscripcion de bases (arts. 21/24) con el adoptante.

### 3.3 Responsables tecnicos observables en el repositorio

- **Operador de mesa de ayuda / sector responsable**: opera la cola de revision humana y
  valida clasificaciones.
- **`administrador_directorio`**: administra altas, bajas y datos del directorio.
- **Token de servicio N8N**: crea incidentes e invoca la clasificacion (menor privilegio).

## 4. Matriz RACI

`R` = Responsable de ejecutar; `A` = Aprueba/rinde cuentas; `C` = Consultado; `I` = Informado.
Las columnas organizacionales son **funciones** de la organizacion adoptante.

| Actividad | Resp. seguridad | DPO | Operador/sector | Adoptante (O) |
|-----------|:---:|:---:|:---:|:---:|
| Aprobar politica de seguridad | A/R | C | I | A |
| Aprobar clasificacion de la informacion | A/R | C | I | I |
| Mantener inventario de activos | R | C | I | I |
| Aprobar/revisar accesos (5.18) | C | I | R | A |
| Planificar y dirigir respuesta a incidentes | A/R | C | R | I |
| Evaluar eventos reportados | R | C | C | I |
| Registrar lecciones aprendidas | R | I | C | I |
| Atender derechos de titulares | I | A/R | R | I |
| Mantener ROPA y bases de licitud | C | A/R | I | C |
| Evaluar inscripcion de bases (arts. 21/24) | I | C | I | A/R |
| Aprobar transferencias internacionales | C | A/R | I | I |
| Revision anual del cuerpo documental | A/R | C | I | I |

## 5. Encuadre

Documento de **alineacion** con ISO/IEC 27002:2022 5.2 y NIST CSF 2.0 GV. Los roles de
seguridad son **funciones** de la organizacion adoptante; no se nombran personas concretas
en el repositorio. No constituye certificacion ni auditoria.
