# Tasks: Documentar la pseudonimización y reconciliar la redacción (change c-202)

Convenciones: `T12/` = `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`; `T11/` = `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex`; `T08/` = `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex`. Las secciones se nombran como "sección N (`archivo.tex`)". "D-n" remite a `design.md`.

**Reglas para todos los grupos.** No commitear, no pushear, no crear tags. No recompilar el PDF (`main.pdf`, `compilacion.md`). No modificar `App/`, `n8n/`, `evaluation/`, el clasificador, el corpus (`data/*.json`, `data/*.csv`) ni `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex`. No tocar las versiones archivadas `v8 (IA)` ni `v9 (IA)`. Gobernanza ALTA (privacidad y Ley 25.326): la redacción nueva solo puede hacer coincidir el texto con el artefacto verificado; no introducir afirmaciones nuevas sin respaldo ni cambiar ninguna cifra. No registrar el change en `CHANGES.md` (lo hace el apply en su cierre).

## 1. Reconocimiento y red de seguridad

- [x] 1.1 Confirmar el estado del corpus versionado: contar las etiquetas en `data/corpus_evaluacion_pseudonimizado.json` para `[EMAIL]`, `[TELEFONO]`, `[TARJETA]`, `[HOST]` y `[PERSONA]`, y comparar sus descripciones con el crudo `data/Corpus Tesis - Hoja 1.csv` ignorando espacios finales. Aceptación: 0 ocurrencias de cada etiqueta y 0 diferencias crudo/JSON; registrar los comandos y su salida en el reporte del apply.
- [x] 1.2 Auditar las afirmaciones sobre etiquetas en las secciones de la tesis: `rg -n "PERSONA|TELEFONO|HOST|EMAIL|TARJETA" "docs/Tesis/v10 (IA)/paper/sections/"`. Aceptación: queda registrada la lista de ocurrencias a corregir (sección 12 y sección 11), la confirmación de que la sección 07 cita `Su PC se reinicia a cada rato...` sin etiquetas, y la decisión por archivo (corregir o dejar igual).

## 2. Reconciliar la sección 12 (Anexo I, corpus)

- [x] 2.1 Reescribir la descripción del campo `descripcion` en la sección del Anexo I (`T12/`) para que afirme que la descripción ES el texto pseudonimizado producido por el módulo, que el módulo reemplaza los identificadores personales directos (nombres, correos, teléfonos, hosts internos, identificadores corporativos) por etiquetas genéricas, y que en el corpus del estudio no había identificadores directos, por lo que NO aparecen etiquetas (en lugar de afirmar que el corpus contiene `[EMAIL]`/`[TELEFONO]`/`[HOST]`/`[PERSONA]`). Aceptación: el texto no afirma que el corpus contiene etiquetas y el mecanismo queda descrito con precisión.
- [x] 2.2 Reescribir el párrafo de privacidad de la sección del Anexo I (`T12/`) para que declare que la pseudonimización se aplica a cada incidente en producción antes de su clasificación y persistencia, que el módulo es la herramienta que la produce, y que en este corpus no había identificadores personales directos. Aceptación: el párrafo conserva la remisión a la Ley 25.326 y no introduce afirmaciones nuevas sin respaldo.

## 3. Precisar la sección 11 (transferencia internacional)

- [x] 3.1 Precisar en `T11/`, en la subsección de transferencia internacional, que el módulo Python local es lo que pseudonimiza el texto antes de la llamada a Gemini y que en el corpus del estudio no había identificadores directos (por lo que no aparecen etiquetas), manteniendo la descripción del mecanismo y sin debilitar el encuadre legal sobre la transferencia internacional. Aceptación: la subsección conserva su estructura legal y agrega las dos precisiones; ninguna cifra cambia.

## 4. Documentar el hallazgo de c-201

- [x] 4.1 Agregar una nota factual y breve, según D2, en la sección del Anexo I (`T12/`): la heurística del pseudonimizador sobreenmascaraba términos no-persona (por ejemplo `Su PC`, `Adobe PDF Reader`, `Recursos Humanos`), `c-201` lo corrigió, y el corpus evaluado no se ve afectado porque se construyó con el texto corregido, por lo que repetir la clasificación es un no-op. Aceptación: la nota es factual, no presenta el hallazgo como falla del estudio, no cambia cifras ni conclusiones y no altera el conteo de limitaciones de la sección 08.

## 5. Reconciliar los documentos de soporte

- [x] 5.1 En `docs/pseudonymization.md`, confirmar que la frontera y `c-201` ya están documentados (secciones 6 y 6 bis) y, si falta, precisar que en el corpus del estudio no hay etiquetas porque no había identificadores directos y que repetir la corrida de clasificación es un no-op. Aceptación: `rg -n "no aparecen|0 etiquetas|no-op" docs/pseudonymization.md` devuelve la frontera del corpus del estudio.
- [x] 5.2 En `docs/anexo_f_corpus.md`, rotular como ilustrativo el ejemplo de esquema con `[HOST]`/`[PERSONA]` y aclarar que el corpus del estudio no contiene esas etiquetas. Aceptación: el ejemplo queda rotulado y la descripción del campo `descripcion` remite a la frontera real.
- [x] 5.3 En `docs/como_cargar_datos_corpus.md`, rotular como ilustrativos los ejemplos JSON y la tabla de tokens con `[PERSONA]`/`[HOST]`, y aclarar que el corpus del estudio no contiene esas etiquetas. Aceptación: cada ejemplo con etiquetas queda rotulado como ilustrativo del formato.

## 6. Verificación final y registro

- [x] 6.1 Ejecutar `openspec validate c-202-documentar-la-pseudonimizacion-y-reconciliar-la-redaccion --strict`. Aceptación: válido.
- [x] 6.2 Revisar el diff de los `.tex`: confirmar que no cambió ninguna cifra canónica y que `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` no fue modificado. Aceptación: `git diff --exit-code -- "docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex"` da exit code 0 y la revisión del diff no muestra cambios de cifras.
- [x] 6.3 Verificación de alcance: `git status --porcelain` debe mostrar solo los `.tex` indicados (`T12/`, `T11/`; `T08/` solo si se eligió esa ubicación), los documentos de soporte (`docs/pseudonymization.md`, `docs/anexo_f_corpus.md`, `docs/como_cargar_datos_corpus.md`) y los artefactos del change. Aceptación: confirmado; no cambiaron `App/`, `n8n/`, `evaluation/`, `data/*.json`, `data/*.csv`, `main.pdf` ni `compilacion.md`.
- [x] 6.4 Registrar el change en `CHANGES.md` con su fase, estado, scope, dependencias, gobernanza y "Leer antes" (lo realiza el apply en su cierre). Aceptación: `rg -n "c-202|documentar-la-pseudonimizacion" CHANGES.md` devuelve coincidencias.
