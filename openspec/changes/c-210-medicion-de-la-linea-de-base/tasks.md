# Tasks: Medicion de la linea de base

Convenciones: `E/` = `evaluation/`; `C/` = `openspec/changes/c-210-medicion-de-la-linea-de-base/`;
`A/` = `evaluation/data/campana/analisis/`. Todo es solo lectura sobre los artefactos
versionados. NO se edita `App/`, `n8n/`, el clasificador de produccion, los corpus, los numeros
canonicos, `CHANGES.md`, los `.tex` ni changes ajenas.

## 1. Ejecucion y artefactos

- [ ] 1.1 Correr la linea de base con `python3 -m evaluation.linea_de_base --salida C/` y verificar que termina sin red y escribe `linea_de_base_clasica_c210.json`, `linea_de_base_clasica_c210.md` y `SHA256SUMS.txt`. Verificacion: los tres archivos existen en `C/`.
- [ ] 1.2 Correr la medicion una segunda vez y verificar que las salidas son identicas byte a byte; registrar los SHA-256. Verificacion: `sha256sum` coincide entre corridas.
- [ ] 1.3 Verificar que el JSON trae las metricas globales y por clase de ambas variantes (`balanced` y `none`), la matriz `5x5`, la lectura muestral y la ponderada, los hashes de entradas y salidas y la declaracion aditiva. Verificacion: cada campo figura en el JSON.
- [ ] 1.4 Verificar que el JSON cita el hibrido desde `A/analisis_fuera_de_muestra_c205.json` sin recalcularlo. Verificacion: las cifras del hibrido coinciden con el artefacto de c-205.
- [ ] 1.5 Verificar que la corrida no modifica ningun corpus, prediccion ni archivo ajeno. Verificacion: `git status` sin cambios en artefactos versionados ajenos.

## 2. Comparacion

- [ ] 2.1 Armar la tabla comparativa linea de base vs hibrido sobre los mismos `103` casos con exactitud estricta, exactitud laxa, macro-F1, balanced accuracy y F1 por clase con soporte. Verificacion: la tabla trae las cinco metricas y las cinco clases para ambos sistemas.
- [ ] 2.2 Reportar la lectura muestral y la lectura ponderada a la prevalencia natural, ambas rotuladas. Verificacion: las dos lecturas figuran con su procedencia.
- [ ] 2.3 Verificar que `Sistemas` figura como clase debil del hibrido (`F1 0.2222`, soporte `5`) y `Bases de Datos` como su mejor clase (`F1 0.963`, soporte `13`), sin transferir esos rotulos a la linea de base. Verificacion: los rotulos estan atados al hibrido y la F1 de la linea de base se reporta aparte.
- [ ] 2.4 Declarar el veredicto honesto: si la linea de base ayuda o perjudica el caso de la tesis, con las cifras exactas medidas y sin maquillaje. Verificacion: el veredicto figura con las cifras y no oculta un resultado desfavorable.

## 3. Borrador de tesis

- [ ] 3.1 Escribir el borrador de seccion en `C/borrador_07-resultados_linea_de_base.md` con la estructura y el tono de `07-resultados.tex`, la tabla comparativa y las notas metodologicas. Verificacion: el borrador existe y contiene la tabla y la procedencia de cada cifra.
- [ ] 3.2 Verificar que el borrador declara que es un insumo para el dueno de la tesis y que no se edito ningun `.tex`. Verificacion: `git diff --name-only` no incluye archivos `.tex`.

## 4. Validacion y cierre

- [ ] 4.1 Correr `openspec validate c-210-medicion-de-la-linea-de-base --strict --no-interactive` y verificar que imprime `is valid` con exit 0. Verificacion: validacion estricta aprobada.
- [ ] 4.2 Correr `cd evaluation && python -m pytest tests/test_linea_de_base.py -q` y verificar exit 0. Verificacion: las pruebas del modulo siguen pasando.
- [ ] 4.3 Revisar `git diff --stat` y confirmar que no se modifico ningun archivo ajeno ni `.engram/`. Verificacion: solo se agregaron los artefactos de la change.
