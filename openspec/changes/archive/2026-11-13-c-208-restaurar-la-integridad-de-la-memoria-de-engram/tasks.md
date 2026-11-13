# Tasks: Restaurar la integridad de la memoria de Engram (change c-208)

Convenciones: `G/` = `scripts/security/check_engram_chunk_integrity.py`; `TG/` = `scripts/security/test_check_engram_chunk_integrity.py`; `R/` = `scripts/security/reexport_missing_engram_data.py`; `W/` = `.github/workflows/ci.yml`; `N/` = la nota canonica de la memoria (por ejemplo `docs/engram-memory.md`). "D-n" remite a `design.md`.

**Reglas para todos los grupos.** No commitear, no pushear, no crear tags. NUNCA editar ni borrar un chunk de `.engram/chunks/`; toda correccion es append-only. NUNCA ejecutar `engram sync --all` ni reescribir el historial de git. NUNCA imprimir secretos ni el nombre real de un colaborador. Toda tarea de codigo sigue el ciclo TDD: primero el test que falla (RED), despues la implementacion minima (GREEN), despues la triangulacion y el refactor, con la suite en verde en cada paso. Reportar la evidencia de RED y GREEN, no solo el resultado final.

**Skills del registro** (`.agents/SKILLS.md`): cargar `python-testing-patterns` antes de escribir tests y `python-design-patterns` antes de refactorizar. Gobernanza: ALTO (integridad de la evidencia de auditoria y guardas de seguridad). Restriccion dura: si alguna tarea exigiera editar un chunk existente, detener y reportar; el arreglo es append-only.

## 1. Red de seguridad y auditoria previa

- [x] 1.1 Registrar el baseline: `ls .engram/chunks/*.jsonl.gz | wc -l` (contar los chunks) y correr la deteccion de integridad sobre la memoria real (union de observaciones, mutaciones de relacion, referencias colgantes). Anotar el numero de referencias colgantes. Si el baseline no es 0 colgantes, detener y reportarlo (el arreglo puntual `04f7cd5` ya deberia haber dejado 0).
- [x] 1.2 Auditar invariantes: `git check-ignore .engram` (no debe imprimir nada), `git status --porcelain .engram` y confirmar que `.engram/` no figura en `.gitignore`. Registrar la conclusion: los chunks son inmutables y el arreglo sera append-only.

## 2. RED — tests de la guarda con fixtures sinteticos

- [x] 2.1 Agregar a `TG/` un fixture que construya chunks `.jsonl.gz` sinteticos sanos (una observacion y una relacion que la referencia) y un test que afirme exit 0 y 0 referencias colgantes. Ejecutar y confirmar que falla hoy porque la guarda no existe (RED).
- [x] 2.2 Agregar a `TG/` un fixture con una relacion `upsert` cuyo `target_id` NO existe como observacion en ningun chunk; el test debe afirmar exit distinto de cero y que el mensaje nombre la relacion y el extremo faltante. Ejecutar y confirmar el fallo esperado (RED).
- [x] 2.3 Agregar a `TG/` casos de triangulacion: un chunk sin `mutations`, un chunk con `mutations` nulo, una relacion con `op != "upsert"` (no debe exigir la observacion) y varias relaciones en el mismo chunk. Confirmar los fallos esperados (RED).
- [x] 2.4 Registrar la salida RED de 2.1 a 2.3 (tests que fallan y motivo) antes de escribir el codigo de la guarda.

## 3. GREEN — implementacion minima de la guarda

- [x] 3.1 Implementar `G/` en Python de solo biblioteca estandar (`gzip`, `json`, `sqlite3`, `tempfile`, `argparse`, `pathlib`): descomprimir cada `.jsonl.gz`, recolectar los `sync_id` de observaciones, crear una base SQLite temporal con la tabla de observaciones y la de relaciones con FK, y aplicar las mutaciones de relacion `upsert`. Aceptacion: el fixture de 2.1 pasa (GREEN).
- [x] 3.2 Hacer que una FK violada produzca exit distinto de cero con un mensaje accionable (relacion y extremo faltante). Aceptacion: el fixture de 2.2 pasa.
- [x] 3.3 Tratar `mutations` ausente/nulo como lista vacia y validar solo `op == "upsert"`. Aceptacion: los casos de 2.3 pasan.
- [x] 3.4 Ejecutar `TG/` completo y confirmar que pasa en su totalidad (GREEN). Correr la guarda sobre `.engram/` real y confirmar exit 0 con 0 colgantes (D1).

## 4. TRIANGULATE y refactor

- [x] 4.1 Triangular con un chunk que referencia una observacion presente en OTRO chunk (la union de todos los chunks debe satisfacer la FK), y con una relacion cuyo `source_id` (no el `target_id`) falta. Aceptacion: ambos pasan.
- [x] 4.2 Refactorizar sin cambiar comportamiento: extraer helpers para parsear chunk, recolectar observaciones y aplicar mutaciones; parametrizar la construccion de fixtures. Aceptacion: la suite sigue verde tras cada paso.

## 5. Cableado de la guarda al pipeline

- [x] 5.1 En `W/`, agregar el paso que corre la guarda (`python3 scripts/security/check_engram_chunk_integrity.py .engram`) dentro del job `secret-scan` (D2). Aceptacion: el paso usa solo el repo y no agrega referencias a `secrets.*`.
- [x] 5.2 Verificar la politica: la guarda es bloqueante (un colgante hace fallar el job) y corre offline. Aceptacion: el YAML parsea y el paso no depende de red ni de credenciales.

## 6. Recuperacion append-only de los datos omitidos

- [x] 6.1 Implementar/documentar `R/`: detectar (solo lectura) el conjunto de observaciones y prompts del proyecto ausentes en la union de los chunks y reportar su conteo. Aceptacion: sobre la base local, el reporte coincide con la medicion de la auditoria (36 observaciones y 106 prompts en el estado de partida; el numero exacto puede variar tras el arreglo de otras sesiones).
- [x] 6.2 Agregar el modo de reparacion que adelanta `updated_at` SOLO de las filas estrictamente faltantes y re-ejecuta `engram sync --project` (nunca `--all`). Aceptacion: se produce un chunk NUEVO; ningun chunk previo se modifica; el contenido no cambia.
  - Nota (2026-11-13, ejecutado): con autorizacion explicita de las autoras y los autores. Deteccion previa: 49 observaciones y 130 prompts ausentes. `--repair --confirm-publish` adelanto `updated_at` en 49 observaciones (respaldo en `/tmp/opencode/engram-db.pre-c208.bak`) y produjo el chunk NUEVO `4ede70f7` (1 sesion, 49 observaciones, 2 prompts). Ningun chunk previo se modifico ni se borro; el manifest solo agrego una entrada.
- [x] 6.3 Verificar la recuperacion: la deteccion posterior reporta 0 ausentes y la guarda reporta 0 colgantes sobre la memoria resultante; el import en un entorno limpio no falla (D4).
  - Nota (2026-11-13, verificado): deteccion posterior 0 observaciones ausentes (128 prompts siguen ausentes: `user_prompts` no tiene `updated_at`, fuera del alcance de este mecanismo). Guarda sobre 166 chunks: 0 referencias colgantes. Import en `ENGRAM_DATA_DIR` limpio: exit 0, 166 chunks aplicados sin el error de FK. `git status` solo muestra el chunk NUEVO y la entrada agregada al manifest.
- [x] 6.4 Confirmar que `R/` no imprime contenido de memoria ni nombres reales y que los guards existentes siguen corriendo en `.githooks/pre-commit`.

## 7. Documentacion y correccion de la nota tecnica

- [x] 7.1 Crear `N/` con: version en uso (Engram 1.20.0, manifest v1); decision de no actualizar a 3.x por ahora con su motivo; mecanismo del defecto (`lastChunkTime` global) y su mitigacion (guarda de CI + recuperacion append-only); invariantes duras (append-only, `.engram/` nunca gitignored, `--all` prohibido).
- [x] 7.2 En `N/`, dejar la afirmacion EXACTA sobre Engram v3.7.1: acepta el manifest v1 y lo migra a v2 al exportar cuando hay sesiones propias del proyecto; rechaza ciertas DEGRADACIONES, no el v1 como un todo (D6). Aceptacion: `rg -n "v1|v2|migra|degradacion" N/` muestra la afirmacion correcta y no existe la frase de que v3 rechaza el v1 como un todo.
- [x] 7.3 Enlazar `N/` desde `README.md` (seccion de memoria de Engram) y desde `AGENTS.md` (seccion de memoria de Engram). Aceptacion: ambos apuntan a `N/`.

## 8. Verificacion final y registro

- [x] 8.1 Ejecutar SOLO los tests relevantes del change: `python3 -m pytest scripts/security/test_check_engram_chunk_integrity.py -q` y la guarda sobre `.engram/` real. Si falta una variable de entorno, usar los dummies de CI de `AGENTS.md` y reportarlo.
- [x] 8.2 Ejecutar `openspec validate c-208-restaurar-la-integridad-de-la-memoria-de-engram --strict`. Evidencia: valido.
- [x] 8.3 Registrar el change en `CHANGES.md` con su fase, estado, scope, dependencias, gobernanza y "Leer antes". Evidencia: `rg -n "c-208|integridad-de-la-memoria-de-engram" CHANGES.md` devuelve coincidencias.
- [x] 8.4 Verificacion de alcance: `git status --porcelain` debe mostrar solo `G/`, `TG/`, `R/`, `W/`, `N/`, `README.md`, `AGENTS.md`, `CHANGES.md`, `.engram/` (chunk nuevo) y los artefactos del change. Confirmar que no se edito ni borro ningun chunk preexistente (`git diff --name-only --diff-filter=D -- .engram/chunks` vacio; `git diff --name-only -- .engram/chunks` sin archivos existentes modificados).
