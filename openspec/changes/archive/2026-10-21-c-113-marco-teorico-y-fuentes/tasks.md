## 1. Preparación y baseline

- [x] 1.1 Confirmar el baseline de citas y expresiones: `grep -n "trazabilidad auditiva" "docs/Tesis/v9 (IA)/paper/sections/"*.tex` (esperado: 1 en `02-marco-teorico.tex:28`), `grep -n "soberanía digital" "docs/Tesis/v9 (IA)/paper/sections/01-introduccion.tex"` (esperado: 1 en la línea 60) y `grep -c "^@" "docs/Tesis/v9 (IA)/Bibliography_base.bib"` (registrar el conteo inicial: 53).
- [x] 1.2 Verificar la resolución de la cita canónica propuesta: `curl -s https://api.crossref.org/works/10.1145/3571730` devuelve "Survey of Hallucination in Natural Language Generation" (ACM Computing Surveys, 2023); registrar el resultado en una nota de tarea.

## 2. Marco teórico — conceptos y terminología

- [x] 2.1 En `02-marco-teorico.tex` §2.3, reformular como glosa propia rotulada ("se entiende aquí por…") o fundamentar con cita verificable las definiciones de "automatización de procesos empresariales" (BPA) e "plataformas de integración como servicio" (iPaaS); verificar que ninguna quede como aserción sin fuente (`grep -n "BPA\|iPaaS"` y lectura del párrafo).
- [x] 2.2 En `02-marco-teorico.tex:28`, corregir "trazabilidad auditiva" por "trazabilidad auditable"; verificar con `grep -rn "trazabilidad auditiva" "docs/Tesis/v9 (IA)/paper/sections/"` (0 coincidencias) y `grep -rn "trazabilidad auditable"` (>= 1).
- [x] 2.3 En `02-marco-teorico.tex` §2.4, añadir la cita canónica de la definición de "alucinación" (`\textcite{Ji2023_hallucination}` o `\parencite{Ji2023_hallucination}`); verificar que el párrafo de la definición la incluya y que colavito2025benchmarking se conserve para su uso actual (ejemplificación).

## 3. Marco teórico — eje de reconocimiento automático del habla

- [x] 3.1 En `02-marco-teorico.tex` §2.5, recortar el párrafo de aplicación (`:62`) que afirma que el ASR permite automatizar la captura telefónica y conservar un desarrollo mínimo que justifique su inclusión como marco conceptual del canal telefónico y declare que la transcripción la provee un servicio externo; verificar que no se afirme integración del ASR al sistema (`grep -n "reconocimiento del habla\|ASR\|Whisper"` y lectura).
- [x] 3.2 Verificar que la restricción de c-92 ("Whisper no se presenta como componente") permanezca satisfecha tras el recorte; confirmar que no se reintroduce lenguaje de integración del ASR.

## 4. Introducción — formulación jurídica de la soberanía

- [x] 4.1 En `01-introduccion.tex` §1.7 (línea 60), sustituir "principio de soberanía digital promovido por la Ley~25.326" por la formulación jurídica exacta (control sobre los datos personales y su tratamiento conforme a la normativa de protección de datos), reutilizando la entrada `Ley25326_2000`; verificar con `grep -rn "soberanía digital" "docs/Tesis/v9 (IA)/paper/sections/"` (0 coincidencias).

## 5. Bibliografía (aditiva)

- [x] 5.1 Agregar de forma aditiva la entrada `Ji2023_hallucination` a `Bibliography_base.bib` con `author`, `title`, `year`, `journal`, `doi = {10.1145/3571730}` y metadatos completos; NO editar entradas existentes; verificar con `grep -n "Ji2023_hallucination" "docs/Tesis/v9 (IA)/Bibliography_base.bib"` y que el conteo `grep -c "^@"` haya aumentado exactamente en las entradas nuevas.
- [x] 5.2 Verificar integridad bibliográfica: cero citas huérfanas y cero entradas sin uso con `python scripts/verify_citations.py` (o el verificador equivalente del repo) desde `docs/Tesis/v9 (IA)/`; registrar el resultado.

## 6. Compilación y verificación final

- [x] 6.1 Compilar con la imagen Docker: `docker run --rm -v "/home/skywalker/Desktop/notas/Tesis/Automatizacion-de-Mesa-de-Ayuda-N8N/docs/Tesis/v9 (IA)":/work -w /work/paper texlive-thesis latexmk main.tex`; verificar compilación sin errores fatales.
- [x] 6.2 Contar páginas del PDF resultante y registrar el total; el neto no debe superar el techo de 100 ni crecer respecto del baseline (c-116 reduce páginas después). Si crece, recortar el eje de ASR (tarea 3.1).
- [x] 6.3 Verificar en el PDF compilado las cinco correcciones: BPA/iPaaS fundamentados o glosados, soberanía reformulada, alucinación con cita canónica, ASR acotado/justificado y "trazabilidad auditable".
