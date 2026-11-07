## 1. Red de seguridad y delimitación del alcance

- [x] 1.1 Ejecutar la suite del frontend en el estado previo (`cd App/Frontend; npm run test`) y registrar la línea base (n pruebas en verde) para detectar regresiones. Verificación: el comando reporta la línea base sin fallos preexistentes.
- [x] 1.2 Localizar todas las menciones a `Gemini` en el frontend (`grep -rn "Gemini" App/Frontend/src`) y confirmar que solo aparecen en los archivos del alcance (`utils/formatters.ts`, `utils/formatters.etapa.test.ts`, `pages/ReportarIncidente/index.tsx`, `pages/ReportarIncidente/index.test.tsx`, `pages/Administracion/DetalleIncidente.test.tsx`, `pages/Administracion/ValidarClasificacionDialog.test.tsx`). Verificación: cualquier coincidencia fuera de esa lista se evalúa antes de tocar y se documenta si queda fuera de alcance.
- [x] 1.3 Confirmar que `RevisionHumanaTable.tsx` obtiene la etiqueta vía `formatearEtapa` (sin literal hardcodeado). Verificación: `grep -n "formatearEtapa" App/Frontend/src/pages/Administracion/RevisionHumanaTable.tsx` muestra el uso y no hay literal "Gemini".

## 2. Contrato de la etiqueta de etapa del pipeline (TDD)

- [x] 2.1 RED: actualizar `App/Frontend/src/utils/formatters.etapa.test.ts` para afirmar que `formatearEtapa('gemini')` es exactamente `"Análisis por IA"` y que no contiene `"Gemini"` ni `"2.5 Flash"`. Verificación: `cd App/Frontend; npm run test src/utils/formatters.etapa.test.ts` falla contra la implementación vigente ("Gemini").
- [x] 2.2 GREEN: cambiar la etiqueta en `App/Frontend/src/utils/formatters.ts` (`gemini: 'Análisis por IA'`) con el mínimo cambio para pasar 2.1. Verificación: `cd App/Frontend; npm run test src/utils/formatters.etapa.test.ts` en verde.
- [x] 2.3 TRIANGULATE: agregar a `formatters.etapa.test.ts` los casos `deterministic` -> `"Determinístico"`, `fallback` -> `"Sin clasificar"` y una etapa desconocida que se devuelve tal cual. Verificación: los casos pasan sin romper 2.2.
- [x] 2.4 REFACTOR: revisar que `formatearEtapa` siga siendo una función pura y sin duplicación; si no hay nada que mejorar, marcar como no aplicable. Verificación: la suite del archivo sigue en verde tras cualquier refactor.

## 3. Pruebas de componente que fijan la etiqueta

- [x] 3.1 Actualizar `App/Frontend/src/pages/Administracion/DetalleIncidente.test.tsx` (aserción de la etapa, línea ~70) para afirmar `"Análisis por IA"` en lugar de `"Gemini"`. Verificación: `cd App/Frontend; npm run test src/pages/Administracion/DetalleIncidente.test.tsx` en verde.
- [x] 3.2 Actualizar `App/Frontend/src/pages/Administracion/ValidarClasificacionDialog.test.tsx` (aserción de la etapa, línea ~140) para afirmar `"Análisis por IA"` en lugar de `"Gemini"`. Verificación: `cd App/Frontend; npm run test src/pages/Administracion/ValidarClasificacionDialog.test.tsx` en verde.

## 4. Texto del portal de reporte (TDD)

- [x] 4.1 RED: actualizar `App/Frontend/src/pages/ReportarIncidente/index.test.tsx` para afirmar que el texto que describe la clasificación automática NO contiene `"Gemini"` ni una versión del modelo, y que sí describe la clasificación automática. Verificación: `cd App/Frontend; npm run test src/pages/ReportarIncidente/index.test.tsx` falla contra el texto vigente ("inteligencia artificial (Gemini)").
- [x] 4.2 GREEN: corregir el texto en `App/Frontend/src/pages/ReportarIncidente/index.tsx` (línea ~77) para eliminar el paréntesis `"(Gemini)"` y quedar agnóstico al proveedor. Verificación: `cd App/Frontend; npm run test src/pages/ReportarIncidente/index.test.tsx` en verde.
- [x] 4.3 TRIANGULATE: afirmar en la misma prueba que la nota informativa conserva el umbral del 70% y que la tarjeta mantiene la etiqueta "Sector Asignado por IA" sin cambios. Verificación: la prueba pasa con los casos agregados.

## 5. Verificación final

- [x] 5.1 Verificado (`grep -rn "Gemini" App/Frontend/src`): las menciones restantes son comentarios de código (no visibles) mas DOS textos visibles FUERA de alcance por decision (2026-11-07): el aviso legal de Privacidad (`Privacidad/privacidadContent.ts:60`, transferencia internacional, Ley 25.326 art. 6 — debe nombrar al proveedor) y la etiqueta de auditoria admin "Respuesta raw de Gemini" (`Administracion/DetalleIncidente.tsx:204`). Ninguna pertenece a la etapa del pipeline ni al portal de reporte.
  - Nota (apply c-177): quedan dos menciones visibles FUERA del alcance declarado del change y NO se tocaron por instruccion explicita: `src/pages/Privacidad/privacidadContent.ts:60` ("Gemini" en el texto de privacidad) y `src/pages/Administracion/DetalleIncidente.tsx:204` ("Respuesta raw de Gemini", seccion de auditoria). El resto de coincidencias son comentarios de codigo o aserciones negativas de test. Se documenta como deuda de alcance; no es una regresion introducida por c-177.
- [x] 5.2 Ejecutar la suite completa del frontend (`cd App/Frontend; npm run test`). Verificación: verde, sin aserciones que fijen el literal "Gemini".
- [x] 5.3 Ejecutar el linter del frontend (`cd App/Frontend; npm run lint`). Verificación: sin errores.
- [x] 5.4 Ejecutar `openspec validate "c-177-rotular-la-etapa-gemini-como-analisis-por-ia" --strict --no-interactive`. Verificación: PASS.
- [x] 5.5 Nota de cobertura: confirmar que `utils/formatters.ts` y `pages/ReportarIncidente/index.tsx` no están excluidos de cobertura en `App/Frontend/vitest.config.ts` (las exclusiones son `src/components/ui/**` y `src/components/layout/**`, quirk de `AGENTS.md`). Verificación: ambos archivos aparecen cubiertos por las pruebas de este change.

## 6. Deploy (manual)

- [x] 6.1 DEPLOY: hecho (`docker compose up -d --build frontend`, 2026-11-07; reconstruido el frontend con la correccion del import duplicado en `ReportarIncidente/index.test.tsx` que rompia `tsc`). Verificación: el bundle servido contiene "Análisis por IA" y "Gemini 2.5" = 0; el portal ya no nombra al proveedor; frontend healthy.
