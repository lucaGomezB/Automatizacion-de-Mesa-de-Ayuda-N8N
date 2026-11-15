## 0. Coordinación y preparación

- [ ] 0.1 Confirmar con `openspec list --json` que ningún otro change activo (hoy c-226) reclama la sección del memo; registrar el estado en la bitácora del change.
- [ ] 0.2 Leer `docs/Tesis/Correcciones/analisis-limitaciones-estructurales-v1.4.1.md` (P2), `contraste_linea_de_base_c213.py` y `analisis_sesgo_corpus_referencia_c219.json` y confirmar que las tres particiones son derivables; registrar la confirmación.
- [ ] 0.3 Verificar con `python3` que los artefactos reproducen las anclas del diseño (`142/206`, `109/142`, `112/150`, `101/206`, `88/206`); registrar el resultado.
- [ ] 0.4 Ejecutar `git diff` sobre `evaluation/`, `App/` y `n8n/` para confirmar que no hay trabajo en curso que colisione; registrar.
- [ ] 0.5 Fijar el número de la sección aditiva del memo (esperado `3.36`) sobre `numeros-canonicos.md` y dejarlo anotado en la bitácora.

## 1. Análisis offline con TDD

- [ ] 1.1 Escribir `evaluation/data/campana/analisis/test_analisis_robustez_linea_de_base_c225.py` con casos sintéticos para las funciones puras (derivación de los tres subconjuntos, contraste por subconjunto y verificación de anclas) y ver los tests fallar (RED).
- [ ] 1.2 Implementar en `analisis_robustez_linea_de_base_c225.py` la derivación de subconjuntos (`consenso_e3_e4`, `original_150`, `arbitrado_completo`) y ver los tests pasar (GREEN).
- [ ] 1.3 Implementar el contraste por subconjunto y variante reutilizando `evaluation.stats.contraste_mcnemar` y el bootstrap de `evaluation.metrics` (semilla `20261021`, `10000` remuestreos) y ver los tests pasar.
- [ ] 1.4 Implementar la verificación de anclas y el aborto sin escribir ante discrepancia; triangular con al menos un caso de ancla fallida y un subconjunto de cardinalidad incorrecta.
- [ ] 1.5 Ejecutar el script sobre los artefactos reales y confirmar que reproduce las anclas y escribe `.json`, `.md` y `.SHA256SUMS.txt`; verificar el determinismo corriendo dos veces y comparando SHA-256.
- [ ] 1.6 Refactorizar sin cambiar comportamiento y volver a correr `pytest` de `evaluation/data/campana/analisis/test_analisis_robustez_linea_de_base_c225.py` en verde.

## 2. Artefactos y documentación de la carpeta

- [ ] 2.1 Verificar que el `.md` generado contiene la brecha y el IC de los tres subconjuntos y la declaración aditiva; ajustar el render si hace falta y volver a correr el script.
- [ ] 2.2 Agregar la entrada del script y sus salidas al `README.md` de `evaluation/data/campana/analisis/` y verificar que la tabla de artefactos lo lista.

## 3. Memo canónico

- [ ] 3.1 Redactar la sección aditiva (`3.36`) en `docs/Tesis/Correcciones/numeros-canonicos.md` con cada cifra, su fuente y su comando, en estado `vigente (nuevo)`; verificar que la sección `3.35` queda intacta.
- [ ] 3.2 Declarar en la sección `3.36` que la cifra primaria `0,6893/206`, el macro-F1 `0,7024` y el veredicto del umbral `0,85` no cambian; verificar con `rg "0,6893"` que no se alteró ninguna línea de las secciones `3.1` a `3.35`.

## 4. Prosa de la tesis

- [ ] 4.1 Agregar la tabla o párrafo de robustez en `07-resultados.tex` junto a `tab:linea-base-clasica`, con la fuente y el rótulo de sensibilidad; verificar que las cifras coinciden con la sección `3.36` del memo.
- [ ] 4.2 Actualizar la limitación sobre la comparación con clasificadores alternativos en `08-discusion.tex` con la lectura acotada; verificar el toque condicional en la limitación séptima y aplicarlo solo si aporta.
- [ ] 4.3 Compilar el PDF y verificar que no hay errores ni referencias indefinidas; medir `abspage@last` y registrar el delta de páginas en el libro mayor de `dictamen-correcciones.md`, compensando en el mismo bloque si hace falta.
- [ ] 4.4 Verificar con `rg -n "c-[0-9]{3}" "docs/Tesis/v10 (IA)/paper/sections"` que no quedan identificadores internos fuera de comentarios y con `python3 docs/Tesis/Correcciones/verify_citations.py` (o el verificador vigente) que las citas están en verde.

## 5. Trazabilidad y verificación

- [ ] 5.1 Registrar la entrada y la matriz de trazabilidad de c-225 en `docs/Tesis/Correcciones/dictamen-correcciones.md` con archivo:línea, ancla y fragmento verificable de cada artefacto; verificar el ancla de cada fila con `rg`.
- [ ] 5.2 Ejecutar `openspec validate c-225-robustez-de-la-linea-de-base-frente-a-la-referencia --strict` y confirmar que pasa.
- [ ] 5.3 Verificar el cierre: la cifra primaria y el veredicto del umbral sin cambios, los tres subconjuntos reportados con IC, y el script determinista; registrar la evidencia en la bitácora del change.
