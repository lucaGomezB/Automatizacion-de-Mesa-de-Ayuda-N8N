# Tasks: Calibración y punto de operación del gate de confianza

Convenciones: `A/` = `evaluation/data/campana/analisis/`; `E/` = `evaluation/data/campana/`;
`C/` = `docs/Tesis/Correcciones/`. Strict TDD. NO se edita `App/Backend/`,
`openspec/config.yaml`, el prompt, `data/*` ni las cachés existentes. Sin red, sin Gemini, sin
Docker. En la prosa usar «sección N (`archivo.tex`)» (gitleaks). **[AUTORES]**/**[LATEX]** marcan
lo que requiere intervención humana. Alcance de esta aplicación: 0 a 4, 5.1 y 6.1 a 6.3; 5.2 y 5.3 quedan
pendientes (no se edita ningún `.tex`: hay otro PR abierto sobre las secciones 7, 8 y 9).

## 0. Preparación y prerregistro (bloqueante)

- [x] 0.1 Confirmar estado: rama propia, `git status` limpio y `openspec validate c-214-calibracion-y-punto-de-operacion-del-gate-de-confianza --strict` en verde.
- [x] 0.2 Red de seguridad: `cd evaluation; python -m pytest -q` y `python -m pytest evaluation/data/campana/analisis -q`; anotar el conteo base; fallas previas se reportan, no se corrigen.
- [x] 0.3 Congelar D2-D5 en el docstring de `A/analisis_calibracion_gate_c214.py` antes de calcular ninguna métrica, junto con la declaración de no ceguera del `design.md`. Verificación: el commit del prerregistro precede al de las salidas.
- [x] 0.4 Detectar insumos opcionales: predicciones de un brazo Gemini solo (change futuro, no propuesto todavía) y corpus arbitrado de c-206 (aún inexistente). Verificación: cada secundario queda anotado como «ejecutable» o «no ejecutado».

## 1. Métricas puras — TDD

- [x] 1.1 (RED) `evaluation/tests/test_calibracion_gate.py`: pruebas que importan `evaluation.calibracion_gate` (inexistente) para `auroc` (orden perfecto = 1,0; señal constante = 0,5; empates a 0,5), `ece` (señal calibrada = 0,0; 10 bandas), `brier` y `sobreconfianza`. Verificar que fallan por módulo ausente.
- [x] 1.2 (GREEN) Implementar las cuatro funciones. Verificación: en verde.
- [x] 1.3 (TRIANGULATE) Casos con todos aciertos, todos errores (AUROC no definido → `None` explícito), una sola observación y valores fuera de [0; 1] (rechazo). Verificación: en verde.
- [x] 1.4 (RED/GREEN) `ic_bootstrap_metrica` con `SEMILLA_BOOTSTRAP`/`REMUESTREOS_BOOTSTRAP` reutilizando `remuestreos_indices` y `percentil_intervalo` de `evaluation/metrics.py`; dos corridas dan el mismo IC. Verificación: en verde.

## 2. Barrido y regla de selección — TDD

- [x] 2.1 (RED) Pruebas de `barrido_umbral` (cobertura, exactitud selectiva con Wilson, errores atrapados, carga de revisión del sistema; umbral vigente sin derivaciones; «derivar todo») y de `seleccionar_umbral` (menor `t` con exactitud `≥ φ` y ≥ 10 aceptados; `ninguno` si no hay). Verificar que fallan.
- [x] 2.2 (GREEN) Implementar. Verificación: en verde.
- [x] 2.3 (RED/GREEN) Pruebas de `evaluar_fuera_de_muestra_gate`: `confirmado`, `no confirmado` y `no estimable` con datos sintéticos, y que la función no acepta reelegir el umbral. Implementar. Verificación: en verde.
- [x] 2.4 (RED/GREEN) Recalibración isotónica ajustada en un conjunto y aplicada a otro, solo para ECE/Brier; prueba de que no cambia el orden (AUROC idéntico). Verificación: en verde.
- [x] 2.5 (REFACTOR) Limpieza; suite en verde tras cada paso.

## 3. Señales de las reglas recomputadas — costo cero

- [x] 3.1 (RED) Prueba de `recomputar_senales_reglas` con un clasificador determinístico simulado: devuelve `score_correctitud`, sector ganador (o `None`) y categoría de acuerdo con Gemini (acuerdo / desacuerdo / sin predicción). Verificar que falla.
- [x] 3.2 (GREEN) Implementar con `DeterministicClassifier` real importado de forma diferida (`PYTHONPATH=App/Backend`). Verificación: en verde.
- [x] 3.3 Prueba de integración: el recómputo sobre los 200 y los 103 reproduce exactamente la etapa y el sector de los casos cortocircuitados de las cachés versionadas (131/131 y 69/69). Si no, detener y reportar la deriva.
- [x] 3.4 Persistir `E/senales_reglas_c214.csv` (`caso_id`, `corpus`, `score_correctitud`, `sector_reglas`, `acuerdo_con_gemini`) con LF y SHA-256 en `E/README.md`. Verificación: una fila por caso; hash coincide.

## 4. Análisis y salidas

- [x] 4.1 (RED/GREEN) Test hermano `A/test_analisis_calibracion_gate_c214.py`: el JSON contiene, por etapa y corpus, fiabilidad, ECE, Brier, sobreconfianza, AUROC con IC, el barrido, `t*` y su evaluación fuera de muestra, S1 y S2 con su resultado de tres vías y los secundarios marcados ejecutados o no; dos ejecuciones dan el mismo SHA-256. Implementar `A/analisis_calibracion_gate_c214.py`.
- [x] 4.2 Generar `A/analisis_calibracion_gate_c214.{json,md}` y registrar sus SHA-256 en `A/README.md` y `A/SHA256SUMS.txt`.
- [ ] 4.3 Suite completa de `evaluation/` y `A/`: conteo base + pruebas nuevas, sin regresiones.

## 5. Registro canónico y tesis

- [ ] 5.1 Sección nueva en `C/numeros-canonicos.md` con cada cifra, archivo y comando, la declaración de no ceguera y, si alguna política quedó `confirmada`, la recomendación para un change posterior (gobernanza HIGH). Verificación: ningún valor `vigente` previo cambia.
- [ ] 5.2 Prosa: sección 4 (`04-marco-metodologico.tex`) definición de ECE, Brier, AUROC y de la regla de selección; sección 7 (`07-resultados.tex`, `subsec:calibracion`) métricas dentro y fuera de la muestra, barrido y señales alternativas, incluido el caso fuera de la muestra con confianza menor que 0,70; sección 8 (`08-discusion.tex`) lectura; sección 9 (`09-conclusiones.tex`) fila del objetivo 6; sección 10 (`10-recomendaciones.tex`, `subsec:calibracion-gate`) pasar de propuesta a resultado y dejar como futuro solo lo que exige cambiar contrato o configuración. Verificación: cada cifra coincide con el memo.
- [ ] 5.3 [LATEX] [AUTORES] Recompilar `main.pdf` y verificar las cifras con `pdftotext`.

## 6. Validación y cierre

- [ ] 6.1 Confirmar que `git diff` no toca `openspec/config.yaml`, `App/Backend/` ni el prompt. Verificación: diff vacío en esas rutas.
- [ ] 6.2 `openspec validate c-214-calibracion-y-punto-de-operacion-del-gate-de-confianza --strict --no-interactive`. Verificación: `is valid`.
- [ ] 6.3 Registrar la fase 70 en `CHANGES.md` al aplicar y guardar el progreso en engram (`opsx/c-214-calibracion-y-punto-de-operacion-del-gate-de-confianza/apply`).
