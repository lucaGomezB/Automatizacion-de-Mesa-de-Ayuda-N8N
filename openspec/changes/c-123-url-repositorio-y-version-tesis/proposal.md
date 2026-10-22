## Why

El Anexo B de la tesis ("Repositorio de código fuente", `sec:anexo-repositorio` en `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`) referencia el repositorio público únicamente mediante la cita APA `\parencite{Gomez2026_repositorio}`: la URL no se muestra de forma explícita en el cuerpo del anexo, sino solo dentro de la entrada bibliográfica que se imprime en Referencias. Un lector que quiera acceder al código debe reconstruir la dirección desde la bibliografía. Además, el título de esa entrada (`Bibliography_base.bib`, entrada `Gomez2026_repositorio`) declara una versión obsoleta —"(Version 1.0.0)"— que no corresponde a la release efectivamente publicada, y el tag y el hash consignados en el manuscrito quedan desactualizados al publicar una nueva release. Se corrige mostrando la URL explícita, alineando la versión bibliográfica con la release publicada y publicando la release `v1.1.1` con su hash consignado.

## What Changes

- **URL explícita en el Anexo B:** en `12-anexos.tex` (`sec:anexo-repositorio`) insertar la URL del repositorio como enlace visible, conservando la prosa y la cita `\parencite{Gomez2026_repositorio}` existentes. Se usa `\url{https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N}` (decisión D1: `\url` en lugar de `\urlref`; ver `design.md`).
- **Versión bibliográfica alineada:** en `Bibliography_base.bib`, entrada `Gomez2026_repositorio`, corregir el título `(Version 1.0.0)` a `(Version 1.1.1)`.
- **Release `v1.1.1`:** en `12-anexos.tex` reemplazar el tag `v1.1.0` por `v1.1.1`; crear el tag anotado `v1.1.1` sobre el commit de cierre (patrón C1/C2 de c-111/c-121) y consignar su hash completo de 40 caracteres en `12-anexos.tex` y en `docs/Tesis/Correcciones/dictamen-correcciones.md`. El tag NO se crea hasta aplicar las ediciones de contenido y recompilar el PDF.
- No hay cambios de código de aplicación.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tesis-document`: se agregan tres requisitos que cierran la omisión de la URL explícita en el anexo de repositorio, la incoherencia de la versión bibliográfica con la release publicada y la publicación/etiquetado de la release `v1.1.1` con su hash consignado e inmutabilidad de los tags previos. Se preserva el presupuesto de páginas (<= 101).

## Impact

- Edita: `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`, `docs/Tesis/v10 (IA)/Bibliography_base.bib` y `docs/Tesis/Correcciones/dictamen-correcciones.md` (trazabilidad del hash).
- No toca: `docs/Tesis/v9 (IA)/`, `auditorias/`, código de aplicación (`App/`, `n8n/`), números canónicos (`docs/Tesis/Correcciones/numeros-canonicos.md`), las cinco cadenas de categoría, figuras, `evaluation/`, `CHANGES.md`.
- Presupuesto de páginas: criterio duro. El PDF está exactamente en 101 páginas; agregar una URL no debe superarlo (riesgo tratado en `design.md`).
- Tags `v1.0.0`/`v1.0.1`/`v1.1.0` inmutables; se crea un tag anotado NUEVO `v1.1.1` (ver `design.md`, D3).

## Rollback

Revertir los archivos `.tex` y `.bib` afectados con `git checkout <commit-previo> -- "docs/Tesis/v10 (IA)/..."` y recompilar el PDF. Si el tag `v1.1.1` ya se publicó, eliminarlo también (`git tag -d v1.1.1` y `git push origin :refs/tags/v1.1.1`) para no dejar una etiqueta sobre una fuente revertida. Los tags `v1.0.0`, `v1.0.1` y `v1.1.0` no se tocan.

## Success Criteria

- [ ] El Anexo B del PDF compilado muestra la URL del repositorio de forma explícita y conserva la cita `\parencite{Gomez2026_repositorio}`.
- [ ] La entrada `Gomez2026_repositorio` declara la versión `1.1.1`, coherente con la release publicada.
- [ ] El tag anotado `v1.1.1` existe, apunta al commit de cierre y está publicado en `origin`; su hash figura en el manuscrito y en `dictamen-correcciones.md`.
- [ ] El PDF compila sin errores fatales y su total es <= 101 páginas.
- [ ] Los tags `v1.0.0`, `v1.0.1` y `v1.1.0` permanecen en sus commits originales.
