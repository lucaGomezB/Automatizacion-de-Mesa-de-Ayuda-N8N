# Proposal: c-92 — Profundidad del marco teórico (Capítulo 2)

## Why

La auditoría de la tesis detectó que el marco teórico no sostiene el uso
operativo que el resto del documento hace de sus conceptos. El Capítulo 2 dedica
cuatro párrafos al eje central de la investigación —los modelos de lenguaje
grandes (LLM)— con solo tres referencias, dos de ellas de 2017 y 2020 (A-04);
define la exactitud con la fórmula binaria y recién después la corrige a
multiclase (A-05); describe Whisper como si se usara en el sistema cuando el canal
telefónico usa la transcripción nativa de Twilio (M-03); justifica PostgreSQL
frente a alternativas no relacionales sin nombrar ninguna (M-04); y contiene una
afirmación sobre corpus EN/DE/PT sin respaldo (M-02) y una atribución editorial
incorrecta de ITIL Service Operation 2011 (A-06, parcial). Estos hallazgos son de
severidad alta y media y afectan la solidez conceptual de la tesis, no su
implementación.

## What Changes

- **§2.4 — Profundizar el eje LLM (A-04)**: desarrollar prompting (zero-shot,
  few-shot y diseño de instrucciones), calibración de la confianza, alucinación,
  sensibilidad al idioma y evaluación de LLM, con referencias adicionales
  verificables. Estos conceptos ya se usan en el sistema y en los capítulos 4, 6,
  7 y 8 sin definición previa.
- **§2.7 — Exactitud multiclase (A-05)**: eliminar la fórmula binaria
  `(TP+TN)/(TP+TN+FP+FN)` como definición principal y definir directamente la
  exactitud multiclase como proporción de predicciones correctas sobre el total,
  en coherencia con la matriz de confusión 5x5 del Capítulo 7.
- **§2.5 — Reconocimiento del habla (M-03)**: retirar la afirmación de que los
  modelos preentrenados de Whisper facilitan la integración del canal telefónico.
  El sistema usa la transcripción nativa de Twilio (§6.4). Whisper puede
  conservarse como antecedente teórico del ASR, pero marcado explícitamente como
  no utilizado en la implementación.
- **§2.6 — Persistencia (M-04)**: justificar PostgreSQL frente a alternativas
  concretas (por ejemplo, motores de documentos como MongoDB y motores clave-valor
  como Redis) en función del modelo relacional, la integridad referencial y la
  auditoría del dominio, en lugar de una comparación genérica contra "lo no
  relacional".
- **§1.7 — Corpus EN/DE/PT (M-02)**: respaldar con citas verificables la
  afirmación de que la mayoría de los estudios de clasificación de tickets usan
  corpus en inglés, alemán o portugués, o reformularla. Se reutilizan las
  referencias incorporadas por c-78; este change NO duplica la modernización
  bibliográfica.
- **§2.2 — Atribución ITIL (A-06, parcial)**: corregir en el cuerpo la atribución
  de ITIL Service Operation (2011) al Office of Government Commerce, precisando
  que la edición de 2011 corresponde a TSO/Cabinet Office. La entrada `.bib` es
  responsabilidad de c-78 (B3); este change solo corrige el texto y remite a esa
  corrección.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `tesis-document`: profundidad conceptual y precisión del marco teórico
  (definiciones de LLM y sus riesgos, métrica multiclase correcta, alcance real
  del ASR, justificación tecnológica con alternativas concretas, respaldo de la
  afirmación comparativa sobre corpus y atribución editorial de ITIL).

## Impact

Documentación únicamente (SIN tocar `App/**`):

- `docs/Tesis/v9 (IA)/paper/sections/02-marco-teorico.tex` (§2.2, §2.4, §2.5,
  §2.6, §2.7).
- `docs/Tesis/v9 (IA)/paper/sections/01-introduccion.tex` (§1.7, M-02).
- `docs/Tesis/v9 (IA)/paper/main.pdf` (recompilación en Overleaf, XeLaTeX).
- `openspec/specs/tesis-document/spec.md` (delta aplicado al archivar).

Coordinación, sin duplicación:

- **c-76** posee los números reales del corpus y las métricas del Capítulo 7; este
  change solo alinea la definición teórica de la métrica.
- **c-77** posee los errores estadísticos e inferenciales; no se toca.
- **c-78** posee la bibliografía, la modernización 2023-2026 y los metadatos de
  `OGC2011_itil`; este change reutiliza esas referencias y NO edita
  `Bibliography_base.bib`.
- **c-79** posee los aspectos legales; no se toca.
- **c-80** posee la forma y la evidencia visual; no se toca.

Governance: MEDIUM. Sin código de aplicación, sin cambios de comportamiento del
sistema.

## Rollback Plan

`git checkout --` sobre los dos `.tex` afectados y `main.pdf`, o `git revert` del
commit del change. Los artefactos OPSX se descartan con el directorio del change.

## Success Criteria

- [ ] §2.4 define prompting, calibración de confianza, alucinación, sensibilidad
      al idioma y evaluación de LLM, con al menos tres referencias nuevas
      verificables respecto de las actuales.
- [ ] §2.7 define la exactitud multiclase directamente; la fórmula binaria
      `(TP+TN)/(TP+TN+FP+FN)` ya no aparece como definición principal.
- [ ] §2.5 no afirma que Whisper se integre al sistema; el texto remite a la
      transcripción nativa de Twilio (§6.4) y, si conserva Whisper, lo marca como
      antecedente no utilizado.
- [ ] §2.6 compara PostgreSQL con al menos dos alternativas concretas y justifica
      la elección por requisitos del dominio.
- [ ] §1.7 respalda o reformula la afirmación sobre corpus EN/DE/PT con al menos
      una cita verificable de c-78.
- [ ] §2.2 atribuye correctamente la edición 2011 de ITIL Service Operation a
      TSO/Cabinet Office y deja la corrección del `.bib` a c-78 (B3).
- [ ] `rg` de control sin los patrones stale definidos en `tasks.md`.
- [ ] `main.pdf` recompilado en Overleaf sin errores fatales.
- [ ] `openspec validate c-92-tesis-marco-teorico-profundidad --strict` pasa.
