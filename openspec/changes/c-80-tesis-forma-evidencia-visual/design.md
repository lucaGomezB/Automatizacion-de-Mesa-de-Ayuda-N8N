# Design: c-80 — Forma y evidencia visual

## Context

Ver `proposal.md` — Why. Estado relevante verificado contra el arbol de trabajo v9
(2026-10-12). Convencion de rutas: `S = docs/Tesis/v9 (IA)/paper/sections`,
`F = docs/Tesis/v9 (IA)/paper/figures`, `D = docs/diagrams`.

Hechos verificados que condicionan el diseno:

- **Ortografia (F1)**: 52 ocurrencias de 4 formas; 50 son errores. `diseñó`=21,
  `desarrolló`=11 (2 verbos legitimos: `S/00-resumen.tex:11` "el estudio se
  desarrolló" y `S/06-implementacion.tex:87` "el frontend se desarrolló"),
  `completó`=13, `aquéllos`=7. La portada `S/00-portada.tex` carece de tildes en
  la linea 8 ("TECNOLOGICA"), 11 ("Programacion"), 13 ("Automatizacion"), 19
  ("Tecnico"/"Programacion") y 27 ("Republica"). Los titulos de seccion tambien
  carecen de tildes (`\section{Introduccion}`, `\section{Conclusiones}`, etc.).
- **Figuras (F2)**: existe **una sola** figura, `S/05-arquitectura.tex:31-36`
  (`\includegraphics{arquitectura_sistema}`). `F/` solo contiene ese PNG y el
  `.gitkeep`; `tables/` esta vacio. El preambulo (`preambles/preamble.tex:68-69`)
  carga `graphicx` con `\graphicspath{{./figures/}}`; NO hay `tikz`, `mermaid` ni
  `svg` cargados. Existen 3 fuentes Mermaid sin embeber: `D/despliegue.md`,
  `D/secuencia.md`, `D/componentes.md`.
- **Anexos (F3)**: `S/12-anexos.tex` tiene 7 `\section` (A-G) descriptivos, sin
  un solo `\includegraphics`, `table`, `lstlisting` o `verbatim`. Fuentes de
  contenido disponibles: `docs/anexo_c_esquema_bd.md`, `docs/openapi.json`
  (115 KB), `n8n/workflow.json` (29 nodos), `data/corpus_evaluacion_pseudonimizado.json`,
  `docs/operational-guide.md`. El Anexo H (`docs/anexo_h_prompt_gemini.md`,
  H.1-H.7) tiene **cero** referencias en los `.tex`.
- **Tablas (F4)**: 9 tablas. Con `\small`: `tab:comparativa` (`03:40`),
  `tab:variables` (`04:26`), `tab:entidades` (`05:70`), `tab:errores` (`07:96`).
  Sin `\small`: `tab:capas` (`05:12`), `tab:api` (`05:92`), `tab:tiempos`
  (`07:12`), `tab:matriz` (`07:42`), `tab:metricas` (`07:61`). La Tabla 1
  (`03:36`) usa `p{}` planas; la Tabla 3 (`05:12`, `tab:capas`) tiene su primera
  columna sin `raggedright`.
- **Duplicaciones (F5)**: 1.1/2.1 (`01:8,10` vs `02:10,12`, Galup2009 casi
  verbatim); 5.3/6.3 (`05:44` vs `06:39,41`, mas "camino de clasificacion unico"
  en `05:60` y `06:44`); 8.1/9.1 (`08:8,10,14` vs `09:12,24`).
- **N8N 1.62 (F6)**: `S/05-arquitectura.tex:21` y `S/06-implementacion.tex:10`
  citan "la version 1.62 no se encuentra disponible en Docker Hub"; contradicen
  `S/12-anexos.tex:37` y `D/despliegue.md` ("N8N 2.11.2").
- **Valorativas (F7)**: `S/08-discusion.tex:8-16` y `S/09-conclusiones.tex:6-18`.
  Evidencia disponible para rebajar (cifras corregidas por c-76 en
  `07-resultados.tex` / `evaluation/report.md`): reduccion de tiempo 75,9~%
  (cota conservadora >= 71,3~%, `07:10`), Wilcoxon \(W=335\),
  \(p=2{,}05\cdot10^{-32}\), \(r=0{,}983\), exactitud 73,5~% (147/200, `07:40`),
  macro-F1 0,5207 (`07:59`), `07:86` (intervencion 9,5~%).

Restriccion dura: la tesis se compila en Overleaf (sin toolchain LaTeX local). No
se toca `App/**`. Existen `.bak` de cada seccion; el barrido y los conteos se
hacen sobre los `.tex` activos (los `.bak` son respaldos obsoletos y no se editan
ni cuentan).

### Correccion de trazabilidad (2026-10-19)

Las cifras de evaluacion de este change provenian del corpus sintetico de 3
clases descartado en C-27. Se corrigen a los valores reales del corpus de 200
casos, cuya fuente de verdad es `evaluation/report.md` y
`data/corpus_evaluacion_pseudonimizado.json`, consolidados por c-76 en el
Capitulo 7. Motivo: c-80 se autorio antes de reconciliar el corpus; conservar los
numeros sinteticos habria dejado la figura de matriz de confusion y las
afirmaciones de 8.1/9.1 inconsistentes con el Capitulo 7 corregido. Regla: toda
cifra de evaluacion citada en este change MUST coincidir con `evaluation/report.md`
(via c-76); no se inventan valores y no se hardcodean celdas de la matriz.

## Goals / Non-Goals

**Goals:**

- Corregir las 50 apariciones ortograficas erroneas de forma contextual y las
  tildes de portada y titulos.
- Producir e incrustar las 8 figuras requeridas con fuente reproducible.
- Convertir los 7 anexos descriptivos en anexos con contenido real e incorporar
  el Anexo H.
- Unificar la composicion de las 9 tablas.
- Deduplicar los tres pares de parrafos repetidos.
- Retirar la acotacion obsoleta de N8N 1.62 y reconciliar la version.
- Rebajar las afirmaciones valorativas de 8.1 y 9.1 a formulaciones respaldadas.

**Non-Goals:**

- No tocar `App/**`, ni la logica del clasificador, ni los numeros del corpus.
- No modificar la estadistica (c-77) ni la bibliografia/atribucion (c-78).
- No reemplazar `.bak` ni tocar `CHANGES.md` /
  `docs/Tesis/Correcciones/dictamen-correcciones.md`.
- No recompilar localmente (Overleaf).
- No migrar el formato de figuras a TikZ nativo ni cambiar el preambulo salvo
  necesidad de renderizado.

## Decisions

### D-F1 — Correccion ortografica contextual (no sustitucion ciega)

**Decision:** sustituir por contexto, no con un `sed` global. Reglas:

- `diseñó` -> `diseño` (21 casos; todos son usos sustantivos: "el diseñó").
- `completó` -> `completo` (13; todos adjetivales: "volumen completó", "mes
  completó", "esquema completó").
- `aquéllos` -> `aquellos` (7; la RAE no admite la tilde diacritica actual).
- `desarrolló` -> `desarrollo` **excepto** los 2 verbos: `S/00-resumen.tex:11`
  ("el estudio se desarrolló") y `S/06-implementacion.tex:87` ("el frontend se
  desarrolló"). Los sustantivos a cambiar incluyen `S/00-resumen.tex:9`
  ("el diseñó, desarrolló, implementación..."), `S/04-marco-metodologico.tex:8,87,98`,
  `S/06-implementacion.tex:8`, `S/08-discusion.tex:16` y `S/12-anexos.tex:25,27,47`.
- Portada `S/00-portada.tex`: agregar tildes en lineas 8, 11, 13, 19, 27
  ("TECNOLOGICA" -> "TECNOLOGICA" con tilde, etc.).
- Titulos de seccion: normalizar tildes de titulos (`Introduccion` ->
  `Introducción`, `Conclusiones` ya tiene, `Discusion`, `Implementacion`,
  `Marco metodologico`, etc.). Se audita cada `\section`/`\subsection` de los
  `.tex`.

**Alternativa:** `sed`/`perl -pi` global — descartado: sustituiria los 2 verbos
legitimos y podria afectar palabras con la misma raiz ("diseño grafico"). El apply
MUST revisar cada reemplazo con `rg -n` antes de confirmarlo.

**Verificacion:** `rg` de control (ver tasks) sin residuos de las 4 formas;
listado explicito de los 2 verbos preservados.

### D-F2 — Produccion e incrustacion de las 8 figuras

El punto duro del change. El preambulo solo carga `graphicx` con `graphicspath
./figures/`; las figuras son archivos raster/vectoriales referenciados por nombre
base. Se generan **fuera** del arbol LaTeX (en `docs/` o `scripts/figures/`) y se
versionan los artefactos finales en `F/`.

**Herramienta Mermaid -> imagen (OQ-F2-1 resuelta 2026-10-12):**
`@mermaid-js/mermaid-cli` (`mmdc`) via `npx -p @mermaid-js/mermaid-cli mmdc`.
Node.js v22.23.2 esta disponible en la maquina del autor (nvm); `mmdc` no requiere
instalacion global (se invoca via `npx`). Requiere Chromium (puppeteer lo descarga
en la primera ejecucion). Comando tipico:
`mmdc -i D/despliegue.md -o F/despliegue.png -b white -s 2` (`-s 2` escala 2x para
nitidez). Si Chromium no se puede obtener sin conexion, fallback manual exportando
PNG desde mermaid.live o incrustando el bloque `mermaid` como `lstlisting` (peor
calidad, solo ultimo recurso). **No** se usa el servicio mermaid.ink en linea
(rompe reproducibilidad/offline).

**Decodificacion de `use` de Mermaid (`\[\n`):** los `.md` traen `\n` literales
para saltos de linea; se conservan (Mermaid los interpreta) o se limpian en la
fuente antes de renderizar. El apply MUST verificar que el diagrama no sale con
`\n` visibles.

Distribucion de las 8 figuras (detalle en **Anexo A**):

| # | Figura | Destino | Fuente | Metodo |
|---|--------|---------|--------|--------|
| 1 | Despliegue | cap5 / Anexo A | `D/despliegue.md` (Mermaid existente) | `mmdc` -> `F/despliegue.png` |
| 2 | Secuencia | cap5 / Anexo A | `D/secuencia.md` (Mermaid existente) | `mmdc` -> `F/secuencia.png` |
| 3 | ER modelo de datos | 5.6 / Anexo C | **nuevo** `D/er_modelo_datos.md` (Mermaid `erDiagram`, derivado de `docs/anexo_c_esquema_bd.md`) | `mmdc` -> `F/er_modelo_datos.png` |
| 4 | Flujo N8N | 6.3 / Anexo E | `n8n/workflow.json` (29 nodos) | captura manual desde la UI N8N (`:5678`) -> `F/flujo_n8n.png` |
| 5 | Panel admin | 6.8 | `App/Frontend` (panel de administracion) | captura manual -> `F/panel_admin.png` |
| 6 | Dashboard | 6.8 | `App/Frontend` (dashboard ReCharts) | captura manual -> `F/dashboard.png` |
| 7 | Boxplot de latencias POR CANAL | 7.1 | `data/corpus_evaluacion_pseudonimizado.json` (`tiempo_manual_s`, `tiempo_automatizado_s`, 200 casos) segmentado por canal | script `scripts/figures/boxplot_tiempos.py` (matplotlib) -> `F/boxplot_tiempos.pdf` (3 paneles / layout agrupado: web, correo, telefonia) |
| 8 | Matriz de confusion | 7.2 | `evaluation/report.md` (matriz 5x5 real, owned by c-76) | script `scripts/figures/matriz_confusion.py` (matplotlib) -> `F/matriz_confusion.pdf` |

**Decisiones de formato:** para las figuras de datos (7 y 8) se emite **PDF
vectorial** (mejor nitidez en el PDF final); para diagramas y capturas, **PNG** a
2x. Ambas extensiones resuelven con `\includegraphics{nombre}` gracias a
`graphicspath`.

**Figura 7 — reporte POR CANAL (regla dura):** `docs/medicion-latencia-e2e.md:50-53`
exige reportar el analisis de latencias POR CANAL porque los puntos de ingreso no
son homogeneos y mezclarlos rompe la comparabilidad. Por eso la figura 7 NO es un
boxplot unico agrupado, sino un boxplot por canal: 3 paneles o layout agrupado
(`formulario web`, `correo`, `telefonia`). Cada panel compara manual vs
automatizado dentro del mismo canal. El script MUST segmentar por canal y emitir
los tres paneles; nunca un boxplot que mezcle los tres ingresos.

**Figura 7 — dependencia de la metrica de telefonia (c-77):** el panel de
telefonia usa la metrica CORREGIDA de `tiempo_automatizado_s`, que incluye la
duracion de la llamada/grabacion; esa correccion se agrega en c-77 como "Opcion A"
y c-80 se aplica DESPUES de c-77. Si c-77 no esta aplicado, el panel de telefonia
MUST anotarse como "automatizado = solo post-procesamiento de la llamada (cota
inferior)". Se prefiere depender de la metrica corregida.

**Figura 7 — verificacion contra cifras corregidas (c-76):** la verificacion de
`n` y medianas ("coherentes con `07:10`") MUST hacerse contra las cifras CORREGIDAS
de `S/07-resultados.tex` (owned by c-76), NO contra los numeros obsoletos actuales.

**Ubicacion LaTeX:** cada figura se incrusta en un `figure[htbp]` con `\centering`,
`\includegraphics[width=...]`, `\caption` y `\label`. Las figuras de diagramas de
cap5 y del Anexo A pueden compartir la misma imagen; se documenta la convencion en
el texto ("la version completa en notacion UML se incluye en el Anexo A", como ya
hace `S/05-arquitectura.tex:34`).

**Alternativa:** incrustar las fuentes Mermaid como bloques `lstlisting` — se
descarta como solucion principal (la consigna pide figuras reales); se admite solo
como contingencia si Chromium no se puede obtener sin conexion y no se consigue el
PNG (ver OQ-F2-1).

**Riesgo de datos (resuelto, OQ-F2-2):** el `metadata` del corpus dice "tiempos
automatizados pendientes de medicion end-to-end", pero esa nota es obsoleta y su
correccion pertenece a c-77 (item D1), NO a este change. `tiempo_automatizado_s`
contiene mediciones end-to-end reales (ver OQ-F2-2); NO se requiere remedicion y
el boxplot usa directamente esos valores. El apply MUST NOT editar el `metadata`
del corpus.

### D-F3 — Anexos con contenido real

**Decision:** cada `\section` de `S/12-anexos.tex` pasa de prosa descriptiva a
prosa introductoria + artefacto embebido:

- **Anexo A** (diagrama de arquitectura): embeber Anexo~`\ref{fig:...}` de las
  figuras 1 y 2 (despliegue y secuencia) y, opcionalmente, la de componentes
  (`D/componentes.md` -> `F/componentes.png`). Reemplaza la descripcion de "los
  diagramas se mantienen en .drawio" (falso: son Mermaid; corregir la nota).
- **Anexo B** (repositorio): agregar un `lstlisting`/`verbatim` con el arbol de
  directorios (o la salida de `tree`), y la tabla de tags/releases.
- **Anexo C** (esquema BD): embeber la figura 3 (ER) y/o una tabla con las siete
  entidades y sus atributos derivada de `docs/anexo_c_esquema_bd.md`.
- **Anexo D** (OpenAPI, OQ-F3-1 resuelta 2026-10-12): incluir una tabla de las 33
  rutas agrupadas por recurso (de `docs/openapi.json`: 33 rutas / 41 metodos / 44
  esquemas, 115 KB) MAS 1 esquema representativo (p. ej. `IncidenteRead`); NO pegar
  los 115 KB completos.
- **Anexo E** (flujo N8N): embeber la figura 4 (captura) y una tabla con los 29
  nodos agrupados por etapa (Recepción, Normalización, Clasificación y
  persistencia, Evaluación, Notificación).
- **Anexo F** (corpus): embeber la tabla del libro de campos (derivada de
  `docs/anexo_f_corpus.md`) o un extracto JSON de ejemplo; declarar el total (200).
- **Anexo G** (documentacion operativa): incluir la tabla de contenidos o un
  extracto del runbook (`docs/operational-guide.md`).
- **Anexo H** (NUEVO): incorporar `docs/anexo_h_prompt_gemini.md` (H.1-H.7) como
  `\section{Especificacion del prompt de Gemini 2.5 Flash}` con su contenido
  (estructura del prompt, categorias, formato de respuesta, parametros). Se
  referencia desde el texto principal (por ejemplo desde 05.5 o el Anexo E).

**Nota (Correccion de trazabilidad 2026-10-19):** verificado contra
`App/Backend/app/models/` (clases mapeadas reales) y la Tabla~4 de la tesis
(`05-arquitectura.tex`, `tab:entidades`), el modelo de datos comprende SIETE
entidades principales: `incidente`, `sector`, `estado`, `canal_origen`,
`clasificacion_log`, `users` y `directorio_empleado`. El numero 7 es correcto y
se conserva; el ER diagrama del Anexo~C y su tabla MUST listar esas siete
entidades (no seis). El modelo ejecutable tiene ademas tablas auxiliares y de
auditoria posteriores (por ejemplo `incidente_evento`, `telefonia_ingreso`),
fuera del alcance de la Tabla~4. La categoria retirada "Operaciones" pertenece a
c-76 y NO se resuelve aqui. El change solo convierte la composicion de los
anexos.

### D-F4 — Composicion uniforme de tablas

**Decision:** unificar con estas reglas:

1. **Fuente:** todas las tablas usan `\small` (convencion mayoritaria del
   preambulo de tablas con prosa). Se agrega `\small` a `tab:capas` (`05:12`),
   `tab:api` (`05:92`), `tab:tiempos` (`07:12`), `tab:matriz` (`07:42`) y
   `tab:metricas` (`07:61`).
2. **Columnas de prosa:** toda columna con oraciones usa
   `>{\raggedright\arraybackslash}p{...}`. Se corrige la primera columna de
   `tab:capas` (`05:16`) y las columnas `p{}` planas de `tab:comparativa`
   (`03:40`) y de `tab:tiempos`/`tab:matriz`/`tab:metricas` cuando contienen
   texto.
3. Las columnas puramente numericas (`tab:matriz`, `tab:metricas`) mantienen
   `p{}` centrado si su contenido es corto, pero el encabezado y las etiquetas de
   fila usan ragged-right cuando son texto.

**Alternativa:** definir un `\newcolumntype` en el preambulo y aplicarlo en todas
las tablas — mas limpio pero mas invasivo (toca `preambles/preamble.tex`, fuera del
arbol de secciones y compartido con c-76/c-77). Se descarta para minimizar el
radio de colision entre changes; se documenta como mejora futura.

**Verificacion:** `rg` de `\small` (debe aparecer en las 9 tablas, conteo
`\begin{table}` = `\small` = 9) y revision visual del PDF en Overleaf.

### D-F5 — Deduplicacion de parrafos

**Decision:** eliminar la repeticion conservando el capitulo "dueno" del material
y dejando remision cruzada:

- **Par 1.1/2.1:** el marco teorico (cap2) es el dueno de la definicion de ITSM
  (Galup2009). La introduccion (1.1) MUST reducir su parrafo a una contextualizacion
  breve con remision ("como se describe en el Capitulo 2"). Se elimina la cita
  duplicada de Galup2009 en 1.1 y las frases espejo ("alinear la operacion
  tecnologica con los objetivos del negocio").
- **Par 5.3/6.3:** la implementacion (6.3) es la duena del flujo N8N; el cap5
  (arquitectura) MUST describir la capa de orquestacion de forma conceptual y
  remitir a 6.3 para los detalles operativos. La frase "camino de clasificacion
  unico para los tres canales" se conserva **una sola vez** en 5.3 (arquitectura
  es el lugar conceptual) o en 6.3; se elige 5.3 y 6.3 remite.
- **Par 8.1/9.1:** la discusion (cap8) interpreta; las conclusiones (cap9)
  sintetizan. Se reescriben las formulaciones espejo de 9.1 para que sinteticen sin
  repetir frases de 8.1 (se articula con D-F7).

**Verificacion:** comparacion manual de los pares + `rg` de frases clave
("alinear la operacion tecnologica", "camino de clasificacion").

### D-F6 — Version de N8N

**Decision:** retirar en `S/05-arquitectura.tex:21` y `S/06-implementacion.tex:10`
el parentetico "version estable mas reciente; la version 1.62 no se encuentra
disponible en Docker Hub al momento del despliegue" y citar `N8N~2.11.2` de forma
consistente con `S/12-anexos.tex:37` y `D/despliegue.md`. En 5.21 la celda de la
tabla queda "Motor N8N 2.11.2 desplegado en contenedor Docker autoalojado". En
6.10 la lista queda "N8N~2.11.2".

**Nota:** `D/despliegue.md` menciona Redis~7.2, que ya no forma parte del stack
(ver `AGENTS.md`, "sin Redis desde c-62"). El diagrama de despliegue se actualiza
al producir la figura 1: retirar Redis o marcarlo como retirado, para no embeder
una figura obsoleta. El apply MUST reconciliar el diagrama con el stack vigente.

### D-F7 — Rebaja de afirmaciones valorativas

**Decision:** clasificar cada expresion en (a) retirar, (b) rebajar a descripcion
de la evidencia, (c) conservar si esta respaldada.

- `08:8` "superan ampliamente los umbrales" -> "superan los umbrales (reduccion
  de tiempo 75,9~% —cota conservadora >= 71,3~%— y exactitud 73,5~%, cifras
  corregidas por c-76 en `07-resultados.tex` / `evaluation/report.md`)".
- `08:10` "valida la hipotesis subsidiaria" -> "es consistente con la hipotesis
  subsidiaria" (la hipotesis no se "valida", se obtiene evidencia a favor).
- `08:12` "consecuencia deseable" -> "consecuencia observada de la automatizacion".
- `08:14` "materializa el esquema human in the loop buscado" -> "es consistente
  con el esquema human in the loop" (9,5~% de intervencion, `07:86`).
- `08:16` "garantia metodologica que no todos los trabajos del area documentan..."
  -> describir la practica propia (aislamiento del corpus) sin comparar con
  terceros no medidos.
- `09:6` "cumplido satisfactoriamente" -> "el trabajo alcanzo el objetivo general".
- `09:12` "supero con holgura" -> "supero los umbrales establecidos (exactitud
  73,5~% y macro-F1 0,5207 frente a las cotas fijadas, cifras corregidas por
  c-76)".
- `09:16` "no deja espacio para la duda razonable", "resultado poco frecuente",
  "trasciende lo meramente estadistico" -> reformular en terminos de la prueba
  (Wilcoxon \(W=335\), \(p=2{,}05\cdot10^{-32}\), \(r=0{,}983\), cifras
  corregidas por c-76) sin los giros valorativos.
- `09:18` "activo que excede el cumplimiento del quinto objetivo" -> "los
  artefactos documentados cubren el quinto objetivo".

**Alternativa:** conservar las expresiones como estilo retorico — descartado: la
consigna exige respaldo evidenciario.

### D-ORDER — Orden de aplicacion (dependencia de secuencia)

Este change comparte archivos con tres changes en vuelo. Se declara la
dependencia de orden:

- **c-76** reescribe numeros en 08/09, la ventana temporal en 11 y las cifras de
  `07-resultados.tex`. La verificacion "n y medianas coherentes con `07:10`" de la
  figura 7 MUST hacerse contra las cifras CORREGIDAS de c-76, no contra las obsoletas.
- **c-77** toca la estadistica (07 y afirmaciones estadisticas) y agrega como
  "Opcion A" la correccion de `tiempo_automatizado_s` de telefonia (incluye la
  duracion de la llamada/grabacion). El panel de telefonia de la figura 7 depende
  de esa metrica corregida; sin c-77, ese panel se anota como cota inferior.
- **c-78** toca 03/08 y la bibliografia/atribucion.

**Regla:** c-80 MUST aplicarse **despues** de c-76, c-77 y c-78. Motivo: F5
(deduplicacion) y F7 (rebaja de afirmaciones) reescriben parrafos de
`08-discusion.tex` y `09-conclusiones.tex` que c-76/c-77/c-78 tambien editan;
aplicar antes pisaria sus correcciones de numeros/atribucion. Si se aplica en
otro orden, el merge se resuelve manualmente respetando la ultima version de los
numeros.

## Risks / Trade-offs

- Editar `.tex` sin compilador local -> mitigar con `rg` de control +
  `openspec validate` + revision visual en Overleaf.
- Las capturas manuales (figuras 4, 5, 6) dependen de levantar el stack local
  (`docker compose up -d`) y de que la UI este operativa -> mitigar documentando
  el procedimiento; si el stack no se puede levantar, sustituir por un diagrama
  esquematico de los nodos extraido de `n8n/workflow.json` y rotularlo como tal.
- `mmdc` se ejecuta via `npx` sobre Node.js v22.23.2 (nvm); el riesgo residual es
  que Chromium no se pueda descargar sin conexion -> mitigar con el fallback
  documentado (mermaid.live manual o `lstlisting`); validar el PNG antes de
  incrustar.
- El `metadata` del corpus declara tiempos automatizados "pendientes" (nota
  obsoleta; su correccion es de c-77 item D1) -> los valores son mediciones
  end-to-end reales (OQ-F2-2); el boxplot los usa directamente y este change NO
  edita el `metadata`.
- Figura 7 por canal depende de la numeracion CORREGIDA de `07-resultados.tex`
  (c-76) y, para telefonia, de la metrica corregida de `tiempo_automatizado_s`
  (c-77 "Opcion A") -> mitigado por D-ORDER (c-80 se aplica despues de c-76/c-77).
- Colision de edicion con c-76/c-77/c-78 -> mitigado por D-ORDER.
- `D/despliegue.md` puede estar desactualizado (Redis, conteo de nodos) -> el
  apply reconcilia el diagrama con el stack vigente antes de renderizar.
- Reescribir parrafos (F5/F7) podria alterar sin querer numeros o citas -> el
  apply MUST conservar cifras y citas exactas; no introduce referencias nuevas
  (eso es c-78).

## Migration Plan

1. **F1**: corregir ortografia contextual y portada/titulos (sin tocar los 2
   verbos). Verificar con `rg`.
2. **F6**: retirar la nota de N8N 1.62 y citar 2.11.2 en 5 y 6.
3. **F4**: unificar `\small` y `raggedright` en las 9 tablas.
4. **F5**: deduplicar los tres pares.
5. **F7**: rebajar las afirmaciones valorativas de 8.1 y 9.1.
6. **F2**: crear `D/er_modelo_datos.md`; renderizar figuras 1, 2, 3 con `mmdc`;
   capturar figuras 4, 5, 6; generar figuras 7, 8 con los scripts; versionar en
   `F/` e incrustar con `\includegraphics`.
7. **F3**: reescribir `S/12-anexos.tex` embebiendo los artefactos e incorporar el
   Anexo H.
8. Verificar (`rg` de control) y recompilar en Overleaf; revisar que las figuras
   rendericen y que el PDF no tenga errores fatales.
9. Rollback: `git checkout --` sobre los `.tex` afectados y remover las figuras
   nuevas de `F/`.

## Open Questions

- OQ-F2-1 (RESUELTA 2026-10-12): Node.js v22.23.2 esta disponible en la maquina
  del autor (nvm); `mmdc` no esta instalado pero se resuelve via
  `npx -p @mermaid-js/mermaid-cli mmdc`; puppeteer descarga Chromium en la primera
  ejecucion. La exportacion manual de PNG queda SOLO como contingencia si Chromium
  no se puede obtener sin conexion. No cambia specs ni el desglose de tareas.
- OQ-F2-2 (RESUELTA 2026-10-12): `tiempo_automatizado_s` es una medicion
  end-to-end REAL derivada de timestamps de la base (`t_e2e_s`), NO un valor
  cargado a mano. Verificado contra el backup de la base: los 119 casos de
  web+correo recomputados coinciden (diferencia maxima 0,00099 s) y los 81 de
  telefonia coinciden con su sidecar. Los 26 valores sub-1 s son GENUINOS y
  pertenecen TODOS al canal `formulario web` (webhook sincronico, sin espera IMAP
  ni STT); web min 0,525 s, mediana 1,26 s. Correo (min 8,97 s) y telefonia
  (min 8,33 s) no tienen ninguno. Conclusion: los valores del corpus son validos
  y NO se requiere remedicion. La correccion del `metadata` descriptivo del
  corpus pertenece a c-77 (item D1), NO a este change. Sin cambio del contrato de
  la spec.
- OQ-F3-1 (RESUELTA 2026-10-12): opcion elegida = Opcion 2 (extracto
  representativo). El Anexo D MUST incluir una tabla de las 33 rutas agrupadas por
  recurso (de `docs/openapi.json`: 33 rutas / 41 metodos / 44 esquemas, 115 KB) MAS
  1 esquema representativo (p. ej. `IncidenteRead`); MUST NOT pegar los 115 KB
  completos. Sin impacto en las specs.

---

## Anexo A — Especificacion de produccion de las 8 figuras

> Todas las salidas se versionan en `F/`. El preambulo resuelve por nombre base
> (sin ruta ni extension) via `\graphicspath{{./figures/}}`.

**1. `despliegue.png` — Diagrama de despliegue.**
Fuente: `D/despliegue.md` (bloque `mermaid` `graph TD`). Accion: actualizar el
diagrama (retirar Redis, confirmar N8N 2.11.2 y el conteo de componentes) y
renderizar con `mmdc -i ... -o F/despliegue.png -b white -s 2`. Destino:
`S/05-arquitectura.tex` (5.1, junto a `fig:arquitectura`) y/o Anexo A.

**2. `secuencia.png` — Diagrama de secuencia.**
Fuente: `D/secuencia.md` (bloque `mermaid` `sequenceDiagram`). Accion:
`mmdc -i ... -o F/secuencia.png -b white -s 2` (los diagramas de secuencia son
anchos; usar `-w 1600` si hace falta). Destino: 5.3 y/o Anexo A.

**3. `er_modelo_datos.png` — Diagrama entidad-relacion.**
Fuente NUEVA: crear `D/er_modelo_datos.md` con un `erDiagram` Mermaid de las 7
entidades (`incidente`, `sector`, `estado`, `canal_origen`, `clasificacion_log`,
`users`, `directorio_empleado`) y sus relaciones, derivado de
`docs/anexo_c_esquema_bd.md`. Render `mmdc` -> `F/er_modelo_datos.png`. Destino:
5.6 (Modelo de datos) y/o Anexo C.

**4. `flujo_n8n.png` — Captura del flujo N8N.**
Fuente: instancia N8N local (`:5678`) con `n8n/workflow.json` importado (29 nodos).
Accion: captura manual del editor de nodos, recortada, exportada PNG a `F/`.
Destino: 6.3 y/o Anexo E. Contingencia: si el stack no se levanta, diagrama
esquematico de los 29 nodos agrupados por etapa, rotulado como reconstruccion.

**5. `panel_admin.png` — Captura del panel de administracion.**
Fuente: `App/Frontend` (vista de administracion: listado de tickets, cola de
revision humana) corriendo en local. Accion: captura manual -> `F/`. Destino: 6.8.

**6. `dashboard.png` — Captura del dashboard.**
Fuente: `App/Frontend` (dashboard ReCharts) con datos de ejemplo o reales.
Accion: captura manual -> `F/`. Destino: 6.8.

**7. `boxplot_tiempos.pdf` — Boxplot de latencias manual vs automatico, POR CANAL.**
Fuente: `data/corpus_evaluacion_pseudonimizado.json` (200 casos, campos
`tiempo_manual_s` y `tiempo_automatizado_s`). Accion: script nuevo
`scripts/figures/boxplot_tiempos.py` (matplotlib, sin Seaborn) que lee el JSON,
SEGMENTA por canal (`formulario web`, `correo`, `telefonia`) y emite un boxplot con
3 paneles / layout agrupado a PDF vectorial en `F/`. Destino: 7.1. El panel de
telefonia depende de la metrica corregida de c-77 (ver D-F2); si c-77 no esta
aplicado, anotar "automatizado = solo post-procesamiento (cota inferior)".
Verificacion: el script MUST reportar `n` y medianas POR CANAL; deben ser
coherentes con las cifras CORREGIDAS de `07:10` (owned by c-76), NO con las cifras
obsoletas actuales.

**8. `matriz_confusion.pdf` — Matriz de confusion (5x5 real).**
Fuente: matriz 5x5 real derivada de `evaluation/report.md` (owned by c-76), en el
orden canonico de sectores (`Seguridad Informatica`, `Soporte Tecnico Hardware`,
`Soporte Tecnico Software`, `Bases de Datos`, `Sistemas`). Matriz de referencia
(MUST NOT hardcodearse en el script): `[[15,2,11,2,1],[1,77,3,0,4],[0,11,48,1,7],
[0,0,1,0,0],[2,0,5,2,7]]`. Accion: script nuevo
`scripts/figures/matriz_confusion.py` (matplotlib `imshow`) que lee la matriz de
`evaluation/report.md` y la grafica anotada a PDF vectorial en `F/`. Destino: 7.2.
Verificacion: totales por fila 31/85/67/1/16 y 200 casos; exactitud 73,5~%
(diagonal 147/200).

**Convencion de incrustacion (verbatim sugerido):**

```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{despliegue}
\caption{Diagrama de despliegue del sistema.}
\label{fig:despliegue}
\end{figure}
```

## Anexo B — Inventario de las 9 tablas y composicion destino

| # | Label | Archivo:linea | `\small` actual | Primera columna | Destino |
|---|-------|---------------|-----------------|-----------------|---------|
| 1 | `tab:comparativa` | `03:36` | Si | `p{2.6cm}` plana | `\small` + ragged-right |
| 2 | `tab:variables` | `04:22` | Si | `p{2.5cm}` plana | `\small` + mantener |
| 3 | `tab:capas` | `05:12` | No | `p{3.0cm}` plana | agregar `\small` + ragged-right |
| 4 | `tab:entidades` | `05:66` | Si | ragged-right | mantener |
| 5 | `tab:api` | `05:92` | No | `p{1.8cm}` plana | agregar `\small` + revisar |
| 6 | `tab:tiempos` | `07:12` | No | `p{4.0cm}` plana | agregar `\small` + ragged-right |
| 7 | `tab:matriz` | `07:42` | No | `p{3.2cm}` plana | agregar `\small` |
| 8 | `tab:metricas` | `07:61` | No | `p{3.5cm}` plana | agregar `\small` |
| 9 | `tab:errores` | `07:92` | Si | ragged-right | mantener |
