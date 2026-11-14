## Why

El dictamen CONEAU posterior a `v1.3.0` (evaluó el commit `5734ea8`, 13-11-2026; rama
`docs/dictamen-coneau-post-v1.3.0`, PR 107, todavía fuera de `main`) aprueba con observaciones
(`8,29` sobre 105) y concentra el riesgo en un defecto de integración: el capítulo de resultados
informa el resultado arbitrado fuera de muestra (`0,6893`, `142` de `206`), pero el resumen, la
discusión, las conclusiones y las recomendaciones siguen razonando con `0,8447` sobre `103` y con
el arbitraje como pendiente. A eso se suman lecturas que faltan (ponderada, sin exclusión, por
origen de la referencia y calibración sobre el corpus arbitrado), un diseño fuera de muestra sin
apartado metodológico, una versión entregada que no contiene la evidencia que el texto informa y
defectos de forma. Todo se corrige con redacción y con cálculos sobre datos ya versionados.

Se verificó cada hallazgo contra `ebd2baa` (posterior a c-216 y c-217): siguen vigentes, salvo los
que se indican en la sección «Hallazgos que cambiaron al verificar contra `ebd2baa`».

## What Changes

| Bloque | Recomendaciones del dictamen | Qué cambia | Gobernanza |
|---|---|---|---|
| **A. Análisis** | 2, 3, 8, 12 | Script nuevo de solo lectura `analisis_propagacion_arbitraje_c218.py` (TDD) con las tres lecturas de la exactitud fuera de muestra, la matriz y las métricas por clase del corpus arbitrado, el desglose por origen de la referencia y por etapa, la calibración descriptiva de la etapa Gemini sobre los `91` casos, la sensibilidad del balance neto y los controles de reproducibilidad. Sección 3.29 aditiva del memo canónico. | MEDIUM |
| **B. Propagación del arbitraje** | 1, 5, 11, 15 | Reescritura de `08-discusion.tex:8`, `:20`, `:28`, `:60`; `09-conclusiones.tex:24`, `:37`, `:47`; `10-recomendaciones.tex:18`, `:26`, con el resultado arbitrado (`25` de `47` discordantes acertados), la clase `Sistemas` con `61` casos y una sola aparición del bloque de cifras sobre `103` fuera de resultados. | MEDIUM |
| **C. Resultados y método** | 2, 3, 6, 9 | Subsecciones propias en `07-resultados.tex` para la validación fuera de muestra y para las comparaciones con esquemas alternativos; tabla nueva de matriz y métricas por clase; fila descriptiva de `91` casos en `tab:calibracion-gate`; apartado metodológico del diseño fuera de muestra y amenazas nuevas en `04-marco-metodologico.tex`. | MEDIUM |
| **D. Resumen y alcance** | 4, 10, 11, 13 | Resumen y *abstract* con la exactitud fuera de muestra y la línea de base (límite de 250 palabras); alcance del capítulo 1 precisado; afirmación de latencia y costo de `05-arquitectura.tex:68` conciliada con lo medido por c-217; identificadores internos retirados del cuerpo. | MEDIUM |
| **E. Balance neto y reproducibilidad** | 8, 12 | Párrafo de sensibilidad del balance neto con la tasa fuera de muestra (rotulado como sensibilidad); declaración de la variación de la confianza de Gemini entre corridas (`7` de `34`), del `commit` inexistente registrado por la primera corrida y del orden del prerregistro de c-214 por fechas de autor. | MEDIUM |
| **F. Marco, estado del arte, glosario y bibliografía** | 14, 16 | TF-IDF, regresión logística, Brier y AUROC en el marco teórico y en el glosario; atribución a Mosqueira-Rey verificada o atenuada; salvedad de Colavito; cinco claves con año inconsistente; dirección de ServiceNow; mención de la Resolución AAIP 198/2023 solo si se verifica en fuente oficial. | MEDIUM; capítulo legal HIGH |
| **G. Identificación del documento** | 7, 17 | Anexo J retirado o trasladado (decisión de los autores); cronograma actualizado; portada, Anexo B y entrada bibliográfica del repositorio alineados con un tag nuevo; `paper/compilacion.md` regenerado. | Tag y push: HIGH, con confirmación expresa |

**No objetivos.**

- No se reabren mediciones de campo, no se reclasifica ni se reentrena, no se invoca a Gemini y
  no hay corridas pagas: todo sale de `predicciones_arbitrado.json`,
  `predicciones_independiente.json`, `corpus_independiente_arbitrado.json`,
  `arbitraje_tres_vias.json` y `doble_etiquetado_arbitrado.csv`.
- No se cambia ningún valor vigente del memo canónico: `0,6893/206`, `0,8447/103`, `0,7024` y los
  de calibración de c-214 se conservan; lo nuevo es aditivo.
- No se re-elige el umbral del gate con datos fuera de muestra (la regla prerregistrada de c-214
  elige solo con los `200` casos de ajuste).
- No se evalúa ni se reescribe la subsección `subsec:ruido-referencia` de c-216, que el dictamen
  no evaluó; solo se ajustan sus referencias cruzadas si cambia la estructura.
- No se deshace el contraste de eficiencia de c-217: donde el dictamen dice que la hipótesis de
  eficiencia no se contrastó, el texto vigente ya lo contrasta y se conserva.
- No se inventan la procedencia ni el período de los `150` casos: son datos que solo pueden
  aportar los autores.
- No se crea ni se publica ningún tag sin confirmación expresa de los autores.

## Capabilities

### New Capabilities

Ninguna. Los requisitos se agregan o modifican sobre capacidades existentes.

### Modified Capabilities

- `evaluation-out-of-sample-validation`: el requisito OOS-018 pasa a describir el corpus
  arbitrado real (`150` originales más `56` de refuerzo, `206` casos); se agregan las tres
  lecturas de la exactitud con su rótulo, el desglose por origen de la referencia y por etapa, la
  sensibilidad del balance neto y los controles de reproducibilidad.
- `confidence-gate-calibration`: se agrega el complemento descriptivo de la calibración sobre los
  `91` casos de la etapa Gemini del corpus arbitrado, sin re-elegir umbral.
- `tesis-numeros-canonicos`: sección 3.29 aditiva con cada cifra nueva, su fuente y su comando.
- `tesis-document`: propagación del arbitraje, estructura de resultados, apartado metodológico,
  resumen, alcance, identificadores internos, marco teórico, glosario, bibliografía, cronograma e
  identificación de la versión entregada.
- `tesis-dictamen-v1-3-0`: el requisito que declaraba el arbitraje como diferido y el de la
  validación fuera de muestra en las conclusiones pasan a reflejar el arbitraje ejecutado.
- `tesis-defensa`: el documento de respuestas deja de incorporarse como Anexo J y queda como
  material de defensa (sujeto a la decisión de los autores, OQ3 del design).

## Impact

| Área | Impacto |
|---|---|
| `evaluation/data/campana/analisis/` | Nuevo script con pruebas, JSON, MD y SHA256SUMS; entrada en el README de la carpeta |
| `docs/Tesis/v10 (IA)/paper/sections/` | `00-glosario`, `00-portada`, `00-resumen`, `01`, `02`, `03`, `04`, `05`, `07`, `08`, `09`, `10`, `11` (solo si se verifica la resolución) y `12` |
| `docs/Tesis/v10 (IA)/Bibliography_base.bib` | Claves o años corregidos, URL de ServiceNow, versión del repositorio, entrada nueva condicional |
| `docs/Tesis/Correcciones/` | `numeros-canonicos.md` (3.29), `dictamen-correcciones.md` (filas C18, libro mayor) |
| `docs/diagrams/cronograma.md` y `paper/figures/cronograma.png` | Hitos de noviembre |
| `paper/compilacion.md`, `docs/Tesis/tesis_ultima_version.pdf` | Regenerados con la compilación final |
| `CHANGES.md` | Fase nueva del change |
| Repositorio remoto | Tag nuevo y push, solo con confirmación de los autores |

Sin cambios en `App/`, `n8n/`, el clasificador, la configuración, los corpus ni las predicciones.

## Risks and rollback

- Que la lectura ponderada parezca elegida por favorable: se rotula la cruda como primaria y se
  citan los diseños previos que ya preveían la ponderación (design D1).
- Paginación y resumen al límite (`248` y `247` palabras sobre 250): se compensa retirando el
  Anexo J y recortando el resumen; libro mayor con delta.
- Regresión del hash del tag: patrón de dos commits con verificación explícita (design D9).
- Colisión con trabajo en curso sobre `main`: `git fetch` y rebase antes de cada bloque de prosa.
- Rollback: `git revert` de los `.tex`, del `.bib`, del script y sus salidas y de la sección 3.29;
  el tag, si ya se publicó, no se borra: se supera con uno nuevo.

## Success Criteria

- [ ] El script reproduce `142/206`, `0,7024` y `0,8447/103` antes de calcular y es determinista.
- [ ] Ninguna cifra nueva entra a la tesis sin estar antes en la sección 3.29 del memo.
- [ ] `08-discusion.tex`, `09-conclusiones.tex` y `10-recomendaciones.tex` no contienen `0,2222`,
      «sin el arbitraje» ni «41 de los 47».
- [ ] El resumen y el *abstract* mencionan la exactitud fuera de muestra y la línea de base con
      ≤ 250 palabras cada uno.
- [ ] `rg "c-[0-9]{3}"` sobre `sections/*.tex` no devuelve líneas fuera de comentarios.
- [ ] Compilación sin errores, referencias ni citas indefinidas; `verify_citations.py` y el
      verificador de la matriz en verde; pytest de `evaluation/` en verde.

## Hallazgos que cambiaron al verificar contra `ebd2baa`

Ya resueltos o modificados por c-216 y c-217 (no se reabren):

- Hipótesis subsidiaria de eficiencia «sin contraste» (dictamen, sección 2): c-217 la contrastó
  con resultado no concluyente (`01-introduccion.tex:38`, `04-marco-metodologico.tex:89`,
  `07-resultados.tex:374`, `08-discusion.tex:10`, `09-conclusiones.tex:6`). La frase de
  `04-marco-metodologico.tex:83` («no contrasta la hipótesis de eficiencia») se refiere a la línea
  de base y sigue siendo correcta.
- «Ningún trabajo declara un corpus en español» con el dato ausente en cuatro de seis filas
  (dictamen, sección 4): `01-introduccion.tex:66` ya dice que el idioma no se informa en la mayoría
  y acota la ausencia al alcance revisado.
- `05-arquitectura.tex:68` (latencia y costo): la afirmación sigue, pero ahora c-217 midió la razón
  de llamadas y de costo (`07-resultados.tex:394`); se concilia, no se retira sin más.
- `09-conclusiones.tex:47` ya acota la viabilidad a «dentro de la muestra» y remite a
  `tab:gemini-solo`; falta el matiz fuera de muestra.

Desplazados o ampliados respecto del dictamen:

- «Seis amenazas» está en `04-marco-metodologico.tex:93` (el dictamen cita `:89`).
- Commits que modifican `sections/` entre `v1.3.0` y `origin/main`: `25` (el dictamen contó `22`
  hasta `5734ea8`).
- Identificador interno adicional no citado por el dictamen: `12-anexos.tex:151` (`c-201`).

Hallazgos nuevos de esta verificación:

- `07-resultados.tex:316` rotula `0,5082` de `Sistemas` como «exactitud estricta»; es su
  sensibilidad (`31/61`).
- `08-discusion.tex:28` y `10-recomendaciones.tex:18` afirman que el error de `Sistemas` va a «una
  única clase adyacente»; con `61` casos, `16` de `30` errores van a `Soporte Tecnico Software` y
  `8` a `Seguridad Informatica`.
- El requisito vigente de `tesis-dictamen-v1-3-0` exige declarar el arbitraje como diferido, y
  OOS-018 de `evaluation-out-of-sample-validation` describe un resultado sobre `150` casos cuando el
  corpus arbitrado tiene `206`: ambos quedan desactualizados y se modifican aquí.
- La fuente del Anexo J ya existe como `docs/defensa/respuestas-tribunal.md` y ninguna referencia
  del cuerpo apunta a `sec:anexo-respuestas-tribunal`.
- El resumen y el *abstract* ya están en `248` y `247` palabras sobre un límite de 250.
