# Modelado de amenazas y seguridad en el SDLC

> **Control mapeado**: ISO/IEC 27002:2022 8.26 (Requisitos de seguridad de aplicaciones);
> NIST CSF 2.0 GV (Govern) e ID (Identify). Requisito SGD-008.
> **Estado**: v1 — aprobada por el autor el 2026-10-01 (governance MEDIO).
> **Alcance**: modelado de amenazas y requisitos de seguridad por change en el SDLC OPSX.
> **Encuadre**: stack de desarrollo local; documento **alineado con** los marcos; no es
> certificacion ni auditoria. Las amenazas se mapean a controles o changes **sin declararlos
> implementados**.

## 1. Proposito

Describir el metodo de modelado de amenazas adoptado, definir los requisitos de seguridad
que cada change debe considerar en el ciclo OPSX (incluido un criterio de verificacion de
seguridad previo al cierre) y mapear las amenazas a los controles o changes que las
abordan.

## 2. Metodo: STRIDE

Se adopta **STRIDE** como metodo de modelado de amenazas, aplicado sobre los flujos del
sistema (entrada por correo/web/telefonia -> N8N -> API FastAPI -> clasificador ->
PostgreSQL -> notificacion). Categorias:

| Categoria STRIDE | Pregunta |
|------------------|----------|
| Spoofing | Se puede suplantar una identidad (usuario, servicio, proveedor)? |
| Tampering | Se puede alterar un dato o una configuracion en transito/reposo? |
| Repudiation | Se puede negar una accion sin trazabilidad? |
| Information disclosure | Se puede filtrar PII o material de clave? |
| Denial of service | Se puede degradar o bloquear el servicio? |
| Elevation of privilege | Se puede escalar de rol o acceder a datos de otro sector? |

## 3. Requisitos de seguridad por change (gate SDLC)

Todo change de tipo (T) o mixto debe, antes del cierre:

1. Identificar las amenazas STRIDE aplicables a su alcance.
2. Mapear cada amenaza a un control (ISO 27002) o a un change que la aborde.
3. Declarar explicitamente que **no** se declara implementado ningun control que no tenga
   evidencia en codigo/configuracion.
4. Registrar el resultado en su `design.md` o en este documento (seccion 4).
5. Pasar el criterio de verificacion de seguridad previo al cierre (revision del change).

La seguridad es una **puerta de calidad** del SDLC (control mapeado a ISO 5.8), en
**alineacion con** el flujo SDD/OPSX y la CI existente.

## 4. Mapeo de amenazas a controles o changes

| Amenaza (STRIDE) | Escenario | Control ISO | Change que la aborda |
|------------------|-----------|-------------|----------------------|
| Information disclosure | Numero llamante crudo en logs (`cost_guard/guard.py`) | 5.34, 8.12, 8.15 | C-66 |
| Information disclosure | Contacto del directorio en texto plano (`models/empleado.py`) | 5.34, 8.12 | C-66 |
| Information disclosure | Servicios internos publicados al host (Redis 6379, PostgreSQL 5433, N8N 5678) | 8.20, 8.22 | C-62 |
| Spoofing | Sin MFA ni politica de contrasenas; JWT HS256 sin revocacion | 8.5, 5.15, 5.17 | C-63 |
| Tampering / Elevation | Claves en `.env` sin KMS ni rotacion | 8.24, 8.2 | C-63 |
| Denial of service | Dependencias sin control de CVE; sin SBOM/SAST | 8.8, 8.28, 8.29 | C-64 |
| Denial of service / Repudiation | Backup en claro, sin offsite ni prueba de restauracion | 8.13, 5.29, 5.30 | C-65 |
| Information disclosure | Transferencia a EE. UU. sin instrumento (Gemini, Twilio) | 5.34, 5.31 | C-66 |
| Repudiation | Sin retencion ni integridad de logs de seguridad | 5.28, 8.15 | C-64 / C-66 |
| Spoofing | Sin hardening de red ni separacion de entornos | 8.22, 8.31 | C-62 |

Ninguna de las mitigaciones anteriores se declara **implementada** por C-61: C-61 documenta
el marco; C-62 a C-67 son los changes que las abordan.

## 5. Criterio de verificacion previo al cierre

Un change no se cierra sin: (a) amenazas STRIDE identificadas, (b) mapeo a control o change,
(c) declaracion de lo no implementado, y (d) registro de la decision de seguridad. En C-61
mismo, la verificacion es **manual** (checklist + `openspec validate --strict`); el doc-lint
automatizado es un change futuro.

## 6. Encuadre

Documento de **alineacion** con ISO/IEC 27002:2022 8.26 y NIST CSF 2.0 GV/ID. No constituye
certificacion ni auditoria.
