## 0. Linea base y gate

- [x] 0.1 Confirmar la linea base recompilando con `docker run --rm -v "$PWD/docs/Tesis/v10 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex` y registrando `pdfinfo` = 118 total, `Anexos` en `main.toc` p. 108 (cuerpo 107, anexos 11) y 13 `Overfull \hbox`. Verificacion: los tres numeros coinciden con los de `dictamen-correcciones.md` (c-169) y `CHANGES.md`. NOTA: la linea base REAL medida (post-c-185) es **119 total, `Anexos` p. 109 (cuerpo 108, anexos 11), 13 overfull**; c-185 (ya aplicado) sumo +1 al total. Se parte de 119.
- [x] 0.2 Capturar el diff base de `git status`/`git diff` sobre `docs/Tesis/v10 (IA)/` para poder comparar el antes/despues. Verificacion: el arbol de la tesis esta limpio antes de empezar. (El arbol tenia solo los cambios de c-185, preservados.)

## 1. Fase A - forma

- [x] 1.1 Reubicar `fig:componentes` (`05-arquitectura.tex:32-37`) al Anexo A de `12-anexos.tex`, conservando figura, pie y fuente. Verificacion: `grep -n "fig:componentes" sections/*.tex` la ubica solo en `12-anexos.tex` y el inventario del Anexo A la lista.
- [x] 1.2 Reubicar `fig:secuencia` (`05-arquitectura.tex:55-60`) al Anexo A de `12-anexos.tex`, conservando figura, pie y fuente. Verificacion: `grep -n "fig:secuencia" sections/*.tex` la ubica solo en `12-anexos.tex`.
- [x] 1.3 Actualizar las remisiones del cuerpo a ambas figuras (parrafos de `05:10` y `05:39`) y el indice de figuras. Verificacion: ninguna `\autoref`/`\ref` a `fig:componentes` o `fig:secuencia` queda indefinida en `main.log`.
- [x] 1.4 Cambiar `07-resultados.tex:108` de `\begin{table}[p]` a `\begin{table}[htbp]` si la tabla cabe en el texto. Verificacion: la tabla aparece en el cuerpo del PDF (no en una pagina de flotantes dedicada) y `pdfinfo` no aumenta.
- [x] 1.5 Compactar los `Overfull \hbox` mayores a 10pt: `06:39-40` (56,9pt), `11:54-64` (20,6pt), `11:78-90` (20,6pt) y los de `12:54` (34,0pt), `12:69-70` (19,2pt), `12:123-124` (18,6pt), sin cambiar el contenido. Verificacion: `grep -c "Overfull \\\\hbox" main.log` baja (13 -> 7) y no queda ninguno > 10pt en el cuerpo (maximo 8,2pt).

## 2. Fase B - de-duplicacion

- [x] 2.1 Reemplazar los pasajes repetidos de `09-conclusiones.tex:41` (y opcional `:6`) por `\autoref` a su seccion primaria. Verificacion: la afirmacion y las cifras siguen en la seccion primaria; 0 referencias indefinidas.
- [x] 2.2 Reemplazar la oracion final repetida de `01-introduccion.tex:18` por `\autoref`. Verificacion: la cifra canonica (61,6 s / 32,2 h) sigue presente y ninguna referencia queda indefinida.
- [x] 2.3 Reemplazar los pasajes repetidos de `10-recomendaciones.tex:6,18` (y `:48`) por `\autoref`. Verificacion: cada afirmacion retirada existe en su seccion primaria; el capitulo conserva sus remisiones.
- [x] 2.4 Reemplazar los pasajes repetidos de `11-aspectos-legales.tex:24,32,36` (y `:8,34`) por `\autoref`. Verificacion: las afirmaciones legales primarias siguen presentes; 0 referencias colgadas.
- [x] 2.5 Reemplazar los pasajes repetidos de `07-resultados.tex:159,252` (y `:161,250-258`) por `\autoref`. Verificacion: las cifras canonicas (73,5 %, 0,6508, 0,5207, W=363, 0,9639) permanecen; las tablas referenciadas siguen renderizando.
- [x] 2.6 Reemplazar los pasajes repetidos de `03-estado-del-arte.tex:6,8,12-14,56` por `\autoref`. Verificacion: la afirmacion primaria y sus citas siguen presentes; 0 citas huerfanas. NOTA: `03` es la seccion PRIMARIA de su contenido (protocolo de revision, soluciones comerciales, brecha); solo se recorto la oracion final de `03:56`, que duplicaba `08:38`/`01:66`. No se retiro contenido primario.
- [x] 2.7 Verificar que ninguna remision introducida deja `\label` sin destino. Verificacion: `main.log` con 0 `undefined` y `python3 "docs/Tesis/v10 (IA)/verify_citations.py"` = PASS.

## 3. Fase C - decision del autor (gateada)

- [x] 3.1 Elevar al autor la decision sobre condensar los capitulos 4 (`04:14,63,65,81,89`) y 6 (`06:99-113` y `06:36-46,70-77`) y sobre reubicar capturas de UI. Verificacion: decision registrada (si/no) y, si es "si", su alcance exacto. DECISION (2026-11-08): APROBADA, con la excepcion de que las capturas de UI (`fig:panel_admin`, `fig:dashboard`, `06:99-113`) PERMANECEN en el cuerpo.
- [x] 3.2 Aplicar solo lo aprobado en 3.1, preservando afirmaciones, cifras y figuras. Verificacion: el diff de los capitulos 4 y 6 esta respaldado por la decision de 3.1 y no retira contenido cientifico.
- [x] 3.3 Si el autor no aprueba la Fase C, dejar los capitulos 4 y 6 sin cambios y registrar la decision como pendiente. Verificacion: `git diff` sin cambios en `04-*` y `06-*`. (N/A: la Fase C fue aprobada en 3.1; no se aplica este camino condicional.)

## 4. Contabilidad de paginas

- [x] 4.1 Corregir la entrada del libro mayor de c-169 en `dictamen-correcciones.md` a la metrica del total: `v1.2.8` = 118 total, exceso **+18** sobre 100; retirar la cuenta por cuerpo sin anexos (rama (b), superada) como base del cumplimiento y conservarla solo como dato complementario. Verificacion: la fila de c-169 usa la metrica del total y declara el exceso +18.
- [x] 4.2 Corregir la clausula "Release vigente `v1.2.8`" de `CHANGES.md` a la metrica del total. Verificacion: la clausula declara 118 totales con exceso +18 sobre el tope total de 100; sin mencion de "+7 de cuerpo" como regla vigente.
- [x] 4.3 Registrar la nueva fila del libro mayor con el total alcanzado y su delta respecto de `v1.2.8` (118). Verificacion: la fila consigna total, cuerpo, anexos, delta total y delta cuerpo, con la metrica del total. (Total 118, cuerpo 105, anexos 13; delta total 0 vs `v1.2.8` y -1 vs c-185.)

## 5. Compilacion y verificacion final

- [x] 5.1 Recompilar en `texlive-thesis` (`latexmk main.tex`) y medir. Verificacion: exit 0; `main.log` con 0 `^!`, 0 `undefined` y 0 `multiply defined`; `pdfinfo` registra el total (118).
- [x] 5.2 Verificar referencias y citas. Verificacion: `python3 "docs/Tesis/v10 (IA)/verify_citations.py"` = PASS; texto del PDF sin `??` (0).
- [x] 5.3 Verificar la invariante de contenido. Verificacion: todas las cifras canonicas (73,5 %, 0,6508, 0,5207, 71,2 %, W=363, 0,9639, kappa 0,87, 2.646, 32,2 h), las 8 figuras y las 9 tablas del change set siguen en el PDF (11 figuras y 22 tablas renderizan).
- [x] 5.4 Confirmar que el preambulo no cambio. Verificacion: `git diff` sin cambios en `preambles/preamble.tex` (interlineado `\doublespacing`, margenes 2,54 cm, `\bibfont` `\footnotesize`) y sin `\newpage` de capitulo retirado.
- [x] 5.5 Registrar el total alcanzado y su delta respecto de la linea base `v1.2.8`. Verificacion: la fila 4.3 y la evidencia de 5.1 coinciden; la meta <= 100 se declara como objetivo (punto dulce) y no alcanzarla no invalida la reduccion.

## 6. Cierre documental

- [x] 6.1 Regenerar los renders derivados (`tesis_para_agente.md`, `tesis_completa_extraida.txt`, `tesis_para_evaluacion.txt`) si el recorte altera el conteo de paginas. Verificacion: los renders reflejan el PDF final.
- [x] 6.2 Correr `openspec validate c-184-recortar-la-longitud-de-la-tesis --strict --no-interactive`. Verificacion: validacion en verde.
