#==============================================================================
# Dockerfile — build de la tesis (v9) con XeLaTeX + fuentes Microsoft core
#
# Por que existe: el host no tiene TeX instalado, y el preambulo de la tesis usa
# \setmainfont{Arial} / \setmonofont{Courier New} (fontspec). XeTeX NO resuelve
# esas familias por sustitucion de fontconfig (los clones metricos como
# Liberation/Arimo no sirven por nombre), asi que hay que instalar las familias
# REALES: de ahi ttf-mscorefonts-installer (paquete de `contrib`).
#
# Construir una vez (el contexto no se usa; -f y contexto apuntan al paper):
#   docker build -t texlive-thesis -f "docs/Tesis/v9 (IA)/paper/Dockerfile" "docs/Tesis/v9 (IA)/paper"
#
# Compilar (montar el directorio PADRE "v9 (IA)" porque latexmkrc fija
# BIBINPUTS=..// y Bibliography_base.bib vive un nivel arriba de paper/):
#   docker run --rm \
#     -v "$PWD/docs/Tesis/v9 (IA)":/work -w /work/paper \
#     texlive-thesis latexmk main.tex
#
# Verificar: pdfinfo "docs/Tesis/v9 (IA)/paper/main.pdf" | grep Pages
#==============================================================================
FROM texlive/texlive

RUN sed -i 's/Components: main/Components: main contrib/' /etc/apt/sources.list.d/debian.sources \
    && echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections \
    && apt-get update \
    && apt-get install -y --no-install-recommends fontconfig ttf-mscorefonts-installer \
    && fc-cache -f \
    && rm -rf /var/lib/apt/lists/*
