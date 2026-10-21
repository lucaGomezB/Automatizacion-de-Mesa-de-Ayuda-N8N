## Context

Ver `proposal.md` — Why. Rama de corrección del dictamen CONEAU 2026-10-20
(dimensiones 2 y 3). Es consumidora del Gate 0 c-102
(`docs/Tesis/Correcciones/numeros-canonicos.md`) y del change c-107, que ya declaró
el estado parcial de la hipótesis principal y retiró el `9,5 %` de intervención
humana. No edita el memo canónico, `CHANGES.md` ni `dictamen-correcciones.md`; no
edita ningún `.tex` en la fase de propuesta.

Governance **ALTO**: las afirmaciones afectadas son la hipótesis y los objetivos
centrales de la tesis. Las decisiones editoriales se registran aquí y se declaran
reversibles. Fuente de verdad numérica (solo lectura): memo canónico, Secciones
3.1 a 3.6 y 7. Dictamen: dimensiones 2 (Hipótesis) y 3 (Objetivos).

Estado actual relevante:

- `01-introduccion.tex:32` formula la hipótesis principal combinando mecanismo
  ("reduce el tiempo y la intervención humana") con umbral de desempeño
  (`85 %`/`0,85`); sólo `01:34` tiene `H0`/`H1` operacionalizada sobre medianas.
- `01-introduccion.tex:40` formula el objetivo general como "Desarrollar e
  implementar".
- `01-introduccion.tex:46` mezcla, en el segundo objetivo, la implementación del
  clasificador con el umbral `85 %`/`0,85`.
- `01-introduccion.tex:52` usa "documentar exhaustivamente" (no falsable).
- No existe un objetivo específico de análisis de errores ni de calibración.
- `09-conclusiones.tex:6` ya declara el estado parcial; `09:8-18` (§Cumplimiento)
  no contiene una tabla de objetivos, cumplimiento y evidencia.
- `00-resumen.tex:13` declara el estado parcial (c-107).

## Goals / Non-Goals

**Goals:**

- Desdoblar la hipótesis principal en tres sub-hipótesis contrastables (tiempo;
  intervención humana; exactitud/F1), cada una con su contraste y su criterio de
  falsación.
- Declarar el estado por sub-hipótesis: confirmada en tiempo, refutada en
  clasificación, intervención humana no medida.
- Reformular el objetivo general como evaluación de viabilidad y desempeño.
- Separar en el segundo objetivo la implementación del umbral de desempeño.
- Reescribir el quinto objetivo en clave verificable y reproducible.
- Agregar un objetivo de análisis de errores y calibración de la confianza.
- Incorporar en las conclusiones la tabla de objetivos, cumplimiento y evidencia.
- Dejar la tesis compilando sin aumentar el conteo de páginas.

**Non-Goals:**

- No recalcular ni cambiar valores canónicos (`73,5 %`, `0,5207`, `71,2 %`,
  `W = 363`, `r = 0,9639`).
- No reintroducir valores `retirado` (`9,5 %`, `3.700`, `45,0 h`) ni el contraste
  de tiempos para justificar el umbral de clasificación.
- No editar el memo canónico, `CHANGES.md` ni `dictamen-correcciones.md`.
- No reducir páginas (eso es c-116, ejecutado después).
- No re-ejecutar el clasificador ni llamar a Gemini/N8N/Twilio.

## Decisions

### D1 — Desdoblamiento de la hipótesis principal en tres sub-hipótesis

La hipótesis principal (`01:32`) es una conjunción de mecanismo y umbral: como
conjunción es falsa y sólo la parte temporal tiene contraste operacionalizado. La
regla es desdoblarla en tres sub-hipótesis con contraste y falsación propios:

- **Tiempo (confirmada).** `H0: M_manual = M_auto`; `H1: M_manual > M_auto` sobre la
  mediana poblacional del tiempo de registro (contraste ya existente en `01:34`).
  Criterio de falsación: no rechazar `H0`. Resultado vigente: `W = 363`,
  `p = 3,08e-32`, `r = 0,9639`; `H0` rechazada.
- **Intervención humana (no medida).** Criterio de falsación declarado: la
  proporción de intervención humana por gate no ser inferior a la fracción
  esperada. El contraste NO se realiza: c-107 retiró el `9,5 %`, el gate
  implementado (`confianza < 0,70`) no dispara casos en el corpus y no existe
  registro primario de intervención por caso. Estado: **no medida**; el documento
  MUST NOT cuantificarla.
- **Exactitud/F1 (refutada).** Criterio de desempeño (no zona de rechazo):
  exactitud `≥ 85 %` y macro-F1 `≥ 0,85`, verificados contra el resultado observado
  y su intervalo de confianza de Wilson. Falsación: exactitud observada por debajo
  de `85 %` o intervalo de confianza que no supera el umbral. Resultado vigente:
  exactitud `73,5 %`, IC Wilson `[67,0 %; 79,1 %]`, macro-F1 `0,5207`; **refutada**.

Alternativa descartada: conservar la conjunción única, que el dictamen rechaza
explícitamente.

### D2 — Estado de la hipótesis por sub-hipótesis

El resumen y las conclusiones SHALL declarar el estado por sub-hipótesis
(confirmada en tiempo, refutada en clasificación, no medida en intervención) y
MUST NOT presentar la hipótesis principal como plenamente confirmada ni en bloque.
Esta decisión extiende el requisito vigente "Declaración del estado de la hipótesis
principal" sin contradecirlo, y la regla de c-107 (el `9,5 %` permanece retirado).

### D3 — Objetivo general como evaluación

El objetivo general (`01:40`) se reformula en términos de **evaluar** la viabilidad
y el desempeño de la automatización del registro inicial de incidentes; el
desarrollo e implementación del sistema se presenta como el **medio** para esa
evaluación, no como el objetivo. Alternativa descartada: conservar "desarrollar e
implementar", que sitúa el objetivo en clave de producto y no de investigación.

### D4 — Separación entre implementación y umbral en el segundo objetivo

En `01:46` se separan la acción (implementar el clasificador automático) del umbral
de desempeño (`85 %`/`0,85`). El umbral se traslada a **criterio de éxito
contingente** verificable contra el resultado observado y su intervalo de
confianza; su estado no alcanzado se declara en las conclusiones. Esto alinea el
objetivo con el requisito vigente "Criterio de exactitud sin zona de rechazo".

### D5 — Quinto objetivo verificable y reproducible

El quinto objetivo (`01:52`) se reescribe en clave reproducible: documentar la
arquitectura, los procedimientos de despliegue y los resultados de modo que una
tercera parte pueda replicarlos. Se elimina el calificador "exhaustivamente" y toda
formulación cuyo cumplimiento no admita verificación.

### D6 — Objetivo de análisis de errores y calibración de la confianza

Se agrega un objetivo específico referido al análisis de los errores de
clasificación y a la calibración de la confianza, alineado con los aportes del
Capítulo de resultados (tipología de tres patrones de error y bandas de confianza).
Debe ser verificable contra artefactos del repositorio (`evaluation/report.md`,
`07-resultados.tex`).

### D7 — Tabla de objetivos, cumplimiento y evidencia en las conclusiones

En `09-conclusiones.tex` (§Cumplimiento) se incorpora una tabla que enumera el
objetivo general y los específicos, su grado de cumplimiento y la evidencia
(sección o métrica). El segundo objetivo figura como **no alcanzado** y la tabla es
coherente con el estado parcial de la hipótesis. La tabla se mantiene compacta para
no comprometer el presupuesto de páginas.

### D8 — Regla dura de consistencia numérica (c-102/c-107)

Los capítulos editados SHALL citar únicamente valores `vigente` del memo
(`73,5 %`, `0,5207`, `71,2 %`, `W = 363`, `r = 0,9639`, IC Wilson `[67,0 %; 79,1 %]`)
y MUST NOT reintroducir valores `retirado` (`9,5 %`, `3.700`, `45,0 h`). No se
redefine ningún número; toda divergencia se resuelve en el memo, no en el capítulo.

### D9 — Secuencia con las demás ramas de tesis

Comparte `01-introduccion.tex` con c-113 (§1.7) y `09-conclusiones.tex` con las
ramas de tesis. Se aplica en secuencia, con un solo pase por archivo. **c-116
(reducción de páginas, tope `≤ 100`) se aplica DESPUÉS**; **c-111 (tag de la versión
evaluada) se cierra al final**.

### D10 — Verificación de compilación

La verificación usa la imagen local `texlive-thesis`:
`docker run --rm -v "<repo>/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis
latexmk main.tex`. No se edita el entorno. El PDF debe compilar sin errores fatales
ni referencias indefinidas; el conteo (hoy `104`) MUST NOT aumentar.

## Sitios a editar (ANTES → DESPUÉS)

| Sitio | ANTES (palabra clave) | DESPUÉS (regla) |
|---|---|---|
| `01:32` | Hipótesis principal = mecanismo + umbral ("reduce ... y ... alcanzando una exactitud ... 85 % ... F1 macro ... 0,85") | Tres sub-hipótesis con contraste y falsación propios (D1); no conjunción indivisible |
| `01:34` | `H0`/`H1` sobre medianas (tiempo) | Conservar como sub-hipótesis de tiempo; agregar la sub-hipótesis de exactitud/F1 con IC y la de intervención no medida |
| `01:40` | "Desarrollar e implementar un sistema ..." | "Evaluar la viabilidad y el desempeño de la automatización ...", con el desarrollo como medio |
| `01:46` | Segundo objetivo con implementar + umbral `85 %`/`0,85` | Separar la acción de implementar del umbral, que pasa a criterio de éxito contingente |
| `01:52` | Quinto objetivo "documentar exhaustivamente" | Objetivo reproducible, sin "exhaustivamente" |
| `01` (nuevo) | (ausente) | Objetivo específico de análisis de errores y calibración |
| `00:13` | Estado parcial (c-107) | Declarar estado por sub-hipótesis; sin `9,5 %` |
| `09:6` | Estado parcial declarado | Estado por sub-hipótesis (tiempo / clasificación / intervención) |
| `09:8-18` | §Cumplimiento sin tabla | Tabla de objetivos, cumplimiento y evidencia; obj. 2 no alcanzado |

## Risks / Trade-offs

- **[Riesgo] Reintroducir el `9,5 %` o el contraste de tiempos en la sub-hipótesis
  de clasificación.** → **Mitigación**: sub-hipótesis de intervención declarada no
  medida (D1/D2); umbral como criterio de desempeño, no zona de rechazo (D4).
- **[Riesgo] Colisión de líneas con c-113/c-115/c-116.** → **Mitigación**: aplicar
  en secuencia; este change limitado a §1.4-§1.6 de `01` y a `09`; c-116 al final.
- **[Riesgo] Crecimiento del conteo de páginas por la tabla y las sub-hipótesis.**
  → **Mitigación**: redacción de longitud neutra; verificar el conteo tras compilar;
  c-116 ejecuta la reducción a `≤ 100`.
- **[Riesgo] El estado "no medida" de la intervención puede leerse como laguna.** →
  **Mitigación**: declarar el criterio de falsación y la ausencia de registro
  primario; remitir a las limitaciones y a c-107.
- **[Riesgo] Reversibilidad.** D1/D3/D4 son reversibles; D8 es una corrección de
  exactitud (no reversible). → **Mitigación**: `git checkout` de los `.tex`; el memo
  se actualiza (upsert) si aparece evidencia nueva.

## Migration Plan

1. Editar `01-introduccion.tex` (§1.4 hipótesis, §1.5-§1.6 objetivos),
   `00-resumen.tex` (estado) y `09-conclusiones.tex` (estado y tabla), un solo pase
   por archivo.
2. Compilar con `texlive-thesis` y confirmar cero errores fatales, cero referencias
   indefinidas y conteo no mayor que `104`.
3. Verificar por búsqueda que no reaparecen `9,5 %`, `3.700` ni `45,0 h` como
   resultado, que el objetivo general no dice "desarrollar e implementar", que el
   quinto no dice "exhaustivamente" y que el objetivo 2 figura como no alcanzado.
4. Revertir = `git checkout` de los `.tex` (ningún otro artefacto se toca).

## Open Questions

Ninguna que condicione specs, enfoque o tareas. Punto abierto de redacción: el
umbral de desempeño puede reportarse con el macro-F1 de cinco clases (`0,5207`,
vigente e informativo) o con el de cuatro clases estimables (`0,6508`, condicional
en el memo §3.2); se conserva el `0,5207` citado por c-107 y se declara la salvedad
de la clase no estimable. Esto no altera el desdoblamiento ni el estado refutado.
