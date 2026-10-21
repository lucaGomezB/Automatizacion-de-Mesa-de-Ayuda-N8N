# Tasks — c-111 — Version y trazabilidad de la version evaluada

> Governance MEDIO. c-111 es el change de CIERRE: NO se aplica hasta que c-104..c-110
> esten archivados y el manuscrito recompilado. El tag DEBE reflejar la fuente FINAL.
> Las decisiones de orden y no-circularidad del hash estan en `design.md`. NO se
> altera contenido cientifico, bibliografia ni codigo.

## 0. Prerrequisitos (gate de secuenciacion)

- [ ] 0.1 Confirmar con `openspec list --json` que c-104, c-105, c-106, c-107, c-108,
  c-109 y c-110 estan ARCHIVADOS (no presentes como changes activos). Verificacion:
  ninguno aparece en la lista de changes activos.
- [ ] 0.2 Confirmar con `git status` que el arbol esta limpio y que `RamaLuca` es la
  rama actual. Registrar el hash de la punta (`git rev-parse HEAD`) como candidato `C1`.
- [ ] 0.3 Registrar el conteo de paginas de partida del PDF final corregido
  (`pdfinfo "docs/Tesis/v9 (IA)/paper/main.pdf" | grep Pages`).
- [ ] 0.4 Confirmar que NO existe ya un tag `v1.0.0` (`git tag -l v1.0.0` vacio).

## 1. Puntero del Anexo B sin el hash (pre-tag)

- [ ] 1.1 En `sections/12-anexos.tex`, `sec:anexo-repositorio`, reemplazar la frase
  que declara la creacion del tag como "accion pendiente" por una afirmacion de que
  la version evaluada se identifica con el tag `v1.0.0`. Verificacion: el parrafo ya
  no contiene "accion pendiente" ni "queda como accion pendiente".
- [ ] 1.2 Verificar que no se altero ningun otro parrafo del Anexo B ni el conteo de
  paginas respecto de 0.3.

## 2. Compilacion y commit de contenido (C1)

- [ ] 2.1 Compilar con la imagen local:
  `docker run --rm -v "<repo>/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`.
  Verificacion: sin errores fatales; registrar el conteo de paginas.
- [ ] 2.2 Confirmar que no hay referencias indefinidas nuevas ni etiquetas rotas.
- [ ] 2.3 Commit del cambio (sin crear aun el tag): commit `C1` con mensaje
  `docs(tesis): identificar la version evaluada con el tag v1.0.0 (c-111)`.
  Verificacion: `git rev-parse HEAD` = hash de `C1`; `git status` limpio.

## 3. Creacion y publicacion del tag

- [ ] 3.1 Crear el tag ANOTADO sobre `C1`:
  `git tag -a v1.0.0 -m "Version evaluada de la tesis (c-111)"`. Verificacion:
  `git cat-file -t v1.0.0` devuelve `tag`.
- [ ] 3.2 Verificar que el tag apunta a `C1`: `git rev-parse v1.0.0^{commit}` coincide
  con el hash de `C1` registrado en 2.3.
- [ ] 3.3 Publicar el tag: `git push origin v1.0.0`. Verificacion:
  `git ls-remote --tags origin v1.0.0` lo devuelve.

## 4. Registro del hash (post-tag, commit C2)

- [ ] 4.1 Calcular el hash evaluado `H = git rev-parse v1.0.0^{commit}` (40 caracteres).
- [ ] 4.2 Insertar `H` en `sections/12-anexos.tex`, `sec:anexo-repositorio`, junto al
  tag `v1.0.0`. Verificacion: el hash completo figura en el `.tex`.
- [ ] 4.3 Registrar `H` y el tag `v1.0.0` en
  `docs/Tesis/Correcciones/dictamen-correcciones.md` (cierre de OQ6).
  Verificacion: la entrada referencia el tag y el hash.
- [ ] 4.4 Compilar de nuevo con la imagen `texlive-thesis` y confirmar que el PDF
  renderiza la nota sin errores fatales y sin aumentar el conteo de paginas de 0.3.

## 5. Verificacion del change (OpenSpec)

- [ ] 5.1 Commit de documentacion `C2` con mensaje
  `docs(tesis): consignar el hash del commit evaluado (c-111)`.
- [ ] 5.2 Ejecutar `openspec validate c-111-version-y-trazabilidad --strict` y
  confirmar que pasa.
- [ ] 5.3 Ejecutar `openspec status --change c-111-version-y-trazabilidad --json` y
  confirmar `isPlanningComplete: true` y todas las tareas completas.
- [ ] 5.4 Verificacion cruzada final: el hash del manuscrito == `git rev-parse
  v1.0.0^{commit}` == el registrado en `dictamen-correcciones.md`; el tag esta en
  `origin`; `git status` limpio.
