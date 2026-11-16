# Auditoría interna en estilo CONEAU — Tesis v1.5.0

- **Fecha**: 2026-11-15.
- **Documento evaluado**: `docs/Tesis/v10 (IA)/paper/` en la version `v1.5.0` (commit `5cd0011e6ddd`), 159 paginas, 11 capitulos y 9 anexos, ~56.000 palabras, 94 entradas bibliograficas.
- **Naturaleza**: **autoevaluacion interna**, elaborada por el equipo para estimar el estado del trabajo antes de la defensa. **NO** es un dictamen oficial de la CONEAU ni de ningun evaluador externo; los dictamenes reales (recibidos) viven en `auditorias/`.
- **Metodo**: lectura completa de las secciones, verificacion de correspondencia texto-bibliografia y comprobacion de resolucion de identificadores de objeto digital (DOI). No se modifico ningun archivo.

---

## 1. VEREDICTO GENERAL

**APROBADO CON OBSERVACIONES.**

Trabajo de grado por encima de la media para la Tecnicatura: sistema efectivamente construido y desplegado, evaluacion empirica con pruebas estadisticas adecuadas, y un ejercicio de honestidad metodologica poco frecuente (refuta dos de sus tres sub-hipotesis y declara con precision sus limites). La documentacion, la reproducibilidad del repositorio y la madurez de la ingenieria (1.773 pruebas unitarias, integracion continua, contenerizacion) son solidas.

Las observaciones **no comprometen la aprobacion**, pero deben ser consideradas por el tribunal y, varias, corregidas antes de la defensa: (i) la validacion primaria es **dentro de la muestra**; (ii) la referencia de verdad depende de **un unico arbitro en 64 de 206 casos**; (iii) la muestra es **no probabilistica, de una sola organizacion**; y (iv) existen **inconsistencias internas** entre resumen, introduccion y los capitulos de resultados/discusion.

---

## 2. OBSERVACIONES POR SECCION

### 2.1. Estructura general — CUMPLE

Organizacion logica. El orden `6 -> 7 -> 8` (Implementacion -> Aspectos legales -> Resultados) esta justificado en `11-aspectos-legales.tex:6`. La numeracion de capitulos no presenta saltos. El capitulo de resultados anuncia "doce apartados", que coinciden con las doce subsecciones existentes (verificado).

**Debilidad**: no existe un apartado ni parrafo que declare explicitamente la organizacion del documento (un "mapa de lectura") en la introduccion.

### 2.2. Claridad y formulacion de la hipotesis — CUMPLE PARCIALMENTE

Hipotesis **explicitas, contrastables y falsables**: tres sub-hipotesis con su prueba y criterio de falsacion nombrados (Wilcoxon pareado; Wilson con regla de tres vias; umbral 85 %/0,85 con IC).

- **No hay hipotesis principal unificada**: el texto la desdobla deliberadamente y no enuncia una proposicion maestra unica.
- **Denominador fijado post hoc** (senal de HARKing) en la sub-hipotesis de intervencion humana (`01-introduccion.tex:34`).
- **Tension regla/veredicto**: la regla daria "refutada" en 25/147 = 17,0 %; el cuerpo lo reporta como "no concluyente" (justificado), pero el resumen omite el matiz.
- **Subsidiaria multicanal**: incorpora "complejidad operativa percibida", que el texto declara no medida (no falsable en ese aspecto).

### 2.3. Definicion y coherencia de los objetivos — CUMPLE PARCIALMENTE

Un objetivo general y seis especificos, con tabla de cumplimiento por objetivo en conclusiones (acierto metodologico).

- **Objetivo 2 (clasificador, umbral 85 %/0,85): "No alcanzado"** (in-sample 73,5 %; fuera de muestra 0,6893). Declarado con honestidad.
- Objetivos 1, 3 y 6 formulados como capacidades sin criterio numerico de aceptacion.
- El umbral, declarado "a priori", se fundamenta en parte con mediciones del propio estudio.
- El resumen afirma "viabilidad tecnica y economica" junto a un criterio de exito no alcanzado; conviene distinguir viabilidad de cumplimiento del umbral.

### 2.4. Estado del arte — CUMPLE

Protocolo de revision declarado y auditable (Scopus, IEEE Xplore, ACM DL, ACL Anthology, Google Scholar, arXiv; cortes 21 y 25 de octubre de 2026). Declara su propio punto ciego (sin repositorios regionales: SciELO, Redalyc, JAIIO). Literatura actual y pertinente (predominio 2023-2026). Brecha de novedad acotada y falsable (Gemini sobre tickets en espanol; cascada reglas+LLM con confianza verbalizada sobre tickets en espanol), con hedged correcto.

**Debilidades**: parte de la evidencia comercial es relevamiento propio de documentacion de proveedores (evidencia debil y volatil); celdas "no reportado en el alcance revisado"; sin analisis de riesgo de sesgo o de calidad de las fuentes.

### 2.5. Marco teorico — CUMPLE

Once ejes, con definiciones operativas y vinculacion a decisiones del sistema. Cubre kappa de Cohen (bandas Landis-Koch), calibracion (ECE, Brier, AUROC), clasificacion multietiqueta y las pruebas estadisticas usadas (Wilcoxon, Wilson, bootstrap, McNemar). Etiqueta como *inferencia de los autores* lo que no proviene de la literatura.

**Debilidades**: eje multietiqueta fino (una fuente); ASR solo como marco conceptual; sin referencias modernas de calibracion de LLM mas alla de 2024.

### 2.6. Desarrollo metodologico o propuesta — CUMPLE PARCIALMENTE

Diseno **cuasiexperimental de muestras pareadas**; arsenal estadistico apropiado (Shapiro-Wilk, Wilcoxon, rank-biserial, Wilson, bootstrap, McNemar, Spearman, potencia con MDE). Sistema construido y desplegado (5 capas, 3 canales, 7 entidades); pruebas cuantificadas (1.773 unitarias, 90 % backend; 61 integracion; 99,6 % frontend); CI en GitHub Actions. Declara **ocho amenazas a la validez**.

Debilidades estructurales:

- **Ajuste y evaluacion sobre el mismo corpus**: metricas primarias son estimaciones dentro de la muestra (declarado).
- **Universo proyectado, no medido**: 2.646 = 42 x 63; muestreo **no probabilistico por conveniencia**.
- **Instrumentos asimetricos y campanas no comparables** (cronometraje manual con redondeo al alza; cambio de instrumento entre campanas).
- **Efecto de orden no estimado** (contrabalanceo no ejecutado; operador confundido con mitad del corpus).
- **Referencia de verdad fragil**: kappa 0,5569; **arbitro unico** en 64/206; etiquetadores = operadores, uno autor; doble etiquetado original no conservado.
- **Configuracion efectiva no unica**: tiempos de `hybrid-v1` vs metricas de `hybrid-v3`.
- **Trazabilidad incompleta**: no constan intervalo efectivo sobre N8N 2.11.2, version del 6 de octubre, ni host SMTP.
- **Metadatos desalineados**: cobertura/pruebas medidas sobre `v1.2.18`; configuracion evaluada `v1.3.0`.

### 2.7. Conclusiones — CUMPLE

Responden explicitamente a hipotesis y objetivos. Veredicto por sub-hipotesis: **una corroborada** (tiempo), **una no concluyente** (intervencion humana, puntual sobre la cota), **una refutada** (exactitud y macro-F1). Tabla de cumplimiento por objetivo (objetivo 2 "No alcanzado"). Fortaleza del trabajo.

**Observacion menor**: el balance neto como positivo con IC que excluye el cero (conclusiones) vs "condicional" (introduccion) sobre una tasa de error manual que, segun la discusion, **si fue medida** (e_man = 26/151 = 0,1722).

### 2.8. Propuestas de trabajos futuros — CUMPLE

Tres niveles de prioridad, fundamentados en limitaciones declaradas. Distingue lo ya ejecutado de lo pendiente (el clasico ya medido; la validacion fuera de muestra ya realizada; la recalibracion isotonica ya probada sin exito). Salvedad: el nivel 3 (cola asincrona y extensiones) no deriva de una limitacion medida ni declara criterio de exito.

### 2.9. Bibliografia — CUMPLE

- **94 entradas**; **40 (43 %) del periodo 2023-2026**; base metodologica clasica.
- **Composicion**: 49 arbitradas (29 articulos + 19 ponencias + 1 capitulo), 12 libros, 4 normas, 16 web/manuales, 12 misc (normativa legal, arXiv, repo propio). Sin blogs.
- **Correspondencia completa**: 0 citas ausentes del `.bib`; 0 entradas huerfanas.
- **DOI**: 44/44 resuelven (42 Crossref + 2 DataCite).

**Anomalias menores (ninguna indica fabricacion)**: `Powers2011_evaluation` (ano 2011, enlace arXiv 2020, sin DOI); `ramonferrer2026tripletotext` (prefijo DOI 10.1177/SAGE en revista de IOS Press; resuelve al titulo correcto); `AAIP2023_resolucion198` (unica sin URL ni DOI).

---

## 3. INCONSISTENCIAS INTERNAS DETECTADAS

| # | Ubicacion | Observacion |
|---|-----------|-------------|
| 1 | Resumen vs. cuerpo | El resumen reporta la intervencion humana como "no concluyente" donde la regla daria "refutada" (25/147 = 17,0 %). |
| 2 | Introduccion vs. discusion | La introduccion dice que la tasa de error manual "no fue re-medida"; la discusion reporta que si fue medida (e_man = 26/151 = 0,1722). |
| 3 | Resumen vs. introduccion | La introduccion acota la contribucion a la validacion dentro de la muestra; el resumen reporta ademas validacion fuera de muestra sin declarar la distincion. |
| 4 | Premisa vs. medicion | Tiempo manual a priori 165 s vs medido 61,6 s (~2,7x). Declarado. |
| 5 | Reproducibilidad | Cobertura y nro. de pruebas medidos sobre `v1.2.18`; configuracion evaluada `v1.3.0`. |
| 6 | Capitulo legal | Conviven etiquetas de release `v1.2.2` y `v1.3.0`. |
| 7 | Nomenclatura | Nombres de sector con tildes en la prosa vs cadenas canonicas sin tildes. |
| 8 | Tipografia | Signos de apertura de interrogacion malformados (`?` en lugar de `¿`). |
| 9 | Redaccion | "tasa de error manual medida (82,78 %)" es ambiguo: 82,78 % es una exactitud. |
| 10 | Limitaciones | Declara "nueve limitaciones", pero la novena (acceso cerrado a `paket2024itservice`) se autocancela ("queda superada"). |

---

## 4. RECOMENDACIONES CONCRETAS

**Forma (bajo costo, alto impacto):**
1. Corregir signos `¿` y unificar los nombres de sector con la forma canonica sin tildes cuando se citan como cadenas del sistema.
2. Etiquetar "(82,78 %)" como *exactitud del brazo manual*, no como tasa de error.
3. Anadir un parrafo de organizacion del documento al final de la introduccion.

**Consistencia (necesarias antes de la defensa):**
4. Reconciliar el veredicto de la intervencion humana (resumen/regla/cuerpo).
5. Reconciliar el estado del balance neto entre introduccion y discusion.
6. Alinear las cifras de cobertura/pruebas con la configuracion evaluada (`v1.3.0`).

**Fondo (no bloqueantes):**
7. Recomponer el relato de un unico corpus congelado (que numero proviene de que configuracion).
8. Reforzar la validez externa en la conclusion (sesgo de seleccion).
9. Precisiones de bibliografia: localizador en `AAIP2023_resolucion198`; ano/enlace de `Powers2011_evaluation`; editor de `ramonferrer2026tripletotext`.

---

## 5. CONCLUSION DEL EVALUADOR

Investigacion aplicada completa, con sistema real, evaluacion empirica fundada y autoexamen metodologico que excede lo habitual. Su aporte (evidencia en espanol rioplatense para clasificacion de tickets con enfoque hibrido) es pertinente y esta bien documentado. Las limitaciones que condicionan su alcance son declaradas por los propios autores con transparencia; ese reconocimiento es un merito, no un defecto oculto. No obstante, mientras subsistan las inconsistencias internas (puntos 4, 5 y 6) y la dependencia de metricas dentro de la muestra (que acota el valor probatorio de los resultados de clasificacion), el veredicto no puede elevarse a "aprobado sin observaciones".

El techo alcanzable con correcciones de redaccion, consistencia y sensibilidad es del orden del documento escrito elevado; superarlo exigiria **evidencia nueva** (otra organizacion, mas etiquetadores independientes, remedicion con instrumento unico), fuera del alcance de esta entrega y correctamente consignada como trabajo futuro.

**Dictamen: APROBADO CON OBSERVACIONES**, con recomendacion expresa de resolver las consistencias internas antes de la defensa oral.

---

*Nota de alcance: esta auditoria es una simulacion interna. El unico dictamen con efecto academico es el emitido por el tribunal evaluador. Los dictamenes externos recibidos se archivan en `auditorias/`.*
