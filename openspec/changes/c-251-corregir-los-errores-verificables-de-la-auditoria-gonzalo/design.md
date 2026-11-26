# Design: Corregir los errores verificables de la auditoría Gonzalo (nivel 2)

## Context

Ver `proposal.md` - Why. Estado verificado sobre `main` (post `v1.6.5`, versión de defensa, tag
anotado). La auditoría independiente de nivel 2 (Gonzalo Sevilla) detecta cinco errores verificables
que NO dependen de la discusión de fondo sobre retractación. Esto es distinto de c-250: aquella
atendió las observaciones C-01 a C-07 del tribunal; esta atiende errores remanentes que la propia
corrección de c-250 dejó a la vista (E1/E3: la redacción del art. 28 y la frase v1.6.0; E2: la fecha
de notificación que c-250 fijó en el sentido contrario al acta) más dos hallazgos de lectura
analítica (E4/E5). No existe un dictamen nuevo del tribunal; la fuente es la propia auditoría
Gonzalo, contrastada contra el acta firmada y la devolución de quinta instancia.

- **Mapa archivo→capítulo (obligatorio).** El nombre del `.tex` NO coincide con el número de capítulo
  rendido: Ch7 (legal, reubicado por c-105) = `11-aspectos-legales.tex`, Ch9 (Discusión) =
  `08-discusion.tex`, Ch4 = `04-marco-metodologico.tex`, Anexo K = `12-anexos.tex`. Las tareas citan
  el nombre de archivo; la prosa, el número rendido.
- **Pasajes exactos (v1.6.5, `main`).** E1 en `11-aspectos-legales.tex:12` ("el artículo 28 dispone
  que los datos disociados no se consideran datos personales..."); E2 en `:32` ("...de forma verbal el
  2026-09-30"); E3 en `:32` (oración final "La versión v1.6.0 afirmó..."); E4 en
  `08-discusion.tex:22` ("la asimetría del instrumento y del alcance ... Eso favorece al segundo");
  E5 en `12-anexos.tex:354`, `04-marco-metodologico.tex:16` y `08-discusion.tex:22/24`. Los números
  de línea se re-verifican con `rg` antes de editar (las ediciones los desplazan).
- **Fuente de verdad de la contradicción E2.** `docs/seguridad/acta-consentimiento-t2.md` cabecera
  (línea 7: "notificación a los integrantes del grupo el 2026-10-01") y §4 (líneas 84-87: "la
  notificación ... se realizó el 2026-10-01"). El tribunal C-05 ("Definir la 'notificación a los
  integrantes del grupo' del 01/10") fija la referencia externa en 2026-10-01. La tesis dice
  2026-09-30. Es una contradicción objetiva, no interpretativa.
- **Fuente de verdad de E1.** Ley 25.326: art. 2 (definición de "disociación de datos"), art. 28
  (exención de archivos de encuestas/estadística/investigación con datos no atribuibles, 28.1, y
  mandato de disociación, 28.2), art. 11.3.e (cesión sin consentimiento cuando media disociación).
  Ningún artículo dice literalmente "disociado = no dato personal".
- **Fuente de verdad de E5.** `04-marco-metodologico.tex:16` ("De los 200 valores, 199 son múltiplos
  de 5 s y 180 de 10 s"). La devolución de quinta instancia C-02 (línea 198) calculó "10 s menos por
  caso, la media manual baja a 51,6 s y la reducción a ≈65,6 %" sobre el componente "carga ~10 s" que
  luego se RETIRÓ (la carga nunca existió). El "descuento de 10 s" de la sensibilidad hereda ese
  origen, no el redondeo (cuyo máximo por caso es < 5 s).
- **Precedentes.** c-250 y c-249 son el template de forma: verificación ANTES/DESPUES con `rg`, línea
  base sin cambios de cifras, grupos gated (ALTA) vs. sin compuerta (MEDIA), documentación en
  `docs/Tesis/Correcciones/dictamen-correcciones.md` con sección propia.

## Goals / Non-Goals

**Goals:**

- Corregir la atribución legal del art. 28 (sin inventar texto legal; lectura fiel de arts. 2, 28 y
  11.3.e) para que el capítulo legal funde la licitud por disociación sin falsa cita (E1).
- Unificar la fecha de notificación a una sola, consistente con el acta firmada y con la referencia
  del tribunal C-05 (E2).
- Retirar la oración de la v1.6.0 que el tribunal C-05 pidió retirar explícitamente (E3).
- Fijar la dirección correcta de la asimetría de alcance (conservadora, cota inferior) separándola
  del instrumento (E4).
- Re-etiquetar la sensibilidad de `-10 s` sin cambiar sus valores (E5).

**Non-Goals:**

- No cambiar ninguna cifra canónica (61,6 s, 17,76 s, 71,2 %, 73,5 %, 56,6 s, 51,6 s, 68,6 %,
  65,6 %, etc.); no recomputar nada; no tocar `data/`, `evaluation/`, `App/`, `n8n/`.
- No editar `docs/seguridad/` (el acta es evidencia, no objeto de edición); no resolver C-06 ni la
  frase "propio entorno operativo" del acta §1.
- No decidir el fondo de la discusión de retractación ("titulares vs. responsables", caracterización
  jurídica del régimen (a)); pertenece a otra auditoría/instancia.
- No compilar, no taggear, no commitear, no archivar.

## Decisions

- **D1. Dos compuertas de autor (OQ-1, OQ-2) para E1 y E2, no para E3-E5.** E1 y E2 requieren un
  hecho o una redacción que solo los autores+director pueden fijar (cuál fecha es la correcta; cómo
  redactar la lectura legal fiel sin abrir una conclusión jurídica nueva). E3 es un retiro literal
  que el tribunal ordenó: no necesita decisión, solo gobernanza ALTA (mostrar el texto propuesto
  antes de escribir). E4 y E5 son re-etiquetados de encuadre ya determinados por el expediente. Nada
  de esto cambia las specs: las specs (ver `specs/`) ya enuncian la corrección y dejan el texto final
  en manos de autores.
- **D2. Gobernanza ALTA en E1-E3, MEDIA en E4-E5.** ALTA = `11-aspectos-legales.tex` (capítulo
  legal) y, en E2, la remisión al acta: mostrar el texto propuesto a autores+director antes de
  escribir. MEDIA = prosa de Discusión/Anexo, sin código: implementar con checkpoint y reportar.
- **D3. E1 no reescribe la conclusión legal; reformula la cita.** La licitud por disociación se
  mantiene como encuadre, pero la fundamentación deja de apoyarse en la frase inexacta del art. 28 y
  pasa a citar el art. 2 (definición), el art. 28 (exención de investigación con datos no
  atribuibles) y el art. 11.3.e (cesión) cada uno por lo que dice. No se introduce doctrina nueva ni
  se cita jurisprudencia: solo lectura fiel (OQ-2 confirma la redacción final). Alternativa
  considerada: cambiar el fundamento de licitud; descartada, porque excede el alcance del error
  verificable y entra en la discusión de fondo.
- **D4. E4 se resuelve separando dos componentes, no invirtiendo el signo global.** El texto actual
  funde "instrumento + alcance" bajo un "favorece al segundo". La corrección distingue: instrumento
  (lag humano) favorece al automatizado; alcance (manual estrecho vs. automatizado amplio) es
  conservador y subestima la ventaja. El número 71,2 % queda como está (es cota superior por
  redondeo, ver E5); solo se declara que la asimetría de alcance, por sí misma, tira la reducción
  reportada hacia abajo (cota inferior), coherente con la octava amenaza (`04:131`). Alternativa
  considerada: reescribir la enumeración completa de las seis explicaciones rivales; descartada por
  alcance (toca conclusiones de fondo).
- **D5. E5 re-etiqueta, no re-cuantifica.** `-5 s` = "cota de redondeo" (redondeo hacia arriba a
  múltiplos de 5 s; inflación máxima por caso < 5 s). `-10 s` = "escenario solicitado por el tribunal
  sobre la carga ~10 s retirada". Los valores 56,6 s / 51,6 s y 68,6 % / 65,6 % quedan intactos; el
  rótulo "mínimo del estimando primario" de la tabla de robustez permanece (proviene del cálculo del
  tribunal, legítimo como escenario adverso). Alternativa considerada: eliminar el `-10 s`;
  descartada, porque el tribunal C-02 pidió explícitamente cuantificarlo y el número es correcto.
- **D6. Registro.** `docs/Tesis/Correcciones/dictamen-correcciones.md` gana una sección c-251 con la
  tabla de decisiones (OQ-1, OQ-2), las filas ANTES/DESPUES por corrección y la gobernanza cumplida.
  Sin release, sin tag: el change termina en la corrección de prosa (la versión de defensa ya está
  liberada; una corrección posterior exigiría decisión de autores sobre si re-emitir).

## Risks / Trade-offs

- [La redacción de E1 abra o reabra la discusión jurídica de fondo (caracterización del régimen (a))]
  → Acotar a lectura fiel de los artículos citados, sin nueva conclusión; OQ-2 decide y el apply no
  redacta sin decisión registrada.
- [E2 corrija la fecha en el sentido equivocado] → OQ-1 fija la fecha por autores+director contra el
  acta firmada y el dictamen C-05; la verificación cruza ambos documentos.
- [E3 toque el consentimiento verbal del 02/10 al retirar la oración] → Retirar SOLO la oración de la
  v1.6.0 (la afirmación "no se sostiene"), sin tocar la cronología del consentimiento verbal
  (2026-10-02) que permanece y está cubierta por otros pasajes.
- [E4 introduzca una afirmación cuantitativa nueva sobre la cota inferior] → No cuantificar: declarar
  dirección y magnitud no estimada, consistente con `04:131`; no adjudicar un número nuevo.
- [E5 altere la lectura de robustez] → No cambiar valores ni el rótulo "mínimo del estimando
  primario"; solo re-etiquetar la JUSTIFICACIÓN del -10 s y del -5 s.

## Migration Plan

Sin migración de código ni de datos. Rollback por `git checkout` de los pasajes editados. No se
mueven tags ni se regeneran derivados; las fuentes `.tex` son el único artefacto modificado.

## Open Questions

**OQ-1 (fecha de notificación) — RESUELTA por los autores (2026-11-25).** Fecha correcta:
**2026-10-01** (1 de octubre). Fuente: acta firmada `docs/seguridad/acta-consentimiento-t2.md`
(cabecera y §4) y la referencia del tribunal C-05 ("notificación ... del 01/10"). La tesis en
`11-aspectos-legales.tex:32` dice "2026-09-30" y debe corregirse a "2026-10-01" (E2). El acta NO se
edita; solo se unifica la fecha del capítulo legal.

**OQ-2 (redacción legal del art. 28) — PROPUESTA y AUTORIZADA por los autores (2026-11-25);
PENDIENTE del aval del director.** Redacción autorizada para E1 (`11-aspectos-legales.tex:12`):

> El artículo 2 de la ley define la disociación como todo tratamiento de datos personales de manera
> que la información obtenida no pueda asociarse a una persona determinada o determinable. El artículo
> 28, en su inciso 1, excluye de la aplicación de la ley a las investigaciones científicas en la medida
> en que los datos recogidos no puedan atribuirse a una persona determinada o determinable y, en su
> inciso 2, ordena utilizar una técnica de disociación cuando no resulte posible mantener el anonimato.
> El artículo 11, inciso 3, apartado e, admite además la cesión de los datos sin consentimiento del
> titular cuando se hubiera aplicado un procedimiento de disociación que torne inidentificables a los
> titulares. Sobre estas bases se funda aquí la licitud por disociación del corpus, figura
> complementaria de la pseudonimización.

Nota de propagación: la relectura del capítulo 11 completo muestra que la cita errónea del art. 28
está AISLADA en `:12`; las demás menciones ("sin datos personales" / "no contiene dato personal") en
`:16`, `:18`, `:26`, `:32`, `:36`, `:46` y `:54` son afirmaciones fácticas, no citas al art. 28. La
corrección E1 es, por tanto, puntual. El apply de E1-E3 sigue bloqueado hasta el aval escrito del
director (gobernanza ALTA); E4-E5 (MEDIA) no tienen compuerta.
