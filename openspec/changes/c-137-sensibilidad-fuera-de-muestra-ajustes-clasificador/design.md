## Context

El change atiende la mitad **analitica** de la recomendacion **A5** del dictamen `auditorias/Dictamen_Tesis_v10_v1.1.0_CONEAU_2026-10-22.md` (VEREDICTO punto 5; seccion 6, septima observacion; seccion 7, ultimo parrafo; RECOMENDACION A5; apartado "VERIFICACION CONTRA EL HISTORIAL DEL REPOSITORIO"). La mitad declarativa (reescribir `05-arquitectura.tex:78`, `06-implementacion.tex:75`, `08-discusion.tex:18` y la primera oracion de `12-anexos.tex:135`, y rotular las metricas como estimaciones dentro de la muestra) es de c-125 (D9, T04, T12, T13, T14). Motivacion completa en `proposal.md`. Este documento cita archivo y linea sobre el arbol de `ramagonzalo` al 2026-10-23 (release vigente `v1.1.1`, commit `4160d84`).

### Hechos verificados en la historia del repositorio (solo lectura)

| Hecho | Evidencia |
|---|---|
| c-71 agrego 62 patrones a `KEYWORD_MAP` (89 -> 151) y no quito ni modifico ninguno; los agrupo bajo cinco comentarios de bloque ("c-71: accesos, credenciales y politicas de seguridad del corpus.", etc.: 12 Seguridad, 20 Hardware, 17 Software, 3 Bases de Datos, 10 Sistemas) sin identificar casos | `git diff 1368fd8^ 1368fd8 -- App/Backend/app/classifiers/keywords.py` (blobs `858f1c6` -> `334a8ed`) |
| El procedimiento se describe solo en forma generica: "ampliar sinonimos/frases por sector guiado por las misclasificaciones del corpus" | `openspec/changes/archive/2026-10-06-c-71-hardening-clasificador-determinista/proposal.md:23`, `design.md:46` (D5), `tasks.md:35` |
| `keywords.py` no cambio despues de c-71; antes, su ultimo cambio fue C-27 (`c73fde4`, 2026-09-11), cuyo diseno declara el corpus real "gitignored y ausente" y define los terminos "con casos de prueba" | `git log --follow -- App/Backend/app/classifiers/keywords.py`; `openspec/changes/archive/2026-09-11-c-27-rediseno-sectores-json/design.md:26,105-111,136` |
| En el mismo commit c-71 cambio la logica: antes, `confianza = w/(w + r + 1e-6)` con cortocircuito si `>= 0,90`; sin coincidencias, el sector era la primera clave del mapa con confianza 0,0; los empates se resolvian por el orden del mapa | `git show 7925903:App/Backend/app/classifiers/deterministic.py` (`classify`), `git show 7925903:App/Backend/app/classifiers/hybrid.py:146`, `git show 7925903:App/Backend/app/config/settings.py:103` |
| Linea base documentada antes de c-71 (vocabulario y logica de la epoca, sobre los 200 casos): escalamiento 64 % (correo 66,7 %, web 73,6 %, telefono 55,6 %); exactitud estricta de los cortocircuitados 0,51 (correo 0,59, web 0,50, telefono 0,47); "pertenencia multietiqueta" de los cortocircuitados 0,76; sobreprediccion de Seguridad Informatica 126 (real 31); 119 casos sin coincidencias | `.../2026-10-06-c-71-.../proposal.md:9-13`; `tasks.md`, "Notas de desviacion" ("no-match 119->57") |
| c-72 agrego al prompt solo el bloque "REGLAS DE FRONTERA" (12 lineas); el prompt no cambio despues. Casos motivadores documentados: R002 y R038 (propuesta) y R015 (test de frontera de infraestructura) | `git diff a76851e^ a76851e -- docs/prompt_gemini.txt` (blobs `1daceb3` -> `49267f4`); `.../2026-10-07-c-72-.../proposal.md:7`; `App/Backend/tests/test_c72_prompt_boundaries.py:96-130` |
| c-74 fijo tau = 0,5166 por validacion cruzada de cinco pliegues con piso comparativo; sobre el corpus equivale a cortocircuitar los 131 casos con senal dominante; `precision_det(S) = 97/131`, `precision_gem(S) = 88/130` con la cache FORCE-ESCALATE | `docs/deterministic_calibration.md:20-79` |
| La simulacion offline con la cache FORCE-ESCALATE (mezcla 131/69) da 0,7300 (146/200) frente a 0,7350 (147/200) de la corrida oficial: la etapa Gemini acerto 49/69 con la cache y 50/69 en la corrida oficial (derivacion: 146 - 97 y 147 - 97) | `docs/deterministic_calibration.md:85-89,160-173` |
| La cache FORCE-ESCALATE es `hybrid-v2` (199 Gemini + 1 deterministica, umbral 1,0): la produjo la medicion hibrida de c-71 (tarea 4.4, corrida sobre una copia normalizada en `/tmp`), es decir el 2026-10-05, antes de que c-72 se propusiera (`4fedce8`, 2026-10-05 21:50 -0300) y se aplicara (`a76851e`, 2026-10-06 16:38 -0300). Inferencia, no prueba: su `cache_meta.generated_at` la confirmaria | `.../2026-10-07-c-74-.../tasks.md:66`; `.../2026-10-06-c-71-.../tasks.md` (0.5, 4.4 y notas); `git log --date=iso` |
| `docs/prompt_gemini_history/` no existe ni existio nunca en el historial | `git log --all` sobre esa ruta: vacio |

### Hechos verificados en el codigo y los datos

- `DeterministicClassifier.__init__` asigna `self._patterns = _compile_patterns()` (`App/Backend/app/classifiers/deterministic.py:204`) y `_score` itera `self._patterns` (`:346`): el vocabulario se puede sustituir en una instancia sin tocar el modulo ni la cache `lru_cache` de `_compile_patterns` (`:158-174`).
- El prompt se resuelve en `_resolve_prompt_path` (`gemini_classifier.py:177-193`, `settings.gemini_prompt_path`, variable `GEMINI_PROMPT_PATH`) y se carga al importar el modulo (`_PROMPT_TEMPLATE = _load_prompt()`, `:257`, con `.strip()`): cada brazo de una ablacion del prompt debe correr en un proceso propio.
- `evaluation/deterministic_measurement.py` ofrece `recolectar_observaciones` con clasificador inyectable (`:109`), `asignar_folds` (`:303`), `calibrar_comparativo_out_of_fold` (`:542`), `cargar_predicciones_cacheadas` (`:701`), `medir_hibrido_con_cache` (`:723`) y `cargar_corpus_tolerante` (`:883`). `medir_hibrido_con_cache` usa cualquier entrada de la cache sin filtrar por `etapa`: la unica entrada deterministica de la FORCE-ESCALATE se usaria como si fuera de Gemini si su caso escalara.
- `evaluation/run_evaluation.py` ofrece el gate de corrida paga (`PaidRunNotConfirmedError`, `_env_confirm_paid`, `format_cost_estimation`, `:70-110`), `evaluar_corpus` (`:137`) y `guardar_predicciones` con `cache_meta` (`:571`); `cache_meta` no registra la version del prompt (`:760-765`).
- c-126 agrega `contraste_mcnemar` (`evaluation/stats.py`) y `contraste_det_gem_en_s` (`evaluation/deterministic_measurement.py`) (D13), y `.gitattributes` con LF para el corpus (D4). c-137 los reutiliza.
- La re-ejecucion offline de la etapa vigente reproduce 131 casos cortocircuitados y 97 aciertos (c-125, "Hechos verificados en los datos"). En esta maquina no hay `pytest` en el Python global; CI instala `App/Backend/requirements.txt` y `evaluation/requirements.txt` (incluye `scipy`).
- Corpus por canal: telefono 81, correo 66, web 53 (c-126, Context). Los porcentajes documentados por c-71 implican enteros unicos: 22, 14 y 36 cortocircuitados (72 en total) y 13, 7 y 17 aciertos (37; 37/72 = 0,514); la "pertenencia" 0,76 equivale a 55/72 y, como los cortocircuitados de la epoca tenian un solo sector con coincidencias, solo puede corresponder a la definicion laxa (sector predicho dentro del conjunto de verdad).
- No hay en el repositorio ningun conjunto de incidentes de preproduccion: la unica mencion esta en `12-anexos.tex:135` y `docs/anexo_h_prompt_gemini.md:160`; `data/` solo contiene el corpus de 200 casos (JSON y CSV).

### Hechos verificados en la tesis

- `07-resultados.tex:140-165` (`subsec:calibracion`, que reescribe c-126) y `:167` (`subsec:analisis-errores`): la subseccion nueva se inserta entre ambas.
- `08-discusion.tex:18` (parrafo que c-125 reescribe con T12; termina en "cuya confirmacion exige un corpus independiente (\autoref{sec:recomendaciones})"); `:38` "El estudio presenta seis limitaciones"; `:40-50`, items "Primero" a "Sexto".
- `09-conclusiones.tex:28`: fila del objetivo especifico 6 de `tab:cumplimiento-objetivos` ("Alcanzado"; evidencia `subsec:analisis-errores` y `subsec:calibracion`). El objetivo 6 (`01-introduccion.tex:56`) es "analizar los errores de clasificacion y calibrar la confianza de las predicciones".
- `12-anexos.tex:135`: la primera oracion es de c-125 (T14); la segunda remite a `docs/prompt_gemini_history/`.
- Afirmaciones equivalentes fuera de la tesis y sin dueno en la familia: `evaluation/README.md:192-204` y `docs/anexo_h_prompt_gemini.md:160,162`.

### Restricciones

- **Numeros canonicos congelados** (`tesis-numeros-canonicos`; politica de deriva de c-126): los valores de la corrida oficial no se recalculan; todo valor de sensibilidad entra en un archivo y una seccion rotulados aparte.
- **Sin cifras inventadas:** lo no computable se declara no computable. Las ramas de redaccion de la tesis se fijan aqui antes de conocer los valores (D2).
- **Sin llamadas pagas** sin autorizacion explicita del usuario; sin contenedores.
- **TDD estricto** para todo codigo nuevo en `evaluation/` (skills `python-testing-patterns` y `pytest-coverage`, `.agents/SKILLS.md`).
- **Sin tocar** `App/`, `n8n/`, `docs/prompt_gemini.txt`, el corpus, `evaluation/report.md`, `evaluation/run_evaluation.py` ni las caches oficiales.
- **Acentuacion:** los textos DESPUES de la seccion "Objetivos de propagacion" son carga util LaTeX y llevan la acentuacion normativa del manuscrito; el resto del artefacto sigue la convencion sin tildes.

## Goals / Non-Goals

**Goals:**

- Acotar con un analisis offline y de costo cero el sesgo optimista que el vocabulario ajustado con el corpus introduce en la exactitud de la etapa deterministica (97/131) y, si hay caches, en la exactitud global y en el contraste entre etapas (0,7405 frente a 0,6769).
- Acotar el efecto de las reglas de frontera del prompt con el mejor nivel de evidencia disponible (sin costo si las caches lo permiten; ablacion controlada solo con autorizacion) o declararlo no cuantificado.
- Pre-registrar variantes, comparadores y lecturas antes de computar, y reportar todas las variantes pre-registradas cualquiera sea su resultado.
- Llevar el resultado a la tesis (resultados, limitaciones, evidencia del objetivo 6) y a los numeros canonicos con procedencia, sin alterar ningun valor canonico ni duplicar el rotulado que hacen c-125, c-126 y c-128.
- Eliminar del repositorio las afirmaciones residuales de no ajuste y la referencia a un historial del prompt inexistente.

**Non-Goals:**

- No se reescriben las cuatro afirmaciones de la tesis ni se rotula la exactitud global como dentro de la muestra (c-125, D9).
- No se re-entrena, re-calibra ni modifica el clasificador, el vocabulario, el prompt ni tau; no se re-deriva tau con el vocabulario previo (D3).
- No se recuperan ni verifican las caches (c-126, D1 y D10) ni se decide su versionado (c-126, D8).
- No se ejecuta Gemini sobre los 131 casos del conjunto `S` (contraste B5 de la hipotesis subsidiaria de eficiencia: c-128).
- No se cambia el estado de ningun objetivo ni la tabla mas alla de la evidencia del objetivo 6 (c-128); no se editan `04-marco-metodologico.tex` (c-129, c-130), el resumen ni el abstract (c-128), `10-recomendaciones.tex` (c-131) ni el parrafo introductorio de `07` (c-130).
- No se construye un conjunto de prueba nuevo ni se etiquetan datos dentro de este change salvo el bloque condicional de D11.

## Decisions

### D1 - Alcance: la mitad analitica de A5 y las afirmaciones residuales sin dueno

c-137 cuantifica; c-125 declara. Reparto:

- **c-125 (D9):** procedencia de los ajustes en `05:78`, `06:75`, `08:18` y primera oracion de `12:135`; rotulo general "estimaciones dentro de la muestra, probablemente optimistas" en `08:18`.
- **c-126:** exactitud por etapa (97/131 y 50/69 con IC) en `07`; contraste de McNemar entre etapas sobre `S` en `docs/deterministic_calibration.md` y en el memo, sin texto de tesis (D13).
- **c-128 (T10):** contraste acotado 0,7405 frente a 0,6769 en `08:10`, ya con la salvedad "proviene del corpus con que se fijo el punto de operacion".
- **c-137:** el analisis, su subseccion y tabla en `07`, la limitacion nueva, la remision desde `08:18`, la evidencia del objetivo 6, la calificacion "dentro de la muestra" **solo donde falte** al aplicar (D12) y las afirmaciones residuales: segunda oracion de `12:135`, `evaluation/README.md:192-204` y `docs/anexo_h_prompt_gemini.md:160,162` (D13).

La cuantificacion vive en un unico lugar (`subsec:sensibilidad-ajustes`); los demas pasajes solo remiten a el. **Alternativa considerada:** que c-125 absorba tambien el analisis (su D9, opcion (a)); se descarta porque mezcla un change documental de gobernanza LOW con codigo de evaluacion bajo TDD y una decision de gasto.

### D2 - Pre-registro del analisis

Este diseno fija, **antes de computar ningun valor**, las variantes (D3, D4, D8, D9), sus comparadores, el formato de reporte y las ramas de redaccion de la tesis (seccion "Objetivos de propagacion"). La fase propose no ejecuto ninguna de las variantes: solo verifico la factibilidad (artefactos en git, puntos de inyeccion, linea base documentada). En apply se reportan todas las variantes pre-registradas cualquiera sea su resultado; cualquier analisis adicional se rotula "exploratorio", queda fuera de la tesis y no reemplaza a uno pre-registrado. Los contrastes pareados se informan con el p exacto como evidencia descriptiva, sin correccion por multiplicidad, y un resultado no significativo nunca se lee como ausencia de efecto.

**Alternativa considerada:** explorar primero y elegir despues la variante a reportar; se descarta porque reintroduce, en el analisis que debe acotar un sesgo, los grados de libertad del investigador que el dictamen observa.

### D3 - Variante principal: vocabulario previo a c-71 con la logica y el punto de operacion vigentes

Configuracion `V0 + L1`: los 89 patrones previos a c-71 (blob `858f1c6`) con el clasificador vigente (senal dominante, sin ausencia ni empate, y `score_correctitud >= 0,5166`, leido de `Settings`). Es una ablacion de un solo factor: lo unico que cambia frente a la configuracion evaluada (`V1 + L1`, 131/97) es el vocabulario que c-71 incorporo a partir de los errores del corpus. Se reportan:

- **E1:** casos cortocircuitados `n_A`, aciertos estrictos `k_A`, exactitud `p_A` con IC de Wilson al 95 % (`intervalo_wilson`) y cobertura `n_A/200`, frente a 97/131 (0,7405, IC [0,6593; 0,8079]); la diferencia `0,7405 - p_A` es descriptiva, porque los conjuntos de casos difieren.
- **Descomposicion pareada:** casos cortocircuitados por ambas configuraciones (exactitud de cada vocabulario sobre los mismos casos y McNemar exacto), casos que solo cortocircuita `V1` (aportados por la ampliacion: su exactitud es la parte mas expuesta al ajuste) y, si existen, casos que solo cortocircuita `V0`. Invariante: los segmentos suman 131 casos y 97 aciertos del lado de `V1`.

**Lectura pre-registrada:** como `V0` carece tambien del conocimiento del dominio que una ampliacion hecha con datos independientes habria aportado, `0,7405 - p_A` es una **cota pesimista** (por exceso) del sesgo atribuible al vocabulario. Si `p_A >= 0,7405`, se declara que el analisis no detecta sesgo atribuible al vocabulario, sin descartarlo. **Supuesto declarado:** `V0` no se ajusto con el corpus (C-27 lo redistribuyo con el corpus ausente del repositorio); si los autores informan lo contrario, la cota pasa a ser parcial y se declara asi.

**Alternativas consideradas:** (a) `V0 + L0` como variante principal: mezcla el vocabulario con cambios de logica de c-71 y c-74 que no son ajuste in-sample (por ejemplo, no inventar un sector sin coincidencias); queda como referencia (D4). (b) Re-derivar tau con `V0` por el procedimiento comparativo de c-74: responde que configuracion se habria elegido, no cuanto se sobrestiman las metricas reportadas, y exige la cache FORCE-ESCALATE; se descarta. (c) Quitar los 62 patrones de a uno (deja-uno-fuera): multiplica comparaciones sin una regla de lectura defendible; se descarta.

### D4 - Referencia historica y control de fidelidad: vocabulario y logica previos a c-71

Configuracion `V0 + L0`: replica pura, en `evaluation/`, de la logica de `7925903` (`confianza = w/(w + r + 1e-6)`, acotada a 1; cortocircuito si `>= 0,90`; sin coincidencias, primer sector del mapa con confianza 0,0; empates por el orden del mapa, que el JSON versionado conserva). Cumple dos funciones:

1. **Control de fidelidad:** debe reproducir la linea base documentada por c-71 sobre el corpus vigente: 72 cortocircuitados (64 % de escalamiento; por canal 22, 14 y 36), 37 aciertos (0,51; por canal 13, 7 y 17), 55/72 en la definicion laxa (0,76), 119 casos sin coincidencias y 126 predicciones de Seguridad Informatica sobre los 200 casos. Un test de caracterizacion lo verifica; si falla, el apply se **detiene**, se revisan la replica (contra `git show 7925903:...`) y la procedencia del corpus (se versiono recien el 2026-10-09, `8f7e6ec`, de modo que la copia local que midio c-71 el 2026-10-05 no es verificable desde git; c-73 no modifico el corpus y c-77 solo cambio tiempos) y la discrepancia se registra con su causa. **Nunca** se ajusta la replica a los datos.
2. **Referencia:** la fila "vocabulario y logica previos" de la tabla de la tesis describe el punto de partida antes de cualquier ajuste con el corpus; no se lee como cota del sesgo porque incluye cambios de logica legitimos.

Ademas, la configuracion evaluada se reproduce por el mismo camino (`V1 + L1` mediante el adaptador de D5): 131 casos y 97 aciertos, caso por caso identicos al clasificador de produccion. Sin esa reproduccion no se reporta ninguna variante.

**Alternativa considerada:** ejecutar el codigo historico desde git; se descarta porque exige reconstruir los modulos `app` de la epoca (configuracion, esquemas, clase base) y no es reproducible en un clon superficial. La replica cita las lineas de origen y la valida la reproduccion de la linea base documentada.

### D5 - Vocabulario inyectado en una instancia del clasificador de produccion, sin tocar `App/`

`clasificador_con_vocabulario(mapa)` construye un `DeterministicClassifier` real (con `GEMINI_API_KEY` ficticio, como los tests existentes de `evaluation/`) y reemplaza el atributo de instancia `_patterns` por los patrones de `mapa` compilados con los mismos indicadores que `_compile_patterns` (`re.IGNORECASE | re.UNICODE`). Asi la logica `L1` (`_score`, `_confidence`, `extraer_features`, `score_correctitud`) es exactamente la de produccion y solo cambia el vocabulario. Guardas por test: (a) con `KEYWORD_MAP` el adaptador reproduce caso por caso al clasificador de produccion (sector, confianza, score, ausencia y empate); (b) una instancia nueva de produccion sigue usando `V1` despues de crear un adaptador con `V0` (sin estado global alterado); (c) si `DeterministicClassifier` deja de exponer `_patterns`, el test falla con un mensaje explicito (acoplamiento a un atributo privado declarado y vigilado).

**Alternativas consideradas:** (a) agregar al constructor un parametro de vocabulario: toca `App/Backend`, que c-125 tambien edita (docstrings), y altera la superficie de produccion por una necesidad de evaluacion; se descarta. (b) replicar `L1` en `evaluation/`: duplica la logica de produccion con riesgo de deriva silenciosa; se descarta.

### D6 - Artefactos historicos versionados con procedencia

En `evaluation/data/sensibilidad_ajustes/`:

- `keywords_pre_c71.json`: `KEYWORD_MAP` del blob `858f1c6` (`7925903:App/Backend/app/classifiers/keywords.py`), extraido con `keyword_map_desde_fuente(texto)`, funcion pura que analiza el fuente con `ast` y evalua solo el literal de `KEYWORD_MAP` (no ejecuta el modulo historico, que importa `app.constants`). Conserva el orden de claves (lo exige el desempate de `L0`).
- `prompt_gemini_pre_c72.txt`: contenido del blob `1daceb3` (`a76851e^:docs/prompt_gemini.txt`).
- `procedencia.json`: por archivo, commit de origen, ruta, blob, fecha, comando de extraccion y SHA-256 del archivo versionado.

`.gitattributes` (creado por c-126) recibe la regla `evaluation/data/sensibilidad_ajustes/* text eol=lf`, de modo que los SHA-256 coinciden en Windows y Linux. Tests: (a) SHA-256 de cada archivo igual al de `procedencia.json`; (b) estructura: cinco claves canonicas en el mismo orden que `V1`, cada lista de `V0` contenida en la de `V1`, 62 patrones de diferencia; (c) el prompt previo es el vigente sin el bloque "REGLAS DE FRONTERA" (unica diferencia); (d) con historial git disponible, igualdad con los blobs (`skipif` en clones superficiales, como CI).

**Alternativas consideradas:** (a) leer los blobs con `git show` en tiempo de ejecucion: falla en clones superficiales y no es una funcion pura; se descarta. (b) crear `docs/prompt_gemini_history/` para que la frase del Anexo H resulte verdadera: adapta el repositorio al texto en lugar de corregir el texto y duplica el historial git; se descarta (D13).

### D7 - Variante por pliegues: no factible, y por que

La variante sugerida por el dictamen ("reconstruyendo el vocabulario por pliegues") exige saber, para cada patron agregado por c-71, que casos del corpus lo motivaron, de modo de incluirlo solo en los pliegues que no contienen esos casos. El repositorio no lo registra: el diff solo trae cinco comentarios de bloque por sector; la propuesta, el diseno y las tareas de c-71 describen el procedimiento en forma generica; el mensaje del commit tampoco lo detalla, y no se versiono el registro de la revision de errores. Cualquier asignacion por pliegues requeriria una regla de atribucion no verificable (por ejemplo, atribuir cada patron a los casos donde coincide con un sector verdadero), cuyo resultado dependeria de la regla elegida: un grado de libertad que D2 excluye. Se declara **no factible** en el reporte (con este motivo) y en una oracion de la tesis; la Seccion 7 del memo lo registra como decision no resoluble, reversible si los autores aportan la atribucion por patron.

**Alternativa considerada:** aproximacion por coincidencia, rotulada como exploratoria; se descarta como estimacion (no es la variante del dictamen y su supuesto no se puede contrastar) y queda como pregunta abierta al usuario (Open Question 4).

### D8 - Sensibilidad global y del contraste entre etapas con la cache FORCE-ESCALATE (condicional, sin costo)

Solo si c-126 recupera y verifica la cache FORCE-ESCALATE (su tarea 3.3):

- **E3, exactitud global con Gemini fijo:** simulacion del pipeline con `V0 + L1` y con `V1 + L1`, usando para todo caso escalado la prediccion `gemini` de la FORCE-ESCALATE (una sola fuente para ambos lados). Las entradas con `etapa != "gemini"` se tratan como ausentes; un caso que necesite una prediccion ausente se excluye de **ambos** lados y se lista. Se reportan aciertos de cada configuracion sobre el mismo conjunto de casos (lado `V1`: 146/200 documentado, o 146 menos lo excluido) y McNemar exacto (`contraste_mcnemar` de c-126). Es la lectura del efecto del vocabulario sobre la metrica global.
- **E4, piso comparativo con `V0`:** `contraste_det_gem_en_s` de c-126 aplicado a las observaciones de `V0`: exactitud de `V0` y de Gemini sobre los mismos casos que `V0` cortocircuita, con McNemar. Se lee frente al contraste en muestra 97/131 frente a 88/130: si con un vocabulario no ajustado la etapa de reglas deja de superar a Gemini, la ventaja que sostiene el punto de operacion y la hipotesis subsidiaria de eficiencia depende del ajuste; se comunica a c-128.

Sin la cache, ambas salidas se declaran "no computable con los artefactos disponibles" y la columna de exactitud global se omite de la tabla de la tesis.

**Alternativa considerada:** usar las predicciones de la corrida oficial para los 69 casos y la FORCE-ESCALATE solo para los casos que `V0` escala de mas; se descarta porque mezcla dos corridas en un mismo lado del contraste.

### D9 - Sensibilidad del prompt: tres niveles de evidencia y checkpoint HIGH

Las reglas de frontera solo influyeron en los 69 casos que la configuracion evaluada escala a Gemini (`S` lo resuelve la etapa de reglas). Niveles, en orden de precedencia para la tesis (c > b > a > ninguno); todos los disponibles se reportan en el archivo:

- **Nivel a (sin costo; requiere la cache oficial):** exactitud de la etapa Gemini sobre los 69 casos con y sin los casos motivadores documentados (R002, R038, R015) que figuren entre ellos. Si ninguno esta entre los 69 (la etapa de reglas pudo resolverlos), se declara "no aplicable". Es una cota debil: solo retira la influencia directa de los casos documentados.
- **Nivel b (sin costo; requiere ambas caches y `cache_meta.generated_at` de la FORCE-ESCALATE):** la version del prompt de la FORCE-ESCALATE se clasifica por fecha: "previa confirmada" si es anterior a la propuesta de c-72 (`4fedce8`, 2026-10-06T00:50:05Z); "probablemente previa" si es anterior a su aplicacion (`a76851e`, 2026-10-06T19:38:20Z); "posterior" en otro caso; "indeterminada" sin fecha. Solo "previa confirmada" habilita el nivel b en la tesis: comparacion pareada de la FORCE-ESCALATE frente a la corrida oficial sobre los 69 casos (se esperan los agregados derivados 49/69 y 50/69) con McNemar exacto, declarando que la diferencia confunde el efecto de las reglas con la variabilidad entre corridas (temperatura 0,3). La clasificacion se comunica a c-128, porque 88/130 provendria de un prompt distinto del evaluado.
- **Nivel c (pago; solo con autorizacion explicita del usuario):** ablacion controlada en dos brazos, en procesos separados y en una misma sesion: control (prompt vigente, `docs/prompt_gemini.txt`) y ablacion (`prompt_gemini_pre_c72.txt` via `GEMINI_PROMPT_PATH`), sobre los mismos 69 casos, seleccionados offline como los que `V1 + L1` no cortocircuita (deben ser 69 y, con la cache oficial, coincidir con los de la etapa Gemini oficial). Cada brazo corre `HybridClassifier` mediante `evaluar_corpus`, verifica antes de la primera llamada que el SHA-256 del prompt cargado (`_PROMPT_TEMPLATE`, texto con `.strip()`) es el esperado, evalua el gate de corrida paga antes de construir el clasificador, imprime la estimacion de costo y escribe `evaluation/predicciones_sensibilidad_prompt_vigente.json` y `..._sin_reglas.json` con `cache_meta` ampliado (brazo, SHA-256 y origen del prompt, modelo, temperatura, version del clasificador, hash del corpus, casos, fecha, fallbacks). Un fallback cuenta como error y se reporta. Se reportan `k_P1/69` frente a `k_P0/69` con McNemar exacto y, con la cache oficial, la deriva del brazo control frente a la corrida oficial (variabilidad entre corridas). Costo: 138 invocaciones; la corrida oficial de 69 costo aprox. 0,0138 USD (`.../2026-10-07-c-74-.../tasks.md:51`), de modo que el total ronda 0,03 USD, con un tope conservador de 0,10 USD segun los precios del capitulo 8.
- **Ninguno:** la tesis declara que el efecto de las reglas de frontera, limitado a los 69 casos de la etapa Gemini, no se cuantifico.

**Alternativas consideradas:** (a) ejecutar el prompt previo sobre `S` (131 casos): el prompt no intervino alli en la configuracion evaluada; el contraste de Gemini sobre `S` es el B5 de c-128; se descarta. (b) un solo brazo comparado con 50/69 oficial: confunde el efecto del prompt con la variabilidad entre corridas y con la deriva temporal del proveedor; se descarta a favor del control en la misma sesion. (c) varias repeticiones por brazo para promediar la temperatura: multiplica el costo; queda a decision del usuario. (d) sesion paga unificada con un eventual B5 de c-128 (ambos prompts sobre los 200 casos): mas eficiente si ambos se aprueban; Open Question 1.

### D10 - Salidas separadas, determinismo y politica de deriva

- `python -m evaluation.sensibilidad_ajustes` (offline, sin Gemini) escribe solo `evaluation/report_sensibilidad_ajustes.md`, con secciones: procedencia (commit, blobs, SHA-256 del corpus y de los artefactos, tau y pesos leidos de `Settings`); configuracion evaluada reproducida; variante principal y descomposicion; referencia historica con la tabla "documentado frente a reproducido"; variante por pliegues (no factible, con motivo); sensibilidad global y piso comparativo (o "no computable"); prompt por nivel (o "no computado"); y, si existiera, un apartado rotulado "exploratorio". Formato numerico del reporte vigente (cuatro decimales, punto decimal).
- Las secciones offline no llevan marcas de tiempo: dos corridas sobre el mismo commit y el mismo corpus producen un archivo identico byte a byte (test).
- Ninguna ruta del modulo escribe `evaluation/report.md`, `evaluation/predicciones.json` ni `evaluation/predicciones_calibracion.json` (test con rutas temporales y verificacion de no escritura).
- Las salidas de la corrida paga se ignoran en git salvo que el usuario haya decidido versionar las caches en c-126 (D8); en ese caso heredan la regla LF.
- Ningun valor de sensibilidad reemplaza un valor canonico (D14; requisito de `tesis-numeros-canonicos`).

**Alternativa considerada:** agregar secciones a `evaluation/report.md` o a `docs/deterministic_calibration.md`; se descarta porque ambos documentan la corrida oficial y la calibracion de c-74, y la politica de deriva de c-126 exige archivos rotulados aparte.

### D11 - Conjunto fuera de muestra genuino: checkpoint sobre los incidentes de preproduccion

El Anexo H menciona "aproximadamente 100 incidentes representativos en entornos de preproduccion"; el repositorio no los contiene. Desenlaces del checkpoint con el usuario:

- **No existen o no se localizan:** la limitacion de la tesis declara que no se dispuso de un corpus independiente; la Seccion 7 del memo lo registra; c-131 conserva la validacion sobre un corpus independiente como trabajo futuro.
- **Existen sin pseudonimizar o sin etiquetar en los cinco sectores:** fuera de alcance de c-137. Pseudonimizar (Ley 25.326) y etiquetar con el protocolo del corpus (dos analistas, kappa) exige un change propio de gobernanza HIGH; se recomienda abrirlo si los plazos lo permiten.
- **Existen pseudonimizados y etiquetados en los cinco sectores:** bloque condicional 9 de `tasks.md`: verificacion de ausencia de datos personales y aprobacion explicita antes de versionarlos; `V0` frente a `V1` con `L1` sobre ese conjunto (offline, sin costo) y, solo con autorizacion, los dos brazos del prompt. Se reportan como **prueba externa respecto de los ajustes de c-71 y c-72**, no como validacion fuera de muestra del clasificador completo: segun el Anexo H, el prompt base se ajusto con esos incidentes, y la version vigente de `08:18` afirma que el filtro se construyo con incidentes ajenos al corpus, que podrian ser esos mismos.

**Alternativa considerada:** tratarlo como validacion fuera de muestra del sistema completo; se descarta por la razon anterior.

### D12 - Presentacion en la tesis y calificacion "dentro de la muestra" sin duplicar

- **Ubicacion:** `\subsection{Sensibilidad al ajuste del clasificador con el corpus}\label{subsec:sensibilidad-ajustes}` en `07-resultados.tex`, entre `subsec:calibracion` (donde c-126 reporta 97/131 con su IC) y `subsec:analisis-errores`. Un parrafo de metodo, la tabla `tab:sensibilidad-ajustes` (`\footnotesize`; filas: configuracion evaluada, vocabulario previo con logica vigente, vocabulario y logica previos; columnas: casos resueltos por la etapa, exactitud de la etapa con IC 95 % y, solo si E3 es computable, exactitud global con Gemini fijo) y un parrafo de lectura con las ramas pre-registradas (T01). El formato numerico es el de `tab:exactitud-etapa-canal` de c-126.
- **Lenguaje:** "cota pesimista", "compatible con", "no detecta ... sin descartarlo"; nunca "demuestra la ausencia de sesgo" ni "fuera de la muestra" referido a metricas del corpus.
- **Calificacion sin duplicar:** al aplicar, se listan con `grep` las apariciones de `0,7405`, `97/131`, `97 de 131`, `0,6769` y `88/130` en `sections/*.tex`. Cada una debe estar en una oracion o parrafo que la califique como estimacion dentro de la muestra o que remita a `subsec:sensibilidad-ajustes`. c-137 agrega una calificacion minima **solo donde falte** (huecos esperados: T05 de c-125 en `05:80`, la primera mencion de c-126 en `07` y la oracion de c-126 en `09:37`); `08:10` lo escribe c-128 despues y recibe la consigna en la tabla de fronteras.
- **Metodo en el capitulo 4:** no se edita `04-marco-metodologico.tex`; el metodo se enuncia en la propia subseccion, como el analisis de sensibilidad de tiempos (`07:62`).

**Alternativas consideradas:** (a) una quinta amenaza en `subsec:amenazas-validez`: duplica la limitacion y esa subseccion es de c-129 y c-130; se descarta. (b) solo prosa, sin tabla: ahorra ~0,2 paginas pero tres configuraciones con intervalos se leen mal en linea; queda como compensacion. (c) analisis en un anexo con resumen en `07`: solo como compensacion C3 de D15.

### D13 - Limitaciones, objetivo 6 y afirmaciones residuales del repositorio

- **Limitacion:** item nuevo al final de `subsec:limitaciones-estudio` con el ordinal siguiente al ultimo existente; el cardinal de la oracion introductoria (`08:38`) se actualiza a la cantidad de items. La regla es robusta al orden: c-128 (T18) agrega otro item despues y debe partir del cardinal vigente.
- **Remision en `08:18`:** una oracion al final del parrafo que reescribe c-125 (T12) remite a la subseccion; no repite la declaracion de procedencia.
- **Objetivo 6:** la celda de evidencia de `09-conclusiones.tex:28` agrega la referencia y la salvedad; el estado ("Alcanzado") no lo cambia c-137, porque los estados son de c-128 (B4). Recomendacion para c-128 y los autores: conservar "Alcanzado", porque el objetivo consiste en realizar los analisis de errores y de calibracion (ahora con su sensibilidad) y la naturaleza dentro de la muestra es una limitacion de las metricas, no del analisis (Open Question 3).
- **Anexo H (`12:135`, segunda oracion) y `docs/anexo_h_prompt_gemini.md:162`:** el historial del prompt se ubica en el historial de versiones de `docs/prompt_gemini.txt`; si el prompt se evaluo (niveles b o c), se agrega la remision al analisis.
- **`evaluation/README.md:192-204` y `docs/anexo_h_prompt_gemini.md:160`:** se reemplaza la afirmacion de no ajuste por la procedencia factual (c-71, c-72, c-74, con commits), la regla vigente (el corpus de evaluacion solo para diagnostico; todo ajuste nuevo se mide sobre datos separados) y la remision al modulo de sensibilidad. La primera oracion de `docs/anexo_h_prompt_gemini.md:160` replica T14 de c-125.

**Alternativas consideradas:** (a) integrar la limitacion en el primer item (tamano de muestra): mezcla dos limitaciones distintas; se descarta. (b) cambiar el estado del objetivo 6: excede a c-137; queda como consigna a c-128. (c) dejar las afirmaciones residuales a c-136: c-136 no edita `evaluation/` ni `docs/` de proyecto; quedarian sin dueno.

### D14 - Numeros canonicos

- Seccion nueva "3.x Sensibilidad frente al ajuste del clasificador con el corpus (c-137)", con `x` = la siguiente libre al aplicar (c-125 y c-126 declaran ambos una "Seccion 3.7": choque que debe resolver el orquestador). Filas: E1 (`n_A`, `k_A`, `p_A`, IC, cobertura), descomposicion pareada, control de fidelidad (documentado frente a reproducido), E3 y E4 (o "no computable"), prompt por nivel (o "no computado") y, si aplica, el conjunto de preproduccion. Procedencia `evaluation/report_sensibilidad_ajustes.md:<linea>` (o derivacion explicita, como 49/69 = 146 - 97 desde `docs/deterministic_calibration.md:89` y `:40`), estado `vigente` como valor de sensibilidad o `condicional` mientras un checkpoint siga abierto, y rotulo "sensibilidad: no reemplaza valores canonicos".
- Notas cruzadas en las filas de `97/131` y de `0,7405`/`0,6769` (seccion de c-125): "estimacion dentro de la muestra; ver seccion 3.x".
- Seccion 7 ("Decisiones no resolubles"): variante por pliegues no factible (reversible con la atribucion por patron); version del prompt de la FORCE-ESCALATE (clasificacion de D9 o "indeterminada"); conjunto de preproduccion (desenlace de D11).
- Ningun valor `vigente` previo cambia (`git diff` del memo restringido a lineas agregadas y notas).

### D15 - Presupuesto de paginas

Conteo de palabras sobre los textos DESPUES de la seccion siguiente con valores ficticios de longitud realista: unas 290 palabras en la rama minima (sin caches ni corrida paga: subseccion de ~175, limitacion de ~75 y remisiones de ~20 a 40) y unas 370 en la maxima (todas las salidas computables: subseccion de ~230, limitacion de ~85 y remisiones de ~40). Con la densidad medida por c-125 (~370 palabras por pagina con doble interlineado) y la tabla (~0,25 a 0,3 pagina con titulo y fuente), el cuerpo crece **+1,0 paginas** en la rama minima y **+1,4** en la maxima (central **+1,2**); el anexo suma una o dos lineas. Compensaciones, en orden: C1, sin E3 la columna global desaparece (automatica); C2, la fila historica pasa a nota de la tabla (-0,05); C3, si la regla de G0 limita el cuerpo sin anexos, la tabla se muda a un anexo y en `07` queda el parrafo de lectura (-0,3 en el cuerpo); C4, la limitacion en dos oraciones (-0,05). No se elimina contenido cientifico; el conteo y el exceso, si lo hay, se registran para c-136.

## Objetivos de propagacion (ANTES -> DESPUES)

Las rutas `sections/` se resuelven desde `docs/Tesis/v10 (IA)/paper/`. Los textos se escriben antes de conocer los valores (D2): `<<...>>` marca un marcador que se reemplaza en apply con el valor registrado en el memo (D14), y las alternativas entre corchetes con rotulo (`[Rama A]`, `[Nivel c]`, etc.) se eligen por la regla indicada, nunca por preferencia. Marcadores: `<<N_A>>`, `<<K_A>>`, `<<P_A>>`, `<<IC_A>>` (variante principal, E1); `<<D_A>>` = (0,7405 - `<<P_A>>`) x 100 con un decimal; `<<N_B>>`, `<<P_B>>`, `<<IC_B>>` (referencia historica); `<<G_REF>>`, `<<G_A>>`, `<<N_G>>`, `<<P_G>>` (E3); `<<K_P0>>`, `<<K_P1>>`, `<<P_P>>` (nivel c); `<<K_FE>>`, `<<P_FE>>` (nivel b); `<<K_EX>>`, `<<N_EX>>` (nivel a). Los p se escriben con coma decimal y tres decimales, o "\(p < 0{,}001\)". Las ramas: **A** si `<<P_A>>` < 0,7405; **B** en otro caso. El nivel del prompt es el mayor disponible (c > b > a > ninguno, D9).

**T01** `07-resultados.tex`, subseccion nueva inmediatamente antes de `\subsection{Análisis de errores y casos límite}\label{subsec:analisis-errores}` (D12).

```latex
% ANTES
(no existe)
% DESPUES
\subsection{Sensibilidad al ajuste del clasificador con el corpus}\label{subsec:sensibilidad-ajustes}

Las métricas de este capítulo son estimaciones dentro de la muestra (\autoref{subsec:interpretacion-resultados}). Para acotar el sesgo atribuible al vocabulario del filtro, ampliado a partir de errores observados en el corpus, se repitió sin invocar al modelo la etapa determinística con el vocabulario previo a esa ampliación (89 de los 151 patrones), conservando la lógica de decisión y el punto de operación evaluados; con la lógica de decisión de entonces, la repetición [Fiel: reprodujo | No fiel: no reprodujo exactamente (véase la nota de la tabla)] la medición registrada antes del ajuste. La reconstrucción del vocabulario por pliegues no es factible, porque el repositorio no registra qué casos motivaron cada patrón. La Tabla~\ref{tab:sensibilidad-ajustes} resume los resultados.

\begin{table}[htbp]
\centering
\caption{Sensibilidad de la exactitud al vocabulario ajustado con el corpus}
\label{tab:sensibilidad-ajustes}
\footnotesize
\begin{tabular}{@{}l c c c@{}}
\toprule
\textbf{Filtro determinístico} & \textbf{Casos} & \textbf{Exactitud (IC 95~\%)} & \textbf{Global\textsuperscript{a}} \\
\midrule
Evaluado (vocabulario ampliado) & 131 & 0,7405 [0,6593; 0,8079] & <<G_REF>>/<<N_G>> \\
Vocabulario previo, lógica vigente & <<N_A>> & <<P_A>> [<<IC_A>>] & <<G_A>>/<<N_G>> \\
Vocabulario y lógica previos & <<N_B>> & <<P_B>> [<<IC_B>>] & --- \\
\bottomrule
\end{tabular}
\par\smallskip
{\footnotesize\textit{Fuente:} elaboración propia a partir del corpus de validación (\(n = 200\)) y de \texttt{evaluation/report\_sensibilidad\_ajustes.md}. Casos y exactitud de la etapa determinística. \textsuperscript{a}Aciertos con las predicciones de la etapa Gemini fijas (caché de calibración); la exactitud global oficial es 147/200.\par}
\end{table}

[Rama A: Sin la ampliación, la exactitud de la etapa determinística baja de 0,7405 a <<P_A>> sobre <<N_A>> casos: la diferencia, de <<D_A>> puntos, es una cota pesimista del sesgo atribuible al vocabulario, porque el vocabulario previo carece también del conocimiento del dominio que una ampliación hecha con datos independientes habría aportado. | Rama B: Sin la ampliación, la exactitud de la etapa determinística sobre <<N_A>> casos es de <<P_A>>, no inferior a 0,7405: el análisis no detecta un sesgo atribuible al vocabulario, sin descartarlo, porque los conjuntos de casos comparados difieren.] [Con E3: Con las predicciones de la etapa Gemini fijas, la exactitud global pasa de <<G_REF>> a <<G_A>> aciertos sobre <<N_G>> casos (McNemar exacto, \(p = <<P_G>>\)).] [Nivel c: En los 69 casos de la etapa Gemini, el prompt sin las reglas de frontera acertó <<K_P1>> frente a <<K_P0>> del prompt evaluado, ejecutados en una misma sesión (McNemar exacto, \(p = <<P_P>>\)). | Nivel b: En los 69 casos de la etapa Gemini, una corrida anterior a las reglas de frontera acertó <<K_FE>> frente a 50 de la corrida oficial (McNemar exacto, \(p = <<P_FE>>\)), diferencia que confunde el efecto de las reglas con la variabilidad entre corridas. | Nivel a: El efecto de las reglas de frontera del prompt, limitado a los 69 casos de la etapa Gemini, no se cuantificó; sin los casos que las motivaron, esa etapa acertó <<K_EX>> de <<N_EX>>. | Ninguno: El efecto de las reglas de frontera del prompt, limitado a los 69 casos de la etapa Gemini, no se cuantificó.] Ningún valor canónico cambia: el análisis estima la sensibilidad de las métricas y no sustituye la medición del sistema evaluado.
```

Sin E3, la tabla pierde la cuarta columna (`l c c`) y la nota "a"; con "No fiel", la nota de la tabla agrega en una oracion la discrepancia registrada en el memo. La fila "Evaluado" usa el IC canonico de c-126; el formato final de los intervalos sigue el de `tab:exactitud-etapa-canal`.

**T02** `07-resultados.tex`, primera oracion de `subsec:calibracion` que reporta la exactitud de la etapa deterministica (redaccion de c-126, tarea 9.5); solo si no esta calificada.

```latex
% ANTES (fragmento de c-126, a confirmar al aplicar)
... 0,7405 [IC de c-126] ...
% DESPUES (inmediatamente despues del intervalo)
... 0,7405 [IC de c-126], estimación dentro de la muestra (\autoref{subsec:sensibilidad-ajustes}) ...
```

**T03** `05-arquitectura.tex:80`, oracion de procedencia del punto de operacion (texto T05 de c-125); solo si no esta calificada.

```latex
% ANTES
... sin que la precisión del filtro fuera inferior a la del modelo sobre el conjunto que resuelve (0,7405 frente a 0,6769), y equivale a resolver los 131 casos con señal dominante.
% DESPUES
... sin que la precisión del filtro fuera inferior a la del modelo sobre el conjunto que resuelve (0,7405 frente a 0,6769, ambas estimadas dentro de la muestra; \autoref{subsec:sensibilidad-ajustes}), y equivale a resolver los 131 casos con señal dominante.
```

**T04** `08-discusion.tex:18`, final del parrafo que reescribe c-125 (T12).

```latex
% ANTES (final de T12 de c-125)
... cuya confirmación exige un corpus independiente (\autoref{sec:recomendaciones}).
% DESPUES
... cuya confirmación exige un corpus independiente (\autoref{sec:recomendaciones}). La \autoref{subsec:sensibilidad-ajustes} acota la parte de ese sesgo atribuible al vocabulario[Nivel b o c:  y a las reglas del prompt].
```

**T05** `08-discusion.tex`, `subsec:limitaciones-estudio`: cardinal de `:38` e item nuevo al final de la lista (D13).

```latex
% ANTES (:38)
El estudio presenta seis limitaciones que deben considerarse al interpretar los hallazgos y al planificar replicaciones futuras.
% DESPUES (:38; el cardinal es la cantidad de items tras la insercion)
El estudio presenta siete limitaciones que deben considerarse al interpretar los hallazgos y al planificar replicaciones futuras.
% DESPUES (item nuevo, despues del ultimo; ordinal siguiente)
Séptimo, el vocabulario del filtro determinístico y las reglas de frontera del prompt se ajustaron con errores observados en el mismo corpus de evaluación, de modo que las métricas de clasificación son estimaciones dentro de la muestra. [Rama A: Sin ese vocabulario, la exactitud de la etapa determinística baja de 0,7405 a <<P_A>>, cota pesimista del sesgo atribuible a él | Rama B: Sin ese vocabulario, la exactitud de la etapa determinística no baja (<<P_A>>), lo que no descarta el sesgo][Nivel c: , y sin sus reglas de frontera el prompt acertó <<K_P1>> de 69 casos frente a <<K_P0>> | Nivel b: , y una corrida anterior a las reglas de frontera acertó <<K_FE>> de 69 casos frente a 50 | Nivel a o ninguno: , y el efecto de las reglas del prompt no se cuantificó] (\autoref{subsec:sensibilidad-ajustes}). Solo un corpus independiente permitiría estimar el desempeño fuera de la muestra.
```

**T06** `09-conclusiones.tex:28`, celda de evidencia del objetivo especifico 6 (D13; el estado no cambia).

```latex
% ANTES
Objetivo específico 6: errores/calibración & Alcanzado & \autoref{subsec:analisis-errores}; \autoref{subsec:calibracion} \\
% DESPUES
Objetivo específico 6: errores/calibración & Alcanzado & \autoref{subsec:analisis-errores}; \autoref{subsec:calibracion}; métricas dentro de la muestra, sensibilidad en \autoref{subsec:sensibilidad-ajustes} \\
```

**T07** `09-conclusiones.tex:37`, oracion de c-126 con la exactitud por etapa (tarea 10.4 de c-126); solo si no esta calificada: agregar ", estimada dentro de la muestra," junto al valor de la etapa deterministica.

**T08** `12-anexos.tex:135`, segunda oracion (la primera es T14 de c-125).

```latex
% ANTES
Las versiones históricas del prompt se conservan en el repositorio bajo \texttt{docs/prompt\_gemini\_history/} para auditoría y eventual reversión.
% DESPUES
Las versiones históricas del prompt se conservan en el historial de versiones del repositorio (archivo \texttt{docs/prompt\_gemini.txt}) para auditoría y eventual reversión[Nivel b o c: ; la versión previa a las reglas de frontera se emplea en la \autoref{subsec:sensibilidad-ajustes}].
```

**R01** `evaluation/README.md:192-204` (documentacion del framework; carga util con acentos).

```markdown
<!-- ANTES -->
## Advertencia Metodológica (Anti Data Leakage — §8.1)

> **El clasificador NO fue ajustado sobre el corpus de evaluación.**

Este framework solo **evalúa** el clasificador. Las reglas determinísticas
(keywords) y el prompt de Gemini fueron definidos antes de la recolección del
corpus final. [...] medí el impacto sobre datos separados.

<!-- DESPUES -->
## Advertencia Metodológica (procedencia de los ajustes y sensibilidad)

> **Parte del clasificador evaluado se ajustó con el corpus de evaluación.**

El historial del repositorio registra tres ajustes hechos con
`data/corpus_evaluacion_pseudonimizado.json` antes de la corrida oficial del
2026-10-07: el vocabulario del filtro determinístico se amplió a partir de sus
errores (c-71, commit `1368fd8`); las reglas de frontera del prompt se
redactaron a partir de casos del corpus (c-72, commit `a76851e`; R002 y R038);
y el punto de operación del cortocircuito se derivó sobre el corpus por
validación cruzada fuera de muestra (c-74, commit `d6bb474`;
`docs/deterministic_calibration.md`). Las métricas de `report.md` son, por lo
tanto, estimaciones dentro de la muestra. `python -m evaluation.sensibilidad_ajustes`
(sin Gemini) acota la parte atribuible al vocabulario en
`report_sensibilidad_ajustes.md`.

Regla vigente: el framework solo **evalúa**; el corpus de evaluación se usa
**solo para diagnóstico** y todo ajuste posterior del clasificador se mide
sobre datos separados y declara su procedencia.
```

**R02** `docs/anexo_h_prompt_gemini.md:160` y `:162`.

```markdown
<!-- ANTES (:160) -->
El prompt ha sido validado y ajustado iterativamente sobre un conjunto de ~100 incidentes representativos en entornos de preproducción, **sin exposición al corpus de validación utilizado en el estudio**.
<!-- DESPUES (:160) -->
El prompt ha sido validado y ajustado iterativamente sobre un conjunto de ~100 incidentes representativos en entornos de preproducción; las reglas de frontera de la versión evaluada se incorporaron a partir de errores observados en el corpus de validación (c-72).
<!-- ANTES (:162) -->
Versiones históricas del prompt se mantienen en el repositorio bajo `docs/prompt_gemini_history/` para auditoría y posible rollback.
<!-- DESPUES (:162) -->
Las versiones históricas del prompt se conservan en el historial de versiones de `docs/prompt_gemini.txt` (`git log -- docs/prompt_gemini.txt`); la versión previa a las reglas de frontera está versionada, con su procedencia, en `evaluation/data/sensibilidad_ajustes/prompt_gemini_pre_c72.txt`.
```

**Revisados sin cambios:** `04-marco-metodologico.tex` (D12); `08-discusion.tex:10` (c-128, T10; consigna en la tabla de fronteras); `11-aspectos-legales.tex:34` (T15 de c-125 ya califica el criterio como "estimada sobre el corpus de validación"); `00-resumen.tex` (c-128); `docs/deterministic_calibration.md` (documenta tau OOF, que sigue siendo cierto).

## Fronteras con la familia de changes

| Superficie | Dueno | Consigna |
|---|---|---|
| `05:78`, `06:75`, `08:18`, primera oracion de `12:135` (procedencia declarada) | c-125 (D9) | c-137 no los reescribe: agrega la remision al final de `08:18` (T04) y corrige solo la segunda oracion de `12:135` (T08). Si el checkpoint D9 de c-125 no confirma los hechos, c-137 se re-evalua antes de tocar la tesis. |
| `05:80`, comparacion 0,7405 frente a 0,6769 (T05 de c-125) | c-125 | c-137 agrega la calificacion solo si falta (T03). Recomendable que c-125 la incluya en T05. |
| Exactitud por etapa en `07` y `09:37`; `tab:exactitud-etapa-canal`; `tab:bandas` | c-126 | c-137 agrega una calificacion minima solo donde falte (T02, T07); no edita tablas de c-126. |
| `contraste_mcnemar`, `contraste_det_gem_en_s`, `.gitattributes`, recuperacion y verificacion de caches | c-126 (D1, D4, D10, D13) | c-137 los reutiliza; sin caches verificadas, sus salidas condicionales se declaran no computables. |
| `08:10`, contraste acotado de la hipotesis subsidiaria de eficiencia | c-128 (T10) | Debe calificar 0,7405 frente a 0,6769 como estimaciones dentro de la muestra con remision a `subsec:sensibilidad-ajustes`, y considerar E4 (piso comparativo con `V0`) y la version del prompt de la FORCE-ESCALATE (D9) al rotular la subsidiaria. |
| Estados de `tab:cumplimiento-objetivos` | c-128 (B4) | c-137 solo agrega evidencia en la fila del objetivo 6 (T06); recomienda conservar "Alcanzado". |
| Lista de `subsec:limitaciones-estudio` | c-137 (item nuevo), c-128 (T18, item siguiente), c-127 (T6, texto del sexto), c-130 (fecha del cuarto) | El cardinal de `08:38` iguala siempre la cantidad de items; quien agrega un item lo actualiza (c-128 parte de "siete" si aplica despues). |
| `subsec:balance-neto` | c-127 | Puede usar E3 como escenario de sensibilidad del balance; no lo exige. |
| `10-recomendaciones.tex` | c-131 | Debe conservar la validacion sobre un corpus independiente (o sobre el conjunto de preproduccion, D11) como linea de trabajo. |
| `07:6`, parrafo introductorio de resultados | c-130 (D9) | Debe enumerar la subseccion nueva entre las vigentes al aplicar. |
| `04-marco-metodologico.tex`, `subsec:amenazas-validez` | c-129, c-130 | c-137 no lo edita; si se reestructura, puede remitir a `subsec:sensibilidad-ajustes`. |
| Seccion 3.x de `numeros-canonicos.md` | c-125 y c-126 declaran ambos "3.7" | El orquestador resuelve el choque; c-137 usa la siguiente libre. |
| Matriz de trazabilidad y precondiciones de la release | c-136 | Su propuesta enumera A1-A4 y c-125..c-135: debe incorporar A5 y c-137. |
| Acentuacion fuera de los fragmentos reescritos | c-132 | Corre despues. |

## Risks / Trade-offs

- **[La referencia historica no reproduce la linea base de c-71]** -> El apply se detiene, revisa la replica contra `git show 7925903:...` y los cambios del corpus posteriores al 2026-10-05, y registra la discrepancia; la replica nunca se ajusta a los datos; la tesis la rotula "No fiel" (T01).
- **[La reproduccion 131/97 por el adaptador falla]** -> Indica deriva entre el codigo y la etapa evaluada o un error del adaptador; no se reporta ninguna variante hasta resolverlo (D4).
- **[Acoplamiento al atributo privado `_patterns`]** -> Test de guarda con mensaje explicito (D5); un cambio de ese atributo en produccion obliga a revisar el adaptador.
- **[`V0` tambien estaba influido por el corpus]** -> Supuesto declarado (D3); si los autores informan lo contrario, la cota se declara parcial.
- **[La cota pesimista se lee como estimacion puntual del sesgo]** -> Ramas de redaccion pre-registradas con "cota pesimista" y la razon por la que lo es (T01, T05).
- **[Resultado incomodo para la tesis (por ejemplo, la etapa de reglas deja de superar a Gemini con `V0`)]** -> Se reporta igual (D2); se comunica a c-128 y c-127, que deciden sus lecturas; no altera ningun canonico. Expectativa no medida, inferida de la linea base documentada por c-71 (0,51 en 72 casos con `V0 + L0`): la rama A es la mas probable, con una cota del orden de 20 puntos, y E4 podria mostrar que con `V0` la etapa de reglas no supera a Gemini sobre los casos que resuelve (en `S`, Gemini acierta 0,6769); la rama se elige igual por el valor medido.
- **[Las caches no se recuperan]** -> E3, E4 y los niveles a y b se declaran no computables; la variante principal y la referencia historica no dependen de ellas.
- **[Prompt equivocado en un brazo pago]** -> Verificacion del SHA-256 del prompt cargado antes de la primera llamada; un proceso por brazo (D9).
- **[Gasto no autorizado]** -> Gate de corrida paga antes de construir el clasificador; tests con clasificador falso; la tarea de ejecucion exige la autorizacion registrada.
- **[Variabilidad de Gemini (temperatura 0,3) en la ablacion]** -> Brazo control en la misma sesion, deriva del control frente a la corrida oficial reportada, McNemar sobre pares y lectura sin causalidad fuerte.
- **[Datos personales en el conjunto de preproduccion]** -> Gobernanza HIGH, verificacion previa y aprobacion explicita; si requiere pseudonimizar o etiquetar, change propio (D11).
- **[Conflictos de edicion con c-125, c-126, c-127, c-128 y c-130]** -> Tabla de fronteras; aplicacion despues de c-125 y c-126 y antes de c-127 y c-128; ediciones por fragmento que conservan los rotulos.
- **[Paginas]** -> D15; decision final en c-136.

## Migration Plan

1. Linea base: entorno con las dependencias de CI, suite de `evaluation/` en verde, hash canonico del corpus (requiere el `.gitattributes` de c-126) y conteo de paginas.
2. Checkpoint del usuario (temprano, sin bloquear los bloques de codigo): nivel c del prompt, conjunto de preproduccion, estado del objetivo 6, variante por pliegues y versionado de las salidas pagas; y estado de los datos de c-126 (P1, P2 o P3; `generated_at` de la FORCE-ESCALATE).
3. Codigo bajo TDD: artefactos historicos (D6), adaptador y replica (D4, D5), metricas puras (D3, D8), reporte y CLI offline (D10).
4. Caracterizacion sobre el corpus real (131/97 y linea base de c-71) y generacion de `evaluation/report_sensibilidad_ajustes.md`.
5. Salidas condicionales: niveles a y b, E3 y E4 si hay caches; nivel c solo con autorizacion; conjunto de preproduccion solo en el desenlace positivo de D11.
6. Memo canonico (D14) y documentacion del repositorio (R01, R02).
7. Tesis (T01-T08), solo con c-125 y c-126 aplicados; barrido de calificacion (D12).
8. Compilacion, paginas, render, citas, trazabilidad en `dictamen-correcciones.md`, suite completa y `openspec validate --strict`.

**Rollback:** `git checkout <commit-previo> -- evaluation/ .gitattributes .gitignore "docs/Tesis/v10 (IA)/" docs/anexo_h_prompt_gemini.md docs/Tesis/Correcciones/numeros-canonicos.md docs/Tesis/Correcciones/dictamen-correcciones.md`, regenerar el render y recompilar. Sin migraciones ni re-ejecucion de la evaluacion; las salidas locales de la corrida paga se borran sin efecto sobre los canonicos.

## Open Questions

1. **(Usuario, gobernanza HIGH) Ablacion paga del prompt (nivel c):** se autorizan las 138 invocaciones (dos brazos sobre los 69 casos de la etapa Gemini, del orden de 0,03 USD y como maximo 0,10 USD)? Recomendacion: si, porque es la unica estimacion controlada del efecto de las reglas de frontera y su costo es marginal; si c-128 tambien decide correr Gemini sobre `S` (B5), evaluar una sesion unificada. Sin autorizacion, el change cierra con los niveles a o b o con la declaracion.
2. **(Usuario) Incidentes de preproduccion del Anexo H:** existen los ~100 incidentes? Donde, en que forma (pseudonimizados o no) y con que etiquetado (cinco sectores, multietiqueta)? Recomendacion: si existen pseudonimizados y etiquetados, usarlos como prueba externa respecto de los ajustes de c-71 y c-72 (D11); si no, declararlo y dejar la validacion independiente como trabajo futuro.
3. **(Autores / c-128) Estado del objetivo especifico 6:** se conserva "Alcanzado" con la salvedad en la evidencia (recomendado) o c-128 lo cambia?
4. **(Usuario) Variante por pliegues:** se acepta declararla no factible (recomendado) o se habilita una aproximacion por coincidencia rotulada como exploratoria y fuera de la tesis?
5. **(Autor de la corrida, Luca Gomez)** Puede aportar el `cache_meta.generated_at` de `evaluation/predicciones_calibracion.json` aunque la cache no se recupere? Habilita la clasificacion de su prompt (D9) y responde tambien la Open Question 5 de c-125.
6. **(Usuario / c-126 D8) Versionado de las salidas de la corrida paga:** se siguen las mismas reglas que las caches de c-126 (recomendado)?
7. **(Usuario / c-136, G0) Paginas:** se acepta el impacto de +1,0 a +1,4 paginas o se aplica desde el inicio la compensacion C3 (tabla en un anexo)?
