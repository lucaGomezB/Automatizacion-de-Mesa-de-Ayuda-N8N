# Tasks: Validación fuera de muestra sobre 150 casos con el clasificador congelado

Convenciones: `C/` = `docs/Tesis/Correcciones/`; `S/` = `docs/Tesis/v10 (IA)/paper/sections/`;
`E/` = `evaluation/data/campana/`; `D` = `auditorias/Dictamen_Tesis_v10_v1.2.12_CONEAU_2026-11-09.md`.
Los grupos 1 a 5 son trabajo de campo de los autores FUERA del repositorio (el repositorio entrega
los instrumentos y versiona los resultados); el grupo 6 se aplica al cerrar el campo, salvo la
tarea 6.1 (residual Galup), que NO depende del campo y puede aplicarse de inmediato. No se edita
código de `App/`, `n8n/`, `evaluation/*.py` ni `analisis/`; sí se versionan artefactos nuevos en
`E/`. En la prosa del registro usar "sección N (`archivo.tex`)" (gitleaks).

## 0. Preparación y decisiones (bloqueante)

- [x] 0.1 Confirmar el estado: `git status` limpio, rama `change/c-191-validacion-fuera-de-muestra-150-casos`, y `openspec validate c-191-validacion-fuera-de-muestra-150-casos --strict` pasa. Verificación: los tres comandos sin error. **Verificado el 2026-11-12**: rama `change/c-191-validacion-fuera-de-muestra-150-casos` (con RamaLucaExtra integrada), sin cambios en archivos rastreados (solo quedan sin rastrear los `mensaje-para-lucas-*.md`, ajenos al change) y `openspec validate ... --strict` imprime `Change ... is valid`.
- [x] 0.2 **Decisión de los autores (design D2, RESUELTA el 2026-11-09, opción A)**: cuota **50 correo / 40 web / 60 telefonía**, con sobremuestreo de `Bases de Datos` (objetivo ≥ 10) y ponderación de la exactitud global por la composición del corpus de 200; registrada en `docs/campana-medicion/runbook-corpus-independiente.md` (sección 1). Verificación: la asignación quedó escrita en el runbook con su justificación y la nota de ponderación.
- [x] 0.3 **Decisión de los autores (design D3)**: confirmar los dos etiquetadores `E3`/`E4` y sus códigos `P<n>`; el director custodia la correspondencia fuera del repositorio. Verificación: las dos filas de `E/registro_sujetos.csv` están definidas sin nombres. **Verificado el 2026-11-12**: `registro_sujetos.csv` tiene `E3,etiquetador,P9` y `E4,etiquetador,P10` (sin nombres; correspondencia fuera del repositorio) y `validar_registro_sujetos` sobre el registro real con una planilla en memoria E1-E4 devuelve `('E1', 'E2', 'E3', 'E4')` sin solape por `persona` (ninguna persona repetida).
- [x] 0.4 Verificar los instrumentos con las fixtures sintéticas: `verificar_no_solape` sobre `evaluation/tests/fixtures/campana/corpus_independiente_fixture.json` imprime `sin solape`; `python -m evaluation.doble_etiquetado --planilla evaluation/tests/fixtures/campana/doble_etiquetado_fixture.csv --corpus evaluation/tests/fixtures/corpus_fixture.json --tarea doble_etiquetado` sale con exit code `0`. Verificación: ambos comandos con la salida esperada. **Verificado el 2026-11-12**: `sin solape; 0 advertencias` y `OK: planilla valida (tarea=doble_etiquetado, n_casos=9, n_registros=18, etiquetadores=E1,E2)` con exit code `0`.
- [x] 0.5 Control de clasificador congelado (design D5): `git diff bf5e099 HEAD -- App/Backend/app/classifiers docs/prompt_gemini.txt App/Backend/app/constants.py App/Backend/app/config/settings.py`; solo diferencias ajenas a la clasificación. Verificación: el diff se inspecciona y su resultado se anota para el README. **Verificado el 2026-11-12**: `bf5e099` resuelve (c-74, `hybrid-v3`); `docs/prompt_gemini.txt` sin diferencias; en `App/Backend/app/classifiers` solo docstrings/comentarios y el import perezoso del paquete (PEP 562, sin cambio de logica); en `constants.py` solo constantes ajenas (`CANAL_CORREO`, `ORIGEN_*` de c-165); en `settings.py` solo seguridad/autenticacion (claves, JWT, cookies, lockout, MFA, CORS), sin umbrales, modelo ni parametros de Gemini. Ninguna diferencia afecta la clasificacion.

## 1. Reunir y pseudonimizar el corpus independiente (campo)

- [ ] 1.1 Reunir 150 casos nuevos del organismo, disjuntos de los 200 del corpus de ajuste, según los estratos de 0.2. Verificación: existen 150 casos con ids `I001..I150` en el crudo.
- [ ] 1.2 Pseudonimizar con `python scripts/corpus_ingest/pseudonymize_corpus.py --csv <crudo.csv> --out <pseudonimizado.csv>` (mismo protocolo del corpus de ajuste; dominios internos con `--internal-domains`). Verificación: exit code `0`; revisión manual de una muestra sin PII visible.
- [ ] 1.3 Armar el JSON de TRABAJO (fuera del repositorio) con las descripciones pseudonimizadas y las cinco cadenas de sector canónicas; comprobar que carga con `cargar_corpus`. Verificación: `cargar_corpus` imprime 150 casos y `['I']`.
- [ ] 1.4 Armar la hoja ciega con solo `id_caso` y descripción (no se versiona; se genera fuera del repositorio o se borra al terminar). Verificación: `head -1` = `id_caso,descripcion`; 151 líneas.

## 2. Doble etiquetado con `E3` y `E4` (campo)

- [ ] 2.1 Entregar a cada etiquetador la hoja ciega, una copia vacía de `evaluation/data/plantilla_etiquetado.csv` y el codebook congelado; sin `sector_asignado`, sin predicciones y sin las etiquetas del otro. Verificación: el cegado queda registrado en `E/README.md` (`estado_cegado`).
- [ ] 2.2 Unir las dos planillas y validar: `python -m evaluation.doble_etiquetado --planilla doble_etiquetado_independiente.csv --corpus <corpus_independiente_trabajo.json> --tarea doble_etiquetado`. Verificación: exit code `0` con `n_casos=150`, `n_registros=300`, `etiquetadores=E3,E4`.
- [ ] 2.3 Versionar la tabla primaria `E/doble_etiquetado_independiente.csv` (LF, UTF-8 sin BOM) con su SHA-256 en `E/README.md`. Verificación: `sha256sum` coincide con el declarado; `git status` no muestra cambios de fin de línea.
- [ ] 2.4 Actualizar `E/registro_sujetos.csv` con `E3` y `E4` (`rol = etiquetador`, `P<n>` nuevos) y comprobar que no hay solapes por `persona`. Verificación: el script de detección de solapes imprime `sin solapes`.
- [ ] 2.5 Armar el JSON FINAL `E/corpus_independiente.json` con la referencia acordada (consenso de `E3`/`E4`) y su SHA-256. Verificación: `cargar_corpus` carga 150 casos y el hash queda en el README.

## 3. No solape (paso previo obligatorio)

- [ ] 3.1 Correr `verificar_no_solape` entre `data/corpus_evaluacion_pseudonimizado.json` y `E/corpus_independiente.json` con `umbral_jaccard=0.8`; revisar a mano cada advertencia de similitud. Verificación: sin `SolapeError`; advertencias revisadas y su decisión registrada.
- [ ] 3.2 Confirmar que los artefactos de la v9 no cambiaron: `git status` no muestra `data/corpus_evaluacion_pseudonimizado.json`, `data/corpus_resultados*.json` ni `evaluation/report.md`. Verificación: `git status` limpio sobre esas rutas.

## 4. Correr el clasificador congelado (corrida paga)

- [ ] 4.1 Clasificar con rutas propias: `PYTHONPATH=App/Backend python -m evaluation.run_evaluation --corpus E/corpus_independiente.json --predicciones E/predicciones_independiente.json --reporte E/reporte_independiente.md --confirm-paid`. Verificación: el cache trae `cache_meta` con `corpus_hash`, `corpus_count`, `classifier_version=hybrid-v3`, `generated_at`, `commit` y `pines`.
- [ ] 4.2 Registrar en `E/README.md` el commit y el resultado del control de congelamiento (0.5) y el SHA-256 de las predicciones y el reporte. Verificación: la tabla SHA-256 queda completa.

## 5. Análisis fuera de muestra

- [ ] 5.1 Correr `evaluar_fuera_de_muestra` con el cache independiente y la referencia in-sample de `E/README.md`. Verificación: devuelve `obtenido=True` con los bloques `in-sample` y `out-of-sample` y la comparabilidad del clasificador.
- [ ] 5.2 Calcular la exactitud estricta y laxa sobre el n efectivo con su IC de Wilson, el conteo de excluidos y las métricas globales con y sin ponderación (D2). Verificación: las cifras se reproducen con un script de solo lectura y se guardan en `E/analisis/`.
- [ ] 5.3 Registrar cada cifra del resultado en `C/numeros-canonicos.md` con su fuente y comando. Verificación: cada valor tiene archivo fuente y comando.

## 6. Actualización de la tesis (incluye el residual Galup)

- [x] 6.1 **Residual Galup (design D8; aplicado el 2026-11-09, no depende del campo)**: en `S/02-marco-teorico.tex` (2.1) la definición de ITSM quedó como definición general con `\parencite{Galup2009_itsm}` como panorama del campo; en `S/01-introduccion.tex` (1.2) se retiró "de Galup". Verificación: `rg -n "de Galup" S/01-introduccion.tex` = 0; Galup2009 se cita con `\parencite`; `verify_citations.py` PASS.
- [ ] 6.2 `S/07-resultados.tex` (`paragraph{Validación fuera de muestra.}`): reemplazar "no realizada" por el estado "realizada" con el resultado y su IC sobre el n efectivo. Verificación: `rg -n "no realizada" S/07-resultados.tex` = 0 en ese párrafo; el resultado figura con su IC.
- [ ] 6.3 `S/08-discusion.tex` (`subsec:interpretacion-resultados` y `subsec:limitaciones-estudio`): declarar la validación realizada con el mismo resultado, el n efectivo y la advertencia de sesgo de exclusión. Verificación: `rg -n "no realizada|no dispuso de un corpus independiente" S/08-discusion.tex` = 0; el resultado es idéntico al de 6.2.
- [ ] 6.4 `S/10-recomendaciones.tex` (`subsec:corpus-independiente` y la remisión de `subsec:clasificador-supervisado`): actualizar la recomendación para reflejar que la validación se realizó, conservando como futura la extensión a otros corpus. Verificación: `rg -n "continúa pendiente|no se realizó" S/10-recomendaciones.tex` = 0.
- [ ] 6.5 `S/00-resumen.tex` y el abstract: incorporar el resultado SOLO si amerita cambiar el veredicto de la sub-hipótesis de clasificación; sin sobreafirmar la confirmación. Verificación: cada uno ≤ 250 palabras con la regla registrada.
- [ ] 6.6 `C/dictamen-correcciones.md`: sección de c-191 con el cierre del dock (criterio 4), las decisiones D2/D3 y su estado. `S/12-anexos.tex` (`sec:anexo-trazabilidad`): actualizar la fila del límite estructural de la validación fuera de muestra a su cierre y la frase de cabecera. Verificación: el verificador de la matriz de trazabilidad no reporta fallas; el Anexo I compila.
- [ ] 6.7 Recompilar `main.pdf` en el entorno de registro, correr `verify_citations.py` y regenerar `compilacion.md`; registrar páginas y palabras. Verificación: sin errores fatales; `verify_citations.py` PASS; resumen y abstract ≤ 250 palabras.

## 7. Release y archivo

- [ ] 7.1 `openspec validate c-191-validacion-fuera-de-muestra-150-casos --strict --no-interactive`. Verificación: pasa.
- [ ] 7.2 Commit de contenido con las fuentes, los memos y los artefactos nuevos de `E/`; tag anotado `v1.3.0`; commit siguiente con el hash. Verificación: `git ls-tree v1.3.0 auditorias/` incluye el dictamen; `git diff --stat v1.3.0 HEAD -- S/` muestra solo la línea del hash. **Número de release definido por los autores (2026-11-12)**: `v1.3.0` es la release que se publica cuando el documento alcanza una puntuación estimada ≥ 9 con las correcciones que solicita la última auditoría del director.
- [ ] 7.3 `engram sync --project "Automatizacion-de-Mesa-de-Ayuda-N8N"` y PR contra `main`. Verificación: la sincronización no reporta secretos; el PR queda abierto.
- [ ] 7.4 Archivar el change en `openspec/changes/archive/2026-MM-DD-c-191-validacion-fuera-de-muestra-150-casos/`. Verificación: el directorio existe bajo `archive/`.
