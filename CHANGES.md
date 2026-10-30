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

C-76 tesis-correcciones-dictamen (ninguna — documento de tesis)          [APLICADO — 47/49; MEDIO]
 └── C-77 tesis-errores-estadisticos-inferenciales (aplicar tras C-76)   [APLICADO — 50/51; MEDIO]
      └── C-78 tesis-bibliografia-atribucion (aplicar tras C-77)         [APLICADO — 24/25; HIGH]
            └── C-79 tesis-aspectos-legales (aplicar tras C-78)           [APLICADO — 24/25; HIGH]
                └── C-80 tesis-forma-evidencia-visual (aplicar tras C-79) [APLICADO — 40/45; BAJO]

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

C-92 tesis-marco-teorico-profundidad (aplicar tras C-80)         [APLICADO — 28/29; MEDIO]
 └── C-93 tesis-metodologia-rigor (aplicar tras C-92)            [APLICADO — 28/29; MEDIO]
      └── C-94 tesis-implementacion-verificabilidad (tras C-93)  [APLICADO — 23/25; MEDIO]
           └── C-95 tesis-resultados-discusion-rigor (tras C-94) [APLICADO — 35/36; MEDIO]
                └── C-96 tesis-citas-tablas-evidencia (tras C-95)[APLICADO — 27/28; BAJO]

--- FASE 32: Seguimiento de dependencias de seguridad (2026-10-19) ---

C-97 actualizar-dependencias-seguridad (C-64)             [ARCHIVADO 2026-10-19 — 14/14; MEDIO; ejecuta el FOLLOW-UP de pip-audit de C-64; specs: supply-chain-security y ci-pipeline modificadas]
```

### Paralelismo por fase

**GATE 0: C-01 foundation-setup** COMPLETADO
  → C-02 notify-n8n-hook                    [Agente A]
  → C-03 pseudonymization-module            [Agente B]
  → C-07 frontend-testing-setup             [Agente C]
  ← PRIMER FORK: 3 changes en paralelo

**GATE 1: C-02 (completado), C-03 (completado)**               ← SEGUNDO FORK
  → C-04 n8n-workflow-validation            [Agente A]
  → C-06 backend-integration-tests          [Agente B]
  → C-08 evaluation-framework               [Agente C]

**GATE 2: C-04** COMPLETADO
  → C-05 n8n-channel-triggers               [Agente A]

**GATE 3: C-05 (completado), C-06 (completado), C-07 (completado), C-08 (completado)**
  → C-09 ci-cd-pipeline                     [Agente A, B, C]

**GATE 4: C-09** COMPLETADO
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
  - Escribir tests de integracion para `POST /api/v1/incidentes` (creacion + clasificacion)
  - Escribir tests de integracion para `GET /api/v1/incidentes` (listado con filtros, paginacion)
  - Escribir tests de integracion para `GET /api/v1/incidentes/{id}` (detalle + 404)
  - Escribir tests de integracion para `PATCH /api/v1/incidentes/{id}` (actualizacion parcial)
  - Escribir tests de integracion para `GET /api/v1/clasificaciones/revision-pendiente` (cola FIFO)
  - Escribir tests de integracion para `PATCH /api/v1/clasificaciones/{id}/validar` (validacion humana)
  - Escribir tests de integracion para `GET /api/v1/health` (health check)
  - Usar `conftest.py` existente con SQLite in-memory + fixture `client` ASGI
  - Cobertura objetivo: > 85% en modulos `routes/`, `services/`, `repositories/` (89% logrado)
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

**Total**: 0 changes ACTIVOS y 157 entradas ARCHIVADAS (159 directorios en `openspec/changes/archive/`; numeracion C-01..C-160, c-63 se cuenta como un change con sus tres partes c-63a/b/c; la FASE 36 (C-130..C-142), la FASE 37 (C-143, 13/13), la FASE 38 (C-144, 18/18), la FASE 39 (C-145, 77/77), la FASE 40 (C-146, 22/23 con la 6.1 bloqueada por acceso externo, y C-147, 23/23), la FASE 41 (C-148, 50/52), la FASE 42 (C-149, 21/22), la FASE 43 (C-150, 26/28), la FASE 44 (C-151, 20/20), la FASE 45 (C-153, 42/42) la FASE 46 (C-152, 12/12, y C-154, 21/21) la FASE 47 (C-155, 17/17, C-156, 27/27, y C-157, 21/21) y la FASE 48 (C-158, 41/42 con la 7.1 diferida a los autores, C-159, 39/39, y C-160, 42/42) estan ARCHIVADAS; C-135 ARCHIVADO el 2026-10-26 con 5.2 justificada, C-140 (73/73) y C-141 (52/52) el 2026-10-27, C-150 el 2026-10-27 y C-151, C-152, C-153 y C-154 el 2026-10-28; C-158, C-159 y C-160 el 2026-10-29). C-21, C-49 y C-50 nunca se crearon; C-51 fue absorbido por C-52 y no se abre. Release vigente: `v1.2.7` (tag anotado sobre `bc6a63ca43c2738cd2904ebca8890529963ac3cd`, 2026-10-30; 112 paginas medidas: cuerpo 101, anexos 11; cuerpo dentro del tope de 100). Los changes c-161 a c-164 (FASES 49 a 51) ya estan publicados en `main`.
**Planificadas (NO creadas)**: ninguna. El plan de cumplimiento (FASE 21) quedo TOTALMENTE EJECUTADO: C-61 `compliance-gobernanza` (MEDIO), C-62 `hardening-infra-red` (ALTO) y C-63 `identidad-accesos-claves` (CRITICO, split en c-63a/b/c) quedaron ARCHIVADOS (2026-10-01, 2026-10-08 y 2026-10-08), con sus specs `security-governance-docs`, `infra-network-hardening` e `identity-access-hardening`; C-64 `vulnerabilidades-supply-chain` (MEDIO) quedo ARCHIVADO (2026-10-19, 33/33), con su spec `supply-chain-security` creada y `ci-pipeline` y `security-governance-docs` modificadas; C-65 `backup-continuidad` (ALTO) quedo ARCHIVADO (2026-10-19, 31/31), con su spec `continuity-planning` creada y `backup-scripts` modificada; y C-66 `privacidad-transferencias` (ALTO) quedo creado y ARCHIVADO (2026-10-19, 36/36), con su spec `privacy-runtime-surface` creada y `runtime-cost-guard`, `security-governance-docs` y `employee-directory` modificadas. Ver `docs/cumplimiento/plan-cambios-cumplimiento.md`.
**Camino critico (software)**: 7 changes (C-01 → C-02 → C-04 → C-05 → C-08 → C-09 → C-10).
**Gates de paralelismo**: 5 gates (permite hasta 3 agentes simultaneos).
**Fases**: 1-52 (la FASE 9 quedo vacia; los changes que alli se preveian se documentan en la FASE 12; la FASE 18 agrupa C-52..C-55, ya CERRADA, la FASE 19 agrupa los changes de endurecimiento, auditoria y herramientas C-56..C-60, la FASE 20 agrupa la notificacion SMS diferida C-67 (archivado 2026-10-19 como NO REALIZADO), la FASE 21 agrupa el plan de cumplimiento ISO/NIST/Ley 25.326, TOTALMENTE EJECUTADA, con C-61 archivado (2026-10-01), C-62 archivado (2026-10-08), C-63a/b/c archivados (2026-10-08), C-64 archivado (2026-10-19), C-65 archivado (2026-10-19) y C-66 archivado (2026-10-19), la FASE 22 agrupa la ingesta del corpus por el flujo N8N real con C-69 archivado (2026-10-05) y C-68 archivado (2026-10-09), la FASE 23 agrupa la medicion del corpus por telefonia real con C-70 archivado (2026-10-06), la FASE 24 agrupa el endurecimiento del clasificador determinista con C-71 archivado (2026-10-06), la FASE 25 agrupa la unificacion de la clasificacion telefonica con C-72 archivado (2026-10-07), la FASE 26 agrupa la pseudonimizacion de numeros de tarjeta hablados con C-73 archivado (2026-10-07), la FASE 27 agrupa la calibracion del cortocircuito determinista con C-74 archivado (2026-10-07), y la FASE 28 agrupa la sincronizacion documental N8N con C-75 archivado (2026-10-08), y la FASE 29 agrupa las correcciones de la tesis por el dictamen CONEAU (C-76..C-80), con C-76..C-80 ARCHIVADOS (C-80 el 2026-10-21), independientes del software, aplicados en secuencia; y la FASE 30 agrupa el RBAC, el ciclo de cierre y la sesion (C-81..C-91), once changes ARCHIVADOS — C-81..C-83 el 2026-10-13 y C-84..C-91 el 2026-10-15; y la FASE 31 agrupa las correcciones de la tesis por la nueva auditoria (C-92..C-96), cinco changes ARCHIVADOS el 2026-10-20, independientes del software, aplicados en secuencia despues de la FASE 29; y las FASES 33, 34 y 35 agrupan el cierre post-roadmap: C-98..C-101 (2026-10-20), C-102..C-119 (2026-10-21) y C-120..C-124 (2026-10-22), todos ARCHIVADOS; la FASE 35 bis agrupa los changes de infraestructura y dependencias de Luca (C-125, C-126, C-127 y C-129, ARCHIVADOS el 2026-10-22, y C-128, ARCHIVADO el 2026-10-23 (22/22, alcance reducido)); y la FASE 36 agrupa las correcciones de la tesis por el dictamen CONEAU v10/v1.1.1 (C-130..C-142), trece changes (C-130..C-141 creados el 2026-10-22 y C-142 el 2026-10-23) aplicados en secuencia tras el gate G0 de C-141 y con la release `v1.2.0` publicada el 2026-10-26: todos ARCHIVADOS (C-130..C-139 y C-142 el 2026-10-26, con C-135 en 35/35 por la justificacion de la 5.2; C-140 (73/73) y C-141 (52/52) el 2026-10-27); y la FASE 37 agrupa la publicacion de la evidencia de evaluacion (C-143), un change ARCHIVADO el 2026-10-23 (13/13, BAJO) independiente de la FASE 36); y la FASE 38 agrupa la declaracion de procedencia real de los ajustes del clasificador y la ausencia de un corpus de preproduccion (C-144), un change ARCHIVADO el 2026-10-23 (18/18, MEDIO) que supersede parcialmente a C-130 (D9) y C-142 (D11/D13/T08) del PR #40); la FASE 39 agrupa la correccion factual y la release `v1.2.1` (C-145, ARCHIVADO el 2026-10-26, 77/77, ALTO); y la FASE 40 agrupa la compactacion y la release `v1.2.2` con C-146 (ARCHIVADO el 2026-10-27, 22/23, 6.1 bloqueada por acceso externo) y C-147 (ARCHIVADO el 2026-10-27, 23/23, ALTO)); la FASE 41 agrupa la sincronizacion de la base de conocimiento y los docs con el stack vigente (C-148, ARCHIVADO el 2026-10-27, 50/52); y la FASE 42 agrupa la actualizacion de dependencias del backend y el endurecimiento de la barrera documental (C-149, ARCHIVADO el 2026-10-27, 21/22); la FASE 43 agrupa el cierre de residuales y la separacion del contrato del corpus (C-150, ARCHIVADO el 2026-10-27, 26/28); la FASE 44 agrupa la correccion del pin de google-genai en el material de referencia y la ampliacion de la barrera documental (C-151, ARCHIVADO el 2026-10-28, 20/20); la FASE 45 agrupa el endurecimiento del directorio para datos reales (C-153, ARCHIVADO el 2026-10-28, 42/42); y la FASE 46 agrupa la regularizacion del indice (C-152, ARCHIVADO el 2026-10-28, 12/12, y C-154, ARCHIVADO el 2026-10-28, 21/21); la FASE 47 regulariza el indice con C-155 (ARCHIVADO el 2026-10-28, 17/17), C-156 (27/27) y C-157 (21/21); y la FASE 48 agrupa las correcciones de la tesis por el dictamen CONEAU v10/v1.2.5 del 2026-10-28, con C-158, C-159 y C-160 ARCHIVADOS el 2026-10-29; la FASE 49 agrupa el cierre de marcadores y decisiones del dictamen CONEAU v10/v1.2.5 (C-161 y C-162, ARCHIVADOS el 2026-10-29); la FASE 50 agrupa las recomendaciones 9 a 13 del dictamen (C-163, ARCHIVADO el 2026-10-29); la FASE 51 agrupa los residuales de deriva documental del dictamen (C-164, ARCHIVADO el 2026-10-29); y la FASE 52 agrupa el programa de medicion de la campana complementaria (C-165 a C-169, ACTIVOS: C-168 APLICADO con el archive pendiente, C-166 en aplicacion, C-165 y C-167 con el apply pendiente y C-169 GATEADO)).

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

- **Estado**: `[x]` aplicado y archivado (2026-10-08, 27/27 — `openspec/changes/archive/2026-10-08-c-56-notificaciones-por-rol`; verify PASS con el smoke manual confirmado).
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

> Changes sobre el documento academico (LaTeX, `docs/Tesis/v9 (IA)/paper/`), independientes del software. Se aplican EN SECUENCIA porque comparten archivos `.tex` (en especial `08-discusion.tex` y `09-conclusiones.tex`). C-76 (49/49), C-77 (51/51), C-78 (25/25) y C-79 (25/25) quedaron APLICADOS y ARCHIVADOS el 2026-10-20; C-80 (45/45) quedo APLICADO y ARCHIVADO el 2026-10-21. La tesis v9 se recompilo con MiKTeX el 2026-10-20 (xelatex -> biber -> xelatex -> xelatex; 103 paginas, 0 errores fatales, 48/48 bibliografia), cubriendo la recompilacion que estaba diferida en el bloque. La unica tarea abierta de C-80 son las capturas de UI (6.5/6.6) y su verificacion (8.2), mas 6.4 (cerrable por contingencia) y el ajuste de 6.9. El registro acumulativo del dictamen vive en `docs/Tesis/Correcciones/dictamen-correcciones.md`. El plan de auditoria (4 bloques, 32 items) queda cubierto por C-76..C-80; el mapeo item -> change esta al final de ese registro.

### [C-76] `tesis-correcciones-dictamen` — ARCHIVADO (2026-10-20, 49/49)

- **Estado**: `[x]` CREADO, APLICADO (49/49) y ARCHIVADO (2026-10-20; `openspec/changes/archive/2026-10-20-c-76-tesis-correcciones-dictamen`).
- **Problema**: la tesis todavia reporta numeros del corpus sintetico descartado en C-27 (3 clases con "Operaciones", exactitud 92 %, F1 0,919, Wilcoxon W=0 falso).
- **Scope**: alinear Cap. 4/7/8 y los capitulos que citan numeros con el corpus real de 200 casos; grupo T1-T7 (trazabilidad y existencia de datos experimentales, ventana temporal, instrumento manual); Anexos F/H y `main.pdf`.
- **Dependencias**: ninguna (documento de tesis).
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/c-76-tesis-correcciones-dictamen/{proposal,design,tasks}.md`
  - `docs/Tesis/Correcciones/dictamen-correcciones.md` (P1.0/P1, T1-T7)
  - `data/corpus_evaluacion_pseudonimizado.json`, `evaluation/report.md`

### [C-77] `tesis-errores-estadisticos-inferenciales` — ARCHIVADO (2026-10-20, 51/51)

- **Estado**: `[x]` CREADO, APLICADO (51/51; OQ1-OQ6 resueltas; ampliado con Grupo E - Opcion A del tiempo automatico telefonico) y ARCHIVADO (2026-10-20; `openspec/changes/archive/2026-10-20-c-77-tesis-errores-estadisticos-inferenciales`).
- **Problema**: errores estadisticos e inferenciales (formula del tamano del efecto, convencion de W, W+/W-, calibracion, "varianza casi diez veces menor", horas-persona, universo 3.700).
- **Scope**: reparar la estadistica y la coherencia metodologica; alinear `evaluation/stats.py`; cruce confianza x acierto; calculo del tamano muestral.
- **Dependencias**: aplicar tras C-76.
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/c-77-tesis-errores-estadisticos-inferenciales/{proposal,design,tasks}.md`
  - `evaluation/stats.py`, `evaluation/report.md`

### [C-78] `tesis-bibliografia-atribucion` — ARCHIVADO (2026-10-20, 25/25)

- **Estado**: `[x]` CREADO, APLICADO (25/25; min. 12 refs; OQ-B3-1 resuelta 2026-10-12) y ARCHIVADO (2026-10-20; `openspec/changes/archive/2026-10-20-c-78-tesis-bibliografia-atribucion`).
- **Problema**: misatribucion a Revina et al. (2020) (BERT/91 %/transferencia: falso); 2 citas fabricadas de v7 ya retiradas; claims sin cita (88-94 %); higiene de citas (Landis & Koch, Stallings/Brown, Jurafsky, et al.).
- **Scope**: reescribir 3.3 y 8.2 con la conclusion real de Revina; incorporar 12 refs arbitradas 2023-2026; corregir metadatos del `.bib`; re-verificacion por DOI.
- **Dependencias**: aplicar tras C-77.
- **Governance**: ALTO (integridad academica)
- **Leer antes**:
  - `openspec/changes/c-78-tesis-bibliografia-atribucion/{proposal,design,tasks}.md`
  - `docs/Tesis/v9 (IA)/Bibliography_base.bib`, `docs/Tesis/v9 (IA)/verify_citations.py`

### [C-79] `tesis-aspectos-legales` — ARCHIVADO (2026-10-20, 25/25)

- **Estado**: `[x]` CREADO, APLICADO (25/25; OQ-L1/L1b/L2/L5 resueltas 2026-10-12) y ARCHIVADO (2026-10-20; `openspec/changes/archive/2026-10-20-c-79-tesis-aspectos-legales`).
- **Problema**: capitulo legal con defectos de correccion juridica: retencion contradictoria ("indefinida" vs "30 dias") sin politica de supresion, base legal "legitimo interes" (GDPR, no existe en Ley 25.326), adecuacion europea mal explicada (bidireccional), transferencia telefonica pre-pseudonimizacion no declarada (Twilio) y fuentes juridicas sin control de vigencia.
- **Scope**: reescribir 11.1-11.3; plazo de conservacion concreto + politica de supresion al vencimiento; base art. 5 inc. 2 ap. b/d; Decision 2003/490/CE + revalidacion 2024; audio crudo + numero a EE.UU. antes de pseudonimizar; instrumento del art. 12; revision de vigencia de las fuentes citadas.
- **Dependencias**: aplicar tras C-78.
- **Governance**: ALTO (legal / privacidad)
- **Leer antes**:
  - `openspec/changes/c-79-tesis-aspectos-legales/{proposal,design,tasks}.md`
  - `docs/cumplimiento/marco-legal-ar-2026.md`, `docs/seguridad/registro-requisitos-legales.md`
  - `docs/runbook-verificacion-telefonia-c52.md`

### [C-80] `tesis-forma-evidencia-visual` — ARCHIVADO (2026-10-21, 45/45)

- **Estado**: `[x]` ARCHIVADO (2026-10-21, 45/45). Las 4 tareas que estaban abiertas (capturas de UI 6.5/6.6 panel admin y dashboard, verificacion de las 8 figuras 8.2, 6.4 por contingencia y ajuste de 6.9) quedaron cerradas; la tesis se recompilo y el change se archivo en el cierre del roadmap (2026-10-22).
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

> Changes sobre el documento academico (LaTeX, `docs/Tesis/v9 (IA)/paper/`), derivados de una NUEVA auditoria capitulo por capitulo (`docs/Tesis/Correcciones/auditoria-capitulos.md`) y del informe completo (`auditorias/Auditoria_Tesis_Gomez_Bustos_Sevilla_040802026.pdf`, 105 hallazgos: 28 criticos / 34 altos / 29 medios / 14 bajos). El cruce con los changes existentes esta en `docs/Tesis/Correcciones/reconciliacion-cobertura.md`. C-76..C-80 (FASE 29) siguen siendo los duenios del corpus, la estadistica/inferencia, la bibliografia, lo legal y la forma; C-92..C-96 cubren los hallazgos NUEVOS A/M/B que los cinco changes previos no abordan. C-18 quedo STALE (el artefacto N8N ya fue corregido por c-29, commit ef656ac; solo resta el residuo textual, en c-77 C3). C-92 (29/29), C-93 (29/29), C-94 (25/25), C-95 (36/36) y C-96 (28/28) quedaron APLICADOS y ARCHIVADOS el 2026-10-20, tras la recompilacion de la tesis v9 (103 paginas, MiKTeX). Se aplican EN SECUENCIA porque comparten archivos `.tex`. Orden aplicado: c-76 -> c-77 -> c-78 -> c-79 -> c-80 -> c-92 -> c-93 -> c-94 -> c-95 -> c-96.

### [C-92] `tesis-marco-teorico-profundidad` — ARCHIVADO (2026-10-20, 29/29)

- **Estado**: `[x]` CREADO, APLICADO (29/29) y ARCHIVADO (2026-10-20; `openspec/changes/archive/2026-10-20-c-92-tesis-marco-teorico-profundidad`).
- **Problema**: el Capitulo 2 no sostiene conceptualmente el uso operativo que el resto del documento hace de sus conceptos: el eje LLM ocupa cuatro parrafos con solo tres referencias (A-04); la exactitud se define con la formula binaria y se corrige al lado (A-05); se describe Whisper como si se usara cuando el sistema usa la transcripcion nativa de Twilio (M-03); PostgreSQL se justifica contra "lo no relacional" sin nombrar alternativas (M-04); y quedan una afirmacion sobre corpus EN/DE/PT sin respaldo (M-02) y la atribucion editorial de ITIL Service Operation 2011 (A-06, parcial).
- **Scope**: §2.4 (profundizar prompting/calibracion de confianza/alucinacion/idioma/evaluacion de LLM, A-04); §2.7 (definir la exactitud multiclase directamente y retirar la formula binaria, A-05); §2.5 (marcar Whisper como antecedente no utilizado y remitir a §6.4, M-03); §2.6 (comparar PostgreSQL con al menos dos alternativas concretas, M-04); §1.7 (citar o reformular la afirmacion sobre corpus EN/DE/PT, reutilizando refs de c-78, M-02); §2.2 (atribuir ITIL Service Operation 2011 a TSO/Cabinet Office; el `.bib` queda en c-78 B3, A-06).
- **Hallazgos**: A-04, A-05, M-03, M-04 (mas M-02 y A-06 parciales).
- **Dependencias**: aplicar tras C-80 (comparte `02-marco-teorico.tex` y `01-introduccion.tex`).
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/c-92-tesis-marco-teorico-profundidad/{proposal,design,tasks}.md`
  - `docs/Tesis/Correcciones/reconciliacion-cobertura.md` (N1)

### [C-93] `tesis-metodologia-rigor` — ARCHIVADO (2026-10-20, 29/29)

- **Estado**: `[x]` CREADO, APLICADO (29/29) y ARCHIVADO (2026-10-20; `openspec/changes/archive/2026-10-20-c-93-tesis-metodologia-rigor`).
- **Problema**: el Cap. 4 declara un diseno metodologico cuya aritmetica y supuestos no son reproducibles: el tamaño muestral (95 % / 6,5 % / correccion por finitud) no reproduce n=200 (A-07); la cobertura de pruebas se afirma sin publicar reporte ni comando (A-08); no hay analisis de potencia a priori (A-09); la rotacion de operadores queda confundida con el efecto de operador (A-10); y el tercer criterio del umbral 85 % de §1.6 confunde el contraste de tiempos con la exactitud (A-03). Faltan ademas criterios de exclusion del corpus (M-05), la demarcacion metodo de investigacion vs construccion del artefacto (M-06) y la declaracion de los analistas etiquetadores (M-07).
- **Scope**: §4.4 (publicar o corregir el calculo del tamaño muestral, A-07; criterios de exclusion, M-05; analistas etiquetadores, M-07); §4.5/§6.7 (publicar el informe de cobertura y el comando o retraer las cifras, A-08); §4.8 (analisis de potencia a priori, A-09); §4.2/§4.8 (reconocer el confundido operador/mitades, A-10); §4.9 (demarcar o reubicar Scrumban, M-06); §1.6 (reformular el tercer criterio sin "zona de rechazo", A-03, coordinado con c-77 B1).
- **Hallazgos**: A-07, A-08, A-09, A-10, M-05, M-06, M-07, A-03.
- **Dependencias**: aplicar tras C-92 (comparte `04-marco-metodologico.tex` y `01-introduccion.tex`).
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/c-93-tesis-metodologia-rigor/{proposal,design,tasks}.md`
  - `docs/Tesis/Correcciones/reconciliacion-cobertura.md` (N2)

### [C-94] `tesis-implementacion-verificabilidad` — ARCHIVADO (2026-10-20, 25/25)

- **Estado**: `[x]` CREADO, APLICADO (25/25) y ARCHIVADO (2026-10-20; `openspec/changes/archive/2026-10-20-c-94-tesis-implementacion-verificabilidad`).
- **Problema**: los Caps. 5 y 6 afirman hechos que el repositorio no respalda: §6.7 declara pruebas e2e que validan N8N (A-11) y una suite de frontend de 89 pruebas con 98,6 % de cobertura (A-12); §6.4 informa una latencia telefonica de 12-15 s sin n, dispersion ni procedimiento y no atribuible dado C-17 (A-13); §6.8 presenta un ejemplo hipotetico como "caso concreto" (M-08); §6.1 declara preparacion para Kubernetes 1.30 sin manifiesto (M-09); §5.4 fija parametros de inferencia "optimizados" sin procedimiento (M-12); y la Tabla 5 lista tres de los puntos de entrada reales (M-13).
- **Scope**: retraer o reformular las pruebas e2e de N8N (A-11) y el recuento/cobertura de la suite de frontend re-midiendo en HEAD (A-12); reformular la latencia telefonica (A-13, coordinado con c-77 Grupo E); marcar el ejemplo del dashboard como hipotetico (M-08); acotar Kubernetes a trabajo futuro (M-09); retirar "optimizados" o documentar el procedimiento (M-12); completar la Tabla 5 y declararla no exhaustiva (M-13). El residuo textual de C-18 (Tabla 4 / §5.3) se referencia desde c-77 C3, sin duplicar.
- **Hallazgos**: A-11, A-12, A-13, M-08, M-09, M-12, M-13.
- **Dependencias**: aplicar tras C-93 (comparte `05-arquitectura.tex` y `06-implementacion.tex`; tambien despues de c-76/c-77/c-80 por coordinacion).
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/c-94-tesis-implementacion-verificabilidad/{proposal,design,tasks}.md`
  - `docs/Tesis/Correcciones/reconciliacion-cobertura.md` (N3)

### [C-95] `tesis-resultados-discusion-rigor` — ARCHIVADO (2026-10-20, 36/36)

- **Estado**: `[x]` CREADO, APLICADO (36/36) y ARCHIVADO (2026-10-20; `openspec/changes/archive/2026-10-20-c-95-tesis-resultados-discusion-rigor`).
- **Problema**: los Caps. 7, 8 y 9 describen resultados sin la evidencia que exigen: la normalidad que justifica Wilcoxon no reporta estadistico ni p (A-15); la discusion interpreta pero no interroga ni explica la confusion sistematica de Sistemas (A-20); el baseline TF-IDF+SVM se enuncia en una sola oracion sin procedimiento, particion, n ni codigo (A-21); la tipologia de errores no publica ningun ejemplo textual (M-10); los costos operativos no tienen fuente (M-16); y el Cap. 9 introduce una interpretacion estadistica que pertenece al Cap. 8 (A-25) y una generalizacion sobre LLM frente a clasificadores supervisados (A-23).
- **Scope**: §4.7/§7.1 (reportar W y p de Shapiro-Wilk, A-15); §8.1 (interrogacion critica con hipotesis rivales y explicacion de la confusion de Sistemas sobre la matriz 5x5, A-20); §8.3 (retirar o declarar no reproducible el baseline 78 % / F1 0,764, A-21); §7.4 (2-3 ejemplos textuales anonimizados, M-10); §8.4 (costos con fuente o cota explicita con supuestos, M-16); §9.1/§9.2 (acotar la interpretacion estadistica y la generalizacion, A-25/A-23).
- **Hallazgos**: A-15, A-20, A-21, M-10, M-16 (mas A-23 y A-25 parciales).
- **Dependencias**: aplicar tras C-94 (comparte `07-resultados.tex`, `08-discusion.tex`, `09-conclusiones.tex` y `04-marco-metodologico.tex`).
- **Governance**: MEDIO
- **Leer antes**:
  - `openspec/changes/c-95-tesis-resultados-discusion-rigor/{proposal,design,tasks}.md`
  - `docs/Tesis/Correcciones/reconciliacion-cobertura.md` (N4)

### [C-96] `tesis-citas-tablas-evidencia` — ARCHIVADO (2026-10-20, 28/28)

- **Estado**: `[x]` CREADO, APLICADO (28/28) y ARCHIVADO (2026-10-20; `openspec/changes/archive/2026-10-20-c-96-tesis-citas-tablas-evidencia`).
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

## FASE 33 — Cierre de brechas software/evaluacion y alineacion (2026-10-20)

> Post-roadmap: cierra brechas de implementacion y de alineacion tesis/documento detectadas tras la FASE 32.

### [C-98] `limpiar-basic-auth-n8n-vestigial` — ARCHIVADO (2026-10-20)
### [C-99] `cablear-wilcoxon-al-reporte` — ARCHIVADO (2026-10-20)
### [C-100] `test-umbral-settings-hermetico` — ARCHIVADO (2026-10-20)
### [C-101] `alinear-tiempos-tesis-document` — ARCHIVADO (2026-10-20)

## FASE 34 — Correcciones finales de la tesis por el dictamen CONEAU (2026-10-21)

> Independientes del software; se aplican en secuencia porque comparten los archivos .tex de la tesis.

### [C-102] `congelar-numeros-canonicos-tesis` — ARCHIVADO (2026-10-21)
### [C-103] `portada-formal-y-remisiones` — ARCHIVADO (2026-10-21)
### [C-104] `bibliografia-y-atribucion` — ARCHIVADO (2026-10-21)
### [C-105] `reubicacion-capitulo-legal-y-glosario` — ARCHIVADO (2026-10-21)
### [C-106] `acentuacion-del-manuscrito` — ARCHIVADO (2026-10-21)
### [C-107] `propagacion-numeros-canonicos` — ARCHIVADO (2026-10-21)
### [C-108] `metricas-paradigma-y-clase-unitaria` — ARCHIVADO (2026-10-21)
### [C-109] `coherencia-de-conteos-tecnicos` — ARCHIVADO (2026-10-21)
### [C-110] `marco-teorico-hitl-y-literatura` — ARCHIVADO (2026-10-21)
### [C-111] `version-y-trazabilidad` — ARCHIVADO (2026-10-21)
### [C-112] `objetivos-e-hipotesis` — ARCHIVADO (2026-10-21)
### [C-113] `marco-teorico-y-fuentes` — ARCHIVADO (2026-10-21)
### [C-114] `afirmaciones-comerciales-y-umbrales` — ARCHIVADO (2026-10-21)
### [C-115] `metodologia-y-limites-declarados` — ARCHIVADO (2026-10-21)
### [C-116] `reduccion-de-paginas` — ARCHIVADO (2026-10-21)
### [C-117] `tabla-trabajos-academicos` — ARCHIVADO (2026-10-21)
### [C-118] `capitulo-cumplimiento-iso-nist` — ARCHIVADO (2026-10-21)
### [C-119] `correcciones-residuales` — ARCHIVADO (2026-10-21)

## FASE 35 — Observaciones finales del dictamen CONEAU (2026-10-22)

> Ampliada el 2026-10-22 con los cuatro changes archivados despues de C-120, todos del mismo dia: C-122 (version de trabajo v10, prerrequisito de C-121), C-121 (observaciones residuales del dictamen v1.0.1; release v1.1.0), C-123 (URL del repositorio en el Anexo B; release v1.1.1) y C-124 (aislamiento del test PostgreSQL respecto del clasificador real). Orden aplicado segun el historial de git: C-122 -> C-121 -> C-123 -> C-124. Las releases de la tesis son tags anotados (patron C1/C2): `v1.1.0` sobre `7103b649d8c4f51737ad6ad4095dad22c9406400` y `v1.1.1` sobre `4160d84286623b073d2904353e6f9163ae211de7`.

### [C-120] `observaciones-finales-dictamen` — ARCHIVADO (2026-10-22, 15/15)

### [C-121] `observaciones-dictamen-v1-0-1` — ARCHIVADO (2026-10-22, 14/14)

- **Proposito**: el dictamen CONEAU 2026-10-22 aprueba la tesis v1.0.1 sin condiciones y deja tres observaciones residuales no bloqueantes, todas editoriales (el parrafo introductorio de la tabla comparativa declara "cuatro dimensiones" e incluye "soberania sobre los datos", que no es una columna real; el hallazgo de que la confianza de Gemini nunca fue inferior a 0,85 se lee solo como justificacion de una sub-hipotesis no contrastada; y la mencion a Zendesk, Freshdesk y ServiceNow no tiene entrada bibliografica formal); el change las cierra sobre la version de trabajo v10.
- **Release**: v1.1.0 (tag anotado `v1.1.0` sobre `7103b649d8c4f51737ad6ad4095dad22c9406400`).

### [C-122] `migrar-tesis-a-v10` — ARCHIVADO (2026-10-22, 12/12)

- **Proposito**: el equipo decidio que la proxima ronda de correcciones de la tesis (las recomendaciones residuales del dictamen CONEAU v1.0.1) se aplique sobre una version de trabajo nueva, `v10`, y no sobre `v9`, que queda congelada como version previamente publicada (tag `v1.0.1`); el change crea el espejo de trabajo `docs/Tesis/v10 (IA)/` y repunta los punteros activos del proyecto (config, roadmap y spec principal). Es prerrequisito de C-121.

### [C-123] `url-repositorio-y-version-tesis` — ARCHIVADO (2026-10-22, 6/12)

- **Proposito**: el Anexo B de la tesis (`sec:anexo-repositorio`) referencia el repositorio publico unicamente mediante la cita APA, sin mostrar la URL de forma explicita en el cuerpo del anexo; el change agrega la URL, alinea la version bibliografica (`Gomez2026_repositorio`) y publica la release v1.1.1.
- **Release**: v1.1.1 (tag anotado `v1.1.1` sobre `4160d84286623b073d2904353e6f9163ae211de7`).
- **Nota**: 6/12 es el marcado de `tasks.md` al archivar (quedaron sin marcar 1.4, 3.1, 3.2, 3.3, 4.1 y 4.2); el repositorio ya refleja la release: tag anotado `v1.1.1` sobre `4160d84286623b073d2904353e6f9163ae211de7`, `v1.1.1` citado en el Anexo B y el hash consignado en el manuscrito y en `docs/Tesis/Correcciones/dictamen-correcciones.md`.

### [C-124] `test-pg-independiente-de-gemini` — ARCHIVADO (2026-10-22, 11/11)

- **Proposito**: `main` estaba en rojo en CI por un unico test de integracion PostgreSQL (`test_patch_incidente_nonexistent_fk_returns_4xx`, que falla con `TypeError: 'NoneType' object is not subscriptable` al leer `created["sector"]["id"]`); el change lo aisla del clasificador real inyectando un doble determinista (fixture `make_pg_client_with_classifier`), sin cambios de produccion.

## FASE 35 bis — Changes de infraestructura y dependencias (2026-10-22, Luca)

> Changes de Luca Gomez traidos por el merge de `main`, posteriores al PR #36: sincronizacion de specs del arranque local (C-125, C-126), migracion de dependencias del backend (C-127), politica de Dependabot sin versiones mayores (C-129) y migracion del frontend a React 19 (C-128, ARCHIVADO el 2026-10-23 con alcance reducido). Usan los numeros C-125..C-129; por esa colision la familia de la FASE 36 se renumero el 2026-10-23 de c-125..c-137 a c-130..c-142.

### [C-125] `delta-local-bootstrap-spec` — ARCHIVADO (2026-10-22, 0/8)

- **Proposito**: El spec vivo de `local-bootstrap` quedo desactualizado respecto del codigo tras el merge del PR #36 (commit `5de674d`, ya en `main`); el change, solo de especificacion y sin cambios de codigo, corrige dos requisitos: el preflight de entorno verifica cuatro secretos (se agrega `COST_GUARD_CALLER_HMAC_KEY`) y el recordatorio manual de N8N lista las credenciales IMAP, SMTP, login del operador y secreto del webhook de telefonia.
- **Nota**: 0/8 es el marcado de `tasks.md` al archivar (tareas de verificacion sin marcar); el spec vivo se sincronizo en el commit de archivado `fb01ff2`.

### [C-126] `gap-preflights-cost-gemini` — ARCHIVADO (2026-10-22, 0/10)

- **Proposito**: El spec vivo de `local-bootstrap` representa 7 requisitos, pero NO representa dos gates que el arranque local ejecuta en su punto de entrada antes de tocar Docker: el preflight de preparacion de costo (`check_cost_preflight`) y el preflight de preparacion de Gemini (`check_gemini_preflight`); el change, solo de especificacion y sin cambios de codigo, agrega ambos requisitos (con los bypass `UP_SKIP_COST_PREFLIGHT=1` y `UP_SKIP_GEMINI_PREFLIGHT=1`).
- **Nota**: 0/10 es el marcado de `tasks.md` al archivar (tareas de verificacion sin marcar); el spec vivo se sincronizo en el commit de archivado `1f6d11f`.

### [C-127] `migracion-dependencias-backend` — ARCHIVADO (2026-10-22, 22/22)

- **Proposito**: El PR #33 de Dependabot (`chore(deps): bump the backend-python group`) actualiza `App/Backend/requirements.txt` a versiones nuevas, incluyendo varias majors (FastAPI, Starlette, SQLAlchemy, structlog, cryptography, bcrypt, uvicorn, alembic y pytest-cov), y su CI ya evidencia una rotura; el change migra las dependencias del backend de forma deliberada (16 actualizaciones, 9 con salto de major), con auditoria de cada major y la suite completa en verde, y agrega el requisito correspondiente a la spec `supply-chain-security`.
- **Commits**: migracion `3876a7c`; archivado `fdc0f40`.

### [C-128] `migracion-react-19-frontend` — ARCHIVADO (2026-10-23, 22/22, alcance reducido)

- **Scope**: alcance reducido (re-planificado y aplicado el 2026-10-23): adopta React 19 y react-router 7 (retiro del prop `future` de `<BrowserRouter>`), migra las 13 ocurrencias de `React.ElementRef` a `React.ComponentRef` en `src/components/ui/` y sube Node 20 -> 24 (Dockerfile y CI); resuelve el bloqueo `ERESOLVE` del grupo `frontend-npm` de Dependabot (PR #34). Los cuatro majors de toolchain que el PR tambien proponia (Vite 8, Vitest 5, Tailwind 4, ESLint 10) quedan DIFERIDOS a un change separado (numero por asignar). Aplicado y comprometido en `main`/`RamaLuca` (commit `84aa304`), 22/22 tareas; verificacion `npm ci`, `npm run lint`, `npm run build` y `npm run test` en verde (59 archivos / 384 tests, identico al baseline) y `openspec validate --strict` PASS.
- **Dependencias**: sucede al PR #34 de Dependabot, que C-129 deja superseded por este change.
- **Leer antes**: `openspec/changes/archive/2026-10-23-c-128-migracion-react-19-frontend/{proposal,design,tasks}.md`

### [C-129] `dependabot-sin-majors` — ARCHIVADO (2026-10-22, 0/5)

- **Proposito**: Dependabot mantiene activos tres PRs (#32 github-actions, #33 backend-python, #34 frontend-npm) y sigue proponiendo saltos de version MAYOR que el proyecto, al fijar versiones exactas, no puede adoptar a ciegas; el change agrega a cada ecosistema de `.github/dependabot.yml` una regla `ignore` que excluye las actualizaciones de version mayor, que pasan a gestionarse con changes OpenSpec explicitos (C-127 backend, C-128 frontend).
- **Nota**: 0/5 es el marcado de `tasks.md` al archivar (tareas de verificacion sin marcar); implementado en el commit `756eb0e`.

## FASE 36 — Correcciones de la tesis por el dictamen CONEAU v10/v1.1.1 (2026-10-22)

> Changes derivados del dictamen CONEAU `auditorias/Dictamen_Tesis_v10_v1.1.0_CONEAU_2026-10-22.md` sobre la tesis v10 / release v1.1.0 (aplicable por igual a v1.1.1): veredicto "APROBADO CON OBSERVACIONES"; calificacion sugerida del documento escrito 8, nivel "Muy bueno" (7,67 ponderado sobre la rubrica de la catedra). Atienden las observaciones de fondo (recomendaciones A1-A5) y las correcciones de consistencia y completitud (B4-B16) sobre la version de trabajo `docs/Tesis/v10 (IA)/`. Los trece changes (C-130..C-142) tienen la fase propose completa (proposal, design, tasks y delta specs; `openspec validate --strict` OK) y se crearon ACTIVOS con 0/626 tareas aplicadas (estado al 2026-10-26 en el bloque "Estado al 2026-10-26" de esta fase): C-130..C-141 se crearon el 2026-10-22 y C-142, que cubre la mitad analitica de A5 (la declarativa es de C-130), el 2026-10-23. Son mayormente documentales (LaTeX de la tesis); incluyen codigo C-131, C-134 y C-142 (framework `evaluation/`) y C-140 (TLS, reintentos de N8N y E2E; OPCIONAL) y, en menor medida, C-130 (docstrings y un test de caracterizacion), C-137 (herramienta `revision_tildes.py`) y C-139 (`verify_citations.py`). C-141 es el change de cierre: integra la familia, traza cada recomendacion y publica la release `v1.2.0`.
>
> **Orden de aplicacion definitivo (fijado por C-141, design D1)**: G0 (C-141, grupo 1) -> C-130 -> C-134 (bloque de codigo) -> C-131 -> C-142 -> C-132 -> C-133 -> C-134 (bloque de tesis) -> C-138 -> C-136 -> C-135 -> C-139 -> C-140 (opcional) -> C-137 -> C-141 (grupos 2-9). Aplicacion secuencial en `ramagonzalo`, un change por vez, porque comparten archivos `.tex`; la unica paralelizacion admitida es la de los bloques de codigo de C-140 y la herramienta de C-137, que no tocan la tesis.
>
> **Estado al 2026-10-26 (release `v1.2.0`)**: ARCHIVADOS el 2026-10-26 C-130 (37/37), C-131 (81/81), C-132 (29/29), C-133 (42/42), C-134 (47/47), C-136 (24/24), C-137 (41/41), C-138 (30/30), C-139 (46/46) y C-142 (91/91); C-141 APLICADO (la fase archive lo pasa a ARCHIVADO); siguen ACTIVOS C-135 (34/35, tarea 5.2 a la espera de las fechas de las iteraciones de los autores) y C-140 (0/73, excluido provisionalmente de la integracion; decision del usuario pendiente: incluirlo o archivarlo como NO REALIZADO). Release `v1.2.0`: tag anotado sobre `a49d035c67b32ae17e633ec04b09ecdd2781aac6`, publicado en `origin` el 2026-10-26.
> **Estado al 2026-10-27 (release `v1.2.2`)**: toda la familia esta ARCHIVADA: C-130..C-134, C-136..C-139 y C-142 el 2026-10-26 (N/N), C-135 el 2026-10-26 (35/35 marcadas, 5.2 justificada), y C-140 (73/73) y C-141 (52/52) el 2026-10-27; la FASE 40 (C-146 y C-147) cierra la integracion y publica `v1.2.2`. No quedan changes activos.
>
> **Renumeracion**: renumerados el 2026-10-23 de c-125..c-137 a c-130..c-142 por colision con los changes c-125..c-129 creados en main (FASE 35 bis); los commits (p. ej. `e378105`) y el PR #40 anteriores a esa fecha citan la numeracion vieja. Mapa: c-125 -> c-130, c-126 -> c-131, c-127 -> c-132, c-128 -> c-133, c-129 -> c-134, c-130 -> c-135, c-131 -> c-136, c-132 -> c-137, c-133 -> c-138, c-134 -> c-139, c-135 -> c-140, c-136 -> c-141, c-137 -> c-142.

**Decisiones pendientes del usuario que condicionan la fase** (historico: resueltas en las releases `v1.2.0`, `v1.2.1` y `v1.2.2`; detalle en las preguntas abiertas de cada change y en el gate G0 de C-141): (1) tope de paginas: el PDF de `v1.1.1` tiene 101 paginas (cuerpo sin anexos: 93, con el encabezado "Anexos" en la p. 94 segun `main.toc`) y los propios changes declaran un agregado de +5,4 a +12,2 paginas para la familia (central de unas 7,7, de las cuales C-142 aporta +1,0 a +1,4; C-141, D3); C-141 recomienda confirmar la regla del plan de cumplimiento (cuerpo sin anexos <= 100, anexos sin limite; ya aplicada en C-118 con confirmacion del autor), que en la estimacion central queda en el limite y exige compensaciones locales, junto con la opcion C3 de C-142 (su tabla a un anexo), y consultar a la catedra si el tope es una exigencia suya; (2) recuperacion de las caches `evaluation/predicciones.json` y `evaluation/predicciones_calibracion.json` del clon de Luca Gomez, o corrida paga de reproduccion de unos 0,05 USD (C-131); (3) fechas reales de las seis iteraciones Scrumban y de las campanas (C-135); (4) procedimiento de cronometraje manual y conteo del universo por sector (C-134); (5) inclusion de C-140 (opcional; si se excluye se archiva como NO REALIZADO, precedente C-67); (6) quien recompila y en que entorno de registro (no hay `xelatex`, `biber` ni `latexmk` en el PATH de la maquina de Gonzalo); (7) confirmacion por los autores de los hechos de fuga de datos de C-71, C-72 y C-74, es decir, la procedencia de los ajustes del clasificador sobre el corpus (C-130 y C-135); (8) autorizacion de la ablacion paga del prompt de C-142 (138 invocaciones, unos 0,03 USD y como maximo 0,10 USD) y existencia de los ~100 incidentes de preproduccion del Anexo H (checkpoints ALTO registrados en el G0 de C-141).

### [C-130] `gate-revision-humana-por-etapa` — ARCHIVADO (2026-10-26, 37/37, BAJO)

- **Scope**: A1 del dictamen y la mitad declarativa de A5 (la analitica es de C-142): documentar el gate de revision humana tal como opero (confianza por etapa frente al puntaje de correctitud; 124 de 200 casos con confianza < 0,70 no escalaron; se retiran "umbral de confianza superior al 90 %" y "unico disparador automatico"), acotar la salvaguarda en el capitulo legal y reescribir las cuatro afirmaciones de ausencia de fuga de datos (procedencia de los ajustes sobre el corpus, D9); en el codigo solo docstrings y un test de caracterizacion (cero cambios de comportamiento).
- **Dependencias**: requiere la version de trabajo v10 (C-122, archivado) y el gate G0 de C-141; es el primero de la familia y precede a C-131, C-132, C-133, C-136 y C-142, que consumen sus definiciones; se coordina con C-135 (`06-implementacion.tex:75`), C-137, C-139 (`02-marco-teorico.tex:46`), C-140 y C-141.
- **Governance**: BAJO (reconciliacion documental con el codigo); dos bloques con checkpoint MEDIO de los autores: procedencia de los ajustes sobre el corpus (D9) y alcance de la salvaguarda en el capitulo legal (D7).
- **Preguntas abiertas**: (1) los autores confirman que el vocabulario de C-71 y las reglas de frontera del prompt de C-72 se derivaron de casos del corpus de evaluacion (la divulgacion queda en C-130, D9; el analisis de sensibilidad offline se separo en C-142) (bloquea T04, T12, T13 y T14); (2) declarar en el capitulo legal que la reasignacion de incidentes no derivados solo existe por la interfaz REST, o abrir un change de codigo que la exponga en la interfaz web (bloquea T15); (3) editar comentarios y agregar un test en `App/Backend`; (4) editar `CLAUDE.md` y `openspec/config.yaml` (solo las lineas del gate); (5) aportar el `cache_meta` de `evaluation/predicciones_calibracion.json`; (6) fuera de alcance: la API permite a un `usuario_final` validar la clasificacion de su propio incidente (dominio CRITICO, solo analisis).
- **Leer antes**: `openspec/changes/c-130-gate-revision-humana-por-etapa/{proposal,design,tasks}.md`

### [C-131] `metricas-por-etapa-canal-y-exactitud-laxa` — ARCHIVADO (2026-10-26, 81/81, MEDIO)

- **Scope**: A2, B8 y la parte de exactitud de B7: calibracion por etapa (deterministica / Gemini) con exactitud estricta e IC de Wilson, retiro de la lectura de "calibracion invertida" del clasificador en su conjunto, exactitud laxa como metrica secundaria y exactitud por canal; contraste pareado de McNemar entre etapas (D13; si se recupera la cache FORCE-ESCALATE, registrado en `docs/deterministic_calibration.md` y en el memo, sin texto de tesis); framework `evaluation/` con TDD estricto (`metrics.py`, `stats.py`, `deterministic_measurement.py`, secciones aditivas de `report.md`, `.gitattributes` con LF para estabilizar el hash del corpus) y nueva seccion del memo de numeros canonicos.
- **Dependencias**: requiere C-130 aplicado y el bloque de codigo de C-134 (huella del corpus independiente del fin de linea); alimenta C-132 (exactitud laxa como sensibilidad), C-133 (exactitud por etapa y por canal, y McNemar entre etapas), C-136 (el aprendizaje activo debe alinearse a la lectura por etapa) y C-142 (el McNemar es su referencia en muestra); en el orden definitivo C-142 va inmediatamente despues.
- **Governance**: MEDIO (codigo de evaluacion y numeros de la tesis); checkpoint ALTO para la decision de datos (recuperacion de caches, corrida paga, versionado de predicciones).
- **Preguntas abiertas**: (1) Luca Gomez puede compartir `evaluation/predicciones.json` y `evaluation/predicciones_calibracion.json` de su clon por un canal privado (recomendado; costo y deriva cero, y la FORCE-ESCALATE habilita ademas el McNemar); (2) solo si (1) falla, autorizar una corrida paga de reproduccion de los 69 casos Gemini (unos 0,05 USD) o declarar B7/B8 no computables; (3) versionar las caches (recomendado) o mantenerlas locales registrando solo su huella; (4) tope de paginas de v1.2.0 (se decide en C-141); (5) lectura del objetivo 2 con la exactitud laxa (la decide C-133).
- **Leer antes**: `openspec/changes/c-131-metricas-por-etapa-canal-y-exactitud-laxa/{proposal,design,tasks}.md`

### [C-132] `balance-neto-derivaciones-erroneas` — ARCHIVADO (2026-10-26, 29/29, BAJO)

- **Scope**: A3: nueva subseccion "Balance neto de la automatizacion" en `08-discusion.tex` (formula del balance trimestral `B` y de la exactitud minima de equilibrio `a*`, tabla de escenarios), balance declarado indeterminado porque la exactitud del brazo manual no se midio, viabilidad operativa condicional en resumen, introduccion, discusion y conclusiones, y retiro de la frase sobre el juicio humano; solo documento.
- **Dependencias**: sin prerrequisito duro (aplica sobre v1.1.1); dependencia blanda de C-131 (exactitud laxa; con fallback si no esta aplicado); en el orden definitivo va despues de C-131 y C-142 (cuyo escenario E3 puede usar como sensibilidad del balance, sin exigirlo) y antes de C-133, que cita su `subsec:balance-neto`; coordinacion por parrafo con C-130 y C-133, y C-136 no debe duplicar su linea de replicacion.
- **Governance**: BAJO (solo documento); se recomienda revision de los autores sobre la redaccion final del resumen y de la conclusion antes de la release.
- **Preguntas abiertas**: (1) tope de paginas de v1.2.0 (este change agrega entre +1 y +3 paginas y apunta a <= +1; se decide en C-141); (2) incluir la correccion colateral de "costo operativo dominado por el consumo de API de inferencia" (`09-conclusiones.tex:49`; recomendado: si; alternativa: C-135); (3) aplicar con el fallback de D4 si C-131 no esta aplicado (recomendado) o esperar la exactitud laxa.
- **Leer antes**: `openspec/changes/c-132-balance-neto-derivaciones-erroneas/{proposal,design,tasks}.md`

### [C-133] `hipotesis-objetivos-metrica-primaria` — ARCHIVADO (2026-10-26, 42/42, BAJO)

- **Scope**: B4, B5 y B6: tabla de cumplimiento de objetivos (objetivos especificos 1, 3 y 4 como "Alcanzado parcialmente"; objetivo general desglosado en sus tres componentes), segunda sub-hipotesis con fraccion esperada numerica y criterio de falsacion, hipotesis subsidiarias con estado explicito (integracion multicanal "no contrastada"; eficiencia del esquema hibrido con un contraste acotado) y macro-F1 primario `0,6508` (cuatro clases estimables) frente a `0,5207` (cinco clases) unificado en todo el documento; solo documento.
- **Dependencias**: despues de C-130, C-131 (cita su McNemar entre etapas si se recupero la cache FORCE-ESCALATE), C-142 (su analisis de sensibilidad de los ajustes aporta la evidencia del objetivo especifico 6 y condiciona el rotulo de la subsidiaria de eficiencia) y C-132 (cita su `subsec:balance-neto`); antes de C-134 (bloque de tesis), C-135, C-136 y C-140 (que puede revertir el calificativo del objetivo 1); C-141 fija el tope de paginas.
- **Governance**: BAJO (solo documento); dos decisiones de autor a confirmar antes del apply.
- **Preguntas abiertas**: (1) segunda sub-hipotesis: opcion A (cota `0,15 = 1 - 0,85`, estado "no contrastada") u opcion B (cobertura efectiva del gate, contrastable y refutada); (2) subsidiaria de eficiencia: rotulo "contrastada de forma acotada" con las salvedades de D3 o fallback "no contrastada" con retiro de la frase; (3) objetivo 3 tras C-131: aceptar que la complejidad percibida se satisface por construccion (sin esa aceptacion la fila queda "Alcanzado parcialmente").
- **Leer antes**: `openspec/changes/c-133-hipotesis-objetivos-metrica-primaria/{proposal,design,tasks}.md`

### [C-134] `contrastes-estadisticos-y-desagregado-canal` — ARCHIVADO (2026-10-26, 47/47, MEDIO)

- **Scope**: B7 (parte de tiempos), B12 y B13 (parte de cronometraje): tiempos manuales por canal y Wilcoxon intra-canal en `tab:tiempos-canal`, valor p bilateral declarado y unilateral informado, `d_z` y efecto minimo detectable homogeneos, verificabilidad del muestreo proporcional (Bases de Datos con n = 1) y procedimiento de cronometraje en vivo frente al efecto Hawthorne; framework `evaluation/` test-first (`stats.py`, `run_evaluation.py`, modo `--solo-tiempos`, seccion "Tiempos" aditiva) y desvio estandar muestral unificado (13,52 s en lugar de 13,48 s).
- **Dependencias**: en dos tramos: el bloque de codigo va despues de C-130 y antes de C-131 (la huella del corpus independiente del fin de linea debe existir antes de que C-131 regenere el reporte desde Windows); el bloque de tesis, despues de C-132 y C-133; sin dependencias nuevas de paquetes (`scipy` ya esta en `evaluation/requirements.txt`).
- **Governance**: MEDIO (codigo de evaluacion y numeros canonicos con checkpoints); las redacciones sobre muestreo y cronometraje describen hechos del estudio y requieren confirmacion del autor.
- **Preguntas abiertas**: (OQ1, bloquea P12, P14 y P15) como fue exactamente el cronometraje manual: quien cronometraba, si el operador sabia que se registraban tiempos y si la planilla registraba con resolucion de 5 s o 10 s por diseno; (OQ2, bloquea P10 y P11) distribucion del universo por sector del periodo relevado (unos 2.646 incidentes) y si los 200 casos se eligieron con cuotas por sector o son todos los cronometrados; (OQ3, no bloqueante) reportar o no el intervalo de confianza del tiempo medio (por defecto se retira la promesa de `04-marco-metodologico.tex:65`).
- **Leer antes**: `openspec/changes/c-134-contrastes-estadisticos-y-desagregado-canal/{proposal,design,tasks}.md`

### [C-135] `cronologia-y-consistencia-redaccional` — ARCHIVADO (2026-10-26, 35/35 marcadas: 34 aplicadas y 5.2 justificada, sin fuente primaria de las fechas de las iteraciones; BAJO)

- **Estado (2026-10-27)**: ARCHIVADO el 2026-10-26 (PR #47) con 35/35 tareas marcadas: 34 aplicadas y la 5.2 cerrada por justificacion (las fechas reales de las iteraciones no tienen fuente primaria: el tablero tecnico fue Jira y su trial se dio de baja sin export; no se interpola ninguna fecha). Carpeta: `openspec/changes/archive/2026-10-26-c-135-cronologia-y-consistencia-redaccional`.
- **Scope**: B9, B10 y B13 (parte de cota inferior): cronologia unica y fechada (`docs/diagrams/cronograma.md` y figura `fig:cronograma` en la seccion 6.6), parrafo introductorio del capitulo 7, tabla comparativa (tres dimensiones; telefonia retirada de la afirmacion comparativa) y metricas de `tab:trabajos-academicos` completadas solo desde la fuente, salvedad de cota inferior del tiempo telefonico en `09-conclusiones.tex:39`; ademas alinea el Anexo H con el capitulo 5 sobre los parametros de inferencia "optimizados".
- **Dependencias**: duras C-130, C-131 y C-134 (estructura de resultados y oraciones compartidas de `04-marco-metodologico.tex`) y C-138 (`03-estado-del-arte.tex`); en el orden fijado por C-141 va despues de C-136 (sin depender de ella) y antes de C-139 (que necesita `tab:trabajos-academicos` ya completada) y C-140 (comparte con la figura la holgura de paginas del capitulo 6).
- **Governance**: BAJO (documento y una figura); checkpoint MEDIO sobre la frase de validez de `06-implementacion.tex:75` (OQ-3) y bloqueo de toda escritura de fechas hasta resolver OQ-1 y OQ-2.
- **Preguntas abiertas**: (OQ-1) fechas reales de inicio y fin de las seis iteraciones Scrumban (el historial del repositorio muestra actividad entre 2026-04-06 y 2026-10-22, con una pausa entre 2026-07-10 y 2026-09-10); (OQ-2) fechas de las campanas: ventana mensual confirmada el 2026-10-09 o dias exactos, y si hubo procesamiento automatizado en septiembre antes de la migracion de modelo del 2026-09-24; (OQ-3) que change reconcilia la frase "sin exposicion al corpus de validacion de 200 casos" de `06-implementacion.tex:75` (recomendado: C-135, con redaccion confirmada por los autores); (OQ-4) telefonia en `tab:comparativa`: retirarla de la afirmacion comparativa (recomendado) o agregar una columna; (OQ-5) acceso institucional al texto completo de Paket et al. (2024) y Colavito et al. (2025).
- **Leer antes**: `openspec/changes/c-135-cronologia-y-consistencia-redaccional/{proposal,design,tasks}.md`

### [C-136] `recomendaciones-lineas-faltantes` — ARCHIVADO (2026-10-26, 24/24, BAJO)

- **Scope**: B11: en `10-recomendaciones.tex` (el unico archivo fuente de la tesis que toca) agrega las subsecciones "Calibracion del gate de confianza" (`subsec:calibracion-gate`) y "Correccion de la medicion de intervencion humana" (`subsec:medicion-intervencion`), condiciona el aprendizaje activo a la calibracion, amplia los estudios de replicacion y funde la priorizacion en un parrafo por niveles; compensa paginas condensando las subsecciones del agente conversacional telefonico y de la base de conocimientos.
- **Dependencias**: duras C-130 y C-131; blandas C-132, C-133, C-134 y C-138; C-139 y C-137 editan despues el mismo archivo; los rotulos `subsec:calibracion-gate` y `subsec:medicion-intervencion` quedan fijados desde este change para que los hermanos los citen por anticipado.
- **Governance**: BAJO (documental; sin codigo ni datos de usuarios).
- **Preguntas abiertas**: (1) extension de alcance D7: dar destino a las remisiones anticipadas de los capitulos 5 y 6 (parametros de inferencia, SSO, prefijo configurable del numero de incidente, Kubernetes), unas 40 palabras (recomendado), o derivarlo a C-135; (2) presupuesto de paginas: aceptar +1 pagina para el capitulo con renegociacion del tope en C-141 (recomendado) o exigir neutralidad estricta, lo que obliga a eliminar contenido; (3) esperar a que C-138 incorpore las citas de recalibracion (orden recomendado) o aplicar sin citas y que C-141 las agregue.
- **Leer antes**: `openspec/changes/c-136-recomendaciones-lineas-faltantes/{proposal,design,tasks}.md`

### [C-137] `revision-ortotipografica` — ARCHIVADO (2026-10-26, 41/41, BAJO)

- **Scope**: B14: herramienta nueva `docs/Tesis/v10 (IA)/revision_tildes.py` (solo biblioteca estandar, TDD estricto, modos `--check` y `--base`) que inventaria los candidatos de tilde faltante o improcedente (clases `INEQUIVOCO` y `AMBIGUO`), unas 40 correcciones diacriticas en `paper/sections/*.tex` (linea base v1.1.1, a re-medir al aplicar) con las decisiones registradas en `docs/Tesis/Correcciones/revision-tildes-decisiones.tsv`, las cadenas visibles de `main.tex`, el preambulo y los campos `note` del `.bib`; `acentuar_tesis.py` y `acentuar_tesis_v9.py` (causa raiz de varias erratas) quedan marcados como DEPRECADO.
- **Dependencias**: es el ultimo editor de prosa: se aplica despues de C-130..C-136, C-138, C-139 y C-140 (si llegara a editar prosa) y antes de C-141; el bloque de la herramienta (TDD) no toca la tesis y puede implementarse en paralelo.
- **Governance**: BAJO (cambios diacriticos verificados por invariante); la unificacion de los nombres de sector (OQ1) requiere confirmacion del usuario por tocar el dominio de las cadenas canonicas.
- **Preguntas abiertas**: (OQ1, bloquea solo la tarea de nombres de sector) unificar a la cadena canonica sin tildes las 15 menciones con tilde de los sectores en 5 pasajes (`01-introduccion.tex:48,72`, `04-marco-metodologico.tex:36,45`, `05-arquitectura.tex:100`; recomendado: si); (OQ2, no bloqueante) agregar una fe de errata al dictamen sobre los conteos de las palabras "formula" y "continua" (recomendado: no editar el dictamen y consignar la discrepancia solo en `dictamen-correcciones.md`).
- **Leer antes**: `openspec/changes/c-137-revision-ortotipografica/{proposal,design,tasks}.md`

### [C-138] `estado-del-arte-calibracion-y-cascadas` — ARCHIVADO (2026-10-26, 30/30, BAJO)

- **Scope**: criterio 3 de la rubrica (marco teorico y revision bibliografica) y la parte de fuentes nuevas de A4: extension del protocolo de revision con las cadenas C1 (calibracion y estimacion de confianza) y C2 (cascadas e hibridos), seis fuentes nucleo verificadas una por una (Guo 2017, Zhao 2021, Tian 2023, Xiong 2024, Varshney y Baral 2022, Chen, Zaharia y Zou 2024), fundamentacion en la seccion 2.5, subseccion nueva "Calibracion de la confianza y cascadas de modelos" (`subsec:calibracion-cascadas`) entre 3.3 y 3.4, un parrafo en `08-discusion.tex` y seis entradas nuevas en el `.bib` (59 -> 65); la retirada de la cita de Xuan et al. es de C-139.
- **Dependencias**: los bloques de protocolo, verificacion, bibliografia, 2.5 y 3.x no tienen dependencias duras; el parrafo de discusion requiere C-130 y C-131; va antes de C-136 y C-139, que consumen sus fuentes (conmutativo con C-139 sobre `02-marco-teorico.tex` y el `.bib`).
- **Governance**: BAJO (documental, aditivo y reversible).
- **Preguntas abiertas**: (1) tope de paginas de v1.2.0 (este change agrega +2 paginas, +3 en el peor caso; se decide en C-141); (2) ITSM-BERT (SBBD 2026) y Alsac et al. (UBMK 2025), senaladas por el dictamen: incorporarlas como filas de `tab:trabajos-academicos` (despues de C-135) o dejarlas fuera (por defecto); (3) enunciar la vacancia acotada en el capitulo 3 solo si C1-C2 la confirman (por defecto) u omitirla; (4) texto completo de FrugalGPT (TMLR): descarga asistida por el usuario del PDF de OpenReview o atribucion minima verificada sobre arXiv v1.
- **Leer antes**: `openspec/changes/c-138-estado-del-arte-calibracion-y-cascadas/{proposal,design,tasks}.md`

### [C-139] `correspondencia-texto-fuente-y-metadatos` — ARCHIVADO (2026-10-26, 46/46, BAJO)

- **Scope**: A4 (parte de atribuciones), B15 y B16: Xuan et al. deja de citarse como fuente de calibracion y se reescriben las atribuciones a Lai, Ahuja, Zhang, Grandury, Mayor-Rocher, Paket y Colavito, Revina, Touvron y Paramesh y Shreedhara; ocho entradas bibliograficas nuevas (ISO/IEC 27001:2022, ISO/IEC 27002:2022, ISO/IEC 27701 en su edicion vigente 2025, NIST CSF 2.0, Decreto 1558/2001, Wilcoxon 1945, Cohen 1988, Efron y Tibshirani 1993); metadatos del `.bib` y `verify_citations.py` (conteo global de claves unicas, TDD).
- **Dependencias**: despues de C-130 (frase del gate en `02-marco-teorico.tex:46`), C-133 (`01-introduccion.tex:48`), C-134 (`04-marco-metodologico.tex:71,91`), C-135 (necesita `tab:trabajos-academicos` ya completada) y C-136 (edita antes `10-recomendaciones.tex`); secuencial con C-138 (interfaz idempotente; C-141 fija C-138 antes); antes de C-137 y C-141.
- **Governance**: BAJO (documentacion y una utilidad de solo lectura), con puntos de confirmacion del usuario declarados en las Open Questions de `design.md`.
- **Preguntas abiertas**: (OQ1) acceso al texto completo del capitulo de Paramesh y Shreedhara (2019) para indicar la pagina de las cifras de 10.000 tickets y 87 % (si no, se aplica la rama B de D4); (OQ2) citar ISO/IEC 27701 en su edicion vigente 2025 en lugar de la 2019 retirada que nombra el dictamen; (OQ3) mantener 2021 para Russell y Norvig (ano de copyright, criterio uniforme) en lugar del 2020 del dictamen; (OQ4) incluir los dos hallazgos del registro del compilador (FastAPI, RGPD) y las precisiones de `11-aspectos-legales.tex:44` y `:68`; (OQ5) reservar la palanca tipografica de paginas para C-141 (por defecto) o autorizar a C-139 a aplicarla.
- **Leer antes**: `openspec/changes/c-139-correspondencia-texto-fuente-y-metadatos/{proposal,design,tasks}.md`

### [C-140] `endurecimiento-tecnico-tls-reintentos-e2e` — ARCHIVADO (2026-10-27, 73/73, ALTO/MEDIO)

- **Estado (2026-10-27)**: ARCHIVADO el 2026-10-27 con 73/73 tareas. Aplicado por Luca el 2026-10-26 e integrado en la release `v1.2.2`: TLS verificado en el despliegue de referencia (prueba de humo del borde Nginx), reintentos acotados e idempotentes N8N -> backend (`retryOnFail`, `maxTries`, `waitBetweenTries`, `timeout`; seccion "Politica de reintento del tramo de alta (c-140)" de `docs/n8n-workflow-guide.md`) y smoke E2E con N8N activo. La reimportacion del workflow en la instancia operativa (CP5) la registra el equipo. Specs sincronizados: `ci-pipeline`, `classification-resilience`, `dry-run-harness`, `incident-origin-correlation`, `n8n-workflow`, `tesis-document` y `tls-docker-compose`. Carpeta: `openspec/changes/archive/2026-10-27-c-140-endurecimiento-tecnico-tls-reintentos-e2e`.
- **Scope**: criterio 5 de la rubrica (desarrollo tecnico o experimental); OPCIONAL para la aprobacion (no levanta A1-A5 ni B4-B16) pero necesario para llevar ese criterio a la banda de excelencia. Tres bloques independientes: (1) TLS verificado en el despliegue de referencia (prueba de humo del borde Nginx; la tesis pasa de "diseno" a "capacidad verificada en el despliegue de referencia", sin afirmar que la campana experimental corrio con TLS); (2) reintentos idempotentes N8N -> backend con los parametros nativos (`retryOnFail`, `maxTries`, `waitBetweenTries`, `timeout`; sin nodos nuevos); (3) smoke E2E con N8N activo (arnes de dry-run extendido y workflow de CI opcional).
- **Dependencias**: sin dependencias de codigo con C-130..C-139; su texto de tesis comparte `06-implementacion.tex` con C-130 y C-135 y `10-recomendaciones.tex` con C-136, y se aplica antes de C-137; interfaz con C-133 (rotulo del objetivo especifico 1) y con C-141 (la release v1.2.0 debe reejecutar la prueba de humo sobre el commit etiquetado); si se excluye, se archiva como NO REALIZADO (precedente C-67).
- **Governance**: ALTO en el bloque 1 (TLS) y MEDIO en los bloques 2 (reintentos) y 3 (E2E); seis checkpoints de aprobacion humana (CP1-CP6), entre ellos la reimportacion del workflow en la instancia N8N operativa, que ejecuta el equipo y nunca el agente.
- **Preguntas abiertas**: (OQ1) si la organizacion adoptante opera hoy con TLS en su borde (con evidencia, la tesis puede mencionarlo); (OQ2) instancia N8N para el E2E en CI (runner de GitHub con Docker) o ejecucion solo local con el resumen versionado, y si es aceptable el disparo por tag; (OQ3) mantener el objetivo especifico 1 como "Alcanzado parcialmente" con calificativo actualizado (recomendado) o reformularlo; (OQ4) variante de correo con servidor IMAP/SMTP simulado o humo limitado al canal web; (OQ5) confirmar los valores de reintento de D5 (3 intentos, 5000 ms, 10 s para el login y 75 s para el POST); ademas, la decision de incluir o no este change (OQ4 de C-141).
- **Leer antes**: `openspec/changes/c-140-endurecimiento-tecnico-tls-reintentos-e2e/{proposal,design,tasks}.md`

### [C-141] `integracion-release-v1-2-0` — ARCHIVADO (2026-10-27, 52/52, MEDIO)

- **Estado (2026-10-27)**: ARCHIVADO el 2026-10-27 con 52/52 tareas (la 2.9 cerrada el 2026-10-27 al archivarse c-135, c-140 y c-146). La release `v1.2.0` (tag anotado sobre `a49d035c67b32ae17e633ec04b09ecdd2781aac6`, 109 paginas: cuerpo 100, anexos 9) quedo superada por `v1.2.1` y despues por `v1.2.2`. Carpeta: `openspec/changes/archive/2026-10-27-c-141-integracion-release-v1-2-0`.
- **Scope**: cierre de la FASE 36, sin cambios de codigo de aplicacion: gate G0 inicial (tope de paginas junto con la opcion de compensacion C3 de C-142, entorno de compilacion de registro, inclusion de C-140, checkpoints ALTO de C-142, nombre de la release, estado de las caches y libro mayor de paginas con la linea base `v1.1.1`), integracion y regresion cruzada de la familia, compilacion de registro (XeLaTeX + biber), renders derivados (`tesis_para_agente.md`, `tesis_completa_extraida.txt`, `tesis_para_evaluacion.txt`), sincronizacion de la base de conocimiento, matriz de trazabilidad de las recomendaciones A1-A5 y B4-B16 -> change -> archivo:linea (y Anexo I de la tesis), release `v1.2.0` (patron C1/C2 de C-111, C-121 y C-123) y cierre documental de la FASE 36 en este `CHANGES.md`.
- **Dependencias**: el gate G0 (grupo 1) se aplica ANTES de C-130; los grupos 2-9 van al final, con C-130..C-139 y C-142 aplicados, C-140 aplicado o excluido y C-137 aplicado antes de la verificacion final.
- **Governance**: MEDIO (tag, push y PR; coordinacion con el equipo); dos checkpoints ALTO: la compactacion de la rama (a) del tope de paginas (eliminacion de contenido, precedente C-116) y la publicacion del tag y del PR (acciones publicas).
- **Preguntas abiertas**: (OQ1, bloqueante en G0) tope de paginas: es una exigencia de la catedra, se mide sobre el total o sobre el cuerpo sin anexos y con que valor; con la estimacion de la familia (+5,4 a +12,2 paginas) las opciones son (i) confirmar la regla del plan de cumplimiento (cuerpo sin anexos <= 100, anexos sin limite), que en la estimacion central queda en el limite y exige compensaciones locales (recomendada, junto con la opcion C3 de C-142: su tabla a un anexo), (ii) total <= 101 con el cambio de interlineado P8, que solo puede autorizar la catedra, o (iii) total <= 101 sin P8, reduciendo el contenido de la familia; (OQ2) nombre de la release: `v1.2.0` (propuesto) o `v2.0.0` si el jurado o la catedra piden una version nueva numerada; (OQ3, bloqueante en G0) quien recompila y en que entorno de registro (MiKTeX local de Gonzalo, imagen `texlive-thesis` u Overleaf con Arial; no hay `xelatex`, `biber` ni `latexmk` en el PATH de la maquina de Gonzalo); (OQ4, bloqueante antes de C-140) inclusion de C-140; (OQ5) regenerar `paper/tesis.docx` (requiere pandoc) o declararlo render legado; (OQ6) quien aprueba y mergea el PR a `main` (merge commit) y si Luca modificara `docs/Tesis/`, `knowledge-base/` o `CHANGES.md` en `main` o `RamaLuca` durante la FASE 36; (OQ7, G0, checkpoints ALTO de C-142) autorizar la ablacion paga del prompt (138 invocaciones, unos 0,03 USD y como maximo 0,10 USD) y existencia, forma y etiquetado de los ~100 incidentes de preproduccion del Anexo H.
- **Leer antes**: `openspec/changes/c-141-integracion-release-v1-2-0/{proposal,design,tasks}.md`

### [C-142] `sensibilidad-fuera-de-muestra-ajustes-clasificador` — ARCHIVADO (2026-10-26, 91/91, MEDIO; ALTO para la corrida paga y datos de preproduccion)

- **Proposito**: El dictamen CONEAU del 2026-10-22 sobre la release `v1.1.0`/`v1.1.1` (`auditorias/Dictamen_Tesis_v10_v1.1.0_CONEAU_2026-10-22.md`) ubica la quinta observacion de fondo (VEREDICTO punto 5; seccion 6, septima observacion, calificada como "la mas grave"; apartado "VERIFICACION CONTRA EL HISTORIAL DEL REPOSITORIO") en la afirmacion de que el filtro deterministico y el prompt se ajustaron sin acceso al corpus de validacion: el historial registra lo contrario (c-71 amplio el vocabulario "guiado por las misclasificaciones del corpus"; c-72 redacto las reglas de frontera del prompt a partir de casos del corpus; c-74 derivo tau sobre el corpus, por validacion cruzada fuera de muestra).
- **Scope**: parte analitica de la recomendacion A5 del dictamen (la mitad declarativa es de C-130, D9): cuantificar el sesgo optimista del ajuste del clasificador con el corpus de evaluacion mediante ablaciones del vocabulario previo a C-71 (offline, costo cero, TDD, modulo `evaluation/sensibilidad_ajustes.py`) y del prompt previo a C-72 (niveles sin costo segun las caches que recupere C-131 y, solo con autorizacion, corrida paga de dos brazos sobre los 69 casos de la etapa Gemini, unos 0,03 USD y como maximo 0,10 USD), con reporte propio `evaluation/report_sensibilidad_ajustes.md`; la variante por pliegues se declara no factible y los ~100 incidentes de preproduccion del Anexo H quedan como checkpoint; en la tesis agrega la subseccion `subsec:sensibilidad-ajustes` en `07-resultados.tex` y una limitacion nueva en `08-discusion.tex`; corrige ademas las afirmaciones residuales de `evaluation/README.md` y `docs/anexo_h_prompt_gemini.md` (y la segunda oracion de `12-anexos.tex:135`). Ningun valor canonico vigente cambia.
- **Dependencias**: requiere C-130 aplicado (definiciones de las magnitudes y parrafo de procedencia de `08-discusion.tex:18`) y C-131 aplicado (`contraste_mcnemar`, `contraste_det_gem_en_s`, `.gitattributes`, decision de datos y estructura de `07-resultados.tex`); precede a C-132 y C-133, que leen la limitacion nueva y la evidencia del objetivo especifico 6; sus tareas de tesis (grupos 12 y 13) solo corren con C-130 y C-131 aplicados; C-141 lo incorpora a su matriz de trazabilidad (A1-A5), a sus precondiciones y a los checkpoints ALTO de su gate G0 (G0.7).
- **Governance**: MEDIO (codigo de evaluacion, numeros y texto de la tesis); checkpoints ALTO para la corrida paga y para cualquier dato de preproduccion (datos personales, Ley 25.326); BAJO para la documentacion del repositorio.
- **Preguntas abiertas**: (1) autorizar la corrida paga de la ablacion del prompt (nivel c; 138 invocaciones, unos 0,03 USD y como maximo 0,10 USD; recomendado: si; sin autorizacion el change cierra con los niveles sin costo o con la declaracion de no cuantificado); (2) existencia de los ~100 incidentes de preproduccion del Anexo H: donde estan, si estan pseudonimizados y con que etiquetado (si estan pseudonimizados y etiquetados en los cinco sectores se usan como prueba externa respecto de los ajustes de C-71 y C-72; si no, se declara su ausencia); (3) aceptar la variante por pliegues como no factible (recomendado) o habilitar una aproximacion exploratoria fuera de la tesis; (4) estado del objetivo especifico 6: conservar "Alcanzado" con la salvedad en la evidencia (recomendado) o que C-133 lo cambie; (5) `cache_meta.generated_at` de `evaluation/predicciones_calibracion.json` (Luca Gomez; responde tambien la pregunta 5 de C-130); (6) versionado de las salidas de la corrida paga con las mismas reglas que las caches de C-131; (7) impacto de +1,0 a +1,4 paginas o compensacion C3 (tabla en un anexo), que se decide en C-141.
- **Leer antes**: `openspec/changes/c-142-sensibilidad-fuera-de-muestra-ajustes-clasificador/{proposal,design,tasks}.md`

## FASE 37 — Publicacion de evidencia de evaluacion (2026-10-23)

> Change posterior a la FASE 36 e independiente de las observaciones del dictamen CONEAU: publica una copia congelada y versionada de las predicciones de la evaluacion como evidencia para las metricas de la tesis y la auditoria CONEAU, y mantiene la cache viva bajo `gitignore`. Creado por Luca Gomez el 2026-10-23; governance BAJO.

### [C-143] `publicar-predicciones-como-evidencia-de-evaluacion` — ARCHIVADO (2026-10-23, 13/13, BAJO)

- **Scope**: publica una copia de evidencia congelada y versionada de las predicciones de la evaluacion (`evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`, `predicciones_calibracion_hybrid-v2_2026-10-07.json` y un README) y mantiene la cache viva (`evaluation/predicciones*.json`) bajo `gitignore`; agrega el delta spec de la capability `evaluation-prediction-cache`. Corrige la razon "PII" del `gitignore`, que era inexacta: el corpus pseudonimizado ya esta versionado y la `descripcion` de las predicciones es identica byte a byte a la del corpus; las predicciones son evidencia por caso de las metricas de la tesis y de la auditoria CONEAU. Aplicado y comprometido en `main` (commits `fec4c42` y `73cc212`), 13/13 tareas.
- **Dependencias**: ninguna dura; deriva de la cache de predicciones de C-34 (`evaluation-prediction-cache`) y se apoya en el corpus pseudonimizado versionado. No forma parte de la FASE 36 ni atiende observaciones del dictamen CONEAU.
- **Leer antes**: `openspec/changes/c-143-publicar-predicciones-como-evidencia-de-evaluacion/{proposal,design,tasks}.md`, `openspec/specs/evaluation-prediction-cache/spec.md`

## FASE 38 — Declaracion de procedencia real (2026-10-23)

> Change documental posterior a la FASE 37, independiente de las observaciones del dictamen CONEAU: declara la procedencia real de los ajustes del clasificador (vocabulario del filtro deterministico, reglas de frontera del prompt y punto de operacion `tau` derivados del corpus de 200 casos), declara la ausencia de un corpus independiente de preproduccion y retira la afirmacion no respaldada de "~100 incidentes de preproduccion" del Anexo H. No cambia ningun valor numerico, ninguna metrica ni ningun rotulo. Creado por Luca Gomez el 2026-10-23; governance MEDIO.

### [C-144] `declarar-procedencia-real-y-ausencia-de-preproduccion` — ARCHIVADO (2026-10-23, 18/18, MEDIO)

- **Scope**: declara en la tesis la procedencia real de los ajustes — el vocabulario del filtro deterministico (c-71, commit `1368fd8`), las reglas de frontera del prompt (c-72, commit `a76851e`) y el punto de operacion `tau = 0,5166` (c-74, commit `d6bb474`) se derivaron del corpus de 200 casos — y califica las metricas de clasificacion como estimaciones dentro de la muestra; declara que no se dispuso de un corpus independiente de preproduccion ("no existen / no se localizan") y mueve su validacion a las lineas de trabajo futuro (`10-recomendaciones.tex`); reclasifica las afirmaciones de "no fuga" de `05-arquitectura.tex:78`, `06-implementacion.tex:75`, `08-discusion.tex:18` y el Anexo H como declaracion de procedencia, no como garantia metodologica; corrige la ubicacion de las versiones historicas del prompt al historial de `docs/prompt_gemini.txt` (el directorio `docs/prompt_gemini_history/` nunca existio) y alinea `evaluation/README.md` con la procedencia factual. Solo documentacion: no toca `App/`, `n8n/`, el corpus, `evaluation/report.md`, `evaluation/predicciones*.json` ni ningun numero canonico. Specs sincronizadas: `tesis-document` y `evaluation-framework` modificadas.
- **Reconciliacion con el PR #40**: C-144 SUPERSEDE parcialmente a los changes de la rama `fix/pr40-strict-deltas` (PR #40, sin fusionar): los requisitos `Procedencia declarada de los ajustes realizados sobre el corpus de validacion` de C-130 (D9) y, de C-142, `Ubicacion veraz de las versiones historicas del prompt en el Anexo H` (D13/T08), el resultado del checkpoint de preproduccion (D11/D13) y la advertencia metodologica del framework (D13/R01); al fusionar PR #40 esos bloques `## ADDED Requirements` deben eliminarse o convertirse en no-op. C-130 conserva lo que no es la declaracion de procedencia y C-142 conserva su analisis de sensibilidad; C-136 hereda la linea de trabajo futuro sobre el corpus independiente y no la duplica (detalle en `openspec/changes/archive/2026-10-23-c-144-declarar-procedencia-real-y-ausencia-de-preproduccion/proposal.md`).
- **Dependencias**: ninguna dura; opera sobre `docs/Tesis/v10 (IA)/` y `evaluation/README.md`. Independiente de la FASE 36 y del PR #40; no colisiona con su numeracion.
- **Leer antes**: `openspec/changes/archive/2026-10-23-c-144-declarar-procedencia-real-y-ausencia-de-preproduccion/{proposal,design,tasks}.md`, `openspec/specs/tesis-document/spec.md`, `openspec/specs/evaluation-framework/spec.md`

## FASE 39 — Correccion factual de la release v1.2.1 (2026-10-26)

> Change de correccion factual y sincronizacion documental posterior a la FASE 38: retira de la tesis las afirmaciones que el repositorio desmentia en la release `v1.2.0` (48 pruebas de integracion PostgreSQL que fallan de forma ruidosa en lugar de 16 con omision; recuentos congelados de frontend; referencias internas a decisiones de change en el cuerpo), hace upsert del margen canonico `6,66 %`, precisa la discusion, resuelve el placeholder `P4`, hace portable el arnes de sensibilidad y agrega la barrera ejecutable `scripts/preflight/docs_stack_sync.py` de `DOC-005`. Publica la release `v1.2.1`. Governance **ALTO** por el bloque F (publica un artefacto versionado: tag, push y PR).

### [C-145] `correccion-factual-sincronizacion-del-memo-y-portabilidad-del-harness` — ARCHIVADO (2026-10-26, 77/77, ALTO)

- **Scope (bloques A-H, todos cerrados)**:
  - **A — correccion factual de la tesis (MEDIO)**: `06-implementacion.tex:87` pasa de "16 tests" con `pytest.skip` a 48 pruebas marcadas como integracion que fallan ruidosamente sin PostgreSQL; se retiran los recuentos congelados de `06-implementacion.tex:91` y las referencias internas `OQ1 = A`/`OQ2 = A del change c-72` del cuerpo (la atribucion de `c-72` pasa al Anexo I); se corrigen los roles de `04-marco-metodologico.tex:95`; el tablero es Jira (no GitHub Projects) y se retira el numero fijo de iteraciones. Consigna la causa raiz de A1 (`a0436e0`, `ef656ac`, `8466cbe`, `7408543`) y la evidencia de A2 (59 archivos de test de frontend, sin `node_modules`).
  - **B — sincronizacion del memo (MEDIO)**: upsert del margen `6,66 %` vigente (`N ≈ 2.646`) y `6,74 %` retirado; barrido de las referencias `07-resultados.tex:<linea>` por correspondencia de contenido.
  - **C — precision de la discusion (MEDIO)**: valor pareado `96/130 (0,7385)` en `08-discusion.tex:10` y celdas `+42,1 / +52,1 / +62,0` en `:95`.
  - **D — higiene del registro (BAJO)**: resuelto el placeholder `P4`; declarada la cache FORCE-ESCALATE con su `corpus_hash` distinto; decision de uso confirmada por el autor (2026-10-26); 30 OQ de la FASE 36 confirmadas.
  - **E — portabilidad del arnes (BAJO)**: `allow_abbrev=False` en el parser de `evaluation/sensibilidad_ajustes.py` y manejo limpio del `FileNotFoundError` de `--solo-tiempos`; excluida la procedencia de las caches de predicciones (E2-ii, trabajo futuro).
  - **F — recompilacion y release (ALTO)**: recompilacion en `texlive-thesis`, cuerpo sin anexos <= 100 (109/100/9, margen 0, palanca D9 no necesaria) y release `v1.2.1`.
  - **G — documentacion para agentes (BAJO)**: `CLAUDE.md` y `openspec/config.yaml` alineados con el codigo (Gemini 3.6 Flash, `fastapi==0.143.3`, sin Redis ni LangChain); docstring del test del hibrido corregido.
  - **H — barrera documental (BAJO)**: `scripts/preflight/docs_stack_sync.py` con doce chequeos, cableado en el job `backend-tests` de CI; `12/12 PASS` sobre el arbol corregido.
- **Release**: tag anotado `v1.2.1` sobre C3 `509ffff105c21fed0c07cbf9a46245ba6c53e0e1`; C4 `fc579d8fae8984718c0a398e31977c6eb01903af` consigna el hash de C3 en el Anexo B y en el REGISTRO; PR #43 `docs(tesis): release v1.2.1 - correccion factual y sincronizacion del memo (c-145)` fusionado a `main` con merge commit `13e9281e3f41ec990584e0c6b62e7034c13e422f` (2026-10-26); `git merge-base --is-ancestor v1.2.1 origin/main` = verdadero. **`v1.2.0` (`a49d035c67b32ae17e633ec04b09ecdd2781aac6`) queda inmutable y registrada como superada.** PDF: **109** paginas (cuerpo 100, anexos 9).
- **Cierre de c-135 5.2**: la tarea 5.2 de `c-135-cronologia-y-consistencia-redaccional` se cerro como **no reconstruible con fuente primaria** (las fechas de las iteraciones de los autores no se pudieron recuperar); c-135 queda 35/35.
- **Sucesion respecto del PR #40**: sucede al merge del PR #40 `ramagonzalo` -> `main` (`224fa160d27ff88aa417c34ef9a4026f8862805f`), ya integrado: corrige en `main` el defecto que ese merge dejo y publica `v1.2.1` mediante un PR propio.
- **Dependencias**: PR #40 mergeado en `main` (`224fa16`); imagen `texlive-thesis`; Python 3.12.3 en la maquina de trabajo (CI usa 3.12.15).
- **Leer antes**: `openspec/changes/c-145-correccion-factual-sincronizacion-del-memo-y-portabilidad-del-harness/{proposal,design,tasks}.md`, `docs/Tesis/Correcciones/dictamen-correcciones.md` (seccion "Correccion factual de la release v1.2.0 (c-145)"), `openspec/specs/tesis-document/spec.md`, `openspec/specs/tesis-numeros-canonicos/spec.md`, `openspec/specs/evaluation-framework/spec.md`, `openspec/specs/project-documentation/spec.md`.

## FASE 40 — Compactacion y release v1.2.2 (2026-10-27)

> Changes posteriores a la FASE 39: completan las metricas de la tabla de trabajos previos (C-146) y cierran la integracion de c-146 y c-140 con una compactacion de forma de la tesis (111 a 104 paginas, sin quitar contenido), la reconciliacion de la regla del tope de paginas con la catedra y la release `v1.2.2` (C-147). Governance **ALTO** por la publicacion del tag, el push y el PR.

### [C-146] `completar-metricas-trabajos-previos` — ARCHIVADO (2026-10-27, 22/23; la 6.1 queda BLOQUEADA por acceso institucional externo, BAJO/MEDIO)

- **Scope**: recomendacion B16 del dictamen: completar la fila de Colavito, Lanubile y Novielli (2025) de `tab:trabajos-academicos` con el F1 macro por dataset (NLBSE'23 y NLBSE'24), extraido del manuscrito aceptado de acceso abierto; agregar a la fila de Paramesh y Shreedhara (2019) un puntero al trabajo companero accesible de los mismos autores (Ramya, Paramesh y Shreedhara, arXiv:2103.15822); alta de una entrada bibliografica nueva; y registrar la procedencia (URL, tipo de version y cifras) en `docs/Tesis/Correcciones/extraccion-metricas-trabajos-c-135.md`. La fila de Paket et al. (2024) permanece cualitativa (sin copia ni alternativa accesible).
- **Estado (2026-10-27)**: ARCHIVADO el 2026-10-27 con 22/23. La tarea 6.1 (extraer la metrica directa de la obra original de Paramesh y Shreedhara, 2019) esta BLOQUEADA por acceso institucional externo a Springer Link; se archiva con la tarea abierta por precedente (c-123). Spec sincronizado: `tesis-document` (+1 ~1). Carpeta: `openspec/changes/archive/2026-10-27-c-146-completar-metricas-trabajos-previos`.
- **Dependencias**: c-135 (tabla y registro de procedencia) y c-139 (fila de Paramesh); requisito externo: acceso institucional para desbloquear la 6.1.
- **Governance**: BAJO para las ediciones editoriales; MEDIO para el delta de `tesis-document` (checkpoint de la redaccion del requisito).
- **Leer antes**: `openspec/changes/archive/2026-10-27-c-146-completar-metricas-trabajos-previos/{proposal,design,tasks}.md`, `docs/Tesis/Correcciones/extraccion-metricas-trabajos-c-135.md`

### [C-147] `compactacion-y-release-v1-2-2` — ARCHIVADO (2026-10-27, 23/23 verificadas el 2026-10-27 contra los commits de las partes A-E; 0/23 marcadas al archivar, ALTO)

- **Scope**:
  - **A — compactacion (aplicada en `8c0cf6d`)**: 111 -> **104 paginas totales** (cuerpo 96, anexos 8) con palancas de forma: indice general y listas de tablas/figuras compactados y fusionados, anexos en `\small`, figuras de la seccion 6.8 al 70 % de ancho y espaciado de la bibliografia. Sin contenido cientifico removido ni referencias colgadas.
  - **B — regla de tope reconciliada**: G0.1 de `dictamen-correcciones.md` pasa a metrica = **total del PDF**, valor = **100**, fuente = **exigencia de la catedra**, con el exceso **+4** honrado y defendido; el libro mayor suma las filas de `v1.2.1` (109/100/9), del borrador (111/102/9), de la compactacion (104/96/8) y de `v1.2.2`; el requisito `Presupuesto de páginas preservado` de `tesis-document` se reescribe.
  - **C — cierre de `c-140` (73/73)**: 3.8 regresion completa de backend (`pytest` 1552 passed + 1 xfailed; red de seguridad 3.1 214 passed + 1 xfailed; `scripts/dry_run` 90 passed; preflights de costo 10/10 y 2/2 GREEN), 3.9 seccion "Politica de reintento del tramo de alta (c-140)" en `docs/n8n-workflow-guide.md` (N8N-DOC-007) y 3.10 (CP5) registrada como accion del equipo.
  - **D — release `v1.2.2`**: C1 `445a47b` integra c-146 y c-140 y sube la version; tag anotado `v1.2.2`; C2 `8e97d99` consigna el hash en el Anexo B; `aac73d8` registra la trazabilidad en el registro.
  - **E — archivo**: `c-146` y `c-140` archivados (specs sincronizados), tarea 2.9 de `c-141` cerrada, `c-141` y `c-147` archivados. **`openspec list` sin changes activos.**
- **Release**: tag anotado `v1.2.2` sobre C1 `445a47b4f6fccca3d4611ee3cb7adea4e7350dcc`; PR #48 `docs(tesis): release v1.2.2 - compactacion y cierre de c-146 + c-140 (c-147)` fusionado a `main` con merge commit `07cc075` (2026-10-27); `git merge-base --is-ancestor v1.2.2 origin/main` = verdadero. **`v1.2.1` (`509ffff105c21fed0c07cbf9a46245ba6c53e0e1`) queda inmutable y registrada como superada.** PDF: **104** paginas (cuerpo 96, anexos 8; exceso +4 sobre el tope de 100 total, honrado y defendido).
- **Cierre de la familia FASE 36**: con `c-146` y `c-140` archivados, la familia del dictamen CONEAU v10/v1.1.1 queda integrada y sin changes activos.
- **Dependencias**: PR #43 a #47 (release `v1.2.1` y archivo de `c-135`) en `main`; imagen `texlive-thesis`; PostgreSQL del compose en `127.0.0.1:5433`.
- **Leer antes**: `openspec/changes/archive/2026-10-27-c-147-compactacion-y-release-v1-2-2/{proposal,design,tasks}.md`, `docs/Tesis/Correcciones/dictamen-correcciones.md` (G0.1 del 2026-10-27 y libro mayor), `openspec/specs/tesis-document/spec.md`.

---

## FASE 41 — Sincronizacion de la base de conocimiento y los docs con el stack vigente (2026-10-27)

> Change documental (mas un ajuste acotado del cliente HTTP) posterior a la FASE 40: alinea `knowledge-base/**` y el material de referencia (`docs/parameters_gemini.md`, `docs/n8n-workflow-guide.md`) con el valor vigente del stack (`gemini-3.6-flash`, timeout 30 s por intento / 60 s total / 2 reintentos, `google-genai >=2.31,<3`), conserva rotulada la procedencia historica (calibracion sobre Gemini 2.5 Flash, DD-04), restaura el invariante del timeout del cliente (Axios 65 s > peor caso total del backend 60 s) y amplia la barrera `scripts/preflight/docs_stack_sync.py` de 12 a 16 chequeos (TDD estricto; 35 -> 50 pruebas). Governance **MEDIO** (A, B, C, E) / **BAJO** (D).

### [C-148] `sincronizar-knowledge-base-y-docs-con-el-stack-vigente` — ARCHIVADO (2026-10-27, MEDIO/BAJO)

- **Scope (bloques A-E)**:
  - **A — base de conocimiento (MEDIO)**: `01`, `02`, `05`, `07`, `08` y `09` declaran `gemini-3.6-flash` / "Gemini 3.6 Flash", `google-genai >=2.31,<3` y timeout 30 s por intento (total 60 s, 2 reintentos); DD-04 se rotula "(historico)" y conserva la calibracion sobre 2.5 Flash con remision al valor vigente.
  - **B — material de referencia (MEDIO)**: `docs/parameters_gemini.md` retitulado y con `model`, `timeout` y la restriccion de `google-genai` al valor vigente; el "Historial de Cambios" queda rotulado como registro historico; `docs/n8n-workflow-guide.md:852` pasa a "Gemini 3.6 Flash".
  - **C — procedencia historica (MEDIO)**: la calibracion sobre 2.5 Flash y DD-04 sobreviven rotuladas; se prohibe el reemplazo ciego "2.5" -> "3.6".
  - **D — barrera documental (BAJO, TDD)**: `scripts/preflight/docs_stack_sync.py` pasa de 12 a 16 chequeos (13 modelo vigente en `knowledge-base/**` y material de referencia, 14 timeout vigente en contexto de Gemini, 15 superficie cubierta, 16 invariante del timeout del cliente); `test_docs_stack_sync.py` pasa de 35 a 50 pruebas (RED -> GREEN -> TRIANGULATE). Sobre el arbol corregido: 16/16 PASS, exit 0.
  - **E — invariante del timeout del cliente (MEDIO, noveno archivo)**: `App/Frontend/src/services/api.ts` sube el timeout de Axios de 20 s a 65 s y corrige sus comentarios (65 s > 60 s, peor caso total del backend). Era un hallazgo fuera de alcance en el proposal original; el autor lo incorporo al alcance.
- **Hallazgo adyacente (fuera de alcance)**: los umbrales `0.90` de `docs/n8n-workflow-guide.md:598,610` pertenecen a DOC-004; se registran, no se corrigen.
- **Verificacion**: `openspec validate c-148-... --strict` OK; `python3 -m pytest scripts/preflight -q` 98 passed; backend `pytest -m "not integration" -q` 1498 passed + 54 deselected + 1 xfailed (sin regresiones; total 1553); frontend `npm run lint` (0 errores), `npm run test` (384 passed) y `npm run build` OK.
- **Dependencias**: barrera de c-145 (12 chequeos, 35 pruebas); `CLAUDE.md` y `openspec/config.yaml` ya correctos desde c-145.
- **Leer antes**: `openspec/changes/c-148-sincronizar-knowledge-base-y-docs-con-el-stack-vigente/{proposal,design,tasks}.md`, `openspec/specs/project-documentation/spec.md`.

---

## FASE 42 — Actualizacion de dependencias del backend y endurecimiento de la barrera documental (2026-10-27)

> Change posterior a la FASE 41, disparado por el PR #42 de Dependabot, que no podia mergearse: el bump de dependencias quedaba bloqueado por la propia barrera documental (chequeos 4, 5 y 17) y, ademas, la suite de esa barrera estaba acoplada al estado real del repositorio, de modo que cualquier bump legitimo la rompia (`assert 4 == 1`). Governance **BAJO** (A) / **MEDIO** (B, C).

### [C-149] `actualizar-dependencias-y-endurecer-la-barrera` — ARCHIVADO (2026-10-27, BAJO/MEDIO)

- **Scope (bloques A-C)**:
  - **A — bump de dependencias (BAJO)**: `App/Backend/requirements.txt` adopta las seis versiones exactas del PR #42 de Dependabot (`fastapi` 0.143.3 -> 0.162.0, `starlette` 1.8.0 -> 1.10.0, `sqlalchemy[asyncio]` 2.1.5 -> 2.1.6, `alembic` 1.20.0 -> 1.20.1, `pydantic-settings` 2.16.0 -> 2.16.1, `google-genai` >=2.31.0,<3 -> >=2.33.0,<3); `uvicorn[standard]` queda en 0.54.0. Se conservan los comentarios historicos y se actualizan los que declaraban un hecho vigente que quedaba falso.
  - **B — documentacion vigilada (MEDIO)**: `openspec/config.yaml` (`stack.backend.framework` = `FastAPI 0.162 + Uvicorn 0.54`; `stack.inference.model` = `Gemini 3.6 Flash (google-genai >=2.33,<3)`), `knowledge-base/02_descripcion_general.md` (FastAPI + Uvicorn `0.162.0 / 0.54.0` y `google-genai >=2.33,<3`) y `knowledge-base/09_decisiones_y_supuestos.md` (DD-06 = FastAPI 0.162.0 sobre Uvicorn 0.54.0). N8N 2.11.2 y Uvicorn 0.54.0 no cambian. DD-06 es una decision VIGENTE: se actualiza la version, no se rotula como historia.
  - **C — suite hermetica de la barrera (MEDIO, TDD estricto)**: `scripts/preflight/test_docs_stack_sync.py` reescribe sus fixtures (`_arbol_sincronizado` / `_contenido_arbol` / `_VERS_BASE`) para construir un arbol SINTETICO autosuficiente con las versiones fijadas por la propia suite; ya no lee los `requirements.txt`, `docker-compose.yml` ni `openspec/config.yaml` reales. Se agregan tres pruebas de aislamiento (no hereda los archivos reales; un bump coordinado sigue sincronizado y aisla un drift; un bump aislado del pin de FastAPI falla solo los chequeos de version). 108 -> 111 pruebas.
- **RED/GREEN/TRIANGULATE (Bloque C)**: RED con el Bloque A aplicado y la suite acoplada (`17 failed, 91 passed`; `assert 4 == 1`); GREEN con los fixtures sinteticos (`111 passed`, tambien con el Bloque A aplicado); TRIANGULATE con un bump coordinado del fixture (17/17 PASS y, con un drift inyectado, exactamente 1 FAIL) y con el bump aislado del pin de FastAPI (exactamente 2 FAIL, ambos de version).
- **Barrier RED -> GREEN (Bloque B)**: con A y sin B, `python3 scripts/preflight/docs_stack_sync.py` = 14/17 PASS con los chequeos 4, 5 y 17 en FAIL (nombran `config.yaml` framework `0.143` vs `0.162.0`, `google-genai >=2.31,<3` vs `>=2.33.0,<3`, `02_descripcion_general.md:8,13` y `09_decisiones_y_supuestos.md:21`); tras el Bloque B, 17/17 PASS, exit 0.
- **OpenAPI**: `tests/test_openapi_sync.py` pasa (5 passed) con el entorno instalado; NO se regenero `docs/openapi.json` (el bump se verifico contra las dependencias instaladas; ver duda residual abajo).
- **Verificacion**: `openspec validate "c-149-..." --strict` OK; `python3 -m pytest scripts/preflight/ -q` 111 passed; backend `pytest -m "not integration" -q` 1498 passed + 54 deselected + 1 xfailed (sin regresiones); `ruff check .` OK; frontend `npm run test` 384 passed.
- **Duda residual**: el entorno local NO reinstalo los pines nuevos (regla "no build after changes"), de modo que `tests/test_openapi_sync.py` validó `docs/openapi.json` contra FastAPI 0.143.3 instalada, no 0.162.0. Si CI (que instala desde `requirements.txt`) detecta un cambio de esquema, se regenera `docs/openapi.json` con `python3 scripts/export_openapi.py`.
- **Dependencias**: PR #42 de Dependabot; barrera de la FASE 41 (c-145/c-148; 17 chequeos, 108 pruebas).
- **Leer antes**: `openspec/changes/c-149-actualizar-dependencias-y-endurecer-la-barrera/{proposal,design,tasks}.md`, `openspec/specs/project-documentation/spec.md`.

---

## FASE 43 — Cierre de residuales y separacion del contrato del corpus (2026-10-27)

> Change documental y de codigo (TDD estricto) que cierra cinco residuales de la FASE 42 y un defecto de contrato del corpus. Governance **ALTO** (W2, W4) / **MEDIO** (W3) / **BAJO** (W1, W5 y confirmaciones). W2 y W4 requieren revision del autor antes del merge.

### [C-150] `cerrar-residuales-y-separar-el-contrato-del-corpus` — ARCHIVADO (2026-10-27, ALTO/MEDIO/BAJO)

- **Scope (W1-W5 y confirmaciones)**:
  - **W1 (BAJO, doc)**: se corrige la nota de estado stale de `CHANGES.md` sobre la deuda residual de C-80; C-80 quedo archivado 45/45 el 2026-10-21 (ya registrado en la actualizacion de cierre del roadmap). No se reescribe ninguna entrada fechada.
  - **W2 (ALTO, doc, artefactos archivados)**: se anotan con fecha las tareas de rollback obsoletas de c-148 (9.1, 9.2) y c-149 (7.1), conservando su texto original como evidencia historica (c-148: commit `3392012`, PR #53, merge `6516f5f`; c-149: commit `f666316`, PR #55, merge `4d9e072`).
  - **W3 (MEDIO, codigo, TDD estricto)**: `evaluation/corpus.py` separa el contrato de CLASIFICACION (obligatorio) del de TIEMPOS (opcional pero estricto cuando presente) y colapsa el loader tolerante duplicado `cargar_corpus_tolerante` en el unico `cargar_corpus()`; se actualizan los consumidores (`evaluation/deterministic_measurement.py`, `evaluation/sensibilidad_ajustes.py`) y los tests. `_a_float` NO se relaja para los campos presentes.
  - **W4 (ALTO, doc, ledger de gobernanza)**: se reasigna el requisito de fidelidad del estado desde `project-documentation` a `employee-directory` (el documento `docs/directorio-evidencia-cumplimiento.md` esta gobernado por DIR-009). Se registra con precision el estado de C-60 (33/33; la tarea 7.4 esta `[x]` porque su contenido es registrar la revision HIGH como PENDIENTE) y se deja la aprobacion HIGH del autor explicitamente PENDIENTE. No se concede ninguna aprobacion.
  - **W5 (BAJO, doc)**: se eliminan las 14 marcas U+2713 de `CHANGES.md` (encabezados de gate a texto explicito `COMPLETADO` / `(completado)`; items de scope completados, se retira la marca porque la completitud ya la declara el encabezado).
  - **Confirmaciones (BAJO, doc)**: el ledger del dictamen registra la aprobacion del autor (2026-10-27) de la redaccion final de `00-resumen.tex` y `09-conclusiones.tex` (item 9), ratifica las decisiones provisionales del item 8 y deja G0.7a/OQ7a (ablacion paga) y OQ6 (`usuario_final`, CRITICAL) explicitamente PENDIENTES.
- **Governance**: W2 y W4 ALTO (el autor revisa esos diffs antes del merge); W3 MEDIO; W1, W5 y confirmaciones BAJO.
- **Verificacion**: `cd evaluation; pytest` 473 passed; barrido de U+2713 en `CHANGES.md` sin coincidencias; `openspec validate c-150-cerrar-residuales-y-separar-el-contrato-del-corpus --strict` OK.
- **Hallazgo (W3)**: el corpus real presente en `data/corpus_evaluacion_pseudonimizado.json` tiene 200 casos y 0 tiempos nulos (la premisa de "56 casos nulos" del proposal no coincide con la version actual del archivo); el corpus real cumple el contrato de clasificacion y carga con el unico `cargar_corpus()`. La opcionalidad de los tiempos queda cubierta por tests sinteticos (mixto, ausente, nulo, borde 0).
- **Dependencias**: FASE 42 (C-149); c-148 y c-149 archivados.
- **Leer antes**: `openspec/changes/c-150-cerrar-residuales-y-separar-el-contrato-del-corpus/{proposal,design,tasks}.md`, `openspec/specs/evaluation-corpus/spec.md`, `openspec/specs/employee-directory/spec.md`.

---

## FASE 44 — Correccion del pin de google-genai en el material de referencia y ampliacion de la barrera documental (2026-10-28)

> Change documental y de barrera (TDD estricto) posterior a la FASE 43. Cierra el residual que dejo la FASE 42: `docs/parameters_gemini.md` seguia citando `google-genai >=2.31,<3` como valor vigente en dos pasajes (linea 5 y linea 101) frente al pin `>=2.33.0,<3` de `App/Backend/requirements.txt`. La barrera no lo detectaba porque el chequeo 17 solo recorria `knowledge-base/**`, no el material de referencia (`DOCS_REFERENCIA`). Governance **BAJO**.

### [C-151] `corregir-pin-google-genai-y-ampliar-la-barrera` — ARCHIVADO (2026-10-28, BAJO)

- **Scope (bloques A y B)**:
  - **A — corregir el documento (BAJO)**: en `docs/parameters_gemini.md` la restriccion citada como vigente pasa de `google-genai >=2.31,<3` a `google-genai >=2.33,<3` en sus DOS pasajes vigentes: linea 5 ("Versión de cliente", seccion `## Invocación de API`) y linea 101 (nota de valor vigente dentro de `## Historial de Cambios`). El encabezado y el resto del registro historico NO se tocan.
  - **B — ampliar la barrera (BAJO, TDD estricto)**: `scripts/preflight/docs_stack_sync.py` extrae el escaneo de la restriccion de `google-genai` a un helper puro (`_restricciones_genai_no_compatibles(rutas, genai_req)`, diseno D4) que reutiliza `_restricciones_genai_en_linea`, `_restriccion_compatible` y `_lineas_con_marcador`, y lo invoca sobre la union de `knowledge-base/**` y `DOCS_REFERENCIA` (`_archivos_superficie`) SOLO para `google-genai` (diseno D2). Los barridos de N8N, FastAPI y Uvicorn siguen limitados a `knowledge-base/**`: la discrepancia ajena `docs/n8n-workflow-guide.md:767` (`N8N 2.25.7`, un registro historico sin marcador reconocido) NO se reporta. El valor esperado se sigue derivando en tiempo de ejecucion de `App/Backend/requirements.txt`; no se hardcodea ninguna version. La barrera se mantiene en 17 chequeos (sin chequeo 18).
- **RED/GREEN/TRIANGULATE (Bloque B)**: RED con el test `test_chequeo_17_genai_no_historico_en_referencia_falla` (`1 failed, 63 passed`; `AssertionError: Se esperaba al menos un FAIL ... assert []`, porque el chequeo 17 aun no escaneaba `parameters_gemini.md`); GREEN con la ampliacion de la superficie (`64 passed`); TRIANGULATE con tres casos nuevos (`67 passed`): el caso positivo (`>=2.33,<3` pasa), la exencion historica (`>=2.31,<3` bajo un encabezado con marcador historico no falla; se uso `## Historial de Cambios (registro historico; antecedentes)` porque la frase pelada "Historial de Cambios" no contiene un marcador de `MARCADORES_HISTORICOS`) y la no regresion de alcance (`N8N 2.25.7` en el material de referencia no falla). REFACTOR: helper puro, sin duplicacion del bucle de `google-genai`.
- **Fixture hermetico (c-149)**: `_VERS_BASE` del arbol sintetico se alinea con el repo real (`google-genai` `>=2.33.0,<3` / `>=2.33,<3`), de modo que el caso RED `>=2.31,<3` es realmente mas laxo que el pin del fixture; se ajustan las dos mutaciones existentes de `google-genai` en consecuencia.
- **Barrier (arbol real)**: con el Bloque B aplicado y el Bloque A pendiente, la barrera reportaria FAIL nombrando `parameters_gemini.md`; tras el Bloque A, `python3 scripts/preflight/docs_stack_sync.py` = **17/17 PASS, exit 0**.
- **Verificacion**: `openspec validate "c-151-..." --strict` OK; `python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q` 67 passed; `python3 -m pytest scripts/preflight -q` 115 passed (sin regresiones: 111 de la FASE 42 + 4 nuevas).
- **Rollback**: `git revert` de los commits del change: `docs/parameters_gemini.md` vuelve a citar `>=2.31,<3` y el chequeo vuelve a la superficie limitada a `knowledge-base/**`. No se publica tag ni release.
- **Dependencias**: barrera de la FASE 41/42 (c-145/c-148/c-149; 17 chequeos, 111 pruebas); `App/Backend/requirements.txt` ya declara el pin correcto `>=2.33.0,<3`.
- **Leer antes**: `openspec/changes/c-151-corregir-pin-google-genai-y-ampliar-la-barrera/{proposal,design,tasks}.md`, `openspec/specs/project-documentation/spec.md`.

---

## FASE 45 — Endurecimiento del directorio para datos reales (2026-10-28)

> Change de endurecimiento del directorio (`employee-directory`) para habilitar de forma segura el tratamiento de PII real. Governance **HIGH** (datos personales bajo Ley 25.326; retencion y ARCO; visibilidad entre sectores). Se aplica por etapas (semillas de TDD estricto). **Gate de gobernanza**: la aprobacion humana HIGH del autor fue **CONCEDIDA el 2026-10-28** y precede a toda implementacion desde el grupo 2 en adelante.

### [C-153] `endurecer-el-directorio-para-datos-reales` — ARCHIVADO (2026-10-28, HIGH)

- **Aprobacion humana HIGH**: **CONCEDIDA (2026-10-28)**. Registrada de forma verificable en `docs/directorio-evidencia-cumplimiento.md` seccion 4 y en este indice. Estado anterior: PENDIENTE (c-60 7.4).
- **Scope (grupos 1-7 aplicados)**:
  - **Grupo 1 — preparacion, red de seguridad y puerta de gobernanza**: hook activado; red de seguridad del directorio (baseline `80 passed`); gate HIGH registrado.
  - **Grupo 2 — Tema A (cifrado at-rest)**: ADR de reversion `docs/seguridad/adr-001-reversion-dir-005-cifrado-contacto.md` (revierte DIR-005/DIR-010; la justificacion por minimizacion previa queda marcada SUPERADA); `email`/`telefono` pasan a `EncryptedText` (Fernet) en `app/models/empleado.py`; migracion Alembic reversible `021_directorio_contacto_cifrado` con backfill; inventario de rotacion extendido en `scripts/rotate_fernet_key.py`; helpers `encrypt_value`/`decrypt_value` encapsulados en `app/utils/encryption.py`.
  - **Grupo 3 — Tema B (indice ciego determinista)**: `email_bidx`/`telefono_bidx` (HMAC-SHA-256 con la clave dedicada `directory_blind_index_key`), derivacion pura en `app/utils/blind_index.py`, repositorio resolviendo por indice, unicidad del email sobre `email_bidx`, migracion `022_directorio_indice_ciego`.
  - **Grupo 4 — Tema C (control de acceso)**: politica por sujeto en `app/services/role_policy.py` (admin/mesa GLOBAL; `usuario_final` solo su fila; `gestion_incidentes` sin lectura), limitacion de tasa y anti-enumeracion en `app/routes/directorio.py`, test negativo de aislamiento entre sectores (VIS-001/VIS-002).
  - **Grupo 5 — Tema D (auditoria durable)**: tabla append-only `directorio_auditoria` sin PII (patron `incidente_evento`), migracion `023_directorio_auditoria`, helper unico `registrar_evento_auditoria`, auditoria de gestion y de los canales de resolucion sin el contacto en claro.
  - **Grupo 6 — Tema E (retencion, ARCO y minimizacion)**: runbook de retencion con purga MANUAL y alerta de acumulacion (solo conteo, sin PII), ARCO de acceso y rectificacion ademas de supresion, ventana de retencion de la auditoria alineada con el ciclo de vida, revision de minimizacion (solo columnas derivadas no-PII).
  - **Grupo 7 — Tema F (operacion, gobernanza y specs)**: inventario de rotacion Fernet extendido a las columnas del directorio y documentado en `docs/seguridad/gestion-secretos-y-rotacion.md`; variables de clave dedicada en `settings.py`/`.env.example`/`conftest.py`/CI; mecanismo de activacion deliberado y auditado (DIR-014) en `app/services/directorio_activacion.py` + CLI env-gateado `scripts/activar_directorio.py`, bloqueado por defecto y sin interruptor de runtime; delta `employee-directory` verificado (`openspec validate --strict`); `docs/openapi.json` sincronizado; procedimientos de `docs/seguridad/` y evidencia de cumplimiento actualizados; este registro en `CHANGES.md`.
- **Leer antes**: `openspec/changes/c-153-endurecer-el-directorio-para-datos-reales/{proposal,design,tasks}.md`, `openspec/specs/employee-directory/spec.md`, `docs/seguridad/adr-001-reversion-dir-005-cifrado-contacto.md`, `docs/seguridad/gestion-secretos-y-rotacion.md`, `docs/directorio-evidencia-cumplimiento.md`.
- **Verificacion (grupo 8, 42/42)**: verificacion final de integracion completada (suite backend offline + subconjunto de integracion PostgreSQL sobre base descartable, lint backend y build/lint de frontend), validacion OPSX estricta y revision humana HIGH firmada (checklist del autor); el change quedo ARCHIVADO el 2026-10-28.
- **Rollback**: `git revert` de los commits del change revierte las migraciones `021`-`023`, la politica por sujeto, el indice ciego, la auditoria durable y el mecanismo de activacion; no se publica tag ni release.

---

## FASE 46 — Regularizacion del indice (C-152, C-154) (2026-10-28)

> Changes documentales del 2026-10-28 que no encajaban en las FASES 44 (C-151) ni 45 (C-153). Se registran aqui C-152 (deriva documental de la base de conocimiento y la guia N8N) y C-154 (correccion del harness de la ablacion paga del prompt); ambos ARCHIVADOS con las specs principales sincronizadas.

### [C-152] `corregir-deriva-documental-knowledge-base-y-guia-n8n` — ARCHIVADO (2026-10-28, 12/12)

- **Scope**: se alinea el marco de estado de la base de conocimiento con el archivado real de los changes referenciados. En `knowledge-base/07_flujos_principales.md` las referencias a `C-02`, `C-04` y `C-05` como "pendiente" pasan al estado implementado, sin borrar el hecho historico. En `knowledge-base/10_preguntas_abiertas.md` se marcan como resueltas las preguntas de `C-17` (CSV del corpus), `C-05` (credenciales y verificacion funcional de canales) y `C-02` (instancia N8N de pruebas). En `docs/n8n-workflow-guide.md` se rotula como historica la seccion "Resultados de verificacion 7.1-7.6" con un token reconocido por `MARCADORES_HISTORICOS` en el encabezado, de modo que `N8N 2.25.7` no se lea como la version vigente (el compose fija `n8nio/n8n:2.11.2`), conservando el registro sin reescribirlo. Commit de archive `76695e6`.
- **Verificacion**: `python3 scripts/preflight/docs_stack_sync.py` con codigo 0 (sin nuevos hallazgos respecto de la linea base); `python3 -m pytest scripts/preflight -q` en verde; `openspec validate "c-152-corregir-deriva-documental-knowledge-base-y-guia-n8n" --strict --no-interactive` OK; sin emojis, sin modificacion de los cinco identificadores canonicos de sector, los valores de `gemini-3.6-flash`, `requirements.txt`, `openspec/config.yaml` ni codigo de `App/`.
- **Rollback**: `git checkout` de los tres archivos documentales (`knowledge-base/07_flujos_principales.md`, `knowledge-base/10_preguntas_abiertas.md`, `docs/n8n-workflow-guide.md`) restituye el estado previo. No hay migracion ni release.
- **Leer antes**: `openspec/changes/archive/2026-10-28-c-152-corregir-deriva-documental-knowledge-base-y-guia-n8n/{proposal,design,tasks}.md`, `openspec/specs/project-documentation/spec.md`.

### [C-154] `corregir-el-harness-de-la-ablacion-paga` — ARCHIVADO (2026-10-28, 21/21)

- **Scope**: se corrigen por TDD estricto los dos defectos del harness de la ablacion paga del prompt (`evaluation/sensibilidad_ajustes.py`). Defecto A (clave envenenada): `preparar_entorno_offline()` inyectaba una `GEMINI_API_KEY` inerte que el camino pago usaba, con las 138 invocaciones fallando por `API_KEY_INVALID`; el camino pago resuelve ahora la credencial real de `App/Backend/.env` sobre `os.environ` sin romper los caminos offline. Defecto B (prompt congelado): el import anticipado de `gemini_classifier` en `App/Backend/app/classifiers/__init__.py` congelaba `_PROMPT_TEMPLATE` antes de que el brazo `sin-reglas` fijara su ruta; el paquete pasa a import perezoso (`__getattr__`, PEP 562) para que cada brazo cargue su propio prompt. Tras la correccion se corrieron los dos brazos ya autorizados, se cerro el nivel c del reporte de sensibilidad y se propago el valor a `numeros-canonicos.md`, `07-resultados.tex`, `08-discusion.tex` y la entrada G0.7a del ledger. Commit de archive `a493083`.
- **Verificacion**: `cd evaluation && pytest tests/test_sensibilidad_ajustes.py -q` en verde; `cd evaluation && pytest -q` 0 fallos; `cd App/Backend && pytest tests/test_prompt_resolution.py -q` 0 fallos; los dos brazos pagos escribieron sus archivos de predicciones con `fallbacks` bajo (no 69/69 por `API_KEY_INVALID`) y el reporte de sensibilidad incluye la seccion del nivel c (aciertos, reservas y McNemar) en lugar de "no computado"; coherencia de la propagacion del nivel c en los cuatro documentos.
- **Rollback**: revertir el commit restaura el harness previo; la corrida paga no se revierte, pero sus salidas son archivos propios ignorados por git y el reporte de sensibilidad es regenerable.
- **Leer antes**: `openspec/changes/archive/2026-10-28-c-154-corregir-el-harness-de-la-ablacion-paga/{proposal,design,tasks}.md`, `openspec/specs/evaluation-framework/spec.md`, `docs/Tesis/Correcciones/dictamen-correcciones.md`, `docs/Tesis/Correcciones/numeros-canonicos.md`.

---

## FASE 47 — Regularizacion del indice (C-155, C-156, C-157) (2026-10-28)

> Registro retroactivo de tres changes documentales ARCHIVADOS el 2026-10-28 que no tenian entrada en este indice (la linea Total aun los daba por "en aplicacion"). Se leen sus conteos de los `tasks.md` archivados; no se reabre ninguno.

### [C-155] `refrescar-el-indice-y-corregir-deriva-documental` — ARCHIVADO (2026-10-28, 17/17)

- **Scope**: refresca `CHANGES.md` (C-151 y C-153 a ARCHIVADO, entradas de C-152 y C-154, lineas de resumen) y corrige la deriva de la base de conocimiento (`knowledge-base/07_flujos_principales.md`, `03_actores_y_roles.md`) y de `docs/por_implementar.md` contra el codigo y `settings.py`.
- **Verificacion**: `openspec validate "c-155-refrescar-el-indice-y-corregir-deriva-documental" --strict --no-interactive` (tarea 4.1 de su `tasks.md`); sin cambios de codigo, de los cinco identificadores canonicos de sector, de `requirements.txt` ni de `openspec/config.yaml`.
- **Rollback**: `git checkout` de los archivos documentales; no hay migracion ni release.
- **Leer antes**: `openspec/changes/archive/2026-10-28-c-155-refrescar-el-indice-y-corregir-deriva-documental/{proposal,design,tasks}.md`.

### [C-156] `reconciliar-el-gap-assessment-y-endurecer-la-documentacion-de-cumplimiento` — ARCHIVADO (2026-10-28, 27/27)

- **Scope**: reconcilia `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` con el estado vigente; agrega un lint documental hermetico de `docs/seguridad/` (`App/Backend/tests/test_compliance_docs_lint.py`), el aviso de privacidad del saludo telefonico en el TwiML (`cost_guard/twiml.py`), la seccion de cadena de custodia (control 5.28) y `docs/seguridad/inventario-licencias.md`; corrige la afirmacion de la tesis sobre MFA y rotacion de claves.
- **Verificacion**: `cd App/Backend; pytest -m "not integration"` (tarea 8.1), `pytest tests/test_twiml_record.py` y `openspec validate ... --strict --no-interactive` (tarea 8.3); el PDF queda para recompilar en una release posterior.
- **Rollback**: revertir el commit; sin migracion.
- **Leer antes**: `openspec/changes/archive/2026-10-28-c-156-reconciliar-el-gap-assessment-y-endurecer-la-documentacion-de-cumplimiento/{proposal,design,tasks}.md`.

### [C-157] `cerrar-las-preguntas-abiertas-y-decisiones-de-tesis` — ARCHIVADO (2026-10-28, 21/21)

- **Scope**: cierra IN-06, IN-03 y SU-05 en `knowledge-base/10_preguntas_abiertas.md`, la observacion O8 del ledger del dictamen, agrega la nota factica de IN-03 en el Anexo C y las dos subsecciones faltantes de `10-recomendaciones.tex` (B1).
- **Verificacion**: `python3 -m pytest scripts/preflight -q` (tarea 6.2) y `openspec validate ... --strict --no-interactive` (tarea 6.3); sin cambios de codigo de aplicacion.
- **Rollback**: `git checkout` de los archivos editados.
- **Leer antes**: `openspec/changes/archive/2026-10-28-c-157-cerrar-las-preguntas-abiertas-y-decisiones-de-tesis/{proposal,design,tasks}.md`.

---

## FASE 48 — Correcciones de la tesis por el dictamen CONEAU v10/v1.2.5 (2026-10-28)

> Tres changes documentales para el dictamen CONEAU del 2026-10-28 sobre la tesis v10 / release `v1.2.5` (`auditorias/Dictamen_Tesis_v10_v1.2.5_CONEAU_2026-10-28.md`), independientes del software y aplicados en secuencia: c-158 (A1 y A2), c-159 (A3 y A4) y c-160 (observaciones B). Gobernanza MEDIO.

### [C-158] `procedencia-de-datos-y-configuracion-evaluada-vs-entregada` — ARCHIVADO (2026-10-29, 41/42; la 7.1 diferida a los autores)

- **Scope**: A1, apartado "Procedencia de los datos del brazo automatizado" en 4.5 con recordatorio en la Seccion 8 y correcciones conexas en 1.8, 9.1, 6.4, la leyenda de la Figura 10 y el Anexo F (predicciones en `evaluation/evidence/`, registros primarios no versionados, `\path{}` para las rutas largas); A2, tabla `tab:configuracion-evaluada-entregada` en el Anexo B (commit evaluado `d6bb474` frente al tag `v1.2.5`) con remisiones desde 5.4, 6.1, 6.2, 6.3, 6.5, 6.7, 7.4 y el Anexo H; precision de "commit definitivo" en el Anexo B; `Gomez2026_repositorio` a "Version 1.2.5" (`urldate` 2026-10-28); parrafo del dictamen del 28-10 en el Anexo I.
- **Verificacion**: compilacion Docker con 0 errores, 0 indefinidas, 0 multiply defined, 0 `??` y 25 Overfull (linea base 26); 109 paginas (cuerpo 100, anexos 9; linea base 106 / 98 / 8); `verify_citations.py` PASS; `openspec validate "c-158-procedencia-de-datos-y-configuracion-evaluada-vs-entregada" --strict --no-interactive`; sin cambios de `App/`, `openspec/config.yaml`, `requirements.txt` ni `docs/Tesis/v9 (IA)/`.
- **Consultas pendientes a los autores**: Q1 (inicio y horas de la corrida telefonica), Q2 (version desplegada de `backend-corpus` y `n8n-corpus`), Q3 (quien recito las llamadas y en que entorno), Q4 (comando del arnes del 2-10), Q5 (intervalo efectivo del disparador IMAP), Q6 (reasociacion de la `cache_meta`), Q7 (registros primarios) y Q8 (proxy del 2-10); cada una deja un marcador `% PENDIENTE AUTORES` o una entrada PENDIENTE en `docs/Tesis/Correcciones/dictamen-correcciones.md`.
- **Rollback**: `git checkout --` de los archivos editados; sin efecto en runtime ni release.
- **Leer antes**: `openspec/changes/archive/2026-10-29-c-158-procedencia-de-datos-y-configuracion-evaluada-vs-entregada/{proposal,design,tasks}.md`, `docs/Tesis/Correcciones/dictamen-correcciones.md` (seccion c-158) y `docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md` (Seccion 7).
- **Coordinacion**: c-159 usa la etiqueta `tab:configuracion-evaluada-entregada` desde las leyendas de las Figuras 1 y 4 y agrega su entrada a esta fase.

### [C-159] `reconciliar-figuras-tablas-y-evidencia-cualitativa` — ARCHIVADO (2026-10-29, 39/39)

- **Scope**: A3, Figuras 1, 4 y 5 regeneradas desde `docs/diagrams/{componentes,secuencia,er_modelo_datos}.md` (gate por etapa, reserva, disparador por directorio con fecha, N8N 2.11.2, respuesta real del alta), Figura 2 reemplazada por `docs/diagrams/arquitectura_sistema.md` (cinco capas y tres canales), Tabla 5 reescrita desde el ORM (contacto cifrado, cuatro roles, sin texto encimado), Tabla 8 reconciliada con el gap assessment (GV 2, ID 2, DE 1, RS 2) y lista de C-61 con 5.2 y 5.9; A4, tres casos literales en la Seccion 8.6, confianza leida por etapa, columna de aciertos laxos en la Tabla 16 (32 de 53) y lectura interpretativa por frontera, con las cifras recomputadas por `docs/Tesis/Correcciones/recontar_errores_frontera.py` (TDD estricto) y registradas en `numeros-canonicos.md` Seccion 3.13.
- **Verificacion**: compilacion Docker con 0 errores, 0 indefinidas, 0 multiply defined, 0 `??` y 24 Overfull (base 25); 108 paginas (cuerpo 99, anexos 9; base 109 / 100 / 9); `verify_citations.py` PASS; `python -m pytest docs/Tesis/Correcciones -q` en `eval-tests` 50 passed; `openspec validate "c-159-reconciliar-figuras-tablas-y-evidencia-cualitativa" --strict --no-interactive`; sin cambios de `App/`, `n8n/`, `evaluation/`, `openspec/config.yaml`, `requirements.txt` ni `docs/Tesis/v9 (IA)/`.
- **Rollback**: `git checkout --` de los archivos editados y borrado de `docs/diagrams/arquitectura_sistema.md` y de los dos archivos Python nuevos; los PNG se restauran desde git. Sin efecto en runtime.
- **Dependencias**: c-158 (etiqueta `tab:configuracion-evaluada-entregada`); c-160 se aplica despues y no toca las figuras.
- **Leer antes**: `openspec/changes/archive/2026-10-29-c-159-reconciliar-figuras-tablas-y-evidencia-cualitativa/{proposal,design,tasks}.md`, `docs/Tesis/Correcciones/dictamen-correcciones.md` (seccion c-159) y `docs/Tesis/Correcciones/numeros-canonicos.md` (Seccion 3.13).

### [C-160] `residuos-de-correccion-anexo-i-y-consistencia-interna` — ARCHIVADO (2026-10-29, 42/42)

- **Scope**: B5, retiro de los siete residuos del proceso de correccion del cuerpo (1.4, 5.5, 6.3, 8.5, 9.1 y las notas de 9.1 y 9.4), trasladados literales al registro; B6, Anexo I con parrafo de naturaleza y autoria de los dictamenes, punteros corregidos, residuos registrados, tabla propia del dictamen del 28-10 (A1 a A4 y B5 a B8) y decisiones c-72, c-74 y c-82; B7, Tabla 18 y prosa de la seccion 10 (TLS posterior a la campana, objetivos 3 y 6 alcanzados parcialmente) y resumen y abstract con la calificacion dentro de la muestra; B8, comparacion 0,7385 frente a 0,6769 en 5.5, remisiones de 5.1, 8.5 y el Anexo G, formulacion canonica del alcance del gate y disparador por directorio fechado (13-10-2026). Sin valores canonicos nuevos.
- **Verificacion**: compilacion Docker con 0 errores, 0 indefinidas, 0 multiply defined, 0 `??` y 24 Overfull (igual a la base); 109 paginas (cuerpo 99, anexos 10; base 108 / 99 / 9); resumen ES 249 y EN 245 (maximo 250); `verify_citations.py` PASS; `openspec validate "c-160-residuos-de-correccion-anexo-i-y-consistencia-interna" --strict --no-interactive`; sin cambios de `App/`, `n8n/`, `evaluation/`, `openspec/config.yaml`, `requirements.txt` ni `docs/Tesis/v9 (IA)/`.
- **Consultas pendientes a los autores**: OQ1 (autoria de los dictamenes: se declara el perfil `Prompt2.docx` aplicado mediante un modelo de lenguaje), mas las heredadas de c-158 (Q1 a Q8) y OQ5 (alcance operativo del disparador por directorio).
- **Rollback**: `git checkout --` de los archivos editados; sin efecto en runtime ni release.
- **Dependencias**: c-158 y c-159 (se aplica despues; no revierte sus ediciones). La release posterior a la familia la publica el orquestador.
- **Leer antes**: `openspec/changes/archive/2026-10-29-c-160-residuos-de-correccion-anexo-i-y-consistencia-interna/{proposal,design,tasks}.md` y `docs/Tesis/Correcciones/dictamen-correcciones.md` (seccion c-160).

---

## FASE 49 — Cierre de marcadores y decisiones del dictamen CONEAU v10/v1.2.5 (2026-10-28)

> Dos changes posteriores a la FASE 48 (C-161, documental y de datos; C-162, flujo N8N) que cierran los items que el dictamen CONEAU del 2026-10-28 sobre la tesis v10 / release `v1.2.5` dejo abiertos (`auditorias/Dictamen_Tesis_v10_v1.2.5_CONEAU_2026-10-28.md`). C-161 cierra las ocho consultas a los autores (Q1-Q8), refuerza la naturaleza del Anexo I como autoevaluacion (OQ1-B), fija el Mermaid como fuente unica de la Figura 2 (retiro del drawio), corrige tres afirmaciones sobre el perfil Nginx del despliegue de la campana y versiona los sidecars PII-free; C-162 cierra OQ5 (alcance operativo del disparador por directorio) con la propagacion del contacto del reportante en el POST del flujo N8N. Gobernanza BAJO (C-161) y MEDIA/ALTA (C-162).

### [C-161] `cierre-de-marcadores-y-decisiones-del-dictamen` — ARCHIVADO (2026-10-29, 34/34)

- **Scope**: cierre de Q1-Q8 en `04-marco-metodologico.tex` (fechas telefonicas "5 y 6 de octubre", version desplegada "no consta", recitado de Luca Gomez con softphone y SF20GM7, arnes del 2-10 con `--source json`/`--insecure`, SMTP e intervalo IMAP "no consta") y en `12-anexos.tex` (Anexo F: registros primarios no conservados en el repositorio); propagacion de la fecha a 1.8, la leyenda de la figura telefonica y el cronograma; OQ1-B: Anexo I como autoevaluacion de control de calidad interno frente a criterios CONEAU; Figura 2 = A (Mermaid unico; `Diagrama de Capas.drawio` archivado); correccion Nginx distinguiendo los dos despliegues (telefonia en perfil aislado `corpus` sin proxy; ingesta del 2-10 en stack base con Nginx) en 5.1, 11.1 y Anexo A; versionado de los sidecars PII-free con relajacion de `.gitignore`; registro en `dictamen-correcciones.md` (seccion c-161). Commit de apply y archive `0ee0584`.
- **Verificacion**: compilacion Docker con exit 0, 0 errores, 0 referencias indefinidas, 0 `??` y `Overfull` <= linea base (24); 109 paginas -> 110 paginas (delta +1 sobre la base de c-160, dentro del presupuesto D9 de 0 a +1); `verify_citations.py` PASS; `openspec validate "c-161-cierre-de-marcadores-y-decisiones-del-dictamen" --strict --no-interactive`; `grep "PENDIENTE AUTORES"` = 0; `grep "no incluyó el proxy"` = 0; sidecars PII-free trackeados y `data/corpus_resultados_n8n.json` sin commitear (OQ2); sin cambios de `App/`, `n8n/`, `evaluation/`, `openspec/config.yaml`, la lista canonica de sectores ni `docs/Tesis/v9 (IA)/`.
- **Consultas/preguntas abiertas**: OQ1 (listado exacto de las repeticiones telefonicas), OQ2 (sidecar autoritativo de N8N: 4 filas locales frente a 119 de la corrida; bloquea su `git add`) y OQ3 (eventual exportacion de los registros primarios).
- **Rollback**: `git checkout --` de las fuentes `.tex`, del render, del registro, de `.gitignore`, de `data/README.md` y de `CHANGES.md` tocados; restaurar el drawio desde `docs/diagrams/archive/`. Sin efecto en runtime ni release.
- **Dependencias**: la familia c-158..c-160 (archivada el 2026-10-29). No revierte sus ediciones.
- **Leer antes**: `openspec/changes/archive/2026-10-29-c-161-cierre-de-marcadores-y-decisiones-del-dictamen/{proposal,design,tasks}.md`, la seccion "Dictamen v10 / v1.2.5 (2026-10-28) - c-161" de `docs/Tesis/Correcciones/dictamen-correcciones.md` y `docs/Tesis/Correcciones/preguntas-para-lucas-dictamen-2026-10-28.md`.

### [C-162] `propagar-el-contacto-del-reportante-en-el-flujo-n8n` — ARCHIVADO (2026-10-29, 20/20, MEDIA/ALTA)

- **Scope**: el workflow N8N entregado no enviaba el contacto del reportante en `POST /api/v1/incidentes`, de modo que TODOS los incidentes de correo y telefonia ingresados por N8N caian en revision humana por VIS-005 (c-82) sin importar la confianza de la clasificacion; el defecto era de transporte, porque el backend ya resolvia al reportante contra el directorio a partir de `reportante_email` y `reportante_telefono`. Nodo `Normalizar entrada del incidente`: emite `reportante_email` (correo, desde el remitente) y `reportante_telefono` (telefonia, desde `caller_number`), `null` en el canal que no corresponde; nodo `HTTP POST a MESA-AYUDAS`: agrega ambos campos al `jsonBody`, null-safe (`|| null`). El contacto es transitorio (el modelo solo guarda `reportante_empleado_id`; no se persiste crudo ni se audita) y el comentario C-40/C-53 del normalizador se reescribe. El canal web queda FUERA de alcance (la cuenta del POST es la del operador). Cinco pruebas nuevas en `App/Backend/tests/test_n8n_workflow.py`; actualizados `docs/n8n-workflow-guide.md`, la tabla `tab:configuracion-evaluada-entregada` (Anexo B) y el registro de OQ5 en `dictamen-correcciones.md`. Capability `n8n-workflow`: 3 requisitos MODIFIED (entre ellos N8N-EMAIL-002, cuyo MUST NOT se acota a la persistencia y la auditoria del `remitente` crudo: supersede parcial de C-40/C-53) y N8N-CONTACT-001 ADDED. Commit de apply y archive `124403e`.
- **Verificacion**: `cd App/Backend; pytest -m "not integration" -q` = 1585 passed, 60 deselected, 1 xfailed (linea base 1580 passed; +5 pruebas c-162); `pytest tests/test_n8n_workflow.py tests/test_c135_n8n_retry_policy.py -q` = 190 passed, 1 xfailed; `openspec validate "c-162-propagar-el-contacto-del-reportante-en-el-flujo-n8n" --strict --no-interactive` = PASS; PDF de 110 a 111 paginas (delta +1, dentro del presupuesto de 0 a +1); sin cambios de `App/Backend/app/**`, `evaluation/`, `openspec/config.yaml` ni `docs/Tesis/v9 (IA)/`.
- **Rollback**: revertir el commit restaura el `jsonBody` anterior (sin los dos campos) y el comentario C-40/C-53; sin migraciones ni cambios de esquema, los incidentes dejan de resolver reportante y vuelven a derivar por VIS-005, que era el comportamiento previo. Los cambios de docs y tesis se revierten en el mismo commit.
- **Governance**: MEDIA/ALTA (toca `n8n/` y el comportamiento entregado; no modifica `App/Backend/app/**`, porque el schema y el resolver ya soportan el contrato). El change solo deja la nota de la release `v1.2.6`, que lo incluye; no la publica.
- **Dependencias**: ninguna; reutiliza `resolver_reportante` y VIS-005 (c-82), ya implementados. Se aplico entre c-161 y c-163 (cadena de paginas del PDF 110 -> 111 -> 112); c-163 y c-164 no lo revierten.
- **Leer antes**: `openspec/changes/archive/2026-10-29-c-162-propagar-el-contacto-del-reportante-en-el-flujo-n8n/{proposal,design,tasks}.md` (delta spec en `specs/n8n-workflow/`), `openspec/specs/n8n-workflow/spec.md`, `docs/n8n-workflow-guide.md` y la seccion "Dictamen v10 / v1.2.6 (2026-10-29) - c-162" de `docs/Tesis/Correcciones/dictamen-correcciones.md`.

---

## FASE 50 — Recomendaciones 9 a 13 del dictamen CONEAU v10/v1.2.5 (2026-10-29)

> Change documental posterior a la FASE 49: cierra las recomendaciones 9 a 13 del dictamen CONEAU del 2026-10-28 sobre la tesis v10 / release `v1.2.5` (`auditorias/Dictamen_Tesis_v10_v1.2.5_CONEAU_2026-10-28.md`), que las FASES 48 y 49 no cubrian. Docs-only sobre `docs/Tesis/v10 (IA)/`; no toca `App/`, `n8n/`, `evaluation/`, `openspec/config.yaml`, las cadenas canonicas ni `docs/Tesis/v9 (IA)/`. Gobernanza MEDIA (rec 10 legal) / BAJA (recs 9, 11, 12, 13). Sin mediciones nuevas.

### [C-163] `atender-las-recomendaciones-9-a-13-del-dictamen` — ARCHIVADO (2026-10-29, 32/32)

- **Scope**: rec 9 (hipotesis nula de Wilcoxon sobre diferencias pareadas en 1.4 y 8.1; "cuasiexperimental" en 4.1; separacion de cobertura y exactitud en 8.5; Anexo H con `safety_settings`, ejemplos por clase y clave JSON `categoría`); rec 10 (11-aspectos-legales: disociacion art. 2, plazos art. 14/16, trazabilidad como medida tecnica, RGPD art. 3.2, entrada de la Decision 2003/490/CE); rec 11 (glosario, citacion de figuras 3-5 y 8, regeneracion de las figuras 3/8/9/11, "seudonimizado", lineas fuera de margen y texto encimado, espaciado del indice, rol de los directores); rec 12 (conformidad formal APA 7: coma con "et al.", sentence case, "2.ª ed.", raya corta, ISO/IEC, "(Vol., pp.)", dia legal, Hohpe y Woolf 2004, Mayor-Rocher en espanol, Touvron, Ramya, Efron); rec 13 (fuentes primarias: Shapiro-Wilk, McNemar, metricas multietiqueta, r rank-biserial, ARE de Hodges & Lehmann y regresion isotonica, con Wilcoxon respaldado en 8.1). Commit de apply y archive `ef7f635`.
- **Verificacion**: compilacion Docker `texlive-thesis` con exit 0, 0 errores, 0 referencias indefinidas, 0 `multiply defined`, 0 `??`, biber sin advertencias; `Overfull` = 12 (base 24; las lineas señaladas ya no exceden el margen); 111 -> 112 paginas (delta +1, exceso registrado y honrado); "Referencias bibliograficas" 97 -> 98; `verify_citations.py` PASS (81 entradas, 0 huerfanas, 0 sin uso); `openspec validate "c-163-atender-las-recomendaciones-9-a-13-del-dictamen" --strict`; render regenerado con `build_tesis_para_agente.py v1.2.5`.
- **Item abierto**: OQ-1 = B — fecha de portada DIFERIDA; `00-portada.tex` conserva `\today` y se atendera cuando la fecha de entrega sea firme.
- **Rollback**: `git checkout --` de las fuentes `.tex`, `Bibliography_base.bib`, las figuras regeneradas, `docs/diagrams/despliegue.md`, `docs/diagrams/flujo_n8n.md`, `scripts/figures/*.py`, el render, el ledger y `CHANGES.md`. Sin efecto en runtime ni release.
- **Dependencias**: archivos del dictamen y su ledger (`dictamen-correcciones.md`). No revierte c-158..c-162.
- **Leer antes**: `openspec/changes/archive/2026-10-29-c-163-atender-las-recomendaciones-9-a-13-del-dictamen/{proposal,design,tasks}.md` y la seccion "Dictamen v10 / v1.2.5 (2026-10-28) - c-163" de `docs/Tesis/Correcciones/dictamen-correcciones.md`.

---

## FASE 51 — Residuales de deriva documental del dictamen CONEAU v10/v1.2.5 (2026-10-29)

> Change documental posterior a la FASE 50: cierra los cinco residuales de "deriva fuera de la tesis" registrados por el dictamen CONEAU del 2026-10-28 sobre la tesis v10 / release `v1.2.5` y por la nota "fuera de alcance" del design de c-158, que las FASES 48/49/50 no cubrian. Alinea el spec `telefonia-corpus-medicion`, dos documentos de `docs/`, el comment del modelo `incidente.py`, el Anexo C (tabla del directorio) y el memo de numeros canonicos; no toca `n8n/`, `evaluation/`, `openspec/config.yaml`, las cadenas canonicas ni los valores numericos canonicos. Gobernanza BAJA (reword de comentario + sincronizacion docs/spec).

### [C-164] `sincronizar-los-residuales-de-deriva-documental` — ARCHIVADO (2026-10-29, 18/18)

- **Scope**: (1) delta MODIFIED de `telefonia-corpus-medicion` con la formula c-77 `duracion_segundos + latencia_e2e_ms / 1000` y la descomposicion reconciliada, con los tres escenarios de nombres EXACTOS; (2) `docs/medicion-latencia-e2e.md` con la formula c-77, la cota inferior por el tope de 45 s y el caveat de correo precisado; (3) comentario de `requiere_revision_humana` en `App/Backend/app/models/incidente.py` (solo comentario; el 0.70 aplica solo a Gemini, el deterministico no deriva por su confianza, el fallback siempre deriva, y desde 2026-10-13 tambien deriva con reportante no identificado, c-82/VIS-005); (4) `docs/anexo_c_esquema_bd.md` con la tabla `directorio_empleado` (Fernet + indice ciego c-153, rol de cuatro valores, FK) y `directorio_auditoria`; (5) `docs/Tesis/Correcciones/numeros-canonicos.md` con el hash LF `89cf956e…` como vigente y la nota del CRLF `3fb5bacd…`; (6) cierre en `dictamen-correcciones.md` y FASE 51. Commit de apply y archive `4ed55ee`.
- **Verificacion**: `python3 scripts/preflight/docs_stack_sync.py` = 17/17 PASS; `openspec validate "c-164-sincronizar-los-residuales-de-deriva-documental" --strict --no-interactive` = PASS; `git diff --stat App/Backend/app/models/incidente.py` solo lineas de comentario (sin cambio de logica); `cd App/Backend; python3 -c "import app.models.incidente"` sin error; ningun `.tex` tocado, de modo que NO se recompilo el PDF; `git status --porcelain` lista solo los archivos del scope.
- **Rollback**: `git checkout --` de los archivos tocados (docs, comment del modelo, `CHANGES.md`, el ledger); sin efecto en runtime ni release.
- **Dependencias**: dictamen CONEAU v10/v1.2.5 y su ledger; design archivado de c-158. No revierte c-158..c-163.
- **Leer antes**: `openspec/changes/archive/2026-10-29-c-164-sincronizar-los-residuales-de-deriva-documental/{proposal,design,specs,tasks}.md`, `openspec/specs/telefonia-corpus-medicion/spec.md` y la seccion "Dictamen v10 / v1.2.5 (2026-10-28) - c-164" de `docs/Tesis/Correcciones/dictamen-correcciones.md`.

---

## FASE 52 — Programa de medicion de la campana complementaria (c-165 a c-169) (2026-10-29 / 2026-10-30)

> Programa de cinco changes que produce los instrumentos, los protocolos y los analisis de las mediciones que la auditoria CONEAU sobre la tesis v10 / release `v1.2.5` (dictamen del 2026-10-28, `auditorias/Dictamen_Tesis_v10_v1.2.5_CONEAU_2026-10-28.md`) marco como faltantes y que acotaron los criterios 1 y 4 de la rubrica: exactitud del brazo manual, tasa de intervencion humana real, efecto de orden del diseno pareado, validacion fuera de muestra e intervalo de confianza del kappa. Lo propuso Luca Gomez el 2026-10-29 (commit `dbaf556`) y se enmendo el 2026-10-30 (commit `867fbe6`) segun la revision previa al apply; los cinco pasan `openspec validate --strict` y adoptan los mismos contratos compartidos (planilla unica de etiquetado y validador de c-168, registro de sujetos, export de intervencion de c-165, plan de campana de c-166 y reparto del fuera de muestra entre c-166 y c-167). El repositorio entrega los instrumentos, los protocolos y los scripts; la campana de campo (llamadas, etiquetado humano, operadores reales) corre FUERA del repositorio. Gobernanza por change: c-165 ALTA, c-166 MEDIA, c-167 BAJA/MEDIA, c-168 BAJA y c-169 BAJA.
>
> **Orden de aplicacion (2026-10-30)**: c-168 (aplicado) -> c-166 (en curso) -> c-165 hasta su checkpoint 2.1 (gobernanza ALTA: no se toca modelo, esquema ni migracion sin confirmacion humana explicita) -> c-167 -> campana de campo (fuera del repositorio) -> c-169 al final. El grupo 1 de c-165 requiere c-168 aplicado; sus grupos 2 en adelante no. Las secciones de kappa y de exactitud del brazo manual de c-167 no dependen de la migracion de c-165 ni del plan de c-166 y pueden adelantarse si urge.
>
> **Orden de archive**: c-165 -> c-166 -> c-168 sobre la capability `evaluation-campaign-instrumentation` (sobre ella los tres solo AGREGAN requisitos, sin repetidos ni MODIFIED cruzados: el orden es seguro; tras el primer archive se completa a mano su `## Purpose`, que el CLI deja en "TBD"); despues c-167 y, al final, c-169, que sigue GATEADO hasta que c-165 a c-168 esten archivados y la campana haya corrido y versionado sus salidas.
>
> **Estado al 2026-10-30**: c-168 APLICADO (31/31, commit `1a065cd`) con el archive pendiente; c-166 EN APLICACION; c-165, c-167 y c-169 propuestos y enmendados, con el apply pendiente (0/36, 0/67 y 0/62 tareas). Ninguno esta archivado.
>
> **Leer antes (programa)**: `docs/campana-medicion/plan-campana-de-medicion.md` (plan de la corrida de campo), `docs/campana-medicion/revision-pre-apply-c-165-a-c-169.md` (revision previa al apply y apendice "estado tras las enmiendas") y `knowledge-base/11_evaluacion_experimental.md` (diseno y evaluacion experimental vigentes).

### [C-165] `instrumentar-la-campana-para-medir-el-brazo-manual-y-la-intervencion` — ACTIVO (propuesto y enmendado el 2026-10-30; apply pendiente, 0/36, ALTA)

- **Estado**: propuesto en `dbaf556` (2026-10-29) y enmendado en `867fbe6` (2026-10-30) segun los transversales T1, T2 y T4 y los bloqueantes 1 a 3 de la revision previa al apply; `openspec validate --strict` OK. Apply pendiente (0/36 tareas): se aplica despues de c-168 y c-166 y se detiene en el checkpoint 2.1 hasta la confirmacion humana. Su tarea 6.6 (registro en este indice) queda cubierta por esta entrada.
- **Scope**: instrumenta la medicion del BRAZO MANUAL y de la TASA DE INTERVENCION HUMANA, que el repositorio no podia producir. (1) Brazo manual: el operador registra su clasificacion por caso en la planilla unica `evaluation/data/plantilla_etiquetado.csv` de c-168 (`tarea = brazo_manual`, operadores fijos `O1` y `O2`, `inicio` y `timestamp` obligatorios), validada con `evaluation/doble_etiquetado.py::validar_doble_etiquetado` sin esquema propio, mas `evaluation/brazo_manual.py` (posicion real reconstruida desde `inicio` y desvios respecto del plan de campana de c-166); los operadores son personas distintas de los etiquetadores `E*` de c-168, de los dos analistas del consenso original y de los autores. (2) Intervencion humana: migracion Alembic `024` sobre `clasificacion_log` con `validado_por_empleado_id` (FK nombrada a `directorio_empleado.id`, nullable), `intervencion_inicio_en`, `validado_en` y `origen_intervencion` (`gate | muestreo | rederivacion | completado_manual`), con el origen derivado por el backend (`PATCH /clasificaciones/{log_id}/validar` y, para `rederivacion`, `PATCH /incidentes/{id}`; `completado_manual` queda reservado y sin escritor), e `intervencion_inicio_en` opcional en el payload y en `ValidarClasificacionDialog.tsx`. (3) Metrica backend `tasa_intervencion_backend` en `ResumenResponse` (distinta de la `tasa_intervencion_humana` offline de c-167), export pseudonimizado `App/Backend/scripts/exportar_intervenciones.py` hacia `evaluation/data/campana/intervenciones.csv` y runbook `docs/campana-medicion/runbook-brazo-manual-e-intervencion.md`. Capabilities: `evaluation-campaign-instrumentation` (nueva; ECM-001..ECM-003) y `sector-assignment` (ASG-005 MODIFIED).
- **Dependencias**: c-168 (esquema de la planilla y validador `validar_doble_etiquetado`): se aplica ANTES del grupo 1 de c-165; el grupo 2 en adelante no depende de c-168. Comparte la capability `evaluation-campaign-instrumentation` con c-166 y c-168 (orden de archive c-165 -> c-166 -> c-168). Usa el plan `plan_campana.csv` y los sidecars por corrida de c-166 para vincular `incidente_id` con `id_caso`; lo consume c-167 (`intervenciones.csv`, planilla del brazo manual y `registro_sujetos.csv`). El corpus `data/corpus_evaluacion_pseudonimizado.json` se usa solo en lectura.
- **Governance**: ALTA (esquema de auditoria `clasificacion_log`). CHECKPOINT 2.1 de su `tasks.md`: antes de cualquier tarea que toque modelo, esquema o migracion se presentan al autor las cuatro columnas, la migracion `024`, el ajuste de `tests/test_migration_023_directorio_auditoria.py` (head `023` -> `024`) y el escritor de `rederivacion`, y NO se avanza sin confirmacion humana explicita.
- **Leer antes**: `openspec/changes/c-165-instrumentar-la-campana-para-medir-el-brazo-manual-y-la-intervencion/{proposal,design,tasks}.md` (delta specs en `specs/evaluation-campaign-instrumentation/` y `specs/sector-assignment/`), `openspec/specs/sector-assignment/spec.md` (ASG-005), `docs/campana-medicion/revision-pre-apply-c-165-a-c-169.md` (seccion c-165 y transversales T1, T2 y T4), `docs/anexo_c_esquema_bd.md` y `knowledge-base/11_evaluacion_experimental.md`.

### [C-166] `contrabalanceo-del-diseno-y-corpus-independiente` — EN APLICACION (2026-10-30, 47 tareas, MEDIA)

- **Estado**: propuesto en `dbaf556` (2026-10-29) y enmendado en `867fbe6` (2026-10-30) segun el transversal T3 y los bloqueantes de la revision previa al apply; `openspec validate --strict` OK. Apply EN CURSO desde el 2026-10-30 (47 tareas; el avance se lleva en su `tasks.md`). Archive pendiente: va segundo en el orden de la capability, despues de c-165.
- **Scope**: contrabalanceo del diseno pareado y corpus independiente para la validacion fuera de muestra. (1) Plan de campana por caso (contrabalanceo de CONDICION, es decir que brazo va primero; reordenar el envio del brazo automatizado no produce efecto de orden): `evaluation/plan_campana.py` con `ordenar_casos` (modos `directo|inverso|alternado|aleatorio`) y `generar_plan_campana` (`id_caso, posicion, mitad, brazo_primero, modo, seed`), exportado a `evaluation/data/campana/plan_campana.csv`. (2) Harnesses: `scripts/corpus_ingest/ingest_via_n8n.py` e `ingest_corpus.py` aceptan `--plan` y `--orden/--seed`, registran `orden`, `posicion`, `mitad`, `brazo_primero` e `id_corrida` por caso (campos aditivos con default `None`) y abortan antes de enviar nada si `--json` o `--sidecar` apuntan a archivos versionados; `ingest_telefonia_corpus.py` no ingesta y solo copia el plan a su sidecar. (3) Corpus independiente: `evaluation/no_solape.py::verificar_no_solape` (prefijo `I`, ids disjuntos, SHA-256 de la descripcion normalizada, advertencia opcional por similitud) y flags `--corpus`, `--predicciones` y `--reporte` en `evaluation/run_evaluation.py`, con proteccion de `evaluation/predicciones.json` y `evaluation/report.md`. (4) Runbooks `docs/campana-medicion/runbook-campana-contrabalanceada.md` y `docs/campana-medicion/runbook-corpus-independiente.md`, y el job `corpus-ingest-tests` en `.github/workflows/ci.yml` (las suites de `scripts/corpus_ingest/` hoy corren fuera del gate). Capability `evaluation-campaign-instrumentation` (ECM-004..ECM-007); sin capabilities modificadas.
- **Dependencias**: c-168 (plantilla `evaluation/data/plantilla_etiquetado.csv` y validador `validar_doble_etiquetado`): el runbook del corpus independiente los usa (ECM-006) y el runbook contrabalanceado los referencia para `tarea = brazo_manual`. Comparte la capability con c-165 y c-168, sin depender de la migracion de c-165 ni de su checkpoint de gobernanza ALTA. Lo consumen c-165 (plan y sidecars por corrida para vincular `incidente_id` con `id_caso`) y c-167 (plan, sidecars y `evaluation/data/campana/predicciones_independiente.json` para el efecto de orden y el fuera de muestra; `evaluar_fuera_de_muestra` y el reporte in-sample / out-of-sample son de c-167). c-169 documenta los resultados.
- **Governance**: MEDIA (codigo de evaluacion, harnesses de ingesta y CI; sin migracion ni cambios de contrato de las capabilities existentes). Los archivos congelados (`data/corpus_evaluacion_pseudonimizado.json`, `data/corpus_resultados*.json`, `evaluation/predicciones.json`, `evaluation/report.md` y los sidecars versionados) no se modifican en ningun camino.
- **Leer antes**: `openspec/changes/c-166-contrabalanceo-del-diseno-y-corpus-independiente/{proposal,design,tasks}.md` (delta spec en `specs/evaluation-campaign-instrumentation/`), `docs/campana-medicion/revision-pre-apply-c-165-a-c-169.md` (seccion c-166 y transversal T3), `docs/campana-medicion/plan-campana-de-medicion.md` y `knowledge-base/11_evaluacion_experimental.md` (seccion "Diseno": contrabalanceo por mitades).

### [C-167] `analisis-de-la-nueva-campana-y-de-la-fiabilidad-entre-etiquetadores` — ACTIVO (propuesto y enmendado el 2026-10-30; apply pendiente, 0/67, BAJA/MEDIA)

- **Estado**: propuesto en `dbaf556` (2026-10-29) y enmendado en `867fbe6` (2026-10-30) segun los transversales T1 a T4 de la revision previa al apply; `openspec validate --strict` OK. Apply pendiente (0/67 tareas), despues de c-165, c-166 y c-168. Sin datos de campo al implementar: los tests usan fixtures sinteticos y cada seccion cuyo dataset falte se declara "no se obtuvo" con el motivo, sin abortar el resto.
- **Scope**: analisis offline, determinista y de solo lectura de los datasets de la campana y de la fiabilidad entre etiquetadores. (1) Kappa de Cohen (`evaluation/kappa.py`): no ponderado, 5 clases (`SECTORES_CANONICOS`), sobre la etiqueta primaria y exactamente dos etiquetadores fijos (`E1`, `E2`), con IC asintotico (varianza bajo H1 de Fleiss, Cohen y Everitt, 1969), IC bootstrap por casos, p_o, p_e, PABAK, n y rotulo de Landis y Koch; es el kappa de los etiquetadores NUEVOS y NO un intervalo del `0,87` original. (2) `evaluation/campana.py`: exactitud estricta y laxa del brazo manual por operador (Wilson) y agregada (bootstrap por caso) contra el consenso del doble etiquetado nuevo, contraste manual vs automatizado con McNemar, `registro_sujetos` que rechaza personas con mas de un rol, tasa de intervencion humana de campana (`tasa_intervencion_humana`: proporcion de casos con IC de Wilson contrastado contra la cota 0,15 de la segunda sub-hipotesis y proporcion del tiempo con bootstrap por caso del cociente), efecto de orden de condicion y de posicion con su efecto minimo detectable, y `evaluar_fuera_de_muestra` (clasificador congelado, bloques in-sample y out-of-sample rotulados). (3) CLI `evaluation/analisis_campana.py` con salidas en `evaluation/data/campana/analisis/` y fixtures en `evaluation/tests/fixtures/campana/`. Unico cambio a codigo existente: `_percentil_intervalo` y `_remuestreos_indices` de `evaluation/metrics.py` pasan a publicos, sin cambio de comportamiento. Capability `evaluation-framework` (6 requisitos ADDED, ninguno modificado).
- **Dependencias**: c-168 (esquema de la planilla y validador), c-165 (export `evaluation/data/campana/intervenciones.csv` y `evaluation/brazo_manual.py`) y c-166 (`plan_campana.csv`, `predicciones_independiente.json` y `verificar_no_solape`), que consume como contratos de datos. Sus secciones de kappa y de exactitud del brazo manual no dependen de la migracion de c-165 ni del plan de c-166 y pueden adelantarse si urge. Sus salidas las consume c-169.
- **Governance**: BAJA/MEDIA (biblioteca pura sin migraciones ni dependencias nuevas; `scipy` ya figura en `evaluation/requirements.txt`). No toca `evaluation/report.md`, `evaluation/predicciones.json` ni los numeros canonicos de v9.
- **Leer antes**: `openspec/changes/c-167-analisis-de-la-nueva-campana-y-de-la-fiabilidad-entre-etiquetadores/{proposal,design,tasks}.md` (delta spec en `specs/evaluation-framework/`), `docs/campana-medicion/revision-pre-apply-c-165-a-c-169.md` (seccion c-167 y transversales T1 a T4), `evaluation/metrics.py`, `evaluation/stats.py` y `knowledge-base/11_evaluacion_experimental.md`.

### [C-168] `plantilla-y-protocolo-de-doble-etiquetado` — APLICADO (2026-10-30, 31/31, BAJA; archive pendiente)

- **Estado**: propuesto en `dbaf556` (2026-10-29), enmendado en `867fbe6` y APLICADO el 2026-10-30 (31/31 tareas, commit `1a065cd`, `feat(c-168): plantilla y validador del doble etiquetado`). Archive PENDIENTE: por el orden de la capability se archiva despues de c-165 y c-166. La tabla primaria `evaluation/data/campana/doble_etiquetado.csv` y `registro_sujetos.csv` no existen aun: se agregan DESPUES de la campana siguiendo el runbook, con su SHA-256 en `evaluation/data/campana/README.md`.
- **Scope**: fija el esquema UNICO de la planilla de etiquetado y el validador UNICO del doble etiquetado independiente (transversal T1 de la revision: c-165, c-167 y c-168 tenian tres esquemas distintos para la misma planilla). Plantilla `evaluation/data/plantilla_etiquetado.csv` (`id_caso, id_etiquetador, tarea, sector_etiquetado, sectores_adicionales_etiquetados, inicio, timestamp`; `sector_asignado` queda reservado al consenso del corpus, lo que desambigua el cegado), validador puro `evaluation/doble_etiquetado.py::validar_doble_etiquetado` con CLI y exit codes por tipo de ofensa (importa `SECTORES_CANONICOS` de `evaluation/corpus.py`, sin duplicar cadenas), protocolo `docs/campana-medicion/runbook-doble-etiquetado.md` (sujetos y exclusiones, cegado, codebook, tamano, discordancias, limitacion declarada si no se consiguen etiquetadores nuevos y recuperacion manual de una tabla parcial), `evaluation/data/campana/README.md` (versionado de la tabla primaria con SHA-256), fixture sintetico y `.gitattributes` con LF para los CSV de la campana. Capability `evaluation-campaign-instrumentation` (ECM-008..ECM-010).
- **Dependencias**: es el DUENO del esquema y del validador que adoptan c-165 (`tarea = brazo_manual`), c-166 (corpus independiente, `id_caso` con prefijo `I`) y c-167 (kappa y exactitud del brazo manual); ninguno define esquema o validador propios. Depende de `evaluation/corpus.py` (`SECTORES_CANONICOS`, `cargar_corpus`) y del corpus pseudonimizado en solo lectura. c-169 reporta el estado del cegado (cumplido o limitacion declarada).
- **Governance**: BAJA (validador puro, plantilla y runbook; sin migracion, sin datos de campo en el repositorio y sin cambios a las cadenas canonicas de sector, al corpus ni a los numeros canonicos).
- **Leer antes**: `openspec/changes/c-168-plantilla-y-protocolo-de-doble-etiquetado/{proposal,design,tasks}.md` (delta spec en `specs/evaluation-campaign-instrumentation/`), `docs/campana-medicion/runbook-doble-etiquetado.md`, `evaluation/data/campana/README.md`, `docs/campana-medicion/revision-pre-apply-c-165-a-c-169.md` (transversales T1 y T2 y seccion c-168), `docs/Tesis/Correcciones/numeros-canonicos.md` (kappa `0,87` sin IC) y `knowledge-base/11_evaluacion_experimental.md`.

### [C-169] `incorporar-los-resultados-de-la-campana-a-la-tesis` — ACTIVO (propuesto y enmendado el 2026-10-30; GATEADO, 0/62, BAJA)

- **Estado**: propuesto en `dbaf556` (2026-10-29) y enmendado en `867fbe6` (2026-10-30) segun la seccion c-169 y los transversales T1 a T4 de la revision previa al apply; `openspec validate --strict` OK. GATEADO (0/62 tareas): no se aplica hasta cumplir el gate mecanico de la tarea 0 de su `tasks.md`. Al archivar se registra su cierre en este indice (tarea 8.10).
- **Scope**: solo documentacion (docs-only) sobre `docs/Tesis/v10 (IA)/`: incorpora los resultados de la campana con desenlace positivo o negativo declarado para cada item (exactitud del brazo manual, intervencion humana real, efecto de orden, validacion fuera de muestra e IC del kappa). Toca el marco metodologico (4.2 a 4.8), la introduccion, el resumen y el abstract (tope de 250 palabras), los resultados (subseccion nueva `subsec:resultados-campana-medicion`), la discusion, las conclusiones, las recomendaciones, los aspectos legales, los Anexos A, B e I, la bibliografia, el memo `docs/Tesis/Correcciones/numeros-canonicos.md` (seccion 3.N nueva) y `docs/Tesis/Correcciones/dictamen-correcciones.md`, mas el PDF, los renders y la release. Decision D-kappa: el `0,87` se conserva como valor historico sin IC y el kappa nuevo se reporta como un valor distinto. Capabilities: `tesis-document` (19 requisitos MODIFIED, 2 de ellos renombrados, 1 REMOVED y 6 ADDED) y `tesis-numeros-canonicos` (2 MODIFIED y 2 ADDED).
- **Dependencias**: GATEADO hasta que c-165, c-166, c-167 y c-168 esten archivados y fuera de `openspec list` y la campana de campo haya corrido y dejado sus salidas versionadas en `evaluation/data/campana/` (tablas, `analisis/` y `registro_sujetos.csv`, con README y SHA-256); sin solapes de sujetos (con solape, ramas negativas declaradas). Si el gate 0.1 o el 0.2 falla, el change se detiene; el corpus independiente es opcional. Consume los contratos de c-168 (planilla, sujetos y tabla primaria), c-165 (export de intervencion), c-166 (plan y predicciones del corpus independiente) y las salidas de c-167.
- **Governance**: BAJA (docs-only). Sin cambios en `App/`, `n8n/`, `evaluation/` (solo lectura de las salidas de c-167), `openspec/config.yaml`, las cadenas canonicas ni `docs/Tesis/v9 (IA)/`; los valores canonicos vigentes no cambian.
- **Leer antes**: `openspec/changes/c-169-incorporar-los-resultados-de-la-campana-a-la-tesis/{proposal,design,tasks}.md` (delta specs en `specs/tesis-document/` y `specs/tesis-numeros-canonicos/`), `docs/campana-medicion/revision-pre-apply-c-165-a-c-169.md` (seccion c-169), `auditorias/Dictamen_Tesis_v10_v1.2.5_CONEAU_2026-10-28.md`, `docs/Tesis/Correcciones/numeros-canonicos.md` y `docs/Tesis/Correcciones/dictamen-correcciones.md`.

---

## Notas del analisis

### Estado actual del proyecto (verificado contra el codigo; actualizado 2026-10-22)

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

Actualizacion 2026-10-20 (recompilacion de la tesis v9 + archivado de 9 changes): la tesis v9 se recompilo con MiKTeX (xelatex -> biber -> xelatex -> xelatex; 103 paginas, 0 errores fatales, 0 referencias indefinidas, 48/48 bibliografia) y se marcaron las 12 tareas de recompilacion repartidas en los 10 changes de tesis, cubriendo la recompilacion que estaba diferida. Con eso se ARCHIVARON nueve changes el 2026-10-20: C-76 (49/49), C-77 (51/51), C-78 (25/25), C-79 (25/25), C-92 (29/29), C-93 (29/29), C-94 (25/25), C-95 (36/36) y C-96 (28/28), bajo `openspec/changes/archive/2026-10-20-*`. Las especificaciones principales se sincronizaron con los delta specs de esos nueve changes (`openspec validate --specs` = 62/62). Queda UN solo change ACTIVO: C-80 `tesis-forma-evidencia-visual` (41/45), con las capturas de UI (6.5/6.6), la verificacion de las 8 figuras (8.2), el cierre de 6.4 por contingencia y el ajuste de 6.9 pendientes. Totales: 94 entradas creadas documentadas (93 numeradas + 1 de mantenimiento sin numero) — 93 archivadas y 1 activa (C-80).

Actualizacion 2026-10-22 (cierre del roadmap — 0 changes activos): se archivo el ultimo change ACTIVO, C-80 `tesis-forma-evidencia-visual` (2026-10-21, 45/45; se incorporaron las capturas de UI y la verificacion de las 8 figuras). Se registran ademas en este indice los changes que faltaban: la FASE 33 (C-98 `limpiar-basic-auth-n8n-vestigial`, C-99 `cablear-wilcoxon-al-reporte`, C-100 `test-umbral-settings-hermetico` y C-101 `alinear-tiempos-tesis-document`, archivados 2026-10-20), la FASE 34 (C-102..C-119, correcciones finales de la tesis por el dictamen CONEAU, archivados 2026-10-21) y la FASE 35 (C-120 `observaciones-finales-dictamen`, archivado 2026-10-22, 15/15). La tesis quedo cerrada con las 7 recomendaciones del dictamen CONEAU 2026-10-21 resueltas; el PDF se mantiene en 101 paginas. El tag anotado `v1.0.1` (`bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0`) identifica la version corregida; el tag `v1.0.0` (`61a6b117dd1321fbee25f9792d9f29b884e5ac8d`) queda como la version evaluada previa. `openspec list` no reporta changes activos.

Actualizacion 2026-10-22 (migracion de la tesis a v10): se creo la version de trabajo `docs/Tesis/v10 (IA)/` como espejo completo de la version publicada v9 (61 archivos en el arbol de trabajo, 60 versionados) y se repuntaron los punteros activos del proyecto a v10: el campo `thesis:` de `openspec/config.yaml` (`docs/Tesis/v10 (IA)/tesis_completa_extraida.txt`), las rutas activas de `openspec/specs/tesis-document/spec.md` (5 ocurrencias) y las rutas de trabajo del change dependiente c-121. La version publicada v9 queda CONGELADA (tag anotado `v1.0.1`, `bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0`) y NO se modifica; `docs/Tesis/v10 (IA)/` es la version de trabajo vigente. Las entradas historicas de este indice y los demas registros historicos conservan sus referencias a la version publicada v9 sin reescritura (regla puntero activo vs registro historico). El change de migracion es `c-122-migrar-tesis-a-v10` (prerequisito); el proximo change de contenido es `c-121-observaciones-dictamen-v1-0-1`, que aplica las recomendaciones editoriales residuales del dictamen CONEAU v1.0.1 SOBRE v10. El tag de release de la nueva version (`v1.1.0`) queda para el cierre de c-121.

Actualizacion 2026-10-22 (FASE 36 — correcciones del dictamen CONEAU v10): se registraron como ARCHIVADOS los cuatro changes posteriores a C-120 agrupados en la FASE 35 ampliada, todos del 2026-10-22: C-121 `observaciones-dictamen-v1-0-1` (14/14; cierra las tres observaciones residuales del dictamen v1.0.1; release v1.1.0), C-122 `migrar-tesis-a-v10` (12/12; version de trabajo `docs/Tesis/v10 (IA)/`), C-123 `url-repositorio-y-version-tesis` (6/12 casillas marcadas al archivar; URL del repositorio en el Anexo B y release v1.1.1) y C-124 `test-pg-independiente-de-gemini` (11/11; aisla el test PostgreSQL del clasificador real). Se registraron tambien, en la FASE 35 bis, los cinco changes de infraestructura y dependencias de Luca traidos por el merge de `main`, todos creados el 2026-10-22: ARCHIVADOS C-125 `delta-local-bootstrap-spec` (0/8 casillas marcadas al archivar), C-126 `gap-preflights-cost-gemini` (0/10 casillas marcadas al archivar), C-127 `migracion-dependencias-backend` (22/22) y C-129 `dependabot-sin-majors` (0/5 casillas marcadas al archivar), y APLICADO C-128 `migracion-react-19-frontend` (22/22, alcance reducido). Se registraron ademas como CREADOS y ACTIVOS los trece changes de la nueva FASE 36, C-130..C-142, derivados del dictamen CONEAU `auditorias/Dictamen_Tesis_v10_v1.1.0_CONEAU_2026-10-22.md` (veredicto "APROBADO CON OBSERVACIONES"; calificacion sugerida del documento escrito 8, nivel "Muy bueno", 7,67 ponderado sobre la rubrica de la catedra): C-130 `gate-revision-humana-por-etapa` (0/36), C-131 `metricas-por-etapa-canal-y-exactitud-laxa` (0/81, con el contraste de McNemar entre etapas), C-132 `balance-neto-derivaciones-erroneas` (0/29), C-133 `hipotesis-objetivos-metrica-primaria` (0/42), C-134 `contrastes-estadisticos-y-desagregado-canal` (0/47), C-135 `cronologia-y-consistencia-redaccional` (0/34), C-136 `recomendaciones-lineas-faltantes` (0/24), C-137 `revision-ortotipografica` (0/41), C-138 `estado-del-arte-calibracion-y-cascadas` (0/30), C-139 `correspondencia-texto-fuente-y-metadatos` (0/46), C-140 `endurecimiento-tecnico-tls-reintentos-e2e` (0/73; OPCIONAL), C-141 `integracion-release-v1-2-0` (0/52) y C-142 `sensibilidad-fuera-de-muestra-ajustes-clasificador` (0/91; mitad analitica de la recomendacion A5, agregada despues de los doce primeros y creada el 2026-10-23). Estos trece se crearon con los numeros c-125..c-137 y se renumeraron el 2026-10-23 a c-130..c-142 por colision con los changes c-125..c-129 de `main`; los commits y el PR #40 anteriores a esa fecha citan la numeracion vieja. En total son 13 activos: los 13 de la FASE 36 con 0/626 tareas aplicadas; C-143 `publicar-predicciones-como-evidencia-de-evaluacion` quedo ARCHIVADO en `main` el 2026-10-23 (13/13, FASE 37) y C-144 `declarar-procedencia-real-y-ausencia-de-preproduccion` quedo ARCHIVADO el 2026-10-23 (18/18, FASE 38); en conjunto, 0/626 tareas activas, sumas verificadas con `grep -c "^- \[ \]"` sobre cada `tasks.md` y con `openspec list --json`; la fase propose esta completa en los trece y `openspec validate --strict` los da por validos. Quedan superadas las frases "No hay changes activos" y "La numeracion va de C-01 a C-120" de las actualizaciones previas (instantaneas historicas, sin reescribir; el estado actual esta en "Primer change recomendado" y en las lineas Total y Fases): la numeracion va de C-01 a C-144 (C-21, C-49 y C-50 nunca se crearon; `c-51` fue absorbido por C-52 y no se abre; c-63 se cuenta como un change con sus tres partes c-63a/b/c). Totales: 141 entradas creadas documentadas (140 numeradas + 1 de mantenimiento sin numero), 128 archivadas y 13 activas (C-130..C-142); `openspec/changes/archive/` contiene 130 directorios (las 128 entradas mas las dos partes adicionales de c-63; la linea Total previa citaba 118, que quedo 1 por debajo del recuento real de ese momento, 119). La release vigente de la tesis es `v1.1.1` (tag anotado sobre `4160d84286623b073d2904353e6f9163ae211de7`, 2026-10-22), que reemplaza a `v1.1.0` (`7103b649d8c4f51737ad6ad4095dad22c9406400`); la release prevista al cierre de la FASE 36 es `v1.2.0` (change C-141; el nombre queda sujeto a confirmacion). El orden de aplicacion definitivo (con C-142 intercalado tras C-131) y las decisiones pendientes del usuario estan en la FASE 36.

Actualizacion 2026-10-26 (release v1.2.0 de la FASE 36): C-141 `integracion-release-v1-2-0` integro la familia y publico la release `v1.2.0` (tag anotado sobre el commit `a49d035c67b32ae17e633ec04b09ecdd2781aac6`, publicado en `origin` el 2026-10-26; PDF de 109 paginas: cuerpo sin anexos 100 y anexos 9). Regla del tope de paginas (decision del equipo del 2026-10-26): el cuerpo sin anexos no supera las 100 paginas y los anexos no tienen limite; se cumplio con margen 0 y una unica palanca de formato (P7, tipografia de la lista de referencias) sin recortes de contenido. Se registraron como ARCHIVADOS el 2026-10-26 C-130 `gate-revision-humana-por-etapa` (37/37), C-131 `metricas-por-etapa-canal-y-exactitud-laxa` (81/81), C-132 `balance-neto-derivaciones-erroneas` (29/29), C-133 `hipotesis-objetivos-metrica-primaria` (42/42), C-134 `contrastes-estadisticos-y-desagregado-canal` (47/47), C-136 `recomendaciones-lineas-faltantes` (24/24), C-137 `revision-ortotipografica` (41/41), C-138 `estado-del-arte-calibracion-y-cascadas` (30/30), C-139 `correspondencia-texto-fuente-y-metadatos` (46/46) y C-142 `sensibilidad-fuera-de-muestra-ajustes-clasificador` (91/91), y C-141 quedo APLICADO. Siguen ACTIVOS C-135 `cronologia-y-consistencia-redaccional` (34/35; la tarea 5.2 espera las fechas de las iteraciones de los autores) y C-140 `endurecimiento-tecnico-tls-reintentos-e2e` (0/73; excluido provisionalmente de la integracion, sin prueba de humo; decision del usuario pendiente: incluirlo o archivarlo como NO REALIZADO). El PR #40 `ramagonzalo` -> `main` (abierto el 2026-10-22 con la numeracion anterior) debe integrarse con merge commit, nunca squash ni rebase, y despues verificarse con `git merge-base --is-ancestor v1.2.0 origin/main`. Quedan superadas las lineas de estado de la actualizacion anterior (13 activos, 0/626 tareas): el estado actual esta en las lineas Total y Fases y en "Primer change recomendado". La release vigente de la tesis pasa a ser `v1.2.0`; `v1.1.1` (`4160d84286623b073d2904353e6f9163ae211de7`) y las anteriores quedan como versiones previas.

Actualizacion 2026-10-26 (release v1.2.1 de la FASE 39): C-145 `correccion-factual-sincronizacion-del-memo-y-portabilidad-del-harness` quedo APLICADO (77/77 marcadas de 77 tareas) y publico la release `v1.2.1` —tag anotado sobre el commit C3 `509ffff105c21fed0c07cbf9a46245ba6c53e0e1`; el commit C4 `fc579d8fae8984718c0a398e31977c6eb01903af` consigna el hash de C3 en el Anexo B y en el REGISTRO—, fusionada a `main` con merge commit `13e9281e3f41ec990584e0c6b62e7034c13e422f` (PR #43, 2026-10-26); `git merge-base --is-ancestor v1.2.1 origin/main` = verdadero y `v1.2.0` sigue siendo ancestro. El PDF quedo en **109** paginas (cuerpo sin anexos **100** y anexos **9**). La **causa raiz de A1** (la oracion "16 tests ... `pytest.skip`"): nacio en `a0436e0` (C-19, 2026-07-03, 16 pruebas con omision), `ef656ac` (2026-09-17) cambio `conftest.py` a fallo ruidoso y la dejo obsoleta, y las copias de trabajo `8466cbe` (2026-10-01, v9) y `7408543` (c-122, 2026-10-22, v10) la arrastraron sin actualizarla. Estado actual: c-135 `cronologia-y-consistencia-redaccional` **35/35** (la tarea 5.2 se cerro como no reconstruible con fuente primaria); c-140 `endurecimiento-tecnico-tls-reintentos-e2e` **0/73** (excluido provisionalmente de la integracion; decision del usuario pendiente: incluirlo o archivarlo como NO REALIZADO); c-141 `integracion-release-v1-2-0` **51/52**; c-145 COMPLETO (77/77 marcadas de 77 tareas) a la espera del archive; c-143 (FASE 37) y c-144 (FASE 38) ARCHIVADOS el 2026-10-23 (13/13 y 18/18). Quedan superadas las lineas de estado de la actualizacion anterior, cuando la release vigente era `v1.2.0`: el estado actual esta en la FASE 39 y en el REGISTRO; la release vigente de la tesis pasa a ser `v1.2.1`.

Actualizacion 2026-10-27 (release v1.2.2 de la FASE 40): C-147 `compactacion-y-release-v1-2-2` integro los changes ya aplicados C-146 `completar-metricas-trabajos-previos` y C-140 `endurecimiento-tecnico-tls-reintentos-e2e` y publico la release `v1.2.2` —tag anotado sobre C1 `445a47b4f6fccca3d4611ee3cb7adea4e7350dcc`; C2 `8e97d99` consigna el hash de C1 en el Anexo B y `aac73d8` lo registra—, fusionada a `main` con merge commit `07cc075` (PR #48, 2026-10-27); `git merge-base --is-ancestor v1.2.2 origin/main` = verdadero y `v1.2.1` sigue siendo ancestro. El PDF quedo en **104** paginas totales (cuerpo 96, anexos 8). La compactacion (commit `8c0cf6d`) bajo el documento de 111 a 104 con palancas de forma (indices y listas de tablas/figuras compactados y fusionados, anexos en `\small`, figuras de la seccion 6.8 al 70 % de ancho y espaciado de la bibliografia), sin remover contenido cientifico ni dejar referencias colgadas. **El tope de paginas real quedo reconciliado**: metrica = total del PDF, valor = 100, fuente = **exigencia de la catedra**, con el exceso **+4** honrado y defendido (G0.1 del 2026-10-27); la regla previa ("cuerpo sin anexos <= 100, decision del equipo, no consta exigencia de la catedra") queda superada. C-140 se cerro **73/73**. Se archivaron C-146, C-140, C-141 y C-147 el 2026-10-27 (`openspec/changes/archive/2026-10-27-*`); `openspec list` no reporta changes activos y la familia del dictamen CONEAU v10/v1.1.1 queda integrada. La release vigente de la tesis pasa a ser `v1.2.2` (`v1.2.1`, `v1.2.0`, `v1.1.1`, `v1.1.0`, `v1.0.1` y `v1.0.0` quedan como versiones previas inmutables).

Actualizacion 2026-10-27 (release v1.2.2 de la FASE 40 y cierre de la familia): C-147 `compactacion-y-release-v1-2-2` (23/23) integro C-146 `completar-metricas-trabajos-previos` (22/23; la 6.1 sigue bloqueada por acceso institucional externo al texto de Paramesh y Shreedhara 2019) y C-140 `endurecimiento-tecnico-tls-reintentos-e2e` (73/73; TLS verificado, reintentos acotados de N8N y smoke E2E, aplicado por Luca el 2026-10-26), compacto la tesis de 111 a 104 paginas totales (cuerpo 96, anexos 8) con palancas de forma y sin quitar contenido (commit `8c0cf6d`), y publico la release `v1.2.2` —tag anotado sobre el commit C1 `445a47b4f6fccca3d4611ee3cb7adea4e7350dcc`; C2 `8e97d99` consigna el hash en el Anexo B y `aac73d8` en el REGISTRO—, fusionada a `main` con merge commit `07cc075` (PR #48); `git merge-base --is-ancestor v1.2.2 origin/main` = verdadero y `v1.0.0` a `v1.2.1` siguen inmutables. La regla del tope de paginas se reconcilio con la catedra: metrica = total del PDF, valor = 100, fuente = exigencia de la catedra, con el exceso de +4 paginas honrado y defendido por los autores (supera la regla provisoria del 2026-10-26, cuerpo sin anexos <= 100). Se archivaron el 2026-10-27 C-146, C-140, C-141 (52/52, con la tarea 2.9 cerrada) y C-147, sincronizando los specs `tesis-document`, `ci-pipeline`, `classification-resilience`, `dry-run-harness`, `incident-origin-correlation`, `n8n-workflow`, `tls-docker-compose`, `project-documentation` y `tesis-numeros-canonicos`; C-135 y C-145 ya estaban archivados desde el 2026-10-26. Estado actual: 0 changes activos; `openspec validate --specs --strict --no-interactive` pasa; release vigente `v1.2.2`; quedan superadas las lineas de estado de la actualizacion anterior. Pendientes residuales: la tarea 6.1 de C-146 (acceso institucional) y las decisiones PROVISIONALES de los autores aun sin confirmar.

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

Los changes C-46, C-47 y C-48 quedaron implementados, verificados y archivados (2026-09-22). Desde entonces tambien se archivaron C-52 (2026-09-30), C-53 (2026-10-01), C-54 (2026-10-01, 51/51), C-55 (2026-09-29), C-57 (2026-09-29), C-58 (2026-09-29), C-59 (2026-10-01), C-61 (2026-10-01, 26/26), C-69 (2026-10-05, 30/30), C-71 (2026-10-06, 43/43), C-60 (2026-10-06, 33/33), C-70 (2026-10-06, 72/72), C-72 (2026-10-07, 37/37), C-73 (2026-10-07, 23/23), C-74 (2026-10-07, 32/32), C-75 (2026-10-08, 14/14), C-56 (2026-10-08, 27/27), C-68 (2026-10-09, 63/63), C-81 (2026-10-13, 24/24), C-82 (2026-10-13, 36/36), C-83 (2026-10-13, 18/18), C-84 (2026-10-15, 15/15), C-85 (2026-10-15, 34/34), C-86 (2026-10-15, 61/61), C-87 (2026-10-15, 25/25), C-88 (2026-10-15, 19/19), C-89 (2026-10-15, 19/19), C-90 (2026-10-15, 17/17) y C-91 (2026-10-15, 48/48); C-97 `actualizar-dependencias-seguridad` (2026-10-19, 14/14, post-roadmap, seguimiento de C-64); y los nueve changes de tesis C-76 (2026-10-20, 49/49), C-77 (2026-10-20, 51/51), C-78 (2026-10-20, 25/25), C-79 (2026-10-20, 25/25), C-92 (2026-10-20, 29/29), C-93 (2026-10-20, 29/29), C-94 (2026-10-20, 25/25), C-95 (2026-10-20, 36/36) y C-96 (2026-10-20, 28/28).

Los changes activos son c-165, c-166, c-167, c-168 y c-169 (FASE 52, programa de medicion: c-168 APLICADO con el archive pendiente, c-166 en aplicacion, c-165 y c-167 con el apply pendiente y c-169 GATEADO); c-161 y c-162 (FASE 49), c-163 (FASE 50) y c-164 (FASE 51) quedaron ARCHIVADOS el 2026-10-29, igual que c-158, c-159 y c-160 (FASE 48); C-155, C-156 y C-157 (FASE 47) estan ARCHIVADOS desde el 2026-10-28; la FASE 36 (C-130..C-142), C-143 (FASE 37), C-144 (FASE 38), C-145 (FASE 39), C-146 y C-147 (FASE 40), C-148 (FASE 41), C-149 (FASE 42), C-150 (FASE 43), C-151 (FASE 44), C-153 (FASE 45) y C-152 y C-154 (FASE 46) estan ARCHIVADOS. C-135 (35/35 marcadas, 5.2 justificada), C-130..C-134, C-136..C-139, C-142 y C-145 se archivaron el 2026-10-26; C-140 (73/73), C-141 (52/52), C-146 (22/23, 6.1 bloqueada por acceso externo) y C-147 (23/23) el 2026-10-27. C-150 (26/28) se archivo el 2026-10-27; C-151 (20/20), C-152 (12/12), C-153 (42/42) y C-154 (21/21) el 2026-10-28. C-143 `publicar-predicciones-como-evidencia-de-evaluacion` de Luca (FASE 37) quedo ARCHIVADO el 2026-10-23 (13/13). C-144 `declarar-procedencia-real-y-ausencia-de-preproduccion` de Luca (FASE 38) quedo ARCHIVADO el 2026-10-23 (18/18). Hasta la FASE 35 el roadmap habia quedado COMPLETO el 2026-10-22: todos los changes creados (C-01..C-124) estaban archivados; ese mismo dia se archivaron tambien C-125, C-126, C-127 y C-129 de Luca, y el 2026-10-23 quedo ARCHIVADO C-128 de Luca (FASE 35 bis, 22/22, alcance reducido).

Los changes de tesis de las FASES 29/31/34 (C-76..C-80, C-92..C-96 y C-102..C-119) y el de la FASE 35 (C-120) quedaron APLICADOS y ARCHIVADOS entre el 2026-10-20 y el 2026-10-22. Orden seguido en las FASES 29/31: C-76 -> C-77 -> C-78 -> C-79 -> C-80 -> C-92 -> C-93 -> C-94 -> C-95 -> C-96; en las FASES 33/34/35: C-98..C-101 -> C-102..C-119 -> C-120. Dentro de la FASE 35 ampliada, C-121, C-122 y C-123 (changes de tesis) y C-124 (test PostgreSQL) tambien quedaron APLICADOS y ARCHIVADOS el 2026-10-22, en el orden C-122 -> C-121 -> C-123 -> C-124.

La numeracion va de C-01 a C-169 (C-21, C-49 y C-50 nunca se crearon; `c-51` fue absorbido por C-52 y no se abre; c-63 se cuenta como un change con sus tres partes c-63a/b/c). Los changes activos son c-165 a c-169 (FASE 52): c-168 APLICADO (31/31, commit `1a065cd`) con el archive pendiente, c-166 en aplicacion, c-165 y c-167 con el apply pendiente y c-169 GATEADO; c-161 a c-164 (FASES 49 a 51) estan ARCHIVADOS desde el 2026-10-29. La release vigente de la tesis es `v1.2.5` (tag anotado sobre `e5508850b5b48368c9cc446de2d616a5198c3f20`, 2026-10-28; 106 paginas: cuerpo 98 y anexos 8); `v1.2.2` (`445a47b4f6fccca3d4611ee3cb7adea4e7350dcc`, 2026-10-27; 104 paginas: cuerpo 96 y anexos 8; change C-147), `v1.2.1` (`509ffff105c21fed0c07cbf9a46245ba6c53e0e1`), `v1.2.0` (`a49d035c67b32ae17e633ec04b09ecdd2781aac6`), `v1.1.1` (`4160d84286623b073d2904353e6f9163ae211de7`), `v1.1.0` (`7103b649d8c4f51737ad6ad4095dad22c9406400`), `v1.0.1` y `v1.0.0` son versiones previas.

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

1. **`c-49-carga-corpus-db`** — SUPERADO (verificado 2026-10-20; NO crear). Objetivo original: cargar los 200 casos del corpus en una tabla dedicada (`corpus_incidente`), solo con la descripcion pseudonimizada, aislada de la tabla operativa, con FK nullable `incidente_id` -> `incidente.id`; era una etapa TEMPORAL "hasta poder correr el flujo completo". Esa condicion ya se cumplio: el flujo real ingesta el corpus 200/200 (C-68 web/correo + C-70 telefonia) y la aislacion se logro con la base descartable `mesa_de_ayuda_corpus` + correlacion exacta por `corpus_case_id` (`openspec/specs/telefonia-corpus-medicion/spec.md`), sin migracion de esquema (`c-68/proposal.md`). La tabla `corpus_incidente` nunca se creo y ningun spec vigente la requiere.
2. **`c-50-corpus-timing-wiring`** — PARCIALMENTE SUPERADO (verificado 2026-10-20). Hecho: `tiempo_automatizado_s` se deriva de `latencia_e2e_ms` medido y el corpus quedo poblado 200/200 (C-68/C-70; `openspec/specs/corpus-n8n-ingest/spec.md`, `openspec/specs/telefonia-corpus-medicion/spec.md`). Residual vivo (no bloqueante): (a) `evaluation/stats.py` (Wilcoxon, corregido por C-77) NO esta cableado al reporte —`evaluation/run_evaluation.py` no importa `evaluation.stats` y `evaluation/report.md` no tiene seccion Wilcoxon; los numeros de la tesis se calcularon ad hoc—; (b) no se separo el contrato del loader de `evaluation/corpus.py` (clasificacion vs timing). Trampa latente: la seccion "Normalidad (Shapiro-Wilk)" de `evaluation/report.md` se agrego a mano en C-95, asi que regenerar el reporte la borra. Cerrar el residual (a) seria un change chico propio. Nota 2026-10-22: el residual (a) y la trampa latente quedaron RESUELTOS por `c-99-cablear-wilcoxon-al-reporte` (archivado 2026-10-20, commit `3c23726`): `evaluation/run_evaluation.py` importa `evaluation.stats` y genera la seccion `## Tiempos` de `evaluation/report.md` (Normalidad (Shapiro-Wilk), prueba de Wilcoxon, reduccion de tiempos y desglose por canal), de modo que regenerar el reporte ya no la borra; el texto anterior se conserva como registro de la verificacion del 2026-10-20 y el residual (b) no se modifica.
3. **Programa de medicion `c-165` a `c-169` (FASE 52)** — ACTIVO (creado el 2026-10-29 y enmendado el 2026-10-30; los cinco figuran en `openspec list`). Orden recomendado: `c-168` (APLICADO el 2026-10-30, 31/31, commit `1a065cd`; archive pendiente) -> `c-166` (en aplicacion) -> `c-165` hasta su checkpoint 2.1 (gobernanza ALTA: confirmacion humana antes de tocar el esquema) -> `c-167` -> campana de campo (fuera del repositorio) -> `c-169` (GATEADO hasta que `c-165` a `c-168` esten archivados y la campana haya corrido). Orden de archive de la capability `evaluation-campaign-instrumentation`: `c-165` -> `c-166` -> `c-168`. Detalle por change en la FASE 52 y plan de la corrida en `docs/campana-medicion/plan-campana-de-medicion.md`.

Operativo para habilitar el pipeline pago (fuera de changes):
- Cargar la credencial real de Twilio (`TWILIO_AUTH_TOKEN`) y apuntar la Voice URL de la
  consola a `https://<host>/api/v1/cost-guard/twilio/voice`; con eso la validacion de firma
  de C-45 se activa sola.
- Verificacion manual en N8N en vivo de C-46 (tareas 5.2/5.3) y C-47 (tarea 5.4): confirmar que
  `.first()` resuelve, que el incidente telefonico persiste `ingresado_en` no nulo y que el
  `AI Agent` recibe el item sellado tras la guarda.

Deuda menor pendiente (no bloqueante):
- Tesis post-pipeline: la reconciliacion del Cap. 7 con el corpus real y las correcciones de 4.3/4.8/Cap. 11 quedaron cubiertas por C-76 (Cap. 4/7/8), C-77 (estadistica/inferencia) y C-79 (Cap. 11), archivados el 2026-10-20. La evidencia visual de C-80 (capturas de UI 6.5/6.6) NO sigue pendiente: C-80 se archivo 45/45 el 2026-10-21 (ver la actualizacion de cierre del roadmap mas arriba, que registra el cierre), de modo que esta deuda residual quedo cerrada.

Para avanzar:
- Workstream aprobado: el plan de cumplimiento ISO/NIST/Ley 25.326 (`docs/cumplimiento/plan-cambios-cumplimiento.md`), en la FASE 21. C-61 (2026-10-01), C-62 (2026-10-08), C-63a/b/c (2026-10-08), C-64 (2026-10-19), C-65 (2026-10-19) y C-66 (2026-10-19) quedaron ARCHIVADOS. El workstream quedo TOTALMENTE EJECUTADO: no quedan changes planificados.
- `c-56`: ARCHIVADO (2026-10-08, 27/27); smoke manual confirmado end-to-end (operador resuelto + fallback + auditoria); spec `notification-routing` creada.
- `c-60`: ARCHIVADO (2026-10-06, 33/33).
- `c-67`: CERRADO NO REALIZADO y ARCHIVADO (2026-10-19, `--skip-specs`, 0/24). El spike de OQ3 cerro el 2026-09-23 con veredicto GO-WITH-CONSTRAINTS (SMS best-effort, correo primario); `C-66 privacidad-transferencias` se creo y archivo despues (2026-10-19, 36/36); SMS no es entregable de la tesis. No hay nada que aplicar en `c-67`.
- `c-68`: ARCHIVADO (2026-10-09, 63/63); harness de ingesta web/correo verificado (PASS, 0 CRITICAL), W1/W3 resueltos, W2 aceptado, corpus 200/200; spec `corpus-n8n-ingest` creada.
- `c-70`: ARCHIVADO (2026-10-06, 72/72); corrida completa de los 81 casos y write-back realizados; corpus 200/200 cargable. Governance ALTO.
