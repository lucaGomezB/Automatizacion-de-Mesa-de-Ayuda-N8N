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

--- FASE 15: Sincronizacion documental (C-42 — ACTIVO) ---

C-42 bootstrap-docs-sync (C-39, C-40, C-41)
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

**Total**: 42 changes documentados — 41 archivados (C-01..C-41, sin C-21) mas el mantenimiento sin numero `improve-dockerfiles`, y C-42 activo (propuesto, no aplicado). C-21 no existe: no fue creado.
**Camino critico (software)**: 7 changes (C-01 → C-02 → C-04 → C-05 → C-08 → C-09 → C-10).
**Gates de paralelismo**: 5 gates (permite hasta 3 agentes simultaneos).
**Fases**: 1-15 (la FASE 9 quedo vacia; los changes que alli se preveian se documentan en la FASE 12).

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

> C-42 alinea la documentacion operativa con el arranque de la Fase 1.

### [C-42] `bootstrap-docs-sync`

- **Estado**: `[x]` completado, verificado y archivado (2026-09-20 — `openspec/changes/archive/2026-09-20-c-42-bootstrap-docs-sync`; 15/15 tareas, 6 tests estructurales, 437 passed)
- **Scope**:
  - Alinear `README.md` y `docs/operational-guide.md` con el arranque de Fase 1: el preflight de entorno ahora exige `JWT_SECRET_KEY`; documentar el gate de costo y el bypass `UP_SKIP_COST_PREFLIGHT=1`; presentar el comando unico (`scripts/up.sh` / `make up`) como camino recomendado en la guia operativa, preservando el camino manual.
  - Test estructural `App/Backend/tests/test_docs_bootstrap_sync.py`.
- **Dependencias**: `C-39`, `C-40`, `C-41`
- **Governance**: BAJO
- **Leer antes**:
  - `openspec/changes/c-42-bootstrap-docs-sync/proposal.md`
  - `openspec/specs/local-bootstrap/spec.md`
  - `openspec/specs/cost-readiness/spec.md`

---

## Notas del analisis

### Estado actual del proyecto (verificado contra el codigo)

| Componente | Estado | Observaciones |
|------------|--------|---------------|
| Backend: clasificadores | COMPLETO | DeterministicClassifier, GeminiClassifier, HybridClassifier implementados y documentados |
| Backend: routes/endpoints | COMPLETO | CRUD incidentes, revision humana, auth, estadisticas, health |
| Backend: servicios | COMPLETO | IncidenteService, ClasificacionService, EstadisticasService |
| Backend: modelos ORM | COMPLETO | Tablas base (incidente, sector, estado, canal_origen, clasificacion_log) mas `users` (C-15) y columnas de timing (C-39, migracion 006) |
| Backend: repositorios | COMPLETO | Patron repositorio con sesion compartida, filtros dinamicos |
| Backend: keywords | COMPLETO | Mapa redistribuido en los 5 sectores canonicos (C-27) |
| Backend: util n8n_webhook | EN USO | `notify_n8n()` fire-and-forget desde el servicio; apunta al webhook N8N dedicado (C-33) |
| Backend: tests | COMPLETO | Suite offline SQLite (437 passed) + subconjunto de integracion PostgreSQL sobre base descartable (C-19/C-32) |
| Backend: pseudonimizacion | COMPLETO | C-03; cifrado at-rest con Fernet |
| Backend: migraciones | COMPLETO | Alembic; migraciones 001-006 (la 006 agrega timing e2e, C-39) |
| Backend: auth | COMPLETO | JWT Bearer (C-15) |
| N8N workflow JSON | COMPLETO | Canales cableados (C-04/C-05), compuerta de confianza de dos capas (C-38), wiring corregido (C-40) |
| Frontend: paginas | COMPLETO | ReportarIncidente, Administracion, Dashboard (C-23), Login (C-15) |
| Frontend: componentes | COMPLETO | shadcn/ui, badges, indicadores, tablas, dialogos |
| Frontend: hooks/services | COMPLETO | React Query + Axios, todos los endpoints conectados |
| Frontend: tests | COMPLETO | Vitest + Testing Library (C-07) |
| Infra: Docker | COMPLETO | docker-compose.yml + nginx TLS (C-20); Dockerfiles multi-stage non-root (improve-dockerfiles) |
| Infra: CI/CD | COMPLETO | .github/workflows/ci.yml (C-09); incluye la suite y el CLI del preflight (C-41) |
| Infra: arranque | COMPLETO | scripts/up.sh / up.ps1 + Makefile (C-28); preflight de entorno y de costo (C-41) |
| Docs: anexos A-G | COMPLETO | C-10 documentation-annexes |
| Docs: guia operativa | COMPLETO | C-42 alinea README y guia operativa con el arranque (archivado) |
| Auth: JWT Bearer | COMPLETO | C-15 jwt-auth-backend-frontend |
| KB: knowledge-base | ACTUALIZADA | C-14 kb-sync-implementation-state |
| Twilio: TwiML script | COMPLETO | C-16 twilio-twiml-script |
| Seguridad: higiene de secretos | COMPLETO | C-37 (hook pre-commit + runbook + escaneo del lado GitHub) |
| Corpus: JSON multietiqueta | PENDIENTE DATOS REALES | C-27 rediseno-sectores-json (sintetico de 200 casos eliminado; el corpus real aun no es cargable porque los tiempos automatizados estan nulos) |
| Timing e2e | IMPLEMENTADO | C-39; `ingresado_en` / `persistido_en` / `latencia_e2e_ms` (pendiente verificacion de runtime del canal telefonico) |
| Backup scripts: PostgreSQL | IMPLEMENTADO | C-26 — scripts/backup.sh y scripts/backup.ps1 con rotacion de 7 dias |
| N8N retention: 30 dias | CONFIGURADO | C-26 — EXECUTIONS_DATA_PRUNE y EXECUTIONS_DATA_MAX_AGE en docker-compose.yml |

Tabla reconciliada con el estado real el 2026-09-20: C-14..C-42 quedaron documentados en las FASE 12-15.

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

Todos los changes estan implementados y archivados (C-01 a C-42; C-21 no existe). No hay
ningun change activo.

El proximo trabajo de mayor valor es la Fase 2 del pipeline, todavia sin change abierto:

1. Verificar en runtime (workflow N8N real) que el sello de ingreso de telefonia sobrevive
   al `AI Agent`; hoy solo tiene verificacion estructural y el try/catch silencioso devuelve
   null si el pairing falla, desactivando la latencia del canal pago.
2. Cablear `tiempo_automatizado_s` al corpus de evaluacion (hoy `evaluation/corpus.py`
   rechaza el corpus real porque los tiempos automatizados estan nulos).

Para abrir el primero: `/opsx:propose c-43-<nombre>`.
