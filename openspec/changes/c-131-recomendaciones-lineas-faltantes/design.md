## Context

El change cierra la observacion de la seccion 8 y la recomendacion B11 del dictamen CONEAU 2026-10-22 (ver `proposal.md` - Why): el capitulo de recomendaciones anuncia tres lineas prioritarias y solo desarrolla una, y su propuesta de aprendizaje activo contradice el hallazgo de calibracion. Es documental: edita unicamente `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex` (capitulo 11 del PDF, porque las consideraciones eticas y legales se compilan como capitulo 7) y agrega una entrada de trazabilidad en `docs/Tesis/Correcciones/dictamen-correcciones.md`.

Pertenece a la familia c-125..c-136 que atiende el dictamen. Las lineas futuras que este change redacta dependen del diagnostico que fijan otros changes: c-125 (el gate de 0,70 solo aplica a la etapa Gemini y a la de reserva; la etapa deterministica se gobierna por el score de correctitud con punto de operacion 0,5166), c-126 (calibracion rehecha por etapa: la confianza autodeclarada de Gemini no discrimina aciertos de errores en su rango efectivo 0,85-1,00), c-127 (balance neto de derivaciones erroneas; la exactitud manual no se midio), c-128 (reformulacion de la sub-hipotesis de intervencion), c-129 (asignacion muestral no proporcional) y c-133 (literatura de calibracion y cascadas, unico dueno de entradas nuevas en el `.bib`).

Estado verificado de las fuentes (solo lectura; HEAD `5de674d`, capitulo sin cambios desde c-122 `7408543`, identico en v1.1.0 y v1.1.1):

- `10-recomendaciones.tex:6` remite el "analisis de errores" a `\autoref{subsec:calibracion}` (en el PDF, "Subseccion 8.4"); el analisis de errores es `subsec:analisis-errores` (8.5). Remision erronea.
- `10-recomendaciones.tex:8` prioriza "calibracion del gate de confianza, clasificador supervisado con corpus propio y correccion de la medicion de intervencion humana" y las ancla en `subsec:limitaciones-estudio`, cuya lista de seis limitaciones (`08-discusion.tex:36-50`) no menciona ni la calibracion ni la medicion de intervencion: esos defectos se reportan en `subsec:calibracion` y `subsec:reduccion-intervencion` (`07-resultados.tex:~134-165`) y se interpretan en `08-discusion.tex:16`. El parrafo, ademas, no clasifica aprendizaje activo, replicacion, modelos abiertos ni agente telefonico.
- Solo existe `subsec:clasificador-supervisado`; no hay subsecciones para las otras dos lineas prioritarias.
- `subsec:aprendizaje-activo` (`10-recomendaciones.tex:24-26`) prioriza "casos clasificados con baja confianza" y afirma que la intervencion humana "de todos modos ocurre en los casos derivados a revision", aunque el gate no derivo ningun caso (`07-resultados.tex:136`).
- `08-discusion.tex:16` ya sugiere "senales independientes del puntaje" (ambiguedad lexica entre categorias candidatas, revision por muestreo de casos de alta confianza): la nueva subseccion se apoya en esa sugerencia.
- `tab:variables` (`04-marco-metodologico.tex:34`) define la intervencion humana en dos formas rotuladas: proporcion de casos que requieren accion manual de un operador y proporcion del tiempo total del proceso dedicado a esa accion. `02-marco-teorico.tex:34` define tres grados de autonomia (revision total, revision selectiva, operacion autonoma con auditoria).
- `clasificacion_log` (`App/Backend/app/models/clasificacion_log.py`; `tab:entidades` en `05-arquitectura.tex`) guarda `requiere_revision_humana`, la categoria validada y `created_at`/`updated_at`, pero no el inicio ni el fin de una intervencion, su origen ni el operador: no existe registro primario de intervencion por caso (`numeros-canonicos.md`, seccion 7, punto 1).
- `numeros-canonicos.md` (seccion 4) muestra que Gemini emitio solo valores de confianza en {0,85; 0,90; 0,95; 0,98} y que la confianza de la etapa deterministica es una fuerza de senal en {0; 1/6; 0,5; 0,75; 1,0}, no un disparador del gate. Estos valores motivan el diseno pero NO son citables en la tesis salvo que c-126 los incorpore a la tabla canonica.
- `docs/deterministic_calibration.md` documenta la curva comparativa cobertura-precision de la etapa deterministica con ajuste fuera de la muestra (cross-fitting de 5 folds): es el antecedente metodologico que la nueva subseccion propone replicar para el gate.
- Referencias anticipadas al capitulo sin destino: `05-arquitectura.tex:64` (SSO, `subsec:capa-canales`), `05-arquitectura.tex:74` (calibracion de los parametros de inferencia, `subsec:capa-procesamiento`), `05-arquitectura.tex:112` (prefijo configurable del numero de incidente, `subsec:modelo-datos`) y `06-implementacion.tex:8` (migracion a Kubernetes, `subsec:entorno-despliegue`). Ninguno de esos temas figura en el capitulo.
- Paginacion (`main.toc`, `main.pdf` de 101 paginas): el capitulo ocupa las paginas 84-87; las cuatro estan llenas (30-31 lineas de texto cada una) y la 87 no tiene margen libre. El capitulo termina en `\newpage`, por lo que cualquier crecimiento neto agrega una pagina completa.
- Linea base de palabras por subseccion (conteo sobre la fuente, sin comandos LaTeX): introduccion 107 (2 parrafos), clasificador supervisado 160, canales 88, panel de monitoreo 175 (2 parrafos), aprendizaje activo 76, replicacion 91, modelos abiertos 85, base de conocimientos 273 (3 parrafos), agente conversacional 330 (2 parrafos); total 1.385.
- Requisitos vigentes del spec que restringen la edicion: "Future work -- organizational analytics expansion" (el primer parrafo del panel de monitoreo no se altera), "Future work -- knowledge base for self-service resolution" (base de conocimientos con al menos dos parrafos, tipos simples de incidente, remisiones a aprendizaje activo y a modelos abiertos, sin citas), "Priorizacion de las lineas de trabajo futuro sobre los defectos medidos" y "Umbral de migracion como referencia indicativa de orden de magnitud".

## Goals / Non-Goals

**Goals:**

- Dar desarrollo propio a las dos lineas prioritarias anunciadas y ausentes, con contenido fundado en los hallazgos que fijan c-125 y c-126 y sin cifras nuevas.
- Resolver la contradiccion del aprendizaje activo con el hallazgo de calibracion.
- Ampliar las replicaciones con la medicion de la exactitud del flujo manual y la asignacion no proporcional.
- Dejar el parrafo de priorizacion verificable: cada linea prioritaria con su subseccion, cada subseccion clasificada en un nivel y cada remision apuntando al rotulo correcto.
- Acotar y declarar el impacto de paginas, con compensacion concreta dentro del capitulo.

**Non-Goals:**

- No se corrige el diagnostico en los capitulos 2, 5, 7 u 8 (es de c-125 y c-126), ni se reformula la sub-hipotesis de intervencion (c-128), ni se computa el balance neto (c-127), ni se discute la asignacion muestral en el capitulo 4 (c-129).
- No se agregan entradas a `Bibliography_base.bib` ni se reescriben atribuciones existentes (c-133 y c-134); en particular no se toca la frase sobre Touvron et al. (2023) de `subsec:clasificador-supervisado`.
- No se edita el primer parrafo de `subsec:panel-monitoreo` ni `subsec:evaluacion-modelos-abiertos`.
- No se corrige ortografia en oraciones que el change no reescribe (c-132); las oraciones reescritas si se redactan con ortografia correcta.
- No se agregan a las replicaciones otras mejoras de diseno ya enunciadas en la discusion (contrabalanceo, instrumento unico de medicion).
- No se modifica el Anexo H (su recomendacion de "especificar umbrales de confianza explicitos" se refiere al prompt y no contradice la nueva subseccion).
- No se implementa en el backend el registro de intervencion: el change describe un protocolo para replicaciones, no un cambio de codigo.
- No se regenera `tesis_para_agente.md` ni se crea ningun tag (c-136).

## Decisions

### D1 - Ubicacion, orden y rotulos de las subsecciones nuevas

Las tres lineas prioritarias pasan a ser las tres primeras subsecciones, en el orden anunciado: "Calibracion del gate de confianza" (`\label{subsec:calibracion-gate}`) se inserta antes de `subsec:clasificador-supervisado`, y "Correccion de la medicion de intervencion humana" (`\label{subsec:medicion-intervencion}`) inmediatamente despues. El resto del capitulo conserva su orden relativo; solo cambia la numeracion, que se resuelve por `\autoref`. Los dos rotulos son contrato estable: los changes hermanos pueden citarlos por anticipado y c-136 verifica que no queden referencias indefinidas.

**Alternativas consideradas:** (a) agregar las subsecciones al final del capitulo, que minimiza el diff pero contradice la priorizacion declarada; (b) reordenar todo el capitulo por niveles, que mueve bloques existentes y agranda el diff sin beneficio verificable; (c) fusionar la calibracion con el aprendizaje activo, que mezcla una linea prioritaria con su consumidora y rompe la remision de la base de conocimientos al aprendizaje activo exigida por el spec.

### D2 - Contenido de "Calibracion del gate de confianza"

Tope de 220 palabras. Elementos obligatorios, en este orden:

1. **Diagnostico citado, no recalculado:** el gate de 0,70 solo aplica a la etapa Gemini y a la de reserva; la etapa deterministica se gobierna por su score de correctitud; la confianza autodeclarada de Gemini se concentra en su rango efectivo (0,85 a 1,00) y no discrimina aciertos de errores, por lo que el gate no derivo ningun caso. Se remite con `\autoref` a la subseccion de resultados que c-126 deja para la calibracion por etapa y a la descripcion del gate que deja c-125. No se reintroduce la "calibracion invertida" del clasificador en su conjunto.
2. **Conjunto de validacion propio**, disjunto del corpus de evaluacion de 200 casos, coherente con la separacion entre datos de construccion y de validacion que la tesis ya declara (`subsec:interpretacion-resultados`).
3. **Senales independientes del puntaje** (al menos tres): ambiguedad lexica entre categorias candidatas (coincidencias del diccionario deterministico con mas de un sector); margen entre la primera y la segunda categoria, que exige ampliar el contrato de salida del modelo con puntajes por categoria (`\autoref{anexo:H}`); desacuerdo entre etapas cuando ambas se ejecutan; y revision por muestreo de casos de alta confianza, que corresponde a la operacion autonoma con auditoria de `subsec:human-in-the-loop` y retoma `08-discusion.tex:16`.
4. **Recalibracion posterior** del puntaje, o de un puntaje que combine las senales, sobre ese conjunto: Platt o regresion isotonica para un puntaje escalar, y escalado de temperatura solo si se obtienen puntajes por categoria. Se declara que una recalibracion monotona corrige el nivel de la confianza pero no crea capacidad de discriminacion; por eso no sustituye a las senales del punto 3.
5. **Umbral derivado de una curva cobertura-precision** ajustada fuera de la muestra, como el punto de operacion de la etapa deterministica, con un criterio declarado antes de observar la curva: un piso comparativo frente a la exactitud de la revision humana (que exige medirla, D5) o un piso absoluto ligado al 85 % del segundo objetivo especifico. Si ninguna senal alcanza el piso, el gate no queda justificado y la revision por muestreo pasa a ser la salvaguarda.
6. **Parametros de inferencia** (D7): una oracion indica que la misma campana permite contrastar la configuracion de inferencia adoptada sin optimizacion documentada (temperatura y top_p, `\autoref{subsec:capa-procesamiento}`).

Prohibido: cifras fuera de la lista blanca (D9); afirmar capacidades del proveedor no documentadas en la tesis (por ejemplo, probabilidades por token); presentar la propuesta como resultado.

**Alternativas consideradas:** (a) proponer solo la recalibracion posterior, que no resuelve el problema porque una transformacion monotona de un puntaje que no discrimina sigue sin discriminar (con cuatro valores discretos de confianza, la isotonica colapsa a lo sumo en cuatro niveles de exactitud parecida); (b) proponer mover el umbral de 0,70, que es arbitrario sin curva y, por debajo de 0,85, no dispararia nunca; (c) reemplazar la confianza autodeclarada por probabilidades del modelo, que depende de capacidades del proveedor no documentadas en la tesis y se deja implicito en el contrato ampliado del punto 3.

### D3 - Contenido de "Correccion de la medicion de intervencion humana"

Tope de 180 palabras. Elementos obligatorios:

1. **Diagnostico:** la sub-hipotesis de intervencion quedo "no contrastada por ausencia de registro primario" (`\autoref{subsec:reduccion-intervencion}` y `\autoref{subsec:hipotesis-trabajo}`, en la formulacion que deje c-128).
2. **Registro primario por caso** con cuatro campos: ocurrencia y origen de la intervencion (derivacion por el gate, revision por muestreo, correccion o rederivacion por el sector receptor, completado manual de datos); consigna de tiempo de inicio y de fin; resultado (categoria confirmada o corregida); y operador seudonimizado, coherente con el tratamiento de datos del capitulo legal.
3. **Almacenamiento:** ampliar `clasificacion_log`, que ya registra el indicador de revision y la categoria validada, o una tabla dedicada vinculada al incidente; se recomienda la tabla dedicada cuando un incidente acumula varias intervenciones o cuando la intervencion no nace de un evento de clasificacion. Sin DDL ni nombres de columnas en la tesis.
4. **Definicion operacional** alineada con las dos formas rotuladas de `tab:variables` (proporcion de casos y proporcion del tiempo del proceso), aplicada de igual modo en ambos brazos.
5. **Contrastabilidad:** el registro permite contrastar la sub-hipotesis en cualquiera de las dos reformulaciones que el dictamen admite: contra una fraccion esperada fijada antes de medir, o como cobertura efectiva del gate (proporcion de clasificaciones erroneas derivadas a revision). La redaccion final sigue la que adopte c-128.
6. **Rendimiento adicional:** el mismo registro mide en cada brazo las derivaciones erroneas y su costo en tiempo, insumos del balance neto que c-127 debio apoyar en estimaciones (remision por `\autoref` a la ubicacion que deje c-127, sin repetir sus cifras).

Prohibido: reportar cualquier proporcion de intervencion como resultado (el 9,5 % esta retirado).

**Alternativas consideradas:** (a) enunciar "medir la intervencion" sin protocolo, que no atiende la causa que el propio documento declara (ausencia de registro primario); (b) incluir el DDL o la migracion en la tesis, detalle impropio de un capitulo de recomendaciones; (c) implementar ahora el campo en el backend, que es un cambio de codigo fuera de alcance y no permitiria medir retroactivamente el corpus.

### D4 - Aprendizaje activo condicionado a la calibracion

La subseccion se reformula (tope de 110 palabras): la seleccion de casos para revision y reentrenamiento se apoya en las senales independientes de `\autoref{subsec:calibracion-gate}`; la confianza declarada solo se usa como criterio de prioridad una vez recalibrada y validada segun esa subseccion; las revisiones que alimentan el ajuste incremental son las registradas segun `\autoref{subsec:medicion-intervencion}`. Se retira "que de todos modos ocurre en los casos derivados a revision". Se conserva el rotulo `subsec:aprendizaje-activo`, del que depende la base de conocimientos.

**Alternativas consideradas:** (a) solo condicionar a la calibracion, que deja la linea sin criterio operativo mientras la calibracion no se resuelva; (b) eliminar la subseccion, que rompe la remision exigida por el requisito de la base de conocimientos; (c) solo reformular sobre senales independientes, que ignora que una confianza bien recalibrada podria volver a ser util. Se combinan ambas vias, como admite el dictamen.

### D5 - Estudios de replicacion

Tope total de 140 palabras. Se agregan dos recomendaciones: (1) medir la exactitud del flujo manual sobre el mismo corpus, registrando el sector al que el operador deriva cada caso, con etiquetadores distintos de los operadores del brazo manual (`\autoref{subsec:limitaciones-estudio}`, sexta limitacion), porque es el insumo faltante del balance neto (c-127) y del piso comparativo del gate (D2); (2) emplear asignacion muestral no proporcional que sobremuestree las clases minoritarias -como Bases de Datos, con un solo caso en este corpus- y pondere las estimaciones globales por la distribucion del universo (`\autoref{subsec:poblacion-muestra-corpus}`, donde c-129 discute la asignacion). Para contener el crecimiento se compacta la oracion existente sobre sectores publico, industrial y organizaciones grandes, sin perder sus tres ejemplos. Se conserva el rotulo `subsec:estudios-replicacion` (c-127 y c-129 pueden remitir a el).

**Alternativas consideradas:** (a) ubicar la exactitud manual en la subseccion de intervencion, que la mezcla con un registro operativo cuando es una propiedad del diseno de replicacion (D3 solo la menciona como rendimiento adicional); (b) desarrollar la asignacion no proporcional con formulas de ponderacion, que excede el presupuesto y pertenece a la metodologia (c-129).

### D6 - Parrafo de priorizacion por niveles

Los dos parrafos introductorios se funden en uno (tope de 140 palabras) que: ancla los defectos en los resultados y la discusion donde efectivamente se reportan (analisis de errores en `\autoref{subsec:analisis-errores}`, calibracion e intervencion en sus subsecciones de resultados, limitaciones en `\autoref{subsec:limitaciones-estudio}`); declara tres niveles: (1) prioritarias, cada una con `\autoref` a su subseccion; (2) lineas complementarias que mejoran el clasificador o fortalecen la evidencia: aprendizaje activo, replicacion y modelos abiertos; (3) extensiones funcionales que amplian el alcance sin alterar la validez de lo medido: canales, monitoreo, base de conocimientos, agente telefonico en tiempo real y las evoluciones de plataforma anticipadas en los capitulos 5 y 6 (D7). Se corrige la remision erronea al analisis de errores.

**Alternativas consideradas:** (a) conservar el parrafo y solo agregar subsecciones, que mantiene la remision erronea y deja subsecciones sin clasificar; (b) un cuadro de prioridades al final del capitulo, que consume paginas sin informacion nueva.

### D7 - Referencias anticipadas sin destino (extension de alcance a confirmar)

Las cuatro remisiones de los capitulos 5 y 6 a `sec:recomendaciones` encuentran destino dentro del capitulo: la calibracion de los parametros de inferencia, en una oracion de `subsec:calibracion-gate` (D2, punto 6); SSO, prefijo configurable del numero de incidente y migracion a Kubernetes, nombrados en el nivel 3 del parrafo de priorizacion (D6). Costo estimado: unas 40 palabras. Es el mismo tipo de defecto que B11 (linea anunciada y ausente), el capitulo es propiedad de este change y la verificacion es mecanica. Se marca como extension de alcance (pregunta abierta 1): si el usuario la rechaza, se omiten los dos agregados y el hallazgo se deriva a c-130.

**Alternativas consideradas:** (a) dejarlo a c-130, que deberia editar el mismo capitulo en paralelo; (b) retirar o redirigir las remisiones en los capitulos 5 y 6, que son archivos que editan c-125 y c-135.

### D8 - Bibliografia y citas

El change no agrega entradas al `.bib` (dueno: c-133) ni citas nuevas a entradas existentes. Si al momento del apply c-133 ya incorporo entradas que traten la recalibracion posterior o la clasificacion selectiva, `subsec:calibracion-gate` las cita donde nombra la tecnica, con la atribucion verificada por c-134. Si no, las tecnicas se nombran sin cita y el concepto de calibracion se remite por `\autoref` al marco teorico (`subsec:nlp-llm`). El concepto de aprendizaje activo se remite a `subsec:human-in-the-loop`, sin citar de nuevo.

**Alternativas consideradas:** (a) agregar desde este change entradas como Platt (1999) o Guo et al. (2017), que pisaria la propiedad de c-133 y su verificacion; (b) citar MosqueiraRey2023_human_in_the_loop en el aprendizaje activo, que crea una atribucion nueva a verificar cuando una remision al marco teorico basta.

### D9 - Cifras: lista blanca

El texto nuevo o reescrito no introduce numeros fuera de esta lista: 0,70 (umbral del gate), 0,85 y 1,00 (rango efectivo de Gemini), 85 % (umbral del segundo objetivo), 200 (tamano del corpus), un caso de Bases de Datos, y los valores que el capitulo ya contenia antes del change (por ejemplo, 45 segundos, 8 kHz y 16 kHz en el agente conversacional, 100 incidentes diarios en la replicacion y 5.000 casos como referencia indicativa). Cualquier otro valor exige estado `vigente` en `numeros-canonicos.md` al momento del apply; se prefiere remitir por `\autoref` antes que repetir cifras. El 0,5166 del punto de operacion deterministico no se repite: se remite a donde lo documente c-125.

### D10 - Presupuesto de paginas: limite duro de 5 paginas y compensacion interna

| Bloque | Linea base (palabras) | Objetivo (tope) | Delta |
|---|---|---|---|
| Introduccion (fusion de dos parrafos) | 107 | 140 | +33 |
| Calibracion del gate (nueva) | 0 | 220 | +220 |
| Medicion de intervencion (nueva) | 0 | 180 | +180 |
| Aprendizaje activo | 76 | 110 | +34 |
| Estudios de replicacion | 91 | 140 | +49 |
| Base de conocimientos (2 parrafos) | 273 | 170 | -103 |
| Agente conversacional | 330 | 170 | -160 |
| Resto (sin cambios) | 508 | 508 | 0 |
| **Total** | **1.385** | **1.638** | **+253** |

Con unas 345 palabras por pagina (unas 11,6 palabras por linea y 30 lineas por pagina), el neto de +253 palabras mas dos titulos equivale a unas 25 lineas: el capitulo pasa de unas 120 a unas 145 lineas, es decir, de 4 a 5 paginas con un margen estimado de 5 a 15 lineas en la quinta. Si los textos nuevos quedan por debajo de sus topes, el neto baja a unas +140 palabras, que igualmente desbordan la cuarta pagina, hoy llena. **Limite duro del change: el capitulo ocupa a lo sumo 5 paginas**, medido como pagina de inicio de "Referencias bibliograficas" menos pagina de inicio del capitulo en `main.toc` (medida independiente de lo que agreguen otros changes en capitulos previos). El delta medido se registra para c-136.

Condensaciones obligatorias: (1) agente conversacional a <= 170 palabras, conservando la propuesta sobre Twilio Media Streams, la madurez en vista previa de las interfaces de audio bidireccional, la transcodificacion mu-law 8 kHz a PCM 16 kHz, la gestion de turnos de habla, el modelo de costo por minuto y la recomendacion de una prueba de concepto con la grabacion actual como modo degradado (los elementos que el dictamen valoro); (2) base de conocimientos a dos parrafos y <= 170 palabras, conservando lo que exige el requisito vigente (foco actual en clasificacion y derivacion, correspondencia con soluciones documentadas, ejemplos de reinicio de sesion, restablecimiento de contrasenas y configuracion de correo, remisiones a aprendizaje activo y a modelos abiertos, sin citas). No se tocan el primer parrafo del panel de monitoreo, el clasificador supervisado ni los modelos abiertos. Si el capitulo excediera 5 paginas, recortes adicionales en este orden: agente a <= 130 palabras, base de conocimientos a <= 150, replicacion a <= 120.

**Alternativas consideradas:** (a) neutralidad estricta (4 paginas): exige recortar unas 520 palabras (38 % del capitulo), incluida la eliminacion de subsecciones como la ampliacion de canales y la justificacion tecnica que el dictamen elogio; se declara inviable sin perdida de contenido (pregunta abierta 2); (b) trasladar texto a un anexo, que no reduce el total del PDF; (c) no compensar, que llevaria el neto a +1,5 paginas de texto y arriesgaria un sexto folio.

### D11 - Dependencias y orden de aplicacion

| Change | Relacion | Motivo |
|---|---|---|
| c-125 | Dura (antes) | La nueva subseccion cita la descripcion del gate por etapa y del score de correctitud. |
| c-126 | Dura (antes) | El diagnostico remite a la calibracion por etapa del capitulo 7 y a su rotulo. |
| c-127 | Blanda (antes, preferente) | Remision al balance neto y al estado de la exactitud manual. |
| c-128 | Blanda (antes, preferente) | La subseccion de intervencion sigue la formulacion final de la sub-hipotesis. |
| c-129 | Coordinacion | Dueno de la discusion metodologica de la asignacion; este change es dueno de la recomendacion. |
| c-133 | Blanda (antes, preferente) | Entradas citables para la recalibracion (D8). |
| c-134 | Despues (mismo archivo) | Corrige la frase de Touvron en el clasificador supervisado y verifica atribuciones nuevas. |
| c-132 | Despues (mismo archivo) | Revision ortotipografica sobre el texto final. |
| c-130 | Coordinacion | No edita el capitulo; recibe el hallazgo D7 si se rechaza la extension. |
| c-135 | Coordinacion | Si agrega remisiones nuevas a `sec:recomendaciones`, debe darles destino; c-136 re-verifica. |
| c-136 | Despues | Integra, compila, verifica el total de paginas, regenera el render y publica v1.2.0. |

Orden sugerido: c-125 -> c-126 -> c-127 -> c-128 -> c-129 -> c-133 -> **c-131** -> c-134 -> c-130 -> c-135 -> c-132 -> c-136 (c-130 y c-135 pueden ir en paralelo con c-131 porque no editan el capitulo). Si c-127, c-128 o c-133 no estan aplicados al momento del apply, c-131 procede con remisiones genericas (`subsec:hipotesis-trabajo`, `sec:discusion`) y sin citas, y lo registra en el reporte de apply.

### D12 - Trazabilidad y render

Se agrega en `docs/Tesis/Correcciones/dictamen-correcciones.md` una entrada "B11 - Recomendaciones: lineas prioritarias faltantes (c-131)" que vincula cada observacion de la seccion 8 del dictamen con la subseccion y el rotulo corregidos, el delta de paginas medido y las dependencias, como exige la descripcion del Anexo I. No se regenera `tesis_para_agente.md`: lo hace c-136 una sola vez para evitar conflictos entre changes que editan capitulos distintos.

## Risks / Trade-offs

- [c-125 o c-126 no aplicados al momento del apply] -> Mitigacion: la tarea 1.1 bloquea el apply; el diagnostico no puede adelantarse a resultados que el capitulo 7 aun no reporta.
- [c-126 renombra o divide `subsec:calibracion`] -> Mitigacion: el rotulo se resuelve por grep en el apply; ninguna remision se escribe de memoria.
- [El capitulo supera 5 paginas] -> Mitigacion: recortes adicionales en el orden de D10; nunca se toca el primer parrafo del panel de monitoreo ni el clasificador supervisado.
- [Imprecision tecnica sobre recalibracion] -> Mitigacion: reglas de D2 (temperatura solo con puntajes por categoria; recalibracion monotona no crea discriminacion; sin capacidades del proveedor no documentadas).
- [Cifras nuevas sin procedencia] -> Mitigacion: lista blanca de D9 y extraccion de numeros del diff (tarea 7.3).
- [Conflicto de archivo con c-134 y c-132] -> Mitigacion: orden de D11; el change no edita el clasificador supervisado y solo corrige ortografia en las oraciones que reescribe; el "hacia" mal acentuado de la base de conocimientos desaparece al condensarla, lo que se avisa a c-132.
- [Requisitos vigentes del spec sobre panel de monitoreo y base de conocimientos] -> Mitigacion: verificacion por grep y por `git diff` de los elementos exigidos (tareas 6.2 y 6.3).
- [El texto se lee como compromiso de implementacion o como resultado] -> Mitigacion: redaccion condicional propia del capitulo ("se propone", "permitiria"), sin afirmar efectos.
- [La extension D7 es rechazada] -> Mitigacion: las dos adiciones son separables (tareas 2.3 y 3.2) y el hallazgo pasa a c-130.

## Migration Plan

1. Verificar prerrequisitos (c-125, c-126) y registrar los rotulos vigentes de calibracion por etapa, gate por etapa, balance neto y sub-hipotesis.
2. Medir la linea base (paginas del capitulo en `main.toc`, total de paginas y palabras por subseccion) y ejecutar las verificaciones de aceptacion antes de editar, confirmando que hoy fallan.
3. Editar `10-recomendaciones.tex` en el orden de `tasks.md`: parrafo de priorizacion, subsecciones nuevas, aprendizaje activo y replicacion, condensaciones.
4. Compilar con XeLaTeX y biber en el contenedor del `Dockerfile` de `paper/` (montando `docs/Tesis/v10 (IA)`); verificar ausencia de errores fatales y de referencias indefinidas; medir paginas y palabras.
5. Ejecutar las verificaciones de aceptacion (deben pasar), `verify_citations.py` y `openspec validate c-131-recomendaciones-lineas-faltantes --strict`.
6. Registrar la entrada B11 en `dictamen-correcciones.md` y el delta de paginas para c-136.
7. Rollback: `git checkout <commit-previo> -- "docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex" docs/Tesis/Correcciones/dictamen-correcciones.md` y recompilar; conservar los rotulos si ya hay remisiones de otros changes.

## Open Questions

1. **Extension de alcance D7:** dar destino en este change a las remisiones anticipadas de los capitulos 5 y 6 (parametros de inferencia, SSO, prefijo configurable, Kubernetes), unas 40 palabras (recomendado), o derivarlo a c-130.
2. **Presupuesto de paginas:** aceptar +1 pagina para el capitulo con renegociacion del tope global en c-136 (recomendado), o exigir neutralidad estricta, lo que obliga a eliminar contenido (por ejemplo, fundir la ampliacion de canales en el parrafo de priorizacion y reducir el agente conversacional a un parrafo).
3. **Citas de recalibracion:** esperar a que c-133 incorpore las entradas (orden recomendado de D11) o aplicar sin citas y que c-136 las agregue en la integracion.

Hallazgos colaterales fuera de alcance (para c-130 y c-134): la tabla `tab:anexo_gemini_params` del Anexo H califica los parametros de inferencia de "optimizados" mientras `05-arquitectura.tex:74` declara que no resultan de un procedimiento de optimizacion documentado; y la sub-hipotesis de intervencion (`01-introduccion.tex:34`) remite a `subsec:limitaciones-estudio`, cuya lista no menciona la intervencion (c-128).
