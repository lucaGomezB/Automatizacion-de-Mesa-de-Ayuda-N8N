# Tasks: Corregir el sobreenmascarado del pseudonimizador (change c-201)

Convenciones: `T/` = `App/Backend/tests/test_pseudonymizer.py`; `P/` = `App/Backend/app/utils/pseudonymizer.py`; `S/` = `scripts/corpus_ingest/pseudonymize_corpus.py`; `C/` = `data/Corpus Tesis - Hoja 1 (pseudonimizado).csv`; `J/` = `data/corpus_evaluacion_pseudonimizado.json`. "D-n" remite a `design.md`.

**Reglas para todos los grupos.** No commitear, no pushear, no crear tags. No ejecutar ninguna corrida paga de Gemini. No modificar `app/classifiers/`, `docs/prompt_gemini.txt`, `app/constants.py`, `J/` ni archivos `.tex` de la tesis. Toda tarea de código sigue el ciclo TDD: primero el test que falla (RED), después la implementación mínima (GREEN), después la triangulación y el refactor, con la suite en verde en cada paso. Reportar la evidencia de RED y GREEN, no solo el resultado final.

**Skills del registro** (`.agents/SKILLS.md`): cargar `python-testing-patterns` antes de escribir tests y `python-design-patterns` antes de refactorizar. Gobernanza: ALTO/CRITICO (PII y seguridad). Restricción dura: el change solo puede reducir falsos positivos; si un test de PII genuina deja de pasar, detener y reportar.

## 1. Red de seguridad y auditoría previa

- [x] 1.1 Registrar el baseline de la suite del pseudonimizador: `cd App/Backend && pytest tests/test_pseudonymizer.py -q` y, desde la raíz, `pytest scripts/corpus_ingest/test_pseudonymize_corpus.py -q`. Anotar el número de tests en verde. Si algo falla antes de tocar código, detener y reportarlo como fallo pre-existente (no corregirlo en este change).
- [x] 1.2 Auditar referencias al CSV y hashes: `rg -n "Corpus Tesis - Hoja 1 \(pseudonimizado\)" --glob '!*.csv' .`; `rg -n "sha-?256|SHA-?256" data/README.md evaluation/data/campana/README.md`. Confirmar que ningún test afirma el contenido ni el SHA-256 del CSV, y que los hashes existentes corresponden a artefactos que este change no modifica. Registrar la conclusión en el reporte del apply. Aceptación: la auditoría queda documentada y no se edita ningún hash.

## 2. RED — tests de los falsos positivos observados

- [x] 2.1 Agregar a `T/` un test parametrizado para determinante más palabra no-persona: `"Su PC se reinicia a cada rato"`, `"La PC no le responde"`, `"El ID del equipo es 42"` y `"Las Heras"`. Aceptación: cada caso conserva la subcadena original, no contiene `[PERSONA]` y el conteo `persona` es cero. Ejecutar y confirmar que falla hoy (RED).
- [x] 2.2 Agregar a `T/` un test parametrizado para productos, áreas, frases de error y topónimos: `Adobe PDF Reader`, `Microsoft Vision`, `NET Framework`, `Recursos Humanos`, `Acceso Denegado`, `San Juan`, `Casa Matriz`, `Rio Negro` y `Cordoba Capital`, cada uno dentro de una oración realista. Aceptación: la frase se conserva, no se inserta `[PERSONA]` y el conteo `persona` es cero. Ejecutar y confirmar los fallos esperados (RED).
- [x] 2.3 Agregar a `T/` un test para la variante acentuada de sector: `"Clasificado como Seguridad Informática por el modelo"`. Aceptación: `Seguridad Informática` se conserva, no hay `[PERSONA]` y el conteo es cero. Ejecutar y confirmar que falla hoy (RED).
- [x] 2.4 Registrar la salida RED de 2.1 a 2.3 (tests que fallan y motivo) antes de escribir código de producción.

## 3. GREEN — implementación mínima

- [x] 3.1 En `P/`, agregar `_DETERMINANTES` y la regla de D1 en `_replace_persona`: si el primer token es determinante, separarlo, evaluar el resto con las reglas existentes y conservar el determinante; preservar cuando el resto es una sola palabra o está excluido. Aceptación: el test de 2.1 pasa y el conteo `persona` es cero para los cuatro casos.
- [x] 3.2 En `P/`, normalizar la comparación de sectores con `unicodedata` (NFKD, sin combinantes, minúsculas) según D2. Aceptación: el test de 2.3 pasa sin tocar `app/constants.py`.
- [x] 3.3 En `P/`, ampliar la allowlist con las frases de D3 y hacer la comparación de frases insensible a tildes. No agregar tokens ambiguos (`Reader`, `Vision`, `Framework`) al mecanismo de composición por tokens. Aceptación: el test de 2.2 pasa para las nueve frases.
- [x] 3.4 Ejecutar `cd App/Backend && pytest tests/test_pseudonymizer.py -q` y confirmar que todos los tests, incluidos los preexistentes, pasan (GREEN).

## 4. TRIANGULATE — regresiones de PII genuina y refactor

- [x] 4.1 Agregar a `T/` regresiones de nombres reales junto a determinantes: `"La PC de Juan Pérez no responde"` debe conservar `La PC` y enmascarar `Juan Pérez`; `"El usuario Juan Pérez reportó el problema"` y `"María Núñez"` deben seguir produciendo `[PERSONA]`. Aceptación: los tres casos pasan y el conteo `persona` es al menos uno.
- [x] 4.2 Agregar a `T/` una regresión combinada con PII genuina: nombre con tilde, email, teléfono argentino, host interno y tarjeta con disparador contextual. Aceptación: cada valor original desaparece, cada etiqueta aparece y los conteos por categoría reflejan cada reemplazo; si este test falla, detener el change.
- [x] 4.3 Triangular los casos de 2.1 a 2.3 con variantes: determinante en minúscula dentro de oración, frase con tilde (`Río Negro`, `Córdoba Capital`), sector acentuado distinto de `Seguridad Informática` y una oración que mezcle una frase preservada con un nombre real. Aceptación: todos pasan y no hay regresiones.
- [x] 4.4 Refactorizar sin cambiar comportamiento: extraer helpers para normalización de tildes y para la decisión de persona; parametrizar tablas de tests repetidas. Aceptación: la suite sigue completamente verde después de cada paso de refactor.

## 5. Regeneración del CSV y equivalencia con el corpus evaluado

- [x] 5.1 Regenerar el CSV con el script canónico: `python scripts/corpus_ingest/pseudonymize_corpus.py --out "data/Corpus Tesis - Hoja 1 (pseudonimizado).csv"`. Aceptación: exit code 0, 0 email residual y 0 teléfono residual en la salida del script.
- [x] 5.2 Verificar que el CSV regenerado no tiene etiquetas de persona ni de teléfono y que coincide con `J/` en las 200 descripciones ignorando espacios finales. Aceptación: un script de comparación por `ID` reporta 0 `[PERSONA]`, 0 `[TELEFONO]` y 0 diferencias contra `J/`.
- [x] 5.3 Verificar que no se tocaron las fuentes: `git diff --exit-code -- "data/Corpus Tesis - Hoja 1.csv" data/corpus_evaluacion_pseudonimizado.json`. Aceptación: exit code 0.
- [x] 5.4 Revisar el diff del CSV: solo se eliminan las 9 etiquetas (8 `[PERSONA]` y 1 `[TELEFONO]`); se conservan las 200 filas, las columnas y el fin de línea CRLF (202 ocurrencias de CRLF). Aceptación: `git diff --stat` y la revisión del diff no muestran cambios de estructura ni de codificación.

## 6. Documentación de la frontera

- [x] 6.1 Actualizar `docs/pseudonymization.md`: documentar qué se enmascara (nombres reales de 2+ palabras, email, teléfono, host, tarjeta) y qué no (determinantes, productos, áreas, frases de error, topónimos listados), la regla del determinante inicial (D1), la exclusión de sectores insensible a tildes (D2), la allowlist ampliada (D3) y la limitación residual de topónimos no listados (D4).
- [x] 6.2 Agregar en `docs/pseudonymization.md` una nota explícita de que las métricas reportadas no cambian: el corpus evaluado ya es la salida del módulo corregido y repetir la corrida es un no-op (D6). Aceptación: `rg -n "determinante|insensible a tildes|no cambian|no-op" docs/pseudonymization.md` devuelve al menos una coincidencia por concepto.

## 7. Verificación final y registro

- [x] 7.1 Ejecutar SOLO los tests relevantes del change: `cd App/Backend && pytest tests/test_pseudonymizer.py tests/test_pseudonymization_integration.py -q` y, desde la raíz, `pytest scripts/corpus_ingest/test_pseudonymize_corpus.py -q`. Por indicación del usuario NO se ejecuta la suite completa del backend. Si falta una variable de entorno, usar los dummies de CI documentados en `AGENTS.md` y reportarlo. Evidencia: 72 passed (`test_pseudonymizer.py` + `test_pseudonymization_integration.py`) y 13 passed (`test_pseudonymize_corpus.py`).
- [x] 7.2 Ejecutar `openspec validate c-201-corregir-el-sobreenmascarado-del-pseudonimizador --strict`. Evidencia: válido.
- [x] 7.3 Registrar el change en `CHANGES.md` con su fase, estado, scope, dependencias, gobernanza y "Leer antes". Evidencia: registrado como FASE 64 (`rg -n "c-201|corregir-el-sobreenmascarado" CHANGES.md` devuelve coincidencias).
- [x] 7.4 Verificación de alcance: `git status --porcelain` debe mostrar solo `P/`, `T/`, `C/`, `docs/pseudonymization.md`, `CHANGES.md` y los artefactos del change. Evidencia: confirmado; no cambiaron `app/classifiers/`, `docs/prompt_gemini.txt`, `app/constants.py`, `J/` ni archivos `.tex`.