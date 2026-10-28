## Why

La ablacion paga del prompt (nivel c, checkpoint "OQ7a/G0.7a", 138 invocaciones sobre 2 brazos x 69 casos) fue autorizada por el autor y ejecutada el 2026-10-28, pero FALLO: el arnes de evaluacion (`evaluation/sensibilidad_ajustes.py`) tiene dos defectos verificados que impiden correr los brazos por los comandos documentados, y el nivel c del prompt en la tesis permanece "no computado". Sin corregir el arnes, la recomendacion A5 del dictamen no puede completarse ni propagarse el valor calculado a los documentos de la tesis.

## What Changes

- **Defecto A (clave envenenada).** `preparar_entorno_offline()` aplica `os.environ.setdefault("GEMINI_API_KEY", "offline-dummy-key-sin-llamadas")` sobre `ENTORNO_OFFLINE`. La clave real vive solo en `App/Backend/.env` y pydantic-settings prioriza `os.environ` sobre `.env`; por eso el camino pago uso la clave ficticia y las 69 invocaciones de cada brazo fallaron con `ClientError 400 API_KEY_INVALID`, cayendo todas a fallback. El arreglo DEBE hacer que el camino pago use la clave real sin romper los caminos puramente offline (lineas de `clasificador_con_vocabulario` y `leer_punto_de_operacion`), que necesitan valores inertes. <!-- gitleaks:allow -->
- **Defecto B (prompt congelado demasiado temprano).** `App/Backend/app/classifiers/__init__.py` importa `gemini_classifier` de forma anticipada al importar el paquete, lo que ejecuta `_PROMPT_TEMPLATE = _load_prompt()` antes de que el brazo `sin-reglas` fije `GEMINI_PROMPT_PATH`. El prompt vigente queda congelado y el gate de SHA-256 rechaza el brazo. El arreglo DEBE hacer que cada brazo cargue su propio prompt (import perezoso y/o carga del prompt despues de fijar la variable de entorno), sin cambiar el comportamiento del clasificador.
- Corregir ambos defectos por TDD estricto (RED -> GREEN -> TRIANGULATE -> REFACTOR) dentro de la suite propia de `evaluation/` (`evaluation/` tiene su propio `pytest.ini`; las pruebas corren desde ese directorio).
- **Grupo final (despues de que la correccion este en verde).** Ejecutar la corrida paga ya autorizada de los dos brazos (`cd App/Backend; PYTHONPATH=../.. python -m evaluation.sensibilidad_ajustes prompt --brazo vigente --confirm-paid` y lo mismo con `--brazo sin-reglas --confirm-paid`), cerrar el reporte de sensibilidad offline con el nivel c y propagar el valor calculado del nivel c a `docs/Tesis/Correcciones/numeros-canonicos.md`, `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex`, `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` y la entrada G0.7a del ledger `docs/Tesis/Correcciones/dictamen-correcciones.md`.

## Capabilities

### New Capabilities

- Ninguna. La correccion se expresa como cambios en la capability existente `evaluation-framework`.

### Modified Capabilities

- `evaluation-framework`: el requisito "Sensibilidad de la etapa semantica frente a las reglas de frontera del prompt" se modifica para exigir que la ablacion paga use la credencial real del proveedor cargada de la configuracion del backend (no un valor inerte inyectado) y que cada brazo cargue su propio prompt antes de que cualquier componente lo lea. Se agrega un requisito que fija la separacion entre el camino pago (credencial real) y los caminos offline (valores inertes), de modo que la correccion del camino pago NO degrade ni altere la reproducibilidad de la evaluacion offline.

## Impact

- `evaluation/sensibilidad_ajustes.py`: `preparar_entorno_offline`, `ENTORNO_OFFLINE`, `_cli_prompt`, `_prompt_cargado_por_el_backend`, `_construir_hybrid_real`, `correr_brazo_prompt`, `_casos_escalados_reales`.
- `App/Backend/app/classifiers/__init__.py`: import anticipado de `gemini_classifier`.
- `App/Backend/app/classifiers/gemini_classifier.py` y `App/Backend/app/config/settings.py`: solo como contexto del congelamiento del prompt y de la prioridad de `os.environ` sobre `.env`; el comportamiento del clasificador NO cambia.
- `evaluation/tests/test_sensibilidad_ajustes.py`: pruebas de regresion de ambos defectos (TDD).
- Documentos propagados tras la corrida (grupo final): `docs/Tesis/Correcciones/numeros-canonicos.md` (fila del nivel c), `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex`, `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` y `docs/Tesis/Correcciones/dictamen-correcciones.md` (entrada G0.7a).
- Governance: BAJO/MEDIO (arnes de evaluacion; NO es codigo de produccion bajo `App/Backend/app/routes|services|repositories`). No se toca el corpus, las cinco cadenas canonicas de sector, los valores de `gemini-3.6-flash`, `requirements.txt` ni `openspec/config.yaml`.
