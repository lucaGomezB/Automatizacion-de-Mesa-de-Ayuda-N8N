# Proposal: c-114 — Afirmaciones comerciales sin respaldo y umbral de 5.000 casos

## Why

El dictamen CONEAU 2026-10-20 observa, en la dimensión 4 (Estado del arte) y la
dimensión 9 (Bibliografía), que las descripciones de plataformas comerciales se
apoyan en páginas de producto y no en literatura: afirmaciones como el "dominio
del segmento" o el "crecimiento sostenido de la adopción" quedan sin respaldo
formal. En la dimensión 8 (Trabajos futuros) observa que el umbral de "5.000
casos" para migrar a un clasificador supervisado se repite sin justificación
empírica ni cálculo de potencia, y que las líneas futuras no priorizan las que
atacan los defectos medidos. Sin cerrar esto, dos afirmaciones de contexto y una
recomendación cuantitativa quedan sin fundamento verificable.

## What Changes

- **Dimensiones 4 y 9 — afirmaciones comerciales.** En `03-estado-del-arte.tex`
  (líneas 12, 14 y 22) reformular como observación propia documentada las
  afirmaciones no respaldadas ("segmento dominado por plataformas integrales",
  "crecimiento sostenido de la adopción", "solución más adecuada del segmento"),
  anclándolas a la documentación pública ya citada en la tabla comparativa, o
  citar un informe de mercado con DOI. No se alteran datos ni se agregan cifras.
- **Dimensión 8 — umbral de 5.000 casos.** Justificar el umbral (cálculo de
  potencia o referencia a régimen de aprendizaje) o degradarlo a valor indicativo,
  de forma consistente en sus tres apariciones: `10-recomendaciones.tex:10`,
  `08-discusion.tex:54` y `12-anexos.tex:139`.
- **Dimensión 8 — priorización.** En `10-recomendaciones.tex`, declarar
  explícitamente que las líneas que atacan los defectos medidos (calibración del
  gate de confianza, clasificador supervisado con corpus propio y corrección de
  la medición de intervención humana) son prioritarias sobre las líneas genéricas.
- **Bibliografía (solo si corresponde).** Si se opta por citar en vez de
  reformular, agregar de forma aditiva en `Bibliography_base.bib` un informe de
  mercado con DOI resoluble. No se editan entradas existentes ni las ya corregidas
  por c-104 (tipado Touvron/Jurafsky).

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `tesis-document`: se agregan tres requisitos — respaldo formal (o reformulación
  como observación propia) de las afirmaciones sobre plataformas comerciales,
  tratamiento justificado o indicativo del umbral de migración a clasificador
  supervisado, y priorización de las líneas de trabajo futuro sobre los defectos
  medidos.

## Impact

- Texto de la tesis en `docs/Tesis/v9 (IA)/paper/sections/`
  (`03-estado-del-arte.tex`, `08-discusion.tex`, `10-recomendaciones.tex`,
  `12-anexos.tex`) y, solo si se agrega, `docs/Tesis/v9 (IA)/Bibliography_base.bib`.
- No se toca código, API ni runtime. No se edita el memo canónico ni `CHANGES.md`.
- Presupuesto de páginas: el PDF está en 104 páginas y `c-116` (reducción de
  páginas, cap <= 100) se aplica DESPUÉS. Este change MUST NOT inflar el conteo:
  las reformulaciones son de longitud neutra o menor.
- Governance: MEDIO (contenido documental, sin datos ni cifras nuevas; riesgo
  acotado al texto y a un posible delta bibliográfico aditivo).
