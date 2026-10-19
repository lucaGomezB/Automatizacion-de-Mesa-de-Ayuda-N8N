## Context

Ver `proposal.md` — Why. El change corrige texto de dos archivos de seccion:
`docs/Tesis/v9 (IA)/paper/sections/05-arquitectura.tex` y
`06-implementacion.tex`. Ademas cubre M-NUEVO: la coherencia del nombre del
modelo en el resto del cuerpo (`00`, `05`, `06`, `08`, `09`, `10`, `11`, `12`).
No se toca `App/**`.

Restricciones que moldean el enfoque:

- Los dos `.tex` son **compartidos** con changes activos: c-77 (C3 sobre Tabla 4 y
  §5.3; C1-C8 de coherencia tecnica) y c-80 (figuras/capturas y la nota de N8N
  1.62 en `05-arquitectura.tex:21` y `06-implementacion.tex:10`). El orden de
  aplicacion debe ser c-76 -> c-77 -> c-80 -> c-94.
- La fuente de verdad de los puntos de entrada REST es `docs/openapi.json`
  (33 rutas). La de cualquier cifra conservada es
  `data/corpus_evaluacion_pseudonimizado.json` y `evaluation/report.md`.
- La fuente de verdad del identificador del modelo de inferencia (M-NUEVO) es
  `App/Backend/app/config/settings.py:78` (`gemini_model: str =
  "gemini-3.6-flash"`), consistente con `App/Backend/.env.example:13`,
  `README.md:315` y `docs/anexo_h_prompt_gemini.md`. c-76 ya alineo §1.6 de
  `01-introduccion.tex` y el Anexo H (tareas 9.2 y 5.3); ambas fuentes
  coinciden, no hay discrepancia que resolver.
- El repositorio **evoluciono** desde el commit de la auditoria
  (`d7df92c`, 2026-07-02). Medicion en HEAD (2026-10-19): 136 archivos
  `test_*.py` en `App/Backend/tests/`; 56 archivos de prueba de frontend con 340
  ocurrencias `it(`; `App/Frontend/coverage` existe pero esta **gitignored** (no
  versionado). Las cifras del dictamen (22 suites de backend, 68 casos de
  frontend) corresponden al estado auditado, no a HEAD.

## Goals / Non-Goals

**Goals:**

- Alinear cada afirmacion de los Caps. 5-6 con lo que el repositorio permite
  verificar: retraer lo no atribuible, reformular lo no reproducible y publicar
  la evidencia cuando exista.
- Producir un recuento y una cobertura de la suite de frontend reproducibles en
  HEAD, o publicar el informe como evidencia versionada.
- Completar la Tabla 5 con los grupos de puntos de entrada reales y declarar su
  no exhaustividad.
- Alinear el nombre del modelo en los ocho archivos de seccion afectados al
  identificador real `gemini-3.6-flash` (M-NUEVO), sin re-editar §1.6 ni el
  Anexo H.
- No colisionar con c-76, c-77, c-80: referenciar sus alcances y no duplicarlos.

**Non-Goals:**

- No se implementa ninguna prueba e2e de N8N (el alcance es solo documental).
- No se agregan capturas ni figuras (owner: c-80).
- No se re-derivan los numeros de resultados (owner: c-76).
- No se re-edita §1.6 de `01-introduccion.tex` ni
  `docs/anexo_h_prompt_gemini.md`: c-76 ya los alineo (tareas 9.2 y 5.3).
- No se reescribe la coherencia tecnica C1-C8 ni el residuo de C-18 (owner:
  c-77).
- No se edita `App/**` ni `CHANGES.md` ni
  `docs/Tesis/Correcciones/dictamen-correcciones.md`.

## Decisions

### D1 — Politica por hallazgo: retraer vs. reformular vs. completar

| Hallazgo | Accion | Justificacion |
|---|---|---|
| A-11 | **Reformular** | Existen pruebas estructurales del workflow y de API/base de datos; se describe lo que hay y se retira la afirmacion de e2e que instancia N8N |
| A-12 | **Re-medir y corregir** (o publicar informe) | La cifra no se reproduce; se re-mide en HEAD y se publica el valor real, o se versiona el informe de cobertura |
| A-13 | **Retraer o reformular con evidencia** | Las observaciones no son atribuibles (C-17); sin `n`/dispersion/procedimiento no hay medicion |
| M-08 | **Reformular** | El ejemplo es hipotetico; se marca como tal |
| M-09 | **Retraer o acotar a futuro** | No hay manifiesto de Kubernetes |
| M-12 | **Reformular** | Se retira «optimizados» o se documenta el procedimiento |
| M-13 | **Completar** | La tabla es incompleta, no incorrecta |
| M-NUEVO | **Alinear** | El identificador real es `gemini-3.6-flash`; el cuerpo conserva «Gemini 2.5 Flash» en ocho archivos. Se sustituye sin tocar §1.6 ni el Anexo H (c-76) |

Alternativa considerada: retraer todas las afirmaciones no verificables. Se
descarta porque destruye contenido verificable (las pruebas estructurales y de
API existen) y empobrece el capitulo.

### D2 — Re-medir contra HEAD, no contra el commit auditado

El recuento de la suite de frontend y la existencia de pruebas e2e se verifican
en HEAD con comandos reproducibles (`rg`, `find`), no contra las cifras del
dictamen. Motivo: el repositorio crecio desde `d7df92c`; hardcodear 68 u 89
introduciria una cifra nueva no reproducible. La tesis cita el valor medido y el
comando que lo produce.

Alternativa considerada: citar la cifra del dictamen (68). Se descarta: no
describe HEAD y repetiria el defecto que el hallazgo senala.

### D3 — Orden de aplicacion y edicion acotada por linea

c-94 se aplica despues de c-76, c-77 y c-80. Cada edicion se acota a las lineas
del hallazgo para minimizar el solapamiento con c-77 (Tabla 4, §5.3) y c-80
(figuras, nota N8N 1.62). Las lineas compartidas se referencian, no se reescriben.

### D4 — Tabla 5 agrupada por recurso, con nota de no exhaustividad

La Tabla 5 se completa agrupando por recurso (auth, incidentes, clasificaciones,
estadisticas, salud) a partir de `docs/openapi.json`, y se agrega una nota de que
no es exhaustiva con remision al Anexo D/OpenAPI. No se vuelca el archivo
completo (115 KB); c-80 Anexo D ya incluye el contrato.

### D5 — Residuo de C-18: referenciar, no duplicar

La alineacion textual de Tabla 4 (`id_canal` -> `canal_origen_id`) y §5.3 (dos
llamadas -> un `POST`) permanece en c-77 C3. c-94 solo agrega una tarea de
verificacion que confirma que c-77 la cubre y que no hay dos ediciones sobre las
mismas lineas.

### D6 — Verificacion sin toolchain local

No hay compilador LaTeX local; la recompilacion se hace en Overleaf (XeLaTeX).
La verificacion textual se hace con `rg` sobre `docs/Tesis/v9 (IA)/paper/sections`
(los `.bak` no se editan ni se cuentan) y el change con
`openspec validate c-94-tesis-implementacion-verificabilidad --strict`.

### D7 — Alinear el cuerpo al identificador real del modelo (`gemini-3.6-flash`)

El cuerpo de la tesis se alinea al identificador que el codigo y la configuracion
desplegados usan realmente: `gemini-3.6-flash`. Fuente de verdad primaria:
`App/Backend/app/config/settings.py:78` (`gemini_model: str = "gemini-3.6-flash"`),
corroborada por `App/Backend/.env.example:13`, `README.md:315` y
`docs/anexo_h_prompt_gemini.md`. Las cuatro fuentes coinciden; no hay
discrepancia que obligue a pausar.

Se sustituyen «Gemini 2.5 Flash» y «Gemini~2.5» en `00-resumen.tex`,
`05-arquitectura.tex`, `06-implementacion.tex`, `08-discusion.tex`,
`09-conclusiones.tex`, `10-recomendaciones.tex`, `11-aspectos-legales.tex` y
`12-anexos.tex`. NO se re-edita §1.6 de `01-introduccion.tex` ni
`docs/anexo_h_prompt_gemini.md`: c-76 ya los alineo (tareas 9.2 y 5.3) y su
titularidad se conserva.

Alternativa considerada: dejar «Gemini 2.5 Flash» y cambiar el codigo a ese
identificador. Se descarta: el modelo 2.5 ya no esta disponible en la familia
desplegada (segun `settings.py:73-74`) y el alcance de este change es documental
(NO se toca `App/**`).

## Risks / Trade-offs

- **[Colision de archivos con c-77/c-80]** -> Orden de aplicacion fijo
  (D3) y edicion acotada por linea; las lineas compartidas se referencian.
- **[La cifra re-medida difiere de la del dictamen]** -> Se publica el valor de
  HEAD con el comando que lo reproduce (D2); el desajuste es el objeto mismo del
  hallazgo A-12.
- **[A-13 retrae la latencia y deja un vacio en §6.4]** -> Reformular con la
  evidencia real coordinada con c-77 Grupo E; si no hay evidencia atribuible, se
  declara la limitacion en vez de inventar un rango.
- **[La cobertura de frontend no puede publicarse sin correr la suite]** ->
  Decision en OQ2: corregir la cifra al valor medido (no requiere informe) o
  versionar el informe generado en `docs/` como evidencia (no edita `App/**`).
- **[A-11 reformulado puede quedar vago]** -> El texto enumera exactamente lo que
  existe: pruebas estructurales del `n8n/workflow.json` y pruebas de API/base de
  datos; sin prometer e2e.
- **[M-NUEVO pisa la alineacion de c-76]** -> Solo se editan los ocho archivos
  fuera de §1.6 y el Anexo H; el barrido `rg` excluye `01-introduccion.tex` y
  `docs/anexo_h_prompt_gemini.md`. Si apareciera una variante en esos dos, se
  reporta como residuo de c-76 y no se reescribe.

## Migration Plan

1. Aplicar c-76, c-77 y c-80 primero (orden D3).
2. Re-medir los conteos de pruebas en HEAD (A-11, A-12).
3. Editar `05-arquitectura.tex` (§5.4, Tabla 5) y `06-implementacion.tex` (§6.1,
   §6.4, §6.7, §6.8) segun D1.
4. Alinear el nombre del modelo a `gemini-3.6-flash` en los ocho archivos de
   seccion afectados (D7), sin tocar §1.6 ni el Anexo H.
5. Verificar con `rg` que no queda «Gemini 2.5 Flash» / «Gemini~2.5» en el cuerpo.
6. Recompilar en Overleaf (XeLaTeX) sin errores fatales.
7. `openspec validate --strict`.

Rollback: `git checkout --` sobre los dos `.tex` o `git revert` del commit; los
artefactos OPSX se descartan con el directorio del change.

## Open Questions

- **OQ1**: valor exacto del recuento de la suite de frontend en HEAD al momento
  de aplicar (la medicion preliminar da 56 archivos / 340 `it(`; el dictamen dice
  68). Se resuelve con el comando de re-medicion en la tarea 1.1.
- **OQ2**: si la cobertura de sentencias se corrige al valor medido o se publica
  el informe versionado en `docs/` como evidencia. Ambas opciones son documentales
  y no cambian el alcance.
- **OQ3**: redaccion exacta de la reformulacion de §6.4 (A-13), pendiente de la
  evidencia atribuible que coordine c-77 Grupo E.
