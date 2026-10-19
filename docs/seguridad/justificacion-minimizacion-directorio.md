# Justificacion por minimizacion del contacto del directorio (texto plano)

> **Control mapeado**: ISO/IEC 27002:2022 5.34 (Privacidad y proteccion de PII) y 8.12
> (Prevencion de fuga de datos), en **alineacion con** ISO/IEC 27701 y el principio de
> minimizacion de la Ley 25.326 art. 4; NIST CSF 2.0 GV, PR. Hallazgo 5.34/8.12.
> **Estado**: v1 — aprobada por el autor el 2026-10-19 (governance MEDIO).
> **Alcance**: justifica la decision de almacenar el email y el telefono del directorio
> (`directorio_empleado`) en texto plano, SIN cifrado de aplicacion ni indice ciego.
> No cubre otros campos ni otras entidades.
> **Encuadre**: stack de desarrollo local; documento **alineado con** los marcos; no es
> certificacion ni auditoria. La justificacion es la decision de diseno vigente.

## 1. Decision

El modelo `App/Backend/app/models/empleado.py` almacena `email` y `telefono` en **texto
plano** (`String`), sin cifrado de aplicacion (Fernet/`EncryptedText`) y sin **indice
ciego**. Esta es la decision **D4** del modelo y la **DIR-005** del directorio, y coincide
con lo que la tesis ya afirma en el capitulo 5 (`05-arquitectura.tex:98`): los datos de
contacto del directorio se almacenan en texto plano **para su auditabilidad directa**.

Este documento **no** cambia esa decision: la justifica por **minimizacion** y registra las
alternativas evaluadas y descartadas, cerrando el hallazgo 5.34/8.12 como control (D)
documental.

## 2. Finalidad del tratamiento del contacto

- El directorio existe con una unica finalidad: la **resolucion de contacto** y la
  **notificacion al usuario** en la gestion de incidentes (enrutamiento y aviso).
- Se almacenan **exactamente** los campos definidos en el modelo (`legajo`, `nombre`,
  `email`, `telefono`, `sector_id`, `rol`, `activo`, `fecha_baja`), sin datos adicionales
  (D6b, minimizacion).
- El correo y el telefono **no son datos sensibles** bajo el articulo 2 de la Ley 25.326.
  Su tratamiento se sustenta en la relacion contractual/laboral (art. 5, inc. 2, apartado d)
  con el deber de informacion del articulo 6 subsistente.

## 3. Por que la minimizacion basta (razon de la decision)

La proteccion del contacto se sustenta en tres controles ya presentes, que en conjunto
hacen **desproporcionado** el costo de cifrar el dato:

1. **Control de acceso por rol.** El acceso al directorio esta gobernado por RBAC
   (`app.services.role_policy`); solo `administrador_directorio` y `mesa_de_ayuda` operan
   sobre el directorio. La lectura esta acotada al personal autorizado.
2. **Red aislada.** Los servicios (N8N, backend, PostgreSQL, Redis) se comunican sobre la
   red interna aislada de Docker, que constituye el perimetro de confianza
   (`11-aspectos-legales.tex:24`).
3. **Auditabilidad directa.** El texto plano permite **resolucion de contactos y unicidad
   de email** de forma operativa y auditable, y no impide el registro de auditoria de los
   accesos.

En terminos de minimizacion, el beneficio de cifrar el contacto es marginal porque el dato
no es sensible y su exposicion ya esta acotada por rol + red + auditoria.

## 4. Alternativas evaluadas y descartadas

| Alternativa | Descripcion | Motivo de descarte |
|-------------|-------------|--------------------|
| **A. Cifrado de aplicacion (`EncryptedText`, Fernet)** | Cifrar `email` y `telefono` a nivel de aplicacion | Agrega custodia de claves (generacion, rotacion, backup, runbook), **rompe las consultas SQL operativas** del directorio (resolucion de contactos y unicidad de email) y aporta un beneficio marginal sobre un dato no sensible (art. 2). |
| **B. Indice ciego (HMAC) para busqueda cifrada** | Cifrar el campo y mantener un indice HMAC para poder consultarlo | Suma complejidad de claves sin un caso de uso que lo justifique: la finalidad del directorio es la resolucion de contacto, que el texto plano ya cubre. No agrega proteccion frente a un acceso ya acotado por rol y red. |

**Elegida**: justificacion documental (texto plano + minimizacion + RBAC + red aislada +
auditoria). Es de bajo costo, coincide con la tesis y no degrada la operacion.

## 5. Trazabilidad del hallazgo

- **Hallazgo 5.34 / 8.12**: el email y el telefono del directorio en texto plano aparecian
  como brecha mapeada a ISO 5.34 (PII) y 8.12 (fuga de datos). Este documento **cierra el
  hallazgo como control (D)**: se justifica por minimizacion, con las alternativas de
  cifrado e indice ciego registradas como evaluadas y descartadas.
- **Fuente**: `App/Backend/app/models/empleado.py` (D4 / DIR-005), hallazgos 5.34/8.12 de
  `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`.
- **Tesis**: `05-arquitectura.tex:98` (texto plano para auditabilidad directa) y
  `11-aspectos-legales.tex:24` (la proteccion se sustenta en RBAC, red aislada y auditoria).

## 6. Encuadre

Documento de **alineacion** con ISO/IEC 27002:2022 5.34/8.12, ISO/IEC 27701 y la Ley
25.326. No constituye certificacion ni auditoria. La decision documentada es la vigente;
cualquier cambio a cifrado o indice ciego requeriria un change tecnico propio, con su
custodia de claves y su migracion.
