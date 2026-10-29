# Design: Plantilla y protocolo de doble etiquetado

## Context

El corpus solo conserva el consenso `sector_asignado`/`sectores_adicionales`; no hay
etiquetas por etiquetador, por lo que la tabla primaria de acuerdo no existe
(`numeros-canonicos.md:198-209`). c-167 (`evaluation/kappa.py`) ya consume una tabla
primaria en forma de registros por caso+etiquetador (ver proposal.md de c-167). El
etiquetado real corre fuera del repositorio; aqui solo se entrega el enabler offline.
Ver `proposal.md - Why`.

## Goals / Non-Goals

**Goals:**
- Definir el contrato de datos (schema) que c-167 consumira para kappa + IC.
- Entregar plantilla + validador offline y runbook de independencia/cegado.

**Non-Goals:**
- Ejecutar el etiquetado o recolectar datos de campo (fuera del repo).
- Calcular kappa o IC (eso es c-167); tocar strings de categorias o numeros canonicos.

## Decisions

- **Capability reutilizada**: c-168 AGREGA ECM-008..010 a
  `evaluation-campaign-instrumentation` (c-165/c-166). Alternativa considerada:
  capability propia (`double-labeling`); se descarta para no fragmentar el instrumento de
  campana. Secuencia de archivo: c-165, c-166, luego c-168.
- **Formato de plantilla: tidy/largo** (una fila por `id_caso`+`id_etiquetador`) sobre
  formato ancho (columnas por etiquetador). Razon: escala con N etiquetadores, encaja
  con validacion por celda y con el consumo de c-167. La plantilla se versiona en
  `evaluation/data/` (CSV cabecera + variante JSON, mismo schema).
- **Ubicacion del codigo**: modulo puro offline en `evaluation/` (p. ej.
  `double_labeling.py`), stdlib solo, reutilizando el cargador de `evaluation/corpus.py`.
  Validador = funcion pura `validate_double_labeling(registros, casos_objetivo)` + CLI
  fino que lee ruta y devuelve exit code no cero con el caso/celda ofensor.
- **Independencia/cegado**: no es forzable tecnicamente en un archivo; el validador
  verifica independencia estructural (>=2 `id_etiquetador` distintos por caso, sin
  duplicados) y el runbook impone el cegado procedimental (no ver consenso ni al par).
- **Ruta de recuperacion**: importador opcional que mapea data parcial por etiquetador
  original al MISMO schema y pasa por el mismo validador; por defecto, re-etiquetado.
- **Contrato con c-167**: el schema (campos ECM-008) es la interfaz estable; c-167 no
  cambia si la data proviene de re-etiquetado o de recuperacion.

## Risks / Trade-offs

- [Etiquetadores ven el consenso y sesgan] -> cegado en runbook + validacion de
  independencia estructural; no hay control tecnico adicional (trade-off aceptado).
- [Muestra de 200 casos es costosa] -> el runbook permite subconjunto justificado con
  criterio de aceptacion explicito.
- [Deriva de strings de categoria] -> validador compara contra las cinco cadenas exactas
  y falla accionable.
- [Solapamiento con c-167] -> limite explicito: aqui se define/valida la tabla, c-167 la
  consume; sin logica de kappa en este change.

## Migration Plan

Cambio aditivo (docs + modulo offline), sin migraciones de DB ni de esquema del corpus.
Rollback: eliminar plantilla, validador, tests y runbook; el corpus y c-167 quedan
intactos.

## Open Questions

- Delimitador exacto de la plantilla CSV (coma vs punto y coma) se fija al implementar
  segun el resto de `evaluation/data/`; no altera specs ni tareas.
