## Why

El dictamen independiente `Dictamen_Tesis_v10_v1.3.0_CONEAU_2026-11-13.md` identifico recomendaciones de consistencia y de forma (puntos 7 a 14, mas una correccion de honestidad) que no requieren evidencia nueva y que un tribunal puede senalar en la defensa. Corregirlas antes de la entrega mejora la coherencia interna del manuscrito sin tocar ninguna cifra canonica.

## What Changes

- **Regla de tres vias asimetrica (rec. 7):** declarar de forma expresa, en `01-introduccion.tex` y en `04-marco-metodologico.tex`, que la regla de la segunda sub-hipotesis es asimetrica (declara "refutada" cuando la estimacion puntual alcanza la cota, sin usar el intervalo) y que el denominador de 147 casos se adopto despues de conocer los datos.
- **Enunciado y veredicto separados (rec. 8):** en `01-introduccion.tex`, dejar las sub-hipotesis solo enunciadas con su contraste y criterio de falsacion; retirar los veredictos y los resultados observados, que pertenecen a resultados y conclusiones. Unificar la posicion sobre el umbral del 85 %: tratarlo como criterio de exito central del estudio, fijado a priori por los autores y no como valor tomado de la literatura.
- **Objetivos 1 y 3 (rec. 9):** reformular el objetivo 1 como comunicacion sincronica (la implementacion lo es) y quitar del objetivo 3 la clausula no medible sobre la complejidad operativa percibida.
- **Higiene de prosa de proceso (rec. 10):** retirar del cuerpo las referencias a versiones anteriores (`01-introduccion.tex:34`, `04-marco-metodologico.tex:81`), la ruta interna del repositorio en `03-estado-del-arte.tex:8` y reducir el Anexo I de `12-anexos.tex` (historia de nueve dictamenes) a una nota breve de versiones, conservando la divulgacion de asistencia de un modelo de lenguaje.
- **Fundamentos teoricos (rec. 11):** agregar al `02-marco-teorico.tex` el acuerdo entre anotadores y el coeficiente kappa, la clasificacion multietiqueta y las pruebas estadisticas empleadas (Wilcoxon, intervalos de Wilson, bootstrap y McNemar).
- **Ubicacion del capitulo legal (rec. 12):** justificar en una oracion, al inicio de `11-aspectos-legales.tex`, por que el capitulo se ubica entre implementacion y resultados. No se mueve el capitulo.
- **Bibliografia (rec. 13):** actualizar la entrada del repositorio propio a la version 1.3.0, convertir a `@inproceedings` las tres entradas de PMLR cargadas como `@article`, agregar la pagina de la atribucion a Zanzotto y verificar que los DOI de las entradas de 2025 y 2026 resuelvan.
- **Glosario (rec. 14):** agregar iPaaS, SaaS, kNN y CoT a `00-glosario.tex`, conservando el orden alfabetico.
- **Honestidad (bonus):** suavizar la afirmacion de que ningun trabajo declara un corpus en espanol, porque descansa en una ausencia de dato (idioma "no reportado" en cuatro de seis filas) y no en una constatacion.

**BREAKING**: ninguna. No cambia ninguna cifra canonica, metrica, dato ni artefacto de evaluacion. No se recompila el PDF.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tesis-document`: se agregan requisitos de consistencia y forma del manuscrito (hipotesis y umbral coherentes, prosa de proceso retirada, fundamentos teoricos previos a la evidencia, ubicacion legal justificada, metadatos bibliograficos y glosario completos, vacancia del corpus en espanol acotada a la evidencia).

## Impact

- Tesis: `00-glosario.tex`, `01-introduccion.tex`, `02-marco-teorico.tex`, `03-estado-del-arte.tex`, `04-marco-metodologico.tex`, `11-aspectos-legales.tex`, `12-anexos.tex` y `Bibliography_base.bib`.
- No se toca: `App/`, `n8n/`, `evaluation/`, `data/`, el corpus, las cifras canonicas, `07-resultados.tex`, `08-discusion.tex` ni `09-conclusiones.tex`; tampoco el parrafo de consentimiento E3/E4 de `11-aspectos-legales.tex`.
- Gobernanza: MEDIA (texto academico y bibliografia). No se altera evidencia ni se introducen afirmaciones nuevas sin respaldo.
- Verificacion: `python3 "docs/Tesis/v10 (IA)/verify_citations.py"` debe permanecer en PASS con 0 huerfanas y 0 sin usar. No se recompila el PDF.
