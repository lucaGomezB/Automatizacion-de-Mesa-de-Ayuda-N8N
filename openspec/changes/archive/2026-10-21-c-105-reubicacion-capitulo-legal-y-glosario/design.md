# Design — c-105 — Reubicación del capítulo legal y glosario de siglas

## Context

Ver `proposal.md` — Why. Estado verificado por lectura directa de
`docs/Tesis/v9 (IA)/paper/`:

- `main.tex` ordena el cuerpo así: `01-introduccion` … `06-implementacion`,
  `07-resultados`, `08-discusion`, `09-conclusiones`, `10-recomendaciones`,
  `11-aspectos-legales`, y luego referencias y `12-anexos` (dentro de
  `appendices`).
- `sections/11-aspectos-legales.tex:4` declara
  `\section{Consideraciones éticas y aspectos legales}\label{sec:aspectos-legales}`.
  Remite con etiqueta a `sec:arquitectura` y `sec:resultados`; otros capítulos
  (`02-marco-teorico.tex:62`, `08-discusion.tex:62`) remiten a
  `sec:aspectos-legales`. Todas son `\label`/`\autoref` (c-103), de modo que el
  movimiento no rompe referencias.
- `preambles/preamble.tex` carga `hyperref` (habilita `\autoref`), `appendix`,
  `booktabs`, `array`, `longtable` NO está cargado. `glossaries` NO está cargado.
- `main.pdf` compila en **103 páginas** con la imagen `texlive-thesis`
  (XeLaTeX + latexmk, `latexmkrc` fija `$pdf_mode = 5`). El `Dockerfile` usa
  `texlive/texlive` (esquema completo: `makeglossaries` disponible, pero no se
  usa).
- El spec principal `tesis-document` ya contiene el escenario "Reubicación del
  capítulo 11 segura" dentro del requisito "Integridad de referencias cruzadas";
  c-105 no lo modifica.

## Goals / Non-Goals

**Goals:**

- Ubicar el capítulo legal antes de resultados (deja de ser apéndice encubierto).
- Agregar un glosario de siglas con cobertura completa sobre el cuerpo.
- Cero referencias indefinidas y cero etiquetas duplicadas tras la recompilación.

**Non-Goals:**

- No reescribir prosa ni contenido científico de ningún capítulo.
- No normalizar tildes (c-106) ni tocar `Bibliography_base.bib` (c-104).
- No integrar el capítulo legal dentro del marco metodológico (reestructuración
  mayor, descartada; ver D1).
- No introducir `glossaries`/`makeglossaries` ni cambiar el pipeline de build
  (ver D2).

## Decisions

### D1. Nueva posición: antes de resultados, después de implementación

Se mueve `\input{sections/11-aspectos-legales.tex}` a entre `06-implementacion` y
`07-resultados`. El dictamen ofrece dos opciones: "antes de resultados" o
"integrarlo a la metodología". Se elige la primera porque materializa la
reubicación con el menor impacto estructural: el capítulo conserva su cuerpo
íntegro y su numeración se recalcula (pasa a ser el capítulo 7; resultados y
posteriores se renumeran). Alternativa descartada: integrarlo al marco
metodológico (capítulo 4), que exigiría reescribir y fusionar contenido, fuera
del alcance de item 15 y con riesgo de conflicto con c-93. El archivo fuente
MUST NOT renombrarse (evita reescribir rutas y banners ajenos).

### D2. Glosario manual en material preliminar, sin dependencia nueva

Se crea `sections/00-glosario.tex` con una lista por descripción (o `longtable`)
de sigla → expansión, en orden alfabético, ubicada después de `\listoffigures` y
antes del cuerpo, con entrada en el índice general. Alternativa descartada: el
paquete `glossaries` con `\makeglossaries`/`\printglossaries`, que agrega un paso
`makeglossaries` al build y altera el pipeline determinista de `latexmk`. El
dictamen pide "un glosario de siglas", no expansión automática en el cuerpo; un
glosario manual es verificable, no requiere tooling nuevo y no depende del orden
de compilación.

### D3. Cobertura del glosario definida por inventario reproducible

El universo de siglas se fija por inventario del cuerpo: extraer tokens en
mayúsculas (siglas/acrónimos) de `sections/*.tex`, depurar falsos positivos
(palabras entre llaves, comandos) y acordar la lista final. La verificación de
cobertura es un `grep` sobre el cuerpo contra las entradas del glosario, de modo
que "sin sigla sin expandir" y "sin entrada sin uso" son comprobables.

### D4. Nombres de archivo y banners

`11-aspectos-legales.tex` conserva su nombre; solo cambia su posición en
`main.tex`. Los banners `% Capitulo 11: ...` y los comentarios de `main.tex` se
actualizan para reflejar la nueva numeración (cosmético, no afecta la
compilación).

### D5. Secuenciación con las ramas de contenido de la tesis

c-104, c-106, c-107, c-108, c-109 y c-110 comparten `main.tex` y `sections/*.tex`
y se aplican en serie (nunca en paralelo sobre los mismos archivos). c-105 depende
de c-103 (ya archivado) porque la seguridad de la reubicación se apoya en
`\label`/`\autoref`. Interacción clave: c-106 normaliza la acentuación y c-105
edita `main.tex` y agrega `00-glosario.tex`; para evitar conflictos, c-105 se
aplica sobre el estado que deje c-106 (o se acuerda el orden inverso) y solo
introduce texto nuevo (glosario) más el reordenamiento de una línea. Tensión de
presupuesto: c-107 apunta a ≤ 100 páginas desde 103; el glosario agrega
aproximadamente una página. c-105 no posee la reducción a 100 y MUST NOT
empeorarla más de lo mínimo; su verificación registra el conteo resultante.

## Risks / Trade-offs

- Referencia indefinida tras reordenar `\input` → todas las remisiones usan
  etiquetas (c-103); verificar el log sin "undefined reference" ni "multiply
  defined label" y recompilar dos pasadas con `latexmk`.
- El glosario agrega páginas y tensiona el límite de 100 de c-107 → mantenerlo
  en una página, en material preliminar, y registrar el conteo final.
- Conflicto de edición con c-106/c-107/c-108/c-110 sobre `main.tex`/`sections/` →
  aplicación serial; c-105 toca una sola línea de `main.tex` y agrega un archivo
  nuevo, minimizando la superficie de conflicto.
- Falsos positivos en el inventario de siglas (comandos LaTeX, palabras en
  mayúsculas) → depuración manual del inventario antes de fijar las entradas.

## Migration Plan

1. Inventariar siglas del cuerpo y acordar la lista de entradas.
2. Crear `sections/00-glosario.tex` y su `\input` en el material preliminar.
3. Reordenar el `\input` de `11-aspectos-legales.tex` antes de `07-resultados`.
4. Actualizar banners/comentarios de numeración.
5. Recompilar con `texlive-thesis` y verificar: cero referencias indefinidas,
   glosario presente y numeración recalculada.

Rollback: `git revert` del commit del change restaura el orden de `main.tex` y
elimina el glosario. Sin migraciones de datos ni estado externo.

Comando de compilación:

```
docker run --rm -v "/home/skywalker/Desktop/notas/Tesis/Automatizacion-de-Mesa-de-Ayuda-N8N/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex
```

## Open Questions

- Ninguna que altere el alcance, los specs o las tareas. La elección entre
  material preliminar y material final para el glosario se resuelve en D2
  (preliminar); si una revisión posterior prefiere material final, no cambia los
  requisitos ni el desglose de tareas.
