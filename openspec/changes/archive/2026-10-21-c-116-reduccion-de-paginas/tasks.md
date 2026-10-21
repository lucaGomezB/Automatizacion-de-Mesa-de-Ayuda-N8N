# Tasks: c-116 — Reducción de páginas

> Secuencia: aplicar DESPUÉS de c-112..c-115 (agregan contenido) y ANTES de c-111
> (tag). Compilar con la imagen Docker `texlive-thesis`:
> `docker run --rm -v "/home/skywalker/Desktop/notas/Tesis/Automatizacion-de-Mesa-de-Ayuda-N8N/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`
> No editar `.bib` ni `App/**`. Governance HIGH: aplicar D4 del design en cada recorte.

## 1. Baseline y presupuesto

- [x] 1.1 Medir el baseline: `pdfinfo main.pdf | grep Pages`. Registrar el valor (esperado 104). Guardar como referencia de partida.
- [x] 1.2 Confirmar la distribución por sección contra `main.toc` y fijar el presupuesto D3 (suma 4,5 >= 4). Registrar la tabla del design.
- [x] 1.3 Re-auditar la redundancia residual (post c-80 F5 y c-110): pares 1.1/2.1, 5.3/6.3, 8.1/9.1, resumen vs introducción, y anexos vs cuerpo. Listar los pasajes candidatos con archivo y línea. Verificar con `rg` que los pares ya deduplicados por c-80 no se reintroducen.

## 2. Reducción — Preliminares y Caps 1-4

- [x] 2.1 Glosario (`00-glosario.tex`): ajustar interlineado/columnas para ganar ~0,3 pág. sin eliminar entradas de siglas efectivamente usadas. Verificar que ninguna sigla del cuerpo queda sin entrada.
- [x] 2.2 Cap1 (`01-introduccion.tex`): eliminar redundancia resumen/introducción y listas redundantes (~0,3 pág.). No retirar cifras canónicas.
- [x] 2.3 Cap2 (`02-marco-teorico.tex`): recortar prosa duplicada con Cap1 (~0,3 pág.). Conservar la subsección HITL de c-110.
- [x] 2.4 Cap3 (`03-estado-del-arte.tex`): reducir leyendas y prosa redundante (~0,2 pág.). Conservar el protocolo de revisión de c-110.
- [x] 2.5 Cap4 (`04-marco-metodologico.tex`): recortar listas/prosa redundante (~0,3 pág.). Conservar fórmula de tamaño muestral, potencia, Shapiro-Wilk y criterios de exclusión.

## 3. Reducción — Caps 5-7

- [x] 3.1 Cap5 (`05-arquitectura.tex`): reducir espaciado vertical alrededor de figuras (las 8 figuras de c-80 se conservan) y listas redundantes (~0,5 pág.).
- [x] 3.2 Cap6 (`06-implementacion.tex`): acortar leyendas sobre-extendidas y prosa duplicada con Cap5 (~0,3 pág.). Conservar tabla de API y conteos de entidades/nodos.
- [x] 3.3 Cap7 (`11-aspectos-legales.tex`): recortar prosa redundante (~0,2 pág.). Conservar plazos, base de licitud, adecuación y transferencia telefónica de c-79.

## 4. Reducción — Caps 8-11 y Anexos

- [x] 4.1 Cap8 (`07-resultados.tex`): acortar leyendas de figuras/tablas y duplicación con Cap9 (~0,4 pág.). Conservar las 9 tablas, matriz 5x5, intervalos y ejemplos de error.
- [x] 4.2 Cap9 (`08-discusion.tex`): recortar duplicación residual con Cap8/Conclusiones (~0,4 pág.). Conservar hipótesis rivales, anti-calibración y costos con fuente.
- [x] 4.3 Caps 10-11 (`09-conclusiones.tex`, `10-recomendaciones.tex`): recortar prosa redundante (~0,3 pág.). Conservar el estado parcial de la hipótesis y las 8 subsecciones de recomendaciones.
- [x] 4.4 Anexos (`12-anexos.tex`): compactar Anexo A (listas) y Anexo H (prosa + `enumerate` + `lstlisting`) (~1,2 pág.). Conservar Anexo B con su referencia al tag, el corpus JSON y la tabla de parámetros.

## 5. Verificación

- [x] 5.1 Verificar invariantes D4: `rg` de los números canónicos (73,5 %, 0,5207, 71,2 %, W=363, 0,9639, 0,87, 2.646, 32,2 h) presentes; `rg` de valores retirados (9,5 %, 3.700, "Operaciones", W=0) ausentes.
- [x] 5.2 Confirmar que las 8 figuras y las 9 tablas siguen presentes y con su línea de fuente.
- [x] 5.3 Recompilar con la imagen `texlive-thesis` (`latexmk main.tex`). Verificar `main.pdf` sin errores fatales.
- [x] 5.4 Verificar `pdfinfo main.pdf | grep Pages` <= 100 y `rg -c "undefined reference|multiply defined label" main.log` = 0. Registrar conteo y resultado. Si `Pages > 100`, ampliar la palanca de anexos/leyendas (D3) sin violar D4 y recompilar.
- [x] 5.5 Confirmar que el tag `v1.0.0` (c-111) se crea sobre esta versión reducida, y no antes.
