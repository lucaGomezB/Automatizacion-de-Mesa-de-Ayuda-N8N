# Inventario de activos de informacion

> **Control mapeado**: ISO/IEC 27002:2022 5.9 (Inventario de activos de informacion); NIST
> CSF 2.0 ID (Identify). Requisito SGD-006.
> **Estado**: v1 — aprobada por el autor el 2026-10-01 (governance MEDIO).
> **Alcance**: activos de datos, software y servicios del sistema.
> **Encuadre**: stack de desarrollo local; documento **alineado con** los marcos; no es
> certificacion ni auditoria.

## 1. Proposito

Identificar los activos de informacion del sistema y asignar a cada uno un responsable y su
clasificacion, como base de la gestion de riesgos. El inventario **no contiene credenciales
ni secretos**: los valores reales viven en `.env` gitignorado y en los paneles de los
proveedores.

## 2. Activos de datos

| Activo | Descripcion | Responsable (funcion) | Clasificacion |
|--------|-------------|-----------------------|---------------|
| Incidentes — descripcion original | Texto original del incidente, cifrado con Fernet | Responsable de seguridad | N4 Restringido |
| Incidentes — descripcion pseudonimizada | Copia con PII reemplazada, expuesta a terceros | DPO | N3 Confidencial (PII) |
| Directorio de empleados | Nombre, correo, celular, sector, estado | `administrador_directorio` (tecnico) | N3 Confidencial (PII) |
| Catalogos | Estados, sectores y canales de origen | Responsable de seguridad | N1 Publico |
| Logs de aplicacion | Trazas structlog sin PII (objetivo) | Responsable de seguridad | N2 Interno |
| Metricas de la guarda de costo | Contadores y alertas de egreso | Responsable de seguridad | N2 Interno |
| Corpus de evaluacion | Incidentes reales pseudonimizados, fuera de git | DPO | N3 Confidencial (PII) |

## 3. Activos de software

| Activo | Descripcion | Responsable (funcion) | Clasificacion |
|--------|-------------|-----------------------|---------------|
| Backend FastAPI | API de incidentes y clasificacion | Responsable de seguridad | N2 Interno |
| Frontend React | Interfaz web de operacion y revision | Responsable de seguridad | N2 Interno |
| Workflow N8N | Orquestacion de canales (`n8n/workflow.json`) | Responsable de seguridad | N2 Interno |
| PostgreSQL | Base de datos de incidentes, directorio y catalogos | Responsable de seguridad | N4 Restringido |
| Redis | Cache y datos transitorios | Responsable de seguridad | N2 Interno |
| Repositorio de codigo | Codigo fuente y documentacion (publico por decision de tesis) | Responsable de seguridad | N1 Publico |

## 4. Activos de servicio (terceros)

| Activo | Descripcion | Responsable (funcion) | Clasificacion |
|--------|-------------|-----------------------|---------------|
| Google Gemini | Inferencia de clasificacion (recibe texto pseudonimizado) | DPO | N3 Confidencial (PII) |
| Twilio | Telefonia y SMS (numero llamante) | DPO | N3 Confidencial (PII) |
| Microsoft Outlook | Correo entrante (origen de incidentes) | DPO | N3 Confidencial (PII) |
| N8N (instancia) | Ejecucion del workflow autoalojado | Responsable de seguridad | N2 Interno |
| GitHub | Hosting del repositorio y automatizacion CI | Responsable de seguridad | N1 Publico |

## 5. Responsabilidades y encuadre

- Cada activo tiene un **responsable** (funcion) y una **clasificacion**; los controles de
  tratamiento por nivel estan en `clasificacion-etiquetado-informacion.md`.
- Los activos marcados N3/N4 se gestionan segun la politica de seguridad y el ROPA
  (`registro-actividades-tratamiento.md`).
- **Sin secretos**: este inventario no incluye credenciales, claves, tokens ni valores de
  `.env`. La gestion de claves y secretos esta mapeada al change C-63.
- El inventario de hardware y de endpoints de operadores compete a la organizacion
  adoptante (O). Los controles fisicos (tema 7.x) quedan fuera del repositorio.

## 6. Encuadre

Documento de **alineacion** con ISO/IEC 27002:2022 5.9 y NIST CSF 2.0 ID. No constituye
certificacion ni auditoria.
