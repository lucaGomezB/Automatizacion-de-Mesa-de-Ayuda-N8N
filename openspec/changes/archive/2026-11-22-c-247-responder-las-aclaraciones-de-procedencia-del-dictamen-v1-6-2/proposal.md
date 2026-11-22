# Proposal: Responder las aclaraciones de procedencia del dictamen sobre v1.6.2

## Why

El dictamen CONEAU del 2026-11-20 sobre `v1.6.2`
(`auditorias/Dictamen_Tesis_v10_v1.6.2_CONEAU_2026-11-20.md`) dicta **APROBADA CON
OBSERVACIONES, condicionada a tres aclaraciones previas a la defensa**: quien reporto los 119
incidentes del regimen (a) y por lo tanto quien es titular de esos datos; que escucharon y donde
cargaron `A1` y `T1` los 200 casos del flujo manual; y una sola cronologia del consentimiento,
coincidente entre la tesis y el acta que cita. Suma una cuarta condicion de release (el PDF del
arbol del tag `v1.6.2` imprime el hash `17aa6d21` del candidato previo y no `e7013127`) y
quince recomendaciones de prosa. Calificacion sugerida 7,88 (8); proyectada 8,33 con las
recomendaciones necesarias 0 a 6. El reencuadre de c-246 quedo aplicado en el nucleo y no en sus
consecuencias (Resumen, Abstract, limitaciones, conclusiones, trabajos futuros), y la formula
hibrida "entorno operativo del propio equipo, presentado como escenario de referencia narrativo"
evita decidir, pasaje por pasaje, que ocurrio y que se supuso.

## What Changes

- **A. Aclaraciones de procedencia (bloqueadas por compuertas de autores).** Cada una es un
  hecho que solo los autores conocen; el agente MUST NOT inventarlo.
  - **OQ-01 (titulares del regimen (a) y base de la composicion):** quien reporto los 119
    incidentes; si los originales con PII eran datos de terceros; en que lugares de trabajo; que
    la composicion 119/81 es una declaracion de los autores sin registro por caso (o su retiro);
    como se corrige la descripcion "200 casos reales" / "clasificacion manual" del metadato del
    corpus. Afecta §4.4, §7.2, §7.5, `01-introduccion.tex:72` y `data/`.
  - **OQ-02 (flujo manual):** lugar y sistema de carga; que escucharon `A1` y `T1` en los 81
    casos telefonicos en junio-agosto, cuando el audio se grabo el 5 y 6-10-2026; experiencia
    real de `A1` y `T1`; definicion unica de `tiempo_manual_s`; destino de las "planillas de
    cronometraje" que el Anexo F dice incluir; "septiembre a octubre" frente a la evidencia
    fechada solo en octubre.
  - **OQ-03 (cronologia del consentimiento):** que ocurrio el 1-10 y el 2-10 (informacion,
    consentimiento o notificacion); actualizacion del acta T2 (redactada 2026-11-17, firmada
    2026-11-20); nota de revision del acta T1 por la edicion del 2026-11-18 (`b01da04d`);
    consentimiento escrito de `A1`; lista completa de transferencias en §7.3; comprobantes de
    facturacion versionados frente a `11-aspectos-legales.tex:24`.
  - **OQ-04 (politica de release, autores y director):** si un tag puede contener un PDF y como
    evita la proxima release el patron de dos commits; `compilacion.md` debe nombrar el commit
    compilado. Este change NO mueve ni borra el tag `v1.6.2`; deja la instruccion al change de
    release.
- **B. Recomendaciones necesarias 1 a 6 (sin compuerta):** Resumen y Abstract reencuadrados
  (balance como ahorro neto por incidente de unos 25,5 s-persona, el trimestre como proyeccion,
  "viabilidad economica" acotada, "inconclusive" alineado); separacion del entorno real y del
  escenario ficticio en los pasajes del Anexo B del dictamen; mediciones no comparadas con
  premisas (`01:18`, `07:37`, fila de la Tabla de procedencia `04:78`); coautoria de los datos
  propagada a §9.3, §10, tabla de cumplimiento, Anexo F y Nota de versiones; "corpus real" en
  `07:99` y `09:37`; residuos de R-01; `N = 2.646` rotulado como supuesto en `08:80`, `08:109` y
  `12:321`.
- **C. Consistencia (recomendaciones 7 a 11 y 15):** nota de facturacion `07:371`; "siete
  apartados" `07:6`; oracion huerfana de TF-IDF `02:54`; hipotesis subsidiarias `01:38`;
  `09:47` y `09:49`; fichas de Paket (`03:49`) y Paramesh (`03:30`, copia arXiv 2103.15822);
  atribucion de `03:34`; "Novena ... superada" `08:46`/`08:64`; 0,864 como cota inferior
  `04:123`; §11.7 (`10:14`, `10:34`); §8.8 con el origen del criterio T = 4 y las dos corridas
  completas; nueve respuestas al tribunal y `docs/defensa/respuestas-tribunal.md:129`.
- **D. Forma (recomendaciones 12 a 14):** portada, §1.9 con el Anexo K, remisiones al memo,
  fragmento de `07:8`, repeticion de `07:343`, cinco oraciones de mas de 60 palabras, cuatro
  tablas sin cita, once figuras y dos tablas sin fuente, flotantes de los Anexos A y J,
  glosario y "Recharts", cuatro entradas bibliograficas incompletas, editorial de Ramon Ferrer,
  fecha de la Decision 2003/490/CE, aviso de la Tabla 25 que ahora es la 26.

**BREAKING (afirmaciones de procedencia):** segun las respuestas OQ-01 a OQ-03, el documento
puede dejar de afirmar que los titulares del regimen (a) son los autores, que "el corpus no
proviene de una organizacion real", que el flujo manual incluyo escuchar llamadas y que el
consentimiento se presto el 2-10-2026.

Fuera de alcance: recompilacion, bump y tag (pertenecen a un change de release, como c-243 y
c-245); cifras canonicas, citas y conclusiones sin ratificacion de autores; `App/`, `n8n/`,
`evaluation/`; los casos del corpus.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tesis-reencuadre-cuarta-instancia`: se AGREGAN requisitos que llevan el reencuadre a sus
  consecuencias (procedencia y titularidad del regimen (a), base de la composicion, flujo manual
  con lugar, sistema y escucha, cronologia unica del consentimiento, Resumen y Abstract, entorno
  real separado del escenario, coautoria propagada, residuos de R-01, consistencia, forma,
  respuestas al tribunal y registro de compuertas).
- `tesis-document`: se AGREGA el requisito de la instruccion de release ante el PDF del tag que
  imprime un hash ajeno (OQ-04), compatible con "Publicacion de una release de correccion sin
  mover tags publicados".

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `docs/Tesis/v10 (IA)/paper/sections/00-resumen.tex`, `00-portada.tex`, `00-glosario.tex` | Modificado | Resumen, Abstract, fecha de portada, glosario |
| `.../sections/01-introduccion.tex`, `02-marco-teorico.tex`, `03-estado-del-arte.tex` | Modificado | Entorno real vs escenario, hipotesis, umbral, TF-IDF, fichas |
| `.../sections/04-marco-metodologico.tex` | Modificado | OQ-01, OQ-02, residuos de R-01, 0,864, oraciones largas |
| `.../sections/06-implementacion.tex`, `07-resultados.tex` | Modificado | Recharts, facturacion, 61,6 s, sonda, fuentes |
| `.../sections/05-arquitectura.tex` | Modificado | Lineas "Fuente" de `fig:despliegue` y `fig:er_modelo_datos` (tarea 6.6) |
| `.../sections/08-discusion.tex`, `09-conclusiones.tex`, `10-recomendaciones.tex` | Modificado | Limitaciones, balance, aportes, §11.7 |
| `.../sections/11-aspectos-legales.tex` | Modificado (HIGH, gated) | OQ-01 y OQ-03 |
| `.../sections/12-anexos.tex`, `Bibliography_base.bib` | Modificado | Anexo F, Nota de versiones, Anexo J, bibliografia |
| `docs/seguridad/acta-consentimiento-t1.md`, `acta-consentimiento-t2.md` | Modificado (HIGH, gated OQ-03) | Fechas y nota de revision |
| `data/README.md` (y, solo si los autores lo eligen, el metadato del JSON) | Modificado (gated OQ-01) | Descripcion del corpus |
| `docs/Tesis/Correcciones/respuestas-tribunal-cuarta-instancia.md`, `docs/defensa/respuestas-tribunal.md` | Modificado | Nueve respuestas y Q15 |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Seccion c-247: compuertas, ANTES/DESPUES, instruccion OQ-04 |
| `.gitignore`, `docs/Tesis/fuentes/README.md` | Nuevo | Carpeta para PDFs de terceros (copyright), ignorada salvo el README (verificacion de la tarea 5.4) |
