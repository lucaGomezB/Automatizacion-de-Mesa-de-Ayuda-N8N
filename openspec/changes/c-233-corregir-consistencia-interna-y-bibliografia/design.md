# Design: Corregir la consistencia interna y la bibliografia de la tesis v1.5.0

## Context

Ver `proposal.md` - Why. Estado y restricciones que moldean el enfoque:

- Documento evaluado: `docs/Tesis/v10 (IA)/paper/` en **v1.5.0** (commit `5cd0011`, tag `v1.5.0`), **159 pp**, con `Anexos` en p. 141. Fuente LaTeX con `main.tex` + `sections/00-*` a `sections/12-*`, bibliografia en `docs/Tesis/v10 (IA)/Bibliography_base.bib` (94 entradas) y verificador `verify_citations.py`.
- Entorno de registro de compilacion: XeTeX 3.141592653-2.6-0.999998 (TeX Live 2026), biber 2.22; el resumen de evidencia vive en `docs/Tesis/v10 (IA)/paper/compilacion.md` y **no se edita a mano** (lo genera `docs/Tesis/Correcciones/resumir_registro_compilacion.py`).
- Cadena de cierre de version que se replica (c-231 / v1.5.0): portada (`00-portada.tex:31`), Anexo B (`12-anexos.tex:58`, tag anotado + hash en commit posterior) y entrada bibliografica (`Bibliography_base.bib:917`). El tag es **anotado** y su hash se consigna en un commit inmediatamente posterior (un commit no puede contener su propio hash).
- Numeracion del memo: la ultima seccion es la **`3.38`** (c-231). c-230/c-229/c-228 esperan `3.39`/`3.40`/`3.41` y c-232 espera `3.42`; **este change NO renumera** y toma la **`3.43`** (si alguno de los changes previstos se aplicara antes, se corre al primer numero libre; la tarea 0 lo fija).
- Configuracion evaluada: commit **`bf5e099`** (7-10-2026), primera revision que versiona la cascada `hybrid-v3`; configuracion entregada: tag **`v1.3.0`** (`1b17e55`). La tesis distingue ambas (Anexo B, `tab:configuracion-evaluada-entregada`). Las cifras de cobertura/pruebas de `06-implementacion.tex:85` hoy se anclan a `v1.2.18` (commit `03d1612`).
- Este change es **independiente** de c-228..c-232: no comparte archivos con ellos y no los bloquea.

## Goals / Non-Goals

**Goals:**

- Cerrar las **diez inconsistencias internas** y las **tres anomalias bibliograficas** del dictamen interno sin alterar ningun valor canonico.
- Re-anclar las cifras de cobertura/pruebas a la configuracion evaluada de forma **reproducible**, declarando la deriva de dependencias.
- Cerrar la version **v1.5.1** con una compilacion limpia y, con **autorizacion expresa**, un tag anotado cuyo hash quede consignado.

**Non-Goals:**

- Medir de nuevo el clasificador, el corpus o los tiempos; introducir datos nuevos.
- Cambiar el valor de ningun numero canonico (salvo las cifras de cobertura de B4, declaradas y canalizadas).
- Nueva capability de bibliografia: las reglas de citas ya viven en `tesis-document`.
- Tocar `App/`, `n8n/`, el clasificador, la configuracion, el corpus o las predicciones.

## Decisions

### D1 — Principio rector: cambia la forma, no el valor

Todas las correcciones A y B son de **palabras, rotulos, procedencia o etiquetas**; el design exige que el diff dirigido no altere ningun numero de resultado. La unica excepcion declarada es **B4** (cifras de cobertura y conteo de pruebas), que puede cambiar de valor por re-anclaje a la configuracion evaluada; se declara en la prosa y se canaliza por el memo `3.43` (ver D8). Verificacion transversal: `git diff` dirigido sobre los `.tex` para confirmar que las cifras de resultados no cambian.

### D2 — Bibliografia (A1, A2, A3): procedencia y localizador

| Entrada | Cambio | Se conserva |
|---|---|---|
| `Powers2011_evaluation` (`:152`) | Agregar `note` que aclara que la URL arXiv `2010.16061` es un **espejo posterior** de JMLT 2(1):37-63, 2011 | `year = 2011`; no se inventa DOI (no existe para el original) |
| `ramonferrer2026tripletotext` (`:361`) | Agregar `publisher = {IOS Press}` | El DOI `10.1177/22104968261440701` **verificado**: resuelve al titulo correcto; no se toca |
| `AAIP2023_resolucion198` (`:1012`) | Agregar `url` al localizador oficial (Boletin Oficial / AAIP Argentina) | El resto de la entrada |

Alternativa descartada (A1): reemplazar la URL arXiv por una referencia sin enlace; se descarta porque oculta el rastro de verificacion y el articulo de 2011 no tiene DOI. Alternativa descartada (A2): cambiar el DOI al de IOS Press; se descarta porque el DOI vigente **resuelve** y cambiarlo introduciria un identificador no verificado.

### D3 — Consistencia del veredicto (B1, B2, B3, B8)

- **B1:** `00-resumen.tex:13` pasa a acompanar `147 / 17,0 %` con el calificador del cuerpo ("no concluyente, con estimacion puntual por encima de la cota"), identico al de `08-discusion.tex:8`, `04-marco-metodologico.tex:88` y `07-resultados.tex:186`.
- **B2:** `01-introduccion.tex:18` se reescribe para **distinguir** la tasa a priori del 15 % (preliminar, **no re-medida**) de la **medicion** del brazo manual de la campana complementaria (`0,8278` = `125/151`; `e_man = 26/151 = 0,1722`). No se elimina la declaracion de condicionalidad; se acota a la tasa a priori.
- **B3:** `01-introduccion.tex:66` agrega la mencion out-of-sample (`0,6893` cruda / `0,7489` ponderada sobre el corpus arbitrado) que ya reportan `00-resumen.tex:13` y `:29`.
- **B8:** `01-introduccion.tex:48` relabela `82,78 %` como "exactitud estricta del brazo manual", no "tasa de error manual medida".

### D4 — Nomenclatura canonica y tipografia (B6, B7)

- **B6:** regla: usar la cadena canonica (sin tildes) cuando el texto cita el sector **como cadena del sistema**; conservar el espanol natural en prosa puramente narrativa cuando no haya riesgo de confusion. Sitios declarados: `01-introduccion.tex:48`, `01-introduccion.tex:72`, `08-discusion.tex:26`, `07-resultados.tex:347`. Se proscribe la forma intermedia en un mismo pasaje.
- **B7:** las 4 aperturas malformadas (`?``) de `01-introduccion.tex:26` y `:28` pasan a `¿`. Verificacion: `rg` sobre el patron malformado con 0 coincidencias (cuidando no capturar LaTeX legitimo).

### D5 — Limitaciones declaradas (B9)

`08-discusion.tex:46` y `:64` conservan "nueve limitaciones" y rotulan explicitamente la novena (acceso cerrado a `paket2024itservice`) como **ya superada**, de modo que el conteo y su estado no se contradigan. Alternativa descartada: bajar el conteo a ocho; se descarta porque el hecho (la limitacion existio y se documento) es informativo y su resolucion es un merito.

### D6 — Mapa de lectura (B10)

Se agrega un parrafo de organizacion al final de `01-introduccion.tex`, antes del `\newpage` (linea 78), que describe la estructura de capitulos y anexos. Presupuesto de paginas: se verifica `\@abspage@last` contra la linea base de 159 pp; si el parrafo agrega paginas, se declara en `compilacion.md`.

### D7 — Desambiguacion de etiquetas de release (B5)

`11-aspectos-legales.tex:34`, `:107` y `05-arquitectura.tex:8` etiquetan `v1.2.2` como **despliegue de referencia** de la prueba de humo TLS y `v1.3.0` como **configuracion entregada**. No se alteran los hechos (terminacion TLS verificada sobre el despliegue de referencia; campana sobre otros perfiles; configuracion evaluada `bf5e099`).

### D8 — Cifras de cobertura/pruebas en la configuracion evaluada (B4) — la decision de mayor riesgo

Objetivo: re-anclar la cobertura y el conteo de pruebas (hoy `90 %`, `2503` sentencias, `242` sin cubrir, `1773` pruebas, anclados a `v1.2.18` / `03d1612`) a la **configuracion evaluada** `bf5e099` y, si difiere, a la **configuracion entregada** `v1.3.0` (`1b17e55`).

Procedimiento reproducible (cada corrida se registra con su salida):

1. `git worktree add /tmp/c233-bf5e099 bf5e099` y `git worktree add /tmp/c233-v130 1b17e55` (arboles de trabajo **limpios**, sin tocar el arbol actual).
2. En cada worktree, crear un virtualenv **aislado** e instalar las dependencias **pinneadas de esa revision** (`App/Backend/requirements.txt` del propio commit), registrando la version de Python usada.
3. Inyectar las variables de CI requeridas por `pydantic-settings` (dummies de `DATABASE_URL`, `GEMINI_API_KEY`, `PSEUDONYMIZATION_ENCRYPTION_KEY`, `JWT_SECRET_KEY`, `COST_GUARD_CALLER_HMAC_KEY`), con el subconjunto SQLite offline (Gemini/N8N mockeados).
4. Correr `pytest -m "not integration" --cov=app.routes --cov=app.services --cov=app.repositories --cov-report=term-missing` desde `App/Backend/`.
5. Capturar de la salida: porcentaje de cobertura, `statements`, `missing` y el conteo de pruebas aprobadas.
6. `git worktree remove` de ambos arboles al terminar.

Reporte en `06-implementacion.tex:85` (y limpieza de la trazabilidad al memo): configuracion evaluada `bf5e099` como ancla primaria; contraparte `v1.3.0` en la misma oracion (o en una nota) **si difiere**; si coinciden, se declara que coinciden.

**Riesgo de deriva de entorno (declarado en la prosa):** `bf5e099` es del 7-10-2026 y `1b17e55` del cierre de la cascada; sus pins pueden no instalar sobre el Python disponible hoy (p. ej. wheels de `asyncpg`/`pydantic-core` para una version de Python nueva) o resolver distinto contra PyPI. Mitigacion: (a) fijar la version de Python declarada por la revision; (b) si la instalacion falla o la medicion no se reproduce, **declararlo como limitacion de reproducibilidad** y **conservar el ancla `v1.2.18` vigente con una nota** en lugar de reportar una cifra no reproducida; (c) registrar los hashes de los requirements del commit. Si **alguna** cifra cambia respecto del valor vigente, la prosa lo declara y el memo `3.43` lo registra con estado `vigente` y la anterior como `retirado` (ver spec `tesis-numeros-canonicos`). Alternativa descartada: medir en el arbol actual y atribuirlo a `bf5e099`; se descarta porque el arbol actual no es esa revision y la atribucion seria falsa.

### D9 — Cierre de version y tag (C1 a C7)

- **C1:** recompilar con `latexmk -xelatex main.tex` (o la secuencia xelatex -> biber -> xelatex -> xelatex) en el entorno de registro; regenerar `compilacion.md` con `resumir_registro_compilacion.py` (no a mano); registrar el delta de paginas respecto de 159.
- **C2:** memo seccion aditiva `3.43` (ver D8) sin renumerar.
- **C3:** filas de trazabilidad en `dictamen-correcciones.md` siguiendo el patron de c-231.
- **C4:** entrada C-233 en `CHANGES.md` (patron C-227..C-232).
- **C5:** bump `v1.5.1` en `00-portada.tex:31`, `12-anexos.tex:58` y `:62`, y `Bibliography_base.bib:917`.
- **C6:** **CHECKPOINT de gobernanza ALTA**: el tag anotado `v1.5.1` se corta **solo** con autorizacion expresa del autor; se consigna su hash en un commit inmediatamente posterior en el Anexo B (patron v1.5.0). No se mueve ningun tag previo.
- **C7:** trackear `docs/Tesis/Correcciones/auditoria-estilo-coneau-v1.5.0.md`.

### D10 — Gobernanza y checkpoints

Gobernanza **ALTA** (tag anotado `v1.5.1`) + **MEDIA** (prosa y bibliografia). Checkpoints humanos: **CHECKPOINT A** antes de re-instanciar los worktrees de B4 y fijar las cifras; **CHECKPOINT B** antes de recompilar/versionar (confirmar que las cifras de B4 quedan cerradas y que el memo `3.43` esta redactado); **CHECKPOINT C (ALTA)** antes de cortar el tag `v1.5.1`. Sin bloque LOW critico. Cero llamadas a Gemini.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| Cambiar por descuido un valor canonico | Principio D1; `git diff` dirigido; solo cambian palabras/rotulos/procedencia |
| Deriva de dependencias impide reproducir B4 | Virtualenv pinneado por revision; si no reproduce, declararlo y conservar el ancla `v1.2.18` con nota (D8) |
| Mapa de lectura crece el PDF | Parrafo acotado; verificar `\@abspage@last` y registrar en `compilacion.md` |
| Etiquetas de release ambiguas tras la edicion | D7 conserva los hechos; verificacion de que la campana y `bf5e099` no cambian |
| Duplicar/desplazar la numeracion del memo | Seccion `3.43` aditiva fijada en la tarea 0; no se renumeran `3.38`-`3.42` |
| Cortar el tag sin autorizacion | CHECKPOINT C bloquea el tag; sin autorizacion el change cierra sin tag |
| `verify_citations.py` roto por la edicion del `.bib` | Correrlo tras A1-A3; debe seguir en PASS |

## Migration Plan

1. Preparacion: linea base, worktrees de B4, fijar el numero de memo (tarea 0); CHECKPOINT A.
2. Bibliografia A1-A3.
3. Consistencia B1, B2, B3, B5, B6, B7, B8, B9, B10.
4. Cifras de cobertura B4 (worktrees + memo `3.43`); CHECKPOINT B.
5. Cierre C1-C5, C7 (compilacion, memo, trazabilidad, CHANGES, version).
6. CKECKPOINT C y tag `v1.5.1` + commit del hash (C6).
7. Verificacion de cierre.

Rollback: `git revert` del commit de contenido (C1 previo al tag); el memo y las filas son aditivos; el tag se elimina (local y remoto) y la version vuelve a `v1.5.0`. Ningun valor canonico previo se modifica.

## Open Questions

- **OQ1 (autores, tarea 0/4)**: confirmar la version de Python del entorno de registro para re-instanciar `bf5e099`/`1b17e55` y si se acepta declarar B4 como no reproducible en caso de deriva. Se resuelve al aplicar; no cambia specs.
- **OQ2 (autores, tarea 4)**: si `bf5e099` y `v1.3.0` difieren en cobertura/pruebas, confirmar cual es la lectura primaria de la prosa (por defecto, la evaluada `bf5e099`, con la entregada como contraparte).
- **OQ3 (autores, tarea 6)**: autorizacion expresa para cortar el tag anotado `v1.5.1` (CHECKPOINT C). Si no se autoriza, el change cierra sin tag y la version `v1.5.1` queda como version de trabajo.
- **OQ4 (aplicacion, tarea 5)**: si el archivo de auditoria se commitea junto con el contenido de C-233 o en un commit propio; por defecto, en el mismo commit de contenido.
