# latexmkrc — Project build configuration
# Works locally (latexmk) and on Overleaf (reads this file automatically).
# Overleaf ignores $pdf_mode — compiler is set via the project menu.

# Use XeLaTeX (mode 5)
$pdf_mode = 5;
$postscript_mode = $dvi_mode = 0;

# Search paths for preambles and bibliography
ensure_path('TEXINPUTS', './preambles//');
ensure_path('BIBINPUTS', '..//');

# Silence — stop on errors but don't pause
$xelatex = 'xelatex -interaction=nonstopmode %O %S';
