## Context

Ver `proposal.md` — Why. La rama c-108 es consumidora del Gate 0 c-102
(`docs/Tesis/Correcciones/numeros-canonicos.md`) y ejecuta los items 5 y 10 del
dictamen CONEAU 2026-10-20. No re-ejecuta el clasificador ni llama a
Gemini/N8N/Twilio: los valores ya estan recalculados en el memo. Governance ALTO
(afecta afirmaciones centrales de la tesis). Fuente de verdad (solo lectura):
memo canonico Seccion 3.2 y Seccion 5 (items 5 y 6).

**Nota de numeracion de lineas.** Igual que en c-102, las referencias
`archivo:linea` usan numeracion de Python/editores. `07-resultados.tex` tiene un
CR suelto en su linea 17: las herramientas que cortan solo por LF reportan un
numero uno menor para toda linea posterior a la 17 (por ejemplo, el parrafo de
metricas citado como `07-resultados.tex:108` aparece como `:107` en `grep -n`).

## Goals / Non-Goals

**Goals:**

- Declarar el paradigma (referencia multietiqueta) y unificar las cinco metricas
  en un solo marco en los capitulos 4, 7 y 8.
- Reportar el IC del kappa y los IC por clase (precision, sensibilidad, F1).
- Tratar `Bases de Datos` (`n = 1`) como no estimable y excluirla del macro-F1 de
  umbral; registrar los valores nuevos en el memo canonico.
- Dejar la tesis compilando y registrar el conteo de paginas.

**Non-Goals:**

- No re-ejecutar el clasificador ni servicios externos.
- No cambiar los valores canonicos ya fijados por c-102 (`0,7350`, `0,5207`,
  `0,43`, `0,3586`, `0,6654`).
- No tocar los capitulos fuera del alcance (`04`, `07`, `08`).
- No inventar la incertidumbre del kappa si no es computable.

## Decisions

### D1 — Paradigma y marco unificado

La referencia de verdad es **multietiqueta** (`107/200 = 53,5 %` de casos con mas
de un sector). La metrica primaria es monoetiqueta (exactitud estricta `0,7350` +
macro-F1 `0,5207`); las secundarias son multietiqueta (subset `0,43`, Hamming
`0,3586`, micro-F1 `0,6654`). El capitulo 7 presenta una **tabla unica** con
columnas `metrica | valor | tarea de referencia | nota`, y declara que el micro-F1
no es equivalente de la exactitud ni de las metricas de conjunto. Alternativa
descartada: retirar las metricas multietiqueta. Se conservan porque el dictamen
pide unificarlas, no eliminarlas, y su penalizacion estructural se declara.

### D2 — IC de las metricas por clase

- Precision y sensibilidad son proporciones binomiales por clase (una contra el
  resto): se estiman con `intervalo_wilson` (ya existe en `evaluation/metrics.py`).
- F1 no es una proporcion simple: su IC se estima por **bootstrap percentil**
  sobre los 200 casos (`B >= 2.000`, semilla fija, reproducibilidad exigida).
- Se agrega una funcion pura `intervalos_por_clase` (o equivalente) con tests en
  `evaluation/tests/`; determinista y sin servicios externos.

### D3 — IC de las metricas de conjunto

Subset accuracy, Hamming loss y micro-F1 se estiman por **bootstrap percentil a
nivel de caso** (remuestreo de los 200 casos con sus conjuntos verdad/predicho).
Misma semilla fija y numero de remuestreos que D2. El micro-F1 bootstrap respeta
la verdad multietiqueta del corpus.

### D4 — Clase con soporte unitario

`Bases de Datos` (`n = 1`) es **no estimable**: sin IC, excluida del macro-F1 de
umbral. Se reporta el macro-F1 de cuatro clases estimables (`0,6508`, metrica de
umbral) y el de cinco clases (`0,5207`, informativo). El `0,0000` de esa clase no
se presenta como evidencia de desempeno. Coincide con el item 6 del memo.

### D5 — IC del kappa (punto abierto)

El kappa `0,87` proviene del doble etiquetado independiente, pero **no hay datos
por caso de los dos analistas en `evaluation/`**: solo el valor agregado
(`00-resumen.tex:11`; memo `3.5`). El IC del kappa requiere la tabla de acuerdo
observado/esperado o las etiquetas por analista. Procedimiento:
1. Verificar si `data/Corpus Tesis - Hoja 1*.csv` u otra fuente contiene etiquetas
   por analista (columnas de doble etiquetado).
2. Si existen: calcular el IC por bootstrap sobre esos casos (semilla fija).
3. Si no existen: declararlo **no computable desde las fuentes permitidas** y
   consignar la condicion de reversibilidad (el autor aporta la tabla primaria),
   tal como el memo declara sus puntos no resolubles. NO se inventa el IC.

### D6 — Registro en el memo canonico

Los valores nuevos (IC del kappa si computable o su no-estimabilidad; IC por
clase; declaracion de no-estimabilidad de `Bases de Datos` en los IC) se agregan
al memo `docs/Tesis/Correcciones/numeros-canonicos.md` (upsert), no a un archivo
nuevo. Ninguna rama fija un numero sin actualizar el memo.

### D7 — Secuenciacion

c-108 edita `04-marco-metodologico.tex`, `07-resultados.tex` y
`08-discusion.tex`, compartidos con c-104/c-105/c-106/c-107/c-109/c-110. La rama
MUST serializarse respecto de esas ramas y ejecutarse **despues de c-107**
(propagacion canonica) para no reintroducir valores `retirado`.

## Risks

| Riesgo | Probabilidad | Mitigacion |
|---|---|---|
| IC del kappa no computable desde las fuentes | Alta | Declararlo no computable + condicion de reversibilidad (D5); no inventar |
| Conflicto de edicion concurrente en `04/07/08` | Media | Serializar (D7); verificar `git status` antes de aplicar |
| Bootstrap no determinista | Baja | Semilla fija y `B` documentado; tests de reproducibilidad |
| Presupuesto de paginas (hoy 103) | Media | Tabla unica en lugar de tablas separadas; medir paginas al final |

## Rollback Plan

`git revert` del commit de la rama restaura las tres `.tex` y, si se edito, el
memo canonico. Al ser cambios de texto, el revert no deja estado residual; se
recompila para confirmar el retorno a 103 paginas. Las decisiones D1-D7 quedan
registradas aqui para su revision.

## Dependencies

- `docs/Tesis/Correcciones/numeros-canonicos.md` (c-102, Gate 0).
- `evaluation/metrics.py` e `evaluation/predicciones.json` (recalculo offline).
- Imagen Docker `texlive-thesis` (compilacion).
