# Tasks: Instrumentar la campana (brazo manual e intervencion)

## 1. Instrumento de captura del brazo manual (ECM-001)

- [ ] 1.1 Definir el esquema de la planilla/CSV offline (id_corpus, id_etiquetador, sector, adicionales) y verificarlo contra el corpus pseudonimizado
- [ ] 1.2 Crear el archivo plantilla del instrumento en `data/` sin PII y verificar que no incluye campos personales
- [ ] 1.3 Documentar en el runbook que el etiquetado es por caso y por etiquetador, con >=2 etiquetadores independientes, y verificar la seccion existe
- [ ] 1.4 Agregar una prueba que valide el esquema del CSV (columnas y tipos) y verificar que pasa en el subset SQLite

## 2. Registro de intervencion humana (ASG-005 modificado) — CHECKPOINT AUDITORIA

- [ ] 2.1 CHECKPOINT: solicitar CONFIRMACION HUMANA explicita antes de aplicar cualquier cambio de schema en `clasificacion_log` (governance ALTA)
- [ ] 2.2 Extender el modelo `ClasificacionLog` con `validado_por_empleado_id` (FK empleado, SET NULL), `validado_en` y `origen_intervencion`, y verificar que el modelo importa sin error
- [ ] 2.3 Validar `origen_intervencion` contra el conjunto `gate|review|sample|manual_completion|reassignment` y verificar con un test que un valor invalido es rechazado
- [ ] 2.4 Crear la migracion Alembic nueva (columnas nullable + FK) sin mutar `001` y verificar `alembic upgrade head` y `downgrade` en PostgreSQL
- [ ] 2.5 Persistir actor, instante propio y origen en `set_validated_sector`/repositorio y verificar con test unitario SQLite
- [ ] 2.6 Propagar `current_user` (id de empleado, sin PII) desde el route de validacion al servicio y verificarlo con test de integracion
- [ ] 2.7 Verificar que el delta antes/despues es reconstruible desde `sector_id_predicho`/`sectores_predichos` vs validado con un test de integracion
- [ ] 2.8 Verificar que un log sin intervencion queda con metadatos NULL (estado no intervenido) con un test unitario

## 3. Metrica de intervencion real (ECM-003)

- [ ] 3.1 Agregar `contar_intervenciones` en `estadisticas_repository` filtrando por `validado_en` no nulo en rango y verificarlo con test unitario
- [ ] 3.2 Exponer `tasa_intervencion_humana` en `estadisticas_service` junto a `tasa_revision_humana` y verificar con test de servicio
- [ ] 3.3 Verificar con test que la tasa cuenta solo intervenciones efectivas (no todos los marcados `requiere_revision_humana`)

## 4. Protocolo de campana (ECM-002)

- [ ] 4.1 Escribir el runbook de campana en `docs/` (sujetos, minimo de casos, independencia, instrumento, aceptacion/verificacion) y verificar que cubre ambos datasets
- [ ] 4.2 Verificar que el runbook referencia el instrumento offline y la metrica de intervencion sin depender de conocimiento tacito

## 5. Cierre

- [ ] 5.1 Ejecutar el subset SQLite (`pytest -m "not integration"`) y verificar verde
- [ ] 5.2 Ejecutar el subset PostgreSQL (`pytest -m integration`) y verificar verde
- [ ] 5.3 Ejecutar `openspec validate "c-165-instrumentar-la-campana-para-medir-el-brazo-manual-y-la-intervencion" --strict --no-interactive` y verificar verde
