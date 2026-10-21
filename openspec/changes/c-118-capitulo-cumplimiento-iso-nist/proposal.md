# Proposal: c-118 — Capitulo de cumplimiento ISO/IEC 27001-27002 y NIST CSF 2.0

## Why

El plan de cumplimiento (`docs/cumplimiento/plan-cambios-cumplimiento.md`) quedo
TOTALMENTE EJECUTADO: los seis changes C-61..C-66 estan implementados y archivados.
Pero su paso 3 sigue pendiente. La tesis no contiene aun el capitulo de cumplimiento:
un `grep -rniE "ISO.?2700|NIST|CSF"` sobre `docs/Tesis/v9 (IA)/paper/sections/` no
devuelve coincidencias, y el Capitulo de aspectos legales (`11-aspectos-legales.tex`)
cubre solo lo juridico (marco normativo, principios, transferencias, seguridad tecnica,
consentimiento). Sin este capitulo, la defensa no exhibe el mapeo ISO/NIST que justifica
el trabajo de cumplimiento ya realizado.

## What Changes

- Nuevo capitulo/seccion de cumplimiento en la tesis: mapeo ISO/IEC 27001:2022 +
  27002:2022 y NIST CSF 2.0, estado actual, brechas principales y hoja de ruta.
- Regla de lenguaje: "alineado con" / "controles mapeados a"; NUNCA "certificado" ni
  "compliant" (no hay auditoria de certificacion).
- Neutralidad de paginas: el capitulo ABSORBE/REEMPLAZA contenido existente ---la
  narracion de "Seguridad tecnica" de 11.4 se pliega al mapeo de controles--- para no
  superar el tope de 100 paginas del PDF.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: agrega requisitos de contenido del capitulo de cumplimiento
  ISO/NIST, de regla de lenguaje de alineacion, de neutralidad de paginas y de
  coherencia con el marco legal del Capitulo 11.

## Impact

| Area | Impacto | Descripcion |
|------|---------|-------------|
| `docs/Tesis/v9 (IA)/paper/sections/11-aspectos-legales.tex` | Modified | Nuevo `\section` de cumplimiento; condensacion de 11.4 "Seguridad tecnica" |
| `docs/Tesis/v9 (IA)/paper/main.pdf` | Modified | Recompilado; gate `pdfinfo <= 100` y 0 referencias indefinidas |
| `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` | Read-only | Insumo del mapeo ISO/NIST |
| `docs/cumplimiento/plan-cambios-cumplimiento.md` | Read-only | Insumo de la hoja de ruta |

Secuenciacion: este change se aplica DESPUES de c-102..c-117 (no puede retirar ninguna
de sus correcciones) y ANTES de c-111 (el tag `v1.0.0` debe capturar la fuente final).
`c-80` es un change separado y anterior (evidencia visual); no lo toca.
