## Why

El plan de correcciones fija un tope duro de 100 paginas para el documento. La
tesis compila hoy en **104 paginas** (`pdfinfo main.pdf`), 4 por encima del tope,
tras las adiciones de c-105 (glosario), c-106 (reduccion del resumen 105->104) y
c-110 (marco teorico HITL). Ningun change en curso posee la reduccion: c-112..c-115
agregan contenido y c-111 solo etiqueta. Sin este change el manuscrito no cumple
el limite de entregables.

## What Changes

- Reducir el PDF de 104 a **<= 100 paginas** eliminando redundancia y ajustando
  formato, sin tocar contenido cientifico, cifras ni correcciones ya aplicadas.
- Presupuesto por seccion (suma >= 4 paginas): glosario 0,3; Capitulos 1-4 1,1;
  Capitulos 5-7 1,0; Capitulos 8-11 1,1; Anexos 1,2 (detalle en design.md).
- Palancas: pasajes duplicados residuales (par 1.1/2.1, 8.1/9.1, resumen vs
  introduccion), leyendas de figura/tabla sobre-extendidas, listas redundantes,
  tamano del glosario, espaciado vertical alrededor de figuras y compactacion de
  anexos.
- Recompilar y verificar: `pdfinfo` <= 100 paginas y 0 referencias indefinidas.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `tesis-document`: el requisito de presupuesto de paginas cambia de 103 paginas
  exactas a un tope de 100 medido sobre el total del PDF, y se agregan requisitos
  de reduccion sin perdida de contenido cientifico y de verificacion de compilacion.

## Impact

- `docs/Tesis/v9 (IA)/paper/sections/*.tex` (prosa, leyendas, listas, glosario).
- `docs/Tesis/v9 (IA)/paper/main.pdf` (recompilacion).
- Requisito "Presupuesto de paginas preservado" de `tesis-document` (hoy 103).
- No toca `.bib`, `App/**` ni el contenido cientifico. Governance HIGH.
