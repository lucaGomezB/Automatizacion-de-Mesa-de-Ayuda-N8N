## Context

El change es documental y cierra la omision de la URL explicita en el anexo de repositorio, la incoherencia de la version bibliografica con la release publicada y la publicacion de la release `v1.1.1`. Ver `proposal.md` (Why). Restricciones que condicionan el diseno:

- **Presupuesto de paginas <= 101** (criterio duro). El PDF actual mide exactamente 101 paginas.
- **Solo se edita dentro de `docs/Tesis/v10 (IA)/`** y `docs/Tesis/Correcciones/dictamen-correcciones.md`. No se toca `v9 (IA)`, `auditorias/` ni codigo de aplicacion.
- **Tags existentes inmutables**: `v1.0.0`, `v1.0.1` y `v1.1.0` no se mueven; se crea un tag anotado NUEVO `v1.1.1`.

Estado verificado de las fuentes (solo lectura):

- `12-anexos.tex:17-23` (`sec:anexo-repositorio`) menciona el repositorio solo via `\parencite{Gomez2026_repositorio}` (lineas 19 y 23); la linea 19 declara el tag `v1.1.0` y la 21 el hash `7103b649d8c4f51737ad6ad4095dad22c9406400`.
- `Bibliography_base.bib:613-619` (`@misc{Gomez2026_repositorio}`): `title = {Automatizaci\'on de Mesa de Ayuda {N8N} (Version 1.0.0)}`, con `url = {https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N}`, `author`, `year` y `note` correctos.
- `preamble.tex:87` carga `hyperref` con `hidelinks`; la linea 145 define `\newcommand{\urlref}[1]{\href{#1}{#1}}` (definido pero sin uso en las secciones).
- `08-discusion.tex:58` ya renderiza URLs largas mediante `\url{...}` en notas al pie (precedente de estilo en el documento).
- Tags vigentes: `v1.0.0` -> `61a6b117dd1321fbee25f9792d9f29b884e5ac8d`, `v1.0.1` -> `bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0`, `v1.1.0` -> `7103b649d8c4f51737ad6ad4095dad22c9406400`.

## Goals / Non-Goals

**Goals:**

- Mostrar la URL del repositorio de forma explicita en el Anexo B, conservando la prosa y la cita.
- Alinear la version declarada en la entrada bibliografica con la release publicada.
- Publicar la release `v1.1.1` con tag anotado y hash consignado, sin mover los tags previos.
- Preservar el presupuesto de paginas (<= 101) y la neutralidad numerica.

**Non-Goals:**

- No se agregan secciones, figuras ni tablas nuevas.
- No se modifica el estilo de citas, los numeros canonicos ni las cinco cadenas de categoria.
- No se toca codigo de aplicacion, `evaluation/`, `CHANGES.md`, `v9 (IA)` ni `auditorias/`.
- No se mueve ni se recrea ningun tag existente.
- No se hace limpieza de macros no usadas (p. ej. `\urlref`): fuera de alcance.

## Decisions

### D1 - Usar `\url{}` en lugar de `\urlref{}` para la URL del anexo

`\urlref` esta definido como `\href{#1}{#1}`: renderiza la URL en la fuente del texto, clicable, pero el texto visible es un token unico de 65 caracteres sin puntos de corte, lo que arriesga un `Overfull \hbox`. `\url{}` (provisto por `hyperref`/`url`) es clicable, permite corte de linea en la puntuacion (`/`, `.`, `-`) y ya se usa en el documento para URLs largas (`08-discusion.tex:58`).

Se elige `\url{https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N}` por dos razones: (a) coherencia con el tratamiento de URLs ya establecido en el propio documento, y (b) su capacidad de corte protege el presupuesto de paginas y evita lineas desbordadas en el anexo.

**Alternativa considerada:** usar el macro propio `\urlref{}`. Se descarta porque su renderizado difiere del resto del documento y, al no permitir corte, introduce riesgo de desborde con una URL de 65 caracteres. El macro queda definido y sin uso; su limpieza no pertenece a este change.

### D2 - Version bibliografica igual a la release publicada (1.1.1)

El titulo de `Gomez2026_repositorio` declara la version entregada; como este change publica `v1.1.1`, el titulo pasa de `(Version 1.0.0)` a `(Version 1.1.1)`. Se modifica unicamente el token de version; `author`, `year`, `url` y `note` se conservan. No se agregan ni se quitan entradas.

**Alternativa considerada:** retirar la version del titulo por completo para evitar futuras desactualizaciones. Se descarta porque reduce la trazabilidad que el revisor busca y excede el cambio minimo pedido.

### D3 - Release `v1.1.1`: tag anotado y hash consignado, con orden estricto (patron C1/C2)

Se replica el patron C1/C2 de c-111/c-121:

- **C1:** `12-anexos.tex` reemplaza el tag `v1.1.0` por `v1.1.1`; el tag anotado `v1.1.1` se crea sobre el commit de cierre (que incluye la URL y la version bibliografica corregidas).
- **C2:** se consigna el hash completo de 40 caracteres del commit etiquetado en `12-anexos.tex` y en `docs/Tesis/Correcciones/dictamen-correcciones.md`.

**Orden obligatorio:** ediciones de contenido -> recompilar y verificar <= 101 -> commit de cierre -> crear el tag `v1.1.1` sobre ese commit y publicarlo -> consignar el hash (C2). El tag NO se crea hasta que las ediciones esten aplicadas y el PDF recompilado, de modo que la etiqueta refleje la fuente final. La consignacion del hash es, por necesidad, posterior al tag (un commit no puede contener su propio hash); el hash registrado corresponde al commit etiquetado y la recompilacion final del PDF incorpora ese valor, igual que en c-121.

**Alternativa considerada:** consignar el hash en el mismo commit etiquetado. Es imposible sin invalidar el hash. Se descarta.

### D4 - Presupuesto de paginas: la URL no debe superar las 101 paginas

La URL se inserta inline en un parrafo existente del anexo: es un token de 65 caracteres que refluye unas pocas lineas y no introduce contenido nuevo en bloque; el cambio de version bibliografica no altera el numero de entradas. El riesgo neto de sumar una pagina es bajo pero no nulo, dado que el documento esta exactamente en el limite.

**Mitigacion:** recompilar con XeLaTeX y contar las paginas; la URL se ubica al final de una oracion existente (no en una linea propia) para minimizar el reflujo; `\url{}` es cortable y no genera desbordes. Si el conteo superara 101, se aplicara un recorte minimo en la misma seccion antes de cerrar (criterio duro).

## Risks / Trade-offs

- **[La URL agrega reflujo y podria superar 101 paginas]** -> Recompilar y contar; ubicar la URL al final de una oracion existente; recortar localmente si se supera el limite.
- **[`Overfull \hbox` por una URL larga]** -> Usar `\url{}` (cortable en puntuacion) en lugar de `\urlref{}` (D1).
- **[Desfase temporal entre tag y hash]** -> Orden estricto C1/C2 (D3); la consignacion del hash es un paso de metadatos posterior al tag, que no altera la revision etiquetada.
- **[Reaparicion de version obsoleta en la bibliografia]** -> Se corrige el token y se verifica que no quede `(Version 1.0.0)`; futuras releases repetiran el ajuste.
- **[Creacion prematura del tag]** -> El tag solo se crea tras aplicar las ediciones y recompilar (D3, verificado en `tasks.md`).

## Migration Plan

1. Editar `12-anexos.tex`: agregar `\url{...}` en `sec:anexo-repositorio` (D1) y reemplazar el tag `v1.1.0` por `v1.1.1`.
2. Editar `Bibliography_base.bib`: titulo de `Gomez2026_repositorio` de `(Version 1.0.0)` a `(Version 1.1.1)`.
3. Recompilar con XeLaTeX (`latexmk -xelatex main.tex`) y verificar ausencia de errores fatales, referencias indefinidas y conteo <= 101 paginas.
4. Ejecutar la verificacion de citas (cero huerfanas, cero sin usar).
5. Hacer el commit de cierre (C).
6. Crear el tag anotado `v1.1.1` sobre C y publicarlo en `origin`.
7. Consignar el hash de 40 caracteres de C en `12-anexos.tex` y en `docs/Tesis/Correcciones/dictamen-correcciones.md` (C2) y recompilar el PDF final.
8. Rollback: `git checkout <commit-previo> -- "docs/Tesis/v10 (IA)/"` y recompilar; si el tag `v1.1.1` ya se publico, eliminarlo (`git tag -d v1.1.1` y `git push origin :refs/tags/v1.1.1`). Los tags `v1.0.0`/`v1.0.1`/`v1.1.0` no se tocan.

## Open Questions

Ninguna.
