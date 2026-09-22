## 1. Guarda de regresión estructural (RED)

- [x] 1.1 Escribir el test estructural que aserta que el `jsCode` de `Se verifica lo que trajo la IA` referencia `$('Sellar ingreso telefonia').first()` y NO referencia `$('Sellar ingreso telefonia').item`; confirmar RED (el código actual usa `.item`). Verificación: el test falla antes de la corrección.
- [x] 1.2 Escribir el test estructural que aserta que el `jsCode` de `Derivar a revision humana` referencia `$('Sellar ingreso telefonia').first()` y NO `.item`; confirmar RED. Verificación: el test falla antes de la corrección.
- [x] 1.3 Escribir el test estructural del fallback: ante sello ausente el validador fija `requiere_revision_humana` y `revision_forzada` verdaderos, emite un WARN y NO retorna null en silencio; el normalizador propaga el marcador y la revisión; confirmar RED. Verificación: el test falla antes de la corrección.
- [x] 1.4 Verificar que el test existente del body del POST (`ingresado_en` por expresión) y `test_c39_telefonia_preserva_ingreso_a_traves_del_agente` siguen siendo válidos y no entran en conflicto con los nuevos; ajustar nombres/aserções si corresponde. Verificación: la suite estructural corre y reporta los nuevos casos en rojo y los previos en verde.

## 2. Corrección del workflow N8N (GREEN)

- [x] 2.1 En `Se verifica lo que trajo la IA`, reemplazar la recuperación `.item` por `$('Sellar ingreso telefonia').first().json.ingresado_en`; ante sello ausente, emitir `console.warn` estructurado y fijar `ingreso_sellado_ausente=true`, `revision_forzada=true` y `requiere_revision_humana=true` en ambas ramas, sin abortar. Verificación: tests 1.1 y 1.3 en verde.
- [x] 2.2 En `Derivar a revision humana`, reemplazar `.item` por `.first()` en la recuperación del item sellado; ante sello ausente, emitir WARN y continuar la fusión del item corrente conservando `requiere_revision_humana=true`. Verificación: test 1.2 en verde.
- [x] 2.3 Confirmar que `Normalizar entrada del incidente` propaga `revision_forzada`, `requiere_revision_humana` y el marcador sin alterar el body del POST; verificar que `ingresado_en` sigue enviándose por expresión y puede ser nulo. Verificación: test 1.4 en verde.
- [x] 2.4 Correr la suite estructural completa `pytest tests/test_n8n_workflow.py` en `App/Backend` y verificar que no hay regresiones. Verificación: suite en verde.

## 3. Contrato del backend sin cambios

- [x] 3.1 Verificar que no se modifica `IncidenteCreate.ingresado_en`, sus validadores, `IncidenteService` ni migraciones; que el flag `clasificacion.requiere_revision_humana` sigue siendo honrado por el backend. Verificación: `git diff` no muestra cambios en `App/Backend/app/` ni en `alembic/`; `pytest tests/test_openapi_sync.py -v` en verde.

## 4. Documentación

- [x] 4.1 Actualizar `docs/n8n-workflow-guide.md` con la recuperación robusta del sello, el comportamiento ante sello ausente (WARN + revisión humana + ticket creado) y el caveat de que la verificación es estructural y requiere una ejecución N8N en vivo. Verificación: la guía describe el comportamiento y, si declara conteos, coinciden con el workflow y la suite.

## 5. Verificación de integración y en vivo

- [x] 5.1 Correr `pytest -m "not integration"` en `App/Backend` y verificar que no hay regresiones. Verificación: suite offline en verde.
- [ ] 5.2 Verificación manual en N8N en vivo (obligatoria, fuera de CI): importar el `workflow.json` y ejecutar el canal telefónico con una transcripción de prueba; confirmar que el incidente persiste `ingresado_en` no nulo. Verificación: registro del incidente con `ingresado_en` presente. (pendiente de verificación manual en N8N en vivo — aprobado dejar documentado)
- [ ] 5.3 Verificación manual del fallback en N8N en vivo: forzar que el sello no resuelva y confirmar WARN estructurado, `requiere_revision_humana=true` y ticket creado (la ejecución no aborta). Verificación: incidente creado con revisión pendiente y log WARN visible. (pendiente de verificación manual en N8N en vivo — aprobado dejar documentado)
- [x] 5.4 Verificación final: `openspec validate --strict --changes c-46-telefonia-ingreso-sellado` en verde y evidencia RED/GREEN registrada por tarea. Verificación: validación estricta sin errores.