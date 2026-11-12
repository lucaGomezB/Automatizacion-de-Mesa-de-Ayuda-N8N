## Why

El tribunal de segunda instancia (devolución del 11-11-2026 sobre `v1.2.18`) declaró que "la defensa se evaluará sobre el ejemplar corregido y sobre las respuestas del grupo a la Sección 8". Esa sección enumera 16 preguntas probables en cuatro bloques (procedencia de los datos, contraste de tiempos, clasificación y supervisión humana, marco legal) y recomienda una respuesta escrita para cada una. El change `c-196` ya atendió las 16 observaciones N-01..N-16 en el texto, pero el documento de respuestas no existe: sin él, la defensa carece del artefacto que el tribunal declaró evaluable.

## What Changes

- Nuevo documento de repositorio `docs/defensa/respuestas-tribunal.md`: 16 respuestas (Q1..Q16), una por pregunta, agrupadas en los cuatro bloques de la Sección 8, cada una fundamentada y verificable contra artefactos versionados (corpus, predicciones, doble etiquetado, brazo manual, intervenciones) y con cifras recalculables.
- Nuevo Anexo J en `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`: incorpora el documento como anexo de la tesis; la serie de anexos pasa de A–I a A–J.
- `docs/Tesis/Correcciones/numeros-canonicos.md`: registra todo valor que las respuestas citen y que no esté ya en el memo, con procedencia y estado.
- `docs/Tesis/Correcciones/dictamen-correcciones.md`: registro de trazabilidad del change.
- `CHANGES.md`: entrada de fase.
- Hechos a aprovechar en las respuestas: el κ = 0,87 se retiró (su origen fue un oversight sin respaldo); la versión de julio (3-7-2026) reportó un corpus sintético; el período relevado es 16/06–10/09/2026 (muestreo por conveniencia); el registro primario de los 119 tiempos se versionó (118/119; `R001` sin registro); las llamadas del brazo telefónico de la campaña complementaria las recitaron `O1`/`O2`, y las 81 de 2026-10, un autor.
- El documento NO se atribuye a un modelo de lenguaje; español neutro, sin emojis, sin atribución de IA.
- **Fuera de alcance:** artefactos de release (tag, versión, hash); nuevas mediciones; `App/`, `n8n/`, `docker/`, `evaluation/`; el change activo `c-191`.

## Capabilities

### New Capabilities
- `tesis-defensa`: contrato del documento de respuestas del grupo a las 16 preguntas del tribunal (Q1..Q16): estructura en cuatro bloques, verificabilidad de cada respuesta contra artefactos versionados, uso exclusivo de cifras canónicas o recalculables, y prohibición de atribución a un modelo de lenguaje.

### Modified Capabilities
- `tesis-document`: se agrega el Anexo J (incorporación del documento de respuestas) y se extiende la enumeración de anexos con contenido real; el anexo reutiliza los valores canónicos.
- `tesis-numeros-canonicos`: se registran los valores que las respuestas citen y que no estén ya en el memo, con procedencia y estado.

## Impact

- Documento nuevo: `docs/defensa/respuestas-tribunal.md`.
- Tesis: `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexo J); PDF recompilado (`main.pdf`, `compilacion.md`).
- Registro: `docs/Tesis/Correcciones/{numeros-canonicos,dictamen-correcciones}.md`; `CHANGES.md`.
- Código: ninguno. No se tocan `App/`, `n8n/`, `docker/` ni `evaluation/`.
- Gobernanza: documento de respuestas MEDIUM; el bloque legal (Q15, Q16) HIGH en lo que afirma sobre hechos.
