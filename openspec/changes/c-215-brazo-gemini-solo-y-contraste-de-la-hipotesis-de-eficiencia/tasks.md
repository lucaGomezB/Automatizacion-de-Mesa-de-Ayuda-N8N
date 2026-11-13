# Tasks: Brazo «Gemini solo» y contraste de la hipótesis de eficiencia

Convenciones: `A/` = `evaluation/data/campana/analisis/`; `E/` = `evaluation/`. Strict TDD: ninguna
línea de producción sin una prueba roja verificada por ejecución antes. NO se edita `App/Backend/`,
`openspec/config.yaml`, `docs/prompt_gemini.txt`, `data/*`, cachés de predicciones existentes,
archivos `.tex`, `numeros-canonicos.md` ni `tesis_para_agente.md`. Ninguna prueba ni comando de
este change llama a la red ni a la API de Gemini. Las tareas `[CORRIDA PAGA]` y `[AUTORES]` no las
puede cerrar un agente.

## 0. Preparación y prerregistro

- [x] 0.1 Proponer el change y validarlo: `openspec validate c-215-brazo-gemini-solo-y-contraste-de-la-hipotesis-de-eficiencia --strict --no-interactive` en verde. Verificación: sin errores.
- [x] 0.2 Red de seguridad: `python -m pytest evaluation -q` (base: 24 fallas preexistentes por `ENTORNO_OFFLINE`, 1331 pasan, 2 omitidas) y `python -m pytest evaluation/data/campana/analisis -q` (base: 59 pasan). Las fallas preexistentes se reportan y no se corrigen.
- [x] 0.3 Prerregistro congelado: D3 a D8 de `design.md` (margen `δ = 0,05`, tope 400, una corrida, precios, regla de tres vías) quedan fijados en el commit de la propuesta, anterior a cualquier dato del brazo.

## 1. Ejecutor del brazo «Gemini solo» (`E/brazo_gemini_solo.py`) — TDD, costo cero

- [x] 1.1 Cliente instrumentado y tope: mide latencia por intento, copia `usage_metadata`, cuenta intentos y se niega a emitir la llamada que superaría el tope (GSOLO-001, GSOLO-003). Probado con un cliente simulado y la etapa `GeminiClassifier` real.
- [x] 1.2 Caché JSONL reanudable con metadatos, `fsync` por caso, contador acumulado de llamadas y aborto ante metadatos incompatibles (GSOLO-002).
- [x] 1.3 Guardas: `--confirmar-costo`, versión del SDK `>=2.33,<3`, credencial solo del entorno y sin imprimirla, SHA-256 del prompt congelado, tope no superior a 400 (GSOLO-004).
- [x] 1.4 Modo `--dry-run`: casos pendientes, llamadas mínimas y máximas y costo estimado en ambos escenarios de precio, sin red, sin clave y sin escribir el caché (GSOLO-004).
- [x] 1.5 Bucle de corrida y CLI: códigos de salida 0 (completa), 2 (guarda), 3 (tope alcanzado); un fallo del proveedor se registra y no corta la corrida.

## 2. Análisis pareado (`A/analisis_brazo_gemini_solo_c215.py`) — TDD, cachés sintéticos

- [x] 2.1 Carga y alineación: caché del brazo, predicciones de H y corpus por bloque; aborta sin escribir ante caché inexistente, incompleto o con hash de corpus distinto (GSOLO-005).
- [x] 2.2 Calidad: exactitud estricta y laxa con Wilson, macro-F1, tabla 2×2, McNemar exacta y diferencia pareada con IC bootstrap de semilla 20261021 (GSOLO-005).
- [x] 2.3 Eficiencia: llamadas, tokens, costo (dos escenarios de precio) y latencia por caso para L y H imputado, razones con IC bootstrap pareado (GSOLO-005).
- [x] 2.4 Regla de tres vías, validez de la corrida, control de deriva y sensibilidad H\* (GSOLO-006).
- [x] 2.5 Salidas JSON y Markdown deterministas con SHA-256 y CLI con código distinto de cero si falta el caché (GSOLO-005).

## 3. Documentación operativa

- [x] 3.1 Comandos exactos de dry-run, corrida real y análisis en `A/README.md`, con requisitos de la corrida (versión del SDK, variables de entorno por nombre, tope y costo).

## 4. Corrida paga y salidas reales

- [x] 4.1 [CORRIDA PAGA] Una persona con `GEMINI_API_KEY` y el visto bueno de gasto instala `google-genai` dentro del pin (`>=2.33,<3`), corre el dry-run, verifica el costo estimado y lanza la corrida real con `--confirmar-costo`. Verificación: caché con los 303 casos, llamadas acumuladas ≤ 400.
- [x] 4.2 [CORRIDA PAGA] Versionar `evaluation/data/campana/brazo_gemini_solo/cache_brazo_gemini_solo.jsonl` en un commit POSTERIOR al del prerregistro.
- [x] 4.3 [AUTORES] Correr el análisis y generar `analisis_brazo_gemini_solo_c215.{json,md}` con su `SHA256SUMS`; anotar el veredicto de tres vías tal como sale, favorable o no.

## 5. Registro y prosa de la tesis

- [x] 5.1 [AUTORES] Registrar las cifras en `numeros-canonicos.md` (sección nueva, con procedencia y comando). Hecho: sección 3.25.
- [x] 5.2 [AUTORES] Escribir la prosa en introducción, resultados, discusión y conclusiones, incluido un veredicto desfavorable o no concluyente, y retirar o condicionar toda afirmación de eficiencia que el resultado no sostenga.
- [x] 5.3 [AUTORES] Agregar la FASE a `CHANGES.md` (hecho: FASE 71) y recompilar el PDF (hecho el 2026-11-13 con Docker `texlive-thesis`: 149 páginas, 0 errores, 0 referencias o citas indefinidas, biber sin avisos, `verify_citations.py` PASS).

## 6. Desviación declarada (2026-11-13): reintento de fallos técnicos

- [x] 6.1 Documentar la desviación en `design.md` (sección «Desviaciones del prerregistro»): incidente, definición estricta de fallo técnico, contabilidad del tope, amenaza a la validez y qué no cambia.
- [x] 6.2 Ejecutor: `es_fallo_tecnico`, doble tope (400 respuestas del modelo y 600 intentos totales), historial append-only con `reintento_de_fallo_tecnico` y `ronda`, y `--reintentar-fallos-tecnicos` con dry-run. Probado con cliente simulado (Strict TDD).
- [x] 6.3 Análisis: registro vigente por caso, control de deriva por bloque y pooled sin los fallos técnicos (con el número de excluidos) y sección «Desviaciones del prerregistro» con conteos leídos del caché.
- [x] 6.4 `A/README.md`: comando exacto del reintento y la contabilidad de llamadas.
- [x] 6.5 Verificación sin costo: `python -m evaluation.brazo_gemini_solo --dry-run --reintentar-fallos-tecnicos` sobre el caché real informa 112 casos a reintentar y 0 pendientes nuevos, sin modificar el caché (SHA-256 idéntico antes y después).
- [x] 6.6 [CORRIDA PAGA] Una persona con `GEMINI_API_KEY` bien cargada y visto bueno de gasto (hasta 209 respuestas, del orden de USD 0,08 a 0,15 a precio introductorio) corre `python -m evaluation.brazo_gemini_solo --confirmar-costo --reintentar-fallos-tecnicos`. Verificación: 0 casos con fallo técnico vigente y llamadas con respuesta menor o igual a 400.
- [x] 6.7 [AUTORES] Regenerar `analisis_brazo_gemini_solo_c215.{json,md}` y su `SHA256SUMS` con el caché completo y declarar la desviación y la amenaza a la validez en la prosa de la tesis.
