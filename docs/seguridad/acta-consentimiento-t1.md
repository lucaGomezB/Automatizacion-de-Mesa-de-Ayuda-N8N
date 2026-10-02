# Acta de consentimiento informado — tratamiento T1 (piloto/desarrollo)

> **Control mapeado**: soporte documental de la base de licitud de la Ley 25.326 art. 5;
> requisito SGD-012. No es uno de los 11 documentos de gobernanza: es el **acta** que
> respalda el tratamiento T1.
> **Estado**: v1 — aprobada/firmada el 2026-10-01.
> **Alcance**: consentimiento del propio grupo de desarrollo para el tratamiento T1.
> **Encuadre**: documento **alineado con** la Ley 25.326; no constituye certificacion ni
> auditoria.

## 1. Partes y contexto

El grupo de desarrollo del proyecto "Automatizacion de Mesa de Ayuda N8N" (tesis UTN-FRM
2026), en su condicion de **responsable del tratamiento** durante la tesis (responsable
directo, **no** la UTN-FRM), opera un **piloto con datos reales** del propio equipo.

Integrantes del grupo que prestan su consentimiento informado:

- Luca Gomez
- Carla Bustos
- Gonzalo Sevilla

## 2. Objeto del consentimiento

El grupo consiente el tratamiento de **sus propios datos personales** (cuentas, correo
electronico y/o numero de contacto) en el marco del tratamiento **T1 Piloto/desarrollo**,
que comprende:

- Cuentas del grupo dentro del sistema.
- Usuarios de prueba cuyos correos o celulares **apuntan a contactos del propio grupo**,
  usados para depuracion (debugging) del flujo de notificaciones.

## 3. Informacion prestada (deber de informacion, art. 6)

Se informa a las partes:

- **Finalidad**: validar el funcionamiento del sistema de registro y clasificacion de
  incidentes y sus notificaciones, y producir el corpus de investigacion (T2).
- **Datos tratados**: identificadores de cuenta, correo y numero de contacto.
- **Destinatarios/encargados**: N8N (orquestacion), Google Gemini (inferencia, solo texto
  pseudonimizado), Twilio (telefonia/SMS), Microsoft Outlook (correo).
- **Transferencia internacional**: los servicios de Gemini y Twilio tienen sede en
  **Estados Unidos**, pais **no adecuado** conforme al art. 12; se requiere instrumento
  (clausulas modelo o consentimiento). Ver `registro-actividades-tratamiento.md`.
- **Caracter de las respuestas**: la participacion en el piloto es **voluntaria**; no
  responder o retirarse no genera consecuencias negativas.
- **Derechos**: acceso (10 dias corridos, art. 14) y rectificacion/actualizacion/supresion
  (5 dias habiles, art. 16). La ley vigente **no** enumera un derecho autonomo de
  oposicion.
- **No se usan datos ficticios**: el piloto opera con datos reales del equipo.

## 4. Manifestacion

Las partes manifiestan haber leido y comprendido la informacion precedente y **prestan su
consentimiento libre, expreso e informado** para el tratamiento T1 descripto.

## 5. Registro

| Integrante | Consentimiento | Fecha |
|------------|----------------|-------|
| Luca Gomez | Si | 2026-10-01 |
| Carla Bustos | Si | 2026-10-01 |
| Gonzalo Sevilla | Si | 2026-10-01 |

Este acta se referencia desde `registro-actividades-tratamiento.md` (T1) y desde
`registro-requisitos-legales.md` §5 como base de licitud del tratamiento T1.

## 6. Encuadre

El acta documenta el consentimiento del **propio grupo** para el piloto. La organizacion
adoptante (T3) debera establecer su propia base de licitud y su politica; los datos de
produccion de un adoptante no se activan sin su aprobacion.
