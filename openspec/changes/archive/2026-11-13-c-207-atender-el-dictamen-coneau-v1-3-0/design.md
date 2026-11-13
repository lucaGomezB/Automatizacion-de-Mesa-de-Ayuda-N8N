## Context

El dictamen CONEAU sobre `v1.3.0` (13-11-2026) fija seis recomendaciones necesarias antes de
la defensa. La rama `change/c-207-atender-el-dictamen-coneau-v1-3-0` está apilada sobre la
de c-205 (PR #94, sin integrar), de modo que el árbol de trabajo ya contiene el análisis
ampliado fuera de muestra (`analisis_fuera_de_muestra_c205.{py,json,md}`, sección 3.20 del
memo y la prosa nueva de `07-resultados.tex` y `08-discusion.tex`). c-206 (PR #95, arbitraje
de los `47` discordantes) está propuesto y sin ejecutar (`0/25` tareas en `openspec list`).

Verificaciones hechas al proponer (lectura del texto y de los artefactos; las cifras se
reconfirman con el script en la tarea correspondiente):

- **c-205 ya cubre** en `07-resultados.tex` (párrafo «Validación fuera de muestra») la
  macro-F1 `0,7447`, la *balanced accuracy* `0,7395`, las métricas por clase y el kappa del
  clasificador `0,7862`; y en `08-discusion.tex` (procedencia de los datos de ajuste) el peor
  caso `0,5800`, el mejor `0,8933`, la cota `0,8189` y la regla de decisión. Falta: una tabla
  en Resultados, el acuerdo entre etiquetadores `E3`/`E4` y el estado del arbitraje.
- **Acuerdo `E3`/`E4`**: no existe en ningún artefacto versionado. El `kappa` de
  `analisis_fuera_de_muestra_c205.json` es del clasificador contra la referencia. La tabla
  primaria `evaluation/data/campana/doble_etiquetado_independiente.csv` permite calcularlo con
  `evaluation/kappa.py::kappa_cohen`.
- **IC de la reducción del `71,2 %`**: no existe. `07-resultados.tex` y el memo (sección 3.1)
  informan solo el valor puntual (`71,16 %` en el memo); `evaluation/stats.py` no tiene una
  función de IC de la reducción. Los `200` pares están en
  `data/corpus_evaluacion_pseudonimizado.json` (`tiempo_manual_s`, `tiempo_automatizado_s`).
- **Balance neto (rec. 5)**: la sospecha tiene respaldo en el texto. La fórmula y la tabla
  `tab:balance-neto` usan `e_aut = 0,265 = 53/200`, medido contra el etiquetado original
  (exactitud `0,7350`). El párrafo siguiente deriva `e_man = 1 − 0,8278 = 0,1722` del brazo
  manual de la campaña complementaria, medido contra el consenso de `E1`/`E2` (138 casos, 151
  derivaciones) y recalcula `a*` con él, mientras la comparación sigue leyéndose contra el
  `73,5 %`. Contra ese mismo consenso el sistema da `110/138 = 0,7971`
  (`07-resultados.tex`, controles de referencia y «Exactitud del brazo manual»). La lectura
  preliminar indica que la asimetría existe y que con una referencia común el signo del
  balance podría cambiar; la confirmación y el recálculo son tareas del change, con código
  probado, y su resultado no se anticipa en el texto.
- **Consentimiento `E3`/`E4`**: `docs/campana-medicion/confirmacion-posterior-consentimiento.md`
  registra `fecha_informacion_verbal = 2026-11-10` y `fecha_confirmacion = por completar`.
  `11-aspectos-legales.tex` (consentimiento y derechos) habla solo de «los cuatro
  participantes» (`E1`, `E2`, `O1`, `O2`). La plantilla dice «campaña complementaria de
  medición» en el punto 1, que no describe la tarea de `E3`/`E4`.
- **Toolchain**: esta máquina no tiene `latexmk`, `xelatex` ni `biber`. `verify_citations.py`
  y `build_tesis_para_agente.py` son Python y sí corren aquí.

## Goals / Non-Goals

**Goals:**

- Cerrar las recomendaciones 1 a 6 con redacción y con cálculos sobre artefactos versionados.
- Que toda cifra nueva salga de un script de solo lectura, determinista y probado (TDD), y
  quede registrada en el memo con procedencia y comando.
- Que el texto afirme solo lo que el registro respalda (consentimiento, arbitraje).

**Non-Goals:**

- Recomendaciones 7 a 15 del dictamen (consistencia y forma): change posterior.
- Ejecutar el arbitraje de c-206, reunir casos nuevos o hacer corridas pagas.
- Editar `App/`, `n8n/`, `data/*`, `evaluation/*.py` del paquete, los corpus o los scripts de
  c-191 y c-205.
- Completar el registro de consentimiento (tarea humana) o recompilar el PDF aquí.

## Decisions

### D1. Un script único de solo lectura para las cifras nuevas

`evaluation/data/campana/analisis/analisis_dictamen_c207.py`, con
`test_analisis_dictamen_c207.py` al lado, siguiendo el patrón de c-205: importa (sin editar)
`evaluation/metrics.py` (`remuestreos_indices`, `percentil_intervalo`, `intervalo_wilson`,
`SEMILLA_BOOTSTRAP = 20261021`, `REMUESTREOS_BOOTSTRAP = 2000`, `NIVEL_CONFIANZA`),
`evaluation/kappa.py` (`kappa_cohen`), `evaluation/stats.py` y `evaluation/corpus.py`; escribe
`analisis_dictamen_c207.{json,md}` (UTF-8 sin BOM, LF), con los SHA-256 de cada entrada.
Bloques: `ic_reduccion_tiempo`, `acuerdo_e3_e4`, `balance_neto_referencia_comun`.

- *Alternativa descartada*: agregar funciones a `evaluation/stats.py`. Obliga a tocar un
  módulo con suite propia y amplía el radio del cambio; el patrón vigente (c-191, c-205) es
  el script de análisis aislado. Si más adelante se quiere reutilizar, se promueve en otro
  change.

### D2. IC de la reducción relativa del tiempo (rec. 6)

Estadístico: `R = 1 − media(automatizado) / media(manual)` sobre los `200` pares (el mismo
que produce el `71,2 %`). IC bootstrap percentil al 95 % remuestreando **pares** (casos) con
reemplazo, con la semilla y `B` del paquete. La prueba de reproducción exige que el valor
puntual coincida con `0,7116` (memo, sección 3.1) antes de aceptar el IC. Se informa además
el IC de la diferencia de medias en segundos (`43,82 s`), útil para el balance. El IC se
rotula como intervalo de la muestra por conveniencia (no extrapolable) y como cota superior,
igual que el valor puntual (manual redondeado al alza).

- *Alternativa*: retirar la promesa del cuarto objetivo. Descartada: el IC es computable con
  datos versionados y el dictamen prefiere informarlo.
- *Alternativa*: IC de la razón por método delta. Descartada: el bootstrap por caso es el
  procedimiento ya declarado en el paquete (c-108, c-167) y no supone normalidad.

### D3. Acuerdo `E3`/`E4` y tabla fuera de muestra (rec. 1)

El script calcula, sobre los `150` casos de `doble_etiquetado_independiente.csv` (sector
principal), la proporción de acuerdo observada (se espera `103/150`, que debe coincidir con
el n efectivo de c-191; si no coincide, se detiene y se reporta) y el kappa de Cohen con sus
IC asintótico y bootstrap mediante `kappa_cohen`. La tabla nueva de `07-resultados.tex`
(`tab:fuera-de-muestra`) reúne: n primario `150`, discordantes `47`, n efectivo `103`,
acuerdo y kappa `E3`/`E4`, exactitud estricta y laxa con IC de Wilson, ponderada `0,8146`,
macro-F1, *balanced accuracy*, kappa del clasificador, peor caso, mejor caso y cota. Todos los
valores salvo los de `acuerdo_e3_e4` ya están en las secciones 3.19 y 3.20 del memo y se
toman de allí. El párrafo de c-205 se conserva como lectura de la tabla; puede remitir a ella
en lugar de repetir cifras, sin borrar ninguna advertencia.

**Arbitraje**: el texto declara que el arbitraje de los `47` discordantes por un tercer
etiquetador está planificado y **no se ejecutó** en esta versión, por lo que la exactitud
fuera de muestra se informa sobre el n efectivo con el peor caso como cota. No se anticipa
resultado. Si los autores completan c-206 antes de la defensa, la incorporación es un change
posterior (c-206 la difiere expresamente).

### D4. Balance neto con referencia común (rec. 5)

Orden obligatorio:

1. **Confirmar** con el script, desde los artefactos: `e_aut` del texto (`53/200`) contra el
   etiquetado original; `e_man` (`26/151`) contra el consenso `E1`/`E2`; `e_aut` contra el
   consenso (`28/138`). Si el texto o los artefactos no sostienen la asimetría, el bloque
   JSON lo declara (`asimetria_confirmada: false`), se registra en el memo y en
   `dictamen-correcciones.md`, y `08-discusion.tex` no cambia.
2. **Si se confirma**, recalcular `B` y `a*` con `e_aut` y `e_man` contra **la misma**
   referencia: la principal es el consenso `E1`/`E2` sobre los `138` casos (`e_aut` de
   `predicciones_in_sample.json`, `e_man` de `brazo_manual.csv`, ambos ya usados por
   `analisis_campana.py`). Se agrega un IC por bootstrap **por caso** de `e_aut − e_man`
   (empareja las derivaciones del brazo manual con su caso) y del `B` resultante, para no
   presentar un signo que la muestra no fija. Si los artefactos permiten también la
   referencia original para el brazo manual (derivaciones de `brazo_manual.csv` contra el
   sector original del corpus), se informa como segunda referencia común.
3. **Redacción**: `08-discusion.tex` declara la referencia de cada tasa, reemplaza la lectura
   asimétrica por la de referencia común y mantiene la tabla de supuestos (`10 %` a `26,5 %`)
   como sensibilidad. Las diferencias residuales que no se pueden igualar (unidad por caso
   frente a por derivación; `Δt` medido en la campaña 2026-10 y no en la complementaria) se
   declaran como límite. El signo del balance se enuncia solo si el IC lo fija; si no, se
   declara condicional.

- *Alternativa*: declarar la asimetría sin recalcular. Se usa solo si el recálculo no es
  posible con los artefactos (por ejemplo, si no se pueden emparejar las derivaciones).

### D5. Conclusiones y resumen (rec. 2 y 3)

Ediciones mínimas, sin cifras nuevas fuera del memo:

- `09-conclusiones.tex`, tercera contribución: la frase «sin requerir sortear barreras
  legales ni asumir riesgos de cumplimiento» se reemplaza por una formulación que identifica
  las condiciones normativas desde el diseño y condiciona la operación con datos reales a la
  suscripción del instrumento de transferencia internacional, con remisión a la sección 11
  (`11-aspectos-legales.tex`, transferencia internacional), que hoy declara el instrumento
  no suscrito y que el audio cruza antes de pseudonimizarse.
- `09-conclusiones.tex`, aportes y generalización: se retira «reduce el costo de inferencia»;
  se dice lo medido (la etapa determinística resolvió 131 de 200 casos sin invocar al modelo)
  y que la eficiencia frente a un esquema solo de modelo no se contrastó. El «patrón de diseño
  reproducible para organizaciones medianas de América Latina» se acota a una organización
  argentina, con la transferencia regional como hipótesis a validar; «no depende de GPU ni de
  licencias propietarias» se reemplaza por lo que es cierto en el texto: no requiere GPU
  propia y depende de servicios externos (Gemini API, Twilio) y de N8N. No se agregan hechos
  externos nuevos sin cita (por ejemplo, la licencia de N8N).
- `00-resumen.tex` (resumen y *abstract*, en paralelo): «respaldan la viabilidad técnica y
  económica» pasa a la lectura condicional (técnica sostenida; costo monetario de la
  inferencia marginal; viabilidad económica y operativa condicionada al balance neto). Se
  verifica el límite APA de 250 palabras en ambos.
- **Coherencia del balance**: hoy el resumen dice «indeterminado», la discusión
  «condicional» y las conclusiones «con los supuestos centrales el balance neto es negativo».
  Tras D4 se unifica una sola lectura en los tres lugares, la que sostenga el recálculo.
- **Rec. 3**: un párrafo en las conclusiones (tras el del segundo objetivo) y la fila del
  objetivo 2 de `tab:cumplimiento-objetivos` incorporan la validación fuera de muestra:
  `0,8447` sobre el n efectivo `103`, con el peor caso `0,5800` y el arbitraje pendiente; no
  modifica el estado «No alcanzado» ni acredita el umbral de `0,85`.

### D6. Consentimiento de `E3`/`E4` (rec. 4)

`11-aspectos-legales.tex` agrega, tras el párrafo de los cuatro participantes, que los
etiquetadores `E3` y `E4` de la validación fuera de muestra fueron informados verbalmente el
10 de noviembre de 2026 en los mismos términos y que su confirmación escrita está pendiente a
la fecha de esta versión. El change MUST NOT escribir fechas de confirmación ni afirmar un
consentimiento escrito. Tareas manuales de los autores: adaptar el punto 1 de la plantilla
para `E3`/`E4` (la tarea no fue la campaña complementaria), recabar las firmas y completar
`fecha_confirmacion`; solo después, un ajuste posterior del texto puede decir que firmaron.

### D7. Registro y compilación

Las cifras nuevas van a la sección 3.21 del memo con procedencia (`analisis_dictamen_c207.json`
y clave), comando y estado (`vigente`; lo derivado de supuestos de costo, `condicional`),
más la entrada de upsert, sin tocar valores `vigente` previos. `dictamen-correcciones.md`
recibe una sección del dictamen v1.3.0 con el estado de cada recomendación (1 a 6 atendidas;
7 a 15 diferidas). `CHANGES.md` recibe la FASE 67. `tesis_para_agente.md` se regenera con
`build_tesis_para_agente.py` y se corre `verify_citations.py`. La recompilación de `main.pdf`
y `compilacion.md` queda **bloqueada en esta máquina** y se marca como tarea manual en el
entorno de registro (o en la imagen de `paper/Dockerfile`, si los autores la habilitan); no
se omite en silencio. En la prosa del change se usa «sección N (`archivo.tex`)» (gitleaks).

## Risks / Trade-offs

- [El recálculo del balance cambia el signo y con él frases de conclusiones y resumen] →
  D4 exige IC por caso y D5 unifica una sola lectura; si el IC no fija el signo, se declara
  condicional y no se anuncia un balance positivo.
- [La proporción de acuerdo `E3`/`E4` no reproduce `103/150`] → el script se detiene y lo
  reporta; no se ajusta a mano.
- [El valor puntual del bootstrap no reproduce `0,7116`] → la prueba falla; se revisa la
  fuente de los pares antes de informar el IC.
- [La tabla nueva repite cifras ya presentes (observación N-12)] → el párrafo de c-205 remite
  a la tabla en lugar de duplicar valores, sin perder advertencias.
- [El resumen supera 250 palabras] → la lectura condicional reemplaza texto, no se suma.
- [Los autores no recaban las firmas antes de la defensa] → el texto queda correcto con
  «pendiente»; nada se adelanta a su respaldo.
- [Sin LaTeX aquí, errores de compilación no detectados] → `verify_citations.py` y revisión de
  etiquetas y referencias cruzadas aquí; la compilación queda como tarea manual explícita.

## Migration Plan

Solo documentos y un script nuevo de análisis. Reversión: revertir el diff de la rama. El
change se integra después de c-205 (PR #94), sobre el que está apilado.

## Open Questions

- ¿Los autores ejecutarán c-206 antes de la defensa? Por defecto el texto declara el
  arbitraje diferido (D3); si se ejecuta, un change posterior actualiza la tabla.
- ¿Se informa la segunda referencia común (original) del balance si es computable? Por
  defecto sí, como complemento de la de consenso (D4).
