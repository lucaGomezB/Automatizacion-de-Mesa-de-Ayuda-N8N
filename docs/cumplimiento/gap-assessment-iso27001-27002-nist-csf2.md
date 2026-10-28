# Evaluacion de brechas frente a ISO/IEC 27001:2022, ISO/IEC 27002:2022 y NIST CSF 2.0

Proyecto: Automatizacion de Mesa de Ayuda N8N (tesis UTN-FRM 2026)
Fecha del assessment: 2026-10-01
Tipo de documento: evaluacion de brechas (gap assessment), solo lectura sobre el repositorio.
Alcance normativo: ISO/IEC 27001:2022 (sistema de gestion), ISO/IEC 27002:2022 (controles del Anexo A) y NIST Cybersecurity Framework 2.0 (funciones GV, ID, PR, DE, RS, RC).

Aviso de lenguaje: este documento identifica controles **alineados con** el marco normativo y **brechas identificadas**. NO constituye una certificacion, una declaracion de conformidad ni una auditoria formal. El sistema NO se declara "certificado" ni "cumple ISO/NIST": se declara su grado de alineacion actual y lo que falta.

Nota de reconciliacion: el cuerpo de las secciones 3 y 4 conserva el texto del snapshot 2026-10-01 con anotaciones de cierre en sitio. Las afirmaciones sobre respaldo y continuidad (resumen ejecutivo §2.3, controles 5.29, 5.30, 5.33, 8.13, 8.14 y la funcion NIST RC) fueron reconciliadas con el cierre de C-65 (`c-65-backup-continuidad`, 2026-10-19), que automatiza el respaldo, lo cifra en reposo, agrega una prueba de restauracion reproducible y documenta el plan de continuidad con RTO/RPO. La reconciliacion completa de los change C-61 a C-67 y de c-153 vive en la seccion "2.4 Registro de estado vigente"; esa seccion es la fuente de verdad del estado actual y prevalece sobre cualquier afirmacion de ausencia del cuerpo principal, que se conserva como registro historico del snapshot 2026-10-01.

---

## 1. Alcance y metodo

### 1.1 Que se reviso

Se inspecciono el estado actual del codigo, la configuracion de despliegue local, la automatizacion de seguridad y la documentacion del repositorio `Automatizacion-de-Mesa-de-Ayuda-N8N`. La revision fue estatica y de solo lectura (sin ejecutar la aplicacion, sin pruebas de penetracion, sin acceso a la infraestructura de produccion, sin consultar bases de vulnerabilidades).

Areas cubiertas:

- Backend `App/Backend/app/`: capa de seguridad (`core/security.py`), autenticacion (`services/auth_service.py`, `routes/auth.py`), logging (`core/logging.py`), manejo de errores (`core/error_handlers.py`), configuracion (`config/settings.py`), cifrado y pseudonimizacion (`utils/encryption.py`, `utils/pseudonymizer.py`, `utils/contactos.py`), modelos (`models/`), guarda de costo (`cost_guard/`), rutas y control de acceso (`routes/`), directorio de empleados (`services/directorio_service.py`).
- Frontend `App/Frontend/`: gestion del token JWT (`src/contexts/AuthContext.tsx`), cliente HTTP (`src/services/api.ts`), build y contenedor.
- Operacion: `docker-compose.yml`, `nginx/nginx.conf`, `App/Backend/Dockerfile`, `App/Frontend/Dockerfile`, `Makefile`, `scripts/` (backup y `scripts/security/`), `.githooks/pre-commit`, `.github/workflows/ci.yml`, `.gitleaks.toml`, `.env.example` (raiz y backend).
- Documentacion y contexto: `README.md`, `AGENTS.md`, `docs/` (incluye `security-hardening.md`, `operational-guide.md`, `troubleshooting.md`, `por_implementar.md`, `pseudonymization.md`), `knowledge-base/`, `openspec/specs/`.

### 1.2 Que NO se reviso

- El entorno de produccion real (no existe un despliegue productivo declarado; el stack es de desarrollo local, `docker-compose.yml` con `name: mesa_local`).
- Infraestructura de hosting, red fisica, endpoints de los operadores y controles fisicos.
- Procesos organizacionales de RRHH, formacion, sanciones y acuerdos de confidencialidad (no hay evidencia en el repositorio).
- La instancia viva de N8N, Twilio, Google Gemini y Microsoft Outlook mas alla de lo que el repositorio declara.
- Bases publicas de CVE y el estado real de parcheo de las imagenes Docker (no se corrio escaneo de vulnerabilidades).
- Acuerdos contractuales con proveedores (no disponibles en el repositorio).

### 1.3 Escala de evaluacion utilizada

- Severidad de la brecha: **Alta** (exposicion directa de datos o servicios, o ausencia total de control critico), **Media** (control parcial o sin evidencia suficiente), **Baja** (mejora recomendable sin exposicion inmediata).
- Esfuerzo de remediacion: **Alto**, **Medio**, **Bajo**.
- Tipo: **Tecnico**, **Documental**, **Organizacional**.

---

## 2. Resumen ejecutivo

### 2.1 Estado general

El sistema presenta un **nivel de alineacion inicial-medio** frente a los marcos. Existe una base tecnica solida en dos areas: (a) tratamiento de datos personales (pseudonimizacion, cifrado at-rest y minimizacion) y (b) ingenieria de software seguro en el ciclo de desarrollo (SDD/OPSX, TDD, CI, higiene de secretos). En contraste, las brechas se concentran en **gobernanza documental de seguridad**, **gestion de identidades y accesos**, **endurecimiento de la red y de los servicios de infraestructura**, **gestion de vulnerabilidades y proveedores** y **continuidad de negocio / respaldo**. La mayor parte del stack es de desarrollo local, por lo que varios controles de produccion no estan implementados ni son exigibles todavia.

### 2.2 Fortalezas verificadas

- Doble representacion del dato con pseudonimizacion determinista y cifrado Fernet de la descripcion original: `App/Backend/app/utils/pseudonymizer.py`, `App/Backend/app/utils/encryption.py`, `App/Backend/app/models/incidente.py:88-92`.
- Frontera de PII hacia la IA y hacia N8N: solo cruza la descripcion pseudonimizada: `App/Backend/app/utils/n8n_webhook.py:113-198`, `openspec/specs/data-pseudonymization/spec.md`.
- Higiene de secretos con defensa en profundidad: hook pre-commit, gitleaks en CI, push protection de GitHub y runbook de rotacion: `.githooks/pre-commit`, `.github/workflows/ci.yml:164-191`, `.gitleaks.toml`, `docs/security-hardening.md`.
- Contenedores sin privilegios de root: `App/Backend/Dockerfile:3-15`, `App/Frontend/Dockerfile:13-21`.
- TLS en el borde con cabeceras de seguridad y redireccion HTTP->HTTPS: `nginx/nginx.conf:56-67`.
- Control de egreso economico (guarda de costo) con fail-closed: `App/Backend/app/cost_guard/`, `App/Backend/app/routes/cost_guard.py`.
- Retencion acotada: poda de ejecuciones N8N a 30 dias (`docker-compose.yml:167-168`, `openspec/specs/n8n-retention/spec.md`) y purga de bajas del directorio a 1 año (`App/Backend/app/services/directorio_service.py:248-282`).
- Ciclo de desarrollo seguro: capas estrictas, pruebas automatizadas, verificacion de sincronia de OpenAPI, escaneo de secretos: `.github/workflows/ci.yml`, `AGENTS.md`.

### 2.3 Brechas criticas (detalle en las secciones 3 y 5)

Estado reconciliado al 2026-10-28. Los cinco bloques del snapshot 2026-10-01 fueron atendidos por los changes C-61 a C-67 y por c-153; se anota el estado vigente y el residual real, que en su mayoria depende de la organizacion adoptante (ver §2.4).

1. Identidad y autenticacion (8.5, 5.15, 5.17): atendida en el repositorio. MFA TOTP con desafio para cuentas privilegiadas (`App/Backend/app/routes/auth.py`), politica de contrasenas y bloqueo por intentos fallidos, rotacion del secreto JWT por keyring (`kid`) y revision de accesos documentada (C-63a/b/c). Residual del adoptante: custodia de claves en KMS/PAM y operacion en produccion.
2. Exposicion de servicios de infraestructura (8.20, 8.22): atendida. Redis fue RETIRADO del stack y su puerto `6379` dejo de publicarse; PostgreSQL y N8N se exponen solo en loopback con segmentacion de red y contrasena (C-62).
3. Gestion de vulnerabilidades y cadena de suministro (8.8, 5.19-5.23): atendida. El job `security-scan` de CI ejecuta bandit (SAST), pip-audit y npm audit; Dependabot esta activo; la evaluacion de seguridad de proveedores esta documentada (C-64). Residual del adoptante: SBOM y clausulas contractuales suscritas.
4. Respaldo y continuidad (8.13, 5.29, 5.30, 5.33): atendida para el alcance del repositorio en C-65. Respaldo automatizado, cifrado en reposo (AES-256) y con prueba de restauracion reproducible; plan de continuidad con RTO/RPO (24 h/24 h). Residual del adoptante: copia offsite y redundancia del PostgreSQL unico.
5. Gobernanza documental (5.1, 5.12, 5.24, 5.26, 5.35): atendida documentalmente. Politica de seguridad, clasificacion y etiquetado, plan de respuesta a incidentes, roles y ROPA vigentes (C-61). Residual del adoptante: revision independiente de seguridad (5.35).

### 2.4 Registro de estado vigente

Registro de reconciliacion al 2026-10-28. Por cada control reconciliado se indica el estado vigente, la evidencia en el repositorio, el residual abierto (si existe) y el change archivado que lo cerro. Este registro es la fuente de verdad del estado actual; las afirmaciones de ausencia que permanezcan en las secciones 3 y 4 describen el snapshot 2026-10-01 y NO el estado vigente.

| Control | Estado vigente | Evidencia | Residual abierto | Change archivado |
|---|---|---|---|---|
| 5.1 Politicas de seguridad de la informacion | Cerrado en el repositorio | `docs/seguridad/politica-seguridad-informacion.md` | Aprobacion y difusion en la organizacion adoptante | C-61 (`2026-10-01-c-61-compliance-gobernanza`) |
| 5.9 Inventario de activos de informacion | Cerrado en el repositorio | `docs/seguridad/inventario-activos-informacion.md` | Inventario de hardware y endpoints de operadores del adoptante | C-61 |
| 5.12 Clasificacion de la informacion | Cerrado en el repositorio | `docs/seguridad/clasificacion-etiquetado-informacion.md` | Ninguno en el repositorio | C-61 |
| 5.15 Control de acceso | Cerrado parcialmente (T) | RBAC, visibilidad por sector y MFA de cuentas privilegiadas (`App/Backend/app/routes/auth.py`) | Revision periodica de accesos como proceso operativo del adoptante | C-63b (`2026-10-08-c-63b-mfa-y-rol-privilegiado`) |
| 5.17 Informacion de autenticacion | Cerrado en el repositorio (T) | bcrypt, politica de contrasenas, bloqueo por intentos y rotacion JWT por `kid` (`docs/seguridad/gestion-secretos-y-rotacion.md`) | Custodia de claves en KMS/PAM del adoptante | C-63a/b/c |
| 5.19 Seguridad en relaciones con proveedores | Cerrado documentalmente (D) | `docs/seguridad/evaluacion-seguridad-proveedores.md` | Clausulas y contratos suscritos con los proveedores por el adoptante | C-64 (`2026-10-19-c-64-vulnerabilidades-supply-chain`) |
| 5.24 Planificacion de gestion de incidentes | Cerrado documentalmente (D) | `docs/seguridad/plan-respuesta-incidentes-seguridad.md` | Operacion del plan en produccion por el adoptante | C-61 |
| 5.28 Recoleccion de evidencia | Cerrado parcialmente (T/D) | Seccion de manejo de evidencia en `docs/seguridad/plan-respuesta-incidentes-seguridad.md` y retencion por clase en `docs/seguridad/politica-retencion-logs.md` | Cadena de custodia formal y preservacion forense completa del adoptante | C-156 (este change) |
| 5.32 Propiedad intelectual | Cerrado documentalmente (D) | `docs/seguridad/inventario-licencias.md` | Verificacion legal definitiva del adoptante | C-156 (este change) |
| 5.34 Privacidad y proteccion de PII | Cerrado en el repositorio (T/D) | Pseudonimizacion + Fernet, cifrado at-rest del contacto del directorio (`adr-001-reversion-dir-005-cifrado-contacto.md`), politica de privacidad en runtime y no-PII en logs | Operacion y bases de licitud del adoptante | C-66 (`2026-10-19-c-66-privacidad-transferencias`), c-153 (`2026-10-28`) |
| 8.5 Autenticacion segura | Cerrado en el repositorio (T) | MFA TOTP con desafio y bloqueo (`App/Backend/app/routes/auth.py`) | Custodia KMS/PAM y operacion en produccion del adoptante | C-63b |
| 8.8 Gestion de vulnerabilidades tecnicas | Cerrado en el repositorio (T) | Job `security-scan` de CI: bandit, pip-audit, npm audit; Dependabot | SBOM y escaneo de imagenes del adoptante | C-64 |
| 8.15 Registro (logging) | Cerrado parcialmente (T/D) | Retencion por clase de registro y no-PII en `docs/seguridad/politica-retencion-logs.md` | Centralizacion de logs y SIEM del adoptante | C-66 |
| 8.20 Seguridad de redes | Cerrado en el repositorio (T) | Redis retirado, puertos en loopback y segmentacion de red (`docker-compose.yml`, C-62) | Proteccion perimetral del entorno productivo del adoptante | C-62 (`2026-10-08-c-62-hardening-infra-red`) |
| 8.24 Uso de criptografia | Cerrado parcialmente (T) | Fernet, TLS, bcrypt, rotacion JWT/Fernet y gestion de secretos (`docs/seguridad/gestion-secretos-y-rotacion.md`) | Gestor de claves KMS/PAM y certificados de CA real del adoptante | C-63c (`2026-10-08-c-63c-rotacion-claves-secretos`) |
| 8.28 Codificacion segura | Cerrado en el repositorio (T) | SAST con bandit en CI (`.github/workflows/ci.yml`) | Revisiones de codigo obligatorias del adoptante | C-64 |

---

## 3. Mapeo ISO/IEC 27002:2022

Nota: la numeracion corresponde a los controles del Anexo A de ISO/IEC 27002:2022. "Estado actual" cita la evidencia localizada. Cuando no hay evidencia se indica "no se encontro evidencia". Los controles claramente no aplicables se agrupan al final.

### 3.1 Tema Organizacional (5.x)

| Control | Tema | Estado actual (evidencia) | Brecha | Severidad | Esfuerzo | Tipo |
|---|---|---|---|---|---|---|
| 5.1 Politicas de seguridad de la informacion | Org. | Politica vigente en `docs/seguridad/politica-seguridad-informacion.md` (C-61) | Cerrado en el repositorio; residual: aprobacion y difusion del adoptante (ver §2.4) | Alta | Medio | Documental |
| 5.2 Roles y responsabilidades de seguridad | Org. | Roles funcionales en `knowledge-base/03_actores_y_roles.md` y roles de seguridad en `docs/seguridad/roles-responsabilidades-seguridad.md` (C-61) | Residual: asignacion formal de responsabilidades por el adoptante | Media | Medio | Organizacional |
| 5.3 Segregacion de funciones | Org. | Disciplina de capas `routes -> services -> repositories` (`AGENTS.md`); rol `administrador_directorio` separado (`App/Backend/app/routes/directorio.py:56-77`) | No hay segregacion de funciones en operacion de infraestructura ni doble control | Baja | Bajo | Organizacional |
| 5.7 Inteligencia de amenazas | Org. | no se encontro evidencia | Ausencia total de fuentes de inteligencia de amenazas | Media | Medio | Organizacional |
| 5.8 Seguridad de la informacion en gestion de proyectos | Org. | Flujo SDD/OPSX, revision y CI (`AGENTS.md`, `openspec/`, `.github/workflows/ci.yml`) | No hay criterios de seguridad como puerta de calidad explicita | Media | Bajo | Documental |
| 5.9 Inventario de activos de informacion | Org. | `docs/seguridad/inventario-activos-informacion.md` (activos de datos, software y servicios; C-61) | Cerrado en el repositorio; residual: inventario de hardware y endpoints del adoptante | Media | Medio | Documental |
| 5.12 Clasificacion de la informacion | Org. | Esquema formal en `docs/seguridad/clasificacion-etiquetado-informacion.md` (C-61) | Cerrado en el repositorio (§2.4) | Alta | Medio | Documental |
| 5.13 Etiquetado de la informacion | Org. | Etiquetado por nivel N1-N4 en `docs/seguridad/clasificacion-etiquetado-informacion.md` (C-61) | Cerrado en el repositorio | Media | Bajo | Documental |
| 5.14 Transferencia de informacion | Org. | Solo texto pseudonimizado cruza hacia N8N/IA (`App/Backend/app/utils/n8n_webhook.py:113-146`); TLS externo en `nginx/nginx.conf:56-62`; HTTP plano interno | Sin acuerdos de transferencia con terceros ni cifrado interno | Media | Medio | Documental |
| 5.15 Control de acceso | Org. | JWT + control por rol (`App/Backend/app/core/security.py`, `App/Backend/app/routes/directorio.py:56-77`, `App/Backend/app/services/incident_visibility.py`) y MFA de cuentas privilegiadas (`routes/auth.py`, C-63b) | Cerrado parcialmente: residual revision periodica de accesos del adoptante (§2.4) | Alta | Alto | Tecnico |
| 5.16 Gestion de identidades | Org. | `User` (`App/Backend/app/models/user.py`) y `Empleado` con `user_id` opcional (`App/Backend/app/models/empleado.py:95-100`) | Sin ciclo de vida formal de altas/bajas de identidad | Media | Medio | Organizacional |
| 5.17 Informacion de autenticacion | Org. | bcrypt para contrasenas (`App/Backend/app/services/auth_service.py:27-56`); politica de contrasenas y bloqueo por intentos; rotacion JWT por `kid` (`docs/seguridad/gestion-secretos-y-rotacion.md`, C-63a/b/c) | Cerrado en el repositorio; residual custodia KMS/PAM del adoptante (§2.4) | Alta | Medio | Tecnico |
| 5.18 Derechos de acceso | Org. | Roles aplicados en capa de rutas y visibilidad por sector (`routes/directorio.py`, `services/incident_visibility.py`) | Sin proceso de aprobacion/revision de derechos | Media | Medio | Organizacional |
| 5.19 Seguridad en relaciones con proveedores | Org. | Proveedores: Twilio, Google Gemini, Microsoft Outlook, N8N (`App/Backend/app/config/settings.py`, `docker-compose.yml`); evaluacion documentada en `docs/seguridad/evaluacion-seguridad-proveedores.md` (C-64) | Cerrado documentalmente; residual clausulas suscritas por el adoptante (§2.4) | Alta | Medio | Documental |
| 5.20 Acuerdos con proveedores | Org. | no se encontro evidencia | Sin clausulas de seguridad/privacidad documentadas | Alta | Medio | Documental |
| 5.21 Cadena de suministro TIC | Org. | Imagenes fijadas (`docker-compose.yml:35,59,120`) | Sin gestion de riesgo de cadena de suministro | Media | Medio | Organizacional |
| 5.22 Monitoreo de servicios de proveedores | Org. | Preflight de costo y Gemini (`scripts/preflight/`) | Sin monitoreo de cambios/incidentes de proveedores | Media | Medio | Organizacional |
| 5.23 Seguridad en uso de servicios en la nube | Org. | Consumo de Gemini y Twilio; sin postura documentada | Sin evaluacion de seguridad de servicios cloud | Media | Medio | Documental |
| 5.24 Planificacion de gestion de incidentes de seguridad | Org. | Plan vigente en `docs/seguridad/plan-respuesta-incidentes-seguridad.md` (C-61) | Cerrado documentalmente; residual operacion en produccion del adoptante (§2.4) | Alta | Medio | Documental |
| 5.25 Evaluacion de eventos de seguridad | Org. | no se encontro evidencia | Sin criterios de triaje de eventos | Media | Bajo | Documental |
| 5.26 Respuesta a incidentes de seguridad | Org. | no se encontro evidencia | Sin procedimiento de respuesta y notificacion | Alta | Medio | Documental |
| 5.27 Aprendizaje de incidentes | Org. | Caso de estudio de filtracion de clave en `docs/security-hardening.md:177-196` | Sin proceso sistematico de lecciones aprendidas | Media | Bajo | Organizacional |
| 5.28 Recoleccion de evidencia | Org. | Logs estructurados a stdout (`App/Backend/app/core/logging.py`); seccion de manejo de evidencia en `docs/seguridad/plan-respuesta-incidentes-seguridad.md` y retencion por clase en `docs/seguridad/politica-retencion-logs.md` (C-156) | Cerrado parcialmente; residual cadena de custodia formal y preservacion forense del adoptante (§2.4) | Media | Medio | Tecnico |
| 5.29 Seguridad durante la disrupcion | Org. | Plan de continuidad con procedimiento de restauracion y encuadre de no-garantia (`docs/seguridad/plan-continuidad.md`); respaldo automatizado y cifrado | Residual: copia offsite y operacion en disrupcion como accion del adoptante | Baja | Bajo | Documental |
| 5.30 Preparacion TIC para continuidad | Org. | Plan de continuidad con RTO/RPO (24 h/24 h) y procedimiento de restauracion (`docs/seguridad/plan-continuidad.md`; CONT-001/CONT-002) | Residual: redundancia del PostgreSQL unico como accion del adoptante; RTO/RPO no medidos en produccion | Baja | Bajo | Documental |
| 5.31 Requisitos legales y contractuales | Org. | Alineacion con Ley 25.326 documentada (`docs/pseudonymization.md`, `docs/por_implementar.md`, tesis seccion 11) | Sin registro de cumplimiento legal sistematico | Media | Medio | Documental |
| 5.32 Propiedad intelectual | Org. | Inventario de dependencias y licencias en `docs/seguridad/inventario-licencias.md` (C-156) | Cerrado documentalmente; residual verificacion legal definitiva del adoptante (§2.4) | Baja | Bajo | Documental |
| 5.33 Proteccion de registros | Org. | Dump cifrado en reposo (AES-256-CBC + pbkdf2) con passphrase de despliegue y rotacion de 7 (`scripts/backup.sh`, BACKUP-005) | Residual: custodia de la passphrase por el adoptante (su perdida inhabilita la restauracion) | Baja | Bajo | Tecnico |
| 5.34 Privacidad y proteccion de PII | Org. | Pseudonimizacion + Fernet (`utils/pseudonymizer.py`, `utils/encryption.py`); contacto del directorio cifrado at-rest con indice ciego (**c-153**, 2026-10-28); politica de privacidad en runtime (`docs/seguridad/politica-privacidad-runtime.md`, C-66); numero de origen como identificador HMAC no reversible en logs (`cost_guard/guard.py`) | Cerrado en el repositorio; residual bases de licitud y operacion del adoptante (§2.4) | Alta | Medio | Mixto |
| 5.35 Revision independiente de seguridad | Org. | no se encontro evidencia | Sin revision independiente | Media | Alto | Organizacional |
| 5.36 Cumplimiento de politicas y normas | Org. | CI ejecuta lint, tests, sincronia OpenAPI y escaneo de secretos (`.github/workflows/ci.yml`) | Sin verificacion de cumplimiento de politicas de seguridad | Media | Medio | Documental |
| 5.37 Procedimientos operativos documentados | Org. | `docs/operational-guide.md`, `docs/troubleshooting.md`, `docs/security-hardening.md`, runbooks de telefonia | Falta procedimientos de seguridad (no solo operativos) | Baja | Bajo | Documental |

### 3.2 Tema Personas (6.x)

| Control | Tema | Estado actual (evidencia) | Brecha | Severidad | Esfuerzo | Tipo |
|---|---|---|---|---|---|---|
| 6.1 Seleccion de personal | Personas | Dato de RRHH fuera de alcance del sistema | No aplicable al codigo; requiere proceso organizacional | Media | Medio | Organizacional |
| 6.3 Concientizacion y formacion | Personas | no se encontro evidencia | Sin programa de concientizacion | Media | Medio | Organizacional |
| 6.5 Responsabilidades tras el cese | Personas | `is_active` y desactivacion/reactivacion de empleado (`models/user.py:45`, `services/directorio_service.py:214-238`) | Sin procedimiento formal de revocacion de accesos al cese | Media | Bajo | Organizacional |
| 6.7 Trabajo remoto | Personas | Desarrollo local con `.env` en disco y tunel ngrok opcional (`docker-compose.yml:231-259`) | Sin politica de trabajo remoto ni controles del endpoint | Media | Medio | Organizacional |
| 6.8 Reporte de eventos de seguridad | Personas | no se encontro evidencia | Sin canal de reporte de incidentes | Media | Bajo | Organizacional |
| 6.2, 6.4, 6.6 | Personas | no se encontro evidencia | No aplicables al repositorio (contratos, sanciones, NDA): competen a la organizacion | Media | N/A | Organizacional |

### 3.3 Tema Fisico (7.x)

| Control | Tema | Estado actual (evidencia) | Brecha | Severidad | Esfuerzo | Tipo |
|---|---|---|---|---|---|---|
| 7.1 - 7.14 | Fisico | Sistema containerizado; se ejecuta en equipos de desarrollo. No hay centro de datos propio declarado | Controles fisicos no aplicables al repositorio; deben cubrirse en el entorno de hosting elegido | N/A | N/A | Organizacional |

Nota: al no existir infraestructura productiva declarada, los 14 controles fisicos se consideran fuera del alcance del assessment y deben evaluarse en la organizacion adoptante o en el proveedor de hosting.

### 3.4 Tema Tecnologico (8.x)

| Control | Tema | Estado actual (evidencia) | Brecha | Severidad | Esfuerzo | Tipo |
|---|---|---|---|---|---|---|
| 8.1 Dispositivos de usuario final | Tec. | no se encontro evidencia | Sin gestion de endpoint de desarrolladores/operadores | Media | Medio | Organizacional |
| 8.2 Derechos de acceso privilegiado | Tec. | Secreto de guarda (`config/settings.py:159-165`), firma Twilio (`cost_guard/twilio_signature.py`), credenciales de BD en `.env` | Sin gestion privilegiada (PAM), sin rotacion, credenciales de BD compartidas | Alta | Alto | Tecnico |
| 8.3 Restriccion de acceso a la informacion | Tec. | Alcance por rol/sector (`services/incident_visibility.py`, `routes/directorio.py`) | Sin control a nivel de fila/columna adicional; `descripcion_original` no expuesta (positivo) | Media | Medio | Tecnico |
| 8.4 Acceso al codigo fuente | Tec. | Repositorio publico en GitHub (intencional para la tesis); sin evidencia de branch protection ni firma de commits | Sin controles de rama ni revision obligatoria documentada | Media | Bajo | Tecnico |
| 8.5 Autenticacion segura | Tec. | bcrypt + JWT HS256 (`core/security.py`, `services/auth_service.py`); MFA TOTP con desafio para cuentas privilegiadas y bloqueo por intentos (`routes/auth.py`, C-63b); token en memoria en frontend (`AuthContext.tsx:56-93`) | Cerrado en el repositorio; residual custodia KMS/PAM del adoptante (§2.4) | Alta | Alto | Tecnico |
| 8.6 Gestion de capacidad | Tec. | Pool de BD configurable (`config/settings.py:62-64`); tope de costo (`cost_guard/`) | Sin monitoreo de capacidad de infraestructura | Baja | Bajo | Tecnico |
| 8.7 Proteccion contra malware | Tec. | no se encontro evidencia | Sin escaneo de imagenes/artefactos | Media | Medio | Tecnico |
| 8.8 Gestion de vulnerabilidades tecnicas | Tec. | Job `security-scan` de CI: bandit (SAST), pip-audit y npm audit; Dependabot; dependencias con cotas de major (`App/Backend/requirements.txt`, C-64) | Cerrado en el repositorio; residual SBOM y escaneo de imagenes del adoptante (§2.4) | Alta | Medio | Tecnico |
| 8.9 Gestion de configuracion | Tec. | `.env.example`, compose versionado, imagen N8N fijada (`docker-compose.yml:120`) | Sin linea base endurecida ni verificacion de deriva (drift) | Media | Medio | Tecnico |
| 8.10 Borrado de informacion | Tec. | Purga directorio (1 año), poda N8N (30 dias); incidentes con conservacion indefinida por decision (`docs/por_implementar.md:99-101`) | Sin borrado cifrado ni politica documentada de supresion de incidentes | Media | Medio | Documental |
| 8.11 Enmascaramiento de datos | Tec. | Pseudonimizacion determinista (`utils/pseudonymizer.py`) | Cobertura regex documentada con limites (`docs/pseudonymization.md`) | Baja | Bajo | Tecnico |
| 8.12 Prevencion de fuga de informacion | Tec. | Frontera de PII hacia IA/N8N (`n8n_webhook.py:113-146`) | Numero de origen crudo en logs (`cost_guard/guard.py:236,252`); contacto de directorio en texto plano (**resuelto por `c-153`**: cifrado at-rest + indice ciego, 2026-10-28) | Alta | Medio | Tecnico |
| 8.13 Respaldo de informacion | Tec. | Backup automatizado versionado (`scripts/backup-schedule.cron`), cifrado en reposo, rotacion 7 y prueba de restauracion (`scripts/backup-restore-test.sh`); `backups/` con dumps reales del 2026-10-09 excluidos de git (BACKUP-005..008) | Residual: copia offsite como accion del adoptante (no provista por el repositorio) | Baja | Bajo | Tecnico |
| 8.14 Redundancia | Tec. | Stack unico; un solo PostgreSQL (Redis retirado en C-62) | Sin redundancia ni alta disponibilidad; documentada como accion del adoptante (`docs/seguridad/plan-continuidad.md`) | Media | Alto | Tecnico |
| 8.15 Registro (logging) | Tec. | structlog JSON con contexto (`core/logging.py`); retencion por clase de registro y no-PII en `docs/seguridad/politica-retencion-logs.md` (C-66) | Cerrado parcialmente; residual centralizacion y SIEM del adoptante (§2.4) | Media | Medio | Tecnico |
| 8.16 Actividades de monitoreo | Tec. | Endpoints `/health` y `/health/db` (`routes/health.py`); alerta de guarda de costo (`cost_guard/alerts.py`) | Sin deteccion de anomalias ni alertas de seguridad | Alta | Medio | Tecnico |
| 8.17 Sincronizacion de reloj | Tec. | Reloj del host compartido; logica de dia comercial UTC-3 (`utils/business_time.py`) | Sin NTP explicito declarado | Baja | Bajo | Tecnico |
| 8.19 Instalacion de software | Tec. | Imagenes fijadas; N8N pinneado (`docker-compose.yml:120`) | Sin proceso de aprobacion de cambios de software | Baja | Bajo | Organizacional |
| 8.20 Seguridad de redes | Tec. | Nginx TLS (`nginx/nginx.conf`); Redis RETIRADO del stack; puertos internos (PostgreSQL, N8N) en loopback con segmentacion de red y contrasena (`docker-compose.yml`, C-62) | Cerrado en el repositorio; residual proteccion perimetral del adoptante (§2.4) | Alta | Medio | Tecnico |
| 8.21 Seguridad de servicios de red | Tec. | TLS 1.2/1.3 en el borde (`nginx/nginx.conf:25,60`) | HTTP plano interno sin TLS mutuo | Media | Medio | Tecnico |
| 8.22 Segregacion de redes | Tec. | Red Docker unica `mesa_local_default` | Sin segmentacion entre N8N, backend y base de datos | Media | Medio | Tecnico |
| 8.23 Filtrado web | Tec. | no se encontro evidencia | No aplicable en el contexto del sistema | Baja | N/A | Organizacional |
| 8.24 Uso de criptografia | Tec. | Fernet at-rest (`utils/encryption.py`), TLS, bcrypt, HMAC (Twilio, guarda); rotacion del secreto JWT y de la clave Fernet (`docs/seguridad/gestion-secretos-y-rotacion.md`, C-63c) | Cerrado parcialmente; residual KMS/PAM y certificados de CA real del adoptante (§2.4) | Alta | Medio | Tecnico |
| 8.25 Ciclo de vida de desarrollo seguro | Tec. | SDD/OPSX, TDD, CI, `AGENTS.md` | Sin requisitos de seguridad formales en cada change | Media | Bajo | Documental |
| 8.26 Requisitos de seguridad de aplicaciones | Tec. | Especificaciones en `openspec/specs/` (secret-hygiene, data-pseudonymization, tls-docker-compose) | Sin modelado de amenazas ni requisitos de seguridad sistematicos | Media | Medio | Documental |
| 8.27 Arquitectura y principios de ingenieria segura | Tec. | Arquitectura en capas y patrones documentados (`AGENTS.md`, `knowledge-base/08_arquitectura_propuesta.md`) | Sin revision de arquitectura de seguridad formal | Baja | Bajo | Documental |
| 8.28 Codificacion segura | Tec. | SAST con bandit en CI (`-lll`, bloquea severidad alta); `ruff` para estilo (`.github/workflows/ci.yml`, C-64) | Cerrado en el repositorio; residual revisiones obligatorias del adoptante (§2.4) | Media | Bajo | Tecnico |
| 8.29 Pruebas de seguridad | Tec. | Suite unitaria + integracion PostgreSQL (`.github/workflows/ci.yml:72-88`) | Sin DAST ni pruebas de penetracion | Media | Medio | Tecnico |
| 8.31 Separacion de entornos | Tec. | Un solo compose `mesa_local`; flag `environment` (`config/settings.py:50`) | Sin separacion efectiva de desarrollo/pruebas/produccion | Media | Medio | Tecnico |
| 8.32 Gestion de cambios | Tec. | Git + OPSX + CI + revision (`AGENTS.md`, `openspec/`) | Sin control de cambios formal para infraestructura | Baja | Bajo | Documental |
| 8.33 Informacion de prueba | Tec. | Base de datos descartable y servicios mockeados (`AGENTS.md`, `.github/workflows/ci.yml`) | Corpus con PII real fuera de git (positivo); sin dato sintetico obligatorio | Baja | Bajo | Tecnico |
| 8.18, 8.30, 8.34 | Tec. | `8.18` utilidades privilegiadas, `8.30` desarrollo externo y `8.34` proteccion durante pruebas de auditoria: no se encontro evidencia | No aplicables o sin evidencia en el repositorio | Baja | N/A | Organizacional |

---

## 4. Mapeo NIST CSF 2.0

Escala informal de madurez: 0 = inexistente, 1 = inicial/ad hoc, 2 = repetible, 3 = definido y gestionado, 4 = medido y optimizado. La evaluacion es del sistema tal como esta en el repositorio, no de la organizacion. Los valores entre parentesis reflejan el snapshot 2026-10-01; la reconciliacion vigente al 2026-10-28 esta en §2.4.

| Funcion | Subcategoria representativa | Madurez (0-4) | Evidencia / brecha principal |
|---|---|---|---|
| **GV (Gobernar)** | Politicas, roles, evaluacion de riesgo, gestion de proveedores | 2 | Politica de seguridad, roles de seguridad y evaluacion de proveedores vigentes en `docs/seguridad/` (C-61, C-64). Residual: revision independiente (5.35) como accion del adoptante. |
| **ID (Identificar)** | Inventario de activos, clasificacion de datos, evaluacion de riesgos | 2 | Inventario de activos (`inventario-activos-informacion.md`) y clasificacion/etiquetado (`clasificacion-etiquetado-informacion.md`) vigentes (C-61). Residual: SBOM del adoptante. |
| **PR (Proteger)** | Control de acceso, formacion, hardening, criptografia, mantenimiento de datos | 3 | Pseudonimizacion, Fernet, TLS, contenedores no-root, JWT+roles, MFA de cuentas privilegiadas (C-63b), Redis retirado y puertos en loopback (C-62), SAST/auditoria de dependencias (C-64). Residual: KMS/PAM del adoptante. |
| **DE (Detectar)** | Monitoreo continuo, deteccion de eventos adversos | 1 | Logs estructurados (`core/logging.py`) y healthchecks (`routes/health.py`); alerta de costo (`cost_guard/alerts.py`); retencion por clase (`politica-retencion-logs.md`, C-66). Residual: SIEM, deteccion de anomalias y alertas de seguridad del adoptante. Brecha 8.16. |
| **RS (Responder)** | Plan de respuesta, comunicacion, mitigacion | 2 | Plan de respuesta a incidentes vigente (`docs/seguridad/plan-respuesta-incidentes-seguridad.md`, C-61) y manejo de evidencia (5.28, C-156). Residual: operacion en produccion del adoptante. |
| **RC (Recuperar)** | Plan de recuperacion, restauracion, mejoras | 2 | Respaldo automatizado, cifrado en reposo y con prueba de restauracion reproducible; plan de continuidad con RTO/RPO (`docs/seguridad/plan-continuidad.md`). Residual: offsite y redundancia como accion del adoptante. Brechas 5.29-5.30, 8.13-8.14 (parciales). |

Sintesis NIST CSF 2.0: perfil objetivo no definido; perfil actual con mayor fuerza en PR, con RS y RC atendidos documentalmente para el alcance del repositorio y las carencias de produccion (SIEM, redundancia, offsite, revision independiente) como accion del adoptante.

---

## 5. Brechas priorizadas y orden de remediacion

Plan historico del snapshot 2026-10-01, conservado como registro de la priorizacion original. Los bloques 1 a 8 fueron atendidos (total o parcialmente) por los changes C-61 a C-67, c-153 y C-156; el estado vigente y los residuales reales estan en §2.4.

1. **Gestion de identidades y accesos (8.5, 5.15, 5.17, 8.2)**. Severidad Alta. Atendido en el repositorio por C-63a/b/c: MFA para cuentas privilegiadas, politica de contrasenas, bloqueo por intentos y rotacion del secreto JWT. Residual: revision periodica de accesos del adoptante.
2. **Endurecimiento de servicios de infraestructura y red (8.20, 8.22, 8.2)**. Severidad Alta. Atendido por C-62: Redis retirado, puertos en loopback, segmentacion de red.
3. **Gestion de vulnerabilidades y cadena de suministro (8.8, 5.19-5.23)**. Severidad Alta. Atendido por C-64: Dependabot, bandit, pip-audit y npm audit en CI, evaluacion de seguridad de proveedores. Residual: SBOM y clausulas suscritas del adoptante.
4. **Respaldo y continuidad de negocio (8.13, 5.29, 5.30, 5.33, 8.14)**. Cierre tecnico/documental mayormente completado en C-65: cifrado del backup, automatizacion por programador versionado, prueba de restauracion periodica y plan de continuidad con RTO/RPO. Residual como accion del adoptante: copia offsite y redundancia del PostgreSQL unico.
5. **Gobernanza documental de seguridad (5.1, 5.12, 5.24, 5.26, 5.35)**. Severidad Alta. Atendido documentalmente por C-61: politica de seguridad, clasificacion de informacion, roles y responsabilidades, plan de respuesta a incidentes. Residual: revision independiente (5.35) del adoptante.
6. **Privacidad y fuga de PII (5.34, 8.12, 8.15)**. Severidad Alta. Atendido: numero de origen como identificador HMAC no reversible en logs, cifrado at-rest del contacto del directorio (c-153) y retencion de logs documentada (C-66).
7. **Gestion de claves y criptografia (8.24, 5.17)**. Severidad Alta. Atendido en el repositorio por C-63c: procedimiento de rotacion de la clave Fernet y del secreto JWT. Residual: gestor KMS/PAM y certificados de CA real como accion del adoptante.
8. **Monitoreo y deteccion (8.15, 8.16, 5.28)**. Severidad Alta. Retencion de logs y manejo de evidencia documentados (C-66, C-156). Residual: centralizacion/SIEM y alertas de seguridad del adoptante.
9. **Trabajo remoto y endpoints (6.7, 8.1)**, **concientizacion (6.3)** y **desarrollo seguro formal (8.25, 8.26, 8.28, 8.29)**: severidad Media; el desarrollo seguro formal (8.28) quedo atendido por C-64 (SAST); el resto compete al adoptante.

---

## 6. Que es documental vs. tecnico

### 6.1 Brechas documentales (no requieren cambio de codigo)

Listado del snapshot 2026-10-01; se anota el estado vigente (§2.4).

- Politica de seguridad de la informacion (5.1) y roles de seguridad (5.2): cerradas documentalmente en C-61.
- Clasificacion y etiquetado de la informacion (5.12, 5.13): cerradas en C-61.
- Gestion de incidentes de seguridad: planificacion, respuesta y aprendizaje (5.24-5.27): plan vigente en C-61.
- Gestion de proveedores y acuerdos de seguridad (5.19-5.23): evaluacion documentada en C-64; residual clausulas suscritas.
- Continuidad de negocio y objetivos de recuperacion (5.29, 5.30): cerrada para el alcance del repositorio en C-65 (`docs/seguridad/plan-continuidad.md`); residual offsite/redundancia como accion del adoptante.
- Requisitos legales sistematicos (5.31), propiedad intelectual (5.32, `inventario-licencias.md`, C-156) y revision independiente (5.35, residual del adoptante).
- Procedimientos de seguridad operativos y de reporte de eventos (5.37, 6.8).
- Modelado de amenazas y requisitos de seguridad en el ciclo de desarrollo (8.26): cerrado en C-61.

### 6.2 Brechas tecnicas (requieren cambios de codigo o infraestructura)

Listado del snapshot 2026-10-01; se anota el estado vigente (§2.4).

- MFA, politica de contrasenas, bloqueo por intentos y revocacion de token (8.5, 5.15, 5.17): implementados en C-63a/b/c.
- Exposicion de puertos y falta de contrasena en Redis (8.20); segmentacion de red (8.22): resueltas en C-62 (Redis retirado).
- Gestion de vulnerabilidades automatizada y SBOM (8.8); SAST (8.28); DAST/pentest (8.29): SAST y auditoria de dependencias en C-64; resto residual del adoptante.
- Cifrado y automatizacion de backups con restauracion probada (8.13): completado en C-65; redundancia (8.14): pendiente como accion del adoptante.
- PII en logs del guarda de costo (`App/Backend/app/cost_guard/guard.py`) y cifrado del contacto del directorio (`App/Backend/app/models/empleado.py`): resueltos (identificador HMAC en logs; cifrado at-rest con indice ciego via c-153) (8.12, 5.34).
- Gestion de claves y rotacion (8.24): rotacion JWT/Fernet implementada en C-63c; KMS/PAM residual del adoptante.
- Centralizacion de logs y alertas de seguridad (8.15, 8.16): retencion documentada en C-66; centralizacion/SIEM residual del adoptante.
- Separacion efectiva de entornos (8.31): residual del adoptante.

### 6.3 Brechas organizacionales (fuera del repositorio)

- Seleccion de personal, formacion y sanciones (6.1-6.4).
- Responsabilidades tras el cese y revocacion de accesos (6.5).
- Trabajo remoto y gestion de endpoints (6.7, 8.1).
- Procesos de aprobacion y revision de derechos de acceso (5.18).
- Controles fisicos (7.x) en el entorno de hosting.

---

## 7. Limitaciones del assessment

- Revision estatica y de solo lectura: no se ejecuto la aplicacion ni se realizaron pruebas de penetracion, analisis dinamico ni escaneo de vulnerabilidades.
- El sistema evaluado es un stack de desarrollo local (`docker-compose.yml`, `name: mesa_local`). Varios controles de produccion no aplican aun o no pueden verificarse; el assessment refleja el estado del repositorio, no de un entorno productivo.
- No se accedio a la infraestructura de hosting, a los paneles de los proveedores (Twilio, Google, Microsoft, N8N) ni a los contratos; las afirmaciones sobre proveedores se basan solo en lo que el repositorio declara.
- No se consultaron bases de datos de CVE ni el estado real de parcheo de imagenes; la brecha de gestion de vulnerabilidades se evalua por ausencia de herramientas y procesos, no por vulnerabilidades concretas confirmadas.
- Los controles relativos a personas, fisicos y organizacionales competen a la organizacion adoptante; el repositorio solo puede evidenciar su parte tecnica y documental.
- La documentacion de la tesis (por ejemplo `docs/Tesis/`) describe politicas de privacidad, consentimiento y derechos ARCO; esas descripciones NO se consideran control implementado en el sistema salvo que exista evidencia en codigo o configuracion.
- Este documento es una evaluacion de brechas, no una auditoria de certificacion; el lenguaje de "alineado con" y "brecha identificada" es deliberado.
