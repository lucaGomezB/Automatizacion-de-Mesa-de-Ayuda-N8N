## Why

La tesis describe el campo `descripcion` del corpus como "texto pseudonimizado, con los identificadores personales reemplazados por etiquetas genéricas como `[EMAIL]`, `[TELEFONO]`, `[HOST]` y `[PERSONA]`". Esa afirmación no coincide con el artefacto: el corpus versionado `data/corpus_evaluacion_pseudonimizado.json` tiene **0** ocurrencias de cualquiera de esas etiquetas, y sus descripciones son equivalentes (0 diferencias ignorando espacios finales) al crudo; el módulo no halló PII genuina en los incidentes. Además, la corrección del sobreenmascarado del pseudonimizador (`c-201`) no está documentada en la tesis. La redacción debe reconciliarse con el artefacto.

## What Changes

- Reconciliar la `descripcion` del campo y el párrafo de privacidad en la sección 12 (`12-anexos.tex`, Anexo I corpus): la descripción ES el texto pseudonimizado producido por el módulo; el módulo reemplaza identificadores personales directos por etiquetas; en el corpus del estudio no había identificadores directos, por lo que **no aparecen etiquetas**; la pseudonimización se aplica en producción antes de clasificar.
- Precisar en la sección 11 (`11-aspectos-legales.tex`, transferencia internacional) que el módulo local es lo que pseudonimiza antes de la llamada a Gemini y que en el corpus del estudio no había identificadores directos; sin debilitar el encuadre legal.
- Documentar el hallazgo de `c-201` en la sección 08 (`08-discusion.tex`): la heurística sobreenmascaraba términos no-persona (`Su PC`, `Adobe PDF Reader`, `Recursos Humanos`); `c-201` lo corrigió; el corpus evaluado no se ve afectado y repetir la clasificación es un no-op. Factual y breve; no como falla del estudio.
- Reconciliar los documentos del repositorio (`docs/pseudonymization.md`, `docs/anexo_f_corpus.md`, `docs/como_cargar_datos_corpus.md`): dejar la frontera correcta y rotular los ejemplos con `[PERSONA]`/`[HOST]` como ilustrativos del formato.

**BREAKING**: ninguna. No cambia ninguna cifra, métrica ni artefacto de datos.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tesis-document`: se agrega el requisito de que la tesis describa la pseudonimización de forma consistente con el artefacto (descripción = salida del módulo, sin afirmar etiquetas inexistentes en el corpus del estudio) y documente el hallazgo de `c-201` sin alterar cifras.

## Impact

- Tesis: sección 12 (`12-anexos.tex`), sección 11 (`11-aspectos-legales.tex`), sección 08 (`08-discusion.tex`).
- Documentos: `docs/pseudonymization.md`, `docs/anexo_f_corpus.md`, `docs/como_cargar_datos_corpus.md`.
- No se toca: `App/`, `n8n/`, `evaluation/`, el clasificador, el corpus (`data/*.json`, `data/*.csv`), `07-resultados.tex`, ni las versiones archivadas de la tesis.
- No se recompila el PDF (`main.pdf`, `compilacion.md`): compilan los autores.
- Gobernanza: ALTA (afirmaciones sobre privacidad y Ley 25.326). El cambio solo hace que el texto coincida con el artefacto; no introduce afirmaciones nuevas sin respaldo.
- Métricas: sin cambios.
