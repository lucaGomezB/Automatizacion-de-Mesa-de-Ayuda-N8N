# Evaluacion de seguridad de proveedores

| Campo | Contenido |
|-------|-----------|
| Control mapeado | ISO/IEC 27002:2022 5.19 (seguridad en relaciones con proveedores), 5.20 (acuerdos con proveedores), 5.21 (cadena de suministro TIC), 5.22 (monitoreo de servicios de proveedores) y 5.23 (seguridad en uso de servicios en la nube); NIST CSF 2.0 GV. Requisito SGD-016 del change `c-64-vulnerabilidades-supply-chain` |
| Estado | v1 — aprobada por el autor el 2026-10-19 (governance MEDIO) |
| Alcance | Postura de seguridad observable publicamente y clausulas a evaluar de los proveedores del sistema (Twilio, Gemini/Google, Microsoft, N8N). No suscribe contratos ni clausulas; no cubre la operacion tecnica de hardening |
| Encuadre | Stack de desarrollo local (`docker-compose.yml`, `name: mesa_local`). Las garantias contractuales competen a la organizacion adoptante (O) |
| Aviso de lenguaje | Alineado con ISO/IEC 27002:2022 5.19-5.23. No constituye certificacion ni auditoria |

> **Encuadre de no-suscripcion.** Este documento **describe el mecanismo de evaluacion** que
> la organizacion adoptante debe completar para cada proveedor. **No implica que exista un
> acuerdo suscrito, vigente ni en vigor**: la suscripcion de acuerdos de procesamiento de
> datos, clausulas de seguridad y niveles de servicio es una **accion organizacional de la
> organizacion adoptante**, fuera del alcance del repositorio. No debe leerse este documento
> como un contrato suscrito.

> **Postura observable frente a garantia.** La columna "postura observable publicamente"
> registra lo que puede verificarse en fuentes publicas del proveedor (centros de confianza,
> documentacion, avisos). Las **declaraciones publicas del proveedor sobre sus propias
> certificaciones NO estan verificadas por este repositorio** y no equivalen a una garantia
> contractual. La columna "clausulas a evaluar" registra lo que la organizacion adoptante
> debe negociar y suscribir; mientras no este suscrito, queda **pendiente**.

## 1. Proposito

Dejar un registro estructurado de la evaluacion de seguridad de los proveedores de servicios
del sistema, separando los **controles mapeados a** ISO/IEC 27002:2022 5.19-5.23 que son
observables publicamente de las **clausulas y garantias contractuales** que la organizacion
adoptante debe evaluar y suscribir. El documento es el punto de trazabilidad de los controles
5.19 a 5.23 en el mapa de `docs/seguridad/README.md`.

## 2. Estructura comun de analisis

Cada proveedor se analiza con el mismo formato:

- **Rol en el sistema**: que servicio presta y que datos trata.
- **Postura observable publicamente**: controles verificables en fuentes publicas del
  proveedor (cifrado en transito, gestion de identidades, certificaciones **declaradas** por
  el proveedor, canal de reporte de vulnerabilidades).
- **Clausulas y garantias a evaluar**: condiciones contractuales que la organizacion
  adoptante debe negociar y suscribir. **Toda clausula no suscrita queda como accion
  pendiente del adoptante.**

## 3. Twilio

- **Rol en el sistema**: telefonia. Graba el audio crudo de la llamada y envia notificaciones
  por SMS; trata el audio crudo y el numero telefonico del llamante antes de la
  pseudonimizacion (`docs/seguridad/instrumento-transferencia-internacional.md` §1-§2).
- **Postura observable publicamente**: cifrado en transito (TLS) en los endpoints de voz y
  mensajeria; gestion de identidades y autenticacion de API con tokens por cuenta; avisos de
  seguridad y canal de reporte de vulnerabilidades publicados por el proveedor; certificaciones
  **declaradas** por el proveedor en su centro de confianza (entre ellas SOC 2 e ISO/IEC
  27001). Estas declaraciones son postura del proveedor, no verificacion de este repositorio.
- **Clausulas y garantias a evaluar**:

| Clausula o garantia | Estado | Accion del adoptante |
|---------------------|--------|----------------------|
| Acuerdo de procesamiento de datos (DPA) con clausulas de seguridad | No suscrita | Negociar y suscribir el DPA |
| Notificacion de brechas con plazo definido | No suscrita | Acordar plazo y canal de notificacion |
| Retencion y borrado de grabaciones de audio crudo | No suscrita | Definir retencion y borrado |
| Clausulas contractuales modelo para la transferencia internacional | No suscrita | Suscribir el instrumento (ver SGD-014) |
| Nivel de servicio (SLA) y soporte de incidentes de seguridad | No suscrita | Acordar SLA y escalamiento |

## 4. Gemini / Google

- **Rol en el sistema**: clasificacion por inferencia de texto (ya pseudonimizado) y
  transcripcion de voz (STT) sobre audio crudo antes de la pseudonimizacion
  (`docs/seguridad/instrumento-transferencia-internacional.md` §1-§2).
- **Postura observable publicamente**: cifrado en transito y en reposo en la plataforma de
  nube; gestion de identidades con roles de IAM; documentacion publica de tratamiento de
  datos y de subencargados; canal de reporte de vulnerabilidades; certificaciones
  **declaradas** por el proveedor (entre ellas ISO/IEC 27001, ISO/IEC 27017, ISO/IEC 27018,
  SOC 1/2/3). Son declaraciones del proveedor, no verificacion de este repositorio.
- **Clausulas y garantias a evaluar**:

| Clausula o garantia | Estado | Accion del adoptante |
|---------------------|--------|----------------------|
| Acuerdo de procesamiento de datos en la nube (DPA) | No suscrita | Negociar y suscribir el DPA |
| Compromiso de no uso de los datos para entrenamiento de modelos | No suscrita | Acordar por contrato el no uso |
| Retencion y borrado de prompts y de audio de voz | No suscrita | Definir retencion y borrado |
| Notificacion de brechas con plazo definido | No suscrita | Acordar plazo y canal de notificacion |
| Clausulas contractuales modelo para la transferencia internacional | No suscrita | Suscribir el instrumento (ver SGD-014) |

## 5. Microsoft

- **Rol en el sistema**: identidad y correo. Proveedor del canal de correo de entrada
  (Outlook y Microsoft Graph) y de la identidad asociada en el flujo original de N8N. El
  canal de correo fue migrado a IMAP/SMTP en C-55; el vinculo con Microsoft quedo inactivo en
  la operacion actual y esta seccion se mantiene como registro de evaluacion.
- **Postura observable publicamente**: cifrado en transito y en reposo; gestion de
  identidades y acceso condicional; centro de confianza y canal de reporte de
  vulnerabilidades publicados; certificaciones **declaradas** por el proveedor (entre ellas
  ISO/IEC 27001, ISO/IEC 27017, ISO/IEC 27018, SOC 1/2/3). Son declaraciones del proveedor,
  no verificacion de este repositorio.
- **Clausulas y garantias a evaluar**:

| Clausula o garantia | Estado | Accion del adoptante |
|---------------------|--------|----------------------|
| Acuerdo de procesamiento de datos (DPA) | No suscrita | Negociar y suscribir el DPA |
| Clausulas de seguridad y de confidencialidad del servicio | No suscrita | Negociar y suscribir |
| Retencion y borrado de buzones y registros tratados | No suscrita | Definir retencion y borrado |
| Notificacion de brechas con plazo definido | No suscrita | Acordar plazo y canal de notificacion |
| Clausulas contractuales modelo para la transferencia internacional | No suscrita | Suscribir el instrumento (ver SGD-014) |

## 6. N8N

- **Rol en el sistema**: orquestacion de flujos. Recibe handoffs HTTP del backend con texto
  pseudonimizado y ejecuta los nodos del workflow (`App/Backend/app/utils/n8n_webhook.py`,
  `n8n/workflow.json`). En el stack local corre **auto-alojado** desde la imagen publicada
  `n8nio/n8n`.
- **Postura observable publicamente**: proyecto de codigo abierto con avisos de seguridad y
  canal de reporte de vulnerabilidades publicados; imagenes publicadas con procedencia en el
  registro de contenedores; documentacion de seguridad de la plataforma. Al ser auto-alojado,
  el proveedor no opera los datos del sistema: la operacion del servicio es del adoptante.
- **Clausulas y garantias a evaluar**:

| Clausula o garantia | Estado | Accion del adoptante |
|---------------------|--------|----------------------|
| Relacion contractual con el proveedor del servicio | No aplica (auto-alojado) | Si se adoptara N8N Cloud, negociar y suscribir DPA |
| Verificacion de procedencia y firma de la imagen usada | Pendiente | Fijar la version, verificar la procedencia y evaluar digest |
| Responsabilidad por la operacion del servicio | Pendiente | Asumida por el adoptante en el auto-alojamiento |
| Aplicacion de parches y actualizaciones de la imagen | Pendiente | Definir la politica de actualizacion del adoptante |
| Notificacion de vulnerabilidades de la imagen | Pendiente | Seguir los avisos del proyecto y evaluar el impacto |

## 7. Clausulas y garantias no suscritas (accion pendiente)

Ninguna de las clausulas y garantias listadas en §3 a §6 esta **suscrita**. Todas quedan como
**accion pendiente de la organizacion adoptante**:

- Suscripcion de los acuerdos de procesamiento de datos de Twilio, Google y Microsoft, y (si
  correspondiera) de N8N Cloud.
- Suscripcion de las clausulas contractuales modelo de transferencia internacional, alineada
  con `docs/seguridad/instrumento-transferencia-internacional.md` y SGD-014.
- Definicion de plazos de notificacion de brechas, retencion y borrado de datos por proveedor.
- Definicion de un proceso de monitoreo de cambios y avisos de seguridad de los proveedores
  (control 5.22), que hoy no existe.

La postura observable publicamente **informa** la evaluacion, pero **no sustituye** la
suscripcion contractual ni constituye una garantia en vigor.

## 8. Encuadre y aviso de lenguaje

Este documento esta **alineado con** ISO/IEC 27002:2022 5.19-5.23 y NIST CSF 2.0 GV.
**Controles mapeados a** los marcos citados. No constituye certificacion ni auditoria, y
**no afirma** que el sistema, el repositorio ni los proveedores esten en estado de
certificacion ni declaren conformidad. El estado actual de las brechas vive en
`docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` (5.19-5.23).

## 9. Fuentes internas

- `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` (brechas 5.19-5.23).
- `docs/cumplimiento/plan-cambios-cumplimiento.md` (fila C-64; fase 21).
- `docs/seguridad/instrumento-transferencia-internacional.md` (§1-§2, §6).
- `docs/seguridad/modelado-amenazas-sdlc.md`.
- `docs/seguridad/README.md` (indice y mapa de trazabilidad).
- `App/Backend/app/config/settings.py`, `docker-compose.yml`, `n8n/workflow.json`.
