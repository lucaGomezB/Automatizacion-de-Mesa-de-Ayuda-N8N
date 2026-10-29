## Why

El dictamen CONEAU del 2026-10-28 sobre la tesis v10 / release `v1.2.5` (`auditorias/Dictamen_Tesis_v10_v1.2.5_CONEAU_2026-10-28.md`) deja abiertas las recomendaciones 9 a 13: precisiones de consistencia estadistica y de metodo, del capitulo legal, de forma y glosario, de bibliografia y de fuentes primarias. Las recomendaciones 5-8 ya las atendio c-160, las A1-A4 c-158/c-159, los marcadores Q1-Q8 y Nginx c-161 y el contacto del reportante c-162. Cerrar los residuos de 9 a 13 antes de la defensa elimina descuentos de rubrica en los criterios 3, 4, 6, 8 y 9 sin agregar mediciones nuevas.

## What Changes

- **Rec 9 (consistencia)**: enunciar la hipotesis nula de Wilcoxon sobre las DIFERENCIAS PAREADAS (1.4 y 8.1); "cuasiexperimental" en 4.1; separar en 8.5 el efecto de cobertura (74 -> 131) del de exactitud (38 vs 37 en los 67 casos comunes) y presentar la "cota pesimista" como interpretacion; completar el Anexo H (`safety_settings`, ejemplos por clase, grafia de la clave JSON).
- **Rec 10 (legal, `11-aspectos-legales.tex`)**: agregar "disociacion" (art. 2, Ley 25.326) junto a "pseudonimizacion"; articulos 14 (10 dias corridos) y 16 (5 dias habiles); presentar la trazabilidad como medida TECNICA que facilita el art. 9; RGPD art. 3.2 ("personas que se encuentren en la Union"); entrada bibliografica de la Decision 2003/490/CE.
- **Rec 11 (forma y consistencia)**: glosario (agregar ECE, HITL, BERT, RAG, ISO, NIST, CSF, MFA, TOTP, KMS, PAM, SIEM, SBOM, RTO, SAST, IC, CMDB; retirar HMM y WIP); citar la Figura 8 desde 8.1 y las Figuras 3-5 desde el capitulo 5; regenerar desde Mermaid las Figuras 2, 3, 8, 9 y 11 (erratas); "sobre que aspecto" -> "sobre que aspecto" con tilde, identificadores sin tilde en Tabla 5, "seudonimizado" -> "pseudonimizado"; lineas fuera de margen (pp. 34/57/99/100/102), texto encimado en Tablas 5 y 6, espaciado del indice 11.10-11.14; fecha de portada fija; rol de cada director en 4.9.
- **Rec 12 (bibliografia)**: coma antes del ano con "et al."; sentence case de titulos; "2.a ed."; raya corta en rangos; "ISO/IEC" como autor institucional; "(Vol., pp.)" en Paramesh; dia en entradas legales; Hohpe y Woolf 2004; nota de Mayor-Rocher en espanol; apellido compuesto de Touvron; version arbitrada o justificacion de Ramya con fecha de consulta; edicion/editor/DOI de Efron y Tibshirani.
- **Rec 13 (fuentes primarias)**: Shapiro-Wilk, McNemar, metricas multietiqueta (subset accuracy, Hamming loss, micro-F1), r rank-biserial, eficiencia relativa asintotica de la prueba de rangos con signo, regresion isotonica como calibracion; y fuente primaria de Wilcoxon en 8.1 ademas de la implementacion.
- Docs-only sobre `docs/Tesis/v10 (IA)/`. Sin cambios en `App/`, `n8n/`, `evaluation/`, `openspec/config.yaml`, cadenas canonicas ni `docs/Tesis/v9 (IA)/`. Sin cambios de numeros canonicos.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tesis-document`: se corrigen la enunciacion de la hipotesis nula de Wilcoxon, el rotulo cuasiexperimental, la descomposicion de 8.5, el Anexo H, la precision legal de la Ley 25.326 y el RGPD, la citacion de figuras, el rol de los directores, la conformidad formal APA 7 y las fuentes primarias de los metodos estadisticos; se congela la fecha de portada y se admite el crecimiento bibliografico por las fuentes de metodo.

## Impact

- Tesis: `docs/Tesis/v10 (IA)/paper/sections/*.tex` (`00-portada`, `00-glosario`, `01-introduccion`, `04-marco-metodologico`, `05-arquitectura`, `07-resultados`, `11-aspectos-legales`, `12-anexos`), `preambles/preamble.tex`, `Bibliography_base.bib`.
- Figuras: PNG de `componentes.png` (Fig. 2), `er_modelo_datos.png` (3), `boxplot_tiempos.png` (8), `heatmap_confusion.png` (9) y la figura del flujo (11), regeneradas desde sus fuentes Mermaid en `docs/diagrams/`.
- Render: `tesis_para_agente.md` y PDF `paper/main.pdf` recompilados al cierre.
- Registro: `docs/Tesis/Correcciones/dictamen-correcciones.md` y `CHANGES.md` (FASE 50).
- Sin impacto en API, base de datos, runtime ni CI. Governance MEDIUM (rec 10 legal sensible; rec 11 forma; rec 12-13 bibliografia).

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| El cuerpo esta en el tope de 100 paginas; nuevas entradas bibliograficas o texto lo empujan | Med | Redactar en el lugar; registrar el delta de paginas y aplicar palancas de forma si hace falta |
| Una figura no se puede regenerar fielmente con el toolchain (`texlive-thesis`/`mmdc`) | Med | Regenerar las que se puedan y declarar explicitamente las que no, sin dejar erratas |
| El tope de paginas no admite margen para la rec 10 | Bajo | Las adiciones legales son de pocas palabras; no se agrega contenido cientifico |

## Rollback Plan

Revertir el commit del change: `git revert <sha>` deja intactas las correcciones previas (c-158 a c-162). Al ser docs-only sin migraciones ni cambios de runtime, no hay estado que restaurar; recompilar el PDF anterior si se revierte el render.

## Dependencies

- Toolchain de Docker `texlive-thesis` y `mmdc` para recompilar y regenerar figuras.
- Fecha de entrega real para la portada (input del autor; ver Open Questions).

## Success Criteria

- [ ] `openspec validate "c-163-atender-las-recomendaciones-9-a-13-del-dictamen" --strict` pasa.
- [ ] La tesis compila sin referencias indefinidas ni etiquetas duplicadas y `verify_citations.py` da PASS.
- [ ] Cada recomendacion 9 a 13 y cada fila del inventario queda atendida o declarada inaplicable.
- [ ] El tope de paginas del cuerpo se mantiene o el exceso queda registrado y honrado.
