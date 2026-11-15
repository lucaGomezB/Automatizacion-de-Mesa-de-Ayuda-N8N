# Tasks: Monitorear el servicio de inferencia y la deriva del modelo

Al final de cada tarea, entre parentesis, el requisito del change que cumple, por nombre corto entre comillas angulares precedido de su capacidad: `IPA` (`inference-provider-abstraction`) y `MDM` (`model-drift-monitoring`). Nombres cortos IPA: «Interfaz», «Taxonomia», «Seleccion», «Neutralidad», «Trazabilidad». Nombres cortos MDM: «Canario», «Job», «Deteccion», «Umbrales», «Preservacion». Las tareas de preparacion y las verificaciones transversales no llevan parentesis.

Este change SI escribe codigo ejecutable (interfaz del proveedor y job de monitoreo): aplica el ciclo TDD estricto (RED -> GREEN -> TRIANGULATE -> REFACTOR) sobre las funciones puras y sobre el contrato de la interfaz. No mide de nuevo la tesis, no invoca al proveedor pago fuera del gate de confirmacion y no toca ningun numero canonico.

## 0. Preparacion y verificacion de estado

- [x] 0.1 Leer `proposal.md`, `design.md` (D1 a D8) y los dos specs delta; cargar los `SKILL.md` completos de `python-testing` y `pytest-coverage` antes de escribir codigo y registrar la resolucion.
- [x] 0.2 Capturar la linea de base como evidencia de partida: `git status`, `git rev-parse HEAD`, `sha256sum evaluation/evidence/*.json` y las predicciones canonicas de referencia. Registrar modificaciones preexistentes ajenas a este change y no tocarlas.
- [x] 0.3 **Red de seguridad:** correr `cd App/Backend && pytest -m "not integration"` y `cd evaluation && pytest -q`; registrar el resultado (debe pasar antes de editar; si algo falla, detenerse y reportarlo como fallo preexistente). Verde: backend 1798 passed / 61 deselected / 1 xfailed; evaluation 1392 passed / 1 skipped.
- [x] 0.4 Releer `App/Backend/app/classifiers/gemini_classifier.py`, `hybrid.py`, `base.py` y los campos de `Settings` relativos a Gemini; confirmar que la interfaz puede extraerse sin cambiar el contrato. (`IPA` «Interfaz»)
- [x] 0.5 Releer `evaluation/metrics.py`, el gate de corrida paga de `evaluation/run_evaluation.py` (`PaidRunNotConfirmedError`, `_env_confirm_paid`) y la estructura de `evaluation/evidence/README.md`. (`MDM` «Job»)
- [x] 0.6 **[CHECKPOINT DE LOS AUTORES — BLOQUEA EL GRUPO 3]** Confirmar los pisos y la tolerancia por defecto (OQ1) y el tamano del canario (OQ2) sobre la linea de base congelada. Registrar la respuesta. CONFIRMADO por los autores: OQ1 delta = 0.05; metricas monitoreadas = `exactitud_estricta` + `f1_macro`; piso = max(0, base - 0.05); SIN pisos por sector; sobrescribibles por entorno. OQ2 canario = corpus independiente completo (103 casos); cadencia offline mensual + ante cambio de proveedor/modelo; corrida paga solo bajo demanda detras del gate.
- [x] 0.7 Identificar el corpus independiente de `evaluation-out-of-sample-validation` y confirmar que el canario puede extraerse de el sin solapamiento con el corpus de ajuste. (`MDM` «Canario») Corpus independiente: `evaluation/data/campana/corpus_independiente.json` (103 casos, ids `I*`); su prediccion versionada `predicciones_independiente.json` habilita la linea de base offline.

## 1. Interfaz del proveedor de inferencia (TDD)

- [x] 1.1 **RED:** escribir la prueba del contrato de la interfaz (una implementacion falsa se inyecta en el clasificador sin importar el SDK; la firma no expone tipos del proveedor) antes de que exista el modulo; ejecutar y confirmar que falla por ausencia de la implementacion. (`IPA` «Interfaz») RED confirmado: sin `provider.py`, `tests/classifiers/test_provider.py` falla con `ModuleNotFoundError`.
- [x] 1.2 **GREEN:** crear `App/Backend/app/classifiers/provider.py` con la interfaz, sus parametros y su taxonomia de errores; implementar la minima logica para pasar. (`IPA` «Interfaz», «Taxonomia»)
- [x] 1.3 **TRIANGULATE:** agregar casos para transitorio (indisponibilidad, limite de tasa, timeout) y terminal (peticion, autenticacion, autorizacion); confirmar que la taxonomia GENERALIZA sin romper. (`IPA` «Taxonomia»)
- [x] 1.4 **REFACTOR:** extraer constantes y nombres; correr las pruebas tras cada paso y confirmar verde. (`IPA` «Interfaz»)
- [x] 1.5 Refactorizar `GeminiClassifier` para implementar `GeminiProvider` detras de la interfaz, conservando la construccion del prompt, la validacion del contrato, el bucle de reintento y el fallback; verificar que las pruebas existentes de `gemini_classifier` siguen verdes. (`IPA` «Interfaz»)
- [x] 1.6 Conectar `HybridClassifier` a la interfaz mediante el registro de proveedores; verificar que las pruebas existentes de `hybrid` siguen verdes. (`IPA` «Interfaz»)
- [x] 1.7 **Neutralidad:** agregar la prueba que clasifica el corpus de evaluacion con el proveedor por defecto a traves de la interfaz y confirma que las predicciones coinciden caso por caso con las vigentes; verificar que ningun numero canonico cambia. (`IPA` «Neutralidad») `tests/classifiers/test_hybrid_neutralidad.py`: 200 casos, 0 diferencias.

## 2. Configuracion y trazabilidad de la identidad (IPA)

- [x] 2.1 Agregar `inference_provider` y `inference_model` a `Settings` con los defaults vigentes; verificar que sin configuracion el proveedor y el modelo resueltos son los actuales. (`IPA` «Seleccion»)
- [x] 2.2 Implementar el registro que resuelve el nombre del proveedor a su factory; verificar que un nombre desconocido falla con error explicito en la inicializacion. (`IPA` «Seleccion»)
- [x] 2.3 Extender el metadata de la cache de predicciones con `provider` y `model`; verificar que la evidencia congelada (sin esos campos) sigue siendo valida bajo los defaults y que una version distinta la invalida. (`IPA` «Trazabilidad»)
- [x] 2.4 Registrar el proveedor y el modelo efectivos en el evento estructurado de clasificacion; verificar que el evento los identifica y NO incluye la clave de API ni el texto crudo. (`IPA` «Trazabilidad»)

## 3. Conjunto canario y job de monitoreo (TDD)

- [x] 3.1 **RED:** escribir `evaluation/monitoreo/test_monitor_deriva.py` con pruebas sinteticas de `metricas_canario`, `comparar_con_base`, `detectar_deriva`, `evaluar_alertas` e `identidad_proveedor` antes de existir el modulo; ejecutar y confirmar que fallan por ausencia de la implementacion. (`MDM` «Deteccion») RED confirmado: `ImportError: cannot import name 'monitor_deriva'`.
- [x] 3.2 **GREEN:** implementar `evaluation/monitoreo/monitor_deriva.py` con la minima logica para pasar; reutilizar `evaluation/metrics.py` sin modificarlo. (`MDM` «Deteccion»)
- [x] 3.3 **TRIANGULATE:** agregar casos con entradas distintas (sin degradacion, degradacion de metrica, cambio de identidad, ambos; metrica bajo el piso y sobre el piso); confirmar que GENERALIZA sin romper. (`MDM` «Deteccion», «Umbrales»)
- [x] 3.4 **REFACTOR:** extraer constantes y nombres; correr las pruebas tras cada paso y confirmar verde. (`MDM` «Deteccion»)
- [x] 3.5 Versionar el conjunto canario en `evaluation/data/canario/canario.json` con su `canario.SHA256SUMS.txt`, tomado del corpus independiente; verificar el no solapamiento con el corpus de ajuste. (`MDM` «Canario») 103 casos; SHA-256 `canario.json` = `535b55d2c866a143db548725844b18b4a0894542c0854550fd5799edc53e894e`; disyunto verificado con `verificar_no_solape`.
- [x] 3.6 Calcular una sola vez y versionar la linea de base congelada `evaluation/data/canario/canario_baseline.json` desde los artefactos versionados, en modo offline; verificar que no se invoca al proveedor. (`MDM` «Job») exactitud estricta `0.8446601941747572`; F1 macro `0.7446560846560847`; SHA-256 = `cc6b1c506a5ee3670d74d342154c3b83c013b50ab5c7aa081378246aa8d49233`.
- [x] 3.7 Implementar el `main()` del job: reproducir la linea de base desde los artefactos versionados (offline por defecto) y, para predicciones frescas, exigir el gate de confirmacion reutilizado del framework; escribir el reporte fechado en `evaluation/data/canario/reportes/`. (`MDM` «Job»)
- [x] 3.8 Verificar que sin confirmacion el job que necesita predicciones frescas aborta sin invocar al proveedor y que dos corridas sobre las mismas entradas producen salidas byte a byte identicas. (`MDM` «Job»)
- [x] 3.9 Implementar los pisos por metrica en `Settings` con defaults derivados de la linea de base y la tolerancia del checkpoint 0.6; verificar que un override por entorno cambia el piso sin recompilar. (`MDM` «Umbrales») `monitoring_tolerancia=0.05`, `monitoring_exactitud_estricta_floor=0.7946601941747572`, `monitoring_f1_macro_floor=0.6946560846560846`.

## 4. Fallback documentado y trazabilidad (MDM)

- [x] 4.1 Redactar en `docs/operational-guide.md` el procedimiento de monitoreo (comando, cadencia, lectura de la deriva) y el fallback operativo vigente remitiendo a `classification-resilience`, con el criterio de restablecimiento del servicio. (`MDM` «Umbrales») Seccion 12.
- [x] 4.2 Verificar que la alerta emitida por el job identifica la metrica, su valor, su piso y la corrida, y que documenta el fallback y el criterio de restablecimiento. (`MDM` «Umbrales»)
- [x] 4.3 Registrar la matriz de decision operativa (proveedor/modelo frente a metrica) en el procedimiento, para distinguir `deriva_de_identidad` de `deriva_de_metrica`. (`MDM` «Deteccion»)

## 5. Verificacion de cierre

- [x] 5.1 Volver a correr `cd App/Backend && pytest -m "not integration"` y `cd evaluation && pytest -q`; confirmar que no hay regresiones. (`IPA` «Neutralidad») Backend 1826 passed / 61 deselected / 1 xfailed; evaluation 1419 passed / 1 skipped.
- [x] 5.2 Ejecutar el job una vez y confirmar que el SHA-256 de `evaluation/evidence/` es identico al de 0.2 y que no cambio ningun artefacto canonico. (`MDM` «Preservacion»)
- [x] 5.3 Confirmar con `git diff --stat` que no cambiaron `n8n/`, la guarda de costo, el corpus de evaluacion, las predicciones canonicas ni los artefactos congelados.
- [x] 5.4 Verificar que el proveedor por defecto reproduce las predicciones vigentes caso por caso y que los cinco sectores, el prompt y los parametros son identicos a los vigentes. (`IPA` «Neutralidad»)
- [x] 5.5 Correr `openspec validate c-227-monitorear-el-servicio-de-inferencia-y-la-deriva-del-modelo --strict` y verificar que pasa.
- [x] 5.6 Dejar a cargo del orquestador la actualizacion de `CHANGES.md` y el `engram sync`; no pushear, no crear tag ni release.
- [x] 5.7 Guardar en Engram el resumen del change con el nombre, los artefactos, los SHA-256 y el resultado de las verificaciones; reportar al orquestador con la tabla de evidencia del ciclo TDD.

## Evidencia del ciclo TDD (obligatoria al reportar)

| Tarea | Archivo de prueba | Capa | Red de seguridad | RED | GREEN | TRIANGULATE | REFACTOR |
|---|---|---|---|---|---|---|---|
| 1.1-1.4 | `App/Backend/tests/classifiers/test_provider.py` | Unit | `pytest -m "not integration"` | falla por ausencia | pasa | transitorio/terminal | limpio |
| 1.7 | `App/Backend/tests/classifiers/test_hybrid_neutralidad.py` | Unit | `pytest -m "not integration"` | — | pasa | corpus caso por caso | limpio |
| 3.1-3.4 | `evaluation/monitoreo/test_monitor_deriva.py` | Unit | `pytest -q` de `evaluation/` | falla por ausencia | pasa | sin deriva/deriva/identidad/umbral | limpio |
