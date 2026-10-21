# Proposal: c-105 — Reubicación del capítulo legal y glosario de siglas

## Why

El dictamen CONEAU (item 15, recomendado) señala dos defectos de organización en
la tesis v9 (103 páginas), `docs/Tesis/v9 (IA)/paper/`:

1. El capítulo de consideraciones éticas y legales
   (`sections/11-aspectos-legales.tex`) está ubicado **después de conclusiones y
   recomendaciones**, lo que lo convierte en un apéndice encubierto y lo
   desconecta del flujo argumental.
2. El documento **no tiene glosario de siglas**: el lector encuentra acrónimos
   (ARCO, ASR, CIA, HMAC, N8N, RPA, etc.) sin un lugar único donde se expandan.

c-103 (Gate 0) ya migró todas las remisiones a `\label`/`\autoref`, de modo que
reordenar los `\input` de `main.tex` ya es seguro. Este change materializa la
reubicación y agrega el glosario.

## What Changes

- **Reubicación**: mover `\input{sections/11-aspectos-legales.tex}` de su
  posición actual (después de `10-recomendaciones.tex`) a **antes de
  `07-resultados.tex`** y después de `06-implementacion.tex` (opción "antes de
  resultados" del dictamen). No se renombra el archivo; la numeración del
  capítulo se recalcula automáticamente.
- **Glosario**: agregar una sección "Glosario de siglas y acrónimos" en el
  material preliminar (después de los índices y antes del cuerpo), con orden
  alfabético y una entrada por sigla usada en el cuerpo.
- **Sin cambios de contenido científico**: no se reescribe prosa de los
  capítulos, no se tocan números canónicos (c-107), tildes (c-106), bibliografía
  (c-104) ni figuras (c-80).

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: agrega el requisito de ubicación del capítulo de
  consideraciones éticas y legales dentro del flujo argumental (no como apéndice
  encubierto) y el requisito de un glosario de siglas y acrónimos con cobertura
  completa sobre el cuerpo. El requisito de integridad de referencias cruzadas y
  su escenario "Reubicación del capítulo 11 segura" ya están sincronizados en el
  spec principal; este change no los modifica.

## Impact

- `docs/Tesis/v9 (IA)/paper/main.tex`: reordenar una línea `\input` y agregar el
  `\input` del glosario en el material preliminar.
- `docs/Tesis/v9 (IA)/paper/sections/00-glosario.tex` (nuevo) y
  `docs/Tesis/v9 (IA)/paper/sections/11-aspectos-legales.tex` (sin cambios de
  cuerpo; solo la posición en `main.tex` cambia).
- Sin dependencias de código ni de datos. Compilación con la imagen Docker
  `texlive-thesis` (XeLaTeX/latexmk), actualmente 103 páginas.
- Secuenciación: comparte `main.tex` y `sections/*.tex` con c-104/c-106/c-107/
  c-108/c-109/c-110, que se aplican en serie.
