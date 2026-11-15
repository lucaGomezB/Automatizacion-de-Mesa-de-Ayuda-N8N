# Tasks: Cerrar la versión, las referencias internas y la matriz de trazabilidad

Al final de cada tarea, entre paréntesis, el requisito del change que cumple, por nombre corto entre comillas angulares precedido de su capacidad: `TD` (`tesis-document`) y `NC` (`tesis-numeros-canonicos`). Nombres cortos: TD «Versión y tag»; TD «Matriz»; TD «Anexo»; NC «Registro del anexo». Las tareas de preparación y las verificaciones transversales no llevan paréntesis.

Este change NO escribe código de producción ejecutable: la Parte 1 corrige una tabla, la Parte 3 agrega un anexo y repunta remisiones, y la Parte 2 crea un tag. No aplica el ciclo TDD sobre código nuevo; la verificación se hace con los scripts de guardia del proyecto (`verificar_matriz_trazabilidad.py`, `verify_citations.py`, `resumir_registro_compilacion.py`), con LaTeX y con `rg`.

## 0. Preparación y verificación de estado

- [x] 0.1 Leer `proposal.md`, `design.md` (D1 a D6) y los dos specs delta.
- [x] 0.2 Capturar la línea de base: `git status`, `git rev-parse HEAD`, `git tag -l` y `git show v1.4.1 --no-patch --format=%H`. Registrar las 12 ocurrencias de `rg -n "Sección[~ ]3\.[0-9]{2}" "docs/Tesis/v10 (IA)/paper/sections"` y su archivo:línea. Registrar el conteo de páginas de `main.pdf` (`pdfinfo`).
- [x] 0.3 Releer `git show c5b2fb9 --stat` y confirmar las cuatro observaciones que cerró (`N-02`, `N-04`, `N-05`, `P16`). Confirmar en el `.tex` vigente el fragmento de cada una (`12-anexos.tex:233-241` y `04-marco-metodologico.tex:46,66`).
- [x] 0.4 Releer el índice de `numeros-canonicos.md` y fijar el primer número de sección libre (hoy el último es `3.37`; esperado `3.38`). Registrar el número elegido.
- [x] 0.5 **Red de seguridad:** correr `python docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` desde la raíz y `python verify_citations.py` desde `docs/Tesis/v10 (IA)/`; registrar el resultado de partida (si algo falla, detenerse y reportarlo como fallo preexistente).

## 1. Matriz de la devolución (TD «Matriz»)

- [x] 1.1 En `docs/Tesis/Correcciones/dictamen-correcciones.md`, sección "Dictamen v10 / v1.2.18 (2026-11-11) - c-196", cambiar el Estado de las filas `N-02`, `N-04` y `N-05` de "parcial: PENDIENTE (...)" a "cerrada (c5b2fb9, 2026-11-11)". No cambiar la observación ni la corrección. (TD «Matriz»)
- [x] 1.2 Retirar la fila `P16` del inventario `PENDIENTE-AUTORES` y declarar que no quedan pendientes de autores. Conservar la fila `N-16` con su estado vigente. (TD «Matriz»)
- [x] 1.3 Verificar el fragmento verificable y el `archivo:línea` de cada fila corregida contra el texto vigente; si el fragmento no aparece, ajustarlo al texto real (sin inventar). (TD «Matriz»)
- [x] 1.4 Correr `python docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` y confirmar 0 fallas. (TD «Matriz»)

## 2. Anexo de números canónicos y repunte (TD «Anexo»; NC «Registro del anexo»)

- [x] 2.1 Determinar la letra del anexo nuevo (esperado "Anexo J", al final de `12-anexos.tex`, después de `sec:anexo-trazabilidad`, para no renumerar los anexos A a I). Registrar la letra elegida. (TD «Anexo»)
- [x] 2.2 Redactar el anexo `sec:anexo-numeros-canonicos` con los valores citados de las secciones `3.31`, `3.33`, `3.35` y `3.36` del memo: cada valor con su cifra, su procedencia (archivo o comando) y su estado. Solo los valores citados; sin reproducir secciones completas ni introducir cifras nuevas. (TD «Anexo»)
- [x] 2.3 Repuntar las 12 ocurrencias de `Sección[~ ]3.xx` del cuerpo (`01-introduccion.tex:48`; `04-marco-metodologico.tex:78`; `07-resultados.tex:393`; `08-discusion.tex:56,62,84,114,117,121,125`; `10-recomendaciones.tex:34`) a `\autoref{sec:anexo-numeros-canonicos}`, sin cambiar la cifra ni el sentido de la oración. (TD «Anexo»)
- [x] 2.4 Verificar con `rg -n "Sección[~ ]3\.[0-9]{2}" "docs/Tesis/v10 (IA)/paper/sections"` que no queda ninguna ocurrencia en los capítulos del cuerpo (la única forma permitida del memo es su fuente interna, no el cuerpo). (TD «Anexo»)
- [x] 2.5 Agregar la sección aditiva `### 3.N` (ver 0.4) en `docs/Tesis/Correcciones/numeros-canonicos.md`: el rótulo del anexo, las secciones citadas, cada valor transcripto con procedencia y estado, y la declaración de que el memo es la fuente interna de verdad y el anexo no cambia valores. (NC «Registro del anexo»)
- [x] 2.6 Verificar con `git diff` dirigido que la sección es aditiva: solo líneas agregadas, sin reescritura de las secciones anteriores. (NC «Registro del anexo»)
- [ ] 2.7 Recompilar con XeLaTeX (`latexmk -xelatex main.tex`), correr `resumir_registro_compilacion.py` y verificar 0 referencias indefinidas, 0 citas indefinidas y 0 etiquetas duplicadas; registrar el total de páginas y el delta respecto de la línea de base. (TD «Anexo»)

## 3. Versión y tag (TD «Versión y tag») — HIGH

- [x] 3.1 **[CHECKPOINT DE LOS AUTORES — OQ1, BLOQUEA EL GRUPO]** Confirmar el número de versión `v1.5.0` (MENOR) frente a `v1.4.2` (PARCHE) y la letra del anexo (OQ2). Registrar la respuesta. (TD «Versión y tag»)
- [x] 3.2 Repuntar la versión en la portada (`00-portada.tex`, `Versión 1.5.0`), en el Anexo B (`12-anexos.tex:58`, tag `v1.5.0` y oración de reemplazo) y en la entrada bibliográfica (`Bibliography_base.bib`, `Gomez2026_repositorio`). Verificar con `rg "1\.4\.1"` que no quedan cadenas de versión sin actualizar fuera de las menciones históricas. (TD «Versión y tag»)
- [x] 3.3 Agregar en el Anexo B la oración que desambigua `versión entregada` (documento, `v1.5.0`) de `configuración entregada` (software, `v1.3.0`). (TD «Versión y tag»)
- [ ] 3.4 **C1 (commit de contenido):** dejar en el Anexo B la oración de reemplazo SIN imprimir el hash de `v1.4.1` ni de ninguna release previa; recompilar el PDF y regenerar `compilacion.md`. Confirmar que el PDF no imprime el hash previo. (TD «Versión y tag»)
- [ ] 3.5 **[AUTORIZACIÓN EXPRESA — OQ3]** Con la confirmación del autor, crear el tag anotado `v1.5.0` sobre C1 y publicarlo en `origin`. Confirmar con `git cat-file -t v1.5.0` (devuelve `tag`) y `git show v1.5.0:` que contiene la evidencia de c-223 a c-226 y el anexo nuevo. No tocar `v1.4.1` ni anteriores. (TD «Versión y tag»)
- [ ] 3.6 **C2 (commit posterior al tag):** reemplazar la oración de reemplazo por el hash completo de 40 caracteres de C1. Verificar con `git diff --stat v1.5.0 HEAD -- "docs/Tesis/v10 (IA)/paper/sections"` que cambia una sola línea. (TD «Versión y tag»)

## 4. Trazabilidad y verificación de cierre

- [x] 4.1 Agregar en `docs/Tesis/Correcciones/dictamen-correcciones.md` la entrada del change con la matriz de trazabilidad (filas corregidas, anexo nuevo, tag `v1.5.0`) y el libro mayor de páginas del anexo. 
- [x] 4.2 Correr `python docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` (0 fallas) y `python verify_citations.py` desde `docs/Tesis/v10 (IA)/` (PASS); confirmar con `rg` que no quedan `Sección[~ ]3.xx` en el cuerpo ni cadenas `1.4.1` vigentes.
- [x] 4.3 Confirmar con `git diff --stat` que no cambiaron `App/`, `n8n/`, el clasificador, la configuración, el corpus ni las predicciones.
- [x] 4.4 Correr `openspec validate c-231-cerrar-version-referencias-internas-y-matriz --strict` y verificar que pasa.
- [ ] 4.5 Dejar a cargo del orquestador la actualización de `CHANGES.md` y el `engram sync`; no pushear sin autorización.
- [x] 4.6 Guardar en Engram el resumen del change con el tag, el anexo, los valores repuntados y el resultado de las verificaciones; reportar al orquestador.

## Evidencia de verificación (obligatoria al reportar)

| Bloque | Verificación | Instrumento | Resultado esperado |
|---|---|---|---|
| Matriz | Estados de `N-02`/`N-04`/`N-05` y ausencia de `P16` en el inventario | `verificar_matriz_trazabilidad.py` | 0 fallas |
| Anexo y referencias | Sin `Sección[~ ]3.xx` en el cuerpo | `rg` | 0 coincidencias |
| Tag | Evidencia contenida y hash consignado | `git show v1.5.0:` y `git diff --stat` | artefactos presentes; 1 línea en C2 |
| Versión | Coherencia de portada, Anexo B y `.bib` | `rg "1\.4\.1"` | solo menciones históricas |
| Compilación | 0 referencias/citas indefinidas, 0 etiquetas duplicadas | `latexmk` + `resumir_registro_compilacion.py` | limpio; delta de páginas registrado |
| Cierre | Change válido | `openspec validate --strict` | válido |
