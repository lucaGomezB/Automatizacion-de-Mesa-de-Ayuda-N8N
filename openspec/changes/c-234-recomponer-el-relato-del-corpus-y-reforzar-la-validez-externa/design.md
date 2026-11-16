# Design: Recomponer el relato del corpus y reforzar la validez externa

## Context

Ver `proposal.md` - Why. Estado y restricciones que moldean el enfoque:

- Documento de trabajo: `docs/Tesis/v10 (IA)/paper/` en **v1.5.1** (cierre de c-233), **161 pp**, con `Anexos` en p. 143. Fuente LaTeX con `main.tex` + `sections/00-*` a `sections/12-*`; bibliografia en `docs/Tesis/v10 (IA)/Bibliography_base.bib` (94 entradas) y verificador `verify_citations.py`.
- Compilacion: se hace con la imagen Docker local `texlive-thesis` (`docker run --rm -v "<repo>/docs/Tesis/v10 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`); el resumen de evidencia vive en `paper/compilacion.md` y **no se edita a mano** (lo genera `docs/Tesis/Correcciones/resumir_registro_compilacion.py` con `--log`, `--blg`, `--pdf`, `--fuente` y `--salida`).
- Numeracion del memo: la ultima seccion es la **`3.43`** (c-233); `3.39`/`3.40`/`3.41` estan reservadas a `c-230`/`c-229`/`c-228` y la `3.42` a `c-232`. **Este change toma el primer numero libre (hoy `3.44`)**, no renumera y la tarea 0 lo confirma.
- Auditoria fuente: `docs/Tesis/Correcciones/auditoria-estilo-coneau-v1.5.0.md`, secciones 2.6, 2.7, 4 (recomendaciones 7 y 8) y 5.
- El corpus congelado es unico: `data/corpus_evaluacion_pseudonimizado.json`, SHA-256 canonico `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`. La procedencia dispersa por configuracion ya vive, fragmentada, en `04-marco-metodologico.tex:66-68`, `07-resultados.tex:8`, `08-discusion.tex:70` y el Anexo B (`12-anexos.tex:62` y `tab:configuracion-evaluada-entregada`).
- Este change es **independiente** de `c-228`..`c-232` y **no duplica `c-229`**: `c-229` entrega el protocolo de muestreo probabilistico, su script de estimacion y su propio tramo de prosa con estado `condicional`; `c-234` es prosa del estado actual y remision a ese remedio.

## Goals / Non-Goals

**Goals:**

- Cerrar la **recomendacion 7** (rec 7): un relato explicito y trazable de un **unico corpus congelado** del que provienen cifras de **varias configuraciones y corridas**.
- Cerrar la **recomendacion 8** (rec 8): la **validez externa** declarada en las conclusiones con la fuerza correcta y con su remedio empirico (`c-229`) declarado condicional.
- Cerrar el change con compilacion limpia, memo aditivo, trazabilidad, fila del libro mayor, entrada en `CHANGES.md` y `openspec validate --strict`.

**Non-Goals:**

- Medir de nuevo, introducir datos nuevos o cambiar el valor de cualquier numero canonico.
- Ejecutar o duplicar el diseno empirico de `c-229`.
- Bump de version o tag anotado: **no por defecto** (decision D7).
- Tocar `App/`, `n8n/`, el clasificador, la configuracion, el corpus, las predicciones o los artefactos congelados.

## Decisions

### D1 — Principio rector: procedencia y fuerza, no valor

Todas las ediciones son de **palabras, rotulos y remisiones de procedencia**. El design exige que el `git diff` dirigido sobre los `.tex` confirme que **ninguna cifra de resultado cambia**. La unica "sustancia" nueva es una declaracion (la del corpus unico) y un refuerzo de fuerza argumentativa (validez externa), no una medicion. Sin numeros nuevos: si un numero necesitara una entrada en el memo, ya la tiene.

### D2 — Rec 7: un corpus congelado, varias configuraciones

Tres piezas de prosa y un mapeo, sin cambiar valores:

1. **Enunciado del corpus unico.** Hacer explicito, en `04-marco-metodologico.tex` (subseccion `subsec:poblacion-muestra-corpus` y/o el parrafo `Procedencia de los datos del brazo automatizado`, linea 66), que la evidencia se apoya en **un unico corpus congelado** (ruta y huella) y que la multiplicidad es de **configuraciones y corridas**, no de corpus. Alternativa descartada: crear un anexo nuevo exclusivo; se descarta por presupuesto de paginas (D6).
2. **Mapeo de procedencia por cifra.** Un cuadro compacto etiquetado (p. ej. `tab:procedencia-numeros`) que asocie cada **familia de cifras** con su **corrida y configuracion** y su **artefacto de origen**: (a) tiempos manuales (campana 2026-10, sub-ventana jun-ago); (b) tiempos automatizados de correo y formulario (2-10-2026, `hybrid-v1`: vocabulario de 89 patrones, prompt sin reglas de frontera, cortocircuito `>= 0,90`); (c) tiempos telefonicos (5 y 6 de octubre de 2026, sin configuracion unica: 25 el 5 y 56 el 6, version del 6 no consta; recalculados el 19-10-2026); (d) metricas de clasificacion (corrida fuera de linea del 7-10-2026, `hybrid-v3`, commit `bf5e099`); (e) campana complementaria (`hybrid-v3` sobre backend posterior, comparable con 2026-10 solo sobre la cache). Ubicacion preferida: `04-marco-metodologico.tex` (junto a la procedencia) o el Anexo B; se fija en la tarea 1 con la verificacion de paginas.
3. **Distincion de configuraciones no unicas.** Donde un pasaje deje implicita una configuracion unica, distinguirla: `hybrid-v1` (tiempos) frente a `hybrid-v3` (metricas); `bf5e099` (evaluada) frente a `v1.3.0` (entregada) frente a la campana complementaria. En `07-resultados.tex` y `08-discusion.tex`, asegurar que la procedencia de cada familia de cifras quede rotulada por corrida (los caption/tablas de tiempos y de metricas ya lo hacen en parte; se explicita donde falte).

Alternativa descartada (para 2): dispersar el mapeo como frases sueltas; se descarta porque el hallazgo de la auditoria es precisamente que el lector no ve un **unico** relato.

### D3 — Rec 8: fuerza de la validez externa en la conclusion

`09-conclusiones.tex` (`subsec:aportes-generalizacion`, linea 49, y/o el cierre de la subseccion) declara, en un pasaje acotado, la amenaza con la fuerza del diseno: muestra **no probabilistica por conveniencia** (los 200 son los cronometrados), **organizacion unica** (servicios, Mendoza), **universo proyectado, no medido** (`2.646 = 42 x 63`), por lo que las cifras valen para este corpus y no se extrapolan al universo. El pasaje remite al **diseno de muestreo probabilistico (`c-229`)** como **remedio empirico**, declarado **condicional y no ejecutado**. `10-recomendaciones.tex` (`subsec:estudios-replicacion`) puede reforzar la remision, sin afirmar resultados. Alternativa descartada: subir la fuerza en la discusion (`08-discusion.tex:50`, limitacion 2) en lugar de en las conclusiones; se descarta porque la recomendacion 8 pide explicitamente la conclusion.

### D4 — Frontera con `c-229` y con `c-228`..`c-232`

`c-229` (`muestreo-probabilistico-del-universo-de-incidentes`, propuesto, HIGH) entrega el **protocolo**, el **script de estimacion** (Horvitz-Thompson + post-estratificacion, efecto de diseno) y su propio tramo de prosa con estado `condicional` (04, 07, 08, 10) y su memo `3.40`. `c-234`:

- **No duplica** el diseno, no crea protocolo ni script, no mide: solo **declara el estado actual** y **remite** a ese remedio.
- **Es complementario**: `c-234` dice "esta es la limitacion y este es el remedio planificado"; `c-229` dice "este es el diseno del remedio y su estado condicional".
- **Independiente** de `c-228`..`c-232`: no comparte archivos sustantivos (comparte `.tex` con `c-229` en 04/07/08/10, pero con ediciones distintas). Si cualquiera se aplicara antes, la prosa compartida puede requerir repuntar lineas; se declara.

### D5 — Memo aditivo (numeracion)

Se agrega una seccion aditiva con el **primer numero libre** (hoy `3.44`; la tarea 0 lo confirma y, si algun change previsto se aplicara antes, corre al siguiente libre sin renumerar). Registra el mapeo de procedencia (cada familia con su corrida/configuracion/artefacto y estado) y la declaracion de validez externa (con `c-229` en `condicional`). No modifica ningun valor ni estado de las secciones `3.1`-`3.43`.

### D6 — Presupuesto de paginas

Linea base **161 pp** (v1.5.1). Los parrafos son acotados; si el mapeo se lleva a una tabla nueva, puede sumar 1-2 pp. Se verifica `\@abspage@last` y se registra el delta en el libro mayor de paginas (G0) y en `compilacion.md`. Si el crecimiento excede el presupuesto razonable, se prefiere una tabla compacta o una nota en el Anexo B a una subseccion nueva.

### D7 — Version y tag: no por defecto

La linea base es **v1.5.1**. Este change **no** bumpea la version ni corta tag salvo pedido explicito de los autores (OQ2). Si se autorizara un bump a `v1.5.2`, se repuntaria la portada (`00-portada.tex`), el Anexo B (`12-anexos.tex`) y la entrada bibliografica (`Bibliography_base.bib`, `Gomez2026_repositorio`), patron c-233; un tag anotado seria CHECKPOINT de gobernanza ALTA y consignaria su hash en un commit posterior. Por defecto el change cierra **sin** bump ni tag.

### D8 — Cierre: recompilacion, memo, trazabilidad, libro mayor y roadmap

- **Recompilacion:** con `texlive-thesis`; regenerar `compilacion.md` con `resumir_registro_compilacion.py` (no a mano); registrar el delta de paginas.
- **Memo:** seccion aditiva (D5).
- **Trazabilidad:** entrada de c-234 y filas `C29/...` en `dictamen-correcciones.md` (patron C28 de c-233), mapeando rec 7 y rec 8 a `archivo:linea` con fragmento verificable.
- **Libro mayor:** fila `+c-234` en la seccion G0 "Libro mayor de paginas" (patron `+c-233`).
- **Roadmap:** entrada C-234 en `CHANGES.md` (patron C-227..C-233).

### D9 — Gobernanza

Gobernanza **MEDIA** (prosa y documentacion). Sin checkpoints de ALTA salvo que los autores autoricen un tag (D7). Cero llamadas a Gemini. TDD estricto no aplica (no hay logica nueva): la red de seguridad es `verify_citations.py`, la recompilacion LaTeX y la busqueda textual de cada correccion.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| Cambiar por descuido un valor canonico | Principio D1; `git diff` dirigido sobre los `.tex`; solo cambian palabras y remisiones |
| Solapar con `c-229` | Frontera D4; `c-234` solo declara y remite; el diseno y los datos nuevos quedan en `c-229` |
| Desplazar la numeracion del memo | Seccion aditiva en el primer libre (D5); no se renumera `3.38`-`3.43` |
| El mapeo crece el PDF | D6; tabla compacta o nota en Anexo B; verificar `\@abspage@last` y registrar el delta |
| `verify_citations.py` roto | No se toca el `.bib`; se corre igualmente al cierre |
| Prosa compartida con `c-229` desfasada si se aplica antes | Se declaran independientes (D4); al aplicar el segundo, repuntar lineas |

## Migration Plan

1. Preparacion: linea base, `verify_citations.py: PASS`, fijar el numero de memo (tarea 0).
2. Rec 7: enunciado del corpus unico, mapeo de procedencia y distincion de configuraciones (grupo 1).
3. Rec 8: fuerza de la validez externa en la conclusion y remision a `c-229` (grupo 2).
4. Memo aditivo, filas de trazabilidad, fila del libro mayor, entrada en `CHANGES.md` (grupo 3).
5. Recompilacion y regeneracion de `compilacion.md` (grupo 4).
6. Verificacion de cierre (grupo 5).

Rollback: `git revert` del commit de contenido; lo aditivo se retira sin tocar secciones previas; el PDF y `compilacion.md` se regeneran. Ningun valor canonico previo se modifica.

## Open Questions

- **OQ1 (aplicacion, tarea 0):** confirmar el **primer numero libre** del memo (se espera `3.44`). Si `c-228`..`c-232` se aplicaran antes, correr al siguiente libre sin renumerar. No cambia specs.
- **OQ2 (autores):** decidir si el cierre **amerita un bump** a `v1.5.2` (y, si correspondiera, un tag anotado). **Por defecto: no hay bump ni tag.** No cambia specs.
- **OQ3 (aplicacion, tareas 1-2):** fijar la ubicacion del mapeo de procedencia (`04-marco-metodologico.tex` vs Anexo B) segun el presupuesto de paginas; por defecto, junto a la procedencia en `04`.
- **OQ4 (aplicacion, tarea 5):** si `c-229` (u otro de `c-228`..`c-232`) se aplicara antes que `c-234`, repuntar las lineas de la prosa compartida que el change previo haya desplazado.
