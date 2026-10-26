# Sensibilidad frente a los ajustes del clasificador (c-142)

## Procedencia

- SHA-256 del corpus: `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb`.
- Punto de operacion vigente (Settings): tau = 0.5166; pesos del score de correctitud: margen = 0.5000, evidencia = 0.3000, densidad = 0.2000.
- Blob `keywords_pre_c71 (7925903)`: `858f1c679c660e5e2a88a06544f2cdc3bfcb6328`.
- Blob `keywords_vigente`: `334a8edb296cf8e88468164c9a35d57f80952c0e`.
- Blob `prompt_pre_c72 (a76851e^)`: `1daceb384f0a585941afaf2a9b87de8bffb31db8`.
- Blob `prompt_vigente`: `49267f4a5cf214bf46899c5177661f1cdbfd10fb`.
- SHA-256 de `keywords_pre_c71.json`: `8d9e646fae8ec5ff746fdaddecc5301a4db8f0df6e46da6d77eca26e56952e55`.
- SHA-256 de `prompt_gemini_pre_c72.txt`: `934542f6d6a96ab77c58615419cb8f3265913f24ae01adbc326ecd723bdcc1ec`.
- Cache FORCE-ESCALATE usada en E3/E4: `classifier_version` `hybrid-v2`, `corpus_hash` `5f062e1466facd1a522d80c2693d1d256017aae37372c2d288646ba104f46a93` (no coincide con el del corpus vigente). La guarda `verificar_cache_contra_corpus` verifico identificador, descripcion y sector asignado de las 200 entradas (0 diferencias); el uso de la cache fue confirmado por los autores.
- Pre-registro: variantes, comparadores y reglas de lectura fijados en el design de c-142 (D2-D4, D8, D9) antes de computar; todas se reportan cualquiera sea el resultado.

## Configuracion evaluada (V1 + L1)

Vocabulario vigente (151 patrones) con la logica y el punto de operacion vigentes, por el adaptador del clasificador de produccion.

- Casos cortocircuitados: 131/200 (cobertura 0.6550).
- Aciertos estrictos: 97/131; exactitud 0.7405; IC de Wilson al 95 %: [0.6593, 0.8079].
- Aciertos laxos (sector dentro del conjunto de verdad): 119/131.
- Reproduccion de la configuracion evaluada: 131/97 frente a 131/97 esperados: coincide.

## Variante principal: vocabulario previo a c-71 con la logica vigente (V0 + L1)

Ablacion de un solo factor: 89 patrones previos a c-71 (blob 858f1c6), misma logica y mismo punto de operacion.

- Casos cortocircuitados: 74/200 (cobertura 0.3700).
- Aciertos estrictos: 39/74; exactitud 0.5270; IC de Wilson al 95 %: [0.4148, 0.6366].
- Aciertos laxos (sector dentro del conjunto de verdad): 57/74.
- Diferencia descriptiva de exactitud (V1 - V0): 0.2134; los conjuntos de casos difieren, por lo que no es una diferencia pareada.

Descomposicion pareada (aciertos estrictos de la etapa 1 de cada vocabulario):

| Segmento | Casos | Aciertos V1 | Aciertos V0 |
|---|---|---|---|
| Cortocircuitados por ambos | 67 | 38 | 37 |
| Solo V1 (aporta la ampliacion de c-71) | 64 | 59 | 0 |
| Solo V0 | 7 | 0 | 2 |

McNemar sobre los casos comunes (V1 frente a V0):

- Tabla 2x2 (67 pares): ambas aciertan 37; solo V1 (b) 1; solo V0 (c) 0; ninguna 29.
- McNemar: p binomial exacto bilateral 1.0000; chi-cuadrado corregido 0.0000 (p = 1.0000); p primario 1.0000 (criterio exacto). Evidencia descriptiva, sin correccion por multiplicidad.

## Referencia historica: vocabulario y logica previos a c-71 (V0 + L0)

Replica pura de la logica de 7925903 (confianza w/(w + r + 1e-6), cortocircuito con confianza >= 0.90). Sirve de control de fidelidad contra la linea base documentada por c-71 y de referencia del punto de partida; no se lee como cota del sesgo.

- Casos cortocircuitados: 72/200 (cobertura 0.3600).
- Aciertos estrictos: 37/72; exactitud 0.5139; IC de Wilson al 95 %: [0.4007, 0.6257].
- Aciertos laxos (sector dentro del conjunto de verdad): 55/72.

Control de fidelidad (documentado por c-71 frente a reproducido):

| Metrica | Documentado | Reproducido | Estado |
|---|---|---|---|
| cortocircuitados | 72 | 72 | coincide |
| cortocircuitados_correo | 22 | 22 | coincide |
| cortocircuitados_web | 14 | 14 | coincide |
| cortocircuitados_telefono | 36 | 36 | coincide |
| aciertos | 37 | 37 | coincide |
| aciertos_correo | 13 | 13 | coincide |
| aciertos_web | 7 | 7 | coincide |
| aciertos_telefono | 17 | 17 | coincide |
| aciertos_laxos | 55 | 55 | coincide |
| sin_coincidencias | 119 | 119 | coincide |
| predicciones_seguridad_informatica | 126 | 126 | coincide |

## Variante por pliegues

- Estado: no factible. El diff de c-71 (commit 1368fd8) solo agrega 62 patrones bajo cinco comentarios de bloque por sector y no registra que casos del corpus motivaron cada patron; el mensaje del commit y los artefactos de c-71 describen el procedimiento en forma generica. Reconstruir el vocabulario por pliegues exigiria una regla de atribucion por patron que el repositorio no permite verificar, y el resultado dependeria de la regla elegida (un grado de libertad que el pre-registro D2 excluye). Reversible si los autores aportan la atribucion por patron.

## Sensibilidad global y piso comparativo

- E3: aciertos estrictos globales sobre 200 casos con una sola fuente de predicciones de Gemini: V1 146/200 (documentado sobre los 200 casos: 146); V0 128/200.
- E3: casos excluidos de ambos lados (sin prediccion de Gemini): ninguno.
  - Tabla 2x2 (200 pares): ambas aciertan 128; solo V1 (b) 18; solo V0 (c) 0; ninguna 54.
  - McNemar: p binomial exacto bilateral 0.0000; chi-cuadrado corregido 16.0556 (p = 0.0001); p primario 0.0000 (criterio exacto). Evidencia descriptiva, sin correccion por multiplicidad.
- E4 referencia en muestra (V1): |S| = 131; pares 130; excluidos R099.
- E4 referencia en muestra (V1): exactitud de la etapa de reglas 0.7385 (96/130); de Gemini 0.6769 (88/130).
  - Tabla 2x2 (130 pares): ambas aciertan 80; solo reglas (b) 16; solo Gemini (c) 8; ninguna 26.
  - McNemar: p binomial exacto bilateral 0.1516; chi-cuadrado corregido 2.0417 (p = 0.1530); p primario 0.1516 (criterio exacto). Evidencia descriptiva, sin correccion por multiplicidad.
- E4 (V0): |S| = 74; pares 73; excluidos R099.
- E4 (V0): exactitud de la etapa de reglas 0.5205 (38/73); de Gemini 0.6575 (48/73).
  - Tabla 2x2 (73 pares): ambas aciertan 35; solo reglas (b) 3; solo Gemini (c) 13; ninguna 22.
  - McNemar: p binomial exacto bilateral 0.0213; chi-cuadrado corregido 5.0625 (p = 0.0244); p primario 0.0213 (criterio exacto). Evidencia descriptiva, sin correccion por multiplicidad.

## Sensibilidad del prompt

Las reglas de frontera de c-72 solo influyeron en los casos que la configuracion evaluada escala a Gemini. Niveles de evidencia (c > b > a > ninguno, D9).

- Nivel a: motivadores entre los 69 casos escalados: R002, R038, R015.
- Nivel a: exactitud de la etapa Gemini con todos los casos 50/69; sin los motivadores 48/66.
- Nivel b: version del prompt de la FORCE-ESCALATE clasificada como "posterior" (cache_meta.generated_at: 2026-10-07T20:33:03.438926+00:00).
- Nivel b: no aplicable (solo la clasificacion "previa confirmada" habilita la comparacion pareada de la FORCE-ESCALATE frente a la corrida oficial).
- Nivel c (ablacion controlada de dos brazos, corrida paga): no computado; requiere autorizacion explicita y no se ejecuto.
