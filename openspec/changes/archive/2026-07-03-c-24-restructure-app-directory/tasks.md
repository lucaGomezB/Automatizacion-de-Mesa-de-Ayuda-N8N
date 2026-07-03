## 1. Verificacion pre-movimiento

- [x] 1.1 Verificar que no hay cambios sin commitear (`git status` limpio)
- [x] 1.2 Ejecutar suite de tests del backend y confirmar que pasan (`cd Gestion_Incidentes; pytest`) — 208 passed, 1 skipped, 1 xfailed
- [x] 1.3 Ejecutar suite de tests del frontend y confirmar que pasan (`cd Frontend; npm run test`) — 68 passed
- [x] 1.4 Verificar que el directorio `App/` no existe en la raiz del repo

## 2. Movimiento de directorios con git mv

- [x] 2.1 Crear directorio `App/` en la raiz
- [x] 2.2 Mover backend: `git mv Gestion_Incidentes App/Backend`
- [x] 2.3 Mover frontend: `git mv Frontend App/Frontend`

## 3. Actualizar archivos de configuracion raiz

- [x] 3.1 Actualizar `docker-compose.yml` — 7 referencias: context, env_file, volumenes (cambiar `./Gestion_Incidentes` → `./App/Backend`, `./Frontend` → `./App/Frontend`)
- [x] 3.2 Actualizar `.github/workflows/ci.yml` — 10 referencias: working-directory, cache-dependency-path para ambos jobs
- [x] 3.3 Actualizar `openspec/config.yaml` — 2 referencias: `stack.backend.path` y `stack.frontend.path`
- [x] 3.4 Verificar `.gitignore` — confirmar que no requiere cambios (patrones genericos, no paths especificos)

## 4. Actualizar documentacion del proyecto

- [x] 4.1 Actualizar `AGENTS.md` — ~15 referencias en Component Map, dev commands, env vars, OpenAPI regen command
- [x] 4.2 Actualizar `CHANGES.md` — ~20 referencias en secciones "Leer antes" de cada cambio archivado
- [x] 4.3 Actualizar `README.md` — ~5 referencias en comandos de setup y seccion de frontend
- [x] 4.4 Actualizar `twilio/README.md` — 1 referencia a `Gestion_Incidentes/.env`

## 5. Actualizar scripts y knowledge-base

- [x] 5.1 Actualizar `scripts/run_provisional.py` — 4 referencias (ruta de .env y sys.path)
- [x] 5.2 Actualizar `knowledge-base/08_arquitectura_propuesta.md` — 2 referencias en el arbol de directorios
- [x] 5.3 Actualizar `knowledge-base/05_reglas_de_negocio.md` — 1 referencia
- [x] 5.4 Actualizar `knowledge-base/06_funcionalidades.md` — 2 referencias
- [x] 5.5 Actualizar `knowledge-base/04_modelo_de_datos.md` — 1 referencia
- [x] 5.6 Actualizar `knowledge-base/02_descripcion_general.md` — 2 referencias

## 6. Verificar funcionalidad post-movimiento

- [~] 6.1 Ejecutar `docker compose up -d` desde la raiz y verificar que todos los servicios inician — Docker no disponible en este entorno, no se puede ejecutar
- [~] 6.2 Ejecutar `docker compose ps` y confirmar que los 5 servicios estan healthy — Docker no disponible en este entorno
- [x] 6.3 Ejecutar suite de tests del backend desde `App/Backend/` y confirmar que pasan — 208 passed, 1 skipped, 1 xfailed
- [x] 6.4 Ejecutar suite de tests del frontend desde `App/Frontend/` y confirmar que pasan — 68 passed
- [~] 6.5 Verificar que `docker compose down` limpia correctamente — Docker no disponible en este entorno

## 7. Notificar cambios activos afectados

- [x] 7.1 Agregar nota en `openspec/changes/c-19-integration-tests-postgresql/proposal.md` indicando que los paths deben actualizarse a `App/Backend/`
- [x] 7.2 Agregar nota en `openspec/changes/c-23-dashboard-analytics-implementation/proposal.md` indicando que los paths deben actualizarse a `App/Backend/` y `App/Frontend/`
- [x] 7.3 Confirmar que `openspec/changes/c-20-tls-docker-compose/` no requiere actualizacion (sin proposal.md aun)

## 8. Commit y documentacion final

- [ ] 8.1 Revisar `git diff --staged` para confirmar que todos los cambios son intencionales
- [ ] 8.2 Crear commit unico con mensaje: `refactor: restructure App/ directory (Backend + Frontend)`
- [ ] 8.3 Verificar que `git log --follow -- App/Backend/app/main.py` muestra historial completo
- [ ] 8.4 Actualizar memoria de engram con la decision de reestructuracion
