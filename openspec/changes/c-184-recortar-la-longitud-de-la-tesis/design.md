# Design: Recortar la longitud de la tesis

## Context

Ver `proposal.md - Why`. Estado de partida medido (2026-11-08):

- `pdfinfo "docs/Tesis/v10 (IA)/paper/main.pdf"` = **118 paginas**; `main.toc:
  \contentsline {section}{Anexos}{108}` => cuerpo 107, anexos 11. Regla vigente:
  **total <= 100** (exigencia de la catedra, G0.1 2026-10-27, `dictamen-correcciones.md:700-712`).
  Exceso actual **+18**.
- Compilacion limpia: `main.log` con 0 `^!` y 0 `undefined`; 13 `Overfull \hbox` (varios > 10pt).
- `preambles/preamble.tex`: `\doublespacing` (linea 24), `geometry` 2,54 cm (linea 20),
  `\bibfont` = `\footnotesize` (linea 145). Todo congelado (APA 7; P8 no aplicado).
- Capitulos: 05 (162 lineas), 07 (260), 11 (102), 06 (119), 09 (53), 10 (70), 01 (78), 03 (92),
  12 (251).

## Goals / Non-Goals

**Goals:**
- Acercar el **total** al tope de 100 tanto como sea posible sin perder contenido; el punto
  dulce es 100, no un criterio obligatorio.
- Corregir la contabilidad de paginas a la metrica del total en el libro mayor de c-169 y en
  la clausula de release de `CHANGES.md`.
- Dejar Fases A y B verificables de forma independiente; Fase C explicitamente del autor.

**Non-Goals:**
- No tocar el preambulo (interlineado/margenes), la fuente de la bibliografia ni los `\newpage`.
- No recompilar ni commitear durante el propose; no editar la tesis ni `CHANGES.md` aqui.
- No reabrir valores canonicos, figuras ni referencias; no tocar `v9 (IA)`.

## Decisions

### D-regla: la metrica vigente es el total del PDF

El conflicto entre la rama (b) del 2026-10-26 ("cuerpo sin anexos <= 100") y la G0.1 del
2026-10-27 ("total <= 100") se resuelve a favor de la ultima: la regla (b) **queda superada**.
El registro de `v1.2.8` (dictamen y `CHANGES.md`) uso la regla superada ("+7 de cuerpo"); la
correccion lo pasa a "118 total, **+18** sobre 100 del total". La cuenta por cuerpo sin anexos
se conserva solo como dato complementario del libro mayor.

### D-fases: plan de recorte por fases independientes

| Fase | Alcance | Palanca | Verificacion | Estimacion (paginas de TOTAL) |
|---|---|---|---|---|
| A | Forma | Reubicar `fig:componentes` (05:32-37) y `fig:secuencia` (05:55-60) al Anexo A (precedente c-139 con `fig:cronograma`); cambiar `07:108 \begin{table}[p]` a `[htbp]`; compactar los `Overfull \hbox` > 10pt de 06:39-40, 11:54-64 y 11:78-90 | `main.toc` (Anexos), `main.lof`, inventario Anexo A, `main.log` (0 overfull > 10pt) | -1 a -3 |
| B | De-duplicacion | Reemplazar pasajes repetidos por `\autoref` a su seccion primaria: 09:41 (y 09:6); 01:18 (oracion final); 10:6,18,48; 11:8,32,34,36; 07:159,161,250-258; 03:6,8,12-14,56 | diff limite a esos pasajes; cifras y citas presentes en la seccion primaria | -2 a -5 |
| C | Condensacion | Capitulos 4 (`04:14,63,65,81,89`) y 6 (`06:99-113` y `06:36-46,70-77`); eventual reubicacion de capturas de UI | decision registrada del autor | -3 a -8 (gateado) |

**Estimacion realista:** la exploracion previa estimó -2 (forma) y -6 a -8 (de-duplicacion),
combinado -8 a -10. La re-derivacion de esta fase acota la de-duplicacion a -2 a -5 (los pasajes
repetidos son oraciones, no bloques; cada capitulo necesita liberar ~50 lineas para perder una
pagina) y deja la forma en -1 a -3 (mover a anexos baja el cuerpo pero el total solo baja si el
anexo tiene holgura; el flotante `[p]` puede devolver 1 pagina). **Realista con A+B: -3 a -8,
aterrizando en ~110-115 totales.** Llegar a <= 100 depende probablemente de la Fase C o de
reubicar bloques mayores; no alcanzarlo es aceptable por D-sweet-spot.

### D-sweet-spot: la meta 100 es objetivo, no obligacion

El autor confirma que la meta es el punto dulce <= 100 y que **no alcanzarlo es aceptable**,
siempre que el exceso quede declarado y honrado y no se recorte a costa del contenido. Se
refleja en `Verificación de compilación tras la reducción`: se registra el conteo alcanzado y su
delta, sin exigir <= 100.

### D-sin-perdida: invariante de contenido

Ninguna afirmacion, valor canonico, tabla, figura ni referencia se elimina. La de-duplicacion
solo procede cuando la afirmacion vive en su seccion primaria; la reubicacion conserva figura,
pie y fuente, y actualiza inventario e indice. Palancas prohibidas: preambulo (interlineado y
margenes APA 7), fuente de bibliografia, `\newpage` de capitulo.

### D-entorno: ciclo de compilacion y verificacion

Entorno de registro `texlive-thesis` (mismo de c-144/c-169):

```
docker run --rm -v "$PWD/docs/Tesis/v10 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex
pdfinfo "docs/Tesis/v10 (IA)/paper/main.pdf" | grep Pages
grep -n '\\contentsline {section}{Anexos}' "docs/Tesis/v10 (IA)/paper/main.toc"
python3 "docs/Tesis/v10 (IA)/verify_citations.py"
```

`total` = paginas de `pdfinfo`; `cuerpo` = pagina de `Anexos` en `main.toc` menos 1; `anexos` =
total - (cuerpo + portada/indices/glosario segun corresponda, consistente con las filas previas).
No se corre docker en el propose.

## Risks / Trade-offs

- **De-duplicacion que borra informacion no repetida** -> cada remision se verifica contra la
  seccion primaria antes de aceptarla; el diff no debe introducir afirmaciones huerfanas.
- **Mover figuras a anexos no baja el total** -> se verifica el total real con `pdfinfo`; la
  palanca se conserva por su efecto en el cuerpo aunque el total no baje.
- **Recompilacion pesada / drift de entorno** -> se usa la imagen `texlive-thesis` de registro;
  el conteo se ancla a `v1.2.8` (118).
- **Fase C invade contenido cientifico** -> gateada por decision explicita del autor; sin ella,
  los capitulos 4 y 6 no se tocan.

## Open Questions

- **Fase C (capitulos 4 y 6) y capturas de UI**: RESUELTO por decision del autor (2026-11-08).
  Fase C **APROBADA**, con una excepcion: las capturas de UI (`fig:panel_admin` y `fig:dashboard`,
  `06:99-113`) **PERMANECEN en el cuerpo**; NO se reubican a anexos. La Fase C se limita a
  condensar la prosa del capitulo 4 (`04:14,63,65,81,89`) y a ajustar las enumeraciones del
  capitulo 6 (`06:36-46,70-77`), sin retirar figuras ni contenido cientifico. Las Fases A y B
  proceden con normalidad.
- Nota de coordinacion: c-185 (ya aplicado) agrego una clausula en `04:69`; la condensacion de
  `04:69-79` debe preservarla.
