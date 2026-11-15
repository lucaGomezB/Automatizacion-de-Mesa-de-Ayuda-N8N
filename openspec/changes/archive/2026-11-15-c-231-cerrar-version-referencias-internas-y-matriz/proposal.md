# Proposal: Cerrar la versión, las referencias internas y la matriz de trazabilidad

## Why

La auditoría contra el último dictamen encontró tres defectos de cierre que dejan puntos sin resolver en el ejemplar de la defensa:

1. **Matriz desactualizada.** La sección de la devolución de segunda instancia (`docs/Tesis/Correcciones/dictamen-correcciones.md`, sección c-196) todavía marca `N-02`, `N-04`, `N-05` y `P16` como `PENDIENTE`, tanto en su tabla como en el inventario `PENDIENTE-AUTORES`. Es falso: el commit `c5b2fb9` (2026-11-11) los cerró y el texto vigente lo prueba (`12-anexos.tex:233-241` para `N-02` y `P16`; `04-marco-metodologico.tex:46` para `N-04`; `04-marco-metodologico.tex:66` para `N-05`). La matriz hace ver como pendientes observaciones ya resueltas.
2. **Tag que no contiene la evidencia.** La portada (`00-portada.tex:31`) y el Anexo B (`12-anexos.tex:58`) declaran la versión `v1.4.1`, pero los commits posteriores (`e7960e0`, `1f6a5ac`, `d3c13cd`, `1150d43`) añadieron evidencia que ese tag NO contiene (`git merge-base --is-ancestor 1f6a5ac v1.4.1` falla). El lector que sigue la referencia verificable no encuentra la evidencia: el defecto exacto que el dictamen penalizó. Además, `12-anexos.tex:58` llama `v1.4.1` «versión entregada» (documento) mientras `:62`/`:72` llaman `v1.3.0` «configuración entregada» (software); la misma palabra designa dos objetos.
3. **Referencias internas irresolubles.** El cuerpo cita el memo interno `docs/Tesis/Correcciones/numeros-canonicos.md` por número de sección (`Sección 3.31`, `3.33`, `3.35`, `3.36`), que el lector no puede resolver porque el memo no está anexado. La auditoría contó 6 ocurrencias; la verificación del executor encontró **12** (las 6 con espacio duro `Sección~3.xx` no estaban contadas).

## What Changes

| Bloque | Qué cambia | Gobernanza |
|---|---|---|
| **A. Matriz** | Corregir en `dictamen-correcciones.md` (sección c-196) las filas `N-02`, `N-04`, `N-05` y `P16` a su estado real (cerrada), con el fragmento verificable del texto vigente, su `archivo:línea` y la cita de `c5b2fb9`; retirarlas del inventario `PENDIENTE-AUTORES`, que queda sin filas pendientes. Sin afirmaciones nuevas. | MEDIUM |
| **B. Versión y tag** | Crear el tag anotado nuevo **`v1.5.0`** sobre el commit que cierra el change, que contiene la evidencia de c-223 a c-226 y el anexo nuevo; repuntar la portada, el Anexo B y la entrada bibliográfica `Gomez2026_repositorio`; consignar el hash completo en el commit posterior (patrón de `1965e33`/`8273`); desambiguar `versión entregada` (documento, `v1.5.0`) de `configuración entregada` (software, `v1.3.0`). | **HIGH** |
| **C. Anexo y referencias** | Agregar en `12-anexos.tex` un anexo nuevo (`sec:anexo-numeros-canonicos`) con los números canónicos citados, y solo ellos, cada uno con procedencia y estado; repuntar las 12 referencias internas a ese anexo; sección aditiva en el memo. El memo queda como fuente interna de verdad. | MEDIUM |

**No objetivos.**

- No se mide de nuevo, no se invoca Gemini y no se toca `App/`, `n8n/`, el clasificador, el corpus ni las predicciones.
- No se cambia ningún valor canónico vigente ni el texto científico: el anexo es una transcripción condensada del memo.
- No se mueven, recrean ni reapuntan tags publicados (`v1.4.1` y anteriores quedan intactos).
- No se crea ni publica el tag sin autorización expresa de los autores.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tesis-document`: se modifica «Versión entregada identificable y con la evidencia vigente» (tag nuevo que contiene la evidencia y desambiguación documento/software) y «Trazabilidad de la devolución de segunda instancia en el registro» (estados reales de la matriz); se agrega «Anexo de números canónicos citados y cuerpo sin referencias internas al memo».
- `tesis-numeros-canonicos`: se agrega el requisito de registro del anexo de números canónicos citados y de sus referencias, con procedencia y estado por valor.

`evaluation-framework` y `project-documentation` no se modifican.

## Impact

| Área | Impacto | Descripción |
|---|---|---|
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Modificado | Filas `N-02`/`N-04`/`N-05`/`P16` y inventario `PENDIENTE-AUTORES`; entrada de trazabilidad del change |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Aditivo | Sección nueva con el registro del anexo y sus referencias |
| `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` | Modificado | Anexo nuevo de números canónicos; Anexo B (tag, hash y desambiguación) |
| `docs/Tesis/v10 (IA)/paper/sections/00-portada.tex` | Modificado | Versión `1.5.0` |
| `docs/Tesis/v10 (IA)/paper/sections/{01,04,07,08,10}-*.tex` | Modificado | Las 12 remisiones internas repuntadas al anexo |
| `docs/Tesis/v10 (IA)/Bibliography_base.bib` | Modificado | Título de `Gomez2026_repositorio` a la versión nueva |
| `docs/Tesis/v10 (IA)/paper/{main.pdf,compilacion.md}` | Modificado | PDF recompilado y su registro |

Sin cambios en `App/`, `n8n/`, la configuración, el corpus ni las predicciones. Cero llamadas a Gemini.

## Risks

| Riesgo | Prob. | Mitigación |
|---|---|---|
| Crecer en páginas por el anexo | Alta | Anexo condensado (solo los valores citados); registrar el delta en el libro mayor; el exceso ya está declarado y honrado |
| Que el tag no contenga la evidencia declarada | Media | El tag se crea sobre el commit de contenido; verificación con `git show <tag>:` de cada artefacto citado |
| Repuntar la versión en un lugar y olvidar otro | Media | Tarea única que recorre portada, Anexo B y `.bib`, con `rg` de cierre |
| Romper la inmutabilidad de tags publicados | Baja | Solo se crea un tag nuevo; los anteriores no se tocan |
| Colisión de la letra del anexo (A-I existentes) | Media | Se anexa al final para no renumerar; la letra se fija al aplicar |
| Que una fila corregida se lea como observación nueva | Baja | Solo se cambia el estado y se cita el commit que la cerró; el fragmento es el vigente |

## Rollback Plan

`git revert` del commit del change: el anexo y las remisiones se revierten por archivo; las filas de la matriz vuelven a su estado previo; la sección del memo se retira sin tocar las anteriores. El tag `v1.5.0` se elimina (local y `origin`) solo antes de publicarse; una vez publicado, se marca como superado sin borrarse. Ningún valor canónico ni tag anterior se modifica, de modo que el rollback no deja huecos.

## Dependencies

- Cierra los pendientes de `c-196` (devolución de segunda instancia) y recoge la evidencia de `c-223`, `c-224`, `c-225` y `c-226`.
- El tag `v1.5.0` publica la fuente de esos changes y el anexo nuevo.
- No depende de `App/` ni de medición: todos los insumos están versionados.

## Success Criteria

- [ ] Las filas `N-02`, `N-04`, `N-05` y `P16` figuran cerradas con el fragmento vigente y la cita de `c5b2fb9`; `PENDIENTE-AUTORES` queda sin filas.
- [ ] El tag `v1.5.0` existe, es anotado y `git show v1.5.0:` encuentra la evidencia que la tesis cita; el Anexo B y la portada nombran la misma versión.
- [ ] La `versión entregada` (documento) y la `configuración entregada` (software) quedan desambiguadas en el Anexo B.
- [ ] El anexo de números canónicos reúne solo los valores citados, con procedencia y estado, sin cifras nuevas.
- [ ] `rg "Sección[~ ]3\.[0-9]{2}" sections/*.tex` no devuelve coincidencias en el cuerpo.
- [ ] `verificar_matriz_trazabilidad.py` reporta 0 fallas; el PDF compila con 0 referencias indefinidas y el delta de páginas queda en el libro mayor.
- [ ] `openspec validate c-231-cerrar-version-referencias-internas-y-matriz --strict` pasa.
