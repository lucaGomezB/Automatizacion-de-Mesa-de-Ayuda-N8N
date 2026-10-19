# Design: c-92 — Profundidad del marco teórico (Capítulo 2)

## Context

Ver `proposal.md` — Why.

Estado verificado del árbol de trabajo `docs/Tesis/v9 (IA)/paper/sections/`:

- `02-marco-teorico.tex` §2.2 (líneas 14–20): la atribución de ITIL Service
  Operation 2011 se apoya en `\parencite{OGC2011_itil}` sin precisar editor.
- `02-marco-teorico.tex` §2.4 (líneas 30–38): el eje LLM se resuelve en cuatro
  párrafos; las referencias son `Jurafsky2023_speech_language`,
  `Vaswani2017_attention` y `Brown2020_few_shot`. No define prompting,
  calibración, alucinación, sensibilidad al idioma ni evaluación.
- `02-marco-teorico.tex` §2.5 (líneas 40–46): describe Whisper (680.000 horas,
  segmentos de 30 s) y afirma que su disponibilidad en código abierto para español
  facilita la integración del canal telefónico.
- `02-marco-teorico.tex` §2.6 (líneas 48–52): justifica PostgreSQL contra
  "alternativas no relacionales" sin nombrar ninguna.
- `02-marco-teorico.tex` §2.7 (líneas 54–70): define la exactitud con
  `(TP+TN)/(TP+TN+FP+FN)` y recién en la línea 62 aclara el caso multiclase.
- `01-introduccion.tex` §1.7 (línea 62): afirma que la mayoría de los estudios de
  clasificación de tickets usan corpus en inglés, alemán o portugués, sin cita.
- Implementación real del canal telefónico: `06-implementacion.tex:50` usa
  Programmable Voice y la transcripción nativa de Twilio; Whisper no se usa.
- c-78 ya incorpora las referencias arbitradas 2023-2026 y corrige
  `OGC2011_itil` en el `.bib`. c-76 posee los números y las métricas del Capítulo
  7.

Restricción dura: NO tocar `App/**`, NO editar `Bibliography_base.bib` y NO
duplicar el trabajo de c-76, c-77, c-78, c-79 ni c-80. Governance MEDIUM.

## Goals / Non-Goals

**Goals:**

- Elevar §2.4 a un tratamiento conceptual completo del eje LLM, con referencias
  verificables ya incorporadas por c-78.
- Corregir la definición de exactitud de §2.7 para que sea multiclase desde el
  inicio.
- Alinear §2.5 con la tecnología realmente usada (Twilio) y delimitar Whisper
  como antecedente teórico.
- Justificar §2.6 frente a alternativas concretas.
- Respaldar o reformular la afirmación de §1.7 sobre idiomas del corpus.
- Corregir en el cuerpo la atribución editorial de ITIL en §2.2.

**Non-Goals:**

- No re-medir el corpus, no cambiar métricas ni estadísticos (c-76/c-77).
- No agregar, quitar ni corregir entradas del `.bib` (c-78).
- No reescribir los capítulos 3–9.
- No tocar aspectos legales (c-79) ni figuras o anexos (c-80).
- No recompilar localmente si no hay toolchain; se usa Overleaf XeLaTeX.

## Decisions

### D1 — §2.4: cinco conceptos, referencias de c-78, sin tocar el `.bib`

Se amplía §2.4 con cinco subsecciones conceptuales:

1. **Prompting**: zero-shot, few-shot y diseño de instrucciones. Se apoya en
   `Brown2020_few_shot` y en `ahuja2023mega` / `lai2023okapi`.
2. **Calibración de la confianza**: relación entre la probabilidad declarada y la
   corrección empírica; se vincula con el umbral operativo de revisión humana
   (`human_review: 0.70`) y con la evaluación comparativa de `xuan2025mmluprox`.
3. **Alucinación**: generación de contenido plausible pero falso; se vincula con
   la necesidad de validación y con `colavito2025benchmarking`.
4. **Sensibilidad al idioma**: variación de desempeño entre idiomas y variedades;
   se apoya en `zhang2023multilingual`, `grandury2025laleaderboard` y
   `mayorrocher2026spanish`.
5. **Evaluación de LLM**: benchmarks, limitaciones de la exactitud aislada y
   necesidad de métricas por clase; se apoya en `xuan2025mmluprox` y
   `ahuja2023mega`, enlazando con §2.7.

Regla de aplicación: solo se citan claves que ya existan en
`Bibliography_base.bib` después de c-78. Si un concepto no tiene una referencia
dedicada en ese conjunto, se lo define conceptualmente y se lo respalda con la
referencia de evaluación más próxima; NO se agrega una entrada nueva. Alternativa
descartada: incorporar bibliografía específica de calibración y alucinación — se
descarta porque duplica el alcance de c-78 y el usuario pidió no repetir ese
trabajo.

### D2 — §2.7: exactitud multiclase directa

Se elimina el bloque `\[ \text{Exactitud} = ... \]` con TP/TN/FP/FN y se lo
reemplaza por la definición multiclase:

`Exactitud = (1/N) * sum_{i=1}^{N} 1[y_hat_i = y_i]`, es decir, la proporción de
predicciones correctas sobre el total. Se conserva la referencia a
`Powers2011_evaluation` y la advertencia sobre desbalance de
`Sokolova2009_performance_measures`. La matriz de confusión 5x5 del Capítulo 7 es
el referente empírico. Alternativa descartada: conservar la fórmula binaria con
una nota aclaratoria — se descarta porque la auditoría la señala como definición
engañosa para un problema multiclase.

### D3 — §2.5: Whisper como antecedente, Twilio como implementación

Se conserva la descripción histórica del ASR (HMM, codificador-decodificador) y
la mención de Whisper como exponente del estado del arte. Se elimina la oración
que afirma que los modelos preentrenados de Whisper facilitan la integración del
canal telefónico. Se agrega una remisión explícita a §6.4: la transcripción
efectiva la provee el servicio nativo de Twilio, y Whisper no forma parte de la
implementación. Alternativa descartada: eliminar toda mención de Whisper — se
descarta porque el estado del arte del ASR sigue siendo pertinente; el problema es
la afirmación de uso, no la referencia teórica.

### D4 — §2.6: alternativas concretas y criterios del dominio

Se reformula la justificación de PostgreSQL comparándolo con:

- un motor de documentos (MongoDB), por su modelo sin esquema fijo;
- un motor clave-valor (Redis), por su persistencia en memoria y su modelo de
  acceso.

La justificación se ancla en integridad referencial declarativa, transacciones
ACID, consultas relacionales para el dashboard y trazabilidad/auditoría. No se
emite un juicio general sobre "lo no relacional". Alternativa descartada:
mantener la contraposición genérica — se descarta porque la auditoría exige una
comparación concreta.

### D5 — §1.7: cita de c-78 o reformulación sin alcance cuantitativo

Se reutilizan las referencias de c-78 (`zangari2023ticket`,
`colavito2025benchmarking`, `grandury2025laleaderboard`, `mayorrocher2026spanish`)
para respaldar la afirmación sobre idiomas del corpus. Si la evidencia disponible
no permite sostener "la mayoría", se reformula a un alcance defendible ("buena
parte de la literatura relevante"). No se agregan entradas al `.bib`.

### D6 — §2.2: corrección de atribución en el cuerpo, `.bib` delegado a c-78

Se corrige el texto para indicar que la edición de 2011 de ITIL Service Operation
fue publicada por The Stationery Office (TSO) por encargo del Cabinet Office, y
que el Office of Government Commerce conserva la titularidad histórica del marco.
La corrección del campo bibliográfico `OGC2011_itil` queda explícitamente a cargo
de c-78 (B3). Alternativa descartada: editar también el `.bib` — se descarta para
no duplicar ni pisar el change bibliográfico.

### D7 — Verificación sin toolchain local

La verificación textual se hace con `rg` sobre `sections/`; la compilación final
se hace en Overleaf con XeLaTeX (no hay toolchain LaTeX local, mismo criterio que
c-76/c-80). Los `.bak` no se editan ni se cuentan.

## Risks / Trade-offs

- [La ampliación de §2.4 puede exceder el límite de 100 páginas] → medir el
  conteo en Overleaf; priorizar densidad conceptual sobre extensión y no duplicar
  lo que ya dicen los capítulos 3 y 8.
- [Referencias de c-78 aún no aplicadas al `.bib`] → ordenar la aplicación de c-92
  después de c-78; si c-78 no está aplicado, usar solo claves ya presentes y
  registrar el bloqueo en las tareas.
- [Riesgo de introducir una referencia no verificada] → prohibido agregar claves
  nuevas; solo se citan claves existentes y verificadas.
- [Solapamiento con c-76/c-77/c-79/c-80] → el change solo toca §2.2, §2.4, §2.5,
  §2.6, §2.7 y §1.7; no toca números, estadística, legal ni figuras.
- [La corrección de atribución de ITIL puede quedar inconsistente con el `.bib`]
  → el texto remite a c-78 y la tarea de verificación compara ambos.

## Migration Plan

1. Confirmar que c-78 está aplicado (claves nuevas en `Bibliography_base.bib`) o
   registrar qué claves faltan.
2. Editar `02-marco-teorico.tex`: §2.2, §2.4, §2.5, §2.6 y §2.7.
3. Editar `01-introduccion.tex` §1.7.
4. Verificar con `rg` los patrones stale y la coherencia con §6.4 y Capítulo 7.
5. Recompilar en Overleaf (XeLaTeX) y verificar el PDF.
6. Ejecutar `openspec validate c-92-tesis-marco-teorico-profundidad --strict`.
7. Rollback: `git checkout --` de los `.tex` y `main.pdf`, o `git revert`.

## Open Questions

- Ninguna bloqueante. La disponibilidad de una referencia dedicada a calibración
  o alucinación se resuelve con la regla de D1 (solo claves existentes) sin
  cambiar el alcance del change.
