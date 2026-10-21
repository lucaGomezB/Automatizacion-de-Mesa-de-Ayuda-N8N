## Context

Ver `proposal.md` — Why. Estado verificado por lectura directa de la fuente en
`docs/Tesis/v9 (IA)/` durante esta sesión (2026-10-21):

- `Bibliography_base.bib`: **48 entradas**, 0 fabricadas, 0 sin resolver (según la
  re-verificación registrada por c-78 el 2026-10-19).
- `Touvron2023_llama2` (línea 204) es `@article` con `journal = {arXiv preprint}`,
  `note = {arXiv:2307.09288}` y `doi = {10.48550/arXiv.2307.09288}`. El dictamen §9
  señala que se renderiza "arXiv preprint" como si fuera una revista.
- `Jurafsky2023_speech_language` (línea 93) es `@book` con
  `publisher = {Stanford University}` y `note = {Borrador de la 3ra edicion...}`.
  c-78 corrigió el `publisher` (era Pearson) pero no el TIPO de entrada.
- Preamble: `biblatex` con `style=apa, backend=biber` (línea 96); el APA de
  biblatex distingue `@article` (revista) de `@misc`/`@online`/`@unpublished`
  (preprint/borrador). El render "arXiv preprint" proviene del `journal`, no del
  título.
- B1/B2/B3 están aplicadas: `Revina2020_it_tickets` (sin BERT), las 12 claves
  2023-2026 (`ahuja2023mega` … `colavito2025benchmarking`), `Landis1977_kappa`,
  `Stallings2017_computer_security` con Lawrie Brown y `OGC2011_itil` sin
  `edition = {2011}`. El pendiente real es el **item 14**: el tipado.
- Sitios de cita: `Touvron2023_llama2` se cita en `10-recomendaciones.tex:10,32`;
  `Jurafsky2023_speech_language` en `02-marco-teorico.tex:32`. Ninguno requiere
  cambio de prosa por el retipado.

## Goals / Non-Goals

**Goals:**

- Retipar `Touvron2023_llama2` y `Jurafsky2023_speech_language` para que el render
  APA corresponda a la naturaleza real de la fuente (item 14 del dictamen).
- Re-verificar B1-B3 por comando y registrar la evidencia (sin regresión).
- Dejar la tesis compilando con 0 referencias indefinidas y el conteo de páginas
  registrado.

**Non-Goals:**

- No duplicar la modernización bibliográfica de B2 (ya hecha por c-78).
- No reintroducir ni reformular los ítems de otras ramas (números canónicos,
  tildes, remisiones, figuras).
- No editar prosa científica salvo que la verificación B1-B3 detecte una regresión.
- No cambiar autoría, año, título ni DOI de ninguna entrada.

## Decisions

### D1. Retipado de las dos entradas (item 14)

- `Touvron2023_llama2` → `@misc` con `howpublished = {arXiv preprint}`,
  `eprint = {2307.09288}`, `archivePrefix = {arXiv}`, `primaryClass = {cs.CL}` y el
  `doi` existente. Alternativa descartada: `@online`, válido pero redundante (el
  `doi` de arXiv ya resuelve); `@misc` es el tipo canónico de preprint en biblatex
  APA y evita el campo `journal`.
- `Jurafsky2023_speech_language` → `@unpublished` con `note` del borrador y
  `publisher`/institución Stanford University. Alternativa descartada: `@misc`
  (válido, pero `@unpublished` expresa mejor "borrador no publicado").
- Solo cambia el `@type` y los campos de tipo; los metadatos de contenido
  (`author`, `title`, `year`, `doi`) permanecen.

### D2. Verificación B1-B3, no re-ejecución

Como B1-B3 ya están en la spec principal y aplicadas, c-104 NO las re-escribe:
corre los comandos de verificación (`grep`/script de citas) y registra el
resultado en `tasks.md`. Si algún comando revela una regresión, el fix es una
edición de `.tex`/`.bib` que MUST serializarse con las demás ramas (ver D3).

### D3. Secuencia y dependencias con las ramas hermanas

Todos los changes de contenido de la tesis comparten los archivos `.tex` (en
especial `08-discusion.tex` y `09-conclusiones.tex`), por lo que **MUST aplicarse
en secuencia, no en paralelo**. Orden serial adoptado para la ola de correcciones:

`c-102` (Gate 0, congelar números) → `c-103` (Gate 0, portada y remisiones) →
**`c-104` (bibliografía y atribución)** → `c-105` (reubicación del capítulo 11) →
`c-106` (tildes) → `c-107` (propagación de números canónicos) → `c-108`/`c-109`/
`c-110` (resto de la ola, en el orden que fije el roadmap).

- c-104 es **`.bib`-only** si la verificación no halla regresión: no edita `.tex`,
  por lo que no colisiona con las ramas de texto. Aun así se declara dentro de la
  secuencia porque el `.bib` es insumo común y porque un hallazgo de regresión
  obliga a tocar `02`/`03`/`04`/`08`.
- **c-105** debe aplicarse DESPUÉS de c-104 (mueve el capítulo 11 y renumeraría
  remisiones; c-104 solo debe dejar consistente el tipado).
- **c-106** (tildes) toca `02`/`03`/`04`/`08`; si corre antes que c-104 y la
  verificación B1-B3 falla, el fix debe hacerse sobre el texto ya normalizado.
- **c-107** reescribe `04`/`07`/`08`/`09`; no toca sitios de cita, pero comparte
  `08-discusion.tex` (Revina y Touvron), por lo que no debe ejecutarse a la vez.
- **c-108/c-109/c-110**: sin definición formal aún; c-104 MUST declararse
  serializado respecto de cualquiera que edite `Bibliography_base.bib` o los
  sitios de cita.

### D4. Governance MEDIO/ALTO

- **ALTO** para la verificación de atribución (B1/B3): afecta la integridad
  académica y la trazabilidad de fuentes; requiere revisión humana del resultado
  antes de cerrar.
- **MEDIO** para el retipado (item 14): es mecánico y reversible; no altera el
  contenido citado.

### D5. Verificación de compilación con Docker `texlive-thesis`

La compilación se verifica con la imagen ya construida (no se instala TeX en el
host):

```bash
docker run --rm -v "/home/skywalker/Desktop/notas/Tesis/Automatizacion-de-Mesa-de-Ayuda-N8N/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex
```

Criterio de aceptación: `main.pdf` compila sin errores fatales, el log no contiene
"undefined reference" ni "multiply defined label", y el conteo de páginas se
registra (base: 103 páginas). El retipado puede alterar levemente la extensión del
bloque de referencias; el conteo se registra, no se fija a 103 como requisito duro.

## Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| `@unpublished`/`@misc` cambian el render APA de forma inesperada | Media | Compilar con Docker y revisar la entrada en el bloque de referencias; si el render empeora, ajustar campos (`howpublished`, `note`) |
| La verificación B1-B3 halla una regresión introducida por otra rama | Baja | Registrar el hallazgo; el fix es una edición `.tex` serializada (D3) |
| Solapamiento con c-105/c-106/c-107 al editar `.tex` | Baja (c-104 es `.bib`-only) | Aplicar en la secuencia declarada en D3 |

## Rollback

`git revert` del commit único del change restaura el `@type` de las dos entradas y
cualquier `.tex` tocado por la verificación. Sin migraciones de datos ni estado
externo; el `.bib` es texto versionado.
