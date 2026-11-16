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
- Convertir la disposicion del repositorio publico en una decision obligatoria registrada, con default alineado a K-02 (retiro), sin tocar bytes en la rama de conservacion.

**Non-Goals:**

- Reescribir el retiro de c-235 (canonico) ni sus requisitos; este change solo AGREGA.
- Balance neto / umbral (c-236), declaracion de IA (c-237), legibilidad (c-238), respuestas al tribunal / tag (c-239).
- Cero codigo de aplicacion, cero re-medicion, cero llamadas a Gemini. La unica excepcion «de codigo» es el ajuste de pruebas de `evaluation/` en la rama de retiro (commit separado).

## Decisions

### D1 — El parrafo de licitud vive en §7.5 y ramifica por P4/P8

El parrafo va en `subsec:consentimiento-derechos` (§7.5), no en §7.3 ni en una seccion nueva. §7.3 sigue siendo la seccion de transferencia (c-235 D3.3 la deja exacta); §7.5 es donde el tribunal pidio la base de licitud y donde ya vive el consentimiento de los etiquetadores. El parrafo ramifica por la respuesta de P4 (quien redacto los 150 textos y si hay datos de terceros) y P8 (si las afirmaciones de consentimiento se sostienen):
- (a) sin datos de terceros → declarar explicitamente que no hay datos de una tercera organizacion y que no se requiere autorizacion ni licitud; remitir a §7.3 para la transferencia a Gemini.
- (b) con datos de terceros → declarar la autorizacion escrita, su base de licitud (Ley 25.326, articulo citado) y su alcance (uso, publicacion, transferencia); remitir a §7.3.

Alternativa descartada: resolver por omision (no escribir nada); viola el requisito no silencioso del tribunal. Alternativa descartada: fijar una unica rama sin compuerta; contradice el estado abierto de P4/P8 en c-235.

### D2 — §1.8 entra al inventario de retiro como frase a reconciliar

La frase de `01-introduccion.tex:72` («La validacion experimental se realiza sobre un corpus... organizacion... de Mendoza») se retira o se reescribe para que la validacion quede presentada como dentro de la muestra sobre una sola organizacion. No se toca la delimitacion geografica de L76 (una unica organizacion de Mendoza), que sigue siendo la limitacion de validez externa vigente (coherente con el requisito «Validez externa declarada en las conclusiones...»). Alternativa descartada: dejar §1.8 como esta porque c-235 «la verifica»; la verificacion de c-235 (tarea 5.1) no garantiza la verdad tras el retiro y el tribunal la senalo explicitamente en A-02.

### D3 — Disposicion del repositorio: decision obligatoria con default K-02

Se invierte la prioridad de c-235 D7/OQ2: el default pasa de CONSERVAR (A) a RETIRAR, alineado con «Si la autorizacion no existe, retirar los textos del repositorio publico y de la tesis». La conservacion queda permitida SOLO como decision registrada de que los textos son descripciones genericas sin datos de terceros. La eliminacion, si se elige, sigue c-235 D7 opcion B: commit separado, ajuste de las tres pruebas y de las sumas SHA-256, suite verde. Alternativa descartada: mantener conservar por defecto; deja el repositorio publico alojando textos que el tribunal pidio retirar salvo acreditacion, y la omision de la decision equivale a conservar (riesgo de K-02).

### D4 — Politica de deltas

Solo ADDED, sin MODIFIED ni REMOVED, para no chocar con c-235 (canonico del retiro) ni c-236 (balance). `tesis-document` gana tres requisitos; `evaluation-out-of-sample-validation` gana OOS-027. OOS-026 de c-235 sigue siendo el canon del rotulado; OOS-027 lo complementa con el default de retiro y el commit separado. Sin tocar: `tesis-dictamen-v1-3-0` (el residual no cambia sus requisitos), `tesis-numeros-canonicos`, `tesis-baseline-integration`.

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
4. Disposicion del repositorio: en la rama de retiro, commit separado con las tres pruebas y las sumas; en la de conservacion, verificar OOS-026 y sumas intactas.
5. Cierre: `openspec validate --strict` y bateria de `rg`.

Rollback: `git revert` por commit; el commit de eliminacion se revierte de forma independiente.

## Open Questions

- **P4/P8 (autores, reabiertas de c-235):** confirmar que los textos del corpus retirado son descripciones genericas sin datos de terceros ni personales, o declarar la autorizacion escrita, su licitud y alcance. Sin respuesta, el parrafo de §7.5 queda bloqueado.
- **DP-01 (autores):** disposicion del repositorio publico: retirar (default K-02) o conservar+rotular con la decision registrada de textos genericos. Sin respuesta, la rama por defecto es retirar.
- **DP-02 (autores):** redaccion exacta del parrafo de §7.5 y de la frase reconciliada de §1.8, para aprobacion previa.
