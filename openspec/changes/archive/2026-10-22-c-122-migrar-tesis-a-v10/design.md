## Context

See `proposal.md` - Why. Estado verificado del repositorio que condiciona el diseno:

- `docs/Tesis/v9 (IA)/` es la version previamente publicada (tag anotado `v1.0.1`); contiene 61 archivos en el arbol de trabajo y 60 versionados en git (`main.log` no esta versionado). Incluye fuente LaTeX (`paper/main.tex`, `paper/preambles/preamble.tex`, `paper/sections/*.tex`), figuras y assets, `Bibliography_base.bib`, `verify_citations.py`, `add_disclaimer.py`, `CLAUDE.md`, los dos `.docx`, los textos extraidos (`tesis_completa_extraida.txt`, `tesis_para_evaluacion.txt`) y artefactos de compilacion (`main.pdf/aux/bbl/bcf/blg/lof/lot/out/toc/run.xml`).
- `docs/Tesis/v9 (IA)/` NO contiene `tesis_para_agente.md`; ese archivo solo existe en `docs/Tesis/v7/`. v9/v10 exponen `tesis_completa_extraida.txt` y `tesis_para_evaluacion.txt`.
- `openspec/config.yaml` linea 48: `thesis: docs/Tesis/v7/tesis_para_agente.md`.
- `CHANGES.md` contiene 4 ocurrencias de `docs/Tesis/v9 (IA)` (lineas ~1680, 1714, 1871 y 2041), todas dentro de registros historicos.
- `openspec/specs/tesis-document/spec.md` contiene 5 ocurrencias de `docs/Tesis/v9 (IA)` (lineas ~434, 2227, 2262, 2766 y 2796), todas en rutas activas del spec vivo.
- `AGENTS.md` no contiene ninguna ocurrencia de `v9` (verificado con grep).
- El change dependiente `openspec/changes/c-121-observaciones-dictamen-v1-0-1/` (c-122 es su prerequisito) referencia `docs/Tesis/v9 (IA)/` en `proposal.md` (2), `design.md` (3) y `tasks.md` (1).

## Goals / Non-Goals

**Goals:**

- Crear `docs/Tesis/v10 (IA)/` como copia completa de `docs/Tesis/v9 (IA)/`.
- Dejar los punteros activos del proyecto resolviendo a v10 y v9 intacto.
- Fijar una regla explicita y auditable de que es "puntero activo" y que es "registro historico".

**Non-Goals:**

- No aplicar las recomendaciones editoriales (eso es c-121).
- No crear ni mover tags; no editar contenido de la tesis ni la referencia interna de version en `12-anexos.tex` (paso de cierre de c-121, tag futuro).
- No reescribir registros historicos ni limpiar residuos historicos ajenos al alcance (por ejemplo, la referencia a `docs/Tesis/v8 (IA)` en la linea 11 del spec vivo).

## Decisions

### D1 - Copia de trabajo como espejo completo con `cp -r`

Mecanismo exacto (desde la raiz del repo):

```
cp -r "docs/Tesis/v9 (IA)" "docs/Tesis/v10 (IA)"
```

- Es un espejo COMPLETO: incluye artefactos de compilacion, por decision del autor (v10 debe reproducir v9 sin depender de una recompilacion inmediata).
- Las comillas son obligatorias: las rutas contienen espacios y parentesis.
- Alternativas consideradas: (a) copiar solo la fuente versionada sin artefactos -> descartado, no cumple el "espejo completo" pedido; (b) clonar solo `paper/*.tex` -> descartado, perderia figuras, `.bib`, scripts y textos extraidos.
- Verificacion de paridad: contar archivos versionados con `git ls-files "docs/Tesis/v10 (IA)" | wc -l` (esperado 60) y comparar contra `git ls-files "docs/Tesis/v9 (IA)" | wc -l`. Se usa `git ls-files` y no `find` porque `main.log` no esta versionado (find da 61, git da 60).

### D2 - Puntero `thesis:` de `openspec/config.yaml`

Se REPUNTA a `docs/Tesis/v10 (IA)/tesis_completa_extraida.txt`.

- Razon: el proposito de la migracion es que los punteros activos resuelvan a la version vigente. `tesis_para_agente.md` es un documento curado para agentes, pero solo existe en v7 y esta STALE (tres versiones por detras); apuntar alli haria que los agentes lean un documento obsoleto. v10 no tiene ese archivo; `tesis_completa_extraida.txt` es el equivalente mas cercano (texto completo de la version vigente).
- Alternativas consideradas: (a) dejar v7 con justificacion de estabilidad -> descartado, contradice el objetivo y desinforma; (b) apuntar al directorio `docs/Tesis/v10 (IA)/` -> el campo tiene semantica de archivo, no de directorio; (c) apuntar a `tesis_para_evaluacion.txt` -> esta orientado a evaluacion, no a contexto general de agente.
- Caveat documentado: v10 no incluye un agente-doc curado. Producir un `tesis_para_agente.md` actualizado de v10 queda FUERA de alcance (posible change futuro).

### D3 - Regla de actualizacion: puntero activo vs registro historico

- **Puntero activo** (designa la ubicacion de trabajo vigente o destino de trabajo futuro) -> se repunta a `docs/Tesis/v10 (IA)`. Incluye: `openspec/config.yaml` (`thesis:`), la entrada NUEVA de estado actual en `CHANGES.md`, las rutas activas de `openspec/specs/tesis-document/spec.md` y las rutas de trabajo de los changes dependientes.
- **Registro historico** (documenta lo que ocurrio en el pasado) -> se preserva VERBATIM. Incluye: entradas fechadas `Actualizacion YYYY-MM-DD` de `CHANGES.md`, dictamenes de `auditorias/`, bitacoras de `docs/Tesis/Correcciones/`, changes de `openspec/changes/archive/` y los bloques de fase cuyo texto narra en pasado el trabajo hecho sobre v9. Solo si fuera imprescindible se agrega una nota entre corchetes; nunca se reescribe el pasado.
- Aplicacion concreta en `CHANGES.md`: las 4 ocurrencias de v9 (lineas ~1680, 1714, 1871, 2041) son historicas -> se preservan. La migracion se registra en una entrada NUEVA fechada `Actualizacion 2026-10-22 (migracion de la tesis a v10)` que contiene la ruta literal `docs/Tesis/v10 (IA)/`, declara v9 congelada y señala que c-121 es el proximo change de contenido (con c-122 como su prerequisito).
- Aplicacion concreta en `openspec/specs/tesis-document/spec.md`: las 5 ocurrencias de v9 son punteros activos -> se repuntan a `docs/Tesis/v10 (IA)` (`grep -c "docs/Tesis/v9 (IA)"` = 0 al final).
- `AGENTS.md`: sin ocurrencias de v9, sin cambios (se confirma con grep en la verificacion).

### D4 - Coordinacion con el change dependiente c-121

Se repuntan a v10 las rutas activas de `openspec/changes/c-121-observaciones-dictamen-v1-0-1/{proposal,design,tasks}.md`.

- Razon: c-121 es el change de contenido que se aplica DESPUES de esta migracion. Si sus artefactos siguen apuntando a v9, su aplicacion editaria la version congelada. Como v10 es copia byte a byte de v9, las lineas verificadas por c-121 siguen siendo validas.
- Alternativas consideradas: (a) dejar c-121 intacto y que se autocorrija al aplicarse -> riesgo alto de editar v9 por error; (b) excluir c-121 del alcance y registrar la deuda -> dejaria incompleto el objetivo "el trabajo futuro resuelve a v10". Se elige repuntar y dejarlo documentado aqui y en `tasks.md`.

### D5 - Sin efectos sobre versionado ni contenido

No se crea ni se mueve ningun tag de git. No se edita contenido de la tesis ni la referencia interna de version (`v1.0.1`/hash) en `12-anexos.tex`; el tag de cierre (`v1.1.0`) es paso de c-121.

## Risks / Trade-offs

- [v10 nace con artefactos de compilacion stale de v9] -> Intencional (espejo completo). No afecta la verificacion de la migracion; se recomienda recompilar en la primera edicion de contenido (c-121).
- [Editar accidentalmente `docs/Tesis/v9 (IA)/`] -> La copia precede a los repuntes; verificacion obligatoria de `git status` sin cambios en `docs/Tesis/v9 (IA)/`.
- [Rutas con espacios mal citadas] -> Usar comillas dobles en `cp` y en los greps (`"docs/Tesis/v10 (IA)"`).
- [Desalineacion de las lineas verificadas de c-121 si v10 difiere de v9] -> v10 es copia byte a byte; se verifica paridad de archivos versionados y `diff -rq` entre v9 y v10.
- [Falso positivo en el conteo de archivos] -> Verificar con `git ls-files` (60), no con `find` (61, por `main.log`).
- [Reescritura inadvertida de historia] -> La regla D3 es explicita; la verificacion comprueba que las 4 ocurrencias historicas de v9 en `CHANGES.md` siguen presentes.

## Migration Plan

1. Crear la copia: `cp -r "docs/Tesis/v9 (IA)" "docs/Tesis/v10 (IA)"`.
2. Verificar paridad: `git ls-files "docs/Tesis/v10 (IA)" | wc -l` = 60 e igual a v9; `diff -rq "docs/Tesis/v9 (IA)" "docs/Tesis/v10 (IA)"` sin diferencias.
3. Repuntar punteros activos: `openspec/config.yaml`, `CHANGES.md` (entrada nueva), `openspec/specs/tesis-document/spec.md` y las rutas activas de c-121.
4. Verificar: `git status` no reporta cambios en `docs/Tesis/v9 (IA)/`; `grep -c "docs/Tesis/v9 (IA)" openspec/specs/tesis-document/spec.md` = 0; las 4 ocurrencias historicas siguen en `CHANGES.md`; `git tag -l` sin cambios.
5. Rollback: `rm -rf "docs/Tesis/v10 (IA)"` y `git checkout -- openspec/config.yaml CHANGES.md openspec/specs/tesis-document/spec.md openspec/changes/c-121-observaciones-dictamen-v1-0-1/`. v9 nunca se modifica, por lo que la version publicada no corre riesgo.
