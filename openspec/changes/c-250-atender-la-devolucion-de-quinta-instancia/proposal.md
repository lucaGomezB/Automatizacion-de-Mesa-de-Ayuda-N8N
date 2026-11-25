# Proposal: Atender la devolucion de quinta instancia

## Why

La devolucion de quinta instancia del tribunal (25/11/2026) sobre `v1.6.4`
(`auditorias/Devolucion_Quinta_Instancia_TFI_v1.6.4_2026-11-25.pdf`, transcripta en el `.md`
homonimo) dicta **APTA PARA DEFENSA, 7,3/10** (cuarta instancia: 7,2; proyectada 7,5 si se
resuelven C-01 a C-04). R-01 a R-07 y B-01 quedan corregidas, pero el reencuadre puso a la vista
tres problemas de prioridad alta en la linea base manual de la sub-hipotesis 1, la unica que el
trabajo corrobora: la cronologia de la campana manual no se concilia con la version del 3 de julio
(C-01), el tiempo manual incluye un componente de carga estimado de magnitud no registrada que el
resto del texto lee como medicion de extremo a extremo (C-02) y, en telefonia, cada brazo proceso
una entrada distinta (C-03). Suma una contradiccion sobre el registro primario (C-04), dos
observaciones legales (C-05 consentimiento y licitud; C-06 empleadores) y siete ajustes de
coherencia (C-07). **Condicion para fijar fecha:** visto bueno escrito del director y version de
defensa con C-01 a C-04 incorporadas; C-05 a C-07 pueden ir en la misma version o exponerse en la
defensa. **Si C-01 no acredita que los 200 casos se cronometraron en el periodo declarado, el
tribunal revisa la calificacion del capitulo de resultados.** La devolucion recomienda ademas
preparar respuestas escritas a diez preguntas probables (seccion 6).

## What Changes

- **A. Hechos que solo conocen los autores, bloqueados por compuertas.** El agente MUST NOT
  inventarlos ni reconstruirlos; cada uno tiene dos ramas (evidencia o valor existe / no existe) y
  el texto de la rama (b) es el que el propio tribunal admite.
  - **OQ-01 (C-01, cronologia):** origen de los 165,3 s del 3 de julio (el repositorio muestra que
    nadie los cronometro: ver design, E1-E2), evidencia fechada de la campana junio-agosto
    (historial de la hoja original, metadatos del `.xlsx`), existencia de los originales y "en su
    domicilio". Rama (b): §4.2, §4.4, Tabla 4, §4.8 y la fuente del cronograma declaran la fecha
    como declaracion de los autores no verificable.
  - **OQ-02 (C-02, componente de carga):** valor exacto sumado, o como vario, y como se obtuvieron
    los cuatro tiempos de 10 s. Rama (c): magnitud desconocida declarada, "fijo" retirado y
    sensibilidad por pares para 5 y 10 s.
  - **OQ-03 (C-05):** que fue la "notificacion a los integrantes del grupo" del 01/10, que
    consentimiento dieron las personas del circulo, quien guarda los originales con
    identificadores y cuando se destruyen. **OQ-04 (C-06):** si los empleadores fueron informados
    y/o aval escrito del director. **OQ-05 (C-07):** si se uso un asistente de IA para reescribir
    las 119 descripciones del regimen (a).
- **B. Recomputo por pares con TDD estricto (C-02, C-03, C-04).** Script de solo lectura
  `analisis_quinta_instancia_c250.py` (prueba primero): reduccion de la media con y sin el
  componente (descuentos 5 y 10 s y, si OQ-02 lo da, el valor declarado), sin telefonia (119
  pares) y combinada, con IC bootstrap por pares (semilla `20261021`, `B = 2000`, convencion de
  c-207) y Wilcoxon; duracion de las 81 grabaciones frente a la lectura manual por par; conteo del
  registro primario de correo y formulario. Salidas con SHA-256 y seccion aditiva `3.49` de
  `numeros-canonicos.md`. Ninguna cifra del tribunal (51,6 s, 65,6 %, 44,1 s, 16,2 s, 63,3 %,
  "unos 77 s") se copia: la prosa cita la salida.
- **C. Prosa de C-02, C-03 y C-04.** Tabla 3 con definicion operacional por brazo; componente
  estimado en Resumen, Abstract, §1.2, §8.1, Tablas 10 y 23 (sin superar 250 palabras); Anexo K con
  la reduccion sin el componente; sexta amenaza ampliada; sub-hipotesis 1 informada tambien sin
  telefonia (rotulo ratificado por los autores, OQ-06); estado unico del registro primario.
- **D. Capitulo legal (HIGH, gated OQ-03/OQ-04).** Consentimiento de colaboradores separado del de
  titulares; retiro de "titulares y responsables son las mismas personas" y de la refutacion de
  v1.6.0 por el consentimiento del 02/10; licitud fundada en la disociacion (arts. 2 y 28, Ley
  25.326); custodia y destruccion de originales; empleadores y deber de confidencialidad (art. 10).
- **E. Coherencia C-07** (Tabla 26, I.3, "por los autores"/"por ese autor", Gemini 3.1 en §7.5,
  frase repetida 8 veces, "corpus propio de la organizacion", "en su domicilio").
- **F. Respuestas escritas a las diez preguntas** en
  `docs/Tesis/Correcciones/respuestas-tribunal-quinta-instancia.md`, cotejadas con
  `cotejar_cifras_respuestas.py`; transcripcion de la devolucion en `auditorias/`.
- **G. Release `v1.6.5` (version de defensa).** Nota de versiones I.1, recompilacion en Docker
  `texlive-thesis`, presupuesto de paginas declarado, regla A de tags, derivados, `CHANGES.md`,
  registro en `dictamen-correcciones.md`; **visto bueno escrito del director** como compuerta
  externa al repositorio antes de entregar la version al tribunal.

**BREAKING (afirmaciones del metodo, de los resultados y del capitulo legal):** el tiempo manual
deja de leerse como medicion de extremo a extremo; segun OQ-02 deja de llamarse "fijo" el
componente; segun OQ-01 la fecha de la campana puede pasar a declaracion no verificable; segun
OQ-06 puede cambiar el rotulo de la sub-hipotesis 1 en Tablas 10 y 23; el capitulo legal deja de
afirmar la identidad entre titulares y responsables del regimen (a).

Fuera de alcance: cifras canonicas vigentes (61,6 s, 17,76 s, 71,2 %, 73,5 %, `W = 363`, 87,2 s,
20,09 s, 77,0 %), que se conservan y se acompanan de las nuevas; el JSON del corpus (SHA-256
`1fd17d7e...`) y la hoja pseudonimizada; `App/`, `n8n/`; artefactos existentes de `evaluation/`
(solo se AGREGA el script con su prueba y sus salidas); mover, borrar o recrear `v1.6.4` u otro
tag; llamadas pagas.

**Gobernanza: MEDIUM** (prosa de la tesis, script de analisis aditivo). **HIGH**: el capitulo legal
(`11-aspectos-legales.tex`), `docs/seguridad/`, `data/README.md` (C-05, C-06) y el grupo de release
(toca el ejemplar de defensa y publica un tag): texto propuesto mostrado a los autores antes de
escribir y OK expreso antes de cada commit y del tag.

**Skills de dominio:** de `.agents/SKILLS.md` aplican `python-testing-patterns` y `python-testing`
al script del grupo 3. Las demas no corresponden (sin backend, frontend ni base de datos).

## Capabilities

### New Capabilities

- `tesis-quinta-instancia`: requisitos que cierran C-01 a C-07 de la devolucion de quinta
  instancia, las respuestas escritas a las diez preguntas, la transcripcion de la devolucion, la
  release de defensa `v1.6.5` con el visto bueno del director y el registro de compuertas de c-250.
  Sigue el precedente de c-246, que abrio `tesis-reencuadre-cuarta-instancia` para la cuarta.

### Modified Capabilities

- `tesis-reencuadre-cuarta-instancia`: MODIFIED de "Capitulo 7 reescrito sin base de empleador
  (R-05)" y de "Titularidad unica del regimen (a) y tensiones del repositorio explicadas (OQ-02 de
  c-249)", porque C-05 contradice su cuerpo: el primero funda la licitud del regimen (a) en el
  consentimiento del grupo y afirma que los titulares son los integrantes del grupo; el segundo
  exige declarar en §7.5 que titulares y responsables son las mismas personas.
- `tesis-numeros-canonicos`: ADDED del registro aditivo de la seccion `3.49` (recomputo de c-250).

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `auditorias/Devolucion_Quinta_Instancia_TFI_v1.6.4_2026-11-25.{pdf,md}` | Nuevo | Devolucion y su transcripcion (`pdftotext -layout`) |
| `docs/Tesis/v10 (IA)/paper/sections/00-resumen.tex` | Modificado | Componente estimado en Resumen y Abstract (<= 250 palabras) |
| `.../01-introduccion.tex` | Modificado | §1.2 (`:18`), frase repetida (`:16`, `:62`, `:72`, `:76`) |
| `.../04-marco-metodologico.tex` | Modificado (gated OQ-01, OQ-02) | §4.2 (`:16`), Tabla 3 (`:31`), §4.4 (`:46`), §4.5 (`:66`, `:79`, `:89`), §4.6 (`:97`), §4.8 (`:117`, `:127`, `:131`) |
| `.../07-resultados.tex` | Modificado | Tabla 10 (`:15-30`), §8.1 (`:36-90`, `:38`, `:74`) |
| `.../08-discusion.tex`, `09-conclusiones.tex` | Modificado | `08:22`, `08:50`; Tabla 23 (`09:15-30`), `09:48`, `09:52` |
| `.../11-aspectos-legales.tex` | Modificado (HIGH, gated OQ-03, OQ-04) | `:16`, `:18`, `:32`, `:46`, `:54` |
| `.../12-anexos.tex` | Modificado | I.1 (`:239-245`), Tabla 26 e I.3 (`:261-279`), Anexo K (`:345-378`) |
| `docs/diagrams/cronograma.md` (+ `cronograma.png` si cambia la leyenda) | Modificado (gated OQ-01) | Fuente de la barra "Campana manual" |
| `evaluation/data/campana/analisis/analisis_quinta_instancia_c250.{py,json,md,SHA256SUMS.txt}`, `test_analisis_quinta_instancia_c250.py` | Nuevo (aditivo) | Recomputo por pares de C-02, C-03 y C-04 |
| `docs/Tesis/Correcciones/numeros-canonicos.md` | Aditivo | Seccion `3.49` |
| `docs/Tesis/Correcciones/respuestas-tribunal-quinta-instancia.md` | Nuevo | Diez respuestas escritas |
| `docs/seguridad/` (acta T2, registro de actividades), `data/README.md` | Modificado (HIGH, gated OQ-03) | Custodia y destruccion de originales; notificacion del 01/10 |
| `docs/Tesis/v10 (IA)/paper/main.pdf`, `compilacion.md`, `tesis_para_agente.md`, `tesis_*.txt`, `docs/Tesis/tesis_ultima_version.pdf` | Regenerado | Release `v1.6.5` |
| `README.md`, `knowledge-base/`, `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md`, `CHANGES.md`, `docs/Tesis/Correcciones/dictamen-correcciones.md` | Modificado / aditivo | Version, registro del change, compuertas, ANTES/DESPUES, paginas |
