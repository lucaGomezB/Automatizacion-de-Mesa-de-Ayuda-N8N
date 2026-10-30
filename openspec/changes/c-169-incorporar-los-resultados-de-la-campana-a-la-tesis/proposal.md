# Proposal: Incorporar los resultados de la campaña a la tesis

> **Estado: GATEADO.** Este change no se aplica hasta que c-165, c-166, c-167 y c-168
> estén archivados y la campaña de medición haya corrido y dejado sus salidas
> versionadas (tarea 0 de `tasks.md`). Las enmiendas pre-apply de 2026-10-30 resuelven
> los bloqueantes de `docs/campana-medicion/revision-pre-apply-c-165-a-c-169.md`
> (sección c-169 y transversales T1 a T4).

## Why

El dictamen CONEAU sobre la v1.2.5 (`auditorias/Dictamen_Tesis_v10_v1.2.5_CONEAU_2026-10-28.md`)
dejó abiertos cinco ítems que la tesis hoy declara no medidos, no contrastados o no
computables. En este change se denominan así, de forma literal:

- **(a) Exactitud del brazo manual**: exactitud estricta y laxa de la derivación del
  operador humano frente a una referencia producida por personas distintas de los
  operadores, con su contraste frente al brazo automatizado.
- **(b) Intervención humana real**: proporción de casos del flujo automatizado con
  acción manual de un operador (y proporción del tiempo del proceso), registrada por
  caso, que contrasta la segunda sub-hipótesis contra la cota `0,15` (compatible,
  refutada o no concluyente según la estimación y el intervalo de Wilson).
- **(c) Efecto de orden**: efecto del orden de condición (qué brazo se procesa primero
  por caso) y de la posición del caso en la secuencia sobre el tiempo del operador.
- **(d) Validación fuera de muestra**: métricas del clasificador congelado sobre un
  corpus independiente, sin solape con los 200 casos de ajuste.
- **(e) IC del kappa**: incertidumbre del acuerdo inter-evaluador del doble etiquetado.

La campaña 2026-10 (flujo manual de junio a agosto y automatizado de septiembre a
octubre de 2026, que sostiene los valores canónicos vigentes) tuvo además una
limitación estructural: los dos analistas que fijaron la referencia fueron los mismos
que operaron el brazo manual (`04-marco-metodologico.tex:55`, `:85`;
`08-discusion.tex:54`, "Sexto"). La campaña de medición del programa c-165 a c-168 la
resuelve con sujetos independientes: etiquetadores `E1`/`E2` y operadores `O1`/`O2`,
distintos entre sí, de los analistas originales y de los autores (o declara el solape
si lo hubo). Este change propaga sus resultados al documento, con desenlace positivo
o negativo declarado para cada ítem. Es solo documentación: la campaña corre fuera
del repositorio y el análisis lo produce c-167.

## What Changes

Secciones verificadas contra `main.toc` y los `\subsection` del `.tex` (2026-10-30):

- **Marco metodológico (Sección 4)**: 4.2 diseño (`04:12-16`, el contrabalanceo de
  `04:14` y la denominación distintiva de la campaña); 4.3 `tab:variables`
  (`04:25`, fila de intervención en `04:34`); 4.4 población y muestra (`04:43-55`:
  doble etiquetado nuevo y etiquetadores en `04:55`); 4.5 protocolo (`04:57-63`:
  plan de campaña, brazo manual con `O1`/`O2`, instrumentación de intervención); 4.6
  métricas e instrumentos (`04:65-69`: retirar "no se midió" de `04:67`); 4.7 análisis
  estadístico (`04:71-77`: IC del kappa, Wilson, bootstrap, McNemar, efecto de orden);
  4.8 amenazas (`04:79-89`: primera y segunda amenaza en `04:83` y `04:85`).
- **Introducción**: `01-introduccion.tex:34` (estado de la segunda sub-hipótesis).
- **Resumen y abstract**: `00-resumen.tex:11`, `:13`, `:27`, `:29` (y `:15`/`:31`
  si cambia el balance neto), con recorte previsto para el tope de 250 palabras.
- **Resultados (Sección 8)**: `07-resultados.tex:6` ("seis apartados"), `:157-161`
  (`subsec:reduccion-intervencion`) y una subsección nueva
  `subsec:resultados-campana-medicion` (kappa con IC, exactitud manual, intervención,
  orden, fuera de muestra).
- **Discusión (Sección 9)**: `08-discusion.tex:20` (corpus independiente), `:22`
  (efecto de orden), `:42` ("ocho limitaciones"), `:54` ("Sexto"), `:56`
  ("Séptimo"), `:58` ("Octavo"), `:70-97` (balance neto y `tab:balance-neto`, `:97`).
- **Conclusiones (Sección 10)**: `09-conclusiones.tex` completo (`:6`, `:22-28`
  `tab:cumplimiento-objetivos`, `:39-41`).
- **Recomendaciones (Sección 11)**: `10-recomendaciones.tex:6`, `:16-18`
  (`subsec:medicion-intervencion`), `:42-44` (`subsec:corpus-independiente`), `:46-48`
  (`subsec:estudios-replicacion`).
- **Aspectos legales (Sección 7)**: `11-aspectos-legales.tex:32` (protocolo y sujetos
  de la campaña de medición, sin datos personales).
- **Anexos**: Anexo B `tab:configuracion-evaluada-entregada` (`12-anexos.tex:38`,
  tercera columna: la configuración de la campaña de medición, con c-165 aplicado);
  Anexo A y `fig:cronograma` (`12-anexos.tex:14`, `:23`) con
  `docs/diagrams/cronograma.md`; Anexo I `tab:anexo-trazabilidad-2810`.
- **Memo y registro**: `docs/Tesis/Correcciones/numeros-canonicos.md` (sección `3.N`
  nueva; la entrada "no computable" del kappa en `:198-209` se cierra con nota) y
  `docs/Tesis/Correcciones/dictamen-correcciones.md` (sección del change).
- **Release**: PDF, renders, referencias de versión, bibliografía
  (`Gomez2026_repositorio`) y `CHANGES.md` al archivar.

**Kappa (decisión D-kappa).** El `0,87` se conserva como valor histórico de la campaña
2026-10, sin IC (tabla primaria no conservada); el kappa nuevo se reporta como valor
distinto, "fiabilidad del doble etiquetado de la campaña de medición", con su IC y su
propio rótulo de Landis y Koch. Nada en la tesis puede decir que el `0,87` tiene IC.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: diecinueve requisitos modificados con desenlaces condicionales
  (dos de ellos renombrados antes, porque sus nombres afirmaban "no medida"), uno
  removido (rótulo fijo de
  la sub-hipótesis) y seis agregados (subsección de resultados de la campaña,
  exactitud manual, intervención, efecto de orden, fuera de muestra y cierre
  verificable de los ítems (a)-(e)).
- `tesis-numeros-canonicos`: modificados el requisito de incertidumbre del kappa y el
  de la regla del gate (fuente primaria de la campaña); agregados el registro de los
  valores de la campaña con procedencia por valor y la invariancia de los valores
  canónicos vigentes.

## Impact

- `docs/Tesis/v10 (IA)/` (00, 01, 04, 07, 08, 09, 10, 11, 12, bibliografía, PDF y
  renders), `docs/diagrams/cronograma.md`, `docs/Tesis/Correcciones/`
  (`numeros-canonicos.md`, `dictamen-correcciones.md`, `conteos-canonicos-tecnicos.md`),
  `CHANGES.md`. Gobernanza BAJA, docs-only.
- Sin cambios en `App/`, `n8n/`, `evaluation/` (solo lectura de las salidas de
  c-167), `openspec/config.yaml`, cadenas canónicas ni `docs/Tesis/v9 (IA)/`.
- Presupuesto de páginas: el total del PDF es hoy 112 frente al tope de 100, con
  exceso declarado; el change declara el nuevo total.

## Dependencies (contratos C1 a C9)

- **C1/C2 (c-168)**: planilla única `evaluation/data/plantilla_etiquetado.csv`;
  etiquetadores `E1`/`E2` distintos de los analistas originales, de los autores y de
  los operadores `O1`/`O2`; tabla primaria `evaluation/data/campana/doble_etiquetado.csv`
  con SHA-256; referencia del brazo manual = consenso del doble etiquetado nuevo
  (`E1 = E2`), discordantes aparte; `registro_sujetos.csv` sin solapes.
- **C5 (c-165)**: export `evaluation/data/campana/intervenciones.csv`, vocabulario
  `gate|muestreo|rederivacion|completado_manual`; métrica de backend
  `tasa_intervencion_backend`, distinta de la métrica de tesis
  `tasa_intervencion_humana` (c-167).
- **C6 (c-166)**: plan `evaluation/data/campana/plan_campana.csv` (`posicion`, `mitad`,
  `brazo_primero`); contrabalanceo de condición.
- **C9**: `evaluation/data/campana/predicciones_independiente.json` con el
  clasificador congelado (opcional: si falta, rama "sin corpus independiente
  declarado").
- **c-167**: salidas en `evaluation/data/campana/analisis/` (kappa con IC asintótico y
  bootstrap, exactitud manual con Wilson y bootstrap, McNemar,
  exactitud de v9 contra la referencia nueva (entrada propia, no reemplaza el
  `73,5 %`), `tasa_intervencion_humana` con estimación y ambos límites, efecto de
  orden de condición (entre grupos independientes) y de posición con el MDE que
  c-167 informe para cada análisis, métricas fuera de muestra).

## Gate (resumen; detalle en `tasks.md` §0)

(0.1) c-165 a c-168 archivados y fuera de `openspec list`; (0.2) tablas y salidas de
la campaña presentes con README y SHA-256; (0.3) `registro_sujetos.csv` sin solapes
(con solape, ramas negativas declaradas); (0.4) `pytest evaluation/` verde. Si 0.1 o
0.2 fallan (salvo el corpus independiente, opcional), el change se detiene.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Cifras citadas sin procedencia de campaña | Media | Gate 0 y registro previo en el memo (`3.N`, `archivo:línea`, SHA-256) |
| Confundir el kappa nuevo con el `0,87` | Media | D-kappa: entradas separadas y escenario "Sin intervalo atribuido al 0,87" |
| Desenlace negativo no previsto | Media | Cada requisito agregado o modificado trae su rama negativa propagada |
| Exceder el tope de palabras del resumen | Alta | Plan de recorte en `design.md` (margen actual ES 1 y EN 5) |
| Crecimiento de páginas | Alta | Sustitución de declaraciones retiradas; nuevo total declarado |
| Contaminar v9 o los valores canónicos | Baja | Alcance `v10 (IA)`; requisito de invariancia de los valores vigentes |

## Rollback Plan

Revertir los commits del change (archivos de `docs/Tesis/v10 (IA)/`,
`docs/Tesis/Correcciones/`, `docs/diagrams/cronograma.md` y `CHANGES.md`). Sin
migraciones ni cambios de esquema. Si la release ya se etiquetó, se publica una
release correctiva en lugar de mover el tag.

## Success Criteria

- [ ] Cada ítem (a)-(e) tiene el mismo estado (positivo o negativo declarado) en
      resumen, introducción, metodología, resultados, discusión, conclusiones,
      recomendaciones y memo.
- [ ] El `0,87` figura sin IC y con estado `vigente (sin IC)`; el kappa nuevo, con IC o
      con su declaración de no estimable.
- [ ] Los valores canónicos vigentes (`61,6 s`, `17,76 s`, `W = 363`, `73,5 %`,
      `0,6508`, kappa `0,87`) no cambian.
- [ ] PDF sin errores ni referencias rotas; `verify_citations.py` PASS; resumen dentro
      de 250 palabras (ES y EN).
- [ ] `openspec validate --strict` en verde y archive sin descartar escenarios.
