## Context

Ver `proposal.md` — Why. La rama c-107 es consumidora del Gate 0 c-102
(`docs/Tesis/Correcciones/numeros-canonicos.md`) y debe propagar sus valores
`vigente`. No edita el memo, `CHANGES.md` ni ningún otro artefacto fuera de los
`.tex` de la tesis. Las decisiones editoriales las confirmó el autor el
2026-10-21; este `design.md` las registra y declara su reversibilidad (governance
ALTO: afectan afirmaciones centrales de la tesis).

Fuente de verdad (solo lectura): `docs/Tesis/Correcciones/numeros-canonicos.md`
(Sección 3.4 para intervención, universo y proyección; Sección 7 puntos 1-2 para
las decisiones no resolubles). Dictamen: `auditorias/Dictamen_Tesis_v9_CONEAU_2026-10-20.md`
recomendaciones obligatorias 1, 2 y 4.

**Nota de numeración de líneas.** Igual que en c-102, las referencias
`archivo:línea` usan la numeración de Python/editores (universal newlines).
`07-resultados.tex` tiene un CR suelto en su línea 17: `grep -n`, `sed -n` y
`awk` reportan un número uno menor para toda línea posterior a la 17.

## Goals / Non-Goals

**Goals:**

- Propagar el retiro del `9,5 %` y reformular el aporte operativo como no medido.
- Propagar el universo de días hábiles (`≈ 2.646`, `≈ 32,2 h`) y retirar el
  calendario (`3.700`, `45,0 h`).
- Recalcular el margen muestral con `N ≈ 2.646` y actualizar el costo de API.
- Declarar el estado de la hipótesis principal como parcialmente confirmada y
  parcialmente refutada en resumen, discusión y conclusiones.
- Dejar la tesis compilando y registrando el conteo de páginas.

**Non-Goals:**

- No editar el memo canónico ni `CHANGES.md` ni `dictamen-correcciones.md`.
- No reducir el resumen a 250 palabras (recomendación 8, fuera de alcance).
- No re-ejecutar el clasificador ni llamar a Gemini/N8N/Twilio.
- No tocar el `19` de `07-resultados.tex:155` (es un acierto por banda, no la
  intervención).

## Decisions

### D1 — Regla de reformulación del `9,5 %`

El `9,5 %` (`19/200`) está `retirado` en el memo. La regla de reformulación es:
el flujo automatizado solo deriva intervención por el gate
`requiere_revision_humana = (confianza < 0,70)`; en el corpus ese gate no dispara
ningún caso (Gemini nunca baja de `0,85` y la etapa determinística fija el campo
en `False`), de modo que la proporción derivable del propio flujo es `0 %`; y,
como NO se conserva un registro primario de intervención por caso, el aporte
operativo se declara **no medido**. Alternativa descartada: reportar `0 %` como
resultado, porque tampoco hay registro de que ningún operador interviniera: el
`0 %` es del gate, no de la intervención real observada.

### D2 — Universo único de días hábiles

Se adopta `≈ 2.646 = 42 × 63` días hábiles (`88 × 5/7 ≈ 62,86 ≈ 63`) y se retira
`3.700 = 42 × 88` calendario. Los cuatro valores (`04:45`, `04:51`, `08:14`,
`08:56`) más las menciones de resumen e introducción (`00:11`, `01:18`) MUST
moverse juntos. Alternativa descartada: conservar `3.700` justificando el
calendario; el dictamen (rec. 4) y el memo lo marcan `retirado`.

### D3 — Recálculo del margen muestral

Fórmula con corrección por finitud: `n = n0 / [1 + (n0 − 1)/N]`, con
`n0 = z² p(1−p)/e²`. La restricción es reproducir `n = 200` con `N = 2.646`.

Despejando `n0` de `n = 200`:

```
n0 = n · (N − 1)/(N − n) = 200 · 2645 / 2446 = 216,27
```

Luego `e² = z² p(1−p)/n0 = 1,96² · 0,5 · 0,5 / 216,27 = 0,9604 / 216,27 =
0,0044406`, de donde:

```
e = √0,0044406 = 0,06664  →  e ≈ 6,66 %
```

Verificación: `n = 216,27 / [1 + 215,27/2.646] = 216,27 / 1,08136 = 200,0`. ✔

Contraste con el valor retirado: con `N = 3.700` el mismo procedimiento con
`e = 6,74 %` da `n0 = 0,9604/0,0045428 = 211,41` y `n = 211,41/1,05687 = 200,03`.
Al caer el universo a `2.646`, para seguir obteniendo `n = 200` el margen baja a
`6,66 %`. El texto MUST declarar `N ≈ 2.646` y `e ≈ 6,66 %`.

Proyección horaria: `43,82 s/incidente × 2.646 incidentes / 3.600 s/h =
115.987,7 / 3.600 = 32,22 h`, es decir `≈ 32,2 h`.

### D4 — Costo de API

`08-discusion.tex:56` declara `3.700` incidentes trimestrales y `34,5 %` de
inferencia externa (69/200). Recálculo sobre el universo vigente:
`2.646 × 0,345 = 912,9` invocaciones × `≈ 7×10⁻⁴ USD` `≈ 0,64 USD`, en el orden de
`1 USD` y por debajo de la cota de `2 USD`. La regla de reformulación: cambiar el
volumen a `≈ 2.646` conservando el porcentaje `34,5 %`, los supuestos de tokens y
la cota superior de `2 USD`.

### D5 — Estado de la hipótesis

La hipótesis principal del `01-introduccion.tex:32` combina tiempo, intervención
y umbrales de clasificación. Al retirar la intervención y no alcanzar los umbrales
(`73,5 %` y `0,5207` frente a `85 %` y `0,85`), el estado SHALL declararse
**parcialmente confirmada** (tiempo) y **parcialmente refutada** (clasificación) en
`00-resumen.tex` (resumen y abstract), `08-discusion.tex` y `09-conclusiones.tex`.
El resumen MUST NOT sugerir confirmación plena (dictamen rec. 2).

### D6 — Capacidades modificadas

Se modifican DOS capacidades: `tesis-numeros-canonicos` (obligación de propagación
de las ramas consumidoras) y `tesis-document` (universo, intervención, margen,
hipótesis, costo). Alternativa descartada: solo `tesis-numeros-canonicos`, que no
capturaría los requisitos observables del documento.

### D7 — Verificación de compilación

La verificación usa la imagen local `texlive-thesis`:
`docker run --rm -v "<repo>/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`.
No se edita el entorno. El PDF debe compilar sin errores fatales.

### D8 — Abstract en inglés

El abstract (`00-resumen.tex:25`) replica `3,700` y `9.5 %`. Aunque no figura en la
lista explícita de objetivos, se incluye por el requisito de consistencia del
resumen en inglés: dejar el abstract desactualizado reintroduciría una divergencia.
Se registra como objetivo de propagación adicional (decisión de c-107).

## Objetivos de propagación (ANTES → DESPUÉS)

| Objetivo | ANTES (palabra clave) | DESPUÉS (regla) |
|---|---|---|
| `07:137-138` | "9,5 % ... 181 (90,5 %) ... 19 (9,5 %) requirieron verificacion" | Declarar el gate (`confianza < 0,70`) y que no dispara casos en el corpus; declarar la intervención por caso como no medida |
| `07:155` | `[0,50;0,70)` 26 / 19 aciertos | INTOCABLE: el `19` es acierto por banda, no intervención |
| `00:11` | "universo aproximado de 3.700 incidentes" | "universo aproximado de 2.646 incidentes" |
| `00:13` | "descendio ... hasta el 9,5 %" | Retirar el 9,5 %; declarar el aporte operativo no medido y el estado parcial de la hipótesis |
| `00:25` (abstract) | "universe of approximately 3,700 ... decreased ... to 9.5 %" | "approximately 2,646" y retiro del 9.5 % |
| `01:18` | "45,0 horas-persona por trimestre" | "32,2 horas-persona por trimestre" |
| `04:34` / `04:65` | Dos dimensiones rotuladas (casos y tiempo) | Conservar las dos definiciones; en 7.3 reportar que la dimensión de casos no se midió |
| `04:45` | "3.700 ... 42 × 88 días de calendario" | "2.646 ... 42 × 63 días hábiles" |
| `04:51` | "N = 3.700 ... margen del 6,74 %" | "N ≈ 2.646 ... margen del 6,66 %" |
| `04:61` | "sin intervencion humana" | "sin intervención humana en la captura, con el gate de revisión aplicable" |
| `08:14` | "9,5 % ... 3.700 ... 45,0 h" | Retirar el 9,5 %; "2.646 ... 32,2 h"; actualizar el footnote del cálculo |
| `08:56` | "3.700 incidentes trimestrales ... 45,0 horas-persona" | "2.646 incidentes trimestrales"; costo recalculado; cota ≤ 2 USD |
| `09:16` | "la reducción de la intervencion humana alcanzó el 9,5 %" | Retirar la cifra; reformular el aporte operativo como no medido |
| `10:24` | "ocurre en el 9,5 % de los casos" | "ocurre en los casos derivados a revisión" (sin cifra) |

## Risks / Trade-offs

- **[Riesgo] Tocar el `19` equivocado.** `07:155` contiene un `19` de aciertos por
  banda. → **Mitigación**: solo se edita el bloque `07:137-138`; verificación con
  la Tabla 7.5 intacta (`98/26/6/31/39`).
- **[Riesgo] Divergencia por numeración de líneas.** El CR suelto de
  `07-resultados.tex:17` corre la numeración en `grep -n`. → **Mitigación**: se
  cita por palabra textual, no solo por línea; se verifica con Python.
- **[Riesgo] Presupuesto de páginas.** El plan exige ≤ 100 páginas; el PDF hoy
  tiene 103. → **Mitigación**: el cambio es principalmente en el mismo lugar; se
  compila y se registra el conteo. c-107 no posee la reducción a 100, pero MUST
  NOT aumentarlo; si el conteo sube, se revierte la redacción a la variante más
  corta.
- **[Riesgo] El resumen excede 250 palabras.** El resumen ya tiene 538 palabras.
  → **Mitigación**: reformular en el lugar y recortar compensando las frases del
  9,5 % retiradas; la reducción formal a 250 es otra recomendación (fuera de
  alcance), pero c-107 no debe empeorar la longitud.
- **[Riesgo] Reversibilidad.** Las decisiones D1/D2 son reversibles si el autor
  aporta la tabla primaria de intervención o ratifica el calendario. →
  **Mitigación**: el memo se actualiza (upsert) y c-107 se re-propaga; el
  `design.md` registra la condición.
- **[Riesgo] Costo de API inconsistente.** Cambiar el volumen sin el porcentaje o
  la cota. → **Mitigación**: `08:56` es un solo párrafo; se actualizan volumen,
  cálculo y cota juntos.

## Migration Plan

1. Editar los `.tex` según la tabla ANTES → DESPUÉS (un solo pase por archivo).
2. Compilar con Docker y confirmar cero errores fatales y conteo de páginas.
3. Verificar por búsqueda que no queden `9,5 %`, `3.700`, `45,0 h` como resultado.
4. Revertir = `git checkout` de los `.tex` (ningún otro artefacto se toca).

## Open Questions

Ninguna que cambie las specs o el enfoque. La justificación a priori del tamaño
muestral (recomendación 9 del dictamen) se conserva en su forma actual ("el margen
que reproduce el corpus") porque c-107 no la reescribe; queda como observación para
una rama posterior.
