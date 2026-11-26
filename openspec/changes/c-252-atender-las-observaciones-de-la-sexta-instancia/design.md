# Design: Atender las observaciones de la sexta instancia del tribunal

## Context

Ver `proposal.md` — Why. Estado verificado el 2026-11-26 sobre `main` (v1.6.5, 159 páginas, tag
`v1.6.5`). La devolución de sexta instancia (APTA PARA DEFENSA, 7,5/10) auditó la v1.6.5 contra las
correcciones C-01 a C-07 de la quinta instancia: C-03, C-04 y C-05 quedaron corregidas, C-07 casi
corregida, y C-01/C-02/C-06 atendidas dentro del reencuadre pero **sin documentación**, que pasa a D-01,
D-02 y D-03. A diferencia de c-250, aquí **cuatro decisiones de hecho siguen ABIERTAS** (OQ-01 a OQ-04) y
el tribunal **reinstala el visto bueno escrito del director** como condición para fijar fecha.

- **Mapa archivo→capítulo (obligatorio).** El nombre del `.tex` NO coincide con el número del capítulo
  rendido: Ch4=`04-marco-metodologico.tex`, Ch7 (legal, reubicado por c-105)=`11-aspectos-legales.tex`,
  Ch8=`07-resultados.tex`, Ch9=`08-discusion.tex`, Ch10=`09-conclusiones.tex`, Anexos=`12-anexos.tex`,
  Resumen/Abstract=`00-resumen.tex`. Las remisiones de tarea usan el nombre de archivo; la prosa usa el
  número de capítulo rendido. Los labels usados: Tabla 3=`tab:variables` (`04:31`), Tabla 4=
  `tab:procedencia-numeros` (`04:71`), Figura 11=`fig:cronograma` (`12:53`), Anexo I.1=
  `subsec:nota-versiones` (`12:239-247`), Anexo I.2=`sec:anexo-trazabilidad` (`12:251`).
- **Detección de ausencias (radar de c-252, verificado en v1.6.5):** (1) los commits `68d06ec`/`ea62576`
  no aparecen en `S/`; (2) el Anexo I.1 no registra ni el cambio de fechas (junio–agosto→octubre) ni el
  de definición del tiempo manual; (3) el Anexo I.2 se detiene en la cuarta instancia (19-11) sin quinta
  ni sexta; (4) "del sector servicios y con sede en la provincia de Mendoza" sobrevive en `01:16` y
  `09:52`; (5) la frase "retirado el componente de carga" (`04:127`) y "ya no contempla" (`12:354`)
  sugieren una corrección de datos que no ocurrió; (6) "redactadas por los autores" (`12:149`) vs "por uno
  de los autores" (`04:129`, `09:54`) conviven.
- **Cifras canónicas (frozen).** Media manual 61,57 s, automatizada 17,76 s; telefonía 87,2 s / 20,09 s;
  sin telefonía 44,1 → 16,2 s (63,3 %, IC 95 % [56,1; 69,6]); con 10 s de descuento 51,6 s / 65,6 %.
  Todas confirmadas por la sexta instancia. Solo OQ-2 puede cambiar la cifra primaria (71,2 % vs 65,6 %).
- **Precedentes.** c-249 (compuertas abiertas, grupos gated vs. sin compuerta, TDD de prosa ANTES/DESPUES,
  script TDD aditivo) es el template de c-252, combinado con c-250 (release + reencuadre de procedencia +
  registro en `dictamen-correcciones.md`). c-252 produce la versión de defensa `v1.6.6`.
- **Reglas vigentes.** La regla de tags de c-249 OQ-05 rige para `v1.6.6`; los tags anteriores son
  inmutables. Presupuesto del Resumen/Abstract (250 palabras) se conserva; el tope de páginas queda en el
  mismo estado de exceso declarado.

## Goals / Non-Goals

**Goals:**

- Cerrar D-01 a D-03 (las tres observaciones que el tribunal exige incorporar a la versión de defensa) con
  cronología día por día, definición del tiempo manual registrada y origen del régimen (a) sin léxico de
  organización, cada una con su evidencia y su registro en la Nota de versiones.
- Resolver D-04 (extensión de descripciones), D-05 (propagación a Resumen/Abstract/Tabla 10 + Anexos I.1/I.2)
  y D-06 (coherencia) en la misma versión.
- Producir la versión de defensa `v1.6.6` con la trazabilidad de c-250, BLOQUEADA por el visto bueno escrito
  del director.
- Registrar las cuatro compuertas OQ-01 a OQ-04 (respuesta literal, fecha, responsable) y las tablas
  ANTES/DESPUES en la sección c-252 de `dictamen-correcciones.md`.

**Non-Goals:**

- No inventar hechos de cronología, medición, ámbito laboral ni autoría: todo queda pendiente de OQ-01 a
  OQ-04 y se codifica tal cual, no se asume.
- No cambiar cifras canónicas salvo lo que OQ-2 determine; no editar casos del corpus ni sus JSON (SHA-256
  `1fd17d7e...` protegido); el campo `metadata.descripcion` histórico (`12:151`) queda intacto.
- No tocar `App/`, `n8n/` ni artefactos existentes de `evaluation/` (solo se AGREGA un script con su prueba
  y su salida).
- No mover, borrar ni recrear `v1.6.5` ni anteriores.
- No publicar el tag `v1.6.6` sin el visto bueno escrito del director.

## Decisions

### D1 — ADDED sobre tres capacidades existentes, sin capacidades nuevas

Como c-250, los requisitos nuevos se AGREGAN a `tesis-reencuadre-cuarta-instancia` (D-01, D-02, D-03, D-06),
`tesis-numeros-canonicos` (D-04, y la cifra primaria de D-02) y `tesis-document` (D-05 + release). No se
introduce capacidad nueva: las observaciones completan las existentes y no contradicen los requisitos de
instancias previas salvo en el punto D-02, que se resuelve como corrección (no MODIFIED, para no re-escribir
bloques enteros de c-249/c-250).

### D2 — Cuatro compuertas RESUELTAS OQ-01 a OQ-04 + aval del director (2026-11-26)

Las cuatro compuertas fueron respondidas por los autores el 2026-11-26. El apply CODIFICA cada decisión, no la
pregunta, y NO debe inventar ningún hecho adicional. Respuestas literales registradas:

- **OQ-01 (D-01) — RESUELTA.** El orden real fue **automatizado primero (2026-10-02, corrida de 119 correo/
  formulario) y manual después (el 09-10, posterior al doble etiquetado)**. El flujo manual NO precedió al automatizado.
  Desglose día por día: 01/10 notificación; 01–02/10 recolección + redacción; 02/10 automatizado; 05–06/10 telefonía;
  06–09/10 doble etiquetado; 09/10 cronometraje manual; 09/10 versionado. Los 165,3 s del 3 de julio se declaran como
  valor del corpus sintético (simulado), no una medición real.
- **OQ-02 (D-02) — RESUELTA.** El `tiempo_manual_s` **NUNCA incluyó** el componente "~10 s de carga": es la
  clasificación pura (lectura + decisión). La descripción de la v1.6.4 (lectura + carga ~10 s) era **inexacta** y la
  Nota de versiones debe decirlo. La cifra primaria de la sub-hipótesis 1 **se mantiene en 71,2 %** (no baja a
  65,6 %). El `-10 s` del Anexo de sensibilidad es el escenario adverso que el tribunal (C-02) pidió cuantificar
  cuando la descripción aún incluía la carga: NO es "remoción de carga" (nunca la hubo) ni "sensibilidad de
  redondeo" (el redondeo a múltiplos de 5 s es < 5 s por caso y queda como sensibilidad separada).
- **OQ-03 (D-03) — RESUELTA.** Los incidentes del régimen (a) **sí** provienen del ámbito laboral de los reportantes
  del círculo, **disociados desde la recolección** (nunca se registró un original con identificador). Corresponde
  citar el **art. 10** (deber de confidencialidad) y corregir `11:18` (deja de negar "información de sistemas ajenos").
- **OQ-04 (D-06) — RESUELTA.** A1 y T1 cronometraron **juntos, en el domicilio de uno de los autores** (no en
  domicilios distintos). "Por pares" es coherente: estaban físicamente reunidos. La atribución de las 81
  reconstrucciones se unifica a una sola forma.

Además, **aval del director:** el visto bueno escrito del director sobre la procedencia declarada (D-03) y sobre
la versión de defensa es una condición del tribunal y bloquea el grupo de release (HIGH). Ninguna tarea de
release se ejecuta antes de ese visto bueno. El origen por **disociación (irreversible)** se confirma: NO hubo
pseudonimización reversible.

### D3 — D-01: cronología día por día declarada, cronometraje acotado por el commit del 09/10

La evidencia fechada que el repo SÍ posee son los commits `68d06ec` (sintético, 2026-06-11) y `ea62576`
(real, 2026-10-09). La cronología fina es una **declaración de los autores**, ya resuelta (OQ-01):

| Fecha (oct. 2026) | Hecho |
|---|---|
| 01/10 | Notificación verbal al círculo («se usarían sus incidentes») — acta T2 |
| 01–02/10 | Recolección y redacción disociada de los 119 casos (simultáneas) |
| 02/10 | Consentimiento verbal + **corrida automatizada** de los 119 (correo+formulario) — `corpus_resultados_web_correo.json` |
| 05–06/10 | Corrida telefónica (81, recitada) |
| 06–09/10 | Doble etiquetado con consenso supervisado |
| **09/10** | **Cronometraje manual por pares (A1 y T1), posterior al etiquetado** |
| 09/10 | Versionado del corpus con `tiempo_manual_s` — commit `ea62576` |

El orden real es **automatizado primero (02/10), manual después (09/10)**: el flujo manual NO precedió al
automatizado (corrige §4.2 `04:14`). El cronometraje manual **posterior al doble etiquetado** implica que el
operador ya conocía el caso, por lo que el tiempo manual (61,6 s) está **sub-estimado** y la reducción (71,2 %)
es una **cota inferior** —sesga en contra de la hipótesis, coherente con la octava amenaza—. Se corrige: §4.8
primera amenaza (`04:117`) para declarar la dirección del efecto de aprendizaje (conservadora), y §9.1 tercera
explicación rival (`08:22`) para que diga "cronometraje manual posterior al etiquetado sesga en contra de la
hipótesis" (hoy dice "manual antes que automatizado"). §4.2/§4.4/Tabla 4/Figura 11 declaran la fecha del
cronometraje como **declaración de los autores, acotada por el commit del 09/10**. Los 165,3 s del 3 de julio
se declaran como valor del corpus sintético (simulado), no medición real; se consignan como histórico.

### D4 — D-02: la definición del tiempo manual zanja la contradicción c-250/c-251

La sexta instancia observa que v1.6.4 (lectura + carga ~10 s) y v1.6.5 (sin componente de carga) describen
el mismo dato y no pueden ser ambas ciertas. Existe además una contradicción heredada: c-250 (D4) etiqueta el
`-10 s` del Anexo de sensibilidad como "sensibilidad de redondeo", mientras c-251 (E5, en curso) lo lee como
"herencia del componente de carga retirado". OQ-02 RESUELTA (**nunca se sumó**: el ~10 s nunca existió en los
datos; la v1.6.4 lo describía mal). El apply:

1. Registra en Anexo I.1 que la descripción correcta es "clasificación pura sin carga" y que la v1.6.4 era
   inexacta al declarar una carga ~10 s.
2. Reemplaza "retirado el componente de carga" (`04:127`) y "componente que la presente versión ya no
   contempla" (`12:354`) por redacción que no sugiera un cambio en los valores.
3. Fija la cifra primaria en **71,2 %** (no 65,6 %) y **unifica la etiqueta del `-10 s` en
   `tesis-numeros-canonicos`** como "escenario adverso que el tribunal (C-02) pidió cuantificar cuando la
   descripción aún incluía la carga", resolviendo la contradicción entre c-250 D4 ("redondeo") y c-251 E5
   ("carga retirada"). c-251 E5 MUST NOT re-narrar el Anexo como "remoción de carga" cuando le toque su turno
   (ver D10).

### D5 — D-03: ámbito laboral declarado una sola vez, art. 10, disociación irreversible

OQ-03 RESUELTA (**ámbito laboral sí, disociado desde la recolección**). Se cita el deber de confidencialidad del
art. 10 (Ley 25.326) junto a la tríada CIA y se explica el léxico corporativo (`11:18`, §4.4, R015 `07:277`):
los incidentes provienen de los trabajos de los reportantes del círculo, disociados desde su recolección (nunca
se registró un original con identificador). Se retira "del sector servicios y con sede en la provincia de
Mendoza" de `01:16`, `09:52` y `01:76`, o se explica a qué se refiere, coherente con el origen laboral declarado.
Se corrige `11:18` para no negar que se trató información de sistemas ajenos: la licitud se funda en la
disociación (arts. 2 y 28), no en "no hay sistemas ajenos". El cambio de origen se registra en el Anexo I.1 como
corrección de veracidad. Como en c-250, el capítulo legal es HIGH: el texto propuesto se muestra a los autores
(y al director, por el aval) antes de escribir. La procedencia se formula UNA SOLA vez y con claridad en §4.4.

### D6 — D-04: script TDD aditivo de extensión de descripciones

`evaluation/data/campana/analisis/analisis_sexta_instancia_c252.py` con
`test_analisis_sexta_instancia_c252.py` escrito primero (Strict TDD), siguiendo el patrón de
`analisis_regimen_c249.py`: lee `data/corpus_evaluacion_pseudonimizado.json` (campo `descripcion`), agrupa por
`canal_origen`, computa media de palabras y de caracteres por canal y por régimen ((a) = correo+formulario, (b)
= telefonía), y escribe `.json`, `.md` y `SHA256SUMS.txt` deterministas. La prosa de §4.4/§4.8 cita esas
cifras y separa lectura de decisión en los 87,2 s manuales. No se edita el corpus (SHA-256 congelado).

### D7 — D-05: propagación y trazabilidad de instancias

El Resumen/Abstract (`00-resumen.tex`) y la Tabla 10 ganan "solo clasificación, no registro" + "63,3 % sin
telefonía". El Anexo I.1 registra el cambio de fechas y el de definición. El Anexo I.2 suma quinta (25/11) y
sexta (26/11). Se versiona la transcripción `.md` de la sexta instancia con el bloque de metadatos del formato
de la quinta.

### D8 — D-06: coherencia (domicilio/por pares, atribución, respaldados, titulares, barra)

OQ-04 RESUELTA (juntos, en el domicilio de uno de los autores): aclarar "por pares" en `04:16` para que diga que
A1 y T1 cronometraron juntos, en un único domicilio (no "en su domicilio" ambiguo ni domicilios distintos);
unificar la atribución de las 81 reconstrucciones (una sola forma); §8.1 usa la fórmula de §4.5 en vez de
"respaldados por" (`07:38`); §7.5 no afirma "titulares… distintos de los autores" (`11:46`); "histórico/retirado"
(`12:247`) se reemplaza por forma sin barra.

### D9 — Release v1.6.6 como versión de defensa, bloqueada por el aval del director

Bump `v1.6.5` → `v1.6.6` en portada, Anexo B, Nota de versiones, `.bib`, `README.md`, `knowledge-base/` y
`inventario-uso-asistentes-ia.md`. Regla de tags de c-249 OQ-05. **Condición de release (nueva):** D-01 a D-03
aplicados + visto bueno escrito del director; sin ambos, el tag `v1.6.6` no se publica. Registro en
`dictamen-correcciones.md` (sección c-252), `CHANGES.md`, `respuestas-tribunal-sexta-instancia.md` (10 preguntas
de la sección 6) y `respuestas-tribunal.md`.

### D10 — Coordinación con c-251 (auditoría Gonzalo, en curso)

c-251 (0/23 tareas, en curso) toca los mismos archivos en puntos distintos: E1/E2/E3 en
`11-aspectos-legales.tex` (art. 28, fecha de notificación, frase v1.6.0), E4 en `08-discusion.tex` (asimetría de
alcance) y E5 en `12-anexos.tex`/`04` (etiqueta del `-10 s`). Coordinación decidida:

- **E1–E4 son independientes de c-252** y pueden completarse por su propia vía; no hay conflicto textual con
  D-01..D-06.
- **E5 colisiona con D-02.** OQ-02 RESUELTA (c-252) en "nunca se sumó": E5 debe alinearse a "escenario adverso que
  el tribunal pidió cuantificar cuando la descripción aún incluía la carga ~10 s" y NO re-narrar el Anexo de
  sensibilidad como "remoción de carga" (nunca la hubo) ni como "sensibilidad de redondeo" (el redondeo es < 5 s).
  La decisión se registra en `dictamen-correcciones.md` y en el `tesis-numeros-canonicos`.
- La recomendación al equipo es **cerrar OQ-02 antes** de aplicar E5, para no re-tocar el mismo párrafo dos veces.

### D11 — Verificación estilo prosa TDD y TDD real donde hay código

Cada tarea de edición corre un `rg` ANTES (muestra el defecto) y DESPUES (estado deseado), registrados en la
sección c-252. Los números de línea son de v1.6.5 y el apply los re-verifica (las ediciones los desplazan). El
script de D6 sigue RED-GREEN-TRIANGULATE-REFACTOR con `pytest`. Las compuertas OQ-01 a OQ-04 se registran con
respuesta literal, fecha y responsable.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| [Inventar la cronología día por día o el ámbito laboral sin respuesta de OQ] | D2/D3/D5: las tareas gated no se tocan hasta la respuesta literal registrada; `rg` ANTES/DESPUES sobre los hechos |
| [Redactar "retirado el componente de carga" como si hubiera cambiado el dato] | D4: reemplazo por forma que no sugiera cambio de valores; verificación por `rg` |
| [Dejar dos etiquetas contradictorias del `-10 s` (c-250 redondeo vs c-251 carga)] | D4/D10: OQ-02 es fuente única; el `tesis-numeros-canonicos` fija una etiqueta |
| [Conservar "del sector servicios y con sede en la provincia de Mendoza" en alguna mención] | D5: barrido `rg` de la cadena; ANTES 3×, DESPUES resuelta (retirada o explicada) |
| [Publicar el tag `v1.6.6` sin el visto bueno del director] | D9: gate explícito; `git rev-parse v1.6.6^{commit}` no debe existir antes del aval |
| [Copiar las extensiones de descripciones del dictamen en vez de computarlas] | D6: script TDD con prueba; la prosa cita la salida versionada |
| [Editar el capítulo legal o `data/README.md` sin revisión (HIGH)] | Texto propuesto mostrado a autores+director antes de escribir |
| [Nombres reales o correspondencia alias-identidad en prosa nueva] | Solo alias (`A1`, `T1`, `E1`, `E2`, `O1`, `O2`); barrido final del diff |
| [Romper el hash del corpus] | Los JSON no se editan; `sha256sum` antes y después |

## Migration Plan

1. Registrar la recepción de la sexta instancia y las cuatro compuertas RESUELTAS (OQ-01 a OQ-04) en la sección
   c-252 de `dictamen-correcciones.md`, con la tabla de decisiones cerradas (respuesta literal, fecha, responsable).
2. Obtener el visto bueno escrito del director sobre la procedencia declarada y la versión de defensa (gestión
   HIGH, previa al grupo de release).
3. Script de análisis D-04 (D6) y las tareas no-gated (D-05, partes de D-06), con ANTES/DESPUES por tarea.
4. Aplicar D-01, D-02, D-03 y las partes gated de D-06 con el texto propuesto mostrado antes de escribir.
5. Coherencia: cifras canónicas; residuos (`rg` de fórmulas retiradas); `openspec validate --strict`.
6. Release `v1.6.6` (HIGH): bump, recompilación, derivados, tag según c-249, `CHANGES.md`, registro y respuestas
   de defensa; solo tras D-01..D-03 aplicados y el aval escrito del director.

Rollback: hasta el paso 5 todo es prosa sin commit; se revierten los archivos tocados. El tag `v1.6.6` no se
publica hasta que su commit esté verificado y el director haya firmado.

## Open Questions

Ninguna abierta. Las cuatro compuertas quedaron CERRADAS por decisión de los autores el 2026-11-26. Se registran
aquí como cierre (respuesta literal + responsable; la fecha es 2026-11-26):

- **OQ-01 — CERRADA (D-01).** El orden real fue automatizado primero (02/10, 119 correo/formulario) y manual
  después (09/10, posterior al doble etiquetado). El manual NO precedió. Cronología fina registrada en D3. Los
  165,3 s del 3 de julio se declaran como valor del corpus sintético (simulado), no medición real.
- **OQ-02 — CERRADA (D-02).** El `tiempo_manual_s` nunca incluyó el ~10 s de carga (clasificación pura); la
  v1.6.4 estaba mal descrita. Cifra primaria 71,2 % (no 65,6 %). El `-10 s` del Anexo de sensibilidad es el
  escenario C-02, no "remoción de carga" ni "redondeo".
- **OQ-03 — CERRADA (D-03).** Los incidentes del régimen (a) provienen del ámbito laboral de los reportantes del
  círculo, disociados de forma irreversible desde la recolección. Corresponde citar el art. 10 y corregir `11:18`.
- **OQ-04 — CERRADA (D-06).** A1 y T1 cronometraron juntos, en el domicilio de uno de los autores (no en
  domicilios distintos). Atribución de las 81 reconstrucciones unificada a una sola forma.

Pendiente externo (no compuerta de autor): el **visto bueno escrito del director** sobre la procedencia declarada
y la versión de defensa, condición del tribunal que bloquea el grupo de release.