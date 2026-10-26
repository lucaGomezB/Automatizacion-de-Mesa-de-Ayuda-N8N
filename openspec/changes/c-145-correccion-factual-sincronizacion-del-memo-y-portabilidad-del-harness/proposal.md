## Why

La release `v1.2.0` (PR #40) integra la FASE 36 pero conserva afirmaciones que el repositorio desmiente: el Capítulo 6 declara 16 pruebas de integración PostgreSQL que se omiten con `pytest.skip` cuando en realidad son 48 y fallan ruidosamente, y publica recuentos de la suite de frontend que no se pueden reproducir. El memo canónico tampoco registra el margen de error vigente del 6,66 % y conserva referencias de línea desfasadas. El PR #40 ya se mergeó a `main` (`224fa16`), de modo que el defecto está en la rama principal y el jurado leería cifras falsas en la versión entregada. La corrección se publica como `v1.2.1` mediante un PR propio. Además, el arnés de sensibilidad falla en Python 3.12.3 por una ambigüedad de `argparse`, de modo que la reproducibilidad depende del parche del intérprete y no del código.

## What Changes

- **Bloque A — corrección factual de la tesis (MEDIO).** Corregir `06-implementacion.tex:87` (48 pruebas de integración, sin omisión automática; falla ruidosa si PostgreSQL no está disponible), retirar los recuentos congelados de `06-implementacion.tex:91` y reemplazar las referencias internas `OQ1 = A` / `OQ2 = A del change c-72` de `06-implementacion.tex:44` y `:54` por lenguaje llano. Registrar en el REGISTRO la causa raíz: la oración nació en `a0436e0` (C-19, 2026-07-03, con 16 pruebas y omisión) y `ef656ac` (2026-09-17) cambió `conftest.py` a fallo ruidoso; la copia a v9/v10 (`8466cbe`, `7408543`) arrastró la oración sin actualizarla.
- **Bloque B — sincronización del memo (MEDIO).** Hacer upsert del margen `6,66 %` con `N ≈ 2.646` como `vigente` y marcar `6,74 %` / `N = 3.700` como `retirado` en `numeros-canonicos.md`; recalcular y corregir todas las referencias `07-resultados.tex:<línea>` del memo, no solo `:129` y `:75`.
- **Bloque C — precisión de la discusión (MEDIO).** En `08-discusion.tex:10` explicitar el valor pareado `96/130 = 0,7385` junto al global; en `08-discusion.tex:95` completar `+42,1 / +52,1 / +62,0` o retirar el paréntesis.
- **Bloque D — higiene del registro (BAJO).** Resolver `dictamen-correcciones.md:140` (`### P4. (a completar)`) con una nota de estado fechada, sin inventar observaciones.
- **Bloque E — portabilidad del arnés (BAJO, código).** Poner `allow_abbrev=False` en el parser de `evaluation/sensibilidad_ajustes.py` y agregar una prueba de regresión que fije el comportamiento. Incluir el manejo limpio del `FileNotFoundError` de `--solo-tiempos` en `run_evaluation.py`; excluir la procedencia de las cachés de predicciones (ver design.md, E2).
- **Bloque G — documentación para agentes sincronizada con el código (BAJO).** `CLAUDE.md` declara Gemini 2.5 Flash, timeout 10 s y un flujo con LangChain AI Agent y Redis que ya no existe; `openspec/config.yaml` (fuente que heredan los sub-agentes) declara Gemini 2.5 Flash, `google-genai >= 1.0`, `timeout_s: 10` y FastAPI 0.115. El código corre `gemini-3.6-flash`, timeout 30 s, total 60 s, 2 reintentos, `fastapi==0.143.3`, `google-genai>=2.31.0,<3`, y el stack no tiene servicio Redis. Se alinean ambos documentos con el código y se corrige el docstring obsoleto (`>= 0.90`) de `App/Backend/tests/test_hybrid_classifier.py:8-9`.
- **Bloque H — barrera mecánica contra el drift documental (BAJO, código).** Un requisito de spec no impide que la documentación vuelva a divergir: `openspec validate` verifica forma, no contenido, y hoy ningún chequeo abre `CLAUDE.md` ni `openspec/config.yaml`. Se agrega `scripts/preflight/docs_stack_sync.py`, que compara esos dos documentos contra `settings.py`, `requirements.txt` y `docker-compose.yml` y falla con un hallazgo por cada divergencia (modelo, timeout, reintentos, FastAPI, Uvicorn, google-genai, imagen de N8N, servicios inexistentes, etapas retiradas). Se cablea en el job `backend-tests` junto a los otros dos preflights. Es la barrera ejecutable de `DOC-005`.
- **Bloque F — recompilación y release (ALTO).** Recompilar en `texlive-thesis`, medir el tope (cuerpo sin anexos ≤ 100), publicar `v1.2.1` con el patrón de dos commits sobre el texto corregido y actualizar REGISTRO, `CHANGES.md` y la descripción del PR de corrección. `v1.2.0` queda inmutable y registrada como superada.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tesis-document`: se modifica el requisito `Verificabilidad de las afirmaciones de pruebas del Capitulo 6` (las cifras y el comportamiento de la suite deben ser reproducibles, incluidas las pruebas de integración PostgreSQL) y se agrega un requisito de publicación de una release de corrección sin mover tags ya publicados.
- `tesis-numeros-canonicos`: se modifica `Registro canónico con procedencia por valor` (todo margen debe registrarse con su `N` y las referencias de línea deben resolver).
- `evaluation-framework`: se agrega un requisito de portabilidad del CLI de sensibilidad entre versiones de Python 3.12.
- `project-documentation`: se agrega `DOC-005`, que exige que la documentación para agentes no declare un stack distinto del que fija el código y las dependencias.

## Impact

- **Sucede a:** el merge del PR #40 `ramagonzalo` → `main` (`224fa16`), ya integrado. Este change corrige en `main` el defecto que ese merge dejó y publica `v1.2.1` mediante un PR propio.
- **Edita:** `docs/Tesis/v10 (IA)/paper/sections/{06-implementacion,08-discusion}.tex`; `docs/Tesis/Correcciones/{numeros-canonicos,dictamen-correcciones}.md`; `evaluation/sensibilidad_ajustes.py`, `evaluation/run_evaluation.py` y `evaluation/tests/test_sensibilidad_ajustes.py`; `CLAUDE.md`; `openspec/config.yaml`; `App/Backend/tests/test_hybrid_classifier.py` (solo el docstring del módulo); `scripts/preflight/docs_stack_sync.py` y su test (nuevos); `.github/workflows/ci.yml`; artefactos de compilación de `paper/`; renders derivados; `CHANGES.md`.
- **No toca:** el código de `App/Backend/app/` (solo un docstring de test), `n8n/`, `data/`, el corpus, los valores canónicos vigentes distintos del margen, ni los tags `v1.0.0`..`v1.2.0`.
- **Gobernanza:** A, B y C MEDIO; D, E, G y H BAJO; F ALTO (artefacto publicado: tag, push y PR).
- **Dependencias:** PR #40 mergeado en `main` (`224fa16`); imagen `texlive-thesis` disponible; Python 3.12.3 en la máquina de trabajo (CI usa 3.12.15).
- **Riesgo principal:** el cuerpo está en 100 páginas exactas; cualquier oración más larga desborda el tope. Se mide antes y después y se aplica una palanca de formato declarada.
