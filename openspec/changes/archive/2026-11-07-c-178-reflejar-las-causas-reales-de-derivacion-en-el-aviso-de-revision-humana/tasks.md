## 1. Red de seguridad y delimitación del alcance

- [x] 1.1 Ejecutar la prueba del aviso en el estado previo (`cd App/Frontend; npm run test src/pages/Administracion/index.aviso.test.tsx`) y registrar la línea base (n pruebas en verde). Verificación: el comando reporta la línea base sin fallos preexistentes.
- [x] 1.2 Localizar todas las referencias al texto vigente del aviso (`grep -rn "confianza inferior al 70" App/Frontend/src`). Verificación: la búsqueda devuelve únicamente `pages/Administracion/index.tsx` y `pages/Administracion/index.aviso.test.tsx`.
- [x] 1.3 Confirmar que no cambia ningún archivo de backend (`git status --short`). Verificación: no aparecen archivos bajo `App/Backend/`, `openspec/config.yaml` ni `n8n/`.

## 2. Contrato del aviso (TDD estricto)

- [x] 2.1 RED: actualizar `App/Frontend/src/pages/Administracion/index.aviso.test.tsx` con el nuevo literal `TEXTO_ESPERADO` (las tres causas) y reemplazar el matcher por regex por un fragmento estable de la nueva redacción. Verificación: `cd App/Frontend; npm run test src/pages/Administracion/index.aviso.test.tsx` falla contra el texto vigente del banner.
- [x] 2.2 GREEN: reescribir el `<p>` del aviso en `App/Frontend/src/pages/Administracion/index.tsx` (~444-447) con la redacción fijada en `design.md` (D1), conservando el cierre "Revisá y confirmá el sector correcto para cada uno". Cambio mínimo para pasar 2.1. Verificación: `cd App/Frontend; npm run test src/pages/Administracion/index.aviso.test.tsx` en verde.
- [x] 2.3 TRIANGULATE: agregar a `index.aviso.test.tsx` aserciones que verifiquen que el aviso menciona la etapa de respaldo y el reportante no identificado, que conserva el cierre de validación, que mantiene "70%" y que sigue sin contener "gemini"/"flash". Verificación: la prueba pasa con los casos agregados.
- [x] 2.4 REFACTOR: revisar que el literal de la prueba y el texto del componente mantengan una única redacción coherente; si no hay nada que mejorar, marcar como no aplicable. Verificación: `cd App/Frontend; npm run test src/pages/Administracion/index.aviso.test.tsx` sigue en verde.

## 3. Verificación de tipos y suite del frontend

- [x] 3.1 Ejecutar el type-check incluyendo los tests (`cd App/Frontend; npx tsc --noEmit`). Verificación: sin errores de tipos.
- [x] 3.2 Ejecutar la suite completa del frontend (`cd App/Frontend; npm run test`). Verificación: verde, sin aserciones del literal retirado.
- [x] 3.3 Ejecutar `openspec validate "c-178-reflejar-las-causas-reales-de-derivacion-en-el-aviso-de-revision-humana" --strict`. Verificación: PASS.

## 4. Despliegue (manual, no ejecutar en apply)

- [x] 4.1 Desplegado (`docker compose up -d --build frontend`, 2026-11-07, exit 0; frontend healthy). Verificación: el bundle servido (`index-BOcF40yD.js`) contiene "requieren revisión humana" y "reportante no fue identificado"; el texto viejo "confianza inferior al 70" ya no aparece.
