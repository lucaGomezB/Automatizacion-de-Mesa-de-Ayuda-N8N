## MODIFIED Requirements

### Requirement: Tabla de configuracion evaluada frente a entregada

El Anexo B (`sec:anexo-repositorio`, `12-anexos.tex`) SHALL incluir una tabla con etiqueta `tab:configuracion-evaluada-entregada` y tres columnas de configuracion: "Configuracion evaluada" (commit `d6bb474`, 7-10-2026), "Configuracion de la campaña complementaria" (la revision o el rango de revisiones sobre el que corrio la campaña complementaria de medicion, con c-165 a c-168 aplicados y el clasificador congelado, verificado con `git log` y con los artefactos de `evaluation/data/campana/` y `docs/campana-medicion/`) y "Configuracion entregada" (el tag que identifica el Anexo B en la release vigente). La tabla SHALL consignar solo valores verificados con `git show <revision>:<archivo>`, con `git log` o con los changes archivados: versiones de FastAPI, Uvicorn, SQLAlchemy, google-genai, pytest, pytest-cov y React; el flujo N8N versionado; la imagen de N8N (oficial `n8nio/n8n:2.11.2` o imagen derivada de `docker/n8n/Dockerfile` con el parche IMAP de c-182); los reintentos del tramo de alta (c-140); el disparador de revision por reportante no identificado en el directorio (c-82); la propagacion del contacto del reportante en el POST (c-162); la prueba de humo de extremo a extremo y la verificacion automatizada de TLS (c-140); la instrumentacion de intervencion (c-165) y la version del clasificador (`classifier_version`), que SHALL coincidir entre la configuracion evaluada y la de la campaña complementaria; y los componentes sin cambios. La columna de la campaña complementaria MUST NOT quedar vacia ("---") en las filas que la condicionan (revision por reportante, propagacion del contacto, instrumentacion, clasificador e imagen de N8N); cuando un valor no sea recuperable SHALL decir "no registrado" y acotar el rango con `git log`. La tabla y su nota de fuente MUST NOT afirmar que la campaña complementaria corrio sobre "la misma configuracion evaluada": SHALL decir que corrio con el mismo clasificador congelado (`hybrid-v3`) sobre un backend posterior con c-82 y c-162 activos. La fila "Sin cambios" MUST NOT incluir N8N 2.11.2 sin calificar si la configuracion entregada usa la imagen derivada. Cada valor SHALL registrarse en `docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md` con su comando de verificacion. La tabla MUST NOT incluir valores no verificados.

#### Scenario: Valores verificados contra ambas revisiones

- **WHEN** se compara cada celda de la tabla con `git show d6bb474:App/Backend/requirements.txt`, con el mismo archivo en la revision de la campaña complementaria y en el tag entregado, con los `package.json`/`package-lock.json` y con `n8n/workflow.json` de las tres revisiones
- **THEN** cada version de la columna evaluada coincide con la registrada (FastAPI 0.115.0, Uvicorn 0.30.6, SQLAlchemy 2.0.36, google-genai >=2.20.0, pytest 8.3.3, pytest-cov 5.0.0, React 18.3.1) y las de las otras dos columnas coinciden con `git show` de su revision
- **AND** las capacidades posteriores figuran como ausentes en la columna evaluada y presentes en las columnas posteriores con su change, incluida la instrumentacion de intervencion de c-165

#### Scenario: Clasificador congelado entre la evaluacion y la campaña complementaria

- **WHEN** se compara la fila de la version del clasificador entre la configuracion evaluada y la de la campaña complementaria
- **THEN** ambas declaran el mismo `classifier_version` y los mismos umbral, prompt y vocabulario
- **AND** si difieren, la tabla lo declara y las metricas de la campaña complementaria se rotulan como de otra configuracion del clasificador

#### Scenario: Columna de la campaña complementaria completa

- **WHEN** se leen las filas de revision por reportante no identificado, propagacion del contacto del reportante, instrumentacion de intervencion, version del clasificador e imagen de N8N en la columna de la campaña complementaria
- **THEN** ninguna celda es "---": cada una declara su valor verificado (por ejemplo, "Si (c-82)") o "no registrado"
- **AND** la columna declara la revision o el rango de revisiones de la campaña con sus fechas

#### Scenario: Sin "misma configuracion evaluada"

- **WHEN** se busca "misma configuración evaluada" en `12-anexos.tex`
- **THEN** no aparece referida a la campaña complementaria
- **AND** la nota de fuente declara el clasificador congelado sobre un backend con c-82 y c-162 activos

#### Scenario: Imagen derivada de N8N declarada

- **WHEN** se leen la fila de la imagen de N8N y la fila "Sin cambios"
- **THEN** la configuracion entregada declara la imagen derivada de `docker/n8n/Dockerfile` (`FROM n8nio/n8n:2.11.2` con el parche IMAP de c-182)
- **AND** "Sin cambios" no declara N8N 2.11.2 como componente identico entre la evaluada y la entregada

#### Scenario: Etiqueta estable para otros changes

- **WHEN** otro change (c-159) remite a la tabla desde las leyendas de las Figuras 1 y 4
- **THEN** la referencia `\ref{tab:configuracion-evaluada-entregada}` resuelve sin advertencias de referencia indefinida

#### Scenario: Registro en el memo de conteos tecnicos

- **WHEN** se lee `docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md`
- **THEN** figura una seccion con cada valor de la tabla, su revision y su comando de verificacion, incluida la columna de la campaña complementaria

### Requirement: Reporte de la exactitud del brazo manual de la campaña de medicion

La tesis SHALL reportar, en el marco metodologico (4.4 y 4.6) y en
`subsec:resultados-campana-medicion`, la exactitud estricta y laxa del brazo manual de
la campaña de medicion contra la referencia del consenso del doble etiquetado nuevo
(coincidencia `E1 = E2`; discordantes informados aparte): por operador (`O1`, `O2`)
con intervalo de Wilson al 95 %, agregada con intervalo bootstrap por caso
(`B = 2000`, semilla `20261021`) y con el contraste de McNemar frente al brazo
automatizado sobre los mismos casos. La exactitud agregada SHALL rotularse con su unidad
real: 0,8278 = 125 de 151 derivaciones de operador (80 de `O1` y 71 de `O2`) sobre 138
casos unicos, 13 de ellos con doble cobertura, y la laxa 0,8609 = 130 de 151; MUST NOT
rotularse como "125 de 138 casos" ni "130 de 138". La comparacion con el brazo
automatizado SHALL expresarse en la misma unidad o declarar la diferencia de unidad
(automatizado por caso, manual por derivacion) y remitir al McNemar por operador como
contraste formal. El brazo automatizado de ese contraste es la
exactitud de v9 (predicciones congeladas del clasificador evaluado) contra la
referencia nueva, un numero nuevo producido por c-167: SHALL rotularse como "exactitud
de v9 contra la referencia de la campaña de medicion", SHALL registrarse en el memo
como entrada propia y MUST NOT reemplazar el `73,5 %` ni ningun otro valor canonico de
v9. La tesis SHALL declarar que esa exactitud (110 de 138) se calcula sobre la cache
in-sample del 7-10-2026 (`predicciones_in_sample.json`, copia de
`evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`) y no sobre la salida en
vivo de la campaña, que difiere en 13 casos (7 de 119 escritos y 6 de 81 telefonicos),
SHALL justificar la eleccion y SHALL indicar que el McNemar usa esa cache. Si
`registro_sujetos.csv` muestra solape entre los operadores y quienes produjeron la
referencia, la tesis SHALL declarar la exactitud manual "no medida: operadores no
independientes" y MUST NOT cuantificarla.

#### Scenario: Exactitud manual reportada con IC

- **WHEN** la exactitud manual fue medida y se lee `subsec:resultados-campana-medicion`
- **THEN** se reporta la exactitud estricta y laxa por operador con intervalo de Wilson, la agregada con intervalo bootstrap, el `n` de casos de referencia y el numero de discordantes excluidos
- **AND** se reporta el contraste de McNemar entre el brazo manual y el automatizado con su estadistico y su valor p

#### Scenario: Denominador de la agregada por derivacion

- **WHEN** se busca "125 de 138" y "130 de 138" en `sections/*.tex`
- **THEN** no hay coincidencias
- **AND** la agregada figura como 125 de 151 derivaciones (80 de `O1` y 71 de `O2`) sobre 138 casos unicos y la laxa como 130 de 151

#### Scenario: Comparacion en la misma unidad

- **WHEN** se lee la oracion que compara la exactitud manual agregada con la del brazo automatizado (110 de 138)
- **THEN** ambas se expresan en la misma unidad o la oracion declara que una es por derivacion y la otra por caso
- **AND** el contraste formal remite al McNemar por operador

#### Scenario: Procedencia de la exactitud automatizada declarada

- **WHEN** se lee la oracion de `subsec:resultados-campana-medicion` que informa 0,7971 (110 de 138)
- **THEN** declara que proviene de la cache in-sample del 7-10-2026 y no de la salida en vivo de la campaña, que difiere en 13 casos
- **AND** justifica la eleccion y declara que el McNemar usa esa cache

#### Scenario: Exactitud manual no medida por falta de independencia

- **WHEN** `registro_sujetos.csv` muestra solape entre operadores y productores de la referencia
- **THEN** el marco metodologico, los resultados, la discusion, las conclusiones y el memo declaran "no medida: operadores no independientes"
- **AND** no se cuantifica ninguna exactitud del brazo manual

#### Scenario: Exactitud automatizada frente a la referencia nueva rotulada

- **WHEN** la subseccion informa la exactitud de v9 contra el consenso de `E1`/`E2`
- **THEN** la rotula como "exactitud de v9 contra la referencia de la campaña de medicion" y cita su entrada propia del memo
- **AND** no la presenta como reemplazo ni como correccion del `73,5 %` ni de otro valor canonico de v9

### Requirement: Reporte de la tasa de intervencion humana de la campaña de medicion

La tesis SHALL reportar en el marco metodologico (4.6 y 4.7) y en
`subsec:reduccion-intervencion` la `tasa_intervencion_humana` de la campaña de
medicion (c-167): proporcion de casos con `n` e intervalo de Wilson al 95 %, desglose
por origen (`gate`, `muestreo`, `rederivacion`, `completado_manual`), por cambio de
sector y por canal, y la segunda dimension rotulada de la variable, la proporcion del
tiempo dedicado a tareas manuales sobre el tiempo del proceso. La regla de tres vias
(limite superior menor que `0,15`: compatible; estimacion mayor o igual que `0,15`:
refutada; estimacion menor que `0,15` con limite superior mayor o igual: no concluyente)
SHALL aplicarse a dos lecturas reportadas por separado y rotuladas: la tasa bruta de
intervencion (147 de 200; IC [67,0 %; 79,1 %]), que SHALL declararse no compatible con
la cota pero atribuida a la configuracion de la prueba (derivacion por reportante no
identificado, c-82) y no a la necesidad de revision del clasificador; y la proporcion de
intervenciones que cambiaron la derivacion (25 de 200 = 12,5 %; IC de Wilson [8,6 %;
17,8 %]), que es la medida pertinente a la variable de la sub-hipotesis y resulta
**no concluyente**. La tesis SHALL distinguir la derivacion por confianza (regla de 0,70
sobre Gemini, 0 casos) de la derivacion por reportante no identificado (147 casos:
66 de 66 de correo, 81 de 81 de telefonia y 0 de 53 del formulario web) y MUST NOT
afirmar a la vez que el gate no derivo ningun caso y que todas las intervenciones fueron
del gate sin esa distincion. Cuando la cobertura de
las consignas de inicio y fin sea mayor o igual que el 80 %, la tesis SHALL reportar la
proporcion del tiempo con su estimacion puntual, su intervalo bootstrap del cociente
(`B = 2000`, semilla `20261021`), la cobertura observada y los tamanos que la
sostienen, y SHALL declarar la limitacion del denominador (tiempo de registro
automatizado de los 191 casos de la corrida, incluidos los no intervenidos, mas la
duracion de la intervencion; no el tiempo total de atencion); cuando
la cobertura sea inferior al 80 %, SHALL declararla "no estimable" con la cobertura
observada. El titulo de `subsec:reduccion-intervencion` SHALL ser coherente con el estado
de la sub-hipotesis. Si el export no cubre la corrida, SHALL declarar "no contrastada:
registro incompleto".

#### Scenario: Tasa de intervencion reportada

- **WHEN** el export cubre la corrida y se lee `subsec:reduccion-intervencion`
- **THEN** se reportan la tasa bruta y la proporcion de intervenciones con cambio de derivacion, cada una con su `n`, su estimacion, ambos limites de Wilson y su veredicto frente a `0,15`, con el desglose por origen, por cambio de sector y por canal
- **AND** la proporcion del tiempo figura con su intervalo bootstrap o como "no estimable" con la cobertura observada

#### Scenario: Derivacion por confianza frente a derivacion por reportante

- **WHEN** se leen los parrafos del gate y de la sub-hipotesis 2 en `subsec:reduccion-intervencion`
- **THEN** la derivacion por confianza se declara en 0 casos y la derivacion por reportante no identificado en 147 casos con su desglose por canal (66/66 correo, 81/81 telefonia, 0/53 formulario web)
- **AND** el texto explica que `origen_intervencion = gate` registra el indicador `requiere_revision_humana` y no la regla de confianza

#### Scenario: Sin el 65,5 % como proporcion de derivacion

- **WHEN** se lee el parrafo del gate en `subsec:reduccion-intervencion`
- **THEN** el 65,5 % no se presenta como proporcion de casos sin derivacion
- **AND** si se menciona, se rotula como cobertura de la etapa deterministica

#### Scenario: Proporcion de tiempo reportada con su valor

- **WHEN** la cobertura de las consignas de inicio y fin es mayor o igual que el 80 % y se lee `subsec:reduccion-intervencion`
- **THEN** la proporcion del tiempo dedicado a tareas manuales se reporta con su estimacion puntual `0,5307`, su intervalo bootstrap del cociente `[0,4407; 0,6111]` (`B = 2000`, semilla `20261021`) y la cobertura observada `0,9388`
- **AND** se declaran los tamanos que la sostienen (147 casos con intervencion, 138 con duracion completa y 191 casos en el denominador de tiempos automatizados, incluidos los no intervenidos) y la limitacion del denominador
- **AND** el valor figura en `docs/Tesis/Correcciones/numeros-canonicos.md` (Seccion 3.14) con estado vigente, no reemplaza ningun valor canonico y aparece en `07-resultados.tex` una sola vez

#### Scenario: Anuncio metodologico alineado con el denominador medido

- **WHEN** se lee el parrafo de metricas del marco metodologico (`04-marco-metodologico.tex`)
- **THEN** la proporcion del tiempo se anuncia con el denominador efectivamente medido (tiempo de registro automatizado mas duracion de la intervencion) y remite con `\autoref` a `subsec:reduccion-intervencion`
- **AND** no se afirma ningun valor de la proporcion del tiempo en el marco metodologico

#### Scenario: Titulo coherente con el estado

- **WHEN** se inspecciona el titulo de `subsec:reduccion-intervencion` y su entrada en el indice
- **THEN** el titulo no promete una reduccion salvo en el estado "contrastada: compatible"
- **AND** el rotulo `subsec:reduccion-intervencion` se conserva

#### Scenario: Registro incompleto

- **WHEN** el export no cubre la corrida de la campaña de medicion
- **THEN** la subseccion declara "no contrastada: registro incompleto" y no cuantifica la proporcion
- **AND** el estado se propaga identico al resumen, la introduccion, las conclusiones y el memo

### Requirement: Reporte del efecto de orden de la campaña de medicion

La tesis SHALL describir en 4.2 (`subsec:diseno-experimental`) y 4.5
(`subsec:protocolo-pruebas`) el contrabalanceo de condicion PLANIFICADO de la campaña de
medicion (plan `evaluation/data/campana/plan_campana.csv`: `posicion`, `mitad`,
`brazo_primero`) y el orden EFECTIVAMENTE EJECUTADO segun las marcas de tiempo de
`brazo_manual.csv` y de los sidecars del brazo automatizado: el brazo manual precedio al
automatizado en los 200 casos (manual el 5-11-2026 entre las 09:20 y las 18:49, −03;
automatizado entre las 23:47 UTC del 5-11 y las 22:45 UTC del 6-11) y los grupos
`brazo_primero` se intercalaron por `posicion` en una misma ventana, sin la secuencia de
turnos del runbook `docs/campana-medicion/runbook-campana-contrabalanceada.md`. El
analisis en 4.6 (`subsec:analisis-estadistico`) y el reporte en
`subsec:resultados-campana-medicion` SHALL declarar que el contraste entre grupos
`brazo_primero` no estima el efecto de orden de las condiciones y MUST NOT presentarlo
como evidencia sobre el orden; SHALL conservar el efecto de posicion (Spearman) como el
unico analisis valido, con su efecto minimo detectable, y SHALL consignar que fue
significativo para `O2` (ρ = −0,3604, p = 0,00011) y no para `O1`. La tesis MUST NOT citar
un efecto minimo detectable pareado para el contraste entre grupos. El efecto de orden
SHALL declararse como amenaza no resuelta en 4.7 (`subsec:amenazas-validez`) y en la
discusion (9.1 y explicaciones rivales de `08-discusion.tex`), que MUST NOT remitir su
descarte a un diseno contrabalanceado.

#### Scenario: Orden ejecutado descrito

- **WHEN** se leen 4.2 y 4.5
- **THEN** se declara que el brazo manual precedio al automatizado en los 200 casos y que los grupos `brazo_primero` se intercalaron en una misma ventana
- **AND** no queda la afirmacion de que la campaña "contrabalancea el orden de las condiciones por caso" sin la salvedad de lo ejecutado

#### Scenario: Efecto de condicion sin valor probatorio sobre el orden

- **WHEN** se lee el parrafo del efecto de orden de `subsec:resultados-campana-medicion`
- **THEN** el contraste entre grupos `brazo_primero` no se presenta como evidencia de ausencia de efecto de orden
- **AND** el efecto de posicion se reporta con su estadistico, su valor p y su efecto minimo detectable, significativo para `O2`

#### Scenario: Amenaza no resuelta

- **WHEN** se leen 4.7 y las explicaciones rivales de la discusion
- **THEN** el efecto de orden figura como amenaza no resuelta
- **AND** ninguna oracion afirma que la campaña complementaria "aborda" o "descarta" el efecto de orden con el contrabalanceo

### Requirement: Declaración de los analistas etiquetadores

El documento SHALL declarar quiénes realizaron el etiquetado del corpus, su
independencia respecto de los autores del trabajo y si alguno de ellos participó
además como operador del brazo manual, para cada campaña. Para la campaña 2026-10
SHALL declarar que los dos analistas que fijaron la referencia fueron también los
operadores del brazo manual y, según `evaluation/data/campana/registro_sujetos.csv` y
la sección "Sujetos" de `evaluation/data/campana/README.md`, que uno de ellos (`T1`) es
autor del trabajo; MUST NOT declarar a ambos "ajenos al equipo de autores". Esa
coincidencia SHALL llevarse como limitación a 4.7 y a 9.4. Para la campaña de medición
SHALL declarar a los etiquetadores `E1` y `E2` y a los operadores `O1` y `O2` por alias
seudonimizado y su independencia mutua, respecto de los analistas originales y respecto
de los autores, según `registro_sujetos.csv`, o declarar el solape que ese registro
muestre. Esta declaración MUST ser coherente con el cómputo de cada acuerdo
inter-evaluador y MUST NOT incluir datos personales.

#### Scenario: Analistas declarados

- **WHEN** se lee la descripción del doble etiquetado independiente
- **THEN** se declaran los analistas etiquetadores de la campaña 2026-10 y los etiquetadores `E1`/`E2` de la campaña de medición
- **AND** se declara su independencia (o dependencia) respecto de los autores

#### Scenario: Analista original autor declarado

- **WHEN** se busca "ajenos al equipo de autores" en `04-marco-metodologico.tex`
- **THEN** no aparece referido a los dos analistas originales
- **AND** 4.4 declara que uno de los analistas originales (`T1`) es autor y operó el brazo manual de 2026-10, y 4.7 y 9.4 lo recogen como limitación

#### Scenario: Solapamiento con el brazo manual declarado

- **WHEN** un etiquetador también operó el brazo manual en alguna de las dos campañas
- **THEN** el documento lo declara explícitamente para esa campaña
- **AND** se discute la implicancia para la independencia de la verdad fundamental

#### Scenario: Independencia de la campaña de medición

- **WHEN** `registro_sujetos.csv` no muestra solape entre `E1`, `E2`, `O1`, `O2`, los analistas originales y los autores
- **THEN** el documento declara que la campaña de medición resolvió la dependencia entre etiquetadores y operadores de la campaña 2026-10
- **AND** la declaración se acompaña de la remisión al registro de sujetos, sin datos personales

### Requirement: Precision del commit de referencia en el Anexo B

El Anexo B SHALL describir el commit al que apunta el tag de la version entregada sin llamarlo "commit definitivo": SHALL declarar que el tag fija el contenido de la version entregada y que un commit posterior de la rama principal consigna su hash, sin modificar las fuentes de la tesis salvo esa linea. Salvo que el usuario elija otro patron de release en c-187 (design D7), el PDF compilado dentro del commit etiquetado MUST NOT imprimir el hash de otra release presentado como el de la version: en ese commit el Anexo B SHALL enunciar que el hash del tag se consigna en el commit siguiente y SHALL dar el procedimiento de verificacion (`git rev-parse <tag>^{commit}` y `git diff --stat <tag> HEAD -- "docs/Tesis/v10 (IA)/paper/sections"`); el commit posterior reemplaza ese enunciado por el hash completo.

#### Scenario: Patron de dos commits declarado

- **WHEN** se lee el primer parrafo del Anexo B
- **THEN** no aparece "commit definitivo"
- **AND** se explica que el hash se consigna en un commit posterior, verificable con `git diff --stat <tag> HEAD -- "docs/Tesis/v10 (IA)/paper/sections"`

#### Scenario: PDF del tag sin hash ajeno

- **WHEN** se extrae el texto del Anexo B del PDF versionado en el commit etiquetado `v1.2.11`
- **THEN** no figura el hash de `v1.2.10` ni de otra release como referencia de la version
- **AND** figuran el nombre del tag y el procedimiento para obtener y verificar su hash

## ADDED Requirements

### Requirement: Mecanismo de derivacion de la campaña complementaria verificado y declarado

Antes de reescribir `subsec:reduccion-intervencion`, el change SHALL verificar, por
lectura del codigo del backend (`App/Backend/app/services/incidente_service.py` y las rutas
que resuelven el reportante por canal), de los artefactos de `evaluation/data/campana/`
(`intervenciones.csv` y los ocho `sidecar_*.json`) y de la documentacion de despliegue de
`docs/campana-medicion/`, que condicion activo `requiere_revision_humana` en los 147 casos
intervenidos, sin mediciones nuevas. La verificacion SHALL registrarse en
`docs/Tesis/Correcciones/dictamen-correcciones.md` con su evidencia. La tesis SHALL
declarar el mecanismo verificado en `subsec:reduccion-intervencion` y en
`subsec:resultados-campana-medicion`, y MUST NOT afirmar un mecanismo que la verificacion
no confirme; si la verificacion no confirma la regla del reportante no identificado
(c-82), la reescritura SHALL suspenderse hasta decision del usuario.

#### Scenario: Verificacion registrada

- **WHEN** se lee la seccion de c-187 en `dictamen-correcciones.md`
- **THEN** figura la nota de verificacion con el mecanismo confirmado, el cruce por canal (66/66, 81/81, 0/53) y las rutas de codigo consultadas
- **AND** se declara como se resuelve el reportante en cada canal

#### Scenario: Mecanismo declarado en la tesis

- **WHEN** se lee `subsec:reduccion-intervencion`
- **THEN** el texto nombra la regla que derivo los 147 casos (reportante no identificado en el directorio, c-82, si la verificacion lo confirma) y su relacion con los remitentes sinteticos del corpus
- **AND** no atribuye esas derivaciones a la regla de confianza

### Requirement: Estado de la segunda sub-hipotesis coherente con la variable medida

El estado de la segunda sub-hipotesis SHALL ser "no concluyente", fundado en la
proporcion de intervenciones que cambiaron la derivacion (25 de 200 = 12,5 %; IC de
Wilson [8,6 %; 17,8 %]), con la declaracion de que la tasa bruta (147 de 200) no es
compatible con la cota de 0,15 pero refleja la regla de derivacion por reportante de la
configuracion de la prueba. Ese estado SHALL ser identico en el resumen, el abstract, la
seccion 1.4 (`01-introduccion.tex`), la seccion 9.1 (`08-discusion.tex`), la Tabla 18
(`tab:cumplimiento-objetivos`, filas del objetivo general y del objetivo especifico 4) y
la seccion 11.3 (`subsec:medicion-intervencion`). La seccion 9.1 SHALL mencionar la
segunda sub-hipotesis al resumir el estado de la hipotesis principal. La Tabla 18 MUST
NOT apoyar el objetivo general ni el objetivo especifico 4 en una intervencion "medida y
refutada". La seccion 11.3 MUST NOT presentar el 73,5 % como defecto del clasificador a
reducir y SHALL proponer la medicion de la variable con reportantes identificados. El
resumen y el abstract MUST NOT contener un parentesis "(73,5 %, IC [67,0 %, 79,1 %])"
cuya magnitud pueda confundirse con la exactitud estricta (tambien 147/200).

#### Scenario: Estado unico de la sub-hipotesis 2

- **WHEN** se comparan el resumen, el abstract, 1.4, 9.1, la Tabla 18 y 11.3
- **THEN** todos declaran la sub-hipotesis 2 como no concluyente con la misma medida (25 de 200, IC [8,6 %; 17,8 %])
- **AND** ninguno la declara "refutada" por la tasa de 73,5 %

#### Scenario: Resumen sin ambiguedad de magnitud

- **WHEN** se lee la oracion del resumen y del abstract que enuncia los estados por sub-hipotesis
- **THEN** la cifra de intervencion nombra su magnitud (intervenciones con cambio de derivacion o tasa bruta por la regla del reportante)
- **AND** no queda un parentesis con 73,5 % y [67,0 %, 79,1 %] adyacente a la intervencion humana

#### Scenario: 11.3 reformulada

- **WHEN** se lee `subsec:medicion-intervencion`
- **THEN** no aparece "respecto del 73,5 %" como meta de reduccion
- **AND** se propone medir la variable con reportantes identificados en el directorio

### Requirement: Fiabilidad de la referencia de verdad discutida

La tesis SHALL reportar en el resumen y el abstract ambos coeficientes kappa con su
naturaleza: 0,87 de la campaña 2026-10 (sin intervalo; tabla primaria no conservada) y
0,5569 de la campaña complementaria (moderado; IC [0,4725; 0,6413]; tabla primaria
conservada con SHA-256). La seccion 9.4 (`08-discusion.tex`, limitaciones) SHALL agregar
una limitacion sobre la fiabilidad de la referencia de verdad de las metricas primarias,
con la concordancia del consenso `E1 = E2` con la referencia original (116 de 138,
84,1 %). La segunda contribucion de 10.2 (`09-conclusiones.tex`, "doble etiquetado")
SHALL matizarse con el kappa moderado de la campaña complementaria. El capitulo 10 SHALL
incluir una conclusion sobre el kappa moderado y sobre el efecto de posicion
significativo para `O2`.

#### Scenario: Ambos kappa en el resumen

- **WHEN** se lee el resumen y el abstract
- **THEN** figuran 0,87 (sin intervalo, tabla no conservada) y 0,5569 con su IC [0,4725; 0,6413]
- **AND** el resumen no informa unicamente el 0,87

#### Scenario: Limitacion de la referencia en 9.4

- **WHEN** se leen las limitaciones de la discusion (9.4)
- **THEN** una limitacion declara la fiabilidad moderada de la referencia nueva y la concordancia de 116 de 138 (84,1 %) con la referencia original
- **AND** declara que las metricas primarias se calculan contra la referencia original y heredan su incertidumbre

#### Scenario: Contribucion matizada y conclusiones completas

- **WHEN** se lee el capitulo 10
- **THEN** la segunda contribucion menciona el kappa moderado de la campaña complementaria
- **AND** el capitulo concluye sobre el efecto de posicion significativo para `O2`

### Requirement: Trazabilidad de la version entregada en la portada y en la implementacion

La portada (`00-portada.tex`) SHALL fecharse en la fecha de la release que la contiene o
en una posterior a las tablas primarias de la campaña complementaria (8-11-2026) y MUST
NOT conservar "30 de octubre de 2026". La seccion 6.1 (`06-implementacion.tex`) SHALL
declarar que la configuracion entregada construye una imagen derivada de N8N
(`docker/n8n/Dockerfile`, `FROM n8nio/n8n:2.11.2` con el parche de decodificacion IMAP de
c-182), coherente con la Tabla 19.

#### Scenario: Portada fechada

- **WHEN** se lee la fecha de `00-portada.tex`
- **THEN** no es "30 de octubre de 2026"
- **AND** es la fecha de la release `v1.2.11` o posterior al 8-11-2026

#### Scenario: Imagen derivada en 6.1

- **WHEN** se lee la seccion 6.1
- **THEN** se declara la imagen derivada de N8N de la configuracion entregada con su change (c-182)
- **AND** la declaracion coincide con la fila de la imagen de N8N de `tab:configuracion-evaluada-entregada`

### Requirement: Consistencia de los parrafos de la campaña complementaria

Los parrafos que este change reescribe SHALL cumplir: el parrafo inicial de la seccion 8
(`07-resultados.tex`) SHALL fechar las corridas del brazo automatizado "del 2 y del 5 y
6 de octubre"; `subsec:resultados-campana-medicion` MUST NOT afirmar que los tiempos de la
campaña alimentan "únicamente" el analisis del efecto de orden, porque tambien alimentan
la proporcion del tiempo; el rotulo "campaña de medición" SHALL reemplazarse por
"campaña 2026-10" o "campaña complementaria" segun corresponda en las leyendas de las
Figuras 3 y 4, el pie de la Tabla 5 (`05-arquitectura.tex`), el Anexo B y la Tabla 19;
la frase de 10.2 (`09-conclusiones.tex`) que califica al LLM como "alternativa
técnicamente viable" SHALL llevar "dentro de la muestra"; la cifra orientativa de
"5.000 casos" SHALL aparecer una sola vez en el documento, con remisiones en los demas
lugares; y la "cota pesimista" de 9.4 (`08-discusion.tex`) SHALL llevar el mismo
calificativo de interpretacion que 8.5.

#### Scenario: Fechas de corrida

- **WHEN** se busca "2 y el 6 de octubre" en `07-resultados.tex`
- **THEN** no hay coincidencias
- **AND** el parrafo inicial dice "del 2 y del 5 y 6 de octubre"

#### Scenario: Rotulo de campaña unificado

- **WHEN** se busca "posterior a la campaña de medición" en `sections/*.tex`
- **THEN** no hay coincidencias
- **AND** las leyendas de las Figuras 3 y 4 y el pie de la Tabla 5 dicen "campaña 2026-10" o "campaña complementaria"

#### Scenario: Calificativos y unicidad

- **WHEN** se busca "técnicamente viable" en `09-conclusiones.tex` y "5.000" (o su forma LaTeX) en `sections/*.tex`
- **THEN** la frase de 10.2 lleva "dentro de la muestra"
- **AND** la cifra de 5.000 casos aparece en un solo lugar

#### Scenario: Unicamente retirado

- **WHEN** se lee el primer parrafo de `subsec:resultados-campana-medicion`
- **THEN** no dice que los tiempos de la campaña alimentan "únicamente" el efecto de orden
- **AND** menciona la proporcion del tiempo como otro uso de esos tiempos

### Requirement: Trazabilidad del dictamen del 8 de noviembre en el registro y en el Anexo I

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL incluir una seccion del change
c-187 con la matriz recomendacion → ubicacion → correccion para A1-A5, B1, B2, B3 y B6, la
nota de verificacion del mecanismo de derivacion, la decision sobre el patron de release
y el conteo final de paginas y palabras. El Anexo I (`sec:anexo-trazabilidad`,
`12-anexos.tex`) SHALL incluir una tercera tabla con etiqueta
`tab:anexo-trazabilidad-0811` y la estructura comun de las tablas del 22 y del 28 de
octubre (recomendacion, change, secciones), con filas para A1-A5, B1, B2, B3 y B6 y una
fila que remita B4, B5, B7 y C1-C5 a un change posterior. El parrafo introductorio del
Anexo I SHALL declarar seis dictamenes, entre el 20 de octubre y el 8 de noviembre de
2026. El anexo MUST NOT contener numeros de linea de las fuentes.

#### Scenario: Tercera tabla del Anexo I

- **WHEN** se compila la tesis y se lee el Anexo I
- **THEN** existe `tab:anexo-trazabilidad-0811` con filas A1-A5, B1, B2, B3, B6 y la fila de remision de B4, B5, B7 y C1-C5
- **AND** cada fila remite con `\autoref` a secciones o tablas que contienen lo atendido

#### Scenario: Cantidad de dictamenes actualizada

- **WHEN** se lee el parrafo introductorio de `sec:anexo-trazabilidad`
- **THEN** declara seis dictamenes hasta el 8 de noviembre de 2026
- **AND** no queda "cinco dictámenes" ni "entre el 20 y el 28 de octubre"

#### Scenario: Registro del change

- **WHEN** se lee `dictamen-correcciones.md`
- **THEN** figura la seccion de c-187 con la matriz, la nota de verificacion, la decision del patron de release y los conteos

### Requirement: Neutralidad de paginas y palabras de las correcciones del dictamen del 8 de noviembre

Las correcciones de c-187 MUST NOT aumentar el total de paginas del PDF compilado
respecto de la release `v1.2.10` (118 paginas). El resumen y el abstract MUST NOT superar
250 palabras cada uno y el parrafo de viabilidad MUST NOT superar 34 palabras, medidos con
el mismo procedimiento que c-169. La compilacion SHALL terminar sin errores fatales ni
referencias o citas indefinidas y `verify_citations.py` SHALL quedar en PASS.

#### Scenario: Paginas sin aumento neto

- **WHEN** se compila `main.tex` tras aplicar el change
- **THEN** el total de paginas es menor o igual que 118
- **AND** el conteo se registra en `dictamen-correcciones.md`

#### Scenario: Topes de palabras

- **WHEN** se cuentan las palabras del resumen, del abstract y del parrafo de viabilidad
- **THEN** el resumen y el abstract tienen a lo sumo 250 palabras y el parrafo de viabilidad a lo sumo 34
- **AND** los conteos se registran en `dictamen-correcciones.md`
