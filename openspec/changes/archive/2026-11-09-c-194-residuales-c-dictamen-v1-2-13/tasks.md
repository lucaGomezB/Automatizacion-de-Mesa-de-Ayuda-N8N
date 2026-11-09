# Tasks: Atender los residuales C1 y C2 del dictamen CONEAU sobre v1.2.13 (c-194)

Convenciones: `S/` = `docs/Tesis/v10 (IA)/paper/sections/`; `B/` =
`docs/Tesis/v10 (IA)/Bibliography_base.bib`; `C/` = `docs/Tesis/Correcciones/`. "C1" y "C2"
remiten al dictamen CONEAU `auditorias/Dictamen_Tesis_v10_v1.2.13_CONEAU_2026-11-09.md`
(2026-11-09) sobre `v1.2.13`. Anclas por texto citado (`rg -n`). Linea base: 118 paginas;
resumen y abstract <= 250 palabras. No se edita `App/`, `n8n/`, `evaluation/`, `data/` ni
figuras. En la prosa del registro usar "seccion N (`archivo.tex`)". Release `v1.2.16`.

## 0. Verificacion de fragmentos y linea base (solo lectura; bloqueante para el apply)

- [x] 0.1 Confirmar la rama `change/c-194-residuales-c-dictamen-v1-2-13` y que existe
  `.openspec.yaml`; trabajar en esa rama.
- [x] 0.2 Compilar la linea base en el entorno de registro (Docker `texlive-thesis`): anotar
  paginas (esperado 118), `Overfull` (cantidad y maximo) y estado de `verify_citations.py`.
  Safety net: `python C/verificar_matriz_trazabilidad.py` -> 0 fallas; `cd C/ && python -m
  unittest test_verificar_matriz_trazabilidad test_resumir_registro_compilacion -v` en verde.
- [x] 0.3 Leer y guardar en el scratchpad el texto exacto de partida de: la fila "Lim."
  (`rg -n "Lim\. &" S/12-anexos.tex`), la nota de `Zendesk2026_help_desk`
  (`rg -n -A 7 "Zendesk2026_help_desk" B/`) y la oracion de Zanzotto
  (`rg -n "HitAI" S/02-marco-teorico.tex`).
- [x] 0.4 Confirmar con `rg -n "v1\.2\.15" S/05-arquitectura.tex S/06-implementacion.tex
  S/11-aspectos-legales.tex S/12-anexos.tex` las 12 ocurrencias (3/1/1/7) y con
  `rg -n "v1\.2\.12" S/` las dos historicas del dictamen (`12-anexos.tex:205` y `:304`).
- [x] 0.5 Registrar en `C/dictamen-correcciones.md` (seccion c-194) el estado de partida y las
  decisiones de los autores del design (D1 a D7).

## 1. Fila "Lim." del Anexo I (C1.a)

- [x] 1.1 `S/12-anexos.tex` (Anexo I, `sec:anexo-trazabilidad`, fila "Lim." de
  `tab:anexo-trazabilidad-2810`): reescribir la celda de secciones como secuencia temporal
  explicita segun design D1 ---primero `c-169` resolvio dos de los cinco limites (exactitud del
  brazo manual e intervalo del kappa) y dejo sin concluir la sub-hipotesis de intervencion
  humana; despues `c-190` la refuto sobre los casos revisados y corrigio la definicion de
  exactitud laxa; el efecto de orden no se resolvio y la validacion fuera de muestra permanece
  como limitacion negativa--- y cambiar la columna Change a `\texttt{c-169}, \texttt{c-190}`.
  Conservar todos los `\autoref` y el cierre con Resumen y `\emph{abstract}` y el Anexo B.
- [x] 1.2 Verificacion: el texto no contiene numeros de linea; "refutada" se aplica a la
  sub-hipotesis de intervencion y no al efecto de orden; la columna Change nombra `c-169` y
  `c-190`; la fila no agrega altura neta (ver 6.2).
- [x] 1.3 Registrar en `C/dictamen-correcciones.md` la correccion de C1.a con su fragmento
  verificable.

## 2. Nota de Zendesk (C2)

- [x] 2.1 `B/Bibliography_base.bib` (`Zendesk2026_help_desk`): reemplazar la nota
  "Documentaci{\'o}n de la plataforma (capacidades y precios)" por una que describa la pagina
  de producto de software de servicio al cliente (design D2). Conservar `author`, `title`,
  `url` (`https://www.zendesk.com/service/`) y `urldate`.
- [x] 2.2 Verificacion: `rg -ni "precios" B/` no devuelve la entrada de Zendesk; la URL y el
  `urldate` no cambian; `verify_citations.py` PASS y biber sin `WARN`/`ERROR`.
- [x] 2.3 Registrar en `C/dictamen-correcciones.md` la correccion de C2.

## 3. Atribucion a Zanzotto en dos oraciones (C1.b)

- [x] 3.1 `S/02-marco-teorico.tex:32` (2.4, `subsec:human-in-the-loop`): partir la oracion
  unica en dos segun design D3; la primera como inferencia de los autores (rol activo ante la
  ambiguedad semantica y responsabilidad de la decision); la segunda como paradigma HitAI
  atribuido a `\textcite{Zanzotto2019_human_in_the_loop}` (retribuir a quienes producen el
  conocimiento y sostener la supervision humana). No cambiar el significado ni las citas
  vecinas (Mosqueira-Rey, Amershi, Shneiderman, Wu).
- [x] 3.2 Verificacion: la oracion de inferencia ya no contiene la clausula de HitAI; la
  `\textcite{Zanzotto2019_human_in_the_loop}` figura en la oracion del paradigma; si hay pagina
  verificada se agrega y si no se registra la omision.
- [x] 3.3 Registrar en `C/dictamen-correcciones.md` la correccion de C1.b y la decision sobre
  la pagina.

## 4. Consistencia de las referencias de version entregada

- [x] 4.1 `S/05-arquitectura.tex`, `S/06-implementacion.tex`, `S/11-aspectos-legales.tex` y
  `S/12-anexos.tex`: cambiar `v1.2.15` a `v1.2.16` en las 12 ocurrencias de la configuracion
  entregada (design D4), incluidas las del Anexo A, el Anexo B y la Tabla de configuracion
  evaluada frente a entregada y su nota de fuente.
- [x] 4.2 Verificacion: `rg -n "v1\.2\.15" S/05-arquitectura.tex S/06-implementacion.tex
  S/11-aspectos-legales.tex S/12-anexos.tex` = 0 como referencia de configuracion entregada;
  `rg -n "v1\.2\.12" S/12-anexos.tex` conserva las dos historicas (`:205` y `:304`).
- [x] 4.3 Registrar en `C/dictamen-correcciones.md` el bump de version.

## 5. Registro, CHANGES y Anexo I

- [x] 5.1 `C/dictamen-correcciones.md`: seccion "Dictamen v10 / v1.2.13 (2026-11-09) - c-194"
  con la matriz en el formato de c-193 (Rec | Observacion | Correccion | Archivo | Estado) que
  cubra C1 y C2, las decisiones de los autores del design y el libro mayor de paginas. Si se
  usa la matriz estricta de 7 columnas con "Fragmento verificable", el verificador SHALL dar
  0 fallas.
- [x] 5.2 `CHANGES.md`: agregar la FASE 59 con el bloque de c-194 (alcance, decisiones,
  dependencias, gobernanza MEDIUM, "Leer antes"), al estilo de la FASE 58.
- [x] 5.3 `S/12-anexos.tex` (Anexo I): declarar C1 y C2 cerrados por c-194 (integrado en la
  reescritura de la fila "Lim." y el parrafo de la tabla; solo si no agrega altura neta; si
  agrega, compensar por D7).
- [x] 5.4 Verificacion: `python C/verificar_matriz_trazabilidad.py` -> 0 fallas; la seccion
  c-194 cubre C1 y C2.

## 6. Compilacion y artefactos generados

- [x] 6.1 Recompilar en el entorno de registro: 0 errores, 0 referencias o citas indefinidas,
  0 `multiply defined`, `main.blg` sin `WARN`/`ERROR`, 0 `??` en `pdftotext`, `Overfull` no
  mayor que la linea base; `verify_citations.py` PASS.
- [x] 6.2 Paginas <= 118 (D7); si se supera, condensar prosa en los parrafos tocados y
  recompilar; si aun asi no, detener y consultar. Resumen y abstract <= 250 palabras (sin
  tocar).
- [x] 6.3 Regenerar `docs/Tesis/v10 (IA)/tesis_para_agente.md` con `build_tesis_para_agente.py`
  (no vacio) y `docs/Tesis/v10 (IA)/paper/compilacion.md` con `C/resumir_registro_compilacion.py`;
  el SHA-256 de `compilacion.md` debe coincidir con `sha256sum main.pdf`.
- [x] 6.4 Registrar el libro mayor de paginas y palabras en `C/dictamen-correcciones.md`
  (seccion c-194).

## 7. Release `v1.2.16` y archivo

- [x] 7.1 `openspec validate c-194-residuales-c-dictamen-v1-2-13 --strict --no-interactive`
  pasa.
- [x] 7.2 `S/12-anexos.tex` (Anexo B, `sec:anexo-repositorio`): dejar la oracion de
  verificacion `git rev-list -n1 v1.2.16` y el nombre de la release entregada como `v1.2.16`;
  retirar el hash y el nombre de `v1.2.15` (decision D6). El texto MUST NOT imprimir el hash de
  una release previa.
- [x] 7.3 (Orquestador) Commit de contenido en
  `change/c-194-residuales-c-dictamen-v1-2-13` con la oracion de verificacion en el Anexo B y
  las fuentes versionadas; tag anotado `v1.2.16`; commit siguiente que reemplaza la oracion por
  el hash completo del commit de contenido (design D6).
- [x] 7.4 Verificacion de la regla de hash: `git diff --stat v1.2.16 HEAD -- "docs/Tesis/v10
  (IA)/paper/sections"` acotado; `pdftotext` del PDF etiquetado `v1.2.16` sin el hash de una
  release previa (`f72e6c8` ni otros).
- [x] 7.5 (Orquestador) `engram sync --project "Automatizacion-de-Mesa-de-Ayuda-N8N"` (nunca
  `--all`), commit de `.engram/`, PR contra `main` (nunca push directo) y archive del change.
