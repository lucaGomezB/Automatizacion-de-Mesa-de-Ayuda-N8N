# Instrumento de transferencia internacional (documentado, no suscrito)

> **Control mapeado**: ISO/IEC 27002:2022 5.34 (Privacidad y proteccion de PII) y 5.31
> (Requisitos legales y contractuales), en **alineacion con** ISO/IEC 27701 y el articulo 12
> de la Ley 25.326; NIST CSF 2.0 GV. Requisito SGD-014.
> **Estado**: v1 — aprobada por el autor el 2026-10-19 (governance MEDIO).
> **Alcance**: documenta el **mecanismo** de transferencia internacional hacia Gemini
> (incluida la transcripcion de audio CRUDO previa a la pseudonimizacion) y Twilio (audio
> crudo y numero del llamante) a Estados Unidos. **NO** suscribe contratos ni clausulas
> modelo.
> **Encuadre**: stack de desarrollo local; documento **alineado con** los marcos; no es
> certificacion ni auditoria. Documenta el mecanismo; la firma es accion organizacional.

> **Encuadre de no-suscripcion.** Este documento **describe el mecanismo habilitante** que
> la organizacion adoptante debe suscribir para transferir a Estados Unidos. **No implica
> que el instrumento este firmado, vigente ni en vigor**: la suscripcion del consentimiento
> expreso o de las clausulas contractuales modelo es una **accion organizacional de la
> organizacion adoptante**, fuera del alcance del repositorio. No debe leerse este documento
> como un contrato suscrito.

## 1. Hecho que motiva el instrumento

El sistema transfiere datos personales a **dos proveedores con sede en Estados Unidos**:

| Canal | Proveedor | Que cruza a EE. UU. | Cuando |
|-------|-----------|---------------------|--------|
| Clasificacion por inferencia | Google Gemini | Fragmentos de **texto** descriptivos del incidente (ya pseudonimizado) | Despues de la pseudonimizacion |
| Transcripcion de voz (STT) | Google Gemini | **Audio CRUDO** del llamante y los identificadores que contiene | **ANTES** de la pseudonimizacion |
| Telefonia | Twilio | **Audio CRUDO** de la llamada y el **numero telefonico del llamante** | **ANTES** de la pseudonimizacion |

## 2. Orden real del tratamiento (audio crudo antes de pseudonimizar)

El orden real del canal telefonico (`11-aspectos-legales.tex:18`, `gemini_stt.py:22-25`):

1. El llamante deja su solicitud y **Twilio graba el audio**.
2. El **audio crudo** y el **numero telefonico del llamante** se transfieren a la
   infraestructura del proveedor en **Estados Unidos**.
3. El servicio de reconocimiento del habla (**STT de Gemini**) **transcribe** el audio.
4. **Recien despues**, el backend aplica la **pseudonimizacion** sobre el **texto** ya
   transcrito.

Consecuencia central: **el audio crudo y el numero del llamante cruzan a Estados Unidos
antes de cualquier pseudonimizacion**, que opera unicamente sobre el texto y **no sobre el
audio**. La pseudonimizacion no alcanza a este tramo del tratamiento.

## 3. Caracter de pais NO adecuado (art. 12)

- **Estados Unidos no integra la lista argentina de paises con nivel adecuado** (art. 12 de
  la Ley 25.326; Disposicion DNPDP 60/2016 y Resolucion AAIP 34/2019).
- La adecuacion opera en un solo sentido: la Union Europea reconoce a la Argentina como pais
  adecuado (Decision 2003/490/CE, revalidada en enero de 2024), lo que **no** habilita el
  flujo Argentina -> Estados Unidos.
- Por lo tanto, la transferencia a Gemini y Twilio **requiere un instrumento especifico**
  conforme al articulo 12.

## 4. Mecanismos habilitantes

Para transferir a un pais no adecuado se requiere uno de estos instrumentos:

1. **Consentimiento expreso del titular**.
2. **Clausulas contractuales modelo**: Disposicion DNPDP 60/2016 (contratos modelo de cesion
   y de prestacion de servicios) y **Resolucion AAIP 198/2023** (clausulas modelo de la RPID,
   Responsable/Responsable y Responsable/Encargado). Si el contrato difiere del modelo, el
   responsable debe solicitar aprobacion de la AAIP dentro de los 30 dias.
3. **Normas corporativas vinculantes** (Resolucion AAIP 159/2018), para empresas de un mismo
   grupo economico.
4. Las excepciones tasadas del articulo 12 (colaboracion judicial internacional, etc.), **no
   aplicables** a un proveedor de nube o inferencia.

Fuente: `docs/cumplimiento/marco-legal-ar-2026.md` §5 (art. 12; EE. UU. no adecuado;
mecanismos).

## 5. La pseudonimizacion mitiga, no sustituye

- La pseudonimizacion previa **mitiga** el riesgo de fuga y acota los identificadores
  directos que viajan en el **texto**.
- Pero **no sustituye** el instrumento de transferencia internacional: los datos tratados
  siguen siendo datos personales (la pseudonimizacion **no equivale a disociacion**, art. 2),
  y **el audio crudo no se pseudonimiza**.
- El acuerdo de procesamiento de datos que cada proveedor pudiera suscribir **complementa**
  el instrumento, pero **no lo sustituye**.

## 6. Estado del instrumento

- Este documento **documenta el mecanismo**; **no** afirma que el instrumento este suscrito,
  vigente ni en vigor.
- **La suscripcion** (consentimiento expreso o clausulas modelo) es una **accion
  organizacional de la organizacion adoptante**, no una accion del repositorio.
- La inscripcion de bases (arts. 21/24) y la documentacion del instrumento por base se
  entregan como checklist para el adoptante (ver ROPA
  `registro-actividades-tratamiento.md` §7).

## 7. Encuadre

Documento de **alineacion** con ISO/IEC 27002:2022 5.34/5.31, ISO/IEC 27701 y la Ley 25.326.
Describe el mecanismo y el objetivo/norma, no el estado actual de suscripcion. No constituye
certificacion ni auditoria. El estado actual (brechas) vive en
`docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`.
