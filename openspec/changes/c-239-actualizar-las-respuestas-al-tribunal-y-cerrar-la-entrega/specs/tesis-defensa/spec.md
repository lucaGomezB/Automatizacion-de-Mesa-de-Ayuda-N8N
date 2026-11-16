## MODIFIED Requirements

### Requirement: Documento de respuestas a las 16 preguntas del tribunal

El proyecto SHALL mantener el documento `docs/defensa/respuestas-tribunal.md` con exactamente 16 respuestas a la devolucion de segunda instancia, numeradas Q1 a Q16, una por cada pregunta de la Seccion 8 de la devolucion de segunda instancia del 11-11-2026, agrupadas en los cuatro bloques de esa seccion: procedencia de los datos (Q1 a Q4), contraste de tiempos (Q5 a Q9), clasificacion y supervision humana (Q10 a Q14) y marco legal (Q15 y Q16). Cada respuesta SHALL enunciar la pregunta y responderla de forma autonoma. Despues de esas 16 respuestas, el documento SHALL contener una seccion separada con las respuestas a las 12 preguntas de la Seccion 8 de la devolucion de tercera instancia del 16-11-2026 (requisito "Respuestas a las doce preguntas de la devolucion de tercera instancia"). El encabezado del documento SHALL nombrar las dos devoluciones a las que responde y la version del ejemplar corregido contra la que se verifico. El documento MUST NOT atribuirse a un modelo de lenguaje ni declarar autoria de IA.

#### Scenario: Las 16 respuestas presentes y numeradas

- **WHEN** se recorren los encabezados de `docs/defensa/respuestas-tribunal.md`
- **THEN** existen 16 respuestas identificadas Q1 a Q16, sin huecos ni duplicados
- **AND** cada respuesta reproduce la pregunta que responde

#### Scenario: Agrupacion en los cuatro bloques

- **WHEN** se leen las secciones de segunda instancia del documento
- **THEN** las respuestas se agrupan en los cuatro bloques de la Seccion 8 (procedencia, tiempos, clasificacion y supervision humana, marco legal)
- **AND** cada bloque contiene las preguntas que le corresponden (4, 5, 5 y 2)

#### Scenario: Encabezado con las dos devoluciones y la version verificada

- **WHEN** se lee el encabezado del documento
- **THEN** nombra la devolucion de segunda instancia (11-11-2026, sobre `v1.2.18`) y la de tercera instancia (16-11-2026, sobre `v1.5.2`)
- **AND** nombra la version del ejemplar corregido contra la que se cotejaron las respuestas

#### Scenario: Sin atribucion a un modelo de lenguaje

- **WHEN** se busca en el documento una atribucion de autoria a un modelo de lenguaje o a una herramienta de IA
- **THEN** no aparece ninguna
- **AND** el documento se presenta como respuesta del grupo

### Requirement: Cifras canonicas o recalculables

Toda cifra citada en una respuesta SHALL coincidir con un valor vigente del memo `docs/Tesis/Correcciones/numeros-canonicos.md` o SHALL ser recalculable desde los artefactos versionados, y SHALL figurar en el texto del ejemplar corregido o en la lista blanca justificada del cotejo. El documento MUST NOT introducir una cifra de resultado sin respaldo y MUST NOT reintroducir valores retirados: en particular, el kappa de 0,87 como evidencia de fiabilidad, las cifras de la validacion fuera de muestra retirada (por ejemplo `0,6893`, `142/206`, `0,7489`, los 206 casos o los 56 de refuerzo como evidencia) y los balances netos superados (`-18,5` a `-43,9` y `+30,6` horas-persona). Cuando una respuesta mencione un valor retirado, SHALL hacerlo solo para declarar que se retiro y por que.

#### Scenario: Cifra coincidente con el memo o recalculable

- **WHEN** se compara cada cifra del documento con el memo canonico y con el texto del ejemplar corregido
- **THEN** coincide con un valor vigente o se reproduce desde un artefacto versionado
- **AND** ninguna cifra queda sin fuente

#### Scenario: Valor retirado no reintroducido

- **WHEN** se busca el kappa de 0,87 en el documento
- **THEN** no aparece como evidencia de fiabilidad
- **AND** si se lo menciona, es para declarar que fue retirado y que sus planillas no se conservaron

#### Scenario: Cifras fuera de muestra y balances superados ausentes como evidencia

- **WHEN** se buscan en el documento `0,6893`, `142/206`, `206 casos`, `-18,5`, `-43,9` y `+30,6`
- **THEN** no aparecen como evidencia vigente
- **AND** toda mencion residual esta en una oracion que declara el retiro o la superacion del valor

### Requirement: El documento precede a su incorporacion como anexo

El documento `docs/defensa/respuestas-tribunal.md` SHALL ser el artefacto fuente de las respuestas
y SHALL existir antes de cualquier edicion de `12-anexos.tex` que lo incorpore o lo retire. La
decision de los autores registrada en `docs/Tesis/Correcciones/dictamen-correcciones.md` (OQ3 de
c-221, decidida el 2026-11-14) es **retirar** el anexo de respuestas; mientras esa decision siga
vigente:

- el documento SHALL conservarse como material de preparacion de la defensa, fuera del cuerpo y de
  los anexos de la tesis;
- `12-anexos.tex` MUST NOT contener la etiqueta `sec:anexo-respuestas-tribunal` y ninguna seccion de
  la tesis SHALL remitir a ella;
- el rotulo "Anexo J" de la tesis designa el anexo vigente de numeros canonicos citados y MUST NOT
  confundirse con el documento de respuestas.

Si los autores revirtieran la decision, el anexo SHALL reproducir el contenido del documento fuente
sin alterar las respuestas ni su numeracion, y MUST NOT incluir cifras de la validacion fuera de
muestra retirada. Mientras una nueva decision no este registrada, el estado vigente del anexo MUST
NOT cambiar.

#### Scenario: El documento fuente precede al anexo

- **WHEN** se verifica el orden de los entregables del change
- **THEN** `docs/defensa/respuestas-tribunal.md` existe con sus respuestas antes de cualquier edicion de `12-anexos.tex` que incorpore o retire el anexo de respuestas
- **AND** si el anexo se reincorporara, reproduce las mismas respuestas sin cambios de fondo respecto del documento fuente

#### Scenario: Anexo de respuestas retirado por decision de los autores

- **WHEN** la decision registrada es retirar el anexo
- **THEN** `12-anexos.tex` no contiene la etiqueta `sec:anexo-respuestas-tribunal`
- **AND** `docs/defensa/respuestas-tribunal.md` se conserva con sus respuestas
- **AND** la compilacion no informa referencias indefinidas

#### Scenario: Sin cifras fuera de muestra en un eventual anexo

- **WHEN** los autores registran la decision de reincorporar el anexo de respuestas
- **THEN** el anexo reproduce el documento fuente
- **AND** no contiene cifras de la validacion fuera de muestra retirada

## ADDED Requirements

### Requirement: Respuestas a las doce preguntas de la devolucion de tercera instancia

`docs/defensa/respuestas-tribunal.md` SHALL contener una seccion con 12 respuestas, numeradas P1 a P12, una por cada pregunta de la Seccion 8 de la devolucion de tercera instancia del 16-11-2026 (`auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md`), agrupadas en sus cuatro bloques: corpus fuera de muestra (P1 a P5), balance neto (P6 a P8), clasificacion (P9 y P10) y autoria (P11 y P12). Cada respuesta SHALL enunciar la pregunta, responderla de forma autonoma y terminar con una linea "Fuentes:". Las respuestas SHALL decir lo que el ejemplar corregido dice y lo que los autores confirmen:

- P1 a P5 SHALL explicar que la validacion fuera de muestra se retiro del ejemplar y por que, en los terminos de la nota de versiones del Anexo I.1 que fija `c-235`; cualquier hecho sobre quienes son `E3`, `E4` y `E5`, como se registraron o produjeron las marcas temporales, de donde provienen los textos de refuerzo, la autorizacion de la compania o la correspondencia de sectores SHALL provenir de una confirmacion escrita de los autores.
- P6 a P8 SHALL reflejar el balance neto vigente de `c-236` (costo `c` como cota inferior del tramo activo medido, balance `B` como cota superior con el termino de revision, lectura condicional) e incluir la recomendacion del grupo a una organizacion adoptante.
- P9 y P10 SHALL explicar que la conclusion de eficiencia queda acotada segun el ejemplar corregido y que aporta la etapa de reglas con las cifras dentro de la muestra vigentes.
- P11 y P12 SHALL coincidir con la declaracion de uso de asistentes de IA del Anexo I que fija `c-237` (subseccion `subsec:declaracion-uso-ia`), con su inventario `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` y con la distribucion del trabajo que confirmen los autores.

P1 a P5, P11 y P12 son **compuerta de autores**: mientras falte el insumo escrito de los autores, cada una SHALL quedar como borrador marcado `PENDIENTE-AUTORES(Pn)` y MUST NOT afirmar hechos de procedencia, autorizacion, autoria o verificacion no confirmados. Las respuestas MUST NOT usar nombres reales de personas: solo alias (`E1` a `E5`, `O1`, `O2`, "los autores", "el director").

#### Scenario: Las 12 respuestas presentes y agrupadas

- **WHEN** se recorren los encabezados de la seccion de tercera instancia
- **THEN** existen 12 respuestas identificadas P1 a P12, sin huecos ni duplicados, agrupadas en cuatro bloques de 5, 3, 2 y 2
- **AND** cada respuesta reproduce la pregunta y termina con una linea "Fuentes:"

#### Scenario: Compuerta de autores sin hechos no confirmados

- **WHEN** se lee P1 a P5, P11 o P12 antes de registrar el insumo escrito de los autores
- **THEN** la respuesta lleva la marca `PENDIENTE-AUTORES(Pn)`
- **AND** no afirma quienes son los etiquetadores, como se produjeron las marcas temporales, de donde provienen los textos, que existio una autorizacion ni que parte produjo un asistente de IA

#### Scenario: Respuesta cerrada con el insumo de los autores

- **WHEN** los autores entregan por escrito el insumo de una pregunta bloqueada y la respuesta se redacta
- **THEN** la marca `PENDIENTE-AUTORES(Pn)` se retira de esa respuesta
- **AND** el registro de trazabilidad consigna la fecha del insumo y que afirmaciones provienen de el

#### Scenario: Retiro explicado en el bloque del corpus fuera de muestra

- **WHEN** se lee el bloque P1 a P5
- **THEN** cada respuesta declara que la validacion fuera de muestra se retiro del ejemplar corregido
- **AND** el motivo coincide con el que declara la nota de versiones del Anexo I.1

#### Scenario: Balance y recomendacion al adoptante

- **WHEN** se lee P8
- **THEN** la respuesta presenta el balance como cota superior condicional con las cifras del ejemplar corregido
- **AND** formula una recomendacion a la organizacion adoptante coherente con Q14

#### Scenario: Sin nombres reales

- **WHEN** se buscan en el documento los nombres propios de los autores, directores o etiquetadores
- **THEN** no aparecen
- **AND** las personas se designan por alias o por rol

### Requirement: Coherencia del documento de respuestas con el ejemplar corregido

Cada respuesta del documento SHALL ser coherente con el ejemplar corregido posterior a `c-235`, `c-236`, `c-237` y `c-238` (observacion M-04 de la devolucion de tercera instancia). En particular: Q14 SHALL presentar el balance neto vigente de `c-236` (cota superior, termino de revision, lectura condicional) y la recomendacion al adoptante, y MUST NOT sostener el balance de `-18,5` a `-43,9` horas-persona; Q15 SHALL describir las transferencias a proveedores en los mismos terminos que el §7.3 y la nota de versiones del Anexo I.1 del ejemplar corregido, y MUST NOT afirmar que a los proveedores llegaron solo 119 textos y 81 audios si el ejemplar declara otras transferencias; Q16 SHALL reproducir o remitir a la declaracion de uso de asistentes de IA vigente del Anexo I (subseccion `subsec:declaracion-uso-ia` de `c-237`, con el texto fuente de su inventario) y MUST NOT citar la declaracion reemplazada. Q1 a Q13 SHALL revisarse contra el ejemplar corregido y conservar solo cifras dentro de la muestra vigentes. Las remisiones a secciones SHALL usar la numeracion de capitulos del PDF (por ejemplo, §7.3 para la transferencia internacional, aunque el archivo sea `11-aspectos-legales.tex`). El documento MUST NOT contener restos de sintaxis LaTeX (`~\%`, `{,}`, `\texttt`, `\ref`).

#### Scenario: Q14 alineada con el balance vigente

- **WHEN** se lee Q14
- **THEN** el balance coincide con el de la discusion (§9.5) y la tabla de balance del ejemplar corregido
- **AND** no aparecen `-18,5` ni `-43,9` como balance vigente

#### Scenario: Q15 alineada con las transferencias declaradas

- **WHEN** se compara Q15 con el §7.3 y el Anexo I.1 del ejemplar corregido
- **THEN** las transferencias a proveedores que declara Q15 coinciden con las del ejemplar
- **AND** Q15 no afirma una cota de transferencias que el ejemplar contradiga

#### Scenario: Q16 con la declaracion de IA vigente

- **WHEN** se compara Q16 con la subseccion `subsec:declaracion-uso-ia` del ejemplar corregido
- **THEN** Q16 reproduce o remite a la declaracion vigente
- **AND** no contiene la oracion de la declaracion reemplazada

#### Scenario: Sin restos de LaTeX

- **WHEN** se buscan en el documento las secuencias `~\%`, `{,}`, `\texttt` y `\ref`
- **THEN** no aparece ninguna

#### Scenario: Remisiones con la numeracion del PDF

- **WHEN** una linea "Fuentes:" remite a una subseccion de la tesis
- **THEN** el numero de subseccion coincide con el del PDF compilado
- **AND** el archivo `.tex` citado es el que contiene esa subseccion

### Requirement: Cotejo automatizado de las cifras del documento de respuestas

El proyecto SHALL proveer el script de solo lectura `docs/Tesis/Correcciones/cotejar_cifras_respuestas.py`, con pruebas en `docs/Tesis/Correcciones/test_cotejar_cifras_respuestas.py`, que extraiga las cifras numericas de `docs/defensa/respuestas-tribunal.md` (enteros, decimales con coma, porcentajes, fracciones `a/b` y valores con signo), las normalice y verifique que cada una figure en el texto extraido del ejemplar corregido o en una lista blanca versionada en la que cada entrada lleve su justificacion. El script SHALL informar ademas, como fallas, las cifras de una lista de valores retirados que aparezcan fuera de una oracion de retiro y los restos de sintaxis LaTeX. Su codigo de salida SHALL ser 0 solo si no hay fallas. El script MUST NOT modificar ningun archivo.

#### Scenario: Cifra presente en el ejemplar

- **WHEN** el documento cita `0,7971` y el texto extraido del ejemplar contiene `0,7971`
- **THEN** el cotejo da esa cifra por verificada

#### Scenario: Cifra ausente del ejemplar

- **WHEN** el documento cita una cifra que no figura en el texto del ejemplar ni en la lista blanca
- **THEN** el cotejo la informa como falla con su linea
- **AND** el codigo de salida es distinto de 0

#### Scenario: Valor retirado detectado

- **WHEN** el documento cita `0,6893` o `-43,9` en una oracion que no declara su retiro
- **THEN** el cotejo lo informa como valor retirado

#### Scenario: Ejecucion final limpia

- **WHEN** se ejecuta el cotejo sobre el documento final y el extracto regenerado del ejemplar corregido
- **THEN** informa 0 fallas
- **AND** el resultado queda registrado en la trazabilidad del change
