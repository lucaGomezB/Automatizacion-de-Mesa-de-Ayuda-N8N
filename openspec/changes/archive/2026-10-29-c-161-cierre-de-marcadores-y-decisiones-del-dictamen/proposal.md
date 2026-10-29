## Why

El dictamen CONEAU del 2026-10-28 sobre la tesis v10 / release `v1.2.5` (`auditorias/Dictamen_Tesis_v10_v1.2.5_CONEAU_2026-10-28.md`) deja pregunta abierta la procedencia de las corridas y el Anexo I con marcadores `% PENDIENTE AUTORES` (Q1-Q8 en `docs/Tesis/Correcciones/preguntas-para-lucas-dictamen-2026-10-28.md`), la Figura 2 con una fuente obsoleta, sidecars de resultados PII-free fuera del control de versiones y tres afirmaciones sobre Nginx que el repositorio desmiente. Los autores ya respondieron; cerrar estos items ahora, antes de la defensa, elimina datos faltantes visibles y una contradiccion factual del despliegue de la campana.

## What Changes

- **OQ1-B - Anexo I** (`12-anexos.tex`, `sec:anexo-trazabilidad`): reforzar el encuadre de los dictamenes como autoevaluaciones / control de calidad interno frente a criterios CONEAU, solicitadas por los autores, generadas con el perfil `docs/Tesis/Correcciones/Prompt2.docx` aplicado mediante un modelo de lenguaje, no vinculantes y previas a la defensa; sin cambiar los hechos ya declarados por c-160.
- **Figura 2 = A**: conservar la fuente Mermaid `docs/diagrams/arquitectura_sistema.md` (cinco capas, tres canales) como fuente unica de `fig:arquitectura` y retirar/archivar `docs/diagrams/Diagrama de Capas.drawio` y su PNG; actualizar referencias. No se regenera el PNG.
- **Cierre Q1-Q8**: reemplazar los marcadores `% PENDIENTE AUTORES` de `04-marco-metodologico.tex` (4.5) y `12-anexos.tex` (Anexo F) por respuestas verificadas o "no consta": fechas de la corrida telefonica (5 y 6 de octubre; ~2 h y ~3 h), version desplegada **no consta**, recitado de Luca Gomez (parafraseado, softphone, dispositivo SF20GM7; repeticiones), `ingest_via_n8n.py` (2-10; `--source json` + `--insecure`; `https://localhost`; SMTP en `ingest.env` **no consta**), IMAP `everyMinute` sin medicion efectiva (**no consta**), hash de `cache_meta` de `hybrid-v3` **no consta**, registros primarios **no conservados en el repositorio**, y Nginx **activo** el 2-10.
- **Sidecars versionados**: reemplazar la regla `.gitignore` (linea 66) para trackear los sidecars COMPLETOS `data/corpus_resultados.json` y `data/corpus_resultados_telefonia.json` (PII-free) y excluir por defecto el resto; actualizar `data/README.md` y `git add` de los completos. El sidecar `corpus_resultados_n8n.json` (4 filas frente a 119) NO se commitea hasta resolver cual artefacto es autoritativo (OQ2).
- **Correccion Nginx (Q8)**: en `05-arquitectura.tex`, `11-aspectos-legales.tex` y `12-anexos.tex` (Anexo A), distinguir los dos despliegues de la campana: la medicion telefonica (5-6/10) corrio sobre el perfil Compose aislado `corpus` sin proxy, y la ingesta del 2-10 sobre el stack base con Nginx (certificado autofirmado; de alli `--insecure`), sin que las mediciones dependan de TLS.
- **Registro y roadmap**: cerrar las entradas PENDIENTE Q1-Q8 y registrar la correccion Nginx en `docs/Tesis/Correcciones/dictamen-correcciones.md`; abrir la FASE 49 en `CHANGES.md`. Render/PDF al cierre si lo fija el change.
- Sin cambios en `App/`, `n8n/`, `evaluation/`, `openspec/config.yaml`, los cinco identificadores canonicos de sector ni el arbol congelado `docs/Tesis/v9 (IA)/`. Ningun valor del memo canonico cambia.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tesis-document`: se cierran los pendientes Q1-Q8 (protocolo de pruebas, cronograma, Anexo F y Anexo I), se refuerza la naturaleza del Anexo I como autoevaluacion, se retira el drawio y se fija la fuente Mermaid unica de la Figura 2, y se corrige el perimetro Nginx del despliegue de la campana.
- `corpus-n8n-ingest`: se declaran versionados los three sidecars de resultados sin PII, con su regla de privacidad y su fuente autoritativa.

## Impact

- Tesis: `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex`, `05-arquitectura.tex`, `11-aspectos-legales.tex`, `12-anexos.tex`; render `tesis_para_agente.md` y PDF `paper/main.pdf` si el cierre lo exige.
- Diagramas: `docs/diagrams/arquitectura_sistema.md` (se conserva) y `docs/diagrams/Diagrama de Capas.drawio` (+ `.png`) (se retiran/archivan).
- Datos: `.gitignore`, `data/README.md`, y `git add` de los sidecars completos (200 y 81 filas; el de N8N queda excluido por OQ2); coherentizar referencias en `docs/como_cargar_datos_corpus.md`, `scripts/corpus_ingest/README.md` y `knowledge-base/09_decisiones_y_supuestos.md`.
- Registro: `docs/Tesis/Correcciones/dictamen-correcciones.md` y `CHANGES.md` (FASE 49).
- Sin impacto en API, base de datos, runtime ni CI. Governance BAJO. Impacto de paginas previsto neutro (0 a +1 sobre la cuenta posterior a c-160, 109 paginas).
