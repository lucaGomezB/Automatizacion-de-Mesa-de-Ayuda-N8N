# Devolución de segunda instancia — TFI «Automatización inteligente del registro de incidentes en mesas de ayuda empresariales»

> Transcripción del documento original, extraída con `pdftotext -layout` del PDF adjunto (`Devolucion_Segunda_Instancia_TFI_v1.2.18_2026-11-11.pdf`); el PDF es la evidencia de referencia, esta transcripción es para búsqueda y diffs. Las tablas conservan el orden del original (pueden quedar con el wrap del PDF).
>
> Entrega auditada: versión 1.2.18 (9/11/2026) · Emisión: 11/11/2026 · Calificación: **7,0 / 10** (antes 3,9 / 10).

---

Devolución de segunda instancia — TFI
«Automatización inteligente del registro de
incidentes en mesas de ayuda empresariales»
Entrega auditada: versión 1.2.18 (9/11/2026) · Fecha de emisión:                                                 ​Nov 11, 2026

1. Ficha y alcance de la verificación
Esta devolución audita la versión 1.2.18 contra los 105 hallazgos de la auditoría del 4 de
agosto de 2026 (calificación entonces: 3,9/10) y contra el repositorio declarado.

  Campo                           Dato

  Título                          Automatización inteligente del registro de
                                  incidentes en mesas de ayuda empresariales
                                  mediante orquestación de flujos con N8N y
                                  procesamiento de lenguaje natural basado en
                                  modelos de lenguaje grandes

  Autores                         Luca Gomez · Carla Bustos · Gonzalo Sevilla

  Directores                      Prof. Alberto Cortez y Prof. Ariel Enferrel

  Institución                     UTN — Facultad Regional Mendoza, Tecnicatura
                                  Universitaria en Programación

  Archivo                         tesis_ultima_version.pdf — versión 1.2.18, fechada
                                  el 9/11/2026

  Extensión                       120 páginas (antes 74) · ≈53.800 palabras (antes
                                  27.847) · 26 tablas · 10 figuras (antes 1) · 9 anexos
                                  (A–I)

  Bibliografía                    ≈88 entradas (antes 33), 37 fechadas en 2023–
                                  2026, de las cuales ≈18 son artículos arbitrados
                                  (antes 0)

  Repositorio                     github.com/lucaGomezB/Automatizacion-de-
                                  Mesa-de-Ayuda-N8N — tag anotado v1.2.18 sobre
                                  el commit
                                  457b14ae2c77ea221429345602aacc9213878640
                                  (coincide con el Anexo B)

  Auditoría previa                Auditoría integral del 4/8/2026: 105 hallazgos (28
                                  críticos), 3,9/10

Planos verificados en esta instancia.

   1. Textual: lectura completa de los 11 capítulos y los 9 anexos, con rastreo de coherencia
       entre hipótesis, métodos, resultados y conclusiones.
   2. Cuantitativo: recálculo independiente con SciPy 1.18.1 sobre los archivos versionados
      (corpus, predicciones, doble etiquetado, brazo manual e intervenciones) de más de 30
       cifras publicadas.
   3. Artefacto: clonado del repositorio en el tag v1.2.18 e inspección del flujo n8n, la
       configuración de despliegue, los datos y la bitácora de correcciones.
   4. Bibliográfico: verificación externa de una muestra de las referencias nuevas de 2023–
      2026.

Cuando un dato no pudo comprobarse, se lo indica como no verificable y no como falso.

2. Dictamen
APTA PARA DEFENSA CON OBSERVACIONES MAYORES. Calificación global: 7,0 / 10
(antes 3,9 / 10).

La nota es definitiva para esta instancia y no está sujeta a condición. Las correcciones de
la Sección 7 deben incorporarse al ejemplar que se lleve al acto de defensa; su ausencia se
evaluará en la defensa como observación no atendida.

Síntesis. La versión 1.2.18 es, en lo sustancial, otro trabajo. El capítulo de resultados ya no
informa la campaña sintética de julio, sino datos versionados que este informe pudo
recalcular dígito a dígito: reducción del tiempo medio de 61,6 s a 17,76 s (71,2 %), Wilcoxon
W = 363 con r = 0,9639, exactitud estricta de 73,5 % y macro-F1 de umbral de 0,6508. Los
autores refutan con honestidad parte de su propia hipótesis, corrigieron los tres errores
jurídicos, alinearon el flujo n8n con el texto y reemplazaron una bibliografía sin artículos
recientes por otra con evidencia arbitrada 2023–2026.

Por qué no es «observaciones menores». Quedan dos problemas de procedencia y cuatro
de método:

       El κ = 0,87 sigue en el Resumen y en tres capítulos, aunque su tabla no existe y el valor
       ya figuraba en la versión de julio, cuando el corpus real no existía (N-01).
       La tesis no declara que la versión de julio reportó resultados de un corpus sintético,
       pese a que la bitácora de los propios autores lo admite (N-02).
       La campaña complementaria midió tiempos manuales con operadores
       independientes y la tesis no los informa: un operador promedió 20,1 s y el otro 76,6 s
       (N-03).
       El mecanismo de selección de los 200 casos se describe de dos formas incompatibles
       (N-04).
       119 de los 200 tiempos automatizados no tienen registro primario verificable (N-05).
       El brazo telefónico automatizado se alimentó con llamadas recitadas por un autor (N-
       06).

Por qué no es una nota menor. Ninguno de esos puntos invalida el resultado central: la
propia campaña complementaria, recalculada en esta auditoría, reproduce la reducción
de tiempo (69,3 %, p = 3,0 × 10⁻²⁸) con sujetos independientes. Todos se resuelven con
escritura y declaración, no con nuevo desarrollo.

3. Estado de los 28 hallazgos críticos del 4 de agosto
De los 28 críticos, 24 quedan corregidos, 3 parcialmente y 1 sigue abierto (C-25, por la
persistencia del κ = 0,87). La verificación se hizo sobre el PDF y sobre el repositorio en el
tag v1.2.18.

  Código           Hallazgo de agosto                                           Estado                Evidencia en la v1.2.18

  C-01             El repositorio declaraba la                                  Corregido             Corpus real pseudonimizado
                   campaña experimental como                                                          versionado el 9/10/2026; la
                   trabajo futuro                                                                     declaración de integridad del
                                                                                                      Anexo F fue reescrita. Ver N-02:
                                                                                                      falta declararlo en la tesis

  C-02             La única corrida daba 63 % y la                              Corregido             Se informa 73,5 % (147/200),
                   tesis 92 %                                                                         recalculado sin diferencias

  C-03             Etapa de fallback no                                         Corregido             §5.5 describe tres etapas; la
                   documentada                                                                        reserva no registró casos

  C-04             No existía ningún dato de tiempo                             Parcial               200 pares versionados; los 81
                                                                                                      telefónicos coinciden con su
                                                                                                      registro primario, los 119 de
                                                                                                      correo y web no (N-05)

  C-05             Contrabalanceo imposible con                                 Corregido             §4.2 declara ejecución
                   datos retrospectivos                                                               secuencial y que el
                                                                                                      contrabalanceo no se ejecutó

  C-06             Tres relatos incompatibles del                               Corregido             Un solo relato: cronometraje
                   instrumento manual                                                                 mutuo en vivo, redondeo hacia
                                                                                                      arriba

  C-07             W = 0 incompatible con la                                    Corregido             W = mín(T+, T−) = 363, T+ =
                   convención de SciPy                                                                19.737, ambos declarados

  C-08             Fórmula y rango del tamaño del                               Corregido             r = (T+ − T−)/[n(n+1)/2] = 0,9639,
                   efecto                                                                             rango [−1, +1] (Kerby, 2014)

  C-09             «Varianza diez veces menor»                                  Corregido             Se habla de desvío (44,9 s frente
                                                                                                      a 13,52 s)

  C-10             180 horas-persona imposibles                                 Corregido             32,2 h brutas, con cálculo al pie, y
                                                                                                      balance neto en §9.5

  C-11             Intervención humana definida                                 Corregido             Tabla 3 rotula las dos
                   de dos formas                                                                      dimensiones y §8.3 informa
                                                                                                      ambas

  Código           Hallazgo de agosto                                           Estado                Evidencia en la v1.2.18

  C-12             Clasificador descalibrado sin                                Corregido             §8.4 y Tabla 14: la confianza de
                   advertirlo                                                                         Gemini (0,85–1,00) no discrimina;
                                                                                                      el gate no derivó ningún caso

  C-13             3.700 incidentes incompatibles                               Corregido             42 × 63 = 2.646
                   con 42 diarios

  C-14             Exactitud humana nunca medida                                Corregido             Campaña complementaria:
                                                                                                      0,8278 manual, McNemar no
                                                                                                      significativo

  C-15             165,3 s coincidía con la                                     Corregido             Media experimental de 61,6 s,
                   estimación preliminar                                                              distinta de la preliminar

  C-16             El IF de confianza precede al                                Corregido             En el flujo, «Requiere revision
                   clasificador                                                                       humana» está aguas abajo del
                                                                                                      POST

  C-17             Agente telefónico sin modelo                                 Corregido             El nodo AI Agent fue retirado; la
                   conectado                                                                          telefonía usa la cascada del
                                                                                                      backend

  C-18             canal_origen no llegaba al                                   Corregido             El POST envía canal_origen_id
                   backend

  C-19             Reintento inexistente                                        Corregido             retryOnFail, 3 intentos, 5 s, en la
                                                                                                      configuración entregada; la tesis
                                                                                                      aclara que no es la evaluada

  C-20             TLS y Nginx inexistentes                                     Corregido             nginx/ y servicio en docker-
                                                                                                      compose; §5.1 aclara que la
                                                                                                      medición telefónica corrió sin
                                                                                                      proxy

  C-21             27 brechas conocidas no                                      Parcial               Tabla 19 distingue configuración
                   reflejadas                                                                         evaluada, entregada y de
                                                                                                      campaña; el Anexo I no traza la
                                                                                                      auditoría de agosto (N-02)

  C-22             Prompt con cuatro sectores                                   Corregido             Taxonomía de cinco sectores
                                                                                                      canónicos coherente en prompt,
                                                                                                      modelo y resultados

  C-23             Tag v1.0.0 inexistente                                       Corregido             Tag anotado v1.2.18 sobre
                                                                                                      457b14ae…, verificado

  Código           Hallazgo de agosto                                           Estado                Evidencia en la v1.2.18

  C-24             Misatribución de Revina et al.                               Corregido             §3.3 y §9.2 informan la
                   (2020)                                                                             conclusión real y discuten la
                                                                                                      tensión

  C-25             Kappa mal rotulado y sin Landis                              Abierto               Etiqueta y cita corregidas, pero
                   y Koch                                                                             el κ = 0,87 sigue sin tabla y con
                                                                                                      procedencia dudosa (N-01)

  C-26             Cero artículos arbitrados                                    Corregido             ≈18 arbitrados 2023–2026 y
                   recientes                                                                          protocolo de búsqueda
                                                                                                      declarado

  C-27             Rango 88–94 % sin cita                                       Corregido             Rango retirado; comparación
                                                                                                      declarada no directa

  C-28             Tres errores jurídicos                                       Parcial               Retención de 12 meses, art. 5.2.d,
                                                                                                      adecuación en la dirección
                                                                                                      correcta y transferencia previa
                                                                                                      del audio declarada; falta
                                                                                                      precisar el instrumento del art. 12
                                                                                                      efectivamente usado (N-13)

El cuerpo de hallazgos altos, medios y bajos de agosto quedó atendido en su gran mayoría:
fórmula de exactitud multiclase, criterios de exclusión, potencia a priori, Shapiro-Wilk
informado, desglose por canal, ejemplos textuales de error, diez figuras, capturas del
panel, fuentes en tablas y ortografía (las 52 formas «diseñó», «desarrolló», «completó» y
«aquéllos» desaparecieron). Persisten A-08 (no se informa el porcentaje de cobertura del
backend) y la concisión, que empeoró (N-07).

4. Verificación independiente de cifras y artefacto
Todas las cifras recalculadas coinciden con las publicadas; ninguna discrepa más allá del
redondeo. Es el cambio de mayor peso respecto de agosto, cuando 7 de 24 verificaciones
fallaron.

  Cifra publicada                  Valor en la tesis            Recálculo de             Fuente del recálculo
                                                                esta auditoría

  Tiempo manual:                   61,6 / 50,0 / 44,9 s         61,585 / 50,0 /          data/corpus_evaluacion_pseudonimizado.json
  media, mediana,                                               44,90 s
  desvío

  Cifra publicada                  Valor en la tesis            Recálculo de             Fuente del recálculo
                                                                esta auditoría

  Tiempo                           17,76 / 17,47 /              17,761 / 17,471          ídem
  automatizado:                    13,52 s                      / 13,516 s
  media, mediana,
  desvío

  Reducción de la                  71,2 % / 65,1 %              71,16 % /                ídem
  media y de la                                                 65,06 %
  mediana

  Wilcoxon bilateral               W = 363, p =                 W = 363, p =             scipy.stats.wilcoxon
                                   3,08e−32                     3,085e−32

  T+ y T−                          19.737 / 363                 19.737 / 363             rangos recalculados

  Rank-biserial r                  0,9639                       0,96388                  (T+ − T−)/20.100

  dz                               1,00                         1,0004                   43,82 / 43,81

  Shapiro-Wilk                     0,803 / 0,902 /              0,8031 /                 scipy.stats.shapiro
  (manual,                         0,822                        0,9022 /
  automático,                                                   0,8225
  diferencias)

  Pares en que el                  12 de 200                    12                       ídem
  automático no fue
  más rápido

  Sensibilidad −5 s /              68,6 % / 65,6 %; r           68,61 % /                ídem
  −10 s                            = 0,8683                     65,57 %; r =
                                                                0,8683

  Por canal:                       77,0 / 51,1 / 93,4           77,0 / 51,1 /            ídem
  reducción y dz                   %; 1,37 / 0,73 /             93,4 %; 1,37 /
                                   1,61                         0,73 / 1,61

  Matriz de                        diagonal                     idéntica                 evaluation/evidence/predicciones_hybrid-
  confusión (Tabla                 15+77+48+0+7 =               celda a celda            v3_2026-10-07.json
  11)                              147

  Exactitud estricta               73,5 % [67,0;                0,735 [0,670;            statsmodels
  e IC de Wilson                   79,1]                        0,791]

  Macro-F1 de                      0,6508 / 0,5207              0,65084 /                ídem
  umbral (4 clases) y                                           0,52067
  de 5 clases

  Exactitud laxa                   179/200                      179                      ídem

  Etapas:                          131 (97 aciertos) /          131 (97) / 69            ídem
  determinística y                 69 (50)                      (50)
  Gemini

  Cifra publicada                  Valor en la tesis            Recálculo de             Fuente del recálculo
                                                                esta auditoría

  Confianza de                     mínimo 0,85;                 0,85; 22/31 y            ídem
  Gemini                           bandas 22/31 y               28/38
                                   28/38

  Kappa nuevo, po,                 0,5569; 0,69;                0,55686; 0,69;           evaluation/data/campana/doble_etiquetado.csv
  pe, PABAK                        0,30; 0,6125                 0,30045;
                                                                0,6125

  IC asintótico del                [0,4725; 0,6413]             [0,4725;                 fórmula de Fleiss, Cohen y Everitt
  kappa (Fleiss et al.,                                         0,6413]
  1969)

  Exactitud manual                 71/80 = 0,8875;              71/80; 54/71             brazo_manual.csv contra consenso E1–E2
  O1 / O2                          54/71 = 0,7606

  Intervenciones                   25 de 147; Wilson            25/147; [11,79;          intervenciones.csv
  que cambiaron la                 [11,8; 23,9] %               23,90] %
  derivación

  Prueba binomial                  p = 0,28                     p = 0,2796               scipy.stats.binomtest
  contra 0,15                                                   unilateral
                                                                (0,488
                                                                bilateral)

  Consenso nuevo                   116 de 138                   116/138                  doble_etiquetado.csv y corpus
  igual al sector
  original

  Margen de error                  6,66 %                       6,664 %                  fórmula con corrección por finitud
  con n = 200 y N =
  2.646

  Ahorro bruto                     32,2 h                       32,19 h                  43,82 s × 2.646 / 3.600
  trimestral

  Balance neto                     −18,5 h; a* = 77,7           −18,51 h; 77,7           fórmula de §9.5
  central (15 %, 10                %                            %
  min)

Artefacto verificado en el tag v1.2.18.

       El flujo n8n/workflow.json tiene 32 nodos (29 operativos y 3 notas), como declaran
       §6.3 y el Anexo E.
       El nodo condicional «Requiere revision humana» recibe la salida del POST: la
       compuerta quedó aguas abajo del clasificador.
       No queda ningún nodo de LangChain; el canal telefónico entra por webhook y se
       clasifica en el backend.
       El POST envía canal_origen_id, reportante_email y reportante_telefono.

       Los nodos HTTP declaran retryOnFail con 3 intentos y 5.000 ms, y la creación desvía
       los errores a una rama propia.
       docker-compose.yml incluye Nginx en la red edge, con terminación TLS.
       Las predicciones, la tabla primaria del doble etiquetado (400 registros), el brazo
       manual (220 registros) y las intervenciones (147) están versionados.

Bibliografía. Se buscaron externamente cinco referencias nuevas. Colavito et al. (2025),
Bernal-Beltrán et al. (2025) y Ramón-Ferrer et al. (2026) existen con los metadatos
citados. De Mayor-Rocher et al. se confirmó la versión de arXiv de 2024, no la de Applied
Linguistics (2026) que cita la tesis. Paket et al. (2024) no pudo localizarse en esta
instancia (N-16). No se detectó ninguna referencia fabricada.

5. Observaciones de esta instancia
Se registran 16 observaciones: 2 críticas, 6 altas, 5 medias y 3 bajas. Las críticas son de
procedencia y declaración; ninguna exige nuevo desarrollo.

Críticas
N-01. El κ = 0,87 no tiene respaldo y su origen es anterior al corpus que describe.
Resumen, Abstract, §1.7, §4.4 y §4.8.

       La tesis admite que la tabla de acuerdo «no se conservó», pero sigue presentando el
       valor como acuerdo de los analistas originales.
       El mismo 0,87 ya figuraba en la versión de julio, compilada cuando el repositorio
       declaraba el corpus real como «trabajo de campo futuro» y cuando, según la propia
       §4.2, el brazo manual aún se estaba cronometrando (junio a agosto).
       El doble etiquetado independiente nuevo da 0,5569 (moderado), y el consenso nuevo
       coincide con el sector original solo en 116 de 138 casos (84,1 %).
       Corrección exigida: retirar el 0,87 del Resumen, del Abstract y de la Introducción
       como evidencia de fiabilidad, o exhibir las planillas que lo sustentan con su fecha. Si no
       existen, declararlo en una oración en §4.4.

N-02. La tesis no declara que la versión de julio informó resultados de un corpus
sintético. Anexo I.

       La bitácora de los autores (docs/Tesis/Correcciones/dictamen-correcciones.md) dice
       que los valores de la versión anterior «siguen siendo los del corpus sintético
       descartado». El archivo docs/anexo_f_corpus.md atribuye ese descarte a «los
       revisores».

       El Anexo I traza nueve autoevaluaciones generadas con un modelo de lenguaje, pero
       omite la auditoría del tribunal del 4 de agosto, que está en el propio repositorio
       (auditorias/) y que originó la reformulación.
       Corrección exigida: una nota de versiones de media página, al inicio del Anexo I, que
       diga qué informó la versión del 3 de julio (165,3 s, 92 %, W = 0, κ = 0,87), que esas cifras
       provenían de un corpus sintético y que fueron reemplazadas. Agregar la auditoría del
       4 de agosto como primera fila de la trazabilidad.

Altas
N-03. Los tiempos manuales de la campaña complementaria no se informan. §4.5 y §8.7.
brazo_manual.csv registra inicio y fin por caso para O1 y O2 (220 registros), y la tesis los
usa solo para el efecto de posición. Recalculados en esta auditoría:

 Operador                      Casos Media                         Media automatizada (mismos                            Reducción p
                                     manual                        casos)                                                          (Wilcoxon)

 O1                            110          20,1 s                 13,3 s                                                33,8 %    9,8 × 10⁻⁷

 O2                            110          76,6 s                 15,5 s                                                79,7 %    9,0 × 10⁻²⁰

 Agregado por                  200          47,6 s                 14,6 s                                                69,3 %    3,0 × 10⁻²⁸
 caso

El resultado agregado replica el de la campaña 2026-10 con sujetos independientes y
fortalece la tesis. Pero muestra que la magnitud depende del operador (34 % a 80 %).
Además, los tiempos manuales por caso de ambas campañas no se correlacionan
(Spearman 0,15 y −0,05): el tiempo manual no es una propiedad estable del incidente. Hay
un registro de 0 s (R025, O1). Corrección exigida: informar esta tabla en §8.7, aclarar si la
tarea manual de ambas campañas es la misma (lectura y carga del ticket, o solo la decisión
de sector) y discutir la dependencia del operador en §9.1.

N-04. El mecanismo de selección de los 200 casos es contradictorio. §4.4. La tesis dice
que el corpus se construyó «por muestreo estratificado con asignación proporcional» y,
párrafos después, que los 200 casos «son los incidentes efectivamente cronometrados»
por disponibilidad. También admite que la distribución del universo no está disponible. No
se declaran las fechas del «período relevado» ni cómo se eligieron 200 de unos 2.646
incidentes (7,6 %). Corrección exigida: describir una sola forma de selección, con fechas
y criterio, y si fue por conveniencia, llamarla así y llevar el sesgo de selección a §4.8.

N-05. 119 de los 200 tiempos automatizados carecen de registro primario verificable.
§4.5 y Anexo F. Los 81 telefónicos coinciden exactamente con
data/corpus_resultados_telefonia.json (duración más latencia). Los 119 de correo y
formulario no coinciden con ningún registro versionado: data/corpus_resultados.json
tiene otra corrida (media de 0,41 s) y el registro de la ingesta por n8n tiene 4 filas frente a

119 y no se versiona, según data/README.md. Corrección exigida: declarar en §4.5 que
esos 119 valores no tienen respaldo primario conservado y de dónde se transcribieron, o
versionar el registro.

N-06. El brazo telefónico automatizado se alimentó con llamadas recitadas por un autor.
§4.5. Un autor parafraseó las descripciones pseudonimizadas en un softphone. Hubo dos
configuraciones distintas entre el 5 y el 6 de octubre, y la versión de los 56 casos del día 6
«no consta». Un locutor que conoce el caso y el sistema habla más claro y más breve que
un usuario real, lo que favorece tiempo y exactitud del canal. Corrección exigida:
incorporarlo como amenaza a la validez en §4.8 y como explicación rival en §9.1.

N-07. La escritura perdió concisión y el texto se lee como bitácora de cambios. Todo el
documento. El cuerpo pasó de ≈26.000 a ≈35.200 palabras. La mediana de oración subió
de 28 a 34 palabras; las oraciones de más de 40 palabras, del 21,7 % al 37,1 %; y las de más
de 60, del 3,7 % al 13,5 %. Hay 47 «de modo que», 166 remisiones «Subsección» e
identificadores internos de cambios (c-82, c-153, C-61…) en cuerpo, tablas y epígrafes.
Corrección exigida: sacar los identificadores de cambio del cuerpo (pueden quedar en el
Anexo I) y partir las oraciones de más de 60 palabras de los capítulos 1, 4, 8 y 9.

N-08. Las métricas primarias se calculan contra una referencia cuya fiabilidad no se
puede demostrar. §8.2 y §9.3. La exactitud de 73,5 % se mide contra el etiquetado original
(sin tabla de acuerdo); contra el consenso independiente nuevo, la exactitud es 0,7971
sobre 138 casos. La tesis lo informa como limitación, pero lo deja fuera de las tablas de
resultados. Corrección exigida: agregar a la Tabla 12 una fila con la exactitud contra el
consenso nuevo y su IC, para que el lector vea ambas referencias juntas.

Medias
N-09. La regla de decisión de la segunda sub-hipótesis se fijó después de ver los datos.
§1.4 y §8.3. Según el Anexo I (Tablas 22 y 24), la proporción quedó «sin concluir» y el
change c-190 la declaró «refutada» después. Con 25/147, IC [11,8 %; 23,9 %] y p = 0,28, la
lectura estadística correcta es no concluyente con estimación puntual sobre la cota. La
decisión va contra el interés de los autores, lo que la atenúa, pero debe declararse
posterior. Indicar también que p = 0,28 es unilateral.

N-10. No se informa el porcentaje de cobertura de las pruebas del backend. §6.7. Se da el
comando pero no el valor, mientras el frontend sí lo informa (99,6 %).

N-11. Las Figuras 2, 7, 8 y 10 son ilegibles a tamaño de impresión. Su texto queda por
debajo de 6 puntos en A4. Pasar a orientación apaisada o dividir por capas.

N-12. Las conclusiones conservan valoraciones sin respaldo y repiten cifras. §10.1: «un
valor que lo posiciona como una vía prácticamente útil» sobre 20,1 s de tiempo telefónico,
que es cota inferior y fue medido con llamadas recitadas (N-06). Sintetizar en lugar de
reiterar los números del capítulo 8.

N-13. Falta decir qué instrumento del art. 12 de la Ley 25.326 se usó durante el estudio.
§7.3. La tesis explica bien que hacen falta consentimiento o cláusulas modelo (Disposición
60-E/2016), pero no dice si se celebraron. Si en el estudio solo cruzó texto pseudonimizado
y audio recitado por un autor, decirlo, y dejar el instrumento como requisito del adoptante.

Bajas
N-14. El Anexo I (Tabla 26, A1) dice que la confirmación escrita del consentimiento «queda
diferida», mientras §7.5 la da por firmada. El registro del repositorio la fecha el 10/11/2026:
actualizar el anexo.

N-15. Los nombres de sector aparecen sin tilde en la prosa («Seguridad Informatica»,
«Soporte Tecnico»). Si son cadenas canónicas del sistema, ir en monoespaciado; en la
prosa, con tilde.

N-16. Aportar copia o DOI verificable de Paket et al. (2024) y aclarar si Mayor-Rocher et al.
se cita en su versión de revista o de arXiv.

6. Calificación por capítulo
Con los mismos pesos de la auditoría de agosto, el promedio ponderado da 6,97, que se
informa como 7,0. Las mayores subas están en Resultados (de 1,5 a 6,5) y Anexos (de 2,5 a
7,0).

 Capítulo                     Correspondencia en                  Agosto Esta                      Peso        Motivo principal
 evaluado                     la tesis                                   instancia

 Introducción                 Cap. 1                              6,5          7,5                 8%          Hipótesis desdoblada con
                                                                                                               criterios de falsación; aritmética
                                                                                                               del universo corregida; persiste
                                                                                                               κ = 0,87 en §1.7

 Marco teórico                Caps. 2 y 3                         6,0          7,5                 8%          Eje de LLM con calibración,
                                                                                                               alucinación e idioma; protocolo
                                                                                                               de búsqueda declarado;
                                                                                                               Whisper ubicado como marco

 Marco                        Cap. 4                              3,5          6,0                 15 %        Instrumento único, potencia,
 metodológico                                                                                                  exclusiones y Shapiro-Wilk;
                                                                                                               restan N-01, N-04, N-06 y N-09

 Desarrollo                   Caps. 6 y 7                         5,5          7,5                 12 %        Flujo, reintentos y TLS alineados
                                                                                                               con el repositorio; marco legal
                                                                                                               corregido; falta N-10 y N-13

 Resultados                   Cap. 8                              1,5          6,5                 20 %        Cifras reproducibles dígito a
                                                                                                               dígito; restan N-03, N-05 y N-08

 Capítulo                     Correspondencia en                  Agosto Esta                      Peso        Motivo principal
 evaluado                     la tesis                                   instancia

 Arquitectura                 Cap. 5                              5,0          7,5                 10 %        Cinco capas, diagramas de
                                                                                                               despliegue y ER, siete entidades
                                                                                                               coherentes; figuras poco
                                                                                                               legibles (N-11)

 Discusión                    Cap. 9                              3,0          7,0                 10 %        Explicaciones rivales, balance
                                                                                                               neto con punto de equilibrio y
                                                                                                               lectura honesta de la
                                                                                                               calibración; falta la dependencia
                                                                                                               del operador

 Conclusiones                 Caps. 10 y 11                       2,5          6,5                 7%          Objetivos con grado de
                                                                                                               cumplimiento realista;
                                                                                                               valoraciones residuales y cifras
                                                                                                               repetidas (N-12)

 Referencias                  Bibliografía                        5,5          8,0                 6%          ≈18 artículos arbitrados 2023–
                                                                                                               2026, sin fabricaciones
                                                                                                               detectadas; dos por confirmar
                                                                                                               (N-16)

 Anexos                       Anexos A–I                          2,5          7,0                 4%          Corpus, prompt, configuración y
                                                                                                               trazabilidad con contenido real;
                                                                                                               Anexo I incompleto (N-02)

 Global                                                           3,9          7,0                 100
 ponderado                                                                                         %

   0{,}08(7{,}5)+0{,}08(7{,}5)+0{,}15(6{,}0)+0{,}12(7{,}5)+0{,}20(6{,}5)+0{,}10(
   7{,}5)+0{,}10(7{,}0)+0{,}07(6{,}5)+0{,}06(8{,}0)+0{,}04(7{,}0)=6{,}97

Índice de calidad de escritura: 6,9 / 10 (antes 6,8). Mejoraron la corrección ortográfica (de
4,5 a 8,5), la precisión terminológica (8,0) y el estilo científico (7,5). Empeoraron la
concisión (de 5,5 a 4,0) y la claridad (de 7,5 a 6,0), por la longitud de las oraciones y las
calificaciones acumuladas en cada corrección.

Fortalezas que el tribunal debe reconocer.

       Reproducibilidad completa de las cifras del estudio desde el repositorio público.
       Honestidad metodológica infrecuente: la tesis refuta dos de sus tres sub-hipótesis,
       declara las métricas como estimaciones dentro de la muestra y estima el sesgo del
       ajuste con el corpus (Tabla 15).
       Análisis de balance neto con exactitud mínima de equilibrio (Tabla 17), que convierte
       un resultado mixto en una regla de decisión útil para un adoptante.
       Campaña complementaria con etiquetadores y operadores independientes, plan pre-
       registrado y tablas primarias versionadas.

       Corrección completa del marco jurídico y alineación del sistema con lo que el texto
       describe.

7. Correcciones obligatorias antes de la defensa
Son diez correcciones de escritura y declaración, ordenadas por prioridad; se estiman en 3
a 5 días de trabajo y no requieren código nuevo ni nuevas mediciones.

   1. Retirar o documentar el κ = 0,87 del Resumen, del Abstract, de §1.7, §4.4 y §4.8 (N-
       01).
   2. Agregar la nota de versiones al inicio del Anexo I, con las cifras de julio, su origen
       sintético y la auditoría del 4 de agosto como primera fila de la trazabilidad (N-02).
   3. Informar los tiempos manuales de la campaña complementaria por operador y
       agregados, y discutir la dependencia del operador (N-03).
   4. Describir una sola forma de selección de los 200 casos, con fechas del período y
       criterio (N-04).
   5. Declarar la procedencia de los 119 tiempos de correo y formulario o versionar su
       registro primario (N-05).
   6. Agregar la recitación por un autor a las amenazas a la validez y a las explicaciones
       rivales (N-06).
   7. Agregar a la Tabla 12 la exactitud contra el consenso independiente (0,7971 sobre 138
      casos) con su IC (N-08).
   8. Declarar posterior la regla de tres vías de la segunda sub-hipótesis e indicar que p =
       0,28 es unilateral (N-09).
   9. Sacar los identificadores de cambio del cuerpo y partir las oraciones de más de 60
       palabras (N-07).
10. Atender las observaciones medias y bajas N-10 a N-16.

La nota de 7,0 refleja el documento tal como fue entregado. La defensa se evaluará sobre
el ejemplar corregido y sobre las respuestas del grupo a la Sección 8.

8. Preguntas probables del tribunal
Se recomienda que el grupo prepare una respuesta escrita para cada una.

Sobre la procedencia de los datos

   1. ¿En qué fecha etiquetaron los analistas originales los 200 casos y dónde está la
       planilla del κ = 0,87, si ese valor ya figuraba en la versión del 3 de julio?
   2. La versión de julio informó 165,3 s, 92 % y W = 0. ¿De dónde salieron esas cifras y por
       qué la tesis actual no lo dice?

   3. ¿Cómo eligieron 200 incidentes entre unos 2.646, y en qué fechas exactas transcurrió
       el período relevado?
   4. ¿De qué registro se transcribieron los 119 tiempos automatizados de correo y
       formulario del 2 de octubre?

Sobre el contraste de tiempos

   5. En la campaña complementaria O1 tardó 20,1 s de media y O2 76,6 s. ¿Cuánto de la
       reducción del 71,2 % depende de quién opere?
   6. ¿La tarea manual de la campaña complementaria (inicio a fin en la planilla) es la misma
       que la de la campaña 2026-10 (lectura, búsqueda y carga del ticket)?
   7. ¿Por qué los tiempos manuales del mismo caso no se correlacionan entre las dos
       campañas?
   8. ¿Qué efecto tiene que las llamadas automatizadas las haya recitado un autor que
       conocía el caso?
   9. En el formulario web el automático mide 1,88 s desde el envío y el manual 28,7 s desde
       la lectura. ¿Miden el mismo tramo del proceso?

Sobre la clasificación y la supervisión humana

10. Si el consenso independiente coincide con la etiqueta original solo en el 84 % de los
       casos, ¿cuál es la exactitud «verdadera» del clasificador?
11. La compuerta de 0,70 no derivó ningún caso y la etapa determinística resuelve el 65,5
       % sin derivación por confianza. ¿Qué supervisión humana efectiva tiene hoy el
       sistema?
12. De 85 confirmaciones humanas con consenso disponible, 11 confirmaron un sector
       incorrecto. ¿Qué dice eso de la revisión como salvaguarda?
13. ¿Cuándo se fijó la regla de tres vías de la segunda sub-hipótesis, antes o después de
    conocer el 17,0 %?
14. Con el escenario central el balance neto es de −18,5 a −43,9 horas-persona por
       trimestre. ¿Recomendarían adoptar el sistema hoy?

Sobre el marco legal

15. ¿Se firmó alguna cláusula contractual modelo de la Disposición 60-E/2016 con Google
       o Twilio, o en el estudio solo se transfirieron datos pseudonimizados y audio recitado?
16. Las autoevaluaciones del Anexo I se generaron con un modelo de lenguaje. ¿Qué parte
       del texto de la tesis fue redactada con asistencia de un modelo de lenguaje y cómo lo
       declaran?
