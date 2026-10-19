# Design: c-93 — Rigor metodológico del Capítulo 4

## Context

Ver `proposal.md` — Why. Estado confirmado contra el árbol de trabajo
(2026-10-19):

- §4.4 (`04-marco-metodologico.tex:43-45`) declara muestreo estratificado
  proporcional, «95 % de confianza», «6,5 % de margen» y «corrección por
  finitud», sin fórmula ni proporción esperada. El corpus declarado es 200.
- §4.5 (`04:51`) afirma cobertura unitaria «superior al 80 %»; §6.7
  (`06-implementacion.tex:83`) afirma «87 % … medida con pytest-cov 5.0.0».
  Ninguno publica el reporte ni el comando.
- §4.8 (`04:83`) reconoce el tamaño muestral (`n=200`) como amenaza a la validez
  de conclusión, sin análisis de potencia.
- §4.2 (`04:14`) y §4.8 (`04:77`) declaran «rotación de operadores entre las dos
  mitades del corpus» como mitigación.
- §4.4 (`04:47`) menciona «dos analistas con experiencia en la mesa de ayuda» sin
  nombrarlos ni declarar su relación con los autores; §4.5 (`04:53`) declara «dos
  operadores experimentados».
- §4.9 (`04:85-100`) describe Scrumban (seis iteraciones, roles, tablero Kanban).
- §1.6 (`01-introduccion.tex:46`), tercer criterio del umbral del 85 %: «reserva
  espacio estadístico para que el intervalo de confianza del estimador no solape
  la zona de rechazo de la hipótesis», confundiendo el contraste de tiempos de
  §1.4 con el umbral de exactitud.

Restricciones duras: solo documentación (NO tocar `App/**`); la tesis se compila
en Overleaf (sin toolchain LaTeX local); el corpus real
(`data/corpus_evaluacion_pseudonimizado.json`, `evaluation/report.md`) es la
fuente de verdad y no se altera. Coordinación: c-76 (T6 ventana, T7 instrumento),
c-77 (B1 `H1`, A7 universo trimestral).

## Goals / Non-Goals

**Goals:**

- Hacer reproducible el cálculo del tamaño muestral y publicar sus insumos.
- Respaldar o retirar las cifras de cobertura de pruebas.
- Añadir el análisis de potencia a priori.
- Tratar honestamente el confundido de la rotación de operadores.
- Declarar criterios de exclusión, analistas etiquetadores y demarcar el método.
- Reformular el criterio de exactitud de §1.6 sin «zona de rechazo».

**Non-Goals:**

- No redefinir la ventana temporal (c-76 T6) ni el instrumento manual (c-76 T7).
- No redefinir `H1` (c-77 B1) ni la aritmética del universo trimestral (c-77 A7).
- No re-medir la cobertura ni ejecutar la suite (solo publicar el comando/reporte
  existente o retraer la cifra).
- No tocar `App/**` ni los datos del corpus.

## Decisions

### D-A07 — Publicar la fórmula del tamaño muestral y reconciliar el margen

Se publica la fórmula clásica de muestreo aleatorio simple con corrección por
finitud:

`n = N · z² · p(1−p) / [ e² · (N−1) + z² · p(1−p) ]`

(o la variante equivalente `n = n0 / [1 + (n0−1)/N]` con `n0 = z²·p(1−p)/e²`),
declarando `N = 3.700`, `z = 1,96` (95 %), `p = 0,5` (proporción esperada
conservadora, ahora explícita) y `e`. **Verificación del implementador (tarea):**
recomputar con `python3` y publicar la salida. La auditoría reporta `n ≈ 219`
con `e = 6,5 %`; la verificación del implementador con la fórmula estándar de
corrección por finitud arroja `n ≈ 215`; en cualquier caso `n ≠ 200`. Para
reproducir `n = 200` el margen debe ser `e ≈ 6,7 %`. **Decisión:** publicar el
cálculo exacto con la salida de `python3` y corregir el margen declarado al valor
que reproduce 200 (o, alternativamente, corregir el tamaño declarado). Se
**prefiere** corregir el margen y conservar `n = 200`, porque el corpus ya está
construido con 200 casos y el resto del documento (y el corpus real) lo asume.
**Alternativa descartada:** conservar «6,5 %» y cambiar el tamaño a ~215 —
incompatible con el corpus existente y con c-76/c-77.

### D-A08 — Publicar el reporte de cobertura o retraer la cifra

`pytest --cov=app.routes --cov=app.services --cov=app.repositories --cov-report=term-missing`
es el comando canónico del proyecto (`AGENTS.md`). **Decisión:** publicar la cifra
de cobertura con su comando generador y el alcance medido (qué paquetes), y
unificar §4.5 y §6.7 en una sola cifra consistente. Si no puede adjuntarse el
reporte, retraer la cifra porcentual en ambos capítulos y describir la estrategia
de pruebas sin número. **Alternativa descartada:** mantener ambas cifras
(«>80 %» y «87 %») sin evidencia — es exactamente el defecto que la auditoría
señala.

### D-A09 — Análisis de potencia a priori

Se agrega un párrafo (en §4.8, junto a la amenaza de tamaño muestral, o en §4.7
como análisis estadístico) que declare: contraste principal (Wilcoxon pareado),
`α = 0,05`, potencia objetivo (0,80), tamaño del efecto asumido (o el mínimo
detectable) y el tamaño muestral `n = 200`, con la conclusión sobre suficiencia.
**Decisión:** calcular el efecto mínimo detectable a partir de `n = 200` y
`α = 0,05` (dos colas) con `python3`, y publicarlo. Debe usar el mismo `n = 200`
que §4.8 para no contradecir la amenaza. **Alternativa descartada:** afirmar
potencia sin cálculo — reproduce el defecto señalado.

### D-A10 — Reconocer el confundido de la rotación

Con dos operadores y dos mitades, asignar un operador distinto a cada mitad en
orden cruzado hace que «mitad del corpus» y «operador» sean colineales: la
rotación queda confundida con el efecto del operador y no aísla el efecto de
aprendizaje. **Decisión:** declarar el número de operadores (dos) y de mitades
(dos), reconocer el confundido y dejar de presentar la rotación como mitigación
no calificada; conservar el contrabalanceo del ORDEN (manual→auto vs.
auto→manual), que sí mitiga el efecto de orden, y declarar la limitación de que
el efecto de operador no es separable con este diseño. **Alternativa
descartada:** rediseñar la campaña (imposible: los datos ya están recogidos).

### D-M05 — Criterios de exclusión del corpus

Se declaran los criterios aplicados al construir el corpus: (a) duplicados
(mismo incidente reportado por más de un canal o repetido), (b) descripciones
vacías o insuficientes (sin contenido clasificable), (c) casos multicategoría
(pertenencia simultánea a más de un sector) y su tratamiento (exclusión,
desambiguación por consenso, o criterio de etiqueta primaria). **Coherencia
obligatoria:** §7.4 identifica descripciones cortas (7/16) y mezcla de
categorías (6/16) como patrones de error dominantes; si esos casos NO se
excluyeron, el texto MUST justificarlo (se conservan como casos límite legítimos
para medir el error del clasificador). **Decisión:** declarar que los casos
cortos y multicategoría se CONSERVARON por ser representativos del entorno real,
con criterio de etiqueta primaria, y que solo se excluyeron duplicados y
descripciones vacías. Esto es coherente con §7.4 y no invalida la tipología de
errores. **Alternativa descartada:** excluir descripciones cortas — contradice el
análisis de errores y reduciría la validez externa.

### D-M06 — Demarcar el método de investigación

Scrumban describe la construcción del artefacto, no el método de investigación.
**Decisión:** demarcar §4.9 con un rótulo explícito que la separe como «método de
construcción del artefacto» (no como metodología de investigación) y añadir una
oración en §4.1 o al inicio de §4.9 que distinga ambos planos. Se evalúa la
reubicación a Cap. 6 (Implementación), que ya describe las iteraciones
(`06:72`); **si** se reubica, §4.9 debe dejar un puntero y c-76/c-77 no deben
verse afectados. **Decisión preferida:** demarcar in situ (menor riesgo de
reescritura y de colisión con otros changes) y, si el autor lo pide, reubicar.
Esto NO duplica alcance de c-76 (que no toca §4.9).

### D-M07 — Declarar los analistas etiquetadores

Se declaran: cuántos analistas etiquetaron (dos), quiénes son (nombres o rol
genérico si hay anonimización), su independencia respecto de los autores, y si
alguno participó además como operador del brazo manual (dos operadores en §4.5).
**Decisión:** declarar explícitamente la relación. Si un analista es también
operador, declararlo y discutir la implicancia para la independencia del
`ground truth`. Si los analistas son los propios autores, declararlo como
limitación. La decisión concreta de nombres/roles la aporta el autor (ver Open
Questions). **Alternativa descartada:** omitir — es el defecto señalado.

### D-A03 — Reformular el criterio de exactitud de §1.6

El tercer criterio del umbral del 85 % (`01:46`) invoca «la zona de rechazo de la
hipótesis», que pertenece al contraste sobre la mediana de tiempos (`H0`/`H1`,
§1.4), no a la exactitud. **Decisión:** reformular el tercer criterio como
argumento de precisión del estimador: el margen por encima del 85 % reserva
espacio para que el límite inferior del intervalo de confianza (Wilson) de la
exactitud observada supere el umbral; se enuncia en términos de desempeño e
intervalo de confianza, no de zona de rechazo. **Coordinación:** c-77 B1
reformula `H1` (retira la comparación con el criterio humano y lo contrasta
contra el umbral ≥85 %); c-93 NO redefine `H1`, solo el criterio de §1.6. Debe
quedar consistente con la `H1` de c-77. **Alternativa descartada:** eliminar el
tercer criterio — se prefiere reformularlo porque el argumento de precisión es
válido y verificable (con el corpus real el IC Wilson de la exactitud es
[0,6698, 0,7913], que NO supera 0,85; ver Riesgos).

## Risks / Trade-offs

- **El IC real no supera el 85 %** (`evaluation/report.md`: exactitud 73,5 %,
  IC Wilson [0,6698, 0,7913]) → el criterio reformulado debe enunciarse como
  argumento de diseño del umbral, no como afirmación de que el IC observado
  supera 85 %. Mitigación: redactar el criterio como propiedad deseada del
  umbral (dejar margen sobre el límite), no como resultado; no introducir el
  IC observado en §1.6 (pertenece al Cap. 7, c-76).
- **`n ≠ 200` bajo los insumos declarados** → mitigación: publicar el cálculo y
  corregir el margen a `e ≈ 6,7 %` conservando `n = 200` (D-A07).
- **Tocar `.tex` sin compilador local** → mitigación: `rg` de control + revisión
  en Overleaf (tarea de recompilación) + `openspec validate --strict`.
- **Solapamiento con c-76/c-77** → mitigación: c-93 solo toca §4.2/4.4/4.5/4.8/4.9
  y §1.6 en los puntos metodológicos señalados; ventana (T6), instrumento (T7),
  `H1` (B1) y universo (A7) se referencian, no se redefinen.
- **Reubicación de §4.9** → riesgo de colisión con otros changes de tesis;
  mitigación: preferir demarcación in situ.
- **Falta de datos del autor** (nombres de analistas, `e` elegido) → mitigación:
  Open Questions; no bloquea la planificación.

## Migration Plan

1. Editar `04-marco-metodologico.tex` (§4.2, §4.4, §4.5, §4.8, §4.9).
2. Editar `01-introduccion.tex` (§1.6).
3. `rg` de control de las afirmaciones stale.
4. Recompilar en Overleaf; verificar PDF sin errores fatales.
5. Rollback: `git checkout --` / `git revert`.

## Open Questions

- **OQ1 (no bloqueante):** nombres/roles de los dos analistas etiquetadores y su
  relación con los autores (D-M07). Si el autor prefiere anonimizar, se usa rol
  genérico y se declara la independencia en términos funcionales.
- **OQ2 (no bloqueante):** valor de `e` a publicar (corregir a ≈6,7 % para
  conservar `n = 200`, vs. corregir `n`). Se prefija corregir `e` (D-A07).
- **OQ3 (no bloqueante):** demarcar §4.9 in situ vs. reubicar a Cap. 6. Se
  prefija demarcar in situ (D-M06).
