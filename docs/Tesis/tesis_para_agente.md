**UNIVERSIDAD TECNOLÓGICA NACIONAL**

**FACULTAD REGIONAL MENDOZA**

*Tecnicatura Universitaria en Programación*

**Automatización inteligente del registro de incidentes**

**en mesas de ayuda empresariales mediante orquestación de**

**flujos con N8N y procesamiento de lenguaje natural**

**basado en modelos de lenguaje grandes**

*Trabajo Final de Carrera presentado para obtener el título de*

***Técnico Universitario en Programación***

**Autores**

**Luca Gómez · Carla Bustos · Gonzalo Sevilla**

**Director**

**Prof. Alberto Cortez**

**Mendoza, República Argentina · 2026**

# Resumen

La creciente digitalización de los procesos organizacionales ha generado una dependencia cada vez mayor de los sistemas informáticos para la ejecución de las actividades operativas. En este contexto, la gestión eficiente de incidentes tecnológicos constituye un factor determinante para garantizar la continuidad del negocio y la calidad del servicio brindado a los usuarios internos. Sin embargo, en numerosas organizaciones medianas el proceso de registro inicial de incidentes continúa realizándose de manera manual, lo que introduce demoras operativas, errores de clasificación y una utilización ineficiente de los recursos técnicos disponibles.

La presente investigación tiene como propósito el diseño, desarrollo, implementación y validación experimental de un sistema automatizado de mesa de ayuda empresarial basado en la integración de orquestación de flujos mediante la plataforma N8N, un módulo de procesamiento de lenguaje natural desarrollado en Python con el marco FastAPI, una capa de inferencia lingüística sustentada en el modelo Gemini 2.5 de Google, una capa de persistencia sobre PostgreSQL versión quince y un canal de telefonía gestionado por Twilio. La arquitectura propuesta contempla la recepción de solicitudes a través de tres canales paralelos ---correo electrónico, formulario web y llamadas telefónicas con transcripción automática--- y deriva cada incidente al sector responsable, Sistemas, Operaciones o Soporte Técnico, mediante un clasificador híbrido en dos etapas que combina reglas determinísticas y modelo de lenguaje grande.

El estudio se desarrolló bajo un enfoque cuantitativo con diseño cuasi experimental de muestras pareadas y contrabalanceo del orden de procesamiento. El corpus de validación, construido por muestreo estratificado proporcional sobre un universo trimestral de aproximadamente 3.700 incidentes, comprende 200 casos representativos del entorno operativo. El acuerdo entre los dos analistas que realizaron el doble etiquetado independiente alcanzó un coeficiente Kappa de Cohen de 0,87, considerado sustancial. Cada incidente fue procesado mediante el flujo manual tradicional y mediante el sistema automatizado, registrando el tiempo de procesamiento, la categoría asignada y la proporción de intervención humana.

Los resultados obtenidos evidencian una reducción estadísticamente significativa del tiempo medio de registro, que descendió desde 165,3 segundos en el flujo manual hasta 18,2 segundos en el flujo automatizado, lo que representa una reducción relativa del 89%. La prueba de Wilcoxon de rangos con signo aplicada sobre las mediciones pareadas arrojó un valor p \< 0,001, permitiendo rechazar la hipótesis nula de igualdad de medianas. La exactitud global del clasificador alcanzó el 92 % y el valor F1 macro promediado se ubicó en 0,919. La proporción de intervención humana descendió desde el 100% en el flujo manual hasta el 9,5% en el flujo automatizado, materializando un esquema human in the loop en el cual el operador conserva la potestad de revisión sobre los casos de baja confianza o ambigüedad estructural.

Los hallazgos confirman la viabilidad técnica, económica y operativa de la automatización inteligente del registro de tickets en organizaciones medianas. La investigación aporta una arquitectura reproducible y escalable construida sobre componentes maduros de código abierto e inferencia lingüística externa, evidencia empírica sobre el desempeño de modelos de lenguaje grandes aplicados a clasificación de tickets en español rioplatense, y un marco normativo aplicable que contempla la Ley 25.326 de Protección de los Datos Personales de la República Argentina.

# Índice general

[Resumen 2](#_heading=)

[1. Introducción 6](#_heading=)

> [1.1. Contextualización 6](#_heading=)
>
> [1.2. Planteamiento del problema 6](#_heading=)
>
> [1.3. Pregunta de investigación 7](#_heading=)
>
> [1.4. Hipótesis de trabajo 7](#_heading=)
>
> [1.5. Objetivo general 8](#_heading=)
>
> [1.6. Objetivos específicos 8](#_heading=)
>
> [1.7. Justificación 9](#_heading=)
>
> [1.8. Alcance y delimitaciones 10](#_heading=)

[2. Marco teórico 11](#_heading=)

> [2.1. Gestión de servicios de tecnologías de la información 11](#_heading=)
>
> [2.2. Mesa de ayuda y modelo ITIL 11](#_heading=)
>
> [2.3. Automatización de procesos y orquestación de flujos 12](#_heading=)
>
> [2.4. Procesamiento de lenguaje natural y modelos de lenguaje grandes 12](#_heading=)
>
> [2.5. Reconocimiento automático del habla 13](#_heading=)
>
> [2.6. Bases de datos relacionales y persistencia transaccional 14](#_heading=)
>
> [2.7. Métricas de evaluación de clasificadores multiclase 14](#_heading=)

[3. Estado del arte 15](#_heading=)

> [3.1. Soluciones comerciales de mesa de ayuda 15](#_heading=)
>
> [3.2. Plataformas de orquestación de flujos 15](#_heading=)
>
> [3.3. Trabajos académicos previos sobre clasificación de tickets 16](#_heading=)
>
> [3.4. Análisis comparativo y brecha identificada 16](#_heading=)

[4. Marco metodológico 18](#_heading=)

> [4.1. Enfoque y tipo de investigación 18](#_heading=)
>
> [4.2. Diseño experimental 18](#_heading=)
>
> [4.3. Operacionalización de variables 19](#_heading=)
>
> [4.4. Población, muestra y corpus 19](#_heading=)
>
> [4.5. Protocolo de pruebas 20](#_heading=)
>
> [4.6. Métricas e instrumentos 20](#_heading=)
>
> [4.7. Análisis estadístico 21](#_heading=)
>
> [4.8. Amenazas a la validez 21](#_heading=)
>
> [4.9. Gestión del proyecto bajo enfoque Scrumban 23](#_heading=)

[5. Arquitectura del sistema 24](#_heading=)

> [5.1. Visión general 24](#_heading=)
>
> [5.2. Capa de canales de entrada 25](#_heading=)
>
> [5.3. Capa de orquestación 25](#_heading=)
>
> [5.4. Capa de procesamiento 26](#_heading=)
>
> [5.5. Subsistema de clasificación híbrido 26](#_heading=)
>
> [5.6. Modelo de datos 28](#_heading=)
>
> [5.7. Contrato de la interfaz REST 28](#_heading=)

[6. Implementación 30](#_heading=)

> [6.1. Entorno de despliegue y dependencias 30](#_heading=)
>
> [6.2. Construcción del módulo Python 30](#_heading=)
>
> [6.3. Construcción del flujo en N8N 30](#_heading=)
>
> [6.4. Integración del canal telefónico 31](#_heading=)
>
> [6.5. Pruebas automatizadas 31](#_heading=)

[7. Resultados 32](#_heading=)

> [7.1. Comparación de tiempos de registro 32](#_heading=)
>
> [7.2. Matriz de confusión y métricas de clasificación 33](#_heading=)
>
> [7.3. Reducción de la intervención humana 34](#_heading=)
>
> [7.4. Análisis de errores y casos límite 34](#_heading=)

[8. Discusión 36](#_heading=)

> [8.1. Interpretación de los resultados 36](#_heading=)
>
> [8.2. Comparación con la literatura 36](#_heading=)
>
> [8.3. Limitaciones del estudio 37](#_heading=)
>
> [8.4. Implicancias prácticas 38](#_heading=)
>
> [8.5. Reflexiones sobre la generalización 38](#_heading=)

[9. Conclusiones 39](#_heading=)

[10. Recomendaciones y líneas de trabajo futuro 41](#_heading=)

[11. Consideraciones éticas y aspectos legales 43](#_heading=)

> [11.1. Marco normativo aplicable 43](#_heading=)
>
> [11.2. Principios aplicados al tratamiento de datos 43](#_heading=)
>
> [11.3. Transferencia internacional y pseudonimización 44](#_heading=)
>
> [11.4. Seguridad técnica 44](#_heading=)
>
> [11.5. Consentimiento, derechos del usuario y supervisión humana 44](#_heading=)

[12. Referencias bibliográficas 46](#_heading=)

[13. Anexos 49](#_heading=)

> [Anexo A. Diagrama de arquitectura del sistema 49](#_heading=)
>
> [Anexo B. Repositorio de código fuente 49](#_heading=)
>
> [Anexo C. Esquema de base de datos 49](#_heading=)
>
> [Anexo D. Especificación OpenAPI de la interfaz REST 49](#_heading=)
>
> [Anexo E. Configuración del flujo N8N 50](#_heading=)
>
> [Anexo F. Corpus de validación 50](#_heading=)
>
> [Anexo G. Documentación operativa 50](#_heading=)

# 1. Introducción

## 1.1. Contextualización

La evolución de las tecnologías de la información ha transformado profundamente la dinámica operativa de las organizaciones contemporáneas. En la actualidad los sistemas informáticos constituyen el soporte fundamental para la ejecución de procesos administrativos, productivos y de comunicación, y esa dependencia tecnológica ha incrementado de manera correlativa la importancia de los servicios de soporte técnico, particularmente aquellos relacionados con la gestión de incidentes informáticos. Galup et al. (2009) caracterizan a la disciplina de gestión de servicios de tecnologías de la información como un cuerpo de prácticas orientado a alinear la operación tecnológica con los objetivos del negocio, donde la mesa de ayuda actúa como punto único de contacto entre el usuario y el área de tecnología.

Dentro de este escenario, las mesas de ayuda empresariales cumplen un rol central en la recepción, registro y seguimiento de incidentes reportados por los usuarios. Estas unidades organizacionales canalizan solicitudes y constituyen la primera línea de atención técnica, de modo que su eficiencia impacta directamente en la continuidad operativa. No obstante, en muchas organizaciones medianas el proceso de registro inicial continúa realizándose manualmente, lo que introduce demoras, inconsistencias y una marcada dependencia del criterio individual del operador.

## 1.2. Planteamiento del problema

La presente investigación se desarrolla en el marco de una organización mediana del sector servicios con sede en la provincia de Mendoza, República Argentina, cuya plantilla asciende a aproximadamente ciento veinte usuarios internos distribuidos en cinco áreas funcionales. El sector de Operaciones desempeña simultáneamente tareas vinculadas a la gestión operativa cotidiana y a la atención de incidentes informáticos reportados por los usuarios, lo que obliga al personal responsable a interrumpir actividades críticas para registrar manualmente fallas de hardware, inconvenientes de software o solicitudes de asistencia técnica.

Las mediciones preliminares realizadas durante una semana laboral representativa evidenciaron un volumen promedio de cuarenta y dos incidentes diarios, un tiempo medio de registro manual de dos minutos con cuarenta y cinco segundos por incidente y una tasa de derivación errónea inicial cercana al 15%. La proyección trimestral sobre estos indicadores arrojó un universo aproximado de tres mil setecientos incidentes, con un costo operativo asociado a la etapa de registro estimado en el orden de doscientas horas-persona por trimestre, lapso que el personal podría redirigir a tareas de mayor valor agregado si la etapa de registro estuviera automatizada. Estos indicadores justifican la búsqueda de una alternativa tecnológica que reduzca el costo operativo, mejore la calidad de la derivación temprana y disminuya la variabilidad asociada al criterio individual.

El registro manual de incidentes implica además la lectura de correos electrónicos, la interpretación de descripciones textuales heterogéneas, la clasificación del problema según el área responsable y la carga manual de la información en un sistema de tickets. Este procedimiento requiere tiempo, interrumpe las tareas del personal técnico y puede generar errores de clasificación que prolongan la cadena de resolución cuando un ticket es derivado a un área incorrecta. La dispersión de los canales de comunicación ---correo, llamada telefónica y formularios internos--- agrava la situación al obligar al personal a monitorear múltiples fuentes simultáneamente.

## 1.3. Pregunta de investigación

A partir del problema descrito, esta investigación se orienta a responder la siguiente pregunta: ¿reduce la automatización del registro inicial de incidentes mediante orquestación de flujos y procesamiento de lenguaje natural el tiempo de registro y mejora la exactitud de clasificación en una mesa de ayuda empresarial mediana, en comparación con el proceso manual realizado por personal experimentado?

## 1.4. Hipótesis de trabajo

La hipótesis principal sostiene que la implementación de un sistema automatizado de registro de incidentes basado en orquestación de flujos con N8N y procesamiento de lenguaje natural mediante un modelo de lenguaje grande permite reducir significativamente el tiempo de registro y la proporción de intervención humana, manteniendo una exactitud de clasificación equivalente o superior a la observada en el proceso manual realizado por personal experimentado. La hipótesis nula complementaria, que se contrasta empíricamente, postula la inexistencia de diferencias significativas entre ambos flujos en las variables observadas. Como hipótesis subsidiarias se plantea, en primer lugar, que la integración de múltiples canales de entrada dentro de un único flujo automatizado mejora la accesibilidad del sistema y reduce la dispersión operativa, y en segundo lugar, que un esquema híbrido de clasificación basado en reglas determinísticas y modelo de lenguaje grande resulta más eficiente, en términos de la relación entre exactitud, latencia y costo de inferencia, que un esquema construido exclusivamente sobre modelo externo.

##  

## 1.5. Objetivo general

Desarrollar e implementar un sistema automatizado de mesa de ayuda empresarial basado en orquestación de flujos con N8N y procesamiento de lenguaje natural en Python que permita recibir, procesar, clasificar y registrar incidentes de usuarios de manera automática, reduciendo el tiempo de registro y la proporción de intervención humana en la etapa inicial del proceso, manteniendo la supervisión técnica para la resolución de los casos y garantizando la trazabilidad de las decisiones tomadas por el sistema.

## 1.6. Objetivos específicos

El primer objetivo específico consiste en diseñar una arquitectura distribuida y modular que integre un motor de orquestación de flujos, un módulo de procesamiento de lenguaje natural, un canal de telefonía con transcripción automática del habla y una base de datos relacional, garantizando comunicación asincrónica entre componentes mediante interfaces de programación de aplicaciones de tipo REST sobre HTTP cifrado.

El segundo objetivo específico se orienta a implementar un clasificador automático que asigne cada incidente a uno de los tres sectores responsables, Sistemas, Operaciones o Soporte Técnico, alcanzando una exactitud global no inferior al 85 % sobre un corpus controlado de 200 casos representativos del entorno operativo, y un valor F1 macro promediado no inferior a 0,85. El umbral del 85 % se fundamenta en tres criterios convergentes: (a) los trabajos de Paramesh y Shreedhara (2019) reportan exactitudes de \~87 % con enfoques SVM + TF-IDF, estableciendo un piso de referencia para el estado del arte en clasificación de tickets; (b) el costo organizacional de una derivación errónea implica al menos 10--15 minutos adicionales de reasignación según las mediciones preliminares de la organización, por lo que una exactitud inferior al 85 % resultaría en tiempos de resolución comparables a los del flujo manual para un volumen de errores inaceptable; y (c) el margen por encima del 85 % reserva espacio estadístico para que el intervalo de confianza del estimador no solape la zona de rechazo de la hipótesis, dado el tamaño muestral de 200 casos.

El tercer objetivo específico plantea integrar tres canales de entrada paralelos ---correo electrónico, formulario web y llamada telefónica con transcripción automática--- dentro de un único flujo automatizado que normalice la entrada y centralice el procesamiento, mejorando la accesibilidad del sistema sin incrementar la complejidad operativa percibida por los usuarios finales.

El cuarto objetivo específico consiste en evaluar comparativamente el flujo manual y el flujo automatizado en términos de tiempo medio de registro, dispersión, exactitud de clasificación y proporción de intervención humana, mediante un diseño cuasi experimental con muestras pareadas, prueba estadística no paramétrica y reporte de intervalos de confianza al 95%.

El quinto objetivo específico se orienta a documentar exhaustivamente la arquitectura, los procedimientos de despliegue y los resultados experimentales, proponiendo una hoja de ruta de evolución que oriente futuras mejoras y replicaciones del estudio en organizaciones de características comparables.

## 1.7. Justificación

La justificación del trabajo se sostiene en tres dimensiones complementarias. Desde la dimensión organizacional, la automatización propuesta libera capacidad operativa del personal técnico, reduce el tiempo de respuesta percibido por los usuarios y disminuye la variabilidad introducida por el criterio individual. Desde la dimensión tecnológica, la solución integra herramientas de bajo costo y código abierto, permitiendo una implementación reproducible en organizaciones de tamaño mediano sin requerir grandes inversiones de capital ni dependencia exclusiva de proveedores comerciales. Desde la dimensión académica, el trabajo aporta evidencia empírica sobre el desempeño de modelos de lenguaje grandes aplicados a la clasificación de tickets en español rioplatense, dominio escasamente documentado en la literatura comparativa disponible (Karchhud et al., 2024).

Adicionalmente, la mayoría de las soluciones comerciales disponibles, tales como Zendesk Suite o ServiceNow ITSM, presentan modelos de costos por agente y mes que escalan linealmente con el equipo y operan exclusivamente en modalidad de software como servicio con almacenamiento de datos en jurisdicciones extranjeras. La propuesta desarrollada en esta investigación utiliza herramientas de despliegue autoalojado, lo que facilita su adopción en organizaciones medianas y simplifica el cumplimiento de la normativa argentina de protección de datos personales.

##  

## 1.8. Alcance y delimitaciones

El alcance del trabajo se circunscribe a la etapa de recepción, clasificación y registro inicial de incidentes, sin abarcar la resolución técnica de los mismos, la cual permanece bajo responsabilidad del personal humano. El sistema contempla tres canales de entrada y tres sectores de derivación, y la validación experimental se realiza sobre un corpus en idioma español rioplatense recolectado en una única organización del sector servicios. Quedan fuera del alcance la integración con sistemas externos de inventario, los modelos de aprendizaje supervisado entrenados con corpus propios de la organización, la implementación de paneles de monitoreo avanzados con visualización en tiempo real y la automatización de la etapa de resolución técnica, todos los cuales se proponen como líneas de trabajo futuro en el capítulo de recomendaciones.

# 2. Marco teórico

## 2.1. Gestión de servicios de tecnologías de la información

La gestión de servicios de tecnologías de la información, conocida internacionalmente por su acrónimo en inglés ITSM, constituye una disciplina sistematizada que articula procesos, personas y tecnologías con el propósito de entregar valor al negocio a través de servicios tecnológicos confiables y mensurables. Galup et al. (2009) caracterizan la disciplina como un cuerpo de prácticas orientado a alinear la operación tecnológica con los objetivos del negocio, donde la mesa de ayuda opera como punto único de contacto entre el usuario y el área de tecnología. Este enfoque rompe con la concepción anterior que entendía a la informática como un área de soporte estrictamente reactivo y la posiciona en cambio como un proveedor de servicios sujeto a acuerdos de nivel de servicio explícitos.

Dentro de este marco general, la gestión de incidentes constituye uno de los procesos operativos centrales. Su objetivo principal consiste en restaurar el servicio afectado en el menor tiempo posible, minimizando el impacto adverso en la operación del negocio. El proceso comprende cuatro etapas secuenciales: la recepción y registro inicial, la clasificación y priorización, la asignación al área responsable y, finalmente, la resolución y cierre. Pressman y Maxim (2020) advierten que los procesos manuales de soporte tienden a degradarse cuando el volumen de solicitudes crece de manera no lineal o cuando el personal debe alternar entre tareas operativas heterogéneas, situación que coincide con la observada en el entorno empresarial analizado en el presente trabajo.

## 2.2. Mesa de ayuda y modelo ITIL

El marco de buenas prácticas ITIL, en su edición de operaciones de servicio (Office of Government Commerce, 2011), establece la distinción conceptual entre incidente, definido como una interrupción no planificada del servicio o una reducción de su calidad, y solicitud de servicio, definida como un pedido formal de información, asesoramiento, acceso a un componente o ejecución de una operación estandarizada. Esta distinción resulta especialmente relevante para el diseño del clasificador propuesto en este trabajo, ya que orienta la categorización inicial y condiciona la priorización subsiguiente. El marco ITIL adicionalmente postula la centralización de la recepción mediante un punto único de contacto y la operación bajo acuerdos de nivel de servicio que cuantifican la calidad esperada en términos de tiempo de respuesta y tiempo de resolución.

Los modelos tradicionales de mesa de ayuda se basan en la interacción manual entre el usuario y el operador, lo que implica tiempos de respuesta variables y una dependencia directa del personal disponible. Cuando el volumen de incidentes excede la capacidad del equipo o cuando los operadores deben alternar simultáneamente entre tareas operativas y de soporte, la calidad del servicio degrada de manera observable. La automatización del registro inicial constituye, en consecuencia, una intervención que aborda el cuello de botella en el punto de mayor sensibilidad del proceso.

## 2.3. Automatización de procesos y orquestación de flujos

La automatización de procesos empresariales permite reducir la intervención humana en tareas repetitivas mediante la ejecución automática de acciones definidas a partir de eventos específicos. Russell y Norvig (2021) ubican a la automatización inteligente dentro del paradigma de los agentes orientados a objetivos, en el cual un sistema reactivo percibe eventos del entorno, decide acciones según una política preestablecida y actúa modificando el estado del entorno. Esta caracterización ofrece un marco conceptual robusto para el diseño de sistemas que combinan reglas determinísticas con decisiones derivadas de modelos probabilísticos.

Las herramientas de orquestación, también denominadas plataformas de integración como servicio o iPaaS por sus siglas en inglés, posibilitan integrar distintos servicios, procesar información y ejecutar acciones automáticas en función de condiciones predefinidas. Estas plataformas se caracterizan por ofrecer modelos visuales de construcción de flujos, soporte nativo para webhooks y disparadores reactivos, y capacidad de transformación de datos entre sistemas heterogéneos. N8N, la herramienta seleccionada para este trabajo, se distingue dentro del segmento por su modelo de licencia de código fuente disponible y su capacidad de despliegue completamente autoalojado, característica que resulta decisiva en escenarios donde el tratamiento de datos sensibles exige mantener la información dentro del perímetro organizacional (n8n GmbH, 2024).

El paradigma de orquestación se diferencia conceptualmente del paradigma de coreografía. Hohpe y Woolf (2003) establecen que la orquestación centraliza la lógica de control en un componente único, lo que simplifica la trazabilidad de cada ejecución pero introduce un punto de coordinación cuya disponibilidad condiciona al sistema completo. La coreografía, en cambio, distribuye la coordinación entre los participantes mediante eventos publicados en un bus común, lo que aumenta la robustez frente a fallos parciales pero dificulta la observabilidad. El presente trabajo adopta el enfoque de orquestación por simplicidad operativa y por la prioridad otorgada a la trazabilidad auditiva de cada decisión del sistema.

## 2.4. Procesamiento de lenguaje natural y modelos de lenguaje grandes

El procesamiento de lenguaje natural constituye un área de la inteligencia artificial orientada a la interpretación del lenguaje humano por parte de sistemas informáticos. Jurafsky y Martin (2023) sistematizan la disciplina en torno a tres ejes principales, el modelado estadístico de secuencias, la representación distribuida de palabras y la comprensión semántica mediante arquitecturas neuronales profundas. Mediante estas técnicas resulta posible analizar texto o audio transcrito, identificar palabras clave, determinar la intención del usuario y clasificar contenido en categorías predefinidas.

La evolución del campo durante la última década ha estado dominada por la arquitectura Transformer (Vaswani et al., 2017), cuyo mecanismo de atención permite a los modelos capturar dependencias de largo alcance sin las limitaciones de las redes neuronales recurrentes. Sobre esta arquitectura se construyeron los modelos de lenguaje grandes contemporáneos, los cuales exhiben capacidades robustas de clasificación en escenarios de pocos ejemplos o sin ejemplos, fenómeno conocido como aprendizaje en contexto. Brown et al. (2020) demostraron que modelos suficientemente grandes pueden generalizar a tareas nuevas a partir de instrucciones expresadas en lenguaje natural, sin requerir ajuste fino sobre datos específicos del dominio.

En el contexto de una mesa de ayuda, el uso de procesamiento de lenguaje natural permite clasificar incidentes y derivarlos al sector correspondiente sin intervención manual, mejorando la velocidad de respuesta y reduciendo la carga operativa del personal encargado del registro. La elección entre un clasificador supervisado entrenado sobre corpus específico, un modelo de lenguaje grande de propósito general invocado mediante instrucciones, o un esquema híbrido que combine ambas estrategias, constituye una decisión de diseño que depende de la disponibilidad de datos etiquetados, del presupuesto de inferencia disponible y de los requerimientos de soberanía sobre los datos procesados.

## 2.5. Reconocimiento automático del habla

Los sistemas de reconocimiento automático del habla permiten convertir audio en texto mediante modelos previamente entrenados sobre grandes corpus de habla anotada. Rabiner y Juang (1993) describen los fundamentos clásicos del reconocimiento basado en modelos ocultos de Markov, mientras que la generación contemporánea de sistemas se apoya mayoritariamente en redes neuronales profundas con arquitecturas codificador decodificador, de las cuales el modelo Whisper (Radford et al., 2023) representa un exponente reciente con alta robustez en escenarios multilingües y en presencia de ruido ambiental. La utilización de estos mecanismos facilita la recepción de incidentes a través de llamadas telefónicas, ampliando los canales de entrada del sistema. La integración entre reconocimiento del habla y procesamiento de lenguaje natural permite automatizar completamente la recepción y clasificación de solicitudes, posibilitando que el sistema interprete la solicitud del usuario y genere el ticket correspondiente sin intervención humana en la etapa de captura.

##  

## 2.6. Bases de datos relacionales y persistencia transaccional

La persistencia de los incidentes en una base de datos relacional permite garantizar las propiedades de atomicidad, consistencia, aislamiento y durabilidad propias del modelo transaccional clásico, conocidas globalmente por su acrónimo en inglés ACID (Date, 2003). PostgreSQL, el motor seleccionado para este trabajo, ofrece soporte completo del estándar SQL, extensiones para tipos de datos avanzados como JSON binario y arreglos, y un modelo de concurrencia basado en control multiversional que resulta adecuado para cargas mixtas de lectura y escritura (The PostgreSQL Global Development Group, 2024). La elección de un motor relacional frente a alternativas no relacionales se sustenta en la naturaleza estructurada de los datos del dominio, donde las relaciones entre incidentes, sectores, estados y canales de origen se modelan naturalmente como tablas vinculadas mediante claves foráneas con integridad referencial declarativa.

## 2.7. Métricas de evaluación de clasificadores multiclase

La evaluación de clasificadores multiclase requiere métricas que capturen tanto el desempeño global como el desempeño por clase. Powers (2011) describe el conjunto canónico de métricas derivadas de la matriz de confusión, entre las cuales destacan la exactitud global, la precisión por clase, la sensibilidad o recall por clase, y la medida F1 como media armónica de las dos anteriores. Sokolova y Lapalme (2009) advierten que en escenarios con clases desbalanceadas la exactitud global puede resultar engañosa y recomiendan reportar valores macro promediados, los cuales otorgan igual peso a cada clase con independencia de su frecuencia. El presente trabajo adopta esta recomendación y reporta tanto exactitud global como F1 macro y métricas desagregadas por clase, permitiendo al lector evaluar la robustez del clasificador frente a la distribución específica del corpus.

Adicionalmente, la matriz de confusión constituye el instrumento estándar de presentación de resultados en clasificación multiclase, ya que permite identificar patrones específicos de error: confusiones sistemáticas entre dos categorías particulares, sesgos hacia una clase mayoritaria o aciertos preferenciales sobre una clase específica. La inspección de la matriz orienta el análisis cualitativo posterior y constituye la base para cualquier propuesta de mejora del clasificador.

# 3. Estado del arte

## 3.1. Soluciones comerciales de mesa de ayuda

El segmento de soluciones comerciales para gestión de mesa de ayuda se encuentra dominado por plataformas integrales que cubren el ciclo completo de vida del ticket. Zendesk Suite, una de las plataformas con mayor presencia en organizaciones medianas y grandes, ofrece funcionalidades de recepción multicanal, automatización de flujos básicos y, mediante un módulo adicional, capacidades de inteligencia artificial para sugerencia de respuestas y deflección de consultas frecuentes. Freshdesk, perteneciente al grupo Freshworks, propone una arquitectura comparable e incorpora el motor Freddy AI para clasificación automática y enrutamiento inteligente. Jira Service Management, parte del ecosistema de Atlassian, es ampliamente adoptada en organizaciones que utilizan otras herramientas del mismo proveedor; su plan estándar ofrece capacidades limitadas de automatización inteligente, aunque la edición Data Center permite el despliegue autoalojado para organizaciones con requisitos de soberanía sobre los datos. ServiceNow ITSM constituye la opción de referencia en el segmento corporativo de mayor envergadura, con un módulo Predictive Intelligence que aplica aprendizaje automático sobre el histórico de tickets de la organización.

Mehdi et al. (2023) reportan que la adopción de capacidades de inteligencia artificial en plataformas comerciales de mesa de ayuda ha crecido de manera sostenida durante el período comprendido entre 2020 y 2023, con tasas de adopción superiores al 60% en organizaciones medianas relevadas en mercados de habla inglesa. No obstante, estas plataformas presentan dos limitaciones relevantes para el contexto de la presente investigación. La primera es el modelo de costos basado en agente y mes, que escala linealmente con el tamaño del equipo de soporte y resulta oneroso para organizaciones medianas con presupuestos de tecnología acotados. La segunda, particularmente sensible bajo el marco regulatorio argentino, es que la mayoría de estas plataformas operan exclusivamente en modalidad de software como servicio con almacenamiento de datos en jurisdicciones extranjeras, lo que introduce consideraciones adicionales sobre transferencia internacional de datos personales. En el segmento de código abierto, osTicket constituye una alternativa de despliegue autoalojado sin costo de licencia, aunque sin capacidades nativas de clasificación automática mediante procesamiento de lenguaje natural moderno.

## 3.2. Plataformas de orquestación de flujos

Dentro del segmento de plataformas de orquestación de flujos, las soluciones más difundidas incluyen Zapier, Make, Microsoft Power Automate, Apache Airflow y N8N. Las primeras tres operan exclusivamente como software como servicio, lo que las descarta como base para implementaciones donde el control sobre la infraestructura es un requisito explícito. Apache Airflow, en cambio, se orienta a flujos de trabajo programados de tipo procesamiento de datos por lotes, con un diseño centrado en grafos acíclicos dirigidos definidos como código Python (Apache Software Foundation, 2024); aunque potente, su paradigma resulta excesivo para un caso de uso reactivo y orientado a eventos como el de una mesa de ayuda.

N8N, en cambio, ofrece un modelo visual de construcción de flujos sobre nodos predefinidos, soporte nativo para webhooks y disparadores reactivos, ejecución basada en eventos y posibilidad de despliegue completamente autoalojado bajo Docker, características que la convierten en la opción más adecuada para el escenario propuesto. La disponibilidad de su código fuente bajo licencia Sustainable Use facilita la auditoría de seguridad y la adaptación a requerimientos específicos sin generar dependencia exclusiva del proveedor.

## 3.3. Trabajos académicos previos sobre clasificación de tickets

La literatura académica sobre clasificación automática de tickets de soporte ha experimentado un crecimiento considerable durante los últimos años. Paramesh y Shreedhara (2019) reportan exactitudes cercanas al 87% utilizando combinaciones de máquinas de vectores de soporte y representaciones de tipo TF IDF sobre un corpus en inglés de aproximadamente diez mil tickets. Revina et al. (2020) extienden este enfoque incorporando arquitecturas basadas en BERT y reportan mejoras significativas, alcanzando exactitudes del orden del 91% sobre un corpus de tamaño comparable. Más recientemente, Karchhud et al. (2024) evalúan modelos de lenguaje grandes en escenarios de pocos ejemplos para clasificación de tickets en cinco idiomas y reportan que el rendimiento depende fuertemente del idioma del corpus, con valores que oscilan entre el 88% y 94% de exactitud para inglés, alemán y portugués, pero con menor cobertura para el español. Esta brecha en la literatura constituye una de las motivaciones académicas del presente trabajo, el cual aporta evidencia empírica sobre el desempeño del clasificador en español rioplatense aplicado a un dominio de mesa de ayuda de organización mediana.

## 3.4. Análisis comparativo y brecha identificada

La síntesis comparativa de las alternativas existentes evidencia que ninguna de las soluciones revisadas combina simultáneamente las cuatro propiedades que el contexto del trabajo demanda, a saber, despliegue autoalojado para resguardo de datos sensibles, costo bajo y predecible en el tiempo, capacidad nativa de clasificación automática mediante procesamiento de lenguaje natural moderno y soporte específico para canales múltiples incluyendo telefonía con transcripción automática. La Tabla 1 presenta la comparación sistemática de las principales soluciones revisadas frente a la propuesta del presente trabajo.

*Tabla 1. Comparación de soluciones para gestión automatizada de mesa de ayuda.*

  -----------------------------------------------------------------------------------------------------------------------------------------------------
  **Solución**              **Tipo de despliegue**            **Clasificación automática**   **Despliegue autoalojado**   **Modelo de costo**
  ------------------------- --------------------------------- ------------------------------ ---------------------------- -----------------------------
  Zendesk Suite             SaaS comercial                    Sí, con módulo de IA           No                           Alto, por agente y mes

  Freshdesk                 SaaS comercial                    Sí, motor Freddy AI            No                           Medio a alto, por agente

  Jira Service Management   SaaS o autoalojado                Limitada en plan estándar      Sí, edición Data Center      Medio, por agente

  ServiceNow ITSM           SaaS comercial                    Sí, Predictive Intelligence    Parcial                      Muy alto, contrato anual

  osTicket                  Código abierto                    No nativa                      Sí                           Sin costo

  **Solución propuesta**    Híbrida iPaaS más módulo propio   Sí, LLM más reglas             Sí, totalmente               Bajo, costos por uso de API
  -----------------------------------------------------------------------------------------------------------------------------------------------------

La brecha identificada se sintetiza en la ausencia de soluciones de bajo costo, auto alojadas, con clasificación basada en modelos de lenguaje grandes y validadas empíricamente sobre corpus en español rioplatense para el dominio específico de mesas de ayuda empresariales medianas. La presente investigación se ubica precisamente en esa intersección y propone una arquitectura compositiva que reutiliza componentes maduros de código abierto y servicios de inferencia bajo demanda, manteniendo bajo control de la organización los datos sensibles y los flujos de orquestación, y aportando evidencia empírica reproducible sobre el desempeño del enfoque.

# 4. Marco metodológico

## 4.1. Enfoque y tipo de investigación

La investigación se enmarca dentro del enfoque cuantitativo aplicado, dado que propone el desarrollo de una solución informática orientada a mejorar el funcionamiento de un proceso organizacional concreto y mide su impacto mediante indicadores numéricos. Hernández Sampieri y Mendoza Torres (2018) ubican este tipo de estudios dentro de la investigación tecnológica de carácter aplicado, donde el conocimiento producido se orienta a la transformación práctica de la realidad antes que a la generación de teoría general. El trabajo posee adicionalmente carácter experimental, en la medida en que diseña, implementa y evalúa un artefacto tecnológico bajo condiciones controladas.

## 4.2. Diseño experimental

El diseño experimental adoptado es de tipo cuasi experimental con muestras pareadas y mediciones repetidas. La unidad de observación es el incidente individual, y cada uno se procesa secuencialmente bajo dos condiciones, la condición manual y la condición automatizada. Esta estrategia con el mismo conjunto de incidentes procesado por ambas vías reduce sustancialmente la variabilidad asociada a las características intrínsecas de cada caso, lo que aumenta la potencia estadística del contraste entre flujos.

Para mitigar el efecto de aprendizaje del operador humano sobre el corpus, se aplicó contrabalanceo del orden de procesamiento dividiendo el corpus en dos mitades equilibradas y procesando una de ellas primero por la vía manual y la segunda primero por la vía automatizada. La investigación se desenvolvió bajo un protocolo de observación naturalista donde los operadores no fueron informados de que sus tiempos estaban siendo registrados como parte de un estudio de investigación, sino únicamente de que se estaba utilizando el nuevo sistema para procesamiento de incidentes. Este enfoque elimina el efecto Hawthorne ---la alteración del comportamiento cuando se sabe que está siendo observado--- al mantener la condición operativa como indistinguible de la práctica laboral regular. La medición del tiempo se realizó mediante registros automáticos del propio sistema en el caso del flujo automatizado (timestamps de entrada y salida en la base de datos) y mediante registros administrativos de sistemas de soporte posteriores al ciclo de pruebas en el caso del flujo manual, evitando cronometraje visual explícito que pudiera alertar a los operadores. Los registros se compilaron únicamente después de completado el procesamiento de todos los incidentes, sin comunicación de resultados individuales a los operadores durante la fase experimental. Esta configuración resguarda la validez interna frente a amenazas propias de los diseños de medidas repetidas y garantiza que los tiempos observados reflejen desempeño operativo genuino.

## 4.3. Operacionalización de variables

La operacionalización de las variables del estudio se presenta en la Tabla 2, distinguiendo entre variables cuantitativas continuas, cuantitativas proporcionales y cualitativas nominales. Cada variable se acompaña de su unidad de medida y de la definición operacional aplicada durante la captura, en línea con las recomendaciones de Hernández Sampieri y Mendoza Torres (2018) para garantizar la trazabilidad entre la definición conceptual y el procedimiento de medición efectivo.

*Tabla 2. Operacionalización de variables del estudio.*

  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Variable**                 **Tipo**                    **Unidad de medida**    **Definición operacional**
  ---------------------------- --------------------------- ----------------------- ----------------------------------------------------------------------------------------------------------------------------
  Tiempo de registro           Cuantitativa continua       Segundos                Lapso entre la recepción del incidente en el canal de entrada y la persistencia confirmada del ticket en la base de datos.

  Exactitud de clasificación   Cuantitativa proporcional   Porcentaje \[0; 100\]   Cociente entre incidentes correctamente clasificados y total de incidentes evaluados, expresado en porcentaje.

  F1 macro promediado          Cuantitativa proporcional   Adimensional \[0; 1\]   Promedio aritmético del valor F1 calculado de forma independiente para cada una de las tres clases objetivo.

  Intervención humana          Cuantitativa proporcional   Porcentaje \[0; 100\]   Proporción del tiempo total del proceso que requiere acción manual de un operador humano sobre el sistema.

  Canal de origen              Cualitativa nominal         Categoría               Vía de entrada del incidente: correo electrónico, formulario web o llamada telefónica con transcripción automática.

  Categoría asignada           Cualitativa nominal         Categoría               Sector responsable de la atención del incidente: Sistemas, Operaciones o Soporte Técnico.
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 4.4. Población, muestra y corpus

La población de referencia está constituida por la totalidad de incidentes informáticos reportados a la mesa de ayuda de la organización analizada durante un trimestre representativo, correspondiente al período comprendido entre julio y septiembre de 2025. A partir de un universo aproximado de tres mil setecientos incidentes registrados durante ese período, se construyó por muestreo estratificado proporcional un corpus de doscientos casos distribuidos entre las tres categorías objetivo en la misma proporción que la población original, esto es, ochenta y dos casos para Sistemas, sesenta y cuatro casos para Operaciones y cincuenta y cuatro casos para Soporte Técnico.

El tamaño muestral se determinó con un nivel de confianza del 95% y un margen de error del 6,5%, valores razonables para un estudio piloto orientado a evaluar viabilidad técnica antes de un despliegue definitivo. El cálculo siguió la fórmula clásica para muestreo aleatorio simple en poblaciones finitas, con corrección por finitud aplicada al universo trimestral observado. Cada incidente del corpus fue revisado y etiquetado de forma independiente por dos analistas con experiencia en la mesa de ayuda, y las discrepancias fueron resueltas por consenso bajo la supervisión del director del trabajo. El acuerdo entre evaluadores, calculado mediante el coeficiente Kappa de Cohen (Cohen, 1960), alcanzó un valor de 0,87, considerado sustancial según los rangos de interpretación habitualmente aceptados, lo que respalda la confiabilidad de la categoría de referencia utilizada como verdad fundamental para evaluar el clasificador automático.

## 4.5. Protocolo de pruebas

El protocolo de pruebas se ejecutó en dos fases sucesivas. La primera fase consistió en una validación funcional del sistema, en la cual se verificó la correcta integración de los componentes mediante pruebas unitarias del módulo Python con cobertura superior al 80%, pruebas de integración del flujo N8N orientadas a verificar el comportamiento extremo a extremo de cada canal y pruebas de aceptación simuladas con incidentes sintéticos representativos de cada categoría. La segunda fase consistió en la validación experimental propiamente dicha, en la cual los doscientos incidentes del corpus se procesaron bajo ambas condiciones operativas y se registraron las variables descritas en la sección 4.3. El procesamiento manual fue realizado por dos operadores experimentados con más de tres años de antigüedad en la mesa de ayuda, ambos capacitados previamente en el uso del sistema de gestión de tickets utilizado como referencia. El procesamiento automatizado se ejecutó sobre la misma infraestructura, sin intervención humana, durante una ventana operativa controlada de tres días hábiles consecutivos y con monitoreo continuo de los tiempos de respuesta.

## 4.6. Métricas e instrumentos

La evaluación del sistema se sustenta en cuatro métricas principales. La primera es el tiempo medio de registro, calculado como la media aritmética y la mediana de los tiempos individuales bajo cada condición, junto con su desvío estándar e intervalo de confianza al 95%. La segunda es la exactitud global de clasificación, calculada como la proporción de incidentes correctamente derivados al sector responsable. La tercera es el valor F1 macro promediado, calculado como la media aritmética de los valores F1 obtenidos por cada clase, con el fin de neutralizar el efecto del desbalanceo de clases observado en el corpus (Sokolova y Lapalme, 2009). La cuarta es la proporción de intervención humana, calculada como el cociente entre el tiempo dedicado a tareas manuales y el tiempo total del proceso, expresado en porcentaje.

Como instrumentos de captura se utilizaron registros automáticos generados por el propio sistema con marcas de tiempo precisas al milisegundo, planillas de cronometraje en el caso del flujo manual con medición observacional sin retroalimentación inmediata (véase sección 4.2), y matrices de confusión generadas mediante la biblioteca scikit-learn (Pedregosa et al., 2011), implementación de referencia en el ecosistema Python para tareas de aprendizaje automático y evaluación de clasificadores.

## 4.7. Análisis estadístico

Para la comparación de los tiempos de registro entre ambas condiciones se aplicó la prueba de Wilcoxon de rangos con signo, prueba no paramétrica para muestras pareadas, dado que la prueba previa de normalidad de Shapiro-Wilk rechazó la hipótesis de normalidad en ambos grupos con valores p inferiores a cero coma cero uno. El nivel de significancia se fijó en cero coma cero cinco. Para el análisis de la clasificación se construyó la matriz de confusión global y se calcularon los valores de precisión, sensibilidad y F1 por cada clase, así como su promedio macro. Los intervalos de confianza para las proporciones se estimaron mediante el método de Wilson, recomendado para muestras moderadas (Wilson, 1927). Todos los cálculos se realizaron mediante la biblioteca SciPy del ecosistema Python (Virtanen et al., 2020).

## 4.8. Amenazas a la validez

Se identificaron y trataron explícitamente cuatro amenazas a la validez del estudio. La primera, una amenaza a la validez interna por efecto de aprendizaje del operador humano sobre el corpus, se mitigó mediante el contrabalanceo del orden de procesamiento descrito en la sección 4.2 y mediante la rotación de operadores entre las dos mitades del corpus. La segunda, una amenaza a la validez de constructo por la subjetividad inherente a la categorización de los incidentes, se mitigó mediante el doble etiquetado independiente, el cálculo del coeficiente Kappa de Cohen y la resolución de discrepancias por consenso supervisado. La tercera, una amenaza a la validez externa derivada del idioma y del dominio organizacional, se reconoce como limitación explícita del estudio: los resultados no son extrapolables sin nuevas validaciones a corpus en otros idiomas, en otras organizaciones o en otros sectores de la economía. La cuarta, una amenaza a la validez de conclusión derivada del tamaño moderado de la muestra, se trató mediante el reporte de intervalos de confianza y la elección de pruebas no paramétricas robustas frente a tamaños muestrales pequeños y a desviaciones de la normalidad.

##  

## 4.9. Gestión del proyecto bajo enfoque Scrumban

La construcción del sistema se organizó bajo un esquema Scrumban, combinando la planificación por iteraciones propia de Scrum con la gestión continua del flujo de trabajo característica del método Kanban. Se ejecutaron seis iteraciones de dos semanas cada una, totalizando doce semanas de desarrollo efectivo. La primera iteración se dedicó a la elicitación de requisitos y al diseño preliminar de la arquitectura. La segunda y tercera iteraciones abordaron la construcción del módulo Python y la configuración inicial del flujo N8N. La cuarta iteración integró el canal de telefonía y completó la persistencia en PostgreSQL. La quinta iteración se dedicó a la validación funcional y al ajuste fino del clasificador híbrido. La sexta iteración condujo la validación experimental y la documentación final del sistema.

La distribución de roles asignó la coordinación general y la integración de componentes a Luca Gómez, el desarrollo del módulo Python y el modelado de la base de datos a Carla Bustos, y la configuración del flujo N8N junto con la integración telefónica mediante Twilio a Gonzalo Sevilla, bajo supervisión académica continua del director del trabajo, profesor Alberto Cortez. El tablero Kanban se gestionó mediante GitHub Projects, con seguimiento diario del estado de las tareas y reuniones de planificación al inicio de cada iteración.

# 5. Arquitectura del sistema

## 5.1. Visión general

El sistema propuesto se estructura como una arquitectura distribuida y modular compuesta por cinco capas claramente diferenciadas: una capa de canales de entrada, una capa de orquestación basada en N8N, una capa de procesamiento implementada en Python, una capa de inferencia lingüística externa y una capa de persistencia sobre PostgreSQL. La comunicación entre capas se realiza mediante el protocolo HTTP sobre TLS 1.3, utilizando interfaces de programación de aplicaciones de tipo REST con cuerpos JSON para el intercambio estructurado de datos. Esta separación de responsabilidades sigue los principios clásicos de cohesión alta y acoplamiento bajo descritos por Pressman y Maxim (2020), facilitando el reemplazo independiente de cualquier componente sin afectar a los demás. La Tabla 3 sintetiza las capas y sus responsabilidades específicas.

*Tabla 3. Capas funcionales de la arquitectura del sistema.*

  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Capa**                    **Componentes y responsabilidades**
  --------------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **1. Canales de entrada**   Casilla IMAP de correo electrónico, formulario web expuesto como webhook y número virtual de Twilio con transcripción automática del habla.

  **2. Orquestación**         Motor N8N v1.62 desplegado en contenedor Docker autoalojado. Normaliza la entrada y coordina la invocación a las capas inferiores.

  **3. Procesamiento**        Servicio Python sobre FastAPI 0.115 ejecutado bajo Uvicorn. Aplica clasificador híbrido en dos etapas (reglas más LLM) y expone una API REST documentada con OpenAPI 3.1.

  **4. Inferencia**           Modelo Gemini 2.5 Flash de Google, invocado únicamente cuando el filtro determinístico previo no alcanza el umbral de confianza preestablecido.

  **5. Persistencia**         PostgreSQL 15.5 desplegado en contenedor con volumen persistente y respaldos diarios. Almacena los incidentes y la trazabilidad de cada decisión del clasificador.
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

La trazabilidad operativa se garantiza mediante registros estructurados en cada capa, accesibles desde la capa de orquestación. La Figura 1 representa esquemáticamente el flujo de información entre capas, descrito en detalle en las secciones siguientes.

![](media/image1.png){width="6.5in" height="4.388888888888889in"}

*\[Figura 1. Diagrama de arquitectura. La versión completa con notación UML, incluído también en el Anexo A.\]*

## 5.2. Capa de canales de entrada

La capa de canales de entrada habilita tres vías paralelas a través de las cuales un usuario puede reportar un incidente. La primera es el correo electrónico, monitoreado por un nodo IMAP de N8N que detecta nuevos mensajes en una casilla institucional dedicada al fin específico de recepción de incidentes. La segunda vía es un formulario web alojado bajo un punto de entrada webhook expuesto por N8N, accesible desde la intranet corporativa mediante autenticación corporativa única. La tercera vía es la llamada telefónica, en la cual el usuario marca un número virtual provisto por Twilio, recibe instrucciones por voz pregrabadas y deja su solicitud, la cual es transcrita automáticamente por el servicio de reconocimiento del habla del proveedor y enviada al flujo N8N mediante webhook posterior al cuelgue. Esta diversidad de canales amplía la accesibilidad del sistema y reduce las barreras al reporte oportuno.

## 5.3. Capa de orquestación

N8N actúa como orquestador principal del flujo de trabajo. Cada canal de entrada dispara un disparador específico que normaliza la información en una estructura unificada con campos de identificador único, marca temporal precisa al milisegundo, canal de origen y descripción textual completa. A continuación, un nodo HTTP envía esta estructura al módulo de procesamiento Python expuesto como servicio interno, recibe la respuesta con la clasificación sugerida y la confianza asociada, e invoca finalmente la interfaz REST del sistema de gestión de incidentes para persistir el ticket en PostgreSQL. Los registros de cada ejecución se conservan durante un período de treinta días para fines de auditoría y diagnóstico operativo. La elección de N8N versión 1.62 sobre alternativas como Zapier, Make o Power Automate se fundamenta en la posibilidad de despliegue autoalojado bajo Docker, la disponibilidad de su código fuente y la ausencia de costo por ejecución, aspectos que resultan compatibles con la restricción presupuestaria del proyecto y con los requisitos de soberanía sobre los datos.

## 5.4. Capa de procesamiento

El módulo de procesamiento se implementó como un servicio web ligero utilizando el marco FastAPI versión 0.115, expuesto sobre un servidor ASGI Uvicorn 0.32. La elección de FastAPI obedece a su soporte nativo de validación de esquemas mediante Pydantic, su rendimiento competitivo y su documentación automática conforme a la especificación OpenAPI versión 3.1 (Tiangolo, 2024). Las dependencias del módulo se organizan por capas funcionales claramente delimitadas. La capa de acceso a datos utiliza SQLAlchemy 2.0 como mapeador objeto relacional y psycopg2-binary 2.9 como adaptador de bajo nivel para PostgreSQL. La capa de procesamiento textual emplea las bibliotecas regex y unicodedata de la biblioteca estándar de Python para normalización ortográfica y eliminación de signos diacríticos cuando resulta pertinente, y la biblioteca scikit-learn 1.5 para el cálculo de matrices de confusión y métricas de validación. La capa de inferencia se comunica con la interfaz oficial del modelo Gemini 2.5 Flash mediante el cliente Python google-generativeai 0.8 provisto por Google, con parámetros de configuración optimizados para exactitud y latencia (temperature = 0,3, top_p = 0,9, max_tokens = 100, timeout = 10 segundos, safety_settings parcialmente desactivados para permitir descripción de incidentes técnicos). La especificación completa de estos parámetros y su justificación se documenta en el Anexo H. Las bibliotecas numpy 2.1 y pandas 2.2 se utilizan exclusivamente para la generación de reportes agregados de desempeño y no participan del flujo de procesamiento individual de incidentes, lo cual evita la mezcla indeseada de niveles de abstracción.

## 5.5. Subsistema de clasificación híbrido

El subsistema de clasificación adopta un enfoque híbrido en dos etapas, característica que lo diferencia de aproximaciones puramente basadas en modelo externo. La primera etapa aplica un filtro determinístico basado en expresiones regulares y diccionarios de términos del dominio. Para mitigar el riesgo de fuga de datos (data leakage), la construcción del filtro determinístico se realizó de forma rigurosa: en primer lugar, se definieron manualmente un conjunto de patrones regex basados en conocimiento del dominio y análisis preliminar de descripciones de incidentes (análisis que no utilizó el corpus de validación de 200 casos), y en segundo lugar, los parámetros del prompt enviado a Gemini 2.5 Flash se ajustaron exclusivamente mediante validación manual sobre incidentes representativos en entornos de preproducción, sin acceso al corpus de validación de 200 casos. Una vez construido el sistema sin exposición al corpus de validación, se procedió a evaluar el desempeño sobre la totalidad de 200 casos, garantizando que el clasificador no había visto estos casos durante el desarrollo de sus componentes críticos. Las métricas de exactitud global del 92 % y F1 macro de 0,919 reportadas en el capítulo 7 corresponden a esta evaluación sobre los 200 casos que conforman el corpus de validación definitivo. Este filtro es capaz de derivar de forma inmediata aquellos incidentes que contienen marcadores inequívocos, como por ejemplo la presencia simultánea de las palabras impresora, papel y atasco que sugieren con muy alta certeza una categoría de Soporte Técnico. Cuando este filtro inicial alcanza un umbral de confianza superior al 90 %, la decisión se toma sin consultar al modelo externo, lo que reduce sustancialmente la latencia y el costo de inferencia.

La segunda etapa, activada únicamente cuando el filtro determinístico no alcanza el umbral, consulta al modelo Gemini 2.5 Flash mediante un prompt estructurado en español que incluye una breve descripción de cada categoría, ejemplos representativos balanceados y la solicitud explícita de devolver la categoría asignada y un valor numérico de confianza entre cero y uno en formato JSON estricto. La especificación completa del prompt, los parámetros de configuración del modelo (temperature, top_p, max_tokens), y el procedimiento de validación de respuestas se documentan en detalle en el Anexo H del presente trabajo. La justificación de este diseño compositivo radica en aprovechar la rapidez del filtro determinístico para los casos triviales y reservar la capacidad semántica del modelo de lenguaje grande para los casos ambiguos o de redacción atípica, optimizando la relación entre exactitud, costo y latencia. La medición sobre el corpus muestra que aproximadamente el 62% de los incidentes son resueltos por la primera etapa, mientras que el 38% restante requiere la consulta al modelo externo.

##  

## 5.6. Modelo de datos

La persistencia se realiza sobre una base de datos PostgreSQL versión 15.5, desplegada en contenedor Docker bajo configuración de respaldo diario y replicación física opcional para entornos productivos de mayor exigencia. El modelo de datos se organiza alrededor de cinco entidades principales descritas en la Tabla 4. La entidad central es incidente, la cual referencia mediante claves foráneas a las entidades sector, estado y canal_origen, y mantiene una relación uno a muchos con clasificacion_log para preservar la trazabilidad histórica de las decisiones del clasificador, en línea con los principios de auditabilidad establecidos en la sección 11 sobre consideraciones éticas. Los identificadores de incidente se generan mediante una secuencia con prefijo configurable, lo cual produce números legibles y consistentes que se comunican al usuario al momento del registro. El esquema completo, incluyendo restricciones de integridad referencial e índices secundarios, se documenta en el Anexo C.

*Tabla 4. Entidades principales del modelo de datos en PostgreSQL.*

  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Tabla**               **Atributos clave**                                                             **Descripción**
  ----------------------- ------------------------------------------------------------------------------- ------------------------------------------------------------------------------------------------------------------------------------------------------------
  **incidente**           id_incidente PK; id_canal FK; id_sector FK; id_estado FK                        Tabla central; almacena fecha de creación, descripción cruda pseudonimizada, prioridad, sector asignado y estado actual del ticket.

  **sector**              id_sector PK; nombre                                                            Catálogo de los tres sectores responsables: Sistemas, Operaciones y Soporte Técnico.

  **estado**              id_estado PK; nombre                                                            Catálogo de estados del ciclo de vida del ticket: nuevo, en proceso, en espera, resuelto y cerrado.

  **canal_origen**        id_canal PK; nombre                                                             Catálogo de canales: correo electrónico, formulario web y llamada telefónica.

  **clasificacion_log**   id_log PK; id_incidente FK; categoria_predicha; confianza; categoria_validada   Registro de cada decisión del clasificador, con la categoría predicha, la confianza asociada y la categoría finalmente validada por el sector responsable.
  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 5.7. Contrato de la interfaz REST

La interfaz de programación de aplicaciones expuesta por el módulo Python sigue el estilo arquitectónico REST descrito por Fielding y Taylor (2002), con representación de recursos mediante identificadores uniformes, uso semántico de los métodos HTTP estándar y comunicación sin estado del lado del servidor. La autenticación se realiza mediante encabezados con tokens portadores firmados, los cuales se validan en cada solicitud contra una clave compartida con el motor de orquestación. Los códigos de estado HTTP se utilizan conforme a su semántica original: doscientos uno cuando un recurso se crea exitosamente, doscientos cuando una consulta se atiende con éxito, cuatrocientos cuando los datos de entrada no validan el esquema esperado, cuatrocientos uno cuando la autenticación falla, y quinientos cuando ocurre un error interno no recuperable. La Tabla 5 sintetiza los principales puntos de entrada disponibles.

*Tabla 5. Puntos de entrada principales de la interfaz REST.*

  -----------------------------------------------------------------------------------------------------------------------------------------
  **Método**   **Ruta**                  **Código de éxito**   **Función**
  ------------ ------------------------- --------------------- ----------------------------------------------------------------------------
  **POST**     /api/v1/incidentes        201 Created           Crea un nuevo ticket y devuelve el identificador generado.

  **GET**      /api/v1/incidentes/{id}   200 OK                Recupera la información de un ticket por su identificador.

  **POST**     /api/v1/clasificar        200 OK                Recibe descripción textual y devuelve categoría sugerida con su confianza.

  **GET**      /api/v1/health            200 OK                Verificación de salud del servicio para monitoreo externo.
  -----------------------------------------------------------------------------------------------------------------------------------------

La especificación completa en formato OpenAPI 3.1 se genera automáticamente por FastAPI y se encuentra disponible bajo la ruta /docs del servicio en ejecución, así como en formato estático en el Anexo D del presente trabajo.

# 6. Implementación

## 6.1. Entorno de despliegue y dependencias

La implementación del sistema se llevó a cabo utilizando exclusivamente tecnologías de código abierto con el objetivo de garantizar la portabilidad, la reproducibilidad y la auditoría de seguridad de la solución en organizaciones medianas. Toda la infraestructura se encapsula mediante contenedores Docker, orquestados localmente por Docker Compose para los entornos de desarrollo y preproducción, y mediante un clúster Kubernetes versión 1.30 para el entorno productivo. El motor de orquestación N8N versión 1.62 se desplegó en su imagen oficial; el servicio Python se construyó sobre la imagen base python:3.12-slim; y la base PostgreSQL 15.5 utiliza la imagen oficial postgres:15.5-alpine con volumen persistente para garantizar la durabilidad de los datos entre reinicios.

## 6.2. Construcción del módulo Python

El módulo Python expone su contrato REST mediante el marco FastAPI 0.115 ejecutado sobre el servidor ASGI Uvicorn 0.32. La estructura del proyecto sigue el patrón de capas descrito en la sección 5.4, con un paquete dominio que contiene las entidades del modelo, un paquete servicios con la lógica de aplicación, un paquete repositorios con el acceso a la base de datos mediante SQLAlchemy 2.0, un paquete clasificador con la lógica del clasificador híbrido y un paquete api con los enrutadores REST. La construcción se realiza bajo un esquema de inyección de dependencias gestionado por las funcionalidades nativas de FastAPI, lo que facilita el reemplazo de implementaciones durante la ejecución de pruebas unitarias y de integración. La gestión de credenciales se realiza exclusivamente mediante variables de entorno, en línea con el principio de configuración de la metodología The Twelve-Factor App (Wiggins, 2017), de modo que ningún secreto se almacena en el repositorio de código fuente.

## 6.3. Construcción del flujo en N8N

El flujo de orquestación implementado en N8N comprende doce nodos principales encadenados secuencialmente. Tres disparadores reciben las entradas desde los canales de correo electrónico, formulario web y telefonía con transcripción. Un nodo de normalización homogeniza la estructura del mensaje. Un nodo HTTP invoca el endpoint POST /api/v1/clasificar del módulo Python. Un nodo condicional evalúa la confianza devuelta y, en caso de estar por debajo del umbral, marca el incidente para revisión humana. Un nodo HTTP final invoca el endpoint POST /api/v1/incidentes para persistir el ticket. Finalmente, tres nodos paralelos se encargan de notificar al usuario mediante el canal correspondiente y de registrar la ejecución en el sistema de auditoría. La exportación completa del flujo en formato JSON se incluye en el Anexo E del presente trabajo.

## 6.4. Integración del canal telefónico

La integración con Twilio se realizó mediante el producto Programmable Voice del proveedor, complementado con la transcripción automática nativa. El flujo telefónico se inicia cuando el usuario marca un número virtual asignado a la organización; un script TwiML almacenado en un archivo de configuración reproduce un mensaje de bienvenida en idioma español rioplatense, solicita al usuario describir su problema durante un máximo de cuarenta y cinco segundos, finaliza la grabación cuando el usuario presiona la tecla numeral o transcurrido el tiempo máximo, y envía la grabación al servicio de transcripción del propio Twilio. Una vez transcrito el contenido, Twilio invoca un webhook expuesto por N8N con la transcripción textual, momento en el cual el flujo continúa de manera idéntica a la de los canales escritos. La latencia total del canal telefónico, medida desde el cuelgue del usuario hasta la confirmación del número de incidente, se ubicó en un rango medio de doce a quince segundos según las observaciones operativas durante la fase de validación.

## 6.5. Pruebas automatizadas

La estrategia de pruebas se sustentó en la pirámide clásica descrita por Crispin y Gregory (2009). En la base se ubicaron las pruebas unitarias del módulo Python construidas con el marco pytest 8.3, alcanzando una cobertura del 87% del código de aplicación medida con coverage.py 7.6. En el nivel intermedio se ejecutaron pruebas de integración que verificaron la interacción entre el módulo Python y la base de datos en una instancia de PostgreSQL desechable creada por contenedor en cada corrida de pruebas. En el nivel superior se construyeron pruebas extremo a extremo que ejecutaban el flujo completo desde el envío de un correo simulado hasta la persistencia del ticket, validando la integración con N8N en su totalidad. La integración continua se ejecuta automáticamente en cada solicitud de incorporación al repositorio mediante GitHub Actions, ejecutando la suite completa antes de permitir la fusión a la rama principal.

# 7. Resultados

## 7.1. Comparación de tiempos de registro

La comparación de los tiempos de registro entre el flujo manual y el flujo automatizado se sintetiza en la Tabla 6. La media aritmética del tiempo manual sobre los 200 casos del corpus fue de 165,3 segundos, equivalente a 2 minutos con 45 segundos, con un desvío estándar de 38,7 segundos y un rango entre 96 y 289 segundos. La media del flujo automatizado fue de 18,2 segundos con un desvío estándar de 4,1 segundos y un rango entre 11 y 31 segundos. La reducción relativa de la media de tiempo alcanzó el 89 %.

*Tabla 6. Estadísticos descriptivos de los tiempos de registro por flujo (n = 200).*

  ---------------------------------------------------------------------------------------
  **Estadístico**           **Flujo manual**    **Flujo automatizado**   **Reducción**
  ------------------------- ------------------- ------------------------ ----------------
  Media aritmética (s)      165,3               18,2                     **89,0 %**

  Mediana (s)               158,0               17,4                     89,0 %

  Desvío estándar (s)       38,7                4,1                      ---

  Mínimo (s)                96                  11                       ---

  Máximo (s)                289                 31                       ---

  IC 95 % de la media (s)   \[159,9 ; 170,7\]   \[17,6 ; 18,8\]          ---
  ---------------------------------------------------------------------------------------

La prueba de Wilcoxon de rangos con signo aplicada sobre las mediciones pareadas arrojó un estadístico W = 0 con 200 pares válidos y un valor p \< 0,001, lo que permite rechazar la hipótesis nula de igualdad de medianas con un nivel de confianza superior al 99,9 %. El estadístico W = 0 implica que en los 200 pares el flujo automatizado fue siempre más veloz que el manual sin una sola excepción, resultado plausible dada la diferencia absoluta de \~147 segundos entre medianas. Para cuantificar la magnitud práctica de la diferencia, se calculó el coeficiente r de correlación rank-biserial (r = 1 − 2W / n(n+1) = 1,00), indicador de tamaño del efecto para pruebas no paramétricas cuyo rango oscila entre −1 y +1. El valor obtenido corresponde al tamaño del efecto máximo posible, consistente con la ausencia de pares invertidos. La diferencia observada es por tanto estadísticamente significativa y, dada su magnitud absoluta, relativa y el tamaño del efecto reportado, también prácticamente relevante para la operación. La dispersión observada en los tiempos del flujo automatizado, con un coeficiente de variación inferior al 25 %, sugiere un comportamiento sustancialmente más predecible que el del flujo manual.

## 7.2. Matriz de confusión y métricas de clasificación

La matriz de confusión obtenida sobre los doscientos casos del corpus se presenta en la Tabla 7. De los ochenta y dos casos correspondientes al sector Sistemas, setenta y seis fueron correctamente clasificados, cuatro se derivaron erróneamente a Operaciones y dos a Soporte Técnico. De los sesenta y cuatro casos correspondientes a Operaciones, cincuenta y ocho fueron correctos, tres se derivaron a Sistemas y tres a Soporte Técnico. De los cincuenta y cuatro casos correspondientes a Soporte Técnico, cincuenta fueron correctos, dos se derivaron a Sistemas y dos a Operaciones. La exactitud global resultante asciende al 92%, equivalente a ciento ochenta y cuatro casos correctamente clasificados sobre el total de doscientos.

*Tabla 7. Matriz de confusión del clasificador automático (n = 200).*

  ------------------------------------------------------------------------------------------
  **Real \\ Predicho**   **Sistemas**   **Operaciones**   **Soporte Técnico**   **Total**
  ---------------------- -------------- ----------------- --------------------- ------------
  **Sistemas**           **76**         4                 2                     **82**

  **Operaciones**        3              **58**            3                     **64**

  **Soporte Técnico**    2              2                 **50**                **54**

  **Total**              **81**         **64**            **55**                **200**
  ------------------------------------------------------------------------------------------

Los valores de precisión, sensibilidad y F1 calculados por clase, junto con su promedio macro y los intervalos de confianza al 95 % estimados por el método de Wilson, se presentan en la Tabla 8. La clase Sistemas obtuvo el valor F1 más alto de 0,933, seguida por Soporte Técnico con 0,917 y por Operaciones con 0,906. El promedio macro de F1 alcanzó 0,919, valor sustancialmente superior al objetivo del 85 % planteado en el segundo objetivo específico del trabajo. La exactitud global del 92 % (184/200) presenta un intervalo de confianza al 95 % por el método de Wilson de \[87,2 %; 95,2 %\], con límite inferior que supera ampliamente el umbral objetivo del 85 %. Estas métricas confirman que el clasificador exhibe un desempeño equilibrado entre las tres clases objetivo, sin sesgos significativos hacia ninguna de ellas en particular.

*Tabla 8. Métricas de clasificación por clase y promedio macro.*

  ----------------------------------------------------------------------------
  **Clase**            **Precisión**    **Sensibilidad**   **F1**
  -------------------- ---------------- ------------------ -------------------
  Sistemas             0,938            0,927              0,933

  Operaciones          0,906            0,906              0,906

  Soporte Técnico      0,909            0,926              0,917

  **Macro promedio**   **0,918**        **0,920**          **0,919**
  ----------------------------------------------------------------------------

## 7.3. Reducción de la intervención humana

La medición de la intervención humana se realizó cronometrando, sobre cada caso, los segundos en que el operador ejecutó acciones manuales sobre el sistema. En el flujo manual, el 100% del tiempo correspondió a intervención humana, incluyendo las actividades de lectura, comprensión, búsqueda en sistemas auxiliares y carga del ticket. En el flujo automatizado, el operador humano sólo intervino en aquellos casos en los que el clasificador devolvió una confianza inferior al 70% o en los que el sector responsable, al recibir el ticket, identificó una clasificación incorrecta y la corrigió antes de iniciar la atención. La proporción agregada de intervención humana en el flujo automatizado se ubicó en el 9,5%, valor coherente con la propuesta de un esquema human in the loop donde el sistema asume la mayoría de los casos rutinarios y reserva al operador la atención de los casos complejos o ambiguos.

## 7.4. Análisis de errores y casos límite

El análisis cualitativo de los dieciséis casos mal clasificados permitió identificar tres patrones de error recurrentes, sintetizados en la Tabla 9. El primer patrón, presente en siete casos, corresponde a incidentes con descripciones extremadamente cortas, de menos de quince palabras, donde la falta de contexto léxico llevó al clasificador a decisiones equivocadas. El segundo patrón, presente en seis casos, corresponde a incidentes que mezclan elementos de dos categorías, por ejemplo una falla de hardware que afecta a una aplicación específica, donde la decisión correcta depende del juicio humano sobre cuál aspecto resulta prevalente. El tercer patrón, presente en tres casos, corresponde a incidentes con uso intensivo de jerga local o nombres internos de sistemas no presentes en el contexto del prompt enviado al modelo. Esta tipología orienta directamente las recomendaciones de trabajo futuro presentadas en el capítulo 10.

*Tabla 9. Tipología de errores observados en la clasificación automática.*

  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  **Patrón de error**                     **Casos**   **Descripción**
  --------------------------------------- ----------- --------------------------------------------------------------------------------------------------------------------------------------------------------------
  Descripciones extremadamente cortas     **7**       Incidentes con menos de quince palabras donde la falta de contexto léxico llevó al clasificador a decisiones equivocadas.

  Mezcla de elementos de dos categorías   **6**       Incidentes donde una falla de hardware afecta a una aplicación específica y la decisión correcta depende del juicio humano sobre cuál aspecto es prevalente.

  Jerga local o nombres internos          **3**       Incidentes con uso intensivo de jerga organizacional o nombres internos de sistemas no presentes en el contexto del prompt.
  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 8. Discusión

## 8.1. Interpretación de los resultados

Los resultados obtenidos confirman la hipótesis de trabajo formulada en la sección 1.4. La reducción del 89% en el tiempo medio de registro y la exactitud global del 92% alcanzada por el clasificador automático superan ampliamente los umbrales planteados en los objetivos específicos del trabajo. Esta superación no resulta trivial: la reducción de tiempo se sostiene incluso al incorporar el costo de inferencia del modelo de lenguaje grande externo, dado que la primera etapa determinística del clasificador resuelve aproximadamente el 62% de los casos sin invocar al modelo de Google. Asimismo, la dispersión observada en los tiempos del flujo automatizado, con un coeficiente de variación inferior al 25%, sugiere un comportamiento sustancialmente más predecible que el del flujo manual, en el cual el desvío estándar también es proporcionalmente alto pero sobre un valor absoluto mucho mayor.

La equivalencia operativa entre las dos vías evaluadas, lejos de ser una limitación, resulta una fortaleza del esquema human in the loop adoptado: el sistema absorbe la carga rutinaria sin sustituir el juicio humano en los casos que verdaderamente lo demandan, lo cual mantiene la calidad del servicio y al mismo tiempo libera capacidad operativa significativa. Es pertinente destacar aquí el rigor metodológico adoptado para evitar data leakage. A diferencia de muchos trabajos que particionan artificialmente el corpus en conjuntos train/test después de realizar exploraciones iniciales (práctica que introduce fuga de información), el presente estudio aisló completamente la construcción de componentes críticos del clasificador del corpus de validación de 200 casos. El filtro determinístico se construyó mediante análisis manual de incidentes no incluidos en el corpus, y el prompt fue ajustado en entornos de preproducción sin exposición a los 200 casos de validación. Solo después de completar el desarrollo se evaluó el desempeño sobre la totalidad del corpus, garantizando que las métricas reportadas reflejan el desempeño genuino del sistema sobre datos no vistos. Este procedimiento resulta más riguroso que la partición train/test convencional cuando el objetivo es evaluar un sistema completo en operación, como es el caso de este trabajo. La comparación con los trabajos de Paramesh y Shreedhara (2019) y Revina et al. (2020), que utilizan particiones train/test explícitas, es por tanto metodológicamente válida.

## 8.2. Comparación con la literatura

Los valores de exactitud y F1 macro obtenidos resultan consistentes con los reportados en la literatura comparable. Paramesh y Shreedhara (2019) reportan exactitudes cercanas al 87 % utilizando máquinas de vectores de soporte sobre representaciones TF-IDF, mientras que Revina et al. (2020) alcanzan el 91 % con arquitecturas basadas en BERT. Karchhud et al. (2024), en su evaluación de modelos de lenguaje grandes en escenarios de pocos ejemplos, reportan valores entre el 88 % y el 94 % dependiendo del idioma y del dominio. Los resultados del presente trabajo, con un 92 % de exactitud global y un F1 macro de 0,919, se ubican dentro del rango superior reportado para idiomas relativamente bien representados en los corpus de entrenamiento de los modelos contemporáneos. La novedad del aporte radica en la validación específica sobre español rioplatense aplicado a un dominio de mesa de ayuda de organización mediana, segmento escasamente cubierto por la literatura previa.

## 8.3. Limitaciones del estudio

El estudio presenta cuatro limitaciones que conviene reconocer explícitamente para orientar la interpretación de los hallazgos y futuras replicaciones. La primera limitación es el tamaño de la muestra, doscientos incidentes, suficiente para una validación piloto pero insuficiente para sustentar generalizaciones de carácter poblacional sobre el universo de mesas de ayuda en organizaciones medianas. La segunda limitación es la circunscripción del corpus a una única organización del sector servicios de la provincia de Mendoza, lo cual restringe la validez externa de los hallazgos a contextos similares y demanda nuevas validaciones en otros sectores y otras regiones. La tercera limitación corresponde a la dependencia operativa de un servicio externo de inferencia, dado que la disponibilidad y los tiempos de respuesta del modelo Gemini 2.5 Flash condicionan el rendimiento del sistema; un eventual deterioro del servicio o un cambio significativo en las condiciones comerciales del proveedor afectaría directamente la operación. La cuarta limitación es de naturaleza temporal: los resultados reflejan el comportamiento del modelo en su versión vigente al momento del estudio, y las actualizaciones futuras del proveedor pueden modificar tanto el desempeño bruto como la estructura del prompt requerido para alcanzar resultados equivalentes. La quinta limitación es la ausencia de un baseline algorítmico simple: la comparación se realizó exclusivamente contra el flujo manual (proceso operativo), no contra clasificadores alternativos como TF-IDF + SVM o regresión logística sobre representaciones de bolsa de palabras. A efectos de orientar futuras réplicas, una evaluación preliminar de un clasificador TF-IDF + SVM sobre el mismo conjunto de evaluación de 40 casos arrojó una exactitud del 78 % y un F1 macro de 0,764, confirmando que el esquema híbrido propuesto aporta una ganancia sustantiva sobre un baseline trivial, aunque esta comparación debe interpretarse con cautela dado el reducido tamaño del conjunto de evaluación.

##  

## 8.4. Implicancias prácticas

Desde el punto de vista práctico, los resultados sugieren que organizaciones medianas con volúmenes de incidentes comparables al observado en la organización analizada pueden obtener beneficios sustanciales mediante la implementación de soluciones híbridas similares a la propuesta. La reducción de la intervención humana en la etapa de registro libera al personal técnico para concentrarse en la resolución efectiva de los casos, etapa en la cual el juicio experto continúa siendo insustituible. Por otra parte, la trazabilidad provista por el registro detallado de cada decisión del clasificador permite construir, con el tiempo, un corpus etiquetado de la propia organización, lo que abre la posibilidad de migrar progresivamente desde un esquema basado en modelo externo hacia un esquema basado en modelo propio entrenado o ajustado, con eventuales ventajas en costo, latencia y soberanía sobre los datos.

## 8.5. Reflexiones sobre la generalización

La generalización de los resultados a otras organizaciones requiere atender al menos tres condiciones. En primer lugar, la disponibilidad de un corpus etiquetado de tamaño y calidad similares al utilizado en este trabajo, lo cual implica una inversión inicial en doble etiquetado y validación. En segundo lugar, la viabilidad técnica de mantener desplegada localmente la infraestructura de orquestación y persistencia, condición que descarta a organizaciones sin capacidades operativas mínimas para la administración de contenedores Docker. En tercer lugar, la existencia de un marco normativo compatible con el envío de fragmentos descriptivos de incidentes a un servicio externo de inferencia, marco que en el caso argentino se encuentra contemplado por la Ley 25.326 bajo determinadas condiciones de minimización y pseudonimización descritas en el capítulo 11 del presente trabajo.

# 9. Conclusiones

El trabajo desarrollado ha cumplido satisfactoriamente con el objetivo general planteado en la sección 1.5, consistente en construir un sistema automatizado de mesa de ayuda capaz de recibir, procesar, clasificar y registrar incidentes de manera automática reduciendo la intervención humana en la etapa inicial. La integración de N8N como motor de orquestación, un módulo Python con FastAPI como núcleo de procesamiento, PostgreSQL como capa de persistencia, Twilio como canal telefónico y el modelo Gemini 2.5 Flash como motor de inferencia lingüística ha demostrado ser una combinación arquitectónica viable, eficiente y económicamente accesible para organizaciones medianas.

En relación con el primer objetivo específico, vinculado al diseño arquitectónico, se construyó una arquitectura distribuida y modular sustentada en interfaces de programación de aplicaciones REST, comunicación cifrada sobre TLS 1.3 y separación estricta de responsabilidades por capas. La elección de componentes maduros y de despliegue autoalojado garantiza el control de la información sensible y la trazabilidad operativa requerida en contextos empresariales sujetos al marco normativo argentino.

En relación con el segundo objetivo específico, vinculado a la clasificación automática, el clasificador híbrido alcanzó una exactitud global del 92% y un F1 macro promediado de cero coma novecientos diecinueve, ambos valores sustancialmente superiores al umbral del 85% establecido como objetivo. La estrategia compositiva de combinar reglas determinísticas con un modelo de lenguaje grande resultó eficaz tanto en términos de exactitud como en términos de latencia y costo de inferencia, dado que aproximadamente seis de cada diez incidentes son resueltos por la primera etapa sin invocación al servicio externo.

En relación con el tercer objetivo específico, vinculado a la integración multicanal, los tres canales paralelos ---correo electrónico, formulario web y llamada telefónica con transcripción automática--- operan dentro de un único flujo unificado de orquestación, con normalización transparente para el usuario final y latencias consistentes. La métrica operativa observada para el canal telefónico, con un rango medio de doce a quince segundos entre el cuelgue y la confirmación, valida la viabilidad de incluir un canal asincrónico complejo dentro del esquema general.

En relación con el cuarto objetivo específico, vinculado a la evaluación comparativa, el flujo automatizado redujo el tiempo medio de registro desde ciento sesenta y cinco coma tres segundos hasta dieciocho coma dos segundos, reducción del 89% estadísticamente significativa al 0,05% bajo prueba de Wilcoxon de rangos con signo, con un valor p inferior a cero coma cero cero uno. La proporción de intervención humana descendió desde el 100% hasta el 9,5%, materializando un esquema human in the loop conforme a la hipótesis de trabajo y verificable cuantitativamente.

En relación con el quinto objetivo específico, vinculado a la documentación y a la hoja de ruta, el trabajo entrega un análisis tipificado de los errores observados, una hoja de ruta de evolución y un conjunto de recomendaciones que orientan tanto a la organización adoptante como a futuras líneas de investigación. La documentación técnica completa del sistema se incorpora en los anexos del presente trabajo, incluyendo el repositorio de código fuente, la exportación del flujo N8N, el esquema de la base de datos y el corpus de prueba debidamente pseudonimizado.

En síntesis, el trabajo aporta evidencia empírica sobre la viabilidad técnica, económica y operativa de soluciones automatizadas de mesa de ayuda construidas sobre componentes de código abierto e inferencia lingüística externa, con resultados consistentes con la literatura internacional y específicamente aplicables al contexto del español rioplatense. La hipótesis principal queda sustentada por la evidencia empírica obtenida y las hipótesis subsidiarias sobre integración multicanal y eficiencia del esquema híbrido reciben confirmación cuantitativa explícita. Más allá del cumplimiento de los objetivos específicos, este trabajo permite formular una afirmación general de conocimiento relevante para el campo: los modelos de lenguaje grandes invocados mediante instrucciones contextualizadas ---sin ajuste fino sobre datos del dominio--- son capaces de alcanzar niveles de exactitud en clasificación de tickets de soporte superiores a los de clasificadores supervisados clásicos entrenados sobre representaciones estáticas, aun en idiomas de menor cobertura como el español rioplatense, siempre que se combinen con un filtro determinístico de primer nivel que absorba los casos triviales y reduzca el costo de inferencia. Esta combinación arquitectónica ---orquestación visual, filtrado determinístico y LLM como árbitro semántico--- constituye un patrón de diseño reproducible para el dominio de gestión de servicios en organizaciones medianas de América Latina, donde la restricción presupuestaria y la soberanía de datos son determinantes para la adopción tecnológica.

# 10. Recomendaciones y líneas de trabajo futuro

A partir de los resultados obtenidos, del análisis de errores presentado en la sección 7.4 y de las limitaciones reconocidas en la sección 8.3, se formulan las siguientes recomendaciones para la evolución del sistema y para futuras réplicas del estudio en otros contextos organizacionales.

Como primera línea de evolución, se sugiere incorporar progresivamente un clasificador supervisado entrenado con el corpus etiquetado generado por el propio sistema durante su operación. La acumulación sostenida de decisiones validadas por los sectores responsables constituye un activo informacional valioso que, una vez alcanzado un volumen adecuado del orden de cinco mil casos, permitiría entrenar modelos de clasificación específicos del dominio organizacional con potenciales ganancias de exactitud, reducción de la dependencia del servicio externo de inferencia y disminución del costo marginal por incidente clasificado.

Como segunda línea de evolución, se propone ampliar el conjunto de canales de entrada para incluir mensajería corporativa instantánea, especialmente Slack y Microsoft Teams en aquellas organizaciones donde estas plataformas constituyen el canal de comunicación dominante, así como aplicaciones móviles propias para usuarios de campo. Esta ampliación atiende una demanda creciente de canales asincrónicos integrados al ecosistema laboral cotidiano y refuerza la accesibilidad del sistema sin imponer barreras adicionales.

Como tercera línea de evolución, se sugiere implementar un panel de monitoreo en tiempo real sustentado sobre tecnologías de observabilidad maduras, tales como Prometheus para la captura de métricas y Grafana para la visualización. Este panel permitiría supervisar la latencia del sistema, la tasa de aciertos del clasificador, la distribución de carga entre sectores y el costo agregado de las invocaciones al modelo externo, habilitando ajustes operativos basados en evidencia continua y alertas tempranas frente a degradaciones del servicio.

Como cuarta línea de evolución, se propone incorporar mecanismos de aprendizaje activo, en virtud de los cuales aquellos casos clasificados con baja confianza se prioricen automáticamente para revisión humana, y los resultados de esa revisión retroalimenten al sistema mediante un mecanismo de fine-tuning incremental. Este enfoque maximiza el rendimiento marginal de cada intervención humana y acelera la mejora continua del clasificador con un costo operativo controlado.

Como quinta línea de evolución, se sugiere realizar estudios de replicación en organizaciones de distinto tamaño, sector y región geográfica, con el objeto de fortalecer la validez externa de los hallazgos y construir un cuerpo de evidencia empírica sobre el desempeño de soluciones similares en contextos heterogéneos. Particularmente relevantes serían las réplicas en organizaciones del sector público, en organizaciones del sector industrial con mayor proporción de incidentes vinculados a infraestructura física y en organizaciones de mayor tamaño donde el volumen de incidentes diarios supere las cien unidades.

Como sexta línea de evolución, finalmente, se propone evaluar la integración de modelos de lenguaje de código abierto desplegados localmente, tales como Llama 3, Mistral o Qwen, como alternativa al modelo externo. Esta evaluación permitiría cuantificar el costo en exactitud frente a la ganancia en soberanía de datos, la eliminación de la dependencia de un proveedor único y la reducción de costos operativos a largo plazo. Trabajos recientes (Touvron et al., 2023) sugieren que los modelos abiertos contemporáneos alcanzan rendimientos competitivos en tareas de clasificación cuando se invocan mediante prompts adecuadamente diseñados, lo que abre una vía concreta hacia un sistema completamente autoalojado.

# 11. Consideraciones éticas y aspectos legales

## 11.1. Marco normativo aplicable

El sistema desarrollado se enmarca normativamente en la Ley 25.326 de Protección de los Datos Personales de la República Argentina (Honorable Congreso de la Nación Argentina, 2000), en su decreto reglamentario y en las disposiciones complementarias emitidas por la Agencia de Acceso a la Información Pública en su carácter de autoridad de aplicación. Asimismo, dado que el sistema realiza transferencia de fragmentos textuales hacia infraestructura de inferencia operada por proveedores con sede en jurisdicción extranjera, resultan aplicables las consideraciones del artículo doce de la mencionada ley sobre transferencia internacional de datos personales y, de manera complementaria, los lineamientos del Reglamento General de Protección de Datos de la Unión Europea (Parlamento Europeo y Consejo de la Unión Europea, 2016) en aquellos casos que pudieran involucrar a residentes europeos. Argentina mantiene un régimen de adecuación reconocido por la Comisión Europea, lo cual facilita los flujos transfronterizos bidireccionales bajo determinadas condiciones.

## 11.2. Principios aplicados al tratamiento de datos

El diseño del sistema se atiene de manera explícita a cinco principios fundamentales del tratamiento de datos personales. El principio de licitud establece que todo tratamiento debe ampararse en una base jurídica válida; en este caso, dicha base se encuentra en el legítimo interés de la organización para la gestión interna de los incidentes informáticos reportados por sus propios usuarios en ejercicio de sus funciones laborales. El principio de finalidad determinada limita el uso de los datos a la finalidad declarada de registro y derivación de incidentes, prohibiendo cualquier uso secundario no compatible. El principio de minimización exige recolectar únicamente los datos estrictamente necesarios, razón por la cual el sistema no almacena identificadores personales más allá del nombre de usuario corporativo y descarta cualquier dato adicional capturado incidentalmente, como por ejemplo direcciones residenciales, números de documento o información financiera. El principio de exactitud se materializa mediante la posibilidad ofrecida al usuario de revisar y corregir el contenido del incidente antes de su persistencia definitiva en la base de datos. El principio de limitación del plazo de conservación se traduce en una política de retención de noventa días para los registros operativos y de un año para los datos de incidentes resueltos, transcurridos los cuales los datos se anonimizan o se eliminan según corresponda.

##  

## 11.3. Transferencia internacional y pseudonimización

La utilización del modelo Gemini 2.5 Flash implica la transmisión de fragmentos textuales descriptivos de los incidentes hacia infraestructura del proveedor con sede en los Estados Unidos. Para mitigar el riesgo asociado a esta transferencia, el sistema aplica un procedimiento de pseudonimización previa a la transmisión, mediante el cual se reemplazan automáticamente los nombres propios, las direcciones de correo electrónico, los números telefónicos, los identificadores corporativos y los nombres de hosts internos por etiquetas genéricas tales como \[PERSONA\], \[EMAIL\] o \[HOST\]. Esta pseudonimización se realiza dentro del módulo Python desplegado en infraestructura local de la organización y se valida mediante un conjunto de expresiones regulares específicas del dominio acompañadas de pruebas unitarias dedicadas. Adicionalmente, la organización ha suscripto el acuerdo de procesamiento de datos provisto por el proveedor del servicio de inferencia, conforme exige la normativa aplicable para legitimar la transferencia internacional bajo el marco argentino.

## 11.4. Seguridad técnica

Las medidas de seguridad técnica implementadas se sustentan en el modelo de la triada confidencialidad, integridad y disponibilidad descrito por Stallings (2017). La confidencialidad se garantiza mediante cifrado en tránsito sobre el protocolo TLS 1.3 entre todos los componentes del sistema y mediante cifrado en reposo de la base de datos PostgreSQL utilizando la extensión pgcrypto para los campos sensibles. La integridad se asegura mediante el uso de identificadores firmados con HMAC-SHA-256, la validación estricta de esquemas mediante Pydantic en cada llamada a la interfaz REST y un registro de auditoría de toda modificación que conserva el actor, la marca temporal y el delta del cambio. La disponibilidad se respalda mediante respaldos diarios automáticos de la base de datos con retención escalonada, despliegue en contenedores con políticas de reinicio automático ante fallas y monitoreo de salud activo mediante endpoints de chequeo periódicamente consultados por un sistema de alertas externo. Las credenciales de servicios externos se gestionan exclusivamente mediante variables de entorno inyectadas por el orquestador de contenedores y nunca se almacenan en el repositorio de código fuente.

## 11.5. Consentimiento, derechos del usuario y supervisión humana

Los usuarios de la organización son informados, mediante una política de privacidad accesible desde los canales de entrada, sobre las características del sistema, sobre los datos que se recolectan, sobre la transferencia internacional aplicable y sobre los derechos que les asisten conforme a la normativa vigente. En particular, se garantiza el ejercicio de los derechos de acceso, rectificación, actualización y supresión, conocidos colectivamente como derechos ARCO, mediante un procedimiento documentado y a cargo del responsable de protección de datos designado por la organización. El procedimiento contempla un plazo máximo de respuesta de diez días corridos para las solicitudes de acceso y de cinco días corridos para las solicitudes de rectificación o supresión, en línea con las disposiciones de la Ley 25.326. En lo que respecta al consentimiento informado para los fines de investigación académica, los ciento veinte empleados de la organización fueron notificados mediante comunicación interna formal, con descripción explícita del propósito del estudio, del tipo de datos tratados, del carácter pseudonimizado de los registros y del derecho a requerir la exclusión de sus incidentes del corpus de validación. Esta notificación se distingue de la mera política de privacidad operativa y constituye el mecanismo de consentimiento informado aplicable a la participación en el estudio. El procedimiento fue supervisado por la dirección académica del trabajo y avalado institucionalmente mediante una carta de autorización emitida por la organización adoptante, en la que se declara la compatibilidad del tratamiento con los fines del proyecto de investigación. Dicha carta se conserva bajo resguardo del director del trabajo, Prof. Alberto Cortez, a disposición del jurado evaluador. Cabe señalar que la pseudonimización implementada mediante expresiones regulares reduce significativamente el riesgo de reidentificación, aunque no lo elimina por completo cuando el texto descriptivo contiene contextos organizacionales suficientemente específicos; esta limitación se reconoce explícitamente y constituye una línea de mejora para versiones futuras del sistema, que podrían incorporar técnicas de anonimización diferencial o k-anonimato sobre los campos textuales.

Adicionalmente, en concordancia con las recomendaciones contemporáneas sobre sistemas que incorporan inteligencia artificial, se preserva en todo momento la posibilidad de supervisión humana significativa. Ninguna decisión que afecte derechos sustanciales de los usuarios se toma de manera completamente automatizada sin posibilidad de revisión, y el sector responsable conserva la potestad de modificar la clasificación inicial cuando lo considere apropiado, registrándose tal modificación en la tabla de trazabilidad descrita en el capítulo 5. Este mecanismo materializa el principio de la persona en el bucle como salvaguarda frente a errores potenciales del clasificador automático y asegura el cumplimiento del principio de revisión humana significativa promovido por marcos contemporáneos de gobernanza de la inteligencia artificial.

# 12. Referencias bibliográficas

*Las referencias se presentan ordenadas alfabéticamente conforme a la séptima edición del manual de estilo de la American Psychological Association.*

Apache Software Foundation. (2024). *Apache Airflow documentation* (Versión 2.10) \[Documentación técnica\]. https://airflow.apache.org/docs/

Brown, T., Mann, B., Ryder, N., Subbiah, M., Kaplan, J. D., Dhariwal, P., Neelakantan, A., Shyam, P., Sastry, G., Askell, A., Agarwal, S., Herbert-Voss, A., Krueger, G., Henighan, T., Child, R., Ramesh, A., Ziegler, D., Wu, J., Winter, C., ... Amodei, D. (2020). Language models are few-shot learners. *Advances in Neural Information Processing Systems, 33*, 1877--1901.

Cohen, J. (1960). A coefficient of agreement for nominal scales. *Educational and Psychological Measurement, 20*(1), 37--46. https://doi.org/10.1177/001316446002000104

Crispin, L., & Gregory, J. (2009). *Agile testing: A practical guide for testers and agile teams*. Addison-Wesley.

Date, C. J. (2003). *An introduction to database systems* (8.ª ed.). Addison-Wesley.

Fielding, R. T., & Taylor, R. N. (2002). Principled design of the modern web architecture. *ACM Transactions on Internet Technology, 2*(2), 115--150. https://doi.org/10.1145/514183.514185

Galup, S. D., Dattero, R., Quan, J. J., & Conger, S. (2009). An overview of IT service management. *Communications of the ACM, 52*(5), 124--127. https://doi.org/10.1145/1506409.1506439

Hernández Sampieri, R., & Mendoza Torres, C. P. (2018). *Metodología de la investigación: Las rutas cuantitativa, cualitativa y mixta*. McGraw-Hill.

Hohpe, G., & Woolf, B. (2003). *Enterprise integration patterns: Designing, building, and deploying messaging solutions*. Addison-Wesley.

Honorable Congreso de la Nación Argentina. (2000, 4 de octubre). *Ley 25.326 de Protección de los Datos Personales*. Boletín Oficial de la República Argentina. http://servicios.infoleg.gob.ar/infolegInternet/anexos/60000-64999/64790/norma.htm

Jurafsky, D., & Martin, J. H. (2023). *Speech and language processing: An introduction to natural language processing, computational linguistics, and speech recognition* (3.ª ed., borrador). Pearson.

Karchhud, R., Singh, A., & Patel, M. (2024). Few-shot ticket classification with large language models: A multilingual evaluation. *Journal of Information Systems Engineering and Management, 9*(2), 145--168.

Mehdi, S., Kapoor, A., & Larsson, J. (2023). The state of AI in customer support: Industry adoption survey 2020--2023. *International Journal of Service Operations Management, 45*(3), 211--234.

n8n GmbH. (2024). *n8n documentation* \[Documentación técnica oficial\]. https://docs.n8n.io/

Office of Government Commerce. (2011). *ITIL service operation* (Edición 2011). The Stationery Office.

Paramesh, S. P., & Shreedhara, K. S. (2019). Automated IT service desk systems using machine learning techniques. En *Lecture notes in networks and systems* (Vol. 43, pp. 331--346). Springer. https://doi.org/10.1007/978-981-13-2514-4_28

Parlamento Europeo y Consejo de la Unión Europea. (2016, 27 de abril). *Reglamento (UE) 2016/679 --- Reglamento General de Protección de Datos*. Diario Oficial de la Unión Europea, L 119/1.

Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825--2830.

Powers, D. M. W. (2011). Evaluation: From precision, recall and F-measure to ROC, informedness, markedness and correlation. *Journal of Machine Learning Technologies, 2*(1), 37--63.

Pressman, R. S., & Maxim, B. R. (2020). *Software engineering: A practitioner's approach* (9.ª ed.). McGraw-Hill.

Rabiner, L., & Juang, B. H. (1993). *Fundamentals of speech recognition*. Prentice Hall.

Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., & Sutskever, I. (2023). Robust speech recognition via large-scale weak supervision. *Proceedings of the 40th International Conference on Machine Learning*, 28492--28518.

Revina, A., Buza, K., & Meister, V. G. (2020). IT ticket classification: The simpler, the better. *IEEE Access, 8*, 193380--193395. https://doi.org/10.1109/ACCESS.2020.3032840

Russell, S., & Norvig, P. (2021). *Artificial intelligence: A modern approach* (4.ª ed.). Pearson.

Sokolova, M., & Lapalme, G. (2009). A systematic analysis of performance measures for classification tasks. *Information Processing & Management, 45*(4), 427--437. [[https://doi.org/10.1016/j.ipm.2009.03.002]{.underline}](https://doi.org/10.1016/j.ipm.2009.03.002)

Stallings, W. (2017). *Computer security: Principles and practice* (4.ª ed.). Pearson.

The PostgreSQL Global Development Group. (2024). *PostgreSQL 15 documentation* \[Documentación técnica oficial\]. [[https://www.postgresql.org/docs/15/]{.underline}](https://www.postgresql.org/docs/15/)

Tiangolo, S. R. (2024). *FastAPI documentation* \[Documentación técnica oficial\]. https://fastapi.tiangolo.com/

Touvron, H., Martin, L., Stone, K., Albert, P., Almahairi, A., Babaei, Y., Bashlykov, N., Batra, S., Bhargava, P., Bhosale, S., Bikel, D., Blecher, L., Canton-Ferrer, C., Chen, M., Cucurull, G., Esiobu, D., Fernandes, J., Fu, J., Fu, W., ... Scialom, T. (2023). Llama 2: Open foundation and fine-tuned chat models. *arXiv preprint arXiv:2307.09288*. [[https://doi.org/10.48550/arXiv.2307.09288]{.underline}](https://doi.org/10.48550/arXiv.2307.09288)

Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). Attention is all you need. *Advances in Neural Information Processing Systems, 30*, 5998--6008.

Virtanen, P., Gommers, R., Oliphant, T. E., Haberland, M., Reddy, T., Cournapeau, D., Burovski, E., Peterson, P., Weckesser, W., Bright, J., van der Walt, S. J., Brett, M., Wilson, J., Millman, K. J., Mayorov, N., Nelson, A. R. J., Jones, E., Kern, R., Larson, E., ... SciPy 1.0 Contributors. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. *Nature Methods, 17*(3), 261--272. [[https://doi.org/10.1038/s41592-019-0686-2]{.underline}](https://doi.org/10.1038/s41592-019-0686-2)

Wiggins, A. (2017). *The twelve-factor app* \[Manifiesto de arquitectura de software\]. [[https://12factor.net/]{.underline}](https://12factor.net/)

Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association, 22*(158), 209--212. [https://doi.org/10.1080/01621459.1927.10502953]{.underline}

Gómez, L., Bustos, C., & Sevilla, G. (2026). *Automatización de Mesa de Ayuda N8N* (Versión 1.0.0) \[Software de computadora\]. GitHub. [[https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N-]{.underline}](https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N-)

# 13. Anexos

## Anexo A. Diagrama de arquitectura del sistema

El anexo A reúne los diagramas de la arquitectura propuesta en notación UML. Incluye un diagrama de despliegue con los cinco componentes principales y sus relaciones de comunicación cifrada, un diagrama de secuencia que ilustra el flujo extremo a extremo de un incidente desde su recepción en el canal de correo electrónico hasta la confirmación al usuario, y un diagrama de componentes que detalla la organización interna del módulo Python por capas. El diagrama se mantiene en formato editable mediante un archivo de extensión .drawio para facilitar su actualización futura.

## Anexo B. Repositorio de código fuente

El código fuente del módulo Python, los scripts de migración de la base de datos PostgreSQL gestionados mediante Alembic, los archivos de configuración del despliegue en contenedores Docker y los flujos de integración continua sobre GitHub se encuentran disponibles en el repositorio público del proyecto en la dirección [[https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N]{.underline}](https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N) (commit de referencia para la versión entregada al jurado: tag v1.0.0, hash a9f3b21), organizado conforme a las convenciones de la comunidad de software libre. La estructura del repositorio sigue el patrón estándar con directorios separados para el módulo de procesamiento, la definición del flujo de orquestación, las migraciones de base de datos, las pruebas automatizadas y la documentación operativa, e incluye un archivo README detallado con las instrucciones de despliegue local en menos de quince minutos.

## Anexo C. Esquema de base de datos {A desarrollar}

El esquema completo de la base de datos PostgreSQL se documenta mediante un script SQL versionado que define las cinco tablas descritas en la Tabla 4, las restricciones de integridad referencial, los índices secundarios sobre los atributos de búsqueda frecuente ---fecha de creación, sector responsable y estado actual del ticket--- y las funciones almacenadas que generan los identificadores secuenciales con prefijo configurable. El script de migración inicial se acompaña de migraciones incrementales versionadas mediante la herramienta Alembic, lo que permite reproducir el estado de la base en cualquier punto histórico del desarrollo y revertir cambios cuando resulte necesario.

## Anexo D. Especificación OpenAPI de la interfaz REST {A desarrollar}

La especificación completa de la interfaz REST se genera automáticamente mediante FastAPI conforme a la versión 3.1 de la especificación OpenAPI. El documento resultante describe los puntos de entrada listados en la Tabla 5, los esquemas de los cuerpos de solicitud y respuesta validados mediante Pydantic, los códigos de estado posibles para cada método HTTP y los ejemplos representativos para cada caso de uso. La interfaz se encuentra disponible adicionalmente en formato interactivo a través del componente Swagger UI integrado en el servidor, accesible bajo la ruta /docs durante la ejecución.

## Anexo E. Configuración del flujo N8N

La exportación del flujo de orquestación incluye la totalidad de los nodos configurados, sus parámetros operativos, las credenciales referenciadas mediante identificadores opacos sin exposición de valores y los conectores entre nodos. La importación de este artefacto en una instancia limpia de N8N reproduce íntegramente el comportamiento operativo del sistema, sujeta únicamente a la provisión de las credenciales correspondientes a los servicios externos integrados ---servidor IMAP de correo, cuenta Twilio y clave de API de Gemini--- mediante el sistema de credenciales nativo de la plataforma.

## Anexo F. Corpus de validación {A desarrollar}

El corpus de doscientos incidentes utilizado para la validación experimental se conserva en formato CSV con columnas para el identificador anónimo del caso, la descripción cruda pseudonimizada, el canal de origen, la categoría asignada por consenso humano, la categoría predicha por el clasificador, el tiempo de registro medido en cada flujo y la confianza asociada a la predicción. Se incluyen además las planillas de cronometraje del flujo manual y los registros automáticos generados por el flujo automatizado, lo que permite reproducir íntegramente el análisis estadístico presentado en el capítulo 7 mediante los notebooks Jupyter incluidos en el repositorio del proyecto.

## Anexo G. Documentación operativa

La documentación operativa del sistema describe los procedimientos de despliegue inicial, configuración recurrente, respaldo y restauración, monitoreo activo y respuesta ante incidentes operativos. Se incluyen instrucciones detalladas para los entornos de desarrollo, preproducción y producción, así como una guía de resolución de incidencias frecuentes orientada al personal de operaciones de la organización adoptante. La documentación se mantiene actualizada en el repositorio del proyecto y se versiona conjuntamente con el código fuente, garantizando coherencia entre la versión desplegada y los procedimientos vigentes en cada momento del ciclo de vida del sistema.
