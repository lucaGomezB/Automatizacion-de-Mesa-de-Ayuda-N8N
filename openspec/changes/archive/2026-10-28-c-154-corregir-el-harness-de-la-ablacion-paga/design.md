## Context

Ver `proposal.md` (Why) para la motivacion. Estado y restricciones verificados el 2026-10-28:

- La ablacion paga del prompt (`python -m evaluation.sensibilidad_ajustes prompt --brazo <brazo> --confirm-paid`) es el camino documentado; los dos brazos seleccionan los 69 casos escalados con `_casos_escalados_reales`, que construye el clasificador determinista real via `clasificador_con_vocabulario`.
- `preparar_entorno_offline()` (lineas ~104-109) recorre `ENTORNO_OFFLINE` y aplica `os.environ.setdefault(clave, valor)`. `ENTORNO_OFFLINE` incluye `GEMINI_API_KEY = "offline-dummy-key-sin-llamadas"`. La clave real vive SOLO en `App/Backend/.env`; pydantic-settings lee `env_file=".env"` relativo al CWD y prioriza `os.environ` sobre `.env` (`Settings`, `App/Backend/app/config/settings.py`). Resultado: en el camino pago, la clave ficticia queda en `os.environ` y `get_genai_client()` construye el cliente con ella; las 138 invocaciones de los dos brazos caen con `ClientError 400 API_KEY_INVALID`. <!-- gitleaks:allow -->
- `preparar_entorno_offline()` tambien es usada por caminos puramente offline (`clasificador_con_vocabulario`, `leer_punto_de_operacion`), que NO invocan al proveedor y necesitan valores inertes para que `Settings` construya sin credenciales. El arreglo NO puede romper estas rutas ni su reproducibilidad.
- `App/Backend/app/classifiers/__init__.py:1-4` importa `gemini_classifier` de forma anticipada. Importar `app.classifiers.deterministic` (lo hace la seleccion offline de casos) ejecuta el `__init__` del paquete, que importa `gemini_classifier` y congela `_PROMPT_TEMPLATE = _load_prompt()` con el prompt vigente. Cuando el harness fija `GEMINI_PROMPT_PATH` para el brazo `sin-reglas` (en `_prompt_cargado_por_el_backend`), el modulo ya esta cargado y el prompt sigue siendo el vigente; el gate de SHA-256 de `correr_brazo_prompt` rechaza el brazo.
- La suite de `evaluation/` tiene su propio `pytest.ini` y corre desde `evaluation/`. El fixture `entorno_backend` inyecta `ENTORNO_OFFLINE` con `monkeypatch.setenv`, por lo que cualquier cambio en esa estructura de datos afecta directamente a los tests.
- Governance BAJO/MEDIO: es el arnes de evaluacion, no codigo de produccion bajo `routes|services|repositories`.

### Referencias de lectura (Leer antes)

- `evaluation/sensibilidad_ajustes.py` (`preparar_entorno_offline`, `_cli_prompt`, `_prompt_cargado_por_el_backend`, `_construir_hybrid_real`, `correr_brazo_prompt`, `_casos_escalados_reales`).
- `App/Backend/app/classifiers/__init__.py`, `App/Backend/app/classifiers/gemini_classifier.py` (`_load_prompt`, `_PROMPT_TEMPLATE`, `get_genai_client`) y `App/Backend/app/config/settings.py`.
- `evaluation/tests/test_sensibilidad_ajustes.py` (Bloques 4, 8 y `entorno_backend`).
- `openspec/specs/evaluation-framework/spec.md` (requisito de la ablacion del prompt).
- `docs/Tesis/Correcciones/dictamen-correcciones.md` (entrada G0.7a) y `docs/Tesis/Correcciones/numeros-canonicos.md` (fila del nivel c).

## Goals / Non-Goals

**Goals:**

- Que el camino pago use la credencial real del proveedor resuelta desde `App/Backend/.env`, de modo que los comandos documentados de los dos brazos lleguen al proveedor.
- Que cada brazo cargue su propio prompt y el gate de SHA-256 lo acepte.
- Preservar sin cambios los caminos puramente offline y su reproducibilidad (sin credenciales, sin red).
- No alterar el comportamiento del clasificador de produccion ni su API publica.

**Non-Goals:**

- Implementar los cambios de codigo en esta fase (este change es solo de planificacion; el apply ejecuta los tasks).
- Cambiar el gate de confirmacion paga, el formato de salida de los brazos o el contrato de `comparar_brazos`.
- Incorporar un corpus nuevo, cambiar el corpus vigente o las caches oficiales.
- Cambiar las cinco cadenas canonicas de sector, los valores de `gemini-3.6-flash`, `requirements.txt` o `openspec/config.yaml`.
- Introducir un gestor de secretos externo o un `.env` nuevo: la fuente sigue siendo `App/Backend/.env`.

## Decisions

### D1 — El camino pago resuelve la credencial real; los caminos offline conservan sus valores inertes

El punto de entrada pago (`_cli_prompt`) resuelve `GEMINI_API_KEY` desde `App/Backend/.env` y la inyecta en `os.environ` —sobrescribiendo cualquier valor inerte previo— antes de construir el clasificador real, y limpia la cache de `get_settings()`. Si ni el entorno ni el archivo definen la credencial, el camino pago falla con un error claro ANTES de construir el clasificador y de cualquier invocacion. `preparar_entorno_offline` y `ENTORNO_OFFLINE` NO cambian: los caminos offline siguen completando los valores inertes con `setdefault` y nunca invocan al proveedor.

- **Alternativa A (descartada): quitar `GEMINI_API_KEY` de `ENTORNO_OFFLINE` y dejar que `Settings` lo cargue de `.env`.** Rompe la construccion offline cuando el CWD no es `App/Backend/` (los tests corren desde `evaluation/` y el fixture `entorno_backend` depende de `ENTORNO_OFFLINE`), y acopla el modo offline a la presencia de un `.env`.
- **Alternativa B (descartada): hacer que `preparar_entorno_offline` no fije nunca la credencial.** Deja la construccion offline de `Settings` sin `gemini_api_key` (campo obligatorio) y rompe la re-medicion offline; el arreglo tendria que rehacer los defaults offline.
- **Alternativa C (descartada): que `preparar_entorno_offline` detecte que corre en modo pago y omita la credencial.** Acopla un helper compartido al flujo pago y oculta la intencion; el punto de decision pertenece al camino pago, no al helper offline.
- **Elegida: resolucion explicita en el camino pago.** Es localizada, no toca los defaults offline (reproducibilidad intacta) y reutiliza la unica fuente de verdad documentada.

Lectura del `.env`: se usa el lector de `python-dotenv` (dependencia transitiva ya presente via pydantic-settings) para obtener el valor del archivo sin ejecutarlo ni imprimirlo. La credencial NUNCA se registra en logs ni se incluye en metadatos de la corrida.

### D2 — Import perezoso del paquete de clasificadores y carga del prompt por brazo

`App/Backend/app/classifiers/__init__.py` deja de importar `gemini_classifier` de forma anticipada: expone los mismos nombres publicos (`BaseClassifier`, `DeterministicClassifier`, `GeminiClassifier`, `HybridClassifier`) mediante un `__getattr__` de nivel de modulo (PEP 562) que importa el submodulo solo cuando se accede al nombre. Asi, importar `app.classifiers.deterministic` durante la seleccion offline de casos NO congela `_PROMPT_TEMPLATE`, y el harness puede fijar `GEMINI_PROMPT_PATH` para el brazo antes de que `gemini_classifier` se importe por primera vez. El harness mantiene el orden ya correcto de `_prompt_cargado_por_el_backend` (fijar `GEMINI_PROMPT_PATH`, limpiar la cache de `Settings`, importar `gemini_classifier`).

- **Alternativa A (descartada): recargar el modulo `gemini_classifier` desde el harness tras fijar la variable.** Depende de la semantica de `importlib.reload`, deja la importacion anticipada como trampa latente para cualquier otro importador y es fragil frente a referencias ya capturadas.
- **Alternativa B (descartada): pasar la ruta del prompt al constructor del clasificador.** Cambia la API del clasificador de produccion y su contrato con `Settings`; es un cambio mayor y fuera del alcance de una correccion del harness.
- **Elegida: import perezoso del paquete.** Elimina la causa raiz (el efecto colateral de importar el paquete) sin cambiar la API publica ni el comportamiento del clasificador.

Verificacion de que nada depende del import anticipado: `app.main` y los modulos que consumen `app.classifiers` usan los nombres publicos, que el `__getattr__` preserva; un test fija el contrato.

### D3 — TDD estricto sobre la suite de `evaluation/`

Cada defecto se corrige con un ciclo RED -> GREEN -> TRIANGULATE -> REFACTOR: primero una prueba que falla y describe el comportamiento esperado (camino pago con credencial real; brazo `sin-reglas` con su prompt), luego el minimo codigo para pasar, luego un segundo caso con insumos distintos, y por ultimo el refactor con la suite en verde. Se incluye una prueba de no regresion de los caminos offline. Las pruebas viven en `evaluation/tests/test_sensibilidad_ajustes.py` y se ejecutan con `cd evaluation && pytest tests/test_sensibilidad_ajustes.py -q`.

### D4 — El grupo final ejecuta la corrida ya autorizada y propaga el nivel c

Una vez en verde, el apply ejecuta los dos brazos por los comandos documentados (`cd App/Backend; PYTHONPATH=../.. python -m evaluation.sensibilidad_ajustes prompt --brazo vigente --confirm-paid` y `--brazo sin-reglas --confirm-paid`), cierra el reporte de sensibilidad offline pasando ambos archivos de brazo para que el nivel c se calcule, y propaga el valor a: `docs/Tesis/Correcciones/numeros-canonicos.md` (fila del nivel c), `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex`, `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` y la entrada G0.7a de `docs/Tesis/Correcciones/dictamen-correcciones.md`. La autorizacion de las 138 invocaciones ya fue concedida por el autor; el gate `--confirm-paid` permanece.

## Risks / Trade-offs

- [La credencial real termina en `os.environ` del proceso] -> Se lee una sola vez en el camino pago, nunca se registra en logs ni en metadatos; el proceso es efimero y la corrida ya exige la credencial.
- [El import perezoso cambia la semantica del paquete] -> Se preservan los nombres publicos con `__getattr__` y `__all__`; un test fija que `from app.classifiers import GeminiClassifier` sigue funcionando y que importar el paquete ya no carga `gemini_classifier`.
- [Romper la reproducibilidad offline al tocar `ENTORNO_OFFLINE`] -> Decision D1 no modifica `ENTORNO_OFFLINE` ni `preparar_entorno_offline`; una prueba de no regresion verifica que las rutas offline siguen inertes y sin red.
- [Un brazo vuelve a fallar por prompt] -> La prueba RED fija el comportamiento esperado del brazo `sin-reglas`; el gate de SHA-256 ya existe y sigue vigente.
- [Costo de la corrida paga] -> Acotado a 138 invocaciones ya autorizadas; el gate `--confirm-paid` no se retira.
- [Incoherencia entre documentos tras propagar el nivel c] -> La propagacion actualiza en el mismo change la fila del memo, la subseccion de resultados, la limitacion de discusion y la entrada del ledger, con la misma fuente (la linea del reporte de sensibilidad).

## Migration Plan

- **Codigo**: cambio en `evaluation/sensibilidad_ajustes.py` (D1, D4) y en `App/Backend/app/classifiers/__init__.py` (D2). Sin migraciones de base de datos ni cambios de esquema.
- **Pruebas**: nuevas pruebas de regresion en `evaluation/tests/test_sensibilidad_ajustes.py`; la suite completa de `evaluation/` debe quedar en verde.
- **Rollback**: revertir el commit restaura el comportamiento previo del harness; la corrida paga no se puede revertir, pero sus salidas son archivos propios ignorados por git y el reporte de sensibilidad es regenerable.
- **Governance**: BAJO/MEDIO; no se modifica codigo bajo `App/Backend/app/routes|services|repositories`.

## Open Questions

- Ninguna que cambie el diseno, las specs o los tasks. El punto sensible (si la credencial se resuelve leyendo `.env` o mediante otra via) se resuelve en D1: lectura con `python-dotenv`, sin preguntas diferidas.
