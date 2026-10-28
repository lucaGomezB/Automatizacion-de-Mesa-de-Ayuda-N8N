## Context

Ver `proposal.md - Why`. Cuatro artefactos documentales se corrigen y dos `.tex` de la version de trabajo (`v10 (IA)`) reciben contenido. La verificacion previa contra los archivos reales, hecha el 2026-10-28, arroja los siguientes hechos que moldean el enfoque:

1. **IN-03 (driver).** La premisa de la entrada ("la tesis dice psycopg2") esta STALE: `docs/Tesis/v10 (IA)/paper/sections/05-arquitectura.tex:74` ya declara "SQLAlchemy~2.0 como mapeador objeto-relacional (ORM) y asyncpg como driver asincronico". Un barrido de `psycopg` sobre `docs/Tesis/**` no encuentra ninguna referencia; las unicas menciones vivas estan en documentacion de proyecto (`knowledge-base/02_descripcion_general.md`, `knowledge-base/09_decisiones_y_supuestos.md` DD-08 y `docs/por_implementar.md:120`), que ya lo describen como decision. DD-08 cierra con "La tesis ha sido actualizada para reflejar esta eleccion".
2. **IN-06 (workflow).** `n8n/workflow.json` tiene 32 nodos (29 operativos + 3 sticky notes), un nodo `n8n-nodes-base.emailReadImap` llamado `Mesa de Ayuda - IMAP`, y ningun nodo de Redis, agente de IA, LangChain ni OpenAI. La entrada vigente describe "16 nodos operativos + 3 sticky", "Microsoft Outlook (NO IMAP)" y "AI Agent (LangChain) + Redis": las tres afirmaciones estan superadas (C-55 redefinio el correo a IMAP/App Password; C-72 retiro el agente telefonico, Redis y el bucle de refinamiento).
3. **SU-05 (Kubernetes).** La tesis ya lo presenta como futuro: `06-implementacion.tex:8` ("la migracion a un cluster Kubernetes~1.30 ... se plantea como trabajo futuro y no cuenta con manifiestos") y `10-recomendaciones.tex:6` la lista entre las evoluciones anticipadas. `knowledge-base/08_arquitectura_propuesta.md:75` y `knowledge-base/09_decisiones_y_supuestos.md:61` (SU-05) ya lo declaran aspiracional. No hay que alinear la tesis; solo cerrar la pregunta.
4. **O8 (timeout).** El ledger (`docs/Tesis/Correcciones/dictamen-correcciones.md:2735`) registra O8 como "cerrada en la tesis ...; pendiente fuera de la tesis". La evidencia muestra que el residual ya no existe: `openspec/config.yaml:34` declara `timeout_s: 30, total_timeout_s: 60` y `CLAUDE.md:50` remite a `openspec/config.yaml` (`stack.inference`) sin repetir un valor de 10 s.
5. **B1 (recomendaciones).** `01-introduccion.tex:74` enumera cuatro lineas fuera de alcance. Del capitulo `10-recomendaciones.tex`, dos tienen subseccion (clasificador supervisado, `subsec:clasificador-supervisado`; panel de monitoreo, `subsec:panel-monitoreo`) y dos no (inventario/CMDB; automatizacion de la resolucion tecnica).
6. **v9 frente a v10.** Ambos directorios (`v9 (IA)` y `v10 (IA)`) contienen los archivos de seccion, pero difieren de forma sustancial: `v9` cita el tag `v1.0.1`, hash `bac4c5f6...`, timeout de 10 s y no incluye el cronograma ni el Anexo I de trazabilidad. `v10` es la version de trabajo vigente: `tesis-document` la fija como fuente (`docs/Tesis/v10 (IA)/paper/main.tex`) y `build_tesis_para_agente.py` genera el render desde ahi.

## Goals / Non-Goals

**Goals:**
- Cerrar IN-03, IN-06 y SU-05 en la base de conocimiento con evidencia verificable y preservando el texto previo como antecedente rotulado.
- Cerrar O8 en el ledger del dictamen con una anotacion fechada y su evidencia.
- Completar la remision interna del capitulo de recomendaciones con las dos subsecciones faltantes.
- Dejar constancia de la reconciliacion del driver en el Anexo C de la tesis.

**Non-Goals:**
- No recompilar el PDF ni etiquetar una release; la recompilacion queda diferida a una release posterior a `v1.2.4`.
- No modificar el codigo de aplicacion, los cinco identificadores canonicos de sector, los valores de `gemini-3.6-flash`, `requirements.txt` ni `openspec/config.yaml`.
- No ampliar el alcance de `scripts/preflight/docs_stack_sync.py`.
- No reescribir registros historicos: la correccion de estado se expresa como actualizacion del marco de estado mas anotacion, no como borrado del hecho previo.
- No editar el arbol de verificacion `docs/Tesis/v9 (IA)` (ver D1).

## Decisions

### D1. Se edita `v10 (IA)`; `v9 (IA)` no se toca

`v10 (IA)` es la version de trabajo vigente: es la que `tesis-document` declara como fuente y la que alimenta el render `tesis_para_agente.md`. `v9 (IA)` es un arbol previo congelado (`tag v1.0.1`, hash `bac4c5f6...`, timeout de 10 s, sin cronograma ni Anexo I), no un gemelo identico de `v10`. Editar un arbol congelado que reproduce una entrega previa contradice la regla de no reescribir registros historicos y no tiene efecto sobre el documento vivo.

Alternativas consideradas: (a) editar ambos arboles — RECHAZADA, falsifica un arbol congelado y no aporta al documento vigente; (b) editar solo el `.tex` de `v9` — RECHAZADA, no toca la version de trabajo. Se deja registrado como verificacion explicita en las tareas, por si el autor confirma que `v9` debe recibir el mismo contenido.

### D2. IN-03 se cierra sin fabricar una divergencia inexistente

La resolucion propuesta original ("anotar la divergencia en el Anexo B/C") presuponia que la tesis aun declara `psycopg2`. Como `05-arquitectura.tex:74` ya declara `asyncpg` con `SQLAlchemy 2.0`, la accion se ajusta a la realidad: la entrada IN-03 se marca RESUELTA con la evidencia (Seccion 5.4 mas DD-08), y el Anexo C recibe una nota factica que declara el driver implementado, consistente con la Seccion 5.4. La nota NO afirma una divergencia "tesis vs codigo", porque esa divergencia ya no existe.

Alternativas consideradas: (a) escribir la nota literal "la tesis dice psycopg2 y el codigo asyncpg" — RECHAZADA, afirmaria un hecho falso sobre el documento vigente; (b) no tocar la tesis y solo cerrar la entrada de la KB — DESCARTADA como unica medida, porque el autor pidio dejar la reconciliacion asentada en el Anexo; se conserva como refuerzo documental factico.

### D3. IN-06 se reescribe con los valores del artefacto

Los conteos y componentes se toman de `n8n/workflow.json`, no de la memoria del change: 32 nodos totales (29 operativos + 3 sticky), disparador `Mesa de Ayuda - IMAP`, clasificacion embebida en `POST /api/v1/incidentes`, sin Redis ni agente de IA. El texto original de la entrada se conserva rotulado como antecedente superado.

### D4. B1: dos subsecciones nuevas, con el patron y las etiquetas de las vecinas

Las dos subsecciones se agregan a `10-recomendaciones.tex` con la forma `\subsection{...}\label{...}` de las existentes. Etiquetas propuestas: `subsec:integracion-inventario` (integracion con sistemas externos de inventario de activos y gestion de configuracion) y `subsec:automatizacion-resolucion` (automatizacion de la etapa de resolucion tecnica). El contenido es un parrafo academico neutral cada una, sin cifras nuevas, apoyado en el encuadre ya existente: la primera conecta con la base de conocimientos y el autoservicio; la segunda explicita que la resolucion tecnica trasciende el alcance de esta investigacion. Se coloca la subseccion de inventario junto a las extensiones funcionales y la de resolucion tecnica cerca de la base de conocimientos, para no romper la agrupacion por prioridad del capitulo.

### D5. O8: anotacion fechada en el ledger, sin tocar la matriz de criterios

Se agrega una nota fechada bajo "## Notas" (patron de las notas de trazabilidad ya presentes) y se actualiza el campo Estado de la fila O8 al estado resuelto con su evidencia. No se reescribe el texto original de la observacion; el cierre se expresa como anotacion.

### D6. Recompilacion diferida

Las ediciones de `10-recomendaciones.tex` y `12-anexos.tex` dejan la fuente y el PDF (`main.pdf`) desalineados. La recompilacion (XeLaTeX + biber, en el entorno de registro) y la verificacion asociada quedan registradas como trabajo de una release posterior a `v1.2.4`, fuera del alcance de aplicacion de este change.

## Risks / Trade-offs

- [Reescribir un registro historico (violacion de la regla dura)] -> Toda correccion de estado se expresa como actualizacion del marco de estado mas anotacion; los hechos previos de IN-03, IN-06 y O8 se conservan rotulados. Verificacion por inspeccion del diff.
- [Afirmar una divergencia inexistente en el Anexo C] -> La nota se limita a declarar el driver implementado, sin afirmar un desfase "tesis vs codigo". Se verifica que `psycopg2` no aparezca como valor vigente.
- [Desalinear la fuente `.tex` del PDF] -> Mitigado registrando la recompilacion como tarea de release posterior; no se etiqueta ninguna release desde este change.
- [Introducir una cifra o afirmacion no respaldada en las subsecciones nuevas] -> El texto de las subsecciones no aporta cifras; se restringe a encuadre cualitativo remitiendo a las secciones existentes.
- [Efecto colateral en la barrera de sincronia documental] -> La barrera barre `knowledge-base/**` y el material de referencia para valores de stack; los cambios de IN-03/IN-06/SU-05 no introducen valores de stack retirados como vigentes. Se ejecuta el preflight para confirmar codigo 0.

## Migration Plan

1. Actualizar el marco de estado y las anotaciones en `knowledge-base/10_preguntas_abiertas.md` (IN-03, IN-06, SU-05).
2. Cerrar O8 en `docs/Tesis/Correcciones/dictamen-correcciones.md`.
3. Agregar la nota del driver en `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` y las dos subsecciones en `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex`.
4. Verificar con `python3 scripts/preflight/docs_stack_sync.py`, `python3 -m pytest scripts/preflight -q` y `openspec validate ... --strict`.

Rollback: revertir los cuatro archivos modificados con `git checkout --`; ninguno tiene efecto en runtime.

## Open Questions

- Confirmar con el autor si el arbol `docs/Tesis/v9 (IA)` debe recibir tambien las dos subsecciones y la nota del driver, o si se mantiene congelado. Es diferible: no cambia las specs, el enfoque ni el desglose de tareas, que por defecto solo tocan `v10 (IA)`.
