## Why

El dictamen CONEAU sobre la v10 / release `v1.3.0` (`auditorias/Dictamen_Tesis_v10_v1.3.0_CONEAU_2026-11-13.md`)
aprueba la tesis con observaciones y fija seis recomendaciones **necesarias antes de la
defensa** (1 a 6). Concentran el riesgo de la defensa: conclusiones y resumen que afirman
más de lo que sostienen los resultados (entre ellas, una frase de las conclusiones que
contradice el capítulo legal), una validación fuera de muestra sin tabla ni lugar en las
conclusiones, un consentimiento de `E3`/`E4` que el texto no menciona, un balance neto que
podría comparar errores medidos contra referencias distintas y un intervalo de confianza de
la reducción del tiempo que el cuarto objetivo promete y no se informa. Todo se corrige con
redacción y con cálculos sobre artefactos ya versionados: sin campo nuevo, sin corrida paga
y sin tocar el clasificador.

## What Changes

Verificación previa (hecha al proponer, sobre el árbol de trabajo que ya incluye c-205):
c-205 ya llevó a `07-resultados.tex` (párrafo «Validación fuera de muestra») la macro-F1
`0,7447`, la *balanced accuracy* `0,7395`, las métricas por clase y el kappa del
clasificador `0,7862`, y a `08-discusion.tex` el peor caso `0,5800`, el mejor caso `0,8933`,
la cota `0,8189` y la regla de decisión. Este change NO repite ese trabajo. No existe en
ningún artefacto ni en el texto un intervalo de confianza de la reducción del `71,2 %` ni un
kappa entre `E3` y `E4`.

- **Rec. 1 (resto no cubierto por c-205).** Una tabla de la validación fuera de muestra en
  `07-resultados.tex` (n primario, discordantes, n efectivo, acuerdo y kappa `E3`/`E4`,
  exactitud estricta y laxa con IC, macro-F1, *balanced accuracy*, kappa del clasificador,
  peor caso, mejor caso y cota), y una declaración expresa de que el arbitraje de los `47`
  discordantes (c-206, sin ejecutar) está **pendiente/diferido** y no forma parte de esta
  versión. El kappa `E3`/`E4` se calcula con código versionado y probado; no se inventa.
- **Rec. 2.** `09-conclusiones.tex` y `00-resumen.tex` (y su *abstract*): condicionar la frase
  de «sin requerir sortear barreras legales» a la suscripción del instrumento de transferencia
  internacional; retirar «reduce el costo de inferencia» (hipótesis de eficiencia no
  contrastada); reemplazar «viabilidad técnica y económica» por la lectura condicional;
  acotar la generalización regional y la afirmación sobre dependencia de licencias y
  servicios; unificar la lectura del balance neto entre resumen, discusión y conclusiones.
- **Rec. 3.** Incorporar la validación fuera de muestra a las conclusiones (prosa y fila del
  objetivo 2 en `tab:cumplimiento-objetivos`) con su límite: n efectivo `103`, sesgo de
  exclusión y peor caso `0,5800`; no acredita el umbral de `0,85`.
- **Rec. 4.** `11-aspectos-legales.tex`: mencionar a `E3` y `E4` solo en lo que el registro
  respalda (información verbal del 2026-11-10; confirmación escrita **pendiente**). Completar
  el registro de `docs/campana-medicion/confirmacion-posterior-consentimiento.md` es una
  tarea manual de los autores; el change no carga fechas ni afirma un consentimiento escrito.
- **Rec. 5.** Verificar primero, contra el texto y los artefactos, la sospecha de que el
  balance neto (`08-discusion.tex`, `subsec:balance-neto`) usa la referencia original para el
  error del sistema (`53/200`) y la de consenso para el manual (`0,1722`). Si se confirma,
  recalcular con una referencia común a partir de artefactos versionados (con código probado)
  o declarar la asimetría; si no se confirma, registrarlo y no cambiar nada.
- **Rec. 6.** Calcular el intervalo de confianza de la reducción relativa de la media
  (`71,2 %`) por bootstrap percentil sobre los `200` pares, con la semilla y el número de
  remuestras del paquete, en un script de solo lectura con pruebas (TDD), e informarlo en
  `07-resultados.tex`; el cuarto objetivo conserva su promesa.
- Registro de todas las cifras nuevas en `docs/Tesis/Correcciones/numeros-canonicos.md`
  (sección 3.21), entrada en `dictamen-correcciones.md`, FASE 67 en `CHANGES.md` y
  regeneración de `tesis_para_agente.md`.

## Capabilities

### New Capabilities

- `tesis-dictamen-v1-3-0`: atención de las seis recomendaciones necesarias del dictamen
  CONEAU sobre `v1.3.0` en el texto de la tesis (tabla fuera de muestra, conclusiones y
  resumen acotados, consentimiento de `E3`/`E4`, balance neto con referencia declarada e IC
  de la reducción del tiempo) y su trazabilidad.

### Modified Capabilities

- `evaluation-framework`: se agrega el IC bootstrap de la reducción relativa del tiempo y el
  recálculo del balance neto con una referencia común, ambos de solo lectura y deterministas.
- `evaluation-out-of-sample-validation`: se agrega el acuerdo entre `E3` y `E4` (proporción
  observada y kappa de Cohen con IC) sobre los `150` casos del doble etiquetado independiente.
- `tesis-numeros-canonicos`: nueva sección 3.21 con procedencia y comando de cada cifra
  introducida por este change.

## Impact

- Nuevo: `evaluation/data/campana/analisis/analisis_dictamen_c207.py`, su prueba
  `test_analisis_dictamen_c207.py` y sus salidas `analisis_dictamen_c207.{json,md}`; solo
  importa `evaluation/metrics.py`, `evaluation/kappa.py`, `evaluation/stats.py` y
  `evaluation/corpus.py` (no los edita).
- Prosa: `docs/Tesis/v10 (IA)/paper/sections/{00-resumen,07-resultados,08-discusion,09-conclusiones,11-aspectos-legales}.tex`.
- Registro: `docs/Tesis/Correcciones/{numeros-canonicos,dictamen-correcciones}.md`,
  `CHANGES.md`, `docs/Tesis/v10 (IA)/tesis_para_agente.md`,
  `evaluation/data/campana/analisis/README.md`.
- Sin cambios: `App/`, `n8n/`, `data/*`, el clasificador, los corpus, los scripts de c-191 y
  c-205 y el change c-206.
- Bloqueado en esta máquina (sin `latexmk`/`xelatex`/`biber`): recompilar `main.pdf` y
  actualizar `compilacion.md`; queda como tarea manual en el entorno de registro.
- Manual de los autores: firmar y registrar la confirmación escrita de `E3` y `E4`.
- Gobernanza: HIGH en lo legal (rec. 2, frase legal, y rec. 4) y en el cambio de hechos de
  la tesis (rec. 1, 5 y 6); toda cifra sale de un artefacto versionado o de código probado.
- Non-goals: las recomendaciones 7 a 15 del dictamen (asimetría de la regla de tres vías,
  enunciado frente a veredicto y umbral del 85 %, reformulación de los objetivos 1 y 3,
  limpieza de referencias a versiones y del Anexo I, marco teórico de acuerdo y multietiqueta,
  ubicación del capítulo legal, bibliografía y DOI, glosario y orden de los trabajos
  futuros) quedan para un change posterior; tampoco se ejecuta el arbitraje de c-206.
