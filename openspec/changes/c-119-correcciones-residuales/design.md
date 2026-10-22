## Context

Ver `proposal.md`. La tesis corregida de `docs/Tesis/v9 (IA)/paper/` compila a un PDF de 102 paginas (cuerpo ~94; tope del plan, cuerpo <= 100). Siete defectos residuales de forma y consistencia sobrevivieron a las correcciones c-102..c-118. Todos estan verificados con evidencia sobre el codigo fuente y sobre `main.pdf` (compilado actualmente: `aggedright` = 6 ocurrencias, `Appendices` = 1 ocurrencia, 102 paginas). Esta fase es de solo planificacion: NO se edita ningun `.tex`.

Restricciones duras: no alterar contenido cientifico, numeros canonicos ni c-102..c-118; no tocar el memo, `CHANGES.md`, `dictamen-correcciones.md` ni `Bibliography_base.bib`; sin emojis; el tag `v1.0.0` ya existe y NO se mueve (un tag nuevo queda fuera de alcance).

## Goals / Non-Goals

**Goals:**

- Cerrar los 7 defectos residuales con cambios de forma neutrales o reductores en paginas.
- Dejar una verificacion reproducible por defecto (comando + valor esperado).
- Compilar y confirmar `aggedright` = 0, `Appendices` = 0 y cuerpo <= 100 paginas.

**Non-Goals:**

- No modificar numeros canonicos, metricas ni figuras.
- No soportar la afirmacion de 4 puntos con una medicion inexistente en `evaluation/` (no hay ablation ni registro de esa medicion).
- No publicar un tag nuevo ni mover `v1.0.0`.
- No refactorizar la estructura de anexos ni el estilo de tablas.

## Decisions

### D1. `\raggedright` partido en el preambulo tabular (`07-resultados.tex`)

La linea 17 termina con `\begin{tabular}{@{}>{` y la 18 empieza con `aggedright\arraybackslash}p{4.0cm} p{3.5cm} p{3.5cm} p{2.5cm}@{}}`; el `\r` desaparecio al partirse la linea.

BEFORE (lineas 17-18):

```latex
\begin{tabular}{@{}>{
aggedright\arraybackslash}p{4.0cm} p{3.5cm} p{3.5cm} p{2.5cm}@{}}
```

AFTER (una sola linea 17; se elimina la 18):

```latex
\begin{tabular}{@{}>{\raggedright\arraybackslash}p{4.0cm} p{3.5cm} p{3.5cm} p{2.5cm}@{}}
```

Preserva exactamente anchos (`4.0/3.5/3.5/2.5 cm`) y contenido.

Verificacion: `pdftotext "main.pdf" - | grep -c aggedright` == 0 (hoy 6).

### D2. Corchete sin cerrar en la tabla de cumplimiento (`09-conclusiones.tex:24`)

BEFORE:

```latex
Objetivo específico 2: clasificador & No alcanzado & Exactitud 73,5~\%, IC [67,0~\%, 79,1~\%, macro-F1 0,5207 \\
```

AFTER:

```latex
Objetivo específico 2: clasificador & No alcanzado & Exactitud 73,5~\%, IC [67,0~\%, 79,1~\%], macro-F1 0,5207 \\
```

Solo se inserta el `]` de cierre del intervalo.

Verificacion: `grep -c 'IC \[67,0~\\%, 79,1~\\%\]' 09-conclusiones.tex` == 1; compilar sin error de alineacion.

### D3. Numero de tabla hardcodeado incorrecto (`12-anexos.tex:35`)

El contrato REST es la tabla con rotulo `tab:api` en `05-arquitectura.tex:128` (subseccion `subsec:contrato-rest`). La remision literal `Tabla~5` no coincide con su numero real.

BEFORE:

```latex
... describe los puntos de entrada listados en la Tabla~5 de la \autoref{sec:arquitectura} ...
```

AFTER:

```latex
... describe los puntos de entrada listados en la Tabla~\ref{tab:api} de la \autoref{sec:arquitectura} ...
```

Decision de rotulo: `tab:api` (unico), verificado en `05-arquitectura.tex:128`.

Verificacion: `grep -n 'Tabla~5' 12-anexos.tex` no devuelve nada; el PDF muestra el numero real de la tabla de endpoints.

### D4. Rotulo de anexos en ingles (`preambles/preamble.tex`)

`main.toc:90` muestra `Appendices` (impreso por `\appendixtocname` del paquete `appendix` con opciones `[toc,title]`, linea 138). El cuerpo usa "Anexo" (p. ej. `12-anexos.tex:7` "El Anexo~A").

BEFORE (tras la linea 138, no existe):

```latex
% (sin redefinicion: el paquete usa los valores en ingles por defecto)
```

AFTER (agregar junto al bloque de apendices):

```latex
\renewcommand{\appendixname}{Anexo}
\renewcommand{\appendixtocname}{Anexos}
\renewcommand{\appendixpagename}{Anexos}
```

Decision: usar "Anexo"/"Anexos" (termino del cuerpo) en lugar del literal "Apéndice" sugerido, para consistencia interna. Alternativa considerada: `Apéndice`; se descarta por introducir un termino distinto al que usa el cuerpo.

Verificacion: `pdftotext "main.pdf" - | grep -c Appendices` == 0 (hoy 1); `grep -n 'Anexos' main.toc` muestra la entrada; `Appendices` ausente en el indice.

### D5. Redis listado como servicio interno (`05-arquitectura.tex:8`)

BEFORE: `... entre los servicios del sistema (N8N, backend, PostgreSQL, Redis) ...`

AFTER: `... entre los servicios del sistema (N8N, backend, PostgreSQL) ...`

Redis fue retirado en c-62. Se quita el elemento y la coma; la oracion queda coherente.

Verificacion: `grep -c Redis 05-arquitectura.tex` == 0.

### D6. Entrada "Referencias bibliograficas" en el indice (`main.tex:78`)

Hallazgo: `main.toc:89` es `\contentsline {section}{Referencias bibliograficas}{89}{subsection.12.8}`. El PRIMER campo es `section`, por lo que la entrada YA es de nivel de seccion (no esta anidada). El unico artefacto es el destino del hipervinculo, `subsection.12.8`, que reutiliza el ancla de la ultima subseccion del capitulo 12. Es un artefacto cosmetico de `hyperref`/`biblatex`, no un problema de nivel.

Decision: aplicar una correccion minima y segura insertando `\phantomsection` antes de `\printbibliography` (linea 78 de `main.tex`) para forzar un ancla propia.

BEFORE (`main.tex:77-78`):

```latex
\newpage
\printbibliography[heading=bibintoc,title={Referencias bibliograficas}]
```

AFTER:

```latex
\newpage
\phantomsection
\printbibliography[heading=bibintoc,title={Referencias bibliograficas}]
```

Si el ancla no cambia o el conteo de paginas variara, se registra como limitacion cosmetica aceptada (el nivel visible de la entrada ya es correcto) y no se escala el cambio.

Verificacion: `grep 'Referencias bibliograficas' main.toc` ya no muestra `subsection.12.8`; el numero de paginas no aumenta.

### D7. Afirmacion cuantitativa sin medicion (`06-implementacion.tex:62`)

No existe en `evaluation/` ninguna ablation ni registro de que el enriquecimiento del prompt elevara 4 puntos de F1 (`evaluation/README.md` declara que reglas y prompt se definieron antes del corpus y que el framework nunca los ajusta). No se inventa un numero.

BEFORE: `... lo que elevó la robustez de la clasificación sobre transcripciones automáticas en aproximadamente 4 puntos porcentuales de F1 respecto de la configuración inicial sin estas instrucciones.`

AFTER: `... lo que mejoró la robustez de la clasificación sobre transcripciones automáticas respecto de la configuración inicial sin estas instrucciones.`

Verificacion: `grep -c 'puntos porcentuales' 06-implementacion.tex` == 0; ningun numero nuevo introducido.

## Risks / Trade-offs

- D4 (renombres de apendices) no afecta el contador de tablas ni el cuerpo -> bajo. Mitigacion: verificar conteo de paginas y TOC.
- D6 (`\phantomsection`) podria no cambiar el ancla si `biblatex` la fija por otra via -> bajo. Mitigacion: verificacion explicita; fallback = limitacion aceptada.
- Cualquier recompilacion podria desplazar marginalmente flotantes -> bajo. Mitigacion: los cambios son neutrales/reductores; confirmar cuerpo <= 100 paginas.
- D3 depende del rotulo `tab:api`; si se renombrara en el futuro, la remision quedaria rota -> mitigado por `\ref` (autorresuelve mientras el rotulo exista); verificar que el rotulo existe antes de compilar.

## Migration Plan

1. Aplicar los 7 cambios en la fase apply (solo `.tex`), en el orden D1-D7.
2. Compilar:
   `docker run --rm -v "/home/skywalker/Desktop/notas/Tesis/Automatizacion-de-Mesa-de-Ayuda-N8N/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`
3. Ejecutar las verificaciones D1-D7; confirmar `aggedright`=0, `Appendices`=0, cuerpo <= 100 paginas.

Rollback: `git checkout -- "docs/Tesis/v9 (IA)/paper"` restaura los `.tex` al estado previo (los cambios quedan bajo control de versiones en apply). No se mueve ningun tag; `v1.0.0` permanece intacto.

## Open Questions

Ninguna que cambie specs, enfoque o tareas. D4 (termino "Anexo" vs "Apéndice") y D6 (correccion de ancla vs limitacion aceptada) quedan resueltos arriba con sus verificaciones.
