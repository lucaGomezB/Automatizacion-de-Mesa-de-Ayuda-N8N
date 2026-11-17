# Design: Cerrar el residual de K-02 y la omision de A-02 en §1.8

## Context

Ver `proposal.md` - Why. Estado y restricciones que moldean el enfoque:

- Fuente: `auditorias/Devolucion_Tercera_Instancia_TFI_v1.5.2_2026-11-16.md`, secciones 2 (dictamen), 5 (K-02, A-02) y 7 (correcciones 2 y 4). K-02 exige «agregar en §7.5 un parrafo con la base de licitud y el alcance de esa autorizacion... Si la autorizacion no existe, retirar los textos del repositorio publico y de la tesis». A-02 senala que §1.8 afirma que la validacion se realiza sobre un corpus de la organizacion de Mendoza.
- c-235 ya: elimina el parrafo de consentimiento de `E3`/`E4`/`E5` de §7.5 (tarea 6.1); deja §7.3 exacta (compuerta P4, D3.3); define OOS-026 (rotulado, opcion A por defecto) y deja la eliminacion (opcion B) como OQ2 opcional. c-235 NO agrega parrafo de licitud, NO lista §1.8 en su inventario de retiro (D2 solo «verifica» §1.8) y NO hace obligatoria la disposicion del repositorio.
- La cadena «licitud» no aparece en c-235..c-239 (verificado por busqueda).
- Archivos: §7.5 = `11-aspectos-legales.tex` `subsec:consentimiento-derechos`; §7.3 = `subsec:transferencia-internacional`; §1.8 = `01-introduccion.tex` `subsec:alcance-delimitaciones` (frase en L72; delimitacion geografica en L76). Corpus publicado: `evaluation/data/campana/corpus_independiente.json`, `corpus_independiente_arbitrado.json`; pruebas que los leen: `evaluation/tests/test_linea_de_base.py`, `evaluation/tests/test_calibracion_gate.py` (L396-399), `evaluation/monitoreo/test_monitor_deriva.py` (L203-226); sumas: `evaluation/data/campana/analisis/SHA256SUMS.txt`.

## Goals / Non-Goals

**Goals:**

- Cerrar el residual de K-02: §7.5 gana un parrafo de licitud y alcance ramificado por la compuerta P4/P8, nunca por omision.
- Cerrar la omision de A-02: §1.8 queda veraz (una sola organizacion, dentro de la muestra).
- Retirar los textos del corpus independiente del repositorio publico (decision de autores registrada), conservando los bytes solo en un archivo privado con SHA-256 como trazabilidad.

**Non-Goals:**

- Reescribir el retiro de c-235 (canonico) ni sus requisitos; este change solo AGREGA.
- Balance neto / umbral (c-236), declaracion de IA (c-237), legibilidad (c-238), respuestas al tribunal / tag (c-239).
- Cero codigo de aplicacion, cero re-medicion, cero llamadas a Gemini. La unica excepcion «de codigo» es el ajuste de pruebas de `evaluation/` en la rama de retiro (commit separado).

## Decisions

### D1 — El parrafo de licitud vive en §7.5 y queda fijado por P4/P8 ya respondidas

El parrafo va en `subsec:consentimiento-derechos` (§7.5), no en §7.3 ni en una seccion nueva. §7.3 sigue siendo la seccion de transferencia (c-235 D3.3 la deja exacta); §7.5 es donde el tribunal pidio la base de licitud y donde ya vive el consentimiento de los etiquetadores. Con P4 y P8 respondidas por los autores (textos construidos, sin datos de terceros ni personales; consentimientos reales), el parrafo queda fijado y declara: (i) ausencia de datos de terceros ni personales; (ii) retiro de esos textos del repositorio publico y de la tesis; (iii) remision a §7.3 para la transferencia a Gemini; (iv) la base de licitud de lo que se conserva (corpus de 200 pseudonimizado y campana complementaria, Ley 25.326 articulo citado).

Alternativa descartada: resolver por omision (no escribir nada); viola el requisito no silencioso del tribunal. Alternativa descartada: mantener una rama (b) «con datos de terceros»; queda superada por la respuesta P4 (no hay datos de terceros).

### D2 — §1.8 entra al inventario de retiro como frase a reconciliar

La frase de `01-introduccion.tex:72` («La validacion experimental se realiza sobre un corpus... organizacion... de Mendoza») se retira o se reescribe para que la validacion quede presentada como dentro de la muestra sobre una sola organizacion. No se toca la delimitacion geografica de L76 (una unica organizacion de Mendoza), que sigue siendo la limitacion de validez externa vigente (coherente con el requisito «Validez externa declarada en las conclusiones...»). Alternativa descartada: dejar §1.8 como esta porque c-235 «la verifica»; la verificacion de c-235 (tarea 5.1) no garantiza la verdad tras el retiro y el tribunal la senalo explicitamente en A-02.

### D3 — Disposicion del repositorio: retiro decidido

La decision de los autores es RETIRAR los textos del corpus independiente del repositorio publico, alineada con «Si la autorizacion no existe, retirar los textos del repositorio publico y de la tesis». No se conservan en el repositorio: se eliminan en un commit propio, con ajuste de las tres pruebas y de las sumas SHA-256 y suite verde. Los bytes se conservan, si los autores lo deciden, en un archivo PRIVADO fuera del repositorio, con sus SHA-256 citados en la tesis como trazabilidad. Alternativa descartada: conservar+rotular en el repositorio publico; deja publicados textos que el tribunal pidio retirar salvo acreditacion, y no asegura K-02.

### D4 — Politica de deltas

Solo ADDED, sin MODIFIED ni REMOVED, para no chocar con c-235 (canonico del retiro) ni c-236 (balance). `tesis-document` gana tres requisitos; `evaluation-out-of-sample-validation` gana OOS-027. OOS-026 de c-235 (rotulado) queda subsumido por el retiro: no quedan archivos del corpus independiente en el repositorio que rotular; OOS-027 define el retiro y el commit separado. Sin tocar: `tesis-dictamen-v1-3-0` (el residual no cambia sus requisitos), `tesis-numeros-canonicos`, `tesis-baseline-integration`.

## Risks / Trade-offs

| Riesgo | Mitigacion |
|---|---|
| [Parrafo de licitud con hechos no confirmados] | Compuertas P4/P8 registradas antes de escribir; rama elegida solo con respuesta escrita |
| [Retiro silencioso del parrafo] | Requisito con escenario «parrafo presente en ambas ramas» |
| [§1.8 reescrita de forma contradictoria con §9.3/§10.2] | Una sola remision a la nota de versiones; alineacion con el requisito de validez externa |
| [Conflicto con c-235] | Solo ADDED; OOS-027 referencia OOS-026 sin reescribirlo |
| [Romper CI al eliminar] | Commit separado; suite de `evaluation/` verde como criterio de cierre |
| [Conflicto con c-236] | No se toca §9.5 ni el balance; se aplica despues de c-235 |

## Migration Plan

1. Compuertas de autores: registrar P4/P8 (reabiertas) y la decision de disposicion del repositorio en `dictamen-correcciones.md`.
2. §7.5: escribir el parrafo de licitud segun la rama registrada.
3. §1.8: retirar/reescribir la frase de Mendoza; verificar coherencia con §9.3/§10.2 y la validez externa.
4. Disposicion del repositorio: commit separado de retiro con las tres pruebas y las sumas; conservar los bytes en archivo privado (si corresponde) con SHA-256 citados.
5. Cierre: `openspec validate --strict` y bateria de `rg`.

Rollback: `git revert` por commit; el commit de eliminacion se revierte de forma independiente.

## Open Questions

- **P4/P8 (autores, reabiertas de c-235):** confirmar que los textos del corpus retirado son descripciones genericas sin datos de terceros ni personales, o declarar la autorizacion escrita, su licitud y alcance. Sin respuesta, el parrafo de §7.5 queda bloqueado.
- **DP-01 (autores, resuelta 2026-11-16):** disposicion del repositorio publico = RETIRAR. No hay rama de conservacion.
- **DP-02 (autores):** redaccion exacta del parrafo de §7.5 y de la frase reconciliada de §1.8, para aprobacion previa.
