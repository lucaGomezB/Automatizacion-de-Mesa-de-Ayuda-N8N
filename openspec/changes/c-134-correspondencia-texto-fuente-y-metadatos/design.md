## Context

El change cierra la observacion de fondo 4 del dictamen v1.1.0 (recomendacion A4) y las correcciones de consistencia B15 y B16 (ver `proposal.md` - Why). Es documental: edita LaTeX y el `.bib` bajo `docs/Tesis/v10 (IA)/`, mas un ajuste minimo de `verify_citations.py`. Restricciones que condicionan el diseno:

- **Regla de correspondencia:** cada reescritura afirma solo lo que la fuente sostiene, al nivel de evidencia disponible (texto completo si es de acceso abierto; si no, el resumen de la pagina del editor). Ninguna frase va mas alla de su evidencia.
- **Sin fabricacion:** ningun DOI, pagina, edicion, ano o cifra entra al `.bib` o al texto sin verificarse; lo no confirmado queda fuera y se declara.
- **Numeros canonicos congelados** (`docs/Tesis/Correcciones/numeros-canonicos.md`): el change no toca cifras propias de la tesis.
- **Presupuesto de paginas:** el PDF tiene 101 paginas; c-116 y c-121 lo trataron como tope duro y la verificacion final de esta familia la hace c-136 (D13).
- **Changes hermanos sobre las mismas lineas:** c-125 (frase del gate en `02:46`), c-128 (`01:48`), c-129 (`04:71`, `04:91`), c-130 (tabla `tab:trabajos-academicos`), c-131 (`10-recomendaciones.tex`), c-132 (ortotipografia, al final), c-133 (fuentes nuevas de calibracion y cascadas, parrafo de calibracion de reemplazo) y c-136 (integracion y `Gomez2026_repositorio`). Ver D14.
- **Convencion de este artefacto:** las frases propuestas se transcriben sin tildes; en el `.tex` se escriben con la acentuacion correcta.

**Estado verificado (solo lectura, 2026-10-22):**

- Sitios de cita de las claves observadas (`grep -n` sobre `paper/sections/*.tex`): `xuan2025mmluprox` 02:46, 02:52, 03:56; `ahuja2023mega` 02:44, 02:52, 03:56; `lai2023okapi` 02:44, 03:56; `zhang2023multilingual` 02:50, 03:56; `grandury2025laleaderboard` 01:66, 02:50, 03:56; `mayorrocher2026spanish` 01:66, 02:50, 03:56; `paket2024itservice` 03:47 (tabla); `colavito2025benchmarking` 01:66, 02:48, 03:49 (tabla); `zangari2023ticket` 01:66, 03:46 (tabla); `Revina2020_it_tickets` 03:30, 03:45, 08:28, 08:30, 08:32; `Touvron2023_llama2` 10:12; `Paramesh2019_it_service_desk` 01:48, 03:28, 03:44, 08:28, 08:30. La frase de `03:32` no lleva cita: se apoya implicitamente en la tabla que sigue. El barrido por tema encontro ademas `08:34`, que sin cita atribuye a "diversos trabajos" la menor cobertura del espanol y compara con un desempeno "reportado para ... el ingles o el aleman" (el aleman no tiene fuente en la bibliografia).
- Resumenes leidos en la pagina del editor o en ACL Anthology: Paket et al. (BERT supera a Titan, Llama y Mistral en 172 clases en turco), Zangari et al. (20.000 reclamos y 35.000 issues; el resumen no nombra idiomas), Mayor-Rocher et al. (TELEIA; comprenden bien el espanol, sin competencia gramatical nativa), Zhang et al. (alternancia de codigo; rinden por debajo de modelos ajustados mas chicos), Lai et al. (Okapi: ajuste por instrucciones con RLHF en 26 idiomas; los LLM abiertos se ajustaron solo para el ingles y pocos idiomas), Xuan et al. (29 idiomas, 36 modelos; caida marcada en idiomas de bajos recursos; sin calibracion), Ahuja et al. (MEGA: 16 conjuntos, 70 idiomas; dificultad en idiomas de bajos recursos), Grandury et al. (La Leaderboard: 66 conjuntos, 50 modelos, variedades del espanol y lenguas de Espana y America Latina) y Paramesh y Shreedhara (comparan NB multinomial, regresion logistica, kNN y SVM sobre tickets reales de infraestructura TI; SVM rinde mejor; el resumen no consigna 10.000 tickets, 87 %, TF-IDF ni idioma). Colavito et al.: el resumen no esta en Crossref ni OpenAlex y ScienceDirect devuelve 403; su contenido (los BERT ajustados logran un desempeno consistente de estado del arte entre conjuntos, aun con pocos datos; los LLM zero-shot varian entre conjuntos y son costosos) se obtuvo de un listado secundario y debe leerse en el repositorio institucional (ricerca.uniba.it) o en la ficha del editor durante la aplicacion.
- Crossref: `Paramesh2019_it_service_desk` tiene autores Paramesh, S. P. y Shreedhara, K. S. (el dictamen lo llama "Paramesh y Ramya": error de denominacion del dictamen); el libro es *Data Analytics and Learning: Proceedings of DAL 2018*, editores P. Nagabhushan, D. S. Guru, B. H. Shekar e Y. H. Sharath Kumar (forma de la ficha de Springer; Crossref la parte como "Kumar, Y. H. Sharath"), LNNS vol. 43, pp. 331-346, Springer Singapore. `liu2025tickit`: evento "FSE Companion '25", pp. 343-354 (FSE 2025, Trondheim, Noruega). `mayorrocher2026spanish`: Crossref sigue sin volumen ni paginas (la nota "advance article" se mantiene).
- Fichas oficiales: ISO/IEC 27001:2022 (ed. 3, 2022-10, publicada, con Amd 1:2024), ISO/IEC 27002:2022 (ed. 3, 2022-02, publicada), ISO/IEC 27701:2019 (**retirada el 2025-10-14**, reemplazada por ISO/IEC 27701:2025, ed. 2, 2025-10, titulo "Privacy information management systems - Requirements and guidance"); NIST CSWP 29 "The NIST Cybersecurity Framework (CSF) 2.0", 2024-02-26, DOI 10.6028/NIST.CSWP.29 (doi.org 302 al PDF de NIST); Decreto 1558/2001 en InfoLEG (id 70368; P.E.N., 29-11-2001; B.O. 03-12-2001; modificado o complementado por 32 normas).
- Metodo: Wilcoxon (1945), "Individual Comparisons by Ranking Methods", **Biometrics Bulletin** 1(6), p. 80 en Crossref (pp. 80-83 a confirmar en JSTOR), DOI 10.2307/3001968; Efron y Tibshirani (1993), *An Introduction to the Bootstrap*, Chapman & Hall, DOI 10.1007/978-1-4899-4541-9 (registro de Springer US de la edicion de 1993); Cohen (1988), *Statistical Power Analysis for the Behavioral Sciences*, 2.a ed., Lawrence Erlbaum Associates, ISBN 0-8058-0283-5 (el DOI 10.4324/9780203771587 corresponde a la reedicion de Routledge de 2013 y no se usa).
- Anos de libros: Pearson consigna (c) 2018 para Stallings y Brown 4.a ed. (publicada en 2017), (c) 2021 para Russell y Norvig 4.a ed. (la portadilla dice "Copyright (c) 2021, 2010, 2003"; una ficha la fecha de publicacion en abril de 2020) y los catalogos dan c2004 para Date 8.a ed. (minoristas: 2003). Jurafsky y Martin: el borrador vigente es la version del 19 de agosto de 2026 en `https://web.stanford.edu/~jurafsky/slp3/`.
- Render de la bibliografia (`main.pdf`): las notas se imprimen entre corchetes y el estilo suprime el punto y coma (`OGC2011_itil` sale "...Office of Government Commerce la titularidad...", `SEPyME2026_mipyme` "...Argentina consultado el...", `mayorrocher2026spanish` "Advance article volume/pages pending"); las cinco `@online` imprimen la fecha dos veces (nota y "Recuperado el..."); `Tiangolo2024_fastapi` sale "Tiangolo, S. R."; `GDPR2016` y `Jurafsky2023_speech_language` salen sin enlace.
- `verify_citations.py`: la linea "Total unique citation keys" y el mensaje "<-> N unique citation keys" usan `sum(len(keys) for keys in file_keys.values())`, la suma de claves unicas por archivo (92), no el conteo global (59). No existe prueba del script y pytest no esta instalado en los interpretes globales (Python 3.13 y 3.14).

## Goals / Non-Goals

**Goals:**

- Que ninguna atribucion de la tesis a las fuentes observadas afirme mas de lo que esas fuentes sostienen, con la evidencia de cada reescritura registrada.
- Incorporar, verificadas y citadas, las ocho entradas de B15, sin citar ediciones retiradas.
- Corregir los metadatos de B16 con criterios uniformes y explicitos.
- Dejar el verificador de citas con rotulos exactos y una prueba que lo proteja.
- Medir el impacto en paginas, mantener el cuerpo neutral y entregar a c-136 los datos para la compensacion final.

**Non-Goals:**

- No se incorporan fuentes sobre calibracion de la confianza ni sobre cascadas reglas-modelo: son de c-133. c-134 solo retira la atribucion erronea y declara el hueco (D1).
- No se reescriben las frases del gate de `02:46` (c-125), las cifras propias de `08:30` (c-126/c-128), los objetivos y el umbral de `01:48` salvo la clausula de Paramesh (c-128), ni los contrastes de `04:71`/`04:91` salvo la insercion de citas (c-129).
- No se completan las metricas de las demas filas de `tab:trabajos-academicos` (B10, c-130); c-134 solo es dueno de la fila de Paramesh.
- No se corrige ortografia fuera de las frases reescritas (c-132), ni el preambulo LaTeX (palanca tipografica de c-136), ni la version de `Gomez2026_repositorio` (c-136).
- No se renombran claves bibliograficas (D8) ni se regenera `tesis_para_agente.md` (c-136).
- No se tocan las copias historicas de `verify_citations.py` en `docs/Tesis/v8 (IA)/` y `v9 (IA)/`.

## Decisions

### D1 - Interfaz con c-133: retirar la atribucion de calibracion a Xuan et al. y declarar el hueco

En `02:46` se elimina la oracion "\textcite{xuan2025mmluprox} documentan, a partir de una evaluacion comparativa en multiples idiomas, que la calibracion depende del modelo y del dominio." El aporte real de Xuan et al. (rendimiento multilingue) se reubica en `02:50`, donde sostiene "el rendimiento no es uniforme entre idiomas" (D3, T2); la cita de `02:52` (benchmarks con resultados desagregados) se conserva. La definicion de calibracion y la frase siguiente del parrafo (gate, propiedad de c-125) no se tocan. Si c-133 aun no esta aplicado, se deja inmediatamente despues de la definicion, en linea propia y sin linea en blanco (no corta el parrafo; `build_tesis_para_agente.py` elimina comentarios), el ancla:

`% [c-133] Pendiente: fuente(s) verificada(s) sobre la calibracion de la confianza declarada por LLM. c-134 retiro xuan2025mmluprox (no trata calibracion).`

Contrato: c-134 no agrega ninguna fuente de calibracion; c-133 inserta sus fuentes en ese parrafo y elimina el ancla; c-136 verifica que no quede ninguna linea `% [c-133]`. Si c-133 ya se aplico, la tarea de c-134 se reduce a verificar que el parrafo de calibracion no cita `xuan2025mmluprox`. Se informa a c-133 que la fuente primaria del efecto del orden y de la seleccion de ejemplos es Zhao et al. (2021), "Calibrate Before Use" (ICML), que es a la vez una fuente de calibracion y podria cubrir ambos usos.

**Alternativas consideradas:** (a) reescribir la frase en el mismo lugar como limite ("los benchmarks de rendimiento, como el de Xuan et al., no miden calibracion"): se descarta porque una cita de Xuan dentro del parrafo de calibracion sigue leyendose como respaldo del concepto; (b) reemplazarla por fuentes de calibracion: se descarta porque esas fuentes son de c-133; (c) borrarla sin reubicar: es viable (Xuan sigue citado en `02:52`), pero se pierde el respaldo correcto que `02:50` necesita tras corregir la atribucion a Zhang et al.

### D2 - Barrido por clave y registro de evidencia

Para cada fuente observada se revisan todos sus sitios de cita (mapa del Context), no solo la linea senalada por el dictamen. Asi entran el agrupamiento de `03:56` (Lai et al. y Zhang et al. citados para "el rendimiento de clasificacion depende del idioma"), la frase de Colavito et al. en `02:48`, la cita de Jurafsky y Martin en `02:38` (su ano cambia en D8), los cinco sitios de las cifras de Paramesh y, por tema (corpus o desempeno en aleman sin fuente), `08:34`. Cada frase nueva se contrasta con el texto completo cuando es de acceso abierto (ACL Anthology, IEEE Access, arXiv, NIST), o con el resumen de la pagina del editor; la evidencia (URL, seccion o "resumen") se registra en la tabla de D15. La lectura es en linea; no se descargan copias no autorizadas.

**Alternativa considerada:** corregir solo las lineas que nombra el dictamen. Se descarta porque el propio dictamen declara que su muestreo no es exhaustivo y porque `03:56` y `01:48` repiten las mismas atribuciones.

### D3 - Frases propuestas por caso

La regla general es reemplazar la atribucion por lo que la fuente sostiene; las propuestas se verifican contra la fuente antes de escribirse y pueden atenuarse, nunca ampliarse.

- **T1 `02:46` (Xuan, calibracion):** retirar la oracion indicada en D1; el parrafo queda "...un modelo bien calibrado acierta con una frecuencia proxima a la confianza que expresa. En el sistema propuesto este concepto fundamenta..." (mas el ancla de D1, si corresponde).
- **T2 `02:50` (idiomas y variedades):** "El rendimiento de los LLM tampoco es uniforme entre idiomas ni entre variedades de un mismo idioma: sobre 29 idiomas, el desempeno de 36 modelos cae de forma marcada en los idiomas con menos recursos \parencite{xuan2025mmluprox}; el ajuste por instrucciones de los modelos de codigo abierto se concentro en el ingles y en unos pocos idiomas \parencite{lai2023okapi}, y ante textos que alternan idiomas los LLM multilingues rinden por debajo de modelos ajustados de menor escala \parencite{zhang2023multilingual}. Para el espanol, \textcite{grandury2025laleaderboard} proponen una tabla de clasificacion abierta para sus variedades de Espana y America Latina, y \textcite{mayorrocher2026spanish}, con pruebas de espanol como lengua extranjera, observan que los modelos comprenden bien el idioma pero no alcanzan la competencia gramatical de un hablante nativo." La oracion final ("Esta sensibilidad resulta directamente relevante...rioplatense...") se conserva. Evidencia: resumenes de ACL Anthology y de OUP.
- **T3 `02:44` (diseno del prompt):** "La evaluacion multilingue de \textcite{ahuja2023mega}, que compara estrategias de prompting entre idiomas ---ejemplos en el idioma de la tarea, en otro idioma o con traduccion previa al ingles---, muestra que la estrategia elegida modifica el rendimiento de manera sustancial, por lo que el diseno del \emph{prompt} constituye una decision de ingenieria y no un detalle accesorio." Se verifica en el texto completo de MEGA (seccion de estrategias de prompting); si no sostiene "de manera sustancial", se atenua a "modifica el rendimiento". Se retira la afirmacion sobre el orden y la seleccion de ejemplos (su fuente primaria es Zhao et al., 2021; ver D1). La primera oracion del parrafo (con la tilde erronea en el verbo "formula", que corrige c-132) no se toca.
- **T4 `02:48` (Colavito):** "Como el desempeno de los LLM generativos en el etiquetado automatico varia de forma marcada entre conjuntos de datos \parencite{colavito2025benchmarking}, sus etiquetas no pueden aceptarse sin validarlas contra un conjunto de referencia." La cita respalda la premisa; la conclusion queda como inferencia de los autores. Se aplica tras leer el resumen.
- **T5 `02:52` (benchmarks):** sin cambios salvo que la verificacion lo exija; precision admitida: "abarcan multiples tareas o disciplinas y reportan resultados desagregados por idioma".
- **T6 `02:38` (Jurafsky y Martin, condicional):** si el indice de la version citada no sostiene "sistematizan la disciplina en torno a tres ejes principales", se atenua a "\textcite{Jurafsky2023_speech_language} abordan, entre otros temas, el modelado estadistico de secuencias, la representacion distribuida de palabras y las arquitecturas neuronales profundas aplicadas a la comprension semantica."
- **T7 `03:30` (Revina):** reemplazar "Un hallazgo especialmente relevante para el presente trabajo es que los modelos preentrenados pueden rendir peor en este dominio, cuyo vocabulario contiene numerosos terminos ausentes del corpus general de entrenamiento. Este resultado introduce una tension productiva" por "Los autores excluyen ademas, como decision de diseno y no como resultado medido, las representaciones de palabras preentrenadas (\emph{word embeddings}), con el argumento de que el vocabulario del dominio contiene numerosos terminos ausentes de los corpus generales de entrenamiento. Ese argumento introduce una tension productiva". El resto de la oracion se conserva.
- **T8 `03:32` (desplazamiento hacia LLM):** "La literatura reciente sobre clasificacion automatica de tickets no respalda un desplazamiento generalizado del enfoque clasico hacia los LLM generativos: en las comparaciones directas relevadas, los modelos tipo BERT superan a los LLM en una clasificacion de 172 clases en turco \parencite{paket2024itservice} y, ajustados con pocos datos etiquetados, ofrecen un desempeno mas consistente entre conjuntos de datos y con menor costo computacional que los LLM en modo \emph{zero-shot} \parencite{colavito2025benchmarking}."
- **T9 `03:56` (agrupamiento de citas):** primera oracion: "La evaluacion multilingue de LLM ha documentado que su rendimiento depende del idioma, con resultados que favorecen a los idiomas con mas recursos \parencite{ahuja2023mega, xuan2025mmluprox}." Lai et al. y Zhang et al. salen del agrupamiento (siguen citados en T2 con su atribucion correcta). Las oraciones de Grandury, Mayor-Rocher, Bernal-Beltran y Ramon-Ferrer se conservan: coinciden con sus titulos y resumenes.
- **T10 `08:28`:** primera oracion: "Los valores de exactitud y F1 macro obtenidos se contrastan a continuacion con los reportados en la literatura comparable." (retira "resultan consistentes", que contradice "por debajo" de `08:30`); la clausula de Revina se acorta a "...son competitivos frente a alternativas mas complejas." (el argumento sobre preentrenados queda en `08:32`); la oracion de Paramesh sigue D4.
- **T11 `08:32` (Revina):** reemplazar "aquellos autores observan que los modelos preentrenados pueden degradarse ante vocabulario especifico del dominio, lo que descarta suponer" por "aquellos autores excluyen por diseno las representaciones preentrenadas, al considerar que el vocabulario especifico del dominio podria degradarlas, lo que desaconseja suponer".
- **T12 `10:12` (Touvron):** reemplazar la oracion de Touvron por "La disponibilidad de modelos de pesos abiertos, como Llama~2 \parencite{Touvron2023_llama2}, abre una via hacia un sistema completamente autoalojado; sin embargo, en clasificacion de tickets con muchas clases los modelos tipo BERT superaron a LLM abiertos como Llama y Mistral \parencite{paket2024itservice}, por lo que esa via deberia evaluarse con modelos ajustados al dominio y no solo mediante \emph{prompts}." (la frase reescrita lleva "hacia" sin la tilde erronea del original).
- **T13 `01:66` (idiomas de los corpus):** reemplazar la oracion "Buena parte de la literatura relevada ... de mesas de ayuda \parencite{grandury2025laleaderboard,mayorrocher2026spanish}." por "Ninguno de los trabajos de clasificacion automatica de tickets relevados (Tabla~\ref{tab:trabajos-academicos}) declara un corpus en espanol, y las evaluaciones de LLM que incorporan el espanol lo hacen con corpus genericos, no especificos del dominio de mesas de ayuda \parencite{grandury2025laleaderboard,mayorrocher2026spanish}." Zangari y Colavito salen de esta oracion (siguen citados en el capitulo 3). Si c-130 o c-133 agregan a la tabla un trabajo con corpus en espanol, la oracion se ajusta (control de c-136).
- **T14 `08:34` (cobertura del espanol, por tema):** reemplazar "Diversos trabajos han senalado la menor cobertura del espanol en los corpus de entrenamiento de los LLM contemporaneos, y los resultados ... resulta inferior al reportado para idiomas de mayor cobertura como el ingles o el aleman," por "Diversos trabajos han senalado que el ajuste y la evaluacion de los LLM se concentran en el ingles y que su rendimiento cae en los idiomas con menos recursos \parencite{lai2023okapi, xuan2025mmluprox}, y los resultados ... resulta inferior al reportado para el ingles,". La cifra propia (F1 macro entre parentesis) y la atribucion final al esquema multietiqueta no se tocan (propiedad de c-126/c-128); la comparacion con el ingles queda como interpretacion de los autores, ya respaldada por las fuentes citadas en la misma oracion.

**Alternativa considerada:** eliminar las citas observadas en lugar de reescribirlas. Se descarta: el dictamen pide reescribirlas conforme a lo que sostienen, y eliminar Lai et al. o Touvron et al. dejaria entradas sin uso.

### D4 - Cifras de Paramesh y Shreedhara (2019): dos ramas segun la verificabilidad

El capitulo es de acceso cerrado y su resumen no consigna 10.000 tickets, 87 %, TF-IDF ni idioma. Las cifras sostienen cinco sitios, entre ellos el primer criterio de la justificacion del umbral del 85 % (`01:48`).

- **Rama A (texto completo accesible, por ejemplo por acceso institucional de los autores):** se localiza cada elemento (tamano del corpus, idioma, representacion, exactitud) y se agrega la pagina con `\textcite[p.~X]{Paramesh2019_it_service_desk}` en `01:48`, `03:44`, `08:28` y `08:30`; cualquier elemento no localizado se retira aun en esta rama.
- **Rama B (no verificable; opcion por defecto):** se aplica la regla vigente de dato no reportado. `03:44`: "\textcite{Paramesh2019_it_service_desk} & NB, LR, kNN y SVM sobre descripciones de tickets & tickets reales de infraestructura TI; tamano e idioma: no reportado en el alcance revisado & no reportado en el alcance revisado (cualitativo: SVM supera a NB, LR y kNN) & clasificacion clasica supervisada". `08:28`: "\textcite{Paramesh2019_it_service_desk} encuentran que SVM supera a Naive Bayes, regresion logistica y k vecinos mas cercanos sobre tickets reales, sin que el resumen consigne cifras comparables." `08:30`: "se ubican por debajo de los valores reportados en la literatura para clasificacion de tickets, si bien la comparacion directa no es estricta:" pasa a "no admiten una comparacion directa con la literatura revisada:"; "SVM+TF-IDF de \textcite{...} (87~\%)" pasa a "SVM de \textcite{...}"; y "aunque su exactitud estricta resulta menor en la comparacion directa" pasa a "aunque la evidencia disponible no permite ubicar su exactitud respecto de la de esos enfoques". Las cifras propias de `08:30` no se tocan. `01:48`, solo la oracion del primer criterio: "Primero, la literatura de clasificacion de tickets toma como referencia a los clasificadores supervisados clasicos, entre los que SVM obtiene el mejor desempeno \parencite{Paramesh2019_it_service_desk}, aunque los trabajos relevados no permiten fijar un piso numerico comun (Tabla~\ref{tab:trabajos-academicos})." Se informa a c-128 que el primer criterio deja de aportar un ancla numerica.
- **En ambas ramas**, `03:28`: "\textcite{Paramesh2019_it_service_desk} comparan clasificadores supervisados clasicos ---Naive Bayes multinomial, regresion logistica, k vecinos mas cercanos y maquinas de vectores de soporte (SVM)--- sobre tickets reales, no estructurados, de una mesa de servicio de infraestructura de TI, y encuentran que SVM obtiene el mejor desempeno." Se retira "uno de los primeros trabajos exhaustivos en el area", que el resumen no sostiene. La autoria del `.bib` (Paramesh y Shreedhara) se conserva: es la de Crossref; "Paramesh y Ramya" es un error del dictamen y se declara en D15.

**Alternativa considerada:** conservar las cifras con "segun reportan los autores". Se descarta: sin acceso al texto completo no se sabe si el capitulo las reporta, y el requisito vigente de procedencia prohibe atribuir resultados que la fuente no reporte.

### D5 - Entradas nuevas de B15: tipos, campos y claves

Las ocho entradas van en un bloque nuevo, a continuacion de "NORMATIVA Y LEGISLACION", con un encabezado de comentario que declara el change, la fecha de verificacion y la fuente de cada dato. Las claves cumplen `\w+` (requisito del extractor de `verify_citations.py`) y la convencion del archivo. `AAAA-MM-DD` es la fecha real de la verificacion hecha en la aplicacion.

```
@report{ISO27001_2022,
  author      = {{International Organization for Standardization}},
  shortauthor = {ISO},
  title       = {Information security, cybersecurity and privacy protection --- Information security management systems --- Requirements},
  type        = {Norma ISO/IEC},
  number      = {27001:2022},
  year        = {2022},
  url         = {https://www.iso.org/standard/27001},
  urldate     = {AAAA-MM-DD},
}

@report{ISO27002_2022,
  author      = {{International Organization for Standardization}},
  shortauthor = {ISO},
  title       = {Information security, cybersecurity and privacy protection --- Information security controls},
  type        = {Norma ISO/IEC},
  number      = {27002:2022},
  year        = {2022},
  url         = {https://www.iso.org/standard/75652.html},
  urldate     = {AAAA-MM-DD},
}

@report{ISO27701_2025,
  author      = {{International Organization for Standardization}},
  shortauthor = {ISO},
  title       = {Information security, cybersecurity and privacy protection --- Privacy information management systems --- Requirements and guidance},
  type        = {Norma ISO/IEC},
  number      = {27701:2025},
  year        = {2025},
  url         = {https://www.iso.org/standard/27701},
  urldate     = {AAAA-MM-DD},
}

@report{NIST2024_csf,
  author      = {{National Institute of Standards and Technology}},
  shortauthor = {NIST},
  title       = {The {NIST} Cybersecurity Framework ({CSF}) 2.0},
  type        = {NIST Cybersecurity White Paper},
  number      = {29},
  year        = {2024},
  doi         = {10.6028/NIST.CSWP.29},
}

@misc{Decreto1558_2001,
  author  = {{Poder Ejecutivo Nacional}},
  title   = {Decreto 1558/2001: Reglamentaci{\'o}n de la Ley 25.326 de Protecci{\'o}n de los Datos Personales},
  year    = {2001},
  month   = {11},
  day     = {29},
  url     = {http://servicios.infoleg.gob.ar/infolegInternet/anexos/70000-74999/70368/norma.htm},
  urldate = {AAAA-MM-DD},
  note    = {Bolet{\'i}n Oficial de la Rep{\'u}blica Argentina, 3 de diciembre de 2001},
}

@article{Wilcoxon1945_individual_comparisons,
  author  = {Wilcoxon, Frank},
  title   = {Individual Comparisons by Ranking Methods},
  journal = {Biometrics Bulletin},
  volume  = {1},
  number  = {6},
  pages   = {80--83},
  year    = {1945},
  doi     = {10.2307/3001968},
}

@book{Cohen1988_power_analysis,
  author    = {Cohen, Jacob},
  title     = {Statistical Power Analysis for the Behavioral Sciences},
  edition   = {2},
  publisher = {Lawrence Erlbaum Associates},
  year      = {1988},
  isbn      = {0-8058-0283-5},
}

@book{Efron1993_bootstrap,
  author    = {Efron, Bradley and Tibshirani, Robert J.},
  title     = {An Introduction to the Bootstrap},
  publisher = {Chapman \& Hall},
  year      = {1993},
  doi       = {10.1007/978-1-4899-4541-9},
}
```

Criterios: las normas ISO se tipan `@report` con `type` y `number` (forma APA "titulo (Norma ISO/IEC N.o 27001:2022)") y `shortauthor` para que la cita en el texto sea "(International Organization for Standardization [ISO], 2022b)" la primera vez y "(ISO, 2022b)" despues; NIST igual con su DOI y sin `urldate` (un DOI no requiere fecha de consulta); el decreto sigue el patron de `Ley25326_2000`; Wilcoxon se cita en su revista original, *Biometrics Bulletin* (nombre de la revista hasta 1947), no *Biometrics*; Cohen (1988) va sin DOI porque el unico DOI disponible es el de la reedicion de 2013; Efron y Tibshirani usan el DOI del registro de la edicion de 1993. Si el render de `@report` con `shortauthor` no fuera aceptable al compilar, la entrada se reescribe como `@manual` o `@misc` con los mismos datos; ningun dato no verificado entra.

**Alternativas consideradas:** `@standard` (tipo no soportado por los estilos estandar de biblatex, que lo tratan como `@misc`); ISO e IEC como dos autores (cita en el texto mas larga, sin ganancia); el DOI de Routledge para Cohen (fecharia la obra en 2013 o mezclaria fechas).

### D6 - ISO/IEC 27701: se cita la edicion vigente (2025)

La recomendacion B15 nombra "ISO/IEC 27701:2019", pero la ficha oficial la declara retirada el 2025-10-14 y reemplazada por ISO/IEC 27701:2025. El plan de cumplimiento del repositorio se aprobo el 2026-10-01 y no fija edicion. Se cita la edicion 2025 y la frase de `11:40` cambia "la extension de privacidad ISO/IEC~27701" por "la norma de gestion de la privacidad ISO/IEC~27701:2025" (la edicion 2025 dejo de ser una extension de 27001/27002 y paso a ser una norma de sistema de gestion propia). La desviacion respecto de la letra del dictamen se declara en D15.

**Alternativa considerada:** citar la edicion 2019 con la nota "retirada en 2025". Se descarta porque presentaria como marco adoptado en 2026 una norma retirada, contra el criterio de vigencia que el capitulo legal ya aplica a sus fuentes. Queda como pregunta abierta para el usuario (OQ2).

### D7 - Ubicacion de las citas nuevas y precisiones adyacentes

- `11:8`: "en su decreto reglamentario, el Decreto~1558/2001 \parencite{Decreto1558_2001}, y en las disposiciones complementarias...".
- `11:40` (primera mencion de cada marco): `\parencite{ISO27001_2022}`, `\parencite{ISO27002_2022}`, `\parencite{NIST2024_csf}` y `\parencite{ISO27701_2025}` junto a cada norma, con la redaccion de D6. No se cita en titulos de seccion, `\caption` ni lineas de fuente de tabla.
- `04:71`: "...la prueba de Wilcoxon de rangos con signo \parencite{Wilcoxon1945_individual_comparisons}, prueba no parametrica para muestras pareadas..." (`Virtanen2020_scipy` sigue como referencia de implementacion en `07:54`).
- `04:79`: "...con bootstrap percentil a nivel de caso \parencite{Efron1993_bootstrap} (2000 remuestreos, semilla fija)."
- `04:91`: "...se evaluo mediante un analisis de potencia estadistica a priori \parencite{Cohen1988_power_analysis}."
- Precisiones que la cita formal vuelve verificables (detectadas al preparar el change; no figuran en el dictamen): `11:44` dice "los controles del Anexo~A de ISO/IEC~27002:2022", pero en la edicion 2022 los 93 controles estan en los capitulos 5 a 8 de 27002 y el Anexo A de 27002 trata atributos; los controles forman el Anexo A de ISO/IEC 27001:2022. Propuesta: "agrupa por tema los controles de ISO/IEC~27002:2022, que corresponden al Anexo~A de ISO/IEC~27001:2022". `11:68` presenta la madurez "de 0 (inexistente) a 4 (optimizado)", escala que NIST CSF 2.0 no define (el marco usa niveles o *tiers* 1 a 4 de rigor de la gestion del riesgo). Propuesta: "su madurez en una escala propia del relevamiento, de 0 (inexistente) a 4 (optimizado)". Ambas se verifican antes de escribir (indice publico de la norma en la plataforma de consulta de ISO; documento CSWP 29).

Si c-129 reescribio los parrafos de `04:71` y `04:91`, las citas se insertan en la nueva redaccion junto a la primera mencion de la prueba de Wilcoxon, del bootstrap percentil y del analisis de potencia.

### D8 - Criterio uniforme de ano y claves estables

Ano = ano de copyright de la obra (criterio APA 7 para libros), confirmado en la ficha del editor o en un catalogo: Stallings y Brown pasa de 2017 a 2018 y Date de 2003 a 2004; Russell y Norvig **se mantiene en 2021** (el 2020 del dictamen es la fecha de puesta en venta, no el copyright). Para el borrador vivo de Jurafsky y Martin el ano es el de la version consultada (2026). Las citas en el texto se actualizan solas (todas son `\textcite`/`\parencite`); no hay anos escritos a mano junto a esas claves. Las claves no se renombran: no se imprimen, y los escenarios vigentes del spec las nombran (`Stallings2017_computer_security`, `Jurafsky2023_speech_language`, `OGC2011_itil`); un comentario en el `.bib` explica que la clave conserva el ano historico.

**Alternativas consideradas:** seguir la letra del dictamen ano por ano (mezcla dos criterios: copyright para Stallings y Date, fecha de venta para Russell y Norvig); renombrar las claves (churn en `.tex` y conflicto con los escenarios vigentes del spec).

### D9 - Fechas de consulta y notas

- `urldate` en las nueve entradas `@manual`/`@misc` con URL: `Apache2024_airflow`, `n8n2024_docs`, `PostgreSQL2024_docs`, `Tiangolo2024_fastapi`, `Wiggins2017_12factor`, `Ley25326_2000`, `SEPyME2026_mipyme`, `APA2017`, `Gomez2026_repositorio`. Fecha: la de la verificacion de la URL en este change (respuesta 200 o pagina de aterrizaje correcta, y contenido coherente con lo que el texto cita), salvo `SEPyME2026_mipyme` y `APA2017`, cuya nota ya declara la consulta del 2026-10-19: esa fecha pasa a `urldate` y sale de la nota.
- Las cinco `@online` (`DigitalOcean2026_pricing`, `Google2026_vertex_pricing`, `Zendesk2026_help_desk`, `Freshdesk2026_platform`, `ServiceNow2026_itsm`) conservan `urldate = {2026-10-19}` y su nota pierde la fecha ("Precio de lista", "Precios de lista", "Documentacion de la plataforma (capacidades y precios)").
- Ninguna nota usa punto y coma (el estilo lo suprime al imprimir): `APA2017` queda "2002, con enmiendas efectivas del 1 de junio de 2010 y del 1 de enero de 2017"; `SEPyME2026_mipyme`, "Ministerio de Econom{\'i}a de la Naci{\'o}n Argentina"; `mayorrocher2026spanish`, "Advance article, volume/pages pending" (Crossref sigue sin volumen ni paginas).
- Las entradas resueltas por DOI no llevan `urldate`.

### D10 - `OGC2011_itil`: autor Cabinet Office, sin nota contradictoria

Los catalogos discrepan (OGC, AXELOS o TSO segun la biblioteca), pero la propia obra de 2011 se publica por TSO por encargo del Cabinet Office, que absorbio al OGC en 2010, y `02:16` ya lo dice asi. La entrada pasa a `author = {{Cabinet Office}}`, `publisher = {The Stationery Office}`, `year = {2011}`, `isbn = {978-0-11-331307-5}`, sin `note` (la nota vigente atribuye el encargo al OGC y es la contradiccion senalada). La cita en el texto pasa a "(Cabinet Office, 2011)". Se confirma con un catalogo nacional (British Library o WorldCat) o con la ficha de TSO/AXELOS antes de escribir.

**Alternativa considerada:** conservar el autor OGC y corregir solo la nota. Viable si el catalogo consultado da OGC; se descarta como opcion por defecto porque la obra de 2011 ya no es del OGC.

### D11 - Resto de B16 y hallazgos del registro del compilador

- `Paramesh2019_it_service_desk`: `booktitle = {Data Analytics and Learning}`, `booksubtitle = {Proceedings of {DAL} 2018}`, `editor = {Nagabhushan, P. and Guru, D. S. and Shekar, B. H. and Sharath Kumar, Y. H.}`, `series = {Lecture Notes in Networks and Systems}`, `volume = {43}`, `pages = {331--346}`, `publisher = {Springer}`, `doi` sin cambios.
- `Jurafsky2023_speech_language`: `year = {2026}`, `note = {Borrador de la 3.a edici{\'o}n, versi{\'o}n del 19 de agosto de 2026}` (o la version vigente en la fecha de consulta), `url = {https://web.stanford.edu/~jurafsky/slp3/}`, `urldate`; se conserva `publisher = {Stanford University}` y el tipo `@unpublished` (requisito vigente de tipado del borrador); el subtitulo se confirma contra la portada de esa version.
- `liu2025tickit`: `booktitle = {Proceedings of the 33rd ACM International Conference on the Foundations of Software Engineering (FSE Companion '25)}` y `address = {Trondheim, Norway}` (patron de las demas `@inproceedings`).
- Incluidos por pertenecer al mismo apartado del dictamen ("Registro del compilador"), vetables por el usuario (OQ4): `Tiangolo2024_fastapi` pasa a `author = {Ram{\'i}rez, Sebasti{\'a}n}` (nombre del creador de FastAPI, confirmado en su perfil publico); la cita pasa a "(Ramirez, 2024)". `GDPR2016` suma `url = {https://eur-lex.europa.eu/eli/reg/2016/679/oj}` y `urldate`.

### D12 - `verify_citations.py`: funcion pura y prueba co-ubicada (TDD)

Se extrae `count_unique_cited_keys(file_keys: dict[str, set[str]]) -> int`, que devuelve `len(set().union(*file_keys.values()))`. La linea "Total unique citation keys" y el mensaje "<-> N unique citation keys" usan ese valor; la suma por archivo se conserva con un rotulo exacto ("Total key-file appearances"). La prueba `docs/Tesis/v10 (IA)/test_verify_citations.py` se co-ubica con el script (patron de `scripts/dry_run/test_checks.py`) y se escribe con `unittest` para correr con `python -m unittest test_verify_citations -v` desde esa carpeta, porque pytest no esta instalado en los interpretes globales (si el agente dispone de pytest, la misma prueba corre con `python -m pytest`). Casos: claves compartidas entre archivos ({a: {k1, k2}, b: {k1}} -> 2; RED), claves disjuntas ({a: {k1}, b: {k2, k3}} -> 3), diccionario vacio (-> 0) y una prueba de comportamiento que ejecuta `main()` con `SECTIONS_DIR` y `BIB_FILE` apuntando a un directorio temporal (dos `.tex` que comparten una clave y un `.bib` con esas claves), captura la salida y exige "2 bibliography entries <-> 2 unique citation keys" y "Total unique citation keys: 2".

**Alternativa considerada:** solo cambiar el texto del rotulo para que diga "suma por archivo". Se descarta: el mensaje de PASS compara entradas contra claves y solo tiene sentido con el conteo global.

### D13 - Presupuesto de paginas: cuerpo neutral y delta bibliografico medido

Medicion (2026-10-22, `main.pdf` de v1.1.1): 101 paginas; la bibliografia empieza en una pagina nueva (88) y termina en la 93, con unas 10 lineas libres (`pdftotext -lineprinter`: ultima linea de texto en la fila 25 frente a 35 de una pagina llena); la ultima pagina del cuerpo (87) tiene unas 2 lineas libres; los anexos empiezan en pagina nueva.

Estimacion: las ocho entradas suman unas 26 lineas (3 a 3,5 por entrada con su separacion); los metadatos suman unas 3 netas (+1 Paramesh, +1 Jurafsky, +1 RGPD, unas +3 por `urldate`, +0,5 TickIt; -2 por la nota de OGC y unas -2 por las fechas duplicadas). Total del orden de +29 lineas frente a 10 libres: la bibliografia desborda a una septima pagina y el PDF pasa a 102 paginas (+1), salvo compensacion tipografica.

Reglas: (1) **cuerpo neutral**: cada bloque de reescritura se compensa dentro de los mismos parrafos (T1 y T9 y la poda de T10 liberan lineas; T2, T8, T12 y las citas de D7 las consumen); criterio verificable: la pagina en que empieza "Referencias bibliograficas" no cambia respecto de la linea base tomada justo antes de aplicar c-134; (2) **bibliografia**: los recortes propios de B16 (fechas duplicadas, nota de OGC, notas sin punto y coma) se aplican siempre; el delta restante se mide (paginas totales y de la bibliografia, antes y despues) y se entrega a c-136 junto con las palancas disponibles y su rendimiento estimado: reducir `\bibitemsep` (unas 16 lineas sobre 59 entradas, porque la separacion actual ronda 0,3 lineas por entrada), `\renewcommand*{\bibfont}{\small}` (del orden de 0,8 paginas) o retirar las notas descriptivas de las cuatro `@manual` (2 a 4 lineas). c-134 no edita el preambulo.

**Alternativa considerada:** aplicar la palanca tipografica en c-134. Se descarta porque el total de la familia (c-125 a c-135, incluidas las altas de c-133) solo se conoce en la integracion, y una palanca aplicada dos veces o fuera de contexto es dificil de calibrar (OQ5).

### D14 - Orden e interfaces con los changes hermanos

| Sitio | c-134 | Otros changes |
|---|---|---|
| `02:46` | retira Xuan y deja el ancla (D1) | c-125 (frase del gate), c-133 (fuentes de calibracion) |
| `02:38`, `02:44`, `02:48`, `02:50`, `02:52` | atribuciones (D3) | c-132 (tilde erronea de "formula" en `02:44`), c-133 si amplia el eje |
| `03:28`, `03:30`, `03:32`, `03:56` | atribuciones (D3, D4) | c-130 (sintesis y tablas), c-133 (subsecciones nuevas) |
| `03:44` (fila de Paramesh) | celdas de corpus y metrica (D4) | c-130 (metricas de las demas filas, B10) |
| `01:48` (primer criterio del umbral) | clausula de Paramesh (D4) | c-128 (objetivos, umbral y metrica primaria) |
| `01:66` | oracion de idiomas (T13) | - |
| `04:71`, `04:79`, `04:91` | insercion de citas (D7) | c-129 (p unilateral, d_z) |
| `08:28`, `08:30`, `08:32`, `08:34` | clausulas de Paramesh y Revina; cita y "aleman" de `08:34` (T14) | c-126/c-128 (cifras de `08:30` y `08:34`), c-127 si toca la discusion |
| `10:12` | oracion de Touvron (T12) | c-131 (subsecciones nuevas), c-132 |
| `11:8`, `11:40`, `11:44`, `11:68` | citas y precisiones (D6, D7) | c-125/c-126 (salvaguarda de 0,70 en el capitulo legal), c-132 (tilde erronea de "hacia" en `11:8`) |
| `Bibliography_base.bib` | 8 altas y metadatos | c-133 (altas de calibracion y cascadas), c-136 (`Gomez2026_repositorio`) |
| `verify_citations.py` | rotulo y prueba | - |

Orden sugerido: despues de c-125, c-128, c-129 y c-130 (c-134 inserta citas y clausulas sobre su redaccion ya estable); c-133 y c-134 en cualquier orden pero **secuenciales**, nunca en paralelo (ambos editan `02:46` y el `.bib`); antes de c-132 (la ortotipografia barre al final) y de c-136. Independiente de c-135. Las tareas localizan por clave o por fragmento de texto, no por numero de linea, y son idempotentes. Entregas: a c-133, el ancla de D1 y la sugerencia de Zhao et al. (2021); a c-136, el delta de paginas y las palancas (D13), la necesidad de actualizar el `urldate` de `Gomez2026_repositorio` al cambiar su version, el control de anclas `% [c-133]` y el control de T13 si la tabla suma trabajos con corpus en espanol.

### D15 - Trazabilidad en el registro de correcciones

Se agrega en `docs/Tesis/Correcciones/dictamen-correcciones.md` un grupo "Correspondencia texto-fuente y metadatos (c-134, dictamen v1.1.0: A4, B15, B16)" con una tabla por hallazgo (ubicacion, fuente, atribucion previa, lo que la fuente sostiene, evidencia con URL y nivel, correccion aplicada) y una lista de decisiones que se apartan de la letra del dictamen: ISO/IEC 27701:2025 en lugar de 2019 (D6), Russell y Norvig 2021 (D8), autoria Paramesh y Shreedhara (D4), revista *Biometrics Bulletin* (D5), rama aplicada para Paramesh (D4) e inclusion de los hallazgos del registro del compilador (D11).

## Risks / Trade-offs

- **[La rama B de Paramesh deja sin ancla numerica el primer criterio del umbral del 85 %]** -> Mitigacion: se edita solo esa oracion, se informa a c-128 y al usuario (OQ1) y se prefiere la rama A si los autores acceden al texto completo.
- **[Si c-133 no se aplica, la definicion de calibracion queda sin cita]** -> Mitigacion: es preferible a una cita erronea; el ancla de D1 lo hace visible y c-136 lo controla.
- **[El PDF pasa a 102 paginas]** -> Mitigacion: cuerpo neutral por construccion, recortes de B16 y delta medido con palancas cuantificadas para c-136 (D13).
- **[Render de `@report` con `shortauthor` o de `booksubtitle` distinto del esperado en biblatex-apa]** -> Mitigacion: inspeccion visual de las entradas nuevas tras compilar y reescritura a `@manual`/`@misc` con los mismos datos si hace falta.
- **[Bloqueos de bots (ScienceDirect 403, EUR-Lex 202, ISO con agente de navegador)]** -> Mitigacion: fuentes alternativas oficiales (repositorio institucional, ficha del editor, indice publico de ISO) o verificacion manual del usuario; nada se escribe sin evidencia.
- **[Deriva de numeros de linea por los changes previos]** -> Mitigacion: tareas por clave o fragmento de texto y mapa de sitios regenerado al iniciar (tarea 1.2).
- **[Una cita retirada deja una entrada sin uso]** -> Mitigacion: cada clave reescrita sigue citada al menos una vez (Lai y Zhang en T2, Zangari y Colavito en el capitulo 3, Touvron en T12); `verify_citations.py` lo controla.
- **[Las ediciones de lineas compartidas pisan cambios de otros changes]** -> Mitigacion: tabla de propiedad de D14, aplicacion secuencial y diff acotado a las clausulas propias.
- **[Etiquetas 2022a/2022b de las dos normas ISO de 2022 desconciertan al lector]** -> Mitigacion: el texto nombra la norma junto a cada cita (ISO/IEC 27001:2022), de modo que la letra no es la unica pista.

## Migration Plan

1. Registrar el estado de c-125, c-128, c-129, c-130 y c-133 y regenerar el mapa de sitios de cita (`grep`).
2. Tomar la linea base: `verify_citations.py`, compilacion, paginas totales, inicio y fin de la bibliografia y holguras (D13).
3. Aplicar A4 (D1-D4) y registrar la evidencia de cada frase.
4. Verificar y agregar las entradas de B15 (D5) y sus citas (D6, D7).
5. Aplicar B16 (D8-D11).
6. Corregir `verify_citations.py` con el ciclo TDD (D12).
7. Recompilar con el contenedor `texlive-thesis` (ver `paper/Dockerfile`, montando `docs/Tesis/v10 (IA)`), revisar `main.log` y `main.blg`, medir paginas y entregar el delta a c-136.
8. Registrar el grupo de correcciones en `dictamen-correcciones.md` (D15) y las entregas a c-133 y c-136.
9. Rollback: `git checkout <commit-previo>` de los archivos editados, borrar la prueba nueva y recompilar; no hay tags que mover.

## Open Questions

- **OQ1 (Paramesh):** los autores pueden acceder al texto completo del capitulo (por ejemplo, por la Biblioteca Electronica de Ciencia y Tecnologia desde la red UTN) e indicar la pagina de 10.000 tickets, 87 %, TF-IDF e idioma? Si no hay respuesta, se aplica la rama B (D4).
- **OQ2 (ISO/IEC 27701):** se confirma citar la edicion vigente 2025 en lugar de la 2019 retirada que nombra el dictamen (D6)?
- **OQ3 (Russell y Norvig):** se confirma mantener 2021 (ano de copyright, criterio uniforme de D8) en lugar del 2020 del dictamen?
- **OQ4 (alcance adicional):** se confirma incluir los dos hallazgos del registro del compilador (FastAPI, RGPD) y las dos precisiones de `11:44` y `11:68` (D7, D11)?
- **OQ5 (paginas):** se reserva la palanca tipografica para c-136 (opcion por defecto) o se autoriza a c-134 a aplicarla si su propio delta lleva el PDF por encima de 101 paginas?
