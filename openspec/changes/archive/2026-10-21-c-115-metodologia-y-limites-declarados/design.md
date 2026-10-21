## Context

Rama de corrección del dictamen CONEAU 2026-10-20 (dimensión 6 y dimensión 7). Es
consumidora del Gate 0 c-102 (`docs/Tesis/Correcciones/numeros-canonicos.md`) y del
change c-107, que propagó los números canónicos pero dejó la recomendación 9 como
pregunta abierta (ver su `design.md`, «Open Questions»). No edita el memo canónico,
no cambia valores canónicos y no edita `.tex` en la fase de propuesta.

Governance MEDIO/ALTO: las afirmaciones afectadas son metodológicas y de
conclusión; las decisiones editoriales se registran aquí y se declaran reversibles.

Fuente de verdad numérica (solo lectura): `docs/Tesis/Correcciones/numeros-canonicos.md`
(Sección 3.4 y Sección 7, punto 2). Dictamen: `auditorias/Dictamen_Tesis_v9_CONEAU_2026-10-20.md`
(dimensión 6, dimension 7, recomendaciones 9 y la síntesis final).

**Numeración de líneas.** Igual que c-102/c-107: referencias `archivo:línea` con
numeración de Python/editores (universal newlines). `07-resultados.tex` tiene un CR
suelto en su línea 17; no se edita ese archivo en este change.

## Goals / Non-Goals

**Goals:**

- Cerrar la rec. 9: declarar que el tamaño muestral se fijó por disponibilidad
  operativa y presentar el `6,66 %` como precisión implicada, no como calibración.
- Cerrar la dimensión 7h/6c: retirar el «riguroso» sin matizar en las conclusiones y
  llevar la dependencia etiquetadores/operadores a limitaciones y conclusiones.
- Dejar la tesis compilando sin aumentar el conteo de páginas.

**Non-Goals:**

- No recalcular ni cambiar valores canónicos (`N ≈ 2.646`, `e ≈ 6,66 %`, `n = 200`).
- No reintroducir `6,74 %`, `3.700`, `45,0 h` ni otras cifras retiradas.
- No editar el memo canónico, `CHANGES.md` ni `dictamen-correcciones.md`.
- No reducir páginas (eso es c-116, ejecutado después).
- No re-ejecutar el clasificador ni llamar a servicios externos.

## Decisions

### D1 — Criterio de fijación del tamaño muestral (rec. 9)

La evidencia disponible no permite justificar el `6,66 %` a priori: el texto
actual declara que ese margen «reproduce de manera exacta el corpus de 200 casos»,
lo que el dictamen marca como inversión de la lógica del muestreo. La alternativa
honesta y respaldada por los hechos es declarar la **disponibilidad operativa**: el
corpus quedó fijado en 200 casos por el relevamiento efectivamente cronometrado
(flujo manual junio-agosto 2026), y el `6,66 %` es la **precisión implicada** por
ese tamaño con `N ≈ 2.646`, `z = 1,96` y `p = 0,5` bajo corrección por finitud.

Regla de reformulación: se conserva la fórmula, los insumos y el resultado
(`n ≈ 200`); se invierte únicamente la secuencia narrativa —el tamaño se fija por
disponibilidad, el margen es su consecuencia—. La verificación aritmética del memo
sigue cumpliéndose (`n0 = 200 · 2645 / 2446 = 216,27`; `e = √(0,9604/216,27) ≈
0,06664`; `n = 216,27 / [1 + 215,27/2.646] ≈ 200,0`). Alternativa descartada:
justificar el margen a priori, porque no hay evidencia pre-registrada de un margen
previo y declararlo sería fabricar una decisión no tomada.

### D2 — Propagación de la dependencia etiquetadores/operadores

La dependencia ya está declarada en `04-marco-metodologico.tex` (subsección
población/muestra y amenazas a la validez). La regla es propagarla, sin duplicar el
argumento: (a) añadirla a la lista de limitaciones del estudio en
`08-discusion.tex` (`subsec:limitaciones-estudio`, hoy cinco limitaciones); (b) en
`09-conclusiones.tex`, acotar el párrafo de aportes empíricos. Se conserva la
referencia cruzada a `subsec:limitaciones-estudio` en lugar de reexplicar.

### D3 — Retiro del «riguroso» sin matizar (dimensión 7h)

`09-conclusiones.tex` califica la evidencia como «recolectada bajo un diseño
experimental riguroso con doble etiquetado independiente y prueba no paramétrica».
Regla: sustituir el calificativo por una formulación descriptiva que no afirme
independencia plena, p. ej. «bajo un diseño cuasiexperimental con muestras pareadas,
doble etiquetado y prueba no paramétrica, cuyos límites de independencia se declaran
en la \autoref{subsec:limitaciones-estudio}». No se elimina el reconocimiento del
doble etiquetado ni del kappa (`0,87`, «casi perfecto»).

### D4 — Presupuesto de páginas

El PDF actual tiene 104 páginas; el tope tras c-116 es ≤ 100 (dictamen, rec. 8 y
presupuesto). Este change MUST NOT aumentar el conteo: las adiciones a limitaciones
y conclusiones son una o dos oraciones; la reformulación del margen reemplaza texto
existente de longitud comparable. Si el conteo sube, se recorta la redacción a la
variante más corta antes de cerrar.

## Objetivos de propagación (ANTES → DESPUÉS)

| Sitio | ANTES (palabra clave) | DESPUÉS (regla) |
|---|---|---|
| `04:51` | «El margen del 6,66 % es ... el valor que reproduce de manera exacta el corpus de 200 casos» | Declarar que el tamaño se fijó por disponibilidad operativa; el `6,66 %` es la precisión implicada por `n = 200` con `N ≈ 2.646` |
| `08:38-48` | Lista de cinco limitaciones (sin la dependencia etiquetadores/operadores) | Agregar la dependencia como limitación acotada (una o dos oraciones) |
| `09:26` | «diseño experimental riguroso con doble etiquetado independiente» | Formulación descriptiva sin «riguroso», con remisión a las limitaciones y acotación del aporte empírico |

## Risks / Trade-offs

- **[Riesgo] El «riguroso» reaparece en otro capítulo.** Puede haber usos legítimos
  del término fuera de las conclusiones. → **Mitigación**: la verificación busca
  «riguros» en `09-conclusiones.tex`; no se prohíbe el término en todo el
  manuscrito, solo el sobreclaim sin matiz en las conclusiones.
- **[Riesgo] Contradicción con el requisito de reproducibilidad.** Declarar el
  tamaño por disponibilidad podría leerse como abandonar la fórmula. →
  **Mitigación**: se conservan fórmula, insumos y resultado; el requisito de
  reproducibilidad (n = 200 consistente con los insumos) se mantiene intacto.
- **[Riesgo] Presupuesto de páginas.** El plan exige ≤ 100; hoy 104. →
  **Mitigación**: D4; compilar y registrar el conteo; recortar si sube.
- **[Riesgo] Divergencia con el memo.** El memo §7.2 solo advierte el recálculo del
  margen, no el criterio a priori vs disponibilidad. → **Mitigación**: no se altera
  ningún valor canónico; el criterio de fijación es narrativa del capítulo, no un
  número nuevo.
- **[Riesgo] Reversibilidad.** D1 es reversible si el autor ratifica un margen
  pre-registrado; D2/D3 son reversibles si el jurado considera suficiente la
  declaración de la dimensión 6. → **Mitigación**: `git checkout` de los `.tex`.

## Migration Plan

1. Editar los tres `.tex` según la tabla ANTES → DESPUÉS (un solo pase por archivo).
2. Compilar con la imagen `texlive-thesis` y confirmar cero errores fatales y el
   conteo de páginas (no mayor que el actual).
3. Verificar por búsqueda que `09-conclusiones.tex` no conserve el «riguroso» sin
   matiz y que la limitación esté en `08` y `09`.
4. Revertir = `git checkout` de los `.tex` (ningún otro artefacto se toca).

## Open Questions

Ninguna que cambie las specs o el enfoque. Queda como verificación de implementación:
el comando de compilación con Docker debe correr desde
`docs/Tesis/v9 (IA)` con `-w /work/paper texlive-thesis latexmk main.tex`.
