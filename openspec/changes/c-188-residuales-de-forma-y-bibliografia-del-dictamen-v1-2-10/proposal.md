# Proposal: Residuales de forma y bibliografia del dictamen CONEAU sobre v1.2.10 (B4, B5, B7, C1-C5)

## Why

El dictamen CONEAU del 2026-11-08 sobre la release `v1.2.10`
(`auditorias/Dictamen_Tesis_v10_v1.2.10_CONEAU_2026-11-08.md`) emitio cinco observaciones
de fondo (A1-A5), siete de consistencia (B1-B7) y cinco de bibliografia y forma (C1-C5).
El change c-187 (release `v1.2.11`, PR #72) cerro A1-A5, B1, B2, B3 y B6 y remitio el
resto a un change posterior: la tesis sigue describiendo las metricas multietiqueta
secundarias sin la definicion que permite reproducirlas, muestra capturas de interfaz
con una "tasa de revision humana" del 64,8 % sin explicar su procedencia, rotula el
frontend del despliegue como "Vite dev server", repite la matriz de confusion como
tabla y como figura, no versiona evidencia de su compilacion, conserva un verificador de
trazabilidad que falla en 22 de 41 filas, y arrastra reparos de fidelidad, pertinencia y
forma bibliografica y un glosario desalineado con el cuerpo. Son las observaciones que un
jurado detecta con el repositorio al lado; ninguna exige mediciones nuevas
(inventario del dictamen, items 27 a 36).

## What Changes

- **B4 — Metricas multietiqueta y ejemplos del prompt** (4.6 y 8.2): declarar que subset
  accuracy (0,43), Hamming loss (0,3586) y micro-F1 (0,6654) toman como conjunto predicho
  la etiqueta principal mas los sectores adicionales que el clasificador emite en 8 casos
  (todos de la etapa deterministica) y que la Hamming loss se normaliza por la union de
  etiquetas del caso, no por las cinco clases (verificado contra
  `evaluation/run_evaluation.py` y `evaluation/metrics.py`); reemplazar "salida forzada a
  una sola etiqueta" por una descripcion exacta. Unificar "ejemplos representativos
  balanceados" (5.5 y 9.5) con "un unico ejemplo representativo por sector" (Anexo H).
- **B5 — Figuras** (6.8, 5.x, 8.2): declarar en las leyendas la procedencia de
  `panel_admin.png` y `dashboard.png` (instancia local de desarrollo capturada el
  21-10-2026 por c-80, rotulo "v1.0.0", 145 incidentes del 2 y del 13-10, 94 en
  revision = 64,8 %) y que el indicador de revision mostrado es el registrado por el
  backend en esa base, no la regla de confianza evaluada fuera de linea (opcion
  recomendada; reemplazar las capturas queda como alternativa, **decision del usuario**);
  corregir `docs/diagrams/despliegue.md` (frontend: bundle Vite servido por
  `nginx:alpine` en el puerto 3000; imagen derivada de N8N de c-182; redes de
  `docker-compose.yml`) y regenerar `figures/despliegue.png`; **retirar la Figura 7**
  (`fig:matriz_confusion`) y conservar la Tabla 11 (`tab:matriz`), lo que ademas libera
  espacio para las adiciones de este change.
- **B7 — Trazabilidad de la compilacion y del registro**: versionar junto al PDF un
  resumen del registro de compilacion (`paper/compilacion.md`) generado por un script
  nuevo con pruebas (`resumir_registro_compilacion.py`) a partir de `main.log`,
  `main.blg` y `main.pdf`; `main.log` sigue ignorado. Actualizar
  `verificar_matriz_trazabilidad.py` bajo TDD para que verifique todas las matrices con
  "Fragmento verificable" del registro (FASE 36, 28-10 y la nueva del 8-11), localice por
  fragmento y no por numero de linea, y omita las filas "superadas"; dejar el registro
  sin fallas.
- **C1 — Fidelidad bibliografica**: reformular como inferencia propia la afirmacion
  atribuida a Galup et al. (2009) en 1.2 y 2.1 (salvo que se verifique la pagina) y la
  "atencion notablemente menor" del rioplatense en 3 (item 32); precisar la definicion del
  F1 macro (media aritmetica de los F1 por clase, la que implementa
  `evaluation/metrics.py`) frente a Sokolova y Lapalme (2009) y citar Opitz y Burst
  (arXiv:1911.03347) para esa variante; citar una fuente primaria verificada del efecto
  Hawthorne en 4.2.
- **C2 — Pertinencia bibliografica**: agregar entradas verificadas (URL real y fecha de
  consulta) de la Gemini API (terminos y documentacion de Google AI, que es el servicio
  que usa el backend con clave de API, incluida la transcripcion de voz), Twilio
  Programmable Voice (grabacion), Docker, Jira Service Management y osTicket (hoy solo URL
  al pie de la Tabla 2) y la normativa argentina complementaria del art. 12 de la
  Ley 25.326 (reglamentacion y disposicion de la autoridad de aplicacion sobre paises
  adecuados y clausulas modelo). Ninguna fuente se inventa: la que no se verifique no se
  agrega.
- **C3 — Terminologia y Tabla 1**: "pseudonimizacion" por "disociacion" en 9.7 al
  referirse a la Ley 25.326; Zangari et al.: retirar "texto inaccesible" (acceso abierto)
  y declarar el idioma si el texto lo informa o "idioma no reportado"; Ramya et al.:
  "de dos de los tres autores"; fecha de la Ley 25.326 coherente (sancion 4-10-2000).
- **C4 — Forma de la lista de referencias**: actas EMNLP con el anio en todas; actas de
  PMLR impresas como *Proceedings of Machine Learning Research* con su volumen;
  mayuscula tras los dos puntos en Mosqueira-Rey; "3.ª" en Jurafsky; URL en Brown,
  Vaswani, Radford, Pedregosa y Powers; "Publicacion anticipada en linea" en Mayor-Rocher;
  apellido "Gomez"/"Gómez" consistente entre portada y `Gomez2026_repositorio`
  (**decision del usuario**).
- **C5 — Glosario**: agregar CONEAU, NLBSE, PABAK, RGPD, UTC y GPT; retirar UML, FRM y UTN
  (sin uso en el cuerpo; FRM y UTN solo aparecen en un comentario de la portada).
- **Item 36**: `docs/diagrams/cronograma.md` (tabla de procedencia) fecha las tablas
  primarias de la campaña complementaria hasta el 2026-11-08 (`intervenciones.csv`); la
  figura no cambia (la barra tiene precision de mes).
- **Registro y Anexo I**: seccion de c-188 en `dictamen-correcciones.md` y filas B4, B5,
  B7 y C1-C5 en `tab:anexo-trazabilidad-0811` en lugar de la fila de remision.
- **Release**: recompilacion, tag `v1.2.12`, commit del hash, `CHANGES.md`, engram sync y
  PR (tareas finales del orquestador).

## Dependencia y ejecucion

c-188 depende de c-187: el apply corre en una rama nueva cortada desde `main` **despues**
de que se fusione el PR #72 (`v1.2.11`). Las anclas de linea del dictamen estan numeradas
sobre el tag `v1.2.10` y c-187 reescribio varios de esos parrafos: en el apply cada ancla
se relocaliza por el texto citado, nunca por el numero.

## Out of Scope

- A1-A5, B1, B2, B3 y B6 (cerradas por c-187).
- Nuevas mediciones, corridas del clasificador o cambios de valores canonicos: las cifras
  multietiqueta se conservan; solo se declara su definicion.
- Cambios de codigo en `App/`, `n8n/` o `evaluation/`. El unico codigo de c-188 son los dos
  scripts de `docs/Tesis/Correcciones/` (uno nuevo y uno actualizado) con sus pruebas.
- Busquedas nuevas en repositorios regionales (SciELO, Redalyc, JAIIO) del estado del arte:
  el dictamen las sugiere sin formularlas como recomendacion.
- Volver a capturar el flujo N8N u otras figuras no observadas.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: se modifican tres requisitos (compilacion de la tesis, con el resumen
  versionado del registro; evidencia visual, con siete figuras y la matriz de confusion
  solo como tabla; trazabilidad del dictamen del 8 de noviembre en el Anexo I, sin la fila
  de remision) y se agregan requisitos para la definicion de las metricas multietiqueta,
  la descripcion unica de los ejemplos del prompt, la procedencia de las capturas, el
  diagrama de despliegue, el verificador de la matriz de trazabilidad, la fidelidad y la
  pertinencia bibliograficas, la terminologia legal y la Tabla 1, la forma de la lista de
  referencias, el glosario, la fecha del cronograma y la neutralidad de paginas. La
  evidencia de compilacion es parte del requisito existente "Thesis PDF compilation"; no
  se crea una capacidad nueva.

## Impact

- `docs/Tesis/v10 (IA)/paper/sections/{00-glosario,00-portada,01-introduccion,02-marco-teorico,03-estado-del-arte,04-marco-metodologico,05-arquitectura,06-implementacion,07-resultados,08-discusion,11-aspectos-legales,12-anexos}.tex`;
  `docs/Tesis/v10 (IA)/Bibliography_base.bib`; `docs/diagrams/{despliegue,cronograma}.md`;
  `paper/figures/despliegue.png`; `paper/compilacion.md` (nuevo, versionado).
- `docs/Tesis/Correcciones/{verificar_matriz_trazabilidad,test_verificar_matriz_trazabilidad}.py`
  (actualizados), `resumir_registro_compilacion.py` y su prueba (nuevos);
  `dictamen-correcciones.md`, `conteos-canonicos-tecnicos.md`; `CHANGES.md` en el release.
- Gobernanza: LOW (documentacion, figuras, bibliografia). Los dos scripts son codigo bajo
  prueba (Strict TDD). Tope de paginas: el PDF del commit etiquetado no supera 118 paginas
  (el de `v1.2.11`); resumen y abstract no se tocan (237/237 palabras, tope 250).
