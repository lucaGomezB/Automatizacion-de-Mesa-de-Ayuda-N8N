## Why

> **Alcance actualizado tras rebasar sobre `main` (9d348c4).** La integración textual de la línea de base (método, tabla `tab:linea-base-clasica`, discusión, conclusiones y recomendaciones) la hizo c-210 y ya está en `main`. Este change conserva solo lo aditivo: el contraste pareado (script, prueba, salidas), su párrafo en `07-resultados.tex`, una cláusula en `08-discusion.tex` y otra en `09-conclusiones.tex`, el párrafo de método en `04-marco-metodologico.tex`, la sección 3.23 del memo y la trazabilidad. Lo que se descartó por duplicar a c-210 se marca "cubierto por c-210" más abajo y en `tasks.md`.

El dictamen CONEAU sobre v1.3.0 (`auditorias/Dictamen_Tesis_v10_v1.3.0_CONEAU_2026-11-13.md`) calificó el criterio 4 (Metodología, peso 20) con 7 y señaló que solo se mueve con evidencia nueva: el arbitraje de los 47 discordantes (c-206, bloqueado por un etiquetador humano) y una línea de base. c-209 y c-210 (PR #101, integrados) implementaron y midieron esa línea de base clásica (TF-IDF + regresión logística, 200 casos de ajuste, 103 casos fuera de muestra con consenso), pero deliberadamente no tocaron los `.tex`. Hoy la tesis contradice la evidencia del repositorio: afirma que no se comparó el esquema híbrido contra un clasificador supervisado (`10-recomendaciones.tex:14`, `08-discusion.tex:56`, `09-conclusiones.tex:47`). Este change integra la comparación en la tesis con una lectura honesta y acotada, y le agrega el contraste pareado que todavía falta.

## What Changes

- **Contraste pareado nuevo (aditivo)**: un script de análisis de solo lectura, determinista y con pruebas (TDD estricto), que reconstruye las predicciones por caso de la línea de base (semilla 42, mismo módulo de c-209), lee las predicciones por caso versionadas del híbrido (`predicciones_independiente.json`) y calcula sobre los mismos 103 casos la tabla 2×2 de aciertos, el contraste de McNemar (`evaluation/stats.py::contraste_mcnemar`, ya existente) y un intervalo de confianza de la diferencia de exactitudes pareadas. Versiona un JSON/MD con las predicciones por caso de la línea de base y el contraste, con SHA-256. Hoy ningún artefacto contiene un contraste pareado ni las predicciones por caso de la línea de base.
- **[Se conserva]** **Tesis, marco metodológico** (`04-marco-metodologico.tex`): párrafo nuevo con el protocolo de la línea de base (qué es y qué no es, entrenamiento con los 200 casos, prueba en los 103, control de filtración, variantes, contraste pareado).
- **[Reducido; la subsección y la tabla las cubre c-210 (`tab:linea-base-clasica`)]** **Tesis, resultados** (`07-resultados.tex`): solo un párrafo corto de contraste pareado tras esa tabla. Plan original descartado: subsección nueva con una tabla línea de base frente a híbrido sobre los mismos 103 casos y el contraste pareado; toda cifra sale de artefactos versionados.
- **[Reducido; la reescritura la cubre c-210]** **Tesis, discusión** (`08-discusion.tex`): solo una cláusula sobre la significación del contraste. Plan original descartado: reescribir la limitación quinta (ya no "no se comparó"), lectura acotada del resultado y amenazas a la validez de la comparación.
- **[Reducido; lo cubre c-210]** **Tesis, conclusiones y recomendaciones**: solo una cláusula en `09-conclusiones.tex`; `10-recomendaciones.tex` queda como en `main`. Plan original descartado (`09-conclusiones.tex`, `10-recomendaciones.tex`, y donde corresponda `01-introduccion.tex`, `00-resumen.tex`): corregir toda frase que niegue la existencia de la comparación; el trabajo futuro pasa a ser lo que falta (brazo solo-LLM, más datos de entrenamiento, modelos supervisados más fuertes, prueba con n = 150 arbitrado).
- **Trazabilidad**: sección nueva 3.23 en `numeros-canonicos.md` (la 3.22 es de c-210), entrada en `dictamen-correcciones.md`, FASE 69 en `CHANGES.md`, regeneración de `tesis_para_agente.md`, `verify_citations.py` (se reutilizan `Pedregosa2011_scikit_learn` y `McNemar1947_sampling_error`, ya presentes en `Bibliography_base.bib`).
- **No se modifica** ningún número canónico, el clasificador de producción, los corpus ni los artefactos de c-205/c-210. Todo es aditivo.

## Capabilities

### New Capabilities
- `evaluation-baseline-paired-contrast`: contraste pareado (McNemar e intervalo de la diferencia) entre la línea de base clásica y el híbrido sobre los mismos casos, con predicciones por caso versionadas.
- `tesis-baseline-integration` (alcance reducido a la parte aditiva del contraste pareado; el resto lo cubre c-210): integración de la línea de base en el texto de la tesis (método, resultados, discusión, conclusiones y trabajo futuro) con lectura acotada, cifras trazables y eliminación de las afirmaciones de inexistencia.

### Modified Capabilities
- (ninguna: las capacidades `tesis-document` y `tesis-numeros-canonicos` se usan sin cambiar sus requisitos; el memo recibe una sección aditiva.)

## Impact

- Código nuevo: `evaluation/data/campana/analisis/contraste_linea_de_base_c213.py` y su prueba; artefactos `contraste_linea_de_base_c213.{json,md}` y `SHA256SUMS`.
- Tesis: `docs/Tesis/v10 (IA)/paper/sections/{00-resumen,01-introduccion,04-marco-metodologico,07-resultados,08-discusion,09-conclusiones,10-recomendaciones}.tex` (solo los de la lista reducida de arriba).
- Documentación: `docs/Tesis/Correcciones/numeros-canonicos.md`, `docs/Tesis/Correcciones/dictamen-correcciones.md`, `CHANGES.md`, `docs/Tesis/v10 (IA)/tesis_para_agente.md`.
- Sin dependencias nuevas (scikit-learn y SciPy ya están en uso). Sin red, sin Gemini, sin API paga.
- El PDF (`main.pdf`) no se recompila en este change: lo recompila el dueño con Docker al final (tarea manual).
- Gobernanza: MEDIUM (texto de la tesis evaluada por el tribunal, con checkpoints), LOW para el script de solo lectura.
