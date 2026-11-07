## Context

Ver `proposal.md` (Why). Estado actual y restricciones que condicionan el enfoque:

- `App/Frontend/src/pages/Administracion/DetalleIncidente.tsx` es un componente presentacional de
  SOLO LECTURA y reutilizado (c-83, FRH-004). Renderiza el bloque de la respuesta raw en un `<pre>`
  dentro de la sección "Clasificación Automática" (~líneas 200-210), condicionado por
  `clasificacion.respuesta_raw`.
- Ese componente lo usan DOS superficies: `ValidarClasificacionDialog.tsx` (línea ~225) y
  `TicketDetailDialog.tsx` (línea ~107). Un cambio en el componente se refleja en ambas sin
  divergencia (FRH-004), que es exactamente el efecto buscado: ocultar la raw en las dos a la vez.
- El campo `respuesta_raw` existe en `App/Frontend/src/types/clasificacion.ts`
  (`ClasificacionLogRead`) y lo devuelve la API. Este change NO lo elimina: solo deja de renderizarlo.
- La etiqueta retirada es "Respuesta raw de Gemini" (`DetalleIncidente.tsx:204`). Su mención había
  quedado explícitamente FUERA de alcance en c-177 (decisión de alcance: privacidad + etiqueta de
  auditoría admin). c-180 la retira ahora, ampliando aquella decisión.
- El requisito FRH-003 (`openspec/specs/frontend-revision-humana/spec.md:42-59`) exige hoy la
  respuesta raw "cuando exista" y tiene el escenario "La clasificacion tiene respuesta raw". FRH-004
  (líneas 61-68) fija la consistencia entre superficies pero su escenario enumera campos de DETALLE
  DEL INCIDENTE (estado, sector, prioridad, canal, fechas, descripción), no campos del bloque de
  clasificación.

## Goals / Non-Goals

**Goals:**

- Dejar de renderizar la respuesta raw del clasificador en AMBAS superficies de detalle.
- Conservar sin cambios el resto del bloque de clasificación (sector predicho, confianza, etapa,
  sector validado, sectores adicionales predichos/validados) y el resto del detalle.
- Mantener `respuesta_raw` en el tipo y en la API para auditoría.
- Corregir el contrato FRH-003 y las pruebas que hoy fijan la presencia de la raw.

**Non-Goals:**

- No eliminar el campo `respuesta_raw` del tipo `ClasificacionLogRead` ni de la respuesta de la API.
- No alterar ningún comportamiento de backend, datos, DB ni esquema.
- No tocar ningún otro campo del bloque de clasificación ni del detalle del incidente.

## Decisions

### D1 — Retirar el bloque en el componente compartido, no en cada superficie

**Decisión: eliminar el bloque (~líneas 200-210) de `DetalleIncidente.tsx`.** Es la única superficie
que conoce el render de la raw; ambas pantallas lo reutilizan (FRH-004). Quitar el bloque allí cumple
el objetivo de "ocultarla en las dos a la vez" con un cambio mínimo y sin duplicar lógica.

Alternativa considerada: ocultarla solo en `ValidarClasificacionDialog`. Se descarta porque el usuario
eligió explícitamente ocultarla en TODAS las superficies, y porque mantenerla en el detalle del ticket
rompería la consistencia FRH-004 (una superficie mostraría la raw y la otra no).

### D2 — Conservar `respuesta_raw` en el tipo y en la API

**Decisión: no tocar `ClasificacionLogRead` ni el backend.** El dato sigue disponible para auditoría
vía la API; el change es estrictamente de presentación. Esto mantiene el cambio en governance LOW
(sin cambios de esquema, contrato ni datos) y evita romper consumidores que hoy tipan el campo.

Alternativa considerada: eliminar el campo del tipo por higiene. Se descarta: rompería el contrato con
la API (que sigue devolviéndolo), exigiría tocar backend y elevaba el alcance y el riesgo sin beneficio
observable para el operador.

### D3 — FRH-003 se MODIFICA; FRH-004 no requiere cambio

**Decisión: modificar únicamente FRH-003 en el delta.** El comportamiento de FRH-003 cambia (deja de
exigir el render de la raw), por lo que es un MODIFIED. Para FRH-004, su escenario lista campos de
detalle del incidente y no enumera el bloque de clasificación; la consistencia entre superficies se
preserva automáticamente porque ambas comparten `DetalleIncidente`. Modificar FRH-004 sin un cambio de
comportamiento real añadiría ruido al delta, contra la guía de OpenSpec ("no inventar un requisito").

**Manejo del escenario "La clasificacion tiene respuesta raw" (mecánica del validador estricto):** en
un bloque MODIFIED, el validador trata un escenario RENOMBRADO como removido y puede fallar
`--strict`. Por eso se CONSERVA el encabezado exacto del escenario y se reescribe únicamente su cuerpo
(`THEN`) para afirmar que el diálogo NO muestra la respuesta raw. El `WHEN` mantiene la condición
"la clasificacion incluye `respuesta_raw`", de modo que el escenario sigue siendo significativo
(dispara la condición y verifica su ausencia visual) sin renombrarlo. El cuerpo del requerimiento se
edita para retirar `respuesta_raw` del conjunto exigido y añadir la prohibición explícita ("NO SHALL
mostrarse").

### D4 — Estrategia de prueba (TDD estricto)

**Decisión: invertir las aserciones existentes en las tres pruebas que hoy afirman la presencia de la
raw.**

- `DetalleIncidente.test.tsx`: la aserción `expect(screen.getByText(/"sector_predicho"/))` del caso
  feliz se reemplaza por una que verifica ausencia; el caso "omite la respuesta raw cuando la
  clasificacion no la aporta" se reformula como "no muestra la respuesta raw aunque la clasificacion
  la aporte" (con el mock que SÍ la trae), que es el contrato nuevo.
- `ValidarClasificacionDialog.test.tsx`: la prueba "muestra la clasificacion completa incluida la
  respuesta raw" pierde la aserción de raw y verifica que el bloque de clasificación sigue presente
  (confianza, etapa) mientras la raw NO aparece; el mock `respuesta_raw` puede conservarse para
  demostrar que el campo existe pero no se renderiza.
- `TicketDetailDialog.test.tsx`: se reemplaza `expect(screen.getByText(/"sector_predicho"/))` por una
  aserción de ausencia, conservando las del resto del detalle compartido.

Se añade al menos una aserción de AUSENCIA de la etiqueta "Respuesta raw de Gemini" además del
contenido `"sector_predicho"`, para cubrir tanto la etiqueta como el `<pre>`.

Alternativa considerada: crear un test nuevo aislado. Se descarta: las pruebas existentes ya fijan el
contrato del bloque de clasificación; solo hay que invertir la expectativa de la raw.

## Risks / Trade-offs

- [Queda una aserción `"sector_predicho"` que ahora falla por el componente corregido] → Mitigación:
  localizar todas las referencias (`grep -rn "sector_predicho\|respuesta raw" App/Frontend/src`) antes
  de editar; las tres pruebas están identificadas en `proposal.md`.
- [Retirar por accidente campos legítimos del bloque] → Mitigación: el diff se acota a ~líneas
  200-210; el resto de `DetalleIncidente` no se toca y las pruebas del bloque siguen en verde.
- [Reintroducir la mención del proveedor en la UI] → Beneficio: el cambio además elimina la etiqueta
  "Respuesta raw de Gemini" del detalle, alineado con el objetivo de c-177 de reducir menciones de
  proveedor en la interfaz.

## Migration Plan

- No hay migración de datos ni de esquema. El cambio se despliega con el bundle del frontend
  (`docker compose up -d --build frontend`, tarea manual, NO se ejecuta en apply).
- Rollback: `git revert` del commit del change (ver `proposal.md`, Rollback Plan).

## Open Questions

Ninguna. El alcance (ocultar en ambas superficies) y el destino del campo (conservarlo en el tipo y la
API) quedan fijados en D1 y D2; no hay decisiones diferidas que puedan alterar specs o tareas.
