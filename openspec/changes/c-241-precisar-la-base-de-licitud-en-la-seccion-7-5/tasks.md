# Tasks: Precisar la base de licitud en §7.5 (distinguir las dos bases)

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `C/` = `docs/Tesis/Correcciones/`.
Equivalente de Strict TDD para prosa: cada tarea de edicion tiene una verificacion que se corre
ANTES (linea base; debe mostrar el estado impreciso) y DESPUES (estado deseado), y ambas salidas se
reportan en `C/dictamen-correcciones.md` (seccion `c-241`). Reglas: no commitear ni pushear sin
pedido; no cambiar cifras, citas ni conclusiones; espanol sin emojis; solo alias (`E1`, `E2`, `O1`,
`O2`, `A1`, `T1`), nunca nombres reales; no tocar `App/`, `n8n/` ni `evaluation/`.

**Orden duro:** aplicar DESPUES de c-238 (tarea 6.3, parte oraciones de `S/11-aspectos-legales.tex`)
y de c-240 (tarea 2.1, escribio la oracion imprecisa). Archivar SOLO despues de archivar c-240 (el
delta MODIFICA un requisito que vive en el delta de c-240).

## 1. Guardas y lectura

- [ ] 1.1 Leer `proposal.md`, `design.md` (D1-D4), el delta `specs/tesis-document/spec.md` y la
  oracion vigente de §7.5 (`rg -n -i "licitud" "S/11-aspectos-legales.tex"`). Verificacion: la linea
  base muestra la oracion que colapsa ambas bases («el articulo~5 ... con el consentimiento
  informado») y §7.2 con la base distinta («articulo~5, inciso~2, apartado~d)»).
- [ ] 1.2 Confirmar que c-238 (tarea 6.3) y c-240 (tarea 2.1) estan aplicados sobre `S/11-aspectos-legales.tex`.
  Verificacion: `git log`/`git diff` o `rg -n` muestran sus efectos; si no, detener y reportar.

## 2. Compuertas de autores (OQ-01, OQ-02)

- [ ] 2.1 **[COMPUERTA OQ-01]** Presentar a los autores la asignacion de la base de licitud por
  artefacto (corpus de 200: articulo~5, inciso~2, apartado~d), consistente con §7.2; campana
  complementaria: consentimiento informado, articulo~5, inciso~1) y registrar su ratificacion
  literal, con fecha y responsable, en la tabla de compuertas de c-241 en `C/dictamen-correcciones.md`.
  Verificacion: la fila existe; sin respuesta, la tarea 3.1 queda bloqueada.
- [ ] 2.2 **[COMPUERTA OQ-02]** Aprobar la redaccion final de la oracion de licitud por artefacto
  antes de escribirla. Verificacion: la redaccion aprobada figura (o su referencia) en la tabla de
  compuertas; sin aprobacion, 3.1 queda bloqueada.

## 3. §7.5 — Oracion de licitud por artefacto

- [ ] 3.1 `S/11-aspectos-legales.tex` (`subsec:consentimiento-derechos`): reescribir la oracion de
  licitud de los datos conservados para declarar la base por artefacto segun la ratificacion de 2.1:
  el corpus de 200 con la base de §7.2 (articulo~5, inciso~2, apartado~d) y la campana complementaria
  con su base ratificada; sin colapsar ambas en «articulo~5 + consentimiento». Verificacion (ANTES):
  la oracion colapsa ambas bases; (DESPUES): declara la base por artefacto y cita el inciso del corpus
  de 200; `rg -n "licitud" "S/11-aspectos-legales.tex"` muestra la oracion corregida.
- [ ] 3.2 Mantener el resto del parrafo de §7.5 y sus remisiones sin cambio (retiro del corpus,
  ausencia de datos de terceros, remision a §7.3). Verificacion: `git diff` limitado a la oracion de
  licitud; no se altera ninguna otra frase factual ni cifra.

## 4. Verificacion de coherencia

- [ ] 4.1 Coherencia §7.2 <-> §7.5: la base del corpus derivado de la relacion de empleo es la misma
  en ambas subsecciones. Verificacion: comparar `rg -n "inciso" "S/11-aspectos-legales.tex"` en
  `subsec:principios-datos` y `subsec:consentimiento-derechos`; deben coincidir en el inciso del
  corpus de 200.
- [ ] 4.2 Sin colapso de bases ni consentimiento mal atribuido. Verificacion:
  `rg -n -i "articulo~?5.*consentimiento|consentimiento.*articulo~?5" "S/11-aspectos-legales.tex"`
  no devuelve una unica invocacion que funda en consentimiento ambos artefactos; §7.5 no funda en el
  consentimiento el corpus de 200.
- [ ] 4.3 Compilacion de verificacion: copiar `docs/Tesis/v10 (IA)` a un directorio temporal y
  compilar alli (`latexmk main.tex`). Verificacion: 0 errores fatales, 0 referencias/citas
  indefinidas, 0 etiquetas duplicadas. No versionar el PDF ni regenerar `compilacion.md`.

## 5. Registro y cierre

- [ ] 5.1 `C/dictamen-correcciones.md`: agregar la entrada de c-241 con la tabla de compuertas
  (OQ-01, OQ-02: respuesta, fecha, responsable), las dos salidas de la verificacion de 3.1 y la fila
  por la imprecision legal de §7.5 (archivo:linea). Verificacion: la seccion `c-241` existe y contiene
  cada bloque; las entradas previas quedan intactas.
- [ ] 5.2 `openspec validate c-241-precisar-la-base-de-licitud-en-la-seccion-7-5 --strict`. Verificacion:
  pasa.
- [ ] 5.3 Verificar la dependencia de fusion: confirmar que c-240 esta archivado antes de archivar
  c-241; si no, NO archivar. Verificacion: `openspec list --json` no lista `c-240-...` como change
  activo (o `openspec/changes/archive/` la contiene).
