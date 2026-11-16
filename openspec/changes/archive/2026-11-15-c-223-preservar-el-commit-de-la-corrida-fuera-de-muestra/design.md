## Context

Ver `proposal.md` — Why. Estado actual que condiciona el diseño:

- `evaluation/data/campana/predicciones_independiente.json` registra en `cache_meta` el commit
  `561b3c480da718b5d681a126b7597170aa7986c0` (HEAD al generar el cache, 2026-11-12 17:53 -03:00).
- `git merge-base --is-ancestor 561b3c4 origin/main` devuelve `1`; ninguna rama ni tag lo contiene;
  `git cat-file -t 561b3c4` devuelve `commit` (objeto colgante local).
- El archivo lo versionó `1b17e55a3cd64b19f7677d49d96f6f369c44f7a4` (2026-11-12 21:21 -03:00), que
  sí es ancestro de `origin/main` (`git merge-base --is-ancestor 1b17e55 origin/main` → `0`).
- **Hallazgo de diseño:** el árbol de `561b3c4` **no contiene** `predicciones_independiente.json`
  (`git cat-file -e 561b3c4:evaluation/data/campana/predicciones_independiente.json` → `128`). Sí
  contiene el clasificador, el prompt, `settings.py`, `constants.py` y los datos de la campaña. Los
  artefactos de la corrida se agregaron después, en `1b17e55`. El tag preserva el **árbol de
  fuentes de la corrida**, no los archivos de salida.
- SHA-256 vigentes: `predicciones_independiente.json`
  `d5ee19f7b0bf2b56a00026a1bd33a2e11ffeb9b224b6a8efa553460895a915a4`; `reporte_independiente.md`
  `304dffcf4afdf1655c4ff7d9a6906d2ba8e134b6926281d65ca0465c629fbf92`.
- El memo canónico termina en la sección `3.33` (c-222). La sección nueva toma el primer número
  libre al aplicar.
- El PDF vigente (`v1.4.1`) tiene 155 páginas (`\@abspage@last{155}`). CI se dispara solo con push
  a `main`, no con tags (`.github/workflows/ci.yml:12-14`).

## Goals / Non-Goals

**Goals:**

- Anclar el commit `561b3c4` con un ref publicado que viaje con `fetch`/`clone`, sin reescribir la
  historia ni alterar la línea de releases.
- Que README y tesis digan con precisión qué preserva el tag y qué versiona `1b17e55`, con los
  SHA-256 verificables.
- Dejar una verificación reproducible de la preservación y una salvedad explícita si el push no
  fuera posible.

**Non-Goals:**

- Hacer que `561b3c4` sea ancestro de `main` o alcanzable desde `main`.
- Reconstruir la corrida, reejecutarla o reescribir el `cache_meta`.
- Reescribir el README de c-221 (solo extender la nota de vigencia).
- Cambiar el conteo de páginas, la release vigente o los tags `v*`.

## Decisions

### D1 — Tag anotado de archivo, no reescritura de historia

**Elegido.** Crear un tag **anotado** `archivo/corrida-fuera-de-muestra-561b3c4` sobre
`561b3c480da718b5d681a126b7597170aa7986c0` y publicarlo como
`refs/tags/archivo/corrida-fuera-de-muestra-561b3c4`.

**Por qué.** Un tag es un ref inmutable que ancla un objeto y viaja en `clone`/`fetch`; el objeto
deja de ser colgante sin tocar la topología de `main`. Un tag anotado agrega un objeto `tag` con
mensaje, autor y fecha, que documenta el propósito y sobrevive a la inspección.

**Alternativas descartadas.**

- *Reescribir `main` para incluir `561b3c4`*: reescribe historia publicada, altera hashes de
  releases y no aporta nada que el tag no aporte.
- *Crear una rama*: una rama implica trabajo en curso y puede borrarse; no es un mecanismo de
  archivo.
- *Dejar solo la nota del README (c-221)*: no hace viajar el objeto; el clon limpio sigue sin el
  commit.

**Consecuencia explícita.** `git merge-base --is-ancestor 561b3c4 origin/main` **seguirá
devolviendo `1`**. Eso es correcto: la preservación es por ref publicado, no por ancestría. La
documentación y el spec MUST NOT presentar ese `1` como falla ni usar esa comprobación como
criterio de éxito.

### D2 — Nombre, mensaje y alcance del tag

- **Nombre:** `archivo/corrida-fuera-de-muestra-561b3c4`. El prefijo `archivo/` lo separa del
  espacio de releases `v*` y hace evidente que no es una versión entregable.
- **Mensaje anotado (contenido mínimo):** propósito (preservar el commit de la primera corrida
  fuera de muestra), SHA completo, asunto y fecha del commit, SHA-256 de las predicciones y del
  reporte, y la frase «no es una release de la tesis; no reescribe la historia».
- **Alcance:** el tag apunta al commit completo, de modo que `git ls-tree -r <tag>` expone el
  clasificador, el prompt y la configuración con los que se generó la corrida. No se etiqueta
  `1b17e55` ni se pretende que el tag contenga los artefactos de salida.

### D3 — Frontera de preservación: árbol de fuentes sí, artefactos versionados aparte

El README y la tesis SHALL distinguir dos cosas:

1. El tag preserva el **árbol de fuentes** de la corrida (`561b3c4`): clasificador, prompt,
   `settings.py`, `constants.py` y datos de campaña.
2. Los **artefactos de salida** (`predicciones_independiente.json` y `reporte_independiente.md`)
   están versionados desde `1b17e55` y se verifican por SHA-256, no por `git show <tag>:<archivo>`.

Esto evita una afirmación falsa: `git show archivo/…:evaluation/data/campana/predicciones_independiente.json`
falla porque el archivo no existía en `561b3c4`. La verificación del árbol se hace con
`git ls-tree -r <tag> -- App/Backend/app/classifiers docs/prompt_gemini.txt App/Backend/app/config/settings.py`.

### D4 — Protocolo de verificación

Antes del push:

1. `git cat-file -t archivo/corrida-fuera-de-muestra-561b3c4` → `tag` (anotado).
2. `git rev-parse archivo/corrida-fuera-de-muestra-561b3c4^{commit}` →
   `561b3c480da718b5d681a126b7597170aa7986c0`.
3. `git show --stat archivo/corrida-fuera-de-muestra-561b3c4` y `git ls-tree -r <tag> -- <rutas>`
   → el árbol de fuentes esperado.
4. `git for-each-ref refs/tags/v1.4.1` sin cambios (la release no se mueve).
5. `git merge-base --is-ancestor 561b3c4 origin/main` → `1`, registrado como topología esperada,
   no como falla.

Después del push:

6. `git ls-remote --tags origin` devuelve `refs/tags/archivo/corrida-fuera-de-muestra-561b3c4` y su
   línea `^{}` con el commit.
7. En un clon nuevo (`git clone` desde `origin`), el tag existe y `git ls-tree` inspecciona el árbol.
8. En un clon existente, `git fetch origin 'refs/tags/archivo/*:refs/tags/archivo/*'` trae el tag.
9. `git tag --list 'v*'` y `git rev-parse v1.4.1^{commit}` sin cambios.

El push es solo del ref del tag; no se pushea `main` ni ninguna rama en este change.

### D5 — Salvedad explícita si el tag no puede publicarse

Si los autores no autorizan el push o el remoto lo rechaza, la rama de respaldo es la del spec:
README y tesis declaran de forma explícita que el commit de la corrida no está preservado en el
remoto, nombran el commit que versionó el archivo (`1b17e55`) y los SHA-256, y MUST NOT afirmar que
el commit no existe. La salvedad no se presenta como equivalente al tag publicado; se registra como
limitación con su causa. La preferencia es el tag.

### D6 — Ubicación y neutralidad de páginas de la declaración

- **Primaria:** `04-marco-metodologico.tex:100`, párrafo «Diseño de la validación fuera de muestra».
  Se agrega una o dos oraciones al final del párrafo: el commit de la corrida se preserva por el tag
  `archivo/corrida-fuera-de-muestra-561b3c4` y los artefactos versionados se identifican por sus
  SHA-256.
- **Secundaria condicional:** `07-resultados.tex`, en `subsec:validacion-fuera-muestra`, solo si
  cabe una remisión de una línea sin agregar páginas. Si no, se omite.
- **Limitaciones:** no se agrega una limitación nueva si el tag se publicó; la falta de
  preservación deja de ser una limitación. Si se aplica la salvedad de D5, se declara en
  `08-discusion.tex` junto a la séptima/octava limitación, con remisión.
- **Neutralidad:** verificar `\@abspage@last` = 155; si la declaración empuja una página, se
  compensa dentro del mismo párrafo (sin retirar contenido científico).
- **Memo:** sección aditiva nueva con el tag, el SHA completo y los dos SHA-256; el número se lee al
  aplicar. `dictamen-correcciones.md` recibe la entrada que cierra la observación de
  reproducibilidad.

### D7 — Diseño de las especificaciones

- **`evaluation-out-of-sample-validation` — OOS-025 (ADDED).** Separa la preservación del commit de
  OOS-008, que gobierna los SHA-256 de los artefactos. OOS-025 exige tag publicado **o** salvedad
  explícita, y fija los escenarios de verificación por clon limpio y de no reescritura de historia.
- **`tesis-document` — «Reproducibilidad declarada» (MODIFIED).** Es el requisito que ya exige
  declarar que el commit no es alcanzable desde `main` y cuál lo versionó; se extiende para exigir
  el tag y los SHA-256, en lugar de crear un requisito paralelo que duplique la regla.
- **`evaluation-framework` no cambia.** La obligación es propia del corpus fuera de muestra y de su
  commit; duplicarla fragmentaría la fuente de verdad.

### D8 — Gobernanza y checkpoints

| Bloque | Nivel | Control |
|---|---|---|
| B. README y specs | LOW | Aplicación directa; verificación de hashes |
| C. Tesis, memo y registro | MEDIUM | Confirmación de los autores sobre la redacción y la ubicación antes de editar; verificación de páginas |
| A. Creación y push del tag | HIGH | **Confirmación expresa**; `git push --dry-run` antes del push real; solo el ref del tag |

Sin cambios en `App/`, `n8n/`, el clasificador ni `docker-compose.yml`. Cero llamadas pagas.

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| El remoto rechaza el push del tag | `git push --dry-run` previo; si falla, rama de salvedad D5 y registro de la causa |
| Se confunde el tag de archivo con una release | Prefijo `archivo/`, mensaje anotado explícito y verificación de que `v1.4.1` no se mueve |
| El tag no viaja en un clon o fetch selectivo | Verificación en clon nuevo y refspec documentado en README |
| Se afirma que el tag contiene las predicciones | D3 fija la frontera: el tag preserva el árbol de fuentes; los artefactos se versionan en `1b17e55` |
| La declaración agrega una página | D6 exige `abspage@last` = 155 y compensación dentro del párrafo |
| Se presenta `merge-base --is-ancestor` = 1 como falla | D1 y D4 lo registran como topología esperada |

## Migration Plan

1. Leer el estado y confirmar que `561b3c4` sigue siendo un commit colgante y que `1b17e55` versionó
   el archivo.
2. Confirmación expresa de los autores para crear y publicar el tag (D8).
3. Crear el tag anotado y verificar D4 (1-5).
4. Actualizar el README (bloque B) y las specs.
5. Actualizar memo, tesis y registro (bloque C), con confirmación de contenido.
6. `git push origin refs/tags/archivo/corrida-fuera-de-muestra-561b3c4` y verificar D4 (6-9).
7. Compilar y verificar 155 páginas, 0 referencias indefinidas; `openspec validate --strict`.

**Rollback:** si el tag no se publicó, `git tag -d` y `git revert` de la documentación. Si ya se
publicó, no se borra ni se mueve: se documenta la corrección y, si hiciera falta, se crea un tag
sucesor que lo supere.

## Open Questions

- **Autorización del push del tag.** Es una acción hacia afuera y HIGH; la respuesta de los autores
  decide entre la rama del tag publicado (preferida) y la salvedad explícita de D5.
- **Alcance de `08-discusion.tex`.** Si el tag se publica, no se agrega limitación; si se aplica D5,
  se confirma con los autores el párrafo exacto de limitaciones donde declararla.
