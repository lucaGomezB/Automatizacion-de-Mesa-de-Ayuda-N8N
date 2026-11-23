# Design: Publicar la release siguiente a v1.6.2 y la nota de erratum

## Context

- c-247 quedo **aplicado y archivado el 2026-11-22**; el cuerpo de la tesis y la portada quedaron listos, salvo el marcador `[FECHA PENDIENTE]` de la portada.
- **Release vigente**: `v1.6.2` (tag anotado; commit de contenido `e7013127b565faa8f67a75284756cd4abe5c148f`). El PDF del arbol del tag imprime, en el Anexo B, el hash `17aa6d21` (candidato previo).
- **Instruccion OQ-04 (opcion A)** registrada en `docs/Tesis/Correcciones/dictamen-correcciones.md` (seccion c-247, tarea 8.1).
- **Patron C3/C4 vigente**: el tag anotado se crea sobre el commit que contiene el texto corregido y el PDF recompilado (C3); el commit siguiente consigna el hash del Anexo B (C4). Las releases previas (c-141, c-147, c-231) usaron ese patron.
- **Compilacion**: el host no tiene LaTeX; se compila por Docker (`texlive-thesis`). Advertencia: `resumir_registro_compilacion.py` arma `compilacion.md` desde `main.log`, `main.blg` y `main.pdf`.

## Goals / Non-Goals

**Goals:**

- Recompilar la tesis desde el arbol con c-247.
- Bump de version y fecha de portada; propagar la version (`README.md`, Anexo B, knowledge-base, inventario I.3).
- Registrar la **nota de erratum de `v1.6.2`** y compilar el PDF de la release de modo que su **Anexo B no imprima ningun hash** (C3), con el hash consignado en C4.
- Regenerar los derivados y `compilacion.md`; verificar los flotantes.
- Publicar el **tag anotado** en `origin` y **fusionar a `main`** con merge commit.

**Non-Goals:**

- Contenido de la tesis (lo cerro c-247).
- Mover, borrar o recrear `v1.6.2` ni ningun tag `v*` previo.
- `App/`, `n8n/`, `evaluation/`, `data/` y el corpus; los changes detenidos (c-228, c-229, c-230, c-232).

## Decisions

### D1 - Opcion (A) de OQ-04: el tag no se mueve

`v1.6.2` queda inmutable. Se registra una nota de erratum que identifica el hash impreso (`17aa6d21`) y el hash del commit de contenido (`e7013127`), y declara que el tag no se mueve ni se borra.

### D2 - Version de la release: `v1.6.3`

Bump de parche (correccion, sin cambio de alcance tematico). **Confirmada por los autores (2026-11-22).**

### D3 - Patron C3/C4 con el Anexo B sin hash en C3

En **C3** el Anexo B (`sec:anexo-repositorio`) **no imprime ningun hash**: remite al tag `v1.6.3` y a `compilacion.md`. En **C4** se consigna el hash del commit de contenido (C3) y se recompila. `compilacion.md` nombra el commit compilado en cada caso. Esto evita el defecto de `v1.6.2` (un PDF que imprimia el hash de otro commit).

### D4 - Fecha de portada

La fecha de la portada (`00-portada.tex`) es la de la release; reemplaza el marcador `[FECHA PENDIENTE]`.

### D5 - Derivados con los metodos verificados

Recompilar con el Docker de registro y regenerar los derivados (`tesis_para_evaluacion.txt`, `tesis_*.txt`, `docs/Tesis/tesis_ultima_version.pdf`) con los mismos metodos que las releases previas; `compilacion.md` con `resumir_registro_compilacion.py`.

### D6 - Gobernanza HIGH

El change toca el ejemplar defendido y publica un tag: ningun `.tex` ni tag sin OK expreso de los autores. El merge a `main` se hace con **merge commit** (nunca squash ni rebase).

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| El PDF del tag `v1.6.2` queda con el hash ajeno | Nota de erratum (D1); el tag no se mueve |
| Repetir el defecto (PDF del tag con hash de otro commit) | D3: C3 sin hash, C4 consigna y recompila |
| Merge que reescribe historia | Merge commit (D6); verificar con `git merge-base --is-ancestor` |
| Compilar en un entorno distinto al de registro | Docker `texlive-thesis` (D5) |

## Migration Plan

1. Bump de version y fecha de portada (portada, `README.md`, Anexo B, knowledge-base, inventario I.3).
2. Recompilar (C3) con el Anexo B sin hash.
3. Regenerar derivados y `compilacion.md`.
4. Verificar: flotantes, `verify_citations.py`, `openspec validate --strict`, cifras canonicas.
5. Commit C3; tag anotado `v1.6.3`; push.
6. Commit C4: consignar el hash del Anexo B y recompilar; push.
7. Merge a `main`; actualizar la copia de entrega y `README.md`.

Rollback: revertir los archivos tocados; el tag `v1.6.3` no se publica hasta el paso 5.

## Open Questions

Resueltas por los autores (2026-11-22):

- **OQ-1**: version = **`v1.6.3`**.
- **OQ-2**: el merge a `main` y la actualizacion de la copia de entrega van **en este change**.
- **OQ-3**: la nota de erratum va **solo en `dictamen-correcciones.md`**, no en el Anexo I.
