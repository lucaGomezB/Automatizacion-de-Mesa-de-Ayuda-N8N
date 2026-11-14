# Sesgo de corpus y fragilidad de la referencia (c-219)

Analisis offline, de solo lectura y determinista, sin red ni Gemini. Los resultados se
rotulan como **sensibilidad**: no son una exactitud corregida ni afirman que la
referencia cause las diferencias. Metodo prerregistrado en el docstring del script.

## Anclajes reproducidos antes de medir

- Casos: 206. Etapa determinista V1: cortocircuito 115, aciertos 88/115 (0,7652).
- Cobertura de V1 (casos con al menos un match): 131 (esperada 131; reproduce: si).
- Hibrido congelado: 142/206 (0,6893), macro-F1 0,7024.
- Patrones: V1 151, V0 89, derivados del corpus 62 (V1 menos V0).

## Vocabulario corpus-blind

- Fuente publica: Glosario de términos de ciberseguridad: una guía de aproximación para el empresario (INCIBE (Instituto Nacional de Ciberseguridad de España), colección Protege tu empresa), https://www.incibe.es/sites/default/files/contenidos/guias/doc/guia_glosario_ciberseguridad_metad.pdf, consultada el 2026-11-13.
- Mas las definiciones canonicas de los cinco sectores (`CLAUDE.md`).
- Derivado el 2026-11-13T23:52:31-03:00; SHA-256 del contenido: `ec350b9615410defe531183e317c197a21f778638eb5ccccdbe9a77b2a34d581`.
- Independencia: procedimental (prerregistro), no de contenido. No se afirma que sus terminos no aparezcan en el corpus.

## Etapa determinista por vocabulario (n = 206)

| Vocabulario | Patrones | Cobertura | Cortocircuito | Aciertos | Precision | IC 95 % Wilson | Delta cobertura | Delta cortocircuito | Delta precision (puntos) |
|---|---|---|---|---|---|---|---|---|---|
| V1 vigente | 151 | 131 | 115 | 88 | 0,7652 | [0,6800; 0,8333] | - | - | - |
| Corpus-blind (fuente externa) | 90 | 83 | 75 | 54 | 0,7200 | [0,6096; 0,8090] | -48 | -40 | -4,5 |
| V0 (control de c-142, 89 patrones previos a c-71) | 89 | 97 | 88 | 65 | 0,7386 | [0,6382; 0,8191] | -34 | -27 | -2,7 |

Los conjuntos de casos cortocircuitados difieren entre vocabularios: la diferencia de
precision no es pareada. Pareado sobre los casos que cortocircuitan en ambos:

| Vocabulario | Casos comunes con V1 | Aciertos del vocabulario | Aciertos de V1 | Mismo sector |
|---|---|---|---|---|
| Corpus-blind (fuente externa) | 54 | 40 | 43 | 47 |
| V0 (control de c-142, 89 patrones previos a c-71) | 83 | 62 | 63 | 82 |

## Exactitud estricta del hibrido congelado por subconjunto de la referencia

| Subconjunto | Casos | Aciertos | Exactitud | IC 95 % Wilson | Exactitud laxa |
|---|---|---|---|---|---|
| Consenso E3 = E4 | 142 | 109 | 0,7676 | [0,6916; 0,8295] | 0,8451 |
| Arbitrado por E5 | 64 | 33 | 0,5156 | [0,3958; 0,6337] | 0,6562 |
| Discordancia de tres vias (subconjunto de los arbitrados) | 6 | 0 | 0,0000 | [0,0000; 0,3903] | 0,5000 |
| Total | 206 | 142 | 0,6893 | [0,6231; 0,7486] | 0,7864 |

El subconjunto literal E3 = E4 = E5 tiene 0 casos: es vacio por
construccion, porque E5 solo etiqueto los 64 casos discordantes. No se fuerza un subconjunto.
La diferencia entre subconjuntos es descriptiva; no se afirma que la referencia la cause.

## Entradas (SHA-256)

- `arbitraje_tres_vias.json`: `4c85ab43bf28cac228caa35a6aaf3863deb327767cba31fbe850b43d2efe6a61`
- `corpus_independiente_arbitrado.json`: `cb2874e649fb932c00b536100025c0a0137b3314ab12d45234e4c29049adc67e`
- `doble_etiquetado_arbitrado.csv`: `7993f3ffda7ae7b380833a41b226ed3a6b4f6aaa36f3fbed66fb52682a61d2a4`
- `keywords_pre_c71.json`: `8d9e646fae8ec5ff746fdaddecc5301a4db8f0df6e46da6d77eca26e56952e55`
- `predicciones_arbitrado.json`: `cb8aba6089dde9868c61740fba713fb75923ee32317370c46e0daeb52a01d5d5`
- `vocabulario_corpus_blind_c219.json`: `2f4473a41be962eda23672120da98c7225a6e6cbd1b818f724a1b3496642beab`
