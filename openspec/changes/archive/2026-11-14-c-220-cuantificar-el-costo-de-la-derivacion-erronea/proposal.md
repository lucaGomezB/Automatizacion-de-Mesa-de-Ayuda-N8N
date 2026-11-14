# Proposal: Cuantificar el costo de la derivación errónea

## Why

El dictamen CONEAU v1.3.0 (2026-11-13) descuenta el criterio 1 («Definición del problema», 8/15) y el criterio 3 («Objetivos») porque el umbral del 85 % «carece de fundamento numérico». Uno de sus tres criterios convergentes es una estimación propia sin respaldo: `01-introduccion.tex:48` afirma que una derivación errónea cuesta «10 a 15 minutos adicionales de reasignación» y aclara que es «una estimación de los autores, sin un registro cuantitativo conservado». El mismo valor alimenta el balance neto (`08-discusion.tex:80-111`), hoy `condicional` justamente por eso, y el memo lo declara «reversible si una réplica mide `c`» (`numeros-canonicos.md:808-810`).

La campaña complementaria ya conserva dos mediciones que nunca se usaron para este fin: `intervenciones.csv` registra la duración de 138 de 147 intervenciones (93,9 %) y `brazo_manual.csv` los 220 tiempos de decisión de sector. No hace falta trabajo de campo para reemplazar la estimación por una cifra con procedencia.

## What Changes

- Análisis nuevo de solo lectura `evaluation/data/campana/analisis/analisis_costo_derivacion_c220.py` (+ test) que descompone `c` en un tramo activo medido (corrección en la compuerta y re-decisión proxy del brazo manual) y un tramo anclado en literatura (reanudación tras interrupción), y compone un intervalo con su propagación.
- Sección aditiva en `numeros-canonicos.md` (próxima libre; se espera `3.29`) con insumos, fórmulas, intervalos, procedencia y estado por valor.
- Prosa de tesis: `01-introduccion.tex:48` (reemplaza la frase sin respaldo) y `04-marco-metodologico.tex` (definición operacional de `c` y método de medición).
- Entrada nueva en `docs/Tesis/Correcciones/dictamen-correcciones.md` con matriz de trazabilidad.
- Entrada bibliográfica nueva solo si el ancla de reanudación no está ya en `Bibliography_base.bib`.

No cambia el umbral del 85 %. Si el intervalo medido excluye la banda `[600; 900] s`, el change NO recorta el balance neto por su cuenta: registra el hallazgo en el memo y abre una decisión del dueño (ver `design.md`, D5).

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tesis-numeros-canonicos`: se agrega el requisito de registro aditivo del costo de la derivación errónea, con procedencia y estado por valor, sin alterar las secciones 3.1 a 3.28.
- `evaluation-framework`: se agrega el requisito del análisis offline, determinista y de solo lectura que descompone `c` sobre los artefactos de la campaña congelados.

## Impact

| Área | Impacto | Descripción |
|------|---------|-------------|
| `evaluation/data/campana/analisis/analisis_costo_derivacion_c220.py` | Nuevo | Análisis de solo lectura, biblioteca estándar, salidas `.json` y `.md` |
| `evaluation/data/campana/analisis/test_analisis_costo_derivacion_c220.py` | Nuevo | TDD del análisis |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Nuevo (aditivo) | Sección del costo de la derivación errónea |
| `docs/Tesis/v10 (IA)/paper/sections/01-introduccion.tex` | Modificado | Frase de `:48` con cifra medida y procedencia |
| `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` | Modificado | Definición operacional y método |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Nuevo (aditivo) | Entrada del dictamen v1.3.0 |
| `docs/Tesis/v10 (IA)/Bibliography_base.bib` | Condicional | Solo si el ancla no existe |

Sin cambios en `App/Backend/`, `App/Frontend/`, `n8n/`, `data/` ni en el clasificador. Cero llamadas a Gemini.

## Riesgos

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| El `c` medido cae fuera de `[600; 900] s` y contradice el balance neto | Alta | Decisión D5: no se toca `08`; el change cierra en memo + prosa de `01/04` y escala la decisión |
| Colisión de numeración de sección del memo con c-218/c-219 | Media | Se asigna el número libre al aplicar, releyendo el índice |
| La duración de 138 casos mide la revisión, no la reasignación aguas abajo | Alta | Se declara el régimen y el tramo no medido en la definición operacional |
| Ancla de interrupción mal aplicada (extrapolación de otro dominio) | Media | Se usa solo como cota superior declarada y se verifica la fuente primaria |

## Plan de reversión

`git revert` del commit del change. El análisis es aditivo y de solo lectura: borrar el script, sus salidas y la sección del memo deja el repositorio en el estado previo. Las ediciones de `01` y `04` son reemplazos de párrafo localizados y reversibles con el diff. Ningún valor canónico vigente de las secciones 3.1 a 3.28 se modifica, de modo que no hay migración de datos ni de cifras.

## Dependencias

- `evaluation/data/campana/intervenciones.csv` e `intervenciones` con `duracion_s` (cobertura 138/147), y `brazo_manual.csv` versionados.
- Fuente primaria del ancla de reanudación verificada antes de citar.
- `openspec/specs/tesis-numeros-canonicos/spec.md` y `openspec/specs/evaluation-framework/spec.md` vigentes.

## Criterios de éxito

- [ ] Existe una cifra de `c` con intervalo, procedencia por componente y estado declarado en el memo.
- [ ] `01-introduccion.tex:48` ya no contiene una estimación sin registro: cita la medición y su alcance.
- [ ] El análisis es determinista y reproduce sus salidas byte a byte.
- [ ] Ningún valor vigente de las secciones 3.1 a 3.28 del memo cambia.
- [ ] `openspec validate c-220-cuantificar-el-costo-de-la-derivacion-erronea --strict` pasa.