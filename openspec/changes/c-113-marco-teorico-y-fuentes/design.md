## Context

Ver `proposal.md` — Why. El marco teórico ya fue intervenido por c-110 (subsección
HITL) y por c-92 (profundidad del eje LLM, ASR, persistencia). Este change no repite
esos trabajos: cierra los déficits que el dictamen deja abiertos en la dimensión 5.
El `.bib` es compartido y se aplica en secuencia; toda edición es aditiva.

Estado actual relevante:

- `02-marco-teorico.tex:24` define BPA sin cita propia (Russell2021 se cita para el
  paradigma de agentes, no para la definición).
- `02-marco-teorico.tex:26` define iPaaS sin cita propia.
- `02-marco-teorico.tex:28` contiene "trazabilidad auditiva".
- `02-marco-teorico.tex:48` define alucinación citando solo colavito2025benchmarking
  (que la ejemplifica, no la define).
- `02-marco-teorico.tex:56-62` desarrolla el ASR y luego admite que no se usa.
- `01-introduccion.tex:60` atribuye "soberanía digital" a la Ley 25.326.

## Goals / Non-Goals

**Goals:**

- Fundamentar o reformular BPA e iPaaS, añadir cita canónica de alucinación, corregir
  la formulación jurídica de la soberanía, acotar o justificar el eje de ASR y corregir
  "auditiva" por "auditable".
- Mantener el `.bib` consistente: cero citas huérfanas, cero entradas sin uso.
- No exceder el techo de páginas (<= 100); el neto de páginas no debe crecer.

**Non-Goals:**

- No tocar código, API ni runtime.
- No duplicar la subsección HITL ni el protocolo de revisión (c-110).
- No reescribir el resto del marco teórico ni la modernización bibliográfica (c-78).
- No ejecutar la reducción de páginas (c-116, posterior).

## Decisions

**D1 — BPA e iPaaS se reformulan como glosa propia, sin atribución.**
Ambos son conceptos de uso corriente cuya definición no exige una fuente puntual; el
riesgo de forzar una cita provisional es introducir una referencia de dudosa pertinencia.
Alternativa considerada: citar una obra canónica de BPM (p. ej. Dumas et al.) y un
informe de mercado para iPaaS. Se descarta por ahora porque exigiría ampliar el `.bib`
con fuentes no verificadas en esta fase. La glosa propia se rotula de forma que el lector
identifique que es definición del autor, no atribución a un tercero.

**D2 — Alucinación se respalda con cita canónica.**
Se incorpora Ji et al. (2023), "Survey of Hallucination in Natural Language Generation",
*ACM Computing Surveys*, DOI `10.1145/3571730` — verificada como resoluble en Crossref.
Clave propuesta: `Ji2023_hallucination`. Alternativa considerada: Maynez et al. (2020);
se prefiere la survey por ser la referencia canónica y más reciente.

**D3 — Soberanía se reformula con el texto legal, sin nueva entrada.**
Se reutiliza `Ley25326_2000` y se enuncia el control sobre los datos personales y su
tratamiento conforme a la normativa, en lugar de "soberanía digital". Alternativa
considerada: citar la AAIP o el RGPD; innecesario, la formulación no es una atribución
de principio sino una descripción del alcance de la ley vigente.

**D4 — El eje de ASR se conserva acotado y justificado.**
Se recorta el párrafo de aplicación (`02-marco-teorico.tex:62`, que hoy afirma que el
ASR permite automatizar la captura telefónica) y se conserva un desarrollo mínimo que
explique por qué se menciona (marco para comprender el canal telefónico) y que la
transcripción la provee Twilio. Alternativa considerada: eliminar la sección 2.5; se
descarta porque el canal telefónico existe en el sistema y compete al marco teórico
explicar el tipo de tecnología involucrada, aunque no la integre.

**D5 — Corrección terminológica mecánica.**
"trazabilidad auditiva" -> "trazabilidad auditable" en `02-marco-teorico.tex:28`.
Verificación: búsqueda de la expresión en `paper/sections/*.tex` con cero coincidencias.

## Risks / Trade-offs

- [Reformular como glosa propia puede leerse como elusión de la cita] -> rotular la
  glosa de forma explícita ("se entiende aquí por…") para que no se confunda con una
  definición atribuida.
- [El neto de páginas podría crecer] -> el recorte del eje de ASR compensa la cita
  adicional; verificar el conteo tras compilar y, si crece, recortar con c-116 en mente.
- [Colisión con otros changes de tesis que comparten `.tex` y `.bib`] -> aplicar en
  secuencia, con este change limitado a las líneas listadas en Context.
- [Cita nueva no resuelve al momento de aplicar] -> verificar el DOI con Crossref antes
  de confirmar la entrada; si no resuelve, reformular la definición como glosa propia.

## Migration Plan

1. Editar `01-introduccion.tex` §1.7 (soberanía) y `02-marco-teorico.tex` §2.3/§2.4/§2.5.
2. Agregar `Ji2023_hallucination` de forma aditiva al `.bib`.
3. Compilar con `texlive-thesis` y verificar 0 citas huérfanas y conteo de páginas.
4. Rollback: revertir los `.tex` y eliminar la entrada nueva del `.bib` (aditiva, sin
   dependencias).

## Open Questions

Ninguna que condicione specs, enfoque o tareas. La elección entre cita y glosa propia
para BPA/iPaaS ya quedó resuelta como decisión de diseño (D1); el único riesgo residual
es la resolución del DOI de la cita de alucinación, con plan de contingencia en D2/Riesgos.
