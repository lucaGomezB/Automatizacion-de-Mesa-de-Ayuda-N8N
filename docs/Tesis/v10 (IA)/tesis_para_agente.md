# Tesis UTN-FRM 2026 - Tesis para agentes (v10 / v1.2.16)

> Documento generado a partir de las fuentes LaTeX de `docs/Tesis/v10 (IA)/paper/sections/` (version de trabajo v10, release `v1.2.16`). Render Markdown de referencia para agentes. Los valores numericos son verbatim de las fuentes.

---

**UNIVERSIDAD TECNOLÓGICA NACIONAL**

**FACULTAD REGIONAL MENDOZA**

 Tecnicatura Universitaria en Programación

 Automatización inteligente del registro de incidentes

 en mesas de ayuda empresariales mediante orquestación de

 flujos con N8N y procesamiento de lenguaje natural

 basado en modelos de lenguaje grandes

 Trabajo Final de Carrera presentado para obtener el título de

 Técnico Universitario en Programación

**Autores**

 Luca Gomez · Carla Bustos · Gonzalo Sevilla

**Directores**

 Prof. Alberto Cortez y Prof. Ariel Enferrel

 Mendoza, República Argentina

 9 de noviembre de 2026

## Resumen

La digitalización eleva la criticidad de la gestión de incidentes, pero en muchas organizaciones medianas el registro inicial aún es manual, con demoras, errores de clasificación y uso ineficiente de recursos técnicos.

Esta investigación diseña, implementa y valida un sistema automatizado de mesa de ayuda que integra N8N, un módulo de lenguaje natural con FastAPI, Gemini 3.6 Flash, PostgreSQL y telefonía con Twilio. Recibe solicitudes por correo, formulario web y teléfono, y las deriva a uno de los cinco sectores mediante un clasificador híbrido de reglas y un modelo de lenguaje grande.

El estudio es cuantitativo y cuasiexperimental, de muestras pareadas, sobre los mismos 200 casos estratificados. El doble etiquetado original alcanzó un kappa de 0,87 (sin intervalo) y el nuevo, de 0,5569 (moderado; IC [0,4725; 0,6413]).

El tiempo medio de registro se redujo significativamente, de 61,6 s a 17,76 s (71,2 %). La prueba de Wilcoxon arrojó \(W = 363\) y un tamaño del efecto \(r = 0,9639\). Dentro de la muestra, la exactitud estricta alcanzó 73,5 % y el macro-F1 de umbral, sobre las cuatro clases estimables, 0,6508. Por sub-hipótesis, la principal se confirma en tiempo de registro y se refuta en el umbral de clasificación; la intervención humana se refuta sobre los 147 casos revisados (25 cambiaron; 17,0 %), con 12,5 % sobre 200 como dato secundario.

Los hallazgos respaldan la viabilidad técnica y económica; la operativa es condicional: el balance neto frente a las derivaciones erróneas resulta indeterminado. Se aporta una arquitectura reproducible y evidencia en español rioplatense.

**Palabras clave:** automatización, mesa de ayuda, procesamiento de lenguaje natural, modelo de lenguaje grande, N8N, FastAPI, clasificación de tickets, español rioplatense, human in the loop

## Abstract

Digitalization raises the criticality of incident management, yet in many medium-sized organizations initial registration is still manual, with delays, classification errors, and inefficient use of technical resources.

This thesis designs, implements, and validates an automated help desk system integrating N8N, a Python natural language processing module built with FastAPI, the Gemini 3.6 Flash model, PostgreSQL, and a Twilio telephony channel. It receives requests through email, web form, and phone calls with automatic transcription, and routes each incident to one of the five canonical sectors using a hybrid classifier that combines deterministic rules with a large language model.

The study is quantitative and quasi-experimental, with paired samples over the same 200 cases drawn by stratified sampling. The original double labeling reached a kappa of 0.87 (no interval), the new one 0.5569 (moderate; CI [0.4725, 0.6413]).

Results show a statistically significant reduction in mean registration time, from 61.6 s to 17.76 s (71.2 %). The Wilcoxon signed-rank test yielded \(W = 363\) with an effect size \(r = 0.9639\). As in-sample estimates, strict classification accuracy reached 73.5 % and the threshold macro-F1, over the four estimable classes, was 0.6508. Per sub-hypothesis, the main one is confirmed in registration time and refuted on the classification threshold; human intervention is refuted over the 147 reviewed cases (25 changed; 17.0 %), with 12.5 % over 200 as a secondary datum.

The findings support technical and economic feasibility; operational feasibility is conditional, since the net balance against misrouted incidents remains undetermined. A reproducible architecture and empirical evidence in Rioplatense Spanish are provided.

**Keywords:** automation, help desk, natural language processing, large language model, N8N, FastAPI, ticket classification, Rioplatense Spanish, human in the loop

## Glosario de siglas y acrónimos

tocsectionGlosario de siglas y acrónimos

spacing1

3pt
tabular@>p0.47@0.05>p0.47@
**ACID** Atomicity, Consistency, Isolation, Durability & **MDE** Minimum Detectable Effect 

**AES** Advanced Encryption Standard & **MFA** Multi-Factor Authentication 

**AI** Artificial Intelligence & **MVCC** Multi-Version Concurrency Control 

**API** Application Programming Interface & **N8N** plataforma de orquestación de flujos (*nodemation*) 

**ARCO** Acceso, Rectificación, Cancelación y Oposición & **NB** Naive Bayes 

**ASGI** Asynchronous Server Gateway Interface & **NIST** National Institute of Standards and Technology 

**ASR** Automatic Speech Recognition & **NLBSE** Natural Language-Based Software Engineering 

**BERT** Bidirectional Encoder Representations from Transformers & **NLP** Natural Language Processing 

**BPA** Business Process Automation & **ORM** Object-Relational Mapper 

**CBC** Cipher Block Chaining & **PABAK** Prevalence-Adjusted Bias-Adjusted Kappa 

**CE** Comunidad Europea & **PAM** Privileged Access Management 

**CI** Continuous Integration & **PATCH** método HTTP de actualización parcial 

**CIA** Confidentiality, Integrity, Availability & **PCM** Pulse Code Modulation 

**CMDB** Configuration Management Database & **PK** Primary Key 

**CONEAU** Comisión Nacional de Evaluación y Acreditación Universitaria & **PNG** Portable Network Graphics 

**CRUD** Create, Read, Update, Delete & **POST** método HTTP de creación 

**CSF** Cybersecurity Framework & **RAG** Retrieval-Augmented Generation 

**DAG** Directed Acyclic Graph & **REST** Representational State Transfer 

**DT** Decision Tree (árbol de decisión) & **RGPD** Reglamento General de Protección de Datos 

**E2E** End-to-End (extremo a extremo) & **RTO** Recovery Time Objective 

**ECE** Expected Calibration Error & **SAST** Static Application Security Testing 

**ETL** Extract, Transform, Load & **SBOM** Software Bill of Materials 

**FK** Foreign Key & **SDK** Software Development Kit 

**GB** Gigabyte & **SHA** Secure Hash Algorithm 

**GET** método HTTP de lectura & **SIEM** Security Information and Event Management 

**GPT** Generative Pre-trained Transformer & **SLA** Service Level Agreement 

**GPU** Graphics Processing Unit & **SMTP** Simple Mail Transfer Protocol 

**HITL** Human In The Loop & **SPA** Single Page Application 

**HMAC** Hash-based Message Authentication Code & **SPOC** Single Point of Contact 

**HTTP** Hypertext Transfer Protocol & **SQL** Structured Query Language 

**IA** Inteligencia Artificial & **SSD** Solid-State Drive 

**IC** Intervalo de Confianza & **SSO** Single Sign-On 

**IDF** Inverse Document Frequency & **SVM** Support Vector Machine 

**IMAP** Internet Message Access Protocol & **TF** Term Frequency 

**IP** Internet Protocol & **TI** Tecnologías de la Información 

**ISO** International Organization for Standardization & **TLS** Transport Layer Security 

**ITIL** Information Technology Infrastructure Library & **TOTP** Time-based One-Time Password 

**ITSM** Information Technology Service Management & **TSO** The Stationery Office 

**JSON** JavaScript Object Notation & **UI** User Interface 

**JWT** JSON Web Token & **URL** Uniform Resource Locator 

**KMS** Key Management Service & **USD** United States Dollar 

**LLM** Large Language Model & **UTC** Coordinated Universal Time 

**LR** Logistic Regression (regresión logística) & **UUID** Universally Unique Identifier 

 & **VM** Virtual Machine 

tabular
spacing

## Introducción

### Contextualización

La evolución de las tecnologías de la información ha transformado profundamente la dinámica operativa de las organizaciones contemporáneas. En la actualidad los sistemas informáticos constituyen el soporte fundamental para la ejecución de procesos administrativos, productivos y de comunicación, y esa dependencia tecnológica ha incrementado de manera correlativa la importancia de los servicios de soporte técnico, particularmente aquellos relacionados con la gestión de incidentes informáticos. La disciplina que da marco a esa actividad —la gestión de servicios de tecnologías de la información (ITSM)— se desarrolla en la §`sec:marco-teorico`, donde se define su alcance y su relación con la mesa de ayuda.

No obstante, en muchas organizaciones medianas el proceso de registro inicial de incidentes continúa realizándose manualmente, lo que introduce demoras, inconsistencias y una marcada dependencia del criterio individual del operador.

El contexto argentino presenta características particulares que acentúan esta problemática. Las organizaciones medianas del país —segmento que la Secretaría de la Pequeña y Mediana Empresa encuadra por tramos según el sector y parámetros como el personal ocupado o el volumen de ventas anuales [SEPyME2026_mipyme]— operan con presupuestos de tecnología acotados y enfrentan restricciones cambiarias que encarecen la adopción de soluciones comerciales internacionales. La combinación de estas restricciones con una demanda creciente de servicios digitales configura un escenario en el que las soluciones basadas en componentes de código abierto y servicios de inferencia bajo demanda resultan particularmente atractivas desde el punto de vista económico y operativo.

### Planteamiento del problema

La presente investigación se desarrolla en el marco de una organización mediana del sector servicios con sede en la provincia de Mendoza, República Argentina, cuya plantilla asciende a aproximadamente 120 usuarios internos distribuidos en cinco áreas funcionales. El área de operaciones desempeña simultáneamente tareas vinculadas a la gestión operativa cotidiana y a la atención de incidentes informáticos reportados por los usuarios, lo que obliga al personal responsable a interrumpir actividades críticas para registrar manualmente fallas de hardware, inconvenientes de software o solicitudes de asistencia técnica.

Las mediciones preliminares realizadas durante una semana laboral representativa evidenciaron un volumen promedio de 42 incidentes diarios, un tiempo medio de registro manual de 2 minutos con 45 segundos por incidente y una tasa de derivación errónea inicial cercana al 15 %. Aquel valor de 2 minutos con 45 segundos constituyó una estimación a priori, obtenida del promedio de una semana completa de operación sin cronometraje individual por caso, y sirvió para dimensionar el problema. La tasa de derivación errónea del 15 % comparte esa naturaleza preliminar y no fue re-medida, por lo que el saldo neto queda indeterminado (§`subsec:balance-neto`). La campaña experimental posterior midió el tiempo de registro incidente por incidente con cronometraje en vivo, consignado en la planilla descrita en la §`subsec:diseno-experimental`, y arrojó una media de 61,6 s sobre los 200 casos del corpus, sustancialmente inferior a la estimación preliminar. El tiempo que el personal podría redirigir a tareas de mayor valor agregado si la etapa de registro estuviera automatizada se cuantifica en la §`subsec:interpretacion-resultados`.

El registro manual de incidentes implica además la lectura de correos electrónicos, la interpretación de descripciones textuales heterogéneas, la clasificación del problema según el área responsable y la carga manual de la información en un sistema de tickets. Este procedimiento requiere tiempo, interrumpe las tareas del personal técnico y puede generar errores de clasificación que prolongan la cadena de resolución cuando un ticket es derivado a un área incorrecta. La dispersión de los canales de comunicación —correo, llamada telefónica y formularios internos— agrava la situación al obligar al personal a monitorear múltiples fuentes simultáneamente.

Este escenario es coherente con la caracterización general de la gestión de servicios de TI [Galup2009_itsm] (véase §`subsec:gestion-servicios-ti`); que los procesos de soporte no automatizados tiendan a degradarse cuando crece el volumen de solicitudes, con mayor impacto en organizaciones medianas donde el personal combina múltiples roles, es una inferencia de los autores de esta tesis y no una afirmación de esa fuente. Estos indicadores justifican la búsqueda de una alternativa tecnológica que reduzca el costo operativo, mejore la calidad de la derivación temprana y disminuya la variabilidad asociada al criterio individual.

### Pregunta de investigación

A partir del problema descrito, esta investigación se orienta a responder la siguiente pregunta: ?`reduce la automatización del registro inicial de incidentes mediante orquestación de flujos y procesamiento de lenguaje natural el tiempo de registro respecto del proceso manual, y alcanza la exactitud de clasificación el umbral objetivo definido para una mesa de ayuda empresarial mediana?

La pregunta se descompone en tres interrogantes subsidiarios que guían el diseño experimental y la selección de métricas. Primero, ?`cuál es la magnitud de la reducción del tiempo de registro que puede obtenerse mediante la automatización, y resulta esa reducción estadísticamente significativa? Segundo, ?`alcanza el clasificador automático el umbral objetivo de exactitud global del 85 % y un valor F1 macro no inferior a 0,85, y cómo se distribuyen los errores entre las categorías objetivo? Tercero, ?`permite la arquitectura propuesta integrar canales múltiples de recepción sin degradar la latencia ni la calidad de la clasificación?

### Hipótesis de trabajo

La hipótesis principal de este trabajo se desdobla en tres sub-hipótesis contrastables, cada una con su propio contraste y su criterio de falsación, y no se enuncia como una conjunción indivisible de mecanismo y umbral de desempeño. La primera sostiene que la automatización reduce el tiempo de registro: su contraste es el no paramétrico de Wilcoxon sobre las *diferencias pareadas* de los tiempos de registro, con \(H_0\): las diferencias pareadas \(D_i = t_manual,i - t_automatizado,i\) se distribuyen de forma simétrica respecto de cero (la automatización no altera el tiempo de registro) frente a \(H_1\): las diferencias tienden a ser positivas (el tiempo manual supera al automatizado), y su criterio de falsación es no rechazar \(H_0\). El contraste se rechaza con los valores vigentes \(W = 363\), \(p = 3,08e-32\) bilateral (\(1,54e-32\) unilateral, de modo que el bilateral es conservador frente a la \(H_1\) direccional) y tamaño del efecto \(r = 0,9639\) (§`sec:resultados`); esta sub-hipótesis se declara confirmada.

La segunda postula que la proporción de casos del flujo automatizado que requieren acción manual de un operador no supera 0,15, complemento del umbral de exactitud fijado a priori en el segundo objetivo específico; se contrasta con el intervalo de Wilson de esa proporción en una regla de tres vías: es compatible si el límite superior del intervalo queda por debajo de 0,15, refutada si la estimación puntual alcanza o supera 0,15, y no concluyente si la estimación queda por debajo de 0,15 pero su límite superior no. La campaña complementaria de medición registró 147 intervenciones en 200 casos (73,5 %), pero esa tasa bruta mide la derivación por reportante no identificado y no la necesidad de revisión. La revisión humana alcanzó 66 casos de correo y 81 de telefonía y ninguno de los 53 del formulario web; de los 147 casos revisados, 25 cambiaron la derivación (17,0 %; IC de Wilson [11,8 %, 23,9 %]), de modo que, sobre ese denominador, esta sub-hipótesis se declara *refutada*. El cociente sobre los 200 casos (12,5 %; IC [8,6 %, 17,8 %]) se conserva solo como dato secundario, porque cuenta 53 casos web sin oportunidad de revisión (véase §`subsec:reduccion-intervencion`).

La tercera postula que la exactitud y el F1 macro alcanzan el umbral de desempeño (exactitud no inferior al 85 % y F1 macro de umbral no inferior a 0,85), verificado contra la exactitud observada y su intervalo de confianza de Wilson, sin invocar la zona de rechazo del contraste de tiempos; su criterio de falsación es una exactitud observada por debajo del 85 % o un intervalo de confianza que no supera el umbral. El resultado vigente —73,5 % de exactitud, IC \([67,0 %, 79,1 %]\) y macro-F1 de umbral de 0,6508 sobre las cuatro clases estimables (§`sec:resultados`)— no alcanza el umbral; esta sub-hipótesis se declara refutada.

Como hipótesis subsidiarias se plantea, en primer lugar, que la integración de múltiples canales de entrada dentro de un único flujo automatizado mejora la accesibilidad del sistema y reduce la dispersión operativa sin introducir cuellos de botella adicionales. En segundo lugar, que un esquema híbrido de clasificación basado en reglas determinísticas y modelo de lenguaje grande resulta más eficiente —en términos de la relación entre exactitud, latencia y costo de inferencia— que un esquema construido exclusivamente sobre modelo externo, dado que una proporción sustancial de los incidentes presenta marcadores léxicos inequívocos que no requieren consulta al modelo de lenguaje. Ninguna tiene contraste formal y ambas se declaran *no contrastadas*.

### Objetivo general

Evaluar la viabilidad y el desempeño de la automatización del registro inicial de incidentes de una mesa de ayuda empresarial mediana mediante la orquestación de flujos con N8N y el procesamiento de lenguaje natural en Python. El desarrollo y la implementación del sistema constituyen el medio para esa evaluación, que abarca la recepción, el procesamiento, la clasificación y el registro automáticos de incidentes y considera la reducción del tiempo de registro, la calidad de la clasificación y la proporción de intervención humana en la etapa inicial, manteniendo la supervisión técnica y la trazabilidad de las decisiones tomadas por el sistema.

### Objetivos específicos

El primer objetivo específico consiste en diseñar una arquitectura distribuida y modular que integre un motor de orquestación de flujos, un módulo de procesamiento de lenguaje natural, un canal de telefonía con transcripción automática del habla y una base de datos relacional, garantizando comunicación asincrónica entre componentes mediante interfaces de programación de aplicaciones de tipo REST sobre HTTP cifrado.

El segundo objetivo específico se orienta a implementar un clasificador automático que asigne cada incidente a uno de los cinco sectores canónicos —Seguridad Informatica, Soporte Tecnico Hardware, Soporte Tecnico Software, Bases de Datos o Sistemas— sobre un corpus controlado de 200 casos representativos del entorno operativo. El umbral de desempeño —exactitud global no inferior al 85 % y F1 macro no inferior a 0,85— no es parte definitoria de este objetivo, sino un criterio de éxito contingente verificable contra la exactitud observada y su intervalo de confianza; su grado de cumplimiento se declara en la §`subsec:cumplimiento-objetivos`. Ese umbral se fundamenta en tres criterios convergentes. Primero, la literatura de clasificación de tickets toma como referencia a los clasificadores supervisados clásicos, entre los que SVM tuvo buen desempeño en todas las muestras de [Paramesh2019_it_service_desk], aunque los trabajos relevados no permiten fijar un piso numérico común (§`tab:trabajos-academicos`). Segundo, el costo organizacional de una derivación errónea se estima en el orden de 10 a 15 minutos adicionales de reasignación, estimación propia de los autores a partir de la observación operativa de la organización adoptante, sin un registro cuantitativo conservado, por lo que una exactitud inferior al 85 % resultaría en tiempos de resolución comparables a los del flujo manual para un volumen de errores inaceptable. Tercero, situar el umbral en el 85 % deja margen para que, si la exactitud verdadera del clasificador lo supera, el límite inferior de su intervalo de confianza pueda ubicarse por encima de la frontera de interés en lugar de quedar solapado con ella.

El tercer objetivo específico plantea integrar tres canales de entrada paralelos —correo electrónico, formulario web y llamada telefónica con transcripción automática— dentro de un único flujo automatizado que normalice la entrada y centralice el procesamiento, mejorando la accesibilidad del sistema sin incrementar la complejidad operativa percibida por los usuarios finales.

El cuarto objetivo específico consiste en evaluar comparativamente el flujo manual y el flujo automatizado en términos de tiempo medio de registro, dispersión, exactitud de clasificación y proporción de intervención humana, mediante un diseño cuasiexperimental con muestras pareadas, prueba estadística no paramétrica y reporte de intervalos de confianza al 95 %. El diseño experimental sigue las recomendaciones de [HernandezSampieri2018_metodologia] para investigaciones tecnológicas de carácter aplicado.

El quinto objetivo específico se orienta a documentar la arquitectura, los procedimientos de despliegue y los resultados experimentales de modo que una tercera parte pueda replicarlos, y a proponer una hoja de ruta de evolución que oriente futuras mejoras y replicaciones del estudio en organizaciones de características comparables.

Como sexto objetivo específico se plantea analizar los errores de clasificación y calibrar la confianza de las predicciones, tipificando los patrones de error y caracterizando las bandas de confianza para interpretar el desempeño más allá de las métricas agregadas. Su cumplimiento es verificable contra el reporte de evaluación del repositorio y la §`subsec:analisis-errores` de la §`sec:resultados`.

### Justificación

La justificación del trabajo se sostiene en tres dimensiones complementarias.

Desde la dimensión organizacional, la automatización propuesta busca liberar capacidad operativa del personal técnico, reducir el tiempo de registro y la variabilidad del criterio individual. La evidencia recogida en una organización mediana argentina cuantifica el ahorro bruto de registro y el punto de equilibrio frente al costo de las derivaciones erróneas (§`subsec:balance-neto`), con el que otras organizaciones pueden estimar, con sus propias tasas, el retorno de una inversión similar.

Desde la dimensión tecnológica, la solución combina componentes de código abierto —Python, FastAPI y PostgreSQL— con N8N, una plataforma de orquestación de flujos cuyo código fuente se distribuye bajo licencia Sustainable Use (*fair-code*) y admite despliegue completamente autoalojado [n8n2024_docs], lo que permite una implementación reproducible en organizaciones de tamaño mediano sin requerir grandes inversiones de capital ni dependencia exclusiva de proveedores comerciales. Esta propiedad es particularmente relevante en el contexto argentino, donde las restricciones de acceso a divisas y los costos de suscripción en moneda extranjera constituyen barreras significativas para la adopción de soluciones comerciales internacionales. Además, el despliegue autoalojado de la totalidad de los componentes —con excepción del servicio de inferencia— otorga a la organización control pleno sobre sus datos operativos, en línea con el control sobre los datos personales y su tratamiento conforme a la normativa de protección de datos [Ley25326_2000].

Desde la dimensión académica, el trabajo aporta evidencia empírica sobre el desempeño de modelos de lenguaje grandes aplicados a la clasificación de tickets en español rioplatense, dominio escasamente documentado en la literatura comparativa disponible. Ninguno de los trabajos de clasificación automática de tickets relevados (§`tab:trabajos-academicos`) declara un corpus en español, y las evaluaciones de LLM que incorporan el español lo hacen con corpus genéricos, no específicos del dominio de mesas de ayuda [grandury2025laleaderboard, mayorrocher2026spanish]. Este trabajo contribuye a cerrar esa brecha mediante la validación de un clasificador híbrido sobre un corpus de 200 casos en español rioplatense: la validación es dentro de la muestra; el acuerdo entre los dos analistas originales, uno de ellos autor, fue de $ = 0,87$ (sin intervalo) y el doble etiquetado nuevo, a cargo de los etiquetadores `E1` y `E2`, arrojó $ = 0,5569$ (moderado, con intervalo).

El relevamiento propio de la documentación pública de los proveedores (consultada el 19-10-2026) muestra que plataformas comerciales como Zendesk Suite, Freshdesk o ServiceNow ITSM operan como software como servicio, con datos en jurisdicciones extranjeras y costos por agente y mes que escalan con el equipo [Zendesk2026_help_desk, Freshdesk2026_platform, ServiceNow2026_itsm]. La propuesta desarrollada en esta investigación utiliza herramientas de despliegue autoalojado, lo que facilita su adopción en organizaciones medianas y simplifica el cumplimiento de la normativa argentina de protección de datos personales.

### Alcance y delimitaciones

El alcance del trabajo se circunscribe a la etapa de recepción, clasificación y registro inicial de incidentes, sin abarcar la resolución técnica de los mismos, la cual permanece bajo responsabilidad del personal humano. El sistema contempla tres canales de entrada (correo electrónico, formulario web y llamada telefónica con transcripción automática) y cinco sectores de derivación (Seguridad Informatica, Soporte Tecnico Hardware, Soporte Tecnico Software, Bases de Datos y Sistemas). La validación experimental se realiza sobre un corpus en idioma español rioplatense recolectado en una organización mediana del sector servicios con sede en la provincia de Mendoza, de aproximadamente 120 usuarios internos distribuidos en cinco áreas funcionales.

Quedan fuera del alcance los siguientes aspectos, los cuales se proponen como líneas de trabajo futuro en la §`sec:recomendaciones`. Primero, la integración con sistemas externos de inventario de activos informáticos o con sistemas de gestión de configuración. Segundo, los modelos de aprendizaje supervisado entrenados con corpus propios de la organización, dado que el volumen actual de datos etiquetados resulta insuficiente para esa estrategia. Tercero, la implementación de paneles de monitoreo avanzados con visualización en tiempo real de métricas operativas. Cuarto, la automatización de la etapa de resolución técnica, que trasciende el alcance del presente trabajo.

Las delimitaciones del estudio incluyen: la restricción geográfica a una única organización de la provincia de Mendoza, lo que limita la validez externa de los hallazgos; la dependencia operativa del servicio externo de inferencia gemini-3.6-flash, cuyo rendimiento y condiciones comerciales escapan al control de los investigadores; y la naturaleza temporal de los resultados, que reflejan el comportamiento del modelo, integrado el 24-09-2026 y vigente en las corridas del 2 y del 7 de octubre de 2026 y en la corrida telefónica del 5 y 6 de octubre (§`subsec:protocolo-pruebas`), sujeta a modificaciones futuras por parte del proveedor.

## Marco teórico

Este capítulo establece los fundamentos conceptuales sobre los cuales se construye la investigación. Se abordan ocho ejes temáticos que proporcionan el andamiaje teórico necesario para comprender el diseño, la implementación y la evaluación del sistema propuesto.

### Gestión de servicios de tecnologías de la información

La gestión de servicios de tecnologías de la información (ITSM) es una disciplina que articula procesos, personas y tecnologías para alinear la operación tecnológica con los objetivos del negocio [Galup2009_itsm]; la noción de mesa de ayuda como punto único de contacto es propia de ITIL [OGC2011_itil]. Este enfoque rompe con la concepción anterior que entendía a la informática como un área de soporte estrictamente reactivo y la posiciona, en cambio, como un proveedor de servicios sujeto a acuerdos de nivel de servicio explícitos.

Dentro de este marco general, la gestión de incidentes constituye uno de los procesos operativos centrales. Su objetivo principal consiste en restaurar el servicio afectado en el menor tiempo posible, minimizando el impacto adverso en la operación del negocio. El proceso comprende cuatro etapas secuenciales: la recepción y registro inicial, la clasificación y priorización, la asignación al área responsable y, finalmente, la resolución y cierre. Los autores de esta tesis infieren que los procesos manuales de soporte tienden a degradarse cuando el volumen de solicitudes crece de manera no lineal o cuando el personal debe alternar entre tareas operativas heterogéneas, situación que coincide con la observada en el entorno empresarial analizado en el presente trabajo.

### Mesa de ayuda y modelo ITIL

El marco de buenas prácticas ITIL (Information Technology Infrastructure Library), en su edición de operaciones de servicio [OGC2011_itil], publicada por The Stationery Office (TSO) por encargo del Cabinet Office y cuyo titular histórico es el Office of Government Commerce, establece la distinción conceptual entre incidente —definido como una interrupción no planificada del servicio o una reducción de su calidad— y solicitud de servicio —definida como un pedido formal de información, asesoramiento, acceso a un componente o ejecución de una operación estandarizada—. Esta distinción resulta especialmente relevante para el diseño del clasificador propuesto en este trabajo, ya que orienta la categorización inicial y condiciona la priorización subsiguiente.

El marco ITIL postula adicionalmente tres principios operativos que guían el diseño de la solución propuesta. El primero es la centralización de la recepción mediante un punto único de contacto (SPOC, por su sigla en inglés), que en el sistema propuesto se materializa a través del flujo unificado de orquestación que normaliza las entradas de los tres canales. El segundo es la operación bajo acuerdos de nivel de servicio (SLA), que cuantifican la calidad esperada en términos de tiempo de respuesta y tiempo de resolución. El tercero es la mejora continua del proceso, que en el sistema propuesto se habilita mediante la trazabilidad de cada decisión del clasificador y la retroalimentación de los sectores responsables.

Los modelos tradicionales de mesa de ayuda se basan en la interacción manual entre el usuario y el operador, lo que implica tiempos de respuesta variables y una dependencia directa del personal disponible. Cuando el volumen de incidentes excede la capacidad del equipo o cuando los operadores deben alternar simultáneamente entre tareas operativas y de soporte, la calidad del servicio se degrada de manera observable. La automatización del registro inicial constituye, en consecuencia, una intervención que aborda el cuello de botella en el punto de mayor sensibilidad del proceso, sin requerir la reestructuración completa del modelo operativo.

### Automatización de procesos y orquestación de flujos

Se entiende aquí por automatización de procesos empresariales (BPA, por su sigla en inglés) la reducción de la intervención humana en tareas repetitivas mediante la ejecución automática de acciones definidas a partir de eventos específicos. [Russell2021_ai_modern] ubican a la automatización inteligente dentro del paradigma de los agentes orientados a objetivos, en el cual un sistema reactivo percibe eventos del entorno, decide acciones según una política preestablecida y actúa modificando el estado del entorno. Esta caracterización ofrece un marco conceptual robusto para el diseño de sistemas que combinan reglas determinísticas con decisiones derivadas de modelos probabilísticos, como el clasificador híbrido propuesto en este trabajo.

Se entiende aquí por plataformas de integración como servicio (iPaaS) las herramientas de orquestación que posibilitan integrar distintos servicios, procesar información y ejecutar acciones automáticas en función de condiciones predefinidas. Estas plataformas se caracterizan por ofrecer modelos visuales de construcción de flujos, soporte nativo para webhooks y disparadores reactivos, y capacidad de transformación de datos entre sistemas heterogéneos. [n8n2024_docs] documenta las capacidades de N8N, la herramienta seleccionada para este trabajo, que se distingue dentro del segmento por su modelo de licencia de código fuente disponible y su despliegue completamente autoalojado, decisivo cuando el tratamiento de datos sensibles exige mantener la información dentro del perímetro organizacional.

El paradigma de orquestación se diferencia conceptualmente del paradigma de coreografía. [Hohpe2003_eip] establecen que la orquestación centraliza la lógica de control en un componente único, lo que simplifica la trazabilidad de cada ejecución pero introduce un punto de coordinación cuya disponibilidad condiciona al sistema completo. La coreografía, en cambio, distribuye la coordinación entre los participantes mediante eventos publicados en un bus común, lo que aumenta la robustez frente a fallos parciales pero dificulta la observabilidad. El presente trabajo adopta el enfoque de orquestación por simplicidad operativa y por la prioridad otorgada a la trazabilidad auditable de cada decisión del sistema, en línea con los requisitos de la Ley 25.326 [Ley25326_2000].

### Human-in-the-loop y grados de autonomía

El paradigma *human-in-the-loop* (HITL) designa los esquemas en los que una persona interviene en el ciclo de decisión de un sistema automático para etiquetar, corregir, validar o supervisar sus salidas. [MosqueiraRey2023_human_in_the_loop] sistematizan el aprendizaje con intervención humana y muestran que las anotaciones y correcciones incorporadas al ciclo mejoran la calidad del modelo cuando los datos escasean o el dominio es ambiguo; Los autores de esta tesis infieren que el diseño debe reservar a la persona un rol activo ante la ambigüedad semántica y la responsabilidad sobre las consecuencias de la decisión. En línea con el paradigma *HitAI*, [Zanzotto2019_human_in_the_loop] reclama retribuir a quienes producen el conocimiento que usan los sistemas y sostener la supervisión humana. [Amershi2019_human_ai] formulan guías de interacción que exigen transparencia sobre la confianza del sistema y control del usuario, [Shneiderman2020_human_centered_ai] propone combinar alta automatización con supervisión significativa, y [Wu2022_ai_chains] muestran que la descomposición de tareas con puntos de control humano hace al sistema inspeccionable.

Los grados de autonomía se ordenan según la proporción de decisiones delegadas y la granularidad de la revisión. La *revisión total* somete cada salida a validación humana; la *revisión selectiva* delega las decisiones de alta confianza y deriva a la persona solo las que caen por debajo de un umbral; y la *operación autónoma con auditoría* ejecuta sin intervención previa y conserva un registro trazable para revisión posterior. El sistema propuesto adopta una revisión selectiva acotada por etapa: la regla `requiere_revision_humana = (confianza < 0,`70) se evalúa solo sobre la salida de la etapa Gemini; la reserva deriva siempre a revisión y la etapa determinística no deriva por su confianza (§`subsec:subsistema-clasificacion`). Desde el 13 de octubre de 2026, posterior a la campaña 2026-10, el backend deriva además a revisión al reportante no identificado. La calibración de la confianza del modelo condiciona la cobertura efectiva de la salvaguarda (§`sec:discusion`).

### Procesamiento de lenguaje natural y modelos de lenguaje grandes

El procesamiento de lenguaje natural (NLP) constituye un área de la inteligencia artificial orientada a la interpretación del lenguaje humano por parte de sistemas informáticos. [Jurafsky2023_speech_language] abordan, entre otros temas, el modelado estadístico de secuencias, la representación distribuida de palabras y las arquitecturas neuronales profundas. Mediante estas técnicas resulta posible analizar texto o audio transcrito, identificar palabras clave, determinar la intención del usuario y clasificar contenido en categorías predefinidas.

La evolución del campo durante la última década ha estado dominada por la arquitectura Transformer [Vaswani2017_attention], cuyo mecanismo de atención permite a los modelos capturar dependencias de largo alcance sin las limitaciones de las redes neuronales recurrentes. El mecanismo de atención multi-cabeza permite ponderar simultáneamente distintas partes de la secuencia de entrada, lo que resulta útil para clasificar descripciones textuales cuya información relevante puede aparecer en cualquier posición.

Sobre esta arquitectura se construyeron los modelos de lenguaje grandes (LLM) contemporáneos, los cuales exhiben capacidades robustas de clasificación en escenarios de pocos ejemplos (*few-shot*) o sin ejemplos (*zero-shot*), fenómeno conocido como aprendizaje en contexto. [Brown2020_few_shot] demostraron que modelos suficientemente grandes pueden generalizar a tareas nuevas a partir de instrucciones expresadas en lenguaje natural, sin requerir ajuste fino sobre datos específicos del dominio. Esta capacidad es particularmente relevante para el contexto de esta investigación, donde el volumen de datos etiquetados resulta insuficiente para entrenar un clasificador supervisado tradicional desde cero.

La forma en que se formula la instrucción condiciona el resultado tanto como la capacidad del modelo. El aprendizaje en contexto admite dos configuraciones principales: el planteamiento *zero-shot*, en el que la instrucción describe la tarea sin ejemplos, y el *few-shot*, en el que se incorporan unos pocos casos resueltos dentro del propio mensaje para orientar la respuesta. La evaluación multilingüe de [ahuja2023mega], que compara estrategias de *prompting* entre idiomas, muestra que la estrategia elegida puede modificar el rendimiento de manera sustancial, sobre todo en idiomas con pocos recursos, por lo que el diseño del *prompt* constituye una decisión de ingeniería y no un detalle accesorio.

Los LLM generan, junto con la etiqueta asignada, una estimación de confianza que no necesariamente coincide con la probabilidad empírica de acierto. La calibración designa el grado de correspondencia entre la confianza declarada por el modelo y su corrección observada: un modelo bien calibrado acierta con una frecuencia próxima a la confianza que expresa. La calibración se mide agrupando las predicciones por nivel de confianza y contrastando la confianza media con la exactitud observada, en diagramas de fiabilidad y en el error de calibración esperado (ECE), y puede corregirse a posteriori, por ejemplo con escalado de temperatura [Guo2017_calibration]. Cuando el modelo se consulta como servicio de caja negra, con entrada y salida solo textuales, la confianza no proviene de probabilidades internas sino que el modelo la verbaliza: en modelos ajustados con retroalimentación humana puede estar mejor calibrada que las probabilidades condicionales en las tareas evaluadas [Tian2023_verbalized_confidence], pero es sobreconfiada, concentra los valores en el extremo alto de la escala y predecir cuáles de sus respuestas son fallas sigue siendo un desafío, dependiente de cómo se la elicita [Xiong2024_confidence_elicitation]. En el sistema propuesto este concepto fundamenta el umbral operativo de revisión humana, ya que las clasificaciones de la etapa semántica con confianza inferior a 0,70 se derivan a supervisión; la fiabilidad de ese umbral depende tanto de la exactitud como de la calibración del modelo.

Una limitación central de los modelos generativos es la alucinación, es decir, la producción de contenido plausible en su forma pero falso o no sustentado en la entrada [Ji2023_hallucination]. En una tarea de clasificación la alucinación puede manifestarse como la asignación de una categoría inexistente o como una justificación inventada a partir de indicios débiles. Como el desempeño de los LLM generativos en el etiquetado automático varía de forma marcada entre conjuntos de datos [colavito2025benchmarking], sus etiquetas no pueden aceptarse sin validarlas contra una referencia. Esta exigencia motiva dos decisiones del sistema: restringir el espacio de salida a las cinco categorías canónicas y validar cada clasificación contra las etiquetas válidas antes de persistirla.

El rendimiento de los LLM tampoco es uniforme entre idiomas ni entre variedades de un mismo idioma: sobre 29 idiomas, el desempeño de 36 modelos cae de forma marcada en los de menos recursos [xuan2025mmluprox]; el ajuste por instrucciones de los modelos abiertos se concentró en el inglés y unos pocos idiomas [lai2023okapi], y ante textos con alternancia de idiomas los LLM multilingües rinden por debajo de modelos ajustados más pequeños [zhang2023multilingual]. Para el español, [grandury2025laleaderboard] proponen una tabla de clasificación abierta para sus variedades y las lenguas de España y América Latina, y [mayorrocher2026spanish], con pruebas de español como lengua extranjera, observan que los modelos comprenden bien el idioma pero no alcanzan la competencia gramatical nativa. Esta sensibilidad resulta directamente relevante para el presente trabajo, cuyo corpus está redactado en español rioplatense, una variedad escasamente representada en los conjuntos de evaluación internacionales.

La evaluación de un LLM no se agota en una medida única de exactitud. Los benchmarks multilingües de [xuan2025mmluprox] y [ahuja2023mega] abarcan múltiples tareas y desagregan sus resultados por idioma, porque una cifra global puede ocultar un desempeño dispar entre categorías. Esta advertencia, que este capítulo desarrolla en la Sección `sec:metricas-multiclase` para el caso de clasificadores multiclase, fundamenta la decisión metodológica de reportar, además de la exactitud global, métricas por clase y el valor F1 macro promediado.

En una mesa de ayuda, el NLP permite clasificar incidentes y derivarlos al sector correspondiente sin intervención manual, mejorando la velocidad de respuesta y reduciendo la carga operativa del registro. La elección entre un clasificador supervisado entrenado sobre corpus específico, un modelo de lenguaje grande de propósito general invocado mediante instrucciones, o un esquema híbrido en cascada [Varshney2022_model_cascading, Chen2024_frugalgpt], en el que el componente más económico resuelve los casos cuya señal de fiabilidad alcanza un umbral y deriva los restantes al más costoso, depende de la disponibilidad de datos etiquetados, del presupuesto de inferencia y de los requerimientos de soberanía sobre los datos.

### Reconocimiento automático del habla

Los sistemas de reconocimiento automático del habla (ASR) permiten convertir audio en texto mediante modelos entrenados sobre grandes corpus de habla anotada, cuyo marco clásico describen [Rabiner1993_speech_recognition], mientras que la generación contemporánea se apoya en redes neuronales profundas cuyo exponente reciente con alta robustez multilingüe es el modelo Whisper
[Radford2023_whisper]. El sistema propuesto no integra un motor de ASR: la transcripción efectiva del canal telefónico la provee un servicio externo (§`subsec:integracion-canal-telefonico`), de modo que la noción de reconocimiento automático del habla se conserva únicamente como marco conceptual de ese canal.

### Bases de datos relacionales y persistencia transaccional

La persistencia de los incidentes en una base de datos relacional permite garantizar las propiedades de atomicidad, consistencia, aislamiento y durabilidad (ACID) propias del modelo transaccional clásico [Date2003_database]. PostgreSQL, el motor seleccionado para este trabajo, ofrece soporte completo del estándar SQL, extensiones para tipos de datos avanzados como JSON binario y arreglos, y un modelo de concurrencia basado en control multiversional (MVCC) que resulta adecuado para cargas mixtas de lectura y escritura [PostgreSQL2024_docs].

La elección de un motor relacional se comprende mejor al contrastarla con alternativas concretas. Un motor de documentos como MongoDB almacena registros con esquema flexible y favorece la evolución de la estructura sin migraciones, pero no impone las relaciones entre incidentes, sectores, estados y canales de origen, de modo que la integridad referencial queda delegada a la aplicación. Un motor clave-valor en memoria como Redis ofrece latencias de acceso muy bajas y resulta adecuado para caché o contadores efímeros, pero no está orientado a la persistencia duradera ni a consultas relacionales complejas. El dominio de este trabajo exige precisamente esas propiedades: las relaciones entre incidentes, sectores, estados y canales se modelan como tablas vinculadas mediante claves foráneas con integridad referencial declarativa, las operaciones de registro y actualización requieren las garantías ACID de la transacción clásica, el dashboard de analítica se apoya en consultas relacionales de agregación sobre múltiples tablas y la trazabilidad de cada decisión del sistema demanda un registro duradero y auditable. Esta combinación de requisitos justifica la elección de PostgreSQL, en línea con los requisitos normativos identificados en la sección de consideraciones éticas y legales (§`sec:aspectos-legales`).

### Métricas de evaluación de clasificadores multiclase

La evaluación de clasificadores multiclase requiere métricas que capturen tanto el desempeño global como el desempeño por clase. [Powers2011_evaluation] describe el conjunto canónico de métricas derivadas de la matriz de confusión, entre las cuales destacan la exactitud global (*accuracy*), la precisión por clase, la sensibilidad o exhaustividad (*recall*) por clase, y la medida F1 como media armónica de las dos anteriores.

La exactitud global se define como la proporción de predicciones correctas sobre el total de casos evaluados:

 Exactitud = 1N _i=1^N 1[y_i = y_i]

donde \(N\) es el número de casos, \(y_i\) la clase predicha para el caso \(i\), \(y_i\) su clase verdadera y \(1[]\) la función indicadora, que vale uno cuando la predicción coincide con la etiqueta y cero en caso contrario. Válida para cualquier número de clases, es la que subyace a la matriz de confusión de cinco sectores de la §`sec:resultados`; no se emplea la formulación binaria de verdaderos y falsos positivos y negativos, que presupone una única clase de interés y resulta inadecuada en un problema multiclase.

[Sokolova2009_performance_measures] advierten que en escenarios con clases desbalanceadas la exactitud global puede resultar engañosa y recomiendan reportar valores macro promediados, los cuales otorgan igual peso a cada clase con independencia de su frecuencia. El valor F1 macro promediado, en la variante que emplea este trabajo (media aritmética de los F1 por clase), se define como:

 F1_macro = 1k _i=1^k F1_i

donde \(k\) es el número de clases y \(F1_i\) es el valor F1 de la clase \(i\). [Opitz2019_macro_f1] documentan que circulan dos fórmulas del F1 macro (esta y la del F1 de la precisión y la sensibilidad macro promediadas) y que no son equivalentes. El presente trabajo adopta esta recomendación y reporta exactitud global, F1 macro y métricas desagregadas por clase, para que el lector evalúe la robustez del clasificador frente a la distribución específica del corpus.

Adicionalmente, la matriz de confusión es el instrumento estándar de presentación de resultados en clasificación multiclase, porque permite identificar patrones de error: confusiones entre dos categorías, sesgos hacia una clase mayoritaria o aciertos preferenciales sobre una clase. Su inspección orienta el análisis cualitativo posterior y fundamenta cualquier propuesta de mejora del clasificador.

## Estado del arte

Este capítulo revisa la literatura académica y las soluciones comerciales disponibles en cuatro áreas relevantes para el presente trabajo: plataformas de mesa de ayuda, herramientas de orquestación de flujos, métodos de clasificación automática de tickets de soporte, y calibración de la confianza y cascadas de modelos. El propósito es situar la contribución de esta investigación en el contexto de los desarrollos previos y fundamentar la brecha que motiva el trabajo.

**Protocolo de revisión.** La revisión que sustenta este capítulo y los fundamentos del marco teórico se construyó con una búsqueda estructurada cuya fecha de corte es el 21 de octubre de 2026, sobre seis fuentes: Scopus, IEEE Xplore, ACM Digital Library, ACL Anthology, Google Scholar y arXiv. Las cadenas, formuladas en inglés, combinaron términos de dominio y de método: A1, "*("help desk" OR "service desk" OR "IT support") AND ("ticket classification" OR "incident classification") AND ("machine learning" OR "natural language processing" OR "large language model")*; A2, "*("large language model" OR "LLM") AND ("ticket" OR "incident") AND ("classification" OR "routing")*; A3, "*("Spanish" OR "español") AND ("large language model" OR "LLM") AND ("evaluation" OR "benchmark")*; A4, "*("Gemini" OR "Google Gemini") AND ("ticket" OR "incident" OR "help desk")*; y B1, "*("human-in-the-loop" OR "human in the loop" OR "human-AI interaction") AND ("machine learning" OR "large language model")*. Criterios de inclusión: publicación arbitrada 2023-2026 para el estado del arte moderno (A1-A4), idioma español o multilingüe y evaluación empírica; para los fundamentos de human-in-the-loop (B1) no se impuso restricción temporal. Criterios de exclusión: literatura no arbitrada, notas de prensa y material comercial sin respaldo metodológico. Una extensión posterior (grupo C), ejecutada el 25 de octubre de 2026 (su fecha de corte propia), agregó sobre las mismas seis bases dos cadenas: C1, "*("calibration" OR "confidence estimation" OR "confidence elicitation" OR "uncertainty") AND ("large language model" OR "LLM" OR "language model" OR "neural network") AND ("classification" OR "few-shot" OR "verbalized" OR "overconfidence")*; y C2, "*("cascade" OR "cascading" OR "routing" OR "hybrid" OR "rule-based") AND ("large language model" OR "LLM" OR "natural language processing" OR "NLP") AND ("classification" OR "cost" OR "efficiency")*. Se incluyeron publicaciones arbitradas, sin restricción temporal, sobre calibración o estimación de confianza de clasificadores y modelos de lenguaje (C1) o sobre cascadas y enrutamiento de modelos con criterio de costo y exactitud (C2), con evaluación empírica o método de referencia; se excluyeron los preprints sin versión arbitrada y el material no arbitrado. De las que cumplían se eligieron, hasta seis, las más próximas al escenario de este trabajo (un modelo consultado como servicio y una cascada de dos etapas). Cada consulta quedó registrada, con base, cadena, fecha y resultado, en la bitácora `docs/Tesis/Correcciones/bitacora-busqueda-c-110.md`, consistente con lo aquí declarado.

Una limitación del protocolo de revisión que se declara, y no se oculta, es la ausencia de búsquedas en repositorios regionales (SciELO, Redalyc y JAIIO), que podrían haber reforzado la brecha declarada para la literatura argentina.

### Soluciones comerciales de mesa de ayuda

El relevamiento propio de la documentación pública de los proveedores, consultada el 19-10-2026, muestra que las soluciones comerciales de gestión de mesa de ayuda examinadas son integrales y cubren el ciclo completo de vida del ticket. Zendesk Suite ofrece funcionalidades de recepción multicanal, automatización de flujos básicos y, mediante un módulo adicional, capacidades de inteligencia artificial para sugerencia de respuestas y deflección de consultas frecuentes. Freshdesk propone una arquitectura comparable e incorpora el motor Freddy AI para clasificación automática y enrutamiento inteligente. Jira Service Management, parte del ecosistema de Atlassian, ofrece capacidades limitadas de automatización inteligente en su plan estándar; la edición Data Center permite el despliegue autoalojado para organizaciones con requisitos de soberanía sobre los datos. ServiceNow ITSM constituye la opción de referencia en el segmento corporativo, con un módulo Predictive Intelligence que aplica aprendizaje automático sobre el histórico de tickets de la organización.

El relevamiento propio de la documentación pública de los proveedores, consultada el 19-10-2026, también muestra que sus ofertas comerciales incorporan capacidades de inteligencia artificial descritas para organizaciones medianas, principalmente en mercados de habla inglesa. No obstante, estas plataformas presentan dos limitaciones relevantes para el contexto de la presente investigación. La primera es el modelo de costos basado en agente y mes, que escala linealmente con el tamaño del equipo de soporte. La segunda es que la mayoría de estas plataformas operan exclusivamente en modalidad de software como servicio (SaaS) con almacenamiento de datos en jurisdicciones extranjeras, lo que introduce consideraciones adicionales sobre transferencia internacional de datos personales bajo la Ley 25.326 [Ley25326_2000].

En el segmento de código abierto, osTicket constituye una alternativa de despliegue autoalojado sin costo de licencia, aunque carece de capacidades nativas de clasificación automática mediante procesamiento de lenguaje natural moderno. Esta brecha funcional motiva la búsqueda de arquitecturas compositivas que integren componentes maduros de código abierto con servicios de inferencia bajo demanda.

### Plataformas de orquestación de flujos

Dentro de las plataformas de orquestación de flujos relevadas para este trabajo (consulta 19-10-2026) se incluyen Zapier, Make (anteriormente Integromat), Microsoft Power Automate, Apache Airflow y N8N. Las primeras tres operan exclusivamente como SaaS, lo que las descarta como base para implementaciones donde el control sobre la infraestructura es un requisito explícito. Apache Airflow se orienta a flujos de trabajo programados de tipo procesamiento de datos por lotes, con un diseño centrado en grafos acíclicos dirigidos (DAG) definidos como código Python [Apache2024_airflow]; aunque potente, su paradigma de ejecución programada resulta inadecuado para un caso de uso reactivo y orientado a eventos como el de una mesa de ayuda.

N8N ofrece un modelo de construcción visual de flujos sobre nodos predefinidos, soporte nativo para webhooks y disparadores reactivos, ejecución basada en eventos y posibilidad de despliegue completamente autoalojado bajo Docker [n8n2024_docs]. La disponibilidad de su código fuente bajo licencia Sustainable Use facilita la auditoría de seguridad y la adaptación a requerimientos específicos sin generar dependencia exclusiva del proveedor. Estas características, verificadas en el relevamiento propio de la documentación pública de la plataforma, consultada el 19-10-2026, confluyen para posicionar a N8N como la opción más adecuada para el escenario propuesto, donde la soberanía sobre los datos y los flujos de procesamiento constituye un requisito no negociable.

### Trabajos académicos previos sobre clasificación de tickets

La literatura académica sobre clasificación automática de tickets de soporte ha experimentado un crecimiento considerable durante los últimos años. La Tabla `tab:trabajos-academicos` sistematiza los trabajos más relevantes de esta subsección, organizados por enfoque metodológico y por orden cronológico.

[Paramesh2019_it_service_desk] comparan Naive Bayes multinomial, regresión logística, k vecinos más cercanos y SVM sobre tickets reales de una mesa de servicio de infraestructura de TI, y reportan buen desempeño de SVM en todas las muestras. La versión arbitrada del mismo trabajo, [Paramesh2018_csitss] (IEEE CSITSS 2018, pp. 221-227), reporta una exactitud de 90,60\,% con árbol de decisión y de 91,81\,% con RandomForest.

[Revina2020_it_tickets] abordan el mismo problema desde otra óptica: clasifican la *complejidad* del ticket (baja, media o alta) y no su categoría. Con 30 y 60 tickets etiquetados, concluyen que los métodos simples y explicables, con pocos rasgos lingüísticos del dominio, son competitivos frente a alternativas más complejas. Excluyen además, por decisión de diseño y no como resultado medido, los *word embeddings* preentrenados, con el argumento de que el vocabulario del dominio contiene numerosos términos ausentes de los corpus generales; esa tensión con el enfoque basado en LLM se retoma en la §`subsec:comparacion-literatura`.

La literatura reciente sobre clasificación de tickets no respalda un desplazamiento generalizado hacia los LLM generativos: en las comparaciones directas relevadas, los modelos tipo BERT superan a los LLM en 172 clases en turco [paket2024itservice] y, ajustados con pocos datos, son más consistentes y menos costosos que los LLM *zero-shot*: [colavito2025benchmarking] reportan un macro-F1 de 0,74 a 0,87 para los modelos tipo BERT y de 0,79 a 0,88 para los LLM en NLBSE'23, y de 0,79 a 0,82 para BERT frente a un máximo de 0,68 para los LLM en NLBSE'24.

**Tabla: Trabajos académicos previos sobre clasificación de tickets**

4pt
| **Trabajo** | **Enfoque** | **Corpus/idioma** | **Métrica reportada** | **Condición** |
| — | — | — | — | — |
| [Paramesh2019_it_service_desk] | NB, LR, kNN y SVM | tickets reales de infraestructura TI; tamaño e idioma: no reportado en el alcance revisado | no reportado en el alcance revisado (texto cerrado); cualitativo: SVM con buen desempeño; compañero arbitrado de dos de los tres autores (IEEE CSITSS 2018, pp. 221-227): árbol de decisión 90,60\,% y RandomForest 91,81\,% | clasificación clásica supervisada |
| [Revina2020_it_tickets] | complejidad baja/media/alta; TF-IDF vs. rasgos lingüísticos; kNN, DT, NB, LR, SVM, semisupervisado | 28.243 y 4.684 tickets (30 y 60 etiquetados); inglés predominante | exactitud 1,000 (árbol de decisión, rasgos lingüísticos) frente a 0,433 como máximo con TF-IDF (primer conjunto) | comparación de representaciones y selección de rasgos |
| [zangari2023ticket] | revisión + BERT; inyección de jerarquía de etiquetas | 20.000 reclamos + 35.000 issues; idioma no consignado en el resumen del artículo (acceso abierto) | mejor embedding: $>$28\,% en F1 sobre el estándar; ML-BERT: hasta 5,7\,% en F1 y 5,4\,% en exactitud (bugs) | clasificación multinivel, dos datasets |
| [paket2024itservice] | LLM (Titan, Llama, Mistral) vs. BERT; zero-shot, fine-tuning, RAG | turco, 172 clases | no reportado en el alcance revisado (texto cerrado); cualitativo: BERT supera a los LLM | clasificación multiclase de 172 clases |
| [liu2025tickit] (TickIt) | escalada de tickets con LLM; fine-tuning supervisado guiado por categoría | tickets de nube (ByteDance), 160 de prueba; idioma: no reportado en el alcance revisado | F1 0,862 (ajuste fino supervisado + CoT) frente a 0,801 como máximo con modelos pequeños | escalada online, dinámica y por relaciones |
| [colavito2025benchmarking] | benchmark de 22 LLM generativos + 2 BERT de base | dos datasets de issues de GitHub (NLBSE'23 y NLBSE'24, 1.500 issues); idioma: no reportado en el alcance revisado | macro-F1: BERT-like NLBSE'23 0,74 (RoBERTa) y 0,82-0,87 (SETFIT); NLBSE'24 0,79 (RoBERTa) y 0,82 (SETFIT); LLM zero-shot 0,79-0,88 (NLBSE'23) y hasta 0,68 (NLBSE'24); BERT ajustado más consistente | zero-shot vs. fine-tuning |

*Fuente:* elaboración propia sobre las obras citadas (resumen y texto abierto; consulta 26-10-2026).

La evaluación de modelos de lenguaje en escenarios de pocos ejemplos ha documentado que el rendimiento de clasificación depende fuertemente del idioma del corpus, con resultados que favorecen a los idiomas con más recursos en el benchmark multilingüe MEGA, que incluye tareas de clasificación [ahuja2023mega]; en un plano más general, el desempeño multilingüe también disminuye en los idiomas con menos recursos [xuan2025mmluprox]. Para el español y sus variantes regionales, [grandury2025laleaderboard] construyen una tabla comparativa de LLM específica para las variedades del español de España y Latinoamérica, mientras que [mayorrocher2026spanish] evalúan modelos con pruebas de español como lengua extranjera, [bernalbeltran2025mexicanspanish] comparan ajuste fino y aprendizaje en contexto sobre español mexicano, y [ramonferrer2026tripletotext] evalúan modelos de bajos recursos sobre un corpus en español. Esta línea sugiere, como inferencia de los autores a partir de las obras citadas, que el español, y en particular sus variantes regionales como el rioplatense, ha recibido una atención notablemente menor en las evaluaciones sistemáticas publicadas. Cabe acotar, además, una brecha concreta en el alcance revisado: en las fuentes consultadas hasta la fecha de corte del protocolo de revisión de este capítulo (21 de octubre de 2026), con las cadenas de búsqueda allí declaradas, no se identificó artículo arbitrado 2023-2026 que evalúe Google Gemini sobre tickets de soporte en español. Esta ausencia relativa al alcance revisado constituye una de las motivaciones académicas del presente trabajo.

### Calibración de la confianza y cascadas de modelos

[Guo2017_calibration] mostraron, en experimentos que incluyen clasificación de documentos, que las redes neuronales modernas tienden a la sobreconfianza y que esta se corrige a posteriori con un parámetro de temperatura. En la clasificación por instrucciones, [Zhao2021_calibrate_before_use] hallaron en GPT-3 y GPT-2 sesgos hacia ciertas etiquetas, que una calibración contextual de la distribución de salida reduce. Para modelos consultados solo por texto, [Tian2023_verbalized_confidence] hallaron, en preguntas y respuestas, mejor calibración de la confianza verbalizada que de las probabilidades condicionales, y [Xiong2024_confidence_elicitation] observaron sobreconfianza, valores concentrados en el extremo alto de la escala y que predecir las fallas sigue siendo un desafío.

En las cascadas, [Varshney2022_model_cascading] consultan modelos de capacidad creciente solo si la confianza de predicción del anterior no alcanza un umbral, con mejoras de eficiencia y exactitud en clasificación de comprensión del lenguaje natural; [Chen2024_frugalgpt] proponen una cascada de LLM de costo creciente con una función de puntaje aprendida y un umbral para aceptar o escalar. En las fuentes consultadas con C1 y C2 hasta el 25 de octubre de 2026 no se identificó trabajo arbitrado que evalúe una cascada de reglas determinísticas y un LLM con confianza verbalizada sobre tickets de soporte en español; la ausencia es relativa al alcance revisado.

### Análisis comparativo y brecha identificada

La Tabla `tab:comparativa` compara las principales soluciones revisadas en tres dimensiones: modalidad de despliegue, clasificación automática y modelo de costo.

**Tabla: Comparación de soluciones para gestión automatizada de mesa de ayuda**

| **Solución** | **Despliegue** | **Clasificación automática** | **Modelo de costo** |
| — | — | — | — |
| Zendesk Suite | SaaS comercial | Sí, módulo de IA | Alto, por agente/mes |
| Freshdesk | SaaS comercial | Sí, motor Freddy AI | Medio-alto, por agente |
| Jira Service Mgmt | SaaS o autoalojado | Limitada en plan estándar | Medio, por agente |
| ServiceNow ITSM | SaaS comercial | Sí, Predictive Intelligence | Muy alto, contrato anual |
| osTicket | Código abierto | No nativa | Sin costo |

*Fuente:* elaboración propia a partir de la documentación oficial de cada plataforma [Zendesk2026_help_desk, Freshdesk2026_platform, Atlassian2026_jira_service_management, ServiceNow2026_itsm, osTicket2026], consultada el 19 de octubre de 2026 (Jira Service Management y osTicket, verificadas además el 9 de noviembre).

La síntesis comparativa evidencia que ninguna de las soluciones revisadas combina simultáneamente las tres propiedades que la tabla releva y que el contexto del trabajo demanda: despliegue autoalojado para resguardo de datos sensibles, costo bajo y predecible en el tiempo, y capacidad nativa de clasificación automática mediante NLP moderno. La brecha identificada, en el alcance revisado en este capítulo y hasta la fecha de corte declarada, se sintetiza en la ausencia de soluciones de bajo costo, autoalojadas, con clasificación basada en modelos de lenguaje grandes y validadas empíricamente sobre corpus en español rioplatense para el dominio específico de mesas de ayuda empresariales medianas.

La presente investigación se ubica precisamente en esa intersección y propone una arquitectura compositiva que reutiliza componentes maduros de código abierto y servicios de inferencia bajo demanda, manteniendo bajo control de la organización los datos sensibles y los flujos de orquestación, y aportando evidencia empírica reproducible sobre el desempeño del enfoque en un contexto lingüístico y organizacional escasamente documentado en la literatura, y sumando un canal telefónico con transcripción automática como rasgo propio, sin pretensión comparativa.

## Marco metodológico

### Enfoque y tipo de investigación

La investigación se enmarca dentro del enfoque cuantitativo aplicado, dado que propone el desarrollo de una solución informática orientada a mejorar el funcionamiento de un proceso organizacional concreto y mide su impacto mediante indicadores numéricos. [HernandezSampieri2018_metodologia] ubican este tipo de estudios dentro de la investigación tecnológica de carácter aplicado, donde el conocimiento producido se orienta a la transformación práctica de la realidad antes que a la generación de teoría general. El trabajo es además cuasiexperimental: diseña, implementa y evalúa un artefacto tecnológico con asignación no aleatoria de casos y control parcial de las condiciones.

### Diseño experimental

El diseño experimental adoptado es de tipo cuasiexperimental con muestras pareadas y mediciones repetidas. La unidad de observación es el incidente individual, y cada uno se procesa secuencialmente bajo dos condiciones: la condición manual y la condición automatizada. Procesar el mismo conjunto por ambas vías reduce la variabilidad de las características intrínsecas de cada caso y aumenta la potencia estadística del contraste entre flujos.

Para acotar el efecto de aprendizaje del operador humano sobre el corpus, el diseño adoptó una ejecución secuencial pareada: los mismos 200 casos se procesaron primero por el flujo manual (junio a agosto de 2026) y luego por el flujo automatizado (septiembre a octubre de 2026; §`fig:cronograma`). El procesamiento manual se distribuyó entre dos operadores experimentados, rotados entre las dos mitades del corpus (100 casos por mitad). Con dos operadores y dos mitades, ambos quedan colineales: la rotación confunde el efecto de aprendizaje con el del operador, de modo que no se presenta como mitigación efectiva sino como limitación reconocida del diseño (véase la §`subsec:amenazas-validez`); sí conserva el control sobre la variabilidad intrínseca de cada caso, al medir el mismo incidente bajo ambas condiciones. El conjunto de las dos corridas de 2026 se denomina en adelante *campaña 2026-10*, y sostiene los valores de referencia del estudio. Para cerrar las mediciones pendientes se instrumentó una *campaña complementaria de medición*, con sujetos independientes y su propio protocolo (§`subsec:protocolo-pruebas`); esa denominación distingue a la campaña nueva en el resto del documento. El plan de la campaña complementaria fija para cada caso su `posicion`, su `mitad` y el `brazo_primero` que, con intención de contrabalancear el orden, se procesaría primero. En la ejecución, sin embargo, el brazo manual precedió al automatizado en los 200 casos (manual: 5 de noviembre, de 09:20 a 18:49 UTC\(-3\); automatizado: del 5 de noviembre, 23:47 UTC, al 6 de noviembre, 22:45 UTC): el contrabalanceo planificado no se ejecutó y el efecto de orden queda sin estimar (§`subsec:amenazas-validez`).

La investigación se desenvolvió bajo un protocolo de medición en vivo. Los dos operadores del brazo manual de la campaña 2026-10 son los analistas originales que fijaron la referencia (§`subsec:poblacion-muestra-corpus`); trabajaron en pares y se cronometraron mutuamente, de modo que sabían que la campaña registraba tiempos, aunque no se anunció el inicio de cada cronometraje. El propósito comparativo (el contraste con un flujo automatizado) se ocultó, a lo sumo, al operador externo (`A1`); el operador que es también autor del trabajo (`T1`) lo conocía por esa condición, de modo que para él no hubo enmascaramiento. La sesión de esclarecimiento (*debriefing*) alcanzó solo a `A1`. Así se atenuó, sin eliminarlo, el efecto Hawthorne —la alteración del comportamiento de los sujetos cuando saben que están siendo observados— [McCambridge2014_hawthorne], que subsiste como amenaza residual (§`sec:discusion`). En el flujo manual, el compañero de par que no registraba el incidente cronometró en vivo el tiempo total, consignado en segundos con redondeo hacia arriba. De los 200 valores, 199 son múltiplos de 5 s y 180 de 10 s, resolución efectiva del instrumento que vincula los descuentos de 5 s y 10 s del análisis de sensibilidad con el procedimiento. El redondeo al alza constituye un sesgo de medición sistemático que infla el tiempo manual y su efecto se acota mediante el análisis de sensibilidad reportado en la §`sec:resultados`.

### Operacionalización de variables

La Tabla `tab:variables` presenta la operacionalización de las variables del estudio, distinguiendo entre variables cuantitativas continuas, cuantitativas proporcionales y cualitativas nominales. Cada variable se acompaña de su unidad de medida y de la definición operacional aplicada durante la captura, garantizando la trazabilidad entre la definición conceptual y el procedimiento de medición efectivo.

**Tabla: Operacionalización de variables del estudio**

| **Variable** | **Tipo** | **Unidad** | **Definición operacional** |
| — | — | — | — |
| Tiempo de registro | Cuantitativa continua | Segundos (s) | Lapso entre la recepción del incidente en el canal de entrada y la persistencia confirmada del ticket en la base de datos. |
| Exactitud de clasificación | Cuantitativa proporcional | Porcentaje [0; 100] | Cociente entre incidentes correctamente clasificados y total de incidentes evaluados. |
| F1 macro promediado | Cuantitativa proporcional | Adimensional [0; 1] | Promedio aritmético del F1 de cada sector; el de umbral excluye los de soporte unitario. |
| Intervención humana | Cuantitativa proporcional | Porcentaje [0; 100] | Se reporta de dos formas rotuladas: proporción de casos que requieren acción manual de un operador humano y proporción del tiempo total del proceso dedicado a esa acción. La fuente por caso es el export de intervenciones de la campaña complementaria de medición, que registra el origen de cada intervención (`gate`, `muestreo`, `rederivacion` o `completado_manual`). |
| Canal de origen | Cualitativa nominal | Categoría | Vía de entrada: correo electrónico, formulario web o llamada telefónica. |
| Categoría asignada | Cualitativa nominal | Categoría | Sector responsable, uno de los cinco sectores canónicos: Seguridad Informatica, Soporte Tecnico Hardware, Soporte Tecnico Software, Bases de Datos o Sistemas. |

*Fuente:* elaboración propia.

### Población, muestra y corpus

La población de referencia está constituida por la totalidad de los incidentes informáticos reportados a la mesa de ayuda de la organización analizada. A partir de un universo aproximado de 2.646 incidentes —proyectado como 42 incidentes diarios sobre los 63 días hábiles del período relevado (\(42 63 2.646\))—, se construyó, por muestreo estratificado con asignación proporcional a la distribución por sector observada en el período relevado, un corpus de 200 casos pseudonimizados distribuidos entre los cinco sectores canónicos: Soporte Tecnico Hardware 85, Soporte Tecnico Software 67, Seguridad Informatica 31, Sistemas 16 y Bases de Datos 1. La distribución del universo por sector no está disponible, por lo que esa proporcionalidad no es verificable; Bases de Datos quedó con un único caso, no estimable por clase, y en replicaciones convendría sobremuestrear las clases minoritarias. Los casos provienen de tres canales de origen: llamada telefónica 81, correo electrónico 66 y formulario web 53. El flujo manual se cronometró entre junio y agosto de 2026; sobre los mismos 200 casos, el flujo automatizado se ejecutó entre septiembre y octubre de 2026.

El tamaño muestral se determinó mediante la fórmula clásica de muestreo aleatorio simple con corrección por finitud, apropiada porque el universo relevado es finito y relativamente acotado:

 n = N\, z^2\, p\,(1-p)e^2\,(N-1) + z^2\, p\,(1-p),

equivalente a \(n = n_0 / [1 + (n_0 - 1)/N]\) con \(n_0 = z^2\, p\,(1-p)/e^2\). En ella, \(N 2.646\) es el tamaño del universo trimestral, \(z = 1,96\) corresponde a un nivel de confianza del 95 %, \(p = 0,5\) es la proporción esperada conservadora (la que maximiza la varianza \(p(1-p)\) y, con ella, el tamaño requerido) y \(e\) es el margen de error absoluto. El tamaño del corpus se fijó, no obstante, por disponibilidad operativa: los 200 casos son los incidentes efectivamente cronometrados en la campaña manual, no un tamaño derivado a priori de la fórmula. Con esos insumos y ese tamaño fijo, el margen de error implicado bajo corrección por finitud es del 6,66 %, cifra que la fórmula reproduce recíprocamente con \(n 200,0\) y que resulta razonable para un estudio piloto de viabilidad técnica previo a un despliegue definitivo.

La construcción del corpus aplicó criterios de exclusión explícitos. En primer lugar, se descartaron los incidentes duplicados, entendiendo por tales los reportados más de una vez sobre el mismo hecho, ya sea por repetición en un mismo canal o por ingreso concurrente por canales distintos. En segundo lugar, se descartaron las descripciones vacías o insuficientes, esto es, los registros sin contenido textual clasificable o cuya extensión no permitía inferir un sector responsable. En cambio, los casos con pertenencia simultánea a más de un sector (multicategoría) y las descripciones muy breves pero clasificables se conservaron deliberadamente por ser representativos del entorno operativo real, con una etiqueta primaria como sector responsable. Esto es coherente con el análisis de errores de la §`sec:resultados`, donde las descripciones muy cortas y la mezcla de categorías figuran entre los patrones de error dominantes: excluirlos habría sesgado el corpus hacia casos artificialmente limpios y sobreestimado el desempeño del clasificador.

Cada incidente del corpus fue revisado y etiquetado de forma independiente por dos analistas con experiencia en la mesa de ayuda: uno externo al equipo de autores y otro que es también autor del trabajo (`T1` en el registro de sujetos de la campaña). La independencia que respalda la validez de constructo es de carácter funcional: los analistas no fueron instruidos según el comportamiento del sistema y no tuvieron acceso a las predicciones del clasificador al momento de etiquetar; la coincidencia analista-autor acota esa independencia y se retoma entre las limitaciones (§`sec:discusion`). Los dos analistas son, además, quienes operaron el brazo manual de la campaña 2026-10 (§`subsec:diseno-experimental`): esta coincidencia no altera el cómputo del acuerdo inter-evaluador, pero implica que la etiqueta de referencia y el brazo de comparación comparten sujetos, lo que acota la independencia del *ground truth* respecto de los operadores cronometrados (§`subsec:amenazas-validez`). Las discrepancias entre analistas fueron resueltas por consenso bajo la supervisión del director del trabajo. El acuerdo entre evaluadores se calculó mediante el coeficiente Kappa de Cohen [Cohen1960_kappa]; el valor obtenido (\( = 0,87\)) se interpreta como casi perfecto según los rangos habitualmente aceptados, que sitúan el acuerdo casi perfecto por encima de \( > 0,80\) [Landis1977_kappa]. Este valor respalda la confiabilidad de la categoría de referencia utilizada como verdad fundamental (*ground truth*) para evaluar el clasificador automático. El \( = 0,87\) se informa sin intervalo de confianza: su cálculo exige la tabla de acuerdo observado y esperado o las etiquetas por caso de ambos analistas, que no se conservaron en las fuentes disponibles. La campaña complementaria retoma esta limitación con un doble etiquetado nuevo sobre los mismos 200 casos, a cargo de `E1` y `E2`, distintos entre sí, de los dos analistas originales, de los autores y de los operadores del brazo manual, sobre una planilla única y sin acceso al consenso, a las predicciones ni a las etiquetas del par. Su tabla primaria se conserva con su SHA-256 en `evaluation/data/campana/doble_etiquetado.csv` (400 registros), de modo que su kappa admite intervalo de confianza, a diferencia del valor de la campaña 2026-10. La referencia del brazo manual de esa campaña es el consenso de `E1` y `E2`; los casos discordantes se excluyen y se informan aparte.

### Protocolo de pruebas

El protocolo se ejecutó en dos fases. La primera validó funcionalmente el sistema, verificando la integración de los componentes mediante: (a) pruebas unitarias del módulo Python, cuya cobertura se mide con `pytest-cov` sobre los paquetes de rutas, servicios y repositorios mediante el comando pytest –cov=app.routes –cov=app.services –cov=app.repositories –cov-report=term-missing, (b) pruebas de integración de la API y de la base de datos, junto con pruebas estructurales que validan el archivo `n8n/workflow.json`, y (c) pruebas de aceptación simuladas con incidentes sintéticos representativos de cada categoría.

La segunda fase consistió en la validación experimental propiamente dicha, en la cual los 200 incidentes del corpus se procesaron bajo ambas condiciones operativas y se registraron las variables descritas en la §`subsec:operacionalizacion-variables`. El procesamiento manual lo realizaron dos operadores experimentados, con más de tres años de antigüedad en la mesa de ayuda y capacitados en el sistema de tickets de referencia. El automatizado de la campaña 2026-10 se ejecutó sin intervención humana en la captura y con el gate de revisión aplicable, en la ventana de septiembre a octubre de 2026; la procedencia de cada conjunto de datos se declara al final de esta sección.

**Procedencia de los datos del brazo automatizado.** Los datos del brazo automatizado provienen de tres corridas con configuraciones distintas del clasificador. Los tiempos de correo y formulario (119 casos) se midieron el 2-10-2026: el autor Luca Gomez ejecutó el arnés de ingesta `scripts/corpus_ingest/ingest_via_n8n.py` con sus valores por defecto (`–source json` y `–insecure`, sobre la URL base por defecto `https://localhost` a través del proxy inverso), que envió cada caso por el canal real del flujo N8N (un correo nuevo al buzón dedicado o un envío al webhook del formulario), con la descripción pseudonimizada como texto; el tiempo va del envío a la persistencia del incidente e incluye, en el correo, la espera de la recogida por el disparador IMAP, configurado para sondear el buzón una vez por minuto (el intervalo efectivo no se midió sobre N8N 2.11.2, de modo que no consta). El host SMTP del arnés reside en `scripts/corpus_ingest/ingest.env`, excluido del control de versiones, por lo que no consta. Regían el vocabulario original del filtro (89 patrones), el *prompt* sin reglas de frontera y el cortocircuito por confianza determinística \( 0,90\) (`hybrid-v1`), que fuera de línea resuelven por reglas 72 de los 200 casos (Tabla `tab:sensibilidad-ajustes`). Los 81 tiempos telefónicos se midieron en una corrida realizada el 5 y 6 de octubre de 2026 (25 casos el 5 y 56 el 6, con unas 2 y 3 horas de trabajo, respectivamente; las horas de reloj exactas no constan), en un entorno aislado: el autor Luca Gomez recitó las llamadas desde un *softphone* VoIP de navegador e interpretó parafraseando la descripción pseudonimizada, con la grabación acotada a 45 s, sobre la computadora SF20GM7. El autor confirma que las únicas repeticiones fueron R126 y R002; el texto no se apoya en el sidecar para acreditarlas, porque este consolida una fila por caso. La versión desplegada que procesó los 56 casos del 6 de octubre (imagen de `backend-corpus` y flujo importado en `n8n-corpus`) no consta. La corrida no tiene configuración única: los 25 casos del 5 de octubre son anteriores a c-71 (vocabulario) y c-72 (clasificación unificada con la cascada del *backend*), contemporáneos de las llamadas del 6; todas son anteriores al cortocircuito evaluado (c-74). Las métricas de clasificación provienen de una ejecución fuera de línea del *framework* sobre el corpus JSON, generada el 7-10-2026 a las 22:22 UTC con `hybrid-v3`, que versiona el commit `d6bb474` (Tabla `tab:configuracion-evaluada-entregada`; evidencia: evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json; hash del corpus `1fd17d7e...`, cuya entrada no difiere en descripciones ni etiquetas de la previa al recálculo). El 19-10-2026 los tiempos telefónicos se recalcularon sumando la duración de la grabación a la latencia posterior al cuelgue, para igualar la base con el tiempo manual, que incluye escuchar la llamada. Como las corridas de tiempos invocaban al modelo más que la configuración evaluada, no favorecen al flujo automatizado frente a ella (inferencia, no medición).

**Protocolo de la campaña complementaria de medición.** La campaña complementaria de medición se ejecutó con un plan explícito por caso (`plan_campana.csv`), que fija la `posicion`, la `mitad` y el `brazo_primero` planificado de cada incidente; en la ejecución el brazo manual precedió al automatizado en los 200 casos (§`subsec:diseno-experimental`). El brazo manual lo operaron dos operadores experimentados, `O1` y `O2`, distintos de los etiquetadores, de los analistas originales y de los autores, que registraron el tiempo por incidente en la planilla única `brazo_manual.csv`. La intervención humana sobre el flujo automatizado se instrumentó siguiendo el procedimiento del export de intervenciones (c-165): cada acción manual queda registrada por caso con su origen (`gate`, `muestreo`, `rederivacion` o `completado_manual`) en `intervenciones.csv`. La campaña corrió con el clasificador congelado en la configuración evaluada (`hybrid-v3`; §`tab:configuracion-evaluada-entregada`), con la regla del reportante activa y una salida en vivo que difiere de la caché en 13 casos; sus métricas son comparables con las de la campaña 2026-10 solo calculadas sobre la caché, y sus tiempos alimentan el análisis del efecto de posición.

### Métricas e instrumentos

La evaluación del sistema se sustenta en cuatro métricas principales. La primera es el tiempo medio de registro: media aritmética y mediana de los tiempos individuales por condición, con su desvío estándar muestral, mínimo, máximo y reducción relativa. La segunda es la exactitud global de clasificación, calculada como la proporción de incidentes correctamente derivados al sector responsable. La tercera es el valor F1 macro promediado, media aritmética de los valores F1 de cada clase estimable (variante que [Opitz2019_macro_f1] distinguen del F1 de la precisión y la sensibilidad macro promediadas), que neutraliza el desbalanceo de clases del corpus [Sokolova2009_performance_measures]. La cuarta es la proporción de intervención humana, en dos dimensiones rotuladas: casos que requieren intervención y tiempo dedicado a tareas manuales, cuyo denominador es el tiempo de registro automatizado más la duración de la intervención, no el tiempo total de atención (§`subsec:reduccion-intervencion`); no se midió en la campaña 2026-10, por ausencia de registro primario, y se mide en la campaña complementaria con el export de intervenciones, que registra el origen de cada acción por caso. Sobre esa campaña se calculan dos métricas que la campaña 2026-10 no midió: la exactitud del brazo manual —derivaciones correctas frente a la referencia del doble etiquetado nuevo—, con su contraste frente al automatizado, y la tasa de intervención humana del flujo automatizado con su intervalo de confianza.

Como instrumentos de captura se utilizaron: (a) registros automáticos generados por el propio sistema con marcas de tiempo precisas al milisegundo para el flujo automatizado, (b) una planilla de cronometraje observacional para el flujo manual, completada en vivo por el compañero de par que no registraba el incidente, con el tiempo total por incidente en segundos y redondeo hacia arriba, y (c) matrices de confusión generadas mediante la biblioteca scikit-learn [Pedregosa2011_scikit_learn]. En el flujo automatizado, el tiempo de registro del canal telefónico comprende tanto la duración de la llamada grabada como la latencia de procesamiento posterior al cuelgue, mientras que los canales de correo electrónico y formulario web se miden como latencia de extremo a extremo de su procesamiento. Dado que la grabación telefónica está acotada a un máximo de 45 s (véase la §`sec:implementacion`), la duración de la llamada registrada —y por lo tanto el tiempo automatizado telefónico— constituye una cota inferior de la duración real de la llamada.

### Análisis estadístico

Para la comparación de los tiempos de registro entre ambas condiciones se aplicó la prueba de Wilcoxon de rangos con signo [Wilcoxon1945_individual_comparisons], prueba no paramétrica para muestras pareadas, dado que la prueba previa de normalidad de Shapiro-Wilk [Shapiro1965_normality] rechazó la hipótesis de normalidad en los tres conjuntos analizados, todos con \(n = 200\): tiempos manuales (\(W = 0,803\), \(p = 3,71 10^-15\)), tiempos automatizados (\(W = 0,902\), \(p = 3,47 10^-10\)) y diferencias pareadas (\(W = 0,822\), \(p = 2,37 10^-14\)). En los tres casos el valor \(p\) queda muy por debajo del nivel de significancia \( = 0,05\), lo que respalda el uso de una prueba no paramétrica. En lo que sigue se denotan \(T^+\) y \(T^-\) la suma de los rangos de las diferencias positivas y negativas, respectivamente. La implementación de referencia (`scipy.stats.wilcoxon` en su variante de dos colas) devuelve como estadístico de contraste el menor de ambos, es decir \(W = (T^+, T^-)\); por lo tanto \(W = T^-\) cuando el flujo automatizado resulta más rápido que el manual en la mayoría de los pares, que es el caso del corpus analizado. Los \(p\) de tiempos son bilaterales, conservadores frente a la \(H_1\) direccional; el unilateral global (`alternative=greater`) es \(1,54 10^-32\).

Para cuantificar la magnitud práctica de la diferencia se calculó el coeficiente \(r\) de correlación rank-biserial [Kerby2014_rank_biserial], indicador de tamaño del efecto para pruebas no paramétricas. El cálculo se define directamente a partir de los dos estadísticos de rango, \(r = (T^+ - T^-) / [n(n+1)/2]\), donde \(n\) es el número de pares. La expresión equivale a \(1 - 4Wn(n+1)\) cuando \(W = T^- = (T^+, T^-)\), y su rango teórico es \([-1, +1]\).

Para el análisis de la clasificación se construyó la matriz de confusión global y se calcularon los valores de precisión, sensibilidad (recall) y F1 por cada clase, así como su promedio macro. La referencia de verdad es multietiqueta (107 de los 200 casos, 53,5 %) y el clasificador emite una etiqueta principal: las métricas primarias son monoetiqueta (exactitud estricta y macro-F1 de umbral) y las secundarias, multietiqueta (subset accuracy, Hamming loss y micro-F1) [Tsoumakas2007_multilabel]. Estas se calculan sobre el conjunto predicho de cada caso (la etiqueta principal más los sectores adicionales que emite la etapa determinística, en 8 casos), y la Hamming loss se normaliza por la unión de las etiquetas verdaderas y predichas del caso (equivalente a \(1 -\) Jaccard), no por las cinco clases. Como métrica secundaria operativa se calculó además la exactitud laxa (sector predicho principal dentro del conjunto de verdad del caso), distinta de la estricta, que sigue siendo la primaria; ambas se desagregaron por etapa y por canal con intervalo de Wilson, y la confianza se analizó por etapa, porque cada una emite una magnitud distinta. Las proporciones por clase se acotaron con el método de Wilson [Wilson1927_probable_inference]; el F1 por clase y las métricas de conjunto, con el bootstrap percentil de [Efron1993_bootstrap] a nivel de caso (2000 remuestreos, semilla fija). La clase de soporte unitario (Bases de Datos, \(n = 1\)) se declara no estimable y se excluye del macro-F1 de umbral, contra el cual se evalúa el criterio de 0,85. Todos los cálculos se realizaron mediante la biblioteca SciPy del ecosistema Python [Virtanen2020_scipy].

**Análisis de la campaña complementaria de medición.** Sobre la campaña complementaria de medición se agregan los siguientes contrastes. El kappa del doble etiquetado nuevo se informa con intervalo de confianza, estimado por dos vías: la aproximación asintótica de [Fleiss1969_large_sample] y el bootstrap percentil a nivel de caso (2000 remuestreos, semilla fija). Las proporciones por operador se acotan con el método de Wilson, y la exactitud agregada del brazo manual, con el bootstrap percentil por caso. La exactitud del brazo manual se contrasta con la del brazo automatizado mediante la prueba de McNemar sobre los casos con predicción de ambas vías, tomando como referencia el consenso del doble etiquetado nuevo. El análisis de orden se limita al efecto de *posición* del caso en la secuencia, estimado por correlación de rangos de Spearman; el contraste entre los grupos `brazo_primero` no estima el efecto de orden, porque ambos grupos recibieron el brazo manual primero (§`subsec:diseno-experimental`). Para cada contraste se informa el efecto mínimo detectable (MDE) que reporta el análisis de la campaña, sin fijar valores a priori. La segunda sub-hipótesis se contrasta contra la cota de 0,15 con una regla de tres vías: compatible si el límite superior del intervalo de Wilson queda por debajo de 0,15; refutada si la estimación puntual alcanza o supera 0,15; y no concluyente si la estimación queda por debajo de 0,15 pero su límite superior no. Aplicada a la campaña complementaria, la revisión humana alcanzó 66 casos de correo, 81 de telefonía y ninguno de los 53 del formulario web; sobre los 147 revisados, 25 cambiaron la derivación (17,0 %; IC de Wilson [11,8 %, 23,9 %]) y la sub-hipótesis resulta *refutada*, mientras que el cociente sobre 200 (12,5 %) se informa solo como dato secundario.

### Amenazas a la validez

Se identificaron y trataron explícitamente cuatro amenazas a la validez del estudio.

La primera, una amenaza a la validez interna por efecto de aprendizaje del operador humano sobre el corpus, se acotó parcialmente mediante la ejecución secuencial pareada descrita en la §`subsec:diseno-experimental`; como se anticipó allí, la rotación de operadores entre las dos mitades no elimina la amenaza (el efecto de operador queda confundido con la mitad del corpus) y se declara como limitación no resuelta del diseño, no como una mitigación efectiva. En la campaña complementaria el efecto de orden tampoco se resolvió (el brazo manual precedió al automatizado en los 200 casos y el contraste entre grupos `brazo_primero` no lo estima); solo se estima el efecto de posición, significativo para uno de los dos operadores y acotado por su efecto mínimo detectable (§`sec:resultados`).

La segunda, una amenaza a la validez de constructo por la subjetividad de la categorización, se mitigó mediante el doble etiquetado independiente, el Kappa de Cohen y la resolución de discrepancias por consenso supervisado; su valor (\( = 0,87\)) corresponde a un acuerdo casi perfecto según los rangos de Landis y Koch [Landis1977_kappa]. Los analistas etiquetadores son las mismas personas que operaron el brazo manual y uno de ellos es autor del trabajo (§`subsec:poblacion-muestra-corpus`): esa coincidencia no invalida el acuerdo inter-evaluador, pero acota la independencia del referente y se asume como limitación explícita. Esa misma coincidencia acota la atenuación del efecto Hawthorne en el brazo manual: para el operador que es autor del trabajo el enmascaramiento del propósito comparativo no existió, de modo que el sesgo de novedad u observación no se distribuye por igual entre los dos operadores; su dirección no se declara, por falta de evidencia sobre cuál fue más rápido. El \( = 0,87\) se informa sin intervalo, porque su tabla primaria no se conservó; la campaña complementaria aporta, con etiquetadores y operadores independientes, un kappa propio con intervalo, que no es el intervalo del \(0,87\) (§`sec:resultados`).

La tercera, una amenaza a la validez externa derivada del idioma y del dominio organizacional, se reconoce como limitación explícita del estudio: los resultados no son extrapolables sin nuevas validaciones a corpus en otros idiomas, en otras organizaciones o en otros sectores de la economía.

La cuarta, una amenaza a la validez de conclusión derivada del tamaño moderado de la muestra (\(n = 200\)), se evaluó mediante un análisis de potencia estadística a priori [Cohen1988_power_analysis]. Para el contraste principal —la prueba de Wilcoxon de rangos con signo sobre las mediciones pareadas, bilateral, con \( = 0,05\)— y una potencia objetivo de \(0,80\), el efecto mínimo detectable con \(n = 200\) es un tamaño del efecto estandarizado \(d_z\) (media de las diferencias pareadas sobre su desvío) de aproximadamente \(0,20\) en la aproximación normal (\(0,21\) con la eficiencia relativa asintótica \(0,864\) de la prueba de rangos frente a la \(t\) pareada [Hodges1956_efficiency]). El \(d_z\) observado, \(1,00\), lo supera más de cuatro veces; por canal es de 1,37 (telefonía), 0,73 (correo) y 1,61 (formulario web), frente a mínimos de 0,31, 0,34 y 0,38 (0,33, 0,37 y 0,41 con el ajuste), de modo que el diseño posee potencia suficiente para el contraste de tiempos. El riesgo se concentra, en cambio, en la precisión de las estimaciones de clasificación (exactitud por clase, macro-F1), que se reportan con intervalos de confianza (Wilson para las proporciones, bootstrap percentil para F1). La amenaza se trata, además, con pruebas no paramétricas robustas frente a tamaños muestrales pequeños y a desviaciones de la normalidad [HernandezSampieri2018_metodologia].

### Gestión del proyecto bajo enfoque Scrumban (método de construcción del artefacto)

Este apartado describe el método de construcción del artefacto, no el de investigación: el diseño experimental, el muestreo, el corpus y el análisis estadístico se definieron en las Secciones 4.1 a 4.8, mientras que la gestión bajo Scrumban concierne solo a cómo se construyó el sistema y se documenta por trazabilidad.

La construcción del sistema siguió un esquema Scrumban, que combina la planificación por iteraciones de Scrum con el flujo continuo de Kanban [Ladas2009_scrumban], con iteraciones de duración y número variables; su detalle y relación con las campañas figuran en la §`subsec:conexion-scrumban` y la §`fig:cronograma`.

La distribución de roles asignó la coordinación general, la integración de componentes y la telefónica (Twilio) a Luca Gomez, y la implementación inicial del módulo Python, la base de datos, el frontend y el flujo N8N a Gonzalo Sevilla; Carla Bustos revisó la tesis y colaboró en los anexos y la corroboración de fuentes. La dirección académica correspondió a los directores de la portada, el Prof. Alberto Cortez y el Prof. Ariel Enferrel.

El tablero Kanban se gestionó en Jira con seguimiento diario y planificación por iteración; la coordinación del grupo, en GitHub Projects. La definición de terminado (*Definition of Done*) exigió pruebas unitarias aprobadas, revisión por pares y documentación actualizada.

## Arquitectura del sistema

### Visión general

El sistema propuesto se estructura como una arquitectura distribuida y modular compuesta por cinco capas claramente diferenciadas, siguiendo los principios de cohesión alta y acoplamiento bajo descritos por [Pressman2020_software_engineering]. En el diseño se previó proteger la comunicación con el exterior mediante TLS 1.2/1.3 a nivel de un proxy inverso (Nginx); la terminación TLS 1.2/1.3 se verifica de forma automatizada sobre el despliegue de referencia de la release v1.2.2 (prueba de humo de la §`subsec:pruebas-automatizadas`, cuyo runbook se cita en el Anexo `sec:anexo-documentacion-operativa`; despliegue de referencia en el Anexo `sec:anexo-diagrama-arquitectura`), con certificado autofirmado de referencia; la campaña experimental usó dos despliegues, y la distinción es relevante: la medición telefónica del 5 y 6 de octubre de 2026 corrió sobre el perfil Compose aislado `corpus`, que no incluye el proxy inverso, mientras que la ingesta del brazo automático del 2 de octubre lo hizo sobre el stack base, que sí incluye Nginx con el certificado autofirmado de referencia; en ningún caso las mediciones de la §`sec:resultados` dependen de TLS. En producción, el adoptante debe proveer un certificado emitido por una CA (autoridad certificadora). La comunicación interna entre los servicios del sistema (N8N, backend, PostgreSQL) se realiza sobre la red aislada de Docker, que constituye el perímetro de confianza. Todas las interfaces entre capas utilizan el estilo arquitectónico REST con cuerpos JSON para el intercambio estructurado de datos [Fielding2002_rest]. Esta separación de responsabilidades facilita el reemplazo independiente de cualquier componente sin afectar a los demás.

La Tabla `tab:capas` sintetiza las cinco capas y sus responsabilidades específicas, y la Figura `fig:componentes` (Anexo `sec:anexo-diagrama-arquitectura`) detalla la organización en capas del módulo de procesamiento.

**Tabla: Capas funcionales de la arquitectura del sistema**

| **Capa** | **Componentes y responsabilidades** |
| — | — |
| 1. Canales de entrada | Casilla de correo electrónico monitoreada mediante IMAP/SMTP, formulario web implementado como SPA React y número virtual de Twilio cuya grabación se transcribe en el backend con la Gemini API. |
| 2. Orquestación | Motor N8N 2.11.2 desplegado en contenedor Docker autoalojado. Normaliza la entrada y coordina la invocación a las capas inferiores. |
| 3. Procesamiento | Servicio Python sobre FastAPI 0.115 (configuración evaluada; Tabla `tab:configuracion-evaluada-entregada`) ejecutado bajo Uvicorn. Aplica clasificador híbrido en dos etapas (reglas + LLM) y expone una API REST documentada con OpenAPI 3.1. |
| 4. Inferencia | Modelo Gemini 3.6 Flash de Google, invocado únicamente cuando el filtro determinístico previo no resuelve el caso (§`subsec:subsistema-clasificacion`). |
| 5. Persistencia | PostgreSQL 15.5 desplegado en contenedor con volumen persistente y respaldos diarios. Almacena los incidentes y la trazabilidad de cada decisión del clasificador. |

*Fuente:* elaboración propia.

La trazabilidad operativa se garantiza mediante registros estructurados en cada capa, accesibles desde la capa de orquestación. La Figura `fig:arquitectura` representa esquemáticamente el flujo de información entre capas. El despliegue del entorno local —servicios, redes Docker (edge, data interna, automation y host_access), volúmenes y servicios externos— se detalla en la Figura `fig:despliegue`, y el flujo extremo a extremo de un incidente, desde el canal de entrada hasta la confirmación o la derivación a revisión, en la Figura `fig:secuencia` (Anexo `sec:anexo-diagrama-arquitectura`).

[Figura: Diagrama de arquitectura del sistema: cinco capas y tres canales de entrada (correo, formulario web y telefonía), en la configuración entregada (release `v1.2.16] (`fig:arquitectura`)

[Figura: Diagrama de despliegue del entorno local. Servicios, redes Docker (edge, data interna, automation y host_access), volúmenes y servicios externos.] (`fig:despliegue`)

### Capa de canales de entrada

La capa de canales de entrada habilita tres vías paralelas a través de las cuales un usuario puede reportar un incidente. La primera es el correo electrónico, monitoreado mediante IMAP/SMTP que detecta nuevos mensajes en una casilla institucional dedicada. La segunda vía es un formulario web implementado como aplicación React de página única (SPA) que se comunica directamente con la API REST del módulo de procesamiento. La autenticación se realiza mediante tokens JWT (JSON Web Tokens) con usuario y contraseña; la autenticación única corporativa (SSO) se prevé como evolución para entornos productivos (§`sec:recomendaciones`). La tercera vía es la llamada telefónica, en la cual el usuario marca un número virtual provisto por Twilio, recibe instrucciones por voz pregrabadas y deja su solicitud; Twilio graba la llamada y notifica la grabación al backend, que la transcribe con la Gemini API y la entrega al flujo N8N. El script TwiML que define el flujo de la llamada —incluyendo el mensaje de bienvenida en español rioplatense y la configuración de grabación— se implementa en el módulo de backend del proyecto (`app/cost_guard/twiml.py`), versionado en el repositorio. Esta diversidad de canales amplía la accesibilidad del sistema y reduce las barreras al reporte oportuno.

### Capa de orquestación

N8N actúa como orquestador principal del flujo de trabajo: recibe la entrada de cada canal, la normaliza en una estructura unificada y coordina la clasificación y la persistencia del incidente. La descripción operativa detallada del flujo —los disparadores por canal, la estructura normalizada con identificador único (UUID v4), la invocación al módulo Python y la persistencia del ticket— se desarrolla en la subsec:construccion-flujo-n8n`. Los registros de cada ejecución se conservan durante 30 días para fines de auditoría y diagnóstico operativo; constituyen un conjunto de datos distinto de los incidentes, cuya retención se rige por la política declarada en la §`subsec:principios-datos`.

### Capa de procesamiento

El módulo de procesamiento se implementó como un servicio web ligero utilizando el marco FastAPI 0.115, expuesto sobre un servidor ASGI Uvicorn 0.30.6 (versiones de la configuración evaluada; Anexo B, Tabla `tab:configuracion-evaluada-entregada`) [Tiangolo2024_fastapi]. La elección de FastAPI obedece a su soporte nativo de validación de esquemas mediante Pydantic, su rendimiento competitivo y su documentación automática conforme a la especificación OpenAPI 3.1.

Las dependencias del módulo se organizan por capas funcionales claramente delimitadas. La capa de acceso a datos utiliza SQLAlchemy 2.0 como mapeador objeto-relacional (ORM) y asyncpg como driver asincrónico para PostgreSQL, en coherencia con la operación no bloqueante de FastAPI. La capa de procesamiento textual emplea las bibliotecas regex y unicodedata de la biblioteca estándar de Python para normalización ortográfica y eliminación de signos diacríticos. La capa de inferencia se comunica con la interfaz oficial del modelo `gemini-3.6-flash` mediante el cliente google-genai >=2.20.0 de la configuración evaluada (SDK unificado de Google Generative AI), con los siguientes parámetros de configuración: temperatura \(= 0,3\), top_p \(= 0,9\), max_tokens \(= 100\) y timeout \(= 30\) s por intento del backend al modelo, con un presupuesto total de \(60\) s por clasificación. Estos valores corresponden a la configuración adoptada para el despliegue y no a un procedimiento de optimización documentado; su calibración sistemática frente a valores alternativos se plantea como trabajo futuro (§`sec:recomendaciones`). Las bibliotecas NumPy 2.1 y Pandas 2.2 se utilizan exclusivamente para la generación de reportes agregados de desempeño y no participan del flujo de procesamiento individual de incidentes.

### Subsistema de clasificación híbrido

El subsistema de clasificación adopta un enfoque híbrido en dos etapas, característica que lo diferencia de aproximaciones puramente basadas en modelo externo. La primera etapa aplica un filtro determinístico basado en expresiones regulares y diccionarios de términos del dominio. La procedencia de los datos empleados para construir el filtro determinístico, redactar las reglas de frontera del prompt y fijar el punto de operación se declara en la §`subsec:interpretacion-resultados`. La especificación detallada del prompt y de los parámetros de configuración del modelo se documenta en el Anexo H.

Este filtro resuelve de inmediato los incidentes con marcadores léxicos inequívocos y emite dos magnitudes en \([0;1]\) que no son probabilidades de acierto: la *confianza*, índice de fuerza de señal —margen del sector ganador sobre el segundo, ponderado por la cantidad de patrones coincidentes— que vale 0 con menos de dos patrones, y el *puntaje de correctitud* (`score_correctitud`), que ordena la correctitud esperada. El filtro decide sin consultar al modelo (cortocircuito) cuando la señal es dominante —sin empate ni ausencia de coincidencias— y el puntaje alcanza el punto de operación 0,5166; la confianza no interviene y esos casos no se derivan a revisión por su confianza. El punto se derivó por validación cruzada de cinco pliegues sobre el corpus, maximizando la cobertura sin que la precisión del filtro fuera inferior a la del modelo sobre el conjunto que resuelve (0,7385 frente a 0,6769 sobre los 130 casos con predicción de ambas etapas, ambas estimadas dentro de la muestra; §`subsec:sensibilidad-ajustes`), y equivale a resolver los 131 casos con señal dominante.

La segunda etapa, activada únicamente cuando el filtro determinístico no resuelve el caso, consulta al modelo Gemini 3.6 Flash mediante un prompt estructurado en español que incluye una breve descripción de cada categoría, un único ejemplo representativo por sector y la solicitud explícita de devolver la categoría asignada y un valor numérico de confianza entre 0 y 1 en formato JSON estricto. El diseño compositivo reserva la capacidad semántica del modelo para los casos que el filtro no resuelve, lo que reduce la latencia y el costo de inferencia. El pipeline completo comprende tres etapas, aplicadas en orden: (1) el filtro determinístico, (2) el modelo Gemini y (3) una etapa de reserva (*fallback*) que, cuando el modelo no responde o no produce una salida válida, fija la confianza en 0,0 y marca siempre el caso para revisión humana. La regla `requiere_revision_humana = (confianza < 0,`70) se evalúa solo sobre la salida de la etapa Gemini; la etapa de reserva deriva siempre a revisión, con confianza 0,0, y la etapa determinística no deriva por su confianza. Desde el 13 de octubre de 2026, posterior a la campaña 2026-10, el backend deriva además a revisión el incidente cuyo reportante no se identifica en el directorio de empleados, condición independiente de la clasificación. El desglose de casos resueltos por cada etapa del pipeline sobre el corpus de validación se reporta en la §`sec:resultados`.

El camino de clasificación es único para los tres canales de entrada. Tanto el correo electrónico y el formulario web como la llamada telefónica resuelven su sector mediante esta misma cascada híbrida, aplicada sobre la descripción pseudonimizada del incidente: ningún canal aporta una clasificación precalculada que omita la cascada, de modo que las reglas determinísticas, el prompt y las reglas de frontera se ajustan una sola vez para todo el sistema. El prompt único incorpora reglas de desambiguación de frontera entre sectores adyacentes (acceder o iniciar sesión en una aplicación se orienta a Soporte Tecnico Software; la digitalización, el escáner o la impresora se orientan a Soporte Tecnico Hardware; el servidor, la red, SMTP o una VM se orientan a Sistemas). Desde el punto de vista del costo, la clasificación telefónica dejó de computarse sobre una invocación incondicional al modelo externo: el canal atraviesa el filtro determinístico y solo escala al modelo semántico cuando la cascada lo requiere.

### Modelo de datos

La persistencia se realiza sobre PostgreSQL 15.5, desplegado en contenedor Docker bajo configuración de respaldo diario y replicación física opcional para entornos productivos [PostgreSQL2024_docs]. El modelo de datos se organiza alrededor de siete entidades principales, descritas en la Tabla `tab:entidades` y en el diagrama entidad-relación de la Figura `fig:er_modelo_datos`.

**Tabla: Entidades principales del modelo de datos de la configuración entregada (release `v1.2.16**

); el atributo reportante_empleado_id`, el cuarto rol del directorio y el cifrado del contacto son posteriores a la campaña 2026-10 (c-82, c-86 y c-153).

4pt
| **Tabla** | **Atributos clave** | **Descripción** |
| — | — | — |
| `incidente` | id (PK), descripcion_original (cifrada), descripcion_pseudonimizada, prioridad, sector_id (FK), estado_id (FK), canal_origen_id (FK), reportante_empleado_id (FK), requiere_revision_humana | Tabla central: descripción original cifrada en reposo y descripción pseudonimizada, prioridad, sector asignado, estado actual, canal de origen, reportante resuelto en el directorio e indicador de revisión humana. |
| `sector` | id (PK), nombre | Catálogo de los cinco sectores canónicos: Seguridad Informatica, Soporte Tecnico Hardware, Soporte Tecnico Software, Bases de Datos y Sistemas. |
| `estado` | id (PK), nombre, es_terminal | Catálogo de estados: nuevo, en proceso, en espera, resuelto y cerrado. |
| `canal_origen` | id (PK), nombre | Catálogo de canales: correo, formulario web y llamada telefónica. |
| `clasificacion_log` | id (PK), incidente_id (FK), sector_id_predicho (FK), sector_id_validado (FK), confianza, etapa, requiere_revision_humana | Registro de cada decisión del clasificador, con el sector predicho, la confianza asociada, la etapa que resolvió, el indicador de revisión y el sector validado por el sector responsable. |
| `users` | id (PK), username (UNIQUE), hashed_password, is_active | Almacena credenciales de operadores para autenticación JWT. |
| `directorio_empleado` | id (PK), legajo (UNIQUE), nombre, email y telefono (cifrados), email_bidx (UNIQUE), telefono_bidx, sector_id (FK), rol, activo, fecha_baja, user_id (FK) | Directorio institucional de empleados para resolución de contacto y notificación. El correo y el teléfono se cifran en reposo con Fernet y se buscan mediante un índice ciego (HMAC-SHA-256), según la decisión de c-153; el campo `rol` admite cuatro valores: usuario final, mesa de ayuda, administrador del directorio y gestión de incidentes. La columna `fecha_baja` registra la desactivación y sostiene la retención (relación laboral activa más un año). |

*Fuente:* elaboración propia a partir de `App/Backend/app/models/`.

El canal de origen constituye una entrada opcional del backend: el esquema de creación de incidentes acepta `canal_origen_id` como campo anulable, de modo que un incidente puede registrarse sin canal conocido. La entidad central `incidente` referencia mediante claves foráneas a los catálogos de sector, estado y canal de origen, y mantiene una relación uno a muchos con `clasificacion_log` para preservar la trazabilidad histórica de las decisiones del clasificador. El número de incidente que se comunica al usuario corresponde al identificador único del registro, formateado para su legibilidad; la incorporación de un prefijo configurable se prevé como evolución futura (§`sec:recomendaciones`). El esquema completo, incluyendo restricciones de integridad referencial e índices secundarios, se documenta en el Anexo C. El directorio de empleados (`directorio_empleado`) se vincula opcionalmente con la tabla de autenticación mediante `user_id` y referencia el catálogo de sectores mediante `sector_id`; su campo `rol` distingue al usuario final, a la mesa de ayuda, al administrador del directorio y a la gestión de incidentes (cuatro valores; §`tab:entidades`).

[Figura: Diagrama entidad-relación de las siete entidades principales del modelo de datos de la configuración entregada (release `v1.2.16] (`fig:er_modelo_datos`)

### Contrato de la interfaz REST

La interfaz de programación de aplicaciones expuesta por el módulo Python sigue el estilo arquitectónico REST [Fielding2002_rest`, con representación de recursos mediante identificadores uniformes, uso semántico de los métodos HTTP estándar y comunicación sin estado del lado del servidor. La autenticación se realiza mediante tokens JWT (JSON Web Tokens) firmados con HS256 (HMAC-SHA256), validados en cada solicitud mediante el esquema OAuth2PasswordBearer de FastAPI. La Tabla `tab:api] sintetiza los principales puntos de entrada.

**Tabla: Puntos de entrada principales de la interfaz REST**

| **Método** | **Ruta** | **Código** | **Función** |
| — | — | — | — |
| **Autenticación**` |
| POST | /api/v1/auth/login, /refresh, /logout | 200 OK | Inicio y renovación de sesión y cierre de sesión de operadores. |
| GET | /api/v1/auth/me | 200 OK | Recupera el perfil del operador autenticado. |
| **Incidentes** |
| POST | /api/v1/incidentes | 201 Created | Crea un nuevo ticket y devuelve el identificador generado. |
| GET | /api/v1/incidentes/id | 200 OK | Recupera la información de un ticket por su identificador. |
| PATCH | `/api/v1/incidentes/id` | 200 OK | Actualiza los campos editables de un ticket. |
| **Clasificaciones** |
| GET | /api/v1/clasificaciones/incidente/id | 200 OK | Recupera la trazabilidad de la clasificación de un incidente. |
| GET | /api/v1/clasificaciones/revision-pendiente | 200 OK | Lista los casos derivados a revisión humana. |
| PATCH | /api/v1/clasificaciones/log_id/validar | 200 OK | Registra la categoría validada por el sector responsable. |
| **Estadísticas** |
| GET | /api/v1/estadisticas/resumen, /tendencias | 200 OK | Agregados y series temporales para el dashboard. |
| **Salud** |
| GET | /health y /health/db | 200 OK | Verificación de salud del servicio para monitoreo externo. |

*Fuente:* elaboración propia.

Los códigos de estado HTTP se utilizan conforme a su semántica original: 201 cuando un recurso se crea exitosamente, 200 cuando una consulta se atiende con éxito, 400 cuando los datos de entrada no validan el esquema esperado, 401 cuando la autenticación falla, y 500 cuando ocurre un error interno no recuperable. La Tabla `tab:api` no es exhaustiva: reúne los grupos principales de puntos de entrada, mientras que el contrato completo de la interfaz —que comprende la totalidad de las rutas expuestas— se documenta en el Anexo D y se versiona en `docs/openapi.json`; la especificación OpenAPI 3.1 la genera FastAPI automáticamente.

## Implementación

### Entorno de despliegue y dependencias

La implementación del sistema se llevó a cabo combinando componentes de código abierto —Python, FastAPI y PostgreSQL— con N8N, cuya licencia Sustainable Use (*fair-code*) permite auditar su código fuente, con el objetivo de garantizar la portabilidad, la reproducibilidad y la auditoría de seguridad de la solución en organizaciones medianas. Toda la infraestructura se encapsula mediante contenedores Docker, orquestados localmente por Docker Compose [Docker2026_compose] para los entornos de desarrollo y preproducción; la migración a un cluster Kubernetes 1.30 para el entorno productivo se plantea como trabajo futuro y no cuenta con manifiestos de despliegue en esta versión (§`sec:recomendaciones`).

Las versiones específicas de los componentes de la configuración evaluada (commit `d6bb474`) son: N8N 2.11.2, Python 3.12, PostgreSQL 15.5 con volumen persistente, FastAPI 0.115, Uvicorn 0.30.6, SQLAlchemy 2.0, y el cliente google-genai >=2.20.0 (SDK unificado de Google Generative AI) para la comunicación con el modelo `gemini-3.6-flash`. Todos los servicios se despliegan sobre imágenes Docker oficiales (`python:3.12-slim` y `postgres:15.5-alpine`). La gestión de dependencias del módulo Python se realiza mediante un archivo `requirements.txt` con versiones fijadas (*pinned*) para garantizar la reproducibilidad de las compilaciones en distintos entornos. La configuración entregada (`v1.2.16`) actualiza las del *backend* y el *frontend* y sustituye la imagen oficial de N8N por una imagen derivada de `n8nio/n8n:2.11.2` con un parche de la decodificación IMAP (c-182; Tabla `tab:configuracion-evaluada-entregada`).

### Construcción del módulo Python

La selección del marco de trabajo para el servicio de procesamiento implicó la evaluación de tres alternativas: Flask, Django REST Framework y FastAPI. Flask, ampliamente adoptado por su simplicidad, carece de validación nativa de esquemas y de generación automática de documentación OpenAPI. Django REST Framework ofrece un conjunto completo de herramientas, pero su modelo sincrónico y componentes no requeridos —el ORM de Django y el motor de plantillas— incrementaban la complejidad sin aportar beneficios a un microservicio acotado. FastAPI, sustentado sobre el servidor ASGI Uvicorn, resolvió esas carencias con validación automática de esquemas mediante Pydantic v2, documentación interactiva conforme a OpenAPI 3.1 y operación asincrónica nativa ante las llamadas concurrentes desde N8N [Tiangolo2024_fastapi].

El módulo Python expone su contrato REST organizado en capas, según la estructura descrita en la §`sec:arquitectura`, con una separación clara entre responsabilidades:

 - **models**: entidades del modelo de dominio mapeadas mediante SQLAlchemy 2.0.
 - **schemas**: modelos de validación y serialización con Pydantic v2.
 - **services**: lógica de aplicación (IncidenteService, ClasificacionService).
 - **repositories**: acceso a datos, aislando las consultas SQL del resto de la aplicación.
 - **classifiers**: lógica del clasificador híbrido (filtro determinístico + LLM).
 - **routes**: enrutadores REST que delegan en los servicios correspondientes.
 - **core**: configuración de base de datos, manejo de errores y logging estructurado.

La construcción se realiza bajo un esquema de inyección de dependencias gestionado por las funcionalidades nativas de FastAPI (`Depends`), lo que facilita el reemplazo de implementaciones durante la ejecución de pruebas unitarias y de integración. Esta arquitectura permite, por ejemplo, sustituir el clasificador real por una implementación simulada durante las pruebas sin modificar el código de los servicios que lo consumen. La gestión de credenciales se realiza exclusivamente mediante variables de entorno, en línea con el principio de configuración de la metodología Twelve-Factor App [Wiggins2017_12factor].

### Construcción del flujo en N8N

El flujo de orquestación implementado en N8N comprende 32 nodos (29 operativos más 3 notas adhesivas), organizados en siete etapas funcionales con ramificaciones específicas por canal. La elección de N8N frente a Apache Airflow, Zapier o Make obedeció a tres criterios. El primero: N8N admite despliegue autoalojado bajo Docker, que mantiene el procesamiento y los datos dentro del perímetro organizacional, mientras que Zapier y Make operan solo como servicios en la nube. El segundo: su editor visual de nodos arrastrables reduce la curva de aprendizaje frente a las alternativas de definición programática, lo que permitió concentrar el esfuerzo en la lógica de negocio. El tercero: la licencia de código fuente (*fair-code*) habilita la auditoría de seguridad del núcleo de orquestación [n8n2024_docs]. Apache Airflow, aunque autoalojable, diseña sus flujos como grafos programados por intervalos temporales, un paradigma inadecuado para un sistema reactivo a eventos no programados [Apache2024_airflow].

La composición de los 29 nodos responde a un patrón de procesamiento por canal, de cinco pasos, que se replica para cada medio de ingreso con ramificaciones específicas según el canal:

[leftmargin=*]
 - **Recepción**: Tres disparadores (*triggers*) reciben las entradas desde correo electrónico (IMAP), formulario web (Webhook) y telefonía (callback de grabación de Twilio); separarlos por canal, en lugar de un único webhook con discriminación interna, preserva la configuración de autenticación y los parámetros de reintento de cada protocolo.
 - **Normalización**: Un nodo de transformación (*Function*) homogeniza el mensaje en un formato unificado [Hohpe2003_eip] con identificador único (UUID v4), marca temporal, canal de origen, remitente y descripción normalizada; esta etapa garantiza que las capas posteriores procesen la misma estructura, sea cual sea la vía de entrada.
 - **Clasificación y persistencia**: Un nodo HTTP invoca el endpoint POST /api/v1/incidentes del módulo Python con la descripción textual y los metadatos del canal. La clasificación se embebe en la creación del incidente: el clasificador híbrido se invoca internamente, la creación persiste el ticket en la misma operación y la respuesta incluye el identificador del ticket, la categoría asignada y el indicador de revisión humana (`requiere_revision_humana`), que el backend activa según las condiciones de la etapa de evaluación. El canal telefónico no es una excepción: su clasificación se resuelve en el backend con la misma cascada híbrida sobre la descripción pseudonimizada, y el cuerpo de la creación no transporta una clasificación precalculada.
 - **Evaluación**: Aguas abajo del POST, un nodo condicional (*IF*) evalúa el indicador de revisión humana: si está activo, notifica al operador designado por correo electrónico y registra el evento en la auditoría; si no, continúa con las confirmaciones al usuario. Antes del POST, un nodo de validación verifica que la descripción no esté vacía y respete la longitud aceptada, de modo que una entrada inválida no genera un incidente. El backend activa el indicador cuando la etapa Gemini devuelve una confianza inferior a 0,70, cuando interviene la etapa de reserva o cuando el reportante no se identifica en el directorio de empleados (este último, posterior a la campaña 2026-10; Tabla `tab:configuracion-evaluada-entregada`); los casos del filtro determinístico no se derivan por su confianza (§`subsec:subsistema-clasificacion`). La calibración de la confianza se analiza en la Sección `subsec:calibracion`.
 - **Notificación**: Tres nodos posteriores notifican al usuario por el canal correspondiente y registran la ejecución en auditoría; la persistencia ocurre en el mismo POST de creación. La notificación es paralela, de modo que la demora de un canal (por ejemplo, el correo) no bloquea el registro de auditoría ni la confirmación por otros medios.

El canal telefónico incorpora un nodo adicional de normalización y validación que prepara la transcripción pseudonimizada antes de incorporarla al flujo principal, pero no determina el sector persistido: la clasificación telefónica se resuelve con la misma cascada híbrida del backend que la del correo electrónico; la configuración con que se procesó cada corrida, incluido el agente LLM de N8N empleado en parte de la corrida telefónica, se declara en la §`subsec:protocolo-pruebas` y en la Tabla `tab:configuracion-evaluada-entregada`. La clasificación del incidente telefónico se rige por el diseño unificado descrito en la §`subsec:subsistema-clasificacion`.

La trazabilidad completa de cada ejecución se preserva almacenando los identificadores de nodo, las marcas temporales de entrada y salida de cada etapa, y los datos de entrada y salida de cada paso del flujo, generando un historial auditable que facilita el cumplimiento del deber de calidad de los datos del artículo 9 de la Ley 25.326 (§`sec:aspectos-legales`), sin que la ley exija literalmente esa forma de registro. La exportación completa del flujo en formato JSON se incluye en el Anexo E.

### Integración del canal telefónico

La integración con Twilio se realizó mediante el producto Programmable Voice [Twilio2026_programmable_voice], que aporta la grabación de la llamada. El flujo telefónico opera de la siguiente manera: el usuario marca un número virtual asignado a la organización; un script TwiML reproduce un mensaje de bienvenida en español rioplatense y solicita al usuario describir su problema durante un máximo de 45 segundos; la grabación finaliza cuando el usuario presiona la tecla numeral (`#`) o transcurrido el tiempo máximo; Twilio notifica la grabación al backend mediante un *callback*; el backend descarga el audio, lo transcribe con la Gemini API (`gemini-3.5-transcribe`) [Google2026_gemini_audio], pseudonimiza el texto y lo entrega a N8N mediante un webhook. A partir de ese punto, el flujo continúa de manera idéntica a la de los canales escritos.

El tiempo de registro del canal telefónico —calculado, para igualar la base de comparación con el flujo manual, como la suma de la duración de la llamada grabada y la latencia de procesamiento desde el cuelgue hasta la persistencia del incidente (recálculo del 19-10-2026; §`subsec:protocolo-pruebas`)— promedió 20,1 segundos sobre los 81 casos del corpus. El corpus registra la suma de ambos tramos, no su descomposición por etapa (transcripción, clasificación y persistencia), de modo que no se publica un desglose de latencias que el repositorio no permite reproducir con tamaño de muestra y procedimiento de medición. La grabación está acotada a un máximo de 45 s, de modo que el tiempo telefónico reportado constituye una cota inferior de la duración real de la llamada.

Unificada la clasificación, la invocación incondicional del agente de N8N dejó de reservar superficie de costo: la clasificación se computa ahora en el backend y solo escala al modelo semántico cuando la cascada híbrida lo requiere (§`subsec:subsistema-clasificacion`).

### Desafíos de integración

La implementación del sistema enfrentó tres desafíos de integración que merecen documentación explícita.

El primer desafío se presentó en la comunicación asincrónica entre N8N y el servicio de clasificación. El nodo HTTP de N8N invoca el endpoint de clasificación de manera sincrónica y espera la respuesta del servidor antes de continuar el flujo. Esta arquitectura, aunque simple de implementar, introduce un punto de fallo único: si el servicio Python no responde, el flujo completo se detiene y el incidente queda sin procesar. Para acotar esa exposición, la configuración entregada —no la evaluada; Tabla `tab:configuracion-evaluada-entregada`— declara en el tramo de alta una política de reintento acotada sobre sus dos nodos HTTP: hasta tres intentos con una espera fija de cinco segundos y un tiempo de espera por intento de diez segundos en el inicio de sesión del operador y de setenta y cinco segundos en la creación del incidente, de modo que el peor caso del tramo queda por debajo del tope de ejecución configurado para la plataforma. La espera es fija y no un retroceso exponencial, y el reintento es idempotente: la clave de deduplicación se calcula una sola vez por ejecución, de modo que un reenvío no duplica el incidente. Agotados los intentos, la ejecución se desvía hacia la rama de error del flujo. La invocación de alta sigue siendo sincrónica y la cola de respaldo en el servicio Python, que retendría los mensajes durante ventanas de saturación, queda como trabajo futuro (§`subsec:cola-respaldo`).

El segundo desafío surgió de la heterogeneidad de los formatos de entrada. Los correos electrónicos incluyen encabezados, firmas corporativas y reenvíos que contaminan el texto que el clasificador recibe; las llamadas telefónicas transcritas introducen errores de reconocimiento del habla, particularmente en términos técnicos (por ejemplo, `API` transcrito como `a p i` o `apeye`); y los formularios web, aunque proveen texto limpio, llegan con una proporción significativa de campos vacíos o con descripciones de una sola palabra. La respuesta a esta heterogeneidad fue doble. Por un lado, se implementó un preprocesador en el nodo de normalización de N8N que elimina firmas, encabezados de reenvío y líneas de disclaimer mediante expresiones regulares específicas del dominio de correo institucional. Por el otro, se enriqueció el prompt enviado al clasificador con instrucciones explícitas para interpretar términos técnicos frecuentemente mal transcritos, lo que mejoró la robustez de la clasificación sobre transcripciones automáticas respecto de la configuración inicial sin estas instrucciones.

El tercer desafío, de naturaleza operativa, se vincula con la persistencia transaccional de la sesión de clasificación. El sistema debe garantizar que una vez que el clasificador asigna una categoría, el incidente se persiste con esa decisión o, en caso de falla de la base de datos, el estado interno del sistema refleje la inconsistencia y pueda recuperarse. La solución adoptó un enfoque pragmático: N8N invoca la creación del incidente —que clasifica y persiste en una sola operación del backend— como paso único del flujo. El nodo HTTP de creación declara un enrutamiento de error (`continueErrorOutput`) que opera una vez agotados los reintentos descritos en el primer desafío: si la persistencia falla tras los intentos, la ejecución se desvía hacia la rama de error del flujo en lugar de continuar. La recuperación del incidente exige una reejecución manual del flujo o el reproceso del mensaje de origen; esa recuperación es segura porque el alta es idempotente, de modo que un reenvío no duplica el incidente ni vuelve a clasificarlo. La tabla de trazabilidad (`clasificacion_log`) conserva un registro por clasificación ejecutada: un replay no agrega registros, y cada replay deja un evento estructurado con el identificador de origen y el del incidente, sin datos personales.

### Conexión con el proceso Scrumban

La construcción del sistema fue organizada bajo el esquema Scrumban descrito en la §`sec:marco-metodologico`, ejecutando iteraciones de duración variable, ubicadas sin fechar por separado en los dos períodos de actividad del repositorio (§`fig:cronograma`, Anexo A). La vinculación entre cada etapa de construcción y los artefactos de implementación producidos se detalla a continuación:

[label=Etapa *:, leftmargin=*]
 - La elicitación de requisitos produjo el diseño preliminar de la arquitectura de cinco capas y la especificación de la interfaz REST, documentadas en la §`sec:arquitectura`.
 - La construcción del módulo Python entregó el modelo de datos, los repositorios con operaciones CRUD asincrónicas y los servicios de negocio; al cierre de la etapa exponía el endpoint de salud y aceptaba la creación de incidentes mediante POST /api/v1/incidentes, con la cobertura unitaria medida por pytest-cov sobre rutas, servicios y repositorios (§`subsec:pruebas-automatizadas`).
 - La configuración inicial del flujo N8N implementó el canal de correo electrónico como vía prioritaria y fijó el patrón de procesamiento por canal que luego se replicaría; al finalizar la etapa, el sistema procesaba incidentes por correo de extremo a extremo, de la recepción a la notificación.
 - La integración del canal telefónico y la persistencia incorporó Twilio Programmable Voice, el script TwiML y el callback de grabación y transcripción en el backend; fue la etapa que más expuso los desafíos de heterogeneidad de formatos (§`subsec:desafios-integracion`) y su resolución consumió cerca del 40 % del esfuerzo de la etapa.
 - La validación funcional y el ajuste fino del clasificador se concentraron en la calibración del filtro determinístico y del prompt de Gemini, a partir de los errores observados en el corpus de validación; no se dispuso de un conjunto independiente de preproducción (§`subsec:interpretacion-resultados`).
 - La validación experimental y la documentación final ejecutaron el protocolo de pruebas descrito en la §`sec:marco-metodologico`, recolectaron las mediciones del corpus completo y produjeron el análisis estadístico presentado en la §`sec:resultados`.

La campaña del flujo manual (junio a agosto de 2026) no es una etapa de construcción; la del flujo automatizado (septiembre a octubre de 2026) corresponde a la validación experimental, con `gemini-3.6-flash` integrado el 24 de septiembre de 2026.

La trazabilidad entre etapas y artefactos, mediada por el tablero Kanban en Jira, permitió identificar tempranamente los desvíos respecto del plan y redistribuir el esfuerzo ante imprevistos, y los límites de trabajo en curso evitaron la acumulación de tareas a medio terminar (§`subsec:gestion-scrumban`).

### Pruebas automatizadas

La estrategia de pruebas se sustentó en la pirámide clásica descrita por [Crispin2009_agile_testing]. En la base se ubicaron las pruebas unitarias del módulo Python construidas con el marco pytest (versiones en la Tabla `tab:configuracion-evaluada-entregada`). La cobertura de código de aplicación se mide con pytest-cov sobre los paquetes de rutas, servicios y repositorios, mediante el comando pytest –cov=app.routes –cov=app.services –cov=app.repositories –cov-report=term-missing, cuyo reporte se genera en cada ejecución del pipeline de integración continua. Estas pruebas cubren los clasificadores (determinístico e híbrido), los servicios de negocio, los esquemas de validación y los repositorios de acceso a datos.

En el nivel intermedio se ejecutaron pruebas de integración en dos variantes complementarias: (a) pruebas rápidas contra SQLite en memoria para la ejecución durante el desarrollo, utilizando el fixture `db_session` con rollback por test; y (b) pruebas de integración contra una instancia real de PostgreSQL 15.5, que validan comportamientos específicos del motor —integridad de claves foráneas, eliminación en cascada, restricciones UNIQUE, precisión de tipos `Numeric(5,4)` y zona horaria en `TIMESTAMPTZ`, índices compuestos y coexistencia de esquemas— mediante 54 pruebas marcadas como integración, que fallan de forma ruidosa si PostgreSQL no está disponible en lugar de omitirse. En el nivel superior, la configuración entregada —no la evaluada; Tabla `tab:configuracion-evaluada-entregada`— incorpora una prueba de humo de extremo a extremo que instancia N8N activo sobre una variante de costo cero del workflow versionado, sin los nodos que requieren credenciales de terceros: el recorrido envía un incidente por el webhook del canal web y verifica su persistencia, su canal de origen, que la clasificación se resuelve en la etapa determinística, la idempotencia del alta ante un reenvío y la recuperación ante una indisponibilidad transitoria del backend. La prueba excluye la etapa Gemini real, que la variante nunca invoca, y el canal telefónico, y se reejecuta sobre el commit etiquetado en cada release. La integración con la plataforma de orquestación se verifica además de forma estructural, mediante pruebas que parsean y validan el archivo `n8n/workflow.json` (composición de nodos, conexiones y límites de costo) y pruebas de API y de base de datos que ejercitan los endpoints y la persistencia del módulo Python.

El frontend se desarrolló como una aplicación React de página única (SPA; versión en la Tabla `tab:configuracion-evaluada-entregada`) con TypeScript y Vite como herramienta de construcción. La aplicación consta de dos vistas principales: un portal de reporte de incidentes con validación de formularios, y un panel de administración que incluye listado de tickets con filtros combinados, cola de revisión humana para los casos derivados por el backend, y visualización detallada de cada incidente con trazabilidad completa de la decisión del clasificador. La comunicación con el backend se realiza mediante Axios, y la gestión del estado del servidor se apoya en React Query para caching y revalidación automática.

El frontend cuenta con una suite de pruebas automatizadas construida con Vitest y Testing Library, que alcanza una cobertura de sentencias del 99,6 % sobre los paquetes medidos, conforme al reporte reproducido con `npm run test:coverage`.

La integración continua (CI) se ejecuta automáticamente en cada solicitud de incorporación (*pull request*) al repositorio mediante GitHub Actions, ejecutando la suite completa de pruebas unitarias y de integración antes de permitir la fusión a la rama principal. El pipeline de CI incluye verificación de estilo de código (Ruff), ejecución de pruebas con reporte de cobertura, y verificación de sincronización de la especificación OpenAPI.

### Dashboard de analítica

El panel de administración incluye un dashboard de analítica desarrollado con la biblioteca ReCharts de React. Este módulo proporciona visualización agregada de los datos históricos de incidentes, permitiendo identificar tendencias temporales, patrones de fallas recurrentes y desequilibrios en la distribución de carga entre sectores. Esta capacidad de análisis retrospectivo transforma los datos operativos acumulados en inteligencia organizacional accionable. La Figura `fig:panel_admin` muestra el panel de administración sobre el que se integra esta capacidad analítica, con el listado de tickets, los filtros combinados y la pestaña de revisión humana, que lista los casos que el backend marcó con su indicador de revisión (§`subsec:reduccion-intervencion`).

[Figura: Panel de administración del sistema: listado de tickets con filtros combinados y cola de revisión humana. Captura del 21-10-2026 (c-80) de una instancia local de desarrollo con rótulo v1.0.0: los tickets visibles son del 2 y del 13-10-2026 y la cola (94 casos) refleja el indicador `requiere_revision_humana] (`fig:panel_admin`)

El dashboard se organiza en tres visualizaciones principales. Un gráfico de tendencias muestra la evolución temporal de los incidentes, agrupables por día o por mes según la granularidad seleccionada por el operador. Un gráfico de torta presenta la distribución proporcional de incidentes entre los cinco sectores responsables. Un gráfico de barras apiladas desglosa los incidentes según su estado en el ciclo de vida, facilitando la identificación de cuellos de botella en la resolución. La Figura fig:dashboard` presenta estas tres visualizaciones junto con los indicadores agregados del período seleccionado.

[Figura: Dashboard de analítica del panel de administración: tendencia temporal de incidentes, distribución por sector y distribución por estado. Misma captura (21-10-2026, instancia local de desarrollo, rótulo v1.0.0), con 145 incidentes entre el 21-09 y el 21-10-2026 (el 2-10 concentra el pico); la tasa de revisión humana (64,8 %, 94 de 145) es el indicador registrado por el backend en esa base y difiere de la evaluación fuera de línea (subsec:reduccion-intervencion] (`fig:dashboard`)

Los controles de filtro permiten acotar el período de análisis mediante un rango de fechas configurable, y alternar entre agrupación diaria y mensual para adaptar la granularidad al horizonte temporal de interés. Cada gráfico puede exportarse como imagen PNG para su inclusión en informes periódicos o presentaciones.

La utilidad práctica del dashboard puede ilustrarse con un escenario hipotético: si el sistema detectara que veinte usuarios reportaron la rotura de auriculares en una franja temporal acotada, el patrón sugeriría un problema de calidad del proveedor antes que una serie de fallas aisladas.

## Consideraciones éticas y aspectos legales

### Marco normativo aplicable

El sistema desarrollado se enmarca normativamente en la Ley 25.326 de Protección de los Datos Personales de la República Argentina [Ley25326_2000], en su decreto reglamentario, el Decreto 1558/2001 [Decreto1558_2001], y en las disposiciones complementarias emitidas por la Agencia de Acceso a la Información Pública en su carácter de autoridad de aplicación. Dado que el sistema realiza transferencia de fragmentos textuales hacia infraestructura de inferencia operada por proveedores con sede en los Estados Unidos, resultan aplicables las consideraciones del artículo 12 de la mencionada ley sobre transferencia internacional de datos personales y, de manera complementaria, los lineamientos del Reglamento General de Protección de Datos de la Unión Europea [GDPR2016] respecto de las personas que se encuentren en la Unión (artículo 3.2 del RGPD). El artículo 2 de la ley define la disociación como el tratamiento que impide la identificación del titular, figura que complementa aquí a la pseudonimización. La Unión Europea reconoce a la Argentina como país con nivel adecuado de protección de datos personales mediante la Decisión 2003/490/CE, del 30 de junio de 2003 [Decision2003_490_CE], revalidada en enero de 2024. Esta adecuación ampara el flujo desde la Unión Europea hacia la Argentina y no opera en sentido inverso: los Estados Unidos no figuran entre los países adecuados para la normativa argentina [DNPDP2016_disposicion60], de modo que la transferencia desde la Argentina hacia los proveedores de inferencia y de telefonía con sede en ese país requiere un instrumento específico conforme al artículo 12 de la Ley 25.326, según se detalla en la §`subsec:transferencia-internacional`.

### Principios aplicados al tratamiento de datos

El diseño se atiene a cinco principios del tratamiento de datos personales. La licitud se funda en el artículo 5, inciso 2, apartado d) de la Ley 25.326, que admite tratar los datos que deriven de una relación contractual, científica o profesional y resulten necesarios para su cumplimiento: la organización es la empleadora y trata datos de sus propios empleados para gestionar los incidentes que estos reportan. Esta base se distingue del consentimiento analizado para el corpus académico en la §`subsec:consentimiento-derechos` y no dispensa el deber de información del artículo 6 de la Ley 25.326. La finalidad determinada limita el uso de los datos a la declaración y derivación de incidentes, sin usos secundarios no compatibles. La minimización se materializa en que solo se almacena el usuario corporativo y un directorio acotado —legajo, nombre, correo electrónico corporativo, teléfono, sector y rol— para resolver el contacto y notificar al usuario, descartando otros datos capturados incidentalmente (domicilios, documentos, información financiera). La exactitud opera mediante la revisión y corrección del incidente antes de su persistencia definitiva; el acceso se satisface en los diez días corridos del artículo 14 y los derechos ARCO, en los cinco días hábiles del artículo 16 de la Ley 25.326. La trazabilidad de cada decisión del clasificador se adopta como medida técnica que facilita el cumplimiento del artículo 9 de la Ley 25.326, no como una exigencia literal de la ley. La limitación del plazo de conservación fija una retención de 12 meses rodantes para los incidentes, justificada por el ciclo estadístico anual, independiente de la retención de 30 días de los registros de ejecución con fines de auditoría y diagnóstico (§`subsec:capa-orquestacion`); los datos del directorio se conservan mientras la relación laboral permanezca activa y hasta un año después de su finalización, y luego se eliminan. Vencido el plazo, los datos del incidente se someten a anonimización irreversible, de modo que se eliminan los identificadores que permiten vincularlos a una persona. El bloqueo de escritura sobre los incidentes cerrados, que rechaza con un error 409 los intentos de modificación, constituye un control de integridad de auditoría y no una excepción permanente al vencimiento del plazo. La pseudonimización y el cifrado en reposo protegen la información durante el plazo de conservación declarado.

### Transferencia internacional y pseudonimización

El tratamiento comporta dos transferencias internacionales hacia proveedores con sede en los Estados Unidos. La primera corresponde a la inferencia Gemini 3.6 Flash mediante la Gemini API [Google2026_gemini_api_terms], a la que se envían fragmentos textuales descriptivos de los incidentes; sobre ese texto, el módulo Python local pseudonimiza los nombres propios, las direcciones de correo electrónico, los números telefónicos, los identificadores corporativos y los nombres de hosts internos con etiquetas genéricas como `[PERSONA]`, `[EMAIL]` o `[HOST]`, de modo que el texto transmitido no contiene identificadores directos. La pseudonimización se valida con expresiones regulares del dominio y pruebas unitarias dedicadas. El servicio de inferencia operó en el nivel pago de la Gemini API, con créditos prepagos; en ese nivel el proveedor no utiliza el contenido transferido para mejorar sus productos [Google2026_gemini_api_pricing], lo que acota el tratamiento del dato transferido con independencia del instrumento de transferencia internacional. El comprobante de facturación se conserva en poder del director del trabajo y no se versiona por contener datos de la cuenta.

La segunda corresponde al canal telefónico: el llamante deja su solicitud y Twilio, con sede en los Estados Unidos, graba el audio [Twilio2026_programmable_voice]; el backend envía esa grabación a la Gemini API, que la transcribe [Google2026_gemini_audio], y recién después pseudonimiza el texto ya transcrito. En consecuencia, el audio crudo cruza a los Estados Unidos (a Twilio y a Google) y el número telefónico a Twilio antes de cualquier pseudonimización, que opera únicamente sobre el texto y no sobre el audio.

Ambas transferencias se dirigen a un país que no reviste la condición de adecuado para la normativa argentina, por lo que requieren un instrumento específico conforme al artículo 12 de la Ley 25.326 y su reglamentación [Decreto1558_2001, DNPDP2016_disposicion60]: el consentimiento del titular o la suscripción de cláusulas contractuales modelo. El acuerdo de procesamiento de datos suscripto con cada proveedor complementa ese instrumento, pero no lo sustituye, en tanto no configura por sí mismo una de las bases de transferencia que la ley admite.

### Seguridad técnica

Las medidas de seguridad técnica del sistema se sustentan en la triada confidencialidad, integridad y disponibilidad (CIA) descrita por [Stallings2017_computer_security], y su evidencia de control se sintetiza en la §`tab:cumplimiento-iso` (tema Tecnológico). El cifrado en reposo con Fernet (AES-128 en modo CBC con HMAC-SHA-256), el cifrado en tránsito sobre TLS 1.2/1.3 en el borde, el control de acceso por rol, el registro de auditoría de las modificaciones, la gestión de credenciales por variables de entorno y las medidas de disponibilidad —respaldo diario cifrado con prueba de restauración, contenedores con reinicio automático y monitoreo de salud— quedan mapeados allí junto con sus brechas residuales. La capa TLS 1.2/1.3 se verifica de forma automatizada sobre el despliegue de referencia de la release v1.2.2, capacidad de la configuración entregada y no de la evaluada (Anexo B, Tabla `tab:configuracion-evaluada-entregada`); los dos despliegues de la campaña experimental y la irrelevancia de TLS para las mediciones se detallan en la §`subsec:vision-general`.

### Consentimiento, derechos del usuario y supervisión humana

Los usuarios de la organización son informados, mediante una política de privacidad accesible desde los canales de entrada, sobre las características del sistema, los datos que se recolectan, la transferencia internacional aplicable y los derechos que les asisten conforme a la normativa vigente. Se garantiza el ejercicio de los derechos de acceso, rectificación, actualización y supresión (derechos ARCO) mediante un procedimiento documentado a cargo del responsable de protección de datos designado por la organización.

En lo que respecta al consentimiento informado para los fines de investigación académica, los 120 empleados de la organización fueron notificados mediante comunicación interna formal, con descripción explícita del propósito del estudio, del tipo de datos tratados, del carácter pseudonimizado de los registros y del derecho a requerir la exclusión de sus incidentes del corpus de validación. El procedimiento fue supervisado por la dirección académica del trabajo y avalado institucionalmente mediante una carta de autorización emitida por la organización adoptante.

En relación con el protocolo de medición en vivo aplicado durante la fase experimental (§`subsec:diseno-experimental`), corresponde dejar constancia de que, una vez concluida la recolección de datos, se realizó una sesión de esclarecimiento posterior (*debriefing*) con el operador que desconocía el propósito comparativo del estudio, externo al equipo de autores (`A1`); el otro operador, autor del trabajo (`T1`), lo conocía por esa condición y no requirió sesión. En dicha sesión se explicó el propósito del estudio, se detalló el procedimiento de medición empleado y se ofreció al operador la posibilidad de solicitar la exclusión de sus registros individuales del corpus de validación. El operador no ejerció este derecho. Este procedimiento se alinea con las recomendaciones de la Asociación Americana de Psicología para investigaciones que emplean medición con información diferida sobre el propósito del estudio [APA2017], y fue supervisado por el director del trabajo.

La campaña complementaria de medición (programa c-165 a c-168) se realizó asimismo con sujetos independientes, identificados en todo el registro únicamente por alias: los etiquetadores `E1` y `E2` y los operadores `O1` y `O2`. Los registros que produjeron no contienen datos personales: la tabla primaria del doble etiquetado almacena solo el alias, el identificador de caso, el sector canónico y la marca de tiempo, y el export de intervenciones identifica al actor mediante un alias derivado con clave criptográfica (HMAC-SHA256), sin nombre, correo, teléfono ni legajo. La correspondencia entre el alias y la identidad de cada sujeto se conserva fuera del repositorio, pseudonimizada; las tablas y salidas de la campaña se versionan ya en esa forma, en consonancia con la pseudonimización descrita para el corpus académico (§`subsec:consentimiento-derechos`). Los cuatro participantes fueron informados verbalmente, antes de realizar sus tareas, del propósito del estudio, del carácter pseudonimizado de los registros, de la voluntariedad de la participación y de su derecho a retirarse sin consecuencias. Con posterioridad a su participación firmaron una confirmación escrita de esa información y de su consentimiento; los originales firmados se conservan en el expediente físico del trabajo, en poder del director del trabajo, y no se versionan en el repositorio por contener datos personales. El repositorio conserva la plantilla de la confirmación y el registro de que se recabó para los cuatro participantes.

En concordancia con las recomendaciones contemporáneas sobre sistemas que incorporan inteligencia artificial, se preserva en todo momento la posibilidad de supervisión humana significativa. Ninguna decisión que afecte derechos sustanciales de los usuarios se toma de manera completamente automatizada sin posibilidad de revisión, y el sector responsable conserva la potestad de modificar la clasificación inicial cuando lo considere apropiado, registrándose tal modificación en la tabla de trazabilidad descrita en la §`sec:arquitectura`. Este mecanismo materializa el principio de la persona en el bucle (*human in the loop*) como salvaguarda frente a errores potenciales del clasificador automático. Cabe precisar su alcance: el gate de revisión se evalúa solo sobre la salida de la etapa Gemini (§`subsec:subsistema-clasificacion`), de modo que sobre el 65,5 % de los casos, resueltos por la etapa determinística, no existe derivación automática por caso basada en la clasificación; desde el 13 de octubre de 2026, posterior a la campaña 2026-10, el backend deriva además a revisión el incidente cuyo reportante no se identifica en el directorio de empleados, condición independiente de la clasificación. Para esa fracción la salvaguarda se limita al criterio con que se fijó el punto de operación del filtro —precisión no inferior a la del modelo sobre el conjunto que resuelve, estimada sobre el corpus de validación— y a la reasignación trazable del incidente descrita, disponible en la interfaz REST y expuesta en la interfaz web solo para los casos derivados. El análisis de calibración por etapa muestra que la confianza de Gemini no discrimina aciertos de errores en su rango observado (0,85 a 1,00) y que la etapa de reglas no emite una confianza utilizable para derivar (§`subsec:calibracion`); el umbral de 0,70 no garantiza, por lo tanto, la detección de errores.

### Cumplimiento normativo y alineación con estándares

#### Marco de referencia adoptado

Este apartado evalúa el grado de alineación del sistema con los marcos adoptados: ISO/IEC 27001:2022 [ISO27001_2022] y su catálogo de controles ISO/IEC 27002:2022 [ISO27002_2022], NIST CSF 2.0 [NIST2024_csf], la norma de gestión de la privacidad ISO/IEC 27701:2025 [ISO27701_2025] y la Ley 25.326. El relevamiento es estático y documental: describe el grado de alineación y las brechas identificadas, no un aseguramiento de un tercero (no constituye una acreditación externa ni una auditoría independiente), y su detalle se conserva en el repositorio (`docs/cumplimiento/`).

#### Estado de alineación con ISO/IEC 27002:2022

La Tabla `tab:cumplimiento-iso` agrupa por tema los controles de ISO/IEC 27002:2022, que corresponden al Anexo A de ISO/IEC 27001:2022; el inventario de los 93 controles reside en el repositorio.

**Tabla: Estado de alineación con los controles de ISO/IEC 27002:2022, agrupados por tema**

4pt
| **Tema** | **Controles** | **Estado** | **Evidencia / brecha principal** |
| — | — | — | — |
| Organizacional | 5.x | Parcial | Política, clasificación, roles e IR (C-61); residual: revisión independiente (5.35) |
| Personas | 6.x | No aplicable | Selección, formación, sanciones y cese: competen al adoptante |
| Físico | 7.x | No aplicable | Sin infraestructura productiva; se cubren en el hosting del adoptante |
| Tecnológico | 8.x | Alineado y parcial | Pseudonimización, Fernet, TLS, JWT y roles, vulnerabilidades en CI y respaldo cifrado (C-62 a C-66), MFA de cuentas privilegiadas (C-63b); residual: operación con KMS/PAM, logs centralizados y redundancia offsite |

*Fuente:* elaboración propia a partir del gap assessment ISO/IEC 27001:2022/27002:2022 y NIST CSF 2.0.

#### Perfil de alineación con NIST CSF 2.0

La Tabla `tab:cumplimiento-nist` cubre las seis funciones de NIST CSF 2.0 y su madurez en una escala propia del relevamiento, de 0 (inexistente) a 4 (optimizado).

**Tabla: Perfil de alineación con las funciones de NIST CSF 2.0**

4pt
| **Función** | **Subcategoría representativa** | **Madurez** | **Brecha principal** |
| — | — | — | — |
| GV (Gobernar) | Políticas, roles, riesgo y proveedores | 2 | Política, roles y evaluación de proveedores vigentes (C-61, C-64); residual: revisión independiente del adoptante (5.35) |
| ID (Identificar) | Inventario de activos y clasificación | 2 | Inventario de activos y clasificación y etiquetado vigentes (C-61; 5.9, 5.12, 5.13); residual: SBOM del adoptante |
| PR (Proteger) | Acceso, endurecimiento y criptografía | 3 | Pseudonimización, Fernet, TLS, JWT y roles, MFA de cuentas privilegiadas y SAST/auditoría de dependencias en CI (C-62 a C-64); residual: KMS/PAM y SIEM del adoptante (8.5, 8.8, 8.20, 8.24) |
| DE (Detectar) | Monitoreo y detección de eventos | 1 | Logs estructurados, chequeos de salud y retención por clase (C-66; 8.15 parcial); sin centralización ni alertas de seguridad (brecha 8.16) |
| RS (Responder) | Plan de respuesta y mitigación | 2 | Plan de respuesta a incidentes vigente (C-61; 5.24–5.27) y manejo de evidencia (5.28 parcial, C-156); residual: operación en producción del adoptante |
| RC (Recuperar) | Recuperación y restauración | 2 | Respaldo cifrado y continuidad con RTO/RPO; copia fuera del host y redundancia como acción del adoptante (5.29, 5.30, 8.13, 8.14) |

*Fuente:* elaboración propia a partir del gap assessment ISO/IEC 27001:2022/27002:2022 y NIST CSF 2.0 (`docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`, sección 4), con el estado reconciliado al 28-10-2026 (release `v1.2.16`).

#### Brechas principales y hoja de ruta

Los seis changes de cumplimiento cerraron, para el alcance del repositorio, las brechas priorizadas: C-61 (gobernanza documental: 5.1, 5.2, 5.9, 5.12, 5.13, 5.24–5.27, 5.31, 8.26), C-62 (endurecimiento de red: 8.20, 8.22, 8.2, 5.14, 8.31), C-63 (identidades y accesos: 8.5, 5.15, 5.17, 8.2), C-64 (vulnerabilidades: 8.8, 8.28, 8.29, 5.19–5.23), C-65 (respaldo y continuidad: 8.13, 8.14, 5.29, 5.30, 5.33) y C-66 (privacidad: 5.34, 8.12, 8.15, 5.31). La MFA TOTP con desafío para cuentas privilegiadas y la rotación de claves (secreto JWT y clave Fernet) quedaron implementadas en el repositorio (C-63a/b/c, archivados el 2026-10-08); su operación con KMS/PAM, la custodia de claves en producción, la centralización de logs, la redundancia fuera del host y el SBOM quedan como acción de la organización adoptante; las brechas organizacionales —personas (6.x), físicas (7.x), revisión independiente (5.35), segregación de funciones (5.3) y trabajo remoto (6.7, 8.1)— son responsabilidad de la organización adoptante.

#### Alineación con el marco legal

El plano legal de la alineación se desarrolla en el §`subsec:marco-normativo` y en la §`subsec:transferencia-internacional`, a los que este apartado remite sin reproducir su contenido. Los controles de privacidad mapeados (5.31, 5.34, 8.12, 8.15) se apoyan en la base de licitud del artículo 5 de la Ley 25.326, en el instrumento de transferencia internacional del artículo 12 y en los plazos de los artículos 14 (acceso) y 16 (rectificación, actualización y supresión).

## Resultados

Los resultados se presentan en siete apartados: tiempos de registro, métricas de clasificación, intervención humana, calibración de la confianza, sensibilidad al ajuste del clasificador, análisis de errores y campaña complementaria de medición.

Los tiempos de registro del brazo automatizado provienen de las corridas del 2 y del 5 y 6 de octubre de 2026 (con el recálculo telefónico del 19-10-2026), mientras que las métricas de clasificación provienen de una ejecución fuera de línea del 7-10-2026 con la versión `hybrid-v3`; la procedencia de cada conjunto se detalla en la §`subsec:protocolo-pruebas`.

### Comparación de tiempos de registro

La comparación de los tiempos de registro entre el flujo manual y el flujo automatizado se sintetiza en la Tabla `tab:tiempos`. La media aritmética del tiempo manual sobre los 200 casos del corpus fue de 61,6 s (mediana de 50,0 s), con un desvío estándar de 44,9 s y un rango entre 10 y 300 s. Este valor, respaldado por la planilla de cronometraje descrita en la §`subsec:diseno-experimental`, corresponde a la medición experimental incidente por incidente y reemplaza a la estimación preliminar de 2 minutos con 45 segundos citada en la §`subsec:planteamiento-problema`, obtenida sin cronometraje individual. La media del flujo automatizado fue de 17,76 s (mediana de 17,47 s), con un desvío estándar de 13,52 s y un rango entre 0,525 y 65,834 s. La reducción relativa de la media de tiempo alcanzó el 71,2 %.

**Tabla: Estadísticos descriptivos de los tiempos de registro por flujo (\(n = 200\))**

| **Estadístico** | **Flujo manual** | **Flujo automatizado** | **Reducción** |
| — | — | — | — |
| Media aritmética (s) | 61,6 | 17,76 | 71,2 % |
| Mediana (s) | 50,0 | 17,47 | 65,1 % |
| Desvío estándar (s) | 44,9 | 13,52 | — |
| Mínimo (s) | 10 | 0,525 | — |
| Máximo (s) | 300 | 65,834 | — |

*Fuente:* elaboración propia a partir del corpus de validación (\(n = 200\)).

El desagregado por canal de origen, con los dos brazos y el contraste intra-canal, se presenta en la Tabla `tab:tiempos-canal`: la reducción de la media va del 51,1 % en correo electrónico, donde se concentran los 12 pares en que el flujo automatizado no fue más rápido, al 93,4 % en formulario web, y el contraste es significativo en los tres canales. El canal telefónico incorpora, además de la latencia de procesamiento, la duración de la llamada grabada; como la grabación está acotada a un máximo de 45 s (véase la §`subsec:metricas-instrumentos`), su valor constituye una cota inferior de la duración real de la llamada. La distribución de los tiempos de registro por canal de origen, en ambos brazos, se representa en la Figura `fig:boxplot_tiempos`.

**Tabla: Tiempo de registro por canal de origen: flujos manual y automatizado, reducción y contraste intra-canal (\(n = 200\))**

2.5pt
| | | **Manual (s)** | **Automatizado (s)** | | | | |
| — | — | — | — | — | — | — | — |
| **Canal de origen** | **Casos** | **Media** | **Mediana** | **Media** | **Mediana** | **Reducción de la media** | **Pares no más rápidos** | **\(p\) bilateral** | **\(d_z\)** |
| Llamada telefónica (cota inferior) | 81 | 87,2 | 72,0 | 20,09 | 18,70 | 77,0 % | 0 de 81 | 5,36e-15 | 1,37 |
| Correo electrónico | 66 | 56,5 | 50,0 | 27,65 | 25,82 | 51,1 % | 12 de 66 | 4,78e-09 | 0,73 |
| Formulario web | 53 | 28,7 | 20,0 | 1,88 | 1,26 | 93,4 % | 0 de 53 | 2,39e-10 | 1,61 |
| **Global** | **200** | **61,6** | **50,0** | **17,76** | **17,47** | **71,2 %** | **12 de 200** | **3,08e-32** | **1,00** |

*Nota:* \(p\): valor bilateral de Wilcoxon sobre las diferencias pareadas (§`subsec:analisis-estadistico`); \(d_z\): media sobre desvío muestral de las diferencias (manual menos automatizado); \(W\), \(T^+\), \(T^-\) y \(r\) por canal figuran en `evaluation/report.md`. *Fuente:* elaboración propia a partir del corpus de validación (\(n = 200\)).

La prueba de Wilcoxon de rangos con signo aplicada sobre las mediciones pareadas [Wilcoxon1945_individual_comparisons, Virtanen2020_scipy] arrojó un estadístico de contraste \(W = (T^+, T^-) = 363\), con una suma de rangos positivos \(T^+ = 19.737\), una suma de rangos negativos \(T^- = 363\) y \(n = 200\) pares válidos, junto con un valor \(p = 3,08 10^-32\) bilateral (§`subsec:analisis-estadistico`), lo que permite rechazar la hipótesis nula sobre las diferencias pareadas con un nivel de confianza superior al 99,9 %. El estadístico refleja que en 188 de los 200 pares el flujo automatizado fue más veloz que el manual; en los 12 pares restantes (6,0 %) el flujo automatizado no fue más rápido, resultado coherente con la diferencia de aproximadamente 32,5 s entre medianas. La prueba se eligió por el rechazo de la normalidad en los tres conjuntos de tiempos (§`subsec:analisis-estadistico`).

Para cuantificar la magnitud práctica de la diferencia, se calculó el coeficiente \(r\) de correlación rank-biserial a partir de los dos estadísticos de rango (\(r = 19.374/20.100 = 0,9639\)), un tamaño del efecto muy alto. En la escala estandarizada del contraste pareado, distinta de la anterior, el tamaño del efecto es \(d_z = 1,00\) (media de las diferencias de 43,82 s sobre su desvío muestral de 43,81 s). La diferencia observada es, por tanto, estadísticamente significativa y, dada su magnitud absoluta, relativa y el tamaño del efecto reportado, también prácticamente relevante para la operación.

Cabe señalar que el tiempo manual se registró con redondeo hacia arriba (véase la §`subsec:diseno-experimental`), un sesgo de medición sistemático que infla la línea base manual. Por ese motivo la reducción del 71,2 % debe leerse como cota superior. Un análisis de sensibilidad que descuenta 5 s y 10 s a cada medición manual reduce la media manual a 56,6 s y 51,6 s, respectivamente, y sitúa la reducción en el 68,6 % y en el 65,6 % como cota inferior conservadora. Aun en el escenario más desfavorable la reducción de tiempo permanece sustancial y estadísticamente significativa (\(p = 1,8 10^-26\) bilateral, \(r = 0,8683\)).

[Figura: Distribución del tiempo de registro por canal de origen (manual frente a automatizado), para la corrida telefónica del 5 y 6 de octubre de 2026. El panel de telefonía incorpora la duración de la llamada grabada.] (`fig:boxplot_tiempos`)

### Matriz de confusión y métricas de clasificación

La evaluación de clasificación se realizó sobre el corpus real de 200 casos pseudonimizados, cuya distribución por sector y por canal se describe en la §`subsec:poblacion-muestra-corpus`.

La matriz de confusión obtenida se presenta en la Tabla `tab:matriz`. La exactitud estricta resultante asciende al 73,5 % (147 casos correctos sobre 200).

**Tabla: Matriz de confusión del clasificador automático (\(n = 200\)). Filas: sector asignado; columnas: sector predicho principal.**

4pt
tabular@>p2.6cm *5>p1.85cm >p1.3cm@

**Asignado \(\) Predicho** & **Seguridad Informatica** & **Soporte Tecnico Hardware** & **Soporte Tecnico Software** & **Bases de Datos** & **Sistemas** & **Total** 

Seguridad Informatica & 15 & 2 & 11 & 2 & 1 & **31** 

Soporte Tecnico Hardware & 1 & **77** & 3 & 0 & 4 & **85** 

Soporte Tecnico Software & 0 & 11 & **48** & 1 & 7 & **67** 

Bases de Datos & 0 & 0 & 1 & 0 & 0 & **1** 

Sistemas & 2 & 0 & 5 & 2 & **7** & **16** 

**Total** & **18** & **90** & **68** & **5** & **19** & **200** 

tabular

*Fuente:* elaboración propia a partir del corpus de validación (\(n = 200\)).

**Tabla: Exactitud estricta y laxa por etapa del pipeline y por canal de origen**

4pt
| **Ámbito** | **Casos** | **Exactitud estricta (IC 95 %)** | **Exactitud laxa (IC 95 %)** |
| — | — | — | — |
| Global | 200 | 147/200 = 0,735 [0,670; 0,791] | 179/200 = 0,895 [0,845; 0,930] |
| Etapa determinística | 131 | 97/131 = 0,740 [0,659; 0,808] | 119/131 = 0,908 [0,847; 0,947] |
| Etapa Gemini | 69 | 50/69 = 0,725 [0,610; 0,816] | 60/69 = 0,870 [0,770; 0,930] |
| Llamada telefónica | 81 | 53/81 = 0,654 [0,546; 0,749] | 70/81 = 0,864 [0,773; 0,922] |
| Correo electrónico | 66 | 51/66 = 0,773 [0,658; 0,857] | 61/66 = 0,924 [0,835; 0,967] |
| Formulario web | 53 | 43/53 = 0,811 [0,686; 0,894] | 48/53 = 0,906 [0,797; 0,959] |

*Fuente:* elaboración propia (\(n = 200\)); IC de Wilson. La etapa de reserva no registró casos; la composición sectorial y la proporción multietiqueta difieren entre canales.

Los valores de precisión, sensibilidad (recall) y F1 por clase, con su intervalo de confianza al 95 % [Sokolova2009_performance_measures], se presentan en la Tabla `tab:metricas`. La evaluación se enmarca en un único marco métrico cuya referencia de verdad es multietiqueta (107 de los 200 casos, 53,5 %), frente a una salida del clasificador de una etiqueta principal: la exactitud estricta del 73,5 % (147/200) es la métrica primaria monoetiqueta, con IC de Wilson al 95 % de [67,0 %, 79,1 %]. El macro-F1 de umbral, métrica primaria contra la que se evalúa el criterio de 0,85, se reporta sobre las cuatro clases estimables (0,6508), excluida Bases de Datos (\(n = 1\), no estimable: su F1 depende de un único incidente y pesaría un quinto del promedio), y el de cinco clases (0,5207) se conserva como valor informativo; ambos quedan por debajo del criterio, de modo que la elección no altera el veredicto. Las métricas secundarias se calculan contra el conjunto de verdad del corpus (multietiqueta): subset accuracy 0,43 (IC [0,36; 0,50]), Hamming loss 0,3586 (IC [0,31; 0,41]) y micro-F1 0,6654 (IC [0,62; 0,71]) [Tsoumakas2007_multilabel, Sokolova2009_performance_measures]. Estas métricas se calculan sobre el conjunto predicho de cada caso (una etiqueta principal y, en 8 casos de la etapa determinística, sectores adicionales; §`subsec:analisis-estadistico`) y no son equivalentes de la exactitud estricta: el micro-F1 acumula los aciertos por etiqueta y no por caso, de modo que su valor (0,6654) no debe leerse como una exactitud (0,7350). De los 200 casos, 131 fueron resueltos por la etapa determinística del clasificador y 69 requirieron la etapa Gemini. La exactitud laxa —sector predicho principal dentro del conjunto de verdad— es secundaria y no reemplaza a la estricta: alcanza el 89,5 % (179/200; IC de Wilson de [84,5 %, 93,0 %]). La Tabla `tab:exactitud-etapa-canal` desagrega ambas por etapa y por canal, como estimaciones dentro de la muestra (§`subsec:sensibilidad-ajustes`).

**Tabla: Métricas de clasificación por clase con intervalo de confianza al 95 % (una contra el resto)**

4pt
| **Clase** | **Precisión (IC 95 %)** | **Sensibilidad (IC 95 %)** | **F1 (IC 95 %)** |
| — | — | — | — |
| Soporte Tecnico Hardware | 0,8556 [0,77; 0,91] | 0,9059 [0,83; 0,95] | 0,8800 [0,82; 0,93] |
| Soporte Tecnico Software | 0,7059 [0,59; 0,80] | 0,7164 [0,60; 0,81] | 0,7111 [0,61; 0,80] |
| Seguridad Informatica | 0,8333 [0,61; 0,94] | 0,4839 [0,32; 0,65] | 0,6122 [0,44; 0,75] |
| Sistemas | 0,3684 [0,19; 0,59] | 0,4375 [0,23; 0,67] | 0,4000 [0,16; 0,59] |
| Bases de Datos | no estimable (\(n = 1\)) |

*Fuente:* elaboración propia a partir del corpus de validación (\(n = 200\)). IC de precisión y sensibilidad por Wilson; IC de F1 por bootstrap percentil (2000 remuestreos).

Las métricas por clase, calculadas según las definiciones de precisión, sensibilidad y F1 de [Sokolova2009_performance_measures], muestran un desempeño desigual entre las clases objetivo. Este desequilibrio importa en el contexto operativo, porque un clasificador que concentra sus errores en una clase minoritaria genera derivaciones erróneas en un sector específico y puede erosionar la confianza de ese equipo en la herramienta, independientemente de sus métricas agregadas.

La inspección de la matriz de confusión revela que los 53 errores totales se concentran en fronteras entre sectores léxicamente próximos, con Soporte Tecnico Software como categoría central; su análisis cualitativo, agrupado por frontera de confusión, se desarrolla en la §`subsec:analisis-errores`.

### Derivación e intervención humana en la campaña complementaria

La derivación por confianza se rige por el gate de revisión implementado (§`subsec:subsistema-clasificacion`). El gate no derivó ningún caso del corpus por confianza: en 124 de los 200 casos (62 %) la confianza registrada fue inferior a 0,70, pero todos pertenecen a la etapa determinística, cuya confianza mide fuerza de señal; los 69 casos de Gemini declararon siempre al menos 0,85 y la etapa de reserva no se activó. El 65,5 % de los casos (131 de 200) corresponde a la cobertura de la etapa determinística, no a una proporción de derivación. El resultado se interpreta en la §`sec:discusion`.

La segunda sub-hipótesis —proporción de casos con acción manual no superior a 0,15 (§`subsec:hipotesis-trabajo`)— se contrasta con el export de intervenciones de la campaña complementaria, que registró 147 intervenciones en 200 casos. Esa tasa bruta, del 73,5 % (IC de Wilson al 95 % [67,0 %, 79,1 %]), mide la regla de derivación por reportante de la configuración de la prueba y no la necesidad de revisión que la hipótesis postula: ningún caso se derivó por confianza y las 147 intervenciones corresponden a la regla de visibilidad y derivación por reportante no identificado (`VIS-005`), que el backend aplica cuando el reportante no se resuelve en el directorio de empleados. Por esa regla, la revisión humana alcanzó 66 casos de correo y 81 de telefonía y ninguno de los 53 del formulario web, cuyo reportante es la cuenta autenticada. El origen `gate` del export registra el indicador de revisión, no la regla de confianza; las demás categorías no registraron casos. La variable de la hipótesis son las intervenciones que cambiaron la derivación: 25 de los 147 casos revisados (17,0 %; IC de Wilson [11,8 %, 23,9 %]); las 122 confirmaciones restantes son el 83,0 % de los 147 revisados y el 61,0 % de los 200 casos. Sobre ese denominador, y con la regla de tres vías declarada, la estimación puntual alcanza la cota de 0,15, de modo que la sub-hipótesis resulta *refutada*; el intervalo [11,8 %, 23,9 %] no excluye el 0,15 y la prueba binomial no rechaza la cota (p = 0,28), de modo que la lectura conservadora es que no se puede descartar un valor cercano al umbral. El cociente 25 de 200 (12,5 %; IC [8,6 %, 17,8 %]) se informa solo como dato secundario, porque cuenta como ``sin acción manual'' a 53 casos web que no tuvieron oportunidad de revisión. Medirla en condiciones válidas exige una corrida con reportantes identificados (§`subsec:medicion-intervencion`). La medición completa se presenta en la §`subsec:resultados-campana-medicion`.

El cotejo de las revisiones con el consenso del doble etiquetado nuevo se informa como dato y sin lectura causal: de las 85 confirmaciones con consenso disponible, 11 confirmaron un sector que el consenso considera incorrecto, y de los 25 cambios de derivación 13 tienen consenso (9 correcciones, 1 empeoramiento y 3 de un error a otro).

La proporción del tiempo dedicado a tareas manuales, segunda dimensión de la variable, se apoya en las consignas de inicio y fin: su cobertura es de 0,9388 (147 casos con intervención y 138 con duración completa), y sobre esa base la proporción del tiempo es de 0,5307, con un intervalo bootstrap del cociente de [0,4407; 0,6111] (\(B = 2000\), semilla \(20261021\)). El denominador de esa proporción usa los tiempos automatizados de la campaña complementaria de medición (`corpus_campana.json`, 191 casos con dato completo, incluidos los 53 sin intervención) más la duración de las intervenciones, no el tiempo total de atención, lo que acota la lectura del valor.

### Calibración de la confianza

La confianza declarada solo es útil como criterio de derivación si guarda relación con la exactitud real, y las dos etapas que la emiten lo hacen con magnitudes distintas (§`subsec:subsistema-clasificacion`); por eso la Tabla `tab:bandas` desagrega la exactitud por banda y por etapa. El umbral de 0,70 del gate se evalúa solo sobre la salida de Gemini (§`subsec:reduccion-intervencion`).

**Tabla: Exactitud por banda de confianza declarada y por etapa del pipeline**

4pt
| | **Etapa determinística** | **Etapa Gemini** |
| — | — | — |
| **Banda de confianza** | **Casos** | **Aciertos** | **Exactitud** | **Casos** | **Aciertos** | **Exactitud** |
| \([0,00\,;\,0,50)\) | 98 | 75 | 0,765 | — | — | — |
| \([0,50\,;\,0,70)\) | 26 | 19 | 0,731 | — | — | — |
| \([0,70\,;\,0,85)\) | 6 | 2 | 0,333 | — | — | — |
| \([0,85\,;\,0,95)\) | — | — | — | 31 | 22 | 0,710 |
| \([0,95\,;\,1,00]\) | 1 | 1 | 1,000 | 38 | 28 | 0,737 |

*Fuente:* elaboración propia (\(n = 200\)). ``—'': la etapa no emitió confianza en esa banda; la reserva no registró casos.

El contraste agregado entre los casos de confianza alta (\( 0,70\), exactitud 0,697) y baja (\(< 0,70\), 0,758) es un efecto de composición, no una medida de calibración: los 124 casos por debajo de 0,70 son todos de la etapa determinística y el resto reúne 7 casos determinísticos y los 69 de Gemini. Por etapa, la exactitud estricta, estimada dentro de la muestra (§`subsec:sensibilidad-ajustes`), es de 0,7405 en la determinística y de 0,7246 en la de Gemini (Tabla `tab:exactitud-etapa-canal`). La confianza de Gemini, concentrada entre 0,85 y 1,00, no discrimina aciertos de errores: rinde 0,710 en la banda \([0,85\,;\,0,95)\) (IC de Wilson [53,4 %, 83,9 %]) y 0,737 en la banda \([0,95\,;\,1,00]\) ([58,0 %, 85,0 %]), con intervalos solapados, y los 46 casos con confianza igual o superior a 0,90 (45 de Gemini) incluyen 13 errores (28,3 %), todos de Gemini. La de la etapa determinística es una fuerza de señal en escala discreta que no ordena la correctitud (0,731 a 0,765 por debajo de 0,70; 0,333 en \([0,70\,;\,0,85)\), con 6 casos) y no es un criterio utilizable para derivar (§`subsec:subsistema-clasificacion`). La conclusión se restringe, así, a Gemini en su rango observado: el umbral de 0,70 no habría aislado sus 19 errores, pues su confianza nunca fue inferior a 0,85. Este hallazgo fundamenta la discusión de la §`sec:discusion`.

### Sensibilidad al ajuste del clasificador con el corpus

Las métricas de este capítulo son estimaciones dentro de la muestra (§`subsec:interpretacion-resultados`). Para acotar el sesgo atribuible al vocabulario del filtro, ampliado a partir de errores observados en el corpus, se repitió sin invocar al modelo la etapa determinística con el vocabulario previo a esa ampliación (89 de los 151 patrones), conservando la lógica de decisión y el punto de operación evaluados; con la lógica de decisión de entonces, la repetición reprodujo la medición registrada antes del ajuste. La reconstrucción del vocabulario por pliegues no es factible, porque el repositorio no registra qué casos motivaron cada patrón. La Tabla `tab:sensibilidad-ajustes` resume los resultados.

**Tabla: Sensibilidad de la exactitud al vocabulario ajustado con el corpus**

| **Filtro determinístico** | **Casos** | **Exactitud (IC 95 %)** | **Global^a** |
| — | — | — | — |
| Evaluado (vocabulario ampliado) | 131 | 0,7405 [0,6593; 0,8079] | 146/200 |
| Vocabulario previo, lógica vigente | 74 | 0,5270 [0,4148; 0,6366] | 128/200 |
| Vocabulario y lógica previos | 72 | 0,5139 [0,4007; 0,6257] | — |

*Fuente:* elaboración propia a partir del corpus de validación (\(n = 200\)) y de `evaluation/report_sensibilidad_ajustes.md`. Casos y exactitud de la etapa determinística. ^aAciertos con las predicciones de la etapa Gemini fijas (caché de calibración); la exactitud global oficial es 147/200.

El efecto de la ampliación del vocabulario admite dos lecturas que conviene separar. Por un lado, un efecto de *cobertura*, que es el dominante: el filtro determinístico pasó de resolver 74 casos a resolver 131. Por otro, un efecto de *exactitud* sobre los casos que ambas configuraciones resuelven: en los 67 casos comunes, el vocabulario ampliado acertó 38 frente a los 37 del vocabulario previo, de modo que la ampliación no deterioró la exactitud sobre los casos que ya resolvía. La diferencia de 21,3 puntos entre las exactitudes de la etapa determinística (0,7405 sobre 131 casos frente a 0,5270 sobre 74) es, si se la lee como señal del sesgo, una *cota pesimista*: es una interpretación de los autores, no una medición, porque las dos cifras se calculan sobre conjuntos de casos distintos y el vocabulario previo carece también del conocimiento del dominio que una ampliación hecha con datos independientes habría aportado. Con las predicciones de la etapa Gemini fijas, la exactitud global pasa de 146 a 128 aciertos sobre 200 casos (McNemar exacto [McNemar1947_sampling_error], \(p < 0,001\)). El efecto de las reglas de frontera del prompt, limitado a los 69 casos de la etapa Gemini, se acotó con una ablación controlada de dos brazos sobre los mismos casos y en una misma sesión: con el prompt vigente esa etapa acertó 50 de 69 y sin las reglas de frontera 46 de 69 (reservas contadas como error: 0 en ambos brazos), una diferencia que no alcanza significación (McNemar exacto entre brazos, \(p = 0,3438\)); sin los casos que las motivaron, la etapa con el prompt vigente acertó 48 de 66 (nivel a; `evaluation/report_sensibilidad_ajustes.md`, línea 95). El análisis estima la sensibilidad de las métricas y no sustituye la medición del sistema evaluado.

### Análisis de errores y casos límite

El análisis cualitativo de los 53 casos mal clasificados permitió identificar patrones de error recurrentes, agrupados por frontera de confusión y sintetizados en la Tabla `tab:errores`.

**Tabla: Confusiones observadas en la clasificación automática, por frontera, con los aciertos laxos entre los errores estrictos**

| **Frontera de confusión** | **Casos** | **Proporción** | **Aciertos laxos** |
| — | — | — | — |
| Soporte Tecnico Hardware \(\) Soporte Tecnico Software | 14 | 26,4 % | 5 |
| Sistemas \(\) Soporte Tecnico Software | 12 | 22,6 % | 10 |
| Seguridad Informatica \(\) Soporte Tecnico Software | 11 | 20,8 % | 8 |
| Otras fronteras | 16 | 30,2 % | 9 |
| **Total** | **53** | **100 %** | **32** |

*Fuente:* elaboración propia a partir del corpus de validación (\(n = 200\)) y de la evidencia de la ejecución `hybrid-v3` del 7-10-2026. Un acierto laxo es un error estricto cuyo sector predicho pertenece al sector asignado o a los sectores adicionales de la referencia (§`subsec:analisis-estadistico`). Recuento: `docs/Tesis/Correcciones/recontar_errores_frontera.py`.

El patrón dominante, presente en 14 casos (26,4 % de los errores), corresponde a la frontera entre Soporte Tecnico Hardware y Soporte Tecnico Software: incidentes en que una falla física de un equipo afecta a una aplicación, o en que una tarea sobre una aplicación se describe con términos de equipamiento, de modo que la decisión correcta depende del juicio humano sobre qué aspecto prevalece. El segundo patrón, presente en 12 casos (22,6 %), corresponde a la frontera entre Sistemas y Soporte Tecnico Software, asociada a acciones sobre servidores y servicios de plataforma descritas como problemas de una aplicación. El tercer patrón, presente en 11 casos (20,8 %), corresponde a la frontera entre Seguridad Informatica y Soporte Tecnico Software, vinculada a incidentes de acceso y credenciales. El 30,2 % restante se reparte entre las demás fronteras, incluidas las confusiones que involucran a Bases de Datos, con un único caso de soporte.

Como lectura interpretativa de la última columna de la §`tab:errores`, 32 de los 53 errores estrictos (60,4 %) derivaron a un sector que la referencia considera corresponsable (acierto laxo), y solo 21 (39,6 %) a un sector ajeno al conjunto de verdad; ambas cifras son consistentes con la exactitud laxa de 179 aciertos sobre 200 (147 estrictos más 32 laxos). La corresponsabilidad se concentra en las fronteras de Sistemas con Soporte Tecnico Software (10 de 12) y de Seguridad Informatica con Soporte Tecnico Software (8 de 11), mientras que en la de Soporte Tecnico Hardware con Soporte Tecnico Software predominan los errores plenos (9 de 14), que son los que exigen una reasignación. Esta lectura no modifica el balance neto (§`subsec:balance-neto`).

Los patrones anteriores se ilustran con tres casos con error estricto del corpus. Las descripciones se reproducen literalmente, tal como figuran en el corpus ya pseudonimizado, y se acompañan con el identificador del caso, el sector asignado, el sector predicho, la confianza y la etapa que resolvió. El primero (R001) corresponde al patrón de descripción corta: ``No puede ingresar al sistema principal'' fue asignada a Seguridad Informatica y predicha como Soporte Tecnico Software por Gemini con una confianza de 0,95; su brevedad no aporta contexto sobre el recurso ni sobre la naturaleza del acceso fallido, de modo que la frontera resulta indistinguible sin información adicional. El segundo (R032) ilustra la mezcla de categorías: ``Su PC se reinicia a cada rato, sospecha que son los cables de la computadora.'' fue asignada a Soporte Tecnico Software y predicha como Soporte Tecnico Hardware por la etapa determinística con 0,50 de confianza, y combina un síntoma de nivel de aplicación con una hipótesis de causa física cuyo peso relativo no queda determinado por el texto. El tercero (R015) ejemplifica la jerga local: ``No le salen correos por flujo del sistema principal y no le llegan las instancias'' fue asignada a Sistemas y predicha como Soporte Tecnico Software por Gemini con 0,85 de confianza, y apela a términos organizacionales (``flujo'', ``instancias'') cuyo significado no está disponible para el clasificador. La confianza se lee por etapa: en R001 y R015 la declarada por Gemini es alta (0,95 y 0,85) pese al error estricto; en R032 la de 0,50 corresponde a la etapa determinística, mide la fuerza de la señal y no es criterio de derivación a revisión (§`subsec:calibracion`). Los tres casos son aciertos laxos: el sector predicho figura entre los sectores adicionales de la referencia (§`subsec:analisis-estadistico`).

### Resultados de la campaña complementaria de medición

Esta subsección reúne los resultados de la campaña complementaria de medición, que instrumentó con sujetos independientes las mediciones que la campaña 2026-10 había dejado pendientes (§`subsec:diseno-experimental`). Sus valores **no reemplazan** los valores canónicos de la campaña 2026-10 reportados en las subsecciones anteriores. Los tiempos registrados en esta campaña alimentan el análisis del efecto de posición y la proporción de tiempo (§`subsec:reduccion-intervencion`) y no intervienen en el contraste principal de tiempos (§`subsec:comparacion-tiempos`).

**Fiabilidad del doble etiquetado.** El doble etiquetado independiente de la campaña, realizado por los etiquetadores `E1` y `E2` sobre los 200 casos, produjo un kappa de Cohen de 0,5569 ($p_o = 0,69$; $p_e = 0,30$) y un PABAK de 0,6125. El intervalo de confianza al 95 % es [0,4725; 0,6413] por la aproximación asintótica [Fleiss1969_large_sample] y [0,4751; 0,6387] por bootstrap percentil (2000 remuestreos); el rótulo de Landis y Koch del valor puntual es *moderado*, y ambos intervalos abarcan las categorías moderada y sustancial. Este kappa es un valor distinto del 0,87 de la campaña 2026-10, y su intervalo *no* es el intervalo de ese valor: el 0,87 se informa sin intervalo, porque su tabla primaria no se conservó (§`subsec:poblacion-muestra-corpus`).

**Exactitud del brazo manual.** Sobre la referencia construida como consenso de `E1` y `E2`, con los casos discordantes excluidos, la exactitud estricta del brazo manual fue de 0,8875 para `O1` (71 de 80 casos; IC de Wilson [0,7998; 0,9397]) y de 0,7606 para `O2` (54 de 71; [0,6496; 0,8448]). En forma agregada, la exactitud estricta fue de 0,8278 (125 de 151 derivaciones de operador, 80 de `O1` y 71 de `O2`, sobre 138 casos únicos, 13 de ellos con doble cobertura; IC bootstrap por caso [0,7647; 0,8882]) y la laxa, de 0,8609 (130 de 151). El contraste de McNemar entre el brazo manual y el automatizado sobre los casos con predicción de ambas vías no resultó significativo (para `O1`, $p$ exacto $= 0,2668$; para `O2`, $p$ exacto $= 1,0000$), de modo que no se detecta una diferencia de exactitud entre ambos brazos. Como referencia de comparabilidad, la exactitud estricta del brazo automatizado sobre la misma referencia nueva es de 0,7971 (110 de 138 casos; IC de Wilson [0,7224; 0,8557]). Las unidades difieren (por caso en el automatizado, por derivación en el manual), por lo que el contraste formal es el McNemar por operador, que empareja casos. El 0,7971 proviene de `predicciones_in_sample.json` (7-10), no de la salida en vivo de la campaña, que difiere en 13 casos (7 de 119 escritos y 6 de 81 telefónicos). La salida en vivo telefónica proviene de la columna `sector_predicho` del export de intervenciones (los sidecars telefónicos tienen el sector nulo) y el contraste de McNemar usa la predicción de la caché `predicciones_hybrid-v3_2026-10-07.json`. El conjunto de verdad laxo del brazo manual se define como el consenso de `E1` y `E2` más la intersección de los sectores adicionales que marcaron ambos etiquetadores. Este valor es propio de la campaña y no reemplaza la exactitud del corpus de 0,7350 (147/200) reportada en la §`subsec:matriz-metricas`, que sigue siendo la métrica primaria del clasificador.

**Efecto de posición y de orden.** En la ejecución, el brazo manual precedió al automatizado en los 200 casos (§`subsec:diseno-experimental`): los dos grupos de `brazo_primero` recibieron la misma condición en el mismo orden, de modo que su contraste no estima el efecto de orden y sus valores se consignan solo en el memo de números canónicos. El efecto de *posición* del caso en la secuencia, estimado por correlación de rangos de Spearman, no fue significativo para `O1` ($ = -0,0628$, $p = 0,5147$) y sí lo fue para `O2` ($ = -0,3604$, $p = 0,00011$), con un efecto mínimo detectable de $ = 0,276$, calculado como la tangente hiperbólica del efecto mínimo de Fisher con $n = 110$ ($n - 3 = 107$) y la eficiencia de la correlación de Spearman frente a la de Pearson bajo normalidad ($9/^2 0,912$): $((z_0,975 + z_0,80)/107 0,912) = 0,276$. Un resultado no significativo no equivale a ausencia de efecto: solo descarta magnitudes mayores que el efecto mínimo detectable de cada contraste.

**Validación fuera de muestra.** No se dispuso de un corpus independiente declarado para la validación fuera de muestra: no se obtuvieron las predicciones ni la referencia de ese corpus, de modo que la validación queda como no realizada y no se reemplaza por las métricas dentro de la muestra (§`subsec:sensibilidad-ajustes`).

## Discusión

### Interpretación de los resultados

Los resultados confirman la hipótesis de trabajo (§`subsec:hipotesis-trabajo`) en el tiempo de registro y la refutan en la clasificación, de modo que la hipótesis principal queda parcialmente confirmada y parcialmente refutada: la reducción del 71,2 % en el tiempo medio de registro es estadísticamente significativa y operativamente relevante, mientras que la exactitud estricta del 73,5 % del clasificador automático quedó por debajo del umbral del 85 % del segundo objetivo específico, resultado que se analiza entre las limitaciones. La segunda sub-hipótesis, sobre la proporción de casos con acción manual, se declara *refutada* sobre los casos revisados: la tasa bruta (147 de 200) mide la derivación por reportante no identificado; la revisión humana alcanzó 66 casos de correo, 81 de telefonía y ninguno de los 53 del formulario web, y de los 147 revisados 25 cambiaron la derivación (17,0 %; IC de Wilson [11,8 %, 23,9 %]), por encima de la cota de 0,15; el intervalo no excluye el 0,15 y la prueba binomial no rechaza la cota (p = 0,28), de modo que la lectura conservadora es que no se puede descartar un valor cercano al umbral (§`subsec:reduccion-intervencion`).

La reducción de tiempo se midió con la inferencia externa incluida y con configuraciones que invocaban al modelo con mayor frecuencia que la evaluada en la clasificación, cuya etapa determinística resuelve el 65,5 % de los casos sin invocar al modelo (§`subsec:protocolo-pruebas`); esa proporción no interviene en la reducción medida. La hipótesis subsidiaria de eficiencia del esquema híbrido no se contrastó: resolver casos sin el modelo no demuestra mayor eficiencia sin comparar la exactitud de cada alternativa. En los 131 casos de esa etapa las reglas aciertan 97/131 (0,7405) y, sobre los 130 casos con predicción de ambas etapas, 96/130 (0,7385) frente a los 88/130 (0,6769) de Gemini, ejecutado con el cortocircuito deshabilitado, estimaciones ambas dentro de la muestra y sin diferencia significativa (McNemar exacta bilateral [McNemar1947_sampling_error], \(p = 0,1516\)); además, con el vocabulario previo a su ajuste con el corpus la etapa de reglas no supera a Gemini (§`subsec:sensibilidad-ajustes`), de modo que esa ventaja no se toma como evidencia de eficiencia. El costo de inferencia recae así únicamente en los casos que el filtro no resuelve, y la latencia no se midió por etapa. La hipótesis subsidiaria de integración multicanal tampoco se contrastó: no se midió la capacidad bajo carga concurrente.

La dispersión de los tiempos automatizados muestra una compresión sustancial de la variabilidad: el desvío estándar pasa de 44,9 s en el manual a 13,52 s en el automatizado, cerca de la tercera parte, consecuencia de la automatización y no un objetivo del diseño.

Si se proyecta el ahorro medio de tiempo por incidente (\(61,6 - 17,76 = 43,8\) s) sobre el volumen trimestral de 2.646 incidentes, la automatización liberaría aproximadamente 32,2 horas-persona brutas por trimestre —unas cuatro jornadas laborales de un operador—, (Cálculo: \(43,)8 s/incidente 2.646 incidentes / 3.600 s/h 32,2\) h-persona por trimestre. tiempo que el personal podría redirigir a tareas de resolución técnica o a actividades de mejora continua. Ese ahorro es bruto: no descuenta el costo de las derivaciones erróneas que el clasificador agrega respecto del flujo manual, cuyo balance se analiza en la §`subsec:balance-neto`.

Sin embargo, la lectura conjunta de la derivación por gate y del análisis de calibración (Sección `subsec:calibracion`) matiza ese resultado, que debe leerse por etapa: el gate del 70 % presupone que la confianza declarada discrimina los casos correctos de los incorrectos, pero solo se evalúa sobre la salida de Gemini y, en el rango observado (0,85 a 1,00), esa confianza no los discrimina; la etapa determinística no emite una confianza utilizable para derivar. La supervisión humana efectiva no puede depender del umbral de confianza: debe complementarse con señales independientes del puntaje —la ambigüedad léxica entre las categorías candidatas o la revisión por muestreo de los casos de alta confianza—. El esquema *human in the loop* conserva su valor de diseño como salvaguarda, pero en el corpus la regla de 0,70 no derivó ningún caso: los 124 casos con confianza inferior a 0,70 pertenecen a la etapa determinística, a la que la regla no se aplica (§`subsec:reduccion-intervencion`).

La exactitud laxa, que acepta como acierto el sector principal predicho cuando integra el conjunto de verdad, alcanza el 89,5 % (179/200) y se lee como la proporción de derivaciones operativamente aceptables, dado que el 53,5 % de los casos admite más de un sector; no es la métrica del segundo objetivo específico y no modifica por sí misma su estado. Por canal, la exactitud estricta fue de 0,654 en la llamada telefónica, 0,773 en el correo electrónico y 0,811 en el formulario web (laxa: 0,864, 0,924 y 0,906), evidencia sobre la dimensión de calidad del tercer objetivo específico y el efecto potencial de la transcripción. La comparación no aísla ese efecto, porque la composición sectorial y la proporción multietiqueta difieren entre canales (49 de 81 telefónicos frente a 15 de 53 del formulario web): la diferencia no se atribuye a la transcripción.

La procedencia de los datos de ajuste merece una observación aparte. Las reglas de frontera del prompt, la ampliación del vocabulario del filtro y el punto de operación del cortocircuito se derivaron de errores observados en el corpus de evaluación; el punto de operación se fijó con validación cruzada fuera de muestra, pero ese protocolo no cubre la ampliación del vocabulario ni las reglas del prompt, definidas sobre la totalidad del corpus. Tampoco la campaña complementaria obtuvo un corpus independiente, de modo que la validación fuera de muestra queda como no realizada en ambas campañas (§`subsec:resultados-campana-medicion`). En consecuencia, las métricas reportadas son estimaciones dentro de la muestra, probablemente optimistas, cuya confirmación exige un corpus independiente (§`sec:recomendaciones`); la §`subsec:sensibilidad-ajustes` acota la parte atribuible al vocabulario.

La reducción del tiempo de registro, aunque estadísticamente robusta, admite explicaciones rivales. Primero, la asimetría del instrumento: el flujo manual se cronometró en vivo e incluye lectura, comprensión, búsqueda y carga del ticket, mientras que el automatizado se midió con marcas de tiempo del sistema, lo que favorece al segundo; lo debilita el análisis de sensibilidad, que mantiene la reducción por encima del 65 % aun descontando 10 s por caso, y se descartaría midiendo ambos flujos con el mismo instrumento. Segundo, la mezcla de canales: parte de la diferencia podría reflejar la composición; lo debilita el desagregado de la Tabla `tab:tiempos-canal`, con reducciones del 51,1 al 93,4 % y contraste intra-canal significativo, aunque la magnitud global depende de la composición. Tercero, la novedad o efecto Hawthorne y el aprendizaje del operador: los operadores sabían que se cronometraba y el procedimiento lo atenúa sin eliminarlo (§`subsec:diseno-experimental`); además, el enmascaramiento del propósito comparativo no existió para el operador que es autor del trabajo, de modo que la atenuación se aplica a lo sumo a la mitad del brazo manual, sin dirección declarada por falta de evidencia; el orden temporal de la campaña (manual antes que automatizado) sesga, de hacerlo, en contra de la hipótesis, y la campaña complementaria de medición no lo resolvió, porque el brazo manual precedió al automatizado en los 200 casos y el contraste entre grupos `brazo_primero` no estima el efecto de orden; el efecto de *posición* del caso en la secuencia fue significativo para uno de los dos operadores, acotado por su efecto mínimo detectable (§`subsec:resultados-campana-medicion`), de modo que el orden no se descarta como explicación rival. Cuarto, la selección de los 200 casos: por ser una muestra estratificada de una sola organización, la magnitud observada no es extrapolable sin nuevas validaciones. Ninguna de estas explicaciones rivales se descarta por completo con el diseño actual.

El patrón de error más informativo es la confusión sistemática de Sistemas: de los 16 casos asignados, solo 7 se clasificaron correctamente y los errores se repartieron entre Soporte Tecnico Software (5), Bases de Datos (2) y Seguridad Informatica (2). Esa frontera combina dos causas. La primera es una ambigüedad léxica y taxonómica: las descripciones sobre servidores, plataformas o aplicaciones admiten más de un sector, y la referencia resuelve esa ambigüedad mediante una convención que el clasificador no conoce. La segunda es falta de contexto: muchas entradas son demasiado breves para desambiguar el sector responsable y el modelo carece de señales que un operador obtendría por conocimiento organizacional. Solo la segunda admite mitigación por enriquecimiento del protocolo de captura; la primera exige revisar la taxonomía o el criterio de etiquetado. Cabe advertir, además, que Bases de Datos (\(n = 1\)) no es estimable: su F1 no debe leerse como evidencia de que el clasificador falla en esa clase, sino como ausencia de soporte estadístico.

Esa lectura no equivale a una confirmación concluyente: la evidencia es compatible con explicaciones rivales que el diseño no descarta por completo. Mientras que la reducción observada admite una lectura causal fuerte en el plano práctico —el sistema registra cada incidente en menos tiempo que el proceso manual—, su atribución a cada componente del esquema y su extrapolación a otras organizaciones permanecen abiertas. Las amenazas a la validez que acotan estas conclusiones están enumeradas en la §`subsec:amenazas-validez`.

### Comparación con la literatura

Los valores de exactitud y F1 macro obtenidos se contrastan a continuación con los reportados en la literatura comparable. [Paramesh2019_it_service_desk] comparan Naive Bayes multinomial, regresión logística, k vecinos más cercanos y SVM sobre tickets reales y reportan buen desempeño de SVM en todas las muestras, sin que el resumen consigne cifras comparables. [Revina2020_it_tickets], en cambio, muestran que los clasificadores simples y explicables construidos con rasgos lingüísticos del dominio son competitivos frente a alternativas más complejas.

Los resultados del presente trabajo —73,5 % de exactitud estricta y un F1 macro de 0,6508 sobre las cuatro clases estimables (0,5207 al incluir la clase de soporte unitario, no estimable)— no admiten una comparación directa con la literatura revisada: los trabajos citados reportan clasificación de etiqueta única, mientras que la evaluación propia se mide contra una referencia multietiqueta sobre cinco sectores canónicos en español rioplatense, tarea considerablemente más exigente. La exactitud laxa (89,5 %) tampoco es comparable con las cifras de etiqueta única y se informa solo como referencia secundaria. Frente al enfoque SVM de [Paramesh2019_it_service_desk] y a la competitividad de los métodos simples de [Revina2020_it_tickets], el esquema propuesto no requiere GPU para inferencia local ni un corpus etiquetado de gran escala, lo que lo hace más accesible para organizaciones medianas, aunque la evidencia no permite ubicar su exactitud frente a la de esos enfoques.

La evidencia de [Revina2020_it_tickets] resulta, en apariencia, contraria al enfoque del presente trabajo, que apuesta por un LLM de propósito general; la tensión, sin embargo, refuerza el análisis: aquellos autores excluyen por diseño las representaciones preentrenadas, al considerar que el vocabulario del dominio podría degradarlas, lo que desaconseja suponer una transferencia no supervisada trivial. Por eso la elección del LLM aquí no se justifica por transferencia pasiva de conocimiento lingüístico, sino por la tarea concreta —clasificación de categoría con contexto instruccional y esquema híbrido de reglas más modelo—, donde el modelo opera como motor de inferencia guiado y no como representación preentrenada sin ajuste.

La literatura de calibración y cascadas (§`subsec:calibracion-cascadas`) permite leer dos resultados. La confianza de la etapa Gemini se concentró en el extremo superior de la escala y no discriminó aciertos de errores en su rango observado (§`subsec:calibracion`), en línea con la sobreconfianza y la concentración en el extremo alto de la escala que [Xiong2024_confidence_elicitation] documentan para la confianza verbalizada, para quienes predecir las fallas sigue siendo un desafío, aunque [Tian2023_verbalized_confidence] muestran que depende de la elicitación. En las cascadas la derivación exige una señal de fiabilidad correlacionada con el acierto y un umbral [Varshney2022_model_cascading, Chen2024_frugalgpt]: el cortocircuito de la etapa determinística la adopta con el puntaje de correctitud, que ordena la correctitud esperada sin ser una probabilidad calibrada, mientras que la revisión humana depende de la confianza verbalizada de Gemini, la señal que esa literatura describe como sobreconfiada. La eficiencia del esquema híbrido frente a una alternativa solo-modelo sigue sin contrastarse (§`subsec:interpretacion-resultados`).

La novedad del aporte radica en la validación específica sobre español rioplatense aplicado a un dominio de mesa de ayuda de organización mediana, segmento escasamente cubierto por la literatura previa. Diversos trabajos han señalado que el ajuste y la evaluación de los LLM se concentran en el inglés y que su rendimiento cae en los idiomas con menos recursos [lai2023okapi, xuan2025mmluprox], y los resultados del presente trabajo (F1 macro = 0,6508 sobre las cuatro clases estimables) sugieren, de forma indirecta y no comparable con las cifras de etiqueta única de la literatura revisada, que el desempeño en español rioplatense resulta inferior al reportado para el inglés, brecha que se atribuye, al menos en parte, al esquema multietiqueta de cinco sectores adoptado en esta evaluación.

### Limitaciones del estudio

El estudio presenta ocho limitaciones que deben considerarse al interpretar los hallazgos y al planificar replicaciones futuras.

Primero, el tamaño de la muestra (\(n = 200\)) basta para una validación piloto pero no para generalizaciones poblacionales sobre el universo de mesas de ayuda en organizaciones medianas. El intervalo de confianza al 95 % de la exactitud estricta, [67,0 %, 79,1 %], queda íntegramente por debajo del umbral del 85 %, por lo que el segundo objetivo específico no se alcanza; muestras mayores, un corpus más equilibrado y una revisión del clasificador serían necesarios para cerrar la brecha.

Segundo, la circunscripción del corpus a una única organización del sector servicios de la provincia de Mendoza restringe la validez externa de los hallazgos. La distribución de tipos de incidentes, el léxico organizacional y los patrones de redacción pueden variar significativamente entre organizaciones, sectores y regiones.

Tercero, la dependencia operativa de un servicio externo de inferencia condiciona el rendimiento del sistema. Un eventual deterioro del servicio de Gemini 3.6 Flash, un cambio significativo en las condiciones comerciales del proveedor, o una modificación en el comportamiento del modelo debido a actualizaciones afectaría directamente la operación. Esta dependencia es intrínseca al enfoque basado en LLM externo y debe ser gestionada como un riesgo operativo.

Cuarto, los resultados reflejan el comportamiento del modelo en su versión vigente durante la campaña automatizada (`gemini-3.6-flash`, integrada al clasificador el 24 de septiembre de 2026; §`fig:cronograma`). Las actualizaciones futuras del proveedor pueden modificar tanto el desempeño bruto como la estructura del prompt requerido para alcanzar resultados equivalentes, lo que aconseja la implementación de un régimen de monitoreo continuo de las métricas de clasificación.

Quinto, la comparación se hizo solo contra el flujo manual, no contra clasificadores alternativos como TF-IDF+SVM o regresión logística sobre el mismo corpus. Un chequeo exploratorio temprano con TF-IDF+SVM sobre un subconjunto no preservado no se reporta como comparación válida: ni la partición ni su tamaño quedaron registrados, de modo que su cifra no es reproducible ni comparable con las métricas de este capítulo; se lo menciona solo como antecedente del diseño, no como evidencia de superioridad del esquema híbrido. Una comparación sistemática contra clasificadores supervisados sobre el corpus completo, con partición y código preservados, queda como trabajo futuro.

Sexto, los analistas que etiquetaron la referencia de la campaña 2026-10 operaron también el brazo manual y uno de ellos es autor del trabajo (§`subsec:poblacion-muestra-corpus`), lo que acota la independencia del *ground truth* de esa campaña y, junto con la falta de registro por caso de la derivación manual, impidió medir sin sesgo la exactitud de ese brazo; la campaña complementaria resolvió esa coincidencia y midió la exactitud del brazo manual con etiquetadores y operadores independientes (§`subsec:resultados-campana-medicion`, §`subsec:balance-neto`).

Séptimo, el vocabulario del filtro determinístico y las reglas de frontera del prompt se ajustaron con errores observados en el mismo corpus de evaluación, de modo que las métricas de clasificación son estimaciones dentro de la muestra. Sin ese vocabulario, la exactitud de la etapa determinística baja de 0,7405 a 0,5270, diferencia que los autores interpretan como cota pesimista del sesgo atribuible a él (interpretación, no medición: los dos valores se calculan sobre conjuntos de casos distintos), y el efecto de las reglas del prompt, acotado por una ablación controlada de dos brazos, es de 50 frente a 46 aciertos sobre los 69 casos de la etapa Gemini (diferencia no significativa; McNemar exacto [McNemar1947_sampling_error], \(p = 0,3438\); `evaluation/report_sensibilidad_ajustes.md`, línea 98) (§`subsec:sensibilidad-ajustes`). Solo un corpus independiente permitiría estimar el desempeño fuera de la muestra, y la campaña complementaria no dispuso de uno (§`subsec:resultados-campana-medicion`).

Octavo, la propia campaña complementaria cuestiona la fiabilidad de la referencia: su doble etiquetado nuevo arrojó un kappa de 0,5569 (moderado; IC [0,4725; 0,6413]; tabla conservada), frente al 0,87 de la campaña 2026-10 (sin intervalo ni tabla), y el consenso nuevo coincide con el sector original en 116 de 138 casos (84,1 %). Las métricas primarias se calculan contra la referencia original y heredan esa incertidumbre (§`subsec:resultados-campana-medicion`).

### Implicancias prácticas

Desde el punto de vista práctico, los resultados sugieren que organizaciones medianas con volúmenes comparables pueden reducir sustancialmente el tiempo de registro con soluciones híbridas similares, con un saldo neto dependiente de la exactitud efectiva (§`subsec:balance-neto`). Automatizar el registro libera al personal técnico para la resolución efectiva de los casos, donde el juicio experto sigue siendo insustituible.

La trazabilidad del registro de cada decisión del clasificador habilita dos procesos de mejora continua: identificar patrones de error sistemáticos y ajustar el filtro determinístico o el prompt; y, con la acumulación sostenida de decisiones validadas por los sectores responsables, constituir un activo informacional que —del orden de 5.000 casos, referencia indicativa, no derivada del corpus ni de un cálculo de potencia— permitiría entrenar modelos específicos del dominio organizacional, con ventajas en costo, latencia y soberanía sobre los datos.

En el plano económico, el costo operativo del sistema se compone de dos rubros principales. El primero es la infraestructura autoalojada: una instancia pública con 2 vCPU y 4 GB de memoria se ofrece a 24 USD/mes, rubro que incluye 4.000 GiB de transferencia saliente y 80 GiB de disco SSD y al que se suman, si se contratan, el respaldo automático (entre el 20 % semanal y el 30 % diario del costo de la instancia) y otros servicios de almacenamiento y direccionamiento; el costo mensual se ubica así en el orden de 24 a 32 USD/mes [DigitalOcean2026_pricing]. (Precio de lista consultado el 19 de octubre de 2026 en https://www.digitalocean.com/pricing/droplets): Droplet Basic de 2 vCPU y 4 GB, 24 USD/mes, con 4.000 GiB de transferencia y 80 GiB de SSD incluidos; el respaldo automático agrega entre el 20 % (semanal) y el 30 % (diario) del costo de la instancia. No se computan volúmenes adicionales, instantáneas ni direcciones IP reservadas. El segundo rubro es el costo de inferencia del LLM. Con el precio introductorio vigente del modelo `gemini-3.6-flash` (0,75 USD por millón de tokens de entrada y 3,75 USD por millón de tokens de salida) [Google2026_gemini_api_pricing], (Precios de lista consultados el 19 de octubre de 2026 en https://ai.google.dev/gemini-api/docs/pricing): Gemini 3.6 Flash, precio introductorio de 0,75/3,75 USD por millón de tokens de entrada/salida vigente hasta el 31 de diciembre de 2026; desde el 1 de enero de 2027 rige el precio estándar de 1,50/7,50 USD por millón de tokens, que duplica la cifra. Equivalen a \(0,7510^-6\) y \(3,7510^-6\) USD por token. y con supuestos explícitos de aproximadamente 800 tokens de entrada (prompt con la descripción de las cinco categorías, un único ejemplo representativo por sector y el incidente) y 30 tokens de salida (JSON estricto con categoría y confianza), cada invocación cuesta del orden de \(710^-4\) USD, entre 0,0006 y 0,0009 USD según el tamaño del prompt. (Cálculo: \(80010^-6)0,75 + 3010^-63,75 710^-4\) USD por invocación; el límite de salida configurado es de 100 tokens y el JSON de respuesta ronda los 15–30 tokens. No se computan reintentos ni la transcripción de voz, que se factura por separado. Para un volumen de 2.646 incidentes trimestrales, con un 34,5 % requiriendo inferencia externa, el costo trimestral de API se sitúa en el orden de 1 USD y en ningún caso por encima de 2 USD, un valor marginal frente a las 32,2 horas-persona brutas liberadas. El costo de la transcripción del canal telefónico queda excluido de este cálculo, porque el modelo (`gemini-3.5-transcribe`) se factura por audio procesado, magnitud que la campaña no registró por caso: el costo reportado corresponde solo a la clasificación.

Un aspecto que excede el alcance técnico pero condiciona la efectividad en operación real es la dimensión organizacional de la adopción. La experiencia de campo indica que los empleados con mayor antigüedad tienden a resistir los cambios de procedimiento, aun con beneficios demostrables, por familiaridad con los procedimientos vigentes y por la percepción —fundada o no— de que el nuevo sistema puede resultar complejo o invasivo. Por eso la puesta en producción se beneficia de un despliegue gradual: un grupo piloto reducido, extensión progresiva a otros sectores y capacitación breve y contextualizada en cada etapa. El enfoque incremental reduce la fricción inicial, ajusta la configuración a cada sector y afianza la confianza de los usuarios finales, condición para que los beneficios cuantificados —reducción del 71,2 % en el tiempo de registro— se traduzcan en mejoras sostenibles.

### Balance neto de la automatización

La proyección de 32,2 horas-persona por trimestre es un ahorro bruto: no descuenta las derivaciones erróneas que el clasificador agrega respecto del flujo manual. Sean \(N = 2.646\) incidentes por trimestre (§`subsec:interpretacion-resultados`), \( t = 43,82\) s el ahorro medio por incidente (§`sec:resultados`), \(e_aut = 0,265\) (53/200) la tasa de error estricta del clasificador, \(e_man\) la tasa de derivación errónea manual (15 % preliminar; §`subsec:planteamiento-problema`) y \(c\) el costo de cada una (10 a 15 minutos, estimación propia; §`subsec:objetivos-especificos`). El balance neto trimestral, en horas-persona, es \(B = (N/3.600)\,[ t - (e_aut - e_man)\,c]\) y la exactitud mínima de equilibrio, \(a^* = 1 - e_man - t/c\), independiente de \(N\).

**Tabla: Exactitud mínima de equilibrio y balance neto trimestral según la tasa de derivación errónea manual y el costo por derivación**

| | **Exactitud mínima \(a^***\) (%) | **Balance neto \(B\) (h-persona)** |
| — | — | — |
| **Tasa manual** | 5 min | 10 min | 15 min | 5 min | 10 min | 15 min |
| 10 % | 75,4 | 82,7 | 85,1 | \(-\)4,2 | \(-\)40,6 | \(-\)76,9 |
| 15 % (preliminar) | 70,4 | 77,7 | 80,1 | +6,9 | \(-\)18,5 | \(-\)43,9 |
| 20 % | 65,4 | 72,7 | 75,1 | +17,9 | +3,5 | \(-\)10,8 |
| 26,5 % (paridad) | 58,9 | 66,2 | 68,6 | +32,2 | +32,2 | +32,2 |

*Fuente:* elaboración propia a partir de \(N = 2.646\), \( t = 43,82\) s y \(e_aut = 53/200\). Tasas y costos son supuestos de sensibilidad, no mediciones. Referencias: exactitud estricta 73,5 % (IC 95 %: [67,0 %; 79,1 %]) y laxa 89,5 % (IC 95 %: [84,5 %; 93,0 %]). Una decimal; con \( t = 43,8\) s dos celdas difieren en 0,1.

Con 15 % y entre 10 y 15 minutos por reasignación, el clasificador agrega unas 304 derivaciones erróneas por trimestre, que cuestan entre 50,7 y 76,1 horas-persona frente a las 32,2 de ahorro: un balance de \(-\)18,5 a \(-\)43,9 horas-persona. El equilibrio tolera entre 7,3 y 4,9 puntos porcentuales de error adicional; el observado es de 11,5. El intervalo de Wilson de la exactitud estricta, [67,0 %; 79,1 %], contiene a \(a^* = 77,7\) % (15 %, 10 minutos), de modo que ni con esos supuestos la muestra fija el signo; con 15 minutos, \(a^* = 80,1\) % lo supera. El umbral del 85 % equivale a la paridad con el 15 % manual, y \(a^*\), que solo acredita el ahorro de registro, es menos exigente. Con la exactitud laxa, que supera los doce valores de \(a^*\), el balance resultaría positivo en todos los escenarios (de +28,9 a +138,1 horas-persona; +42,1, +52,1 y +62,0 en el central); es, sin embargo, la lectura favorable, porque supone que ninguna derivación a un sector válido genera reasignación.

El balance neto es, entonces, condicional al costo con el diseño actual. La campaña 2026-10 no midió la exactitud del brazo manual (sin registro por caso de la derivación del operador y con operadores que fijaron la referencia); la campaña complementaria sí la midió, con etiquetadores y operadores independientes: de su exactitud estricta agregada por derivación (0,8278; 125 de 151) se deriva una tasa de derivación errónea manual \(e_man = 1 - 0,8278 = 0,1722\) (IC [0,1118; 0,2353]), que se ubica entre los escenarios del 15 % y del 20 % de la §`tab:balance-neto` y recalcula \(a^* = 68,2 %\) (5 min), 75,5 % (10 min) y 77,9 % (15 min). El 26,5 % es una cota superior de la tasa operativa, porque el 53,5 % de los casos admite más de un sector. El signo del balance depende del costo \(c\) por derivación errónea, estimación propia (10 a 15 minutos) porque la campaña no cronometra las reasignaciones; por eso el balance se declara *condicional*. Quedan sostenidas la viabilidad técnica (reducción del 71,2 % del tiempo de registro) y la económica (costo monetario marginal); la operativa es condicional a que la exactitud efectiva supere \(a^*\). Cronometrar las reasignaciones es una línea futura (§`subsec:estudios-replicacion`).

### Reflexiones sobre la generalización

La generalización a otras organizaciones requiere tres condiciones: un corpus etiquetado de tamaño y calidad similares, que implica inversión inicial en doble etiquetado y validación del acuerdo inter-evaluador; la viabilidad técnica de desplegar localmente la infraestructura de orquestación y persistencia, que descarta a organizaciones sin capacidades mínimas para administrar contenedores Docker; y un marco normativo compatible con enviar fragmentos descriptivos a un servicio externo de inferencia, que en la Argentina contempla la Ley 25.326 [Ley25326_2000] bajo las condiciones de minimización y disociación de la §`sec:aspectos-legales`.

## Conclusiones

El trabajo desarrollado ha cumplido parcialmente el objetivo general de evaluar la viabilidad y el desempeño de la automatización del registro inicial de incidentes, con el desarrollo y la implementación del sistema como medio: la combinación de N8N como orquestación, FastAPI como núcleo de procesamiento, PostgreSQL como persistencia, Twilio como canal telefónico y Gemini 3.6 Flash como motor de inferencia resultó técnicamente viable, eficiente en el registro y económicamente accesible para organizaciones medianas, con viabilidad operativa condicionada al balance neto (§`subsec:balance-neto`). Ese cumplimiento no se extiende al segundo objetivo específico: la exactitud estricta del 73,5 % y el macro-F1 de umbral (0,6508) quedaron por debajo de las cotas mínimas de 85 % y 0,85 fijadas como criterio de éxito contingente, por lo que ese objetivo no se alcanza. La reducción del tiempo de registro del 71,2 % sí se sostiene como resultado central, con significación estadística (véase la §`sec:resultados`). Por sub-hipótesis, la hipótesis principal se confirma en tiempo de registro, se refuta en el umbral de clasificación y se refuta también en intervención humana sobre el denominador de los casos revisados (25 de 147; 17,0 %); las dos hipótesis subsidiarias no se contrastaron (§`subsec:interpretacion-resultados`).

### Cumplimiento de los objetivos del trabajo

La Tabla `tab:cumplimiento-objetivos` sintetiza el grado de cumplimiento de cada objetivo y la evidencia que lo respalda.

**Tabla: Cumplimiento de los objetivos del trabajo y evidencia de respaldo**

4pt
| **Objetivo** | **Cumplimiento** | **Evidencia** |
| — | — | — |
| Objetivo general: viabilidad y desempeño | Alcanzado parcialmente | Tiempo de registro alcanzado (71,2 %); clasificación por debajo del umbral (objetivo 2); intervención humana refutada sobre los casos revisados (25 de 147, 17,0 %, frente a la cota de 0,15); viabilidad operativa condicionada (§`subsec:balance-neto`) |
| Objetivo específico 1: arquitectura | Alcanzado parcialmente | §`sec:arquitectura`; alta sincrónica con reintentos idempotentes de la configuración entregada (§`subsec:desafios-integracion`) y TLS 1.2/1.3 verificado después de la campaña, en el despliegue de referencia (§`subsec:vision-general`) |
| Objetivo específico 2: clasificador | No alcanzado | Exactitud 73,5 %, IC [67,0 %, 79,1 %]; macro-F1 de umbral 0,6508 (0,5207 con cinco clases, una no estimable) |
| Objetivo específico 3: tres canales | Alcanzado parcialmente | §`subsec:capa-canales`; latencia y exactitud por canal (Tabla `tab:exactitud-etapa-canal`); complejidad percibida no medida |
| Objetivo específico 4: comparación | Alcanzado parcialmente | §`subsec:comparacion-tiempos`; exactitud del brazo manual medida y contrastada frente al automatizado (§`subsec:resultados-campana-medicion`); alcanzado en tiempo y en esa exactitud; intervención humana refutada sobre los casos revisados (25 de 147; el intervalo no excluye 0,15 y la regla del reportante acotó la revisión) |
| Objetivo específico 5: documentación | Alcanzado | §`sec:anexo-repositorio`; §`sec:recomendaciones` |
| Objetivo específico 6: errores/calibración | Alcanzado parcialmente | §`subsec:analisis-errores`; §`subsec:calibracion`; §`subsec:sensibilidad-ajustes`; §`subsec:calibracion-gate`; confianza sin recalibrar; en la muestra |

*Fuente:* elaboración propia.

La arquitectura de cinco capas distribuyó las responsabilidades entre componentes comunicados mediante interfaces REST, y la elección de tecnologías maduras y autoalojadas (Docker, PostgreSQL, N8N) respondió a las restricciones presupuestarias, cambiarias y normativas de las organizaciones medianas argentinas. El primer objetivo específico se alcanza solo parcialmente: la invocación de N8N al servicio de clasificación es sincrónica y la terminación TLS 1.2/1.3 se verificó después de la campaña, en el despliegue de referencia y no en la configuración evaluada ni en la instancia operativa (Tabla `tab:configuracion-evaluada-entregada`).

Sobre esa arquitectura se construyó el clasificador híbrido, cuyo desempeño sobre el corpus real quedó por debajo de las cotas mínimas fijadas en el segundo objetivo específico, por lo que ese objetivo no se alcanza; la brecha se analiza en la §`sec:discusion`. La exactitud estricta, estimada dentro de la muestra, fue de 0,7405 (reglas) y 0,7246 (Gemini); la laxa, del 89,5 %; por canal, de 0,654 a 0,811. La estrategia compositiva —un filtro determinístico de primera etapa y un modelo de lenguaje grande reservado para los casos que el filtro no resuelve— resultó el rasgo más relevante del sistema: el 65,5 % de los casos se resuelve sin inferencia externa y el modelo actúa como árbitro de último recurso (§`subsec:subsistema-clasificacion`); que esa estrategia sea más eficiente que un esquema solo de modelo no se contrastó (§`subsec:interpretacion-resultados`).

Los tres canales quedaron integrados en un único flujo de orquestación. El canal telefónico, cuya transcripción automática del habla representaba el mayor desafío técnico, alcanzó un tiempo de registro medio de 20,1 segundos, que incluye la duración de la llamada grabada y es una cota inferior de la duración real por el tope de 45 s de grabación (§`subsec:metricas-instrumentos`) —un valor que lo posiciona como una vía prácticamente útil. La normalización de la entrada en el propio N8N, antes de invocar al servicio de clasificación, aisló la complejidad de cada protocolo de recepción del núcleo de procesamiento. Estos resultados son compatibles con la hipótesis subsidiaria de integración multicanal, pero no la contrastan: no se midieron la capacidad bajo carga concurrente ni la complejidad percibida, y el tercer objetivo específico se alcanza parcialmente (latencia y exactitud medidas por canal).

La evaluación comparativa entre el flujo manual y el automatizado se presenta en la §`subsec:comparacion-tiempos` y se interpreta, con sus alcances y límites, en la §`subsec:interpretacion-resultados`. En síntesis, el sistema automatizado resultó más rápido que el operador humano en 188 de los 200 pares medidos, con la reducción del tiempo de registro como resultado central. La comparación se completa con la campaña complementaria de medición, que midió la exactitud del brazo manual y la contrastó con la del brazo automatizado y refutó la segunda sub-hipótesis de intervención humana sobre los casos revisados (25 de 147); el brazo manual precedió al automatizado en los 200 casos, de modo que el efecto de orden no se resolvió y solo el efecto de posición fue significativo, para uno de los dos operadores. Con ello el cuarto objetivo específico se alcanza parcialmente, en tiempo y exactitud del brazo manual, y el saldo neto del ahorro de registro frente a las derivaciones erróneas permanece condicional al costo (§`subsec:resultados-campana-medicion`, §`subsec:balance-neto`).

La documentación generada —arquitectura, procedimientos de despliegue, especificación OpenAPI, flujo N8N exportable, análisis tipificado de errores y bandas de confianza— constituye el aporte documental del quinto objetivo específico y sustenta parcialmente el sexto. La tipología de tres patrones de error (descripciones cortas, mezcla de categorías y jerga local) ofrece un punto de partida para replicar o adaptar el sistema y anticipar fallos probables.

### Aportes y generalización

Más allá del cumplimiento de los objetivos específicos, los resultados permiten formular una conclusión acotada a este corpus y al contraste efectivamente realizados: en este corpus de 200 incidentes de mesa de ayuda, en español rioplatense y con cinco categorías canónicas, un modelo de lenguaje grande invocado mediante instrucciones contextualizadas —sin ajuste fino— resultó, dentro de la muestra, una alternativa técnicamente viable para la clasificación de tickets cuando se combina con un filtro determinístico que absorba los casos triviales y reduzca el costo de inferencia. Esta lectura se limita a este dominio: no se realizó una comparación directa contra clasificadores supervisados entrenados sobre el mismo corpus, de modo que no se sostiene aquí una superioridad general de los modelos de lenguaje (véase la §`subsec:limitaciones-estudio`).

Esta combinación arquitectónica —orquestación visual, filtrado determinístico y LLM como árbitro semántico— constituye un patrón de diseño reproducible para la gestión de servicios en organizaciones medianas de América Latina, donde la restricción presupuestaria y la soberanía de datos son determinantes. La arquitectura propuesta no depende de GPU ni de licencias propietarias; su costo monetario, dominado por la infraestructura y no por la inferencia, se cuantifica en la §`subsec:implicancias-practicas`.

El trabajo aporta tres contribuciones que se sostienen más allá del caso particular. La primera es una arquitectura reproducible documentada en todos sus niveles —modelo de datos, contrato REST y flujo de orquestación—, replicable por cualquier equipo con conocimientos básicos de Docker, Python y N8N. La segunda es evidencia empírica, bajo un diseño cuasiexperimental con muestras pareadas, doble etiquetado (de acuerdo moderado, kappa de 0,5569, en la campaña complementaria) y prueba no paramétrica, sobre el desempeño de LLM en un dominio y una variante lingüística escasamente documentados; sus límites de independencia y de fiabilidad de la referencia se declaran en la §`subsec:limitaciones-estudio`. La tercera es un marco de implementación que contempla desde el inicio las restricciones normativas argentinas, sin requerir sortear barreras legales ni asumir riesgos de cumplimiento.

## Recomendaciones y líneas de trabajo futuro

A partir de los resultados, del análisis de errores (§`subsec:analisis-errores`), de la calibración y la intervención humana medidas (§`subsec:calibracion`, §`subsec:reduccion-intervencion`) y de las limitaciones (§`subsec:limitaciones-estudio`), se formulan recomendaciones para la evolución del sistema y para futuras replicaciones, en tres niveles de prioridad. Son prioritarias las que atacan los defectos medidos: la calibración del gate de confianza (§`subsec:calibracion-gate`) y el clasificador supervisado con corpus propio (§`subsec:clasificador-supervisado`). Fortalecen la evidencia o el clasificador la medición de la intervención humana con reportantes identificados (§`subsec:medicion-intervencion`), que la campaña complementaria de medición refutó sobre los casos revisados (§`subsec:reduccion-intervencion`), el aprendizaje activo, la validación independiente, la replicación y los modelos abiertos. Amplían el alcance sin alterar la validez de lo medido las extensiones funcionales: canales, monitoreo, base de conocimientos, agente telefónico, la cola de respaldo del alta y las evoluciones de plataforma anticipadas en las Secciones `sec:arquitectura` y `sec:implementacion` (autenticación única corporativa, SSO; prefijo configurable del número de incidente; migración a Kubernetes).

### Calibración del gate de confianza

Por etapa (§`subsec:calibracion`), el gate de 0,70 solo se evalúa sobre la salida de Gemini, la etapa de reserva deriva siempre a revisión y la etapa determinística no deriva por su confianza y se rige por su puntaje de correctitud (§`subsec:subsistema-clasificacion`) y la confianza autodeclarada de Gemini, concentrada entre 0,85 y 1,00, no discrimina aciertos de errores, por lo que el gate no derivó ningún caso. Se propone, sobre un conjunto de validación propio, disjunto del corpus de evaluación: (i) incorporar señales independientes del puntaje —ambigüedad léxica entre categorías, margen entre las dos primeras categorías (que exige ampliar el contrato de salida, §`anexo:H`), desacuerdo entre etapas y revisión por muestreo de casos de alta confianza (§`subsec:human-in-the-loop`)—; (ii) recalibrar el puntaje por regresión isotónica [NiculescuMizil2005_probabilities], o por escalado de temperatura [Guo2017_calibration] si se obtienen puntajes por categoría, advirtiendo que una recalibración monótona corrige el nivel de la confianza verbalizada, sobreconfiada y dependiente de la elicitación [Xiong2024_confidence_elicitation, Tian2023_verbalized_confidence], pero no crea capacidad de discriminación; y (iii) derivar el umbral de una curva cobertura-precisión con ajuste fuera de la muestra, como el punto de operación de la etapa determinística, cuya ventaja frente a Gemini depende del vocabulario (§`subsec:sensibilidad-ajustes`), con un piso declarado antes de observarla (la exactitud de la revisión humana o el 85 % del segundo objetivo), y confirmarlo en un corpus independiente (§`subsec:corpus-independiente`). La misma campaña permitiría contrastar los parámetros de inferencia, sin optimización documentada (§`subsec:capa-procesamiento`).

### Incorporación de un clasificador supervisado con corpus propio

Se sugiere incorporar progresivamente un clasificador supervisado entrenado con el corpus etiquetado generado por el propio sistema durante su operación. La acumulación sostenida de decisiones validadas por los sectores responsables constituye un activo informacional valioso que, una vez alcanzado un volumen del orden de magnitud indicado en la §`subsec:implicancias-practicas`, permitiría entrenar modelos de clasificación específicos del dominio organizacional. Las ventajas potenciales de esta migración incluyen: reducción del costo marginal por incidente clasificado al eliminar la dependencia del servicio externo de inferencia, disminución de la latencia al ejecutar la inferencia localmente, y ganancia de soberanía sobre los datos al evitar la transferencia internacional de fragmentos textuales. La disponibilidad de modelos de pesos abiertos, como Llama 2 [Touvron2023_llama2], abre una vía hacia un sistema completamente autoalojado; sin embargo, en clasificación de tickets con muchas clases los modelos tipo BERT superaron a LLM abiertos como Llama y Mistral [paket2024itservice], por lo que esa vía debería evaluarse con modelos ajustados al dominio y no solo mediante *prompts*.

### Medición continua de la intervención humana en operación

La campaña complementaria refutó la segunda sub-hipótesis sobre los casos revisados: sus 147 intervenciones corresponden a la derivación por reportante no identificado y no a la confianza, y de los 147 casos que tuvieron revisión humana (66 de correo y 81 de telefonía) 25 cambiaron la derivación (17,0 %; IC [11,8 %, 23,9 %]; §`subsec:reduccion-intervencion`). La tasa bruta del 73,5 % mide la configuración de la prueba y no un defecto del clasificador. Se recomienda repetir la medición con reportantes identificados en el directorio y evaluar entonces el refinamiento del clasificador y del gate —mediante las señales independientes del puntaje y la recalibración de la §`subsec:calibracion-gate`— contra la proporción de intervenciones que cambian la derivación. Dos requisitos acotan esa medición futura: que la revisión alcance a todos los canales, o a una muestra aleatoria de cada uno, de modo que el denominador sea el de los casos revisables, y que cada validación se coteje con una referencia independiente, para medir cuántas veces la revisión acierta y no solo cuántas cambia. Para vigilarla se propone registrar, en operación y para cada caso, la ocurrencia y el origen de la intervención (derivación por el gate, revisión por muestreo, corrección o rederivación por el sector receptor, completado manual de datos), una consigna de tiempo de inicio y de fin, el resultado (categoría confirmada o corregida) y el operador, pseudonimizado. El registro ampliaría `clasificacion_log`, que hoy guarda el indicador de revisión y la categoría validada, o se llevaría en una tabla dedicada vinculada al incidente, preferible cuando un incidente acumula varias intervenciones. La definición operacional seguiría las dos formas rotuladas de la §`tab:variables` —proporción de casos y proporción del tiempo del proceso— y se aplicaría de igual modo en ambos brazos. El mismo registro mediría las derivaciones erróneas y su costo en tiempo, insumos del balance neto (§`subsec:balance-neto`).

### Cola de respaldo y alta asincrónica

La invocación de alta es sincrónica. Una evolución de mayor alcance la desacopla mediante un patrón *outbox* o un intermediario de mensajes con reproceso, de modo que el alta se persista de forma diferida. Esa línea tensiona la respuesta sincrónica que el formulario web consume para informar el número de incidente y la medición de los tiempos de ingreso y persistencia (§`subsec:desafios-integracion`) sobre la que se apoyan los resultados del Capítulo `sec:resultados`, y exigiría reintroducir la infraestructura de mensajería que el stack retiró (§`sec:arquitectura`); se propone como trabajo futuro y no altera lo medido.

### Ampliación de canales de entrada

Se propone ampliar el conjunto de canales de entrada para incluir mensajería corporativa instantánea, particularmente Slack y Microsoft Teams en aquellas organizaciones donde estas plataformas constituyen el canal de comunicación dominante. La inclusión de aplicaciones móviles propias para usuarios de campo constituye una extensión natural que atiende la demanda creciente de canales asincrónicos integrados al ecosistema laboral cotidiano. La arquitectura modular propuesta en la §`sec:arquitectura` facilita esta ampliación: cada nuevo canal requiere únicamente un disparador adicional en N8N, sin modificaciones en las capas de procesamiento ni de persistencia.

### Panel de monitoreo en tiempo real

El sistema incorpora un dashboard de analítica basado en ReCharts que permite visualizar tendencias históricas, distribución por sector y desglose por estado (véase §`subsec:dashboard-analitica`). Como evolución de esta capacidad, se sugiere implementar una capa de monitoreo en tiempo real sustentada sobre tecnologías de observabilidad maduras, tales como Prometheus para la captura de métricas y Grafana para la visualización. Esta capa permitiría supervisar la latencia del sistema, la tasa de aciertos del clasificador, la distribución de carga entre sectores y el costo agregado de las invocaciones al modelo externo, habilitando alertas tempranas frente a degradaciones del servicio. La existencia de endpoints de salud (`GET /api/v1/health`) en cada componente del sistema proporciona los puntos de datos necesarios para instrumentar esta capa de observabilidad.

Más allá del monitoreo operativo, los datos acumulados de incidentes constituyen una fuente de inteligencia organizacional: su registro sistemático habilita flujos ETL (*Extract, Transform, Load*) que permiten identificar patrones recurrentes de fallas, detectar áreas con mayor demanda de soporte y generar indicadores trimestrales que orienten decisiones estratégicas de inversión.

### Integración con sistemas externos de inventario de activos y gestión de configuración

La clasificación automática operada por el sistema se sostiene en el contenido textual del incidente y en el catálogo de sectores, sin consultar fuentes externas de verdad operativa. Una extensión de alcance consistente con la base de conocimientos (§`subsec:base-conocimientos`) consiste en integrar el flujo con un sistema de inventario de activos o con una base de datos de gestión de configuración (*CMDB*), de modo que la derivación pueda contrastarse con la titularidad registrada de los equipos, las aplicaciones y los servicios afectados. Esa integración permitiría verificar la coherencia entre el sector sugerido y la responsabilidad formal del activo, enriquecer la derivación con el historial de cambios de configuración y acotar los casos que un operador debe determinar manualmente. Su adopción exige acuerdos de interoperabilidad con los sistemas corporativos y una definición previa del modelo de activos, por lo que se plantea como trabajo futuro y no modifica la validez de lo medido.

### Mecanismos de aprendizaje activo

Se propone incorporar mecanismos de aprendizaje activo (*active learning*; §`subsec:human-in-the-loop`) que seleccionen los casos para revisión y reentrenamiento mediante las señales independientes del puntaje de la §`subsec:calibracion-gate`: ambigüedad léxica, margen entre categorías, desacuerdo entre etapas y muestreo de casos de alta confianza. La confianza declarada solo se usaría como criterio de prioridad una vez recalibrada y validada según esa subsección, porque en el rango observado de Gemini no discrimina aciertos de errores y la etapa determinística no emite una confianza utilizable. Las revisiones que alimenten el ajuste incremental serían las registradas según la §`subsec:medicion-intervencion`, de modo que cada intervención mejore al clasificador con un costo operativo controlado.

### Validación sobre un corpus independiente

El clasificador evaluado se ajustó, en parte, con el mismo corpus sobre el que se reportan las métricas de clasificación (vocabulario del filtro determinístico y reglas de frontera del prompt), de modo que esas métricas son estimaciones dentro de la muestra. La confirmación del desempeño fuera de la muestra exige construir un corpus independiente, etiquetado con el mismo protocolo y sin solapamiento con el corpus de evaluación, y reportar sobre él las métricas de la etapa determinística y de la etapa semántica. Esa validación no se realizó en este trabajo porque no se dispuso de un corpus de preproducción con esas características. La campaña complementaria de medición tampoco obtuvo un corpus independiente declarado, de modo que esta validación continúa pendiente (§`subsec:resultados-campana-medicion`).

### Estudios de replicación

Se sugiere realizar estudios de replicación en organizaciones de distinto tamaño, sector y región geográfica, para fortalecer la validez externa de los hallazgos y reunir evidencia empírica sobre soluciones similares en contextos heterogéneos. Serían relevantes las réplicas en organizaciones del sector público (con más incidentes de sistemas administrativos), del sector industrial (con más incidentes de infraestructura física) y de mayor tamaño, donde el volumen diario supere las 100 unidades. La exactitud del flujo manual sobre el mismo corpus ya se midió en la campaña complementaria de medición, con etiquetadores distintos de los operadores del brazo manual (§`subsec:resultados-campana-medicion`); toda replicación debería conservar ese criterio de independencia y, además, cronometrar las reasignaciones, que el análisis de esa campaña no registró (§`subsec:balance-neto`). Convendría, asimismo, una asignación muestral no proporcional que sobremuestree las clases minoritarias —como Bases de Datos, con un solo caso— y pondere las estimaciones globales por la distribución del universo (§`subsec:poblacion-muestra-corpus`).

### Evaluación de modelos de lenguaje de código abierto

Se propone evaluar la integración de modelos de lenguaje de código abierto desplegados localmente —tales como Llama 3, Mistral o Qwen— como alternativa al modelo externo Gemini 3.6 Flash. Esta evaluación permitiría cuantificar el costo en exactitud frente a la ganancia en soberanía de datos, la eliminación de la dependencia de un proveedor único y la reducción de costos operativos a largo plazo. La realización de un benchmark comparativo sobre el mismo corpus de 200 casos constituiría una contribución adicional significativa al estado del arte.

### Base de conocimientos para resolución automática

El sistema se concentra en la clasificación y derivación de incidentes hacia los sectores responsables, pero no aborda la resolución de los casos que admiten soluciones estandarizadas y repetibles. Se recomienda incorporar una base de conocimientos, un repositorio estructurado de soluciones verificadas que, tras la clasificación inicial, permita proponer los pasos de resolución cuando el incidente coincida con un patrón documentado y validado. Ese autoservicio absorbería los casos simples y repetitivos —reinicios de sesión, restablecimiento de contraseñas o configuraciones básicas de correo electrónico— y reduciría la carga de los sectores de soporte.

Su construcción puede articularse con el aprendizaje activo (§`subsec:aprendizaje-activo`): cada caso resuelto por un operador y validado como correcto sería candidato a incorporarse, previa curación editorial. La viabilidad técnica se apoya en la capacidad de los modelos de lenguaje para generar respuestas estructuradas a partir de documentación técnica, línea que conecta con la evaluación de modelos de código abierto (§`subsec:evaluacion-modelos-abiertos`).

### Automatización de la etapa de resolución técnica

La presente investigación abarca la recepción, la clasificación y el registro inicial de incidentes, y deja la resolución técnica bajo responsabilidad del personal humano (§`subsec:alcance-delimitaciones`). Una línea de trabajo posterior consiste en extender la automatización a esa etapa, articulando la base de conocimientos (§`subsec:base-conocimientos`) con los procedimientos operativos de cada sector para proponer pasos de resolución verificados y, eventualmente, ejecutar acciones de bajo riesgo sobre los sistemas afectados. Su factibilidad y su alcance dependen de la disponibilidad de procedimientos estandarizados, de la integración con las herramientas de gestión del inventario de activos (§`subsec:integracion-inventario`) y del nivel de supervisión humana que la organización considere admisible; la resolución de los casos complejos permanecería bajo juicio experto. Se propone como línea de trabajo futuro que trasciende el alcance de esta investigación.

### Agente conversacional telefónico en tiempo real

Se propone, como evolución de mayor alcance del canal telefónico, reemplazar la captura de toma única —una grabación de hasta 45 segundos que se transcribe de forma diferida— por un agente que dialogue en tiempo real. Sobre Twilio Media Streams, que habilita el envío bidireccional del audio mediante WebSocket, podría formular preguntas de aclaración, comunicar el número de incidente asignado y cerrar la llamada, lo que elevaría la calidad de la captura en línea con el tercer objetivo específico.

Su adopción estuvo condicionada por la madurez de las interfaces de audio bidireccional, entonces en vista previa (*preview*) y sujetas a cambios, y exige infraestructura no contemplada: un punto de entrada WebSocket con *upgrade* en el proxy inverso, la transcodificación del audio (mu-law, 8 kHz) al formato del modelo (PCM, 16 kHz), la gestión de turnos de habla y un modelo de costo por minuto de transmisión, no por grabación. Se recomienda una prueba de concepto acotada que conserve la grabación y transcripción actuales como modo degradado de respaldo.

=3em

## Diagrama de arquitectura del sistema

El Anexo A inventaría los diagramas de la arquitectura del sistema entregado (release `v1.2.16`). Los diagramas de arquitectura y despliegue se incluyen como figuras de la §`sec:arquitectura` y no se reproducen aquí; los diagramas de secuencia, componentes y cronograma se reproducen a continuación. Los cinco artefactos son:

 - **Diagrama de arquitectura del sistema** (Figura `fig:arquitectura`, §`sec:arquitectura`): las cinco capas de la Tabla `tab:capas` y los tres canales de entrada (correo, formulario web y telefonía), sin versiones de bibliotecas, que constan en la Tabla `tab:capas` y en la §`tab:configuracion-evaluada-entregada`. Fuente versionada: docs/diagrams/arquitectura_sistema.md.
 - **Diagrama de despliegue** (Figura `fig:despliegue`, §`sec:arquitectura`): los cinco componentes principales (N8N, FastAPI, PostgreSQL, Gemini 3.6 Flash, Twilio), el proxy inverso Nginx, que provee terminación TLS 1.2/1.3 verificada en el despliegue de referencia y que forma parte del stack base sobre el que corrió la ingesta del 2 de octubre (la medición telefónica del 5 y 6 de octubre usó el perfil aislado `corpus`, sin proxy), y las relaciones de comunicación entre ellos. Fuente versionada: docs/diagrams/despliegue.md.
 - **Diagrama de secuencia** (Figura `fig:secuencia`): flujo extremo a extremo de un incidente desde su recepción en cualquiera de los tres canales (correo electrónico, formulario web o telefonía) hasta la confirmación al usuario o la derivación a revisión humana, incluyendo las interacciones con el clasificador híbrido y la base de datos. Fuente versionada: docs/diagrams/secuencia.md.
 - **Diagrama de componentes** (Figura `fig:componentes`): organización interna del módulo Python por capas (routes, services, repositories, models, classifiers), con sus dependencias y relaciones. Fuente versionada: docs/diagrams/componentes.md.
 - **Cronograma** (Figura `fig:cronograma`, §`subsec:conexion-scrumban`): construcción, campañas de medición de la campaña 2026-10, campaña complementaria de medición y versión del modelo evaluada, con la procedencia de cada fecha. Fuente versionada: docs/diagrams/cronograma.md.

Los diagramas se generan a partir de fuentes Mermaid versionadas en formato `.md` en el directorio `docs/diagrams/` del repositorio y se renderizan a imágenes PNG para su inclusión en el documento [Gomez2026_repositorio].

[Figura: Diagrama de secuencia del flujo extremo a extremo de un incidente, desde el canal de entrada hasta la confirmación o la derivación a revisión humana, en la configuración entregada (release `v1.2.16] (`fig:secuencia`)

[Figura: Diagrama de componentes del módulo Python organizado en capas (routes, services, repositories, classifiers). Describe la configuración entregada (release v1.2.16] (`fig:componentes`)

[Figura: Cronograma de la construcción, las campañas y la versión del modelo (barras con precisión de mes; hitos, de día). Fuente: historial del repositorio para los hitos, incluido el recálculo del tiempo telefónico del 19-10-2026 (c-77); las fechas de la corrida telefónica (el 5 y 6 de octubre de 2026) provienen de la respuesta de los autores del 2026-10-28, y la confirmación del 9-10-2026 cubre las ventanas de las campañas. La campaña complementaria de medición (programa c-165 a c-168) corrió en noviembre de 2026; su plan pre-registrado se versionó el 2026-11-01 y sus tablas primarias y análisis, entre el 2026-11-04 y el 2026-11-08.] (`fig:cronograma`)

## Repositorio de código fuente

El código fuente del módulo Python, los scripts de migración de la base de datos PostgreSQL gestionados mediante Alembic, los archivos de configuración del despliegue en contenedores Docker y los flujos de integración continua sobre GitHub Actions se encuentran disponibles en el repositorio público del proyecto [Gomez2026_repositorio`, accesible en https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N]. El commit de referencia para la versión entregada al jurado se identifica con el tag anotado `v1.2.16`, creado sobre el commit que fija el contenido de la versión entregada. Como un commit no puede contener su propio hash, la rama principal registra después un commit que solo consigna ese hash, y los commits posteriores no modifican las fuentes de la tesis.

El hash completo de ese commit es ` f72e6c899ba3bce7ae11ffe1b0a980f57241a0ea`, que constituye la referencia verificable de la versión corregida.

La verificación de la compilación se conserva en paper/compilacion.md, que registra las páginas, los errores y el SHA-256 del PDF, y la de la matriz de trazabilidad de las correcciones, en docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py; ambos artefactos corresponden a este anexo de repositorio.

La versión entregada no es la que se evaluó. La *configuración evaluada* es la del commit `d6bb474` (7-10-2026), primera revisión que versiona la cascada `hybrid-v3`; las corridas de tiempos usaron revisiones anteriores con las mismas dependencias (§`subsec:protocolo-pruebas`). La *configuración entregada* es la del tag `v1.2.16`. La *configuración de la campaña complementaria* no es un único commit: el brazo automatizado de correo y formulario web corrió desde `cda7712` (5-11-2026), el de telefonía el 6-11-2026 tras `c-174` y `c-175`, y las intervenciones se validaron entre el 7 y el 8-11-2026 (`c-177` a `c-183`), todas con `hybrid-v3`, la instrumentación de `c-165` y la derivación por reportante activas (§`subsec:resultados-campana-medicion`). La §`tab:configuracion-evaluada-entregada` consigna, con valores verificados sobre las tres revisiones, lo que cambió; los pasajes de la tesis que citan versiones o capacidades remiten a ella.

**Tabla: Configuración evaluada, configuración entregada y configuración de la campaña complementaria**

4pt
| Elemento | Configuración evaluada (`d6bb474`) | Configuración entregada (`v1.2.16`) | Campaña complementaria |
| — | — | — | — |
| FastAPI y Uvicorn | 0.115.0 y 0.30.6 | 0.162.0 y 0.54.0 | Como la entregada |
| SQLAlchemy | 2.0.36 | 2.1.6 | Como la entregada |
| `google-genai` | `>=2.20.0` | `>=2.33.0,<3` | Como la entregada |
| pytest y pytest-cov | 8.3.3 y 5.0.0 | 9.1.1 y 7.1.0 | Como la entregada |
| React | 18.3.1 | 19.3.1 | Como la entregada |
| Flujo N8N | 28 nodos (25 operativos y 3 notas); 38 (35 y 3) hasta c-72 | 32 nodos (29 operativos y 3 notas) | Como la entregada |
| Reintentos del alta | No | Sí: hasta 3 intentos, espera fija de 5000 ms y tiempo de espera por intento de 10 s (inicio de sesión) y 75 s (alta) | Como la entregada |
| Revisión por reportante no identificado | No | Sí (c-82) | Sí (c-82) |
| Propagación del contacto del reportante en el POST | No | Sí (c-162, posterior a la campaña 2026-10): el flujo N8N envía `reportante_email` (correo) y `reportante_telefono` (telefonía), que habilitan la resolución del reportante de c-82 | Sí (c-162) |
| Prueba de humo E2E y verificación de TLS | No | Sí (c-140) | No registrado |
| Instrumentación de intervención | No | Sí (c-165) | Sí (c-165; parte de las de `O1` con un *frontend* previo) |
| Imagen de N8N | `n8nio/n8n:2.11.2` | Derivada de `n8nio/n8n:2.11.2` (`docker/n8n/Dockerfile`) con parche de la decodificación IMAP (c-182) | `n8nio/n8n:2.11.2`; la derivada es posterior (7-11-2026) |
| `classifier_``version` | `hybrid-v3` | `hybrid-v3` | `hybrid-v3` |
| Modelo de transcripción | `gemini-3.5-``transcribe` | `gemini-3.5-``transcribe` | Como la entregada |
| Sin cambios | Python 3.12-slim, PostgreSQL 15.5-alpine, `gemini-3.6-flash` con sus parámetros, umbrales (0,5166 y 0,70), vocabulario y *prompt*; la lógica del clasificador solo cambió en comentarios e importaciones diferidas | Sin cambios |

*Fuente:* elaboración propia a partir de `git show d6bb474:`*archivo*, `git show v1.2.16:`*archivo* y `git show d6bb474:App/Backend/app/constants.py` sobre `requirements.txt`, `package-lock.json`, `n8n/workflow.json`, `docker-compose.yml` y `settings.py`, y de los changes archivados, y de `git diff –stat cda7712 v1.2.16 – App/ n8n/ docker/ docker-compose.yml` (24 archivos; no cambian `requirements.txt`, `package-lock.json`, `n8n/workflow.json` ni `settings.py`; cambian `docker-compose.yml` y `docker/n8n/`, por la imagen derivada de N8N, y archivos del backend y del frontend que no intervienen en la clasificación). La campaña complementaria usó `hybrid-v3` sobre un *backend* posterior, con c-82 y c-162 activos; *no registrado* señala lo que los artefactos no permiten recuperar.

La estructura del repositorio separa el módulo de procesamiento (`App/Backend/`, con la aplicación FastAPI, las migraciones Alembic y las pruebas), la interfaz de usuario (`App/Frontend/`, React con TypeScript), la definición del flujo de orquestación (`n8n/workflow.json`), los artefactos de evaluación (`evaluation/`), el corpus pseudonimizado (`data/`), los scripts auxiliares (`scripts/`) y la documentación (`docs/`), junto con las especificaciones de los changes (`openspec/`) y los archivos de orquestación local `docker-compose.yml` y `Makefile`. El archivo `README.md` describe esta organización y reúne las instrucciones detalladas para el despliegue local en menos de 15 minutos, por lo que constituye el punto de entrada al código fuente disponible en el repositorio público [Gomez2026_repositorio].

## Esquema de base de datos

El esquema completo de la base de datos PostgreSQL se documenta mediante scripts SQL versionados que definen las siete entidades descritas en la Tabla `tab:entidades` de la §`sec:arquitectura`, las restricciones de integridad referencial (claves foráneas con eliminación en cascada condicional), los índices secundarios sobre los atributos de búsqueda frecuente (fecha de creación, sector responsable y estado actual del ticket), y la generación de los identificadores de incidente. La capa de acceso a datos del módulo utiliza SQLAlchemy 2.0 como mapeador objeto-relacional y `asyncpg` como driver asincrónico para PostgreSQL, en coherencia con la Sección 5.4 y con el código del repositorio. Las migraciones incrementales se gestionan mediante Alembic, lo que permite reproducir el estado de la base en cualquier punto histórico del desarrollo y revertir cambios cuando resulte necesario.

La migración inicial incluye la creación de las tablas de catálogo (`sector`, `estado`, `canal_``origen`) con sus valores semilla, garantizando que un despliegue nuevo del sistema comience con los datos de referencia correctos. Las migraciones subsiguientes documentan la evolución del esquema durante las etapas de desarrollo descritas en la §`sec:marco-metodologico`.

El diagrama entidad-relación de las siete entidades se incluye como Figura `fig:er_modelo_datos` de la §`sec:arquitectura`; su fuente Mermaid versionada reside en `docs/diagrams/er_modelo_datos.md`.

## Especificación OpenAPI de la interfaz REST

La especificación completa de la interfaz REST se genera automáticamente mediante FastAPI conforme a la versión 3.1 de la especificación OpenAPI [Tiangolo2024_fastapi]. El documento resultante describe los puntos de entrada listados en la Tabla `tab:api` de la §`sec:arquitectura`, los esquemas de los cuerpos de solicitud y respuesta validados mediante Pydantic v2, los códigos de estado posibles para cada método HTTP, y ejemplos representativos para cada caso de uso.

La interfaz se encuentra disponible adicionalmente en formato interactivo a través del componente Swagger UI integrado en el servidor, accesible bajo la ruta `/docs` durante la ejecución, y en formato estático como archivo `openapi.json` en el directorio `docs/` del repositorio. La sincronización entre el código y la especificación estática se verifica automáticamente en el pipeline de integración continua.

La especificación OpenAPI vigente describe 33 puntos de entrada que exponen 41 métodos HTTP y 44 esquemas de datos, agrupados por recurso: autenticación, catálogos, clasificaciones, incidentes, directorio, estadísticas, telefonía, control de costo y salud.

A título ilustrativo, los 44 esquemas de datos comprenden las estructuras de los catálogos, las entidades de dominio y los objetos de respuesta de cada recurso. El esquema `IncidenteRead`, por ejemplo, expone el identificador del ticket, la descripción pseudonimizada, la prioridad, el sector y los sectores adicionales, el estado, el canal de origen, el reportante, las marcas temporales de ingreso y persistencia, y los indicadores de latencia end-to-end y de latencia anómala, con sus tipos y campos de solo lectura. El detalle exhaustivo de atributos, tipos y ejemplos reside en `docs/openapi.json`.

## Configuración del flujo N8N

La exportación del flujo de orquestación en formato JSON incluye la totalidad de los 32 nodos configurados, sus parámetros operativos, las credenciales referenciadas mediante identificadores opacos sin exposición de valores, y los conectores entre nodos. El archivo `n8n/workflow.json` contiene esta exportación. La importación de este artefacto en una instancia limpia de N8N 2.11.2 reproduce íntegramente el comportamiento operativo del sistema, sujeta únicamente a la provisión de las credenciales correspondientes a los servicios externos integrados (servidor IMAP de correo, cuenta Twilio y clave de API de Gemini) mediante el sistema de credenciales nativo de la plataforma.

La Figura `fig:anexo_flujo_n8n` presenta una reconstrucción esquemática del flujo, derivada de la exportación JSON y agrupada por etapa funcional. Los 29 nodos operativos (más 3 notas adhesivas, 32 nodos en total) se organizan en siete etapas: entrada (triggers), con la recepción de correo por IMAP y los disparadores de telefonía, formulario web y notificación de clasificación; validación y normalización de la información de entrada, incluida la marca de canal y el sellado de ingreso; envío al backend, con la autenticación del operador y la solicitud POST del incidente; ruteo por canal de origen; revisión humana, con la notificación al operador designado y las respuestas de handoff; respuesta y auditoría del ticket; y aviso post-revisión. La parametrización completa de cada nodo reside en `n8n/workflow.json`.

[Figura: Reconstrucción esquemática del flujo de orquestación N8N: no es una captura de la interfaz; los 29 nodos operativos se agrupan por etapa funcional.] (`fig:anexo_flujo_n8n`)

## Corpus de validación

El corpus de 200 incidentes utilizado para la validación experimental reside en el repositorio en formato JSON, en su forma pseudonimizada y versionada, bajo la ruta data/corpus_evaluacion_pseudonimizado.json. Cada caso incluye el identificador anónimo, la descripción cruda pseudonimizada, el canal de origen, el sector asignado por consenso humano, los sectores adicionales de verdad y el tiempo de registro medido en cada flujo. La categoría predicha por el clasificador y la confianza asociada no forman parte del corpus: se conservan en la copia versionada de la caché, evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json. Los tiempos automatizados constan por caso en el corpus; sus registros primarios (base operativa del 2-10-2026 con los incidentes ingresados, respaldo del 9-10-2026 de los 81 ingresos telefónicos y ejecuciones de N8N) no se conservan en el repositorio. Se incluyen además las planillas de cronometraje del flujo manual.

Cada uno de los 200 casos del corpus se compone de siete campos: `id` (identificador anónimo, por ejemplo `R001`), `descripcion` (texto pseudonimizado, con los identificadores personales reemplazados por etiquetas genéricas como `[EMAIL]`, `[TELEFONO]`, `[HOST]` y `[PERSONA]`), `canal_origen` (correo electrónico, formulario web o llamada telefónica), `sector_asignado` (sector principal de verdad, exactamente uno de los cinco sectores canónicos), `sectores_adicionales` (sectores de verdad complementarios, sin repetir el asignado), `tiempo_manual_s` (tiempo de clasificación manual, en segundos) y `tiempo_automatizado_s` (tiempo del sistema automatizado, en segundos). El corpus completo reside en data/corpus_evaluacion_pseudonimizado.json y las predicciones del clasificador en evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json.

Por razones de privacidad y en cumplimiento de la Ley 25.326 [Ley25326_2000], las descripciones textuales han sido pseudonimizadas previamente a su inclusión en el repositorio público, reemplazando nombres propios, direcciones de correo y otros identificadores personales por etiquetas genéricas.

## Documentación operativa

La documentación operativa del sistema, que reúne los procedimientos de despliegue, configuración, respaldo y restauración, monitoreo y respuesta ante incidentes operativos, se versiona en el repositorio junto con el código fuente; el runbook operativo reside en `docs/operational-guide.md`, y el procedimiento de la prueba de humo y de la verificación del borde TLS del despliegue de referencia, en `docs/runbook-smoke-stack-referencia.md`.

## Especificación del prompt de Gemini 3.6 Flash

Este anexo documenta la especificación del prompt enviado al modelo `gemini-3.6-flash` (Gemini 3.6 Flash en el texto) y los parámetros de configuración de la inferencia. El prompt se mantiene en el repositorio bajo `docs/prompt_gemini.txt` y es único para los tres canales de entrada. El canal telefónico emplea además el modelo de transcripción `gemini-3.5-transcribe`, declarado en la configuración del backend (`settings.py`) y excluido del cálculo económico (§`subsec:implicancias-practicas`).

### Estructura y contenido del prompt

El prompt sigue una estructura fija en español organizada en cinco componentes funcionales y un conjunto de reglas de desambiguación:

 - **Instrucción de rol**: define que el modelo actúa como agente especializado en clasificación de incidentes técnicos en español rioplatense, lo que ancla el comportamiento en el dominio y el dialecto del estudio.
 - **Definición de categorías**: presenta los cinco sectores canónicos con sus *strings* exactos (sensibles a mayúsculas y sin tildes), un ámbito descriptivo por sector y un único ejemplo representativo extraído del dominio real por clase (cinco en total).
 - **Formato de respuesta**: solicita un JSON válido con exactamente dos campos, `categoría` (uno de los cinco valores canónicos) y `confianza` (número entre 0,0 y 1,0), sin texto adicional, comentarios ni explicaciones.
 - **Lógica de decisión**: indica analizar la descripción y asignar una categoría única entre las cinco opciones; ante elementos de múltiples categorías, elegir la dominante.
 - **Validación sintáctica**: exige validar la corrección sintáctica del JSON antes de devolverlo y reducir la confianza cuando no sea posible clasificar con seguridad.
 - **Reglas de desambiguación de frontera**: las acciones sobre aplicaciones o sistemas operativos (acceder, iniciar sesión, abrir una aplicación) se orientan a `Soporte Tecnico Software`; los dispositivos físicos y su digitalización (escáner, impresora, periférico, error de digitalización) a `Soporte Tecnico Hardware`; y la infraestructura y los servicios de plataforma (servidor, red, SMTP, VM) a `Sistemas`. Estas reglas corrigen casos de frontera medidos sobre el corpus.

### Parámetros de configuración

La invocación del modelo se realiza mediante el SDK `google-genai` (`>=2.20.0`, configuración evaluada; Tabla `tab:configuracion-evaluada-entregada`), con los hiperparámetros que resume la Tabla `tab:anexo_gemini_params`, que corresponden a la configuración adoptada para el despliegue y no al resultado de una calibración documentada frente a valores alternativos (§`subsec:capa-procesamiento`).

**Tabla: Parámetros de configuración de la inferencia con `gemini-3.6-flash**

.`

| Parámetro | Valor | Justificación |
| — | — | — |
| `temperature` | 0,3 | Valor bajo que reduce la variabilidad de la generación y mejora la consistencia en tareas de clasificación determinística. |
| `top_p` | 0,9 | *Nucleus sampling* que admite variantes léxicas válidas en español rioplatense sin sacrificar coherencia. |
| `max_tokens` | 100 | Límite suficiente para la respuesta JSON, con margen ante variaciones y sin truncamiento. |
| `candidate_count` | 1 | Respuesta única sin remuestreo, que acota la latencia del procesamiento en tiempo real. |
| `safety_settings` | Cuatro categorías con umbral `BLOCK_NONE` | Desactiva los cuatro filtros de contenido (`HARM_CATEGORY_HARASSMENT`, `HARM_CATEGORY_HATE_SPEECH`, `HARM_CATEGORY_SEXUALLY_EXPLICIT` y `HARM_CATEGORY_DANGEROUS_CONTENT`, todos con umbral `BLOCK_NONE`) para no rechazar descripciones legítimas de incidentes; no se configura ningún filtro de umbral intermedio. |
| `timeout` | 30 segundos por intento; 60 segundos en total | Límite de latencia por intento del backend al modelo (hasta dos reintentos ante fallas transitorias, dentro de un presupuesto total de 60 segundos por clasificación; no son reintentos de N8N al backend); al agotarse, el clasificador devuelve confianza 0,0 y marca el caso para revisión humana. |
| Umbral de revisión humana | 0,70 | Confianza mínima de una respuesta del modelo para no marcarla para revisión; se evalúa solo sobre la salida de Gemini (la reserva deriva siempre y la etapa determinística no deriva por su confianza; §`subsec:subsistema-clasificacion`). Desde el 13 de octubre de 2026 el backend deriva además a revisión al reportante no identificado en el directorio de empleados. |
| SDK | `google-genai` `>=2.20.0` | Versión de la configuración evaluada; la entregada exige `>=2.33.0,<3` (Tabla `tab:configuracion-evaluada-entregada`). |
*Fuente:* elaboración propia a partir de la documentación del SDK `google-genai`.

### Validación de la respuesta

Antes de aceptar la respuesta del modelo, el módulo de clasificación valida que el texto sea JSON parseable, que contenga exactamente las claves `categoría` y `confianza`, que la categoría sea uno de los cinco valores canónicos y que la confianza sea un número en el intervalo \([0,0, 1,0]\). Si cualquiera de estas condiciones falla, se registra la excepción, se asigna confianza 0,0, se marca el incidente para revisión humana y no se propagan estados inconsistentes a la base de datos. Este procedimiento garantiza la confiabilidad operativa frente a errores de formato o alucinaciones del modelo. El Listado `lst:validar-gemini` resume la rutina de validación.

lstlisting[caption=Validación de la respuesta de Gemini (resumen).,label=lst:validar-gemini]
def validar_respuesta_gemini(response_text: str) -> tuple[bool, dict]:
 try:
 data = json.loads(response_text)
 except json.JSONDecodeError as e:
 return False, "error": f"JSON invalido: e"
 if "categoría" not in data:
 return False, "error": "Falta campo 'categoría'"
 if data["categoría"] not in SECTORES_CANONICOS:
 return False, "error": f"Categoría invalida: data['categoría']"
 if "confianza" not in data:
 return False, "error": "Falta campo 'confianza'"
 if not isinstance(data["confianza"], (int, float)) \
 or not (0.0 <= data["confianza"] <= 1.0):
 return False, "error": f"Confianza invalida: data['confianza']"
 return True, data
lstlisting

### Iteración y mejora del prompt

El prompt de la versión evaluada se ajustó de forma iterativa a partir de errores observados en el corpus de validación; no se dispuso de un corpus independiente de preproducción. Las versiones históricas del prompt se conservan en el historial de versiones del repositorio (archivo docs/prompt_gemini.txt) para auditoría y eventual reversión.

### Recomendaciones para futuras iteraciones

Ante una degradación de las métricas por cambios en el modelo, se recomienda ampliar los ejemplos por clase (partiendo del único ejemplo actual, hasta cuatro o cinco), agregar contraejemplos de incidentes limítrofes, especificar umbrales de confianza explícitos, incluir un diccionario de términos clave por categoría y, una vez acumulado un corpus etiquetado del orden de magnitud indicado en la §`subsec:implicancias-practicas`, migrar a un modelo ajustado específicamente al dominio.

## Trazabilidad de las correcciones de los dictámenes

Los dictámenes que motivan las correcciones de la tesis son autoevaluaciones de control de calidad interno frente a criterios de la CONEAU, esto es revisiones evaluativas previas a la defensa solicitadas por los propios autores y no una revisión por pares. Se elaboraron aplicando un perfil de evaluador con criterios de la CONEAU, versionado en `docs/Tesis/Correcciones/Prompt2.docx`, mediante un modelo de lenguaje; no los emitieron el jurado, la dirección, la cátedra ni la CONEAU, no constituyen una revisión por pares humana y no son vinculantes. La serie comprende siete dictámenes fechados entre el 20 de octubre y el 9 de noviembre de 2026, que se conservan en `auditorias/`; cada uno declara su alcance (lectura íntegra del manuscrito, recomputo de las cifras, verificación bibliográfica y cotejo con el repositorio). Este anexo traza cuatro: el del 22 de octubre, sobre la versión `v1.1.0`, el del 28 de octubre, sobre la `v1.2.5`, el del 8 de noviembre, sobre la `v1.2.10`, y el del 9 de noviembre, sobre la `v1.2.12` (§`tab:anexo-trazabilidad-0911`). El registro acumulativo de las correcciones se conserva como artefacto versionado en docs/Tesis/Correcciones/dictamen-correcciones.md y vincula cada observación con el archivo y la línea corregidos.

El dictamen del 22 de octubre de 2026, aplicable por igual a `v1.1.1`, formuló cinco observaciones de fondo (A1 a A5) y correcciones de consistencia (B4 a B16), atendidas mediante changes del repositorio; la §`tab:anexo-trazabilidad` indica, para cada una, el change responsable y las secciones donde se la atendió. Cuando una recomendación se dividió en partes, figuran los changes que las atendieron, y los residuos que el dictamen siguiente volvió a señalar remiten a la fila que los atiende (§`tab:anexo-trazabilidad-2810`) o figuran como pendientes.

**Tabla: Recomendaciones del dictamen del 22 de octubre de 2026, change responsable y secciones donde se atendieron.**

4pt
| Rec. | Change | Secciones de la tesis |
| — | — | — |
| A1 | `c-130` | §`subsec:human-in-the-loop`, §`subsec:subsistema-clasificacion`, §`subsec:construccion-flujo-n8n`, §`subsec:reduccion-intervencion`; residuos en A3 y B8 del 28-10 |
| A2 | `c-131` | §`subsec:calibracion`, §`tab:bandas`, §`tab:exactitud-etapa-canal`, §`subsec:interpretacion-resultados` |
| A3 | `c-132` | §`subsec:balance-neto`, §`subsec:implicancias-practicas` |
| A4 | `c-139`, `c-138` | §`subsec:nlp-llm`, §`subsec:trabajos-academicos`, §`subsec:calibracion-cascadas`, §`subsec:clasificador-supervisado` |
| A5 | `c-130`, `c-144`, `c-142`, `c-154` | §`subsec:subsistema-clasificacion`, §`subsec:conexion-scrumban`, §`subsec:interpretacion-resultados`, §`subsec:anexo-iteracion-prompt`; §`subsec:sensibilidad-ajustes`, §`subsec:limitaciones-estudio` |
| B4 | `c-133` | §`tab:cumplimiento-objetivos`, §`subsec:cumplimiento-objetivos`; residuo en B7 del 28-10 |
| B5 | `c-133` | §`subsec:hipotesis-trabajo` |
| B6 | `c-133` | §`subsec:analisis-estadistico`, §`subsec:matriz-metricas`, §`tab:cumplimiento-objetivos` |
| B7 | `c-134`, `c-131` | §`tab:tiempos-canal`; §`tab:exactitud-etapa-canal` |
| B8 | `c-131` | §`subsec:analisis-estadistico`, §`subsec:matriz-metricas`, §`tab:exactitud-etapa-canal` |
| B9 | `c-135` | §`subsec:gestion-scrumban`, §`subsec:conexion-scrumban`, §`fig:cronograma`, §`subsec:limitaciones-estudio`; residuos en A1 del 28-10; las fechas de las iteraciones Scrumban no son recuperables (el tablero técnico fue Jira y su prueba se dio de baja sin export, el campo de iteración de GitHub Projects no es legible con el token local y el autor confirmó que el número de iteraciones se ajustó durante el proyecto), lo que se declara como limitación y no como pendiente |
| B10 | `c-135`, `c-146` | §`sec:resultados`, §`tab:comparativa`, §`tab:trabajos-academicos` |
| B11 | `c-136` | §`sec:recomendaciones`, §`subsec:calibracion-gate`, §`subsec:medicion-intervencion`, §`subsec:aprendizaje-activo` |
| B12 | `c-134` | §`subsec:analisis-estadistico`, §`subsec:amenazas-validez`, §`subsec:poblacion-muestra-corpus` |
| B13 | `c-135`, `c-134` | §`subsec:cumplimiento-objetivos`; §`subsec:diseno-experimental`, §`subsec:consentimiento-derechos` |
| B14 | `c-137`, `c-159`, `c-163` | Todo el documento (revisión ortotipográfica); residuos en A3 y A4 del 28-10 cerrados por c-159 y c-163 (erratas de figuras y *pseudonimizado*) |
| B15 | `c-139` | §`subsec:cumplimiento`, §`subsec:analisis-estadistico` |
| B16 | `c-139`, `c-141`, `c-163` | §`sec:anexo-repositorio` y Referencias bibliográficas; residuos en A2 del 28-10 cerrados por c-163 (fecha de consulta de una referencia) |

*Fuente:* elaboración propia a partir de docs/Tesis/Correcciones/dictamen-correcciones.md.

El dictamen del 28 de octubre de 2026, sobre la versión `v1.2.5`, formuló observaciones de método (A1 y A2), de coherencia entre figuras, tablas y texto (A3), de evidencia cualitativa (A4) y de residuos del proceso de corrección y consistencia interna (B5 a B8); la §`tab:anexo-trazabilidad-2810` indica el change responsable y las secciones donde se las atendió. Las demás observaciones de ese dictamen se atienden en changes posteriores del repositorio, entre ellos `c-169`, que midió cuatro de los cinco límites estructurales que el dictamen consignó y declara el quinto —la validación fuera de muestra— como limitación negativa (la fila ``Lím.'' de la tabla); el dictamen del 8 de noviembre acotó después dos de esas mediciones (§`tab:anexo-trazabilidad-0811`).

**Tabla: Recomendaciones del dictamen del 28 de octubre de 2026, change responsable y secciones donde se atendieron.**

4pt
| Rec. | Change | Secciones de la tesis |
| — | — | — |
| A1 | `c-158` | §`subsec:protocolo-pruebas`, párrafo inicial de la §`sec:resultados`, §`subsec:alcance-delimitaciones`, §`subsec:interpretacion-resultados`, §`subsec:integracion-canal-telefonico`, §`fig:cronograma`, §`sec:anexo-corpus` |
| A2 | `c-158` | §`tab:configuracion-evaluada-entregada` (§`sec:anexo-repositorio`); Secciones `subsec:capa-procesamiento`, `subsec:entorno-despliegue`, `subsec:construccion-modulo-python`, `subsec:construccion-flujo-n8n`, `subsec:desafios-integracion`, `subsec:pruebas-automatizadas`, `subsec:seguridad-tecnica`, §`subsec:anexo-parametros-config` |
| A3 | `c-159` | Figuras `fig:componentes`, `fig:arquitectura`, `fig:secuencia` y `fig:er_modelo_datos`; §`tab:entidades`; §`tab:cumplimiento-nist`; §`subsec:cumplimiento-brechas` |
| A4 | `c-159` | §`subsec:analisis-errores`, §`tab:errores` |
| B5 | `c-160` | §`subsec:hipotesis-trabajo`, §`subsec:subsistema-clasificacion`, §`subsec:construccion-flujo-n8n`, §`subsec:sensibilidad-ajustes`, §`subsec:interpretacion-resultados`, §`subsec:implicancias-practicas` |
| B6 | `c-160` | §`sec:anexo-trazabilidad` |
| B7 | `c-160` | Resumen y *abstract*, §`subsec:cumplimiento-objetivos`, §`tab:cumplimiento-objetivos` |
| B8 | `c-160` | §`subsec:vision-general`, §`subsec:human-in-the-loop`, §`subsec:subsistema-clasificacion`, §`subsec:construccion-flujo-n8n`, §`subsec:consentimiento-derechos`, §`subsec:sensibilidad-ajustes`, §`subsec:calibracion-gate`, §`subsec:anexo-parametros-config`, §`sec:anexo-documentacion-operativa` |
| Lím. | `c-169`, `c-190` | De los cinco límites estructurales que el dictamen consignó sin computarlos como incumplimiento, la campaña complementaria resolvió primero dos —la exactitud del brazo manual y el intervalo del kappa— (§`subsec:resultados-campana-medicion`, §`subsec:balance-neto`) y dejó entonces sin concluir la proporción de intervención humana (§`subsec:reduccion-intervencion`); más tarde, esa sub-hipótesis quedó refutada sobre los casos revisados y se corrigió la definición de la exactitud laxa (§`subsec:reduccion-intervencion`, §`subsec:resultados-campana-medicion`). El efecto de orden no se resolvió (§`subsec:diseno-experimental`) y la validación fuera de muestra permanece como limitación negativa declarada por ausencia de un corpus independiente (§`subsec:limitaciones-estudio`); Resumen y *abstract*; §`sec:anexo-repositorio` (Tabla `tab:configuracion-evaluada-entregada`) |

*Fuente:* elaboración propia a partir de docs/Tesis/Correcciones/dictamen-correcciones.md.

El dictamen del 8 de noviembre de 2026, sobre la versión `v1.2.10`, formuló cinco observaciones de fondo (A1 a A5) y de consistencia y forma; la §`tab:anexo-trazabilidad-0811` indica las secciones que los changes `c-187` y `c-188` corrigieron.

**Tabla: Recomendaciones del dictamen del 8 de noviembre de 2026, secciones donde se atendieron (change responsable: `c-187**

 para A1 a A5, B1 a B3 y B6; c-188` para B4, B5, B7 y C1 a C5).

4pt
| Rec. | Secciones de la tesis |
| — | — |
| A1 | §`subsec:reduccion-intervencion`, §`subsec:hipotesis-trabajo`, §`subsec:interpretacion-resultados`, §`tab:cumplimiento-objetivos`, §`subsec:medicion-intervencion`, Resumen y *abstract* |
| A2 | §`subsec:diseno-experimental`, §`subsec:protocolo-pruebas`, §`subsec:amenazas-validez`, §`subsec:resultados-campana-medicion`, §`subsec:interpretacion-resultados` |
| A3 | §`subsec:poblacion-muestra-corpus`, §`subsec:amenazas-validez`, §`subsec:limitaciones-estudio`, §`subsec:aportes-generalizacion`, Resumen y *abstract* |
| A4 | §`subsec:resultados-campana-medicion`, §`subsec:balance-neto` |
| A5 | §`sec:anexo-repositorio`, §`tab:configuracion-evaluada-entregada`, §`subsec:entorno-despliegue`, portada |
| B1, B2 | §`subsec:resultados-campana-medicion`, §`subsec:reduccion-intervencion`, párrafo inicial de la §`sec:resultados` |
| B3 | Figuras `fig:secuencia` y `fig:componentes`, §`tab:entidades`, §`tab:configuracion-evaluada-entregada` |
| B6 | §`subsec:aportes-generalizacion`, §`subsec:limitaciones-estudio`, §`subsec:medicion-intervencion`, Resumen y *abstract* |
| B4 | §`subsec:analisis-estadistico`, §`subsec:matriz-metricas`, §`subsec:subsistema-clasificacion`, §`subsec:implicancias-practicas` |
| B5 | §`subsec:dashboard-analitica`, Figura `fig:despliegue`, §`tab:matriz` |
| B7 | Resumen de compilación y verificador de trazabilidad, versionados en el repositorio (§`sec:anexo-repositorio`) |
| C1 | §`subsec:planteamiento-problema`, §`subsec:mesa-ayuda-itil`, §`subsec:metricas-instrumentos`, §`subsec:diseno-experimental` |
| C2 | §`tab:comparativa`, §`subsec:transferencia-internacional`, §`subsec:entorno-despliegue`, §`subsec:integracion-canal-telefonico` |
| C3 | §`subsec:reflexiones-generalizacion`, §`tab:trabajos-academicos` |
| C4 | Lista de referencias |
| C5 | Glosario de siglas y acrónimos |

*Fuente:* elaboración propia a partir de docs/Tesis/Correcciones/dictamen-correcciones.md.

El dictamen del 9 de noviembre de 2026, sobre la versión `v1.2.12`, formuló tres observaciones de fondo (A1 a A3), cuatro de consistencia (B1 a B4) y dos de forma y bibliografía (C1 y C2); su change responsable es `c-190`, y la §`tab:anexo-trazabilidad-0911` indica las secciones que corrigió.

**Tabla: Recomendaciones del dictamen del 9 de noviembre de 2026, secciones donde se atendieron (change responsable: `c-190**

).`

4pt
| Rec. | Change | Secciones de la tesis |
| — | — | — |
| A1 | `c-190` | §`subsec:reduccion-intervencion`, §`subsec:hipotesis-trabajo`, §`subsec:interpretacion-resultados`, §`tab:cumplimiento-objetivos`, §`subsec:medicion-intervencion`, Resumen y *abstract* |
| A2 | `c-190` | §`subsec:diseno-experimental`, §`subsec:poblacion-muestra-corpus`, §`subsec:amenazas-validez`, §`subsec:interpretacion-resultados`, §`subsec:consentimiento-derechos` |
| A3 | `c-190` | §`tab:configuracion-evaluada-entregada` |
| B1 | `c-190` | §`subsec:capa-canales`, §`subsec:integracion-canal-telefonico`, §`subsec:conexion-scrumban`, §`tab:configuracion-evaluada-entregada`, §`anexo:H`, §`subsec:implicancias-practicas`, Figura `fig:despliegue` |
| B2 | `c-190` | §`subsec:reduccion-intervencion`, §`subsec:resultados-campana-medicion`, §`subsec:balance-neto` |
| B3 | `c-190` | §`subsec:human-in-the-loop`, §`subsec:subsistema-clasificacion`, §`subsec:construccion-flujo-n8n`, §`subsec:consentimiento-derechos`, §`subsec:protocolo-pruebas`, Figuras `fig:secuencia` y `fig:componentes` |
| B4 | `c-190` | §`subsec:justificacion`, Resumen y *abstract*, §`tab:cumplimiento-objetivos` |
| C1 | `c-190` | §`subsec:limitaciones-estudio`, §`subsec:reduccion-intervencion`, §`tab:cumplimiento-objetivos`, §`sec:anexo-repositorio`, Glosario de siglas y acrónimos, portada |
| C2 | `c-190` | §`subsec:human-in-the-loop`, §`subsec:gestion-servicios-ti`, §`subsec:implicancias-practicas`, §`sec:aspectos-legales`, §`subsec:trabajos-academicos` |

*Fuente:* elaboración propia a partir de docs/Tesis/Correcciones/dictamen-correcciones.md.

La trazabilidad interna de tres decisiones de diseño que el cuerpo de la §`sec:implementacion` presenta en lenguaje llano se conserva aquí: el retiro de la rama de clasificación telefónica por agente LLM basada en LangChain y el traslado de la superficie de costo al backend (`c-72`); el reemplazo del umbral de 0,90 sobre la confianza por el punto de operación del puntaje de correctitud (`c-74`); y la derivación a revisión del incidente cuyo reportante no se identifica en el directorio de empleados, incorporada el 13 de octubre de 2026 (`c-82`). El detalle de cada decisión figura en docs/Tesis/Correcciones/dictamen-correcciones.md.
