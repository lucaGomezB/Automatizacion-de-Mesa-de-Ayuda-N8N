## MODIFIED Requirements

### Requirement: English abstract

The thesis SHALL contain an English abstract section immediately after the Spanish "Resumen" in `00-resumen.tex`. The abstract SHALL be at most 250 words, SHALL accurately summarize the thesis content, and SHALL be consistent with the reduced Spanish "Resumen" (same key figures, same category strings, same declared state of the principal hypothesis).

#### Scenario: English abstract present and positioned
- **WHEN** opening the compiled PDF
- **THEN** an "Abstract" section appears after the Spanish "Resumen" section
- **AND** the abstract title is formatted at the same heading level as "Resumen"

#### Scenario: English abstract length
- **WHEN** counting the words in the English abstract (prose body, excluding LaTeX commands and the keywords line)
- **THEN** the word count is at most 250 words

#### Scenario: English abstract content accuracy
- **WHEN** reading the English abstract
- **THEN** it covers the thesis problem, methodology, key results, and conclusions
- **AND** all technical terms are consistent with the Spanish text (same classifier names, tool names, category strings)
- **AND** the key figures match those of the reduced Spanish "Resumen" (200 paired cases, 61.6~s to 17.76~s, 71.2~\% reduction, \(W = 363\), \(r = 0.9639\), 73.5~\% accuracy, macro-F1 0.5207, Cohen's Kappa 0.87)

## ADDED Requirements

### Requirement: Acentuación normalizada del manuscrito

Los 14 archivos `.tex` de `docs/Tesis/v9 (IA)/paper/sections/` SHALL presentar el
texto español acentuado conforme a las reglas ortográficas del español. La
normalización SHALL aplicarse a la prosa (cuerpo, encabezados, pies de página,
pies de figura y tabla, celdas de texto) incluyendo el texto dentro de argumentos
de comandos portadores de texto (`\section{}`, `\subsection{}`, `\caption{}`,
`\textbf{}`, `\emph{}`, `\item`, `\footnote{}`). El documento MUST NOT modificar
tokens protegidos: las cinco cadenas canónicas de categorías (`Seguridad
Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de
Datos`, `Sistemas`), las claves de `\label{}`/`\ref{}`/`\autoref{}`/`\cref{}`,
las claves de `\cite{}`/`\textcite{}`/`\parencite{}`, las rutas de
`\input{}`/`\includegraphics{}`/`\bibliography{}` y las rutas de repositorio en
prosa (`docs/Tesis/`, `evaluation/`, `data/`, `App/Backend`), el contenido de
`verbatim`/`lstlisting`/`\verb`, las URLs y DOI, la matemática, los nombres de
comandos LaTeX y las palabras ya acentuadas. Ninguna corrección SHALL
des-acentuar texto, duplicar tildes ni alterar cifras. El cambio MUST NOT editar
`Bibliography_base.bib`.

#### Scenario: Prosa acentuada
- **WHEN** se busca en `sections/*.tex` una forma sin tilde de una palabra que la requiere (por ejemplo "clasificacion", "informacion", "metodologico", "Capitulo", "Introduccion")
- **THEN** no queda ninguna ocurrencia en prosa sin acentuar
- **AND** el texto ya acentuado permanece sin cambios (no se des-acentúa ni se duplica la tilde)

#### Scenario: Tokens protegidos intactos
- **WHEN** se comparan antes y después las cinco cadenas canónicas de categorías, las claves de `\label`/`\ref`/`\autoref`, las claves de citas y las rutas de `\input`/`\includegraphics`
- **THEN** el conjunto de tokens es idéntico
- **AND** ninguna cadena de categoría incorpora tilde

#### Scenario: Pares sensibles preservados
- **WHEN** se inspeccionan las ocurrencias de `hipótesis` y `síntesis`
- **THEN** se conservan exactamente acentuadas como corresponde
- **AND** no aparecen como `hipotesis`/`sintesis` ni con tilde duplicada

#### Scenario: Sin residuos de la herramienta
- **WHEN** se revisa el árbol de trabajo tras aplicar la normalización
- **THEN** no existen archivos `.tex.bak` nuevos
- **AND** ningún archivo fuera de `docs/Tesis/v9 (IA)/paper/sections/` fue modificado

### Requirement: Presupuesto de palabras del resumen en español

El resumen en español (`00-resumen.tex`) SHALL tener como máximo 250 palabras de
prosa. La reducción SHALL conservar el problema, el método y diseño (200 casos
pareados), los resultados clave (61,6~s a 17,76~s, reducción del 71,2~\%, \(W =
363\), \(r = 0,9639\), exactitud 73,5~\%, macro-F1 0,5207, Kappa de Cohen 0,87) y
la conclusión. El resumen MUST NOT reintroducir valores retirados por c-107 (la
intervención humana del 9,5~\% y el universo calendario 3.700) ni presentar la
hipótesis principal como plenamente confirmada.

#### Scenario: Longitud del resumen
- **WHEN** se cuenta el número de palabras de prosa del cuerpo del resumen en español (excluyendo comandos LaTeX y la línea "Palabras clave")
- **THEN** el conteo es como máximo 250 palabras

#### Scenario: Cifras clave conservadas
- **WHEN** se lee el resumen reducido
- **THEN** aparecen 200 casos, 61,6~s, 17,76~s, 71,2~\%, \(W = 363\), \(r = 0,9639\), 73,5~\% y 0,5207
- **AND** el resumen no presenta la hipótesis principal como plenamente confirmada

#### Scenario: Sin valores retirados
- **WHEN** se busca "9,5 %" o "3.700" en el resumen y el abstract
- **THEN** no aparecen como resultado vigente
- **AND** el texto es coherente con los valores canónicos propagados por c-107
