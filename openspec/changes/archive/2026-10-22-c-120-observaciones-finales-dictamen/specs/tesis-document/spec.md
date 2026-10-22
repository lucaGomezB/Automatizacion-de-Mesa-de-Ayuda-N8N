## ADDED Requirements

### Requirement: Rotulo de la sub-hipotesis de intervencion humana como no contrastada

La tesis SHALL rotular la sub-hipotesis de intervencion humana de forma explicita como "no contrastada por ausencia de registro primario" en el resumen, la introduccion, los resultados y las conclusiones, y SHALL retitular la subseccion homonima del capitulo de resultados para que su titulo no prometa un resultado que la tesis no entrega. El texto MUST NOT presentar esa sub-hipotesis como una laguna sin declarar, ni dejar un titulo que afirme una reduccion no medida.

#### Scenario: Rotulo explicito en las cuatro secciones

- **WHEN** se lee la sub-hipotesis de intervencion humana en el resumen, la introduccion, los resultados y las conclusiones
- **THEN** en las cuatro se declara que la sub-hipotesis es "no contrastada por ausencia de registro primario"
- **AND** no se la presenta como no medida sin explicar la causa, ni como confirmada o refutada

#### Scenario: Subseccion de resultados retitulada

- **WHEN** se inspecciona el titulo de la subseccion de intervencion humana del capitulo de resultados
- **THEN** el titulo no promete una "Reduccion de la intervencion humana" no entregada
- **AND** la entrada correspondiente del indice refleja el nuevo titulo

### Requirement: Trazabilidad bibliografica de afirmaciones sobre plataformas comerciales y precios

Toda afirmacion de la tesis sobre productos comerciales, plataformas o precios (por ejemplo Zendesk, Freshdesk, ServiceNow, DigitalOcean, Vertex AI) SHALL apoyarse en una referencia bibliografica formal presente en `Bibliography_base.bib`, o bien reformularse de forma explicita como observacion propia de los autores. El documento MUST NOT sostener afirmaciones comerciales citables apoyadas unicamente en URLs al pie o en la documentacion publica sin entrada bibliografica.

#### Scenario: Referencias formales o reformulacion propia

- **WHEN** se leen las afirmaciones sobre plataformas comerciales y precios en los capitulos que las contienen (estado del arte, introduccion y discusion)
- **THEN** cada afirmacion citable se respalda con una entrada bibliografica formal en `Bibliography_base.bib`
- **AND** las afirmaciones no citables se reformulan como observacion propia declarada
- **AND** no queda ninguna afirmacion comercial apoyada solo en una URL al pie

#### Scenario: Correspondencia citas-bibliografia preservada

- **WHEN** se agregan las entradas nuevas a `Bibliography_base.bib`
- **THEN** cada entrada nueva incluye autor o entidad, titulo, ano y campo de publicacion mas `url` o `doi`
- **AND** no se introduce ninguna cita huerfana ni ninguna entrada sin usar

### Requirement: Declaracion del intervalo de confianza del kappa

La tesis SHALL reportar el intervalo de confianza del coeficiente kappa (0,87) si la tabla de doble etiquetado es recuperable, calculandolo por bootstrap con semilla fija. Si la tabla primaria no es recuperable, la tesis SHALL conservar y elevar al cuerpo una declaracion explicita de no computabilidad, sin fabricar un intervalo. La decision SHALL quedar registrada en el diseno del cambio.

#### Scenario: Tabla recuperable

- **WHEN** la tabla de acuerdo observado/esperado o las etiquetas por caso de ambos analistas estan disponibles
- **THEN** la tesis reporta el intervalo de confianza del kappa junto al valor puntual 0,87
- **AND** declara el metodo y la semilla empleados

#### Scenario: Tabla no recuperable

- **WHEN** la tabla primaria de doble etiquetado no esta disponible en las fuentes del repositorio
- **THEN** la tesis declara de forma explicita que el intervalo de confianza del kappa es no computable por ausencia de la tabla primaria
- **AND** no se fabrica ni se estima un intervalo
- **AND** el rotulo interpretativo "casi perfecto" (Landis y Koch) se conserva

### Requirement: Umbral de migracion como referencia indicativa de orden de magnitud

El umbral de "5.000 casos" para migrar a un clasificador supervisado propio SHALL presentarse como una referencia indicativa explicita de orden de magnitud, no como un valor derivado del corpus. El documento MUST NOT presentarlo como un valor calculado ni como una condicion tecnica exacta.

#### Scenario: Umbral rotulado como indicativo

- **WHEN** se lee el pasaje de recomendaciones sobre el clasificador supervisado propio
- **THEN** el umbral de 5.000 casos se declara como referencia indicativa de orden de magnitud
- **AND** se aclara que no deriva del corpus actual ni de un calculo de potencia estadistica

### Requirement: Acotacion del eje de reconocimiento automatico del habla

El eje de reconocimiento automatico del habla (ASR) del marco teorico SHALL acotarse al minimo conceptual necesario para el canal telefonico, dado que el sistema delega la transcripcion en un servicio externo y no integra un motor de ASR. El documento SHALL conservar unicamente la nocion conceptual y la aclaracion de que la transcripcion efectiva la provee un servicio externo.

#### Scenario: Eje de ASR reducido

- **WHEN** se lee la subseccion de reconocimiento automatico del habla del marco teorico
- **THEN** su extension se limita al minimo conceptual necesario para situar el canal telefonico
- **AND** se declara que el sistema no integra un motor de ASR y que la transcripcion la provee un servicio externo
- **AND** la reduccion no introduce paginas netas al cuerpo

### Requirement: Numeracion limpia del capitulo de aspectos legales

El capitulo de consideraciones eticas y aspectos legales SHALL presentar una unica seccion de nivel superior, de modo que no incremente en uno la numeracion de los capitulos siguientes. Los comentarios internos de numeracion de los archivos `.tex` SHALL reflejar la posicion real de cada capitulo en el documento.

#### Scenario: Unica seccion de nivel superior

- **WHEN** se inspecciona la estructura de secciones del capitulo de aspectos legales
- **THEN** el capitulo contiene una sola seccion de nivel superior
- **AND** las subsecciones previamente bajo la segunda seccion pasan a depender de la unica seccion superior sin perder contenido
- **AND** la numeracion de los capitulos posteriores no se desplaza

#### Scenario: Comentarios de numeracion coherentes

- **WHEN** se revisan los comentarios de numeracion en la cabecera de los archivos `.tex` y en `main.tex`
- **THEN** cada comentario declara la posicion real del capitulo en el documento compilado
- **AND** no queda ningun comentario que asigne al capitulo legal un numero de posicion incorrecto

### Requirement: Fuente del criterio del umbral del 85 por ciento

La justificacion del umbral de exactitud del 85~\% SHALL declarar la fuente de cada uno de sus criterios convergentes. El criterio que hoy se apoya en "mediciones organizacionales preliminares" SHALL citarse con una fuente formal, o bien reformularse de forma explicita como estimacion propia de los autores sin presentarla como medicion de respaldo. El documento MUST NOT atribuir a mediciones organizacionales preliminares una precision que no esta citada ni declarada como propia.

#### Scenario: Fuente declarada o reformulacion propia

- **WHEN** se lee la justificacion del umbral de exactitud del 85~\% en el capitulo de introduccion
- **THEN** cada uno de los criterios convergentes declara su fuente
- **AND** el criterio apoyado en mediciones organizacionales preliminares se cita con una referencia formal o se reformula como estimacion propia declarada
- **AND** no queda ninguna medicion organizacional preliminar presentada como respaldo sin fuente
