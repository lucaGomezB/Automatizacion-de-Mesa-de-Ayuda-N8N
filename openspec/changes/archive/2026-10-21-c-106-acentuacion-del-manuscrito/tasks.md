# Tasks — c-106 — Acentuación normalizada del manuscrito y resumen ≤ 250 palabras

> Governance BAJO/MEDIO. Alcance y tokens protegidos: `design.md` (D1-D2).
> NO se edita `Bibliography_base.bib`, `main.tex`, `preambles/` ni `docs/Tesis/`.
> c-106 se aplica **después** de c-104/c-105/c-107 (y c-108/c-109/c-110 cuando
> existan): D7.

## 0. Prerrequisitos (solo lectura)

- [x] 0.1 Confirmar con `git status` que el árbol está limpio y que los changes de
  prosa previos (c-104/c-105/c-107) ya están aplicados; si no, DETENER.
- [x] 0.2 Registrar el conteo de páginas de partida (`main.pdf` = 103) y la fecha.
  (Nota: el `main.pdf` presente al iniciar tenía **105** páginas; se registró ese valor.)
- [x] 0.3 Capturar la allowlist de tokens protegidos (D2): `rg` de las cinco
  cadenas de categorías y de las claves de `\label`/`\ref`/`\cite` a un archivo
  temporal para la comparación posterior.

## 1. Preparar el pase de acentuación (D3)

- [x] 1.1 Decidir: adaptar `docs/Tesis/acentuar_tesis.py` o escribir un pase
  equivalente. Requisitos mínimos: retarget a `v9 (IA)`, acentuar dentro de
  argumentos de texto, allowlist de tokens protegidos, sin `.tex.bak`.
- [x] 1.2 Implementar/adaptar el pase y correr en **dry-run**; revisar que el diff
  propuesto no incluya líneas con tokens protegidos.
- [x] 1.3 Confirmar cobertura: el pase MUST acentuar `\section{}`/`\caption{}`/
  `\textbf{}`/`\footnote{}` y prosa, y MUST saltar `verbatim`/`lstlisting`/`\verb`/
  matemática/URL/DOI/rutas/claves.

## 2. Aplicar la normalización (D1, D2, D4)

- [x] 2.1 Aplicar el pase a los 14 `sections/*.tex`.
- [x] 2.2 Revisar el diff: ninguna cadena de categoría con tilde; ninguna clave
  `\label`/`\ref`/`\cite` cambiada; ningún dígito/comando alterado; `hipótesis` y
  `síntesis` intactas.
- [x] 2.3 Verificar que no se crearon `.tex.bak` ni se tocó otro directorio.

## 3. Reducir el resumen a ≤ 250 palabras (D5)

- [x] 3.1 Reescribir el resumen español (`00-resumen.tex`) a `≤ 250` palabras de
  prosa conservando problema, método (200 casos pareados), resultados clave
  (61,6 s → 17,76 s, 71,2 %, `W=363`, `r=0,9639`, 73,5 %, 0,5207, Kappa 0,87) y
  conclusión.
- [x] 3.2 Confirmar que NO se reintroducen valores retirados por c-107 (9,5 %,
  3.700) ni confirmación plena de la hipótesis.
- [x] 3.3 Contar palabras con el método de D5 y registrar el resultado (`≤ 250`).

## 4. Alinear el abstract (D6)

- [x] 4.1 Ajustar el abstract (`00-resumen.tex:25`) a `≤ 250` palabras y a la
  misma información que el resumen reducido (mismas cifras, categorías y estado de
  hipótesis).
- [x] 4.2 Contar palabras del abstract y registrar el resultado (`≤ 250`).

## 5. Verificación de tokens protegidos (D8)

- [x] 5.1 Re-capturar la allowlist y comparar: el conjunto de cadenas de
  categorías y de claves `\label`/`\ref`/`\cite` es idéntico al de 0.3.
- [x] 5.2 `rg` de control: las cinco cadenas de categorías permanecen SIN tilde.
- [x] 5.3 `rg` de control: no quedan formas sin tilde de palabras que la requieren
  en prosa (`clasificacion`, `informacion`, `metodologico`, `Capitulo`,
  `Introduccion`, etc.).
- [x] 5.4 Confirmar que `Bibliography_base.bib` y la ruta `docs/Tesis/` no fueron
  tocados.

## 6. Compilación y presupuesto de páginas (D8, D9)

- [x] 6.1 Compilar con la imagen local:
  `docker run --rm -v "<repo>/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`.
- [x] 6.2 Confirmar cero errores fatales y cero "undefined reference" nuevas;
  registrar el conteo de páginas y confirmar que no aumentó respecto de 103.