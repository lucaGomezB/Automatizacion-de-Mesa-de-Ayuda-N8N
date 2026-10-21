## Context

Ver `proposal.md` — Why. Estado verificado por lectura directa de la fuente en
`docs/Tesis/v9 (IA)/paper/` durante esta sesión:

- `main.pdf` compila en **103 páginas** (XeLaTeX/MiKTeX).
- `sections/00-portada.tex` (32 líneas): cabecera "UNIVERSIDAD TECNOLÓGICA
  NACIONAL / FACULTAD REGIONAL MENDOZA", rótulo "Tecnicatura Universitaria en
  Programación", título, "Trabajo Final de Carrera presentado...", autores,
  "Director: Prof. Alberto Cortez", "Mendoza, República Argentina", "2026" fijo.
- `preambles/preamble.tex`: `\documentclass[11pt,a4paper]{article}`; `graphicx`
  con `\graphicspath{{./figures/}}`; `hyperref` cargado (habilita `\autoref`);
  `cleveref` NO está cargado; `pdfsubject={Tesis de Grado — ...}`.
- `assets/logo-utn-frm.png`: PNG 332×62, 8-bit RGBA, entrelazado.
- Inventario de referencias: **23 `\label`** en `sections/`; **71 ocurrencias**
  del patrón de remisión dura "Capítulo N"/"Sección N.N" en `sections/` (de las
  cuales ~11 son comentarios de cabecera de archivo); ~93 comandos
  `\section`/`\subsection`, casi todos sin `\label`. Solo `sec:metricas-multiclase`
  y `subsec:calibracion` son etiquetas de sección.
- `\documentclass{article}` renderiza "1", "1.1" mientras la prosa dice "Capítulo N":
  inconsistencia señalada por el dictamen.
- Remisión errónea: `sections/07-resultados.tex:32` remite a "Sección~4.4" para la
  cota de 45 s, que se enuncia en 4.6 (`04-marco-metodologico.tex:67`).

## Goals / Non-Goals

**Goals:**
- Portada formal con logo UTN-FRM, "Trabajo Final de Carrera", autores y dos
  directores, fecha `\today`.
- Metadatos PDF coherentes con "Trabajo Final".
- Infraestructura de referencias por etiquetas: cero remisiones duras, cero indefinidas.
- PDF preservado en 103 páginas.

**Non-Goals:**
- No corregir prosa ni contenido científico.
- No normalizar tildes (c-106).
- No tocar `Bibliography_base.bib` (c-104).
- No migrar a `report`/`book` (agrega saltos de página).
- No crear figuras ni embeber panel/dashboard (c-80).
- No reubicar el capítulo 11 (c-105); sí dejarlo listo para moverse.

## Decisions

### D1. Mecanismo de referencia: `\autoref` con nombres renombrados

`hyperref` ya está cargado, así que `\autoref` está disponible sin dependencias
nuevas; `cleveref` no está cargado y agregarlo sería una dependencia nueva no
justificada. Se define `\renewcommand{\sectionautorefname}{Sección}` y
`\renewcommand{\subsectionautorefname}{Sección}` para que la prosa quede en
"Sección 4.6". Alternativas: (a) `\ref` con "Sección~" escrito a mano — funciona
pero es más verboso y propenso a error; (b) `cleveref` — rechazada por dependencia
nueva. Se prefiere `\autoref`.

### D2. Convención de etiquetas

Prefijos estables: `sec:<slug>` para `\section`, `subsec:<slug>` para
`\subsection`, con slug en kebab-case ASCII derivado del título. Se conservan las
etiquetas existentes `sec:metricas-multiclase` y `subsec:calibracion`.

### D3. Logo sin romper el presupuesto de páginas

El logo se inserta con `\includegraphics[width=...]{assets/logo-utn-frm.png}` en la
portada. Como `\graphicspath{{./figures/}}` no incluye `./assets/`, se agrega `./`
y `./assets/` al `\graphicspath` (o se usa la ruta relativa explícita). La altura
del logo (~2 cm) y los espacios de la portada se ajustan (reducción de los
`\\[..pt]`) para que la portada siga ocupando una sola página y el PDF quede en 103.
Verificación: `pdfinfo main.pdf | grep Pages` == 103.

### D4. Fecha con `\today`

Se reemplaza el "2026" fijo por `\today`; babel spanish lo renderiza como "20 de
octubre de 2026". No se hardcodea.

### D5. Nomenclatura sin reemplazo ciego

Se renombran las 6 ocurrencias de "Tesis de Grado" (preamble 2, 3, 85; main 2, 33;
portada 2). La ruta `docs/Tesis/Correcciones/...` (`12-anexos.tex:143`) se
preserva. Se evita el reemplazo global porque "hipótesis" y "síntesis" contienen
la subcadena "tesis".

### D6. Orden de trabajo (Gate 0 serial)

Primero etiquetas, luego conversión de remisiones, luego portada y metadatos, luego
compilación y verificación. Un solo commit para mantener la migración atómica.

## Risks / Trade-offs

- Migración masiva de referencias en un solo commit → compilar y verificar el log
  (cero undefined/multiply-defined) antes de cerrar; reversible con `git revert`.
- Conflicto con c-104/c-105 si introducen remisiones nuevas → c-104 (bibliografía)
  no toca referencias; c-105 debe escribir sus remisiones con etiquetas. c-103 va
  primero.
- Logo de 332 px insuficiente para 300 dpi → NO bloquea; nota explícita de que se
  solicitará una versión ≥1200 px o vectorial.
- Dependencia con el movimiento del capítulo 11 (c-105) → las etiquetas hacen el
  movimiento seguro; c-105 solo reordena `\input` en `main.tex`.

## Migration Plan

1. Agregar labels a todas las secciones/subsections.
2. Convertir remisiones duras a `\autoref`/`\ref`; corregir 4.4→4.6.
3. Portada + metadatos + nomenclatura.
4. Compilar y verificar: 103 páginas, cero indefinidas, cero duras.

Rollback: `git revert <commit>` restaura el estado previo (sin estado externo ni
migraciones de datos).

## Open Questions

- ¿Se dispone de una versión del logo ≥1200 px o vectorial? Se resuelve sin
  bloquear el change: se usa la versión actual (332 px) y se deja la nota de
  seguimiento para reemplazarla cuando esté disponible.
