## 1. Plantilla y schema de doble etiquetado

- [ ] 1.1 Definir el schema tidy (`id_caso`, `id_etiquetador`, `sector_asignado`, `sectores_adicionales`, `timestamp`) y verificar que documenta las cinco cadenas canonicas exactas
- [ ] 1.2 Crear la plantilla versionada (CSV con cabecera + variante JSON equivalente) en `evaluation/data/` y verificar que abre sin error y comparte el mismo schema

## 2. Validador offline (TDD)

- [ ] 2.1 Escribir test que exige dos `id_etiquetador` distintos por caso y verificarlo en RED
- [ ] 2.2 Implementar `validate_double_labeling` minimo para pasar el test de cobertura por caso (GREEN)
- [ ] 2.3 Agregar tests de cobertura incompleta, `(id_caso, id_etiquetador)` duplicado y sector fuera del conjunto canonico, y generalizar el validador (TRIANGULATE)
- [ ] 2.4 Agregar CLI fino que lee una ruta y devuelve exit code no cero con caso/celda ofensor, y verificar el comportamiento con un fixture invalido
- [ ] 2.5 Refactorizar el validador (nombres, constantes de cadenas canonicas) con la suite en verde (REFACTOR)

## 3. Protocolo de doble etiquetado (runbook)

- [ ] 3.1 Escribir el runbook con elegibilidad, cegado (no ver consenso ni al par) y mismo codebook, y verificar que cubre los tres puntos
- [ ] 3.2 Documentar tamano de muestra (200 casos o subconjunto justificado) y criterios de aceptacion (cobertura completa, sin celdas faltantes) en el runbook

## 4. Ruta de recuperacion opcional

- [ ] 4.1 Implementar importador que mapea data parcial por etiquetador original al schema y lo pasa por el validador, y verificar con un fixture de recuperacion
- [ ] 4.2 Documentar en el runbook que el re-etiquetado es el camino por defecto y la recuperacion es opcional

## 5. Verificacion

- [ ] 5.1 Correr la suite offline de `evaluation/` desde `evaluation/` y verificar cobertura de los escenarios ECM-008..010
- [ ] 5.2 Ejecutar `openspec validate "c-168-plantilla-y-protocolo-de-doble-etiquetado" --strict --no-interactive` y verificar que pasa
