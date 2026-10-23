## Context

El change atiende la recomendacion **A1** del dictamen `auditorias/Dictamen_Tesis_v10_v1.1.0_CONEAU_2026-10-22.md` (VEREDICTO punto 1; seccion 5, segunda observacion de fondo; seccion 6, ultimo parrafo; seccion 7 (a)). Motivacion completa en `proposal.md`. Nota de numeracion: el dictamen cita capitulos por el numero de archivo; en el PDF `11-aspectos-legales.tex` es la seccion 7 y `07-resultados.tex` la seccion 8 (orden de `main.tex`). Este documento cita siempre archivo y linea.

### Hechos verificados en el codigo (solo lectura)

| Hecho | Evidencia |
|---|---|
| El cortocircuito se decide por `score_correctitud >= deterministic_score_threshold` con senal dominante (sin `sin_prediccion` ni `ambiguo`); la `confianza` no participa | `App/Backend/app/classifiers/hybrid.py:159-178`; `settings.py:110-134` |
| El cortocircuito devuelve `det_result` tal cual, con `requiere_revision_humana=False` | `hybrid.py:178`; `deterministic.py:249,294` |
| El umbral 0,70 solo se aplica a la salida de Gemini (dentro del clasificador y como "segunda linea") | `gemini_classifier.py:410,534`; `hybrid.py:250-255` |
| La reserva marca revision por construccion con confianza 0,0 (timeout, indisponibilidad, guarda de costo, respuesta invalida) | `hybrid.py:221-230,239-248`; `gemini_classifier.py:580-603` |
| El docstring de `classify` afirma que la revision se activa "de cualquier etapa": falso desde c-74 | `hybrid.py:143-147` frente a `hybrid.py:178` |
| Docstrings con el umbral 0,90 retirado y con la atribucion falsa de la revision al hibrido | `deterministic.py:8-10,227-229,294,349-360`; `gemini_classifier.py:11-13`; `hybrid.py:59-61` ("casos de alta confianza") |
| `deterministic_confidence_threshold` vale 1.0 y solo alimenta `is_confident`, que no usa el pipeline | `settings.py:115`; `deterministic.py:206,349-360` (unico consumidor: `tests/test_deterministic_classifier.py:212`) |
| Confianza deterministica = `min(1, margin_ratio * min(1, winner/(min_matches+2)))`, 0 si `winner < min_matches` (2), empate o sin senal | `deterministic.py:12-23,301-324`; `settings.py:116` |
| Segundo disparador del backend: reportante no identificado (VIS-005, c-82, posterior a la corrida oficial del 2026-10-07) | `App/Backend/app/services/incidente_service.py:401-410`; `openspec/specs/incident-visibility/spec.md:215-249` |
| N8N: el IF `Entrada valida` evalua una `confianza` sintetica de validez de entrada (>= 0.70) antes del POST; el IF `Requiere revision humana` evalua el indicador del backend | `n8n/workflow.json` (nodos `Normalizar entrada del incidente`, `Entrada valida`, `Requiere revision humana`) |
| La reasignacion de un incidente (`PATCH /api/v1/clasificaciones/{log_id}/validar`) no exige que el caso este marcado; la interfaz web solo la expone desde la cola de revision | `App/Backend/app/routes/clasificaciones.py:158-200`; `App/Frontend/src/pages/Administracion/index.tsx:503`, `RevisionHumanaTable.tsx:128`; `DetalleIncidente.tsx:1-14` (solo lectura) |

### Hechos verificados en los datos

- **Repeticion offline de la etapa deterministica** (fase propose; replica de `deterministic.py` con `min_matches=2`, pesos 0,5/0,3/0,2, longitud de referencia 200 y tau 0,5166 sobre `data/corpus_evaluacion_pseudonimizado.json`; sin servicios externos): 57 casos sin prediccion, 12 ambiguos, 131 con senal dominante; los 131 tienen score >= 0,516667 (minimo) y cortocircuitan; 97/131 aciertos estrictos; confianzas {0,0: 90; 1/6: 8; 0,5: 26; 0,75: 6; 1,0: 1}; 124 con confianza < 0,70 (94 aciertos), 7 con >= 0,70, 1 con >= 0,90. Reproduce exactamente la Seccion 4 de `numeros-canonicos.md`, la tabla `tab:bandas` (98/26/6 deterministicos) y `docs/deterministic_calibration.md:20,39-40`: no hay deriva entre el codigo vigente y la etapa evaluada.
- **Calibracion comparativa** (`docs/deterministic_calibration.md:35-53,72-79`): tau OOF 0,516666... en los cinco pliegues, truncado a 0,5166; `precision_det(S)` 97/131 = 0,7405; `precision_gem(S)` 88/130 = 0,6769 sobre la cache FORCE-ESCALATE (un caso sin prediccion de Gemini excluido). Con el piso comparativo cumplido en todo `S`, el punto equivale a cortocircuitar todo caso con senal dominante (cualquier umbral en [0; 0,5167] da el mismo conjunto).
- Las caches `evaluation/predicciones.json` y `evaluation/predicciones_calibracion.json` estan en `.gitignore:72-73` y no existen en este arbol: los valores dependientes de Gemini (88/130, 0,85 minimo) solo se citan desde fuentes versionadas (`docs/deterministic_calibration.md`, Seccion 4 del memo, `07-resultados.tex`).

### Hechos verificados en la historia del repositorio

- **c-71** (commit `1368fd8`, 2026-10-05): "ampliar sinonimos/frases por sector guiado por las misclasificaciones del corpus" (`openspec/changes/archive/2026-10-06-c-71-hardening-clasificador-determinista/proposal.md:23`, `design.md:46`, `tasks.md:35`); `keywords.py` +67 lineas con comentarios "del corpus".
- **c-72** (commit `a76851e`, 2026-10-06): reglas de frontera del prompt redactadas a partir de casos del corpus (R002, R038) (`.../2026-10-07-c-72-unificar-clasificacion-telefonica/proposal.md:7`, `design.md:44`).
- **c-74** (2026-10-07): tau por validacion cruzada OOF sobre el corpus (`.../2026-10-07-c-74-calibracion-cortocircuito-determinista/design.md:93-94`), opcion (iii) admitida por `evaluation-framework` ("Provenance de los datos de calibracion", que exige documentar la procedencia "junto con su tradeoff").
- La corrida oficial (2026-10-07) uso ese vocabulario, ese prompt y ese tau. Esto contradice `05-arquitectura.tex:78`, `06-implementacion.tex:75`, `08-discusion.tex:18` y `12-anexos.tex:135` ("sin exposicion al corpus").

### Restricciones

- **Gate 0 de numeros canonicos** (`tesis-numeros-canonicos`): todo valor nuevo entra primero en `numeros-canonicos.md` con procedencia; esta rama registra abajo sus objetivos de propagacion con texto ANTES y DESPUES y la reversibilidad de cada decision editorial.
- **Sin fabricacion y sin cambio de comportamiento**: el change no re-ejecuta la evaluacion, no llama a Gemini y no altera la logica del clasificador ni del flujo.
- **Presupuesto de paginas**: PDF actual de 101 paginas (`main.aux`: `\@abspage@last{101}`), tratado como tope por c-116/c-121; ver "Presupuesto de paginas".
- **Acentuacion**: los textos DESPUES son carga util LaTeX y se escriben con la acentuacion normativa del manuscrito; el resto de este artefacto sigue la convencion sin tildes.

## Goals / Non-Goals

**Goals:**

- Una sola definicion de las magnitudes de la etapa deterministica (fuerza de senal y puntaje de correctitud) y de la confianza de cada etapa, usada con los mismos nombres en todos los capitulos.
- Declarar el alcance real del gate por etapa y el segundo disparador del backend, y retirar "superior al 90 %" y "unico disparador automatico".
- Consignar en resultados los 124/200 casos no escalados y su causa.
- Declarar en el capitulo legal el alcance real de la salvaguarda sobre el 65,5 % de los casos.
- Registrar los numeros nuevos en el memo canonico y sincronizar la documentacion para agentes, la base de conocimiento, las specs con deriva y los docstrings con el comportamiento vigente.
- No dejar en la tesis una afirmacion de separacion estricta entre datos de ajuste y de validacion que el repositorio desmiente (sujeto a checkpoint, D9).

**Non-Goals:**

- No se modifica la logica del gate ni del cortocircuito, ni `Settings`, ni el flujo N8N (D1).
- No se rehace la calibracion por etapa ni las tablas por etapa o por canal, ni se reformula la conclusion de "calibracion invertida" (c-126).
- No se reformula la sub-hipotesis de intervencion humana (`01-introduccion.tex:34`, `07-resultados.tex:138`) ni las hipotesis subsidiarias (c-128); no se computa el balance de derivaciones erroneas (c-127); no se agregan lineas de trabajo futuro (c-131).
- No se corrige la acentuacion fuera de los fragmentos reescritos (c-132), la cita de Xuan et al. (c-134), la cronologia (c-130) ni la fila `timeout` del Anexo H (c-135).
- No se re-mide el clasificador sin los ajustes de c-71/c-72 (posible analisis de sensibilidad: Open Questions).
- No se verifica ni negocia el tope de paginas de la familia (c-136).

## Decisions

### D1 - Documentar el comportamiento implementado; no tocar la logica

La tesis pasa a describir lo que el codigo hace y lo que opero en el experimento. **Alternativas descartadas:** (a) extender la regla 0,70 a la etapa deterministica: marcaria 124/200 casos (62 %) para revision, invalidaria la evaluacion ya reportada y aplicaria un umbral de probabilidad a una magnitud que no lo es; (b) crear ahora un gate por caso sobre el puntaje (por ejemplo, revisar los cortocircuitos de un unico patron coincidente): es una linea de trabajo futuro que corresponde a c-131.

### D2 - Nomenclatura unica de las magnitudes

- **Confianza** se conserva como nombre del campo persistido, siempre calificada por etapa: en la etapa deterministica es un *indice de fuerza de senal* en [0;1] (margen del ganador sobre el segundo ponderado por la cantidad de patrones; 0 con menos de dos patrones coincidentes); en Gemini es la *confianza autodeclarada* por el modelo; en la reserva vale 0,0 por construccion.
- **Puntaje de correctitud** (`score_correctitud`) nombra el criterio de cortocircuito; ordena la correctitud esperada y no es una probabilidad.
- **Punto de operacion** nombra el umbral 0,5166 sobre el puntaje. **Cortocircuito** se introduce una vez.

**Alternativa descartada:** renombrar la confianza deterministica como "fuerza de senal" en toda la tesis y dejar de llamarla confianza. Se descarta porque el campo persistido y la tabla `tab:bandas` (c-126) usan `confianza`; calificarla evita una discrepancia entre texto, base de datos y tablas. Se prefiere "puntaje" a "score" en la prosa (el manuscrito ya usa "puntaje" en `08-discusion.tex:16` y `11-aspectos-legales.tex:34`); el nombre del campo va en `\texttt{}` una vez.

### D3 - Alcance del gate por etapa y segundo disparador

Se declara en `02`, `05`, `06`, `07`, `08` y `11` que la regla `requiere_revision_humana = (confianza < 0,70)` se evalua solo sobre la salida de Gemini, que la reserva deriva siempre y que la etapa deterministica no deriva por su confianza. En `06-implementacion.tex:40`, que describe el flujo del sistema, se agrega el segundo disparador del backend (reportante no identificado, VIS-005). **Alternativa descartada:** omitir VIS-005 para ahorrar texto; dejaria falso el reemplazo de "unico disparador". En resultados no se menciona VIS-005: la evaluacion mide el indicador del clasificador, y la frase "derivacion automatica por caso basada en la clasificacion" lo acota.

### D4 - Criterio de cortocircuito vigente en lugar del "90 %"

`05-arquitectura.tex:80` reemplaza la frase del 90 % por el criterio vigente (senal dominante y puntaje >= 0,5166), su procedencia (validacion cruzada de cinco pliegues con piso comparativo frente a Gemini, 0,7405 frente a 0,6769) y su equivalencia en el corpus (los 131 casos con senal dominante), y explica que el umbral 0,90 del diseno inicial se retiro porque esa confianza no reflejaba la fiabilidad de la decision (c-71). Se elimina el ejemplo de la impresora, que afirma "alta certeza" y usa el rotulo no canonico "Soporte Tecnico" sin calificar: es incompatible con D2 y su retiro compensa paginas. **Alternativas descartadas:** (a) borrar el 90 % sin explicar su origen: deja abierta la disyuntiva del dictamen ("o bien la descripcion del diseno no corresponde a lo implementado"); (b) citar la cobertura de 1/200 del piso de precision 0,90 de c-71: mezcla un piso de precision con un umbral de confianza y agrega un numero que la tesis no necesita.

### D5 - Resultados: 124/200 y fronteras con c-126 y c-128

El primer parrafo de `subsec:reduccion-intervencion` (`07-resultados.tex:136`) consigna 124 de 200 (62 %) casos con confianza < 0,70 sin escalamiento, todos deterministicos, su causa (D2, D3), los 69 casos de Gemini con confianza >= 0,85 y la reserva sin activarse, y que sobre el 65,5 % no hubo derivacion automatica por caso basada en la clasificacion. El parrafo de `07-resultados.tex:138` (rotulo de la sub-hipotesis) queda para c-128. La subseccion `subsec:calibracion` (`07-resultados.tex:140-165`) queda para c-126, que debe adoptar D2 y reformular "umbral del 70 % que gobierna el gate" (`:143`) y "el gate del 70 % no aislo los errores" (`:165`); la frase "sobre los 200 casos del corpus" de `:143` es correcta en ese contexto (la tabla de bandas cubre los 200 casos) y no se toca. **Alternativa descartada:** consignar los 124 casos en la subseccion de calibracion; mezcla la definicion del gate con el analisis de calibracion que el dictamen pide rehacer por etapa.

### D6 - Hallazgo de Gemini en la discusion: alcance correcto y valoracion neutra

La ultima oracion de `08-discusion.tex:16` (introducida por c-121) atribuye la conducta a "los 200 casos del corpus"; Gemini resolvio 69. Se corrige el alcance y se reemplaza "lectura positiva" por una lectura propia cuya valoracion (fiabilidad o sobreconfianza) se remite a la calibracion por etapa (c-126), coherente con A2 ("la confianza autodeclarada por Gemini no discrimina aciertos de errores dentro del rango observado"). Se modifica en consecuencia el requisito "Hallazgo del gate de clasificacion presentado como resultado propio". **Alternativa descartada:** conservar "positiva"; un modelo que declara siempre >= 0,85 con exactitud cercana al 72 % puede leerse como sobreconfianza, y c-126 debe poder concluirlo sin contradecir un requisito vigente. **Reversibilidad:** c-126 fija la valoracion final.

### D7 - Capitulo legal: alcance real de la salvaguarda (MEDIUM, checkpoint de autores)

La ultima oracion de `11-aspectos-legales.tex:34` declara que el 0,70 solo alcanza a la etapa semantica y a la reserva; que sobre el 65,5 % no existe derivacion automatica por caso basada en la clasificacion; que la salvaguarda de esa fraccion se limita al criterio de diseno del punto de operacion (estimado sobre el corpus de validacion) y a la reasignacion trazable, disponible en la interfaz REST y expuesta en la interfaz web solo para los casos derivados; y remite la capacidad discriminante de la confianza del modelo a `subsec:calibracion`, sin afirmar su resultado (asi c-126 no necesita reeditar esta oracion). Se aparta del encuadre sugerido de "calibracion comparativa como gate operativo": es un criterio de diseno de nivel de etapa, no deriva ningun caso y se estimo dentro de la muestra (D9). **Alternativas descartadas:** (a) presentar la calibracion comparativa como garantia: sobreafirma; (b) omitir la limitacion de la interfaz web: el parrafo afirma que el sector "conserva la potestad de modificar la clasificacion", y la unica via sin la cola de revision es la API. **Reversibilidad:** si un change de codigo expone la reasignacion de incidentes no derivados en la interfaz web, se retira la salvedad. **Checkpoint:** los autores confirman esta redaccion antes de editar (Open Question 2).

### D8 - Anexo H: fila del umbral de revision

Se agrega a `tab:anexo_gemini_params` (`12-anexos.tex:96-107`) una fila "Umbral de revision humana" (0,70) que declara que es la confianza minima de una respuesta del modelo para no marcarla y que no se aplica a la etapa deterministica. El rotulo va en prosa y no como `\texttt{human\_review\_threshold}`, porque la primera columna mide 3,0 cm y el identificador en monoespaciado la desborda. El punto de operacion 0,5166 no se agrega: no es un parametro de la inferencia con Gemini y queda definido en `05-arquitectura.tex`. **Alternativa descartada:** una oracion en `subsec:anexo-validacion-respuesta`; la tabla es el lugar donde un replicador busca los parametros.

### D9 - Procedencia de los ajustes realizados sobre el corpus (MEDIUM, checkpoint de autores)

El change introduce en la tesis que el punto de operacion se derivo por validacion cruzada sobre el corpus (D4); con eso, `08-discusion.tex:18` ("separacion estricta entre datos de construccion y datos de validacion", "datos no vistos") queda contradicho por el propio change, y la historia del repositorio lo contradice tambien para el vocabulario (c-71) y las reglas de frontera del prompt (c-72). Se reescriben con texto veraz `05-arquitectura.tex:78` (puntero unico a la discusion), `06-implementacion.tex:75`, `08-discusion.tex:18` y `12-anexos.tex:135`: las metricas de clasificacion son estimaciones dentro de la muestra, probablemente optimistas, y su confirmacion exige un corpus independiente. No se altera ningun numero. **Alternativas:** (a) change dedicado c-137 con estas cuatro ediciones y un analisis de sensibilidad offline (vocabulario previo a c-71 sobre la cache FORCE-ESCALATE); c-125 conservaria solo el puntero de `05:78`, pero `08:18` seguiria contradiciendo el texto de c-125 hasta que c-137 se aplique; (b) no mencionar la procedencia del tau; incumple el requisito de procedencia de `evaluation-framework` y oculta un dato verificable en el repositorio publico. **Recomendacion:** incluir en c-125 (default) con checkpoint; la opcion (a) es aceptable si c-136 queda bloqueado hasta aplicar c-137. **Reversibilidad:** si los autores acreditan que los ajustes de c-71/c-72 usaron datos ajenos al corpus de evaluacion, se restituye la afirmacion de no exposicion citando esa evidencia.

### D10 - Numeros canonicos: Seccion 3.7

Se agrega a `numeros-canonicos.md` la Seccion 3.7 "Gate de revision por etapa y punto de operacion (c-125)" con: casos con confianza < 0,70 sin escalamiento `124/200` (`62,0 %`); confianza minima declarada por Gemini `0,85` en sus `69` casos; punto de operacion `0,5166`; cobertura del punto `131/200` (equivalente a la etapa deterministica); `precision_det(S)` `97/131` (`0,7405`); `precision_gem(S)` `88/130` (`0,6769`). Cada fila con archivo:linea y estado `vigente`, mas notas: 97/131 coincide con la exactitud de la etapa deterministica de la corrida oficial (c-126 la consume y le agrega el IC); 88/130 proviene de una cache no versionada y excluye un caso; ambos son estimaciones dentro de la muestra (D9). La Seccion 7 suma un punto no resoluble: la version del prompt de la cache FORCE-ESCALATE no esta documentada (reversible si el autor aporta su `cache_meta`). **Alternativa descartada:** registrar solo los cuatro valores pedidos; el 62,0 % y el 0,85 sobre 69 casos tambien se citan en el texto nuevo y el Gate 0 exige su fila.

### D11 - Documentacion para agentes, base de conocimiento y specs con deriva

- `openspec/config.yaml` (declarado autoritativo para umbrales en `AGENTS.md:16`): linea 11 (descripcion) y linea 42 (`thresholds: { deterministic_score: 0.5166, human_review: 0.70 }` con comentario de alcance). Ningun codigo lee esa clave (verificado con `grep`).
- `CLAUDE.md`: linea 50 (alcance del gate por etapa, reserva, cortocircuito por puntaje, VIS-005) y linea 100 (distinguir el IF de validacion de entrada del IF del indicador del backend). Se mantiene el ingles del archivo; no se tocan otras reglas.
- `knowledge-base/`: `01:14,24`, `02:39`, `03:63`, `04:57`, `05:8,9,11`, `06:28,61`, `07:9,15,48`, `08:64-65`, `09:12,23-24`, `README.md:32`. Lo leen los agentes de c-126 a c-136 (`openspec/config.yaml` `context_files`); dejarlo con el 0,90 arriesga reintroducir el error en la tesis.
- Specs: `classification-resilience` "Clasificacion telefonica determinista-primero" (dice "confianza calibrada") y `incident-visibility` VIS-005 (formula `(confianza < 0.70) OR ...`) se corrigen como MODIFIED en este change.

Los cambios de `CLAUDE.md` y `openspec/config.yaml` son archivos de configuracion de agentes: requieren la confirmacion explicita del usuario antes de aplicarse (Open Question 4). **Alternativa descartada:** limitarse a `config.yaml` y `CLAUDE.md` como pedia el encargo; la base de conocimiento repite la regla 0,90/0,70 en reglas de negocio (RN-CL-02, RN-CL-05) y decisiones (DD-07) que consumen los agentes de la familia. `docs/n8n-workflow-guide.md:541,553` y `docs/parameters_gemini.md:100` no se tocan: son registros historicos fechados.

### D12 - Codigo: docstrings y test de caracterizacion

- Docstrings y comentarios alineados, sin cambiar el numero de lineas (las citas `archivo:linea` de la Seccion 4 del memo y de este diseno siguen apuntando al mismo contenido): `hybrid.py:59-61,143-147`; `deterministic.py:8-10,227-229,294,349-360`; `gemini_classifier.py:11-13`.
- Test de caracterizacion en `tests/test_hybrid_classifier.py`: el cortocircuito deterministico con puntaje en el punto de operacion y confianza en {0,0; 1/6; 0,5} devuelve `requiere_revision_humana is False` y no invoca Gemini. Fija el contrato que la tesis declara: si alguien extiende el gate a la etapa deterministica, el test y la tesis deben cambiar juntos.
- **Modo TDD estricto:** no se escribe codigo de produccion; la red de seguridad (tests del clasificador antes y despues) y la comparacion de AST sin docstrings demuestran que no hay cambio de comportamiento. El test de caracterizacion pasa en la primera ejecucion por diseno (RED no aplica) y se triangula con tres valores de confianza.

**Alternativa descartada:** documentar el desfase solo en la tesis o en el memo. Un evaluador que contraste la tesis con el codigo encontraria la afirmacion contraria en el docstring. Si el usuario prefiere no tocar `App/Backend` en esta familia (Open Question 3), se omite el bloque 7 de `tasks.md` y el desfase se registra en la Seccion 4 del memo.

## Objetivos de propagacion (ANTES -> DESPUES)

Lineas segun la numeracion de `grep -n` sobre el arbol actual (sin CR sueltos en `sections/*.tex`). Las ediciones de D7 y D9 (T04, T12, T13, T14, T15) se aplican despues del checkpoint de autores.

**T01** `02-marco-teorico.tex:34`, dos oraciones finales.

```latex
% ANTES
El sistema propuesto adopta el grado intermedio: clasifica de forma automática y escala a revisión humana todo caso cuya confianza declarada cae por debajo del umbral, según la regla \texttt{requiere\_revision\_humana = (confianza < 0{,}70)}, evaluada en la \autoref{sec:resultados}. La calibración de esa confianza condiciona la cobertura efectiva de la salvaguarda (\autoref{sec:discusion}).
% DESPUES
El sistema propuesto adopta una revisión selectiva acotada por etapa: la regla \texttt{requiere\_revision\_humana = (confianza < 0{,}70)} se aplica a la confianza autodeclarada por el modelo de lenguaje y a la etapa de reserva, pero no a la etapa determinística, cuya confianza mide fuerza de señal y no probabilidad de acierto (\autoref{subsec:subsistema-clasificacion}). La calibración de la confianza del modelo condiciona la cobertura efectiva de la salvaguarda (\autoref{sec:discusion}).
```

**T02** `02-marco-teorico.tex:46`, oracion final (las oraciones previas, con la cita de Xuan et al., son de c-134).

```latex
% ANTES
En el sistema propuesto este concepto fundamenta el umbral operativo de revisión humana, ya que las clasificaciones con confianza inferior a 0,70 se derivan a supervisión; la fiabilidad de ese umbral depende tanto de la exactitud como de la calibración del clasificador.
% DESPUES
En el sistema propuesto este concepto fundamenta el umbral operativo de revisión humana, ya que las clasificaciones de la etapa semántica con confianza inferior a 0,70 se derivan a supervisión; la fiabilidad de ese umbral depende tanto de la exactitud como de la calibración del modelo.
```

**T03** `05-arquitectura.tex:24`, celda de la capa 4 de `tab:capas`.

```latex
% ANTES
4. Inferencia & Modelo Gemini~3.6 Flash de Google, invocado únicamente cuando el filtro determinístico previo no alcanza el umbral de confianza preestablecido. \\
% DESPUES
4. Inferencia & Modelo Gemini~3.6 Flash de Google, invocado únicamente cuando el filtro determinístico previo no resuelve el caso (\autoref{subsec:subsistema-clasificacion}). \\
```

**T04** `05-arquitectura.tex:78`, oracion intermedia (D9).

```latex
% ANTES
Tanto la construcción del filtro determinístico como el ajuste del prompt se realizaron sin acceso al corpus de validación, para evitar fuga de datos (véase \autoref{subsec:interpretacion-resultados}).
% DESPUES
La procedencia de los datos empleados para ajustar el filtro, el prompt y el punto de operación se declara en la \autoref{subsec:interpretacion-resultados}.
```

**T05** `05-arquitectura.tex:80`, parrafo completo (D2, D4).

```latex
% ANTES
Este filtro es capaz de derivar de forma inmediata aquellos incidentes que contienen marcadores inequivocos. Por ejemplo, la presencia simultanea de las palabras \texttt{impresora}, \texttt{papel} y \texttt{atasco} sugiere con alta certeza una categoría de Soporte Técnico. Cuando este filtro inicial alcanza un umbral de confianza superior al 90~\%, la decisión se toma sin consultar al modelo externo, lo que reduce sustancialmente la latencia y el costo de inferencia.
% DESPUES
Este filtro resuelve de inmediato los incidentes con marcadores léxicos inequívocos y emite dos magnitudes en \([0;1]\) que no son probabilidades de acierto: la \emph{confianza}, índice de fuerza de señal ---margen del sector ganador sobre el segundo, ponderado por la cantidad de patrones coincidentes--- que vale 0 con menos de dos patrones, y el \emph{puntaje de correctitud} (\texttt{score\_correctitud}), que ordena la correctitud esperada. El filtro decide sin consultar al modelo (cortocircuito) cuando la señal es dominante ---sin empate ni ausencia de coincidencias--- y el puntaje alcanza el punto de operación 0,5166; la confianza no interviene y esos casos no se derivan a revisión por su confianza. El punto se derivó por validación cruzada de cinco pliegues sobre el corpus, maximizando la cobertura sin que la precisión del filtro fuera inferior a la del modelo sobre el conjunto que resuelve (0,7405 frente a 0,6769), y equivale a resolver los 131 casos con señal dominante. Sustituyó al umbral de 0,90 sobre la confianza del diseño inicial, retirado porque esa confianza no reflejaba la fiabilidad de la decisión.
```

**T06** `05-arquitectura.tex:82`, tres fragmentos (el tercero precisa la reserva; el segundo es compensacion C1).

```latex
% ANTES (1)
La segunda etapa, activada únicamente cuando el filtro determinístico no alcanza el umbral, consulta
% DESPUES (1)
La segunda etapa, activada únicamente cuando el filtro determinístico no resuelve el caso, consulta
% ANTES (2)
La justificación de este diseño compositivo radica en aprovechar la rapidez del filtro determinístico para los casos triviales y reservar la capacidad semántica del modelo de lenguaje grande para los casos ambiguos o de redacción atípica, optimizando la relación entre exactitud, costo y latencia.
% DESPUES (2)
El diseño compositivo reserva la capacidad semántica del modelo para los casos que el filtro no resuelve, lo que reduce la latencia y el costo de inferencia.
% ANTES (3)
(3)~una etapa de reserva (\emph{fallback}) que asigna una categoría por defecto y marca el caso para revisión humana cuando las etapas previas no producen una salida válida.
% DESPUES (3)
(3)~una etapa de reserva (\emph{fallback}) que, cuando el modelo no responde o no produce una salida válida, fija la confianza en 0,0 y marca siempre el caso para revisión humana.
```

**T07** `06-implementacion.tex:39`, final de la oracion del indicador (compensacion C4: la condicion completa se enuncia una vez en T08).

```latex
% ANTES
que el backend activa cuando la confianza del clasificador resulta inferior al umbral de 0,70.
% DESPUES
que el backend activa según las condiciones descritas en la etapa de evaluación.
```

**T08** `06-implementacion.tex:40`, dos fragmentos (D3; corrige "esta" solo dentro del fragmento reescrito).

```latex
% ANTES (1)
Cuando el indicador esta activo ---es decir, cuando la confianza del clasificador fue inferior al umbral de 0,70--- el flujo notifica
% DESPUES (1)
Cuando el indicador está activo el flujo notifica
% ANTES (2)
El umbral de 0,70 opera como único disparador automático de revisión humana; su calibración se analiza en la Sección~\ref{subsec:calibracion}.
% DESPUES (2)
El backend activa el indicador cuando la etapa Gemini devuelve una confianza inferior a 0,70, cuando interviene la etapa de reserva o cuando el reportante no se identifica en el directorio de empleados; los casos que resuelve el filtro determinístico no se derivan por su confianza (\autoref{subsec:subsistema-clasificacion}). La calibración de la confianza del modelo se analiza en la Sección~\ref{subsec:calibracion}.
```

**T09** `06-implementacion.tex:87` y `:95`.

```latex
% ANTES (:87)
cola de revisión humana para casos de baja confianza
% DESPUES (:87)
cola de revisión humana para los casos derivados por el backend
% ANTES (:95)
la pestaña de revisión humana para los casos de baja confianza
% DESPUES (:95)
la pestaña de revisión humana para los casos derivados por el backend
```

**T10** `07-resultados.tex:136`, parrafo completo; se conserva `\label{subsec:reduccion-intervencion}` (`:134`) y el parrafo `:138` (D5).

```latex
% ANTES
La intervención humana en el flujo automatizado se deriva del gate de revisión implementado, \texttt{requiere\_revision\_humana = (confianza < 0,70)}, que escala un caso a un operador humano cuando la confianza devuelta por el clasificador cae por debajo de ese umbral. El gate de revisión no derivó ningún caso del corpus: la etapa determinística fija el campo en \texttt{False} y la etapa Gemini nunca devolvió una confianza inferior a 0,85, resultado que se interpreta en la \autoref{sec:discusion}.
% DESPUES
La intervención humana en el flujo automatizado se deriva del gate de revisión implementado, \texttt{requiere\_revision\_humana = (confianza < 0,70)}, que solo se evalúa sobre la salida de la etapa Gemini; la etapa de reserva deriva siempre y la determinística no deriva por su confianza (\autoref{subsec:subsistema-clasificacion}). El gate no derivó ningún caso del corpus: en 124 de los 200 casos (62~\%) la confianza registrada fue inferior a 0,70, pero todos pertenecen a la etapa determinística, cuya confianza mide fuerza de señal; los 69 casos de Gemini declararon siempre al menos 0,85 y la etapa de reserva no se activó. Sobre el 65,5~\% de los casos no existió, por lo tanto, derivación automática por caso basada en la clasificación. El resultado se interpreta en la \autoref{sec:discusion}.
```

**T11** `08-discusion.tex:16`, oracion final (D6).

```latex
% ANTES
El comportamiento del gate admite, además, una lectura positiva: la etapa Gemini nunca declaró una confianza inferior a 0,85 sobre los 200 casos del corpus, de modo que el gate de revisión (confianza inferior a 0,70) no derivó ningún caso.
% DESPUES
El comportamiento del gate admite, además, una lectura propia: en los 69 casos que resolvió, la etapa Gemini nunca declaró una confianza inferior a 0,85, de modo que el gate (confianza inferior a 0,70) no derivó ningún caso; si esa conducta expresa fiabilidad o sobreconfianza depende de la calibración por etapa (\autoref{subsec:calibracion}).
```

**T12** `08-discusion.tex:18`, parrafo completo (D9).

```latex
% ANTES
El rigor metodológico adoptado para evitar \emph{data leakage} merece una observación aparte. El filtro determinístico se construyó mediante análisis manual de incidentes no incluidos en el corpus y el prompt fue ajustado en entornos de preproducción sin exposición a los 200 casos de validación; solo después de completar el desarrollo se evaluó el desempeño sobre la totalidad del corpus, garantizando que las métricas reportadas reflejan el desempeño del sistema sobre datos no vistos. Esta separación estricta entre datos de construcción y datos de validación constituye una garantía metodológica del presente estudio.
% DESPUES
La procedencia de los datos de ajuste merece una observación aparte, porque la separación entre datos de construcción y de validación no fue estricta: las reglas de frontera del prompt y la ampliación del vocabulario del filtro se incorporaron a partir de errores observados en el corpus, y el punto de operación del filtro se derivó por validación cruzada sobre él. Las métricas de clasificación reportadas ---en particular la exactitud de la etapa determinística--- son, por lo tanto, estimaciones dentro de la muestra, probablemente optimistas, cuya confirmación exige un corpus independiente (\autoref{sec:recomendaciones}).
```

**T13** `06-implementacion.tex:75`, segunda oracion del item (D9; las semanas y fechas del item son de c-130).

```latex
% ANTES
Los ajustes se realizaron exclusivamente sobre incidentes representativos en entornos de preproducción, sin exposición al corpus de validación de 200 casos, preservando la integridad de la etapa experimental posterior.
% DESPUES
Los ajustes se realizaron sobre incidentes de preproducción y, en su tramo final, sobre errores observados en el corpus de validación (\autoref{subsec:interpretacion-resultados}).
```

**T14** `12-anexos.tex:135`, primera oracion (D9).

```latex
% ANTES
El prompt se validó y ajustó de forma iterativa sobre un conjunto de aproximadamente 100 incidentes representativos en entornos de preproducción, sin exposición al corpus de validación de 200 casos.
% DESPUES
El prompt se validó y ajustó de forma iterativa sobre un conjunto de aproximadamente 100 incidentes representativos en entornos de preproducción; las reglas de frontera de la versión evaluada se incorporaron a partir de errores observados en el corpus de validación.
```

**T15** `11-aspectos-legales.tex:34`, oracion final (D7).

```latex
% ANTES
Cabe precisar que el umbral de confianza de 0,70 que dispara la revisión obligatoria no constituye, por sí solo, una garantía suficiente de esa salvaguarda: el análisis de calibración de la \autoref{sec:resultados} muestra que la confianza declarada por el clasificador no discrimina de forma fiable los casos correctos de los incorrectos, por lo que la supervisión humana efectiva se apoya además en la revisión por el sector responsable y en la trazabilidad de las correcciones, y no únicamente en el puntaje del modelo.
% DESPUES
Cabe precisar su alcance: el umbral de confianza de 0,70 que dispara la revisión obligatoria solo alcanza a la etapa semántica y a la de reserva, de modo que sobre el 65,5~\% de los casos, resueltos por la etapa determinística, no existe derivación automática por caso basada en la clasificación. Para esa fracción la salvaguarda se limita al criterio con que se fijó el punto de operación del filtro ---precisión no inferior a la del modelo sobre el conjunto que resuelve, estimada sobre el corpus de validación--- y a la reasignación trazable del incidente descrita, disponible en la interfaz REST y expuesta en la interfaz web solo para los casos derivados. La capacidad de la confianza del modelo para discriminar aciertos de errores se analiza en la \autoref{subsec:calibracion}.
```

**T16** `12-anexos.tex`, fila nueva en `tab:anexo_gemini_params` despues de la fila `timeout` (`:104`) (D8).

```latex
% DESPUES (fila nueva)
Umbral de revisión humana & 0,70 & Confianza mínima de una respuesta del modelo para no marcarla para revisión; no se aplica a la etapa determinística (\autoref{subsec:subsistema-clasificacion}). \\
```

**Revisados sin cambios:** `04-marco-metodologico.tex:61` ("con el gate de revision aplicable": no es falso y la linea es de c-130); `05-arquitectura.tex:58,145`; `12-anexos.tex:104,113` (la reserva con confianza 0,0 y revision ya esta bien descrita); `01-introduccion.tex:34` y `07-resultados.tex:138` (c-128); `09-conclusiones.tex:41` y `08-discusion.tex:14` (c-127); `10-recomendaciones.tex:8,26` (c-131).

## Fronteras con la familia de changes

| Superficie | Dueno | Consigna para el otro change |
|---|---|---|
| Definicion de magnitudes y alcance del gate (T01-T11, T15, T16) | c-125 | c-126, c-127, c-128 y c-131 usan los nombres de D2 y el alcance de D3 y no los redefinen. |
| `07-resultados.tex:140-165` (bandas y calibracion), valoracion del hallazgo de Gemini | c-126 | Desagregar por etapa con D2; reformular `:143` y `:165`; conservar `\label{subsec:calibracion}` (T08, T11 y T15 lo referencian); rotular la exactitud deterministica como estimacion dentro de la muestra (D9); consumir 97/131 de la Seccion 3.7 y agregar su IC. |
| `01-introduccion.tex:34`, `07-resultados.tex:138` | c-128 | Si la sub-hipotesis pasa a "cobertura efectiva del gate", la base es 69 de 200 casos sujetos al gate (Gemini) mas la reserva (0). La hipotesis de eficiencia del esquema hibrido no puede apoyarse en 0,7405 frente a 0,6769 como evidencia independiente (D9). |
| `08-discusion.tex:14`, `09-conclusiones.tex:41` | c-127 | "Sin sustituir el juicio humano" debe reconocer que no hubo derivacion por caso basada en la clasificacion sobre el 65,5 % (T10). |
| `10-recomendaciones.tex` | c-131 | La linea "calibracion del gate de confianza" puede proponer un gate por caso sobre el puntaje o sobre los cortocircuitos de un unico patron (D1 (b)) y la confirmacion sobre un corpus independiente (D9). |
| `02-marco-teorico.tex:46` (cita) | c-134 | Edita las oraciones previas; T02 solo la ultima. Aplicar en serie. |
| `06-implementacion.tex:75` (semanas), modelo evaluado | c-130 | T13 no fecha los ajustes; c-130 fija las fechas. Deriva de modelo detectada: `CLAUDE.md` y `openspec/config.yaml` dicen "Gemini 2.5 Flash"; tesis y `Settings`, 3.6. |
| `12-anexos.tex:104` (`timeout` 10 s frente a 30 s en `settings.py:85`) | c-135 | T16 agrega una fila contigua; no editar la misma fila. |
| Acentuacion fuera de los fragmentos reescritos (por ejemplo `06-implementacion.tex:40` "no lo esta", "continua", "este vacia") | c-132 | Correr despues de c-125. |
| Paginas, release | c-136 | Recibe el conteo de paginas registrado en la tarea 9.4. |

## Presupuesto de paginas

- **Estimacion.** Conteo de palabras ANTES/DESPUES de T01-T16 (script de conteo sobre los bloques de la seccion anterior): +279 tokens netos (los decimales cuentan doble), aprox. +250 palabras. A la densidad medida del manuscrito (aprox. 370 palabras por pagina con `\doublespacing`, 11 pt, A4: por ejemplo `08-discusion.tex`, 2.951 palabras en 7 paginas) el change agrega aprox. **+0,7 pagina** (rango +0,6 a +0,9 por cortes de parrafo y la fila nueva de tabla). Mayores aportes: T05 (+113), T10 (+50), T15 (+46), T08 (+26), T16 (+26); sin el bloque D9 (T04, T12, T13, T14) el total apenas cambia (+278).
- **Compensacion incluida:** C1 (T06(2), fusion de la justificacion de `05:82`, -20), C2 (T05 sin el ejemplo de la impresora, -20), C4 (T07, puntero en lugar de repetir la condicion, -5) y la reescritura compacta de T12-T13.
- **Compensacion condicional C3**, solo si tras compilar el PDF supera 101 paginas: en `05-arquitectura.tex:84`, eliminar la aposicion final de las reglas de frontera (cadena literal del manuscrito: `, redactadas con los cinco strings canónicos sin tildes`) y la coda del costo telefonico (`, momento en el cual la reserva de costo se imputa a la superficie de inferencia del backend`) (aprox. -25). No se recorta texto que pertenezca a otros changes.
- **Declaracion.** Con 101 paginas de base, c-125 puede llevar el PDF a 102 aun con C3. La familia (tablas por etapa y por canal de c-126 y c-129, balance de c-127, dos subsecciones de c-131, literatura de c-133) excede el tope con certeza; el tope de 101 paginas debe renegociarse o resolverse con una pasada de reduccion global en c-136. c-125 registra su conteo y no recorta contenido de otros changes.

## Risks / Trade-offs

- [Los autores discuten los hechos de D9 (c-71/c-72)] -> Checkpoint previo (tarea 1.4) con la evidencia citada; reversibilidad declarada en D9; si se elige un change dedicado, se mueve el bloque y se bloquea c-136 hasta aplicarlo.
- [La divulgacion de D9 debilita la afirmacion de validez] -> No cambia ningun numero; la refutacion de la sub-hipotesis 3 se refuerza (una estimacion optimista ya queda por debajo del 85 %); el resultado de tiempos no depende de la clasificacion; la historia es publica en `openspec/changes/archive/` y un evaluador puede encontrarla.
- [Conflictos de edicion con changes que tocan las mismas lineas] -> Tabla de fronteras; c-125 se aplica primero; las ediciones son por fragmento y conservan los `\label`.
- [Las citas `archivo:linea` del memo dejan de apuntar al contenido citado tras editar docstrings] -> Ediciones de igual cantidad de lineas (D12); tarea 2.2 re-verifica las citas de la Seccion 4.
- [Sin caches locales no se pueden recalcular 88/130 ni el 0,85] -> Se citan desde fuentes versionadas; la repeticion offline del determinista cubre 131/124/97; la incertidumbre de la cache FORCE-ESCALATE se declara en la Seccion 7 del memo.
- [Desborde de la primera columna de `tab:anexo_gemini_params`] -> Rotulo en prosa (D8); revisar `Overfull \hbox` en el `.log`.
- [Presupuesto de paginas excedido] -> Compensacion C1-C4 y decision final en c-136.
- [Edicion de archivos de configuracion de agentes] -> Solo con confirmacion explicita del usuario (Open Question 4); `openspec validate --strict` tras editar `config.yaml`.

## Migration Plan

1. Linea base: conteo de paginas actual, red de seguridad de los tests del clasificador y repeticion offline de la etapa deterministica (bloque 1 de `tasks.md`).
2. Checkpoint de autores y del usuario: D9, D7, D12 y D11 (`CLAUDE.md`, `config.yaml`); registrar las decisiones en `dictamen-correcciones.md`.
3. Gate 0: Seccion 3.7 del memo antes de tocar la tesis.
4. Ediciones de la tesis T01-T16 por archivo; las de D7 y D9 solo con el checkpoint aprobado.
5. Docstrings y test de caracterizacion, con red de seguridad antes y despues y comparacion de AST.
6. Documentacion para agentes y base de conocimiento.
7. Trazabilidad, regeneracion de `tesis_para_agente.md`, compilacion, referencias, conteo de paginas (C3 si corresponde) y `openspec validate --strict`.
8. **Rollback:** `git checkout <commit-previo> -- <rutas>` de los archivos editados, regenerar el render y recompilar. Sin migraciones ni re-ejecucion de la evaluacion.

## Open Questions

1. **(Bloquea T04, T12, T13 y T14)** ¿Confirman los autores que el vocabulario de c-71 y las reglas de frontera del prompt de c-72 se derivaron de casos del corpus de evaluacion? ¿Se divulga en c-125 (recomendado) o en un change dedicado c-137, bloqueando c-136 hasta aplicarlo? ¿Se agrega un analisis de sensibilidad offline (vocabulario previo a c-71 sobre la cache FORCE-ESCALATE)?
2. **(Bloquea T15)** ¿Aceptan declarar en el capitulo legal que la reasignacion de incidentes no derivados solo esta disponible por la interfaz REST (default), o prefieren abrir un change de codigo que la exponga en la interfaz web antes de la defensa?
3. ¿Se acepta editar comentarios de `App/Backend` y agregar un test en esta familia, centrada en la tesis (default: si; gobernanza LOW)?
4. ¿Autoriza el usuario editar `CLAUDE.md` y `openspec/config.yaml`, archivos de configuracion de agentes (default: si, solo las lineas del gate)?
5. ¿Puede el autor aportar el `cache_meta` de `evaluation/predicciones_calibracion.json` (fecha y version del prompt)? Si no, 88/130 queda con la salvedad de la Seccion 7 del memo.
6. Observacion fuera de alcance para el usuario: la API permite a un `usuario_final` validar (reasignar) la clasificacion de su propio incidente (`tests/test_clasificacion_visibility.py:288`). Es una decision de autorizacion (dominio CRITICAL, solo analisis) que conviene confirmar o revisar en un change propio.
