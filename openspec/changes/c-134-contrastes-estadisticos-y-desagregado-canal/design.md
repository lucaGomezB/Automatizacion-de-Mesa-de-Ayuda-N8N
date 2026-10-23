## Context

El change cierra la parte de tiempos y contrastes del dictamen CONEAU 2026-10-22 (ver `proposal.md` - Why): seccion 6, observaciones primera (H1 unilateral con p bilateral), segunda (potencia con magnitud no estandarizada), tercera (muestreo "proporcional" no verificable y Bases de Datos `n = 1`) y quinta (cronometraje "no anunciado" frente a cronometraje "en vivo por el companero"); seccion 7 (desagregado por canal sin tabla manual); recomendaciones B7 (parte de tiempos), B12 y B13 (parte de cronometraje). La exactitud por canal de B7 es de c-131 y la salvedad telefonica de las conclusiones (B13) es de c-135.

### Estado verificado (solo lectura, 2026-10-22)

Codigo y reporte:

- `evaluation/stats.py:89` llama a `scipy.stats.wilcoxon(..., alternative="two-sided")`; `ResultadoWilcoxon` (`stats.py:27`) expone `estadistico` (`W = min(T+, T-)`), `t_positivos`, `t_negativos`, `p` (bilateral), `r` y `n`. `reduccion_tiempos` (`stats.py:229`) calcula la cota conservadora descontando 1 s (`stats.py:254`). No hay funciones de descriptivos, `d_z`, efecto minimo detectable ni p unilateral.
- `evaluation/run_evaluation.py:242` (`_seccion_tiempos`) emite Shapiro-Wilk (`:263`), Wilcoxon global, reduccion y "Desglose por canal" (`:319`) con `W`, `T+`, `T-`, `p`, `r` por canal, y la linea del SHA-256. No emite descriptivos (los 61,6/50,0/44,9/10/300 y 17,76/17,47/13,48/0,525/65,834 de `tab:tiempos` no los produce el runner) ni tiempos manuales por canal.
- La "trampa latente" que `CHANGES.md` ("Pendientes planificados", punto 2) atribuye a la seccion "Normalidad (Shapiro-Wilk)" agregada a mano en C-95 **ya no existe**: c-99 la cableo al runner (`run_evaluation.py:263-284`) y `evaluation/report.md:59-65` es salida generada. La nota de `CHANGES.md` esta desactualizada (fuera de alcance de este change; se informa a c-141).
- Regenerar `evaluation/report.md` exige predicciones: `generar_reporte(predicciones, corpus, ...)` (`run_evaluation.py:345`) y el cache `evaluation/predicciones.json` esta en `.gitignore:72`, nunca se versiono y no existe en este arbol de trabajo. La recuperacion del cache es de c-131; sin ella, la corrida completa pide `--confirm-paid` (corrida paga).
- `_compute_corpus_hash` (`run_evaluation.py:496-506`) hashea los bytes crudos. En este checkout de Windows (`core.autocrlf=true`, `git ls-files --eol` = `i/lf w/crlf`) el corpus del arbol de trabajo da `7408cd2a...`, mientras el blob versionado da `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`, la huella canonica (`report.md:99`, `numeros-canonicos.md:17,132`). Regenerar desde Windows cambiaria espuriamente la huella.
- Entorno: el Python local (3.13/3.14) no tiene `scipy`; CI usa Python 3.12 con `App/Backend/requirements.txt` (pytest 9.1.1, pytest-asyncio, pytest-cov) y `evaluation/requirements.txt` (`scipy>=1.13`), y corre `pytest` desde `evaluation/`.
- Tests c-99 que fijan la forma actual: cabeceras `| n | W | T+ | T− | p | r |` y `| Canal | Pares válidos | W | T+ | T− | p | r |`, y la fila exacta `| 5 | 5.0000 | 10.0000 | 5.0000 | 0.625 | 0.3333 |` (`evaluation/tests/test_run_evaluation.py:981-1135`).

Tesis (`docs/Tesis/v10 (IA)/paper/sections/`, todos los archivos con CRLF uniforme; numeracion `grep -n` = editor):

- `01-introduccion.tex:32`: `H_1: M_manual > M_automatizado` y "`p = 3{,}08\text{e-}32`" sin convencion.
- `04-marco-metodologico.tex:16`: "el cronometraje no fue anunciado en tiempo real al operador cuyo tiempo se registraba" y, en el mismo parrafo, "el tiempo lo cronometro en vivo el companero que no estaba registrando el incidente"; `:67` repite la planilla "completada en vivo por el companero de par".
- `04-marco-metodologico.tex:45`: "muestreo estratificado proporcional" con 85/67/31/16/1 sin distribucion del universo; `:51` declara que "los 200 casos son los incidentes efectivamente cronometrados en la campana manual" y conserva una nota historica ("Ese margen sustituye al 6,5 %...").
- `04-marco-metodologico.tex:65`: la metrica de tiempo promete "desvio estandar e intervalo de confianza al 95 %"; ningun intervalo del tiempo medio se reporta en resultados.
- `04-marco-metodologico.tex:71`: "`scipy.stats.wilcoxon` en su variante de dos colas"; `:77` nota historica sobre la definicion previa de `r`; `:91` potencia "bilateral", `d_z ~ 0,20` (0,21 con ARE) comparado con "La reduccion de tiempo observada (71,2 %)".
- `07-resultados.tex:10` y `:23`: desvio automatizado `13,48` (convencion poblacional) junto al manual `44,9` (muestral); `:32-52`: `tab:tiempos-canal` solo con tiempos automatizados; `:54`: `p = 3{,}08 \times 10^{-32}`; `:56-60`: ecuacion desplegada de `r`; `:62`: sensibilidad (68,6 %, 65,6 %, `p = 1{,}8 \times 10^{-26}`, `r = 0{,}8683`).
- `08-discusion.tex:12`: "pasa de 44,9~s ... a 13,48~s"; `:20`: "lo debilita el desagregado por canal, con reducciones positivas en los tres, y se descartaria con un contraste intra-canal apareado" (el contraste ya existe en el reporte) y la explicacion rival del efecto Hawthorne.
- `11-aspectos-legales.tex:32`: repite "el cronometraje no fue anunciado en tiempo real ... pero cuyo conocimiento fue diferido".
- `00-resumen.tex:11` ("con muestreo estratificado") y `:27` ("drawn by proportional stratified sampling").

Requisitos vigentes que condicionan el diseno: `tesis-document` "Rigor inferencial del tamano del efecto" prohibe presentar `W = 0` o `r = 1,00` como resultado del corpus real; "Instrumento unico de medicion manual del tiempo" y "Consistencia de la ventana temporal y reconciliacion anti-Hawthorne" fijan el relato del instrumento; `tesis-numeros-canonicos` exige procedencia por valor y una lista de propagacion ANTES/DESPUES con reversibilidad en el `design.md` de toda rama consumidora (seccion "Objetivos de propagacion" mas abajo).

### Vista previa de valores (solo lectura, no canonica)

Calculada con una replica en Python puro de la aproximacion normal de `scipy.stats.wilcoxon` (`zero_method="wilcox"`, sin correccion de continuidad) sobre el corpus versionado. La replica reproduce exactamente los valores vigentes del reporte (global `W = 363`, `T+ = 19737`, `p = 3,08e-32`, `r = 0,9639`; por canal `p = 5,36e-15`, `4,78e-09`, `2,39e-10`) y los de sensibilidad de la tesis (`-10 s`: `p = 1,8e-26`, `r = 0,8683`). Los valores canonicos seran los del reporte regenerado en apply; si difieren de esta vista, se detiene y se investiga.

| Ambito | n | Manual media / mediana / desvio / min / max (s) | Automatizado media / mediana / desvio / min / max (s) | Reduccion media / mediana | No mas rapidos | W / T+ / T- | p bilateral | p unilateral | r | d_z | MDE (ARE 1 / 0,864) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Global | 200 | 61,585 / 50 / 44,896 / 10 / 300 | 17,761 / 17,471 / 13,516 / 0,525 / 65,834 | 71,16 % / 65,06 % | 12 | 363 / 19737 / 363 | 3,08e-32 | 1,54e-32 | 0,9639 | 1,0004 | 0,1981 / 0,2131 |
| Llamada telefonica | 81 | 87,247 / 72 / 48,899 / 30 / 220 | 20,088 / 18,698 / 6,025 / 14,027 / 59,150 | 76,98 % / 74,03 % | 0 | 0 / 3321 / 0 | 5,36e-15 | 2,68e-15 | 1,0000 | 1,3674 | 0,3113 / 0,3349 |
| Correo electronico | 66 | 56,515 / 50 / 35,809 / 20 / 300 | 27,655 / 25,818 / 14,200 / 8,970 / 65,834 | 51,07 % / 48,36 % | 12 | 189 / 2022 / 189 | 4,78e-09 | 2,39e-09 | 0,8290 | 0,7345 | 0,3449 / 0,3710 |
| Formulario web | 53 | 28,679 / 20 / 16,442 / 10 / 100 | 1,882 / 1,265 / 1,266 / 0,525 / 4,162 | 93,44 % / 93,67 % | 0 | 0 / 1431 / 0 | 2,39e-10 | 1,19e-10 | 1,0000 | 1,6147 | 0,3848 / 0,4140 |

Diferencias pareadas globales: media `43,824 s`, desvio muestral `43,807 s`. Sensibilidad (descuento al manual): 1 s -> 60,59 s, 70,68 %, `p = 7,25e-32` (unilateral `3,62e-32`), `r = 0,9580`; 5 s -> 56,59 s, 68,61 %, `p = 4,87e-30` (`2,44e-30`), `r = 0,9286`; 10 s -> 51,59 s, 65,57 %, `p = 1,80e-26` (`8,98e-27`), `r = 0,8683`. Granularidad de `tiempo_manual_s`: 199/200 multiplos de 5 s y 180/200 multiplos de 10 s (el unico no multiplo de 5 es 72 s). Los 12 pares no mas rapidos pertenecen todos a correo electronico. El desvio automatizado `13,48` de la tesis es el poblacional (`13,516 x raiz(199/200) = 13,483`); el manual `44,9` es el muestral (el poblacional seria 44,8).

### Gobernanza

MEDIUM: codigo de evaluacion y numeros canonicos con checkpoints. Las redacciones de muestreo (D8) y cronometraje (D9) describen hechos del estudio que solo el autor conoce: se aplican con el texto por defecto unicamente tras la respuesta a OQ1/OQ2.

## Goals / Non-Goals

**Goals:**

- Hacer reproducible desde el runner todo el bloque de tiempos que la tesis cita (descriptivos, por canal, sensibilidad), mas el p unilateral, `d_z` y el efecto minimo detectable, sin predicciones ni gasto.
- Cerrar B7 (tiempos), B12 y B13 (cronometraje) en la tesis con cifras trazables al reporte y al memo canonico.
- Mantener intactos los valores vigentes (W, T+, T-, p bilateral, r, medias, medianas, sensibilidad) y la forma de las tablas existentes del reporte.
- Acotar el impacto neto de paginas y dejarlo medido para c-141.

**Non-Goals:**

- Exactitud de clasificacion por canal, exactitud laxa, metricas por etapa y recuperacion del cache de predicciones (c-131).
- Salvedad de cota inferior del canal telefonico en `09-conclusiones.tex:39` y cronologia de la campana (c-135); parrafo introductorio de resultados (c-135).
- Recomendacion de asignacion no proporcional en `10-recomendaciones.tex` (c-136 decide si la recoge; ver D8).
- Referencias metodologicas primarias de Wilcoxon, potencia y bootstrap (B15, change bibliografico de la familia, previsiblemente c-139): este change no agrega entradas `.bib` ni citas nuevas.
- Cambiar el diseno experimental, re-medir o re-clasificar; editar `CHANGES.md`; crear tags; agregar `.gitattributes`.

## Decisions

### D1 - Convencion del valor p: bilateral declarado, unilateral informado

Se conservan los p bilaterales como valores reportados (3,08e-32 global; sensibilidad; por canal) y se declara explicitamente que son conservadores frente a la alternativa direccional `H_1: M_manual > M_automatizado`. El runner calcula ademas el p unilateral con una segunda llamada `wilcoxon(diferencias, alternative="greater")` (no por division del bilateral) y la tesis lo cita una vez en `04-marco-metodologico.tex` (analisis estadistico) y en `01-introduccion.tex:32` (1,54e-32 global). `ResultadoWilcoxon` agrega el campo `p_unilateral`; `estadistico`, `p` y `r` no cambian.

Razon: la convencion declarada `W = min(T+, T-)` (`04:71`, `report.md:69`, escenario de convencion de `W` del requisito de analisis estadistico de tiempos de `evaluation-framework`) es la del contraste de dos colas de `scipy`; para `alternative="greater"` `scipy` devuelve `T+` como estadistico. Pasar al unilateral como valor principal obligaria a reportar `T+ = 19.737` como estadistico, contradiria la convencion y el requisito vigente que fija `W=363 ... p=3,08e-32`, y moveria cifras canonicas en 01, 07, memo y specs. El bilateral no altera ninguna decision (es mayor que el unilateral cuando el efecto va en la direccion de H1).

**Alternativas:** (B) reportar el unilateral como principal: descartada por lo anterior. (C) solo declarar la convencion sin cifra unilateral: aceptable para el dictamen, pero citar la cifra cierra la observacion de forma verificable a costo nulo. **Reversible si** el autor prefiere B (cambio acotado a 01:32, 07:54 y memo 3.1).

### D2 - Tamano del efecto estandarizado y potencia homogenea

`d_z = media(d) / desvio(d)` con `d = manual - automatizado` y desvio muestral (divisor `n - 1`), global y por canal; no aplicable con `n < 2` o desvio nulo. Efecto minimo detectable en escala `d_z` por aproximacion normal: `MDE = (z_{1-alfa/2} + z_{potencia}) / raiz(n * ARE)` (variante unilateral con `z_{1-alfa}`), implementado con `statistics.NormalDist` (sin dependencias nuevas). Se reportan `ARE = 1` y `ARE = 0,864` (cota inferior de Hodges-Lehmann, 108/125, de la eficiencia de la prueba de rangos frente a la `t` pareada), que reproduce exactamente las cifras vigentes de la tesis (0,1981 ~ 0,20 y 0,2131 ~ 0,21). La potencia se mantiene bilateral (`alfa = 0,05`), coherente con D1. La tesis compara `d_z` observado 1,00 con el minimo 0,20/0,21 (mas de cuatro veces) y, por canal, `d_z` 1,37/0,73/1,61 con 0,31/0,34/0,38 (0,33/0,37/0,41 con ARE).

**Alternativas:** potencia por `t` no central o simulacion (tipo G*Power: 0,1990 frente a 0,1981): diferencia despreciable, mas complejidad; `ARE = 3/pi` (padre normal, 0,2027): no reproduce el 0,21 publicado y no es la cota conservadora; `d_av` o `d_rm` en lugar de `d_z`: no corresponden al contraste pareado ni a la formula del MDE. **No reversible** (correccion de exactitud: se reemplaza una comparacion heterogenea).

### D3 - Convencion unica del desvio y estadisticos declarados

Desvio muestral (`statistics.stdev`, divisor `n - 1`) en runner y tesis. El desvio automatizado pasa de `13,48` (poblacional) a `13,52` en `07:10`, `07:23` y `08:12`; el manual `44,9` no cambia (ya muestral); la frase "aproximadamente la tercera parte" sigue siendo cierta (0,30). En `04:65` se retira la promesa de "intervalo de confianza al 95 %" del tiempo medio, que resultados no informa, y se alinea la lista con lo reportado.

**Alternativas:** divisor `n` en ambos (44,8 y 13,48): descartada, `d_z` y `pandas`/`statistics` usan `n - 1`; reportar el IC del tiempo medio (t o bootstrap) en `tab:tiempos`: agrega una fila y tres cifras canonicas con costo de paginas, sin pedido del dictamen. **Reversible si** el autor prefiere reportar el IC (OQ3, no bloqueante) o la convencion poblacional en todo el documento.

### D4 - Seccion "Tiempos" estrictamente aditiva

Tres subsecciones nuevas, insertadas despues de "### Desglose por canal" y antes de la linea del SHA-256: "### Descriptivos global y por canal" (n, manual y automatizado con media, mediana, desvio, minimo y maximo, reduccion relativa de media y mediana, pares no mas rapidos), "### Contraste direccional y tamano del efecto estandarizado" (n, p bilateral, p unilateral, `d_z`, MDE con ARE 1 y 0,864, con los supuestos declarados en el reporte) y "### Escenarios de sensibilidad del redondeo manual" (descuentos de 5 s y 10 s con media ajustada, reduccion relativa, p bilateral, p unilateral, `r`, mas la granularidad 5 s/10 s). Precision fija (`.4f`, porcentajes `.2f`, p con 3 cifras significativas) y el orden canonico de canales de c-99 (conteo descendente, desempate alfabetico) para preservar el determinismo byte a byte. Las tablas existentes no se tocan.

**Alternativa:** ensanchar las tablas existentes con columnas nuevas: descartada, rompe los asserts de c-99 y su decision de aditividad (c-99 D7).

### D5 - Regeneracion sin predicciones: `--solo-tiempos` con reemplazo del bloque

Funcion pura `reemplazar_seccion_tiempos(reporte: str, seccion: str) -> str`: el bloque va desde la linea `## Tiempos` hasta antes del siguiente encabezado que empiece con `## ` o de la linea `---` del pie; si falta, se inserta antes del pie. `main_solo_tiempos(corpus_path, report_path)` carga el corpus, calcula la huella (D6) y `_seccion_tiempos`, y reescribe el reporte; si el reporte no existe, error claro (no crea un reporte parcial). En el CLI, `--solo-tiempos` es incompatible con `--force`/`--no-cache`/`--confirm-paid` (validacion con `parser.error`, codigo 2, porque esos dos flags si pueden combinarse entre si) y se despacha antes de cualquier logica de cache o de gate pago; nunca construye ni invoca el clasificador ni lee/escribe `predicciones.json`. `evaluation/README.md` lo documenta.

**Alternativas:** esperar el cache de c-131 o confirmar una corrida paga: bloquea c-134 y gasta sin necesidad (el bloque de tiempos solo depende del corpus); artefacto separado `report_tiempos.md`: dos fuentes y `report.md` desactualizado; `generar_reporte(predicciones=None)` que omita la clasificacion: borraria las secciones de clasificacion del reporte versionado.

### D6 - Huella del corpus independiente del fin de linea

`_compute_corpus_hash` pasa a `sha256(bytes.replace(b"\r\n", b"\n"))`. En Linux/CI (LF) la huella no cambia; en Windows con `autocrlf` pasa a la canonica `1fd17d7e...`. Una diferencia real de contenido sigue cambiando la huella. Efecto lateral positivo para c-131: un cache con la huella canonica se valida tambien en Windows.

**Alternativas:** `.gitattributes` (`data/corpus_evaluacion_pseudonimizado.json -text`): complementaria, requiere re-checkout y no cubre copias fuera de git; se deja como seguimiento opcional (c-140/c-141). Regenerar solo en Linux o con `git show HEAD:...` a un temporal: fragil y no protege a c-131.

### D7 - Tabla `tab:tiempos-canal` ampliada y discusion verificable

Una sola tabla (3 canales + Global): Canal | Casos | Manual media / mediana (s) | Automatizado media / mediana (s) | Reduccion de la media | Pares no mas rapidos | p (bilateral) | `d_z`. Precision: manual 1 decimal (como 61,6), automatizado 2 decimales (como 17,76), reduccion 1 decimal, p 3 cifras significativas, `d_z` 2 decimales. Nota al pie: cota inferior telefonica, convencion de p (D1) y remision a `evaluation/report.md` para `W`, `T+`, `T-` y `r` por canal. `07:32` se reescribe para presentar ambos brazos y el contraste intra-canal; `08:20` remite a la tabla y conserva "lo debilita" (la magnitud global depende de la composicion por canal, aunque el efecto existe en los tres). La exactitud por canal NO va en esta tabla (c-131, tabla propia en la subseccion de clasificacion).

Por que sin columnas `W` y `r`: telefonia y formulario web tienen `W = 0` y `r = 1` (ningun par desfavorable), lo que choca con la letra del requisito "Rigor inferencial del tamano del efecto" (prohibe presentar `W = 0` o `r = 1,00` como resultado del corpus real), escrito para impedir la antigua afirmacion global falsa. El p del contraste, `d_z` y los pares no mas rapidos (0/12/0) transmiten la misma informacion con dos columnas menos, y los estadisticos de rango quedan en el reporte.

**Alternativas:** incluir `W` y `r` modificando ese requisito (MODIFIED): mas churn de specs y dos columnas mas; dos tablas (descriptivos y contraste): mas paginas.

### D8 - Muestreo y asignacion (B12)

Por defecto (OQ2 sin distribucion del universo): `04:45` pasa a "muestreo estratificado, con asignacion proporcional a la distribucion por sector observada en el periodo relevado", declara que la distribucion del universo por sector no esta disponible en las fuentes del estudio y que, por eso, la proporcionalidad no es verificable frente al universo; agrega que la asignacion dejo a Bases de Datos con un unico caso, no estimable para la inferencia por clase, y que en replicaciones conviene una asignacion no proporcional con sobremuestreo de las clases minoritarias (frase autocontenida, sin remision a recomendaciones). El abstract (`00-resumen.tex:27`) deja "proportional stratified sampling" por una forma equivalente a la del capitulo 4; el resumen (`:11`, "con muestreo estratificado") no cambia. Si el autor aporta la distribucion del universo, se reporta en una frase junto a la muestral y se registra en el memo. Si el autor aclara que no hubo estratificacion (los 200 son los incidentes cronometrados, `04:51`), la descripcion pasa a "muestra no probabilistica por disponibilidad". Handoff a c-136: puede recoger la asignacion no proporcional en `subsec:estudios-replicacion`.

**Alternativa:** retirar toda referencia a la estratificacion sin consultar: descartada, puede borrar un hecho verdadero del diseno. **Reversible si** el autor aporta el universo o aclara el procedimiento de seleccion (OQ2).

### D9 - Cronometraje y efecto Hawthorne (B13)

Por defecto (OQ1, opcion a): los dos operadores trabajaron en pares y se cronometraron mutuamente, de modo que sabian que la campana registraba tiempos; lo que no se anuncio fue el inicio de cada cronometraje individual y el proposito comparativo del estudio (el contraste con un flujo automatizado), informados en el debriefing. La medicion no fue encubierta: el efecto Hawthorne queda atenuado, no eliminado, y se trata como amenaza residual. Se declara la granularidad verificable de la planilla (multiplos de 5 s en 199/200 y de 10 s en 180/200), que vincula los escenarios de sensibilidad de 5 s y 10 s con la resolucion efectiva del instrumento. Propagacion: `04:16` (relato principal), `08:20` (explicacion rival "Tercero"), `11-aspectos-legales.tex:32` (debriefing, conservando `\parencite{APA2017}`); `04:67` solo cambia si OQ1 no es la opcion a.

**Alternativa:** mantener "no anunciado" y "en vivo por el companero" con una aclaracion minima: no resuelve la contradiccion que el dictamen senala. **Reversible si** el autor describe otro procedimiento (OQ1); el texto se ajusta a su relato.

### D10 - Presupuesto de paginas

Impacto bruto estimado: `07` +7 a +9 lineas (tabla con cabecera de dos niveles y parrafo), `04` +10 a +14 lineas (convencion, potencia, muestreo, cronometraje), `01`/`08`/`11`/`00` +2 a +3 lineas: +0,4 a +0,6 pagina. Compensacion dentro de los mismos pasajes: retirar la nota historica de `04:51` ("Ese margen sustituye al 6,5 %..."), la de `04:77` ("La definicion anterior... queda reemplazada"), compactar la ecuacion desplegada de `r` en `07:56-59` a una linea (la formula ya esta definida en `04:73-77`) y acortar `04:65` (D3): -5 a -8 lineas. Neto esperado <= +0,4 pagina. Reserva si la compilacion supera 101 paginas (sin tocar las columnas exigidas por el spec): reducir el parrafo de `07:32` a una frase que remita a la tabla, acortar los textos por defecto de D8 y D9, y escalar a c-141 la compensacion que reste. La verificacion final integrada es de c-141; nota para c-141: el requisito vigente "Presupuesto de paginas preservado" de `tesis-document` fija <= 100, mientras c-120/c-121 operaron con <= 101 y el PDF actual tiene 101.

### D11 - Numeros canonicos

`docs/Tesis/Correcciones/numeros-canonicos.md` recibe una seccion nueva "3.7 Tiempos por canal, contrastes y sensibilidad (c-134)" con cada valor citado nuevo o hasta hoy no registrado del bloque de tiempos (descriptivos globales y por canal, reduccion relativa, pares no mas rapidos, p unilateral, `d_z`, MDE y supuestos, sensibilidad de 5 s y 10 s, granularidad), procedencia `evaluation/report.md:<linea>` del reporte regenerado mas la funcion de `evaluation/stats.py` que lo calcula, y estado. `13,48` queda `retirado` (convencion poblacional) con `13,52` `vigente`; las filas de 3.1 que citan `p = 3,08e-32` y `W = 363` agregan la nota de convencion (D1). Se agrega la nota de upsert al pie, como hizo c-108.

### D12 - Propiedad de secciones y orden de aplicacion en la familia

| Artefacto | c-134 (este change) | Otros |
|---|---|---|
| `evaluation/report.md` | Bloque "## Tiempos" completo (y su linea SHA-256) | c-131: secciones de clasificacion (exactitud laxa, por etapa, por canal), siempre ANTES de "## Tiempos"; nadie inserta contenido dentro del bloque de tiempos |
| `evaluation/stats.py` | Funciones de tiempos | c-131: `evaluation/metrics.py` |
| `evaluation/run_evaluation.py` | `_seccion_tiempos`, `reemplazar_seccion_tiempos`, `main_solo_tiempos`, flag `--solo-tiempos`, `_compute_corpus_hash` | c-131: `generar_reporte` (bloques de clasificacion), cache y su recuperacion |
| `evaluation/tests/test_run_evaluation.py` | Bloque de tests "c-134" al final | c-131: su propio bloque |
| `07-resultados.tex` | `subsec:comparacion-tiempos` (`:8-69`) | c-131: `subsec:matriz-metricas` y exactitud por canal; c-130: intervencion y calibracion; c-135: parrafo introductorio `:6` |
| `04-marco-metodologico.tex` | `:16`, `:45` (clausula de muestreo), `:51` (nota historica), `:65` (clausula de tiempo), `:67` (si OQ1 lo exige), `:71`, `:77`, `:91` | Previsto: c-135 fechas de `:14`/`:45` y Scrumban; c-130/c-133 resto de `:65` (metricas de clasificacion e intervencion) |
| `01-introduccion.tex` | Clausula del p en `:32` | Previsto: c-133 sub-hipotesis 2, 3 y subsidiarias (`:34-38`) |
| `08-discusion.tex` | `:12` (desvio) y explicaciones rivales "Segundo" y "Tercero" de `:20` | Previsto: c-132 implicancias y balance; c-130 gate; c-135 cuarta limitacion |
| `00-resumen.tex` | Clausula de muestreo de `:27` (y `:11` si OQ2 lo exige) | Previsto: c-132/c-133 viabilidad, metrica primaria e hipotesis |
| `numeros-canonicos.md` | Seccion 3.7 y notas en 3.1 | c-131: sus propias secciones |

Orden sugerido: el bloque de codigo de c-134 (tareas 1 a 5) no depende de nadie y conviene aplicarlo antes de cualquier regeneracion completa del reporte que c-131 haga desde Windows (D6). Las ediciones de tesis van despues de c-133 (01) y c-132 (resumen), y antes de c-135 (consistencia redaccional), c-137 (ortotipografia sobre el texto nuevo) y c-141 (paginas y release). Si c-131 regenera el reporte despues de c-134, el test de idempotencia garantiza que el bloque de tiempos se reproduce byte a byte.

## Objetivos de propagacion (ANTES -> DESPUES)

Fragmentos ANTES en ASCII como ancla de `grep` (el `.tex` real lleva tildes); el DESPUES es el contenido a redactar con la acentuacion correcta del espanol. Las cifras DESPUES se toman del reporte regenerado y del memo, no de esta tabla.

| # | Archivo:linea | ANTES (ancla) | DESPUES | Decision | Reversibilidad |
|---|---|---|---|---|---|
| P1 | `07-resultados.tex:10` | `13,48~s` | `13,52~s` | D3 | Si el autor adopta divisor `n` en todo el documento |
| P2 | `07-resultados.tex:23` | `& 13,48   &` | `& 13,52 &` | D3 | Idem |
| P3 | `08-discusion.tex:12` | `a 13,48~s en el automatizado` | `a 13,52~s en el automatizado` | D3 | Idem |
| P4 | `04-marco-metodologico.tex:65` | `e intervalo de confianza al 95~\%` | Lista alineada a lo reportado (media, mediana, desvio, minimo, maximo y reduccion relativa) | D3 | Si OQ3 pide el IC del tiempo medio |
| P5 | `01-introduccion.tex:32` | `\(p = 3{,}08\text{e-}32\)` | El mismo p rotulado bilateral y conservador frente a `H_1` direccional, con el p unilateral `1,54e-32` | D1 | Si el autor prefiere el unilateral como principal |
| P6 | `04-marco-metodologico.tex:71` | `en su variante de dos colas)` | Frase nueva: los p de tiempos se informan bilaterales, conservadores frente a H1; el unilateral (`alternative = greater`) vale `1,54e-32` en el contraste global | D1 | Idem P5 |
| P7 | `07-resultados.tex:54` | `junto con un valor \(p = 3{,}08 \times 10^{-32}\)` | El mismo valor con el rotulo "bilateral" y remision a `subsec:analisis-estadistico` | D1 | Idem P5 |
| P8 | `04-marco-metodologico.tex:91` | `(71,2~\%) supera holgadamente ese m` | `d_z` observado 1,00 (media 43,82 s sobre desvio 43,81 s) frente al minimo 0,20 (0,21 con ARE) y, por canal, `d_z` 0,73-1,61 frente a minimos 0,31-0,38 (0,33-0,41 con ARE); ARE 0,864 declarada en el parentesis del ajuste | D2 | No reversible |
| P9 | `07-resultados.tex:56-60` | Ecuacion desplegada de `r` | `r` en linea (`19.374/20.100 = 0,9639`) mas la frase de `d_z = 1,00` | D2/D10 | Reversible (forma) |
| P10 | `04-marco-metodologico.tex:45` | `por muestreo estratificado proporcional un corpus` | Texto por defecto de D8 (asignacion proporcional a lo observado en el periodo, no verificable frente al universo; Bases de Datos `n = 1`; asignacion no proporcional para replicaciones) | D8 | Si OQ2 aporta el universo o aclara la seleccion |
| P11 | `00-resumen.tex:27` | `drawn by proportional stratified sampling` | Forma equivalente a P10 en ingles | D8 | Idem P10 |
| P12 | `04-marco-metodologico.tex:16` | `no fue anunciado en tiempo real al operador` / `lo cronometr` (ancla `en vivo el compa`) | Texto por defecto de D9 (cronometraje mutuo conocido; no anunciados el inicio de cada medicion ni el proposito; Hawthorne atenuado y residual; granularidad 5 s/10 s) | D9 | Si OQ1 describe otro procedimiento |
| P13 | `08-discusion.tex:20` | `lo debilita el desagregado por canal, con reducciones positivas en los tres, y se descartar` | Remision a `tab:tiempos-canal` y al contraste intra-canal ya realizado (reduccion de 51,1 % en correo, donde se concentran los 12 pares no mas rapidos, a 93,4 % en web); "lo debilita" se conserva | D7 | Reversible (forma) |
| P14 | `08-discusion.tex:20` | `Tercero, la novedad o efecto Hawthorne` | Agrega que el procedimiento lo atenua sin eliminarlo, con remision a `subsec:diseno-experimental` | D9 | Idem P12 |
| P15 | `11-aspectos-legales.tex:32` | `el cronometraje no fue anunciado en tiempo real al operador cuyo tiempo se registraba` | Mismo relato que P12; "conocimiento diferido" pasa a "informacion diferida sobre el proposito del estudio"; se conserva `\parencite{APA2017}` | D9 | Idem P12 |
| P16 | `07-resultados.tex:32-52` | `El tiempo automatizado de registro desagregado por canal` y la tabla de 4 columnas | Parrafo con ambos brazos y contraste intra-canal; tabla de D7 | D7 | Reversible (forma) |
| P17 | `04-marco-metodologico.tex:51` | `Ese margen sustituye al 6,5~\%` | Se retira la oracion (nota historica) | D10 | Reversible |
| P18 | `04-marco-metodologico.tex:77` | `queda reemplazada por esta formulaci` | Se retira la oracion (nota historica) | D10 | Reversible |

## Risks / Trade-offs

- [Respuesta del autor contradice el texto por defecto de D8/D9] -> Las tareas de esas redacciones quedan bloqueadas hasta OQ1/OQ2; el resto del change avanza; el texto por defecto afirma solo lo que se deduce de la propia tesis.
- [La huella normalizada (D6) cambia la validacion del cache de c-131] -> Solo para copias CRLF, que pasan a la huella canonica; test explicito de que un cambio de contenido sigue invalidando el cache; coordinacion declarada en D12.
- [El reemplazo de bloque (D5) borra contenido ajeno] -> Funcion pura con tests de preservacion de secciones previas y posteriores e idempotencia frente a la corrida completa; contrato de D12 (nadie inserta dentro de "## Tiempos").
- [La vista previa difiere de `scipy`] -> La replica reproduce exactamente los valores vigentes; el p unilateral se calcula con `scipy` y se contrasta contra la vista; si difiere, se detiene.
- [`scipy` usa metodo exacto en `n` chicos y aproximado en `n > 50`] -> Tests chicos con valores exactos (0,3125; 0,78125) y comparacion de la corrida real con la vista previa.
- [Aumento de paginas por encima de 101] -> Compensaciones de D10 y reserva; medicion registrada; verificacion final en c-141.
- [Tabla ancha con desborde] -> `\footnotesize`, cabecera de dos niveles, `\tabcolsep` reducido; verificar `Overfull \hbox` en el `.log`.
- [Choque de lineas con c-131/c-133/c-135 sobre los mismos archivos] -> Propiedad por pasaje (D12) y anclas de `grep` en tareas; re-ubicar por ancla, no por numero de linea, si otro change se aplico antes.
- [`d_z = 1,00` confundido con el rank-biserial prohibido `r = 1,00`] -> `d_z` siempre rotulado; el requisito de tesis lo exige.
- [Entorno sin `scipy`] -> Python 3.12 con los requirements de CI (venv o contenedor `python:3.12-slim`).

## Migration Plan

1. Preparar el entorno (Python 3.12 con `App/Backend/requirements.txt` y `evaluation/requirements.txt`) y correr la linea base de `pytest` en `evaluation/` (red de seguridad).
2. TDD de `stats.py` (descriptivos, reduccion relativa, p unilateral, `d_z`, MDE, sensibilidad, granularidad).
3. TDD de la seccion "Tiempos" del runner (subsecciones aditivas; asserts de c-99 intactos).
4. TDD de la huella normalizada, de `reemplazar_seccion_tiempos`, de `main_solo_tiempos` y del flag `--solo-tiempos`; actualizar `evaluation/README.md`.
5. Regenerar `evaluation/report.md` con `--solo-tiempos`; verificar que solo cambia el bloque de tiempos, que las filas previas no cambian, que la huella es la canonica y que los valores nuevos coinciden con la vista previa.
6. Upsert de `numeros-canonicos.md` (D11) con lineas del reporte regenerado.
7. Ediciones de tesis D1, D2, D3, D7 y D10 (no dependen de OQ); D8 y D9 tras OQ2/OQ1.
8. Compilar (XeLaTeX con `latexmk`, o el contenedor `texlive-thesis` de changes previos), medir paginas, aplicar compensaciones si hace falta, regenerar `tesis_para_agente.md` con `build_tesis_para_agente.py`.
9. Rollback: `git checkout <commit-previo> -- evaluation/ "docs/Tesis/v10 (IA)/" docs/Tesis/Correcciones/numeros-canonicos.md` y recompilar; el reporte previo vuelve con el mismo checkout, sin predicciones.

## Open Questions

- **OQ1 (bloquea solo P12, P14 y P15): como fue exactamente el cronometraje manual.** (a) Los dos operadores se cronometraban mutuamente y sabian que la campana registraba tiempos; no se anunciaba el inicio de cada medicion ni el proposito comparativo (texto por defecto). (b) Cronometraba una tercera persona (por ejemplo, un autor) y el operador no sabia que su tiempo se registraba. (c) Otro procedimiento: describirlo. Tambien: la planilla registraba con resolucion de 5 s/10 s por diseno o los valores se redondeaban a ojo.
- **OQ2 (bloquea solo P10 y P11): distribucion del universo y seleccion de los 200 casos.** Existe en el sistema de tickets de la organizacion el conteo por sector del periodo relevado (universo ~2.646)? Si existe, se reporta (con su fuente). Ademas: los 200 casos se eligieron con cuotas por sector o son todos los incidentes cronometrados en la campana (`04:51`)? Sin respuesta, se aplica el texto por defecto de D8.
- **OQ3 (no bloqueante): intervalo de confianza del tiempo medio.** Por defecto se retira la promesa de `04:65` (D3); si el autor prefiere reportarlo, se agrega al runner y a `tab:tiempos` (una fila mas).
