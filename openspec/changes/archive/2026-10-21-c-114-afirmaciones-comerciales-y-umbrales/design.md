## Context

Ver `proposal.md` — Why. Este change cubre las dimensiones 4, 8 y 9 del dictamen
CONEAU 2026-10-20 sobre `03-estado-del-arte.tex`, `08-discusion.tex`,
`10-recomendaciones.tex` y `12-anexos.tex`. Estado actual: el estado del arte
afirma el dominio del segmento (`03:12`), el crecimiento sostenido de la adopción
(`03:14`) y la idoneidad de N8N para el segmento (`03:22`) apoyándose en páginas
de producto (URLs ya relevadas en la tabla comparativa, consultadas el 19-10-2026).
El umbral de "5.000 casos" aparece en `10:10`, `08:54` y `12:139`. El capítulo de
recomendaciones no declara prioridad entre líneas futuras. Existe el helper
`docs/Tesis/v9 (IA)/verify_citations.py`. El PDF tiene 104 páginas.

## Goals / Non-Goals

**Goals:**

- Respaldar o reformular como observación propia documentada las afirmaciones
  comerciales no fundadas de `03-estado-del-arte.tex`.
- Justificar o declarar indicativo el umbral de 5.000 casos, de forma consistente.
- Priorizar en `10-recomendaciones.tex` las líneas que atacan los defectos medidos.

**Non-Goals:**

- No reescribir la tabla comparativa ni sus fuentes URL (ya declaran la consulta).
- No duplicar la corrección de tipado Touvron/Jurafsky (ya hecha por c-104).
- No corregir la Tabla 7.5 ni la medición de intervención (otro change de la
  dimensión 7); aquí solo se PRIORIZA esa línea como trabajo futuro.
- No editar el memo canónico, `CHANGES.md` ni `dictamen-correcciones.md`.
- No iniciar la reducción de páginas (eso es `c-116`, posterior).

## Decisions

### D1 — Capacidad delta: `tesis-document` (MODIFIED), sin capacidad nueva

Se modifican los requisitos de la capacidad existente `tesis-document` con tres
requisitos ADDED. No se crea capacidad nueva: los tres son contratos de calidad del
documento de tesis, ya regidos por `tesis-document`. Alternativa descartada: una
capacidad `tesis-estado-del-arte-*` fragmentaría el contrato del documento.

### D2 — Afirmaciones comerciales: reformular como observación propia (ruta primaria)

Ruta primaria: reformular las tres afirmaciones como observación propia documentada,
anclada a la documentación pública de las plataformas ya citada en la tabla
comparativa (`03:57`, consulta 19-10-2026), sin agregar cifras ni entradas nuevas.
Ejemplo de forma objetivo: "Según la documentación pública de las plataformas
relevadas (consulta 19-10-2026), las soluciones integrales …". Ruta secundaria
(solo si en apply se verifica un informe de mercado con DOI resoluble): citar el
informe y agregar su entrada de forma aditiva. Se descarta por defecto la vía de
informes de mercado porque la mayoría son de pago y sin DOI, y porque inflaría la
bibliografía y el recuento de páginas. Ninguna ruta introduce datos cuantitativos
nuevos.

### D3 — Umbral de 5.000 casos: declarar indicativo con justificación compacta

No hay base empírica ni cálculo de potencia en el trabajo para fijar el umbral, y
un cálculo de potencia requeriría supuestos no medidos (efecto esperado, varianza),
que inflarían el texto. Decisión: declararlo explícitamente como valor indicativo
("del orden de miles de casos"; "cifra indicativa que depende del régimen de
aprendizaje y del desempeño objetivo, no derivada del corpus actual"), en una
formulación compacta idéntica en sustancia en las tres apariciones (`10:10`,
`08:54`, `12:139`). Alternativa descartada: introducir un cálculo de potencia
artificial, que agregaría una justificación no sustentada por datos.

### D4 — Priorización de líneas futuras

Se agrega al inicio del capítulo de recomendaciones (`10`) un párrafo breve que
declara la prioridad: primero las líneas que atacan los defectos medidos
(calibración del gate de confianza, clasificador supervisado con corpus propio y
corrección de la medición de intervención humana), luego las extensiones
funcionales (canales, paneles, base de conocimientos). El párrafo remite a las
limitaciones de la discusión y no introduce claims nuevos.

### D5 — Secuenciación con los demás changes de contenido

- `c-104-bibliografia-y-atribucion`: ya aplicado (tipado Touvron/Jurafsky). Este
  change NO toca esas entradas; si agrega una entrada de mercado, solo AGREGA.
- `c-116` (reducción de páginas, cap <= 100): se aplica DESPUÉS. Este change debe
  ser neutro o reductor en páginas (D6).
- Otros changes de contenido (`c-105`/`c-106`/`c-107`/`c-108`/`c-109`/`c-111`):
  independencia por archivo; re-verificar solape antes de aplicar. `08-discusion.tex`
  y `10-recomendaciones.tex` pueden solaparse con changes de la dimensión 7; coordinar.

### D6 — Presupuesto de páginas

Baseline: 104 páginas. Las reformulaciones se redactan de longitud neutra o menor;
el párrafo de priorización se compensa recortando redundancia en los propios
pasajes editados. Se registra el conteo antes y después; si crece, se recorta sin
alterar contenido ajeno.

### D7 — Instrumentos de verificación

`verify_citations.py` como guardia de integridad de citas (huérfanas / sin usar);
verificación por `grep` de que no quedan formulaciones sin respaldo ni ocurrencias
inconsistentes del umbral; compilación con la imagen `texlive-thesis` y revisión
de `main.log` (0 fatales, 0 referencias indefinidas) y del PDF con `pdftotext`.

## Risks / Trade-offs

- **Reformular en vez de citar podría leerse como debilitamiento.** Mitigación: la
  observación propia se ancla a una base declarada (documentación pública, fecha).
- **Informe de mercado sin DOI resoluble.** Mitigación: D2 (ruta secundaria solo
  con DOI verificado; por defecto se reformula).
- **Inconsistencia del umbral entre apariciones.** Mitigación: D3 y escenario de
  consistencia en el delta; verificación por grep.
- **Crecimiento de páginas.** Mitigación: D6.
- **Solape con changes de contenido.** Mitigación: D5 (re-verificar antes de aplicar).

## Open Questions

- El dictamen menciona el umbral "cuatro veces" pero solo se localizan tres
  apariciones en `sections/` (`10:10`, `08:54`, `12:139`); `grep` sobre `paper/`
  no halla una cuarta. Se tratará como ambigüedad de conteo: en apply se re-verifica
  con grep y, si aparece una cuarta, se alinea con la misma formulación.
- Si en apply se halla un informe de mercado con DOI resoluble y pertinente, se
  evalúa la ruta secundaria de D2; de lo contrario se mantiene la reformulación.
