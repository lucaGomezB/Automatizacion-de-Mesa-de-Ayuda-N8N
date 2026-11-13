# Tasks: Arbitraje de los discordantes y refuerzo de clases chicas

Convenciones: `C/` = `docs/Tesis/Correcciones/`; `E/` = `evaluation/data/campana/`;
`R/` = `docs/campana-medicion/`. Los grupos 4 y 5 son trabajo de campo de los autores FUERA
del repositorio (el repositorio entrega protocolo, instrumentos y validador, y versiona los
resultados). NO se edita el código del clasificador (`App/Backend/app/classifiers`), el
corpus de ajuste (`data/*`) ni `evaluation/doble_etiquetado.py`. En la prosa usar
"sección N (`archivo.tex`)" (gitleaks).

## 0. Preparación y decisiones (bloqueante)

- [x] 0.1 Confirmar el estado: `git status` limpio, rama `change/c-206-arbitraje-de-los-discordantes-y-refuerzo-de-clases-chicas` y `openspec validate c-206-arbitraje-de-los-discordantes-y-refuerzo-de-clases-chicas --strict` pasa. Verificación: los tres comandos sin error.
- [ ] 0.2 Decisión de los autores: identificar al tercer etiquetador `E5` (código `P11`) y al custodio de identidades; confirmar que es independiente de `E1`-`E4`, `A1`, `T1`-`T3` y `O1`/`O2`. Verificación: la decisión queda registrada en el runbook sin nombres.
- [ ] 0.3 Decisión de los autores: volumen del refuerzo de `Sistemas` y `Bases de Datos`. Verificación: la cuota queda registrada en el runbook antes de reunir casos.

## 1. Protocolo e instrumentos

- [x] 1.1 Crear `R/runbook-arbitraje-discordantes.md` con: quién etiqueta (`E5`), qué ve (hoja ciega + plantilla `C1` + codebook congelado), la regla de arbitraje de dos y de tres vías, el conjunto laxo arbitrado, el refuerzo de clases, la aceptación y el versionado. Verificación: el runbook nombra `E5`, el cegado, la regla de tres vías, el refuerzo y el criterio de aceptación, cada paso con comando o artefacto.
- [ ] 1.2 Preparar el instrumento de arbitraje: hoja ciega de los `47` casos (solo `id_caso` y descripción) y una copia vacía de `evaluation/data/plantilla_etiquetado.csv`. Verificación: `head -1` de la hoja = `id_caso,descripcion`; 48 líneas.
- [x] 1.3 Actualizar `R/runbook-corpus-independiente.md` para remitir al arbitraje de los discordantes y al refuerzo. Verificación: la sección de referencia cruzada figura con su enlace.

## 2. Validador y constructor de la referencia arbitrada (TDD)

- [x] 2.1 (RED) Escribir `evaluation/tests/test_arbitraje.py` con pruebas que importen el módulo inexistente y verifiquen: la validación de una planilla con `E3`/`E4`/`E5`; el rechazo de una planilla con menos o más etiquetadores; y que la referencia de un caso discordante toma la etiqueta de `E5`; correr `cd App/Backend; ...` o `pytest` desde la raíz de `evaluation/` y verificar que fallan por módulo ausente.
- [x] 2.2 (GREEN) Crear `evaluation/arbitraje.py` con el validador (exactamente `E3`, `E4`, `E5`) y el constructor de la referencia arbitrada (referencia = consenso de `E3`/`E4` cuando coinciden; etiqueta de `E5` cuando difieren; bandera en la discordancia de tres vías); reutilizar los helpers de `evaluation/doble_etiquetado.py` cuando apliquen, sin cambiar su contrato; correr las pruebas de 2.1 y verificar que pasan.
- [x] 2.3 (TRIANGULATE) Agregar pruebas para el conjunto laxo arbitrado (intersección de adicionales de al menos dos de los tres) y para la bandera de tres vías; verificar que pasan.
- [x] 2.4 Verificar que `evaluation/doble_etiquetado.py` sigue aceptando exactamente dos etiquetadores para la tarea `doble_etiquetado` (su contrato intacto). Verificación: `python -m pytest evaluation/tests -q` pasa y la prueba del contrato de dos etiquetadores sigue verde.

## 3. Registro de sujetos

- [ ] 3.1 Agregar `E5,etiquetador,P11` a `E/registro_sujetos.csv`; comprobar que no hay solapes por `persona` y que no hay nombre/correo/legajo. Verificación: `validar_registro_sujetos` no reporta solape y las columnas quedan `alias,rol,persona`.

## 4. Campo: arbitraje y refuerzo (autores, fuera del repositorio)

- [ ] 4.1 Entregar a `E5` la hoja ciega, la plantilla `C1` y el codebook congelado; sin la etiqueta de `E3`, la de `E4`, la referencia ni predicciones. Verificación: el cegado queda registrado en `E/README.md` (`estado_cegado`).
- [ ] 4.2 Reunir los casos de refuerzo de `Sistemas` y `Bases de Datos` con ids nuevos prefijo `I`, disjuntos del corpus de ajuste. Verificación: existen los casos con su `sector_asignado` de referencia.
- [ ] 4.3 Etiquetar los casos de refuerzo con `E3`/`E4` (arbitraje `E5` si difieren) y unir la planilla del arbitraje. Verificación: la planilla unida valida con el validador de 2.2 (exit code `0`).
- [ ] 4.4 Versionar la tabla primaria del arbitraje `E/doble_etiquetado_arbitrado.csv` (LF, UTF-8 sin BOM) con su SHA-256. Verificación: `sha256sum` coincide con el declarado; `git status` sin cambios de fin de línea.
- [ ] 4.5 Construir el JSON FINAL `E/corpus_independiente_arbitrado.json` con la referencia arbitrada (consenso `E3`/`E4`; `E5` en los discordantes; bandera de tres vías) y su SHA-256. Verificación: `cargar_corpus` carga los `150` casos (más el refuerzo) con prefijo `['I']`; el hash queda en el README.

## 5. No solape, corrida paga y control de congelamiento

- [ ] 5.1 Correr `verificar_no_solape` entre `data/corpus_evaluacion_pseudonimizado.json` y `E/corpus_independiente_arbitrado.json` con `umbral_jaccard=0.8`; revisar a mano cada advertencia. Verificación: sin `SolapeError`; advertencias revisadas y registradas.
- [ ] 5.2 Control de clasificador congelado: `git diff bf5e099 HEAD -- App/Backend/app/classifiers docs/prompt_gemini.txt App/Backend/app/constants.py App/Backend/app/config/settings.py`; solo diferencias ajenas a la clasificación. Verificación: el diff se inspecciona y su resultado se anota para el README.
- [ ] 5.3 Clasificar con rutas propias: `PYTHONPATH=App/Backend python -m evaluation.run_evaluation --corpus E/corpus_independiente_arbitrado.json --predicciones E/predicciones_arbitrado.json --reporte E/reporte_arbitrado.md --confirm-paid`. Verificación: el cache trae `cache_meta` con `corpus_hash`, `corpus_count`, `classifier_version`, `generated_at`, `commit` y `pines`.
- [ ] 5.4 Confirmar que los artefactos de la v9 no cambiaron: `git status` no muestra `data/corpus_evaluacion_pseudonimizado.json`, `data/corpus_resultados*.json` ni `evaluation/report.md`. Verificación: `git status` limpio sobre esas rutas.

## 6. Artefactos, registro y análisis

- [ ] 6.1 Registrar en `E/README.md` el commit, el control de congelamiento (5.2), el `estado_cegado` y el SHA-256 de cada archivo nuevo. Verificación: la tabla SHA-256 queda completa y sin filas `pendiente`.
- [ ] 6.2 Correr `evaluar_fuera_de_muestra` con el cache arbitrado y reportar el n efectivo `150` sin exclusión y las métricas por clase de `Sistemas` y `Bases de Datos` estimables. Verificación: devuelve `obtenido=True` con el n efectivo `150`.
- [ ] 6.3 Registrar las cifras del corpus arbitrado en `C/numeros-canonicos.md` en una sección nueva, con procedencia y comando, conservando el resultado de c-191 sobre `103` rotulado como estimación con exclusión. Verificación: cada cifra nueva tiene archivo fuente y comando; ningún valor `vigente` previo cambia.

## 7. Validación y archivo

- [ ] 7.1 `openspec validate c-206-arbitraje-de-los-discordantes-y-refuerzo-de-clases-chicas --strict --no-interactive`. Verificación: imprime `is valid` (exit 0).
- [ ] 7.2 Archivar el change en `openspec/changes/archive/2026-MM-DD-c-206-arbitraje-de-los-discordantes-y-refuerzo-de-clases-chicas/` con las specs sincronizadas. Verificación: el directorio existe bajo `archive/`.
