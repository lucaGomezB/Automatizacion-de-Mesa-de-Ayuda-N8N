## 1. Configuracion de Dependabot

- [ ] 1.1 Editar `.github/dependabot.yml` agregando a cada una de las tres entradas (`pip` en `/App/Backend`, `npm` en `/App/Frontend`, `github-actions` en `/`) un bloque `ignore` con `dependency-name: "*"` y `update-types: [version-update:semver-major]`, sin alterar `schedule.interval: weekly` ni los `groups`. Verificacion: el archivo contiene tres bloques `ignore` con `version-update:semver-major`.
- [ ] 1.2 Validar la sintaxis y el esquema del YAML. Verificacion: el archivo parsea sin error (`python -c "import yaml; yaml.safe_load(open('.github/dependabot.yml'))"`) y, si hay red, valida contra el esquema oficial de Dependabot (SchemaStore `dependabot-2.0.json` con `check-jsonschema`); sin red, revision manual contra la referencia de opciones de Dependabot.

## 2. Preservacion y trazabilidad

- [ ] 2.1 Confirmar que la configuracion previa se preserva: `version: 2`, las tres entradas de ecosistema, `schedule.interval: weekly` y los `groups` por ecosistema. Verificacion: inspeccion del archivo contra el contenido previo del change (c-64, D9).
- [ ] 2.2 Confirmar que los PRs abiertos #33 (backend-python) y #34 (frontend-npm) son saltos de version mayor y quedan superseded por c-127 (backend) y c-128 (frontend); cerrarlos o dejar nota referenciando esos changes. Verificacion: nota/comentario en los PRs o en c-129 que referencia c-127 y c-128, y que no se adopta el salto de mayor por esa via.

## 3. Verificacion final

- [ ] 3.1 Correr `openspec validate c-129-dependabot-sin-majors --strict` hasta obtener PASS. Verificacion: la salida reporta el change como valido.
