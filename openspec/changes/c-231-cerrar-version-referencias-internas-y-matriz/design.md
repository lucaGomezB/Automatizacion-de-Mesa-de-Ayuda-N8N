# Design: Cerrar la versión, las referencias internas y la matriz de trazabilidad

## Context

Tres defectos de cierre encontrados al auditar la tesis contra el último dictamen. El estado
vigente del repositorio y su evidencia:

- **Matriz de la devolución (Parte 1).** En `docs/Tesis/Correcciones/dictamen-correcciones.md`, la
  tabla de correcciones de la sección c-196 (`Rec | Observación | Corrección | Archivo | Estado`)
  marca `N-02`, `N-04` y `N-05` con «parcial: PENDIENTE (...)» e incluye `P16` en el inventario
  `PENDIENTE-AUTORES`. El commit `c5b2fb9` («resolver los pendientes de autores y remapear las
  citas de commits», 2026-11-11) cerró exactamente `N-02`, `N-04`, `N-05` y `P16` (lo declara su
  mensaje). El texto vigente lo confirma:
  - `N-02` (fecha de la versión de julio) → `12-anexos.tex:235` («La versión del 3 de julio de
    2026 ...»).
  - `N-04` (período y criterio de selección) → `04-marco-metodologico.tex:46` («muestreo no
    probabilístico por conveniencia»; período 16-06 a 10-09-2026).
  - `N-05` (registro primario de los 119 tiempos) → `04-marco-metodologico.tex:66` (registro
    versionado `data/corpus_resultados_web_correo.json`, 118 de 119).
  - `P16` (uso de modelos de lenguaje en la redacción) → `12-anexos.tex:241`.
- **Tag (Parte 2).** `git tag -l` da como máximo `v1.4.1`, que apunta a `2d8b0d5` (2026-11-14). Los
  commits `e7960e0`, `1f6a5ac`, `d3c13cd` y `1150d43` son POSTERIORES y no están contenidos en el
  tag. El Anexo B ya usa el patrón de consignación del hash (requisito 8273 y commit `1965e33`).
- **Referencias internas (Parte 3).** El memo `docs/Tesis/Correcciones/numeros-canonicos.md` no se
  anexa. Sus secciones citadas por el cuerpo: `3.31` (costo de la derivación errónea), `3.33`
  (balance neto), `3.35` (acotación del arbitraje por mayoría) y `3.36` (robustez de la brecha).

**Discrepancia verificada por el executor (importante).** La auditoría afirma «exactamente 6
ocurrencias» de `Sección 3.xx`, y todas usan el espacio normal (`Sección 3.xx`):
`01-introduccion.tex:48`, `04-marco-metodologico.tex:78`, `07-resultados.tex:393`,
`08-discusion.tex:56`, `08-discusion.tex:62`, `08-discusion.tex:125`. Una segunda búsqueda de la
forma con espacio duro (`Sección~3.xx`) encuentra **6 ocurrencias más**: `10-recomendaciones.tex:34`
(`3.31`), `08-discusion.tex:84` (`3.31` y `3.33`), `:114`, `:117` y `:121` (`3.33`). Total real:
**12**. El change DEBE cubrir las 12; dejar 6 sin repuntar reproduciría el defecto que motiva la
Parte 3. Se documenta la diferencia en lugar de copiar el conteo de la auditoría.

**Insumos de solo lectura.** `dictamen-correcciones.md` (sección c-196), `numeros-canonicos.md`
(secciones 3.31, 3.33, 3.35, 3.36), las secciones `*.tex` citadas y el historial de git
(`c5b2fb9`, `1965e33`, `2d8b0d5`, `1150d43`).

## Goals / Non-Goals

**Goals:**

- Alinear la matriz de la devolución con el estado real y el texto vigente, sin cifras nuevas.
- Publicar un tag que contenga la evidencia de c-223 a c-226 y el anexo nuevo, y repuntar todas las
  cadenas de versión.
- Anexar los números canónicos citados y dejar el cuerpo sin referencias internas por sección.

**Non-Goals:**

- Medir de nuevo, invocar a Gemini o tocar `App/`, `n8n/`, el clasificador, el corpus o las
  predicciones.
- Cambiar cualquier valor canónico vigente o el texto científico.
- Mover, recrear o reapuntar tags publicados ni crear el tag sin autorización del autor.

## Decisions

### D1 — Corrección de la matriz con evidencia verificable, sin afirmaciones nuevas

Se editan solo las celdas de estado de las filas `N-02`, `N-04` y `N-05` y se retira la fila `P16`
del inventario `PENDIENTE-AUTORES`. La corrección NO reescribe la observación ni la «Corrección»;
solo cambia «parcial: PENDIENTE (...)» por «cerrada (c5b2fb9, 2026-11-11)» y, en `N-16`, se
mantiene el estado ya vigente. El fragmento verificable que respalde cada fila es su archivo:línea
del texto vigente (arriba), de modo que `verificar_matriz_trazabilidad.py` pueda resolverlo. El
inventario `PENDIENTE-AUTORES` queda sin filas pendientes y lo declara.

Regla: el estado nuevo se prueba contra `git show c5b2fb9 -- <archivo>` y contra el `.tex` vigente,
nunca contra el conteo de la auditoría. Alternativa descartada: reescribir toda la sección c-196,
porque desborda el alcance de un change de cierre y arriesga tocar filas ya cerradas.

### D2 — Número de versión: `v1.5.0`

El tag debe contener evidencia NUEVA (las lecturas de c-224/c-225/c-226) y contenido NUEVO (el
anexo de números canónicos). Eso es un incremento menor, no una corrección dentro de la línea
`v1.4.x`:

- `v1.4.0`/`v1.4.1` fueron correcciones dentro de la línea `v1.4` (la última, c-222: recálculo del
  balance neto, una corrección).
- Este cierre AGREGA evidencia y un anexo al ejemplar. Un parche (`v1.4.2`) señalaría «solo
  corrección» y describiría mal el contenido; además, el defecto que se penaliza es justamente que
  la referencia verificable NO contenga la evidencia, y eso se resuelve con una versión que sí la
  contenga.
- Semántica elegida: `MAYOR` = reestructuración del manuscrito; `MENOR` = contenido/evidencia
  nuevo sobre la estructura vigente; `PARCHE` = corrección sin contenido nuevo. `v1.5.0` = MENOR.

**Alternativa descartada:** `v1.4.2` (parche), porque no refleja la adición de evidencia ni del
anexo. **Checkpoint de autores (OQ1):** el número es una decisión editorial y el tag es HIGH; se
confirma antes de crearlo.

### D3 — Creación del tag y consignación del hash (patrón de `1965e33` y requisito 8273)

Dos commits, como en cada release previa:

1. **C1 (commit de contenido, etiquetado).** Contiene la tesis final (anexo nuevo, remisiones
   repuntadas, versión `1.5.0`) y, en el Anexo B, la **oración de reemplazo** (SIN imprimir el hash
   de `v1.4.1` ni ningún hash previo): declara que el PDF compilado en el propio tag no imprime ese
   hash y que el commit siguiente lo consigna. El PDF etiquetado MUST NOT imprimir el hash de una
   release previa (requisito 8273).
2. **C2 (commit posterior al tag).** Reemplaza la oración de reemplazo por el hash completo de 40
   caracteres de C1, y no toca las fuentes.

El tag `v1.5.0` es ANOTADO sobre C1 y se publica en `origin` solo con autorización del autor
(precedente: el tag de archivo de c-223). `v1.4.1` y anteriores no se tocan.

### D4 — Desambiguación «versión entregada» vs «configuración entregada»

El Anexo B usa «versión entregada» para el tag del documento (`v1.4.1`, hoy) y «configuración
entregada» para el tag del software (`v1.3.0`), en `12-anexos.tex:58` frente a `:62`/`:72`. Se fija
la nomenclatura:

- **«Versión entregada» (`v1.5.0`)** = el documento de tesis entregado al jurado (el tag del
  manuscrito). Es el que rige la portada y la entrada bibliográfica.
- **«Configuración entregada» (`v1.3.0`)** = el software desplegado, que no cambia en este change.

Se agrega en el Anexo B una oración que declare ambas explícitamente para que la misma palabra no
designe dos objetos.

### D5 — Anexo de números canónicos citados y repunte de las referencias

Anexo nuevo en `12-anexos.tex`, **al final** (después de `sec:anexo-trazabilidad`), para no
renumerar los anexos A a I. Letra esperada: **Anexo J**; etiqueta `sec:anexo-numeros-canonicos`. El
content se RECORTA a los números que el cuerpo cita —los de las secciones `3.31`, `3.33`, `3.35` y
`3.36` del memo—, cada uno con:

| Campo | Contenido |
|---|---|
| Valor | La cifra canónica (por ejemplo, el costo medido `c = 69,51 s`, IC [33,42; 106,56]) |
| Procedencia | Archivo o comando que lo reproduce (por ejemplo, `evaluation/...`, `brazo_manual.csv`) |
| Estado | Uno de `{vigente, sensibilidad, reinterpretacion, condicional, retirado}` |

El anexo MUST NOT reproducir las secciones completas del memo, MUST NOT introducir valores ausentes
del memo y MUST NOT cambiar ningún valor. El memo se conserva como fuente interna de verdad y no se
retira del repositorio.

El repunte afecta las **12** ocurrencias de `Sección[~ ]3.xx` (D5 en Context): cada una pasa a
`(\autoref{sec:anexo-numeros-canonicos})`, sin cambiar la cifra ni el sentido de la oración. La
verificación de cierre busca `Sección[~ ]3\.[0-9]{2}` en `sections/*.tex` y exige cero coincidencias.

Alternativa descartada: nombrar el anexo con una letra intermedia (por ejemplo, después del Anexo
F), porque renumeraría las letras de los anexos siguientes y sus remisiones.

### D6 — Orden, gobernanza y frontera

1. Línea de base (`git status`, tags, `main.pdf`).
2. Parte 1 (matriz): MEDIUM, verificable con el script de la matriz.
3. Parte 3 (anexo y repunte): MEDIUM; requiere recompilar.
4. Parte 2 (tag): **HIGH**; se ejecuta al final, sobre el commit de contenido, con confirmación del
   autor.
5. Verificación de cierre y trazabilidad.

Sin cambios en `App/`, `n8n/`, el clasificador, la configuración, el corpus ni las predicciones.
Cero llamadas pagas.

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| El anexo crece en páginas | Recorte a los valores citados; registrar el delta en el libro mayor; el exceso ya está declarado y honrado |
| Quedan referencias internas sin repuntar | Recorrido con `rg "Sección[~ ]3\.[0-9]{2}"` sobre `sections/*.tex`, exigiendo 0 coincidencias; la tarea enumera las 12 |
| El tag no contiene la evidencia | El tag se crea sobre C1, que contiene los artefactos; verificación con `git show v1.5.0:` de cada ruta citada |
| Se imprime el hash de una release previa en el PDF del tag | C1 lleva la oración de reemplazo; C2 inserta el hash nuevo; `rg` del hash de `v1.4.1` sobre el PDF del tag |
| Repuntar la versión en un lugar y olvidar otro | Tarea única que recorre portada, Anexo B y `.bib`; `rg "1\.4\.1"` de cierre |
| Romper inmutabilidad de tags | Solo se crea un tag nuevo; `v1.4.1` y anteriores no se tocan |
| El patch `c5b2fb9` se cita mal | El fragmento se toma del `.tex` vigente y se contrasta con `git show c5b2fb9` |

## Migration Plan

1. Preparación y línea de base (grupo 0).
2. Parte 1: matriz (grupo 1).
3. Parte 3: anexo, repunte de las 12 remisiones, sección aditiva del memo, recompilación (grupo 2).
4. Parte 2: tag `v1.5.0`, repunte de versiones y consignación del hash (grupo 3), con autorización
   del autor.
5. Trazabilidad y verificaciones de cierre (grupo 4).

## Open Questions

- **OQ1 (autores, bloquea el grupo 3):** confirmar el número de versión `v1.5.0` (MENOR) frente a
  `v1.4.2` (PARCHE). Recomendación del design: `v1.5.0` (D2).
- **OQ2 (autores, opcional):** confirmar la letra del anexo nuevo (esperado «Anexo J», al final) y
  el crecimiento de páginas que el libro mayor registre.
- **OQ3 (autores, bloquea la publicación):** autorización expresa para crear y publicar el tag
  `v1.5.0` (gobernanza HIGH).
