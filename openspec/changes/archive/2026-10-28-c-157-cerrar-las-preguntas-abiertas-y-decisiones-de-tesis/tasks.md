## 1. Verificacion previa de estado

- [x] 1.1 Re-verificar contra `docs/Tesis/v10 (IA)/paper/sections/05-arquitectura.tex:74` que la tesis vigente declara `SQLAlchemy 2.0` con `asyncpg` (y que `grep -rn "psycopg" docs/Tesis/**` no devuelve coincidencias), antes de marcar IN-03; confirmar que el resultado coincide con el design D2.
- [x] 1.2 Re-verificar contra `n8n/workflow.json` el disparador IMAP (`Mesa de Ayuda - IMAP`), el conteo de nodos (32 totales: 29 operativos mas 3 sticky notes) y la ausencia de nodos Redis, agente de IA, LangChain u OpenAI, antes de reescribir IN-06; confirmar que el resultado coincide con el design D3.
- [x] 1.3 Re-verificar que `openspec/config.yaml:34` declara `timeout_s: 30` y `total_timeout_s: 60`, y que `CLAUDE.md` remite a `openspec/config.yaml` (`stack.inference`) sin repetir el valor de 10 s, antes de cerrar O8.
- [x] 1.4 Re-verificar que `docs/Tesis/v10 (IA)/paper/sections/06-implementacion.tex:8` y `10-recomendaciones.tex:6` presentan la migracion a Kubernetes como trabajo futuro, antes de cerrar SU-05; confirmar el encuadre del design D3.

## 2. Cerrar las entradas de la base de conocimiento

- [x] 2.1 En `knowledge-base/10_preguntas_abiertas.md` marcar IN-03 como RESUELTA, con la evidencia de que la Seccion 5.4 de la tesis declara `asyncpg` con `SQLAlchemy 2.0` y de que DD-08 lo confirma; preservar el texto de la resolucion propuesta original como antecedente rotulado. Verificar que la entrada no presenta `psycopg2` como driver vigente de la tesis.
- [x] 2.2 En `knowledge-base/10_preguntas_abiertas.md` reescribir IN-06 a la arquitectura vigente del workflow (IMAP, clasificacion embebida en el backend, sin agente LangChain ni Redis en telefonia) y marcar la divergencia como reconciliada, conservando el texto original rotulado como antecedente superado. Verificar que la entrada no describe Outlook, AI Agent ni Redis como componentes vigentes.
- [x] 2.3 En `knowledge-base/10_preguntas_abiertas.md` marcar la pregunta de Kubernetes (SU-05) como RESUELTA con el estado aspiracional/fuera de alcance; verificar que la tabla de preguntas abiertas ya no la lista como pendiente y que la declaracion coincide con `knowledge-base/08_arquitectura_propuesta.md:75` y `knowledge-base/09_decisiones_y_supuestos.md:61`.
- [x] 2.4 Confirmar por inspeccion que las correcciones 2.1-2.3 no borran las afirmaciones de estado originales cuando aportan contexto historico, sino que las reencuadran con una anotacion (conforme al requisito de no reescritura).

## 3. Cerrar la observacion O8 en el ledger del dictamen

- [x] 3.1 En `docs/Tesis/Correcciones/dictamen-correcciones.md` actualizar el campo Estado de la fila O8 de la tabla de observaciones al estado RESUELTA y agregar una nota fechada bajo la seccion "Notas" que cite la evidencia (`openspec/config.yaml` con `timeout_s: 30` y `total_timeout_s: 60`; `CLAUDE.md` remitiendo a esa seccion), conservando el texto original de la observacion. Verificar que la observacion O8 ya no figura como pendiente "fuera de la tesis" sin anotacion de cierre.
- [x] 3.2 Verificar que la anotacion no introduce emojis ni pictogramas y que respeta el formato de las notas de trazabilidad ya presentes en el mismo archivo.

## 4. Completar el capitulo de recomendaciones y la nota del Anexo C

- [x] 4.1 En `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex` agregar la subseccion "Integracion con sistemas externos de inventario de activos y gestion de configuracion" con etiqueta `subsec:integracion-inventario` y un parrafo academico neutral; verificar que usa la forma `\subsection{...}\label{...}` de las subsecciones vecinas y que no introduce cifras nuevas.
- [x] 4.2 En `docs/Tesis/v10 (IA)/paper/sections/10-recomendaciones.tex` agregar la subseccion "Automatizacion de la etapa de resolucion tecnica" con etiqueta `subsec:automatizacion-resolucion` y un parrafo academico neutral; verificar que su etiqueta es unica en el documento.
- [x] 4.3 Verificar que las cuatro lineas de trabajo futuro enumeradas en `01-introduccion.tex:74` tienen ahora subseccion correspondiente en `10-recomendaciones.tex` (clasificador supervisado, panel de monitoreo, inventario/CMDB, automatizacion de la resolucion tecnica).
- [x] 4.4 En `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`, en la seccion del esquema de base de datos (Anexo C), agregar una nota factica que declare `SQLAlchemy 2.0` con `asyncpg` como capa de acceso a datos; verificar que la nota es consistente con la Seccion 5.4 y que no afirma que la tesis vigente declara `psycopg2`.
- [x] 4.5 Confirmar por inspeccion que el encuadre de la migracion a Kubernetes en `10-recomendaciones.tex:6` y en `06-implementacion.tex:8` sigue siendo de trabajo futuro/aspiracional y que ninguna linea afirma un despliegue vigente en Kubernetes.

## 5. Release diferida

- [x] 5.1 Registrar en el ledger del dictamen (o en la nota de release correspondiente) que la recompilacion del PDF (`docs/Tesis/v10 (IA)/paper/main.pdf`) por las ediciones de los `.tex` queda diferida a una release posterior a `v1.2.4`, sin ejecutarla en este change.

## 6. Verificacion final

- [x] 6.1 Ejecutar `python3 scripts/preflight/docs_stack_sync.py` y verificar que termina con codigo 0 (sin nuevos hallazgos respecto de la linea base).
- [x] 6.2 Ejecutar `python3 -m pytest scripts/preflight -q` y verificar que la suite sigue en verde.
- [x] 6.3 Ejecutar `openspec validate "c-157-cerrar-las-preguntas-abiertas-y-decisiones-de-tesis" --strict --no-interactive` y verificar que el change valida sin errores.
- [x] 6.4 Revisar `git diff` de los cuatro archivos tocados y verificar que no hay emojis, que el texto esta en espanol tecnico neutral, y que no se modificaron los cinco identificadores canonicos de sector, los valores de `gemini-3.6-flash`, `requirements.txt`, `openspec/config.yaml` ni codigo de `App/`.
- [x] 6.5 Confirmar por inspeccion que el arbol `docs/Tesis/v9 (IA)` no fue modificado y dejar constancia de la Open Question del design (si debe recibir el mismo contenido), para resolucion con el autor.
