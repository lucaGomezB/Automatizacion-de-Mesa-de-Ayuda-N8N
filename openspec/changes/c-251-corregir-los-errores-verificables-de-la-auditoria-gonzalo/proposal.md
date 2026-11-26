# Proposal: Corregir los errores verificables de la auditoría Gonzalo (nivel 2)

## Why

La tesis ya liberó la versión de defensa `v1.6.5` (tag anotado). Una auditoría independiente de
nivel 2 (Gonzalo Sevilla) revisó esa versión y detectó **cinco errores verificables** — objetivos,
independientes de la discusión de fondo sobre retractación — en el capítulo legal y en la lectura de
la línea base de tiempo. Tres son de prioridad **ALTA** (capítulo legal, `11-aspectos-legales.tex`):
una paráfrasis inexacta del art. 28 de la Ley 25.326, una fecha de notificación contradictoria con
el acta firmada y una frase sobre la v1.6.0 que el tribunal C-05 pidió retirar explícitamente. Dos
son de prioridad **MEDIA**: la inversión del razonamiento de asimetría de alcance en la Discusión y
la etiqueta incorrecta del `-10 s` del Anexo K (presentado como "redondeo" cuando es herencia del
componente "carga ~10 s" ya retirado por C-02). Ningún número cambia: se corrige redacción y
etiqueta. Los tres puntos ALTA exigen aprobación de autores+director antes del apply, y dos hechos
quedan abiertos como compuertas (OQ-1 fecha de notificación; OQ-2 redacción legal del art. 28).

## What Changes

- **E1 (ALTA). Paráfrasis inexacta del art. 28 de la Ley 25.326** — `11-aspectos-legales.tex:12`.
  El texto actual dice "el artículo 28 dispone que los datos disociados no se consideran datos
  personales a los efectos de la ley"; el art. 28 NO dice eso. Texto oficial: el art. 2 DEFINE
  "disociación de datos"; el art. 28 (archivos relativos a encuestas) exime encuestas/estadística/
  investigación científica en la medida en que los datos no puedan atribuirse a una persona
  determinada o determinable (28.1) y manda usar técnica de disociación cuando no se pueda mantener
  el anonimato (28.2); el art. 11.3.e permite la cesión sin consentimiento cuando media disociación.
  Ningún artículo dice literalmente "disociado = no dato personal". Se reformula la fundamentación de
  la licitud por disociación con lectura fiel. **[OQ-2: la redacción legal final la deciden
  autores+director.]** Propagación a verificar en `:16`, `:18`, `:32`, `:36`, `:46`, `:54`.
- **E2 (ALTA). Fecha de notificación contradictoria** — `11-aspectos-legales.tex:32`. El texto dice
  "La notificación a los integrantes del grupo ... se realizó de forma verbal el 2026-09-30"; el acta
  firmada (`docs/seguridad/acta-consentimiento-t2.md`, cabecera y §4) consigna "2026-10-01" y el
  tribunal C-05 habla de "la notificación del 01/10". Se unifica a UNA fecha. **[OQ-1: autores
  definen cuál es la correcta.]** Nota: el acta §1 aún dice "propio entorno operativo" (stale),
  perteneciente a la discusión C-06 = fuera de alcance; solo se consigna como nota.
- **E3 (ALTA). Frase sobre v1.6.0 aún presente** — `11-aspectos-legales.tex:32` (final). Se retira
  la oración "La versión v1.6.0 afirmó que no se había recabado el consentimiento de los titulares
  para la transferencia internacional; esa afirmación no se sostiene, porque el consentimiento verbal
  se prestó el 2026-10-02, aunque su constancia escrita es posterior.", que el tribunal C-05 pidió
  retirar explícitamente.
- **E4 (MEDIA). Inversión del razonamiento de asimetría de alcance** — `08-discusion.tex:22`. Se
  separa el componente de INSTRUMENTO (cronómetro humano con lag, infla el manual, SÍ favorece al
  automatizado) del de ALCANCE (manual = clasificación pura, alcance ESTRECHO sub-contado;
  automatizado = extremo a extremo, alcance AMPLIO). La asimetría de ALCANCE subestima la ventaja del
  automatizado (la línea base manual queda sub-estimada y la reducción reportada es COTA INFERIOR), no
  lo favorece; consistente con la octava amenaza (`04-marco-metodologico.tex:131`: "la dirección y la
  magnitud ... no se estimaron").
- **E5 (MEDIA). Anexo K: "-10 s presentado como redondeo"** — `12-anexos.tex:354` (+
  `04-marco-metodologico.tex:16` y `08-discusion.tex`). El redondeo es hacia arriba a múltiplos de
  5 s (199/200 valores múltiplos de 5 s), así que la inflación máxima por caso es < 5 s, no 10 s. El
  `-10 s` es herencia del componente "carga ~10 s" ya retirado (el tribunal C-02 calculó literalmente
  "10 s menos → 51,6 s / 65,6 %"). Se re-etiqueta honestamente: `-5 s` = cota de redondeo; `-10 s` =
  escenario que el tribunal pidió cuantificar cuando la descripción aún incluía la "carga". Los
  números quedan; cambia la etiqueta/justificación.

**BREAKING (afirmaciones del capítulo legal y de la lectura de la reducción):** ninguno de los cinco
errores cambia una cifra canónica; cambian afirmaciones de hecho (atribución legal del art. 28, fecha
de notificación) y de encuadre (dirección de la asimetría de alcance, origen de la sensibilidad de
-10 s).

Fuera de alcance: la discusión de fondo sobre retractación; la edición de `docs/seguridad/` (el acta
solo se referencia como evidencia de la contradicción en E2, no se edita); la frase stale "propio
entorno operativo" del acta §1 (C-06); todo `.tex` fuera de los pasajes listados; `App/`, `n8n/`,
`evaluation/`, `data/`; mover o recrear tags; compilación/regeneración de derivados (queda para el
apply post-aprobación, si los autores lo indican).

**Gobernanza: ALTA en E1-E3** (capítulo legal) y **MEDIA en E4-E5**. Los puntos ALTA requieren
aprobación explícita de autores+director ANTES del apply; OQ-1 y OQ-2 bloquean las tareas
correspondientes.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `tesis-reencuadre-cuarta-instancia`: se AGREGAN requisitos que corrigen los tres errores del
  capítulo legal detectados por la auditoría Gonzalo: paráfrasis fiel del art. 28/2/11.3.e con la
  licitud fundada en disociación (E1), fecha de notificación unificada y consistente con el acta
  (E2) y retiro de la frase sobre la v1.6.0 (E3).
- `tesis-numeros-canonicos`: se AGREGAN requisitos que corrigen la lectura de la reducción de tiempo:
  dirección correcta y explícita de la asimetría de alcance (conservadora, cota inferior; E4) y
  re-etiquetado honesto de la sensibilidad de `-10 s` en el rango de robustez de tiempos (herencia
  del componente "carga ~10 s" retirado, no "redondeo"; E5).

## Impact

| Area | Impacto | Descripcion |
|---|---|---|
| `docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex` | Modificado (ALTA) | E1, E2, E3 (arts. 2/28/11.3.e; fecha de notificación unificada; retiro de la frase v1.6.0) |
| `docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex` | Modificado (MEDIA) | E4 (separar instrumento vs alcance; dirección de la asimetría de alcance) y re-etiquetado del -10 s (E5) |
| `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` | Modificado (MEDIA) | E5 (Anexo K: -5 s = cota de redondeo, -10 s = escenario C-02) |
| `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex` | Modificado (MEDIA) | E5 (línea 16: no vincular ambos descuentos 5/10 s al "redondeo") |
| `docs/seguridad/acta-consentimiento-t2.md` | Referencia (sin editar) | Evidencia de la contradicción de fecha en E2 |
| `auditorias/Devolucion_Quinta_Instancia_TFI_v1.6.4_2026-11-25.md` | Referencia (sin editar) | Observación C-05: retiro de la frase v1.6.0 y fecha 01/10 |
