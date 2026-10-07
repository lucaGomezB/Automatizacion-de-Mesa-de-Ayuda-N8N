# Proposal: pseudonimizacion de numeros de tarjeta hablados

## Why

El pseudonimizador cubre 4 categorias de PII (email, telefono, host, persona) pero NO las tarjetas. Cuando un llamante menciona "tarjeta" y lee un numero de 16 digitos, el patron de TELEFONO lo consume parcialmente y deja digitos en claro:

- `mi tarjeta numero 4517 6712 3456 7890 vencio` -> `mi tarjeta numero [TELEFONO] 7890 vencio` (fuga `7890`)
- `Hola, mi tarjeta es 0102301239999320 y no puedo operar` -> `... 010[TELEFONO] ...`

Es PII financiera (Ley 25.326): debe enmascararse completa. R169 (telefonia) es el caso tematico.

## What Changes

- Nueva categoria CARD -> `[TARJETA]` (MAYUSCULAS), con contador `tarjeta` en `conteos`.
- Aplicada ANTES de TELEFONO para que este no la consuma.
- Disparador CONTEXTUAL: solo ante mencion de `tarjeta`/`tarjetas`, dentro de una ventana de 40 caracteres despues del disparador.
- Tolerancia 4-4-4-4 con espacios o guiones, y la forma contigua de 16 digitos.
- No regresion: la corrida del DLL de R067 (`axm0102301239999320002302`, sin "tarjeta") NO se clasifica como `[TARJETA]`.

### Out of Scope

- Validacion de Luhn y longitudes distintas de 16 (Amex 15).
- Corregir el falso positivo PREEXISTENTE de TELEFONO sobre R067.
- Disparadores sin la palabra "tarjeta"; NER/modelos.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `data-pseudonymization`: agrega la categoria `[TARJETA]` con disparador contextual y ventana; extiende el conteo (`tarjeta`) y el orden (CARD antes de TELEFONO); agrega la no regresion de corridas de 16 digitos sin contexto.

## Impact

- Modified: `App/Backend/app/utils/pseudonymizer.py` (patron CARD, etiqueta, contador, orden).
- Modified: `App/Backend/tests/test_pseudonymizer.py` (tests nuevos; dict `conteos` con clave `tarjeta`).
- Modified: `App/Backend/tests/test_pseudonymization_integration.py` (conteos con la nueva clave si aplica).

Sin cambios de API, esquema ni dependencias. La funcion sigue PURA.

## Governance

**HIGH.** PII financiera sensible (Ley 25.326). La deteccion se propone y valida con tests; no se alteran controles de seguridad. Requiere revision antes de produccion.

## Risks

- Falso positivo sobre corridas legitimas (R067) -> disparador contextual + escenario de no regresion.
- Falso negativo sin decir "tarjeta" -> tradeoff documentado; ventana configurable.
- Romper el contrato de `conteos` -> tarea de actualizar el dict; delta MODIFIED.
- Ventana mal calibrada -> constante `_CARD_CONTEXT_WINDOW_CHARS = 40` testeada.

## Rollback Plan

Revertir el commit restaura `pseudonymizer.py` y sus tests al estado previo (4 categorias). Sin migraciones ni datos afectados: la pseudonimizacion es pura y en tiempo de ejecucion. No requiere backfill.

## Success Criteria

- [ ] Formatos agrupados y contiguos de 16 digitos se reemplazan por `[TARJETA]` con contexto.
- [ ] `conteos["tarjeta"]` refleja cada reemplazo; las 4 categorias previas no se alteran.
- [ ] R067 sin mencion de "tarjeta" NO produce `[TARJETA]`.
- [ ] `openspec validate c-73-pseudonimizacion-tarjeta --strict` pasa.