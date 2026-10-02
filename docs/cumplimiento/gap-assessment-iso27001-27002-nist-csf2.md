# Evaluacion de brechas frente a ISO/IEC 27001:2022, ISO/IEC 27002:2022 y NIST CSF 2.0

Proyecto: Automatizacion de Mesa de Ayuda N8N (tesis UTN-FRM 2026)
Fecha del assessment: 2026-10-01
Tipo de documento: evaluacion de brechas (gap assessment), solo lectura sobre el repositorio.
Alcance normativo: ISO/IEC 27001:2022 (sistema de gestion), ISO/IEC 27002:2022 (controles del Anexo A) y NIST Cybersecurity Framework 2.0 (funciones GV, ID, PR, DE, RS, RC).

Aviso de lenguaje: este documento identifica controles **alineados con** el marco normativo y **brechas identificadas**. NO constituye una certificacion, una declaracion de conformidad ni una auditoria formal. El sistema NO se declara "certificado" ni "cumple ISO/NIST": se declara su grado de alineacion actual y lo que falta.

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

1. Identidad y autenticacion: sin MFA, sin politica de contrasenas, sin bloqueo por intentos fallidos, JWT HS256 con secreto unico y 24 h de expiracion sin rotacion ni revocacion, sin revision periodica de accesos (`App/Backend/app/core/security.py`, `App/Backend/app/services/auth_service.py`, `App/Backend/app/routes/auth.py`).
2. Exposicion de servicios de infraestructura: Redis sin contrasena publicado en `6379`, PostgreSQL en `5433`, N8N accesible directo en `5678`, red Docker unica sin segmentacion (`docker-compose.yml:47-67`, `118-182`).
3. Gestion de vulnerabilidades y cadena de suministro: sin Dependabot/pip-audit/trivy/SBOM; varias dependencias con pin minimo (`>=`) sin control de CVE; sin evaluacion de seguridad de proveedores (Twilio, Gemini, Microsoft, N8N) (`App/Backend/requirements.txt`, `.github/`).
4. Respaldo y continuidad: backup manual, dump SQL en texto plano con datos de directorio, sin cifrado, sin copia offsite, sin prueba de restauracion ni plan de recuperacion (`scripts/backup.sh`, `backups/` vacio, `docs/por_implementar.md:129-133`).
5. Gobernanza documental: sin politica de seguridad de la informacion, sin clasificacion formal de la informacion, sin plan de respuesta a incidentes de seguridad, sin roles de seguridad ni revision independiente (`docs/`, `knowledge-base/03_actores_y_roles.md`).

---

## 3. Mapeo ISO/IEC 27002:2022

Nota: la numeracion corresponde a los controles del Anexo A de ISO/IEC 27002:2022. "Estado actual" cita la evidencia localizada. Cuando no hay evidencia se indica "no se encontro evidencia". Los controles claramente no aplicables se agrupan al final.

### 3.1 Tema Organizacional (5.x)

| Control | Tema | Estado actual (evidencia) | Brecha | Severidad | Esfuerzo | Tipo |
|---|---|---|---|---|---|---|
| 5.1 Politicas de seguridad de la informacion | Org. | Solo aspectos legales descritos en la tesis y `knowledge-base/`; no hay politica de seguridad vigente en el repositorio | Falta politica formal aprobada y comunicada | Alta | Medio | Documental |
| 5.2 Roles y responsabilidades de seguridad | Org. | Roles funcionales en `knowledge-base/03_actores_y_roles.md`; no hay roles de seguridad (CISO, responsable de datos) ni matriz RACI | Sin asignacion formal de responsabilidades de seguridad | Media | Medio | Organizacional |
| 5.3 Segregacion de funciones | Org. | Disciplina de capas `routes -> services -> repositories` (`AGENTS.md`); rol `administrador_directorio` separado (`App/Backend/app/routes/directorio.py:56-77`) | No hay segregacion de funciones en operacion de infraestructura ni doble control | Baja | Bajo | Organizacional |
| 5.7 Inteligencia de amenazas | Org. | no se encontro evidencia | Ausencia total de fuentes de inteligencia de amenazas | Media | Medio | Organizacional |
| 5.8 Seguridad de la informacion en gestion de proyectos | Org. | Flujo SDD/OPSX, revision y CI (`AGENTS.md`, `openspec/`, `.github/workflows/ci.yml`) | No hay criterios de seguridad como puerta de calidad explicita | Media | Bajo | Documental |
| 5.9 Inventario de activos de informacion | Org. | `knowledge-base/04_modelo_de_datos.md` documenta el modelo; no hay inventario de activos ni SBOM | Falta inventario de activos (hardware, software, datos, servicios) | Media | Medio | Documental |
| 5.12 Clasificacion de la informacion | Org. | Tratamiento implicito de PII (`openspec/specs/data-pseudonymization/spec.md`, `docs/pseudonymization.md`); no hay esquema de clasificacion formal | Falta criterio de clasificacion y etiquetado de datos | Alta | Medio | Documental |
| 5.13 Etiquetado de la informacion | Org. | no se encontro evidencia | Sin etiquetado de informacion | Media | Bajo | Documental |
| 5.14 Transferencia de informacion | Org. | Solo texto pseudonimizado cruza hacia N8N/IA (`App/Backend/app/utils/n8n_webhook.py:113-146`); TLS externo en `nginx/nginx.conf:56-62`; HTTP plano interno | Sin acuerdos de transferencia con terceros ni cifrado interno | Media | Medio | Documental |
| 5.15 Control de acceso | Org. | JWT + control por rol (`App/Backend/app/core/security.py`, `App/Backend/app/routes/directorio.py:56-77`, `App/Backend/app/services/incident_visibility.py`) | Sin MFA, sin revision de accesos, sin minimo privilegio sobre tokens de servicio | Alta | Alto | Tecnico |
| 5.16 Gestion de identidades | Org. | `User` (`App/Backend/app/models/user.py`) y `Empleado` con `user_id` opcional (`App/Backend/app/models/empleado.py:95-100`) | Sin ciclo de vida formal de altas/bajas de identidad | Media | Medio | Organizacional |
| 5.17 Informacion de autenticacion | Org. | bcrypt para contrasenas (`App/Backend/app/services/auth_service.py:27-56`); JWT `exp` obligatorio (`core/security.py:71-76`) | Sin politica de contrasenas, sin rotacion del secreto JWT, token de 24 h sin refresco | Alta | Medio | Tecnico |
| 5.18 Derechos de acceso | Org. | Roles aplicados en capa de rutas y visibilidad por sector (`routes/directorio.py`, `services/incident_visibility.py`) | Sin proceso de aprobacion/revision de derechos | Media | Medio | Organizacional |
| 5.19 Seguridad en relaciones con proveedores | Org. | Proveedores: Twilio, Google Gemini, Microsoft Outlook, N8N (`App/Backend/app/config/settings.py`, `docker-compose.yml`) | Sin evaluacion de seguridad de proveedores | Alta | Medio | Documental |
| 5.20 Acuerdos con proveedores | Org. | no se encontro evidencia | Sin clausulas de seguridad/privacidad documentadas | Alta | Medio | Documental |
| 5.21 Cadena de suministro TIC | Org. | Imagenes fijadas (`docker-compose.yml:35,59,120`) | Sin gestion de riesgo de cadena de suministro | Media | Medio | Organizacional |
| 5.22 Monitoreo de servicios de proveedores | Org. | Preflight de costo y Gemini (`scripts/preflight/`) | Sin monitoreo de cambios/incidentes de proveedores | Media | Medio | Organizacional |
| 5.23 Seguridad en uso de servicios en la nube | Org. | Consumo de Gemini y Twilio; sin postura documentada | Sin evaluacion de seguridad de servicios cloud | Media | Medio | Documental |
| 5.24 Planificacion de gestion de incidentes de seguridad | Org. | `docs/troubleshooting.md` es operativo, no de seguridad; no hay plan de respuesta a incidentes de seguridad | Ausencia de plan de IR de seguridad | Alta | Medio | Documental |
| 5.25 Evaluacion de eventos de seguridad | Org. | no se encontro evidencia | Sin criterios de triaje de eventos | Media | Bajo | Documental |
| 5.26 Respuesta a incidentes de seguridad | Org. | no se encontro evidencia | Sin procedimiento de respuesta y notificacion | Alta | Medio | Documental |
| 5.27 Aprendizaje de incidentes | Org. | Caso de estudio de filtracion de clave en `docs/security-hardening.md:177-196` | Sin proceso sistematico de lecciones aprendidas | Media | Bajo | Organizacional |
| 5.28 Recoleccion de evidencia | Org. | Logs estructurados a stdout (`App/Backend/app/core/logging.py`) | Sin retencion, integridad ni cadena de custodia de evidencia | Media | Medio | Tecnico |
| 5.29 Seguridad durante la disrupcion | Org. | Backups manuales (`scripts/backup.sh`) | Sin procedimientos de operacion en disrupcion | Media | Medio | Documental |
| 5.30 Preparacion TIC para continuidad | Org. | no se encontro evidencia | Sin plan de continuidad ni objetivos de recuperacion (RTO/RPO) | Alta | Alto | Documental |
| 5.31 Requisitos legales y contractuales | Org. | Alineacion con Ley 25.326 documentada (`docs/pseudonymization.md`, `docs/por_implementar.md`, tesis seccion 11) | Sin registro de cumplimiento legal sistematico | Media | Medio | Documental |
| 5.32 Propiedad intelectual | Org. | no se encontro evidencia | Sin inventario de licencias de dependencias | Baja | Bajo | Documental |
| 5.33 Proteccion de registros | Org. | Backup en claro, rotacion 7 dias (`scripts/backup.sh:26,83-98`) | Registros de respaldo sin cifrado ni proteccion | Alta | Medio | Tecnico |
| 5.34 Privacidad y proteccion de PII | Org. | Pseudonimizacion + Fernet (`utils/pseudonymizer.py`, `utils/encryption.py`); retencion directorio/N8N | Contacto del directorio en texto plano (`models/empleado.py:16-18`); sin politica de privacidad en runtime; numero de origen crudo en logs (`cost_guard/guard.py:236,252`) | Alta | Medio | Mixto |
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
| 8.5 Autenticacion segura | Tec. | bcrypt + JWT HS256 (`core/security.py`, `services/auth_service.py`); token en memoria en frontend (`AuthContext.tsx:56-93`) | Sin MFA, sin bloqueo, sin reglas de complejidad; sin revocacion de sesion | Alta | Alto | Tecnico |
| 8.6 Gestion de capacidad | Tec. | Pool de BD configurable (`config/settings.py:62-64`); tope de costo (`cost_guard/`) | Sin monitoreo de capacidad de infraestructura | Baja | Bajo | Tecnico |
| 8.7 Proteccion contra malware | Tec. | no se encontro evidencia | Sin escaneo de imagenes/artefactos | Media | Medio | Tecnico |
| 8.8 Gestion de vulnerabilidades tecnicas | Tec. | Dependencias con pin parcial (`App/Backend/requirements.txt`: `>=` en varias) | Sin Dependabot, pip-audit, trivy ni SBOM; sin SLA de parcheo | Alta | Medio | Tecnico |
| 8.9 Gestion de configuracion | Tec. | `.env.example`, compose versionado, imagen N8N fijada (`docker-compose.yml:120`) | Sin linea base endurecida ni verificacion de deriva (drift) | Media | Medio | Tecnico |
| 8.10 Borrado de informacion | Tec. | Purga directorio (1 año), poda N8N (30 dias); incidentes con conservacion indefinida por decision (`docs/por_implementar.md:99-101`) | Sin borrado cifrado ni politica documentada de supresion de incidentes | Media | Medio | Documental |
| 8.11 Enmascaramiento de datos | Tec. | Pseudonimizacion determinista (`utils/pseudonymizer.py`) | Cobertura regex documentada con limites (`docs/pseudonymization.md`) | Baja | Bajo | Tecnico |
| 8.12 Prevencion de fuga de informacion | Tec. | Frontera de PII hacia IA/N8N (`n8n_webhook.py:113-146`) | Numero de origen crudo en logs (`cost_guard/guard.py:236,252`); contacto de directorio en texto plano | Alta | Medio | Tecnico |
| 8.13 Respaldo de informacion | Tec. | `scripts/backup.sh` / `backup.ps1`, rotacion 7 dias, sin cifrado | Backup manual, en claro, sin offsite ni prueba de restauracion; `backups/` vacio | Alta | Medio | Tecnico |
| 8.14 Redundancia | Tec. | Stack unico; un solo PostgreSQL y un solo Redis (`docker-compose.yml`) | Sin redundancia ni alta disponibilidad | Media | Alto | Tecnico |
| 8.15 Registro (logging) | Tec. | structlog JSON con contexto (`core/logging.py`) | Sin centralizacion, retencion ni control de PII en logs | Media | Medio | Tecnico |
| 8.16 Actividades de monitoreo | Tec. | Endpoints `/health` y `/health/db` (`routes/health.py`); alerta de guarda de costo (`cost_guard/alerts.py`) | Sin deteccion de anomalias ni alertas de seguridad | Alta | Medio | Tecnico |
| 8.17 Sincronizacion de reloj | Tec. | Reloj del host compartido; logica de dia comercial UTC-3 (`utils/business_time.py`) | Sin NTP explicito declarado | Baja | Bajo | Tecnico |
| 8.19 Instalacion de software | Tec. | Imagenes fijadas; N8N pinneado (`docker-compose.yml:120`) | Sin proceso de aprobacion de cambios de software | Baja | Bajo | Organizacional |
| 8.20 Seguridad de redes | Tec. | Nginx TLS (`nginx/nginx.conf`); puertos internos no publicados para backend/frontend | Redis sin contrasena en `6379`, PostgreSQL en `5433`, N8N en `5678` (`docker-compose.yml:47-67,118-182`) | Alta | Medio | Tecnico |
| 8.21 Seguridad de servicios de red | Tec. | TLS 1.2/1.3 en el borde (`nginx/nginx.conf:25,60`) | HTTP plano interno sin TLS mutuo | Media | Medio | Tecnico |
| 8.22 Segregacion de redes | Tec. | Red Docker unica `mesa_local_default` | Sin segmentacion entre N8N, backend y base de datos | Media | Medio | Tecnico |
| 8.23 Filtrado web | Tec. | no se encontro evidencia | No aplicable en el contexto del sistema | Baja | N/A | Organizacional |
| 8.24 Uso de criptografia | Tec. | Fernet at-rest (`utils/encryption.py`), TLS, bcrypt, HMAC (Twilio, guarda) | Gestion de claves debil: claves en `.env`, sin KMS ni rotacion; certificado self-signed en desarrollo (`docs/por_implementar.md:72-80`) | Alta | Medio | Tecnico |
| 8.25 Ciclo de vida de desarrollo seguro | Tec. | SDD/OPSX, TDD, CI, `AGENTS.md` | Sin requisitos de seguridad formales en cada change | Media | Bajo | Documental |
| 8.26 Requisitos de seguridad de aplicaciones | Tec. | Especificaciones en `openspec/specs/` (secret-hygiene, data-pseudonymization, tls-docker-compose) | Sin modelado de amenazas ni requisitos de seguridad sistematicos | Media | Medio | Documental |
| 8.27 Arquitectura y principios de ingenieria segura | Tec. | Arquitectura en capas y patrones documentados (`AGENTS.md`, `knowledge-base/08_arquitectura_propuesta.md`) | Sin revision de arquitectura de seguridad formal | Baja | Bajo | Documental |
| 8.28 Codificacion segura | Tec. | `ruff` limitado a reglas E (`AGENTS.md`) | Sin SAST (bandit/semgrep) en CI | Media | Bajo | Tecnico |
| 8.29 Pruebas de seguridad | Tec. | Suite unitaria + integracion PostgreSQL (`.github/workflows/ci.yml:72-88`) | Sin DAST ni pruebas de penetracion | Media | Medio | Tecnico |
| 8.31 Separacion de entornos | Tec. | Un solo compose `mesa_local`; flag `environment` (`config/settings.py:50`) | Sin separacion efectiva de desarrollo/pruebas/produccion | Media | Medio | Tecnico |
| 8.32 Gestion de cambios | Tec. | Git + OPSX + CI + revision (`AGENTS.md`, `openspec/`) | Sin control de cambios formal para infraestructura | Baja | Bajo | Documental |
| 8.33 Informacion de prueba | Tec. | Base de datos descartable y servicios mockeados (`AGENTS.md`, `.github/workflows/ci.yml`) | Corpus con PII real fuera de git (positivo); sin dato sintetico obligatorio | Baja | Bajo | Tecnico |
| 8.18, 8.30, 8.34 | Tec. | `8.18` utilidades privilegiadas, `8.30` desarrollo externo y `8.34` proteccion durante pruebas de auditoria: no se encontro evidencia | No aplicables o sin evidencia en el repositorio | Baja | N/A | Organizacional |

---

## 4. Mapeo NIST CSF 2.0

Escala informal de madurez: 0 = inexistente, 1 = inicial/ad hoc, 2 = repetible, 3 = definido y gestionado, 4 = medido y optimizado. La evaluacion es del sistema tal como esta en el repositorio, no de la organizacion.

| Funcion | Subcategoria representativa | Madurez (0-4) | Evidencia / brecha principal |
|---|---|---|---|
| **GV (Gobernar)** | Politicas, roles, evaluacion de riesgo, gestion de proveedores | 1 | No hay politica de seguridad, roles de seguridad ni gestion de riesgo formal. Documentacion operativa y legal en `knowledge-base/`, `docs/`. Brechas 5.1, 5.19, 5.24, 5.35. |
| **ID (Identificar)** | Inventario de activos, clasificacion de datos, evaluacion de riesgos | 1 | Modelo de datos documentado (`knowledge-base/04_modelo_de_datos.md`) y specs en `openspec/specs/`, pero sin inventario de activos, clasificacion ni SBOM. Brechas 5.9, 5.12. |
| **PR (Proteger)** | Control de acceso, formacion, hardening, criptografia, mantenimiento de datos | 2 | Fortalezas reales: pseudonimizacion, Fernet, TLS en el borde, contenedores no-root, JWT+roles, higiene de secretos. Debilidades: sin MFA, servicios internos expuestos, claves en `.env`, sin gestion de vulnerabilidades. Brechas 8.5, 8.8, 8.20, 8.24. |
| **DE (Detectar)** | Monitoreo continuo, deteccion de eventos adversos | 1 | Logs estructurados (`core/logging.py`) y healthchecks (`routes/health.py`); alerta de costo (`cost_guard/alerts.py`). Sin SIEM, sin deteccion de anomalias ni alertas de seguridad. Brechas 8.15, 8.16. |
| **RS (Responder)** | Plan de respuesta, comunicacion, mitigacion | 0 | No se encontro plan de respuesta a incidentes de seguridad; `docs/troubleshooting.md` es de resolucion operativa. Brechas 5.24-5.26. |
| **RC (Recuperar)** | Plan de recuperacion, restauracion, mejoras | 1 | Scripts de backup manual (`scripts/backup.sh`) sin cifrado, offsite ni prueba de restauracion; sin RTO/RPO. Brechas 5.29-5.30, 8.13. |

Sintesis NIST CSF 2.0: perfil objetivo no definido (GV e ID en nivel inicial), perfil actual con mayor fuerza en PR y las mayores carencias en RS y RC.

---

## 5. Brechas priorizadas y orden de remediacion

Orden sugerido por relacion riesgo/esfuerzo y dependencias entre brechas.

1. **Gestion de identidades y accesos (8.5, 5.15, 5.17, 8.2)**. Severidad Alta. Cierre tecnico: MFA para cuentas de operacion/administracion, politica de contrasenas, bloqueo por intentos, acortar expiracion del JWT y habilitar rotacion/revocacion, revision periodica de accesos. Depende de la decision de despliegue productivo.
2. **Endurecimiento de servicios de infraestructura y red (8.20, 8.22, 8.2)**. Severidad Alta. Cierre tecnico: quitar publicacion de `5433`/`6379`/`5678` al host, contrasena en Redis, segmentacion de red, restringir la UI de N8N. Esfuerzo bajo-medio y alto impacto.
3. **Gestion de vulnerabilidades y cadena de suministro (8.8, 5.19-5.23)**. Severidad Alta. Cierre tecnico/organizacional: Dependabot o equivalente, pip-audit/npm audit y escaneo de imagenes en CI, SBOM, evaluacion de seguridad y clausulas con Twilio/Gemini/Microsoft/N8N.
4. **Respaldo y continuidad de negocio (8.13, 5.29, 5.30, 5.33, 8.14)**. Severidad Alta. Cierre tecnico/documental: cifrado del backup, copia offsite, automatizacion por cron y prueba de restauracion periodica; definir RTO/RPO y plan de continuidad.
5. **Gobernanza documental de seguridad (5.1, 5.12, 5.24, 5.26, 5.35)**. Severidad Alta. Cierre documental: politica de seguridad, clasificacion de informacion, roles y responsabilidades, plan de respuesta a incidentes, revision independiente.
6. **Privacidad y fuga de PII (5.34, 8.12, 8.15)**. Severidad Alta. Cierre tecnico: eliminar el numero de origen crudo de los logs o seudonimizarlo, evaluar cifrado del contacto del directorio o justificarlo por minimizacion, documentar retencion de logs.
7. **Gestion de claves y criptografia (8.24, 5.17)**. Severidad Alta. Cierre tecnico: gestor de secretos (Vault/SM y de nube), procedimiento de rotacion de la clave Fernet y del secreto JWT, certificados de CA real para produccion.
8. **Monitoreo y deteccion (8.15, 8.16, 5.28)**. Severidad Alta. Cierre tecnico: centralizacion de logs con retencion, alertas de seguridad, base para deteccion.
9. **Trabajo remoto y endpoints (6.7, 8.1)**, **concientizacion (6.3)** y **desarrollo seguro formal (8.25, 8.26, 8.28, 8.29)**: severidad Media; abordables despues de los bloques 1-8.

---

## 6. Que es documental vs. tecnico

### 6.1 Brechas documentales (no requieren cambio de codigo)

- Politica de seguridad de la informacion (5.1) y roles de seguridad (5.2).
- Clasificacion y etiquetado de la informacion (5.12, 5.13).
- Gestion de incidentes de seguridad: planificacion, respuesta y aprendizaje (5.24-5.27).
- Gestion de proveedores y acuerdos de seguridad (5.19-5.23).
- Continuidad de negocio y objetivos de recuperacion (5.29, 5.30).
- Requisitos legales sistematicos (5.31), propiedad intelectual (5.32) y revision independiente (5.35).
- Procedimientos de seguridad operativos y de reporte de eventos (5.37, 6.8).
- Modelado de amenazas y requisitos de seguridad en el ciclo de desarrollo (8.26).

### 6.2 Brechas tecnicas (requieren cambios de codigo o infraestructura)

- MFA, politica de contrasenas, bloqueo por intentos y revocacion de token (8.5, 5.15, 5.17).
- Exposicion de puertos y falta de contrasena en Redis (8.20); segmentacion de red (8.22).
- Gestion de vulnerabilidades automatizada y SBOM (8.8); SAST (8.28); DAST/pentest (8.29).
- Cifrado y automatizacion de backups con restauracion probada (8.13); redundancia (8.14).
- PII en logs del guarda de costo (`App/Backend/app/cost_guard/guard.py:236,252`) y cifrado del contacto del directorio (`App/Backend/app/models/empleado.py:16-18`) (8.12, 5.34).
- Gestion de claves y rotacion (8.24).
- Centralizacion de logs y alertas de seguridad (8.15, 8.16).
- Separacion efectiva de entornos (8.31).

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
