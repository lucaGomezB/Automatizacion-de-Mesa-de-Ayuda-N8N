# Acta de consentimiento informado — tratamiento T1 (piloto/desarrollo)

> **Control mapeado**: soporte documental de la base de licitud de la Ley 25.326 art. 5;
> requisito SGD-012. No es uno de los 11 documentos de gobernanza: es el **acta** que
> respalda el tratamiento T1.
> **Estado**: v1 — aprobada/firmada el 2026-10-01.
> **Alcance**: consentimiento del propio grupo de desarrollo para el tratamiento T1.
> **Encuadre**: documento **alineado con** la Ley 25.326; no constituye certificación ni
> auditoría.

## 1. Partes y contexto

El grupo de desarrollo del proyecto "Automatización de Mesa de Ayuda N8N" (tesis UTN-FRM
2026), en su condición de **responsable del tratamiento** durante la tesis (responsable
directo, **no** la UTN-FRM), opera un **piloto con datos reales** del propio equipo.

Integrantes del grupo que prestan su consentimiento informado:

- Luca Gomez
- Carla Bustos
- Gonzalo Sevilla

## 2. Objeto del consentimiento

El grupo consiente el tratamiento de **sus propios datos personales** (cuentas, correo
electrónico y/o número de contacto) en el marco del tratamiento **T1 Piloto/desarrollo**,
que comprende:

- Cuentas del grupo dentro del sistema.
- Usuarios de prueba cuyos correos o celulares **apuntan a contactos del propio grupo**,
  usados para depuración (debugging) del flujo de notificaciones.

## 3. Información prestada (deber de información, art. 6)

Se informa a las partes:

- **Finalidad**: validar el funcionamiento del sistema de registro y clasificación de
  incidentes y sus notificaciones, y producir el corpus de investigación (T2).
- **Datos tratados**: identificadores de cuenta, correo y número de contacto.
- **Destinatarios/encargados**: N8N (orquestación), Google Gemini (inferencia, solo texto
  pseudonimizado), Twilio (telefonía/SMS), Microsoft Outlook (correo).
- **Transferencia internacional**: los servicios de Gemini y Twilio tienen sede en
  **Estados Unidos**, país **no adecuado** conforme al art. 12; se requiere instrumento
  (cláusulas modelo o consentimiento). Ver `registro-actividades-tratamiento.md`.
- **Carácter de las respuestas**: la participación en el piloto es **voluntaria**; no
  responder o retirarse no genera consecuencias negativas.
- **Derechos**: acceso (10 días corridos, art. 14) y rectificación/actualización/supresión
  (5 días hábiles, art. 16). La ley vigente **no** enumera un derecho autónomo de
  oposición.
- **No se usan datos ficticios**: el piloto opera con datos reales del equipo.

## 4. Manifestación

Las partes manifiestan haber leído y comprendido la información precedente y **prestan su
consentimiento libre, expreso e informado** para el tratamiento T1 descripto.

## 5. Registro

| Integrante | Consentimiento | Fecha |
|------------|----------------|-------|
| Luca Gomez | Sí | 2026-10-01 |
| Carla Bustos | Sí | 2026-10-01 |
| Gonzalo Sevilla | Sí | 2026-10-01 |

Este acta se referencia desde `registro-actividades-tratamiento.md` (T1) y desde
`registro-requisitos-legales.md` §5 como base de licitud del tratamiento T1.

## 6. Encuadre

El acta documenta el consentimiento del **propio grupo** para el piloto. La organización
adoptante (T3) deberá establecer su propia base de licitud y su política; los datos de
producción de un adoptante no se activan sin su aprobación.
