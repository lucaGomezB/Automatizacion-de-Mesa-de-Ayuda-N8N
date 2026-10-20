# Proposal: c-94 — Verificabilidad de la implementacion y la arquitectura (Caps. 5-6)

## Why

La re-auditoria de capitulos (`docs/Tesis/Correcciones/auditoria-capitulos.md`)
detecto que los Capitulos 5 (Arquitectura) y 6 (Implementacion) afirman hechos
que el repositorio no respalda, y que la reconciliacion
(`docs/Tesis/Correcciones/reconciliacion-cobertura.md`, seccion 3, N3) asigno a
este change. El §6.7 declara pruebas extremo a extremo que ejecutan el flujo
completo hasta la persistencia validando N8N (A-11) y una suite de frontend de
89 pruebas con 98,6 % de cobertura de sentencias (A-12); ninguna de las dos
cifras se reproduce. El §6.4 informa una latencia telefonica de 12 a 15 s
desglosada en tres tramos, sin `n`, sin dispersion y sin procedimiento, y dado
C-17 (el agente no puede ejecutarse como esta publicado) esas observaciones no
son atribuibles al flujo publicado (A-13). Ademas, el §6.8 presenta un ejemplo
imaginado como «caso concreto» (M-08), el §6.1 declara preparacion para
Kubernetes 1.30 sin ningun manifiesto (M-09), el §5.4 fija parametros de
inferencia «optimizados» sin procedimiento (M-12) y la Tabla 5 lista tres de los
puntos de entrada reales de la API (M-13).

Ademas, el cuerpo de la tesis sigue nombrando el modelo de inferencia como
«Gemini 2.5 Flash» (o «Gemini~2.5») en pasajes de `00-resumen.tex`,
`05-arquitectura.tex`, `06-implementacion.tex`, `08-discusion.tex`,
`09-conclusiones.tex`, `10-recomendaciones.tex`, `11-aspectos-legales.tex` y
`12-anexos.tex`, mientras que el codigo y la configuracion desplegados usan
`gemini-3.6-flash`. c-76 alineo unicamente §1.6 de `01-introduccion.tex` y
`docs/anexo_h_prompt_gemini.md`; el resto del cuerpo quedo inconsistente. Es un
hallazgo de coherencia (P2/R3 del dictamen) que ningun change habia tomado como
propio.

El objeto del change es alinear el texto de los Capitulos 5 y 6 con lo que el
repositorio permite verificar —y, por extension, la coherencia del nombre del
modelo en todo el cuerpo—: retraer o reformular cada afirmacion no respaldada,
alinear el identificador del modelo con el real, y publicar la evidencia cuando
exista. No se modifica codigo.

## What Changes

### Grupo A — Altas

| Id | Correccion | Evidencia (texto) |
|----|-----------|-------------------|
| A-11 | §6.7 declara «pruebas extremo a extremo que ejecutaban el flujo completo desde el envio de un correo simulado hasta la persistencia del ticket, validando la integracion con N8N en su totalidad». No existe ninguna prueba que instancie N8N: la suite de backend incluye pruebas estructurales del `n8n/workflow.json` y pruebas de API/base de datos, pero ninguna ejecuta el flujo de extremo a extremo. Retraer la afirmacion o reformularla a lo que existe | `06-implementacion.tex:85` |
| A-12 | §6.7 declara «una suite de 89 pruebas automatizadas» con «cobertura de sentencias del 98,6 %», desagregada en 27 servicios + 10 hooks + 43 paginas/graficos + 9 componentes (=89). El recuento `it(`/`test(` no reproduce 89 y no existe informe de cobertura versionado. Re-medir contra HEAD, corregir las cifras o publicar el informe como evidencia | `06-implementacion.tex:89` |
| A-13 | §6.4 informa latencia telefonica de 12 a 15 s «segun las observaciones operativas durante la fase de validacion», en tres tramos, sin `n`, sin dispersion y sin procedimiento. Dado C-17, las observaciones no son atribuibles al flujo publicado. Retraer o reformular con evidencia real; coordinar con c-77 Grupo E (tiempo telefonico) | `06-implementacion.tex:52` |

### Grupo M — Medias

| Id | Correccion | Evidencia (texto) |
|----|-----------|-------------------|
| M-08 | §6.8 cierra con un ejemplo hipotetico («si el sistema detecta que veinte usuarios han reportado la rotura de auriculares...») presentado como «utilidad practica [...] se ilustra con un caso concreto». Reformular como hipotetico. La captura del dashboard es de c-80 (tarea 6.6); no duplicar | `06-implementacion.tex:101` |
| M-09 | §6.1 declara el despliegue «preparado para migracion a un cluster Kubernetes 1.30» sin ningun manifiesto en el repositorio. Retraer o acotar explicitamente como trabajo futuro | `06-implementacion.tex:8` |
| M-12 | §5.4 fija parametros de inferencia (temperatura 0,3, top-p 0,9, max 100 tokens, timeout 10 s) «optimizados para exactitud y latencia», sin describir procedimiento ni valores alternativos evaluados. Reformular o documentar el procedimiento | `05-arquitectura.tex:50` |
| M-13 | Tabla 5 (`tab:api`) lista tres puntos de entrada; la API real expone ademas autenticacion (`/api/v1/auth`), clasificaciones (GET y PATCH) y un PATCH sobre incidentes. Completar la tabla (agrupando por recurso) y agregar una nota de que no es exhaustiva, con remision al contrato completo en el Anexo D/OpenAPI | `05-arquitectura.tex:92-105` |

### Grupo M-NUEVO — Nombre del modelo inconsistente en el cuerpo (P2/R3 del dictamen)

| Id | Correccion | Evidencia (texto) |
|----|-----------|-------------------|
| M-NUEVO | El cuerpo nombra el modelo de inferencia como «Gemini 2.5 Flash» / «Gemini~2.5», pero el identificador real configurado y desplegado es `gemini-3.6-flash` (ver D7 en `design.md`). Alinear todas las menciones del cuerpo al identificador real. El §1.6 de `01-introduccion.tex` y `docs/anexo_h_prompt_gemini.md` ya fueron alineados por c-76 (tareas 9.2 y 5.3); NO se duplican | `00-resumen.tex:9,23`; `05-arquitectura.tex:23,50,54,58`; `06-implementacion.tex:10`; `08-discusion.tex:34,46`; `09-conclusiones.tex:6`; `10-recomendaciones.tex:32`; `11-aspectos-legales.tex:16`; `12-anexos.tex:10` |

### Coordinacion — residuo textual de C-18 (sin duplicar)

- El residuo textual de C-18 (Tabla 4 usa `id_canal` en vez de `canal_origen_id`;
  §5.3 describe dos llamadas —modulo de procesamiento + REST— cuando el flujo
  real es un unico `POST /api/v1/incidentes` que clasifica y persiste) ya
  pertenece a **c-77 C3** (`openspec/changes/c-77-tesis-errores-estadisticos-inferenciales/tasks.md:60-62`).
  Este change lo **referencia y verifica**, no lo redefine ni lo reescribe.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `tesis-document`: verificabilidad de las afirmaciones de implementacion y
  arquitectura de los Capitulos 5 y 6 — retraccion o reformulacion de las
  pruebas e2e de N8N (A-11) y del recuento/cobertura de la suite de frontend
  (A-12); reformulacion de la latencia telefonica sin atribuir (A-13); marcado
  del ejemplo del dashboard como hipotetico (M-08); acotacion de la afirmacion
  de Kubernetes (M-09); retiro del calificativo «optimizados» sin procedimiento
  en los parametros de inferencia (M-12); y completitud y no exhaustividad
  declarada de la Tabla 5 de puntos de entrada REST (M-13). Tambien cubre la
  coherencia del nombre del modelo en el cuerpo de la tesis (M-NUEVO / P2-R3),
  alineandolo al identificador real `gemini-3.6-flash` sin duplicar el alcance
  ya aplicado por c-76 en §1.6 y el Anexo H.

## Impact

Solo documentacion (NO se toca `App/**`):

- `docs/Tesis/v9 (IA)/paper/sections/05-arquitectura.tex` (§5.3, §5.4, §5.6
  Tabla 4, §5.7 Tabla 5).
- `docs/Tesis/v9 (IA)/paper/sections/06-implementacion.tex` (§6.1, §6.3, §6.4,
  §6.7, §6.8).
- Coherencia del nombre del modelo (M-NUEVO): `00-resumen.tex`, `05-arquitectura.tex`,
  `06-implementacion.tex`, `08-discusion.tex`, `09-conclusiones.tex`,
  `10-recomendaciones.tex`, `11-aspectos-legales.tex` y `12-anexos.tex`.
  NO se editan §1.6 de `01-introduccion.tex` ni `docs/anexo_h_prompt_gemini.md`
  (ya alineados por c-76).
- `main.pdf` (recompilado en Overleaf con XeLaTeX).

Fuentes de verdad (no se alteran):

- `docs/openapi.json` (contrato real de la API; 33 rutas) para la Tabla 5.
- `data/corpus_evaluacion_pseudonimizado.json` y `evaluation/report.md` para
  cualquier cifra que se conserve.
- Para M-NUEVO, el identificador real del modelo: `gemini-3.6-flash` en
  `App/Backend/app/config/settings.py:78` (`gemini_model: str =
  "gemini-3.6-flash"`), `App/Backend/.env.example:13`, `README.md:315` y
  `docs/anexo_h_prompt_gemini.md` (este ultimo ya alineado por c-76).

Coordinacion (sin duplicar alcance):

- **c-80** es dueno de figuras/capturas (incluida la del dashboard, tarea 6.6) y
  de la nota de N8N 1.62; c-94 no agrega capturas ni toca esa nota.
- **c-76** es dueno de los numeros (tiempos, exactitud, macro-F1); c-94 no los
  re-deriva. c-76 ya alineo §1.6 de `01-introduccion.tex` y
  `docs/anexo_h_prompt_gemini.md` al identificador real (tareas 9.2 y 5.3); c-94
  referencia esa alineacion y NO la duplica.
- **c-77** es dueno de la coherencia tecnica C1-C8, incluido C3 (Tabla 4
  `id_canal` -> `canal_origen_id` y §5.3 de dos llamadas a una); c-94 solo lo
  referencia.
- **c-80/c-77** son duenos de las descripciones de flujo; c-94 no las reescribe.
- Orden de aplicacion: c-94 DESPUES de c-76, c-77 y c-80 (comparte
  `05-arquitectura.tex` y `06-implementacion.tex`).

## Rollback Plan

`git checkout --` sobre los dos `.tex` afectados, o `git revert` del commit del
change. Los artefactos OPSX se descartan con el directorio del change.

## Success Criteria

- [ ] §6.7 ya no afirma pruebas e2e que instancien N8N; el texto describe lo
      que existe (pruebas estructurales del workflow y pruebas de API/base de
      datos), o la prueba e2e se implementa fuera de este change (no aplica:
      alcance solo documental).
- [ ] §6.7 publica un recuento y una cobertura de la suite de frontend
      reproducibles en HEAD, o publica el informe de cobertura como evidencia
      versionada; no queda la cifra 89/98,6 % sin respaldo.
- [ ] §6.4 ya no declara la latencia 12-15 s como observacion operativa
      atribuible; se retrae o se reformula con evidencia real y coordinada con
      c-77 Grupo E.
- [ ] §6.8 presenta el ejemplo del dashboard como hipotetico, no como «caso
      concreto».
- [ ] §6.1 no declara preparacion para Kubernetes 1.30 sin manifiesto; se
      retrae o se acota como trabajo futuro.
- [ ] §5.4 no usa «optimizados para exactitud y latencia» sin procedimiento; el
      calificativo se retira o el procedimiento se documenta.
- [ ] Tabla 5 lista los grupos de puntos de entrada reales (auth, incidentes,
      clasificaciones, estadisticas/health) y declara que no es exhaustiva, con
      remision al Anexo D/OpenAPI.
- [ ] El residuo textual de C-18 (Tabla 4 / §5.3) queda cubierto por c-77 C3 sin
      duplicacion en este change.
- [ ] M-NUEVO: ninguna mencion del cuerpo usa «Gemini 2.5 Flash» ni «Gemini~2.5»;
      todas usan el identificador real `gemini-3.6-flash`, y `rg` no encuentra
      residuos en los ocho archivos de seccion afectados. §1.6 y el Anexo H
      permanecen como los dejo c-76, sin re-edicion.
- [ ] `main.pdf` recompilado en Overleaf (XeLaTeX) sin errores fatales.
- [ ] `openspec validate c-94-tesis-implementacion-verificabilidad --strict`
      pasa.
