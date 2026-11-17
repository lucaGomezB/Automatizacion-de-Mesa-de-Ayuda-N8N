# Proposal: Declarar de forma completa el uso de asistentes de IA

## Why

La **devolucion de tercera instancia** del tribunal (16/11/2026, nota 6,7/10; `auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md`) registra la observacion **A-03**: "La declaracion de uso de IA es mas acotada que lo que registra el repositorio" (Anexo I.2). La declaracion vigente (`docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex:241`) limita la asistencia a "la correccion de estilo y la edicion del texto" y a "la generacion de diagramas de flujo", sin nombrar herramienta, modelo, alcance sobre el codigo o el analisis, ni procedimiento de verificacion. El repositorio, en cambio, registra guias para agentes de codigo (`AGENTS.md`, `CLAUDE.md`), un roadmap de cambios que "un agente puede implementar en una sesion" (`CHANGES.md`), skills y memoria de agentes (`.agents/`, `.opencode/`, `.engram/`), el flujo `openspec/` (85 specs, 226 changes archivados) cuyas tareas encargan al agente codigo, scripts de analisis y prosa de la tesis (ejemplo citado por el tribunal: bloque "Prosa de la tesis" de c-222), y **154 de 1.173 commits** con trailer `Co-Authored-By` de un asistente (41 de los 253 entre `v1.2.18` y `v1.5.2`).

El tribunal aclara que "el uso de estas herramientas no es en si una falta"; exige que la declaracion sea **completa** (seccion 7, punto 5) e indique que partes del codigo, de los scripts de analisis y del texto produjo un asistente, con que herramientas y como verificaron los autores cada cifra y cada afirmacion, ajustada a la normativa de la facultad. Las preguntas 11 y 12 de la seccion 8 piden lo mismo para la defensa y la distribucion del trabajo entre los tres autores. Es una correccion obligatoria para el ejemplar que se lleve al acto.

## What Changes

| Bloque | Que cambia | Gobernanza |
|---|---|---|
| **A. Inventario reproducible** | Documento de respaldo `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` derivado solo del repositorio: conteos de commits con y sin trailer de asistente por periodo (rango de tags) y por modelo, con el comando exacto; lista de artefactos de orquestacion de agentes; mapa de changes archivados por ambito (codigo, analisis, prosa, flujo N8N). Script minimo `contar_uso_asistentes.py` con su prueba `test_contar_uso_asistentes.py` (Strict TDD), sin datos personales en la salida. | BAJA (utilidad de solo lectura) |
| **B. Compuerta de autores** | Cuestionario a T1, T2 y T3 (herramientas fuera del repositorio, verificacion efectiva de cifras y afirmaciones, distribucion del trabajo, normativa aplicable). Sus respuestas se registran en el inventario. **Nada de la declaracion se escribe en el `.tex` sin esa confirmacion.** | ALTA (declaracion de autoria) |
| **C. Declaracion nueva** | Se reemplaza el parrafo de `12-anexos.tex:241` por una subseccion nueva **I.3** (`subsec:declaracion-uso-ia`) con la declaracion por ambitos: (a) codigo del sistema, (b) scripts de analisis y evaluacion, (c) texto de la tesis, (d) diagramas, (e) autoevaluaciones estilo CONEAU; para cada uno: herramienta/modelo, que produjo y el procedimiento de verificacion que los autores confirmen. Una pagina como maximo, sin registro de bitacora. Queda ademas el texto fuente para que c-239 actualice la respuesta Q16. | ALTA |

No se modifica ninguna cifra de resultado, ningun numero canonico, ni `App/`, `n8n/`, `evaluation/`, el corpus o los artefactos congelados.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: se AGREGAN dos requisitos: (i) la declaracion completa del uso de asistentes de IA en el Anexo I, por ambitos, con herramienta, alcance y verificacion confirmados por los autores; (ii) el inventario reproducible del uso de asistentes que respalda esa declaracion. No existe hoy un requisito sobre la declaracion de asistencia de IA (se verifico en `openspec/specs/tesis-document/spec.md`), por lo que ambos son ADDED.

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` | Modificado | Se retira el parrafo de L241 (Anexo I.2) y se agrega la subseccion I.3 tras I.2 |
| `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md` | Nuevo | Inventario reproducible, respuestas de los autores y texto fuente para Q16 |
| `docs/Tesis/Correcciones/contar_uso_asistentes.py`, `test_contar_uso_asistentes.py` | Nuevo | Conteo reproducible de trailers y clasificacion de changes por ambito |

Fuera de alcance: respuestas al tribunal y Q16 (`docs/defensa/respuestas-tribunal.md`, c-239), matriz de trazabilidad, bump, recompilacion de cierre y tag (c-239), nota de versiones I.1 (c-235), formato general de anexos (c-238), `CHANGES.md` y `.engram/`.

## Risks

| Riesgo | Prob. | Mitigacion |
|---|---|---|
| Subdeclarar (repetir el "solo estilo") | Media | La declaracion debe ser coherente con el inventario; cada ambito con evidencia en el repo SHALL figurar |
| Sobredeclarar o inventar procedimientos de verificacion | Media | Solo se redacta lo que los autores confirman; lo no confirmado queda fuera y se declara la omision |
| Leer el trailer como medida exacta | Alta | El conteo se presenta como **cota inferior** de commits asistidos, no como proporcion de autoria |
| Exponer nombres o correos de autores | Baja | El script no emite identidades; solo alias T1..T3 en el texto |
| Colision en `12-anexos.tex` con c-235 (I.1) y c-238 (formato) | Media | Subsecciones distintas; se repuntan lineas al aplicar el segundo |
| Sin respuesta de los autores a tiempo | Media | La compuerta bloquea solo el `.tex`; el inventario y el borrador quedan listos |

## Rollback Plan

`git revert` del commit de contenido: el inventario y el script son archivos nuevos; la edicion del `.tex` es una sustitucion textual acotada. No hay cifras canonicas, tag ni bump que deshacer.

## Dependencies

- Ninguna dependencia dura. Coordinacion textual con **c-235** (misma seccion del anexo, subseccion I.1) y **c-238** (formato de anexos). **c-239** consume el texto fuente para Q16, re-ejecuta el conteo en la ref de la release y recompila.

## Success Criteria

- [ ] El inventario reproduce, con un comando versionado, los conteos de commits con y sin trailer por periodo y por modelo, y lista artefactos de orquestacion y el mapa de changes por ambito.
- [ ] Los autores confirmaron por escrito (alias, fecha) herramientas, verificacion, distribucion del trabajo y normativa; lo no confirmado no figura como hecho.
- [ ] El Anexo I contiene una declaracion por ambitos (a)-(e) con herramienta/modelo, que produjo y verificacion, de una pagina como maximo, y el parrafo viejo ya no figura.
- [ ] `test_contar_uso_asistentes.py` pasa; `openspec validate c-237-declarar-de-forma-completa-el-uso-de-asistentes-de-ia --strict` pasa.
