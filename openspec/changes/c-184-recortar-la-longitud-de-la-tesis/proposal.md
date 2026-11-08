# Proposal: Recortar la longitud de la tesis

## Why

El PDF vigente (`docs/Tesis/v10 (IA)/paper/main.pdf`, release `v1.2.8`) tiene **118
paginas totales** frente al tope de la catedra **total <= 100** (exceso **+18**), medido
con `pdfinfo` (118; encabezado `Anexos` en la p. 108 de `main.toc` => cuerpo 107, anexos 11).
El registro vigente consigno el resultado con la regla superada "cuerpo sin anexos <= 100"
(rama (b) del 2026-10-26, "+7 de cuerpo"), que el dictamen declaro superada el 2026-10-27
(G0.1, `dictamen-correcciones.md:700-712`). Hace falta acercar el total al tope **sin perder
contenido** y corregir la contabilidad de paginas a la regla vigente.

## What Changes

- Reducir la longitud del PDF acercandolo al tope **total <= 100**. La meta es el "punto
  dulce": **no alcanzarlo no invalida el change**, pero cuanto mas se recorte, mejor.
- **Sin perdida de contenido**: ninguna afirmacion, valor canonico, tabla, figura ni
  referencia se elimina; ningun `\label` queda huerfano.
- **Correccion contable**: `dictamen-correcciones.md` (entrada del libro mayor de c-169) y la
  clausula "Release vigente `v1.2.8`" de `CHANGES.md` pasan a reportar el exceso **sobre el
  total** (+18 sobre 100); la cuenta por cuerpo sin anexos (rama (b), superada) se retira como
  base del cumplimiento y queda solo como informacion complementaria.
- **Fases de recorte**: Fase A (forma: reubicar figuras de cuerpo a Anexo A con el precedente
  de c-139, resolver el flotante `[p]`, limpiar `Overfull \hbox`) y Fase B (de-duplicacion:
  pasajes repetidos reemplazados por `\autoref` a su seccion primaria) son aplicables y
  verificables de forma independiente; Fase C (condensar los capitulos 4 y 6) queda como
  **decision explicita del autor**.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: se ajustan tres requisitos existentes. (1) `Presupuesto de páginas
  preservado`: fija que la metrica es el total del PDF, prohibe la metrica superada
  cuerpo-sin-anexos como base del cumplimiento, y consigna la release `v1.2.8` (118 total,
  exceso +18). (2) `Verificación de compilación tras la reducción`: la meta <= 100 pasa a ser
  objetivo no obligatorio y se registra el conteo alcanzado. (3) `Reducción sin pérdida de
  contenido científico`: agrega el plan por fases, las palancas admisibles (reubicacion a
  anexos, de-duplicacion por remision) y las palancas prohibidas (interlineado/margenes APA 7,
  fuente de bibliografia, `\newpage` de capitulo).

## Impact

- `docs/Tesis/v10 (IA)/paper/sections/*.tex` (05, 07, 09, 01, 10, 11, 06, 03, 12) y
  `preambles/preamble.tex` (solo lectura); `verify_citations.py`; PDF y renders derivados.
- `docs/Tesis/Correcciones/dictamen-correcciones.md` (libro mayor de c-169).
- `CHANGES.md` (clausula "Release vigente `v1.2.8`"; su registracion completa ocurre al
  archivar).
- Gobernanza **MEDIUM** (presentacion del documento academico). Sin cambios en `App/`,
  `n8n/`, `evaluation/`, `openspec/config.yaml`, cadenas canonicas ni `docs/Tesis/v9 (IA)/`.
