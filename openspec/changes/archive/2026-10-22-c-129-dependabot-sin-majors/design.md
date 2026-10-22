## Context

Ver `proposal.md` (Why) para la motivacion. Estado y restricciones que condicionan el diseno:

- `.github/dependabot.yml` YA existe en el arbol (creado por c-64, D9): `version: 2`, tres entradas (`pip` en `/App/Backend`, `npm` en `/App/Frontend`, `github-actions` en `/`), `schedule.interval: weekly` y un `groups` por ecosistema con `patterns: ["*"]`. No hay reglas `ignore`. No se configura por la UI de GitHub.
- El proyecto fija versiones exactas o cotas de mayor: `App/Backend/requirements.txt` y `App/Frontend/package.json` (ver `AGENTS.md`). Un salto de mayor es una frontera de compatibilidad, no una actualizacion rutinaria.
- c-127 (`migracion-dependencias-backend`) y c-128 (`migracion-react-19-frontend`) ya existen como los vehivulos para las migraciones de mayor. Este change NO las ejecuta; solo evita que Dependabot las proponga automaticamente.
- Referencia oficial de esquema: Dependabot options reference (docs.github.com) — `ignore` acepta `dependency-name` (comodin `*`), `versions` y `update-types` (`version-update:semver-major|minor|patch`). No se inventan claves.

## Goals / Non-Goals

**Goals:**

- Que Dependabot deje de abrir pull requests de version por saltos de version MAYOR en los tres ecosistemas.
- Preservar el comportamiento actual en todo lo demas (tres ecosistemas, cadencia semanal, agrupacion, sin auto-merge).
- Mantener la propuesta automatica de actualizaciones menores y de parche.

**Non-Goals:**

- No ejecutar las migraciones de mayor (eso es c-127 y c-128).
- No cambiar el workflow de CI, ni el job `security-scan`, ni el codigo de aplicacion.
- No introducir auto-merge ni auto-aprobacion.
- No bloquear parches de seguridad menores/parche.

## Decisions

### D1 — Excluir mayores con `ignore` por ecosistema, no con `groups` ni `allow`

Cada entrada de `updates` recibe:

```yaml
ignore:
  - dependency-name: "*"
    update-types:
      - version-update:semver-major
```

- Razon: `ignore` es el mecanismo oficial que filtra versiones/actualizaciones por nivel SemVer y es el que garantiza que un salto de mayor no abra PR. `dependency-name: "*"` aplica la exclusion a todas las dependencias del ecosistema.
- Alternativa descartada — `groups` que "excluya" mayores: los `groups` solo determinan como se agrupan las PRs; una dependencia no cubierta por ningun grupo abre su propia PR. No previene los saltos de mayor.
- Alternativa descartada — `allow` con solo `semver-minor`/`semver-patch`: expresa lo mismo desde el lado positivo, pero es mas fragil ante nuevas dependencias y no es la forma idiomatica de "ignorar mayores".

### D2 — Preservar `weekly` y `groups` existentes

No se toca `schedule.interval` ni los `groups`. Solo se agrega el bloque `ignore`.

- Razon: minimizar el diff y el riesgo; el change es aditivo y su unico efecto observable es no proponer mayores.

### D3 — Aplicar la exclusion a los tres ecosistemas, incluido `github-actions`

- Razon: uniformidad y coherencia con "los saltos de mayor se adoptan de forma deliberada". Los saltos de mayor de actions (p.ej. cambios de runtime Node) tambien son potencialmente rompientes. Si en el futuro se decide dejar que actions suba de mayor automaticamente, se revisa en otro change.
- Alternativa descartada: excluir mayores solo en `pip` y `npm` (deja a `github-actions` abierto a saltos de mayor rompientes).

## Risks / Trade-offs

- [Una actualizacion de SEGURIDAD que solo se resuelva con un salto de mayor tampoco se propondria] -> Segun la referencia oficial, `ignore` tambien afecta a las actualizaciones de seguridad. La red de seguridad es el job `security-scan` de la CI (`pip-audit` sobre `requirements.txt` y `npm audit` sobre el frontend), que sigue detectando esas advisories; una advisory corregible solo por mayor se resuelve con un change explicito (patron ya usado en c-97), no con un PR automatico.
- [Se pierde la visibilidad de que existe un mayor pendiente] -> Los PRs #33/#34 ya evidencian los mayores pendientes y c-127/c-128 los rastrean; la migracion queda trazada en OpenSpec.
- [YAML mal formado desactiva Dependabot silenciosamente] -> Tarea explicita de validacion de sintaxis YAML y de esquema contra la referencia oficial (SchemaStore `dependabot-2.0.json`), mas inspeccion de que la config previa se preserva.
- [El comodin `dependency-name: "*"` no matchea alguna dependencia] -> Es el patron documentado para "todas las dependencias"; se verifica en la tarea de validacion que los tres bloques `ignore` existan.

## Migration Plan

1. Editar `.github/dependabot.yml`: agregar el bloque `ignore` a cada una de las tres entradas, sin alterar `schedule` ni `groups`.
2. Validar sintaxis YAML y esquema de Dependabot.
3. Verificar que la configuracion previa (tres ecosistemas, weekly, grupos) se preserva.
4. Cerrar/dejar nota en los PRs abiertos #33 y #34, referenciando c-127 (backend) y c-128 (frontend) como los vehivulos de migracion de mayor.
5. Rollback: revertir `.github/dependabot.yml` al contenido previo (quitar los tres bloques `ignore`); el cambio es puramente aditivo y no requiere migracion de datos.
