# Proposal: Atender la devolucion de segunda instancia del tribunal sobre v1.2.18 (N-01 a N-16)

## Why

El tribunal emitio el 11-11-2026 la devolucion de segunda instancia sobre la version `v1.2.18`
(9-11-2026): "APTA PARA DEFENSA CON OBSERVACIONES MAYORES", calificacion 7,0/10 (antes 3,9/10
en la auditoria integral del 4-8-2026). La nota es definitiva, pero las correcciones de su
seccion 7 deben estar en el ejemplar que se lleve a la defensa; su ausencia se evaluara como
observacion no atendida. Son 16 observaciones (2 criticas, 6 altas, 5 medias, 3 bajas). Las
criticas son de procedencia y declaracion: el kappa de 0,87 sigue presentado como evidencia
aunque no tiene planillas y ya figuraba antes de que existiera el corpus real (N-01), y la tesis
no declara que la version de julio informo cifras de un corpus sintetico ni traza la auditoria
del 4 de agosto (N-02). Segun el propio tribunal, "no requieren codigo nuevo ni nuevas
mediciones": se resuelven con escritura y declaracion. Este change hace que el texto declare
solo lo que el repositorio respalda y deja marcado, sin redactarlo como hecho, lo que solo los
autores pueden aportar.

## What Changes

- **N-01 (critica)**: se retira el kappa de 0,87 como evidencia de fiabilidad del Resumen, el
  Abstract, 1.7, 4.8 y 9.3; 4.4 conserva una unica mencion que declara que las planillas no se
  conservaron y que el valor no se presenta como evidencia; la fiabilidad se estima con el kappa
  de 0,5569 (moderado) de la campana complementaria.
- **N-02 (critica)**: nota de versiones al inicio del Anexo I (cifras de la version de julio y
  su origen sintetico); la auditoria del 4-8-2026 pasa a ser la primera fila de la trazabilidad;
  la serie distingue auditoria del tribunal, autoevaluaciones con modelo de lenguaje y
  devolucion del 11-11; tabla nueva con el estado de N-01 a N-16.
- **N-03**: tabla nueva de tiempos manuales de la campana complementaria por operador y
  agregados (8.7), definicion de la tarea manual de esa campana (4.5) y dependencia del
  operador como explicacion rival (9.1).
- **N-04**: una sola descripcion de la seleccion de los 200 casos (muestreo no probabilistico
  por conveniencia), coherente en 4.4, Resumen, Abstract y 9.1; sesgo de seleccion en 4.8.
- **N-05**: 4.5, 8.1 y el Anexo F declaran que 119 tiempos automatizados (correo y formulario)
  no tienen registro primario conservado.
- **N-06**: la recitacion de las 81 llamadas por un autor pasa a amenaza a la validez (4.8) y a
  explicacion rival (9.1).
- **N-07**: sin identificadores de cambio (`c-NNN`, `C-NN`) fuera del Anexo I; sin oraciones de
  mas de 60 palabras en los capitulos 1, 4, 8 y 9.
- **N-08**: la Tabla 12 suma la exactitud contra el consenso independiente (110/138 = 0,797;
  Wilson [0,722; 0,856]) y la de la referencia original sobre los mismos 138; el veredicto de la
  tercera sub-hipotesis se mantiene sobre la referencia primaria y se transparenta el limite 0,856.
- **N-09**: la segunda sub-hipotesis pasa a "no concluyente, con estimacion puntual por encima
  de la cota" en todas sus apariciones; se declara que el denominador de 147 y la lectura de la
  regla se fijaron despues de conocer los datos y que p = 0,28 es unilateral.
- **N-10**: 6.7 informa la cobertura de sentencias del backend con commit, fecha y el comando del
  CI (el valor lo mide el orquestador; sin valor no se escribe cifra).
- **N-11**: las Figuras 2, 7, 8 y 10 se regeneran legibles a tamano de impresion.
- **N-12**: 10.1 sin valoraciones sin respaldo ni cifras repetidas del capitulo 8.
- **N-13**: 7.3 declara que no se suscribieron clausulas modelo ni se recabo consentimiento para
  la transferencia y deja el instrumento del art. 12 como requisito del adoptante.
- **N-14**: el Anexo I registra la confirmacion escrita del consentimiento como atendida el
  10-11-2026.
- **N-15**: nombres de sector con tilde en la prosa y `\texttt{}` sin tilde donde se cita la
  cadena del sistema.
- **N-16**: PENDIENTE de los autores (solo un comentario `% PENDIENTE-AUTORES(N-16)` en el `.bib`).
- Mecanismo transversal: lo que solo saben los autores queda como comentario LaTeX
  `% PENDIENTE-AUTORES(N-xx): ...` y el texto visible queda verdadero sin ese dato.

**Fuera de alcance:** nuevas mediciones (salvo la lectura de la cobertura del backend, N-10);
la release (version, tag y hash del Anexo B), que hace el orquestador con el usuario; N-16 y los
datos de los autores (origen y fecha del 0,87, periodo y criterio de seleccion, registro de los
119 tiempos, instrumentos firmados con Google o Twilio, declaracion del uso de modelos de
lenguaje en la redaccion); el change activo `c-191`; `App/`, `n8n/`, `docker/`.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- `tesis-document`: se modifican los requisitos del kappa de 0,87 (interpretacion, intervalos,
  resumen, atribucion de 1.6/1.7, fiabilidad de la referencia, valores canonicos de la campana y
  de la reduccion), del estado de la segunda sub-hipotesis y de su propagacion al memo, de la
  verificabilidad del muestreo, de los nombres de sector, de la trazabilidad de los controles y
  del cuerpo sin residuos; se reemplaza la regla de tres vias "asimetrica" por una regla con
  lectura posterior declarada; se agregan requisitos para la nota de versiones y la trazabilidad
  de la devolucion en el Anexo I, los tiempos manuales por operador, el registro primario de los
  tiempos, las llamadas recitadas, la exactitud contra el consenso, el cuerpo sin identificadores
  de cambio y oraciones acotadas, la cobertura del backend, las conclusiones sin valoraciones, el
  instrumento del art. 12, la legibilidad de figuras y el mecanismo de pendientes de los autores.
- `tesis-numeros-canonicos`: el kappa de 0,87 pasa de "vigente (sin IC)" a retirado como
  evidencia; el estado de la segunda sub-hipotesis se registra como no concluyente con ambos
  denominadores; se registran los tiempos manuales por operador y la exactitud contra el consenso.

## Impact

- Tesis: `docs/Tesis/v10 (IA)/paper/sections/{00-resumen,00-glosario,01-introduccion,04-marco-metodologico,05-arquitectura,06-implementacion,07-resultados,08-discusion,09-conclusiones,10-recomendaciones,11-aspectos-legales,12-anexos}.tex`,
  `docs/Tesis/v10 (IA)/Bibliography_base.bib` (solo comentarios N-16), `paper/figures/*.png` y
  `docs/diagrams/*.md` (N-11); `paper/compilacion.md`, `paper/main.pdf` y `tesis_para_agente.md`
  regenerados.
- Registro: `docs/Tesis/Correcciones/{dictamen-correcciones,numeros-canonicos}.md`; la
  devolucion del tribunal se versiona en `auditorias/`.
- Codigo: ninguno. La cobertura del backend se mide con el comando del CI, sin cambiar codigo.
- Gobernanza: texto de la tesis MEDIUM; aspectos legales (7.3) y consentimiento (Anexo I) HIGH
  en lo que afirman sobre hechos: solo se redacta lo que consta en el repositorio.
