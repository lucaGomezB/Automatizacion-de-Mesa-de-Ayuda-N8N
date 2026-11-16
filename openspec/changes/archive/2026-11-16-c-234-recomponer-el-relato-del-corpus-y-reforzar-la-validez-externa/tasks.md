# Tasks: Recomponer el relato del corpus y reforzar la validez externa

Al final de cada tarea, entre parentesis, el requisito del change que cumple (nombre corto). Nombres cortos: `TD` (`tesis-document`) «Procedencia» (relato del corpus unico), «Validez externa»; `NC` (`tesis-numeros-canonicos`) «Registro aditivo», «Trazabilidad». Las tareas de preparacion y las verificaciones transversales no llevan parentesis.

Este change **no escribe codigo de aplicacion**: es prosa LaTeX y documentacion. El ciclo TDD estricto NO aplica (no hay logica nueva que probar); la red de seguridad son `verify_citations.py`, la recompilacion LaTeX y la busqueda textual de cada correccion.

Gobernanza **MEDIA** (prosa y documentacion). Sin checkpoints de gobernanza ALTA salvo que los autores autoricen un bump de version o un tag (OQ2). Cero llamadas a Gemini.

## 0. Preparacion y linea base

- [x] 0.1 Leer `proposal.md`, `design.md` (D1 a D9) y los dos specs delta; confirmar el alcance y que no se toca ningun archivo de `App/`, `n8n/`, el corpus ni los artefactos congelados.
- [x] 0.2 Capturar la linea base: `git status`, `git rev-parse HEAD`, `git describe --tags` y los anchos de pagina de `docs/Tesis/v10 (IA)/paper/compilacion.md` (**161 pp**, `Anexos` p. 143). Registrar modificaciones preexistentes ajenas a este change y no tocarlas.
- [x] 0.3 **Red de seguridad:** correr `cd docs/Tesis/v10 (IA) && python verify_citations.py` y registrar que el estado de partida es `STATUS: PASS`.
- [x] 0.4 Releer los encabezados `3.N` de `docs/Tesis/Correcciones/numeros-canonicos.md` y fijar el **primer numero libre** (hoy la ultima seccion es la `3.43` de c-233; `3.39`-`3.42` estan reservadas a `c-230`/`c-229`/`c-228`/`c-232`; se espera `3.44`). Registrar el numero elegido; si algun change previsto se aplicara antes, correr al siguiente libre sin renumerar (OQ1). (NC «Registro aditivo»)
- [x] 0.5 Releer la entrada de trazabilidad de c-233 (`C28/...`) y la fila `+c-233` del libro mayor (seccion G0) en `docs/Tesis/Correcciones/dictamen-correcciones.md`, para replicar el formato de las filas y de la fila del libro mayor.
- [x] 0.6 Registrar la respuesta a OQ2: confirmar con los autores que **no hay bump de version ni tag** por defecto, o la decision contraria si la hubiera. Registrar la respuesta.

## 1. Relato del corpus unico congelado (rec 7)

- [x] 1.1 `04-marco-metodologico.tex` (subseccion `subsec:poblacion-muestra-corpus` y/o el parrafo `Procedencia de los datos del brazo automatizado`): agregar el enunciado explicito de que la evidencia se apoya en un **unico corpus congelado** (`data/corpus_evaluacion_pseudonimizado.json`, SHA-256 `1fd17d7e...`) y que la multiplicidad es de **configuraciones y corridas**, no de corpus; verificar que el enunciado no cambia ningun valor. (TD «Procedencia»)
- [x] 1.2 Agregar el **mapeo de procedencia por cifra** (tabla compacta etiquetada, p. ej. `tab:procedencia-numeros`, en `04-marco-metodologico.tex` o el Anexo B segun OQ3): cada familia (tiempos manuales; tiempos automatizados de correo/formulario con `hybrid-v1`; tiempos telefonicos de config no unica; metricas de clasificacion con `hybrid-v3`/`bf5e099`; campana complementaria) con su corrida, su configuracion y su artefacto de origen; verificar que cada celda coincide con el texto vigente. (TD «Procedencia»)
- [x] 1.3 `07-resultados.tex` y `08-discusion.tex`: explicitar la procedencia por corrida donde un pasaje deje implicita una configuracion unica (por ejemplo `hybrid-v1` en los tiempos frente a `hybrid-v3` en las metricas; `bf5e099` evaluada frente a `v1.3.0` entregada); verificar con `rg` que las remisiones de procedencia quedan rotuladas y que ningun valor cambia. (TD «Procedencia»)
- [x] 1.4 Anexo B (`12-anexos.tex:62` y, si corresponde, `tab:configuracion-evaluada-entregada`): asegurar que el relato del anexo remite al mapeo de procedencia y distingue configuracion evaluada, entregada y de la campana complementaria; verificar coherencia con 04 y 07. (TD «Procedencia»)
- [x] 1.5 Verificacion transversal de rec 7: `git diff` dirigido sobre los `.tex` para confirmar que **ninguna cifra de resultado cambio** (solo palabras, rotulos y remisiones); registrar el resultado. (TD «Procedencia»)

## 2. Validez externa en la conclusion (rec 8)

- [x] 2.1 `09-conclusiones.tex` (`subsec:aportes-generalizacion` y/o el cierre): agregar el pasaje que declara la validez externa con la fuerza correcta (muestra no probabilistica por conveniencia; organizacion unica —servicios, Mendoza—; universo proyectado, no medido, `2.646 = 42 x 63`) y que las cifras valen para este corpus y no se extrapolan; verificar la busqueda textual del pasaje. (TD «Validez externa»)
- [x] 2.2 En el mismo pasaje, declarar el **diseno de muestreo probabilistico (c-229)** como **remedio empirico**, condicional y no ejecutado; verificar que el texto NO afirma que la validez externa ya fue establecida ni que c-229 este aplicado. (TD «Validez externa»)
- [x] 2.3 `10-recomendaciones.tex` (`subsec:estudios-replicacion`): si refuerza la lectura, remitir al diseno probabilistico sin duplicar el contenido de `c-229`; verificar que no se introducen cifras nuevas. (TD «Validez externa»)
- [x] 2.4 Verificacion transversal de rec 8: `git diff` dirigido para confirmar que no cambio ningun valor canonico y que el unico agregado sustantivo es la declaracion; registrar el resultado. (TD «Validez externa»)

## 3. Memo, trazabilidad, libro mayor y roadmap

- [x] 3.1 Agregar la seccion aditiva (ver 0.4; esperada `3.44`) en `numeros-canonicos.md` con el mapeo de procedencia (cada familia con su corrida/configuracion/artefacto y estado) y la declaracion de validez externa (`c-229` en `condicional`); declarar que no modifica ninguna seccion `3.1` a `3.43`; verificar que la numeracion sigue consecutiva y sin duplicados. (NC «Registro aditivo»)
- [x] 3.2 Agregar en `docs/Tesis/Correcciones/dictamen-correcciones.md` la entrada y las filas de trazabilidad de c-234 (patron `C28`), mapeando la rec 7 y la rec 8 a `archivo:linea` con fragmento verificable; verificar que las entradas previas quedan intactas. (NC «Trazabilidad»)
- [x] 3.3 Agregar la fila `+c-234` al **libro mayor de paginas** de la seccion G0 (patron `+c-233`) con el conteo medido tras la recompilacion (grupo 4) y su delta frente a `161 / 142 / 19`; verificar el formato de la tabla. (NC «Trazabilidad»)
- [x] 3.4 Agregar en `CHANGES.md` la entrada C-234 (patron C-227..C-233), con scope, gobernanza MEDIA, dependencias declaradas como independientes de `c-228`..`c-232` y la frontera con `c-229` (complementario, no duplicado), y "Leer antes". (NC «Trazabilidad»)

## 4. Recompilacion y cierre

- [x] 4.1 Recompilar con la imagen Docker `texlive-thesis`: `docker run --rm -v "<repo>/docs/Tesis/v10 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`; verificar 0 errores fatales, 0 referencias/citas indefinidas y 0 etiquetas duplicadas. (TD «Cierre»)
- [x] 4.2 Regenerar `paper/compilacion.md` con `python3 -I docs/Tesis/Correcciones/resumir_registro_compilacion.py --log ... --blg ... --pdf ... --fuente "<descripcion del arbol>" --salida ...` (no a mano); registrar el nuevo conteo de paginas y el delta frente a 161 pp. (TD «Cierre»)
- [x] 4.3 Completar la fila `+c-234` del libro mayor (tarea 3.3) con el conteo y el delta medidos; verificar que coincide con `compilacion.md`. (NC «Trazabilidad»)
- [x] 4.4 Confirmar el cierre de version segun OQ2/0.6: por defecto **sin** bump ni tag; si los autores autorizaron bump a `v1.5.2`, repuntar portada (`00-portada.tex`), Anexo B (`12-anexos.tex`) y `Bibliography_base.bib` (`Gomez2026_repositorio`), y, si se autoriza un tag anotado, tratarlo como CHECKPOINT de gobernanza ALTA con hash consignado en un commit posterior (patron c-233). Registrar la decision. (TD «Cierre»)

## 5. Verificacion de cierre

- [x] 5.1 Confirmar con `git diff --stat` que no cambiaron `App/`, `n8n/`, el clasificador, la configuracion, el corpus ni las predicciones; que no se renumeraron secciones del memo; y que el diff de los `.tex` solo agrega prosa de procedencia y de validez externa, sin alterar ningun valor canonico (OQ4: si `c-229` u otro se aplico antes, repuntar lineas desplazadas).
- [x] 5.2 Correr `python verify_citations.py` y confirmar `STATUS: PASS`; confirmar que el PDF no contiene la secuencia `??` y que `\@abspage@last` quedo registrado en `compilacion.md`.
- [x] 5.3 Confirmar el enunciado del corpus unico (ruta y huella), el mapeo de procedencia y la declaracion de validez externa con remision a `c-229` (condicional), cada uno con su busqueda textual de verificacion.
- [x] 5.4 Correr `openspec validate c-234-recomponer-el-relato-del-corpus-y-reforzar-la-validez-externa --strict` y verificar que pasa (registrar el codigo de salida).
- [x] 5.5 Dejar a cargo del orquestador el `engram sync`; no pushear ni publicar sin instruccion del autor. — No se pusheo aun; el `engram sync` queda a cargo del autor.
- [x] 5.6 Guardar en Engram el resumen del change con el nombre, los artefactos, el numero de memo, el conteo de paginas y el resultado de las verificaciones. — Guardado (`opsx/c-234-relato-corpus-validez-externa/apply`).
