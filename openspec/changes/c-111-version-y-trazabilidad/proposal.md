# Proposal: c-111 — Version y trazabilidad de la version evaluada (cierre)

## Why

El dictamen CONEAU (item 13) exige "cerrar el tag de la versión evaluada y consignar
el hash del commit". El Anexo B de la tesis (`12-anexos.tex`, `sec:anexo-repositorio`)
YA afirma que el commit de referencia se consigna mediante el tag `v1.0.0`, pero ese
tag NO existe en el repositorio (`git tag -l` vacío) y el propio anexo declara su
creación como "acción pendiente". Es un puntero a un artefacto inexistente: el
documento bajo revisión no es trazable a un commit concreto. c-111 cierra ese
puntero al final de las correcciones.

## What Changes

- **Tag de la version evaluada**: crear un tag anotado `v1.0.0` sobre el commit cuya
  fuente compila el PDF evaluado, SOLO después de aplicar c-104..c-110 y recompilar.
- **Registro del hash**: reemplazar en `12-anexos.tex` (`sec:anexo-repositorio`) el
  lenguaje de "acción pendiente" por el hash completo (40 caracteres) del commit
  etiquetado, y consignarlo también en el registro de trazabilidad
  `docs/Tesis/Correcciones/dictamen-correcciones.md`.
- **Nota de version y trazabilidad**: el manuscrito SHALL identificar la version
  evaluada con el tag `v1.0.0` y su hash, de modo que el PDF entregado sea
  verificable contra el repositorio.
- **Publicacion**: publicar el tag en `origin` para que la trazabilidad sea externa.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: agrega el requisito de etiqueta de la version evaluada (tag
  anotado sobre la fuente final corregida) y el de trazabilidad del hash del commit
  evaluado en el manuscrito y el registro de correcciones.

## Impact

- `docs/Tesis/v9 (IA)/paper/sections/12-anexos.tex` (Anexo B, `sec:anexo-repositorio`).
- `docs/Tesis/Correcciones/dictamen-correcciones.md` (registro de trazabilidad OQ6).
- Estado de git: un tag anotado nuevo `v1.0.0` publicado en `origin`.
- Sin cambios de contenido científico ni de codigo; no toca `Bibliography_base.bib`.

## Risks

- El tag se corta sobre un commit que no es la fuente final (c-104..c-110 sin cerrar)
  → gate de prerrequisito: verificar que esos changes están archivados y el arbol limpio.
- El hash de un commit no puede figurar dentro de ese mismo commit (circularidad)
  → el hash se documenta en el commit de documentación inmediatamente posterior.
- Tag local sin publicar → `git push origin v1.0.0` obligatorio.

## Rollback

`git tag -d v1.0.0` (y `git push origin :refs/tags/v1.0.0` si se publicó) más
`git revert` del commit de documentación. Sin migraciones de datos ni estado externo.

## Success Criteria

- [ ] `openspec validate c-111-version-y-trazabilidad --strict` pasa.
- [ ] `git tag -l` muestra `v1.0.0` y `git rev-parse v1.0.0^{commit}` resuelve al commit final.
- [ ] El PDF compilado contiene el hash completo de 40 caracteres, igual al del tag.
- [ ] El texto "acción pendiente" sobre el tag no permanece en `12-anexos.tex`.
- [ ] El tag está publicado en `origin`.
