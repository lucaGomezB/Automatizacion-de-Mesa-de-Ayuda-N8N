# Tasks — c-118 — Capitulo de cumplimiento ISO/IEC 27001-27002 y NIST CSF 2.0

> Governance ALTO: contenido de tesis + riesgo de neutralidad de paginas (tope duro
> de 100). NO se edita `.tex` en la fase de propose. NO se tocan
> `docs/Tesis/Correcciones/numeros-canonicos.md`, `CHANGES.md` ni
> `dictamen-correcciones.md`. Las decisiones estan en `design.md`.

## 0. Prerrequisitos y linea base (gate de secuenciacion)

- [ ] 0.1 Confirmar con `openspec list --json` que c-102..c-117 estan aplicados/archivados
  y que c-111 sigue activo sin aplicar. Verificacion: c-111 aparece como change activo;
  ningun change de contenido c-102..c-117 queda pendiente.
- [ ] 0.2 Registrar el conteo de paginas de partida:
  `pdfinfo "docs/Tesis/v9 (IA)/paper/main.pdf" | grep Pages`. Verificacion: el valor
  registrado es el tope vigente (<= 100).
- [ ] 0.3 Registrar el conteo de figuras de partida:
  `grep -rc "begin{figure}" "docs/Tesis/v9 (IA)/paper/sections/" | awk -F: '{s+=$2} END {print s}'`.
  Verificacion: el valor registrado es 8.
- [ ] 0.4 Confirmar que no existe contenido ISO/NIST en la tesis:
  `grep -rniE "ISO.?2700|NIST|CSF" "docs/Tesis/v9 (IA)/paper/sections/"`. Verificacion:
  sin coincidencias.

## 1. Redaccion del capitulo de cumplimiento

- [ ] 1.1 Agregar un `\section{Cumplimiento normativo y alineacion con estandares}`
  con `\label{sec:cumplimiento}` al final de `sections/11-aspectos-legales.tex` (antes
  del `\newpage`). Verificacion: el `\section` existe y tiene `\label`.
- [ ] 1.2 Redactar `\subsection{Marco de referencia adoptado}` (`\label{subsec:cumplimiento-marco}`)
  declarando los estandares (ISO/IEC 27001:2022 + 27002:2022, NIST CSF 2.0, ISO/IEC
  27701, Ley 25.326) y el descargo de que es una evaluacion de alineacion, no una
  certificacion. Verificacion: el parrafo nombra los cuatro estandares y el descargo.
- [ ] 1.3 Redactar `\subsection{Estado de alineacion con ISO/IEC 27002:2022}`
  (`\label{subsec:cumplimiento-iso}`) con la Tabla `tab:cumplimiento-iso` (columnas
  `Tema | Controles | Estado | Evidencia / brecha principal`) agrupando por tema
  (5.x, 6.x, 7.x, 8.x) y con linea de fuente. Verificacion: la tabla existe, agrupa por
  tema, no lista los 93 controles y declara su fuente.
- [ ] 1.4 Redactar `\subsection{Perfil de alineacion con NIST CSF 2.0}`
  (`\label{subsec:cumplimiento-nist}`) con la Tabla `tab:cumplimiento-nist` (seis
  funciones GV/ID/PR/DE/RS/RC, subcategoria representativa y madurez 0-4) y linea de
  fuente. Verificacion: la tabla tiene las seis funciones y su madurez.
- [ ] 1.5 Redactar `\subsection{Brechas principales y hoja de ruta}`
  (`\label{subsec:cumplimiento-brechas}`) cruzando cada brecha priorizada con su estado
  (cerrada por C-61..C-66 o residual) y marcando las organizacionales como
  responsabilidad del adoptante. Verificacion: cada control cerrado se asocia a su
  change o artefacto; las brechas organizacionales quedan atribuidas al adoptante.
- [ ] 1.6 Redactar `\subsection{Alineacion con el marco legal}`
  (`\label{subsec:cumplimiento-legal}`) remitiendo con `\autoref` al marco normativo y a
  la transferencia internacional del Capitulo 11, sin repetir su contenido.
  Verificacion: hay remisiones cruzadas y no se duplica el marco normativo.

## 2. Neutralidad de paginas (absorcion / reemplazo)

- [ ] 2.1 Reemplazar la prosa de `11.4 Seguridad tecnica` por 2-3 oraciones de remision
  a la Tabla `tab:cumplimiento-iso`, plegando su evidencia tecnica a la tabla.
  Verificacion: la subseccion ya no contiene la narracion extensa; su evidencia
  permanece en la tabla.
- [ ] 2.2 Compilar con la imagen local y medir:
  `docker run --rm -v "<repo>/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`
  y `pdfinfo "docs/Tesis/v9 (IA)/paper/main.pdf" | grep Pages`. Verificacion: total <= 100.
- [ ] 2.3 Si el total excede 100, condensar la prosa redundante de `11.2`/`11.3` y del
  Anexo `12.7 Documentacion operativa` (que reitera documentos del repositorio), sin
  retirar hechos juridicos exigidos por el spec. Verificacion: el total vuelve a <= 100
  sin perder hechos juridicos, numeros canonicos ni lineas de fuente.
- [ ] 2.4 Si aun con 2.3 no se alcanza el tope, DETENER y escalar al autor; no eliminar
  contenido cientifico para hacer lugar. Verificacion: queda registrada la decision del
  autor antes de continuar.

## 3. Lenguaje y coherencia

- [ ] 3.1 Verificar ausencia de terminos prohibidos:
  `grep -rniE "certificado|certificacion|compliant|conforme|cumple ISO|cumple NIST" "docs/Tesis/v9 (IA)/paper/sections/11-aspectos-legales.tex"`.
  Verificacion: sin coincidencias como declaracion de conformidad; el vocabulario usado
  es "alineado con" / "controles mapeados a".
- [ ] 3.2 Verificar coherencia legal: comparar las menciones a Ley 25.326, transferencia
  internacional y plazos ARCO del capitulo nuevo con 11.3/11.5. Verificacion: son
  consistentes y no contradictorias.

## 4. Compilacion y gates finales

- [ ] 4.1 Compilar de nuevo con `texlive-thesis` tras todas las ediciones.
  Verificacion: sin errores fatales.
- [ ] 4.2 Verificar cero referencias indefinidas en el log:
  `grep -iE "undefined|multiply defined" main.log`. Verificacion: sin coincidencias.
- [ ] 4.3 Verificar el tope de paginas: `pdfinfo main.pdf | grep Pages`.
  Verificacion: total <= 100.
- [ ] 4.4 Verificar el conteo de figuras:
  `grep -rc "begin{figure}" sections/ | awk -F: '{s+=$2} END {print s}'`.
  Verificacion: 8.
- [ ] 4.5 Verificar que los numeros canonicos y las tablas con fuente no cambiaron.
  Verificacion: comparacion contra la linea base de 0.2/0.3 sin diferencias.
- [ ] 4.6 Recompilar `main.pdf` y confirmar que refleja el capitulo nuevo.
  Verificacion: el PDF contiene la seccion de cumplimiento con sus tablas.

## 5. Cierre

- [ ] 5.1 Actualizar `tasks.md` marcando las tareas completadas. Verificacion: todas las
  tareas de 0 a 4 estan en `[x]` o justificadas.
- [ ] 5.2 Registrar en la evidencia del change el conteo final de paginas y el comando
  reproducible. Verificacion: el conteo final <= 100 queda consignado.
- [ ] 5.3 NO crear el tag `v1.0.0` (eso corresponde a c-111). Verificacion: `git tag -l`
  no incluye un tag creado por c-118.
