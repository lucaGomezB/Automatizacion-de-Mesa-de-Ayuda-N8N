# Tasks: Corregir la consistencia interna y la bibliografia de la tesis v1.5.0

Al final de cada tarea, entre parentesis, el requisito del change que cumple (nombre corto). Nombres cortos: `TD` (`tesis-document`) «Consistencia», «Bibliografia», «Nomenclatura», «Tipografia», «Mapa», «Release», «Cobertura», «Cierre»; `NC` (`tesis-numeros-canonicos`) «Registro aditivo», «Trazabilidad». Las tareas de preparacion y las verificaciones transversales no llevan parentesis.

Este change **no escribe codigo de aplicacion**: es prosa LaTeX, entradas bibliograficas y documentacion. El ciclo TDD estricto NO aplica (no hay logica nueva que probar); la red de seguridad son `verify_citations.py`, la recompilacion LaTeX y la busqueda textual de cada correccion. La unica corrida ejecutable es la medicion de cobertura de B4, que reusa la suite existente (no crea pruebas).

Gobernanza **ALTA** (tag anotado `v1.5.1`) + **MEDIA** (prosa y bibliografia). Checkpoints humanos obligatorios: **CHECKPOINT A** antes de instanciar los arboles de trabajo de B4 y fijar las cifras; **CHECKPOINT B** antes de recompilar y versionar; **CHECKPOINT C (ALTA)** antes de cortar el tag `v1.5.1`.

## 0. Preparacion y linea base

- [x] 0.1 Leer `proposal.md`, `design.md` (D1 a D10) y los dos specs delta; confirmar el alcance y que no se toca ningun archivo de `App/`, `n8n/` ni el corpus.
- [x] 0.2 Capturar la linea base: `git status`, `git rev-parse HEAD`, `git describe --tags`, y los anchos de pagina de `docs/Tesis/v10 (IA)/paper/compilacion.md` (159 pp, `Anexos` p. 141). Registrar modificaciones preexistentes ajenas a este change y no tocarlas.
- [x] 0.3 **Red de seguridad:** correr `cd docs/Tesis/v10 (IA) && python verify_citations.py` y registrar que el estado de partida es `STATUS: PASS`.
- [x] 0.4 Releer la lista de secciones del memo `numeros-canonicos.md` y fijar el **primer numero libre** (hoy la ultima es la `3.38`; se espera la `3.43`). Registrar el numero elegido. Si algun change previsto (c-228..c-232) se aplicara antes, correr al siguiente libre sin renumerar.
- [x] 0.5 Releer la entrada de trazabilidad de c-231 en `docs/Tesis/Correcciones/dictamen-correcciones.md` para replicar el formato de filas.
- [x] 0.6 **[CHECKPOINT A — BLOQUEA EL GRUPO 3]** Confirmar con los autores la version de Python del entorno de registro para re-instanciar `bf5e099`/`1b17e55` (OQ1) y la aceptacion de declarar B4 como no reproducible si la deriva de dependencias impide instalarlo. Registrar la respuesta.

  **Checkpoints resueltos (OQ1/OQ2/OQ3):** OQ1: se usa el Python del proyecto (3.12.3); se acepta declarar B4 como no reproducible ante deriva de dependencias (no hizo falta: ambas revisiones instalaron y midieron). OQ2: la lectura primaria de la prosa es la configuracion evaluada `bf5e099`, con `v1.3.0` como contraparte. OQ3: se autoriza el tag anotado `v1.5.1` (fase posterior; no se corta en este grupo).


## 1. Bibliografia: procedencia y localizador (A1, A2, A3)

- [x] 1.1 Agregar el campo `note` a `Powers2011_evaluation` en `Bibliography_base.bib` aclarando que la URL arXiv `2010.16061` es un espejo posterior del articulo de 2011, conservando `year = 2011`; verificar con `rg -n "Powers2011" -A 8 Bibliography_base.bib`. (TD «Bibliografia»)
- [x] 1.2 Agregar `publisher = {IOS Press}` a `ramonferrer2026tripletotext` sin modificar el DOI `10.1177/22104968261440701`; verificar que el DOI sigue intacto con `rg -n "22104968261440701" Bibliography_base.bib`. (TD «Bibliografia»)
- [x] 1.3 Agregar el campo `url` con el localizador oficial (Boletin Oficial o AAIP Argentina) a `AAIP2023_resolucion198`; verificar que la entrada ya tiene URL o DOI. (TD «Bibliografia»)
- [x] 1.4 Correr `python verify_citations.py` y confirmar `STATUS: PASS` tras A1-A3. (TD «Bibliografia»)

## 2. Consistencia interna y forma (B1 a B3, B5 a B10)

- [x] 2.1 `00-resumen.tex:13`: agregar a `147 / 17,0 %` el calificador "no concluyente, con estimacion puntual por encima de la cota"; verificar que coincide con `08-discusion.tex`, `04-marco-metodologico.tex` y `07-resultados.tex`. (TD «Consistencia»)
- [x] 2.2 `01-introduccion.tex:18`: reescribir la oracion para distinguir la tasa a priori del 15 % (preliminar, no re-medida) de la exactitud del brazo manual medida (`0,8278` = `125/151`; `e_man = 26/151 = 0,1722`); verificar que el texto ya no afirma de forma plana que la tasa manual "no fue re-medida". (TD «Consistencia»)
- [x] 2.3 `01-introduccion.tex:66`: agregar la mencion de la validacion fuera de muestra (`0,6893` cruda / `0,7489` ponderada sobre el corpus arbitrado); verificar que la contribucion ya no se acota solo a la validacion dentro de la muestra. (TD «Consistencia»)
- [x] 2.4 `01-introduccion.tex:48`: relabelar `82,78 %` como "exactitud estricta del brazo manual", no "tasa de error manual medida". (TD «Consistencia»)
- [x] 2.5 `11-aspectos-legales.tex:34`, `:107` y `05-arquitectura.tex:8`: desambiguar `v1.2.2` (despliegue de referencia de la prueba de humo TLS) de `v1.3.0` (configuracion entregada) sin alterar los hechos; verificar que no cambian las afirmaciones sobre la campana ni sobre `bf5e099`. (TD «Release»)
- [x] 2.6 Sector names (B6): aplicar la regla de D4 en `01-introduccion.tex:48`, `01-introduccion.tex:72`, `08-discusion.tex:26` y `07-resultados.tex:347`, usando la cadena canonica donde se cita el sistema; verificar cada sitio. (TD «Nomenclatura»)
- [x] 2.7 Tipografia (B7): reemplazar las 4 aperturas malformadas (`?` + comilla invertida) por `¿` en `01-introduccion.tex:26` y `:28`; verificar con una busqueda dirigida que quedan 0 ocurrencias del patron malformado. (TD «Tipografia»)
- [x] 2.8 Limitaciones (B9): rotular explicitamente la novena limitacion (acceso cerrado a `paket2024itservice`) como ya superada en `08-discusion.tex:46` y `:64`, conservando "nueve"; verificar que el conteo y su estado no se contradicen. (TD «Tipografia»)
- [x] 2.9 Mapa de lectura (B10): agregar el parrafo de organizacion del documento al final de `01-introduccion.tex`, antes del `\newpage` (linea 78). (TD «Mapa»)
- [x] 2.10 Verificacion transversal: `git diff` dirigido sobre los `.tex` para confirmar que ningun numero de resultado cambio (solo palabras, rotulos y etiquetas); registrar el resultado. (TD «Consistencia»)

## 3. Cifras de cobertura y pruebas en la configuracion evaluada (B4)

- [x] 3.1 `git worktree add /tmp/c233-bf5e099 bf5e099` y `git worktree add /tmp/c233-v130 1b17e55`; verificar con `git -C /tmp/c233-bf5e099 rev-parse HEAD` y `git -C /tmp/c233-v130 rev-parse HEAD` que son las revisiones correctas. (TD «Cobertura»)
- [x] 3.2 En cada worktree, crear un virtualenv aislado e instalar `App/Backend/requirements.txt` de esa revision; registrar la version de Python y el resultado de la instalacion (exito o fallo). (TD «Cobertura»)
- [x] 3.3 Con las variables de CI dummy, correr en cada worktree `pytest -m "not integration" --cov=app.routes --cov=app.services --cov=app.repositories --cov-report=term-missing`; capturar cobertura (%), `statements`, `missing` y pruebas aprobadas. (TD «Cobertura»)
- [x] 3.4 Actualizar `06-implementacion.tex:85` anclando las cifras a `bf5e099` (7-10-2026) con el comando; agregar la contraparte `v1.3.0` (`1b17e55`) si difiere (o declarar que coinciden). (TD «Cobertura»)
- [x] 3.5 Si alguna cifra cambia respecto del anclaje a `v1.2.18`, declararlo en la prosa y registrar el cambio en el memo `3.43` con su procedencia y estado; si la instalacion falla o la medicion no se reproduce, declararlo como limitacion de reproducibilidad y conservar el ancla `v1.2.18` con nota. (TD «Cobertura», NC «Registro aditivo»)
- [x] 3.6 `git worktree remove /tmp/c233-bf5e099` y `git worktree remove /tmp/c233-v130`; verificar con `git worktree list` que no quedan arboles colgados. (TD «Cobertura»)

## 4. Memo, trazabilidad y roadmap (C2, C3, C4)

- [x] 4.1 Agregar la seccion aditiva (ver 0.4; esperada `3.43`) en `numeros-canonicos.md` con las cifras de cobertura/pruebas y sus procedencias y estados; declarar que no modifica ninguna seccion `3.1` a `3.42`; verificar que la numeracion sigue consecutiva y sin duplicados. (NC «Registro aditivo»)
- [x] 4.2 Agregar en `docs/Tesis/Correcciones/dictamen-correcciones.md` la entrada y las filas de trazabilidad de c-233 (patron c-231) mapeando A1..A3 y B1..B10 a archivo:linea y fragmento verificable; verificar que las entradas previas quedan intactas. (NC «Trazabilidad»)
- [x] 4.3 Agregar en `CHANGES.md` la entrada C-233 (patron C-227..C-232), con scope, governance, dependencias declaradas como independientes y "Leer antes". (NC «Trazabilidad»)

## 5. Cierre de version, compilacion y tag (C1, C5, C6, C7)

- [x] 5.1 **[CHECKPOINT B]** Confirmar con los autores que las cifras de B4 quedaron cerradas y que el memo `3.43` y la prosa son consistentes; registrar la respuesta. (BLOQUEA la recompilacion de cierre.)

  **CHECKPOINT B resuelto (autores):** las cifras de B4 quedaron cerradas y el memo `3.43` y la prosa son consistentes; se autoriza la recompilacion de cierre.

- [x] 5.2 Bump de version a `v1.5.1` en `00-portada.tex:31` ("Versión 1.5.1"), `12-anexos.tex:58` (tag anotado `v1.5.1`) y `:62`, y `Bibliography_base.bib:917`; verificar que no queda una mencion vigente de `1.5.0` en esos puntos. (TD «Cierre»)
- [ ] 5.3 Commitear `docs/Tesis/Correcciones/auditoria-estilo-coneau-v1.5.0.md` (hoy sin trackear, C7); verificar con `git status` que ya no figura sin seguimiento. (TD «Cierre»)
- [x] 5.4 Recompilar con `latexmk -xelatex main.tex` (o xelatex -> biber -> xelatex -> xelatex) en el entorno de registro; verificar 0 errores fatales, 0 referencias/citas indefinidas y 0 etiquetas duplicadas. (TD «Cierre»)
- [x] 5.5 Regenerar `paper/compilacion.md` con `docs/Tesis/Correcciones/resumir_registro_compilacion.py` (no a mano); registrar el nuevo conteo de paginas y el delta frente a 159 pp. (TD «Cierre»)
- [ ] 5.6 **[CHECKPOINT C — ALTA]** Presentar a los autores la compilacion de cierre y solicitar autorizacion expresa para cortar el tag anotado `v1.5.1` (OQ3). Registrar la decision. (TD «Cierre»)
- [ ] 5.7 Con autorizacion (5.6), cortar el tag anotado `v1.5.1` sobre el commit de contenido y consignar su hash en un commit inmediatamente posterior en el Anexo B (patron v1.5.0); verificar que ningun tag previo se movio con `git tag -l "v1.5.*"`. Si no hay autorizacion, cerrar sin tag y registrarlo. (TD «Cierre»)

## 6. Verificacion de cierre

- [ ] 6.1 Confirmar con `git diff --stat` que no cambiaron `App/`, `n8n/`, el clasificador, la configuracion, el corpus ni las predicciones; que no se renumeraron secciones del memo; y que solo A1..A3 y B1..B10 cambiaron en la tesis.
- [ ] 6.2 Correr `python verify_citations.py` y confirmar `STATUS: PASS`; confirmar que el PDF no contiene la secuencia `??` y que `\@abspage@last` quedo registrado en `compilacion.md`.
- [ ] 6.3 Confirmar que los tres checkpoints (A, B, C) quedaron registrados y que el tag, si se corto, tiene autorizacion y hash consignado.
- [ ] 6.4 Correr `openspec validate c-233-corregir-consistencia-interna-y-bibliografia --strict` y verificar que pasa.
- [ ] 6.5 Dejar a cargo del orquestador el `engram sync`; no pushear ni publicar sin instruccion del autor.
- [ ] 6.6 Guardar en Engram el resumen del change con el nombre, los artefactos, el numero de memo, el conteo de paginas y el resultado de las verificaciones.
