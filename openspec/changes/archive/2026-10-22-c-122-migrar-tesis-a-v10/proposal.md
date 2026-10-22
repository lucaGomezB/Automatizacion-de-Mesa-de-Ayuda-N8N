## Why

El equipo decidio que la proxima ronda de correcciones de la tesis (las recomendaciones residuales del dictamen CONEAU v1.0.1) se aplique sobre una version de trabajo NUEVA, `v10`, y no sobre `v9`, que queda congelada como version previamente publicada (tag `v1.0.1`). Antes de editar contenido se necesita una version de trabajo v10 que sea copia fiel de v9 y que los punteros activos del proyecto (config, roadmap y spec principal) resuelvan a v10, de modo que el trabajo futuro no toque la version congelada. Este change es la migracion prerequisito: NO aplica las recomendaciones editoriales (eso es c-121, que depende de este) ni crea el tag de release (paso de cierre de c-121).

## What Changes

- **S1 - Copia de trabajo v10:** espejo completo de `docs/Tesis/v9 (IA)/` a `docs/Tesis/v10 (IA)/` (fuente LaTeX, figuras y assets, bibliografia, scripts de verificacion y disclaimer, los dos `.docx`, los textos extraidos y los artefactos de compilacion). `docs/Tesis/v9 (IA)/` queda intacto como version previamente publicada.
- **S2 - Repunte de punteros activos:** `openspec/config.yaml` (campo `thesis:`), `CHANGES.md` (entrada nueva fechada + punteros de estado actual), `openspec/specs/tesis-document/spec.md` (rutas activas) y, por coordinacion de dependencia, los artefactos de c-121 que hoy apuntan a v9 y que deben editar v10 al aplicarse.
- **S3 - Fuera de alcance:** no se toca el contenido de la tesis, ni `docs/Tesis/v9 (IA)/`, ni el dictamen (`auditorias/`), ni las bitacoras (`docs/Tesis/Correcciones/`), ni changes archivados, ni codigo de aplicacion (`App/`, `n8n/`, `data/`, `evaluation/`), ni los tags de git.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tesis-document`: se agrega un requisito que fija la version de trabajo vigente de la tesis en `docs/Tesis/v10 (IA)/` y exige que los punteros activos del proyecto resuelvan a v10, preservando `docs/Tesis/v9 (IA)/` intacto como version previamente publicada y sin reescribir registros historicos.

## Impact

- Nuevo: `docs/Tesis/v10 (IA)/` (espejo completo de `docs/Tesis/v9 (IA)/`, 61 archivos en el arbol de trabajo, 60 versionados).
- Edita: `openspec/config.yaml`, `CHANGES.md`, `openspec/specs/tesis-document/spec.md`; por coordinacion, `openspec/changes/c-121-observaciones-dictamen-v1-0-1/{proposal,design,tasks}.md`.
- No toca: `docs/Tesis/v9 (IA)/`, `auditorias/`, `docs/Tesis/Correcciones/`, `openspec/changes/archive/`, `App/`, `n8n/`, `data/`, `evaluation/`, contenido de la tesis ni ningun tag de git.
- Dependencia: c-122 es prerequisito de c-121 (el trabajo editorial de c-121 se aplica sobre v10).
- Rollback: `rm -rf "docs/Tesis/v10 (IA)"` y `git checkout -- openspec/config.yaml CHANGES.md openspec/specs/tesis-document/spec.md openspec/changes/c-121-observaciones-dictamen-v1-0-1/`; v9 nunca se modifica, por lo que no hay riesgo para la version publicada.
- Criterios de exito: existe `docs/Tesis/v10 (IA)/`; los punteros activos resuelven a v10; `docs/Tesis/v9 (IA)/` permanece sin cambios (`git status` limpio para esa ruta); `openspec validate c-122-migrar-tesis-a-v10 --strict` pasa.
