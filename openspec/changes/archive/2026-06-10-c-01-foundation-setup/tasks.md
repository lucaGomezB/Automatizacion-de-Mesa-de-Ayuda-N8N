# Tasks — c-01-foundation-setup

## 1. Configuración OPSX

- [x] 1.1 Crear `openspec/config.yaml` con stack tecnológico, rutas canónicas (`Gestion_Incidentes/`, `Frontend/`, `knowledge-base/`, `CHANGES.md`) y convenciones del proyecto
- [x] 1.2 Verificar que `openspec list --json` y `openspec status --change "c-01-foundation-setup" --json` respondan sin error

## 2. Fix resolución del prompt de Gemini

- [x] 2.1 Escribir test (RED) que verifique que la ruta del prompt se resuelve correctamente con cwd en `Gestion_Incidentes/` y que un override por `GEMINI_PROMPT_PATH` es respetado
- [x] 2.2 Agregar `gemini_prompt_path` a `Settings` (`Gestion_Incidentes/app/config/settings.py`) con default anclado a la raíz del repo vía `Path(__file__)` (GREEN)
- [x] 2.3 Modificar `Gestion_Incidentes/app/classifiers/gemini_classifier.py` para usar `settings.gemini_prompt_path`; ante ruta inexistente: warning con ruta intentada + modo degradado sin impedir el arranque
- [x] 2.4 Verificar que el arranque desde `Gestion_Incidentes/` ya no emite `prompt_file_not_found` (smoke test de `create_app()`)

## 3. Base de datos: migraciones y catálogos

- [x] 3.1 Levantar PostgreSQL (`docker compose up -d` en `Gestion_Incidentes/`) y ejecutar `alembic upgrade head`
- [x] 3.2 Verificar catálogos sembrados: 3 sectores, 5 estados, 3 canales (query de conteo); confirmar idempotencia re-ejecutando `alembic upgrade head`
- [x] 3.3 N/A — Docker estaba disponible (Docker Desktop iniciado en la sesión); tareas 3.1 y 3.2 ejecutadas contra PostgreSQL real

## 4. Memoria compartida engram

- [x] 4.1 Ejecutar `engram sync` desde la raíz (filtro por proyecto — NUNCA `--all`) y verificar que `.engram/chunks/` se genera
- [x] 4.2 Confirmar que `.engram/` NO está en `.gitignore` (`git check-ignore .engram`) y versionarlo
- [x] 4.3 Documentar el workflow en `README.md`: `engram sync` antes de push, `engram sync --import` después de clone/pull

## 5. Cierre

- [x] 5.1 Correr la suite de tests del backend (`pytest`) y confirmar que no hay regresiones
- [x] 5.2 Actualizar `CHANGES.md`: marcar C-01 como `[x]` completado
