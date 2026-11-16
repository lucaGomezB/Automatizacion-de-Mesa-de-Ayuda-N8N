# Proposal: Cerrar el residual de K-02 y la omision de A-02 en §1.8

## Why

c-235 resuelve K-01 por retiro y cierra la mayor parte de K-02, pero deja tres residuales que la
devolucion de tercera instancia exige (`auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md`,
Secciones 5 y 7):

1. **§7.5 sin base de licitud (K-02 residual).** El tribunal exige «agregar en §7.5 un parrafo con la
   base de licitud y el alcance de esa autorizacion» para los datos de la tercera organizacion. c-235 solo
   ELIMINA el parrafo de consentimiento de `E3`/`E4`/`E5` (tarea 6.1) y no agrega nada: la cadena
   «licitud» no aparece en c-235..c-239 (verificado por busqueda). El requisito debe ser no silencioso y
   ramificado por la compuerta de autores P4/P8.
2. **§1.8 que queda falsa (A-02 residual).** §1.8 (`01-introduccion.tex:72`) dice que «la validacion
   experimental se realiza sobre un corpus... organizacion... de Mendoza». Con el retiro, la unica
   validacion vigente es dentro de la muestra (una sola organizacion); la frase debe retirarse o
   reescribirse para no afirmar que la validacion retirada corria sobre el corpus de Mendoza. El
   inventario de c-235 (D2) lista §1.4 y §1.7 pero NO §1.8 (su tarea 5.1 solo «verifica coherencia»).
3. **Repositorio publico sin decision obligatoria (K-02 residual).** c-235 D7 deja por defecto
   CONSERVAR+re-rotular (opcion A) y la eliminacion (opcion B) como decision opcional (OQ2). El tribunal
   exige: «Si la autorizacion no existe, retirar los textos del repositorio publico y de la tesis.» La
   disposicion debe ser una decision OBLIGATORIA registrada, con default alineado a K-02.

## What Changes

| Bloque | Que cambia | Observacion que cierra | Gobernanza |
|---|---|---|---|
| **A. Licitud en §7.5** | `11-aspectos-legales.tex` (`subsec:consentimiento-derechos`) gana un parrafo con la base de licitud y el alcance de la autorizacion de los datos de la tercera organizacion, ramificado por P4/P8 | K-02 (residual) | ALTA |
| **B. §1.8 veraz** | `01-introduccion.tex` (`subsec:alcance-delimitaciones`) retira o reescribe la frase que afirma que la validacion corre sobre el corpus de Mendoza, dejando una sola organizacion dentro de la muestra | A-02 (residual) | MEDIA |
| **C. Disposicion del repositorio publico** | Decision OBLIGATORIA y registrada en `dictamen-correcciones.md`, con default alineado a K-02 (retirar) salvo que los autores registren que los textos son descripciones genericas sin datos de terceros | K-02 (residual) | ALTA |

Fuera de alcance: recompilar, bump y tag (`c-239`); balance neto y umbral (`c-236`); declaracion de IA
(`c-237`); legibilidad (`c-238`). Este change no escribe codigo de aplicacion, no mide de nuevo y no llama
a Gemini. La eliminacion de archivos, si se elige, es la unica excepcion «de codigo»: ajusta pruebas de
`evaluation/` y sumas SHA-256 en un commit separado.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tesis-document`: se AGREGAN tres requisitos — parrafo de licitud y alcance en §7.5 ramificado por
  P4/P8; §1.8 veraz (una sola organizacion, dentro de la muestra); y disposicion del repositorio publico
  como decision obligatoria y registrada con default K-02.
- `evaluation-out-of-sample-validation`: se AGREGA OOS-027 — retiro del corpus independiente del
  repositorio publico (default K-02), con ajuste de las tres pruebas y las sumas SHA-256 en un commit
  separado.

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex` | Modificado | §7.5 gana el parrafo de licitud (rama P4/P8) |
| `docs/Tesis/v10 (IA)/paper/sections/01-introduccion.tex` | Modificado | §1.8 frase de Mendoza retirada/reescrita |
| `docs/Tesis/Correcciones/dictamen-correcciones.md` | Aditivo | Entrada del change, compuertas P4/P8/DP-01/DP-02 y la decision registrada |
| `evaluation/data/campana/corpus_independiente.json`, `corpus_independiente_arbitrado.json` | Sin cambio por defecto; retirados solo si los autores lo registran | c-235 D7 opcion B |
| `evaluation/tests/test_linea_de_base.py`, `evaluation/tests/test_calibracion_gate.py`, `evaluation/monitoreo/test_monitor_deriva.py`, `analisis/SHA256SUMS.txt` | Modificados solo en el commit separado de eliminacion | Ajuste tras retiro |
| Changes c-235..c-239 | Coordinacion, no edicion | c-235 canonico del retiro; se aplica despues de c-235, antes del tag de c-239 |

## Risks

| Riesgo | Prob. | Mitigacion |
|---|---|---|
| Parrafo de licitud redactado con hechos no confirmados | Media | Compuertas P4/P8 registradas antes de escribir; la rama se elige solo con respuesta escrita |
| Resolver el parrafo por omision (retiro silencioso) | Media | Requisito con escenario «parrafo presente en ambas ramas» |
| Conflicto con c-235 (canonico del retiro) | Media | Solo ADDED; no reescribe requisitos de c-235 |
| Conflicto con c-236 (balance) | Baja | No toca el balance neto ni el umbral; se aplica despues de c-235 |
| Romper CI al eliminar artefactos | Alta si se elimina | Default K-02 = eliminar; ajuste de pruebas y sumas en commit separado con suite verde |

## Rollback Plan

`git revert` de cada commit: las ediciones de `.tex` son reemplazos localizados; la entrada de
`dictamen-correcciones.md` es aditiva; la eventual eliminacion de artefactos va en un commit separado,
revertible de forma independiente.

## Dependencies

- Precondicion dura: respuesta registrada de los autores a P4/P8 y a la decision de disposicion del
  repositorio antes de escribir §7.5 y de eliminar archivos.
- Se aplica DESPUES de c-235 (construye sobre su retiro y su OOS-026) y ANTES del tag de c-239.
- No toca c-236 (balance/umbral) ni c-237/c-238; coordina con c-239 solo en el orden.

## Success Criteria

- [ ] §7.5 contiene el parrafo de licitud y alcance, ramificado por P4/P8, en ambas ramas (nunca por omision).
- [ ] §1.8 no afirma que la validacion corre sobre un corpus de una segunda organizacion; presenta una sola organizacion, dentro de la muestra.
- [ ] La disposicion del repositorio publico esta registrada como decision de autores con default K-02; si se conserva, esta documentado que los textos son genericos sin datos de terceros.
- [ ] Si se retira, las tres pruebas y las sumas SHA-256 estan ajustadas en un commit separado y la suite de `evaluation/` esta verde.
- [ ] `openspec validate c-240-cerrar-el-residual-de-k-02 --strict` y `openspec validate --strict` pasan sin conflictos.
