# Inventario del uso de asistentes de IA

Documento de respaldo de la declaracion del Anexo I.3 (change c-237). Deriva solo del
repositorio y es regenerable con el comando que se indica. No contiene nombres reales ni
correos de personas: los autores figuran solo como T1, T2 y T3.

## 1. Alcance y ref

- **Ref de conteo:** tag `v1.5.2` (la version evaluada en tercera instancia). El conteo se puede
  re-ejecutar sobre cualquier ref. **Re-ejecucion de c-239 (2026-11-17):** sobre la ref de la
  entrega (commit `3f03597`, previo al commit de contenido de la version `v1.6.0`) el historial
  da **162 de 1199** commits con marca de asistente y el rango `v1.2.18..3f03597` da **49 de 282**
  (unico modelo: Claude Fable 5.2). Es el conteo que el Anexo I.3 declara para la entrega
  `v1.6.0`.
- **Re-ejecucion de la release v1.6.4 (2026-11-24):** sobre la ref de la entrega (commit `76ec960`, previo al commit de contenido de la version `v1.6.4`) el historial da **165 de 1278** commits con marca de asistente. Es el conteo que el Anexo I.3 declara para la entrega `v1.6.4`.
- **Re-ejecucion de la release v1.6.3 (2026-11-22):** sobre la ref de la entrega (commit `87ce685`, previo al commit de contenido de la version `v1.6.3`) el historial da **165 de 1250** commits con marca de asistente (unico modelo: Claude Fable 5.2). Es el conteo que el Anexo I.3 declara para la entrega `v1.6.3`.
- **Re-ejecucion de la release v1.6.2 (2026-11-20):** sobre la ref de la entrega (commit `5847e0d`, previo al commit de contenido de la version `v1.6.2`) el historial da **162 de 1235** commits con marca de asistente (unico modelo: Claude Fable 5.2). Es el conteo que el Anexo I.3 declara para la entrega `v1.6.2`.
- **Re-ejecucion de la release v1.6.1 (2026-11-19):** sobre la ref de la entrega (commit `e2e5504`, previo al commit de contenido de la version `v1.6.1`) el historial da **162 de 1221** commits con marca de asistente y el rango `v1.2.18..e2e5504` da **49 de 304** (unico modelo: Claude Fable 5.2). Es el conteo que el Anexo I.3 declara para la entrega `v1.6.1`; la serie de `v1.5.2` de mas abajo se conserva como historia.
- **Ref del arbol de trabajo al levantar este inventario:** `e52276e` (`v1.5.2-15`), con el
  arbol limpio.
- **Herramienta:** `docs/Tesis/Correcciones/contar_uso_asistentes.py`, con su prueba
  `docs/Tesis/Correcciones/test_contar_uso_asistentes.py` (`unittest`).
- **Naturaleza del conteo:** el numero de commits con marca `Co-Authored-By` de un asistente
  es una **cota inferior** de commits asistidos, no una proporcion de autoria (design D2). La
  marca solo se registra con una de las herramientas; un commit sin marca no prueba la
  ausencia de asistencia. No se traduce a porcentaje de autoria del texto ni del codigo.
- **Privacidad:** el script lee solo `%H` (hash), `%ad` (fecha) y el trailer de co-autoria; no
  lee ni emite `%an` ni `%ae`. El desglose por modelo usa el nombre de pantalla del asistente,
  sin la parte del correo.

## 2. Conteos de commits

Comando exacto (desde la raiz del repositorio):

```
python3 docs/Tesis/Correcciones/contar_uso_asistentes.py \
    --ref v1.5.2 --desde-ref v1.2.18 \
    --archivo-changes openspec/changes/archive
```

Salida sobre la ref `v1.5.2` (reproducida con el script versionado):

| Periodo | Commits | Con marca de asistente (cota inferior) | Sin marca |
|---|---|---|---|
| Historial hasta `v1.5.2` | 1170 | 154 | 1016 |
| Rango `v1.2.18..v1.5.2` | 253 | 41 | 212 |

Desglose por modelo (historial hasta `v1.5.2`):

| Modelo de asistente | Commits |
|---|---|
| Claude Fable 5 | 35 |
| Claude Fable 5.1 | 65 |
| Claude Fable 5.2 | 41 |
| Claude Opus 5.5 | 11 |
| Claude Sonnet 4.6 | 2 |
| **Total** | **154** |

El total con marca coincide con la suma del desglose (154). En el rango `v1.2.18..v1.5.2` el
unico modelo registrado es Claude Fable 5.2 (41 commits).

**Contraste con los anclajes del change.** El rango `v1.2.18..v1.5.2` da 253 / 41, que coincide
con el anclaje del `proposal.md` (41 de 253). El total del historial es 1170 sobre el tag
`v1.5.2`; el `design.md` registra 1173 porque conto sobre un HEAD posterior (`88edd02`, previo
a este apply), no sobre el tag. La diferencia se explica por la ref: el tag `v1.5.2` no incluye
los commits posteriores a la release. El desglose por modelo (35/65/41/11/2) coincide con el
registrado en `design.md`.

Comando alternativo reproducible (equivalente, en una linea) para verificar el rango:

```
git rev-list --count v1.2.18..v1.5.2
git log v1.2.18..v1.5.2 --format='%(trailers:key=Co-Authored-By,valueonly)' | grep -c .
```

## 3. Artefactos de orquestacion de agentes

Existencia verificada con `ls` en la raiz del repositorio:

| Artefacto | Funcion |
|---|---|
| `AGENTS.md` | Reglas duras del proyecto para agentes: arquitectura, comandos, convenciones. |
| `CLAUDE.md` | Referencia legada del proyecto; conserva la tabla de enrutamiento de skills. |
| `CHANGES.md` | Roadmap de changes con dependencias y nivel de gobernanza por change. |
| `.agents/` | Skills de dominio vendorizadas y su registro `SKILLS.md`. |
| `.opencode/` | Skills y comandos de flujo OPSX (explore, propose, apply, archive, sync). |
| `.engram/` | Memoria persistente de los agentes, versionada como evidencia. |
| `openspec/` | 85 specs principales y 226 changes archivados con sus tareas. |
| `knowledge-base/` | 11 archivos canonicos: vision, dominio, arquitectura, flujos. |
| `docs/Tesis/Correcciones/Prompt2.docx` | Perfil de evaluador usado en las autoevaluaciones estilo CONEAU. |

## 4. Mapa de changes archivados por ambito

Conteo de changes archivados cuyo `tasks.md` nombra cada ambito, segun `clasificar_change` del
script (patrones textuales; un mismo change puede nombrar mas de un ambito, por lo que las
filas no son excluyentes):

| Ambito | Changes que lo nombran | Ejemplo verificable |
|---|---|---|
| Codigo del sistema (`App/Backend`, `App/Frontend`) | 112 | `openspec/changes/archive/2026-07-03-c-23-dashboard-analytics-implementation/tasks.md` (`App/Backend/app/schemas/estadisticas.py`) |
| Scripts de analisis y evaluacion (`evaluation/`, `docs/Tesis/Correcciones/`) | 118 | `openspec/changes/archive/2026-06-11-c-08-evaluation-framework/tasks.md` (`evaluation/requirements.txt`) |
| Prosa de la tesis (`.tex`) | 110 | `openspec/changes/archive/2026-11-14-c-222-recalcular-el-balance-neto-con-el-costo-medido/tasks.md`, bloque "Prosa de la tesis" (linea 26); p. ej. `08-discusion.tex` |
| Flujo N8N (`n8n/workflow`) | 37 | `openspec/changes/archive/2026-07-03-c-25-root-cleanup/tasks.md` (`n8n/workflow.json`) |

Nota de reproducibilidad: el conteo de prosa es 110 y no 111 porque el patron exige el limite
de palabra `\.tex\b`; un `grep -E '\.tex'` cuenta de mas al capturar `response.text` en
`2026-09-17-c-30-bugfix-seams/tasks.md`. El numero del inventario es el del script versionado.

## 5. Compuerta de autores (design D5)

**Compuerta resuelta el 2026-11-16.** Las respuestas de T1, T2 y T3 a las preguntas OQ1-OQ6
estan registradas en 5.2, por alias y con fecha. Solo entonces se escribio la declaracion del
Anexo I.3 en el `.tex`. Ninguna pregunta se respondio por inferencia del agente.

### 5.1 Cuestionario a los autores (OQ1-OQ6)

- **OQ1 — Herramientas fuera del repositorio.** Cada autor (T1, T2, T3): que asistentes de IA uso
  que el repositorio no registra (asistentes de chat, autocompletado en el editor, opencode con
  que modelos, herramientas de diagramas, traductores)? Para que ambito (a)-(e) y en que periodo?
  Con que herramienta y modelo se generaron las autoevaluaciones con `Prompt2.docx` y los
  diagramas de flujo?
- **OQ2 — Verificacion de cifras y afirmaciones.** Cada autor: como verifico las cifras que el
  asistente escribio en la tesis (recalculo desde los artefactos versionados, comparacion con el
  memo de numeros canonicos, ejecucion de los scripts, muestreo)? Como verifico las afirmaciones
  no numericas y las citas (lectura de la fuente, `verify_citations.py`)? Reviso cada diff antes
  de aceptarlo o por muestreo? Hubo partes aceptadas sin revision linea por linea?
- **OQ3 — Distribucion del trabajo en esta version (pregunta 12 del tribunal).** Como se
  repartieron entre T1, T2 y T3 el codigo, el analisis, la redaccion y la verificacion entre
  `v1.2.18` y `v1.5.2`? A que autor corresponde cada una de las 4 identidades de commit del rango
  (respuesta solo para el inventario, sin publicar correos)? Quien opero las sesiones de agente?
- **OQ4 — Normativa aplicable.** Existe una norma de la facultad (UTN-FRM) o de la UTN sobre uso
  de IA en trabajos finales? Consultarlo con los directores; si existe, citarla con su numero y
  fecha; si no existe, la declaracion lo dice asi y remite a la indicacion del tribunal.
- **OQ5 — Lo hecho sin asistencia.** Que partes confirman los autores como realizadas sin
  asistente (diseno metodologico, recoleccion y etiquetado de datos, mediciones de tiempo,
  decisiones de contenido, otras)?
- **OQ6 — Ubicacion.** Aceptan la subseccion nueva I.3 (design D4) o prefieren reescribir en el
  lugar dentro de I.2?

### 5.2 Registro de respuestas

Las respuestas de los tres autores (T1, T2 y T3) se recibieron y registraron el 2026-11-16. Se
transcriben consolidadas, por pregunta, sin nombres ni correos. El mapeo entre cada alias y su
identidad real se conserva fuera del repositorio y no se publica.

| Autor | Fecha | Respuesta |
|---|---|---|
| T1 | 2026-11-16 | OQ1-OQ6 |
| T2 | 2026-11-16 | OQ1-OQ6 |
| T3 | 2026-11-16 | OQ1-OQ6 |

- **OQ1 (herramientas).** Se declaran solo las herramientas con evidencia en el repositorio:
  Claude Code, con los modelos registrados en los trailers de los commits (Claude Fable 5,
  Claude Fable 5.1, Claude Fable 5.2, Claude Opus 5.5 y Claude Sonnet 4.6); opencode
  (`.opencode/`); y los artefactos de orquestacion de agentes (`AGENTS.md`, `CLAUDE.md`,
  `.agents/`, `.engram/`, `openspec/`), junto con el perfil de evaluador
  `docs/Tesis/Correcciones/Prompt2.docx` para las autoevaluaciones estilo CONEAU. No se
  declaran herramientas sin evidencia en el repositorio. Los diagramas se produjeron con un
  modelo de lenguaje, sin individualizar el modelo, a partir de la estructura planteada por los
  autores: fuentes Mermaid `.md` en `docs/diagrams/` renderizadas a PNG.
- **OQ2 (verificacion).** Los autores confirman que ninguna parte se acepto sin revision previa.
  Mecanismos: las suites de pruebas del backend y de `evaluation/`; `verify_citations.py`;
  `verificar_matriz_trazabilidad.py`; el memo `docs/Tesis/Correcciones/numeros-canonicos.md`;
  `resumir_registro_compilacion.py`; `sent_c197.py` y `list_long_c197.py`;
  `recontar_errores_frontera.py`; y la revision de cada change antes de archivarlo.
- **OQ3 (distribucion del trabajo).** T1, T2 y T3 son los tres autores de la tesis. El mapeo
  entre cada alias y su identidad se conserva fuera del repositorio; no se publica ni en este
  inventario ni en el texto de la declaracion.
- **OQ4 (normativa).** No existe una norma escrita de la facultad (UTN-FRM) sobre el uso de
  asistentes de IA en trabajos finales. El uso quedo autorizado por el director de la carrera en
  una reunion virtual del 7 de mayo de 2026; no se nombra al director.
- **OQ5 (sin asistencia).** El diseno metodologico; la recoleccion de datos, que comprende las
  mediciones de tiempo y el etiquetado de los datos; y las decisiones de contenido.
- **OQ6 (ubicacion).** Se aprueba la subseccion nueva I.3, tras I.2, con la etiqueta
  `subsec:declaracion-uso-ia`; se retira el parrafo de la declaracion vigente de I.2 y se
  conserva el parrafo de I.2 sobre las revisiones.

### 5.3 Borrador aprobado (design D7)

El borrador D7 quedo resuelto con las respuestas de 5.2 y aprobado por los tres autores el
2026-11-16. El texto aprobado es la seccion 6 de este inventario; es el que se traslada al
Anexo I.3 del `.tex` y el que c-239 usara para actualizar Q16.

## 6. Texto fuente de la declaracion (para el `.tex` y Q16)

Texto aprobado por los autores el 2026-11-16 (respuestas de la seccion 5). Es el que se traslada
al Anexo I.3 del `.tex` con ortografia acentuada y el que c-239 usara para actualizar Q16 de
`docs/defensa/respuestas-tribunal.md`. No quedan huecos por confirmar: cada procedimiento de
verificacion consta como confirmado en la seccion 5 (OQ2) y los conteos provienen de la ref
`v1.5.2` y se presentan como cota inferior (seccion 1).

### 6.1 Apertura

El desarrollo del sistema, los scripts de analisis y evaluacion y la redaccion de esta tesis se
realizaron con asistencia sistematica de agentes de codigo basados en modelos de lenguaje. El
trabajo se organizo en changes con especificacion previa (propuesta, diseno y tareas) que los
autores definian y revisaban; el agente implementaba las tareas y los autores aceptaban o
rechazaban el resultado. El inventario versionado
`docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` reproduce los conteos: en la ref de la entrega (el commit previo al commit de contenido de
la version `v1.6.2`), 162 de 1235 commits llevan la marca de co-autoria de un asistente, cifra
que es una cota inferior porque la marca solo se registra con una de las herramientas en uso.

### 6.2 Ambitos

| Ambito | Herramienta y modelo | Que produjo el asistente | Verificacion de los autores |
|---|---|---|---|
| Codigo del sistema (backend, frontend y flujo N8N) | Claude Code y opencode; modelos registrados en los trailers del repositorio: Claude Fable 5, 5.1 y 5.2, Claude Opus 5.5 y Claude Sonnet 4.6 | Implementacion de rutas, servicios, repositorios y componentes de interfaz, y del flujo N8N, a partir de tareas especificadas y revisadas por los autores | Suite de pruebas del backend (`pytest`); revision de cada change antes de archivarlo |
| Scripts de analisis y evaluacion | Idem | Scripts de analisis y evaluacion, y el recalculo de las cifras que citan | Suite de pruebas de `evaluation/` (`pytest`); recalculo de las cifras desde los artefactos versionados y su registro en el memo `docs/Tesis/Correcciones/numeros-canonicos.md`; `recontar_errores_frontera.py`, `sent_c197.py` y `list_long_c197.py` |
| Texto de la tesis | Idem | Borradores de prosa a partir de tareas especificadas por los autores (redaccion, ademas de correccion de estilo y edicion) | `verify_citations.py`; `verificar_matriz_trazabilidad.py`; `resumir_registro_compilacion.py`; contraste con el memo de numeros canonicos; revision de cada change antes de archivarlo |
| Diagramas | Un modelo de lenguaje, sin individualizar el modelo; fuentes Mermaid versionadas en `docs/diagrams/` | Diagramas de flujo y de arquitectura a partir de la estructura planteada por los autores, en fuentes Mermaid `.md` renderizadas a PNG | Revision de cada change antes de archivarlo; las fuentes Mermaid se versionan como texto y se revisan como diferencias |
| Autoevaluaciones estilo CONEAU | Asistente de lenguaje con el perfil de evaluador `docs/Tesis/Correcciones/Prompt2.docx` | Informes de autoevaluacion frente a criterios de la CONEAU; no son una revision por pares | Revision de los autores |

### 6.3 Cierre

El diseno metodologico, la recoleccion de datos (que comprende las mediciones de tiempo y el
etiquetado de los datos) y las decisiones de contenido son de los autores, que asumen la
responsabilidad final de cada cifra y cada afirmacion. El uso de asistentes de inteligencia
artificial fue autorizado por el director de la carrera en una reunion virtual del 7 de mayo de
2026; no existe una norma escrita de la facultad (UTN-FRM) sobre su uso en trabajos finales.
