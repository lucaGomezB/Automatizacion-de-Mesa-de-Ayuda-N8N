# Introduccion
 
## Capitulo 1 (1.1 - 1.8)

Coherencia. El hilo conductor es sólido y explícito: contextualización → problema medido →
pregunta → hipótesis → objetivos → justificación → alcance. Es la mejor cadena argumental
del trabajo y está por encima de la media de la carrera. El §1.6 fundamenta el umbral del
85 % con tres criterios convergentes explicitados, práctica infrecuente y meritoria.
Rupturas detectadas.
• A-01 (Alta). El §1.2 proyecta 3.700 incidentes trimestrales desde 42 diarios; la
aritmética no cierra (C-13).
• A-02 (Alta). El §1.2 estima el costo de la etapa de registro «en el orden de 200 horas-
persona por trimestre». Con los propios datos (3.700 × 165,3 s) el valor es 169,9 h.
Ninguna de las dos cifras de horas que el trabajo publica (200 en §1.2, 180 en §8.1) es
derivable de sus insumos.
• A-03 (Alta). El tercer criterio del umbral del 85 % en §1.6 —«el margen por encima
del 85 % reserva espacio estadístico para que el intervalo de confianza del estimador
no solape la zona de rechazo de la hipótesis»— confunde el contraste de la hipótesis
sobre tiempos (H0/H1 del §1.4, que es sobre medianas de tiempo) con el umbral de
exactitud del clasificador. No hay «zona de rechazo» definida para la exactitud.
• M-01 (Media). El §1.1 atribuye a «la Secretaría de la Pequeña y Mediana Empresa» la
definición de empresa mediana (50-200 trabajadores en servicios) sin cita ni entrada
bibliográfica: cita huérfana.
• M-02 (Media). El §1.7 afirma que «la mayoría de los estudios publicados sobre
clasificación automática de tickets utilizan corpus en inglés, alemán o portugués, y los
pocos trabajos que incluyen el español lo hacen con variantes peninsulares» sin una
sola referencia que lo sostenga. Es la premisa de la contribución académica declarada.
• B-01 (Baja). El §1.2 y el §1.8 alternan «organización mediana del sector servicios
con sede en la provincia de Mendoza» y «única organización», sin nombrarla ni
caracterizarla más allá de los 120 usuarios y cinco áreas.
Profundidad científica. Adecuada. El planteamiento del problema se apoya en mediciones
preliminares propias, lo que es más de lo que suele verse. Falta, en cambio, cualquier
discusión de por qué la mediana argentina es un caso distinto del que la literatura
internacional estudia más allá de la restricción cambiaria, que se menciona pero no se
cuantifica.
Calidad académica. Buena. Terminología estable y registro formal sostenido.
Coherencia interna. El eslabón débil es el segundo interrogante subsidiario del §1.3
(comparación con el criterio humano), que nunca se responde (C-14).
Calificación: 6,5 / 10.

# Marco Teorico

## Capitulo 2 (2.1 - 2.7)

Coherencia. Los siete ejes están bien elegidos y cada uno tiene función instrumental
posterior: ITSM e ITIL fundan la unidad de análisis, orquestación versus coreografía funda
la decisión arquitectónica, las métricas multiclase fundan el Capítulo 7. Es un marco teórico
útil, no decorativo, lo cual lo distingue favorablemente.
Debilidades detectadas.
• A-04 (Alta). El §2.4 es el eje central del trabajo —modelos de lenguaje grandes— y
se resuelve en cuatro párrafos con tres referencias, dos de ellas de 2017 y 2020. No
hay tratamiento de prompting, calibración de confianza, alucinación, sensibilidad al
idioma ni evaluación de LLM, todos ellos conceptos que el trabajo usa operativamente
en capítulos posteriores sin haberlos definido.
• A-05 (Alta). El §2.7 define la exactitud global con la fórmula binaria (T P +
T N )/(T P + T N + F P + F N ) y a continuación aclara que «para problemas de
clasificación multiclase, la exactitud se calcula como la proporción de predicciones
correctas sobre el total». Presentar primero una fórmula que no aplica al problema y
corregirla en la oración siguiente es un defecto de precisión conceptual en el capítulo
que define el instrumento de medición.
• A-06 (Alta). El §2.2 atribuye ITIL Service Operation (edición 2011) a la Office of
Government Commerce. La edición 2011 fue publicada por TSO en nombre del Cabinet
Office; la OGC corresponde a la edición 2007. Requiere verificación por los autores.
• M-03 (Media). El §2.5 describe Whisper con detalle (680.000 horas, segmentos de 30
s) y concluye que «la disponibilidad de modelos preentrenados de código abierto para
español facilita su integración en el canal telefónico del sistema propuesto». Whisper
no se usa en el sistema: el §6.4 emplea la transcripción nativa de Twilio. Toda la sección
es teoría sin correlato en el artefacto.
• M-04 (Media). El §2.6 justifica PostgreSQL sobre alternativas no relacionales sin
considerar ninguna alternativa concreta; es una justificación por afirmación.
• B-02 (Baja). Jurafsky y Martin (2023) se cita como obra de Pearson cuando el tercer
volumen es un borrador de libre acceso no publicado por esa editorial.
Profundidad. Desigual: §2.3 (orquestación vs. coreografía) y §2.7 (métricas) son sólidos;
§2.4 y §2.6 son superficiales para el peso que cargan.
Calificación: 6,0 / 10.

# Marco Metodologico

## Corresponde al Capitulo 4 (4.1 a 4.9), el Capitulo 3 de la tesis es el estado del arte y se evalua en la seccion de revision bibliografica. Este es el capitulo con mayor concentracion de hallazgos criticos

lementos correctamente tratados. La operacionalización de variables (Tabla 2) tiene
tipo, unidad y definición operacional por variable, práctica infrecuente y meritoria. El §4.8
identifica cuatro amenazas a la validez con su tratamiento, por iniciativa propia. La elección
de pruebas no paramétricas está justificada con un contraste previo de normalidad. Se
declaran el nivel de significancia, el método de intervalo de confianza (Wilson) y la biblioteca
de cálculo.
Debilidades adicionales a las críticas ya documentadas.
• A-07 (Alta). El §4.4 declara «nivel de confianza del 95 % y un margen de error del
6,5 %» y una «corrección por finitud aplicada al universo trimestral observado», pero
no publica el cálculo ni la proporción esperada supuesta. Con N = 3.700, z = 1,96,
21p = 0,5 y e = 0,065 el tamaño resultante es 219, no 200. Con e = 0,068 da 200. El
margen declarado no reproduce el tamaño declarado.
• A-08 (Alta). El §4.5 afirma cobertura de pruebas unitarias «superior al 80 %» y el §6.7
la precisa en 87 %; ninguno de los dos publica el informe de cobertura ni el comando
que lo genera.
• A-09 (Alta). No hay ningún análisis de potencia estadística a priori, pese a que el §4.8
identifica el tamaño muestral como amenaza a la validez de conclusión.
• A-10 (Alta). El §4.2 declara «rotación de operadores entre las dos mitades del corpus»
como mitigación, pero con dos operadores y dos mitades la rotación no puede separarse
del efecto de operador: el diseño confunde ambos factores.
• M-05 (Media). No se declara ningún criterio de exclusión de incidentes del corpus
(duplicados, descripciones vacías, incidentes multicategoría), pese a que el §7.4
identifica «descripciones cortas» y «mezcla de categorías» como los dos patrones de
error dominantes.
• M-06 (Media). El §4.9 (Scrumban) es gestión de proyecto, no metodología de
investigación, y su ubicación en el capítulo metodológico desdibuja la distinción entre
el método del estudio y el método de construcción del artefacto.
• M-07 (Media). No se declara quiénes fueron los dos analistas que etiquetaron el
corpus, ni su independencia respecto de los autores, ni si alguno de ellos es también
uno de los dos operadores del brazo manual. Si lo fueran, el ground truth y el brazo de
comparación compartirían sujeto.
Calificación: 3,5 / 10.

# Desarrollo del Estudio

## Capitulo 6 (6.1 - 6.8)

Fortalezas. Es, junto con el Capítulo 5, la mejor ingeniería documentada del trabajo. El §6.2
justifica la elección de FastAPI contra Flask y Django REST con criterios técnicos concretos y
no por preferencia. La descomposición en capas (models, schemas, services, repositories,
classifiers, routes, core) se corresponde exactamente con la estructura real del
repositorio, verificada en esta auditoría. El §6.5 (desafíos de integración) es un ejercicio
de honestidad técnica poco común, y el §6.7 describe una estrategia de pruebas en pirámide
con instrumentos concretos.
Debilidades.
• Los críticos C-16 a C-22 se localizan íntegramente en este capítulo.
• A-11 (Alta). El §6.7 afirma «pruebas extremo a extremo que ejecutaban el flujo
completo desde el envío de un correo simulado hasta la persistencia del ticket,
validando la integración con N8N en su totalidad». No hay ninguna prueba de ese tipo
en el repositorio: las 22 suites de backend cubren unidades, esquemas, repositorios e
integración con base de datos, pero ninguna instancia de N8N.
• A-12 (Alta). El §6.7 declara «una suite de 89 pruebas automatizadas» en el frontend
«con una cobertura de sentencias del 98,6 %» y las desagrega en 27 servicios, 10 hooks,
43 páginas y gráficos y 9 componentes compartidos (suma: 89). El recuento de casos
it( / test( en los archivos de prueba del repositorio da 68. La cifra publicada no se
reproduce y la cobertura del 98,6 % no está respaldada por ningún informe versionado.
• A-13 (Alta). El §6.4 informa una latencia telefónica de extremo a extremo de 12
a 15 segundos «según las observaciones operativas durante la fase de validación»,
desglosada en tres tramos con rangos. Dado C-17 (el agente no puede ejecutarse),
esas observaciones no son atribuibles al flujo publicado. Además la cifra carece de n,
22de dispersión y de procedimiento.
• M-08 (Media). El §6.8 describe el dashboard con tres visualizaciones y controles de
filtro, y cierra con un ejemplo hipotético («si el sistema detecta que veinte usuarios han
reportado la rotura de auriculares...»). El ejemplo se presenta como «utilidad práctica
[...] se ilustra con un caso concreto» cuando es un caso imaginado. No hay ninguna
captura del dashboard en el documento.
• M-09 (Media). El §6.1 declara preparación «para migración a un clúster Kubernetes
1.30» sin ningún manifiesto en el repositorio.
Calificación: 5,5 / 10.

# Resultados

## Capitulo 7 (7.1 - 7.4)

Este es el capítulo que determina el dictamen. Se le aplican los críticos C-01, C-02, C-03,
C-04, C-07, C-08, C-11 y C-12.
Lo que el capítulo hace bien —y debe reconocerse. La presentación es formalmente
impecable: estadísticos descriptivos completos con desvíos, rangos e intervalos de
confianza; matriz de confusión íntegra; métricas por clase y macro promedio; análisis
cualitativo de los 16 errores con una tipología de tres patrones y sus frecuencias.
La verificación aritmética independiente de las cifras publicadas arrojó 17
comprobaciones correctas sobre 24: la matriz de confusión de la Tabla 7 cierra en filas,
columnas y total; las nueve métricas por clase de la Tabla 8 son exactas hasta el tercer
decimal a partir de esa matriz; el macro promedio es correcto; la exactitud del 92 % y
la distribución de los 16 errores por patrón (7 + 6 + 3) son consistentes. Ese nivel de
consistencia interna es excepcional.
El problema no es que las cifras estén mal calculadas. Es que no se sabe de dónde salen.
Debilidades adicionales.
• A-14 (Alta). El §7.1 afirma «La reducción relativa de la media de tiempo alcanzó el
89,0 %» y la Tabla 6 consigna «89,0 %» tanto para la media como para la mediana. El
cálculo da 88,99 % en ambos casos — coincidencia hasta el segundo decimal entre dos
estadísticos independientes que, con datos reales, sería extraordinaria.
• A-15 (Alta). No se reporta el estadístico ni el valor p concreto de la prueba de Shapiro-
Wilk que el §4.7 dice haber aplicado, ni por grupo ni sobre las diferencias.
• A-16 (Alta). No se reporta ningún resultado de tiempo desagregado por canal, pese
a que el canal es variable del estudio (Tabla 2) y a que la latencia telefónica declarada
en §6.4 (12-15 s) y el máximo del flujo automatizado de la Tabla 6 (31 s) sugieren
distribuciones muy distintas por canal.
• M-10 (Media). El §7.4 tipifica los 16 errores pero no publica ni un solo ejemplo textual
de incidente mal clasificado, lo cual haría el análisis verificable sin comprometer
privacidad.
• M-11 (Media). El capítulo tiene cero figuras: ni un diagrama de cajas de los tiempos,
ni un mapa de calor de la matriz de confusión, ni una curva de calibración.
Calificación: 1,5 / 10. La forma es sobresaliente; el fundamento probatorio, ausente.

# Arquitectura e interfaz de visualizacion

## Capitulo 5 (5.1 - 5.7)

Fortalezas. La arquitectura de cinco capas está bien delimitada, con responsabilidades
claras y justificación de la separación. El §5.5 (subsistema de clasificación híbrido) describe
un diseño correcto y efectivamente implementado: la verificación del repositorio
confirma umbrales configurables de 0,90 para cortocircuitar la etapa determinística y 0,70
para marcar revisión humana, tal como el texto declara. El §5.6 y el §5.7 (modelo de datos
y contrato REST) son precisos y el Anexo D (OpenAPI) los respalda con un archivo real
de 39 KB con prueba de sincronización en integración continua. La declaración de que
la clasificación está embebida en POST /api/v1/incidentes y no expuesta como recurso
independiente coincide con el código.
Debilidades.
• C-20 (TLS/Nginx inexistentes) se localiza aquí.
• A-17 (Alta). La Figura 1 es la única figura del trabajo en 74 páginas. Es un diagrama
de flujo dibujado a mano alzada, sin notación normalizada, con seis cajas y una
decisión, que no representa las cinco capas descritas en la Tabla 3, no muestra ningún
componente por su nombre (N8N, FastAPI, PostgreSQL, Gemini, Twilio) y menciona
solo Twilio como origen, ignorando los otros dos canales. El pie remite al Anexo A «en
notación UML», que no está en el documento.
• A-18 (Alta). La Tabla 3 declara para la capa de orquestación: «Motor N8N (versión
estable más reciente; la versión 1.62 no se encuentra disponible en Docker Hub
al momento del despliegue)». Esta acotación —repetida literalmente en §6.1— es
una nota de trabajo interna que quedó en el cuerpo de la tesis. Una tesis no documenta
lo que no pudo instalar en el medio de una tabla de arquitectura; declara la versión
efectivamente desplegada.
• A-19 (Alta). El §5.6 anuncia «seis entidades principales» y la Tabla 4 las enumera
(incidente, sector, estado, canal_origen, clasificacion_log, users), pero el Anexo
C dice «las cinco tablas descritas en la Tabla 4». Contradicción entre el cuerpo y
el anexo.
• M-12 (Media). El §5.4 fija parámetros de inferencia (temperatura 0,3, top-p 0,9,
máximo 100 tokens, timeout 10 s) «optimizados para exactitud y latencia», sin
describir ningún procedimiento de optimización ni los valores alternativos evaluados.
• M-13 (Media). La Tabla 5 lista tres puntos de entrada; la API real expone además
rutas de autenticación (/api/v1/auth), de clasificaciones (GET y PATCH) y un PATCH
sobre incidentes. La tabla es incompleta, no incorrecta.
• M-14 (Media). No hay ninguna captura de pantalla del frontend ni del panel de
administración en todo el documento, pese a que el §6.7 los describe con detalle. La
«interfaz de visualización» es, para el lector, enteramente textual.
Calificación: 5,0 / 10.

# Discusion

## Capitulo 8 (8.1 - 8.5)

Fortalezas reales. El §8.3 enumera cinco limitaciones por iniciativa propia, incluida
la dependencia del proveedor externo y la volatilidad del modelo. La quinta limitación es
particularmente meritoria: reconoce que la comparación se hizo solo contra el flujo manual y
aporta un baseline propio de TF-IDF + SVM al 78 % de exactitud y 0,764 de F1 macro. El §8.4
introduce la dimensión organizacional de la adopción y la resistencia al cambio, tema que
casi ningún trabajo de esta cohorte aborda. El §8.5 fija tres condiciones de generalización
con criterio.
Debilidades.
24• C-09, C-10, C-24 y C-27 se localizan aquí.
• A-20 (Alta). El §8.1 dedica cuatro párrafos a interpretar resultados y cero a
interrogarlos. No hay una sola hipótesis alternativa considerada, ni una explicación
rival para la reducción del 89 %, ni discusión de por qué el clasificador confunde
sistemáticamente Sistemas con Operaciones más allá de la observación léxica.
• A-21 (Alta). El baseline TF-IDF + SVM del §8.3 (78 %, F1 0,764) se menciona en
una sola oración, sin descripción del procedimiento, sin partición, sin tamaño del
subconjunto de evaluación («un subconjunto» sin cuantificar) y sin publicar el código.
Es el único contraste metodológico del trabajo y está tratado como nota al pie.
• A-22 (Alta). El §8.1 califica de «garantía metodológica» la separación entre datos
de construcción y datos de validación, y afirma que «solo después de completar el
desarrollo se evaluó el desempeño sobre la totalidad del corpus». Esta afirmación es
exactamente lo que el material del repositorio no permite verificar (C-01) y es, por
tanto, el pasaje del trabajo que más expuesto queda ante el tribunal.
• M-15 (Media). El §8.2 compara con dos trabajos (2019 y 2020) y un rango sin cita.
No hay comparación con ningún trabajo posterior a 2020.
• M-16 (Media). El §8.4 estima el costo de infraestructura en «50-100 USD/mes según
el proveedor de nube local» y el costo de inferencia en «0,02 USD por cada invocación»,
ambos sin fuente. El segundo es especialmente relevante: 0,02 USD por invocación es
un orden de magnitud superior al precio típico de un modelo de la clase Flash para
prompts de menos de 500 tokens, de modo que la estimación de 28 USD trimestrales
probablemente sea conservadora, pero sin fuente el tribunal no puede evaluarla.
Calificación: 3,0 / 10.

# Conclusiones

## Capitulo 9 (9.1 - 9.2)

Coherencia con los objetivos. El §9.1 recorre los cinco objetivos específicos en orden
y declara su cumplimiento, lo cual es correcto en forma. El §9.2 formula una afirmación
general de conocimiento, que es lo que un capítulo de conclusiones debe hacer.
Debilidades.
• A-23 (Alta). El §9.2 enuncia como aporte general que los LLM invocados por
instrucciones «son capaces de alcanzar niveles de exactitud en clasificación de tickets
de soporte superiores a los de clasificadores supervisados clásicos entrenados
sobre representaciones estáticas». El trabajo no sustenta esa comparación: el
único contraste supervisado es el baseline propio de §8.3, tratado en una oración, y la
fuente que se invoca para el estado del arte supervisado sostiene lo contrario (C-24).
Es una generalización que excede la evidencia.
• A-24 (Alta). El §9.1 repite TLS 1.3 como logro arquitectónico consumado (C-20).
• A-25 (Alta). El §9.1 introduce interpretación estadística nueva —«La prueba de
Wilcoxon con W = 0 es, en sí misma, un resultado poco frecuente en la investigación
aplicada y merece ser interpretada con cautela»— que corresponde al Capítulo 8,
no a las conclusiones. El instrumento prescribe que las conclusiones no introduzcan
resultados ni interpretaciones nuevas.
• M-17 (Media). El §9.1 y §9.2 repiten literalmente las cifras del Capítulo 7 (165,3
s → 18,2 s, 92 %, 0,919, 9,5 %, 62 %/38 %, 28 USD, 180 h) en lugar de sintetizar
su significado. El instrumento observa expresamente que las conclusiones no deben
repetir literalmente los resultados.
• M-18 (Media). Se declara «seis de cada diez incidentes se resuelven sin costo de
25inferencia externa» sobre el 62 % que el repositorio no respalda (C-03).
• B-03 (Baja). El §9.2 califica la distribución del trabajo entre etapas como «una
propiedad emergente del diseño» y «uno de los hallazgos más valiosos», registro
valorativo que roza lo subjetivo para un capítulo de conclusiones.
Calificación: 2,5 / 10.

# Refrencias bibliograficas

## Actualizacion de las fuentes
|Franja temporal|Entradas|Porcentaje|
|Últimos 3 años (2023-2026)|4|12,1%|
|Últimos 5 años (2021-2026)|5|15,2%|
|2015-2020|6|18,2%|
|2010-2014|9|27,3%|
|Anteriores a 2010|13|39,4%|
|Articulos arbitrados de los ultimos 3 años|0|0%|
|Articulos arbitrados de los ultimos 5 años|0|0%|

De las cuatro entradas de los últimos tres años, una es el borrador no publicado de un libro
de texto, una es el software propio de los autores y dos son artículos de conferencia sobre
modelos (Whisper y Llama 2) que no tratan el dominio del trabajo. La bibliografía no está
actualizada y el desfase es especialmente grave dado que el objeto del trabajo son los
modelos de lenguaje grandes, campo cuya literatura se renueva por semestres.

## Clasificacion por tipo y calidad de fuente

|Tipo|Entradas|Observaciones|
|Revista cientifica (Q1 en su categoria)|8|Cohen, Fielding y Taylor, Galup et al., Pedregosa et al., Revina et al., Sokolova y Lapalme, Virtanen et al., Wilson|
|Revista sin indexación verificable|1|Powers (2011), Journal of Machine Learning Technologies - revista sin factor de impacto ni indexación en JCR / Scopus. La misma obra circula como informe técnico de Flinders University. Fuente de confiabilidad media-baja para sostener la definición canónica de las métricas.
|Coherencia de primer nivel|4|Brown et al. (NeurIPS), Radford et al. (ICML), Vaswani et al. (NIPS), Paramesh y Shreedhara (Springer LNNS)|
|Preprint sin arbitraje|1|Touvron et al. (2023), arXiv:2307.09288 - declarado como preprint, lo cual es correcto|
|Libro / manual|10|Todos de editoriales reconocidas|
|Norma o marco normativo|3|Ley 25.326, RGPD, ITIL Service Operation|
|Documentación técnica de proveedor|4|apache Airflow, N8N, PostgreSQL, FastAPI|
|Software propio|1|Gómez, Bustos y Sevilla (2026)|
|Sitio web|1|Wiggins (2017), The Twelve-Factor App|

Fuentes de confiabilidad cuestionable: una (Powers 2011). Documentación de
proveedor usada como sustento conceptual: cuatro, aceptable para decisiones de
implementación, insuficiente para sostener afirmaciones sobre el estado del arte.

## Existencia real de las referencias

Se verificaron las 33 entradas contra fuentes externas (DOI, revista, volumen, número,
páginas, autoría, año, editorial).
Resultado global — y es el mejor de todos los planos auditados:
• Referencias fabricadas o inexistentes: 0.
• DOI que resuelven a un artículo distinto del citado: 0.
• Autorías intercambiadas o inventadas: 0.
• Entradas verificadas como correctas en todos sus metadatos: 29 de 33 (87,9
%).
Este resultado sitúa al trabajo por encima de la media de la cohorte en integridad
bibliográfica y debe consignarse como fortaleza. Los cuatro problemas detectados son de
atribución y metadatos, no de fabricación:

|Entrada|Problema|Severidad|
|Revina, Buza y Meister (2020)|Metadatos correctos (IEEE Access 8, 193380-193395, DOI 10.1109/ACCESS.2020.3032840). Misatribución de contenido: El Cap. 3.3 y 8.2 la presentan como estudio con arquitecturas BERT al 91%; el artículo compara TF-IDF con rasgos linguisticos y concluye que lo simple rinde mejor (c-24)|Critica|
|Stallings, W. (2017). Computer Security Principles and Practice (4° ed.)|Coautor omitido. La obra es de William Stallings y Lawrie Brown|Alta.|
|Office of Government Commerce (2011). ITIL Service Operation|Autoría institucional probablemente errónea: La edición 2011 corresponde al Cabinet Office (TSO como editor); la OGC firmó la edición 2007. Requiere verificación por los autores.|Alta|
|Jurafsky, D. y Martin, J.H. (2023), 3° ed. (Borrador)|Editorial incorrecta: Se atribuye a Perason un borrador de acceso libre no publicado por esa editorial. La marca (Borrador) es correcta y meritoria; la editorial no.|Media|

Atribución adicional a corregir (no de metadatos): los rangos de interpretación del
coeficiente Kappa se atribuyen implícitamente a Cohen (1960); provienen de Landis y Koch
(1977), obra ausente de la bibliografía (C-25).

## Correspondencia entre citas y referencias

Recuento medido sobre el texto extraído: aproximadamente 34 citas parentéticas y
26 citas narrativas, unas 60 en total sobre 27.847 palabras, es decir una cita cada 464
palabras. Es una densidad aceptable para una tesis de tecnicatura, aunque muy desigual
entre capítulos.

|Verificación|Resultado|
|Referencias no citadas en el texto (huérfanas)|0 / 33|
|Citas sin entradas en la bibliografía|2|
|Citas duplicadas o inconsistentes|0|
|Errores de año en citas|0|
|Errores de autor en citas|0|

Las dos citas huérfanas.
1. (APA, 2017) en §11.5: «Este procedimiento se alinea con las recomendaciones
de la Asociación Americana de Psicología (APA, 2017) para investigaciones que
emplean observación sin conocimiento previo de los participantes». No hay entrada
correspondiente. Es la cita que sostiene la justificación ética del engaño metodológico,
de modo que su ausencia es especialmente sensible.
2. Secretaría de la Pequeña y Mediana Empresa en §1.1, invocada como fuente de la
definición de empresa mediana, sin cita formal ni entrada.

## Distribución de citas por capítulo - el problema real

|Capítulo|Citas aproximadas|Palaras aproximadas|
|1. Introduccion|6|3100|
|2. Marco Teórico|17|2700|
|3. Estado del arte|8|1900|
|4. Marco metodológico|8|2600|
|5. Arquitectura|5|2300|
|6. Implementación|4|4000|
|7. Resultados|0|2100|
|8. Discusión|3|2700|
|9-10. Conclusiones y recomendaciones|2|2600|
|11. Consideraciones eticas y legales|6|1900|

El Capítulo 6 tiene una cita cada 1.000 palabras y el Capítulo 7 ninguna. El Capítulo 3
—estado del arte— sostiene su tabla comparativa de seis soluciones comerciales (Tabla
1) sin una sola cita: los modelos de costo, las capacidades de IA y las modalidades de
despliegue de Zendesk, Freshdesk, Jira Service Management, ServiceNow y osTicket se
afirman sin fuente. En una tabla que compara productos comerciales cuyas condiciones
cambian trimestralmente, la ausencia de fuente y de fecha de consulta es un defecto grave
(A-26, Alta).

## Cumplimiento de las normas APA

Edición utilizada: APA 7.a, coherentemente aplicada en la mayor parte del documento. La
lista de referencias está alfabetizada, usa sangría francesa, cursivas correctas en títulos de
libros y revistas, y consigna DOI en formato de URL en las entradas que lo tienen. Es, en
conjunto, un formateo cuidado.
Incumplimientos detectados:

|Regla APA 7|Incumplimiento|Severidad|
|Coma antes del año en citas con "et al."|Sistemáticamente omitida en modo parentético. Solo ocurre en las citas con "et al."; en las de 2 autores la coma está bien puesta.|Media|
|Toda cita debe tener entrada|2 citas huérfanas (APA 2017; SEPyME)|Alta|
|Fecha de consulta en documentación web actualizable|Ausente en las 4 entradas de documentación técnica (Apache, N8N, PostgreSQL, FastAPI) y en Wiggins (2017)|Media|
|Autoría Corporativa|"Tiangolo, S.R. (2024)" trata como persona un seudónimo de proyecto; la convención correcta sería la autoría corporativa del proyecto FastAPI|Baja|
|Entradas de Software|Gómez et al. (2026) está ben formada con designación de versión y descriptor entre corchetes|Correcto|
|Números de página en citas de referencia directa|El cap 3.3 atribuye cifras concretas (87%, 91%) a 2 fuentes sin indicar página|Media
|Consistencia del descriptor de edición|8° ed., 3°ed.,  (2011.° ed.) - La última forma es incorrecta|Baja

Calificación del capítulo de referencias: 5,5 / 10. Integridad alta, actualización nula,
misatribución crítica en la fuente que sostiene el argumento central.

# Revisión de tablas

El documento contiene nueve tablas rotuladas (Tablas 1 a 9), todas numeradas, todas con
título y todas referidas desde el texto. La numeración es correlativa y correcta. Ninguna es
redundante y ninguna debe fusionarse. Es, en conjunto, el aspecto formal mejor resuelto
del trabajo.

|Tabla|Contenido|Evaluación|
|1|Comparación de soluciones de mesa de ayuda|Sin línea de fuente y sin una sola cita (A-26). Las columnas "Modelo de costo" usan categorías cualitativas no definidas ("Alto", "Medio-alto", "Muy alto") sin umbral. La fila "Propuesta" se autoevalúa en la misma tabla que evalúa a terceros, lo que introduce sesgo de presentación|
|2|Operacionalización de variables|La mejor tabla del trabajo. Tipo, unidad y definición operacional por variable. Su único defecto es sustantivo, no formal: La definición de "Intervención humana" no coincide con lo reportado en el cap 7.3 (c-11)|
|3|Capas funcionales de la arquitectura|Correcta en estructura. Contiene la acotación sobre la indisponibilidad de N8N 1.62 en Docker Hub, que no coresponde a una tabla de arquitectura (A-18).|
|4|Entidades del modelo de datos|Correcta y verificada contra el repositorio. Contradicha por el Anexo C, que habla de 5 tablas (A-19)|
|5|Puntos de entrada de la interfaz REST|Incompleta respecto de la API real (M-13)|
|6|Estadísticos descriptivos de tiempos|Formalmente ejemplar (media, mediana, desvío, mínimo, máximo, IC 95%). Sustancialmente sin insumo verificable (C-04). La columna "Reducción" repite 89,0% en 2 filas|
|7|Matriz de confusión|Aritméticamente correcta: filas 82+64+54=200, columnas 81+64+55=200, diagonal 76+58+50=184. Verificada|
|8|Métricas por clase y macro|Veriicada dígito a dígito contra la Tabla 7: Las 9 celdas y los 3 promedios macro son exactos|
|9|Tipología de errores|Correcta y consistente: 7+6+3 = 16, coincidente con los errores de la Tabla 7. Le falta una columna con ejemplos textuales anonimizados|

Defectos transversales: ninguna de las nueve tablas tiene línea de fuente («Fuente:
elaboración propia» o la referencia correspondiente), lo cual APA 7 exige. Ninguna
tiene nota al pie explicativa de abreviaturas. La Tabla 1 y la Tabla 3 tienen problemas de
composición tipográfica —palabras partidas en los encabezados («Clasificacion automatica»
quebrado, «SaaS o autoalojadoLimitada» sin espacio)— atribuibles al ajuste de columnas
en LaTeX.
Calificación de la dimensión «tablas»: 6,5 / 10.

# Revisión de Figuras

El documento contiene una (1) figura en 74 páginas

|Aspecto|Evaluación de la Figura 1|
|Numeración|Correcta "Figura 1"|
|Título|Presente|
|Fuente|Ausente|
|Resolución|Aceptable, pero es una imagen rasterizada de un diagrama dibujado en herramienta de trazado libre|
|Notación|No normalizada. No es UML, BPMN, C4 o un diagrama de flujo formal, sin semántica declarada|
|Tipografía|Inconsistente: Mezcla mayúsculas y minúsculas, tres tamaños distintos, un texto con paréntesis explicativo en cuerpo menor|
|Legibilidad|Aceptable|
|Correspondencia con el texto| Deficiente. La Tabla 3 describe 5 capas con componentes nombrados (n8n, FastAPI, PostgreSQL, Gemini 2.5 Flash, Twilio). La figura no nombra ninguno salvo Twilio, no muestra capas, y presenta el sistema como si tuviera un {unico canal de entrada telefónico, ignorando el correcto y el formulario web que son 2 tercios del diseño}
|Explicación|El pie remite al Anexo A "en notación UML", que no forma parte del documento|

Ausencias que un tribunal señalará. En 74 páginas no hay: diagrama de despliegue,
diagrama de secuencia, diagrama de componentes, diagrama entidad-relación, captura del
flujo N8N, captura del frontend, captura del panel de administración, captura del dashboard
de analítica, diagrama de cajas de los tiempos, representación gráfica de la matriz de
confusión, ni gráfico alguno de los tres que el §6.8 describe (tendencias, torta por sector,
barras apiladas por estado).
Un trabajo de ingeniería informática de 74 páginas con una sola figura, y esa figura dibujada
a mano alzada, comunica visualmente menos de lo que su propio texto describe. Este es,
junto con el Capítulo 7, el punto más vulnerable del documento en la instancia de defensa:
el tribunal pedirá ver el sistema y el documento no lo muestra.
Calificación de la dimensión «figuras»: 1,5 / 10.

# Revisión técnica

## Arquitectura

El diseño de cinco capas es correcto, está bien delimitado y responde a los principios de
cohesión alta y acoplamiento bajo que el §5.1 invoca. La verificación contra el repositorio
confirma que la descomposición del módulo Python descrita en §6.2 se corresponde
exactamente con la estructura real (models, schemas, services, repositories, classifiers,
routes, core), lo cual es notable y debe reconocerse: la mayoría de los trabajos de esta
cohorte describen arquitecturas que su código no tiene.
El subsistema de clasificación híbrido está bien diseñado. La idea de reservar el modelo
de lenguaje para los casos que el filtro determinístico no resuelve es correcta, está
implementada con umbrales configurables (0,90 y 0,70) leídos de la configuración y no
fijados en el código, y respeta el contrato BaseClassifier de modo que cualquiera de las
dos etapas puede sustituirse o simularse en pruebas. Es el mejor componente del trabajo.

## Diagramas

No hay diagramas UML, C4, BPMN ni entidad-relación en el documento. El
Anexo A los declara existentes en el repositorio, en formato .drawio, e incluye tres tipos
(despliegue, secuencia, componentes). En el repositorio clonado no existe ningún archivo
.drawio. Existen, en cambio, tres archivos Markdown en docs/diagrams/ (componentes.md,
despliegue.md, secuencia.md) que contienen diagramas en notación textual, y dos imágenes
PNG. La afirmación del Anexo A sobre el formato editable es incorrecta.
Evaluación de corrección técnica de los diagramas: no evaluable, porque el documento
no los contiene.

## Consistencia entre arquitectura y desarrollo

Se verificaron doce afirmaciones arquitectónicas del Capítulo 5 contra el artefacto:

|Afirmación|Verificación|
|Backend FastAPI en capas PostgreSQL 15.5|Confirmada|
|PostgreSQL 15.5 en contenedor con volumen persistente|Confirmada (postgres:15.5-alpine)|
|Redis para memoria conversacional|Confirmada (redis:72-alpinte)|
|Clasificador híbrido en 2 etapas con umbrales 0,90 / 0,70|Confirmada|
|Seis entidades en el modelo de datos|Confirmada (3 migraciones Alembic)|
|OpenAPI 3.1 generado automáticamente y verificado en CI| Confirmada (docs/openapi.json, 39 KB, con prueba de sinronización)|
|Clasificación embebida en POST /api/v1/incidentes|Confirmada|
|Autenticación JWT con HS256|Confirmada (app/core/security.py)|
|Cifrado Fernet de campos sensibles en reposo|Confirmada (app/utils/encryption.py, EncryptedText)|
|Pseudonimización previa al envío al proveedor|Parcialmente confirmada: Existe en el backend, pero el canal telefónico envía la transcripción cruda al agente antes de llegar allí (c-28)|
|TLS 1.3 en proxy inverso Nginx|Refutada (c-20)|
|Reintento con retroceso exponencial y cola de respaldo| Refutada (c-19)|

Diez de doce confirmadas. La ingeniería es real; el problema está concentrado en las dos
afirmaciones de seguridad y resiliencia, que son precisamente las dos que no se pueden
verificar leyendo el documento.
Calificación de la dimensión técnica: 6,0 / 10.

# Revisión de Anexos

El documento declara siete anexos (A a G) en las páginas 72 a 74. Ninguno de ellos
contiene material: los siete son descripciones de material que no se adjunta, con
una extensión total de aproximadamente 1.100 palabras.

|Anexo|Qué declara|Verificación contra el repositorio|
|Diagramas|Tres diagramas UML (despliegue, secuencia, componentes) en formato .drawio eidtable, versión de alta resolución en docs/|No cumple. No hay archivos .drawio. Hay 3 .md con notación textual y 2 PNG. Ningún diagrama en el documento.|
|Repositorio|Código, migraciones, Alembic, Docker, CI; commit de referencia en tag v1.0.0; despliegue local en menos de 15 minuto|Cumple parcialmente. Repositorio real, público, con todo enumerado y README que efectivamente promete menos de 15 minutos. El tag v1.0.0 no existe (c-23)|
|Esquema de base de datos|"Las 5 tablas descritas en la Tabla 4", restricciones, índices, funciones almacenadas de identificadores con prefijo, migraciones Alembic| Cumple parcialmente. Las migraciones existen (3). La Tabla 4 tiene 6 entidades, no 5 (A-19). No se pudo localizar la función almacenada de generación de identificadores con prefijo configurable que el capítulo 5.6 describe|
|OpenAPI|Especificación 3.1 generada automáticamente, Swagger UI en /docs, archivo estático verificado en CI|Cumple plenamente. docs/openapi.json de 39 KB con prueba de sincronización. Es el mejor anexo del trabajo.|
|Flujo N8N|"La totalidad de los 12 nodos configurados"; importación en "una instancia limpia de N8N 1.62" reproduce el comportamiento; script TwiML documentado|No cumple. El JSON tiene 19 nodos, cifra que el Capitulo 6.1 declara no disponible en Docker Hub. El script TwiML existe en twilio/ pero el flujo no es reproducible por C-17|
|Corpus de validación|CSV en evaluation/data/ con 7 columnas incluídas predicción, timepos y confianza; planillas de cronometraje del flujo manual; registros automáticos del flujo automatizado|No cumple, y es el hallazgo central. El CSV tiene 4 columnas, es sintético y su documentación en el repo declara que no debe interprestarse como evidencia experimental y que la campaña real es trabajo futuro (c-01). No hay planillas de cronometraje ni registros de tiempo (C-04)|
|Docuemntación operativa|Procedimientos de despliegue, resplado, restauración, monitoreo y respuesta a incidentes para 3 entornos|Cumple. docs/operation-guide.md y docs/troubleshootin.md existen y tienen contenido real.

Reproducibilidad del estudio. El instrumento pide determinar si los anexos son
suficientes para garantizar la reproducibilidad. La respuesta es no, con un matiz
importante:
• La reproducibilidad del sistema está bien servida: cualquier lector con Docker
puede levantar el entorno, consultar el contrato OpenAPI e inspeccionar el código.
Esto es más de lo que ofrece la mayoría de los trabajos comparables.
• La reproducibilidad del estudio es nula: no hay corpus real, no hay etiquetas de
los dos anotadores, no hay planilla de tiempos, no hay script que reproduzca la Tabla
6, y el único informe de evaluación versionado arroja números incompatibles con los
publicados.
Material que existe en el repositorio y la tesis no incorpora. El repositorio contiene
un archivo ANEXO_H_Prompt_Gemini_Especificacion.md con la especificación completa del
prompt enviado al modelo. Es exactamente el tipo de material que un anexo de una tesis
sobre clasificación con LLM debería contener —y que permitiría al tribunal evaluar el diseño
del prompt— y la tesis, cuyos anexos llegan hasta la letra G, no lo incluye. Recomendación:
incorporarlo como Anexo H.
Calificación de la dimensión «anexos»: 2,5 / 10.

#Auditoría de la calidad de escritura científica

## Mediciones realizadas

Se procesó el cuerpo del documento (capítulos 1 a 11, excluidos encabezados de página,
índices y bibliografía) y se obtuvieron los siguientes indicadores objetivos:

|Indicador|Valor|Referencia deseable|
|Oraciones analizadas|697|-|
|Longitud ediana de oración|28 palabras|20-25|
|Longitud media de oración|29,3|20-25|
|Oraciones de más de 40 palabras|21,7%|<15%|
|Oraciones de más de 60 palabras|3,7%|<3%|
|Construcciones en pasiva refleja ("se + verbo")|-24%|<30%|
|Ocurrencias de "mediante"|83|-|
|Ocurrencias dde "constituye"|23|-|
|Ocurrencias de "de manera/forma + adjetivo"|17|-|
|Errores ortográficos sistemáticos|4 patrones (ver más abajo)|0|

## Voz activa y pasiva

El trabajo emplea predominantemente voz activa con sujeto inanimado —«el sistema
procesa», «la arquitectura contempla», «el clasificador exhibe»— que es exactamente el
registro que el instrumento recomienda. La pasiva refleja se concentra, como corresponde,
en el capítulo metodológico, donde el agente es irrelevante («se aplicó contrabalanceo»,
«se calculó el coeficiente»). Este es un punto fuerte del trabajo: el 24 % medido está
claramente por debajo del umbral problemático y muy por debajo de la media de la cohorte.
Casos concretos donde la pasiva es innecesaria y conviene sustituirla:
• §4.2: «se aplicó contrabalanceo del orden de procesamiento» → «el diseño contrabalanceó
el orden de procesamiento».
• §6.5: «La solución consistió en implementar un mecanismo...» → «El equipo
implementó un mecanismo...» (además obliga a declarar el agente, lo que habría
hecho visible C-19).
• §11.3: «se aplica un procedimiento de pseudonimización previa» → «el módulo Python
pseudonimiza el texto antes de transmitirlo» (más preciso y verificable).

## Claridad

Alta en general. La mayoría de las oraciones expresa una idea principal y se comprende en
una sola lectura. Los pasajes problemáticos son de dos tipos:
Oraciones que acumulan tres o más proposiciones. Ejemplo del §1.5 (objetivo
general), de 63 palabras, que encadena cinco verbos coordinados («recibir, procesar,
clasificar y registrar»), dos gerundios («reduciendo», «manteniendo») y un participio final
(«garantizando»). Un objetivo general debe caber en una oración de menos de 40 palabras.
Ambigüedad referencial. §8.1: «Esta compresión de la variabilidad no fue un objetivo
explícito del diseño pero emerge como una consecuencia deseable de la automatización» —
«esta» puede referirse al rango, a la varianza o al desvío, y de esa ambigüedad procede el
error C-09.

## Consición

Es la dimensión más débil de la escritura. Se detectan:
• Repetición literal entre capítulos. El párrafo de Galup et al. sobre la degradación
de los procesos manuales aparece tres veces casi textualmente (§1.1, §1.2, §2.1). La
descripción de las restricciones cambiarias argentinas aparece dos veces (§1.1, §1.7).
La caracterización de N8N como plataforma autoalojada de código fuente disponible
aparece cuatro veces (§2.3, §3.2, §6.3, §9.1).
• Explicación circular. §2.1 define la gestión de incidentes y §2.2 vuelve a definirla con
otras palabras sin agregar contenido.
• Duplicación entre capítulos 5 y 6. El §5.3 (capa de orquestación) y el §6.3
(construcción del flujo) describen el mismo pipeline de cinco etapas con distinto nivel
de detalle; podrían fundirse y ahorrar unas 600 palabras.
• Duplicación entre capítulos 8 y 9. El §9.1 reproduce párrafos enteros del §8.1 con
mínimas variaciones.
Una reducción del 12 al 15 % de la extensión total mejoraría el trabajo sin perder una sola
idea.

## Presición terminológica

uena y estable. La terminología se mantiene consistente a lo largo de los once capítulos:
«flujo manual» y «flujo automatizado» no cambian de nombre, «clasificador híbrido», «filtro
determinístico», «sector responsable» y «canal de origen» conservan su significado. Esto
es infrecuente y meritorio.
Inconsistencias detectadas:
• «N8N», «n8n» y «N8n» alternan a lo largo del documento; la marca oficial es n8n.
• El §2.3 y el §3.2 llaman a n8n «modelo de licencia de código fuente disponible» y
«licencia Sustainable Use», lo cual es correcto y digno de mención —muchos
trabajos comparables lo llaman erróneamente «código abierto»—; pero el §1.7 y el
§6.1 lo incluyen sin matices en la enumeración «herramientas de bajo costo y código
abierto —N8N, Python, FastAPI, PostgreSQL—», reintroduciendo el error que los
otros dos capítulos evitan (A-27, Alta).
• «Exactitud» y «precisión» se usan correctamente como conceptos distintos, salvo en
§1.2, donde «tasa de derivación errónea» se compara implícitamente con la exactitud
del clasificador sin declarar que son métricas de poblaciones distintas.
• «Intervención humana» designa dos magnitudes distintas (C-11).

## Fluidez

Las transiciones entre secciones son explícitas y correctas; casi todos los capítulos abren
con un párrafo que anuncia su contenido. Los cortes abruptos detectados son dos:
• El §4.9 (Scrumban) irrumpe al final del capítulo metodológico sin conexión con las ocho
secciones anteriores, que son de método de investigación.
• El §6.8 (dashboard de analítica) aparece después de la sección de pruebas, sin
transición, y su último párrafo cambia de registro hacia lo especulativo.

## Estilo científico

Tono formal sostenido, sin lenguaje coloquial, sin primera persona. Las expresiones vagas
están razonablemente controladas. Se detectan, no obstante, afirmaciones valorativas
40sin respaldo que un tribunal marcará:
• §9.1: «no deja espacio para la duda razonable»; «un resultado poco frecuente en la
investigación aplicada».
• §9.1: «uno de los hallazgos más valiosos del trabajo».
• §8.1: «El rigor metodológico adoptado para evitar data leakage merece una
observación aparte» seguido de «una garantía metodológica que no todos los trabajos
del área documentan con el mismo nivel de explicitación». Autoelogio comparativo sin
muestra de comparación.
• §6.4: «un valor que lo posiciona como una vía prácticamente útil y no como una
demostración de laboratorio».

## Economía del lenguaje

Nominalización elevada pero dentro de lo esperable en el registro académico en español.
El uso de «mediante» (83 ocurrencias, una cada 335 palabras) es excesivo y produce
cadenas de frases preposicionales encadenadas. Ejemplo del §11.4: «La confidencialidad
se garantiza mediante cifrado en tránsito sobre TLS 1.3 a nivel del proxy inverso (Nginx)
[...] y mediante el cifrado a nivel de aplicación mediante Fernet» — tres «mediante» en
una oración, dos de ellos consecutivos.

## Corrección ortográfica

Se detectó un patrón sistemático de acentuación incorrecta que afecta a cuatro
palabras de alta frecuencia. Las mediciones sobre el texto completo:

|Forma correcta|Ocurrencias|Forma incorrecta usada|Ocurrencias|
|diseño (sustantivo)|0|diseñó|21|
|desarrollo (sustantivo)|1|desarrolló|11|
|completo (adjetivo)|0|completó|13|
|aquellos (pronombre)|0|aquéllos|7|

El resultado es que el trabajo escribe «el diseñó experimental», «el desarrolló del
módulo Python», «el ciclo completó de vida del ticket» y «aquéllos incidentes» de forma
sistemática: 52 errores del mismo tipo. Los tres primeros son errores gramaticales (verbo
en lugar de sustantivo/adjetivo); el cuarto es una tilde diacrítica que la RAE suprimió en
2010.
Origen identificado. El repositorio contiene el script docs/Tesis/acentuar_tesis.py, un
acentuador automático cuyo diccionario de reemplazo incluye las entradas categóricas
"diseno": "diseñó", "desarrollo": "desarrolló", "completo": "completó" y "aquellos":
"aquéllos". El script no distingue categoría gramatical, de modo que convirtió todos los
sustantivos en verbos. Es un defecto trivial de corregir y muy visible para un tribunal:
la palabra «diseño» no aparece ni una sola vez en una tesis de ingeniería de 74 páginas.
A esto se suma la portada sin acentuar: «Automatizacion inteligente...», «Tecnicatura
Universitaria en Programacion», «Tecnico Universitario en Programacion», «Republica
Argentina». El primer contacto del tribunal con el trabajo es una portada con siete palabras
sin tilde.

# Índice de calidad de escritura

|Dimensión|Puntaje|
|Predominio de voz activa|8,0|
|Claridad|7,5|
|Precisión terminológica|7,5|
|Concisión|5,5|
|Fluidez|7,5|
|Coherencia discrusiva|6,5|
|Estilo científico|6,5|
|Corrección ortográfica y formal|4,5|

**ÍNDICE DE CALIDAD DE ESCRITURA CIENTÍFICA:
6,8 / 10**
Justificación. La escritura de esta tesis está claramente por encima de la media de
los trabajos finales de la carrera: la voz activa predomina, la terminología es estable
a lo largo de once capítulos, las transiciones son explícitas y el registro académico se
sostiene sin caídas. El puntaje no llega a 8 por tres razones concretas y todas reparables:
la extensión mediana de oración (28 palabras) está cinco por encima de lo deseable y
una de cada cinco oraciones supera las 40 palabras; hay duplicación literal de contenido
entre capítulos que podría eliminarse; y la corrupción ortográfica sistemática de cuatro
palabras de alta frecuencia (52 ocurrencias) daña la impresión de cuidado del documento
de manera desproporcionada a su gravedad real. Este último punto se corrige con
cuatro sustituciones globales y es la mejora de mayor rendimiento por unidad de
esfuerzo de todo el trabajo.

#Matriz de riesgos de rechazo

## Distribución de hallazgos
|Severidad|Cantidad|Definición operativa|
|Crítica|28|Compromete la validez de una conclusión o la integridad del trabajo. Debe corregirse antes de la defensa|
|Alta|34|Genera observación mayor del tribunal. Debe corregirse|
|Media|29|Genera observación menor o pregunta incómoda|
|Baja|14|Defecto formal|
|Total|105|-|

## Distribución por capítulo

|Capítulo|Críticos|Altos|Medios|Bajos|Total|
|1. Introducción|2|3|2|1|8|
|2. Marco teórico|0|3|2|1|6|
|3. Estado del arte|3|2|2|0|7|
|4. Marco metodológico|6|4|3|1|14|
|5. Arquitectura|3|3|3|2|11|
|6. Implementación|6|4|2|2|14|
|7. Resultados|5|3|2|1|11|
|8. Discusión|2|3|2|1|8|
|9. Conclusiones|0|3|2|1|6|
|10. Recomendaciones|0|0|2|1|3|
|11. Ética y legales|1|2|2|1|6|
|Anexos|0|4|3|2|9|
|Transversales (figuras, APA, ortografía)|0|0|2|0|2|

## Riesgos por tipo

|Tipo de riesgo|Nivel|Fundamento|
|Riesgo metodológico|Muy alto|Instrumento de medición descrito de tres maneras incompatibles; contrabalanceo imposible con datos retrospectivos; variable de intervención humana definidad de un modo y medida de otro; interrogante subsidiario sin respuesta|
|Riesgo estadístico|Alto|Estadístico W incompatible con su propia definición; fórmula del tamaño del efecto incorrecta y con rango declarado falso; código ajustado al resultado publicado|
|Riesgo bibliográfico|Medio-alto|Cero fabricaciones y cero referencias huérfanas (fortaleza real) pero cero artículos arbitrados de los últimos 5 años y misatribución crítica en la fuente que sostiene el argumento central|
|Riesgo formal|Medio-alto|Una sola figura en 74 páginas, dibujada a mano; siete anexos sin contenido; 52 errores ortográficos sistemáticos; portada sin acentuar|
|Riesgo jurídico|Alto|3 errores sustantivos en el capítulo de cumplimiento normativo, incluída una contradicción en los términos sobre el plazo de conservación|
|Riesgo de integridad académica|Alto|El repositorio contiene una declaración firmada por los autores que contradice el capítulo 7, y un comentario de código que documenta el ajuste de un estimador para reproducir un número ya publicado|

# Preguntas problables del tribunal

Se anticipan las preguntas que el material auditado hace previsibles. Se recomienda a los
autores preparar respuesta escrita para cada una.
Sobre los datos
1. Muéstrennos el corpus de 200 casos reales. ¿Dónde está?
2. El README de evaluation/data/ dice que las métricas generadas con ese corpus no son
válidas para el Capítulo 7. ¿Qué corpus usaron entonces, y dónde está publicado?
3. El documento docs/anexo_f_corpus.md de su propio repositorio declara que el corpus
real es «trabajo de campo futuro». ¿Cuándo se hizo ese trabajo de campo y por qué
esa declaración sigue allí?
4. report_provisional.md reporta 63,0 % de exactitud y F1 macro 0,5936. ¿Por qué la
tesis reporta 92 % y 0,919?
5. ¿Dónde están los 200 pares de tiempos? El Anexo F promete siete columnas y el archivo
tiene cuatro.
6. Los incidentes son de julio-septiembre de 2025 y el estudio es de junio de 2026. ¿Cómo
se contrabalanceó el orden de procesamiento de incidentes ocurridos nueve meses
antes?
Sobre la estadística
7. evaluation/stats.py invoca scipy.stats.wilcoxon(..., alternative='greater'),
que devuelve la suma de rangos positivos. Con 200 pares favorables eso da W =
20.100. ¿Por qué la tesis reporta W = 0?
8. Evalúen su fórmula r = 1 − 2W /[n(n + 1)] en W = n(n + 1)/2. ¿Cómo llega a −1?
9. Un comentario de su propio código dice: «Para consistencia con la tesis que reporta
r=1.00, calculamos r como la proporción de pares donde manual > automatizado».
¿Por qué se ajustó el estimador al número publicado en lugar de corregir el número?
10. La Tabla 2 define la intervención humana como proporción de tiempo; el §7.3 reporta
19 de 200 casos. ¿Cuál de las dos midieron?
11. Tienen 16 errores y 19 intervenciones. ¿Cuántos de los 16 errores fueron detectados
por la compuerta de confianza del 0,70?
12. ¿Cuál es la exactitud de clasificación del brazo manual? El §1.3 pregunta si el
clasificador supera al criterio humano.
13. 3.700 × 165,3 s son 169,9 horas. ¿De dónde salen las 180 horas-persona liberadas?
14. Con 42 incidentes diarios, ¿cuántos días hábiles tuvo su trimestre para llegar a 3.700?
Sobre el sistema
15. En su flujo N8N, el nodo IF que evalúa la confianza está conectado antes del nodo
HTTP que invoca al clasificador. ¿Qué confianza está evaluando?
16. Para los canales de correo y web, ¿de dónde sale el valor de confianza que ese IF
compara con 0,70?
17. El nodo AI Agent no tiene ningún modelo de lenguaje conectado. ¿Cómo se ejecutó el
canal telefónico?
18. El cuerpo del POST envía solo descripcion y prioridad. ¿Cómo llegó canal_origen a
la base de datos, si es una de las variables de su estudio?
19. La palabra nginx no aparece en su repositorio. ¿Dónde está la terminación TLS 1.3 que
declaran en §5.1, §9.1 y §11.4?
20. Ningún nodo del flujo tiene retryOnFail ni onError. ¿Dónde está el reintento con
retroceso exponencial del §6.5 y cuáles fueron las pruebas de carga que menciona?
21. Su prompt telefónico clasifica en cuatro sectores, incluida «Seguridad». ¿Por qué la
tesis tiene tres?
5222. El Anexo E dice 12 nodos y el §6.3 dice 19. El archivo tiene 19. ¿Cuál es correcto?
23. El tag v1.0.0 del Anexo B no existe. ¿Qué commit evaluamos?
24. En la única corrida documentada, 95 de 200 casos terminaron en la rama de fallback
por fallo de Gemini. ¿Por qué esa etapa no está en la tesis?
Sobre la bibliografía y el marco normativo
25. Su propia bibliografía transcribe el título del artículo de Revina et al. (2020): IT Ticket
Classification: The Simpler, the Better. ¿En qué parte de ese artículo hay BERT?
26. ¿De dónde sale el rango de 88 % a 94 % con el que compara sus resultados en el §8.2?
27. ¿Qué artículo arbitrado posterior a 2021 sustenta su estado del arte?
28. Su §4.4 dice que κ = 0,87 es «sustancial» y en la misma oración aclara que κ > 0,80
es «casi perfecto». ¿Cuál es?
29. ¿Cómo se concilia «política de conservación indefinida» con el principio de limitación
del plazo de conservación del art. 4 inc. 7 de la Ley 25.326?
30. El «legítimo interés» es una base de licitud del RGPD. ¿Cuál es la base del art. 5 de la
Ley 25.326 que ampara este tratamiento?
31. La decisión de adecuación europea habilita flujos hacia Argentina. ¿Cómo justifica una
transferencia de Argentina hacia los Estados Unidos?
32. En el canal telefónico, la transcripción cruda llega al proveedor del modelo antes de
pasar por el pseudonimizador del backend. ¿Cómo se concilia con el §11.3?

Informe emitido el 4 de agosto de 2026. Auditoría realizada sobre el archivo Tesis_ultima_versión__1_.pd
(74 páginas, 27.847 palabras) y sobre el repositorio público declarado en su Anexo B, en el
estado del commit d7df92c del 2 de julio de 2026.
