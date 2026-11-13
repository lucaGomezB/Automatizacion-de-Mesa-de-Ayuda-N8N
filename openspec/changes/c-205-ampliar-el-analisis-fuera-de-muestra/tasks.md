# Tasks: Ampliar el análisis fuera de muestra

Convenciones: `C/` = `docs/Tesis/Correcciones/`; `S/` = `docs/Tesis/v10 (IA)/paper/sections/`;
`A/` = `evaluation/data/campana/analisis/`. Todo es solo lectura sobre los artefactos
versionados de c-191. NO se edita `App/`, `n8n/`, `evaluation/*.py` (solo se importan),
`data/*`, el corpus congelado ni `analisis/analisis_fuera_de_muestra_c191.py`. En la prosa
usar "sección N (`archivo.tex`)" (gitleaks).

## 1. Script de análisis (TDD)

- [x] 1.1 (RED) Escribir `A/test_analisis_fuera_de_muestra_c205.py` con una prueba que importe el módulo inexistente y verifique que el documento JSON trae macro-F1, *balanced accuracy*, kappa del clasificador, matriz `5x5` y los escenarios de exclusión; correr `cd evaluation/data/campana/analisis; python -m pytest test_analisis_fuera_de_muestra_c205.py -q` y verificar que falla por módulo ausente.
- [x] 1.2 (GREEN) Crear `A/analisis_fuera_de_muestra_c205.py` que reutilice `evaluation/metrics.py`, `evaluation/kappa.py` y `evaluation/stats.py`, consuma los artefactos de c-191 vía `cargar_corpus_solo_lectura` y escriba `A/analisis_fuera_de_muestra_c205.{json,md}` (LF, UTF-8 sin BOM); correr la prueba de 1.1 y verificar que pasa.
- [x] 1.3 (TRIANGULATE) Agregar casos a la prueba (macro-F1 con una clase de soporte cero y el cálculo del semi-ancho de Wilson) y verificar que pasan.
- [x] 1.4 Ejecutar el script dos veces y verificar salidas idénticas byte a byte y `git status` limpio; registrar los SHA-256 de `analisis_fuera_de_muestra_c205.json` y `.md`. Verificación: hashes estables entre corridas y sin archivos modificados por la ejecución.
- [x] 1.5 Verificar que el JSON declara: macro-F1 de las cinco clases; por clase precisión/sensibilidad/F1/soporte; *balanced accuracy*; kappa del clasificador con `p_o`/`p_e`/PABAK/`n`/IC; matriz `5x5`; semi-ancho de Wilson observado del n efectivo `103` frente al objetivo D1 (~8,4 pts); escenarios peor/mejor caso y cota con la regla de decisión; y el bloque de balance neto o su declaración de no computable. Verificación: cada campo presente en `analisis_fuera_de_muestra_c205.json`.
- [x] 1.6 Documentar en `A/README.md` el nuevo script, sus entradas versionadas, el comando y el método. Verificación: la sección nueva figura con comando reproducible.

## 2. Registro canónico (`C/`)

- [x] 2.1 Agregar la sección 3.20 del memo `C/numeros-canonicos.md` (posterior a 3.19) con macro-F1, métricas por clase con soporte, *balanced accuracy*, kappa del clasificador, matriz de confusión, potencia/precisión y escenarios de exclusión, cada valor con su procedencia (`A/analisis_fuera_de_muestra_c205.json`), su comando y su estado (`vigente`; escenarios de exclusión `condicional`). Verificación: toda cifra tiene archivo fuente y comando; la numeración de la Sección 3 sigue consecutiva.
- [x] 2.2 Agregar la entrada de upsert de c-205 al encabezado del memo y verificar que NO cambia ningún valor ni estado `vigente` de las Secciones 3.1 a 3.19. Verificación: `git diff` del memo limitado a la sección nueva y al encabezado; ningún valor previo modificado.
- [x] 2.3 Verificar que la regla de decisión de D6 figura explícita y ata el peor caso (`87/150 = 0,5800`) a la exactitud reportada. Verificación: la regla figura textual en la sección 3.20.

## 3. Prosa de la tesis (`S/`)

- [x] 3.1 `S/07-resultados.tex` (bloque fuera de muestra): agregar macro-F1, métricas por clase con soporte, *balanced accuracy* y kappa del clasificador, rotuladas como estimaciones sobre el n efectivo `103`, con los valores del memo. Verificación: las cifras figuran y coinciden con `C/numeros-canonicos.md`.
- [x] 3.2 `S/08-discusion.tex` (validación fuera de muestra / limitaciones): tratar explícitamente el sesgo de exclusión con los escenarios peor/mejor caso y la cota y la regla de decisión. Verificación: los escenarios y la regla figuran textuales; sin "no realizada".
- [x] 3.3 Verificar que ninguna sección presenta los escenarios como medición ni la macro-F1 fuera de muestra como equivalente de la exactitud estricta. Verificación: revisión de las secciones tocadas.
- [x] 3.4 Recompilar `main.pdf` en el entorno de registro, correr `verify_citations.py` y regenerar `compilacion.md`; registrar páginas y palabras. Verificación: sin errores fatales; `verify_citations.py` PASS; resumen y abstract ≤ 250 palabras.

## 4. Validación y cierre

- [x] 4.1 Correr `cd evaluation/data/campana/analisis; python -m pytest test_analisis_fuera_de_muestra_c205.py -q` y verificar que pasa. Verificación: exit 0.
- [x] 4.2 Correr `openspec validate c-205-ampliar-el-analisis-fuera-de-muestra --strict --no-interactive` y verificar que pasa. Verificación: imprime `is valid` (exit 0).
- [ ] 4.3 Archivar el change en `openspec/changes/archive/2026-MM-DD-c-205-ampliar-el-analisis-fuera-de-muestra/` con las specs sincronizadas. Verificación: el directorio existe bajo `archive/`.
