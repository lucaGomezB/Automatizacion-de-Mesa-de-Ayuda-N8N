## Context

Ver `proposal.md` — Why. El corpus cambió en c-77 (commit `4602bf5`) y la tesis se recompiló con los valores nuevos. La spec principal de `tesis-document` conserva los valores previos en dos requisitos. La capability `evaluation-framework` ya fue sincronizada por c-99 al archivar, por lo que no se toca.

Fuentes autoritativas verificadas (lectura directa):

- `docs/Tesis/v9 (IA)/paper/sections/07-resultados.tex`
  - línea 10: media automatizada `17,76 s`, reducción `71,2 %`.
  - línea 55: `W = min(T+, T−) = 363`, `T+ = 19.737`, `T− = 363`, `n = 200`, `p = 3,08e-32`, `188 de 200` pares a favor, `12` pares (6,0 %) sin ser más rápidos.
  - línea 59: `r = (19.737 − 363) / (200·201/2) = 19.374/20.100 = 0,9639`.
  - línea 63: análisis de sensibilidad; descuento de 5 s y 10 s a la medición manual sitúa la reducción en `68,6 %` y `65,6 %` como cota inferior conservadora.
- `00-resumen.tex` línea 13: `17,76 s`, `71,2 %`, `W = 363`, `p = 3,08e-32`, `r = 0,9639`.
- `04-marco-metodologico.tex` líneas 71-77: convención `W = min(T+, T−)`; fórmula rank-biserial `r = (T+ − T−) / (n(n+1)/2)`, equivalente a `1 − 4W/(n(n+1))` cuando `W = T−`.
- `08-discusion.tex` y `09-conclusiones.tex`: `71,2 %`.

Verificación de alcance: el valor previo `14,8 s` (media automatizada) no aparece en ninguno de los dos requisitos stale de la spec principal, por lo que queda fuera del delta (su corrección ya está reflejada en la tesis y en `evaluation-framework`). Del mismo modo, `T+`/`T−` no figuraban con valores concretos en el requisito de divulgación; se incorporan ahora para alinear con la tesis y con el requisito hermano `Rigor inferencial del tamaño del efecto`.

## Goals / Non-Goals

**Goals:**

- Alinear los dos requisitos stale de `tesis-document` con los valores de la tesis corregida.
- Mantener el delta mínimo: exactamente esos dos requisitos.

**Non-Goals:**

- No tocar `evaluation-framework` (ya sincronizada por c-99).
- No modificar `docs/Tesis/**` ni `docs/Tesis/Correcciones/*.md`.
- No introducir ni retirar requisitos; solo operaciones `MODIFIED`.

## Decisions

- **Usar `## MODIFIED Requirements` copiando el bloque completo de cada requisito.** Es la operación correcta porque cambia el contenido de requisitos existentes; `## ADDED` duplicaría el requisito y `## REMOVED` lo eliminaría. Alternativa descartada: editar la spec principal directamente (viola la regla de que solo el delta modifica la spec).
- **Mantener el modal `SHALL`/`MUST` en la primera línea del enunciado.** El validador de OpenSpec lee solo la primera línea del texto del requisito para detectar el modal. Ambos enunciados conservan `SHALL` en su línea 1.
- **Incorporar `T+` y `T−` al enunciado del requisito de divulgación.** La tesis reporta ambos estadísticos de rango (`07-resultados.tex:55`) y el requisito hermano ya exige reportarlos; explicitarlos elimina la ambigüedad de `W = min(T+, T−)`.

## Risks / Trade-offs

- [Riesgo] Copiar parcialmente el bloque del requisito pierde detalle al archivar. → Mitigación: se copia el bloque completo (`### Requirement:` hasta el último escenario de cada requisito).
- [Riesgo] Que el encabezado no coincida textualmente con la spec principal y el validador no aplique el `MODIFIED`. → Mitigación: encabezado copiado textualmente desde `openspec/specs/tesis-document/spec.md`.
- [Trade-off] El valor de `r` se corrige a `0,9639` (cálculo con `T+ = 19737`), distinto del `0,9667` previo; es el valor reproducible de la tesis.
