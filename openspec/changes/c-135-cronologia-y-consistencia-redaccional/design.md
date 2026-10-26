## Context

El change cierra B9, B10 y la parte de cota telefonica de B13 del dictamen CONEAU 2026-10-22 (ver `proposal.md` - Why). Es documental: edita LaTeX, agrega una figura generada desde Mermaid y dos archivos de trazabilidad. Abreviaturas usadas aqui y en `tasks.md`: `S` = `docs/Tesis/v10 (IA)/paper/sections`, `F` = `docs/Tesis/v10 (IA)/paper/figures`, `D` = `docs/diagrams`, `C` = `docs/Tesis/Correcciones`.

**Numeracion.** El PDF numera los capitulos segun el orden de `main.tex`, que inserta `11-aspectos-legales.tex` como capitulo 7 (c-105): `07-resultados.tex` es el capitulo 8 del PDF; el archivo `08-discusion.tex` es el 9 y el archivo `09-conclusiones.tex` es el 10. El dictamen numera por archivo. Este change cita siempre archivos.

**Restricciones:**

- **Sin fabricacion:** ninguna fecha ni cifra se inventa, interpola ni se expresa con mas precision que su evidencia.
- **Numeros canonicos congelados** (`C/numeros-canonicos.md`): no se introduce ni altera ningun numero de resultados. Las unicas cifras nuevas son fechas (con procedencia), metricas de trabajos ajenos (textuales de su fuente) y el tiempo de espera de la inferencia tomado de `settings.py` (D15).
- **Paginas:** 101 hoy; c-116 y c-121 trataron 100/101 como tope duro. Este change debe ser neutral (D12); el tope absoluto lo verifica c-141.
- **Changes concurrentes** sobre los mismos archivos (mapa de propiedad en D11), en el orden fijado por c-141: c-130 -> c-134 (codigo) -> c-131 -> c-132 -> c-133 -> c-134 (tesis) -> c-138 -> c-136 -> **c-135** -> c-139 -> c-140 -> c-137 -> c-141.
- **Modo TDD estricto: no aplica** (no hay codigo de produccion ni runner para LaTeX); la verificacion es por `rg`, compilacion y conteo de paginas.

**Estado verificado de las fuentes (solo lectura, 2026-10-22):**

- Cronologia en el texto:
  - `S/04-marco-metodologico.tex:97`: "seis iteraciones de dos semanas cada una, totalizando 12 semanas de desarrollo efectivo", seguida de una lista de seis items (`:99-106`) que repite la de 6.6.
  - `S/06-implementacion.tex:68`: "seis iteraciones de dos semanas cada una"; `:70-77`: lista con "(Semanas 1--2)" ... "(Semanas 11--12)"; el item 6 es la validacion experimental; el item 5 (`:75`) afirma que el ajuste del filtro deterministico y del prompt se hizo "sin exposicion al corpus de validacion de 200 casos".
  - `S/04:14` y `S/04:45`: flujo manual de junio a agosto de 2026, automatizado de septiembre a octubre de 2026; `S/04:61`: "ventana de septiembre a octubre de 2026".
  - `S/08-discusion.tex:46`: version del modelo "vigente al momento del estudio (junio de 2026)".
  - `S/01-introduccion.tex:76`: "version vigente al momento del estudio (entre junio y octubre de 2026)".
  - `S/12-anexos.tex:29` remite a "las seis iteraciones de desarrollo"; `S/12-anexos.tex:15` declara que los diagramas se generan desde Mermaid en `docs/diagrams/`.
- Evidencia del repositorio (comandos en D5):
  - Primer commit 2026-04-06; commits por mes: abril 4, mayo 16, junio 79, julio 22, agosto 0, septiembre 120, octubre 278; sin commits entre 2026-07-10 y 2026-09-10; 14 semanas ISO con actividad.
  - Pull requests fusionados: #1-#7 (2026-05-20 a 05-22: modulo de gestion de incidentes y frontend), #8-#27 (2026-06-10 a 06-12: fundacion OPSX, validacion del flujo N8N, disparadores de canales, framework de evaluacion, CI), #28-#31 (2026-09-17).
  - Changes archivados: c-01..c-10 (2026-06-10/11), c-11..c-26 (2026-07-02/03), c-27..c-124 (2026-09-11 a 2026-10-22).
  - Modelo: el clasificador uso `gemini-2.5-flash` hasta el commit `11036be` (2026-09-24, "migrar el clasificador a Gemini 3.6 Flash"); desde entonces `gemini-3.6-flash` (`App/Backend/app/config/settings.py:78`).
  - Campana automatizada: instrumentacion de tiempos de extremo a extremo (c-39, archivado 2026-09-20); corrida completa de correo y formulario, 119 casos, el 2026-10-02 (c-68, `tasks.md` 6.4); corrida completa telefonica, 81 casos, el 2026-10-06 (c-70, `tasks.md` 8.2); recalculo de la metrica telefonica decidido el 2026-10-12 y versionado el 2026-10-19 (c-77, commit `4602bf5`); `evaluation/report.md` versionado el 2026-10-20 (commit `8e1ca55`).
  - Confirmacion del autor del 2026-10-09, registrada en `C/dictamen-correcciones.md` (T6): flujo manual jun-ago 2026; automatizado sep-oct 2026.
  - Ajustes del clasificador medidos sobre el corpus: c-71 (commit `1368fd8`, 2026-10-05) y c-74 (commit `d6bb474`, 2026-10-07; calibracion out-of-fold decidida por el autor el 2026-10-07) midieron OFFLINE sobre los 200 casos, despues de la corrida de correo y formulario y en paralelo a la telefonica (ver OQ-3).
  - El campo de iteracion del tablero GitHub Projects no es legible con el token actual (falta el scope `read:project`).
- Consistencia redaccional:
  - `S/07-resultados.tex:6` anuncia "cuatro dimensiones ... reduccion de la intervencion humana ..."; el capitulo tiene cinco `\subsection`: `:8` tiempos, `:71` matriz y metricas, `:134` "Intervencion humana en el flujo automatizado" (label `subsec:reduccion-intervencion`), `:140` "Calibracion de la confianza" (sin label) y `:167` analisis de errores.
  - `S/03-estado-del-arte.tex:60`: "cuatro dimensiones relevantes: la solucion considerada, su modalidad de despliegue, su capacidad de clasificacion automatica y su modelo de costo"; `tab:comparativa` (`:62-80`) tiene cuatro columnas (Solucion, Despliegue, Clasificacion automatica, Modelo de costo), linea de fuente y fecha de consulta (19-10-2026).
  - `S/03:82`, primera oracion: "ninguna de las soluciones revisadas combina simultaneamente las cuatro propiedades ..."; la cuarta es la telefonia, sin columna. La segunda oracion (brecha) no depende de la telefonia.
  - `tab:trabajos-academicos` (`S/03:34-54`): "no reportado en el alcance revisado" en la metrica de Revina 2020, Paket 2024, Liu 2025 y Colavito 2025; en Zangari 2023 la metrica figura, pero el idioma no; en Liu faltan tamano e idioma y en Colavito el tamano. La fila de Paramesh 2019 esta completa (la pagina de origen de sus cifras es de c-139, recomendacion A4).
  - Telefono: `S/09-conclusiones.tex:39` ("20,1 segundos ... via practicamente util") no declara la cota; `S/04:67`, `S/06:52`, `S/07:32` y la fila de `tab:tiempos-canal` (20,09 s, "cota inferior") si la declaran.
  - Anexo H (asignado por el orquestador a partir de un hallazgo de c-136): `S/12-anexos.tex:88` (`subsec:anexo-parametros-config`) presenta los hiperparametros de `tab:anexo_gemini_params` como "optimizados para equilibrar exactitud, latencia y costo de inferencia", y la fila de `candidate_count` (`:102`) dice que "optimiza la latencia"; en cambio, `S/05-arquitectura.tex:74` (`subsec:capa-procesamiento`) declara que los mismos valores "corresponden a la configuracion adoptada para el despliegue y no a un procedimiento de optimizacion documentado" y remite su calibracion a trabajo futuro. El requisito vigente "Parametros de inferencia sin calificativo no respaldado" solo cubre el capitulo 5. La leyenda de la tabla es neutra.
  - Tiempo de espera (asignado por el orquestador; c-140, su dueno alternativo, es opcional): `S/05:74` declara "timeout = 10 s" y la fila `timeout` de `tab:anexo_gemini_params` (`S/12-anexos.tex:104`) "10 segundos", con la justificacion "al excederse, el clasificador devuelve confianza 0,0 y marca el caso para revision humana". `App/Backend/app/config/settings.py` fija `gemini_timeout_seconds = 30` (`:85`, "limite de espera antes de activar fallback", por intento; introducido en el commit `11036be` del 2026-09-24, que reemplazo los 10 s) y `gemini_total_timeout_seconds = 60` (`:104`, presupuesto de reloj para toda la clasificacion, intentos y esperas incluidos; introducido con los reintentos acotados de c-58, `gemini_max_retries = 2`, en el commit `429f2c9` del 2026-09-29). Ambos son anteriores a las corridas de la campana (2026-10-02 y 2026-10-06). En los archivos versionados no hay override activo: `docs/operational-guide.md:67` solo muestra comentado `GEMINI_TOTAL_TIMEOUT_SECONDS=60` y ningun archivo versionado fija `GEMINI_TIMEOUT_SECONDS`; los `.env*` no se leen por politica de permisos. `CLAUDE.md` y `openspec/config.yaml` tambien dicen 10 s y son de c-130. `S/06:60` dice que no se implementaron reintentos con retroceso exponencial, pero se refiere a la invocacion de N8N al backend (dueno: c-140), no a la del backend al modelo.
- Acceso a las fuentes de la tabla (OpenAlex, consulta 2026-10-22): Revina 2020, acceso abierto (IEEE Access), resumen sin cifras; Zangari 2023, acceso abierto hibrido (ESWA y repositorio institucional), resumen con cifras y sin idioma; Paket 2024, acceso cerrado (IEEE, UBMK), resumen solo cualitativo; Liu 2025, acceso abierto (ACM y arXiv 2504.08475), resumen sin cifras; Colavito 2025, acceso cerrado segun OpenAlex (IST), resumen no indexado alli.
- Paginas (PDF de 101 paginas; lineas no vacias por pagina segun `pdftotext`, unas 32 en una pagina llena; cada capitulo empieza en pagina nueva): ultima pagina del capitulo 1 (p. 17) con 31 lineas; capitulo 3 (p. 30) llena; capitulo 4 (p. 39) con 29 (unas 3 libres); capitulo 6 (p. 60) con 21 (unas 11 libres); capitulo 8 (archivo `07-resultados`, p. 73) con 12 (unas 20 libres); capitulo 9 = `08-discusion` (p. 80) con 31; capitulo 10 = `09-conclusiones` (p. 83) con 32. El indice de figuras (p. 9) tiene lugar para una entrada mas.

## Goals / Non-Goals

**Goals:**

- Una cronologia unica, fechada y con procedencia, que concilie `01`, `04`, `06` y `08` (B9).
- Cerrar los residuos redaccionales de B10 (parrafo introductorio de resultados, dimensiones y sintesis de `tab:comparativa`, metricas de `tab:trabajos-academicos`) y la salvedad de cota de B13.
- Alinear el Anexo H con el capitulo 5 en la descripcion de los parametros de inferencia (configuracion adoptada, no optimizada), sin cifras nuevas.
- Alinear el tiempo de espera declarado en el capitulo 5 y en el Anexo H con la configuracion vigente durante la campana automatizada, con procedencia registrada.
- Neutralidad numerica y de paginas.

**Non-Goals:**

- No se escribe ninguna fecha sin evidencia o confirmacion de los autores: las tareas de fechas quedan bloqueadas hasta resolver OQ-1/OQ-2.
- No se resuelve la cuestion de validez del ajuste del clasificador sobre el corpus (OQ-3): se registra y, solo si el usuario lo decide, se ajusta la frase de `S/06:75`.
- No se tocan, por ser de otros changes: el cronometraje y el efecto Hawthorne (`S/04:16`) y la tabla de tiempos por canal (c-134); la descripcion del gate (c-130); metricas por etapa, por canal y exactitud laxa (c-131); el balance neto (c-132); hipotesis, objetivos y metrica primaria (c-133); recomendaciones (c-136); la ortotipografia fuera de los fragmentos reescritos (c-137); nuevas referencias, protocolo de revision y literatura de calibracion y cascadas (c-138); atribuciones y metadatos, incluidas `S/03:32`, `S/03:28`, `S/03:30`, `S/03:56` y `S/01:66` (c-139); endurecimiento tecnico (c-140); release, render Markdown y tags (c-141).
- No se agrega una columna a `tab:comparativa` (salvo que OQ-4 elija la opcion a).
- No se corrige la frase "costo operativo dominado por el consumo de API de inferencia" de `S/09-conclusiones.tex:49`: la corrige c-132.
- No se cambia ningun valor de los parametros de inferencia salvo el tiempo de espera (D15).
- No se tocan `CLAUDE.md` ni `openspec/config.yaml`, que tambien declaran 10 s: los alinea c-130 con confirmacion del usuario; c-135 solo deja la nota de coordinacion (D13).
- No se edita `S/06:60` (reintentos de N8N al backend; dueno c-140): la redaccion de D15 distingue ese nivel del de los reintentos del backend al modelo.
- No se fechan hitos que B9 no pide (por ejemplo, el periodo relevado del universo de 63 dias habiles).

## Decisions

### D1 - Fuente unica de la cronologia: `D/cronograma.md`

Se crea `D/cronograma.md` con: (a) un encabezado descriptivo, como los demas diagramas de `D/`; (b) un bloque `mermaid` de tipo `gantt`; (c) una tabla **Procedencia** con una fila por elemento del cronograma: elemento, fecha o intervalo, precision (dia o mes), evidencia (commit, pull request, change archivado o confirmacion de los autores con su fecha) y comando o documento que la reproduce. Toda mencion textual de periodos en `S/01`, `S/04`, `S/06` y `S/08` (y `S/12-anexos.tex:29` si cambiara el numero de iteraciones) se deriva de esta fuente.

**Alternativas:** fechar solo en el `.tex` (descartada: sin fuente unica las tres cronologias ya divergieron); registrar las fechas en `C/numeros-canonicos.md` (descartada: ese memo fija numeros de resultados; mezclarlo con fechas de gestion lo desnaturaliza y obligaria a reabrir su gate).

### D2 - Representacion: figura Gantt Mermaid renderizada a PNG

Se usa un diagrama `gantt` de Mermaid con tres secciones: "Construccion (Scrumban)" (seis barras, una por iteracion), "Estudio" (campana manual y campana automatizada) y "Modelo evaluado" (hito de integracion de `gemini-3.6-flash` el 2026-09-24, mas los hitos de corrida que confirme OQ-2). Parametros: `dateFormat YYYY-MM-DD` y `axisFormat` numerico (`%m/%Y` o `%d/%m`), porque Mermaid rotula los meses en ingles; rotulos con la ortografia del manuscrito. Esqueleto (las fechas entre corchetes angulares se completan solo con valores confirmados):

```
gantt
    dateFormat YYYY-MM-DD
    axisFormat %m/%Y
    section Construccion (Scrumban)
    Iteracion 1                 :it1, <inicio>, <fin>
    (iteraciones 2 a 6 analogas)
    section Estudio
    Campana manual              :cm, <inicio>, <fin>
    Campana automatizada        :ca, <inicio>, <fin>
    section Modelo evaluado
    Integracion de gemini-3.6-flash :milestone, m1, 2026-09-24, 0d
```

Render como c-80: bloque extraido a un `.mmd` temporal fuera del repositorio y `mmdc -i <tmp>.mmd -o "F/cronograma.png" -b white -s 2` (mmdc via `npx -y @mermaid-js/mermaid-cli` o el contenedor `minlag/mermaid-cli`), registrando la version de mmdc en la tabla de procedencia. La leyenda declara la precision de las fechas y su fuente (historia del repositorio y confirmacion de los autores).

**Alternativas:** (i) tabla `tab:cronograma` con columnas Elemento / Periodo / Evidencia: expresa precision mixta en texto y la evidencia por fila, pero no muestra superposiciones ni la pausa; costo similar en paginas (~13 lineas). Queda como **respaldo** si mmdc no puede ejecutarse o si D12 lo exige. (ii) Script matplotlib a PDF vectorial (como el boxplot y la matriz): descartado porque la convencion del repositorio para diagramas que no derivan de datos del corpus es Mermaid (`S/12-anexos.tex:15`). (iii) Solo prosa: descartada; el dictamen pide un cronograma.

### D3 - Ubicacion: seccion 6.6 (`subsec:conexion-scrumban`), referenciada desde 1.8, 4.2, 4.9 y 9.3

La figura (`\label{fig:cronograma}`, `[htbp]`, `width=\textwidth,height=0.28\textheight,keepaspectratio`) se inserta tras la lista de iteraciones de 6.6, que es donde se vinculan iteraciones y artefactos. Se referencia una vez en 4.2 (ventanas de las campanas), en 4.9, en 1.8 y en la cuarta limitacion de 9.3. Razon de paginas: la ultima pagina del capitulo 6 tiene unas 11 lineas libres y la figura con leyenda ocupa unas 9-11; la del capitulo 4 tiene unas 3. La lista de 4.9 duplica la de 6.6 y se condensa en una oracion que remite a 6.6 y a la figura, conservando el parrafo de demarcacion (requisito "Demarcacion del metodo de investigacion"); condensar listas redundantes es una palanca admitida por "Reduccion sin perdida de contenido cientifico".

**Alternativas:** figura en 4.9 o en 4.2 (descartadas: el capitulo 4 tiene unas 3 lineas libres; con la condensacion el neto seria de unas +5 lineas, con riesgo de +1 pagina); en el capitulo 8 (`07-resultados`, unas 20 lineas libres) (descartada: no es su lugar natural; queda solo como palanca extrema de D12).

### D4 - Relato conciliado

Plantilla de redaccion, sujeta a las respuestas de OQ-1/OQ-2:

1. **Iteraciones.** Se conserva "seis iteraciones" (de ello depende `S/12-anexos.tex:29`). Su calendario se declara con los intervalos confirmados. "De dos semanas cada una" y "12 semanas de desarrollo efectivo" se conservan solo si los autores confirman esa duracion nominal y, en ese caso, se aclara que las iteraciones no fueron contiguas. Los rotulos "(Semanas k--k+1)" de 6.6 se reemplazan por los intervalos o se retiran en favor de la figura.
2. **Campana manual.** La medicion del flujo manual, a cargo de los operadores de la mesa de ayuda, transcurre en paralelo a la construccion y no es una iteracion; se declara asi en 6.6.
3. **Campana automatizada.** Corresponde a la iteracion 6 (validacion experimental). La ventana textual es la confirmada; las corridas documentadas se muestran como hitos si OQ-2 lo confirma.
4. **Version del modelo.** La version evaluada es `gemini-3.6-flash`, integrada al clasificador el 2026-09-24 (commit `11036be`) y vigente durante la campana automatizada. "Junio de 2026" se retira de `S/08:46`: en junio el clasificador usaba `gemini-2.5-flash`.
5. **Delimitacion de `S/01:76`.** La naturaleza temporal de los resultados se refiere a la version del modelo vigente durante la campana automatizada, no a todo el estudio.
6. **Coherencia de las descripciones.** Ninguna descripcion de iteracion puede afirmar un orden o una condicion incompatible con sus fechas (OQ-3 para el item 5).

**Alternativa:** conservar las "12 semanas contiguas" y ajustar las campanas a ese molde (descartada: contradice la historia del repositorio y la ventana que el autor confirmo el 2026-10-09).

### D5 - Procedimiento de derivacion de fechas, sin invencion

1. **Anclas del repositorio** (solo lectura; resultados a la tabla de procedencia):
   - `git log --reverse --date=short --format='%ad %h %s' | head -20` (inicio de la actividad).
   - `git log --date=format:'%G-W%V' --format='%ad' | sort | uniq -c` (semanas activas y pausa).
   - `gh pr list --state merged --limit 200 --json number,title,mergedAt` (integraciones por tema).
   - `ls openspec/changes/archive/` (el prefijo es la fecha de archivo de cada change; `CHANGES.md` solo indexa, no fecha).
   - `git for-each-ref --sort=creatordate --format='%(refname:short) %(creatordate:short)' refs/tags` (los tags `v1.0.0` a `v1.1.1` son de 2026-10-21/22: acotan el cierre documental, no las iteraciones).
   - `git log -S "gemini-3.6-flash" --date=short --format='%ad %h %s' -- App/Backend/app/config/settings.py` (version del modelo).
   - `openspec/changes/archive/2026-10-09-c-68-corpus-ingesta-n8n/tasks.md` (6.4), `openspec/changes/archive/2026-10-06-c-70-softphone-corpus-telefonia/tasks.md` (8.2), `openspec/changes/archive/2026-10-20-c-77-tesis-errores-estadisticos-inferenciales/tasks.md` (grupo E) y `git log --date=short --format='%ad %h %s' -- data/corpus_evaluacion_pseudonimizado.json evaluation/report.md` (corridas y consolidacion).
2. **Fuente primaria de las iteraciones:** el campo de iteracion del tablero GitHub Projects (`gh project list --owner lucaGomezB` y `gh project field-list <n> --owner lucaGomezB --format json`), que requiere que el usuario otorgue el scope con `gh auth refresh -s read:project`; o los registros de los autores.
3. **Confirmacion de los autores** para toda fecha sin fuente primaria, registrada con su fecha en la tabla de procedencia.

Reglas: (i) las fechas de commit son evidencia de actividad, no limites de iteracion; ninguna se convierte en inicio o fin de una iteracion sin confirmacion; (ii) cada elemento declara su precision (dia o mes) y la figura no la excede; (iii) ninguna fecha del texto puede contradecir un ancla (por ejemplo, la version del modelo); (iv) si un elemento no se confirma, se rotula con la precision disponible (por ejemplo, "junio a agosto de 2026") y jamas se completa por interpolacion.

### D6 - `tab:comparativa`: las dimensiones excluyen la clave de fila

El parrafo `S/03:60` pasa a declarar **tres** dimensiones (modalidad de despliegue, capacidad de clasificacion automatica y modelo de costo); `Solucion` es la clave de fila. Se MODIFICA el requisito de c-121 cuyo escenario "el numero de dimensiones enunciadas coincide con el numero de columnas" origino el residuo. La tabla conserva sus cuatro columnas, rotulo y linea de fuente.

**Alternativa:** hablar de "cuatro columnas" (descartada: la columna Solucion no es una dimension de comparacion).

### D7 - Telefonia: se retira de la afirmacion comparativa (opcion b)

La primera oracion de `S/03:82` declara que ninguna solucion revisada combina las **tres** propiedades que la tabla releva (despliegue autoalojado, costo bajo y predecible, clasificacion automatica nativa con NLP moderno), afirmacion que la tabla sostiene fila por fila. El canal telefonico con transcripcion automatica se menciona en `S/03:84` como rasgo de la arquitectura propuesta, sin afirmar que las soluciones revisadas carezcan de el. Razones: (1) agregar la columna exige verificar en la documentacion publica de cinco proveedores una capacidad que depende de modulos y planes, con nueva fecha de consulta; Jira Service Management y osTicket no tienen entrada `@online` (las nuevas referencias son de c-138); y obliga a modificar el requisito "La tabla SHALL conservar sus cuatro columnas"; (2) el capitulo 3 termina en pagina llena y una quinta columna agrega unas 2-4 lineas; (3) la brecha declarada en la segunda oracion de `S/03:82` no depende de la telefonia; (4) precedente de c-121 D1 (editar la prosa antes que agregar columnas).

**Alternativa (a), si el usuario la prefiere (OQ-4):** consultar la documentacion publica vigente de los cinco proveedores; poblar la columna "Canales / telefonia" solo con lo verificable ("Si (modulo X)", "No nativa", "No documentado"); fecha de consulta en la linea de fuente; coordinar con c-138 las entradas `@online` nuevas; MODIFICAR el requisito de columnas en el delta spec antes del apply.

### D8 - `tab:trabajos-academicos`: completar las metricas solo desde la fuente

- **Alcance:** filas de Revina 2020, Zangari 2023, Paket 2024, Liu 2025 y Colavito 2025; columnas "Metrica reportada" y "Corpus/idioma". La fila de Paramesh 2019 no se toca (su pagina de origen es de c-139).
- **Orden de consulta:** (1) resumen en la pagina DOI del editor (o en OpenAlex o Crossref); (2) texto completo de acceso abierto (version del editor, preprint o repositorio institucional); (3) acceso institucional de los autores (OQ-5).
- **Regla de consignacion:** solo cifras textuales de la fuente (nombre de la metrica, valor y modelo o condicion), sin recalcular, promediar ni inferir; formato de la tesis (coma decimal, `\,\%`); si la fuente reporta varias cifras, se consigna la principal que declaran sus autores (la del resumen o la de su tabla principal) y, si cabe en la celda, la comparacion BERT frente a LLM generativos que necesita `S/03:32`.
- **Residuo:** donde la fuente accesible no consigna la cifra, se conserva la leyenda "no reportado en el alcance revisado" que exige el requisito de c-117 y se le agrega el motivo abreviado (por ejemplo, "resumen sin cifra; texto completo de acceso cerrado").
- **Registro de procedencia:** `C/extraccion-metricas-trabajos-c-135.md`, con una fila por celda: obra, DOI, URL consultada, fecha de consulta, ubicacion en la fuente (seccion, tabla o pagina), valor consignado y nota de acceso; precedente: la bitacora `C/bitacora-busqueda-c-110.md`.
- **Linea de fuente de la tabla:** "elaboracion propia sobre las obras citadas: resumen y, cuando es de acceso abierto, texto completo (consulta <fecha>)".
- **Sin altas en el `.bib`:** las cinco claves ya existen; `verify_citations.py` debe seguir sin huerfanas ni entradas sin usar.
- **Coherencia con c-139:** `S/03:32` ("desplazamiento hacia LLM") y `S/01:66` (idiomas de los corpus) deben quedar coherentes con la tabla completada. En el orden fijado, c-139 aplica despues de c-135 y necesita la tabla ya completada: c-135 deja la tabla y el registro completos y anota en el registro las discrepancias que detecte con esas frases, sin editarlas; c-139 las resuelve consumiendo el registro.
- **Paginas:** las celdas no deben quedar mas altas que las actuales (hoy de 4 a 6 lineas en una columna de 3,1 cm).

**Alternativa:** dejar "no reportado" y ampliar el alcance de la leyenda (descartada: el dictamen senala que los resumenes y los DOI permiten completar la tabla).

### D9 - Parrafo introductorio de resultados (`S/07:6`)

Se enumeran las subsecciones vigentes al aplicar, en su orden y con denominaciones coherentes con sus titulos, sin cardinal (o con un cardinal igual al numero de `\subsection`), y la dimension se llama "intervencion humana". El label `subsec:reduccion-intervencion` no se renombra: es invisible en el PDF y renombrarlo romperia los `\autoref` existentes. En el orden fijado, c-130, c-131 y c-134, que pueden cambiar la estructura del capitulo, ya aplicaron cuando aplica c-135.

**Alternativa:** fijar hoy "cinco dimensiones" (descartada: se desincronizaria si c-131 agrega una subseccion).

### D10 - Cota inferior del tiempo telefonico en `S/09:39`

Se agrega a la oracion del canal telefonico que los 20,1 s constituyen una cota inferior de la duracion real de la llamada por el tope de 45 s de grabacion, con remision a 4.6 (`subsec:metricas-instrumentos`). La redaccion es de longitud neutra porque la ultima pagina del capitulo 10 esta llena; por ejemplo, condensando la aposicion "que incluye la duracion de la llamada grabada ademas de la latencia de procesamiento" y reemplazando el cierre retorico "y no como una demostracion de laboratorio" por la salvedad. El valor 20,1 no cambia (redondeo del 20,09 de `tab:tiempos-canal`).

**Alternativa:** una nota al pie (descartada: agrega lineas al pie de una pagina llena).

### D11 - Mapa de propiedad de los fragmentos compartidos

| Archivo | Fragmento (ancla) | Dueno | Notas |
|---|---|---|---|
| `S/03` | Parrafo de Paramesh (`:28`), de Revina (`:30`), frase "desplazamiento hacia LLM" (`:32`), evaluacion multilingue (`:56`) | c-139 | c-135 no los edita |
| `S/03` | `tab:trabajos-academicos`: celdas de las cinco filas indicadas y linea de fuente | c-135 | filas nuevas: c-138 |
| `S/03` | Protocolo de revision (`:8`) y nuevos parrafos de calibracion y cascadas | c-138 | |
| `S/03` | Parrafo introductorio de `tab:comparativa` (`:60`) | c-135 | |
| `S/03` | `tab:comparativa` | sin cambios | c-135 solo si OQ-4 = (a) |
| `S/03` | `:82`, primera oracion (propiedades) | c-135 | |
| `S/03` | `:82`, segunda oracion (brecha) | c-138 si incorpora calibracion y cascadas | |
| `S/03` | `:84` (posicionamiento): inciso de telefonia | c-135 | |
| `S/04` | Ventanas de campana en `:14`, `:45` (ultima oracion) y `:61` (frase de ventana) | c-135 | |
| `S/04` | Parrafo de medicion en vivo y Hawthorne (`:16`) | c-134 | |
| `S/04` | Frase del gate en `:61`; resto de 4.4 y 4.7 | segun c-130 / c-134 | misma oracion que la ventana en `:61` |
| `S/04` | 4.9: oracion de iteraciones y lista (`:97-106`) | c-135 | tildes de `:108` y `:110`: c-137 |
| `S/06` | 6.6 completa (`:66-79`) y la figura | c-135 | item 5: OQ-3 |
| `S/06` | 6.5, 6.7 y descripcion del gate | c-140 / c-130 | comparten la holgura de paginas del capitulo 6 |
| `S/07` | Parrafo introductorio (`:6`) | c-135 | 7.1: c-134; 7.3: c-130; 7.4 y metricas por etapa o canal: c-131 |
| `S/08` | Cuarta limitacion (`:46`): solo la fecha | c-135 | resto de 9.3: segun c-130..c-134 |
| `S/09` | `:39`, oracion del canal telefonico | c-135 (confirmado por el orquestador) | primera oracion de `:39` y tabla de objetivos: c-133 (y c-131) |
| `S/09` | `:49`, "costo operativo dominado por el consumo de API" | c-132 | c-135 no la toca |
| `S/01` | `:76`, parentesis temporal | c-135 | `:66`: c-139; hipotesis y objetivos: c-133 |
| `S/12-anexos` | `:88` (prosa de `subsec:anexo-parametros-config`), leyenda de `tab:anexo_gemini_params` y justificacion de `candidate_count` (`:102`) | c-135 (asignado desde c-136) | valores de la tabla: sin cambios |
| `S/12-anexos` | `:29` ("seis iteraciones") | c-135 solo si OQ-1 cambia el numero de iteraciones | |
| `S/12-anexos` | `:104`, fila `timeout` de `tab:anexo_gemini_params` (valor y justificacion) | c-135 (D15, asignado por el orquestador) | c-140 (opcional, despues): solo verifica |
| `S/05` | `:74`, expresion del tiempo de espera | c-135 (D15) | resto de `:74`: sin cambios |
| `S/06` | `:60`, reintentos de N8N al backend | c-140 | c-135 no la edita |
| `C/conteos-canonicos-tecnicos.md` | upsert del tiempo de espera | c-135 (D15) | |
| `CLAUDE.md`, `openspec/config.yaml` | tiempo de espera de 10 s | c-130 (con confirmacion del usuario) | c-135 coordina por nota |

Regla: cada change edita solo sus fragmentos; el que aplica despues rebasa sobre el texto vigente y verifica con `git diff` que no revierte ediciones ajenas. En el orden fijado, c-138 y c-136 aplican antes que c-135 (c-135 rebasa sobre sus agregados en `S/03`, incluida la segunda oracion de `:82` si c-138 la modifico), y c-139, c-140 y c-137 aplican despues. El texto nuevo se escribe con ortografia correcta; las tildes preexistentes fuera de los fragmentos reescritos son de c-137.

### D12 - Presupuesto de paginas: neutral respecto de la linea base

- **Linea base:** se mide al iniciar el apply, despues de los changes previos; criterio: total final menor o igual que la linea base.
- **Estimacion sobre la v1.1.1 (101 paginas):** figura, unas +9 a +11 lineas en el capitulo 6 (unas 11 libres): 0 paginas esperadas; 4.9 condensada: unas -5 a -6 lineas en el capitulo 4; capitulo 3: de -1 a +2 lineas (sintesis -1,5; inciso de telefonia +1; tabla +/-2) sobre una ultima pagina llena; capitulos 1, 9 y 10 del PDF: redacciones neutras sobre ultimas paginas llenas; capitulo 8 (`07-resultados`): +0 a +1 linea con unas 20 libres; Anexo H: redaccion neutra (el ultimo anexo, p. 101, tiene unas 21 lineas libres). **Neto esperado: 0 paginas; peor caso: +1** (si los changes previos, en particular c-130, consumen la holgura del capitulo 6).
- **Palancas, en orden:** (1) condensar 4.9 (ya previsto); (2) limitar el alto de la figura y acortar la leyenda; (3) reemplazar la figura por la tabla compacta de respaldo (D2); (4) escalar a c-141.
- **Aviso a c-140:** aplica despues de c-135 y edita 6.5 y 6.7; debe contar con la figura al medir la holgura del capitulo 6. Se deja constancia en el grupo de `C/dictamen-correcciones.md` (D13).

### D13 - Trazabilidad y no regresion

- Se agrega a `C/dictamen-correcciones.md` el grupo "Cronologia y consistencia redaccional (c-135)", con el mapeo de B9, B10, B13 (cota) y la consistencia del Anexo H (asignada desde c-136) a correccion, archivo y decision, siguiendo el patron de los grupos existentes (por ejemplo, c-95).
- Las procedencias quedan en `D/cronograma.md` (fechas), en `C/extraccion-metricas-trabajos-c-135.md` (metricas) y en `C/conteos-canonicos-tecnicos.md` (tiempo de espera, D15).
- El grupo de `C/dictamen-correcciones.md` deja las notas de coordinacion: para c-130, sobre `CLAUDE.md` y `openspec/config.yaml` (10 s); para c-140, sobre la figura del capitulo 6 y la verificacion del tiempo de espera.
- No se modifican `Bibliography_base.bib`, `C/numeros-canonicos.md`, `evaluation/`, `data/`, codigo, `CLAUDE.md` ni `openspec/config.yaml`.

### D14 - Anexo H coherente con el capitulo 5 sobre los parametros de inferencia

Se reescribe la oracion de `S/12-anexos.tex:88` para que declare, como `S/05:74`, que los hiperparametros de `tab:anexo_gemini_params` son la configuracion adoptada para el despliegue y no el resultado de un procedimiento de optimizacion documentado, con remision a `subsec:capa-procesamiento` (y a la calibracion como trabajo futuro, si cabe en longitud neutra). En la fila de `candidate_count` (`:102`) se reemplaza "optimiza la latencia" por una formulacion del mecanismo (respuesta unica sin remuestreo que acota la latencia). La leyenda de la tabla puede incorporar "configuracion adoptada" si hace falta para la coherencia. Los valores (0,3; 0,9; 100; 1; parcialmente desactivados; `>=2.20.0`) y la columna "Justificacion" (fundamentos cualitativos de cada valor) se conservan; el tiempo de espera se trata en D15. Es una correccion de redaccion de longitud neutra; no introduce cifras.

**Alternativas:** documentar un procedimiento de optimizacion (descartada: no existe y seria fabricacion); eliminar la columna "Justificacion" (descartada: perderia contenido y el requisito "Reduccion sin perdida de contenido cientifico" lo impide).

### D15 - Tiempo de espera alineado con la configuracion vigente durante la campana

El tiempo de espera que declaran `S/05:74` y la fila `timeout` de `tab:anexo_gemini_params` (`S/12-anexos.tex:104`) pasa de 10 s a los valores de `settings.py` vigentes durante la campana automatizada: 30 s por intento (`gemini_timeout_seconds`, commit `11036be`, 2026-09-24) y 60 s de presupuesto total por clasificacion (`gemini_total_timeout_seconds`, commit `429f2c9`, 2026-09-29). Reglas:

- **Sin cifras ajenas a la evidencia:** toda cifra nueva sale de `settings.py` o de la historia git (`git log -S`); si para explicar "por intento" se menciona el numero de reintentos (`gemini_max_retries = 2`, mismo commit `429f2c9`), se toma de alli.
- **Semantica fiel al codigo:** antes de redactar la justificacion de la fila se verifica, en solo lectura, en `App/Backend/app/classifiers/` que ocurre al agotarse el presupuesto (etapa de reserva con confianza 0,0 y revision humana, segun la especificacion del Anexo H.3); si el codigo difiere, se describe lo que el codigo hace.
- **Dos niveles de reintento:** la redaccion aclara que son reintentos del backend al modelo, distintos de la invocacion de N8N al backend que `S/06:60` describe sin reintentos.
- **Valor vigente:** se consignan los valores por defecto de `settings.py`, porque ningun archivo versionado los sobreescribe (`docs/operational-guide.md:67` solo comenta el presupuesto total). Los `.env*` no se leen; si los autores declaran que el `.env` de la campana los sobreescribio, prevalece el valor declarado y se registra.
- **Procedencia:** se registra en `C/conteos-canonicos-tecnicos.md` y no en `C/numeros-canonicos.md`. El primero es la fuente unica de los hechos tecnicos citados en `05`, `06` y `12-anexos` (incluido el SDK de esas mismas lineas); el segundo fija resultados. Se agrega una linea "Upsert c-135" en su encabezado, filas `vigente` para 30 s y 60 s y una fila `retirado` para 10 s en la Seccion 2 (archivo:linea y commit), las filas ANTES -> DESPUES de `05:74` y `12-anexos:104` en la Seccion 3, y la evidencia en la Seccion 5.
- **Coordinacion:** `CLAUDE.md` y `openspec/config.yaml` (10 s) son de c-130, que los alinea con confirmacion del usuario; c-135 deja la nota en `C/dictamen-correcciones.md` (D13). Si c-140, que es opcional, se aplica despues, solo verifica la coherencia; si cambiara los valores en el codigo, la tesis seguiria reportando los vigentes durante la campana, y c-140 deberia agregar la fila correspondiente en el memo.
- **Longitud neutra:** en `S/05:74` se reemplaza "timeout = 10 s" por la expresion equivalente con los dos valores; en el Anexo H solo cambian la celda Valor y la justificacion de esa fila.

**Alternativas:** mantener 10 s con una nota de discrepancia (descartada: el experimento corrio con 30 s y 60 s); declarar solo los 30 s por intento (descartada: omite el presupuesto total que acota la latencia de la clasificacion); registrar la procedencia en `C/numeros-canonicos.md` (descartada: ese memo es de resultados y su alcance no incluye parametros tecnicos).

## Risks / Trade-offs

- [Fechas sin confirmar a tiempo] -> Las tareas de fechas (grupos 1 y 2 de `tasks.md`) quedan bloqueadas; los grupos 3 a 5 (B10 y B13) son independientes y pueden aplicarse antes; nunca se interpola una fecha.
- [Leer los commits como limites de iteracion] -> Regla D5 (i): los commits son anclas de actividad; los limites requieren fuente primaria o confirmacion.
- [La descripcion de la iteracion 5 contradice la evidencia (OQ-3)] -> Checkpoint MEDIUM: la cronologia no se publica mientras su item 5 afirme una condicion incompatible con sus fechas.
- [mmdc no instalado o sin Chromium] -> `npx` o el contenedor `minlag/mermaid-cli`; respaldo: tabla (D2).
- [Rotulos de mes en ingles o figura ilegible al ancho de pagina] -> `axisFormat` numerico, `-s 2`, etiquetas cortas y revision visual del PDF.
- [Holgura del capitulo 6 consumida por los changes previos, o por c-140 despues] -> Palancas de D12 y aviso a c-140; c-141 verifica el tope.
- [El parrafo de `S/07:6` se desincroniza si la estructura cambia despues] -> En el orden fijado, c-130, c-131 y c-134 aplican antes; el escenario del delta spec compara el conteo de `\subsection`; c-141 re-verifica.
- [c-139 aplica despues y necesita la tabla completada] -> D8: la tabla y el registro quedan completos al cerrar c-135, con las discrepancias anotadas para c-139.
- [Reescribir el Anexo H altera valores o suma lineas] -> D14: solo se cambian la oracion de `:88`, la leyenda si hace falta y la justificacion de `candidate_count`; el unico valor que cambia es el tiempo de espera (D15).
- [El `.env` de la campana sobreescribio los tiempos de espera] -> D15: valores por defecto de `settings.py` salvo declaracion de los autores, que prevalece y se registra.
- ["Por intento" se lee como contradiccion con `S/06:60`] -> D15: la redaccion distingue los reintentos del backend al modelo de la invocacion de N8N al backend.
- [c-130 no alinea `CLAUDE.md` y `openspec/config.yaml`] -> Nota de coordinacion en `C/dictamen-correcciones.md`; c-141 verifica la coherencia global.
- [Conflictos de edicion en parrafos compartidos] -> Mapa D11, rebase sobre el texto vigente y `git diff` por fragmento.
- [Fuentes de acceso cerrado (Paket, Colavito)] -> Residuo "no reportado en el alcance revisado" con motivo; OQ-5.
- [Una metrica extraida contradice `S/03:32` o `S/01:66` (c-139)] -> Se registra y se comunica a c-139; c-135 no edita esas frases.
- [El requisito MODIFIED de `tab:comparativa` presupone OQ-4 = (b)] -> Si el usuario elige (a), se actualiza el delta spec antes del apply.

## Migration Plan

1. Resolver con el usuario OQ-1 a OQ-5; OQ-1, OQ-2 y OQ-3 bloquean solo las tareas que dependen de ellas.
2. Medir la linea base: compilar (`latexmk` en el contenedor `texlive-thesis` del `Dockerfile` de `paper/`, o `xelatex -> biber -> xelatex -> xelatex` con MiKTeX como en c-80) y contar paginas (`pdftotext main.pdf - | tr -cd '\f' | wc -c` o `pdfinfo`).
3. Aplicar los bloques independientes de B10 y B13: `S/03` (D6, D7), `tab:trabajos-academicos` (D8), `S/07:6` (D9), `S/09:39` (D10), el Anexo H (D14) y el tiempo de espera con su procedencia (D15). Por el orden fijado, c-130 a c-134, c-138 y c-136 ya aplicaron.
4. Aplicar B9: evidencia (D5), `D/cronograma.md`, render de `F/cronograma.png`, 6.6, 4.2, 4.4, 4.5, 4.9, `S/08:46` y `S/01:76`.
5. Trazabilidad (D13).
6. Compilar y verificar: sin errores fatales, sin referencias indefinidas ni etiquetas duplicadas, paginas menores o iguales que la linea base, numeros canonicos intactos; `openspec validate c-135-cronologia-y-consistencia-redaccional --strict`.
7. Rollback: `git checkout <commit-previo> -- "docs/Tesis/v10 (IA)/paper/sections" docs/Tesis/Correcciones/dictamen-correcciones.md`, `git rm` de los archivos nuevos y recompilar.

## Open Questions

- **OQ-1 (bloquea las fechas de las iteraciones).** Fechas reales de inicio y fin de las seis iteraciones Scrumban. Fueron de dos semanas y contiguas? La historia del repositorio muestra actividad entre 2026-04-06 y 2026-10-22, con una pausa entre 2026-07-10 y 2026-09-10, lo que no es compatible con doce semanas contiguas que terminan en la validacion experimental. Fuente preferida: el tablero GitHub Projects (requiere que el usuario ejecute `gh auth refresh -s read:project`) o los registros de los autores. Recomendacion: declarar "seis iteraciones" con sus intervalos reales y conservar "dos semanas" solo como duracion nominal confirmada, aclarando que no fueron contiguas.
  - **RESUELTA PROVISIONALMENTE (2026-10-25): no hay fuente primaria (el token de `gh` no tiene el scope `read:project`; `gh project list --owner lucaGomezB` falla) ni confirmacion de los autores; se aplica la regla (iv) de D5: ninguna fecha por interpolacion. Las seis iteraciones NO se fechan individualmente: la construccion se representa con dos barras de precision de mes que cubren los periodos de actividad del repositorio (abril a julio y septiembre a octubre de 2026; pausa 2026-07-10 a 2026-09-10) y la leyenda declara que las iteraciones no se fechan por separado. Se retiran "de dos semanas cada una", "12 semanas" y los rotulos "(Semanas k--k+1)"; se conserva "seis iteraciones". Pendiente de confirmacion del autor: inicio y fin de cada iteracion y si fueron de dos semanas y contiguas.**
- **OQ-2 (bloquea las fechas de las campanas).** Se mantiene la ventana mensual confirmada el 2026-10-09 (manual jun-ago 2026; automatizada sep-oct 2026) o se fechan dias exactos? Se muestran como hitos las corridas documentadas (2026-10-02 correo y formulario; 2026-10-06 telefonia) y el recalculo telefonico (2026-10-19)? Hubo procesamiento automatizado del corpus en septiembre, antes de la migracion a `gemini-3.6-flash` del 2026-09-24? Si lo hubo, con que modelo (afecta la cuarta limitacion)? Cuando se generaron las predicciones evaluadas (`evaluation/predicciones.json`, no versionado)?
  - **RESUELTA PROVISIONALMENTE (2026-10-25): se mantiene la ventana mensual confirmada el 2026-10-09 (manual junio a agosto de 2026; automatizada septiembre a octubre de 2026), con precision de mes, mas los hitos documentados en el repositorio (integracion de `gemini-3.6-flash` 2026-09-24, corridas de correo y formulario 2026-10-02 y de telefonia 2026-10-06, recalculo telefonico 2026-10-19), cada uno con su comando en `docs/diagrams/cronograma.md`; pendiente de confirmacion del autor: si hubo procesamiento automatizado del corpus entre 2026-09-01 y 2026-09-23 (con `gemini-2.5-flash`) y cuando se generaron las predicciones evaluadas.**
- **OQ-3 (checkpoint MEDIUM).** `S/06:75` afirma que los ajustes del clasificador se hicieron "sin exposicion al corpus de validacion de 200 casos", pero c-71 (2026-10-05) y c-74 (2026-10-07) midieron sobre el corpus, con calibracion out-of-fold, despues de la corrida de correo y formulario; la configuracion evaluada (131 casos resueltos por la etapa deterministica) coincide con la politica de cortocircuito medida en c-74. Que change reconcilia la frase? Recomendacion: c-135 la ajusta en el mismo item que fecha, con redaccion factual confirmada por los autores (ajuste del prompt sin exposicion; seleccion del cortocircuito deterministico con calibracion out-of-fold sobre el corpus, fechada); alternativas: c-139 o un change nuevo. El Anexo H.4 (prompt) no queda contradicho por esta evidencia y no se toca.
  - **RESUELTA PROVISIONALMENTE (2026-10-25): la oracion del item 5 ya fue reescrita por c-144 y verificada por c-130; el item no afirma "sin exposicion al corpus" (`grep -c "sin exposici"` = 0) y no declara fechas, de modo que es compatible con el cronograma; c-135 no la modifica. Redaccion final PROVISIONAL; pendiente de confirmacion del autor (nota: c-71 y c-74 midieron sobre el corpus el 2026-10-05 y 2026-10-07, despues de la corrida de correo y formulario del 2026-10-02 y en paralelo a la telefonica; el orden 5 -> 6 de la lista no implica fechas).**
- **OQ-4.** Telefonia en `tab:comparativa`: se confirma la opcion (b) recomendada (retirarla de la afirmacion comparativa) o se prefiere (a) (agregar una columna verificada)?
  - **RESUELTA PROVISIONALMENTE (2026-10-25): opcion (b); la telefonia sale de la afirmacion comparativa y queda en `03:84` como rasgo de la propuesta; `tab:comparativa` conserva sus cuatro columnas; pendiente de confirmacion del autor.**
- **OQ-5.** Los autores tienen acceso institucional (por ejemplo, la Biblioteca Electronica de Ciencia y Tecnologia via UTN) al texto completo de Paket et al. (2024) y Colavito et al. (2025)? Si no lo tienen, esas celdas conservan "no reportado en el alcance revisado" con el motivo.
  - **RESUELTA PROVISIONALMENTE (2026-10-25): sin acceso institucional desde la maquina de apply ni confirmacion de los autores; Paket 2024 y Colavito 2025 (acceso cerrado) quedan como "no reportado en el alcance revisado" con el motivo; el texto completo de Zangari 2023 (acceso abierto) no fue recuperable por controles anti-bot (no evadidos), asi que solo su idioma queda sin dato; pendiente de confirmacion del autor.**

## Desvios del apply (2026-10-25)

- **Ubicacion de la figura (D3/D12):** la figura `fig:cronograma` se reproduce en el Anexo A (`12-anexos.tex`, junto a los demas diagramas Mermaid de `docs/diagrams/`), no en `subsec:conexion-scrumban`: el capitulo 6 no tenia holgura (su ultima pagina estaba llena tras c-130..c-136; la figura abria una pagina nueva, total 109 y 110 en las pruebas) y el Anexo A lo absorbio con delta 0 (total 108). `06-implementacion.tex` la referencia con `\autoref{fig:cronograma}` (Anexo~A); `04` y `08` tambien.
- **Render:** `@mermaid-js/mermaid-cli@11` (mmdc 11.17.0) con `-w 760` y `fontSize` 13, mas recorte de margenes blancos con Pillow; el `.mmd` temporal quedo fuera del repositorio.
- **Tabla de trabajos academicos:** se ensancho la columna de metrica y se acortaron las celdas y la linea de fuente (palanca de forma) para no abrir una pagina en el capitulo 3.
