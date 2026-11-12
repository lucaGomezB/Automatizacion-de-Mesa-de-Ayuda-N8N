## Context

Ver `proposal.md` — Why. Hechos verificados en esta sesión (read-only):

- Los 14 SHAs de commit viejos resuelven como `commit` en este checkout SOLO porque los tags
  `v1.0.0`..`v1.2.7` y la rama `RamaLuca` siguen apuntando a la historia previa. Ninguno es ancestro
  de `HEAD` (`git merge-base --is-ancestor <sha> HEAD` falla para los 14). El criterio de "viejo vs
  nuevo" es la alcanzabilidad desde `HEAD`, NO la resolución de `git cat-file`.
- Cada par viejo→nuevo tiene el MISMO asunto de commit y el mismo árbol (mismo contenido, distinto
  SHA). Los 14 nuevos son ancestros de `HEAD`.
- Las 69 ocurrencias se reparten así: 3 + 9 + 12 + 6 + 1 + 2 (auditorías) + 6 + 6 (`.txt`) + 9 + 1 +
  2 + 4 + 8 (`evaluation/`) = 69. `procedencia.json` tiene 8: incluye la forma completa
  `7925903ab...` (línea 9) y `a76851e^ = 771b392d...` (dos en la línea 21).
- Los 9 SHAs de blob de `evaluation/` (`1daceb38`, `334a8edb`, `49267f4a`, `858f1c67`, `e69de29b`)
  resuelven como `blob` y son independientes del saneo de la historia de commits.
- Los `.txt` se generan con `pdftotext -enc UTF-8 main.pdf` (documentado en
  `dictamen-correcciones.md`, líneas 2588 y 2605). La fuente `.tex` (`12-anexos.tex`) ya fue
  remapeada por `ed4b386` (hoy tiene `bf5e099`), pero los `.txt` son instantáneas extraídas de un
  `main.pdf` anterior y conservan `d6bb474`.
- `verificar_matriz_trazabilidad.py` reporta `Filas: 256; avisos: 80; fallas: 4`: tres filas cuyo
  fragmento fue re-capitalizado/repuntuado por c-197 (`04-marco-metodologico.tex:14`,
  `10-recomendaciones.tex:18`, `02-marco-teorico.tex:32`) y la sección de c-197 sin matriz.
- Safety net de `evaluation/` (con `DIRECTORY_BLIND_INDEX_KEY` y las demás variables de CI):
  `test_sensibilidad_ajustes.py` 158 passed, `test_sensibilidad_corpus.py` 2 passed,
  `test_campana.py` 198 passed. Sin esas variables, 24 fallos PRE-EXISTENTES por `Settings`
  incompleto (no son fallos del repositorio).

## Goals / Non-Goals

**Goals:**
- Que las 69 citas de commit de los 13 archivos resuelvan a la historia saneada.
- Que `verificar_matriz_trazabilidad.py` reporte `fallas: 0` sin tocar el script.
- Actualizar código, tests y datos de `evaluation/` de forma coherente (Strict TDD).

**Non-Goals:**
- No tocar `App/`, `n8n/`, las fuentes `.tex`, `main.pdf`, los SHAs de blob ni el verificador.
- No recompilar la tesis ni regenerar los `.txt` (fuera de alcance; se remapea la instantánea).
- No reescribir historia de git ni mover tags.

## Decisions

- **D1 — Criterio de viejo vs nuevo por alcanzabilidad.** Se clasifica un SHA como "viejo" si NO es
  ancestro de `HEAD`, aunque `git cat-file -t` devuelva `commit` (los tags/rama viejos lo mantienen
  resoluble). Cada mapping se verifica comparando el asunto del commit viejo y el nuevo (idénticos).
  Alternativa descartada: clasificar por `cat-file` (daría "todos válidos" y no detectaría nada).
- **D2 — `evaluation/` bajo Strict TDD, código+tests juntos.** El safety net se corre ANTES (358
  tests verdes). Como los tests afirman los SHAs viejos (`test_campana.py` espera `d6bb474`;
  `test_sensibilidad_ajustes.py` espera `7925903`/`a76851e`), el ciclo es: (RED) actualizar la
  expectativa del test al SHA nuevo —falla porque el código/dato aún emite el viejo—; (GREEN)
  actualizar la constante/dato en `sensibilidad_ajustes.py` y `procedencia.json`; (TRIANGULAR) cubrir
  la forma corta y la de 40 hex (`7925903ab...`). Alternativa descartada: cambiar solo el código sin
  el test (lo dejaría en rojo y sin red de seguridad).
- **D3 — Los `.txt` se remapean como instantánea; la regeneración es la vía durable, diferida.** Los
  `.txt` son salida de `pdftotext` sobre `main.pdf`. La corrección durable es re-extraer tras
  recompilar el PDF, que este change NO hace (recompilar está fuera de alcance). Remapear la
  instantánea mantiene coherente la evidencia versionada; como `12-anexos.tex` ya tiene `bf5e099`,
  una futura re-extracción nacerá con el SHA nuevo. Se registra esta condición en el design y en las
  tareas.
- **D4 — `d6a7c13` (viejo tip de `main`) SÍ se remapea a `a5f36894`.** El objetivo es que toda cita
  resuelva a la historia vigente; dejar el viejo tip sería citar un commit no alcanzable. El par
  tiene el mismo asunto (`chore(engram): sincronizar la memoria del proyecto (cierre de sesion)`) y
  el mismo contenido: es la misma contribución re-escrita. Se documenta que el remapeo no afirma nada
  sobre el avance posterior de `main`.
- **D5 — SHAs de blob intactos.** Los 9 blobs (`1daceb38`, `334a8edb`, `49267f4a`, `858f1c67`,
  `e69de29b`) identifican contenido, no commits; el saneo no los altera. El test que valida
  `blob_git(b"") == "e69de29b..."` (hash del blob vacío) es prueba viva de que no deben tocarse.
- **D6 — Goal 2: alinear fragmento o marcar SUPERADA.** Para c-188 A2 y c-190 Res. 11.3 la sustancia
  del ítem sigue vigente y solo cambió la mayúscula inicial: se actualiza el fragmento a
  `El contrabalanceo planificado no se ejecutó` y `Que la revisión alcance a todos los canales, o a
  una muestra aleatoria de cada uno`, manteniendo `cerrada`. Para c-195 C1/13 el ítem era
  precisamente "minúscula tras el punto y coma" y c-197 convirtió el `;` en `.` mayusculando: el
  ítem quedó obsoleto, por lo que se marca `SUPERADA por c-197`. Alternativa descartada: marcar las
  tres SUPERADA (sería inexacto para A2 y Res. 11.3, cuya corrección sigue en pie).
- **D7 — Matriz nueva de c-197.** Se agrega una sección "Matriz de trazabilidad (verificada por
  `verificar_matriz_trazabilidad.py`)" a la sección de c-197, con filas que citan archivos y
  fragmentos reales: N-02 (`12-anexos.tex:239`/`:255`, `\label{tab:trazabilidad-revisiones}`) y N-07
  (medición de concisión en `docs/Tesis/Correcciones/sent_c197.py`). Los fragmentos y anclas se
  verifican contra el árbol antes de escribirlos (el propio verificador es la red).

## Risks / Trade-offs

- [Remapear un SHA con el mapping equivocado] → Cada par se verifica por igualdad de asunto de commit
  y alcanzabilidad de `HEAD`; se remapea el token completo, nunca un prefijo parcial.
- [Los tests de `evaluation/` dependen de variables de entorno] → El safety net se corre con las
  variables de CI (incluida `DIRECTORY_BLIND_INDEX_KEY`); sin ellas los fallos son pre-existentes y
  ajenos al change.
- [Los `.txt` quedan desincronizados de `main.pdf` hasta recompilar] → Aceptado y declarado: la
  instantánea se remapea; la regeneración depende de un `main.pdf` nuevo, fuera de alcance.
- [El fragmento de una fila de matriz no existe literalmente en la línea citada] → El verificador
  acepta desplazamiento con aviso; se apunta a la línea real y se evita `--estricto` como criterio de
  cierre (la tarea de cierre corre el script sin `--estricto`).

## Migration Plan

1. Safety net de `evaluation/` (3 archivos de test, verdes con env de CI).
2. Goal 2: alinear las 3 filas, marcar C1/13 SUPERADA, agregar la matriz de c-197; correr el
   verificador hasta `fallas: 0`.
3. Goal 1 `evaluation/`: RED de tests, GREEN de código/datos; re-correr los 3 archivos.
4. Goal 1 docs: remapear `auditorias/` y los `.txt`.
5. Cierre: `openspec validate --strict`; `git status --short` acota el alcance.
6. Rollback: revertir los archivos tocados; no hay migración de datos ni de runtime.
