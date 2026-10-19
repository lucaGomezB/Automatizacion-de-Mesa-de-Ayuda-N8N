# Politica de retencion de logs

> **Control mapeado**: ISO/IEC 27002:2022 8.12 (Prevencion de fuga de datos), 8.15 (Registro
> de eventos) y 5.34 (Privacidad y proteccion de PII), en **alineacion con** ISO/IEC 27701 y
> el deber de seguridad de la Ley 25.326 art. 9; NIST CSF 2.0 PR, GV. Requisito SGD-015.
> **Estado**: v1 — aprobada por el autor el 2026-10-19 (governance MEDIO).
> **Alcance**: retencion de los registros del sistema por clase de registro, el no-PII en
> logs y la exclusion de centralizacion/SIEM. No cubre la implementacion de la infraestructura
> de logging.
> **Encuadre**: stack de desarrollo local; documento **alineado con** los marcos; no es
> certificacion ni auditoria.

## 1. Proposito

Definir por cuanto tiempo se conserva cada **clase de registro** del sistema y que datos
personales **no** deben quedar en claro en los logs, para acotar la retencion al minimo
necesario y evitar la fuga de datos personales por registros.

## 2. Clases de registro y plazos

| Clase de registro | Que contiene | Retencion | Fundamento |
|-------------------|--------------|-----------|------------|
| **Ejecucion del sistema** (por ejemplo, ejecuciones de N8N) | Trazas de ejecucion del orquestador y del backend | **30 dias** | Poda vigente del orquestador; consistente con el capitulo 11 de la tesis |
| **Contadores de tasa por origen** (guarda de costo) | Conteo agregado por identificador derivado | **Solo durante la ventana del contador**; se purga al cerrar la ventana | No se conserva el historico por origen |
| **Registro de auditoria de cambios** | Actor, marca temporal y delta de las modificaciones | Segun la politica de la organizacion adoptante | Trazabilidad del sistema |

Los contadores por origen usan como clave el **numero crudo** del llamante en el almacen
efimero de la guarda, y la **purga por ventana** acota su retencion: al cerrar la ventana el
contador se elimina, por lo que **no existe retencion historica por origen**.

## 3. No-PII en logs

- El **numero de origen NO se registra CRUDO** en los eventos estructurados. Los eventos del
  guarda emiten un **identificador derivado no reversible**, obtenido con **HMAC-SHA-256**
  sobre el numero, usando una **clave DEDICADA** (`cost_guard_caller_hmac_key`, env
  `COST_GUARD_CALLER_HMAC_KEY`), **independiente** de la clave de pseudonimizacion
  (Fernet/`PSEUDONYMIZATION_ENCRYPTION_KEY`). No se reutiliza material de clave entre
  primitivas (Fernet vs HMAC) ni se acopla la rotacion de Fernet a los identificadores de
  log. El identificador se trunca (aproximadamente 12 caracteres hex) y permite correlacionar
  llamadas del mismo origen dentro de la ventana, sin ser reversible sin la clave.
- Los **datos personales del directorio** (correo corporativo y telefono) **NO aparecen en
  claro** en los logs. La representacion de las entidades (`__repr__`) no incluye PII.
- El corpus de evaluacion **no incluye el numero de origen**.

## 4. Alcance y exclusiones

- Quedan **fuera del alcance** de esta politica la **centralizacion de logs**, el **SIEM** y
  la **deteccion de anomalias**. Las brechas 8.15/8.16 de
  `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` se mapean a **changes
  separados**; este documento solo define la retencion y el no-PII de los registros que el
  sistema ya produce.
- No se documenta aqui la infraestructura de logging (agregacion, transporte, almacenamiento
  central): es objetivo de la organizacion adoptante.

## 5. Relacion con el ROPA

El ROPA (`registro-actividades-tratamiento.md` §6) declara la conservacion por actividad; esta
politica lo complementa con la retencion por **clase de registro** (ejecucion del sistema,
contadores de origen, auditoria). Ambas deben permanecer consistentes.

## 6. Encuadre

Documento de **alineacion** con ISO/IEC 27002:2022 8.12/8.15 y 5.34, ISO/IEC 27701 y la Ley
25.326. No constituye certificacion ni auditoria. La centralizacion, el SIEM y la deteccion
de anomalias son changes futuros.
