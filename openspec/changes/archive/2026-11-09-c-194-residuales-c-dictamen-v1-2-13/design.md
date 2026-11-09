# Design: Atender los residuales C1 y C2 del dictamen CONEAU sobre v1.2.13

## Context

Ver `proposal.md` para la motivacion. El dictamen CONEAU del 2026-11-09 sobre `v1.2.13`
(`auditorias/Dictamen_Tesis_v10_v1.2.13_CONEAU_2026-11-09.md`) dejo tres residuales de forma
y bibliografia:

- **C1.a** — Reescribir la fila "Lim." del Anexo I como SECUENCIA TEMPORAL: "primero no
  concluyente, con `c-169`; luego refutada sobre los casos revisados, con `c-190`".
- **C1.b** — Separar en dos oraciones la atribucion a Zanzotto en 2.4 (inferencia propia vs.
  paradigma HitAI) y paginarla si es posible.
- **C2** — Ajustar la nota de `Zendesk2026_help_desk` a lo que la pagina muestra.

c-192 y c-193 (release `v1.2.15`) cerraron el resto del dictamen y remitieron estos tres
residuales a `v1.2.16`. El dictamen no cambia cifras ni resultados; son desajustes de redaccion
y de referencia.

**Estado de partida verificado al proponer** (solo lectura):

- `12-anexos.tex:263` (Anexo I, `tab:anexo-trazabilidad-2810`, fila "Lim.") dice hoy, en una
  sola oracion compuesta: "la campana complementaria resuelve dos ---la exactitud del brazo
  manual y el intervalo del kappa--- ... deja entonces sin concluir la proporcion de
  intervencion humana, refutada despues sobre los casos revisados ... y no resuelve el efecto
  de orden ...; el quinto, la validacion fuera de muestra, permanece como limitacion negativa
  ...". La columna Change es `\texttt{c-169}`. El encabezado de la tabla es
  `Rec. & Change & Secciones de la tesis`, con la columna Change de `p{1.6cm}`.
- `Bibliography_base.bib:655-662` (`Zendesk2026_help_desk`): titulo "Zendesk Suite --- software
  de servicio al cliente", URL `https://www.zendesk.com/service/`, `urldate 2026-10-19`, nota
  "Documentacion de la plataforma (capacidades y precios)".
- `02-marco-teorico.tex:32` (2.4): una sola oracion une la inferencia de los autores ("los
  autores de esta tesis infieren que el diseno debe reservar a la persona un rol activo ... en
  el paradigma HitAI, que reclama retribuir a quienes producen el conocimiento y sostener la
  supervision humana") con `\parencite{Zanzotto2019_human_in_the_loop}`.
- `v1.2.15` aparece 12 veces como referencia de la configuracion entregada en
  `05-arquitectura.tex` (3), `06-implementacion.tex` (1), `11-aspectos-legales.tex` (1) y
  `12-anexos.tex` (7, incluido el Anexo B y la Tabla de configuracion). Dos referencias
  historicas al dictamen sobre `v1.2.12` (`12-anexos.tex:205` y `:304`) NO se tocan.
- Anexo B (`12-anexos.tex:44-46`): el tag vigente que imprime el PDF nombra `v1.2.15` y su hash
  `f72e6c8...`; el patron de release exige que el PDF etiquetado no imprima el hash de una
  release previa.

## Goals / Non-Goals

**Goals:**

- Que la fila "Lim." del Anexo I lea como secuencia temporal con los dos changes en la
  columna Change (D1).
- Que la nota de Zendesk describa la pagina de producto, sin "precios" (D2).
- Que la oracion de Zanzotto quede partida en dos con la atribucion correcta (D3).
- Que las referencias de version entregada queden en `v1.2.16` sin tocar las historicas de
  `v1.2.12` (D4).
- Que el registro, `CHANGES.md` y los artefactos generados queden actualizados (D5).
- Que `v1.2.16` cierre el ciclo con el patron de hash del Anexo B (D6) y que el PDF no supere
  las 118 paginas (D7).

**Non-Goals:**

- Tocar `App/`, `n8n/`, `evaluation/`, `data/` o figuras.
- Cambiar cifras, resultados, tablas de resultados o el presupuesto del resumen y el abstract.
- Reducir el PDF por debajo de 118 paginas.

## Decisions

### D0 — Verificacion previa de los fragmentos exactos (bloqueante, solo lectura)

Antes de editar, guardar en el scratchpad el texto exacto de partida de: la fila "Lim."
(`12-anexos.tex:263`), la nota de `Zendesk2026_help_desk` (`Bibliography_base.bib:661`) y la
oracion de Zanzotto (`02-marco-teorico.tex:32`). Confirmar que las 12 ocurrencias de `v1.2.15`
en los cuatro archivos son de la configuracion entregada y que las dos de `v1.2.12`
(`12-anexos.tex:205` y `:304`) son historicas del dictamen. Si algun fragmento difiere del
esperado, detener y consultar: el texto se reescribe sobre el vigente, no sobre el supuesto.

### D1 — Fila "Lim." del Anexo I como secuencia temporal

Reescribir el contenido de la celda de "Secciones de la tesis" de la fila "Lim." para que
exprese, en ese orden:

1. Primero (`c-169`): de los cinco limites estructurales que el dictamen consigno sin
   computarlos como incumplimiento, la campana complementaria resolvio dos ---la exactitud del
   brazo manual y el intervalo del kappa--- y dejo sin concluir la sub-hipotesis de
   intervencion humana; no resolvio el efecto de orden.
2. Despues (`c-190`): la sub-hipotesis de intervencion humana fue refutada sobre los casos
   revisados y se corrigio la definicion de exactitud laxa del brazo manual.
3. El quinto limite, la validacion fuera de muestra, permanece como limitacion negativa
   declarada por ausencia de un corpus independiente y no se cierra.

La columna Change SHALL quedar como `\texttt{c-169}, \texttt{c-190}`. Se conservan todos los
`\autoref` (`subsec:resultados-campana-medicion`, `subsec:balance-neto`,
`subsec:reduccion-intervencion`, `subsec:diseno-experimental`, `subsec:limitaciones-estudio`),
el cierre con "Resumen y \emph{abstract}; \autoref{sec:anexo-repositorio}
(Tabla~\ref{tab:configuracion-evaluada-entregada})" y el articulo de "intervencion humana"
como lo usa hoy la tesis. La fila MUST NOT contener numeros de linea y MUST NOT introducir
"refutada" para el efecto de orden (que no se resolvio). La reescritura MUST NOT agregar altura
neta: si la nueva redaccion ocupa una linea mas que la vigente, se condensa la misma prosa hasta
empatar (D7).

### D2 — Nota de Zendesk ajustada a la pagina

En `Bibliography_base.bib`, entrada `Zendesk2026_help_desk`: la nota pasa de "Documentacion de
la plataforma (capacidades y precios)" a describir lo que la pagina muestra, es decir, una
pagina de producto de software de servicio al cliente (por ejemplo, "Pagina de producto de
Zendesk Suite, software de servicio al cliente"). Se conservan `author`, `title`, `url`
(`https://www.zendesk.com/service/`) y `urldate`. La nota MUST NOT contener "precios". No se
agrega ni se retira ninguna entrada.

### D3 — Atribucion a Zanzotto en dos oraciones

En `02-marco-teorico.tex:32` se parte la oracion unica en dos, sin cambiar el significado:

- Oracion 1 (inferencia de los autores): los autores de esta tesis infieren que el diseno debe
  reservar a la persona un rol activo ante la ambiguedad semantica y la responsabilidad sobre
  las consecuencias de la decision.
- Oracion 2 (paradigma HitAI, atribuido a la fuente): en el paradigma \emph{HitAI}, que reclama
  retribuir a quienes producen el conocimiento y sostener la supervision humana
  `\parencite{Zanzotto2019_human_in_the_loop}`.

Se conserva el resto del parrafo (el aporte de Mosqueira-Rey et al. sobre las anotaciones y
correcciones, y las citas de Amershi, Shneiderman y Wu). La segunda oracion queda como el
paradigma y no como inferencia de los autores. Si el dictamen pidio paginar y no hay pagina
verificada, se deja la cita sin pagina y se registra la omision en `dictamen-correcciones.md`
(no se inventa un localizador).

### D4 — Consistencia de las referencias de version entregada

Las referencias a la configuracion entregada pasan de `v1.2.15` a `v1.2.16` en las 12
ocurrencias de `05-arquitectura.tex`, `06-implementacion.tex`, `11-aspectos-legales.tex` y
`12-anexos.tex` (incluidos el Anexo A, el Anexo B, la Tabla de configuracion evaluada frente a
entregada y su nota de fuente). Las dos referencias historicas al dictamen del 9-11 sobre
`v1.2.12` (`12-anexos.tex:205` y `:304`) MUST NOT modificarse: describen el dictamen sobre esa
version. La version `v1.2.15` NO se nombra como "entregada" en ninguna otra parte; si aparece
en un contexto historico, se conserva.

### D5 — Registro y CHANGES

- `docs/Tesis/Correcciones/dictamen-correcciones.md`: seccion "Dictamen v10 / v1.2.13
  (2026-11-09) - c-194" con la matriz de 5 columnas (Rec | Observacion | Correccion | Archivo |
  Estado) que cubra C1 (fila "Lim." y Zanzotto) y C2 (nota de Zendesk), con las decisiones de
  los autores y el libro mayor de paginas.
- `CHANGES.md`: agregar la FASE 59 con el bloque de c-194 (alcance, decisiones, dependencias,
  gobernanza MEDIUM, "Leer antes"), al estilo de la FASE 58.

### D6 — Release `v1.2.16` con el patron de hash del Anexo B (c-188)

Patron: el commit de contenido SHALL llevar en el Anexo B la oracion de verificacion
(`git rev-list -n1 v1.2.16`) en lugar del hash; el tag anotado `v1.2.16` apunta al commit de
contenido; el commit inmediatamente posterior reemplaza la oracion por el hash completo del
commit de contenido; los commits posteriores MUST NOT modificar las fuentes de la tesis. El
Anexo B SHALL nombrar la release entregada como `v1.2.16` y MUST NOT conservar el hash de una
release previa (`f72e6c8...` de `v1.2.15`, ni otros). El PDF compilado en el tag MUST NOT
imprimir el hash de una release anterior.

### D7 — Neutralidad de paginas

El PDF del tag `v1.2.16` MUST NOT superar las 118 paginas del tag `v1.2.15`. Las ediciones son
de redaccion y la fila "Lim." ya existe: si la compilacion supera 118, se condensa prosa en los
mismos parrafos tocados (fila "Lim.", 2.4 o la fuente) y se recompila; si aun asi no se logra,
se detiene y se consulta. El resumen y el abstract MUST NOT superar 250 palabras (no se tocan).

## Risks / Trade-offs

- [La fila "Lim." agrega una linea y supera 118 paginas] -> D1 exige condensar la misma prosa y
  D7 recorta y recompila; si no alcanza, se consulta.
- [Se toca por error una referencia historica a `v1.2.12`] -> D4 las fija y la tarea 4.2 las
  verifica con `rg`.
- [No hay pagina verificada para Zanzotto] -> D3 la deja sin pagina y registra la omision; no se
  inventa un localizador.
- [El Anexo B hereda el hash de `v1.2.15`] -> D6 lo corrige en el commit de contenido; la tarea
  7.4 verifica que el PDF etiquetado no lo imprima.
- [Gitleaks marca prosa con claves de cita o rutas] -> se usa "seccion N (`archivo.tex`)" y no
  se escriben claves que parezcan secretos.

## Migration Plan

Apply en el orden de `tasks.md`; compilacion en el entorno de registro (Docker `texlive-thesis`),
`verify_citations.py`, verificador de la matriz y `openspec validate --strict`. Release
(orquestador): rama `change/c-194-residuales-c-dictamen-v1-2-13`, commit de contenido con la
oracion de verificacion en el Anexo B, tag `v1.2.16`, commit del hash, `engram sync --project`,
PR contra `main` y archive. Rollback: revertir las fuentes y el registro al commit previo; no
hay codigo ni datos que revertir.

## Open Questions

- D3: paginar la cita de Zanzotto si se dispone de la pagina verificada de la fuente; si no, se
  registra la omision.
- D5: la matriz de la seccion c-194 se mantiene en 5 columnas (como c-193); si se opta por la
  matriz estricta de 7 columnas, `verificar_matriz_trazabilidad.py` SHALL dar 0 fallas.
- D4: confirmar en el apply que las 12 ocurrencias de `v1.2.15` son todas de configuracion
  entregada y que no hay ninguna adicional fuera de los cuatro archivos.
