# Design — c-111 — Version y trazabilidad de la version evaluada

## Context

Ver `proposal.md` para la motivacion. Estado relevante:

- El repositorio tiene CERO tags (`git tag -l` vacio) y el `HEAD` de `RamaLuca` es
  `16a7dfea...`. El remoto es `origin` (`github.com/lucaGomezB/...`).
- `sections/12-anexos.tex:19` (`sec:anexo-repositorio`) YA anticipa el tag `v1.0.0`
  y declara su creacion como "accion pendiente". Es un puntero sin resolver.
- `docs/Tesis/Correcciones/dictamen-correcciones.md` registra la accion diferida OQ6:
  crear el tag `v1.0.0` sobre el commit entregado al jurado y consignar el hash
  completo en el Anexo B.
- `openspec/specs/tesis-document/spec.md` ya exige (requisito "Coherencia tecnica
  entre la tesis y el sistema implementado", escenario "Punteros de repositorio
  validos") que todo tag referenciado exista y tenga su hash registrado.
- Secuencia de correcciones vigente: c-104..c-110 son changes de contenido que
  reescriben `sections/*.tex`. El tag DEBE reflejar la fuente FINAL corregida.

## Goals / Non-Goals

**Goals:**

- Resolver el puntero `v1.0.0` con un tag anotado real sobre la fuente final.
- Consignar el hash completo del commit evaluado en el manuscrito y en el registro
  de correcciones, de forma verificable.
- Publicar el tag para trazabilidad externa.

**Non-Goals:**

- No se corrige contenido cientifico, bibliografia ni codigo del sistema.
- No se re-etiqueta sobre fuentes intermedias.
- No se introduce un sistema de versionado semantico nuevo; se usa el tag ya
  anticipado por el documento.

## Decisions

### D1 — Tag anotado `v1.0.0` sobre la fuente final

Se crea un **tag anotado** `v1.0.0` (no lightweight) sobre el commit cuya fuente
compila el PDF evaluado. Nombre tomado del propio documento y de OQ6.

- Alternativa descartada: tag lightweight. No lleva mensaje/fecha/autoria y es
  menos auditable.
- Alternativa descartada: renombrar el tag (p. ej. `tesis-v9-evaluada`). Requeriria
  editar la afirmacion existente del Anexo B y romperia la continuidad con OQ6.

### D2 — No circularidad del hash (decision central)

Un commit no puede contener su propio hash. Se adopta la convencion "etiquetar y
luego documentar":

1. Aplicados c-104..c-110 y recompilado el manuscrito, se confirma el commit final
   de contenido `C1` en la punta de `RamaLuca`.
2. Se crea el tag anotado `v1.0.0` sobre `C1`; `H = git rev-parse v1.0.0^{commit}`
   es el hash evaluado.
3. En un commit **de documentacion** `C2` (no altera contenido cientifico) se inserta
   `H` en `12-anexos.tex` y en `dictamen-correcciones.md`, y se recompila el PDF.
4. El tag permanece sobre `C1` (la fuente evaluada). El PDF de `C2` es el que
   consigna el hash.

- Alternativa descartada: re-etiquetar `C2`. Moveria `H` a `C2` y dejaria el hash
  consignado (`C1`) desalineado con el tag; el tag no debe moverse.
- Alternativa descartada: omitir el hash en el manuscrito y dejarlo solo en el
  registro. Incumple OQ6 ("consignar el hash completo en el Anexo B").

### D3 — Lugar de la nota

La nota vive en `sections/12-anexos.tex`, `sec:anexo-repositorio`, en el parrafo que
hoy declara la accion pendiente: se reemplaza ese parrafo, no se agrega contenido
extenso. Opcional y diferible: exponer la version en `\hypersetup{pdfkeywords}`
(ver OQ-A).

- Alternativa descartada: la portada (`00-portada.tex`). c-103 fijo su contenido y
  su presupuesto de pagina; un hash no pertenece a la identidad institucional.

### D4 — Secuenciacion (gate de cierre)

c-111 es el change de **cierre** de la secuencia de correcciones. Depende de
c-104..c-110. El tag NO se crea hasta que todos esten archivados. Esto se
materializa como gate de prerrequisito en `tasks.md` (grupo 0) y como escenario del
delta spec ("Sin tag sobre fuente intermedia").

### D5 — Registro del hash en dos lugares

El hash se consigna en (a) el Anexo B del manuscrito y (b) el registro de
trazabilidad acumulativo `docs/Tesis/Correcciones/dictamen-correcciones.md`. Al
archivar el change, `CHANGES.md` documentara el cierre (fuera del alcance de
`apply` de `.tex`).

### D6 — Capacidad modificada

Se modifica `tesis-document`. El cambio es de comportamiento observable del
documento y del repositorio (tag existente + hash consignado), por lo que requiere
delta spec. No se modifica `tesis-numeros-canonicos` ni ninguna capacidad de
software.

## Risks / Trade-offs

- **[Tag sobre fuente intermedia]** → gate del grupo 0: verificar con
  `openspec list --json` que c-104..c-110 estan archivados y con `git status` que el
  arbol esta limpio antes de etiquetar.
- **[Desalineacion hash/tag]** → el hash consignado se obtiene con
  `git rev-parse v1.0.0^{commit}` DESPUES de crear el tag; se verifica coincidencia
  exacta antes de cerrar.
- **[Presupuesto de paginas]** → el plan de correcciones apunta a un tope de
  paginas; la nota REEMPLAZA un parrafo existente, por lo que no agrega paginas. Se
  registra el conteo de partida y se exige que no aumente.
- **[Tag local sin publicar]** → tarea explicita de `git push origin v1.0.0` y
  verificacion con `git ls-remote --tags origin v1.0.0`.
- **[Dependencia rígida]** → si c-104..c-110 se retrasan, c-111 no puede aplicarse.
  Es intencional: la trazabilidad exige la fuente final.

## Migration Plan

1. Gate: confirmar c-104..c-110 archivados y arbol limpio.
2. Recompilar y registrar el conteo de paginas de partida.
3. Editar `12-anexos.tex` para que la version evaluada se identifique con el tag
   `v1.0.0` (sin el hash todavia, que aun no existe).
4. Recompilar; commit `C1`.
5. Crear tag anotado `v1.0.0` sobre `C1`; publicar en `origin`.
6. Calcular `H`; insertar `H` en `12-anexos.tex` y en `dictamen-correcciones.md`;
   recompilar; commit `C2`.
7. `openspec validate --strict`; archivar.

**Rollback**: `git tag -d v1.0.0` (+ borrado remoto) y `git revert` de `C2` y `C1`.
Sin estado externo ni migraciones.

## Open Questions

- **OQ-A (diferible)**: si conviene exponer ademas la version/hash en los metadatos
  PDF (`\hypersetup`). La nota en el Anexo B satisface el requisito; agregarlo a los
  metadatos es opcional y no altera spec, enfoque ni tareas. Default: solo Anexo B.
- **OQ-B (diferible)**: la redaccion exacta de la nota (idioma y formato del hash,
  mayusculas/minusculas). No afecta la verificabilidad; se resuelve en `apply`.
