## ADDED Requirements

### Requirement: OOS-025 — Preservación y alcanzabilidad del commit de la corrida fuera de muestra

El commit que la primera corrida fuera de muestra registra en `cache_meta` de
`predicciones_independiente.json` (`561b3c480da718b5d681a126b7597170aa7986c0`) SHALL preservarse
mediante un tag anotado de archivo, `archivo/corrida-fuera-de-muestra-561b3c4`, publicado en
`origin`, de modo que el objeto viaje con `clone` y `fetch`. Si el tag no puede publicarse, la
documentación SHALL declarar la salvedad de forma explícita, con la causa y el commit que versionó
el archivo. El tag SHALL apuntar al commit completo y MUST NOT usarse para reescribir la historia:
la preservación por ref no convierte al commit en ancestro de `main` ni lo hace alcanzable desde
`main`. La verificación SHALL comprobar que `git rev-parse <tag>^{commit}` devuelve el SHA de la
corrida, que `git ls-remote --tags origin` devuelve el tag y su línea `^{}`, y que un clon nuevo
contiene el tag y permite inspeccionar su árbol con `git ls-tree`. La documentación SHALL declarar
que el tag preserva el árbol de fuentes de la corrida y que `predicciones_independiente.json` y
`reporte_independiente.md` están versionados desde
`1b17e55a3cd64b19f7677d49d96f6f369c44f7a4` con sus SHA-256.

#### Scenario: Tag publicado y árbol inspeccionable

- **WHEN** se consulta el tag de archivo en el remoto y en un clon nuevo
- **THEN** `git rev-parse archivo/corrida-fuera-de-muestra-561b3c4^{commit}` devuelve `561b3c480da718b5d681a126b7597170aa7986c0`
- **AND** `git ls-remote --tags origin` devuelve el tag y su línea `^{}` con ese commit
- **AND** un clon nuevo contiene el tag y `git ls-tree` inspecciona el árbol de fuentes de la corrida

#### Scenario: El tag preserva el árbol de fuentes y no los artefactos de salida

- **WHEN** se inspecciona el árbol del tag
- **THEN** figuran el clasificador, el prompt, `settings.py`, `constants.py` y los datos de la campaña
- **AND** la documentación declara que `predicciones_independiente.json` y `reporte_independiente.md` se versionaron después, en `1b17e55`, con sus SHA-256
- **AND** no se afirma que el tag contenga esos artefactos

#### Scenario: La preservación no reescribe la historia

- **WHEN** se ejecuta `git merge-base --is-ancestor 561b3c4 origin/main`
- **THEN** devuelve `1` y se registra como topología esperada
- **AND** la documentación y el change no lo presentan como falla ni como incumplimiento

#### Scenario: Salvedad explícita si el tag no se publica

- **WHEN** el tag de archivo no se publica
- **THEN** el README de la campaña declara la salvedad de forma explícita, con su causa y el commit `1b17e55` que versionó el archivo
- **AND** la salvedad no se presenta como equivalente a la preservación por tag
