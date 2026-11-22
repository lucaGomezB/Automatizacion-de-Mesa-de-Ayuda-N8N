# Design: Responder las aclaraciones de procedencia del dictamen sobre v1.6.2

## Context

Ver `proposal.md` - Why. Estado y restricciones verificados sobre `main` (`fe9ad024`, arbol
limpio, mismas lineas que el tag `v1.6.2` salvo el hash del Anexo B):

- **Precedente inmediato c-246** (archivado 2026-11-20): cambio de prosa con compuertas de
  autores (OQ-01 a OQ-03), visto bueno del director como gate duro y "verificacion estilo prosa
  TDD" (`rg` ANTES/DESPUES registrado en `docs/Tesis/Correcciones/dictamen-correcciones.md`,
  seccion c-246, lineas ~6678-6770). c-247 reutiliza ese formato y su capacidad
  `tesis-reencuadre-cuarta-instancia`, que ya esta en `openspec/specs/` (240 lineas).
- **Contradiccion c-242 D5 / c-246 OQ-01.** c-242 D5 (18-11) declaro que la mezcla de regimenes
  esta en ambos canales, que la procedencia "no esta codificada" en ningun artefacto y que el
  documento MUST NOT declarar una proporcion numerica sin registro primario. c-246 OQ-01 (20-11)
  declaro 119 texto / 81 telefono por declaracion de los autores. Entre ambos no entro ningun
  registro primario. c-247 no resuelve cual es la verdadera: obliga a la tesis a declarar la base
  (declaracion sin registro por caso) o a retirar el desglose, segun decidan los autores.
- **Indicios del dictamen sobre el regimen (a)** (no prueban quien reporto): descripciones en
  tercera persona con lexico de clientes, sucursales y estados de cuenta (R016, R043, R165-R167,
  R180); `data/README.md` declara que los originales "contienen PII"; la Nota de versiones
  (`12-anexos.tex:237`) ubica un ambito laboral en una "compania financiera"; §4.4
  (`04-marco-metodologico.tex:46`) dice que las llamadas se recibieron "en su trabajo".
- **Metadato del corpus congelado.** `data/corpus_evaluacion_pseudonimizado.json`
  (`metadata.descripcion` = "200 casos reales ... los tiempos manuales corresponden a la
  clasificacion manual") tiene SHA-256 `1fd17d7e...`, citado en `04-marco-metodologico.tex`,
  `numeros-canonicos.md`, `tesis_para_agente.md` y artefactos de `evaluation/data/campana/`
  (predicciones y analisis). Editar el JSON cambia el hash y rompe esa cadena.
- **Cronologia del consentimiento hoy divergente:** tesis `11:30` (notificacion 2-10, firma
  20-11); acta T2 `docs/seguridad/acta-consentimiento-t2.md:7-9`, `:73-74` (informacion 1-10,
  consentimiento 2-10, "sin fecha de firma consignada aqui"); `docs/defensa/respuestas-tribunal.md:129`
  ("prestado el 2026-10-02"); acta T1 presentada como "firmada el 2026-10-01" con ocho lineas
  agregadas el 18-11 (`b01da04d`); firma de `A1` registrada el 20-11
  (`docs/campana-medicion/confirmacion-posterior-consentimiento.md:59`).
- **Restriccion de release vigente.** `tesis-document` "Publicacion de una release de correccion
  sin mover tags publicados" exige que un tag publicado MUST NOT borrarse, recrearse ni
  reapuntarse, y fija el patron C3 (tag) / C4 (hash), que es justamente lo que dejo en el arbol
  del tag un PDF compilado con el hash de otro commit.
- **Presupuesto del Resumen y del Abstract:** maximo 250 palabras cada uno (`tesis-document`
  "Presupuesto de palabras del resumen en espanol" y "English abstract"); hoy unas 207 y 197.
  El reencuadre del Resumen tiene unas 40 palabras de margen.

## Goals / Non-Goals

**Goals:**

- Convertir las tres aclaraciones de procedencia y la decision de release en compuertas OQ que
  bloquean solo sus tareas, para que el bloque A se aplique apenas respondan los autores.
- Llevar el reencuadre a sus consecuencias (bloques B, C y D) sin compuerta, porque son cambios
  de prosa que no dependen de hechos nuevos.
- Separar en cada pasaje lo que ocurrio (entorno real de recoleccion, mediciones) de lo que se
  supuso (escenario de 120 usuarios, 42 diarios, 2 min 45 s, 2.646).
- Mantener la verificacion estilo prosa TDD por tarea y registrar todo en
  `dictamen-correcciones.md` seccion c-247.

**Non-Goals:**

- No inventar quien reporto los incidentes, donde se cargaron, que se escucho, ni fechas.
- No cambiar cifras canonicas (61,6 s, 17,76 s, 71,2 %, 73,5 %, W = 363, 25,47 s, +18,72 h,
  a* = 43,07 %, c* = 898,8 s, etc.), citas ni conclusiones sin ratificacion de autores.
- No editar los casos del corpus ni `App/`, `n8n/`, `evaluation/`.
- No recompilar, bump ni tag; no mover ni borrar `v1.6.2`.
- No escribir nada en la fase de propose fuera de `openspec/changes/c-247-.../`.

## Decisions

### D1 - ADDED sobre la capacidad existente, no capacidad nueva

c-246 ya archivo `tesis-reencuadre-cuarta-instancia` en `openspec/specs/`. c-247 agrega
requisitos nuevos a esa capacidad (ADDED) en lugar de MODIFIED: los requisitos R-01 a R-07
siguen vigentes tal como estan y c-247 agrega exigencias que los completan (titularidad,
base de la composicion, lugar y escucha, cronologia unica, propagacion). La instruccion de
release (OQ-04) va como ADDED en `tesis-document`, junto a las reglas de release existentes.
Alternativa descartada: MODIFIED de R-02, R-03 y R-05. Obligaria a copiar bloques completos y
reescribir escenarios que siguen siendo verdaderos; el riesgo de perder detalle al archivar no
compensa.

### D2 - Compuertas OQ-01 a OQ-04 bloquean solo su bloque

Las tareas del grupo 3 (A, procedencia) quedan bloqueadas por la OQ que se indica en cada una;
los grupos 4 a 7 (B, C, D) no dependen de ninguna OQ salvo donde se marca. Esto difiere de
c-246, que bloqueaba toda escritura hasta todas las OQ: el dictamen deja claro que los bloques
B a D son "trabajo de prosa, no de medicion". Los pasajes que se tocan desde ambos bloques
(`01:72`, `04:46`, `11:40`) se editan una sola vez, en la tarea gated, y la tarea no gated
remite a ella.

### D3 - Ninguna resolucion inventada para la composicion 119/81

Opciones para la respuesta de OQ-01 (las decide el grupo):
(a) mantener el desglose y declararlo "declaracion de los autores sin registro de procedencia
por caso", con una oracion que reconozca que una version anterior del diseno lo describio como
mezcla en ambos canales; (b) retirar el desglose por canal y volver a la descripcion cualitativa
de c-242 D5, propagando el retiro a §4.4, §4.9 y la Nota de versiones. En ambos casos la
septima amenaza se conserva. El agente MUST NOT elegir.

### D4 - Metadato del corpus: no romper el hash congelado sin decision expresa

Opciones para la sub-pregunta de OQ-01 sobre `metadata.descripcion`:
(i) **recomendada**: no editar el JSON; corregir la descripcion en `data/README.md` y en el
Anexo F, declarando que la cadena del metadato ("200 casos reales", "clasificacion manual") es
historica y queda superada; el SHA-256 `1fd17d7e...` sigue valido;
(ii) editar `metadata.descripcion` y propagar el nuevo SHA-256 a todas sus menciones, lo que
toca `evaluation/data/campana/` (fuera del alcance de este change) y obliga a un change propio.
Cualquiera de las dos es una tarea de metadatos de datos gated por OQ-01; no cambia casos.

### D5 - Separar entorno real y escenario con dos oraciones, no con la formula hibrida

Donde hoy dice "entorno operativo del propio equipo, presentado como escenario de referencia
narrativo" (`01:16`, `01:62`, `01:72`, `01:76`, `04:46`, `08:22`, `08:50`, `09:51`), la prosa
SHALL usar dos oraciones: una para el entorno real de recoleccion (contenido segun OQ-01; si
OQ-01 no respondio, la oracion queda en una formulacion neutra que no afirma quien reporto y la
tarea gated la completa) y otra para el escenario de 120 usuarios como dispositivo de
dimensionamiento. Nada se "recolecta" ni se "recoge" en un escenario.

### D6 - Balance: magnitud independiente de N como lectura primaria

Resumen, `08:120`, `09:6` y `09:22` presentan como lectura primaria el ahorro neto por
incidente (nucleo de la formula, 43,82 - 0,735 x 22,06 - 0,0307 x 69,51 = 25,47 s-persona,
cota superior) con la exactitud y el costo de equilibrio; las +18,7 horas-persona quedan como
proyeccion sobre el volumen supuesto. Los valores no cambian; cambia el rotulo y el orden.

### D7 - Verificacion estilo prosa TDD (heredada de c-238/c-242/c-246)

Cada tarea de edicion corre un `rg` ANTES (muestra el defecto) y DESPUES (estado deseado), y
ambas salidas se registran en `dictamen-correcciones.md` seccion c-247. Los numeros de linea son
los de `main` `fe9ad024`; el apply los re-verifica con `rg` porque las ediciones previas los
desplazan. Patrones con `.` en lugar de vocales acentuadas para tolerar la codificacion.

### D8 - OQ-04: la decision de release es de autores y director

c-247 no toca tags ni PDF. Presenta tres opciones al grupo y al director, y deja la elegida
como instruccion en `dictamen-correcciones.md` para el change de release:
(A) **recomendada, compatible con la regla vigente**: `v1.6.2` queda inmutable y se registra
como superada con una nota de erratum (el PDF de su arbol imprime `17aa6d21`); la proxima release
compila en C3 un PDF cuyo Anexo B no imprime ningun hash (remite al tag y a `compilacion.md`), y
C4 consigna el hash y recompila; `compilacion.md` nombra el commit compilado en cada caso;
(B) no versionar PDF en el commit del tag (el PDF queda solo en `main` tras C4 o como adjunto de
la release); (C) regenerar el PDF despues de consignar el hash y mover el tag una sola vez: viola
"Publicacion de una release de correccion sin mover tags publicados" y exige un MODIFIED de ese
requisito aprobado expresamente.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| [El agente decide quien reporto los 119 casos o la base 119/81] | OQ-01 bloqueante; D3 lista opciones sin elegir; escenario "sin respuesta, la tarea queda bloqueada" |
| [Fundar una base para terceros que no existe, o negar terceros que si existen] | El requisito exige distinguir origen (quien reporto) de contenido (descripciones sin dato personal) y fundar el tratamiento de los originales con PII si hubo terceros |
| [Romper el hash `1fd17d7e...` del corpus] | D4: opcion recomendada no edita el JSON; la opcion (ii) se deriva a un change propio |
| [Mover el tag `v1.6.2`] | D8: Non-Goal; opcion (C) marcada como incompatible con la regla vigente |
| [Exceder 250 palabras en Resumen o Abstract] | Tarea con conteo ANTES/DESPUES; reemplazar, no agregar |
| [Cambiar una cifra al re-rotular] | Tarea de cifras canonicas intactas con `rg` antes/despues |
| [Editar `docs/seguridad/` sin revision (dominio HIGH)] | Tareas gated por OQ-03; el texto propuesto se muestra a los autores antes de escribir |
| [Nombres reales o correspondencia alias-identidad en la prosa nueva] | Regla de alias en cada tarea y `rg` final de nombres de sujetos |
| [Bloques B a D tocan los mismos parrafos que A] | D2: una sola edicion por pasaje compartido, en la tarea gated |

## Migration Plan

1. Presentar OQ-01 a OQ-04 a los autores (y OQ-04 tambien al director); registrar las respuestas
   literales con fecha y responsable en la tabla de compuertas de c-247.
2. Aplicar en paralelo los bloques B, C y D (sin compuerta) con ANTES/DESPUES por tarea.
3. Aplicar el bloque A a medida que llega cada respuesta OQ.
4. Coherencia: bateria `rg` de residuales, cifras canonicas, nombres, conteo del Resumen y del
   Abstract; compilacion de verificacion en directorio temporal solo si el apply la habilita.
5. Registrar en `dictamen-correcciones.md` seccion c-247 y dejar la instruccion OQ-04 para el
   change de release (recompilacion, bump, tag).
Rollback: cambio de prosa sin commit en esta fase; revertir los archivos tocados por el apply.

## Open Questions

- **OQ-01 (autores; bloquea 3.1 a 3.4).** (1) Los 119 incidentes del regimen (a), 66 de correo y
  53 de formulario: ¿los reportaron los propios autores, u otras personas (colegas, clientes) de
  los lugares de trabajo de uno o mas autores? (2) ¿Cuantos lugares de trabajo, de que tipo y en
  que periodo se recogieron los casos? (3) ¿Los originales con PII que menciona `data/README.md`
  eran datos de terceros? Si lo eran, ¿con que base se trataron (art. 5 de la Ley 25.326 o
  disociacion del art. 2) y quien los pseudonimizo? (4) La composicion 119/81: ¿se declara como
  declaracion de los autores sin registro por caso (D3 a) o se retira el desglose (D3 b)?
  (5) Metadato del corpus: ¿opcion D4 (i) o (ii)? (6) ¿Se retira "el corpus no proviene de una
  organizacion real" (`01:72`)?
- **OQ-02 (autores; bloquea 3.5 a 3.8).** (1) ¿Donde (lugar) y en que sistema (planilla,
  prototipo, otro sistema de tickets) cargaron `A1` y `T1` los 200 casos? (2) En los 81 casos
  telefonicos de junio a agosto, ¿que escucharon, si el audio se grabo el 5 y 6-10-2026
  (`04:66`, `04:89`)? (3) ¿Cual es la experiencia real de `A1` y `T1` (sin apelar al escenario)?
  (4) ¿`tiempo_manual_s` mide la carga completa del ticket o la clasificacion manual? (5) ¿Las
  "planillas de cronometraje" (`12:145`) existen? Si existen, ¿se versionan; si no, se retira la
  frase? (6) ¿Hubo corrida automatizada del corpus en septiembre? Si no, "septiembre a octubre"
  (`04:14`, `04:64`, `06:79`) pasa a "octubre"; si si, ¿cuando, y antes o despues de la
  notificacion del 2-10?
- **OQ-03 (autores; bloquea 3.9 a 3.13).** (1) ¿Que ocurrio el 1-10-2026 y el 2-10-2026
  (informacion, consentimiento verbal, notificacion)? Un solo vocabulario para tesis, acta T2 y
  respuestas. (2) Confirmar: acta T2 redactada el 2026-11-17 y firmada el 2026-11-20. (3) Nota de
  revision del acta T1 por las lineas agregadas el 2026-11-18 (`b01da04d`): texto aprobado.
  (4) Mencion del consentimiento escrito de `A1` (2026-11-20) en §7.5. (5) ¿La corrida de texto
  del 2-10 fue anterior o posterior a la hora de la notificacion? (6) ¿Por que `v1.6.0` afirmaba
  que "no se recabo el consentimiento de los titulares para la transferencia"? Una oracion.
- **OQ-04 (autores y director; bloquea 8.1).** Opcion de release D8 (A), (B) o (C), y texto de la
  nota de erratum de `v1.6.2`.
