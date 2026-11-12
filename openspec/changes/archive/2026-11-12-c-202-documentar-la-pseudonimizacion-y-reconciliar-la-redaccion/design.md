# Design: Documentar la pseudonimización y reconciliar la redacción (change c-202)

## Context

Ver `proposal.md` — Why. Estado verificado al proponer (2026-11-12):

- El corpus versionado `data/corpus_evaluacion_pseudonimizado.json` tiene **0** ocurrencias de `[EMAIL]`, `[TELEFONO]`, `[TARJETA]`, `[HOST]` y `[PERSONA]`; sus descripciones son equivalentes al crudo `data/Corpus Tesis - Hoja 1.csv` (0 diferencias ignorando espacios finales). Los 9 falsos positivos del módulo sobre el crudo se restauraron antes de versionar; `c-201` corrigió la heurística en el código.
- La sección 12 (`12-anexos.tex`, Anexo I, `sec:anexo-corpus`) afirma que la `descripcion` es "texto pseudonimizado, con los identificadores personales reemplazados por etiquetas genéricas como `[EMAIL]`, `[TELEFONO]`, `[HOST]` y `[PERSONA]`", y que las descripciones "han sido pseudonimizadas... reemplazando nombres propios, direcciones de correo y otros identificadores personales por etiquetas genéricas". Ambas afirmaciones sobreestiman lo que el artefacto contiene.
- La sección 11 (`11-aspectos-legales.tex`, `subsec:transferencia-internacional`) describe el mecanismo (el módulo local enmascara nombres, correos, teléfonos, identificadores corporativos y hosts con etiquetas como `[PERSONA]`, `[EMAIL]` o `[HOST]`). Es una descripción del mecanismo, válida; conviene precisar que el módulo es lo que pseudonimiza antes de la llamada a Gemini y que en el corpus del estudio no había identificadores directos.
- La sección 07 (`07-resultados.tex`) ya cita `Su PC se reinicia a cada rato...` (texto restaurado): es consistente, NO se toca.
- `docs/pseudonymization.md` ya documenta la frontera de `c-201` (secciones 6 y 6 bis); `docs/anexo_f_corpus.md` y `docs/como_cargar_datos_corpus.md` muestran `[PERSONA]`/`[HOST]` en ejemplos de esquema.
- No se recompila el PDF (`main.pdf`, `compilacion.md`): lo compilan los autores.

## Goals / Non-Goals

**Goals:**

- Hacer que el texto de la tesis coincida con el artefacto: la `descripcion` es la salida del módulo; en el corpus del estudio no había identificadores directos y por eso no aparecen etiquetas.
- Describir el mecanismo con precisión (módulo local antes de Gemini) sin debilitar el encuadre legal.
- Documentar el hallazgo de `c-201` de forma factual y breve, sin cambiar cifras ni conclusiones.
- Rotular los ejemplos de los documentos de soporte como ilustrativos.

**Non-Goals:**

- No se cambia ninguna cifra, métrica, ni los archivos del corpus (`data/*.json`, `data/*.csv`).
- No se toca `App/`, `n8n/`, `evaluation/` ni el clasificador.
- No se recompila el PDF.
- No se tocan las versiones archivadas `v8 (IA)` ni `v9 (IA)`.

## Decisions

### D1. Reconciliar por exactitud; no reescribir el mecanismo

Se conserva la descripción del mecanismo (qué enmascara el módulo) y se corrige únicamente la afirmación sobre el contenido del corpus del estudio. La nueva redacción debe decir que la descripción ES el texto pseudonimizado producido por el módulo, que el módulo reemplaza identificadores personales directos por etiquetas genéricas, y que en este corpus no había identificadores directos, por lo que **no aparecen etiquetas**. Se agrega que la pseudonimización se aplica al incidente en producción antes de su clasificación y persistencia. Alternativa descartada: eliminar toda mención a las etiquetas. Se descarta porque el mecanismo sí emite esas etiquetas y su documentación es correcta y necesaria (Ley 25.326); el problema es la afirmación sobre el corpus, no la del mecanismo.

### D2. Ubicación del hallazgo de `c-201`: nota precisa en el Anexo I

El hallazgo (la heurística sobreenmascaraba términos no-persona; `c-201` lo corrigió; el corpus evaluado no se ve afectado porque se construyó con el texto corregido, y repetir la clasificación es un no-op) se documenta como una nota factual y breve dentro de la sección del Anexo I sobre el corpus (sección 12, `12-anexos.tex`). Alternativa considerada: la subsección de limitaciones del estudio (sección 08, `08-discusion.tex`, `subsec:limitaciones-estudio`). Se descarta como ubicación primaria porque esa subsección declara expresamente "ocho limitaciones" y enumerarlas; insertar un ítem cambiaría ese conteo y enmarcaría la corrección ya resuelta como una falla del estudio, contra la indicación de no presentarla como tal. La nota del Anexo I queda junto al texto que se reconcilia y no altera el conteo.

### D3. Documentos de soporte: ejemplos rotulados como ilustrativos

Los ejemplos de esquema en `docs/anexo_f_corpus.md` y `docs/como_cargar_datos_corpus.md` (bloques JSON con `[HOST]`/`[PERSONA]` y tabla de tokens) se conservan porque ilustran el formato de pseudonimización, pero se rotulan como ilustrativos del formato y se aclara que el corpus del estudio no contiene esas etiquetas. Se agrega la remisión a `c-201` donde corresponda. Alternativa descartada: eliminar los ejemplos con etiquetas. Se descarta porque el esquema documenta el formato que el módulo puede emitir; borrarlos perdería información sin ganar exactitud.

### D4. No recompilar el PDF

El cambio no ejecuta la compilación ni regenera `main.pdf`/`compilacion.md`; los autores compilan. La verificación se limita a la validación de artefactos OPSX y a revisar el texto fuente.

### D5. Alcance del texto: no tocar `07-resultados.tex`

La sección 07 ya reproduce `Su PC se reinicia a cada rato...` (texto restaurado), consistente con el artefacto. No se modifica para no introducir cambios no solicitados ni mover cifras.

### D6. Gobernanza ALTA: solo coincidir, no afirmar de más

El cambio es de gobernanza ALTA (privacidad y Ley 25.326). Restricción dura: la redacción nueva solo puede hacer coincidir el texto con el artefacto verificado (0 etiquetas en el corpus versionado; equivalencia con el crudo). No se introducen afirmaciones nuevas sin respaldo (por ejemplo, no se promete cobertura universal de la pseudonimización ni se declara un impacto cuantificado de `c-201`).

## Risks / Trade-offs

- **Sobre-corrección que borre el mecanismo** → D1 conserva la descripción del mecanismo y corrige solo la afirmación sobre el corpus; la revisión verifica que ambas partes queden.
- **Enmarcar `c-201` como falla** → D2 lo ubica como nota factual en el Anexo I, sin alterar el conteo de limitaciones.
- **Ejemplos de esquema que sigan pareciendo literales** → D3 los rotula explícitamente como ilustrativos.
- **Cambiar una cifra por descuido** → verificación final compara el diff y confirma que no se tocan cifras ni `07-resultados.tex`.
- **Tocar archivos fuera de alcance** → verificación de alcance (`git status`) restringe el change a los `.tex` indicados y a los tres documentos de soporte.

## Migration Plan

No hay migración de datos: el cambio es editorial. Rollback: revertir los `.tex` de las secciones 12, 11 y 08 y los documentos de soporte. El corpus y las métricas no se tocan, por lo que el rollback no afecta la evidencia.

## Open Questions

None.
