## Why

El dictamen CONEAU del 22-10-2026 sobre la version de trabajo v10 (release `v1.1.0`, aplicable tambien a `v1.1.1`; `auditorias/Dictamen_Tesis_v10_v1.1.0_CONEAU_2026-10-22.md`) observa en la seccion 1 un "patron sistematico de tildes faltantes o incorrectas que trasciende la errata aislada", con casos que cambian el significado ("hacía" por la preposicion "hacia", "fórmula" por el verbo "formula"), y lo convierte en la recomendacion **B14**: revision ortotipografica completa de las fuentes LaTeX. Es ademas uno de los descuentos del criterio 8 de la rubrica (Redaccion academica, 7/10), que el propio dictamen proyecta a 8 tras esta revision. La verificacion hecha para esta propuesta sobre el arbol de trabajo (secciones identicas a `v1.1.1` salvo el hash del Anexo B) confirma el patron, encuentra erratas fuera de la muestra del dictamen y muestra que la muestra no sirve como criterio de aceptacion por conteo bruto: de los 4 "fórmula" solo 1 es verbal (los otros 3 son el sustantivo, correcto) y de los 16 "continua" solo 4 son verbales (12 son adjetivos correctos, no 11 verbos). Ademas, tres familias de erratas que cambian el significado coinciden con entradas incondicionales del diccionario de las utilidades de acentuacion del repositorio (`acentuar_tesis.py`: `hacia`->`hacía`, `aquellas`->`aquéllas`; ambas utilidades: `formula`->`fórmula`; "se fórmula" entra con el commit `f0546ec` de c-106). Por eso la recomendacion del dictamen de "aplicar las utilidades existentes" no se sigue literalmente: hace falta un inventario que separe lo inequivoco de los homografos que exigen juicio humano, y una pasada repetible para que c-141 detecte erratas reintroducidas por cambios tardios.

## What Changes

- **Inventario reproducible (script nuevo):** `docs/Tesis/v10 (IA)/revision_tildes.py`, solo biblioteca estandar y con pruebas en `docs/Tesis/v10 (IA)/test_revision_tildes.py` (TDD estricto en apply). Sin opciones no escribe nada y lista por archivo, linea y columna cada candidato de tilde faltante o improcedente en `paper/sections/*.tex`, con forma sugerida, clase (`INEQUIVOCO` | `AMBIGUO`) y zona (`prosa` | `tabla` | `cita`), excluyendo las zonas protegidas (cinco cadenas canonicas, `\texttt`, `\url`, `\href`, claves de `\label`/`\ref`/citas, rutas, `lstlisting`/`verbatim`, matematica, comentarios y el Abstract en ingles).
- **Aplicacion en dos pasos:** (1) correcciones `INEQUIVOCO` en prosa por script, con `--diff` revisable antes de `--apply`; (2) casos `AMBIGUO` y candidatos en tablas o citas, uno por uno, con decision y justificacion registradas en `docs/Tesis/Correcciones/revision-tildes-decisiones.tsv`.
- **Correcciones esperadas en `sections/` (linea base v1.1.1, a re-medir al aplicar):** 40 en total. Muestra del dictamen: 4 "hacía" preposicionales, 1 "fórmula" verbal, 4 "continua" verbales, 4 "esta"/"este" verbales, "heterogeneas" (2), "erronea"/"erroneas" (3), "antiguedad" (2), "perimetro" (2), "inequivocos" (2), "enganosa", "simultanea", "aquéllas", "asigno" y "gestiono". Fuera de la muestra: "multiples" (6), "alla" (3, "mas allá"), "escaner" y "por si mismo".
- **Cadenas visibles fuera de `sections/` y bibliografia impresa:** `paper/main.tex` ("Indice general", "Indice de tablas", "Indice de figuras", titulo "Referencias bibliograficas"), `paper/preambles/preamble.tex` (encabezado de pagina "AUTOMATIZACION DE MESA DE AYUDA", cadena `bibliography`, `pdftitle`, `pdfkeywords`) y el texto impreso de los campos `note` de `Bibliography_base.bib` ("Documentacion tecnica [oficial]", "Documentacion de la plataforma", "edicion"). Solo tildes; claves y metadatos bibliograficos intactos.
- **Coherencia de nombres de sector (pregunta abierta OQ1):** 15 menciones con tilde de los sectores en 5 pasajes que los presentan como "sectores canonicos" (`01-introduccion.tex:48,72`, `04-marco-metodologico.tex:36,45`, `05-arquitectura.tex:100`) contradicen la definicion de la propia tesis (strings exactos "sin tildes", `05-arquitectura.tex:84`, `12-anexos.tex:79`). Se recomienda unificarlas a la cadena canonica, sujeto a confirmacion del usuario.
- **Pasada corta repetible:** `revision_tildes.py --check` (codigo 0/1) para que c-141 la ejecute tras cualquier edicion tardia; `--base <dir>` verifica que el diff sea puramente diacritico.
- **Verificacion:** diff puramente diacritico (sin cambios de cifras, claves ni rutas), cadenas canonicas sin alteraciones, mismo numero de paginas que antes de la pasada, compilacion sin errores, `verify_citations.py` PASS y `tesis_para_agente.md` regenerado.
- **Causa raiz y registro:** `docs/Tesis/acentuar_tesis.py` y `docs/Tesis/acentuar_tesis_v9.py` quedan marcados DEPRECADO en su cabecera (sin cambios de logica) y `docs/Tesis/Correcciones/dictamen-correcciones.md` registra la pasada (conteos, clases, decisiones, discrepancias con el dictamen, causa raiz y procedimiento de la pasada corta).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tesis-document`: se agregan requisitos de inventario reproducible de tildes, aplicacion en dos pasos con registro de decisiones, ausencia de las erratas del dictamen v1.1.0, cadenas visibles y bibliografia impresa acentuadas, coherencia de los nombres de sector, neutralidad (diff diacritico, paginas, cadenas canonicas), pasada corta repetible y registro con neutralizacion de la causa raiz. Se modifica "Acentuación normalizada del manuscrito" para admitir el retiro justificado de tildes improcedentes, proteger el Abstract en ingles y permitir los archivos que esta revision toca fuera de `sections/`.

## Impact

- Crea: `docs/Tesis/v10 (IA)/revision_tildes.py`, `docs/Tesis/v10 (IA)/test_revision_tildes.py`, `docs/Tesis/Correcciones/revision-tildes-decisiones.tsv`.
- Edita (solo tildes, dieresis y eñe): `docs/Tesis/v10 (IA)/paper/sections/*.tex`, `paper/main.tex`, `paper/preambles/preamble.tex` y los campos `note` (y, por decision registrada, la etiqueta de version del titulo de `Gomez2026_repositorio`) de `docs/Tesis/v10 (IA)/Bibliography_base.bib`. Regenera `docs/Tesis/v10 (IA)/tesis_para_agente.md` y los artefactos de compilacion (`paper/main.pdf` y auxiliares versionados).
- Edita (sin efecto en la tesis): cabecera de `docs/Tesis/acentuar_tesis.py` y `docs/Tesis/acentuar_tesis_v9.py`; seccion nueva en `docs/Tesis/Correcciones/dictamen-correcciones.md`.
- No toca: codigo de aplicacion (`App/`, `n8n/`), numeros canonicos, cifras, las ocurrencias existentes de las cinco cadenas canonicas, claves de `\label`/`\ref`/citas, claves y metadatos de la bibliografia, figuras, `evaluation/`, `CHANGES.md`, el dictamen auditado.
- Paginas: neutral por construccion (cambios diacriticos); se verifica que el conteo posterior sea igual al previo a la pasada y <= 101.
- Orden: se aplica DESPUES de c-130, c-131, c-132, c-133, c-134, c-135, c-136, c-138 y c-139 (y de c-140 si llegara a editar prosa) y ANTES de c-141. El bloque de la herramienta (TDD) no toca la tesis y puede implementarse en paralelo con esos changes.
- Gobernanza: LOW (cambios diacriticos verificados por invariante). La unificacion de los nombres de sector (OQ1) requiere confirmacion del usuario por tocar el dominio de las cadenas canonicas.

## Rollback

Restaurar los archivos de la tesis desde el commit base registrado al iniciar la pasada: `git checkout <base> -- "docs/Tesis/v10 (IA)/paper/sections" "docs/Tesis/v10 (IA)/paper/main.tex" "docs/Tesis/v10 (IA)/paper/preambles/preamble.tex" "docs/Tesis/v10 (IA)/Bibliography_base.bib"`, recompilar el PDF y regenerar `tesis_para_agente.md`. La herramienta, sus pruebas y el registro de decisiones pueden conservarse (por defecto no modifican nada) o retirarse con el mismo `git checkout`/`git rm`. No hay tags ni releases involucrados: la publicacion es de c-141.

## Success Criteria

- [ ] `revision_tildes.py` existe, su ejecucion por defecto no modifica archivos y sus pruebas pasan, incluida la regresion que detecta las 40 erratas de la linea base con la clase esperada.
- [ ] Cero erratas de la muestra del dictamen y de los hallazgos adicionales fuera de zonas protegidas; todo candidato no automatico tiene decision y justificacion registradas; `revision_tildes.py --check` termina con codigo 0.
- [ ] Cadenas visibles de `main.tex`/`preamble.tex` y notas impresas de la bibliografia acentuadas; OQ1 resuelta y aplicada o documentada.
- [ ] Diff puramente diacritico; ninguna ocurrencia previa de las cadenas canonicas alterada; cifras, claves y rutas intactas; mismo numero de paginas que antes de la pasada (<= 101); compilacion sin errores ni referencias indefinidas; `verify_citations.py` PASS; `tesis_para_agente.md` regenerado.
- [ ] `dictamen-correcciones.md` registra la pasada B14 con causa raiz y procedimiento de pasada corta; `acentuar_tesis.py` y `acentuar_tesis_v9.py` marcados DEPRECADO.
