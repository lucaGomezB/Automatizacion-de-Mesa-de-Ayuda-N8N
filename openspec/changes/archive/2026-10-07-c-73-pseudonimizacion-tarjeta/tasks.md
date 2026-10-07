# Tasks: pseudonimizacion de numeros de tarjeta hablados

Modo TDD estricto. Cada bloque de comportamiento sigue RED -> GREEN -> TRIANGULATE -> REFACTOR.
Archivo de tests: `App/Backend/tests/test_pseudonymizer.py`. Comando: `cd App/Backend; pytest tests/test_pseudonymizer.py -v`.

## 1. Safety net y contrato

- [x] 1.1 Ejecutar la suite existente del pseudonimizador y capturar la linea base (`cd App/Backend; pytest tests/test_pseudonymizer.py -v`); verificar que todos los tests pasan antes de tocar codigo. Si hay fallos, reportarlos como preexistentes y no continuar.
- [x] 1.2 Identificar las aserciones que comparan el dict `conteos` completo (`test_pseudonymize_texto_sin_pii_devuelve_texto_intacto_y_conteos_en_cero`) y verificar que seran actualizadas al agregar la clave `tarjeta`.

## 2. RED — categoria CARD con disparador contextual

- [x] 2.1 Escribir en `test_pseudonymizer.py` un test que afirme que `pseudonymize("mi tarjeta numero 4517 6712 3456 7890 vencio", [])` produce `[TARJETA]`, no deja ningun digito de la tarjeta y `conteos["tarjeta"] == 1`; verificar que FALLA contra el codigo actual (RED).
- [x] 2.2 Escribir el test de la forma contigua `"Hola, mi tarjeta es 0102301239999320 y no puedo operar"`; verificar que FALLA (RED).
- [x] 2.3 Escribir el test de la forma con guiones `"4517-6712-3456-7890"` con contexto; verificar que FALLA (RED).

## 3. GREEN — implementacion minima

- [x] 3.1 Agregar `_LABEL_TARJETA = "[TARJETA]"`, la constante `_CARD_CONTEXT_WINDOW_CHARS = 40` y el patron `_RE_TARJETA` (disparador `tarjetas?` + ventana lazy + grupo de numero 4-4-4-4 o 16 contiguos con bordes de digito) en `app/utils/pseudonymizer.py`; verificar que los tests 2.1-2.3 pasan (GREEN).
- [x] 3.2 Inicializar `conteos["tarjeta"] = 0` y aplicar `_RE_TARJETA` con una funcion de reemplazo que preserve el disparador y sustituya solo el numero, ANTES de `_RE_TELEFONO`; verificar que los tests 2.1-2.3 siguen en GREEN.
- [x] 3.3 Actualizar el dict esperado en `test_pseudonymize_texto_sin_pii_devuelve_texto_intacto_y_conteos_en_cero` para incluir `"tarjeta": 0`; verificar que el test pasa.

## 4. TRIANGULATE — cobertura de escenarios del spec

- [x] 4.1 Test de la etiqueta exacta en mayusculas `[TARJETA]` (sin variantes) sobre un caso con contexto; verificar que pasa.
- [x] 4.2 Test parametrizado de variantes de disparador (`tarjeta de credito`, `tarjeta de debito`, `numero de tarjeta`, plural `tarjetas`) con un numero de 16 digitos en ventana; verificar que cada variante produce `[TARJETA]` y conteo 1.
- [x] 4.3 Test de ventana: numero de 16 digitos ubicado a mas de 40 caracteres del disparador (sin nueva mencion) NO se enmascara y `conteos["tarjeta"] == 0`; verificar que pasa.
- [x] 4.4 Test de numero de 16 digitos SIN mencion de "tarjeta" que NO se enmascara; verificar `[TARJETA]` ausente y conteo 0.
- [x] 4.5 Test de orden: el numero de tarjeta con contexto no se fragmenta como `[TELEFONO]` (`conteos["telefono"] == 0` y sin remanentes de digitos); verificar que pasa.
- [x] 4.6 Test de determinismo extendido: dos invocaciones con contexto de tarjeta devuelven el mismo texto y los mismos conteos, incluida la clave `tarjeta`; verificar que pasa.
- [x] 4.7 Test de combinacion de categorias: texto con nombre, email, telefono, tarjeta con contexto y host; verificar cada etiqueta y cada conteo por categoria.

## 5. No regresion del corpus

- [x] 5.1 Test R067: `pseudonymize("Le sale un cartel \"Falta el dll axm0102301239999320002302\" al intentar iniciar el sistema principal", [])` NO contiene `[TARJETA]` y `conteos["tarjeta"] == 0`; verificar que pasa (no se altera el comportamiento preexistente de las otras categorias).
- [x] 5.2 Test R169: `pseudonymize("Tiene problemas al dar de alta una tarjeta", [])` devuelve el texto identico, `conteos["tarjeta"] == 0` y ninguna etiqueta de tarjeta; verificar que pasa.

## 6. REFACTOR y documentacion

- [x] 6.1 Refactorizar nombres/constantes si hace falta sin cambiar comportamiento; ejecutar `pytest tests/test_pseudonymizer.py -v` despues de cada paso y verificar que todo sigue en verde.
- [x] 6.2 Actualizar el docstring del modulo y el de `pseudonymize` (lista de categorias, etiquetas y orden de aplicacion) para incluir `[TARJETA]`; verificar que no quedan referencias a 4 categorias en el modulo.
- [x] 6.3 Actualizar `App/Backend/tests/test_pseudonymization_integration.py` si alguna asercion compara el dict de conteos; verificar que la suite de integracion relevante pasa.
- [x] 6.4 Ejecutar la suite completa del backend (`cd App/Backend; pytest -m "not integration"`) y verificar que no hay regresiones.

## 7. Validacion del change

- [x] 7.1 Ejecutar `openspec validate c-73-pseudonimizacion-tarjeta --strict` y verificar que PASA.
- [x] 7.2 Revisar que ningun string canonico de sector ni `evaluation/corpus.py::_a_float` fue modificado; verificar con `git diff --name-only`.