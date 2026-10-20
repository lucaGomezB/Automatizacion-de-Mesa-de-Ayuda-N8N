## Why

La spec principal `openspec/specs/tesis-document/spec.md` conserva estadísticas obsoletas anteriores al cambio de corpus del commit `4602bf5` (cambio c-77). La tesis corregida (`docs/Tesis/v9 (IA)/paper/sections/**`) ya reporta los valores vigentes, pero dos requisitos de la spec quedaron desalineados y ningún delta activo los cubre. Esto deja la spec —fuente de verdad del comportamiento del documento— contradiciendo el artefacto que describe.

## What Changes

- Actualizar el requisito `Divulgacion del procedimiento de medicion de tiempos y analisis de sensibilidad`: el estadístico de Wilcoxon pasa de `W=335`, `p=2,05e-32`, `r=0,983` a `W=363`, `T+=19737`, `T−=363`, `p=3,08e-32`, `r=0,9639`; la reducción como cota superior pasa de `75,9 %` a `71,2 %`; y la cota conservadora deja de ser `>= 71,3 %` para reportar `68,6 %` (descuento de 5 s) y `65,6 %` (descuento de 10 s).
- Actualizar el requisito `Rigor inferencial del tamaño del efecto`: el valor de `r` sobre el corpus real pasa de `0,9667` a `0,9639`.
- No se modifica ningún otro requisito de `tesis-document` ni de otra capability.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `tesis-document`: se corrigen los valores numéricos de dos requisitos (estadístico de Wilcoxon y tamaño del efecto) para que reflejen la tesis corregida tras el cambio de corpus de c-77.

## Impact

- `openspec/specs/tesis-document/spec.md`: requisitos `Divulgacion del procedimiento de medicion de tiempos y analisis de sensibilidad` y `Rigor inferencial del tamaño del efecto` (se sincronizan al archivar este cambio).
- Sin impacto en runtime, código, API ni dependencias. Governance: BAJO.
- No se toca `docs/Tesis/**` (ya correcto), `docs/Tesis/Correcciones/*.md` (registros históricos de auditoría) ni `openspec/specs/**` directamente.
