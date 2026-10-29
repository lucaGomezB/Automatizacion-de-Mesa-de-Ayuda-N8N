# Design: Incorporar los resultados de la campaña a la tesis

## Context

La tesis declara hoy como no medidos / no contrastados / no estimables cuatro
resultados que la campaña produce: exactitud del brazo manual, tasa de intervención
humana, IC del kappa y efecto de orden (más la validación fuera de muestra). Los
enablers ya existen: instrumento/protocolo (c-165/c-166/c-168) y análisis (c-167). El
diseño experimental corre FUERA del repositorio; este change solo propaga resultados a
`docs/Tesis/v10 (IA)/`, al memo canónico y al tracking. Ver `proposal.md - Why`.

## Goals / Non-Goals

**Goals:**
- Sustituir declaraciones superadas por resultados medidos, con IC y procedencia.
- Registrar los valores en `numeros-canonicos.md` y subir el IC del kappa a computado.

**Non-Goals:**
- Ejecutar la campaña, recalcular métricas o tocar `evaluation/` (c-167).
- Introducir cifras nuevas sin artefacto de procedencia.

## Decisions

- **Capacidades**: `tesis-document` (comportamiento del documento) y
  `tesis-numeros-canonicos` (registro canónico). Alternativa: `skip_specs: true`
  (docs-only). Se descarta: el comportamiento textual exigido SÍ cambia (los requisitos
  que hoy ordenan declarar "no medido" pasan a ordenar reportar mediciones).
- **Kappa CI — MODIFIED, no ADDED**: el requisito y el escenario "Tabla recuperable"
  ya preveían el camino de recuperación; la campaña lo activa. Se modifican
  "Declaracion del intervalo de confianza del kappa" y "Intervalos de confianza del
  kappa y por clase en la tesis", preservando TODOS los nombres de escenario.
- **Rótulo de sub-hipótesis — REMOVED, no MODIFIED**: el requisito "Rotulo de la
  sub-hipotesis de intervencion humana como no contrastada" queda lógicamente invertido
  (ordenaba rotular como no contrastada). Se remueve con Reason/Migration; el nuevo
  comportamiento lo cubren los requisitos modificados de estado de hipótesis e
  intervención medida.
- **Nuevos reportes — ADDED**: exactitud del brazo manual, tasa de intervención por
  caso, efecto de orden y validación fuera de muestra se agregan como requisitos
  nuevos (comportamiento que no existía), no como modificaciones.
- **Gate por outputs de campaña**: cada tarea de escritura de cifras depende de que
  exista el artefacto de campaña correspondiente. Sin campaña, las tareas quedan
  planificadas y no se ejecutan (`tasks.md` §0).
- **Presupuesto de páginas**: se SUSTITUYEN declaraciones retiradas por resultados, no
  se agrega un capítulo; cada adición neta se señala y se compensa recortando prosa
  equivalente para no superar el tope de 100 páginas del cuerpo.

## Risks / Trade-offs

- [Cifra citada sin procedencia] → registro previo en `numeros-canonicos.md`; sin
  fuente, la tarea no se ejecuta.
- [Superar 100 páginas] → sustitución neta nula por defecto; recortes compensatorios.
- [Confundido de orden persiste] → escenario "Limitacion residual declarada" obliga a
  declararlo en vez de sobrevender el contrabalanceo.

## Migration Plan

Cambio aditivo de documentación. Aplicar en orden: (1) `numeros-canonicos.md`, (2)
capítulos 04/07, (3) 08/10, (4) resumen/abstract, (5) dictamen + `CHANGES.md`.
Rollback: revertir los archivos tocados al commit previo; sin migraciones.

## Open Questions

- Delimitador/formatos exactos de los artefactos de campaña (CSV vs JSON) no afectan
  specs ni tareas; se resuelven al ejecutar la campaña.
