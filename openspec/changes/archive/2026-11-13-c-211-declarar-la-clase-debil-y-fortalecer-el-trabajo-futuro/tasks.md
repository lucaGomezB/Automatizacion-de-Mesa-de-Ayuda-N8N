# Tasks: Declarar la clase debil y fortalecer el trabajo futuro (change c-211)

Convenciones: `T10/` = `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex`; `T08/` = `08-discusion.tex`; `T09/` = `09-conclusiones.tex`. "D-n" remite a `design.md`. Cifras verbatim de `evaluation/data/campana/analisis/analisis_fuera_de_muestra_c205.json`.

**Reglas para todos los grupos.** No commitear salvo el cierre, no pushear, no crear tags. No recompilar el PDF (`main.pdf`, `compilacion.md`). No modificar `App/`, `n8n/`, `evaluation/`, el clasificador, el corpus (`data/*.json`, `data/*.csv`) ni los archivos de otro workstream (`01`, `02`, `03`, `04`, `11`, `12`, `00-glosario`, `Bibliography_base.bib`); tampoco `07-resultados.tex`. Gobernanza MEDIA: ninguna cifra canonica cambia; no introducir cifras fuera de un artefacto versionado. No tocar `.engram/`. No registrar el change en `CHANGES.md`: queda fuera del alcance solicitado y el archivo lo comparte el workstream c-207 en aplicacion.

## 1. Reconocimiento y red de seguridad

- [x] 1.1 Confirmar las cifras por clase y de la validacion en `analisis_fuera_de_muestra_c205.json`: `Sistemas` F1 0,2222 (soporte 5), 3 de 5 predichos como `Soporte Tecnico Software`; macro-F1 0,7447; exactitud estricta 0,8447 (87/103); 47 excluidos. Aceptacion: queda registrada la lista de cifras verbatim a usar en el reporte.
- [x] 1.2 Ejecutar `python3 "docs/Tesis/v10 (IA)/verify_citations.py"` para capturar el baseline (PASS) antes de editar. Aceptacion: baseline registrado; `STATUS: PASS`.
- [x] 1.3 Auditar las referencias a labels de `T10/` en `docs/Tesis/v10 (IA)/paper/`: confirmar que solo `subsec:cola-respaldo` es externa (`06-implementacion.tex:60`). Aceptacion: lista de labels seguros de eliminar y del label a conservar.

## 2. Declarar la clase medida mas debil en la discusion

- [x] 2.1 En `T08/`, subseccion "Interpretacion de los resultados", agregar un parrafo explicito tras el parrafo de la confusion de `Sistemas`: F1 0,2222 sobre 5 casos, 3 de 5 predichos como `Soporte Tecnico Software`, soporte pequeno que vuelve imprecisa la estimacion; la frontera es un problema de taxonomia o de criterio de etiquetado; el proximo paso de medicion es el sobremuestreo de las dos clases adyacentes con doble etiquetado y arbitraje. No afirmar ni sugerir mejora. Aceptacion: el parrafo declara la clase debil con sus cifras verbatim y prohibe la promesa de mejora.
- [x] 2.2 En `T09/`, agregar una oracion breve en la conclusion que declare `Sistemas` como la clase de peor desempeno medido, con su cifra y su frontera taxonomica, y remita a la discusion y a los trabajos futuros. Aceptacion: la conclusion menciona la clase debil con su cifra, sin cambiar ninguna otra cifra.

## 3. Reordenar y fundamentar los trabajos futuros (`T10/`)

- [x] 3.1 Reescribir el parrafo introductorio de `T10/` para declarar la prioridad de forma explicita y ordenada, segun D1: (1) defectos medidos, (2) fortalecimiento de la evidencia o del clasificador, (3) extensiones funcionales; y anunciar el orden de las subsecciones. Aceptacion: la introduccion declara el orden que siguen las subsecciones.
- [x] 3.2 Reordenar las subsecciones de `T10/` al orden de D1: `calibracion-gate`, `clasificador-supervisado`, `frontera-sistemas` (nueva), `medicion-intervencion`, `corpus-independiente`, `aprendizaje-activo`, `estudios-replicacion`, `evaluacion-modelos-abiertos`, `cola-respaldo`, `ampliaciones-producto` (nueva). Aceptacion: el orden del archivo coincide con el declarado.
- [x] 3.3 Agregar la subseccion nueva `subsec:frontera-sistemas` (prioridad 2) que ata el item a la limitacion medida (F1 0,2222 sobre 5 casos; 3 de 5) y propone el sobremuestreo con doble etiquetado y arbitraje como medicion. Aceptacion: el item cita la cifra medida y da el proximo paso de medicion.
- [x] 3.4 Reescribir `subsec:corpus-independiente` para retirar las cifras de la validacion fuera de muestra (D3) y conservar solo el trabajo futuro (otros corpus, muestras mayores, sin sesgo de exclusion), remitiendo a `07-resultados.tex` para las cifras. Aceptacion: la subseccion no re-informa 0,8447, macro-F1 ni n efectivo.
- [x] 3.5 Fundamentar cada item restante con su limitacion medida o con criterio de exito/tamano de muestra: `calibracion-gate` (gate no derivo ningun caso; confianza de Gemini no discrimina), `clasificador-supervisado` (sin linea de base; orden de magnitud de 5.000 casos), `medicion-intervencion` (25 de 147, 17,0~\%; IC; criterio de Wilson por debajo de 0,15), `estudios-replicacion` (validez externa; cronometrar reasignaciones), `evaluacion-modelos-abiertos` (criterio de exito con corpus independiente, no el corpus ajustado), `cola-respaldo` (criterio de exito explicito). Aceptacion: ningun item queda sin anclaje medido ni sin criterio.
- [x] 3.6 Degradar los seis items de producto a un unico parrafo rotulado `subsec:ampliaciones-producto` (D2): canales de mensajeria, panel de monitoreo, inventario/CMDB, base de conocimientos, automatizacion de la resolucion y agente conversacional; eliminar sus subsecciones y labels, y las referencias internas a ellos. Aceptacion: `rg -n "subsec:panel-monitoreo|subsec:ampliacion-canales|subsec:base-conocimientos|subsec:agente-conversacional|subsec:integracion-inventario|subsec:automatizacion-resolucion" "docs/Tesis/v10 (IA)/paper/"` no devuelve coincidencias.

## 4. Verificacion final y registro

- [x] 4.1 Ejecutar `python3 "docs/Tesis/v10 (IA)/verify_citations.py"` desde la raiz del repositorio. Aceptacion: `STATUS: PASS` (91 entradas, 0 huerfanas, 0 sin usar).
- [x] 4.2 Ejecutar `openspec validate c-211-declarar-la-clase-debil-y-fortalecer-el-trabajo-futuro --strict`. Aceptacion: valido.
- [x] 4.3 Revisar el diff de los `.tex` y confirmar que no cambio ninguna cifra canonica y que `07-resultados.tex` no fue modificado. Aceptacion: `git diff --exit-code -- "docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex"` da exit code 0 y las cifras del texto coinciden con `analisis_fuera_de_muestra_c205.json`.
- [x] 4.4 Verificacion de alcance: `git status --porcelain` debe mostrar solo `10-recomendaciones.tex`, `08-discusion.tex`, `09-conclusiones.tex` y los artefactos del change. Aceptacion: confirmado; no cambiaron `App/`, `n8n/`, `evaluation/`, `data/*.json`, `data/*.csv`, `main.pdf`, `compilacion.md` ni `.engram/`.
