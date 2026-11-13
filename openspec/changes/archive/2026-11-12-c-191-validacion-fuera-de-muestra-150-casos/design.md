# Design: Validación fuera de muestra sobre 150 casos con el clasificador congelado

## Context

Ver `proposal.md` — Why. El dictamen CONEAU del 2026-11-09 deja como único dock de rúbrica
pendiente la "validación fuera de muestra no realizada" (criterio 4). La tesis la declara no
realizada en `07-resultados.tex` (`paragraph{Validación fuera de muestra.}`), `08-discusion.tex`
(`subsec:interpretacion-resultados`, `subsec:limitaciones-estudio`) y `10-recomendaciones.tex`
(`subsec:corpus-independiente`). El repositorio ya tiene los instrumentos (c-166 y c-168):
`evaluation/no_solape.py::verificar_no_solape`, `evaluation/doble_etiquetado.py`,
`evaluation/data/plantilla_etiquetado.csv`, `evaluation/run_evaluation.py` con `--corpus`,
`--predicciones`, `--reporte` y `--confirm-paid`, y `evaluation/campana.py::evaluar_fuera_de_muestra`.

Verificaciones ya hechas al proponer (solo lectura):

- `evaluation/kappa.py::parear_doble_etiquetado` acepta DOS alias `E<n>` cualesquiera
  (ordenados alfabéticamente), de modo que `E3`/`E4` funcionan con
  `construir_referencia("consenso_doble_etiquetado", ...)` sin cambiar código.
- `evaluation/doble_etiquetado.py` valida el alias con `re.compile(r"E\d+")`: `E3` y `E4` son
  válidos; la regla (a) exige exactamente dos `id_etiquetador` distintos.
- `construir_referencia` calcula el conjunto de verdad laxo como el sector consensuado más la
  INTERSECCIÓN de los adicionales de ambos etiquetadores, y marca los discordantes con
  `ADVERTENCIA_SESGO_DISCORDANTES`. Es exactamente la referencia que este change necesita.
- `evaluar_fuera_de_muestra` re-ejecuta `verificar_no_solape` y exige el cache independiente
  con `commit` y `pines`; no invoca Gemini. La corrida paga la hace `run_evaluation.py`.

## Goals / Non-Goals

**Goals:**

- Medir la exactitud del clasificador CONGELADO sobre casos que no vio, con la misma
  pseudonimización y el mismo doble etiquetado, sin recalibrar.
- Declarar el n efectivo, el sesgo de exclusión y el IC del resultado.
- Actualizar la tesis de "no realizada" a "realizada" con el resultado y sus límites.
- Cerrar el residual de atribución a Galup (2009) en 2.1 y 1.2.
- Versionar los artefactos con SHA-256 y registrar el protocolo.

**Non-Goals:**

- Medir el brazo manual o involucrar a los operadores `O1`/`O2` (ya resuelto por el dictamen A4).
- Estimar el efecto de orden o cronometrar las reasignaciones.
- Cambiar el clasificador, recalibrar tau/prompt/vocabulario, o editar código o datos de
  `App/`, `n8n/` y `analisis/`.
- Agregar código nuevo: se reutilizan el runner y el análisis existentes.

## Decisions

### D0 — Alcance: solo la validación de clasificación del clasificador congelado

La campaña mide SOLO la clasificación del clasificador congelado. No hay brazo manual ni
operadores. Alternativa descartada: re-medir el brazo manual; el dictamen A4 ya aceptó 125/151
y la sub-hipótesis 2 se resolvió en c-190, de modo que re-medirla reabriría un punto cerrado.

### D1 — Tamaño y n efectivo: 150 casos, ~104 con consenso, ~46 excluidos

150 casos nuevos (`I001..I150`). Con el acuerdo reciente entre etiquetadores (~69 %), se
esperan ~104 casos con consenso (`E3` = `E4`) y ~46 discordantes excluidos. El IC de Wilson de
la exactitud estricta sobre el n efectivo tiene un semi-ancho de ~8,4 puntos porcentuales. Se
ACEPTA este ancho: la validación cierra un dock cualitativo ("no realizada"), no reemplaza el
umbral del 85 %. Alternativa descartada: aumentar a 300 casos; duplica el costo de campo sin
reducir el sesgo de exclusión, que depende del acuerdo, no del tamaño.

### D2 — Estratos de muestreo — DECISIÓN DE LOS AUTORES (RESUELTA, 2026-11-09)

Muestreo estratificado por canal (correo, formulario web, telefonía) y por sector, con
sobremuestreo de la clase minoritaria (`Bases de Datos`, n=1 en el corpus de 200) y
ponderación de las estimaciones globales por la distribución del universo, como recomienda la
tesis 10.2. Cuotas DEFINIDAS por los autores (opción A: sostiene el canal más difícil, aunque
cueste más registro de llamadas):

| Canal | Cuota | Criterio |
|-------|-------|----------|
| Correo | 50 | Mantiene el canal más numeroso del corpus de 200 |
| Formulario web | 40 | El más fácil de recolectar, pero el menos informativo |
| Telefonía | 60 | Canal con peor exactitud (0,654) y peor acuerdo (0,617): concentrar casos aquí sostiene la estimación que más importa |

Esta composición es casi proporcional a la del corpus de 200 (correo 50/150 = 33,3 % vs
66/200 = 33,0 %; web 40/150 = 26,7 % vs 53/200 = 26,5 %; telefonía 60/150 = 40,0 % vs
81/200 = 40,5 %), de modo que la exactitud global sin ponderar (~0,735) coincide con la
ponderada y el sesgo de composición es despreciable. Aun así, el análisis (tarea 5.2) SHALL
reportar ambas (la ponderada por la composición del corpus de 200, o por la mezcla operativa
declarada) y SHALL declarar la composición en la tesis y en el README. Con el acuerdo por canal
observado, el consenso esperado es ~36 correo, ~30 web y ~37 telefonía; la global ponderada
tiene un semiancho de ~8,5 puntos y la estimación de telefonía ~14,7.

Dentro de cada canal, cuota mínima por sector para estimar las cinco clases, con
sobremuestreo explícito de `Bases de Datos` (objetivo ≥ 10 casos frente a 1 en el corpus de
200). Alternativa descartada: muestreo proporcional puro; dejaría `Bases de Datos` sin soporte
inferencial, que es justamente el defecto que la tesis 10.2 señala.

### D3 — Etiquetadores `E3` y `E4` y registro de sujetos

Dos etiquetadores nuevos, alias `E3` y `E4`, distintos entre sí y de `A1` (analista original),
`T1`-`T3` (autores) y `O1`/`O2` (operadores). Se agregan dos filas a
`evaluation/data/campana/registro_sujetos.csv` con `rol = etiquetador` y códigos `P<n>` nuevos
(distintos de `P1`-`P8`). La correspondencia alias-identidad NO entra al repositorio (custodia
del director). Alternativa descartada: reutilizar `E1`/`E2`; serían los mismos analistas que
fijaron el consenso original y violarían la independencia.

### D4 — No solape: reuso de `verificar_no_solape`

El corpus final se contrasta con `data/corpus_evaluacion_pseudonimizado.json` mediante
`verificar_no_solape` (prefijo `I`, ids y descripciones normalizadas disjuntas, advertencias
Jaccard revisadas a mano). El runner repite el control como paso previo obligatorio. Límite
declarado: el control no detecta paráfrasis.

### D5 — Clasificador congelado y runner reutilizado

`classifier_version = hybrid-v3`, commit `bf5e099`. Control `git diff bf5e099 HEAD` sobre
`App/Backend/app/classifiers`, `docs/prompt_gemini.txt`, `App/Backend/app/constants.py` y
`App/Backend/app/config/settings.py` (solo se admiten diferencias ajenas a la clasificación).
Se corre `python -m evaluation.run_evaluation --corpus ... --predicciones ... --reporte ...
--confirm-paid`. Prohibido recalibrar después de ver el corpus. No se agrega código salvo lo
estrictamente necesario.

### D6 — Referencia por consenso y métricas

Referencia = `consenso_doble_etiquetado` de `E3`/`E4` sobre `sector_etiquetado`; conjunto laxo
= sector consensuado más la intersección de adicionales. Los discordantes se excluyen y se
informan. Métricas: exactitud estricta y laxa sobre el n efectivo con IC de Wilson, desglose por
etapa de la cascada (vía `evaluar_fuera_de_muestra`) y por canal; las globales con y sin
ponderación (D2). Alternativa descartada: resolver discordancias por consenso a posteriori; el
protocolo lo prohíbe (sesga el kappa y la referencia).

### D7 — Artefactos a versionar y SHA-256

En `evaluation/data/campana/`: `corpus_independiente.json` (JSON final pseudonimizado con la
referencia acordada), `doble_etiquetado_independiente.csv` (tabla primaria del doble etiquetado
independiente), `registro_sujetos.csv` (actualizado con `E3`/`E4`),
`predicciones_independiente.json`, `reporte_independiente.md`, las salidas de análisis y el
`README.md` con el SHA-256 de cada archivo, el resultado del control de congelamiento y el
commit. Los artefactos de la v9 quedan intactos (`git status` sin cambios en el corpus, los
resultados y `evaluation/report.md`).

### D8 — Residual Galup (2009) — aplicable de inmediato, no depende del campo

En 2.1 la definición de ITSM se enuncia como definición general de la disciplina y Galup2009 se
cita con `\parencite{Galup2009_itsm}` como panorama del campo, sin atribuirle una afirmación
específica. En 1.2 se retira "de Galup" y la caracterización queda general. Galup2009 se
conserva en `Bibliography_base.bib`. Esta tarea NO depende de la campaña y el orquestador puede
aplicarla de inmediato.

### D9 — Release y archivo

Release `v1.3.0`: commit de contenido con el dictamen versionado y las fuentes actualizadas,
tag anotado y commit siguiente que consigna el hash. Archivo del change en
`openspec/changes/archive/2026-MM-DD-c-191-...`. `engram sync --project` antes del push.

## Risks / Trade-offs

- [Acuerdo `E3`/`E4` ~69 % deja ~46 casos excluidos] → se declara el n efectivo y el sesgo de
  exclusión junto al resultado; el IC (~8,4 pts) se acepta y se informa.
- [No se consiguen etiquetadores nuevos] → `estado_cegado: limitacion_declarada` en el README;
  el resultado se reporta como limitación y NO como etiquetado ciego.
- [Deriva del clasificador respecto de `bf5e099`] → control `git diff` antes de clasificar; si
  cambió, se detiene y se reporta; no se mide fuera de muestra con un clasificador distinto.
- [Sobremuestreo desbalancea el global] → se informan las métricas globales con y sin
  ponderación por la distribución del universo.
- [Sobreinterpretar el resultado como confirmación] → el texto reporta el IC, el n efectivo y
  la exclusión; no extrapola ni afirma confirmación fuerte.
- [Gitleaks marca prosa con nombres de archivo] → en el registro y el Anexo I se usa
  "sección N (`archivo.tex`)".

## Migration Plan

Apply en el orden de `tasks.md`. El residual Galup (D8) y las actualizaciones de registro se
pueden aplicar de inmediato; el resto depende del trabajo de campo (recolección, doble
etiquetado, corrida paga), que los autores hacen fuera del repositorio. La compilación de la
tesis usa el entorno de registro y `verify_citations.py`. Release (orquestador): rama
`change/c-191-validacion-fuera-de-muestra-150-casos`, commit de contenido, tag `v1.3.0`,
commit del hash, `engram sync --project`, PR contra `main`. Rollback: revertir las fuentes
`.tex`, los memos y los artefactos nuevos de `evaluation/data/campana/`; el tag se elimina si
no se publicó. No hay datos ni código productivo que revertir.

## Open Questions

- **D2 — Estratos**: RESUELTA el 2026-11-09 (opción A): **50 correo / 40 web / 60 telefonía**
  (150 total), con sobremuestreo de `Bases de Datos` y ponderación obligatoria de la exactitud
  global. La decisión se registra en el runbook antes de reunir el corpus (grupo 1).
- **D3 — Etiquetadores**: quiénes son `E3` y `E4` y sus códigos `P<n>` (los asigna el director
  fuera del repositorio). Bloquea el grupo 2.
- **Resumen/abstract**: si el resultado amerita modificar el veredicto de la sub-hipótesis de
  clasificación (tarea 6.x). Se decide al ver el resultado.
