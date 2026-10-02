# Overleaf Compilation Instructions

## Files to Upload

Upload the following from `docs/Tesis/v8 (IA)/`:

1. **main.tex** (from `paper/`)
2. **Entire `paper/preambles/` folder** (contains `preamble.tex`)
3. **Entire `paper/sections/` folder** (14 .tex files)
4. **`Bibliography_base.bib`** (MUST be one level ABOVE the `paper/` folder on Overleaf -- the preamble references it at `../Bibliography_base.bib`)

## Folder Structure on Overleaf

```
overleaf-project/
├── main.tex
├── Bibliography_base.bib          <-- one level UP from paper/
├── preambles/
│   └── preamble.tex
├── sections/
│   ├── 00-portada.tex
│   ├── 00-resumen.tex
│   ├── 01-introduccion.tex
│   ├── 02-marco-teorico.tex
│   ├── 03-estado-del-arte.tex
│   ├── 04-marco-metodologico.tex
│   ├── 05-arquitectura.tex
│   ├── 06-implementacion.tex
│   ├── 07-resultados.tex
│   ├── 08-discusion.tex
│   ├── 09-conclusiones.tex
│   ├── 10-recomendaciones.tex
│   ├── 11-aspectos-legales.tex
│   └── 13-anexos.tex
```

**CRITICAL**: `Bibliography_base.bib` must be at the same level as `main.tex` (together at project root). The preamble references it as `../Bibliography_base.bib`. If using Overleaf's file picker, ensure the .bib is uploaded to the project root, NOT inside any subfolder.

## Compiler Configuration

1. In Overleaf, go to **Menu** (top left)
2. Set **Compiler** to **XeLaTeX**
3. Set **TeX Live version** to the latest available
4. Set **Main document** to `main.tex`

## Compilation Steps

1. Click **Recompile** 
2. First compilation may show warnings -- this is normal for BibLaTeX
3. If bibliography does not appear, compile AGAIN (BibLaTeX needs two passes: first for citations, second for bibliography rendering)
4. Click the **Logs and output files** button to inspect errors

## Font Note

The preamble configures **Arial** as the main font. If Arial is not available on Overleaf's servers:
- Try `\setmainfont{TeX Gyre Heros}` (Arial/Helvetica equivalent)
- Or `\setmainfont{Latin Modern Sans}` (fallback sans-serif)

## Common Issues and Fixes

| Error | Fix |
|-------|-----|
| `! Package babel Error: Unknown language 'spanish'` | Ensure XeLaTeX is selected (not pdfLaTeX) |
| `! LaTeX Error: File 'Arial' not found` | Change font to TeX Gyre Heros or install Arial |
| `! Package biblatex Error: Bibliography file not found` | Move Bibliography_base.bib to project root |
| Empty bibliography | Compile twice (BibLaTeX needs 2 passes) |
| `! Undefined control sequence` | Check for unescaped special chars (underscores in text) |

## After Successful Compilation

Download the PDF and save it as:
`docs/Tesis/v8 (IA)/paper/main.pdf`

## Alternative: Compile Locally

If you prefer to install MiKTeX or TeX Live locally:

```bash
# Install TeX Live (Windows: download from tug.org/texlive)
# Then compile:
cd docs/Tesis/v8 (IA)/paper
latexmk -xelatex main.tex
```

MiKTeX download (~2 GB): https://miktex.org/download
