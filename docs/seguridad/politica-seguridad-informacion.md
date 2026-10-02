# Politica de seguridad de la informacion

> **Control mapeado**: ISO/IEC 27002:2022 5.1 (Politicas de seguridad de la informacion);
> NIST CSF 2.0 GV (Govern). Requisito SGD-002.
> **Estado**: v1 — APROBADA por el autor el 2026-10-01 (governance MEDIO).
> **Alcance**: sistema de mesa de ayuda automatizada y sus activos de informacion
> (datos, software y servicios descritos en `inventario-activos-informacion.md`).
> **Encuadre**: el repositorio es un stack de desarrollo local (`docker-compose.yml`,
> `name: mesa_local`). Esta politica esta **alineada con** los marcos citados; **no
> constituye certificacion ni auditoria**. Los controles organizacionales (6.x) y fisicos
> (7.x) competen a la organizacion adoptante (O).

## 1. Proposito

Establecer los principios, el alcance y las responsabilidades de seguridad de la
informacion del sistema, de modo que el tratamiento de datos personales y operativos se
realice con medidas tecnicas y organizativas proporcionales al riesgo, en **alineacion
con** ISO/IEC 27002:2022 5.1 y la funcion NIST CSF 2.0 GV. La politica es el documento
raiz del que dependen la clasificacion de la informacion, los roles de seguridad, la
gestion de incidentes, el inventario de activos y el registro de requisitos legales.

## 2. Alcance

Aplica al sistema de mesa de ayuda automatizada y a todos los activos de informacion que
trata (ver `inventario-activos-informacion.md`):

- Datos: incidentes (descripcion original cifrada + descripcion pseudonimizada), directorio
  de empleados, catalogos y logs.
- Software: backend FastAPI, frontend React, workflow N8N, base PostgreSQL, cache Redis.
- Servicios de terceros: Google Gemini, Twilio, Microsoft Outlook.
- Repositorio de codigo y su automatizacion (CI, hooks).

Fuera de alcance: el entorno productivo de una organizacion adoptante (no declarado), la
infraestructura de hosting, los endpoints de los operadores y los controles fisicos. Estos
competen a la **organizacion adoptante (O)**.

## 3. Principios de seguridad

1. **Minimizacion de datos.** Solo se recogen y tratan los datos necesarios para la
   finalidad declarada; el directorio se limita a los campos operativos.
2. **Defensa en profundidad.** Controles en capas: pseudonimizacion, cifrado at-rest,
   higiene de secretos, TLS en el borde, contenedores sin privilegios de root y guarda de
   costo con fail-closed.
3. **Frontera de datos personales.** Hacia terceros de inferencia y orquestacion solo
   cruza la descripcion pseudonimizada; la descripcion original permanece cifrada y no se
   expone por API.
4. **Revision humana.** Ninguna clasificacion automatizada con confianza menor a 0,70 es
   definitiva sin revision humana; toda decision es trazable.
5. **Menor privilegio.** El acceso a datos y funciones se otorga por rol y sector, segun la
   matriz de `roles-responsabilidades-seguridad.md`.
6. **Higiene de secretos.** Los valores reales viven solo en `.env` gitignorado; el hook
   pre-commit, gitleaks y la push protection de GitHub son defensas en profundidad
   (`docs/security-hardening.md`).
7. **Alineacion, no certificacion.** El sistema se declara **alineado con** el marco
   normativo; no se declara en estado de certificacion ni de conformidad.

## 4. Responsabilidades de aprobacion, comunicacion y revision

Los roles de seguridad se definen como **FUNCIONES de la organizacion adoptante** en
`roles-responsabilidades-seguridad.md`; no se nombran personas en el repositorio.

| Actividad | Funcion responsable | Periodicidad |
|-----------|---------------------|--------------|
| Aprobacion de la politica | Responsable de seguridad de la informacion | Inicial y ante cambio mayor |
| Comunicacion a los participantes | Responsable de seguridad de la informacion | Tras aprobacion y ante cambio |
| Revision de vigencia y alcance | Responsable de seguridad de la informacion | Anual o ante cambio de alcance/normativa |
| Revision de la dimension de privacidad | Responsable de proteccion de datos (DPO) | Anual |
| Registro de la aprobacion | Responsable de seguridad de la informacion | Por cada version |

Esta politica fue **aprobada como v1 por el autor el 2026-10-01**. La designacion nominal de
estas funciones queda a cargo de la organizacion adoptante. Durante la tesis el sistema
opera como piloto (T1) bajo consentimiento documentado del propio grupo.

## 5. Cumplimiento y excepciones

- Se **alinea con** ISO/IEC 27002:2022 5.1, con la funcion NIST CSF 2.0 GV y con la Ley
  25.326 (arts. 9 y 10: seguridad y confidencialidad).
- Las desviaciones respecto de esta politica deben registrarse como excepcion con su
  justificacion, aprobacion y plazo de revision.
- La verificacion del cumplimiento documental es manual en C-61; el doc-lint automatizado
  es un change futuro.

## 6. Encuadre

El repositorio es un **stack de desarrollo local**; varios controles de produccion no
aplican todavia. Los controles organizacionales y fisicos (temas 6.x y 7.x) **no se
implementan en el repositorio**: se documentan como responsabilidad de la organizacion
adoptante. Este documento es de **alineacion** y no constituye certificacion ni auditoria
formal.
