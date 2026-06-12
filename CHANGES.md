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
 │    └── C-10 documentation-annexes (C-04, C-05, C-09)
 └── C-09 ci-cd-pipeline (C-06, C-07)
      └── C-10 documentation-annexes (C-09)
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
  - `Gestion_Incidentes/app/utils/n8n_webhook.py` (funcion existente)
  - `Gestion_Incidentes/app/services/incidente_service.py` (donde debe llamarse)
  - `Gestion_Incidentes/app/config/settings.py` §n8n_webhook_url

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
  - `ANEXO_H_Prompt_Gemini_Especificacion.md` §H.3 (validacion de respuesta)
  - `Gestion_Incidentes/app/classifiers/gemini_classifier.py` (donde se envia a Gemini)

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
  - `Automatizacion_Mesa_de_Ayuda.json` (workflow actual)

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
  - `Gestion_Incidentes/tests/conftest.py` (infraestructura existente)
  - `Gestion_Incidentes/tests/test_deterministic_classifier.py` (patron de tests existente)
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
  - `Frontend/package.json` (dependencias actuales)
  - `Frontend/vite.config.ts` (configuracion existente)
  - `docs/Tesis/tesis_para_agente.md` §6.5 (pruebas automatizadas)

---

## FASE 5 — Evaluacion y Automatizacion

> C-08 implementa el framework de evaluacion que la tesis describe en el Capitulo 7.
> C-09 automatiza la ejecucion de pruebas en cada push.

### [C-08] `evaluation-framework`

- **Estado**: `[x]` completado (2026-06-11 — openspec/changes/archive/2026-06-11-c-08-evaluation-framework; tarea 8.1 corrida real pendiente del corpus no-trackeado)
- **Scope**:
  - Crear script Python en `evaluation/run_evaluation.py` que cargue el corpus de 200 casos desde CSV
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
  - `ANEXO_H_Prompt_Gemini_Especificacion.md` §H.4 (iteracion y mejora)

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
  - `Gestion_Incidentes/pytest.ini` (configuracion pytest existente)
  - `Gestion_Incidentes/requirements.txt` (dependencias)

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
  - `Gestion_Incidentes/Dockerfile` y `Gestion_Incidentes/docker-compose.yml`
  - `Frontend/vite.config.ts`

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

**Total**: 10 changes organizados en 6 fases.
**Camino critico**: 7 changes (C-01 → C-02 → C-04 → C-05 → C-08 → C-09 → C-10).
**Gates de paralelismo**: 5 gates (permite hasta 3 agentes simultaneos).

---

## Notas del analisis

### Estado actual del proyecto (verificado contra el codigo)

| Componente | Estado | Observaciones |
|------------|--------|---------------|
| Backend: clasificadores | COMPLETO | DeterministicClassifier, GeminiClassifier, HybridClassifier implementados y documentados |
| Backend: routes/endpoints | COMPLETO | CRUD incidentes, revision humana, health check |
| Backend: servicios | COMPLETO | IncidenteService, ClasificacionService con inyeccion de dependencias |
| Backend: modelos ORM | COMPLETO | 5 tablas segun tesis: incidente, sector, estado, canal_origen, clasificacion_log |
| Backend: repositorios | COMPLETO | Patron repositorio con sesion compartida, filtros dinanicos |
| Backend: keywords | COMPLETO | Regex para Sistemas (24), Operaciones (16), Soporte Tecnico (20) |
| Backend: util n8n_webhook | DEFINIDO NO USADO | `notify_n8n()` existe pero nunca se llama desde el servicio |
| Backend: tests | PARCIAL | 13 tests solo clasificador; conftest.py listo para integration tests |
| Backend: pseudonimizacion | NO IMPLEMENTADO | Requisito Ley 25.326 para envio a Gemini |
| Backend: migraciones | COMPLETO | Alembic configurado |
| N8N workflow JSON | PLACEHOLDER | Nodos JS/Python con logica placeholder, IF conditions vacias |
| Frontend: paginas | COMPLETO | ReportarIncidente (form), Administracion (tickets + revision humana) |
| Frontend: componentes | COMPLETO | shadcn/ui, badges, indicadores, tablas, dialogos |
| Frontend: hooks/services | COMPLETO | React Query + Axios, todos los endpoints conectados |
| Frontend: tests | NO IMPLEMENTADO | Sin Vitest, sin testing-library |
| Infra: Docker | COMPLETO | docker-compose.yml, Dockerfile |
| Infra: CI/CD | NO IMPLEMENTADO | Sin GitHub Actions |
| Docs: anexos A-G | PARCIAL | Algunos marcados "{A desarrollar}" en la tesis |

Cambios que NO estan en el roadmap porque el proyecto completario esta implementado:
- Clasificador hibrido (completo)
- CRUD de incidentes (completo)
- Cola de revision humana (completa)
- Frontend completo (completo)
- Infraestructura Docker (completa)
- Keywords dictionary (completo)

---

## Primer change recomendado

Para arrancar: `/opsx:propose C-01-foundation-setup`

Este change prepara el terreno para todos los demas: completa la configuracion OPSX,
configura el `.engram/` compartido, y verifica que las migraciones y catalogos esten
en orden antes de empezar a tocar codigo.
