# Design: Reportar la proporción de tiempo de la campaña

## Context

Ver `proposal.md` — Why. La campaña complementaria de medición midió la variable
intervención humana en sus dos dimensiones rotuladas: proporción de casos (reportada:
`73,5 %`, `07-resultados.tex`, `subsec:reduccion-intervencion`) y proporción del tiempo
(NO reportada en ningún pasaje). El valor existe y está registrado en el memo canónico
(`docs/Tesis/Correcciones/numeros-canonicos.md`, Sección 3.14, rama (b') "estimable"),
procedente de `evaluation/data/campana/analisis/resultados.json:910-927`:

- Proporción `0,5307`, IC bootstrap `[0,4407; 0,6111]` (`B = 2000`, semilla `20261021`).
- Cobertura `0,9388` (mayor o igual que `0,80`); casos intervenidos `147`, con duración
  completa `138`.
- Limitación: el denominador es el tiempo de registro automatizado más la duración de la
  intervención, no el tiempo total de atención.

La spec principal exige reportarla en dos requisitos vigentes tras c-169:
"Intervención humana reportada según el registro de la campaña de medición" (cláusula de
la proporción del tiempo) y "Reporte de la tasa de intervencion humana de la campaña de
medicion" (que fija la ubicación en `subsec:reduccion-intervencion`).

## Goals / Non-Goals

**Goals:**
- Cerrar la omisión: el valor de la proporción de tiempo queda reportado en el cuerpo.
- Cerrar el desajuste entre la definición anunciada y el denominador efectivamente medido.
- Hacer el requisito explícito y verificable para que la omisión no se repita.

**Non-Goals:**
- Recalcular, redondear o modificar cualquier valor (memo 3.14 es la fuente; no se edita).
- Tocar `evaluation/` (los datos crudos son de c-167) ni `02-*`/código.
- Reescribir la proporción de casos (73,5 %), el veredicto de (b) ni el resto de (a)-(e).
- Recortar páginas: eso es c-184; este change no asume sus ediciones.

## Decisions

### D-ubicacion: reportar en `subsec:reduccion-intervencion`

La proporción del tiempo es la segunda dimensión de la MISMA variable que la proporción
de casos (ambas "formas rotuladas" de `tab:variables`). El requisito "Reporte de la tasa
de intervencion humana de la campaña de medicion" ubica ambas en
`subsec:reduccion-intervencion`. Reportar el valor ahí, en la misma oración o
inmediatamente después de la proporción de casos y su desglose, mantiene juntas las dos
dimensiones y evita partir la variable en dos subsecciones.

Alternativas consideradas:
- `subsec:resultados-campana-medicion` (donde viven (a), (c), (d) y (e)): la proporción
  de casos (b) NO está ahí, de modo que (b') quedaría separada de su dimensión hermana.
  Descartada por incoherencia interna.
- Reportar en AMBAS: duplicaría el valor y crearía dos fuentes de verdad. Descartada.

### D-valores: cita literal, sin redondeo

Se citan los valores del memo tal cual (`0,5307`, `[0,4407; 0,6111]`, `0,9388`, `147`,
`138`, `B = 2000`, semilla `20261021`). En LaTeX, decimal con llave (`0{,}5307`) según la
convención del manuscrito. El valor NO se presenta como sustituto de ningún canónico.

### D-desambiguacion: el anuncio de `04:69`

`04-marco-metodologico.tex:69` anuncia la dimensión como "la proporción del tiempo
dedicado a tareas manuales sobre el tiempo total del proceso", mientras el denominador
efectivamente medido es el tiempo de registro automatizado más la duración de la
intervención. Para que el lector no lea una inconsistencia, el párrafo SHALL precisar el
denominador y remitir con `\autoref` a `subsec:reduccion-intervencion`. Se acota a una
cláusula para no arrastrar `tab:variables` (`04:34`), cuya etiqueta "proporción del
tiempo del proceso" se conserva (la fija el requisito "Subseccion de correccion de la
medicion de intervencion humana").

### D-spec: MODIFIED sobre el requisito de reporte

El requisito "Reporte de la tasa de intervencion humana de la campaña de medicion" YA
menciona la proporción de tiempo, pero de forma genérica ("o la declaración no
estimable"). Se MODIFICA para hacer explícito el camino positivo (estimación puntual,
intervalo bootstrap, cobertura, tamaños y limitación del denominador) y se agrega un
escenario que fija los valores observados. No se crea un requisito nuevo: duplicaría la
cláusula y generaría dos requisitos sobre el mismo comportamiento.

## Risks / Trade-offs

- [Más páginas] → la oración agrega texto; se registra el impacto para el cierre de
  release y se coordina con c-184, que recorta. Si c-184 reescribe `04:69`, la cláusula
  se aplica sobre el texto resultante.
- [Colisión de líneas con c-184] → editar `04:69` como cláusula mínima; si c-184 ya tocó
  la línea, se reaplica sobre su resultado (merge textual, no semántico).
- [Desalineación con `tab:variables`] → se conserva la etiqueta de `04:34`; la limitación
  del denominador se declara donde el valor se reporta, no se cambia la etiqueta.

## Migration Plan

1. Confirmar (read-only) la ausencia del valor y su presencia en el memo 3.14.
2. Agregar la oración en `subsec:reduccion-intervencion`.
3. Desambiguar `04:69`.
4. Verificar (grep + neutralidad de valores canónicos) y registrar en el cierre.

Rollback: revertir el commit del change; no hay migraciones ni estado derivado.

## Open Questions

- Ubicación definitiva: se elige `subsec:reduccion-intervencion` por coherencia con (b);
  los autores pueden optar por duplicar una remisión desde
  `subsec:resultados-campana-medicion` al aplicar, sin mover el valor.
