# Devolución de tercera instancia — TFI «Automatización inteligente del registro de incidentes en mesas de ayuda empresariales»

> Transcripción del documento original, extraída con `pdftotext -layout` del PDF adjunto (`Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.pdf`); el PDF es la evidencia de referencia, esta transcripción solo facilita la búsqueda y la trazabilidad. Las tablas de las secciones 3, 4 y 6 pierden la alineación de columnas en la extracción.
>
> Entrega auditada: versión 1.5.2 (14/11/2026) · Emisión: 16/11/2026 · Dictamen: apta para defensa, condicionada a K-01 y K-02 · Calificación: **6,7 / 10** (antes 7,0 / 10).

---

Devolución de tercera instancia — TFI «Automatización inteligente del registro de incidentes en mesas de ayuda empresariales»

Devolución de tercera instancia — TFI
«Automatización inteligente del registro de
incidentes en mesas de ayuda empresariales»

Entrega auditada: versión 1.5.2 (14/11/2026) · Fecha de emisión: N​ ov 16, 2026

1. Ficha y alcance de la verificación

Esta devolución audita la versión 1.5.2 contra las 16 observaciones de la devolución de
segunda instancia (11/11/2026, calificación 7,0/10) y contra el repositorio en el commit que
contiene el PDF entregado.

Campo        Dato

Título       Automatización inteligente del registro de
             incidentes en mesas de ayuda empresariales
             mediante orquestación de flujos con N8N y
             procesamiento de lenguaje natural basado en
             modelos de lenguaje grandes

Autores      Luca Gomez · Carla Bustos · Gonzalo Sevilla

Directores   Prof. Alberto Cortez y Prof. Ariel Enferrel

Institución  UTN — Facultad Regional Mendoza, Tecnicatura
             Universitaria en Programación

Archivo      tesis_ultima_version.pdf — versión 1.5.2, fechada el
             14/11/2026

Extensión    164 páginas (antes 120) · cuerpo ≈51.900 palabras
             (antes ≈43.600, medido con el mismo método) · 33
             tablas · 14 figuras · 10 anexos (A–J)

Repositorio  github.com/lucaGomezB/Automatizacion-de-
             Mesa-de-Ayuda-N8N — tag anotado v1.5.2
             (5509cbf); el PDF entregado es byte a byte el del
             commit siguiente, 7335fa5, que consigna el hash en
             el Anexo B

Cambios desde la instancia anterior 253 commits entre v1.2.18 y v1.5.2 (11 al 16/11/2026),
                                                      41 de ellos co-firmados por un asistente de IA

Devolución de tercera instancia — TFI «Automatización inteligente del registro de incidentes en mesas de ayuda empresariales»

Campo             Dato
Instancia previa
                  Devolución de segunda instancia del 11/11/2026: 16
                  observaciones (2 críticas, 6 altas, 5 medias, 3
                  bajas), 7,0/10

Planos verificados en esta instancia.

  1. Textual: lectura completa de los 11 capítulos y los 10 anexos, con rastreo de cada
     observación de segunda instancia y de la coherencia entre resumen, resultados,
     discusión y conclusiones.

  2. Cuantitativo: recálculo independiente de las cifras nuevas (validación fuera de
     muestra, línea de base, brazo de modelo solo, calibración, balance neto) sobre los
     archivos versionados.

  3. Artefacto: clonado del repositorio, inspección de las tablas primarias de etiquetado,
     del registro de la ingesta del 2/10, del análisis del costo de derivación y de la historia
     de commits.

  4. Procedencia: análisis de las marcas temporales de las cinco planillas de etiquetado y
     de los dos operadores, y lectura de los 206 textos del corpus fuera de muestra.

  5. Bibliográfico: verificación externa de las dos referencias pendientes (N-16).

Cuando un dato no pudo comprobarse, se lo indica como no verificable y no como falso.

2. Dictamen

APTA PARA DEFENSA, CONDICIONADA A K-01 Y K-02. Calificación global: 6,7 / 10
(antes 7,0 / 10).

No se fija fecha de defensa hasta que el grupo acredite la procedencia y la autorización
del corpus fuera de muestra, o lo retire del ejemplar con todo lo que depende de él.
Cumplida esa condición y las correcciones de la Sección 7, la proyección es de 7,4 / 10.

Síntesis. El grupo atendió la segunda instancia con rigor: de las 16 observaciones, 14
quedan corregidas y 2 parcialmente, y los 28 críticos de agosto quedan todos cerrados. El
κ = 0,87 salió del Resumen, la nota de versiones declara el origen sintético de las cifras de
julio y los tiempos de los operadores independientes ya se informan. Esta auditoría
verificó además que los 118 tiempos de correo y formulario son coherentes con el registro
de la base. El núcleo del trabajo, la reducción del tiempo de registro de 61,6 s a 17,76 s
sobre el corpus de 200 casos, sigue siendo reproducible y sólido.

Por qué la nota baja. En cinco días se agregó evidencia nueva que esta auditoría no puede
acreditar como se la describe:

Devolución de tercera instancia — TFI «Automatización inteligente del registro de incidentes en mesas de ayuda empresariales»

     Las 476 marcas temporales del etiquetado fuera de muestra (E3, E4, E5) no tienen la
     forma de un registro manual: todas las duraciones caen entre 30 y 90 s, con
     distribución uniforme, y las pausas entre casos son de 1 a 8 s, sin interrupciones
     durante sesiones de más de dos horas (K-01).

     Los 56 casos de refuerzo tienen la forma de un catálogo de tipos de incidente crítico,
     no de tickets reportados por usuarios de una compañía financiera entre noviembre de
     2025 y febrero de 2026 (K-01).

     Los datos provienen de una tercera organización sin autorización documentada, están
     publicados en el repositorio y se enviaron a la Gemini API, y el Capítulo 7 no lo trata (K-
     02).

     El balance neto pasó de −18,5 a +30,6 horas-persona con «signo fijado por la muestra»,
     pero omite el tiempo de revisión que el propio análisis del grupo midió y usa un costo
     de derivación que solo cubre el tramo activo (A-01).

Por qué no es «no apta». Ninguno de esos puntos afecta la evidencia principal, que ya
estaba verificada en la segunda instancia y sigue intacta. La validación fuera de muestra
no fue exigida por este tribunal; si no puede acreditarse, se retira y la tesis vuelve a
sostenerse sobre lo que sí está verificado.

3. Estado de las observaciones de segunda instancia

De las 16 observaciones del 11 de noviembre, 14 quedan corregidas y 2 parcialmente (N-07
y N-15). Con ello se cierran también los cuatro críticos de agosto que seguían parciales o
abiertos (C-04, C-21, C-25 y C-28): los 28 críticos de la auditoría del 4 de agosto quedan
corregidos.

Código Observación de segunda    Estado     Evidencia en la v1.5.2
              instancia

N-01  κ = 0,87 sin respaldo      Corregida  Retirado del Resumen, el
                                            Abstract y §1.7; §4.4 declara que
                                            no puede respaldarse; la
                                            fiabilidad se estima con κ =
                                            0,5569

N-02  No se declaraba el corpus  Corregida  Anexo I.1 informa 165,3 s, 92 %, W
      sintético de julio                    = 0 y κ = 0,87 y su origen
                                            sintético; I.2 nombra la auditoría
                                            del 4/8 como primera revisión

Devolución de tercera instancia — TFI «Automatización inteligente del registro de incidentes en mesas de ayuda empresariales»

Código Observación de segunda            Estado     Evidencia en la v1.5.2
              instancia

N-03  Tiempos manuales de O1 y O2        Corregida  Tabla 22 (20,1 s y 76,6 s; 33,8 % a
      sin informar                                  79,7 %); §4.5 declara que la tarea
                                                    difiere; §9.1 la discute como
                                                    quinta explicación rival

N-04  Selección de los 200 casos         Corregida  §4.4: muestra por conveniencia,
      contradictoria                                sin estratificación, período del
                                                    16/6 al 10/9; §4.8, quinta amenaza

N-05  119 tiempos sin registro primario  Corregida  Registro de la base de 118 de 119
                                                    casos versionado (R001 sin
                                                    registro, declarado). Verificado:
                                                    ver Sección 4

N-06  Llamadas recitadas por un autor Corregida §4.8, sexta amenaza; §9.1, sexta
                                                                           explicación rival; §10.1

N-07 Concisión y bitácora de cambios Parcial        Identificadores de cambio en el
                                                    cuerpo: de 83 a 0. Oraciones de
                                                    más de 60 palabras: de 134 a 85.
                                                    Pero el cuerpo creció un 19 %
                                                    (ver M-03)

N-08  Falta la exactitud contra el       Corregida Tabla 14: 110/138 = 0,797 [0,722;
      consenso                                             0,856] y macro-F1 0,757

N-09  Regla de la segunda sub-           Corregida  §1.4 y §8.3 declaran el
      hipótesis posterior a los datos               denominador posterior; p
                                                    unilateral 0,28 y bilateral 0,49

N-10  Cobertura del backend sin          Corregida  §6.7: 88 % en la configuración
      informar                                      evaluada y 90 % en la entregada,
                                                    con sentencias y pruebas

N-11  Figuras ilegibles                  Corregida Figuras 2 y 7 a 10 divididas en
                                                           partes y a página completa

N-12  Valoraciones sin respaldo en       Corregida  Retirada la valoración del canal
      conclusiones                                  telefónico; ver A-01 para la nueva
                                                    sobre el balance

N-13  Instrumento del art. 12 sin        Corregida  §7.3: el instrumento no se
      precisar                                      suscribió y queda como requisito
                                                    del adoptante. Para el corpus
                                                    nuevo, ver K-02

Devolución de tercera instancia — TFI «Automatización inteligente del registro de incidentes en mesas de ayuda empresariales»

Código Observación de segunda          Estado    Evidencia en la v1.5.2
              instancia

N-14  Consentimiento «diferido» en el  Corregida La tabla se retiró; §7.5 es
      Anexo I                                            coherente

N-15  Nombres de sector sin tilde en la Parcial  En tablas van en monoespaciado;
      prosa                                      en la prosa siguen en la fuente
                                                 del cuerpo y sin tilde, mezclados
                                                 con formas acentuadas (B-01)

N-16  Paket et al. y Mayor-Rocher et al. Corregida Ambas con DOI; la copia de Paket
                                                                           et al. se declara obtenida el 14/11

4. Verificación independiente de cifras y artefacto

Todas las cifras nuevas que se recalcularon coinciden con las publicadas. La aritmética no
es el problema de esta versión; lo es la procedencia de una parte de los datos (Sección 5).

Cifra publicada     Valor en la      Recálculo   Fuente
                    tesis            de esta     corpus_independiente_arbitrado.json
Exactitud estricta                   auditoría   y predicciones_arbitrado.json
fuera de muestra                                 ídem y corpus de 200
(206)               142/206 =        142/206;
                    0,6893 [0,6231;  Wilson      arbitraje_tres_vias.json
Lecturas            0,7486]          [0,6231;
complementarias                      0,7486]     ídem
                                                 doble_etiquetado_independiente.csv
Por origen de la    0,7489           0,74890;
referencia          ponderada;       112/150
                    112/150 =
Exactitud laxa y    0,7467
macro-F1 (206)
κ de E3 y E4 (150   109/142          109/142;
casos)              consenso;        33/64
                    33/64
                    arbitrado

                    162/206;         162;
                    0,7024           0,70243

                    0,6055; 103      0,60548;
                    coincidencias    103

Devolución de tercera instancia — TFI «Automatización inteligente del registro de incidentes en mesas de ayuda empresariales»

Cifra publicada     Valor en la                Recálculo   Fuente
                    tesis                      de esta     binomial exacta
                                               auditoría
McNemar híbrido     61 y 20
frente a línea de   discordantes;              p = 5,66 ×
base                p = 5,7 × 10⁻⁶             10⁻⁶

McNemar híbrido     3y6                        p = 0,5078 binomial exacta
frente a modelo     discordantes;
solo (103)          p = 0,5078                 0,51684     predicciones_hybrid-v3_2026-10-
                                                           07.json
AUROC de la         0,5168 (69
confianza de        casos, 50                  +30,64 h;   fórmula de §9.5
Gemini (in-         aciertos)                  a* = 19,74  load_test_multicanal_2026-11-13.json
sample)                                        %
                    +30,6 h; a* =
Balance neto        19,7 %                     coincide
central

Test de carga, p95  1215,8 ms
con 20              backend;
concurrentes        6788,4 ms
                    webhook

Registro primario de los 119 tiempos (N-05). El archivo
data/corpus_resultados_web_correo.json cubre 118 casos. En formulario web, el tiempo
del corpus supera al de la base entre 0,08 y 0,35 s (correlación de Spearman 0,98), lo
esperable por el envío. En correo lo supera entre 8,5 y 63 s, compatible con un sondeo
IMAP de un minuto. La observación queda cerrada.

Marcas temporales de las planillas de etiquetado y del brazo manual. Según el runbook
del doble etiquetado, cada etiquetador anota a mano el inicio y el fin de cada caso. Las
cuatro planillas anteriores tienen la irregularidad propia de ese registro; las tres del 12 y 13
de noviembre, no.

Sujeto Registros Duración                 Pausa mediana Pausa máxima  Pausas de                                                Ajuste a una uniforme
                            por caso (s)                              más de 60                                                (p de Kolmogorov-
                                          entre casos dentro de la    s                                                        Smirnov)
                                                                      44                                                       < 0,001
                                          (s)  sesión (s)             122                                                      < 0,001
                                                                      12                                                       < 0,001
E1  200          0 a 113                  15   4.471                  50                                                       < 0,001

E2  200          0 a 158                  94   3.190

O1  110          0 a 57                   3    823

O2 110           42 a 178                 52   310

Devolución de tercera instancia — TFI «Automatización inteligente del registro de incidentes en mesas de ayuda empresariales»

Sujeto Registros Duración                 Pausa mediana Pausa máxima  Pausas de                                                Ajuste a una uniforme
                            por caso (s)                              más de 60                                                (p de Kolmogorov-
                                          entre casos dentro de la    s                                                        Smirnov)

                                          (s)  sesión (s)             0                                                        0,66

E3  206  30 a 90                          3    5                      0                                                        0,58

E4  206  30 a 90                          4    8                      0                                                        0,35

E5  64   30 a 88                          3    5

E3 etiquetó 150 casos seguidos el 12/11 entre las 15:23 y las 17:57, y E4 entre las 14:59 y las
17:43. En ese lapso, ninguno de los dos se detuvo más de 5 u 8 segundos entre un caso y el
siguiente, y ninguna duración quedó fuera del intervalo de 30 a 90 s. Las pausas de E3 y E5
toman solo los valores enteros de 1 a 5 s.

Bibliografía (N-16). Se confirmó la versión arXiv de Mayor-Rocher et al. (2409.15334); la
versión de revista que cita la tesis (Applied Linguistics, 2026) y el artículo de Paket et al.
(UBMK 2024) no pudieron consultarse en esta instancia, pero ambos traen DOI y el grupo
declara tener la copia. No se detectó ninguna referencia fabricada.

5. Observaciones de esta instancia

Se registran 12 observaciones: 2 críticas, 3 altas, 4 medias y 3 bajas. Las dos críticas se
refieren a la evidencia agregada entre el 12 y el 14 de noviembre; ninguna afecta el
contraste de tiempos ni las métricas sobre el corpus de 200 casos.

Críticas

K-01. La procedencia del corpus fuera de muestra no es verificable, y sus registros no
coinciden con lo que la tesis describe. §4.4, §8.4, §8.6, §8.9, §8.10, §8.12, Resumen y
Abstract.

La tesis describe 150 incidentes reales de una compañía financiera, ocurridos entre el
2/11/2025 y el 12/2/2026, más 56 de refuerzo con el mismo origen. Según la tesis, los
etiquetaron a ciegas E3 y E4 y los arbitró E5. Dos rasgos de los artefactos versionados no
son compatibles con esa descripción:

     Las marcas temporales de E3, E4 y E5 (476 registros) no tienen la forma de un registro
     manual (Sección 4). Todas las duraciones caen entre 30 y 90 s con distribución
     uniforme, y las pausas entre casos nunca superan los 8 s en sesiones de más de dos
     horas. Las planillas de E1, E2, O1 y O2 no muestran ese patrón.
     Los 56 casos de refuerzo (I151 a I206) tienen la forma de un catálogo de tipos de
     incidente crítico, no de tickets de usuarios de una sola compañía en tres meses. Entre
     ellos hay un ataque masivo de ransomware (I156), una exfiltración de datos de clientes
     (I173), un zero-day (I176), una intrusión en sistemas SCADA (I182), dos aislamientos

Devolución de tercera instancia — TFI «Automatización inteligente del registro de incidentes en mesas de ayuda empresariales»

     forenses por orden judicial (I192, I193), un incendio en el CPD detectado por sensores
     IoT (I194) y el colapso de una cola Kafka (I191). También aparecen cajas registradoras
     de locales comerciales (I163) y camiones de un depósito (I171). Varios traen una glosa
     que define el término, ajena a un ticket. Por ejemplo, I177 dice: «Se cayó el firewall
     perimetral principal. Se ha interrumpido el dispositivo que filtra y protege el tráfico de
     red». Los 150 originales, en cambio, tienen el registro propio de una mesa de ayuda,
     errores de tipeo incluidos.

A eso se suma el cronograma. Los 150 casos se incorporaron y se etiquetaron el 12/11 y se
clasificaron esa misma noche. El 13/11, en una ventana de seis horas, se reunieron y
etiquetaron los 56 de refuerzo, 40 de ellos de Sistemas, después de conocer el bajo
desempeño en esa clase. Ese mismo día se arbitraron 64 casos.
Esta auditoría no afirma que los datos sean inventados. Afirma que, tal como están
versionados, no pueden aceptarse como el registro primario que la tesis describe. El
antecedente de julio, con cifras de un corpus sintético, obliga a pedir una acreditación
expresa.

Corrección exigida: una de dos opciones antes de fijar la defensa.
  1. Acreditar la procedencia ante el director, para el tribunal, con tres elementos. Primero,
     las planillas originales de E3, E4 y E5 tal como se completaron, con los metadatos del
     archivo. Segundo, la exportación original de los 206 incidentes desde el sistema de la
     compañía, con sus fechas. Tercero, una declaración de cómo se generaron las marcas
     temporales y los textos del refuerzo. Si alguno fue construido o reconstruido, debe
     declararse en la tesis.
  2. Retirar del ejemplar la validación fuera de muestra y todo lo que depende de ella: §8.9,
     la parte fuera de muestra de §8.4 y §8.6, §8.10, §8.12, las cifras fuera de muestra del
     Resumen, de §1.7, §9 y §10, la Tabla 31 y el Anexo J. La tesis se sostiene sin ellos.

K-02. El uso de datos de una tercera organización no tiene encuadre ético ni legal en la
tesis. §4.4, Capítulo 7.

La única mención de la compañía financiera está en §4.4. El Capítulo 7 no dice si la
compañía autorizó el uso de sus incidentes, si sus empleados fueron informados ni con
qué base de licitud se los trató. Solo trata el consentimiento de los etiquetadores.
Mientras tanto, los 206 textos están publicados en el repositorio público
(corpus_independiente.json y corpus_independiente_arbitrado.json), con nombres de
sucursales y referencias al «sistema principal». Además se enviaron a la Gemini API en las
corridas del 12 y el 13/11 y en el brazo de modelo solo. Por eso §7.3 ya no es exacta: sigue
diciendo que a los proveedores llegaron solo 119 textos y 81 audios.

Devolución de tercera instancia — TFI «Automatización inteligente del registro de incidentes en mesas de ayuda empresariales»

Corrección exigida: incorporar al expediente la autorización escrita de la compañía y
agregar en §7.5 un párrafo con la base de licitud y el alcance de esa autorización. También
hay que corregir §7.3 con todas las transferencias. Si la autorización no existe, retirar los
textos del repositorio público y de la tesis.

Altas

A-01. El balance neto positivo con «signo fijado» no está respaldado. Resumen, §9.5, §10,
Tabla 31.

El costo c = 69,51 s suma dos tramos. El primero son 24,01 s de corrección en la compuerta
de revisión. El segundo son 45,50 s de la mediana de decisión de sector del brazo manual,
tomada como proxy del rediagnóstico. El tramo de reanudación queda «sin cota
disponible» (Anexo J). En la configuración evaluada la compuerta no detecta errores
(AUROC 0,5168, ninguna derivación por confianza), de modo que los errores llegan al
sector receptor. Ese costo se aproxima con el tiempo de decidir un sector sobre una hoja,
no con el de un equipo que toma un ticket ajeno, lo diagnostica y lo devuelve. Por lo tanto,
c es una cota inferior y B una cota superior.

Además, el análisis del propio grupo (analisis_costo_derivacion_c220.md) midió un tiempo
de revisión de 22,06 s por intervención. Ese mismo análisis registra que el flujo
automatizado sí agrega ese tiempo, en contra del supuesto del balance, y no lo incorpora a
B. Recalculado por esta auditoría con la tasa de revisión observada (147/200), B baja de
+30,6 a +18,7 horas-persona. Con la exactitud cruda fuera de muestra baja a +13,2. Con 10
minutos por reasignación y esa exactitud es de −28,9, valor que la propia §9.5 informa. El
signo depende de un tramo que no se midió.

Corrección exigida: incluir el término de revisión en B y presentar c como el tramo activo
medido, es decir, como cota inferior del costo. B debe presentarse como cota superior.
Hay que retirar «signo fijado por la muestra» y «viabilidad económica y operativa positiva»
del Resumen, de §9.5, de §10 y de la Tabla 31, y restituir la lectura condicional de la versión
anterior.

A-02. La validación «fuera de muestra» es en otra organización, y la tesis la presenta
como si fuera la misma. Resumen, §1.7, §1.8, §8.9, §9.3, §10.2.

El Resumen, §1.7 y §8.9 hablan de un «corpus independiente» sin decir que proviene de
otra organización y de otro sector. Al mismo tiempo, §1.8 dice que la validación se realiza
sobre un corpus de la organización de Mendoza. La segunda limitación de §9.3 y §10.2
afirman que los datos provienen de una sola organización, «el único contexto en que se
evaluó». El runbook del grupo (c-166) pedía «casos nuevos del organismo», y el cambio de
fuente no se declara como desvío del plan. Tampoco se explica cómo se asignaron las
áreas de la compañía financiera a los cinco sectores de la organización de Mendoza. Sin
esa explicación, el 0,6893 mezcla error de generalización con desajuste de taxonomía.

Devolución de tercera instancia — TFI «Automatización inteligente del registro de incidentes en mesas de ayuda empresariales»

Corrección exigida (si la validación se conserva tras K-01): llamarla validación en una
segunda organización y declararlo en el Resumen y el Abstract. Hay que conciliar §1.8,
§9.3 y §10.2, describir la correspondencia de sectores y discutir el desajuste de taxonomía
como explicación rival.

A-03. La declaración de uso de IA es más acotada que lo que registra el repositorio.
Anexo I.2.

La tesis declara asistencia de un modelo de lenguaje «para la corrección de estilo y la
edición del texto, y para la generación de diagramas». El repositorio registra más que eso:

     AGENTS.md es una guía para sesiones de un agente de código.
     CHANGES.md organiza el trabajo en cambios que «un agente puede implementar en
     una sesión».
     41 de los 253 commits de esta versión están co-firmados por un asistente de IA.
     Las tareas archivadas de los cambios encargan al agente la redacción de la prosa de la
     tesis. Por ejemplo, el bloque «Prosa de la tesis» de c-222 incluye reemplazar el costo c,
     declarar la viabilidad operativa y alinear el Resumen.

El uso de estas herramientas no es en sí una falta. Lo que se exige es que la declaración
sea completa.

Corrección exigida: una declaración que indique qué partes del código, de los scripts de
análisis y del texto produjo un asistente de IA, con qué herramientas y cómo verificaron
los autores cada cifra y cada afirmación. Debe ajustarse a la normativa de la facultad.

Medias

M-01. La justificación del umbral del 85 % contradice el costo medido. §1.6. El texto
sostiene que, por debajo del 85 %, los tiempos de resolución serían comparables a los del
flujo manual. Con el c que la tesis adopta, la exactitud de equilibrio es 19,7 %, por lo que el
argumento queda refutado por las propias cifras. El otro fundamento, la paridad con el
82,78 % del brazo manual, se midió en noviembre y no puede justificar un umbral fijado a
priori. Corrección: declarar que el 85 % es un criterio fijado a priori por los autores y
trasladar a la discusión, rotulados como posteriores, los argumentos que dependen de
mediciones nuevas.

M-02. La hipótesis de eficiencia se decide sobre el subconjunto más fácil. §4.7 y §8.10,
Tabla 27. El brazo de modelo solo se midió sobre los 103 casos de consenso. La propia §8.9
reconoce que ese subconjunto sesga la referencia hacia los casos fáciles. La exactitud
primaria, en cambio, se informa sobre los 206 casos, donde la etapa Gemini del híbrido
acierta solo 54 de 91 (0,5934). En el bloque primario el modelo solo supera al híbrido en la
estimación puntual (0,8738 frente a 0,8447). En el bloque dentro de la muestra, 112 casos
se reintentaron por una decisión tomada después de ver los resultados. Corrección: si la

Devolución de tercera instancia — TFI «Automatización inteligente del registro de incidentes en mesas de ayuda empresariales»

validación se conserva, medir el brazo de modelo solo sobre los 206 casos, con un costo
estimado menor de USD 0,30 al precio estándar, o declarar por qué no se hizo y acotar la
conclusión.
M-03. La tesis creció en extensión y perdió legibilidad. Todo el documento. La tesis pasó
de 120 a 164 páginas y el cuerpo, de ≈43.600 a ≈51.900 palabras (+19 %), medido con el
mismo método en ambas versiones. Hubo mejoras: los identificadores de cambio salieron
del cuerpo (de 83 a 0), las oraciones de más de 60 palabras bajaron de 134 a 85 y «de modo
que», de 52 a 29. Pero el Capítulo 8 tiene ahora doce apartados con cifras rotuladas como
primaria, complementaria, sensibilidad, cota de alcance, vigente o superada, y el lector no
encuentra en un solo lugar qué se concluye. El Anexo J transcribe un memo interno con
columnas de estado («vigente (nuevo)»), en el registro de una bitácora. Corrección: abrir
el Capítulo 8 con una tabla única de cifras primarias y llevar a un anexo §8.6, §8.12 y las
tablas de robustez. También hay que quitar del Anexo J la columna de estado y las
referencias al memo, y partir las 85 oraciones de más de 60 palabras.
M-04. El documento de respuestas al tribunal contradice la versión entregada.
docs/defensa/respuestas-tribunal.md. La respuesta a Q14 sostiene un balance de −18,5 a
−43,9 horas-persona y una viabilidad operativa condicional. La de Q15 dice que a los
proveedores llegaron solo 119 textos y 81 audios. Ninguna de las dos coincide con la v1.5.2.
Corrección: actualizar el documento antes de la defensa, en concordancia con lo que
resulte de K-01, K-02 y A-01.

Bajas

B-01. Los nombres de sector siguen sin tilde en la prosa y en la fuente del cuerpo
(«Seguridad Informatica» en §1.6, §1.8 y §9), mezclados con formas acentuadas en otros
párrafos («Soporte Técnico Hardware 85» en §4.4). En las tablas ya van en monoespaciado.
Unificar: monoespaciado para la cadena del sistema y forma con tilde en la prosa (N-15).
B-02. Hay que aclarar la cronología de E3 y E4. El registro de sujetos los incorpora en el
commit ed4b386 del 11/11, pero §7.5 dice que fueron informados verbalmente el 12/11.
Según §4.4, los casos se incorporaron «el 12 y el 13», y E4 comenzó a etiquetar a las 14:59
del 12/11.
B-03. Las tablas del Anexo J (p. 162) tienen texto superpuesto en la columna de
procedencia («justificacion_umbral.paridad_manual» sobre «vigente») y rutas espaciadas
letra por letra («. . . c 2 2 0 . j s»).

Devolución de tercera instancia — TFI «Automatización inteligente del registro de incidentes en mesas de ayuda empresariales»

6. Calificación por capítulo

Con los mismos pesos de las instancias anteriores, el promedio ponderado da 6,69, que se
informa como 6,7. Suben Marco teórico, Arquitectura y Referencias, por las correcciones
de la segunda instancia. Bajan Introducción, Desarrollo, Resultados, Discusión y
Conclusiones, por K-01, K-02 y A-01. Metodología y Anexos quedan igual: lo que se corrigió
se compensa con lo que se agregó sin respaldo.

Capítulo      Correspondencia  Agosto Segunda          Esta       Peso Motivo principal
evaluado      en la tesis                   instancia  instancia
                                                       7,0
Introducción  Cap. 1           6,5  7,5                8,0        8 % κ = 0,87 retirado; la
                                                                             justificación del 85 %
                                                       6,0                   contradice el c medido
                                                                             (M-01) y §1.8 contradice
                                                       6,5                   el corpus nuevo (A-02)

Marco teórico Caps. 2 y 3      6,0  7,5                6,0        8 % Calibración, Brier y
                                                       8,0                   AUROC, cascadas, línea
                                                                             de base TF-IDF y
                                                                             acuerdo entre
                                                                             anotadores bien
                                                                             fundados

Marco         Cap. 4           3,5  6,0                           15 %  N-01, N-04, N-06 y N-09
                                                                        resueltos y ocho
metodológico                                                            amenazas declaradas,
                                                                        pero el diseño fuera de
                                                                        muestra descansa en un
                                                                        corpus no acreditado
                                                                        (K-01)

Desarrollo    Caps. 6 y 7      5,5  7,5                           12 %  Cobertura informada e
                                                                        instrumento del art. 12
                                                                        precisado; el Capítulo 7
                                                                        no trata los datos de la
                                                                        tercera organización (K-
                                                                        02)

Resultados    Cap. 8           1,5  6,5                           20 %  N-03, N-05 y N-08
                                                                        cerrados y verificados;
                                                                        §8.9 a §8.12 dependen
                                                                        del corpus no
                                                                        acreditado

Arquitectura Cap. 5            5,0  7,5                           10 %  Figuras legibles (N-11);
                                                                        flujo único de
                                                                        clasificación coherente
                                                                        con el repositorio

Devolución de tercera instancia — TFI «Automatización inteligente del registro de incidentes en mesas de ayuda empresariales»

Capítulo     Correspondencia  Agosto Segunda          Esta       Peso Motivo principal
evaluado     en la tesis                   instancia
                                                      instancia
Discusión    Cap. 9
                              3,0  7,0                6,0        10 % Seis explicaciones

                                                                      rivales bien planteadas;

                                                                      balance sobreestimado

                                                                      (A-01) y contradicciones

                                                                      sobre la organización

                                                                      (A-02)

Conclusiones Caps. 10 y 11    2,5  6,5                6,0        7 % Objetivos con grado de

                                                                      cumplimiento realista;

                                                                      «viabilidad económica y

                                                                      operativa positiva» sin

                                                                      respaldo

Referencias  Bibliografía     5,5  8,0                8,5        6 % N-16 atendida con DOI;

                                                                      sin referencias

                                                                      fabricadas detectadas

Anexos       Anexos A–J       2,5  7,0                7,0        4 % Nota de versiones

                                                                      honesta (N-02);

                                                                      declaración de IA

                                                                      incompleta (A-03) y

                                                                      Anexo J con formato de

                                                                      bitácora

Global                        3,9  7,0                6,7        100
ponderado
                                                                 %

  0{,}08(7{,}0)+0{,}08(8{,}0)+0{,}15(6{,}0)+0{,}12(6{,}5)+0{,}20(6{,}0)+0{,}10(
  8{,}0)+0{,}10(6{,}0)+0{,}07(6{,}0)+0{,}06(8{,}5)+0{,}04(7{,}0)=6{,}69

Proyección. Con K-01 y K-02 resueltos (por acreditación o por retiro) y A-01 a A-03 y las
medias corregidas, las notas por capítulo pasarían a 7,5 · 8,0 · 7,0 · 7,5 · 7,0 · 8,0 · 7,5 · 7,0 · 8,5
· 7,5, con un global de 7,4.

Fortalezas que el tribunal debe reconocer.

     Respuesta completa y verificable a la segunda instancia: 14 de 16 observaciones
     cerradas en cinco días, con los 28 críticos de agosto resueltos.
     Honestidad en la nota de versiones. La tesis declara que las cifras de julio y el κ = 0,87
     provenían de un corpus sintético.
     Análisis de calibración con regla prerregistrada y resultado adverso informado: la
     confianza de Gemini no sostiene ningún umbral (AUROC 0,5168, verificado).
     Test de carga con regla de decisión fijada antes de medir, y veredicto «no sostenida»
     informado sin rodeos.
     Seis explicaciones rivales del contraste de tiempos, incluidas la dependencia del
     operador y la recitación de las llamadas.

Devolución de tercera instancia — TFI «Automatización inteligente del registro de incidentes en mesas de ayuda empresariales»

     Reproducibilidad: todas las cifras recalculadas coinciden con los archivos
     versionados.

7. Correcciones obligatorias y condición para fijar la defensa

Las dos primeras son condición para fijar fecha de defensa; las demás deben estar en el
ejemplar que se lleve al acto. Ninguna exige código nuevo. Si se opta por retirar la
validación fuera de muestra, el trabajo total se estima en 3 a 5 días.

  1. K-01. Acreditar ante el director, para el tribunal, la procedencia del corpus fuera de
     muestra (planillas originales de E3, E4 y E5, exportación original de los 206 incidentes
     y declaración sobre las marcas temporales y los textos del refuerzo), o retirarlo del
     ejemplar con todo lo que depende de él.

  2. K-02. Incorporar la autorización escrita de la compañía, agregar su encuadre en §7.5 y
     corregir §7.3. Sin autorización, retirar los textos del repositorio público.

  3. A-01. Incluir el tiempo de revisión en el balance, presentar c como cota inferior y B
     como cota superior, y restituir la lectura condicional en el Resumen, §9.5, §10 y la Tabla
     31.

  4. A-02. Si la validación se conserva, nombrarla como validación en una segunda
     organización, declararlo en el Resumen y el Abstract, conciliar §1.8, §9.3 y §10.2 y
     describir la correspondencia de sectores.

  5. A-03. Reemplazar la declaración del Anexo I.2 por una completa sobre el uso de
     asistentes de IA en el código, el análisis y el texto.

  6. M-01. Declarar el 85 % como criterio a priori y mover a la discusión los argumentos
     posteriores.

  7. M-02. Medir el brazo de modelo solo sobre los 206 casos o acotar la conclusión de
     eficiencia.

  8. M-03. Abrir el Capítulo 8 con una tabla de cifras primarias, llevar a un anexo las
     lecturas de sensibilidad, depurar el Anexo J y partir las oraciones de más de 60
     palabras.

  9. M-04. Actualizar el documento de respuestas al tribunal.
10. Atender las observaciones bajas B-01 a B-03.
La nota de 6,7 refleja el documento tal como fue entregado. La defensa se evaluará sobre
el ejemplar corregido y sobre las respuestas del grupo a la Sección 8.

Devolución de tercera instancia — TFI «Automatización inteligente del registro de incidentes en mesas de ayuda empresariales»

8. Preguntas probables del tribunal

Se recomienda que el grupo prepare una respuesta escrita para cada una. Las respuestas
a las 16 preguntas de la segunda instancia siguen vigentes, una vez actualizadas según M-
04.
Sobre el corpus fuera de muestra

  1. ¿Quiénes son E3, E4 y E5 respecto de la compañía financiera y de los autores, y cómo
     registraron el inicio y el fin de cada caso?

  2. ¿Por qué todas las duraciones de E3, E4 y E5 caen entre 30 y 90 s y ninguna pausa
     entre casos supera los 8 s?

  3. ¿De qué sistema se exportaron los 56 casos de refuerzo? ¿En qué fecha ocurrieron,
     por ejemplo, la intrusión en SCADA (I182) y el incendio del CPD (I194)?

  4. ¿La compañía autorizó el uso de sus incidentes, su publicación en el repositorio y su
     envío a Google?

  5. ¿Cómo se asignaron las áreas de la compañía a los cinco sectores de la organización
     de Mendoza?

Sobre el balance neto
  6. Cuando una derivación errónea llega al sector equivocado, ¿cuánto tarda ese sector
     en advertirlo y devolverla? ¿Por qué los 45,5 s de decisión de sector del brazo manual
     representan ese costo?
  7. ¿Por qué el balance no descuenta los 22 s de revisión por caso que su propio análisis
     midió?
  8. Con la exactitud fuera de muestra y 10 minutos por reasignación, el balance es de
     −28,9 horas-persona. ¿Qué le recomendarían hoy a una organización adoptante?

Sobre la clasificación
  9. En el bloque primario, el brazo de modelo solo acertó más que el híbrido. ¿Qué aporta
     hoy la etapa de reglas, además del ahorro de llamadas?

10. ¿Por qué el contraste de eficiencia usa los 103 casos de consenso y la exactitud
     primaria, los 206?

Sobre la autoría
11. ¿Qué partes del código de análisis y del texto de la tesis produjeron los asistentes de

     IA registrados en el repositorio, y cómo verificaron los autores cada cifra?
12. ¿Cómo se distribuyó entre los tres autores el trabajo de esta última versión?


