# Procedimiento de reporte de eventos de seguridad

> **Control mapeado**: ISO/IEC 27002:2022 5.25 (Evaluacion de eventos de seguridad), 5.27
> (Aprendizaje de incidentes), 6.8 (Reporte de eventos de seguridad — (O)); NIST CSF 2.0 RS.
> Requisito SGD-005.
> **Estado**: v1 — aprobada por el autor el 2026-10-01 (governance MEDIO).
> **Alcance**: canal de reporte de eventos y registro de lecciones aprendidas.
> **Encuadre**: stack de desarrollo local; documento **alineado con** los marcos; no es
> certificacion ni auditoria. El canal fisico/organizacional de reporte compete al
> adoptante (O).

## 1. Proposito

Definir como cualquier persona reporta un evento de seguridad y quien lo evalua, y como se
registran y difunden las lecciones aprendidas. Se encadena con
`plan-respuesta-incidentes-seguridad.md`.

## 2. Canal de reporte

Todo evento de seguridad se reporta por un canal unico y trazable:

- **Canal interno de reporte**: incidencia/issue en el repositorio con la etiqueta
  `security`, o el medio interno que designe la organizacion adoptante.
- El reporte debe indicar: fecha/hora, sistema afectado, descripcion del evento, evidencia
  disponible y datos personales involucrados (si los hubiera).
- No se debe incluir en el reporte material de clave ni valores de secretos; se referencia
  su ubicacion, no su valor.

## 3. Rol evaluador

- **Evaluador primario**: **responsable de seguridad de la informacion** (funcion).
- **Consulta obligatoria**: **DPO** (funcion) si el evento involucra datos personales.
- El evaluador confirma el evento, asigna severidad segun
  `plan-respuesta-incidentes-seguridad.md` §3 y decide si se activa el plan de respuesta.
- En la tesis y el piloto, la evaluacion la realiza el grupo de desarrollo en su rol de
  responsable de seguridad (funcion), sin nombrar una persona distinta.

## 4. Registro de lecciones aprendidas

- Cada evento evaluado deja un registro con: identificador, causa raiz, severidad,
  acciones de contencion/erradicacion/recuperacion, controles afectados y mejoras.
- Las lecciones se incorporan al cuerpo documental de `docs/seguridad/` (politica,
  clasificacion, inventario o modelado de amenazas, segun corresponda) y a los changes
  tecnicos que cierren la brecha (C-62 a C-67).
- Se revisan en la revision anual o tras cada incidente S1/S2.

## 5. Encuadre

Documento de **alineacion** con ISO/IEC 27002:2022 5.25/5.27 y NIST CSF 2.0 RS. El control
6.8 (reporte de eventos por el personal) es de tipo **(O)**: la organizacion adoptante debe
instituir formalmente el canal y la obligacion de reportar. No constituye certificacion ni
auditoria.
