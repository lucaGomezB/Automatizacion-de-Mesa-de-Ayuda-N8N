# Proposal: Atender el dictamen CONEAU sobre v1.2.16 (consentimiento, segunda sub-hipotesis, Anexo I y residuales)

## Why

El dictamen CONEAU del 2026-11-09 sobre la release `v1.2.16`
(`auditorias/Dictamen_Tesis_v10_v1.2.16_CONEAU_2026-11-09.md`, noveno de la serie) califica el
documento escrito con 9,21 y lo aprueba con observaciones. La de mayor peso es etica: la seccion
7.5 afirma que los cuatro participantes de la campana complementaria "firmaron una confirmacion
escrita" y que "el repositorio conserva ... el registro de que se recabo", pero el registro esta
vacio y los autores confirmaron que las firmas todavia no se recabaron. Las otras dos
observaciones de fondo son la frase "Medirla en condiciones validas" que sigue en 8.3 (y la
asimetria de la regla de tres vias, no declarada donde se define) y el Anexo I, que dejo de trazar
el ultimo dictamen (dice "siete" y traza cuatro). Se suman un MDE impreso (0,276) que el analisis
versionado no produce (0,2834) y residuales de propagacion, forma y bibliografia. El patron comun,
segun el dictamen, son declaraciones que se adelantan a su respaldo: este change hace que el texto
diga solo lo que el repositorio muestra, o que el repositorio pase a mostrar lo que el texto dice.
La release `v1.2.17` cierra el dictamen.

## What Changes

- **A1 - Consentimiento veraz (7.5): DIFERIDA A LOS AUTORES.** El co-autor Luca Gomez reescribira
  7.5 cuando los cuatro participantes hayan firmado, con las fechas reales; c-195 no edita 7.5
  (`11-aspectos-legales.tex`), la plantilla `docs/campana-medicion/confirmacion-posterior-consentimiento.md`
  ni el README de la campana. El registro y el Anexo I consignan A1 y los items 1 y 2 como
  "PENDIENTE (diferida: la atienden los autores al recabar las firmas)".
- **A2 - Lectura unica de la segunda sub-hipotesis**: 8.3 reemplaza "Medirla en condiciones
  validas ..." por una condicion de generalizacion (formulario web y reportantes identificados);
  1.4 y 4.7 declaran, al definir la regla de tres vias, que es asimetrica ("refutada" = la
  estimacion puntual alcanza la cota, no un rechazo estadistico de p <= 0,15); 8.3 y 9.1 dicen que
  el intervalo no permite descartar una proporcion INFERIOR a la cota.
- **A3 - Anexo I**: la serie pasa a nueve dictamenes; se agregan dos tablas de trazabilidad
  compactas, la del dictamen del 9-11 sobre `v1.2.13` (c-192, c-193, c-194) y la del dictamen
  sobre `v1.2.16` (c-195). `dictamen-correcciones.md` gana matrices de 7 columnas verificables
  para c-192 a c-195, y `verificar_matriz_trazabilidad.py` pasa a fallar cuando una seccion de
  dictamen desde c-190 no tiene matriz (Strict TDD).
- **B1 - MDE del Spearman alineado con el analisis versionado**: constante de la eficiencia de
  Spearman (9/pi^2) en `evaluation/stats.py`, usada solo en el MDE del Spearman de
  `evaluation/campana.py`; regeneracion de `analisis/resultados.json`, `resultados.md` y
  `SHA256SUMS.txt` con el comando del proyecto, con diff que pruebe que solo cambia el MDE del
  Spearman (0,2834 -> 0,276). Si no se cumple, se revierte y 8.7 declara la discrepancia.
- **B2 - Propagacion pendiente**: 6.3 nombra el webhook `telefonia-handoff` y "tres
  disparadores de canal"; 4.2 consigna que el observador de `A1` fue el autor `T1`; 8.7 declara
  que las dos caches del 7-10 contienen las mismas 200 predicciones; `numeros-canonicos.md`
  actualiza el estado de la sub-hipotesis, la interseccion del laxo y la fila del MDE.
- **B3 - Zanzotto (2.4)**: la atribucion se limita a lo que el resumen sostiene (retribuir a
  quienes aportan el conocimiento); se retira "y sostener la supervision humana".
- **C1/C2 - Forma**: "; Los autores" -> "; los autores"; VIS-005 presentado como requisito de
  la especificacion de visibilidad de incidentes (c-82); el capitulo 11 dice que la campana
  refuto la sub-hipotesis; 11.3 agrega el requisito de dimensionar la muestra; la entrada de
  Zendesk pierde "Suite"; la URL de ServiceNow se reintenta y se registra su estado.
- **Release `v1.2.17`**: patron de hash de c-188/c-192 (oracion de reemplazo en el commit de
  contenido, tag anotado, commit posterior con el hash); referencias de la version entregada a
  `v1.2.17`; registro c-195, FASE 60 en `CHANGES.md`, `compilacion.md` y `tesis_para_agente.md`
  regenerados. El crecimiento de paginas por las dos tablas del Anexo I se acepta y se registra.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- `tesis-document`: se modifican los requisitos del estado de la segunda sub-hipotesis, del MDE
  del Spearman, de la fidelidad bibliografica del 9-11 (Zanzotto y Zendesk), dla linea futura de 11.3, de la trazabilidad
  del dictamen sobre v1.2.13 y del verificador de la matriz; se reemplaza el requisito del canal
  telefonico por "callback de grabacion" y los dos requisitos de la release v1.2.16; se agregan
  requisitos para la asimetria de la regla de tres vias, la propagacion del dictamen sobre
  v1.2.16, la forma residual, la trazabilidad del dictamen sobre v1.2.16, la release v1.2.17 y
  el libro mayor de paginas de c-195.

## Impact

- Tesis: `docs/Tesis/v10 (IA)/paper/sections/{01-introduccion,02-marco-teorico,04-marco-metodologico,05-arquitectura,06-implementacion,07-resultados,08-discusion,10-recomendaciones,11-aspectos-legales,12-anexos}.tex`
  y `docs/Tesis/v10 (IA)/Bibliography_base.bib`; `paper/compilacion.md`, `paper/main.pdf` y
  `tesis_para_agente.md` regenerados.
- Etica y campana: sin cambios en este change (A1 diferida a los autores).
- Codigo de evaluacion: `evaluation/stats.py` (constante nueva), `evaluation/campana.py`
  (MDE del Spearman), `evaluation/tests/test_stats.py`, `evaluation/tests/test_campana.py`;
  salidas regeneradas `evaluation/data/campana/analisis/{resultados.json,resultados.md,SHA256SUMS.txt}`.
- Registro: `docs/Tesis/Correcciones/{dictamen-correcciones,numeros-canonicos}.md`,
  `verificar_matriz_trazabilidad.py` y su prueba; `CHANGES.md` (FASE 60).
- Fuera de alcance: `App/`, `n8n/`, `docker/`; el change `c-191` (activo, de otro autor); nuevas
  mediciones de campo; la mencion de c-191 en 11.8 (el dictamen la condiciona a que se ejecute
  antes de la defensa); la reduccion al tope de 100 paginas.
- Gobernanza: texto de la tesis MEDIUM; consentimiento (HIGH) fuera de este change; codigo de evaluacion MEDIUM (Strict TDD).
