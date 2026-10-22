## 1. Crear la copia de trabajo v10 (S1)

- [x] 1.1 Crear el espejo completo con `cp -r "docs/Tesis/v9 (IA)" "docs/Tesis/v10 (IA)"` (desde la raiz del repo); verificar que existen `docs/Tesis/v10 (IA)/paper/main.tex`, `docs/Tesis/v10 (IA)/Bibliography_base.bib`, `docs/Tesis/v10 (IA)/tesis_completa_extraida.txt` y `docs/Tesis/v10 (IA)/tesis_para_evaluacion.txt`
- [x] 1.2 Verificar la paridad del espejo: `git ls-files "docs/Tesis/v10 (IA)" | wc -l` es 60 e igual a `git ls-files "docs/Tesis/v9 (IA)" | wc -l`, y `diff -rq "docs/Tesis/v9 (IA)" "docs/Tesis/v10 (IA)"` no reporta diferencias
- [x] 1.3 Confirmar que la version publicada no cambio: `git status --short "docs/Tesis/v9 (IA)"` no reporta ninguna ruta (sin agregados, modificados ni borrados bajo v9)

## 2. Repuntar los punteros activos (S2)

- [x] 2.1 En `openspec/config.yaml`, repuntar `thesis:` de `docs/Tesis/v7/tesis_para_agente.md` a `docs/Tesis/v10 (IA)/tesis_completa_extraida.txt` (decision D2 de `design.md`); verificar que `grep -n "thesis:" openspec/config.yaml` devuelve el valor nuevo
- [x] 2.2 En `openspec/specs/tesis-document/spec.md`, repuntar las rutas activas `docs/Tesis/v9 (IA)` a `docs/Tesis/v10 (IA)` (5 ocurrencias, lineas ~434, 2227, 2262, 2766, 2796); verificar `grep -c "docs/Tesis/v9 (IA)" openspec/specs/tesis-document/spec.md` es 0 y `grep -c "docs/Tesis/v10 (IA)" openspec/specs/tesis-document/spec.md` es 5
- [x] 2.3 Confirmar que `AGENTS.md` no requiere cambios: `grep -c "v9" AGENTS.md` es 0 (no contiene ninguna referencia a v9); no modificar el archivo

## 3. Registrar la migracion en el roadmap (S2 - CHANGES.md)

- [x] 3.1 En `CHANGES.md`, agregar una entrada nueva fechada `Actualizacion 2026-10-22 (migracion de la tesis a v10)` a continuacion de la entrada `Actualizacion 2026-10-22 (cierre del roadmap ...)`; la entrada registra la migracion, declara `docs/Tesis/v9 (IA)/` congelada, indica que `docs/Tesis/v10 (IA)/` es la version de trabajo vigente y que c-121 es el proximo change de contenido (con c-122 como su prerequisito); verificar con `grep -n "Actualizacion 2026-10-22 (migracion de la tesis a v10)" CHANGES.md` y `grep -c "docs/Tesis/v10 (IA)" CHANGES.md` >= 1
- [x] 3.2 Verificar la preservacion historica (regla D3 de `design.md`): las 4 ocurrencias previas de `docs/Tesis/v9 (IA)` en `CHANGES.md` siguen presentes sin reescritura; verificar `grep -c "docs/Tesis/v9 (IA)" CHANGES.md` es 4 y que ninguna entrada fechada previa (`Actualizacion 2026-10-19`, `2026-10-20`, `2026-10-22 (cierre del roadmap)`) fue editada para designar v10

## 4. Coordinar el change dependiente c-121 (D4)

- [x] 4.1 (PRE-SATISFECHO al definir c-121) En `openspec/changes/c-121-observaciones-dictamen-v1-0-1/{proposal,design,tasks}.md`, repuntar las rutas activas `docs/Tesis/v9 (IA)` a `docs/Tesis/v10 (IA)` (v10 es copia byte a byte de v9, por lo que las lineas verificadas de c-121 siguen validas); verificar `grep -rc "docs/Tesis/v9 (IA)" openspec/changes/c-121-observaciones-dictamen-v1-0-1/` es 0 y `grep -rc "docs/Tesis/v10 (IA)" openspec/changes/c-121-observaciones-dictamen-v1-0-1/` >= 6

## 5. Verificacion global y no-regresion

- [x] 5.1 Confirmar que el planning valida: `openspec validate c-122-migrar-tesis-a-v10 --strict` pasa sin errores
- [x] 5.2 Confirmar los no-goals: `git status --short` no reporta cambios en `docs/Tesis/v9 (IA)/`, `auditorias/`, `docs/Tesis/Correcciones/`, `openspec/changes/archive/`, `App/`, `n8n/`, `data/` ni `evaluation/`; y `git tag -l` sigue mostrando solo `v1.0.0` y `v1.0.1` (ningun tag nuevo ni movido)
- [x] 5.3 Confirmar que no se edito contenido de la tesis: `diff -rq "docs/Tesis/v9 (IA)" "docs/Tesis/v10 (IA)"` no reporta diferencias (v10 identico a v9) y ningun `.tex` de v10 fue modificado tras la copia
