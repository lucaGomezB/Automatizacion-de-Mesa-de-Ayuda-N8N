# Procedimiento ARCO del directorio de empleados

> **Control mapeado**: ISO/IEC 27002:2022 5.34 (Privacidad y proteccion de PII), en
> **alineacion con** ISO/IEC 27701 y los articulos 14 y 16 de la Ley 25.326; NIST CSF 2.0
> GV. Requisito DIR-015.
> **Estado**: v1 — elaborado en el change `c-153` (governance HIGH).
> **Alcance**: aplica el procedimiento general `docs/seguridad/procedimiento-arco.md` a los
> datos personales del **directorio de empleados** (`directorio_empleado`). Cubre ACCESO,
> RECTIFICACION, ACTUALIZACION y SUPRESION; NO limita el flujo a la supresion.
> **Encuadre**: stack de desarrollo local; documento **alineado con** los marcos; no es
> certificacion ni auditoria. El canal y la funcion responsable corresponden a la
> organizacion adoptante.

## 1. Encuadre y relacion con el procedimiento general

Este documento **complementa** `docs/seguridad/procedimiento-arco.md` para el directorio. El
procedimiento general define el canal informado, la funcion responsable, la tramitacion y la
constancia; este documento particulariza las acciones sobre los datos del directorio y su
evidencia interna. El canal es **informado** y NO se implementa un endpoint backend de
solicitudes ARCO (misma decision que el procedimiento general).

## 2. Datos alcanzados

Las solicitudes ARCO sobre el directorio alcanzan los campos de contacto y de identificacion
del empleado: `legajo`, `nombre`, `email`, `telefono`, `sector_id`, `rol`, `activo` y
`fecha_baja`. El contacto se almacena **cifrado at-rest** (`EncryptedText`) y se busca por
indice ciego; el titular recibe su informacion en claro por el canal informado, sin exponerla
en logs ni en la auditoria.

## 3. Acciones por derecho y plazos

| Derecho | Accion sobre el directorio | Plazo legal |
|---------|----------------------------|-------------|
| **Acceso** (art. 14) | Poner a disposicion del titular los datos del directorio que le conciernen | **10 dias corridos** desde la intimacion fehaciente |
| **Rectificacion** (art. 16) | Corregir los datos inexactos o incompletos del directorio (por ejemplo, contacto o nombre) | **5 dias habiles** desde el reclamo o desde que se advierte el error |
| **Actualizacion** (art. 16) | Poner al dia los datos desactualizados del directorio | **5 dias habiles** desde el reclamo o desde que se advierte el error |
| **Supresion** (art. 16) | Suprimir la fila del directorio cuando corresponda (borrado ARCO explicito) | **5 dias habiles** desde el reclamo o desde que se advierte el error |

- El ejercicio del derecho de **acceso** es gratuito a intervalos no inferiores a seis meses,
  salvo interes legitimo acreditado (mismo criterio que el procedimiento general).
- La **rectificacion** y la **actualizacion** se ejecutan con la operacion de edicion del
  servicio de directorio (`actualizar_empleado`), revalidando la unicidad de legajo/email y el
  formato E.164 del telefono.
- La **supresion** se ejecuta con el borrado ARCO del directorio (`borrar_empleado_arco`),
  distinto del borrado por vencimiento de retencion.

## 4. Tramitacion

1. **Recepcion**: la funcion de proteccion de datos recibe la solicitud por el canal informado
   y la registra.
2. **Verificacion**: se verifica la identidad del titular y la procedencia de la solicitud.
3. **Resolucion**: se ejecuta la accion por derecho dentro del plazo legal aplicable:
   acceso (puesta a disposicion), rectificacion o actualizacion (edicion de los datos) o
   supresion (borrado ARCO).
4. **Respuesta**: se comunica al titular la resolucion por el canal informado.
5. **Constancia**: la solicitud, su tramite y su resolucion quedan **registrados de forma
   auditable** (seccion 5).

## 5. Constancia auditable

Toda solicitud ARCO sobre el directorio deja **constancia auditable** en un registro de la
organizacion adoptante, con: fecha de recepcion, derecho ejercido, canal, resolucion
adoptada, fecha de resolucion y responsable interviniente (por funcion, sin datos
innecesarios del titular). El registro es la evidencia del tramite y su plazo y es
responsabilidad de la funcion de proteccion de datos.

Ademas, las operaciones de gestion del directorio dejan traza en la auditoria durable
`directorio_auditoria` (append-only y sin PII): la edicion por rectificacion y el borrado ARCO
por supresion quedan auditados con actor, operacion, resultado e instante, sin el valor de
contacto en claro.

## 6. Derechos no enumerados

La Ley 25.326 vigente no enumera un derecho autonomo de oposicion separado; el acronimo ARCO
proviene de la practica comparada. Este procedimiento cubre **acceso, rectificacion,
actualizacion y supresion**, en linea con el procedimiento general.

## 7. Encuadre

Documento de **alineacion** con ISO/IEC 27002:2022 5.34, ISO/IEC 27701 y la Ley 25.326.
Describe el objetivo/norma y el procedimiento, no el estado actual. No constituye
certificacion ni auditoria. La ejecucion real del procedimiento es responsabilidad de la
organizacion adoptante.
