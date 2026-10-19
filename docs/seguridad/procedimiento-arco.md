# Procedimiento ARCO (derechos del titular)

> **Control mapeado**: ISO/IEC 27002:2022 5.34 (Privacidad y proteccion de PII), en
> **alineacion con** ISO/IEC 27701 y los articulos 14 y 16 de la Ley 25.326; NIST CSF 2.0
> GV. Requisito SGD-013.
> **Estado**: v1 — aprobada por el autor el 2026-10-19 (governance MEDIO).
> **Alcance**: procedimiento operativo para el ejercicio de los derechos del titular
> (acceso; rectificacion, actualizacion y supresion). El canal es **informado**; NO se
> implementa endpoint backend de solicitudes.
> **Encuadre**: stack de desarrollo local; documento **alineado con** los marcos; no es
> certificacion ni auditoria. El canal y la funcion responsable corresponden a la
> organizacion adoptante.

## 1. Alcance y encuadre

Este procedimiento describe como el titular ejerce sus derechos sobre los datos tratados por
el sistema (gestion de incidentes y directorio de empleados). El canal es **INFORMADO**: la
superficie de privacidad en runtime (`/privacidad`) indica al titular ante quien presentar
la solicitud, y este documento describe la tramitacion. **NO** se introduce ni se exige un
endpoint backend de solicitudes ARCO (defecto mantenido por decision; ver §7).

## 2. Canal de presentacion y funcion responsable

- **Canal**: el **informado por la funcion de proteccion de datos de la organizacion
  adoptante** (el mismo canal publicado en la superficie de privacidad). La presentacion no
  requiere autenticarse en el sistema.
- **Funcion responsable**: la **funcion de proteccion de datos de la organizacion
  adoptante** (responsable de proteccion de datos), **sin nombrar personas**. Recibe,
  tramita y resuelve la solicitud, y es la unica habilitada a responderla.
- **Responsable del tratamiento**: la organizacion adoptante (ver
  `registro-actividades-tratamiento.md` §2).

## 3. Acciones por derecho y plazos

| Derecho | Accion | Plazo legal |
|---------|--------|-------------|
| **Acceso** (art. 14) | Poner a disposicion del titular la informacion sobre sus datos personales tratados | **10 dias corridos** desde la intimacion fehaciente |
| **Rectificacion** (art. 16) | Corregir datos inexactos o incompletos | **5 dias habiles** desde el reclamo o desde que se advierte el error |
| **Actualizacion** (art. 16) | Poner al dia datos desactualizados | **5 dias habiles** desde el reclamo o desde que se advierte el error |
| **Supresion** (art. 16) | Suprimir datos cuando corresponda | **5 dias habiles** desde el reclamo o desde que se advierte el error |

- El ejercicio del derecho de acceso es **gratuito** a intervalos no inferiores a **seis
  meses**, salvo interes legitimo acreditado.
- En caso de cesion o transferencia, la rectificacion o supresion se **notifica al
  cesionario dentro del quinto dia habil** (art. 16).

### 3.1 Sobre el derecho de oposicion

La **Ley 25.326 vigente no enumera un derecho autonomo de oposicion** separado. El acronimo
"ARCO" proviene de la practica comparada y de los proyectos de reforma; no debe atribuirse a
la ley vigente un derecho generico de oposicion. Este procedimiento cubre **acceso,
rectificacion, actualizacion y supresion**.

## 4. Tramitacion

1. **Recepcion**: la funcion de proteccion de datos recibe la solicitud por el canal
   informado y la registra.
2. **Verificacion**: se verifica la identidad del titular y la procedencia de la solicitud.
3. **Resolucion**: se ejecuta la accion por derecho dentro del plazo legal aplicable.
4. **Respuesta**: se comunica al titular la resolucion por el canal informado.
5. **Constancia**: la solicitud, su tramite y su resolucion quedan **registrados de forma
   auditable** (§5).

## 5. Constancia auditable

Toda solicitud ARCO deja **constancia auditable** en un registro de la organizacion
adoptante, con: fecha de recepcion, derecho ejercido, canal, resolucion adoptada, fecha de
resolucion y responsable interviniente (por funcion, sin datos innecesarios del titular). El
registro es la evidencia del tramite y su plazo, y es responsabilidad de la funcion de
proteccion de datos. El detalle operativo del registro es de la organizacion adoptante.

## 6. Remision a la superficie de privacidad

El canal informado en este procedimiento es el publicado en la superficie de privacidad en
runtime (`/privacidad`, change C-66): "canal informado por la funcion de proteccion de datos
de la organizacion adoptante". El titular conoce el canal **antes** de tratar sus datos, en
el punto de recoleccion (formulario de reporte y pagina de login).

## 7. Encuadre de decisiones (OQ2 resuelto)

- **El canal es informado y NO se implementa endpoint backend de solicitudes ARCO.** Se
  evaluo un formulario/endpoint dedicado y se **descarto**: un canal informado con registro
  auditable atiende el requisito sin ampliar la superficie ni recolectar datos nuevos. Un
  formulario dedicado queda como eventual change futuro, sin acoplarse a C-66.
- La verificacion de no regresion: no deben existir rutas backend nuevas de solicitudes
  ARCO (`grep` sobre `App/Backend/app/routes/`).

## 8. Encuadre

Documento de **alineacion** con ISO/IEC 27002:2022 5.34, ISO/IEC 27701 y la Ley 25.326.
Describe el objetivo/norma y el procedimiento, no el estado actual. No constituye
certificacion ni auditoria. La ejecucion real del procedimiento es responsabilidad de la
organizacion adoptante.
