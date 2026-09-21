## 1. RED — Red de seguridad estructural

- [x] 1.1 Crear `App/Backend/tests/test_docs_restructure_sync.py` con un helper de lectura por path relativo a la raíz (`Path(__file__).resolve().parents[3]`, patrón de `test_docs_bootstrap_sync.py`) y un helper que aísle una sección por su encabezado; agregar el test que asserta que la sección "Configurar las variables de entorno" de `README.md` contiene `JWT_SECRET_KEY`; ejecutar `cd App/Backend; pytest tests/test_docs_restructure_sync.py -q` y confirmar que FALLA (RED) porque la tabla de esa sección no lista la variable
- [x] 1.2 Agregar el test que asserta que el bloque dotenv de la sección 1.2 (Configurar variables de entorno) de `docs/operational-guide.md` contiene `JWT_SECRET_KEY`; ejecutar el archivo y confirmar RED
- [x] 1.3 Agregar un test parametrizado que asserta que cada documento en alcance referencia `App/Backend/` donde corresponde: `docs/operational-guide.md`, `docs/troubleshooting.md`, `docs/como_cargar_datos_corpus.md`, `docs/diagrams/componentes.md`, `docs/parameters_gemini.md`, `docs/pseudonymization.md`, `docs/anexo_c_esquema_bd.md`; ejecutar y confirmar RED en los documentos que hoy no contienen la ruta vigente (troubleshooting, componentes, parameters_gemini, pseudonymization, anexo_c)
- [x] 1.4 Agregar el control negativo que asserta que ninguno de esos siete documentos (más `docs/operational-guide.md`) contiene el token obsoleto `Gestion_Incidentes/`; ejecutar y confirmar RED en los ocho documentos
- [x] 1.5 Agregar el test del caso histórico y de la anotación: `docs/security-hardening.md` conserva `Gestion_Incidentes/` (el hecho) y contiene el marcador de anotación `ruta historica`; ejecutar y confirmar RED porque la anotación aún no existe

## 2. GREEN — Variables de entorno (`JWT_SECRET_KEY`)

- [x] 2.1 Agregar la fila `JWT_SECRET_KEY` a la tabla de la sección "Configurar las variables de entorno" de `README.md` (líneas 94-98), describiéndola como clave de firma HS256 e incluyendo `python -c "import secrets; print(secrets.token_urlsafe(32))"`; ejecutar `cd App/Backend; pytest tests/test_docs_restructure_sync.py -q` y confirmar GREEN del test de README
- [x] 2.2 Agregar `JWT_SECRET_KEY` al bloque dotenv de la sección 1.2 de `docs/operational-guide.md` (líneas 48-61) con la misma descripción y comando de generación; ejecutar el archivo y confirmar GREEN del test de la guía
- [x] 2.3 Verificar releyendo ambas secciones que `JWT_SECRET_KEY` aparece con descripción de firma HS256 y comando de generación, sin eliminar `DATABASE_URL`, `GEMINI_API_KEY` ni `PSEUDONYMIZATION_ENCRYPTION_KEY`

## 3. GREEN — Rutas post-reestructuración verificadas

- [x] 3.1 Verificar los destinos reales antes de editar: `ls App/Backend/.env.example App/Backend/requirements.txt App/Backend/scripts/export_openapi.py` y confirmar que existen; registrar el resultado en la sesión de apply
- [x] 3.2 Reemplazar en `docs/operational-guide.md` las líneas 43 y 46 (`Gestion_Incidentes/.env.example` / `.env` → `App/Backend/.env.example` / `.env`), la línea 372 (`cd Gestion_Incidentes` → `cd App/Backend` para regenerar OpenAPI) y la línea 383 (`Gestion_Incidentes/requirements.txt` → `App/Backend/requirements.txt`)
- [x] 3.3 Reemplazar en `docs/troubleshooting.md` las líneas 25, 27, 85 y 152 (`Gestion_Incidentes/.env` → `App/Backend/.env`, incluido el `cp` de la plantilla)
- [x] 3.4 Reemplazar en `docs/como_cargar_datos_corpus.md` la línea 189 (`PYTHONPATH=Gestion_Incidentes` → `PYTHONPATH=App/Backend`, alineado con `evaluation/run_evaluation.py` que espera esa ruta)
- [x] 3.5 Reemplazar en `docs/diagrams/componentes.md` la línea 3 (`Gestion_Incidentes/app/` → `App/Backend/app/`), en `docs/parameters_gemini.md` la línea 59 (`Gestion_Incidentes/app/classifiers/gemini_classifier.py` → `App/Backend/...`) y en `docs/pseudonymization.md` la línea 4 (`Gestion_Incidentes/app/utils/pseudonymizer.py` → `App/Backend/...`)
- [x] 3.6 Reemplazar en `docs/anexo_c_esquema_bd.md` las líneas 4 y 5 (`Gestion_Incidentes/app/models/` → `App/Backend/app/models/`; `Gestion_Incidentes/alembic/` → `App/Backend/alembic/`); ejecutar `cd App/Backend; pytest tests/test_docs_restructure_sync.py -q` y confirmar GREEN de los tests de rutas y del control negativo

## 4. GREEN — Narrativa histórica preservada

- [x] 4.1 En `docs/security-hardening.md` línea 179, conservar el hecho (el archivo estaba en `Gestion_Incidentes/.env`) y agregar una aclaración parentética con el marcador `ruta historica` indicando que hoy el módulo vive en `App/Backend/`; ejecutar `cd App/Backend; pytest tests/test_docs_restructure_sync.py -q` y confirmar GREEN del test histórico
- [x] 4.2 Confirmar que `docs/Tesis/**` no fue modificado: ejecutar `git status --porcelain docs/Tesis` y verificar que no hay entradas

## 5. TRIANGULATE — Cobertura de los escenarios de la spec

- [x] 5.1 Confirmar que el control negativo se aplica exactamente al conjunto de documentos en alcance y excluye `docs/security-hardening.md`; ejecutar el archivo y confirmar que el caso parametrizado cubre los ocho documentos de la Sección 3
- [x] 5.2 Agregar un caso que asserta que `README.md` conserva los tokens de c-42 (`UP_SKIP_COST_PREFLIGHT` y `https://localhost/api/v1/health`) para evitar regresión; ejecutar y confirmar que pasa
- [x] 5.3 Agregar un caso que asserta que `docs/operational-guide.md` conserva el comando unico (`scripts/up.sh` o `make up`) y el camino manual (`docker compose up -d`); ejecutar y confirmar que pasa

## 6. REFACTOR y verificación final

- [x] 6.1 Refactorizar `App/Backend/tests/test_docs_restructure_sync.py` extrayendo constantes de path y helpers reutilizables, dejando los asserts legibles; ejecutar `cd App/Backend; pytest tests/test_docs_restructure_sync.py -q` y confirmar que sigue GREEN
- [x] 6.2 Ejecutar `cd App/Backend; pytest tests/test_docs_bootstrap_sync.py tests/test_docs_restructure_sync.py -q` y confirmar que ambos módulos pasan (sin regresión de c-42)
- [x] 6.3 Ejecutar la suite offline completa `cd App/Backend; pytest -m "not integration" -q` y confirmar que no hay regresiones
- [x] 6.4 Ejecutar `openspec validate --strict --changes c-43-docs-restructure-sync` y confirmar que pasa
- [x] 6.5 Ejecutar `openspec status --change c-43-docs-restructure-sync` y confirmar que las tareas quedan registradas