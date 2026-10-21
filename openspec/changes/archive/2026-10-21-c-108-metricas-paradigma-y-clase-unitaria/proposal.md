# Proposal: c-108 — Paradigma metrico y tratamiento de la clase unitaria

## Why

El dictamen CONEAU 2026-10-20 (item 5) observa una mezcla de paradigmas
metricos: el micro-F1 reportado (`0,6654`) no es compatible con una tarea
monoetiqueta, donde coincidiria con la exactitud (`0,735`); la presencia
simultanea de subset accuracy y Hamming loss sugiere una verdad de referencia
multietiqueta que el clasificador no produce, y esos indicadores penalizan
estructuralmente una salida forzada a una etiqueta. El item 10 pide reportar el
intervalo de confianza del kappa y de las metricas por clase, y tratar la clase
con `n = 1` (`Bases de Datos`) como no estimable. El Gate 0 c-102 ya fijo los
valores canonicos y las decisiones de paradigma; sin este change, el capitulo 7
no es interpretable internamente.

## What Changes

- **Definir el paradigma y unificar el marco metrico.** Declarar que la
  referencia de verdad es multietiqueta (`107/200`), fijar la metrica primaria
  monoetiqueta (exactitud estricta `0,7350` + macro-F1 `0,5207`) y las
  secundarias multietiqueta (subset accuracy `0,43`, Hamming loss `0,3586`,
  micro-F1 `0,6654`), y presentarlas en un unico marco que explicite la
  referencia y la penalizacion estructural. El micro-F1 NO se presentara como
  equivalente de la exactitud de etiqueta unica.
- **Reportar incertidumbre.** Agregar el IC del kappa de doble etiquetado y los
  IC de las metricas por clase (precision, sensibilidad, F1) en metodologia y
  resultados, con el procedimiento declarado.
- **Tratar la clase con n=1 como no estimable.** Excluir `Bases de Datos` del
  macro-F1 de umbral (4 clases estimables `0,6508`) y de los IC; conservar el
  macro-F1 de cinco clases (`0,5207`) como valor informativo.
- **Registrar los valores nuevos en el memo canonico.** El IC del kappa y los IC
  por clase SHALL incorporarse a `docs/Tesis/Correcciones/numeros-canonicos.md`.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `tesis-numeros-canonicos`: se agrega la obligacion de registrar el IC del kappa
  y los IC de las metricas por clase, y de declarar no estimable la clase con
  soporte unitario en esos estimadores.
- `tesis-document`: se agrega el marco metrico unificado mono/multietiqueta en
  los capitulos 4, 7 y 8, y el reporte de los IC del kappa y por clase.

## Impact

- Capitulos `04-marco-metodologico.tex`, `07-resultados.tex`, `08-discusion.tex`
  de `docs/Tesis/v9 (IA)/paper/sections/`. No se toca codigo de runtime ni la API.
- Fuente de verdad: `docs/Tesis/Correcciones/numeros-canonicos.md` (c-102); el IC
  del kappa y los IC por clase se incorporan alli.
- Posible herramienta de recalculo en `evaluation/metrics.py` (IC por clase y de
  conjunto); el kappa puede no ser computable desde las fuentes actuales.
- Compilacion: `latexmk` con Docker (`texlive-thesis`); hoy 103 paginas.
- Governance: ALTO (afecta afirmaciones centrales de la tesis).
- Secuenciacion: comparte archivos `.tex` con c-104/c-105/c-106/c-107/c-109/c-110;
  MUST serializarse para evitar conflictos de edicion concurrente.
