## 1. Red de seguridad y delimitacion del alcance

- [x] 1.1 Ejecutar la suite del bloque de detalle en el estado previo (`cd App/Frontend; npm run test src/pages/Administracion/DetalleIncidente.test.tsx src/pages/Administracion/ValidarClasificacionDialog.test.tsx src/pages/Administracion/TicketDetailDialog.test.tsx`) y registrar la linea base (n pruebas en verde). Verificacion: el comando reporta la linea base sin fallos preexistentes.
- [x] 1.2 Localizar todas las referencias a la respuesta raw y a su etiqueta (`grep -rn "respuesta_raw\|Respuesta raw\|sector_predicho" App/Frontend/src`). Verificacion: las referencias de render quedan acotadas a `pages/Administracion/DetalleIncidente.tsx` y a las tres pruebas; el campo del tipo en `types/clasificacion.ts` es el unico NO alcanzado por el cambio.
- [x] 1.3 Confirmar que no cambia ningun archivo de backend, tipos ni API (`git status --short`). Verificacion: no aparecen archivos bajo `App/Backend/`, `App/Frontend/src/types/`, `openspec/config.yaml` ni `n8n/`.

## 2. Contrato de la UI (TDD estricto)

- [x] 2.1 RED: invertir en `App/Frontend/src/pages/Administracion/DetalleIncidente.test.tsx` las aserciones que hoy exigen la raw — reemplazar `expect(screen.getByText(/"sector_predicho"/))` por una asercion de ausencia y reformular el caso "omite la respuesta raw…" como "no muestra la respuesta raw aunque la clasificacion la aporte" (mock con `respuesta_raw` presente). Verificacion: `cd App/Frontend; npm run test src/pages/Administracion/DetalleIncidente.test.tsx` falla contra el componente vigente que si renderiza la raw.
- [x] 2.2 RED: invertir en `App/Frontend/src/pages/Administracion/ValidarClasificacionDialog.test.tsx` y `App/Frontend/src/pages/Administracion/TicketDetailDialog.test.tsx` las aserciones `expect(screen.getByText(/"sector_predicho"/))` por aserciones de ausencia, conservando las del resto del bloque de clasificacion/detalle. Verificacion: `cd App/Frontend; npm run test src/pages/Administracion/ValidarClasificacionDialog.test.tsx src/pages/Administracion/TicketDetailDialog.test.tsx` falla contra el componente vigente.
- [x] 2.3 GREEN: eliminar el bloque de la respuesta raw (~lineas 200-210, incluida la etiqueta "Respuesta raw de Gemini" y el `<pre>`) en `App/Frontend/src/pages/Administracion/DetalleIncidente.tsx`, sin tocar ningun otro campo del detalle. Cambio minimo para pasar 2.1 y 2.2. Verificacion: `cd App/Frontend; npm run test src/pages/Administracion/DetalleIncidente.test.tsx src/pages/Administracion/ValidarClasificacionDialog.test.tsx src/pages/Administracion/TicketDetailDialog.test.tsx` en verde.
- [x] 2.4 TRIANGULATE: agregar/ajustar aserciones que verifiquen que (a) la etiqueta "Respuesta raw de Gemini" NO aparece, (b) el contenido `"sector_predicho"` NO aparece, y (c) sector predicho, confianza, etapa, sector validado y sectores adicionales predichos/validados SI siguen renderizandose. Verificacion: las tres pruebas pasan con los casos agregados.
- [x] 2.5 REFACTOR: revisar que no queden importaciones ni variables huerfanas en `DetalleIncidente.tsx` tras retirar el bloque (por ejemplo `respuesta_raw` sin uso) y que el comentario de cabecera del componente refleje el contrato vigente; si no hay nada que mejorar, marcar como no aplicable. Verificacion: `cd App/Frontend; npm run lint` sin errores y las tres pruebas siguen en verde.

## 3. Verificacion de tipos y suite del frontend

- [x] 3.1 Ejecutar el type-check incluyendo los tests (`cd App/Frontend; npx tsc --noEmit`). Verificacion: sin errores de tipos (nota: `npm run build` corre `tsc`, que tambien type-checkea los `.test.tsx`).
- [x] 3.2 Ejecutar la suite completa del frontend (`cd App/Frontend; npm run test`). Verificacion: verde, sin aserciones del bloque retirado.
- [x] 3.3 Ejecutar `openspec validate "c-180-ocultar-la-respuesta-raw-de-la-clasificacion-en-la-ui" --strict --no-interactive`. Verificacion: PASS.

## 4. Despliegue (manual, NO ejecutar en apply)

- [x] 4.1 Desplegado (`docker compose up -d --build frontend`, 2026-11-07; mas `docker compose restart nginx` por DNS de upstream cacheado que causo 502). Verificacion: el bundle servido ya no contiene "Respuesta raw" (=0) ni el bloque `<pre>` de la raw; app y tunel publico en 200.
