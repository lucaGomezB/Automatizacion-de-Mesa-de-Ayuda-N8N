# Politica de privacidad en runtime (objetivo/norma)

> **Control mapeado**: ISO/IEC 27002:2022 5.34 (Privacidad y proteccion de PII), en
> **alineacion con** ISO/IEC 27701 y el deber de informacion de la Ley 25.326 art. 6;
> NIST CSF 2.0 GV. Requisito SGD-009.
> **Estado**: v1 — aprobada por el autor el 2026-10-01 (governance MEDIO).
> **Alcance**: informacion al titular, bases de licitud y derechos. Describe el
> **objetivo/norma**, NO el estado actual de implementacion.
> **Encuadre**: stack de desarrollo local; documento **alineado con** los marcos; no es
> certificacion ni auditoria.

> **Nota de alcance (D10).** Este documento fija el objetivo normativo. El **estado actual**
> (brechas, controles presentes/ausentes) vive en
> `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`. No debe leerse este
> documento como diagnostico ni como control ya implementado.

## 1. Informacion al titular (art. 6)

El sistema debe presentar al titular, de forma expresa y clara, antes de tratar sus datos:

- **Finalidad** del tratamiento y **destinatarios** de los datos.
- **Existencia e identidad del responsable** del tratamiento.
- **Caracter obligatorio o facultativo** de las respuestas y **consecuencias** de
  proporcionar o no los datos.
- **Posibilidad de ejercer** los derechos de acceso, rectificacion y supresion.
- Advertencia de que algunas notificaciones **generan respuestas automaticas**.

La exhibicion de esta informacion en sitio visible es objeto de la Resolucion AAIP 14/2018.

## 2. Bases de licitud

| Tratamiento | Datos | Base de licitud |
|-------------|-------|-----------------|
| Gestion de incidentes (usuarios) | Identificadores y descripcion del incidente | art. 5 inc. 2 apartados b)/d) (obligacion legal / relacion laboral/profesional), con deber de informacion |
| Directorio de empleados | Nombre, correo, celular, sector | art. 5 inc. 2 apartado d) (relacion contractual), con deber de informacion |
| Clasificacion automatica | Texto pseudonimizado del incidente | art. 5; con revision humana y trazabilidad |
| **T1 Piloto/desarrollo** | Datos reales del grupo | **Consentimiento informado** del grupo (`acta-consentimiento-t1.md`) |
| **T2 Corpus de investigacion** | Incidentes reales pseudonimizados | Pseudonimizacion (ver §4) |
| **T3 Adoptante futuro** | Datos de produccion de la empresa adoptante | Base y politica propias del adoptante |

## 3. Derechos y plazos legales

- **Acceso (art. 14): 10 dias corridos** desde la intimacion fehaciente. Ejercicio gratuito
  a intervalos no inferiores a seis meses, salvo interes legitimo acreditado.
- **Rectificacion, actualizacion o supresion (art. 16): 5 dias habiles** desde el reclamo o
  desde que se advierte el error. En caso de cesion o transferencia, se notifica la
  correccion al cesionario dentro del quinto dia habil.
- **Derecho de oposicion:** la Ley 25.326 vigente **no enumera un derecho autonomo de
  oposicion** separado; el acronimo "ARCO" proviene de la practica comparada y de los
  proyectos de reforma. No debe atribuirse a la ley vigente un derecho generico de
  oposicion.
- **Decisiones automatizadas:** la Resolucion AAIP 4/2019 fija el criterio de explicabilidad
  para decisiones exclusivamente automatizadas con efecto significativo; el sistema mantiene
  **revision humana** (human-in-the-loop) y **trazabilidad** como salvaguarda.

## 4. Pseudonimizacion y disociacion (art. 2)

- La Ley 25.326 define **"disociacion de datos"** (art. 2) como el tratamiento que impide
  asociar la informacion a una persona determinada o determinable; el art. 11 inc. 3
  apartado e exime de consentimiento la cesion cuando se aplico disociacion.
- La **pseudonimizacion** implementada por el sistema reemplaza los identificadores, pero
  **conserva la posibilidad de reidentificacion** con informacion adicional (el original
  cifrado existe). Por lo tanto, **pseudonimizacion no equivale a disociacion**: los datos
  tratados siguen siendo datos personales a los efectos de la ley.
- Consecuencia: la pseudonimizacion **mitiga** el riesgo de fuga y la transferencia, pero
  **no sustituye** el instrumento de transferencia internacional ni elimina el deber de
  informacion.

## 5. Transferencias internacionales

- Estados Unidos **no** integra la lista argentina de paises con nivel adecuado (art. 12).
- Para transferir a Gemini y Twilio (EE. UU.) se requiere **consentimiento expreso** o
  **clausulas contractuales modelo** (Disposicion DNPDP 60/2016, Resolucion AAIP 198/2023),
  o normas corporativas vinculantes. Ver ROPA `registro-actividades-tratamiento.md` y el
  change C-66.
- La pseudonimizacion previa mitiga, pero no reemplaza el instrumento.

## 6. Encuadre

Documento de **alineacion** con ISO/IEC 27002:2022 5.34, ISO/IEC 27701 y la Ley 25.326.
Describe el **objetivo/norma**, no el estado actual. No constituye certificacion ni
auditoria. La implementacion en runtime (informacion al titular, procedimiento ARCO,
instrumentos de transferencia) esta mapeada a los changes C-66 y C-67.
