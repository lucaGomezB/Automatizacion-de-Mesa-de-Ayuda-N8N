# Design: Atender las observaciones de la quinta instancia del tribunal

## Context

Ver `proposal.md` - Why. Estado verificado el 2026-11-25 sobre `main` (v1.6.4, 157 páginas, tag
`v1.6.4`). El dictamen de quinta instancia (APTA PARA DEFENSA, 7,3/10; proyectada 7,5) auditó la
v1.6.4 contra las correcciones de cuarta instancia (R-01 a R-07 y B-01, todas aplicadas) y emitió
siete observaciones nuevas (C-01 a C-07) que surgen de la información que el propio reencuadre puso a
la vista. A diferencia de c-249, aquí **las cinco compuertas de autores ya fueron respondidas**: los
hechos quedaron resueltos y el apply los CODIFICA, no los pregunta.

- **Mapa archivo→capítulo (obligatorio para este change).** El nombre del `.tex` NO coincide con el
  número del capítulo rendido: Ch4=`04-marco-metodologico.tex`, Ch7 (legal, reubicado por c-105)=
  `11-aspectos-legales.tex`, Ch8=`07-resultados.tex`, Ch9=`08-discusion.tex`, Ch10=
  `09-conclusiones.tex`, Anexos=`12-anexos.tex`. Toda remisión de tarea usa el nombre de archivo, y
  la prosa de la tesis usa el número de capítulo rendido.
- **Cifras canónicas (frozen) en `docs/Tesis/Correcciones/numeros-canonicos.md`.** Las medias por
  canal (87,25 s / 20,09 s teléfono; 56,52 / 27,65 correo; 28,68 / 1,88 formulario), las reducciones
  (76,98 % / 51,07 % / 93,44 %; global 71,16 %), la sección 3.8 con los tiempos por canal y el
  bloque de sensibilidad del redondeo manual (descuento fijo `5 s` → 56,585 s / 68,61 %; `10 s` →
  51,585 s / 65,57 %) son las fuentes de las cifras recomputadas de C-03. El script de análisis no
  cambia ningún valor `vigente`; agrega las lecturas que el dictamen pidió (sin telefonía) con su
  propia procedencia.
- **Cifras del dictamen que el script debe reproducir (o corregir).** C-03: correo+formulario
  ≈44,1 s → ≈16,2 s (≈63,3 %); mediana de grabación+procesamiento 18,7 s (en realidad `t_e2e_s`,
  18,698 s) frente a la grabación cruda `duracion_segundos` (mediana 7,0 s / media 7,26 s). Ambas son
  derivables de `data/corpus_resultados_telefonia.json` (81 registros con `duracion_segundos` y
  `t_e2e_s`), `data/corpus_resultados_web_correo.json` (119 registros), y
  `data/corpus_evaluacion_pseudonimizado.json` (canal + `tiempo_manual_s`).
- **El componente "~10 s" NO existe (C-02 resuelta).** El `tiempo_manual_s` del corpus es
  **clasificación manual (lectura + decisión de sector)**, no E2E. No hay columna de carga ni en el
  CSV ni en el JSON. La sensibilidad de redondeo del Anexo K (−10 s → 51,6 s / 65,6 %) es legítima y
  PERMANECE como **sensibilidad de redondeo**, NO como "quitar carga": los valores se redondearon
  ARRIBA a múltiplos de 5 s y el descuento explora ese redondeo. El apply no debe re-relatar Anexo K
  como "reducción sin componente de carga".
- **Cronología (C-01 resuelta).** La clasificación manual del corpus REAL ocurrió en OCTUBRE 2026.
  commits `68d06ec` (2026-06-11, corpus sintético) y `ea62576` (2026-10-09, corpus real versionado).
  El "junio–agosto" del texto es un artefacto de la era sintética y sale.
- **Estado del registro primario (C-04).** `data/README.md:35-51` confirma 118 filas en
  `corpus_resultados_web_correo.json` con R001 faltante; §4.5 (`04:66`,`:79`) y `12-anexos.tex:149`
  ya dicen 118/119 con registro versionado. Solo `07:38` la contradice. Redacción pura, sin datos.
- **Procedencia (C-06 resuelta).** El origen real es familiares y amigos (el círculo), no empleadores.
  Reencuadre de procedencia: retirar "integrantes del entorno operativo del propio equipo"; conservar
  el escenario ficticio y la "organización adoptante".
- **Precedentes.** c-249 es el template más cercano: compuertas, grupos gated vs. sin compuerta, TDD
  de prosa (ANTES/DESPUES con `rg`), script de análisis TDD real en `evaluation/data/campana/analisis/`,
  y release con tag anotado. c-250 reutiliza ese formato pero con las cinco compuertas ya RESUELTAS
  (no gated) y produce la versión de defensa `v1.6.5`.
- **Reglas vigentes que acotan el diseño.** La regla de tags quedó escrita por c-249 OQ-05
  (`tesis-document`, "Regla escrita de movimiento de tags de release"); `v1.6.4` aplicó la opción
  elegida y los tags anteriores son inmutables. El presupuesto de palabras del Resumen (250) y del
  Abstract (250) se conserva; el presupuesto de páginas (100) queda en el mismo estado de exceso
  declarado.

## Goals / Non-Goals

**Goals:**

- Que la línea base manual de la sub-hipótesis 1 se describa con honestidad: cronología referida al
  corpus vigente en **octubre 2026** (C-01), tiempo manual declarado **clasificación pura sin
  componente de carga** (C-02), y asimetría telefónica por brazo con lectura sin telefonía (C-03).
- Que el capítulo legal separe el consentimiento de colaboradores del de titulares, funde la licitud
  en la disociación (arts. 2 y 28), cite el deber de confidencialidad (art. 10), retire los
  "empleadores reales" y no declare custodio/destrucción de originales que no existen (C-05, C-06).
- Aplicar el reencuadre de procedencia (familiares y amigos), cerrar la consistencia (C-04, C-07) y
  publicar la versión de defensa `v1.6.5` con la misma trazabilidad de c-249.

**Non-Goals:**

- No inventar hechos de cronología, consentimiento, custodio, empleadores ni autoría; todo quedó
  decidido en las compuertas ya respondidas y se codifica tal cual.
- No cambiar cifras canónicas ni conclusiones sin ratificación; no editar casos del corpus ni sus
  JSON (el SHA-256 `1fd17d7e...` sigue protegido).
- No relatar el Anexo K como "remoción del componente de carga": es una sensibilidad de redondeo y
  permanece.
- No tocar `App/`, `n8n/` ni los artefactos existentes de `evaluation/`.
- No mover, borrar ni recrear `v1.6.2`, `v1.6.3` ni `v1.6.4`.

## Decisions

### D1 - ADDED sobre las capacidades existentes

Como c-249, los requisitos nuevos se AGREGAN a `tesis-reencuadre-cuarta-instancia` (contenido) y a
`tesis-document` (release). Alternativa descartada: MODIFIED sobre requisitos de c-249 — copiaría
bloques largos para cambiar una cláusula; aquí las observaciones son nuevas (quinta instancia) y no
contradicen los requisitos de cuarta instancia, los completan (y corrigen dos reencuadres previos:
la procedencia y el componente de carga).

### D2 - Cinco decisiones RESUELTAS OQ-01 a OQ-05, sin bloqueo pendiente

Las cinco compuertas de c-250 fueron respondidas por los autores. NO queda "ask the authors": el
apply codifica cada decisión. Las tres primeras afectan datos de procedencia/medición y las dos
últimas redacción. El agente MUST NOT inventar ningún hecho adicional; las decisiones ya resueltas
están registradas en la sección c-250 de `dictamen-correcciones.md` (tabla de decisiones con
respuesta literal, fecha y responsable). No hay "director aval" que gestionar: C-06 se disolvió.

### D3 - Cronología: la campaña del corpus vigente es octubre 2026 (RESUELTO — OQ-01)

La clasificación manual del corpus REAL ocurrió en **octubre 2026**. Evidencia fechada: commit
`68d06ec` (2026-06-11) versiona el corpus **sintético**; commit `ea62576` (2026-10-09) versiona el
corpus **real**. La ventana "junio–agosto" de `04:14`, `04:46`, Tabla 4 (`04:78`) y `01:16` es un
artefacto de la era sintética: se reemplaza por **octubre 2026**. La declaración honesta
("declaración de los autores sin registro fechado") se conserva. El 165,3 s del corpus sintético del
3 de julio queda solo en la Nota de versiones como histórico/retirado. §7.3 ya registra el retiro del
sintético el 11-09 y el versionado del vigente el 09-10 (`11-aspectos-legales.tex:34`), coherente
con esta decisión.

### D4 - Componente "~10 s" REMOVIDO, no declarado (RESUELTO — OQ-02)

El "~10 s de carga del ticket" no existe en los datos: el `tiempo_manual_s` es **clasificación manual
(lectura + decisión de sector)**, sin componente E2E ni de carga. Se retira la fórmula de `04:89`,
`04:131` (octava amenaza), `12:153`, `07-resultados.tex:285`, `01:18`, Resumen, Abstract, Tabla 10 y
Tabla 23, y `data/README.md`. La Tabla 3 (`04:31`) gana una definición operacional **por brazo**:
manual = clasificación (lectura + decisión); automatizado = E2E (recepción → persistencia). **Matiz
crítico:** el Anexo K (`12-anexos.tex:351,353,367`) ya computa −10 s → 51,6 s / 65,6 % como una
**sensibilidad de redondeo** (valores redondeados ARRIBA a múltiplos de 5 s). Esa sensibilidad es
legítima y PERMANECE; NO se re-relata como "remoción de carga". El script (D6) reproduce los pares de
la lectura sin telefonía, no "sin carga".

### D5 - Telefonía: dos constructos, dos lecturas (RESUELTO — OQ-05 en lo de redacción)

Se distingue la grabación cruda `duracion_segundos` (mediana 7,0 s / media 7,26 s) del `t_e2e_s`
(mediana 18,698 s, lo que el dictamen llama "mediana de grabación más procesamiento 18,7 s"). La
sexta amenaza se amplía con la asimetría de entrada (descripción completa leída en voz alta vs.
paráfrasis recitada con tope 45 s), sin confundir los dos constructos. Con el ~10 s removido, el
87,2 s manual es clasificación pura y el 20,09 s automatizado es E2E: la asimetría es aún más
fundamental (distinto alcance Y distinta entrada). La sub-hipótesis 1 se informa también sin telefonía
(correo+formulario ≈44,1 s → ≈16,2 s, ≈63,3 %), recomputada por pares con intervalo desde
`corpus_resultados_web_correo.json` + `corpus_evaluacion_pseudonimizado.json`.

### D6 - Script de análisis TDD aditivo, como c-249

`evaluation/data/campana/analisis/analisis_quinta_instancia_c250.py` con
`test_analisis_quinta_instancia_c250.py` escrito primero (Strict TDD). Sobre datos sintéticos
mínimos fija: (1) la desagregación sin telefonía (correo+formulario) y su intervalo de diferencia
pareada; (2) la reducción sin telefonía; (3) la mediana/media de `duracion_segundos` vs. `t_e2e_s` de
`corpus_resultados_telefonia.json`. Salidas `.json`, `.md` y `SHA256SUMS.txt`. La prosa toma las
cifras de esa salida; cualquier diferencia con el dictamen (≈44,1 s → ≈16,2 s / ≈63,3 %) se registra
en la sección c-250.

### D7 - Capítulo legal: separar, fundar por disociación, retirar originales y empleadores (RESUELTO)

Cuatro ejes (HIGH), todos con decisión ya tomada:

1. **Retirar la afirmación de originales con identificadores.** `11:18` y `data/README.md:55-63`: el
   corpus fue SIEMPRE genérico ("sistema principal"/"sistema secundario"), sin nombres de sistema ni
   ID USUARIO. No hay originales, no hay custodio ni fecha de destrucción que declarar.
2. **Separar consentimiento de colaboradores del de titulares.** Retirar `11:46` ("titulares y
   responsables son las mismas personas"). Los colaboradores son los autores + A1; los titulares son
   los reportantes del círculo.
3. **Fundar la licitud en la disociación citando arts. 2 y 28** (art. 28 es adición neta; hoy solo
   art. 2 en `11:12`). Definir la notificación: **verbal el 2026-09-30** (corrige el 01/10 actual),
   comunicando el uso pseudonimizado y disociado de los incidentes construidos a partir de sus
   descripciones.
4. **Retirar los "empleadores reales"** y "no se requirió autorización de esas organizaciones"
   (`11:18`); el origen es el círculo (familiares y amigos). Sin empleador, no hay aval del director
   que gestionar. Agregar el deber de confidencialidad (**art. 10**, Ley 25.326) a los principios
   generales (junto a la tríada CIA en `11:40`).

Las tareas del capítulo legal se muestran a los autores antes de escribir (gobernanza HIGH), pero ya
no quedan bloqueadas por compuerta abierta.

### D8 - Release v1.6.5 como versión de defensa

Bump `v1.6.4` → `v1.6.5` en portada, Anexo B, Nota de versiones, `.bib`, `README.md`,
`knowledge-base/` e inventario. La regla de tags ya escrita por c-249 OQ-05 rige para `v1.6.5`; el
Anexo B debe decir qué commit apunta el tag y qué hash imprime. Condición de release: visto bueno
escrito del director (condición del tribunal) y ninguna tarea de edición abierta. **No hay tarea de
"obtener aval del director" por C-06** (la gestión se disolvió). Registro: sección c-250 de
`dictamen-correcciones.md`, `CHANGES.md`, y respuestas de defensa (`docs/defensa/respuestas-tribunal.md`
y `respuestas-tribunal-cuarta-instancia.md`) para las 10 preguntas probables si las tocan.

### D9 - Verificación estilo prosa TDD y TDD real donde hay código

Cada tarea de edición corre un `rg` ANTES (muestra el defecto) y DESPUES (estado deseado),
registrados en la sección c-250 de `dictamen-correcciones.md`. Los números de línea son los de
v1.6.4; el apply los re-verifica porque las ediciones los desplazan. El script de D6 sigue
RED-GREEN-TRIANGULATE-REFACTOR con `pytest`. Patrones con `.` en lugar de vocales acentuadas.

### D10 - Reencuadre de procedencia (nuevo, conforme a C-06)

El régimen (a) de procedencia pasa a "los autores y las personas de su círculo (**familiares y
amigos**)". Se retira "integrantes del entorno operativo del propio equipo" de toda mención de
procedencia (`01:16`, `01:48`, `01:72`, `04:46`, `08:22`, `08:42`, `08:50`, `09:52`, `11:16`,
`11:46`, `11:54`, Resumen). Se CONSERVAN el escenario ficticio ("organización mediana del sector
servicios / 120 usuarios / 42 diarios", dispositivo de dimensionamiento explícitamente no-real por
R-01) y la "organización adoptante" (despliegue futuro). El reencuadre se registra en la Nota de
versiones como corrección de veracidad (estilo R-01 a R-07).

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| [El agente re-relata Anexo K como "remoción de carga" en vez de sensibilidad de redondeo] | D4: matiz escrito; verificación ANTES/DESPUES en la fila del descuento |
| [El agente re-declara custodio/destrucción de originales que no existen] | D7 eje 1: retirada explícita; `rg` residual sobre "custodi|destrucción" = 0 |
| [El agente conserva "integrantes del entorno operativo" en alguna mención de procedencia] | D10: barrido `rg` de la cadena en `S/`; ANTES 12×, DESPUES 0 |
| [Copiar cifras del dictamen en lugar de recomputarlas] | D6: script con prueba; la prosa cita la salida versionada; las diferencias se registran |
| [Confundir `duracion_segundos` con `t_e2e_s` en telefonía] | D5: dos constructos nombrados y medias/medianas separadas; verificación por `rg` |
| [El brazo manual sigue leyéndose como "hasta la persistencia del ticket"] | D4: definición operacional por brazo en Tabla 3; verificación ANTES/DESPUES |
| [Editar el capítulo legal o `data/README.md` sin revisión (HIGH)] | Texto propuesto mostrado a los autores antes de escribir |
| [Reintroducir "junio–agosto" como fecha de la campaña vigente] | D3: `rg` de la ventana; ANTES presente, DESPUES solo como histórico |
| [Repetir el desfasaje tag/PDF] | D8: regla de c-249 reutilizada; `git rev-parse v1.6.5^{commit}` comparado con el hash impreso |
| [Nombres reales o correspondencia alias-identidad en prosa nueva] | Solo alias (`A1`, `T1`, `E1`, `E2`, `O1`, `O2`); barrido final del diff |
| [Romper el hash del corpus] | Los JSON no se editan; `sha256sum` antes y después |

## Migration Plan

1. Registrar las cinco decisiones RESUELTAS (OQ-01 a OQ-05) con respuesta literal, fecha y
   responsable en la sección c-250 de `dictamen-correcciones.md` (tabla de decisiones; ya no hay
   compuertas pendientes ni presentación a los autores pendiente).
2. Script de análisis (D6), C-04 (redacción), y las tareas de C-02, C-03 y C-07, con ANTES/DESPUES
   por tarea.
3. Aplicar las tareas del capítulo legal (C-05, C-06) y de la procedencia (D10), con el texto
   propuesto mostrado a los autores antes de escribir (HIGH).
4. Coherencia: cifras canónicas; residuos (`rg` de fórmulas retiradas); `verify_citations.py`;
   `openspec validate --strict`.
5. Release `v1.6.5` (HIGH): bump, recompilación, derivados, tag según la regla de c-249, `CHANGES.md`,
   registro y respuestas de defensa. Sin tarea de aval del director (C-06 disuelto).

Rollback: hasta el paso 5 todo es prosa sin commit; se revierten los archivos tocados. El tag
`v1.6.5` no se publica hasta que el commit que lo recibe esté verificado y el director haya dado su
visto bueno escrito.

## Open Questions

Ninguna. Las cinco compuertas de c-250 quedaron **CERRADAS** por decisión de los autores. Se listan
aquí como registro del cierre (respuesta literal + fecha + responsable en la sección c-250):

- **OQ-01 — CERRADA (C-01).** La clasificación manual del corpus REAL ocurrió en **octubre 2026**, no
  junio–agosto. Evidencia: commits `68d06ec` (2026-06-11, sintético) y `ea62576` (2026-10-09, real).
  El 165,3 s del sintético queda solo como histórico en la Nota de versiones.
- **OQ-02 — CERRADA (C-02).** El valor de "carga de ticket" NO se declara: ese componente no existe.
  `tiempo_manual_s` = clasificación manual (lectura + decisión). Se retira el "~10 s"; la sensibilidad
  de redondeo de Anexo K permanece.
- **OQ-03 — CERRADA (C-05).** No hay originales con identificadores (ni custodio ni destrucción que
  declarar); el corpus fue siempre genérico. Notificación verbal el **2026-09-30** (no 01/10). Licitud
  por disociación (arts. 2 y 28).
- **OQ-04 — CERRADA (C-06).** No hay empleadores reales: el origen es familiares y amigos (el
  círculo). No hay aval del director que gestionar. Se agrega el deber de confidencialidad (art. 10).
- **OQ-05 — CERRADA (C-07).** No se usó IA en la redacción de las 119 descripciones; la atribución
  correcta de las reconstrucciones queda unificada; "en su domicilio" se aclara según la decisión de
  autoría registrada.