Al final de cada tarea, entre paréntesis, los requisitos del change que cumple, por nombre corto entre «» precedido de su capacidad: `OOS` (`evaluation-out-of-sample-validation`) y `TD` (`tesis-document`). Nombres cortos: OOS «Preservación»; TD «Reproducibilidad». Las tareas de preparación y las verificaciones transversales no llevan paréntesis.

Este change no escribe código de producción: no hay ciclo RED/GREEN que aplicar. La única red de seguridad automatizada es la suite de `evaluation/` que valida las tablas SHA-256 del README de la campaña; se corre antes y después de editarlo.

## 0. Preparación y verificación de estado

- [x] 0.1 Leer `proposal.md`, `design.md` (D1 a D8) y los dos specs delta; confirmar que no hay skill de código aplicable (el change no toca `App/` ni `evaluation/` ejecutable) y registrar la decisión.
- [x] 0.2 Capturar la línea de base y guardarla como evidencia de partida: `git cat-file -t 561b3c4` (`commit`), `git merge-base --is-ancestor 561b3c4 origin/main` (`1`, esperado), `git log --diff-filter=A --format=%h -- evaluation/data/campana/predicciones_independiente.json` (`1b17e55`), `git rev-parse v1.4.1^{commit}` (`2d8b0d5c…`), `sha256sum` de `predicciones_independiente.json` y `reporte_independiente.md`, y `git status`. Registrar que hoy hay dos modificaciones preexistentes ajenas a este change (`docs/Tesis/v10 (IA)/Bibliography_base.bib` y `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex`, de c-221) y no tocarlas ni incluirlas en los commits de este change.
- [x] 0.3 **Red de seguridad:** correr `cd evaluation && pytest tests/test_doble_etiquetado.py::test_tabla_primaria_versionada_integra tests/test_campana.py::test_las_tablas_sha256_del_readme_de_campana_coinciden_con_los_archivos -q` y registrar el resultado (debe pasar antes de editar el README). Si falla, detenerse y reportarlo como fallo preexistente.
- [x] 0.4 **[CHECKPOINT DE LOS AUTORES — BLOQUEA EL GRUPO 1]** Confirmar por escrito la autorización para crear y publicar el tag (acción HIGH). Registrar la respuesta; sin autorización no se ejecutan 1.2 ni 1.5 y se aplica la rama de salvedad de 1.7.
- [x] 0.5 Releer el índice de `numeros-canonicos.md` y fijar el primer número de sección libre (hoy la última es `3.33`; esperado `3.34`). Registrar el número elegido.

## 1. Tag de archivo (bloque A, HIGH)

- [x] 1.1 Verificar que no existe un tag homónimo (`git tag --list 'archivo/*'`) y que `git cat-file -t 561b3c4` sigue devolviendo `commit`; confirmar el SHA completo `561b3c480da718b5d681a126b7597170aa7986c0`. (OOS «Preservación»)
- [x] 1.2 Crear el tag anotado `archivo/corrida-fuera-de-muestra-561b3c4` sobre `561b3c480da718b5d681a126b7597170aa7986c0`, con mensaje que declare: propósito, SHA completo, asunto y fecha del commit, SHA-256 de las predicciones y del reporte, «no es una release de la tesis» y «no reescribe la historia». (OOS «Preservación»; TD «Reproducibilidad»)
- [x] 1.3 Verificar en local: `git cat-file -t archivo/corrida-fuera-de-muestra-561b3c4` → `tag`; `git rev-parse archivo/corrida-fuera-de-muestra-561b3c4^{commit}` → el SHA completo; `git ls-tree -r <tag> -- App/Backend/app/classifiers docs/prompt_gemini.txt App/Backend/app/config/settings.py App/Backend/app/constants.py` muestra el árbol de fuentes; `git cat-file -e <tag>:evaluation/data/campana/predicciones_independiente.json` falla (el tag no contiene el artefacto). (OOS «Preservación»)
- [x] 1.4 Verificar que la release no se movió: `git for-each-ref refs/tags/v1.4.1 --format='%(objecttype) %(objectname) %(*objectname)'` idéntico a la línea de base; `git tag --list 'v*'` sin cambios. (OOS «Preservación»)
- [x] 1.5 Publicar solo el ref del tag: `git push origin refs/tags/archivo/corrida-fuera-de-muestra-561b3c4` (nunca `main` ni una rama). Antes, si se quiere, `git push --dry-run origin refs/tags/archivo/corrida-fuera-de-muestra-561b3c4`. (OOS «Preservación»)
- [x] 1.6 Verificar en el remoto y en un clon limpio: `git ls-remote --tags origin` devuelve el tag y su línea `^{}` con el SHA; un `git clone` nuevo contiene el tag y permite `git ls-tree`; en un clon existente, `git fetch origin 'refs/tags/archivo/*:refs/tags/archivo/*'` lo trae. (OOS «Preservación»)
- [x] 1.7 **[CONDICIONAL]** Si el push no se autoriza o se rechaza: no crear un tag local huérfano como sustituto; documentar la causa y aplicar la salvedad explícita de D5 en README y tesis, nombrando `1b17e55` y los SHA-256, sin afirmar que el commit no existe. Registrar la decisión. (OOS «Preservación»; TD «Reproducibilidad») — **no aplica**: el push se publicó con éxito.

## 2. README de la campaña (bloque B, LOW)

- [x] 2.1 Extender la «Nota de vigencia del `commit` `561b3c4`» de `evaluation/data/campana/README.md` para nombrar el tag `archivo/corrida-fuera-de-muestra-561b3c4`, el SHA completo, el árbol de fuentes que preserva y los comandos de verificación (D4), conservando la afirmación de que el commit no es alcanzable desde `main` y que lo versionó `1b17e55`. (OOS «Preservación»; TD «Reproducibilidad»)
- [x] 2.2 Declarar en la misma nota la frontera de D3: el tag preserva el árbol de fuentes, no `predicciones_independiente.json` ni `reporte_independiente.md`; esos archivos se versionaron en `1b17e55` y sus SHA-256 son `d5ee19f7…` y `304dffcf…`. No agregar una línea `- sha256:` nueva ni una tabla `| Archivo | SHA-256 |` nueva; citar los valores en prosa. (OOS «Preservación»; TD «Reproducibilidad»)
- [x] 2.3 **Red de seguridad:** volver a correr las dos pruebas de 0.3 y verificar que siguen verdes; en particular, que el primer `- sha256:` del README sigue siendo el de `doble_etiquetado.csv` (`8b30b15b…`) y que no se agregó una fila SHA-256 nueva. (OOS «Preservación»; TD «Reproducibilidad»)
- [x] 2.4 Verificar con `rg` que la nota contiene el tag, el SHA completo y los dos SHA-256, y que no afirma que el tag contiene los artefactos ni que el commit no existe. (TD «Reproducibilidad»)

## 3. Memo, tesis y registro (bloque C, MEDIUM; tras 0.4)

- [x] 3.1 Agregar la sección aditiva `### 3.N` (primer libre; ver 0.5) a `docs/Tesis/Correcciones/numeros-canonicos.md` con el tag, el SHA completo, los dos SHA-256, el commit que versionó los artefactos y la topología esperada (`merge-base` → `1`); declarar que no reemplaza ningún valor previo. (TD «Reproducibilidad»)
- [x] 3.2 Agregar una o dos oraciones al final del párrafo «Diseño de la validación fuera de muestra» de `04-marco-metodologico.tex:100`: el árbol de fuentes de la corrida se preserva por el tag `archivo/corrida-fuera-de-muestra-561b3c4` y los artefactos versionados se identifican por sus SHA-256; sin datos nuevos. (TD «Reproducibilidad»)
- [x] 3.3 **[CONDICIONAL]** Agregar una remisión de una línea en `07-resultados.tex`, `subsec:validacion-fuera-muestra`, solo si no agrega páginas; si no, omitir y registrar la decisión. (TD «Reproducibilidad») — **omitida**: se prefirió no arriesgar la neutralidad de páginas; el requisito lo cubre la declaración metodológica de `04`.
- [x] 3.4 **[CONDICIONAL]** Si se aplicó la salvedad de 1.7, declararla en `08-discusion.tex` junto a las limitaciones, con remisión; si el tag se publicó, no agregar una limitación nueva y registrar la decisión. (TD «Reproducibilidad») — **no aplicada**: el tag se publicó, la falta de preservación deja de ser una limitación (D6).
- [x] 3.5 Agregar en `docs/Tesis/Correcciones/dictamen-correcciones.md` la entrada que cierra la observación de reproducibilidad del dictamen post-`v1.3.0`, con el tag, el SHA y los archivos afectados.
- [x] 3.6 Compilar con XeLaTeX y verificar `\@abspage@last{155}`, cero referencias indefinidas y cero etiquetas duplicadas. Si la declaración empuja una página, compensar dentro del mismo párrafo sin retirar contenido científico. (TD «Reproducibilidad»)
- [x] 3.7 Verificar con `rg -n "c-[0-9]{3}"` sobre `sections/*.tex` que no se agregaron identificadores internos de cambio fuera de comentarios; y que el resumen y el *abstract* no cambiaron de conteo de palabras. (TD «Reproducibilidad»)

## 4. Verificación de cierre

- [x] 4.1 Repetir D4 completo: tag local anotado, `rev-parse^{commit}`, `ls-remote --tags origin` con la línea `^{}`, clon nuevo con el tag y `ls-tree` inspeccionable, `merge-base --is-ancestor` → `1` registrado como topología esperada. (OOS «Preservación»)
- [x] 4.2 Confirmar con `git diff --stat` que no cambiaron `App/`, `n8n/`, el clasificador, `docker-compose.yml`, la configuración, el corpus, `predicciones_independiente.json`, `reporte_independiente.md` ni se movió ningún tag `v*`. (OOS «Preservación»)
- [x] 4.3 Correr `openspec validate c-223-preservar-el-commit-de-la-corrida-fuera-de-muestra --strict` y verificar que pasa. (OOS «Preservación»; TD «Reproducibilidad»)
- [x] 4.4 Ejecutar la suite de `evaluation/` que cubre el README (`cd evaluation && pytest tests/test_doble_etiquetado.py tests/test_campana.py -q`) y confirmar que no hay regresiones.
- [x] 4.5 Dejar a cargo del orquestador la actualización de `CHANGES.md` (FASE 75), la apertura del PR de la documentación y el `engram sync`; no pushear `main` ni crear la release en este change.

## 5. Cierre y handoff

- [x] 5.1 Guardar en Engram el resumen del change con el nombre, el tag, el SHA, los SHA-256 y el resultado de las verificaciones.
- [x] 5.2 Reportar al orquestador: tag publicado (o salvedad aplicada), archivos modificados, resultado de `openspec validate --strict` y páginas del PDF.
