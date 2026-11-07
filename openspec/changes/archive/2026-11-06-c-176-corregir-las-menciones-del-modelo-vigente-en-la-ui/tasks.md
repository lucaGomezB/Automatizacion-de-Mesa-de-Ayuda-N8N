## 1. Red de seguridad y delimitación del alcance

- [x] 1.1 Ejecutar la suite del frontend en el estado previo (`cd App/Frontend; npm run test`) y registrar la linea base (n pruebas en verde) para detectar regresiones. Verificacion: el comando reporta la linea base sin fallos preexistentes.
- [x] 1.2 Localizar todas las menciones vigentes del modelo retirado en el frontend (`grep -rn "Gemini 2.5\|2.5 Flash" App/Frontend/src`). Verificacion: la busqueda devuelve unicamente los archivos del alcance (`utils/formatters.ts`, `pages/ReportarIncidente/index.tsx`, `utils/validators.ts`, `pages/Administracion/DetalleIncidente.test.tsx`, `pages/Administracion/ValidarClasificacionDialog.test.tsx`).

## 2. Contrato de la etiqueta de etapa del pipeline (TDD)

- [x] 2.1 RED: crear `App/Frontend/src/utils/formatters.etapa.test.ts` con un caso que afirma que `formatearEtapa('gemini')` es `"Gemini"` y que no contiene `"2.5 Flash"`. Verificacion: la prueba falla contra la implementacion vigente.
- [x] 2.2 GREEN: cambiar la etiqueta en `App/Frontend/src/utils/formatters.ts` (`gemini: 'Gemini'`) con el minimo cambio para pasar 2.1. Verificacion: `cd App/Frontend; npm run test src/utils/formatters.etapa.test.ts` en verde.
- [x] 2.3 TRIANGULATE: agregar a `formatters.etapa.test.ts` los casos de las etapas `deterministic` -> `"Deterministico"`, `fallback` -> `"Sin clasificar"` y una etapa desconocida que se devuelve tal cual. Verificacion: los casos pasan sin romper 2.2.
- [x] 2.4 REFACTOR: revisar que `formatearEtapa` siga siendo una funcion pura y sin duplicacion; si no hay nada que mejorar, marcar como no aplicable. Verificacion: la suite del archivo sigue en verde tras cualquier refactor.

## 3. Pruebas de componente que fijan la etiqueta

- [x] 3.1 Actualizar `App/Frontend/src/pages/Administracion/DetalleIncidente.test.tsx:70` para afirmar `"Gemini"` en lugar de `"Gemini 2.5 Flash"`. Verificacion: la prueba pasa.
- [x] 3.2 Actualizar `App/Frontend/src/pages/Administracion/ValidarClasificacionDialog.test.tsx:140` para afirmar `"Gemini"` en lugar de `"Gemini 2.5 Flash"`. Verificacion: la prueba pasa.

## 4. Texto del portal de reporte (TDD)

- [x] 4.1 RED: agregar un caso a `App/Frontend/src/pages/ReportarIncidente/index.test.tsx` que afirme que el texto que describe la clasificacion automatica no contiene `"2.5 Flash"` ni una version del modelo. Verificacion: la prueba falla contra el texto vigente.
- [x] 4.2 GREEN: corregir el texto en `App/Frontend/src/pages/ReportarIncidente/index.tsx` para que sea agnostico a la version (quitar `"2.5 Flash"`). Verificacion: el caso 4.1 pasa.
- [x] 4.3 TRIANGULATE: afirmar en la misma prueba que el texto sigue describiendo la clasificacion automatica y que la nota informativa conserva el umbral del 70%. Verificacion: la prueba pasa con los casos agregados.

## 5. Comentarios y verificacion final

- [x] 5.1 Actualizar el comentario de cabecera de `App/Frontend/src/utils/formatters.ts:10` para no nombrar la version del modelo. Verificacion: el comentario ya no contiene `"2.5 Flash"`.
- [x] 5.2 Actualizar el comentario de cabecera de `App/Frontend/src/utils/validators.ts:10` de forma equivalente. Verificacion: el comentario ya no contiene `"2.5 Flash"`.
- [x] 5.3 Verificar que no queda ninguna mencion vigente del literal en el frontend (`grep -rn "2.5 Flash" App/Frontend/src`). Verificacion: sin coincidencias.
- [x] 5.4 Verificar que las menciones historicas fuera de alcance permanecen intactas (`git diff --name-only`). Verificacion: el diff no incluye `knowledge-base/**`, `App/Backend/app/config/settings.py`, `evaluation/**`, `App/Backend/tests/test_gemini_generation_config.py`, `openspec/specs/foundation-environment/spec.md` ni `CHANGES.md`.
- [x] 5.5 Ejecutar la suite completa del frontend (`cd App/Frontend; npm run test`). Verificacion: verde, sin aserciones del literal retirado.
- [x] 5.6 Ejecutar `openspec validate "c-176-corregir-las-menciones-del-modelo-vigente-en-la-ui" --strict`. Verificacion: PASS.
