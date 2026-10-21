# Proposal: c-112 — Objetivos e hipótesis

## Why

El dictamen CONEAU 2026-10-20 cierra dos dimensiones. La 2 (Hipótesis): la
principal combina una afirmación de mecanismo ("reduce tiempo e intervención
humana") con un umbral de desempeño ("exactitud ≥ 85 %, F1 macro ≥ 0,85"); como
conjunción es falsa y solo la parte temporal tiene hipótesis nula operacionalizada.
La 3 (Objetivos): el general está en clave de desarrollo ("desarrollar e
implementar"), el segundo mezcla la acción con su umbral, el quinto usa
"exhaustivamente" (no falsable) y falta un objetivo de análisis de errores y
calibración. Sin este cierre, las afirmaciones centrales no tienen formulación
contrastable ni estado declarado.

## What Changes

- **Hipótesis (§1.4)**: desdoblar la principal en tres sub-hipótesis (tiempo,
  intervención humana, exactitud/F1), cada una con su contraste y su criterio de
  falsación.
- **Estado de la hipótesis (resumen, conclusiones)**: confirmada en tiempo,
  refutada en clasificación; la sub-hipótesis de intervención humana se declara
  **no medida** (c-107 retiró el 9,5 %).
- **Objetivo general (§1.5)**: reformularlo como evaluación de viabilidad y
  desempeño, con el desarrollo como medio.
- **Segundo objetivo (§1.6)**: separar la implementación del umbral, que pasa a
  criterio de éxito contingente.
- **Quinto objetivo (§1.6)**: reescribirlo en clave reproducible, sin
  "exhaustivamente".
- **Objetivo nuevo**: análisis de errores y calibración de la confianza.
- **Conclusiones**: tabla de objetivos, cumplimiento y evidencia.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `tesis-document`: se modifica "Declaración del estado de la hipótesis principal"
  y se agregan seis requisitos: desdoblamiento de la hipótesis, objetivo general
  como evaluación, separación implementación/umbral del segundo objetivo, quinto
  objetivo reproducible, objetivo de análisis de errores y calibración, y tabla de
  objetivos/cumplimiento/evidencia.

## Impact

- `01-introduccion.tex` (§1.4, §1.5-§1.6) y `09-conclusiones.tex` (§9.1 y tabla).
- Sin código, API ni runtime. No toca `Bibliography_base.bib`.
- Secuencia: comparte `01-introduccion.tex` con c-113 (§1.7); c-116 (tope 100) se
  aplica DESPUÉS; c-111 cierra el tag al final. Solo valores `vigente`; NO
  reintroduce `retirado` (9,5 %, 3.700, 45,0 h).
- Governance: **ALTO**.

## Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Reintroducir el 9,5 % o el contraste de tiempos | Med | Sub-hipótesis de intervención no medida; umbral como desempeño, no zona de rechazo |
| Conflicto de líneas con c-113/c-115/c-116 | Med | Aplicar en secuencia; c-116 al final; c-111 cierra el tag |
| Inflar páginas por la tabla y las sub-hipótesis | Med | Longitud neutra; techo verificado por c-116 |

## Rollback Plan

`git revert` de la edición de `01-introduccion.tex`, `00-resumen.tex` y
`09-conclusiones.tex`. Sin migraciones ni estado externo; la propuesta y el delta
se descartan al no archivar.

## Success Criteria

- [ ] `openspec validate c-112-objetivos-e-hipotesis --strict` pasa.
- [ ] §1.4 enuncia tres sub-hipótesis con contraste y criterio de falsación.
- [ ] Resumen y conclusiones declaran la hipótesis confirmada en tiempo y refutada en clasificación; sin 9,5 %.
- [ ] Objetivo general evalúa viabilidad/desempeño; existe objetivo de errores/calibración y tabla de objetivos.
- [ ] El PDF compila con `texlive-thesis` sin reintroducir cifras retiradas.
