## Context

El change atiende la recomendacion **A2** (condicionante) y las recomendaciones **B7** (parte de exactitud por canal) y **B8** del dictamen CONEAU 2026-10-22 (ver `proposal.md` - Why). Toca dos superficies: el framework de evaluacion (`evaluation/`, codigo Python bajo TDD estricto) y la tesis (`docs/Tesis/v10 (IA)/paper/sections/`). Ninguna mejora exige una medicion de campo nueva, pero B7 y B8 exigen predicciones **por caso**, que hoy no estan en el clon.

### Estado verificado (solo lectura, 2026-10-22)

**Framework**

- `evaluation/run_evaluation.py::generar_reporte` emite etapas, exactitud estricta y "de pertenencia" con Wilson, matriz 5x5, metricas por sector, metricas de conjunto y la seccion "Tiempos". **No** emite calibracion, desglose por etapa ni por canal.
- `evaluation/metrics.py` ya tiene `calibracion_por_bandas`, `contingencia_confianza` (c-77) e `intervalo_wilson`, pero las dos primeras no tienen consumidor en el runner: la Tabla 7.5 y la contingencia del memo se calcularon con un comando ad hoc (`numeros-canonicos.md`, seccion 2). El requisito vigente "Reporte de calibración de la confianza del clasificador" de `evaluation-framework` queda asi sin cumplirse en `report.md`.
- `aciertos_pertenencia` mide `sector_asignado` dentro del conjunto **predicho**; solo 8 casos tienen sectores adicionales predichos, por lo que vale 147/200, igual que la estricta. **No** es la exactitud laxa del dictamen (prediccion principal dentro del conjunto de **verdad**).
- `Prediccion` no guarda `canal_origen`; `generar_reporte` recibe el corpus en el mismo orden que las predicciones y todos los tests existentes las construyen con `caso_id = caso.id`.
- La "trampa" de `CHANGES.md` ("Pendientes planificados", punto 2: la seccion Shapiro-Wilk se agrego a mano y regenerar el reporte la borra) **esta resuelta**: c-99 (commit `3c23726`, 2026-10-20) cablea `_seccion_tiempos`, que genera Shapiro-Wilk, Wilcoxon, divulgacion y desglose por canal. Regenerar `report.md` no pierde contenido. La nota de `CHANGES.md` quedo obsoleta (la actualiza c-136).
- No hay interprete con `pytest` en esta maquina. CI instala `App/Backend/requirements.txt` (pytest 9.1.1, pytest-asyncio 1.4.0) y `evaluation/requirements.txt`, y corre `pytest` dentro de `evaluation/`.

**Datos por caso**

- `evaluation/predicciones.json` (oficial, `hybrid-v3`) y `evaluation/predicciones_calibracion.json` (FORCE-ESCALATE, `hybrid-v2`) estan en `.gitignore` (lineas 72-73, agregadas por lucaGomezB en `d6bb474`, c-74, 2026-10-07), **nunca** se commitearon (`git log --all` vacio) y no existen en este clon. Toda la evidencia de uso es de lucaGomezB: corrida oficial (c-74, 2026-10-07), re-clave del `corpus_hash` (c-99: `5f062e14...` -> `1fd17d7e...`, sin tocar el payload ni `generated_at`), recalculos de c-102 y c-108 (2026-10-21).
- `HYBRID_CACHE_VERSION` sigue en `"hybrid-v3"` (`App/Backend/app/constants.py:48`): una cache oficial recuperada es un cache hit.
- Desde `d6bb474` no hubo cambios en `App/Backend/app/classifiers/` (solo `settings.py`/`constants.py` por auth, RBAC y privacidad). La etapa deterministica es reproducible offline y sin costo (`evaluation/deterministic_measurement.py::recolectar_observaciones`); la etapa Gemini no (temperatura 0,3, `settings.py:79`).

**Hash del corpus**

- `core.autocrlf=true` y no hay `.gitattributes`. La copia de trabajo del corpus esta en CRLF y hashea `7408cd2a39932803932a4b39f982b86f787d783c228c04b3b21b69b56ee62134`; el blob (LF) hashea el canonico `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`. En este clon `_is_cache_valid` rechazaria una cache recuperada (y el runner frenaria en el gate de corrida paga) y un reporte regenerado imprimiria otro hash.

**Corpus por canal** (`data/corpus_evaluacion_pseudonimizado.json`, 200 casos, 107 multietiqueta)

| Canal | Casos | Multietiqueta | Composicion sectorial (asignado) |
|---|---|---|---|
| llamada telefonica | 81 | 49 | Hardware 30, Software 28, Seguridad 14, Sistemas 9 |
| correo electronico | 66 | 43 | Hardware 23, Software 23, Seguridad 14, Sistemas 6 |
| formulario web | 53 | 15 | Hardware 32, Software 16, Seguridad 3, Bases de Datos 1, Sistemas 1 |

La composicion difiere: formulario web concentra Hardware (la clase con mejor F1, 0,8800) y tiene pocos casos multietiqueta; cualquier diferencia de exactitud entre canales queda confundida con esa composicion.

**Valores por etapa derivables sin caches.** Combinando agregados ya canonicos ---contingencia por etapa (`numeros-canonicos.md`, seccion 4), tramo `>= 0,90` con 46 casos, 13 errores y composicion 45 Gemini + 1 deterministico (seccion 5, item 3), Tabla 7.5 (`07-resultados.tex:154-158`) y la curva absoluta heredada de `docs/deterministic_calibration.md` (confianza deterministica `>= 1/6`: 33/22; `>= 0,5`: 33/22; `>= 0,75`: 7/3; `= 1,0`: 1/1)--- se obtiene, por aritmetica y con `intervalo_wilson` del propio framework:

| Segmento | Casos | Aciertos | Exactitud | IC Wilson 95 % |
|---|---|---|---|---|
| Etapa deterministica | 131 | 97 | 0,7405 | [0,6593; 0,8079] |
| Etapa Gemini | 69 | 50 | 0,7246 | [0,6095; 0,8161] |
| Det., confianza 0 (banda [0; 0,5)) | 98 | 75 | 0,7653 | [0,6724; 0,8382] |
| Det., confianza 0,5 (banda [0,5; 0,7)) | 26 | 19 | 0,7308 | [0,5392; 0,8630] |
| Det., confianza 0,75 (banda [0,7; 0,85)) | 6 | 2 | 0,3333 | [0,0968; 0,7000] |
| Det., confianza 1,0 (banda [0,95; 1,0]) | 1 | 1 | 1,0000 | --- |
| Gemini, banda [0,85; 0,95) (valores 0,85 y 0,90) | 31 | 22 | 0,7097 | [0,5341; 0,8390] |
| Gemini, banda [0,95; 1,0] (valores 0,95 y 0,98) | 38 | 28 | 0,7368 | [0,5799; 0,8503] |
| Gemini, confianza 0,85 | 24 | 18 | 0,7500 | [0,5510; 0,8800] |
| Gemini, confianza 0,90 | 7 | 4 | 0,5714 | [0,2505; 0,8418] |
| Gemini, confianza `>= 0,90` | 45 | 32 | 0,7111 | [0,5663; 0,8227] |

Control: el IC global 147/200 calculado igual reproduce el canonico [0,6698; 0,7913]. Lectura inmediata: el contraste agregado 0,697 (`>= 0,70`: 7 deterministicos + 69 Gemini) frente a 0,758 (`< 0,70`: 124 deterministicos) compara etapas; dentro de Gemini las dos bandas rinden 0,710 y 0,737 con IC solapados; y la confianza deterministica no ordena la correctitud (98 de sus 131 decisiones declaran 0 y aciertan el 76,5 %; las 6 de 0,75 aciertan 2). La cifra 0,744 que cita el dictamen para la banda superior incluye el caso deterministico; Gemini solo es 28/38 = 0,737. **Estos valores son derivados**: la cache oficial debe confirmarlos (D10) antes de registrarlos como `vigente` con procedencia en el reporte.

**Tesis** (numeracion de `str.splitlines`, que aqui coincide con `grep -n`)

- `07-resultados.tex:107` (marco metrico; cierra con la distribucion 131/69, exigida por el requisito "Divulgacion de las etapas del pipeline incluida la etapa fallback"), `:140-165` (`subsec:calibracion`; `tab:bandas` en 145-163; "calibracion invertida o anti-calibrada" en 165).
- `08-discusion.tex:16` (lectura de calibracion y gate, con el hallazgo positivo de c-121), `:30` (comparacion con la literatura).
- `09-conclusiones.tex:37` (parrafo del clasificador hibrido).
- `11-aspectos-legales.tex:34` (supervision humana; cita el analisis de calibracion y el umbral de 0,70).
- `04-marco-metodologico.tex:79` (analisis estadistico de la clasificacion).
- `subsec:calibracion` lo referencian `08-discusion.tex:16`, `09-conclusiones.tex:28` y `10-recomendaciones.tex:6`.
- El requisito vigente "Calibración de la confianza del clasificador" de `tesis-document` exige hoy discutir la "anti-calibracion" (0,697 frente a 0,758): por eso se MODIFICA en este change.

### Restricciones

- **Numeros canonicos congelados**: ningun valor `vigente` de `numeros-canonicos.md` cambia; todo valor nuevo entra con procedencia.
- **Sin cifras inventadas**: lo no computable se declara no computable.
- **Presupuesto de paginas**: el PDF tiene 101 paginas (tope de facto desde c-120/c-121; el spec principal todavia dice 100 en "Neutralidad de paginas del contenido de cumplimiento", inconsistencia previa que resuelve c-136).
- **TDD estricto** para toda funcion nueva en `evaluation/`, con las skills `python-testing-patterns` y `pytest-coverage` (`.agents/SKILLS.md`).
- **Sin llamadas pagas** salvo autorizacion explicita del usuario (gate `--confirm-paid` del runner).

## Goals / Non-Goals

**Goals:**

- Rehacer la calibracion por etapa (A2) y cerrar la observacion de artefacto de agregacion, sin depender de la recuperacion de datos.
- Agregar exactitud laxa (B8) y exactitud por canal (B7) con IC de Wilson cuando haya predicciones por caso verificadas; declararlas no computables en caso contrario.
- Hacer que el runner emita de forma reproducible todo lo que la tesis cita de calibracion y de los desgloses nuevos.
- Fijar una politica de deriva que impida reemplazar en silencio los numeros canonicos.
- Estabilizar el hash del corpus entre plataformas.
- Aportar a c-128 y c-137, si se recupera la cache FORCE-ESCALATE, el contraste pareado de McNemar entre la etapa deterministica y Gemini sobre el conjunto cortocircuitable (D13).

**Non-Goals:**

- No se cambia la metrica primaria, el estado del objetivo especifico 2 ni la tabla de cumplimiento de objetivos (c-128).
- No se definen las magnitudes "confianza" y "score de correctitud" ni el alcance del gate (c-125); este change usa esas definiciones.
- Salvo el contraste pareado de McNemar entre etapas (D13), no se agregan contrastes de hipotesis (tampoco entre canales) ni metricas de calibracion de literatura (ECE, Brier, AUROC): los desgloses se reportan con IC de Wilson descriptivos. Una calibracion formal del gate es linea futura (c-131).
- No se tocan los tiempos por canal ni `tab:tiempos-canal` (c-129), las recomendaciones (c-131), la bibliografia (c-133/c-134) ni `CHANGES.md` (c-136).
- No se re-ejecuta el clasificador salvo autorizacion explicita (D3) y nunca para sustituir la corrida oficial.
- No se modifica el backend, el prompt, el clasificador ni el contenido del corpus.

## Decisions

### D1 - Datos por caso: recuperar la corrida oficial y verificarla por huella

Orden de preferencia, con checkpoint del usuario (gobernanza HIGH):

1. **P1 (recomendada):** pedir a Luca Gomez las dos caches de su clon y colocarlas en `evaluation/predicciones.json` y `evaluation/predicciones_calibracion.json`. Verificar la oficial por metadata (`corpus_hash = 1fd17d7e...`, `corpus_count = 200`, `classifier_version = hybrid-v3`, `generated_at` de la corrida del 2026-10-07) y por **huella agregada** (D10). La FORCE-ESCALATE se verifica con `classifier_version = hybrid-v2`, 200 predicciones (199 Gemini + 1 deterministica) y el comando offline de `docs/deterministic_calibration.md`, que debe reproducir `precision_gem(S) = 88/130` y tau `0,5166`. Costo cero, deriva cero.
2. **P2 (solo con autorizacion explicita):** si P1 falla definitivamente, corrida de reproduccion bajo la politica D3: la etapa deterministica es identica (codigo sin cambios desde c-74), por lo que solo los 69 casos escalados invocan a Gemini (del orden de 0,05 USD con el precio del capitulo 8).
3. **P3:** si el usuario no habilita P1 ni P2, se entrega solo A2 (D2) y B7/B8 se declaran no computables con los artefactos disponibles.

La FORCE-ESCALATE no alimenta ningun numero del texto de la tesis en c-126: sostiene la reproducibilidad de `docs/deterministic_calibration.md` y el contraste pareado de McNemar de D13 (`precision_det(S) = 97/131` frente a `precision_gem(S) = 88/130`, con la salvedad de ser otra corrida y otra version), insumo sin costo de c-128 (B5) y de c-137.

**Alternativas consideradas:** (a) re-ejecutar directamente (descartada como primera opcion: introduce deriva, cuesta dinero y no es necesaria si existe la corrida oficial); (b) reconstruir por caso desde agregados (imposible para canal y laxa: los agregados no dicen a que canal ni a que conjunto de verdad pertenece cada error).

### D2 - Desacople: A2 no queda bloqueada por los datos

A2 (condicionante del dictamen) se resuelve con los valores derivados del Context, que solo usan agregados canonicos. B7 y B8 (mejoras de completitud, no condicionantes segun el propio dictamen) dependen de D1. En consecuencia `tasks.md` ordena los bloques de modo que la reescritura de la calibracion pueda aplicarse y cerrarse aunque el checkpoint de datos siga abierto; cuando llegue la cache, la huella (D10) confirma los derivados y su procedencia pasa a ser la linea del reporte regenerado.

**Alternativa considerada:** esperar los datos para todo el change. Se descarta porque bloquearia la unica observacion condicionante por una decision externa.

### D3 - Politica de deriva

- Los canonicos de clasificacion provienen de la corrida oficial (`hybrid-v3`, 2026-10-07) y **no se recalculan** en este change.
- Con P1, todo valor nuevo sale de esa corrida y `evaluation/report.md` se regenera por cache hit (sin costo).
- Con P2, la corrida de reproduccion se escribe en archivos separados (`evaluation/predicciones_reproduccion.json`, `evaluation/report_reproduccion.md`) invocando `main_con_corpus_real(report_path=..., predicciones_path=..., force=True, confirm_paid=True)`; `evaluation/report.md` y `evaluation/predicciones.json` no se tocan. La deriva se cuantifica contra los agregados oficiales de la etapa Gemini (50/69; bandas 31/22 y 38/28; tramo `>= 0,90` de 45 casos con 13 errores; matriz de Gemini = matriz oficial menos la deterministica reproducida offline). La exactitud por canal y la laxa se publican en la tesis desde ese reporte, con su propia fila global, su fecha y una nota que cuantifica la deriva; los canonicos (147/200, F1, bandas, etc.) no cambian.
- La **sustitucion total** (adoptar la corrida nueva como canonica y propagar a toda la tesis) se descarta salvo decision explicita del usuario registrada en el memo: reabriria valores de c-102, c-107 y c-108 en todos los capitulos a dias de la defensa.

**Alternativa considerada:** mezclar la corrida nueva con la oficial caso por caso. Se descarta: produciria tablas que no suman a los totales oficiales sin una explicacion trazable.

### D4 - Hash estable: `.gitattributes` con LF para el corpus

Se crea `.gitattributes` con `data/corpus_evaluacion_pseudonimizado.json text eol=lf` (y la misma regla para los archivos de predicciones si se versionan, D8), se refresca la copia de trabajo (se borra el archivo y se restaura con `git checkout -- data/corpus_evaluacion_pseudonimizado.json`) y se verifica que el SHA-256 local sea `1fd17d7e...`. El blob no cambia.

**Alternativas consideradas:** (a) `-text` (sin conversion): se descarta porque permitiria commitear un CRLF accidental y cambiar el hash; (b) normalizar fines de linea dentro de `_compute_corpus_hash`: mas robusto ante copias fuera de git, pero cambia el contrato del cache ("SHA-256 del archivo"); queda como posible endurecimiento en c-135.

### D5 - Exactitud laxa: tercera definicion, metrica secundaria

- Definicion: `acierto_laxo(caso) = sector_predicho in conjunto_verdad(caso)`, con `conjunto_verdad = {sector_asignado} | sectores_adicionales` del corpus (`CasoEvaluacion.conjunto_verdad`). Prediccion vacia o no canonica = error.
- Se **conserva** la "pertenencia" (requisito vigente y su escenario), pero el reporte enuncia por separado cada definicion. Se modifica el requisito de Wilson de `evaluation-framework` para pasar de dos a tres definiciones.
- En la tesis la laxa es **metrica secundaria operativa** (proporcion de derivaciones aceptables). No reemplaza a la estricta ni cambia el estado del objetivo 2: si la laxa alcanzara el 85 %, la lectura correspondiente la decide c-128.

**Alternativa considerada:** renombrar "pertenencia" a "laxa" o retirarla. Se descarta: rompe un requisito vigente sin necesidad y mezclaria dos conceptos distintos.

### D6 - API pura en `evaluation/metrics.py`

Funciones nuevas, todas puras y sin I/O, que reutilizan `intervalo_wilson`, `calibracion_por_bandas` y `contingencia_confianza`:

- `aciertos_laxos(predichos, conjuntos_verdad) -> int`.
- `ResumenExactitud` (dataclass congelada: `casos`, `aciertos_estrictos`, `aciertos_laxos`, exactitudes e IC de Wilson; `None` cuando `casos == 0`) y `resumen_exactitud(reales, predichos, conjuntos_verdad, confianza=NIVEL_CONFIANZA)`.
- `desglose_exactitud(claves, reales, predichos, conjuntos_verdad, orden=None) -> Dict[str, ResumenExactitud]`: con `orden` explicito lista exactamente esas claves (incluidas las de 0 casos, para las etapas); con `orden=None` ordena por conteo descendente y desempate alfabetico (misma regla que el desglose de tiempos, para los canales).
- `ETAPAS_PIPELINE = ("deterministic", "gemini", "fallback")`.
- `distribucion_confianza(confianzas, reales, predichos, decimales=4)`: valores distintos (redondeados para agrupar, por ejemplo `1/6`) en orden ascendente, con casos y aciertos.
- `calibracion_por_etapa(confianzas, reales, predichos, etapas, bandas=BANDAS_CALIBRACION_DEFECTO)`: aplica `calibracion_por_bandas` al subconjunto de cada etapa, en el orden de `ETAPAS_PIPELINE`.

Invariantes que los tests fijan: laxa >= estricta; aditividad de los desgloses (suma de casos y aciertos = global); bandas por etapa suman la banda global; `casos == 0` produce `None` y nunca `[0, 1]`.

**Alternativa considerada:** calcular los desgloses dentro del formateador del reporte. Se descarta: los dejaria sin prueba unitaria y repetiria logica.

### D7 - Secciones aditivas del reporte y procedencia

`generar_reporte` agrega, sin alterar ninguna linea existente:

1. Tras "Total de casos evaluados", una linea de **procedencia** (`classifier_version`, `generated_at`) cuando recibe `procedencia` (parametro nuevo opcional). `main_con_corpus_real` la pasa siempre: en cache hit la lee con `cargar_cache_meta(path)` (nueva) y en corrida nueva usa el `cache_meta` recien construido.
2. En la seccion de exactitud, la definicion de la laxa y sus tres lineas (exactitud, aciertos, IC de Wilson), despues de las de pertenencia.
3. Antes de "Tiempos", tres secciones nuevas: exactitud por etapa del pipeline; exactitud por canal de origen (con composicion por etapa); calibracion de la confianza (bandas globales que reproducen la Tabla 7.5, contingencia en 0,70 y tramo `>= 0,90` globales y por etapa, bandas por etapa con IC de Wilson y distribucion de valores por etapa). Etapas o bandas vacias se rotulan "no aplicable", como ya hace la seccion de tiempos.
4. Validacion de alineacion: si `predicciones[i].caso_id != corpus[i].id`, `ValueError` con la posicion y ambos identificadores.

El formato numerico sigue el del reporte vigente (4 decimales, punto decimal). Verificacion de no regresion: `git diff --numstat evaluation/report.md` sin lineas eliminadas.

**Alternativa considerada:** un reporte separado para los desgloses. Se descarta: el spec vigente exige que la calibracion este en `report.md` y la tesis cita ese archivo como procedencia.

### D8 - Versionado de las caches (decision del usuario, recomendado)

Recomendacion: versionar `evaluation/predicciones.json` y `evaluation/predicciones_calibracion.json` tal cual, con la regla LF de D4. Fundamento: el campo `descripcion` de cada prediccion es copia del texto **pseudonimizado** que ya esta versionado en el corpus (el runner lo toma de `caso.descripcion`), de modo que la exposicion incremental es nula; una tarea lo verifica caso por caso antes de commitear. Beneficios: cualquiera puede regenerar el reporte por cache hit sin costo, la huella (D10) corre en CI y todos los numeros de la tesis quedan verificables desde el repositorio (el dictamen reprocha la falta de registros primarios en otro punto).

Alternativas: (a) mantenerlas locales y registrar en el memo solo su `cache_meta` y su SHA-256 (opcion conservadora, sin cambiar `.gitignore`); (b) versionar una variante sin `descripcion` (minimizacion maxima, pero exige un cargador nuevo que una por `caso_id`; se descarta por costo frente a un beneficio nulo en exposicion).

### D9 - Presentacion en la tesis

- **`tab:bandas` reestructurada** (mismo rotulo, misma ubicacion): cinco bandas por fila y, por columna, casos, aciertos y exactitud de la etapa deterministica y de la etapa Gemini; celdas vacias con "---". Los totales por banda de la Tabla 7.5 siguen siendo derivables (suma de las dos etapas).
- **Tabla nueva unica `tab:exactitud-etapa-canal`** en `subsec:matriz-metricas`: filas Global, Etapa deterministica, Etapa Gemini, Llamada telefonica, Correo electronico, Formulario web; columnas casos, exactitud estricta con IC y exactitud laxa con IC. Si B7/B8 no son computables (P3), no se crea: la exactitud estricta por etapa con IC va en la prosa de `subsec:calibracion`.
- **Prosa de calibracion** (reemplaza `07-resultados.tex:165`, misma extension): contraste agregado como efecto de composicion; conclusion restringida a Gemini en 0,85-1,00 (0,710 y 0,737 con IC solapados: la confianza autodeclarada no discrimina aciertos de errores en el rango observado); la confianza de la etapa de reglas es una fuerza de senal en escala discreta que no ordena la correctitud y no sirve como criterio de derivacion, con la terminologia que fije c-125 en `subsec:subsistema-clasificacion`. Sin las expresiones "anti-calibr" ni "calibracion invertida".
- **Metodologia** (`04-marco-metodologico.tex:79`): una o dos oraciones con la definicion de la laxa y de los desgloses.
- **Rotulos** `subsec:calibracion`, `tab:bandas` y `subsec:matriz-metricas` intactos; se conserva la oracion de distribucion 131/69 en `07-resultados.tex:107`.

**Alternativa considerada:** una tabla nueva de bandas por etapa ademas de la Tabla 7.5. Se descarta por paginas y por redundancia.

### D10 - Huella canonica como test de caracterizacion

`evaluation/tests/test_huella_canonica.py` verifica, **solo si la cache esta presente** (`pytest.mark.skipif`), que las predicciones reproducen los agregados canonicos: 147/200; etapas 131/69/0; bandas `98/26/6/31/39` con `75/19/2/22/29`; contingencia `76/53` y `124/94` y su composicion por etapa; tramo `>= 0,90` de 46 casos con 13 errores (45 Gemini); exactitud por etapa 97/131 y 50/69; distribucion deterministica `{0: 98, 0,5: 26, 0,75: 6, 1,0: 1}`; y, si el corpus esta presente, su SHA-256 canonico. No conduce codigo de produccion (caracteriza datos), por lo que no sigue el ciclo RED/GREEN: se declara asi en la evidencia TDD. Sirve como oraculo de D1 y, si D8 se aprueba, como guarda permanente en CI.

**Alternativa considerada:** un script de verificacion ad hoc. Se descarta: no quedaria como guarda reproducible.

### D11 - Propagacion y limites con los changes hermanos

- **c-125 antes de los bloques de tesis de c-126**: ambos editan `08-discusion.tex:16` y `11-aspectos-legales.tex:34`, y c-126 usa sus definiciones. Los bloques de codigo de c-126 pueden avanzar en paralelo con c-125 (no comparten archivos).
- c-126 edita: `04:79`, `07:107` y `07:140-165`, `08:16` (solo la lectura de calibracion), un parrafo nuevo breve en `08` (laxa y canal), `08:30` (una oracion), `09:37` (una oracion) y la ultima oracion de `11:34`.
- c-126 **no** edita: `tab:cumplimiento-objetivos` y `08:10` (c-128), `08:20` y `tab:tiempos-canal` (c-129), `10-recomendaciones.tex` (c-131), `09:39` (salvedad de cota inferior, B13).
- Consumidores posteriores: c-127 (laxa como sensibilidad del balance neto), c-128 (exactitud por etapa y McNemar de D13 para B5, por canal para el objetivo 3, laxa para la lectura del objetivo 2), c-131 (aprendizaje activo condicionado a la lectura por etapa), c-136 (paginas, `CHANGES.md`, release) y c-137 (sensibilidad fuera de muestra; el McNemar de D13 es su referencia en muestra).

### D12 - Presupuesto de paginas

Estimacion bruta: +0,6 a +0,9 paginas (tabla nueva ~0,3; `tab:bandas` +0,05; prosa neta de 04/07/08/09 ~0,3). Compensaciones previstas, en orden: (1) `tab:bandas` sin fila de totales (los totales por etapa estan en la tabla nueva); (2) tabla nueva en `\footnotesize`, sin columnas de aciertos (se leen como `k/n` en la celda); (3) el parrafo de calibracion y el de `08:16` no crecen en lineas; (4) condensar la introduccion de `subsec:calibracion` (`07:143`). Con P3 el impacto cae a ~+0,2. Si tras compilar el PDF supera 101 paginas, se registra el exceso y su causa para c-136; no se elimina contenido cientifico.

### D13 - Contraste pareado de McNemar entre etapas sobre S (insumo de c-128 y c-137)

Condicionado a que la cache FORCE-ESCALATE se recupere y pase la verificacion de la tarea 3.3, se computa un contraste pareado de McNemar entre la etapa deterministica y Gemini sobre el conjunto cortocircuitable `S` (131 casos con senal no ambigua y `score_correctitud >= 0,5166`):

- **Pares:** los casos de `S` con prediccion de ambas etapas. La deterministica sale de la reproduccion offline (`recolectar_observaciones`, identica a la etapa `deterministic` de la cache oficial porque el codigo no cambio desde c-74); la de Gemini, de la cache FORCE-ESCALATE (`etapa == "gemini"`). Se espera `n = 130`: el caso de `S` que tambien cortocircuito en la corrida forzada no tiene prediccion de Gemini y se excluye, declarando su identificador. Criterio de acierto: estricto (metrica primaria).
- **Estadistico:** tabla 2x2 de aciertos, con `b` = acierta solo la deterministica y `c` = acierta solo Gemini. Chi-cuadrado con correccion de continuidad `max(0, |b - c| - 1)^2 / (b + c)` (1 grado de libertad; el `max` evita un estadistico positivo cuando `b = c`) y valor p binomial exacto bilateral `min(1, 2 P(X <= min(b, c)))` con `X ~ Bin(b + c; 0,5)`. Se reportan ambos; el p primario es el exacto cuando `b + c < 25` (pocas discordancias) y el corregido en otro caso. Sin discordancias (`b + c = 0`), "no aplicable".
- **Implementacion (TDD):** funcion pura `contraste_mcnemar` en `evaluation/stats.py` (junto a Wilcoxon y Shapiro-Wilk; `scipy` ya esta en `evaluation/requirements.txt`) y ensamblado `contraste_det_gem_en_s` en `evaluation/deterministic_measurement.py`, que ya resuelve la cache FORCE-ESCALATE; el reporte comparativo offline imprime la linea del contraste.
- **Registro:** seccion nueva en `docs/deterministic_calibration.md` (hogar de `precision_det(S) = 97/131` y `precision_gem(S) = 88/130`) y fila en la seccion 3.7 del memo con procedencia, rotulada "insumo de c-128 (hipotesis subsidiaria de eficiencia del esquema hibrido) y de c-137 (sensibilidad fuera de muestra por el ajuste del clasificador con el corpus, A5)". c-126 **no** lo incorpora al texto de la tesis: su lectura corresponde a c-128 y c-137 (impacto de paginas nulo).
- **Salvedades registradas junto al valor:** la prediccion de Gemini sobre `S` proviene de otra corrida y otra version (`hybrid-v2`) que la oficial, en la que Gemini nunca vio `S`; el contraste es dentro de la muestra de evaluacion y `S` se definio con el tau out-of-fold calibrado sobre el mismo corpus; un resultado no significativo no demuestra equivalencia.
- **Sin cache:** si la cache FORCE-ESCALATE no se recupera o no pasa la verificacion, la tarea se cierra como "no computable con los artefactos disponibles" y se registra asi en el memo; no bloquea el change ni habilita una corrida forzada paga (si c-128 o c-137 la necesitan, la deciden ellos).

**Alternativas consideradas:** (a) comparar 97/131 y 88/130 como proporciones independientes (prueba z o de Fisher): se descarta porque son los mismos casos y la prueba ignoraria el apareamiento; (b) chi-cuadrado sin correccion: se descarta porque con pocas discordancias la aproximacion es pobre; (c) solo el p exacto: valido, pero se conserva el corregido por comparabilidad con la literatura; (d) delegar el computo a c-128: se descarta porque c-126 ya recupera y verifica las caches y el ensamblado reutiliza su codigo.

## Risks / Trade-offs

- **[Las caches no aparecen]** -> D2 garantiza A2; D3 (P2) o P3 cubren B7/B8 sin inventar cifras.
- **[La cache recuperada no es la oficial]** (otro `generated_at`, otra version, payload editado) -> D10 la rechaza; se registra la discrepancia y se pasa a P2/P3.
- **[Deriva en la corrida de reproduccion]** -> D3: archivos separados, deriva cuantificada, canonicos intactos.
- **[Conflictos de edicion con c-125]** en `08:16`, `11:34` y subsecciones vecinas de 07 -> secuencia D11.
- **[Confusion entre pertenencia y laxa]** -> D5: definiciones enunciadas por separado en reporte, metodologia y resultados.
- **[Lectura causal del canal]** (transcripcion telefonica) -> salvedad obligatoria de composicion sectorial y multietiqueta (spec `tesis-document`).
- **[Bandas con n muy chico]** (Gemini 0,90: n = 7; deterministica 0,75: n = 6) -> se reportan con IC y no se afirman tendencias; la tesis cita bandas, no valores sueltos.
- **[Paginas > 101]** -> D12; decision final en c-136.
- **[Versionar caches expone datos]** -> D8 verifica igualdad con el corpus pseudonimizado ya versionado antes de commitear; requiere aprobacion explicita.
- **[El `.gitattributes` altera otros archivos]** -> la regla nombra solo archivos JSON del corpus y, si se aprueba D8, de predicciones; no usa patrones globales.
- **[El McNemar de D13 se lee como prueba de superioridad o de equivalencia]** -> se registra con sus salvedades (otra corrida y version, contraste en muestra, no significativo no implica equivalencia) y su lectura queda en c-128 y c-137.

## Migration Plan

1. Prerrequisitos: entorno con `pip install -r App/Backend/requirements.txt -r evaluation/requirements.txt`; baseline de la suite `evaluation/` y del conteo de paginas.
2. D4: `.gitattributes`, refresco del corpus y verificacion del hash.
3. Checkpoint D1 (usuario): pedir las caches a Luca; verificar con D10. Si fallan, pedir decision P2/P3.
4. Bloques de codigo bajo TDD (D6, D7, D13), en paralelo con el checkpoint.
5. Con P1: regenerar `evaluation/report.md` por cache hit y verificar diff sin eliminaciones. Con P2: generar `evaluation/report_reproduccion.md` con rutas separadas. Con P3: no se regenera. Con la cache FORCE-ESCALATE verificada: computar y transcribir el McNemar de D13; sin ella, declararlo no computable.
6. D8 (si se aprueba): versionar las caches.
7. Upsert de `numeros-canonicos.md`.
8. Ediciones de la tesis (D9, D11), solo con c-125 aplicado.
9. Compilar, verificar paginas (D12), regenerar `tesis_para_agente.md`, verificar citas y limites.

**Rollback:** `git checkout <commit-previo> -- evaluation/ .gitattributes "docs/Tesis/v10 (IA)/" docs/Tesis/Correcciones/numeros-canonicos.md` y recompilar. Las caches locales no requieren rollback; si se versionaron, revertir `.gitignore` y `git rm --cached` de ambas. Los archivos de una corrida de reproduccion se eliminan sin afectar canonicos.

## Open Questions

1. **(Usuario, bloquea B7/B8) Recuperacion de caches:** Luca Gomez puede compartir `evaluation/predicciones.json` y `evaluation/predicciones_calibracion.json` de su clon (por un canal privado, no por el repositorio mientras no se decida la pregunta 3)? Recomendacion: si; es la unica via con costo y deriva cero, y la FORCE-ESCALATE habilita ademas el McNemar de D13.
2. **(Usuario, solo si la 1 falla) Corrida de reproduccion:** se autoriza una corrida paga de los 69 casos Gemini (del orden de 0,05 USD) bajo la politica D3, o se declaran B7/B8 no computables (P3)? Recomendacion: autorizar solo si la 1 falla definitivamente; B7/B8 no condicionan la aprobacion plena del dictamen (solo A1-A4 y B4-B6 lo hacen).
3. **(Usuario, gobernanza HIGH) Versionado de las caches (D8):** se versionan tal cual tras verificar que `descripcion` coincide con el corpus pseudonimizado, o se mantienen locales registrando solo su huella? Recomendacion: versionarlas.
4. **(Usuario / c-136) Tope de paginas de la release v1.2.0:** c-125, c-127, c-128, c-129 y c-131 tambien agregan contenido; se mantiene el tope de 101 paginas o se renegocia en c-136? Este change cumple su parte con D12 y registra cualquier exceso.
5. **(c-128) Lectura del objetivo 2 con la exactitud laxa:** c-126 solo reporta la laxa como metrica secundaria; si su valor alcanza el 85 %, c-128 decide si y como cambia la lectura del objetivo 2.
