# Proposal: Incorporar los resultados de la campaña a la tesis

## Why

Tras ejecutar la campaña de campo (instrumento/protocolo de c-165/c-166/c-168 y
análisis de c-167), quedan mediciones que la tesis hoy declara como no medidas, no
contrastadas o no estimables: exactitud del brazo manual, tasa de intervención humana
(sub-hipótesis 2), efecto de orden, validación fuera de muestra y kappa con su IC.
Cerrar el programa de medición (c-165..c-169) exige incorporarlas al documento y retirar
las declaraciones que quedaron superadas. El diseño experimental corrió fuera del
repositorio; este change es solo documentación.

## What Changes

- `04-marco-metodologico.tex`: 4.4 (doble etiquetado + IC del kappa), 4.5 (procedimiento
  de campaña: brazo manual, orden contrabalanceado, instrumentación de intervención),
  4.7 (métricas e instrumentos de exactitud manual y tasa de intervención), 4.8 (análisis
  de efecto de orden y método de IC del kappa).
- `07-resultados.tex` (8.x): reportar exactitud manual, tasa de intervención, efecto de
  orden y kappa+IC como RESULTADOS nuevos; actualizar el estado de la sub-hipótesis 2
  (`:157-163`), hoy "no contrastada por ausencia de registro primario".
- `08-discusion.tex` / `10-recomendaciones.tex`: actualizar limitaciones donde se
  declararon no medidos (`08-discusion.tex:58`), incluida la corrección de la medición
  de intervención como línea futura ya saldada.
- `00-resumen.tex` (ES + abstract EN): actualizar estados/frases clave, respetando el
  tope de 250 palabras.
- `docs/Tesis/Correcciones/numeros-canonicos.md`: registrar los nuevos números canónicos
  (exactitud manual, tasa de intervención, kappa + IC, efecto de orden) con procedencia y
  estado; subir el IC del kappa de "no computable" a computado (`:198-209`).
- `docs/Tesis/Correcciones/dictamen-correcciones.md` y `CHANGES.md`: registrar los
  valores y abrir la FASE correspondiente.
- Retirar las declaraciones "no medido / no contrastado / no estimable" que estas
  mediciones superan (ítems de auditoría (a)-(e)).

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: cambian requisitos que declaran no-medición/no-computabilidad
  (IC del kappa; estado y rótulo de la sub-hipótesis de intervención humana; intervención
  por gate no medida; confundido de la rotación de operadores; sub-hipótesis de tiempo,
  intervención y exactitud) y se AGREGAN requisitos de reporte de exactitud del brazo
  manual, efecto de orden y validación fuera de muestra.
- `tesis-numeros-canonicos`: cambia el requisito de incertidumbre del kappa y de las
  métricas por clase (el IC del kappa pasa de "no estimable" a registrado con
  procedimiento).

## Impact

- `docs/Tesis/v10 (IA)/` (04, 07, 08, 10, 00), `docs/Tesis/Correcciones/` (números
  canónicos, dictamen), `CHANGES.md`. BAJA gobernanza, docs-only.
- Sin cambios en `App/`, `n8n/`, `evaluation/`, `openspec/config.yaml`, strings de
  categorías ni `docs/Tesis/v9 (IA)/`.
- Presupuesto de páginas: el cuerpo está en el tope de 100; señalar cada adición.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Cifras citadas sin procedencia de campaña | Med | Gate: registrar cada número con fuente (`numeros-canonicos.md`) antes de citarlo |
| Superar el tope de 100 páginas | Alta | Sustituir declaraciones retiradas por resultados; recortar prosa equivalente |
| Contaminar v9 | Baja | Alcance restringido a `v10 (IA)`; revisión de rutas en tareas |

## Rollback Plan

Revertir los archivos de `docs/Tesis/v10 (IA)/`, `docs/Tesis/Correcciones/` y `CHANGES.md`
al commit previo. No hay migraciones ni cambios de esquema; el repositorio de código queda
intacto.

## Dependencies

- c-165, c-166, c-167, c-168 aplicados. La **campaña de campo debe haberse ejecutado**
  (fuera del repositorio) para producir los números. Si no corrió, las tareas quedan
  planificadas y no ejecutadas.

## Success Criteria

- [ ] Los cinco valores nuevos están en `numeros-canonicos.md` con procedencia y estado.
- [ ] El IC del kappa se reporta con método y semilla; ya no se declara no computable.
- [ ] La sub-hipótesis 2 se declara contrastada con la tasa de intervención medida.
- [ ] `openspec validate --strict` en verde.
