# CHANGES — Secuencia de Implementacion

> Indice canonico de todos los changes del proyecto **Automatizacion de Mesa de Ayuda N8N**.
> Cada change es atomico: un agente puede implementarlo en una sesion (~4-6 horas).
> **Leer este archivo antes de ejecutar cualquier `/opsx:propose`.**
>
> Fuente: Tesis "Automatizacion inteligente del registro de incidentes en mesas de ayuda
> empresariales mediante orquestacion de flujos con N8N y procesamiento de lenguaje natural
> basado en modelos de lenguaje grandes" (Gomez, Bustos, Sevilla, 2026).

---

## Como usar este documento

1. Identifica el change que quieres implementar en `FASE {N}`.
2. Lee los documentos referenciados en **Leer antes** (tesis + docs/).
3. Ejecuta `/opsx:propose C-{NN}-{kebab-name}` para crear los artefactos OPSX.
4. Implementa el cambio siguiendo las tareas generadas.
5. Una vez completado, ejecuta `/opsx:archive C-{NN}-{kebab-name}`.
6. Marca el change como `[x]` en este documento.

---

## Arbol de dependencias

```
C-01 foundation-setup (ninguna)
 └── C-02 notify-n8n-hook (C-01)
 │    └── C-04 n8n-workflow-validation (C-02)
 │         └── C-05 n8n-channel-triggers (C-04)
 └── C-03 pseudonymization-module (C-01)
 └── C-06 backend-integration-tests (C-02, C-03)
 └── C-07 frontend-testing-setup (C-01)
 ├── C-08 evaluation-framework (C-02, C-03)
 └── C-09 ci-cd-pipeline (C-06, C-07)
      └── C-10 documentation-annexes (C-04, C-05, C-09)

C-11 tesis-correcciones-academicas (ninguna — documento independiente)
  └── C-12 tesis-recomendaciones-coneau (C-11)
       └── C-13 tesis-notas-sentido-comun (C-12)

--- FASE 10: Cierre de brechas tesis/codigo (2026-07-03) ---

C-26 corpus-simulado-backup-retencion (C-17)

--- FASE 11: Rediseno de sectores y corpus JSON multietiqueta (2026-09-11) ---

C-27 rediseno-sectores-json (C-26)

--- FASE 12: Auth, integraciones externas y alineacion de tesis (2026-07-02 / 2026-07-03) ---

C-14 kb-sync-implementation-state (ninguna — KB update)
 └── C-15 jwt-auth-backend-frontend (C-01, C-14)
C-16 twilio-twiml-script (C-05)
C-17 evaluation-corpus-simulado (C-08)
C-18 tesis-alineacion-tecnologica (ninguna)

--- FASE 13: Infra, pruebas de integracion y saneamiento de repositorio (2026-07-03 / 2026-07-10) ---

C-19 integration-tests-postgresql (C-15, C-24)
C-20 tls-docker-compose (ninguna)
C-22 tesis-dashboard-analytics (C-23)
C-23 dashboard-analytics-implementation (C-15, C-24)
C-24 restructure-app-directory (ninguna)
 └── C-25 root-cleanup (C-24)
improve-dockerfiles (sin numero — ninguna)

--- FASE 14: Endurecimiento y pipeline end-to-end (2026-09-17 / 2026-09-18 / 2026-09-20) ---

C-28 bootstrap-un-comando (C-20, C-25)
C-29 seam-tests (C-19, C-27)
 └── C-30 bugfix-seams (C-29)
      ├── C-31 dry-run-harness (C-30)
      ├── C-32 disposable-test-db (C-29, C-30)
      ├── C-33 cost-guards (C-30, C-31, C-32)
      ├── C-35 dashboard-business-day-grouping (C-30, C-32)
      └── C-38 n8n-confidence-gate (C-30, C-33)
C-34 evaluation-prediction-cache (C-08, C-27)
C-36 credentialing-readiness (C-33, C-34)
C-37 secret-hardening (ninguna)
C-39 e2e-timing-instrumentation (C-33, C-32)
 └── C-40 n8n-wiring-fixes (C-39)
C-41 cost-preflight-wiring (C-36)

--- FASE 15: Sincronizacion documental (C-42, C-43, C-44) ---

C-42 bootstrap-docs-sync (C-39, C-40, C-41)
C-43 docs-restructure-sync (C-42)
C-44 docs-evaluation-sync (C-43)

--- FASE 16: Guarda de costo en runtime (2026-09-21) ---

C-45 runtime-cost-guard (C-41, C-33)

--- FASE 17: Fidelidad de medicion del pipeline (2026-09-22) ---

C-46 telefonia-ingreso-sellado (C-39, C-45)
 └── C-47 guard-costo-item (C-46, C-45)
 └── C-48 timing-en-listado (C-39)

--- FASE 18: Notificacion, directorio y canal de correo (2026-09-23 / 2026-09-25) — CERRADA ---

C-52 telefonia-transcripcion-async (C-47, C-45)          [ARCHIVADO 2026-09-30 — 44/44]
 └── C-53 notificacion-numero-incidente (C-52, C-45)     [ARCHIVADO 2026-10-01 — 12/12; SMS diferido -> C-67, cerrado NO REALIZADO 2026-10-19]
C-54 directorio-usuarios (C-53)                          [ARCHIVADO 2026-10-01 — 51/51]
C-55 canal-correo-imap (ninguna)                         [ARCHIVADO 2026-09-29 — 15/15]

--- FASE 19: Endurecimiento, auditoria y herramientas (2026-09-28 / 2026-09-30) ---

C-56 notificaciones-por-rol (C-54, C-55, C-53, C-38)    [ARCHIVADO 2026-10-08 — 27/27]
C-57 auditoria-rama-revision (ninguna nueva; C-55)       [ARCHIVADO 2026-09-29 — 15/15]
C-58 resiliencia-gemini (specs C-33/C-36/C-45)           [ARCHIVADO 2026-09-29 — 33/33]
C-59 softphone-voip-pruebas (C-52, C-45)                 [ARCHIVADO 2026-10-01 — 23/23]
C-60 directorio-endurecimiento (C-54, C-56)              [ARCHIVADO 2026-10-06 — 33/33; aprobacion humana HIGH (7.4) pendiente]

--- FASE 20: Notificacion SMS diferida (2026-10-01) — CERRADA (NO REALIZADO) ---

C-67 notificacion-sms-llamante (C-53 archivado; C-66 creado y archivado 2026-10-19, despues del cierre de C-67) [ARCHIVADO 2026-10-19 — NO REALIZADO, 0/24; OQ3 cerrado GO-WITH-CONSTRAINTS]

--- FASE 21: Cumplimiento ISO/NIST/Ley 25.326 (2026-10-01) — CERRADA ---

C-61 compliance-gobernanza (ninguna)                      [ARCHIVADO 2026-10-01 — 26/26; MEDIO; habilita C-63]
 └── C-63 identidad-accesos-claves (C-61)                 [ARCHIVADO 2026-10-08 — split c-63a/b/c (30+26+28)]
C-62 hardening-infra-red (ninguna)                        [ARCHIVADO 2026-10-08 — 33/33]
C-64 vulnerabilidades-supply-chain (ninguna)              [ARCHIVADO 2026-10-19 — 33/33; MEDIO; specs: supply-chain-security creada; ci-pipeline y security-governance-docs modificadas]
C-65 backup-continuidad (ninguna)                         [ARCHIVADO 2026-10-19 — 31/31; ALTO; specs: continuity-planning creada; backup-scripts modificada]
C-66 privacidad-transferencias (C-53 alineacion)         [ARCHIVADO 2026-10-19 — 36/36; ALTO; specs: privacy-runtime-surface creada; runtime-cost-guard, security-governance-docs y employee-directory modificadas]

--- FASE 22: Ingesta del corpus por el flujo N8N real (2026-10-02) ---

C-69 dedup-correlacion-altas (ninguna; habilita C-68)     [ARCHIVADO 2026-10-05 — 30/30; MEDIO]
C-68 corpus-ingesta-n8n (C-69)                            [ARCHIVADO 2026-10-09 — 63/63; MEDIO; spec corpus-n8n-ingest creada]

--- FASE 23: Medicion del corpus por telefonia real (2026-10-02) ---

C-70 softphone-corpus-telefonia (C-59, C-52, C-68)        [ARCHIVADO 2026-10-06 — 72/72; ALTO]

--- FASE 24: Endurecimiento del clasificador determinista (2026-10-05) ---

C-71 hardening-clasificador-determinista (ninguna nueva)  [ARCHIVADO 2026-10-06 — 43/43; MEDIO; specs sincronizadas]

--- FASE 25: Unificacion de la clasificacion telefonica a la cascada (2026-10-05) ---

C-72 unificar-clasificacion-telefonica (C-71)             [ARCHIVADO 2026-10-07 — 37/37; ALTO; specs sincronizadas (classification-resilience, n8n-workflow, runtime-cost-guard, sector-assignment ASG-012, sector-taxonomy TAX-004, telefonia-stt-intake); 5.2 cerrada con hibrido oficial (global macro-F1 0.5207, telefonia 0.4783)]

--- FASE 26: Pseudonimizacion de numeros de tarjeta hablados (2026-10-06) ---

C-73 pseudonimizacion-tarjeta (ninguna)                   [ARCHIVADO 2026-10-07 — 23/23; HIGH; spec data-pseudonymization sincronizada; [TARJETA] con disparador contextual]

--- FASE 27: Calibracion del cortocircuito determinista (2026-10-07) ---

C-74 calibracion-cortocircuito-determinista (C-71, C-72)   [ARCHIVADO 2026-10-07 — 32/32; ALTO; specs sincronizadas (classification-resilience, sector-assignment, evaluation-framework); official macro-F1 0.5207]

--- FASE 28: Sincronizacion documental N8N (2026-10-08) ---

C-75 sincronizar-docs-n8n (ninguna — drift de C-72/C-55)   [ARCHIVADO 2026-10-08 — 14/14; MEDIO; spec n8n-workflow +3 requirements]

--- FASE 29: Correcciones de la tesis por el dictamen CONEAU (2026-10-09 / 2026-10-12) ---
(independientes del software; se aplican en secuencia porque comparten .tex)

C-76 tesis-correcciones-dictamen (ninguna — documento de tesis)          [ACTIVO — 0/46; MEDIO]
 └── C-77 tesis-errores-estadisticos-inferenciales (aplicar tras C-76)   [ACTIVO — 0/49; MEDIO]
      └── C-78 tesis-bibliografia-atribucion (aplicar tras C-77)         [ACTIVO — 0/25; HIGH]
            └── C-79 tesis-aspectos-legales (aplicar tras C-78)           [ACTIVO — 0/25; HIGH]
                └── C-80 tesis-forma-evidencia-visual (aplicar tras C-79) [ACTIVO — 0/45; BAJO]

--- FASE 30: RBAC, ciclo de cierre y sesion (2026-10-13 / 2026-10-15) ---

C-81 frontend-rbac (C-82)                                [ARCHIVADO 2026-10-13 — 24/24; CRITICO]
C-82 rbac-redesign (ninguna; habilita C-81)              [ARCHIVADO 2026-10-13 — 36/36; CRITICO]
C-83 revision-humana-info-completa (ninguna)             [ARCHIVADO 2026-10-13 — 18/18; MEDIO]
C-84 logout-navbar-y-toggle-password (ninguna)           [ARCHIVADO 2026-10-15 — 15/15; BAJO]
C-85 revision-humana-contador-y-mensaje (ninguna)        [ARCHIVADO 2026-10-15 — 34/34; MEDIO]
C-86 rol-gestion-incidentes-ciclo-cierre (ninguna)       [ARCHIVADO 2026-10-15 — 61/61; ALTO]
 └── C-87 borrado-logico-incidentes (C-86)               [ARCHIVADO 2026-10-15 — 25/25; ALTO]
 └── C-88 busqueda-incidentes-panel (ninguna; c-86)       [ARCHIVADO 2026-10-15 — 19/19; MEDIO]
C-89 ui-directorio-administrador (C-86)                  [ARCHIVADO 2026-10-15 — 19/19; MEDIO]
C-90 prioridad-critica-restringida (C-86)                [ARCHIVADO 2026-10-15 — 17/17; ALTO]
C-91 sesion-jwt-cookie-rotativa (ninguna)                [ARCHIVADO 2026-10-15 — 48/48; CRITICO]

--- FASE 31: Correcciones de la tesis por la nueva auditoria (2026-10-19) ---
(independientes del software; se aplican en secuencia porque comparten .tex; tras la FASE 29)

C-92 tesis-marco-teorico-profundidad (aplicar tras C-80)         [ACTIVO — 0/29; MEDIO]
 └── C-93 tesis-metodologia-rigor (aplicar tras C-92)            [ACTIVO — 0/29; MEDIO]
      └── C-94 tesis-implementacion-verificabilidad (tras C-93)  [ACTIVO — 0/19; MEDIO]
           └── C-95 tesis-resultados-discusion-rigor (tras C-94) [ACTIVO — 0/35; MEDIO]
                └── C-96 tesis-citas-tablas-evidencia (tras C-95)[ACTIVO — 0/28; BAJO]

--- FASE 32: Seguimiento de dependencias de seguridad (2026-10-19) ---

C-97 actualizar-dependencias-seguridad (C-64)             [ARCHIVADO 2026-10-19 — 14/14; MEDIO; ejecuta el FOLLOW-UP de pip-audit de C-64; specs: supply-chain-security y ci-pipeline modificadas]
```

### Paralelismo por fase

**GATE 0: C-01 foundation-setup** ✓
  → C-02 notify-n8n-hook                    [Agente A]
  → C-03 pseudonymization-module            [Agente B]
  → C-07 frontend-testing-setup             [Agente C]
  ← PRIMER FORK: 3 changes en paralelo

**GATE 1: C-02 ✓, C-03 ✓**               ← SEGUNDO FORK
  → C-04 n8n-workflow-validation            [Agente A]
  → C-06 backend-integration-tests          [Agente B]
  → C-08 evaluation-framework               [Agente C]

**GATE 2: C-04 ✓**
  → C-05 n8n-channel-triggers               [Agente A]

**GATE 3: C-05 ✓, C-06 ✓, C-07 ✓, C-08 ✓**
  → C-09 ci-cd-pipeline                     [Agente A, B, C]

**GATE 4: C-09 ✓**
  → C-10 documentation-annexes              [Agente A, B, C]

### Camino critico (7 changes — minimo irreducible)

`C-01 → C-02 → C-04 → C-05 → C-08 → C-09 → C-10`

### Plan optimo con 3 agentes

| Paso | Agente A (Backend) | Agente B (Backend Aux) | Agente C (Testing/Frontend) |
|------|--------------------|------------------------|-----------------------------|
| 1 | `C-01` foundation-setup | — | — |
| 2 | `C-02` notify-n8n-hook | `C-03` pseudonymization | `C-07` frontend-testing |
| 3 | `C-04` n8n-workflow | `C-06` integration-tests | `C-08` evaluation |
| 4 | `C-05` n8n-channels | — | — |
| 5 | `C-09` ci-cd-pipeline (A, B, C juntos) | — | — |
| 6 | `C-10` documentation-annexes (A, B, C juntos) | — | — |

---

## FASE 1 — Cimientos

> C-01 sienta la base OPSX y la memoria compartida. Sin el no puede operar ningun agente.

### [C-01] `foundation-setup`

- **Estado**: `[x]` completado (2026-06-10 — openspec/changes/c-01-foundation-setup)
- **Scope**:
  - Completar `openspec/config.yaml` con el stack tecnologico del proyecto
  - Configurar `.engram/` en el repo para memoria compartida entre colaboradores
  - Documentar el workflow de `engram sync` en el README
  - Verificar que `openspec list` y `openspec status` respondan correctamente
  - Sembrar catalogos en base de datos (sector, estado, canal_origen) si no existen
  - Confirmar que las migraciones Alembic esten al dia
- **Dependencias**: ninguna
- **Governance**: BAJO
- **Leer antes**:
  - `docs/Tesis/tesis_para_agente.md` §5.6 (modelo de datos)
  - `docs/Tesis/tesis_para_agente.md` §6.1 (entorno de despliegue)
  - `CLAUDE.md` (reglas del proyecto)

---

## FASE 2 — Conectividad y Privacidad

> C-02 y C-03 cierran los dos gaps funcionales del backend: notificar a N8N post-clasificacion
> y pseudonimizar datos antes de enviarlos a Gemini. Ambos son independientes entre si.

### [C-02] `notify-n8n-hook`

- **Estado**: `[x]` completado (2026-06-10 — openspec/changes/archive/2026-06-10-c-02-notify-n8n-hook, PR #9)
- **Scope**:
  - Importar y llamar `notify_n8n(incidente_id, result)` desde `IncidenteService._apply_classification()` en `app/services/incidente_service.py`
  - La llamada debe ser fire-and-forget (no bloquear la respuesta HTTP ni propagar fallos)
  - Agregar test unitario que verifique que se llama a notify_n8n con los parametros correctos (usando mock de httpx)
  - Agregar test de integracion que verifique el webhook con un servidor HTTP mock
- **Dependencias**: `C-01`
- **Governance**: BAJO
- **Leer antes**:
  - `docs/Tesis/tesis_para_agente.md` §5.3 (capa de orquestacion N8N)
  - `docs/Tesis/tesis_para_agente.md` §5.7 (contrato REST)
  - `App/Backend/app/utils/n8n_webhook.py` (funcion existente)
  - `App/Backend/app/services/incidente_service.py` (donde debe llamarse)
  - `App/Backend/app/config/settings.py` §n8n_webhook_url

### [C-03] `pseudonymization-module`

- **Estado**: `[x]` completado (2026-06-11 — openspec/changes/archive/2026-06-11-c-03-pseudonymization-module, PR #10)
- **Scope**:
  - Crear `app/utils/pseudonymizer.py` con modulo de pseudonimizacion pre-transmision
  - Implementar regex que reemplace: nombres propios → `[PERSONA]`, emails → `[EMAIL]`, telefonos → `[TELEFONO]`, hosts internos → `[HOST]`
  - Aplicar pseudonimizacion ANTES de enviar la descripcion a Gemini (en `HybridClassifier.classify()` o `GeminiClassifier.classify()`)
  - Escribir tests unitarios para cada patron regex del pseudonymizer
  - Documentar el procedimiento en `docs/pseudonymization.md`
- **Dependencias**: `C-01`
- **Governance**: ALTO (datos personales — Ley 25.326)
- **Leer antes**:
  - `docs/Tesis/tesis_para_agente.md` §11.3 (transferencia internacional y pseudonimizacion)
  - `docs/Tesis/tesis_para_agente.md` §5.4 (capa de procesamiento Python)
  - `docs/anexo_h_prompt_gemini.md` §H.3 (validacion de respuesta)
  - `App/Backend/app/classifiers/gemini_classifier.py` (donde se envia a Gemini)

---

## FASE 3 — Orquestacion N8N

> C-04 y C-05 completan el flujo de N8N, que es el corazon de la orquestacion segun la tesis.
> Actualmente el JSON exportado tiene nodos placeholder (logica JS/Python vacia, condiciones IF sin configurar).

### [C-04] `n8n-workflow-validation`

- **Estado**: `[x]` completado (2026-06-11 — openspec/changes/archive/2026-06-11-c-04-n8n-workflow-validation; tareas 8.1–8.3 de verificación funcional pendientes de entorno Docker)
- **Scope**:
  - Reemplazar la logica placeholder en los nodos JavaScript del workflow N8N con la logica real de validacion del Anexo H
  - Configurar condiciones IF para evaluar `confianza >= 0.70` y rutear a revision humana vs creacion directa
  - Implementar nodo de normalizacion que homogenice la estructura de los 3 canales en un formato unificado
  - Agregar nodo HTTP que invoque `POST /api/v1/clasificar` del modulo Python
  - Agregar nodo HTTP que invoque `POST /api/v1/incidentes` para persistir el ticket
  - Verificar que el workflow completo sea funcional en un entorno de pruebas
  - Documentar los cambios en `docs/n8n-workflow-guide.md`
- **Dependencias**: `C-02`
- **Governance**: MEDIO
- **Leer antes**:
  - `docs/Tesis/tesis_para_agente.md` §5.3 (capa de orquestacion)
  - `docs/Tesis/tesis_para_agente.md` §6.3 (construccion del flujo N8N)
  - `docs/Tesis/tesis_para_agente.md` §6.5 (pruebas automatizadas)
  - `n8n/workflow.json` (workflow actual)

### [C-05] `n8n-channel-triggers`

- **Estado**: `[x]` completado (2026-06-11 — openspec/changes/archive/2026-06-11-c-05-n8n-channel-triggers; verificación funcional 7.1–7.6 ejecutada con alcance parcial: 7.1 y 7.6 verificados end-to-end, 7.2–7.5 verificados hasta backend; 4 defectos latentes detectados D-1/D-4 — ver tasks.md y n8n-workflow-guide.md)
- **Scope**:
  - Configurar nodo trigger IMAP para recepcion de correos electronicos (Outlook)
  - Configurar nodo trigger Webhook para formulario web (consumido por el frontend)
  - Configurar nodo trigger Webhook para transcripcion de Twilio (llamada telefonica)
  - Agregar nodos paralelos de notificacion al usuario post-registro (email, confirmacion web)
  - Agregar nodo de registro de auditoria (log de ejecucion por 30 dias, segun tesis)
  - Probar cada canal de forma independiente y el flujo completo
- **Dependencias**: `C-04`
- **Governance**: MEDIO
- **Leer antes**:
  - `docs/Tesis/tesis_para_agente.md` §5.2 (capa de canales de entrada)
  - `docs/Tesis/tesis_para_agente.md` §6.4 (integracion del canal telefonico)
  - `docs/Tesis/tesis_para_agente.md` §5.3 (normalizacion de entrada)

---

## FASE 4 — Testing y Validacion

> C-06 y C-07 cierran la base de la piramide de testing. El `conftest.py` ya tiene toda la
> infraestructura para integration tests; solo falta escribir los tests. El frontend no tiene
> NADA de testing.

### [C-06] `backend-integration-tests`

- **Estado**: `[x]` completado (2026-06-11 — openspec/changes/archive/2026-06-11-c-06-backend-integration-tests; 36 tareas completadas, 187 tests nuevos en verde, cobertura 89% — superando objetivo del 85%)
- **Scope**:
  - Escribir tests de integracion para `POST /api/v1/incidentes` (creacion + clasificacion) ✓
  - Escribir tests de integracion para `GET /api/v1/incidentes` (listado con filtros, paginacion) ✓
  - Escribir tests de integracion para `GET /api/v1/incidentes/{id}` (detalle + 404) ✓
  - Escribir tests de integracion para `PATCH /api/v1/incidentes/{id}` (actualizacion parcial) ✓
  - Escribir tests de integracion para `GET /api/v1/clasificaciones/revision-pendiente` (cola FIFO) ✓
  - Escribir tests de integracion para `PATCH /api/v1/clasificaciones/{id}/validar` (validacion humana) ✓
  - Escribir tests de integracion para `GET /api/v1/health` (health check) ✓
  - Usar `conftest.py` existente con SQLite in-memory + fixture `client` ASGI ✓
  - Cobertura objetivo: > 85% en modulos `routes/`, `services/`, `repositories/` ✓ (89% logrado)
- **Dependencias**: `C-02`, `C-03`
- **Governance**: BAJO
- **Leer antes**:
  - `App/Backend/tests/conftest.py` (infraestructura existente)
  - `App/Backend/tests/test_deterministic_classifier.py` (patron de tests existente)
  - `docs/Tesis/tesis_para_agente.md` §6.5 (pruebas automatizadas)
  - `docs/Tesis/tesis_para_agente.md` §4.5 (protocolo de pruebas)

### [C-07] `frontend-testing-setup`

- **Estado**: `[x]` completado (2026-06-11 — openspec/changes/archive/2026-06-11-c-07-frontend-testing-setup; Vitest + Testing Library, 68 tests, cobertura 98.6% en components/hooks/services)
- **Scope**:
  - Instalar Vitest + `@testing-library/react` + `@testing-library/jest-dom` + `happy-dom`
  - Configurar `vitest.config.ts` con alias `@/` y entorno `happy-dom`
  - Agregar script `test` en `package.json`
  - Escribir tests para componentes clave: `IncidenteForm`, `SuccessCard`, `TicketsTable`, `RevisionHumanaTable`, `SectorBadge`, `ConfianzaIndicator`
  - Escribir tests para hooks: `useReportarIncidente`, `useIncidentes`, `useRevisionPendiente`
  - Escribir tests para servicios: `api.ts`, `incidentesService.ts`, `clasificacionesService.ts`
  - Mockear Axios en los tests de servicios y hooks
  - Cobertura objetivo: > 70% en `components/`, `hooks/`, `services/`
- **Dependencias**: `C-01`
- **Governance**: BAJO
- **Leer antes**:
  - `App/Frontend/package.json` (dependencias actuales)
  - `App/Frontend/vite.config.ts` (configuracion existente)
  - `docs/Tesis/tesis_para_agente.md` §6.5 (pruebas automatizadas)

---

## FASE 5 — Evaluacion y Automatizacion

> C-08 implementa el framework de evaluacion que la tesis describe en el Capitulo 7.
> C-09 automatiza la ejecucion de pruebas en cada push.

### [C-08] `evaluation-framework`

- **Estado**: `[x]` completado (2026-06-11 — openspec/changes/archive/2026-06-11-c-08-evaluation-framework; tarea 8.1 corrida real pendiente del corpus no-trackeado)
- **Scope**:
  - Crear script Python en `evaluation/run_evaluation.py` que cargue el corpus de 200 casos desde CSV (superado por C-27: corpus JSON multietiqueta)
  - Ejecutar el clasificador hibrido sobre cada caso y recolectar: categoria predicha, confianza, etapa
  - Calcular metricas: exactitud global, matriz de confusion, precision/sensibilidad/F1 por clase, F1 macro
  - Generar reporte en `evaluation/report.md` con tablas de metricas
  - Crear notebook Jupyter en `evaluation/analysis.ipynb` con visualizaciones (matriz de confusion, distribucion de confianzas, curva de calibracion)
  - Implementar calculo de Wilcoxon signed-rank test para comparacion de tiempos
  - Documentar el procedimiento en `evaluation/README.md`
  - Incluir `evaluation/requirements.txt` con dependencias (scikit-learn, scipy, pandas, matplotlib, seaborn)
- **Dependencias**: `C-02`, `C-03`
- **Governance**: BAJO
- **Leer antes**:
  - `docs/Tesis/tesis_para_agente.md` §4.6 (metricas e instrumentos)
  - `docs/Tesis/tesis_para_agente.md` §4.7 (analisis estadistico)
  - `docs/Tesis/tesis_para_agente.md` §7.1-7.4 (resultados esperados)
  - `docs/anexo_h_prompt_gemini.md` §H.4 (iteracion y mejora)

### [C-09] `ci-cd-pipeline`

- **Estado**: `[x]` completado (2026-06-11 — openspec/changes/archive/2026-06-11-c-09-ci-cd-pipeline; .github/workflows/ci.yml creado con jobs backend-tests + frontend-tests; ruff.toml permisivo; ESLint flat config; badge en README)
- **Scope**:
  - Crear `.github/workflows/ci.yml` con workflow de GitHub Actions
  - Jobs: `backend-tests` (pytest + coverage) y `frontend-tests` (vitest)
  - Backend tests: Python 3.12, instalar dependencias, ejecutar pytest con coverage
  - Frontend tests: Node 20, npm ci, ejecutar vitest
  - Agregar step de linting (ruff para Python, eslint para frontend)
  - Configurar que los tests se ejecuten en cada push a main y en cada PR
  - Agregar badge de coverage en README.md
- **Dependencias**: `C-06`, `C-07`
- **Governance**: BAJO
- **Leer antes**:
  - `docs/Tesis/tesis_para_agente.md` §6.5 (pruebas automatizadas)
  - `App/Backend/pytest.ini` (configuracion pytest existente)
  - `App/Backend/requirements.txt` (dependencias)

---

## FASE 6 — Documentacion y Cierre

> C-10 completa los anexos que la tesis define como "A desarrollar" y la documentacion
> operativa.

### [C-10] `documentation-annexes`

- **Estado**: `[x]` completado (2026-06-11 — openspec/changes/archive/2026-06-11-c-10-documentation-annexes; 25 tareas completadas, especificacion project-documentation sincronizada, todos los anexos A-G y documentacion operativa generados)
- **Scope**:
  - Crear diagrama de arquitectura UML (despliegue, secuencia, componentes) en `docs/diagrams/`
  - Generar especificacion OpenAPI 3.1 estatica en `docs/openapi.json`
  - Completar `docs/anexo_c_esquema_bd.md` con script SQL completo de las 5 tablas
  - Completar `docs/anexo_f_corpus.md` con descripcion del corpus de validacion
  - Crear `docs/operational-guide.md` con procedimientos de despliegue, backup, monitoreo
  - Actualizar `README.md` con instrucciones de despliegue local (< 15 minutos)
  - Agregar guia de troubleshooting para operadores en `docs/troubleshooting.md`
- **Dependencias**: `C-04`, `C-05`, `C-09`
- **Governance**: BAJO
- **Leer antes**:
  - `docs/Tesis/tesis_para_agente.md` §13 (Anexos A-G)
  - `docs/Tesis/tesis_para_agente.md` §11.4 (seguridad tecnica)
  - `docs/Tesis/tesis_para_agente.md` §6.1 (entorno de despliegue)
  - `App/Backend/Dockerfile` y `App/Backend/docker-compose.yml`
  - `App/Frontend/vite.config.ts`

---

## Resumen de Changes

| ID | Nombre | Fase | Dependencias | Governance | Agente |
|----|--------|------|--------------|------------|--------|
| C-01 | foundation-setup | 1 | ninguna | BAJO | A |
| C-02 | notify-n8n-hook | 2 | C-01 | BAJO | A |
| C-03 | pseudonymization-module | 2 | C-01 | ALTO | B |
| C-04 | n8n-workflow-validation | 3 | C-02 | MEDIO | A |
| C-05 | n8n-channel-triggers | 3 | C-04 | MEDIO | A |
| C-06 | backend-integration-tests | 4 | C-02, C-03 | BAJO | B |
| C-07 | frontend-testing-setup | 4 | C-01 | BAJO | C |
| C-08 | evaluation-framework | 5 | C-02, C-03 | BAJO | C |
| C-09 | ci-cd-pipeline | 5 | C-06, C-07 | BAJO | A/B/C |
| C-10 | documentation-annexes | 6 | C-04, C-05, C-09 | BAJO | A/B/C |
| C-11 | tesis-correcciones-academicas | 7 | ninguna (documento independiente) | BAJO | — |
| C-12 | tesis-recomendaciones-coneau | 8 | C-11 (documento de tesis) | BAJO | — |
| C-13 | tesis-notas-sentido-comun | 8 | C-12 (documento de tesis) | BAJO | — |
| C-14 | kb-sync-implementation-state | 12 | ninguna | BAJO | — |
| C-15 | jwt-auth-backend-frontend | 12 | C-01, C-14 | ALTO | — |
| C-16 | twilio-twiml-script | 12 | C-05 | MEDIO | — |
| C-17 | evaluation-corpus-simulado | 12 | C-08 | BAJO | — |
| C-18 | tesis-alineacion-tecnologica | 12 | ninguna | MEDIO | — |
| C-19 | integration-tests-postgresql | 13 | C-15, C-24 | MEDIO | — |
| C-20 | tls-docker-compose | 13 | ninguna | MEDIO | — |
| C-22 | tesis-dashboard-analytics | 13 | C-23 | MEDIO | — |
| C-23 | dashboard-analytics-implementation | 13 | C-15, C-24 | MEDIO | — |
| C-24 | restructure-app-directory | 13 | ninguna | BAJO | — |
| C-25 | root-cleanup | 13 | C-24 | BAJO | — |
| — | improve-dockerfiles (sin numero) | 13 | ninguna | MEDIO | — |
| C-26 | corpus-simulado-backup-retencion | 10 | C-17 | BAJO | — |
| C-27 | rediseno-sectores-json | 11 | C-26 | CRITICO | — |
| C-28 | bootstrap-un-comando | 14 | C-20, C-25 | MEDIO | — |
| C-29 | seam-tests | 14 | C-19, C-27 | MEDIO | — |
| C-30 | bugfix-seams | 14 | C-29 | CRITICO | — |
| C-31 | dry-run-harness | 14 | C-30 | MEDIO | — |
| C-32 | disposable-test-db | 14 | C-29, C-30 | ALTO | — |
| C-33 | cost-guards | 14 | C-30, C-31, C-32 | ALTO | — |
| C-34 | evaluation-prediction-cache | 14 | C-08, C-27 | MEDIO | — |
| C-35 | dashboard-business-day-grouping | 14 | C-30, C-32 | MEDIO | — |
| C-36 | credentialing-readiness | 14 | C-33, C-34 | ALTO | — |
| C-37 | secret-hardening | 14 | ninguna | CRITICO | — |
| C-38 | n8n-confidence-gate | 14 | C-30, C-33 | MEDIO | — |
| C-39 | e2e-timing-instrumentation | 14 | C-33, C-32 | ALTO | — |
| C-40 | n8n-wiring-fixes | 14 | C-39 | ALTO | — |
| C-41 | cost-preflight-wiring | 14 | C-36 | MEDIO | — |
| C-42 | bootstrap-docs-sync | 15 | C-39, C-40, C-41 | BAJO | — |
| C-43 | docs-restructure-sync | 15 | C-42 | BAJO | — |
| C-44 | docs-evaluation-sync | 15 | C-43 | BAJO | — |
| C-45 | runtime-cost-guard | 16 | C-41, C-33 | ALTO | — |
| C-46 | telefonia-ingreso-sellado | 17 | C-39, C-45 | MEDIO | — |
| C-47 | guard-costo-item | 17 | C-46, C-45 | MEDIO | — |
| C-48 | timing-en-listado | 17 | C-39 | BAJO | — |
| C-52 | telefonia-transcripcion-async | 18 | C-47, C-45 | CRITICO | — |
| C-53 | notificacion-numero-incidente | 18 | C-52, C-45 | ALTO | — |
| C-54 | directorio-usuarios | 18 | C-53 | ALTO | — |
| C-55 | canal-correo-imap | 18 | ninguna | MEDIO | — |
| C-56 | notificaciones-por-rol | 19 | C-54, C-55, C-53, C-38 | ALTO | — |
| C-57 | auditoria-rama-revision | 19 | ninguna nueva (C-55) | MEDIO | — |
| C-58 | resiliencia-gemini | 19 | C-33, C-36, C-45 | ALTO | — |
| C-59 | softphone-voip-pruebas | 19 | C-52, C-45 | MEDIO | — |
| C-60 | directorio-endurecimiento | 19 | C-54, C-56 | ALTO | — |
| C-67 | notificacion-sms-llamante | 20 | C-53 (archivado); C-66 (creado y archivado 2026-10-19; C-67 NO REALIZADO) | ALTO | — |
| C-61 | compliance-gobernanza | 21 | ninguna | MEDIO | — |
| C-62 | hardening-infra-red | 21 | ninguna | ALTO | — |
| C-63 | identidad-accesos-claves (c-63a/b/c) | 21 | C-61 | CRITICO | — |
| C-66 | privacidad-transferencias | 21 | C-53 (alineacion) | ALTO | — |
| C-68 | corpus-ingesta-n8n | 22 | C-69 | MEDIO | — |
| C-69 | dedup-correlacion-altas | 22 | ninguna (habilita C-68) | MEDIO | — |
| C-70 | softphone-corpus-telefonia | 23 | C-59, C-52, C-68 | ALTO | — |
| C-71 | hardening-clasificador-determinista | 24 | ninguna nueva | MEDIO | — |
| C-72 | unificar-clasificacion-telefonica | 25 | C-71 | ALTO | — |
| C-73 | pseudonimizacion-tarjeta | 26 | ninguna | ALTO | — |
| C-74 | calibracion-cortocircuito-determinista | 27 | C-71, C-72 | ALTO | — |
| C-75 | sincronizar-docs-n8n | 28 | ninguna (drift de C-72/C-55) | MEDIO | — |
| C-76 | tesis-correcciones-dictamen | 29 | ninguna (documento de tesis) | MEDIO | — |
| C-77 | tesis-errores-estadisticos-inferenciales | 29 | aplicar tras C-76 | MEDIO | — |
| C-78 | tesis-bibliografia-atribucion | 29 | aplicar tras C-77 | ALTO | — |
| C-79 | tesis-aspectos-legales | 29 | aplicar tras C-78 | ALTO | — |
| C-80 | tesis-forma-evidencia-visual | 29 | aplicar tras C-79 | BAJO | — |
| C-81 | frontend-rbac | 30 | C-82 (archivado) | CRITICO | — |
| C-82 | rbac-redesign | 30 | ninguna (habilita C-81) | CRITICO | — |
| C-83 | revision-humana-info-completa | 30 | ninguna (frontend) | MEDIO | — |
| C-84 | logout-navbar-y-toggle-password | 30 | ninguna (frontend) | BAJO | — |
| C-85 | revision-humana-contador-y-mensaje | 30 | ninguna (frontend + conteo) | MEDIO | — |
| C-86 | rol-gestion-incidentes-ciclo-cierre | 30 | ninguna nueva | ALTO | — |
| C-87 | borrado-logico-incidentes | 30 | C-86 | ALTO | — |
| C-88 | busqueda-incidentes-panel | 30 | ninguna (ortogonal a C-86) | MEDIO | — |
| C-89 | ui-directorio-administrador | 30 | C-86 | MEDIO | — |
| C-90 | prioridad-critica-restringida | 30 | C-86 | ALTO | — |
| C-91 | sesion-jwt-cookie-rotativa | 30 | ninguna nueva | CRITICO | — |
| C-92 | tesis-marco-teorico-profundidad | 31 | aplicar tras C-80 | MEDIO | — |
| C-93 | tesis-metodologia-rigor | 31 | aplicar tras C-92 | MEDIO | — |
| C-94 | tesis-implementacion-verificabilidad | 31 | aplicar tras C-93 | MEDIO | — |
| C-95 | tesis-resultados-discusion-rigor | 31 | aplicar tras C-94 | MEDIO | — |
| C-96 | tesis-citas-tablas-evidencia | 31 | aplicar tras C-95 | BAJO | — |
| C-97 | actualizar-dependencias-seguridad | 32 | C-64 | MEDIO | — |

**Total**: 94 entradas creadas documentadas (93 numeradas + 1 de mantenimiento sin numero) — 84 archivadas (83 numeradas: C-01..C-20, C-22..C-48, C-52, C-53, C-54, C-55, C-56, C-57, C-58, C-59, C-60, C-61, C-62, C-63, C-64, C-65, C-66, C-67, C-68, C-69, C-70, C-71, C-72, C-73, C-74, C-75, C-81..C-91 y C-97; mas `improve-dockerfiles`) y 10 ACTIVOS (C-76, C-77, C-78, C-79, C-80, C-92, C-93, C-94, C-95, C-96). C-21, C-49 y C-50 nunca se crearon; C-51 fue absorbido por C-52 y no se abre.
**Planificadas (NO creadas)**: ninguna. El plan de cumplimiento (FASE 21) quedo TOTALMENTE EJECUTADO: C-61 `compliance-gobernanza` (MEDIO), C-62 `hardening-infra-red` (ALTO) y C-63 `identidad-accesos-claves` (CRITICO, split en c-63a/b/c) quedaron ARCHIVADOS (2026-10-01, 2026-10-08 y 2026-10-08), con sus specs `security-governance-docs`, `infra-network-hardening` e `identity-access-hardening`; C-64 `vulnerabilidades-supply-chain` (MEDIO) quedo ARCHIVADO (2026-10-19, 33/33), con su spec `supply-chain-security` creada y `ci-pipeline` y `security-governance-docs` modificadas; C-65 `backup-continuidad` (ALTO) quedo ARCHIVADO (2026-10-19, 31/31), con su spec `continuity-planning` creada y `backup-scripts` modificada; y C-66 `privacidad-transferencias` (ALTO) quedo creado y ARCHIVADO (2026-10-19, 36/36), con su spec `privacy-runtime-surface` creada y `runtime-cost-guard`, `security-governance-docs` y `employee-directory` modificadas. Ver `docs/cumplimiento/plan-cambios-cumplimiento.md`.
**Camino critico (software)**: 7 changes (C-01 → C-02 → C-04 → C-05 → C-08 → C-09 → C-10).
**Gates de paralelismo**: 5 gates (permite hasta 3 agentes simultaneos).
**Fases**: 1-31 (la FASE 9 quedo vacia; los changes que alli se preveian se documentan en la FASE 12; la FASE 18 agrupa C-52..C-55, ya CERRADA, la FASE 19 agrupa los changes de endurecimiento, auditoria y herramientas C-56..C-60, la FASE 20 agrupa la notificacion SMS diferida C-67 (archivado 2026-10-19 como NO REALIZADO), la FASE 21 agrupa el plan de cumplimiento ISO/NIST/Ley 25.326, TOTALMENTE EJECUTADA, con C-61 archivado (2026-10-01), C-62 archivado (2026-10-08), C-63a/b/c archivados (2026-10-08), C-64 archivado (2026-10-19), C-65 archivado (2026-10-19) y C-66 archivado (2026-10-19), la FASE 22 agrupa la ingesta del corpus por el flujo N8N real con C-69 archivado (2026-10-05) y C-68 archivado (2026-10-09), la FASE 23 agrupa la medicion del corpus por telefonia real con C-70 archivado (2026-10-06), la FASE 24 agrupa el endurecimiento del clasificador determinista con C-71 archivado (2026-10-06), la FASE 25 agrupa la unificacion de la clasificacion telefonica con C-72 archivado (2026-10-07), la FASE 26 agrupa la pseudonimizacion de numeros de tarjeta hablados con C-73 archivado (2026-10-07), la FASE 27 agrupa la calibracion del cortocircuito determinista con C-74 archivado (2026-10-07), y la FASE 28 agrupa la sincronizacion documental N8N con C-75 archivado (2026-10-08), y la FASE 29 agrupa las correcciones de la tesis por el dictamen CONEAU (C-76..C-80), cinco changes ACTIVOS (0 tareas), independientes del software, aplicables en secuencia; y la FASE 30 agrupa el RBAC, el ciclo de cierre y la sesion (C-81..C-91), once changes ARCHIVADOS — C-81..C-83 el 2026-10-13 y C-84..C-91 el 2026-10-15; y la FASE 31 agrupa las correcciones de la tesis por la nueva auditoria (C-92..C-96), cinco changes ACTIVOS (0 tareas), independientes del software, aplicables en secuencia despues de la FASE 29).

---

## FASE 7 — Documento de Tesis

> C-11 opera sobre el documento academico de tesis (LaTeX), independiente del software.
> No comparte dependencias con C-01 a C-10.

### [C-11] `tesis-correcciones-academicas`

- **Estado**: `[x]` completado (2026-07-02 — openspec/changes/archive/2026-07-02-c-11-tesis-correcciones-academicas)
- **Scope**:
  - Compilar la tesis desde fuente LaTeX (XeLaTeX + biber) a PDF canonico (68 paginas, 294 KB)
  - Verificar integridad de citas: 67 comandos de citacion, 34 entradas bibliograficas, cero huerfanos
  - Revisar y corregir prosa academica en los 11 archivos .tex (eliminar patrones de escritura IA, fortalecer voz interpretativa)
  - Expandir Capitulo 6 (implementacion): justificacion de tecnologia, diseno de flujo N8N, desafios de integracion
  - Reestructurar Capitulo 9 (conclusiones): eliminar enumeracion mecanica, agregar profundidad interpretativa
  - Agregar abstract en ingles (~242 palabras) en `00-resumen.tex`
  - Generar DOCX secundario via pandoc con disclaimer bilinguee
- **Dependencias**: ninguna (documento independiente del software)
- **Governance**: BAJO
  - **Nueva capacidad**: `tesis-document`
  - **Leer antes**:
    - `docs/Tesis/v8 (IA)/paper/` (fuente LaTeX)
    - `docs/Tesis/v8 (IA)/paper/preamble.tex` (configuracion biblatex-apa)
    - `openspec/specs/tesis-document/spec.md` (especificacion sincronizada)

---

## FASE 8 — Recomendaciones Finales CONEAU

> C-12 incorpora las recomendaciones post-defensa de un evaluador CONEAU al documento de tesis.
> Opera sobre el mismo documento LaTeX que C-11.

### [C-12] `tesis-recomendaciones-coneau`

- **Estado**: `[x]` completado (2026-07-02 — openspec/changes/archive/2026-07-02-c-12-tesis-recomendaciones-coneau)
- **Scope**:
  - **R1**: Renombrar `13-anexos.tex` a `12-anexos.tex` (numeracion consistente de capitulos)
  - **R2**: Reemplazar referencias bibliograficas debiles: Pressman2020 por Galup2009 (degradacion ITSM), Crispin2009 por Ladas2009 (metodologia Scrumban); preservar Crispin2009 para testing pyramid
  - **R3 (CRITICO)**: Eliminar dos referencias fabricadas (Karchhud2024, Mehdi2023) de Bibliography_base.bib y todos los .tex; reescribir parrafos afectados sin claims cuantitativos infundados
  - **R4**: Corregir argumento CV enganoso en 08-discusion.tex; reemplazar con analisis de rango absoluto
  - **R5**: Agregar parrafo de debriefing post-hoc en 11-aspectos-legales.tex sobre operadores cuyos tiempos fueron medidos
  - **Verificacion**: verify_citations.py PASS (33 entradas, 0 huerfanos, 0 sin uso); compilacion PDF limpia (68 paginas, cero warnings)
- **Dependencias**: C-11 (documento de tesis)
- **Governance**: BAJO
- **Leer antes**:
  - `docs/Tesis/v8 (IA)/paper/` (fuente LaTeX)
  - `docs/Tesis/v8 (IA)/paper/Bibliography_base.bib` (archivo de bibliografia)
  - `docs/Tesis/v8 (IA)/verify_citations.py` (script de verificacion de citas)
   - `openspec/specs/tesis-document/spec.md` (especificacion sincronizada)

### [C-13] `tesis-notas-sentido-comun`

- **Estado**: `[x]` completado (2026-07-02 — openspec/changes/archive/2026-07-02-c-13-tesis-notas-sentido-comun)
- **Scope**:
  - Integrar 3 notas de "sentido comun" operativo de mesa de ayuda en la discusion y trabajo futuro
  - **N2**: Agregar parrafo sobre gestion gradual del cambio en 08-discusion.tex §8.4
  - **N3**: Expandir parrafo de analitica organizacional en 10-recomendaciones.tex §10.3
  - **N4**: Nueva subseccion 10.7 "Base de conocimientos para resolucion automatica" en 10-recomendaciones.tex
  - Tambien en esta sesion (no trackeado como tareas separadas): diagrama de arquitectura en Capitulo 5, ajuste de 6 tablas por warnings LaTeX, 225 acentos en 14 archivos .tex, backups .tex.bak
- **Dependencias**: C-12 (documento de tesis)
- **Governance**: BAJO
- **Leer antes**:
  - `docs/Tesis/v8 (IA)/paper/` (fuente LaTeX)
  - `openspec/specs/tesis-document/spec.md` (especificacion sincronizada)

---

## FASE 10 — Cierre de brechas tesis/codigo

> C-26 cierra las brechas de alineacion entre la tesis y el codigo:
> corpus calibrado con metricas exactas, scripts de backup automatizados,
> y configuracion de retencion de datos N8N.

### [C-26] `corpus-simulado-backup-retencion`

- **Estado**: `[x]` completado (2026-07-03 — openspec/changes/c-26-corpus-simulado-backup-retencion)
- **Scope**:
  - (SUPERADO por C-27) Reemplazar corpus simulado por corpus calibrado que produce metricas exactas de tesis (92% accuracy, F1 macro ~0.919, matriz de confusion Tabla 7, Wilcoxon W=0, p<0.001)
  - Agregar columnas `tiempo_manual_s` y `tiempo_automatizado_s` al CSV del corpus
  - Crear `scripts/backup.sh` (Bash) y `scripts/backup.ps1` (PowerShell) para backups PostgreSQL con rotacion de 7 dias
  - Configurar retencion de ejecuciones N8N a 30 dias via variables de entorno en docker-compose.yml
  - Actualizar guia operativa con referencias a scripts de backup, retencion N8N, y seccion de evaluacion
  - (SUPERADO por C-27) Actualizar FakeClassifier con mapeos calibrados para los 200 casos
  - 38 tests de evaluacion pasando (37 pass, 1 skip)
- **Dependencias**: C-17
- **Governance**: BAJO
- **Leer antes**:
  - `evaluation/generate_corpus.py` (generador de corpus calibrado, seed=42)
  - `evaluation/data/README.md` (documentacion del corpus)
  - `scripts/backup.sh` y `scripts/backup.ps1` (scripts de backup)
  - `docker-compose.yml` (variables EXECUTIONS_DATA_PRUNE / EXECUTIONS_DATA_MAX_AGE)
  - `docs/operational-guide.md` §3 (backup) y §1.5 (N8N retencion)

---

## FASE 11 — Rediseño de sectores y corpus JSON multietiqueta

> C-27 reemplaza la taxonomia de 3 categorias por 5 sectores canonicos, migra la
> verdad del corpus a JSON multietiqueta y elimina el corpus sintetico de 200 casos.

### [C-27] `rediseno-sectores-json`

- **Estado**: `[x]` completado (2026-09-11 — openspec/changes/c-27-rediseno-sectores-json)
- **Scope**:
  - Vocabulario canonico de 5 sectores sin tildes (`Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos`, `Sistemas`); `Operaciones` eliminado.
  - Migracion `004_sectores_multietiqueta.py`: tablas de union `incidente_sector_adicional`, `clasificacion_sector_predicho`, `clasificacion_sector_validado`.
  - Contrato `sector_predicho` + `sectores_adicionales` en schemas, servicio y webhook N8N.
  - Corpus JSON multietiqueta (`schema_version`/`metadata`/`casos`) con `sector_asignado` + `sectores_adicionales`; elimina `categoria_real` y el corpus sintetico de 200 casos.
  - Metricas multietiqueta: matriz primaria 5x5, subset accuracy, Hamming loss, micro/macro F1, Wilson en igualdad estricta y pertenencia.
  - Frontend sin IDs numericos fijos: catalogo de sectores en runtime (`GET /api/v1/catalogos/sectores`).
- **Dependencias**: C-26 (corpus sintetico y andamiaje que se elimina)
- **Governance**: ALTA/CRITICA (strings de dominio persistidos + migracion de datos)
- **Nota**: los numeros 82/64/54, exactitud 92 %, F1 ~0.919 y Tabla 7 del corpus sintetico quedan superados; se re-miden con el corpus real.
- **Leer antes**:
  - `openspec/changes/c-27-rediseno-sectores-json/design.md` (decisiones D1-D8)
  - `knowledge-base/05_reglas_de_negocio.md` (RN-CL-01/04, RN-VA-03)
  - `docs/anexo_f_corpus.md` (esquema JSON y 5 categorias)

---

## FASE 12 — Auth, integraciones externas y alineacion de tesis

> Cierra las brechas entre lo documentado y lo implementado: sincroniza la KB, agrega autenticacion JWT, completa el canal telefonico, genera corpus de evaluacion y alinea la tesis con el codigo real.

### [C-14] `kb-sync-implementation-state`

- **Estado**: `[x]` completado (2026-07-02 — `openspec/changes/archive/2026-07-02-c-14-kb-sync-implementation-state`; KB sincronizada con el estado real de implementacion)
- **Scope**:
  - Corregir 8 flags obsoletos en `knowledge-base/06_funcionalidades.md` (US-002, US-003, US-005, US-007, US-010, US-011, US-012, US-013, US-014, US-015)
  - Actualizar estados de flujos en `knowledge-base/07_flujos_principales.md`
  - Actualizar la tabla de seguridad (pseudonimizacion) en `knowledge-base/08_arquitectura_propuesta.md`
  - Actualizar SU-01, SU-02 y SU-04 en `knowledge-base/09_decisiones_y_supuestos.md`
  - Actualizar IN-01, IN-02, IN-06 y la tabla de preguntas en `knowledge-base/10_preguntas_abiertas.md`
- **Dependencias**: ninguna
- **Governance**: BAJO
- **Leer antes**:
  - `openspec/changes/archive/2026-07-02-c-14-kb-sync-implementation-state/proposal.md`
  - `knowledge-base/06_funcionalidades.md`

### [C-15] `jwt-auth-backend-frontend`

- **Estado**: `[x]` completado (2026-07-02 — `openspec/changes/archive/2026-07-02-c-15-jwt-auth-backend-frontend`; JWT Bearer con bcrypt + HS256, login y rutas protegidas)
- **Scope**:
  - Crear tabla `users` (username + hashed_password) y sembrar un usuario admin en la primera migracion
  - Implementar `POST /api/v1/auth/login` que devuelve JWT (HS256, expiracion 24 h)
  - Validar JWT via dependency injection y proteger `/api/v1/incidentes/*` y `/api/v1/clasificaciones/*`; dejar publicos `/health` y `/health/db`
  - Agregar `AuthContext`, pagina `/login` y `ProtectedRoute` en el frontend
  - Interceptor Axios para inyectar `Authorization: Bearer` y limpiar sesion ante 401
- **Dependencias**: `C-01`, `C-14`
- **Governance**: ALTO
- **Leer antes**:
  - `openspec/changes/archive/2026-07-02-c-15-jwt-auth-backend-frontend/proposal.md`
  - `openspec/changes/archive/2026-07-02-c-15-jwt-auth-backend-frontend/design.md`
  - `knowledge-base/08_arquitectura_propuesta.md`

### [C-16] `twilio-twiml-script`

- **Estado**: `[x]` completado (2026-07-02 — `openspec/changes/archive/2026-07-02-c-16-twilio-twiml-script`; TwiML y documentacion de configuracion del canal telefonico)
- **Scope**:
  - Crear `twilio/twiml.xml` con marcado TwiML valido para Programmable Voice
  - Mensaje de bienvenida en espanol rioplatense (voseo)
  - Configurar grabacion de hasta 45 segundos, finalizacion con `#` y transcripcion automatica
  - Documentar la configuracion de la cuenta en `twilio/README.md`
  - Agregar variables de entorno de Twilio en `.env.example`
- **Dependencias**: `C-05`
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-07-02-c-16-twilio-twiml-script/proposal.md`
  - `openspec/changes/archive/2026-07-02-c-16-twilio-twiml-script/design.md`
  - `docs/Tesis/tesis_para_agente.md` §6.4 (integracion del canal telefonico)

### [C-17] `evaluation-corpus-simulado`

- **Estado**: `[x]` completado (2026-07-02 — `openspec/changes/archive/2026-07-02-c-17-evaluation-corpus-simulado`; corpus simulado de 200 casos con distribucion 82/64/54, luego superado por C-27)
- **Scope**:
  - Generar `evaluation/data/corpus_evaluacion.csv` con 200 incidentes realistas en espanol rioplatense
  - Respetar la distribucion de la tesis: 82 Sistemas / 64 Operaciones / 54 Soporte Tecnico (taxonomia previa a C-27)
  - Incluir categoria real (ground truth), canal de origen y variaciones de estilo con ~10% de errores de tipeo
  - Crear el generador reproducible `evaluation/generate_corpus.py` con seed fijo
  - Documentar el origen simulado en `evaluation/data/README.md` y agregar tests del corpus generado
- **Dependencias**: `C-08`
- **Governance**: BAJO
- **Leer antes**:
  - `openspec/changes/archive/2026-07-02-c-17-evaluation-corpus-simulado/proposal.md`
  - `openspec/changes/archive/2026-07-02-c-17-evaluation-corpus-simulado/design.md`
  - `knowledge-base/06_funcionalidades.md`

### [C-18] `tesis-alineacion-tecnologica`

- **Estado**: `[x]` completado (2026-07-03 — `openspec/changes/archive/2026-07-03-c-18-tesis-alineacion-tecnologica`; capitulos 5 y 6 alineados a la implementacion real)
- **Scope**:
  - Corregir 27 brechas entre tesis y codigo en los capitulos 5 y 6 (Outlook Graph API, google-genai, asyncpg, Uvicorn 0.30.6, pytest-cov)
  - Actualizar conteo de nodos N8N (19), pipeline con AI Agent (LangChain) + Redis y entidades del modelo (6)
  - Reflejar `/health` y `/health/db`, JWT Bearer sobre SSO y el frontend React SPA independiente
  - Mantener como aspiracional/trabajo futuro TLS 1.3, HMAC-SHA-256, pgcrypto y retencion de datos
  - Actualizar `09_decisiones_y_supuestos.md` (DD-08, DD-10, DD-12) y `08_arquitectura_propuesta.md`
- **Dependencias**: ninguna
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-07-03-c-18-tesis-alineacion-tecnologica/proposal.md`
  - `knowledge-base/09_decisiones_y_supuestos.md`
  - `knowledge-base/08_arquitectura_propuesta.md`

---

## FASE 13 — Infra, pruebas de integracion y saneamiento de repositorio

> Agrega pruebas contra PostgreSQL real, terminacion TLS en el stack Docker, dashboard de analitica y reordena el repositorio para la entrega academica.

### [C-19] `integration-tests-postgresql`

- **Estado**: `[x]` completado (2026-07-03 — `openspec/changes/archive/2026-07-03-c-19-integration-tests-postgresql`; subconjunto de tests de integracion con PostgreSQL real)
- **Scope**:
  - Agregar el marcador `pytest.mark.integration` y fixtures `pg_engine`/`pg_session` en `tests/conftest.py`
  - Implementar 10-15 tests de integracion: FKs, clasificacion, constraints UNIQUE, cascade delete, Numeric(5,4) y created_at con timezone
  - Provisionar base desechable por sesion (contenedor/testcontainers o PostgreSQL local)
  - Integrar un servicio PostgreSQL en `.github/workflows/ci.yml`
  - Mantener los tests unitarios SQLite como suite rapida y offline
- **Dependencias**: `C-15`, `C-24`
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-07-03-c-19-integration-tests-postgresql/proposal.md`
  - `openspec/changes/archive/2026-07-03-c-19-integration-tests-postgresql/design.md`
  - `knowledge-base/04_modelo_de_datos.md`

### [C-20] `tls-docker-compose`

- **Estado**: `[x]` completado (2026-07-03 — `openspec/changes/archive/2026-07-03-c-20-tls-docker-compose`; nginx como terminacion TLS y stack servido por HTTPS)
- **Scope**:
  - Agregar un servicio nginx reverse proxy que termina TLS 1.3 en el borde
  - Exponer `/api/v1/` → backend, `/` → frontend y `/n8n/` → N8N sobre el puerto 443, con redireccion 80 → 443
  - Crear `scripts/generate-certs.sh` y `scripts/generate-certs.ps1` para certificados autofirmados
  - Habilitar cabeceras HSTS y actualizar `N8N_PROTOCOL`, `WEBHOOK_URL` y `VITE_API_BASE_URL`
  - Actualizar `README.md` y `docs/operational-guide.md` con los nuevos puertos y URLs HTTPS
- **Dependencias**: ninguna
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-07-03-c-20-tls-docker-compose/proposal.md`
  - `openspec/changes/archive/2026-07-03-c-20-tls-docker-compose/design.md`
  - `docs/operational-guide.md`

### [C-22] `tesis-dashboard-analytics`

- **Estado**: `[x]` completado (2026-07-03 — `openspec/changes/archive/2026-07-03-c-22-tesis-dashboard-analytics`; seccion 6.8 y politica de conservacion indefinida en la tesis)
- **Scope**:
  - Agregar la seccion 6.8 (Dashboard de Analitica) al Capitulo 6 con componentes, endpoints y filtros
  - Reemplazar en el Capitulo 10 la recomendacion de monitoreo por el dashboard ya implementado y mover alertas por umbrales a trabajo futuro
  - Reescribir §11.2 con la politica de conservacion indefinida con bloqueo de escritura sobre incidentes cerrados
  - Actualizar el Anexo G (documentacion operativa) con la seccion del dashboard
  - Dejar el Anexo C sin cambios por ser compatible con la conservacion indefinida
- **Dependencias**: `C-23`
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-07-03-c-22-tesis-dashboard-analytics/proposal.md`
  - `knowledge-base/09_decisiones_y_supuestos.md`

### [C-23] `dashboard-analytics-implementation`

- **Estado**: `[x]` completado (2026-07-03 — `openspec/changes/archive/2026-07-03-c-23-dashboard-analytics-implementation`; dashboard de analitica y bloqueo de escritura en incidentes cerrados)
- **Scope**:
  - Crear endpoints `GET /api/v1/estadisticas/tendencias` y `GET /api/v1/estadisticas/resumen` con `agrupar_por`, `desde`, `hasta` y `sector_id`
  - Implementar el bloqueo `409 Conflict` en `PATCH /api/v1/incidentes/{id}` y en `DELETE` para incidentes cerrados (`es_terminal=true`)
  - Construir la pagina `/dashboard` con `TendenciaChart`, `SectorPieChart`, `EstadoBarChart` y filtros dia/mes
  - Agregar exportacion del grafico a PNG (`html2canvas`/`recharts`) y link Dashboard en el Header
  - Marcar como solo lectura los tickets cerrados en `TicketDetailDialog` y `TicketsTable`
- **Dependencias**: `C-15`, `C-24`
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-07-03-c-23-dashboard-analytics-implementation/proposal.md`
  - `openspec/changes/archive/2026-07-03-c-23-dashboard-analytics-implementation/design.md`
  - `knowledge-base/04_modelo_de_datos.md`

### [C-24] `restructure-app-directory`

- **Estado**: `[x]` completado (2026-07-03 — `openspec/changes/archive/2026-07-03-c-24-restructure-app-directory`; backend y frontend reubicados bajo `App/`)
- **Scope**:
  - Mover `Gestion_Incidentes/` a `App/Backend/` y `Frontend/` a `App/Frontend/` con `git mv`
  - Actualizar rutas en `docker-compose.yml`, `.github/workflows/ci.yml`, `openspec/config.yaml`, `AGENTS.md`, `CHANGES.md` y `README.md`
  - Actualizar las referencias en `knowledge-base/`, `twilio/README.md`, `scripts/run_provisional.py` y los specs principales
  - Corregir los proposal files activos (C-19, C-23) para que reflejen las nuevas rutas
  - No modificar imports internos, suites de tests ni el workflow N8N
- **Dependencias**: ninguna
- **Governance**: BAJO
- **Leer antes**:
  - `openspec/changes/archive/2026-07-03-c-24-restructure-app-directory/proposal.md`
  - `openspec/changes/archive/2026-07-03-c-24-restructure-app-directory/design.md`
  - `openspec/config.yaml`

### [C-25] `root-cleanup`

- **Estado**: `[x]` completado (2026-07-03 — `openspec/changes/archive/2026-07-03-c-25-root-cleanup`; raiz saneada con `docs/`, `n8n/` y referencias actualizadas)
- **Scope**:
  - Mover `ANEXO_H_Prompt_Gemini_Especificacion.md` a `docs/anexo_h_prompt_gemini.md` y actualizar sus referencias
  - Mover `Automatizacion_Mesa_de_Ayuda.json` a `n8n/workflow.json` y actualizar las ~14 referencias activas
  - Mover `twilio/` a `n8n/twilio/` y corregir sus referencias internas y en la spec `project-structure`
  - Crear el directorio `n8n/` como agrupador de artefactos N8N
  - Corregir en `.env.example` raiz `Gestion_Incidentes/.env` → `App/Backend/.env`
- **Dependencias**: `C-24`
- **Governance**: BAJO
- **Leer antes**:
  - `openspec/changes/archive/2026-07-03-c-25-root-cleanup/proposal.md`
  - `openspec/changes/archive/2026-07-03-c-25-root-cleanup/design.md`

### [improve-dockerfiles] — mantenimiento sin numero

- **Estado**: `[x]` completado (2026-07-10 — `openspec/changes/archive/2026-07-10-improve-dockerfiles`; Dockerfiles multi-stage, usuarios non-root y healthchecks)
- **Scope**:
  - Agregar `.dockerignore` en backend y frontend
  - Implementar multi-stage builds para el frontend (build + nginx)
  - Agregar usuarios non-root y healthchecks en ambos Dockerfiles
  - Usar `npm ci` en lugar de `npm install` para builds deterministas
  - Servir el build estatico del frontend con nginx en vez del servidor de desarrollo de Vite
- **Dependencias**: ninguna
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-07-10-improve-dockerfiles/proposal.md`
  - `openspec/changes/archive/2026-07-10-improve-dockerfiles/design.md`

---

## FASE 14 — Endurecimiento y pipeline end-to-end

> Cambios ejecutados entre el 2026-09-17 y el 2026-09-20. C-39/C-40/C-41 son la "Fase 1" del pipeline (timing e2e, wiring n8n, preflight de costo), verificados y archivados el 2026-09-20.

### [C-28] `bootstrap-un-comando`

- **Estado**: `[x]` completado (2026-09-17 — `openspec/changes/archive/2026-09-17-c-28-bootstrap-un-comando`; scripts `up.sh`/`up.ps1` y `Makefile` con preflight de entorno, generacion TLS, arranque y verificacion de salud)
- **Scope**:
  - Agregar scripts pareados `scripts/up.sh` (bash) y `scripts/up.ps1` (PowerShell) que reproducen el camino feliz de arranque de forma determinista.
  - Preflight que falla con exit code distinto de cero si `App/Backend/.env` no existe, o si `GEMINI_API_KEY` / `PSEUDONYMIZATION_ENCRYPTION_KEY` estan vacias o siguen siendo placeholders; nunca imprime valores de secretos.
  - Generacion de certificados TLS si `openssl/mesa.crt` u `openssl/mesa.key` faltan, arranque con `docker compose up -d --build` (proyecto fijo `mesa_local`, sin `-p`) y espera acotada hasta que los servicios queden sanos.
  - Verificacion de salud con `curl -k https://localhost/api/v1/health` y `/api/v1/health/db`, impresion de URLs de acceso y recordatorio manual de importar `n8n/workflow.json` y configurar credenciales.
  - Agregar `Makefile` raiz como conveniencia opcional (`up`, `down`, `ps`, `logs`, `health`) que detecta el SO y delega en el script correspondiente; actualizar el README con el camino de un solo comando.
- **Dependencias**: `C-20`, `C-25`
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-17-c-28-bootstrap-un-comando/proposal.md`
  - `openspec/changes/archive/2026-09-17-c-28-bootstrap-un-comando/design.md`
  - `knowledge-base/08_arquitectura_propuesta.md`

### [C-29] `seam-tests`

- **Estado**: `[x]` completado (2026-09-17 — `openspec/changes/archive/2026-09-17-c-29-seam-tests`; infraestructura de tests reparada y comportamiento correcto codificado como tests que hoy fallan, fase RED de TDD)
- **Scope**:
  - Eliminar el auto-skip silencioso de la suite PostgreSQL de integracion: la ausencia de PostgreSQL ahora falla con mensaje accionable, no salta.
  - Declarar explicitamente `asyncio_default_fixture_loop_scope` / `loop_scope` para pytest-asyncio 0.24, evitando conexiones asyncpg atadas a otro event loop.
  - Habilitar `PRAGMA foreign_keys=ON` en el engine SQLite de tests para que las violaciones de FK se manifiesten.
  - Agregar pruebas de contrato runtime N8N (auth en el HTTP Request, `canal_origen_id`, Switch por indice numerico, Chat Model del AI Agent, trigger de Outlook, `respondToWebhook` alcanzable, credenciales declaradas).
  - Agregar pruebas de integracion PostgreSQL (estadisticas 200 y PATCH con FK inexistente 4xx) y de configuracion frontend/Docker (`VITE_API_BASE_URL` sin `/api/v1` duplicado, `ARG` del Dockerfile, rutas alineadas con OpenAPI).
  - Registrar linea base de conteos de tests antes/despues de tocar `conftest.py` y `pytest.ini`.
- **Dependencias**: `C-19`, `C-27`
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-17-c-29-seam-tests/proposal.md`
  - `openspec/changes/archive/2026-09-17-c-29-seam-tests/design.md`
  - `openspec/changes/archive/2026-09-17-c-29-seam-tests/notes.md`

### [C-30] `bugfix-seams`

- **Estado**: `[x]` completado (2026-09-17 — `openspec/changes/archive/2026-09-17-c-30-bugfix-seams`; correccion de los defectos de costura confirmados por la auditoria, fase GREEN de TDD)
- **Scope**:
  - Corregir los blockers del flujo N8N: login dinamico + header `Authorization` (JWT Bearer), Chat Model conectado al `AI Agent`, prompt con el payload del trigger, contrato de salida del agente alineado con el validador, `Switch` por canal normalizado, `responseMode` alcanzable y extraccion del body desde el trigger de Outlook.
  - Backend: eliminar `func.strftime` de `estadisticas_service.py` (SQL portable), validar existencia de FK en PATCH (4xx en lugar de 500), mapear `CanalOrigenNotFoundError` a 4xx, unificar el envelope de error y preservar terminos tecnicos/marcas en el pseudonimizador.
  - Frontend: base URL unica del API, barra final contra el 307 del proxy, invalidacion de query del detalle, contador de revision sobre el total, fechas del dashboard sin desfase UTC y estado de carga compuesto.
  - Cubrir las tareas por severidad (blocker, alto, medio, bajo) del inventario B-01..B-17, BE B1..B8 y FE 1..8.
- **Dependencias**: `C-29`
- **Governance**: CRITICO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-17-c-30-bugfix-seams/proposal.md`
  - `openspec/changes/archive/2026-09-17-c-30-bugfix-seams/design.md`
  - `knowledge-base/07_flujos_principales.md`

### [C-31] `dry-run-harness`

- **Estado**: `[x]` completado (2026-09-17 — `openspec/changes/archive/2026-09-17-c-31-dry-run-harness`; arnes local de costo cero que valida la plomeria compartida de alta de incidentes)
- **Scope**:
  - CLI local en `scripts/dry_run/` que levanta o reutiliza el stack `mesa_local` con `GEMINI_API_KEY` ficticia.
  - Preflight de contratos contra backend y webhook N8N: login devuelve `access_token`, alta valida 201, descripcion menor a 10 caracteres 422, falta de barra final detectada (307) y webhook alcanzable.
  - Verificacion end-to-end del canal web: webhook N8N -> normalizacion/login/validacion -> `POST /api/v1/incidentes/` -> persistencia con `canal_origen_id` correcto.
  - Guardarrailes de costo cero: prohibicion de invocar Gemini/Twilio reales y afirmacion de que una clave ficticia esta en efecto antes de ejecutar.
  - Documentar el canal correo (gratis, paso opcional) y el canal telefono (manual, fuera del camino de costo cero) mas un objetivo opcional en el `Makefile`.
- **Dependencias**: `C-30`
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-17-c-31-dry-run-harness/proposal.md`
  - `openspec/changes/archive/2026-09-17-c-31-dry-run-harness/design.md`

### [C-32] `disposable-test-db`

- **Estado**: `[x]` completado (2026-09-17 — `openspec/changes/archive/2026-09-17-c-32-disposable-test-db`; la suite de integracion ya no puede destruir la base de aplicacion)
- **Scope**:
  - `_get_pg_url()` deja de resolver por defecto a `mesa_de_ayuda`; apunta a una base descartable dedicada (`mesa_de_ayuda_test`) o exige `TEST_PG_URL`.
  - Aprovisionamiento (`CREATE DATABASE`) y descarte (`DROP DATABASE`) de la base descartable por sesion via conexion de mantenimiento.
  - Guardia que aborta el DDL destructivo si el nombre de la base coincide con el de la aplicacion (escape explicito `TEST_PG_ALLOW_APP_DB`).
  - Conservar las garantias de C-29: fallo ruidoso ante PostgreSQL ausente, `PRAGMA foreign_keys=ON` y tests de integracion en verde; CI sin cambios.
  - Corregir `AGENTS.md` y `openspec/config.yaml` para declarar el prerequisito PostgreSQL del subconjunto de integracion y el flujo local seguro.
- **Dependencias**: `C-29`, `C-30`
- **Governance**: ALTO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-17-c-32-disposable-test-db/proposal.md`
  - `openspec/changes/archive/2026-09-17-c-32-disposable-test-db/design.md`

### [C-33] `cost-guards`

- **Estado**: `[x]` completado (2026-09-17 — `openspec/changes/archive/2026-09-17-c-33-cost-guards`; bucles y reproceso de trabajo pago acotados antes de conectar credenciales reales)
- **Scope**:
  - Acotar el refinamiento del `AI Agent` telefonico a un maximo de 2 intentos, con derivacion a nodo terminal que persiste con `requiere_revision_humana=true`.
  - Idempotencia por `Message-ID` de Outlook: columna `origen_message_id` UNIQUE nullable en `Incidente` con migracion Alembic; el backend cortocircuita duplicados antes de clasificar.
  - Extender el contrato de alta para aceptar clasificacion precalculada (sector + confianza + origen explicito) que omite la reclasificacion paga.
  - Marcar el correo como leido en todas las ramas terminales (exito, rechazo, error) y acotar la rafaga inicial con filtro `receivedDateTime` (lookback de 24 h).
  - Apuntar la notificacion del backend a un webhook N8N dedicado que no crea incidentes; ajustar `N8N_WEBHOOK_URL` a la ruta dedicada.
- **Dependencias**: `C-30`, `C-31`, `C-32`
- **Governance**: ALTO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-17-c-33-cost-guards/proposal.md`
  - `openspec/changes/archive/2026-09-17-c-33-cost-guards/design.md`

### [C-34] `evaluation-prediction-cache`

- **Estado**: `[x]` completado (2026-09-17 — `openspec/changes/archive/2026-09-17-c-34-evaluation-prediction-cache`; cache de predicciones, pin de imagen N8N y limpieza de variables Twilio)
- **Scope**:
  - Cache de predicciones en `evaluation/run_evaluation.py` validado por hash SHA-256 del corpus + cantidad de casos + clave de configuracion del clasificador.
  - Invalidacion automatica ante cualquier cambio del corpus o la config, con bandera `--force` / `--no-cache` para saltar el cache.
  - `evaluation/predicciones.json` pasa a llevar un campo de metadata de cache ademas de las predicciones.
  - Fijar la imagen `n8nio/n8n:2.11.2` en `docker-compose.yml` (reemplaza `latest`).
  - Comentar las variables `TWILIO_*` en `App/Backend/.env.example` con nota de que pertenecen a N8N.
  - Agregar tests TDD de los tres escenarios del cache (hit, invalidacion, force).
- **Dependencias**: `C-08`, `C-27`
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-17-c-34-evaluation-prediction-cache/proposal.md`
  - `openspec/changes/archive/2026-09-17-c-34-evaluation-prediction-cache/design.md`
  - `knowledge-base/11_evaluacion_experimental.md`

### [C-35] `dashboard-business-day-grouping`

- **Estado**: `[x]` completado (2026-09-17 — `openspec/changes/archive/2026-09-17-c-35-dashboard-business-day-grouping`; agrupacion del dashboard por dia de negocio UTC-3)
- **Scope**:
  - `EstadisticasRepository._period_expression` convierte `created_at` a `America/Argentina/Buenos_Aires` antes de truncar la etiqueta de fecha.
  - Expresion por dialecto: PostgreSQL `func.timezone(...)` + `func.to_char(...)`; SQLite `func.datetime(created_at, '-3 hours')` + `func.strftime(...)` con offset inyectable via `tz_offset_hours`.
  - Actualizar los tests que afirman sobre etiquetas `periodo` y agregar escenarios de frontera 21:00-23:59 BA; delta de `dashboard-analytics`.
  - Verificacion PostgreSQL via subconjunto `@pytest.mark.integration` sobre la base descartable de C-32.
  - Eliminar el code fence desbalanceado de `docs/operational-guide.md` (linea 431).
- **Dependencias**: `C-30`, `C-32`
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-17-c-35-dashboard-business-day-grouping/proposal.md`
  - `openspec/changes/archive/2026-09-17-c-35-dashboard-business-day-grouping/design.md`
  - `knowledge-base/06_funcionalidades.md`

### [C-36] `credentialing-readiness`

- **Estado**: `[x]` completado (2026-09-17 — `openspec/changes/archive/2026-09-17-c-36-credentialing-readiness`; tope de ejecucion N8N, preflight de costo y gate de corrida paga listos sin credenciales)
- **Scope**:
  - Declarar `EXECUTIONS_TIMEOUT=300` y `EXECUTIONS_TIMEOUT_MAX=600` en el environment del servicio `n8n` de `docker-compose.yml`.
  - Nuevo `scripts/preflight/cost_readiness.py` (+ tests) que verifica 10 guardas en `n8n/workflow.json` y `docker-compose.yml`, reporta PASS/FAIL y sale no-cero si falta una guarda; sin red ni Docker.
  - Gate de corrida paga en `evaluation/run_evaluation.py`: exige `--confirm-paid` o `EVALUATION_CONFIRM_PAID`, imprime estimacion de costo y rechaza por defecto sin cache valido.
  - Test de regresion en `test_n8n_workflow.py`: ningun nodo pago habilita `retryOnFail`/`maxTries`.
  - Actualizar `docs/por_implementar.md` y `openspec/config.yaml` (N8N 2.11.2).
- **Dependencias**: `C-33`, `C-34`
- **Governance**: ALTO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-17-c-36-credentialing-readiness/proposal.md`
  - `openspec/changes/archive/2026-09-17-c-36-credentialing-readiness/design.md`

### [C-37] `secret-hardening`

- **Estado**: `[x]` completado (2026-09-18 — `openspec/changes/archive/2026-09-18-c-37-secret-hardening`; postura de escaneo de secretos repetible y auditable para el repositorio publico)
- **Scope**:
  - Nueva capacidad `secret-hygiene`: contrato verificable del hook pre-commit, el escaneo del lado de GitHub (secret scanning + push protection), el triaje/resolucion de alertas y el runbook de rotacion.
  - Delta de `local-bootstrap`: credenciales de desarrollo local parametrizadas por variables de entorno, sin defaults trivialmente adivinables en archivos versionados.
  - Nuevo runbook `docs/security-hardening.md` (configuracion API vs UI, push protection, triaje de alertas y rotacion con la filtracion de Gemini como caso de estudio).
  - Nuevo `scripts/security/configure_github_secret_scanning.sh` idempotente que habilita lo API-settable e imprime los pasos solo-UI; resolucion de alerta opt-in con confirmacion.
  - Tareas operativas: habilitar patrones no-proveedor y verificaciones de validez, resolver la alerta #1 como `revoked` y verificar el estado final.
- **Dependencias**: ninguna
- **Governance**: CRITICO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-18-c-37-secret-hardening/proposal.md`
  - `openspec/changes/archive/2026-09-18-c-37-secret-hardening/design.md`

### [C-38] `n8n-confidence-gate`

- **Estado**: `[x]` completado (2026-09-18 — `openspec/changes/archive/2026-09-18-c-38-n8n-confidence-gate`; spec `n8n-workflow` sincronizada con el gate de dos capas de `5efce4b`)
- **Scope**:
  - Formalizar la compuerta de dos capas: `Entrada valida` pre-POST (validacion de entrada con `confianza >= 0.70 OR revision_forzada == true`) y `Requiere revision humana` post-POST sobre el flag del backend.
  - Documentar la rama verdadera: notificacion al operador designado via `$env.OPERATOR_EMAIL` (nodo `Notificar operador designado`) y registro de auditoria; para correo, ademas marca el mensaje como leido.
  - Documentar la rama falsa (confirmaciones por canal) y que los nodos HTTP resuelven el host del backend con `$env.BACKEND_URL`, sin host hardcodeado.
  - Actualizar el requerimiento "Ruteo por umbral de confianza" y agregar "Notificacion al operador designado" y "URLs del backend configurables por entorno" en la spec `n8n-workflow`.
- **Dependencias**: `C-30`, `C-33`
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-18-c-38-n8n-confidence-gate/proposal.md`
  - `openspec/changes/archive/2026-09-18-c-38-n8n-confidence-gate/design.md`
  - `knowledge-base/05_reglas_de_negocio.md`

### [C-39] `e2e-timing-instrumentation`

- **Estado**: `[x]` completado y verificado (2026-09-20 — `openspec/changes/archive/2026-09-20-c-39-e2e-timing-instrumentation`; 21/21 tareas, 431 passed offline y 22 passed en el subconjunto PostgreSQL de integracion)
- **Scope**:
  - Nuevo contrato temporal por incidente: `ingresado_en`, `persistido_en` y `latencia_e2e_ms` derivada.
  - Backend: `IncidenteCreate` acepta `ingresado_en` (ISO-8601 con zona); migracion Alembic 006 aditiva agrega columnas `ingresado_en` y `persistido_en`; `IncidenteRead` expone ambos instantes y la latencia.
  - N8N: captura `ingresado_en` en el borde de cada trigger (en telefonia, antes del `AI Agent`) y lo envia en el body del POST a `/api/v1/incidentes/`.
  - Contrato de medicion documentado: definicion de ingreso y persistencia confirmada, unidades (ms), caveats por canal y exclusion de replays idempotentes.
  - Tests unitarios de schema/servicio, de migracion y estructurales del workflow N8N.
- **Dependencias**: `C-33`, `C-32`
- **Governance**: ALTO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-20-c-39-e2e-timing-instrumentation/proposal.md`
  - `openspec/changes/archive/2026-09-20-c-39-e2e-timing-instrumentation/design.md`
  - `openspec/changes/archive/2026-09-20-c-39-e2e-timing-instrumentation/verify-report.md`
  - `knowledge-base/11_evaluacion_experimental.md`

### [C-40] `n8n-wiring-fixes`

- **Estado**: `[x]` completado y verificado (2026-09-20 — `openspec/changes/archive/2026-09-20-c-40-n8n-wiring-fixes`; 21/21 tareas, suite estructural N8N 129 passed + 1 xfailed y 431 passed en el subconjunto offline)
- **Scope**:
  - WEB DEAD-END: agregar el guard `Es web?` y el nodo `respondToWebhook` de cierre, alcanzable desde rechazo de validacion, error del backend y revision humana.
  - EMAIL CONFIRMATION RECIPIENT: propagar el remitente original como `remitente` en la estructura normalizada y resolver `toRecipients` desde el nodo normalizador aguas arriba.
  - TELEPHONY MIS-ROUTE: quitar las salidas telefonia/fallback del switch hacia `Correo de confirmacion al usuario`; la confirmacion telefonica queda en la respuesta TwiML.
  - REDIS MEMORY: declarar la credencial `redis` y parametros de sesion no vacios en `memoryRedisChat`, extendiendo la lista de tipos que requieren credenciales de la suite estructural.
  - DUPLICATE AUTHORIZATION / AUDIT: dejar un unico mecanismo de autenticacion en el POST de persistencia, cablear `Registro de auditoria` en la salida de error y usar `onError: continueRegularOutput` en la notificacion.
  - DOC DRIFT: sincronizar `docs/n8n-workflow-guide.md` (conteo de nodos, tests y excepcion obsoleta) con el workflow real.
- **Dependencias**: `C-39`
- **Governance**: ALTO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-20-c-40-n8n-wiring-fixes/proposal.md`
  - `openspec/changes/archive/2026-09-20-c-40-n8n-wiring-fixes/design.md`
  - `openspec/changes/archive/2026-09-20-c-40-n8n-wiring-fixes/verify-report.md`

### [C-41] `cost-preflight-wiring`

- **Estado**: `[x]` completado y verificado (2026-09-20 — `openspec/changes/archive/2026-09-20-c-41-cost-preflight-wiring`; 15/15 tareas, 61 assertions del harness, 26 passed del preflight y `10/10 guardas en PASS`)
- **Scope**:
  - Cablear `scripts/preflight/cost_readiness.py` al arranque local desde `scripts/up.sh` antes de tocar Docker, con aborto no destructivo, resumen de guardas en FAIL y exit code distinto de cero.
  - Paridad Windows en `scripts/up.ps1` con el mismo gate.
  - Agregar `JWT_SECRET_KEY` a la lista de secretos requeridos del preflight de entorno (presencia, no vacio, no placeholder) en ambos scripts.
  - Objetivo `preflight` en el `Makefile` para invocacion manual discoverable (solo lectura, sin Docker ni red).
  - CI `backend-tests` instala `scripts/preflight/requirements.txt` y ejecuta la suite mas el CLI del preflight, cerrando el follow-up de C-36.
  - Extender `scripts/tests/test_up_preflight.sh` con los casos de JWT y un stub del gate que prueba falla -> no arranca y pasa -> continua; bypass `UP_SKIP_COST_PREFLIGHT=1`.
- **Dependencias**: `C-36`
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-20-c-41-cost-preflight-wiring/proposal.md`
  - `openspec/changes/archive/2026-09-20-c-41-cost-preflight-wiring/design.md`
  - `openspec/changes/archive/2026-09-20-c-41-cost-preflight-wiring/verify-report.md`

---

## FASE 15 — Sincronizacion documental

> C-42 alinea la documentacion operativa con el arranque de la Fase 1. C-43 cierra la
> deuda de rutas post-reestructuracion y completa la documentacion de `JWT_SECRET_KEY`.

### [C-42] `bootstrap-docs-sync`

- **Estado**: `[x]` completado, verificado y archivado (2026-09-20 — `openspec/changes/archive/2026-09-20-c-42-bootstrap-docs-sync`; 15/15 tareas, 6 tests estructurales, 437 passed)
- **Scope**:
  - Alinear `README.md` y `docs/operational-guide.md` con el arranque de Fase 1: el preflight de entorno ahora exige `JWT_SECRET_KEY`; documentar el gate de costo y el bypass `UP_SKIP_COST_PREFLIGHT=1`; presentar el comando unico (`scripts/up.sh` / `make up`) como camino recomendado en la guia operativa, preservando el camino manual.
  - Test estructural `App/Backend/tests/test_docs_bootstrap_sync.py`.
- **Dependencias**: `C-39`, `C-40`, `C-41`
- **Governance**: BAJO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-20-c-42-bootstrap-docs-sync/proposal.md`
  - `openspec/specs/local-bootstrap/spec.md`
  - `openspec/specs/cost-readiness/spec.md`

### [C-43] `docs-restructure-sync`

- **Estado**: `[x]` completado, verificado y archivado (2026-09-21 — `openspec/changes/archive/2026-09-21-c-43-docs-restructure-sync`; 24/24 tareas, 20 tests estructurales nuevos, 457 passed, 32/32 specs validos)
- **Scope**:
  - Cerrar la deuda de rutas post-reestructuracion (c-24 movio el modulo de `Gestion_Incidentes/` a `App/Backend/`): reemplazar las referencias obsoletas en `docs/operational-guide.md`, `docs/troubleshooting.md`, `docs/como_cargar_datos_corpus.md`, `docs/diagrams/componentes.md`, `docs/parameters_gemini.md`, `docs/pseudonymization.md` y `docs/anexo_c_esquema_bd.md`, verificando cada destino contra el repo real.
  - Preservar y anotar la narrativa historica de `docs/security-hardening.md` (el archivo estaba realmente en `Gestion_Incidentes/.env`); el hecho no se reescribe.
  - Completar la documentacion de entorno: agregar `JWT_SECRET_KEY` (clave de firma HS256) a la tabla de variables del `README.md` y al bloque dotenv de la seccion 1.2 de `docs/operational-guide.md`.
  - Test estructural `App/Backend/tests/test_docs_restructure_sync.py` con control negativo del token obsoleto.
  - Fuera de alcance: `docs/Tesis/**` y el docstring de `App/Backend/scripts/export_openapi.py` (queda como observacion para un change de scripts).
- **Dependencias**: `C-42`
- **Governance**: BAJO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-21-c-43-docs-restructure-sync/proposal.md`
  - `openspec/specs/project-documentation/spec.md`
  - `docs/operational-guide.md`

### [C-44] `docs-evaluation-sync`

- **Estado**: `[x]` completado, verificado y archivado (2026-09-21 — `openspec/changes/archive/2026-09-21-c-44-docs-evaluation-sync`; 25/25 tareas, 12 tests estructurales/funcionales, 469 passed, 32/32 specs validos)
- **Scope**:
  - Corregir `docs/operational-guide.md` §8.1: invocacion real del runner `PYTHONPATH=App/Backend python -m evaluation.run_evaluation` (antes `cd evaluation; python run_evaluation.py`, que no resolvia los imports).
  - Eliminar la §8.3 muerta (`evaluation/generate_corpus.py`, eliminado por C-27) y reemplazarla por un puntero a `docs/como_cargar_datos_corpus.md`.
  - Documentar el gate de corrida paga (`--confirm-paid` / `EVALUATION_CONFIRM_PAID=1`, aborto con exit 2, estimacion de costo) en la guia §8 y en `evaluation/README.md`.
  - **Bugfix**: `App/Backend/scripts/export_openapi.py` no inyectaba dummy de `JWT_SECRET_KEY` (obligatoria en `Settings`), por lo que fallaba en entorno limpio; se corrige el dummy y el docstring (rutas `Gestion_Incidentes` → `App/Backend`, ejemplo `--output`).
  - Eliminar el `cd evaluation` engañoso en `docs/como_cargar_datos_corpus.md` §8 (invocacion del runner).
  - Fuera de alcance: `docs/anexo_f_corpus.md` (historico correcto), `docs/Tesis/**`, el runtime de evaluacion (se documenta el gate, no se cambia).
- **Dependencias**: `C-43`
- **Governance**: BAJO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-21-c-44-docs-evaluation-sync/proposal.md`
  - `openspec/specs/project-documentation/spec.md`
  - `openspec/specs/evaluation-framework/spec.md`

---

## FASE 16 — Guarda de costo en runtime

> C-45 acota el gasto pago en runtime (Gemini del backend, Gemini del `AI Agent` de n8n y
> transcripcion de Twilio) con presupuesto global semanal, rate limit y degradacion segura.
> Cierra el riesgo real de perdida de dinero al activar credenciales pagas reales.

### [C-45] `runtime-cost-guard`

- **Estado**: `[x]` completado, verificado y archivado (2026-09-21 — `openspec/changes/archive/2026-09-21-c-45-runtime-cost-guard`; 86/86 tareas, 72 tests de la guarda, 545 passed offline, ruff clean, 34/37 escenarios compliant y 0 failing; integracion PostgreSQL 25 passed con la deriva de password del volumen documentada)
- **Scope**:
  - Bolsa GLOBAL compartida de USD 10/semana (ventana tumbling 604800 s, configurable) sobre las TRES superficies pagas: Gemini del backend, Gemini del `AI Agent` de n8n y transcripcion de Twilio; costo unitario por superficie (estimaciones configurables, ajustables por el operador).
  - Rate limit global (30/h) y por origen (3/h), este ultimo indexado por el numero de telefono llamante (logueado CRUDO para anti-abuso inicial, explicitamente EXCLUIDO del corpus de la tesis).
  - Almacen PostgreSQL: tabla `costo_guarda_contador` con migracion Alembic 007; reserva atomica en transaccion propia (`INSERT ... ON CONFLICT ... RETURNING`) con rollback cuando la decision deniega.
  - Puntos de enforcement: backend antes de Gemini (`HybridClassifier`); endpoint `/api/v1/cost-guard/reserve` para n8n (nodo `Guard de costo`); webhook de voz pre-llamada de Twilio `/api/v1/cost-guard/twilio/voice` que devuelve TwiML (`<Record transcribe="true">` permite / `<Say>`+`<Hangup>` deniega).
  - Auth: `X-Cost-Guard-Secret` obligatorio en `/reserve` (cableado en n8n via `COST_GUARD_SHARED_SECRET`, fuente unica en `docker-compose.yml`); `X-Twilio-Signature` (HMAC-SHA1) obligatorio en `/twilio/voice` cuando `TWILIO_AUTH_TOKEN` esta configurado, con 401 fail-closed sin token.
  - Degradacion: deterministico + `requiere_revision_humana=True` (nunca invoca al proveedor pago); politica `hard_block` disponible. Fail-closed con notificacion estructurada (`cost_guard_tripped`, `cost_guard_store_unavailable`, `cost_guard_twilio_token_missing`).
  - Default conservador habilitado con override por `.env`; postura efectiva registrada al arranque.
  - Docs: `README.md`, `docs/operational-guide.md` (§11), `docs/n8n-workflow-guide.md`; firma Twilio valida con `FORWARDED_ALLOW_IPS=*` detras del Nginx del compose (backend sin puerto publicado).
  - Limitaciones conocidas documentadas: campo de transcripcion del evento `call-summary.complete` de Twilio sin verificar (fallback hardcodeado en el workflow); subconjunto de integracion no re-ejecutable en hosts con deriva de password del volumen.
- **Dependencias**: `C-41` (preflight de costo), `C-33` (cost-guards)
- **Governance**: ALTO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-21-c-45-runtime-cost-guard/proposal.md`
  - `openspec/changes/archive/2026-09-21-c-45-runtime-cost-guard/design.md`
  - `openspec/changes/archive/2026-09-21-c-45-runtime-cost-guard/verify-report.md`
  - `openspec/specs/runtime-cost-guard/spec.md`

---

## FASE 17 — Fidelidad de medicion del pipeline

> La Fase 2 del pipeline ataca la fidelidad de la medicion (no el costo) y se divide en
> changes chicos (C-46 a C-50). C-46 cierra la perdida silenciosa del sello de ingreso de
> telefonia a traves del `AI Agent`.

### [C-46] `telefonia-ingreso-sellado`

- **Estado**: `[x]` completado, verificado y archivado (2026-09-22 — `openspec/changes/archive/2026-09-22-c-46-telefonia-ingreso-sellado`; 13/15 tareas, 2 pendientes manuales documentadas; 5/5 scenarios compliant; 134 passed + 1 xfailed en la suite N8N, 550 passed offline, 33/33 specs validos)
- **Scope**:
  - Recuperar el sello `ingresado_en` con `$('Sellar ingreso telefonia').first()` (no `.item`) en `Se verifica lo que trajo la IA` y en `Derivar a revision humana`, eliminando la dependencia de `pairedItem` que devolvia `null` en silencio cuando el item provenia del `AI Agent` (desviacion HIGH #3 de C-39).
  - Ante sello irresoluble: WARN estructurado + `revision_forzada=true` + `requiere_revision_humana=true`, conservando la creacion del ticket (nunca aborta ni pierde el incidente).
  - Suite estructural extendida en `test_n8n_workflow.py` (5 scenarios del requerimiento `N8N-TIMING-003`); `docs/n8n-workflow-guide.md` actualizado. Backend sin cambios.
- **Pendiente documentado**: verificacion manual en N8N en vivo (tareas 5.2/5.3) — no bloqueante, aprobado dejarla pendiente.
- **Dependencias**: `C-39` (instrumentacion temporal), `C-45` (guarda de costo)
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-22-c-46-telefonia-ingreso-sellado/verify-report.md`
  - `openspec/specs/n8n-workflow/spec.md` (N8N-TIMING-003)
  - `openspec/changes/archive/2026-09-20-c-39-e2e-timing-instrumentation/verify-report.md` (desviacion HIGH #3)

### [C-47] `guard-costo-item`

- **Estado**: `[x]` completado, verificado y archivado (2026-09-22 — `openspec/changes/archive/2026-09-22-c-47-guard-costo-item`; 16/17 tareas, 1 pendiente manual no bloqueante; 5/5 scenarios compliant; 140 passed + 1 xfailed en la suite N8N, 556 passed offline, 33/33 specs validos; verify PASS WITH WARNINGS)
- **Scope**:
  - Nuevo nodo `code` `Restaurar item telefonia` entre `Guard de costo` y `Guard permite?`: recupera el item sellado con `$('Sellar ingreso telefonia').first()` (patron C-46) y le re-inyecta la decision `allowed`, de modo que el `AI Agent` vuelve a recibir el item sellado (no solo el cuerpo de la guarda) y el IF conserva el ruteo por `$json.allowed`.
  - `caller` del body de `Guard de costo`: del `.item` fragil (`n8n/workflow.json:779`) al item corriente (`$json.From || $json.from`), sin referencia cruzada entre nodos.
  - Suite estructural extendida en `test_n8n_workflow.py` (6 tests: N8N-GUARD-001/002); adaptacion minima del assert de C-45 en `test_runtime_cost_guard.py`; `docs/n8n-workflow-guide.md` sincronizada (35 nodos, 141 propiedades). Backend sin cambios.
- **Alcance acotado (hallazgo del verify)**: la descripcion del canal telefonico sigue vacia porque el payload del trigger `com.twilio.voice.insights.call-summary.complete` NO expone la transcripcion (limitacion heredada de C-45). C-47 garantiza la propagacion del item; el gap real (entrega de la transcripcion + `caller`) se rastrea en un change aparte (ver "Primer change recomendado").
- **Pendiente documentado**: verificacion manual en N8N en vivo (tarea 5.4) — no bloqueante.
- **Dependencias**: `C-46` (mismo nodo terminal `Derivar a revision humana`), `C-45` (guarda de costo)
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-22-c-47-guard-costo-item/verify-report.md`
  - `openspec/specs/n8n-workflow/spec.md` (N8N-GUARD-001, N8N-GUARD-002)
  - `openspec/changes/archive/2026-09-21-c-45-runtime-cost-guard/design.md` (limitacion de la transcripcion)

### [C-48] `timing-en-listado`

- **Estado**: `[x]` completado, verificado y archivado (2026-09-22 — `openspec/changes/archive/2026-09-22-c-48-timing-en-listado`; 20/20 tareas; verify READY TO ARCHIVE; 566 passed offline, ruff limpio, `openspec validate --strict` pasa)
- **Scope**: `IncidenteListItem` expone `ingresado_en`, `persistido_en`, `latencia_e2e_ms` y `latencia_anomala`, con paridad exacta respecto de `IncidenteRead` (derivacion extraida a funciones puras compartidas). `docs/openapi.json` regenerado (cambio aditivo). Sin cambios en repositorio, rutas, modelos, migraciones ni n8n. Cierra la desviacion #2 de C-39.
- **Dependencias**: `C-39` (instrumentacion temporal)
- **Governance**: BAJO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-22-c-48-timing-en-listado/verify-report.md`
  - `openspec/specs/e2e-timing-instrumentation/spec.md`

## FASE 18 — Notificacion, directorio y canal de correo (2026-09-23 / 2026-09-25)

> Changes post-roadmap. C-52 continua el pipeline telefonico asincrono; C-53 entrega el numero de incidente en los tres canales; C-54 agrega el directorio de empleados; C-55 migra el canal de correo a IMAP/SMTP. C-52 (2026-09-30), C-53 (2026-10-01), C-54 (2026-10-01, 51/51) y C-55 (2026-09-29) ya estan ARCHIVADOS; la FASE 18 queda CERRADA.

### [C-52] `telefonia-transcripcion-async` — ARCHIVADO (2026-09-30, 44/44)

- **Estado**: `[x]` completado y archivado (2026-09-30 — `openspec/changes/archive/2026-09-30-c-52-telefonia-transcripcion-async`; 44/44 tareas). Absorbe el change cancelado `c-51-twilio-payload-wiring`.
- **Problema**: el canal de telefonia clasifica sobre una descripcion VACIA. El evento `com.twilio.voice.insights.call-summary.complete` no trae la transcripcion, y `<Record transcribe="true">` es solo ingles estadounidense. Ademas hay una fuga latente de PII (el `AI Agent` de n8n manda el transcript crudo a Gemini antes de pseudonimizar).
- **Scope**:
  - STT EN EL BACKEND con Google Gemini (transcripcion dedicada, modelo `gemini-3.5-transcribe`, modo `verbatim`, via Interactions API, `store=False`) sobre la grabacion mono de Twilio. El backend es dueno de la descarga (`RecordingUrl`, Basic auth) y de la transcripcion; pseudonimiza INMEDIATAMENTE y entrega SOLO texto pseudonimizado a n8n.
  - TwiML: `<Record>` mono con `recordingStatusCallback` + `action`, sin `transcribe`; se corrige el `<Say>` post-grabacion (hoy inalcanzable).
  - Tabla `telefonia_ingreso` (transcript crudo cifrado Fernet + pseudonimizado), migracion Alembic `008`.
  - Nueva superficie paga `backend_stt` en la guarda de costo; `ingresado_en` sellado en el callback del backend; `origen_message_id = CallSid` para idempotencia.
  - n8n: el `twilioTrigger` se reemplaza por un webhook; sobreviven guarda/restauracion/agente/validador/normalizador.
- **Preguntas abiertas (estado al proponer; 1-3 resueltas)**: (1) `google-genai==2.8.0` no tipa `transcription_config` (upgrade vs dict sin tipar vs REST con httpx); (2) disponibilidad y precio real de `gemini-3.5-transcribe`; (3) si `language_codes=["es-AR"]` se acepta (fallback auto-detect o `es-MX`); (4) retencion del audio; (5) alta placeholder vs reintento ante fallo de STT; (6) drop de la suscripcion Event Streams; (7) reescritura del `<Say>`.
- **Dependencias**: `C-47` (mismo flujo telefonico), `C-45` (guarda de costo)
- **Governance**: CRITICO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-30-c-52-telefonia-transcripcion-async/{proposal,design,tasks}.md`
  - `openspec/specs/n8n-workflow/spec.md`, `openspec/specs/runtime-cost-guard/spec.md`
  - `openspec/changes/archive/2026-09-21-c-45-runtime-cost-guard/design.md` (limitacion de la transcripcion)

---

### [C-53] `notificacion-numero-incidente` — ARCHIVADO (2026-10-01, 12/12)

- **Estado**: `[x]` completado y archivado (2026-10-01 — `openspec/changes/archive/2026-10-01-c-53-notificacion-numero-incidente`; 12/12 tareas). Se archivo el alcance implementado (numero canonico, correo y web); el alcance SMS diferido se movio a `C-67`, bloqueado por OQ3 (entregabilidad SMS AR) y por `C-66` (privacidad-transferencias, que se creo y archivo despues, 2026-10-19); `C-67` quedo CERRADO NO REALIZADO y archivado el 2026-10-19 (`--skip-specs`).
- **Problema**: el usuario final no recibe de forma garantizada el numero de incidente. El correo no confirma cuando `requiere_revision_humana=true` y su destinatario puede resolverse invalido (el `from` de Outlook es tipicamente un objeto `from.emailAddress.address`); el web responde `incidente_id: null` en revision humana; la telefonia no notifica (el `<Say>` de cierre no conoce el numero porque el alta es asincrona). No existe numero legible de incidente (solo el PK `id`).
- **Scope**:
  - Telefonia: SMS al numero llamante con el numero de incidente via Twilio Messaging; captura y persistencia cifrada del `From` en el webhook de VOZ (correlacion por `CallSid`); sin numero no se envia y se deja traza. Superficie de guarda nueva `twilio_sms`. (Diferido: este alcance SMS se movio a `C-67`, cerrado NO REALIZADO y archivado el 2026-10-19; los specs principales no se tocaron.)
  - Correo: extraccion del remitente soportando `from` string y objeto `from.emailAddress.address`; confirmacion tambien en la rama de revision humana.
  - Web: la rama de revision humana responde con el `incidente_id` real (no `null`).
  - Numero de incidente: PK `id` como numero canonico (prefijo configurable diferido).
  - Doc fix en `docs/n8n-workflow-guide.md`.
- **Dependencias**: `C-52` (flujo telefonico asincrono), `C-45` (guarda de costo)
- **Governance**: ALTO
- **Leer antes**:
  - `openspec/changes/archive/2026-10-01-c-53-notificacion-numero-incidente/{proposal,design,tasks}.md`
  - `openspec/specs/n8n-workflow/spec.md`, `openspec/specs/runtime-cost-guard/spec.md`

---

### [C-54] `directorio-usuarios` — ARCHIVADO (2026-10-01, 51/51)

- **Estado**: `[x]` completado y archivado (2026-10-01 — `openspec/changes/archive/2026-10-01-c-54-directorio-usuarios`; 51/51 tareas). La tarea 7.5 (revision humana HIGH: politica de retencion/ARCO, visibilidad de incidentes por rol y ausencia de PII) quedo resuelta y aprobada; la profundizacion del endurecimiento se continua en `C-60`. La implementacion uso datos sinteticos.
- **Problema**: la mesa de ayuda no sabe QUIEN reporta ni a QUIEN avisar; no existe directorio de empleados ni modelo de roles (`users` es solo autenticacion).
- **Scope**:
  - Entidad `directorio_empleado` (migracion 009), separada de `users`, con vinculo opcional a una cuenta.
  - Modelo de roles minimo (`usuario_final` / `operador` / `administrador_directorio`) vinculado al catalogo `sector` canonico.
  - Resolucion de contactos (telefono -> empleado, email -> empleado, usuario -> empleado); "no encontrado" no fatal.
  - Datos personales en texto plano (sin cifrado de aplicacion ni indice ciego) con minimizacion, control de acceso por rol, auditoria y sin PII en logs.
  - Visibilidad de incidentes por rol a nivel API (frontend diferido).
  - Seed idempotente dev-only con un usuario sintetico por rol (sin PII real).
- **Dependencias**: `C-53` (contrato de resolucion de contacto; no implementa notificaciones aqui)
- **Governance**: ALTO
- **Leer antes**:
  - `openspec/changes/archive/2026-10-01-c-54-directorio-usuarios/{proposal,design,tasks}.md`
  - `App/Backend/app/models/empleado.py`, `openspec/specs/employee-directory/spec.md`

---

### [C-55] `canal-correo-imap` — ARCHIVADO (2026-09-29, 15/15)

- **Estado**: `[x]` completado y archivado (2026-09-29 — `openspec/changes/archive/2026-09-29-c-55-canal-correo-imap`; 15/15 tareas; migracion del canal de correo ejecutada y con smoke sobre casilla Gmail real).
- **Problema**: el canal de correo depende de Microsoft Entra OAuth2 (`microsoftOutlookTrigger`, `microsoftOutlook`, credencial `microsoftOutlookOAuth2Api`), via no provisionable: la cuenta Microsoft disponible es personal y sin tenant.
- **Scope**:
  - Migrar el trigger a `n8n-nodes-base.emailReadImap` (IMAP Gmail: `imap.gmail.com:993`, `UNSEEN` + `SINCE`/24 h, `postProcessAction=read`, `format=simple`).
  - Reemplazar los nodos `microsoftOutlook` de envio por `emailSend` (SMTP `smtp.gmail.com:465`).
  - `origen_message_id` desde `metadata['message-id']` con fallback a `attributes.uid`; `canal_raw="correo"`.
  - Eliminar `Marcar correo como leido` y rewiring (conteo 37 nodos).
  - Migrar las guardas de `scripts/preflight/` y actualizar `docs/n8n-workflow-guide.md`.
- **Dependencias**: ninguna
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-29-c-55-canal-correo-imap/{proposal,design,tasks}.md`
  - `openspec/specs/n8n-workflow/spec.md`, `docs/n8n-workflow-guide.md`

---

## FASE 19 — Endurecimiento, auditoria y herramientas (2026-09-28 / 2026-09-30)

> Changes post-roadmap que endurecen el directorio y las notificaciones, corrigen la auditoria de la rama de revision, agregan resiliencia a Gemini y suman una herramienta de pruebas de telefonia. C-57 y C-58 estan ARCHIVADOS (2026-09-29) y C-59 quedo ARCHIVADO (2026-10-01); C-56 quedo APLICADO y ARCHIVADO (2026-10-08, 27/27; verify PASS con el smoke manual confirmado) y C-60 quedo ARCHIVADO (33/33, 2026-10-06; aprobacion humana HIGH 7.4 pendiente).

### [C-56] `notificaciones-por-rol` — ARCHIVADO (2026-10-08, 27/27)

- **Estado**: `[ ]` propuesto (2026-09-28) — planning completo (proposal, specs, design, tasks), `openspec validate --strict` pasa. Sin aplicar.
- **Problema**: el destinatario de la notificacion de revision humana esta fijado en N8N como una unica casilla (`$env.OPERATOR_EMAIL`). Aunque c-54 creo un directorio con roles y sector, nadie lo usa para enrutar; con mas de un operador no se puede avisar al operador del sector correcto.
- **Scope**:
  - El backend resuelve los destinatarios de la notificacion de revision desde `directorio_empleado`: empleados activos con `rol=operador` cuyo sector coincide con el sector predicho principal del incidente.
  - La respuesta de alta (`POST /api/v1/incidentes`) expone `destinatarios_revision` (lista de emails), poblada solo cuando `requiere_revision_humana=true`.
  - N8N `Preparar destinatarios de revision` (Code) emite un item por destinatario y `Notificar operador designado` envia una copia a cada uno; si la lista llega vacia, cae al fallback `$env.OPERATOR_EMAIL` (un unico destinatario). Un correo por destinatario, nunca `To`/`Cc` compartido.
  - Fire-and-forget intacto: la resolucion es una lectura indexada acotada al caso de revision; sin migracion Alembic (reutiliza el directorio de c-54).
- **Dependencias**: `C-54` (directorio, roles, sector y seam de resolucion), `C-55` (nodos `emailSend`/SMTP del operador), `C-53` (numero de incidente), `C-38` (gate `Requiere revision humana`)
- **Governance**: ALTO
- **Leer antes**:
  - `openspec/changes/c-56-notificaciones-por-rol/{proposal,design,tasks}.md`
  - `knowledge-base/05_reglas_de_negocio.md`, `knowledge-base/06_funcionalidades.md`
  - `openspec/specs/n8n-workflow/spec.md`, `docs/n8n-workflow-guide.md`

---

### [C-57] `auditoria-rama-revision` — ARCHIVADO (2026-09-29, 15/15)

- **Estado**: `[x]` completado y archivado (2026-09-29 — `openspec/changes/archive/2026-09-29-c-57-auditoria-rama-revision`; 15/15 tareas; spec `n8n-workflow` sincronizada).
- **Problema**: el smoke de c-55 creo el incidente #9, pero `Registro de auditoria` quedo con `incidente_id: null` y `resultado: rechazado_datos_incompletos`. Causa raiz de cableado: en la rama de revision la auditoria era sucesora de `Notificar operador designado`, por lo que recibia el resultado SMTP (sin `id`) en vez de la respuesta del POST.
- **Scope**:
  - Rewiring: agregar `Requiere revision humana[main#0] -> Registro de auditoria` y quitar `Notificar operador designado[main#0] -> Registro de auditoria`; la notificacion queda terminal y la auditoria en paralelo (un fallo de notificacion no la omite).
  - Sin cambios al `jsCode`: con el item correcto ya distingue `creado` / `rechazado_datos_incompletos` / `error_backend`.
  - Tests estructurales: invertir las dos aserciones que fijaban la arista SMTP->auditoria y agregar las de la nueva topologia e independencia del item SMTP; actualizar `docs/n8n-workflow-guide.md`.
- **Dependencias**: ninguna nueva (se apoya en el gate post-POST y en `Notificar operador designado` de c-55)
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-29-c-57-auditoria-rama-revision/{proposal,design,tasks}.md`
  - `openspec/specs/n8n-workflow/spec.md` (N8N-AUDIT-001/003/004)

---

### [C-58] `resiliencia-gemini` — ARCHIVADO (2026-09-29, 33/33)

- **Estado**: `[x]` completado y archivado (2026-09-29 — `openspec/changes/archive/2026-09-29-c-58-resiliencia-gemini`; 33/33 tareas; specs `classification-resilience`, `runtime-cost-guard`, `n8n-workflow` y `cost-readiness` sincronizadas).
- **Problema**: un `HTTP 503` transitorio de `gemini-3.6-flash` hacia que la clasificacion cayera a `etapa=fallback` porque `GeminiClassifier.classify` hace un solo intento y trata la falla transitoria como dura. El canal telefonico tenia el mismo hueco (el `AI Agent` abortaba ante error del sub-nodo y el nodo de modelo ni fijaba `modelName`).
- **Scope**:
  - Reintento acotado propio en `GeminiClassifier` (backoff exponencial + jitter) SOLO para fallas transitorias (503/429/5xx y timeouts); los errores terminales (400/401/403, JSON invalido) no se reintentan. Se desactiva el auto-retry del SDK para tener una unica fuente de politica.
  - Nuevas settings `gemini_max_retries` / `gemini_retry_*` / `gemini_total_timeout_seconds` con defaults seguros; presupuesto total de latencia.
  - Guarda de costo: UNA reserva por clasificacion dimensionada al peor caso (`amount = gemini_max_retries + 1`); los reintentos no reservan de nuevo.
  - N8N: `modelName` explicito en `Google Gemini Chat Model` (paridad con `settings.gemini_model`) + reintento acotado del `AI Agent`, reconciliado con N8N-REFINE-001; preflight `gemini_readiness` estatico y reforma de la guarda de reintentos de nodos pagos.
- **Dependencias**: specs compartidas con `C-33` (cost-guards), `C-36` (credentialing-readiness) y `C-45` (runtime-cost-guard); sin dependencia nueva de changes
- **Governance**: ALTO
- **Leer antes**:
  - `openspec/changes/archive/2026-09-29-c-58-resiliencia-gemini/{proposal,design,tasks}.md`
  - `openspec/specs/classification-resilience/spec.md`, `openspec/specs/runtime-cost-guard/spec.md`
  - `docs/n8n-workflow-guide.md`

---

### [C-59] `softphone-voip-pruebas` — ARCHIVADO (2026-10-01, 23/23)

- **Estado**: `[x]` completado y archivado (2026-10-01 — `openspec/changes/archive/2026-10-01-c-59-softphone-voip-pruebas`; 23/23 tareas).
- **Problema**: el canal telefónico no se puede probar de forma barata ni repetible: llamar al número Twilio de EE. UU. desde un celular argentino factura tarifa internacional, y la auto-llamada entre números de la MISMA cuenta Twilio está bloqueada (`21216`). El "truco" Twilio-a-Twilio con TTS no es viable.
- **Scope**:
  - Herramienta standalone de desarrollo en `scripts/voip_softphone/`: softphone VoIP de navegador (Twilio Voice SDK sobre WebRTC) que inyecta la voz del operador en el pipeline telefónico existente (`From = client:<identity>`, audio `client`, sin tramo PSTN ni auto-llamada).
  - Acuñado local del Access Token de Twilio (JWT HS256 con `VoiceGrant`) con secretos EXCLUSIVAMENTE desde variables de entorno; identidad por defecto única por sesión y TTL acotado (defaults D7).
  - Página HTML estática sin pasos de build + servidor local de loopback que sirve la página y un token fresco en el mismo origen (sin CORS).
  - Configuración scriptable de Twilio por CLI (perfil `Luca`): API Key + TwiML App reutilizando `/api/v1/cost-guard/twilio/voice` como Voice URL; el backend de producción NO se modifica.
  - Guía operativa paso a paso como entregable; tests offline de la forma del token y de la validación de configuración.
- **Dependencias**: `C-52` (intake telefónico, archivado 2026-09-30; su defecto de sesión de `memoryRedisChat` ya fue corregido en `4946584`, por lo que el intake es funcional), `C-45` (guarda de costo que el flujo reutiliza)
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-10-01-c-59-softphone-voip-pruebas/{proposal,design,tasks}.md`
  - `knowledge-base/07_flujos_principales.md`, `knowledge-base/08_arquitectura_propuesta.md`
  - `docs/n8n-workflow-guide.md`, `docs/runbook-verificacion-telefonia-c52.md`

---

### [C-60] `directorio-endurecimiento` — ARCHIVADO (2026-10-06, 33/33; aprobacion humana HIGH 7.4 pendiente)

- **Estado**: `[x]` aplicado y ARCHIVADO (2026-10-06; `openspec/changes/archive/2026-10-06-c-60-directorio-endurecimiento`) — 33/33 tareas; verify-report PASS WITH WARNINGS (0 CRITICAL; 33/33 escenarios); specs sincronizadas (`employee-directory` +2/+1, `incident-visibility` +1/+1; 42 specs validan). OQ1..OQ4 RESUELTAS por el autor (todas A); migracion renumerada a `012` (down_revision `011`). Implementado: rol `mesa_de_ayuda` sin sector (modelo + migracion + `_validar_sector_por_rol`), `AlcanceIncidentes` con modos GLOBAL/SECTOR/REVISION/VACIO y `permite_incidente`, cola `revision-pendiente` acotada por rol/sector, purga manual con ids auditados (`POST /directorio/purga`), guardia de entorno solo en el seed, evidencia de cierre 7.5. Suites: 991 offline + 39 integracion; ruff limpio; OpenAPI sincronizado. **PENDIENTE**: aprobacion humana HIGH (tarea 7.4) — activar datos reales sigue bloqueado; implementacion con datos sinteticos, sin PII real.
- **Problema**: c-54 dejo abierto el endurecimiento del directorio, la visibilidad de incidentes y la retencion: la tarea 7.5 (revision humana HIGH) sigue pendiente y bloquea activar datos reales; la purga por retencion registra solo un conteo (sin los ids de lo borrado); la cola `revision-pendiente` es global multi-sector; no existe un rol que cubra la cola de revision; y el seed dev-only no tiene guardia de entorno.
- **Scope**:
  - Purga MANUAL disparada por un operador (`administrador_directorio`, via API y CLI), sin cron/scheduler; el registro incluye los ids de las filas eliminadas (sin datos personales).
  - Acotar `revision-pendiente` por sector/rol; un no administrador solo ve la cola de su sector.
  - Modelo de visibilidad por rol: `administrador_directorio` (ADMIN, ve todo), `mesa_de_ayuda` (rol NUEVO: incidentes sin sector o en revision) y `usuario_final`/`operador` (solo su sector); migracion Alembic append-only `012` (`down_revision = "011"`) que suma `mesa_de_ayuda` al CHECK de `rol`.
  - Guardia de entorno SOLO en el seed (rechaza correr fuera de development/test); cierra las confirmaciones pendientes de c-54 7.5 (retencion/ARCO, visibilidad por rol, ausencia de PII real, sin clave de indice ciego).
- **Dependencias**: `C-54` (directorio, roles y visibilidad base) — prerequisito, ARCHIVADO 2026-10-01; `C-56` (consume roles/sector) — compatible, no bloqueante
- **Governance**: ALTO
- **Leer antes**:
  - `openspec/changes/c-60-directorio-endurecimiento/{proposal,design,tasks}.md`
  - `knowledge-base/05_reglas_de_negocio.md`, `knowledge-base/04_modelo_de_datos.md`
  - `openspec/changes/c-54-directorio-usuarios/design.md`, `docs/directorio-usuarios.md`

---

## FASE 20 — Notificacion SMS diferida (2026-10-01)

> Change post-roadmap que retomaba el alcance SMS del llamante que C-53 dejo diferido al archivarse. Permanecio en estado diferido y nunca se implemento; se archivo el 2026-10-19 como NO REALIZADO.

### [C-67] `notificacion-sms-llamante` — ARCHIVADO (NO REALIZADO, 0/24)

- **Estado**: `[ ]` propuesto y diferido (2026-10-01) — 0/24 tareas; nunca implementado. Dependia de resolver OQ3 (entregabilidad de SMS en Argentina) y de contar con `C-66` (privacidad-transferencias, creado y archivado despues, 2026-10-19). CERRADO Y ARCHIVADO como NO REALIZADO (2026-10-19) con `--skip-specs`; los specs principales no se tocaron.
- **Problema**: el llamante no recibe de forma garantizada el numero de incidente por SMS. C-53 implemento el numero canonico, el correo y el web, pero al archivarse movio aqui el envio por mensajeria, que depende de la entregabilidad real de SMS en Argentina y del marco de privacidad para capturar y cifrar el numero del llamante.
- **Scope**:
  - SMS al llamante con el numero de incidente via Twilio Messaging.
  - Nueva superficie `twilio_sms` en la guarda de costo runtime.
  - Cliente Twilio Messaging dedicado.
  - Captura y cifrado del numero del llamante (persistencia protegida).
  - Servicio de notificacion SMS integrado al alta de incidente.
- **Dependencias**: `C-53` (archivado 2026-10-01; origen del numero canonico y del seam de notificacion); dependia de OQ3 (entregabilidad SMS AR; cerrado 2026-09-23 con veredicto GO-WITH-CONSTRAINTS) y de `C-66` (privacidad-transferencias, creado y archivado despues, 2026-10-19).
- **Governance**: ALTO
- **Leer antes**:
  - `openspec/changes/archive/2026-10-19-c-67-notificacion-sms-llamante/{proposal,design,tasks}.md`
  - `docs/cumplimiento/marco-legal-ar-2026.md`

---

## FASE 21 — Cumplimiento ISO/NIST/Ley 25.326 (totalmente ejecutado)

> Plan de cumplimiento aprobado por el autor el 2026-10-01 para alinear el sistema (lo mas posible) con ISO/IEC 27001:2022 + 27002:2022, ISO/IEC 27701 (privacidad), NIST CSF 2.0 y el marco legal argentino vigente 2026 (Ley 25.326 + AAIP), y asi reforzar la defensa de la tesis. Plan completo en `docs/cumplimiento/plan-cambios-cumplimiento.md`, sobre los informes `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` y `docs/cumplimiento/marco-legal-ar-2026.md`. Regla de lenguaje: se usa "alineado con" / "controles mapeados a"; NO se declara "certificado" ni "compliant". C-61 quedo ARCHIVADO (2026-10-01, 26/26; spec `security-governance-docs`) y C-62 quedo ARCHIVADO (2026-10-08, 33/33; spec `infra-network-hardening` creada + `foundation-environment` modificado). C-63 se separo en `c-63a/b/c` y los tres quedaron ARCHIVADOS (2026-10-08). C-66 quedo CREADO, APLICADO (36/36) y ARCHIVADO (2026-10-19; specs sincronizadas: `privacy-runtime-surface` creada, `runtime-cost-guard`, `security-governance-docs` y `employee-directory` modificadas). C-64 quedo CREADO, APLICADO (33/33) y ARCHIVADO (2026-10-19; specs sincronizadas: `supply-chain-security` creada, `ci-pipeline` y `security-governance-docs` modificadas) y C-65 quedo CREADO, APLICADO (31/31, con revision humana firmada) y ARCHIVADO (2026-10-19; specs sincronizadas: `continuity-planning` creada y `backup-scripts` modificada). Con esto la FASE 21 queda TOTALMENTE EJECUTADA: no quedan changes planificados.

### [C-61] `compliance-gobernanza` — ARCHIVADO (2026-10-01, 26/26)

- **Estado**: `[x]` ARCHIVADO (2026-10-01) — 26/26 tareas. Change archivado en `openspec/changes/archive/2026-10-01-c-61-compliance-gobernanza/`; su spec `security-governance-docs` fue creada. Prioridad 1. Governance MEDIO; habilita C-63.
- **Scope** (D):
  - Politica de seguridad de la informacion; clasificacion y etiquetado de la informacion.
  - Roles y responsabilidades de seguridad (incl. responsable de datos); plan de respuesta a incidentes de seguridad y procedimiento de reporte de eventos.
  - Inventario de activos y registro de requisitos legales; modelado de amenazas; politica de privacidad en runtime; registro de bases (ROPA).
- **Dependencias**: ninguna
- **Governance**: MEDIO
- **Leer antes**:
  - `docs/cumplimiento/plan-cambios-cumplimiento.md` §2-§3
  - `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`
  - `docs/cumplimiento/marco-legal-ar-2026.md`

### [C-62] `hardening-infra-red` — ARCHIVADO (2026-10-08, 33/33)

- **Estado**: `[x]` creado, aplicado (33/33), verificado (PASS, 0 CRITICAL) y ARCHIVADO (2026-10-08; `openspec/changes/archive/2026-10-08-c-62-hardening-infra-red`); spec `infra-network-hardening` creada (INFRA-001..009) + `foundation-environment` modificado (ENV-001). OQ-1..OQ-8 resueltas por el autor (loopback de puertos, Redis retirado, redes edge/data/automation + soporte host_access, nginx endurecido, override `docker-compose.dev.yml`). Incluye el fix de un drift de c-72 en `scripts/preflight/` (el job de CI `backend-tests` estaba en ROJO). Prioridad 2.
- **Scope** (T):
  - Quitar la publicacion al host de los puertos `5433`/`6379`/`5678`; contrasena en Redis; segmentacion de red Docker.
  - Restringir el acceso a la UI de N8N; endurecer nginx.
  - Separar entornos dev/test/prod.
- **Dependencias**: ninguna
- **Governance**: ALTO
- **Leer antes**:
  - `docs/cumplimiento/plan-cambios-cumplimiento.md` §2-§3
  - `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`

### [C-63] `identidad-accesos-claves` — ARCHIVADO (2026-10-08; split en c-63a/b/c)

- **Estado**: `[x]` aplicado, verificado y ARCHIVADO como TRES changes (governance CRITICO cada uno): `c-63a-auth-hardening` (30/30; politica de contrasenas, lockout, JWT corto + refresh rotativo + revocacion), `c-63b-mfa-y-rol-privilegiado` (26/26; `User.is_privileged` + MFA TOTP + login en dos pasos) y `c-63c-rotacion-claves-secretos` (28/28; keyring JWT `kid`, rotacion Fernet `MultiFernet`, higiene de secretos + docs 5.16/5.18). Spec nueva `identity-access-hardening` (IAH-001..011). Prioridad 4. KMS/Vault/PAM/CA real y los controles 5.16/5.18 quedan documentados como (O)/futuro.
- **Scope** (T) original:
  - MFA para cuentas de operacion/administracion; politica de contrasenas; bloqueo por intentos fallidos.
  - Expiracion/rotacion/revocacion de JWT (refresh o lista de revocacion); revision periodica de accesos.
  - Gestion de claves (secret manager/KMS, rotacion de Fernet y del secreto JWT, CA real).
- **Dependencias**: `C-61` (parametros de politica)
- **Governance**: CRITICO
- **Leer antes**:
  - `docs/cumplimiento/plan-cambios-cumplimiento.md` §2-§3
  - `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`

### [C-64] `vulnerabilidades-supply-chain` — ARCHIVADO (2026-10-19, 33/33)

- **Estado**: `[x]` CREADO, APLICADO (33/33) y ARCHIVADO (2026-10-19; `openspec/changes/archive/2026-10-19-c-64-vulnerabilidades-supply-chain`). Governance MEDIO. Specs sincronizadas: `supply-chain-security` creada (capability nueva) y `ci-pipeline` y `security-governance-docs` modificadas (SGD-001). Entrega: `.github/dependabot.yml`; job `security-scan` en CI (pip-audit + bandit + npm audit); pinning de imagenes Docker (nginx:1.31.7-alpine, ngrok/ngrok:3.39.8-debian); cotas superiores de dependencias; documento de evaluacion de seguridad de proveedores. Cierra los controles ISO 8.8, 8.28, 8.29 y 5.19-5.23. trivy/SBOM evaluados y diferidos (no-goals). Prioridad 5.
- **Scope** (T+D):
  - Dependabot; `pip-audit`/`npm audit` en CI; escaneo de imagenes (trivy); SBOM; SAST (bandit/semgrep); pinning estricto de dependencias.
  - Evaluacion de seguridad y clausulas con proveedores (Twilio, Gemini, Microsoft, N8N).
- **Dependencias**: ninguna
- **Governance**: MEDIO
- **Leer antes**:
  - `docs/cumplimiento/plan-cambios-cumplimiento.md` §2-§3
  - `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`

### [C-65] `backup-continuidad` — ARCHIVADO (2026-10-19, 31/31)

- **Estado**: `[x]` CREADO, APLICADO (31/31; revision humana firmada, tarea 9.4) y ARCHIVADO (2026-10-19; `openspec/changes/archive/2026-10-19-c-65-backup-continuidad`). Governance ALTO. Specs sincronizadas: `continuity-planning` creada (capability nueva) y `backup-scripts` modificada (+BACKUP-005..008). Entrega: backup cifrado (openssl AES-256-CBC, `BACKUP_ENCRYPTION_PASSPHRASE`); scheduler versionado (cron + systemd timer); prueba de restauracion reproducible; `docs/seguridad/plan-continuidad.md` (RTO/RPO 24h; offsite/redundancia como accion del adoptante); correccion del gap assessment; Purpose real para `backup-scripts`. Cierra los controles ISO 8.13, 8.14, 5.29, 5.30 y 5.33. Prioridad 6.
- **Scope** (T+D):
  - Cifrado del backup; copia offsite; automatizacion; prueba de restauracion periodica.
  - RTO/RPO; plan de continuidad; redundancia basica.
- **Dependencias**: ninguna
- **Governance**: ALTO
- **Leer antes**:
  - `docs/cumplimiento/plan-cambios-cumplimiento.md` §2-§3
  - `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`

### [C-66] `privacidad-transferencias` — ARCHIVADO (2026-10-19, 36/36)

- **Estado**: `[x]` CREADO, APLICADO (36/36), verificado con revision humana firmada y ARCHIVADO (2026-10-19; `openspec/changes/archive/2026-10-19-c-66-privacidad-transferencias`). Governance ALTO. Specs sincronizadas: `privacy-runtime-surface` creada (capability nueva) + `runtime-cost-guard`, `security-governance-docs` y `employee-directory` modificadas (+7 agregados, 2 modificados, 1 removido en el sync). Cierra los controles ISO 5.34, 8.12, 8.15 y 5.31. Entrega: pseudonimizacion del numero llamante en los logs del guarda de costo con clave HMAC DEDICADA (`cost_guard_caller_hmac_key`, independiente de la clave de pseudonimizacion Fernet); superficie de privacidad en runtime (`/privacidad`) con informacion al titular y canal ARCO; procedimiento ARCO con plazos; politica de retencion de logs; justificacion por minimizacion del directorio e instrumento de transferencia internacional (documentado, no firmado); corrige dos inconsistencias documentales. Prioridad 3.
- **Scope** (T+D):
  - Quitar/pseudonimizar el numero llamante en logs (`cost_guard/guard.py:236,252`); cifrar o justificar por minimizacion el contacto del directorio (`models/empleado.py:16-18`).
  - Instrumento de transferencia internacional para Gemini/Twilio (clausulas modelo o consentimiento); consentimiento e informacion al titular.
  - Procedimiento ARCO con plazos; retencion de logs.
- **Dependencias**: —
- **Governance**: ALTO
- **Leer antes**:
  - `docs/cumplimiento/plan-cambios-cumplimiento.md` §2-§4
  - `docs/cumplimiento/marco-legal-ar-2026.md`
  - `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`

---

## FASE 22 — Ingesta del corpus por el flujo N8N real (2026-10-02)

> Change post-roadmap que desbloquea la carga del corpus de evaluacion: hoy los 200 casos tienen `tiempo_automatizado_s = null` y `evaluation/corpus.py` los rechaza. C-68 mide web y correo por el flujo N8N real y escribe de vuelta la metrica hibrida; telefonia queda a cargo manual del autor.

### [C-69] `dedup-correlacion-altas` — ARCHIVADO (2026-10-05, 30/30)

- **Estado**: `[x]` completado y archivado (2026-10-05 — `openspec/changes/archive/2026-10-05-c-69-dedup-correlacion-altas`; 30/30 tareas). Apply, testeado y commiteado (`1d6601b`); specs sincronizadas (added 5: `incident-origin-correlation` creada; `incident-intake-guards` y `n8n-workflow` modificadas). Governance MEDIO.
- **Problema**: el canal web envia `origen_message_id = null`, esquivando el indice unico de la migracion 005 (dedup server-side) y duplicando incidentes al reingestar; y `IncidenteRead` no expone `origen_message_id` ni el listado filtra por el, forzando correlacion por ventana temporal. Cierra las OQ2 (dedup web) y OQ6 (correlacion) de C-68.
- **Scope**:
  - `IncidenteRead` expone `origen_message_id`; filtro exacto opcional `origen_message_id` en el listado (routes -> service -> repository).
  - Rama web del normalizador N8N: acepta id deterministico del llamador (harness `corpus-<ID>`) y genera uno unico para el formulario real; correo/telefonia intactos.
  - Sin migracion ni backfill (indice unico 005 ya existe; legacy web queda nulo).
  - Tests TDD de schema, filtro, idempotencia web y estructura del workflow.
- **Dependencias**: **PREREQUISITO de `c-68-corpus-ingesta-n8n`** (OQ2/OQ6 delegadas). Reutiliza `incident-intake-guards` (idempotencia por origen) y `e2e-timing-instrumentation` (§6, replays sin re-medir). OQ-A..OQ-D RESUELTAS por el autor: OQ-A n8n genera el id (deterministico del llamador o unico por ejecucion; UUID backend opcional); OQ-B exponer `origen_message_id` en `IncidenteRead` + filtro exacto en el listado; OQ-C el formulario real no envia id (sin cambio de frontend); OQ-D sin backfill. Sin preguntas abiertas bloqueantes: apply-ready.
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/c-69-dedup-correlacion-altas/{proposal,design,tasks}.md`
  - `n8n/workflow.json` (nodo "Normalizar entrada del incidente")
  - `docs/medicion-latencia-e2e.md`

### [C-68] `corpus-ingesta-n8n` — ARCHIVADO (2026-10-09, 63/63)

- **Estado**: `[x]` completado y ARCHIVADO (2026-10-09 — `openspec/changes/archive/2026-10-09-c-68-corpus-ingesta-n8n`; 63/63 tareas). Harness de ingesta N8N operativo (observer no bloqueante, timeout IMAP/busqueda acotada, writers que saltan metricas anomalas y merge del sidecar por `case_id`); corpus web 53/53 y correo 66/66 medidos por el flujo N8N real (telefonia 81/81 medida por C-70); spec `corpus-n8n-ingest` creada. Governance MEDIO.
- **Problema**: el corpus de tesis no es cargable (`tiempo_automatizado_s` nulo en 200/200) y el harness existente mide un POST directo, no el flujo N8N real ni la espera del poller de correo.
- **Scope**:
  - Harness `scripts/corpus_ingest/ingest_via_n8n.py`: web por webhook + lectura por id; correo por SMTP + trigger IMAP + sondeo.
  - Metrica hibrida (D): `t_pipeline_s`, `t_espera_s`, `t_e2e_s`; `tiempo_automatizado_s = t_e2e_s` (web y correo).
  - Write-back a XLSX/CSV + sidecar sin descripciones + merge del JSON de evaluacion.
  - Runbook de activacion de N8N y credenciales; login desde entorno.
  - Tests offline (TDD) de la logica pura.
- **Dependencias**: `docs/medicion-latencia-e2e.md` (contrato de timing, C-39/C-48); `dry-run-harness` (verificacion web/correo, sin modificar). OQ1..OQ6 RESUELTAS/DELEGADAS: OQ1 canonico de correo (resuelta), OQ2 dedup web (delegada a c-69), OQ3 descomposicion (resuelta), OQ4 confirmacion de correo (resuelta), OQ5 telefonico (resuelta: carga manual del autor), OQ6 correlacion de correo (delegada a c-69).
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-10-09-c-68-corpus-ingesta-n8n/{proposal,design,tasks}.md`
  - `docs/medicion-latencia-e2e.md`
  - `docs/como_cargar_datos_corpus.md`

---

## FASE 23 — Medicion del corpus por telefonia real (2026-10-02)

> Change post-roadmap que cierra la carga manual que C-68 dejo para el canal telefonico. Mide los 81 casos de `llamada telefonica` por el flujo real (softphone -> Twilio -> backend C-52 -> n8n), con correlacion exacta llamada <-> caso del corpus y write-back de la metrica canonica, sobre una base descartable.

### [C-70] `softphone-corpus-telefonia` — ARCHIVADO (2026-10-06, 72/72)

- **Estado**: `[x]` aplicado, verificado y ARCHIVADO (2026-10-06; `openspec/changes/archive/2026-10-06-c-70-softphone-corpus-telefonia`) — 72/72 tareas; verify-report PASS WITH WARNINGS (0 CRITICAL; 31/35 escenarios; 4 infra/static manuales). **Corrida completa 8.2 REALIZADA (2026-10-06)**: 81/81 casos telefonicos cargados en la base descartable (duplicado R126 limpiado con `--replace` acotado); write-back `medidos=81 anomalos=0 pendientes=0 fallidos=0`. **8.3 REALIZADA**: `cd evaluation; pytest -q` -> 79 passed sin `CorpusError`; corpus 200/200 (81 telefono + 66 correo + 53 web). Specs sincronizadas al archivar: `telefonia-corpus-medicion` CREADA (8 reqs), `telefonia-stt-intake` (+1), `telephony-test-softphone` (+1). Suites: backend 991 offline + 39 integracion, evaluation 79, corpus_ingest 153, softphone 69, ruff limpio. OQ1..OQ6 resueltas. Governance ALTO. **Drift de entorno (no defecto)**: el stack operativo quedo en migracion 010 con imagen stale; se actualiza al reconstruir el backend base.
- **Problema**: el corpus tiene 81 casos de `llamada telefonica` con `tiempo_automatizado_s = null`; C-68 los dejo fuera de alcance para carga manual. No existe via reproducible para medirlos por el flujo real ni para correlacionar de forma exacta una llamada con su caso.
- **Scope**:
  - Softphone (extiende C-59): `<select>` con los casos telefonicos del corpus (default vacio); el modo `serve` expone la lista leida del JSON pseudonimizado; el autor RECITA el caso (sin playback).
  - `telefonia_ingreso.corpus_case_id` nullable (migracion Alembic): el param custom viaja del softphone al webhook de voz y al `recordingStatusCallback`, y se persiste al sellar `ingresado_en`. NO toca `call_sid` ni `origen_message_id`.
  - Script de recuperacion + write-back (`--replace`) reutilizando el merge/skip y la privacidad de `ingest_via_n8n.py`.
  - Metrica canonica de telefonia: `tiempo_automatizado_s = latencia_e2e_ms/1000 = t_pipeline_s = t_e2e_s`; `t_espera_s` vacia/N-A (no medible).
  - Perfil Compose `corpus` con base descartable y wipe; conmutacion manual de la Voice URL.
  - Los 81 casos los mide el autor (sin muestreo).
- **Dependencias**: `C-59` (softphone, archivado 2026-10-01; herramienta a extender); `C-52` (intake telefonico async, archivado 2026-09-30; flujo a preservar); `C-68` (write-back/merge/privacidad que reutiliza). OQ1..OQ6 RESUELTAS por el autor: OQ1 store keyed-by-CallSid (tabla efimera en PostgreSQL), OQ2 perfil `corpus` completo aislado, OQ3 endpoint `/corpus-cases`, OQ4 `t_espera_s` vacia/N-A, OQ5 endpoint de lectura dedicado, OQ6 `--replace` acotado con dry-run. Apply-ready.
- **Governance**: ALTO
- **Leer antes**:
  - `openspec/changes/c-70-softphone-corpus-telefonia/{proposal,design,tasks}.md`
  - `openspec/changes/archive/2026-10-01-c-59-softphone-voip-pruebas/{proposal,design,tasks}.md`
  - `docs/medicion-latencia-e2e.md` §5, `scripts/corpus_ingest/README.md`

---

## FASE 24 — Endurecimiento del clasificador determinista (2026-10-05)

> Change post-roadmap que corrige la debilidad MEDIDA del clasificador determinista. La cascada `REGEX -> Gemini -> humano` ya existe (Anexo H), pero la medicion offline sobre el corpus (sin llamar a Gemini) mostro: escalado a Gemini del **64%** (correo 66.7%, web 73.6%, telefono 55.6%); umbral 0.90 **degenerado** (el 100% de los cortocircuitos tiene confianza exactamente 1.0, o sea "un solo sector matcheo", no confiabilidad); el cortocircuito acierta la etiqueta primaria solo **~51%** (pertenencia multietiqueta 76%); sin matches, el desempate predice "Seguridad Informatica" por defecto (126 predicciones vs 31 reales); vocabulario (89 patrones) insuficiente para Hardware/Software. El F1 de Gemini/hibrido queda **pendiente** (sin cache `evaluation/predicciones.json`; Gemini con 429).

### [C-71] `hardening-clasificador-determinista` — ARCHIVADO (2026-10-06, 43/43)

- **Estado**: `[x]` aplicado (2026-10-05) y ARCHIVADO (2026-10-06; `openspec/changes/archive/2026-10-06-c-71-hardening-clasificador-determinista`) — 43/43 tareas; specs sincronizadas (classification-resilience +2/+1, sector-assignment +3, sector-taxonomy +1/+1; sin removals). OQ1..OQ5 resueltas (OQ1 piso de precision 0.90; OQ2 escalar SIEMPRE a Gemini sin fabricar sector; OQ3 umbral fijo re-derivado offline; OQ4 derivado a C-72; OQ5 baseline capturado). Vocabulario ampliado, confianza (min_matches + margen) y calibracion offline; `HYBRID_CACHE_VERSION=hybrid-v2`. Determinista estricto 0.485->0.670, macro-F1 0.4196->0.4801; no-match 119->57. Suites: 955 offline + 37 integracion + 79 evaluation; ruff limpio. **Desviacion**: con el piso 0.90 el umbral calibrado es 1.0 y cortocircuita 1/200 (el hibrido escala ~99.5% a Gemini) -> desactiva el atajo barato; decision del autor pendiente (`docs/deterministic_calibration.md`). Governance MEDIO.
- **Problema**: el clasificador determinista no esta a la altura de su rol en la cascada: no es ni confiable como atajo (cortocircuito ~51% estricto) ni amplio para evitar escalar (64% va a Gemini). El umbral de confianza no discrimina y el desempate sin señal inventa un sector.
- **Scope**:
  - No-match/empate: senal nula devuelve "sin prediccion" explicito (no un sector arbitrario); empate marca ambiguedad; ambos escalan.
  - Vocabulario: ampliar sinonimos/frases por sector guiado por misclasificaciones del corpus; preservar `set(KEYWORD_MAP.keys()) == set(SECTORES_CANONICOS)`.
  - Confianza/umbral: redefinir la medida (conteo minimo + margen) y recalibrar el cortocircuito con una curva precision/cobertura derivada del corpus.
  - Re-medicion: subir `HYBRID_CACHE_VERSION` (`hybrid-v1` -> `hybrid-v2`) e invalidar cache; re-medir F1 determinista vs hibrido.
- **Dependencias**: ninguna nueva. Reutiliza `sector-assignment`, `sector-taxonomy`, `classification-resilience` y el framework de `evaluation/`. Relacionado con C-70 (telefono) pero NO lo modifica (telefono sigue "siempre IA" en n8n; OQ4 fuera de alcance).
- **Governance**: MEDIO
- **OQs abiertas**: OQ1 piso de precision del cortocircuito vs cobertura; OQ2 no-match (Gemini vs humano); OQ3 umbral fijo vs derivado; OQ4 unificar telefono (fuera de alcance); OQ5 capturar baseline F1 Gemini/hibrido al restaurar la cuota.
- **Leer antes**:
  - `openspec/changes/archive/2026-10-06-c-71-hardening-clasificador-determinista/{proposal,design,tasks}.md`
  - `App/Backend/app/classifiers/{deterministic.py,keywords.py,hybrid.py}`
  - `docs/medicion-latencia-e2e.md`, `evaluation/README.md`

---

## FASE 25 — Unificacion de la clasificacion telefonica a la cascada (2026-10-05)

> Change que unifica la clasificacion del canal telefonico a la MISMA cascada del backend que ya usan correo/web (deterministico -> Gemini -> humano), en lugar del `AI Agent` de n8n que hoy clasifica SIEMPRE con Gemini (via `clasificacion` precalculada en el handoff). Beneficio: un solo camino y un solo prompt (`docs/prompt_gemini.txt`), telefono cortocircuita barato y las reglas de frontera (p. ej. R002 "acceder al sistema" y R038 "digitalizar") se arreglan una vez para todos los canales. Depende de C-71.

### [C-72] `unificar-clasificacion-telefonica` — ARCHIVADO (2026-10-07, 37/37)

- **Estado**: `[x]` aplicado (2026-10-06) — 37/37 tareas; `openspec validate --strict` pasa. OQ1..OQ5 RESUELTAS por el autor (todas opcion A): OQ1 retirar el `AI Agent` de telefonia; OQ2 confirmar el traslado de costo a `backend_gemini`; OQ3 retirar el bucle de refinamiento con camino terminal con revision humana; OQ4 sin backfill (fuera de alcance); OQ5 adoptar las reglas minimas de frontera del design. Implementado: (S1) el backend resuelve telefonia por la cascada `HybridClassifier` ignorando la `clasificacion` precalculada y preservando el borde de pseudonimizacion (`constants.py` `CANAL_TELEFONIA`/`es_canal_telefonia()`, `incidente_service._resolve_classification`); (S2) `n8n/workflow.json` de 38 a 28 nodos: POST sin `clasificacion`, `AI Agent` + Gemini chat model + memoria + guarda `n8n_gemini` retirados, telefono `Sellar -> Normalizar`; (S3) `docs/prompt_gemini.txt` con las reglas de frontera compartidas; (S4) costo: telefonia no reserva `n8n_gemini`, la escalacion reserva `backend_gemini`; (S5) medicion offline + nota; (S6) Anexo H, narrativa de tesis y decision de backfill documentadas. Suites: 943 offline + 1 xfailed, ruff limpio; `openspec validate --strict` OK. **Delta reconciliado (2026-10-06)**: el delta `n8n-workflow` quedo con 14 `REMOVED`, 5 `MODIFIED` y 4 `ADDED` (sin solapamientos). `REMOVED`: los requisitos de nodos retirados (`N8N-INTAKE-001`, `Acoplamiento del AI Agent...`, `N8N-AGENT-001/002/003`, `N8N-MEMORY-001`, `N8N-TIMING-003`, `N8N-PHONE-001`, `N8N-VALID-001`, `N8N-GUARD-001/002`) mas `N8N-REFINE-001` (el bucle de refinamiento y el agente se retiran por completo, OQ1=A/OQ3=A). `MODIFIED`: `Normalizacion de canales`, `Trigger Webhook Twilio`, `Entrada valida`/ruteo, `Credenciales declaradas` y los cuerpos de timing/phone. `ADDED`: versiones renombradas de `N8N-TIMING-001` y `N8N-PHONE-003` (sufijo del heading ajustado para evitar colision ADDED/REMOVED) con titulos de escenario sin "agente" (`Telefonia captura antes de la cascada del backend`, `La cascada del backend consume la descripcion pseudonimizada`). Tras archivar, el spec principal no conservara ninguna mencion al `AI Agent` en requisitos vigentes; solo quedaran en los `Reason`/`Migration` de los REMOVED. `runtime-cost-guard` sin REMOVED (su unico requisito afectado ya esta en MODIFIED). 5.2 (F1 hibrido) PENDIENTE por cuota Gemini y corpus incompleto. Governance ALTO.
- **Problema**: dos clasificadores y dos prompts divergentas; telefono paga Gemini siempre (sin atajo determinista) y muestra errores de frontera (medido: 25 casos, 92% pertenencia / 56% estricto).
- **Scope**:
  - El handoff de telefono DEJA de mandar `clasificacion` precalculada; el backend clasifica con `HybridClassifier` como correo/web.
  - Retirar/ajustar la rama `AI Agent` de telefono en `n8n/workflow.json` (y su reserva `n8n_gemini` / loop de refinamiento).
  - Reglas de frontera al prompt compartido `docs/prompt_gemini.txt` (digitalizar/escaner -> Hardware; acceder a aplicacion/sistema -> Software; servidor/red -> Sistemas).
  - Actualizar Anexo H / docs.
- **Dependencias**: **C-71** (prerrequisito: la cascada solo conviene una vez endurecido el determinista). Relacionado con C-70.
- **Governance**: ALTO
- **Leer antes**:
  - `openspec/changes/c-72-unificar-clasificacion-telefonica/{proposal,design,tasks}.md`
  - `App/Backend/app/classifiers/{hybrid.py,deterministic.py}`, `docs/prompt_gemini.txt`, `n8n/workflow.json`

---

## FASE 26 — Pseudonimizacion de numeros de tarjeta hablados (2026-10-06)

> Change que agrega la categoria `[TARJETA]` al pseudonimizador para censurar numeros de tarjeta de 16 digitos dictados por un llamante distraido. R169 (telefonia) es el caso tematico.

### [C-73] `pseudonimizacion-tarjeta` — ARCHIVADO (2026-10-07, 23/23)

- **Estado**: `[x]` aplicado (2026-10-06) y ARCHIVADO (2026-10-07, 23/23; `openspec/changes/archive/2026-10-07-c-73-pseudonimizacion-tarjeta`) — 23/23 tareas; verify PASS (16/16 escenarios) tras cerrar la mascara multi-tarjeta y el test de auditoria; spec `data-pseudonymization` sincronizada. Governance HIGH.
- **Problema**: el pseudonimizador tiene 4 categorias (email, telefono, host, persona) y ninguna de tarjeta; el patron de TELEFONO consume parcialmente las corridas de 16 digitos y deja digitos en claro (p. ej. `4517 6712 3456 7890` -> `[TELEFONO] 7890`).
- **Scope**: nueva categoria CARD -> `[TARJETA]` (mayusculas) aplicada ANTES de TELEFONO; disparador contextual (mencion de `tarjeta`) con ventana de 40 caracteres; tolerancia 4-4-4-4; no regresion del caso R067 (corrida de 16 digitos de un DLL, sin "tarjeta", NO debe censurarse). Fuera de alcance: Luhn y longitudes distintas de 16.
- **Dependencias**: ninguna.
- **Governance**: HIGH (PII financiera, Ley 25.326).
- **Leer antes**:
  - `openspec/changes/c-73-pseudonimizacion-tarjeta/{proposal,design,tasks}.md`
  - `App/Backend/app/utils/pseudonymizer.py`, `openspec/specs/data-pseudonymization/spec.md`

---

## FASE 27 — Calibracion del cortocircuito determinista (2026-10-07)

> Change que redisenia la senal de seleccion del cortocircuito determinista (criterio comparativo contra Gemini, piso de correctitud, conformal/cross-fitting) y fija la corrida oficial hybrid-v3 del capitulo 7. Depende de C-71/C-72.

### [C-74] `calibracion-cortocircuito-determinista` — ARCHIVADO (2026-10-07, 32/32)

- **Estado**: `[x]` aplicado, verificado (PASS, 18/18 escenarios) y ARCHIVADO (2026-10-07; `openspec/changes/archive/2026-10-07-c-74-calibracion-cortocircuito-determinista`) — 32/32 tareas. Corrida paga oficial (hybrid-v3) ejecutada: macro-F1 0.5207, estricta 0.7350. Convencion de dos caches de calibracion (`evaluation/predicciones.json` vs `evaluation/predicciones_calibracion.json`) desacoplada via `resolver_cache_calibracion`. Governance MEDIO.
- **Problema**: la `confianza` determinista esta anti-correlacionada con el acierto; ningun piso absoluto (0.85) alcanza cobertura util (techo ~6%).
- **Scope**: senal de seleccion comparativa (determinista 0.740 > Gemini 0.677), conformal/risk-controlled, cross-fitting, piso 0.85 y `min_matches` como feature; re-medicion oficial con el corpus real.
- **Dependencias**: C-71 (determinista endurecido), C-72 (cascada unica).
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-10-07-c-74-calibracion-cortocircuito-determinista/{proposal,design,tasks}.md`
  - `evaluation/deterministic_measurement.py`, `openspec/specs/classification-resilience/spec.md`, `openspec/specs/evaluation-framework/spec.md`

---

## FASE 28 — Sincronizacion documental N8N (2026-10-08)

> Change de solo documentacion que sincroniza los docs operativos con la verdad vigente del workflow N8N tras C-72 (retiro de la rama IA telefonica) y C-55 (Outlook -> IMAP/SMTP). No toca runtime ni infraestructura.

### [C-75] `sincronizar-docs-n8n` — ARCHIVADO (2026-10-08, 14/14)

- **Estado**: `[x]` propuesto, aplicado (14/14), verificado (PASS, 15/15 escenarios) y ARCHIVADO (2026-10-08; `openspec/changes/archive/2026-10-08-c-75-sincronizar-docs-n8n`). Spec `n8n-workflow` sincronizada: +3 requirements (N8N-DOC-004/005/006). Suite de doc-sync 202 passed / 1 xfailed; `openspec validate --specs` 43/43. Governance MEDIUM.
- **Problema**: la verdad del workflow se movio y la documentacion no: 10 docs describian nodos retirados (`AI Agent`, `Guard de costo`, `memoryRedisChat`, etc.), transporte Outlook/Twilio y credenciales inexistentes.
- **Scope**: Tier 1 (guia N8N, `por_implementar.md`, runbook c-52, diagramas) y Tier 2 (`dry-run-harness.md`, `operational-guide.md`, `medicion-latencia-e2e.md`, `troubleshooting.md`). Fuera de alcance: `n8n/workflow.json`, `docker-compose.yml`, codigo de produccion.
- **Dependencias**: ninguna (correccion de drift de C-72/C-55).
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-10-08-c-75-sincronizar-docs-n8n/{proposal,design,tasks,verify-report}.md`
  - `n8n/workflow.json`, `docs/n8n-workflow-guide.md`, `openspec/specs/n8n-workflow/spec.md`

---

## FASE 29 — Correcciones de la tesis por el dictamen CONEAU (2026-10-09 / 2026-10-12)

> Changes sobre el documento academico (LaTeX, `docs/Tesis/v9 (IA)/paper/`), independientes del software. Se aplican EN SECUENCIA porque comparten archivos `.tex` (en especial `08-discusion.tex` y `09-conclusiones.tex`). Ninguno esta aplicado (0 tareas); todos con planning OPSX completo y `openspec validate --strict` OK. El registro acumulativo del dictamen vive en `docs/Tesis/Correcciones/dictamen-correcciones.md`. El plan de auditoria (4 bloques, 32 items) queda cubierto por C-76..C-80; el mapeo item -> change esta al final de ese registro.

### [C-76] `tesis-correcciones-dictamen` — ACTIVO (0/46)

- **Estado**: `[ ]` propuesto (planning completo). Sin aplicar.
- **Problema**: la tesis todavia reporta numeros del corpus sintetico descartado en C-27 (3 clases con "Operaciones", exactitud 92 %, F1 0,919, Wilcoxon W=0 falso).
- **Scope**: alinear Cap. 4/7/8 y los capitulos que citan numeros con el corpus real de 200 casos; grupo T1-T7 (trazabilidad y existencia de datos experimentales, ventana temporal, instrumento manual); Anexos F/H y `main.pdf`.
- **Dependencias**: ninguna (documento de tesis).
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/c-76-tesis-correcciones-dictamen/{proposal,design,tasks}.md`
  - `docs/Tesis/Correcciones/dictamen-correcciones.md` (P1.0/P1, T1-T7)
  - `data/corpus_evaluacion_pseudonimizado.json`, `evaluation/report.md`

### [C-77] `tesis-errores-estadisticos-inferenciales` — ACTIVO (0/49)

- **Estado**: `[ ]` propuesto (planning completo; OQ1-OQ6 resueltas; ampliado con Grupo E - Opcion A del tiempo automatico telefonico). Sin aplicar.
- **Problema**: errores estadisticos e inferenciales (formula del tamano del efecto, convencion de W, W+/W-, calibracion, "varianza casi diez veces menor", horas-persona, universo 3.700).
- **Scope**: reparar la estadistica y la coherencia metodologica; alinear `evaluation/stats.py`; cruce confianza x acierto; calculo del tamano muestral.
- **Dependencias**: aplicar tras C-76.
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/c-77-tesis-errores-estadisticos-inferenciales/{proposal,design,tasks}.md`
  - `evaluation/stats.py`, `evaluation/report.md`

### [C-78] `tesis-bibliografia-atribucion` — ACTIVO (0/25)

- **Estado**: `[ ]` propuesto (planning completo; min. 12 refs; OQ-B3-1 resuelta 2026-10-12). Sin aplicar.
- **Problema**: misatribucion a Revina et al. (2020) (BERT/91 %/transferencia: falso); 2 citas fabricadas de v7 ya retiradas; claims sin cita (88-94 %); higiene de citas (Landis & Koch, Stallings/Brown, Jurafsky, et al.).
- **Scope**: reescribir 3.3 y 8.2 con la conclusion real de Revina; incorporar 12 refs arbitradas 2023-2026; corregir metadatos del `.bib`; re-verificacion por DOI.
- **Dependencias**: aplicar tras C-77.
- **Governance**: ALTO (integridad academica)
- **Leer antes**:
  - `openspec/changes/c-78-tesis-bibliografia-atribucion/{proposal,design,tasks}.md`
  - `docs/Tesis/v9 (IA)/Bibliography_base.bib`, `docs/Tesis/v9 (IA)/verify_citations.py`

### [C-79] `tesis-aspectos-legales` — ACTIVO (0/25)

- **Estado**: `[ ]` propuesto (planning completo; OQ-L1/L1b/L2/L5 resueltas 2026-10-12; apply-ready). Sin aplicar.
- **Problema**: capitulo legal con defectos de correccion juridica: retencion contradictoria ("indefinida" vs "30 dias") sin politica de supresion, base legal "legitimo interes" (GDPR, no existe en Ley 25.326), adecuacion europea mal explicada (bidireccional), transferencia telefonica pre-pseudonimizacion no declarada (Twilio) y fuentes juridicas sin control de vigencia.
- **Scope**: reescribir 11.1-11.3; plazo de conservacion concreto + politica de supresion al vencimiento; base art. 5 inc. 2 ap. b/d; Decision 2003/490/CE + revalidacion 2024; audio crudo + numero a EE.UU. antes de pseudonimizar; instrumento del art. 12; revision de vigencia de las fuentes citadas.
- **Dependencias**: aplicar tras C-78.
- **Governance**: ALTO (legal / privacidad)
- **Leer antes**:
  - `openspec/changes/c-79-tesis-aspectos-legales/{proposal,design,tasks}.md`
  - `docs/cumplimiento/marco-legal-ar-2026.md`, `docs/seguridad/registro-requisitos-legales.md`
  - `docs/runbook-verificacion-telefonia-c52.md`

### [C-80] `tesis-forma-evidencia-visual` — ACTIVO (0/45)

- **Estado**: `[ ]` propuesto (planning completo; OQ-F2-1/F2-2/F3-1 resueltas 2026-10-12; figura 7 por canal; apply-ready). Sin aplicar.
- **Problema**: Bloque 4 del dictamen (items 26-32): 52 errores ortograficos, 8 figuras faltantes (hay 1 sola), 7 anexos A-G descriptivos + Anexo H fuera de la tesis, fuente de tablas inconsistente, ~900 palabras duplicadas, nota obsoleta "N8N 1.62", afirmaciones valorativas sin respaldo.
- **Scope**: sustitucion ortografica contextual; 8 figuras (Mermaid->PNG, screenshots, matplotlib); anexos con contenido + Anexo H; unificar tablas; deduplicar 1.1/2.1, 5.3/6.3, 8.1/9.1; retirar la nota 1.62; rebajar claims de 8.1/9.1.
- **Dependencias**: aplicar tras C-79 (al final: comparte 08/09 con C-76/C-77).
- **Governance**: BAJO
- **Leer antes**:
  - `openspec/changes/c-80-tesis-forma-evidencia-visual/{proposal,design,tasks}.md`
  - `docs/diagrams/despliegue.md`, `docs/diagrams/secuencia.md`
  - `docs/anexo_h_prompt_gemini.md`, `docs/anexo_c_esquema_bd.md`

---

## FASE 30 — RBAC, ciclo de cierre y sesion (2026-10-13 / 2026-10-15)

> Changes post-roadmap sobre el RBAC, el ciclo de vida del incidente, la operacion del panel y el ciclo de sesion. Se dividen en la reelaboracion del RBAC y las pantallas de revision (C-81..C-83, archivados 2026-10-13) y el ciclo de cierre, borrado logico, busqueda, directorio, prioridad y ciclo de sesion (C-84..C-91, archivados 2026-10-15). Todos quedan ARCHIVADOS.

### [C-81] `frontend-rbac` — ARCHIVADO (2026-10-13, 24/24)

- **Estado**: `[x]` completado y archivado (2026-10-13 — `openspec/changes/archive/2026-10-13-c-81-frontend-rbac`; 24/24 tareas). Endpoint aditivo `GET /api/v1/auth/me` (identidad + `alcance.modo`), guard de rutas por modo, navegacion del `Header` por modo y vista "Mis incidentes". Specs sincronizadas: `frontend-rbac` creada, `identity-access-hardening` +IAH-012.
- **Problema**: la GUI de incidentes era role-blind: el RBAC vivia SOLO en el backend y el frontend no conocia ni reflejaba rol/alcance. Tras C-82 (tres roles, modos PROPIO/GLOBAL/VACIO, sin aislamiento por sector) los artefactos originales asumian cuatro roles y modos SECTOR/REVISION inexistentes.
- **Scope**: `GET /api/v1/auth/me` aditivo (recomputado por request desde el directorio); `AuthContext` consume `rol` + `alcance.modo`; guard de rutas (GLOBAL -> superficie operativa; PROPIO -> "Mis incidentes"; VACIO -> portal); navegacion por `alcance.modo`; filtro de sector como conveniencia de UI (no frontera). El backend NO cambia su enforcement (`incident_visibility`/`role_policy` siguen siendo la unica fuente).
- **Dependencias**: `C-82` (RBAC backend, archivado 2026-10-13).
- **Governance**: CRITICO (superficie auth/RBAC; la porcion frontend es MEDIA).
- **Leer antes**:
  - `openspec/changes/archive/2026-10-13-c-81-frontend-rbac/{proposal,design,tasks}.md`
  - `openspec/specs/frontend-rbac/spec.md`, `openspec/specs/identity-access-hardening/spec.md`

### [C-82] `rbac-redesign` — ARCHIVADO (2026-10-13, 36/36)

- **Estado**: `[x]` completado y archivado (2026-10-13 — `openspec/changes/archive/2026-10-13-c-82-rbac-redesign`; 36/36 tareas). Specs sincronizadas: `role-policy` creada; `incident-visibility`, `employee-directory`, `notification-routing` e `identity-access-hardening` modificadas. Migracion Alembic 017.
- **Problema**: el RBAC estaba inconsistente: cuatro roles con el conocimiento duplicado en cinco lugares, `operador` y `mesa_de_ayuda` solapados, el sector a la vez frontera de acceso y categoria de clasificacion, y un `usuario_final` que no podia ver los incidentes que el mismo reporto.
- **Scope** (BREAKING): vocabulario a EXACTAMENTE tres roles (`usuario_final` PROPIO, `mesa_de_ayuda` GLOBAL privilegiado sin directorio, `administrador_directorio` GLOBAL privilegiado); se ELIMINA `operador` y el aislamiento por sector (el sector queda solo como categoria de clasificacion); vinculo de reportante (FK nullable) poblado por canal; destinatarios de revision = todos los `mesa_de_ayuda` activos; registro canonico `role-policy` como fuente unica; migracion 017 (CHECK del rol + reportante + backfill `operador -> mesa_de_ayuda`).
- **Dependencias**: ninguna (habilita `C-81`).
- **Governance**: CRITICO/ALTO (auth/RBAC, directorio, datos personales y visibilidad).
- **Leer antes**:
  - `openspec/changes/archive/2026-10-13-c-82-rbac-redesign/{proposal,design,tasks}.md`
  - `openspec/specs/role-policy/spec.md`, `openspec/specs/incident-visibility/spec.md`

### [C-83] `revision-humana-info-completa` — ARCHIVADO (2026-10-13, 18/18)

- **Estado**: `[x]` completado y archivado (2026-10-13 — `openspec/changes/archive/2026-10-13-c-83-revision-humana-info-completa`; 18/18 tareas). Spec `frontend-revision-humana` creada. Frontend unicamente.
- **Problema**: en "Revision Humana" el operador validaba a ciegas: ni la tabla ni el dialogo mostraban la descripcion ni la clasificacion, forzando a abandonar la pestana y abrir el ticket en "Lista de Tickets".
- **Scope**: el dialogo de validacion muestra descripcion pseudonimizada, metadatos, clasificacion (sector predicho, confianza, etapa, respuesta raw) y sectores multietiqueta editables (principal + adicionales); se extrae una vista de detalle de solo lectura compartida con `TicketDetailDialog`; `ClasificacionLogRead` expone `sectores_predichos`/`sectores_validados`; sin cambios de backend.
- **Dependencias**: ninguna nueva (reutiliza `obtenerIncidente` y `listarClasificacionesPorIncidente`).
- **Governance**: MEDIO (frontend; flujo de revision humana).
- **Leer antes**:
  - `openspec/changes/archive/2026-10-13-c-83-revision-humana-info-completa/{proposal,design,tasks}.md`
  - `openspec/specs/frontend-revision-humana/spec.md`

### [C-84] `logout-navbar-y-toggle-password` — ARCHIVADO (2026-10-15, 15/15)

- **Estado**: `[x]` completado y archivado (2026-10-15 — `openspec/changes/archive/2026-10-15-c-84-logout-navbar-y-toggle-password`; 15/15 tareas). Spec `frontend-session-ui` creada. Frontend unicamente.
- **Problema**: dos huecos de usabilidad: el Header no ofrecia cerrar sesion (la sesion quedaba atrapada hasta expirar el token) y el campo de contrasena del login no tenia confirmacion visual de lo tipeado.
- **Scope**: boton "Cerrar sesion" en el Header para todo autenticado (invoca el `logout()` existente y navega a `/login`); toggle ojo `Eye`/`EyeOff` en el input de contrasena con `aria-label` dinamico y operable por teclado. Sin cambios de logica de auth, endpoints ni schemas.
- **Dependencias**: ninguna nueva.
- **Governance**: BAJO (chrome de sesion del frontend, sin logica de autenticacion).
- **Leer antes**:
  - `openspec/changes/archive/2026-10-15-c-84-logout-navbar-y-toggle-password/{proposal,design,tasks}.md`
  - `openspec/specs/frontend-session-ui/spec.md`

### [C-85] `revision-humana-contador-y-mensaje` — ARCHIVADO (2026-10-15, 34/34)

- **Estado**: `[x]` completado y archivado (2026-10-15 — `openspec/changes/archive/2026-10-15-c-85-revision-humana-contador-y-mensaje`; 34/34 tareas). Specs sincronizadas: `frontend-revision-humana` (+FRH-008/009/010), `incident-visibility` (+VIS-006).
- **Problema**: el badge de "Revision Humana" se calculaba sobre una consulta topeada a 50 filas (contador congelado en 50 y tabla truncada en silencio); el aviso ambar referenciaba el modelo retirado "Gemini 2.5 Flash".
- **Scope**: nuevo endpoint aditivo `GET /clasificaciones/revision-pendiente/count` con el mismo alcance que el listado; el badge consume el total real; la cola se pagina (`limit`/`offset`) sin truncamiento; aviso reescrito agnostico al modelo (umbral 70%).
- **Dependencias**: ninguna nueva.
- **Governance**: MEDIO (endpoint + frontend; logica de alcance de la cola).
- **Leer antes**:
  - `openspec/changes/archive/2026-10-15-c-85-revision-humana-contador-y-mensaje/{proposal,design,tasks}.md`
  - `openspec/specs/frontend-revision-humana/spec.md`, `openspec/specs/incident-visibility/spec.md`

### [C-86] `rol-gestion-incidentes-ciclo-cierre` — ARCHIVADO (2026-10-15, 61/61)

- **Estado**: `[x]` completado y archivado (2026-10-15 — `openspec/changes/archive/2026-10-15-c-86-rol-gestion-incidentes-ciclo-cierre`; 61/61 tareas). Specs: `incident-lifecycle`, `incident-comments` y `frontend-incidentes-historial` creadas; `employee-directory`, `role-policy`, `incident-visibility`, `notification-routing` y `frontend-rbac` modificadas. Migracion Alembic 018.
- **Problema**: faltaba el rol operativo `gestion_incidentes` (atiende y cierra los incidentes de SU sector) y todo el ciclo de cierre: cierre por sector, reapertura, historial de cerrados, comentarios duraderos y registro de QUIEN cierra o cambia de estado.
- **Scope** (BREAKING): cuarto rol `gestion_incidentes` (requiere sector, alcance nuevo `SECTOR`, no privilegiado, no gestiona directorio; cierra y edita estado de su sector, no crea/borra/valida); alcance `SECTOR` acotado server-side por pertenencia al conjunto de sectores y no-cerrado; ciclo de cierre (`incidente_cierre_sector`, cierre GLOBAL de `mesa_de_ayuda`, transicion terminal a `cerrado`, `REHABILITAR` exclusivo de `mesa_de_ayuda`); comentarios append-only `incidente_comentario`; auditoria de ciclo de vida `incidente_evento`; notificacion post-revision a los `gestion_incidentes` del sector; pestana "Historial de Incidentes Cerrados"; migracion 018.
- **Dependencias**: ninguna nueva (reelabora el modelo de `C-82`, archivado).
- **Governance**: ALTO (politica de autorizacion/rol + ciclo de vida + migracion de datos).
- **Leer antes**:
  - `openspec/changes/archive/2026-10-15-c-86-rol-gestion-incidentes-ciclo-cierre/{proposal,design,tasks}.md`
  - `openspec/specs/incident-lifecycle/spec.md`, `openspec/specs/role-policy/spec.md`, `openspec/specs/incident-visibility/spec.md`

### [C-87] `borrado-logico-incidentes` — ARCHIVADO (2026-10-15, 25/25)

- **Estado**: `[x]` completado y archivado (2026-10-15 — `openspec/changes/archive/2026-10-15-c-87-borrado-logico-incidentes`; 25/25 tareas). Specs: `incident-soft-delete` creada; `role-policy` (+RP-005), `incident-visibility` (+VIS-009) y `frontend-rbac` (+FR-RBAC-006) modificadas. Migracion Alembic 019.
- **Problema**: no existia forma de retirar un incidente erroneo o duplicado; el unico borrado era fisico (`hard_delete`, herramienta interna sin control de rol), y el historial de cerrados mostraria filas retiradas.
- **Scope**: columnas nullable `deleted_at`/`deleted_by` (FK a `directorio_empleado.id`, `ON DELETE SET NULL`); `DELETE /api/v1/incidentes/{id}` con borrado LOGICO 204 y autorizacion exclusiva de `administrador_directorio` (403 el resto; fuera de alcance 404); exclusion de los incidentes borrados de todas las superficies de lectura (listado, detalle, colas e historial); accion de UI solo para el administrador con confirmacion; migracion 019 aditiva.
- **Dependencias**: `C-86` (pestana de historial que la exclusion condiciona).
- **Governance**: ALTO (autorizacion + retencion/auditoria Ley 25.326).
- **Leer antes**:
  - `openspec/changes/archive/2026-10-15-c-87-borrado-logico-incidentes/{proposal,design,tasks}.md`
  - `openspec/specs/incident-soft-delete/spec.md`, `openspec/specs/role-policy/spec.md`

### [C-88] `busqueda-incidentes-panel` — ARCHIVADO (2026-10-15, 19/19)

- **Estado**: `[x]` completado y archivado (2026-10-15 — `openspec/changes/archive/2026-10-15-c-88-busqueda-incidentes-panel`; 19/19 tareas). Specs: `incident-search` y `frontend-incident-search` creadas. Migracion Alembic 020.
- **Problema**: el Panel solo filtraba por listas cerradas (estado, sector, prioridad); hallar un incidente por su contenido obligaba a recorrer paginas a mano.
- **Scope**: parametro `q` en `GET /api/v1/incidentes` (ILIKE parcial case-insensitive sobre `descripcion_pseudonimizada`, coincidencia exacta por `id` cuando es numerico, escape de comodines LIKE, composicion AND con los filtros y el alcance); migracion 020 (`pg_trgm` + indice GIN trigram); barra de busqueda en el Panel con debounce 300 ms, minimo 2 caracteres y reinicio de pagina; sin cambios rupturistas (`q` opcional).
- **Dependencias**: ninguna nueva (ortogonal al alcance de `C-86`).
- **Governance**: MEDIO (busqueda + migracion de indice + frontend).
- **Leer antes**:
  - `openspec/changes/archive/2026-10-15-c-88-busqueda-incidentes-panel/{proposal,design,tasks}.md`
  - `openspec/specs/incident-search/spec.md`, `openspec/specs/frontend-incident-search/spec.md`

### [C-89] `ui-directorio-administrador` — ARCHIVADO (2026-10-15, 19/19)

- **Estado**: `[x]` completado y archivado (2026-10-15 — `openspec/changes/archive/2026-10-15-c-89-ui-directorio-administrador`; 19/19 tareas). Specs: `frontend-directorio` creada; `frontend-rbac` modificada. Sin cambios de backend.
- **Problema**: el backend ya exponia la API completa del directorio (`/api/v1/directorio`), pero no habia superficie en el frontend: solo se podia gestionar por API/CLI.
- **Scope**: nueva pagina `/directorio` sobre los endpoints existentes (listar, crear, editar, activar/desactivar, borrado ARCO y purga por retencion); guard de ruta por ROL `administrador_directorio` (ademas del modo `GLOBAL`); entrada de navegacion en el `Header` solo para ese rol; formulario con seleccion de rol (incluye `gestion_incidentes` y sector condicional); confirmaciones para acciones destructivas. Sin migraciones ni regeneracion de OpenAPI.
- **Dependencias**: `C-86` (rol `gestion_incidentes` en enum/CHECK/policy).
- **Governance**: MEDIO (frontend de administracion del directorio; acciones destructivas con confirmacion).
- **Leer antes**:
  - `openspec/changes/archive/2026-10-15-c-89-ui-directorio-administrador/{proposal,design,tasks}.md`
  - `openspec/specs/frontend-directorio/spec.md`, `openspec/specs/frontend-rbac/spec.md`

### [C-90] `prioridad-critica-restringida` — ARCHIVADO (2026-10-15, 17/17)

- **Estado**: `[x]` completado y archivado (2026-10-15 — `openspec/changes/archive/2026-10-15-c-90-prioridad-critica-restringida`; 17/17 tareas). Specs: `role-policy` (+RP-006) y `frontend-rbac` (+FR-RBAC-009) modificadas. Sin migracion.
- **Problema**: la prioridad `critica` no se ofrecia en el formulario web, pero el backend la aceptaba sin restriccion de rol; un llamante no autorizado podia fijarla o conservarla con una llamada directa a la API.
- **Scope**: permiso `puede_asignar_prioridad_critica` en el registro de politica (verdadero para `mesa_de_ayuda` y `administrador_directorio`); `POST`/`PATCH /incidentes` rechazan con 403 cuando un llamante sin permiso asigna o conserva `critica`; `baja|media|alta` sin restriccion; frontend alinea el control de prioridad y los badges, sin ofrecer `critica` en el reporte publico.
- **Dependencias**: `C-86` (RP-001/002/003 no se tocan; RP-006 es adicional).
- **Governance**: ALTO (enforcement de autorizacion server-side).
- **Leer antes**:
  - `openspec/changes/archive/2026-10-15-c-90-prioridad-critica-restringida/{proposal,design,tasks}.md`
  - `openspec/specs/role-policy/spec.md`, `openspec/specs/frontend-rbac/spec.md`

### [C-91] `sesion-jwt-cookie-rotativa` — ARCHIVADO (2026-10-15, 48/48)

- **Estado**: `[x]` completado y archivado (2026-10-15 — `openspec/changes/archive/2026-10-15-c-91-sesion-jwt-cookie-rotativa`; 48/48 tareas). Specs: `frontend-session-lifecycle` creada; `identity-access-hardening` modificada (IAH-003/004 + IAH-013/014). Gate CRITICAL satisfecho (aprobacion humana explicita "Aplica", 2026-10-15).
- **Problema**: la sesion no sobrevivia un reload (tokens solo en memoria), el access duraba 15 min, la regla "7 dias sin acceso" existia de hecho pero no estaba declarada en ninguna spec, y no habia aviso proactivo de expiracion.
- **Scope** (BREAKING en el transporte del refresh): access 15 -> 30 min; inactividad de 7 dias con refresh deslizante (sin migracion, sin tope absoluto de vida); refresh token en cookie `HttpOnly`+`Secure`+`SameSite` (login/refresh/logout; rehidratacion silenciosa al arranque); UX de expiracion con modal "continuar/cerrar" y ventana de gracia de 30 s; coherencia multipestana con `BroadcastChannel`; CSRF `SameSite=Strict` + verificacion de `Origin`; CORS con credenciales y origenes exactos.
- **Dependencias**: ninguna nueva de runtime (reutiliza `RefreshToken`, `auth_service` y la rotacion existentes).
- **Governance**: CRITICO (auth/seguridad — requiere aprobacion humana antes de escribir codigo).
- **Leer antes**:
  - `openspec/changes/archive/2026-10-15-c-91-sesion-jwt-cookie-rotativa/{proposal,design,tasks}.md`
  - `openspec/specs/identity-access-hardening/spec.md`, `openspec/specs/frontend-session-lifecycle/spec.md`

---

## FASE 31 — Correcciones de la tesis por la nueva auditoria (2026-10-19)

> Changes sobre el documento academico (LaTeX, `docs/Tesis/v9 (IA)/paper/`), derivados de una NUEVA auditoria capitulo por capitulo (`docs/Tesis/Correcciones/auditoria-capitulos.md`) y del informe completo (`auditorias/Auditoria_Tesis_Gomez_Bustos_Sevilla_040802026.pdf`, 105 hallazgos: 28 criticos / 34 altos / 29 medios / 14 bajos). El cruce con los changes existentes esta en `docs/Tesis/Correcciones/reconciliacion-cobertura.md`. C-76..C-80 (FASE 29) siguen siendo los duenios del corpus, la estadistica/inferencia, la bibliografia, lo legal y la forma; C-92..C-96 cubren los hallazgos NUEVOS A/M/B que los cinco changes previos no abordan. C-18 quedo STALE (el artefacto N8N ya fue corregido por c-29, commit ef656ac; solo resta el residuo textual, en c-77 C3). Ninguno esta aplicado (0 tareas); todos con planning OPSX completo y `openspec validate --strict` OK. Se aplican EN SECUENCIA porque comparten archivos `.tex`. Orden recomendado: c-76 -> c-77 -> c-78 -> c-79 -> c-80 -> c-92 -> c-93 -> c-94 -> c-95 -> c-96.

### [C-92] `tesis-marco-teorico-profundidad` — ACTIVO (0/29)

- **Estado**: `[ ]` propuesto (planning completo). Sin aplicar.
- **Problema**: el Capitulo 2 no sostiene conceptualmente el uso operativo que el resto del documento hace de sus conceptos: el eje LLM ocupa cuatro parrafos con solo tres referencias (A-04); la exactitud se define con la formula binaria y se corrige al lado (A-05); se describe Whisper como si se usara cuando el sistema usa la transcripcion nativa de Twilio (M-03); PostgreSQL se justifica contra "lo no relacional" sin nombrar alternativas (M-04); y quedan una afirmacion sobre corpus EN/DE/PT sin respaldo (M-02) y la atribucion editorial de ITIL Service Operation 2011 (A-06, parcial).
- **Scope**: §2.4 (profundizar prompting/calibracion de confianza/alucinacion/idioma/evaluacion de LLM, A-04); §2.7 (definir la exactitud multiclase directamente y retirar la formula binaria, A-05); §2.5 (marcar Whisper como antecedente no utilizado y remitir a §6.4, M-03); §2.6 (comparar PostgreSQL con al menos dos alternativas concretas, M-04); §1.7 (citar o reformular la afirmacion sobre corpus EN/DE/PT, reutilizando refs de c-78, M-02); §2.2 (atribuir ITIL Service Operation 2011 a TSO/Cabinet Office; el `.bib` queda en c-78 B3, A-06).
- **Hallazgos**: A-04, A-05, M-03, M-04 (mas M-02 y A-06 parciales).
- **Dependencias**: aplicar tras C-80 (comparte `02-marco-teorico.tex` y `01-introduccion.tex`).
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/c-92-tesis-marco-teorico-profundidad/{proposal,design,tasks}.md`
  - `docs/Tesis/Correcciones/reconciliacion-cobertura.md` (N1)

### [C-93] `tesis-metodologia-rigor` — ACTIVO (0/29)

- **Estado**: `[ ]` propuesto (planning completo). Sin aplicar.
- **Problema**: el Cap. 4 declara un diseno metodologico cuya aritmetica y supuestos no son reproducibles: el tamaño muestral (95 % / 6,5 % / correccion por finitud) no reproduce n=200 (A-07); la cobertura de pruebas se afirma sin publicar reporte ni comando (A-08); no hay analisis de potencia a priori (A-09); la rotacion de operadores queda confundida con el efecto de operador (A-10); y el tercer criterio del umbral 85 % de §1.6 confunde el contraste de tiempos con la exactitud (A-03). Faltan ademas criterios de exclusion del corpus (M-05), la demarcacion metodo de investigacion vs construccion del artefacto (M-06) y la declaracion de los analistas etiquetadores (M-07).
- **Scope**: §4.4 (publicar o corregir el calculo del tamaño muestral, A-07; criterios de exclusion, M-05; analistas etiquetadores, M-07); §4.5/§6.7 (publicar el informe de cobertura y el comando o retraer las cifras, A-08); §4.8 (analisis de potencia a priori, A-09); §4.2/§4.8 (reconocer el confundido operador/mitades, A-10); §4.9 (demarcar o reubicar Scrumban, M-06); §1.6 (reformular el tercer criterio sin "zona de rechazo", A-03, coordinado con c-77 B1).
- **Hallazgos**: A-07, A-08, A-09, A-10, M-05, M-06, M-07, A-03.
- **Dependencias**: aplicar tras C-92 (comparte `04-marco-metodologico.tex` y `01-introduccion.tex`).
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/c-93-tesis-metodologia-rigor/{proposal,design,tasks}.md`
  - `docs/Tesis/Correcciones/reconciliacion-cobertura.md` (N2)

### [C-94] `tesis-implementacion-verificabilidad` — ACTIVO (0/19)

- **Estado**: `[ ]` propuesto (planning completo). Sin aplicar.
- **Problema**: los Caps. 5 y 6 afirman hechos que el repositorio no respalda: §6.7 declara pruebas e2e que validan N8N (A-11) y una suite de frontend de 89 pruebas con 98,6 % de cobertura (A-12); §6.4 informa una latencia telefonica de 12-15 s sin n, dispersion ni procedimiento y no atribuible dado C-17 (A-13); §6.8 presenta un ejemplo hipotetico como "caso concreto" (M-08); §6.1 declara preparacion para Kubernetes 1.30 sin manifiesto (M-09); §5.4 fija parametros de inferencia "optimizados" sin procedimiento (M-12); y la Tabla 5 lista tres de los puntos de entrada reales (M-13).
- **Scope**: retraer o reformular las pruebas e2e de N8N (A-11) y el recuento/cobertura de la suite de frontend re-midiendo en HEAD (A-12); reformular la latencia telefonica (A-13, coordinado con c-77 Grupo E); marcar el ejemplo del dashboard como hipotetico (M-08); acotar Kubernetes a trabajo futuro (M-09); retirar "optimizados" o documentar el procedimiento (M-12); completar la Tabla 5 y declararla no exhaustiva (M-13). El residuo textual de C-18 (Tabla 4 / §5.3) se referencia desde c-77 C3, sin duplicar.
- **Hallazgos**: A-11, A-12, A-13, M-08, M-09, M-12, M-13.
- **Dependencias**: aplicar tras C-93 (comparte `05-arquitectura.tex` y `06-implementacion.tex`; tambien despues de c-76/c-77/c-80 por coordinacion).
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/c-94-tesis-implementacion-verificabilidad/{proposal,design,tasks}.md`
  - `docs/Tesis/Correcciones/reconciliacion-cobertura.md` (N3)

### [C-95] `tesis-resultados-discusion-rigor` — ACTIVO (0/35)

- **Estado**: `[ ]` propuesto (planning completo). Sin aplicar.
- **Problema**: los Caps. 7, 8 y 9 describen resultados sin la evidencia que exigen: la normalidad que justifica Wilcoxon no reporta estadistico ni p (A-15); la discusion interpreta pero no interroga ni explica la confusion sistematica de Sistemas (A-20); el baseline TF-IDF+SVM se enuncia en una sola oracion sin procedimiento, particion, n ni codigo (A-21); la tipologia de errores no publica ningun ejemplo textual (M-10); los costos operativos no tienen fuente (M-16); y el Cap. 9 introduce una interpretacion estadistica que pertenece al Cap. 8 (A-25) y una generalizacion sobre LLM frente a clasificadores supervisados (A-23).
- **Scope**: §4.7/§7.1 (reportar W y p de Shapiro-Wilk, A-15); §8.1 (interrogacion critica con hipotesis rivales y explicacion de la confusion de Sistemas sobre la matriz 5x5, A-20); §8.3 (retirar o declarar no reproducible el baseline 78 % / F1 0,764, A-21); §7.4 (2-3 ejemplos textuales anonimizados, M-10); §8.4 (costos con fuente o cota explicita con supuestos, M-16); §9.1/§9.2 (acotar la interpretacion estadistica y la generalizacion, A-25/A-23).
- **Hallazgos**: A-15, A-20, A-21, M-10, M-16 (mas A-23 y A-25 parciales).
- **Dependencias**: aplicar tras C-94 (comparte `07-resultados.tex`, `08-discusion.tex`, `09-conclusiones.tex` y `04-marco-metodologico.tex`).
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/c-95-tesis-resultados-discusion-rigor/{proposal,design,tasks}.md`
  - `docs/Tesis/Correcciones/reconciliacion-cobertura.md` (N4)

### [C-96] `tesis-citas-tablas-evidencia` — ACTIVO (0/28)

- **Estado**: `[ ]` propuesto (planning completo). Sin aplicar.
- **Problema**: defectos transversales de trazabilidad de fuentes: la Tabla 1 (Cap. 3) compara seis soluciones comerciales sin cita, linea de fuente ni fecha de consulta y autoevalua la fila "Propuesta" (A-26); la definicion de empresa mediana atribuida a la SEPyME carece de cita y entrada bibliografica (M-01); queda una cita huerfana "(APA, 2017)" en §11.5; §1.7 y §6.1 rotulan a N8N como "codigo abierto" pese a su licencia Sustainable Use (A-27); §1.2/§1.8 caracterizan de forma inconsistente a la organizacion adoptante (B-01); ninguna de las nueve tablas declara fuente (APA 7) y la densidad de citas es desigual (Cap. 6 y Cap. 7).
- **Scope**: Tabla 1 con linea de fuente, cita y fecha de consulta por fila y separacion de la fila "Propuesta" (A-26); cita y entrada SEPyME para §1.1 y resolucion de la cita huerfana APA 2017 de §11.5 (M-01); corregir "codigo abierto" en §1.7/§6.1 (A-27); unificar la organizacion adoptante en §1.2/§1.8 (B-01); linea de fuente APA 7 en las nueve tablas (coordinado con c-80, duenio del formato); aumentar y equilibrar la densidad de citas reutilizando la bibliografia de c-78 (Cap. 3/6/7).
- **Hallazgos**: A-26, M-01 + cita huerfana APA 2017, A-27, B-01 (mas las dimensiones transversales de fuente de tablas y densidad de citas).
- **Dependencias**: aplicar tras C-95 (comparte `01-introduccion.tex`, `03-estado-del-arte.tex`, `05-arquitectura.tex`, `06-implementacion.tex`, `07-resultados.tex` y el `.bib`; tambien despues de c-78 y en coordinacion con c-80).
- **Governance**: BAJO
- **Leer antes**:
  - `openspec/changes/c-96-tesis-citas-tablas-evidencia/{proposal,design,tasks}.md`
  - `docs/Tesis/Correcciones/reconciliacion-cobertura.md` (N5)

---

## FASE 32 — Seguimiento de dependencias de seguridad (2026-10-19)

> Change post-roadmap de seguimiento: ejecuta el FOLLOW-UP de `pip-audit` que C-64 (vulnerabilidades-supply-chain, FASE 21) dejo declarado como deuda tecnica. NO forma parte del plan de cumplimiento ISO/NIST/Ley 25.326 (ya TOTALMENTE EJECUTADO); es una tarea de saneamiento posterior al roadmap.

### [C-97] `actualizar-dependencias-seguridad` — ARCHIVADO (2026-10-19, 14/14)

- **Estado**: `[x]` CREADO, APLICADO (14/14) y ARCHIVADO (2026-10-19; `openspec/changes/archive/2026-10-19-c-97-actualizar-dependencias-seguridad`). Governance MEDIO. Ejecuta el FOLLOW-UP de `pip-audit` declarado por `C-64` (FASE 21); NO forma parte del plan de cumplimiento, que ya quedo TOTALMENTE EJECUTADO. Specs sincronizadas: `supply-chain-security` y `ci-pipeline` modificadas.
- **Problema**: la lista de excepciones de `pip-audit` de C-64 registraba 10 hallazgos, 8 de ellos corregibles solo mediante una actualizacion mayor rompiente (7 advisories de `starlette 0.38.6` via `fastapi 0.115` y `PYSEC-2026-1845` de `pytest 8.3.3`), declarados como deuda tecnica pendiente (FOLLOW-UP). Mantener esa deuda engrosaba la superficie mitigada solo por excepcion.
- **Scope**:
  - Subir los pins de `App/Backend/requirements.txt`: `fastapi` 0.115.0 -> 0.135.0 (levanta el cap `starlette<0.39`), `starlette` 1.3.1 (pin explicito nuevo), `pytest` 9.1.1 y `pytest-asyncio` 1.4.0.
  - Podar 8 IDs de `scripts/security/pip_audit_exceptions.txt` (7 advisories de `starlette` + `PYSEC-2026-1845` de `pytest`), dejando solo los 2 hallazgos sin correccion publicada (`python-jose` PYSEC-2026-4298 y `ecdsa` PYSEC-2026-1325); eliminar el bloque FOLLOW-UP y ajustar el encabezado.
  - Regenerar `docs/openapi.json` con el generador canonico `scripts/export_openapi.py` (unico fallout de FastAPI 0.135: el schema OpenAPI); sin cambios en codigo de aplicacion.
  - Sin rotura de la suite: 1449 passed (baseline igual, 48 deselected, 1 xfailed); subconjunto de integracion PostgreSQL 48 passed.
- **Dependencias**: `C-64` (vulnerabilidades-supply-chain, FASE 21; ejecuta su FOLLOW-UP de `pip-audit`).
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/archive/2026-10-19-c-97-actualizar-dependencias-seguridad/{proposal,design,tasks}.md`
  - `openspec/specs/supply-chain-security/spec.md`, `openspec/specs/ci-pipeline/spec.md`

---

## Notas del analisis

### Estado actual del proyecto (verificado contra el codigo; actualizado 2026-10-19)

| Componente | Estado | Observaciones |
|------------|--------|---------------|
| Backend: clasificadores | COMPLETO | DeterministicClassifier, GeminiClassifier, HybridClassifier implementados y documentados; reintento acotado con backoff+jitter y fallback tras agotar intentos (C-58) |
| Backend: routes/endpoints | COMPLETO | CRUD incidentes, revision humana, auth, estadisticas, health |
| Backend: servicios | COMPLETO | IncidenteService, ClasificacionService, EstadisticasService |
| Backend: modelos ORM | COMPLETO | Tablas base (incidente, sector, estado, canal_origen, clasificacion_log) mas `users` (C-15) y columnas de timing (C-39, migracion 006) |
| Backend: repositorios | COMPLETO | Patron repositorio con sesion compartida, filtros dinamicos |
| Backend: keywords | COMPLETO | Mapa redistribuido en los 5 sectores canonicos (C-27) |
| Backend: util n8n_webhook | EN USO | `notify_n8n()` fire-and-forget desde el servicio; apunta al webhook N8N dedicado (C-33) |
| Backend: tests | COMPLETO | Suite offline SQLite (1449 passed, 48 deselected, 1 xfailed) + subconjunto de integracion PostgreSQL sobre base descartable (48 tests; C-19/C-32/C-45) |
| Backend: pseudonimizacion | COMPLETO | C-03; cifrado at-rest con Fernet |
| Backend: migraciones | COMPLETO | Alembic; migraciones 001-011 (la 006 agrega timing e2e, C-39; la 007 agrega `costo_guarda_contador`, C-45; la 008 agrega `telefonia_ingreso`, C-52; la 009 agrega `directorio_empleado` y la 010 `directorio_fecha_baja`, C-54; la 011 agrega `corpus_case_id`, C-70). La 012 (rol `mesa_de_ayuda`) la introduce c-60 (archivado 2026-10-06) |
| Backend: auth | COMPLETO | JWT Bearer (C-15) |
| Costo runtime: guarda | COMPLETO | C-45 bolsa global USD 10/semana, rate global y por origen, PostgreSQL 007, webhook pre-llamada de Twilio y fail-closed (archivado); C-58 la dimensiona al peor caso de intentos por clasificacion |
| N8N workflow JSON | COMPLETO | Canales cableados (C-04/C-05), compuerta de confianza de dos capas (C-38), wiring corregido (C-40), recuperacion robusta del sello de ingreso de telefonia (C-46), item de telefonia preservado a traves de la guarda de costo (C-47), auditoria de la rama de revision corregida (C-57) y modelo explicito + reintento acotado del agente (C-58) |
| Frontend: paginas | COMPLETO | ReportarIncidente, Administracion, Dashboard (C-23), Login (C-15), MisIncidentes, Directorio (C-89), MfaEnrollment (C-63b), Privacidad (c-66) |
| Frontend: componentes | COMPLETO | shadcn/ui, badges, indicadores, tablas, dialogos |
| Frontend: hooks/services | COMPLETO | React Query + Axios, todos los endpoints conectados |
| Frontend: tests | COMPLETO | Vitest + Testing Library (C-07); 365 tests en 57 archivos |
| Infra: Docker | COMPLETO | docker-compose.yml + nginx TLS (C-20); Dockerfiles multi-stage non-root (improve-dockerfiles) |
| Infra: CI/CD | COMPLETO | .github/workflows/ci.yml (C-09); incluye la suite y el CLI del preflight (C-41) |
| Infra: arranque | COMPLETO | scripts/up.sh / up.ps1 + Makefile (C-28); preflight de entorno y de costo (C-41) |
| Docs: anexos A-G | COMPLETO | C-10 documentation-annexes |
| Docs: guia operativa | COMPLETO | C-42 alinea README y guia operativa con el arranque; C-43 agrega `JWT_SECRET_KEY` a las tablas de entorno; C-45 documenta la guarda de costo (§11) (todos archivados) |
| Docs: rutas post-reestructuracion | COMPLETO | C-43 reemplaza `Gestion_Incidentes/` por `App/Backend/` en 7 documentos y anota la narrativa historica (archivado) |
| Docs: evaluacion y exportador OpenAPI | COMPLETO | C-44 corrige la invocacion del runner, elimina el generador inexistente de C-27, documenta el gate de corrida paga y arregla `export_openapi.py` (dummy de `JWT_SECRET_KEY` + rutas) (archivado) |
| Auth: JWT Bearer | COMPLETO | C-15 jwt-auth-backend-frontend |
| KB: knowledge-base | ACTUALIZADA | C-14 kb-sync-implementation-state |
| Twilio: TwiML script | COMPLETO | C-16 twilio-twiml-script |
| Seguridad: higiene de secretos | COMPLETO | C-37 (hook pre-commit + runbook + escaneo del lado GitHub) |
| Corpus: JSON multietiqueta | COMPLETO | C-27 rediseno-sectores-json (sintetico eliminado); corpus 200/200 con `tiempo_automatizado_s` (C-68 web 53/53 + correo 66/66; C-70 telefonia 81/81) |
| Timing e2e | IMPLEMENTADO | C-39; `ingresado_en` / `persistido_en` / `latencia_e2e_ms`. C-46 elimina la perdida silenciosa del sello en el canal telefonico (verificacion de runtime en vivo pendiente) |
| Backup scripts: PostgreSQL | COMPLETO | C-26 (pg_dump + rotacion de 7 dias) + c-65 (cifrado AES-256 en reposo, scheduler cron/systemd versionado, prueba de restauracion reproducible; plan de continuidad con RTO/RPO 24h) |
| N8N retention: 30 dias | CONFIGURADO | C-26 — EXECUTIONS_DATA_PRUNE y EXECUTIONS_DATA_MAX_AGE en docker-compose.yml |

Tabla reconciliada con el estado real el 2026-10-01: C-14..C-48 quedaron documentados en las FASE 12-17; C-52..C-55 en la FASE 18 (C-52, C-53, C-54 y C-55 archivados) y C-56..C-60 en la FASE 19 (C-57 y C-58 archivados). Actualizacion 2026-10-01: C-53 y C-59 quedaron archivados; C-67 quedo registrado (notificacion SMS diferida, FASE 20). Actualizacion 2026-10-01 (tarde): C-54 quedo ARCHIVADO (2026-10-01, 51/51) y la FASE 18 queda CERRADA; se aprobo el plan de cumplimiento ISO/NIST/Ley 25.326, registrado como planificado en la FASE 21 (C-61..C-66, aun sin crear). Actualizacion 2026-10-01 (noche): C-61 `compliance-gobernanza` quedo CREADO como change OPSX (FASE 21, 0/23, MEDIO, sin dependencias, habilita C-63); los totales se ajustan a 58 changes numeradas creadas (54 archivadas + 4 activos) y 5 planificadas sin crear (C-62..C-66); C-66 no depende de C-67 sino que C-67 depende de C-66. Actualizacion 2026-10-01 (noche, cierre): C-61 quedo ARCHIVADO (2026-10-01, 26/26) y su spec `security-governance-docs` fue creada; la FASE 21 quedo parcialmente ejecutada y los totales se ajustan a 58 changes numeradas creadas (55 archivadas + 3 activos) mas 1 de mantenimiento sin numero (56 archivadas en total) y 5 planificadas sin crear (C-62..C-66). Actualizacion 2026-10-05: C-69 `dedup-correlacion-altas` quedo ARCHIVADO (2026-10-05, 30/30; specs sincronizadas: added 5 — `incident-origin-correlation` creada, `incident-intake-guards` y `n8n-workflow` modificadas) y C-68 quedo en 58/63 (apply avanzado; corpus web 53/53 y correo 66/66 medido por el flujo N8N real). Se registro C-70 `softphone-corpus-telefonia` (FASE 23, 0/65, ALTO, OQ1..OQ6 resueltas; apply-ready). Totales: 61 changes numeradas creadas (56 archivadas + 5 activas: C-56, C-60, C-67, C-68 y C-70) mas 1 de mantenimiento sin numero (57 archivadas en total) y 5 planificadas sin crear (C-62..C-66). Actualizacion 2026-10-05 (tarde): C-70 quedo en 62/65 (apply completo y verificado; 8.1-8.3 operativas pendientes) y se propuso C-71 `hardening-clasificador-determinista` (FASE 24, 0/43, MEDIO, OQ1..OQ5 abiertas) tras medir que el clasificador determinista escala el 64% y su cortocircuito acierta ~51% (estricto) / ~76% (multietiqueta). Totales: 62 changes numeradas creadas (56 archivadas + 6 activas: C-56, C-60, C-67, C-68, C-70 y C-71) mas 1 de mantenimiento sin numero (57 archivadas en total) y 5 planificadas sin crear (C-62..C-66). Actualizacion 2026-10-05 (noche): C-71 `hardening-clasificador-determinista` quedo APLICADO (43/43; vocabulario+calibracion, `hybrid-v2`; calibracion pendiente de decision) y se propuso C-72 `unificar-clasificacion-telefonica` (FASE 25, 0/37, ALTO) para unificar la clasificacion telefonica a la cascada. Totales: 63 changes numeradas creadas (56 archivadas + 7 activas: C-56, C-60, C-67, C-68, C-70, C-71 y C-72) mas 1 de mantenimiento sin numero (57 archivadas en total) y 5 planificadas sin crear (C-62..C-66). (Instantaneas historicas fechadas; para el estado actual de la FASE 21 ver la Actualizacion 2026-10-19 (c-64 y c-65 archivados) mas abajo, donde C-64, C-65 y C-66 quedan creados y archivados y la FASE 21 queda TOTALMENTE EJECUTADA.)

Actualizacion 2026-10-12: C-68 `corpus-ingesta-n8n` quedo ARCHIVADO (2026-10-09, 63/63; spec `corpus-n8n-ingest` creada) y se registraron los cinco changes de correccion de la tesis por el dictamen CONEAU (nueva FASE 29): C-76 `tesis-correcciones-dictamen` (0/46), C-77 `tesis-errores-estadisticos-inferenciales` (0/49), C-78 `tesis-bibliografia-atribucion` (0/25), C-79 `tesis-aspectos-legales` (0/25) y C-80 `tesis-forma-evidencia-visual` (0/45), todos ACTIVOS. Totales: 74 entradas creadas documentadas (73 numeradas + 1 de mantenimiento sin numero) — 68 archivadas y 6 activas. El plan de auditoria (4 bloques, 32 items) queda cubierto por C-76..C-80.

Actualizacion 2026-10-15 (reconciliacion con el estado real de OpenSpec): se registraron como ARCHIVADOS los once changes de la FASE 30 — C-81 `frontend-rbac` (2026-10-13, 24/24), C-82 `rbac-redesign` (2026-10-13, 36/36), C-83 `revision-humana-info-completa` (2026-10-13, 18/18), C-84 `logout-navbar-y-toggle-password` (2026-10-15, 15/15), C-85 `revision-humana-contador-y-mensaje` (2026-10-15, 34/34), C-86 `rol-gestion-incidentes-ciclo-cierre` (2026-10-15, 61/61), C-87 `borrado-logico-incidentes` (2026-10-15, 25/25), C-88 `busqueda-incidentes-panel` (2026-10-15, 19/19), C-89 `ui-directorio-administrador` (2026-10-15, 19/19), C-90 `prioridad-critica-restringida` (2026-10-15, 17/17) y C-91 `sesion-jwt-cookie-rotativa` (2026-10-15, 48/48) — y se corrigio el ESTADO de C-68, que figuraba ACTIVO (58/63) y quedo ARCHIVADO (2026-10-09, 63/63). El conjunto ACTIVO sigue siendo de seis: C-67 (diferido), C-76, C-77, C-78, C-79 y C-80. Totales: 85 entradas creadas documentadas (84 numeradas + 1 de mantenimiento sin numero) — 79 archivadas y 6 activas.

Actualizacion 2026-10-19 (nueva auditoria): se registraron los cinco changes de correccion de la tesis por la NUEVA auditoria capitulo por capitulo (nueva FASE 31): C-92 `tesis-marco-teorico-profundidad` (0/29), C-93 `tesis-metodologia-rigor` (0/29), C-94 `tesis-implementacion-verificabilidad` (0/19), C-95 `tesis-resultados-discusion-rigor` (0/35) y C-96 `tesis-citas-tablas-evidencia` (0/28), todos ACTIVOS (planning completo, `openspec validate --strict` OK, sin aplicar). C-76..C-80 (FASE 29) siguen siendo los duenios del corpus, la estadistica/inferencia, la bibliografia, lo legal y la forma; C-92..C-96 cubren los hallazgos NUEVOS A/M/B de la re-auditoria (`docs/Tesis/Correcciones/auditoria-capitulos.md` + informe completo en `auditorias/`; cruce en `reconciliacion-cobertura.md`). C-18 queda STALE (el artefacto N8N ya fue corregido por c-29, commit ef656ac; residuo textual en c-77 C3). Orden recomendado de aplicacion: c-76 -> c-77 -> c-78 -> c-79 -> c-80 -> c-92 -> c-93 -> c-94 -> c-95 -> c-96. Totales: 90 entradas creadas documentadas (89 numeradas + 1 de mantenimiento sin numero) — 79 archivadas y 11 activas (C-67, C-76..C-80, C-92..C-96); instantanea previa al cierre de C-67, que queda archivado en la Actualizacion 2026-10-19 (cierre C-67) siguiente.

Actualizacion 2026-10-19 (cierre C-67): C-67 `notificacion-sms-llamante` quedo ARCHIVADO como NO REALIZADO (2026-10-19; 0/24; `--skip-specs`, specs principales sin tocar). Motivos: el spike de OQ3 cerro el 2026-09-23 con veredicto GO-WITH-CONSTRAINTS (SMS best-effort, correo como canal primario), `C-66 privacidad-transferencias` nunca fue creado, y la cadena "SMS" no aparece en la tesis (`docs/Tesis/v9 (IA)/paper/sections/`) ni en `knowledge-base/` (es backlog de completitud de software, no un entregable de la tesis). Totales: 90 entradas creadas documentadas (89 numeradas + 1 de mantenimiento sin numero) — 80 archivadas y 10 activas (C-76..C-80, C-92..C-96). Instantanea previa a la Actualizacion 2026-10-19 (c-66 archivado) siguiente, donde C-66 se crea y archiva y la FASE 21 queda con C-64 y C-65 planificados.

Actualizacion 2026-10-19 (c-66 archivado): C-66 `privacidad-transferencias` quedo CREADO, APLICADO (36/36; apply completo y revision humana firmada) y ARCHIVADO (2026-10-19; `openspec/changes/archive/2026-10-19-c-66-privacidad-transferencias`). Governance ALTO. Entrego la pseudonimizacion del numero llamante en los logs del guarda de costo con una clave HMAC DEDICADA (`cost_guard_caller_hmac_key`, independiente de la clave de pseudonimizacion Fernet), la superficie de privacidad en runtime (`/privacidad`) con procedimiento ARCO y plazos, la politica de retencion de logs, la justificacion por minimizacion del directorio y el instrumento de transferencia internacional (documentado, no firmado); corrigio dos inconsistencias documentales. Cierra los controles ISO 5.34, 8.12, 8.15 y 5.31. Specs sincronizadas: `privacy-runtime-surface` creada (capability nueva) y `runtime-cost-guard`, `security-governance-docs` y `employee-directory` modificadas (+7 agregados, 2 modificados, 1 removido). Con esto la FASE 21 deja solo C-64 `vulnerabilidades-supply-chain` y C-65 `backup-continuidad` como planificados (sin crear). Totales: 91 entradas creadas documentadas (90 numeradas + 1 de mantenimiento sin numero) — 81 archivadas y 10 activas (C-76..C-80, C-92..C-96).

Actualizacion 2026-10-19 (c-64 y c-65 archivados): C-64 `vulnerabilidades-supply-chain` (MEDIO) y C-65 `backup-continuidad` (ALTO) quedaron CREADOS, APLICADOS y ARCHIVADOS (2026-10-19; `openspec/changes/archive/2026-10-19-c-64-vulnerabilidades-supply-chain` y `openspec/changes/archive/2026-10-19-c-65-backup-continuidad`). C-64 (33/33) entrego `.github/dependabot.yml`, el job `security-scan` en CI (pip-audit + bandit + npm audit), pinning de imagenes Docker (nginx:1.31.7-alpine, ngrok/ngrok:3.39.8-debian), cotas superiores de dependencias y el documento de evaluacion de seguridad de proveedores; cierra los controles ISO 8.8, 8.28, 8.29 y 5.19-5.23 (trivy/SBOM evaluados y diferidos). C-65 (31/31; revision humana firmada, tarea 9.4) entrego el backup cifrado (openssl AES-256-CBC, `BACKUP_ENCRYPTION_PASSPHRASE`), el scheduler versionado (cron + systemd timer), la prueba de restauracion reproducible, `docs/seguridad/plan-continuidad.md` (RTO/RPO 24h; offsite/redundancia como accion del adoptante), la correccion del gap assessment y el Purpose real para `backup-scripts`; cierra los controles ISO 8.13, 8.14, 5.29, 5.30 y 5.33. Specs sincronizadas en el commit previo al archive (`--skip-specs`): `supply-chain-security` y `continuity-planning` creadas (capabilities nuevas); `ci-pipeline`, `security-governance-docs` (SGD-001 + SGD-016) y `backup-scripts` (BACKUP-005..008) modificadas. Con esto la FASE 21 del plan de cumplimiento ISO/NIST/Ley 25.326 queda TOTALMENTE EJECUTADA (C-61, C-62, C-63a/b/c, C-64, C-65 y C-66 archivados; no queda nada planificado). Totales: 93 entradas creadas documentadas (92 numeradas + 1 de mantenimiento sin numero) — 83 archivadas y 10 activas (C-76..C-80, C-92..C-96).

Actualizacion 2026-10-19 (c-97 archivado): C-97 `actualizar-dependencias-seguridad` (MEDIO) quedo CREADO, APLICADO (14/14) y ARCHIVADO (2026-10-19; `openspec/changes/archive/2026-10-19-c-97-actualizar-dependencias-seguridad`). Es un change post-roadmap que ejecuta el FOLLOW-UP de `pip-audit` declarado por C-64 (FASE 21), NO parte del plan de cumplimiento ISO/NIST/Ley 25.326 (ya TOTALMENTE EJECUTADO). Entrego: `fastapi` 0.115.0 -> 0.135.0 (levanta el cap `starlette<0.39`), `starlette` 1.3.1 (pin explicito nuevo), `pytest` 9.1.1 y `pytest-asyncio` 1.4.0; podo 8 IDs de `scripts/security/pip_audit_exceptions.txt` (7 advisories de `starlette` + `PYSEC-2026-1845` de `pytest`), dejando solo los 2 hallazgos sin correccion publicada (`python-jose` PYSEC-2026-4298 y `ecdsa` PYSEC-2026-1325); regenero `docs/openapi.json` (unico fallout de FastAPI 0.135); sin rotura de codigo de aplicacion (suite 1449 passed, baseline igual; integracion PostgreSQL 48 passed). Specs sincronizadas: `supply-chain-security` y `ci-pipeline` modificadas. Totales: 94 entradas creadas documentadas (93 numeradas + 1 de mantenimiento sin numero) — 84 archivadas y 10 activas (C-76..C-80, C-92..C-96).

Cambios que NO estan en el roadmap original porque se implementaron durante el desarrollo:
- Clasificador hibrido (completo)
- CRUD de incidentes (completo)
- Cola de revision humana (completa)
- Frontend completo (completo)
- Infraestructura Docker (completa)
- Keywords dictionary (completo)
- Pseudonymization module (completo — C-03)
- CI/CD pipeline (completo — C-09)
- Frontend testing (completo — C-07)
- Backend integration tests (completo — C-06)

---

## Primer change recomendado

Los changes C-46, C-47 y C-48 quedaron implementados, verificados y archivados (2026-09-22). Desde entonces tambien se archivaron C-52 (2026-09-30), C-53 (2026-10-01), C-54 (2026-10-01, 51/51), C-55 (2026-09-29), C-57 (2026-09-29), C-58 (2026-09-29), C-59 (2026-10-01), C-61 (2026-10-01, 26/26), C-69 (2026-10-05, 30/30), C-71 (2026-10-06, 43/43), C-60 (2026-10-06, 33/33), C-70 (2026-10-06, 72/72), C-72 (2026-10-07, 37/37), C-73 (2026-10-07, 23/23), C-74 (2026-10-07, 32/32), C-75 (2026-10-08, 14/14), C-56 (2026-10-08, 27/27), C-68 (2026-10-09, 63/63), C-81 (2026-10-13, 24/24), C-82 (2026-10-13, 36/36), C-83 (2026-10-13, 18/18), C-84 (2026-10-15, 15/15), C-85 (2026-10-15, 34/34), C-86 (2026-10-15, 61/61), C-87 (2026-10-15, 25/25), C-88 (2026-10-15, 19/19), C-89 (2026-10-15, 19/19), C-90 (2026-10-15, 17/17) y C-91 (2026-10-15, 48/48); y C-97 `actualizar-dependencias-seguridad` (2026-10-19, 14/14, post-roadmap, seguimiento de C-64).

Hay 10 changes ACTIVOS:
- **`c-76-tesis-correcciones-dictamen`** — 0/46 (FASE 29) — Governance MEDIO.
- **`c-77-tesis-errores-estadisticos-inferenciales`** — 0/49 (FASE 29) — Governance MEDIO.
- **`c-78-tesis-bibliografia-atribucion`** — 0/25 (FASE 29) — Governance ALTO.
- **`c-79-tesis-aspectos-legales`** — 0/25 (FASE 29) — Governance ALTO.
- **`c-80-tesis-forma-evidencia-visual`** — 0/45 (FASE 29) — Governance BAJO.
- **`c-92-tesis-marco-teorico-profundidad`** — 0/29 (FASE 31) — Governance MEDIO.
- **`c-93-tesis-metodologia-rigor`** — 0/29 (FASE 31) — Governance MEDIO.
- **`c-94-tesis-implementacion-verificabilidad`** — 0/19 (FASE 31) — Governance MEDIO.
- **`c-95-tesis-resultados-discusion-rigor`** — 0/35 (FASE 31) — Governance MEDIO.
- **`c-96-tesis-citas-tablas-evidencia`** — 0/28 (FASE 31) — Governance BAJO.

Los cinco changes de la FASE 29 son correcciones del documento de tesis (independientes del software) y se aplican en secuencia, en el orden C-76 -> C-77 -> C-78 -> C-79 -> C-80. Los cinco changes de la FASE 31 (C-92..C-96) cubren los hallazgos NUEVOS de la re-auditoria y se aplican a continuacion, en el orden C-92 -> C-93 -> C-94 -> C-95 -> C-96 (tras la FASE 29).

C-01..C-48, C-52, C-53, C-54, C-55, C-56, C-57, C-58, C-59, C-60, C-61, C-62, C-63, C-64, C-65, C-66, C-67, C-68, C-69, C-70, C-71, C-72, C-73, C-74, C-75, C-81..C-91 y C-97 estan archivados (C-21 no existe). C-49/C-50 nunca se crearon; `c-51` fue absorbido por C-52 y no se abre.

**Detalle de `c-52-telefonia-transcripcion-async`** (Gobernanza CRITICA; ARCHIVADO 2026-09-30):

- Cierra el gap del canal telefonico: la descripcion llegaba VACIA al `AI Agent` porque el evento
  `call-summary.complete` no trae la transcripcion y `<Record transcribe="true">` es solo ingles.
- Diseno: STT EN EL BACKEND con Google Gemini (transcripcion dedicada, `gemini-3.5-transcribe`,
  `verbatim`, via Interactions API, `store=False`) sobre la grabacion mono de Twilio; el backend
  es dueno de la descarga y de la transcripcion, pseudonimiza ANTES del handoff a n8n (cierra una
  fuga latente de PII), persiste una tabla intake cifrada, agrega la superficie de guarda
  `backend_stt` y sella `ingresado_en` en el callback del backend. Absorbe `c-51`.
- **Preguntas abiertas 1-3 RESUELTAS en apply**: (1) subir `google-genai` a `>=2.20.0` (el tipado de
  `transcription_config` llega en `2.13.0`); (2) `gemini-3.5-transcribe` esta Stable, ~USD 0.005/min
  (por debajo de Whisper); (3) se usa `language_codes=["es-419"]` (es-AR no soportado), con fallback
  a auto-detect o `es-MX`. Las preguntas de diseno 4-7 (retencion del audio, comportamiento ante
  fallo de STT/denegacion, drop de la suscripcion Event Streams, reescritura del `<Say>`) quedan registradas en el design del change archivado.
- **Leer antes**: `openspec/changes/archive/2026-09-30-c-52-telefonia-transcripcion-async/{proposal,design,tasks}.md`,
  `openspec/specs/n8n-workflow/spec.md`, `openspec/specs/runtime-cost-guard/spec.md`.

Pendientes planificados, en orden recomendado:

1. **`c-49-carga-corpus-db`**: cargar los 200 casos del corpus en una tabla dedicada
   (`corpus_incidente`), solo con la descripcion pseudonimizada, aislada de la tabla operativa,
   con FK nullable `incidente_id` -> `incidente.id`; temporal hasta poder correr el flujo completo.
2. **`c-50-corpus-timing-wiring`**: separar el contrato del loader de `evaluation/corpus.py`
   (carga para clasificacion vs analisis de timing), derivar `tiempo_automatizado_s` de
   `latencia_e2e_ms` medido y cablear `stats.py`/Wilcoxon al reporte.

Operativo para habilitar el pipeline pago (fuera de changes):
- Cargar la credencial real de Twilio (`TWILIO_AUTH_TOKEN`) y apuntar la Voice URL de la
  consola a `https://<host>/api/v1/cost-guard/twilio/voice`; con eso la validacion de firma
  de C-45 se activa sola.
- Verificacion manual en N8N en vivo de C-46 (tareas 5.2/5.3) y C-47 (tarea 5.4): confirmar que
  `.first()` resuelve, que el incidente telefonico persiste `ingresado_en` no nulo y que el
  `AI Agent` recibe el item sellado tras la guarda.

Deuda menor pendiente (no bloqueante):
- Tesis post-pipeline: reconciliar cap. 7 con el corpus real y corregir 4.3/4.8/cap. 11.

Para avanzar:
- Workstream aprobado: el plan de cumplimiento ISO/NIST/Ley 25.326 (`docs/cumplimiento/plan-cambios-cumplimiento.md`), en la FASE 21. C-61 (2026-10-01), C-62 (2026-10-08), C-63a/b/c (2026-10-08), C-64 (2026-10-19), C-65 (2026-10-19) y C-66 (2026-10-19) quedaron ARCHIVADOS. El workstream quedo TOTALMENTE EJECUTADO: no quedan changes planificados.
- `c-56`: ARCHIVADO (2026-10-08, 27/27); smoke manual confirmado end-to-end (operador resuelto + fallback + auditoria); spec `notification-routing` creada.
- `c-60`: ARCHIVADO (2026-10-06, 33/33).
- `c-67`: CERRADO NO REALIZADO y ARCHIVADO (2026-10-19, `--skip-specs`, 0/24). El spike de OQ3 cerro el 2026-09-23 con veredicto GO-WITH-CONSTRAINTS (SMS best-effort, correo primario); `C-66 privacidad-transferencias` se creo y archivo despues (2026-10-19, 36/36); SMS no es entregable de la tesis. No hay nada que aplicar en `c-67`.
- `c-68`: ARCHIVADO (2026-10-09, 63/63); harness de ingesta web/correo verificado (PASS, 0 CRITICAL), W1/W3 resueltos, W2 aceptado, corpus 200/200; spec `corpus-n8n-ingest` creada.
- `c-70`: ARCHIVADO (2026-10-06, 72/72); corrida completa de los 81 casos y write-back realizados; corpus 200/200 cargable. Governance ALTO.
