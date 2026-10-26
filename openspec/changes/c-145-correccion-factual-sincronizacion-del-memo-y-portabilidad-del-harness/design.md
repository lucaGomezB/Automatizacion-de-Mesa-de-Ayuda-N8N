## Context

Ver `proposal.md` (Why). Estado verificado en el arbol de trabajo (2026-10-26, rama `change/c-145-...`, base `origin/ramagonzalo` en `78d11f1`):

- **A1.** `06-implementacion.tex:87` afirma "16 tests con un mecanismo de omisión automática (`pytest.skip`)". `cd App/Backend && pytest -m integration --collect-only -q` devuelve 48 pruebas sobre 1510. `App/Backend/tests/conftest.py:291` documenta "FALLA RUIDOSAMENTE (D2), nunca skip"; los unicos `pytest.skip` de `App/Backend/tests/` estan en `test_openapi_sync.py` y no se refieren a PostgreSQL. Causa raiz: la oracion nacio en `a0436e0` (C-19, 2026-07-03, commit que agrego 16 pruebas con skip); `ef656ac` (2026-09-17, c-29/c-30/c-32) cambio `conftest.py` a fallo ruidoso; la copia a v9 (`8466cbe`) y a v10 (`7408543`) arrastro la oracion sin actualizarla. Es un defecto preexistente en `main`, no introducido por el PR #40.
- **A2.** `06-implementacion.tex:91` congela "357 pruebas ... 56 archivos". `find "App/Frontend/src" -type f \( -name '*.test.ts' -o -name '*.test.tsx' \) | wc -l` devuelve 59 archivos. El worktree no tiene `App/Frontend/node_modules`, de modo que la suite no se puede ejecutar sin `npm install`, prohibido en esta fase.
- **A3.** `06-implementacion.tex:44` y `:54` citan "decisión OQ1 = A del change c-72" y "decisión OQ2 = A del change c-72". El Anexo I ya existe (`sec:anexo-trazabilidad`) pero mapea recomendaciones del dictamen, no decisiones internas de changes.
- **B1.** `04-marco-metodologico.tex:51` publica `6,66 %` con `N ≈ 2.646`; `numeros-canonicos.md:832` y `:732` conservan `6,74 %` con `N = 3.700`. Verificacion aritmetica: `n₀ = z²p(1−p)/e²`, `n = n₀/[1+(n₀−1)/N]`; con `e = 0,0666` y `N = 2646` da `200,21 ≈ 200`; con `6,74 %` da `195,8`. El valor de la tesis es correcto y el memo esta desactualizado.
- **B2.** `numeros-canonicos.md:119-120` y `:550` citan `07-resultados.tex:129` y `:75`; en el arbol actual el parrafo esta en `:128` y el dato en `:74`. El archivo ya no tiene CR suelto. Un barrido completo muestra mas deriva: la tabla de bandas esta en `:166-187` (el memo cita `:167-188`), el tramo `>= 0,90` esta en `:189` (correcto), y las filas `9,5 %` citan `:160`, donde ya no aparece el valor retirado.
- **C1.** `08-discusion.tex:10` cita `97/131 (0,7405)` junto a Gemini `88/130 (0,6769)`. El valor pareado canonico es `96/130 = 0,7385` (`numeros-canonicos.md:460`, `report_sensibilidad_ajustes.md:81`).
- **C2.** `08-discusion.tex:95` cita "+52,1 y +62,0 en el central"; el memo registra tres celdas `+42,1 / +52,1 / +62,0` (`numeros-canonicos.md:585`).
- **D1.** `dictamen-correcciones.md:140` contiene `### P4. (a completar)`.
- **E1.** `evaluation/sensibilidad_ajustes.py:1180-1204` define `--brazo-vigente` y `--brazo-sin-reglas` en el parser superior y `--brazo` en el subparser `prompt`. En Python 3.12.3 la suite de `evaluation/` da **4 failed, 448 passed, 1 skipped**; los 4 fallos son del CLI y el error es `ambiguous option: --brazo could match --brazo-vigente, --brazo-sin-reglas`. En Python 3.12.15 (CI) pasan.
- **F1.** `main.pdf` = 109 paginas (`pdfinfo`); `main.toc:96` ubica `Anexos` en la pagina 101, luego cuerpo = 100, anexos = 9. La regla adoptada el 2026-10-26 es cuerpo sin anexos <= 100, anexos sin limite, con margen 0. El cuerpo esta exactamente en el limite.
- **F2.** `v1.2.0` es anotado, publicado, apunta a `a49d035c67b32ae17e633ec04b09ecdd2781aac6` (C1). `12-anexos.tex:27-29` declara `v1.2.0` y el hash de C1; C2 (`3bd0a53`) escribio ese hash. El texto corregido no sera C1.
- **Entorno.** Docker `texlive-thesis:latest` existe y es el entorno de registro de c-141 (`latexmk main.tex`). Python local 3.12.3; CI 3.12.15.

## Goals / Non-Goals

**Goals:**

- Que el texto de la release afirme solo lo que el repositorio reproduce (A1, A2) y que no filtre identificadores internos al cuerpo (A3).
- Que el memo canonico sea la fuente unica tambien para el margen de error y que sus referencias de linea resuelvan (B1, B2).
- Que la discusion use denominadores comparables y no omita celdas canonicas (C1, C2).
- Que el CLI de sensibilidad sea portable entre parches de Python 3.12 (E1) y que su error de reporte ausente sea limpio (E2-i).
- Publicar una release de correccion sin mover `v1.2.0` y sin desbordar el tope de paginas (F).

**Non-Goals:**

- No re-investigar el dictamen CONEAU ni reabrir las correcciones de la FASE 36.
- No re-ejecutar el clasificador, Gemini, N8N ni Twilio; no se generan valores numericos nuevos.
- No reescribir el memo entero ni renumerar sus secciones 3.1 a 3.12.
- No agregar la procedencia de las caches de predicciones al reporte de sensibilidad (E2-ii, ver D8).
- No instalar dependencias de frontend ni ejecutar la suite de Vitest en esta fase.
- No tocar `App/`, `n8n/`, `data/`, el corpus ni los tags `v1.0.0`..`v1.2.0`.

## Decisions

### D1 - Orden de aplicacion y unidad del change

Orden: (1) bloques E y H (codigo, pruebas y barrera ejecutable); (2) bloques D y G (higiene del registro y documentacion para agentes); (3) bloque B (memo); (4) bloques A y C (tesis); (5) recompilacion y medicion de paginas (F1/F3); (6) release `v1.2.1` (F2); (7) cierre documental (F4).

El bloque E va primero porque su suite es la red de seguridad del resto y porque el baseline debe quedar registrado con el interprete local. B va antes que A/C porque A/C consumen valores del memo y porque la correccion de referencias debe hacerse sobre el texto ya editado. F va al final porque mide y etiqueta el resultado integrado.

**Por que un solo change y no dos (E separado):** los bloques A/B/C/F comparten el mismo artefacto publicable y el mismo PR bloqueado; separarlos exigiria dos recompilaciones, dos releases o una release intermedia con el texto aun falso. El bloque E es pequeno (una linea de parser, una rama de error y pruebas) y su prueba de regresion debe viajar en el mismo commit que el arnes para que la evidencia de reproducibilidad de la release sea valida. El cambio sigue siendo acotado: un archivo de codigo, uno de runner, un archivo de pruebas, dos `.tex`, dos documentos de registro y artefactos de compilacion.

**Alternativa considerada:** publicar primero `v1.2.1` solo con A/B/C y dejar E para un change posterior. Se descarta porque el PR #40 seguiria bloqueado hasta la segunda release y porque la verificacion de la release se correria en un interprete distinto del documentado, sin la prueba que fija el comportamiento.

**Integracion en la rama del PR (paso obligatorio).** C3 y C4 se crean en `change/c-145-...`, la rama de este change, cortada de `origin/ramagonzalo` en `78d11f1`. Cerrada la release, esa rama se fusiona con `git merge --no-ff` en `ramagonzalo` y se publica con `git push origin ramagonzalo` (checkpoint ALTO, con confirmacion explicita del usuario). Sin ese paso el PR #40 no cambia: publicar solo la rama del change dejaria el tag `v1.2.1` fuera del PR y la verificacion `git merge-base --is-ancestor v1.2.1 origin/main` fallaria despues del merge, con lo que la release dejaria de ser trazable desde `main`. Es el mismo patron que uso c-141 con las ramas `change/*` de la FASE 36. La rama del change se publica solo si el usuario lo pide; el requisito es que `ramagonzalo` contenga C3 y C4 antes de actualizar el PR.

### D2 - A1: redaccion de la correccion y causa raiz

Reemplazar la clausula de `06-implementacion.tex:87` por una que declare el recuento real y el comportamiento real, por ejemplo: "mediante 48 pruebas marcadas como integracion, que fallan de forma ruidosa si PostgreSQL no esta disponible en lugar de omitirse". El numero 48 se obtiene del comando `cd App/Backend && pytest -m integration --collect-only -q` y se registra en el REGISTRO con la salida. No se agrega una lista de archivos ni se fija un numero de pruebas por archivo, para no crear otro valor que se desactualice.

La causa raiz se consigna en el REGISTRO con los dos commits y la cadena de copia:

| Hecho | Commit | Fecha | Efecto |
|---|---|---|---|
| Se agregan 16 pruebas de integracion PostgreSQL con omision automatica | `a0436e0` (C-19) | 2026-07-03 | Nace la oracion "16 tests ... pytest.skip" |
| `conftest.py` pasa a fallo ruidoso y la suite crece | `ef656ac` (c-29/c-30/c-32) | 2026-09-17 | La oracion queda obsoleta |
| Copia de trabajo v9 | `8466cbe` | 2026-10-01 | Arrastra la oracion |
| Copia de trabajo v10 | `7408543` (c-122) | 2026-10 | La publica en v10 |

**Alternativa considerada:** corregir solo la cifra (16 -> 48) y mantener "omision automatica". Se descarta: la segunda mitad es falsa y es la que el jurado puede contrastar contra `conftest.py`.

### D3 - A2: retirar los recuentos congelados (opcion ii)

Se eliminan de `06-implementacion.tex:91` los valores "357" y "56" y se conserva la frase que remite al reporte vigente del pipeline ("la cifra queda sujeta al reporte vigente"). No se reemplazan por otros numeros: la suite no se puede ejecutar sin `node_modules` y no se permite `npm install`. En el REGISTRO se deja constancia del unico dato reproducible en este entorno, `find "App/Frontend/src" ... | wc -l = 59` archivos de prueba, y de que el recuento de casos y la cobertura no se midieron.

**Alternativa considerada (i):** ejecutar Vitest y actualizar a los valores reales. Se descarta en esta fase por la restriccion explicita de no instalar dependencias; queda como verificacion opcional si el entorno de apply ya tiene `node_modules`. Si se ejecutara, el REGISTRO deberia guardar el comando y la salida completa y la tesis citaria el numero reproducido.

### D4 - A3: lenguaje llano y trazabilidad en el Anexo I

En `06-implementacion.tex:44` reemplazar "(decisión OQ1 = A del change c-72)" por una descripcion del hecho: la rama de clasificacion telefonica por agente LLM basada en LangChain fue retirada y la clasificacion telefonica se unifico con la cascada hibrida del backend. En `:54`, reemplazar "(decisión OQ2 = A del change c-72)" por: el traslado de la superficie de costo al backend elimina la reserva telefonica del proveedor invocado desde N8N.

La trazabilidad interna se mueve al Anexo I solo si no esta ya alli: se agrega una nota breve que registre que esas dos decisiones corresponden a `c-72` y remita a `docs/Tesis/Correcciones/dictamen-correcciones.md`. No se agregan numeros de linea ni identificadores `OQ` al cuerpo.

**Alternativa considerada:** dejar los identificadores y explicarlos en una nota al pie. Se descarta: el cuerpo debe leerse sin conocer la nomenclatura interna del repositorio; el Anexo I es el lugar natural para la trazabilidad.

### D5 - B1/B2: upsert del margen y barrido completo de referencias

En `numeros-canonicos.md`:

1. En la Seccion 3.4 (universo) agregar la fila del margen `6,66 %` con `N ≈ 2.646`, `z = 1,96`, `p = 0,5`, `n = 200`, la formula y la procedencia `04-marco-metodologico.tex:51`, estado `vigente`.
2. Marcar la fila del `6,74 %` / `N = 3.700` como `retirado` con nota de reemplazo, sin borrar la fila.
3. En el punto 2 de la Seccion 7 (decisiones no resolubles), actualizar el texto que aun dice "margen de error del 6,74 % calibrado con N = 3.700": el margen quedo recalculado y registrado como `6,66 %`; la decision de universo no cambia.
4. Barrer **todas** las referencias `07-resultados.tex:<linea>` con un script de correspondencia de contenido, no solo `:129` y `:75`. Minimo a corregir: `:129 -> :128` (parrafo del marco metrico y del reparto 131/69), `:75 -> :74` (exactitud estricta), `:167-188 -> :166-187` (entorno de la tabla de bandas) y `:179-183 -> :178-182` (filas de bandas). Las filas del valor `retirado` `9,5 %` que citan `:160` se corrigen a la seccion donde el valor retirado se declara ausente, o se anota que la referencia es historica.
5. Registrar en el encabezado del memo el upsert de c-145 con fecha y alcance.

El script de barrido se guarda como comando reproducible en el REGISTRO (no se agrega un archivo nuevo al repositorio salvo que el apply lo considere necesario).

**Alternativa considerada:** corregir solo las tres referencias senaladas por la auditoria. Se descarta: el barrido ya detecto otras derivas y el requisito modificado exige que toda referencia resuelva.

### D6 - C1/C2: denominadores pareados y celdas completas

En `08-discusion.tex:10`, conservar el valor global `97/131 (0,7405)` y agregar el pareado: "sobre los 130 casos con prediccion de ambas etapas, 96/130 (0,7385) frente a 88/130 (0,6769)". La oracion debe seguir calificando ambas cifras como estimaciones dentro de la muestra y remitir a `subsec:sensibilidad-ajustes`.

En `08-discusion.tex:95`, completar el parentesis con las tres celdas: "+42,1, +52,1 y +62,0 en el central" (los tres costos de 5, 10 y 15 minutos del escenario laxo). Si la oracion no admite las tres sin ambiguedad, se retira el parentesis y se remite a `tab:balance-neto`; se prefiere completarlo.

**Alternativa considerada:** borrar el valor global y dejar solo el pareado. Se descarta: el valor global es canonico y su eliminacion perderia la lectura sobre los 131 casos de la etapa.

### D7 - D1: nota de estado del placeholder P4

`dictamen-correcciones.md:140` se reemplaza por una nota fechada: "P4 — Sin observaciones pendientes al 2026-10-26. El bloque P se cerro con P1 a P3; no hay material fuente para completar P4 y no se inventan observaciones." Se conserva el encabezado `### P4.` para no romper remisiones, con el estado explicito.

**Alternativa considerada:** eliminar la seccion. Se descarta: otras notas o indices pueden referenciar P4; una nota de estado es reversible y auditable.

### D8 - E1/E2: portabilidad, regresion y alcance del arnes

**E1 (incluido).** Agregar `allow_abbrev=False` al `ArgumentParser` de nivel superior en `evaluation/sensibilidad_ajustes.py`. TDD estricto: primero una prueba que ejecute el parser (o el CLI via `subprocess`) con `prompt --brazo vigente` y falle en Python 3.12.3; luego el cambio minimo; despues triangular con `--brazo-sin-reglas` y con un prefijo ambiguo; por ultimo refactorizar. La prueba debe quedar en `evaluation/tests/test_sensibilidad_ajustes.py` y fallar si se quita `allow_abbrev=False`.

**E2-i (incluido).** Envolver la llamada de `evaluation/run_evaluation.py:1523` a `main_solo_tiempos` para capturar `FileNotFoundError`, imprimir un mensaje legible y salir con codigo distinto de cero, sin traza. Es trivial y mejora la interfaz que el apply documenta.

**E2-ii (excluido).** Registrar en `construir_procedencia` la identidad (ruta, SHA-256 y `generated_at`) de las caches de predicciones consumidas infla el change: obliga a cambiar el esquema del reporte, sus pruebas de formato y la documentacion de `evaluation/README.md`, y no es un defecto que bloquee el PR ni la release. Queda como trabajo futuro declarado en el REGISTRO.

**Alternativa considerada:** incluir E2-ii por completitud. Se descarta por disciplina de alcance: el change ya publica una release y no debe ampliar el contrato del reporte de sensibilidad sin una necesidad verificada.

### D9 - F1: medicion del tope y palanca declarada

Medicion: compilar con el entorno de registro y leer `abspage@last` de `main.aux`; calcular el cuerpo como `pagina de \contentsline {section}{Anexos}` de `main.toc` menos 1; contrastar con el conteo de saltos de pagina de `pdftotext -enc UTF-8 main.pdf -`. Se registran total, cuerpo y anexos antes y despues de las ediciones.

Regla: cuerpo sin anexos <= 100 (decision del equipo del 2026-10-26). El cuerpo esta hoy en 100, margen 0. La correccion A1 es mas larga que la clausula original y A3 agrega prosa; A2 acorta. Si el cuerpo supera 100:

1. Palanca declarada: tipografia de la lista de referencias, precedente P7 de c-141, ya aplicada como `\small`. Se permite ajustarla a `\footnotesize` (o reducir el espaciado de la lista) porque no elimina contenido y es reversible; se registra el diff exacto en el preambulo y el conteo antes/despues.
2. Si aun supera 100, se aplican compensaciones locales de forma en las secciones editadas (frases mas compactas sin perder el hecho) y se vuelve a medir.
3. Si sigue superando 100, el apply se DETIENE y solicita aprobacion explicita de un recorte documentado (checkpoint ALTO). No se publica `v1.2.1` con el cuerpo por encima de 100.

**Alternativa considerada:** recortar contenido de forma preventiva. Se descarta: los invariantes de c-141 prohiben eliminar contenido cientifico, valores canonicos, figuras y tablas requeridas sin aprobacion.

### D10 - F2: identidad de la release `v1.2.1` (recomendada)

Se publica `v1.2.1` con el patron de dos commits, identico a `v1.2.0`:

- **C3:** corrige A/B/C/D/E, actualiza el Anexo B a `v1.2.1`, retira el hash de `v1.2.0` y actualiza la version de `Gomez2026_repositorio` a `1.2.1`; recompila y regenera renders. Tag anotado `v1.2.1` sobre C3 y push con confirmacion del usuario.
- **C4:** consigna el hash completo de C3 en `12-anexos.tex`, agrega la nota "Trazabilidad `v1.2.1`" al REGISTRO y recompila/regenera renders. Commit C4 y push.
- **PR #40:** se actualiza la descripcion con el tag `v1.2.1`, el hash de C3 y la indicacion de merge commit; el PR sigue siendo el mismo y queda desbloqueado.

`v1.2.0` queda inmutable y registrada como superada. No se borra ni se reapunta.

Comandos de verificacion:

```bash
git cat-file -t v1.2.1                                  # debe devolver "tag"
git rev-parse v1.2.1^{commit}                           # C3
git rev-parse v1.2.0^{commit}                           # a49d035c67b32ae17e633ec04b09ecdd2781aac6
git rev-parse v1.0.0^{commit} v1.0.1^{commit} v1.1.0^{commit} v1.1.1^{commit}
git merge-base --is-ancestor v1.2.1 origin/main         # verdadero despues del merge
git ls-remote --tags origin v1.2.1                      # el tag publicado
```

**Alternativa considerada:** reapuntar `v1.2.0`. Se descarta: un tag publicado es inmutable; moverlo falsifica la nota de trazabilidad de C2, que consigna el hash de C1, y rompe la afirmacion de `12-anexos.tex:29`.

### D11 - F3: compilacion de registro y renders

Comando (el mismo de c-141):

```bash
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "<repo>/docs/Tesis/v10 (IA):/work" -w /work/paper \
  texlive-thesis latexmk main.tex
```

Verificaciones: `grep -c "^!" main.log` = 0; `grep -i undefined main.log` vacio; `grep -c "multiply defined" main.log` = 0; `grep -E "WARN|ERROR" main.blg` vacio; "Found N citekeys" = cantidad de `@` del `.bib` (hoy 73); `python verify_citations.py` = `STATUS: PASS`; `pdftotext -enc UTF-8 main.pdf - | grep -c "??"` = 0; cada `\includegraphics` resuelve; `git status --short` limpio despues de commitear los artefactos regenerados.

Renders: `python "docs/Tesis/v10 (IA)/build_tesis_para_agente.py" v1.2.1 > "docs/Tesis/v10 (IA)/tesis_para_agente.md"`; `pdftotext -enc UTF-8` para `tesis_para_evaluacion.txt` y `tesis_completa_extraida.txt`; verificar que las oraciones corregidas (48 pruebas, ausencia de recuentos de frontend, margen 6,66 %, 96/130, tres celdas) aparecen en el texto extraido.

**Alternativa considerada:** no regenerar los renders. Se descarta: el spec de c-141 exige que reflejen la release y el jurado puede leer el `.md`.

### D12 - F4: rastro documental

- **REGISTRO:** nueva seccion "Correccion factual de la release v1.2.0 (c-145)" con: estado inicial y final de cada bloque; causa raiz de A1; evidencia de A2 (conteo de archivos y ausencia de `node_modules`); upsert del margen; tabla de referencias corregidas; decision E2; pagina ledger (fila base 109/100/9 y fila final); evidencia de compilacion; nota de release `v1.2.1` con tag, hash y `v1.2.0` superada.
- **CHANGES.md:** nueva FASE 39 (la ultima es la 38) con la entrada C-145, governance ALTO por el bloque F, dependencia explicita del PR #40 y nota en "Notas del analisis".
- **PR #40:** actualizar la descripcion despues del apply, como ultimo paso y con confirmacion del usuario.

**Alternativa considerada:** actualizar solo el REGISTRO. Se descarta: `CHANGES.md` es el indice operativo y el PR es donde el revisor ve el estado.

### D13 - Specs: compatibilidad con OpenSpec 1.10.0

Los requisitos `MODIFIED` conservan **todos** los nombres de escenario vivos, copiados literalmente del spec principal:

- `Verificabilidad de las afirmaciones de pruebas del Capitulo 6`: `Sin afirmacion de pruebas e2e de N8N no verificable`, `Recuento y cobertura de frontend reproducibles`.
- `Registro canónico con procedencia por valor`: `Todo valor tiene fuente y estado`, `Valor retirado no se cita como vigente`.

Los escenarios nuevos se agregan con `####`. No se modifica `Presupuesto de páginas preservado` en este change porque su delta de c-141 aun no esta archivado y su sincronizacion es responsabilidad de la fase archive de c-141; el tope se documenta en el design y en el REGISTRO. Verificacion: `openspec validate c-145-... --strict --no-interactive` y `openspec validate --specs --strict --no-interactive` (esperado 64 de 64).

### D14 - G: documentacion para agentes sincronizada con el codigo

Regla del bloque: cada valor que se escriba en `CLAUDE.md` u `openspec/config.yaml` se toma del **codigo o del archivo de dependencias**, nunca de otro documento. Se verifico cada uno antes de proponer el change:

| Dato | Estado en `CLAUDE.md` / `config.yaml` | Valor real | Fuente verificada |
|---|---|---|---|
| Modelo de inferencia | "Gemini 2.5 Flash" (`CLAUDE.md:7,48`; `config.yaml:10,33`) | `gemini-3.6-flash` | `App/Backend/app/config/settings.py:78` |
| Timeout de inferencia | 10 s (`CLAUDE.md:50`; `config.yaml:33`) | 30 s por intento, 60 s total | `settings.py:85,104` |
| Reintentos | no documentados | 2 adicionales (peor caso 3 intentos) | `settings.py:97` |
| Parametros de muestreo | temperature 0.3, top_p 0.9, max 100 tokens | identicos | `settings.py:79-81` |
| FastAPI / Uvicorn | "FastAPI 0.115 + Uvicorn" (`config.yaml:17`) | `fastapi==0.143.3`, `uvicorn==0.54.0` | `App/Backend/requirements.txt:5,9` |
| google-genai | ">= 1.0" (`config.yaml:33`; `CLAUDE.md:93`) | `>=2.31.0,<3` | `requirements.txt:37` |
| N8N | "N8N 1.62" (`CLAUDE.md:102`) | `n8nio/n8n:2.11.2` | `docker-compose.yml:133,380` |
| Redis | presente en el diagrama y en la lista de servicios (`CLAUDE.md:41,94,102`) | no existe servicio `redis` en el compose | `docker-compose.yml` (sin servicio) |
| Flujo de clasificacion | "LangChain AI Agent + Redis Memory" (`CLAUDE.md:40-41`) | pipeline deterministico -> Gemini -> fallback; el workflow no contiene nodos LangChain ejecutables | `App/Backend/tests/test_c72_prompt_boundaries.py:144` y `tests/test_n8n_workflow.py:1295-1297` afirman la ausencia |
| Corpus pseudonimizado | "is not tracked in git" (`CLAUDE.md:103`) | versionado (68.911 bytes, `git ls-files` lo resuelve) | `git ls-files --error-unmatch data/corpus_evaluacion_pseudonimizado.json` |
| Docstring del test del hibrido | `>= 0.90` / `< 0.90` (`tests/test_hybrid_classifier.py:8-9`) | `score_correctitud >= 0.5166` | `app/classifiers/hybrid.py:151` y `settings.py:134` |

Alcance de la correccion: reemplazar los valores por los reales; convertir el diagrama obsoleto de LangChain/Redis en una descripcion del pipeline vigente con remision a `knowledge-base/08_arquitectura_propuesta.md`; retirar la linea de Redis de la lista de servicios y de la descripcion del compose. No se agrega documentacion nueva que no exista ya en `knowledge-base/` ni se reescriben otras secciones de `CLAUDE.md`.

**Alternativa considerada:** dejar la documentacion para agentes fuera de este change y abrir un c-146. Se descarta por decision del autor: es documentacion de bajo riesgo, sin efecto en el PDF ni en la release, y dejarla afuera mantendria dos documentos que se contradicen dentro del mismo PR que se propone corregir.

**Requisito normativo:** `project-documentation` incorpora `DOC-005`, que exige que todo valor de stack declarado en la documentacion para agentes coincida con el codigo o el archivo de dependencias, con escenarios para modelo, versiones y flujo vigente. Es un requisito `ADDED`, de modo que no altera escenarios vivos de otros requisitos.

### D15 - H: barrera ejecutable de `DOC-005`

Un requisito de spec no se verifica solo: `openspec validate --specs --strict` comprueba forma y consistencia estructural, no el contenido de `CLAUDE.md`. Sin un chequeo ejecutable, `DOC-005` seria una declaracion de intencion y el drift volveria en la proxima pasada de redaccion, que es exactamente como sobrevivio la afirmacion de los 16 tests. Por eso el bloque H materializa el requisito.

**Ubicacion:** `scripts/preflight/docs_stack_sync.py`, junto a `cost_readiness.py` y `gemini_readiness.py`, que ya corren en el job `backend-tests`. Se reutiliza su contrato (`Check`, `exit_code`, `format_summary`) y su `requirements.txt`, que ya declara `PyYAML>=6.0,<7.0`.

**Entradas (solo lectura, sin red, sin credenciales, sin Docker):**

| Fuente | Que se extrae | Como |
|---|---|---|
| `App/Backend/app/config/settings.py` | defaults de `gemini_model`, `gemini_timeout_seconds`, `gemini_total_timeout_seconds`, `gemini_max_retries`, `gemini_temperature`, `gemini_top_p`, `gemini_max_output_tokens` | `ast.parse` y lectura del valor literal de cada asignacion anotada |
| `App/Backend/app/constants.py` | `SECTORES_CANONICOS` | `ast.parse` y lectura de la tupla literal |
| `App/Backend/requirements.txt` | pins de `fastapi`, `uvicorn`, `google-genai` | lineas de requerimiento |
| `docker-compose.yml` | imagenes por servicio | `yaml.safe_load` |
| `openspec/config.yaml` | modelo, `params`, `stack.backend.framework`, `stack.orchestration.tool` | `yaml.safe_load` |
| `CLAUDE.md` | modelo, parametros, servicios y etapas que afirma | texto |

**Decision de parsing:** se usa `ast` sobre `settings.py` en lugar de importar `Settings`. Importarlo obligaria al preflight a depender de `pydantic-settings` y de las variables de entorno de CI, justo lo que el resto de los preflights evita a proposito. `ast` es estatico, offline y no ejecuta codigo del backend. Alternativa descartada: importar `Settings` con las variables dummy de CI; acopla el preflight al arranque de la app y a `App/Backend/requirements.txt`.

**Chequeos (cada uno devuelve un `Check` propio, de modo que el mensaje nombre el valor divergente):**

1. Modelo declarado en `config.yaml` y en `CLAUDE.md` igual a `Settings.gemini_model`.
2. `timeout_s`, `total_timeout_s` y `max_retries` de `config.yaml` iguales a `Settings`.
3. `temperature`, `top_p` y `max_output_tokens` iguales a `Settings`.
4. Versiones de FastAPI y Uvicorn de `config.yaml` compatibles con los pins de `requirements.txt`.
5. Restriccion de `google-genai` de `config.yaml` y de `CLAUDE.md` compatible con la de `requirements.txt`.
6. Version de N8N de `config.yaml` igual al tag de la imagen `n8nio/n8n` del compose (sin sufijo de registro).
7. Todo servicio que `CLAUDE.md` describa como parte del stack existe como servicio del compose (el caso Redis).
8. Ninguna etapa o tecnologia retirada se describe como vigente (el caso LangChain): si `CLAUDE.md` menciona un nodo o etapa, el workflow debe contenerlo; los tests de c-72 documentan su ausencia.
9. `openspec/config.yaml` parsea como YAML y conserva las claves que consume el CLI.
10. `conventions.thresholds.deterministic_score` y `.human_review` de `config.yaml` iguales a `Settings.deterministic_score_threshold` y `Settings.human_review_threshold`.
11. `conventions.categorias` de `config.yaml` igual, en contenido y en orden, a `SECTORES_CANONICOS` de `App/Backend/app/constants.py` (leido con `ast`, no importado).
12. Sin duplicacion sin cobertura: `CLAUDE.md` no puede contener los literales volatiles que declara `config.yaml`. Donde los repite, el texto remite a `openspec/config.yaml` en lugar de restatear el numero. Asi el conjunto de valores vigilados tiene una sola fuente y el chequeo 12 impide que reaparezca una segunda.

**Como se construye la lista del chequeo 12 (decision de diseno).** Los literales prohibidos se **derivan de `config.yaml` en tiempo de ejecucion**, no se codifican como constante: los dos umbrales de `conventions.thresholds`, las versiones de `stack.backend.framework`, la restriccion de `google-genai` y la version de N8N. Una lista hardcodeada reintroduciria el mismo defecto un nivel mas arriba: al cambiar un valor en `config.yaml` y en el codigo, la constante seguiria prohibiendo el valor viejo y dejaria de prohibir el nuevo, con lo cual `CLAUDE.md` podria restatear el valor nuevo y pasar el chequeo. Se mantiene una lista **estatica** separada, solo para identificadores retirados que ya no figuran en `config.yaml` (`2.5 Flash`, `1.62`), porque son los que no se pueden derivar de ningun lado y son justamente los que reaparecen por copiar texto viejo. La prueba de que la derivacion funciona es un caso de triangulacion: cambiar el umbral en `config.yaml` y restatear el valor nuevo en `CLAUDE.md` debe fallar.

**Huecos que cubre la extension (10 a 12).** Los chequeos 1 a 9 solo comparan valores que ya se declaran en `config.yaml`. Eso deja dos agujeros: (a) `thresholds` y `categorias` estan declarados en `config.yaml:42-43` pero ninguno de los chequeos los leia, y son justo los valores que el PR #40 corrige; (b) `CLAUDE.md` repite cinco literales volatiles en prosa (`:50` y `:100` entre otras), de modo que un cambio de umbral actualizado en `config.yaml` y en el codigo podia dejar `CLAUDE.md` afirmando el valor viejo con el pipeline en verde. El agujero real no era la ausencia de un dato, era la duplicacion sin cobertura.

**Semantica:** `exit_code(checks)` es 0 si y solo si todos son PASS, igual que los otros preflights. Un YAML malformado produce un `Check` FAIL con mensaje explicito, nunca una traza cruda. Los chequeos 1 a 11 fallan por divergencia de valor; el 12 falla por presencia de un valor duplicado en `CLAUDE.md`, que es una condicion distinta y debe reportarse como tal.

**Fuera de alcance explicito:** no se verifica la completitud de los 82 campos de `Settings`. La mayoria (`cost_guard_*`, `db_pool_size`, `twilio_*`, claves y secretos) no debe figurar en la documentacion para agentes, y una lista de exenciones de 80 entradas tendria mas costo de mantenimiento que valor. La barrera cubre la superficie documentada, no todo el objeto de configuracion. Tampoco cubre la tesis: los numeros del documento tienen su propio circuito (memo canonico y `verificar_matriz_trazabilidad.py`, bloques B y D de este change).

**Cableado en CI:** paso nuevo en el job `backend-tests`, despues del preflight de Gemini, mas la inclusion automatica en `python -m pytest scripts/preflight -q`, que ya corre el job. El orden importa: el preflight se ejecuta despues de que el bloque G corrige la documentacion, porque antes de esa correccion debe fallar (y ese fallo se usa como prueba de que la barrera detecta el drift real).

**Prueba de que la barrera sirve:** se corre el preflight sobre el arbol **sin** el bloque G aplicado y se verifica que falla nombrando exactamente el modelo, el timeout, FastAPI, la imagen de N8N, Redis y la duplicacion de literales en `CLAUDE.md` (chequeo 12). Ese resultado se consigna en el REGISTRO. Despues del bloque G, el mismo comando debe salir 0. Una barrera que nunca se vio fallar no es evidencia de nada.

**Nota sobre el chequeo 12 y los umbrales:** los umbrales de `config.yaml` son correctos hoy (0.5166 y 0.70 coinciden con `Settings`), de modo que los chequeos 10 y 11 pasan desde el primer dia. El que debe fallar antes del bloque G es el 12, porque `CLAUDE.md` repite esos valores en prosa. Esa asimetria es intencional: no se busca que todo falle, se busca que el chequeo nuevo demuestre que detecta la duplicacion.

**Alternativa considerada:** validar solo con `grep` de las cadenas retiradas. Se descarta: detecta el sintoma ya conocido y no el proximo drift (una version nueva, un servicio nuevo, una etapa nueva); el chequeo cruzado contra la fuente falla ante cualquier divergencia, incluida la que todavia no conocemos.

## Risks / Trade-offs

- [El cuerpo supera 100 paginas por la prosa nueva] -> Medicion antes/despues y palanca P7 (`\footnotesize` de la lista de referencias); si no alcanza, se detiene y se pide aprobacion de recorte. No se publica la release fuera del tope.
- [El recuento de 48 pruebas de integracion cambia entre la correccion y el commit etiquetado] -> Se mide en el commit que se etiqueta y se registra la salida; el texto cita 48 solo si el comando lo devuelve en ese commit.
- [La suite de frontend se puede ejecutar en el entorno de apply y el recuento difiere de 59 archivos] -> La decision D3 no depende de ese dato; si se ejecuta, se actualiza la evidencia del REGISTRO, no el texto.
- [El barrido de referencias del memo detecta mas filas de las previstas] -> Se corrigen todas las que no resuelvan; el requisito modificado lo exige.
- [El cambio de `allow_abbrev=False` rompe un uso legitimo de abreviaturas] -> No hay usos documentados de abreviaturas; la prueba de regresion cubre los tres nombres exactos y el subcomando.
- [Ventana entre C3 y C4 con el hash aun ausente] -> Es el patron aceptado de `v1.1.1` y `v1.2.0`; el Anexo B declara el tag en C3 y el hash en C4, y el REGISTRO lo explica.
- [El apply no puede ejecutar Docker o no tiene red] -> La compilacion es requisito de la release; si el entorno falla, se detiene y se reporta, no se etiqueta.
- [Se toca un tag publicado] -> Verificacion `git rev-parse` de todos los tags antes y despues; `v1.2.0` debe seguir en `a49d035`.

## Migration Plan

1. **Safety Net:** `cd evaluation && python3 -m pytest -q`; registrar interprete y baseline (en 3.12.3: 4 failed, 448 passed, 1 skipped; en 3.12.15: 0 failed).
2. **Bloque E (TDD):** RED con la prueba de regresion, GREEN con `allow_abbrev=False`, TRIANGULATE, REFACTOR; agregar el manejo de `--solo-tiempos`; correr `pytest tests/test_sensibilidad_ajustes.py tests/test_run_evaluation.py`.
3. **Bloque D:** resolver `P4` y verificar que no quedan `(a completar)`.
4. **Bloque B:** upsert del margen y barrido de referencias; verificar con script.
5. **Bloques A y C:** editar los dos `.tex`; verificar con grep que no quedan "16 tests", "pytest.skip" en la clausula de PostgreSQL, "357", "56 archivos", "OQ1 = A", "OQ2 = A", "decisión OQ".
6. **Compilacion y tope:** compilar en `texlive-thesis`, medir, aplicar la palanca si hace falta, repetir verificaciones.
7. **Release:** C3, tag `v1.2.1`, push con confirmacion; C4 con hash y REGISTRO; push.
8. **Cierre:** `CHANGES.md`, `openspec validate`, descripcion del PR #40.
9. **Rollback:** antes del tag, `git revert` de los commits; despues del tag y antes de entregar, eliminar el tag solo con confirmacion; despues de entregar, no se borra: se corrige con `v1.2.2`. `v1.2.0` y anteriores no se tocan.

## Open Questions

Ninguna que cambie el alcance. Las decisiones aplazables son: (a) si el entorno de apply tiene `node_modules`, se puede medir el recuento real de frontend y enriquecer el REGISTRO sin cambiar el texto; (b) si el cuerpo no alcanza el tope con P7, la aprobacion del recorte la da el usuario en el checkpoint ALTO.
