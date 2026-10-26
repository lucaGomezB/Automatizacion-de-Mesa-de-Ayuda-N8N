## Why

El dictamen CONEAU del 2026-10-22 sobre la tesis v10 / release `v1.1.0` (`auditorias/Dictamen_Tesis_v10_v1.1.0_CONEAU_2026-10-22.md`, aplicable por igual a `v1.1.1`) aprueba con observaciones (nota 8, ponderado 7,67 en su revision vigente) y condiciona la aprobacion plena a cinco observaciones de fondo (A1-A5) mas trece correcciones de consistencia (B4-B16), con "reexamen de las cinco observaciones de fondo antes de la defensa". La FASE 36 reparte esas recomendaciones en doce changes (c-130..c-140 y c-142) que editan las mismas secciones de la tesis (resumen y capitulos 2 a 11 y anexos), agregan numeros, tablas, referencias, al menos una figura y un analisis de sensibilidad, y cada uno verifica solo su porcion. Nadie verifica el documento integrado: que compile limpio, que respete el tope de paginas (hoy 101, con la familia agregando contenido), que los numeros nuevos esten consolidados con procedencia, que los renders y la base de conocimiento reflejen la version final, que cada recomendacion quede trazada y que exista una version etiquetada para el reexamen. Este change cierra la familia: integra, verifica, traza y publica la release `v1.2.0`. La decision del tope de paginas, que este change posee, debe tomarse al inicio de la familia (gate G0) porque condiciona como escriben los demas changes.

## What Changes

- **Gate G0 (al inicio de la familia, antes de aplicar c-130):** registrar en `docs/Tesis/Correcciones/dictamen-correcciones.md` las decisiones bloqueantes: regla y valor del tope de paginas, entorno de compilacion de registro (con reproduccion de la linea base de 101 paginas), inclusion o exclusion de c-140, checkpoints HIGH de c-142 (corrida paga de la ablacion del prompt; existencia de los ~100 incidentes de preproduccion) y nombre de la release; fijar el orden de aplicacion y abrir el libro mayor de paginas con la linea base `v1.1.1`.
- **Precondiciones de integracion:** cada change de la familia (c-130..c-140 y c-142) archivado (o aplicado y pendiente solo de archivo) o explicitamente excluido (solo c-140 es opcional; precedente de cierre "NO REALIZADO" de c-67); sincronizacion de `ramagonzalo` con `origin/main`; regresion cruzada de las verificaciones de cada change sobre el texto integrado; memo `numeros-canonicos.md` consolidado con procedencia y numeracion de secciones unica (hoy varios changes reclaman la "Seccion 3.7"); `evaluation/report.md` y `evaluation/report_sensibilidad_ajustes.md` coherentes con el memo.
- **Presupuesto de paginas:** el total integrado se mide contra el tope vigente. Rama (a), tope de 101 paginas: plan de compactacion por seccion con palancas de forma (precedente c-116) y checkpoints de revision. Rama (b), tope renegociado: se documenta la nueva regla con fuente y fecha.
- **Compilacion de registro:** XeLaTeX + biber en el entorno de registro; 0 errores fatales, 0 referencias o citas indefinidas, 0 etiquetas duplicadas, biber sin WARN ni ERROR, `verify_citations.py` PASS, todas las figuras presentes (incluido el cronograma de c-135 si se adopta), resumen <= 250 palabras y cero valores retirados. La evidencia se consigna en el registro porque `main.log` no se versiona.
- **Renders derivados:** regenerar `tesis_para_agente.md` con `build_tesis_para_agente.py` (su encabezado hoy declara la release `v1.1.0` y el render es anterior a `v1.1.1`); regenerar desde el PDF los textos `tesis_completa_extraida.txt` y `tesis_para_evaluacion.txt` (copias legadas de la era `.docx`: sin tildes y con un solo director); tratar `paper/tesis.docx` segun la disponibilidad de pandoc; verificar el puntero `thesis:` de `openspec/config.yaml` y repuntarlo solo si la ruta cambia.
- **Base de conocimiento:** sincronizar `knowledge-base/11_evaluacion_experimental.md` y `knowledge-base/README.md` con los numeros vigentes de la release (hoy dicen que los numeros "se re-miden", citan una ruta de render y un modelo desactualizados y repiten la afirmacion de ausencia de fuga de datos que A5 refuta).
- **Trazabilidad:** nueva seccion del registro con la matriz A1-A5 y B4-B16 -> change -> archivo:linea en el arbol etiquetado + `\label` ancla, las observaciones no numeradas del dictamen, la lista de verificacion contra la rubrica de la catedra (nueve criterios evaluables) y el libro mayor de paginas; actualizacion del Anexo I de la tesis con el mapeo recomendacion -> change -> seccion.
- **Release `v1.2.0` (patron C1/C2 de c-111, c-121 y c-123):** C1 cambia el tag del Anexo B a `v1.2.0` sin linea de hash y el numero de version del titulo de `Gomez2026_repositorio` a `1.2.0`; tag anotado `v1.2.0` sobre C1 y publicacion en `origin`; C2 consigna el hash completo de 40 caracteres en el Anexo B y en el registro; integracion a `main` por PR con merge commit.
- **Cierre documental:** pasada ortotipografica corta (verificaciones de c-137, sin reaplicar las utilidades de acentuacion que el dictamen identifica como origen de erratas) sobre el texto modificado despues de c-137; cierre de la FASE 36 en `CHANGES.md`.
- Sin cambios de codigo de aplicacion.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tesis-document`: se modifican tres requisitos (compilacion de la tesis apuntada a v10 con las verificaciones de release; presupuesto de paginas como regla unica de tope vigente registrado; coherencia de la version bibliografica con la release publicada, ahora `1.2.0`) y se agregan requisitos para la integracion verificada de la familia c-130..c-142, la trazabilidad de A1-A5 y B4-B16 en el registro y en el Anexo I, la verificacion contra la rubrica del dictamen, los renders derivados regenerados y la release `v1.2.0` con su hash.
- `tesis-numeros-canonicos`: se agrega la consolidacion de los valores introducidos por la familia c-130..c-142 en el memo, con procedencia, estado y numeracion de secciones unica, como precondicion de la release.
- `project-documentation`: se agrega la sincronia de la base de conocimiento con la release publicada de la tesis.

## Impact

- Edita: `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` (Anexos B e I) y, solo bajo la rama (a), las secciones que requiera la compactacion; `docs/Tesis/v10 (IA)/Bibliography_base.bib` (version de `Gomez2026_repositorio`); `docs/Tesis/v10 (IA)/build_tesis_para_agente.py` (encabezado de release); los renders `tesis_para_agente.md`, `tesis_completa_extraida.txt` y `tesis_para_evaluacion.txt`; los artefactos de compilacion versionados de `paper/` (`main.pdf`, `main.aux`, `main.bbl`, `main.bcf`, `main.blg`, `main.toc`, `main.lof`, `main.lot`, `main.out`, `main.run.xml`); `docs/Tesis/Correcciones/dictamen-correcciones.md`; `docs/Tesis/Correcciones/numeros-canonicos.md` (solo encabezado, numeracion y consolidacion, sin redefinir valores); `knowledge-base/11_evaluacion_experimental.md` y `knowledge-base/README.md`; `CHANGES.md` (cierre de la FASE 36); `openspec/config.yaml` solo si cambia la ruta del render.
- No toca: `App/`, `n8n/`, el codigo de `evaluation/` (solo verifica `report.md` y `report_sensibilidad_ajustes.md`), `data/`, `auditorias/`, `docs/Tesis/v9 (IA)/` ni las cinco cadenas de categoria. El contenido sustantivo de los capitulos es de c-130..c-142; este change no lo reescribe, salvo la compactacion de forma de la rama (a).
- Tags: `v1.0.0`, `v1.0.1`, `v1.1.0` y `v1.1.1` son inmutables; se crea el tag anotado NUEVO `v1.2.0` (o el nombre que resuelva la pregunta abierta de nombre).
- Paginas: segun lo que declaran los propios changes, la familia agrega de 5,4 a 12,2 paginas (central del orden de 7,7, de las cuales c-142 aporta +1,0 a +1,4; `design.md`, D3). Con un tope de 101 sobre el total, las palancas de forma no alcanzan y la decision del tope (OQ1) es el riesgo principal del cierre; con la regla del plan de cumplimiento (cuerpo sin anexos <= 100) la estimacion central queda en el limite y exige compensaciones locales.
- Dependencias: c-130..c-139 y c-142 aplicados; c-140 aplicado o excluido; c-137 aplicado antes de la verificacion final.
- Coordinacion: el flujo corre en `ramagonzalo` (Luca trabaja en `main` y `RamaLuca`); el tag, el push y el PR son acciones publicas que requieren confirmacion del usuario.
- Entorno: compilacion con las fuentes reales Arial y Courier New (MiKTeX local, imagen `texlive-thesis` u Overleaf con Arial); en esta maquina no se detectaron `xelatex` en el PATH ni la imagen Docker construida.

## Rollback

Antes de publicar el tag: `git revert` de los commits del change (o `git checkout <commit-previo> -- <rutas>`) y recompilar; los changes de contenido c-130..c-142 no se revierten desde aqui. Despues de publicar el tag: si el PDF aun no se entrego, eliminar `v1.2.0` local y remoto (`git tag -d v1.2.0` y `git push origin :refs/tags/v1.2.0`) solo con confirmacion del usuario; si ya se entrego al jurado, NO se borra ni se mueve: se corrige con una release nueva `v1.2.1`. Los tags `v1.0.0`, `v1.0.1`, `v1.1.0` y `v1.1.1` no se tocan en ningun caso.

## Success Criteria

- [ ] Las decisiones del gate G0 (tope de paginas, entorno de compilacion, inclusion de c-140, checkpoints de c-142, orden de aplicacion y nombre de la release) estan registradas antes de aplicar c-130.
- [ ] Cada change c-130..c-140 y c-142 esta archivado o excluido con justificacion, y las verificaciones de cada uno pasan sobre el texto integrado.
- [ ] El PDF de la release compila sin errores fatales, sin referencias ni citas indefinidas, con biber sin WARN y `verify_citations.py` PASS, y su conteo cumple el tope vigente registrado.
- [ ] Toda recomendacion A1-A5 y B4-B16 figura en el registro con change, archivo:linea en el arbol etiquetado y ancla, y el Anexo I resume ese mapeo.
- [ ] El memo canonico tiene una seccion por numero (sin "3.7" duplicadas) y todo valor de la familia con procedencia.
- [ ] `tesis_para_agente.md`, los textos extraidos y la base de conocimiento reflejan la release `v1.2.0`, y `config.yaml` resuelve a un archivo existente.
- [ ] El tag anotado `v1.2.0` existe, apunta a C1, esta publicado en `origin`, y su hash figura en el Anexo B y en `dictamen-correcciones.md` y coincide con `git rev-parse v1.2.0^{commit}`; tras el merge del PR, `git merge-base --is-ancestor v1.2.0 origin/main` es verdadero.
- [ ] La FASE 36 queda cerrada en `CHANGES.md` y `openspec list` no reporta changes activos de la familia.
