# Proposal: Preservar el commit de la corrida fuera de muestra

## Why

El dictamen CONEAU posterior a `v1.3.0` observó que «el commit que registra la primera corrida
fuera de muestra (`561b3c4`) no es alcanzable desde ninguna rama ni tag del repositorio: quedó como
objeto colgante, de modo que no se reproduce desde un clon y la corrida que identifica no es
reconstruible» (`auditorias/Dictamen_Tesis_v10_post-v1.3.0_5734ea8_CONEAU_2026-11-13.md:72`).

c-221 ya documentó la salvedad en `evaluation/data/campana/README.md` (la nota de vigencia de
`561b3c4`), pero la documentación no hace viajar el objeto: un `fetch` o un `clone` no trae un
commit colgante. La tesis tampoco declara la preservación. El resultado es que un evaluador con un
clon limpio no puede inspeccionar el árbol de fuentes con el que se generó la corrida, aunque los
artefactos (`predicciones_independiente.json` y `reporte_independiente.md`) sí estén versionados.

La causa raíz es de conservación, no de datos: el commit existe localmente
(`git cat-file -t 561b3c4` devuelve `commit`), pero ningún ref lo ancla. La corrección honesta es
anclarlo con un tag de archivo publicado, sin reescribir la historia ni fabricar una pertenencia a
`main` que no existe.

## What Changes

| Bloque | Qué cambia | Gobernanza |
|---|---|---|
| **A. Tag de archivo** | Crear un tag anotado `archivo/corrida-fuera-de-muestra-561b3c4` sobre `561b3c480da718b5d681a126b7597170aa7986c0`, con mensaje que declare el propósito, el SHA completo, el SHA-256 de los artefactos y que no es una release. Publicarlo en `origin` para que el objeto viaje con `fetch`/`clone`. No se mueve ningún tag de release. | HIGH (acción hacia afuera; confirmación expresa) |
| **B. Documentación de la campaña** | Actualizar la nota de vigencia de `evaluation/data/campana/README.md` para nombrar el tag de archivo, el SHA completo, el árbol preservado y los comandos de verificación; conservar la afirmación de que el commit no es alcanzable desde `main` y que lo versionó `1b17e55`. | LOW |
| **C. Declaración en la tesis** | Agregar una declaración breve en el apartado metodológico del diseño fuera de muestra (`04-marco-metodologico.tex:100`) y, si corresponde, en resultados o limitaciones: el commit de la corrida se preserva por el tag de archivo, con su nombre, y los SHA-256 de `predicciones_independiente.json` (`d5ee19f7…`) y `reporte_independiente.md` (`304dffcf…`). Sin datos nuevos ni afirmaciones no verificadas. Registrar la cifra y la procedencia en una sección aditiva del memo canónico. | MEDIUM |
| **D. Especificaciones** | Delta de `evaluation-out-of-sample-validation` (OOS-025: el commit de la corrida se preserva por tag publicado o se declara la salvedad explícita) y de `tesis-document` (modificación de «Reproducibilidad declarada»: la tesis y la documentación nombran el tag y los SHA-256). | LOW |

**No objetivos.**

- No se reescribe `predicciones_independiente.json`, su `cache_meta` ni el commit de la corrida.
- No se reejecuta la corrida, no se invoca a Gemini y no hay llamadas pagas.
- No se reescribe la historia ni se hace que `561b3c4` sea ancestro de `main`: el tag conserva el
  objeto, no cambia la topología. `git merge-base --is-ancestor 561b3c4 origin/main` seguirá
  devolviendo `1` y eso no es un defecto de este change.
- No se mueven ni se borran `v1.0.0` a `v1.4.1`; el tag nuevo no es una release de la tesis.
- No se toca `App/`, `n8n/`, el clasificador, `docker-compose.yml`, la configuración, el corpus ni
  las predicciones.
- No se inventa procedencia, fecha ni contenido del commit.
- No se edita `CHANGES.md` en esta fase (lo actualiza el orquestador al aplicar).

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `evaluation-out-of-sample-validation`: se agrega OOS-025, que exige preservar y publicar el
  commit de la corrida fuera de muestra mediante un tag de archivo, o declarar la salvedad
  explícita si no puede publicarse, con verificación por clon limpio.
- `tesis-document`: se modifica «Reproducibilidad declarada» para exigir que la tesis y el README
  nombren el tag de archivo y los SHA-256 de las predicciones y del reporte, además de la
  alcanzabilidad desde `main` ya declarada.

`evaluation-framework` no se modifica: la obligación es específica del corpus fuera de muestra y su
commit de corrida, y vive mejor en la capacidad que ya gobierna esos artefactos. Duplicarla en
`evaluation-framework` fragmentaría la regla.

## Impact

| Área | Impacto | Descripción |
|---|---|---|
| Repositorio remoto (`origin`) | Nuevo ref | Tag anotado `archivo/corrida-fuera-de-muestra-561b3c4`, publicado |
| `evaluation/data/campana/README.md` | Modificado | Nota de vigencia con el tag, el SHA completo, el árbol y los comandos de verificación |
| `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` | Modificado | Declaración de preservación en el apartado del diseño fuera de muestra |
| `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` y/o `08-discusion.tex` | Modificado condicional | Remisión o limitación, solo si el diseño confirma que aporta |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Nuevo (aditivo) | Sección con el tag y los SHA-256, sin reemplazar valores previos |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Nuevo (aditivo) | Entrada que cierra la observación de reproducibilidad del dictamen |
| `openspec/specs/…` | Delta | OOS-025 y «Reproducibilidad declarada» |

Sin cambios en `App/`, `n8n/`, el clasificador, la configuración, los corpus ni las predicciones.
Cero llamadas a Gemini.

## Risks

| Riesgo | Prob. | Mitigación |
|---|---|---|
| El remoto rechaza el push del tag (permisos, protección) | Media | Verificar antes con `git push --dry-run`; si no se puede publicar, aplicar la rama de salvedad explícita del spec (README y tesis declaran la limitación) sin afirmar que el commit no existe |
| Confundir el tag de archivo con una release y alterar la versión entregada | Baja | Prefijo `archivo/`, mensaje anotado que lo declara fuera de la línea de releases y verificación de que `v1.4.1` no se mueve |
| El tag no viaja en clones o fetches selectivos | Baja | Verificar con un clon nuevo y con `git fetch origin refs/tags/archivo/*:refs/tags/archivo/*`; documentar el refspec |
| Deriva de los SHA-256 si se regeneran los artefactos | Baja | No se regeneran; se toma el SHA de los archivos versionados y se verifica con `sha256sum` |
| Aumento del PDF por la declaración | Media | Declaración de una a dos oraciones dentro de un párrafo existente; verificar `abspage@last` y compensar dentro del mismo párrafo si hace falta |
| Afirmar por error que el tag hace alcanzable el commit desde `main` | Media | La prosa y el spec distinguen preservación por ref de ancestría; una verificación con `git merge-base --is-ancestor` documenta que sigue siendo `1` y no se reporta como falla |

## Rollback Plan

- Si el tag no se publicó todavía: `git tag -d archivo/corrida-fuera-de-muestra-561b3c4` y revertir
  la documentación con `git revert`.
- Si ya se publicó: no se borra ni se mueve el tag. Se documenta la corrección en el README y en la
  tesis; si el tag quedó mal, se crea uno nuevo que lo supere y se declara la relación.
- La declaración de la tesis y el README se revierten con `git revert` del commit que los modificó.

## Dependencies

- c-191 (corrida fuera de muestra y commit `561b3c4`), c-221 (nota de vigencia y observación del
  dictamen) y c-222 (estado vigente de la entrega, `v1.4.1`).
- Autorización expresa de los autores para crear y publicar el tag (bloque HIGH de A).

## Success Criteria

- [ ] El tag anotado existe, apunta a `561b3c480da718b5d681a126b7597170aa7986c0` y `git ls-remote --tags origin` lo devuelve.
- [ ] Un clon limpio contiene el tag y permite inspeccionar el árbol con `git ls-tree`.
- [ ] El README y la tesis nombran el tag y los SHA-256 de las predicciones y del reporte.
- [ ] `git merge-base --is-ancestor 561b3c4 origin/main` sigue devolviendo `1` y la documentación no lo presenta como falla.
- [ ] Ningún tag de release se movió; `git diff --stat` no toca `App/`, `n8n/`, el corpus ni las predicciones.
- [ ] `openspec validate c-223-preservar-el-commit-de-la-corrida-fuera-de-muestra --strict` pasa.
